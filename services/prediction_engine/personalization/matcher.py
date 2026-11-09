"""Map a frozen world mechanism to a consented minimum profile; no private data to LLMs."""

from datetime import datetime
from typing import Literal
from uuid import UUID, uuid5

from prediction_engine.contracts.models import (
    PersonalAssessmentV1,
    ProfileSnapshotV1,
    PublishedForecastV1,
)
from prediction_engine.decision_value.rules import evaluate_value
from prediction_engine.personalization.taxonomy import industry


def match_forecast(
    snapshot: ProfileSnapshotV1,
    version: PublishedForecastV1,
    domain_tags: tuple[str, ...],
    report_id: UUID,
    now: datetime,
) -> PersonalAssessmentV1:
    profile = snapshot.profile
    definition = industry(profile.industry_l1_code, profile.industry_l2_code)
    matched = tuple(sorted(set(definition["domain_tags"]) & set(domain_tags)))
    target = version.body.target
    assert target is not None
    relevance: Literal["low", "medium", "high"] = "medium" if matched else "low"
    # Task vocabulary is only an extra constraint; industry, mechanism and geography
    # must already match. Nonempty free text alone cannot establish a personal link.
    task_text = " ".join(profile.tasks).casefold()
    task_fit = any(
        word in task_text
        for word in (
            "开发",
            "编码",
            "测试",
            "流程",
            "质量",
            "维护",
            "验证",
            "code",
            "test",
            "workflow",
            "quality",
        )
    )
    if matched and profile.use_optional_fields and task_fit and profile.goals:
        relevance = "high"
    # Narrow release events do not establish broad labour or productivity impacts.
    if target.metric_definition == "playwright_stable_release_occurs":
        relevance = "medium" if profile.industry_l2_code in {"software", "quality"} else "low"
    region = profile.country_code or profile.region
    if (
        profile.use_optional_fields
        and region
        and target.geography
        not in {
            "global",
            "global public repository",
            region,
        }
    ):
        relevance = "low"
    impact_id = uuid5(report_id, "impact:" + str(version.version_id))
    domain_risk = bool(set(domain_tags) & {"health", "macro_finance", "housing"})
    decision = evaluate_value(
        impact_id,
        relevance,
        now,
        target.target_end_at,
        bool(
            profile.use_optional_fields
            and profile.allow_low_cost_experiments
            and task_fit
            and profile.goals
        ),
        profile.available_minutes_per_week if profile.use_optional_fields else None,
        domain_risk,
        version.label,
    )
    path = (
        (
            f"固定预测目标：{target.metric_definition}",
            f"条件机制：{version.body.fusions[0].mechanism}",
            f"关联任务范围：{definition['label']}",
            "需要本人用实际任务验证后才能推断个人影响",
        )
        if matched
        else ("预测的地区/领域/机制尚未连到当前行业任务",)
    )
    return PersonalAssessmentV1(
        impact_id=impact_id,
        user_id=snapshot.user_id,
        profile_snapshot_id=snapshot.snapshot_id,
        forecast_version_id=version.version_id,
        relevance=relevance,
        mechanism_path=path,
        relevance_reason=(
            "行业领域存在机制交集；不是仅凭职位关键词推断失业或收益"
            if matched
            else "没有可验证的直接个人影响路径"
        ),
        positive_impacts=("若适用条件经任务验证成立，可能带来流程调整机会；尚无个人效果证据",)
        if matched
        else (),
        negative_impacts=("工具迁移、校验和学习可能增加时间成本；不能假定净收益",)
        if matched
        else (),
        applicable_conditions=(
            target.population_scope,
            target.geography,
            "须与用户实际任务口径一致",
        ),
        uncertainty="个性化判断不等于世界预测事实；没有个人因果收益或校准概率",
        matched_domains=matched,
        decision=decision,
    )
