from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import (
    JSON,
    BigInteger,
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Integer,
    String,
    UniqueConstraint,
    Uuid,
    create_engine,
    event,
    text,
)
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker


class Base(DeclarativeBase):
    pass


def utcnow() -> datetime:
    return datetime.now(UTC)


class User(Base):
    __tablename__ = "users"
    __table_args__ = (CheckConstraint("role IN ('user','admin')", name="ck_user_role"),)
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    auth_subject: Mapped[str] = mapped_column(String(200), unique=True)
    role: Mapped[str] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Job(Base):
    __tablename__ = "jobs"
    __table_args__ = (
        UniqueConstraint("user_id", "idempotency_key", name="uq_job_user_key"),
        CheckConstraint("attempts >= 0", name="ck_job_attempts"),
        CheckConstraint(
            "status IN ('queued','running','succeeded','failed_retryable',"
            "'failed_terminal','cancelled')",
            name="ck_job_status",
        ),
    )
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    request_id: Mapped[UUID] = mapped_column(Uuid, unique=True, default=uuid4)
    trace_id: Mapped[UUID] = mapped_column(Uuid, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    task_type: Mapped[str] = mapped_column(String(80), default="demo_research")
    idempotency_key: Mapped[str] = mapped_column(String(128))
    input_hash: Mapped[str] = mapped_column(String(64))
    payload: Mapped[dict[str, Any]] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(30), default="queued", index=True)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    lease_token: Mapped[UUID | None] = mapped_column(Uuid)
    lease_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    available_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    result: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    error_code: Mapped[str | None] = mapped_column(String(80))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class OutboxEvent(Base):
    __tablename__ = "outbox_events"
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    job_id: Mapped[UUID] = mapped_column(ForeignKey("jobs.id"), index=True)
    event_type: Mapped[str] = mapped_column(String(80))
    payload_version: Mapped[int] = mapped_column(Integer, default=1)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON)
    emitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class InboxProcessed(Base):
    __tablename__ = "inbox_processed"
    consumer: Mapped[str] = mapped_column(String(80), primary_key=True)
    event_id: Mapped[UUID] = mapped_column(
        ForeignKey("outbox_events.id"), primary_key=True, index=True
    )
    processed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


def make_engine(url: str) -> Engine:
    if url.startswith("sqlite:///") and ":memory:" not in url:
        Path(url.removeprefix("sqlite:///")).parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(
        url,
        pool_pre_ping=True,
        **({"connect_args": {"check_same_thread": False}} if url.startswith("sqlite") else {}),
    )
    if url.startswith("sqlite"):

        @event.listens_for(engine, "connect")
        def sqlite_fk(connection: Any, _: Any) -> None:
            connection.execute("PRAGMA foreign_keys=ON")

    return engine


def session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(engine, expire_on_commit=False)


# M1 evidence persistence. Domain contracts and temporal/dedup rules stay in the core package.
from sqlalchemy import Float, Text  # noqa: E402


class SourceGroup(Base):
    __tablename__ = "source_groups"
    __table_args__ = (UniqueConstraint("label", "fingerprint", name="uq_source_group"),)
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    fingerprint: Mapped[str] = mapped_column(String(64))
    label: Mapped[str] = mapped_column(String(10))


class SourceDocument(Base):
    __tablename__ = "source_documents"
    __table_args__ = (UniqueConstraint("label", "url_hash", name="uq_source_url"),)
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    canonical_url: Mapped[str] = mapped_column(Text)
    url_hash: Mapped[str] = mapped_column(String(64))
    label: Mapped[str] = mapped_column(String(10))
    ingested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class SourceVersion(Base):
    __tablename__ = "source_versions"
    __table_args__ = (
        UniqueConstraint("source_id", "snapshot_hash", name="uq_source_snapshot"),
        CheckConstraint(
            "available_at IS NULL OR published_at IS NULL OR available_at >= published_at",
            name="ck_source_available",
        ),
    )
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    source_id: Mapped[UUID] = mapped_column(ForeignKey("source_documents.id"), index=True)
    source_group_id: Mapped[UUID] = mapped_column(ForeignKey("source_groups.id"), index=True)
    version_label: Mapped[str] = mapped_column(String(80))
    snapshot_hash: Mapped[str] = mapped_column(String(64))
    content_hash: Mapped[str] = mapped_column(String(64), index=True)
    content: Mapped[str] = mapped_column(Text)
    title: Mapped[str] = mapped_column(String(4000))
    publisher: Mapped[str] = mapped_column(String(4000))
    source_type: Mapped[str] = mapped_column(String(30))
    original_language: Mapped[str] = mapped_column(String(80))
    region: Mapped[str] = mapped_column(String(200))
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    event_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    available_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    ingested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    revised_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    availability_basis: Mapped[str] = mapped_column(String(30))
    availability_note: Mapped[str] = mapped_column(Text)
    usage_permission: Mapped[str] = mapped_column(String(30))
    license_note: Mapped[str] = mapped_column(Text)
    access_method: Mapped[str] = mapped_column(String(30))
    reliability_note: Mapped[str] = mapped_column(Text)
    dedup_method: Mapped[str] = mapped_column(String(30))
    original_source_url: Mapped[str | None] = mapped_column(Text)
    domain_tags: Mapped[list[str]] = mapped_column(JSON)
    label: Mapped[str] = mapped_column(String(10), index=True)


class EvidenceClaim(Base):
    __tablename__ = "evidence_claims"
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    source_version_id: Mapped[UUID] = mapped_column(ForeignKey("source_versions.id"), index=True)
    claim_text: Mapped[str] = mapped_column(Text)
    quote: Mapped[str] = mapped_column(Text)
    source_locator: Mapped[str] = mapped_column(Text)
    relation: Mapped[str] = mapped_column(String(20))
    claim_kind: Mapped[str] = mapped_column(String(20))
    known_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    verification_status: Mapped[str] = mapped_column(String(20))
    verification_note: Mapped[str] = mapped_column(Text)
    verified_by: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"), index=True)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    scope: Mapped[str] = mapped_column(Text)
    caveat: Mapped[str] = mapped_column(Text)
    label: Mapped[str] = mapped_column(String(10))


