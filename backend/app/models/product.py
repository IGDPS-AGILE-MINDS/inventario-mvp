from datetime import date, datetime
from enum import Enum

from sqlmodel import Field, SQLModel

from app.models.base import utcnow


class ProductStatus(str, Enum):
    vigente = "vigente"
    proximo_a_vencer = "proximo_a_vencer"
    vencido = "vencido"
    agotado = "agotado"


class Product(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    sku: str = Field(unique=True, index=True, max_length=60)
    name: str = Field(index=True, max_length=160)
    description: str | None = Field(default=None, max_length=1000)
    category_id: int | None = Field(default=None, foreign_key="category.id")
    supplier_id: int | None = Field(default=None, foreign_key="supplier.id")
    quantity: int = Field(default=0, ge=0)
    unit: str = Field(default="unidad", max_length=30)
    min_stock: int = Field(default=0, ge=0)
    purchase_price: float = Field(default=0, ge=0)
    weighted_average_cost: float | None = Field(default=None, ge=0)
    sale_price: float = Field(default=0, ge=0)
    entry_date: date = Field(default_factory=date.today)
    expiration_date: date | None = None
    location: str | None = Field(default=None, max_length=120)
    status: str = Field(default=ProductStatus.vigente.value, max_length=30)
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)
