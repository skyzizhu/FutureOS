import json
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from uuid import UUID

import httpx
import pyotp
import pytest
from pydantic import SecretStr
from sqlalchemy import func, select, text
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.orm import Session

from infra.accounts import token_hash, vault_for
from infra.admin_security import AdminSecurity
from infra.db import (
    AdminMFA,
    AuthAccount,
    AuthAudit,
    AuthEmailCode,
    utcnow,
)
from infra.evidence_repository import EvidenceError
from tests.integration.test_m4_reports import PASSWORD, account, registration_data


def owner(runtime):
    client, engine, config = runtime
    with Session(engine) as session:
        token = AdminSecurity(session, config).bootstrap_token()
    bootstrap = client.post(
        "/api/v1/admin-auth/bootstrap",
        json={"email": "owner@example.invalid", "password": PASSWORD, "bootstrap_token": token},
    )
    assert bootstrap.status_code == 200, bootstrap.text
    challenge = bootstrap.json()
    assert challenge["stage"] == "enroll" and "access_token" not in challenge
    result = client.post(
        "/api/v1/admin-auth/enroll",
        json={
            "challenge_token": challenge["challenge_token"],
            "code": pyotp.TOTP(challenge["secret"]).now(),
        },
    )
    assert result.status_code == 200, result.text
    data = result.json()
    return {"Authorization": "Bearer " + data["access_token"]}, data, challenge


def email_proof(runtime, email, purpose="password_reset"):
    client, engine, config = runtime
    sent = client.post("/api/v1/auth/email-code", json={"email": email, "purpose": purpose})
    assert sent.status_code == 200, sent.text
    with Session(engine) as session:
        row = session.get(AuthEmailCode, UUID(sent.json()["challenge_id"]))
        code = (
            vault_for(session, config).open(row.code_ciphertext, "auth-code:" + str(row.id))["code"]
            if row.code_ciphertext
            else None
        )
    return sent.json()["challenge_id"], code


def test_registration_requires_four_digit_proof_before_account_exists(runtime):
    client, engine, _ = runtime
    email = "new@example.invalid"
    assert (
        client.post(
            "/api/v1/auth/register", json={"email": email, "password": PASSWORD}
        ).status_code
        == 422
    )
    proof = registration_data(client, email)
    assert len(proof["code"]) == 4 and proof["code"].isdigit()
    with Session(engine) as session:
        assert session.scalar(select(func.count()).select_from(AuthAccount)) == 0
        row = session.get(AuthEmailCode, UUID(proof["verification_id"]))
        assert row.code_digest != proof["code"] and proof["code"] not in row.code_ciphertext
    response = client.post(
        "/api/v1/auth/register", json={"email": email, "password": PASSWORD, **proof}
    )
    assert response.status_code == 201 and response.json()["identity"]["email_verified"] is True
    assert (
        client.post(
            "/api/v1/auth/register", json={"email": email, "password": PASSWORD, **proof}
        ).status_code
        == 401
    )


def test_email_proof_is_bound_to_address_purpose_and_five_attempts(runtime):
    client, engine, _ = runtime
    proof = registration_data(client, "bound@example.invalid")
    assert (
        client.post(
            "/api/v1/auth/register",
            json={"email": "other@example.invalid", "password": PASSWORD, **proof},
        ).status_code
        == 401
    )
    assert (
        client.post(
            "/api/v1/auth/password-reset",
            json={"email": "bound@example.invalid", "password": PASSWORD, **proof},
        ).status_code
        == 401
    )
    wrong = "9999" if proof["code"] != "9999" else "0000"
    for _ in range(5):
        assert (
            client.post(
                "/api/v1/auth/register",
                json={
                    "email": "bound@example.invalid",
                    "password": PASSWORD,
                    **proof,
                    "code": wrong,
                },
            ).status_code
            == 401
        )
    assert (
        client.post(
            "/api/v1/auth/register",
            json={"email": "bound@example.invalid", "password": PASSWORD, **proof},
        ).status_code
        == 401
    )
    with Session(engine) as session:
        assert session.get(AuthEmailCode, UUID(proof["verification_id"])).attempts == 5


