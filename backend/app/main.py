from fastapi import FastAPI

from app.routers.categories import router as categories_router
from app.routers.health import router as health_router


app = FastAPI(
    title="Detail Warehouse Accounting API",
    description="Backend API for a coursework project about accounting details in a warehouse.",
    version="0.1.0",
)

app.include_router(health_router)
app.include_router(categories_router)
