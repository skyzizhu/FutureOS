import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from hashlib import sha256

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from infra.accounts import AccountRepository, AuthRateLimited
from infra.db import AuthAttempt, utcnow
from tests.integration.test_m4_reports import PASSWORD, account, registration_data


def test_concurrent_admission_cannot_exceed_account_limit(runtime):
    _, engine, config = runtime
    config.auth_identity_attempts = 3
    identity = sha256(b"synthetic-identity").hexdigest()

    def attempt(_):
        with Session(engine) as session:
            try:
                AccountRepository(session, config).attempt(identity)
                return "accepted"
            except AuthRateLimited:
                return "limited"

    with ThreadPoolExecutor(max_workers=4) as pool:
        outcomes = list(pool.map(attempt, range(12)))
    assert outcomes.count("accepted") == 3
    assert outcomes.count("limited") == 9
    with Session(engine) as session:
        assert session.scalar(select(func.count()).select_from(AuthAttempt)) == 3


def test_source_limit_does_not_trust_forwarded_ip_and_precedes_kdf(runtime, monkeypatch):
    client, engine, config = runtime
    config.auth_source_attempts = 3
    calls = []

    def reject(password, encoded):
        calls.append(encoded)
        return False

    monkeypatch.setattr("infra.accounts.password_matches", reject)
    for i in range(4):
        response = client.post(
            "/api/v1/auth/login",
            json={"email": f"unknown-{i}@example.invalid", "password": PASSWORD},
            headers={"X-Forwarded-For": f"203.0.113.{i}", "X-Real-IP": f"192.0.2.{i}"},
        )
        assert response.status_code == (401 if i < 3 else 429), response.text
    assert len(calls) == 3 and all(v is None for v in calls)
    assert 0 < int(response.headers["Retry-After"]) <= 900
    assert response.headers["Cache-Control"] == "private, no-store"
    with Session(engine) as session:
        sources = session.scalars(select(AuthAttempt.source_hash)).all()
        assert len(set(sources)) == 1 and len(sources[0]) == 64
        assert "testclient" not in sources[0]


def test_limit_survives_repository_restart_and_expires_without_permanent_lock(runtime, monkeypatch):
    _, engine, config = runtime
    config.auth_identity_attempts = 1
    original = utcnow()
    monkeypatch.setattr("infra.accounts.utcnow", lambda: original)
    with Session(engine) as session:
        AccountRepository(session, config).attempt("a" * 64)
    with Session(engine) as session, pytest.raises(AuthRateLimited) as caught:
        AccountRepository(session, config).attempt("a" * 64)
    assert caught.value.retry_after == 900
    monkeypatch.setattr("infra.accounts.utcnow", lambda: original + timedelta(seconds=901))
    with Session(engine) as session:
        AccountRepository(session, config).attempt("a" * 64)
        assert session.scalar(select(func.count()).select_from(AuthAttempt)) == 1


def test_global_limit_applies_across_accounts_and_sources(runtime):
    _, engine, config = runtime
    config.auth_global_attempts = 3
    with Session(engine) as session:
        for i in range(3):
            AccountRepository(session, config).attempt(str(i) * 64, source=f"peer-{i}")
        with pytest.raises(AuthRateLimited):
            AccountRepository(session, config).attempt("x" * 64, source="different-peer")


def test_register_and_login_share_source_quota(runtime, monkeypatch):
    client, _, config = runtime
    config.auth_source_attempts = 4
    _, _, email = account(client)
    monkeypatch.setattr("infra.accounts.password_matches", lambda *_: False)
    assert (
        client.post("/api/v1/auth/login", json={"email": email, "password": PASSWORD}).status_code
        == 401
    )
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "second@example.invalid",
            "password": PASSWORD,
            **registration_data(client, "second@example.invalid"),
        },
    )
    assert response.status_code == 429
    assert "Retry-After" in response.headers


def test_missing_and_existing_accounts_have_same_login_error_and_kdf_path(runtime, monkeypatch):
    client, _, _ = runtime
    _, _, email = account(client)
    observed = []

    def reject(password, encoded):
        observed.append(encoded)
        return False

    monkeypatch.setattr("infra.accounts.password_matches", reject)
    responses = [
        client.post("/api/v1/auth/login", json={"email": address, "password": PASSWORD})
        for address in [email, "missing@example.invalid"]
    ]
    assert [r.status_code for r in responses] == [401, 401]
    assert [(r.json()["code"], r.json()["message"]) for r in responses] == [
        ("AUTH_REQUIRED", "邮箱或密码不匹配")
    ] * 2
    assert observed[0].startswith("scrypt-v1$") and observed[1] is None


def test_saturated_password_workers_reject_without_waiting(runtime, monkeypatch):
    client, _, _ = runtime
    slots = threading.BoundedSemaphore(1)
    slots.acquire()
    monkeypatch.setattr("infra.accounts._HASH_SLOTS", slots)
    try:
        response = client.post(
            "/api/v1/auth/login", json={"email": "missing@example.invalid", "password": PASSWORD}
        )
        assert response.status_code == 503
        assert response.json()["code"] == "AUTH_BUSY"
        assert response.headers["Retry-After"] == "2"
    finally:
        slots.release()
