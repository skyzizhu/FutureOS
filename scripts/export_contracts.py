import inspect
import json
from pathlib import Path

from prediction_engine.contracts import models
from pydantic import BaseModel

from apps.api.main import app


def export() -> None:
    target = Path("packages/contracts")
    schemas = target / "schemas"
    schemas.mkdir(parents=True, exist_ok=True)
    for name, model in inspect.getmembers(models, inspect.isclass):
        if issubclass(model, BaseModel) and name.endswith("V1"):
            (schemas / f"{name}.json").write_text(
                json.dumps(model.model_json_schema(), indent=2, ensure_ascii=False) + "\n"
            )
    (target / "openapi.json").write_text(
        json.dumps(app.openapi(), indent=2, ensure_ascii=False) + "\n"
    )


if __name__ == "__main__":
    export()