class Indicator(Base):
    __tablename__ = "indicators"
    __table_args__ = (
        UniqueConstraint(
            "code",
            "provider",
            "geo_scope",
            "definition_version",
            "label",
            name="uq_indicator_definition",
        ),
    )
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    code: Mapped[str] = mapped_column(String(200))
    name: Mapped[str] = mapped_column(String(4000))
    provider: Mapped[str] = mapped_column(String(200))
    geo_scope: Mapped[str] = mapped_column(String(200))
    unit: Mapped[str] = mapped_column(String(200))
    frequency: Mapped[str] = mapped_column(String(20))
    definition_version: Mapped[str] = mapped_column(String(200))
    label: Mapped[str] = mapped_column(String(10))


class ObservationVintage(Base):
    __tablename__ = "indicator_observation_vintages"
    __table_args__ = (
        UniqueConstraint(
            "indicator_id",
            "period_start",
            "period_end",
            "revision_number",
            name="uq_observation_vintage",
        ),
        CheckConstraint(
            "period_end >= period_start AND available_at >= published_at AND revision_number >= 1",
            name="ck_observation_times",
        ),
    )
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    indicator_id: Mapped[UUID] = mapped_column(ForeignKey("indicators.id"), index=True)
    source_version_id: Mapped[UUID] = mapped_column(ForeignKey("source_versions.id"), index=True)
    period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    value: Mapped[float] = mapped_column(Float)
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    available_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    revision_number: Mapped[int] = mapped_column(Integer)
    quality_flag: Mapped[str] = mapped_column(String(20))
    definition_note: Mapped[str] = mapped_column(Text)
    label: Mapped[str] = mapped_column(String(10))


class Signal(Base):
    __tablename__ = "signals"
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    headline: Mapped[str] = mapped_column(Text)
    lifecycle_stage: Mapped[str] = mapped_column(String(20))
    mechanism_tags: Mapped[list[str]] = mapped_column(JSON)
    domain_tags: Mapped[list[str]] = mapped_column(JSON)
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    label: Mapped[str] = mapped_column(String(10))


class SignalSource(Base):
    __tablename__ = "signal_sources"
    signal_id: Mapped[UUID] = mapped_column(ForeignKey("signals.id"), primary_key=True)
    evidence_claim_id: Mapped[UUID] = mapped_column(
        ForeignKey("evidence_claims.id"), primary_key=True, index=True
    )
    source_version_id: Mapped[UUID] = mapped_column(ForeignKey("source_versions.id"), index=True)
    source_group_id: Mapped[UUID] = mapped_column(ForeignKey("source_groups.id"), index=True)


class HistoricalCase(Base):
    __tablename__ = "historical_cases"
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    title: Mapped[str] = mapped_column(String(4000))
    cutoff_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    domain_tags: Mapped[list[str]] = mapped_column(JSON)
    mechanism_tags: Mapped[list[str]] = mapped_column(JSON)
    initial_conditions: Mapped[str] = mapped_column(Text)
    limitations: Mapped[list[str]] = mapped_column(JSON)
    label: Mapped[str] = mapped_column(String(10))


class HistoricalCaseEvent(Base):
    __tablename__ = "historical_case_sources"
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    case_id: Mapped[UUID] = mapped_column(ForeignKey("historical_cases.id"), index=True)
    source_version_id: Mapped[UUID] = mapped_column(ForeignKey("source_versions.id"), index=True)
    text: Mapped[str] = mapped_column(Text)
    known_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    data_role: Mapped[str] = mapped_column(String(20))
    outcome_category: Mapped[str | None] = mapped_column(String(20))


class WebAccessLog(Base):
    __tablename__ = "web_access_logs"
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    tool: Mapped[str] = mapped_column(String(20))
    input_hash: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(30))
    requested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, index=True
    )
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    http_attempts: Mapped[int] = mapped_column(Integer, default=0)


class ResearchTopic(Base):
    __tablename__ = "research_topics"
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    owner_user_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"), index=True)
    title: Mapped[str] = mapped_column(String(200))
    scope: Mapped[str] = mapped_column(Text)
    domain_tags: Mapped[list[str]] = mapped_column(JSON)
    version: Mapped[int] = mapped_column(Integer, default=1)
    label: Mapped[str] = mapped_column(String(10))


class ResearchRun(Base):
    __tablename__ = "research_runs"
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    topic_id: Mapped[UUID] = mapped_column(ForeignKey("research_topics.id"), index=True)
    creator_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    job_id: Mapped[UUID] = mapped_column(ForeignKey("jobs.id"), unique=True)
    research_as_of: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    provider: Mapped[str] = mapped_column(String(20))
    model_id: Mapped[str] = mapped_column(String(200))
    input_hash: Mapped[str] = mapped_column(String(64))
    engine_code_hash: Mapped[str] = mapped_column(String(64))
    prompt_hash: Mapped[str] = mapped_column(String(64))
    snapshot: Mapped[dict[str, Any]] = mapped_column(JSON)
    label: Mapped[str] = mapped_column(String(10))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class WorldForecast(Base):
    __tablename__ = "world_forecasts"
    __table_args__ = (UniqueConstraint("topic_id", "stable_target_key", name="uq_world_target"),)
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    topic_id: Mapped[UUID] = mapped_column(ForeignKey("research_topics.id"), index=True)
    stable_target_key: Mapped[str] = mapped_column(String(64))
    target_type: Mapped[str] = mapped_column(String(20))
    lifecycle_stage: Mapped[str] = mapped_column(String(20))
    current_version_id: Mapped[UUID | None] = mapped_column(Uuid)
    status: Mapped[str] = mapped_column(String(30), default="internal_unreviewed")


class ForecastVersion(Base):
    __tablename__ = "forecast_versions"
    __table_args__ = (UniqueConstraint("forecast_id", "version_num", name="uq_forecast_version"),)
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    forecast_id: Mapped[UUID] = mapped_column(ForeignKey("world_forecasts.id"), index=True)
    research_run_id: Mapped[UUID] = mapped_column(ForeignKey("research_runs.id"), index=True)
    version_num: Mapped[int] = mapped_column(Integer)
    draft_id: Mapped[UUID] = mapped_column(ForeignKey("forecast_drafts.id"), unique=True)
    review_id: Mapped[UUID] = mapped_column(ForeignKey("critic_runs.id"), index=True)
    change_reason: Mapped[str] = mapped_column(Text)
    label: Mapped[str] = mapped_column(String(10))
    immutable_hash: Mapped[str] = mapped_column(String(64))
    statement: Mapped[str] = mapped_column(Text)
    target: Mapped[dict[str, Any]] = mapped_column(JSON)
    research_as_of: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    body: Mapped[dict[str, Any]] = mapped_column(JSON)


