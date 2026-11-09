"""Run one industry research draft with synthetic fixtures or explicitly enabled providers."""

import argparse
import asyncio
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from prediction_engine.contracts.models import (
    IndustryResearchRunV1,
    IndustryResearchScopeV1,
    ProfileInputV1,
)
from prediction_engine.forecasting.industry_agent import IndustryAgent, scope_from_profile

from infra.providers.deepseek import DeepSeekWebProvider
from infra.providers.deepseek_llm import DeepSeekLLMProvider
from infra.providers.industry_demo import DemoIndustryProviders
from infra.providers.policy import ProviderPolicy
from infra.settings import get_settings


async def run(args: argparse.Namespace) -> IndustryResearchRunV1:
    profile = (
        ProfileInputV1.model_validate_json(args.profile.read_bytes()) if args.profile else None
    )
    scope = (
        scope_from_profile(profile, args.horizon_days)
        if profile and not args.industry
        else IndustryResearchScopeV1(
            industry=args.industry or "样本软件服务行业", horizon_days=args.horizon_days
        )
    )
    now, trace = datetime.now(UTC), str(uuid4())
    if not args.live:
        demo = DemoIndustryProviders()
        return await IndustryAgent(demo, demo, demo).run(scope, now, trace, profile)
    config = get_settings()
    key = config.deepseek_api_key
    if not (key and config.live_web_enabled and config.live_research_enabled):
        raise SystemExit("LIVE_INDUSTRY_AGENT_REQUIRES_EXPLICIT_PROVIDER_CONFIGURATION")
    async with DeepSeekWebProvider(
        key,
        allowed_hosts=config.fetch_allowed_hosts,
        policy=ProviderPolicy(timeout_seconds=12, attempts=1, min_interval_seconds=0.1),
    ) as web:
        model = DeepSeekLLMProvider(key, config.deepseek_research_model)
        return await IndustryAgent(web, web, model).run(
            scope.model_copy(update={"label": "REAL"}), now, trace, profile
        )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--industry", help="公开可检索的行业范围")
    parser.add_argument(
        "--profile", type=Path, help="本地 ProfileInputV1 JSON，仅授权字段用于个性化"
    )
    parser.add_argument("--horizon-days", type=int, default=180)
    parser.add_argument("--live", action="store_true", help="显式调用已配置的真实提供商")
    args = parser.parse_args()
    if args.live and not (args.industry or args.profile):
        parser.error("--live requires --industry or --profile")
    result = asyncio.run(run(args))
    print(result.model_dump_json(indent=2))
    if result.status != "draft":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
