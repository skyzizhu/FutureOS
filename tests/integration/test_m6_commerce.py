"""Sandbox payment verification, conserved credit lifecycle and paid/free boundaries."""

import hashlib
import hmac
from datetime import timedelta
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from prediction_engine.contracts.models import PaymentEventV1
from sqlalchemy import func, select, text
from sqlalchemy.exc import DatabaseError
from sqlalchemy.orm import Session

from apps.api.main import create_app
from infra.billing import BillingRepository
from infra.db import (
    CommerceCheckout,
    CommercePaymentEvent,
    CostObservation,
    ForecastVersion,
    InAppNotification,
    Job,
    MailDelivery,
    ModelCall,
    PaidResearchReservation,
    PaidSubscription,
    ResearchCreditGrant,
    SharedTopicStudy,
    UsageLedger,
    UserResearchTopic,
    utcnow,
)
from infra.paid_research import schedule_paid
from tests.conftest import ADMIN_HEADERS, USER_HEADERS
from tests.integration.test_m4_reports import account, profile
from workers.research.main import run_once

SCOPE = {
    "domain": "technology",
    "focus": "workflow_adoption",
    "population": "small_teams",
    "geography": "global",
    "label": "DEMO",
}
CONSENT = {"explicit_sandbox_consent": True}


@pytest.fixture
def commerce(runtime):
    _, engine, config = runtime
    enabled = config.model_copy(update={"sandbox_commerce_enabled": True})
    app = create_app(enabled)
    with TestClient(app, raise_server_exceptions=False) as client:
        yield client, engine, enabled
    app.state.engine.dispose()


def user(runtime):
    client, _, _ = runtime
    headers, state, _ = account(client)
    profile(client, headers)
    return headers, UUID(state["identity"]["user_id"])


def purchase(runtime, headers, plan="demo_pack", key=None):
    client, _, _ = runtime
    checkout = client.post(
        "/api/v1/billing/checkout",
        headers={**headers, "Idempotency-Key": key or uuid4().hex},
        json={**CONSENT, "plan_code": plan},
    )
    assert checkout.status_code == 201, checkout.text
    data = checkout.json()
    result = client.post(
        "/api/v1/billing/checkouts/" + data["checkout_id"] + "/confirm",
        headers=headers,
        json=CONSENT,
    )
    assert result.status_code == 200, result.text
    return data


def submit(runtime, headers, scope=None, key=None):
    client, _, _ = runtime
    quote = client.post("/api/v1/research/quote", headers=headers, json=scope or SCOPE)
    assert quote.status_code == 200, quote.text
    result = client.post(
        "/api/v1/research/submit",
        headers={**headers, "Idempotency-Key": key or uuid4().hex},
        json={"quote_id": quote.json()["quote_id"], "accept_usage_rules": True},
    )
    return quote.json(), result


def drain(runtime):
    _, engine, config = runtime
    for _ in range(30):
        if not run_once(engine, config):
            return
    raise AssertionError("Bounded queue did not drain")


def balance(runtime, headers):
    return runtime[0].get("/api/v1/billing/balance", headers=headers).json()


def report_for(runtime, headers, accepted):
    client, _, _ = runtime
    job = client.get("/api/v1/jobs/" + accepted["job_id"], headers=headers)
    assert job.status_code == 200 and job.json()["status"] == "succeeded", job.text
    response = client.get("/api/v1/reports/" + job.json()["result"]["report_id"], headers=headers)
    assert response.status_code == 200, response.text
    return response.json()


def test_feature_flag_default_and_no_unverified_unlock(runtime):
    client, _, _ = runtime
    headers, _ = user(runtime)
    assert client.get("/api/v1/billing/status").json()["enabled"] is False
    assert (
        client.post(
            "/api/v1/billing/checkout",
            headers={**headers, "Idempotency-Key": "disabled"},
            json={**CONSENT, "plan_code": "demo_pack"},
        ).status_code
        == 503
    )
    assert client.post("/api/v1/research/quote", headers=headers, json=SCOPE).status_code == 503
    assert balance(runtime, headers)["available"] == 0


