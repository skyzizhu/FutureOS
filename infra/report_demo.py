"""Current-time, explicitly synthetic catalog; every entry passes the ordinary M2/M3 gates."""

import fcntl
from datetime import timedelta
from pathlib import Path

from prediction_engine.contracts.models import (
    HistoricalCaseImportV1,
    PublishRequestV1,
    ResearchSnapshotV1,
    ResearchSubmitV1,
    SignalImportV1,
    SourceImportV1,
)
from prediction_engine.evidence.temporal import utc
from prediction_engine.forecasting.workflow import build_forecast_draft, mock_narrative
from sqlalchemy import select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from infra.db import (
    ForecastDraft,
    InboxProcessed,
    Job,
    OutboxEvent,
    ReportCatalogEntry,
    ResearchRun,
    utcnow,
)
from infra.evidence_repository import EvidenceError, EvidenceRepository
from infra.research_repository import ResearchRepository, engine_code_hash
from infra.review_repository import ReviewRepository
from infra.settings import Settings
from scripts.seed_demo import ADMIN_ID

CATALOG = (
    ("technology", "technology"),
    ("manufacturing", "industry"),
    ("healthcare", "health"),
    ("education", "education"),
    ("finance", "macro_finance"),
    ("services", "consumption"),
    ("logistics", "supply_chain"),
    ("energy", "energy"),
    ("society", "society"),
)


def seed_input(session: Session, code: str, domain: str) -> ResearchSubmitV1:
    repo = EvidenceRepository(session)
    now = utcnow()
    signals = []
    sources = []
    for index, capability in enumerate(
        ("context_understanding", "tool_execution", "feedback_validation", "reliability_risk")
    ):
        content = (
            f"DEMO {code} independent synthetic component {capability}; no real-world evidence."
        )
        result = repo.ingest(
            SourceImportV1.model_validate(
                {
                    "url": f"https://example.invalid/m4/{code}/{capability}",
                    "title": f"DEMO {code} {capability}",
                    "publisher": f"Own synthetic observer {index}",
                    "source_type": "manual",
                    "published_at": now - timedelta(days=2),
                    "available_at": now - timedelta(days=2),
                    "availability_basis": "verified_archive",
                    "availability_note": (
                        "Owned current-time synthetic fixture, not a historical archive"
                    ),
                    "content": content,
                    "usage_permission": "authorized_full",
                    "license_note": "Own synthetic material",
                    "reliability_note": "DEMO only; not real claims about the sector",
                    "domain_tags": [domain],
                    "label": "DEMO",
                    "claims": [
                        {
                            "claim_text": content,
                            "quote": content,
                            "source_locator": "fixture paragraph 1",
                            "relation": "contradicts" if index == 3 else "supports",
                            "claim_kind": "fact",
                            "verification_status": "verified",
                            "verification_note": "Synthetic literal matched",
                            "scope": "DEMO " + code,
                        }
                    ],
                }
            ),
            ADMIN_ID,
        )
        sources.append(result)
        signal = repo.create_signal(
            SignalImportV1.model_validate(
                {
                    "headline": content,
                    "claim_ids": result.claim_ids,
                    "mechanism_tags": [capability],
                    "domain_tags": [domain],
                }
            )
        )
        signals.append(signal.signal_id)
    cases = []
    for index, category in ((0, "success"), (3, "failure")):
        cases.append(
            repo.historical_case(
                HistoricalCaseImportV1.model_validate(
                    {
                        "title": f"DEMO {code} {category} case",
                        "cutoff_at": now - timedelta(days=1),
                        "domain_tags": [domain],
                        "mechanism_tags": ["complementarity", "adoption"],
                        "initial_conditions": "Owned synthetic pilot; not sector observations",
                        "limitations": [
                            "Synthetic analogy only; no real success probability or causal claim"
                        ],
                        "label": "DEMO",
                        "events": [
                            {
                                "text": "DEMO pilot initial state",
                                "known_at": now - timedelta(days=2),
                                "source_version_id": sources[index].version.source_version_id,
                                "data_role": "contemporaneous",
                            },
                            {
                                "text": "DEMO " + category,
                                "known_at": now - timedelta(hours=1),
                                "source_version_id": sources[index].version.source_version_id,
                                "data_role": "outcome",
                                "outcome_category": category,
                            },
                        ],
                    }
                )
            )
        )
    return ResearchSubmitV1.model_validate(
        {
            "title": "DEMO M4 " + code + " workflow milestone",
            "scope": "Synthetic " + code + " task workflow only; no claim of personal benefit",
            "domain_tags": [domain],
            "research_as_of": now,
            "signal_ids": signals,
            "historical_case_ids": cases,
            "target": {
                "target_type": "milestone",
                "population_scope": "DEMO " + code + " isolated trial",
                "geography": "global",
                "metric_definition": "demo_" + code + "_verified_workflow",
                "direction_or_threshold": ">=1 completed_milestone",
                "baseline": "Synthetic initial state: no milestone",
                "target_start_at": now + timedelta(days=1),
                "target_end_at": now + timedelta(days=90),
                "resolution_source": f"https://example.invalid/m4/{code}/resolution",
                "resolution_rule": (
                    "Own synthetic trial, same scope and verification"
                    "; missing data stays unresolved"
                ),
            },
            "provider": "mock",
            "label": "DEMO",
        }
    )


