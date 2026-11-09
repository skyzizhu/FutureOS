from prediction_engine.contracts.models import AnalogyAssessmentV1, ResearchSnapshotV1
from prediction_engine.mechanisms.catalog import RECIPES


def compare_cases(snapshot: ResearchSnapshotV1) -> tuple[AnalogyAssessmentV1, ...]:
    recipe = RECIPES[snapshot.request.recipe_id]
    tags = {snapshot.request.recipe_id, *recipe.capabilities, "complementarity", "adoption"}
    result = []
    for case in snapshot.cases:
        overlap = tuple(sorted(tags & set(case.mechanism_tags)))
        if not overlap:
            continue
        result.append(
            AnalogyAssessmentV1(
                case_id=case.case_id,
                mechanism_overlap=overlap,
                similarities=(
                    "共同机制标签：" + "、".join(overlap),
                    "案例当时前提：" + case.initial_conditions,
                ),
                key_differences=(
                    "案例领域："
                    + "/".join(case.domain_tags)
                    + "；当前领域："
                    + "/".join(tag.value for tag in snapshot.request.domain_tags),
                    "当前适用范围：" + snapshot.request.scope,
                    "机构、地区和采用障碍未被证明一致，标签重合不证明因果可迁移",
                ),
                non_transferable=("不能迁移历史增长曲线、就业变化幅度或成功概率",),
                known_outcomes=case.outcomes,
                limitations=case.limitations,
            )
        )
    return tuple(result)
