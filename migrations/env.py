from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# Alembic Config object
config = context.config

# Set up loggers
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ── Import ALL models so Alembic can detect them ──────────────────────────────
from app.models.base import Base          # noqa: E402

import app.models.user                   # noqa: F401
import app.models.farm                   # noqa: F401
import app.models.field                  # noqa: F401
import app.models.field_boundary         # noqa: F401
import app.models.crop_cycle             # noqa: F401
import app.models.sensor_reading         # noqa: F401
import app.models.weather                # noqa: F401
import app.models.satellite_observation  # noqa: F401
import app.models.diagnosis              # noqa: F401
import app.models.irrigation_plan        # noqa: F401
import app.models.yield_prediction       # noqa: F401
import app.models.crop_mix_recommendation# noqa: F401
import app.models.crop_mix_allocation   # noqa: F401

# ── Pull DATABASE_URL from .env via our settings ──────────────────────────────
from app.core.config import settings
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

target_metadata = Base.metadata
# ─────────────────────────────────────────────────────────────────────────────


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (no live DB connection needed)."""
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
    """Run migrations in 'online' mode (live DB connection)."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
