from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4

import pytest
from prediction_engine.contracts.models import SourceImportV1
from sqlalchemy import func, select, text
from sqlalchemy.exc import DatabaseError
from sqlalchemy.orm import Session

from infra.db import SourceVersion
from infra.evidence_repository import EvidenceRepository
from scripts.seed_demo import ADMIN_ID
from tests.conftest import ADMIN_HEADERS, USER_HEADERS

BASE = "/api/v1/admin"


def source_payload(
    url="https://example.invalid/original",
    *,
    content=None,
    available="2020-08-10T00:00:00Z",
    label="DEMO",
):
    content = (
        content or "DEMO：2020年7月软件岗位招聘指标为1200。技术工具可靠性改善，但采用受成本约束。"
    )
    return {
        "url": url,
        "title": "DEMO 合成来源",
        "publisher": "Synthetic Fixture",
        "source_type": "manual",
        "published_at": available,
        "available_at": available,
        "availability_basis": "verified_archive",
        "availability_note": "DEMO archive snapshot fixture",
        "content": content,
        "usage_permission": "authorized_full",
        "license_note": "Synthetic fixture authored for tests",
        "reliability_note": "DEMO only; no real forecasting evidence",
        "domain_tags": ["workforce", "technology"],
        "label": label,
        "claims": [
            {
                "claim_text": content,
                "quote": content,
                "source_locator": "paragraph 1",
                "relation": "supports",
                "claim_kind": "fact",
                "verification_status": "verified",
                "verification_note": "Synthetic expected fact checked against fixture",
                "scope": "DEMO region",
            }
        ],
    }


def ingest(client, payload=None):
    response = client.post(
        BASE + "/sources/ingest", headers=ADMIN_HEADERS, json=payload or source_payload()
    )
    assert response.status_code == 200, response.text
    return response.json()


def test_ingest_dedup_and_signal_candidate(runtime):
    client, engine, _ = runtime
    first = ingest(client)
    replay = ingest(client)
    assert first["version"]["source_version_id"] == replay["version"]["source_version_id"]
    assert replay["duplicate"]
    signals = client.get(BASE + "/signals", headers=ADMIN_HEADERS).json()
    assert len(signals) == 1
    assert signals[0]["kind"] == "signal" and signals[0]["status"] == "candidate"
    assert signals[0]["lifecycle_stage"] == "unknown"
    assert signals[0]["independent_source_count"] == 1
    assert (
        client.get(
            BASE + "/evidence", headers=ADMIN_HEADERS, params={"as_of": "2020-08-01T00:00:00Z"}
        ).json()
        == []
    )
    assert (
        len(
            client.get(
                BASE + "/evidence", headers=ADMIN_HEADERS, params={"as_of": "2020-08-11T00:00:00Z"}
            ).json()
        )
        == 1
    )
    with Session(engine) as session:
        assert session.scalar(select(func.count()).select_from(SourceVersion)) == 1


def test_reprints_not_independent_and_url_tracking(runtime):
    client, _, _ = runtime
    first = ingest(client)
    copied = [first] + [
        ingest(client, source_payload(f"https://example.invalid/reprint-{i}")) for i in range(2)
    ]
    assert len({item["version"]["source_group_id"] for item in copied}) == 1
    response = client.post(
        BASE + "/signals",
        headers=ADMIN_HEADERS,
        json={
            "headline": "DEMO combined",
            "claim_ids": [item["claim_ids"][0] for item in copied],
            "domain_tags": ["technology"],
        },
    )
    assert response.status_code == 200, response.text
    assert response.json()["independent_source_count"] == 1
    changed = source_payload("https://example.invalid/original?utm_source=test#fragment")
    assert ingest(client, changed)["version"]["source_id"] == first["version"]["source_id"]


