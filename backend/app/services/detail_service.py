from fastapi import HTTPException, status
from sqlalchemy import delete, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.category import Category
from app.models.detail import Detail
from app.models.supplier import Supplier
from app.models.warehouse import Warehouse
from app.schemas.detail import (
    DetailCreate,
    DetailPartialUpdate,
    DetailQuantityUpdate,
    DetailUpdate,
)


class DetailService:
    async def get_details(
        self,
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        category_id: int | None = None,
        supplier_id: int | None = None,
        warehouse_id: int | None = None,
        search: str | None = None,
    ) -> list[Detail]:
        query = select(Detail).options(*self._detail_options())

        if category_id is not None:
            query = query.where(Detail.category_id == category_id)
        if supplier_id is not None:
            query = query.where(Detail.supplier_id == supplier_id)
        if warehouse_id is not None:
            query = query.where(Detail.warehouse_id == warehouse_id)

        if search is not None:
            normalized_search = search.strip()
            if normalized_search:
                pattern = f"%{normalized_search}%"
                query = query.where(
                    or_(
                        Detail.name.ilike(pattern),
                        Detail.article.ilike(pattern),
                        Detail.material.ilike(pattern),
                    )
                )

        query = query.order_by(Detail.id).offset(skip).limit(limit)
        result = await session.execute(query)
        return list(result.scalars().all())

    async def get_detail_by_id(
        self,
        session: AsyncSession,
        detail_id: int,
    ) -> Detail:
        result = await session.execute(
            select(Detail)
            .options(*self._detail_options())
            .where(Detail.id == detail_id)
        )
        detail = result.scalar_one_or_none()
        if detail is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Деталь не найдена",
            )
        return detail

    async def create_detail(
        self,
        session: AsyncSession,
        payload: DetailCreate,
    ) -> Detail:
        detail_data = payload.model_dump()
        await self._validate_references(session, detail_data)
        await self._raise_if_article_exists(session, detail_data["article"])

        detail = Detail(**detail_data)
        session.add(detail)

        try:
            await session.commit()
        except IntegrityError as exc:
            await session.rollback()
            raise self._article_conflict_error() from exc

        return await self.get_detail_by_id(session, detail.id)

    async def update_detail(
        self,
        session: AsyncSession,
        detail_id: int,
        payload: DetailUpdate,
    ) -> Detail:
        detail = await self.get_detail_by_id(session, detail_id)
        detail_data = payload.model_dump()

        await self._validate_references(session, detail_data)
        await self._raise_if_article_exists(
            session,
            detail_data["article"],
            exclude_id=detail_id,
        )

        for field, value in detail_data.items():
            setattr(detail, field, value)

        try:
            await session.commit()
        except IntegrityError as exc:
            await session.rollback()
            raise self._article_conflict_error() from exc

        return await self.get_detail_by_id(session, detail_id)

    async def partial_update_detail(
        self,
        session: AsyncSession,
        detail_id: int,
        payload: DetailPartialUpdate,
    ) -> Detail:
        detail = await self.get_detail_by_id(session, detail_id)
        update_data = payload.model_dump(exclude_unset=True)

        await self._validate_references(session, update_data, partial=True)
        if "article" in update_data:
            await self._raise_if_article_exists(
                session,
                update_data["article"],
                exclude_id=detail_id,
            )

        for field, value in update_data.items():
            setattr(detail, field, value)

        try:
            await session.commit()
        except IntegrityError as exc:
            await session.rollback()
            raise self._article_conflict_error() from exc

        return await self.get_detail_by_id(session, detail_id)

    async def delete_detail(
        self,
        session: AsyncSession,
        detail_id: int,
    ) -> None:
        await self.get_detail_by_id(session, detail_id)

        try:
            await session.execute(delete(Detail).where(Detail.id == detail_id))
            await session.commit()
        except IntegrityError as exc:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Деталь нельзя удалить из-за ограничений базы данных",
            ) from exc

    async def get_low_stock_details(
        self,
        session: AsyncSession,
        threshold: int = 5,
    ) -> list[Detail]:
        result = await session.execute(
            select(Detail)
            .options(*self._detail_options())
            .where(Detail.quantity <= threshold)
            .order_by(Detail.quantity, Detail.id)
        )
        return list(result.scalars().all())

    async def update_detail_quantity(
        self,
        session: AsyncSession,
        detail_id: int,
        payload: DetailQuantityUpdate,
    ) -> Detail:
        detail = await self.get_detail_by_id(session, detail_id)
        detail.quantity = payload.quantity

        try:
            await session.commit()
        except IntegrityError as exc:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Количество детали не удалось изменить",
            ) from exc

        return await self.get_detail_by_id(session, detail_id)

    async def _validate_references(
        self,
        session: AsyncSession,
        data: dict,
        partial: bool = False,
    ) -> None:
        if not partial or "category_id" in data:
            await self._raise_if_missing(
                session,
                Category,
                data["category_id"],
                "Категория не найдена",
            )

        if "supplier_id" in data and data["supplier_id"] is not None:
            await self._raise_if_missing(
                session,
                Supplier,
                data["supplier_id"],
                "Поставщик не найден",
            )

        if "warehouse_id" in data and data["warehouse_id"] is not None:
            await self._raise_if_missing(
                session,
                Warehouse,
                data["warehouse_id"],
                "Склад не найден",
            )

    async def _raise_if_missing(
        self,
        session: AsyncSession,
        model,
        object_id: int,
        message: str,
    ) -> None:
        if await session.get(model, object_id) is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=message,
            )

    async def _raise_if_article_exists(
        self,
        session: AsyncSession,
        article: str,
        exclude_id: int | None = None,
    ) -> None:
        query = select(Detail).where(Detail.article == article)
        if exclude_id is not None:
            query = query.where(Detail.id != exclude_id)

        result = await session.execute(query)
        if result.scalar_one_or_none() is not None:
            raise self._article_conflict_error()

    @staticmethod
    def _article_conflict_error() -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Деталь с таким артикулом уже существует",
        )

    @staticmethod
    def _detail_options():
        return (
            selectinload(Detail.category),
            selectinload(Detail.supplier),
            selectinload(Detail.warehouse),
        )


detail_service = DetailService()
