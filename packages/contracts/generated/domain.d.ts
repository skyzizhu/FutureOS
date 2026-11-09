// Generated from Pydantic JSON Schemas. Do not edit.

export type SchemaVersion = "1.0";
export type Email = string;
export type Password = string;
export type SchemaVersion1 = "1.0";
export type UserId = string;
export type Role = "user" | "admin";
export type EmailMasked = string;
export type EmailVerified = boolean;
export type SchemaVersion2 = "1.0";
export type AccessToken = string;
export type ExpiresAt = string;
export type SchemaVersion3 = "1.0";
export type DecisionId = string;
export type DraftId = string;
export type FindingIds = string[];
export type RuleVersion = string;
export type Decision = "accept" | "annotate" | "targeted_research" | "block";
export type Rationale = string;
export type DecidedAt = string;
export type SchemaVersion4 = "1.0";
export type PermissionGroup = "owner" | "reviewer" | "operator" | "viewer";
export type Enabled = boolean;
export type SchemaVersion5 = "1.0";
export type Email1 = string;
export type Password1 = string;
export type BootstrapToken = string;
export type SchemaVersion6 = "1.0";
export type ChallengeToken = string;
export type Stage = "enroll" | "verify";
export type ExpiresIn = number;
export type Secret = string | null;
export type ProvisioningUri = string | null;
export type SchemaVersion7 = "1.0";
export type Email2 = string;
export type Password2 = string;
export type PermissionGroup1 = "owner" | "reviewer" | "operator" | "viewer";
export type SchemaVersion8 = "1.0";
export type ChallengeToken1 = string;
export type Code = string;
export type SchemaVersion9 = "1.0";
export type AccessToken1 = string;
export type ExpiresAt1 = string;
export type RecoveryCodes = string[];
export type SchemaVersion10 = "1.0";
export type Code1 = string;
export type SchemaVersion11 = "1.0";
export type CaseId = string;
export type MechanismOverlap = string[];
export type Similarities = string[];
/**
 * @minItems 1
 */
export type KeyDifferences = [string, ...string[]];
/**
 * @minItems 1
 */
export type NonTransferable = [string, ...string[]];
export type SchemaVersion12 = "1.0";
export type Text = string;
export type KnownAt = string;
export type SourceVersionId = string;
export type DataRole = "contemporaneous" | "outcome";
export type OutcomeCategory = ("success" | "failure" | "inconclusive") | null;
export type KnownOutcomes = HistoricalEventImportV1[];
export type Limitations = string[];
export type SchemaVersion13 = "1.0";
export type Id = string;
export type UserId1 = string | null;
export type RequestId = string;
export type Action = "login" | "register";
export type Outcome = "succeeded" | "rejected";
export type Reason = string | null;
export type Fingerprint = string;
export type FingerprintKind = "browser" | "client_headers";
export type PeerIp = string | null;
export type Device = string;
export type UserAgent = string;
export type AcceptLanguage = string;
export type CreatedAt = string;
export type SchemaVersion14 = "1.0";
export type EmailCodeLength = 4;
export type EmailTransport = "local_preview" | "smtp" | "disabled";
export type TurnstileEnabled = boolean;
export type TurnstileSiteKey = string;
export type DemoAdminEnabled = boolean;
export type SchemaVersion15 = "1.0";
export type Method = "last_value" | "not_applicable";
export type SampleCount = number;
export type ObservationIds = string[];
export type LastObservedValue = number | null;
export type ProjectedValue = number | null;
export type Unit = string | null;
/**
 * @minItems 1
 */
export type Limitations1 = [string, ...string[]];
export type SchemaVersion16 = "1.0";
export type Code2 = string;
export type Name = string;
export type AmountMinor = number;
export type Currency = "CNY";
export type Units = number;
export type ValidDays = number;
export type Recurring = boolean;
export type CadenceDays = number | null;
export type Label = "DEMO";
export type SchemaVersion17 = "1.0";
export type EventId = string;
export type DeliveryId = string;
export type Kind = "bounce" | "complaint";
export type SchemaVersion18 = "1.0";
export type Kind1 =
  | "critical_assumption_broken"
  | "resolution_source_revised"
  | "new_bottleneck_removed"
  | "material_new_counterevidence";
/**
 * @minItems 1
 */
export type ClaimIds = [string, ...string[]];
export type PriorClaimId = string | null;
export type VerificationNote = string;
export type SchemaVersion19 = "1.0";
export type Stage1 = "search" | "analysis" | "report";
export type StartedAt = string;
export type SchemaVersion20 = "1.0";
export type ClientId = string;
export type IndustryId = string;
export type HorizonDays = number;
export type ConfirmDemo = true;
export type SchemaVersion21 = "1.0";
export type Id1 = string;
export type Industry = string;
export type HorizonDays1 = number;
export type JobStatus = "queued" | "running" | "succeeded" | "failed_retryable" | "failed_terminal" | "cancelled";
export type Stages = ChatResearchStageViewV1[];
export type ErrorCode = string | null;
export type CreatedAt1 = string;
export type SchemaVersion22 = "1.0";
export type SchemaVersion23 = "1.0";
export type Industry1 = string;
export type Region = string;
export type HorizonDays2 = number;
export type Label1 = "DEMO" | "REAL";
export type AsOf = string;
export type Status = "draft" | "evidence_limited";
export type SchemaVersion24 = "1.0";
export type Lane = "industry" | "market" | "policy" | "indicators" | "counter" | "analogy";
export type Query = string;
export type Searched = IndustrySearchQueryV1[];
export type SchemaVersion25 = "1.0";
export type SourceId = string;
export type Url = string;
export type Title = string;
export type PublishedAt = string | null;
export type RetrievedAt = string;
export type ContentHash = string;
export type Excerpt = string;
export type Sources = IndustrySourceExcerptV1[];
export type SchemaVersion26 = "1.0";
export type SourceId1 = string;
export type Kind2 = "direct" | "indicator" | "counter" | "analogy";
export type Quote = string;
export type Interpretation = string;
export type ComparableConditions = string | null;
export type KeyDifference = string | null;
export type IndicatorName = string | null;
export type IndicatorPeriod = string | null;
export type IndicatorValue = string | null;
export type Evidence = IndustryEvidenceV1[];
export type SchemaVersion27 = "1.0";
export type CaseId1 = string;
export type Industry2 = string;
export type Context = string;
/**
 * @minItems 2
 * @maxItems 8
 */
export type Milestones =
  | [IndustryAnalogyMilestoneV1, IndustryAnalogyMilestoneV1]
  | [IndustryAnalogyMilestoneV1, IndustryAnalogyMilestoneV1, IndustryAnalogyMilestoneV1]
  | [IndustryAnalogyMilestoneV1, IndustryAnalogyMilestoneV1, IndustryAnalogyMilestoneV1, IndustryAnalogyMilestoneV1]
  | [
      IndustryAnalogyMilestoneV1,
      IndustryAnalogyMilestoneV1,
      IndustryAnalogyMilestoneV1,
      IndustryAnalogyMilestoneV1,
      IndustryAnalogyMilestoneV1
    ]
  | [
      IndustryAnalogyMilestoneV1,
      IndustryAnalogyMilestoneV1,
      IndustryAnalogyMilestoneV1,
      IndustryAnalogyMilestoneV1,
      IndustryAnalogyMilestoneV1,
      IndustryAnalogyMilestoneV1
    ]
  | [
      IndustryAnalogyMilestoneV1,
      IndustryAnalogyMilestoneV1,
      IndustryAnalogyMilestoneV1,
      IndustryAnalogyMilestoneV1,
      IndustryAnalogyMilestoneV1,
      IndustryAnalogyMilestoneV1,
      IndustryAnalogyMilestoneV1
    ]
  | [
      IndustryAnalogyMilestoneV1,
      IndustryAnalogyMilestoneV1,
      IndustryAnalogyMilestoneV1,
      IndustryAnalogyMilestoneV1,
      IndustryAnalogyMilestoneV1,
      IndustryAnalogyMilestoneV1,
      IndustryAnalogyMilestoneV1,
      IndustryAnalogyMilestoneV1
    ];
export type SchemaVersion28 = "1.0";
export type Period = string;
export type ObservedChange = string;
export type SourceId2 = string;
export type Quote1 = string;
export type Mechanism = string;
export type ComparableConditions1 = string;
export type KeyDifference1 = string;
export type AnalogyChains = IndustryAnalogyChainV1[];
export type Gaps = string[];
export type SchemaVersion29 = "1.0";
/**
 * @minItems 1
 * @maxItems 4
 */
export type Forecasts =
  | [IndustryForecastDraftV1]
  | [IndustryForecastDraftV1, IndustryForecastDraftV1]
  | [IndustryForecastDraftV1, IndustryForecastDraftV1, IndustryForecastDraftV1]
  | [IndustryForecastDraftV1, IndustryForecastDraftV1, IndustryForecastDraftV1, IndustryForecastDraftV1];
export type SchemaVersion30 = "1.0";
export type Statement = string;
export type Mechanism1 = string;
export type ExpectedSignal = string;
export type Falsifier = string;
export type Uncertainty = string;
/**
 * @minItems 1
 * @maxItems 3
 */
export type Alternatives = [string] | [string, string] | [string, string, string];
/**
 * @minItems 1
 * @maxItems 12
 */
export type SupportingSourceIds =
  | [string]
  | [string, string]
  | [string, string, string]
  | [string, string, string, string]
  | [string, string, string, string, string]
  | [string, string, string, string, string, string]
  | [string, string, string, string, string, string, string]
  | [string, string, string, string, string, string, string, string]
  | [string, string, string, string, string, string, string, string, string]
  | [string, string, string, string, string, string, string, string, string, string]
  | [string, string, string, string, string, string, string, string, string, string, string]
  | [string, string, string, string, string, string, string, string, string, string, string, string];
/**
 * @maxItems 12
 */
export type CounterSourceIds =
  | []
  | [string]
  | [string, string]
  | [string, string, string]
  | [string, string, string, string]
  | [string, string, string, string, string]
  | [string, string, string, string, string, string]
  | [string, string, string, string, string, string, string]
  | [string, string, string, string, string, string, string, string]
  | [string, string, string, string, string, string, string, string, string]
  | [string, string, string, string, string, string, string, string, string, string]
  | [string, string, string, string, string, string, string, string, string, string, string]
  | [string, string, string, string, string, string, string, string, string, string, string, string];
export type Basis = "direct" | "analogy";
/**
 * @maxItems 4
 */
export type AnalogyCaseIds =
  [] | [string] | [string, string] | [string, string, string] | [string, string, string, string];
/**
 * @minItems 1
 * @maxItems 8
 */
export type Actions =
  | [IndustryActionDraftV1]
  | [IndustryActionDraftV1, IndustryActionDraftV1]
  | [IndustryActionDraftV1, IndustryActionDraftV1, IndustryActionDraftV1]
  | [IndustryActionDraftV1, IndustryActionDraftV1, IndustryActionDraftV1, IndustryActionDraftV1]
  | [IndustryActionDraftV1, IndustryActionDraftV1, IndustryActionDraftV1, IndustryActionDraftV1, IndustryActionDraftV1]
  | [
      IndustryActionDraftV1,
      IndustryActionDraftV1,
      IndustryActionDraftV1,
      IndustryActionDraftV1,
      IndustryActionDraftV1,
      IndustryActionDraftV1
    ]
  | [
      IndustryActionDraftV1,
      IndustryActionDraftV1,
      IndustryActionDraftV1,
      IndustryActionDraftV1,
      IndustryActionDraftV1,
      IndustryActionDraftV1,
      IndustryActionDraftV1
    ]
  | [
      IndustryActionDraftV1,
      IndustryActionDraftV1,
      IndustryActionDraftV1,
      IndustryActionDraftV1,
      IndustryActionDraftV1,
      IndustryActionDraftV1,
      IndustryActionDraftV1,
      IndustryActionDraftV1
    ];
export type SchemaVersion31 = "1.0";
/**
 * Zero-based forecast position
 */
export type ForecastIndex = number;
export type Domain = "career" | "work" | "learning" | "spending" | "finance" | "life" | "health";
export type Action1 = string;
export type Trigger = string;
export type CheckAfterDays = number;
export type TimeMinutes = number;
export type SuccessCheck = string;
export type StopCondition = string;
export type PersonalActions = IndustryActionDraftV1[] | null;
export type FetchCalls = number;
export type ModelCalls = number;
export type ProviderFailures = number;
export type SchemaVersion32 = "1.0";
export type PlanCode = string;
export type ExplicitSandboxConsent = true;
export type SchemaVersion33 = "1.0";
export type ClaimText = string;
export type Quote2 = string;
export type SourceLocator = string;
export type Relation = "supports" | "contradicts" | "context";
export type ClaimKind = "fact" | "opinion" | "hypothesis";
export type VerificationStatus = "unverified" | "verified";
export type VerificationNote1 = string;
export type Scope = string;
export type Caveat = string;
export type SchemaVersion34 = "1.0";
export type Id2 = string;
export type PublicationId = string;
export type Kind3 = "like" | "bookmark";
export type Title1 = string;
export type Summary = string;
export type CreatedAt2 = string;
export type Read = boolean;
export type SchemaVersion35 = "1.0";
export type Name1 = string;
export type Description = string;
export type Domain1 =
  "technology" | "energy" | "healthcare" | "manufacturing" | "education" | "finance" | "services" | "society";
