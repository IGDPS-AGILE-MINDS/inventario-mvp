from datetime import datetime
from typing import Literal

from pydantic import Field
from sqlmodel import SQLModel


class MovementCreate(SQLModel):
    product_id: int = Field(ge=1)
    quantity: int = Field(gt=0)
    note: str | None = Field(default=None, max_length=500)


class StockEntryCreate(MovementCreate):
    unit_cost: float = Field(ge=0)


class StockExitCreate(MovementCreate):
    reason: Literal["consumo", "perdida", "ajuste"]


class MovementRead(SQLModel):
    id: int
    product_id: int | None
    product_name: str | None = None
    movement_type: str
    quantity: int
    previous_quantity: int
    new_quantity: int
    unit_cost: float | None = None
    total_cost: float | None = None
    reason: str
    note: str | None
    created_at: datetime


class MovementList(SQLModel):
    items: list[MovementRead]
    total: int
    limit: int
    offset: int
