"""Index non-leading foreign keys in composite primary keys."""

from alembic import op

revision = "0003_m1_fk_indexes"
down_revision = "0002_m1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index("ix_signal_sources_evidence_claim_id", "signal_sources", ["evidence_claim_id"])
    op.create_index("ix_inbox_processed_event_id", "inbox_processed", ["event_id"])


def downgrade() -> None:
    op.drop_index("ix_inbox_processed_event_id", table_name="inbox_processed")
    op.drop_index("ix_signal_sources_evidence_claim_id", table_name="signal_sources")