def test_checkout_signature_replay_amount_and_owner_isolation(commerce):
    client, engine, config = commerce
    owner, _ = user(commerce)
    other, _ = user(commerce)
    body = {**CONSENT, "plan_code": "demo_pack"}
    checkout = client.post(
        "/api/v1/billing/checkout", headers={**owner, "Idempotency-Key": "one-order"}, json=body
    ).json()
    assert balance(commerce, owner)["available"] == 0
    assert (
        client.post(
            "/api/v1/billing/checkout", headers={**owner, "Idempotency-Key": "one-order"}, json=body
        ).json()
        == checkout
    )
    assert (
        client.post(
            "/api/v1/billing/checkout",
            headers={**owner, "Idempotency-Key": "one-order"},
            json={**CONSENT, "plan_code": "demo_monthly"},
        ).status_code
        == 409
    )
    path = "/api/v1/billing/checkouts/" + checkout["checkout_id"]
    assert client.get(path, headers=other).status_code == 404
    assert client.post(path + "/confirm", headers=other, json=CONSENT).status_code == 404
    assert (
        client.post(
            path + "/confirm", headers=owner, json={"explicit_sandbox_consent": 1}
        ).status_code
        == 422
    )
    with Session(engine) as session:
        row = session.get(CommerceCheckout, UUID(checkout["checkout_id"]))
        key = BillingRepository(session, config).signing_key()
        event = PaymentEventV1(
            event_id="verified-event",
            checkout_id=row.id,
            provider_reference=row.provider_reference,
            event_type="checkout.paid",
            amount_minor=row.plan["amount_minor"],
            currency="CNY",
            occurred_at=utcnow(),
        )
    raw = event.model_dump_json().encode()
    assert (
        client.post(
            "/api/v1/billing/webhook", content=raw, headers={"X-Payment-Signature": "forged"}
        ).status_code
        == 403
    )
    wrong = (
        event.model_copy(update={"amount_minor": event.amount_minor + 1}).model_dump_json().encode()
    )
    assert (
        client.post(
            "/api/v1/billing/webhook",
            content=wrong,
            headers={"X-Payment-Signature": hmac.new(key, wrong, hashlib.sha256).hexdigest()},
        ).status_code
        == 409
    )
    assert balance(commerce, owner)["available"] == 0
    signed = {"X-Payment-Signature": hmac.new(key, raw, hashlib.sha256).hexdigest()}
    for duplicate in (False, True):
        response = client.post("/api/v1/billing/webhook", content=raw, headers=signed)
        assert response.status_code == 200 and response.json()["duplicate"] is duplicate, (
            response.text
        )
    assert balance(commerce, owner)["available"] == 3
    assert balance(commerce, other)["available"] == 0
    assert client.get("/api/v1/billing/history", headers=other).json()["checkouts"] == []
    with Session(engine) as session:
        assert session.scalar(select(func.count()).select_from(ResearchCreditGrant)) == 1
        assert session.scalar(select(func.count()).select_from(CommercePaymentEvent)) == 1
    assert client.get("/api/v1/billing/history", headers=USER_HEADERS).status_code == 403


