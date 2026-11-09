from datetime import timedelta
from uuid import uuid4

import pytest
from prediction_engine.contracts.models import ChangeAssertionV1, MonitorPolicyV1
from prediction_engine.turning_points.rules import classify

from scripts.m3_eval_suite import fixture


def evidence(snapshot, count=1, duplicate=False):
    template = snapshot.claims[0]
    added = tuple(
        template.model_copy(
            update={
                "claim_id": uuid4(),
                "source_group_id": uuid4(),
                "relation": "contradicts",
                "claim_text": "Same verified counterclaim"
                if duplicate
                else f"Independent new fact {index}",
            }
        )
        for index in range(count)
    )
    return snapshot.model_copy(update={"claims": (*snapshot.claims, *added)}), added


def test_t0_metadata_and_reprints_t1_one_source_t2_independent():
    _, old = fixture("clean")
    policy = MonitorPolicyV1()
    assert classify(old, old, policy).level == "T0"
    now = old.model_copy(
        update={
            "request": old.request.model_copy(
                update={"research_as_of": old.request.research_as_of + timedelta(days=1)}
            )
        }
    )
    assert (
        classify(old, now, policy).delta.fingerprint == classify(old, old, policy).delta.fingerprint
    )
    new, _ = evidence(old)
    assert classify(old, new, policy).level == "T1"
    new, _ = evidence(old, 2)
    assert classify(old, new, policy).level == "T2"
    reprints, _ = evidence(old, 3, duplicate=True)
    decision = classify(old, reprints, policy)
    assert decision.level == "T1" and len(decision.delta.duplicate_claim_ids) == 2
    copied = old.claims[0].model_copy(update={"claim_id": uuid4(), "source_group_id": uuid4()})
    assert (
        classify(old, old.model_copy(update={"claims": (*old.claims, copied)}), policy).level
        == "T0"
    )


def test_t3_requires_existing_prior_and_verified_evidence_references():
    _, old = fixture("clean")
    new, added = evidence(old)
    assertion = ChangeAssertionV1(
        kind="critical_assumption_broken",
        prior_claim_id=old.claims[0].claim_id,
        claim_ids=(added[0].claim_id,),
        verification_note="Admin checked literal original and contradictory follow-up",
    )
    assert classify(old, new, MonitorPolicyV1(), (assertion,)).level == "T3"
    with pytest.raises(ValueError, match="CRITICAL_ASSERTION_NOT_SUPPORTED"):
        classify(
            old, new, MonitorPolicyV1(), (assertion.model_copy(update={"prior_claim_id": uuid4()}),)
        )
    with pytest.raises(ValueError, match="ASSERTION_EVIDENCE_MISSING"):
        classify(
            old, new, MonitorPolicyV1(), (assertion.model_copy(update={"claim_ids": (uuid4(),)}),)
        )


def test_indicator_threshold_is_explicit_and_requires_consecutive_periods():
    _, old = fixture("clean")
    template = old.observations[-1]
    changed = tuple(
        template.model_copy(
            update={
                "observation_id": uuid4(),
                "period_end": template.period_end + timedelta(days=i + 1),
                "value": template.value + 20,
            }
        )
        for i in range(2)
    )
    new = old.model_copy(update={"observations": (*old.observations, *changed)})
    assert classify(old, new, MonitorPolicyV1()).level == "T1"
    policy = MonitorPolicyV1(indicator_absolute_delta=10, consecutive_periods=2)
    assert classify(old, new, policy).level == "T2"
    single_period = new.model_copy(
        update={
            "observations": (
                *old.observations,
                changed[0],
                changed[1].model_copy(update={"period_end": changed[0].period_end}),
            )
        }
    )
    assert classify(old, single_period, policy).level == "T1"
