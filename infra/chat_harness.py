"""Scoped chat memory and bounded provider input. All retained facts are conversation-local."""

import json
import re
from dataclasses import dataclass
from hashlib import sha256
from typing import TypedDict

from prediction_engine.forecasting.harness import external_text

POLICY_VERSION = "chat-harness-v1"
MAX_CONTEXT_BYTES = 10_000
MAX_RECENT_MESSAGES = 7

_MEMORY_FIELDS = (
    ("region", re.compile(r"国内|中国|海外|全球|美国|欧洲|日本|韩国|东南亚")),
    (
        "horizon",
        re.compile(r"(?:未来|接下来|近)[一二两三四五六七八九十半\d]{1,4}(?:个?月|年|季度)"),
    ),
    ("decision", re.compile(r"跳槽|转行|求职|升职|学习|创业|消费|节约|理财|健身|养生")),
)


class MemoryItem(TypedDict):
    field: str
    mention: str
    message_index: int


@dataclass(frozen=True)
class ChatContext:
    payload: str
    memory: tuple[MemoryItem, ...]
    bytes: int
    included_messages: int
    digest: str


def assemble_context(
    history: list[dict[str, str]],
    scope: str | None,
    *,
    include_memory: bool,
    system_bytes: int,
) -> ChatContext:
    start = max(0, len(history) - MAX_RECENT_MESSAGES)
    mentions: dict[str, MemoryItem] = {}
    for index, message in enumerate(history):
        if message["role"] != "user":
            continue
        for field, pattern in _MEMORY_FIELDS:
            matches = list(pattern.finditer(external_text(message["text"])))
            if matches:
                mentions[field] = {
                    "field": field,
                    "mention": matches[-1].group(),
                    "message_index": index,
                }

    while True:
        memory = tuple(item for item in mentions.values() if item["message_index"] < start)
        payload = json.dumps(
            {
                "selected_industry": external_text(scope) if scope else None,
                "dialogue": [
                    {"role": message["role"], "text": external_text(message["text"])}
                    for message in history[start:]
                ],
                "historical_mentions": memory if include_memory else (),
            },
            ensure_ascii=False,
            separators=(",", ":"),
        )
        encoded = payload.encode()
        size = len(encoded) + system_bytes
        if size <= MAX_CONTEXT_BYTES:
            return ChatContext(
                payload, memory, size, len(history) - start, sha256(encoded).hexdigest()
            )
        if start >= len(history) - 1:
            raise ValueError("CHAT_CONTEXT_TOO_LARGE")
        # Drop a complete oldest turn so the recent transcript starts with a user message.
        start += 2 if history[start]["role"] == "user" else 1


def action_requested(text: str) -> bool:
    return bool(
        re.search(
            r"(?:添加|加入|新增|帮我加|加到|加进).{0,65}(?:行业|列表)"
            r"|^(?:请)?(?:帮我)?(?:添加|新增|加入)\s*\S"
            r"|\b(?:add|save)\b.{1,90}\b(?:industry|list|watchlist)\b",
            text,
            re.IGNORECASE,
        )
    )
