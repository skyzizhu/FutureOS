"""Private report orchestration, atomic one-report quota and ownership on every read."""

from datetime import timedelta
from typing import Any
from uuid import UUID, uuid4, uuid5

from prediction_engine.contracts.models import (
    EmailAuthorizationV1,
    EmailPreviewV1,
    FirstReportRequestV1,
    FreeReportEntitlementV1,
    JobAcceptedV1,
    LocalDeliveryV1,
    PrivateReportV1,
    ProfileInputV1,
    RecommendationFeedbackV1,
    RecommendationV1,
    ReportSummaryV1,
    ResearchIntakeResultV1,
    ResearchIntakeV1,
    UserReportResultV1,
)
from prediction_engine.evidence.temporal import utc
from prediction_engine.forecasting.workflow import hashed
from prediction_engine.personalization.taxonomy import industry
from prediction_engine.reporting.builder import build_private_report
from sqlalchemy import func, select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from infra.accounts import AccountRepository, normalized_email, vault_for
from infra.db import (
    EntitlementReservation,
    ForecastVersion,
    Job,
    LocalEmailDelivery,
    OutboxEvent,
    PersonalImpact,
    Recommendation,
    RecommendationFeedback,
    ReportBuildInput,
    ReportCatalogEntry,
    ReportRequest,
    ReportVersionForecast,
    ResearchTopic,
    UsageLedger,
    User,
    UserEntitlement,
    UserReport,
    UserReportVersion,
    WorldForecast,
    utcnow,
)
from infra.engine_artifacts import freeze_engine
from infra.evidence_repository import EvidenceError
from infra.profiles import ProfileRepository
from infra.report_demo import ensure_demo_catalog
from infra.research_repository import engine_code_hash
from infra.review_repository import ReviewRepository
from infra.settings import Settings


