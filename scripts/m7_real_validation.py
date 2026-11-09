"""One bounded REAL provider run over verified public inputs; review only, never auto-publish."""

import json
import time
from datetime import timedelta
from pathlib import Path
from uuid import UUID

from prediction_engine.contracts.models import ResearchSubmitV1
from sqlalchemy.orm import Session

from infra.db import ForecastDraft, Job, ModelCall, ResearchRun, make_engine, utcnow
from infra.research_repository import ResearchRepository
from infra.review_repository import ReviewRepository
from infra.settings import Settings
from scripts.seed_demo import ADMIN_ID

OUTPUT = Path("docs/milestones/evidence/M7-real-validation.json")


def main() -> None:
    if OUTPUT.exists():
        print("Existing M7 real validation retained; no automatic paid rerun")
        return
    config = Settings()
    engine = make_engine(config.database_url)
    report: dict[str, object] = {
        "label": "REAL",
        "purpose": "bounded live provider/critic validation, not accuracy",
        "max_output_tokens": 4096,
        "external_model_calls_requested": 0,
        "auto_publish": False,
        "independent_human_review": False,
        "real_forward_accuracy": None,
    }
    with Session(engine) as session:
        saved = json.loads(Path("docs/evaluations/M3-forward-registration.json").read_text())
        original = session.get(ResearchRun, UUID(saved["run_id"]))
        if original is None or not config.live_research_enabled or config.deepseek_api_key is None:
            report["status"] = "blocked_missing_frozen_real_inputs_or_provider_configuration"
            OUTPUT.write_text(json.dumps(report, indent=2))
            return
        old = ResearchSubmitV1.model_validate(original.snapshot["request"])
        assert old.target is not None
        now = utcnow()
        target = old.target.model_copy(
            update={
                "target_start_at": now + timedelta(hours=1),
                "target_end_at": now + timedelta(days=30),
            }
        )
        request = old.model_copy(
            update={
                "title": "M7 bounded REAL release-window validation",
                "research_as_of": now,
                "target": target,
                "provider": "deepseek",
            }
        )
        accepted = ResearchRepository(session).submit(
            request, ADMIN_ID, "m7-one-real-validation", config
        )
        report.update(
            {
                "job_id": str(accepted.job_id),
                "run_id": str(accepted.run_id),
                "research_as_of": now.isoformat(),
                "external_model_calls_requested": 1,
                "source_basis": (
                    "previously verified frozen public inputs; no claim of refreshed news"
                ),
                "status": "queued",
            }
        )
        OUTPUT.write_text(json.dumps(report, indent=2))
    # The ordinary worker alone owns the lease and durable model-call reservation.
    for _ in range(110):
        with Session(engine) as session:
            job = session.get(Job, accepted.job_id)
            assert job is not None
            if job.status in {"succeeded", "failed_terminal", "cancelled"}:
                report["job_status"] = job.status
                report["error_code"] = job.error_code
                call = session.get(ModelCall, accepted.run_id)
                report["model_call_status"] = call.status if call else None
                report["usage"] = call.usage if call else None
                report["model_id"] = call.model_id if call else None
                if job.status == "succeeded":
                    draft = session.get(ForecastDraft, UUID(job.result["draft_id"]))
                    assert draft is not None
                    reviewed = ReviewRepository(session).review(draft.id)
                    replay = ResearchRepository(session).replay(accepted.run_id)
                    report.update(
                        {
                            "status": "reviewed_internal",
                            "critic_decision": reviewed.decision.decision,
                            "critic_publication_allowed": reviewed.decision.publication_allowed,
                            "findings": [
                                {"code": f.code, "severity": f.severity}
                                for f in reviewed.report.findings
                            ],
                            "offline_replay_identical": replay.identical,
                            "new_public_version_created": False,
                        }
                    )
                else:
                    report["status"] = "provider_or_pipeline_failed_no_auto_retry"
                OUTPUT.write_text(json.dumps(report, indent=2))
                break
        time.sleep(1)
    else:
        report["status"] = "pending_or_uncertain_inspect_existing_job_no_auto_retry"
        OUTPUT.write_text(json.dumps(report, indent=2))
    engine.dispose()
    print("M7 REAL validation recorded; no accuracy claim or automatic publication")


if __name__ == "__main__":
    main()
