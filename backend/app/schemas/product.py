from datetime import date, datetime

from pydantic import Field
from sqlmodel import SQLModel

from app.models.product import ProductStatus


class ProductCreate(SQLModel):
    sku: str = Field(min_length=1, max_length=60)
    name: str = Field(min_length=1, max_length=160)
    description: str | None = Field(default=None, max_length=1000)
    category_id: int | None = None
    supplier_id: int | None = None
    quantity: int = Field(0, ge=0)
    unit: str = Field(default="unidad", min_length=1, max_length=30)
    min_stock: int = Field(0, ge=0)
    purchase_price: float = Field(0, ge=0)
    sale_price: float = Field(0, ge=0)
    entry_date: date = Field(default_factory=date.today)
    expiration_date: date | None = None
    location: str | None = Field(default=None, max_length=120)
    status: ProductStatus = ProductStatus.vigente


class ProductUpdate(SQLModel):
    sku: str | None = Field(default=None, min_length=1, max_length=60)
    name: str | None = Field(default=None, min_length=1, max_length=160)
    description: str | None = Field(default=None, max_length=1000)
    category_id: int | None = None
    supplier_id: int | None = None
    quantity: int | None = Field(default=None, ge=0)
    unit: str | None = Field(default=None, min_length=1, max_length=30)
    min_stock: int | None = Field(default=None, ge=0)
    purchase_price: float | None = Field(default=None, ge=0)
    sale_price: float | None = Field(default=None, ge=0)
    entry_date: date | None = None
    expiration_date: date | None = None
    location: str | None = Field(default=None, max_length=120)
    status: ProductStatus | None = None


class ProductRead(SQLModel):
    id: int
    sku: str
    name: str
    description: str | None
    category_id: int | None
    supplier_id: int | None
    quantity: int
    unit: str
    min_stock: int
    purchase_price: float
    sale_price: float
    entry_date: date
    expiration_date: date | None
    location: str | None
    status: ProductStatus
    created_at: datetime
    updated_at: datetime
    expiration_status: str = "sin_fecha"


class ProductList(SQLModel):
    items: list[ProductRead]
    total: int
    limit: int
    offset: int
