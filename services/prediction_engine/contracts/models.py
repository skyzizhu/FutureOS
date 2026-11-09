from enum import StrEnum
from typing import Annotated, Literal
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, field_validator, model_validator

Text = Annotated[str, Field(min_length=1, max_length=4000)]
ShortText = Annotated[str, Field(min_length=1, max_length=200)]
IDs = Annotated[tuple[UUID, ...], Field(min_length=1)]


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    schema_version: Literal["1.0"] = "1.0"


class ContentKind(StrEnum):
    FACT = "fact"
    HYPOTHESIS = "hypothesis"
    FORECAST = "forecast"
    SCENARIO = "scenario"
    RECOMMENDATION = "recommendation"


class LifecycleStage(StrEnum):
    EMERGENCE = "emergence"
    GROWTH = "growth"
    MATURITY = "maturity"
    INFLECTION = "inflection"
    DECLINE = "decline"
    UNKNOWN = "unknown"


class JobStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED_RETRYABLE = "failed_retryable"
    FAILED_TERMINAL = "failed_terminal"
    CANCELLED = "cancelled"


class ResearchTopicV1(Contract):
    topic_id: UUID
    owner_user_id: UUID | None = None
    title: Text
    scope: Text
    domain_tags: tuple[Text, ...]
    version: int = Field(ge=1)


class WorldForecastV1(Contract):
    forecast_id: UUID
    topic_id: UUID
    stable_target_key: Text
    target_type: Literal["binary", "numeric", "ordinal", "milestone"]
    lifecycle_stage: LifecycleStage
    current_version_id: UUID | None = None


class ForecastTargetV1(Contract):
    target_type: Literal["binary", "numeric", "ordinal", "milestone"]
    population_scope: Text
    geography: Text
    metric_definition: Text
    direction_or_threshold: Text
    baseline: Text
    target_start_at: AwareDatetime
    target_end_at: AwareDatetime
    resolution_source: Text
    resolution_rule: Text

    @model_validator(mode="after")
    def ordered(self) -> "ForecastTargetV1":
        if self.target_end_at <= self.target_start_at:
            raise ValueError("target_end_at must follow target_start_at")
        return self


class ForecastDraftV1(Contract):
    draft_id: UUID
    run_id: UUID
    draft_sequence: Literal["A", "B1", "B2"]
    kind: Literal["hypothesis", "draft_forecast"]
    statement: Text
    research_as_of: AwareDatetime
    target: ForecastTargetV1 | None = None
    evidence_claim_ids: tuple[UUID, ...]
    inputs_hash: Annotated[str, Field(pattern=r"^[a-f0-9]{64}$")]
    model_version: Text

    @model_validator(mode="after")
    def testable(self) -> "ForecastDraftV1":
        if self.kind == "draft_forecast" and (not self.target or not self.evidence_claim_ids):
            raise ValueError("draft_forecast requires target and evidence")
        return self


class ForecastVersionV1(Contract):
    forecast_version_id: UUID
    forecast_id: UUID
    research_run_id: UUID
    version_num: int = Field(ge=1)
    kind: Literal["forecast"] = "forecast"
    statement: Text
    target: ForecastTargetV1
    research_as_of: AwareDatetime
    forecast_published_at: AwareDatetime
    evidence_claim_ids: IDs
    contradiction_claim_ids: tuple[UUID, ...]
    mechanism_ids: IDs
    historical_case_ids: tuple[UUID, ...]
    assumptions: tuple[Text, ...]
    falsification_conditions: Annotated[tuple[Text, ...], Field(min_length=1)]
    scenario_ids: IDs
    uncertainty_state: Literal["uncalibrated", "qualitative_assessment"] = "uncalibrated"
    next_review_at: AwareDatetime
    evidence_snapshot_hash: Annotated[str, Field(pattern=r"^[a-f0-9]{64}$")]
    change_reason: Text

    @model_validator(mode="after")
    def publication_order(self) -> "ForecastVersionV1":
        if self.forecast_published_at < self.research_as_of:
            raise ValueError("publication precedes research cutoff")
        if self.target.target_end_at <= self.research_as_of:
            raise ValueError("forecast target must end after research cutoff")
        if self.next_review_at <= self.research_as_of:
            raise ValueError("review must follow research cutoff")
        return self


class PersonalImpactV1(Contract):
    impact_id: UUID
    user_id: UUID
    profile_snapshot_id: UUID
    forecast_version_id: UUID
    affected_area: Text
    mechanism_path: tuple[Text, ...]
    relevance_reason: Text
    positive_impacts: tuple[Text, ...]
    negative_impacts: tuple[Text, ...]
    time_horizon: Text
    applicable_conditions: tuple[Text, ...]
    uncertainty: Text
    updated_at: AwareDatetime


class UserReportV1(Contract):
    report_id: UUID
    user_id: UUID
    current_version_id: UUID


class UserReportVersionV1(Contract):
    report_version_id: UUID
    report_id: UUID
    user_id: UUID
    report_version: int = Field(ge=1)
    profile_snapshot_id: UUID
    research_as_of: AwareDatetime
    forecast_version_ids: IDs
    personal_impact_ids: IDs
    change_reason: Text
    created_at: AwareDatetime


class SourceV1(Contract):
    source_id: UUID
    url: Text
    published_at: AwareDatetime
    provenance: Text
    snippet: Text
    label: Literal["DEMO", "REAL"]


class IndicatorObservationVintageV1(Contract):
    indicator_id: Text
    period_start: AwareDatetime
    period_end: AwareDatetime
    value: float = Field(allow_inf_nan=False)
    published_at: AwareDatetime
    available_at: AwareDatetime
    vintage: Text
    quality_flag: Literal["DEMO_DATA", "UNVERIFIED", "VERIFIED"]


class SignalFusionV1(Contract):
    fusion_id: UUID
    signal_ids: tuple[UUID, ...]
    independent_source_groups: int = Field(ge=0)
    mechanism: Text
    remaining_bottlenecks: tuple[Text, ...]
    emergent_hypotheses: tuple[Text, ...]
    opposing_explanations: tuple[Text, ...]
    next_observable_signals: tuple[Text, ...]
    stage: LifecycleStage
    status: Literal["hypothesis"] = "hypothesis"


class CriticFindingV1(Contract):
    finding_id: UUID
    draft_id: UUID
    category: Literal["evidence", "historical", "causal", "scenario", "temporal_resolution"]
    severity: Literal["L0", "L1", "L2", "L3"]
    statement: Text
    verified_source_refs: tuple[UUID, ...]
    verification_status: Literal["pending", "verified", "refuted"]
    scope: Text
    affected_assumption_ids: tuple[UUID, ...]
    recommended_action: Text


class AdjudicationDecisionV1(Contract):
    decision_id: UUID
    draft_id: UUID
    finding_ids: tuple[UUID, ...]
    rule_version: Text
    decision: Literal["accept", "annotate", "targeted_research", "block"]
    rationale: Text
    decided_at: AwareDatetime


class TurningPointReviewV1(Contract):
    trigger_id: UUID
    forecast_id: UUID
    old_version_id: UUID
    new_version_id: UUID | None = None
    final_level: Literal["T0", "T1", "T2", "T3"]
    decision: Literal["archive", "observe", "retain", "reforecast", "personal_impact_only"]
    evidence_delta_hash: Text
    reviewed_at: AwareDatetime


