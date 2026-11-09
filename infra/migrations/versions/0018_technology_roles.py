"""Append requested technology choices without rewriting historical taxonomy rows."""

import sqlalchemy as sa
from alembic import op

revision = "0018_tech_roles"
down_revision = "0017_social"
branch_labels = None
depends_on = None


def upgrade() -> None:
    table = sa.table(
        "industry_taxonomy",
        sa.column("code", sa.String),
        sa.column("parent_code", sa.String),
        sa.column("label", sa.String),
        sa.column("level", sa.Integer),
        sa.column("version", sa.String),
        sa.column("domain_tags", sa.JSON),
    )
    present = set(op.get_bind().scalars(sa.select(table.c.code)))
    for code, label in (
        ("technology_product_management", "产品经理"),
        ("technology_ui_design", "UI设计师"),
    ):
        if code not in present:
            op.bulk_insert(
                table,
                [
                    {
                        "code": code,
                        "parent_code": "technology",
                        "label": label,
                        "level": 2,
                        "version": "futureos-industry-v2.1",
                        "domain_tags": ["technology", "workforce"],
                    }
                ],
            )


def downgrade() -> None:
    if op.get_bind().exec_driver_sql("SELECT count(*) FROM profiles").scalar():
        raise RuntimeError("TECHNOLOGY_ROLES_REQUIRE_FORWARD_REPAIR")
    # Preserve append-only lookup rows; a full schema teardown removes them.
