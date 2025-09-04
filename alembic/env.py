from logging.config import fileConfig

from sqlalchemy import pool

from alembic import context
from src.database import SQL_ALCHEMY_DB_URL

config = context.config

if config.config_file_name is not None:
  fileConfig(config.config_file_name)

from src.database import Base

from src.chemical.models import Chemical, InventoryLog

target_metadata = Base.metadata

config.set_main_option("sqlalchemy.url", SQL_ALCHEMY_DB_URL)


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


def run_migrations_online() -> None:
  """Run migrations in 'online' mode.

  In this scenario we need to create an Engine
  and associate a connection with the context.

  """
  import asyncio

  from sqlalchemy.ext.asyncio import async_engine_from_config

  connectable = async_engine_from_config(
    config.get_section(config.config_ini_section, {}),
    prefix="sqlalchemy.",
    poolclass=pool.NullPool,
  )

  def do_run_migrations(connection):
    # This function runs in a sync context but receives
    # a sync Connection bridged from the async connection.
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
      context.run_migrations()

  async def run_async_migrations():
    async with connectable.connect() as async_connection:
      await async_connection.run_sync(do_run_migrations)
    await connectable.dispose()

  asyncio.run(run_async_migrations())


if context.is_offline_mode():
  run_migrations_offline()
else:
  run_migrations_online()