class DecisionValueV1(Contract):
    impact_id: UUID
    relevance: Literal["low", "medium", "high"]
    impact_window: Text
    actionability: Text
    reversibility: Literal["low", "medium", "high"]
    cost_note: Text
    decision_priority: Literal["prepare", "observe", "no_action"]
    reasons: tuple[Text, ...]
    unknowns: tuple[Text, ...]
    reevaluate_if: tuple[Text, ...]


class PredictionRequestV1(Contract):
    request_id: UUID
    user_id: UUID
    topic_id: UUID
    profile_snapshot_id: UUID
    entitlement_reservation_id: UUID | None = None
    request_kind: Literal["first_report", "new_topic", "material_review"]
    idempotency_key: Text


class EntitlementV1(Contract):
    user_id: UUID
    subscription_status: Literal["free", "active", "cancelled", "expired"]
    paid_periodic_research_enabled: bool
    email_digest_opt_in: bool = False
    email_alert_opt_in: bool = False


class NotificationEligibilityV1(Contract):
    user_id: UUID
    report_version_id: UUID
    channel: Literal["in_app", "email"]
    reason: Text
    consent_snapshot_ref: UUID | None = None
    dedupe_key: Text
    eligible: bool


class DemoResearchInputV1(Contract):
    question: Annotated[str, Field(min_length=3, max_length=500)]


class DemoResearchResultV1(Contract):
    label: Literal["DEMO"] = "DEMO"
    kind: Literal["hypothesis"] = "hypothesis"
    statement: Text
    research_as_of: AwareDatetime
    source_ids: IDs
    limitations: Annotated[tuple[Text, ...], Field(min_length=1)]
    model_id: Literal["mock-llm-v1"] = "mock-llm-v1"
    prompt_hash: Annotated[str, Field(pattern=r"^[a-f0-9]{64}$")]
    cost_units: Literal[0] = 0


class JobAcceptedV1(Contract):
    job_id: UUID
    request_id: UUID


class ErrorV1(Contract):
    code: Text
    message: Text
    request_id: str
    details: dict[str, bool | str | int] = Field(default_factory=dict)


class SearchHitV1(Contract):
    """Unverified provider output, separate from ingested/verified SourceV1 evidence."""

    hit_id: UUID
    provider: Literal["mock", "deepseek"]
    url: Annotated[str, Field(min_length=1, max_length=8192)]
    title: str
    snippet: str
    summary: str
    content: str
    site_name: str | None = None
    published_at: AwareDatetime | None
    retrieved_at: AwareDatetime
    provider_rank_score: float | None = Field(default=None, ge=0, le=3)
    provider_authority: int | None = Field(default=None, ge=-1, le=4)
    evidence_status: Literal["unverified"] = "unverified"
    label: Literal["DEMO", "REAL"]


class FetchedPageV1(Contract):
    """Untrusted Markdown; fetch time is never a substitute for publication time."""

    provider: Literal["mock", "deepseek"]
    url: Annotated[str, Field(min_length=1, max_length=8192)]
    title: str
    content: Annotated[str, Field(min_length=1, max_length=2_000_000)]
    content_hash: Annotated[str, Field(pattern=r"^[a-f0-9]{64}$")]
    retrieved_at: AwareDatetime
    published_at: None = None
    evidence_status: Literal["unverified"] = "unverified"
    label: Literal["DEMO", "REAL"]


class DomainTag(StrEnum):
    MACRO_FINANCE = "macro_finance"
    TECHNOLOGY = "technology"
    INDUSTRY = "industry"
    WORKFORCE = "workforce"
    POLICY = "policy"
    CONSUMPTION = "consumption"
    HOUSING = "housing"
    EDUCATION = "education"
    HEALTH = "health"
    ENERGY = "energy"
    SUPPLY_CHAIN = "supply_chain"
    SOCIETY = "society"


class ClaimImportV1(Contract):
    claim_text: Text
    quote: Annotated[str, Field(min_length=1, max_length=4000)]
    source_locator: Text
    relation: Literal["supports", "contradicts", "context"]
    claim_kind: Literal["fact", "opinion", "hypothesis"]
    verification_status: Literal["unverified", "verified"] = "unverified"
    verification_note: str = ""
    scope: Text
    caveat: str = ""

    @model_validator(mode="after")
    def reviewed(self) -> "ClaimImportV1":
        if self.verification_status == "verified" and not self.verification_note.strip():
            raise ValueError("verified claims require a human verification note")
        return self


class SourceImportV1(Contract):
    url: Annotated[str, Field(min_length=1, max_length=8192)]
    title: Text
    publisher: Text
    source_type: Literal["official", "paper", "licensed_data", "news", "community", "manual"]
    original_language: str = "zh"
    region: str = "unspecified"
    published_at: AwareDatetime | None = None
    event_at: AwareDatetime | None = None
    available_at: AwareDatetime | None = None
    availability_basis: Literal["observed_now", "verified_archive", "verified_release", "unknown"]
    availability_note: str = ""
    revised_at: AwareDatetime | None = None
    content: Annotated[str, Field(max_length=100_000)] = ""
    usage_permission: Literal["metadata_only", "excerpt", "authorized_full"]
    license_note: Text
    access_method: Literal["manual", "deepseek", "archive", "licensed_api"] = "manual"
    reliability_note: Text
    original_source_url: str | None = None
    domain_tags: Annotated[tuple[DomainTag, ...], Field(min_length=1)]
    claims: tuple[ClaimImportV1, ...] = ()
    label: Literal["DEMO", "REAL"]

    @model_validator(mode="after")
    def consistency(self) -> "SourceImportV1":
        if self.availability_basis in {"verified_archive", "verified_release"}:
            if self.available_at is None or not self.availability_note.strip():
                raise ValueError("historical availability requires timestamp and proof locator")
        elif self.available_at is not None:
            raise ValueError("observed/unknown availability is assigned by server")
        if self.available_at and self.published_at and self.available_at < self.published_at:
            raise ValueError("available_at cannot precede publication")
        if self.usage_permission == "metadata_only" and (self.content or self.claims):
            raise ValueError("metadata_only cannot retain content or claims")
        if self.usage_permission == "excerpt" and len(self.content) > 2000:
            raise ValueError("excerpt retention is limited to 2000 characters")
        if self.claims and not self.content.strip():
            raise ValueError("claims require retained authorized content")
        return self


class SourceVersionV1(Contract):
    source_version_id: UUID
    source_id: UUID
    source_group_id: UUID
    source_type: str
    original_language: str
    region: str
    dedup_method: str
    original_source_url: str | None = None
    version_label: str
    url: str
    title: str
    publisher: str
    published_at: AwareDatetime | None
    event_at: AwareDatetime | None
    available_at: AwareDatetime | None
    ingested_at: AwareDatetime
    revised_at: AwareDatetime | None
    availability_basis: str
    availability_note: str
    content_hash: str
    content: str
    usage_permission: str
    license_note: str
    access_method: str
    reliability_note: str
    domain_tags: tuple[DomainTag, ...]
    label: Literal["DEMO", "REAL"]


class EvidenceClaimV1(Contract):
    claim_id: UUID
    source_version_id: UUID
    source_group_id: UUID
    claim_text: str
    quote: str
    source_locator: str
    relation: Literal["supports", "contradicts", "context"]
    claim_kind: Literal["fact", "opinion", "hypothesis"]
    known_at: AwareDatetime | None
    verification_status: Literal["unverified", "verified"]
    verification_note: str
    scope: str
    caveat: str
    label: Literal["DEMO", "REAL"]


