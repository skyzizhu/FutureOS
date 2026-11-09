from collections.abc import Callable, Iterator
from datetime import timedelta
from typing import Annotated, Any, Literal
from uuid import UUID

from fastapi import APIRouter, Depends
from prediction_engine.contracts.models import (
    ErrorV1,
    EvidenceClaimV1,
    HistoricalCaseImportV1,
    HistoricalCaseViewV1,
    IndicatorDefinitionV1,
    IndicatorImportV1,
    ObservationImportV1,
    ObservationV1,
    SignalImportV1,
    SignalV1,
    SourceImportV1,
    SourceIngestedV1,
    SourceVersionV1,
    WebFetchPreviewV1,
    WebFetchRequestV1,
    WebSearchRequestV1,
    WebSearchResponseV1,
)
from pydantic import AwareDatetime
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from infra.db import HistoricalCase, Indicator, SourceVersion, User, WebAccessLog, utcnow
from infra.evidence_repository import EvidenceError, EvidenceRepository, columns, digest
from infra.providers.deepseek import DeepSeekRequestError, DeepSeekWebProvider
from infra.providers.policy import ProviderPolicy, ProviderUnavailable
from infra.settings import Settings


def create_evidence_router(
    session_dependency: Callable[..., Iterator[Session]],
    admin_dependency: Callable[..., User],
    config: Settings,
) -> APIRouter:
    router = APIRouter(
        prefix="/api/v1/admin",
        tags=["M1 Evidence"],
        responses={code: {"model": ErrorV1} for code in (401, 403, 404, 409, 422, 429, 502, 503)},
    )
    admin = Depends(admin_dependency)
    database = Depends(session_dependency)
    responses: dict[int | str, dict[str, Any]] = {}

    @router.post("/sources/ingest", response_model=SourceIngestedV1, responses=responses)
    def ingest(
        data: SourceImportV1, user: Annotated[User, admin], session: Annotated[Session, database]
    ) -> SourceIngestedV1:
        return EvidenceRepository(session).ingest(data, user.id)

    @router.get("/sources", response_model=list[SourceVersionV1])
    def sources(
        user: Annotated[User, admin],
        session: Annotated[Session, database],
        as_of: AwareDatetime | None = None,
        label: Literal["DEMO", "REAL"] | None = None,
    ) -> Any:
        return EvidenceRepository(session).sources(as_of, label)

    @router.get("/sources/{source_version_id}", response_model=SourceVersionV1)
    def source(
        source_version_id: UUID, user: Annotated[User, admin], session: Annotated[Session, database]
    ) -> Any:
        row = session.get(SourceVersion, source_version_id)
        if row is None:
            raise EvidenceError("SOURCE_NOT_FOUND", "来源版本不存在", 404)
        return EvidenceRepository(session).version(row)

    @router.get("/evidence", response_model=list[EvidenceClaimV1])
    def claims(
        user: Annotated[User, admin],
        session: Annotated[Session, database],
        as_of: AwareDatetime,
        label: Literal["DEMO", "REAL"] | None = None,
    ) -> Any:
        return EvidenceRepository(session).evidence(as_of, label)

    @router.post("/indicators", response_model=IndicatorDefinitionV1)
    def indicator(
        data: IndicatorImportV1, user: Annotated[User, admin], session: Annotated[Session, database]
    ) -> Any:
        return EvidenceRepository(session).indicator(data)

    @router.get("/indicators", response_model=list[IndicatorDefinitionV1])
    def indicators(user: Annotated[User, admin], session: Annotated[Session, database]) -> Any:
        return [
            IndicatorDefinitionV1.model_validate(
                {**columns(row), "indicator_id": row.id}, extra="ignore"
            )
            for row in session.scalars(select(Indicator).order_by(Indicator.code).limit(200))
        ]

    @router.post("/indicators/{indicator_id}/observations", response_model=ObservationV1)
    def observation(
        indicator_id: UUID,
        data: ObservationImportV1,
        user: Annotated[User, admin],
        session: Annotated[Session, database],
    ) -> Any:
        return EvidenceRepository(session).observation(indicator_id, data)

    @router.get("/indicators/{indicator_id}/series", response_model=list[ObservationV1])
    def series(
        indicator_id: UUID,
        user: Annotated[User, admin],
        session: Annotated[Session, database],
        as_of: AwareDatetime,
        start: AwareDatetime | None = None,
        end: AwareDatetime | None = None,
    ) -> Any:
        if start is not None and end is not None and start > end:
            raise EvidenceError("INVALID_PERIOD", "统计期起点不得晚于终点")
        return EvidenceRepository(session).series(indicator_id, as_of, start, end)

    @router.post("/signals", response_model=SignalV1)
    def signal(
        data: SignalImportV1, user: Annotated[User, admin], session: Annotated[Session, database]
    ) -> Any:
        return EvidenceRepository(session).create_signal(data)

    @router.get("/signals", response_model=list[SignalV1])
    def signals(
        user: Annotated[User, admin],
        session: Annotated[Session, database],
        as_of: AwareDatetime | None = None,
        label: Literal["DEMO", "REAL"] | None = None,
    ) -> Any:
        return EvidenceRepository(session).signals(as_of, label)

    @router.post("/historical-cases")
    def historical_case(
        data: HistoricalCaseImportV1,
        user: Annotated[User, admin],
        session: Annotated[Session, database],
    ) -> dict[str, UUID]:
        return {"case_id": EvidenceRepository(session).historical_case(data)}

    @router.get("/historical-cases")
    def historical_cases(
        user: Annotated[User, admin], session: Annotated[Session, database]
    ) -> Any:
        return [
            {"case_id": row.id, "title": row.title, "cutoff_at": row.cutoff_at, "label": row.label}
            for row in session.scalars(select(HistoricalCase).limit(100))
        ]

    @router.get("/historical-cases/{case_id}", response_model=HistoricalCaseViewV1)
    def historical_view(
        case_id: UUID,
        user: Annotated[User, admin],
        session: Annotated[Session, database],
        as_of: AwareDatetime,
    ) -> Any:
        return EvidenceRepository(session).case_view(case_id, as_of)

    def live_provider() -> DeepSeekWebProvider:
        if not config.live_web_enabled or config.deepseek_api_key is None:
            raise EvidenceError("LIVE_WEB_DISABLED", "真实搜索未开启或未配置服务端 Key", 503)
        # One upstream attempt per manual operation; errors remain explicit.
        return DeepSeekWebProvider(
            config.deepseek_api_key,
            allowed_hosts=config.fetch_allowed_hosts,
            policy=ProviderPolicy(timeout_seconds=20, attempts=1, min_interval_seconds=0.1),
        )

    def reserve_call(session: Session, user: User, tool: str, value: str) -> WebAccessLog:
        if not config.live_web_enabled or config.deepseek_api_key is None:
            raise EvidenceError("LIVE_WEB_DISABLED", "真实搜索未开启或未配置服务端 Key", 503)
        session.scalar(select(User).where(User.id == user.id).with_for_update())
        now = utcnow()
        count = session.scalar(
            select(func.count())
            .select_from(WebAccessLog)
            .where(
                WebAccessLog.user_id == user.id,
                WebAccessLog.requested_at >= now - timedelta(days=1),
            )
        )
        recent = session.scalar(
            select(func.count())
            .select_from(WebAccessLog)
            .where(
                WebAccessLog.user_id == user.id,
                WebAccessLog.requested_at >= now - timedelta(minutes=1),
            )
        )
        if (count or 0) >= 20 or (recent or 0) >= 5:
            raise EvidenceError(
                "WEB_REQUEST_BUDGET_EXCEEDED", "达到本地研究请求上限（每分钟5次，每日20次）", 429
            )
        entry = WebAccessLog(user_id=user.id, tool=tool, input_hash=digest(value), status="started")
        session.add(entry)
        session.commit()
        return entry

    def finish_call(session: Session, entry: WebAccessLog, status: str, attempts: int) -> None:
        entry.status, entry.http_attempts, entry.finished_at = status, attempts, utcnow()
        session.commit()

    @router.get("/web-access")
    def web_access(user: Annotated[User, admin], session: Annotated[Session, database]) -> Any:
        return [
            columns(row)
            for row in session.scalars(
                select(WebAccessLog).order_by(WebAccessLog.requested_at.desc()).limit(100)
            )
        ]

    @router.post("/sources/search", response_model=WebSearchResponseV1)
    async def web_search(
        data: WebSearchRequestV1,
        user: Annotated[User, admin],
        session: Annotated[Session, database],
    ) -> WebSearchResponseV1:
        entry = reserve_call(session, user, "search", data.query)
        provider = live_provider()
        try:
            async with provider:
                results = await provider.search(data.query, max_results=data.count)
                finish_call(
                    session,
                    entry,
                    "succeeded" if results else "no_results",
                    provider.request_counts["search"],
                )
                return WebSearchResponseV1(results=results)
        except DeepSeekRequestError as exc:
            finish_call(session, entry, "failed", provider.request_counts["search"])
            raise EvidenceError(
                exc.code.upper(), "DeepSeek 请求失败，请检查授权、余额或请求内容", 502
            ) from None
        except (ProviderUnavailable, ValueError):
            finish_call(session, entry, "failed", provider.request_counts["search"])
            raise EvidenceError(
                "PROVIDER_UNAVAILABLE", "DeepSeek 暂不可用或参数无效，未保存来源", 503
            ) from None

    @router.post("/sources/fetch", response_model=WebFetchPreviewV1)
    async def web_fetch(
        data: WebFetchRequestV1, user: Annotated[User, admin], session: Annotated[Session, database]
    ) -> WebFetchPreviewV1:
        entry = reserve_call(session, user, "fetch", data.url)
        provider = live_provider()
        try:
            async with provider:
                page = await provider.fetch(data.url)
                excerpt = page.content[:2000]
                finish_call(session, entry, "succeeded", provider.request_counts["fetch"])
                return WebFetchPreviewV1(
                    url=page.url,
                    title=page.title,
                    excerpt=excerpt,
                    full_content_hash=page.content_hash,
                    retrieved_at=page.retrieved_at,
                    retained_characters=len(excerpt),
                )
        except ValueError:
            finish_call(session, entry, "rejected", provider.request_counts["fetch"])
            raise EvidenceError(
                "FETCH_URL_INVALID", "抓取 URL 必须为不含凭据的公开 HTTP(S) 地址"
            ) from None
        except DeepSeekRequestError as exc:
            finish_call(session, entry, "failed", provider.request_counts["fetch"])
            raise EvidenceError(exc.code.upper(), "DeepSeek 抓取失败，未保存来源", 502) from None
        except ProviderUnavailable:
            finish_call(session, entry, "failed", provider.request_counts["fetch"])
            raise EvidenceError(
                "PROVIDER_UNAVAILABLE", "DeepSeek 暂不可用，未保存来源", 503
            ) from None

    return router
