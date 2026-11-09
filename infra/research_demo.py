"""Own synthetic M2 fixtures. No network, true historical evidence or real prediction."""

from datetime import UTC, datetime
from uuid import UUID

from prediction_engine.contracts.models import (
    DomainTag,
    ForecastTargetV1,
    HistoricalCaseImportV1,
    IndicatorImportV1,
    ObservationImportV1,
    ResearchSubmitV1,
    SignalImportV1,
    SourceImportV1,
    SourceIngestedV1,
)
from sqlalchemy.orm import Session

from infra.evidence_repository import EvidenceRepository


def moment(text: str) -> datetime:
    return datetime.fromisoformat(text).replace(tzinfo=UTC)


def seed_research_demo(session: Session, actor: UUID) -> ResearchSubmitV1:
    repo = EvidenceRepository(session)

    def source(
        name: str, body: str, date: str, fact: bool = True, contradicts: bool = False
    ) -> SourceIngestedV1:
        data = {
            "url": f"https://example.invalid/m2/{name}",
            "title": "DEMO " + name,
            "publisher": "FutureOS synthetic fixture",
            "source_type": "manual",
            "published_at": moment(date),
            "available_at": moment(date),
            "availability_basis": "verified_archive",
            "availability_note": "Synthetic archived fixture",
            "content": body,
            "usage_permission": "authorized_full",
            "license_note": "Own synthetic fixture for software testing",
            "reliability_note": "DEMO only; not real-world facts",
            "domain_tags": ["technology", "workforce"],
            "label": "DEMO",
            "claims": [
                {
                    "claim_text": body,
                    "quote": body,
                    "source_locator": "fixture paragraph 1",
                    "relation": "contradicts" if contradicts else "supports",
                    "claim_kind": "fact",
                    "verification_status": "verified",
                    "verification_note": "Checked against owned synthetic fixture",
                    "scope": "DEMO-lab",
                }
            ]
            if fact
            else [],
        }
        return repo.ingest(SourceImportV1.model_validate(data), actor)

    signals = []
    for i, (capability, body) in enumerate(
        [
            ("context_understanding", "DEMO：在预登记的独立试验中，上下文理解组件能读取任务约束。"),
            ("tool_execution", "DEMO：另一个工具执行组件能在隔离环境中运行指定操作。"),
            ("feedback_validation", "DEMO：第三个反馈校验组件能检查任务输出并发现部分错误。"),
            ("reliability_risk", "DEMO反证：复杂任务可靠性仍不足，治理与验证成本尚未下降。"),
        ],
        start=1,
    ):
        item = source(capability, body, f"2020-05-0{i}", contradicts=i == 4)
        signal = repo.create_signal(
            SignalImportV1(
                headline=body,
                claim_ids=item.claim_ids,
                mechanism_tags=(capability,),
                domain_tags=(DomainTag.TECHNOLOGY, DomainTag.WORKFORCE),
            )
        )
        signals.append(signal.signal_id)
    statistics = source(
        "reliability", "DEMO：受控任务完成数按每100次试验计，1月40、2月50、3月60。", "2020-05-05"
    )
    indicator = repo.indicator(
        IndicatorImportV1(
            code="demo_task_reliability",
            name="DEMO task reliability",
            provider="synthetic",
            geo_scope="DEMO-lab",
            unit="completed_tasks_per_100_trials",
            frequency="month",
            definition_version="v1",
            label="DEMO",
        )
    )
    for month, value in [(1, 40), (2, 50), (3, 60)]:
        repo.observation(
            indicator.indicator_id,
            ObservationImportV1(
                source_version_id=statistics.version.source_version_id,
                period_start=moment(f"2020-{month:02}-01"),
                period_end=moment(f"2020-{month:02}-28"),
                value=value,
                published_at=moment("2020-05-05"),
                available_at=moment("2020-05-05"),
                revision_number=1,
                quality_flag="DEMO_DATA",
                definition_note="Synthetic fixed trial protocol",
            ),
        )
    cases = []
    for letter, category in [("A", "success"), ("B", "failure")]:
        initial = source(
            "case-" + letter,
            "DEMO 跨领域案例 " + letter + "：互补组件进入早期试点。",
            "2010-01-01",
            False,
        )
        outcome = source(
            "outcome-" + letter, "DEMO 历史结果 " + letter + ": " + category, "2012-01-01", False
        )
        cases.append(
            repo.historical_case(
                HistoricalCaseImportV1.model_validate(
                    {
                        "title": "DEMO cross-domain case " + letter,
                        "cutoff_at": moment("2010-06-01"),
                        "domain_tags": ["industry" if letter == "A" else "education"],
                        "mechanism_tags": ["complementarity", "adoption"],
                        "initial_conditions": "DEMO pilot in distinct institutions",
                        "limitations": [
                            "Synthetic analogy; no real-world forecasting accuracy implication"
                        ],
                        "label": "DEMO",
                        "events": [
                            {
                                "text": "Complementary components entered pilot",
                                "known_at": moment("2010-01-01"),
                                "source_version_id": initial.version.source_version_id,
                                "data_role": "contemporaneous",
                            },
                            {
                                "text": "DEMO retrospective " + category,
                                "known_at": moment("2012-01-01"),
                                "source_version_id": outcome.version.source_version_id,
                                "data_role": "outcome",
                                "outcome_category": category,
                            },
                        ],
                    }
                )
            )
        )
    return ResearchSubmitV1(
        title="DEMO AI 工具与软件开发任务",
        scope="DEMO-lab 受控试验；不外推就业或个人行动",
        domain_tags=(DomainTag.TECHNOLOGY, DomainTag.WORKFORCE),
        research_as_of=moment("2020-06-01"),
        signal_ids=tuple(signals),
        historical_case_ids=tuple(cases),
        indicator_id=indicator.indicator_id,
        target=ForecastTargetV1(
            target_type="numeric",
            population_scope="DEMO fixed trial protocol",
            geography="DEMO-lab",
            metric_definition=indicator.code,
            direction_or_threshold=">=70 tasks/100",
            baseline="2020-03: 60 completed tasks per 100 trials",
            target_start_at=moment("2020-06-02"),
            target_end_at=moment("2020-12-31"),
            resolution_source="https://example.invalid/m2/reliability",
            resolution_rule="预登记固定100次任务试验，按相同口径核对完成数；数据缺失则不可判定",
        ),
        label="DEMO",
    )
