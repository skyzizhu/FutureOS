from datetime import timedelta
from uuid import UUID, uuid4

import pytest
from sqlalchemy import func, select, text, update
from sqlalchemy.exc import DatabaseError
from sqlalchemy.orm import Session

from infra.db import (
    AuthAccount,
    AuthSession,
    EntitlementReservation,
    ForecastVersion,
    Job,
    LocalEmailDelivery,
    ModelCall,
    ProfileSnapshot,
    ReportCatalogEntry,
    UsageLedger,
    UserReportVersion,
)
from tests.conftest import ADMIN_HEADERS
from workers.research.main import run_once

PASSWORD = "Local-test-password-123!"


def registration_data(client, email):
    from infra.accounts import vault_for
    from infra.db import AuthEmailCode

    sent = client.post("/api/v1/auth/email-code", json={"email": email, "purpose": "register"})
    assert sent.status_code == 200, sent.text
    identifier = UUID(sent.json()["challenge_id"])
    with Session(client.app.state.engine) as session:
        row = session.get(AuthEmailCode, identifier)
        code = vault_for(session, client.app.state.settings).open(
            row.code_ciphertext, "auth-code:" + str(identifier)
        )["code"]
    return {"verification_id": str(identifier), "code": code}


def account(client, email=None):
    email = email or f"m4-{uuid4().hex[:12]}@example.invalid"
    response = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": PASSWORD, **registration_data(client, email)},
    )
    assert response.status_code == 201, response.text
    state = response.json()
    return {"Authorization": "Bearer " + state["access_token"]}, state, email


def profile(client, headers, **changes):
    value = {"industry_l1_code": "technology", "industry_l2_code": "software", **changes}
    response = client.put("/api/v1/me/profile", headers=headers, json=value)
    assert response.status_code == 200, response.text
    return response.json()


def submit(client, headers, label="DEMO", key="first", **changes):
    return client.post(
        "/api/v1/research/first-report",
        headers={**headers, "Idempotency-Key": key},
        json={"label": label, **changes},
    )


def complete_report(runtime, headers):
    client, engine, config = runtime
    accepted = submit(client, headers)
    assert accepted.status_code == 202, accepted.text
    job_id = accepted.json()["job_id"]
    assert run_once(engine, config)
    job = client.get("/api/v1/jobs/" + job_id, headers=headers)
    assert job.status_code == 200, job.text
    assert job.json()["status"] == "succeeded", job.text
    report = client.get("/api/v1/reports/" + job.json()["result"]["report_id"], headers=headers)
    assert report.status_code == 200, report.text
    return accepted.json(), report.json()


def test_register_password_session_logout_and_role_isolation(runtime):
    client, engine, _ = runtime
    headers, state, email = account(client, "Case.Test@example.invalid")
    assert state["identity"]["role"] == "user" and state["identity"]["email_verified"] is True
    assert "access_token" in state and "password" not in state
    assert client.get("/api/v1/admin/overview", headers=headers).status_code == 403
    assert (
        client.post(
            "/api/v1/auth/register", json={"email": email.lower(), "password": PASSWORD}
        ).status_code
        == 422
    )
    assert (
        client.post(
            "/api/v1/auth/register",
            json={"email": "role@example.invalid", "password": PASSWORD, "role": "admin"},
        ).status_code
        == 422
    )
    assert (
        client.post(
            "/api/v1/auth/login", json={"email": email, "password": "wrong-password-123!"}
        ).status_code
        == 401
    )
    login = client.post("/api/v1/auth/login", json={"email": email.lower(), "password": PASSWORD})
    assert login.status_code == 200, login.text
    with Session(engine) as session:
        row = session.get(AuthAccount, UUID(state["identity"]["user_id"]))
        assert row.password_hash.startswith("scrypt-v1$") and PASSWORD not in row.password_hash
        assert email not in row.email_ciphertext
        assert session.get(AuthSession, state["access_token"]) is None
    assert (
        client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": headers["Authorization"].replace("Bearer ", "bearer ")},
        ).status_code
        == 200
    )
    assert client.get("/api/v1/auth/identity", headers=headers).status_code == 401
    assert (
        client.get(
            "/api/v1/me", headers={"Authorization": "Bearer " + login.json()["access_token"]}
        ).status_code
        == 200
    )


