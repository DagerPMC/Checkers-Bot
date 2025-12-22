import sys
import asyncio
import logging

from sqlalchemy.sql.schema import SchemaItem

sys.path = ['', '..'] + sys.path[1:]

from logging.config import fileConfig

from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine

from bot.db.base import Base
import bot.db.models  # noqa - import models to register them

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

log = logging.getLogger('alembic')

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata


def do_run_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = create_async_engine(
        config.get_main_option("sqlalchemy.url"),
        future=True
    )
    log.info(f'Current DB: {connectable.url}')
    async with connectable.connect() as connection:
        try:
            await connection.run_sync(do_run_migrations)
        except Exception:
            log.exception(f'Error occurred; DB: {connectable.url}\n')

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
