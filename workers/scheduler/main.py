"""Native bounded local watcher. Email preferences never control world review scheduling."""

import argparse
import logging
import time
from datetime import timedelta

from prediction_engine.contracts.models import MonitorCheckRequestV1, MonitorPolicyV1
from prediction_engine.evidence.temporal import utc
from sqlalchemy import delete, select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from infra.db import (
    AuthAccessEvent,
    ForecastMonitor,
    ForecastVersion,
    ReportVersionForecast,
    UserReport,
    WorldForecast,
    make_engine,
    utcnow,
)
from infra.evidence_repository import EvidenceError
from infra.monitoring import MonitorRepository
from infra.notifications import queue_eligible_mail
from infra.paid_research import schedule_paid
from infra.settings import Settings, get_settings
from infra.updates import queue_refresh


def tick(engine: Engine, config: Settings) -> dict[str, int]:
    if not config.scheduler_enabled:
        return {"checked": 0, "queued": 0, "errors": 0}
    checked = queued = errors = 0
    with Session(engine) as session:
        session.execute(
            delete(AuthAccessEvent).where(
                AuthAccessEvent.created_at
                < utcnow() - timedelta(days=config.auth_access_retention_days)
            )
        )
        session.commit()
        ids = list(
            session.scalars(
                select(WorldForecast.id)
                .where(WorldForecast.current_version_id.is_not(None))
                .order_by(WorldForecast.id)
                .limit(100)
            )
        )
    for identifier in ids:
        with Session(engine) as session:
            repo = MonitorRepository(session, config)
            monitor = repo.enroll(identifier)
            session.commit()
            if monitor.next_check_at and utc(monitor.next_check_at) > utcnow():
                continue
            checked += 1
            try:
                result = repo.enqueue(identifier, MonitorCheckRequestV1(), automatic=True)
                queued += bool(result.get("job_id") and not result.get("deduplicated"))
            except Exception as exc:
                session.rollback()
                failed_monitor = session.get(ForecastMonitor, identifier)
                if failed_monitor:
                    policy = MonitorPolicyV1.model_validate(failed_monitor.policy)
                    failed_monitor.last_error = (
                        exc.code if isinstance(exc, EvidenceError) else "MONITOR_SCAN_FAILED"
                    )
                    failed_monitor.next_check_at = utcnow() + timedelta(
                        seconds=policy.interval_seconds
                    )
                    session.commit()
                errors += 1
    with Session(engine) as session:
        for report in session.scalars(
            select(UserReport).where(UserReport.current_version_id.is_not(None)).limit(200)
        ):
            if report.current_version_id:
                versions = session.scalars(
                    select(ForecastVersion)
                    .join(
                        ReportVersionForecast,
                        ReportVersionForecast.forecast_version_id == ForecastVersion.id,
                    )
                    .where(ReportVersionForecast.report_version_id == report.current_version_id)
                ).all()
                stale = any(
                    (
                        (world := session.get(WorldForecast, v.forecast_id)) is not None
                        and world.current_version_id != v.id
                    )
                    for v in versions
                )
                if stale:
                    with session.begin_nested():
                        queue_refresh(
                            session,
                            config,
                            report.user_id,
                            report.id,
                            "原主题版本已更新：免费追赶复查，不新增主题",
                        )
                queue_eligible_mail(
                    session, config, report.user_id, report.current_version_id, "digest"
                )
        session.commit()
    paid = schedule_paid(engine, config)
    return {
        "checked": checked,
        "queued": queued + paid["queued"],
        "errors": errors + paid["errors"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()
    config = get_settings()
    engine = make_engine(config.database_url)
    while True:
        try:
            tick(engine, config)
        except Exception:
            logging.getLogger(__name__).error("SCHEDULER_TICK_FAILED")
        if args.once:
            return
        time.sleep(max(5, config.scheduler_tick_seconds))


if __name__ == "__main__":
    main()
