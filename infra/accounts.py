"""Local password accounts, one-way opaque sessions, no email verification claims."""

import hashlib
import hmac
import math
import secrets
import threading
from datetime import timedelta
from uuid import UUID, uuid4

from prediction_engine.contracts.models import (
    AccountCredentialsV1,
    AccountIdentityV1,
    AccountSessionV1,
)
from prediction_engine.evidence.temporal import utc
from sqlalchemy import delete, func, select, true, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from infra.db import (
    AdminMFA,
    AuthAccessEvent,
    AuthAccount,
    AuthAttempt,
    AuthAudit,
    AuthEmailCode,
    AuthSession,
    AuthThrottleLock,
    PrivacyErasure,
    Profile,
    ProfileSnapshot,
    User,
    UserEntitlement,
    UserReportVersion,
    utcnow,
)
from infra.evidence_repository import EvidenceError
from infra.privacy import PrivacyVault
from infra.settings import Settings


def normalized_email(value: str) -> str:
    return value.strip().casefold()


_HASH_SLOTS = threading.BoundedSemaphore(2)


class AuthRateLimited(EvidenceError):
    def __init__(self, retry_after: int, message: str = "登录尝试过多，请稍后再试") -> None:
        super().__init__("AUTH_RATE_LIMITED", message, 429)
        self.retry_after = retry_after


def password_hash(password: str, salt: bytes | None = None) -> str:
    salt = salt or secrets.token_bytes(16)
    if not _HASH_SLOTS.acquire(blocking=False):
        raise EvidenceError("AUTH_BUSY", "登录服务繁忙，请稍后再试", 503)
    try:
        digest = hashlib.scrypt(
            password.encode(), salt=salt, n=2**17, r=8, p=1, maxmem=256 * 1024 * 1024, dklen=32
        )
    finally:
        _HASH_SLOTS.release()
    return "scrypt-v1$" + salt.hex() + "$" + digest.hex()


def password_matches(password: str, encoded: str | None) -> bool:
    parts = encoded.split("$") if encoded else ["scrypt-v1", "00" * 16, "00" * 32]
    if len(parts) != 3 or parts[0] != "scrypt-v1":
        return False
    candidate = password_hash(password, bytes.fromhex(parts[1]))
    return encoded is not None and hmac.compare_digest(candidate, encoded)


def device_label(user_agent: str) -> str:
    value = user_agent[:500].lower()
    browser = next(
        (
            name
            for marker, name in [
                ("edg/", "Edge"),
                ("firefox/", "Firefox"),
                ("chrome/", "Chrome"),
                ("safari/", "Safari"),
            ]
            if marker in value
        ),
        "其他客户端",
    )
    system = next(
        (
            name
            for marker, name in [
                ("android", "Android"),
                ("iphone", "iOS"),
                ("ipad", "iPadOS"),
                ("windows", "Windows"),
                ("macintosh", "macOS"),
                ("linux", "Linux"),
            ]
            if marker in value
        ),
        "未知系统",
    )
    return browser + " / " + system


def token_hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def session_user(session: Session, token: str) -> User | None:
    row = session.get(AuthSession, token_hash(token))
    if row is None or row.revoked_at is not None or utc(row.expires_at) <= utcnow():
        return None
    account = session.get(AuthAccount, row.user_id)
    user = session.get(User, row.user_id)
    if account is None or not account.enabled or user is None:
        return None
    if user.role == "admin" and (row.kind != "admin" or row.mfa_verified_at is None):
        return None
    return user


def auth_lock(session: Session, slot: int = 1) -> None:
    insert = pg_insert if session.get_bind().dialect.name == "postgresql" else sqlite_insert
    session.execute(insert(AuthThrottleLock).values(id=slot).on_conflict_do_nothing())
    session.execute(update(AuthThrottleLock).where(AuthThrottleLock.id == slot).values(id=slot))


