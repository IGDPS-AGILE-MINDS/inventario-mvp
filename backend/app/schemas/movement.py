from datetime import datetime

from pydantic import Field
from sqlmodel import SQLModel


class MovementCreate(SQLModel):
    product_id: int = Field(ge=1)
    quantity: int = Field(gt=0)
    note: str | None = Field(default=None, max_length=500)


class MovementRead(SQLModel):
    id: int
    product_id: int
    product_name: str | None = None
    movement_type: str
    quantity: int
    previous_quantity: int
    new_quantity: int
    note: str | None
    created_at: datetime


class MovementList(SQLModel):
    items: list[MovementRead]
    total: int
    limit: int
    offset: int
