from logging.config import fileConfig
from sqlalchemy import create_engine, pool
from alembic import context

# --- Import your database setup ---
from app_db import Base, APP_DB_URL  # Base = declarative_base()
from models import Base  # Base should include Promotion
# Alembic Config object
config = context.config

# Use APP_DB_URL from applicationDb.py
config.set_main_option("sqlalchemy.url", APP_DB_URL)

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
        url=APP_DB_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode."""
    # Use SQLAlchemy engine directly
    connectable = create_engine(APP_DB_URL, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
