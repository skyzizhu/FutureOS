"""M3 application orchestration; reviewers receive DTOs only and cannot persist changes."""

import re
import time
from typing import Any
from uuid import UUID, uuid4, uuid5

from prediction_engine.adjudication.rules import adjudicate
from prediction_engine.contracts.models import (
    CriticReportV1,
    EvaluationProtocolV1,
    EvaluationRegisterV1,
    ForecastResolutionV1,
    M2DraftV1,
    PublishedForecastV1,
    PublishRequestV1,
    ResearchSnapshotV1,
    ResolveRequestV1,
    ReviewDecisionV1,
    ReviewViewV1,
    RevisionRequestV1,
    RevisionViewV1,
)
from prediction_engine.evaluation.resolution import resolve
from prediction_engine.evidence.temporal import utc
from prediction_engine.forecasting.workflow import build_forecast_draft, hashed
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from infra.critic_runner import run_critic
from infra.db import (
    AdjudicationRecord,
    CriticRun,
    DraftRevision,
    EvaluationProtocol,
    ForecastDraft,
    ForecastResolution,
    ForecastVersion,
    Indicator,
    ObservationVintage,
    ResearchRun,
    SourceVersion,
    WorldForecast,
    utcnow,
)
from infra.engine_artifacts import freeze_engine
from infra.evidence_repository import EvidenceError, EvidenceRepository
from infra.research_repository import ResearchRepository, engine_code_hash


