"""Frozen synthetic fault-injection suite, separate from real-world forecast accuracy."""

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

from prediction_engine.adjudication.rules import adjudicate
from prediction_engine.contracts.models import M2DraftV1, ResearchSnapshotV1
from prediction_engine.critic.checkers import review_draft
from prediction_engine.forecasting.workflow import build_forecast_draft, hashed, mock_narrative

ROOT = Path(__file__).resolve().parents[1]
RUN_ID = UUID("1501f3ad-9646-43ec-8332-fa39974945f5")
FUTURE = datetime(2021, 1, 1, tzinfo=UTC)
NOW = datetime(2026, 11, 1, tzinfo=UTC)


def fixture(case: str) -> tuple[M2DraftV1, ResearchSnapshotV1]:
    snapshot = ResearchSnapshotV1.model_validate_json(
        (ROOT / "fixtures/m3/base_snapshot.v1.json").read_text()
    )
    draft = build_forecast_draft(RUN_ID, snapshot, mock_narrative(snapshot), "synthetic-m3-v1")
    if case in {"clean", "reasonable_alternative"}:
        return draft, snapshot
    if case in {"future_source", "unknown_source_time", "mixed_source_label"}:
        source_id = next(
            c.source_version_id for c in snapshot.claims if c.claim_id in draft.evidence_claim_ids
        )
        source = next(s for s in snapshot.sources if s.source_version_id == source_id)
        update = {
            "future_source": {"available_at": FUTURE},
            "unknown_source_time": {"available_at": None},
            "mixed_source_label": {"label": "REAL"},
        }[case]
        snapshot = snapshot.model_copy(
            update={
                "sources": tuple(
                    s.model_copy(update=update)
                    if s.source_version_id == source.source_version_id
                    else s
                    for s in snapshot.sources
                )
            }
        )
    elif case in {
        "unverified_fact",
        "opinion_as_fact",
        "bad_quote",
        "future_claim",
        "wrong_claim_group",
        "mixed_claim_label",
    }:
        claim = next(c for c in snapshot.claims if c.claim_id in draft.evidence_claim_ids)
        updates = {
            "unverified_fact": {"verification_status": "unverified"},
            "opinion_as_fact": {"claim_kind": "opinion"},
            "bad_quote": {"quote": "invented quotation"},
            "future_claim": {"known_at": FUTURE},
            "wrong_claim_group": {"source_group_id": uuid4()},
            "mixed_claim_label": {"label": "REAL"},
        }
        snapshot = snapshot.model_copy(
            update={
                "claims": tuple(
                    c.model_copy(update=updates[case]) if c.claim_id == claim.claim_id else c
                    for c in snapshot.claims
                )
            }
        )
    elif case in {"future_vintage", "future_period", "publication_after_cutoff"}:
        row = snapshot.observations[-1]
        updates = {
            "future_vintage": {"available_at": FUTURE},
            "future_period": {"period_end": FUTURE},
            "publication_after_cutoff": {"published_at": FUTURE},
        }
        snapshot = snapshot.model_copy(
            update={
                "observations": (*snapshot.observations[:-1], row.model_copy(update=updates[case]))
            }
        )
    elif case == "future_case_outcome":
        case_row = next(c for c in snapshot.cases if c.outcomes)
        modified = case_row.model_copy(
            update={"outcomes": (case_row.outcomes[0].model_copy(update={"known_at": FUTURE}),)}
        )
        snapshot = snapshot.model_copy(
            update={
                "cases": tuple(
                    modified if c.case_id == case_row.case_id else c for c in snapshot.cases
                )
            }
        )
    elif case == "duplicate_sources":
        group = snapshot.sources[0].source_group_id
        snapshot = snapshot.model_copy(
            update={
                "sources": tuple(
                    s.model_copy(update={"source_group_id": group}) for s in snapshot.sources
                ),
                "claims": tuple(
                    c.model_copy(update={"source_group_id": group}) for c in snapshot.claims
                ),
            }
        )
    else:
        updates: dict[str, Any] = {
            "missing_citation": {"evidence_claim_ids": (uuid4(),)},
            "no_evidence": {"evidence_claim_ids": ()},
            "omitted_counter": {"contradiction_claim_ids": ()},
            "counter_as_support": {
                "evidence_claim_ids": (*draft.evidence_claim_ids, *draft.contradiction_claim_ids)
            },
            "no_failure_case": {
                "analogies": tuple(
                    a.model_copy(
                        update={
                            "known_outcomes": tuple(
                                e for e in a.known_outcomes if e.outcome_category != "failure"
                            )
                        }
                    )
                    for a in draft.analogies
                )
            },
            "no_analogy": {"analogies": ()},
            "unsupported_analogy": {
                "analogies": tuple(
                    a.model_copy(update={"mechanism_overlap": ("unsupported",)})
                    for a in draft.analogies
                )
            },
            "transfer_gap": {
                "analogies": tuple(
                    a.model_copy(update={"key_differences": ()}) for a in draft.analogies
                )
            },
            "causal_gap": {"mechanism_chain": ()},
            "no_reverse_path": {
                "mechanism_chain": tuple(e for e in draft.mechanism_chain if e.sign != "negative")
            },
            "causal_leap": {
                "mechanism_chain": tuple(
                    e.model_copy(update={"conditions": ()}) for e in draft.mechanism_chain
                )
            },
            "missing_path": {"scenarios": draft.scenarios[:2]},
            "no_falsifier": {"falsification_conditions": ()},
            "baseline_wrong": {
                "baseline": draft.baseline.model_copy(update={"projected_value": 999})
            },
            "baseline_unit": {"baseline": draft.baseline.model_copy(update={"unit": "wrong"})},
            "wrong_geography": {
                "target": draft.target.model_copy(update={"geography": "wrong"})
                if draft.target
                else None
            },
            "no_target": {"target": None},
            "expired_target": {
                "target": draft.target.model_copy(
                    update={"target_end_at": datetime(2019, 1, 1, tzinfo=UTC)}
                )
                if draft.target
                else None
            },
            "wrong_cutoff": {"research_as_of": datetime(2020, 5, 31, tzinfo=UTC)},
        }[case]
        draft = draft.model_copy(update=updates)
    return draft, snapshot


