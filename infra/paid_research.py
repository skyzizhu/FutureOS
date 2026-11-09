"""Guided scope/paid service orchestration; private profiles never enter shared research."""

import time
from datetime import timedelta
from typing import Any
from uuid import UUID, uuid4, uuid5

from prediction_engine.contracts.models import (
    MonitorCheckRequestV1,
    MonitorPolicyV1,
    PaidResearchAcceptedV1,
    PaidResearchSubmitV1,
    PeriodicResearchRequestV1,
    PublishRequestV1,
    ResearchQuoteV1,
    ResearchScopeV1,
    UserReportResultV1,
)
from prediction_engine.evidence.temporal import utc
from prediction_engine.forecasting.workflow import (
    build_forecast_draft,
    hashed,
    input_hash,
    mock_narrative,
    narrative_messages,
)
from prediction_engine.reporting.builder import build_private_report
from prediction_engine.turning_points.rules import classify
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from infra.billing import BillingRepository, commerce_gate
from infra.costs import record_cost
from infra.db import (
    ForecastVersion,
    InAppNotification,
    Job,
    OutboxEvent,
    PaidResearchRequest,
    PaidResearchReservation,
    ReportCatalogEntry,
    ResearchCreditGrant,
    ResearchRun,
    ResearchRunClaim,
    ResearchRunObservation,
    ResearchRunSource,
    ResearchScopeQuote,
    ResearchTopic,
    SharedTopicStudy,
    UserResearchTopic,
    WorldForecast,
    utcnow,
)
from infra.engine_artifacts import freeze_engine
from infra.evidence_repository import EvidenceError, EvidenceRepository, stable_id
from infra.job_budget import enforce_queue_budget
from infra.monitoring import MonitorRepository
from infra.notifications import queue_eligible_mail
from infra.profiles import ProfileRepository
from infra.report_demo import CATALOG, ensure_demo_catalog
from infra.reports import ReportRepository
from infra.research_repository import ResearchRepository, engine_code_hash
from infra.review_repository import ReviewRepository
from infra.settings import Settings
from scripts.seed_demo import ADMIN_ID

RULES = (
    "新主题完整报告预留1份套餐额度，成功后扣除；失败/取消归还，不使用首次免费权益。",
    "已完成原主题的更新免费；共享世界研究可复用，新主题私有报告仍按1份计。",
    "周期研究另行明确开启，每期完整服务使用1份套餐额度；关闭邮件不停止研究。",
    "当前只演示标准化范围的合成资料，不调用付费模型，也不作为现实行动依据。",
)


def scope_hash(scope: ResearchScopeV1) -> str:
    return hashed({"version": "m6-scope-v1", "scope": scope.model_dump(mode="json")})


