import { isAxiosError } from "axios";
import { useCallback, useEffect, useState } from "react";
import type { FormEvent } from "react";

import {
  createSupplier,
  deleteSupplier,
  getSuppliers,
  updateSupplier,
} from "../api/suppliers";
import { useRole } from "../auth/useRole";
import type { Supplier, SupplierCreate } from "../types/supplier";

interface SupplierFormState {
  name: string;
  email: string;
  phone: string;
  address: string;
}

const emptyForm: SupplierFormState = {
  name: "",
  email: "",
  phone: "",
  address: "",
};

const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export default function SuppliersPage() {
  const { role, canCreate, canEdit, canDelete } = useRole();
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [form, setForm] = useState<SupplierFormState>(emptyForm);
  const [editingSupplier, setEditingSupplier] = useState<Supplier | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [deletingId, setDeletingId] = useState<number | null>(null);
  const [pageError, setPageError] = useState<string | null>(null);
  const [formError, setFormError] = useState<string | null>(null);

  const loadSuppliers = useCallback(async () => {
    setIsLoading(true);
    setPageError(null);

    try {
      const loadedSuppliers = await getSuppliers();
      setSuppliers(loadedSuppliers);
    } catch {
      setPageError(
        "Не удалось загрузить поставщиков. Проверьте, что backend запущен.",
      );
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadSuppliers();
  }, [loadSuppliers]);

  const resetForm = () => {
    setForm(emptyForm);
    setEditingSupplier(null);
    setFormError(null);
  };

  const validateForm = (): string | null => {
    const name = form.name.trim();
    const email = form.email.trim();
    const phone = form.phone.trim();
    const address = form.address.trim();

    if (!name) {
      return "Название поставщика обязательно.";
    }

    if (name.length < 2) {
      return "Название поставщика должно содержать минимум 2 символа.";
    }

    if (name.length > 150) {
      return "Название поставщика не должно превышать 150 символов.";
    }

    if (!email) {
      return "Email поставщика обязателен.";
    }

    if (!emailPattern.test(email)) {
      return "Введите корректный email поставщика.";
    }

    if (phone.length > 30) {
      return "Телефон поставщика не должен превышать 30 символов.";
    }

    if (address.length > 300) {
      return "Адрес поставщика не должен превышать 300 символов.";
    }

    return null;
  };

  const buildPayload = (): SupplierCreate => ({
    name: form.name.trim(),
    email: form.email.trim(),
    phone: form.phone.trim() || null,
    address: form.address.trim() || null,
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

      if (editingSupplier) {
        await updateSupplier(editingSupplier.id, payload);
      } else {
        await createSupplier(payload);
      }

      resetForm();
      await loadSuppliers();
    } catch (error) {
      setFormError(getMutationErrorMessage(error));
    } finally {
      setIsSaving(false);
    }
  };

  const handleEdit = (supplier: Supplier) => {
    if (!canEdit) {
      return;
    }

    setEditingSupplier(supplier);
    setForm({
      name: supplier.name,
      email: supplier.email,
      phone: supplier.phone ?? "",
      address: supplier.address ?? "",
    });
    setFormError(null);
  };

  const handleDelete = async (supplier: Supplier) => {
    if (!canDelete) {
      return;
    }

    const confirmed = window.confirm(
      `Удалить поставщика «${supplier.name}»?`,
    );

    if (!confirmed) {
      return;
    }

    setDeletingId(supplier.id);
    setPageError(null);

    try {
      await deleteSupplier(supplier.id);
      if (editingSupplier?.id === supplier.id) {
        resetForm();
      }
      await loadSuppliers();
    } catch (error) {
      setPageError(getMutationErrorMessage(error));
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <section className="page-section">
      <div className="page-heading">
        <p className="eyebrow">Контрагенты</p>
        <h1>Поставщики</h1>
        <p className="lead">
          Управление поставщиками деталей и контактными данными контрагентов.
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
                {editingSupplier ? "Редактирование поставщика" : "Новый поставщик"}
              </h2>
            </div>

            <label className="field">
              <span>Название</span>
              <input
                value={form.name}
                maxLength={150}
                placeholder="Например: ООО ТехКомплект"
                onChange={(event) =>
                  setForm((current) => ({
                    ...current,
                    name: event.target.value,
                  }))
                }
              />
            </label>

            <label className="field">
              <span>Email</span>
              <input
                value={form.email}
                maxLength={255}
                placeholder="info@example.ru"
                type="email"
                onChange={(event) =>
                  setForm((current) => ({
                    ...current,
                    email: event.target.value,
                  }))
                }
              />
            </label>

            <label className="field">
              <span>Телефон</span>
              <input
                value={form.phone}
                maxLength={30}
                placeholder="+7 495 100-20-30"
                onChange={(event) =>
                  setForm((current) => ({
                    ...current,
                    phone: event.target.value,
                  }))
                }
              />
            </label>

            <label className="field">
              <span>Адрес</span>
              <textarea
                value={form.address}
                maxLength={300}
                placeholder="Юридический или складской адрес"
                rows={4}
                onChange={(event) =>
                  setForm((current) => ({
                    ...current,
                    address: event.target.value,
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
                  : editingSupplier
                    ? "Сохранить"
                    : "Добавить"}
              </button>
              {editingSupplier && (
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
              <h2>Список поставщиков</h2>
            </div>
            <button
              className="button button-secondary"
              type="button"
              onClick={() => void loadSuppliers()}
              disabled={isLoading}
            >
              Обновить
            </button>
          </div>

          {pageError && <div className="alert alert-error">{pageError}</div>}

          {isLoading ? (
            <div className="state-box">Загрузка поставщиков...</div>
          ) : suppliers.length === 0 ? (
            <div className="state-box">Поставщики пока не добавлены.</div>
          ) : (
            <div className="table-wrap">
              <table className="data-table data-table-wide">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Название</th>
                    <th>Email</th>
                    <th>Телефон</th>
                    <th>Адрес</th>
                    <th>Дата создания</th>
                    {(canEdit || canDelete) && <th>Действия</th>}
                  </tr>
                </thead>
                <tbody>
                  {suppliers.map((supplier) => (
                    <tr key={supplier.id}>
                      <td>{supplier.id}</td>
                      <td>{supplier.name}</td>
                      <td>{supplier.email}</td>
                      <td>{supplier.phone || "—"}</td>
                      <td>{supplier.address || "—"}</td>
                      <td>{formatDate(supplier.created_at)}</td>
                      {(canEdit || canDelete) && (
                        <td>
                          <div className="row-actions">
                            {canEdit && (
                              <button
                                className="button button-secondary"
                                type="button"
                                onClick={() => handleEdit(supplier)}
                              >
                                Редактировать
                              </button>
                            )}
                            {canDelete && (
                              <button
                                className="button button-danger"
                                type="button"
                                disabled={deletingId === supplier.id}
                                onClick={() => void handleDelete(supplier)}
                              >
                                {deletingId === supplier.id
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

      if (!detail || detail.includes("email")) {
        return "Поставщик с таким email уже существует.";
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
