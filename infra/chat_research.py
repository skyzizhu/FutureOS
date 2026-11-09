"""Conversation-owned DEMO research on the durable worker queue."""

from uuid import UUID, uuid4

from prediction_engine.contracts.models import (
    ChatResearchStartV1,
    ChatResearchViewV1,
    IndustryResearchRunV1,
    IndustryResearchScopeV1,
    IndustryResearchStage,
)
from prediction_engine.evidence.temporal import utc
from prediction_engine.forecasting.harness import public_search_term
from prediction_engine.forecasting.industry_agent import IndustryAgent
from prediction_engine.forecasting.workflow import hashed
from sqlalchemy import Select, select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from infra.accounts import vault_for
from infra.community import CommunityRepository
from infra.db import (
    AuthAccount,
    ChatIndustryResearch,
    Job,
    OutboxEvent,
    ResearchConversation,
    utcnow,
)
from infra.evidence_repository import EvidenceError
from infra.job_budget import enforce_queue_budget
from infra.providers.industry_demo import DemoIndustryProviders
from infra.settings import Settings

CHAT_RESEARCH_TASK = "chat_industry_research"
ACTIVE = {"queued", "running", "failed_retryable"}


def scope_key(job_id: UUID) -> str:
    return "chat-research-scope:" + str(job_id)


def result_key(job_id: UUID) -> str:
    return "chat-research-result:" + str(job_id)


class ChatResearchRepository:
    def __init__(self, session: Session, config: Settings) -> None:
        self.session, self.config = session, config
        self.community = CommunityRepository(session, config)

    def rows(
        self, conversation: ResearchConversation, job_id: UUID | None = None
    ) -> Select[tuple[Job, ChatIndustryResearch]]:
        query = (
            select(Job, ChatIndustryResearch)
            .join(ChatIndustryResearch, ChatIndustryResearch.job_id == Job.id)
            .where(
                ChatIndustryResearch.conversation_id == conversation.id,
                Job.user_id == conversation.user_id,
            )
        )
        return query.where(Job.id == job_id) if job_id else query

    def view(
        self, job: Job, run: ChatIndustryResearch, *, detail: bool = False
    ) -> ChatResearchViewV1:
        vault = vault_for(self.session, self.config)
        scope = vault.open(run.scope_ciphertext, scope_key(job.id))
        result = (
            vault.open(run.result_ciphertext, result_key(job.id))
            if detail and job.status == "succeeded" and run.result_ciphertext
            else None
        )
        return ChatResearchViewV1.model_validate(
            {
                "id": job.id,
                "industry": scope["scope"]["industry"],
                "horizon_days": scope["scope"]["horizon_days"],
                "status": job.status,
                "stages": run.stages,
                "error_code": job.error_code,
                "created_at": utc(job.created_at),
                "result": result,
            }
        )

    def list(
        self, conversation: ResearchConversation, *, export: bool = False
    ) -> list[ChatResearchViewV1]:
        query = self.rows(conversation).order_by(Job.created_at.desc(), Job.id.desc())
        return [
            self.view(job, run, detail=export)
            for job, run in self.session.execute(query if export else query.limit(20))
        ]

    def detail(self, conversation: ResearchConversation, job_id: UUID) -> ChatResearchViewV1:
        pair = self.session.execute(self.rows(conversation, job_id)).one_or_none()
        if pair is None:
            raise EvidenceError("CHAT_RESEARCH_NOT_FOUND", "这项研究不存在", 404)
        job, run = pair
        return self.view(job, run, detail=True)

    def start(
        self, conversation: ResearchConversation, data: ChatResearchStartV1
    ) -> ChatResearchViewV1:
        owner = conversation.user_id
        self.community.fence(owner)
        if self.session.get(ResearchConversation, conversation.id, populate_existing=True) is None:
            raise EvidenceError("CONVERSATION_NOT_FOUND", "研究对话不存在", 404)
        key = f"chat-industry:{conversation.id}:{data.client_id}"
        digest = hashed(data.model_dump(mode="json"))
        prior = self.session.scalar(
            select(Job).where(Job.user_id == owner, Job.idempotency_key == key)
        )
        if prior:
            if prior.input_hash != digest:
                raise EvidenceError("IDEMPOTENCY_CONFLICT", "同一请求不能更换研究范围", 409)
            return self.detail(conversation, prior.id)
        if self.session.execute(
            self.rows(conversation).where(Job.status.in_(ACTIVE)).limit(1)
        ).first():
            raise EvidenceError("CHAT_RESEARCH_RUNNING", "这段对话已有研究在进行", 409)
        enforce_queue_budget(self.session, owner, self.config.queue_max_pending_per_user)
        industry = self.community.industry(data.industry_id, owner)
        if not public_search_term(industry.name):
            raise EvidenceError(
                "CHAT_RESEARCH_SCOPE_INVALID", "请选择不含链接或私人信息的行业名称", 422
            )
        scope = IndustryResearchScopeV1(industry=industry.name, horizon_days=data.horizon_days)
        job = Job(
            id=uuid4(),
            user_id=owner,
            task_type=CHAT_RESEARCH_TASK,
            idempotency_key=key,
            input_hash=digest,
            payload={"label": "DEMO"},
        )
        self.session.add(job)
        self.session.flush()
        vault = vault_for(self.session, self.config)
        run = ChatIndustryResearch(
            job_id=job.id,
            conversation_id=conversation.id,
            scope_ciphertext=vault.seal(
                {"scope": scope.model_dump(mode="json"), "industry_id": str(industry.id)},
                scope_key(job.id),
            ),
        )
        self.session.add(run)
        self.session.add(
            OutboxEvent(
                job_id=job.id,
                event_type="ChatIndustryResearchRequested.v1",
                payload={"job_id": str(job.id), "label": "DEMO"},
            )
        )
        self.session.commit()
        return self.view(job, run)

    def cancel(self, conversation: ResearchConversation, job_id: UUID | None = None) -> None:
        self.community.fence(conversation.user_id)
        pairs = self.session.execute(self.rows(conversation, job_id).with_for_update(of=Job)).all()
        if job_id is not None and not pairs:
            raise EvidenceError("CHAT_RESEARCH_NOT_FOUND", "这项研究不存在", 404)
        for job, _ in pairs:
            if job.status in ACTIVE:
                job.status, job.error_code = "cancelled", "USER_CANCELLED"
                job.lease_token = job.lease_until = None
                job.updated_at = utcnow()
            if job_id is None:
                job.idempotency_key, job.input_hash = "erased:" + str(job.id), "0" * 64