class ForecastDraft(Base):
    __tablename__ = "forecast_drafts"
    __table_args__ = (
        UniqueConstraint("run_id", "draft_sequence", name="uq_run_draft"),
        CheckConstraint("draft_sequence IN ('A','B1','B2')", name="ck_m3_draft_sequence"),
    )
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    run_id: Mapped[UUID] = mapped_column(ForeignKey("research_runs.id"), index=True)
    forecast_id: Mapped[UUID | None] = mapped_column(ForeignKey("world_forecasts.id"), index=True)
    draft_sequence: Mapped[str] = mapped_column(String(10), default="A")
    body: Mapped[dict[str, Any]] = mapped_column(JSON)
    inputs_hash: Mapped[str] = mapped_column(String(64))
    immutable_hash: Mapped[str] = mapped_column(String(64))
    model_id: Mapped[str] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class ResearchRunSource(Base):
    __tablename__ = "research_run_sources"
    run_id: Mapped[UUID] = mapped_column(ForeignKey("research_runs.id"), primary_key=True)
    source_version_id: Mapped[UUID] = mapped_column(
        ForeignKey("source_versions.id"), primary_key=True, index=True
    )


class ResearchRunClaim(Base):
    __tablename__ = "research_run_claims"
    run_id: Mapped[UUID] = mapped_column(ForeignKey("research_runs.id"), primary_key=True)
    claim_id: Mapped[UUID] = mapped_column(
        ForeignKey("evidence_claims.id"), primary_key=True, index=True
    )


class ResearchRunObservation(Base):
    __tablename__ = "research_run_observations"
    run_id: Mapped[UUID] = mapped_column(ForeignKey("research_runs.id"), primary_key=True)
    observation_id: Mapped[UUID] = mapped_column(
        ForeignKey("indicator_observation_vintages.id"), primary_key=True, index=True
    )


class ResearchRunCase(Base):
    __tablename__ = "research_run_cases"
    run_id: Mapped[UUID] = mapped_column(ForeignKey("research_runs.id"), primary_key=True)
    case_id: Mapped[UUID] = mapped_column(
        ForeignKey("historical_cases.id"), primary_key=True, index=True
    )


class ModelCall(Base):
    __tablename__ = "model_calls"
    run_id: Mapped[UUID] = mapped_column(ForeignKey("research_runs.id"), primary_key=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    status: Mapped[str] = mapped_column(String(30))
    model_id: Mapped[str] = mapped_column(String(200))
    response: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    usage: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    error_code: Mapped[str | None] = mapped_column(String(100))
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class CriticRun(Base):
    __tablename__ = "critic_runs"
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    draft_id: Mapped[UUID] = mapped_column(ForeignKey("forecast_drafts.id"), index=True)
    draft_hash: Mapped[str] = mapped_column(String(64))
    independent_snapshot: Mapped[dict[str, Any]] = mapped_column(JSON)
    independent_input_hash: Mapped[str] = mapped_column(String(64))
    engine_code_hash: Mapped[str] = mapped_column(String(64))
    report: Mapped[dict[str, Any]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class AdjudicationRecord(Base):
    __tablename__ = "adjudication_records"
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    critic_run_id: Mapped[UUID] = mapped_column(ForeignKey("critic_runs.id"), unique=True)
    draft_id: Mapped[UUID] = mapped_column(ForeignKey("forecast_drafts.id"), index=True)
    decision: Mapped[str] = mapped_column(String(30))
    publication_allowed: Mapped[bool] = mapped_column(default=False)
    body: Mapped[dict[str, Any]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class DraftRevision(Base):
    __tablename__ = "draft_revisions"
    draft_id: Mapped[UUID] = mapped_column(ForeignKey("forecast_drafts.id"), primary_key=True)
    parent_draft_id: Mapped[UUID] = mapped_column(ForeignKey("forecast_drafts.id"), unique=True)
    review_id: Mapped[UUID] = mapped_column(ForeignKey("critic_runs.id"), index=True)
    snapshot: Mapped[dict[str, Any]] = mapped_column(JSON)
    changes: Mapped[dict[str, Any]] = mapped_column(JSON)
    finding_ids: Mapped[list[str]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class EvaluationProtocol(Base):
    __tablename__ = "evaluation_protocols"
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    version_id: Mapped[UUID] = mapped_column(ForeignKey("forecast_versions.id"), unique=True)
    mode: Mapped[str] = mapped_column(String(30))
    label: Mapped[str] = mapped_column(String(10))
    due_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    body: Mapped[dict[str, Any]] = mapped_column(JSON)
    immutable_hash: Mapped[str] = mapped_column(String(64))
    registered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class ForecastResolution(Base):
    __tablename__ = "forecast_resolutions"
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    protocol_id: Mapped[UUID] = mapped_column(ForeignKey("evaluation_protocols.id"), index=True)
    observation_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("indicator_observation_vintages.id"), index=True
    )
    status: Mapped[str] = mapped_column(String(40))
    body: Mapped[dict[str, Any]] = mapped_column(JSON)
    checked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class AuthAccount(Base):
    __tablename__ = "auth_accounts"
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), primary_key=True)
    email_lookup: Mapped[str] = mapped_column(String(64), unique=True)
    email_ciphertext: Mapped[str] = mapped_column(Text)
    password_hash: Mapped[str] = mapped_column(Text)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    email_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class AuthSession(Base):
    __tablename__ = "auth_sessions"
    token_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    public_id: Mapped[UUID] = mapped_column(Uuid, unique=True, index=True, default=uuid4)
    kind: Mapped[str] = mapped_column(String(16), default="user")
    device_label: Mapped[str] = mapped_column(String(80), default="未知设备")
    mfa_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class AuthAttempt(Base):
    __tablename__ = "auth_attempts"
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    identity_hash: Mapped[str] = mapped_column(String(64), index=True)
    source_hash: Mapped[str | None] = mapped_column(String(64), index=True)
    device_hash: Mapped[str | None] = mapped_column(String(64), index=True)
    outcome: Mapped[str] = mapped_column(String(16), default="admitted")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, index=True
    )


class AuthThrottleLock(Base):
    __tablename__ = "auth_throttle_lock"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)


