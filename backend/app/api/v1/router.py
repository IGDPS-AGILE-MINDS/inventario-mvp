from fastapi import APIRouter

from app.api.v1 import admin, categories, dashboard, movements, products, settings, suppliers

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(categories.router)
api_router.include_router(suppliers.router)
api_router.include_router(products.router)
api_router.include_router(movements.router)
api_router.include_router(settings.router)
api_router.include_router(dashboard.router)
api_router.include_router(admin.router)
