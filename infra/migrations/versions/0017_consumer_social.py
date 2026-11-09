"""Persist personal industry copies, tracking intents, appearance, likes and author inbox."""

import sqlalchemy as sa
from alembic import op

revision = "0017_social"
down_revision = "0016_profile"
branch_labels = None
depends_on = None
TABLES = (
    "community_industry_copies",
    "consumer_preferences",
    "industry_tracking",
    "community_likes",
    "community_activities",
)


def upgrade() -> None:
    op.create_table(
        "community_industry_copies",
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id"), primary_key=True),
        sa.Column(
            "source_industry_id",
            sa.Uuid(),
            sa.ForeignKey("community_industries.id"),
            primary_key=True,
        ),
        sa.Column(
            "industry_id",
            sa.Uuid(),
            sa.ForeignKey("community_industries.id"),
            nullable=False,
            unique=True,
        ),
    )
    op.create_table(
        "consumer_preferences",
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id"), primary_key=True),
        sa.Column("theme", sa.String(10), nullable=False),
    )
    op.create_table(
        "industry_tracking",
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id"), primary_key=True),
        sa.Column(
            "industry_id", sa.Uuid(), sa.ForeignKey("community_industries.id"), primary_key=True
        ),
        sa.Column("monitor_enabled", sa.Boolean(), nullable=False),
        sa.Column("prediction_enabled", sa.Boolean(), nullable=False),
        sa.Column("email_enabled", sa.Boolean(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "community_likes",
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id"), primary_key=True),
        sa.Column(
            "publication_id",
            sa.Uuid(),
            sa.ForeignKey("community_publications.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_community_likes_publication_id", "community_likes", ["publication_id"])
    op.create_table(
        "community_activities",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("recipient_user_id", sa.Uuid(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("actor_user_id", sa.Uuid(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column(
            "publication_id",
            sa.Uuid(),
            sa.ForeignKey("community_publications.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("kind", sa.String(16), nullable=False),
        sa.Column("read_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint(
            "recipient_user_id",
            "actor_user_id",
            "publication_id",
            "kind",
            name="uq_community_activity",
        ),
    )
    for column in ("recipient_user_id", "actor_user_id", "publication_id"):
        op.create_index("ix_community_activities_" + column, "community_activities", [column])
    op.execute(
        sa.text(
            "INSERT INTO industry_tracking (user_id, industry_id, monitor_enabled, "
            "prediction_enabled, email_enabled, updated_at) "
            "SELECT user_id, id, true, true, false, CURRENT_TIMESTAMP "
            "FROM community_industries WHERE user_id IS NOT NULL"
        )
    )


def downgrade() -> None:
    connection = op.get_bind()
    for table in TABLES:
        if connection.exec_driver_sql(f"SELECT count(*) FROM {table}").scalar():
            raise RuntimeError("SOCIAL_DATA_REQUIRES_FORWARD_REPAIR")
    for table in reversed(TABLES):
        op.drop_table(table)
