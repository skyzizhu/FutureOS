"""Freeze M1 inputs at submission; persist M2 drafts without any publication path."""

import subprocess
from pathlib import Path
from uuid import UUID, uuid4
from zipfile import BadZipFile

import prediction_engine
from prediction_engine.contracts.models import (
    IndicatorDefinitionV1,
    M2DraftV1,
    M2ResearchResultV1,
    ReplayResultV1,
    ResearchAcceptedV1,
    ResearchRunViewV1,
    ResearchSnapshotV1,
    ResearchSubmitV1,
)
from prediction_engine.evidence.temporal import utc
from prediction_engine.forecasting.workflow import (
    build_forecast_draft,
    hashed,
    input_hash,
    narrative_messages,
    validate_snapshot,
)
from sqlalchemy import select
from sqlalchemy.orm import Session

from infra.db import (
    EvidenceClaim,
    ForecastDraft,
    Indicator,
    Job,
    OutboxEvent,
    ResearchRun,
    ResearchRunCase,
    ResearchRunClaim,
    ResearchRunObservation,
    ResearchRunSource,
    ResearchTopic,
    Signal,
    SourceVersion,
    WorldForecast,
    utcnow,
)
from infra.engine_artifacts import freeze_engine, replay_archived
from infra.evidence_repository import EvidenceError, EvidenceRepository, columns, stable_id
from infra.job_budget import enforce_queue_budget
from infra.settings import Settings


def engine_code_hash() -> str:
    root = Path(prediction_engine.__file__).parent
    return hashed(
        [
            (str(path.relative_to(root)), path.read_text())
            for path in sorted(root.rglob("*.py"))
            if "build" not in path.parts
        ]
    )


