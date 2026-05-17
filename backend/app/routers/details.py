from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db_session
from app.schemas.detail import (
    DetailCreate,
    DetailPartialUpdate,
    DetailReadFull,
    DetailUpdate,
)
from app.services.detail_service import detail_service


router = APIRouter(prefix="/details", tags=["details"])

SessionDep = Annotated[AsyncSession, Depends(get_db_session)]


@router.get("", response_model=list[DetailReadFull])
async def get_details(
    session: SessionDep,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
):
    return await detail_service.get_details(session, skip=skip, limit=limit)


@router.get("/{detail_id}", response_model=DetailReadFull)
async def get_detail(detail_id: int, session: SessionDep):
    return await detail_service.get_detail_by_id(session, detail_id)


@router.post(
    "",
    response_model=DetailReadFull,
    status_code=status.HTTP_201_CREATED,
)
async def create_detail(payload: DetailCreate, session: SessionDep):
    return await detail_service.create_detail(session, payload)


@router.put("/{detail_id}", response_model=DetailReadFull)
async def update_detail(
    detail_id: int,
    payload: DetailUpdate,
    session: SessionDep,
):
    return await detail_service.update_detail(session, detail_id, payload)


@router.patch("/{detail_id}", response_model=DetailReadFull)
async def partial_update_detail(
    detail_id: int,
    payload: DetailPartialUpdate,
    session: SessionDep,
):
    return await detail_service.partial_update_detail(session, detail_id, payload)


@router.delete("/{detail_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_detail(detail_id: int, session: SessionDep) -> None:
    await detail_service.delete_detail(session, detail_id)
