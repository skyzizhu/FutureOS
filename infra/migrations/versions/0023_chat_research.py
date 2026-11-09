"""Private industry research runs owned by conversations."""

import sqlalchemy as sa
from alembic import op

revision = "0023_chat_research"
down_revision = "0022_chat_harness"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "chat_industry_research",
        sa.Column("job_id", sa.Uuid(), sa.ForeignKey("jobs.id"), primary_key=True),
        sa.Column(
            "conversation_id",
            sa.Uuid(),
            sa.ForeignKey("research_conversations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("scope_ciphertext", sa.Text(), nullable=False),
        sa.Column("result_ciphertext", sa.Text(), nullable=True),
        sa.Column("stages", sa.JSON(), nullable=False),
    )
    op.create_index(
        "ix_chat_industry_research_conversation_id", "chat_industry_research", ["conversation_id"]
    )


def downgrade() -> None:
    if op.get_bind().exec_driver_sql("SELECT count(*) FROM chat_industry_research").scalar():
        raise RuntimeError("CHAT_RESEARCH_REQUIRES_FORWARD_REPAIR")
    op.drop_table("chat_industry_research")
