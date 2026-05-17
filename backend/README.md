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
    schemas/
    routers/
      health.py
    services/
  alembic/
  alembic.ini
  requirements.txt
  .env.example
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

Применить миграции:

```powershell
alembic upgrade head
```

Создать новую миграцию после добавления моделей:

```powershell
alembic revision --autogenerate -m "create initial tables"
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
