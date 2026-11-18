from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session
from app.models.base import utcnow

from app.db.session import get_session
from app.models.movement import InventoryMovement
from app.models.product import Product

router = APIRouter(prefix="/admin", tags=["admin"])


@router.delete(
    "/products/{product_id}", status_code=204,
    description="Desactiva el producto y conserva su ficha y movimientos asociados.",
)
def admin_delete_product(product_id: int, session: Session = Depends(get_session)):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(404, "Producto no encontrado")
    product.is_active = False
    product.updated_at = utcnow()
    session.add(product)
    session.commit()
    return Response(status_code=204)


@router.delete(
    "/movements/{movement_id}", status_code=204,
    description="Elimina permanentemente el movimiento indicado.",
)
def admin_delete_movement(movement_id: int, session: Session = Depends(get_session)):
    movement = session.get(InventoryMovement, movement_id)
    if not movement:
        raise HTTPException(404, "Movimiento no encontrado")
    session.delete(movement)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(409, "No se pudo eliminar el movimiento")
    return Response(status_code=204)
