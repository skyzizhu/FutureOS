"""Current editable profile and minimum immutable encrypted snapshots."""

from typing import cast, get_args
from uuid import UUID, uuid4

from prediction_engine.contracts.models import (
    CommunityIndustryDomain,
    CommunityIndustryInputV1,
    ProfileInputV1,
    ProfileSnapshotV1,
    ProfileViewV1,
)
from prediction_engine.evidence.temporal import utc
from prediction_engine.forecasting.workflow import hashed
from prediction_engine.personalization.taxonomy import TAXONOMY_VERSION, industry
from sqlalchemy import select
from sqlalchemy.orm import Session

from infra.accounts import vault_for
from infra.db import Profile, ProfileIndustry, ProfileSnapshot, utcnow
from infra.evidence_repository import EvidenceError
from infra.settings import Settings


class ProfileRepository:
    def __init__(self, session: Session, config: Settings) -> None:
        self.session = session
        self.config = config

    def view(self, user_id: UUID) -> ProfileViewV1:
        row = self.session.get(Profile, user_id)
        if row is None:
            raise EvidenceError("PROFILE_REQUIRED", "请先选择一级和二级行业", 409)
        data = vault_for(self.session, self.config).open(row.ciphertext, "profile:" + str(user_id))
        return ProfileViewV1(
            user_id=user_id,
            profile=ProfileInputV1.model_validate(data),
            revision=row.revision,
            updated_at=utc(row.updated_at),
            taxonomy_version=TAXONOMY_VERSION,
        )

    def save(self, user_id: UUID, data: ProfileInputV1) -> ProfileViewV1:
        from infra.community import CommunityRepository

        community = CommunityRepository(self.session, self.config)
        community.fence(user_id)
        vault = vault_for(self.session, self.config)
        row = self.session.get(Profile, user_id)
        previous = None
        withdraw = False
        if row is not None:
            previous = ProfileInputV1.model_validate(
                vault.open(row.ciphertext, "profile:" + str(user_id))
            )
            withdraw = previous.use_optional_fields and not data.use_optional_fields
        if row is None:
            row = Profile(
                user_id=user_id,
                industry_l1_code=data.industry_l1_code,
                industry_l2_code=data.industry_l2_code,
                ciphertext="",
                revision=0,
            )
            self.session.add(row)
        row.industry_l1_code = data.industry_l1_code
        row.industry_l2_code = data.industry_l2_code
        row.ciphertext = vault.seal(data.model_dump(mode="json"), "profile:" + str(user_id))
        row.revision += 1
        row.updated_at = utcnow()
        mapping = self.session.get(ProfileIndustry, user_id)
        if data.industry_l1_code == "not_applicable":
            if mapping:
                self.session.delete(mapping)
        elif not (
            mapping
            and previous
            and previous.industry_l1_code == data.industry_l1_code
            and previous.industry_l2_code == data.industry_l2_code
            and (
                not data.industry_l2_code.endswith("_other")
                or previous.industry_detail.strip() == data.industry_detail.strip()
            )
        ):
            label: str = industry(data.industry_l1_code, data.industry_l2_code)["label"]
            name = (
                data.industry_detail.strip() if data.industry_l2_code.endswith("_other") else label
            )[:60].rstrip()
            existing = community.find_personal_industry(user_id, name)
            industry_id = (
                existing.id
                if existing
                else community.create(
                    user_id,
                    CommunityIndustryInputV1(
                        name=name,
                        description="由个人行业画像添加，用于整理行业动态与未来趋势。",
                        domain=cast(
                            CommunityIndustryDomain,
                            data.industry_l1_code
                            if data.industry_l1_code in get_args(CommunityIndustryDomain)
                            else "society",
                        ),
                    ),
                    commit=False,
                ).id
            )
            if mapping:
                mapping.industry_id = industry_id
            else:
                self.session.add(ProfileIndustry(user_id=user_id, industry_id=industry_id))
        if withdraw:
            from infra.db import Job
            from infra.reports import ReportRepository

            for job_id in self.session.scalars(
                select(Job.id).where(
                    Job.user_id == user_id,
                    Job.task_type.in_(["m4_report", "m5_report_refresh", "m6_research"]),
                    Job.status.in_(["queued", "running", "failed_retryable"]),
                )
            ):
                job = self.session.get(Job, job_id)
                if job is not None and job.task_type == "m6_research":
                    from infra.billing import BillingRepository

                    BillingRepository(self.session, self.config).cancel_job(
                        user_id, job_id, commit=False
                    )
                else:
                    ReportRepository(self.session, self.config).cancel(
                        user_id, job_id, commit=False
                    )
        self.session.commit()
        return self.view(user_id)

    def snapshot(self, user_id: UUID) -> ProfileSnapshotV1:
        view = self.view(user_id)
        data = view.profile
        if not data.use_optional_fields:
            data = ProfileInputV1(
                industry_l1_code=data.industry_l1_code,
                industry_l2_code=data.industry_l2_code,
                industry_detail=data.industry_detail,
                locale=data.locale,
                timezone=data.timezone,
            )
        # Demographics are optional account information, not forecast inputs.
        # Keep them out of immutable research snapshots even with optional-field consent.
        data = data.model_copy(update={"gender": None, "age": None})
        identifier = uuid4()
        now = utcnow()
        fingerprint = hashed(
            {
                "id": str(identifier),
                "profile": data.model_dump(mode="json"),
                "revision": view.revision,
            }
        )
        result = ProfileSnapshotV1(
            snapshot_id=identifier,
            user_id=user_id,
            profile=data,
            profile_revision=view.revision,
            consent_scope="optional_fields" if data.use_optional_fields else "industry_only",
            created_at=now,
            snapshot_hash=fingerprint,
        )
        vault = vault_for(self.session, self.config)
        self.session.add(
            ProfileSnapshot(
                id=identifier,
                user_id=user_id,
                profile_revision=view.revision,
                ciphertext=vault.seal(
                    result.model_dump(mode="json"),
                    "snapshot:" + str(user_id) + ":" + str(identifier),
                ),
                snapshot_hash=fingerprint,
                created_at=now,
            )
        )
        self.session.flush()
        return result

    def read_snapshot(self, identifier: UUID, user_id: UUID) -> ProfileSnapshotV1:
        row = self.session.scalar(
            select(ProfileSnapshot).where(
                ProfileSnapshot.id == identifier, ProfileSnapshot.user_id == user_id
            )
        )
        if row is None:
            raise EvidenceError("SNAPSHOT_NOT_FOUND", "画像快照不存在", 404)
        data = vault_for(self.session, self.config).open(
            row.ciphertext, "snapshot:" + str(user_id) + ":" + str(identifier)
        )
        result = ProfileSnapshotV1.model_validate(data)
        if result.snapshot_hash != row.snapshot_hash:
            raise EvidenceError("SNAPSHOT_HASH_MISMATCH", "快照校验失败", 409)
        return result
