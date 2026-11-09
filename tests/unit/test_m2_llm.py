import asyncio
import json
from uuid import uuid4

import httpx
import pytest
from prediction_engine.contracts.models import ResearchNarrativeV1
from pydantic import SecretStr

from infra.providers.deepseek import DeepSeekRequestError
from infra.providers.deepseek_llm import DeepSeekLLMProvider


def output():
    return {
        "hypothesis": "Conditional synthetic hypothesis",
        "enabling_conditions": ["test"],
        "bottlenecks": ["reliability"],
        "opposing_explanations": ["integration cost"],
        "next_observable_signals": ["trial results"],
        "falsification_conditions": ["trial fails"],
        "cited_claim_ids": [str(uuid4())],
    }


def test_llm_json_and_bounded_request():
    body = output()

    def handler(request):
        data = json.loads(request.content)
        assert str(request.url) == "https://api.deepseek.com/chat/completions"
        assert data["model"] == "deepseek-flash" and data["max_tokens"] == 4096
        assert data["response_format"] == {"type": "json_object"}
        assert "tools" not in data
        return httpx.Response(
            200,
            json={
                "model": "deepseek-flash",
                "choices": [{"finish_reason": "stop", "message": {"content": json.dumps(body)}}],
                "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
            },
        )

    async def scenario():
        provider = DeepSeekLLMProvider(SecretStr("fake"), transport=httpx.MockTransport(handler))
        result = await provider.generate_structured(
            ResearchNarrativeV1, ("Return JSON", "data"), 4096, "trace"
        )
        assert result.hypothesis == body["hypothesis"]
        assert provider.usage["total_tokens"] == 30

    asyncio.run(scenario())


@pytest.mark.parametrize(
    "finish,content",
    [
        ("length", json.dumps(output())),
        ("stop", " "),
        ("tool_calls", "{}"),
        ("stop", '{"invented":"field"}'),
    ],
)
def test_llm_invalid_or_partial_content_is_not_success(finish, content):
    async def scenario():
        provider = DeepSeekLLMProvider(
            SecretStr("fake"),
            transport=httpx.MockTransport(
                lambda _: httpx.Response(
                    200,
                    json={
                        "model": "test",
                        "choices": [{"finish_reason": finish, "message": {"content": content}}],
                    },
                )
            ),
        )
        with pytest.raises(DeepSeekRequestError):
            await provider.generate_structured(ResearchNarrativeV1, ("JSON", "data"), 2000, "trace")

    asyncio.run(scenario())


def test_llm_error_does_not_retry_or_expose_key():
    calls = []

    def handler(request):
        calls.append(request)
        return httpx.Response(429, json={"error": {"message": "fake-private-key"}})

    async def scenario():
        provider = DeepSeekLLMProvider(
            SecretStr("fake-private-key"), transport=httpx.MockTransport(handler)
        )
        with pytest.raises(DeepSeekRequestError) as caught:
            await provider.generate_structured(ResearchNarrativeV1, ("JSON", "data"), 4096, "trace")
        assert len(calls) == 1 and "fake-private-key" not in str(caught.value)

    asyncio.run(scenario())
