"""M5 synthetic acceptance: immutable publications, shared updates and consent gates."""

import hashlib
import hmac
import json
from uuid import UUID, uuid4

from pydantic import SecretStr
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from infra.db import (
    ForecastVersion,
    InAppNotification,
    Job,
    MailAttempt,
    MailDelivery,
    MonitorOutcome,
    OutboxEvent,
    UsageLedger,
    WorldForecast,
)
from infra.notifications import accept_bounce
from tests.conftest import ADMIN_HEADERS
from tests.integration.test_m4_reports import account, complete_report, profile
from workers.research.main import run_once


def setup_report(runtime):
    client, _, _ = runtime
    owner, _, _ = account(client)
    profile(client, owner)
    _, report = complete_report(runtime, owner)
    return owner, report


def world_id(engine, report):
    with Session(engine) as session:
        return str(
            session.get(ForecastVersion, UUID(report["forecast_version_ids"][0])).forecast_id
        )


def drain(engine, config):
    for _ in range(25):
        if not run_once(engine, config):
            return
    raise AssertionError("Worker did not drain bounded queue")


def demo_change(runtime, identifier):
    client, engine, config = runtime
    response = client.post(
        "/api/v1/admin/monitor/forecasts/" + identifier + "/demo-change", headers=ADMIN_HEADERS
    )
    assert response.status_code == 200, response.text
    drain(engine, config)
    return response.json()


def test_t0_no_version_and_shared_t2_free_private_updates(runtime):
    client, engine, config = runtime
    first, a = setup_report(runtime)
    second, _, _ = account(client)
    profile(client, second)
    _, b = complete_report(runtime, second)
    identifier = world_id(engine, a)
    check_path = "/api/v1/admin/monitor/forecasts/" + identifier + "/check"
    first_check = client.post(check_path, headers=ADMIN_HEADERS, json={})
    assert first_check.status_code == 200, first_check.text
    drain(engine, config)
    duplicate = client.post(check_path, headers=ADMIN_HEADERS, json={}).json()
    assert duplicate["deduplicated"] and duplicate["job_id"] == first_check.json()["job_id"]
    with Session(engine) as session:
        before_count = session.scalar(select(func.count()).select_from(ForecastVersion))
        t0 = session.get(MonitorOutcome, UUID(first_check.json()["monitor_run_id"]))
        assert t0.body["level"] == "T0" and t0.body["outcome"] == "archived"
        old_world = session.get(ForecastVersion, UUID(a["forecast_version_ids"][0]))
        old_hash = old_world.immutable_hash
    result = demo_change(runtime, identifier)
    with Session(engine) as session:
        outcome = session.get(MonitorOutcome, UUID(result["monitor_run_id"]))
        assert outcome is not None, session.get(Job, UUID(result["job_id"])).error_code
        assert outcome.body["level"] == "T2" and outcome.body["outcome"] == "published", (
            outcome.body
        )
        assert outcome.body["refreshed_reports"] == 2 and outcome.body["external_model_calls"] == 0
        assert session.scalar(select(func.count()).select_from(ForecastVersion)) == before_count + 1
        assert (
            session.get(ForecastVersion, UUID(a["forecast_version_ids"][0])).immutable_hash
            == old_hash
        )
        assert (
            session.scalar(
                select(func.count())
                .select_from(UsageLedger)
                .where(UsageLedger.entry_kind == "consumed")
            )
            == 2
        )
    for headers, old in [(first, a), (second, b)]:
        new = client.get("/api/v1/reports/" + old["report_id"], headers=headers).json()
        assert new["version_num"] == 2, new
        assert new["previous_report_version_id"] == old["report_version_id"]
        assert new["change_summary"] and len(new["forecast_version_ids"]) == len(
            old["forecast_version_ids"]
        )
        assert (
            client.get(
                "/api/v1/reports/" + old["report_id"] + "/versions/" + old["report_version_id"],
                headers=headers,
            ).json()
            == old
        )
        notices = client.get("/api/v1/notifications", headers=headers).json()
        assert len(notices) == 1 and notices[0]["report_version_id"] == new["report_version_id"]
        assert (
            client.post(
                "/api/v1/notifications/" + notices[0]["notification_id"] + "/read", headers=headers
            ).status_code
            == 200
        )
        assert client.get("/api/v1/notifications", headers=headers).json()[0]["read"]
    other_notices = client.get("/api/v1/notifications", headers=second).json()
    assert (
        client.post(
            "/api/v1/notifications/" + other_notices[0]["notification_id"] + "/read", headers=first
        ).status_code
        == 404
    )
    assert client.get("/api/v1/me/mail-deliveries", headers=first).json() == []


