"""Add current weighted average cost to products."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0005"
down_revision: Union[str, None] = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("product", sa.Column("weighted_average_cost", sa.Float(), nullable=True))
    op.execute("UPDATE product SET weighted_average_cost = purchase_price WHERE quantity > 0")


def downgrade() -> None:
    op.drop_column("product", "weighted_average_cost")