def test_expired_email_proof_and_resend_replace_old_code(runtime):
    client, engine, _ = runtime
    email = "expiry@example.invalid"
    proof = registration_data(client, email)
    resend = client.post("/api/v1/auth/email-code", json={"email": email, "purpose": "register"})
    assert resend.status_code == 429 and int(resend.headers["Retry-After"]) > 0
    with Session(engine) as session:
        row = session.get(AuthEmailCode, UUID(proof["verification_id"]))
        row.created_at = utcnow() - timedelta(seconds=61)
        session.commit()
    new = registration_data(client, email)
    assert (
        client.post(
            "/api/v1/auth/register", json={"email": email, "password": PASSWORD, **proof}
        ).status_code
        == 401
    )
    with Session(engine) as session:
        row = session.get(AuthEmailCode, UUID(new["verification_id"]))
        row.expires_at = utcnow() - timedelta(seconds=1)
        session.commit()
    assert (
        client.post(
            "/api/v1/auth/register", json={"email": email, "password": PASSWORD, **new}
        ).status_code
        == 401
    )


def test_password_change_consumes_code_and_revokes_all_sessions(runtime):
    client, _, _ = runtime
    headers, state, email = account(client)
    second = client.post("/api/v1/auth/login", json={"email": email, "password": PASSWORD}).json()
    proof, code = email_proof(runtime, email)
    response = client.post(
        "/api/v1/auth/password-reset",
        json={
            "email": email,
            "password": "New-password-for-test-123!",
            "verification_id": proof,
            "code": code,
        },
    )
    assert response.status_code == 200, response.text
    for token in [state["access_token"], second["access_token"]]:
        assert (
            client.get(
                "/api/v1/me/sessions", headers={"Authorization": "Bearer " + token}
            ).status_code
            == 401
        )
    assert (
        client.post("/api/v1/auth/login", json={"email": email, "password": PASSWORD}).status_code
        == 401
    )
    assert (
        client.post(
            "/api/v1/auth/login", json={"email": email, "password": "New-password-for-test-123!"}
        ).status_code
        == 200
    )
    assert (
        client.post(
            "/api/v1/auth/password-reset",
            json={"email": email, "password": PASSWORD, "verification_id": proof, "code": code},
        ).status_code
        == 401
    )


def test_unknown_password_reset_does_not_disclose_account_or_create_preview(runtime):
    client, engine, _ = runtime
    _, _, email = account(client)
    known = client.post(
        "/api/v1/auth/email-code", json={"email": email, "purpose": "password_reset"}
    )
    missing = client.post(
        "/api/v1/auth/email-code",
        json={"email": "missing@example.invalid", "purpose": "password_reset"},
    )
    assert known.status_code == missing.status_code == 200
    assert set(known.json()) == set(missing.json())
    with Session(engine) as session:
        row = session.get(AuthEmailCode, UUID(missing.json()["challenge_id"]))
        assert row.code_ciphertext is None and row.delivery_status == "suppressed"


def test_sessions_ownership_and_password_confirmed_revoke_all(runtime):
    client, _, _ = runtime
    headers, state, email = account(client)
    other, _, _ = account(client)
    second = client.post("/api/v1/auth/login", json={"email": email, "password": PASSWORD}).json()
    sessions = client.get("/api/v1/me/sessions", headers=headers).json()
    assert len(sessions) == 2 and sum(row["current"] for row in sessions) == 1
    assert "token_hash" not in json.dumps(sessions) and state["access_token"] not in json.dumps(
        sessions
    )
    sid = sessions[0]["session_id"]
    assert client.delete("/api/v1/me/sessions/" + sid, headers=other).status_code == 404
    assert (
        client.post(
            "/api/v1/me/sessions/revoke-all",
            headers=headers,
            json={"password": "wrong-password-123!"},
        ).status_code
        == 401
    )
    assert (
        client.post(
            "/api/v1/me/sessions/revoke-all", headers=headers, json={"password": PASSWORD}
        ).status_code
        == 200
    )
    assert (
        client.get(
            "/api/v1/me/profile", headers={"Authorization": "Bearer " + second["access_token"]}
        ).status_code
        == 401
    )