def test_profile_only_industry_required_hierarchy_and_minimum_consent(runtime):
    client, engine, _ = runtime
    headers, _, _ = account(client)
    assert submit(client, headers).status_code == 409
    taxonomy = client.get("/api/v1/taxonomies/industries").json()
    assert len(taxonomy["entries"]) >= 24
    assert (
        client.put(
            "/api/v1/me/profile",
            headers=headers,
            json={"industry_l1_code": "technology", "industry_l2_code": "clinical"},
        ).status_code
        == 422
    )
    assert (
        client.put(
            "/api/v1/me/profile",
            headers=headers,
            json={
                "industry_l1_code": "technology",
                "industry_l2_code": "software",
                "gender": "must-not-be-required",
            },
        ).status_code
        == 422
    )
    saved = profile(
        client,
        headers,
        occupation_text="Private occupation string",
        goals=["Secret goal never shared"],
        use_optional_fields=False,
    )
    snapshot = client.post("/api/v1/me/profile/snapshots", headers=headers).json()
    assert (
        snapshot["consent_scope"] == "industry_only"
        and snapshot["profile"]["occupation_text"] == ""
        and snapshot["profile"]["goals"] == []
    )
    assert client.get("/api/v1/me/profile", headers=headers).json() == saved
    other, _, _ = account(client)
    assert (
        client.get(
            "/api/v1/me/profile/snapshots/" + snapshot["snapshot_id"], headers=other
        ).status_code
        == 404
    )
    with Session(engine) as session:
        raw = session.get(ProfileSnapshot, UUID(snapshot["snapshot_id"])).ciphertext
        assert "Secret goal never shared" not in raw


def test_free_full_report_pins_multiple_versions_once_and_no_network(runtime):
    client, engine, _ = runtime
    headers, _, _ = account(client)
    profile(client, headers)
    accepted, report = complete_report(runtime, headers)
    assert report["label"] == "DEMO" and len(report["forecast_version_ids"]) == 3
    assert report["primary_impacts"] and report["observation_only"]
    assert all(action["priority"] != "prepare" for action in report["recommendations"])
    assert all(
        "停止" in action["stop_or_revisit_condition"] for action in report["recommendations"]
    )
    credit = client.get("/api/v1/me/entitlements", headers=headers).json()
    assert credit["consumed"] == 1 and credit["available"] == 0 and credit["reserved"] == 0
    assert submit(client, headers).json() == accepted
    assert submit(client, headers, key="another").status_code == 409
    assert submit(client, headers, label="REAL").status_code == 409
    with Session(engine) as session:
        assert (
            session.scalar(
                select(func.count())
                .select_from(UsageLedger)
                .where(UsageLedger.entry_kind == "consumed")
            )
            == 1
        )
        assert session.scalar(select(func.count()).select_from(ModelCall)) == 0
        assert session.scalar(select(func.count()).select_from(ReportCatalogEntry)) == 3
        assert session.scalar(select(func.count()).select_from(LocalEmailDelivery)) == 0
        stored = session.get(UserReportVersion, UUID(report["report_version_id"]))
        assert report["title"] not in stored.ciphertext
    original = report.copy()
    profile(
        client,
        headers,
        industry_l1_code="healthcare",
        industry_l2_code="clinical",
        goals=["Changed goal"],
    )
    assert client.get("/api/v1/reports/" + report["report_id"], headers=headers).json() == original
    assert (
        client.get(
            "/api/v1/reports/" + report["report_id"] + "/versions/" + report["report_version_id"],
            headers=headers,
        ).json()
        == original
    )
    detail = client.get(
        "/api/v1/forecasts/versions/" + report["forecast_version_ids"][0], headers=headers
    )
    assert detail.status_code == 200 and detail.json()["claims"] and detail.json()["cases"]
    for table, assignment in [
        ("user_report_versions", "label='REAL'"),
        ("profile_snapshots", "profile_revision=99"),
        ("usage_ledger", "units_delta=99"),
        ("personal_impacts", "ciphertext='tamper'"),
        ("recommendations", "ciphertext='tamper'"),
    ]:
        with engine.begin() as connection:
            with pytest.raises(DatabaseError):
                connection.execute(text(f"UPDATE {table} SET {assignment}"))


def test_reservation_cancel_failure_and_expired_lease_release(runtime, monkeypatch):
    client, engine, config = runtime
    headers, state, _ = account(client)
    profile(client, headers)
    accepted = submit(client, headers).json()
    assert client.get("/api/v1/me/entitlements", headers=headers).json()["reserved"] == 1
    assert (
        client.post(
            "/api/v1/research/jobs/" + accepted["job_id"] + "/cancel", headers=headers
        ).status_code
        == 200
    )
    assert client.get("/api/v1/me/entitlements", headers=headers).json()["available"] == 1
    failed = submit(client, headers, key="fail").json()
    import workers.research.main as worker

    def fail(*args, **kwargs):
        raise ValueError("TEST_REPORT_FAILED")

    monkeypatch.setattr(worker, "execute_report", fail)
    assert run_once(engine, config)
    result = client.get("/api/v1/jobs/" + failed["job_id"], headers=headers).json()
    assert result["status"] == "failed_terminal" and result["error_code"] == "TEST_REPORT_FAILED"
    assert client.get("/api/v1/me/entitlements", headers=headers).json()["available"] == 1
    capped = submit(client, headers, key="capped").json()
    from infra.db import utcnow

    with Session(engine) as session:
        job = session.get(Job, UUID(capped["job_id"]))
        job.status = "running"
        job.attempts = config.job_max_attempts
        job.lease_until = utcnow() - timedelta(seconds=1)
        session.commit()
    run_once(engine, config)
    assert client.get("/api/v1/me/entitlements", headers=headers).json()["available"] == 1
    assert client.get("/api/v1/reports", headers=headers).json() == []


