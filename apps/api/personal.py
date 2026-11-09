from collections.abc import Callable, Iterator
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, Header, Request
from prediction_engine.contracts.models import (
    AccountIdentityV1,
    AccountSessionV1,
    CountryCatalogV1,
    CountryOptionV1,
    EmailAuthorizationV1,
    EmailPreviewV1,
    FirstReportRequestV1,
    FreeReportEntitlementV1,
    JobAcceptedV1,
    LocalDeliveryV1,
    PersonalDataErasedV1,
    PersonalDataEraseV1,
    PrivateReportV1,
    ProfileInputV1,
    ProfileSnapshotV1,
    ProfileViewV1,
    ProtectedLoginV1,
    RecommendationFeedbackV1,
    ReportSummaryV1,
    ResearchIntakeResultV1,
    ResearchIntakeV1,
    VerifiedRegistrationV1,
)
from prediction_engine.personalization.taxonomy import TAXONOMY_VERSION, rows
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from apps.api.auth_access import auth_access
from infra.account_security import AccountSecurity
from infra.accounts import AccountRepository
from infra.db import (
    AuthAccount,
    ForecastDraft,
    ForecastVersion,
    Job,
    User,
    UserReportVersion,
    WorldForecast,
)
from infra.evidence_repository import EvidenceError
from infra.human_verification import guard_login
from infra.personal_data import erase_private, export_private
from infra.profiles import ProfileRepository
from infra.reports import ReportRepository
from infra.review_repository import ReviewRepository
from infra.settings import Settings