def test_bootstrap_is_one_time_and_password_alone_has_no_admin_session(runtime):
    client, engine, config = runtime
    headers, state, _ = owner(runtime)
    assert len(state["recovery_codes"]) == 10
    assert client.get("/api/v1/admin/security/admins", headers=headers).status_code == 200
    with Session(engine) as session, pytest.raises(EvidenceError, match="BOOTSTRAP_CLOSED"):
        AdminSecurity(session, config).bootstrap_token()
    assert (
        client.post(
            "/api/v1/auth/login", json={"email": "owner@example.invalid", "password": PASSWORD}
        ).status_code
        == 401
    )
    challenge = client.post(
        "/api/v1/admin-auth/login", json={"email": "owner@example.invalid", "password": PASSWORD}
    ).json()
    assert (
        challenge["stage"] == "verify"
        and challenge["secret"] is None
        and "access_token" not in challenge
    )
    assert (
        client.get(
            "/api/v1/admin/overview",
            headers={"Authorization": "Bearer " + challenge["challenge_token"]},
        ).status_code
        == 401
    )
    assert (
        client.post(
            "/api/v1/admin-auth/enroll",
            json={"challenge_token": challenge["challenge_token"], "code": "123456"},
        ).status_code
        == 401
    )


def test_admin_mfa_encrypted_replay_rejected_and_challenge_capped(runtime):
    client, engine, _ = runtime
    _, state, binding = owner(runtime)
    login = client.post(
        "/api/v1/admin-auth/login", json={"email": "owner@example.invalid", "password": PASSWORD}
    ).json()
    code = pyotp.TOTP(binding["secret"]).now()
    assert (
        client.post(
            "/api/v1/admin-auth/verify",
            json={"challenge_token": login["challenge_token"], "code": code},
        ).status_code
        == 401
    )
    for _ in range(4):
        assert (
            client.post(
                "/api/v1/admin-auth/verify",
                json={"challenge_token": login["challenge_token"], "code": "not-a-real-code"},
            ).status_code
            == 401
        )
    assert (
        client.post(
            "/api/v1/admin-auth/verify",
            json={
                "challenge_token": login["challenge_token"],
                "code": pyotp.TOTP(binding["secret"]).at(utcnow().timestamp() + 30),
            },
        ).status_code
        == 401
    )
    with Session(engine) as session:
        factor = session.get(AdminMFA, UUID(state["identity"]["user_id"]))
        assert binding["secret"] not in factor.secret_ciphertext
        assert not any(c in json.dumps(factor.recovery_hashes) for c in state["recovery_codes"])


def test_same_totp_concurrently_cannot_issue_two_admin_sessions(runtime):
    client, _, _ = runtime
    _, _, binding = owner(runtime)
    challenges = [
        client.post(
            "/api/v1/admin-auth/login",
            json={"email": "owner@example.invalid", "password": PASSWORD},
        ).json()["challenge_token"]
        for _ in range(2)
    ]
    code = pyotp.TOTP(binding["secret"]).at(utcnow().timestamp() + 30)
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(
            pool.map(
                lambda token: (
                    client.post(
                        "/api/v1/admin-auth/verify", json={"challenge_token": token, "code": code}
                    ).status_code
                ),
                challenges,
            )
        )
    assert sorted(results) == [200, 401]


def test_recovery_code_revokes_sessions_and_requires_reenrollment(runtime):
    client, _, _ = runtime
    headers, state, _ = owner(runtime)
    challenge = client.post(
        "/api/v1/admin-auth/login", json={"email": "owner@example.invalid", "password": PASSWORD}
    ).json()
    recovered = client.post(
        "/api/v1/admin-auth/verify",
        json={"challenge_token": challenge["challenge_token"], "code": state["recovery_codes"][0]},
    )
    assert recovered.status_code == 200, recovered.text
    assert recovered.json()["stage"] == "enroll" and "access_token" not in recovered.json()
    assert client.get("/api/v1/admin/overview", headers=headers).status_code == 401
    assert (
        client.post(
            "/api/v1/admin-auth/verify",
            json={
                "challenge_token": challenge["challenge_token"],
                "code": state["recovery_codes"][0],
            },
        ).status_code
        == 401
    )
    binding = recovered.json()
    new = client.post(
        "/api/v1/admin-auth/enroll",
        json={
            "challenge_token": binding["challenge_token"],
            "code": pyotp.TOTP(binding["secret"]).now(),
        },
    )
    assert new.status_code == 200 and len(new.json()["recovery_codes"]) == 10


