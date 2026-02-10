"""remove borrower_name from equipment_requests

Revision ID: 801c3951d010
Revises: 54520fc6b05e
Create Date: 2026-01-30 14:10:40.927286

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '801c3951d010'
down_revision: Union[str, Sequence[str], None] = '54520fc6b05e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_column("equipment_requests", "borrower_name")


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column(
        "equipment_requests",
        sa.Column("borrower_name", sa.String(length=255), nullable=False)
    )
