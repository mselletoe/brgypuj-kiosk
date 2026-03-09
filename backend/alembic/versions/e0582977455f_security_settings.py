"""security_settings

Revision ID: e0582977455f
Revises: 1844eacf67f4
Create Date: 2026-03-10 00:09:33.286095

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e0582977455f'
down_revision: Union[str, Sequence[str], None] = '1844eacf67f4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Step 1: add as nullable so existing rows don't violate NOT NULL
    op.add_column('system_config', sa.Column('auto_logout_duration', sa.Integer(), nullable=True))
    # Step 2: backfill — convert old minutes to seconds
    op.execute('UPDATE system_config SET auto_logout_duration = auto_logout_minutes * 60')
    # Step 3: now safe to enforce NOT NULL
    op.alter_column('system_config', 'auto_logout_duration', nullable=False)
    # Step 4: drop the old column
    op.drop_column('system_config', 'auto_logout_minutes')

    # resident lockout columns
    op.add_column('residents', sa.Column('failed_pin_attempts', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('residents', sa.Column('locked_until', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.add_column('system_config', sa.Column('auto_logout_minutes', sa.INTEGER(), autoincrement=False, nullable=True))
    op.execute('UPDATE system_config SET auto_logout_minutes = auto_logout_duration / 60')
    op.alter_column('system_config', 'auto_logout_minutes', nullable=False)
    op.drop_column('system_config', 'auto_logout_duration')

    op.drop_column('residents', 'locked_until')
    op.drop_column('residents', 'failed_pin_attempts')