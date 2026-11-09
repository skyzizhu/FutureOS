"""Exactly one manual Search and one Fetch through the admin API, with sanitized output.

Requires explicit local configuration. No model completion or forecasting. Stores metadata only.
"""

import json
import os
from datetime import UTC, datetime
from pathlib import Path

import httpx
from dotenv import dotenv_values


def main() -> None:
    env = {
        **os.environ,
        **{key: value for key, value in dotenv_values(".env").items() if value is not None},
    }
    api = env.get("API_INTERNAL_URL", "http://127.0.0.1:8100")
    headers = {"Authorization": "Bearer " + env.get("DEMO_ADMIN_TOKEN", "demo-admin-local-only")}
    report: dict[str, object] = {
        "checked_at": datetime.now(UTC).isoformat(),
        "provider": "deepseek",
        "purpose": "M1 manual connectivity; not a forecast",
        "results": [],
    }
    results = []
    with httpx.Client(base_url=api, headers=headers, timeout=25, trust_env=False) as client:
        search = client.post(
            "/api/v1/admin/sources/search",
            json={"query": "PostgreSQL transactions site:postgresql.org/docs/16/", "count": 1},
        )
        search_body = search.json()
        results.append(
            {
                "tool": "search",
                "http_status": search.status_code,
                "result_count": len(search_body.get("results", [])),
                "error_code": search_body.get("code"),
            }
        )
        fetched = client.post(
            "/api/v1/admin/sources/fetch",
            json={"url": "https://www.postgresql.org/docs/16/tutorial-transactions.html"},
        )
        fetch_body = fetched.json()
        results.append(
            {
                "tool": "fetch",
                "http_status": fetched.status_code,
                "retained_characters": fetch_body.get("retained_characters", 0),
                "error_code": fetch_body.get("code"),
            }
        )
        if fetched.status_code == 200:
            # Retain only a link/title and provenance; no fetched third-party body is stored here.
            response = client.post(
                "/api/v1/admin/sources/ingest",
                json={
                    "url": fetch_body["url"],
                    "title": fetch_body["title"] or "PostgreSQL documentation",
                    "publisher": "PostgreSQL Documentation",
                    "source_type": "official",
                    "original_language": "en",
                    "availability_basis": "observed_now",
                    "usage_permission": "metadata_only",
                    "license_note": "Metadata/link only; no body retained",
                    "access_method": "deepseek",
                    "reliability_note": "Provider retrieval; content and time remain unverified",
                    "domain_tags": ["technology"],
                    "label": "REAL",
                    "claims": [],
                },
            )
            results.append(
                {
                    "operation": "ingest_metadata",
                    "http_status": response.status_code,
                    "error_code": response.json().get("code"),
                }
            )
        audit = client.get("/api/v1/admin/web-access")
        if audit.status_code == 200:
            report["audit"] = [
                {key: row[key] for key in ("tool", "status", "http_attempts")}
                for row in audit.json()[:2]
            ]
    report["results"] = results
    output = Path("docs/milestones/evidence/M1-deepseek-live.json")
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if any(result["http_status"] != 200 for result in results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