def test_source_revisions_append_and_cannot_mutate(runtime):
    client, engine, _ = runtime
    old = ingest(client)
    new = ingest(
        client,
        source_payload(
            content="DEMO：指标修订为1120，岗位变化仍需观察。", available="2020-09-01T00:00:00Z"
        ),
    )
    assert new["version"]["source_id"] == old["version"]["source_id"]
    assert new["version"]["source_version_id"] != old["version"]["source_version_id"]
    early = client.get(
        BASE + "/sources", headers=ADMIN_HEADERS, params={"as_of": "2020-08-20T00:00:00Z"}
    ).json()
    assert [row["source_version_id"] for row in early] == [old["version"]["source_version_id"]]
    with engine.begin() as connection:
        with pytest.raises(DatabaseError):
            connection.execute(text("UPDATE source_versions SET title='tampered'"))
    with engine.begin() as connection:
        with pytest.raises(DatabaseError):
            connection.execute(text("DELETE FROM source_versions"))


def test_observed_now_is_not_historical_snapshot(runtime):
    client, _, _ = runtime
    payload = source_payload()
    payload.update(
        availability_basis="observed_now",
        available_at=None,
        claims=[],
        published_at="2020-01-01T00:00:00Z",
    )
    row = ingest(client, payload)["version"]
    assert row["available_at"] != payload["published_at"]
    assert (
        client.get(
            BASE + "/sources", headers=ADMIN_HEADERS, params={"as_of": "2020-12-31T00:00:00Z"}
        ).json()
        == []
    )


def test_unknown_time_stays_out_of_evidence_and_signals(runtime):
    client, _, _ = runtime
    payload = source_payload()
    payload.update(availability_basis="unknown", available_at=None, published_at=None)
    rejected = client.post(BASE + "/sources/ingest", headers=ADMIN_HEADERS, json=payload)
    assert rejected.status_code == 422 and rejected.json()["code"] == "SOURCE_AVAILABILITY_UNKNOWN"
    payload["claims"][0].update(verification_status="unverified", verification_note="")
    row = ingest(client, payload)
    assert row["version"]["available_at"] is None
    assert client.get(BASE + "/signals", headers=ADMIN_HEADERS).json() == []


def indicator_and_sources(client):
    first = ingest(client)
    second = ingest(
        client,
        source_payload(content="DEMO：修订招聘指标为1120。", available="2020-09-01T00:00:00Z"),
    )
    response = client.post(
        BASE + "/indicators",
        headers=ADMIN_HEADERS,
        json={
            "code": "demo_jobs",
            "name": "DEMO Jobs",
            "provider": "synthetic",
            "geo_scope": "demo",
            "unit": "postings",
            "frequency": "month",
            "definition_version": "v1",
            "label": "DEMO",
        },
    )
    assert response.status_code == 200, response.text
    indicator_id = response.json()["indicator_id"]

    def observation(source, value, date, revision):
        return {
            "source_version_id": source["version"]["source_version_id"],
            "period_start": "2020-07-01T00:00:00Z",
            "period_end": "2020-07-31T00:00:00Z",
            "value": value,
            "published_at": date,
            "available_at": date,
            "revision_number": revision,
            "quality_flag": "DEMO_DATA",
            "definition_note": "synthetic monthly fixture",
        }

    return (
        indicator_id,
        observation(first, 1200, "2020-08-10T00:00:00Z", 1),
        observation(second, 1120, "2020-09-01T00:00:00Z", 2),
    )


