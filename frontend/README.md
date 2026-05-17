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

Для работы страницы категорий должен быть запущен backend:

```text
http://localhost:8000
```

## Страница категорий

Страница доступна по адресу:

```text
http://localhost:5173/categories
```

На странице реализованы:

- загрузка списка категорий из backend API;
- отображение таблицы категорий;
- добавление категории;
- редактирование категории;
- удаление категории с подтверждением;
- сообщения загрузки, пустого списка и ошибок.

## Страница поставщиков

Страница доступна по адресу:

```text
http://localhost:5173/suppliers
```

На странице реализованы:

- загрузка списка поставщиков из backend API;
- отображение таблицы поставщиков;
- добавление поставщика;
- редактирование поставщика;
- удаление поставщика с подтверждением;
- сообщения загрузки, пустого списка и ошибок.

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
