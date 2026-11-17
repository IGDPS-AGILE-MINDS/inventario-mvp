from fastapi import HTTPException
from sqlalchemy import select as sa_select
from sqlmodel import Session

from app.models.movement import InventoryMovement, MovementType
from app.models.product import Product, ProductStatus
from typing import Literal


def register_movement(
    session: Session, product_id: int, movement_type: MovementType, quantity: int,
    note: str | None, unit_cost: float | None = None,
    reason: Literal["consumo", "perdida", "ajuste"] = "consumo",
) -> InventoryMovement:
    try:
        product = session.execute(
            sa_select(Product).where(Product.id == product_id).with_for_update()
        ).scalar_one_or_none()
        if not product:
            raise HTTPException(404, "Producto no encontrado")

        previous = product.quantity
        if movement_type == MovementType.OUT and quantity > previous:
            raise HTTPException(400, f"Stock insuficiente: disponible {previous}, solicitado {quantity}")

        if movement_type == MovementType.IN:
            if unit_cost is None:
                raise HTTPException(400, "El costo unitario de adquisición es obligatorio para registrar una entrada")
            if previous > 0 and product.weighted_average_cost is None:
                raise HTTPException(400, "No se puede calcular el costo promedio: el producto tiene existencias sin CPPM")
            old_cost = product.weighted_average_cost or 0
            unit_cost = round(unit_cost, 2)
            average_cost = unit_cost if previous == 0 else round((previous * old_cost + quantity * unit_cost) / (previous + quantity), 2)
            product.weighted_average_cost = average_cost
        elif product.weighted_average_cost is None:
            raise HTTPException(400, "No se puede registrar la salida: el producto no tiene costo promedio ponderado")
        else:
            unit_cost = product.weighted_average_cost

        new_quantity = previous + quantity if movement_type == MovementType.IN else previous - quantity
        product.quantity = new_quantity
        if new_quantity == 0:
            product.status = ProductStatus.agotado.value
        elif movement_type == MovementType.IN and product.status == ProductStatus.agotado.value:
            product.status = ProductStatus.vigente.value

        movement = InventoryMovement(
            product_id=product_id, product_name=product.name, movement_type=movement_type.value, quantity=quantity,
            previous_quantity=previous, new_quantity=new_quantity, unit_cost=unit_cost,
            total_cost=round(quantity * unit_cost, 2), reason="entrada_compra" if movement_type == MovementType.IN else reason,
            note=note,
        )
        session.add(movement)
        session.add(product)
        session.commit()
        session.refresh(movement)
        return movement
    except Exception:
        session.rollback()
        raise
