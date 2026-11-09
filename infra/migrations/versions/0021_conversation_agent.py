"""Allow unscoped conversations, persist profile-industry links and bound chat model calls."""

import sqlalchemy as sa
from alembic import op

revision = "0021_conversation_agent"
down_revision = "0020_auth_access"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("research_conversations") as batch:
        batch.alter_column("industry_id", existing_type=sa.Uuid(), nullable=True)
    op.create_table(
        "profile_industries",
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id"), primary_key=True),
        sa.Column(
            "industry_id", sa.Uuid(), sa.ForeignKey("community_industries.id"), nullable=False
        ),
    )
    op.create_table(
        "chat_model_budgets",
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id"), primary_key=True),
        sa.Column("window_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("turns", sa.Integer(), nullable=False),
        sa.Column("lease_id", sa.Uuid(), nullable=True),
        sa.Column("lease_until", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    bind = op.get_bind()
    if (
        bind.exec_driver_sql(
            "SELECT count(*) FROM research_conversations WHERE industry_id IS NULL"
        ).scalar()
        or bind.exec_driver_sql("SELECT count(*) FROM profile_industries").scalar()
        or bind.exec_driver_sql("SELECT count(*) FROM chat_model_budgets").scalar()
    ):
        raise RuntimeError("CONVERSATION_AGENT_REQUIRES_FORWARD_REPAIR")
    op.drop_table("chat_model_budgets")
    op.drop_table("profile_industries")
    with op.batch_alter_table("research_conversations") as batch:
        batch.alter_column("industry_id", existing_type=sa.Uuid(), nullable=False)
