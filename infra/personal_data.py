"""Reauthentication, transaction-fenced erasure and owner-only complete private export."""

import json
from datetime import datetime, timedelta
from uuid import UUID, uuid4

from prediction_engine.contracts.models import PersonalDataErasedV1, PersonalDataEraseV1
from sqlalchemy import delete, or_, select, update
from sqlalchemy.orm import Session

from infra.accounts import AccountRepository, password_matches, token_hash, vault_for
from infra.billing import BillingRepository
from infra.db import (
    AuthAccessEvent,
    AuthAccount,
    AuthAttempt,
    AuthSession,
    Base,
    CommerceCheckout,
    CommerceLedger,
    CommunityActivity,
    CommunityBookmark,
    CommunityIndustry,
    CommunityIndustryCopy,
    CommunityLike,
    CommunityMembership,
    CommunityPrivateReport,
    CommunityPublication,
    ConsumerPreference,
    IndustryTracking,
    Job,
    PaidSubscription,
    PrivacyErasure,
    Profile,
    ProfileSnapshot,
    ResearchConversation,
    ResearchScopeQuote,
    SharedTopicStudy,
    User,
    UserReportVersion,
    UserResearchTopic,
    utcnow,
)
from infra.erasure_journal import append_tombstone
from infra.erasure_policy import DELETE_TABLES
from infra.evidence_repository import EvidenceError, columns
from infra.profiles import ProfileRepository
from infra.reports import ReportRepository
from infra.settings import Settings


def export_private(session: Session, user_id: UUID, config: Settings) -> dict[str, object]:
    session.scalar(select(User).where(User.id == user_id).with_for_update(key_share=True))
    account = session.get(AuthAccount, user_id)
    if account is None:
        raise EvidenceError("LOCAL_ACCOUNT_REQUIRED", "请使用注册账号", 403)
    profile = (
        ProfileRepository(session, config).view(user_id) if session.get(Profile, user_id) else None
    )
    repo = ReportRepository(session, config)
    reports = [
        repo.report(user_id, row.report_id, row.id).model_dump(mode="json")
        for row in session.scalars(
            select(UserReportVersion).where(UserReportVersion.user_id == user_id)
        )
    ]
    snapshots = [
        ProfileRepository(session, config).read_snapshot(row.id, user_id).model_dump(mode="json")
        for row in session.scalars(
            select(ProfileSnapshot).where(ProfileSnapshot.user_id == user_id)
        )
    ]
    data: dict[str, object] = {
        "exported_at": utcnow().isoformat(),
        "profile": profile.model_dump(mode="json") if profile else None,
        "account": {
            "user_id": str(user_id),
            "email": AccountRepository(session, config).recipient(user_id),
        },
        "reports": reports,
        "profile_snapshots": snapshots,
        "recommendations": [
            {
                "recommendation": row["recommendation"].model_dump(mode="json"),
                "feedback": row["feedback"],
            }
            for row in repo.recommendations(user_id)
        ],
        "billing_ledger": [
            json.loads(json.dumps(columns(r), default=str))
            for r in session.scalars(
                select(CommerceLedger).where(CommerceLedger.user_id == user_id)
            )
        ],
        "scopes": [
            r.body
            for r in session.scalars(
                select(ResearchScopeQuote).where(ResearchScopeQuote.user_id == user_id)
            )
        ],
    }
    vault = vault_for(session, config)
    data["auth_access_events"] = [
        {
            **vault.open(row.context_ciphertext, "auth-access:" + str(row.id)),
            "action": row.action,
            "created_at": row.created_at,
            "request_id": row.request_id,
            "fingerprint": row.device_hash,
        }
        for row in session.scalars(
            select(AuthAccessEvent).where(
                AuthAccessEvent.user_id == user_id,
                AuthAccessEvent.outcome == "succeeded",
                AuthAccessEvent.created_at
                >= utcnow() - timedelta(days=config.auth_access_retention_days),
            )
        )
    ]
    from infra.chat_research import ChatResearchRepository
    from infra.conversations import ConversationRepository

    conversations = ConversationRepository(session, config)
    chat_research = ChatResearchRepository(session, config)
    exported_chats = []
    for row in session.scalars(
        select(ResearchConversation).where(ResearchConversation.user_id == user_id)
    ):
        item = conversations.view(user_id, row.id, include_harness=True)
        item["industry_research"] = [
            run.model_dump(mode="json") for run in chat_research.list(row, export=True)
        ]
        exported_chats.append(item)
    data["conversations"] = exported_chats
    data["community_industries"] = [
        columns(row)
        for row in session.scalars(
            select(CommunityIndustry)
            .join(CommunityMembership)
            .where(CommunityMembership.user_id == user_id)
        )
    ]
    data["community_publications"] = [
        columns(row)
        for row in session.scalars(
            select(CommunityPublication).where(CommunityPublication.user_id == user_id)
        )
    ]
    data["community_bookmarks"] = [
        columns(row)
        for row in session.scalars(
            select(CommunityBookmark).where(CommunityBookmark.user_id == user_id)
        )
    ]
    data["private_report_folders"] = [
        columns(row)
        for row in session.scalars(
            select(CommunityPrivateReport).where(CommunityPrivateReport.user_id == user_id)
        )
    ]
    for key, model in (
        ("industry_copies", CommunityIndustryCopy),
        ("industry_tracking", IndustryTracking),
        ("likes", CommunityLike),
        ("appearance", ConsumerPreference),
    ):
        data[key] = [
            columns(row) for row in session.scalars(select(model).where(model.user_id == user_id))
        ]
    from infra.consumer_social import ConsumerSocial

    data["community_notifications"] = [
        row.model_dump(mode="json") for row in ConsumerSocial(session, config).inbox(user_id)
    ]
    data = json.loads(json.dumps(data, default=str))
    if len(json.dumps(data, ensure_ascii=False).encode()) > config.export_max_bytes:
        raise EvidenceError("EXPORT_TOO_LARGE", "导出超过本地安全上限，需要分批处理", 413)
    return data


