from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db_session
from app.schemas.warehouse import (
    WarehouseCreate,
    WarehousePartialUpdate,
    WarehouseRead,
    WarehouseUpdate,
)
from app.services.warehouse_service import warehouse_service


router = APIRouter(prefix="/warehouses", tags=["warehouses"])

SessionDep = Annotated[AsyncSession, Depends(get_db_session)]


@router.get("", response_model=list[WarehouseRead])
async def get_warehouses(
    session: SessionDep,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
):
    return await warehouse_service.get_warehouses(session, skip=skip, limit=limit)


@router.get("/{warehouse_id}", response_model=WarehouseRead)
async def get_warehouse(warehouse_id: int, session: SessionDep):
    return await warehouse_service.get_warehouse_by_id(session, warehouse_id)


@router.post(
    "",
    response_model=WarehouseRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_warehouse(payload: WarehouseCreate, session: SessionDep):
    return await warehouse_service.create_warehouse(session, payload)


@router.put("/{warehouse_id}", response_model=WarehouseRead)
async def update_warehouse(
    warehouse_id: int,
    payload: WarehouseUpdate,
    session: SessionDep,
):
    return await warehouse_service.update_warehouse(session, warehouse_id, payload)


@router.patch("/{warehouse_id}", response_model=WarehouseRead)
async def partial_update_warehouse(
    warehouse_id: int,
    payload: WarehousePartialUpdate,
    session: SessionDep,
):
    return await warehouse_service.partial_update_warehouse(
        session,
        warehouse_id,
        payload,
    )


@router.delete("/{warehouse_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_warehouse(warehouse_id: int, session: SessionDep) -> None:
    await warehouse_service.delete_warehouse(session, warehouse_id)