def test_other_user_cannot_read_report_job_feedback_snapshot_or_email(runtime):
    client, _, _ = runtime
    owner, _, _ = account(client)
    stranger, _, _ = account(client)
    profile(client, owner)
    accepted, report = complete_report(runtime, owner)
    for path in [
        "/reports/" + report["report_id"],
        "/reports/" + report["report_id"] + "/versions",
        "/reports/" + report["report_id"] + "/email-preview",
        "/jobs/" + accepted["job_id"],
        "/me/profile/snapshots/" + report["profile_snapshot_id"],
    ]:
        assert client.get("/api/v1" + path, headers=stranger).status_code == 404
    recommendation = report["recommendations"][0]["recommendation_id"]
    assert (
        client.post(
            "/api/v1/recommendations/" + recommendation + "/feedback",
            headers=stranger,
            json={"status": "helpful"},
        ).status_code
        == 404
    )
    assert (
        client.post(
            "/api/v1/reports/" + report["report_id"] + "/email",
            headers=stranger,
            json={"explicit_consent": True, "recipient": "wrong@example.invalid"},
        ).status_code
        == 404
    )
    assert client.get("/api/v1/reports", headers=stranger).json() == []
    assert (
        client.get("/api/v1/reports/" + report["report_id"], headers=ADMIN_HEADERS).status_code
        == 403
    )


def test_email_authorization_is_explicit_local_and_idempotent(runtime):
    client, engine, _ = runtime
    headers, _, email = account(client)
    profile(client, headers)
    _, report = complete_report(runtime, headers)
    path = "/api/v1/reports/" + report["report_id"]
    preview = client.get(path + "/email-preview", headers=headers).json()
    assert preview["external_delivery"] is False and preview["private_link"].startswith("/reports/")
    assert "industry" not in preview["summary"]
    assert (
        client.post(
            path + "/email", headers=headers, json={"explicit_consent": False, "recipient": email}
        ).status_code
        == 422
    )
    assert (
        client.post(
            path + "/email",
            headers=headers,
            json={"explicit_consent": True, "recipient": "other@example.invalid"},
        ).status_code
        == 409
    )
    response = client.post(
        path + "/email", headers=headers, json={"explicit_consent": True, "recipient": email}
    )
    assert response.status_code == 200, response.text
    assert response.json()["status"] == "saved_locally_not_sent"
    assert (
        client.post(
            path + "/email", headers=headers, json={"explicit_consent": True, "recipient": email}
        ).json()
        == response.json()
    )
    with Session(engine) as session:
        rows = session.scalars(select(LocalEmailDelivery)).all()
        assert len(rows) == 1 and email not in rows[0].recipient_ciphertext


def test_second_user_reuses_catalog_without_second_world_research(runtime):
    client, engine, _ = runtime
    first, _, _ = account(client)
    profile(client, first)
    _, a = complete_report(runtime, first)
    with Session(engine) as session:
        count = session.scalar(select(func.count()).select_from(ForecastVersion))
    second, _, _ = account(client)
    profile(client, second)
    _, b = complete_report(runtime, second)
    assert (
        a["forecast_version_ids"] == b["forecast_version_ids"] and a["report_id"] != b["report_id"]
    )
    with Session(engine) as session:
        assert session.scalar(select(func.count()).select_from(ForecastVersion)) == count
        assert (
            session.scalar(
                select(func.count())
                .select_from(UsageLedger)
                .where(UsageLedger.entry_kind == "consumed")
            )
            == 2
        )


def test_withdraw_optional_consent_cancels_pending_report(runtime):
    client, _, _ = runtime
    headers, _, _ = account(client)
    profile(client, headers, use_optional_fields=True, goals=["Private goal"])
    accepted = submit(client, headers).json()
    profile(client, headers, use_optional_fields=False)
    state = client.get("/api/v1/jobs/" + accepted["job_id"], headers=headers).json()
    assert state["status"] == "cancelled"
    assert client.get("/api/v1/me/entitlements", headers=headers).json()["available"] == 1


