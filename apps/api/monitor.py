from collections.abc import Callable, Iterator
from datetime import timedelta
from typing import Annotated, Any
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends
from prediction_engine.contracts.models import (
    MonitorCheckRequestV1,
    MonitorPolicyV1,
    SignalImportV1,
    SourceImportV1,
)
from prediction_engine.evidence.temporal import utc
from sqlalchemy import select
from sqlalchemy.orm import Session

from infra.db import (
    ForecastVersion,
    Job,
    MonitorOutcome,
    MonitorRun,
    User,
    WorldForecast,
    utcnow,
)
from infra.evidence_repository import EvidenceError, EvidenceRepository
from infra.monitoring import MonitorRepository
from infra.settings import Settings


def create_monitor_router(
    db_dependency: Callable[..., Iterator[Session]],
    admin_dependency: Callable[..., User],
    config: Settings,
) -> APIRouter:
    router = APIRouter(prefix="/api/v1/admin/monitor", tags=["M5 monitors"])
    db = Depends(db_dependency)
    admin = Depends(admin_dependency)

    @router.get("/forecasts")
    def forecasts(user: Annotated[User, admin], session: Annotated[Session, db]) -> Any:
        records = []
        for world in session.scalars(
            select(WorldForecast)
            .where(WorldForecast.current_version_id.is_not(None))
            .order_by(WorldForecast.id)
            .limit(100)
        ):
            monitor = MonitorRepository(session, config).enroll(world.id)
            version = session.get(ForecastVersion, world.current_version_id)
            records.append(
                {
                    "forecast_id": world.id,
                    "current_version_id": world.current_version_id,
                    "label": version.label if version else "",
                    "statement": version.statement if version else "",
                    "policy": monitor.policy,
                    "next_check_at": monitor.next_check_at,
                    "cooldown_until": monitor.cooldown_until,
                    "last_error": monitor.last_error,
                }
            )
        session.commit()
        return records

    @router.put("/forecasts/{forecast_id}/policy")
    def policy(
        forecast_id: UUID,
        data: MonitorPolicyV1,
        user: Annotated[User, admin],
        session: Annotated[Session, db],
    ) -> Any:
        if session.get(WorldForecast, forecast_id) is None:
            raise EvidenceError("FORECAST_NOT_FOUND", "预测不存在", 404)
        monitor = MonitorRepository(session, config).enroll(forecast_id)
        previous = MonitorPolicyV1.model_validate(monitor.policy)
        if monitor.cooldown_until and (
            data.cooldown_seconds < previous.cooldown_seconds or data.cooldown_seconds == 0
        ):
            monitor.cooldown_until = min(
                utc(monitor.cooldown_until), utcnow() + timedelta(seconds=data.cooldown_seconds)
            )
        monitor.policy = data.model_dump(mode="json")
        session.commit()
        return monitor.policy

    @router.post("/forecasts/{forecast_id}/check")
    def check(
        forecast_id: UUID,
        data: MonitorCheckRequestV1,
        user: Annotated[User, admin],
        session: Annotated[Session, db],
    ) -> Any:
        return MonitorRepository(session, config).enqueue(forecast_id, data, user.id)

    @router.get("/runs")
    def runs(user: Annotated[User, admin], session: Annotated[Session, db]) -> Any:
        records = []
        for row in session.scalars(
            select(MonitorRun).order_by(MonitorRun.created_at.desc()).limit(100)
        ):
            outcome = session.get(MonitorOutcome, row.id)
            job = session.get(Job, row.job_id)
            records.append(
                {
                    "monitor_run_id": row.id,
                    "forecast_id": row.forecast_id,
                    "old_version_id": row.old_version_id,
                    "decision": row.decision,
                    "created_at": row.created_at,
                    "status": job.status if job else "",
                    "result": outcome.body if outcome else None,
                    "error_code": job.error_code if job else None,
                }
            )
        return records

    @router.post("/forecasts/{forecast_id}/demo-change")
    def demo(
        forecast_id: UUID, user: Annotated[User, admin], session: Annotated[Session, db]
    ) -> Any:
        world = session.get(WorldForecast, forecast_id)
        version = session.get(ForecastVersion, world.current_version_id) if world else None
        if version is None or version.label != "DEMO":
            raise EvidenceError("DEMO_ONLY", "只允许对合成演示创建测试资料", 409)
        original = MonitorRepository(session, config).snapshot_for(version)
        repo = EvidenceRepository(session)
        for index in range(2):
            marker = uuid4().hex
            content = (
                f"DEMO independent follow-up {index} {marker}: "
                "integration cost remains a verified bottleneck."
            )
            result = repo.ingest(
                SourceImportV1.model_validate(
                    {
                        "url": "https://example.invalid/m5/" + marker,
                        "title": "DEMO M5 follow-up",
                        "publisher": "Own independent synthetic observer " + str(index),
                        "source_type": "manual",
                        "availability_basis": "observed_now",
                        "content": content,
                        "usage_permission": "authorized_full",
                        "license_note": "Own synthetic fixture",
                        "reliability_note": "DEMO only",
                        "domain_tags": [tag.value for tag in original.request.domain_tags],
                        "label": "DEMO",
                        "claims": [
                            {
                                "claim_text": content,
                                "quote": content,
                                "source_locator": "fixture paragraph 1",
                                "relation": "contradicts",
                                "claim_kind": "fact",
                                "verification_status": "verified",
                                "verification_note": "Own literal synthetic text checked",
                                "scope": original.request.scope,
                            }
                        ],
                    }
                ),
                user.id,
            )
            repo.create_signal(
                SignalImportV1.model_validate(
                    {
                        "headline": content,
                        "claim_ids": result.claim_ids,
                        "mechanism_tags": ["reliability_risk"],
                        "domain_tags": [tag.value for tag in original.request.domain_tags],
                    }
                )
            )
        return MonitorRepository(session, config).enqueue(
            forecast_id, MonitorCheckRequestV1(), user.id
        )

    return router