class AdminAccess(Base):
    __tablename__ = "admin_access"
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), primary_key=True)
    permission_group: Mapped[str] = mapped_column(String(20))


class AdminMFA(Base):
    __tablename__ = "admin_mfa"
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), primary_key=True)
    secret_ciphertext: Mapped[str] = mapped_column(Text)
    enabled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_counter: Mapped[int] = mapped_column(BigInteger, default=-1)
    recovery_hashes: Mapped[list[str]] = mapped_column(JSON, default=list)


class AuthChallenge(Base):
    __tablename__ = "auth_challenges"
    token_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"), index=True)
    purpose: Mapped[str] = mapped_column(String(30))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    consumed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class AuthEmailCode(Base):
    __tablename__ = "auth_email_codes"
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    email_lookup: Mapped[str] = mapped_column(String(64), index=True)
    email_ciphertext: Mapped[str] = mapped_column(Text)
    purpose: Mapped[str] = mapped_column(String(20))
    code_digest: Mapped[str] = mapped_column(String(64))
    failed_attempts: Mapped[int] = mapped_column(Integer, default=0)
    code_ciphertext: Mapped[str | None] = mapped_column(Text)
    delivery_status: Mapped[str] = mapped_column(String(20))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    consumed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class AuthHumanToken(Base):
    __tablename__ = "auth_human_tokens"
    token_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)


class AuthAudit(Base):
    __tablename__ = "auth_audits"
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    actor_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"), index=True)
    target_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"), index=True)
    event: Mapped[str] = mapped_column(String(50), index=True)
    detail: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class AuthAccessEvent(Base):
    __tablename__ = "auth_access_events"
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    user_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"), index=True)
    identity_hash: Mapped[str] = mapped_column(String(64), index=True)
    request_id: Mapped[UUID] = mapped_column(Uuid, unique=True)
    action: Mapped[str] = mapped_column(String(16))
    outcome: Mapped[str] = mapped_column(String(16))
    reason: Mapped[str | None] = mapped_column(String(64))
    device_hash: Mapped[str] = mapped_column(String(64))
    context_ciphertext: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)


class IndustryTaxonomy(Base):
    __tablename__ = "industry_taxonomy"
    __table_args__ = (UniqueConstraint("code", "parent_code", name="uq_industry_parent"),)
    code: Mapped[str] = mapped_column(String(100), primary_key=True)
    parent_code: Mapped[str | None] = mapped_column(
        ForeignKey("industry_taxonomy.code"), index=True
    )
    label: Mapped[str] = mapped_column(String(200))
    level: Mapped[int] = mapped_column(Integer)
    version: Mapped[str] = mapped_column(String(80))
    domain_tags: Mapped[list[str]] = mapped_column(JSON)


class Profile(Base):
    __tablename__ = "profiles"
    __table_args__ = (
        ForeignKeyConstraint(
            ["industry_l2_code", "industry_l1_code"],
            ["industry_taxonomy.code", "industry_taxonomy.parent_code"],
            name="fk_profile_industry_pair",
        ),
    )
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), primary_key=True)
    industry_l1_code: Mapped[str] = mapped_column(ForeignKey("industry_taxonomy.code"), index=True)
    industry_l2_code: Mapped[str] = mapped_column(String(100), index=True)
    ciphertext: Mapped[str] = mapped_column(Text)
    revision: Mapped[int] = mapped_column(Integer)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class ProfileSnapshot(Base):
    __tablename__ = "profile_snapshots"
    __table_args__ = (UniqueConstraint("id", "user_id", name="uq_snapshot_owner"),)
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    profile_revision: Mapped[int] = mapped_column(Integer)
    ciphertext: Mapped[str] = mapped_column(Text)
    snapshot_hash: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class UserEntitlement(Base):
    __tablename__ = "user_entitlements"
    __table_args__ = (CheckConstraint("first_report_quota=1", name="ck_m4_first_report_quota"),)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), primary_key=True)
    first_report_quota: Mapped[int] = mapped_column(Integer, default=1)


