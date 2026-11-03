from datetime import date, datetime

from pydantic import Field, field_validator, model_validator
from sqlmodel import SQLModel

from app.models.product import ProductStatus


class ProductCreate(SQLModel):
    sku: str = Field(min_length=1, max_length=60)
    name: str = Field(min_length=1, max_length=160)
    description: str | None = Field(default=None, max_length=1000)
    category_id: int | None = Field(default=None, ge=1)
    supplier_id: int | None = Field(default=None, ge=1)
    quantity: int = Field(0, ge=0)
    unit: str = Field(default="unidad", min_length=1, max_length=30)
    min_stock: int = Field(0, ge=0)
    purchase_price: float | None = Field(default=None, ge=0)
    sale_price: float = Field(0, ge=0)
    entry_date: date = Field(default_factory=date.today)
    expiration_date: date | None = None
    location: str | None = Field(default=None, max_length=120)
    status: ProductStatus = ProductStatus.vigente

    @field_validator("sku", "name")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Este campo es obligatorio")
        return value

    @model_validator(mode="after")
    def require_initial_cost_for_stock(self):
        if self.quantity > 0 and self.purchase_price is None:
            raise ValueError("El costo unitario inicial es obligatorio cuando la cantidad es mayor que cero")
        return self


class ProductUpdate(SQLModel):
    sku: str = Field(default=None, min_length=1, max_length=60)
    name: str = Field(default=None, min_length=1, max_length=160)
    description: str | None = Field(default=None, max_length=1000)
    category_id: int | None = Field(default=None, ge=1)
    supplier_id: int | None = Field(default=None, ge=1)
    quantity: int = Field(default=None, ge=0)
    unit: str = Field(default=None, min_length=1, max_length=30)
    min_stock: int = Field(default=None, ge=0)
    purchase_price: float = Field(default=None, ge=0)
    sale_price: float = Field(default=None, ge=0)
    entry_date: date = None
    expiration_date: date | None = None
    location: str | None = Field(default=None, max_length=120)
    status: ProductStatus = None

    @field_validator("sku", "name")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Este campo es obligatorio")
        return value


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
    weighted_average_cost: float | None
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
