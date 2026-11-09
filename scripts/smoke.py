"""Read-only checks plus a synthetic job on an already running local DEMO stack."""

import os
import time
from uuid import uuid4

import httpx


def main() -> None:
    with httpx.Client(
        base_url="http://127.0.0.1:" + os.getenv("FUTUREOS_API_PORT", "8100"),
        timeout=5,
        trust_env=False,
    ) as client:
        assert client.get("/api/v1/health/ready").status_code == 200
        headers = {"Authorization": "Bearer demo-user-local-only", "Idempotency-Key": str(uuid4())}
        response = client.post(
            "/api/v1/demo/research", headers=headers, json={"question": "DEMO smoke research"}
        )
        assert response.status_code == 202, response.text
        accepted = response.json()
        replay = client.post(
            "/api/v1/demo/research", headers=headers, json={"question": "DEMO smoke research"}
        )
        assert replay.json() == accepted
        for _ in range(30):
            job = client.get(f"/api/v1/jobs/{accepted['job_id']}", headers=headers).json()
            if job["status"] == "succeeded":
                assert job["result"]["label"] == "DEMO"
                assert job["result"]["kind"] == "hypothesis"
                print(
                    "PASS: readiness -> accepted -> idempotent replay -> worker -> DEMO hypothesis"
                )
                return
            assert job["status"] not in {"failed_terminal", "cancelled"}, job
            time.sleep(1)
        raise AssertionError("Worker did not complete within 30 seconds")


if __name__ == "__main__":
    main()