class EntitlementReservation(Base):
    __tablename__ = "entitlement_reservations"
    __table_args__ = (
        CheckConstraint(
            "state IN ('reserved','consumed','released') AND units=1", name="ck_m4_reservation"
        ),
        Index(
            "uq_m4_user_reservation",
            "user_id",
            unique=True,
            postgresql_where=text("state='reserved'"),
            sqlite_where=text("state='reserved'"),
        ),
        Index(
            "uq_m4_user_consumed_reservation",
            "user_id",
            unique=True,
            postgresql_where=text("state='consumed'"),
            sqlite_where=text("state='consumed'"),
        ),
    )
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    job_id: Mapped[UUID] = mapped_column(ForeignKey("jobs.id"), unique=True)
    state: Mapped[str] = mapped_column(String(20))
    units: Mapped[int] = mapped_column(Integer, default=1)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class UsageLedger(Base):
    __tablename__ = "usage_ledger"
    __table_args__ = (
        UniqueConstraint("job_id", "entry_kind", name="uq_m4_ledger_entry"),
        CheckConstraint(
            (
                "(entry_kind='consumed' AND units_delta=-1) OR (e"
                "ntry_kind='released' AND units_delta=0)"
            ),
            name="ck_m4_ledger_units",
        ),
        Index(
            "uq_m4_user_consumption",
            "user_id",
            unique=True,
            postgresql_where=text("entry_kind='consumed'"),
            sqlite_where=text("entry_kind='consumed'"),
        ),
    )
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    job_id: Mapped[UUID] = mapped_column(ForeignKey("jobs.id"), index=True)
    reservation_id: Mapped[UUID] = mapped_column(
        ForeignKey("entitlement_reservations.id"), index=True
    )
    entry_kind: Mapped[str] = mapped_column(String(30))
    units_delta: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class ReportRequest(Base):
    __tablename__ = "prediction_requests"
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    job_id: Mapped[UUID] = mapped_column(ForeignKey("jobs.id"), unique=True)
    profile_snapshot_id: Mapped[UUID] = mapped_column(
        ForeignKey("profile_snapshots.id"), index=True
    )
    reservation_id: Mapped[UUID] = mapped_column(
        ForeignKey("entitlement_reservations.id"), unique=True
    )
    label: Mapped[str] = mapped_column(String(10))
    forecast_version_ids: Mapped[list[str]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class ReportBuildInput(Base):
    __tablename__ = "report_build_inputs"
    job_id: Mapped[UUID] = mapped_column(ForeignKey("jobs.id"), primary_key=True)
    forecast_version_ids: Mapped[list[str]] = mapped_column(JSON)
    engine_code_hash: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class UserReport(Base):
    __tablename__ = "user_reports"
    __table_args__ = (UniqueConstraint("id", "user_id", name="uq_report_owner"),)
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    current_version_id: Mapped[UUID | None] = mapped_column(Uuid)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class UserReportVersion(Base):
    __tablename__ = "user_report_versions"
    __table_args__ = (
        UniqueConstraint("report_id", "version_num", name="uq_private_report_version"),
        UniqueConstraint("id", "user_id", name="uq_report_version_owner"),
        ForeignKeyConstraint(
            ["report_id", "user_id"],
            ["user_reports.id", "user_reports.user_id"],
            name="fk_report_version_owner",
        ),
        ForeignKeyConstraint(
            ["profile_snapshot_id", "user_id"],
            ["profile_snapshots.id", "profile_snapshots.user_id"],
            name="fk_report_snapshot_owner",
        ),
    )
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    report_id: Mapped[UUID] = mapped_column(Uuid, index=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    profile_snapshot_id: Mapped[UUID] = mapped_column(Uuid, index=True)
    version_num: Mapped[int] = mapped_column(Integer)
    label: Mapped[str] = mapped_column(String(10))
    ciphertext: Mapped[str] = mapped_column(Text)
    immutable_hash: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class ReportVersionForecast(Base):
    __tablename__ = "report_version_forecasts"
    report_version_id: Mapped[UUID] = mapped_column(
        ForeignKey("user_report_versions.id"), primary_key=True
    )
    forecast_version_id: Mapped[UUID] = mapped_column(
        ForeignKey("forecast_versions.id"), primary_key=True, index=True
    )


class PersonalImpact(Base):
    __tablename__ = "personal_impacts"
    __table_args__ = (
        ForeignKeyConstraint(
            ["report_version_id", "user_id"],
            ["user_report_versions.id", "user_report_versions.user_id"],
            name="fk_impact_owner",
        ),
    )
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    report_version_id: Mapped[UUID] = mapped_column(Uuid, index=True)
    profile_snapshot_id: Mapped[UUID] = mapped_column(
        ForeignKey("profile_snapshots.id"), index=True
    )
    forecast_version_id: Mapped[UUID] = mapped_column(
        ForeignKey("forecast_versions.id"), index=True
    )
    ciphertext: Mapped[str] = mapped_column(Text)


class Recommendation(Base):
    __tablename__ = "recommendations"
    __table_args__ = (UniqueConstraint("id", "user_id", name="uq_recommendation_owner"),)
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    report_version_id: Mapped[UUID] = mapped_column(
        ForeignKey("user_report_versions.id"), index=True
    )
    impact_id: Mapped[UUID] = mapped_column(ForeignKey("personal_impacts.id"), index=True)
    ciphertext: Mapped[str] = mapped_column(Text)


class RecommendationFeedback(Base):
    __tablename__ = "recommendation_feedback"
    __table_args__ = (
        ForeignKeyConstraint(
            ["recommendation_id", "user_id"],
            ["recommendations.id", "recommendations.user_id"],
            name="fk_feedback_owner",
        ),
    )
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    recommendation_id: Mapped[UUID] = mapped_column(ForeignKey("recommendations.id"), index=True)
    status: Mapped[str] = mapped_column(String(30))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class LocalEmailDelivery(Base):
    __tablename__ = "local_email_deliveries"
    __table_args__ = (
        ForeignKeyConstraint(
            ["report_version_id", "user_id"],
            ["user_report_versions.id", "user_report_versions.user_id"],
            name="fk_delivery_owner",
        ),
    )
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), unique=True)
    report_version_id: Mapped[UUID] = mapped_column(
        ForeignKey("user_report_versions.id"), unique=True
    )
    recipient_ciphertext: Mapped[str] = mapped_column(Text)
    consented_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class ReportCatalogEntry(Base):
    __tablename__ = "report_catalog_entries"
    code: Mapped[str] = mapped_column(String(100), primary_key=True)
    forecast_version_id: Mapped[UUID] = mapped_column(
        ForeignKey("forecast_versions.id"), unique=True
    )


class ForecastMonitor(Base):
    __tablename__ = "forecast_monitors"
    forecast_id: Mapped[UUID] = mapped_column(ForeignKey("world_forecasts.id"), primary_key=True)
    policy: Mapped[dict[str, Any]] = mapped_column(JSON)
    next_check_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    cooldown_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_fingerprint: Mapped[str | None] = mapped_column(String(64))
    last_error: Mapped[str | None] = mapped_column(String(100))