def test_permissions_last_owner_and_disabled_sessions(runtime):
    client, engine, _ = runtime
    headers, state, _ = owner(runtime)
    uid = state["identity"]["user_id"]
    assert (
        client.put(
            "/api/v1/admin/security/admins/" + uid,
            headers=headers,
            json={"permission_group": "viewer", "enabled": True},
        ).status_code
        == 409
    )
    assert (
        client.put(
            "/api/v1/admin/security/admins/" + uid,
            headers=headers,
            json={"permission_group": "owner", "enabled": False},
        ).status_code
        == 409
    )
    created = client.post(
        "/api/v1/admin/security/admins",
        headers=headers,
        json={
            "email": "viewer@example.invalid",
            "password": PASSWORD,
            "permission_group": "viewer",
        },
    )
    assert created.status_code == 201, created.text
    viewer_id = created.json()["user_id"]
    binding = client.post(
        "/api/v1/admin-auth/login", json={"email": "viewer@example.invalid", "password": PASSWORD}
    ).json()
    state = client.post(
        "/api/v1/admin-auth/enroll",
        json={
            "challenge_token": binding["challenge_token"],
            "code": pyotp.TOTP(binding["secret"]).now(),
        },
    ).json()
    viewer = {"Authorization": "Bearer " + state["access_token"]}
    assert client.get("/api/v1/admin/readiness", headers=viewer).status_code == 200
    assert client.get("/api/v1/admin/security/admins", headers=viewer).status_code == 403
    assert client.post("/api/v1/admin/research/demo-inputs", headers=viewer).status_code == 403
    assert (
        client.post(
            "/api/v1/admin-auth/recovery-codes",
            headers=viewer,
            json={"code": pyotp.TOTP(binding["secret"]).at(utcnow().timestamp() + 30)},
        ).status_code
        == 200
    )
    assert (
        client.put(
            "/api/v1/admin/security/admins/" + viewer_id,
            headers=headers,
            json={"permission_group": "viewer", "enabled": False},
        ).status_code
        == 200
    )
    assert client.get("/api/v1/admin/readiness", headers=viewer).status_code == 401
    with Session(engine) as session:
        assert session.scalar(select(func.count()).select_from(AuthAudit)) > 0
        with pytest.raises((IntegrityError, DBAPIError)):
            session.execute(text("DELETE FROM auth_audits"))
            session.commit()


def test_admin_password_reset_preserves_second_factor_and_invalidates_pending_login(runtime):
    client, _, _ = runtime
    headers, _, _ = owner(runtime)
    pending = client.post(
        "/api/v1/admin-auth/login", json={"email": "owner@example.invalid", "password": PASSWORD}
    ).json()
    identifier, code = email_proof(runtime, "owner@example.invalid")
    assert (
        client.post(
            "/api/v1/auth/password-reset",
            json={
                "email": "owner@example.invalid",
                "password": "New-owner-password-123!",
                "verification_id": identifier,
                "code": code,
            },
        ).status_code
        == 200
    )
    assert client.get("/api/v1/admin/readiness", headers=headers).status_code == 401
    assert (
        client.post(
            "/api/v1/admin-auth/verify",
            json={"challenge_token": pending["challenge_token"], "code": "123456"},
        ).status_code
        == 401
    )
    state = client.post(
        "/api/v1/admin-auth/login",
        json={"email": "owner@example.invalid", "password": "New-owner-password-123!"},
    ).json()
    assert state["stage"] == "verify" and not state["secret"]


def test_demo_admin_disabled_by_default(runtime):
    client, _, config = runtime
    config.demo_admin_enabled = False
    assert (
        client.get(
            "/api/v1/admin/overview", headers={"Authorization": "Bearer " + config.demo_admin_token}
        ).status_code
        == 401
    )


