from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest
from prediction_engine.contracts.models import (
    ResearchSnapshotV1,
    SignalImportV1,
)
from prediction_engine.forecasting.workflow import build_forecast_draft, mock_narrative
from sqlalchemy import func, insert, select, text
from sqlalchemy.exc import DatabaseError
from sqlalchemy.orm import Session

from infra.db import ForecastVersion, ModelCall, ResearchRun, Signal, WorldForecast
from infra.evidence_repository import EvidenceRepository
from tests.conftest import ADMIN_HEADERS, USER_HEADERS
from workers.research.main import run_once

BASE = "/api/v1/admin/research"


def demo(client):
    response = client.post(BASE + "/demo-inputs", headers=ADMIN_HEADERS)
    assert response.status_code == 200, response.text
    return response.json()


def submit(client, payload, key="m2-request"):
    return client.post(
        BASE + "/submit", headers={**ADMIN_HEADERS, "Idempotency-Key": key}, json=payload
    )


def complete(runtime, payload=None, key="m2-request"):
    client, engine, config = runtime
    response = submit(client, payload or demo(client), key)
    assert response.status_code == 202, response.text
    accepted = response.json()
    assert run_once(engine, config)
    view = client.get(BASE + "/runs/" + accepted["run_id"], headers=ADMIN_HEADERS)
    assert view.status_code == 200, view.text
    assert view.json()["status"] == "succeeded", view.text
    return accepted, view.json()


def test_m2_pipeline_freeze_baseline_and_replay(runtime):
    client, engine, _ = runtime
    accepted, view = complete(runtime)
    draft = view["draft"]
    assert draft["kind"] == "draft_forecast"
    assert draft["publication_allowed"] is False and draft["status"] == "internal_unreviewed"
    assert draft["baseline"]["projected_value"] == 60 and draft["baseline"]["sample_count"] == 3
    assert draft["fusions"][0]["independent_source_groups"] == 3
    assert draft["contradiction_claim_ids"]
    assert {scenario["path"] for scenario in draft["scenarios"]} == {
        "base",
        "acceleration",
        "friction",
    }
    assert any(edge["sign"] == "negative" for edge in draft["mechanism_chain"])
    assert any(
        event["outcome_category"] == "failure"
        for analogy in draft["analogies"]
        for event in analogy["known_outcomes"]
    )
    replay = client.post(BASE + "/runs/" + accepted["run_id"] + "/replay", headers=ADMIN_HEADERS)
    assert replay.status_code == 200, replay.text
    assert replay.json()["identical"] and replay.json()["network_calls"] == 0
    job = client.get("/api/v1/jobs/" + accepted["job_id"], headers=ADMIN_HEADERS).json()
    assert job["result"]["draft_hash"] == view["draft_hash"]
    with Session(engine) as session:
        assert session.scalar(select(func.count()).select_from(ForecastVersion)) == 0
        assert session.scalar(select(WorldForecast)).current_version_id is None


def test_m2_idempotency_and_permissions(runtime):
    client, _, _ = runtime
    payload = demo(client)
    first = submit(client, payload)
    assert first.json() == submit(client, payload).json()
    assert submit(client, {**payload, "title": "changed"}).status_code == 409
    assert (
        client.post(
            BASE + "/submit", headers={**USER_HEADERS, "Idempotency-Key": "ordinary"}, json=payload
        ).status_code
        == 403
    )
    assert client.get(BASE + "/runs", headers=USER_HEADERS).status_code == 403
    assert (
        client.get("/api/v1/jobs/" + first.json()["job_id"], headers=USER_HEADERS).status_code
        == 404
    )


@pytest.mark.parametrize(
    "change,reason",
    [
        ("no_target", "NO_TESTABLE_TARGET"),
        ("no_numeric_data", "NUMERIC_BASELINE_OR_SCOPE_INSUFFICIENT"),
        ("missing_capability", "NO_INDEPENDENT_COMPLEMENTARY_FUSION"),
    ],
)
def test_incomplete_research_is_hypothesis(runtime, change, reason):
    client, _, _ = runtime
    payload = demo(client)
    if change == "no_target":
        payload["target"] = None
    elif change == "no_numeric_data":
        payload["indicator_id"] = None
    else:
        payload["signal_ids"] = payload["signal_ids"][:2]
    _, view = complete(runtime, payload)
    assert view["draft"]["kind"] == "hypothesis"
    assert reason in view["draft"]["downgrade_reasons"]