class MonitorRun(Base):
    __tablename__ = "monitor_runs"
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    forecast_id: Mapped[UUID] = mapped_column(ForeignKey("world_forecasts.id"), index=True)
    old_version_id: Mapped[UUID] = mapped_column(ForeignKey("forecast_versions.id"), index=True)
    job_id: Mapped[UUID] = mapped_column(ForeignKey("jobs.id"), unique=True)
    snapshot: Mapped[dict[str, Any]] = mapped_column(JSON)
    assertions: Mapped[list[dict[str, Any]]] = mapped_column(JSON)
    decision: Mapped[dict[str, Any]] = mapped_column(JSON)
    engine_code_hash: Mapped[str] = mapped_column(String(64))
    verified_by: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class MonitorOutcome(Base):
    __tablename__ = "monitor_outcomes"
    run_id: Mapped[UUID] = mapped_column(ForeignKey("monitor_runs.id"), primary_key=True)
    new_version_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("forecast_versions.id"), index=True
    )
    body: Mapped[dict[str, Any]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class ReportRefresh(Base):
    __tablename__ = "report_refresh_requests"
    __table_args__ = (
        ForeignKeyConstraint(
            ["report_id", "user_id"],
            ["user_reports.id", "user_reports.user_id"],
            name="fk_refresh_report_owner",
        ),
        ForeignKeyConstraint(
            ["old_report_version_id", "user_id"],
            ["user_report_versions.id", "user_report_versions.user_id"],
            name="fk_refresh_version_owner",
        ),
        ForeignKeyConstraint(
            ["profile_snapshot_id", "user_id"],
            ["profile_snapshots.id", "profile_snapshots.user_id"],
            name="fk_refresh_snapshot_owner",
        ),
        UniqueConstraint("report_id", "input_hash", name="uq_report_refresh_input"),
    )
    job_id: Mapped[UUID] = mapped_column(ForeignKey("jobs.id"), primary_key=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    report_id: Mapped[UUID] = mapped_column(ForeignKey("user_reports.id"), index=True)
    old_report_version_id: Mapped[UUID] = mapped_column(
        ForeignKey("user_report_versions.id"), index=True
    )
    profile_snapshot_id: Mapped[UUID] = mapped_column(
        ForeignKey("profile_snapshots.id"), index=True
    )
    monitor_run_id: Mapped[UUID | None] = mapped_column(ForeignKey("monitor_runs.id"), index=True)
    forecast_version_ids: Mapped[list[str]] = mapped_column(JSON)
    input_hash: Mapped[str] = mapped_column(String(64))
    reason: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class InAppNotification(Base):
    __tablename__ = "in_app_notifications"
    __table_args__ = (
        ForeignKeyConstraint(
            ["report_id", "user_id"],
            ["user_reports.id", "user_reports.user_id"],
            name="fk_notification_report_owner",
        ),
        ForeignKeyConstraint(
            ["report_version_id", "user_id"],
            ["user_report_versions.id", "user_report_versions.user_id"],
            name="fk_notification_version_owner",
        ),
        UniqueConstraint("id", "user_id", name="uq_notification_owner"),
    )
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    report_id: Mapped[UUID] = mapped_column(ForeignKey("user_reports.id"), index=True)
    report_version_id: Mapped[UUID] = mapped_column(
        ForeignKey("user_report_versions.id"), unique=True
    )
    title: Mapped[str] = mapped_column(String(200))
    summary: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class NotificationRead(Base):
    __tablename__ = "notification_reads"
    __table_args__ = (
        ForeignKeyConstraint(
            ["notification_id", "user_id"],
            ["in_app_notifications.id", "in_app_notifications.user_id"],
            name="fk_notification_read_owner",
        ),
    )
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), primary_key=True)
    notification_id: Mapped[UUID] = mapped_column(
        ForeignKey("in_app_notifications.id"), primary_key=True, index=True
    )


class NotificationPreference(Base):
    __tablename__ = "notification_preferences"
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), primary_key=True)
    body: Mapped[dict[str, Any]] = mapped_column(JSON)
    suppressed: Mapped[bool] = mapped_column(default=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class PreferenceAudit(Base):
    __tablename__ = "notification_preference_audits"
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    body: Mapped[dict[str, Any]] = mapped_column(JSON)
    reason: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class MailDelivery(Base):
    __tablename__ = "mail_deliveries"
    __table_args__ = (
        ForeignKeyConstraint(
            ["report_version_id", "user_id"],
            ["user_report_versions.id", "user_report_versions.user_id"],
            name="fk_mail_delivery_owner",
        ),
        UniqueConstraint("user_id", "report_version_id", "purpose", name="uq_mail_delivery"),
    )
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    report_version_id: Mapped[UUID] = mapped_column(
        ForeignKey("user_report_versions.id"), index=True
    )
    job_id: Mapped[UUID] = mapped_column(ForeignKey("jobs.id"), unique=True)
    purpose: Mapped[str] = mapped_column(String(30))
    status: Mapped[str] = mapped_column(String(30))
    ciphertext: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, index=True
    )


class MailAttempt(Base):
    __tablename__ = "mail_attempts"
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    delivery_id: Mapped[UUID] = mapped_column(ForeignKey("mail_deliveries.id"), index=True)
    status: Mapped[str] = mapped_column(String(30))
    error_code: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class UnsubscribeGrant(Base):
    __tablename__ = "unsubscribe_grants"
    token_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class MailBounce(Base):
    __tablename__ = "mail_bounces"
    event_id: Mapped[str] = mapped_column(String(200), primary_key=True)
    delivery_id: Mapped[UUID] = mapped_column(ForeignKey("mail_deliveries.id"), index=True)
    kind: Mapped[str] = mapped_column(String(30))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class CommerceCheckout(Base):
    __tablename__ = "commerce_checkouts"
    __table_args__ = (
        UniqueConstraint("user_id", "idempotency_key", name="uq_checkout_key"),
        UniqueConstraint("id", "user_id", name="uq_checkout_owner"),
        CheckConstraint(
            "status IN ('pending','paid','refunded','expired')", name="ck_checkout_status"
        ),
    )
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    idempotency_key: Mapped[str] = mapped_column(String(128))
    input_hash: Mapped[str] = mapped_column(String(64))
    plan: Mapped[dict[str, Any]] = mapped_column(JSON)
    provider_reference: Mapped[str] = mapped_column(String(200), unique=True)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class CommercePaymentEvent(Base):
    __tablename__ = "commerce_payment_events"
    __table_args__ = (UniqueConstraint("provider", "external_event_id", name="uq_commerce_event"),)
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    provider: Mapped[str] = mapped_column(String(30))
    external_event_id: Mapped[str] = mapped_column(String(120))
    checkout_id: Mapped[UUID] = mapped_column(ForeignKey("commerce_checkouts.id"), index=True)
    event_type: Mapped[str] = mapped_column(String(40))
    payload_hash: Mapped[str] = mapped_column(String(64))
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    verified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class PaidSubscription(Base):
    __tablename__ = "paid_subscriptions"
    __table_args__ = (
        UniqueConstraint("id", "user_id", name="uq_subscription_owner"),
        ForeignKeyConstraint(
            ["checkout_id", "user_id"],
            ["commerce_checkouts.id", "commerce_checkouts.user_id"],
            name="fk_subscription_checkout_owner",
        ),
        CheckConstraint("status IN ('active','expired','refunded')", name="ck_subscription_status"),
    )
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    checkout_id: Mapped[UUID] = mapped_column(ForeignKey("commerce_checkouts.id"), unique=True)
    status: Mapped[str] = mapped_column(String(20))
    cancel_at_period_end: Mapped[bool] = mapped_column(default=False)
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    cadence_days: Mapped[int] = mapped_column(Integer)


