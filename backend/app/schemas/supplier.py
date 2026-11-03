from datetime import datetime

from pydantic import Field
from sqlmodel import SQLModel


class SupplierCreate(SQLModel):
    name: str = Field(min_length=1, max_length=120)
    contact_name: str | None = Field(default=None, max_length=120)
    email: str | None = Field(default=None, max_length=120)
    phone: str | None = Field(default=None, max_length=40)
    address: str | None = Field(default=None, max_length=255)


class SupplierUpdate(SQLModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    contact_name: str | None = Field(default=None, max_length=120)
    email: str | None = Field(default=None, max_length=120)
    phone: str | None = Field(default=None, max_length=40)
    address: str | None = Field(default=None, max_length=255)


class SupplierRead(SQLModel):
    id: int
    name: str
    contact_name: str | None
    email: str | None
    phone: str | None
    address: str | None
    created_at: datetime
    updated_at: datetime
