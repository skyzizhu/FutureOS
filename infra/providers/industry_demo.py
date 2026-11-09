"""Deterministic fixtures for the industry research CLI and private DEMO jobs."""

import json
from datetime import UTC, datetime
from hashlib import sha256
from typing import TypeVar
from uuid import NAMESPACE_URL, uuid5

from prediction_engine.contracts.models import (
    FetchedPageV1,
    IndustryCoverageReviewV1,
    IndustryEvidenceReviewV1,
    IndustryReportDraftV1,
    SearchHitV1,
)
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)
DEMO_TIME = datetime(2026, 1, 1, tzinfo=UTC)
ANALOGY_START = "DEMO：虚构物流行业早期由各企业分别对接仓配接口，接入成本较高。"
ANALOGY_OUTCOME = "DEMO：虚构物流行业采用统一接口后，可复用的跨企业配送服务开始增加。"
FIXTURES = {
    "industry": "DEMO：样本企业开始把新工具从单项试用推进到可校验的流程试点。",
    "market": "DEMO：样本采购方开始要求供应商交付附带验收记录的完整流程。",
    "policy": "DEMO：虚构行业指南要求在扩大部署前保留人工检查与退出路径。",
    "counter": "DEMO：另一样本的复核时间持续上升，说明采用速度可能低于预期。",
    "analogy": ANALOGY_START + "\n" + ANALOGY_OUTCOME,
    "indicator": "DEMO：样本采用率在2026年第一季度为28%，上一季度为20%。",
}
SEARCH_KEYS = {
    "行业最新动态": "industry",
    "样本市场覆盖": "market",
    "监管 政策": "policy",
    "趋势反证": "counter",
    "跨行业相似机制": "analogy",
    "样本季度统计": "indicator",
}


def fixture_url(key: str) -> str:
    return f"https://demo-{key}.invalid/sample"


def fixture_id(key: str) -> str:
    return str(uuid5(NAMESPACE_URL, fixture_url(key)))


class DemoIndustryProviders:
    async def search(
        self,
        query: str,
        as_of: datetime | None = None,
        region: str | None = None,
        max_results: int = 5,
    ) -> tuple[SearchHitV1, ...]:
        key = next((key for phrase, key in SEARCH_KEYS.items() if phrase in query), None)
        if key is None or max_results < 1:
            return ()
        return (
            SearchHitV1(
                hit_id=uuid5(NAMESPACE_URL, fixture_url(key)),
                provider="mock",
                url=fixture_url(key),
                title="DEMO " + key,
                snippet=FIXTURES[key],
                summary="虚构研究资料",
                content="",
                published_at=DEMO_TIME,
                retrieved_at=DEMO_TIME,
                label="DEMO",
            ),
        )

    async def fetch(self, url: str) -> FetchedPageV1:
        key = next(key for key in FIXTURES if url == fixture_url(key))
        content = FIXTURES[key]
        return FetchedPageV1(
            provider="mock",
            url=url,
            title="DEMO " + key,
            content=content,
            content_hash=sha256(content.encode()).hexdigest(),
            retrieved_at=DEMO_TIME,
            label="DEMO",
        )

    async def generate_structured(
        self, schema: type[T], messages: tuple[str, ...], budget: int, trace_context: str
    ) -> T:
        payload = json.loads(messages[1])["input"]
        if schema is IndustryCoverageReviewV1:
            found = any(row["title"] == "DEMO market" for row in payload)
            return schema.model_validate(
                {
                    "sufficient": found,
                    "gaps": [] if found else ["缺少市场需求线索"],
                    "queries": [] if found else [{"lane": "market", "query": "样本市场覆盖"}],
                }
            )
        if schema is IndustryEvidenceReviewV1:
            source_ids = {row["source_id"] for row in payload}
            found = fixture_id("indicator") in source_ids
            chains = []
            if fixture_id("analogy") in source_ids:
                chains.append(
                    {
                        "case_id": "demo-logistics-interface",
                        "industry": "DEMO 虚构物流行业",
                        "context": "仓配服务需要在不同企业的系统之间交接",
                        "milestones": [
                            {
                                "period": "统一接口采用前",
                                "observed_change": "不同企业需要分别对接仓配接口",
                                "source_id": fixture_id("analogy"),
                                "quote": ANALOGY_START,
                            },
                            {
                                "period": "统一接口采用后",
                                "observed_change": "可复用的跨企业配送服务开始增加",
                                "source_id": fixture_id("analogy"),
                                "quote": ANALOGY_OUTCOME,
                            },
                        ],
                        "mechanism": "重复接入工作减少后，服务更容易跨企业复制",
                        "comparable_conditions": "两类流程都存在重复对接和跨团队验收",
                        "key_difference": "软件流程的错误可能比物流交接更难观察",
                    }
                )
            evidence = []
            for key, kind in (
                ("industry", "direct"),
                ("market", "direct"),
                ("counter", "counter"),
                ("analogy", "analogy"),
                ("indicator", "indicator"),
            ):
                if fixture_id(key) not in source_ids:
                    continue
                item = {
                    "source_id": fixture_id(key),
                    "kind": kind,
                    "quote": FIXTURES[key],
                    "interpretation": "虚构样本用于验证引用和流程",
                }
                if key == "analogy":
                    item.update(
                        comparable_conditions="都依赖标准化接口和验收",
                        key_difference="行业约束和采用成本不同",
                    )
                if key == "indicator":
                    item.update(
                        indicator_name="样本采用率",
                        indicator_period="2026年第一季度",
                        indicator_value="28%",
                    )
                evidence.append(item)
            return schema.model_validate(
                {
                    "sufficient": found,
                    "gaps": [] if found else ["缺少季度量化指标"],
                    "queries": [] if found else [{"lane": "indicators", "query": "样本季度统计"}],
                    "evidence": evidence,
                    "analogy_chains": chains,
                }
            )
        if schema is not IndustryReportDraftV1:
            raise ValueError("UNKNOWN_DEMO_SCHEMA")
        return schema.model_validate(
            {
                "forecasts": [
                    {
                        "statement": "DEMO：若复核成本下降，样本市场可能从试用转向小规模流程部署。",
                        "mechanism": "验收接口标准化降低跨团队协作成本",
                        "expected_signal": "更多试点完成可复现验收",
                        "falsifier": "复核耗时持续超过原流程",
                        "uncertainty": "虚构数据，仅用于流程验收",
                        "alternatives": ["复核成本持续偏高，采用停在试用阶段"],
                        "supporting_source_ids": [
                            fixture_id("industry"),
                            fixture_id("indicator"),
                            fixture_id("analogy"),
                        ],
                        "counter_source_ids": [fixture_id("counter")],
                        "analogy_case_ids": ["demo-logistics-interface"],
                    }
                ],
                "actions": [
                    {
                        "forecast_index": 0,
                        "domain": "work",
                        "action": "选一项可逆的低风险工作流，比较试用和原流程耗时",
                        "trigger": "发现团队重复执行相同任务",
                        "check_after_days": 14,
                        "time_minutes": 30,
                        "success_check": "记录执行和复核总耗时，检查能否稳定复现",
                        "stop_condition": "复核耗时持续超过原流程",
                    }
                ],
            }
        )