export type SchemaVersion36 = "1.0";
export type Id3 = string;
export type Name2 = string;
export type Description1 = string;
export type Domain2 = string;
export type Public = boolean;
export type Owned = boolean;
export type Added = boolean;
export type PersonalIndustryId = string | null;
export type SourceIndustryId = string | null;
export type SchemaVersion37 = "1.0";
export type IndustryId1 = string | null;
export type ReportVersionId = string;
export type ConfirmPublic = true;
export type SchemaVersion38 = "1.0";
export type VisitorId = string;
export type SchemaVersion39 = "1.0";
export type Id4 = string;
export type IndustryId2 = string | null;
export type IndustryName = string;
export type Title2 = string;
export type Summary1 = string;
export type Label2 = "DEMO" | "REAL";
export type Sample = boolean;
export type Image = string;
export type SchemaVersion40 = "1.0";
export type Heading = string;
export type Text1 = string;
export type Sections = CommunitySectionV1[];
export type CreatedAt3 = string;
export type Author = string;
export type Reason1 = string;
export type ViewsCount = number;
export type LikesCount = number;
export type BookmarksCount = number;
export type Liked = boolean;
export type Saved = boolean;
export type SavedIndustryId = string | null;
export type Owned1 = boolean;
export type Public1 = boolean;
export type SchemaVersion41 = "1.0";
export type IndustryId3 = string;
export type SchemaVersion42 = "1.0";
export type Public2 = boolean;
export type SchemaVersion43 = "1.0";
export type Theme = "system" | "light" | "dark";
export type SchemaVersion44 = "1.0";
export type ModelAvailable = boolean;
export type SchemaVersion45 = "1.0";
export type IndustryId4 = string | null;
export type Question = string;
export type ClientId1 = string;
export type UseModel = boolean;
export type IncludeMemory = boolean;
export type SchemaVersion46 = "1.0";
export type Id5 = string;
export type Name3 = string;
export type Status1 = "pending" | "added" | "already_exists";
export type IndustryId5 = string | null;
export type SchemaVersion47 = "1.0";
export type Text2 = string;
export type ClientId2 = string;
export type UseModel1 = boolean;
export type IncludeMemory1 = boolean;
export type SchemaVersion48 = "1.0";
export type Role1 = "user" | "assistant";
export type Text3 = string;
export type ClientId3 = string | null;
export type Source = ("local" | "llm") | null;
export type SchemaVersion49 = "1.0";
export type ConfirmDemoReuse = true;
export type SchemaVersion50 = "1.0";
export type Id6 = string;
export type IndustryId6 = string | null;
export type Title3 = string;
export type CreatedAt4 = string;
export type Messages = ConversationMessageViewV1[];
export type JobId = string | null;
export type ErrorCode1 = string | null;
export type ReportId = string | null;
export type Mode = "demo_reuse";
export type NewForecastRulesPending = true;
export type SchemaVersion51 = "1.0";
export type SchemaVersion52 = "1.0";
export type Code3 = string;
export type Label3 = string;
export type Entries = CountryOptionV1[];
export type Source1 = "Unicode CLDR";
export type SchemaVersion53 = "1.0";
export type FindingId = string;
export type DraftId1 = string;
export type Category = "evidence" | "historical" | "causal" | "scenario" | "temporal_resolution";
export type Severity = "L0" | "L1" | "L2" | "L3";
export type Statement1 = string;
export type VerifiedSourceRefs = string[];
export type VerificationStatus1 = "pending" | "verified" | "refuted";
export type Scope1 = string;
export type AffectedAssumptionIds = string[];
export type RecommendedAction = string;
export type SchemaVersion54 = "1.0";
export type CriticRunId = string;
export type DraftId2 = string;
export type DraftHash = string;
export type IndependentInputHash = string;
export type SchemaVersion55 = "1.0";
export type FindingId1 = string;
export type Checker = "evidence" | "historical" | "causal" | "scenario" | "temporal_resolution";
export type Code4 = string;
export type Severity1 = "L0" | "L1" | "L2" | "L3";
export type Statement2 = string;
export type VerificationStatus2 = "verified" | "pending" | "refuted";
export type SourceRefs = string[];
export type AffectedFields = string[];
export type RecommendedAction1 = string;
export type Findings = ReviewFindingV1[];
export type CheckersCompleted = string[];
export type RulesVersion = "m3-critic-v1";
export type DurationMs = number;
export type ModelCalls1 = 0;
export type Limitations2 = string[];
export type SchemaVersion56 = "1.0";
export type Password3 = string;
export type SchemaVersion57 = "1.0";
export type ImpactId = string;
export type Relevance = "low" | "medium" | "high";
export type ImpactWindow = string;
export type Actionability = string;
export type Reversibility = "low" | "medium" | "high";
export type CostNote = string;
export type DecisionPriority = "prepare" | "observe" | "no_action";
export type Reasons = string[];
export type Unknowns = string[];
export type ReevaluateIf = string[];
export type SchemaVersion58 = "1.0";
export type Question1 = string;
export type SchemaVersion59 = "1.0";
export type Label4 = "DEMO";
export type Kind4 = "hypothesis";
export type Statement3 = string;
export type ResearchAsOf = string;
/**
 * @minItems 1
 */
export type SourceIds = [string, ...string[]];
/**
 * @minItems 1
 */
export type Limitations3 = [string, ...string[]];
export type ModelId = "mock-llm-v1";
export type PromptHash = string;
export type CostUnits = 0;
export type SchemaVersion60 = "1.0";
export type ExplicitConsent = true;
export type Recipient = string;
export type SchemaVersion61 = "1.0";
export type Email3 = string;
export type Purpose = "register" | "password_reset";
export type HumanToken = string;
export type SchemaVersion62 = "1.0";
export type ChallengeId = string;
export type ExpiresIn1 = number;
export type ResendAfter = number;
export type DeliveryMode = "local_preview" | "smtp" | "disabled";
export type SchemaVersion63 = "1.0";
export type ReportVersionId1 = string;
export type RecipientMasked = string;
export type Subject = string;
export type Summary2 = string;
export type PrivateLink = string;
export type Transport = "mock_local";
export type ExternalDelivery = false;
export type SchemaVersion64 = "1.0";
export type Purpose1 = "first_report" | "alert" | "digest";
export type ExplicitConsent1 = true;
export type SchemaVersion65 = "1.0";
export type UserId2 = string;
export type SubscriptionStatus = "free" | "active" | "cancelled" | "expired";
export type PaidPeriodicResearchEnabled = boolean;
export type EmailDigestOptIn = boolean;
export type EmailAlertOptIn = boolean;
export type SchemaVersion66 = "1.0";
export type Code5 = string;
export type Message = string;
export type RequestId1 = string;
export type SchemaVersion67 = "1.0";
export type ProtocolId = string;
export type VersionId = string;
export type Mode1 = "synthetic" | "temporal_backtest" | "forward";
export type Label5 = "DEMO" | "REAL";
export type RegisteredAt = string;
export type AsOf1 = string;
export type DueAt = string;
export type MetricDefinition = string;
export type Geography = string;
export type Unit1 = string;
export type ResolutionSource = string;
export type Operator = "gte" | "lte" | "eq";
export type Threshold = number;
export type PointPredictionA = number | null;
export type PointPredictionB = number | null;
export type BaselineValue = number | null;
export type SourceSnapshotHash = string;
export type ModelId1 = string;
export type PromptHash1 = string;
export type TestsetVersion = string;
export type ProtocolVersion = "m3-resolution-v1";
export type Limitations4 = string[];
export type SchemaVersion68 = "1.0";
export type Mode2 = "synthetic" | "temporal_backtest" | "forward";
export type Operator1 = "gte" | "lte" | "eq";
export type Threshold1 = number;
export type Unit2 = string;
export type TestsetVersion1 = string;
export type SchemaVersion69 = "1.0";
export type ClaimId = string;
export type SourceVersionId1 = string;
export type SourceGroupId = string;
export type ClaimText1 = string;
export type Quote3 = string;
export type SourceLocator1 = string;
export type Relation1 = "supports" | "contradicts" | "context";
export type ClaimKind1 = "fact" | "opinion" | "hypothesis";
export type KnownAt1 = string | null;
export type VerificationStatus3 = "unverified" | "verified";
export type VerificationNote2 = string;
export type Scope2 = string;
export type Caveat1 = string;
export type Label6 = "DEMO" | "REAL";
export type SchemaVersion70 = "1.0";
export type AddedClaimIds = string[];
export type IndependentGroups = number;
export type DuplicateClaimIds = string[];
export type ChangedObservationIds = string[];
export type Reasons1 = string[];
export type Fingerprint1 = string;
export type SchemaVersion71 = "1.0";
export type Provider = "mock" | "deepseek";
export type Url1 = string;
export type Title4 = string;
export type Content = string;
export type ContentHash1 = string;
export type RetrievedAt1 = string;
export type PublishedAt1 = null;
export type EvidenceStatus = "unverified";
export type Label7 = "DEMO" | "REAL";
export type SchemaVersion72 = "1.0";
export type Label8 = "DEMO" | "REAL";
/**
 * @maxItems 5
 */
export type ForecastVersionIds =
  | []
  | [string]
  | [string, string]
  | [string, string, string]
  | [string, string, string, string]
  | [string, string, string, string, string];
export type SchemaVersion73 = "1.0";
export type DraftId3 = string;
export type RunId = string;
export type DraftSequence = "A" | "B1" | "B2";
export type Kind5 = "hypothesis" | "draft_forecast";
export type Statement4 = string;
export type ResearchAsOf1 = string;
export type SchemaVersion74 = "1.0";
export type TargetType = "binary" | "numeric" | "ordinal" | "milestone";
export type PopulationScope = string;
export type Geography1 = string;
export type MetricDefinition1 = string;
export type DirectionOrThreshold = string;
export type Baseline = string;
export type TargetStartAt = string;
export type TargetEndAt = string;
export type ResolutionSource1 = string;
export type ResolutionRule = string;
export type EvidenceClaimIds = string[];
export type InputsHash = string;
export type ModelVersion = string;
export type SchemaVersion75 = "1.0";
export type ResolutionId = string;
export type ProtocolId1 = string;
export type Status2 = "not_due" | "confirmed" | "disconfirmed" | "inconclusive" | "unresolved_due_to_data";
export type CheckedAt = string;
export type ObservationId = string | null;
export type ObservedValue = number | null;
export type ForecastAbsoluteErrorA = number | null;
export type ForecastAbsoluteErrorB = number | null;
export type BaselineAbsoluteError = number | null;
export type Reason2 = string;
export type SchemaVersion76 = "1.0";
export type ForecastVersionId = string;
export type ForecastId = string;
export type ResearchRunId = string;
export type VersionNum = number;
export type Kind6 = "forecast";
export type Statement5 = string;
export type ResearchAsOf2 = string;
export type ForecastPublishedAt = string;
/**
 * @minItems 1
 */
export type EvidenceClaimIds1 = [string, ...string[]];
export type ContradictionClaimIds = string[];
/**
 * @minItems 1
 */
export type MechanismIds = [string, ...string[]];
export type HistoricalCaseIds = string[];
export type Assumptions = string[];
/**
 * @minItems 1
 */
export type FalsificationConditions = [string, ...string[]];
/**
 * @minItems 1
 */
export type ScenarioIds = [string, ...string[]];
export type UncertaintyState = "uncalibrated" | "qualitative_assessment";
export type NextReviewAt = string;
export type EvidenceSnapshotHash = string;
export type ChangeReason = string;
export type SchemaVersion77 = "1.0";
export type Total = 1;
export type Available = number;
export type Reserved = number;
export type Consumed = number;
export type PaidResearchEnabled = false;
export type SchemaVersion78 = "1.0";
export type Title5 = string;
export type CutoffAt = string;
/**
 * @minItems 1
 */
export type DomainTags = [DomainTag, ...DomainTag[]];
export type DomainTag =
  | "macro_finance"
  | "technology"
  | "industry"
  | "workforce"
  | "policy"
  | "consumption"
  | "housing"
  | "education"
  | "health"
  | "energy"
  | "supply_chain"
  | "society";
export type MechanismTags = string[];
export type InitialConditions = string;
/**
 * @minItems 1
 */
export type Limitations5 = [string, ...string[]];
/**
 * @minItems 1
 */
export type Events = [HistoricalEventImportV1, ...HistoricalEventImportV1[]];
export type Label9 = "DEMO" | "REAL";
export type SchemaVersion79 = "1.0";
export type CaseId2 = string;
export type Title6 = string;
export type CutoffAt1 = string;
export type AsOf2 = string;
export type DomainTags1 = DomainTag[];
export type MechanismTags1 = string[];
export type InitialConditions1 = string;
export type Limitations6 = string[];
export type Contemporaneous = HistoricalEventImportV1[];
export type Outcomes = HistoricalEventImportV1[];
export type Label10 = "DEMO" | "REAL";
export type SchemaVersion80 = "1.0";
export type NotificationId = string;
export type ReportId1 = string;
export type ReportVersionId2 = string;
export type Title7 = string;
export type Summary3 = string;
export type CreatedAt5 = string;
export type Read1 = boolean;
export type SchemaVersion81 = "1.0";
export type Code6 = string;
export type Name4 = string;
export type Provider1 = string;
export type GeoScope = string;
export type Unit3 = string;
export type Frequency = "day" | "week" | "month" | "quarter" | "year" | "irregular";
export type DefinitionVersion = string;
export type Label11 = "DEMO" | "REAL";
export type IndicatorId = string;
export type SchemaVersion82 = "1.0";
export type Code7 = string;
export type Name5 = string;
export type Provider2 = string;
export type GeoScope1 = string;
export type Unit4 = string;
export type Frequency1 = "day" | "week" | "month" | "quarter" | "year" | "irregular";
export type DefinitionVersion1 = string;
export type Label12 = "DEMO" | "REAL";
export type SchemaVersion83 = "1.0";
export type IndicatorId1 = string;
export type PeriodStart = string;
export type PeriodEnd = string;
export type Value = number;
export type PublishedAt2 = string;
export type AvailableAt = string;
export type Vintage = string;
export type QualityFlag = "DEMO_DATA" | "UNVERIFIED" | "VERIFIED";
export type SchemaVersion84 = "1.0";
export type Sufficient = boolean;
/**
 * @maxItems 8
 */
export type Gaps1 =
  | []
  | [string]
  | [string, string]
  | [string, string, string]
  | [string, string, string, string]
  | [string, string, string, string, string]
  | [string, string, string, string, string, string]
  | [string, string, string, string, string, string, string]
  | [string, string, string, string, string, string, string, string];
/**
 * @maxItems 4
 */
export type Queries =
  | []
  | [IndustrySearchQueryV1]
  | [IndustrySearchQueryV1, IndustrySearchQueryV1]
  | [IndustrySearchQueryV1, IndustrySearchQueryV1, IndustrySearchQueryV1]
  | [IndustrySearchQueryV1, IndustrySearchQueryV1, IndustrySearchQueryV1, IndustrySearchQueryV1];
export type SchemaVersion85 = "1.0";
export type Sufficient1 = boolean;
/**
 * @maxItems 8
 */
export type Gaps2 =
  | []
  | [string]
  | [string, string]
  | [string, string, string]
  | [string, string, string, string]
  | [string, string, string, string, string]
  | [string, string, string, string, string, string]
  | [string, string, string, string, string, string, string]
  | [string, string, string, string, string, string, string, string];
/**
 * @maxItems 4
 */
export type Queries1 =
  | []
  | [IndustrySearchQueryV1]
  | [IndustrySearchQueryV1, IndustrySearchQueryV1]
  | [IndustrySearchQueryV1, IndustrySearchQueryV1, IndustrySearchQueryV1]
  | [IndustrySearchQueryV1, IndustrySearchQueryV1, IndustrySearchQueryV1, IndustrySearchQueryV1];
/**
 * @maxItems 16
 */
export type Evidence1 =
  | []
  | [IndustryEvidenceV1]
  | [IndustryEvidenceV1, IndustryEvidenceV1]
  | [IndustryEvidenceV1, IndustryEvidenceV1, IndustryEvidenceV1]
  | [IndustryEvidenceV1, IndustryEvidenceV1, IndustryEvidenceV1, IndustryEvidenceV1]
  | [IndustryEvidenceV1, IndustryEvidenceV1, IndustryEvidenceV1, IndustryEvidenceV1, IndustryEvidenceV1]
  | [
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1
    ]
  | [
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1
    ]
  | [
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1
    ]
  | [
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1
    ]
  | [
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1
    ]
  | [
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1
    ]
  | [
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1
    ]
  | [
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1
    ]
  | [
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1
    ]
  | [
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1
    ]
  | [
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1,
      IndustryEvidenceV1
    ];
/**
 * @maxItems 4
 */
