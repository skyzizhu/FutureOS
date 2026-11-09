from datetime import datetime

from prediction_engine.contracts.models import SearchHitV1

from infra.providers.deepseek import DeepSeekWebProvider
from infra.providers.mock import (
    MockDataSourceProvider,
    MockEmailProvider,
    MockFetchProvider,
    MockLLMProvider,
    MockPaymentProvider,
    MockSearchProvider,
    MockStorageProvider,
)
from infra.providers.policy import ProviderRunner


class GuardedSearch(MockSearchProvider):
    def __init__(self) -> None:
        self.runner = ProviderRunner()

    async def search(
        self,
        query: str,
        as_of: datetime | None = None,
        region: str | None = None,
        max_results: int = 5,
    ) -> tuple[SearchHitV1, ...]:
        return await self.runner.call(
            lambda: super(GuardedSearch, self).search(query, as_of, region, max_results)
        )


def mock_providers() -> tuple[GuardedSearch, MockLLMProvider]:
    return GuardedSearch(), MockLLMProvider()


__all__ = [
    "DeepSeekWebProvider",
    "MockDataSourceProvider",
    "MockEmailProvider",
    "MockFetchProvider",
    "MockLLMProvider",
    "MockPaymentProvider",
    "MockSearchProvider",
    "MockStorageProvider",
    "mock_providers",
]