def test_preferences_local_queue_unsubscribe_ownership_and_bounce(runtime):
    client, engine, config = runtime
    owner, report = setup_report(runtime)
    stranger, _, _ = account(client)
    pref_path = "/api/v1/me/notification-preferences"
    deliver = "/api/v1/reports/" + report["report_id"] + "/deliver"
    assert client.get(pref_path, headers=owner).json()["alert_opt_in"] is False
    assert client.put(pref_path, headers=owner, json={"alert_opt_in": True}).status_code == 422
    consent = {
        "first_report_opt_in": True,
        "alert_opt_in": True,
        "digest_opt_in": True,
        "explicit_consent": True,
    }
    assert client.put(pref_path, headers=owner, json=consent).status_code == 200
    assert (
        client.post(
            deliver, headers=owner, json={"purpose": "first_report", "explicit_consent": False}
        ).status_code
        == 422
    )
    payload = {"purpose": "first_report", "explicit_consent": True}
    queued = client.post(deliver, headers=owner, json=payload).json()
    assert queued["eligible"]
    assert client.post(deliver, headers=owner, json=payload).json()["deduplicated"]
    assert client.post(deliver, headers=stranger, json=payload).status_code == 404
    drain(engine, config)
    path = "/api/v1/me/mail-deliveries/" + queued["delivery_id"]
    assert client.get(path, headers=stranger).status_code == 404
    content = client.get(path, headers=owner).json()
    assert report["report_version_id"] in content["link"] and "recipient" not in content
    deliveries = client.get("/api/v1/me/mail-deliveries", headers=owner).json()
    assert deliveries[0]["status"] == "delivered_local" and not deliveries[0]["external_delivery"]
    with Session(engine) as session:
        assert session.scalar(select(func.count()).select_from(MailAttempt)) == 1
    token = content["unsubscribe_link"].split("token=")[1]
    for _ in range(2):
        assert client.post("/api/v1/mail/unsubscribe", json={"token": token}).status_code == 200
    assert not client.get(pref_path, headers=owner).json()["alert_opt_in"]
    assert client.post("/api/v1/mail/unsubscribe", json={"token": "x" * 40}).status_code == 404
    # Re-enable, then a signed provider bounce permanently suppresses eligibility.
    client.put(pref_path, headers=owner, json=consent)
    raw = json.dumps(
        {"event_id": uuid4().hex, "delivery_id": queued["delivery_id"], "kind": "bounce"}
    ).encode()
    secured = config.model_copy(update={"bounce_webhook_secret": SecretStr("test-only-bounce-key")})
    sig = hmac.new(b"test-only-bounce-key", raw, hashlib.sha256).hexdigest()
    import pytest

    from infra.evidence_repository import EvidenceError

    with Session(engine) as session:
        with pytest.raises(EvidenceError):
            accept_bounce(session, secured, raw, "wrong")
        assert accept_bounce(session, secured, raw, sig)["duplicate"] is False
        assert accept_bounce(session, secured, raw, sig)["duplicate"] is True
    assert not client.post(
        deliver, headers=owner, json={"purpose": "digest", "explicit_consent": True}
    ).json()["eligible"]


