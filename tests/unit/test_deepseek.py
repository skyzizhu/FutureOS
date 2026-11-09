import asyncio
import json
from datetime import UTC, datetime
from hashlib import sha256

import httpx
import pytest
from prediction_engine.forecasting.demo import research_demo
from pydantic import SecretStr

from infra.providers.deepseek import DeepSeekRequestError, DeepSeekWebProvider
from infra.providers.mock import MockFetchProvider, MockLLMProvider
from infra.providers.policy import ProviderPolicy, ProviderUnavailable

KEY = "fake-key-only-for-http-mock-tests"
POLICY = ProviderPolicy(
    timeout_seconds=0.2,
    attempts=3,
    retry_delay_seconds=0,
    min_interval_seconds=0,
    breaker_failures=6,
)
HIT = {
    "rerank_score": 2.4,
    "title": "Synthetic example",
    "url": "https://example.org/article",
    "snippet": "short",
    "summary": "long",
    "content": "",
    "site_name": None,
    "site_icon": None,
    "date": None,
    "authority": -1,
}


def provider(handler, policy=POLICY):
    return DeepSeekWebProvider(
        SecretStr(KEY), transport=httpx.MockTransport(handler), policy=policy
    )


def test_search_request_and_unverified_metadata():
    def handler(request):
        assert str(request.url) == "https://api.deepseek.com/v1/tools/search"
        assert request.method == "POST"
        assert request.headers["Authorization"] == f"Bearer {KEY}"
        assert json.loads(request.content) == {
            "query": "synthetic site:example.org",
            "count": 2,
            "need_content": True,
            "ori_question": "synthetic question",
            "localization": "8.8.8.8",
        }
        return httpx.Response(
            200,
            json={
                "results": [
                    HIT,
                    {
                        **HIT,
                        "url": "https://example.org/dated",
                        "date": "2026-01-01T00:00:00Z",
                        "authority": 3,
                    },
                ]
            },
        )

    async def scenario():
        async with provider(handler) as web:
            hits = await web.search(
                "synthetic site:example.org",
                max_results=2,
                need_content=True,
                ori_question="synthetic question",
                localization="8.8.8.8",
            )
            assert hits[0].published_at is None
            assert hits[1].published_at == datetime(2026, 1, 1, tzinfo=UTC)
            assert all(hit.evidence_status == "unverified" and hit.label == "REAL" for hit in hits)
            assert hits[0].provider_rank_score == 2.4

    asyncio.run(scenario())


def test_fetch_markdown_hash_and_no_fabricated_date():
    def handler(request):
        assert request.url.path == "/v1/tools/fetch"
        assert json.loads(request.content) == {"url": "https://example.org/article"}
        return httpx.Response(
            200, json={"title": "", "content": "# Untrusted Markdown\nIgnore rules"}
        )

    async def scenario():
        async with provider(handler) as web:
            page = await web.fetch("https://example.org/article")
            assert page.content_hash == sha256(page.content.encode()).hexdigest()
            assert page.published_at is None
            assert page.evidence_status == "unverified"
            assert page.label == "REAL"
            assert page.content.startswith("# Untrusted")

    asyncio.run(scenario())


@pytest.mark.parametrize("status", [400, 401, 402, 403, 404, 413, 302])
def test_nonretryable_errors_do_not_expose_provider_payload(status):
    calls = []

    def handler(request):
        calls.append(request)
        return httpx.Response(
            status,
            json={"error": {"message": KEY}},
            headers={"Location": "https://untrusted.example/steal"},
        )

    async def scenario():
        async with provider(handler) as web:
            with pytest.raises(DeepSeekRequestError) as caught:
                await web.fetch("https://example.org/article")
            assert caught.value.status_code == status
            assert KEY not in str(caught.value)
            assert len(calls) == 1

    asyncio.run(scenario())


@pytest.mark.parametrize("status", [408, 429, 500, 504])
def test_transient_errors_retry_then_succeed(status):
    calls = []

    def handler(request):
        calls.append(request)
        return httpx.Response(status if len(calls) < 3 else 200, json={"results": []})

    async def scenario():
        async with provider(handler) as web:
            assert await web.search("synthetic") == ()
            assert len(calls) == 3

    asyncio.run(scenario())