def test_three_same_source_signals_cannot_fuse(runtime):
    client, engine, _ = runtime
    payload = demo(client)
    with Session(engine) as session:
        repo = EvidenceRepository(session)
        original = session.get(Signal, UUID(payload["signal_ids"][0]))
        claim_ids = repo.signal_view(original).claim_ids
        repeated = [
            repo.create_signal(
                SignalImportV1.model_validate(
                    {
                        "headline": "DEMO reprint " + str(i),
                        "claim_ids": claim_ids,
                        "mechanism_tags": [cap],
                        "domain_tags": ["technology"],
                    }
                )
            ).signal_id
            for i, cap in enumerate(
                ["context_understanding", "tool_execution", "feedback_validation"]
            )
        ]
    payload["signal_ids"] = list(map(str, repeated))
    _, view = complete(runtime, payload)
    assert view["draft"]["fusions"] == [] and view["draft"]["kind"] == "hypothesis"


def test_future_source_and_missing_signal_fail_closed(runtime):
    client, _, _ = runtime
    payload = demo(client)
    assert submit(client, {**payload, "signal_ids": [str(uuid4())]}).status_code == 404
    payload["research_as_of"] = "2020-05-01T00:00:00Z"
    rejected = submit(client, payload)
    assert rejected.status_code == 422, rejected.text
    assert "TIME" in rejected.json()["code"]


def test_frozen_inputs_and_draft_are_append_only_and_publish_blocked(runtime):
    _, engine, _ = runtime
    _, view = complete(runtime)
    for table, assignment in [
        ("forecast_drafts", "model_id='tampered'"),
        ("research_runs", "model_id='tampered'"),
    ]:
        with engine.begin() as connection:
            with pytest.raises(DatabaseError):
                connection.execute(text(f"UPDATE {table} SET {assignment}"))
    with Session(engine) as session:
        target = session.scalar(select(WorldForecast))
        run = session.scalar(select(ResearchRun))
        values = dict(
            id=uuid4(),
            forecast_id=target.id,
            research_run_id=run.id,
            version_num=1,
            statement="must not publish",
            target={},
            research_as_of=datetime.now(UTC),
            published_at=datetime.now(UTC),
            body={},
        )
    with engine.begin() as connection:
        with pytest.raises(DatabaseError):
            connection.execute(insert(ForecastVersion).values(**values))


def test_model_unknown_citation_or_future_case_is_rejected(runtime):
    client, engine, _ = runtime
    accepted = submit(client, demo(client)).json()
    with Session(engine) as session:
        run = session.get(ResearchRun, UUID(accepted["run_id"]))
        snapshot = ResearchSnapshotV1.model_validate(run.snapshot)
        narrative = mock_narrative(snapshot)
        bad = narrative.model_copy(update={"cited_claim_ids": (uuid4(),)})
        with pytest.raises(ValueError, match="CITATION"):
            build_forecast_draft(run.id, snapshot, bad, "test")
        case = snapshot.cases[0]
        future = case.outcomes[0].model_copy(update={"known_at": datetime(2030, 1, 1, tzinfo=UTC)})
        bad_case = case.model_copy(update={"outcomes": (future,)})
        with pytest.raises(ValueError, match="FUTURE_LEAK"):
            build_forecast_draft(
                run.id, snapshot.model_copy(update={"cases": (bad_case,)}), narrative, "test"
            )


def test_live_requires_separate_opt_in_and_mock_label(runtime):
    client, _, _ = runtime
    payload = demo(client)
    assert submit(client, {**payload, "provider": "deepseek"}).status_code == 503
    assert submit(client, {**payload, "label": "REAL"}).status_code == 422


