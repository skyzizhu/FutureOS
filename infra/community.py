"""Consumer access rules. Public snapshots never serialize private reports or chats."""

from typing import Any
from unicodedata import normalize
from uuid import UUID, uuid4

from prediction_engine.contracts.models import (
    CommunityIndustryInputV1,
    CommunityIndustryViewV1,
    CommunityPublishV1,
    CommunityReportViewV1,
)
from prediction_engine.evidence.temporal import utc
from sqlalchemy import case, delete, func, or_, select
from sqlalchemy.orm import Session

from infra.db import (
    CommunityBookmark,
    CommunityIndustry,
    CommunityIndustryCopy,
    CommunityLike,
    CommunityMembership,
    CommunityPublication,
    CommunityReportMetric,
    ForecastVersion,
    IndustryTracking,
    Profile,
    ProfileIndustry,
    ResearchTopic,
    User,
    WorldForecast,
    utcnow,
)
from infra.evidence_repository import EvidenceError
from infra.reports import ReportRepository
from infra.settings import Settings


class CommunityRepository:
    def __init__(self, session: Session, config: Settings):
        self.session, self.config = session, config
        self._views: dict[UUID, int] = {}

    def fence(self, user_id: UUID) -> None:
        self.session.scalar(select(User).where(User.id == user_id).with_for_update())

    def industry(self, identifier: UUID, user_id: UUID | None = None) -> CommunityIndustry:
        row = self.session.get(CommunityIndustry, identifier)
        member = self.session.get(CommunityMembership, (user_id, identifier)) if user_id else None
        if row is None or not (row.public or (user_id and row.user_id == user_id) or member):
            raise EvidenceError("INDUSTRY_NOT_FOUND", "行业不存在或未公开", 404)
        return row

    def industry_view(
        self, row: CommunityIndustry, user_id: UUID | None = None
    ) -> CommunityIndustryViewV1:
        copy = (
            self.session.scalar(
                select(CommunityIndustryCopy).where(
                    CommunityIndustryCopy.industry_id == row.id,
                    CommunityIndustryCopy.user_id == user_id,
                )
            )
            if user_id
            else None
        )
        personal = self.session.get(CommunityIndustryCopy, (user_id, row.id)) if user_id else None
        personal_id = (
            personal.industry_id
            if personal
            else row.id
            if row.user_id == user_id and user_id
            else None
        )
        return CommunityIndustryViewV1(
            personal_industry_id=personal_id,
            source_industry_id=copy.source_industry_id if copy else None,
            id=row.id,
            name=row.name,
            description=row.description,
            domain=row.domain,
            public=row.public,
            owned=user_id is not None and row.user_id == user_id,
            added=bool(
                user_id
                and (
                    self.session.get(CommunityMembership, (user_id, row.id))
                    or (
                        personal_id
                        and self.session.get(CommunityMembership, (user_id, personal_id))
                    )
                )
            ),
        )

    def industries(
        self, user_id: UUID | None = None, mine: bool = False
    ) -> list[CommunityIndustryViewV1]:
        query = select(CommunityIndustry)
        if mine:
            query = query.where(
                or_(
                    CommunityIndustry.id.in_(
                        select(CommunityMembership.industry_id).where(
                            CommunityMembership.user_id == user_id
                        )
                    ),
                    CommunityIndustry.user_id == user_id,
                )
            )
            profile_id = (
                select(ProfileIndustry.industry_id)
                .where(ProfileIndustry.user_id == user_id)
                .scalar_subquery()
            )
            query = query.order_by(case((CommunityIndustry.id == profile_id, 0), else_=1))
        else:
            query = query.where(CommunityIndustry.public.is_(True)).limit(100)
        query = query.order_by(CommunityIndustry.created_at, CommunityIndustry.id)
        return [self.industry_view(row, user_id) for row in self.session.scalars(query)]

    def find_personal_industry(self, user_id: UUID, name: str) -> CommunityIndustry | None:
        def key(value: str) -> str:
            normalized = " ".join(normalize("NFKC", value).split()).casefold()
            return normalized.removesuffix("行业").rstrip() or normalized

        requested = key(name)
        query = (
            select(CommunityIndustry)
            .where(
                or_(
                    CommunityIndustry.user_id == user_id,
                    CommunityIndustry.id.in_(
                        select(CommunityMembership.industry_id).where(
                            CommunityMembership.user_id == user_id
                        )
                    ),
                )
            )
            .order_by(CommunityIndustry.created_at, CommunityIndustry.id)
        )
        return next(
            (row for row in self.session.scalars(query) if key(row.name) == requested), None
        )

    def create(
        self, user_id: UUID, data: CommunityIndustryInputV1, *, commit: bool = True
    ) -> CommunityIndustryViewV1:
        self.fence(user_id)
        if not data.name.strip() or not data.description.strip():
            raise EvidenceError("INDUSTRY_EMPTY", "请填写行业名称与简介", 422)
        row = CommunityIndustry(
            id=uuid4(),
            user_id=user_id,
            name=data.name.strip(),
            description=data.description.strip(),
            domain=data.domain,
            public=False,
        )
        self.session.add(row)
        self.session.flush()
        self.session.add(CommunityMembership(user_id=user_id, industry_id=row.id))
        self.session.add(IndustryTracking(user_id=user_id, industry_id=row.id))
        if commit:
            self.session.commit()
        else:
            self.session.flush()
        return self.industry_view(row, user_id)

    def membership(self, user_id: UUID, identifier: UUID, add: bool) -> None:
        self.fence(user_id)
        self.industry(identifier, user_id)
        existing = self.session.get(CommunityMembership, (user_id, identifier))
        if add and existing is None:
            self.session.add(CommunityMembership(user_id=user_id, industry_id=identifier))
        elif not add and existing:
            self.session.delete(existing)
            tracking = self.session.get(IndustryTracking, (user_id, identifier))
            if tracking:
                tracking.monitor_enabled = tracking.prediction_enabled = tracking.email_enabled = (
                    False
                )
                tracking.updated_at = utcnow()
        self.session.commit()

    def visibility(self, user_id: UUID, identifier: UUID, public: bool) -> None:
        self.fence(user_id)
        row = self.industry(identifier, user_id)
        if row.user_id != user_id:
            raise EvidenceError("INDUSTRY_NOT_FOUND", "只能管理自己创建的行业", 404)
        row.public = public
        self.session.commit()

    def publication(self, identifier: UUID, user_id: UUID | None = None) -> CommunityPublication:
        row = self.session.get(CommunityPublication, identifier)
        if row is None or (not row.public and (user_id is None or row.user_id != user_id)):
            raise EvidenceError("PUBLIC_REPORT_NOT_FOUND", "报告未公开或已撤回", 404)
        # Withdrawing an industry removes it and its reports from public discovery.
        if row.industry_id is not None:
            industry = self.session.get(CommunityIndustry, row.industry_id)
            if industry is None or (
                not industry.public and (user_id is None or row.user_id != user_id)
            ):
                raise EvidenceError("PUBLIC_REPORT_NOT_FOUND", "所属行业未公开", 404)
        return row

    def report_view(
        self, row: CommunityPublication, user_id: UUID | None = None, reason: str = ""
    ) -> CommunityReportViewV1:
        industry = self.session.get(CommunityIndustry, row.industry_id) if row.industry_id else None
        bookmark = self.session.get(CommunityBookmark, (user_id, row.id)) if user_id else None
        metric = (
            self.session.get(CommunityReportMetric, row.id) if row.id not in self._views else None
        )
        return CommunityReportViewV1(
            views_count=self._views.get(row.id, metric.views_count if metric else 0),
            id=row.id,
            industry_id=row.industry_id,
            industry_name=industry.name if industry else "独立公开报告",
            **row.body,
            created_at=utc(row.created_at),
            author="FutureOS 阅读示例" if row.body["sample"] else "社区研究者",
            reason=reason,
            likes_count=self.session.scalar(
                select(func.count())
                .select_from(CommunityLike)
                .where(CommunityLike.publication_id == row.id)
            )
            or 0,
            bookmarks_count=self.session.scalar(
                select(func.count())
                .select_from(CommunityBookmark)
                .where(CommunityBookmark.publication_id == row.id)
            )
            or 0,
            liked=bool(user_id and self.session.get(CommunityLike, (user_id, row.id))),
            saved=bool(user_id and self.session.get(CommunityBookmark, (user_id, row.id))),
            saved_industry_id=bookmark.industry_id if bookmark else None,
            owned=bool(user_id and row.user_id == user_id),
            public=row.public,
        )

    def feed(
        self,
        user_id: UUID | None = None,
        industry_id: UUID | None = None,
        offset: int = 0,
        mine: bool = False,
        query_text: str = "",
        sort: str = "recommended",
        standalone: bool = False,
        limit: int = 24,
    ) -> list[CommunityReportViewV1]:
        query = (
            select(CommunityPublication)
            .outerjoin(CommunityIndustry)
            .where(
                CommunityPublication.public.is_(True),
                or_(
                    CommunityPublication.industry_id.is_(None),
                    CommunityIndustry.public.is_(True),
                ),
            )
        )
        if standalone:
            query = query.where(CommunityPublication.industry_id.is_(None))
        if industry_id:
            self.industry(industry_id, user_id)
            query = query.where(CommunityPublication.industry_id == industry_id)
        if mine:
            query = select(CommunityPublication).where(CommunityPublication.user_id == user_id)
        domains = (
            {
                r.domain
                for r in self.session.scalars(
                    select(CommunityIndustry)
                    .join(CommunityMembership)
                    .where(CommunityMembership.user_id == user_id)
                )
            }
            if user_id
            else set()
        )
        profile = self.session.get(Profile, user_id) if user_id else None
        if profile:
            domains.add(profile.industry_l1_code)

        if query_text.strip():
            query = query.where(
                or_(
                    CommunityPublication.body["title"]
                    .as_string()
                    .contains(query_text.strip(), autoescape=True),
                    CommunityPublication.body["summary"]
                    .as_string()
                    .contains(query_text.strip(), autoescape=True),
                )
            )
        if domains and not mine and sort == "recommended":
            query = query.order_by(case((CommunityIndustry.domain.in_(domains), 0), else_=1))
        rows = list(
            self.session.scalars(
                query.order_by(
                    CommunityPublication.created_at.asc()
                    if sort == "oldest"
                    else CommunityPublication.created_at.desc(),
                    CommunityPublication.id,
                )
                .offset(offset)
                .limit(limit)
            )
        )

        self._views = {row.id: 0 for row in rows}
        for metric in self.session.scalars(
            select(CommunityReportMetric).where(
                CommunityReportMetric.publication_id.in_([row.id for row in rows])
            )
        ):
            self._views[metric.publication_id] = metric.views_count

        def relevant(row: CommunityPublication) -> bool:
            industry = (
                self.session.get(CommunityIndustry, row.industry_id) if row.industry_id else None
            )
            return bool(industry and industry.domain in domains)

        return [
            self.report_view(
                row,
                user_id,
                ("与你的画像或关注行业相关" if relevant(row) else "探索其他行业")
                if user_id
                else "",
            )
            for row in rows
        ]

    def preview(
        self, user_id: UUID, report_id: UUID, version_id: UUID, industry_id: UUID | None
    ) -> dict[str, Any]:
        industry = self.industry(industry_id, user_id) if industry_id else None
        body = ReportRepository(self.session, self.config).report(user_id, report_id, version_id)
        sections = []
        public_topic_title = ""
        for identifier in body.forecast_version_ids:
            row = self.session.get(ForecastVersion, identifier)
            world = self.session.get(WorldForecast, row.forecast_id) if row else None
            topic = self.session.get(ResearchTopic, world.topic_id) if world else None
            if row is None or topic is None or topic.owner_user_id is not None:
                raise EvidenceError(
                    "PRIVATE_SOURCE_NOT_SHAREABLE", "这份报告含有私有研究资料，暂不能公开", 409
                )
            if not public_topic_title:
                public_topic_title = topic.title
            sections.append({"heading": "行业观察", "text": row.statement})
            sections.append(
                {
                    "heading": "前提与不确定性",
                    "text": "；".join(row.body.get("assumptions", []))
                    or "结论尚未校准，不能作为确定结果。",
                }
            )
            sections.append(
                {
                    "heading": "哪些变化会推翻判断",
                    "text": "；".join(row.body.get("falsification_conditions", [])),
                }
            )
        if not sections:
            raise EvidenceError("SHARE_CONTENT_EMPTY", "没有可公开的行业研究内容", 409)
        return {
            "title": (industry.name if industry else public_topic_title) + " · 行业观察",
            "summary": "从报告中提取的行业研究内容，不包含作者的个人画像、私人影响分析和行动建议。",
            "label": body.label,
            "sample": False,
            "image": "report-code.webp",
            "sections": sections,
        }

    def publish(
        self, user_id: UUID, report_id: UUID, data: CommunityPublishV1
    ) -> CommunityReportViewV1:
        self.fence(user_id)
        industry = self.industry(data.industry_id, user_id) if data.industry_id else None
        if industry is not None and not industry.public:
            raise EvidenceError(
                "INDUSTRY_PRIVATE",
                "请先公开行业，或选择已有公开行业；公开报告不会自动公开行业",
                409,
            )
        snapshot = self.preview(user_id, report_id, data.report_version_id, data.industry_id)
        row = self.session.scalar(
            select(CommunityPublication).where(CommunityPublication.report_id == report_id)
        )
        if row is None:
            row = CommunityPublication(
                id=uuid4(),
                user_id=user_id,
                report_id=report_id,
                industry_id=data.industry_id,
                body=snapshot,
            )
            self.session.add(row)
        row.industry_id, row.report_version_id, row.body, row.public = (
            data.industry_id,
            data.report_version_id,
            snapshot,
            True,
        )
        self.session.commit()
        return self.report_view(row, user_id)

    def withdraw(self, user_id: UUID, identifier: UUID) -> None:
        self.fence(user_id)
        row = self.session.scalar(
            select(CommunityPublication).where(
                CommunityPublication.id == identifier, CommunityPublication.user_id == user_id
            )
        )
        if row is None:
            raise EvidenceError("PUBLIC_REPORT_NOT_FOUND", "公开记录不存在", 404)
        row.public = False
        self.session.commit()

    def bookmark(self, user_id: UUID, identifier: UUID, industry_id: UUID | None) -> None:
        self.fence(user_id)
        if industry_id is None:
            self.session.execute(
                delete(CommunityBookmark).where(
                    CommunityBookmark.user_id == user_id,
                    CommunityBookmark.publication_id == identifier,
                )
            )
            self.session.commit()
            return
        row = self.publication(identifier, user_id)
        was_saved = self.session.get(CommunityBookmark, (user_id, identifier)) is not None
        self.session.execute(
            delete(CommunityBookmark).where(
                CommunityBookmark.user_id == user_id, CommunityBookmark.publication_id == row.id
            )
        )
        if industry_id:
            self.industry(industry_id, user_id)
            if self.session.get(CommunityMembership, (user_id, industry_id)) is None:
                self.session.add(CommunityMembership(user_id=user_id, industry_id=industry_id))
            self.session.add(
                CommunityBookmark(user_id=user_id, publication_id=row.id, industry_id=industry_id)
            )
        if not was_saved:
            from infra.consumer_social import ConsumerSocial

            ConsumerSocial(self.session, self.config).notify(user_id, row, "bookmark")
        self.session.commit()

    def saved(self, user_id: UUID, industry_id: UUID | None = None) -> list[CommunityReportViewV1]:
        query = select(CommunityBookmark).where(CommunityBookmark.user_id == user_id)
        if industry_id:
            query = query.where(CommunityBookmark.industry_id == industry_id)
        result = []
        for entry in self.session.scalars(query.order_by(CommunityBookmark.created_at.desc())):
            try:
                result.append(
                    self.report_view(self.publication(entry.publication_id, user_id), user_id)
                )
            except EvidenceError:
                continue
        return result
