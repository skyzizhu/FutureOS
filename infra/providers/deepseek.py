"""DeepSeek Search/Fetch boundary. M0 uses this only with fake HTTP transports.

No model completion, HTML rendering, evidence verification or automatic DEMO fallback.
"""

import asyncio
import socket
from datetime import UTC, datetime
from hashlib import sha256
from ipaddress import ip_address
from typing import Self
from urllib.parse import urlsplit
from uuid import NAMESPACE_URL, uuid5

import httpx
from prediction_engine.contracts.models import FetchedPageV1, SearchHitV1
from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, SecretStr

from infra.providers.policy import ProviderPolicy, ProviderRunner


class DeepSeekRequestError(Exception):
    """Sanitized non-retryable failure; never exposes upstream body, URL or credentials."""

    def __init__(self, code: str, status_code: int | None = None) -> None:
        self.code = code
        self.status_code = status_code
        super().__init__(code)


class _Hit(BaseModel):
    model_config = ConfigDict(extra="ignore", strict=True)
    rerank_score: float = Field(ge=0, le=3)
    title: str
    url: str
    snippet: str
    summary: str
    content: str
    site_name: str | None
    site_icon: str | None
    date: AwareDatetime | None
    authority: int = Field(ge=-1, le=4)


class _SearchResponse(BaseModel):
    model_config = ConfigDict(strict=True)
    results: tuple[_Hit, ...]


class _FetchResponse(BaseModel):
    model_config = ConfigDict(strict=True)
    title: str
    content: str = Field(min_length=1)


def validate_public_url(url: str) -> None:
    """Basic request guard; DeepSeek performs remote DNS/navigation, not this process."""
    if not 1 <= len(url) <= 8192 or any(ord(c) <= 32 for c in url) or "\\" in url:
        raise ValueError("invalid_fetch_url")
    try:
        parsed = urlsplit(url)
        host = (parsed.hostname or "").rstrip(".").lower().encode("idna").decode()
        _ = parsed.port
    except (ValueError, UnicodeError):
        raise ValueError("invalid_fetch_url") from None
    if (
        parsed.scheme not in {"http", "https"}
        or not host
        or parsed.username is not None
        or parsed.password is not None
        or "%" in host
        or parsed.port not in {None, 80, 443}
    ):
        raise ValueError("invalid_fetch_url")
    try:
        address = ip_address(host)
    except ValueError:
        if (
            "." not in host
            or host.endswith((".localhost", ".local", ".internal"))
            or all(c in "0123456789." for c in host)
        ):
            raise ValueError("non_public_fetch_url") from None
    else:
        if not address.is_global:
            raise ValueError("non_public_fetch_url")


