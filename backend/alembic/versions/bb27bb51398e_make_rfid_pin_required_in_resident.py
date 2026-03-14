"""make rfid_pin required in resident

Revision ID: bb27bb51398e
Revises: 1b8954971830
Create Date: 2026-02-23 15:36:40.965653
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'bb27bb51398e'
down_revision = '1b8954971830'
branch_labels = None
depends_on = None

def upgrade() -> None:
    """Upgrade schema."""

    # Step 1: Set all NULL rfid_pin values to '0000'
    op.execute("UPDATE residents SET rfid_pin = '0000' WHERE rfid_pin IS NULL")

    # Step 2: Alter column to NOT NULL
    op.alter_column(
        'residents',
        'rfid_pin',
        existing_type=sa.VARCHAR(length=255),
        nullable=False
    )

def downgrade() -> None:
    """Downgrade schema."""

    # Revert column to nullable
    op.alter_column(
        'residents',
        'rfid_pin',
        existing_type=sa.VARCHAR(length=255),
        nullable=True
    )