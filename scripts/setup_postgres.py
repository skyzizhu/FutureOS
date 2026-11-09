"""Install/configure an isolated native PostgreSQL cluster under .local (no Docker)."""

import os
import secrets
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url


def main() -> None:
    import pgserver

    folder = Path(".local").resolve()
    folder.mkdir(exist_ok=True)
    output = Path(".env")
    if output.exists():
        raise SystemExit(".env exists; configure it manually or preserve it before setup")
    server = pgserver.get_server(folder / "postgres-demo", cleanup_mode="stop")
    admin_url = make_url(server.get_uri()).set(drivername="postgresql+psycopg")
    engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")
    password = secrets.token_urlsafe(32)
    try:
        with engine.connect() as connection:
            print("Native PostgreSQL:", connection.scalar(text("SELECT version()")))
            if connection.scalar(text("SELECT 1 FROM pg_roles WHERE rolname='futureos_local'")):
                raise SystemExit("futureos_local role exists; preserving its credentials")
            # DDL uses psycopg's identifier/literal composition, never SQL interpolation.
            import psycopg.sql

            raw = connection.connection.driver_connection
            raw.execute(
                psycopg.sql.SQL("CREATE ROLE futureos_local LOGIN PASSWORD {}").format(
                    psycopg.sql.Literal(password)
                )
            )
            for name in ("futureos_m0_demo", "futureos_m0_test"):
                if not connection.scalar(
                    text("SELECT 1 FROM pg_database WHERE datname=:name"), {"name": name}
                ):
                    raw.execute(
                        psycopg.sql.SQL("CREATE DATABASE {} OWNER futureos_local").format(
                            psycopg.sql.Identifier(name)
                        )
                    )

        def url(database: str) -> str:
            return admin_url.set(
                username="futureos_local", password=password, database=database
            ).render_as_string(hide_password=False)

        body = "\n".join(
            [
                "DEMO_MODE=true",
                "APP_ENV=development",
                f"DATABASE_URL={url('futureos_m0_demo')}",
                f"TEST_DATABASE_URL={url('futureos_m0_test')}",
                "FUTUREOS_MANAGED_POSTGRES=true",
                "REDIS_URL=redis://127.0.0.1:6381/0",
                "REQUIRE_REDIS=true",
                "FUTUREOS_API_PORT=8100",
                "FUTUREOS_WEB_PORT=3100",
                "API_INTERNAL_URL=http://127.0.0.1:8100",
                "NEXT_TELEMETRY_DISABLED=1",
                "",
            ]
        )
        fd = os.open(output, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        with os.fdopen(fd, "w") as stream:
            stream.write(body)
        print("Created isolated PostgreSQL demo/test databases; .env written (0600).")
    finally:
        engine.dispose()
        server.cleanup()


if __name__ == "__main__":
    main()
