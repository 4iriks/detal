from app.routers.categories import router as categories_router
from app.routers.details import router as details_router
from app.routers.health import router as health_router
from app.routers.suppliers import router as suppliers_router
from app.routers.warehouses import router as warehouses_router

__all__ = [
    "categories_router",
    "details_router",
    "health_router",
    "suppliers_router",
    "warehouses_router",
]
