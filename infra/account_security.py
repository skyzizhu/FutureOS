"""Purpose-bound four-digit email proofs, password changes and private sessions."""

import hashlib
import hmac
import secrets
import smtplib
import ssl
from datetime import timedelta
from email.message import EmailMessage
from typing import Any
from uuid import UUID, uuid4

from prediction_engine.contracts.models import (
    AccountCredentialsV1,
    AccountSessionV1,
    EmailCodeRequestV1,
    EmailCodeSentV1,
    PasswordResetV1,
    VerifiedRegistrationV1,
)
from prediction_engine.evidence.temporal import utc
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from infra.accounts import (
    AccountRepository,
    AuthRateLimited,
    auth_lock,
    normalized_email,
    password_hash,
    password_matches,
    token_hash,
    vault_for,
)
from infra.admin_security import audit, revoke_sessions
from infra.db import AuthAccount, AuthEmailCode, AuthSession, User, utcnow
from infra.evidence_repository import EvidenceError
from infra.human_verification import verify_human
from infra.settings import Settings


def deliver_code(config: Settings, email: str, code: str, purpose: str) -> None:
    message = EmailMessage()
    message["From"] = config.smtp_from
    message["To"] = email
    message["Subject"] = "FutureOS 邮箱验证" if purpose == "register" else "FutureOS 密码修改验证"
    message.set_content(
        f"你的验证码是 {code}，5分钟内有效。请勿向他人提供。若非本人操作，请忽略此邮件。"
    )
    context = ssl.create_default_context()
    assert config.smtp_host and config.smtp_username and config.smtp_password
    if config.smtp_port == 465:
        with smtplib.SMTP_SSL(
            config.smtp_host, config.smtp_port, timeout=10, context=context
        ) as smtp:
            smtp.login(config.smtp_username, config.smtp_password.get_secret_value())
            smtp.send_message(message)
    else:
        with smtplib.SMTP(config.smtp_host, config.smtp_port, timeout=10) as smtp:
            smtp.ehlo()
            smtp.starttls(context=context)
            smtp.ehlo()
            smtp.login(config.smtp_username, config.smtp_password.get_secret_value())
            smtp.send_message(message)


