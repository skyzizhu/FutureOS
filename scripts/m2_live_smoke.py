"""Explicit one-call DeepSeek completion test on DEMO inputs; no real-world prediction."""

import json
import os
import time
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import httpx
from dotenv import dotenv_values


def main() -> None:
    env = {
        **os.environ,
        **{key: value for key, value in dotenv_values(".env").items() if value is not None},
    }
    report: dict[str, object] = {
        "checked_at": datetime.now(UTC).isoformat(),
        "input_label": "DEMO",
        "publication_allowed": False,
        "purpose": "M2 bounded JSON connectivity, not forecasting accuracy",
    }
    with httpx.Client(
        base_url=env.get("API_INTERNAL_URL", "http://127.0.0.1:8100"),
        trust_env=False,
        timeout=15,
        headers={"Authorization": "Bearer " + env.get("DEMO_ADMIN_TOKEN", "demo-admin-local-only")},
    ) as client:
        response = client.post("/api/v1/admin/research/demo-inputs")
        response.raise_for_status()
        payload = response.json()
        payload["provider"] = "deepseek"
        accepted = client.post(
            "/api/v1/admin/research/submit",
            json=payload,
            headers={"Idempotency-Key": "m2-live-" + str(uuid4())},
        )
        if accepted.status_code != 202:
            report.update(status="rejected", code=accepted.json().get("code"))
        else:
            run_id = accepted.json()["run_id"]
            report["run_id"] = run_id
            for _ in range(110):
                state = client.get(f"/api/v1/admin/research/runs/{run_id}").json()
                if state.get("status") in {"succeeded", "failed_terminal", "cancelled"}:
                    report.update(
                        status=state["status"],
                        error_code=state.get("error_code"),
                        model_id=state.get("model_id"),
                        draft_hash=state.get("draft_hash"),
                    )
                    if state.get("draft"):
                        report["draft_label"] = state["draft"]["label"]
                        report["kind"] = state["draft"]["kind"]
                        report["actual_model_id"] = state["draft"]["model_id"]
                        replay = client.post(f"/api/v1/admin/research/runs/{run_id}/replay")
                        report["offline_replay_identical"] = replay.json().get("identical")
                    break
                time.sleep(1)
            else:
                report.update(
                    status="timeout_waiting", error_code="CHECK_RUN_MANUALLY_NO_AUTO_RETRY"
                )
            calls = client.get("/api/v1/admin/research/model-calls").json()
            report["model_call"] = [
                {key: row.get(key) for key in ("status", "model_id", "usage", "error_code")}
                for row in calls
                if row["run_id"] == run_id
            ]
    path = Path("docs/milestones/evidence/M2-deepseek-live.json")
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if report.get("status") != "succeeded":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