async def execute_chat_research(
    engine: Engine, config: Settings, job_id: UUID, lease: UUID
) -> dict[str, object]:
    with Session(engine) as session:
        job, run = leased_run(session, job_id, lease)
        frozen = vault_for(session, config).open(run.scope_ciphertext, scope_key(job.id))
        account = session.get(AuthAccount, job.user_id)
        if account is None or not account.enabled:
            raise ValueError("CHAT_RESEARCH_ACCOUNT_UNAVAILABLE")
        CommunityRepository(session, config).industry(UUID(frozen["industry_id"]), job.user_id)
        scope = IndustryResearchScopeV1.model_validate(frozen["scope"])
        started_at, trace = utc(job.created_at), str(job.trace_id)
        run.stages = []
        session.commit()

    def record_stage(stage: IndustryResearchStage) -> None:
        with Session(engine) as session:
            _, run = leased_run(session, job_id, lease)
            run.stages = [*run.stages, {"stage": stage, "started_at": utcnow().isoformat()}]
            session.commit()

    providers = DemoIndustryProviders()
    result = await IndustryAgent(providers, providers, providers).run(
        scope, started_at, trace, on_stage=record_stage
    )
    return result.model_dump(mode="json")


def leased_run(session: Session, job_id: UUID, lease: UUID) -> tuple[Job, ChatIndustryResearch]:
    job = session.scalar(select(Job).where(Job.id == job_id).with_for_update())
    if (
        job is None
        or job.lease_token != lease
        or job.status != "running"
        or not job.lease_until
        or utc(job.lease_until) <= utcnow()
    ):
        raise ValueError("CHAT_RESEARCH_LEASE_LOST")
    run = session.get(ChatIndustryResearch, job.id)
    if run is None:
        raise ValueError("CHAT_RESEARCH_NOT_FOUND")
    return job, run


def persist_chat_research(
    session: Session, config: Settings, job: Job, result: dict[str, object]
) -> None:
    if job.lease_token is None:
        raise ValueError("CHAT_RESEARCH_LEASE_LOST")
    _, run = leased_run(session, job.id, job.lease_token)
    account = session.get(AuthAccount, job.user_id)
    if account is None or not account.enabled:
        raise ValueError("CHAT_RESEARCH_ACCOUNT_UNAVAILABLE")
    vault = vault_for(session, config)
    frozen = vault.open(run.scope_ciphertext, scope_key(job.id))
    CommunityRepository(session, config).industry(UUID(frozen["industry_id"]), job.user_id)
    report = IndustryResearchRunV1.model_validate(result)
    run.result_ciphertext = vault.seal(report.model_dump(mode="json"), result_key(job.id))
