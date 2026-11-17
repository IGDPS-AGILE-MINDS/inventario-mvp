"""Store movement costs and reason."""

from typing import Union

import sqlalchemy as sa
from alembic import op

revision: str = "0006"
down_revision: Union[str, None] = "0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("inventory_movement", sa.Column("unit_cost", sa.Float(), nullable=True))
    op.add_column("inventory_movement", sa.Column("total_cost", sa.Float(), nullable=True))
    op.add_column("inventory_movement", sa.Column("reason", sa.String(length=20), nullable=False, server_default="manual"))


def downgrade() -> None:
    op.drop_column("inventory_movement", "reason")
    op.drop_column("inventory_movement", "total_cost")
    op.drop_column("inventory_movement", "unit_cost")