def create_personal_router(
    session_dependency: Callable[..., Iterator[Session]],
    user_dependency: Callable[..., User],
    config: Settings,
) -> APIRouter:
    router = APIRouter(prefix="/api/v1", tags=["M4 Account and private reports"])
    db = Depends(session_dependency)

    def private_user(
        user: Annotated[User, Depends(user_dependency)], session: Annotated[Session, db]
    ) -> User:
        if session.get(AuthAccount, user.id) is None:
            raise EvidenceError("LOCAL_ACCOUNT_REQUIRED", "私有资料需要使用独立注册账号", 403)
        return user

    identity = Depends(private_user)

    @router.post("/auth/register", response_model=AccountSessionV1, status_code=201)
    def register(
        data: VerifiedRegistrationV1, request: Request, session: Annotated[Session, db]
    ) -> Any:
        with auth_access(session, config, request, "register", data.email) as access:
            result = AccountSecurity(session, config).register(
                data, access.source, access.device, access.device_hash, commit=False
            )
            access.user_id = result.identity.user_id
            return result

    @router.post("/auth/login", response_model=AccountSessionV1)
    def login(data: ProtectedLoginV1, request: Request, session: Annotated[Session, db]) -> Any:
        with auth_access(session, config, request, "login", data.email) as access:
            guard_login(
                session,
                config,
                data.email,
                data.human_token,
                access.source,
                "login",
                access.device_hash,
            )
            result = AccountRepository(session, config).login(
                data,
                source=access.source,
                device=access.device,
                device_hash=access.device_hash,
                commit=False,
            )
            access.user_id = result.identity.user_id
            return result

    @router.post("/auth/logout")
    def logout(
        user: Annotated[User, identity],
        session: Annotated[Session, db],
        authorization: Annotated[str, Header()],
    ) -> Any:
        AccountRepository(session, config).logout(authorization.split(" ", 1)[1])
        return {"ok": True}

    @router.get("/auth/identity", response_model=AccountIdentityV1)
    def who(user: Annotated[User, identity], session: Annotated[Session, db]) -> Any:
        return AccountRepository(session, config).identity(user)

    @router.get("/taxonomies/industries")
    def taxonomy() -> Any:
        return {
            "version": TAXONOMY_VERSION,
            "entries": rows(),
            "classification": "product_owned_not_official_standard",
        }

    @router.get("/taxonomies/countries", response_model=CountryCatalogV1)
    def countries() -> CountryCatalogV1:
        from prediction_engine.personalization.geography import COUNTRIES

        return CountryCatalogV1(
            entries=tuple(CountryOptionV1(code=code, label=label) for code, label in COUNTRIES)
        )

    @router.get("/me/profile", response_model=ProfileViewV1)
    def profile(user: Annotated[User, identity], session: Annotated[Session, db]) -> Any:
        return ProfileRepository(session, config).view(user.id)

    @router.put("/me/profile", response_model=ProfileViewV1)
    def save(
        data: ProfileInputV1, user: Annotated[User, identity], session: Annotated[Session, db]
    ) -> Any:
        return ProfileRepository(session, config).save(user.id, data)

    @router.post("/me/profile/snapshots", response_model=ProfileSnapshotV1)
    def snapshot(user: Annotated[User, identity], session: Annotated[Session, db]) -> Any:
        result = ProfileRepository(session, config).snapshot(user.id)
        session.commit()
        return result

    @router.get("/me/profile/snapshots/{snapshot_id}", response_model=ProfileSnapshotV1)
    def snapshot_view(
        snapshot_id: UUID, user: Annotated[User, identity], session: Annotated[Session, db]
    ) -> Any:
        return ProfileRepository(session, config).read_snapshot(snapshot_id, user.id)

    @router.get("/me/entitlements", response_model=FreeReportEntitlementV1)
    def entitlement(user: Annotated[User, identity], session: Annotated[Session, db]) -> Any:
        return ReportRepository(session, config).entitlement(user.id)

    @router.get("/me/export")
    def export(user: Annotated[User, identity], session: Annotated[Session, db]) -> Any:
        return export_private(session, user.id, config)

    @router.delete("/me/data", response_model=PersonalDataErasedV1)
    def erase(
        data: PersonalDataEraseV1, user: Annotated[User, identity], session: Annotated[Session, db]
    ) -> Any:
        return erase_private(session, user.id, data, config)

    @router.post("/research/intake", response_model=ResearchIntakeResultV1)
    def intake(
        data: ResearchIntakeV1, user: Annotated[User, identity], session: Annotated[Session, db]
    ) -> Any:
        return ReportRepository(session, config).intake(user.id, data)

    @router.get("/research/requests")
    def requests(user: Annotated[User, identity], session: Annotated[Session, db]) -> Any:
        return [
            {
                "job_id": job.id,
                "task_type": job.task_type,
                "status": job.status,
                "error_code": job.error_code,
                "created_at": job.created_at,
            }
            for job in session.scalars(
                select(Job)
                .where(
                    Job.user_id == user.id,
                    Job.task_type.in_(["m4_report", "m5_report_refresh", "m6_research"]),
                )
                .order_by(Job.created_at.desc())
                .limit(20)
            )
        ]

    @router.post("/research/first-report", status_code=202, response_model=JobAcceptedV1)
    def first(
        data: FirstReportRequestV1,
        user: Annotated[User, identity],
        session: Annotated[Session, db],
        idempotency_key: Annotated[str, Header(min_length=1, max_length=128)],
    ) -> Any:
        try:
            return ReportRepository(session, config).submit(user.id, data, idempotency_key)
        except IntegrityError:
            session.rollback()
            return ReportRepository(session, config).submit(user.id, data, idempotency_key)

    @router.post("/research/jobs/{job_id}/cancel")
    def cancel(
        job_id: UUID, user: Annotated[User, identity], session: Annotated[Session, db]
    ) -> Any:
        job = session.get(Job, job_id)
        if job is not None and job.user_id == user.id and job.task_type == "m6_research":
            from infra.billing import BillingRepository

            BillingRepository(session, config).cancel_job(user.id, job_id)
        else:
            ReportRepository(session, config).cancel(user.id, job_id)
        return {"ok": True}

    @router.get("/reports", response_model=list[ReportSummaryV1])
    def reports(user: Annotated[User, identity], session: Annotated[Session, db]) -> Any:
        return ReportRepository(session, config).summaries(user.id)

    @router.get("/reports/{report_id}", response_model=PrivateReportV1)
    def report(
        report_id: UUID, user: Annotated[User, identity], session: Annotated[Session, db]
    ) -> Any:
        return ReportRepository(session, config).report(user.id, report_id)

    @router.get("/reports/{report_id}/versions")
    def versions(
        report_id: UUID, user: Annotated[User, identity], session: Annotated[Session, db]
    ) -> Any:
        ReportRepository(session, config).report(user.id, report_id)
        return [
            {"report_version_id": r.id, "version_num": r.version_num, "created_at": r.created_at}
            for r in session.scalars(
                select(UserReportVersion)
                .where(
                    UserReportVersion.report_id == report_id, UserReportVersion.user_id == user.id
                )
                .order_by(UserReportVersion.version_num)
            )
        ]

    @router.get("/reports/{report_id}/versions/{version_id}", response_model=PrivateReportV1)
    def report_version(
        report_id: UUID,
        version_id: UUID,
        user: Annotated[User, identity],
        session: Annotated[Session, db],
    ) -> Any:
        return ReportRepository(session, config).report(user.id, report_id, version_id)

    @router.get("/recommendations")
    def recommendations(user: Annotated[User, identity], session: Annotated[Session, db]) -> Any:
        return ReportRepository(session, config).recommendations(user.id)

    @router.post("/recommendations/{recommendation_id}/feedback")
    def feedback(
        recommendation_id: UUID,
        data: RecommendationFeedbackV1,
        user: Annotated[User, identity],
        session: Annotated[Session, db],
    ) -> Any:
        ReportRepository(session, config).feedback(user.id, recommendation_id, data)
        return {"ok": True}

    @router.get("/reports/{report_id}/email-preview", response_model=EmailPreviewV1)
    def preview(
        report_id: UUID, user: Annotated[User, identity], session: Annotated[Session, db]
    ) -> Any:
        return ReportRepository(session, config).email_preview(user, report_id)

    @router.post("/reports/{report_id}/email", response_model=LocalDeliveryV1)
    def email(
        report_id: UUID,
        data: EmailAuthorizationV1,
        user: Annotated[User, identity],
        session: Annotated[Session, db],
    ) -> Any:
        return ReportRepository(session, config).authorize_email(user, report_id, data)

    def forecast_detail(version_id: UUID, user: User, session: Session) -> dict[str, Any]:
        version, domains = ReportRepository(session, config).public_forecast(version_id, user.id)
        draft = session.get(ForecastDraft, version.draft_id)
        assert draft is not None
        snapshot = ReviewRepository(session).snapshot(draft)
        sources = [
            {
                "source_version_id": s.source_version_id,
                "url": s.url,
                "title": s.title,
                "publisher": s.publisher,
                "published_at": s.published_at,
                "available_at": s.available_at,
                "usage_permission": s.usage_permission,
            }
            for s in snapshot.sources
        ]
        claims = [
            {
                "claim_id": c.claim_id,
                "text": c.claim_text,
                "relation": c.relation,
                "quote": c.quote[:500],
                "source_version_id": c.source_version_id,
                "known_at": c.known_at,
                "caveat": c.caveat,
            }
            for c in snapshot.claims
        ]
        from infra.monitoring import pending_notice

        notice = pending_notice(session, version.forecast_id)
        return {
            "monitor_notice": notice.body if notice else None,
            "version": version,
            "domain_tags": domains,
            "sources": sources,
            "claims": claims,
            "cases": snapshot.cases,
            "limitations": ["案例结果的已知时间与研究 cutoff 分开展示；不代表可迁移成功率"],
        }

    @router.get("/forecasts")
    def forecasts(user: Annotated[User, identity], session: Annotated[Session, db]) -> Any:
        repo = ReportRepository(session, config)
        result = []
        for identifier in session.scalars(
            select(WorldForecast.current_version_id)
            .where(WorldForecast.current_version_id.is_not(None))
            .limit(100)
        ):
            if identifier is None:
                continue
            try:
                version, _ = repo.public_forecast(identifier, user.id)
            except EvidenceError:
                continue
            result.append(version)
        return result

    @router.get("/forecasts/versions/{version_id}")
    def forecast(
        version_id: UUID, user: Annotated[User, identity], session: Annotated[Session, db]
    ) -> Any:
        return forecast_detail(version_id, user, session)

    @router.get("/forecasts/{forecast_id}/versions")
    def forecast_versions(
        forecast_id: UUID, user: Annotated[User, identity], session: Annotated[Session, db]
    ) -> Any:
        result = []
        for row in session.scalars(
            select(ForecastVersion)
            .where(ForecastVersion.forecast_id == forecast_id)
            .order_by(ForecastVersion.version_num)
        ):
            result.append(ReportRepository(session, config).public_forecast(row.id, user.id)[0])
        if not result:
            raise EvidenceError("FORECAST_NOT_FOUND", "预测不存在", 404)
        return result

    @router.get("/forecasts/{forecast_id}/versions/{version_id}")
    def exact_forecast(
        forecast_id: UUID,
        version_id: UUID,
        user: Annotated[User, identity],
        session: Annotated[Session, db],
    ) -> Any:
        result = forecast_detail(version_id, user, session)
        if result["version"].forecast_id != forecast_id:
            raise EvidenceError("FORECAST_NOT_FOUND", "预测不存在", 404)
        return result

    return router
