import json
import logging
import secrets
import time
from collections.abc import Iterator
from typing import Annotated, Any
from uuid import UUID, uuid4

import redis
from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from prediction_engine.contracts.models import (
    DemoResearchInputV1,
    DemoResearchResultV1,
    ErrorV1,
    JobAcceptedV1,
    JobStatus,
    JobV1,
    M2ResearchResultV1,
    MailDeliveryResultV1,
    MonitorResultV1,
    UserReportResultV1,
)
from sqlalchemy import func, select, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette.exceptions import HTTPException as StarletteHTTPException

from apps.api.account_security import create_account_security_router
from apps.api.body_limit import BodyLimitMiddleware
from apps.api.commerce import create_commerce_router
from apps.api.community import create_community_router
from apps.api.evidence import create_evidence_router
from apps.api.jobs import IdempotencyConflict, submit
from apps.api.monitor import create_monitor_router
from apps.api.notifications import create_notification_router
from apps.api.operations import create_operations_router
from apps.api.personal import create_personal_router
from apps.api.research import create_research_router
from apps.api.review import create_review_router
from infra.accounts import AuthRateLimited, session_user
from infra.admin_security import permission
from infra.db import (
    AuthSession,
    CommerceCheckout,
    Job,
    ObservationVintage,
    ProfileSnapshot,
    ResearchCreditGrant,
    SourceVersion,
    User,
    UserReportVersion,
    make_engine,
    session_factory,
)
from infra.evidence_repository import EvidenceError
from infra.settings import Settings, get_settings
from scripts.seed_demo import ADMIN_ID, OTHER_ID, USER_ID

logger = logging.getLogger("futureos.requests")
bearer = HTTPBearer(auto_error=False)


