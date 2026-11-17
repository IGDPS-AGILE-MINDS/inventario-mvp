"""Preserve movement snapshots when deleting products."""

from typing import Union

import sqlalchemy as sa
from alembic import op

revision: str = "0007"
down_revision: Union[str, None] = "0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("inventory_movement", sa.Column("product_name", sa.String(length=160), nullable=True))
    op.execute(
        "UPDATE inventory_movement SET product_name = product.name "
        "FROM product WHERE inventory_movement.product_id = product.id"
    )
    op.drop_constraint("inventory_movement_product_id_fkey", "inventory_movement", type_="foreignkey")
    op.alter_column("inventory_movement", "product_id", existing_type=sa.Integer(), nullable=True)
    op.create_foreign_key(
        "inventory_movement_product_id_fkey", "inventory_movement", "product",
        ["product_id"], ["id"], ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("inventory_movement_product_id_fkey", "inventory_movement", type_="foreignkey")
    op.create_foreign_key(
        "inventory_movement_product_id_fkey", "inventory_movement", "product",
        ["product_id"], ["id"],
    )
    op.alter_column("inventory_movement", "product_id", existing_type=sa.Integer(), nullable=False)
    op.drop_column("inventory_movement", "product_name")
