# Backend: учет деталей на складе предприятия

Backend для курсовой работы «Разработка клиент-серверного приложения для учета деталей на складе предприятия».

## Стек

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy 2.x
- Alembic
- Pydantic Settings

## Структура

```text
backend/
  app/
    main.py
    core/
      config.py
    database/
      session.py
      base.py
    models/
      category.py
      detail.py
      supplier.py
      warehouse.py
    schemas/
    routers/
      health.py
    services/
  alembic/
    versions/
      20260517_0001_core_tables.py
      20260517_0002_detail_article_length.py
      20260517_0003_db_objects.py
  alembic.ini
  requirements.txt
  .env.example
```

## Таблицы БД

В первой миграции создаются 4 основные таблицы:

- `categories` - категории деталей: название, описание, даты создания и обновления.
- `suppliers` - поставщики: название, email, телефон, адрес, даты создания и обновления.
- `warehouses` - склады: название, адрес, ответственное лицо, даты создания и обновления.
- `details` - детали: название, артикул, материал, вес, цена, количество и связи с категорией, поставщиком и складом.

Связи:

- `categories.id` -> `details.category_id`: одна категория содержит много деталей.
- `suppliers.id` -> `details.supplier_id`: один поставщик связан со многими деталями.
- `warehouses.id` -> `details.warehouse_id`: один склад связан со многими деталями.

В миграции также добавлены ограничения уникальности и индексы для:

- `categories.name`
- `suppliers.email`
- `warehouses.name`
- `details.article`

## SQL-объекты БД

Миграция `20260517_0003_db_objects.py` добавляет SQL-объекты PostgreSQL для требований курсовой работы.

Таблица журнала:

- `detail_logs` - хранит изменения количества и цены деталей.

Представления:

- `view_details_full` - показывает детали вместе с названием категории, поставщика и склада.
- `view_low_stock_details` - показывает детали с количеством `quantity <= 5`.
- `view_supplier_details_summary` - показывает сводку по поставщикам: количество деталей, общий остаток и суммарную стоимость.

Функции:

- `get_total_details_count()` - возвращает общее количество деталей.
- `calculate_total_stock_value()` - возвращает общую стоимость остатков деталей.
- `get_details_count_by_category(p_category_id integer)` - возвращает количество деталей в выбранной категории.

Процедуры:

- `increase_detail_quantity(p_detail_id integer, p_amount integer)` - увеличивает количество детали.
- `decrease_detail_quantity(p_detail_id integer, p_amount integer)` - уменьшает количество детали и не допускает отрицательный остаток.
- `set_detail_price(p_detail_id integer, p_price numeric)` - изменяет цену детали и не допускает отрицательную цену.

Триггеры:

- `trigger_check_detail_values` - проверяет, что `quantity`, `price` и `weight` не отрицательные.
- `trigger_update_detail_updated_at` - автоматически обновляет `updated_at` при изменении детали.
- `trigger_log_detail_changes` - записывает изменение `quantity` или `price` в `detail_logs`.

## Запуск через Docker

Команды выполняются из корня проекта.

Запустить PostgreSQL и FastAPI backend:

```powershell
docker compose up --build
```

Применить миграции Alembic:

```powershell
docker compose exec backend alembic upgrade head
```

Проверочные адреса:

```text
http://localhost:8000/health
http://localhost:8000/docs
```

Остановить контейнеры:

```powershell
docker compose down
```

Остановить контейнеры и полностью очистить данные PostgreSQL:

```powershell
docker compose down -v
```

## Подготовка окружения

Команды выполняются из папки `backend`.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Создайте файл `.env` на основе примера:

```powershell
Copy-Item .env.example .env
```

