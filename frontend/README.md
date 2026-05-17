# Frontend: учет деталей на складе

Клиентская часть курсовой работы «Разработка клиент-серверного приложения для учета деталей на складе предприятия».

## Стек

- React
- TypeScript
- Vite
- React Router
- Axios

## Установка зависимостей

Команды выполняются из папки `frontend`.

```powershell
npm install
```

## Переменные окружения

Создайте `.env` на основе `.env.example`:

```powershell
Copy-Item .env.example .env
```

Переменная `VITE_API_URL` задает адрес backend API:

```env
VITE_API_URL=http://localhost:8000
```

## Запуск dev-сервера

```powershell
npm run dev
```

После запуска frontend доступен по адресу:

```text
http://localhost:5173
```

## Структура

```text
frontend/
  src/
    api/
      client.ts
    components/
      Layout.tsx
      Navigation.tsx
    pages/
      HomePage.tsx
      DetailsPage.tsx
      CategoriesPage.tsx
      SuppliersPage.tsx
      WarehousesPage.tsx
      NotFoundPage.tsx
    types/
      detail.ts
      category.ts
      supplier.ts
      warehouse.ts
    App.tsx
    main.tsx
    index.css
```