class ResearchRepository:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.evidence = EvidenceRepository(session)

    def snapshot(self, request: ResearchSubmitV1) -> ResearchSnapshotV1:
        if request.research_as_of > utcnow():
            raise EvidenceError("RESEARCH_CUTOFF_IN_FUTURE", "研究截止时间不能晚于当前时间")
        if request.target is not None:
            fields = request.target.model_dump(
                exclude={"schema_version", "target_type", "target_start_at", "target_end_at"}
            )
            if any(
                not str(value).strip()
                or str(value).strip().casefold() in {"unknown", "n/a", "tbd", "待定", "未知"}
                for value in fields.values()
            ):
                raise EvidenceError(
                    "RESEARCH_TARGET_UNRESOLVED",
                    "目标的范围、基线和验证规则必须明确；不明确时请移除 target 保留假设",
                )
        claims = {}
        sources = {}
        signals = []
        for identifier in sorted(set(request.signal_ids)):
            row = self.session.get(Signal, identifier)
            if row is None:
                raise EvidenceError("RESEARCH_SIGNAL_MISSING", "所选信号不存在", 404)
            signal = self.evidence.signal_view(row)
            signals.append(signal)
            for claim_id in signal.claim_ids:
                claim = self.session.get(EvidenceClaim, claim_id)
                if claim is None:
                    raise EvidenceError("RESEARCH_SOURCE_MISSING", "信号缺少引用主张", 404)
                claims[claim_id] = self.evidence.claim(claim)
        # Bounded, domain-scoped counterevidence discovery, not exhaustive web search.
        for claim in self.session.scalars(
            select(EvidenceClaim)
            .where(
                EvidenceClaim.relation == "contradicts",
                EvidenceClaim.label == request.label,
                EvidenceClaim.claim_kind == "fact",
                EvidenceClaim.verification_status == "verified",
                EvidenceClaim.known_at <= request.research_as_of,
            )
            .order_by(EvidenceClaim.id)
            .limit(100)
        ):
            source = self.session.get(SourceVersion, claim.source_version_id)
            if source and set(source.domain_tags) & {tag.value for tag in request.domain_tags}:
                claims[claim.id] = self.evidence.claim(claim)
        source_ids = {claim.source_version_id for claim in claims.values()}
        cases = [
            self.evidence.case_view(identifier, request.research_as_of)
            for identifier in sorted(set(request.historical_case_ids))
        ]
        for case in cases:
            source_ids.update(
                event.source_version_id for event in (*case.contemporaneous, *case.outcomes)
            )
        indicator = None
        observations = []
        if request.indicator_id:
            definition = self.session.get(Indicator, request.indicator_id)
            if definition is None or definition.label != request.label:
                raise EvidenceError("RESEARCH_INDICATOR_INVALID", "指标不存在或数据标签不一致")
            indicator = IndicatorDefinitionV1.model_validate(
                {**columns(definition), "indicator_id": definition.id}, extra="ignore"
            )
            observations = self.evidence.series(definition.id, request.research_as_of)[-24:]
            if any(
                row.period_end > row.available_at or row.period_end > request.research_as_of
                for row in observations
            ):
                raise EvidenceError(
                    "RESEARCH_OBSERVATION_NOT_OBSERVED", "不能把未来统计期的预测值当作已观察指标"
                )
            source_ids.update(row.source_version_id for row in observations)
        for identifier in sorted(source_ids):
            source = self.session.get(SourceVersion, identifier)
            if source is None:
                raise EvidenceError("RESEARCH_SOURCE_MISSING", "引用来源版本不存在", 404)
            sources[identifier] = self.evidence.version(source)
        snapshot = ResearchSnapshotV1(
            request=request,
            signals=tuple(signals),
            claims=tuple(claims[key] for key in sorted(claims)),
            sources=tuple(sources.values()),
            cases=tuple(cases),
            indicator=indicator,
            observations=tuple(observations),
            engine_code_hash=engine_code_hash(),
        )
        try:
            validate_snapshot(snapshot)
        except ValueError as exc:
            raise EvidenceError(
                str(exc), "来源、时间、标签或事实核实状态不满足研究准入条件"
            ) from None
        return snapshot

    def submit(
        self, request: ResearchSubmitV1, user_id: UUID, key: str, config: Settings
    ) -> ResearchAcceptedV1:
        # Serialize one user's request reservations without serializing the long model work.
        from infra.db import User

        self.session.scalar(select(User).where(User.id == user_id).with_for_update())
        request_hash = hashed({"task": "m2_research", "request": request.model_dump(mode="json")})
        prior = self.session.scalar(
            select(Job).where(Job.user_id == user_id, Job.idempotency_key == key)
        )
        if prior:
            if prior.task_type != "m2_research" or prior.input_hash != request_hash:
                raise EvidenceError("IDEMPOTENCY_CONFLICT", "同一幂等键不能更换研究输入", 409)
            run = self.session.scalar(select(ResearchRun).where(ResearchRun.job_id == prior.id))
            assert run is not None
            return ResearchAcceptedV1(job_id=prior.id, request_id=prior.request_id, run_id=run.id)
        if request.provider == "mock" and request.label != "DEMO":
            raise EvidenceError("MOCK_REQUIRES_DEMO", "Mock 研究只能使用 DEMO 数据")
        if request.provider == "deepseek" and (
            not config.live_research_enabled or not config.deepseek_api_key
        ):
            raise EvidenceError("LIVE_RESEARCH_DISABLED", "真实生成需单独开启并配置服务端 Key", 503)
        enforce_queue_budget(self.session, user_id, config.queue_max_pending_per_user)
        snapshot = self.snapshot(request)
        freeze_engine(snapshot.engine_code_hash)
        run_id = uuid4()
        topic_id = stable_id(
            "topic:"
            + hashed(
                [
                    request.title,
                    request.scope,
                    request.label,
                    sorted(tag.value for tag in request.domain_tags),
                ]
            )
        )
        self.evidence.ensure(
            ResearchTopic,
            {
                "id": topic_id,
                "owner_user_id": None,
                "title": request.title,
                "scope": request.scope,
                "domain_tags": [tag.value for tag in request.domain_tags],
                "version": 1,
                "label": request.label,
            },
        )
        job = Job(
            user_id=user_id,
            task_type="m2_research",
            idempotency_key=key,
            input_hash=request_hash,
            payload={"run_id": str(run_id), "label": request.label},
        )
        self.session.add(job)
        self.session.flush()
        self.session.add(
            ResearchRun(
                id=run_id,
                topic_id=topic_id,
                creator_id=user_id,
                job_id=job.id,
                research_as_of=request.research_as_of,
                provider=request.provider,
                model_id="mock-research-v1"
                if request.provider == "mock"
                else config.deepseek_research_model,
                input_hash=input_hash(snapshot),
                engine_code_hash=snapshot.engine_code_hash,
                prompt_hash=hashed(narrative_messages(snapshot)),
                snapshot=snapshot.model_dump(mode="json"),
                label=request.label,
            )
        )
        self.session.flush()
        self.session.add_all(
            [
                ResearchRunSource(run_id=run_id, source_version_id=row.source_version_id)
                for row in snapshot.sources
            ]
        )
        self.session.add_all(
            [ResearchRunClaim(run_id=run_id, claim_id=row.claim_id) for row in snapshot.claims]
        )
        self.session.add_all(
            [
                ResearchRunObservation(run_id=run_id, observation_id=row.observation_id)
                for row in snapshot.observations
            ]
        )
        self.session.add_all(
            [ResearchRunCase(run_id=run_id, case_id=row.case_id) for row in snapshot.cases]
        )
        self.session.add(
            OutboxEvent(
                job_id=job.id,
                event_type="M2ResearchRequested.v1",
                payload={"run_id": str(run_id), "job_id": str(job.id)},
            )
        )
        self.session.commit()
        return ResearchAcceptedV1(job_id=job.id, request_id=job.request_id, run_id=run_id)

    def persist_draft(self, run_id: UUID, draft: M2DraftV1) -> M2ResearchResultV1:
        run = self.session.get(ResearchRun, run_id)
        assert run is not None
        if draft.input_hash != run.input_hash or draft.prompt_hash != run.prompt_hash:
            raise ValueError("RESEARCH_FROZEN_INPUT_MISMATCH")
        forecast_id = None
        if draft.kind == "draft_forecast" and draft.target is not None:
            target_key = hashed(draft.target.model_dump(mode="json"))
            forecast_id = stable_id("world-target:" + str(run.topic_id) + target_key)
            self.evidence.ensure(
                WorldForecast,
                {
                    "id": forecast_id,
                    "topic_id": run.topic_id,
                    "stable_target_key": target_key,
                    "target_type": draft.target.target_type,
                    "lifecycle_stage": draft.lifecycle_stage.value,
                    "current_version_id": None,
                    "status": "internal_unreviewed",
                },
            )
        body = draft.model_dump(mode="json")
        fingerprint = hashed(body)
        existing = self.session.get(ForecastDraft, draft.draft_id)
        if existing and existing.immutable_hash != fingerprint:
            raise ValueError("RESEARCH_IMMUTABLE_DRAFT_CONFLICT")
        self.evidence.ensure(
            ForecastDraft,
            {
                "id": draft.draft_id,
                "run_id": run.id,
                "forecast_id": forecast_id,
                "draft_sequence": "A",
                "body": body,
                "inputs_hash": run.input_hash,
                "immutable_hash": fingerprint,
                "model_id": draft.model_id,
            },
        )
        return M2ResearchResultV1(
            run_id=run.id,
            draft_id=draft.draft_id,
            label=draft.label,
            kind=draft.kind,
            input_hash=run.input_hash,
            draft_hash=fingerprint,
        )

    def view(self, run_id: UUID) -> ResearchRunViewV1:
        run = self.session.get(ResearchRun, run_id)
        if run is None:
            raise EvidenceError("RESEARCH_RUN_NOT_FOUND", "研究运行不存在", 404)
        job = self.session.get(Job, run.job_id)
        topic = self.session.get(ResearchTopic, run.topic_id)
        assert job is not None and topic is not None
        draft = self.session.scalar(
            select(ForecastDraft).where(
                ForecastDraft.run_id == run_id, ForecastDraft.draft_sequence == "A"
            )
        )
        return ResearchRunViewV1.model_validate(
            {
                "run_id": run.id,
                "topic_id": run.topic_id,
                "job_id": job.id,
                "title": topic.title,
                "status": job.status,
                "research_as_of": utc(run.research_as_of),
                "input_hash": run.input_hash,
                "engine_code_hash": run.engine_code_hash,
                "provider": run.provider,
                "model_id": run.model_id,
                "label": run.label,
                "draft": draft.body if draft else None,
                "draft_hash": draft.immutable_hash if draft else None,
                "error_code": job.error_code,
            }
        )

    def replay(self, run_id: UUID) -> ReplayResultV1:
        from prediction_engine.contracts.models import ResearchNarrativeV1

        from infra.db import ModelCall

        run = self.session.get(ResearchRun, run_id)
        draft = self.session.scalar(
            select(ForecastDraft).where(
                ForecastDraft.run_id == run_id, ForecastDraft.draft_sequence == "A"
            )
        )
        if run is None or draft is None:
            raise EvidenceError("RESEARCH_DRAFT_NOT_FOUND", "尚无可重放的冻结草稿", 404)
        snapshot = ResearchSnapshotV1.model_validate(run.snapshot)
        original = M2DraftV1.model_validate(draft.body)
        if run.provider in {"mock", "incremental"}:
            narrative = original.raw_narrative
        else:
            call = self.session.get(ModelCall, run_id)
            if call is None or call.response is None:
                raise EvidenceError(
                    "REPLAY_RESPONSE_MISSING", "缺少已冻结模型响应，禁止重发付费请求", 409
                )
            narrative = ResearchNarrativeV1.model_validate(call.response)
        if run.engine_code_hash == engine_code_hash():
            replayed = build_forecast_draft(
                run.id,
                snapshot,
                narrative,
                original.model_id,
                parent_version_id=original.parent_version_id,
            )
            fingerprint = hashed(replayed.model_dump(mode="json"))
        else:
            try:
                fingerprint = replay_archived(
                    run.engine_code_hash,
                    {
                        "run_id": str(run.id),
                        "snapshot": run.snapshot,
                        "narrative": narrative.model_dump(mode="json"),
                        "model_id": original.model_id,
                        "parent_version_id": str(original.parent_version_id)
                        if original.parent_version_id
                        else None,
                    },
                )
            except (OSError, ValueError, BadZipFile, subprocess.SubprocessError):
                raise EvidenceError(
                    "REPLAY_ENGINE_VERSION_MISMATCH",
                    "原引擎工件缺失或校验失败，禁止联网替代历史重放",
                    409,
                ) from None
        return ReplayResultV1(
            run_id=run.id,
            identical=fingerprint == draft.immutable_hash,
            input_hash=run.input_hash,
            original_draft_hash=draft.immutable_hash,
            replay_draft_hash=fingerprint,
        )
