# Учет деталей на складе предприятия

Курсовой backend для темы «Разработка клиент-серверного приложения для учета деталей на складе предприятия».

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

Заполнить базу демонстрационными данными:

```powershell
docker compose exec backend python -m app.seed
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

## Состав

- `docker-compose.yml` - запуск PostgreSQL и backend.
- `backend/` - FastAPI, SQLAlchemy, Alembic, CRUD API и SQL-объекты PostgreSQL.

## Заполнение базы демонстрационными данными

Seed-скрипт создает реалистичные данные для проверки API:

- 4 категории деталей;
- 3 поставщика;
- 3 склада;
- 10 деталей.

Скрипт идемпотентный: повторный запуск не создает дубликаты, потому что записи проверяются по уникальным полям.

Стандартный порядок запуска для демонстрации:

```powershell
docker compose up --build
docker compose exec backend alembic upgrade head
docker compose exec backend python -m app.seed
```

После этого API можно проверять в Swagger UI:

```text
http://localhost:8000/docs
```
