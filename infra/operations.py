"""Read-only quality/queue/release snapshot. No flags or manual approvals are inferred."""

import json
from pathlib import Path
from typing import Any

from prediction_engine.evidence.temporal import utc
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from infra.db import (
    AuthAccount,
    EvaluationProtocol,
    ForecastResolution,
    Job,
    ModelCall,
    ObservationVintage,
    PrivacyErasure,
    ProfileSnapshot,
    SourceVersion,
    WorldForecast,
    utcnow,
)
from infra.review_repository import ReviewRepository
from infra.settings import Settings


def readiness(session: Session, config: Settings) -> dict[str, Any]:
    now = utcnow()
    pending = Job.status.in_(["queued", "running", "failed_retryable"])
    oldest = session.scalar(select(func.min(Job.created_at)).where(pending))
    age = max(0, int((now - utc(oldest)).total_seconds())) if oldest else 0
    expired = (
        session.scalar(
            select(func.count())
            .select_from(Job)
            .where(Job.status == "running", Job.lease_until < now)
        )
        or 0
    )
    errors = (
        session.scalar(select(func.count()).select_from(Job).where(Job.status == "failed_terminal"))
        or 0
    )
    licenses = [
        {"permission": permission, "count": count}
        for permission, count in session.execute(
            select(SourceVersion.usage_permission, func.count()).group_by(
                SourceVersion.usage_permission
            )
        )
    ]
    missing_license = (
        session.scalar(
            select(func.count())
            .select_from(SourceVersion)
            .where(SourceVersion.label == "REAL", SourceVersion.license_note == "")
        )
        or 0
    )
    revisions = session.execute(
        select(
            ObservationVintage.indicator_id,
            ObservationVintage.period_end,
            func.count(func.distinct(ObservationVintage.value)),
        )
        .where(ObservationVintage.label == "REAL")
        .group_by(ObservationVintage.indicator_id, ObservationVintage.period_end)
        .having(func.count(func.distinct(ObservationVintage.value)) > 1)
    ).all()
    integrity = []
    overdue = 0
    for identifier in session.scalars(
        select(WorldForecast.current_version_id)
        .where(WorldForecast.current_version_id.is_not(None))
        .limit(1000)
    ):
        if identifier:
            try:
                version = ReviewRepository(session).version_view(identifier)
                integrity.append({"version_id": str(identifier), "hash_valid": True})
                overdue += version.label == "REAL" and version.body.next_review_at < now
            except Exception:
                integrity.append({"version_id": str(identifier), "hash_valid": False})
    evaluations = []
    for protocol in session.scalars(
        select(EvaluationProtocol).order_by(EvaluationProtocol.due_at).limit(200)
    ):
        last = session.scalar(
            select(ForecastResolution)
            .where(ForecastResolution.protocol_id == protocol.id)
            .order_by(ForecastResolution.checked_at.desc())
            .limit(1)
        )
        state = (
            "not_due"
            if utc(protocol.due_at) > now
            else last.status
            if last
            else "unresolved_due_to_data"
        )
        evaluations.append(
            {
                "protocol_id": str(protocol.id),
                "mode": protocol.mode,
                "label": protocol.label,
                "due_at": utc(protocol.due_at).isoformat(),
                "status": state,
            }
        )
    resurrected = (
        session.scalar(
            select(func.count())
            .select_from(AuthAccount)
            .join(PrivacyErasure, PrivacyErasure.user_id == AuthAccount.user_id)
        )
        or 0
    )
    unscrubbed = (
        session.scalar(
            select(func.count())
            .select_from(ProfileSnapshot)
            .join(PrivacyErasure, PrivacyErasure.user_id == ProfileSnapshot.user_id)
            .where(ProfileSnapshot.ciphertext != "ERASED")
        )
        or 0
    )
    uncertain = (
        session.scalar(
            select(func.count())
            .select_from(ModelCall)
            .where(ModelCall.status.in_(["started", "uncertain"]))
        )
        or 0
    )
    backup_path = Path(".local/m7-restore-drill.json")
    backup = json.loads(backup_path.read_text()) if backup_path.exists() else None
    checks = [
        {
            "name": "published_version_hashes",
            "passed": all(r["hash_valid"] for r in integrity),
            "scope": "latest versions, up to1000",
        },
        {"name": "erasure_no_account_resurrection", "passed": resurrected == 0 and unscrubbed == 0},
        {"name": "queue_age", "passed": age <= config.queue_alert_seconds and expired == 0},
        {"name": "real_model_no_uncertain_call", "passed": uncertain == 0},
        {
            "name": "payment_and_email_closed",
            "passed": not config.live_payments_enabled and not config.live_email_enabled,
        },
        {"name": "restore_drill", "passed": bool(backup and backup.get("passed"))},
    ]
    return {
        "observed_at": now.isoformat(),
        "environment": "local-only",
        "production_ready": False,
        "checks": checks,
        "queue": {
            "oldest_pending_seconds": age,
            "expired_leases": expired,
            "terminal_failures": errors,
            "alert_after_seconds": config.queue_alert_seconds,
        },
        "quality": {
            "source_permissions": licenses,
            "real_missing_license_notes": missing_license,
            "real_indicator_revised_periods": len(revisions),
            "real_reviews_overdue": overdue,
            "version_integrity": integrity,
            "evaluations": evaluations,
            "real_forward_accuracy": None,
        },
        "backup_drill": backup,
        "production_blockers": [
            "独立人工质量评审尚未完成",
            "真实支付与邮件供应商尚未接入并验收",
            "公网认证部署/HTTPS/密钥托管与外部监控尚未验收",
            "真实模型和资料许可/单位成本仍需业务复核",
        ],
        "limitations": [
            "这是本地工程就绪快照，不是独立安全认证或上线批准",
            "未到期与缺失数据不算预测成功；未校准真实准确率",
            "远程抓取供应商的重定向与DNS行为不能仅由本机预检保证",
        ],
    }