class AccountSecurity:
    def __init__(self, session: Session, config: Settings):
        self.session, self.config = session, config
        self.repo = AccountRepository(session, config)

    def digest(self, identifier: UUID, lookup: str, purpose: str, code: str) -> str:
        payload = f"email-code-v1:{identifier}:{lookup}:{purpose}:{code}".encode()
        return hmac.new(
            vault_for(self.session, self.config).key, payload, hashlib.sha256
        ).hexdigest()

    def request_code(
        self, data: EmailCodeRequestV1, source: str, device_hash: str | None = None
    ) -> EmailCodeSentV1:
        if self.config.auth_mail_transport == "disabled":
            raise EvidenceError("EMAIL_UNAVAILABLE", "验证邮件尚未配置", 503)
        vault = vault_for(self.session, self.config)
        email = normalized_email(data.email)
        lookup = vault.lookup(email)
        # Protect provider calls before accepting a human-verification token.
        self.repo.attempt(token_hash("email-send:" + lookup), source, device_hash)
        verify_human(
            self.session,
            self.config,
            data.human_token,
            "signup" if data.purpose == "register" else "password_reset",
        )
        auth_lock(self.session, 3)
        now = utcnow()
        recent = self.session.scalars(
            select(AuthEmailCode)
            .where(
                AuthEmailCode.email_lookup == lookup,
                AuthEmailCode.purpose == data.purpose,
                AuthEmailCode.created_at > now - timedelta(minutes=15),
            )
            .order_by(AuthEmailCode.created_at.desc())
        ).all()
        if recent and utc(recent[0].created_at) > now - timedelta(seconds=60):
            self.session.rollback()
            raise AuthRateLimited(
                max(1, 60 - int((now - utc(recent[0].created_at)).total_seconds()))
            )
        if len(recent) >= 3:
            self.session.rollback()
            raise AuthRateLimited(900, "验证码发送过于频繁，请稍后再试")
        daily_sends = (
            self.session.scalar(
                select(func.count())
                .select_from(AuthEmailCode)
                .where(
                    AuthEmailCode.email_lookup == lookup,
                    AuthEmailCode.purpose == data.purpose,
                    AuthEmailCode.created_at > now - timedelta(days=1),
                )
            )
            or 0
        )
        if daily_sends >= 10:
            self.session.rollback()
            raise AuthRateLimited(86400, "邮箱验证操作过于频繁，请稍后再试")
        count, oldest = self.session.execute(
            select(func.count(), func.min(AuthEmailCode.created_at)).where(
                AuthEmailCode.created_at > now - timedelta(days=1)
            )
        ).one()
        if count >= self.config.auth_email_global_daily_sends and oldest:
            self.session.rollback()
            retry_after = max(1, int((utc(oldest) + timedelta(days=1) - now).total_seconds()) + 1)
            raise AuthRateLimited(retry_after, "邮件验证服务达到日发送上限，请稍后再试")
        # Invalidate all earlier codes for this mailbox and purpose, including unused ones.
        for prior in recent:
            prior.consumed_at = now
            prior.code_ciphertext = None
        # Expired content need not remain as a password recovery artifact.
        self.session.execute(
            delete(AuthEmailCode)
            .where(AuthEmailCode.expires_at < now - timedelta(hours=25))
            .execution_options(synchronize_session=False)
        )
        identifier = uuid4()
        code = f"{secrets.randbelow(10000):04d}"
        account = self.session.scalar(select(AuthAccount).where(AuthAccount.email_lookup == lookup))
        deliver = data.purpose == "register" or bool(account and account.enabled)
        row = AuthEmailCode(
            id=identifier,
            email_lookup=lookup,
            email_ciphertext=vault.seal({"email": email}, "auth-email:" + str(identifier)),
            purpose=data.purpose,
            code_digest=self.digest(identifier, lookup, data.purpose, code),
            code_ciphertext=vault.seal({"code": code}, "auth-code:" + str(identifier))
            if deliver and self.config.auth_mail_transport == "local_preview"
            else None,
            delivery_status="local_preview"
            if deliver and self.config.auth_mail_transport == "local_preview"
            else "pending"
            if deliver
            else "suppressed",
            expires_at=now + timedelta(minutes=5),
            created_at=now,
        )
        self.session.add(row)
        self.session.commit()
        if deliver and self.config.auth_mail_transport == "smtp":
            try:
                deliver_code(self.config, email, code, data.purpose)
                row.delivery_status = "sent"
            except (OSError, smtplib.SMTPException):
                row.delivery_status = "failed"
                # No auto retry of an uncertain SMTP send; a resend creates a new proof.
                audit(self.session, "auth_email_failed")
            self.session.commit()
        return EmailCodeSentV1(
            challenge_id=identifier, delivery_mode=self.config.auth_mail_transport
        )

    def proof(self, identifier: UUID, email: str, purpose: str, code: str) -> AuthEmailCode:
        row = self.session.get(AuthEmailCode, identifier)
        lookup = vault_for(self.session, self.config).lookup(normalized_email(email))
        if (
            not row
            or row.email_lookup != lookup
            or row.purpose != purpose
            or row.consumed_at
            or utc(row.expires_at) <= utcnow()
            or row.attempts >= 5
        ):
            raise EvidenceError("EMAIL_CODE_INVALID", "验证码无效或已过期", 401)
        daily_failures = (
            self.session.scalar(
                select(func.sum(AuthEmailCode.failed_attempts)).where(
                    AuthEmailCode.email_lookup == lookup,
                    AuthEmailCode.purpose == purpose,
                    AuthEmailCode.created_at > utcnow() - timedelta(days=1),
                )
            )
            or 0
        )
        if daily_failures >= 5:
            raise AuthRateLimited(86400, "邮箱验证操作过于频繁，请稍后再试")
        row.attempts += 1
        if row.delivery_status not in {"sent", "local_preview"} or not hmac.compare_digest(
            row.code_digest, self.digest(identifier, lookup, purpose, code)
        ):
            row.failed_attempts += 1
            audit(self.session, "email_code_failed")
            self.session.commit()
            raise EvidenceError("EMAIL_CODE_INVALID", "验证码无效或已过期", 401)
        return row

    def register(
        self,
        data: VerifiedRegistrationV1,
        source: str,
        device: str = "未知设备",
        device_hash: str | None = None,
        commit: bool = True,
    ) -> AccountSessionV1:
        lookup = vault_for(self.session, self.config).lookup(normalized_email(data.email))
        self.repo.attempt(lookup, source, device_hash)
        auth_lock(self.session, 3)
        row = self.proof(data.verification_id, data.email, "register", data.code)
        row.consumed_at = utcnow()
        row.code_ciphertext = None
        return self.repo.register(
            AccountCredentialsV1(email=data.email, password=data.password),
            verified=True,
            attempt_recorded=True,
            device=device,
            commit=commit,
        )

    def reset_password(
        self, data: PasswordResetV1, source: str, device_hash: str | None = None
    ) -> None:
        lookup = vault_for(self.session, self.config).lookup(normalized_email(data.email))
        self.repo.attempt(token_hash("password-reset:" + lookup), source, device_hash)
        # Hash before holding user/challenge locks, subject to admission and KDF bound.
        encoded = password_hash(data.password)
        account = self.session.scalar(select(AuthAccount).where(AuthAccount.email_lookup == lookup))
        if account:
            self.session.scalar(select(User).where(User.id == account.user_id).with_for_update())
            self.session.refresh(account)
        auth_lock(self.session, 3)
        self.proof(data.verification_id, data.email, "password_reset", data.code)
        if not account or not account.enabled:
            raise EvidenceError("EMAIL_CODE_INVALID", "验证码无效或已过期", 401)
        account.password_hash = encoded
        account.email_verified_at = utcnow()
        # Consume every reset proof, not only the supplied code; revoke user and admin sessions.
        for old in self.session.scalars(
            select(AuthEmailCode).where(
                AuthEmailCode.email_lookup == lookup, AuthEmailCode.purpose == "password_reset"
            )
        ):
            old.consumed_at = utcnow()
            old.code_ciphertext = None
        revoke_sessions(self.session, account.user_id)
        audit(self.session, "password_changed", target=account.user_id)
        self.session.commit()

    def sessions(self, user: User, current_token: str) -> list[dict[str, Any]]:
        return [
            {
                "session_id": str(r.public_id),
                "kind": r.kind,
                "device_label": r.device_label,
                "created_at": utc(r.created_at).isoformat(),
                "expires_at": utc(r.expires_at).isoformat(),
                "current": hmac.compare_digest(r.token_hash, token_hash(current_token)),
            }
            for r in self.session.scalars(
                select(AuthSession)
                .where(
                    AuthSession.user_id == user.id,
                    AuthSession.revoked_at.is_(None),
                    AuthSession.expires_at > utcnow(),
                )
                .order_by(AuthSession.created_at.desc())
            )
        ]

    def revoke(self, user: User, identifier: UUID) -> None:
        self.session.scalar(select(User).where(User.id == user.id).with_for_update())
        row = self.session.scalar(
            select(AuthSession).where(
                AuthSession.public_id == identifier, AuthSession.user_id == user.id
            )
        )
        if not row:
            raise EvidenceError("SESSION_NOT_FOUND", "会话不存在", 404)
        row.revoked_at = utcnow()
        audit(self.session, "session_revoked", user.id, user.id)
        self.session.commit()

    def revoke_all(self, user: User, password: str) -> None:
        account = self.session.get(AuthAccount, user.id)
        if not account:
            raise EvidenceError("AUTH_REQUIRED", "账号不可用", 401)
        self.repo.attempt(account.email_lookup)
        original_hash = account.password_hash
        matched = password_matches(password, original_hash)
        self.session.scalar(select(User).where(User.id == user.id).with_for_update())
        self.session.refresh(account)
        if not matched or not account.enabled or account.password_hash != original_hash:
            raise EvidenceError("REAUTH_REQUIRED", "密码不匹配", 401)
        revoke_sessions(self.session, user.id)
        audit(self.session, "all_sessions_revoked", user.id, user.id)
        self.session.commit()