def test_live_reserved_attempt_does_not_repeat_paid_calls(runtime):
    client, engine, config = runtime
    payload = demo(client)
    # Submit under an explicitly enabled local configuration, but never touch a real provider.
    from prediction_engine.contracts.models import ResearchSubmitV1
    from pydantic import SecretStr

    from infra.research_repository import ResearchRepository
    from scripts.seed_demo import ADMIN_ID

    live = config.model_copy(
        update={"live_research_enabled": True, "deepseek_api_key": SecretStr("fake")}
    )
    with Session(engine) as session:
        accepted = ResearchRepository(session).submit(
            ResearchSubmitV1.model_validate({**payload, "provider": "deepseek"}),
            ADMIN_ID,
            "paid",
            live,
        )
        session.add(
            ModelCall(run_id=accepted.run_id, user_id=ADMIN_ID, status="started", model_id="test")
        )
        session.commit()
    assert run_once(engine, live)
    view = client.get(BASE + "/runs/" + str(accepted.run_id), headers=ADMIN_HEADERS).json()
    assert view["status"] == "failed_terminal"
    assert view["error_code"] == "MODEL_CALL_UNCERTAIN_REQUIRES_REVIEW"


def test_replay_ignores_later_vintage_import(runtime):
    client, _, _ = runtime
    payload = demo(client)
    accepted, view = complete(runtime, payload)
    source = client.post(
        "/api/v1/admin/sources/ingest",
        headers=ADMIN_HEADERS,
        json={
            "url": "https://example.invalid/m2/new-vintage",
            "title": "DEMO correction",
            "publisher": "Fixture",
            "source_type": "manual",
            "published_at": "2020-05-20T00:00:00Z",
            "available_at": "2020-05-20T00:00:00Z",
            "availability_basis": "verified_archive",
            "availability_note": "Synthetic proof",
            "content": "DEMO value is 90",
            "usage_permission": "authorized_full",
            "license_note": "Own fixture",
            "reliability_note": "DEMO",
            "domain_tags": ["technology"],
            "label": "DEMO",
            "claims": [],
        },
    ).json()
    old = view["draft"]["baseline"]["observation_ids"]
    observation = client.post(
        f"/api/v1/admin/indicators/{payload['indicator_id']}/observations",
        headers=ADMIN_HEADERS,
        json={
            "source_version_id": source["version"]["source_version_id"],
            "period_start": "2020-03-01T00:00:00Z",
            "period_end": "2020-03-28T00:00:00Z",
            "value": 90,
            "published_at": "2020-05-20T00:00:00Z",
            "available_at": "2020-05-20T00:00:00Z",
            "revision_number": 2,
            "quality_flag": "DEMO_DATA",
            "definition_note": "DEMO correction",
        },
    )
    assert observation.status_code == 200, observation.text
    replay = client.post(
        BASE + "/runs/" + accepted["run_id"] + "/replay", headers=ADMIN_HEADERS
    ).json()
    assert replay["identical"]
    _, new = complete(runtime, payload, key="new-vintage")
    assert new["draft"]["baseline"]["projected_value"] == 90
    assert new["draft"]["baseline"]["observation_ids"] != old


@pytest.mark.parametrize(
    "stage", ["emergence", "growth", "maturity", "inflection", "decline", "unknown"]
)
def test_m2_supports_all_lifecycle_stages(runtime, stage):
    client, _, _ = runtime
    payload = demo(client)
    _, view = complete(runtime, {**payload, "lifecycle_stage": stage})
    assert view["draft"]["lifecycle_stage"] == stage
    assert view["draft"]["fusions"][0]["stage"] == stage


def test_stable_target_shared_by_runs_and_percentages_not_calibrated(runtime):
    client, engine, _ = runtime
    payload = demo(client)
    accepted, first = complete(runtime, payload)
    _, second = complete(runtime, payload, key="second-run")
    assert first["draft"]["run_id"] != second["draft"]["run_id"]
    with Session(engine) as session:
        assert session.scalar(select(func.count()).select_from(WorldForecast)) == 1
        run = session.get(ResearchRun, UUID(accepted["run_id"]))
        snapshot = ResearchSnapshotV1.model_validate(run.snapshot)
        with pytest.raises(ValueError, match="UNCALIBRATED"):
            build_forecast_draft(
                run.id,
                snapshot,
                mock_narrative(snapshot).model_copy(update={"hypothesis": "88% probability"}),
                "test",
            )


