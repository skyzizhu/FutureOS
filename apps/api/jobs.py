from hashlib import sha256
from uuid import UUID

from prediction_engine.contracts.models import DemoResearchInputV1
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from infra.db import Job, OutboxEvent, User
from infra.job_budget import enforce_queue_budget


class IdempotencyConflict(Exception):
    pass


def submit(
    session: Session, user_id: UUID, key: str, payload: DemoResearchInputV1, queue_limit: int = 20
) -> Job:
    session.scalar(select(User).where(User.id == user_id).with_for_update(key_share=True))
    fingerprint = sha256(payload.model_dump_json().encode()).hexdigest()

    def existing() -> Job | None:
        return session.scalar(select(Job).where(Job.user_id == user_id, Job.idempotency_key == key))

    prior = existing()
    if prior is None:
        enforce_queue_budget(session, user_id, queue_limit)
        job = Job(
            user_id=user_id,
            idempotency_key=key,
            input_hash=fingerprint,
            payload=payload.model_dump(mode="json"),
        )
        session.add(job)
        try:
            session.flush()
            session.add(
                OutboxEvent(
                    job_id=job.id,
                    event_type="DemoResearchRequested.v1",
                    payload={"job_id": str(job.id), "label": "DEMO"},
                )
            )
            session.commit()
            return job
        except IntegrityError:
            session.rollback()
            prior = existing()
            if prior is None:
                raise
    if prior.input_hash != fingerprint:
        raise IdempotencyConflict
    return prior
