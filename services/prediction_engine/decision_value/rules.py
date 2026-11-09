"""Explainable cost/reversibility gates, independent of popularity and model confidence."""

from datetime import datetime
from typing import Literal
from uuid import UUID

from prediction_engine.contracts.models import DecisionValueV1


def evaluate_value(
    impact_id: UUID,
    relevance: Literal["low", "medium", "high"],
    now: datetime,
    due_at: datetime,
    allow_experiment: bool,
    minutes: int | None,
    high_risk_domain: bool,
    label: str,
    reversible: bool = True,
    costly: bool = False,
) -> DecisionValueV1:
    priority: Literal["prepare", "observe", "no_action"] = "observe"
    reasons = ["机制关联只说明需要观察，不证明对个人的收益或损失"]
    if relevance == "low":
        priority = "no_action"
        reasons.append("缺少个人任务的直接传播路径，移出核心建议")
    elif due_at <= now:
        priority = "no_action"
        reasons.append("目标窗口已结束，需要到期结果或更新版本")
    elif high_risk_domain or costly or not reversible:
        reasons.append("高成本、不可逆或高风险领域，禁止直接行动建议")
    elif label == "REAL" and allow_experiment and minutes is not None and minutes >= 30:
        priority = "prepare"
        reasons.append("用户允许小规模实验且明确提供时间预算，只推荐可停止的低成本验证")
    else:
        reasons.append("缺少明确预算/授权或为合成资料，仅观察，不推断现实行动")
    return DecisionValueV1(
        impact_id=impact_id,
        relevance=relevance,
        impact_window=due_at.isoformat(),
        actionability="low_cost_reversible_check"
        if priority == "prepare"
        else "observe_or_no_action",
        reversibility="high" if reversible else "low",
        cost_note="不建议新增付费投入；时间以用户预算为上限",
        decision_priority=priority,
        reasons=tuple(reasons),
        unknowns=("个人实际任务效果尚无独立测量",),
        reevaluate_if=("出现新过审版本或任务验证结果", "预算/目标改变或验证源失效"),
    )
