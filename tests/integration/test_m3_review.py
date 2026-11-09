from uuid import UUID, uuid4

import pytest
from prediction_engine.contracts.models import SourceImportV1
from sqlalchemy import select, text
from sqlalchemy.exc import DatabaseError
from sqlalchemy.orm import Session

from infra.db import DraftRevision, ForecastVersion
from infra.evidence_repository import EvidenceRepository
from tests.conftest import ADMIN_HEADERS, USER_HEADERS
from tests.integration.test_m2_research import complete

BASE = "/api/v1/admin/review"


def check(client, draft_id):
    response = client.post(f"{BASE}/drafts/{draft_id}/check", headers=ADMIN_HEADERS, json={})
    assert response.status_code == 200, response.text
    return response.json()


def publish(client, draft_id, review_id):
    return client.post(
        f"{BASE}/drafts/{draft_id}/publish",
        headers=ADMIN_HEADERS,
        json={"review_id": review_id, "change_reason": "M3 test publication"},
    )


def add_counter(engine):
    from scripts.seed_demo import ADMIN_ID

    with Session(engine) as session:
        EvidenceRepository(session).ingest(
            SourceImportV1.model_validate(
                {
                    "url": "https://example.invalid/m3/new-counter",
                    "title": "DEMO archived counterfact",
                    "publisher": "Synthetic independent archive",
                    "source_type": "manual",
                    "published_at": "2020-05-20T00:00:00Z",
                    "available_at": "2020-05-20T00:00:00Z",
                    "availability_basis": "verified_archive",
                    "availability_note": "Owned synthetic late ingestion",
                    "content": (
                        "DEMO new counterfact: independent follow-up found "
                        "integration costs remain high."
                    ),
                    "usage_permission": "authorized_full",
                    "license_note": "Own synthetic fixture",
                    "reliability_note": "Synthetic test only",
                    "domain_tags": ["technology"],
                    "label": "DEMO",
                    "claims": [
                        {
                            "claim_text": "DEMO integration costs remain high",
                            "quote": "integration costs remain high",
                            "source_locator": "paragraph 1",
                            "relation": "contradicts",
                            "claim_kind": "fact",
                            "verification_status": "verified",
                            "verification_note": "Synthetic text checked",
                            "scope": "DEMO-lab",
                        }
                    ],
                }
            ),
            ADMIN_ID,
        )
        session.commit()


def test_review_publish_immutable_protocol_and_missing_result(runtime):
    client, engine, _ = runtime
    accepted, view = complete(runtime)
    draft_id = view["draft"]["draft_id"]
    review = check(client, draft_id)
    assert review["decision"]["decision"] == "annotate"
    assert review["report"]["model_calls"] == 0
    review_id = review["report"]["critic_run_id"]
    response = publish(client, draft_id, review_id)
    assert response.status_code == 200, response.text
    version = response.json()
    assert publish(client, draft_id, review_id).json() == version
    assert version["body"]["statement"] == view["draft"]["statement"]
    registration = {
        "mode": "synthetic",
        "operator": "gte",
        "threshold": 70,
        "unit": "completed_tasks_per_100_trials",
    }
    response = client.post(
        f"{BASE}/versions/{version['version_id']}/register",
        headers=ADMIN_HEADERS,
        json=registration,
    )
    assert response.status_code == 200, response.text
    protocol = response.json()
    assert protocol["baseline_value"] == 60 and protocol["point_prediction_a"] is None
    assert (
        client.post(
            f"{BASE}/versions/{version['version_id']}/register",
            headers=ADMIN_HEADERS,
            json={**registration, "threshold": 1},
        ).status_code
        == 409
    )
    assert (
        client.post(
            f"{BASE}/versions/{version['version_id']}/register",
            headers=ADMIN_HEADERS,
            json={**registration, "mode": "forward"},
        ).status_code
        == 409
    )
    response = client.post(
        f"{BASE}/protocols/{protocol['protocol_id']}/resolve",
        headers=ADMIN_HEADERS,
        json={"unavailable_reason": "No admissible observation"},
    )
    assert response.status_code == 200, response.text
    assert response.json()["status"] == "unresolved_due_to_data"
    board = client.get(BASE + "/scoreboard", headers=ADMIN_HEADERS).json()
    assert board["records"][0]["latest_resolution"]["status"] == "unresolved_due_to_data"
    assert len(board["records"][0]["resolution_history"]) == 2
    assert board["strata"][2]["count"] == 0 and board["real_accuracy_available"] is False
    assert (
        client.post(
            f"{BASE}/protocols/{protocol['protocol_id']}/resolve",
            headers=ADMIN_HEADERS,
            json={"value": 999},
        ).status_code
        == 422
    )
    assert client.get(BASE + "/drafts", headers=USER_HEADERS).status_code == 403
    assert (
        client.post(f"{BASE}/drafts/{draft_id}/check", headers=USER_HEADERS, json={}).status_code
        == 403
    )
    for table, assignment in [
        ("forecast_versions", "statement='tamper'"),
        ("critic_runs", "draft_hash='bad'"),
        ("adjudication_records", "decision='accept'"),
        ("evaluation_protocols", "mode='forward'"),
        ("forecast_resolutions", "status='confirmed'"),
    ]:
        with engine.begin() as conn:
            with pytest.raises(DatabaseError):
                conn.execute(text(f"UPDATE {table} SET {assignment}"))
    replay = client.post(
        "/api/v1/admin/research/runs/" + accepted["run_id"] + "/replay", headers=ADMIN_HEADERS
    )
    assert replay.status_code == 200 and replay.json()["identical"]


