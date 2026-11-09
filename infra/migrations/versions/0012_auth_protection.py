"""Serialize authentication admission and add pseudonymous peer limits."""

import sqlalchemy as sa
from alembic import op

revision = "0012_auth"
down_revision = "0011_m7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("auth_attempts", sa.Column("source_hash", sa.String(64), nullable=True))
    op.create_index("ix_auth_attempts_source_hash", "auth_attempts", ["source_hash"])
    op.create_table("auth_throttle_lock", sa.Column("id", sa.Integer(), primary_key=True))


def downgrade() -> None:
    op.drop_table("auth_throttle_lock")
    op.drop_index("ix_auth_attempts_source_hash", "auth_attempts")
    op.drop_column("auth_attempts", "source_hash")
