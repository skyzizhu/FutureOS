from collections.abc import Callable, Iterator
from typing import Annotated, Any, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, Response
from prediction_engine.contracts.models import (
    ChatResearchStartV1,
    ChatResearchViewV1,
    CommunityActivityV1,
    CommunityIndustryInputV1,
    CommunityIndustryViewV1,
    CommunityPublishV1,
    CommunityReadInputV1,
    CommunityReportViewV1,
    CommunitySaveReportV1,
    CommunityVisibilityV1,
    ConsumerPreferenceV1,
    ConversationCapabilitiesV1,
    ConversationCreateV1,
    ConversationMessageV1,
    ConversationStartV1,
    ConversationViewV1,
    IndustryTrackingV1,
    IndustryTrackingViewV1,
)
from sqlalchemy import select
from sqlalchemy.orm import Session

from infra.chat_agent import model_available
from infra.chat_research import ChatResearchRepository
from infra.community import CommunityRepository
from infra.consumer_social import ConsumerSocial
from infra.conversations import ConversationRepository
from infra.db import AuthAccount, CommunityPrivateReport, ResearchConversation, User
from infra.evidence_repository import EvidenceError
from infra.reports import ReportRepository
from infra.settings import Settings


def create_community_router(
    session_dependency: Callable[..., Iterator[Session]],
    user_dependency: Callable[..., User],
    config: Settings,
) -> APIRouter:
    def no_cache(response: Response) -> None:
        response.headers["Cache-Control"] = "no-store"
        response.headers["Pragma"] = "no-cache"

    router = APIRouter(
        prefix="/api/v1", tags=["Consumer community"], dependencies=[Depends(no_cache)]
    )
    database = Depends(session_dependency)

    def account(
        user: Annotated[User, Depends(user_dependency)], session: Annotated[Session, database]
    ) -> User:
        if session.get(AuthAccount, user.id) is None:
            raise EvidenceError("LOCAL_ACCOUNT_REQUIRED", "请使用注册账号", 403)
        return user

    identity = Depends(account)

    @router.get("/community/industries", response_model=list[CommunityIndustryViewV1])
    def industries(session: Annotated[Session, database]) -> Any:
        return CommunityRepository(session, config).industries()

    @router.get("/community/industries/{identifier}", response_model=CommunityIndustryViewV1)
    def industry(identifier: UUID, session: Annotated[Session, database]) -> Any:
        repo = CommunityRepository(session, config)
        return repo.industry_view(repo.industry(identifier))

    @router.get("/community/reports", response_model=list[CommunityReportViewV1])
    def reports(
        session: Annotated[Session, database],
        industry_id: UUID | None = None,
        offset: Annotated[int, Query(ge=0, le=10000)] = 0,
        q: Annotated[str, Query(max_length=100)] = "",
        sort: Literal["newest", "oldest", "recommended"] = "newest",
        standalone: bool = False,
        limit: Annotated[int, Query(ge=1, le=24)] = 24,
    ) -> Any:
        return CommunityRepository(session, config).feed(
            industry_id=industry_id,
            offset=offset,
            query_text=q,
            sort=sort,
            standalone=standalone,
            limit=limit,
        )

    @router.get("/community/reports/{identifier}", response_model=CommunityReportViewV1)
    def public_report(identifier: UUID, session: Annotated[Session, database]) -> Any:
        repo = CommunityRepository(session, config)
        return repo.report_view(repo.publication(identifier))

    @router.post("/community/reports/{identifier}/read", response_model=CommunityReportViewV1)
    def record_read(
        identifier: UUID, data: CommunityReadInputV1, session: Annotated[Session, database]
    ) -> Any:
        ConsumerSocial(session, config).record_read(identifier, data.visitor_id)
        repo = CommunityRepository(session, config)
        return repo.report_view(repo.publication(identifier))

    @router.get("/me/preferences", response_model=ConsumerPreferenceV1)
    def preference(user: Annotated[User, identity], session: Annotated[Session, database]) -> Any:
        return ConsumerSocial(session, config).preference(user.id)

    @router.put("/me/preferences", response_model=ConsumerPreferenceV1)
    def save_preference(
        data: ConsumerPreferenceV1,
        user: Annotated[User, identity],
        session: Annotated[Session, database],
    ) -> Any:
        return ConsumerSocial(session, config).preference(user.id, data)

    @router.put("/me/community/industries/{identifier}/add", response_model=CommunityIndustryViewV1)
    def copy_industry(
        identifier: UUID, user: Annotated[User, identity], session: Annotated[Session, database]
    ) -> Any:
        return ConsumerSocial(session, config).add_industry(user.id, identifier)

    @router.get(
        "/me/community/industries/{identifier}/tracking", response_model=IndustryTrackingViewV1
    )
    def tracking(
        identifier: UUID, user: Annotated[User, identity], session: Annotated[Session, database]
    ) -> Any:
        return ConsumerSocial(session, config).tracking(user.id, identifier)

    @router.put(
        "/me/community/industries/{identifier}/tracking", response_model=IndustryTrackingViewV1
    )
    def save_tracking(
        identifier: UUID,
        data: IndustryTrackingV1,
        user: Annotated[User, identity],
        session: Annotated[Session, database],
    ) -> Any:
        return ConsumerSocial(session, config).tracking(user.id, identifier, data)

    @router.get("/me/community/reports/{identifier}", response_model=CommunityReportViewV1)
    def personal_report(
        identifier: UUID, user: Annotated[User, identity], session: Annotated[Session, database]
    ) -> Any:
        repo = CommunityRepository(session, config)
        return repo.report_view(repo.publication(identifier, user.id), user.id)

    @router.put("/me/community/reports/{identifier}/like")
    def like(
        identifier: UUID, user: Annotated[User, identity], session: Annotated[Session, database]
    ) -> Any:
        ConsumerSocial(session, config).like(user.id, identifier, True)
        return {"ok": True}

    @router.delete("/me/community/reports/{identifier}/like")
    def unlike(
        identifier: UUID, user: Annotated[User, identity], session: Annotated[Session, database]
    ) -> Any:
        ConsumerSocial(session, config).like(user.id, identifier, False)
        return {"ok": True}

    @router.get("/me/community/reports/{identifier}/download")
    def download(
        identifier: UUID, user: Annotated[User, identity], session: Annotated[Session, database]
    ) -> Response:
        body = ConsumerSocial(session, config).download(user.id, identifier)
        return Response(
            content=body,
            media_type="text/markdown; charset=utf-8",
            headers={
                "Content-Disposition": f'attachment; filename="futureos-report-{identifier}.md"',
                "Cache-Control": "no-store",
            },
        )

    @router.get("/me/community/notifications", response_model=list[CommunityActivityV1])
    def activities(user: Annotated[User, identity], session: Annotated[Session, database]) -> Any:
        return ConsumerSocial(session, config).inbox(user.id)

    @router.post("/me/community/notifications/{identifier}/read")
    def read_activity(
        identifier: UUID, user: Annotated[User, identity], session: Annotated[Session, database]
    ) -> Any:
        ConsumerSocial(session, config).read(user.id, identifier)
        return {"ok": True}

    @router.get("/me/community/industries", response_model=list[CommunityIndustryViewV1])
    def mine(user: Annotated[User, identity], session: Annotated[Session, database]) -> Any:
        return CommunityRepository(session, config).industries(user.id, mine=True)

    @router.post(
        "/me/community/industries", response_model=CommunityIndustryViewV1, status_code=201
    )
    def create(
        data: CommunityIndustryInputV1,
        user: Annotated[User, identity],
        session: Annotated[Session, database],
    ) -> Any:
        return CommunityRepository(session, config).create(user.id, data)

    @router.get("/me/community/industries/{identifier}", response_model=CommunityIndustryViewV1)
    def mine_detail(
        identifier: UUID, user: Annotated[User, identity], session: Annotated[Session, database]
    ) -> Any:
        repo = CommunityRepository(session, config)
        return repo.industry_view(repo.industry(identifier, user.id), user.id)

    @router.put("/me/community/industries/{identifier}")
    def edit(
        identifier: UUID,
        data: CommunityIndustryInputV1,
        user: Annotated[User, identity],
        session: Annotated[Session, database],
    ) -> Any:
        repo = CommunityRepository(session, config)
        repo.fence(user.id)
        row = repo.industry(identifier, user.id)
        if row.user_id != user.id:
            raise EvidenceError("INDUSTRY_NOT_FOUND", "只能编辑自己创建的行业", 404)
        row.name, row.description, row.domain = (
            data.name.strip(),
            data.description.strip(),
            data.domain,
        )
        if not row.name or not row.description:
            raise EvidenceError("INDUSTRY_EMPTY", "行业名称和简介不能为空", 422)
        session.commit()
        return repo.industry_view(row, user.id)

    @router.put("/me/community/industries/{identifier}/visibility")
    def visibility(
        identifier: UUID,
        data: CommunityVisibilityV1,
        user: Annotated[User, identity],
        session: Annotated[Session, database],
    ) -> Any:
        CommunityRepository(session, config).visibility(user.id, identifier, data.public)
        return {"ok": True}

    @router.put("/me/community/industries/{identifier}/membership")
    def add(
        identifier: UUID, user: Annotated[User, identity], session: Annotated[Session, database]
    ) -> Any:
        CommunityRepository(session, config).membership(user.id, identifier, True)
        return {"ok": True}

    @router.delete("/me/community/industries/{identifier}/membership")
    def remove(
        identifier: UUID, user: Annotated[User, identity], session: Annotated[Session, database]
    ) -> Any:
        CommunityRepository(session, config).membership(user.id, identifier, False)
        return {"ok": True}

    @router.get("/me/community/feed", response_model=list[CommunityReportViewV1])
    def feed(
        user: Annotated[User, identity],
        session: Annotated[Session, database],
        industry_id: UUID | None = None,
        offset: Annotated[int, Query(ge=0, le=10000)] = 0,
        q: Annotated[str, Query(max_length=100)] = "",
        sort: Literal["newest", "oldest", "recommended"] = "recommended",
        standalone: bool = False,
        limit: Annotated[int, Query(ge=1, le=24)] = 24,
    ) -> Any:
        return CommunityRepository(session, config).feed(
            user.id,
            industry_id,
            offset,
            query_text=q,
            sort=sort,
            standalone=standalone,
            limit=limit,
        )

    @router.get("/me/community/publications", response_model=list[CommunityReportViewV1])
    def publications(
        user: Annotated[User, identity],
        session: Annotated[Session, database],
        offset: Annotated[int, Query(ge=0, le=10000)] = 0,
    ) -> Any:
        return CommunityRepository(session, config).feed(user.id, offset=offset, mine=True)

    @router.get("/me/community/bookmarks", response_model=list[CommunityReportViewV1])
    def bookmarks(
        user: Annotated[User, identity],
        session: Annotated[Session, database],
        industry_id: UUID | None = None,
    ) -> Any:
        return CommunityRepository(session, config).saved(user.id, industry_id)

    @router.put("/me/community/reports/{identifier}/bookmark")
    def save(
        identifier: UUID,
        data: CommunitySaveReportV1,
        user: Annotated[User, identity],
        session: Annotated[Session, database],
    ) -> Any:
        CommunityRepository(session, config).bookmark(user.id, identifier, data.industry_id)
        return {"ok": True}

    @router.delete("/me/community/reports/{identifier}/bookmark")
    def unsave(
        identifier: UUID, user: Annotated[User, identity], session: Annotated[Session, database]
    ) -> Any:
        CommunityRepository(session, config).bookmark(user.id, identifier, None)
        return {"ok": True}

    @router.post("/me/community/reports/{identifier}/preview")
    def preview(
        identifier: UUID,
        data: CommunityPublishV1,
        user: Annotated[User, identity],
        session: Annotated[Session, database],
    ) -> Any:
        return CommunityRepository(session, config).preview(
            user.id, identifier, data.report_version_id, data.industry_id
        )

    @router.post("/me/community/reports/{identifier}/publish", response_model=CommunityReportViewV1)
    def publish(
        identifier: UUID,
        data: CommunityPublishV1,
        user: Annotated[User, identity],
        session: Annotated[Session, database],
    ) -> Any:
        return CommunityRepository(session, config).publish(user.id, identifier, data)

    @router.delete("/me/community/publications/{identifier}")
    def withdraw(
        identifier: UUID, user: Annotated[User, identity], session: Annotated[Session, database]
    ) -> Any:
        CommunityRepository(session, config).withdraw(user.id, identifier)
        return {"ok": True}

    @router.get("/me/community/private-reports")
    def private_links(
        user: Annotated[User, identity], session: Annotated[Session, database]
    ) -> Any:
        return [
            {"report_id": row.report_id, "industry_id": row.industry_id}
            for row in session.scalars(
                select(CommunityPrivateReport).where(CommunityPrivateReport.user_id == user.id)
            )
        ]

    @router.put("/me/community/private-reports/{identifier}")
    def file_private(
        identifier: UUID,
        data: CommunitySaveReportV1,
        user: Annotated[User, identity],
        session: Annotated[Session, database],
    ) -> Any:
        repo = CommunityRepository(session, config)
        repo.fence(user.id)
        repo.industry(data.industry_id, user.id)
        ReportRepository(session, config).report(user.id, identifier)
        row = session.get(CommunityPrivateReport, (user.id, identifier))
        if row is None:
            row = CommunityPrivateReport(
                user_id=user.id, report_id=identifier, industry_id=data.industry_id
            )
            session.add(row)
        row.industry_id = data.industry_id
        session.commit()
        return {"ok": True}

    @router.post("/me/conversations", status_code=201, response_model=ConversationViewV1)
    def conversation(
        data: ConversationCreateV1,
        request: Request,
        user: Annotated[User, identity],
        session: Annotated[Session, database],
    ) -> Any:
        token = request.headers.get("authorization", "").partition(" ")[2].strip()
        return ConversationRepository(session, config).create(user.id, data, token)

    @router.get("/me/chat-capabilities", response_model=ConversationCapabilitiesV1)
    def chat_capabilities(user: Annotated[User, identity]) -> ConversationCapabilitiesV1:
        return ConversationCapabilitiesV1(model_available=model_available(config))

    @router.get("/me/conversations", response_model=list[ConversationViewV1])
    def conversations(
        user: Annotated[User, identity],
        session: Annotated[Session, database],
        industry_id: UUID | None = None,
    ) -> Any:
        query = select(ResearchConversation).where(ResearchConversation.user_id == user.id)
        if industry_id:
            query = query.where(ResearchConversation.industry_id == industry_id)
        repo = ConversationRepository(session, config)
        return [
            repo.view(user.id, row.id)
            for row in session.scalars(query.order_by(ResearchConversation.created_at.desc()))
        ]

    @router.get("/me/conversations/{identifier}", response_model=ConversationViewV1)
    def read_conversation(
        identifier: UUID, user: Annotated[User, identity], session: Annotated[Session, database]
    ) -> Any:
        return ConversationRepository(session, config).view(user.id, identifier)

    @router.post("/me/conversations/{identifier}/messages", response_model=ConversationViewV1)
    def message(
        identifier: UUID,
        data: ConversationMessageV1,
        request: Request,
        user: Annotated[User, identity],
        session: Annotated[Session, database],
    ) -> Any:
        token = request.headers.get("authorization", "").partition(" ")[2].strip()
        return ConversationRepository(session, config).message(user.id, identifier, data, token)

    @router.post("/me/conversations/{identifier}/start", response_model=ConversationViewV1)
    def start(
        identifier: UUID,
        data: ConversationStartV1,
        user: Annotated[User, identity],
        session: Annotated[Session, database],
    ) -> Any:
        return ConversationRepository(session, config).start(user.id, identifier)

    @router.post(
        "/me/conversations/{identifier}/industries/{proposal_id}",
        response_model=ConversationViewV1,
    )
    def confirm_industry(
        identifier: UUID,
        proposal_id: UUID,
        user: Annotated[User, identity],
        session: Annotated[Session, database],
    ) -> Any:
        return ConversationRepository(session, config).confirm_industry(
            user.id, identifier, proposal_id
        )

    @router.post(
        "/me/conversations/{identifier}/industry-research",
        status_code=202,
        response_model=ChatResearchViewV1,
    )
    def start_industry_research(
        identifier: UUID,
        data: ChatResearchStartV1,
        user: Annotated[User, identity],
        session: Annotated[Session, database],
    ) -> ChatResearchViewV1:
        conversation = ConversationRepository(session, config).row(user.id, identifier)
        return ChatResearchRepository(session, config).start(conversation, data)

    @router.get(
        "/me/conversations/{identifier}/industry-research",
        response_model=list[ChatResearchViewV1],
    )
    def list_industry_research(
        identifier: UUID,
        user: Annotated[User, identity],
        session: Annotated[Session, database],
    ) -> list[ChatResearchViewV1]:
        conversation = ConversationRepository(session, config).row(user.id, identifier)
        return ChatResearchRepository(session, config).list(conversation)

    @router.get(
        "/me/conversations/{identifier}/industry-research/{job_id}",
        response_model=ChatResearchViewV1,
    )
    def read_industry_research(
        identifier: UUID,
        job_id: UUID,
        user: Annotated[User, identity],
        session: Annotated[Session, database],
    ) -> ChatResearchViewV1:
        conversation = ConversationRepository(session, config).row(user.id, identifier)
        return ChatResearchRepository(session, config).detail(conversation, job_id)

    @router.post("/me/conversations/{identifier}/industry-research/{job_id}/cancel")
    def cancel_industry_research(
        identifier: UUID,
        job_id: UUID,
        user: Annotated[User, identity],
        session: Annotated[Session, database],
    ) -> dict[str, bool]:
        conversation = ConversationRepository(session, config).row(user.id, identifier)
        ChatResearchRepository(session, config).cancel(conversation, job_id)
        session.commit()
        return {"ok": True}

    @router.delete("/me/conversations/{identifier}")
    def delete_conversation(
        identifier: UUID, user: Annotated[User, identity], session: Annotated[Session, database]
    ) -> Any:
        repo = ConversationRepository(session, config)
        repo.community.fence(user.id)
        row = repo.row(user.id, identifier)
        if row.job_id:
            ReportRepository(session, config).cancel(user.id, row.job_id, commit=False)
        ChatResearchRepository(session, config).cancel(row)
        session.delete(row)
        session.commit()
        return {"ok": True}

    return router
