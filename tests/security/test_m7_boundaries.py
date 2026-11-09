import asyncio
import io
import json
import socket
import zipfile
from datetime import timedelta
from hashlib import sha256
from unittest.mock import AsyncMock

import httpx
import pytest
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from pydantic import SecretStr
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from infra.backup import decrypt_bundle, encrypt_bundle
from infra.db import Job, OutboxEvent, utcnow
from infra.providers.deepseek import DeepSeekWebProvider, validate_public_url
from tests.conftest import ADMIN_HEADERS, USER_HEADERS
from workers.research.main import run_once


@pytest.mark.parametrize(
    "url",
    [
        "http://127.0.0.1",
        "http://169.254.169.254/latest/meta-data",
        "http://[::1]/",
        "http://[::ffff:127.0.0.1]/",
        "http://2130706433/",
        "http://0x7f000001/",
        "http://127.1/",
        "http://secret.internal/",
        "https://user:secret@example.org/",
        "https://example.org:8080/",
        "https://example.org\\@127.0.0.1/",
        "file:///etc/passwd",
        "https://%31%32%37.0.0.1/",
        "javascript:alert(1)",
        "https://example.org/\r\nX:bad",
    ],
)
def test_ssrf_url_forms_fail_closed(url):
    with pytest.raises(ValueError):
        validate_public_url(url)


def test_fetch_allowlist_and_mixed_private_dns_no_supplier_call(monkeypatch):
    requests = []

    async def scenario():
        provider = DeepSeekWebProvider(
            SecretStr("fake-key"),
            allowed_hosts=("example.org",),
            transport=httpx.MockTransport(lambda request: requests.append(request)),
        )
        with pytest.raises(ValueError, match="host_not_allowed"):
            await provider.fetch("https://example.org.evil.invalid/")
        provider.resolve_dns = True
        monkeypatch.setattr(
            asyncio.get_running_loop(),
            "getaddrinfo",
            AsyncMock(
                return_value=[
                    (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("8.8.8.8", 443)),
                    (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("127.0.0.1", 443)),
                ]
            ),
        )
        with pytest.raises(ValueError, match="dns_not_public"):
            await provider.fetch("https://example.org/")
        await provider.aclose()

    asyncio.run(scenario())
    assert requests == []


def test_encrypted_backup_rejects_wrong_key_tamper_and_unexpected_paths():
    key = AESGCM.generate_key(bit_length=256)
    stream = io.BytesIO()
    dump = b"private database bytes"
    with zipfile.ZipFile(stream, "w") as archive:
        archive.writestr("db.dump", dump)
        archive.writestr("private-profile.key", b"x" * 32)
        archive.writestr("manifest.json", json.dumps({"dump_sha256": sha256(dump).hexdigest()}))
    encrypted = encrypt_bundle(stream.getvalue(), key)
    assert b"private database bytes" not in encrypted
    assert decrypt_bundle(encrypted, key)["db.dump"] == dump
    with pytest.raises(InvalidTag):
        decrypt_bundle(encrypted, AESGCM.generate_key(bit_length=256))
    with pytest.raises(InvalidTag):
        decrypt_bundle(encrypted[:-1] + bytes([encrypted[-1] ^ 1]), key)
    bad = io.BytesIO()
    with zipfile.ZipFile(bad, "w") as archive:
        archive.writestr("../../escape", b"bad")
    with pytest.raises(ValueError, match="MEMBERS"):
        decrypt_bundle(encrypt_bundle(bad.getvalue(), key), key)


def test_queue_budget_idempotency_worker_claims_and_expired_lease_recovery(runtime):
    client, engine, config = runtime
    accepted = []
    for i in range(config.queue_max_pending_per_user):
        response = client.post(
            "/api/v1/demo/research",
            headers={**USER_HEADERS, "Idempotency-Key": f"load-{i}"},
            json={"question": "DEMO bounded pressure test"},
        )
        assert response.status_code == 202, response.text
        accepted.append(response.json())
    assert (
        client.post(
            "/api/v1/demo/research",
            headers={**USER_HEADERS, "Idempotency-Key": "over-budget"},
            json={"question": "DEMO over budget"},
        ).status_code
        == 429
    )
    assert (
        client.post(
            "/api/v1/demo/research",
            headers={**USER_HEADERS, "Idempotency-Key": "load-0"},
            json={"question": "DEMO bounded pressure test"},
        ).json()
        == accepted[0]
    )
    from concurrent.futures import ThreadPoolExecutor

    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(lambda _: run_once(engine, config), range(30)))
    while run_once(engine, config):
        pass
    with Session(engine) as session:
        jobs = session.scalars(select(Job).where(Job.idempotency_key.like("load-%"))).all()
        assert len(jobs) == 20 and all(j.status == "succeeded" for j in jobs)
        assert (
            session.scalar(
                select(func.count())
                .select_from(OutboxEvent)
                .where(OutboxEvent.event_type == "DemoResearchCompleted.v1")
            )
            == 20
        )
    status = client.get("/api/v1/admin/readiness", headers=ADMIN_HEADERS)
    assert status.status_code == 200 and status.json()["production_ready"] is False
    assert client.get("/api/v1/admin/readiness", headers=USER_HEADERS).status_code == 403


def test_worker_redis_failure_keeps_db_polling(runtime, monkeypatch):
    _, engine, config = runtime
    from unittest.mock import MagicMock

    import redis

    import workers.research.main as worker

    cache = MagicMock()
    cache.set.side_effect = redis.ConnectionError("synthetic outage")
    monkeypatch.setattr(
        worker, "get_settings", lambda: config.model_copy(update={"require_redis": True})
    )
    monkeypatch.setattr(worker.redis.Redis, "from_url", lambda *args, **kwargs: cache)
    monkeypatch.setattr("sys.argv", ["worker", "--once"])
    worker.main()


def test_admin_shorter_cooldown_applies_to_current_deadline(runtime):
    from uuid import UUID

    from infra.db import ForecastMonitor, ForecastVersion
    from tests.integration.test_m4_reports import account, complete_report, profile

    client, engine, _ = runtime
    owner, _, _ = account(client)
    profile(client, owner)
    _, report = complete_report(runtime, owner)
    with Session(engine) as session:
        identifier = session.get(
            ForecastVersion, UUID(report["forecast_version_ids"][0])
        ).forecast_id
    client.get("/api/v1/admin/monitor/forecasts", headers=ADMIN_HEADERS)
    with Session(engine) as session:
        monitor = session.get(ForecastMonitor, identifier)
        monitor.cooldown_until = utcnow() + timedelta(hours=6)
        session.commit()
    response = client.put(
        "/api/v1/admin/monitor/forecasts/" + str(identifier) + "/policy",
        headers=ADMIN_HEADERS,
        json={"cooldown_seconds": 0},
    )
    assert response.status_code == 200, response.text
    with Session(engine) as session:
        from prediction_engine.evidence.temporal import utc

        assert utc(session.get(ForecastMonitor, identifier).cooldown_until) <= utcnow()
