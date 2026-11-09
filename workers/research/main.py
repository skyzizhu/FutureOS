import argparse
import asyncio
import logging
import time
import traceback
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import UUID, uuid4

import redis
from prediction_engine.contracts.models import M2DraftV1, PrivateReportV1
from prediction_engine.contracts.providers import LLMProvider, SearchProvider
from prediction_engine.evidence.temporal import utc
from prediction_engine.forecasting.demo import research_demo
from sqlalchemy import and_, or_, select, update
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from infra.billing import BillingRepository
from infra.chat_research import CHAT_RESEARCH_TASK, execute_chat_research, persist_chat_research
from infra.costs import record_cost
from infra.db import (
    InboxProcessed,
    Job,
    ModelCall,
    OutboxEvent,
    PaidResearchRequest,
    UserResearchTopic,
    make_engine,
    utcnow,
)
from infra.evidence_repository import EvidenceError
from infra.monitoring import MonitorRepository
from infra.notifications import dispatch_local
from infra.paid_research import persist_paid, prepare_paid
from infra.providers import mock_providers
from infra.providers.policy import ProviderRunner, ProviderUnavailable
from infra.reports import ReportRepository, execute_report
from infra.research_repository import ResearchRepository
from infra.settings import Settings, get_settings
from infra.updates import execute_refresh, persist_refresh
from workers.research.m2 import execute_m2

logger = logging.getLogger("futureos.worker")