def test_turnstile_server_verification_checks_action_host_and_duplicate(runtime, monkeypatch):
    client, _, config = runtime
    config.turnstile_enabled = True
    config.turnstile_site_key = "public-test-site"
    config.turnstile_secret_key = SecretStr("private-test-secret")
    calls = []
    answer = {
        "success": True,
        "hostname": "localhost",
        "action": "signup",
        "challenge_ts": utcnow().isoformat(),
    }
    original = httpx.Client

    def factory(**kwargs):
        assert kwargs["trust_env"] is False and kwargs["follow_redirects"] is False

        def transport(request):
            calls.append(request)
            assert str(request.url) == "https://challenges.cloudflare.com/turnstile/v0/siteverify"
            return httpx.Response(200, json=answer)

        return original(**kwargs, transport=httpx.MockTransport(transport))

    monkeypatch.setattr("infra.human_verification.httpx.Client", factory)
    missing = client.post(
        "/api/v1/auth/email-code", json={"email": "one@example.invalid", "purpose": "register"}
    )
    assert missing.status_code == 403 and not calls
    good = client.post(
        "/api/v1/auth/email-code",
        json={"email": "one@example.invalid", "purpose": "register", "human_token": "once-only"},
    )
    assert good.status_code == 200, good.text
    assert (
        client.post(
            "/api/v1/auth/email-code",
            json={
                "email": "two@example.invalid",
                "purpose": "register",
                "human_token": "once-only",
            },
        ).status_code
        == 403
    )
    answer["hostname"] = "evil.invalid"
    assert (
        client.post(
            "/api/v1/auth/email-code",
            json={
                "email": "three@example.invalid",
                "purpose": "register",
                "human_token": "new-token",
            },
        ).status_code
        == 403
    )
    answer["hostname"] = "localhost"
    answer["action"] = "wrong-action"
    assert (
        client.post(
            "/api/v1/auth/email-code",
            json={
                "email": "four@example.invalid",
                "purpose": "register",
                "human_token": "other-token",
            },
        ).status_code
        == 403
    )
    config_out = client.get("/api/v1/auth/config").text
    assert "private-test-secret" not in config_out and "public-test-site" in config_out


def test_four_digit_signup_concurrency_creates_one_account(runtime):
    client, engine, _ = runtime
    proof = registration_data(client, "concurrent@example.invalid")

    def register(_):
        return client.post(
            "/api/v1/auth/register",
            json={"email": "concurrent@example.invalid", "password": PASSWORD, **proof},
        ).status_code

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(register, range(2)))
    assert sorted(results) == [201, 401]
    with Session(engine) as session:
        assert session.scalar(select(func.count()).select_from(AuthAccount)) == 1


def test_login_challenge_after_three_failed_passwords(runtime, monkeypatch):
    client, _, config = runtime
    _, _, email = account(client)
    for _ in range(3):
        assert (
            client.post(
                "/api/v1/auth/login",
                json={"email": email, "password": "Bad-password-for-test-123!"},
            ).status_code
            == 401
        )
    config.turnstile_enabled = True
    config.turnstile_site_key = "public-test"
    config.turnstile_secret_key = SecretStr("private-test")

    def no_password_check(*args):
        raise AssertionError("KDF must not run before required human check")

    monkeypatch.setattr("infra.accounts.password_matches", no_password_check)
    response = client.post("/api/v1/auth/login", json={"email": email, "password": PASSWORD})
    assert response.status_code == 403 and response.json()["code"] == "HUMAN_VERIFICATION_REQUIRED"


def test_captcha_outage_fails_closed_without_issuing_email_code(runtime, monkeypatch):
    client, engine, config = runtime
    config.turnstile_enabled = True
    config.turnstile_site_key = "public-test"
    config.turnstile_secret_key = SecretStr("private-test")

    def unavailable(**kwargs):
        raise httpx.ConnectError("private-provider-detail")

    monkeypatch.setattr("infra.human_verification.httpx.Client", unavailable)
    response = client.post(
        "/api/v1/auth/email-code",
        json={
            "email": "blocked@example.invalid",
            "purpose": "register",
            "human_token": "some-token",
        },
    )
    assert response.status_code == 503 and "private-provider-detail" not in response.text
    with Session(engine) as session:
        assert session.scalar(select(func.count()).select_from(AuthEmailCode)) == 0


