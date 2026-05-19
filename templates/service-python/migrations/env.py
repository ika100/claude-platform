{%- if not needs_migrations -%}
# Alembic scaffolding was disabled at template time. Re-run `copier update`
# with --data needs_migrations=true to enable.
{%- else -%}
"""Alembic env for {{ project_name }}.

Reads the database URL from DATABASE_URL — never hardcode it here.
Wire your declarative Base into ``target_metadata`` so autogenerate
can introspect the models.
"""

from __future__ import annotations

import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

database_url = os.environ.get("DATABASE_URL")
if not database_url:
    raise RuntimeError("DATABASE_URL environment variable is required for migrations.")
config.set_main_option("sqlalchemy.url", database_url)

# TODO: import your declarative Base and assign its metadata here so
# autogenerate sees the models. Example:
#     from {{ module_name }}.models import Base
#     target_metadata = Base.metadata
target_metadata = None


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode — emits SQL without a live DB."""
    context.configure(
        url=database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode — opens a connection to the DB."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
{%- endif %}
