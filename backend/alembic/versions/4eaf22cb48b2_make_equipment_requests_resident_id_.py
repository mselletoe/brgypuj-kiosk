"""Make equipment_requests.resident_id required

Revision ID: 4eaf22cb48b2
Revises: 801c3951d010
Create Date: 2026-02-06 21:20:30.770873
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "4eaf22cb48b2"
down_revision: Union[str, Sequence[str], None] = "801c3951d010"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    orphan_count = conn.execute(
        sa.text(
            "SELECT COUNT(*) FROM equipment_requests WHERE resident_id IS NULL"
        )
    ).scalar()

    if orphan_count > 0:
        raise RuntimeError(
            "Migration aborted: equipment_requests contains rows with NULL resident_id"
        )

    op.drop_constraint(
        "equipment_requests_resident_id_fkey",
        "equipment_requests",
        type_="foreignkey",
    )

    op.alter_column(
        "equipment_requests",
        "resident_id",
        existing_type=sa.Integer(),
        nullable=False,
    )

    op.create_foreign_key(
        "equipment_requests_resident_id_fkey",
        "equipment_requests",
        "residents",
        ["resident_id"],
        ["id"],
        ondelete="RESTRICT",
    )


def downgrade() -> None:

    op.drop_constraint(
        "equipment_requests_resident_id_fkey",
        "equipment_requests",
        type_="foreignkey",
    )

    op.alter_column(
        "equipment_requests",
        "resident_id",
        existing_type=sa.Integer(),
        nullable=True,
    )

    op.create_foreign_key(
        "equipment_requests_resident_id_fkey",
        "equipment_requests",
        "residents",
        ["resident_id"],
        ["id"],
        ondelete="SET NULL",
    )