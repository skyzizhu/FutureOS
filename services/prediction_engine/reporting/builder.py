"""Pure report assembly from fixed approved versions, with explicit personal assumptions."""

from datetime import datetime, timedelta
from uuid import UUID, uuid5

from prediction_engine.contracts.models import (
    PrivateReportV1,
    ProfileSnapshotV1,
    PublishedForecastV1,
    RecommendationV1,
)
from prediction_engine.personalization.matcher import match_forecast


def build_private_report(
    report_id: UUID,
    version_id: UUID,
    snapshot: ProfileSnapshotV1,
    forecasts: tuple[tuple[PublishedForecastV1, tuple[str, ...]], ...],
    now: datetime,
) -> PrivateReportV1:
    if not forecasts or len({v.label for v, _ in forecasts}) != 1:
        raise ValueError("REPORT_APPROVED_FORECASTS_REQUIRED")
    impacts = tuple(
        match_forecast(snapshot, forecast, domains, version_id, now)
        for forecast, domains in forecasts
    )
    primary = tuple(i for i in impacts if i.relevance != "low")
    observation = tuple(i for i in impacts if i.relevance == "low")
    recommendations = []
    for impact in primary[:3]:
        priority = impact.decision.decision_priority
        action = (
            "选取一项非敏感、可回滚的重复任务，离线记录质量、耗时与校验成本；不接入生产数据"
            if priority == "prepare"
            else "保留观察：先核对版本变化与自身任务是否适用，暂不据此调整工作或支出"
        )
        recommendations.append(
            RecommendationV1(
                recommendation_id=uuid5(impact.impact_id, "recommendation"),
                impact_id=impact.impact_id,
                action=action,
                rationale="；".join(impact.decision.reasons),
                forecast_version_ids=(impact.forecast_version_id,),
                applicability="仅在来源口径与本人任务匹配、具备可停止条件时适用",
                suggested_start=now,
                review_date=now + timedelta(days=14),
                estimated_effort_and_cost="不新增付费支出；可选验证不超过每周30分钟且以用户预算为上限",
                tradeoffs="验证需要额外时间，工具表现不能替代原流程质量检查",
                alternatives=("维持现有流程，只阅读来源或等待新证据", "不参加实验，继续观察"),
                success_metrics=("记录同一任务的质量、耗时和校验成本；样本不足不推断收益",),
                stop_or_revisit_condition="超出预算、质量下降、涉及敏感资料或验证源失效时立即停止并重新核对",
                priority=priority,
                personalization_assumptions=(
                    "只使用画像快照中已授权的行业/目标/任务",
                    "未假定收入、性别、年龄或能力",
                ),
                suppressed_high_risk_actions=(
                    "辞职或高成本转行",
                    "借贷、买卖资产或集中投资",
                    "自行调整医疗治疗",
                ),
            )
        )
    label = forecasts[0][0].label
    return PrivateReportV1(
        report_id=report_id,
        report_version_id=version_id,
        user_id=snapshot.user_id,
        version_num=1,
        profile_snapshot_id=snapshot.snapshot_id,
        profile_revision=snapshot.profile_revision,
        label=label,
        title="个人未来观察报告" + ("（合成演示）" if label == "DEMO" else ""),
        created_at=now,
        forecast_version_ids=tuple(v.version_id for v, _ in forecasts),
        primary_impacts=primary,
        observation_only=observation,
        recommendations=tuple(recommendations),
        evidence_gaps=("个人任务尚未测量", "没有地区/岗位的可靠统计时不推断个人结果")
        + (() if primary else ("暂无足够直接关联的过审预测，不生成核心行动建议",)),
        limitations=(
            "DEMO 为合成流程演示，不能据此采取现实行动"
            if label == "DEMO"
            else "真实前瞻尚无到期成绩，不能宣称准确率",
            "报告固定引用生成时的画像与预测版本；后续编辑不会覆盖本版",
            "没有咨询或收益保证；建议可以选择不执行",
        ),
    )
