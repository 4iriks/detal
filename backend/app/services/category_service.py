from fastapi import HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.schemas.category import (
    CategoryCreate,
    CategoryPartialUpdate,
    CategoryUpdate,
)


class CategoryService:
    async def get_categories(
        self,
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Category]:
        result = await session.execute(
            select(Category).order_by(Category.id).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def get_category_by_id(
        self,
        session: AsyncSession,
        category_id: int,
    ) -> Category:
        category = await session.get(Category, category_id)
        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Категория не найдена",
            )
        return category

    async def create_category(
        self,
        session: AsyncSession,
        payload: CategoryCreate,
    ) -> Category:
        await self._raise_if_name_exists(session, payload.name)

        category = Category(**payload.model_dump())
        session.add(category)

        try:
            await session.commit()
            await session.refresh(category)
        except IntegrityError as exc:
            await session.rollback()
            raise self._name_conflict_error() from exc

        return category

    async def update_category(
        self,
        session: AsyncSession,
        category_id: int,
        payload: CategoryUpdate,
    ) -> Category:
        category = await self.get_category_by_id(session, category_id)
        await self._raise_if_name_exists(session, payload.name, exclude_id=category_id)

        category.name = payload.name
        category.description = payload.description

        try:
            await session.commit()
            await session.refresh(category)
        except IntegrityError as exc:
            await session.rollback()
            raise self._name_conflict_error() from exc

        return category

    async def partial_update_category(
        self,
        session: AsyncSession,
        category_id: int,
        payload: CategoryPartialUpdate,
    ) -> Category:
        category = await self.get_category_by_id(session, category_id)
        update_data = payload.model_dump(exclude_unset=True)

        if "name" in update_data:
            await self._raise_if_name_exists(
                session,
                update_data["name"],
                exclude_id=category_id,
            )

        for field, value in update_data.items():
            setattr(category, field, value)

        try:
            await session.commit()
            await session.refresh(category)
        except IntegrityError as exc:
            await session.rollback()
            raise self._name_conflict_error() from exc

        return category

    async def delete_category(
        self,
        session: AsyncSession,
        category_id: int,
    ) -> None:
        await self.get_category_by_id(session, category_id)

        try:
            await session.execute(delete(Category).where(Category.id == category_id))
            await session.commit()
        except IntegrityError as exc:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Категорию нельзя удалить, потому что она используется деталями",
            ) from exc

    async def _raise_if_name_exists(
        self,
        session: AsyncSession,
        name: str,
        exclude_id: int | None = None,
    ) -> None:
        query = select(Category).where(Category.name == name)
        if exclude_id is not None:
            query = query.where(Category.id != exclude_id)

        result = await session.execute(query)
        if result.scalar_one_or_none() is not None:
            raise self._name_conflict_error()

    @staticmethod
    def _name_conflict_error() -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Категория с таким названием уже существует",
        )


category_service = CategoryService()
