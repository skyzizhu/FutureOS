from pathlib import Path

from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.config import Config
from alembic.migration import MigrationContext
from sqlalchemy import inspect, text

from infra.db import Base, make_engine
from infra.settings import get_settings


def test_migration_round_trip(tmp_path: Path, monkeypatch):
    url = f"sqlite:///{tmp_path / 'migrate.db'}"
    monkeypatch.setenv("DATABASE_URL", url)
    get_settings.cache_clear()
    config = Config("alembic.ini")
    command.upgrade(config, "head")
    engine = make_engine(url)
    assert set(inspect(engine).get_table_names()) == set(Base.metadata.tables) | {"alembic_version"}
    with engine.connect() as connection:
        assert compare_metadata(MigrationContext.configure(connection), Base.metadata) == []
        labels = dict(
            connection.execute(
                text(
                    "SELECT code, label FROM industry_taxonomy WHERE code IN "
                    "('technology_product_management', 'technology_ui_design')"
                )
            ).all()
        )
        assert labels == {
            "technology_product_management": "产品经理",
            "technology_ui_design": "UI设计师",
        }

    command.downgrade(config, "base")
    assert inspect(engine).get_table_names() == ["alembic_version"]
    command.upgrade(config, "head")
    engine.dispose()
    get_settings.cache_clear()


def test_database_constraints_match_migrations(runtime):
    _, engine, _ = runtime
    with engine.connect() as connection:
        assert compare_metadata(MigrationContext.configure(connection), Base.metadata) == []


def test_active_database_upgrade_downgrade_upgrade(runtime):
    _, engine, _ = runtime
    config = Config("alembic.ini")
    command.downgrade(config, "base")
    assert inspect(engine).get_table_names() == ["alembic_version"]
    command.upgrade(config, "head")
    with engine.connect() as connection:
        assert compare_metadata(MigrationContext.configure(connection), Base.metadata) == []