def test_new_counterevidence_revision_does_not_change_a(runtime):
    client, engine, _ = runtime
    accepted, view = complete(runtime)
    identifier = view["draft"]["draft_id"]
    add_counter(engine)
    review = check(client, identifier)
    assert review["decision"]["decision"] == "targeted_research"
    assert publish(client, identifier, review["report"]["critic_run_id"]).status_code == 409
    findings = [
        f["finding_id"]
        for f in review["report"]["findings"]
        if f["severity"] in {"L2", "L3"} and f["verification_status"] == "verified"
    ]
    data = {"review_id": review["report"]["critic_run_id"], "confirmed_finding_ids": findings}
    response = client.post(f"{BASE}/drafts/{identifier}/revise", headers=ADMIN_HEADERS, json=data)
    assert response.status_code == 200, response.text
    revision = response.json()
    assert revision["draft_sequence"] == "B1" and "contradiction_claim_ids" in revision["changes"]
    assert (
        client.post(f"{BASE}/drafts/{identifier}/revise", headers=ADMIN_HEADERS, json=data).json()
        == revision
    )
    revised_review = check(client, revision["draft_id"])
    assert revised_review["decision"]["publication_allowed"]
    assert (
        publish(client, revision["draft_id"], revised_review["report"]["critic_run_id"]).status_code
        == 200
    )
    original = client.get(
        "/api/v1/admin/research/runs/" + accepted["run_id"], headers=ADMIN_HEADERS
    ).json()
    assert original["draft"] == view["draft"] and original["draft_hash"] == view["draft_hash"]
    assert client.post(
        "/api/v1/admin/research/runs/" + accepted["run_id"] + "/replay", headers=ADMIN_HEADERS
    ).json()["identical"]
    with Session(engine) as session:
        assert session.scalar(select(DraftRevision)).parent_draft_id == UUID(identifier)
    for table, assignment in [
        ("draft_revisions", "changes='{}'"),
        ("forecast_drafts", "draft_sequence='A'"),
    ]:
        with engine.begin() as conn:
            with pytest.raises(DatabaseError):
                conn.execute(text(f"UPDATE {table} SET {assignment}"))


def test_approved_review_cannot_publish_other_draft_or_bypass_db(runtime):
    client, engine, _ = runtime
    _, view = complete(runtime, key="one")
    _, other = complete(runtime, key="two")
    review = check(client, view["draft"]["draft_id"])
    assert (
        publish(client, other["draft"]["draft_id"], review["report"]["critic_run_id"]).status_code
        == 409
    )
    response = publish(client, view["draft"]["draft_id"], review["report"]["critic_run_id"])
    assert response.status_code == 200, response.text
    with Session(engine) as session:
        row = session.get(ForecastVersion, UUID(response.json()["version_id"]))
        values = {c.name: getattr(row, c.name) for c in ForecastVersion.__table__.columns}
        values.update(
            id=uuid4(), version_num=2, draft_id=UUID(other["draft"]["draft_id"]), statement="forged"
        )
    with engine.begin() as conn:
        with pytest.raises(DatabaseError):
            conn.execute(ForecastVersion.__table__.insert().values(**values))
    with engine.begin() as conn:
        with pytest.raises(DatabaseError):
            conn.execute(text("UPDATE world_forecasts SET stable_target_key='forged'"))


