from datetime import datetime

from pydantic import Field
from sqlmodel import SQLModel


class CategoryCreate(SQLModel):
    name: str = Field(min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=500)


class CategoryUpdate(SQLModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=500)


class CategoryRead(SQLModel):
    id: int
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime
