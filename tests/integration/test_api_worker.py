from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from uuid import uuid4

from prediction_engine.contracts.models import DemoResearchInputV1
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from apps.api.jobs import submit
from infra.db import InboxProcessed, Job, OutboxEvent, utcnow
from scripts.seed_demo import USER_ID
from tests.conftest import ADMIN_HEADERS, USER_HEADERS
from workers.research.main import run_once


def create(client, key="job-key", question="DEMO research"):
    return client.post(
        "/api/v1/demo/research",
        headers={**USER_HEADERS, "Idempotency-Key": key},
        json={"question": question},
    )


def test_health_and_full_mock_workflow(runtime):
    client, engine, config = runtime
    assert client.get("/api/v1/health/live").json()["label"] == "DEMO"
    assert client.get("/api/v1/health/ready").status_code == 200
    accepted = create(client)
    assert accepted.status_code == 202
    job_id = accepted.json()["job_id"]
    assert client.get(f"/api/v1/jobs/{job_id}", headers=USER_HEADERS).json()["status"] == "queued"
    assert run_once(engine, config)
    job = client.get(f"/api/v1/jobs/{job_id}", headers=USER_HEADERS).json()
    assert job["status"] == "succeeded"
    assert job["attempts"] == 1
    assert job["result"]["label"] == "DEMO"
    assert job["result"]["kind"] == "hypothesis"
    assert job["result"]["cost_units"] == 0
    assert not run_once(engine, config)
    with Session(engine) as session:
        assert session.scalar(select(func.count()).select_from(InboxProcessed)) == 1
        assert session.scalar(select(func.count()).select_from(OutboxEvent)) == 2
    assert client.get("/api/v1/admin/overview", headers=ADMIN_HEADERS).json()["job_counts"] == {
        "succeeded": 1
    }


def test_replay_and_changed_payload(runtime):
    client, engine, _ = runtime
    assert create(client).json() == create(client).json()
    conflict = create(client, question="changed request")
    assert conflict.status_code == 409
    assert conflict.json()["code"] == "IDEMPOTENCY_CONFLICT"
    with Session(engine) as session:
        assert session.scalar(select(func.count()).select_from(Job)) == 1
        assert session.scalar(select(func.count()).select_from(OutboxEvent)) == 1


def test_concurrent_submission_and_claim(runtime):
    _, engine, config = runtime

    def enqueue(_):
        with Session(engine) as session:
            return submit(
                session, USER_ID, "concurrent", DemoResearchInputV1(question="DEMO concurrent")
            ).id

    with ThreadPoolExecutor(max_workers=4) as pool:
        ids = list(pool.map(enqueue, range(8)))
    assert len(set(ids)) == 1
    with ThreadPoolExecutor(max_workers=3) as pool:
        list(pool.map(lambda _: run_once(engine, config), range(3)))
    with Session(engine) as session:
        job = session.get(Job, ids[0])
        assert job.status == "succeeded"
        assert job.attempts == 1
        assert session.scalar(select(func.count()).select_from(InboxProcessed)) == 1


class BrokenSearch:
    async def search(self, *args, **kwargs):
        raise ConnectionError("sensitive-provider-error")


class EmptySearch:
    async def search(self, *args, **kwargs):
        return ()


def test_retry_then_recover(runtime):
    client, engine, config = runtime
    job_id = create(client).json()["job_id"]
    assert run_once(engine, config, search=BrokenSearch())
    failed = client.get(f"/api/v1/jobs/{job_id}", headers=USER_HEADERS).json()
    assert failed["status"] == "failed_retryable"
    assert failed["error_code"] == "PROVIDER_UNAVAILABLE"
    assert "sensitive" not in str(failed)
    with Session(engine) as session:
        job = session.scalar(select(Job))
        job.available_at = utcnow() - timedelta(seconds=1)
        session.commit()
    assert run_once(engine, config)
    result = client.get(f"/api/v1/jobs/{job_id}", headers=USER_HEADERS).json()
    assert result["status"] == "succeeded"
    assert result["attempts"] == 2
    assert result["error_code"] is None


def test_unverified_evidence_fails_closed(runtime):
    client, engine, config = runtime
    job_id = create(client).json()["job_id"]
    run_once(engine, config, search=EmptySearch())
    result = client.get(f"/api/v1/jobs/{job_id}", headers=USER_HEADERS).json()
    assert result["status"] == "failed_terminal"
    assert result["result"] is None
    with Session(engine) as session:
        assert session.scalar(select(func.count()).select_from(InboxProcessed)) == 0


def test_expired_lease_recovered_and_capped(runtime):
    client, engine, config = runtime
    create(client)
    with Session(engine) as session:
        job = session.scalar(select(Job))
        job.status = "running"
        job.attempts = 1
        job.lease_token = uuid4()
        job.lease_until = utcnow() - timedelta(seconds=1)
        session.commit()
    assert run_once(engine, config)
    assert client.get("/api/v1/admin/overview", headers=ADMIN_HEADERS).json()["job_counts"] == {
        "succeeded": 1
    }
    create(client, key="exhausted")
    with Session(engine) as session:
        job = session.scalar(select(Job).where(Job.idempotency_key == "exhausted"))
        job.status = "running"
        job.attempts = config.job_max_attempts
        job.lease_until = utcnow() - timedelta(seconds=1)
        session.commit()
    assert not run_once(engine, config)
    with Session(engine) as session:
        job = session.scalar(select(Job).where(Job.idempotency_key == "exhausted"))
        assert job.status == "failed_terminal"
        assert job.error_code == "JOB_RETRY_EXHAUSTED"
