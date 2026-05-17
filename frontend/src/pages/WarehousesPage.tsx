import { isAxiosError } from "axios";
import { useCallback, useEffect, useState } from "react";
import type { FormEvent } from "react";

import {
  createWarehouse,
  deleteWarehouse,
  getWarehouses,
  updateWarehouse,
} from "../api/warehouses";
import { useRole } from "../auth/useRole";
import type { Warehouse, WarehouseCreate } from "../types/warehouse";

interface WarehouseFormState {
  name: string;
  address: string;
  responsible_person: string;
}

const emptyForm: WarehouseFormState = {
  name: "",
  address: "",
  responsible_person: "",
};

export default function WarehousesPage() {
  const { role, canCreate, canEdit, canDelete } = useRole();
  const [warehouses, setWarehouses] = useState<Warehouse[]>([]);
  const [form, setForm] = useState<WarehouseFormState>(emptyForm);
  const [editingWarehouse, setEditingWarehouse] = useState<Warehouse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [deletingId, setDeletingId] = useState<number | null>(null);
  const [pageError, setPageError] = useState<string | null>(null);
  const [formError, setFormError] = useState<string | null>(null);

  const loadWarehouses = useCallback(async () => {
    setIsLoading(true);
    setPageError(null);

    try {
      const loadedWarehouses = await getWarehouses();
      setWarehouses(loadedWarehouses);
    } catch {
      setPageError(
        "Не удалось загрузить склады. Проверьте, что backend запущен.",
      );
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadWarehouses();
  }, [loadWarehouses]);

  const resetForm = () => {
    setForm(emptyForm);
    setEditingWarehouse(null);
    setFormError(null);
  };

  const validateForm = (): string | null => {
    const name = form.name.trim();
    const address = form.address.trim();
    const responsiblePerson = form.responsible_person.trim();

    if (!name) {
      return "Название склада обязательно.";
    }

    if (name.length < 2) {
      return "Название склада должно содержать минимум 2 символа.";
    }

    if (name.length > 150) {
      return "Название склада не должно превышать 150 символов.";
    }

    if (!address) {
      return "Адрес склада обязателен.";
    }

    if (address.length < 5) {
      return "Адрес склада должен содержать минимум 5 символов.";
    }

    if (address.length > 300) {
      return "Адрес склада не должен превышать 300 символов.";
    }

    if (responsiblePerson.length > 150) {
      return "Ответственное лицо не должно превышать 150 символов.";
    }

    return null;
  };

  const buildPayload = (): WarehouseCreate => ({
    name: form.name.trim(),
    address: form.address.trim(),
    responsible_person: form.responsible_person.trim() || null,
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

      if (editingWarehouse) {
        await updateWarehouse(editingWarehouse.id, payload);
      } else {
        await createWarehouse(payload);
      }

      resetForm();
      await loadWarehouses();
    } catch (error) {
      setFormError(getMutationErrorMessage(error));
    } finally {
      setIsSaving(false);
    }
  };

  const handleEdit = (warehouse: Warehouse) => {
    if (!canEdit) {
      return;
    }

    setEditingWarehouse(warehouse);
    setForm({
      name: warehouse.name,
      address: warehouse.address,
      responsible_person: warehouse.responsible_person ?? "",
    });
    setFormError(null);
  };

  const handleDelete = async (warehouse: Warehouse) => {
    if (!canDelete) {
      return;
    }

    const confirmed = window.confirm(`Удалить склад «${warehouse.name}»?`);

    if (!confirmed) {
      return;
    }

    setDeletingId(warehouse.id);
    setPageError(null);

    try {
      await deleteWarehouse(warehouse.id);
      if (editingWarehouse?.id === warehouse.id) {
        resetForm();
      }
      await loadWarehouses();
    } catch (error) {
      setPageError(getMutationErrorMessage(error));
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <section className="page-section">
      <div className="page-heading">
        <p className="eyebrow">Хранение</p>
        <h1>Склады</h1>
        <p className="lead">
          Управление складами, адресами хранения и ответственными лицами.
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
                {editingWarehouse ? "Редактирование склада" : "Новый склад"}
              </h2>
            </div>

            <label className="field">
              <span>Название</span>
              <input
                value={form.name}
                maxLength={150}
                placeholder="Например: Основной склад"
                onChange={(event) =>
                  setForm((current) => ({
                    ...current,
                    name: event.target.value,
                  }))
                }
              />
            </label>

            <label className="field">
              <span>Адрес</span>
              <textarea
                value={form.address}
                maxLength={300}
                placeholder="Адрес склада"
                rows={4}
                onChange={(event) =>
                  setForm((current) => ({
                    ...current,
                    address: event.target.value,
                  }))
                }
              />
            </label>

            <label className="field">
              <span>Ответственное лицо</span>
              <input
                value={form.responsible_person}
                maxLength={150}
                placeholder="Иванов Иван Иванович"
                onChange={(event) =>
                  setForm((current) => ({
                    ...current,
                    responsible_person: event.target.value,
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
                  : editingWarehouse
                    ? "Сохранить"
                    : "Добавить"}
              </button>
              {editingWarehouse && (
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
              <h2>Список складов</h2>
            </div>
            <button
              className="button button-secondary"
              type="button"
              onClick={() => void loadWarehouses()}
              disabled={isLoading}
            >
              Обновить
            </button>
          </div>

          {pageError && <div className="alert alert-error">{pageError}</div>}

          {isLoading ? (
            <div className="state-box">Загрузка складов...</div>
          ) : warehouses.length === 0 ? (
            <div className="state-box">Склады пока не добавлены.</div>
          ) : (
            <div className="table-wrap">
              <table className="data-table data-table-wide">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Название</th>
                    <th>Адрес</th>
                    <th>Ответственное лицо</th>
                    <th>Дата создания</th>
                    {(canEdit || canDelete) && <th>Действия</th>}
                  </tr>
                </thead>
                <tbody>
                  {warehouses.map((warehouse) => (
                    <tr key={warehouse.id}>
                      <td>{warehouse.id}</td>
                      <td>{warehouse.name}</td>
                      <td>{warehouse.address}</td>
                      <td>{warehouse.responsible_person || "—"}</td>
                      <td>{formatDate(warehouse.created_at)}</td>
                      {(canEdit || canDelete) && (
                        <td>
                          <div className="row-actions">
                            {canEdit && (
                              <button
                                className="button button-secondary"
                                type="button"
                                onClick={() => handleEdit(warehouse)}
                              >
                                Редактировать
                              </button>
                            )}
                            {canDelete && (
                              <button
                                className="button button-danger"
                                type="button"
                                disabled={deletingId === warehouse.id}
                                onClick={() => void handleDelete(warehouse)}
                              >
                                {deletingId === warehouse.id
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

      if (!detail || detail.includes("названием")) {
        return "Склад с таким названием уже существует.";
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