def test_optout_before_dispatch_and_failure_produce_no_external_delivery(runtime, monkeypatch):
    client, engine, config = runtime
    owner, report = setup_report(runtime)
    pref_path = "/api/v1/me/notification-preferences"
    client.put(
        pref_path, headers=owner, json={"first_report_opt_in": True, "explicit_consent": True}
    )
    client.post(
        "/api/v1/reports/" + report["report_id"] + "/deliver",
        headers=owner,
        json={"purpose": "first_report", "explicit_consent": True},
    )
    client.put(pref_path, headers=owner, json={})
    drain(engine, config)
    assert (
        client.get("/api/v1/me/mail-deliveries", headers=owner).json()[0]["status"] == "suppressed"
    )
    with Session(engine) as session:
        assert (
            session.scalar(
                select(func.count())
                .select_from(OutboxEvent)
                .where(OutboxEvent.event_type == "MailSuppressed.v1")
            )
            == 1
        )
        assert (
            session.scalar(
                select(func.count())
                .select_from(OutboxEvent)
                .where(OutboxEvent.event_type == "MailDelivered.v1")
            )
            == 0
        )
    import infra.monitoring as monitoring

    def fail(*args, **kwargs):
        raise ValueError("TEST_MONITOR_FAILED")

    monkeypatch.setattr(monitoring.MonitorRepository, "persist", fail)
    response = client.post(
        "/api/v1/admin/monitor/forecasts/" + world_id(engine, report) + "/check",
        headers=ADMIN_HEADERS,
        json={},
    )
    drain(engine, config)
    with Session(engine) as session:
        assert session.get(Job, UUID(response.json()["job_id"])).status == "failed_terminal"
        assert session.scalar(select(func.count()).select_from(InAppNotification)) == 0
        assert session.scalar(select(func.count()).select_from(MailDelivery)) == 1
        assert session.scalar(select(func.count()).select_from(MonitorOutcome)) == 0


def test_scheduler_and_profile_refresh_stay_with_original_topics(runtime):
    client, engine, config = runtime
    owner, report = setup_report(runtime)
    from workers.scheduler.main import tick

    assert tick(engine, config.model_copy(update={"scheduler_enabled": False}))["checked"] == 0
    assert tick(engine, config)["errors"] == 0
    drain(engine, config)
    assert tick(engine, config)["queued"] == 0
    profile(client, owner, industry_l1_code="healthcare", industry_l2_code="clinical")
    result = client.post("/api/v1/reports/" + report["report_id"] + "/refresh", headers=owner)
    assert result.status_code == 200, result.text
    drain(engine, config)
    new = client.get("/api/v1/reports/" + report["report_id"], headers=owner).json()
    assert new["version_num"] == 2 and new["forecast_version_ids"] == report["forecast_version_ids"]
    assert client.get("/api/v1/me/entitlements", headers=owner).json()["consumed"] == 1


def add_counter(engine, config, identifier):
    from prediction_engine.contracts.models import SignalImportV1, SourceImportV1

    from infra.evidence_repository import EvidenceRepository
    from infra.monitoring import MonitorRepository
    from scripts.seed_demo import ADMIN_ID

    with Session(engine) as session:
        version = session.get(
            ForecastVersion, session.get(WorldForecast, UUID(identifier)).current_version_id
        )
        snapshot = MonitorRepository(session, config).snapshot_for(version)
        content = "Verified synthetic cost constraint " + uuid4().hex
        repo = EvidenceRepository(session)
        imported = repo.ingest(
            SourceImportV1.model_validate(
                {
                    "url": "https://example.invalid/critical/" + uuid4().hex,
                    "title": "Critical synthetic follow-up",
                    "publisher": "Independent own observer",
                    "source_type": "manual",
                    "availability_basis": "observed_now",
                    "content": content,
                    "usage_permission": "authorized_full",
                    "license_note": "Own synthetic text",
                    "reliability_note": "Synthetic acceptance",
                    "domain_tags": snapshot.request.domain_tags,
                    "label": "DEMO",
                    "claims": [
                        {
                            "claim_text": content,
                            "quote": content,
                            "source_locator": "paragraph 1",
                            "relation": "contradicts",
                            "claim_kind": "fact",
                            "verification_status": "verified",
                            "verification_note": "Literal check",
                            "scope": snapshot.request.scope,
                        }
                    ],
                }
            ),
            ADMIN_ID,
        )
        repo.create_signal(
            SignalImportV1(
                headline=content,
                claim_ids=imported.claim_ids,
                mechanism_tags=("reliability_risk",),
                domain_tags=snapshot.request.domain_tags,
            )
        )
        return snapshot, imported.claim_ids[0]