class SourceIngestedV1(Contract):
    version: SourceVersionV1
    claim_ids: tuple[UUID, ...]
    duplicate: bool


class IndicatorImportV1(Contract):
    code: ShortText
    name: Text
    provider: ShortText
    geo_scope: ShortText
    unit: ShortText
    frequency: Literal["day", "week", "month", "quarter", "year", "irregular"]
    definition_version: ShortText
    label: Literal["DEMO", "REAL"]


class IndicatorDefinitionV1(IndicatorImportV1):
    indicator_id: UUID


class ObservationImportV1(Contract):
    source_version_id: UUID
    period_start: AwareDatetime
    period_end: AwareDatetime
    value: float = Field(allow_inf_nan=False)
    published_at: AwareDatetime
    available_at: AwareDatetime
    revision_number: int = Field(ge=1)
    quality_flag: Literal["DEMO_DATA", "UNVERIFIED", "VERIFIED"]
    definition_note: Text

    @model_validator(mode="after")
    def times(self) -> "ObservationImportV1":
        if self.period_end < self.period_start or self.available_at < self.published_at:
            raise ValueError("invalid observation time ordering")
        return self


class ObservationV1(ObservationImportV1):
    observation_id: UUID
    indicator_id: UUID
    label: Literal["DEMO", "REAL"]


class SignalImportV1(Contract):
    headline: Text
    claim_ids: IDs
    lifecycle_stage: LifecycleStage = LifecycleStage.UNKNOWN
    mechanism_tags: tuple[Text, ...] = ()
    domain_tags: Annotated[tuple[DomainTag, ...], Field(min_length=1)]


class SignalV1(Contract):
    signal_id: UUID
    kind: Literal["signal"] = "signal"
    status: Literal["candidate"] = "candidate"
    headline: str
    lifecycle_stage: LifecycleStage
    claim_ids: tuple[UUID, ...]
    source_group_ids: tuple[UUID, ...]
    independent_source_count: int = Field(ge=1)
    mechanism_tags: tuple[str, ...]
    domain_tags: tuple[DomainTag, ...]
    detected_at: AwareDatetime
    label: Literal["DEMO", "REAL"]


class HistoricalEventImportV1(Contract):
    text: Text
    known_at: AwareDatetime
    source_version_id: UUID
    data_role: Literal["contemporaneous", "outcome"]
    outcome_category: Literal["success", "failure", "inconclusive"] | None = None

    @model_validator(mode="after")
    def role(self) -> "HistoricalEventImportV1":
        if self.data_role == "contemporaneous" and self.outcome_category is not None:
            raise ValueError("outcome labels must stay out of contemporaneous view")
        return self


class HistoricalCaseImportV1(Contract):
    title: Text
    cutoff_at: AwareDatetime
    domain_tags: Annotated[tuple[DomainTag, ...], Field(min_length=1)]
    mechanism_tags: tuple[Text, ...]
    initial_conditions: Text
    limitations: Annotated[tuple[Text, ...], Field(min_length=1)]
    events: Annotated[tuple[HistoricalEventImportV1, ...], Field(min_length=1)]
    label: Literal["DEMO", "REAL"]


class HistoricalCaseViewV1(Contract):
    case_id: UUID
    title: str
    cutoff_at: AwareDatetime
    as_of: AwareDatetime
    domain_tags: tuple[DomainTag, ...]
    mechanism_tags: tuple[str, ...]
    initial_conditions: str
    limitations: tuple[str, ...]
    contemporaneous: tuple[HistoricalEventImportV1, ...]
    outcomes: tuple[HistoricalEventImportV1, ...]
    label: Literal["DEMO", "REAL"]


class WebSearchRequestV1(Contract):
    query: Annotated[str, Field(min_length=1, max_length=128, pattern=r"\S")]
    count: int = Field(default=5, ge=1, le=10, strict=True)


class WebSearchResponseV1(Contract):
    results: tuple[SearchHitV1, ...]


class WebFetchRequestV1(Contract):
    url: Annotated[str, Field(min_length=1, max_length=8192)]


class WebFetchPreviewV1(Contract):
    url: str
    title: str
    excerpt: str
    full_content_hash: str
    retrieved_at: AwareDatetime
    published_at: None = None
    label: Literal["REAL"] = "REAL"
    evidence_status: Literal["unverified"] = "unverified"
    retained_characters: int


class ResearchSubmitV1(Contract):
    title: ShortText
    scope: Text
    domain_tags: Annotated[tuple[DomainTag, ...], Field(min_length=1, max_length=12)]
    research_as_of: AwareDatetime
    signal_ids: Annotated[tuple[UUID, ...], Field(min_length=1, max_length=20)]
    historical_case_ids: Annotated[tuple[UUID, ...], Field(max_length=10)] = ()
    indicator_id: UUID | None = None
    target: ForecastTargetV1 | None = None
    lifecycle_stage: LifecycleStage = LifecycleStage.UNKNOWN
    recipe_id: Literal["verifiable_agent", "technology_diffusion"] = "verifiable_agent"
    provider: Literal["mock", "deepseek"] = "mock"
    label: Literal["DEMO", "REAL"]


class ResearchSnapshotV1(Contract):
    request: ResearchSubmitV1
    signals: tuple[SignalV1, ...]
    claims: tuple[EvidenceClaimV1, ...]
    sources: tuple[SourceVersionV1, ...]
    cases: tuple[HistoricalCaseViewV1, ...]
    indicator: IndicatorDefinitionV1 | None = None
    observations: tuple[ObservationV1, ...] = ()
    engine_code_hash: Annotated[str, Field(pattern=r"^[a-f0-9]{64}$")]
    rules_version: Literal["m2-rules-v1"] = "m2-rules-v1"


class ResearchNarrativeV1(Contract):
    hypothesis: Text
    enabling_conditions: Annotated[tuple[Text, ...], Field(min_length=1, max_length=6)]
    bottlenecks: Annotated[tuple[Text, ...], Field(min_length=1, max_length=6)]
    opposing_explanations: Annotated[tuple[Text, ...], Field(min_length=1, max_length=6)]
    next_observable_signals: Annotated[tuple[Text, ...], Field(min_length=1, max_length=6)]
    falsification_conditions: Annotated[tuple[Text, ...], Field(min_length=1, max_length=6)]
    cited_claim_ids: IDs


class MechanismEdgeV1(Contract):
    from_node: Text
    to_node: Text
    relationship: Literal["enables", "constrains", "counteracts"]
    sign: Literal["positive", "negative"]
    lag_range: Text
    conditions: tuple[Text, ...]
    evidence_claim_ids: IDs
    uncertainty: Text


class AnalogyAssessmentV1(Contract):
    case_id: UUID
    mechanism_overlap: tuple[str, ...]
    similarities: tuple[Text, ...]
    key_differences: Annotated[tuple[Text, ...], Field(min_length=1)]
    non_transferable: Annotated[tuple[Text, ...], Field(min_length=1)]
    known_outcomes: tuple[HistoricalEventImportV1, ...]
    limitations: tuple[str, ...]