class ReportRepository:
    def __init__(self, session: Session, config: Settings) -> None:
        self.session = session
        self.config = config

    def entitlement(self, user_id: UUID) -> FreeReportEntitlementV1:
        consumed = (
            self.session.scalar(
                select(func.count())
                .select_from(UsageLedger)
                .where(UsageLedger.user_id == user_id, UsageLedger.entry_kind == "consumed")
            )
            or 0
        )
        reserved = (
            self.session.scalar(
                select(func.count())
                .select_from(EntitlementReservation)
                .where(
                    EntitlementReservation.user_id == user_id,
                    EntitlementReservation.state == "reserved",
                )
            )
            or 0
        )
        return FreeReportEntitlementV1(
            available=max(0, 1 - consumed - reserved),
            reserved=min(1, reserved),
            consumed=min(1, consumed),
        )

    def release(self, job_id: UUID) -> None:
        row = self.session.scalar(
            select(EntitlementReservation)
            .where(EntitlementReservation.job_id == job_id)
            .with_for_update()
        )
        if row is None or row.state != "reserved":
            return
        row.state = "released"
        self.session.add(
            UsageLedger(
                id=uuid5(job_id, "released"),
                user_id=row.user_id,
                job_id=job_id,
                reservation_id=row.id,
                entry_kind="released",
                units_delta=0,
            )
        )

    def cancel(self, user_id: UUID, job_id: UUID, commit: bool = True) -> None:
        job = self.session.scalar(
            select(Job)
            .where(
                Job.id == job_id,
                Job.user_id == user_id,
                Job.task_type.in_(["m4_report", "m5_report_refresh"]),
            )
            .with_for_update()
        )
        if job is None:
            raise EvidenceError("JOB_NOT_FOUND", "报告任务不存在", 404)
        if job.status in {"queued", "running", "failed_retryable"}:
            job.status = "cancelled"
            job.lease_token = None
            job.lease_until = None
            job.error_code = "USER_CANCELLED"
            self.release(job.id)
        if commit:
            self.session.commit()

    def expire(self, user_id: UUID) -> None:
        for row in self.session.scalars(
            select(EntitlementReservation).where(
                EntitlementReservation.user_id == user_id,
                EntitlementReservation.state == "reserved",
                EntitlementReservation.expires_at < utcnow(),
            )
        ):
            job = self.session.scalar(
                select(Job).where(Job.id == row.job_id).with_for_update(skip_locked=True)
            )
            if job is None or (
                job.status == "running" and job.lease_until and utc(job.lease_until) > utcnow()
            ):
                continue
            if job.status not in {"succeeded", "cancelled"}:
                job.status = "failed_terminal"
                job.error_code = "RESERVATION_EXPIRED"
                job.lease_token = None
                job.lease_until = None
            self.release(job.id)
        self.session.flush()

    def submit(self, user_id: UUID, data: FirstReportRequestV1, key: str) -> JobAcceptedV1:
        self.session.scalar(select(User).where(User.id == user_id).with_for_update(key_share=True))
        digest = hashed({"task": "m4_report", "request": data.model_dump(mode="json")})
        prior = self.session.scalar(
            select(Job).where(Job.user_id == user_id, Job.idempotency_key == key)
        )
        if prior:
            if prior.task_type != "m4_report" or prior.input_hash != digest:
                raise EvidenceError("IDEMPOTENCY_CONFLICT", "同键不能更换报告请求", 409)
            return JobAcceptedV1(job_id=prior.id, request_id=prior.request_id)
        if len(set(data.forecast_version_ids)) != len(data.forecast_version_ids):
            raise EvidenceError("REPORT_DUPLICATE_VERSION", "同一预测版本不能重复计入报告", 422)
        self.expire(user_id)
        if self.entitlement(user_id).available != 1:
            # A concurrent identical request may have committed after the first lookup.
            # Observe that durable job before reporting that its reservation used the quota.
            prior = self.session.scalar(
                select(Job).where(Job.user_id == user_id, Job.idempotency_key == key)
            )
            if prior:
                if prior.task_type != "m4_report" or prior.input_hash != digest:
                    raise EvidenceError("IDEMPOTENCY_CONFLICT", "同键不能更换报告请求", 409)
                return JobAcceptedV1(job_id=prior.id, request_id=prior.request_id)
            raise EvidenceError("FIRST_REPORT_UNAVAILABLE", "首次报告额度已预留或已使用", 409)
        snapshot = ProfileRepository(self.session, self.config).snapshot(user_id)
        for identifier in data.forecast_version_ids:
            self.public_forecast(identifier, user_id, data.label)
        job = Job(
            user_id=user_id,
            task_type="m4_report",
            idempotency_key=key,
            input_hash=digest,
            payload={"label": data.label},
        )
        self.session.add(job)
        self.session.flush()
        reservation = EntitlementReservation(
            id=uuid4(),
            user_id=user_id,
            job_id=job.id,
            state="reserved",
            expires_at=utcnow() + timedelta(minutes=15),
        )
        self.session.add(reservation)
        self.session.flush()
        if self.session.get(UserEntitlement, user_id) is None:
            self.session.add(UserEntitlement(user_id=user_id))
        self.session.add(
            ReportRequest(
                id=job.request_id,
                user_id=user_id,
                job_id=job.id,
                profile_snapshot_id=snapshot.snapshot_id,
                reservation_id=reservation.id,
                label=data.label,
                forecast_version_ids=[str(i) for i in data.forecast_version_ids],
            )
        )
        self.session.add(
            OutboxEvent(
                job_id=job.id,
                event_type="FirstReportRequested.v1",
                payload={"job_id": str(job.id), "label": data.label},
            )
        )
        self.session.commit()
        return JobAcceptedV1(job_id=job.id, request_id=job.request_id)

    def public_forecast(
        self, identifier: UUID, user_id: UUID, label: str | None = None
    ) -> tuple[Any, tuple[str, ...]]:
        row = self.session.get(ForecastVersion, identifier)
        if row is None or (label and row.label != label):
            raise EvidenceError("FORECAST_NOT_FOUND", "过审版本不存在或标签不符", 404)
        world = self.session.get(WorldForecast, row.forecast_id)
        topic = self.session.get(ResearchTopic, world.topic_id) if world else None
        if topic is None or (topic.owner_user_id is not None and topic.owner_user_id != user_id):
            raise EvidenceError("FORECAST_NOT_FOUND", "预测不可访问", 404)
        version = ReviewRepository(self.session).version_view(identifier)
        return version, tuple(topic.domain_tags)

    def select_forecasts(
        self, user_id: UUID, label: str, profile: ProfileInputV1 | None = None
    ) -> tuple[tuple[Any, tuple[str, ...]], ...]:
        profile = profile or ProfileRepository(self.session, self.config).view(user_id).profile
        tags = set(industry(profile.industry_l1_code, profile.industry_l2_code)["domain_tags"])
        if label == "DEMO":
            ids = list(
                self.session.scalars(
                    select(ReportCatalogEntry.forecast_version_id).order_by(ReportCatalogEntry.code)
                )
            )
        else:
            ids = list(
                self.session.scalars(
                    select(ForecastVersion.id)
                    .join(WorldForecast, WorldForecast.current_version_id == ForecastVersion.id)
                    .where(ForecastVersion.label == "REAL")
                )
            )
        versions = [self.public_forecast(i, user_id, label) for i in ids]
        versions = [
            v
            for v in versions
            if v[0].body.target is not None and v[0].body.target.target_end_at > utcnow()
        ]
        versions.sort(key=lambda v: (-len(tags & set(v[1])), str(v[0].version_id)))
        return tuple(versions[:3])

    def intake(self, user_id: UUID, data: ResearchIntakeV1) -> ResearchIntakeResultV1:
        profile = ProfileRepository(self.session, self.config).view(user_id)
        matches = self.select_forecasts(user_id, data.label)
        return ResearchIntakeResultV1(
            scope="首份行业观察报告，复用已过审世界预测；不扩展付费新主题",
            matched_version_ids=tuple(v.version_id for v, _ in matches),
            available_free_reports=self.entitlement(user_id).available,
            additional_questions=(
                () if profile.profile.goals else ("可选：你希望观察哪个任务或目标？可以不填",)
            ),
            limitations=(
                "提问仅用于范围确认，不自动调用模型或扣额度",
                "明确提交后才预留首次报告权益",
                "尚无过审资料时会明确提示或释放额度，不编造结论",
            ),
        )

    def store_new(self, body: PrivateReportV1) -> None:
        vault = vault_for(self.session, self.config)
        self.session.add(
            UserReport(
                id=body.report_id,
                user_id=body.user_id,
                current_version_id=None,
                created_at=body.created_at,
            )
        )
        self.session.flush()
        self.session.add(
            UserReportVersion(
                id=body.report_version_id,
                report_id=body.report_id,
                user_id=body.user_id,
                profile_snapshot_id=body.profile_snapshot_id,
                version_num=1,
                label=body.label,
                ciphertext=vault.seal(
                    body.model_dump(mode="json"),
                    "report:" + str(body.user_id) + ":" + str(body.report_version_id),
                ),
                immutable_hash=hashed(body.model_dump(mode="json")),
                created_at=body.created_at,
            )
        )
        self.session.flush()
        self.session.add_all(
            ReportVersionForecast(report_version_id=body.report_version_id, forecast_version_id=i)
            for i in body.forecast_version_ids
        )
        self.session.flush()
        for impact in (*body.primary_impacts, *body.observation_only):
            self.session.add(
                PersonalImpact(
                    id=impact.impact_id,
                    user_id=body.user_id,
                    report_version_id=body.report_version_id,
                    profile_snapshot_id=body.profile_snapshot_id,
                    forecast_version_id=impact.forecast_version_id,
                    ciphertext=vault.seal(
                        impact.model_dump(mode="json"),
                        "impact:" + str(body.user_id) + ":" + str(impact.impact_id),
                    ),
                )
            )
        self.session.flush()
        for action in body.recommendations:
            self.session.add(
                Recommendation(
                    id=action.recommendation_id,
                    user_id=body.user_id,
                    report_version_id=body.report_version_id,
                    impact_id=action.impact_id,
                    ciphertext=vault.seal(
                        action.model_dump(mode="json"),
                        "recommendation:" + str(body.user_id) + ":" + str(action.recommendation_id),
                    ),
                )
            )
        report = self.session.get(UserReport, body.report_id)
        assert report is not None
        report.current_version_id = body.report_version_id
        self.session.flush()

    def persist(self, job_id: UUID, body: PrivateReportV1) -> UserReportResultV1:
        request = self.session.scalar(select(ReportRequest).where(ReportRequest.job_id == job_id))
        if (
            request is None
            or request.user_id != body.user_id
            or request.profile_snapshot_id != body.profile_snapshot_id
        ):
            raise ValueError("REPORT_OWNER_OR_SNAPSHOT_MISMATCH")
        reservation = self.session.get(EntitlementReservation, request.reservation_id)
        if (
            reservation is None
            or reservation.state != "reserved"
            or utc(reservation.expires_at) <= utcnow()
        ):
            raise ValueError("REPORT_RESERVATION_EXPIRED")
        inputs = self.session.get(ReportBuildInput, job_id)
        if inputs is None or set(inputs.forecast_version_ids) != set(
            str(i) for i in body.forecast_version_ids
        ):
            raise ValueError("REPORT_FIXED_INPUT_MISMATCH")
        self.store_new(body)
        reservation.state = "consumed"
        self.session.flush()
        self.session.add(
            UsageLedger(
                id=uuid5(job_id, "consumed"),
                user_id=body.user_id,
                job_id=job_id,
                reservation_id=reservation.id,
                entry_kind="consumed",
                units_delta=-1,
            )
        )
        from infra.notifications import queue_eligible_mail

        queue_eligible_mail(
            self.session, self.config, body.user_id, body.report_version_id, "first_report"
        )
        return UserReportResultV1(
            report_id=body.report_id, report_version_id=body.report_version_id, label=body.label
        )

    def report(
        self, user_id: UUID, identifier: UUID, version_id: UUID | None = None
    ) -> PrivateReportV1:
        report = self.session.scalar(
            select(UserReport).where(UserReport.id == identifier, UserReport.user_id == user_id)
        )
        if report is None:
            raise EvidenceError("REPORT_NOT_FOUND", "报告不存在", 404)
        row = self.session.scalar(
            select(UserReportVersion).where(
                UserReportVersion.id == (version_id or report.current_version_id),
                UserReportVersion.user_id == user_id,
                UserReportVersion.report_id == identifier,
            )
        )
        if row is None:
            raise EvidenceError("REPORT_VERSION_NOT_FOUND", "报告版本不存在", 404)
        value = vault_for(self.session, self.config).open(
            row.ciphertext, "report:" + str(user_id) + ":" + str(row.id)
        )
        body = PrivateReportV1.model_validate(value)
        if hashed(value) != row.immutable_hash:
            raise EvidenceError("REPORT_HASH_MISMATCH", "报告完整性校验失败", 409)
        return body

    def summaries(self, user_id: UUID) -> list[ReportSummaryV1]:
        result = []
        for row in self.session.scalars(
            select(UserReport)
            .where(UserReport.user_id == user_id)
            .order_by(UserReport.created_at.desc())
        ):
            body = self.report(user_id, row.id)
            result.append(
                ReportSummaryV1(
                    report_id=body.report_id,
                    report_version_id=body.report_version_id,
                    version_num=body.version_num,
                    title=body.title,
                    label=body.label,
                    created_at=body.created_at,
                )
            )
        return result

    def recommendations(self, user_id: UUID) -> list[dict[str, Any]]:
        result = []
        vault = vault_for(self.session, self.config)
        for row in self.session.scalars(
            select(Recommendation).where(Recommendation.user_id == user_id)
        ):
            data = vault.open(row.ciphertext, "recommendation:" + str(user_id) + ":" + str(row.id))
            feedback = self.session.scalar(
                select(RecommendationFeedback)
                .where(
                    RecommendationFeedback.user_id == user_id,
                    RecommendationFeedback.recommendation_id == row.id,
                )
                .order_by(RecommendationFeedback.created_at.desc())
                .limit(1)
            )
            result.append(
                {
                    "recommendation": RecommendationV1.model_validate(data),
                    "feedback": feedback.status if feedback else None,
                }
            )
        return result

    def feedback(self, user_id: UUID, identifier: UUID, data: RecommendationFeedbackV1) -> None:
        row = self.session.scalar(
            select(Recommendation).where(
                Recommendation.id == identifier, Recommendation.user_id == user_id
            )
        )
        if row is None:
            raise EvidenceError("RECOMMENDATION_NOT_FOUND", "建议不存在", 404)
        self.session.add(
            RecommendationFeedback(
                user_id=user_id, recommendation_id=identifier, status=data.status
            )
        )
        self.session.commit()

    def email_preview(self, user: User, identifier: UUID) -> EmailPreviewV1:
        body = self.report(user.id, identifier)
        identity = AccountRepository(self.session, self.config).identity(user)
        return EmailPreviewV1(
            report_version_id=body.report_version_id,
            recipient_masked=identity.email_masked,
            subject="FutureOS：你的报告已就绪",
            summary="请登录后查看完整私有报告；摘要不包含个人画像。",
            private_link="/reports/" + str(identifier),
        )

    def authorize_email(
        self, user: User, identifier: UUID, data: EmailAuthorizationV1
    ) -> LocalDeliveryV1:
        self.session.scalar(select(User).where(User.id == user.id).with_for_update(key_share=True))
        preview = self.email_preview(user, identifier)
        actual = AccountRepository(self.session, self.config).recipient(user.id)
        if normalized_email(data.recipient) != actual:
            raise EvidenceError("EMAIL_RECIPIENT_MISMATCH", "只能授权发送到当前账号邮箱", 409)
        row = self.session.scalar(
            select(LocalEmailDelivery).where(LocalEmailDelivery.user_id == user.id)
        )
        if row is None:
            row = LocalEmailDelivery(
                id=uuid4(),
                user_id=user.id,
                report_version_id=preview.report_version_id,
                recipient_ciphertext=vault_for(self.session, self.config).seal(
                    {"email": actual}, "delivery:" + str(user.id)
                ),
            )
            self.session.add(row)
            self.session.commit()
        elif row.report_version_id != preview.report_version_id:
            raise EvidenceError("FIRST_EMAIL_ALREADY_AUTHORIZED", "首份报告模拟投递已使用", 409)
        return LocalDeliveryV1(
            delivery_id=row.id,
            report_version_id=row.report_version_id,
            consented_at=utc(row.consented_at),
        )