class ResearchCreditGrant(Base):
    __tablename__ = "research_credit_grants"
    __table_args__ = (
        UniqueConstraint("id", "user_id", name="uq_credit_grant_owner"),
        ForeignKeyConstraint(
            ["checkout_id", "user_id"],
            ["commerce_checkouts.id", "commerce_checkouts.user_id"],
            name="fk_credit_checkout_owner",
        ),
        ForeignKeyConstraint(
            ["subscription_id", "user_id"],
            ["paid_subscriptions.id", "paid_subscriptions.user_id"],
            name="fk_grant_subscription_owner",
        ),
        CheckConstraint(
            "available>=0 AND reserved>=0 AND consumed>=0 AND revoked>=0 "
            "AND units=available+reserved+consumed+revoked",
            name="ck_credit_conservation",
        ),
    )
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    checkout_id: Mapped[UUID] = mapped_column(ForeignKey("commerce_checkouts.id"), unique=True)
    subscription_id: Mapped[UUID | None] = mapped_column(ForeignKey("paid_subscriptions.id"))
    units: Mapped[int] = mapped_column(Integer)
    available: Mapped[int] = mapped_column(Integer)
    reserved: Mapped[int] = mapped_column(Integer, default=0)
    consumed: Mapped[int] = mapped_column(Integer, default=0)
    revoked: Mapped[int] = mapped_column(Integer, default=0)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)


class PaidResearchReservation(Base):
    __tablename__ = "paid_research_reservations"
    __table_args__ = (
        UniqueConstraint("id", "user_id", name="uq_paid_reservation_owner"),
        ForeignKeyConstraint(
            ["grant_id", "user_id"],
            ["research_credit_grants.id", "research_credit_grants.user_id"],
            name="fk_reservation_grant_owner",
        ),
        CheckConstraint(
            "state IN ('reserved','consumed','released')", name="ck_paid_reservation_state"
        ),
    )
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    job_id: Mapped[UUID] = mapped_column(ForeignKey("jobs.id"), unique=True)
    grant_id: Mapped[UUID] = mapped_column(ForeignKey("research_credit_grants.id"), index=True)
    state: Mapped[str] = mapped_column(String(20))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class CommerceLedger(Base):
    __tablename__ = "commerce_ledger"
    __table_args__ = (
        UniqueConstraint("source_key", "entry_kind", name="uq_commerce_ledger_source"),
        CheckConstraint(
            "entry_kind IN ('granted','reserved','consumed','released',"
            "'revoked','refund','subscription_cancelled')",
            name="ck_commerce_ledger_kind",
        ),
        ForeignKeyConstraint(
            ["grant_id", "user_id"],
            ["research_credit_grants.id", "research_credit_grants.user_id"],
            name="fk_ledger_grant_owner",
        ),
    )
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    grant_id: Mapped[UUID | None] = mapped_column(ForeignKey("research_credit_grants.id"))
    job_id: Mapped[UUID | None] = mapped_column(ForeignKey("jobs.id"))
    source_key: Mapped[str] = mapped_column(String(150))
    entry_kind: Mapped[str] = mapped_column(String(30))
    units_delta: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class SharedTopicStudy(Base):
    __tablename__ = "shared_topic_studies"
    scope_fingerprint: Mapped[str] = mapped_column(String(64), primary_key=True)
    scope: Mapped[dict[str, Any]] = mapped_column(JSON)
    forecast_id: Mapped[UUID | None] = mapped_column(ForeignKey("world_forecasts.id"))
    checked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class UserResearchTopic(Base):
    __tablename__ = "user_research_topics"
    __table_args__ = (
        UniqueConstraint("user_id", "scope_fingerprint", name="uq_user_research_scope"),
        UniqueConstraint("id", "user_id", name="uq_user_topic_owner"),
        ForeignKeyConstraint(
            ["latest_report_id", "user_id"],
            ["user_reports.id", "user_reports.user_id"],
            name="fk_topic_report_owner",
        ),
        ForeignKeyConstraint(
            ["subscription_id", "user_id"],
            ["paid_subscriptions.id", "paid_subscriptions.user_id"],
            name="fk_topic_subscription_owner",
        ),
    )
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    scope_fingerprint: Mapped[str] = mapped_column(
        ForeignKey("shared_topic_studies.scope_fingerprint"), index=True
    )
    latest_report_id: Mapped[UUID | None] = mapped_column(ForeignKey("user_reports.id"))
    subscription_id: Mapped[UUID | None] = mapped_column(ForeignKey("paid_subscriptions.id"))
    periodic_enabled: Mapped[bool] = mapped_column(default=False)
    next_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    last_error: Mapped[str | None] = mapped_column(String(100))


class ResearchScopeQuote(Base):
    __tablename__ = "research_scope_quotes"
    __table_args__ = (UniqueConstraint("id", "user_id", name="uq_research_quote_owner"),)
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    scope_fingerprint: Mapped[str] = mapped_column(
        ForeignKey("shared_topic_studies.scope_fingerprint")
    )
    body: Mapped[dict[str, Any]] = mapped_column(JSON)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class PaidResearchRequest(Base):
    __tablename__ = "paid_research_requests"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_topic_id", "user_id"],
            ["user_research_topics.id", "user_research_topics.user_id"],
            name="fk_paid_topic_owner",
        ),
        ForeignKeyConstraint(
            ["profile_snapshot_id", "user_id"],
            ["profile_snapshots.id", "profile_snapshots.user_id"],
            name="fk_paid_snapshot_owner",
        ),
        ForeignKeyConstraint(
            ["reservation_id", "user_id"],
            ["paid_research_reservations.id", "paid_research_reservations.user_id"],
            name="fk_paid_request_reservation_owner",
        ),
    )
    job_id: Mapped[UUID] = mapped_column(ForeignKey("jobs.id"), primary_key=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    user_topic_id: Mapped[UUID] = mapped_column(ForeignKey("user_research_topics.id"), index=True)
    profile_snapshot_id: Mapped[UUID] = mapped_column(ForeignKey("profile_snapshots.id"))
    reservation_id: Mapped[UUID] = mapped_column(
        ForeignKey("paid_research_reservations.id"), unique=True
    )
    purpose: Mapped[str] = mapped_column(String(20))
    engine_code_hash: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class CostObservation(Base):
    __tablename__ = "cost_observations"
    __table_args__ = (
        UniqueConstraint("job_id", "stage", "source_key", name="uq_cost_observation"),
    )
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    job_id: Mapped[UUID] = mapped_column(ForeignKey("jobs.id"), index=True)
    stage: Mapped[str] = mapped_column(String(40))
    source_key: Mapped[str] = mapped_column(String(100))
    reused: Mapped[bool] = mapped_column(default=False)
    duration_ms: Mapped[int] = mapped_column(Integer)
    external_model_calls: Mapped[int] = mapped_column(Integer)
    usage: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    external_cost_minor: Mapped[int | None] = mapped_column(Integer)
    cost_basis: Mapped[str] = mapped_column(String(120))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class PrivacyErasure(Base):
    __tablename__ = "privacy_erasures"
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), unique=True)
    erased_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    counts: Mapped[dict[str, Any]] = mapped_column(JSON)


