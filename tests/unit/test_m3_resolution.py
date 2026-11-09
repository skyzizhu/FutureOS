from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from prediction_engine.contracts.models import EvaluationProtocolV1
from prediction_engine.evaluation.resolution import resolve

NOW = datetime(2026, 11, 1, tzinfo=UTC)


def protocol(**changes):
    fields = dict(
        protocol_id=uuid4(),
        version_id=uuid4(),
        mode="forward",
        label="REAL",
        registered_at=NOW,
        as_of=NOW,
        due_at=NOW + timedelta(days=1),
        metric_definition="fixed_metric",
        geography="fixed_region",
        unit="count",
        resolution_source="https://example.invalid/statistics",
        operator="gte",
        threshold=70,
        point_prediction_a=75,
        point_prediction_b=72,
        baseline_value=60,
        source_snapshot_hash="0" * 64,
        model_id="fixture",
        prompt_hash="1" * 64,
        testset_version="m3-v1",
        limitations=("Synthetic test contract, not a real forecast",),
    )
    return EvaluationProtocolV1(**{**fields, **changes})


@pytest.mark.parametrize(
    "value,status", [(80, "confirmed"), (70, "confirmed"), (69, "disconfirmed")]
)
def test_resolution_preregistered_and_baseline(value, status):
    p = protocol()
    result = resolve(p, NOW + timedelta(days=2), value, uuid4())
    assert result.status == status
    assert result.forecast_absolute_error_a == abs(75 - value)
    assert result.forecast_absolute_error_b == abs(72 - value)
    assert result.baseline_absolute_error == abs(60 - value)


def test_not_due_and_missing_never_counts_as_success():
    p = protocol()
    result = resolve(p, NOW, 999, uuid4())
    assert result.status == "not_due" and result.observed_value is None
    assert resolve(p, NOW + timedelta(days=2)).status == "inconclusive"
    assert (
        resolve(p, NOW + timedelta(days=2), unavailable_reason="Missing verified data").status
        == "unresolved_due_to_data"
    )


def test_threshold_is_not_a_point_prediction():
    p = protocol(point_prediction_a=None, point_prediction_b=None)
    result = resolve(p, NOW + timedelta(days=2), 80, uuid4())
    assert result.forecast_absolute_error_a is None and result.forecast_absolute_error_b is None
    assert result.baseline_absolute_error == 20
