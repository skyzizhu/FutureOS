from collections.abc import Callable, Iterator
from datetime import timedelta
from typing import Annotated, Any, cast
from uuid import UUID

from fastapi import APIRouter, Depends, Header, Request
from prediction_engine.contracts.models import (
    AdminAccessChangeV1,
    AdminBootstrapV1,
    AdminChallengeV1,
    AdminCreateV1,
    AdminSecondFactorV1,
    AdminSessionV1,
    AdminStepUpV1,
    AuthAccessEventViewV1,
    AuthConfigurationV1,
    CurrentPasswordV1,
    EmailCodeRequestV1,
    EmailCodeSentV1,
    LoginSessionViewV1,
    PasswordResetV1,
    ProtectedLoginV1,
)
from prediction_engine.evidence.temporal import utc
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from apps.api.auth_access import auth_source, browser_hash
from infra.account_security import AccountSecurity
from infra.accounts import AccountRepository, device_label, vault_for
from infra.admin_security import AdminSecurity
from infra.db import AdminAccess, AdminMFA, AuthAccessEvent, AuthAccount, AuthAudit, User, utcnow
from infra.human_verification import guard_login
from infra.settings import Settings


def create_account_security_router(
    session_dependency: Callable[..., Iterator[Session]],
    user_dependency: Callable[..., User],
    admin_dependency: Callable[..., User],
    config: Settings,
) -> APIRouter:
    router = APIRouter(prefix="/api/v1", tags=["Account security"])
    db = Depends(session_dependency)
    identity = Depends(user_dependency)
    admin = Depends(admin_dependency)

    @router.get("/auth/config", response_model=AuthConfigurationV1)
    def auth_config() -> Any:
        return {
            "email_code_length": 4,
            "email_transport": config.auth_mail_transport,
            "turnstile_enabled": config.turnstile_enabled,
            "turnstile_site_key": config.turnstile_site_key if config.turnstile_enabled else "",
            "demo_admin_enabled": config.demo_admin_enabled,
        }

    @router.post("/auth/email-code", response_model=EmailCodeSentV1)
    def email_code(
        data: EmailCodeRequestV1, request: Request, session: Annotated[Session, db]
    ) -> Any:
        return AccountSecurity(session, config).request_code(
            data, auth_source(request), browser_hash(session, config, request)
        )

    @router.post("/auth/password-reset")
    def reset_password(
        data: PasswordResetV1, request: Request, session: Annotated[Session, db]
    ) -> Any:
        AccountSecurity(session, config).reset_password(
            data, auth_source(request), browser_hash(session, config, request)
        )
        return {"ok": True, "message": "密码已修改，请重新登录"}

    @router.get("/me/sessions", response_model=list[LoginSessionViewV1])
    def sessions(
        user: Annotated[User, identity],
        session: Annotated[Session, db],
        authorization: Annotated[str, Header()],
    ) -> Any:
        return AccountSecurity(session, config).sessions(user, authorization.split(" ", 1)[1])

    @router.delete("/me/sessions/{identifier}")
    def revoke(
        identifier: UUID, user: Annotated[User, identity], session: Annotated[Session, db]
    ) -> Any:
        AccountSecurity(session, config).revoke(user, identifier)
        return {"ok": True}

    @router.post("/me/sessions/revoke-all")
    def revoke_all(
        data: CurrentPasswordV1, user: Annotated[User, identity], session: Annotated[Session, db]
    ) -> Any:
        AccountSecurity(session, config).revoke_all(user, data.password)
        return {"ok": True}

    @router.post("/admin-auth/bootstrap", response_model=AdminChallengeV1)
    def bootstrap(data: AdminBootstrapV1, request: Request, session: Annotated[Session, db]) -> Any:
        return AdminSecurity(session, config).bootstrap(
            data, request.client.host if request.client else "unknown-peer"
        )

    @router.post("/admin-auth/login", response_model=AdminChallengeV1)
    def admin_login(
        data: ProtectedLoginV1, request: Request, session: Annotated[Session, db]
    ) -> Any:
        guard_login(
            session,
            config,
            data.email,
            data.human_token,
            request.client.host if request.client else "unknown-peer",
            "admin_login",
        )
        return AdminSecurity(session, config).login(
            data, request.client.host if request.client else "unknown-peer"
        )

    @router.post("/admin-auth/enroll", response_model=AdminSessionV1 | AdminChallengeV1)
    def enroll(data: AdminSecondFactorV1, request: Request, session: Annotated[Session, db]) -> Any:
        return AdminSecurity(session, config).verify(
            data, enroll=True, device=device_label(request.headers.get("user-agent", ""))
        )

    @router.post("/admin-auth/verify", response_model=AdminSessionV1 | AdminChallengeV1)
    def verify(data: AdminSecondFactorV1, request: Request, session: Annotated[Session, db]) -> Any:
        return AdminSecurity(session, config).verify(
            data, device=device_label(request.headers.get("user-agent", ""))
        )

    @router.post("/admin-auth/step-up")
    def step_up(
        data: AdminStepUpV1,
        user: Annotated[User, admin],
        session: Annotated[Session, db],
        authorization: Annotated[str, Header()],
    ) -> Any:
        return AdminSecurity(session, config).step_up(
            user, authorization.split(" ", 1)[1], data.code
        )

    @router.post("/admin-auth/recovery-codes")
    def rotate(
        data: AdminStepUpV1,
        user: Annotated[User, admin],
        session: Annotated[Session, db],
        authorization: Annotated[str, Header()],
    ) -> Any:
        return AdminSecurity(session, config).step_up(
            user, authorization.split(" ", 1)[1], data.code, rotate=True
        )

    @router.post("/admin-auth/logout")
    def admin_logout(
        user: Annotated[User, identity],
        session: Annotated[Session, db],
        authorization: Annotated[str, Header()],
    ) -> Any:
        AccountRepository(session, config).logout(authorization.split(" ", 1)[1])
        return {"ok": True}

    @router.get("/admin/security/admins")
    def admins(user: Annotated[User, admin], session: Annotated[Session, db]) -> Any:
        return [
            {
                "user_id": str(access.user_id),
                "permission_group": access.permission_group,
                "enabled": account.enabled,
                "email_masked": AccountRepository(session, config)
                .identity(cast(User, session.get(User, access.user_id)))
                .email_masked,
                "mfa_enabled": bool(
                    (factor := session.get(AdminMFA, access.user_id)) and factor.enabled_at
                ),
            }
            for access, account in session.execute(
                select(AdminAccess, AuthAccount).join(
                    AuthAccount, AuthAccount.user_id == AdminAccess.user_id
                )
            )
        ]

    @router.post("/admin/security/admins", status_code=201)
    def create_admin(
        data: AdminCreateV1,
        user: Annotated[User, admin],
        session: Annotated[Session, db],
        authorization: Annotated[str, Header()],
    ) -> Any:
        return {
            "user_id": str(
                AdminSecurity(session, config).create_admin(
                    user, data, authorization.split(" ", 1)[1]
                )
            )
        }

    @router.put("/admin/security/admins/{target}")
    def change_admin(
        target: UUID,
        data: AdminAccessChangeV1,
        user: Annotated[User, admin],
        session: Annotated[Session, db],
        authorization: Annotated[str, Header()],
    ) -> Any:
        AdminSecurity(session, config).change_access(
            user, target, data, authorization.split(" ", 1)[1]
        )
        return {"ok": True}

    @router.post("/admin/security/admins/{target}/reset-mfa")
    def reset_mfa(
        target: UUID,
        user: Annotated[User, admin],
        session: Annotated[Session, db],
        authorization: Annotated[str, Header()],
    ) -> Any:
        AdminSecurity(session, config).reset_mfa(user, target, authorization.split(" ", 1)[1])
        return {"ok": True}

    @router.get("/admin/security/audit")
    def audits(user: Annotated[User, admin], session: Annotated[Session, db]) -> Any:
        failures = (
            session.scalar(
                select(func.count())
                .select_from(AuthAudit)
                .where(
                    AuthAudit.created_at > utcnow() - timedelta(minutes=15),
                    AuthAudit.event.in_(
                        [
                            "admin_login_failed",
                            "admin_mfa_failed",
                            "admin_step_up_failed",
                            "user_login_failed",
                            "email_code_failed",
                        ]
                    ),
                )
            )
            or 0
        )
        vault = vault_for(session, config)
        recent = session.scalars(
            select(AuthAccessEvent)
            .where(
                AuthAccessEvent.created_at
                >= utcnow() - timedelta(days=config.auth_access_retention_days)
            )
            .order_by(AuthAccessEvent.created_at.desc(), AuthAccessEvent.id)
            .limit(100)
        )
        access_events = [
            AuthAccessEventViewV1.model_validate(
                {
                    **vault.open(row.context_ciphertext, "auth-access:" + str(row.id)),
                    "id": row.id,
                    "user_id": row.user_id,
                    "request_id": row.request_id,
                    "action": row.action,
                    "outcome": row.outcome,
                    "reason": row.reason,
                    "fingerprint": row.device_hash,
                    "created_at": utc(row.created_at),
                }
            ).model_dump(mode="json")
            for row in recent
        ]
        return {
            "access_events": access_events,
            "requires_attention": failures >= 5,
            "failed_events_15m": failures,
            "external_alerts_enabled": False,
            "events": [
                {
                    "id": str(row.id),
                    "event": row.event,
                    "actor_id": str(row.actor_id) if row.actor_id else None,
                    "target_id": str(row.target_id) if row.target_id else None,
                    "detail": row.detail,
                    "created_at": row.created_at.isoformat(),
                }
                for row in session.scalars(
                    select(AuthAudit).order_by(AuthAudit.created_at.desc()).limit(100)
                )
            ],
        }

    return router