def execute_report(engine: Engine, job_id: UUID, config: Settings) -> PrivateReportV1:
    with Session(engine) as session:
        request = session.scalar(select(ReportRequest).where(ReportRequest.job_id == job_id))
        if request is None:
            raise ValueError("REPORT_REQUEST_MISSING")
        label = request.label
        frozen_profile = (
            ProfileRepository(session, config)
            .read_snapshot(request.profile_snapshot_id, request.user_id)
            .profile
        )
    if label == "DEMO":
        tags = tuple(
            industry(frozen_profile.industry_l1_code, frozen_profile.industry_l2_code)[
                "domain_tags"
            ]
        )
        ensure_demo_catalog(engine, config, tags)
    with Session(engine) as session:
        repo = ReportRepository(session, config)
        request = session.scalar(select(ReportRequest).where(ReportRequest.job_id == job_id))
        assert request is not None
        snapshot = ProfileRepository(session, config).read_snapshot(
            request.profile_snapshot_id, request.user_id
        )
        inputs = session.get(ReportBuildInput, job_id)
        if inputs is None:
            forecasts = (
                tuple(
                    repo.public_forecast(UUID(i), request.user_id, request.label)
                    for i in request.forecast_version_ids
                )
                if request.forecast_version_ids
                else repo.select_forecasts(request.user_id, request.label, snapshot.profile)
            )
            if not forecasts:
                raise ValueError("NO_APPROVED_FORECAST_AVAILABLE")
            code_hash = engine_code_hash()
            freeze_engine(code_hash)
            inputs = ReportBuildInput(
                job_id=job_id,
                forecast_version_ids=[str(v.version_id) for v, _ in forecasts],
                engine_code_hash=code_hash,
            )
            session.add(inputs)
            session.commit()
        if inputs.engine_code_hash != engine_code_hash():
            raise ValueError("REPORT_ENGINE_CHANGED_RETRY_MANUALLY")
        forecasts = tuple(
            repo.public_forecast(UUID(i), request.user_id, request.label)
            for i in inputs.forecast_version_ids
        )
        return build_private_report(
            uuid5(job_id, "report"),
            uuid5(job_id, "report-v1"),
            snapshot,
            forecasts,
            utc(inputs.created_at),
        )