def ensure_demo_catalog(engine: Engine, config: Settings, domains: tuple[str, ...] = ()) -> None:
    # Native single-host deployment: lock covers only cheap local Mock bootstrap, no network.
    folder = Path(config.profile_key_path).parent
    folder.mkdir(parents=True, exist_ok=True)
    with (folder / "report-catalog.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        selected = sorted(CATALOG, key=lambda entry: entry[1] not in domains)[:3]
        for code, domain in selected:
            with Session(engine) as session:
                if session.get(ReportCatalogEntry, code):
                    continue
                key = "m4-catalog-v1:" + code
                prior = session.scalar(
                    select(Job).where(Job.user_id == ADMIN_ID, Job.idempotency_key == key)
                )
                if prior:
                    run = session.scalar(select(ResearchRun).where(ResearchRun.job_id == prior.id))
                    assert run is not None
                    run_id = run.id
                    job_id = prior.id
                else:
                    accepted = ResearchRepository(session).submit(
                        seed_input(session, code, domain), ADMIN_ID, key, config
                    )
                    run_id = accepted.run_id
                    job_id = accepted.job_id
                job = session.scalar(select(Job).where(Job.id == job_id).with_for_update())
                assert job is not None
                if job.status == "running" and job.lease_until and utc(job.lease_until) > utcnow():
                    raise EvidenceError("CATALOG_BUSY", "共享合成资料正在准备，请重试", 503)
                row = session.scalar(
                    select(ForecastDraft).where(
                        ForecastDraft.run_id == run_id, ForecastDraft.draft_sequence == "A"
                    )
                )
                if row is None:
                    run = session.get(ResearchRun, run_id)
                    assert run is not None
                    if run.engine_code_hash != engine_code_hash():
                        raise EvidenceError(
                            "CATALOG_ENGINE_CHANGED",
                            "合成目录的冻结引擎已变更，须管理员显式更新目录版本",
                            409,
                        )
                    snapshot = ResearchSnapshotV1.model_validate(run.snapshot)
                    draft = build_forecast_draft(
                        run_id, snapshot, mock_narrative(snapshot), "mock-research-v1"
                    )
                    result = ResearchRepository(session).persist_draft(run_id, draft)
                    job.result = result.model_dump(mode="json")
                    job.attempts += 1
                    requested = session.scalar(
                        select(OutboxEvent).where(
                            OutboxEvent.job_id == job_id,
                            OutboxEvent.event_type == "M2ResearchRequested.v1",
                        )
                    )
                    if (
                        requested
                        and session.get(InboxProcessed, ("m2-research", requested.id)) is None
                    ):
                        session.add(InboxProcessed(consumer="m2-research", event_id=requested.id))
                    session.add(
                        OutboxEvent(
                            job_id=job_id,
                            event_type="M2DraftFrozen.v1",
                            payload={"job_id": str(job_id), "label": "DEMO"},
                        )
                    )
                    job.status = "succeeded"
                    job.lease_token = None
                    job.lease_until = None
                    session.commit()
                    draft_id = draft.draft_id
                else:
                    draft_id = row.id
                review = ReviewRepository(session).review(draft_id)
                if not review.decision.publication_allowed:
                    raise EvidenceError("DEMO_CATALOG_REVIEW_BLOCKED", "合成资料未通过审查", 409)
                version = ReviewRepository(session).publish(
                    draft_id,
                    PublishRequestV1(
                        review_id=review.report.critic_run_id,
                        change_reason=(
                            "M4 shared synthetic report catalog; no external "
                            "research or real prediction"
                        ),
                    ),
                )
                session.add(ReportCatalogEntry(code=code, forecast_version_id=version.version_id))
                session.commit()
