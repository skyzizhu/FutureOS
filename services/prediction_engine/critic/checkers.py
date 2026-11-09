"""Independent deterministic reviewers. Inputs only: no DB, tools, prompts or write capability."""

from time import perf_counter
from typing import Any, Literal
from uuid import UUID, uuid5

from prediction_engine.contracts.models import (
    CriticReportV1,
    M2DraftV1,
    ResearchSnapshotV1,
    ReviewFindingV1,
)
from prediction_engine.forecasting.workflow import hashed

CHECKERS = ("evidence", "historical", "causal", "scenario", "temporal_resolution")


def review_draft(review_id: UUID, draft: M2DraftV1, snapshot: ResearchSnapshotV1) -> CriticReportV1:
    """Structural facts are verified directly; semantic truth remains a manual M1 prerequisite."""
    started = perf_counter()
    findings: list[ReviewFindingV1] = []

    def add(
        checker: Any,
        code: str,
        severity: Literal["L0", "L1", "L2", "L3"],
        text: str,
        fields: tuple[str, ...],
        refs: tuple[UUID, ...] = (),
        verified: bool = True,
    ) -> None:
        findings.append(
            ReviewFindingV1(
                finding_id=uuid5(review_id, code),
                checker=checker,
                code=code,
                severity=severity,
                statement=text,
                verification_status="verified" if verified else "pending",
                source_refs=refs,
                affected_fields=fields,
                recommended_action="retain_and_annotate"
                if severity in {"L0", "L1"}
                else "targeted_main_engine_review",
            )
        )

    cutoff = draft.research_as_of
    sources = {s.source_version_id: s for s in snapshot.sources}
    claims = {c.claim_id: c for c in snapshot.claims}
    cited = set(draft.evidence_claim_ids) | set(draft.contradiction_claim_ids)
    if not draft.evidence_claim_ids or not cited <= claims.keys():
        add(
            "evidence",
            "MISSING_CITATION",
            "L3",
            "关键引用缺失或不在冻结证据中",
            ("evidence_claim_ids",),
        )
    invalid_claims = []
    for identifier in cited & claims.keys():
        claim = claims[identifier]
        source = sources.get(claim.source_version_id)
        if (
            source is None
            or claim.verification_status != "verified"
            or claim.claim_kind != "fact"
            or not claim.quote.strip()
            or claim.quote not in source.content
            or claim.source_group_id != source.source_group_id
            or claim.label != draft.label
            or source.label != draft.label
        ):
            invalid_claims.append(identifier)
    if invalid_claims:
        add(
            "evidence",
            "INVALID_FACT_OR_QUOTE",
            "L3",
            "引用与原文/核实状态/标签不一致",
            ("evidence_claim_ids",),
            tuple(invalid_claims),
        )
    groups = {
        claims[i].source_group_id
        for i in draft.evidence_claim_ids
        if i in claims and claims[i].relation == "supports"
    }
    if len(groups) < 2:
        add(
            "evidence",
            "DUPLICATE_OR_INSUFFICIENT_SOURCES",
            "L3",
            "独立支持来源不足；转载不能增加证据数量",
            ("fusions",),
        )
    expected_counter = {c.claim_id for c in snapshot.claims if c.relation == "contradicts"}
    if expected_counter - set(draft.contradiction_claim_ids):
        add(
            "evidence",
            "NEW_OR_OMITTED_COUNTEREVIDENCE",
            "L2",
            "独立库内查证发现未纳入的已核实反证",
            ("contradiction_claim_ids",),
            tuple(sorted(expected_counter - set(draft.contradiction_claim_ids))),
        )
    if any(claims[i].relation == "contradicts" for i in draft.evidence_claim_ids if i in claims):
        add(
            "evidence",
            "COUNTEREVIDENCE_AS_SUPPORT",
            "L3",
            "反证被错误标为支持证据",
            ("evidence_claim_ids",),
        )

    available_cases = {c.case_id: c for c in snapshot.cases}
    if not draft.analogies or not any(
        e.outcome_category == "failure" for a in draft.analogies for e in a.known_outcomes
    ):
        add(
            "historical",
            "NO_FAILURE_CASE",
            "L2",
            "缺少当时已知的失败类比，需定向核实",
            ("analogies",),
        )
    for analogy in draft.analogies:
        case = available_cases.get(analogy.case_id)
        if (
            case is None
            or not analogy.mechanism_overlap
            or not set(analogy.mechanism_overlap) <= set(case.mechanism_tags)
        ):
            add(
                "historical",
                "UNSUPPORTED_ANALOGY",
                "L2",
                "类比机制缺乏对应案例支持",
                ("analogies",),
            )
        if any(
            event.known_at > cutoff or case is None or event not in case.outcomes
            for event in analogy.known_outcomes
        ):
            add(
                "historical",
                "UNVERIFIED_OR_FUTURE_OUTCOME",
                "L3",
                "草稿类比包含不存在或未来才知道的结果",
                ("analogies",),
            )
        if not analogy.key_differences or not analogy.non_transferable:
            add(
                "historical",
                "ANALOGY_TRANSFER_GAP",
                "L2",
                "未说明制度差异或不可迁移部分",
                ("analogies",),
            )

    if not draft.mechanism_chain or any(
        not edge.evidence_claim_ids or not set(edge.evidence_claim_ids) <= claims.keys()
        for edge in draft.mechanism_chain
    ):
        add("causal", "CAUSAL_EVIDENCE_GAP", "L2", "机制链缺少中间节点或引用", ("mechanism_chain",))
    if not any(e.sign == "negative" for e in draft.mechanism_chain):
        add(
            "causal",
            "NO_COUNTERACTING_PATH",
            "L2",
            "未保留成本、替代或反向作用路径",
            ("mechanism_chain",),
        )
    if any(not e.conditions or not e.uncertainty for e in draft.mechanism_chain):
        add(
            "causal",
            "UNCONDITIONAL_CAUSAL_LEAP",
            "L2",
            "相关性不能直接作为无条件因果关系",
            ("mechanism_chain",),
        )
    if not draft.fusions or any(f.independent_source_groups > len(groups) for f in draft.fusions):
        add("causal", "FUSION_NOT_SUPPORTED", "L3", "融合不存在或夸大独立来源", ("fusions",))

    if {s.path for s in draft.scenarios} != {"base", "acceleration", "friction"}:
        add("scenario", "MISSING_COMPETING_PATH", "L2", "未包含三类竞争路径", ("scenarios",))
    if not draft.falsification_conditions or any(
        not s.falsification_conditions or not s.observable_signals for s in draft.scenarios
    ):
        add(
            "scenario",
            "NO_FALSIFIER",
            "L2",
            "缺少反证或可观察信号",
            ("scenarios", "falsification_conditions"),
        )
    if draft.raw_narrative.opposing_explanations:
        add(
            "scenario",
            "REASONABLE_ALTERNATIVE",
            "L1",
            "保留合理竞争解释；不同观点不构成事实否决",
            ("raw_narrative.opposing_explanations",),
        )

    temporal_refs = []
    for source in snapshot.sources:
        if (
            source.available_at is None
            or source.available_at > cutoff
            or (source.published_at is not None and source.published_at > cutoff)
        ):
            temporal_refs.append(source.source_version_id)
    for claim in snapshot.claims:
        if claim.known_at is None or claim.known_at > cutoff:
            temporal_refs.append(claim.claim_id)
    for row in snapshot.observations:
        if (
            row.available_at > cutoff
            or row.published_at > cutoff
            or row.period_end > cutoff
            or row.period_end > row.available_at
        ):
            temporal_refs.append(row.observation_id)
    for case in snapshot.cases:
        if case.cutoff_at > cutoff:
            temporal_refs.append(case.case_id)
        for event in (*case.contemporaneous, *case.outcomes):
            if event.known_at > cutoff:
                temporal_refs.append(event.source_version_id)
    if temporal_refs:
        add(
            "temporal_resolution",
            "FUTURE_INFORMATION_LEAK",
            "L3",
            "资料/统计版本/案例结果在研究时点尚不可获取",
            ("research_as_of", "baseline", "analogies"),
            tuple(sorted(set(temporal_refs))),
        )
    target = draft.target
    if (
        draft.kind != "draft_forecast"
        or target is None
        or not target.resolution_rule.strip()
        or target.target_end_at <= cutoff
        or (target.target_start_at < cutoff and draft.parent_version_id is None)
    ):
        add(
            "temporal_resolution",
            "UNRESOLVABLE_TARGET",
            "L3",
            "目标、期限或验证规则不满足发布条件",
            ("target", "kind"),
        )
    if target and target.target_type == "numeric":
        indicator = snapshot.indicator
        if (
            indicator is None
            or target.metric_definition != indicator.code
            or target.geography != indicator.geo_scope
            or any(
                o.indicator_id != indicator.indicator_id
                or o.source_version_id not in sources
                or o.label != draft.label
                for o in snapshot.observations
            )
        ):
            add(
                "temporal_resolution",
                "INDICATOR_SCOPE_MISMATCH",
                "L3",
                "指标定义/地区口径不匹配",
                ("target", "baseline"),
            )
        values = sorted(snapshot.observations, key=lambda o: (o.period_end, o.revision_number))
        by_period = {o.period_end: o for o in values if o.available_at <= cutoff}
        last = by_period[max(by_period)] if by_period else None
        if (
            len(by_period) < 3
            or last is None
            or draft.baseline.method != "last_value"
            or draft.baseline.projected_value != last.value
            or draft.baseline.sample_count != len(by_period)
            or (indicator and draft.baseline.unit != indicator.unit)
        ):
            add(
                "temporal_resolution",
                "BASELINE_OR_VINTAGE_ERROR",
                "L3",
                "基线与当时可用统计期/修订不一致",
                ("baseline",),
            )
    if snapshot.request.research_as_of != cutoff or draft.label != snapshot.request.label:
        add(
            "temporal_resolution",
            "CUTOFF_OR_LABEL_MISMATCH",
            "L3",
            "草稿与独立输入的时间或标签不一致",
            ("research_as_of", "label"),
        )
    for checker in CHECKERS:
        if not any(f.checker == checker for f in findings):
            add(
                checker,
                checker.upper() + "_CLEAR",
                "L0",
                "已完成可确定性检查；语义真实性仍依赖人工核实资料",
                (),
            )
    return CriticReportV1(
        critic_run_id=review_id,
        draft_id=draft.draft_id,
        draft_hash=hashed(draft.model_dump(mode="json")),
        independent_input_hash=hashed(snapshot.model_dump(mode="json")),
        findings=tuple(findings),
        checkers_completed=CHECKERS,
        duration_ms=(perf_counter() - started) * 1000,
        limitations=(
            "独立检查不读取主引擎提示词；不调用外部模型；独立补充检索限本地证据库",
            "原文存在/时间/口径可确定性核对，语义事实与因果真实性未被自动证明",
            "历史时间截断不能排除基础模型未来知识；没有真实前瞻准确率",
        ),
    )
