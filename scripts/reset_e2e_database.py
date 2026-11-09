"""Reset only the explicitly named PostgreSQL test database before browser acceptance."""

from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from infra.db import Base, make_engine
from infra.settings import Settings
from scripts.seed_demo import seed


def main() -> None:
    config = Settings()
    url = make_url(config.database_url)
    if (
        config.app_env != "test"
        or not (url.database or "").endswith("_test")
        or url.get_backend_name() != "postgresql"
    ):
        raise SystemExit("Refusing to reset a non-PostgreSQL, non-test or non-_test database")
    engine = make_engine(config.database_url)
    with Session(engine) as session:
        names = ", ".join('"' + table.name + '"' for table in Base.metadata.sorted_tables)
        session.execute(text("TRUNCATE TABLE " + names + " CASCADE"))
        session.commit()
        seed(session)
    engine.dispose()
    print("PASS: isolated browser test database reset and seeded")


if __name__ == "__main__":
    main()
