from datetime import datetime
from enum import Enum

from sqlmodel import Field, SQLModel

from app.models.base import utcnow


class MovementType(str, Enum):
    IN = "IN"
    OUT = "OUT"


class InventoryMovement(SQLModel, table=True):
    __tablename__ = "inventory_movement"

    id: int | None = Field(default=None, primary_key=True)
    product_id: int | None = Field(default=None, foreign_key="product.id", index=True)
    product_name: str | None = Field(default=None, max_length=160)
    movement_type: str = Field(max_length=3)
    quantity: int = Field(gt=0)
    previous_quantity: int
    new_quantity: int
    unit_cost: float | None = Field(default=None, ge=0)
    total_cost: float | None = Field(default=None, ge=0)
    reason: str = Field(default="manual", max_length=20)
    note: str | None = Field(default=None, max_length=500)
    created_at: datetime = Field(default_factory=utcnow)
