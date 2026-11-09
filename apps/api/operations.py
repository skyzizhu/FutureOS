from collections.abc import Callable, Iterator
from typing import Annotated, Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from infra.db import User
from infra.operations import readiness
from infra.settings import Settings


def create_operations_router(
    db_dependency: Callable[..., Iterator[Session]],
    admin_dependency: Callable[..., User],
    config: Settings,
) -> APIRouter:
    router = APIRouter(prefix="/api/v1/admin", tags=["M7 readiness"])

    @router.get("/readiness")
    def snapshot(
        user: Annotated[User, Depends(admin_dependency)],
        session: Annotated[Session, Depends(db_dependency)],
    ) -> Any:
        return readiness(session, config)

    return router
