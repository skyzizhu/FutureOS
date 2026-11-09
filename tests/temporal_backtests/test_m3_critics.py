import json
from pathlib import Path
from uuid import uuid4

import pytest
from prediction_engine.adjudication.rules import adjudicate
from prediction_engine.critic.checkers import review_draft
from prediction_engine.forecasting.workflow import hashed

from scripts.m3_eval_suite import NOW, fixture, run_suite

CASES = json.loads(Path("fixtures/m3/critic_cases.v1.json").read_text())["cases"]


@pytest.mark.parametrize("case", CASES, ids=lambda c: c["id"])
def test_independent_critic_faults(case):
    draft, snapshot = fixture(case["id"])
    before = hashed(draft.model_dump(mode="json"))
    report = review_draft(uuid4(), draft, snapshot)
    assert any(f.code == case["code"] and f.severity == case["severity"] for f in report.findings)
    decision = adjudicate(report, 0, NOW)
    assert decision.decision == case["decision"]
    assert decision.publication_allowed == (case["severity"] == "L1")
    assert hashed(draft.model_dump(mode="json")) == before
    assert set(report.checkers_completed) == {
        "evidence",
        "historical",
        "causal",
        "scenario",
        "temporal_resolution",
    }


def test_revision_limit_and_pending_finding():
    draft, snapshot = fixture("baseline_wrong")
    report = review_draft(uuid4(), draft, snapshot)
    assert adjudicate(report, 2, NOW).decision == "research_only"
    finding = next(f for f in report.findings if f.severity == "L3")
    pending = finding.model_copy(update={"verification_status": "pending"})
    report = report.model_copy(update={"findings": (pending,)})
    assert adjudicate(report, 0, NOW).decision == "targeted_research"
    incomplete = report.model_copy(update={"checkers_completed": ("evidence",)})
    assert adjudicate(incomplete, 0, NOW).decision == "block"


def test_suite_keeps_failures_and_disclaims_accuracy():
    report = run_suite()
    assert report["total"] >= 20 and report["passed"] == report["total"]
    assert report["real_forward_accuracy"] is None
    assert "pending" in report["review_status"]
