import ast
from pathlib import Path


def imports(path):
    for node in ast.walk(ast.parse(path.read_text())):
        if isinstance(node, ast.Import):
            yield from (alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            yield node.module.split(".")[0]


def test_engine_is_an_independent_package():
    forbidden = {"apps", "infra", "workers", "fastapi", "sqlalchemy", "redis", "httpx", "requests"}
    for path in Path("services/prediction_engine").rglob("*.py"):
        assert not forbidden.intersection(imports(path)), path


def test_web_has_no_providers_or_prediction_implementation():
    for path in Path("apps/web/app").rglob("*.tsx"):
        text = path.read_text()
        assert "OPENAI_API_KEY" not in text
        assert "sk_live_" not in text
        assert "prediction_engine" not in text
    for module in ["ingestion", "evidence", "signal_fusion", "critic", "adjudication"]:
        assert list(Path(f"services/prediction_engine/{module}").iterdir())


def test_critic_contract_cannot_return_rewritten_forecast():
    from prediction_engine.contracts.models import CriticFindingV1

    assert "statement" in CriticFindingV1.model_fields
    assert "replacement_forecast" not in CriticFindingV1.model_fields
    assert "forecast_version_id" not in CriticFindingV1.model_fields
