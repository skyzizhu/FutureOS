from alembic import context

from infra.db import Base, make_engine
from infra.settings import get_settings

if context.is_offline_mode():
    context.configure(
        url=get_settings().database_url,
        target_metadata=Base.metadata,
        literal_binds=True,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()
else:
    with make_engine(get_settings().database_url).connect() as connection:
        context.configure(connection=connection, target_metadata=Base.metadata, compare_type=True)
        with context.begin_transaction():
            context.run_migrations()