def test_unresolved_target_cannot_be_promoted(runtime):
    client, _, _ = runtime
    payload = demo(client)
    payload["target"]["resolution_rule"] = "   "
    response = submit(client, payload)
    assert response.status_code == 422
    assert response.json()["code"] == "RESEARCH_TARGET_UNRESOLVED"


def test_completed_model_call_is_reused_and_frozen(runtime):
    from prediction_engine.contracts.models import ResearchSubmitV1
    from pydantic import SecretStr

    from infra.research_repository import ResearchRepository
    from scripts.seed_demo import ADMIN_ID

    client, engine, config = runtime
    payload = demo(client)
    enabled = config.model_copy(
        update={"live_research_enabled": True, "deepseek_api_key": SecretStr("fake")}
    )
    with Session(engine) as session:
        accepted = ResearchRepository(session).submit(
            ResearchSubmitV1.model_validate({**payload, "provider": "deepseek"}),
            ADMIN_ID,
            "cached",
            enabled,
        )
        row = session.get(ResearchRun, accepted.run_id)
        snapshot = ResearchSnapshotV1.model_validate(row.snapshot)
        session.add(
            ModelCall(
                run_id=row.id,
                user_id=ADMIN_ID,
                status="completed",
                model_id="cached-test-model",
                response=mock_narrative(snapshot).model_dump(mode="json"),
                usage={"total_tokens": 1},
            )
        )
        session.commit()
    assert run_once(engine, enabled)
    replay = client.post(BASE + "/runs/" + str(accepted.run_id) + "/replay", headers=ADMIN_HEADERS)
    assert replay.status_code == 200 and replay.json()["identical"]
    with engine.begin() as connection:
        with pytest.raises(DatabaseError):
            connection.execute(text("UPDATE model_calls SET model_id='tampered'"))


def test_future_period_projection_is_not_observed_baseline(runtime):
    from prediction_engine.contracts.models import ObservationImportV1

    from infra.db import ObservationVintage

    client, engine, _ = runtime
    payload = demo(client)
    with Session(engine) as session:
        original = session.scalar(
            select(ObservationVintage).where(
                ObservationVintage.indicator_id == UUID(payload["indicator_id"])
            )
        )
        EvidenceRepository(session).observation(
            UUID(payload["indicator_id"]),
            ObservationImportV1(
                source_version_id=original.source_version_id,
                period_start=datetime(2020, 7, 1, tzinfo=UTC),
                period_end=datetime(2020, 7, 28, tzinfo=UTC),
                value=99,
                published_at=datetime(2020, 5, 5, tzinfo=UTC),
                available_at=datetime(2020, 5, 5, tzinfo=UTC),
                revision_number=1,
                quality_flag="DEMO_DATA",
                definition_note="Negative fixture: future projection",
            ),
        )
    response = submit(client, payload)
    assert response.status_code == 422
    assert response.json()["code"] == "RESEARCH_OBSERVATION_NOT_OBSERVED"


def test_replay_uses_verified_archived_core_when_current_code_changes(
    runtime, monkeypatch, tmp_path
):
    import infra.engine_artifacts as artifacts

    monkeypatch.setattr(artifacts, "FOLDER", tmp_path / "engines")
    client, _, _ = runtime
    accepted, _ = complete(runtime)
    monkeypatch.setattr("infra.research_repository.engine_code_hash", lambda: "f" * 64)
    response = client.post(BASE + "/runs/" + accepted["run_id"] + "/replay", headers=ADMIN_HEADERS)
    assert response.status_code == 200, response.text
    assert response.json()["identical"] and response.json()["network_calls"] == 0


def test_corrupted_engine_artifact_fails_closed(runtime, monkeypatch, tmp_path):
    import infra.engine_artifacts as artifacts

    monkeypatch.setattr(artifacts, "FOLDER", tmp_path / "engines")
    client, _, _ = runtime
    accepted, _ = complete(runtime)
    for file in (tmp_path / "engines").glob("*.zip"):
        file.write_bytes(b"corrupted")
    monkeypatch.setattr("infra.research_repository.engine_code_hash", lambda: "f" * 64)
    response = client.post(BASE + "/runs/" + accepted["run_id"] + "/replay", headers=ADMIN_HEADERS)
    assert response.status_code == 409
    assert response.json()["code"] == "REPLAY_ENGINE_VERSION_MISMATCH"
