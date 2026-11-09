"""Server-authoritative local sandbox commerce. No live payment transport or credentials."""

import hashlib
import hmac
import json
from datetime import timedelta
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4, uuid5

from prediction_engine.contracts.models import BillingPlanV1, CheckoutRequestV1, PaymentEventV1
from prediction_engine.evidence.temporal import utc
from prediction_engine.forecasting.workflow import hashed
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from infra.accounts import vault_for
from infra.db import (
    CommerceCheckout,
    CommerceLedger,
    CommercePaymentEvent,
    Job,
    PaidResearchReservation,
    PaidSubscription,
    ResearchCreditGrant,
    User,
    UserResearchTopic,
    utcnow,
)
from infra.evidence_repository import EvidenceError
from infra.providers.mock import MockPaymentProvider
from infra.settings import Settings


def commerce_gate(config: Settings) -> None:
    if not config.sandbox_commerce_enabled:
        raise EvidenceError("COMMERCE_DISABLED", "套餐与新主题沙盒尚未开启", 503)
    if not config.demo_mode or config.live_payments_enabled:
        raise EvidenceError("SANDBOX_ONLY", "当前仅支持本地模拟，不接受真实付款", 503)


def plans(config: Settings) -> tuple[BillingPlanV1, ...]:
    rows = tuple(
        BillingPlanV1.model_validate(p)
        for p in json.loads(Path(config.billing_plans_path).read_text())
    )
    if not rows or len({p.code for p in rows}) != len(rows):
        raise ValueError("BILLING_PLAN_CONFIG_INVALID")
    return rows


