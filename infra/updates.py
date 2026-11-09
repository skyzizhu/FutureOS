"""Free updates only for a report's original world topics; immutable private versions."""

from typing import Any
from uuid import UUID, uuid5

from prediction_engine.contracts.models import PrivateReportV1, UserReportResultV1
from prediction_engine.evidence.temporal import utc
from prediction_engine.forecasting.workflow import hashed
from prediction_engine.reporting.builder import build_private_report
from sqlalchemy import select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from infra.accounts import vault_for
from infra.db import (
    ForecastVersion,
    InAppNotification,
    Job,
    MonitorRun,
    OutboxEvent,
    PersonalImpact,
    Recommendation,
    ReportRefresh,
    ReportVersionForecast,
    UserReport,
    UserReportVersion,
    WorldForecast,
)
from infra.evidence_repository import EvidenceError
from infra.profiles import ProfileRepository
from infra.reports import ReportRepository
from infra.settings import Settings


def queue_refresh(
    session: Session,
    config: Settings,
    user_id: UUID,
    report_id: UUID,
    reason: str,
    monitor_run_id: UUID | None = None,
) -> dict[str, Any]:
    report = session.scalar(
        select(UserReport)
        .where(UserReport.id == report_id, UserReport.user_id == user_id)
        .with_for_update()
    )
    if report is None:
        raise EvidenceError("REPORT_NOT_FOUND", "报告不存在", 404)
    old = ReportRepository(session, config).report(user_id, report_id)
    profile = ProfileRepository(session, config).view(user_id)
    # Original report topics remain the boundary even after profile edits.
    ids = []
    for identifier in old.forecast_version_ids:
        version = session.get(ForecastVersion, identifier)
        assert version is not None
        world = session.get(WorldForecast, version.forecast_id)
        assert world is not None
        ids.append(str(world.current_version_id or identifier))
    key = hashed(
        [str(report_id), str(report.current_version_id), profile.revision, ids, str(monitor_run_id)]
    )
    prior = session.scalar(
        select(ReportRefresh).where(
            ReportRefresh.report_id == report_id, ReportRefresh.input_hash == key
        )
    )
    if prior:
        return {"job_id": prior.job_id, "unchanged": False, "deduplicated": True}
    if (
        ids == [str(i) for i in old.forecast_version_ids]
        and profile.revision == old.profile_revision
        and monitor_run_id is None
    ):
        return {"unchanged": True}
    snapshot = ProfileRepository(session, config).snapshot(user_id)
    job = Job(
        user_id=user_id,
        task_type="m5_report_refresh",
        idempotency_key="m5-report:" + key,
        input_hash=key,
        payload={"label": old.label},
    )
    session.add(job)
    session.flush()
    session.add(
        ReportRefresh(
            job_id=job.id,
            user_id=user_id,
            report_id=report_id,
            old_report_version_id=report.current_version_id,
            profile_snapshot_id=snapshot.snapshot_id,
            monitor_run_id=monitor_run_id,
            forecast_version_ids=ids,
            input_hash=key,
            reason=reason,
        )
    )
    session.add(
        OutboxEvent(
            job_id=job.id,
            event_type="UserImpactChanged.v1",
            payload={"report_id": str(report_id), "job_id": str(job.id), "label": old.label},
        )
    )
    return {"job_id": job.id, "unchanged": False, "deduplicated": False}


def queue_affected_reports(session: Session, run: MonitorRun, config: Settings) -> int:
    refs = session.execute(
        select(UserReport.id, UserReport.user_id)
        .join(
            ReportVersionForecast,
            ReportVersionForecast.report_version_id == UserReport.current_version_id,
        )
        .join(ForecastVersion, ForecastVersion.id == ReportVersionForecast.forecast_version_id)
        .where(ForecastVersion.forecast_id == run.forecast_id)
    ).all()
    count = 0
    for report_id, user_id in refs:
        result = queue_refresh(
            session,
            config,
            user_id,
            report_id,
            "原主题 " + run.decision["level"] + " 复查：证据/条件更新；不扩展新主题",
            run.id,
        )
        count += not result.get("unchanged", False) and not result.get("deduplicated", False)
    return count


