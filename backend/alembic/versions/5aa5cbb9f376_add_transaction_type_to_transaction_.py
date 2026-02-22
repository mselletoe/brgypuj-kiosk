"""add transaction_type to transaction_history

Revision ID: 5aa5cbb9f376
Revises: 6466b8d7ccd0
Create Date: 2026-02-22 16:29:30.871383

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5aa5cbb9f376'
down_revision: Union[str, Sequence[str], None] = '6466b8d7ccd0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('transaction_history', sa.Column(
        'transaction_type',
        sa.String(length=20),
        nullable=False,
        server_default='document'    # ← this was missing
    ))
    op.create_check_constraint(
        'ck_transaction_history_transaction_type',
        'transaction_history',
        "transaction_type IN ('document', 'equipment', 'rfid')"
    )
    op.alter_column('transaction_history', 'transaction_name',
               existing_type=sa.VARCHAR(length=50),
               type_=sa.String(length=100),
               existing_nullable=False)


def downgrade() -> None:
    op.alter_column('transaction_history', 'transaction_name',
               existing_type=sa.String(length=100),
               type_=sa.VARCHAR(length=50),
               existing_nullable=False)
    op.drop_constraint('ck_transaction_history_transaction_type', 'transaction_history')
    op.drop_column('transaction_history', 'transaction_type')
