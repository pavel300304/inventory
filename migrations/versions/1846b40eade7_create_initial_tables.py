"""create initial tables

Revision ID: 1846b40eade7
Revises: 
Create Date: 2026-10-07 18:58:05.580812

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1846b40eade7'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE tenants (
          id   SERIAL PRIMARY KEY,
          name TEXT NOT NULL UNIQUE
        )
    """)
    op.execute("""
        CREATE TABLE users (
          id        SERIAL PRIMARY KEY,
          tenant_id INT NOT NULL REFERENCES tenants(id),
          email     TEXT NOT NULL UNIQUE
        )
    """)
    op.execute("""
        CREATE TABLE items (
          id        SERIAL PRIMARY KEY,
          tenant_id INT NOT NULL REFERENCES tenants(id),
          name      TEXT NOT NULL,
          stock     INT NOT NULL CHECK (stock >= 0)
        )
    """)
    op.execute("""
        CREATE TABLE orders (
          id         SERIAL PRIMARY KEY,
          tenant_id  INT NOT NULL REFERENCES tenants(id),
          user_id    INT NOT NULL REFERENCES users(id),
          created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """)
    op.execute("""
        CREATE TABLE order_items (
          order_id INT NOT NULL REFERENCES orders(id),
          item_id  INT NOT NULL REFERENCES items(id),
          quantity INT NOT NULL CHECK (quantity > 0),
          PRIMARY KEY (order_id, item_id)
        )
    """)


def downgrade() -> None:
    op.execute("DROP TABLE order_items, orders, items, users, tenants")
