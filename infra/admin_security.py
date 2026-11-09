"""Controlled administrator enrollment, TOTP/recovery and server-enforced permissions."""

import hashlib
import hmac
import secrets
from datetime import timedelta
from typing import Any
from uuid import UUID, uuid4

import pyotp
from prediction_engine.contracts.models import (
    AccountCredentialsV1,
    AdminAccessChangeV1,
    AdminBootstrapV1,
    AdminChallengeV1,
    AdminCreateV1,
    AdminSecondFactorV1,
    AdminSessionV1,
)
from prediction_engine.evidence.temporal import utc
from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from infra.accounts import (
    AccountRepository,
    auth_lock,
    normalized_email,
    password_hash,
    password_matches,
    token_hash,
    vault_for,
)
from infra.db import (
    AdminAccess,
    AdminMFA,
    AuthAccount,
    AuthAttempt,
    AuthAudit,
    AuthChallenge,
    AuthSession,
    User,
    utcnow,
)
from infra.evidence_repository import EvidenceError
from infra.settings import Settings

PERMISSIONS: dict[str, set[str]] = {
    "owner": {"*"},
    "reviewer": {"read", "review.write"},
    "operator": {
        "read",
        "sources.write",
        "evidence.write",
        "indicators.write",
        "signals.write",
        "historical-cases.write",
        "research.write",
        "monitor.write",
    },
    "viewer": {"read"},
}


def audit(
    session: Session,
    event: str,
    actor: UUID | None = None,
    target: UUID | None = None,
    **detail: Any,
) -> None:
    session.add(AuthAudit(event=event, actor_id=actor, target_id=target, detail=detail))


def revoke_sessions(session: Session, user_id: UUID) -> None:
    session.execute(
        update(AuthSession)
        .where(AuthSession.user_id == user_id, AuthSession.revoked_at.is_(None))
        .values(revoked_at=utcnow())
    )
    session.execute(
        update(AuthChallenge)
        .where(AuthChallenge.user_id == user_id, AuthChallenge.consumed_at.is_(None))
        .values(consumed_at=utcnow())
    )


def permission(
    session: Session, config: Settings, user: User, token: str, area: str, write: bool
) -> None:
    if (
        config.demo_admin_enabled
        and area != "security"
        and hmac.compare_digest(token, config.demo_admin_token)
    ):
        return
    account, access, factor = (
        session.get(AuthAccount, user.id),
        session.get(AdminAccess, user.id),
        session.get(AdminMFA, user.id),
    )
    login = session.get(AuthSession, token_hash(token))
    if not (
        account
        and account.enabled
        and access
        and factor
        and factor.enabled_at
        and login
        and login.kind == "admin"
        and login.mfa_verified_at
        and login.revoked_at is None
        and utc(login.expires_at) > utcnow()
    ):
        raise EvidenceError("ADMIN_MFA_REQUIRED", "需要完成管理员双重认证", 403)
    allowed = PERMISSIONS.get(access.permission_group, set())
    required = area + ".write" if write and area != "self" else "read"
    if area == "security":
        required = "security.write"
    if "*" not in allowed and required not in allowed:
        raise EvidenceError("FORBIDDEN", "当前管理员没有该操作权限", 403)


def require_fresh(session: Session, token: str) -> AuthSession:
    row = session.get(AuthSession, token_hash(token))
    if (
        not row
        or not row.mfa_verified_at
        or utc(row.mfa_verified_at) < utcnow() - timedelta(minutes=5)
    ):
        raise EvidenceError("MFA_STEP_UP_REQUIRED", "请使用新的动态码重新验证身份", 403)
    return row