def test_research_success_consumes_once_reuses_world_and_old_topic_free(commerce):
    client, engine, _ = commerce
    owner, _ = user(commerce)
    purchase(commerce, owner)
    quote, response = submit(commerce, owner, key="new-scope")
    assert quote["kind"] == "new_topic" and quote["units_required"] == 1
    assert response.status_code == 202, response.text
    accepted = response.json()
    assert balance(commerce, owner)["reserved"] == 1 and balance(commerce, owner)["available"] == 2
    assert client.post(
        "/api/v1/research/submit",
        headers={**owner, "Idempotency-Key": "new-scope"},
        json={"quote_id": quote["quote_id"], "accept_usage_rules": True},
    ).json()["deduplicated"]
    drain(commerce)
    first = report_for(commerce, owner, accepted)
    published = client.get(
        "/api/v1/forecasts/versions/" + first["forecast_version_ids"][0], headers=owner
    ).json()["version"]
    from datetime import datetime

    assert datetime.fromisoformat(first["created_at"]) >= datetime.fromisoformat(
        published["published_at"]
    )
    assert balance(commerce, owner)["consumed"] == 1 and balance(commerce, owner)["reserved"] == 0
    assert client.get("/api/v1/me/entitlements", headers=owner).json()["available"] == 1
    profile(client, owner, occupation_text="Private role not shared", use_optional_fields=True)
    same_quote, same = submit(commerce, owner)
    assert same_quote["kind"] == "existing_topic" and same_quote["units_required"] == 0
    assert same.json()["reserved_units"] == 0
    drain(commerce)
    updated = client.get("/api/v1/reports/" + first["report_id"], headers=owner).json()
    assert updated["version_num"] == 2 and balance(commerce, owner)["consumed"] == 1
    assert (
        client.get(
            "/api/v1/reports/" + first["report_id"] + "/versions/" + first["report_version_id"],
            headers=owner,
        ).json()
        == first
    )
    with Session(engine) as session:
        count = session.scalar(select(func.count()).select_from(ForecastVersion))
        assert session.scalar(select(func.count()).select_from(UsageLedger)) == 0
    other, _ = user(commerce)
    purchase(commerce, other)
    _, another = submit(commerce, other)
    drain(commerce)
    second = report_for(commerce, other, another.json())
    assert second["forecast_version_ids"] == first["forecast_version_ids"]
    assert second["report_id"] != first["report_id"]
    with Session(engine) as session:
        assert session.scalar(select(func.count()).select_from(ForecastVersion)) == count
        assert session.scalar(select(func.count()).select_from(ModelCall)) == 0
        assert (
            session.scalar(
                select(func.count())
                .select_from(CostObservation)
                .where(CostObservation.stage == "shared_research", CostObservation.reused.is_(True))
            )
            == 1
        )
    assert client.get("/api/v1/reports/" + first["report_id"], headers=other).status_code == 404
    assert (
        client.post(
            "/api/v1/research/topics/" + accepted["user_topic_id"] + "/pause", headers=other
        ).status_code
        == 404
    )
    cost = client.get("/api/v1/admin/costs", headers=ADMIN_HEADERS).json()
    assert cost["shared_research_total"] == 2 and cost["shared_research_reused"] == 1
    assert client.get("/api/v1/admin/costs", headers=owner).status_code == 403


def test_failure_cancellation_real_insufficiency_and_optional_withdraw_release(
    commerce, monkeypatch
):
    client, engine, _ = commerce
    owner, _ = user(commerce)
    purchase(commerce, owner)
    _, request = submit(commerce, owner)
    assert (
        client.post(
            "/api/v1/research/paid-jobs/" + request.json()["job_id"] + "/cancel", headers=owner
        ).status_code
        == 200
    )
    assert balance(commerce, owner)["available"] == 3
    import infra.paid_research as paid

    def fail(*args, **kwargs):
        raise ValueError("TEST_PAID_REPORT_FAILED")

    with monkeypatch.context() as patcher:
        patcher.setattr(paid, "build_private_report", fail)
        _, response = submit(commerce, owner)
        drain(commerce)
        job = client.get("/api/v1/jobs/" + response.json()["job_id"], headers=owner).json()
        assert job["status"] == "failed_terminal" and job["error_code"] == "TEST_PAID_REPORT_FAILED"
    assert balance(commerce, owner)["available"] == 3
    with Session(engine) as session:
        assert session.scalar(select(func.count()).select_from(InAppNotification)) == 0
        assert session.scalar(select(func.count()).select_from(MailDelivery)) == 0
        assert session.scalar(select(SharedTopicStudy)).forecast_id is None
    _, real = submit(commerce, owner, scope={**SCOPE, "label": "REAL"})
    drain(commerce)
    job = client.get("/api/v1/jobs/" + real.json()["job_id"], headers=owner).json()
    assert (
        job["status"] == "failed_terminal"
        and job["error_code"] == "REAL_CUSTOM_RESEARCH_NOT_ENABLED"
    )
    assert balance(commerce, owner)["available"] == 3
    profile(client, owner, goals=["Private optional goal"], use_optional_fields=True)
    _, pending = submit(commerce, owner)
    profile(client, owner, use_optional_fields=False)
    assert (
        client.get("/api/v1/jobs/" + pending.json()["job_id"], headers=owner).json()["status"]
        == "cancelled"
    )
    assert balance(commerce, owner)["available"] == 3