def run_suite() -> dict[str, Any]:
    corpus = json.loads((ROOT / "fixtures/m3/critic_cases.v1.json").read_text())
    records = []
    for case in corpus["cases"]:
        draft, snapshot = fixture(case["id"])
        report = review_draft(uuid4(), draft, snapshot)
        decision = adjudicate(report, 0, NOW)
        codes = {(f.code, f.severity) for f in report.findings}
        passed = (case["code"], case["severity"]) in codes and decision.decision == case["decision"]
        records.append(
            {
                **case,
                "passed": passed,
                "actual_decision": decision.decision,
                "findings": [{"code": f.code, "severity": f.severity} for f in report.findings],
                "a_hash": hashed(draft.model_dump(mode="json")),
                "critic_ms": report.duration_ms,
                "external_model_calls": 0,
            }
        )
    return {
        "testset_version": corpus["testset_version"],
        "review_status": corpus["review_status"],
        "label": "DEMO",
        "mode": "synthetic",
        "cases": records,
        "total": len(records),
        "passed": sum(r["passed"] for r in records),
        "real_forward_accuracy": None,
        "limits": [
            "故障题组由代码作者逐项编写，尚未经独立人工评审；不冒充历史预测成绩",
            "结构性缺陷检出不等于语义事实审查或真实准确率；无法完全排除基础模型未来知识",
        ],
    }


def main() -> None:
    report = run_suite()
    path = ROOT / "docs/evaluations/M3-synthetic-critic.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(f"M3 synthetic critics: {report['passed']}/{report['total']}; no real accuracy claim")
    if report["passed"] != report["total"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
