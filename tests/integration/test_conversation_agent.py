import json
from uuid import uuid4

from pydantic import SecretStr
from sqlalchemy.orm import Session

from infra.accounts import token_hash
from infra.db import AuthSession, utcnow
from infra.providers.deepseek_llm import DeepSeekLLMProvider
from tests.integration.test_m4_reports import account, profile

INDUSTRIES = "/api/v1/me/community/industries"
CHAT = "/api/v1/me/conversations"


def test_profile_industry_is_private_first_and_idempotent(runtime):
    client, _, _ = runtime
    owner, _, _ = account(client)
    other, _, _ = account(client)
    manual = client.post(
        INDUSTRIES,
        headers=owner,
        json={"name": "人形机器人", "domain": "manufacturing", "description": "观察供应链"},
    ).json()
    profile(client, owner)
    profile(client, owner)
    items = client.get(INDUSTRIES, headers=owner).json()
    assert [item["name"] for item in items] == ["软件开发", "人形机器人"]
    first = items[0]
    assert first["owned"] and not first["public"]
    assert client.get(f"{INDUSTRIES}/{first['id']}", headers=other).status_code == 404

    profile(client, owner, industry_l1_code="energy", industry_l2_code="storage")
    items = client.get(INDUSTRIES, headers=owner).json()
    assert [item["name"] for item in items] == ["储能", "人形机器人", "软件开发"]
    assert items[1]["id"] == manual["id"]
    profile(client, owner, industry_l1_code="not_applicable", industry_l2_code="student")
    assert len(client.get(INDUSTRIES, headers=owner).json()) == 3


def test_unscoped_chat_clarifies_addition_then_confirms_once(runtime):
    client, _, _ = runtime
    owner, _, _ = account(client)
    other, _, _ = account(client)
    opened = client.post(
        CHAT, headers=owner, json={"question": "帮我添加行业", "client_id": str(uuid4())}
    )
    assert opened.status_code == 201, opened.text
    chat = opened.json()
    assert chat["industry_id"] is None
    assert chat["messages"][-1]["source"] == "local"
    assert chat["messages"][-1]["proposal"] is None
    url = f"{CHAT}/{chat['id']}"
    reply = client.post(
        url + "/messages", headers=owner, json={"text": "储能", "client_id": str(uuid4())}
    )
    assert reply.status_code == 200, reply.text
    proposal = reply.json()["messages"][-1]["proposal"]
    assert proposal["status"] == "pending" and proposal["name"] == "储能"
    assert client.get(INDUSTRIES, headers=owner).json() == []
    confirm_url = f"{url}/industries/{proposal['id']}"
    assert client.post(confirm_url, headers=other).status_code == 404
    confirmed = client.post(confirm_url, headers=owner)
    assert confirmed.status_code == 200, confirmed.text
    added = confirmed.json()["messages"][-1]["proposal"]
    assert added["status"] == "added" and added["industry_id"]
    assert client.post(confirm_url, headers=owner).json() == confirmed.json()

    duplicate = client.post(
        url + "/messages",
        headers=owner,
        json={"text": "把储能行业加入我的行业", "client_id": str(uuid4())},
    )
    assert duplicate.json()["messages"][-1]["proposal"]["status"] == "already_exists"
    items = client.get(INDUSTRIES, headers=owner).json()
    assert len(items) == 1 and items[0]["id"] == added["industry_id"]
    assert not items[0]["public"]


