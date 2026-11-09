"""Critic runs in a separate read-only process with no credentials or external tools."""

import json
import os
import subprocess
import sys
from pathlib import Path
from uuid import UUID

import prediction_engine
from prediction_engine.contracts.models import CriticReportV1, M2DraftV1, ResearchSnapshotV1


def run_critic(identifier: UUID, draft: M2DraftV1, snapshot: ResearchSnapshotV1) -> CriticReportV1:
    code = """
import sys,json
sys.path.insert(0,sys.argv[1])
from uuid import UUID
from prediction_engine.contracts.models import M2DraftV1,ResearchSnapshotV1
from prediction_engine.critic.checkers import review_draft
# No network, child processes or filesystem writes after trusted imports.
def deny(event,args):
    forbidden = ('subprocess.Popen','os.system','os.remove','os.rename','os.mkdir')
    if event.startswith('socket.') or event in forbidden:
        raise PermissionError('CRITIC_READ_ONLY')
    if event in ('open','os.listdir','os.scandir'):
        raise PermissionError('CRITIC_NO_FILESYSTEM')
sys.addaudithook(deny)
p=json.load(sys.stdin)
r=review_draft(UUID(p['id']),M2DraftV1.model_validate(p['draft']),ResearchSnapshotV1.model_validate(p['snapshot']))
print(r.model_dump_json())
"""
    result = subprocess.run(
        [
            sys.executable,
            "-I",
            "-B",
            "-c",
            code,
            str(Path(prediction_engine.__file__).parent.parent),
        ],
        input=json.dumps(
            {
                "id": str(identifier),
                "draft": draft.model_dump(mode="json"),
                "snapshot": snapshot.model_dump(mode="json"),
            }
        ),
        text=True,
        capture_output=True,
        timeout=15,
        env={k: v for k, v in os.environ.items() if k in {"PATH", "SYSTEMROOT", "LANG", "LC_ALL"}},
    )
    if result.returncode != 0 or len(result.stdout) > 1_000_000:
        raise ValueError("CRITIC_PROCESS_FAILED")
    return CriticReportV1.model_validate_json(result.stdout)
