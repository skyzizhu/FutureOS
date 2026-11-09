import os
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import delete, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from apps.api.main import create_app
from infra.db import Base, make_engine
from infra.settings import Settings, get_settings
from scripts.seed_demo import seed


@pytest.fixture
def runtime(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    url = os.getenv("TEST_DATABASE_URL", f"sqlite:///{tmp_path / 'test.db'}")
    if not url.startswith("sqlite"):
        assert (make_url(url).database or "").endswith("_test"), (
            "Refusing to clear non-test database"
        )
    monkeypatch.setenv("DATABASE_URL", url)
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("REQUIRE_REDIS", "false")
    get_settings.cache_clear()
    command.upgrade(Config("alembic.ini"), "head")
    engine = make_engine(url)
    with Session(engine) as session:
        if engine.dialect.name == "postgresql":
            names = ", ".join(f'"{table.name}"' for table in Base.metadata.sorted_tables)
            session.execute(text(f"TRUNCATE TABLE {names} CASCADE"))
        else:
            for table in reversed(Base.metadata.sorted_tables):
                if table.name != "industry_taxonomy":
                    session.execute(delete(table))
        session.commit()
        seed(session)
    config = Settings(
        _env_file=None,
        database_url=url,
        app_env="test",
        require_redis=False,
        sandbox_commerce_enabled=False,
        demo_admin_enabled=True,
        auth_mail_transport="local_preview",
        live_web_enabled=False,
        live_research_enabled=False,
        deepseek_api_key=None,
        profile_key_path=str(tmp_path / "private-profile.key"),
    )
    app = create_app(config)
    with TestClient(app, raise_server_exceptions=False) as client:
        yield client, engine, config
    app.state.engine.dispose()
    engine.dispose()
    get_settings.cache_clear()


USER_HEADERS = {"Authorization": "Bearer demo-user-local-only"}
ADMIN_HEADERS = {"Authorization": "Bearer demo-admin-local-only"}
OTHER_HEADERS = {"Authorization": "Bearer demo-other-local-only"}