def test_model_gated_contextual_and_schema_limited(runtime, monkeypatch):
    client, _, config = runtime
    owner, _, _ = account(client)
    profile(client, owner, occupation_text="PRIVATE_PROFILE_NEVER_SEND")
    payload = {"question": "我的职业未来会怎样？", "client_id": str(uuid4()), "use_model": True}
    assert (
        client.get("/api/v1/me/chat-capabilities", headers=owner).json()["model_available"] is False
    )
    assert client.post(CHAT, headers=owner, json=payload).status_code == 409
    assert client.get(CHAT, headers=owner).json() == []
    monkeypatch.setattr(config, "deepseek_api_key", SecretStr("test-key"))
    monkeypatch.setattr(config, "live_chat_enabled", True)
    calls = []

    async def fake_model(self, schema, messages, budget, trace_context):
        assert "个人未来决策" in messages[0]
        assert "PRIVATE_PROFILE_NEVER_SEND" not in messages[1]
        calls.append(json.loads(messages[1]))
        assert budget == 1024
        return schema.model_validate(
            {"intent": "clarify", "reply": "你更想看岗位变化，还是转型机会？"}
        )

    monkeypatch.setattr(DeepSeekLLMProvider, "generate_structured", fake_model)
    assert (
        client.get("/api/v1/me/chat-capabilities", headers=owner).json()["model_available"] is True
    )
    opened = client.post(CHAT, headers=owner, json=payload)
    assert opened.status_code == 201, opened.text
    chat = opened.json()
    assert chat["messages"][-1]["source"] == "llm"
    assert client.post(CHAT, headers=owner, json=payload).json() == chat
    followup = client.post(
        f"{CHAT}/{chat['id']}/messages",
        headers=owner,
        json={"text": "转型机会", "client_id": str(uuid4()), "use_model": True},
    )
    assert followup.status_code == 200, followup.text
    assert len(calls) == 2
    assert [message["role"] for message in calls[-1]["dialogue"]] == [
        "user",
        "assistant",
        "user",
    ]
    assert calls[-1]["dialogue"][-1]["text"] == "转型机会"


def test_harness_blocks_unsafe_io_and_limits_provider_across_accounts(runtime, monkeypatch):
    client, _, config = runtime
    owner, _, _ = account(client)
    other, _, _ = account(client)
    monkeypatch.setattr(config, "deepseek_api_key", SecretStr("test-key"))
    monkeypatch.setattr(config, "live_chat_enabled", True)
    monkeypatch.setattr(config, "chat_model_global_window_limit", 1)
    calls = []

    async def fake_model(self, schema, messages, budget, trace_context):
        calls.append(trace_context)
        return schema.model_validate({"intent": "other", "reply": "<script>invalid</script>"})

    monkeypatch.setattr(DeepSeekLLMProvider, "generate_structured", fake_model)
    base = {"client_id": str(uuid4()), "use_model": True}
    response = client.post(
        CHAT, headers=owner, json={**base, "question": "api_key=example_secret_123456"}
    )
    assert response.status_code == 422 and response.json()["code"] == "CHAT_INPUT_BLOCKED"
    assert calls == []
    response = client.post(CHAT, headers=owner, json={**base, "question": "我想讨论储能"})
    assert response.status_code == 422 and response.json()["code"] == "CHAT_OUTPUT_BLOCKED"
    assert client.get(CHAT, headers=owner).json() == []
    response = client.post(CHAT, headers=other, json={**base, "question": "我想讨论储能"})
    assert response.status_code == 429 and response.json()["code"] == "CHAT_SERVICE_BUSY"
    assert len(calls) == 1


def test_harness_discards_model_reply_when_session_revoked(runtime, monkeypatch):
    client, engine, config = runtime
    owner, _, _ = account(client)
    monkeypatch.setattr(config, "deepseek_api_key", SecretStr("test-key"))
    monkeypatch.setattr(config, "live_chat_enabled", True)

    async def fake_model(self, schema, messages, budget, trace_context):
        with Session(engine) as session:
            entry = session.get(AuthSession, token_hash(owner["Authorization"].split()[1]))
            assert entry is not None
            entry.revoked_at = utcnow()
            session.commit()
        return schema.model_validate({"intent": "clarify", "reply": "你关注什么？"})

    monkeypatch.setattr(DeepSeekLLMProvider, "generate_structured", fake_model)
    response = client.post(
        CHAT,
        headers=owner,
        json={"client_id": str(uuid4()), "use_model": True, "question": "储能趋势是什么"},
    )
    assert response.status_code == 401 and response.json()["code"] == "AUTH_REQUIRED"