class ScenarioV1(Contract):
    scenario_id: UUID
    kind: Literal["scenario"] = "scenario"
    path: Literal["base", "acceleration", "friction"]
    statement: Text
    conditions: Annotated[tuple[Text, ...], Field(min_length=1)]
    observable_signals: Annotated[tuple[Text, ...], Field(min_length=1)]
    falsification_conditions: Annotated[tuple[Text, ...], Field(min_length=1)]


class BaselineV1(Contract):
    method: Literal["last_value", "not_applicable"]
    sample_count: int = Field(ge=0)
    observation_ids: tuple[UUID, ...]
    last_observed_value: float | None = Field(default=None, allow_inf_nan=False)
    projected_value: float | None = Field(default=None, allow_inf_nan=False)
    unit: str | None = None
    limitations: Annotated[tuple[Text, ...], Field(min_length=1)]


class M2DraftV1(Contract):
    parent_version_id: UUID | None = None
    draft_id: UUID
    run_id: UUID
    draft_sequence: Literal["A", "B1", "B2"] = "A"
    status: Literal["internal_unreviewed"] = "internal_unreviewed"
    publication_allowed: Literal[False] = False
    label: Literal["DEMO", "REAL"]
    kind: Literal["hypothesis", "draft_forecast"]
    statement: Text
    research_as_of: AwareDatetime
    lifecycle_stage: LifecycleStage
    target: ForecastTargetV1 | None
    evidence_claim_ids: tuple[UUID, ...]
    contradiction_claim_ids: tuple[UUID, ...]
    fusions: tuple[SignalFusionV1, ...]
    mechanism_chain: tuple[MechanismEdgeV1, ...]
    analogies: tuple[AnalogyAssessmentV1, ...]
    scenarios: Annotated[tuple[ScenarioV1, ...], Field(min_length=3, max_length=3)]
    baseline: BaselineV1
    raw_narrative: ResearchNarrativeV1
    assumptions: tuple[Text, ...]
    falsification_conditions: Annotated[tuple[Text, ...], Field(min_length=1)]
    uncertainty_state: Literal["uncalibrated"] = "uncalibrated"
    next_review_at: AwareDatetime
    limitations: tuple[Text, ...]
    downgrade_reasons: tuple[str, ...]
    input_hash: Annotated[str, Field(pattern=r"^[a-f0-9]{64}$")]
    prompt_hash: Annotated[str, Field(pattern=r"^[a-f0-9]{64}$")]
    model_id: str
    rules_version: Literal["m2-rules-v1"] = "m2-rules-v1"

    @model_validator(mode="after")
    def draft_invariants(self) -> "M2DraftV1":
        if {scenario.path for scenario in self.scenarios} != {"base", "acceleration", "friction"}:
            raise ValueError("three distinct competing paths required")
        if self.kind == "draft_forecast" and (
            self.target is None
            or not self.fusions
            or not self.evidence_claim_ids
            or self.downgrade_reasons
        ):
            raise ValueError(
                "draft forecast requires complete target, fusion and validated evidence"
            )
        return self


class M2ResearchResultV1(Contract):
    run_id: UUID
    draft_id: UUID
    status: Literal["internal_draft_ready"] = "internal_draft_ready"
    label: Literal["DEMO", "REAL"]
    kind: Literal["hypothesis", "draft_forecast"]
    publication_allowed: Literal[False] = False
    input_hash: str
    draft_hash: str


class ResearchAcceptedV1(JobAcceptedV1):
    run_id: UUID


class ResearchRunViewV1(Contract):
    run_id: UUID
    topic_id: UUID
    job_id: UUID
    title: str
    status: JobStatus
    research_as_of: AwareDatetime
    input_hash: str
    engine_code_hash: str
    provider: Literal["mock", "deepseek", "incremental"]
    model_id: str
    label: Literal["DEMO", "REAL"]
    draft: M2DraftV1 | None
    draft_hash: str | None
    error_code: str | None


class ReplayResultV1(Contract):
    run_id: UUID
    identical: bool
    input_hash: str
    original_draft_hash: str
    replay_draft_hash: str
    network_calls: Literal[0] = 0


class ReviewFindingV1(Contract):
    finding_id: UUID
    checker: Literal["evidence", "historical", "causal", "scenario", "temporal_resolution"]
    code: ShortText
    severity: Literal["L0", "L1", "L2", "L3"]
    statement: Text
    verification_status: Literal["verified", "pending", "refuted"]
    source_refs: tuple[UUID, ...] = ()
    affected_fields: tuple[str, ...]
    recommended_action: Text


class CriticReportV1(Contract):
    critic_run_id: UUID
    draft_id: UUID
    draft_hash: str
    independent_input_hash: str
    findings: tuple[ReviewFindingV1, ...]
    checkers_completed: tuple[str, ...]
    rules_version: Literal["m3-critic-v1"] = "m3-critic-v1"
    duration_ms: float = Field(ge=0)
    model_calls: Literal[0] = 0
    limitations: tuple[Text, ...]


class ReviewDecisionV1(Contract):
    decision_id: UUID
    critic_run_id: UUID
    draft_id: UUID
    decision: Literal["accept", "annotate", "targeted_research", "block", "research_only"]
    publication_allowed: bool
    verified_finding_ids: tuple[UUID, ...]
    rule_version: Literal["m3-adjudication-v1"] = "m3-adjudication-v1"
    rationale: Text
    decided_at: AwareDatetime


class ReviewViewV1(Contract):
    report: CriticReportV1
    decision: ReviewDecisionV1


class RevisionRequestV1(Contract):
    review_id: UUID
    confirmed_finding_ids: IDs
    additional_case_ids: Annotated[tuple[UUID, ...], Field(max_length=10)] = ()


class RevisionViewV1(Contract):
    draft_id: UUID
    parent_draft_id: UUID
    draft_sequence: Literal["B1", "B2"]
    input_hash: str
    draft_hash: str
    changes: dict[str, object]
    body: M2DraftV1


class PublishRequestV1(Contract):
    review_id: UUID
    change_reason: Text


class PublishedForecastV1(Contract):
    version_id: UUID
    forecast_id: UUID
    version_num: int = Field(ge=1)
    draft_id: UUID
    review_id: UUID
    label: Literal["DEMO", "REAL"]
    published_at: AwareDatetime
    version_hash: str
    change_reason: Text
    body: M2DraftV1


class EvaluationProtocolV1(Contract):
    protocol_id: UUID
    version_id: UUID
    mode: Literal["synthetic", "temporal_backtest", "forward"]
    label: Literal["DEMO", "REAL"]
    registered_at: AwareDatetime
    as_of: AwareDatetime
    due_at: AwareDatetime
    metric_definition: Text
    geography: Text
    unit: Text
    resolution_source: Text
    operator: Literal["gte", "lte", "eq"]
    threshold: float = Field(allow_inf_nan=False)
    point_prediction_a: float | None = Field(default=None, allow_inf_nan=False)
    point_prediction_b: float | None = Field(default=None, allow_inf_nan=False)
    baseline_value: float | None = Field(default=None, allow_inf_nan=False)
    source_snapshot_hash: str
    model_id: str
    prompt_hash: str
    testset_version: str
    protocol_version: Literal["m3-resolution-v1"] = "m3-resolution-v1"
    limitations: tuple[Text, ...]


