"""Owned industry copies and durable interactions; no mail or provider dispatch."""

from datetime import timedelta
from hashlib import sha256
from typing import Literal, cast
from uuid import UUID, uuid4
from zoneinfo import ZoneInfo

from prediction_engine.contracts.models import (
    CommunityActivityV1,
    CommunityIndustryViewV1,
    ConsumerPreferenceV1,
    IndustryTrackingV1,
    IndustryTrackingViewV1,
)
from prediction_engine.evidence.temporal import utc
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from infra.community import CommunityRepository
from infra.db import (
    CommunityActivity,
    CommunityIndustry,
    CommunityIndustryCopy,
    CommunityLike,
    CommunityMembership,
    CommunityPublication,
    CommunityReportMetric,
    CommunityReportRead,
    ConsumerPreference,
    IndustryTracking,
    utcnow,
)
from infra.evidence_repository import EvidenceError
from infra.settings import Settings


class ConsumerSocial:
    def __init__(self, session: Session, config: Settings):
        self.session, self.config = session, config
        self.community = CommunityRepository(session, config)

    def add_industry(
        self, user_id: UUID, identifier: UUID, commit: bool = True
    ) -> CommunityIndustryViewV1:
        self.community.fence(user_id)
        source = self.community.industry(identifier, user_id)
        link = self.session.get(CommunityIndustryCopy, (user_id, identifier))
        if source.user_id == user_id:
            target = source
        elif link:
            existing_target = self.session.get(CommunityIndustry, link.industry_id)
            assert existing_target
            target = existing_target
        else:
            if not source.public:
                raise EvidenceError("INDUSTRY_NOT_FOUND", "该行业未公开", 404)
            target = CommunityIndustry(
                id=uuid4(),
                user_id=user_id,
                name=source.name,
                description=source.description,
                domain=source.domain,
                public=False,
            )
            self.session.add(target)
            self.session.flush()
            self.session.add(
                CommunityIndustryCopy(
                    user_id=user_id, source_industry_id=identifier, industry_id=target.id
                )
            )
        if self.session.get(CommunityMembership, (user_id, target.id)) is None:
            self.session.add(CommunityMembership(user_id=user_id, industry_id=target.id))
        if self.session.get(IndustryTracking, (user_id, target.id)) is None:
            self.session.add(IndustryTracking(user_id=user_id, industry_id=target.id))
        # Replace the legacy follow entry, while leaving existing private report folders intact.
        if source.id != target.id:
            self.session.execute(
                delete(CommunityMembership).where(
                    CommunityMembership.user_id == user_id,
                    CommunityMembership.industry_id == source.id,
                )
            )
        self.session.flush()
        if commit:
            self.session.commit()
        return self.community.industry_view(target, user_id)

    def preference(
        self, user_id: UUID, data: ConsumerPreferenceV1 | None = None
    ) -> ConsumerPreferenceV1:
        if data is not None:
            self.community.fence(user_id)
        row = self.session.get(ConsumerPreference, user_id)
        if data is not None:
            if row is None:
                row = ConsumerPreference(user_id=user_id, theme=data.theme)
                self.session.add(row)
            row.theme = data.theme
            self.session.commit()
        return ConsumerPreferenceV1.model_validate({"theme": row.theme if row else "system"})

    def tracking(
        self, user_id: UUID, identifier: UUID, data: IndustryTrackingV1 | None = None
    ) -> IndustryTrackingViewV1:
        self.community.industry(identifier, user_id)
        row_industry = self.session.get(CommunityIndustry, identifier)
        if row_industry is None or row_industry.user_id != user_id:
            raise EvidenceError("INDUSTRY_NOT_FOUND", "请先添加为自己的行业", 404)
        if data is not None:
            self.community.fence(user_id)
        row = self.session.get(IndustryTracking, (user_id, identifier))
        if data is not None:
            if row is None:
                row = IndustryTracking(user_id=user_id, industry_id=identifier)
                self.session.add(row)
            row.monitor_enabled, row.prediction_enabled, row.email_enabled = (
                data.monitor_enabled,
                data.prediction_enabled,
                data.email_enabled,
            )
            row.updated_at = utcnow()
            self.session.commit()
        body = data or IndustryTrackingV1(
            monitor_enabled=row.monitor_enabled if row else True,
            prediction_enabled=row.prediction_enabled if row else True,
            email_enabled=row.email_enabled if row else False,
        )
        return IndustryTrackingViewV1(
            industry_id=identifier,
            **body.model_dump(exclude={"schema_version"}),
            status="waiting_rules" if body.monitor_enabled or body.prediction_enabled else "paused",
        )

    def like(self, user_id: UUID, identifier: UUID, enabled: bool) -> None:
        self.community.fence(user_id)
        if enabled:
            publication = self.community.publication(identifier, user_id)
            if self.session.get(CommunityLike, (user_id, identifier)) is None:
                self.session.add(CommunityLike(user_id=user_id, publication_id=identifier))
                self.notify(user_id, publication, "like")
        else:
            self.session.execute(
                delete(CommunityLike).where(
                    CommunityLike.user_id == user_id, CommunityLike.publication_id == identifier
                )
            )
        self.session.commit()

    def notify(self, actor: UUID, publication: CommunityPublication, kind: str) -> None:
        owner = publication.user_id
        if owner is None or owner == actor:
            return
        prior = self.session.scalar(
            select(CommunityActivity.id).where(
                CommunityActivity.recipient_user_id == owner,
                CommunityActivity.actor_user_id == actor,
                CommunityActivity.publication_id == publication.id,
                CommunityActivity.kind == kind,
            )
        )
        if prior is None:
            self.session.add(
                CommunityActivity(
                    id=uuid4(),
                    recipient_user_id=owner,
                    actor_user_id=actor,
                    publication_id=publication.id,
                    kind=kind,
                )
            )

    def inbox(self, user_id: UUID) -> list[CommunityActivityV1]:
        result = []
        for row in self.session.scalars(
            select(CommunityActivity)
            .where(CommunityActivity.recipient_user_id == user_id)
            .order_by(CommunityActivity.created_at.desc())
            .limit(100)
        ):
            publication = self.session.get(CommunityPublication, row.publication_id)
            if publication is None:
                continue
            action = "点赞" if row.kind == "like" else "收藏"
            result.append(
                CommunityActivityV1(
                    id=row.id,
                    publication_id=row.publication_id,
                    kind=cast(Literal["like", "bookmark"], row.kind),
                    title="你的公开报告收到了" + action,
                    summary="一位读者" + action + "了《" + publication.body["title"] + "》。",
                    created_at=utc(row.created_at),
                    read=row.read_at is not None,
                )
            )
        return result

    def read(self, user_id: UUID, identifier: UUID) -> None:
        row = self.session.scalar(
            select(CommunityActivity).where(
                CommunityActivity.id == identifier, CommunityActivity.recipient_user_id == user_id
            )
        )
        if row is None:
            raise EvidenceError("NOTIFICATION_NOT_FOUND", "通知不存在", 404)
        row.read_at = utcnow()
        self.session.commit()

    def record_read(self, identifier: UUID, visitor: UUID) -> None:
        publication = self.community.publication(identifier)
        # Serialize deduplication and aggregate updates on the public report row.
        self.session.refresh(publication, with_for_update=True)
        self.community.publication(identifier)
        day = utcnow().astimezone(ZoneInfo("Asia/Shanghai")).date()
        digest = sha256(f"{identifier}:{day}:{visitor}".encode()).hexdigest()
        if self.session.get(CommunityReportRead, (identifier, day, digest)) is None:
            self.session.add(
                CommunityReportRead(publication_id=identifier, day=day, visitor_hash=digest)
            )
            metric = self.session.get(CommunityReportMetric, identifier)
            if metric is None:
                metric = CommunityReportMetric(publication_id=identifier, views_count=0)
                self.session.add(metric)
            metric.views_count += 1
        self.session.execute(
            delete(CommunityReportRead).where(CommunityReportRead.day < day - timedelta(days=1))
        )
        self.session.commit()

    def download(self, user_id: UUID, identifier: UUID) -> str:
        row = self.community.publication(identifier, user_id)
        industry = self.session.get(CommunityIndustry, row.industry_id) if row.industry_id else None
        body = row.body
        lines = [
            "# " + body["title"],
            "",
            "行业：" + industry.name if industry else "发布方式：独立公开报告",
            "",
            "资料：" + ("演示资料" if body["label"] == "DEMO" else "真实研究资料"),
            "",
            body["summary"],
            "",
        ]
        for section in body["sections"]:
            lines.extend(["## " + section["heading"], "", section["text"], ""])
        lines.extend(
            [
                "预测包含不确定性。"
                if body["label"] == "REAL"
                else "本文使用演示资料，不构成现实预测或行动建议。",
                "",
            ]
        )
        return "\n".join(lines)
