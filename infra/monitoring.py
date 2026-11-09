"""Pinned local evidence monitoring and atomic incremental publication, never paid discovery."""

from datetime import timedelta
from typing import Any
from uuid import UUID, uuid4

from prediction_engine.contracts.models import (
    ChangeAssertionV1,
    M2DraftV1,
    MonitorCheckRequestV1,
    MonitorPolicyV1,
    MonitorResultV1,
    PublishRequestV1,
    ResearchSnapshotV1,
    TurningDecisionV1,
)
from prediction_engine.evidence.temporal import utc
from prediction_engine.forecasting.workflow import build_forecast_draft, hashed
from prediction_engine.turning_points.rules import classify
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from infra.db import (
    EvidenceClaim,
    ForecastDraft,
    ForecastMonitor,
    ForecastVersion,
    Job,
    MonitorOutcome,
    MonitorRun,
    OutboxEvent,
    ResearchRun,
    Signal,
    SourceVersion,
    WorldForecast,
    utcnow,
)
from infra.engine_artifacts import freeze_engine
from infra.evidence_repository import EvidenceError
from infra.research_repository import ResearchRepository, engine_code_hash
from infra.review_repository import ReviewRepository
from infra.settings import Settings
from scripts.seed_demo import ADMIN_ID


class MonitorRepository:
    def __init__(
        self, session: Session, config: Settings | None = None, autocommit: bool = True
    ) -> None:
        self.session = session
        self.config = config or Settings()
        self.autocommit = autocommit

    def finish(self) -> None:
        if self.autocommit:
            self.session.commit()
        else:
            self.session.flush()

    def enroll(self, forecast_id: UUID) -> ForecastMonitor:
        row = self.session.get(ForecastMonitor, forecast_id)
        if row is None:
            row = ForecastMonitor(
                forecast_id=forecast_id,
                policy=MonitorPolicyV1().model_dump(mode="json"),
                next_check_at=utcnow(),
            )
            self.session.add(row)
            self.session.flush()
        return row

    def snapshot_for(self, version: ForecastVersion) -> ResearchSnapshotV1:
        draft = self.session.get(ForecastDraft, version.draft_id)
        assert draft is not None
        return ReviewRepository(self.session).snapshot(draft)

    def latest_inputs(self, version: ForecastVersion) -> ResearchSnapshotV1:
        old = self.snapshot_for(version)
        repo = ResearchRepository(self.session)
        tags = {tag.value for tag in old.request.domain_tags}
        identifiers = list(old.request.signal_ids)
        for signal in self.session.scalars(
            select(Signal)
            .where(Signal.label == version.label)
            .order_by(Signal.detected_at.desc())
            .limit(200)
        ):
            if set(signal.domain_tags) & tags and signal.id not in identifiers:
                view = repo.evidence.signal_view(signal)
                admitted = True
                for identifier in view.claim_ids:
                    claim = self.session.get(EvidenceClaim, identifier)
                    source = (
                        self.session.get(SourceVersion, claim.source_version_id) if claim else None
                    )
                    if (
                        not claim
                        or not source
                        or claim.claim_kind != "fact"
                        or claim.verification_status != "verified"
                        or claim.known_at is None
                        or utc(claim.known_at) > utcnow()
                        or source.available_at is None
                        or utc(source.available_at) > utcnow()
                    ):
                        admitted = False
                if admitted and view.claim_ids:
                    identifiers.append(signal.id)
        request = old.request.model_copy(
            update={"research_as_of": utcnow(), "signal_ids": tuple(identifiers[:20])}
        )
        # Unverified/newly observed signals do not silently become facts: admission is fail-closed.
        return repo.snapshot(request)

    def enqueue(
        self,
        forecast_id: UUID,
        data: MonitorCheckRequestV1,
        actor: UUID = ADMIN_ID,
        automatic: bool = False,
    ) -> dict[str, Any]:
        world = self.session.scalar(
            select(WorldForecast).where(WorldForecast.id == forecast_id).with_for_update()
        )
        if world is None or world.current_version_id is None:
            raise EvidenceError("FORECAST_NOT_FOUND", "只能复查已发布预测", 404)
        monitor = self.enroll(forecast_id)
        policy = MonitorPolicyV1.model_validate(monitor.policy)
        if not policy.enabled:
            raise EvidenceError("MONITOR_DISABLED", "此预测复查已暂停", 409)
        old_version = self.session.get(ForecastVersion, world.current_version_id)
        assert old_version is not None
        old = self.snapshot_for(old_version)
        new = self.latest_inputs(old_version)
        try:
            decision = classify(old, new, policy, data.assertions)
        except ValueError as exc:
            raise EvidenceError(str(exc), "核实断言需要对应原假设与有效证据", 422) from None
        digest = hashed(
            [
                str(old_version.id),
                decision.delta.fingerprint,
                [a.model_dump(mode="json") for a in data.assertions],
            ]
        )
        key = "m5-monitor:" + digest
        existing = self.session.scalar(
            select(Job).where(Job.user_id == ADMIN_ID, Job.idempotency_key == key)
        )
        if existing:
            if automatic:
                monitor.next_check_at = utcnow() + timedelta(seconds=policy.interval_seconds)
                self.finish()
            run = self.session.scalar(select(MonitorRun).where(MonitorRun.job_id == existing.id))
            assert run is not None
            return {"job_id": existing.id, "monitor_run_id": run.id, "deduplicated": True}
        now = utcnow()
        if automatic and monitor.last_fingerprint == decision.delta.fingerprint:
            monitor.next_check_at = now + timedelta(seconds=policy.interval_seconds)
            self.finish()
            return {"unchanged": True}
        if (
            decision.level in {"T2", "T3"}
            and monitor.cooldown_until
            and utc(monitor.cooldown_until) > now
            and decision.level != "T3"
        ):
            raise EvidenceError("MONITOR_COOLDOWN", "处于冷却期，保留观察，不启动重复研究", 409)
        count = (
            self.session.scalar(
                select(func.count())
                .select_from(MonitorRun)
                .where(
                    MonitorRun.forecast_id == forecast_id,
                    MonitorRun.created_at >= now - timedelta(days=1),
                )
            )
            or 0
        )
        if count >= policy.max_daily_jobs:
            raise EvidenceError("MONITOR_DAILY_BUDGET", "本预测已达每日任务预算", 429)
        freeze_engine(engine_code_hash())
        job = Job(
            user_id=ADMIN_ID,
            task_type="m5_monitor",
            idempotency_key=key,
            input_hash=digest,
            payload={"label": old_version.label},
        )
        self.session.add(job)
        self.session.flush()
        run = MonitorRun(
            id=uuid4(),
            forecast_id=forecast_id,
            old_version_id=old_version.id,
            job_id=job.id,
            snapshot=new.model_dump(mode="json"),
            assertions=[a.model_dump(mode="json") for a in data.assertions],
            decision=decision.model_dump(mode="json"),
            engine_code_hash=engine_code_hash(),
            verified_by=actor,
        )
        self.session.add(run)
        self.session.add(
            OutboxEvent(
                job_id=job.id,
                event_type="TurningPointCandidateDetected.v1",
                payload={"monitor_run_id": str(run.id), "label": old_version.label},
            )
        )
        monitor.last_fingerprint = decision.delta.fingerprint
        monitor.next_check_at = now + timedelta(seconds=policy.interval_seconds)
        self.finish()
        return {"job_id": job.id, "monitor_run_id": run.id, "deduplicated": False}

    def persist(self, job_id: UUID) -> MonitorResultV1:
        run = self.session.scalar(select(MonitorRun).where(MonitorRun.job_id == job_id))
        assert run is not None
        prior = self.session.get(MonitorOutcome, run.id)
        if prior:
            return MonitorResultV1.model_validate(prior.body)
        if run.engine_code_hash != engine_code_hash():
            raise ValueError("MONITOR_ENGINE_CHANGED")
        world = self.session.scalar(
            select(WorldForecast).where(WorldForecast.id == run.forecast_id).with_for_update()
        )
        assert world is not None
        old_row = self.session.get(ForecastVersion, run.old_version_id)
        assert old_row is not None
        old = M2DraftV1.model_validate(old_row.body)
        decision = TurningDecisionV1.model_validate(run.decision)
        new_version = None
        changes: tuple[str, ...] = ()
        outcome = "retained"
        reason = decision.rationale
        if world.current_version_id != run.old_version_id:
            reason = "基准版本已经更新，本任务保持旧版，不覆盖较新结论"
        elif decision.level == "T0":
            outcome = "archived"
        elif decision.level == "T1":
            outcome = "observed"
        elif old.target is None or old.target.target_end_at <= utcnow():
            reason = "原目标已到期，保留结果待评估，不改动验证窗口"
        else:
            snapshot = ResearchSnapshotV1.model_validate(run.snapshot)
            assertions = tuple(ChangeAssertionV1.model_validate(a) for a in run.assertions)
            removed = {
                a.prior_claim_id
                for a in assertions
                if a.kind in {"critical_assumption_broken", "resolution_source_revised"}
            }
            if removed:
                claims = tuple(c for c in snapshot.claims if c.claim_id not in removed)
                kept = {c.claim_id for c in claims}
                signals = []
                for signal in snapshot.signals:
                    ids = tuple(i for i in signal.claim_ids if i in kept)
                    if not ids:
                        continue
                    groups = tuple(sorted({c.source_group_id for c in claims if c.claim_id in ids}))
                    signals.append(
                        signal.model_copy(
                            update={
                                "claim_ids": ids,
                                "source_group_ids": groups,
                                "independent_source_count": len(groups),
                            }
                        )
                    )
                snapshot = snapshot.model_copy(update={"claims": claims, "signals": tuple(signals)})
            narrative = old.raw_narrative.model_copy(
                update={"cited_claim_ids": tuple(c.claim_id for c in snapshot.claims)}
            )
            new_run_id = uuid4()
            draft = build_forecast_draft(
                new_run_id, snapshot, narrative, "m5-incremental-v1", parent_version_id=old_row.id
            )
            fields = (
                "evidence_claim_ids",
                "contradiction_claim_ids",
                "baseline",
                "fusions",
                "mechanism_chain",
                "analogies",
                "kind",
            )
            changes = tuple(
                field
                for field in fields
                if old.model_dump(mode="json")[field] != draft.model_dump(mode="json")[field]
            )
            if changes:
                internal = Job(
                    user_id=ADMIN_ID,
                    task_type="m2_research",
                    idempotency_key="m5-incremental:" + str(run.id),
                    input_hash=draft.input_hash,
                    payload={"label": old.label},
                    status="succeeded",
                    attempts=1,
                )
                self.session.add(internal)
                self.session.flush()
                self.session.add(
                    ResearchRun(
                        id=new_run_id,
                        topic_id=world.topic_id,
                        creator_id=ADMIN_ID,
                        job_id=internal.id,
                        research_as_of=draft.research_as_of,
                        provider="incremental",
                        model_id=draft.model_id,
                        input_hash=draft.input_hash,
                        engine_code_hash=engine_code_hash(),
                        prompt_hash=draft.prompt_hash,
                        snapshot=snapshot.model_dump(mode="json"),
                        label=old.label,
                    )
                )
                self.session.flush()
                draft_result = ResearchRepository(self.session).persist_draft(new_run_id, draft)
                internal.result = draft_result.model_dump(mode="json")
                review = ReviewRepository(self.session, autocommit=False).review(draft.draft_id)
                if review.decision.publication_allowed:
                    version = ReviewRepository(self.session, autocommit=False).publish(
                        draft.draft_id,
                        PublishRequestV1(
                            review_id=review.report.critic_run_id,
                            change_reason=decision.level
                            + "：新核实资料导致的定向更新；原目标与旧版本保留",
                        ),
                    )
                    new_version = version.version_id
                    outcome = "published"
                    reason = "经独立 Critic 放行，冻结新的证据/基线版本；不声称预测准确率改善"
                else:
                    outcome = "review_blocked"
                    reason = "关键问题未通过独立审查，原版本保留并标记待核实；不发布新结论"
        result = MonitorResultV1.model_validate(
            {
                "monitor_run_id": run.id,
                "forecast_id": run.forecast_id,
                "old_version_id": run.old_version_id,
                "new_version_id": new_version,
                "level": decision.level,
                "outcome": outcome,
                "reason": reason,
                "changed_fields": changes,
                "refreshed_reports": 0,
            }
        )
        monitor = self.enroll(run.forecast_id)
        policy = MonitorPolicyV1.model_validate(monitor.policy)
        if decision.level in {"T2", "T3"}:
            monitor.cooldown_until = utcnow() + timedelta(seconds=policy.cooldown_seconds)
        monitor.last_error = None
        if outcome in {"published", "review_blocked"}:
            from infra.updates import queue_affected_reports

            count = queue_affected_reports(self.session, run, self.config)
            result = result.model_copy(update={"refreshed_reports": count})

        self.session.add(
            MonitorOutcome(
                run_id=run.id, new_version_id=new_version, body=result.model_dump(mode="json")
            )
        )
        return result


def pending_notice(session: Session, forecast_id: UUID) -> MonitorOutcome | None:
    world = session.get(WorldForecast, forecast_id)
    if world is None:
        return None
    return session.scalar(
        select(MonitorOutcome)
        .join(MonitorRun, MonitorRun.id == MonitorOutcome.run_id)
        .where(
            MonitorRun.forecast_id == forecast_id,
            MonitorRun.old_version_id == world.current_version_id,
            MonitorOutcome.body["outcome"].as_string() == "review_blocked",
        )
        .order_by(MonitorOutcome.created_at.desc())
        .limit(1)
    )