def test_indicator_revisions_do_not_change_old_asof(runtime):
    client, engine, _ = runtime
    identifier, v1, v2 = indicator_and_sources(client)
    path = f"{BASE}/indicators/{identifier}"
    assert client.post(path + "/observations", headers=ADMIN_HEADERS, json=v1).status_code == 200
    early = client.get(
        path + "/series", headers=ADMIN_HEADERS, params={"as_of": "2020-08-20T00:00:00Z"}
    ).json()
    assert early[0]["value"] == 1200
    assert client.post(path + "/observations", headers=ADMIN_HEADERS, json=v2).status_code == 200
    assert (
        client.get(
            path + "/series", headers=ADMIN_HEADERS, params={"as_of": "2020-08-20T00:00:00Z"}
        ).json()
        == early
    )
    assert (
        client.get(
            path + "/series", headers=ADMIN_HEADERS, params={"as_of": "2020-09-02T00:00:00Z"}
        ).json()[0]["value"]
        == 1120
    )
    assert (
        client.get(
            path + "/series", headers=ADMIN_HEADERS, params={"as_of": "2020-08-09T00:00:00Z"}
        ).json()
        == []
    )
    assert (
        client.post(
            path + "/observations", headers=ADMIN_HEADERS, json={**v1, "value": 999}
        ).status_code
        == 409
    )
    with engine.begin() as connection:
        with pytest.raises(DatabaseError):
            connection.execute(text("UPDATE indicator_observation_vintages SET value=999"))


def test_missing_source_and_future_source_are_explained(runtime):
    client, _, _ = runtime
    identifier, v1, v2 = indicator_and_sources(client)
    response = client.post(
        f"{BASE}/indicators/{identifier}/observations",
        headers=ADMIN_HEADERS,
        json={**v1, "source_version_id": str(uuid4())},
    )
    assert response.status_code == 404 and response.json()["code"] == "SOURCE_NOT_FOUND"
    response = client.post(
        f"{BASE}/indicators/{identifier}/observations",
        headers=ADMIN_HEADERS,
        json={**v1, "source_version_id": v2["source_version_id"]},
    )
    assert (
        response.status_code == 422
        and response.json()["code"] == "OBSERVATION_SOURCE_NOT_AVAILABLE"
    )


@pytest.mark.parametrize("category", ["success", "failure"])
def test_historical_outcomes_do_not_leak(runtime, category):
    client, _, _ = runtime
    before = ingest(client)
    after = ingest(
        client,
        source_payload(
            f"https://example.invalid/outcome-{category}",
            content=f"DEMO outcome {category}",
            available="2021-01-01T00:00:00Z",
        ),
    )
    body = {
        "title": "DEMO neutral historical case",
        "cutoff_at": "2020-08-20T00:00:00Z",
        "domain_tags": ["technology"],
        "mechanism_tags": ["adoption"],
        "initial_conditions": "DEMO early pilot",
        "limitations": ["Synthetic case, not retrospective forecasting proof"],
        "label": "DEMO",
        "events": [
            {
                "text": "Pilot announced",
                "known_at": "2020-08-10T00:00:00Z",
                "source_version_id": before["version"]["source_version_id"],
                "data_role": "contemporaneous",
            },
            {
                "text": f"Retrospective result {category}",
                "known_at": "2021-01-01T00:00:00Z",
                "source_version_id": after["version"]["source_version_id"],
                "data_role": "outcome",
                "outcome_category": category,
            },
        ],
    }
    response = client.post(BASE + "/historical-cases", headers=ADMIN_HEADERS, json=body)
    assert response.status_code == 200, response.text
    path = BASE + "/historical-cases/" + response.json()["case_id"]
    early = client.get(path, headers=ADMIN_HEADERS, params={"as_of": body["cutoff_at"]}).json()
    assert early["outcomes"] == [] and len(early["contemporaneous"]) == 1
    assert category not in str(early)
    late = client.get(path, headers=ADMIN_HEADERS, params={"as_of": "2021-01-02T00:00:00Z"}).json()
    assert late["outcomes"][0]["outcome_category"] == category


def test_bad_quote_or_missing_time_proof_does_not_persist(runtime):
    client, engine, _ = runtime
    payload = source_payload()
    payload["claims"][0]["quote"] = "invented quote"
    assert (
        client.post(BASE + "/sources/ingest", headers=ADMIN_HEADERS, json=payload).json()["code"]
        == "CLAIM_QUOTE_NOT_FOUND"
    )
    payload = source_payload()
    payload["availability_note"] = ""
    assert (
        client.post(BASE + "/sources/ingest", headers=ADMIN_HEADERS, json=payload).status_code
        == 422
    )
    with Session(engine) as session:
        assert session.scalar(select(func.count()).select_from(SourceVersion)) == 0


