from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.categories import router as categories_router
from app.routers.details import router as details_router
from app.routers.health import router as health_router
from app.routers.suppliers import router as suppliers_router
from app.routers.warehouses import router as warehouses_router


app = FastAPI(
    title="Detail Warehouse Accounting API",
    description="Backend API for a coursework project about accounting details in a warehouse.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(categories_router)
app.include_router(suppliers_router)
app.include_router(warehouses_router)
app.include_router(details_router)
