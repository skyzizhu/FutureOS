"""Single bounded JSON completion; no tools, automatic retry or public publication."""

from typing import Any, TypeVar

import httpx
from pydantic import BaseModel, SecretStr

from infra.providers.deepseek import DeepSeekRequestError

T = TypeVar("T", bound=BaseModel)


class DeepSeekLLMProvider:
    def __init__(
        self,
        key: SecretStr,
        model: str = "deepseek-flash",
        *,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._key = key
        self.model_id = model
        self.actual_model_id = model
        self.usage: dict[str, Any] = {}
        self.transport = transport

    async def generate_structured(
        self, schema: type[T], messages: tuple[str, ...], budget: int, trace_context: str
    ) -> T:
        if not 1 <= budget <= 4096 or sum(map(len, messages)) > 50_000:
            raise ValueError("RESEARCH_MODEL_BUDGET_EXCEEDED")
        try:
            async with httpx.AsyncClient(
                base_url="https://api.deepseek.com",
                timeout=90,
                follow_redirects=False,
                trust_env=False,
                transport=self.transport,
            ) as client:
                async with client.stream(
                    "POST",
                    "/chat/completions",
                    headers={
                        "Authorization": "Bearer " + self._key.get_secret_value(),
                        "X-Request-ID": trace_context,
                    },
                    json={
                        "model": self.model_id,
                        "messages": [
                            {"role": "system" if i == 0 else "user", "content": message}
                            for i, message in enumerate(messages)
                        ],
                        "thinking": {"type": "disabled"},
                        "response_format": {"type": "json_object"},
                        "temperature": 0,
                        "max_tokens": budget,
                        "stream": False,
                    },
                ) as response:
                    if response.status_code != 200:
                        raise DeepSeekRequestError(
                            f"RESEARCH_MODEL_HTTP_{response.status_code}", response.status_code
                        )
                    payload = bytearray()
                    async for chunk in response.aiter_bytes():
                        payload.extend(chunk)
                        if len(payload) > 1_000_000:
                            raise DeepSeekRequestError("RESEARCH_MODEL_RESPONSE_TOO_LARGE")
            import json

            envelope = json.loads(payload)
            choice = envelope["choices"][0]
            message = choice["message"]
            if (
                choice["finish_reason"] != "stop"
                or message.get("role", "assistant") != "assistant"
                or message.get("tool_calls")
                or message.get("function_call")
            ):
                raise ValueError("incomplete_or_tool_response")
            result = schema.model_validate_json(message["content"])
            self.actual_model_id = str(envelope["model"])
            usage = envelope.get("usage", {})
            self.usage = {
                key: value
                for key, value in usage.items()
                if key in {"prompt_tokens", "completion_tokens", "total_tokens"}
                and isinstance(value, int)
                and value >= 0
            }
            fingerprint = envelope.get("system_fingerprint")
            if isinstance(fingerprint, str):
                self.usage["system_fingerprint"] = fingerprint
            return result
        except httpx.TransportError:
            raise DeepSeekRequestError("RESEARCH_MODEL_TRANSPORT_UNCERTAIN") from None
        except (ValueError, KeyError, IndexError, TypeError):
            raise DeepSeekRequestError("RESEARCH_MODEL_INVALID_JSON_OR_SCHEMA") from None
