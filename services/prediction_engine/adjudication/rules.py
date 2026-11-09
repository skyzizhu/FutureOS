"""Versioned deterministic decisions; no replacement forecast or tool authority."""

from datetime import datetime
from typing import Literal
from uuid import uuid5

from prediction_engine.contracts.models import CriticReportV1, ReviewDecisionV1


def adjudicate(report: CriticReportV1, revision_number: int, now: datetime) -> ReviewDecisionV1:
    verified = tuple(f for f in report.findings if f.verification_status == "verified")
    levels = {f.severity for f in verified}
    pending = any(
        f.verification_status == "pending" and f.severity in {"L2", "L3"} for f in report.findings
    )
    decision: Literal["accept", "annotate", "targeted_research", "block", "research_only"] = (
        "accept"
    )
    if set(report.checkers_completed) != {
        "evidence",
        "historical",
        "causal",
        "scenario",
        "temporal_resolution",
    }:
        decision = "block"
    elif "L3" in levels:
        decision = "block"
    elif "L2" in levels or pending:
        decision = "targeted_research"
    elif "L1" in levels:
        decision = "annotate"
    if revision_number >= 2 and decision in {"block", "targeted_research"}:
        decision = "research_only"
    return ReviewDecisionV1(
        decision_id=uuid5(report.critic_run_id, "adjudication"),
        critic_run_id=report.critic_run_id,
        draft_id=report.draft_id,
        decision=decision,
        publication_allowed=decision in {"accept", "annotate"},
        verified_finding_ids=tuple(f.finding_id for f in verified),
        decided_at=now,
        rationale={
            "accept": "全部检查完成，无实质问题",
            "annotate": "仅补充合理竞争解释，保留原结论",
            "targeted_research": "重要问题需主引擎定向核实，当前不可发布",
            "block": "已核实关键错误或审查不完整，阻断发布",
            "research_only": "两轮复核仍未消除关键问题，转研究假设/人工处理",
        }[decision],
    )