class EvaluationRegisterV1(Contract):
    mode: Literal["synthetic", "temporal_backtest", "forward"]
    operator: Literal["gte", "lte", "eq"]
    threshold: float = Field(allow_inf_nan=False)
    unit: Text
    testset_version: ShortText = "manual-v1"


class ResolveRequestV1(Contract):
    observation_id: UUID | None = None
    unavailable_reason: Text | None = None

    @model_validator(mode="after")
    def exactly_one(self) -> "ResolveRequestV1":
        if (self.observation_id is None) == (self.unavailable_reason is None):
            raise ValueError("Provide either an observation or a data-unavailable reason")
        return self


class ForecastResolutionV1(Contract):
    resolution_id: UUID
    protocol_id: UUID
    status: Literal[
        "not_due", "confirmed", "disconfirmed", "inconclusive", "unresolved_due_to_data"
    ]
    checked_at: AwareDatetime
    observation_id: UUID | None = None
    observed_value: float | None = Field(default=None, allow_inf_nan=False)
    forecast_absolute_error_a: float | None = None
    forecast_absolute_error_b: float | None = None
    baseline_absolute_error: float | None = None
    reason: Text


class AccountCredentialsV1(Contract):
    email: Annotated[
        str,
        Field(
            min_length=3,
            max_length=254,
            pattern=r"^[A-Za-z0-9.!#$%&*+/=?^_`{|}~-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$",
        ),
    ]
    password: Annotated[str, Field(min_length=12, max_length=128)]


class AccountIdentityV1(Contract):
    user_id: UUID
    role: Literal["user", "admin"]
    email_masked: str
    email_verified: bool = False


class AccountSessionV1(Contract):
    access_token: str
    expires_at: AwareDatetime
    identity: AccountIdentityV1


class ProfileInputV1(Contract):
    industry_l1_code: ShortText
    industry_l2_code: ShortText
    industry_detail: Annotated[str, Field(max_length=120)] = ""
    occupation_text: Annotated[str, Field(max_length=300)] = ""
    country_code: Annotated[str, Field(max_length=2)] = ""
    subdivision: Annotated[str, Field(max_length=100)] = ""
    gender: Literal["female", "male", "other"] | None = None
    age: int | None = Field(default=None, ge=1, le=120, strict=True)
    region: Annotated[str, Field(max_length=200)] = ""
    goals: Annotated[tuple[ShortText, ...], Field(max_length=5)] = ()
    tasks: Annotated[tuple[ShortText, ...], Field(max_length=8)] = ()
    available_minutes_per_week: int | None = Field(default=None, ge=0, le=10080, strict=True)
    allow_low_cost_experiments: bool = Field(default=False, strict=True)
    use_optional_fields: bool = Field(default=False, strict=True)
    locale: Literal["zh-CN", "en"] = "zh-CN"
    timezone: Literal["Asia/Shanghai", "UTC"] = "Asia/Shanghai"

    @model_validator(mode="after")
    def valid_industry(self) -> "ProfileInputV1":
        from prediction_engine.personalization.geography import COUNTRY_CODES
        from prediction_engine.personalization.taxonomy import industry

        industry(self.industry_l1_code, self.industry_l2_code)
        if self.industry_l2_code.endswith("_other") and not self.industry_detail.strip():
            raise ValueError("CUSTOM_INDUSTRY_DETAIL_REQUIRED")
        if self.country_code and self.country_code not in COUNTRY_CODES:
            raise ValueError("COUNTRY_CODE_INVALID")
        if self.subdivision.strip() and not self.country_code:
            raise ValueError("COUNTRY_REQUIRED_FOR_SUBDIVISION")
        return self


class ProfileViewV1(Contract):
    user_id: UUID
    profile: ProfileInputV1
    revision: int = Field(ge=1)
    updated_at: AwareDatetime
    taxonomy_version: str


class ProfileSnapshotV1(Contract):
    snapshot_id: UUID
    user_id: UUID
    profile: ProfileInputV1
    profile_revision: int
    consent_scope: Literal["industry_only", "optional_fields"]
    created_at: AwareDatetime
    snapshot_hash: str


class FirstReportRequestV1(Contract):
    label: Literal["DEMO", "REAL"] = "DEMO"
    forecast_version_ids: Annotated[tuple[UUID, ...], Field(max_length=5)] = ()


class FreeReportEntitlementV1(Contract):
    total: Literal[1] = 1
    available: int = Field(ge=0, le=1)
    reserved: int = Field(ge=0, le=1)
    consumed: int = Field(ge=0, le=1)
    paid_research_enabled: Literal[False] = False


class ResearchIntakeV1(Contract):
    question: Annotated[str, Field(max_length=500)] = ""
    label: Literal["DEMO", "REAL"] = "DEMO"


class ResearchIntakeResultV1(Contract):
    scope: str
    matched_version_ids: tuple[UUID, ...]
    available_free_reports: int
    additional_questions: tuple[str, ...]
    limitations: tuple[str, ...]


class PersonalAssessmentV1(Contract):
    impact_id: UUID
    user_id: UUID
    profile_snapshot_id: UUID
    forecast_version_id: UUID
    relevance: Literal["low", "medium", "high"]
    mechanism_path: tuple[Text, ...]
    relevance_reason: Text
    positive_impacts: tuple[Text, ...]
    negative_impacts: tuple[Text, ...]
    applicable_conditions: tuple[Text, ...]
    uncertainty: Text
    matched_domains: tuple[str, ...]
    decision: DecisionValueV1


class RecommendationV1(Contract):
    recommendation_id: UUID
    impact_id: UUID
    action: Text
    rationale: Text
    forecast_version_ids: IDs
    applicability: Text
    suggested_start: AwareDatetime
    review_date: AwareDatetime
    estimated_effort_and_cost: Text
    tradeoffs: Text
    alternatives: Annotated[tuple[Text, ...], Field(min_length=1)]
    success_metrics: Annotated[tuple[Text, ...], Field(min_length=1)]
    stop_or_revisit_condition: Text
    priority: Literal["prepare", "observe", "no_action"]
    personalization_assumptions: tuple[Text, ...]
    suppressed_high_risk_actions: tuple[Text, ...]


class PrivateReportV1(Contract):
    report_id: UUID
    report_version_id: UUID
    user_id: UUID
    version_num: int = Field(ge=1)
    profile_snapshot_id: UUID
    profile_revision: int
    label: Literal["DEMO", "REAL"]
    title: Text
    created_at: AwareDatetime
    forecast_version_ids: IDs
    primary_impacts: tuple[PersonalAssessmentV1, ...]
    observation_only: tuple[PersonalAssessmentV1, ...]
    recommendations: tuple[RecommendationV1, ...]
    evidence_gaps: tuple[Text, ...]
    limitations: tuple[Text, ...]
    algorithm_version: Literal["m4-personal-v1"] = "m4-personal-v1"
    previous_report_version_id: UUID | None = None
    change_summary: tuple[str, ...] = ()


class UserReportResultV1(Contract):
    report_id: UUID
    report_version_id: UUID
    label: Literal["DEMO", "REAL"]
    status: Literal["private_report_ready"] = "private_report_ready"


class ReportSummaryV1(Contract):
    report_id: UUID
    report_version_id: UUID
    version_num: int
    title: str
    label: Literal["DEMO", "REAL"]
    created_at: AwareDatetime


class RecommendationFeedbackV1(Contract):
    status: Literal["helpful", "not_applicable", "taken", "hide"]


