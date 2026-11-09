"""Content-addressed, verified copies of our own Core code for offline replay."""

import json
import os
import subprocess
import sys
from pathlib import Path
from uuid import uuid4
from zipfile import ZIP_DEFLATED, ZipFile

import prediction_engine
from prediction_engine.forecasting.workflow import hashed

FOLDER = Path(".local/engine_versions")


def manifest() -> list[tuple[str, str]]:
    root = Path(prediction_engine.__file__).parent
    return [
        (str(path.relative_to(root)), path.read_text())
        for path in sorted(root.rglob("*.py"))
        if "build" not in path.parts
    ]


def freeze_engine(expected: str) -> None:
    entries = manifest()
    if hashed(entries) != expected:
        raise ValueError("RESEARCH_ENGINE_CHANGED_DURING_SUBMISSION")
    FOLDER.mkdir(parents=True, exist_ok=True)
    target = FOLDER / f"{expected}.zip"
    if target.exists():
        verify_engine(expected)
        return
    temporary = target.with_suffix(f".{os.getpid()}.{uuid4().hex}.tmp")
    with ZipFile(temporary, "w", compression=ZIP_DEFLATED) as archive:
        for name, content in entries:
            archive.writestr("prediction_engine/" + name, content)
    temporary.replace(target)


def verify_engine(expected: str) -> Path:
    target = FOLDER / f"{expected}.zip"
    with ZipFile(target) as archive:
        entries = []
        for name in sorted(archive.namelist()):
            if (
                not name.startswith("prediction_engine/")
                or not name.endswith(".py")
                or ".." in Path(name).parts
            ):
                raise ValueError("INVALID_ENGINE_ARTIFACT")
            entries.append((name.removeprefix("prediction_engine/"), archive.read(name).decode()))
    if hashed(entries) != expected:
        raise ValueError("ENGINE_ARTIFACT_HASH_MISMATCH")
    return target.resolve()


def replay_archived(expected: str, payload: dict[str, object]) -> str:
    target = verify_engine(expected)
    code = """import sys,json
sys.path.insert(0,sys.argv[1])
from prediction_engine.contracts.models import ResearchSnapshotV1,ResearchNarrativeV1
from prediction_engine.forecasting.workflow import build_forecast_draft,hashed
from uuid import UUID
p=json.load(sys.stdin)
kwargs={'parent_version_id':UUID(p['parent_version_id'])} if p.get('parent_version_id') else {}
d=build_forecast_draft(UUID(p['run_id']),ResearchSnapshotV1.model_validate(p['snapshot']),
    ResearchNarrativeV1.model_validate(p['narrative']),p['model_id'],**kwargs)
print(hashed(d.model_dump(mode='json')))
"""
    # Isolated interpreter receives only frozen data, with no API keys/DB credentials or proxy env.
    result = subprocess.run(
        [sys.executable, "-I", "-c", code, str(target)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        timeout=15,
        env={
            key: value
            for key, value in os.environ.items()
            if key in {"PATH", "SYSTEMROOT", "LANG", "LC_ALL"}
        },
    )
    fingerprint = result.stdout.strip()
    if (
        result.returncode != 0
        or len(fingerprint) != 64
        or any(c not in "0123456789abcdef" for c in fingerprint)
    ):
        raise ValueError("ARCHIVED_ENGINE_REPLAY_FAILED")
    return fingerprint
