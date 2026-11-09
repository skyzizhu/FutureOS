from collections.abc import Callable, Iterator
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends
from prediction_engine.contracts.models import (
    EvaluationProtocolV1,
    EvaluationRegisterV1,
    ForecastResolutionV1,
    PublishedForecastV1,
    PublishRequestV1,
    ResolveRequestV1,
    ReviewViewV1,
    RevisionRequestV1,
    RevisionViewV1,
)
from sqlalchemy import select
from sqlalchemy.orm import Session

from infra.db import CriticRun, ForecastDraft, ForecastVersion, User
from infra.review_repository import ReviewRepository


def create_review_router(
    session_dependency: Callable[..., Iterator[Session]], admin_dependency: Callable[..., User]
) -> APIRouter:
    router = APIRouter(prefix="/api/v1/admin/review", tags=["M3 Critic and evaluation"])
    db = Depends(session_dependency)
    admin = Depends(admin_dependency)

    @router.get("/drafts")
    def drafts(user: Annotated[User, admin], session: Annotated[Session, db]) -> Any:
        return [
            {
                "draft_id": row.id,
                "run_id": row.run_id,
                "draft_sequence": row.draft_sequence,
                "draft_hash": row.immutable_hash,
                "label": row.body["label"],
                "statement": row.body["statement"],
            }
            for row in session.scalars(
                select(ForecastDraft).order_by(ForecastDraft.created_at.desc()).limit(100)
            )
        ]

    @router.post("/drafts/{draft_id}/check", response_model=ReviewViewV1)
    def check(draft_id: UUID, user: Annotated[User, admin], session: Annotated[Session, db]) -> Any:
        return ReviewRepository(session).review(draft_id)

    @router.get("/runs")
    def runs(user: Annotated[User, admin], session: Annotated[Session, db]) -> Any:
        repo = ReviewRepository(session)
        return [
            repo.review_view(row.id)
            for row in session.scalars(
                select(CriticRun).order_by(CriticRun.created_at.desc()).limit(100)
            )
        ]

    @router.get("/runs/{review_id}", response_model=ReviewViewV1)
    def run(review_id: UUID, user: Annotated[User, admin], session: Annotated[Session, db]) -> Any:
        return ReviewRepository(session).review_view(review_id)

    @router.post("/drafts/{draft_id}/revise", response_model=RevisionViewV1)
    def revise(
        draft_id: UUID,
        data: RevisionRequestV1,
        user: Annotated[User, admin],
        session: Annotated[Session, db],
    ) -> Any:
        return ReviewRepository(session).revise(draft_id, data)

    @router.get("/drafts/{draft_id}/revision", response_model=RevisionViewV1)
    def revision(
        draft_id: UUID, user: Annotated[User, admin], session: Annotated[Session, db]
    ) -> Any:
        return ReviewRepository(session).revision_view(draft_id)

    @router.post("/drafts/{draft_id}/publish", response_model=PublishedForecastV1)
    def publish(
        draft_id: UUID,
        data: PublishRequestV1,
        user: Annotated[User, admin],
        session: Annotated[Session, db],
    ) -> Any:
        return ReviewRepository(session).publish(draft_id, data)

    @router.get("/versions", response_model=list[PublishedForecastV1])
    def versions(user: Annotated[User, admin], session: Annotated[Session, db]) -> Any:
        repo = ReviewRepository(session)
        return [
            repo.version_view(row.id)
            for row in session.scalars(
                select(ForecastVersion).order_by(ForecastVersion.published_at.desc()).limit(100)
            )
        ]

    @router.post("/versions/{version_id}/register", response_model=EvaluationProtocolV1)
    def register(
        version_id: UUID,
        data: EvaluationRegisterV1,
        user: Annotated[User, admin],
        session: Annotated[Session, db],
    ) -> Any:
        return ReviewRepository(session).register(version_id, data)

    @router.post("/protocols/{protocol_id}/resolve", response_model=ForecastResolutionV1)
    def resolution(
        protocol_id: UUID,
        data: ResolveRequestV1,
        user: Annotated[User, admin],
        session: Annotated[Session, db],
    ) -> Any:
        return ReviewRepository(session).resolve(protocol_id, data)

    @router.get("/scoreboard")
    def scoreboard(user: Annotated[User, admin], session: Annotated[Session, db]) -> Any:
        return ReviewRepository(session).scoreboard()

    return router
