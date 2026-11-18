from datetime import date, timedelta

from sqlalchemy import func
from sqlmodel import Session, SQLModel, select

from app.models.movement import InventoryMovement
from app.models.product import Product
from app.services.expiration import get_warning_days


class MovementSummary(SQLModel):
    id: int
    product_id: int | None
    product_name: str | None
    movement_type: str
    quantity: int
    created_at: str


class DashboardSummary(SQLModel):
    total_products: int
    total_units: int
    low_stock: int
    out_of_stock: int
    expiring_soon: int
    expired: int
    last_movements: list[MovementSummary]


def get_dashboard_summary(session: Session) -> DashboardSummary:
    total_products = session.exec(select(func.count(Product.id))).one()
    total_units = session.exec(select(func.coalesce(func.sum(Product.quantity), 0))).one()
    low_stock = session.exec(
        select(func.count(Product.id)).where(
            Product.is_active.is_(True),
            Product.quantity > 0,
            Product.quantity <= Product.min_stock,
        )
    ).one()
    out_of_stock = session.exec(
        select(func.count(Product.id)).where(Product.is_active.is_(True), Product.quantity == 0)
    ).one()

    today = date.today()
    warning = today + timedelta(days=get_warning_days(session))
    expiring_soon = session.exec(
        select(func.count(Product.id)).where(
            Product.expiration_date.is_not(None),
            Product.expiration_date >= today,
            Product.expiration_date <= warning,
        )
    ).one()
    expired = session.exec(
        select(func.count(Product.id)).where(Product.expiration_date < today)
    ).one()

    rows = session.exec(
        select(InventoryMovement).order_by(InventoryMovement.created_at.desc()).limit(5)
    ).all()
    last = []
    for m in rows:
        product = session.get(Product, m.product_id) if m.product_id is not None else None
        last.append(MovementSummary(
            id=m.id, product_id=m.product_id,
            product_name=m.product_name or (product.name if product else None),
            movement_type=m.movement_type, quantity=m.quantity,
            created_at=m.created_at.isoformat(),
        ))
    return DashboardSummary(
        total_products=total_products, total_units=total_units, low_stock=low_stock,
        out_of_stock=out_of_stock,
        expiring_soon=expiring_soon, expired=expired, last_movements=last,
    )