Проверьте строку подключения к PostgreSQL:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/detail_warehouse
```

База данных должна быть создана в PostgreSQL заранее. SQLite в проекте не используется.

## Миграции

Применить текущие миграции:

```powershell
alembic upgrade head
```

Создать новую миграцию после изменения моделей:

```powershell
alembic revision --autogenerate -m "описание миграции"
```

Откатить последнюю миграцию:

```powershell
alembic downgrade -1
```

## Запуск сервера

```powershell
uvicorn app.main:app --reload
```

После запуска endpoint проверки доступен по адресу:

```text
GET http://127.0.0.1:8000/health
```

Ответ:

```json
{
  "status": "ok"
}
```

Swagger UI доступен после запуска сервера:

```text
http://127.0.0.1:8000/docs
```

## API категорий

Для сущности `Category` реализован CRUD:

```text
GET    /categories?skip=0&limit=100
GET    /categories/{category_id}
POST   /categories
PUT    /categories/{category_id}
PATCH  /categories/{category_id}
DELETE /categories/{category_id}
```

Пример JSON для `POST /categories`:

```json
{
  "name": "Крепеж",
  "description": "Болты, гайки, шайбы и другие крепежные элементы"
}
```

Пример JSON для `PUT /categories/{category_id}`:

```json
{
  "name": "Механические детали",
  "description": "Валы, шестерни, корпуса и другие механические элементы"
}
```

## API поставщиков

Для сущности `Supplier` реализован CRUD:

```text
GET    /suppliers?skip=0&limit=100
GET    /suppliers/{supplier_id}
POST   /suppliers
PUT    /suppliers/{supplier_id}
PATCH  /suppliers/{supplier_id}
DELETE /suppliers/{supplier_id}
```

Пример JSON для `POST /suppliers`:

```json
{
  "name": "ООО МеталлПром",
  "email": "sales@metallprom.ru",
  "phone": "+7 495 100-20-30",
  "address": "г. Москва, Промышленная ул., 12"
}
```

Пример JSON для `PUT /suppliers/{supplier_id}`:

```json
{
  "name": "АО ТехКомплект",
  "email": "info@techkomplekt.ru",
  "phone": "+7 812 200-30-40",
  "address": "г. Санкт-Петербург, Складская ул., 5"
}
```

Проверить все endpoint-ы можно через Swagger UI:

```text
http://127.0.0.1:8000/docs
```

## API складов

Для сущности `Warehouse` реализован CRUD:

```text
GET    /warehouses?skip=0&limit=100
GET    /warehouses/{warehouse_id}
POST   /warehouses
PUT    /warehouses/{warehouse_id}
PATCH  /warehouses/{warehouse_id}
DELETE /warehouses/{warehouse_id}
```

Пример JSON для `POST /warehouses`:

```json
{
  "name": "Основной склад",
  "address": "г. Москва, Заводская ул., 10",
  "responsible_person": "Иванов Иван Иванович"
}
```

Пример JSON для `PUT /warehouses/{warehouse_id}`:

```json
{
  "name": "Склад готовой продукции",
  "address": "г. Москва, Производственный проезд, 7",
  "responsible_person": "Петров Петр Петрович"
}
```

Проверить API складов можно через Swagger UI:

```text
http://127.0.0.1:8000/docs
```

## API деталей

Для основной сущности `Detail` реализован CRUD, фильтрация, поиск и изменение количества:

```text
GET    /details?skip=0&limit=100
GET    /details/{detail_id}
POST   /details
PUT    /details/{detail_id}
PATCH  /details/{detail_id}
DELETE /details/{detail_id}
GET    /details/low-stock?threshold=5
PATCH  /details/{detail_id}/quantity
```

Пример JSON для `POST /details`:

```json
{
  "name": "Болт М8",
  "article": "BOLT-M8-001",
  "material": "Сталь",
  "weight": 0.035,
  "price": 12.5,
  "quantity": 100,
  "category_id": 1,
  "supplier_id": 1,
  "warehouse_id": 1
}
```

Пример JSON для `PUT /details/{detail_id}`:

```json
{
  "name": "Болт М8 усиленный",
  "article": "BOLT-M8-002",
  "material": "Нержавеющая сталь",
  "weight": 0.04,
  "price": 15.75,
  "quantity": 80,
  "category_id": 1,
  "supplier_id": 1,
  "warehouse_id": 1
}
```

Пример JSON для `PATCH /details/{detail_id}`:

```json
{
  "price": 14.9,
  "quantity": 60,
  "warehouse_id": 2
}
```

Примеры фильтрации и поиска:

```text
GET /details?category_id=1
GET /details?supplier_id=1
GET /details?warehouse_id=1
GET /details?search=bolt
GET /details/low-stock?threshold=3
```

Пример JSON для `PATCH /details/{detail_id}/quantity`:

```json
{
  "quantity": 10
}
```

Все endpoint-ы деталей доступны в Swagger UI:

```text
http://127.0.0.1:8000/docs
```
