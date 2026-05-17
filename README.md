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