class CommunityIndustry(Base):
    __tablename__ = "community_industries"
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    user_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(60))
    description: Mapped[str] = mapped_column(String(300))
    domain: Mapped[str] = mapped_column(String(40))
    public: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class CommunityMembership(Base):
    __tablename__ = "community_memberships"
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), primary_key=True)
    industry_id: Mapped[UUID] = mapped_column(
        ForeignKey("community_industries.id"), primary_key=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class ProfileIndustry(Base):
    __tablename__ = "profile_industries"
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), primary_key=True)
    industry_id: Mapped[UUID] = mapped_column(ForeignKey("community_industries.id"))


class ChatModelBudget(Base):
    __tablename__ = "chat_model_budgets"
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), primary_key=True)
    window_start: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    turns: Mapped[int] = mapped_column(Integer)
    lease_id: Mapped[UUID | None] = mapped_column(Uuid)
    lease_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)


class ChatModelGlobalBudget(Base):
    __tablename__ = "chat_model_global_budget"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    window_start: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    turns: Mapped[int] = mapped_column(Integer)


class CommunityPublication(Base):
    __tablename__ = "community_publications"
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    user_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"), index=True)
    industry_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("community_industries.id"), index=True
    )
    report_id: Mapped[UUID | None] = mapped_column(ForeignKey("user_reports.id"), unique=True)
    report_version_id: Mapped[UUID | None] = mapped_column(ForeignKey("user_report_versions.id"))
    public: Mapped[bool] = mapped_column(default=False)
    body: Mapped[dict[str, Any]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class CommunityBookmark(Base):
    __tablename__ = "community_bookmarks"
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), primary_key=True)
    publication_id: Mapped[UUID] = mapped_column(
        ForeignKey("community_publications.id", ondelete="CASCADE"), primary_key=True
    )
    industry_id: Mapped[UUID] = mapped_column(ForeignKey("community_industries.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class ResearchConversation(Base):
    __tablename__ = "research_conversations"
    __table_args__ = (UniqueConstraint("user_id", "client_id", name="uq_conversation_client"),)
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    client_id: Mapped[UUID] = mapped_column(Uuid)
    industry_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("community_industries.id"), index=True
    )
    ciphertext: Mapped[str] = mapped_column(Text)
    job_id: Mapped[UUID | None] = mapped_column(ForeignKey("jobs.id"))
    report_id: Mapped[UUID | None] = mapped_column(ForeignKey("user_reports.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class ChatIndustryResearch(Base):
    __tablename__ = "chat_industry_research"
    job_id: Mapped[UUID] = mapped_column(ForeignKey("jobs.id"), primary_key=True)
    conversation_id: Mapped[UUID] = mapped_column(
        ForeignKey("research_conversations.id", ondelete="CASCADE"), index=True
    )
    scope_ciphertext: Mapped[str] = mapped_column(Text)
    result_ciphertext: Mapped[str | None] = mapped_column(Text)
    stages: Mapped[list[dict[str, str]]] = mapped_column(JSON, default=list)


class CommunityPrivateReport(Base):
    __tablename__ = "community_private_reports"
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), primary_key=True)
    report_id: Mapped[UUID] = mapped_column(ForeignKey("user_reports.id"), primary_key=True)
    industry_id: Mapped[UUID] = mapped_column(ForeignKey("community_industries.id"), index=True)


class CommunityIndustryCopy(Base):
    __tablename__ = "community_industry_copies"
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), primary_key=True)
    source_industry_id: Mapped[UUID] = mapped_column(
        ForeignKey("community_industries.id"), primary_key=True
    )
    industry_id: Mapped[UUID] = mapped_column(ForeignKey("community_industries.id"), unique=True)


class ConsumerPreference(Base):
    __tablename__ = "consumer_preferences"
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), primary_key=True)
    theme: Mapped[str] = mapped_column(String(10), default="system")


class IndustryTracking(Base):
    __tablename__ = "industry_tracking"
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), primary_key=True)
    industry_id: Mapped[UUID] = mapped_column(
        ForeignKey("community_industries.id"), primary_key=True
    )
    monitor_enabled: Mapped[bool] = mapped_column(default=True)
    prediction_enabled: Mapped[bool] = mapped_column(default=True)
    email_enabled: Mapped[bool] = mapped_column(default=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class CommunityLike(Base):
    __tablename__ = "community_likes"
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), primary_key=True)
    publication_id: Mapped[UUID] = mapped_column(
        ForeignKey("community_publications.id", ondelete="CASCADE"), primary_key=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class CommunityActivity(Base):
    __tablename__ = "community_activities"
    __table_args__ = (
        UniqueConstraint(
            "recipient_user_id",
            "actor_user_id",
            "publication_id",
            "kind",
            name="uq_community_activity",
        ),
    )
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    recipient_user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    actor_user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    publication_id: Mapped[UUID] = mapped_column(
        ForeignKey("community_publications.id", ondelete="CASCADE"), index=True
    )
    kind: Mapped[str] = mapped_column(String(16))
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class CommunityReportMetric(Base):
    __tablename__ = "community_report_metrics"
    publication_id: Mapped[UUID] = mapped_column(
        ForeignKey("community_publications.id", ondelete="CASCADE"), primary_key=True
    )
    views_count: Mapped[int] = mapped_column(BigInteger, default=0)


class CommunityReportRead(Base):
    __tablename__ = "community_report_reads"
    publication_id: Mapped[UUID] = mapped_column(
        ForeignKey("community_publications.id", ondelete="CASCADE"), primary_key=True
    )
    day: Mapped[date] = mapped_column(Date, primary_key=True, index=True)
    visitor_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