class PaidResearchRepository:
    def __init__(self, session: Session, config: Settings) -> None:
        self.session, self.config = session, config
        self.billing = BillingRepository(session, config)

    def ensure_study(self, scope: ResearchScopeV1) -> str:
        fingerprint = scope_hash(scope)
        insert = (
            pg_insert
            if self.session.bind is not None and self.session.bind.dialect.name == "postgresql"
            else sqlite_insert
        )
        self.session.execute(
            insert(SharedTopicStudy)
            .values(scope_fingerprint=fingerprint, scope=scope.model_dump(mode="json"))
            .on_conflict_do_nothing(index_elements=["scope_fingerprint"])
        )
        return fingerprint

    def topic(self, user_id: UUID, fingerprint: str) -> UserResearchTopic | None:
        return self.session.scalar(
            select(UserResearchTopic).where(
                UserResearchTopic.user_id == user_id,
                UserResearchTopic.scope_fingerprint == fingerprint,
            )
        )

    def quote(self, user_id: UUID, scope: ResearchScopeV1, commit: bool = True) -> ResearchQuoteV1:
        commerce_gate(self.config)
        self.billing.lock_user(user_id)
        ProfileRepository(self.session, self.config).view(user_id)
        fingerprint = self.ensure_study(scope)
        topic = self.topic(user_id, fingerprint)
        report_id = topic.latest_report_id if topic else None
        quote = ResearchQuoteV1(
            quote_id=uuid4(),
            scope=scope,
            scope_fingerprint=fingerprint,
            kind="existing_topic" if report_id else "new_topic",
            units_required=0 if report_id else 1,
            existing_report_id=report_id,
            expires_at=utcnow() + timedelta(minutes=15),
            rules=RULES,
        )
        self.session.add(
            ResearchScopeQuote(
                id=quote.quote_id,
                user_id=user_id,
                scope_fingerprint=fingerprint,
                body=quote.model_dump(mode="json"),
                expires_at=quote.expires_at,
            )
        )
        if commit:
            self.session.commit()
        else:
            self.session.flush()
        return quote

    def submit(
        self,
        user_id: UUID,
        data: PaidResearchSubmitV1,
        key: str,
        purpose: str = "manual",
        subscription_id: UUID | None = None,
        commit: bool = True,
    ) -> PaidResearchAcceptedV1:
        commerce_gate(self.config)
        self.billing.lock_user(user_id)
        self.billing.expire(user_id)
        row = self.session.get(ResearchScopeQuote, data.quote_id)
        if row is None or row.user_id != user_id:
            raise EvidenceError("RESEARCH_QUOTE_NOT_FOUND", "范围确认不存在", 404)
        quote = ResearchQuoteV1.model_validate(row.body)
        digest = hashed([data.model_dump(mode="json"), purpose, str(subscription_id)])
        prior = self.session.scalar(
            select(Job).where(Job.user_id == user_id, Job.idempotency_key == "m6:" + key)
        )
        if prior:
            if prior.task_type != "m6_research" or prior.input_hash != digest:
                raise EvidenceError("IDEMPOTENCY_CONFLICT", "相同请求键不能更换研究范围", 409)
            request = self.session.get(PaidResearchRequest, prior.id)
            assert request is not None
            if commit:
                self.session.commit()
            return PaidResearchAcceptedV1(
                action="queued",
                job_id=prior.id,
                user_topic_id=request.user_topic_id,
                reserved_units=1
                if prior.status in {"queued", "running", "failed_retryable"}
                else 0,
                deduplicated=True,
            )
        if utc(row.expires_at) <= utcnow():
            raise EvidenceError("RESEARCH_QUOTE_EXPIRED", "范围确认已过期，请重新确认", 409)
        topic = self.topic(user_id, row.scope_fingerprint)
        if topic is not None and topic.latest_report_id and purpose == "manual":
            from infra.updates import queue_refresh

            result = queue_refresh(
                self.session,
                self.config,
                user_id,
                topic.latest_report_id,
                "本人复查已完成原主题：免费更新",
            )
            if commit:
                self.session.commit()
            return PaidResearchAcceptedV1(
                action="queued" if result.get("job_id") else "existing_report",
                job_id=result.get("job_id"),
                report_id=topic.latest_report_id,
                user_topic_id=topic.id,
                reserved_units=0,
            )
        if topic is None:
            topic = UserResearchTopic(
                id=uuid4(),
                user_id=user_id,
                scope_fingerprint=row.scope_fingerprint,
                latest_report_id=None,
                subscription_id=None,
                periodic_enabled=False,
            )
            self.session.add(topic)
            self.session.flush()
        pending = self.session.scalar(
            select(Job)
            .join(PaidResearchRequest, PaidResearchRequest.job_id == Job.id)
            .where(
                PaidResearchRequest.user_topic_id == topic.id,
                Job.status.in_(["queued", "running", "failed_retryable"]),
            )
        )
        if pending:
            if commit:
                self.session.commit()
            return PaidResearchAcceptedV1(
                action="queued",
                job_id=pending.id,
                user_topic_id=topic.id,
                reserved_units=1,
                deduplicated=True,
            )
        enforce_queue_budget(self.session, user_id, self.config.queue_max_pending_per_user)
        snapshot = ProfileRepository(self.session, self.config).snapshot(user_id)
        freeze_engine(engine_code_hash())
        job = Job(
            user_id=user_id,
            task_type="m6_research",
            idempotency_key="m6:" + key,
            input_hash=digest,
            payload={"label": quote.scope.label},
        )
        self.session.add(job)
        self.session.flush()
        reservation = self.billing.reserve(user_id, job.id, subscription_id)
        self.session.add(
            PaidResearchRequest(
                job_id=job.id,
                user_id=user_id,
                user_topic_id=topic.id,
                profile_snapshot_id=snapshot.snapshot_id,
                reservation_id=reservation.id,
                purpose=purpose,
                engine_code_hash=engine_code_hash(),
            )
        )
        self.session.add(
            OutboxEvent(
                job_id=job.id,
                event_type="PaidResearchRequested.v1",
                payload={"job_id": str(job.id), "label": quote.scope.label},
            )
        )
        if commit:
            self.session.commit()
        else:
            self.session.flush()
        return PaidResearchAcceptedV1(
            action="queued", job_id=job.id, user_topic_id=topic.id, reserved_units=1
        )

    def schedule(
        self, user_id: UUID, topic_id: UUID, data: PeriodicResearchRequestV1
    ) -> dict[str, Any]:
        commerce_gate(self.config)
        self.billing.lock_user(user_id)
        self.billing.expire(user_id)
        topic = self.session.get(UserResearchTopic, topic_id)
        if topic is None or topic.user_id != user_id:
            raise EvidenceError("RESEARCH_TOPIC_NOT_FOUND", "研究主题不存在", 404)
        subscription = self.billing.subscription_owned(user_id, data.subscription_id)
        if subscription.status != "active" or utc(subscription.ends_at) <= utcnow():
            raise EvidenceError("SUBSCRIPTION_INACTIVE", "订阅不在有效期内", 409)
        if not topic.periodic_enabled or topic.subscription_id != subscription.id:
            topic.subscription_id = subscription.id
            topic.periodic_enabled = True
            topic.next_run_at = utcnow() + timedelta(days=subscription.cadence_days)
        topic.last_error = None
        self.session.commit()
        return {
            "ok": True,
            "next_run_at": topic.next_run_at,
            "cadence_days": subscription.cadence_days,
        }


