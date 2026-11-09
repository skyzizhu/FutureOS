"""Fixed Turnstile endpoint; server validation, hostname/action and replay gates."""

from datetime import datetime, timedelta

import httpx
from prediction_engine.evidence.temporal import utc
from sqlalchemy import delete, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from infra.accounts import AccountRepository, normalized_email, token_hash, vault_for
from infra.db import AuthAttempt, AuthHumanToken, utcnow
from infra.evidence_repository import EvidenceError
from infra.settings import Settings


def login_needs_human(session: Session, config: Settings, email: str) -> bool:
    if not config.turnstile_enabled:
        return False
    lookup = vault_for(session, config).lookup(normalized_email(email))
    latest_success = session.scalar(
        select(func.max(AuthAttempt.created_at)).where(
            AuthAttempt.identity_hash == lookup, AuthAttempt.outcome == "succeeded"
        )
    )
    since = (
        max(utc(latest_success), utcnow() - timedelta(seconds=config.auth_window_seconds))
        if latest_success
        else utcnow() - timedelta(seconds=config.auth_window_seconds)
    )
    count = (
        session.scalar(
            select(func.count())
            .select_from(AuthAttempt)
            .where(
                AuthAttempt.identity_hash == lookup,
                AuthAttempt.created_at > since,
                AuthAttempt.outcome == "failed",
            )
        )
        or 0
    )
    return count >= 3


def verify_human(session: Session, config: Settings, token: str, action: str) -> None:
    if not config.turnstile_enabled:
        return
    if not token or len(token) > 2048:
        raise EvidenceError("HUMAN_VERIFICATION_REQUIRED", "请先完成动态验证", 403)
    assert config.turnstile_secret_key is not None
    try:
        with httpx.Client(timeout=5, trust_env=False, follow_redirects=False) as client:
            response = client.post(
                "https://challenges.cloudflare.com/turnstile/v0/siteverify",
                json={"secret": config.turnstile_secret_key.get_secret_value(), "response": token},
            )
            if response.status_code != 200 or len(response.content) > 16000:
                raise ValueError("invalid response")
            data = response.json()
        if not isinstance(data, dict):
            raise ValueError("invalid response")
        if data.get("success") is not True:
            raise EvidenceError("HUMAN_VERIFICATION_FAILED", "动态验证无效，请重新验证", 403)
        if not isinstance(data.get("challenge_ts"), str):
            raise ValueError("invalid timestamp")
        issued = datetime.fromisoformat(data["challenge_ts"].replace("Z", "+00:00"))
        if issued.tzinfo is None or not -30 <= (utcnow() - issued).total_seconds() <= 300:
            raise EvidenceError("HUMAN_VERIFICATION_FAILED", "动态验证已过期，请重新验证", 403)
        if (
            data.get("success") is not True
            or data.get("hostname") not in config.turnstile_hostnames
            or data.get("action") != action
        ):
            raise EvidenceError("HUMAN_VERIFICATION_FAILED", "动态验证无效，请重新验证", 403)
    except (httpx.HTTPError, ValueError, TypeError, KeyError):
        raise EvidenceError(
            "HUMAN_VERIFICATION_UNAVAILABLE", "动态验证服务暂不可用，请稍后再试", 503
        ) from None
    session.execute(delete(AuthHumanToken).where(AuthHumanToken.expires_at <= utcnow()))
    session.add(
        AuthHumanToken(token_hash=token_hash(token), expires_at=utcnow() + timedelta(minutes=5))
    )
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise EvidenceError(
            "HUMAN_VERIFICATION_FAILED", "动态验证已经使用，请重新验证", 403
        ) from None


def guard_login(
    session: Session,
    config: Settings,
    email: str,
    token: str,
    source: str,
    action: str,
    device_hash: str | None = None,
) -> None:
    if login_needs_human(session, config, email):
        lookup = vault_for(session, config).lookup(normalized_email(email))
        AccountRepository(session, config).attempt(
            token_hash("human-login:" + lookup), source, device_hash
        )
        verify_human(session, config, token, action)