class AdminSecurity:
    def __init__(self, session: Session, config: Settings):
        self.session, self.config = session, config
        self.repo = AccountRepository(session, config)

    def bootstrap_token(self) -> str:
        auth_lock(self.session, 2)
        if self.session.scalar(select(AdminAccess.user_id).limit(1)):
            raise EvidenceError("BOOTSTRAP_CLOSED", "已有管理员，不能再次初始化", 409)
        self.session.execute(
            update(AuthChallenge)
            .where(AuthChallenge.purpose == "bootstrap")
            .values(consumed_at=utcnow())
        )
        token = secrets.token_urlsafe(32)
        self.session.add(
            AuthChallenge(
                token_hash=token_hash(token),
                purpose="bootstrap",
                expires_at=utcnow() + timedelta(minutes=15),
            )
        )
        self.session.commit()
        return token

    def create(self, data: AccountCredentialsV1, group: str, actor: UUID | None = None) -> User:
        vault = vault_for(self.session, self.config)
        email = normalized_email(data.email)
        if self.session.scalar(
            select(AuthAccount.user_id).where(AuthAccount.email_lookup == vault.lookup(email))
        ):
            raise EvidenceError("ACCOUNT_NOT_AVAILABLE", "该登录标识不可用", 409)
        user = User(id=uuid4(), auth_subject="admin:" + str(uuid4()), role="admin")
        self.session.add(user)
        self.session.flush()
        self.session.add(
            AuthAccount(
                user_id=user.id,
                email_lookup=vault.lookup(email),
                email_ciphertext=vault.seal({"email": email}, "account:" + str(user.id)),
                password_hash=password_hash(data.password),
            )
        )
        self.session.add(AdminAccess(user_id=user.id, permission_group=group))
        audit(self.session, "admin_created", actor, user.id, permission_group=group)
        self.session.flush()
        return user

    def bootstrap(self, data: AdminBootstrapV1, source: str) -> AdminChallengeV1:
        self.repo.attempt(token_hash("bootstrap:" + source), source)
        auth_lock(self.session, 2)
        row = self.session.get(AuthChallenge, token_hash(data.bootstrap_token))
        if (
            self.session.scalar(select(AdminAccess.user_id).limit(1))
            or not row
            or row.purpose != "bootstrap"
            or row.consumed_at
            or utc(row.expires_at) <= utcnow()
        ):
            raise EvidenceError("BOOTSTRAP_INVALID", "初始化凭证无效或已过期", 401)
        user = self.create(data, "owner")
        row.consumed_at = utcnow()
        result = self.challenge(user)
        self.session.commit()
        return result

    def login(self, data: AccountCredentialsV1, source: str) -> AdminChallengeV1:
        vault = vault_for(self.session, self.config)
        lookup = vault.lookup(normalized_email(data.email))
        attempt_id = self.repo.attempt(lookup, source)
        account = self.session.scalar(select(AuthAccount).where(AuthAccount.email_lookup == lookup))
        original_hash = account.password_hash if account else None
        matched = password_matches(data.password, original_hash)
        user = self.session.get(User, account.user_id) if account else None
        if (
            not matched
            or not account
            or not account.enabled
            or not user
            or user.role != "admin"
            or not self.session.get(AdminAccess, user.id)
        ):
            self.session.execute(
                update(AuthAttempt).where(AuthAttempt.id == attempt_id).values(outcome="failed")
            )
            audit(self.session, "admin_login_failed")
            self.session.commit()
            raise EvidenceError("AUTH_REQUIRED", "邮箱或密码不匹配", 401)
        self.session.scalar(select(User).where(User.id == user.id).with_for_update())
        self.session.refresh(account)
        if not account.enabled or account.password_hash != original_hash:
            raise EvidenceError("AUTH_REQUIRED", "邮箱或密码不匹配", 401)
        self.session.execute(
            update(AuthAttempt).where(AuthAttempt.id == attempt_id).values(outcome="succeeded")
        )
        result = self.challenge(user)
        self.session.commit()
        return result

    def challenge(self, user: User) -> AdminChallengeV1:
        token = secrets.token_urlsafe(32)
        self.session.add(
            AuthChallenge(
                token_hash=token_hash(token),
                user_id=user.id,
                purpose="admin_mfa",
                expires_at=utcnow() + timedelta(minutes=5),
            )
        )
        factor = self.session.get(AdminMFA, user.id)
        if factor is None or factor.enabled_at is None:
            secret = pyotp.random_base32()
            vault = vault_for(self.session, self.config)
            if factor is None:
                factor = AdminMFA(user_id=user.id, secret_ciphertext="")
                self.session.add(factor)
            factor.secret_ciphertext = vault.seal({"secret": secret}, "admin-mfa:" + str(user.id))
            factor.last_counter = -1
            factor.recovery_hashes = []
            # A new enrollment secret invalidates previously issued enrollment challenges.
            self.session.flush()
            return AdminChallengeV1(
                challenge_token=token,
                stage="enroll",
                secret=secret,
                provisioning_uri=pyotp.TOTP(secret).provisioning_uri(
                    name=str(user.id), issuer_name="FutureOS Admin"
                ),
            )
        return AdminChallengeV1(challenge_token=token, stage="verify")

    def _totp(self, factor: AdminMFA, code: str) -> bool:
        if not code.isascii() or not code.isdigit() or len(code) != 6:
            return False
        secret = vault_for(self.session, self.config).open(
            factor.secret_ciphertext, "admin-mfa:" + str(factor.user_id)
        )["secret"]
        otp = pyotp.TOTP(secret)
        now_counter = int(utcnow().timestamp()) // 30
        for counter in range(now_counter - 1, now_counter + 2):
            if counter > factor.last_counter and hmac.compare_digest(otp.at(counter * 30), code):
                factor.last_counter = counter
                return True
        return False

    def _recovery_hash(self, user_id: UUID, code: str) -> str:
        return hmac.new(
            vault_for(self.session, self.config).key,
            b"admin-recovery-v1:" + str(user_id).encode() + b":" + code.encode(),
            hashlib.sha256,
        ).hexdigest()

    def recovery_codes(self, factor: AdminMFA) -> tuple[str, ...]:
        codes = tuple(secrets.token_hex(10) for _ in range(10))
        factor.recovery_hashes = [self._recovery_hash(factor.user_id, code) for code in codes]
        return codes

    def verify(
        self, data: AdminSecondFactorV1, enroll: bool = False, device: str = "未知设备"
    ) -> AdminSessionV1 | AdminChallengeV1:
        # Slot2 serializes challenge consumption even under SQLite, not only PostgreSQL row locks.
        auth_lock(self.session, 2)
        row = self.session.get(AuthChallenge, token_hash(data.challenge_token))
        if (
            not row
            or row.purpose != "admin_mfa"
            or not row.user_id
            or row.consumed_at
            or utc(row.expires_at) <= utcnow()
            or row.attempts >= 5
        ):
            raise EvidenceError("MFA_CHALLENGE_INVALID", "验证已失效，请重新登录", 401)
        user = self.session.scalar(select(User).where(User.id == row.user_id).with_for_update())
        account, factor = (
            self.session.get(AuthAccount, row.user_id),
            self.session.get(AdminMFA, row.user_id),
        )
        if not user or not account or not account.enabled or not factor:
            raise EvidenceError("AUTH_REQUIRED", "账号不可用", 401)
        self.session.refresh(row)
        self.session.refresh(account)
        self.session.refresh(factor)
        if (
            row.consumed_at
            or row.attempts >= 5
            or utc(row.expires_at) <= utcnow()
            or not account.enabled
        ):
            raise EvidenceError("MFA_CHALLENGE_INVALID", "验证已失效，请重新登录", 401)
        row.attempts += 1
        valid = self._totp(factor, data.code)
        if not valid and not enroll and factor.enabled_at:
            digest = self._recovery_hash(user.id, data.code)
            if any(hmac.compare_digest(digest, h) for h in factor.recovery_hashes):
                row.consumed_at = utcnow()
                factor.enabled_at = None
                factor.recovery_hashes = []
                revoke_sessions(self.session, user.id)
                result = self.challenge(user)
                audit(self.session, "admin_recovery_used", user.id, user.id)
                self.session.commit()
                return result
        if (
            not valid
            or (enroll and factor.enabled_at is not None)
            or (not enroll and factor.enabled_at is None)
        ):
            audit(self.session, "admin_mfa_failed", target=user.id)
            self.session.commit()
            raise EvidenceError("MFA_INVALID", "动态码或恢复码无效", 401)
        codes: tuple[str, ...] = ()
        if enroll:
            factor.enabled_at = utcnow()
            codes = self.recovery_codes(factor)
        row.consumed_at = utcnow()
        audit(self.session, "admin_login_succeeded", user.id, user.id, enrolled=enroll)
        state = self.repo.new_session(user, admin=True, device=device)
        return AdminSessionV1(**state.model_dump(), recovery_codes=codes)

    def step_up(self, user: User, token: str, code: str, rotate: bool = False) -> dict[str, Any]:
        self.repo.attempt(token_hash("step-up:" + str(user.id)))
        auth_lock(self.session, 2)
        factor = self.session.get(AdminMFA, user.id)
        row = self.session.get(AuthSession, token_hash(token))
        if (
            not factor
            or not factor.enabled_at
            or not row
            or row.revoked_at
            or not self._totp(factor, code)
        ):
            audit(self.session, "admin_step_up_failed", user.id, user.id)
            self.session.commit()
            raise EvidenceError("MFA_INVALID", "动态码无效或已使用，请等待下一个动态码", 401)
        row.mfa_verified_at = utcnow()
        codes = self.recovery_codes(factor) if rotate else ()
        audit(
            self.session, "admin_recovery_rotated" if rotate else "admin_step_up", user.id, user.id
        )
        self.session.commit()
        return {"ok": True, "recovery_codes": codes}

    def change_access(
        self, actor: User, target: UUID, data: AdminAccessChangeV1, token: str
    ) -> None:
        auth_lock(self.session, 2)
        self.session.expire_all()
        permission(self.session, self.config, actor, token, "security", True)
        require_fresh(self.session, token)
        access = self.session.get(AdminAccess, target)
        account = self.session.get(AuthAccount, target)
        if not access or not account:
            raise EvidenceError("ADMIN_NOT_FOUND", "管理员不存在", 404)
        self.session.scalar(select(User).where(User.id == target).with_for_update())
        self.session.refresh(account)
        self.session.refresh(access)
        owners = (
            self.session.scalar(
                select(func.count())
                .select_from(AdminAccess)
                .join(AuthAccount, AuthAccount.user_id == AdminAccess.user_id)
                .where(AdminAccess.permission_group == "owner", AuthAccount.enabled.is_(True))
            )
            or 0
        )
        if (
            access.permission_group == "owner"
            and account.enabled
            and (not data.enabled or data.permission_group != "owner")
            and owners <= 1
        ):
            raise EvidenceError("LAST_OWNER_REQUIRED", "必须保留至少一名启用的所有者", 409)
        access.permission_group = data.permission_group
        account.enabled = data.enabled
        revoke_sessions(self.session, target)
        audit(
            self.session,
            "admin_access_changed",
            actor.id,
            target,
            permission_group=data.permission_group,
            enabled=data.enabled,
        )
        self.session.commit()

    def create_admin(self, actor: User, data: AdminCreateV1, token: str) -> UUID:
        auth_lock(self.session, 2)
        self.session.expire_all()
        permission(self.session, self.config, actor, token, "security", True)
        require_fresh(self.session, token)
        user = self.create(data, data.permission_group, actor.id)
        self.session.commit()
        return user.id

    def reset_mfa(self, actor: User, target: UUID, token: str) -> None:
        require_fresh(self.session, token)
        if target == actor.id:
            raise EvidenceError("USE_RECOVERY_FLOW", "本人请使用恢复码重新绑定", 409)
        auth_lock(self.session, 2)
        self.session.expire_all()
        permission(self.session, self.config, actor, token, "security", True)
        require_fresh(self.session, token)
        factor = self.session.get(AdminMFA, target)
        if not factor:
            raise EvidenceError("ADMIN_NOT_FOUND", "尚无可重置的双重认证", 404)
        factor.enabled_at = None
        factor.recovery_hashes = []
        factor.last_counter = -1
        revoke_sessions(self.session, target)
        audit(self.session, "admin_mfa_reset", actor.id, target)
        self.session.commit()
