import asyncio
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import async_session_maker
from app.models.category import Category
from app.models.detail import Detail
from app.models.supplier import Supplier
from app.models.warehouse import Warehouse


CATEGORIES = [
    {
        "name": "Крепеж",
        "description": "Болты, гайки, шайбы и другие крепежные элементы.",
    },
    {
        "name": "Электронные компоненты",
        "description": "Радиодетали и компоненты для электронных узлов.",
    },
    {
        "name": "Механические детали",
        "description": "Подшипники, валы, шестерни и элементы механизмов.",
    },
    {
        "name": "Корпусные элементы",
        "description": "Корпуса, панели, пластины и элементы конструкций.",
    },
]

SUPPLIERS = [
    {
        "name": "ООО «ТехноПоставка»",
        "email": "sales@technopostavka.ru",
        "phone": "+7 495 101-20-30",
        "address": "г. Москва, Промышленная ул., 15",
    },
    {
        "name": "ЗАО «ПромКомплект»",
        "email": "info@promkomplekt.ru",
        "phone": "+7 812 210-30-40",
        "address": "г. Санкт-Петербург, Складской пр., 8",
    },
    {
        "name": "ООО «Механика-Сервис»",
        "email": "order@mechanika-service.ru",
        "phone": "+7 343 300-40-50",
        "address": "г. Екатеринбург, Заводская ул., 22",
    },
]

WAREHOUSES = [
    {
        "name": "Основной склад",
        "address": "г. Москва, Заводская ул., 10",
        "responsible_person": "Иванов Иван Иванович",
    },
    {
        "name": "Склад комплектующих",
        "address": "г. Москва, Производственный проезд, 7",
        "responsible_person": "Петров Петр Петрович",
    },
    {
        "name": "Резервный склад",
        "address": "г. Москва, Складская ул., 3",
        "responsible_person": "Сидоров Сергей Сергеевич",
    },
]

DETAILS = [
    {
        "name": "Болт М8",
        "article": "BOLT-M8-001",
        "material": "Сталь",
        "weight": Decimal("0.035"),
        "price": Decimal("12.50"),
        "quantity": 120,
        "category": "Крепеж",
        "supplier": "sales@technopostavka.ru",
        "warehouse": "Основной склад",
    },
    {
        "name": "Гайка М8",
        "article": "NUT-M8-001",
        "material": "Сталь",
        "weight": Decimal("0.012"),
        "price": Decimal("5.20"),
        "quantity": 180,
        "category": "Крепеж",
        "supplier": "sales@technopostavka.ru",
        "warehouse": "Основной склад",
    },
    {
        "name": "Шайба 8 мм",
        "article": "WASHER-8-001",
        "material": "Оцинкованная сталь",
        "weight": Decimal("0.006"),
        "price": Decimal("3.10"),
        "quantity": 240,
        "category": "Крепеж",
        "supplier": "info@promkomplekt.ru",
        "warehouse": "Склад комплектующих",
    },
    {
        "name": "Подшипник 608ZZ",
        "article": "BEARING-608ZZ",
        "material": "Сталь",
        "weight": Decimal("0.120"),
        "price": Decimal("95.00"),
        "quantity": 35,
        "category": "Механические детали",
        "supplier": "order@mechanika-service.ru",
        "warehouse": "Склад комплектующих",
    },
    {
        "name": "Резистор 10 кОм",
        "article": "RES-10K-025W",
        "material": "Керамика",
        "weight": Decimal("0.001"),
        "price": Decimal("1.80"),
        "quantity": 500,
        "category": "Электронные компоненты",
        "supplier": "sales@technopostavka.ru",
        "warehouse": "Склад комплектующих",
    },
    {
        "name": "Конденсатор 100 мкФ",
        "article": "CAP-100UF-25V",
        "material": "Алюминий",
        "weight": Decimal("0.004"),
        "price": Decimal("8.40"),
        "quantity": 300,
        "category": "Электронные компоненты",
        "supplier": "sales@technopostavka.ru",
        "warehouse": "Склад комплектующих",
    },
    {
        "name": "Стальная пластина",
        "article": "PLATE-ST-120X80",
        "material": "Сталь",
        "weight": Decimal("0.450"),
        "price": Decimal("210.00"),
        "quantity": 24,
        "category": "Корпусные элементы",
        "supplier": "info@promkomplekt.ru",
        "warehouse": "Основной склад",
    },
    {
        "name": "Алюминиевый корпус",
        "article": "CASE-AL-001",
        "material": "Алюминий",
        "weight": Decimal("0.780"),
        "price": Decimal("580.00"),
        "quantity": 12,
        "category": "Корпусные элементы",
        "supplier": "info@promkomplekt.ru",
        "warehouse": "Резервный склад",
    },
    {
        "name": "Вал приводной",
        "article": "SHAFT-DRV-250",
        "material": "Легированная сталь",
        "weight": Decimal("1.250"),
        "price": Decimal("1250.00"),
        "quantity": 4,
        "category": "Механические детали",
        "supplier": "order@mechanika-service.ru",
        "warehouse": "Резервный склад",
    },
    {
        "name": "Шестерня малая",
        "article": "GEAR-SM-032",
        "material": "Сталь",
        "weight": Decimal("0.330"),
        "price": Decimal("430.00"),
        "quantity": 6,
        "category": "Механические детали",
        "supplier": "order@mechanika-service.ru",
        "warehouse": "Основной склад",
    },
]


