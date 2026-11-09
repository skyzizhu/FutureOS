"""Manual, bounded observation collector for the pre-registered Playwright milestone.
No timer, notification or model call. Before due date no network request is made.
"""

import json
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

import httpx
from prediction_engine.contracts.models import (
    EvaluationProtocolV1,
    IndicatorImportV1,
    ObservationImportV1,
    ResolveRequestV1,
    SourceImportV1,
)
from sqlalchemy.orm import Session

from infra.db import EvaluationProtocol, make_engine
from infra.evidence_repository import EvidenceRepository
from infra.review_repository import ReviewRepository
from infra.settings import Settings
from scripts.seed_demo import ADMIN_ID

URL = "https://api.github.com/repos/microsoft/playwright/releases"


def main() -> None:
    registration = json.loads(Path("docs/evaluations/M3-forward-registration.json").read_text())
    identifier = UUID(registration["protocol_id"])
    engine = make_engine(Settings().database_url)
    with Session(engine) as session:
        row = session.get(EvaluationProtocol, identifier)
        assert row is not None
        protocol = EvaluationProtocolV1.model_validate(row.body)
        if datetime.now(UTC) < protocol.due_at:
            print("not_due: no network request, no model call")
            return
        if (
            protocol.resolution_source != URL
            or protocol.metric_definition != "playwright_stable_release_occurs"
        ):
            raise SystemExit("Unsupported frozen protocol; no inferred collector")
        version = ReviewRepository(session).version_view(protocol.version_id)
        assert version.body.target is not None
        start = version.body.target.target_start_at
        matched = []
        complete = False
        try:
            with httpx.Client(
                timeout=20, trust_env=False, headers={"User-Agent": "FutureOS-M3-resolution/0.4"}
            ) as client:
                # Exhaust all pages: ordering by creation can differ from publication ordering.
                for page in range(1, 11):
                    response = client.get(URL, params={"per_page": 100, "page": page})
                    response.raise_for_status()
                    records = response.json()
                    if not isinstance(records, list):
                        raise ValueError("Invalid release response")
                    for record in records:
                        if record["draft"] or record["prerelease"] or not record["published_at"]:
                            continue
                        published = datetime.fromisoformat(
                            record["published_at"].replace("Z", "+00:00")
                        )
                        if start <= published <= protocol.due_at:
                            matched.append(
                                {
                                    key: record[key]
                                    for key in ("id", "tag_name", "published_at", "html_url")
                                }
                            )
                    if len(records) < 100:
                        complete = True
                        break
        except (httpx.HTTPError, ValueError, KeyError):
            complete = False
        if not complete:
            result = ReviewRepository(session).resolve(
                identifier,
                ResolveRequestV1(
                    unavailable_reason=(
                        "Official GitHub API unavailable or pagination "
                        "incomplete; not scored as failure/success"
                    )
                ),
            )
        else:
            now = datetime.now(UTC)
            evidence = EvidenceRepository(session)
            source = evidence.ingest(
                SourceImportV1.model_validate(
                    {
                        "url": URL,
                        "title": "Pre-registered release-window observation",
                        "publisher": "Microsoft Playwright",
                        "source_type": "official",
                        "published_at": now,
                        "availability_basis": "observed_now",
                        "content": json.dumps(
                            {
                                "window_start": start.isoformat(),
                                "window_end": protocol.due_at.isoformat(),
                                "matched_release_count": len(matched),
                                "matched_releases": matched,
                                "pagination_complete": True,
                            },
                            sort_keys=True,
                        ),
                        "usage_permission": "authorized_full",
                        "license_note": (
                            "Own structured observation of public factual GitHub metadata"
                        ),
                        "reliability_note": (
                            "Measures public-release existence only, not ta"
                            "sk reliability or adoption"
                        ),
                        "domain_tags": ["technology"],
                        "label": "REAL",
                        "claims": [],
                    }
                ),
                ADMIN_ID,
            )
            indicator = evidence.indicator(
                IndicatorImportV1(
                    code=protocol.metric_definition,
                    name="Public stable-release event",
                    provider="github-public-api",
                    geo_scope=protocol.geography,
                    unit=protocol.unit,
                    frequency="irregular",
                    definition_version="m3-forward-v1",
                    label="REAL",
                )
            )
            observation = evidence.observation(
                indicator.indicator_id,
                ObservationImportV1(
                    source_version_id=source.version.source_version_id,
                    period_start=start,
                    period_end=protocol.due_at,
                    value=1 if matched else 0,
                    published_at=now,
                    available_at=source.version.available_at,
                    revision_number=1,
                    quality_flag="VERIFIED",
                    definition_note=(
                        "Frozen inclusive window, non-draft and non-pre"
                        "release; complete public pagination"
                    ),
                ),
            )
            result = ReviewRepository(session).resolve(
                identifier, ResolveRequestV1(observation_id=observation.observation_id)
            )
        print(result.model_dump_json(indent=2))
    engine.dispose()


if __name__ == "__main__":
    main()