class DeepSeekWebProvider:
    BASE_URL = "https://api.deepseek.com"

    def __init__(
        self,
        api_key: SecretStr,
        *,
        transport: httpx.AsyncBaseTransport | None = None,
        policy: ProviderPolicy | None = None,
        allowed_hosts: tuple[str, ...] | None = None,
    ) -> None:
        if not api_key.get_secret_value().strip():
            raise ValueError("deepseek_api_key_required")
        self.allowed_hosts = allowed_hosts
        self.resolve_dns = transport is None and allowed_hosts is not None
        self._client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers={
                "Authorization": f"Bearer {api_key.get_secret_value()}",
                "Content-Type": "application/json",
            },
            timeout=20,
            follow_redirects=False,
            trust_env=False,
            transport=transport,
        )
        # Independent Search/Fetch rate and circuit state. Account-wide quotas remain upstream.
        self.request_counts = {"search": 0, "fetch": 0}
        self._runners = {
            name: ProviderRunner(
                policy
                or ProviderPolicy(
                    timeout_seconds=20,
                    attempts=3,
                    retry_delay_seconds=0.5,
                    min_interval_seconds=0.05,
                    breaker_failures=6,
                )
            )
            for name in ("search", "fetch")
        }
        self._locks = {name: asyncio.Lock() for name in ("search", "fetch")}

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        await self._client.aclose()

    async def _post(self, tool: str, payload: dict[str, object]) -> bytes:
        async def request() -> bytes:
            self.request_counts[tool] += 1
            try:
                async with self._client.stream(
                    "POST", f"/v1/tools/{tool}", json=payload
                ) as response:
                    status = response.status_code
                    if status in {408, 429} or 500 <= status <= 599:
                        raise ConnectionError("deepseek_retryable_http")
                    if status != 200:
                        raise DeepSeekRequestError(f"deepseek_http_{status}", status)
                    data = bytearray()
                    async for chunk in response.aiter_bytes():
                        data.extend(chunk)
                        if len(data) > 2_000_000:
                            raise DeepSeekRequestError("deepseek_response_too_large")
                    return bytes(data)
            except httpx.TransportError:
                raise ConnectionError("deepseek_transport_unavailable") from None

        async with self._locks[tool]:
            return await self._runners[tool].call(request)

    async def search(
        self,
        query: str,
        as_of: datetime | None = None,
        region: str | None = None,
        max_results: int = 5,
        *,
        need_content: bool = False,
        ori_question: str | None = None,
        localization: str = "",
    ) -> tuple[SearchHitV1, ...]:
        if not 1 <= len(query) <= 128 or not query.strip():
            raise ValueError("deepseek_query_requires_1_to_128_characters")
        if type(max_results) is not int or not 1 <= max_results <= 50:
            raise ValueError("deepseek_count_requires_1_to_50")
        if ori_question is not None and not 1 <= len(ori_question) <= 128:
            raise ValueError("deepseek_original_question_requires_1_to_128_characters")
        if as_of is not None:
            raise ValueError("deepseek_live_search_cannot_provide_historical_as_of")
        if region:
            raise ValueError("deepseek_region_not_supported_use_explicit_localization_ip")
        if localization:
            ip_address(localization)  # Provider expects an IP, not a country/city or profile field.
        payload: dict[str, object] = {
            "query": query,
            "count": max_results,
            "need_content": need_content,
            "localization": localization,
        }
        if ori_question is not None:
            payload["ori_question"] = ori_question
        raw = await self._post("search", payload)
        try:
            response = _SearchResponse.model_validate_json(raw)
            for hit in response.results:
                validate_public_url(hit.url)
            now = datetime.now(UTC)
            return tuple(
                SearchHitV1(
                    hit_id=uuid5(NAMESPACE_URL, "deepseek:" + hit.url),
                    provider="deepseek",
                    url=hit.url,
                    title=hit.title,
                    snippet=hit.snippet,
                    summary=hit.summary,
                    content=hit.content,
                    site_name=hit.site_name,
                    published_at=hit.date,
                    retrieved_at=now,
                    provider_rank_score=hit.rerank_score,
                    provider_authority=hit.authority,
                    label="REAL",
                )
                for hit in response.results[:max_results]
            )
        except ValueError:
            raise DeepSeekRequestError("deepseek_invalid_search_response") from None

    async def fetch(self, url: str) -> FetchedPageV1:
        validate_public_url(url)
        if self.allowed_hosts is not None:
            host = (urlsplit(url).hostname or "").rstrip(".").lower().encode("idna").decode()
            if host not in self.allowed_hosts:
                raise ValueError("fetch_host_not_allowed")
            if self.resolve_dns:
                try:
                    addresses = await asyncio.wait_for(
                        asyncio.get_running_loop().getaddrinfo(host, 443, type=socket.SOCK_STREAM),
                        timeout=5,
                    )
                except (OSError, TimeoutError):
                    raise ValueError("fetch_dns_unavailable") from None
                if not addresses or any(not ip_address(row[4][0]).is_global for row in addresses):
                    raise ValueError("fetch_dns_not_public")
        raw = await self._post("fetch", {"url": url})
        try:
            response = _FetchResponse.model_validate_json(raw)
            if not response.content.strip():
                raise ValueError("empty_content")
            return FetchedPageV1(
                provider="deepseek",
                url=url,
                title=response.title,
                content=response.content,
                content_hash=sha256(response.content.encode()).hexdigest(),
                retrieved_at=datetime.now(UTC),
                label="REAL",
            )
        except ValueError:
            raise DeepSeekRequestError("deepseek_invalid_fetch_response") from None