def test_latest_review_prevents_using_old_approval(runtime):
    client, engine, _ = runtime
    _, view = complete(runtime)
    identifier = view["draft"]["draft_id"]
    old = check(client, identifier)
    add_counter(engine)
    latest = check(client, identifier)
    assert latest["decision"]["publication_allowed"] is False
    response = publish(client, identifier, old["report"]["critic_run_id"])
    assert response.status_code == 409 and response.json()["code"] == "STALE_REVIEW"


def test_unreviewed_and_hypothesis_never_publish(runtime):
    client, _, _ = runtime
    _, view = complete(runtime)
    assert publish(client, view["draft"]["draft_id"], str(uuid4())).status_code == 404
    from tests.integration.test_m2_research import demo

    payload = demo(client)
    payload["target"] = None
    _, hypothesis = complete(runtime, payload, key="hypothesis")
    report = check(client, hypothesis["draft"]["draft_id"])
    assert report["decision"]["decision"] == "block"
    assert (
        publish(
            client, hypothesis["draft"]["draft_id"], report["report"]["critic_run_id"]
        ).status_code
        == 409
    )


def test_wrong_observation_cannot_resolve_or_change_protocol(runtime):
    client, engine, _ = runtime
    _, view = complete(runtime)
    report = check(client, view["draft"]["draft_id"])
    response = publish(client, view["draft"]["draft_id"], report["report"]["critic_run_id"])
    version = response.json()
    registration = {
        "mode": "synthetic",
        "operator": "gte",
        "threshold": 70,
        "unit": "completed_tasks_per_100_trials",
    }
    protocol = client.post(
        f"{BASE}/versions/{version['version_id']}/register",
        headers=ADMIN_HEADERS,
        json=registration,
    ).json()
    from infra.db import ObservationVintage

    with Session(engine) as session:
        old = session.scalar(select(ObservationVintage))
        identifier = str(old.id)
    response = client.post(
        f"{BASE}/protocols/{protocol['protocol_id']}/resolve",
        headers=ADMIN_HEADERS,
        json={"observation_id": identifier},
    )
    assert response.status_code == 409


def test_only_two_revisions_and_research_only_after_limit(runtime):
    from tests.integration.test_m2_research import demo

    client, engine, _ = runtime
    payload = demo(client)
    payload["historical_case_ids"] = []
    _, view = complete(runtime, payload)
    identifier = view["draft"]["draft_id"]
    for expected in ["B1", "B2"]:
        review = check(client, identifier)
        assert review["decision"]["decision"] == "targeted_research"
        findings = [
            f["finding_id"]
            for f in review["report"]["findings"]
            if f["severity"] in {"L2", "L3"} and f["verification_status"] == "verified"
        ]
        response = client.post(
            f"{BASE}/drafts/{identifier}/revise",
            headers=ADMIN_HEADERS,
            json={
                "review_id": review["report"]["critic_run_id"],
                "confirmed_finding_ids": findings,
            },
        )
        assert response.status_code == 200, response.text
        assert response.json()["draft_sequence"] == expected
        identifier = response.json()["draft_id"]
    final = check(client, identifier)
    assert final["decision"]["decision"] == "research_only"
    assert publish(client, identifier, final["report"]["critic_run_id"]).status_code == 409
    assert (
        client.post(
            f"{BASE}/drafts/{identifier}/revise",
            headers=ADMIN_HEADERS,
            json={
                "review_id": final["report"]["critic_run_id"],
                "confirmed_finding_ids": [
                    f["finding_id"] for f in final["report"]["findings"] if f["severity"] == "L2"
                ],
            },
        ).status_code
        == 409
    )
    with Session(engine) as session:
        assert len(session.scalars(select(DraftRevision)).all()) == 2


def test_new_inputs_require_fresh_review_even_without_second_check(runtime):
    client, engine, _ = runtime
    _, view = complete(runtime)
    identifier = view["draft"]["draft_id"]
    report = check(client, identifier)
    add_counter(engine)
    response = publish(client, identifier, report["report"]["critic_run_id"])
    assert response.status_code == 409 and response.json()["code"] == "REVIEW_INPUT_CHANGED"