class EmailPreviewV1(Contract):
    report_version_id: UUID
    recipient_masked: str
    subject: str
    summary: str
    private_link: str
    transport: Literal["mock_local"] = "mock_local"
    external_delivery: Literal[False] = False


class EmailAuthorizationV1(Contract):
    explicit_consent: Literal[True]
    recipient: Annotated[str, Field(min_length=3, max_length=254)]

    @model_validator(mode="before")
    @classmethod
    def consent_is_explicit(cls, value: object) -> object:
        if not isinstance(value, dict) or value.get("explicit_consent") is not True:
            raise ValueError("Explicit boolean consent is required")
        return value


class LocalDeliveryV1(Contract):
    delivery_id: UUID
    report_version_id: UUID
    status: Literal["saved_locally_not_sent"] = "saved_locally_not_sent"
    external_delivery: Literal[False] = False
    consented_at: AwareDatetime


class MonitorPolicyV1(Contract):
    enabled: bool = True
    interval_seconds: int = Field(default=300, ge=30, le=86400)
    cooldown_seconds: int = Field(default=21600, ge=0, le=604800)
    max_daily_jobs: int = Field(default=12, ge=1, le=100)
    independent_groups_required: int = Field(default=2, ge=2, le=5)
    indicator_absolute_delta: float | None = Field(default=None, gt=0, allow_inf_nan=False)
    consecutive_periods: int = Field(default=2, ge=2, le=6)


class ChangeAssertionV1(Contract):
    kind: Literal[
        "critical_assumption_broken",
        "resolution_source_revised",
        "new_bottleneck_removed",
        "material_new_counterevidence",
    ]
    claim_ids: IDs
    prior_claim_id: UUID | None = None
    verification_note: Text


class MonitorCheckRequestV1(Contract):
    assertions: Annotated[tuple[ChangeAssertionV1, ...], Field(max_length=10)] = ()


class EvidenceDeltaV1(Contract):
    added_claim_ids: tuple[UUID, ...]
    independent_groups: int
    duplicate_claim_ids: tuple[UUID, ...]
    changed_observation_ids: tuple[UUID, ...]
    reasons: tuple[str, ...]
    fingerprint: str


class TurningDecisionV1(Contract):
    level: Literal["T0", "T1", "T2", "T3"]
    action: Literal["archive", "observe", "targeted_research", "block_pending_review"]
    delta: EvidenceDeltaV1
    rationale: Text
    rules_version: Literal["m5-turning-v1"] = "m5-turning-v1"


class MonitorResultV1(Contract):
    monitor_run_id: UUID
    forecast_id: UUID
    old_version_id: UUID
    new_version_id: UUID | None = None
    level: Literal["T0", "T1", "T2", "T3"]
    outcome: Literal["archived", "observed", "retained", "published", "review_blocked"]
    reason: str
    changed_fields: tuple[str, ...]
    refreshed_reports: int
    external_model_calls: Literal[0] = 0


class NotificationPreferencesV1(Contract):
    first_report_opt_in: bool = Field(default=False, strict=True)
    alert_opt_in: bool = Field(default=False, strict=True)
    digest_opt_in: bool = Field(default=False, strict=True)
    frequency: Literal["daily", "weekly"] = "weekly"
    explicit_consent: bool = Field(default=False, strict=True)

    @model_validator(mode="after")
    def consent_for_optin(self) -> "NotificationPreferencesV1":
        if (
            self.first_report_opt_in or self.alert_opt_in or self.digest_opt_in
        ) and not self.explicit_consent:
            raise ValueError("Explicit consent required for email opt-in")
        return self


class InAppNotificationV1(Contract):
    notification_id: UUID
    report_id: UUID
    report_version_id: UUID
    title: str
    summary: str
    created_at: AwareDatetime
    read: bool


class EmailQueueRequestV1(Contract):
    purpose: Literal["first_report", "alert", "digest"] = "first_report"
    explicit_consent: Literal[True]


class BounceEventV1(Contract):
    event_id: ShortText
    delivery_id: UUID
    kind: Literal["bounce", "complaint"]


class MailDeliveryResultV1(Contract):
    delivery_id: UUID
    status: Literal["delivered_local", "suppressed"]
    external_delivery: Literal[False] = False


class JobV1(Contract):
    job_id: UUID
    request_id: UUID
    trace_id: UUID
    status: JobStatus
    attempts: int
    label: Literal["DEMO", "REAL"] = "DEMO"
    result: (
        DemoResearchResultV1
        | M2ResearchResultV1
        | UserReportResultV1
        | MonitorResultV1
        | MailDeliveryResultV1
        | None
    ) = None
    error_code: str | None = None


class BillingPlanV1(Contract):
    code: Annotated[str, Field(pattern=r"^[a-z][a-z0-9_]{2,39}$")]
    name: ShortText
    amount_minor: int = Field(gt=0, le=10000000)
    currency: Literal["CNY"] = "CNY"
    units: int = Field(ge=1, le=1000)
    valid_days: int = Field(ge=1, le=366)
    recurring: bool
    cadence_days: int | None = Field(default=None, ge=1, le=30)
    label: Literal["DEMO"] = "DEMO"

    @model_validator(mode="after")
    def valid_cadence(self) -> "BillingPlanV1":
        if self.recurring != (self.cadence_days is not None):
            raise ValueError("Recurring plans require an explicit cadence")
        return self


class CheckoutRequestV1(Contract):
    plan_code: ShortText
    explicit_sandbox_consent: Literal[True]

    @field_validator("explicit_sandbox_consent", mode="before")
    @classmethod
    def actual_true(cls, value: object) -> object:
        if value is not True:
            raise ValueError("Explicit sandbox consent required")
        return value


class SandboxConsentV1(Contract):
    explicit_sandbox_consent: Literal[True]

    @field_validator("explicit_sandbox_consent", mode="before")
    @classmethod
    def actual_true(cls, value: object) -> object:
        if value is not True:
            raise ValueError("Explicit sandbox consent required")
        return value


class PaymentEventV1(Contract):
    provider: Literal["mock"] = "mock"
    label: Literal["DEMO"] = "DEMO"
    event_id: ShortText
    checkout_id: UUID
    provider_reference: ShortText
    event_type: Literal["checkout.paid", "checkout.refunded"]
    amount_minor: int = Field(gt=0)
    currency: Literal["CNY"]
    occurred_at: AwareDatetime


class ResearchScopeV1(Contract):
    domain: Literal[
        "technology",
        "manufacturing",
        "healthcare",
        "education",
        "finance",
        "services",
        "logistics",
        "energy",
        "society",
    ]
    focus: Literal["workflow_adoption", "integration_constraints"]
    population: Literal["small_teams", "large_organizations"]
    geography: Literal["global", "CN"] = "global"
    label: Literal["DEMO", "REAL"] = "DEMO"


class ResearchQuoteV1(Contract):
    quote_id: UUID
    scope: ResearchScopeV1
    scope_fingerprint: str
    kind: Literal["new_topic", "existing_topic"]
    units_required: int = Field(ge=0, le=1)
    existing_report_id: UUID | None
    expires_at: AwareDatetime
    rules: tuple[str, ...]


class PaidResearchSubmitV1(Contract):
    quote_id: UUID
    accept_usage_rules: Literal[True]

    @field_validator("accept_usage_rules", mode="before")
    @classmethod
    def actual_true(cls, value: object) -> object:
        if value is not True:
            raise ValueError("Explicit acceptance required")
        return value