def test_periodic_research_ignores_email_optout_and_expires(commerce, monkeypatch):
    client, engine, config = commerce
    owner, _ = user(commerce)
    purchase(commerce, owner, plan="demo_monthly")
    _, accepted = submit(commerce, owner)
    drain(commerce)
    report_for(commerce, owner, accepted.json())
    subscription = client.get("/api/v1/billing/history", headers=owner).json()["subscriptions"][0]
    topic_id = accepted.json()["user_topic_id"]
    schedule = client.post(
        "/api/v1/research/topics/" + topic_id + "/schedule",
        headers=owner,
        json={"subscription_id": subscription["id"], "explicit_periodic_consent": True},
    )
    assert schedule.status_code == 200, schedule.text
    assert (
        client.put("/api/v1/me/notification-preferences", headers=owner, json={}).status_code == 200
    )
    # Scheduler cursor is mutable; subscription/grant periods themselves remain immutable.
    with Session(engine) as session:
        topic = session.get(UserResearchTopic, UUID(topic_id))
        topic.next_run_at = utcnow() - timedelta(seconds=1)
        session.commit()
    assert schedule_paid(engine, config)["queued"] == 1
    assert schedule_paid(engine, config)["queued"] == 0
    drain(commerce)
    assert balance(commerce, owner)["consumed"] == 2
    notices = client.get("/api/v1/notifications", headers=owner).json()
    assert any(n["title"] == "周期研究报告已完成" for n in notices)
    assert client.get("/api/v1/me/mail-deliveries", headers=owner).json() == []
    cancel = client.post(
        "/api/v1/billing/subscriptions/" + subscription["id"] + "/cancel", headers=owner
    )
    assert cancel.status_code == 200 and cancel.json()["cancel_at_period_end"]
    with Session(engine) as session:
        assert session.get(PaidSubscription, UUID(subscription["id"])).status == "active"
    import infra.billing as billing

    monkeypatch.setattr(billing, "utcnow", lambda: utcnow() + timedelta(days=31))
    current = balance(commerce, owner)
    assert current["available"] == 0 and current["revoked"] == 8 and current["consumed"] == 2
    with Session(engine) as session:
        assert session.get(PaidSubscription, UUID(subscription["id"])).status == "expired"
        assert not session.get(UserResearchTopic, UUID(topic_id)).periodic_enabled


def test_unused_refund_revokes_pending_and_used_refund_is_not_faked(commerce):
    client, _, _ = commerce
    owner, _ = user(commerce)
    checkout = purchase(commerce, owner)
    _, pending = submit(commerce, owner)
    path = "/api/v1/billing/checkouts/" + checkout["checkout_id"] + "/refund"
    for duplicate in (False, True):
        response = client.post(path, headers=owner, json=CONSENT)
        assert response.status_code == 200 and response.json()["duplicate"] is duplicate, (
            response.text
        )
    assert (
        client.get("/api/v1/jobs/" + pending.json()["job_id"], headers=owner).json()["status"]
        == "cancelled"
    )
    assert balance(commerce, owner)["available"] == 0 and balance(commerce, owner)["revoked"] == 3
    checkout = purchase(commerce, owner)
    _, accepted = submit(commerce, owner)
    drain(commerce)
    report_for(commerce, owner, accepted.json())
    assert (
        client.post(
            "/api/v1/billing/checkouts/" + checkout["checkout_id"] + "/refund",
            headers=owner,
            json=CONSENT,
        ).status_code
        == 409
    )
    assert balance(commerce, owner)["consumed"] == 1


@pytest.mark.parametrize("same_scope", [True, False])
def test_concurrent_submissions_do_not_overspend(commerce, same_scope):
    from concurrent.futures import ThreadPoolExecutor

    client, engine, _ = commerce
    owner, _ = user(commerce)
    purchase(commerce, owner)
    scopes = [SCOPE, SCOPE if same_scope else {**SCOPE, "focus": "integration_constraints"}]
    quotes = [client.post("/api/v1/research/quote", headers=owner, json=s).json() for s in scopes]
    with ThreadPoolExecutor(max_workers=2) as pool:
        responses = list(
            pool.map(
                lambda pair: client.post(
                    "/api/v1/research/submit",
                    headers={**owner, "Idempotency-Key": pair[0]},
                    json={"quote_id": pair[1]["quote_id"], "accept_usage_rules": True},
                ),
                zip(["concurrent-a", "concurrent-b"], quotes, strict=True),
            )
        )
    assert all(r.status_code == 202 for r in responses), [r.text for r in responses]
    assert (responses[0].json()["job_id"] == responses[1].json()["job_id"]) is same_scope
    assert balance(commerce, owner)["reserved"] == (1 if same_scope else 2)
    with Session(engine) as session:
        assert session.scalar(select(func.count()).select_from(PaidResearchReservation)) == (
            1 if same_scope else 2
        )


