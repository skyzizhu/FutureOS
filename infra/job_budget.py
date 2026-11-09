from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from infra.db import Job
from infra.evidence_repository import EvidenceError


def enforce_queue_budget(session: Session, user_id: UUID, limit: int) -> None:
    pending = (
        session.scalar(
            select(func.count())
            .select_from(Job)
            .where(
                Job.user_id == user_id, Job.status.in_(["queued", "running", "failed_retryable"])
            )
        )
        or 0
    )
    if pending >= limit:
        raise EvidenceError("QUEUE_BUDGET_EXCEEDED", "待处理任务达到上限，请等待或取消旧任务", 429)
