from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from infra.accounts import vault_for
from infra.db import AuthAccessEvent, AuthAccount, AuthAttempt, AuthEmailCode
from tests.integration.test_m4_reports import PASSWORD, registration_data


def test_auth_events_link_browser_encrypt_context_and_reject_injection(runtime):
    client, engine, config = runtime
    browser = TestClient(client.app, client=("127.0.0.2", 4321), raise_server_exceptions=False)
    email = "audit-test@example.invalid"
    agent = "Mozilla/5.0 (Macintosh) Chrome/130.0"
    device = str(uuid4())
    headers = {
        "User-Agent": agent,
        "Accept-Language": "zh-CN",
        "X-FutureOS-Auth-Device": device,
        "X-Forwarded-For": "203.0.113.55",
        "X-Real-IP": "203.0.113.55",
    }
    proof = registration_data(browser, email)
    registration = browser.post(
        "/api/v1/auth/register",
        json={"email": email, "password": PASSWORD, **proof},
        headers=headers,
    )
    assert registration.status_code == 201
    auth = {"Authorization": "Bearer " + registration.json()["access_token"]}
    reused = browser.post(
        "/api/v1/auth/register",
        json={"email": email, "password": PASSWORD, **proof},
        headers=headers,
    )
    assert reused.status_code == 401
    wrong = browser.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "' OR 1=1 -- DROP TABLE users"},
        headers=headers,
    )
    assert wrong.status_code == 401
    malformed = browser.post(
        "/api/v1/auth/login",
        json={"email": "' OR 1=1 --", "password": PASSWORD},
        headers=headers,
    )
    assert malformed.status_code == 422
    assert "DROP TABLE" not in wrong.text
    with Session(engine) as session:
        events = session.scalars(select(AuthAccessEvent).order_by(AuthAccessEvent.created_at)).all()
        assert [(e.action, e.outcome) for e in events] == [
            ("register", "succeeded"),
            ("register", "rejected"),
            ("login", "rejected"),
        ]
        assert len({e.device_hash for e in events}) == 1
        vault = vault_for(session, config)
        for event in events:
            assert len(event.device_hash) == 64 and device != event.device_hash
            context = vault.open(event.context_ciphertext, "auth-access:" + str(event.id))
            assert context == {
                "peer_ip": "127.0.0.2",
                "device": "Chrome / macOS",
                "user_agent": agent,
                "accept_language": "zh-CN",
                "fingerprint_kind": "browser",
            }
            assert "127.0.0.2" not in event.context_ciphertext
        assert session.scalar(select(func.count()).select_from(AuthAccount)) == 1
        assert events[-1].reason == "AUTH_REQUIRED"
        assert str(events[-1].request_id) == wrong.headers["X-Request-ID"]
    assert browser.get("/api/v1/admin/security/audit", headers=auth).status_code == 403
    exported = browser.get("/api/v1/me/export", headers=auth)
    assert exported.status_code == 200
    events = exported.json()["auth_access_events"]
    assert len(events) == 1 and events[0]["peer_ip"] == "127.0.0.2"
    erased = browser.request(
        "DELETE",
        "/api/v1/me/data",
        headers=auth,
        json={"password": PASSWORD, "confirmation": "DELETE MY DATA"},
    )
    assert erased.status_code == 200
    with Session(engine) as session:
        assert session.scalar(select(func.count()).select_from(AuthAccessEvent)) == 0
        assert session.scalar(select(func.count()).select_from(AuthAttempt)) == 0


def test_browser_budget_applies_across_mailboxes_and_peers(runtime, monkeypatch):
    client, engine, config = runtime
    config.auth_device_attempts = 2
    monkeypatch.setattr("infra.accounts.password_matches", lambda *_: False)
    headers = {"X-FutureOS-Auth-Device": str(uuid4())}
    for index in range(3):
        peer = TestClient(client.app, client=(f"127.0.0.{index + 1}", 4321))
        response = peer.post(
            "/api/v1/auth/login",
            headers=headers,
            json={"email": f"browser-limit-{index}@example.invalid", "password": PASSWORD},
        )
        assert response.status_code == (401 if index < 2 else 429)
    assert int(response.headers["Retry-After"]) > 0
    with Session(engine) as session:
        assert session.scalar(select(func.count()).select_from(AuthAttempt)) == 2
        rejected = session.scalar(
            select(AuthAccessEvent).where(AuthAccessEvent.reason == "AUTH_RATE_LIMITED")
        )
        assert rejected is not None


def test_code_daily_budget_is_atomic_across_mailboxes(runtime):
    client, engine, config = runtime
    config.auth_email_global_daily_sends = 2

    def send(index):
        return client.post(
            "/api/v1/auth/email-code",
            json={"email": f"code-limit-{index}@example.invalid", "purpose": "register"},
        )

    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(send, range(5)))
    assert sorted(r.status_code for r in results) == [200, 200, 429, 429, 429]
    assert all(int(r.headers["Retry-After"]) > 0 for r in results if r.status_code == 429)
    with Session(engine) as session:
        assert session.scalar(select(func.count()).select_from(AuthEmailCode)) == 2