export type AnalogyChains1 =
  | []
  | [IndustryAnalogyChainV1]
  | [IndustryAnalogyChainV1, IndustryAnalogyChainV1]
  | [IndustryAnalogyChainV1, IndustryAnalogyChainV1, IndustryAnalogyChainV1]
  | [IndustryAnalogyChainV1, IndustryAnalogyChainV1, IndustryAnalogyChainV1, IndustryAnalogyChainV1];
export type SchemaVersion86 = "1.0";
export type MonitorEnabled = boolean;
export type PredictionEnabled = boolean;
export type EmailEnabled = boolean;
export type SchemaVersion87 = "1.0";
export type MonitorEnabled1 = boolean;
export type PredictionEnabled1 = boolean;
export type EmailEnabled1 = boolean;
export type IndustryId7 = string;
export type Status3 = "waiting_rules" | "paused";
export type SchemaVersion88 = "1.0";
export type JobId1 = string;
export type RequestId2 = string;
export type SchemaVersion89 = "1.0";
export type JobId2 = string;
export type RequestId3 = string;
export type TraceId = string;
export type Attempts = number;
export type Label13 = "DEMO" | "REAL";
export type Result =
  DemoResearchResultV1 | M2ResearchResultV1 | UserReportResultV1 | MonitorResultV1 | MailDeliveryResultV1 | null;
export type SchemaVersion90 = "1.0";
export type RunId1 = string;
export type DraftId4 = string;
export type Status4 = "internal_draft_ready";
export type Label14 = "DEMO" | "REAL";
export type Kind7 = "hypothesis" | "draft_forecast";
export type PublicationAllowed = false;
export type InputHash = string;
export type DraftHash1 = string;
export type SchemaVersion91 = "1.0";
export type ReportId2 = string;
export type ReportVersionId3 = string;
export type Label15 = "DEMO" | "REAL";
export type Status5 = "private_report_ready";
export type SchemaVersion92 = "1.0";
export type MonitorRunId = string;
export type ForecastId1 = string;
export type OldVersionId = string;
export type NewVersionId = string | null;
export type Level = "T0" | "T1" | "T2" | "T3";
export type Outcome1 = "archived" | "observed" | "retained" | "published" | "review_blocked";
export type Reason3 = string;
export type ChangedFields = string[];
export type RefreshedReports = number;
export type ExternalModelCalls = 0;
export type SchemaVersion93 = "1.0";
export type DeliveryId1 = string;
export type Status6 = "delivered_local" | "suppressed";
export type ExternalDelivery1 = false;
export type ErrorCode2 = string | null;
export type SchemaVersion94 = "1.0";
export type DeliveryId2 = string;
export type ReportVersionId4 = string;
export type Status7 = "saved_locally_not_sent";
export type ExternalDelivery2 = false;
export type ConsentedAt = string;
export type SchemaVersion95 = "1.0";
export type SessionId = string;
export type Kind8 = "user" | "admin";
export type DeviceLabel = string;
export type CreatedAt6 = string;
export type ExpiresAt2 = string;
export type Current = boolean;
export type SchemaVersion96 = "1.0";
export type ParentVersionId = string | null;
export type DraftId5 = string;
export type RunId2 = string;
export type DraftSequence1 = "A" | "B1" | "B2";
export type Status8 = "internal_unreviewed";
export type PublicationAllowed1 = false;
export type Label16 = "DEMO" | "REAL";
export type Kind9 = "hypothesis" | "draft_forecast";
export type Statement6 = string;
export type ResearchAsOf3 = string;
export type LifecycleStage = "emergence" | "growth" | "maturity" | "inflection" | "decline" | "unknown";
export type EvidenceClaimIds2 = string[];
export type ContradictionClaimIds1 = string[];
export type SchemaVersion97 = "1.0";
export type FusionId = string;
export type SignalIds = string[];
export type IndependentSourceGroups = number;
export type Mechanism2 = string;
export type RemainingBottlenecks = string[];
export type EmergentHypotheses = string[];
export type OpposingExplanations = string[];
export type NextObservableSignals = string[];
export type Status9 = "hypothesis";
export type Fusions = SignalFusionV1[];
export type SchemaVersion98 = "1.0";
export type FromNode = string;
export type ToNode = string;
export type Relationship = "enables" | "constrains" | "counteracts";
export type Sign = "positive" | "negative";
export type LagRange = string;
export type Conditions = string[];
/**
 * @minItems 1
 */
export type EvidenceClaimIds3 = [string, ...string[]];
export type Uncertainty1 = string;
export type MechanismChain = MechanismEdgeV1[];
export type Analogies = AnalogyAssessmentV1[];
/**
 * @minItems 3
 * @maxItems 3
 */
export type Scenarios = [ScenarioV1, ScenarioV1, ScenarioV1];
export type SchemaVersion99 = "1.0";
export type ScenarioId = string;
export type Kind10 = "scenario";
export type Path = "base" | "acceleration" | "friction";
export type Statement7 = string;
/**
 * @minItems 1
 */
export type Conditions1 = [string, ...string[]];
/**
 * @minItems 1
 */
export type ObservableSignals = [string, ...string[]];
/**
 * @minItems 1
 */
export type FalsificationConditions1 = [string, ...string[]];
export type SchemaVersion100 = "1.0";
export type Hypothesis = string;
/**
 * @minItems 1
 * @maxItems 6
 */
export type EnablingConditions =
  | [string]
  | [string, string]
  | [string, string, string]
  | [string, string, string, string]
  | [string, string, string, string, string]
  | [string, string, string, string, string, string];
/**
 * @minItems 1
 * @maxItems 6
 */
export type Bottlenecks =
  | [string]
  | [string, string]
  | [string, string, string]
  | [string, string, string, string]
  | [string, string, string, string, string]
  | [string, string, string, string, string, string];
/**
 * @minItems 1
 * @maxItems 6
 */
export type OpposingExplanations1 =
  | [string]
  | [string, string]
  | [string, string, string]
  | [string, string, string, string]
  | [string, string, string, string, string]
  | [string, string, string, string, string, string];
/**
 * @minItems 1
 * @maxItems 6
 */
export type NextObservableSignals1 =
  | [string]
  | [string, string]
  | [string, string, string]
  | [string, string, string, string]
  | [string, string, string, string, string]
  | [string, string, string, string, string, string];
/**
 * @minItems 1
 * @maxItems 6
 */
export type FalsificationConditions2 =
  | [string]
  | [string, string]
  | [string, string, string]
  | [string, string, string, string]
  | [string, string, string, string, string]
  | [string, string, string, string, string, string];
/**
 * @minItems 1
 */
export type CitedClaimIds = [string, ...string[]];
export type Assumptions1 = string[];
/**
 * @minItems 1
 */
export type FalsificationConditions3 = [string, ...string[]];
export type UncertaintyState1 = "uncalibrated";
export type NextReviewAt1 = string;
export type Limitations7 = string[];
export type DowngradeReasons = string[];
export type InputHash1 = string;
export type PromptHash2 = string;
export type ModelId2 = string;
export type RulesVersion1 = "m2-rules-v1";
export type SchemaVersion101 = "1.0";
/**
 * @maxItems 10
 */
export type Assertions =
  | []
  | [ChangeAssertionV1]
  | [ChangeAssertionV1, ChangeAssertionV1]
  | [ChangeAssertionV1, ChangeAssertionV1, ChangeAssertionV1]
  | [ChangeAssertionV1, ChangeAssertionV1, ChangeAssertionV1, ChangeAssertionV1]
  | [ChangeAssertionV1, ChangeAssertionV1, ChangeAssertionV1, ChangeAssertionV1, ChangeAssertionV1]
  | [ChangeAssertionV1, ChangeAssertionV1, ChangeAssertionV1, ChangeAssertionV1, ChangeAssertionV1, ChangeAssertionV1]
  | [
      ChangeAssertionV1,
      ChangeAssertionV1,
      ChangeAssertionV1,
      ChangeAssertionV1,
      ChangeAssertionV1,
      ChangeAssertionV1,
      ChangeAssertionV1
    ]
  | [
      ChangeAssertionV1,
      ChangeAssertionV1,
      ChangeAssertionV1,
      ChangeAssertionV1,
      ChangeAssertionV1,
      ChangeAssertionV1,
      ChangeAssertionV1,
      ChangeAssertionV1
    ]
  | [
      ChangeAssertionV1,
      ChangeAssertionV1,
      ChangeAssertionV1,
      ChangeAssertionV1,
      ChangeAssertionV1,
      ChangeAssertionV1,
      ChangeAssertionV1,
      ChangeAssertionV1,
      ChangeAssertionV1
    ]
  | [
      ChangeAssertionV1,
      ChangeAssertionV1,
      ChangeAssertionV1,
      ChangeAssertionV1,
      ChangeAssertionV1,
      ChangeAssertionV1,
      ChangeAssertionV1,
      ChangeAssertionV1,
      ChangeAssertionV1,
      ChangeAssertionV1
    ];
export type SchemaVersion102 = "1.0";
export type Enabled1 = boolean;
export type IntervalSeconds = number;
export type CooldownSeconds = number;
export type MaxDailyJobs = number;
export type IndependentGroupsRequired = number;
export type IndicatorAbsoluteDelta = number | null;
export type ConsecutivePeriods = number;
export type SchemaVersion103 = "1.0";
export type UserId3 = string;
export type ReportVersionId5 = string;
export type Channel = "in_app" | "email";
export type Reason4 = string;
export type ConsentSnapshotRef = string | null;
export type DedupeKey = string;
export type Eligible = boolean;
export type SchemaVersion104 = "1.0";
export type FirstReportOptIn = boolean;
export type AlertOptIn = boolean;
export type DigestOptIn = boolean;
export type Frequency2 = "daily" | "weekly";
export type ExplicitConsent2 = boolean;
export type SchemaVersion105 = "1.0";
export type SourceVersionId2 = string;
export type PeriodStart1 = string;
export type PeriodEnd1 = string;
export type Value1 = number;
export type PublishedAt3 = string;
export type AvailableAt1 = string;
export type RevisionNumber = number;
export type QualityFlag1 = "DEMO_DATA" | "UNVERIFIED" | "VERIFIED";
export type DefinitionNote = string;
export type SchemaVersion106 = "1.0";
export type SourceVersionId3 = string;
export type PeriodStart2 = string;
export type PeriodEnd2 = string;
export type Value2 = number;
export type PublishedAt4 = string;
export type AvailableAt2 = string;
export type RevisionNumber1 = number;
export type QualityFlag2 = "DEMO_DATA" | "UNVERIFIED" | "VERIFIED";
export type DefinitionNote1 = string;
export type ObservationId1 = string;
export type IndicatorId2 = string;
export type Label17 = "DEMO" | "REAL";
export type SchemaVersion107 = "1.0";
export type Action2 = "queued" | "existing_report";
export type JobId3 = string | null;
export type ReportId3 = string | null;
export type UserTopicId = string | null;
export type ReservedUnits = number;
export type Deduplicated = boolean;
export type SchemaVersion108 = "1.0";
export type QuoteId = string;
export type AcceptUsageRules = true;
export type SchemaVersion109 = "1.0";
export type Email4 = string;
export type Password4 = string;
export type VerificationId = string;
export type Code8 = string;
export type SchemaVersion110 = "1.0";
export type Provider3 = "mock";
export type Label18 = "DEMO";
export type EventId1 = string;
export type CheckoutId = string;
export type ProviderReference = string;
export type EventType = "checkout.paid" | "checkout.refunded";
export type AmountMinor1 = number;
export type Currency1 = "CNY";
export type OccurredAt = string;
export type SchemaVersion111 = "1.0";
export type SubscriptionId = string;
export type ExplicitPeriodicConsent = true;
export type SchemaVersion112 = "1.0";
export type ImpactId1 = string;
export type UserId4 = string;
export type ProfileSnapshotId = string;
export type ForecastVersionId1 = string;
export type Relevance1 = "low" | "medium" | "high";
export type MechanismPath = string[];
export type RelevanceReason = string;
export type PositiveImpacts = string[];
export type NegativeImpacts = string[];
export type ApplicableConditions = string[];
export type Uncertainty2 = string;
export type MatchedDomains = string[];
export type SchemaVersion113 = "1.0";
export type Password5 = string;
export type Confirmation = "DELETE MY DATA";
export type SchemaVersion114 = "1.0";
export type ErasureId = string;
export type ErasedAt = string;
export type Retained = string[];
export type BackupNotice = string;
export type SchemaVersion115 = "1.0";
export type ImpactId2 = string;
export type UserId5 = string;
export type ProfileSnapshotId1 = string;
export type ForecastVersionId2 = string;
export type AffectedArea = string;
export type MechanismPath1 = string[];
export type RelevanceReason1 = string;
export type PositiveImpacts1 = string[];
export type NegativeImpacts1 = string[];
export type TimeHorizon = string;
export type ApplicableConditions1 = string[];
export type Uncertainty3 = string;
export type UpdatedAt = string;
export type SchemaVersion116 = "1.0";
export type RequestId4 = string;
export type UserId6 = string;
export type TopicId = string;
export type ProfileSnapshotId2 = string;
export type EntitlementReservationId = string | null;
export type RequestKind = "first_report" | "new_topic" | "material_review";
export type IdempotencyKey = string;
export type SchemaVersion117 = "1.0";
export type ReportId4 = string;
export type ReportVersionId6 = string;
export type UserId7 = string;
export type VersionNum1 = number;
export type ProfileSnapshotId3 = string;
export type ProfileRevision = number;
export type Label19 = "DEMO" | "REAL";
export type Title8 = string;
export type CreatedAt7 = string;
/**
 * @minItems 1
 */
export type ForecastVersionIds1 = [string, ...string[]];
export type PrimaryImpacts = PersonalAssessmentV1[];
export type ObservationOnly = PersonalAssessmentV1[];
export type SchemaVersion118 = "1.0";
export type RecommendationId = string;
export type ImpactId3 = string;
export type Action3 = string;
export type Rationale1 = string;
/**
 * @minItems 1
 */
export type ForecastVersionIds2 = [string, ...string[]];
export type Applicability = string;
export type SuggestedStart = string;
export type ReviewDate = string;
export type EstimatedEffortAndCost = string;
export type Tradeoffs = string;
/**
 * @minItems 1
 */
export type Alternatives1 = [string, ...string[]];
/**
 * @minItems 1
 */
export type SuccessMetrics = [string, ...string[]];
export type StopOrRevisitCondition = string;
export type Priority = "prepare" | "observe" | "no_action";
export type PersonalizationAssumptions = string[];
export type SuppressedHighRiskActions = string[];
export type Recommendations = RecommendationV1[];
export type EvidenceGaps = string[];
export type Limitations8 = string[];
export type AlgorithmVersion = "m4-personal-v1";
export type PreviousReportVersionId = string | null;
export type ChangeSummary = string[];
export type SchemaVersion119 = "1.0";
export type IndustryL1Code = string;
export type IndustryL2Code = string;
export type IndustryDetail = string;
export type OccupationText = string;
export type CountryCode = string;
export type Subdivision = string;
export type Gender = ("female" | "male" | "other") | null;
export type Age = number | null;
export type Region1 = string;
/**
 * @maxItems 5
 */