def test_real_insufficient_data_releases_quota_and_intake_is_free(runtime):
    client, engine, config = runtime
    headers, _, _ = account(client)
    profile(client, headers)
    response = client.post(
        "/api/v1/research/intake",
        headers=headers,
        json={"question": "What changes matter to my work?", "label": "REAL"},
    )
    assert response.status_code == 200 and response.json()["matched_version_ids"] == []
    assert client.get("/api/v1/me/entitlements", headers=headers).json()["available"] == 1
    accepted = submit(client, headers, label="REAL").json()
    assert run_once(engine, config)
    assert (
        client.get("/api/v1/jobs/" + accepted["job_id"], headers=headers).json()["error_code"]
        == "NO_APPROVED_FORECAST_AVAILABLE"
    )
    assert client.get("/api/v1/me/entitlements", headers=headers).json()["available"] == 1


def test_token_expiration_and_auth_rate_limit(runtime):
    client, engine, _ = runtime
    headers, state, email = account(client)
    from infra.accounts import token_hash
    from infra.db import utcnow

    with Session(engine) as session:
        row = session.get(AuthSession, token_hash(state["access_token"]))
        row.expires_at = utcnow() - timedelta(seconds=1)
        session.commit()
    assert client.get("/api/v1/me/profile", headers=headers).status_code == 401
    for _ in range(12):
        response = client.post(
            "/api/v1/auth/login", json={"email": email, "password": "incorrect-but-long-password"}
        )
    assert response.status_code == 429


@pytest.mark.parametrize("same_key", [True, False])
def test_concurrent_first_report_has_one_reservation(runtime, same_key):
    from concurrent.futures import ThreadPoolExecutor

    client, engine, _ = runtime
    headers, _, _ = account(client)
    profile(client, headers)
    with ThreadPoolExecutor(max_workers=2) as pool:
        responses = list(
            pool.map(
                lambda key: submit(client, headers, key=key), ["one", "one" if same_key else "two"]
            )
        )
    assert sorted(r.status_code for r in responses) == ([202, 202] if same_key else [202, 409]), [
        r.text for r in responses
    ]
    if same_key:
        assert responses[0].json() == responses[1].json()
    with Session(engine) as session:
        assert (
            session.scalar(
                select(func.count())
                .select_from(EntitlementReservation)
                .where(EntitlementReservation.state == "reserved")
            )
            == 1
        )
        assert session.scalar(select(func.count()).select_from(ProfileSnapshot)) == 1


def test_sql_quota_and_snapshot_ownership_cannot_be_forged(runtime):
    client, engine, _ = runtime
    owner, state, _ = account(client)
    profile(client, owner)
    other, other_state, _ = account(client)
    profile(client, other)
    accepted, report = complete_report(runtime, owner)
    with Session(engine) as session:
        reservation = session.scalar(select(EntitlementReservation))
        reservation_id = reservation.id
        row = session.get(UserReportVersion, UUID(report["report_version_id"]))
        values = {
            column.name: getattr(row, column.name) for column in UserReportVersion.__table__.columns
        }
    with engine.begin() as connection:
        with pytest.raises(DatabaseError):
            connection.execute(
                update(EntitlementReservation)
                .where(EntitlementReservation.id == reservation_id)
                .values(state="released")
            )
    values.update(id=uuid4(), version_num=2, user_id=UUID(other_state["identity"]["user_id"]))
    with engine.begin() as connection:
        with pytest.raises(DatabaseError):
            connection.execute(UserReportVersion.__table__.insert().values(**values))
    with engine.begin() as connection:
        with pytest.raises(DatabaseError):
            connection.execute(
                UsageLedger.__table__.insert().values(
                    id=uuid4(),
                    user_id=UUID(state["identity"]["user_id"]),
                    job_id=UUID(accepted["job_id"]),
                    reservation_id=reservation_id,
                    entry_kind="consumed",
                    units_delta=0,
                )
            )


def test_missing_encryption_key_does_not_silently_replace_private_data(runtime):
    from pathlib import Path

    client, _, config = runtime
    headers, _, _ = account(client)
    profile(client, headers, occupation_text="Private original")
    key = Path(config.profile_key_path)
    original = key.read_bytes()
    key.unlink()
    response = client.get("/api/v1/me/profile", headers=headers)
    assert response.status_code == 503 and response.json()["code"] == "PRIVATE_KEY_UNAVAILABLE"
    assert not key.exists()
    key.write_bytes(original)
    key.chmod(0o600)
    assert (
        client.get("/api/v1/me/profile", headers=headers).json()["profile"]["occupation_text"]
        == "Private original"
    )