def prepare_paid(engine: Engine, job_id: UUID, config: Settings) -> None:
    commerce_gate(config)
    with Session(engine) as session:
        request = session.get(PaidResearchRequest, job_id)
        if request is None:
            raise ValueError("PAID_RESEARCH_REQUEST_MISSING")
        topic = session.get(UserResearchTopic, request.user_topic_id)
        assert topic is not None
        study = session.get(SharedTopicStudy, topic.scope_fingerprint)
        assert study is not None
        scope = ResearchScopeV1.model_validate(study.scope)
    if scope.label != "DEMO":
        raise ValueError("REAL_CUSTOM_RESEARCH_NOT_ENABLED")
    domain = dict(CATALOG)[scope.domain]
    ensure_demo_catalog(engine, config, (domain,))


def resolve_study(
    session: Session, study: SharedTopicStudy, job_id: UUID, config: Settings
) -> tuple[UUID, bool]:
    scope = ResearchScopeV1.model_validate(study.scope)
    if study.forecast_id:
        world = session.get(WorldForecast, study.forecast_id)
        assert world is not None and world.current_version_id is not None
        current = session.get(ForecastVersion, world.current_version_id)
        assert current is not None
        repo = MonitorRepository(session, config, autocommit=False)
        old, new = repo.snapshot_for(current), repo.latest_inputs(current)
        monitor = repo.enroll(world.id)
        decision = classify(old, new, MonitorPolicyV1.model_validate(monitor.policy))
        if decision.level in {"T2", "T3"}:
            accepted = repo.enqueue(world.id, MonitorCheckRequestV1())
            internal = session.get(Job, accepted["job_id"])
            assert internal is not None
            if not accepted.get("deduplicated") and internal.status == "queued":
                result = repo.persist(internal.id)
                if result.outcome == "review_blocked":
                    raise ValueError("PAID_RESEARCH_REVIEW_BLOCKED")
                internal.result = result.model_dump(mode="json")
                internal.status = "succeeded"
                session.add(
                    OutboxEvent(
                        job_id=internal.id,
                        event_type="TurningPointReviewed.v1",
                        payload={"label": scope.label},
                    )
                )
            elif internal.status != "succeeded":
                raise ValueError("SHARED_REVIEW_IN_PROGRESS")
        study.checked_at = utcnow()
        session.flush()
        assert world.current_version_id is not None
        return world.current_version_id, True
    catalog = session.get(ReportCatalogEntry, scope.domain)
    if catalog is None:
        raise ValueError("DEMO_SCOPE_CATALOG_MISSING")
    base = session.get(ForecastVersion, catalog.forecast_version_id)
    assert base is not None
    snapshot = MonitorRepository(session, config).snapshot_for(base)
    assert snapshot.request.target is not None
    target = snapshot.request.target.model_copy(
        update={
            "population_scope": (
                f"DEMO {scope.domain} {scope.population} {scope.focus} isolated synthetic trial"
            ),
            "geography": scope.geography,
            "target_start_at": utcnow() + timedelta(days=1),
            "target_end_at": utcnow() + timedelta(days=90),
        }
    )
    request = snapshot.request.model_copy(
        update={
            "title": (
                f"DEMO guided {scope.domain}/{scope.focus}/{scope.population}/{scope.geography}"
            ),
            "scope": "Standardized synthetic scope " + study.scope_fingerprint,
            "research_as_of": utcnow(),
            "target": target,
        }
    )
    snapshot = ResearchRepository(session).snapshot(request)
    topic_id = stable_id("m6-shared-topic:" + study.scope_fingerprint)
    EvidenceRepository(session).ensure(
        ResearchTopic,
        {
            "id": topic_id,
            "owner_user_id": None,
            "title": request.title,
            "scope": request.scope,
            "domain_tags": [tag.value for tag in request.domain_tags],
            "version": 1,
            "label": scope.label,
        },
    )
    run_id = uuid5(job_id, "shared-run")
    internal = Job(
        user_id=ADMIN_ID,
        task_type="m2_research",
        idempotency_key="m6-shared:" + study.scope_fingerprint,
        input_hash=input_hash(snapshot),
        payload={"label": scope.label},
        status="succeeded",
        attempts=1,
    )
    session.add(internal)
    session.flush()
    draft = build_forecast_draft(run_id, snapshot, mock_narrative(snapshot), "mock-research-v1")
    session.add(
        ResearchRun(
            id=run_id,
            topic_id=topic_id,
            creator_id=ADMIN_ID,
            job_id=internal.id,
            research_as_of=request.research_as_of,
            provider="mock",
            model_id=draft.model_id,
            input_hash=draft.input_hash,
            engine_code_hash=engine_code_hash(),
            prompt_hash=hashed(narrative_messages(snapshot)),
            snapshot=snapshot.model_dump(mode="json"),
            label=scope.label,
        )
    )
    session.flush()
    session.add_all(
        ResearchRunSource(run_id=run_id, source_version_id=s.source_version_id)
        for s in snapshot.sources
    )
    session.add_all(ResearchRunClaim(run_id=run_id, claim_id=c.claim_id) for c in snapshot.claims)
    session.add_all(
        ResearchRunObservation(run_id=run_id, observation_id=o.observation_id)
        for o in snapshot.observations
    )
    session.flush()
    draft_result = ResearchRepository(session).persist_draft(run_id, draft)
    internal.result = draft_result.model_dump(mode="json")
    review = ReviewRepository(session, autocommit=False).review(draft.draft_id)
    if not review.decision.publication_allowed:
        raise ValueError("PAID_RESEARCH_REVIEW_BLOCKED")
    version = ReviewRepository(session, autocommit=False).publish(
        draft.draft_id,
        PublishRequestV1(
            review_id=review.report.critic_run_id,
            change_reason="M6 shared standardized DEMO scope; no real research claim",
        ),
    )
    study.forecast_id = version.forecast_id
    study.checked_at = utcnow()
    return version.version_id, False