export type Goals =
  | []
  | [string]
  | [string, string]
  | [string, string, string]
  | [string, string, string, string]
  | [string, string, string, string, string];
/**
 * @maxItems 8
 */
export type Tasks =
  | []
  | [string]
  | [string, string]
  | [string, string, string]
  | [string, string, string, string]
  | [string, string, string, string, string]
  | [string, string, string, string, string, string]
  | [string, string, string, string, string, string, string]
  | [string, string, string, string, string, string, string, string];
export type AvailableMinutesPerWeek = number | null;
export type AllowLowCostExperiments = boolean;
export type UseOptionalFields = boolean;
export type Locale = "zh-CN" | "en";
export type Timezone = "Asia/Shanghai" | "UTC";
export type SchemaVersion120 = "1.0";
export type SnapshotId = string;
export type UserId8 = string;
export type ProfileRevision1 = number;
export type ConsentScope = "industry_only" | "optional_fields";
export type CreatedAt8 = string;
export type SnapshotHash = string;
export type SchemaVersion121 = "1.0";
export type UserId9 = string;
export type Revision = number;
export type UpdatedAt1 = string;
export type TaxonomyVersion = string;
export type SchemaVersion122 = "1.0";
export type Email5 = string;
export type Password6 = string;
export type HumanToken1 = string;
export type SchemaVersion123 = "1.0";
export type ReviewId = string;
export type ChangeReason1 = string;
export type SchemaVersion124 = "1.0";
export type VersionId1 = string;
export type ForecastId2 = string;
export type VersionNum2 = number;
export type DraftId6 = string;
export type ReviewId1 = string;
export type Label20 = "DEMO" | "REAL";
export type PublishedAt5 = string;
export type VersionHash = string;
export type ChangeReason2 = string;
export type SchemaVersion125 = "1.0";
export type Status10 = "helpful" | "not_applicable" | "taken" | "hide";
export type SchemaVersion126 = "1.0";
export type RunId3 = string;
export type Identical = boolean;
export type InputHash2 = string;
export type OriginalDraftHash = string;
export type ReplayDraftHash = string;
export type NetworkCalls = 0;
export type SchemaVersion127 = "1.0";
export type ReportId5 = string;
export type ReportVersionId7 = string;
export type VersionNum3 = number;
export type Title9 = string;
export type Label21 = "DEMO" | "REAL";
export type CreatedAt9 = string;
export type SchemaVersion128 = "1.0";
export type JobId4 = string;
export type RequestId5 = string;
export type RunId4 = string;
export type SchemaVersion129 = "1.0";
export type Scope3 = string;
export type MatchedVersionIds = string[];
export type AvailableFreeReports = number;
export type AdditionalQuestions = string[];
export type Limitations9 = string[];
export type SchemaVersion130 = "1.0";
export type Question2 = string;
export type Label22 = "DEMO" | "REAL";
export type SchemaVersion131 = "1.0";
export type QuoteId1 = string;
export type SchemaVersion132 = "1.0";
export type Domain3 =
  | "technology"
  | "manufacturing"
  | "healthcare"
  | "education"
  | "finance"
  | "services"
  | "logistics"
  | "energy"
  | "society";
export type Focus = "workflow_adoption" | "integration_constraints";
export type Population = "small_teams" | "large_organizations";
export type Geography2 = "global" | "CN";
export type Label23 = "DEMO" | "REAL";
export type ScopeFingerprint = string;
export type Kind11 = "new_topic" | "existing_topic";
export type UnitsRequired = number;
export type ExistingReportId = string | null;
export type ExpiresAt3 = string;
export type Rules = string[];
export type SchemaVersion133 = "1.0";
export type RunId5 = string;
export type TopicId1 = string;
export type JobId5 = string;
export type Title10 = string;
export type ResearchAsOf4 = string;
export type InputHash3 = string;
export type EngineCodeHash = string;
export type Provider4 = "mock" | "deepseek" | "incremental";
export type ModelId3 = string;
export type Label24 = "DEMO" | "REAL";
export type DraftHash2 = string | null;
export type ErrorCode3 = string | null;
export type SchemaVersion134 = "1.0";
export type SchemaVersion135 = "1.0";
export type Title11 = string;
export type Scope4 = string;
/**
 * @minItems 1
 * @maxItems 12
 */
export type DomainTags2 =
  | [DomainTag]
  | [DomainTag, DomainTag]
  | [DomainTag, DomainTag, DomainTag]
  | [DomainTag, DomainTag, DomainTag, DomainTag]
  | [DomainTag, DomainTag, DomainTag, DomainTag, DomainTag]
  | [DomainTag, DomainTag, DomainTag, DomainTag, DomainTag, DomainTag]
  | [DomainTag, DomainTag, DomainTag, DomainTag, DomainTag, DomainTag, DomainTag]
  | [DomainTag, DomainTag, DomainTag, DomainTag, DomainTag, DomainTag, DomainTag, DomainTag]
  | [DomainTag, DomainTag, DomainTag, DomainTag, DomainTag, DomainTag, DomainTag, DomainTag, DomainTag]
  | [DomainTag, DomainTag, DomainTag, DomainTag, DomainTag, DomainTag, DomainTag, DomainTag, DomainTag, DomainTag]
  | [
      DomainTag,
      DomainTag,
      DomainTag,
      DomainTag,
      DomainTag,
      DomainTag,
      DomainTag,
      DomainTag,
      DomainTag,
      DomainTag,
      DomainTag
    ]
  | [
      DomainTag,
      DomainTag,
      DomainTag,
      DomainTag,
      DomainTag,
      DomainTag,
      DomainTag,
      DomainTag,
      DomainTag,
      DomainTag,
      DomainTag,
      DomainTag
    ];
export type ResearchAsOf5 = string;
/**
 * @minItems 1
 * @maxItems 20
 */
export type SignalIds1 =
  | [string]
  | [string, string]
  | [string, string, string]
  | [string, string, string, string]
  | [string, string, string, string, string]
  | [string, string, string, string, string, string]
  | [string, string, string, string, string, string, string]
  | [string, string, string, string, string, string, string, string]
  | [string, string, string, string, string, string, string, string, string]
  | [string, string, string, string, string, string, string, string, string, string]
  | [string, string, string, string, string, string, string, string, string, string, string]
  | [string, string, string, string, string, string, string, string, string, string, string, string]
  | [string, string, string, string, string, string, string, string, string, string, string, string, string]
  | [string, string, string, string, string, string, string, string, string, string, string, string, string, string]
  | [
      string,
      string,
      string,
      string,
      string,
      string,
      string,
      string,
      string,
      string,
      string,
      string,
      string,
      string,
      string
    ]
  | [
      string,
      string,
      string,
      string,
      string,
      string,
      string,
      string,
      string,
      string,
      string,
      string,
      string,
      string,
      string,
      string
    ]
  | [
      string,
      string,
      string,
      string,
      string,
      string,
      string,
      string,
      string,
      string,
      string,
      string,
      string,
      string,
      string,
      string,
      string
    ]
  | [
      string,
      string,
      string,
      string,
      string,
      string,
      string,
      string,
      string,
      string,
      string,
      string,
      string,
      string,
      string,
      string,
      string,
      string
    ]
  | [
      string,
      string,
      string,
      string,
      string,
      string,
      string,
      string,
      string,
      string,
      string,
      string,
      string,
      string,
      string,
      string,
      string,
      string,
      string
    ]
  | [
      string,
      string,
      string,
      string,
      string,
      string,
      string,
      string,
      string,
      string,
      string,
      string,
      string,
      string,
      string,
      string,
      string,
      string,
      string,
      string
    ];
/**
 * @maxItems 10
 */
export type HistoricalCaseIds1 =
  | []
  | [string]
  | [string, string]
  | [string, string, string]
  | [string, string, string, string]
  | [string, string, string, string, string]
  | [string, string, string, string, string, string]
  | [string, string, string, string, string, string, string]
  | [string, string, string, string, string, string, string, string]
  | [string, string, string, string, string, string, string, string, string]
  | [string, string, string, string, string, string, string, string, string, string];
export type IndicatorId3 = string | null;
export type LifecycleStage1 = "emergence" | "growth" | "maturity" | "inflection" | "decline" | "unknown";
export type RecipeId = "verifiable_agent" | "technology_diffusion";
export type Provider5 = "mock" | "deepseek";
export type Label25 = "DEMO" | "REAL";
export type SchemaVersion136 = "1.0";
export type SignalId = string;
export type Kind12 = "signal";
export type Status11 = "candidate";
export type Headline = string;
export type ClaimIds1 = string[];
export type SourceGroupIds = string[];
export type IndependentSourceCount = number;
export type MechanismTags2 = string[];
export type DomainTags3 = DomainTag[];
export type DetectedAt = string;
export type Label26 = "DEMO" | "REAL";
export type Signals = SignalV1[];
export type Claims = EvidenceClaimV1[];
export type SchemaVersion137 = "1.0";
export type SourceVersionId4 = string;
export type SourceId3 = string;
export type SourceGroupId1 = string;
export type SourceType = string;
export type OriginalLanguage = string;
export type Region2 = string;
export type DedupMethod = string;
export type OriginalSourceUrl = string | null;
export type VersionLabel = string;
export type Url2 = string;
export type Title12 = string;
export type Publisher = string;
export type PublishedAt6 = string | null;
export type EventAt = string | null;
export type AvailableAt3 = string | null;
export type IngestedAt = string;
export type RevisedAt = string | null;
export type AvailabilityBasis = string;
export type AvailabilityNote = string;
export type ContentHash2 = string;
export type Content1 = string;
export type UsagePermission = string;
export type LicenseNote = string;
export type AccessMethod = string;
export type ReliabilityNote = string;
export type DomainTags4 = DomainTag[];
export type Label27 = "DEMO" | "REAL";
export type Sources1 = SourceVersionV1[];
export type Cases = HistoricalCaseViewV1[];
export type Observations = ObservationV1[];
export type EngineCodeHash1 = string;
export type RulesVersion2 = "m2-rules-v1";
export type SchemaVersion138 = "1.0";
export type TopicId2 = string;
export type OwnerUserId = string | null;
export type Title13 = string;
export type Scope5 = string;
export type DomainTags5 = string[];
export type Version = number;
export type SchemaVersion139 = "1.0";
export type ObservationId2 = string | null;
export type UnavailableReason = string | null;
export type SchemaVersion140 = "1.0";
export type DecisionId1 = string;
export type CriticRunId1 = string;
export type DraftId7 = string;
export type Decision1 = "accept" | "annotate" | "targeted_research" | "block" | "research_only";
export type PublicationAllowed2 = boolean;
export type VerifiedFindingIds = string[];
export type RuleVersion1 = "m3-adjudication-v1";
export type Rationale2 = string;
export type DecidedAt1 = string;
export type SchemaVersion141 = "1.0";
export type SchemaVersion142 = "1.0";
export type ReviewId2 = string;
/**
 * @minItems 1
 */
export type ConfirmedFindingIds = [string, ...string[]];
/**
 * @maxItems 10
 */
export type AdditionalCaseIds =
  | []
  | [string]
  | [string, string]
  | [string, string, string]
  | [string, string, string, string]
  | [string, string, string, string, string]
  | [string, string, string, string, string, string]
  | [string, string, string, string, string, string, string]
  | [string, string, string, string, string, string, string, string]
  | [string, string, string, string, string, string, string, string, string]
  | [string, string, string, string, string, string, string, string, string, string];
export type SchemaVersion143 = "1.0";
export type DraftId8 = string;
export type ParentDraftId = string;
export type DraftSequence2 = "B1" | "B2";
export type InputHash4 = string;
export type DraftHash3 = string;
export type SchemaVersion144 = "1.0";
export type ExplicitSandboxConsent1 = true;
export type SchemaVersion145 = "1.0";
export type HitId = string;
export type Provider6 = "mock" | "deepseek";
export type Url3 = string;
export type Title14 = string;
export type Snippet = string;
export type Summary4 = string;
export type Content2 = string;
export type SiteName = string | null;
export type PublishedAt7 = string | null;
export type RetrievedAt2 = string;
export type ProviderRankScore = number | null;
export type ProviderAuthority = number | null;
export type EvidenceStatus1 = "unverified";
export type Label28 = "DEMO" | "REAL";
export type SchemaVersion146 = "1.0";
export type Headline1 = string;
/**
 * @minItems 1
 */
export type ClaimIds2 = [string, ...string[]];
export type LifecycleStage2 = "emergence" | "growth" | "maturity" | "inflection" | "decline" | "unknown";
export type MechanismTags3 = string[];
/**
 * @minItems 1
 */
export type DomainTags6 = [DomainTag, ...DomainTag[]];
export type SchemaVersion147 = "1.0";
export type Url4 = string;
export type Title15 = string;
export type Publisher1 = string;
export type SourceType1 = "official" | "paper" | "licensed_data" | "news" | "community" | "manual";
export type OriginalLanguage1 = string;
export type Region3 = string;
export type PublishedAt8 = string | null;
export type EventAt1 = string | null;
export type AvailableAt4 = string | null;
export type AvailabilityBasis1 = "observed_now" | "verified_archive" | "verified_release" | "unknown";
export type AvailabilityNote1 = string;
export type RevisedAt1 = string | null;
export type Content3 = string;
export type UsagePermission1 = "metadata_only" | "excerpt" | "authorized_full";
export type LicenseNote1 = string;
export type AccessMethod1 = "manual" | "deepseek" | "archive" | "licensed_api";
export type ReliabilityNote1 = string;
export type OriginalSourceUrl1 = string | null;
/**
 * @minItems 1
 */
export type DomainTags7 = [DomainTag, ...DomainTag[]];
export type Claims1 = ClaimImportV1[];
export type Label29 = "DEMO" | "REAL";
export type SchemaVersion148 = "1.0";
export type ClaimIds3 = string[];
export type Duplicate = boolean;
export type SchemaVersion149 = "1.0";
export type SourceId4 = string;
export type Url5 = string;
export type PublishedAt9 = string;
export type Provenance = string;
export type Snippet1 = string;
export type Label30 = "DEMO" | "REAL";
export type SchemaVersion150 = "1.0";
export type Level1 = "T0" | "T1" | "T2" | "T3";
export type Action4 = "archive" | "observe" | "targeted_research" | "block_pending_review";
export type Rationale3 = string;
export type RulesVersion3 = "m5-turning-v1";
export type SchemaVersion151 = "1.0";
export type TriggerId = string;
export type ForecastId3 = string;
export type OldVersionId1 = string;
export type NewVersionId1 = string | null;
export type FinalLevel = "T0" | "T1" | "T2" | "T3";
export type Decision2 = "archive" | "observe" | "retain" | "reforecast" | "personal_impact_only";
export type EvidenceDeltaHash = string;
export type ReviewedAt = string;
export type SchemaVersion152 = "1.0";
export type ReportId6 = string;
export type UserId10 = string;
export type CurrentVersionId = string;
export type SchemaVersion153 = "1.0";
export type ReportVersionId8 = string;
export type ReportId7 = string;
export type UserId11 = string;
export type ReportVersion = number;
export type ProfileSnapshotId4 = string;
export type ResearchAsOf6 = string;
/**
 * @minItems 1
 */
