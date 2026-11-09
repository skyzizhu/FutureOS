"""Explicit one-call REAL forward registration. Never rerun a paid request on uncertainty.

Uses primary-source excerpts inspected via the coding agent web tool,
reads current GitHub metadata, retains <=25-word attributed excerpts per article,
uses one bounded DeepSeek generation, then the same M3 checks and publication gate.
The milestone tests release activity only, not general agent capability or accuracy.
"""

import json
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path

import httpx
from dotenv import dotenv_values
from prediction_engine.contracts.models import (
    HistoricalCaseImportV1,
    ResearchSubmitV1,
    SignalImportV1,
    SourceImportV1,
)
from sqlalchemy.orm import Session

from infra.db import make_engine
from infra.evidence_repository import EvidenceRepository
from infra.research_repository import ResearchRepository
from infra.settings import Settings
from scripts.seed_demo import ADMIN_ID

OUTPUT = Path("docs/evaluations/M3-forward-registration.json")
RELEASE_URL = "https://api.github.com/repos/microsoft/playwright/releases"


def main() -> None:
    if OUTPUT.exists():
        raise SystemExit("Forward record exists; use saved run/protocol, no automatic paid re-run")
    config = Settings()
    engine = make_engine(config.database_url)
    with httpx.Client(
        timeout=25, trust_env=False, headers={"User-Agent": "FutureOS-M3-research/0.4"}
    ) as public:
        documents = [
            (
                "https://github.com/google-gemini/gemini-cli",
                "Google Gemini CLI",
                "Provide persistent context to Gemini CLI.",
                "context_understanding",
                "官方 README 描述持久上下文配置；只核实文档声明，不证明通用理解能力",
            ),
            (
                "https://github.com/microsoft/playwright",
                "Microsoft Playwright",
                "Playwright is a framework for web automation and testing.",
                "tool_execution",
                "官方 README 将 Playwright 描述为网页自动化及测试框架；不等于生产可靠性已验证",
            ),
            (
                "https://www.anthropic.com/research/writing-tools-for-agents",
                "Anthropic",
                (
                    "Building an evaluation allows you to systematically measure the "
                    "performance of your tools."
                ),
                "feedback_validation",
                "官方文章描述工具评估方法；不证明因果收益或预测效果",
            ),
            (
                "https://support.google.com/stadia/answer/9578631?hl=en",
                "Google Stadia",
                "the Stadia servers will be turned off on January 18, 2023.",
                "reliability_risk",
                "官方停止服务公告；技术存在不能保证持续采用，跨领域迁移有限",
            ),
        ]
        # Each literal excerpt was inspected in this implementation session using the
        # primary-source web reader. GitHub HTML is not reliably reachable directly here.
        texts = [quote for _, _, quote, _, _ in documents]
        releases = public.get(RELEASE_URL, params={"per_page": 10})
        releases.raise_for_status()
        stable = next(r for r in releases.json() if not r["draft"] and not r["prerelease"])
    signals = []
    source_rows = []
    with Session(engine) as session:
        repo = EvidenceRepository(session)
        for (url, publisher, _, capability, note), excerpt in zip(documents, texts, strict=True):
            ingested = repo.ingest(
                SourceImportV1.model_validate(
                    {
                        "url": url,
                        "title": publisher + " primary-source excerpt",
                        "publisher": publisher,
                        "source_type": "official",
                        "published_at": None,
                        "availability_basis": "observed_now",
                        "availability_note": (
                            "Current retrieval only; no backdated historical availability"
                        ),
                        "content": excerpt,
                        "usage_permission": "excerpt",
                        "license_note": (
                            "Short attributed excerpt, retained for verification with original URL"
                        ),
                        "reliability_note": note,
                        "domain_tags": ["technology"],
                        "label": "REAL",
                        "claims": [
                            {
                                "claim_text": note,
                                "quote": excerpt,
                                "source_locator": (
                                    "literal excerpt checked via primary-source web retrieval"
                                ),
                                "relation": "contradicts"
                                if capability == "reliability_risk"
                                else "supports",
                                "claim_kind": "fact",
                                "verification_status": "verified",
                                "verification_note": (
                                    "Statement checked via primary web retrieval; "
                                    "not independent human semantic verification"
                                ),
                                "scope": (
                                    "Official document statement only; no measured causal effect"
                                ),
                            }
                        ],
                    }
                ),
                ADMIN_ID,
            )
            source_rows.append(ingested)
            signal = repo.create_signal(
                SignalImportV1(
                    headline=note,
                    claim_ids=ingested.claim_ids,
                    mechanism_tags=(capability,),
                    domain_tags=("technology",),
                )
            )
            signals.append(signal.signal_id)
        release_content = json.dumps(
            {
                key: stable[key]
                for key in ("tag_name", "published_at", "html_url", "draft", "prerelease")
            },
            sort_keys=True,
        )
        release_source = repo.ingest(
            SourceImportV1.model_validate(
                {
                    "url": stable["html_url"],
                    "title": "Playwright public stable release metadata",
                    "publisher": "Microsoft Playwright",
                    "source_type": "official",
                    "published_at": stable["published_at"],
                    "availability_basis": "observed_now",
                    "availability_note": "Metadata observed now; no historical archive claim",
                    "content": release_content,
                    "usage_permission": "excerpt",
                    "license_note": "Public GitHub release factual metadata only",
                    "reliability_note": "Release existence is not adoption or task success",
                    "domain_tags": ["technology"],
                    "label": "REAL",
                    "claims": [],
                }
            ),
            ADMIN_ID,
        )
        cases = []
        for source, category, title, scope in [
            (
                release_source,
                "success",
                "Playwright achieved a public stable-release milestone",
                "software_testing",
            ),
            (
                source_rows[-1],
                "failure",
                "Stadia officially announced service shutdown",
                "digital_services",
            ),
        ]:
            cases.append(
                repo.historical_case(
                    HistoricalCaseImportV1.model_validate(
                        {
                            "title": title,
                            "cutoff_at": source.version.available_at,
                            "domain_tags": ["technology"],
                            "mechanism_tags": ["complementarity", "adoption"],
                            "initial_conditions": scope
                            + (
                                "; current official artifact/statement, not a complete causal his"
                                "tory"
                            ),
                            "limitations": [
                                (
                                    "Only artifact/closure outcome is verified; "
                                    "no adoption-effect es"
                                    "timate"
                                ),
                                (
                                    "Different institutions, markets and time horizons; "
                                    "no transferab"
                                    "le success probability"
                                ),
                            ],
                            "label": "REAL",
                            "events": [
                                {
                                    "text": title,
                                    "known_at": source.version.available_at,
                                    "source_version_id": source.version.source_version_id,
                                    "data_role": "contemporaneous",
                                },
                                {
                                    "text": title,
                                    "known_at": datetime.now(UTC),
                                    "source_version_id": source.version.source_version_id,
                                    "data_role": "outcome",
                                    "outcome_category": category,
                                },
                            ],
                        }
                    )
                )
            )
        as_of = datetime.now(UTC)
        start = as_of + timedelta(minutes=15)
        end = start + timedelta(days=30)
        request = ResearchSubmitV1.model_validate(
            {
                "title": "真实前瞻：浏览器自动化工具的公开发布里程碑",
                "scope": (
                    "仅预测 microsoft/playwright 是否出现公开稳定发布，"
                    "不推断就业、生产可靠性或个人行动；文档功能标签为候选机制线索"
                ),
                "domain_tags": ["technology"],
                "research_as_of": as_of,
                "signal_ids": signals,
                "historical_case_ids": cases,
                "provider": "deepseek",
                "label": "REAL",
                "target": {
                    "target_type": "milestone",
                    "population_scope": (
                        "GitHub microsoft/playwright public non-draft non-prerelease releases"
                    ),
                    "geography": "global public repository",
                    "metric_definition": "playwright_stable_release_occurs",
                    "direction_or_threshold": ">=1 binary_event",
                    "baseline": (
                        "No calibrated event baseline; prior stable-release existence is "
                        "context, not a numeric forecast"
                    ),
                    "target_start_at": start,
                    "target_end_at": end,
                    "resolution_source": RELEASE_URL,
                    "resolution_rule": (
                        "After deadline, paginate official GitHub releases until publishe"
                        "d_at is earlier than window start; retain raw metadata hash. Out"
                        "come=1 iff >=1 non-draft, non-prerelease release has published_a"
                        "t in the inclusive frozen window, else 0. Incomplete pagination/"
                        "API outage => unresolved_due_to_data; a missing response is neve"
                        "r 0."
                    ),
                },
            }
        )
        accepted = ResearchRepository(session).submit(
            request, ADMIN_ID, "m3-first-real-forward-v1", config
        )
    report = {
        "run_id": str(accepted.run_id),
        "registered_at": None,
        "status": "awaiting_generation",
        "label": "REAL",
        "purpose": "First real prospective public-release milestone; no accuracy claim",
        "research_as_of": as_of.isoformat(),
        "window_start": start.isoformat(),
        "window_end": end.isoformat(),
        "source_urls": [d[0] for d in documents] + [stable["html_url"]],
        "known_stable_tag": stable["tag_name"],
        "external_model_calls_requested": 1,
        "independent_human_review": False,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    env = dotenv_values(".env")
    headers = {"Authorization": "Bearer " + env.get("DEMO_ADMIN_TOKEN", "demo-admin-local-only")}
    with httpx.Client(
        base_url="http://127.0.0.1:8100", headers=headers, trust_env=False, timeout=25
    ) as client:
        for _ in range(120):
            state = client.get("/api/v1/admin/research/runs/" + str(accepted.run_id))
            state.raise_for_status()
            body = state.json()
            if body["status"] in {"succeeded", "failed_terminal", "cancelled"}:
                break
            time.sleep(1)
        report["status"] = body["status"]
        report["error_code"] = body.get("error_code")
        if body["status"] == "succeeded":
            draft_id = body["draft"]["draft_id"]
            checked = client.post(f"/api/v1/admin/review/drafts/{draft_id}/check", json={})
            checked.raise_for_status()
            review = checked.json()
            report["review_decision"] = review["decision"]["decision"]
            report["review_id"] = review["report"]["critic_run_id"]
            if review["decision"]["publication_allowed"]:
                published = client.post(
                    f"/api/v1/admin/review/drafts/{draft_id}/publish",
                    json={
                        "review_id": report["review_id"],
                        "change_reason": (
                            "First current-time REAL forward milestone, narrow scope and no a"
                            "ccuracy claim"
                        ),
                    },
                )
                published.raise_for_status()
                version = published.json()
                protocol = client.post(
                    f"/api/v1/admin/review/versions/{version['version_id']}/register",
                    json={
                        "mode": "forward",
                        "operator": "gte",
                        "threshold": 1,
                        "unit": "binary_event",
                        "testset_version": "m3-first-forward-v1",
                    },
                )
                protocol.raise_for_status()
                report.update(
                    status="registered_not_due",
                    version_id=version["version_id"],
                    version_hash=version["version_hash"],
                    protocol_id=protocol.json()["protocol_id"],
                    registered_at=protocol.json()["registered_at"],
                    resolution_status="not_due",
                )
        calls = client.get("/api/v1/admin/research/model-calls")
        calls.raise_for_status()
        report["model_calls"] = [
            {k: r.get(k) for k in ("status", "model_id", "usage", "error_code")}
            for r in calls.json()
            if r["run_id"] == str(accepted.run_id)
        ]
    OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    engine.dispose()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if report["status"] != "registered_not_due":
        raise SystemExit("No automatic retry: inspect frozen run and review first")


if __name__ == "__main__":
    main()
