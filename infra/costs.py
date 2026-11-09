"""Measured execution counts/timings; unknown provider prices stay unknown."""

from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from infra.db import CostObservation


def record_cost(
    session: Session,
    job_id: UUID,
    stage: str,
    source_key: str,
    duration_ms: int,
    reused: bool = False,
    external_calls: int = 0,
    usage: dict[str, Any] | None = None,
) -> None:
    session.add(
        CostObservation(
            job_id=job_id,
            stage=stage,
            source_key=source_key,
            duration_ms=max(0, duration_ms),
            reused=reused,
            external_model_calls=external_calls,
            usage=usage,
            external_cost_minor=0 if external_calls == 0 else None,
            cost_basis="no external provider charge; excludes local compute"
            if external_calls == 0
            else "provider price not configured; usage only",
        )
    )