def execute_refresh(engine: Engine, job_id: UUID, config: Settings) -> PrivateReportV1:
    with Session(engine) as session:
        request = session.get(ReportRefresh, job_id)
        if request is None:
            raise ValueError("REPORT_REFRESH_MISSING")
        old = ReportRepository(session, config).report(
            request.user_id, request.report_id, request.old_report_version_id
        )
        snapshot = ProfileRepository(session, config).read_snapshot(
            request.profile_snapshot_id, request.user_id
        )
        forecasts = tuple(
            ReportRepository(session, config).public_forecast(UUID(i), request.user_id, old.label)
            for i in request.forecast_version_ids
        )
        body = build_private_report(
            request.report_id,
            uuid5(job_id, "report-refresh"),
            snapshot,
            forecasts,
            utc(request.created_at),
        )
        return body.model_copy(
            update={
                "version_num": old.version_num + 1,
                "previous_report_version_id": old.report_version_id,
                "change_summary": (
                    request.reason,
                    "旧报告及原世界版本保留；本次复查不消耗首次免费额度",
                ),
            }
        )


def persist_refresh(
    session: Session, job_id: UUID, body: PrivateReportV1, config: Settings
) -> UserReportResultV1:
    request = session.get(ReportRefresh, job_id)
    assert request is not None
    report = session.scalar(
        select(UserReport).where(UserReport.id == request.report_id).with_for_update()
    )
    assert report is not None
    if report.current_version_id != request.old_report_version_id:
        raise ValueError("REPORT_REFRESH_BASE_CHANGED")
    if (
        body.user_id != request.user_id
        or body.profile_snapshot_id != request.profile_snapshot_id
        or set(str(i) for i in body.forecast_version_ids) != set(request.forecast_version_ids)
    ):
        raise ValueError("REPORT_REFRESH_INPUT_MISMATCH")
    from infra.monitoring import pending_notice

    blocked = any(
        pending_notice(session, version.forecast_id) is not None
        for identifier in body.forecast_version_ids
        if (version := session.get(ForecastVersion, identifier)) is not None
    )
    if blocked:
        body = body.model_copy(
            update={
                "recommendations": tuple(
                    action.model_copy(update={"priority": "observe"})
                    for action in body.recommendations
                ),
                "evidence_gaps": (
                    *body.evidence_gaps,
                    "原世界预测关键证据待核实，未发布新结论；请保留观察",
                ),
            }
        )
    current = ProfileRepository(session, config).view(body.user_id).profile
    pinned = ProfileRepository(session, config).read_snapshot(
        body.profile_snapshot_id, body.user_id
    )
    if pinned.profile.use_optional_fields and not current.use_optional_fields:
        raise ValueError("REPORT_CONSENT_WITHDRAWN")
    vault = vault_for(session, config)
    session.add(
        UserReportVersion(
            id=body.report_version_id,
            report_id=body.report_id,
            user_id=body.user_id,
            profile_snapshot_id=body.profile_snapshot_id,
            version_num=body.version_num,
            label=body.label,
            ciphertext=vault.seal(
                body.model_dump(mode="json"),
                "report:" + str(body.user_id) + ":" + str(body.report_version_id),
            ),
            immutable_hash=hashed(body.model_dump(mode="json")),
            created_at=body.created_at,
        )
    )
    session.flush()
    session.add_all(
        ReportVersionForecast(report_version_id=body.report_version_id, forecast_version_id=i)
        for i in body.forecast_version_ids
    )
    session.flush()
    for impact in (*body.primary_impacts, *body.observation_only):
        session.add(
            PersonalImpact(
                id=impact.impact_id,
                user_id=body.user_id,
                report_version_id=body.report_version_id,
                profile_snapshot_id=body.profile_snapshot_id,
                forecast_version_id=impact.forecast_version_id,
                ciphertext=vault.seal(
                    impact.model_dump(mode="json"),
                    "impact:" + str(body.user_id) + ":" + str(impact.impact_id),
                ),
            )
        )
    session.flush()
    for action in body.recommendations:
        session.add(
            Recommendation(
                id=action.recommendation_id,
                user_id=body.user_id,
                report_version_id=body.report_version_id,
                impact_id=action.impact_id,
                ciphertext=vault.seal(
                    action.model_dump(mode="json"),
                    "recommendation:" + str(body.user_id) + ":" + str(action.recommendation_id),
                ),
            )
        )
    report.current_version_id = body.report_version_id
    session.add(
        InAppNotification(
            id=uuid5(job_id, "notification"),
            user_id=body.user_id,
            report_id=body.report_id,
            report_version_id=body.report_version_id,
            title="原主题报告有更新",
            summary=request.reason,
        )
    )
    from infra.notifications import queue_eligible_mail

    queue_eligible_mail(session, config, body.user_id, body.report_version_id, "alert")
    return UserReportResultV1(
        report_id=body.report_id, report_version_id=body.report_version_id, label=body.label
    )
