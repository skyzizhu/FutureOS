from collections.abc import Callable, Iterator
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, Header, Request
from prediction_engine.contracts.models import EmailQueueRequestV1, NotificationPreferencesV1
from sqlalchemy import select
from sqlalchemy.orm import Session

from infra.accounts import vault_for
from infra.db import AuthAccount, InAppNotification, MailDelivery, NotificationRead, User
from infra.evidence_repository import EvidenceError
from infra.notifications import (
    accept_bounce,
    preferences,
    queue_eligible_mail,
    save_preferences,
    unsubscribe,
)
from infra.reports import ReportRepository
from infra.settings import Settings
from infra.updates import queue_refresh


def create_notification_router(
    db_dependency: Callable[..., Iterator[Session]],
    user_dependency: Callable[..., User],
    config: Settings,
) -> APIRouter:
    router = APIRouter(prefix="/api/v1", tags=["M5 private notifications"])
    db = Depends(db_dependency)

    def private(
        user: Annotated[User, Depends(user_dependency)], session: Annotated[Session, db]
    ) -> User:
        if session.get(AuthAccount, user.id) is None:
            raise EvidenceError("LOCAL_ACCOUNT_REQUIRED", "请使用注册账号", 403)
        return user

    auth = Depends(private)

    @router.get("/me/notification-preferences")
    def prefs(user: Annotated[User, auth], session: Annotated[Session, db]) -> Any:
        return preferences(session, user.id)

    @router.put("/me/notification-preferences")
    def save(
        data: NotificationPreferencesV1,
        user: Annotated[User, auth],
        session: Annotated[Session, db],
    ) -> Any:
        save_preferences(session, user.id, data)
        session.commit()
        return data

    @router.get("/notifications")
    def notifications(user: Annotated[User, auth], session: Annotated[Session, db]) -> Any:
        return [
            {
                "notification_id": row.id,
                "report_id": row.report_id,
                "report_version_id": row.report_version_id,
                "title": row.title,
                "summary": row.summary,
                "created_at": row.created_at,
                "read": session.get(NotificationRead, (user.id, row.id)) is not None,
            }
            for row in session.scalars(
                select(InAppNotification)
                .where(InAppNotification.user_id == user.id)
                .order_by(InAppNotification.created_at.desc())
                .limit(100)
            )
        ]

    @router.post("/notifications/{notification_id}/read")
    def read(
        notification_id: UUID, user: Annotated[User, auth], session: Annotated[Session, db]
    ) -> Any:
        row = session.get(InAppNotification, notification_id)
        if row is None or row.user_id != user.id:
            raise EvidenceError("NOTIFICATION_NOT_FOUND", "通知不存在", 404)
        if session.get(NotificationRead, (user.id, row.id)) is None:
            session.add(NotificationRead(user_id=user.id, notification_id=row.id))
            session.commit()
        return {"ok": True}

    @router.post("/reports/{report_id}/refresh")
    def refresh(
        report_id: UUID, user: Annotated[User, auth], session: Annotated[Session, db]
    ) -> Any:
        result = queue_refresh(
            session, config, user.id, report_id, "本人画像/原主题版本变化：仅免费复查原主题"
        )
        session.commit()
        return result

    @router.post("/reports/{report_id}/deliver")
    def deliver(
        report_id: UUID,
        data: EmailQueueRequestV1,
        user: Annotated[User, auth],
        session: Annotated[Session, db],
    ) -> Any:
        report = ReportRepository(session, config).report(user.id, report_id)
        result = queue_eligible_mail(
            session, config, user.id, report.report_version_id, data.purpose
        )
        session.commit()
        return result

    @router.get("/me/mail-deliveries")
    def deliveries(user: Annotated[User, auth], session: Annotated[Session, db]) -> Any:
        return [
            {
                "delivery_id": r.id,
                "report_version_id": r.report_version_id,
                "purpose": r.purpose,
                "status": r.status,
                "created_at": r.created_at,
                "external_delivery": False,
            }
            for r in session.scalars(
                select(MailDelivery)
                .where(MailDelivery.user_id == user.id)
                .order_by(MailDelivery.created_at.desc())
                .limit(100)
            )
        ]

    @router.get("/me/mail-deliveries/{delivery_id}")
    def local_mail(
        delivery_id: UUID, user: Annotated[User, auth], session: Annotated[Session, db]
    ) -> Any:
        row = session.get(MailDelivery, delivery_id)
        if row is None or row.user_id != user.id:
            raise EvidenceError("DELIVERY_NOT_FOUND", "投递不存在", 404)
        data = vault_for(session, config).open(
            row.ciphertext, "mail:" + str(user.id) + ":" + str(row.id)
        )
        return {k: v for k, v in data.items() if k != "recipient"}

    @router.post("/mail/unsubscribe")
    def optout(data: dict[str, str], session: Annotated[Session, db]) -> Any:
        token = data.get("token", "")
        if not 20 <= len(token) <= 200:
            raise EvidenceError("UNSUBSCRIBE_TOKEN_INVALID", "链接无效", 404)
        unsubscribe(session, token)
        return {"ok": True}

    @router.post("/mail/bounce")
    async def bounce(
        request: Request,
        session: Annotated[Session, db],
        signature: Annotated[str, Header(alias="X-Webhook-Signature")] = "",
    ) -> Any:
        raw = await request.body()
        if len(raw) > 4096:
            raise EvidenceError("WEBHOOK_BODY_TOO_LARGE", "回调内容过长", 422)
        return accept_bounce(session, config, raw, signature)

    return router
