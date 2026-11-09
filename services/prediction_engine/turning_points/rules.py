"""Local, verifiable evidence deltas; no hot-word count or universal percentage threshold."""

from prediction_engine.contracts.models import (
    ChangeAssertionV1,
    EvidenceDeltaV1,
    MonitorPolicyV1,
    ResearchSnapshotV1,
    TurningDecisionV1,
)
from prediction_engine.forecasting.workflow import hashed


def fingerprint(snapshot: ResearchSnapshotV1) -> str:
    return hashed(
        {
            "claims": sorted(
                (str(c.claim_id), c.claim_text, c.relation, str(c.source_group_id))
                for c in snapshot.claims
            ),
            "observations": sorted((str(o.observation_id), o.value) for o in snapshot.observations),
            "cases": sorted(
                (str(c.case_id), [e.model_dump(mode="json") for e in c.outcomes])
                for c in snapshot.cases
            ),
        }
    )


def classify(
    old: ResearchSnapshotV1,
    new: ResearchSnapshotV1,
    policy: MonitorPolicyV1,
    assertions: tuple[ChangeAssertionV1, ...] = (),
) -> TurningDecisionV1:
    old_ids = {c.claim_id for c in old.claims}
    old_signatures = {(c.claim_text.strip().casefold(), c.relation) for c in old.claims}
    added = [c for c in new.claims if c.claim_id not in old_ids]
    duplicates = []
    novel = []
    seen = set(old_signatures)
    for claim in added:
        signature = (claim.claim_text.strip().casefold(), claim.relation)
        if signature in seen:
            duplicates.append(claim.claim_id)
        else:
            novel.append(claim)
            seen.add(signature)
    groups = {c.source_group_id for c in novel if c.relation != "context"}
    old_obs = {o.observation_id for o in old.observations}
    changed = [o for o in new.observations if o.observation_id not in old_obs]
    reasons = []
    level = "T0"
    if novel or changed:
        level = "T1"
        reasons.append("NEW_VERIFIED_DATA")
    counter_groups = {c.source_group_id for c in novel if c.relation == "contradicts"}
    if len(counter_groups) >= policy.independent_groups_required:
        level = "T2"
        reasons.append("INDEPENDENT_COUNTEREVIDENCE")
    if policy.indicator_absolute_delta and old.observations:
        baseline = max(old.observations, key=lambda o: o.period_end).value
        recent = sorted(changed, key=lambda o: o.period_end)[-policy.consecutive_periods :]
        if len({o.period_end for o in recent}) >= policy.consecutive_periods and all(
            abs(o.value - baseline) >= policy.indicator_absolute_delta for o in recent
        ):
            level = "T2"
            reasons.append("SUSTAINED_INDICATOR_CHANGE")
    new_ids = {c.claim_id: c for c in new.claims}
    for assertion in assertions:
        if not set(assertion.claim_ids) <= new_ids.keys():
            raise ValueError("ASSERTION_EVIDENCE_MISSING")
        if assertion.kind in {"critical_assumption_broken", "resolution_source_revised"}:
            if assertion.prior_claim_id not in old_ids or not any(
                new_ids[i].relation == "contradicts" for i in assertion.claim_ids
            ):
                raise ValueError("CRITICAL_ASSERTION_NOT_SUPPORTED")
            level = "T3"
            reasons.append(assertion.kind.upper())
        elif (
            len({new_ids[i].source_group_id for i in assertion.claim_ids})
            >= policy.independent_groups_required
            and level != "T3"
        ):
            level = "T2"
            reasons.append(assertion.kind.upper())
    delta = EvidenceDeltaV1(
        added_claim_ids=tuple(c.claim_id for c in novel),
        independent_groups=len(groups),
        duplicate_claim_ids=tuple(duplicates),
        changed_observation_ids=tuple(o.observation_id for o in changed),
        reasons=tuple(reasons),
        fingerprint=fingerprint(new),
    )
    return TurningDecisionV1.model_validate(
        {
            "level": level,
            "action": {
                "T0": "archive",
                "T1": "observe",
                "T2": "targeted_research",
                "T3": "block_pending_review",
            }[level],
            "delta": delta,
            "rationale": {
                "T0": "仅重复/元数据变化，归档不重预测",
                "T1": "新增线索尚未达到预登记实质变化门槛",
                "T2": "独立反证或持续指标变化，进入定向复核",
                "T3": "核实的关键假设/数据更正，优先复核并保留旧版待核实标记",
            }[level],
        }
    )
