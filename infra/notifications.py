"""Consent/frequency gates, persistent local delivery, unsubscribe and bounce suppression."""

import hashlib
import hmac
import secrets
from datetime import timedelta
from typing import Any
from uuid import UUID, uuid4

from prediction_engine.contracts.models import BounceEventV1, NotificationPreferencesV1
from prediction_engine.evidence.temporal import utc
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from infra.accounts import AccountRepository, token_hash, vault_for
from infra.db import (
    AuthAccount,
    Job,
    MailAttempt,
    MailBounce,
    MailDelivery,
    NotificationPreference,
    OutboxEvent,
    PreferenceAudit,
    UnsubscribeGrant,
    User,
    UserReportVersion,
    utcnow,
)
from infra.evidence_repository import EvidenceError
from infra.settings import Settings


def preferences(session: Session, user_id: UUID) -> NotificationPreferencesV1:
    row = session.get(NotificationPreference, user_id)
    return (
        NotificationPreferencesV1.model_validate(row.body) if row else NotificationPreferencesV1()
    )


def save_preferences(
    session: Session, user_id: UUID, data: NotificationPreferencesV1, reason: str = "user_consent"
) -> None:
    row = session.get(NotificationPreference, user_id)
    if row is None:
        row = NotificationPreference(user_id=user_id, body={}, suppressed=False)
        session.add(row)
    row.body = data.model_dump(mode="json")
    row.updated_at = utcnow()
    session.add(PreferenceAudit(user_id=user_id, body=row.body, reason=reason))
    session.flush()


def queue_eligible_mail(
    session: Session, config: Settings, user_id: UUID, report_version_id: UUID, purpose: str
) -> dict[str, Any]:
    session.scalar(select(User).where(User.id == user_id).with_for_update(key_share=True))
    version = session.get(UserReportVersion, report_version_id)
    if version is None or version.user_id != user_id:
        raise EvidenceError("REPORT_NOT_FOUND", "私有版本不存在", 404)
    pref = preferences(session, user_id)
    row = session.get(NotificationPreference, user_id)
    if not getattr(pref, purpose + "_opt_in", False) or (row and row.suppressed):
        return {"eligible": False, "reason": "CONSENT_OR_SUPPRESSION"}
    prior = session.scalar(
        select(MailDelivery).where(
            MailDelivery.user_id == user_id,
            MailDelivery.report_version_id == report_version_id,
            MailDelivery.purpose == purpose,
        )
    )
    if prior:
        return {"eligible": True, "delivery_id": prior.id, "deduplicated": True}
    if purpose == "first_report" and session.scalar(
        select(MailDelivery.id).where(
            MailDelivery.user_id == user_id, MailDelivery.purpose == "first_report"
        )
    ):
        return {"eligible": False, "reason": "FIRST_EMAIL_ALREADY_QUEUED"}
    now = utcnow()
    count = (
        session.scalar(
            select(func.count())
            .select_from(MailDelivery)
            .where(
                MailDelivery.user_id == user_id,
                MailDelivery.created_at > now - timedelta(days=7),
                MailDelivery.status.not_in(["suppressed", "failed_terminal"]),
            )
        )
        or 0
    )
    if count >= 5:
        return {"eligible": False, "reason": "WEEKLY_LIMIT"}
    if purpose != "first_report":
        last = session.scalar(
            select(MailDelivery)
            .where(MailDelivery.user_id == user_id, MailDelivery.purpose == purpose)
            .order_by(MailDelivery.created_at.desc())
            .limit(1)
        )
        seconds = 86400 if pref.frequency == "daily" else 604800
        if last and utc(last.created_at) + timedelta(seconds=seconds) > now:
            return {"eligible": False, "reason": "COOLDOWN"}
    if session.get(AuthAccount, user_id) is None:
        return {"eligible": False, "reason": "LOCAL_ACCOUNT_REQUIRED"}
    recipient = AccountRepository(session, config).recipient(user_id)
    raw = secrets.token_urlsafe(32)
    session.add(
        UnsubscribeGrant(
            token_hash=token_hash(raw), user_id=user_id, expires_at=now + timedelta(days=90)
        )
    )
    identifier = uuid4()
    job = Job(
        user_id=user_id,
        task_type="m5_mail",
        idempotency_key="m5-mail:" + str(identifier),
        input_hash=str(identifier),
        payload={"label": version.label},
    )
    session.add(job)
    session.flush()
    session.add(
        OutboxEvent(
            job_id=job.id,
            event_type="EmailDeliveryRequested.v1",
            payload={"delivery_id": str(identifier), "label": version.label},
        )
    )
    content = {
        "recipient": recipient,
        "subject": "FutureOS：你的私有报告有更新",
        "summary": "请登录后查看报告；邮件摘要不含个人画像。",
        "link": "/reports/" + str(version.report_id) + "?version=" + str(version.id),
        "unsubscribe_link": "/unsubscribe?token=" + raw,
    }
    session.add(
        MailDelivery(
            id=identifier,
            user_id=user_id,
            report_version_id=version.id,
            job_id=job.id,
            purpose=purpose,
            status="queued",
            ciphertext=vault_for(session, config).seal(
                content, "mail:" + str(user_id) + ":" + str(identifier)
            ),
        )
    )
    return {"eligible": True, "delivery_id": identifier, "deduplicated": False}


