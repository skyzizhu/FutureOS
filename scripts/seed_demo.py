"""Explicit, repeatable local seed. Never runs at API import/startup."""

from uuid import UUID

from sqlalchemy.orm import Session

from infra.db import IndustryTaxonomy, User, make_engine
from infra.settings import get_settings

USER_ID = UUID("00000000-0000-4000-8000-000000000001")
ADMIN_ID = UUID("00000000-0000-4000-8000-000000000002")
OTHER_ID = UUID("00000000-0000-4000-8000-000000000003")


def seed(session: Session) -> None:
    for user_id, role in [(USER_ID, "user"), (ADMIN_ID, "admin"), (OTHER_ID, "user")]:
        if session.get(User, user_id) is None:
            session.add(User(id=user_id, auth_subject=f"DEMO:{user_id}", role=role))
    from prediction_engine.personalization.taxonomy import rows

    for row in rows():
        if session.get(IndustryTaxonomy, row["code"]) is None:
            session.add(IndustryTaxonomy(**row))
            session.flush()
    from infra.community_seed import seed_community

    seed_community(session)
    session.commit()


if __name__ == "__main__":
    with Session(make_engine(get_settings().database_url)) as session:
        seed(session)
