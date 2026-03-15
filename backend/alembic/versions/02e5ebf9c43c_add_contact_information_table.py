"""add contact_information table

Revision ID: 02e5ebf9c43c
Revises: 94ee6ab58b98
Create Date: 2026-03-09 14:19:28.609846

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '02e5ebf9c43c'
down_revision: Union[str, Sequence[str], None] = '94ee6ab58b98'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass  # contact_information already created in 94ee6ab58b98


def downgrade() -> None:
    pass