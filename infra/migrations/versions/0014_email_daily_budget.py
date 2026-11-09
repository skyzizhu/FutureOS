"""Keep the four-digit proof guessing budget across code resends."""

import sqlalchemy as sa
from alembic import op

revision = "0014_email"
down_revision = "0013_security"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "auth_email_codes",
        sa.Column("failed_attempts", sa.Integer(), server_default="0", nullable=False),
    )
    # Existing short-lived attempts are conservatively included, never reset by upgrade.
    op.execute("UPDATE auth_email_codes SET failed_attempts = attempts")


def downgrade() -> None:
    if (
        op.get_bind()
        .exec_driver_sql("SELECT count(*) FROM auth_email_codes WHERE failed_attempts > 0")
        .scalar()
    ):
        raise RuntimeError("ACTIVE_EMAIL_GUESS_BUDGET_USE_FORWARD_REPAIR")
    op.drop_column("auth_email_codes", "failed_attempts")