def test_demo_real_data_isolation(runtime):
    client, _, _ = runtime
    demo = ingest(client)
    real = ingest(client, source_payload(label="REAL"))
    assert demo["version"]["source_group_id"] != real["version"]["source_group_id"]
    response = client.post(
        BASE + "/signals",
        headers=ADMIN_HEADERS,
        json={
            "headline": "mixed",
            "claim_ids": [demo["claim_ids"][0], real["claim_ids"][0]],
            "domain_tags": ["technology"],
        },
    )
    assert response.status_code == 422 and response.json()["code"] == "DATASET_LABEL_MISMATCH"


@pytest.mark.parametrize("path", ["/sources", "/signals", "/indicators", "/historical-cases"])
def test_m1_admin_data_is_protected(runtime, path):
    client, _, _ = runtime
    assert client.get(BASE + path).status_code == 401
    assert client.get(BASE + path, headers=USER_HEADERS).status_code == 403


def test_live_web_is_explicit_and_off_during_tests(runtime):
    client, _, _ = runtime
    response = client.post(BASE + "/sources/search", headers=ADMIN_HEADERS, json={"query": "test"})
    assert response.status_code == 503 and response.json()["code"] == "LIVE_WEB_DISABLED"
    assert (
        client.post(
            BASE + "/sources/fetch", headers=USER_HEADERS, json={"url": "https://example.org"}
        ).status_code
        == 403
    )


def test_concurrent_source_import_is_idempotent(runtime):
    _, engine, _ = runtime
    data = SourceImportV1.model_validate(source_payload())

    def submit(_):
        with Session(engine) as session:
            return EvidenceRepository(session).ingest(data, ADMIN_ID).version.source_version_id

    with ThreadPoolExecutor(max_workers=4) as pool:
        identifiers = list(pool.map(submit, range(4)))
    assert len(set(identifiers)) == 1
    with Session(engine) as session:
        assert session.scalar(select(func.count()).select_from(SourceVersion)) == 1


def test_live_calls_have_budget_audit_and_no_key_leak(runtime, monkeypatch):
    import httpx
    from fastapi.testclient import TestClient
    from pydantic import SecretStr

    from apps.api.main import create_app
    from infra.providers.deepseek import DeepSeekWebProvider

    _, _, config = runtime
    calls = []

    def transport(request):
        calls.append(request)
        return httpx.Response(200, json={"results": []})

    def factory(key, **kwargs):
        return DeepSeekWebProvider(key, transport=httpx.MockTransport(transport), **kwargs)

    monkeypatch.setattr("apps.api.evidence.DeepSeekWebProvider", factory)
    app = create_app(
        config.model_copy(
            update={
                "live_web_enabled": True,
                "deepseek_api_key": SecretStr("fake-m1-key-never-real"),
            }
        )
    )
    with TestClient(app) as client:
        for _ in range(5):
            assert (
                client.post(
                    BASE + "/sources/search", headers=ADMIN_HEADERS, json={"query": "synthetic"}
                ).status_code
                == 200
            )
        limited = client.post(
            BASE + "/sources/search", headers=ADMIN_HEADERS, json={"query": "synthetic"}
        )
        assert limited.status_code == 429
        assert len(calls) == 5
        audit = client.get(BASE + "/web-access", headers=ADMIN_HEADERS)
        assert len(audit.json()) == 5
        assert all(
            row["status"] == "no_results" and row["http_attempts"] == 1 for row in audit.json()
        )
        assert "fake-m1-key" not in audit.text
    app.state.engine.dispose()


def test_invalid_source_url_is_an_explainable_validation_error(runtime):
    client, _, _ = runtime
    response = client.post(
        BASE + "/sources/ingest",
        headers=ADMIN_HEADERS,
        json=source_payload("https://example.org:invalid/"),
    )
    assert response.status_code == 422
    assert response.json()["code"] == "SOURCE_URL_INVALID"
