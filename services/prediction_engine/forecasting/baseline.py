from prediction_engine.contracts.models import BaselineV1, ResearchSnapshotV1


def last_value_baseline(snapshot: ResearchSnapshotV1) -> BaselineV1:
    rows = sorted(snapshot.observations, key=lambda item: item.period_end)
    if snapshot.indicator is None or len(rows) < 3:
        return BaselineV1(
            method="not_applicable",
            sample_count=len(rows),
            observation_ids=tuple(item.observation_id for item in rows),
            limitations=("至少需要三个口径一致的统计期；不得用 LLM 虚构数值",),
        )
    if len({(row.period_start, row.period_end) for row in rows}) != len(rows):
        raise ValueError("DUPLICATE_OBSERVATION_PERIOD")
    return BaselineV1(
        method="last_value",
        sample_count=len(rows),
        observation_ids=tuple(item.observation_id for item in rows),
        last_observed_value=rows[-1].value,
        projected_value=rows[-1].value,
        unit=snapshot.indicator.unit,
        limitations=("朴素持平对照，不证明主假设成立，不包含可靠区间或校准概率",),
    )
