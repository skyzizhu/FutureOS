"""Allow explicitly published reports without a public industry destination."""

import sqlalchemy as sa
from alembic import op

revision = "0024_standalone_reports"
down_revision = "0023_chat_research"
branch_labels = None
depends_on = None

TABLE = "community_publications"


def change_nullable(nullable: bool) -> None:
    connection = op.get_bind()
    if connection.dialect.name != "sqlite":
        op.alter_column(TABLE, "industry_id", existing_type=sa.Uuid(), nullable=nullable)
        return
    column = next(
        column
        for column in sa.inspect(connection).get_columns(TABLE)
        if column["name"] == "industry_id"
    )
    if column["nullable"] == nullable:
        return
    # SQLite rebuilds the parent table. Keep its bookmarked/read child rows intact.
    with op.get_context().autocommit_block():
        connection.exec_driver_sql("PRAGMA foreign_keys=OFF")
        connection.exec_driver_sql("BEGIN")
        try:
            with op.batch_alter_table(TABLE) as batch:
                batch.alter_column("industry_id", existing_type=sa.Uuid(), nullable=nullable)
            connection.exec_driver_sql("COMMIT")
        except BaseException:
            connection.exec_driver_sql("ROLLBACK")
            raise
        finally:
            connection.exec_driver_sql("PRAGMA foreign_keys=ON")


def upgrade() -> None:
    change_nullable(True)


def downgrade() -> None:
    if (
        op.get_bind()
        .exec_driver_sql("SELECT count(*) FROM community_publications WHERE industry_id IS NULL")
        .scalar()
    ):
        raise RuntimeError("STANDALONE_REPORTS_REQUIRE_FORWARD_REPAIR")
    change_nullable(False)