class PaidResearchAcceptedV1(Contract):
    action: Literal["queued", "existing_report"]
    job_id: UUID | None = None
    report_id: UUID | None = None
    user_topic_id: UUID | None = None
    reserved_units: int = Field(ge=0, le=1)
    deduplicated: bool = False


class PeriodicResearchRequestV1(Contract):
    subscription_id: UUID
    explicit_periodic_consent: Literal[True]

    @field_validator("explicit_periodic_consent", mode="before")
    @classmethod
    def actual_true(cls, value: object) -> object:
        if value is not True:
            raise ValueError("Explicit periodic research consent required")
        return value


class PersonalDataEraseV1(Contract):
    password: Annotated[str, Field(min_length=12, max_length=128)]
    confirmation: Literal["DELETE MY DATA"]


class PersonalDataErasedV1(Contract):
    erasure_id: UUID
    erased_at: AwareDatetime
    cleared_records: dict[str, int]
    retained: tuple[str, ...]
    backup_notice: str


class EmailCodeRequestV1(Contract):
    email: Annotated[
        str,
        Field(
            min_length=3,
            max_length=254,
            pattern=r"^[A-Za-z0-9.!#$%&*+/=?^_`{|}~-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$",
        ),
    ]
    purpose: Literal["register", "password_reset"]
    human_token: Annotated[str, Field(max_length=2048)] = ""


class EmailCodeSentV1(Contract):
    challenge_id: UUID
    expires_in: int = 300
    resend_after: int = 60
    delivery_mode: Literal["local_preview", "smtp", "disabled"]


class VerifiedRegistrationV1(AccountCredentialsV1):
    verification_id: UUID
    code: Annotated[str, Field(pattern=r"^[0-9]{4}$")]


class ProtectedLoginV1(AccountCredentialsV1):
    human_token: Annotated[str, Field(max_length=2048)] = ""


class PasswordResetV1(VerifiedRegistrationV1):
    pass


class CurrentPasswordV1(Contract):
    password: Annotated[str, Field(min_length=12, max_length=128)]


class AdminBootstrapV1(AccountCredentialsV1):
    bootstrap_token: Annotated[str, Field(min_length=32, max_length=128)]


class AdminSecondFactorV1(Contract):
    challenge_token: Annotated[str, Field(min_length=32, max_length=128)]
    code: Annotated[str, Field(min_length=6, max_length=64)]


class AdminChallengeV1(Contract):
    challenge_token: str
    stage: Literal["enroll", "verify"]
    expires_in: int = 300
    secret: str | None = None
    provisioning_uri: str | None = None


class AdminSessionV1(AccountSessionV1):
    recovery_codes: tuple[str, ...] = ()


class AdminAccessChangeV1(Contract):
    permission_group: Literal["owner", "reviewer", "operator", "viewer"]
    enabled: bool = True


class AdminCreateV1(AccountCredentialsV1):
    permission_group: Literal["owner", "reviewer", "operator", "viewer"]


class AdminStepUpV1(Contract):
    code: Annotated[str, Field(pattern=r"^[0-9]{6}$")]


class AuthConfigurationV1(Contract):
    email_code_length: Literal[4] = 4
    email_transport: Literal["local_preview", "smtp", "disabled"]
    turnstile_enabled: bool
    turnstile_site_key: str
    demo_admin_enabled: bool


class LoginSessionViewV1(Contract):
    session_id: UUID
    kind: Literal["user", "admin"]
    device_label: Annotated[str, Field(max_length=80)]
    created_at: AwareDatetime
    expires_at: AwareDatetime
    current: bool


CommunityIndustryDomain = Literal[
    "technology",
    "energy",
    "healthcare",
    "manufacturing",
    "education",
    "finance",
    "services",
    "society",
]


class CommunityIndustryInputV1(Contract):
    name: Annotated[str, Field(min_length=1, max_length=60)]
    description: Annotated[str, Field(min_length=1, max_length=300)]
    domain: CommunityIndustryDomain


class CommunityVisibilityV1(Contract):
    public: bool = Field(strict=True)


class CommunityPublishV1(Contract):
    industry_id: UUID | None
    report_version_id: UUID
    confirm_public: Literal[True]

    @field_validator("confirm_public", mode="before")
    @classmethod
    def explicit_public(cls, value: object) -> object:
        if value is not True:
            raise ValueError("Explicit publication consent required")
        return value


class CommunitySaveReportV1(Contract):
    industry_id: UUID


class ConversationCreateV1(Contract):
    industry_id: UUID | None = None
    question: Annotated[str, Field(min_length=2, max_length=1000)]
    client_id: UUID
    use_model: bool = Field(default=False, strict=True)
    include_memory: bool = Field(default=False, strict=True)


class ConversationMessageV1(Contract):
    text: Annotated[str, Field(min_length=1, max_length=1000)]
    client_id: UUID
    use_model: bool = Field(default=False, strict=True)
    include_memory: bool = Field(default=False, strict=True)


class ConversationStartV1(Contract):
    confirm_demo_reuse: Literal[True]

    @field_validator("confirm_demo_reuse", mode="before")
    @classmethod
    def explicit_demo(cls, value: object) -> object:
        if value is not True:
            raise ValueError("Explicit scope acceptance required")
        return value


class CommunitySectionV1(Contract):
    heading: str
    text: str


class CommunityIndustryViewV1(Contract):
    id: UUID
    name: str
    description: str
    domain: str
    public: bool
    owned: bool = False
    added: bool = False
    personal_industry_id: UUID | None = None
    source_industry_id: UUID | None = None


class CommunityReportViewV1(Contract):
    id: UUID
    industry_id: UUID | None
    industry_name: str
    title: str
    summary: str
    label: Literal["DEMO", "REAL"]
    sample: bool
    image: str
    sections: tuple[CommunitySectionV1, ...]
    created_at: AwareDatetime
    author: str
    reason: str = ""
    views_count: int = Field(default=0, ge=0)
    likes_count: int = Field(default=0, ge=0)
    bookmarks_count: int = Field(default=0, ge=0)
    liked: bool = False
    saved: bool = False
    saved_industry_id: UUID | None = None
    owned: bool = False
    public: bool = True


class ConversationIndustryProposalV1(Contract):
    id: UUID
    name: str
    status: Literal["pending", "added", "already_exists"]
    industry_id: UUID | None = None


class ConversationCapabilitiesV1(Contract):
    model_available: bool


class ConversationMessageViewV1(Contract):
    role: Literal["user", "assistant"]
    text: str
    client_id: UUID | None = None
    source: Literal["local", "llm"] | None = None
    proposal: ConversationIndustryProposalV1 | None = None


class ConversationViewV1(Contract):
    id: UUID
    industry_id: UUID | None
    title: str
    created_at: AwareDatetime
    messages: tuple[ConversationMessageViewV1, ...]
    job_id: UUID | None
    job_status: JobStatus | None
    error_code: str | None
    report_id: UUID | None
    mode: Literal["demo_reuse"] = "demo_reuse"
    new_forecast_rules_pending: Literal[True] = True


class CountryOptionV1(Contract):
    code: str
    label: str


class CountryCatalogV1(Contract):
    entries: tuple[CountryOptionV1, ...]
    source: Literal["Unicode CLDR"] = "Unicode CLDR"


