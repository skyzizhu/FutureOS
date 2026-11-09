from collections.abc import Callable, Iterator
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, Header, Request
from prediction_engine.contracts.models import (
    CheckoutRequestV1,
    PaidResearchAcceptedV1,
    PaidResearchSubmitV1,
    PeriodicResearchRequestV1,
    ResearchQuoteV1,
    ResearchScopeV1,
    SandboxConsentV1,
)
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from infra.billing import BillingRepository, commerce_gate, plans
from infra.db import (
    AuthAccount,
    CommerceCheckout,
    CommerceLedger,
    CostObservation,
    Job,
    PaidSubscription,
    ResearchCreditGrant,
    SharedTopicStudy,
    User,
    UserResearchTopic,
)
from infra.evidence_repository import EvidenceError, columns
from infra.paid_research import PaidResearchRepository
from infra.settings import Settings


def create_commerce_router(
    db_dependency: Callable[..., Iterator[Session]],
    user_dependency: Callable[..., User],
    admin_dependency: Callable[..., User],
    config: Settings,
) -> APIRouter:
    router = APIRouter(prefix="/api/v1", tags=["M6 sandbox commerce"])
    db = Depends(db_dependency)

    def private(
        user: Annotated[User, Depends(user_dependency)], session: Annotated[Session, db]
    ) -> User:
        if session.get(AuthAccount, user.id) is None:
            raise EvidenceError("LOCAL_ACCOUNT_REQUIRED", "请使用本地注册账号", 403)
        return user

    auth = Depends(private)

    @router.get("/billing/status")
    def status() -> Any:
        return {
            "enabled": config.sandbox_commerce_enabled,
            "label": "DEMO",
            "real_payments_enabled": False,
        }

    @router.get("/billing/plans")
    def catalog() -> Any:
        commerce_gate(config)
        return plans(config)

    @router.get("/billing/balance")
    def balance(user: Annotated[User, auth], session: Annotated[Session, db]) -> Any:
        return BillingRepository(session, config).balance(user.id)

    @router.post("/billing/checkout", status_code=201)
    async def checkout(
        data: CheckoutRequestV1,
        user: Annotated[User, auth],
        session: Annotated[Session, db],
        key: Annotated[str, Header(alias="Idempotency-Key", min_length=1, max_length=128)],
    ) -> Any:
        try:
            return await BillingRepository(session, config).create_checkout(user.id, data, key)
        except IntegrityError:
            session.rollback()
            return await BillingRepository(session, config).create_checkout(user.id, data, key)

    @router.get("/billing/checkouts/{checkout_id}")
    def view(
        checkout_id: UUID, user: Annotated[User, auth], session: Annotated[Session, db]
    ) -> Any:
        repo = BillingRepository(session, config)
        return repo.checkout_view(repo.checkout_owned(user.id, checkout_id))

    @router.post("/billing/checkouts/{checkout_id}/confirm")
    async def confirm(
        checkout_id: UUID,
        data: SandboxConsentV1,
        user: Annotated[User, auth],
        session: Annotated[Session, db],
    ) -> Any:
        return await BillingRepository(session, config).confirm_local(user.id, checkout_id)

    @router.post("/billing/checkouts/{checkout_id}/refund")
    async def refund(
        checkout_id: UUID,
        data: SandboxConsentV1,
        user: Annotated[User, auth],
        session: Annotated[Session, db],
    ) -> Any:
        return await BillingRepository(session, config).confirm_local(
            user.id, checkout_id, refund=True
        )

    @router.post("/billing/webhook")
    async def webhook(
        request: Request,
        session: Annotated[Session, db],
        signature: Annotated[str, Header(alias="X-Payment-Signature")] = "",
    ) -> Any:
        body = await request.body()
        if len(body) > 16384:
            raise EvidenceError("WEBHOOK_BODY_TOO_LARGE", "回调内容过长", 422)
        return await BillingRepository(session, config).apply_webhook(body, signature)

    @router.get("/billing/history")
    def history(user: Annotated[User, auth], session: Annotated[Session, db]) -> Any:
        repo = BillingRepository(session, config)
        repo.lock_user(user.id)
        repo.expire(user.id)
        session.commit()
        return {
            "checkouts": [
                repo.checkout_view(row)
                for row in session.scalars(
                    select(CommerceCheckout)
                    .where(CommerceCheckout.user_id == user.id)
                    .order_by(CommerceCheckout.created_at.desc())
                    .limit(100)
                )
            ],
            "subscriptions": [
                columns(row)
                for row in session.scalars(
                    select(PaidSubscription).where(PaidSubscription.user_id == user.id)
                )
            ],
            "grants": [
                columns(row)
                for row in session.scalars(
                    select(ResearchCreditGrant).where(ResearchCreditGrant.user_id == user.id)
                )
            ],
            "ledger": [
                columns(row)
                for row in session.scalars(
                    select(CommerceLedger)
                    .where(CommerceLedger.user_id == user.id)
                    .order_by(CommerceLedger.created_at.desc())
                    .limit(100)
                )
            ],
            "real_charge": False,
        }

    @router.post("/billing/subscriptions/{subscription_id}/cancel")
    def cancel_subscription(
        subscription_id: UUID, user: Annotated[User, auth], session: Annotated[Session, db]
    ) -> Any:
        return BillingRepository(session, config).cancel_subscription(user.id, subscription_id)

    @router.post("/research/quote", response_model=ResearchQuoteV1)
    def quote(
        data: ResearchScopeV1, user: Annotated[User, auth], session: Annotated[Session, db]
    ) -> Any:
        return PaidResearchRepository(session, config).quote(user.id, data)

    @router.post("/research/submit", response_model=PaidResearchAcceptedV1, status_code=202)
    def submit(
        data: PaidResearchSubmitV1,
        user: Annotated[User, auth],
        session: Annotated[Session, db],
        key: Annotated[str, Header(alias="Idempotency-Key", min_length=1, max_length=128)],
    ) -> Any:
        try:
            return PaidResearchRepository(session, config).submit(user.id, data, key)
        except IntegrityError:
            session.rollback()
            return PaidResearchRepository(session, config).submit(user.id, data, key)

    @router.post("/research/paid-jobs/{job_id}/cancel")
    def cancel_job(
        job_id: UUID, user: Annotated[User, auth], session: Annotated[Session, db]
    ) -> Any:
        BillingRepository(session, config).cancel_job(user.id, job_id)
        return {"ok": True}

    @router.get("/research/topics")
    def topics(user: Annotated[User, auth], session: Annotated[Session, db]) -> Any:
        return [
            {
                **columns(topic),
                "scope": study.scope,
            }
            for topic in session.scalars(
                select(UserResearchTopic).where(UserResearchTopic.user_id == user.id)
            )
            if (study := session.get(SharedTopicStudy, topic.scope_fingerprint)) is not None
        ]

    @router.post("/research/topics/{topic_id}/schedule")
    def schedule(
        topic_id: UUID,
        data: PeriodicResearchRequestV1,
        user: Annotated[User, auth],
        session: Annotated[Session, db],
    ) -> Any:
        return PaidResearchRepository(session, config).schedule(user.id, topic_id, data)

    @router.post("/research/topics/{topic_id}/pause")
    def pause(topic_id: UUID, user: Annotated[User, auth], session: Annotated[Session, db]) -> Any:
        repo = BillingRepository(session, config)
        repo.lock_user(user.id)
        topic = session.get(UserResearchTopic, topic_id)
        if topic is None or topic.user_id != user.id:
            raise EvidenceError("RESEARCH_TOPIC_NOT_FOUND", "研究主题不存在", 404)
        topic.periodic_enabled = False
        session.commit()
        return {"ok": True}

    @router.get("/admin/costs")
    def costs(
        user: Annotated[User, Depends(admin_dependency)], session: Annotated[Session, db]
    ) -> Any:
        groups = session.execute(
            select(
                CostObservation.stage,
                func.count(),
                func.sum(CostObservation.duration_ms),
                func.sum(CostObservation.external_model_calls),
            ).group_by(CostObservation.stage)
        ).all()
        reuse = (
            session.scalar(
                select(func.count())
                .select_from(CostObservation)
                .where(CostObservation.stage == "shared_research", CostObservation.reused.is_(True))
            )
            or 0
        )
        total = (
            session.scalar(
                select(func.count())
                .select_from(CostObservation)
                .where(CostObservation.stage == "shared_research")
            )
            or 0
        )
        return {
            "stages": [
                {
                    "stage": stage,
                    "observations": count,
                    "duration_ms": duration,
                    "external_model_calls": calls,
                }
                for stage, count, duration, calls in groups
            ],
            "shared_research_reused": reuse,
            "shared_research_total": total,
            "reuse_ratio": reuse / total if total else None,
            "provider_cost_unknown": session.scalar(
                select(func.count())
                .select_from(CostObservation)
                .where(CostObservation.external_cost_minor.is_(None))
            ),
            "job_statuses": [
                {"status": status, "count": count}
                for status, count in session.execute(
                    select(Job.status, func.count())
                    .where(Job.task_type == "m6_research")
                    .group_by(Job.status)
                )
            ],
            "limitations": [
                "观测从M6开始，不补造历史成本；本地计算成本和真实供应商单价未标定",
                "Mock 外部调用为零不能代表真实运行成本或预测质量",
            ],
        }

    return router
