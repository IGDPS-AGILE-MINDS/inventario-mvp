from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.category import Category
from app.models.product import Product
from app.models.base import utcnow
from app.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/", response_model=list[CategoryRead])
def list_categories(session: Session = Depends(get_session)):
    return session.exec(select(Category).order_by(Category.name)).all()


@router.post("/", response_model=CategoryRead, status_code=201)
def create_category(data: CategoryCreate, session: Session = Depends(get_session)):
    category = Category.model_validate(data)
    session.add(category)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(400, "La categoría ya existe")
    session.refresh(category)
    return category


@router.put("/{category_id}", response_model=CategoryRead)
def update_category(category_id: int, data: CategoryUpdate, session: Session = Depends(get_session)):
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(404, "Categoría no encontrada")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(category, key, value)
    category.updated_at = utcnow()
    session.add(category)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(400, "La categoría ya existe")
    session.refresh(category)
    return category


@router.delete("/{category_id}", status_code=204)
def delete_category(category_id: int, session: Session = Depends(get_session)):
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(404, "Categoría no encontrada")
    linked_products = session.exec(select(func.count(Product.id)).where(Product.category_id == category_id)).one()
    if linked_products:
        raise HTTPException(409, "No se puede eliminar la categoría porque tiene productos asociados")
    session.delete(category)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(409, "No se puede eliminar la categoría porque tiene productos asociados")