class ConsumerPreferenceV1(Contract):
    theme: Literal["system", "light", "dark"] = "system"


class IndustryTrackingV1(Contract):
    monitor_enabled: bool = Field(default=True, strict=True)
    prediction_enabled: bool = Field(default=True, strict=True)
    email_enabled: bool = Field(default=False, strict=True)


class IndustryTrackingViewV1(IndustryTrackingV1):
    industry_id: UUID
    status: Literal["waiting_rules", "paused"]


class CommunityActivityV1(Contract):
    id: UUID
    publication_id: UUID
    kind: Literal["like", "bookmark"]
    title: str
    summary: str
    created_at: AwareDatetime
    read: bool


class CommunityReadInputV1(Contract):
    visitor_id: UUID


IndustryResearchLane = Literal["industry", "market", "policy", "indicators", "counter", "analogy"]
IndustryActionDomain = Literal[
    "career", "work", "learning", "spending", "finance", "life", "health"
]


class IndustryResearchScopeV1(Contract):
    industry: ShortText
    region: ShortText = "global"
    horizon_days: int = Field(default=180, ge=1, le=1095)
    label: Literal["DEMO", "REAL"] = "DEMO"


class IndustrySearchQueryV1(Contract):
    lane: IndustryResearchLane
    query: Annotated[str, Field(min_length=1, max_length=128)]


class IndustryCoverageReviewV1(Contract):
    sufficient: bool
    gaps: Annotated[tuple[ShortText, ...], Field(max_length=8)]
    queries: Annotated[tuple[IndustrySearchQueryV1, ...], Field(max_length=4)]


class IndustryEvidenceV1(Contract):
    source_id: UUID
    kind: Literal["direct", "indicator", "counter", "analogy"]
    quote: Annotated[str, Field(min_length=12, max_length=500)]
    interpretation: ShortText
    comparable_conditions: ShortText | None = None
    key_difference: ShortText | None = None
    indicator_name: ShortText | None = None
    indicator_period: ShortText | None = None
    indicator_value: ShortText | None = None

    @model_validator(mode="after")
    def validate_evidence_fields(self) -> "IndustryEvidenceV1":
        if self.kind == "analogy" and not (self.comparable_conditions and self.key_difference):
            raise ValueError("INDUSTRY_ANALOGY_REQUIRES_BOUNDARIES")
        if self.kind == "indicator" and (
            not all(
                field and field.strip() and field in self.quote
                for field in (self.indicator_name, self.indicator_period, self.indicator_value)
            )
            or not any(character.isdecimal() for character in self.indicator_value or "")
        ):
            raise ValueError("INDUSTRY_INDICATOR_REQUIRES_QUOTED_FIELDS")
        return self


class IndustryAnalogyMilestoneV1(Contract):
    period: ShortText
    observed_change: ShortText
    source_id: UUID
    quote: Annotated[str, Field(min_length=12, max_length=500)]


class IndustryAnalogyChainV1(Contract):
    case_id: ShortText
    industry: ShortText
    context: ShortText
    milestones: Annotated[tuple[IndustryAnalogyMilestoneV1, ...], Field(min_length=2, max_length=8)]
    mechanism: ShortText
    comparable_conditions: ShortText
    key_difference: ShortText


class IndustryEvidenceReviewV1(IndustryCoverageReviewV1):
    evidence: Annotated[tuple[IndustryEvidenceV1, ...], Field(max_length=16)]
    analogy_chains: Annotated[tuple[IndustryAnalogyChainV1, ...], Field(max_length=4)] = ()


class IndustryForecastDraftV1(Contract):
    statement: ShortText
    mechanism: ShortText
    expected_signal: ShortText
    falsifier: ShortText
    uncertainty: ShortText
    alternatives: Annotated[tuple[ShortText, ...], Field(min_length=1, max_length=3)]
    supporting_source_ids: Annotated[tuple[UUID, ...], Field(min_length=1, max_length=12)]
    counter_source_ids: Annotated[tuple[UUID, ...], Field(max_length=12)] = ()
    basis: Literal["direct", "analogy"] = "direct"
    analogy_case_ids: Annotated[tuple[ShortText, ...], Field(max_length=4)] = ()


class IndustryActionDraftV1(Contract):
    forecast_index: int = Field(ge=0, le=3, description="Zero-based forecast position")
    domain: IndustryActionDomain
    action: ShortText
    trigger: ShortText
    check_after_days: int = Field(ge=1, le=365)
    time_minutes: int = Field(ge=1, le=480)
    success_check: ShortText
    stop_condition: ShortText


class IndustryReportDraftV1(Contract):
    forecasts: Annotated[tuple[IndustryForecastDraftV1, ...], Field(min_length=1, max_length=4)]
    actions: Annotated[tuple[IndustryActionDraftV1, ...], Field(min_length=1, max_length=8)]


class IndustrySourceExcerptV1(Contract):
    source_id: UUID
    url: Annotated[str, Field(min_length=1, max_length=8192)]
    title: Annotated[str, Field(max_length=250)]
    published_at: AwareDatetime | None
    retrieved_at: AwareDatetime
    content_hash: Annotated[str, Field(pattern=r"^[a-f0-9]{64}$")]
    excerpt: Annotated[str, Field(min_length=1, max_length=1400)]


class IndustryResearchRunV1(Contract):
    scope: IndustryResearchScopeV1
    as_of: AwareDatetime
    status: Literal["draft", "evidence_limited"]
    searched: tuple[IndustrySearchQueryV1, ...]
    sources: tuple[IndustrySourceExcerptV1, ...]
    evidence: tuple[IndustryEvidenceV1, ...]
    analogy_chains: tuple[IndustryAnalogyChainV1, ...] = ()
    gaps: tuple[ShortText, ...]
    report: IndustryReportDraftV1 | None = None
    personal_actions: tuple[IndustryActionDraftV1, ...] | None = None
    fetch_calls: int = Field(ge=0)
    model_calls: int = Field(ge=0)
    provider_failures: int = Field(ge=0)


IndustryResearchStage = Literal["search", "analysis", "report"]


class ChatResearchStartV1(Contract):
    client_id: UUID
    industry_id: UUID
    horizon_days: int = Field(default=180, ge=1, le=1095, strict=True)
    confirm_demo: Literal[True]

    @field_validator("confirm_demo", mode="before")
    @classmethod
    def explicit_demo(cls, value: object) -> object:
        if value is not True:
            raise ValueError("Explicit demo consent required")
        return value


class ChatResearchStageViewV1(Contract):
    stage: IndustryResearchStage
    started_at: AwareDatetime


class ChatResearchViewV1(Contract):
    id: UUID
    industry: str
    horizon_days: int
    status: JobStatus
    stages: tuple[ChatResearchStageViewV1, ...]
    error_code: str | None
    created_at: AwareDatetime
    result: IndustryResearchRunV1 | None = None


class AuthAccessEventViewV1(Contract):
    id: UUID
    user_id: UUID | None
    request_id: UUID
    action: Literal["login", "register"]
    outcome: Literal["succeeded", "rejected"]
    reason: str | None
    fingerprint: str
    fingerprint_kind: Literal["browser", "client_headers"]
    peer_ip: str | None
    device: str
    user_agent: str
    accept_language: str
    created_at: AwareDatetime