def test_smtp_code_requires_tls_and_never_stores_recoverable_live_code(runtime, monkeypatch):
    from unittest.mock import MagicMock

    client, engine, config = runtime
    config.auth_mail_transport = "smtp"
    config.smtp_port = 587  # Explicit STARTTLS fixture, independent of local .env.
    config.smtp_host = "smtp.example.invalid"
    config.smtp_username = "test-user"
    config.smtp_password = SecretStr("test-secret")
    smtp = MagicMock()
    smtp.__enter__.return_value = smtp
    monkeypatch.setattr("infra.account_security.smtplib.SMTP", lambda *args, **kwargs: smtp)
    sent = client.post(
        "/api/v1/auth/email-code",
        json={"email": "smtp-test@example.invalid", "purpose": "register"},
    )
    assert sent.status_code == 200, sent.text
    smtp.starttls.assert_called_once()
    smtp.login.assert_called_once()
    smtp.send_message.assert_called_once()
    with Session(engine) as session:
        row = session.get(AuthEmailCode, UUID(sent.json()["challenge_id"]))
        assert row.delivery_status == "sent" and row.code_ciphertext is None
    body = smtp.send_message.call_args.args[0].get_content()
    import re

    code = re.search(r"\b[0-9]{4}\b", body).group()
    result = client.post(
        "/api/v1/auth/register",
        json={
            "email": "smtp-test@example.invalid",
            "password": PASSWORD,
            "verification_id": sent.json()["challenge_id"],
            "code": code,
        },
    )
    assert result.status_code == 201, result.text


def test_stale_admin_factor_confirmation_required_for_sensitive_actions(runtime):
    client, engine, _ = runtime
    headers, state, _ = owner(runtime)
    with Session(engine) as session:
        from infra.db import AuthSession

        row = session.get(AuthSession, token_hash(state["access_token"]))
        row.mfa_verified_at = utcnow() - timedelta(minutes=6)
        session.commit()
    response = client.post(
        "/api/v1/admin/security/admins",
        headers=headers,
        json={
            "email": "blocked-admin@example.invalid",
            "password": PASSWORD,
            "permission_group": "viewer",
        },
    )
    assert response.status_code == 403 and response.json()["code"] == "MFA_STEP_UP_REQUIRED"


def test_backup_fingerprint_detects_admin_factor_change(runtime):
    from infra.backup import fingerprint

    client, engine, _ = runtime
    _, state, _ = owner(runtime)
    with engine.connect() as connection:
        before = fingerprint(connection)
    with Session(engine) as session:
        factor = session.get(AdminMFA, UUID(state["identity"]["user_id"]))
        factor.recovery_hashes = ["0" * 64]
        session.commit()
    with engine.connect() as connection:
        after = fingerprint(connection)
    assert before["counts"] == after["counts"]
    assert before["authentication_digest"] != after["authentication_digest"]


def test_resending_email_cannot_reset_daily_guess_budget(runtime):
    client, engine, _ = runtime
    email = "daily-budget@example.invalid"
    proof = registration_data(client, email)
    wrong = "9999" if proof["code"] != "9999" else "0000"
    for _ in range(5):
        assert (
            client.post(
                "/api/v1/auth/register",
                json={"email": email, "password": PASSWORD, **proof, "code": wrong},
            ).status_code
            == 401
        )
    with Session(engine) as session:
        row = session.get(AuthEmailCode, UUID(proof["verification_id"]))
        row.created_at = utcnow() - timedelta(seconds=61)
        session.commit()
    newer = registration_data(client, email)
    response = client.post(
        "/api/v1/auth/register", json={"email": email, "password": PASSWORD, **newer}
    )
    assert response.status_code == 429 and int(response.headers["Retry-After"]) == 86400
