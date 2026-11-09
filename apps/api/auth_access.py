"""Collect bounded authentication metadata from the actual connection and browser."""

import hashlib
import hmac
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from ipaddress import ip_address
from typing import Literal
from uuid import UUID, uuid4

from fastapi import Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from infra.accounts import device_label, normalized_email, vault_for
from infra.db import AuthAccessEvent, AuthAccount, utcnow
from infra.evidence_repository import EvidenceError
from infra.settings import Settings


def auth_source(request: Request) -> str:
    return request.client.host if request.client else "unknown-peer"


def peer_ip(request: Request) -> str | None:
    try:
        return str(ip_address(auth_source(request)))
    except ValueError:
        return None


def browser_hash(session: Session, config: Settings, request: Request) -> str | None:
    peer = peer_ip(request)
    if peer is None or not ip_address(peer).is_loopback:
        return None
    value = request.headers.get("x-futureos-auth-device", "")
    if len(value) != 36:
        return None
    try:
        identifier = UUID(value)
    except ValueError:
        return None
    if identifier.version != 4:
        return None
    return hmac.new(
        vault_for(session, config).key,
        b"auth-browser-v1:" + identifier.bytes,
        hashlib.sha256,
    ).hexdigest()


@dataclass
class Access:
    source: str
    device: str
    device_hash: str | None
    user_id: UUID | None = None


@contextmanager
def auth_access(
    session: Session,
    config: Settings,
    request: Request,
    action: Literal["register", "login"],
    email: str,
) -> Iterator[Access]:
    now = utcnow()
    vault = vault_for(session, config)
    identity = vault.lookup(normalized_email(email))
    ua = request.headers.get("user-agent", "")[:500]
    language = request.headers.get("accept-language", "")[:120]
    device_hash = browser_hash(session, config, request)
    event_id = uuid4()
    access = Access(auth_source(request), device_label(ua), device_hash)
    fingerprint = (
        device_hash
        or hmac.new(
            vault.key, ("auth-headers-v1:" + ua + "\0" + language).encode(), hashlib.sha256
        ).hexdigest()
    )
    ciphertext = vault.seal(
        {
            "peer_ip": peer_ip(request),
            "device": access.device,
            "user_agent": ua,
            "accept_language": language,
            "fingerprint_kind": "browser" if device_hash else "client_headers",
        },
        "auth-access:" + str(event_id),
    )
    event = AuthAccessEvent(
        id=event_id,
        identity_hash=identity,
        request_id=UUID(request.state.request_id),
        action=action,
        device_hash=fingerprint,
        context_ciphertext=ciphertext,
        created_at=now,
    )
    try:
        yield access
    except Exception as exc:
        # Retain security counters committed by the authentication service.
        session.rollback()
        event.user_id = session.scalar(
            select(AuthAccount.user_id).where(AuthAccount.email_lookup == identity)
        )
        event.outcome = "rejected"
        event.reason = exc.code if isinstance(exc, EvidenceError) else "INTERNAL_ERROR"
        session.add(event)
        session.commit()
        raise
    else:
        event.user_id = access.user_id
        event.outcome = "succeeded"
        session.add(event)
        session.commit()
