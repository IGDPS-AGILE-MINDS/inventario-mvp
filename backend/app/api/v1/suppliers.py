from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.base import utcnow
from app.models.supplier import Supplier
from app.models.product import Product
from app.schemas.supplier import SupplierCreate, SupplierRead, SupplierUpdate

router = APIRouter(prefix="/suppliers", tags=["suppliers"])


@router.get("/", response_model=list[SupplierRead])
def list_suppliers(session: Session = Depends(get_session)):
    return session.exec(select(Supplier).order_by(Supplier.name)).all()


@router.post("/", response_model=SupplierRead, status_code=201)
def create_supplier(data: SupplierCreate, session: Session = Depends(get_session)):
    supplier = Supplier.model_validate(data)
    session.add(supplier)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(400, "El proveedor ya existe")
    session.refresh(supplier)
    return supplier


@router.put("/{supplier_id}", response_model=SupplierRead)
def update_supplier(supplier_id: int, data: SupplierUpdate, session: Session = Depends(get_session)):
    supplier = session.get(Supplier, supplier_id)
    if not supplier:
        raise HTTPException(404, "Proveedor no encontrado")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(supplier, key, value)
    supplier.updated_at = utcnow()
    session.add(supplier)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(400, "El proveedor ya existe")
    session.refresh(supplier)
    return supplier


@router.delete("/{supplier_id}", status_code=204)
def delete_supplier(supplier_id: int, session: Session = Depends(get_session)):
    supplier = session.get(Supplier, supplier_id)
    if not supplier:
        raise HTTPException(404, "Proveedor no encontrado")
    linked_products = session.exec(select(func.count(Product.id)).where(Product.supplier_id == supplier_id)).one()
    if linked_products:
        raise HTTPException(409, "No se puede eliminar el proveedor porque tiene productos asociados")
    session.delete(supplier)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(409, "No se puede eliminar el proveedor porque tiene productos asociados")
