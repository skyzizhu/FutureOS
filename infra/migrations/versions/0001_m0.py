"""M0: users, jobs and generic events only; no future milestone business tables."""

import sqlalchemy as sa
from alembic import op

revision = "0001_m0"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("auth_subject", sa.String(200), nullable=False, unique=True),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("role IN ('user','admin')", name="ck_user_role"),
    )
    op.create_table(
        "jobs",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("request_id", sa.Uuid(), nullable=False, unique=True),
        sa.Column("trace_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("task_type", sa.String(80), nullable=False),
        sa.Column("idempotency_key", sa.String(128), nullable=False),
        sa.Column("input_hash", sa.String(64), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(30), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False),
        sa.Column("lease_token", sa.Uuid(), nullable=True),
        sa.Column("lease_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("available_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("result", sa.JSON(), nullable=True),
        sa.Column("error_code", sa.String(80), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("user_id", "idempotency_key", name="uq_job_user_key"),
        sa.CheckConstraint("attempts >= 0", name="ck_job_attempts"),
        sa.CheckConstraint(
            "status IN ('queued','running','succeeded','failed_retryable',"
            "'failed_terminal','cancelled')",
            name="ck_job_status",
        ),
    )
    op.create_index("ix_jobs_user_id", "jobs", ["user_id"])
    op.create_index("ix_jobs_status", "jobs", ["status"])
    op.create_table(
        "outbox_events",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("job_id", sa.Uuid(), sa.ForeignKey("jobs.id"), nullable=False),
        sa.Column("event_type", sa.String(80), nullable=False),
        sa.Column("payload_version", sa.Integer(), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("emitted_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_outbox_events_job_id", "outbox_events", ["job_id"])
    op.create_table(
        "inbox_processed",
        sa.Column("consumer", sa.String(80), primary_key=True),
        sa.Column("event_id", sa.Uuid(), sa.ForeignKey("outbox_events.id"), primary_key=True),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    for table in ["inbox_processed", "outbox_events", "jobs", "users"]:
        op.drop_table(table)