def create_app(settings: Settings | None = None) -> FastAPI:
    config = settings or get_settings()
    engine = make_engine(config.database_url)
    sessions = session_factory(engine)
    cache: redis.Redis = redis.Redis.from_url(
        config.redis_url, socket_connect_timeout=0.3, socket_timeout=0.3
    )
    app = FastAPI(
        title="FutureOS M7 Readiness",
        version="0.8.0",
        openapi_url="/api/v1/openapi.json",
        docs_url="/api/v1/docs",
        redoc_url=None,
    )
    app.add_middleware(BodyLimitMiddleware)
    app.state.engine = engine
    app.state.sessions = sessions
    app.state.settings = config

    @app.middleware("http")
    async def request_log(request: Request, call_next: Any) -> Any:
        request.state.request_id = str(uuid4())
        start = time.monotonic()
        response = await call_next(request)
        response.headers["X-Request-ID"] = request.state.request_id
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        if request.headers.get("authorization") or request.url.path.startswith(
            ("/api/v1/auth/", "/api/v1/admin-auth/")
        ):
            response.headers["Cache-Control"] = "private, no-store"
            response.headers["Pragma"] = "no-cache"
        # No query, URL IDs, input text, auth headers, or exception messages in logs.
        route = request.scope.get("route")
        logger.info(
            json.dumps(
                {
                    "request_id": request.state.request_id,
                    "route": getattr(route, "path", "unmatched"),
                    "method": request.method,
                    "status": response.status_code,
                    "duration_ms": round((time.monotonic() - start) * 1000),
                }
            )
        )
        return response

    def error(request: Request, code: str, message: str, status: int) -> JSONResponse:
        body = ErrorV1(
            code=code,
            message=message,
            request_id=request.state.request_id,
            details={"retryable": status == 503},
        )
        return JSONResponse(
            body.model_dump(mode="json"),
            status_code=status,
            headers={"X-Request-ID": request.state.request_id, "Cache-Control": "no-store"},
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_error(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        codes = {
            401: "AUTH_REQUIRED",
            403: "FORBIDDEN",
            404: "NOT_FOUND",
            409: "IDEMPOTENCY_CONFLICT",
            503: "PROVIDER_UNAVAILABLE",
        }
        code = codes.get(exc.status_code, "REQUEST_ERROR")
        return error(request, code, code, exc.status_code)

    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
        return error(request, "VALIDATION_ERROR", "请求格式无效", 422)

    @app.exception_handler(EvidenceError)
    async def evidence_error(request: Request, exc: EvidenceError) -> JSONResponse:
        response = error(request, exc.code, exc.message, exc.status)
        if isinstance(exc, AuthRateLimited):
            response.headers["Retry-After"] = str(exc.retry_after)
        elif exc.code == "AUTH_BUSY":
            response.headers["Retry-After"] = "2"
        return response

    @app.exception_handler(Exception)
    async def unexpected_error(request: Request, exc: Exception) -> JSONResponse:
        return error(request, "INTERNAL_ERROR", "内部错误，请使用 request_id 查询", 500)

    def db_session() -> Iterator[Session]:
        with sessions() as session:
            yield session

    def current_user(
        request: Request,
        credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
        session: Annotated[Session, Depends(db_session)],
    ) -> User:
        if credentials is None:
            raise HTTPException(401)
        user_id = None
        for token, candidate in [
            (config.demo_user_token, USER_ID),
            (config.demo_admin_token, ADMIN_ID),
            (config.demo_other_token, OTHER_ID),
        ]:
            if (candidate != ADMIN_ID or config.demo_admin_enabled) and secrets.compare_digest(
                credentials.credentials, token
            ):
                user_id = candidate
        user = (
            session.get(User, user_id)
            if user_id
            else session_user(session, credentials.credentials)
        )
        if user is None:
            raise HTTPException(401)
        return user

    def admin_user(
        request: Request,
        user: Annotated[User, Depends(current_user)],
        session: Annotated[Session, Depends(db_session)],
        authorization: Annotated[str, Header()],
    ) -> User:
        if user.role != "admin":
            raise HTTPException(403)
        area = request.url.path.removeprefix("/api/v1/admin/").split("/")[0]
        if request.url.path.startswith("/api/v1/admin-auth/"):
            area = "self"
        permission(
            session,
            config,
            user,
            authorization.split(" ", 1)[1],
            area,
            request.method not in {"GET", "HEAD"},
        )
        return user

    errors: dict[int | str, dict[str, Any]] = {
        code: {"model": ErrorV1} for code in [401, 403, 404, 409, 422, 500, 503]
    }

    @app.get("/api/v1/health/live")
    def live() -> dict[str, str]:
        return {"status": "ok", "label": "DEMO", "milestone": "M7"}

    @app.get("/api/v1/health/ready", responses={503: {"model": ErrorV1}})
    def ready(request: Request) -> Any:
        try:
            with sessions() as session:
                session.execute(text("SELECT 1"))
                session.execute(select(User.id).limit(1))
                session.execute(select(Job.id).limit(1))
                session.execute(select(SourceVersion.id).limit(1))
                session.execute(select(ObservationVintage.id).limit(1))
                session.execute(select(AuthSession.token_hash).limit(1))
                session.execute(select(ProfileSnapshot.id).limit(1))
                session.execute(select(UserReportVersion.id).limit(1))
                session.execute(select(CommerceCheckout.id).limit(1))
                session.execute(select(ResearchCreditGrant.id).limit(1))
            redis_status = "ok"
            try:
                cache.ping()
            except redis.RedisError:
                if config.require_redis:
                    raise HTTPException(503) from None
                redis_status = "optional_unavailable"
            return {"status": "ok", "label": "DEMO", "database": "ok", "redis": redis_status}
        except (SQLAlchemyError, HTTPException):
            return error(request, "DEPENDENCY_UNAVAILABLE", "依赖尚未就绪，请检查迁移与服务", 503)

    @app.get("/api/v1/me", responses=errors)
    def me(user: Annotated[User, Depends(current_user)]) -> dict[str, str]:
        return {"user_id": str(user.id), "role": user.role, "label": "DEMO"}

    @app.post(
        "/api/v1/demo/research", status_code=202, response_model=JobAcceptedV1, responses=errors
    )
    def demo_research(
        payload: DemoResearchInputV1,
        user: Annotated[User, Depends(current_user)],
        session: Annotated[Session, Depends(db_session)],
        idempotency_key: Annotated[str, Header(min_length=1, max_length=128)],
    ) -> Any:
        try:
            job = submit(
                session, user.id, idempotency_key, payload, config.queue_max_pending_per_user
            )
        except IdempotencyConflict:
            raise HTTPException(409) from None
        try:
            # Redis is only a wake-up hint; DB polling recovers a lost hint after commit.
            cache.lpush("futureos:DEMO:wakeup", str(job.id))
            cache.ltrim("futureos:DEMO:wakeup", 0, 999)
        except redis.RedisError:
            pass
        return JobAcceptedV1(job_id=job.id, request_id=job.request_id)

    @app.get("/api/v1/jobs/{job_id}", response_model=JobV1, responses=errors)
    def get_job(
        job_id: UUID,
        user: Annotated[User, Depends(current_user)],
        session: Annotated[Session, Depends(db_session)],
    ) -> JobV1:
        job = session.scalar(select(Job).where(Job.id == job_id, Job.user_id == user.id))
        if job is None:
            raise HTTPException(404)
        return JobV1(
            job_id=job.id,
            request_id=job.request_id,
            trace_id=job.trace_id,
            status=JobStatus(job.status),
            attempts=job.attempts,
            label=job.result.get("label", job.payload.get("label", "DEMO"))
            if job.result
            else job.payload.get("label", "DEMO"),
            result=(
                MonitorResultV1.model_validate(job.result)
                if job.task_type == "m5_monitor"
                else MailDeliveryResultV1.model_validate(job.result)
                if job.task_type == "m5_mail"
                else UserReportResultV1.model_validate(job.result)
                if job.task_type in {"m4_report", "m5_report_refresh", "m6_research"}
                else M2ResearchResultV1.model_validate(job.result)
                if job.task_type == "m2_research"
                else DemoResearchResultV1.model_validate(job.result)
            )
            if job.result and job.task_type != "chat_industry_research"
            else None,
            error_code=job.error_code,
        )

    @app.get("/api/v1/admin/overview", responses=errors)
    def overview(
        user: Annotated[User, Depends(admin_user)], session: Annotated[Session, Depends(db_session)]
    ) -> dict[str, Any]:
        counts = session.execute(select(Job.status, func.count()).group_by(Job.status)).all()
        return {
            "label": "DEMO",
            "milestone": "M7",
            "job_counts": {row[0]: row[1] for row in counts},
            "production_enabled": False,
        }

    app.include_router(create_evidence_router(db_session, admin_user, config))
    app.include_router(create_research_router(db_session, admin_user, config))
    app.include_router(create_review_router(db_session, admin_user))
    app.include_router(create_account_security_router(db_session, current_user, admin_user, config))
    app.include_router(create_personal_router(db_session, current_user, config))
    app.include_router(create_community_router(db_session, current_user, config))
    app.include_router(create_monitor_router(db_session, admin_user, config))
    app.include_router(create_notification_router(db_session, current_user, config))
    app.include_router(create_commerce_router(db_session, current_user, admin_user, config))
    app.include_router(create_operations_router(db_session, admin_user, config))
    return app


app = create_app()
