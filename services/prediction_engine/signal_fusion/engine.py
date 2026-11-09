from uuid import NAMESPACE_URL, UUID, uuid5

from prediction_engine.contracts.models import ResearchSnapshotV1, SignalFusionV1
from prediction_engine.mechanisms.catalog import RECIPES


def fuse_signals(snapshot: ResearchSnapshotV1) -> tuple[SignalFusionV1, ...]:
    recipe = RECIPES[snapshot.request.recipe_id]
    groups: set[UUID] = set()
    capabilities = set()
    signal_ids = []
    support = {claim.claim_id for claim in snapshot.claims if claim.relation != "contradicts"}
    for signal in snapshot.signals:
        relevant = set(signal.mechanism_tags) & set(recipe.capabilities)
        supporting = [
            claim
            for claim in snapshot.claims
            if claim.claim_id in signal.claim_ids and claim.claim_id in support
        ]
        if relevant and supporting:
            groups.update(claim.source_group_id for claim in supporting)
            capabilities.update(relevant)
            signal_ids.append(signal.signal_id)
    if len(groups) < 2 or len(signal_ids) < 2 or not set(recipe.capabilities) <= capabilities:
        return ()
    return (
        SignalFusionV1(
            fusion_id=uuid5(NAMESPACE_URL, "fusion:" + ":".join(map(str, sorted(signal_ids)))),
            signal_ids=tuple(sorted(signal_ids)),
            independent_source_groups=len(groups),
            mechanism=recipe.mechanism,
            remaining_bottlenecks=recipe.bottlenecks,
            emergent_hypotheses=("若互补条件同时有效，可能出现组合能力；仍须排除瓶颈和替代解释",),
            opposing_explanations=recipe.opposing,
            next_observable_signals=recipe.observables,
            stage=snapshot.request.lifecycle_stage,
        ),
    )