def test_database_conservation_append_only_and_unverified_grant_rejected(commerce):
    client, engine, _ = commerce
    owner, user_id = user(commerce)
    purchase(commerce, owner)
    for statement in [
        "UPDATE commerce_ledger SET units_delta=999",
        "UPDATE research_credit_grants SET available=99",
        "UPDATE commerce_checkouts SET plan='{}'",
        "UPDATE commerce_payment_events SET event_type='checkout.refunded'",
    ]:
        with engine.begin() as connection:
            with pytest.raises(DatabaseError):
                connection.execute(text(statement))
    pending = client.post(
        "/api/v1/billing/checkout",
        headers={**owner, "Idempotency-Key": "unverified"},
        json={**CONSENT, "plan_code": "demo_pack"},
    ).json()
    with engine.begin() as connection:
        with pytest.raises(DatabaseError):
            connection.execute(
                ResearchCreditGrant.__table__.insert().values(
                    id=uuid4(),
                    user_id=user_id,
                    checkout_id=UUID(pending["checkout_id"]),
                    units=3,
                    available=3,
                    reserved=0,
                    consumed=0,
                    revoked=0,
                    expires_at=utcnow() + timedelta(days=30),
                )
            )


def test_only_one_remaining_credit_cannot_be_reserved_twice(commerce):
    from concurrent.futures import ThreadPoolExecutor

    client, _, _ = commerce
    owner, _ = user(commerce)
    purchase(commerce, owner)
    for geography in ("global", "CN"):
        _, accepted = submit(commerce, owner, {**SCOPE, "geography": geography})
        drain(commerce)
        report_for(commerce, owner, accepted.json())
    assert balance(commerce, owner)["available"] == 1
    quotes = [
        client.post(
            "/api/v1/research/quote",
            headers=owner,
            json={**SCOPE, "focus": "integration_constraints", "geography": geo},
        ).json()
        for geo in ("global", "CN")
    ]
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(
            pool.map(
                lambda q: client.post(
                    "/api/v1/research/submit",
                    headers={**owner, "Idempotency-Key": uuid4().hex},
                    json={"quote_id": q["quote_id"], "accept_usage_rules": True},
                ),
                quotes,
            )
        )
    assert sorted(r.status_code for r in results) == [202, 409], [r.text for r in results]
    assert balance(commerce, owner)["available"] == 0 and balance(commerce, owner)["reserved"] == 1


def test_quote_expiry_consent_owner_and_expired_lease_release(commerce, monkeypatch):
    client, engine, config = commerce
    owner, _ = user(commerce)
    other, _ = user(commerce)
    purchase(commerce, owner)
    quote = client.post("/api/v1/research/quote", headers=owner, json=SCOPE).json()
    body = {"quote_id": quote["quote_id"], "accept_usage_rules": True}
    assert (
        client.post(
            "/api/v1/research/submit",
            headers={**other, "Idempotency-Key": "wrong-owner"},
            json=body,
        ).status_code
        == 404
    )
    assert (
        client.post(
            "/api/v1/research/submit",
            headers={**owner, "Idempotency-Key": "no-consent"},
            json={**body, "accept_usage_rules": 1},
        ).status_code
        == 422
    )
    import infra.paid_research as paid

    with monkeypatch.context() as patcher:
        patcher.setattr(paid, "utcnow", lambda: utcnow() + timedelta(minutes=16))
        assert (
            client.post(
                "/api/v1/research/submit",
                headers={**owner, "Idempotency-Key": "expired-quote"},
                json=body,
            ).status_code
            == 409
        )
    assert balance(commerce, owner)["available"] == 3
    _, response = submit(commerce, owner)
    with Session(engine) as session:
        job = session.get(Job, UUID(response.json()["job_id"]))
        job.status = "running"
        job.attempts = config.job_max_attempts
        job.lease_until = utcnow() - timedelta(seconds=1)
        session.commit()
    drain(commerce)
    assert balance(commerce, owner)["available"] == 3 and balance(commerce, owner)["reserved"] == 0