def test_t1_then_t3_blocked_preserves_world_and_downgrades_private_advice(runtime):
    client, engine, config = runtime
    owner, report = setup_report(runtime)
    identifier = world_id(engine, report)
    snapshot, counter = add_counter(engine, config, identifier)
    path = "/api/v1/admin/monitor/forecasts/" + identifier + "/check"
    t1 = client.post(path, headers=ADMIN_HEADERS, json={}).json()
    drain(engine, config)
    with Session(engine) as session:
        result = session.get(MonitorOutcome, UUID(t1["monitor_run_id"]))
        assert result.body["level"] == "T1" and result.body["outcome"] == "observed"
        count = session.scalar(select(func.count()).select_from(ForecastVersion))
    assertions = [
        {
            "kind": "critical_assumption_broken",
            "prior_claim_id": str(c.claim_id),
            "claim_ids": [str(counter)],
            "verification_note": "Synthetic critical assumption invalidated for fault injection",
        }
        for c in snapshot.claims
    ]
    accepted = client.post(path, headers=ADMIN_HEADERS, json={"assertions": assertions})
    assert accepted.status_code == 200, accepted.text
    drain(engine, config)
    with Session(engine) as session:
        result = session.get(MonitorOutcome, UUID(accepted.json()["monitor_run_id"]))
        assert result is not None, session.get(Job, UUID(accepted.json()["job_id"])).error_code
        assert result.body["level"] == "T3" and result.body["outcome"] == "review_blocked", (
            result.body
        )
        assert result.body["new_version_id"] is None
        assert session.scalar(select(func.count()).select_from(ForecastVersion)) == count
    current = client.get("/api/v1/reports/" + report["report_id"], headers=owner).json()
    assert (
        current["version_num"] == 2
        and current["forecast_version_ids"] == report["forecast_version_ids"]
    )
    assert any("待核实" in gap for gap in current["evidence_gaps"])
    assert all(a["priority"] == "observe" for a in current["recommendations"])
    detail = client.get(
        "/api/v1/forecasts/versions/" + report["forecast_version_ids"][0], headers=owner
    ).json()
    assert detail["monitor_notice"]["outcome"] == "review_blocked"


def test_monitor_budget_and_unauthorized_checks(runtime):
    client, engine, config = runtime
    owner, report = setup_report(runtime)
    identifier = world_id(engine, report)
    path = "/api/v1/admin/monitor/forecasts/" + identifier
    assert client.post(path + "/check", headers=owner, json={}).status_code == 403
    assert (
        client.put(path + "/policy", headers=ADMIN_HEADERS, json={"max_daily_jobs": 1}).status_code
        == 200
    )
    assert client.post(path + "/check", headers=ADMIN_HEADERS, json={}).status_code == 200
    drain(engine, config)
    add_counter(engine, config, identifier)
    assert client.post(path + "/check", headers=ADMIN_HEADERS, json={}).status_code == 429
    assert (
        client.put(path + "/policy", headers=ADMIN_HEADERS, json={"enabled": False}).status_code
        == 200
    )
    assert client.post(path + "/check", headers=ADMIN_HEADERS, json={}).status_code == 409


def test_failure_after_draft_publication_rolls_back_and_sends_no_notifications(
    runtime, monkeypatch
):
    client, engine, config = runtime
    owner, report = setup_report(runtime)
    import infra.updates as updates

    def fail(*args, **kwargs):
        raise ValueError("TEST_DOWNSTREAM_FAILED")

    monkeypatch.setattr(updates, "queue_affected_reports", fail)
    with Session(engine) as session:
        count = session.scalar(select(func.count()).select_from(ForecastVersion))
    accepted = demo_change(runtime, world_id(engine, report))
    with Session(engine) as session:
        job = session.get(Job, UUID(accepted["job_id"]))
        assert job.status == "failed_terminal"
        assert session.scalar(select(func.count()).select_from(ForecastVersion)) == count
        assert session.scalar(select(func.count()).select_from(InAppNotification)) == 0
        assert session.scalar(select(func.count()).select_from(MailDelivery)) == 0
    assert client.get("/api/v1/reports/" + report["report_id"], headers=owner).json() == report
