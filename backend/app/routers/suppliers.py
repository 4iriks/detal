from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db_session
from app.schemas.supplier import (
    SupplierCreate,
    SupplierPartialUpdate,
    SupplierRead,
    SupplierUpdate,
)
from app.services.supplier_service import supplier_service


router = APIRouter(prefix="/suppliers", tags=["suppliers"])

SessionDep = Annotated[AsyncSession, Depends(get_db_session)]


@router.get("", response_model=list[SupplierRead])
async def get_suppliers(
    session: SessionDep,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
):
    return await supplier_service.get_suppliers(session, skip=skip, limit=limit)


@router.get("/{supplier_id}", response_model=SupplierRead)
async def get_supplier(supplier_id: int, session: SessionDep):
    return await supplier_service.get_supplier_by_id(session, supplier_id)


@router.post(
    "",
    response_model=SupplierRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_supplier(payload: SupplierCreate, session: SessionDep):
    return await supplier_service.create_supplier(session, payload)


@router.put("/{supplier_id}", response_model=SupplierRead)
async def update_supplier(
    supplier_id: int,
    payload: SupplierUpdate,
    session: SessionDep,
):
    return await supplier_service.update_supplier(session, supplier_id, payload)


@router.patch("/{supplier_id}", response_model=SupplierRead)
async def partial_update_supplier(
    supplier_id: int,
    payload: SupplierPartialUpdate,
    session: SessionDep,
):
    return await supplier_service.partial_update_supplier(session, supplier_id, payload)


@router.delete("/{supplier_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_supplier(supplier_id: int, session: SessionDep) -> None:
    await supplier_service.delete_supplier(session, supplier_id)