def erase_private(
    session: Session, user_id: UUID, data: PersonalDataEraseV1, config: Settings
) -> PersonalDataErasedV1:
    from infra.db import AdminAccess

    if session.get(AdminAccess, user_id):
        raise EvidenceError("ADMIN_ACCOUNT_MANAGED", "管理员账号请使用管理停用流程", 403)
    session.scalar(select(User).where(User.id == user_id).with_for_update(key_share=True))
    account = session.get(AuthAccount, user_id)
    if account is None:
        raise EvidenceError("LOCAL_ACCOUNT_REQUIRED", "请使用注册账号", 403)
    # Same bounded KDF/rate controls as login; a captured session alone cannot erase data.
    AccountRepository(session, config).attempt(account.email_lookup)
    session.scalar(select(User).where(User.id == user_id).with_for_update(key_share=True))
    session.expire_all()
    account = session.get(AuthAccount, user_id)
    if account is None or not password_matches(data.password, account.password_hash):
        raise EvidenceError("REAUTH_REQUIRED", "密码不匹配，未删除任何资料", 401)
    return apply_erasure(session, user_id, config)


def apply_erasure(
    session: Session,
    user_id: UUID,
    config: Settings,
    erasure_id: UUID | None = None,
    erased_at: datetime | None = None,
) -> PersonalDataErasedV1:
    session.scalar(select(User).where(User.id == user_id).with_for_update(key_share=True))
    identifier, now = erasure_id or uuid4(), erased_at or utcnow()
    account = session.get(AuthAccount, user_id)
    lookup = account.email_lookup if account else None
    counts: dict[str, int] = {}
    # Cancel owned pending jobs with the same user→Job order as M6 settlement.
    for job in session.scalars(select(Job).where(Job.user_id == user_id).with_for_update()):
        if job.status in {"queued", "running", "failed_retryable"}:
            if job.task_type == "m4_report":
                ReportRepository(session, config).release(job.id)
            elif job.task_type == "m6_research":
                BillingRepository(session, config).release(job.id)
            job.status = "cancelled"
        job.lease_token = job.lease_until = None
        job.payload, job.result = {"erased": True, "label": "DEMO"}, None
        job.input_hash, job.idempotency_key = "0" * 64, "erased:" + str(job.id)
        job.error_code = "ACCOUNT_ERASED"
    for subscription in session.scalars(
        select(PaidSubscription).where(PaidSubscription.user_id == user_id)
    ):
        subscription.cancel_at_period_end = True
    for topic in session.scalars(
        select(UserResearchTopic).where(UserResearchTopic.user_id == user_id)
    ):
        # No original personal scope link is retained in the financial request graph.
        redacted = session.get(SharedTopicStudy, "0" * 64)
        if redacted is None:
            session.add(SharedTopicStudy(scope_fingerprint="0" * 64, scope={"erased": True}))
            session.flush()
        topic.scope_fingerprint = "0" * 64
        topic.latest_report_id = None
        topic.subscription_id = None
        topic.periodic_enabled = False
        topic.next_run_at = None
        topic.last_error = "ACCOUNT_ERASED"
    for industry in session.scalars(
        select(CommunityIndustry).where(CommunityIndustry.user_id == user_id)
    ):
        industry.name = "已撤回行业"
        industry.description = "原分享者已删除资料，请重新整理关注范围。"
        industry.public, industry.user_id = False, None
    session.flush()
    # The audit receipt authorizes ONLY deletes of this user's private graph and exact tombstones.
    receipt = PrivacyErasure(id=identifier, user_id=user_id, erased_at=now, counts={})
    session.add(receipt)
    session.flush()
    changed_activity = session.connection().execute(
        delete(CommunityActivity).where(
            or_(
                CommunityActivity.recipient_user_id == user_id,
                CommunityActivity.actor_user_id == user_id,
            )
        )
    )
    counts["community_activities"] = changed_activity.rowcount
    for name in DELETE_TABLES:
        table = Base.metadata.tables[name]
        if "user_id" in table.c:
            predicate = table.c.user_id == user_id
        elif name == "report_version_forecasts":
            predicate = table.c.report_version_id.in_(
                select(UserReportVersion.id).where(UserReportVersion.user_id == user_id)
            )
        elif name in {"mail_attempts", "mail_bounces"}:
            deliveries = Base.metadata.tables["mail_deliveries"]
            predicate = table.c.delivery_id.in_(
                select(deliveries.c.id).where(deliveries.c.user_id == user_id)
            )
        else:
            predicate = table.c.job_id.in_(select(Job.id).where(Job.user_id == user_id))
        changed = session.connection().execute(delete(table).where(predicate))
        counts[name] = changed.rowcount
    changed = session.connection().execute(
        update(ProfileSnapshot)
        .where(ProfileSnapshot.user_id == user_id)
        .values(ciphertext="ERASED", snapshot_hash="0" * 64)
    )
    counts["profile_snapshots_scrubbed"] = changed.rowcount
    session.execute(delete(Profile).where(Profile.user_id == user_id))
    session.execute(delete(AuthSession).where(AuthSession.user_id == user_id))
    if lookup:
        from infra.db import AuthEmailCode

        session.execute(delete(AuthEmailCode).where(AuthEmailCode.email_lookup == lookup))
        session.execute(
            delete(AuthAttempt).where(
                AuthAttempt.identity_hash.in_(
                    (
                        lookup,
                        *(
                            token_hash(prefix + lookup)
                            for prefix in (
                                "email-send:",
                                "password-reset:",
                                "human-login:",
                            )
                        ),
                    )
                )
            )
        )
    session.execute(
        delete(AuthAccessEvent).where(
            or_(AuthAccessEvent.user_id == user_id, AuthAccessEvent.identity_hash == lookup)
            if lookup
            else AuthAccessEvent.user_id == user_id
        )
    )
    from infra.db import AdminAccess, AdminMFA, AuthChallenge

    session.execute(delete(AuthChallenge).where(AuthChallenge.user_id == user_id))
    session.execute(delete(AdminMFA).where(AdminMFA.user_id == user_id))
    session.execute(delete(AdminAccess).where(AdminAccess.user_id == user_id))
    session.execute(delete(AuthAccount).where(AuthAccount.user_id == user_id))
    # Financial checkout snapshots remain, but arbitrary client idempotency keys are removed.
    for checkout in session.scalars(
        select(CommerceCheckout).where(CommerceCheckout.user_id == user_id)
    ):
        checkout.idempotency_key = "erased:" + str(checkout.id)
        checkout.input_hash = "0" * 64
    # Receipt is append-only: finalize counts with a fresh INSERT rather than UPDATE.
    # counts describe observable cleared categories in the response; audit keeps identity/time only.
    append_tombstone(config.profile_key_path, user_id, identifier, now.isoformat())
    session.commit()
    return PersonalDataErasedV1(
        erasure_id=identifier,
        erased_at=now,
        cleared_records=counts,
        retained=(
            "不含邮箱、画像或报告正文的随机用户ID与必要额度/订单审计",
            "公开共享研究与匿名系统计量",
        ),
        backup_notice="历史加密备份可能保留旧资料；恢复时必须重放删除登记，备份到期后清除。",
    )
