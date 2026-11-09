import logging
from uuid import uuid4

import pytest
from pydantic import ValidationError

from infra.settings import Settings
from tests.conftest import ADMIN_HEADERS, OTHER_HEADERS, USER_HEADERS


def test_auth_and_rbac(runtime):
    client, _, _ = runtime
    assert client.get("/api/v1/me").status_code == 401
    assert client.get("/api/v1/me", headers={"Authorization": "Bearer bogus"}).status_code == 401
    assert client.get("/api/v1/admin/overview", headers=USER_HEADERS).status_code == 403
    assert client.get("/api/v1/admin/overview", headers=ADMIN_HEADERS).status_code == 200
    forged = client.get("/api/v1/admin/overview", headers={**USER_HEADERS, "X-Role": "admin"})
    assert forged.status_code == 403


def test_private_job_ownership(runtime):
    client, _, _ = runtime
    accepted = client.post(
        "/api/v1/demo/research",
        headers={**USER_HEADERS, "Idempotency-Key": "private"},
        json={"question": "private DEMO question"},
    )
    job_id = accepted.json()["job_id"]
    response = client.get(f"/api/v1/jobs/{job_id}", headers=OTHER_HEADERS)
    missing = client.get(f"/api/v1/jobs/{uuid4()}", headers=OTHER_HEADERS)
    assert response.status_code == missing.status_code == 404
    assert set(response.json()) == set(missing.json())
    assert "private DEMO" not in response.text
    # Even admin has no implicit access to another user's private job payload/result.
    assert client.get(f"/api/v1/jobs/{job_id}", headers=ADMIN_HEADERS).status_code == 404


@pytest.mark.parametrize("path", ["/api/v1/jobs/not-a-uuid", "/does-not-exist"])
def test_public_error_shape(runtime, path):
    client, _, _ = runtime
    response = client.get(path, headers=USER_HEADERS)
    body = response.json()
    assert {"code", "message", "request_id", "details"} <= body.keys()
    assert body["request_id"] == response.headers["X-Request-ID"]
    assert "input" not in body


def test_validation_does_not_echo_sensitive_data(runtime, caplog):
    client, _, _ = runtime
    caplog.set_level(logging.INFO, logger="futureos.requests")
    response = client.post(
        "/api/v1/demo/research",
        headers={**USER_HEADERS, "Idempotency-Key": "private"},
        json={"question": "private-secret", "api_key": "sensitive-secret"},
    )
    assert response.status_code == 422
    assert "sensitive-secret" not in response.text
    assert "private-secret" not in caplog.text
    assert "demo-user-local-only" not in caplog.text


@pytest.mark.parametrize(
    "values",
    [{"demo_mode": False}, {"app_env": "production"}, {"demo_admin_token": "demo-user-local-only"}],
)
def test_m0_cannot_enable_production(values):
    with pytest.raises(ValidationError):
        Settings(_env_file=None, **values)
