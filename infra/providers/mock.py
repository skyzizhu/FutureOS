"""No network, email transport, production payment SDK or keys in any Mock adapter."""

import hashlib
import hmac
import json
from datetime import UTC, datetime
from typing import TypeVar
from urllib.parse import urlsplit
from uuid import UUID

from prediction_engine.contracts.models import (
    FetchedPageV1,
    IndicatorObservationVintageV1,
    SearchHitV1,
)
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)
DEMO_TIME = datetime(2026, 1, 1, tzinfo=UTC)
DEMO_SOURCE = UUID("10000000-0000-4000-8000-000000000001")


class MockSearchProvider:
    async def search(
        self,
        query: str,
        as_of: datetime | None = None,
        region: str | None = None,
        max_results: int = 5,
    ) -> tuple[SearchHitV1, ...]:
        if max_results < 1 or (as_of is not None and as_of < DEMO_TIME):
            return ()
        return (
            SearchHitV1(
                hit_id=DEMO_SOURCE,
                provider="mock",
                title="DEMO synthetic source",
                summary="Synthetic search response for M0 wiring tests",
                content="",
                retrieved_at=DEMO_TIME,
                url="https://example.invalid/DEMO",
                published_at=DEMO_TIME,
                snippet="DEMO synthetic source, not a real world observation",
                label="DEMO",
            ),
        )


class MockFetchProvider:
    async def fetch(self, url: str) -> FetchedPageV1:
        parsed = urlsplit(url)
        if (
            parsed.scheme != "https"
            or parsed.hostname != "example.invalid"
            or parsed.username is not None
            or parsed.password is not None
        ):
            raise ValueError("DEMO fetch supports https://example.invalid only")
        content = "# DEMO\nSynthetic Markdown; not real-world evidence."
        return FetchedPageV1(
            provider="mock",
            url=url,
            title="DEMO fixture",
            content=content,
            content_hash=hashlib.sha256(content.encode()).hexdigest(),
            retrieved_at=DEMO_TIME,
            label="DEMO",
        )


class MockDataSourceProvider:
    async def get_series(
        self, indicator_id: str, as_of: datetime, start: datetime, end: datetime
    ) -> tuple[IndicatorObservationVintageV1, ...]:
        if as_of < DEMO_TIME or not start <= DEMO_TIME <= end:
            return ()
        return (
            IndicatorObservationVintageV1(
                indicator_id=indicator_id,
                period_start=DEMO_TIME,
                period_end=DEMO_TIME,
                value=100,
                published_at=DEMO_TIME,
                available_at=DEMO_TIME,
                vintage="demo-v1",
                quality_flag="DEMO_DATA",
            ),
        )


class MockLLMProvider:
    async def generate_structured(
        self, schema: type[T], messages: tuple[str, ...], budget: int, trace_context: str
    ) -> T:
        if budget < 1:
            raise ValueError("budget_exceeded")
        # Deliberately ignores user-supplied commands; only returns a validated fixed fixture.
        return schema.model_validate(
            {
                "label": "DEMO",
                "kind": "hypothesis",
                "statement": "DEMO：工具可靠性提高可能改变任务分工；此条为合成研究假设。",
                "research_as_of": DEMO_TIME,
                "source_ids": [DEMO_SOURCE],
                "limitations": ["合成数据，仅验证模块连通性；未进行真实研究、Critic 或预测发布"],
                "prompt_hash": hashlib.sha256(messages[0].encode()).hexdigest(),
            }
        )


class MockEmailProvider:
    def __init__(self) -> None:
        self.sent: dict[str, str] = {}

    async def send(
        self, template_id: str, recipient: str, payload: dict[str, str], dedupe_key: str
    ) -> str:
        if not recipient.endswith("@example.invalid"):
            raise ValueError("DEMO recipient must use @example.invalid")
        fingerprint = hashlib.sha256(
            json.dumps([template_id, recipient, payload], sort_keys=True).encode()
        ).hexdigest()
        if dedupe_key in self.sent and self.sent[dedupe_key] != fingerprint:
            raise ValueError("idempotency_conflict")
        self.sent[dedupe_key] = fingerprint
        return "DEMO-email-" + fingerprint[:12]


class MockPaymentProvider:
    def __init__(self, webhook_secret: bytes = b"DEMO-only-test-secret") -> None:
        self.webhook_secret = webhook_secret
        self.sessions: dict[str, tuple[str, str, str]] = {}

    async def create_checkout(self, user_id: str, plan_code: str, idempotency_key: str) -> str:
        url = (
            "https://example.invalid/DEMO-checkout/"
            + hashlib.sha256(f"{user_id}:{plan_code}:{idempotency_key}".encode()).hexdigest()[:16]
        )
        value = (user_id, plan_code, url)
        if idempotency_key in self.sessions and self.sessions[idempotency_key] != value:
            raise ValueError("idempotency_conflict")
        self.sessions[idempotency_key] = value
        return url

    async def verify_webhook(self, payload: bytes, signature: str) -> dict[str, str]:
        expected = hmac.new(self.webhook_secret, payload, "sha256").hexdigest()
        if not hmac.compare_digest(signature, expected):
            raise ValueError("invalid_demo_signature")
        data = json.loads(payload)
        if not isinstance(data, dict) or data.get("label") != "DEMO":
            raise ValueError("DEMO payload required")
        return {str(k): str(v) for k, v in data.items()}

    async def get_subscription(self, reference: str) -> dict[str, str]:
        return {"label": "DEMO", "status": "inactive", "reference": reference}


class MockStorageProvider:
    def __init__(self) -> None:
        self.objects: dict[str, bytes] = {}

    async def put(self, key: str, content: bytes) -> str:
        if key in self.objects and self.objects[key] != content:
            raise ValueError("immutable_object_conflict")
        self.objects[key] = content
        return key

    async def get(self, key: str) -> bytes:
        return self.objects[key]
