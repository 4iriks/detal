from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db_session
from app.schemas.category import (
    CategoryCreate,
    CategoryPartialUpdate,
    CategoryRead,
    CategoryUpdate,
)
from app.services.category_service import category_service


router = APIRouter(prefix="/categories", tags=["categories"])

SessionDep = Annotated[AsyncSession, Depends(get_db_session)]


@router.get("", response_model=list[CategoryRead])
async def get_categories(
    session: SessionDep,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
):
    return await category_service.get_categories(session, skip=skip, limit=limit)


@router.get("/{category_id}", response_model=CategoryRead)
async def get_category(category_id: int, session: SessionDep):
    return await category_service.get_category_by_id(session, category_id)


@router.post(
    "",
    response_model=CategoryRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_category(payload: CategoryCreate, session: SessionDep):
    return await category_service.create_category(session, payload)


@router.put("/{category_id}", response_model=CategoryRead)
async def update_category(
    category_id: int,
    payload: CategoryUpdate,
    session: SessionDep,
):
    return await category_service.update_category(session, category_id, payload)


@router.patch("/{category_id}", response_model=CategoryRead)
async def partial_update_category(
    category_id: int,
    payload: CategoryPartialUpdate,
    session: SessionDep,
):
    return await category_service.partial_update_category(session, category_id, payload)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(category_id: int, session: SessionDep) -> None:
    await category_service.delete_category(session, category_id)
