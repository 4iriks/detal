from fastapi import HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.warehouse import Warehouse
from app.schemas.warehouse import (
    WarehouseCreate,
    WarehousePartialUpdate,
    WarehouseUpdate,
)


class WarehouseService:
    async def get_warehouses(
        self,
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Warehouse]:
        result = await session.execute(
            select(Warehouse).order_by(Warehouse.id).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def get_warehouse_by_id(
        self,
        session: AsyncSession,
        warehouse_id: int,
    ) -> Warehouse:
        warehouse = await session.get(Warehouse, warehouse_id)
        if warehouse is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Склад не найден",
            )
        return warehouse

    async def create_warehouse(
        self,
        session: AsyncSession,
        payload: WarehouseCreate,
    ) -> Warehouse:
        await self._raise_if_name_exists(session, payload.name)

        warehouse = Warehouse(**payload.model_dump())
        session.add(warehouse)

        try:
            await session.commit()
            await session.refresh(warehouse)
        except IntegrityError as exc:
            await session.rollback()
            raise self._name_conflict_error() from exc

        return warehouse

    async def update_warehouse(
        self,
        session: AsyncSession,
        warehouse_id: int,
        payload: WarehouseUpdate,
    ) -> Warehouse:
        warehouse = await self.get_warehouse_by_id(session, warehouse_id)
        await self._raise_if_name_exists(session, payload.name, exclude_id=warehouse_id)

        warehouse.name = payload.name
        warehouse.address = payload.address
        warehouse.responsible_person = payload.responsible_person

        try:
            await session.commit()
            await session.refresh(warehouse)
        except IntegrityError as exc:
            await session.rollback()
            raise self._name_conflict_error() from exc

        return warehouse

    async def partial_update_warehouse(
        self,
        session: AsyncSession,
        warehouse_id: int,
        payload: WarehousePartialUpdate,
    ) -> Warehouse:
        warehouse = await self.get_warehouse_by_id(session, warehouse_id)
        update_data = payload.model_dump(exclude_unset=True)

        if "name" in update_data:
            await self._raise_if_name_exists(
                session,
                update_data["name"],
                exclude_id=warehouse_id,
            )

        for field, value in update_data.items():
            setattr(warehouse, field, value)

        try:
            await session.commit()
            await session.refresh(warehouse)
        except IntegrityError as exc:
            await session.rollback()
            raise self._name_conflict_error() from exc

        return warehouse

    async def delete_warehouse(
        self,
        session: AsyncSession,
        warehouse_id: int,
    ) -> None:
        await self.get_warehouse_by_id(session, warehouse_id)

        try:
            await session.execute(delete(Warehouse).where(Warehouse.id == warehouse_id))
            await session.commit()
        except IntegrityError as exc:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Склад нельзя удалить, потому что он используется деталями",
            ) from exc

    async def _raise_if_name_exists(
        self,
        session: AsyncSession,
        name: str,
        exclude_id: int | None = None,
    ) -> None:
        query = select(Warehouse).where(Warehouse.name == name)
        if exclude_id is not None:
            query = query.where(Warehouse.id != exclude_id)

        result = await session.execute(query)
        if result.scalar_one_or_none() is not None:
            raise self._name_conflict_error()

    @staticmethod
    def _name_conflict_error() -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Склад с таким названием уже существует",
        )


warehouse_service = WarehouseService()
