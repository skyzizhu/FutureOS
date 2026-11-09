"""Encrypted dialogue, confirmed industry actions and existing report workflow."""

import asyncio
import logging
from datetime import timedelta
from time import monotonic
from typing import Any
from uuid import UUID, uuid4

from prediction_engine.contracts.models import (
    CommunityIndustryInputV1,
    ConversationCreateV1,
    ConversationMessageV1,
    FirstReportRequestV1,
)
from prediction_engine.evidence.temporal import utc
from prediction_engine.forecasting.harness import has_credential
from sqlalchemy import select
from sqlalchemy.orm import Session

from infra.accounts import session_user, vault_for
from infra.chat_admission import admit_global_model_turn
from infra.chat_agent import (
    SYSTEM_PROMPT,
    ChatTurn,
    gate_model_action,
    local_turn,
    model_available,
    model_turn,
)
from infra.chat_harness import POLICY_VERSION, assemble_context
from infra.community import CommunityRepository
from infra.db import ChatModelBudget, Job, ResearchConversation, utcnow
from infra.evidence_repository import EvidenceError
from infra.reports import ReportRepository
from infra.settings import Settings

logger = logging.getLogger(__name__)


class ConversationRepository:
    def __init__(self, session: Session, config: Settings):
        self.session, self.config = session, config
        self.community = CommunityRepository(session, config)

    def row(self, user_id: UUID, identifier: UUID) -> ResearchConversation:
        row = self.session.scalar(
            select(ResearchConversation).where(
                ResearchConversation.id == identifier, ResearchConversation.user_id == user_id
            )
        )
        if row is None:
            raise EvidenceError("CONVERSATION_NOT_FOUND", "研究对话不存在", 404)
        return row

    def content(self, row: ResearchConversation) -> dict[str, Any]:
        return vault_for(self.session, self.config).open(
            row.ciphertext, "conversation:" + str(row.user_id) + ":" + str(row.id)
        )

    def store(self, row: ResearchConversation, data: dict[str, Any]) -> None:
        row.ciphertext = vault_for(self.session, self.config).seal(
            data, "conversation:" + str(row.user_id) + ":" + str(row.id)
        )

    def view(
        self, user_id: UUID, identifier: UUID, *, include_harness: bool = False
    ) -> dict[str, Any]:
        row = self.row(user_id, identifier)
        data = self.content(row)
        job = self.session.get(Job, row.job_id) if row.job_id else None
        report_id = (
            (job.result or {}).get("report_id") if job and job.status == "succeeded" else None
        )
        return {
            "id": row.id,
            "industry_id": row.industry_id,
            "created_at": utc(row.created_at),
            "title": data["title"],
            "messages": data["messages"],
            "job_id": row.job_id,
            "job_status": job.status if job else None,
            "error_code": job.error_code if job else None,
            "report_id": report_id,
            "mode": "demo_reuse",
            "new_forecast_rules_pending": True,
            **(
                {
                    "harness_memory": data.get("harness_memory"),
                    "harness_events": data.get("harness_events", []),
                }
                if include_harness
                else {}
            ),
        }

    def reserve_model_turn(self, user_id: UUID) -> UUID:
        if not model_available(self.config):
            raise EvidenceError("CHAT_MODEL_DISABLED", "当前可使用本地对话，模型服务尚未启用", 409)
        budget = self.session.get(ChatModelBudget, user_id)
        now = utcnow()
        if budget is None:
            budget = ChatModelBudget(user_id=user_id, window_start=now, turns=0)
            self.session.add(budget)
        if budget.lease_until and utc(budget.lease_until) > now:
            raise EvidenceError("CHAT_BUSY", "上一条模型回复仍在处理中，请稍候", 409)
        if utc(budget.window_start) + timedelta(minutes=15) <= now:
            budget.window_start, budget.turns = now, 0
        if budget.turns >= 10:
            raise EvidenceError("CHAT_RATE_LIMIT", "模型对话过于频繁，请稍后再试", 429)
        admit_global_model_turn(self.session, self.config, now)
        lease = uuid4()
        budget.turns += 1
        budget.lease_id, budget.lease_until = lease, now + timedelta(seconds=20)
        self.session.commit()
        return lease

    def reply(
        self,
        user_id: UUID,
        industry_id: UUID | None,
        content: dict[str, Any],
        use_model: bool,
        include_memory: bool,
        token: str,
    ) -> ChatTurn:
        messages = content["messages"]
        history = [{"role": m["role"], "text": m["text"]} for m in messages]
        scope = self.community.industry(industry_id, user_id).name if industry_id else None
        if not scope:
            for message in reversed(messages):
                proposal = message.get("proposal")
                if proposal and proposal["status"] in {"added", "already_exists"}:
                    scope = proposal["name"]
                    break
        if has_credential(history[-1]["text"]):
            raise EvidenceError("CHAT_INPUT_BLOCKED", "消息含有疑似凭据，请移除后再发送", 422)
        context = assemble_context(
            history, scope, include_memory=include_memory, system_bytes=len(SYSTEM_PROMPT.encode())
        )
        content["harness_memory"] = {"version": POLICY_VERSION, "mentions": context.memory}
        if not use_model:
            return local_turn(history, scope)
        lease = self.reserve_model_turn(user_id)
        started = monotonic()
        try:
            turn, usage = asyncio.run(model_turn(self.config, context, lease))
        except EvidenceError as exc:
            logger.warning("chat_provider_rejected trace=%s reason=%s", lease, exc.code)
            self.release_model_turn(user_id, lease)
            self.session.commit()
            raise
        self.release_model_turn(user_id, lease)
        user = session_user(self.session, token)
        if user is None or user.id != user_id:
            self.session.commit()
            raise EvidenceError("AUTH_REQUIRED", "会话已失效，请重新登录", 401)
        result = gate_model_action(turn, history)
        content.setdefault("harness_events", []).append(
            {
                "policy": POLICY_VERSION,
                "trace_id": str(lease),
                "kind": "model_reply",
                "at": utcnow().isoformat(),
                "elapsed_ms": round((monotonic() - started) * 1000),
                "usage": usage,
                "context_digest": context.digest,
                "context_bytes": context.bytes,
                "message_count": context.included_messages,
                "memory_sent": include_memory and bool(context.memory),
                "action_blocked": turn is not result,
            }
        )
        return result

    def release_model_turn(self, user_id: UUID, lease: UUID) -> None:
        self.session.expire_all()
        self.community.fence(user_id)
        budget = self.session.get(ChatModelBudget, user_id)
        if budget and budget.lease_id == lease:
            budget.lease_id = budget.lease_until = None

    def append_reply(
        self,
        user_id: UUID,
        content: dict[str, Any],
        turn: ChatTurn,
        use_model: bool,
    ) -> None:
        message: dict[str, Any] = {
            "role": "assistant",
            "text": turn.reply,
            "source": "llm" if use_model else "local",
        }
        if turn.intent == "add_industry" and turn.proposal:
            name = turn.proposal.name
            existing = self.community.find_personal_industry(user_id, name)
            proposal_id = str(uuid4())
            message["proposal"] = {
                "id": proposal_id,
                "name": existing.name if existing else name,
                "status": "already_exists" if existing else "pending",
                "industry_id": str(existing.id) if existing else None,
            }
            if existing:
                message["text"] = "你的行业列表中已有这个行业，可以继续在这里讨论。"
            else:
                content.setdefault("proposal_domains", {})[proposal_id] = turn.proposal.domain
        content["messages"].append(message)

    def prior_create(
        self, user_id: UUID, data: ConversationCreateV1
    ) -> ResearchConversation | None:
        prior = self.session.scalar(
            select(ResearchConversation).where(
                ResearchConversation.user_id == user_id,
                ResearchConversation.client_id == data.client_id,
            )
        )
        if prior and (
            prior.industry_id != data.industry_id
            or self.content(prior)["messages"][0]["text"] != data.question.strip()
        ):
            raise EvidenceError("IDEMPOTENCY_CONFLICT", "同一请求不能更换问题", 409)
        return prior

    def create(self, user_id: UUID, data: ConversationCreateV1, token: str) -> dict[str, Any]:
        self.community.fence(user_id)
        prior = self.prior_create(user_id, data)
        if prior:
            return self.view(user_id, prior.id)
        question = data.question.strip()
        if not question:
            raise EvidenceError("QUESTION_EMPTY", "请先输入想研究的问题", 422)
        content: dict[str, Any] = {
            "title": question,
            "messages": [{"role": "user", "text": question, "client_id": str(data.client_id)}],
        }
        turn = self.reply(
            user_id, data.industry_id, content, data.use_model, data.include_memory, token
        )
        if data.use_model:
            prior = self.prior_create(user_id, data)
            if prior:
                self.session.commit()
                return self.view(user_id, prior.id)
            if data.industry_id:
                self.community.industry(data.industry_id, user_id)
        row = ResearchConversation(
            id=uuid4(),
            user_id=user_id,
            client_id=data.client_id,
            industry_id=data.industry_id,
            ciphertext="",
        )
        self.append_reply(user_id, content, turn, data.use_model)
        self.store(row, content)
        self.session.add(row)
        self.session.commit()
        return self.view(user_id, row.id)

    @staticmethod
    def already_received(content: dict[str, Any], data: ConversationMessageV1) -> bool:
        for message in content["messages"]:
            if message.get("client_id") == str(data.client_id):
                if message["text"] != data.text.strip():
                    raise EvidenceError("IDEMPOTENCY_CONFLICT", "同一请求不能更换消息", 409)
                return True
        return False

    def message(
        self, user_id: UUID, identifier: UUID, data: ConversationMessageV1, token: str
    ) -> dict[str, Any]:
        self.community.fence(user_id)
        row = self.row(user_id, identifier)
        content = self.content(row)
        if self.already_received(content, data):
            return self.view(user_id, identifier)
        if len(content["messages"]) >= 40 or not data.text.strip():
            raise EvidenceError("CHAT_LIMIT", "请开启新的研究对话，或输入有效内容", 422)
        original = row.ciphertext
        content["messages"].append(
            {"role": "user", "text": data.text.strip(), "client_id": str(data.client_id)}
        )
        turn = self.reply(
            user_id, row.industry_id, content, data.use_model, data.include_memory, token
        )
        if data.use_model:
            row = self.row(user_id, identifier)
            if row.ciphertext != original:
                if self.already_received(self.content(row), data):
                    self.session.commit()
                    return self.view(user_id, identifier)
                self.session.commit()
                raise EvidenceError("CHAT_STATE_CHANGED", "对话已更新，请刷新后重试", 409)
            if row.industry_id:
                self.community.industry(row.industry_id, user_id)
        self.append_reply(user_id, content, turn, data.use_model)
        self.store(row, content)
        self.session.commit()
        return self.view(user_id, identifier)

    def confirm_industry(
        self, user_id: UUID, identifier: UUID, proposal_id: UUID
    ) -> dict[str, Any]:
        self.community.fence(user_id)
        row = self.row(user_id, identifier)
        content = self.content(row)
        for message in content["messages"]:
            proposal = message.get("proposal")
            if not proposal or proposal["id"] != str(proposal_id):
                continue
            if proposal["status"] == "pending":
                name = proposal["name"]
                existing = self.community.find_personal_industry(user_id, name)
                domain = content["proposal_domains"].pop(str(proposal_id))
                industry_id = (
                    existing.id
                    if existing
                    else self.community.create(
                        user_id,
                        CommunityIndustryInputV1(
                            name=name,
                            description="从未来决策对话添加，用于关注这个行业的变化。",
                            domain=domain,
                        ),
                        commit=False,
                    ).id
                )
                proposal["status"] = "already_exists" if existing else "added"
                proposal["industry_id"] = str(industry_id)
                content.setdefault("harness_events", []).append(
                    {
                        "policy": POLICY_VERSION,
                        "kind": "add_private_industry",
                        "proposal_id": str(proposal_id),
                        "outcome": proposal["status"],
                        "at": utcnow().isoformat(),
                    }
                )
                self.store(row, content)
                self.session.commit()
            return self.view(user_id, identifier)
        raise EvidenceError("CHAT_PROPOSAL_NOT_FOUND", "这条行业建议不存在", 404)

    def start(self, user_id: UUID, identifier: UUID) -> dict[str, Any]:
        self.community.fence(user_id)
        row = self.row(user_id, identifier)
        if row.job_id:
            return self.view(user_id, identifier)
        # Reuse the same entitlement, immutable inputs and durable worker. No new rules/LLM calls.
        repo = ReportRepository(self.session, self.config)
        from prediction_engine.contracts.models import ResearchIntakeV1

        intake = repo.intake(user_id, ResearchIntakeV1(label="DEMO"))
        accepted = repo.submit(
            user_id,
            FirstReportRequestV1(label="DEMO", forecast_version_ids=intake.matched_version_ids),
            "conversation:" + str(identifier),
        )
        # submit is idempotent: a restart between commits can safely reconnect this same job.
        self.community.fence(user_id)
        row = self.row(user_id, identifier)
        row.job_id = accepted.job_id
        self.session.commit()
        return self.view(user_id, identifier)