def run_once(
    engine: Engine,
    config: Settings,
    search: SearchProvider | None = None,
    llm: LLMProvider | None = None,
) -> bool:
    started = time.monotonic()
    now = utcnow()
    eligible = or_(
        and_(Job.status.in_(["queued", "failed_retryable"]), Job.available_at <= now),
        and_(Job.status == "running", Job.lease_until < now),
    )
    token = uuid4()
    # Portable compare-and-set claim: PostgreSQL for deployment, SQLite for fast tests.
    # Only the winning lease holder may commit output; duplicate delivery is harmless.
    with Session(engine, expire_on_commit=False) as session:
        exhausted_jobs = session.execute(
            select(Job.id, Job.user_id, Job.task_type)
            .where(eligible, Job.attempts >= config.job_max_attempts)
            .order_by(Job.user_id, Job.id)
        ).all()
        for exhausted_id, exhausted_user, exhausted_type in exhausted_jobs:
            if exhausted_type in {"m4_report", "m6_research"}:
                BillingRepository(session, config).lock_user(exhausted_user)
            if exhausted_type == "m4_report":
                ReportRepository(session, config).release(exhausted_id)
            elif exhausted_type == "m6_research":
                BillingRepository(session, config).release(exhausted_id)
        session.execute(
            update(Job)
            .execution_options(synchronize_session=False)
            .where(eligible, Job.attempts >= config.job_max_attempts)
            .values(
                status="failed_terminal",
                error_code="JOB_RETRY_EXHAUSTED",
                lease_token=None,
                lease_until=None,
                updated_at=now,
            )
        )
        candidate = session.scalar(
            select(Job.id)
            .where(eligible, Job.attempts < config.job_max_attempts)
            .order_by(Job.created_at)
            .limit(1)
        )
        if candidate is None:
            session.commit()
            return False
        claimed = session.connection().execute(
            update(Job)
            .where(Job.id == candidate, eligible, Job.attempts < config.job_max_attempts)
            .values(
                status="running",
                attempts=Job.attempts + 1,
                lease_token=token,
                lease_until=now + timedelta(seconds=max(config.job_lease_seconds, 150)),
                updated_at=now,
            )
        )
        session.commit()
        if claimed.rowcount != 1:
            return False
        job = session.get(Job, candidate)
        assert job is not None
        job_id, trace_id, payload, attempt = job.id, job.trace_id, job.payload, job.attempts
        task_type = job.task_type
    result = None
    error_code = None
    retryable = False
    demo_search, demo_llm = mock_providers()

    async def execute() -> dict[str, object]:
        if task_type == CHAT_RESEARCH_TASK:
            return await execute_chat_research(engine, config, job_id, token)
        if task_type == "m6_research":
            prepare_paid(engine, job_id, config)
            return {"prepared": True}
        if task_type in {"m5_monitor", "m5_mail"}:
            return {"prepared": True}
        if task_type == "m5_report_refresh":
            return execute_refresh(engine, job_id, config).model_dump(mode="json")
        if task_type == "m4_report":
            report = execute_report(engine, job_id, config)
            return report.model_dump(mode="json")
        if task_type == "m2_research":
            draft = await execute_m2(engine, UUID(payload["run_id"]), config)
            return draft.model_dump(mode="json")
        output = await ProviderRunner().call(
            lambda: research_demo(
                payload["question"], now, str(trace_id), search or demo_search, llm or demo_llm
            )
        )
        return output.model_dump(mode="json")

    try:
        result = asyncio.run(execute())
    except ProviderUnavailable:
        error_code, retryable = "PROVIDER_UNAVAILABLE", True
    except ValueError as exc:
        code = str(exc)
        error_code = (
            code
            if task_type
            in {
                "m2_research",
                "m4_report",
                "m5_monitor",
                "m5_report_refresh",
                "m5_mail",
                "m6_research",
                CHAT_RESEARCH_TASK,
            }
            and code.replace("_", "").isalnum()
            and len(code) < 100
            else "EVIDENCE_UNVERIFIED"
        )
    except Exception as exc:
        frames = [
            (Path(frame.filename).name, frame.lineno, frame.name)
            for frame in traceback.extract_tb(exc.__traceback__)
        ]
        logging.getLogger(__name__).error(
            "JOB_EXECUTION_FAILED type=%s task=%s frames=%s", type(exc).__name__, task_type, frames
        )
        error_code = "JOB_FAILED"
    with Session(engine) as session:
        if task_type in {
            "m4_report",
            "m5_report_refresh",
            "m5_mail",
            "m6_research",
            CHAT_RESEARCH_TASK,
        }:
            owner_id = session.scalar(select(Job.user_id).where(Job.id == job_id))
            if owner_id is not None:
                BillingRepository(session, config).lock_user(owner_id)
        # Lease fencing: a slow/crashed worker cannot overwrite a newer attempt's output.
        current = session.scalar(select(Job).where(Job.id == job_id).with_for_update())
        if current is None or current.lease_token != token or current.status != "running":
            return True
        if result and task_type == "m2_research":
            draft = M2DraftV1.model_validate(result)
            outcome = ResearchRepository(session).persist_draft(draft.run_id, draft)
            result = outcome.model_dump(mode="json")
        if result and task_type == CHAT_RESEARCH_TASK:
            try:
                with session.begin_nested():
                    persist_chat_research(session, config, current, result)
                    result = {"label": "DEMO"}
                    session.add(
                        OutboxEvent(
                            job_id=job_id,
                            event_type="ChatIndustryResearchCompleted.v1",
                            payload={"job_id": str(job_id), "label": "DEMO"},
                        )
                    )
            except (EvidenceError, ValueError):
                result, error_code = None, "CHAT_RESEARCH_RESULT_REJECTED"
        if result and task_type == "m4_report":
            try:
                with session.begin_nested():
                    outcome4 = ReportRepository(session, config).persist(
                        job_id, PrivateReportV1.model_validate(result)
                    )
                    result = outcome4.model_dump(mode="json")
            except Exception:
                result = None
                error_code = "REPORT_PERSIST_FAILED"
                retryable = False
        if result and task_type.startswith("m5_"):
            try:
                with session.begin_nested():
                    if task_type == "m5_monitor":
                        result = (
                            MonitorRepository(session, config)
                            .persist(job_id)
                            .model_dump(mode="json")
                        )
                    elif task_type == "m5_report_refresh":
                        result = persist_refresh(
                            session, job_id, PrivateReportV1.model_validate(result), config
                        ).model_dump(mode="json")
                    elif task_type == "m5_mail":
                        result = dispatch_local(session, job_id, config)
            except Exception:
                result = None
                error_code = "M5_PERSIST_FAILED"
                retryable = False
        if result and task_type == "m6_research":
            try:
                with session.begin_nested():
                    result = persist_paid(session, job_id, config).model_dump(mode="json")
            except Exception as exc:
                logger.error("PAID_RESEARCH_PERSIST_FAILED type=%s", type(exc).__name__)
                result = None
                error_code = (
                    str(exc)
                    if isinstance(exc, (ValueError, EvidenceError))
                    and str(exc).replace("_", "").isalnum()
                    and len(str(exc)) < 100
                    else "PAID_RESEARCH_FAILED"
                )
                retryable = False
        if not result and task_type == "m5_mail":
            from infra.db import MailAttempt, MailDelivery

            delivery = session.scalar(select(MailDelivery).where(MailDelivery.job_id == job_id))
            if delivery:
                delivery.status = "uncertain" if delivery.status == "started" else "failed_terminal"
                session.add(
                    MailAttempt(
                        delivery_id=delivery.id, status=delivery.status, error_code=error_code
                    )
                )
        current.result = result
        current.error_code = error_code
        current.status = (
            "succeeded"
            if result
            else "failed_retryable"
            if retryable and attempt < config.job_max_attempts
            else "failed_terminal"
        )
        current.available_at = utcnow() + timedelta(seconds=2**attempt if error_code else 0)
        current.lease_token, current.lease_until = None, None
        current.updated_at = utcnow()
        if task_type == "m4_report" and current.status == "failed_terminal":
            ReportRepository(session, config).release(job_id)
        if task_type == "m6_research" and current.status == "failed_terminal":
            BillingRepository(session, config).release(job_id)
            paid_request = session.get(PaidResearchRequest, job_id)
            topic = (
                session.get(UserResearchTopic, paid_request.user_topic_id) if paid_request else None
            )
            if topic is not None:
                topic.last_error = error_code
        if result and (task_type.startswith("m5_") or task_type == "m6_research"):
            request_event = session.scalar(
                select(OutboxEvent)
                .where(OutboxEvent.job_id == job_id)
                .order_by(OutboxEvent.emitted_at)
                .limit(1)
            )
            if (
                request_event
                and session.get(
                    InboxProcessed,
                    ("m6-worker" if task_type == "m6_research" else "m5-worker", request_event.id),
                )
                is None
            ):
                session.add(
                    InboxProcessed(
                        consumer="m6-worker" if task_type == "m6_research" else "m5-worker",
                        event_id=request_event.id,
                    )
                )
            session.add(
                OutboxEvent(
                    job_id=job_id,
                    event_type="TurningPointReviewed.v1"
                    if task_type == "m5_monitor"
                    else "ReportReady.v1"
                    if task_type in {"m5_report_refresh", "m6_research"}
                    else "MailSuppressed.v1"
                    if result.get("status") == "suppressed"
                    else "MailDelivered.v1",
                    payload={"job_id": str(job_id), "label": payload.get("label", "DEMO")},
                )
            )
        if (
            result
            and not task_type.startswith("m5_")
            and task_type not in {"m6_research", CHAT_RESEARCH_TASK}
        ):
            requested = session.scalar(
                select(OutboxEvent).where(
                    OutboxEvent.job_id == job_id,
                    OutboxEvent.event_type
                    == (
                        "FirstReportRequested.v1"
                        if task_type == "m4_report"
                        else "M2ResearchRequested.v1"
                        if task_type == "m2_research"
                        else "DemoResearchRequested.v1"
                    ),
                )
            )
            if (
                requested
                and session.get(
                    InboxProcessed,
                    (
                        "m4-report"
                        if task_type == "m4_report"
                        else "m2-research"
                        if task_type == "m2_research"
                        else "demo-research",
                        requested.id,
                    ),
                )
                is None
            ):
                session.add(
                    InboxProcessed(
                        consumer="m4-report"
                        if task_type == "m4_report"
                        else "m2-research"
                        if task_type == "m2_research"
                        else "demo-research",
                        event_id=requested.id,
                    )
                )
            session.add(
                OutboxEvent(
                    job_id=job_id,
                    event_type="ReportReady.v1"
                    if task_type == "m4_report"
                    else "M2DraftFrozen.v1"
                    if task_type == "m2_research"
                    else "DemoResearchCompleted.v1",
                    payload={"job_id": str(job_id), "label": payload.get("label", "DEMO")},
                )
            )
        calls = 0
        usage = None
        if task_type == "m2_research" and payload.get("run_id"):
            call = session.get(ModelCall, UUID(payload["run_id"]))
            if call is not None and utc(call.started_at) >= now:
                calls = 1
                usage = call.usage
        record_cost(
            session,
            job_id,
            "incremental_review" if task_type == "m5_monitor" else "execution",
            "attempt:" + str(attempt),
            int((time.monotonic() - started) * 1000),
            external_calls=calls,
            usage=usage,
        )
        session.commit()
        logger.info("job_id=%s status=%s attempt=%s", job_id, current.status, attempt)
    return True


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--heartbeat", action="store_true")
    args = parser.parse_args()
    config = get_settings()
    engine = make_engine(config.database_url)
    cache: redis.Redis = redis.Redis.from_url(
        config.redis_url, socket_timeout=2, socket_connect_timeout=1
    )
    if args.heartbeat:
        stamp = cache.get("futureos:DEMO:worker-heartbeat")
        if (
            not isinstance(stamp, bytes)
            or (datetime.now(UTC) - datetime.fromisoformat(stamp.decode())).total_seconds() > 15
        ):
            raise SystemExit(1)
        return
    while True:
        try:
            cache.set("futureos:DEMO:worker-heartbeat", utcnow().isoformat(), ex=20)
        except redis.RedisError:
            logger.warning("REDIS_HEARTBEAT_UNAVAILABLE_DB_POLLING_CONTINUES")
        worked = run_once(engine, config)
        if args.once:
            return
        if not worked:
            try:
                cache.blpop(["futureos:DEMO:wakeup"], timeout=1)
            except redis.RedisError:
                import time

                time.sleep(1)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