class BillingRepository:
    def __init__(self, session: Session, config: Settings) -> None:
        self.session, self.config = session, config

    def lock_user(self, user_id: UUID) -> None:
        self.session.scalar(select(User).where(User.id == user_id).with_for_update(key_share=True))

    def provider(self) -> MockPaymentProvider:
        return MockPaymentProvider(self.signing_key())

    def signing_key(self) -> bytes:
        return hmac.new(
            vault_for(self.session, self.config).key, b"m6-mock-webhook-v1", hashlib.sha256
        ).digest()

    def ledger(
        self,
        user_id: UUID,
        kind: str,
        source: str,
        delta: int = 0,
        grant_id: UUID | None = None,
        job_id: UUID | None = None,
    ) -> None:
        self.session.add(
            CommerceLedger(
                user_id=user_id,
                grant_id=grant_id,
                job_id=job_id,
                entry_kind=kind,
                source_key=source,
                units_delta=delta,
            )
        )

    def checkout_owned(self, user_id: UUID, checkout_id: UUID) -> CommerceCheckout:
        row = self.session.get(CommerceCheckout, checkout_id)
        if row is None or row.user_id != user_id:
            raise EvidenceError("CHECKOUT_NOT_FOUND", "付款会话不存在", 404)
        return row

    def checkout_view(self, row: CommerceCheckout) -> dict[str, Any]:
        return {
            "checkout_id": row.id,
            "plan": row.plan,
            "status": row.status,
            "expires_at": utc(row.expires_at),
            "created_at": utc(row.created_at),
            "checkout_url": "/billing?checkout=" + str(row.id),
            "label": "DEMO",
            "real_charge": False,
        }

    async def create_checkout(
        self, user_id: UUID, data: CheckoutRequestV1, key: str
    ) -> dict[str, Any]:
        commerce_gate(self.config)
        self.lock_user(user_id)
        self.expire(user_id)
        digest = hashed(data.model_dump(mode="json"))
        old = self.session.scalar(
            select(CommerceCheckout).where(
                CommerceCheckout.user_id == user_id, CommerceCheckout.idempotency_key == key
            )
        )
        if old:
            if old.input_hash != digest:
                raise EvidenceError("IDEMPOTENCY_CONFLICT", "相同请求键不能更换套餐", 409)
            self.session.commit()
            return self.checkout_view(old)
        plan = next((p for p in plans(self.config) if p.code == data.plan_code), None)
        if plan is None:
            raise EvidenceError("PLAN_NOT_FOUND", "套餐不存在", 404)
        if plan.recurring and self.session.scalar(
            select(PaidSubscription.id).where(
                PaidSubscription.user_id == user_id,
                PaidSubscription.status == "active",
                PaidSubscription.ends_at > utcnow(),
            )
        ):
            raise EvidenceError(
                "SUBSCRIPTION_ALREADY_ACTIVE", "已有有效订阅；本沙盒不叠加订阅周期", 409
            )
        reference = await self.provider().create_checkout(
            str(user_id), plan.code, str(user_id) + ":" + key
        )
        row = CommerceCheckout(
            id=uuid4(),
            user_id=user_id,
            idempotency_key=key,
            input_hash=digest,
            plan=plan.model_dump(mode="json"),
            provider_reference=reference,
            expires_at=utcnow() + timedelta(minutes=30),
            status="pending",
        )
        self.session.add(row)
        self.session.commit()
        return self.checkout_view(row)

    async def confirm_local(
        self, user_id: UUID, checkout_id: UUID, refund: bool = False
    ) -> dict[str, Any]:
        commerce_gate(self.config)
        row = self.checkout_owned(user_id, checkout_id)
        event = PaymentEventV1(
            event_id=("refund:" if refund else "paid:") + str(row.id),
            checkout_id=row.id,
            provider_reference=row.provider_reference,
            event_type="checkout.refunded" if refund else "checkout.paid",
            amount_minor=row.plan["amount_minor"],
            currency=row.plan["currency"],
            occurred_at=utcnow(),
        )
        # Repeated local confirmation reuses the already verified event.
        prior = self.session.scalar(
            select(CommercePaymentEvent).where(
                CommercePaymentEvent.provider == "mock",
                CommercePaymentEvent.external_event_id == event.event_id,
            )
        )
        if prior:
            return {
                "ok": True,
                "duplicate": True,
                "checkout_id": row.id,
                "status": row.status,
                "real_charge": False,
            }
        raw = event.model_dump_json().encode()
        signature = hmac.new(self.signing_key(), raw, hashlib.sha256).hexdigest()
        return await self.apply_webhook(raw, signature)

    async def apply_webhook(self, raw: bytes, signature: str) -> dict[str, Any]:
        commerce_gate(self.config)
        try:
            await self.provider().verify_webhook(raw, signature)
        except (ValueError, TypeError):
            raise EvidenceError("PAYMENT_SIGNATURE_INVALID", "沙盒回调签名无效", 403) from None
        try:
            event = PaymentEventV1.model_validate_json(raw)
        except ValidationError:
            raise EvidenceError("PAYMENT_EVENT_INVALID", "回调格式无效", 422) from None
        row = self.session.get(CommerceCheckout, event.checkout_id)
        if row is None:
            raise EvidenceError("CHECKOUT_NOT_FOUND", "付款会话不存在", 404)
        self.lock_user(row.user_id)
        self.session.refresh(row, with_for_update=True)
        digest = hashlib.sha256(raw).hexdigest()
        prior = self.session.scalar(
            select(CommercePaymentEvent).where(
                CommercePaymentEvent.provider == event.provider,
                CommercePaymentEvent.external_event_id == event.event_id,
            )
        )
        if prior:
            if prior.payload_hash != digest:
                raise EvidenceError("PAYMENT_EVENT_CONFLICT", "事件ID重复但内容不同", 409)
            return {
                "ok": True,
                "duplicate": True,
                "checkout_id": row.id,
                "status": row.status,
                "real_charge": False,
            }
        if (
            event.provider_reference != row.provider_reference
            or event.amount_minor != row.plan["amount_minor"]
            or event.currency != row.plan["currency"]
        ):
            raise EvidenceError(
                "PAYMENT_ORDER_MISMATCH", "回调必须匹配服务端冻结的订单、金额和币种", 409
            )
        if event.occurred_at > utcnow() + timedelta(minutes=1):
            raise EvidenceError("PAYMENT_EVENT_TIME_INVALID", "回调时间无效", 422)
        self.session.add(
            CommercePaymentEvent(
                provider=event.provider,
                external_event_id=event.event_id,
                checkout_id=row.id,
                event_type=event.event_type,
                payload_hash=digest,
                occurred_at=event.occurred_at,
            )
        )
        self.session.flush()
        if event.event_type == "checkout.paid":
            if row.status == "pending":
                if utc(row.expires_at) < utcnow() or event.occurred_at < utc(row.created_at):
                    raise EvidenceError("CHECKOUT_EXPIRED", "付款会话已过期，请重新创建", 409)
                self.activate(row)
            elif row.status != "paid":
                raise EvidenceError("PAYMENT_STATE_INVALID", "当前订单不能再次开通", 409)
        else:
            self.refund(row)
        self.session.commit()
        return {
            "ok": True,
            "duplicate": False,
            "checkout_id": row.id,
            "status": row.status,
            "real_charge": False,
        }

    def activate(self, row: CommerceCheckout) -> None:
        plan = BillingPlanV1.model_validate(row.plan)
        now = utcnow()
        ends = now + timedelta(days=plan.valid_days)
        subscription_id = None
        row.status = "paid"
        self.session.flush()
        if plan.recurring:
            if self.session.scalar(
                select(PaidSubscription.id).where(
                    PaidSubscription.user_id == row.user_id,
                    PaidSubscription.status == "active",
                    PaidSubscription.ends_at > now,
                )
            ):
                raise EvidenceError(
                    "SUBSCRIPTION_ALREADY_ACTIVE", "已有有效订阅，本次不重复开通", 409
                )
            subscription_id = uuid5(row.id, "subscription")
            self.session.add(
                PaidSubscription(
                    id=subscription_id,
                    user_id=row.user_id,
                    checkout_id=row.id,
                    status="active",
                    starts_at=now,
                    ends_at=ends,
                    cadence_days=plan.cadence_days,
                )
            )
            self.session.flush()
        row.status = "paid"
        grant = ResearchCreditGrant(
            id=uuid5(row.id, "credit-grant"),
            user_id=row.user_id,
            checkout_id=row.id,
            subscription_id=subscription_id,
            units=plan.units,
            available=plan.units,
            reserved=0,
            consumed=0,
            revoked=0,
            expires_at=ends,
        )
        self.session.add(grant)
        self.session.flush()
        self.ledger(row.user_id, "granted", str(row.id), plan.units, grant.id)

    def release(self, job_id: UUID) -> None:
        reservation = self.session.scalar(
            select(PaidResearchReservation)
            .where(PaidResearchReservation.job_id == job_id)
            .with_for_update()
        )
        if reservation is None or reservation.state != "reserved":
            return
        grant = self.session.get(ResearchCreditGrant, reservation.grant_id)
        assert grant is not None
        grant.reserved -= 1
        grant.available += 1
        reservation.state = "released"
        self.session.flush()
        self.ledger(reservation.user_id, "released", str(job_id), 1, grant.id, job_id)
        self.session.flush()

    def cancel_job(self, user_id: UUID, job_id: UUID, commit: bool = True) -> None:
        self.lock_user(user_id)
        job = self.session.scalar(
            select(Job)
            .where(Job.id == job_id, Job.user_id == user_id, Job.task_type == "m6_research")
            .with_for_update()
        )
        if job is None:
            raise EvidenceError("JOB_NOT_FOUND", "研究任务不存在", 404)
        if job.status in {"queued", "running", "failed_retryable"}:
            job.status = "cancelled"
            job.error_code = "USER_CANCELLED"
            job.lease_token = job.lease_until = None
            self.release(job.id)
        if commit:
            self.session.commit()

    def expire(self, user_id: UUID) -> None:
        now = utcnow()
        for checkout in self.session.scalars(
            select(CommerceCheckout).where(
                CommerceCheckout.user_id == user_id,
                CommerceCheckout.status == "pending",
                CommerceCheckout.expires_at <= now,
            )
        ):
            checkout.status = "expired"
        for reservation in self.session.scalars(
            select(PaidResearchReservation).where(
                PaidResearchReservation.user_id == user_id,
                PaidResearchReservation.state == "reserved",
                PaidResearchReservation.expires_at <= now,
            )
        ):
            self.cancel_job(user_id, reservation.job_id, commit=False)
        for grant in self.session.scalars(
            select(ResearchCreditGrant).where(
                ResearchCreditGrant.user_id == user_id, ResearchCreditGrant.expires_at <= now
            )
        ):
            if grant.available:
                units = grant.available
                grant.revoked += units
                grant.available = 0
                self.ledger(user_id, "revoked", "expired:" + str(grant.id), -units, grant.id)
        for subscription in self.session.scalars(
            select(PaidSubscription).where(
                PaidSubscription.user_id == user_id,
                PaidSubscription.status == "active",
                PaidSubscription.ends_at <= now,
            )
        ):
            subscription.status = "expired"
            for topic in self.session.scalars(
                select(UserResearchTopic).where(
                    UserResearchTopic.subscription_id == subscription.id
                )
            ):
                topic.periodic_enabled = False
        self.session.flush()

    def balance(self, user_id: UUID) -> dict[str, Any]:
        self.lock_user(user_id)
        self.expire(user_id)
        grants = self.session.scalars(
            select(ResearchCreditGrant).where(ResearchCreditGrant.user_id == user_id)
        ).all()
        result = {
            key: sum(getattr(g, key) for g in grants)
            for key in ("available", "reserved", "consumed", "revoked")
        }
        result.update(
            {"label": "DEMO", "real_charge": False, "enabled": self.config.sandbox_commerce_enabled}
        )
        self.session.commit()
        return result

    def reserve(
        self, user_id: UUID, job_id: UUID, subscription_id: UUID | None = None
    ) -> PaidResearchReservation:
        query = select(ResearchCreditGrant).where(
            ResearchCreditGrant.user_id == user_id,
            ResearchCreditGrant.available > 0,
            ResearchCreditGrant.expires_at > utcnow(),
        )
        if subscription_id:
            query = query.where(ResearchCreditGrant.subscription_id == subscription_id)
        grant = self.session.scalar(
            query.order_by(ResearchCreditGrant.expires_at, ResearchCreditGrant.id)
            .with_for_update()
            .limit(1)
        )
        if grant is None:
            raise EvidenceError(
                "RESEARCH_CREDITS_REQUIRED", "没有可用研究额度；原主题免费更新仍可用", 409
            )
        grant.available -= 1
        grant.reserved += 1
        reservation = PaidResearchReservation(
            id=uuid4(),
            user_id=user_id,
            job_id=job_id,
            grant_id=grant.id,
            state="reserved",
            expires_at=min(utc(grant.expires_at), utcnow() + timedelta(hours=1)),
        )
        self.session.add(reservation)
        self.session.flush()
        self.ledger(user_id, "reserved", str(job_id), -1, grant.id, job_id)
        return reservation

    def consume(self, reservation: PaidResearchReservation) -> None:
        if reservation.state != "reserved" or utc(reservation.expires_at) <= utcnow():
            raise ValueError("PAID_RESERVATION_EXPIRED")
        grant = self.session.get(ResearchCreditGrant, reservation.grant_id)
        assert grant is not None
        grant.reserved -= 1
        grant.consumed += 1
        reservation.state = "consumed"
        self.session.flush()
        self.ledger(
            reservation.user_id,
            "consumed",
            str(reservation.job_id),
            0,
            grant.id,
            reservation.job_id,
        )
        self.session.flush()

    def subscription_owned(self, user_id: UUID, identifier: UUID) -> PaidSubscription:
        row = self.session.get(PaidSubscription, identifier)
        if row is None or row.user_id != user_id:
            raise EvidenceError("SUBSCRIPTION_NOT_FOUND", "订阅不存在", 404)
        return row

    def cancel_subscription(self, user_id: UUID, identifier: UUID) -> dict[str, Any]:
        self.lock_user(user_id)
        self.expire(user_id)
        row = self.subscription_owned(user_id, identifier)
        if not row.cancel_at_period_end:
            row.cancel_at_period_end = True
            self.ledger(user_id, "subscription_cancelled", str(row.id))
        self.session.commit()
        return {
            "ok": True,
            "ends_at": row.ends_at,
            "cancel_at_period_end": True,
            "message": "到期不续订，当前周期权益和已授权研究保留至到期；本沙盒不会自动扣款",
        }

    def refund(self, row: CommerceCheckout) -> None:
        if row.status == "refunded":
            return
        if row.status != "paid":
            raise EvidenceError("REFUND_STATE_INVALID", "仅已确认的沙盒订单可撤销", 409)
        grant = self.session.scalar(
            select(ResearchCreditGrant).where(ResearchCreditGrant.checkout_id == row.id)
        )
        assert grant is not None
        if grant.consumed:
            raise EvidenceError(
                "REFUND_REQUIRES_UNUSED_ORDER",
                "本沙盒只演示未使用订单全额退款，已使用请人工处理",
                409,
            )
        for reservation in self.session.scalars(
            select(PaidResearchReservation).where(
                PaidResearchReservation.grant_id == grant.id,
                PaidResearchReservation.state == "reserved",
            )
        ):
            self.cancel_job(row.user_id, reservation.job_id, commit=False)
        amount = grant.available
        grant.revoked += amount
        grant.available = 0
        self.ledger(row.user_id, "refund", str(row.id), -amount, grant.id)
        row.status = "refunded"
        if grant.subscription_id:
            subscription = self.session.get(PaidSubscription, grant.subscription_id)
            assert subscription is not None
            subscription.status = "refunded"
            for topic in self.session.scalars(
                select(UserResearchTopic).where(
                    UserResearchTopic.subscription_id == subscription.id
                )
            ):
                topic.periodic_enabled = False