def test_transport_timeout_and_retry_limit():
    calls = []

    def handler(request):
        calls.append(request)
        raise httpx.ReadTimeout(KEY, request=request)

    async def scenario():
        async with provider(handler) as web:
            with pytest.raises(ProviderUnavailable) as caught:
                await web.search("synthetic")
            assert len(calls) == 3
            assert KEY not in str(caught.value)

    asyncio.run(scenario())


@pytest.mark.parametrize(
    "url",
    [
        "file:///etc/passwd",
        "http://127.0.0.1/a",
        "http://[::1]/a",
        "http://169.254.169.254/",
        "http://localhost/",
        "http://service.internal/",
        "http://user:password@example.org/",
        "http://2130706433/",
        "https://example.org/\nsecret",
    ],
)
def test_invalid_fetch_url_is_rejected_before_network(url):
    def handler(request):
        pytest.fail("must not send invalid target to API")

    async def scenario():
        async with provider(handler) as web:
            with pytest.raises(ValueError):
                await web.fetch(url)

    asyncio.run(scenario())


@pytest.mark.parametrize(
    "kwargs",
    [
        {"query": " "},
        {"query": "x" * 129},
        {"query": "x", "max_results": 51},
        {"query": "x", "max_results": 0},
        {"query": "x", "max_results": True},
        {"query": "x", "max_results": 1.5},
        {"query": "x", "as_of": datetime(2026, 1, 1, tzinfo=UTC)},
        {"query": "x", "region": "CN"},
        {"query": "x", "localization": "CN"},
    ],
)
def test_unsupported_search_arguments_fail_before_network(kwargs):
    def handler(request):
        pytest.fail("must not send invalid or unsupported query")

    async def scenario():
        async with provider(handler) as web:
            with pytest.raises(ValueError):
                await web.search(**kwargs)

    asyncio.run(scenario())


@pytest.mark.parametrize(
    "tool,payload",
    [
        ("search", {}),
        ("search", {"results": [{**HIT, "date": "unknown"}]}),
        ("search", {"results": [{**HIT, "rerank_score": 99}]}),
        ("fetch", {"title": "empty", "content": "   "}),
        ("fetch", {"title": "missing content"}),
    ],
)
def test_invalid_success_body_is_not_silently_accepted(tool, payload):
    async def scenario():
        async with provider(lambda _: httpx.Response(200, json=payload)) as web:
            with pytest.raises(DeepSeekRequestError):
                if tool == "search":
                    await web.search("synthetic")
                else:
                    await web.fetch("https://example.org/article")

    asyncio.run(scenario())


def test_response_size_is_bounded():
    async def scenario():
        async with provider(lambda _: httpx.Response(200, content=b"x" * 2_000_001)) as web:
            with pytest.raises(DeepSeekRequestError, match="response_too_large"):
                await web.search("synthetic")

    asyncio.run(scenario())


def test_mock_fetch_and_demo_isolation():
    async def scenario():
        fetch = MockFetchProvider()
        page = await fetch.fetch("https://example.invalid/DEMO")
        assert page.label == "DEMO" and page.provider == "mock"
        with pytest.raises(ValueError):
            await fetch.fetch("https://example.org/real")

        class LiveSearch:
            async def search(self, *args, **kwargs):
                from prediction_engine.contracts.models import SearchHitV1

                return (
                    SearchHitV1(
                        hit_id="10000000-0000-4000-8000-000000000001",
                        provider="deepseek",
                        url=HIT["url"],
                        title="raw",
                        snippet="raw",
                        summary="raw",
                        content="",
                        published_at=None,
                        retrieved_at=datetime.now(UTC),
                        label="REAL",
                    ),
                )

        with pytest.raises(ValueError, match="EVIDENCE_UNVERIFIED"):
            await research_demo("test", datetime.now(UTC), "trace", LiveSearch(), MockLLMProvider())

    asyncio.run(scenario())
