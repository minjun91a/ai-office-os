import os
import sys
from logging.config import fileConfig

from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool

from alembic import context

sys.path.insert(0, os.getcwd())
load_dotenv()

from app.core.database import Base # noqa: E402
from app.models.user import User # noqa: E402,F401
from app.models.document import Document # noqa: E402,F401
from app.models.document_analysis import DocumentAnalysis # noqa: E402,F401
from app.models.report import Report # noqa: E402,F401
from app.models.google_credential import GoogleCredential # noqa: E402,F401
from app.models.organization import Organization # noqa: E402,F401
from app.models.api_log import ApiLog # noqa: E402,F401


config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

config.set_main_option(
    "sqlalchemy.url",
    os.getenv("DATABASE_URL", "postgresql://aioffice:aioffice_dev_pw@localhost:5432/aioffice"),
)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
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