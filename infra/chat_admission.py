"""Atomic service-wide admission for provider requests across API processes."""

from datetime import datetime, timedelta

from prediction_engine.evidence.temporal import utc
from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.orm import Session

from infra.db import ChatModelBudget, ChatModelGlobalBudget
from infra.evidence_repository import EvidenceError
from infra.settings import Settings


def admit_global_model_turn(session: Session, config: Settings, now: datetime) -> None:
    insert = pg_insert if session.get_bind().dialect.name == "postgresql" else sqlite_insert
    session.execute(
        insert(ChatModelGlobalBudget)
        .values(id=1, window_start=now, turns=0)
        .on_conflict_do_nothing()
    )
    budget = session.scalar(
        select(ChatModelGlobalBudget).where(ChatModelGlobalBudget.id == 1).with_for_update()
    )
    assert budget is not None
    active = (
        session.scalar(
            select(func.count())
            .select_from(ChatModelBudget)
            .where(ChatModelBudget.lease_until > now)
        )
        or 0
    )
    if utc(budget.window_start) + timedelta(minutes=1) <= now:
        budget.window_start, budget.turns = now, 0
    if (
        budget.turns >= config.chat_model_global_window_limit
        or active >= config.chat_model_global_inflight_limit
    ):
        raise EvidenceError("CHAT_SERVICE_BUSY", "模型服务当前繁忙，请稍后重试", 429)
    budget.turns += 1
