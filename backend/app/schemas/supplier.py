from datetime import datetime

from pydantic import Field, field_validator
from sqlmodel import SQLModel


class SupplierCreate(SQLModel):
    name: str = Field(min_length=1, max_length=120)
    contact_name: str | None = Field(default=None, max_length=120)
    email: str | None = Field(default=None, max_length=120, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    phone: str | None = Field(default=None, max_length=40)
    address: str | None = Field(default=None, max_length=255)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("El nombre es obligatorio")
        return value


class SupplierUpdate(SQLModel):
    name: str = Field(default=None, min_length=1, max_length=120)
    contact_name: str | None = Field(default=None, max_length=120)
    email: str | None = Field(default=None, max_length=120, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    phone: str | None = Field(default=None, max_length=40)
    address: str | None = Field(default=None, max_length=255)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("El nombre es obligatorio")
        return value


class SupplierRead(SQLModel):
    id: int
    name: str
    contact_name: str | None
    email: str | None
    phone: str | None
    address: str | None
    created_at: datetime
    updated_at: datetime