export type ForecastVersionIds3 = [string, ...string[]];
/**
 * @minItems 1
 */
export type PersonalImpactIds = [string, ...string[]];
export type ChangeReason3 = string;
export type CreatedAt10 = string;
export type SchemaVersion154 = "1.0";
export type Email6 = string;
export type Password7 = string;
export type VerificationId1 = string;
export type Code9 = string;
export type SchemaVersion155 = "1.0";
export type Url6 = string;
export type Title16 = string;
export type Excerpt1 = string;
export type FullContentHash = string;
export type RetrievedAt3 = string;
export type PublishedAt10 = null;
export type Label31 = "REAL";
export type EvidenceStatus2 = "unverified";
export type RetainedCharacters = number;
export type SchemaVersion156 = "1.0";
export type Url7 = string;
export type SchemaVersion157 = "1.0";
export type Query1 = string;
export type Count = number;
export type SchemaVersion158 = "1.0";
export type Results = SearchHitV1[];
export type SchemaVersion159 = "1.0";
export type ForecastId4 = string;
export type TopicId3 = string;
export type StableTargetKey = string;
export type TargetType1 = "binary" | "numeric" | "ordinal" | "milestone";
export type CurrentVersionId1 = string | null;

export interface DomainContracts {
  AccountCredentialsV1?: AccountCredentialsV1;
  AccountIdentityV1?: AccountIdentityV1;
  AccountSessionV1?: AccountSessionV1;
  AdjudicationDecisionV1?: AdjudicationDecisionV1;
  AdminAccessChangeV1?: AdminAccessChangeV1;
  AdminBootstrapV1?: AdminBootstrapV1;
  AdminChallengeV1?: AdminChallengeV1;
  AdminCreateV1?: AdminCreateV1;
  AdminSecondFactorV1?: AdminSecondFactorV1;
  AdminSessionV1?: AdminSessionV1;
  AdminStepUpV1?: AdminStepUpV1;
  AnalogyAssessmentV1?: AnalogyAssessmentV1;
  AuthAccessEventViewV1?: AuthAccessEventViewV1;
  AuthConfigurationV1?: AuthConfigurationV1;
  BaselineV1?: BaselineV1;
  BillingPlanV1?: BillingPlanV1;
  BounceEventV1?: BounceEventV1;
  ChangeAssertionV1?: ChangeAssertionV1;
  ChatResearchStageViewV1?: ChatResearchStageViewV1;
  ChatResearchStartV1?: ChatResearchStartV1;
  ChatResearchViewV1?: ChatResearchViewV1;
  CheckoutRequestV1?: CheckoutRequestV1;
  ClaimImportV1?: ClaimImportV1;
  CommunityActivityV1?: CommunityActivityV1;
  CommunityIndustryInputV1?: CommunityIndustryInputV1;
  CommunityIndustryViewV1?: CommunityIndustryViewV1;
  CommunityPublishV1?: CommunityPublishV1;
  CommunityReadInputV1?: CommunityReadInputV1;
  CommunityReportViewV1?: CommunityReportViewV1;
  CommunitySaveReportV1?: CommunitySaveReportV1;
  CommunitySectionV1?: CommunitySectionV1;
  CommunityVisibilityV1?: CommunityVisibilityV1;
  ConsumerPreferenceV1?: ConsumerPreferenceV1;
  ConversationCapabilitiesV1?: ConversationCapabilitiesV1;
  ConversationCreateV1?: ConversationCreateV1;
  ConversationIndustryProposalV1?: ConversationIndustryProposalV1;
  ConversationMessageV1?: ConversationMessageV1;
  ConversationMessageViewV1?: ConversationMessageViewV1;
  ConversationStartV1?: ConversationStartV1;
  ConversationViewV1?: ConversationViewV1;
  CountryCatalogV1?: CountryCatalogV1;
  CountryOptionV1?: CountryOptionV1;
  CriticFindingV1?: CriticFindingV1;
  CriticReportV1?: CriticReportV1;
  CurrentPasswordV1?: CurrentPasswordV1;
  DecisionValueV1?: DecisionValueV1;
  DemoResearchInputV1?: DemoResearchInputV1;
  DemoResearchResultV1?: DemoResearchResultV1;
  EmailAuthorizationV1?: EmailAuthorizationV1;
  EmailCodeRequestV1?: EmailCodeRequestV1;
  EmailCodeSentV1?: EmailCodeSentV1;
  EmailPreviewV1?: EmailPreviewV1;
  EmailQueueRequestV1?: EmailQueueRequestV1;
  EntitlementV1?: EntitlementV1;
  ErrorV1?: ErrorV1;
  EvaluationProtocolV1?: EvaluationProtocolV1;
  EvaluationRegisterV1?: EvaluationRegisterV1;
  EvidenceClaimV1?: EvidenceClaimV1;
  EvidenceDeltaV1?: EvidenceDeltaV1;
  FetchedPageV1?: FetchedPageV1;
  FirstReportRequestV1?: FirstReportRequestV1;
  ForecastDraftV1?: ForecastDraftV1;
  ForecastResolutionV1?: ForecastResolutionV1;
  ForecastTargetV1?: ForecastTargetV1;
  ForecastVersionV1?: ForecastVersionV1;
  FreeReportEntitlementV1?: FreeReportEntitlementV1;
  HistoricalCaseImportV1?: HistoricalCaseImportV1;
  HistoricalCaseViewV1?: HistoricalCaseViewV1;
  HistoricalEventImportV1?: HistoricalEventImportV1;
  InAppNotificationV1?: InAppNotificationV1;
  IndicatorDefinitionV1?: IndicatorDefinitionV1;
  IndicatorImportV1?: IndicatorImportV1;
  IndicatorObservationVintageV1?: IndicatorObservationVintageV1;
  IndustryActionDraftV1?: IndustryActionDraftV1;
  IndustryAnalogyChainV1?: IndustryAnalogyChainV1;
  IndustryAnalogyMilestoneV1?: IndustryAnalogyMilestoneV1;
  IndustryCoverageReviewV1?: IndustryCoverageReviewV1;
  IndustryEvidenceReviewV1?: IndustryEvidenceReviewV1;
  IndustryEvidenceV1?: IndustryEvidenceV1;
  IndustryForecastDraftV1?: IndustryForecastDraftV1;
  IndustryReportDraftV1?: IndustryReportDraftV1;
  IndustryResearchRunV1?: IndustryResearchRunV1;
  IndustryResearchScopeV1?: IndustryResearchScopeV1;
  IndustrySearchQueryV1?: IndustrySearchQueryV1;
  IndustrySourceExcerptV1?: IndustrySourceExcerptV1;
  IndustryTrackingV1?: IndustryTrackingV1;
  IndustryTrackingViewV1?: IndustryTrackingViewV1;
  JobAcceptedV1?: JobAcceptedV1;
  JobV1?: JobV1;
  LocalDeliveryV1?: LocalDeliveryV1;
  LoginSessionViewV1?: LoginSessionViewV1;
  M2DraftV1?: M2DraftV1;
  M2ResearchResultV1?: M2ResearchResultV1;
  MailDeliveryResultV1?: MailDeliveryResultV1;
  MechanismEdgeV1?: MechanismEdgeV1;
  MonitorCheckRequestV1?: MonitorCheckRequestV1;
  MonitorPolicyV1?: MonitorPolicyV1;
  MonitorResultV1?: MonitorResultV1;
  NotificationEligibilityV1?: NotificationEligibilityV1;
  NotificationPreferencesV1?: NotificationPreferencesV1;
  ObservationImportV1?: ObservationImportV1;
  ObservationV1?: ObservationV1;
  PaidResearchAcceptedV1?: PaidResearchAcceptedV1;
  PaidResearchSubmitV1?: PaidResearchSubmitV1;
  PasswordResetV1?: PasswordResetV1;
  PaymentEventV1?: PaymentEventV1;
  PeriodicResearchRequestV1?: PeriodicResearchRequestV1;
  PersonalAssessmentV1?: PersonalAssessmentV1;
  PersonalDataEraseV1?: PersonalDataEraseV1;
  PersonalDataErasedV1?: PersonalDataErasedV1;
  PersonalImpactV1?: PersonalImpactV1;
  PredictionRequestV1?: PredictionRequestV1;
  PrivateReportV1?: PrivateReportV1;
  ProfileInputV1?: ProfileInputV1;
  ProfileSnapshotV1?: ProfileSnapshotV1;
  ProfileViewV1?: ProfileViewV1;
  ProtectedLoginV1?: ProtectedLoginV1;
  PublishRequestV1?: PublishRequestV1;
  PublishedForecastV1?: PublishedForecastV1;
  RecommendationFeedbackV1?: RecommendationFeedbackV1;
  RecommendationV1?: RecommendationV1;
  ReplayResultV1?: ReplayResultV1;
  ReportSummaryV1?: ReportSummaryV1;
  ResearchAcceptedV1?: ResearchAcceptedV1;
  ResearchIntakeResultV1?: ResearchIntakeResultV1;
  ResearchIntakeV1?: ResearchIntakeV1;
  ResearchNarrativeV1?: ResearchNarrativeV1;
  ResearchQuoteV1?: ResearchQuoteV1;
  ResearchRunViewV1?: ResearchRunViewV1;
  ResearchScopeV1?: ResearchScopeV1;
  ResearchSnapshotV1?: ResearchSnapshotV1;
  ResearchSubmitV1?: ResearchSubmitV1;
  ResearchTopicV1?: ResearchTopicV1;
  ResolveRequestV1?: ResolveRequestV1;
  ReviewDecisionV1?: ReviewDecisionV1;
  ReviewFindingV1?: ReviewFindingV1;
  ReviewViewV1?: ReviewViewV1;
  RevisionRequestV1?: RevisionRequestV1;
  RevisionViewV1?: RevisionViewV1;
  SandboxConsentV1?: SandboxConsentV1;
  ScenarioV1?: ScenarioV1;
  SearchHitV1?: SearchHitV1;
  SignalFusionV1?: SignalFusionV1;
  SignalImportV1?: SignalImportV1;
  SignalV1?: SignalV1;
  SourceImportV1?: SourceImportV1;
  SourceIngestedV1?: SourceIngestedV1;
  SourceV1?: SourceV1;
  SourceVersionV1?: SourceVersionV1;
  TurningDecisionV1?: TurningDecisionV1;
  TurningPointReviewV1?: TurningPointReviewV1;
  UserReportResultV1?: UserReportResultV1;
  UserReportV1?: UserReportV1;
  UserReportVersionV1?: UserReportVersionV1;
  VerifiedRegistrationV1?: VerifiedRegistrationV1;
  WebFetchPreviewV1?: WebFetchPreviewV1;
  WebFetchRequestV1?: WebFetchRequestV1;
  WebSearchRequestV1?: WebSearchRequestV1;
  WebSearchResponseV1?: WebSearchResponseV1;
  WorldForecastV1?: WorldForecastV1;
}
export interface AccountCredentialsV1 {
  schema_version?: SchemaVersion;
  email: Email;
  password: Password;
}
export interface AccountIdentityV1 {
  schema_version?: SchemaVersion1;
  user_id: UserId;
  role: Role;
  email_masked: EmailMasked;
  email_verified?: EmailVerified;
}
export interface AccountSessionV1 {
  schema_version?: SchemaVersion2;
  access_token: AccessToken;
  expires_at: ExpiresAt;
  identity: AccountIdentityV1;
}
export interface AdjudicationDecisionV1 {
  schema_version?: SchemaVersion3;
  decision_id: DecisionId;
  draft_id: DraftId;
  finding_ids: FindingIds;
  rule_version: RuleVersion;
  decision: Decision;
  rationale: Rationale;
  decided_at: DecidedAt;
}
export interface AdminAccessChangeV1 {
  schema_version?: SchemaVersion4;
  permission_group: PermissionGroup;
  enabled?: Enabled;
}
export interface AdminBootstrapV1 {
  schema_version?: SchemaVersion5;
  email: Email1;
  password: Password1;
  bootstrap_token: BootstrapToken;
}
export interface AdminChallengeV1 {
  schema_version?: SchemaVersion6;
  challenge_token: ChallengeToken;
  stage: Stage;
  expires_in?: ExpiresIn;
  secret?: Secret;
  provisioning_uri?: ProvisioningUri;
}
export interface AdminCreateV1 {
  schema_version?: SchemaVersion7;
  email: Email2;
  password: Password2;
  permission_group: PermissionGroup1;
}
export interface AdminSecondFactorV1 {
  schema_version?: SchemaVersion8;
  challenge_token: ChallengeToken1;
  code: Code;
}
export interface AdminSessionV1 {
  schema_version?: SchemaVersion9;
  access_token: AccessToken1;
  expires_at: ExpiresAt1;
  identity: AccountIdentityV1;
  recovery_codes?: RecoveryCodes;
}
export interface AdminStepUpV1 {
  schema_version?: SchemaVersion10;
  code: Code1;
}
export interface AnalogyAssessmentV1 {
  schema_version?: SchemaVersion11;
  case_id: CaseId;
  mechanism_overlap: MechanismOverlap;
  similarities: Similarities;
  key_differences: KeyDifferences;
  non_transferable: NonTransferable;
  known_outcomes: KnownOutcomes;
  limitations: Limitations;
}
export interface HistoricalEventImportV1 {
  schema_version?: SchemaVersion12;
  text: Text;
  known_at: KnownAt;
  source_version_id: SourceVersionId;
  data_role: DataRole;
  outcome_category?: OutcomeCategory;
}
export interface AuthAccessEventViewV1 {
  schema_version?: SchemaVersion13;
  id: Id;
  user_id: UserId1;
  request_id: RequestId;
  action: Action;
  outcome: Outcome;
  reason: Reason;
  fingerprint: Fingerprint;
  fingerprint_kind: FingerprintKind;
  peer_ip: PeerIp;
  device: Device;
  user_agent: UserAgent;
  accept_language: AcceptLanguage;
  created_at: CreatedAt;
}
export interface AuthConfigurationV1 {
  schema_version?: SchemaVersion14;
  email_code_length?: EmailCodeLength;
  email_transport: EmailTransport;
  turnstile_enabled: TurnstileEnabled;
  turnstile_site_key: TurnstileSiteKey;
  demo_admin_enabled: DemoAdminEnabled;
}
export interface BaselineV1 {
  schema_version?: SchemaVersion15;
  method: Method;
  sample_count: SampleCount;
  observation_ids: ObservationIds;
  last_observed_value?: LastObservedValue;
  projected_value?: ProjectedValue;
  unit?: Unit;
  limitations: Limitations1;
}
export interface BillingPlanV1 {
  schema_version?: SchemaVersion16;
  code: Code2;
  name: Name;
  amount_minor: AmountMinor;
  currency?: Currency;
  units: Units;
  valid_days: ValidDays;
  recurring: Recurring;
  cadence_days?: CadenceDays;
  label?: Label;
}
export interface BounceEventV1 {
  schema_version?: SchemaVersion17;
  event_id: EventId;
  delivery_id: DeliveryId;
  kind: Kind;
}
export interface ChangeAssertionV1 {
  schema_version?: SchemaVersion18;
  kind: Kind1;
  claim_ids: ClaimIds;
  prior_claim_id?: PriorClaimId;
  verification_note: VerificationNote;
}
export interface ChatResearchStageViewV1 {
  schema_version?: SchemaVersion19;
  stage: Stage1;
  started_at: StartedAt;
}
export interface ChatResearchStartV1 {
  schema_version?: SchemaVersion20;
  client_id: ClientId;
  industry_id: IndustryId;
  horizon_days?: HorizonDays;
  confirm_demo: ConfirmDemo;
}
export interface ChatResearchViewV1 {
  schema_version?: SchemaVersion21;
  id: Id1;
  industry: Industry;
  horizon_days: HorizonDays1;
  status: JobStatus;
  stages: Stages;
  error_code: ErrorCode;
  created_at: CreatedAt1;
  result?: IndustryResearchRunV1 | null;
}
export interface IndustryResearchRunV1 {
  schema_version?: SchemaVersion22;
  scope: IndustryResearchScopeV1;
  as_of: AsOf;
  status: Status;
  searched: Searched;
  sources: Sources;
  evidence: Evidence;
  analogy_chains?: AnalogyChains;
  gaps: Gaps;
  report?: IndustryReportDraftV1 | null;
  personal_actions?: PersonalActions;
  fetch_calls: FetchCalls;
  model_calls: ModelCalls;
  provider_failures: ProviderFailures;
}
export interface IndustryResearchScopeV1 {
  schema_version?: SchemaVersion23;
  industry: Industry1;
  region?: Region;
  horizon_days?: HorizonDays2;
  label?: Label1;
}
export interface IndustrySearchQueryV1 {
  schema_version?: SchemaVersion24;
  lane: Lane;
  query: Query;
}
export interface IndustrySourceExcerptV1 {
  schema_version?: SchemaVersion25;
  source_id: SourceId;
  url: Url;
  title: Title;
  published_at: PublishedAt;
  retrieved_at: RetrievedAt;
  content_hash: ContentHash;
  excerpt: Excerpt;
}
export interface IndustryEvidenceV1 {
  schema_version?: SchemaVersion26;
  source_id: SourceId1;
  kind: Kind2;
  quote: Quote;
  interpretation: Interpretation;
  comparable_conditions?: ComparableConditions;
  key_difference?: KeyDifference;
  indicator_name?: IndicatorName;
  indicator_period?: IndicatorPeriod;
  indicator_value?: IndicatorValue;
}
export interface IndustryAnalogyChainV1 {
  schema_version?: SchemaVersion27;
  case_id: CaseId1;
  industry: Industry2;
  context: Context;
  milestones: Milestones;
  mechanism: Mechanism;
  comparable_conditions: ComparableConditions1;
  key_difference: KeyDifference1;
}
export interface IndustryAnalogyMilestoneV1 {
  schema_version?: SchemaVersion28;
  period: Period;
  observed_change: ObservedChange;
  source_id: SourceId2;
  quote: Quote1;
}
export interface IndustryReportDraftV1 {
  schema_version?: SchemaVersion29;
  forecasts: Forecasts;
  actions: Actions;
}
export interface IndustryForecastDraftV1 {
  schema_version?: SchemaVersion30;
  statement: Statement;
  mechanism: Mechanism1;
  expected_signal: ExpectedSignal;
  falsifier: Falsifier;
  uncertainty: Uncertainty;
  alternatives: Alternatives;
  supporting_source_ids: SupportingSourceIds;
  counter_source_ids?: CounterSourceIds;
  basis?: Basis;
  analogy_case_ids?: AnalogyCaseIds;
}
export interface IndustryActionDraftV1 {
  schema_version?: SchemaVersion31;
  forecast_index: ForecastIndex;
  domain: Domain;
  action: Action1;
  trigger: Trigger;
  check_after_days: CheckAfterDays;
  time_minutes: TimeMinutes;
  success_check: SuccessCheck;
  stop_condition: StopCondition;
}
export interface CheckoutRequestV1 {
  schema_version?: SchemaVersion32;
  plan_code: PlanCode;
  explicit_sandbox_consent: ExplicitSandboxConsent;
}
export interface ClaimImportV1 {
  schema_version?: SchemaVersion33;
  claim_text: ClaimText;
  quote: Quote2;
  source_locator: SourceLocator;
  relation: Relation;
  claim_kind: ClaimKind;
  verification_status?: VerificationStatus;
  verification_note?: VerificationNote1;
  scope: Scope;
  caveat?: Caveat;
}
export interface CommunityActivityV1 {
  schema_version?: SchemaVersion34;
  id: Id2;
  publication_id: PublicationId;
  kind: Kind3;
  title: Title1;
  summary: Summary;
  created_at: CreatedAt2;
  read: Read;
}
export interface CommunityIndustryInputV1 {
  schema_version?: SchemaVersion35;
  name: Name1;
  description: Description;
  domain: Domain1;
}
export interface CommunityIndustryViewV1 {
  schema_version?: SchemaVersion36;
  id: Id3;
  name: Name2;
  description: Description1;
  domain: Domain2;
  public: Public;
  owned?: Owned;
  added?: Added;
  personal_industry_id?: PersonalIndustryId;
  source_industry_id?: SourceIndustryId;
}
export interface CommunityPublishV1 {
  schema_version?: SchemaVersion37;
  industry_id: IndustryId1;
  report_version_id: ReportVersionId;
  confirm_public: ConfirmPublic;
}
export interface CommunityReadInputV1 {
  schema_version?: SchemaVersion38;
  visitor_id: VisitorId;
}
export interface CommunityReportViewV1 {
  schema_version?: SchemaVersion39;
  id: Id4;
  industry_id: IndustryId2;
  industry_name: IndustryName;
  title: Title2;
  summary: Summary1;
  label: Label2;
  sample: Sample;
  image: Image;
  sections: Sections;
  created_at: CreatedAt3;
  author: Author;
  reason?: Reason1;
  views_count?: ViewsCount;
  likes_count?: LikesCount;
  bookmarks_count?: BookmarksCount;
  liked?: Liked;
  saved?: Saved;
  saved_industry_id?: SavedIndustryId;
  owned?: Owned1;
  public?: Public1;
}
export interface CommunitySectionV1 {
  schema_version?: SchemaVersion40;
  heading: Heading;
  text: Text1;
}
export interface CommunitySaveReportV1 {
  schema_version?: SchemaVersion41;
  industry_id: IndustryId3;
}
export interface CommunityVisibilityV1 {
  schema_version?: SchemaVersion42;
  public: Public2;
}
export interface ConsumerPreferenceV1 {
  schema_version?: SchemaVersion43;
  theme?: Theme;
}
export interface ConversationCapabilitiesV1 {
  schema_version?: SchemaVersion44;
  model_available: ModelAvailable;
}
export interface ConversationCreateV1 {
  schema_version?: SchemaVersion45;
  industry_id?: IndustryId4;
  question: Question;
  client_id: ClientId1;
  use_model?: UseModel;
  include_memory?: IncludeMemory;
}
export interface ConversationIndustryProposalV1 {
  schema_version?: SchemaVersion46;
  id: Id5;
  name: Name3;
  status: Status1;
  industry_id?: IndustryId5;
}
export interface ConversationMessageV1 {
  schema_version?: SchemaVersion47;
  text: Text2;
  client_id: ClientId2;
  use_model?: UseModel1;
  include_memory?: IncludeMemory1;
}
export interface ConversationMessageViewV1 {
  schema_version?: SchemaVersion48;
  role: Role1;
  text: Text3;
  client_id?: ClientId3;
  source?: Source;
  proposal?: ConversationIndustryProposalV1 | null;
}
export interface ConversationStartV1 {
  schema_version?: SchemaVersion49;
  confirm_demo_reuse: ConfirmDemoReuse;
}
export interface ConversationViewV1 {
  schema_version?: SchemaVersion50;
  id: Id6;
  industry_id: IndustryId6;
  title: Title3;
  created_at: CreatedAt4;
  messages: Messages;
  job_id: JobId;
  job_status: JobStatus | null;
  error_code: ErrorCode1;
  report_id: ReportId;
  mode?: Mode;
  new_forecast_rules_pending?: NewForecastRulesPending;
}
export interface CountryCatalogV1 {
  schema_version?: SchemaVersion51;
  entries: Entries;
  source?: Source1;
}
export interface CountryOptionV1 {
  schema_version?: SchemaVersion52;
  code: Code3;
  label: Label3;
}
export interface CriticFindingV1 {
  schema_version?: SchemaVersion53;
  finding_id: FindingId;
  draft_id: DraftId1;
  category: Category;
  severity: Severity;
  statement: Statement1;
  verified_source_refs: VerifiedSourceRefs;
  verification_status: VerificationStatus1;
  scope: Scope1;
  affected_assumption_ids: AffectedAssumptionIds;
  recommended_action: RecommendedAction;
}
export interface CriticReportV1 {
  schema_version?: SchemaVersion54;
  critic_run_id: CriticRunId;
  draft_id: DraftId2;
  draft_hash: DraftHash;
  independent_input_hash: IndependentInputHash;
  findings: Findings;
  checkers_completed: CheckersCompleted;
  rules_version?: RulesVersion;
  duration_ms: DurationMs;
  model_calls?: ModelCalls1;
  limitations: Limitations2;
}
export interface ReviewFindingV1 {
  schema_version?: SchemaVersion55;
  finding_id: FindingId1;
  checker: Checker;
  code: Code4;
  severity: Severity1;
  statement: Statement2;
  verification_status: VerificationStatus2;
  source_refs?: SourceRefs;
  affected_fields: AffectedFields;
  recommended_action: RecommendedAction1;
}
export interface CurrentPasswordV1 {
  schema_version?: SchemaVersion56;
  password: Password3;
}
export interface DecisionValueV1 {
  schema_version?: SchemaVersion57;
  impact_id: ImpactId;
  relevance: Relevance;
  impact_window: ImpactWindow;
  actionability: Actionability;
  reversibility: Reversibility;
  cost_note: CostNote;
  decision_priority: DecisionPriority;
  reasons: Reasons;
  unknowns: Unknowns;
  reevaluate_if: ReevaluateIf;
}
export interface DemoResearchInputV1 {
  schema_version?: SchemaVersion58;
  question: Question1;
}
export interface DemoResearchResultV1 {
  schema_version?: SchemaVersion59;
  label?: Label4;
  kind?: Kind4;
  statement: Statement3;
  research_as_of: ResearchAsOf;
  source_ids: SourceIds;
  limitations: Limitations3;
  model_id?: ModelId;
  prompt_hash: PromptHash;
  cost_units?: CostUnits;
}
export interface EmailAuthorizationV1 {
  schema_version?: SchemaVersion60;
  explicit_consent: ExplicitConsent;
  recipient: Recipient;
}
export interface EmailCodeRequestV1 {
  schema_version?: SchemaVersion61;
  email: Email3;
  purpose: Purpose;
  human_token?: HumanToken;
}
export interface EmailCodeSentV1 {
  schema_version?: SchemaVersion62;
  challenge_id: ChallengeId;
  expires_in?: ExpiresIn1;
  resend_after?: ResendAfter;
  delivery_mode: DeliveryMode;
}
export interface EmailPreviewV1 {
  schema_version?: SchemaVersion63;
  report_version_id: ReportVersionId1;
  recipient_masked: RecipientMasked;
  subject: Subject;
  summary: Summary2;
  private_link: PrivateLink;
  transport?: Transport;
  external_delivery?: ExternalDelivery;
}
export interface EmailQueueRequestV1 {
  schema_version?: SchemaVersion64;
  purpose?: Purpose1;
  explicit_consent: ExplicitConsent1;
}
export interface EntitlementV1 {
  schema_version?: SchemaVersion65;
  user_id: UserId2;
  subscription_status: SubscriptionStatus;
  paid_periodic_research_enabled: PaidPeriodicResearchEnabled;
  email_digest_opt_in?: EmailDigestOptIn;
  email_alert_opt_in?: EmailAlertOptIn;
}
export interface ErrorV1 {
  schema_version?: SchemaVersion66;
  code: Code5;
  message: Message;
  request_id: RequestId1;
  details?: Details;
}
export interface Details {
  [k: string]: boolean | string | number;
}
export interface EvaluationProtocolV1 {
  schema_version?: SchemaVersion67;
  protocol_id: ProtocolId;
  version_id: VersionId;
  mode: Mode1;
  label: Label5;
  registered_at: RegisteredAt;
  as_of: AsOf1;
  due_at: DueAt;
  metric_definition: MetricDefinition;
  geography: Geography;
  unit: Unit1;
  resolution_source: ResolutionSource;
  operator: Operator;
  threshold: Threshold;
  point_prediction_a?: PointPredictionA;
  point_prediction_b?: PointPredictionB;
  baseline_value?: BaselineValue;
  source_snapshot_hash: SourceSnapshotHash;
  model_id: ModelId1;
  prompt_hash: PromptHash1;
  testset_version: TestsetVersion;
  protocol_version?: ProtocolVersion;
  limitations: Limitations4;
}
export interface EvaluationRegisterV1 {
  schema_version?: SchemaVersion68;
  mode: Mode2;
  operator: Operator1;
  threshold: Threshold1;
  unit: Unit2;
  testset_version?: TestsetVersion1;
}
export interface EvidenceClaimV1 {
  schema_version?: SchemaVersion69;
  claim_id: ClaimId;
  source_version_id: SourceVersionId1;
  source_group_id: SourceGroupId;
  claim_text: ClaimText1;
  quote: Quote3;
  source_locator: SourceLocator1;
  relation: Relation1;
  claim_kind: ClaimKind1;
  known_at: KnownAt1;
  verification_status: VerificationStatus3;
  verification_note: VerificationNote2;
  scope: Scope2;
  caveat: Caveat1;
  label: Label6;
}
export interface EvidenceDeltaV1 {
  schema_version?: SchemaVersion70;
  added_claim_ids: AddedClaimIds;
  independent_groups: IndependentGroups;
  duplicate_claim_ids: DuplicateClaimIds;
  changed_observation_ids: ChangedObservationIds;
  reasons: Reasons1;
  fingerprint: Fingerprint1;
}
/**
 * Untrusted Markdown; fetch time is never a substitute for publication time.
 */
export interface FetchedPageV1 {
  schema_version?: SchemaVersion71;
  provider: Provider;
  url: Url1;
  title: Title4;
  content: Content;
  content_hash: ContentHash1;
  retrieved_at: RetrievedAt1;
  published_at?: PublishedAt1;
  evidence_status?: EvidenceStatus;
  label: Label7;
}
export interface FirstReportRequestV1 {
  schema_version?: SchemaVersion72;
  label?: Label8;
  forecast_version_ids?: ForecastVersionIds;
}
export interface ForecastDraftV1 {
  schema_version?: SchemaVersion73;
  draft_id: DraftId3;
  run_id: RunId;
  draft_sequence: DraftSequence;
  kind: Kind5;
  statement: Statement4;
  research_as_of: ResearchAsOf1;
  target?: ForecastTargetV1 | null;
  evidence_claim_ids: EvidenceClaimIds;
  inputs_hash: InputsHash;
  model_version: ModelVersion;
}
export interface ForecastTargetV1 {
  schema_version?: SchemaVersion74;
  target_type: TargetType;
  population_scope: PopulationScope;
  geography: Geography1;
  metric_definition: MetricDefinition1;
  direction_or_threshold: DirectionOrThreshold;
  baseline: Baseline;
  target_start_at: TargetStartAt;
  target_end_at: TargetEndAt;
  resolution_source: ResolutionSource1;
  resolution_rule: ResolutionRule;
}
export interface ForecastResolutionV1 {
  schema_version?: SchemaVersion75;
  resolution_id: ResolutionId;
  protocol_id: ProtocolId1;
  status: Status2;
  checked_at: CheckedAt;
  observation_id?: ObservationId;
  observed_value?: ObservedValue;
  forecast_absolute_error_a?: ForecastAbsoluteErrorA;
  forecast_absolute_error_b?: ForecastAbsoluteErrorB;
  baseline_absolute_error?: BaselineAbsoluteError;
  reason: Reason2;
}
export interface ForecastVersionV1 {
  schema_version?: SchemaVersion76;
  forecast_version_id: ForecastVersionId;
  forecast_id: ForecastId;
  research_run_id: ResearchRunId;
  version_num: VersionNum;
  kind?: Kind6;
  statement: Statement5;
  target: ForecastTargetV1;
  research_as_of: ResearchAsOf2;
  forecast_published_at: ForecastPublishedAt;
  evidence_claim_ids: EvidenceClaimIds1;
  contradiction_claim_ids: ContradictionClaimIds;
  mechanism_ids: MechanismIds;
  historical_case_ids: HistoricalCaseIds;
  assumptions: Assumptions;
  falsification_conditions: FalsificationConditions;
  scenario_ids: ScenarioIds;
  uncertainty_state?: UncertaintyState;
  next_review_at: NextReviewAt;
  evidence_snapshot_hash: EvidenceSnapshotHash;
  change_reason: ChangeReason;
}
export interface FreeReportEntitlementV1 {
  schema_version?: SchemaVersion77;
  total?: Total;
  available: Available;
  reserved: Reserved;
  consumed: Consumed;
  paid_research_enabled?: PaidResearchEnabled;
}
export interface HistoricalCaseImportV1 {
  schema_version?: SchemaVersion78;
  title: Title5;
  cutoff_at: CutoffAt;
  domain_tags: DomainTags;
  mechanism_tags: MechanismTags;
  initial_conditions: InitialConditions;
  limitations: Limitations5;
  events: Events;
  label: Label9;
}
export interface HistoricalCaseViewV1 {
  schema_version?: SchemaVersion79;
  case_id: CaseId2;
  title: Title6;
  cutoff_at: CutoffAt1;
  as_of: AsOf2;
  domain_tags: DomainTags1;
  mechanism_tags: MechanismTags1;
  initial_conditions: InitialConditions1;
  limitations: Limitations6;
  contemporaneous: Contemporaneous;
  outcomes: Outcomes;
  label: Label10;
}
export interface InAppNotificationV1 {
  schema_version?: SchemaVersion80;
  notification_id: NotificationId;
  report_id: ReportId1;
  report_version_id: ReportVersionId2;
  title: Title7;
  summary: Summary3;
  created_at: CreatedAt5;
  read: Read1;
}
export interface IndicatorDefinitionV1 {
  schema_version?: SchemaVersion81;
  code: Code6;
  name: Name4;
  provider: Provider1;
  geo_scope: GeoScope;
  unit: Unit3;
  frequency: Frequency;
  definition_version: DefinitionVersion;
  label: Label11;
  indicator_id: IndicatorId;
}
export interface IndicatorImportV1 {
  schema_version?: SchemaVersion82;
  code: Code7;
  name: Name5;
  provider: Provider2;
  geo_scope: GeoScope1;
  unit: Unit4;
  frequency: Frequency1;
  definition_version: DefinitionVersion1;
  label: Label12;
}
export interface IndicatorObservationVintageV1 {
  schema_version?: SchemaVersion83;
  indicator_id: IndicatorId1;
  period_start: PeriodStart;
  period_end: PeriodEnd;
  value: Value;
  published_at: PublishedAt2;
  available_at: AvailableAt;
  vintage: Vintage;
  quality_flag: QualityFlag;
}
export interface IndustryCoverageReviewV1 {
  schema_version?: SchemaVersion84;
  sufficient: Sufficient;
  gaps: Gaps1;
  queries: Queries;
}
export interface IndustryEvidenceReviewV1 {
  schema_version?: SchemaVersion85;
  sufficient: Sufficient1;
  gaps: Gaps2;
  queries: Queries1;
  evidence: Evidence1;
  analogy_chains?: AnalogyChains1;
}
export interface IndustryTrackingV1 {
  schema_version?: SchemaVersion86;
  monitor_enabled?: MonitorEnabled;
  prediction_enabled?: PredictionEnabled;
  email_enabled?: EmailEnabled;
}
export interface IndustryTrackingViewV1 {
  schema_version?: SchemaVersion87;
  monitor_enabled?: MonitorEnabled1;
  prediction_enabled?: PredictionEnabled1;
  email_enabled?: EmailEnabled1;
  industry_id: IndustryId7;
  status: Status3;
}
export interface JobAcceptedV1 {
  schema_version?: SchemaVersion88;
  job_id: JobId1;
  request_id: RequestId2;
}
export interface JobV1 {
  schema_version?: SchemaVersion89;
  job_id: JobId2;
  request_id: RequestId3;
  trace_id: TraceId;
  status: JobStatus;
  attempts: Attempts;
  label?: Label13;
  result?: Result;
  error_code?: ErrorCode2;
}
export interface M2ResearchResultV1 {
  schema_version?: SchemaVersion90;
  run_id: RunId1;
  draft_id: DraftId4;
  status?: Status4;
  label: Label14;
  kind: Kind7;
  publication_allowed?: PublicationAllowed;
  input_hash: InputHash;
  draft_hash: DraftHash1;
}
export interface UserReportResultV1 {
  schema_version?: SchemaVersion91;
  report_id: ReportId2;
  report_version_id: ReportVersionId3;
  label: Label15;
  status?: Status5;
}
export interface MonitorResultV1 {
  schema_version?: SchemaVersion92;
  monitor_run_id: MonitorRunId;
  forecast_id: ForecastId1;
  old_version_id: OldVersionId;
  new_version_id?: NewVersionId;
  level: Level;
  outcome: Outcome1;
  reason: Reason3;
  changed_fields: ChangedFields;
  refreshed_reports: RefreshedReports;
  external_model_calls?: ExternalModelCalls;
}
export interface MailDeliveryResultV1 {
  schema_version?: SchemaVersion93;
  delivery_id: DeliveryId1;
  status: Status6;
  external_delivery?: ExternalDelivery1;
}
export interface LocalDeliveryV1 {
  schema_version?: SchemaVersion94;
  delivery_id: DeliveryId2;
  report_version_id: ReportVersionId4;
  status?: Status7;
  external_delivery?: ExternalDelivery2;
  consented_at: ConsentedAt;
}
export interface LoginSessionViewV1 {
  schema_version?: SchemaVersion95;
  session_id: SessionId;
  kind: Kind8;
  device_label: DeviceLabel;
  created_at: CreatedAt6;
  expires_at: ExpiresAt2;
  current: Current;
}
export interface M2DraftV1 {
  schema_version?: SchemaVersion96;
  parent_version_id?: ParentVersionId;
  draft_id: DraftId5;
  run_id: RunId2;
  draft_sequence?: DraftSequence1;
  status?: Status8;
  publication_allowed?: PublicationAllowed1;
  label: Label16;
  kind: Kind9;
  statement: Statement6;
  research_as_of: ResearchAsOf3;
  lifecycle_stage: LifecycleStage;
  target: ForecastTargetV1 | null;
  evidence_claim_ids: EvidenceClaimIds2;
  contradiction_claim_ids: ContradictionClaimIds1;
  fusions: Fusions;
  mechanism_chain: MechanismChain;
  analogies: Analogies;
  scenarios: Scenarios;
  baseline: BaselineV1;
  raw_narrative: ResearchNarrativeV1;
  assumptions: Assumptions1;
  falsification_conditions: FalsificationConditions3;
  uncertainty_state?: UncertaintyState1;
  next_review_at: NextReviewAt1;
  limitations: Limitations7;
  downgrade_reasons: DowngradeReasons;
  input_hash: InputHash1;
  prompt_hash: PromptHash2;
  model_id: ModelId2;
  rules_version?: RulesVersion1;
}
export interface SignalFusionV1 {
  schema_version?: SchemaVersion97;
  fusion_id: FusionId;
  signal_ids: SignalIds;
  independent_source_groups: IndependentSourceGroups;
  mechanism: Mechanism2;
  remaining_bottlenecks: RemainingBottlenecks;
  emergent_hypotheses: EmergentHypotheses;
  opposing_explanations: OpposingExplanations;
  next_observable_signals: NextObservableSignals;
  stage: LifecycleStage;
  status?: Status9;
}
export interface MechanismEdgeV1 {
  schema_version?: SchemaVersion98;
  from_node: FromNode;
  to_node: ToNode;
  relationship: Relationship;
  sign: Sign;
  lag_range: LagRange;
  conditions: Conditions;
  evidence_claim_ids: EvidenceClaimIds3;
  uncertainty: Uncertainty1;
}
export interface ScenarioV1 {
  schema_version?: SchemaVersion99;
  scenario_id: ScenarioId;
  kind?: Kind10;
  path: Path;
  statement: Statement7;
  conditions: Conditions1;
  observable_signals: ObservableSignals;
  falsification_conditions: FalsificationConditions1;
}
export interface ResearchNarrativeV1 {
  schema_version?: SchemaVersion100;
  hypothesis: Hypothesis;
  enabling_conditions: EnablingConditions;
  bottlenecks: Bottlenecks;
  opposing_explanations: OpposingExplanations1;
  next_observable_signals: NextObservableSignals1;
  falsification_conditions: FalsificationConditions2;
  cited_claim_ids: CitedClaimIds;
}
export interface MonitorCheckRequestV1 {
  schema_version?: SchemaVersion101;
  assertions?: Assertions;
}
export interface MonitorPolicyV1 {
  schema_version?: SchemaVersion102;
  enabled?: Enabled1;
  interval_seconds?: IntervalSeconds;
  cooldown_seconds?: CooldownSeconds;
  max_daily_jobs?: MaxDailyJobs;
  independent_groups_required?: IndependentGroupsRequired;
  indicator_absolute_delta?: IndicatorAbsoluteDelta;
  consecutive_periods?: ConsecutivePeriods;
}
export interface NotificationEligibilityV1 {
  schema_version?: SchemaVersion103;
  user_id: UserId3;
  report_version_id: ReportVersionId5;
  channel: Channel;
  reason: Reason4;
  consent_snapshot_ref?: ConsentSnapshotRef;
  dedupe_key: DedupeKey;
  eligible: Eligible;
}
export interface NotificationPreferencesV1 {
  schema_version?: SchemaVersion104;
  first_report_opt_in?: FirstReportOptIn;
  alert_opt_in?: AlertOptIn;
  digest_opt_in?: DigestOptIn;
  frequency?: Frequency2;
  explicit_consent?: ExplicitConsent2;
}
export interface ObservationImportV1 {
  schema_version?: SchemaVersion105;
  source_version_id: SourceVersionId2;
  period_start: PeriodStart1;
  period_end: PeriodEnd1;
  value: Value1;
  published_at: PublishedAt3;
  available_at: AvailableAt1;
  revision_number: RevisionNumber;
  quality_flag: QualityFlag1;
  definition_note: DefinitionNote;
}
export interface ObservationV1 {
  schema_version?: SchemaVersion106;
  source_version_id: SourceVersionId3;
  period_start: PeriodStart2;
  period_end: PeriodEnd2;
  value: Value2;
  published_at: PublishedAt4;
  available_at: AvailableAt2;
  revision_number: RevisionNumber1;
  quality_flag: QualityFlag2;
  definition_note: DefinitionNote1;
  observation_id: ObservationId1;
  indicator_id: IndicatorId2;
  label: Label17;
}
export interface PaidResearchAcceptedV1 {
  schema_version?: SchemaVersion107;
  action: Action2;
  job_id?: JobId3;
  report_id?: ReportId3;
  user_topic_id?: UserTopicId;
  reserved_units: ReservedUnits;
  deduplicated?: Deduplicated;
}
export interface PaidResearchSubmitV1 {
  schema_version?: SchemaVersion108;
  quote_id: QuoteId;
  accept_usage_rules: AcceptUsageRules;
}
export interface PasswordResetV1 {
  schema_version?: SchemaVersion109;
  email: Email4;
  password: Password4;
  verification_id: VerificationId;
  code: Code8;
}
export interface PaymentEventV1 {
  schema_version?: SchemaVersion110;
  provider?: Provider3;
  label?: Label18;
  event_id: EventId1;
  checkout_id: CheckoutId;
  provider_reference: ProviderReference;
  event_type: EventType;
  amount_minor: AmountMinor1;
  currency: Currency1;
  occurred_at: OccurredAt;
}
export interface PeriodicResearchRequestV1 {
  schema_version?: SchemaVersion111;
  subscription_id: SubscriptionId;
  explicit_periodic_consent: ExplicitPeriodicConsent;
}
export interface PersonalAssessmentV1 {
  schema_version?: SchemaVersion112;
  impact_id: ImpactId1;
  user_id: UserId4;
  profile_snapshot_id: ProfileSnapshotId;
  forecast_version_id: ForecastVersionId1;
  relevance: Relevance1;
  mechanism_path: MechanismPath;
  relevance_reason: RelevanceReason;
  positive_impacts: PositiveImpacts;
  negative_impacts: NegativeImpacts;
  applicable_conditions: ApplicableConditions;
  uncertainty: Uncertainty2;
  matched_domains: MatchedDomains;
  decision: DecisionValueV1;
}
export interface PersonalDataEraseV1 {
  schema_version?: SchemaVersion113;
  password: Password5;
  confirmation: Confirmation;
}
export interface PersonalDataErasedV1 {
  schema_version?: SchemaVersion114;
  erasure_id: ErasureId;
  erased_at: ErasedAt;
  cleared_records: ClearedRecords;
  retained: Retained;
  backup_notice: BackupNotice;
}
export interface ClearedRecords {
  [k: string]: number;
}
export interface PersonalImpactV1 {
  schema_version?: SchemaVersion115;
  impact_id: ImpactId2;
  user_id: UserId5;
  profile_snapshot_id: ProfileSnapshotId1;
  forecast_version_id: ForecastVersionId2;
  affected_area: AffectedArea;
  mechanism_path: MechanismPath1;
  relevance_reason: RelevanceReason1;
  positive_impacts: PositiveImpacts1;
  negative_impacts: NegativeImpacts1;
  time_horizon: TimeHorizon;
  applicable_conditions: ApplicableConditions1;
  uncertainty: Uncertainty3;
  updated_at: UpdatedAt;
}
export interface PredictionRequestV1 {
  schema_version?: SchemaVersion116;
  request_id: RequestId4;
  user_id: UserId6;
  topic_id: TopicId;
  profile_snapshot_id: ProfileSnapshotId2;
  entitlement_reservation_id?: EntitlementReservationId;
  request_kind: RequestKind;
  idempotency_key: IdempotencyKey;
}
export interface PrivateReportV1 {
  schema_version?: SchemaVersion117;
  report_id: ReportId4;
  report_version_id: ReportVersionId6;
  user_id: UserId7;
  version_num: VersionNum1;
  profile_snapshot_id: ProfileSnapshotId3;
  profile_revision: ProfileRevision;
  label: Label19;
  title: Title8;
  created_at: CreatedAt7;
  forecast_version_ids: ForecastVersionIds1;
  primary_impacts: PrimaryImpacts;
  observation_only: ObservationOnly;
  recommendations: Recommendations;
  evidence_gaps: EvidenceGaps;
  limitations: Limitations8;
  algorithm_version?: AlgorithmVersion;
  previous_report_version_id?: PreviousReportVersionId;
  change_summary?: ChangeSummary;
}
export interface RecommendationV1 {
  schema_version?: SchemaVersion118;
  recommendation_id: RecommendationId;
  impact_id: ImpactId3;
  action: Action3;
  rationale: Rationale1;
  forecast_version_ids: ForecastVersionIds2;
  applicability: Applicability;
  suggested_start: SuggestedStart;
  review_date: ReviewDate;
  estimated_effort_and_cost: EstimatedEffortAndCost;
  tradeoffs: Tradeoffs;
  alternatives: Alternatives1;
  success_metrics: SuccessMetrics;
  stop_or_revisit_condition: StopOrRevisitCondition;
  priority: Priority;
  personalization_assumptions: PersonalizationAssumptions;
  suppressed_high_risk_actions: SuppressedHighRiskActions;
}
export interface ProfileInputV1 {
  schema_version?: SchemaVersion119;
  industry_l1_code: IndustryL1Code;
  industry_l2_code: IndustryL2Code;
  industry_detail?: IndustryDetail;
  occupation_text?: OccupationText;
  country_code?: CountryCode;
  subdivision?: Subdivision;
  gender?: Gender;
  age?: Age;
  region?: Region1;
  goals?: Goals;
  tasks?: Tasks;
  available_minutes_per_week?: AvailableMinutesPerWeek;
  allow_low_cost_experiments?: AllowLowCostExperiments;
  use_optional_fields?: UseOptionalFields;
  locale?: Locale;
  timezone?: Timezone;
}
export interface ProfileSnapshotV1 {
  schema_version?: SchemaVersion120;
  snapshot_id: SnapshotId;
  user_id: UserId8;
  profile: ProfileInputV1;
  profile_revision: ProfileRevision1;
  consent_scope: ConsentScope;
  created_at: CreatedAt8;
  snapshot_hash: SnapshotHash;
}
export interface ProfileViewV1 {
  schema_version?: SchemaVersion121;
  user_id: UserId9;
  profile: ProfileInputV1;
  revision: Revision;
  updated_at: UpdatedAt1;
  taxonomy_version: TaxonomyVersion;
}
export interface ProtectedLoginV1 {
  schema_version?: SchemaVersion122;
  email: Email5;
  password: Password6;
  human_token?: HumanToken1;
}
export interface PublishRequestV1 {
  schema_version?: SchemaVersion123;
  review_id: ReviewId;
  change_reason: ChangeReason1;
}
export interface PublishedForecastV1 {
  schema_version?: SchemaVersion124;
  version_id: VersionId1;
  forecast_id: ForecastId2;
  version_num: VersionNum2;
  draft_id: DraftId6;
  review_id: ReviewId1;
  label: Label20;
  published_at: PublishedAt5;
  version_hash: VersionHash;
  change_reason: ChangeReason2;
  body: M2DraftV1;
}
export interface RecommendationFeedbackV1 {
  schema_version?: SchemaVersion125;
  status: Status10;
}
export interface ReplayResultV1 {
  schema_version?: SchemaVersion126;
  run_id: RunId3;
  identical: Identical;
  input_hash: InputHash2;
  original_draft_hash: OriginalDraftHash;
  replay_draft_hash: ReplayDraftHash;
  network_calls?: NetworkCalls;
}
export interface ReportSummaryV1 {
  schema_version?: SchemaVersion127;
  report_id: ReportId5;
  report_version_id: ReportVersionId7;
  version_num: VersionNum3;
  title: Title9;
  label: Label21;
  created_at: CreatedAt9;
}
export interface ResearchAcceptedV1 {
  schema_version?: SchemaVersion128;
  job_id: JobId4;
  request_id: RequestId5;
  run_id: RunId4;
}
export interface ResearchIntakeResultV1 {
  schema_version?: SchemaVersion129;
  scope: Scope3;
  matched_version_ids: MatchedVersionIds;
  available_free_reports: AvailableFreeReports;
  additional_questions: AdditionalQuestions;
  limitations: Limitations9;
}
export interface ResearchIntakeV1 {
  schema_version?: SchemaVersion130;
  question?: Question2;
  label?: Label22;
}
export interface ResearchQuoteV1 {
  schema_version?: SchemaVersion131;
  quote_id: QuoteId1;
  scope: ResearchScopeV1;
  scope_fingerprint: ScopeFingerprint;
  kind: Kind11;
  units_required: UnitsRequired;
  existing_report_id: ExistingReportId;
  expires_at: ExpiresAt3;
  rules: Rules;
}
export interface ResearchScopeV1 {
  schema_version?: SchemaVersion132;
  domain: Domain3;
  focus: Focus;
  population: Population;
  geography?: Geography2;
  label?: Label23;
}
export interface ResearchRunViewV1 {
  schema_version?: SchemaVersion133;
  run_id: RunId5;
  topic_id: TopicId1;
  job_id: JobId5;
  title: Title10;
  status: JobStatus;
  research_as_of: ResearchAsOf4;
  input_hash: InputHash3;
  engine_code_hash: EngineCodeHash;
  provider: Provider4;
  model_id: ModelId3;
  label: Label24;
  draft: M2DraftV1 | null;
  draft_hash: DraftHash2;
  error_code: ErrorCode3;
}
export interface ResearchSnapshotV1 {
  schema_version?: SchemaVersion134;
  request: ResearchSubmitV1;
  signals: Signals;
  claims: Claims;
  sources: Sources1;
  cases: Cases;
  indicator?: IndicatorDefinitionV1 | null;
  observations?: Observations;
  engine_code_hash: EngineCodeHash1;
  rules_version?: RulesVersion2;
}
export interface ResearchSubmitV1 {
  schema_version?: SchemaVersion135;
  title: Title11;
  scope: Scope4;
  domain_tags: DomainTags2;
  research_as_of: ResearchAsOf5;
  signal_ids: SignalIds1;
  historical_case_ids?: HistoricalCaseIds1;
  indicator_id?: IndicatorId3;
  target?: ForecastTargetV1 | null;
  lifecycle_stage?: LifecycleStage1;
  recipe_id?: RecipeId;
  provider?: Provider5;
  label: Label25;
}
export interface SignalV1 {
  schema_version?: SchemaVersion136;
  signal_id: SignalId;
  kind?: Kind12;
  status?: Status11;
  headline: Headline;
  lifecycle_stage: LifecycleStage;
  claim_ids: ClaimIds1;
  source_group_ids: SourceGroupIds;
  independent_source_count: IndependentSourceCount;
  mechanism_tags: MechanismTags2;
  domain_tags: DomainTags3;
  detected_at: DetectedAt;
  label: Label26;
}
export interface SourceVersionV1 {
  schema_version?: SchemaVersion137;
  source_version_id: SourceVersionId4;
  source_id: SourceId3;
  source_group_id: SourceGroupId1;
  source_type: SourceType;
  original_language: OriginalLanguage;
  region: Region2;
  dedup_method: DedupMethod;
  original_source_url?: OriginalSourceUrl;
  version_label: VersionLabel;
  url: Url2;
  title: Title12;
  publisher: Publisher;
  published_at: PublishedAt6;
  event_at: EventAt;
  available_at: AvailableAt3;
  ingested_at: IngestedAt;
  revised_at: RevisedAt;
  availability_basis: AvailabilityBasis;
  availability_note: AvailabilityNote;
  content_hash: ContentHash2;
  content: Content1;
  usage_permission: UsagePermission;
  license_note: LicenseNote;
  access_method: AccessMethod;
  reliability_note: ReliabilityNote;
  domain_tags: DomainTags4;
  label: Label27;
}
export interface ResearchTopicV1 {
  schema_version?: SchemaVersion138;
  topic_id: TopicId2;
  owner_user_id?: OwnerUserId;
  title: Title13;
  scope: Scope5;
  domain_tags: DomainTags5;
  version: Version;
}
export interface ResolveRequestV1 {
  schema_version?: SchemaVersion139;
  observation_id?: ObservationId2;
  unavailable_reason?: UnavailableReason;
}
export interface ReviewDecisionV1 {
  schema_version?: SchemaVersion140;
  decision_id: DecisionId1;
  critic_run_id: CriticRunId1;
  draft_id: DraftId7;
  decision: Decision1;
  publication_allowed: PublicationAllowed2;
  verified_finding_ids: VerifiedFindingIds;
  rule_version?: RuleVersion1;
  rationale: Rationale2;
  decided_at: DecidedAt1;
}
export interface ReviewViewV1 {
  schema_version?: SchemaVersion141;
  report: CriticReportV1;
  decision: ReviewDecisionV1;
}
export interface RevisionRequestV1 {
  schema_version?: SchemaVersion142;
  review_id: ReviewId2;
  confirmed_finding_ids: ConfirmedFindingIds;
  additional_case_ids?: AdditionalCaseIds;
}
export interface RevisionViewV1 {
  schema_version?: SchemaVersion143;
  draft_id: DraftId8;
  parent_draft_id: ParentDraftId;
  draft_sequence: DraftSequence2;
  input_hash: InputHash4;
  draft_hash: DraftHash3;
  changes: Changes;
  body: M2DraftV1;
}
export interface Changes {
  [k: string]: unknown;
}
export interface SandboxConsentV1 {
  schema_version?: SchemaVersion144;
  explicit_sandbox_consent: ExplicitSandboxConsent1;
}
/**
 * Unverified provider output, separate from ingested/verified SourceV1 evidence.
 */
