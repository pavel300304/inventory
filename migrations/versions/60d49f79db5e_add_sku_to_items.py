"""add sku to items

Revision ID: 60d49f79db5e
Revises: 1846b40eade7
Create Date: 2026-10-07 19:12:07.999534

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '60d49f79db5e'
down_revision: Union[str, Sequence[str], None] = '1846b40eade7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TABLE items ADD COLUMN sku TEXT")


def downgrade() -> None:
    op.execute("ALTER TABLE items DROP COLUMN sku")
