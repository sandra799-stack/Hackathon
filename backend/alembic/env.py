from logging.config import fileConfig
from sqlalchemy import create_engine, pool
from alembic import context

# --- Import your database setup ---
from applicationDb import Base, DATABASE_URL  # Base = declarative_base()
import models  # ensures Promotion & ActivePromotion are registered

# Alembic Config object
config = context.config

# Use DATABASE_URL from applicationDb.py
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# Configure Python logging from config file
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Alembic will use this metadata to detect tables
target_metadata = Base.metadata

# Optional: verify that tables are loaded
print("Registered tables:", list(Base.metadata.tables.keys()))


def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode."""
    # Use SQLAlchemy engine directly
    connectable = create_engine(DATABASE_URL, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
