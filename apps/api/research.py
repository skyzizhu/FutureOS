from collections.abc import Callable, Iterator
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, Header
from prediction_engine.contracts.models import (
    ErrorV1,
    ReplayResultV1,
    ResearchAcceptedV1,
    ResearchRunViewV1,
    ResearchSnapshotV1,
    ResearchSubmitV1,
)
from sqlalchemy import select
from sqlalchemy.orm import Session

from infra.db import ModelCall, ResearchRun, User
from infra.evidence_repository import EvidenceError, columns
from infra.research_demo import seed_research_demo
from infra.research_repository import ResearchRepository
from infra.settings import Settings


def create_research_router(
    session_dependency: Callable[..., Iterator[Session]],
    admin_dependency: Callable[..., User],
    config: Settings,
) -> APIRouter:
    router = APIRouter(
        prefix="/api/v1/admin/research",
        tags=["M2 Internal Research"],
        responses={code: {"model": ErrorV1} for code in [401, 403, 404, 409, 422, 503]},
    )
    database = Depends(session_dependency)
    admin = Depends(admin_dependency)

    @router.get("/config")
    def settings(user: Annotated[User, admin]) -> dict[str, Any]:
        return {
            "live_research_enabled": config.live_research_enabled,
            "model_id": config.deepseek_research_model,
            "publication_allowed": False,
        }

    @router.post("/demo-inputs", response_model=ResearchSubmitV1)
    def demo(user: Annotated[User, admin], session: Annotated[Session, database]) -> Any:
        return seed_research_demo(session, user.id)

    @router.post("/submit", response_model=ResearchAcceptedV1, status_code=202)
    def submit(
        data: ResearchSubmitV1,
        user: Annotated[User, admin],
        session: Annotated[Session, database],
        idempotency_key: Annotated[str, Header(min_length=1, max_length=128)],
    ) -> Any:
        return ResearchRepository(session).submit(data, user.id, idempotency_key, config)

    @router.get("/runs", response_model=list[ResearchRunViewV1])
    def runs(user: Annotated[User, admin], session: Annotated[Session, database]) -> Any:
        repo = ResearchRepository(session)
        return [
            repo.view(identifier)
            for identifier in session.scalars(
                select(ResearchRun.id).order_by(ResearchRun.created_at.desc()).limit(50)
            )
        ]

    @router.get("/runs/{run_id}", response_model=ResearchRunViewV1)
    def run(
        run_id: UUID, user: Annotated[User, admin], session: Annotated[Session, database]
    ) -> Any:
        return ResearchRepository(session).view(run_id)

    @router.get("/runs/{run_id}/inputs", response_model=ResearchSnapshotV1)
    def inputs(
        run_id: UUID, user: Annotated[User, admin], session: Annotated[Session, database]
    ) -> Any:
        row = session.get(ResearchRun, run_id)
        if row is None:
            raise EvidenceError("RESEARCH_RUN_NOT_FOUND", "研究运行不存在", 404)
        return row.snapshot

    @router.post("/runs/{run_id}/replay", response_model=ReplayResultV1)
    def replay(
        run_id: UUID, user: Annotated[User, admin], session: Annotated[Session, database]
    ) -> Any:
        return ResearchRepository(session).replay(run_id)

    @router.get("/model-calls")
    def model_calls(user: Annotated[User, admin], session: Annotated[Session, database]) -> Any:
        return [
            {key: value for key, value in columns(row).items() if key != "response"}
            for row in session.scalars(
                select(ModelCall).order_by(ModelCall.started_at.desc()).limit(50)
            )
        ]

    return router