def persist_paid(session: Session, job_id: UUID, config: Settings) -> UserReportResultV1:
    commerce_gate(config)
    request = session.get(PaidResearchRequest, job_id)
    assert request is not None
    reservation = session.get(PaidResearchReservation, request.reservation_id)
    assert reservation is not None
    if reservation.state != "reserved" or utc(reservation.expires_at) <= utcnow():
        raise ValueError("PAID_RESERVATION_EXPIRED")
    if request.engine_code_hash != engine_code_hash():
        raise ValueError("PAID_RESEARCH_ENGINE_CHANGED")
    topic = session.get(UserResearchTopic, request.user_topic_id)
    assert topic is not None
    study = session.scalar(
        select(SharedTopicStudy)
        .where(SharedTopicStudy.scope_fingerprint == topic.scope_fingerprint)
        .with_for_update()
    )
    assert study is not None
    profile = ProfileRepository(session, config).read_snapshot(
        request.profile_snapshot_id, request.user_id
    )
    current = ProfileRepository(session, config).view(request.user_id)
    if profile.profile.use_optional_fields and not current.profile.use_optional_fields:
        raise ValueError("REPORT_CONSENT_WITHDRAWN")
    started = time.monotonic()
    version_id, reused = resolve_study(session, study, job_id, config)
    record_cost(
        session,
        job_id,
        "shared_research",
        "resolve",
        int((time.monotonic() - started) * 1000),
        reused,
    )
    forecast = ReportRepository(session, config).public_forecast(version_id, request.user_id)
    started = time.monotonic()
    body = build_private_report(
        uuid5(job_id, "paid-report"),
        uuid5(job_id, "paid-report-v1"),
        profile,
        (forecast,),
        max(utc(request.created_at), forecast[0].published_at),
    )
    body = body.model_copy(
        update={
            "limitations": (*body.limitations, "标准化主题的本地沙盒研究，非自由问题的真实定制预测")
        }
    )
    ReportRepository(session, config).store_new(body)
    BillingRepository(session, config).consume(reservation)
    topic.latest_report_id = body.report_id
    topic.last_error = None
    session.add(
        InAppNotification(
            id=uuid5(job_id, "paid-notification"),
            user_id=body.user_id,
            report_id=body.report_id,
            report_version_id=body.report_version_id,
            title="周期研究报告已完成" if request.purpose == "periodic" else "新主题研究报告已完成",
            summary="已生成固定版本报告；成功使用1份套餐额度，原主题重大更新仍免费",
        )
    )
    queue_eligible_mail(
        session,
        config,
        body.user_id,
        body.report_version_id,
        "digest" if request.purpose == "periodic" else "alert",
    )
    record_cost(
        session, job_id, "personalization", "report", int((time.monotonic() - started) * 1000)
    )
    return UserReportResultV1(
        report_id=body.report_id, report_version_id=body.report_version_id, label=body.label
    )


