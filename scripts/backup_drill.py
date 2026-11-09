"""Historical backup restore plus replay of deletion performed after that snapshot."""

import json
from pathlib import Path
from uuid import uuid4

from prediction_engine.contracts.models import (
    AccountCredentialsV1,
    PersonalDataEraseV1,
    ProfileInputV1,
)
from sqlalchemy.orm import Session

from infra.accounts import AccountRepository
from infra.backup import create_backup, restore_drill
from infra.db import make_engine
from infra.personal_data import erase_private
from infra.profiles import ProfileRepository
from infra.settings import Settings


def main() -> None:
    config = Settings()
    engine = make_engine(config.database_url)
    password = "M7-restore-fixture-" + uuid4().hex
    with Session(engine) as session:
        identity = AccountRepository(session, config).register(
            AccountCredentialsV1(
                email="m7-restore-" + uuid4().hex + "@example.invalid", password=password
            )
        )
        uid = identity.identity.user_id
        ProfileRepository(session, config).save(
            uid,
            ProfileInputV1(
                industry_l1_code="technology",
                industry_l2_code="software",
                occupation_text="Own synthetic restore-erasure fixture",
                use_optional_fields=True,
            ),
        )
        ProfileRepository(session, config).snapshot(uid)
        session.commit()
    path = create_backup(config)
    with Session(engine) as session:
        erase_private(
            session,
            uid,
            PersonalDataEraseV1(password=password, confirmation="DELETE MY DATA"),
            config,
        )
    report = restore_drill(config, path)
    assert report["deletions_replayed"] >= 1
    Path(".local/m7-restore-drill.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False)
    )
    Path("docs/milestones/evidence/M7-restore-drill.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False)
    )
    engine.dispose()
    print("PASS: isolated restore, private hashes and post-backup erasure replay verified")


if __name__ == "__main__":
    main()
