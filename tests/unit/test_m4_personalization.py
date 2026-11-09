from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from prediction_engine.contracts.models import (
    ProfileInputV1,
    ProfileSnapshotV1,
    PublishedForecastV1,
)
from prediction_engine.decision_value.rules import evaluate_value
from prediction_engine.forecasting.workflow import hashed
from prediction_engine.personalization.matcher import match_forecast
from prediction_engine.personalization.taxonomy import rows
from prediction_engine.reporting.builder import build_private_report
from pydantic import ValidationError

from scripts.m3_eval_suite import fixture

NOW = datetime(2026, 11, 1, tzinfo=UTC)


def inputs(label="REAL", **changes):
    draft, _ = fixture("clean")
    target = draft.target.model_copy(
        update={
            "target_start_at": NOW + timedelta(days=1),
            "target_end_at": NOW + timedelta(days=60),
            "geography": "global",
        }
    )
    draft = draft.model_copy(update={"target": target, "label": label})
    version = PublishedForecastV1(
        version_id=uuid4(),
        forecast_id=uuid4(),
        version_num=1,
        draft_id=draft.draft_id,
        review_id=uuid4(),
        label=label,
        published_at=NOW,
        version_hash="0" * 64,
        change_reason="Synthetic unit fixture",
        body=draft,
    )
    profile = ProfileInputV1(industry_l1_code="technology", industry_l2_code="software", **changes)
    snapshot = ProfileSnapshotV1(
        snapshot_id=uuid4(),
        user_id=uuid4(),
        profile=profile,
        profile_revision=1,
        consent_scope="optional_fields" if profile.use_optional_fields else "industry_only",
        created_at=NOW,
        snapshot_hash="0" * 64,
    )
    return snapshot, version


def test_only_two_industry_fields_required_and_no_sensitive_stereotype_inputs():
    profile = ProfileInputV1(industry_l1_code="technology", industry_l2_code="software")
    assert not profile.goals and not profile.use_optional_fields
    with pytest.raises(ValidationError):
        ProfileInputV1(industry_l1_code="technology", industry_l2_code="clinical")
    with pytest.raises(ValidationError):
        ProfileInputV1(industry_l1_code="technology", industry_l2_code="software", gender="ignored")
    children = [entry for entry in rows() if entry["level"] == 2]
    assert all(
        any(parent["code"] == entry["parent_code"] and parent["level"] == 1 for parent in rows())
        for entry in children
    )


@pytest.mark.parametrize(
    "consent,budget,allowed,expected",
    [
        (False, 60, True, "observe"),
        (True, None, True, "observe"),
        (True, 0, True, "observe"),
        (True, 60, False, "observe"),
        (True, 60, True, "prepare"),
    ],
)
def test_explicit_budget_and_optional_consent_gate(consent, budget, allowed, expected):
    snapshot, version = inputs(
        goals=("学习工具",),
        tasks=("维护软件测试流程",),
        use_optional_fields=consent,
        allow_low_cost_experiments=allowed,
        available_minutes_per_week=budget,
    )
    result = match_forecast(snapshot, version, ("technology",), uuid4(), NOW)
    assert result.decision.decision_priority == expected
    assert result.mechanism_path and result.relevance_reason


@pytest.mark.parametrize(
    "risk,costly,reversible", [(True, False, True), (False, True, True), (False, False, False)]
)
def test_high_risk_costly_irreversible_never_promoted(risk, costly, reversible):
    decision = evaluate_value(
        uuid4(), "high", NOW, NOW + timedelta(days=60), True, 120, risk, "REAL", reversible, costly
    )
    assert decision.decision_priority != "prepare"


def test_low_relevance_not_core_and_raw_profile_does_not_leak():
    snapshot, version = inputs(
        use_optional_fields=True,
        occupation_text="PRIVATE OCCUPATION",
        goals=("PRIVATE GOAL",),
        tasks=("PRIVATE TASK",),
    )
    before = hashed(version.model_dump(mode="json"))
    report = build_private_report(uuid4(), uuid4(), snapshot, ((version, ("health",)),), NOW)
    assert (
        report.primary_impacts == ()
        and report.recommendations == ()
        and len(report.observation_only) == 1
    )
    assert "PRIVATE GOAL" not in report.model_dump_json()
    assert hashed(version.model_dump(mode="json")) == before


def test_demo_and_expired_targets_do_not_become_real_action_advice():
    snapshot, version = inputs(
        label="DEMO",
        use_optional_fields=True,
        available_minutes_per_week=120,
        allow_low_cost_experiments=True,
    )
    report = build_private_report(uuid4(), uuid4(), snapshot, ((version, ("technology",)),), NOW)
    assert all(action.priority != "prepare" for action in report.recommendations)
    assert report.label == "DEMO"
    expired = version.model_copy(
        update={
            "body": version.body.model_copy(
                update={
                    "target": version.body.target.model_copy(
                        update={"target_end_at": NOW - timedelta(days=1)}
                    )
                }
            )
        }
    )
    result = match_forecast(snapshot, expired, ("technology",), uuid4(), NOW)
    assert result.decision.decision_priority == "no_action"


def test_recommendation_required_fields_stop_cost_alternatives_and_fixed_versions():
    snapshot, version = inputs(
        goals=("学习工具",),
        tasks=("维护软件测试流程",),
        use_optional_fields=True,
        available_minutes_per_week=60,
        allow_low_cost_experiments=True,
    )
    report = build_private_report(uuid4(), uuid4(), snapshot, ((version, ("technology",)),), NOW)
    action = report.recommendations[0]
    assert action.priority == "prepare"
    assert action.forecast_version_ids == (version.version_id,)
    assert (
        action.tradeoffs
        and action.alternatives
        and action.success_metrics
        and action.stop_or_revisit_condition
    )
    assert "辞职或高成本转行" in action.suppressed_high_risk_actions
    assert report.profile_snapshot_id == snapshot.snapshot_id
