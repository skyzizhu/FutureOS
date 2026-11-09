"""Ports only. Implementations live in infra/providers, never in the engine."""

from datetime import datetime
from typing import Protocol, TypeVar

from pydantic import BaseModel

from .models import FetchedPageV1, IndicatorObservationVintageV1, SearchHitV1

T = TypeVar("T", bound=BaseModel)


class SearchProvider(Protocol):
    async def search(
        self,
        query: str,
        as_of: datetime | None = None,
        region: str | None = None,
        max_results: int = 5,
    ) -> tuple[SearchHitV1, ...]: ...


class FetchProvider(Protocol):
    async def fetch(self, url: str) -> FetchedPageV1: ...


class DataSourceProvider(Protocol):
    async def get_series(
        self, indicator_id: str, as_of: datetime, start: datetime, end: datetime
    ) -> tuple[IndicatorObservationVintageV1, ...]: ...


class LLMProvider(Protocol):
    async def generate_structured(
        self, schema: type[T], messages: tuple[str, ...], budget: int, trace_context: str
    ) -> T: ...


class EmailProvider(Protocol):
    async def send(
        self, template_id: str, recipient: str, payload: dict[str, str], dedupe_key: str
    ) -> str: ...


class PaymentProvider(Protocol):
    async def create_checkout(self, user_id: str, plan_code: str, idempotency_key: str) -> str: ...
    async def verify_webhook(self, payload: bytes, signature: str) -> dict[str, str]: ...
    async def get_subscription(self, reference: str) -> dict[str, str]: ...


class StorageProvider(Protocol):
    async def put(self, key: str, content: bytes) -> str: ...
    async def get(self, key: str) -> bytes: ...
