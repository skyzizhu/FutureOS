"""Store public report read totals and short-lived daily deduplication hashes."""

import sqlalchemy as sa
from alembic import op

revision = "0019_reads"
down_revision = "0018_tech_roles"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "community_report_metrics",
        sa.Column(
            "publication_id",
            sa.Uuid(),
            sa.ForeignKey("community_publications.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("views_count", sa.BigInteger(), nullable=False),
    )
    op.create_table(
        "community_report_reads",
        sa.Column(
            "publication_id",
            sa.Uuid(),
            sa.ForeignKey("community_publications.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("day", sa.Date(), primary_key=True),
        sa.Column("visitor_hash", sa.String(64), primary_key=True),
    )
    op.create_index("ix_community_report_reads_day", "community_report_reads", ["day"])


def downgrade() -> None:
    if op.get_bind().exec_driver_sql("SELECT count(*) FROM community_report_metrics").scalar():
        raise RuntimeError("REPORT_READS_REQUIRE_FORWARD_REPAIR")
    op.drop_table("community_report_reads")
    op.drop_table("community_report_metrics")
