from datetime import datetime

from pydantic import Field, field_validator
from sqlmodel import SQLModel


class CategoryCreate(SQLModel):
    name: str = Field(min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=500)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("El nombre es obligatorio")
        return value


class CategoryUpdate(SQLModel):
    name: str = Field(default=None, min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=500)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("El nombre es obligatorio")
        return value


class CategoryRead(SQLModel):
    id: int
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime
