import asyncio
from datetime import UTC, datetime
from typing import TypeVar
from uuid import uuid4

import pytest
from prediction_engine.contracts.models import (
    IndustryCoverageReviewV1,
    IndustryEvidenceReviewV1,
    IndustryReportDraftV1,
    IndustryResearchScopeV1,
    ProfileInputV1,
)
from prediction_engine.forecasting.industry_agent import IndustryAgent, scope_from_profile
from pydantic import BaseModel

from infra.providers.industry_demo import DemoIndustryProviders, fixture_id

T = TypeVar("T", bound=BaseModel)


def test_monitor_runs_both_search_loops_and_keeps_personal_context_local():
    class InspectingProvider(DemoIndustryProviders):
        async def search(self, query, *args, **kwargs):
            assert "private-context" not in query
            return await super().search(query, *args, **kwargs)

        async def generate_structured(self, schema, messages, budget, trace_context):
            assert "private-context" not in "".join(messages)
            return await super().generate_structured(schema, messages, budget, trace_context)

    profile = ProfileInputV1(
        industry_l1_code="technology",
        industry_l2_code="software",
        occupation_text="private-context 开发",
        goals=("private-context 学习",),
        country_code="CN",
        age=31,
        gender="other",
        use_optional_fields=True,
        available_minutes_per_week=30,
        allow_low_cost_experiments=True,
    )
    scope = scope_from_profile(profile, 180)
    providers = InspectingProvider()
    result = asyncio.run(
        IndustryAgent(providers, providers, providers).run(
            scope, datetime.now(UTC), "test", profile
        )
    )
    assert result.status == "draft"
    assert scope.industry == "软件开发" and scope.region == "CN"
    assert {query.query for query in result.searched} >= {"样本市场覆盖", "样本季度统计"}
    assert {"direct", "indicator", "counter", "analogy"} == {e.kind for e in result.evidence}
    assert result.report and result.report.forecasts[0].counter_source_ids
    assert result.report.forecasts[0].analogy_case_ids == ("demo-logistics-interface",)
    assert [step.period for step in result.analogy_chains[0].milestones] == [
        "统一接口采用前",
        "统一接口采用后",
    ]
    assert result.personal_actions and result.personal_actions[0].time_minutes == 30
    assert "private-context" not in result.model_dump_json()


def test_unsupported_evidence_stops_before_report_generation():
    class MissingIndicator(DemoIndustryProviders):
        async def search(self, query, *args, **kwargs):
            if query == "样本季度统计":
                return ()
            return await super().search(query, *args, **kwargs)

        async def generate_structured(self, schema, messages, budget, trace_context):
            if schema is IndustryReportDraftV1:
                raise AssertionError("report stage must not run")
            return await super().generate_structured(schema, messages, budget, trace_context)

    providers = MissingIndicator()
    result = asyncio.run(
        IndustryAgent(providers, providers, providers).run(
            IndustryResearchScopeV1(industry="样本行业"), datetime.now(UTC), "test"
        )
    )
    assert result.status == "evidence_limited" and result.report is None
    assert "缺少季度量化指标" in result.gaps
    assert result.model_calls == 3 and result.provider_failures == 0


def test_report_cannot_cite_an_unknown_source():
    class HallucinatedCitation(DemoIndustryProviders):
        async def generate_structured(
            self, schema: type[T], messages: tuple[str, ...], budget: int, trace_context: str
        ) -> T:
            value = await super().generate_structured(schema, messages, budget, trace_context)
            if isinstance(value, IndustryReportDraftV1):
                payload = value.model_dump(mode="json")
                payload["forecasts"][0]["supporting_source_ids"].append(str(uuid4()))
                return schema.model_validate(payload)
            return value

    providers = HallucinatedCitation()
    result = asyncio.run(
        IndustryAgent(providers, providers, providers).run(
            IndustryResearchScopeV1(industry="样本行业"), datetime.now(UTC), "test"
        )
    )
    assert result.status == "evidence_limited" and result.report is None
    assert "报告引用或行动关联未通过校验" in result.gaps


@pytest.mark.parametrize("forged_outcome", [False, True])
def test_other_industry_chain_can_ground_a_conditional_report(forged_outcome):
    class AnalogyOnly(DemoIndustryProviders):
        async def generate_structured(self, schema, messages, budget, trace_context):
            value = await super().generate_structured(schema, messages, budget, trace_context)
            payload = value.model_dump(mode="json")
            if schema is IndustryEvidenceReviewV1:
                payload.update(sufficient=True, gaps=[], queries=[])
                payload["evidence"] = []
                if forged_outcome:
                    payload["analogy_chains"][0]["milestones"][-1]["quote"] = (
                        "这段所谓结果不存在于任何抓取的历史原文中"
                    )
            if schema is IndustryReportDraftV1:
                payload["forecasts"][0].update(
                    basis="analogy",
                    supporting_source_ids=[fixture_id("analogy")],
                    counter_source_ids=[],
                )
            return schema.model_validate(payload)

    providers = AnalogyOnly()
    result = asyncio.run(
        IndustryAgent(providers, providers, providers).run(
            IndustryResearchScopeV1(industry="样本软件服务行业"), datetime.now(UTC), "test"
        )
    )
    if forged_outcome:
        assert result.status == "evidence_limited" and result.report is None
        assert not result.analogy_chains
    else:
        assert result.report and result.report.forecasts[0].basis == "analogy"
        assert not result.evidence
        assert result.analogy_chains[0].industry == "DEMO 虚构物流行业"


def test_model_generated_url_or_credential_never_reaches_search_provider():
    class InjectedReview(DemoIndustryProviders):
        async def search(self, query, *args, **kwargs):
            assert "http://" not in query and "api_key=" not in query
            return await super().search(query, *args, **kwargs)

        async def generate_structured(self, schema, messages, budget, trace_context):
            result = await super().generate_structured(schema, messages, budget, trace_context)
            if isinstance(result, IndustryCoverageReviewV1) and not result.sufficient:
                data = result.model_dump(mode="json")
                data["queries"] = [
                    *data["queries"],
                    {"lane": "market", "query": "http://169.254.169.254/latest/meta-data"},
                    {"lane": "market", "query": "api_key=example_secret_123456"},
                ]
                return schema.model_validate(data)
            return result

    providers = InjectedReview()
    result = asyncio.run(
        IndustryAgent(providers, providers, providers).run(
            IndustryResearchScopeV1(industry="样本行业"), datetime.now(UTC), "test"
        )
    )
    assert result.status == "draft"
    assert all(
        "http://" not in query.query and "api_key=" not in query.query for query in result.searched
    )