def schedule_paid(engine: Engine, config: Settings) -> dict[str, int]:
    if not config.sandbox_commerce_enabled:
        return {"queued": 0, "errors": 0}
    queued = errors = 0
    with Session(engine) as session:
        users = list(session.scalars(select(ResearchCreditGrant.user_id).distinct()))
    for user_id in users:
        with Session(engine) as session:
            billing = BillingRepository(session, config)
            billing.lock_user(user_id)
            billing.expire(user_id)
            session.commit()
    with Session(engine) as session:
        identifiers = list(
            session.scalars(
                select(UserResearchTopic.id)
                .where(
                    UserResearchTopic.periodic_enabled.is_(True),
                    UserResearchTopic.next_run_at <= utcnow(),
                )
                .order_by(UserResearchTopic.next_run_at)
                .limit(100)
            )
        )
    for identifier in identifiers:
        with Session(engine) as session:
            topic = session.get(UserResearchTopic, identifier)
            assert topic is not None
            billing = BillingRepository(session, config)
            billing.lock_user(topic.user_id)
            session.refresh(topic, with_for_update=True)
            if (
                not topic.periodic_enabled
                or topic.next_run_at is None
                or utc(topic.next_run_at) > utcnow()
            ):
                continue
            if topic.subscription_id is None:
                topic.periodic_enabled = False
                session.commit()
                continue
            subscription = billing.subscription_owned(topic.user_id, topic.subscription_id)
            if subscription.status != "active" or utc(subscription.ends_at) <= utcnow():
                topic.periodic_enabled = False
                session.commit()
                continue
            slot = utc(topic.next_run_at).isoformat()
            repo = PaidResearchRepository(session, config)
            study = session.get(SharedTopicStudy, topic.scope_fingerprint)
            assert study is not None
            try:
                with session.begin_nested():
                    quote = repo.quote(
                        topic.user_id, ResearchScopeV1.model_validate(study.scope), commit=False
                    )
                    result = repo.submit(
                        topic.user_id,
                        PaidResearchSubmitV1(quote_id=quote.quote_id, accept_usage_rules=True),
                        "periodic:" + str(topic.id) + ":" + slot,
                        purpose="periodic",
                        subscription_id=subscription.id,
                        commit=False,
                    )
                    queued += not result.deduplicated
                topic.next_run_at = utcnow() + timedelta(days=subscription.cadence_days)
                topic.last_error = None
            except EvidenceError as exc:
                topic.last_error = exc.code
                topic.next_run_at = utcnow() + timedelta(hours=1)
                errors += 1
            session.commit()
    return {"queued": queued, "errors": errors}
