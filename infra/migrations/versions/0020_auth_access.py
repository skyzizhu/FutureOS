"""Add encrypted authentication access events and per-browser throttling."""

import sqlalchemy as sa
from alembic import op

revision = "0020_auth_access"
down_revision = "0019_reads"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("auth_attempts", sa.Column("device_hash", sa.String(64), nullable=True))
    op.create_index("ix_auth_attempts_device_hash", "auth_attempts", ["device_hash"])
    op.create_table(
        "auth_access_events",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("identity_hash", sa.String(64), nullable=False),
        sa.Column("request_id", sa.Uuid(), nullable=False, unique=True),
        sa.Column("action", sa.String(16), nullable=False),
        sa.Column("outcome", sa.String(16), nullable=False),
        sa.Column("reason", sa.String(64), nullable=True),
        sa.Column("device_hash", sa.String(64), nullable=False),
        sa.Column("context_ciphertext", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    for column in ("user_id", "identity_hash", "created_at"):
        op.create_index(f"ix_auth_access_events_{column}", "auth_access_events", [column])


def downgrade() -> None:
    if op.get_bind().exec_driver_sql("SELECT count(*) FROM auth_access_events").scalar():
        raise RuntimeError("AUTH_ACCESS_EVENTS_REQUIRE_FORWARD_REPAIR")
    op.drop_table("auth_access_events")
    op.drop_index("ix_auth_attempts_device_hash", table_name="auth_attempts")
    op.drop_column("auth_attempts", "device_hash")
