from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.movement import InventoryMovement, MovementType
from app.models.product import Product
from app.schemas.movement import MovementCreate, MovementList, MovementRead, StockEntryCreate, StockExitCreate
from app.services.movement_service import register_movement

router = APIRouter(prefix="/movements", tags=["movements"])


@router.post("/in", response_model=MovementRead, status_code=201)
def register_in(data: StockEntryCreate, session: Session = Depends(get_session)):
    movement = register_movement(session, data.product_id, MovementType.IN, data.quantity, data.note, data.unit_cost)
    return _to_read(session, movement)


@router.post("/out", response_model=MovementRead, status_code=201)
def register_out(data: StockExitCreate, session: Session = Depends(get_session)):
    movement = register_movement(session, data.product_id, MovementType.OUT, data.quantity, data.note, reason=data.reason)
    return _to_read(session, movement)


def _to_read(session: Session, movement: InventoryMovement) -> MovementRead:
    product = session.get(Product, movement.product_id) if movement.product_id is not None else None
    return MovementRead(
        id=movement.id,
        product_id=movement.product_id,
        product_name=movement.product_name or (product.name if product else None),
        movement_type=movement.movement_type,
        quantity=movement.quantity,
        previous_quantity=movement.previous_quantity,
        new_quantity=movement.new_quantity,
        unit_cost=movement.unit_cost,
        total_cost=movement.total_cost,
        reason=movement.reason,
        note=movement.note,
        created_at=movement.created_at,
    )


@router.get("/", response_model=MovementList)
def list_movements(
    product_id: int | None = Query(default=None),
    movement_type: MovementType | None = Query(default=None),
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    session: Session = Depends(get_session),
):
    query = select(InventoryMovement)
    count_query = select(func.count(InventoryMovement.id))
    conditions = []
    if product_id is not None:
        conditions.append(InventoryMovement.product_id == product_id)
    if movement_type is not None:
        conditions.append(InventoryMovement.movement_type == movement_type.value)
    for condition in conditions:
        query = query.where(condition)
        count_query = count_query.where(condition)
    total = session.exec(count_query).one()
    items = session.exec(query.order_by(InventoryMovement.created_at.desc()).offset(offset).limit(limit)).all()
    return MovementList(
        items=[_to_read(session, m) for m in items], total=total, limit=limit, offset=offset
    )
