import os

# must run before app.db is imported: tests use their own database,
# never the dev one the server uses
ADMIN_URL = "postgresql://postgres:dev@localhost:5432/postgres"
TEST_DB = "postgres_test"
os.environ["DATABASE_URL"] = f"postgresql://postgres:dev@localhost:5432/{TEST_DB}"

import psycopg  # noqa: E402
import pytest  # noqa: E402
from alembic import command  # noqa: E402
from alembic.config import Config  # noqa: E402

from app.db import get_conn  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def test_database():
    with psycopg.connect(ADMIN_URL, autocommit=True) as conn:
        exists = conn.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s", (TEST_DB,)
        ).fetchone()
        if not exists:
            conn.execute(f"CREATE DATABASE {TEST_DB}")

    config = Config("alembic.ini")
    config.set_main_option(
        "sqlalchemy.url",
        os.environ["DATABASE_URL"].replace(
            "postgresql://", "postgresql+psycopg://"),
    )
    command.upgrade(config, "head")

    with get_conn() as conn:
        conn.execute(
            "INSERT INTO tenants (id, name) VALUES (1, 'Acme Hardware'), (2, 'Best Tools') "
            "ON CONFLICT DO NOTHING"
        )
        conn.execute(
            "INSERT INTO users (id, tenant_id, email) VALUES "
            "(1, 1, 'dana@acme.test'), (2, 2, 'noa@best.test') ON CONFLICT DO NOTHING"
        )


@pytest.fixture(autouse=True)
def clean_db():
    with get_conn() as conn:
        conn.execute("TRUNCATE order_items, orders, items RESTART IDENTITY")
