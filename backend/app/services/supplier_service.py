from fastapi import HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.supplier import Supplier
from app.schemas.supplier import (
    SupplierCreate,
    SupplierPartialUpdate,
    SupplierUpdate,
)


class SupplierService:
    async def get_suppliers(
        self,
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Supplier]:
        result = await session.execute(
            select(Supplier).order_by(Supplier.id).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def get_supplier_by_id(
        self,
        session: AsyncSession,
        supplier_id: int,
    ) -> Supplier:
        supplier = await session.get(Supplier, supplier_id)
        if supplier is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Поставщик не найден",
            )
        return supplier

    async def create_supplier(
        self,
        session: AsyncSession,
        payload: SupplierCreate,
    ) -> Supplier:
        supplier_data = payload.model_dump()
        supplier_data["email"] = str(supplier_data["email"])

        await self._raise_if_email_exists(session, supplier_data["email"])

        supplier = Supplier(**supplier_data)
        session.add(supplier)

        try:
            await session.commit()
            await session.refresh(supplier)
        except IntegrityError as exc:
            await session.rollback()
            raise self._email_conflict_error() from exc

        return supplier

    async def update_supplier(
        self,
        session: AsyncSession,
        supplier_id: int,
        payload: SupplierUpdate,
    ) -> Supplier:
        supplier = await self.get_supplier_by_id(session, supplier_id)
        supplier_data = payload.model_dump()
        supplier_data["email"] = str(supplier_data["email"])

        await self._raise_if_email_exists(
            session,
            supplier_data["email"],
            exclude_id=supplier_id,
        )

        supplier.name = supplier_data["name"]
        supplier.email = supplier_data["email"]
        supplier.phone = supplier_data["phone"]
        supplier.address = supplier_data["address"]

        try:
            await session.commit()
            await session.refresh(supplier)
        except IntegrityError as exc:
            await session.rollback()
            raise self._email_conflict_error() from exc

        return supplier

    async def partial_update_supplier(
        self,
        session: AsyncSession,
        supplier_id: int,
        payload: SupplierPartialUpdate,
    ) -> Supplier:
        supplier = await self.get_supplier_by_id(session, supplier_id)
        update_data = payload.model_dump(exclude_unset=True)

        if "email" in update_data:
            update_data["email"] = str(update_data["email"])
            await self._raise_if_email_exists(
                session,
                update_data["email"],
                exclude_id=supplier_id,
            )

        for field, value in update_data.items():
            setattr(supplier, field, value)

        try:
            await session.commit()
            await session.refresh(supplier)
        except IntegrityError as exc:
            await session.rollback()
            raise self._email_conflict_error() from exc

        return supplier

    async def delete_supplier(
        self,
        session: AsyncSession,
        supplier_id: int,
    ) -> None:
        await self.get_supplier_by_id(session, supplier_id)

        try:
            await session.execute(delete(Supplier).where(Supplier.id == supplier_id))
            await session.commit()
        except IntegrityError as exc:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Поставщика нельзя удалить, потому что он используется деталями",
            ) from exc

    async def _raise_if_email_exists(
        self,
        session: AsyncSession,
        email: str,
        exclude_id: int | None = None,
    ) -> None:
        query = select(Supplier).where(Supplier.email == email)
        if exclude_id is not None:
            query = query.where(Supplier.id != exclude_id)

        result = await session.execute(query)
        if result.scalar_one_or_none() is not None:
            raise self._email_conflict_error()

    @staticmethod
    def _email_conflict_error() -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Поставщик с таким email уже существует",
        )


supplier_service = SupplierService()