export interface SearchHitV1 {
  schema_version?: SchemaVersion145;
  hit_id: HitId;
  provider: Provider6;
  url: Url3;
  title: Title14;
  snippet: Snippet;
  summary: Summary4;
  content: Content2;
  site_name?: SiteName;
  published_at: PublishedAt7;
  retrieved_at: RetrievedAt2;
  provider_rank_score?: ProviderRankScore;
  provider_authority?: ProviderAuthority;
  evidence_status?: EvidenceStatus1;
  label: Label28;
}
export interface SignalImportV1 {
  schema_version?: SchemaVersion146;
  headline: Headline1;
  claim_ids: ClaimIds2;
  lifecycle_stage?: LifecycleStage2;
  mechanism_tags?: MechanismTags3;
  domain_tags: DomainTags6;
}
export interface SourceImportV1 {
  schema_version?: SchemaVersion147;
  url: Url4;
  title: Title15;
  publisher: Publisher1;
  source_type: SourceType1;
  original_language?: OriginalLanguage1;
  region?: Region3;
  published_at?: PublishedAt8;
  event_at?: EventAt1;
  available_at?: AvailableAt4;
  availability_basis: AvailabilityBasis1;
  availability_note?: AvailabilityNote1;
  revised_at?: RevisedAt1;
  content?: Content3;
  usage_permission: UsagePermission1;
  license_note: LicenseNote1;
  access_method?: AccessMethod1;
  reliability_note: ReliabilityNote1;
  original_source_url?: OriginalSourceUrl1;
  domain_tags: DomainTags7;
  claims?: Claims1;
  label: Label29;
}
export interface SourceIngestedV1 {
  schema_version?: SchemaVersion148;
  version: SourceVersionV1;
  claim_ids: ClaimIds3;
  duplicate: Duplicate;
}
export interface SourceV1 {
  schema_version?: SchemaVersion149;
  source_id: SourceId4;
  url: Url5;
  published_at: PublishedAt9;
  provenance: Provenance;
  snippet: Snippet1;
  label: Label30;
}
export interface TurningDecisionV1 {
  schema_version?: SchemaVersion150;
  level: Level1;
  action: Action4;
  delta: EvidenceDeltaV1;
  rationale: Rationale3;
  rules_version?: RulesVersion3;
}
export interface TurningPointReviewV1 {
  schema_version?: SchemaVersion151;
  trigger_id: TriggerId;
  forecast_id: ForecastId3;
  old_version_id: OldVersionId1;
  new_version_id?: NewVersionId1;
  final_level: FinalLevel;
  decision: Decision2;
  evidence_delta_hash: EvidenceDeltaHash;
  reviewed_at: ReviewedAt;
}
export interface UserReportV1 {
  schema_version?: SchemaVersion152;
  report_id: ReportId6;
  user_id: UserId10;
  current_version_id: CurrentVersionId;
}
export interface UserReportVersionV1 {
  schema_version?: SchemaVersion153;
  report_version_id: ReportVersionId8;
  report_id: ReportId7;
  user_id: UserId11;
  report_version: ReportVersion;
  profile_snapshot_id: ProfileSnapshotId4;
  research_as_of: ResearchAsOf6;
  forecast_version_ids: ForecastVersionIds3;
  personal_impact_ids: PersonalImpactIds;
  change_reason: ChangeReason3;
  created_at: CreatedAt10;
}
export interface VerifiedRegistrationV1 {
  schema_version?: SchemaVersion154;
  email: Email6;
  password: Password7;
  verification_id: VerificationId1;
  code: Code9;
}
export interface WebFetchPreviewV1 {
  schema_version?: SchemaVersion155;
  url: Url6;
  title: Title16;
  excerpt: Excerpt1;
  full_content_hash: FullContentHash;
  retrieved_at: RetrievedAt3;
  published_at?: PublishedAt10;
  label?: Label31;
  evidence_status?: EvidenceStatus2;
  retained_characters: RetainedCharacters;
}
export interface WebFetchRequestV1 {
  schema_version?: SchemaVersion156;
  url: Url7;
}
export interface WebSearchRequestV1 {
  schema_version?: SchemaVersion157;
  query: Query1;
  count?: Count;
}
export interface WebSearchResponseV1 {
  schema_version?: SchemaVersion158;
  results: Results;
}
export interface WorldForecastV1 {
  schema_version?: SchemaVersion159;
  forecast_id: ForecastId4;
  topic_id: TopicId3;
  stable_target_key: StableTargetKey;
  target_type: TargetType1;
  lifecycle_stage: LifecycleStage;
  current_version_id?: CurrentVersionId1;
}
