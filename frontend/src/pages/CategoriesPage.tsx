import { isAxiosError } from "axios";
import { useCallback, useEffect, useState } from "react";
import type { FormEvent } from "react";

import {
  createCategory,
  deleteCategory,
  getCategories,
  updateCategory,
} from "../api/categories";
import { useRole } from "../auth/useRole";
import type { Category, CategoryCreate } from "../types/category";

interface CategoryFormState {
  name: string;
  description: string;
}

const emptyForm: CategoryFormState = {
  name: "",
  description: "",
};

export default function CategoriesPage() {
  const { role, canCreate, canEdit, canDelete } = useRole();
  const [categories, setCategories] = useState<Category[]>([]);
  const [form, setForm] = useState<CategoryFormState>(emptyForm);
  const [editingCategory, setEditingCategory] = useState<Category | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [deletingId, setDeletingId] = useState<number | null>(null);
  const [pageError, setPageError] = useState<string | null>(null);
  const [formError, setFormError] = useState<string | null>(null);

  const loadCategories = useCallback(async () => {
    setIsLoading(true);
    setPageError(null);

    try {
      const loadedCategories = await getCategories();
      setCategories(loadedCategories);
    } catch {
      setPageError(
        "Не удалось загрузить категории. Проверьте, что backend запущен.",
      );
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadCategories();
  }, [loadCategories]);

  const resetForm = () => {
    setForm(emptyForm);
    setEditingCategory(null);
    setFormError(null);
  };

  const validateForm = (): string | null => {
    const name = form.name.trim();
    const description = form.description.trim();

    if (!name) {
      return "Название категории обязательно.";
    }

    if (name.length < 2) {
      return "Название категории должно содержать минимум 2 символа.";
    }

    if (description.length > 500) {
      return "Описание категории не должно превышать 500 символов.";
    }

    return null;
  };

  const buildPayload = (): CategoryCreate => ({
    name: form.name.trim(),
    description: form.description.trim() || null,
  });

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (!canCreate && !canEdit) {
      return;
    }

    const validationError = validateForm();
    if (validationError) {
      setFormError(validationError);
      return;
    }

    setIsSaving(true);
    setFormError(null);

    try {
      const payload = buildPayload();

      if (editingCategory) {
        await updateCategory(editingCategory.id, payload);
      } else {
        await createCategory(payload);
      }

      resetForm();
      await loadCategories();
    } catch (error) {
      setFormError(getMutationErrorMessage(error));
    } finally {
      setIsSaving(false);
    }
  };

  const handleEdit = (category: Category) => {
    if (!canEdit) {
      return;
    }

    setEditingCategory(category);
    setForm({
      name: category.name,
      description: category.description ?? "",
    });
    setFormError(null);
  };

  const handleDelete = async (category: Category) => {
    if (!canDelete) {
      return;
    }

    const confirmed = window.confirm(
      `Удалить категорию «${category.name}»?`,
    );

    if (!confirmed) {
      return;
    }

    setDeletingId(category.id);
    setPageError(null);

    try {
      await deleteCategory(category.id);
      if (editingCategory?.id === category.id) {
        resetForm();
      }
      await loadCategories();
    } catch (error) {
      setPageError(getMutationErrorMessage(error));
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <section className="page-section">
      <div className="page-heading">
        <p className="eyebrow">Справочник</p>
        <h1>Категории</h1>
        <p className="lead">
          Управление категориями деталей: добавление, изменение и удаление
          справочных записей.
        </p>
        <div className="role-info">
          Текущая роль: <strong>{role}</strong>
        </div>
      </div>

      <div className={canCreate ? "entity-grid" : "entity-grid entity-grid-single"}>
        {canCreate && (
          <form className="entity-form" onSubmit={handleSubmit}>
            <div>
              <h2>
                {editingCategory ? "Редактирование категории" : "Новая категория"}
              </h2>
            </div>

            <label className="field">
              <span>Название</span>
              <input
                value={form.name}
                maxLength={100}
                placeholder="Например: Крепеж"
                onChange={(event) =>
                  setForm((current) => ({
                    ...current,
                    name: event.target.value,
                  }))
                }
              />
            </label>

            <label className="field">
              <span>Описание</span>
              <textarea
                value={form.description}
                maxLength={500}
                placeholder="Краткое описание категории"
                rows={5}
                onChange={(event) =>
                  setForm((current) => ({
                    ...current,
                    description: event.target.value,
                  }))
                }
              />
            </label>

            {formError && <div className="alert alert-error">{formError}</div>}

            <div className="form-actions">
              <button
                className="button button-primary"
                type="submit"
                disabled={isSaving}
              >
                {isSaving
                  ? "Сохранение..."
                  : editingCategory
                    ? "Сохранить"
                    : "Добавить"}
              </button>
              {editingCategory && (
                <button
                  className="button button-secondary"
                  type="button"
                  onClick={resetForm}
                >
                  Отмена
                </button>
              )}
            </div>
          </form>
        )}

        <div className="entity-panel">
          <div className="panel-heading">
            <div>
              <h2>Список категорий</h2>
            </div>
            <button
              className="button button-secondary"
              type="button"
              onClick={() => void loadCategories()}
              disabled={isLoading}
            >
              Обновить
            </button>
          </div>

          {pageError && <div className="alert alert-error">{pageError}</div>}

          {isLoading ? (
            <div className="state-box">Загрузка категорий...</div>
          ) : categories.length === 0 ? (
            <div className="state-box">Категории пока не добавлены.</div>
          ) : (
            <div className="table-wrap">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Название</th>
                    <th>Описание</th>
                    <th>Дата создания</th>
                    {(canEdit || canDelete) && <th>Действия</th>}
                  </tr>
                </thead>
                <tbody>
                  {categories.map((category) => (
                    <tr key={category.id}>
                      <td>{category.id}</td>
                      <td>{category.name}</td>
                      <td>{category.description || "—"}</td>
                      <td>{formatDate(category.created_at)}</td>
                      {(canEdit || canDelete) && (
                        <td>
                          <div className="row-actions">
                            {canEdit && (
                              <button
                                className="button button-secondary"
                                type="button"
                                onClick={() => handleEdit(category)}
                              >
                                Редактировать
                              </button>
                            )}
                            {canDelete && (
                              <button
                                className="button button-danger"
                                type="button"
                                disabled={deletingId === category.id}
                                onClick={() => void handleDelete(category)}
                              >
                                {deletingId === category.id
                                  ? "Удаление..."
                                  : "Удалить"}
                              </button>
                            )}
                          </div>
                        </td>
                      )}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}

function formatDate(value: string): string {
  return new Intl.DateTimeFormat("ru-RU", {
    dateStyle: "short",
    timeStyle: "short",
  }).format(new Date(value));
}

function getMutationErrorMessage(error: unknown): string {
  if (isAxiosError(error)) {
    if (error.response?.status === 409) {
      const detail = getBackendDetail(error);

      if (!detail || detail.includes("таким названием")) {
        return "Категория с таким названием уже существует.";
      }

      return detail;
    }

    return getBackendDetail(error) ?? "Не удалось выполнить действие.";
  }

  return "Не удалось выполнить действие.";
}

function getBackendDetail(error: unknown): string | null {
  if (!isAxiosError(error)) {
    return null;
  }

  const data = error.response?.data;

  if (
    data &&
    typeof data === "object" &&
    "detail" in data &&
    typeof data.detail === "string"
  ) {
    return data.detail;
  }

  return null;
}
