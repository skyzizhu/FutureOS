"""Consumer industries, explicit public snapshots, collections and encrypted conversations."""

from alembic import op
from sqlalchemy.orm import Session

from infra.community_seed import seed_community
from infra.db import Base

revision = "0015_consumer"
down_revision = "0014_email"
branch_labels = None
depends_on = None
TABLES = (
    "community_industries",
    "community_memberships",
    "community_publications",
    "community_bookmarks",
    "research_conversations",
    "community_private_reports",
)


def upgrade() -> None:
    connection = op.get_bind()
    for name in TABLES:
        Base.metadata.tables[name].create(connection)
    with Session(bind=connection) as session:
        seed_community(session)
        session.commit()


def downgrade() -> None:
    connection = op.get_bind()
    for name in TABLES:
        predicate = (
            " WHERE user_id IS NOT NULL"
            if name in {"community_industries", "community_publications"}
            else ""
        )
        count = connection.exec_driver_sql(f"SELECT count(*) FROM {name}{predicate}").scalar()
        if count:
            raise RuntimeError("CONSUMER_DATA_REQUIRES_FORWARD_REPAIR")
    for name in reversed(TABLES):
        op.drop_table(name)