def dispatch_local(session: Session, job_id: UUID, config: Settings) -> dict[str, Any]:
    delivery = session.scalar(
        select(MailDelivery).where(MailDelivery.job_id == job_id).with_for_update()
    )
    if delivery is None:
        raise ValueError("MAIL_DELIVERY_MISSING")
    if delivery.status in {"delivered_local", "suppressed"}:
        return {
            "delivery_id": str(delivery.id),
            "status": delivery.status,
            "external_delivery": False,
        }
    if delivery.status == "started":
        raise ValueError("MAIL_UNCERTAIN_NO_AUTO_RETRY")
    pref = preferences(session, delivery.user_id)
    row = session.get(NotificationPreference, delivery.user_id)
    if not getattr(pref, delivery.purpose + "_opt_in", False) or (row and row.suppressed):
        delivery.status = "suppressed"
    else:
        # No network in DEMO; persistence is the local transport's idempotent acceptance.
        content = vault_for(session, config).open(
            delivery.ciphertext, "mail:" + str(delivery.user_id) + ":" + str(delivery.id)
        )
        if not content["link"].startswith("/reports/"):
            raise ValueError("MAIL_PRIVATE_LINK_INVALID")
        if config.live_email_enabled:
            raise ValueError("EXTERNAL_EMAIL_REQUIRES_NON_DEMO_DEPLOYMENT")
        delivery.status = "delivered_local"
    session.add(MailAttempt(delivery_id=delivery.id, status=delivery.status))
    return {"delivery_id": str(delivery.id), "status": delivery.status, "external_delivery": False}


def unsubscribe(session: Session, token: str) -> None:
    grant = session.get(UnsubscribeGrant, token_hash(token))
    if grant is None or utc(grant.expires_at) < utcnow():
        raise EvidenceError("UNSUBSCRIBE_TOKEN_INVALID", "退订链接无效或已过期", 404)
    if grant.used_at is None:
        save_preferences(session, grant.user_id, NotificationPreferencesV1(), "unsubscribe")
        grant.used_at = utcnow()
    session.commit()


def accept_bounce(
    session: Session, config: Settings, raw: bytes, signature: str
) -> dict[str, bool]:
    if not config.bounce_webhook_secret:
        raise EvidenceError("BOUNCE_WEBHOOK_DISABLED", "退信回调未配置", 503)
    expected = hmac.new(
        config.bounce_webhook_secret.get_secret_value().encode(), raw, hashlib.sha256
    ).hexdigest()
    if not hmac.compare_digest(expected, signature):
        raise EvidenceError("WEBHOOK_SIGNATURE_INVALID", "回调签名无效", 403)
    event = BounceEventV1.model_validate_json(raw)
    if session.get(MailBounce, event.event_id):
        return {"ok": True, "duplicate": True}
    delivery = session.get(MailDelivery, event.delivery_id)
    if delivery is None:
        raise EvidenceError("DELIVERY_NOT_FOUND", "投递不存在", 404)
    row = session.get(NotificationPreference, delivery.user_id)
    if row is None:
        save_preferences(session, delivery.user_id, NotificationPreferencesV1(), "bounce")
        row = session.get(NotificationPreference, delivery.user_id)
    assert row is not None
    row.suppressed = True
    session.add(MailBounce(event_id=event.event_id, delivery_id=delivery.id, kind=event.kind))
    session.commit()
    return {"ok": True, "duplicate": False}
