from uuid import UUID

import pytest
from sqlalchemy import select, text
from sqlalchemy.exc import DatabaseError
from sqlalchemy.orm import Session

from infra.db import (
    AuthAccount,
    AuthSession,
    ForecastVersion,
    Job,
    PrivacyErasure,
    ProfileSnapshot,
    UsageLedger,
    UserReportVersion,
)
from infra.erasure_journal import read_tombstones
from tests.integration.test_m4_reports import PASSWORD, account, complete_report, profile
from tests.integration.test_m6_commerce import commerce as commerce
from tests.integration.test_m6_commerce import drain, purchase, submit, user

ERASE = {"password": PASSWORD, "confirmation": "DELETE MY DATA"}


def test_erasure_reauth_owner_all_private_versions_and_shared_public_survives(runtime):
    client, engine, config = runtime
    owner, state, email = account(client)
    other, _, _ = account(client)
    profile(client, owner, occupation_text="Private-delete-test", use_optional_fields=True)
    _, report = complete_report(runtime, owner)
    exported = client.get("/api/v1/me/export", headers=owner)
    assert exported.status_code == 200 and len(exported.json()["reports"]) == 1
    assert "password_hash" not in exported.text and "access_token" not in exported.text
    assert (
        client.request(
            "DELETE", "/api/v1/me/data", headers=owner, json={**ERASE, "confirmation": "no"}
        ).status_code
        == 422
    )
    assert (
        client.request(
            "DELETE",
            "/api/v1/me/data",
            headers=owner,
            json={**ERASE, "password": "Wrong-password-123!"},
        ).status_code
        == 401
    )
    assert client.get("/api/v1/reports/" + report["report_id"], headers=owner).status_code == 200
    with Session(engine) as session:
        public_before = session.scalars(select(ForecastVersion.immutable_hash)).all()
    result = client.request("DELETE", "/api/v1/me/data", headers=owner, json=ERASE)
    assert result.status_code == 200, result.text
    assert result.json()["cleared_records"]["user_report_versions"] == 1
    assert client.get("/api/v1/me/profile", headers=owner).status_code == 401
    assert client.get("/api/v1/reports/" + report["report_id"], headers=owner).status_code == 401
    assert (
        client.post("/api/v1/auth/login", json={"email": email, "password": PASSWORD}).status_code
        == 401
    )
    assert client.get("/api/v1/auth/identity", headers=other).status_code == 200
    uid = UUID(state["identity"]["user_id"])
    with Session(engine) as session:
        assert session.get(AuthAccount, uid) is None
        assert session.scalar(select(AuthSession).where(AuthSession.user_id == uid)) is None
        assert (
            session.scalar(select(UserReportVersion).where(UserReportVersion.user_id == uid))
            is None
        )
        assert (
            session.scalar(select(ProfileSnapshot).where(ProfileSnapshot.user_id == uid)).ciphertext
            == "ERASED"
        )
        assert session.scalars(select(ForecastVersion.immutable_hash)).all() == public_before
        assert session.scalar(select(UsageLedger).where(UsageLedger.user_id == uid)) is not None
        assert (
            session.scalar(select(PrivacyErasure).where(PrivacyErasure.user_id == uid)) is not None
        )
    assert read_tombstones(config.profile_key_path)[0]["user_id"] == str(uid)
    with engine.begin() as conn:
        with pytest.raises(DatabaseError):
            conn.execute(text("UPDATE privacy_erasures SET counts='{}'"))


def test_erasure_of_funded_pending_job_releases_without_worker_resurrection(commerce):
    client, engine, config = commerce
    owner, uid = user(commerce)
    purchase(commerce, owner)
    _, accepted = submit(commerce, owner)
    result = client.request("DELETE", "/api/v1/me/data", headers=owner, json=ERASE)
    assert result.status_code == 200, result.text
    drain(commerce)
    with Session(engine) as session:
        job = session.get(Job, UUID(accepted.json()["job_id"]))
        assert job.status == "cancelled" and job.result is None and job.payload.get("erased")
        from infra.db import ResearchCreditGrant, UserResearchTopic

        grant = session.scalar(
            select(ResearchCreditGrant).where(ResearchCreditGrant.user_id == uid)
        )
        assert grant.reserved == 0 and grant.consumed == 0
        topic = session.scalar(select(UserResearchTopic).where(UserResearchTopic.user_id == uid))
        assert topic.scope_fingerprint == "0" * 64 and not topic.periodic_enabled


def test_body_limit_no_secret_echo_and_private_errors_not_cached(runtime):
    client, _, _ = runtime
    response = client.post("/api/v1/auth/login", content=b"X" * (1048576 + 1))
    assert response.status_code == 413 and "XXXX" not in response.text
    assert response.json()["request_id"] == response.headers["X-Request-ID"]
    response = client.get("/api/v1/me/profile")
    assert response.status_code == 401 and "no-store" in response.headers["cache-control"]
