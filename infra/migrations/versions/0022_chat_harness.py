"""Bound chat model admission across accounts and server processes."""

import sqlalchemy as sa
from alembic import op

revision = "0022_chat_harness"
down_revision = "0021_conversation_agent"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "chat_model_global_budget",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=False),
        sa.Column("window_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("turns", sa.Integer(), nullable=False),
    )
    op.create_index("ix_chat_model_budgets_lease_until", "chat_model_budgets", ["lease_until"])


def downgrade() -> None:
    op.drop_index("ix_chat_model_budgets_lease_until", table_name="chat_model_budgets")
    op.drop_table("chat_model_global_budget")