def vault_for(session: Session, config: Settings) -> PrivacyVault:
    exists = (
        session.scalar(select(AuthAccount.user_id).limit(1))
        or session.scalar(select(Profile.user_id).limit(1))
        or session.scalar(select(ProfileSnapshot.id).limit(1))
        or session.scalar(select(UserReportVersion.id).limit(1))
        or session.scalar(select(PrivacyErasure.id).limit(1))
        or session.scalar(select(AuthEmailCode.id).limit(1))
        or session.scalar(select(AuthAccessEvent.id).limit(1))
        or session.scalar(select(AdminMFA.user_id).limit(1))
    )
    try:
        return PrivacyVault(config.profile_key_path, create=not bool(exists))
    except (OSError, ValueError):
        raise EvidenceError(
            "PRIVATE_KEY_UNAVAILABLE", "私有数据密钥不可用，请恢复配套备份", 503
        ) from None


class AccountRepository:
    def __init__(self, session: Session, config: Settings) -> None:
        self.session = session
        self.config = config

    def identity(self, user: User) -> AccountIdentityV1:
        account = self.session.get(AuthAccount, user.id)
        if account is None:
            raise EvidenceError("LOCAL_ACCOUNT_REQUIRED", "请使用本地注册账号", 403)
        vault = vault_for(self.session, self.config)
        email = vault.open(account.email_ciphertext, "account:" + str(user.id))["email"]
        local, domain = email.split("@", 1)
        return AccountIdentityV1(
            user_id=user.id,
            role="admin" if user.role == "admin" else "user",
            email_masked=local[:1] + "***@" + domain,
            email_verified=account.email_verified_at is not None,
        )

    def attempt(
        self, identity: str, source: str | None = None, device_hash: str | None = None
    ) -> UUID:
        # A short DB transaction serializes admission across processes. No KDF is
        # performed while holding this lock; Redis availability is irrelevant.
        auth_lock(self.session)
        now = utcnow()
        window = timedelta(seconds=self.config.auth_window_seconds)
        self.session.execute(delete(AuthAttempt).where(AuthAttempt.created_at <= now - window))
        source_hash = (
            hmac.new(
                vault_for(self.session, self.config).key,
                b"auth-source-v1:" + source.encode(),
                hashlib.sha256,
            ).hexdigest()
            if source
            else None
        )
        limits = [
            (true(), self.config.auth_global_attempts),
            (AuthAttempt.identity_hash == identity, self.config.auth_identity_attempts),
        ]
        if source_hash:
            limits.append(
                (AuthAttempt.source_hash == source_hash, self.config.auth_source_attempts)
            )
        if device_hash:
            limits.append(
                (AuthAttempt.device_hash == device_hash, self.config.auth_device_attempts)
            )
        retry_after = 0
        for predicate, maximum in limits:
            count, oldest = self.session.execute(
                select(func.count(), func.min(AuthAttempt.created_at)).where(predicate)
            ).one()
            if count >= maximum and oldest:
                retry_after = max(
                    retry_after, math.ceil((utc(oldest) + window - now).total_seconds())
                )
        if retry_after:
            self.session.rollback()
            raise AuthRateLimited(retry_after)
        attempt = AuthAttempt(
            id=uuid4(),
            identity_hash=identity,
            source_hash=source_hash,
            device_hash=device_hash,
            created_at=now,
        )
        self.session.add(attempt)
        self.session.commit()
        return attempt.id

    def register(
        self,
        data: AccountCredentialsV1,
        *,
        source: str | None = None,
        verified: bool = False,
        attempt_recorded: bool = False,
        device: str = "未知设备",
        commit: bool = True,
    ) -> AccountSessionV1:
        vault = vault_for(self.session, self.config)
        email = normalized_email(data.email)
        lookup = vault.lookup(email)
        if not attempt_recorded:
            self.attempt(lookup, source)
        if self.session.scalar(select(AuthAccount).where(AuthAccount.email_lookup == lookup)):
            raise EvidenceError("ACCOUNT_NOT_AVAILABLE", "该登录标识不可用", 409)
        identifier = uuid4()
        user = User(id=identifier, auth_subject="local:" + str(identifier), role="user")
        self.session.add(user)
        self.session.flush()
        self.session.add(
            AuthAccount(
                user_id=identifier,
                email_lookup=lookup,
                email_ciphertext=vault.seal({"email": email}, "account:" + str(identifier)),
                password_hash=password_hash(data.password),
                email_verified_at=utcnow() if verified else None,
            )
        )
        self.session.add(UserEntitlement(user_id=identifier))
        try:
            self.session.flush()
        except IntegrityError:
            self.session.rollback()
            raise EvidenceError("ACCOUNT_NOT_AVAILABLE", "该登录标识不可用", 409) from None
        return self.new_session(user, device=device, commit=commit)

    def login(
        self,
        data: AccountCredentialsV1,
        *,
        source: str | None = None,
        device: str = "未知设备",
        device_hash: str | None = None,
        commit: bool = True,
    ) -> AccountSessionV1:
        vault = vault_for(self.session, self.config)
        lookup = vault.lookup(normalized_email(data.email))
        attempt_id = self.attempt(lookup, source, device_hash)
        account = self.session.scalar(select(AuthAccount).where(AuthAccount.email_lookup == lookup))
        original_hash = account.password_hash if account else None
        if not password_matches(data.password, original_hash):
            self.session.execute(
                update(AuthAttempt).where(AuthAttempt.id == attempt_id).values(outcome="failed")
            )
            self.session.add(
                AuthAudit(event="user_login_failed", target_id=account.user_id if account else None)
            )
            self.session.commit()
            raise EvidenceError("AUTH_REQUIRED", "邮箱或密码不匹配", 401)
        assert account is not None
        user = self.session.get(User, account.user_id)
        assert user is not None
        self.session.scalar(select(User).where(User.id == user.id).with_for_update())
        self.session.refresh(account)
        if not account.enabled or user.role == "admin" or account.password_hash != original_hash:
            self.session.execute(
                update(AuthAttempt).where(AuthAttempt.id == attempt_id).values(outcome="failed")
            )
            self.session.add(
                AuthAudit(event="user_login_failed", target_id=account.user_id if account else None)
            )
            self.session.commit()
            raise EvidenceError("AUTH_REQUIRED", "邮箱或密码不匹配", 401)
        self.session.execute(
            update(AuthAttempt).where(AuthAttempt.id == attempt_id).values(outcome="succeeded")
        )
        self.session.add(
            AuthAudit(event="user_login_succeeded", actor_id=user.id, target_id=user.id)
        )
        return self.new_session(user, device=device, commit=commit)

    def new_session(
        self, user: User, *, admin: bool = False, device: str = "未知设备", commit: bool = True
    ) -> AccountSessionV1:
        token = secrets.token_urlsafe(32)
        expiry = utcnow() + (
            timedelta(minutes=self.config.admin_session_minutes)
            if admin
            else timedelta(hours=self.config.session_hours)
        )
        self.session.add(
            AuthSession(
                token_hash=token_hash(token),
                user_id=user.id,
                expires_at=expiry,
                kind="admin" if admin else "user",
                device_label=device,
                mfa_verified_at=utcnow() if admin else None,
            )
        )
        if commit:
            self.session.commit()
        return AccountSessionV1(access_token=token, expires_at=expiry, identity=self.identity(user))

    def logout(self, token: str) -> None:
        row = self.session.get(AuthSession, token_hash(token))
        if row:
            row.revoked_at = utcnow()
            self.session.commit()

    def recipient(self, user_id: UUID) -> str:
        account = self.session.get(AuthAccount, user_id)
        if account is None:
            raise EvidenceError("LOCAL_ACCOUNT_REQUIRED", "本地账号未配置", 403)
        return str(
            vault_for(self.session, self.config).open(
                account.email_ciphertext, "account:" + str(user_id)
            )["email"]
        )
