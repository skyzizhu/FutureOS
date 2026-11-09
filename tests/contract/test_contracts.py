import inspect
import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import uuid4

import jsonschema
import pytest
from prediction_engine.contracts import models
from prediction_engine.contracts.models import (
    EntitlementV1,
    ForecastDraftV1,
    ForecastTargetV1,
    UserReportVersionV1,
)
from pydantic import BaseModel, ValidationError

from apps.api.main import create_app
from infra.settings import Settings

MODELS = [
    (name, model)
    for name, model in inspect.getmembers(models, inspect.isclass)
    if issubclass(model, BaseModel) and name.endswith("V1")
]


@pytest.mark.parametrize("name,model", MODELS)
def test_generated_schema_is_current(name, model):
    schema = json.loads(Path(f"packages/contracts/schemas/{name}.json").read_text())
    assert schema == model.model_json_schema()
    jsonschema.Draft202012Validator.check_schema(schema)


def test_openapi_is_current(tmp_path):
    app = create_app(Settings(_env_file=None, database_url=f"sqlite:///{tmp_path / 'unused.db'}"))
    assert app.openapi() == json.loads(Path("packages/contracts/openapi.json").read_text())
    assert "/api/v1/demo/research" in app.openapi()["paths"]


def test_no_target_is_hypothesis_only():
    fields = dict(
        draft_id=uuid4(),
        run_id=uuid4(),
        draft_sequence="A",
        statement="hypothesis",
        research_as_of=datetime.now(UTC),
        evidence_claim_ids=(),
        inputs_hash="a" * 64,
        model_version="mock",
    )
    assert ForecastDraftV1(kind="hypothesis", **fields).target is None
    with pytest.raises(ValidationError):
        ForecastDraftV1(kind="draft_forecast", **fields)


def test_time_validation():
    now = datetime.now(UTC)
    fields = dict(
        target_type="binary",
        population_scope="demo",
        geography="demo",
        metric_definition="demo",
        direction_or_threshold="demo",
        baseline="demo",
        target_start_at=now,
        target_end_at=now + timedelta(days=1),
        resolution_source="demo",
        resolution_rule="demo",
    )
    assert ForecastTargetV1(**fields)
    with pytest.raises(ValidationError):
        ForecastTargetV1(**{**fields, "target_end_at": now})
    with pytest.raises(ValidationError):
        ForecastTargetV1(**{**fields, "target_start_at": datetime(2026, 1, 1)})


def test_frozen_reports_pin_versions_and_subscription_is_independent():
    version_id = uuid4()
    report = UserReportVersionV1(
        report_version_id=uuid4(),
        report_id=uuid4(),
        user_id=uuid4(),
        report_version=1,
        profile_snapshot_id=uuid4(),
        research_as_of=datetime.now(UTC),
        forecast_version_ids=(version_id,),
        personal_impact_ids=(uuid4(),),
        change_reason="initial",
        created_at=datetime.now(UTC),
    )
    with pytest.raises(ValidationError):
        report.forecast_version_ids = (uuid4(),)
    assert report.forecast_version_ids == (version_id,)
    entitlement = EntitlementV1(
        user_id=uuid4(),
        subscription_status="active",
        paid_periodic_research_enabled=True,
        email_digest_opt_in=False,
        email_alert_opt_in=False,
    )
    assert entitlement.paid_periodic_research_enabled
