import os

import psycopg
from psycopg.rows import dict_row

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://postgres:dev@localhost:5432/postgres"
)


def get_conn():
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)
