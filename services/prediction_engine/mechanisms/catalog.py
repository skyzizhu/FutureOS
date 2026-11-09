"""Named, inspectable conditional recipes; never discovered causal truth."""

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Recipe:
    recipe_id: str
    capabilities: tuple[str, ...]
    mechanism: str
    steps: tuple[str, ...]
    bottlenecks: tuple[str, ...]
    opposing: tuple[str, ...]
    observables: tuple[str, ...]
    falsifiers: tuple[str, ...]


RECIPES = {
    "verifiable_agent": Recipe(
        "verifiable_agent",
        ("context_understanding", "tool_execution", "feedback_validation"),
        "上下文理解、工具执行与反馈校验互补，可能形成可验证的多步骤任务工作流",
        ("理解任务", "执行工具", "验证反馈", "受控试点采用"),
        ("长任务可靠性", "集成和治理成本"),
        ("演示收益不能推广到真实复杂任务", "治理和验证开销可能抵消效率收益"),
        ("预登记真实任务完成率", "独立试点采用与总成本"),
        ("真实任务可靠性未改善", "含验证开销的总成本持续高于现有流程"),
    ),
    "technology_diffusion": Recipe(
        "technology_diffusion",
        ("cost_decline", "reliability_improvement", "adoption_evidence"),
        "成本、可靠性与采用证据互补，可能缓解扩散约束",
        ("成本变化", "可靠性验证", "试点采用", "扩散或停滞"),
        ("总拥有成本", "采用和制度障碍"),
        ("成本下降可能被迁移成本抵消", "试点需求不代表持续需求"),
        ("独立采用统计", "全生命周期成本与留存"),
        ("采用率未持续变化", "全生命周期成本并未下降"),
    ),
}


def catalog_data() -> list[dict[str, object]]:
    return [asdict(RECIPES[key]) for key in sorted(RECIPES)]