@pytest.mark.parametrize("value,expected", [(80, "confirmed"), (40, "disconfirmed")])
def test_resolution_uses_frozen_source_scope_and_observation(runtime, value, expected):
    from datetime import UTC, datetime

    from prediction_engine.contracts.models import ObservationImportV1

    from infra.db import Indicator
    from scripts.seed_demo import ADMIN_ID

    client, engine, _ = runtime
    _, view = complete(runtime)
    report = check(client, view["draft"]["draft_id"])
    version = publish(client, view["draft"]["draft_id"], report["report"]["critic_run_id"]).json()
    protocol = client.post(
        f"{BASE}/versions/{version['version_id']}/register",
        headers=ADMIN_HEADERS,
        json={
            "mode": "synthetic",
            "operator": "gte",
            "threshold": 70,
            "unit": "completed_tasks_per_100_trials",
        },
    ).json()
    with Session(engine) as session:
        repo = EvidenceRepository(session)
        data = SourceImportV1.model_validate(
            {
                "url": view["draft"]["target"]["resolution_source"],
                "title": "DEMO later observation",
                "publisher": "FutureOS synthetic fixture",
                "source_type": "manual",
                "published_at": "2021-01-10T00:00:00Z",
                "available_at": "2021-01-10T00:00:00Z",
                "availability_basis": "verified_archive",
                "availability_note": "Own synthetic result",
                "content": f"DEMO pre-registered trial result: {value} tasks completed.",
                "usage_permission": "authorized_full",
                "license_note": "Own synthetic fixture",
                "reliability_note": "Synthetic data only",
                "domain_tags": ["technology"],
                "label": "DEMO",
            }
        )
        source = repo.ingest(data, ADMIN_ID)
        indicator = session.scalar(select(Indicator))
        observation = repo.observation(
            indicator.id,
            ObservationImportV1(
                source_version_id=source.version.source_version_id,
                period_start=datetime(2020, 6, 2, tzinfo=UTC),
                period_end=datetime(2020, 12, 31, tzinfo=UTC),
                value=value,
                published_at=datetime(2021, 1, 10, tzinfo=UTC),
                available_at=datetime(2021, 1, 10, tzinfo=UTC),
                revision_number=1,
                quality_flag="DEMO_DATA",
                definition_note="Same fixed synthetic protocol",
            ),
        )
    response = client.post(
        f"{BASE}/protocols/{protocol['protocol_id']}/resolve",
        headers=ADMIN_HEADERS,
        json={"observation_id": str(observation.observation_id)},
    )
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["status"] == expected and result["baseline_absolute_error"] == abs(value - 60)
    assert result["forecast_absolute_error_a"] is None
    assert (
        client.get(BASE + "/scoreboard", headers=ADMIN_HEADERS).json()["records"][0][
            "latest_resolution"
        ]["status"]
        == expected
    )


def test_database_rejects_forged_version_shape_and_initial_pointer(runtime):
    client, engine, _ = runtime
    _, view = complete(runtime)
    report = check(client, view["draft"]["draft_id"])
    published = publish(client, view["draft"]["draft_id"], report["report"]["critic_run_id"]).json()
    from infra.db import WorldForecast

    with Session(engine) as session:
        version = session.get(ForecastVersion, UUID(published["version_id"]))
        values = {
            column.name: getattr(version, column.name)
            for column in ForecastVersion.__table__.columns
        }
        world = session.get(WorldForecast, version.forecast_id)
        world_values = {
            column.name: getattr(world, column.name) for column in WorldForecast.__table__.columns
        }
    values.update(id=uuid4(), version_num=99)
    with engine.begin() as connection:
        with pytest.raises(DatabaseError, match="M3_INVALID_VERSION_SHAPE"):
            connection.execute(ForecastVersion.__table__.insert().values(**values))
    world_values.update(id=uuid4(), stable_target_key="forged-initial-pointer")
    with engine.begin() as connection:
        with pytest.raises(DatabaseError, match="M3_INVALID_INITIAL_POINTER"):
            connection.execute(WorldForecast.__table__.insert().values(**world_values))


def test_verified_failure_case_can_be_added_in_targeted_revision(runtime):
    from tests.integration.test_m2_research import demo

    client, _, _ = runtime
    payload = demo(client)
    case_ids = payload["historical_case_ids"]
    payload["historical_case_ids"] = []
    _, view = complete(runtime, payload)
    identifier = view["draft"]["draft_id"]
    review = check(client, identifier)
    findings = [
        f["finding_id"]
        for f in review["report"]["findings"]
        if f["severity"] in {"L2", "L3"} and f["verification_status"] == "verified"
    ]
    response = client.post(
        f"{BASE}/drafts/{identifier}/revise",
        headers=ADMIN_HEADERS,
        json={
            "review_id": review["report"]["critic_run_id"],
            "confirmed_finding_ids": findings,
            "additional_case_ids": case_ids,
        },
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["body"]["target"] == view["draft"]["target"]
    assert len(body["body"]["analogies"]) == 2
    assert check(client, body["draft_id"])["decision"]["publication_allowed"]
