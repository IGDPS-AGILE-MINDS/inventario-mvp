from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.base import utcnow
from app.models.product import Product, ProductStatus
from app.models.category import Category
from app.models.supplier import Supplier
from app.schemas.product import ProductCreate, ProductList, ProductRead, ProductUpdate
from app.services.expiration import expiration_status, get_warning_days

router = APIRouter(prefix="/products", tags=["products"])


def _with_expiration(session: Session, product: Product) -> ProductRead:
    read = ProductRead.model_validate(product, from_attributes=True)
    read.expiration_status = expiration_status(product.expiration_date, get_warning_days(session))
    return read


@router.get("/", response_model=ProductList)
def list_products(
    search: str | None = Query(default=None),
    category_id: int | None = Query(default=None),
    status: ProductStatus | None = Query(default=None),
    expiration: str | None = Query(default=None),
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    session: Session = Depends(get_session),
):
    query = select(Product)
    count_query = select(func.count(Product.id))

    conditions = []
    if search:
        like = f"%{search}%"
        conditions.append(or_(Product.name.ilike(like), Product.sku.ilike(like)))
    if category_id is not None:
        conditions.append(Product.category_id == category_id)
    if status is not None:
        conditions.append(Product.status == status)
    if expiration is not None:
        today = date.today()
        warning_days = get_warning_days(session)
        limit_date = today + timedelta(days=warning_days)
        if expiration == "vencido":
            conditions.append(Product.expiration_date < today)
        elif expiration == "proximo_a_vencer":
            conditions.append(Product.expiration_date >= today)
            conditions.append(Product.expiration_date <= limit_date)
        elif expiration == "vigente":
            conditions.append(Product.expiration_date > limit_date)
        elif expiration == "sin_fecha":
            conditions.append(Product.expiration_date.is_(None))

    for condition in conditions:
        query = query.where(condition)
        count_query = count_query.where(condition)

    total = session.exec(count_query).one()
    items = session.exec(query.order_by(Product.name).offset(offset).limit(limit)).all()
    return ProductList(items=[_with_expiration(session, p) for p in items], total=total, limit=limit, offset=offset)


@router.post("/", response_model=ProductRead, status_code=201)
def create_product(data: ProductCreate, session: Session = Depends(get_session)):
    if data.category_id is not None and not session.get(Category, data.category_id):
        raise HTTPException(400, "La categoría seleccionada no existe")
    if data.supplier_id is not None and not session.get(Supplier, data.supplier_id):
        raise HTTPException(400, "El proveedor seleccionado no existe")
    product = Product.model_validate(data, update={
        "purchase_price": data.purchase_price or 0,
        "weighted_average_cost": data.purchase_price if data.quantity > 0 else None,
    })
    if product.entry_date is None:
        from datetime import date

        product.entry_date = date.today()
    session.add(product)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(400, "El SKU ya existe")
    session.refresh(product)
    return _with_expiration(session, product)


@router.get("/{product_id}", response_model=ProductRead)
def get_product(product_id: int, session: Session = Depends(get_session)):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(404, "Producto no encontrado")
    return _with_expiration(session, product)


@router.put("/{product_id}", response_model=ProductRead)
def update_product(product_id: int, data: ProductUpdate, session: Session = Depends(get_session)):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(404, "Producto no encontrado")
    changes = data.model_dump(exclude_unset=True)
    if changes.get("category_id") is not None and not session.get(Category, changes["category_id"]):
        raise HTTPException(400, "La categoría seleccionada no existe")
    if changes.get("supplier_id") is not None and not session.get(Supplier, changes["supplier_id"]):
        raise HTTPException(400, "El proveedor seleccionado no existe")
    for key, value in changes.items():
        setattr(product, key, value)
    product.updated_at = utcnow()
    session.add(product)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(400, "El SKU ya existe")
    session.refresh(product)
    return _with_expiration(session, product)


@router.delete("/{product_id}", status_code=204)
def delete_product(product_id: int, session: Session = Depends(get_session)):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(404, "Producto no encontrado")
    session.delete(product)
    session.commit()