class ReviewRepository:
    def __init__(self, session: Session, autocommit: bool = True) -> None:
        self.session = session
        self.autocommit = autocommit

    def finish(self) -> None:
        if self.autocommit:
            self.session.commit()
        else:
            self.session.flush()

    def draft(self, identifier: UUID, lock: bool = False) -> ForecastDraft:
        query = select(ForecastDraft).where(ForecastDraft.id == identifier)
        row = self.session.scalar(query.with_for_update() if lock else query)
        if row is None:
            raise EvidenceError("DRAFT_NOT_FOUND", "草稿不存在", 404)
        if hashed(row.body) != row.immutable_hash:
            raise EvidenceError("DRAFT_HASH_MISMATCH", "草稿完整性检查失败", 409)
        return row

    def snapshot(self, row: ForecastDraft) -> ResearchSnapshotV1:
        revision = self.session.get(DraftRevision, row.id)
        run = self.session.get(ResearchRun, row.run_id)
        assert run is not None
        return ResearchSnapshotV1.model_validate(revision.snapshot if revision else run.snapshot)

    def independent_snapshot(self, row: ForecastDraft) -> ResearchSnapshotV1:
        prior = self.snapshot(row)
        # Independently query M1 at the original cutoff; no main-engine prompt is passed.
        # A late-ingested archival contradiction may be admitted, never a future-known fact.
        independent = ResearchRepository(self.session).snapshot(prior.request)
        return independent.model_copy(
            update={
                "sources": tuple(
                    {
                        s.source_version_id: s for s in (*prior.sources, *independent.sources)
                    }.values()
                ),
                "claims": tuple(
                    {c.claim_id: c for c in (*prior.claims, *independent.claims)}.values()
                ),
            }
        )

    def review(self, identifier: UUID) -> ReviewViewV1:
        row = self.draft(identifier, lock=True)
        draft = M2DraftV1.model_validate(row.body)
        snapshot = self.independent_snapshot(row)
        identifier = uuid4()
        started = time.monotonic()
        report = run_critic(identifier, draft, snapshot)
        from infra.costs import record_cost

        run = self.session.get(ResearchRun, row.run_id)
        assert run is not None
        record_cost(
            self.session,
            run.job_id,
            "critic",
            str(identifier),
            int((time.monotonic() - started) * 1000),
        )
        number = {"A": 0, "B1": 1, "B2": 2}[row.draft_sequence]
        decision = adjudicate(report, number, utcnow())
        freeze_engine(engine_code_hash())
        self.session.add(
            CriticRun(
                id=identifier,
                draft_id=row.id,
                draft_hash=row.immutable_hash,
                independent_snapshot=snapshot.model_dump(mode="json"),
                independent_input_hash=report.independent_input_hash,
                engine_code_hash=engine_code_hash(),
                report=report.model_dump(mode="json"),
            )
        )
        self.session.flush()
        self.session.add(
            AdjudicationRecord(
                id=decision.decision_id,
                critic_run_id=identifier,
                draft_id=row.id,
                decision=decision.decision,
                publication_allowed=decision.publication_allowed,
                body=decision.model_dump(mode="json"),
            )
        )
        self.finish()
        return ReviewViewV1(report=report, decision=decision)

    def review_view(self, identifier: UUID) -> ReviewViewV1:
        run = self.session.get(CriticRun, identifier)
        decision = self.session.scalar(
            select(AdjudicationRecord).where(AdjudicationRecord.critic_run_id == identifier)
        )
        if run is None or decision is None:
            raise EvidenceError("REVIEW_NOT_FOUND", "审查记录不存在", 404)
        return ReviewViewV1(
            report=CriticReportV1.model_validate(run.report),
            decision=ReviewDecisionV1.model_validate(decision.body),
        )

    def revise(self, identifier: UUID, request: RevisionRequestV1) -> RevisionViewV1:
        parent = self.draft(identifier, lock=True)
        view = self.review_view(request.review_id)
        if view.report.draft_id != identifier or view.decision.decision not in {
            "block",
            "targeted_research",
        }:
            raise EvidenceError("REVISION_NOT_AUTHORIZED", "仅裁决层确认的问题可触发定向复核", 409)
        actionable = {
            f.finding_id
            for f in view.report.findings
            if f.severity in {"L2", "L3"} and f.verification_status == "verified"
        }
        if not set(request.confirmed_finding_ids) <= actionable or not actionable <= set(
            request.confirmed_finding_ids
        ):
            raise EvidenceError(
                "FINDINGS_NOT_VERIFIED", "须确认全部已核实的实质问题；普通分歧不能改写", 409
            )
        if parent.draft_sequence == "B2":
            raise EvidenceError("REVISION_LIMIT", "最多两轮复核，转研究假设/人工处理", 409)
        sequence = "B1" if parent.draft_sequence == "A" else "B2"
        revision_id = uuid5(identifier, sequence)
        existing = self.session.get(DraftRevision, revision_id)
        if existing:
            if existing.review_id != request.review_id or (
                request.additional_case_ids
                and not set(str(i) for i in request.additional_case_ids)
                <= set(existing.snapshot["request"]["historical_case_ids"])
            ):
                raise EvidenceError("REVISION_CONFLICT", "此父草稿已冻结定向复核", 409)
            return self.revision_view(revision_id)
        review = self.session.get(CriticRun, request.review_id)
        assert review is not None
        snapshot = ResearchSnapshotV1.model_validate(review.independent_snapshot)
        if request.additional_case_ids:
            case_ids = tuple(
                sorted(set(snapshot.request.historical_case_ids) | set(request.additional_case_ids))
            )
            if len(case_ids) > 10:
                raise EvidenceError("REVISION_CASE_LIMIT", "每次研究最多10个历史案例", 409)
            revised_request = snapshot.request.model_copy(update={"historical_case_ids": case_ids})
            snapshot = ResearchRepository(self.session).snapshot(revised_request)

        original = M2DraftV1.model_validate(parent.body)
        # Main engine, not Critic, regenerates only from verified frozen review inputs.
        # No new model call: retained narrative plus verified new counter-citations.
        narrative = original.raw_narrative.model_copy(
            update={
                "cited_claim_ids": tuple(
                    sorted(
                        set(original.raw_narrative.cited_claim_ids)
                        | {c.claim_id for c in snapshot.claims if c.relation == "contradicts"}
                    )
                ),
            }
        )
        try:
            revised = build_forecast_draft(original.run_id, snapshot, narrative, original.model_id)
        except ValueError:
            raise EvidenceError(
                "REVISION_REQUIRES_VERIFIED_DATA",
                "无法用合法输入修正，保留原稿并待人工补充资料",
                409,
            ) from None
        revised = revised.model_copy(update={"draft_id": revision_id, "draft_sequence": sequence})
        body = revised.model_dump(mode="json")
        before = parent.body
        changes = {
            field: {"before": before.get(field), "after": value}
            for field, value in body.items()
            if value != before.get(field)
        }
        self.session.add(
            ForecastDraft(
                id=revision_id,
                run_id=parent.run_id,
                forecast_id=parent.forecast_id,
                draft_sequence=sequence,
                body=body,
                inputs_hash=revised.input_hash,
                immutable_hash=hashed(body),
                model_id=revised.model_id,
            )
        )
        self.session.flush()
        self.session.add(
            DraftRevision(
                draft_id=revision_id,
                parent_draft_id=identifier,
                review_id=request.review_id,
                snapshot=snapshot.model_dump(mode="json"),
                changes=changes,
                finding_ids=[str(i) for i in request.confirmed_finding_ids],
            )
        )
        self.finish()
        return self.revision_view(revision_id)

    def revision_view(self, identifier: UUID) -> RevisionViewV1:
        row = self.draft(identifier)
        revision = self.session.get(DraftRevision, identifier)
        if revision is None:
            raise EvidenceError("REVISION_NOT_FOUND", "不是复核草稿", 404)
        assert row.draft_sequence in {"B1", "B2"}
        return RevisionViewV1(
            draft_id=row.id,
            parent_draft_id=revision.parent_draft_id,
            draft_sequence="B1" if row.draft_sequence == "B1" else "B2",
            input_hash=row.inputs_hash,
            draft_hash=row.immutable_hash,
            changes=revision.changes,
            body=M2DraftV1.model_validate(row.body),
        )

    def publish(self, identifier: UUID, request: PublishRequestV1) -> PublishedForecastV1:
        row = self.draft(identifier, lock=True)
        view = self.review_view(request.review_id)
        if (
            view.report.draft_id != row.id
            or view.report.draft_hash != row.immutable_hash
            or not view.decision.publication_allowed
        ):
            raise EvidenceError("FORECAST_REVIEW_BLOCKED", "草稿尚未通过独立审查", 409)
        # Re-check the newest review, not an old favourable decision.
        latest = self.session.scalar(
            select(CriticRun)
            .where(CriticRun.draft_id == row.id)
            .order_by(CriticRun.created_at.desc(), CriticRun.id.desc())
            .limit(1)
        )
        if latest is None or latest.id != request.review_id:
            raise EvidenceError("STALE_REVIEW", "只能使用此草稿最新审查记录发布", 409)
        audit = self.session.get(CriticRun, request.review_id)
        assert audit is not None
        if audit.engine_code_hash != engine_code_hash() or audit.independent_input_hash != hashed(
            self.independent_snapshot(row).model_dump(mode="json")
        ):
            raise EvidenceError("REVIEW_INPUT_CHANGED", "资料或审查代码已变更，请重新审查", 409)
        prior = self.session.scalar(
            select(ForecastVersion).where(ForecastVersion.draft_id == row.id)
        )
        if prior:
            return self.version_view(prior.id)
        draft = M2DraftV1.model_validate(row.body)
        now = utcnow()
        if draft.parent_version_id:
            parent = self.session.get(ForecastVersion, draft.parent_version_id)
            world = self.session.get(WorldForecast, row.forecast_id)
            if (
                draft.target is None
                or parent is None
                or world is None
                or parent.forecast_id != row.forecast_id
                or world.current_version_id != parent.id
                or parent.target != draft.target.model_dump(mode="json")
            ):
                raise EvidenceError(
                    "INVALID_FORECAST_CONTINUATION", "重预测必须延续同一已发布目标及当前版本", 409
                )
        if draft.kind != "draft_forecast" or draft.target is None or row.forecast_id is None:
            raise EvidenceError("FORECAST_TARGET_REQUIRED", "研究假设不能发布成正式预测", 409)
        if draft.label == "REAL" and (
            draft.target.target_end_at <= now or draft.next_review_at <= now
        ):
            raise EvidenceError(
                "FORECAST_NOT_FORWARD", "真实发布要求目标和复查时间晚于当前时间", 409
            )
        world = self.session.scalar(
            select(WorldForecast).where(WorldForecast.id == row.forecast_id).with_for_update()
        )
        assert world is not None
        number = (
            self.session.scalar(
                select(func.max(ForecastVersion.version_num)).where(
                    ForecastVersion.forecast_id == world.id
                )
            )
            or 0
        ) + 1
        version_id = uuid4()
        fingerprint = hashed(
            {
                "body": row.body,
                "review_id": str(request.review_id),
                "published_at": now.isoformat(),
                "change_reason": request.change_reason,
            }
        )
        version = ForecastVersion(
            id=version_id,
            forecast_id=world.id,
            research_run_id=row.run_id,
            version_num=number,
            draft_id=row.id,
            review_id=request.review_id,
            label=draft.label,
            immutable_hash=fingerprint,
            change_reason=request.change_reason,
            statement=draft.statement,
            target=draft.target.model_dump(mode="json"),
            research_as_of=draft.research_as_of,
            published_at=now,
            body=row.body,
        )
        self.session.add(version)
        self.session.flush()
        world.current_version_id = version_id
        world.status = "published"
        self.finish()
        return self.version_view(version_id)

    def version_view(self, identifier: UUID) -> PublishedForecastV1:
        row = self.session.get(ForecastVersion, identifier)
        if row is None:
            raise EvidenceError("VERSION_NOT_FOUND", "版本不存在", 404)
        expected = hashed(
            {
                "body": row.body,
                "review_id": str(row.review_id),
                "published_at": utc(row.published_at).isoformat(),
                "change_reason": row.change_reason,
            }
        )
        if expected != row.immutable_hash:
            raise EvidenceError("VERSION_HASH_MISMATCH", "版本完整性校验失败", 409)
        return PublishedForecastV1(
            version_id=row.id,
            forecast_id=row.forecast_id,
            version_num=row.version_num,
            draft_id=row.draft_id,
            review_id=row.review_id,
            label=M2DraftV1.model_validate(row.body).label,
            published_at=utc(row.published_at),
            version_hash=row.immutable_hash,
            change_reason=row.change_reason,
            body=M2DraftV1.model_validate(row.body),
        )

    def register(self, identifier: UUID, request: EvaluationRegisterV1) -> EvaluationProtocolV1:
        version = self.session.scalar(
            select(ForecastVersion).where(ForecastVersion.id == identifier).with_for_update()
        )
        if version is None:
            raise EvidenceError("VERSION_NOT_FOUND", "版本不存在", 404)
        prior = self.session.scalar(
            select(EvaluationProtocol).where(EvaluationProtocol.version_id == identifier)
        )
        draft = M2DraftV1.model_validate(version.body)
        assert draft.target is not None
        target = draft.target
        # Do not let evaluator invent a favourable threshold after seeing the outcome.
        actual = target.direction_or_threshold.replace(" ", "")
        match = re.fullmatch(r"(>=|<=|=)(-?\d+(?:\.\d+)?)(.*)", actual)
        if (
            match is None
            or match[1] != {"gte": ">=", "lte": "<=", "eq": "="}[request.operator]
            or float(match[2]) != request.threshold
        ):
            raise EvidenceError(
                "PROTOCOL_TARGET_MISMATCH", "评估阈值必须匹配冻结目标，不能事后改题", 409
            )
        if prior:
            body = EvaluationProtocolV1.model_validate(prior.body)
            if (
                body.mode != request.mode
                or body.operator != request.operator
                or body.threshold != request.threshold
                or body.unit != request.unit
                or body.testset_version != request.testset_version
            ):
                raise EvidenceError("PROTOCOL_IMMUTABLE", "预登记协议已冻结", 409)
            return body
        now = utcnow()
        if request.mode == "forward" and (
            draft.label != "REAL"
            or target.target_start_at < now
            or target.target_end_at <= now
            or (now - draft.research_as_of).total_seconds() > 86400
        ):
            raise EvidenceError(
                "FORWARD_REGISTRATION_INVALID",
                "真实前瞻必须用近期真实输入，在目标窗口开始前预登记",
                409,
            )
        if draft.label == "DEMO" and request.mode != "synthetic":
            raise EvidenceError("DEMO_NOT_REAL_EVALUATION", "合成资料只能进入 synthetic 评估", 409)
        if draft.baseline.unit and request.unit != draft.baseline.unit:
            raise EvidenceError("PROTOCOL_UNIT_MISMATCH", "评估单位必须匹配冻结指标", 409)
        protocol = EvaluationProtocolV1(
            protocol_id=uuid4(),
            version_id=identifier,
            mode=request.mode,
            label=draft.label,
            registered_at=now,
            as_of=draft.research_as_of,
            due_at=target.target_end_at,
            metric_definition=target.metric_definition,
            geography=target.geography,
            unit=request.unit,
            resolution_source=target.resolution_source,
            operator=request.operator,
            threshold=request.threshold,
            baseline_value=draft.baseline.projected_value,
            source_snapshot_hash=draft.input_hash,
            model_id=draft.model_id,
            prompt_hash=draft.prompt_hash,
            testset_version=request.testset_version,
            limitations=(
                "没有校准概率；阈值不冒充数值点预测，A/B 数值误差在没有点预测时为空",
                "合成和历史测试不能证明真实前瞻准确率；基础模型未来知识不能完全排除",
            ),
        )
        self.session.add(
            EvaluationProtocol(
                id=protocol.protocol_id,
                version_id=identifier,
                mode=request.mode,
                label=draft.label,
                due_at=protocol.due_at,
                body=protocol.model_dump(mode="json"),
                immutable_hash=hashed(protocol.model_dump(mode="json")),
            )
        )
        self.session.flush()
        initial = resolve(protocol, now)
        self.session.add(
            ForecastResolution(
                id=initial.resolution_id,
                protocol_id=protocol.protocol_id,
                observation_id=None,
                status=initial.status,
                body=initial.model_dump(mode="json"),
            )
        )
        self.finish()
        return protocol

    def resolve(self, identifier: UUID, request: ResolveRequestV1) -> ForecastResolutionV1:
        row = self.session.get(EvaluationProtocol, identifier)
        if row is None:
            raise EvidenceError("PROTOCOL_NOT_FOUND", "评估协议不存在", 404)
        protocol = EvaluationProtocolV1.model_validate(row.body)
        now = utcnow()
        value = None
        if request.observation_id:
            observation = self.session.get(ObservationVintage, request.observation_id)
            indicator = (
                self.session.get(Indicator, observation.indicator_id) if observation else None
            )
            source = (
                self.session.get(SourceVersion, observation.source_version_id)
                if observation
                else None
            )
            if (
                not observation
                or not indicator
                or not source
                or observation.label != protocol.label
                or observation.quality_flag == "UNVERIFIED"
                or indicator.code != protocol.metric_definition
                or indicator.geo_scope != protocol.geography
                or indicator.unit != protocol.unit
                or utc(observation.period_end) != protocol.due_at
                or utc(observation.available_at) > now
                or utc(observation.period_end) > utc(observation.available_at)
                or utc(observation.published_at) > now
                or source.available_at is None
                or utc(source.available_at) > now
            ):
                raise EvidenceError(
                    "RESOLUTION_OBSERVATION_INVALID",
                    "观测必须符合预登记的统计期、来源、时间与口径",
                    409,
                )
            # Source identity is an explicit frozen field, never accept arbitrary evaluator numbers.
            document = EvidenceRepository(self.session).version(source)
            if protocol.resolution_source not in {document.url, document.publisher}:
                raise EvidenceError("RESOLUTION_SOURCE_MISMATCH", "观测来源与冻结规则不一致", 409)
            value = observation.value
        result = resolve(protocol, now, value, request.observation_id, request.unavailable_reason)
        self.session.add(
            ForecastResolution(
                id=result.resolution_id,
                protocol_id=identifier,
                observation_id=result.observation_id,
                status=result.status,
                body=result.model_dump(mode="json"),
            )
        )
        self.finish()
        return result

    def scoreboard(self) -> dict[str, Any]:
        rows = self.session.scalars(
            select(EvaluationProtocol).order_by(
                EvaluationProtocol.registered_at, EvaluationProtocol.id
            )
        ).all()
        records: list[dict[str, Any]] = []
        for row in rows:
            latest = self.session.scalar(
                select(ForecastResolution)
                .where(ForecastResolution.protocol_id == row.id)
                .order_by(ForecastResolution.checked_at.desc(), ForecastResolution.id.desc())
                .limit(1)
            )
            history = self.session.scalars(
                select(ForecastResolution)
                .where(ForecastResolution.protocol_id == row.id)
                .order_by(ForecastResolution.checked_at, ForecastResolution.id)
            ).all()
            records.append(
                {
                    "protocol": row.body,
                    "latest_resolution": latest.body if latest else None,
                    "resolution_history": [result.body for result in history],
                }
            )
        strata = []
        for mode in ("synthetic", "temporal_backtest", "forward"):
            group = [r for r in records if r["protocol"]["mode"] == mode]
            counts = {
                status: sum((r["latest_resolution"] or {}).get("status") == status for r in group)
                for status in (
                    "not_due",
                    "confirmed",
                    "disconfirmed",
                    "inconclusive",
                    "unresolved_due_to_data",
                )
            }
            strata.append({"mode": mode, "count": len(group), "statuses": counts, "accuracy": None})
        return {
            "records": records,
            "strata": strata,
            "real_accuracy_available": False,
            "limitations": [
                "保留失败、未到期和无法判定样本；不混合 synthetic/history/forward",
                "不把阈值当作点预测；无 A/B 数值点预测时不编造 MAE 改善；无真实前瞻到期成绩",
            ],
        }
