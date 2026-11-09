"""Host-only local preview for development/E2E; never an HTTP endpoint."""

import argparse
from uuid import UUID

from prediction_engine.evidence.temporal import utc
from sqlalchemy.orm import Session

from infra.accounts import vault_for
from infra.db import AuthEmailCode, make_engine, utcnow
from infra.settings import Settings


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("challenge_id", type=UUID)
    args = parser.parse_args()
    config = Settings()
    if config.auth_mail_transport != "local_preview":
        raise SystemExit("Local preview is disabled")
    engine = make_engine(config.database_url)
    with Session(engine) as session:
        row = session.get(AuthEmailCode, args.challenge_id)
        if (
            not row
            or row.delivery_status != "local_preview"
            or not row.code_ciphertext
            or row.consumed_at
            or utc(row.expires_at) <= utcnow()
        ):
            raise SystemExit("Preview not available")
        print(
            vault_for(session, config).open(row.code_ciphertext, "auth-code:" + str(row.id))["code"]
        )
    engine.dispose()


if __name__ == "__main__":
    main()
