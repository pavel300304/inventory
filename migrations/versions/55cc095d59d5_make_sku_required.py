"""make sku required

Revision ID: 55cc095d59d5
Revises: 60d49f79db5e
Create Date: 2026-10-07 20:31:56.718957

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '55cc095d59d5'
down_revision: Union[str, Sequence[str], None] = '60d49f79db5e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TABLE items ALTER COLUMN sku SET NOT NULL")


def downgrade() -> None:
    op.execute("ALTER TABLE items ALTER COLUMN sku DROP NOT NULL")