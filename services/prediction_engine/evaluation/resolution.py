"""Pre-registered resolution, with no missing-data-as-success or invented numeric forecast."""

from datetime import datetime
from typing import Literal
from uuid import UUID, uuid4

from prediction_engine.contracts.models import EvaluationProtocolV1, ForecastResolutionV1


def resolve(
    protocol: EvaluationProtocolV1,
    now: datetime,
    value: float | None = None,
    observation_id: UUID | None = None,
    unavailable_reason: str | None = None,
) -> ForecastResolutionV1:
    status: Literal[
        "not_due", "confirmed", "disconfirmed", "inconclusive", "unresolved_due_to_data"
    ] = "not_due"
    reason = "尚未到预登记验证期限"
    if now >= protocol.due_at:
        if value is None:
            status = "unresolved_due_to_data" if unavailable_reason else "inconclusive"
            reason = unavailable_reason or "缺少符合预登记口径的观测，不能认定预测正确"
        else:
            confirmed = {
                "gte": value >= protocol.threshold,
                "lte": value <= protocol.threshold,
                "eq": value == protocol.threshold,
            }[protocol.operator]
            status = "confirmed" if confirmed else "disconfirmed"
            reason = "按冻结阈值、口径和验证来源判定；不追溯修改题面"

    def error(prediction: float | None) -> float | None:
        return (
            abs(prediction - value)
            if prediction is not None and value is not None and now >= protocol.due_at
            else None
        )

    return ForecastResolutionV1(
        resolution_id=uuid4(),
        protocol_id=protocol.protocol_id,
        status=status,
        checked_at=now,
        observation_id=observation_id if now >= protocol.due_at else None,
        observed_value=value if now >= protocol.due_at else None,
        forecast_absolute_error_a=error(protocol.point_prediction_a),
        forecast_absolute_error_b=error(protocol.point_prediction_b),
        baseline_absolute_error=error(protocol.baseline_value),
        reason=reason,
    )