async def get_or_create_category(
    session: AsyncSession,
    category_data: dict,
) -> Category:
    result = await session.execute(
        select(Category).where(Category.name == category_data["name"])
    )
    category = result.scalar_one_or_none()
    if category is not None:
        return category

    category = Category(**category_data)
    session.add(category)
    await session.flush()
    return category


async def get_or_create_supplier(
    session: AsyncSession,
    supplier_data: dict,
) -> Supplier:
    result = await session.execute(
        select(Supplier).where(Supplier.email == supplier_data["email"])
    )
    supplier = result.scalar_one_or_none()
    if supplier is not None:
        return supplier

    supplier = Supplier(**supplier_data)
    session.add(supplier)
    await session.flush()
    return supplier


async def get_or_create_warehouse(
    session: AsyncSession,
    warehouse_data: dict,
) -> Warehouse:
    result = await session.execute(
        select(Warehouse).where(Warehouse.name == warehouse_data["name"])
    )
    warehouse = result.scalar_one_or_none()
    if warehouse is not None:
        return warehouse

    warehouse = Warehouse(**warehouse_data)
    session.add(warehouse)
    await session.flush()
    return warehouse


async def create_detail_if_missing(
    session: AsyncSession,
    detail_data: dict,
    categories_by_name: dict[str, Category],
    suppliers_by_email: dict[str, Supplier],
    warehouses_by_name: dict[str, Warehouse],
) -> Detail | None:
    result = await session.execute(
        select(Detail).where(Detail.article == detail_data["article"])
    )
    if result.scalar_one_or_none() is not None:
        return None

    category = categories_by_name[detail_data["category"]]
    supplier = suppliers_by_email[detail_data["supplier"]]
    warehouse = warehouses_by_name[detail_data["warehouse"]]

    detail = Detail(
        name=detail_data["name"],
        article=detail_data["article"],
        material=detail_data["material"],
        weight=detail_data["weight"],
        price=detail_data["price"],
        quantity=detail_data["quantity"],
        category_id=category.id,
        supplier_id=supplier.id,
        warehouse_id=warehouse.id,
    )
    session.add(detail)
    await session.flush()
    return detail


async def get_count(session: AsyncSession, model) -> int:
    result = await session.execute(select(func.count()).select_from(model))
    return int(result.scalar_one())


async def seed_database() -> None:
    async with async_session_maker() as session:
        categories = [
            await get_or_create_category(session, category_data)
            for category_data in CATEGORIES
        ]
        suppliers = [
            await get_or_create_supplier(session, supplier_data)
            for supplier_data in SUPPLIERS
        ]
        warehouses = [
            await get_or_create_warehouse(session, warehouse_data)
            for warehouse_data in WAREHOUSES
        ]

        categories_by_name = {category.name: category for category in categories}
        suppliers_by_email = {supplier.email: supplier for supplier in suppliers}
        warehouses_by_name = {warehouse.name: warehouse for warehouse in warehouses}

        for detail_data in DETAILS:
            await create_detail_if_missing(
                session,
                detail_data,
                categories_by_name,
                suppliers_by_email,
                warehouses_by_name,
            )

        await session.commit()

        categories_count = await get_count(session, Category)
        suppliers_count = await get_count(session, Supplier)
        warehouses_count = await get_count(session, Warehouse)
        details_count = await get_count(session, Detail)

    print("Демонстрационные данные готовы.")
    print(f"Категорий в базе: {categories_count}")
    print(f"Поставщиков в базе: {suppliers_count}")
    print(f"Складов в базе: {warehouses_count}")
    print(f"Деталей в базе: {details_count}")


def main() -> None:
    asyncio.run(seed_database())


if __name__ == "__main__":
    main()
