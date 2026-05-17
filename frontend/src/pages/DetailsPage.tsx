import { isAxiosError } from "axios";
import { useCallback, useEffect, useState } from "react";
import type { FormEvent } from "react";

import { getCategories } from "../api/categories";
import {
  createDetail,
  deleteDetail,
  getDetails,
  updateDetail,
} from "../api/details";
import { getSuppliers } from "../api/suppliers";
import { getWarehouses } from "../api/warehouses";
import type { Category } from "../types/category";
import type { Detail, DetailCreate } from "../types/detail";
import type { Supplier } from "../types/supplier";
import type { Warehouse } from "../types/warehouse";

interface DetailFormState {
  name: string;
  article: string;
  material: string;
  weight: string;
  price: string;
  quantity: string;
  category_id: string;
  supplier_id: string;
  warehouse_id: string;
}

const emptyForm: DetailFormState = {
  name: "",
  article: "",
  material: "",
  weight: "",
  price: "",
  quantity: "0",
  category_id: "",
  supplier_id: "",
  warehouse_id: "",
};

export default function DetailsPage() {
  const [details, setDetails] = useState<Detail[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [warehouses, setWarehouses] = useState<Warehouse[]>([]);
  const [form, setForm] = useState<DetailFormState>(emptyForm);
  const [editingDetail, setEditingDetail] = useState<Detail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [deletingId, setDeletingId] = useState<number | null>(null);
  const [pageError, setPageError] = useState<string | null>(null);
  const [formError, setFormError] = useState<string | null>(null);

  const loadReferences = useCallback(async () => {
    const [loadedCategories, loadedSuppliers, loadedWarehouses] =
      await Promise.all([getCategories(), getSuppliers(), getWarehouses()]);

    setCategories(loadedCategories);
    setSuppliers(loadedSuppliers);
    setWarehouses(loadedWarehouses);
  }, []);

  const loadDetails = useCallback(async () => {
    setIsLoading(true);
    setPageError(null);

    try {
      const loadedDetails = await getDetails();
      setDetails(loadedDetails);
    } catch {
      setPageError(
        "Не удалось загрузить детали. Проверьте, что backend запущен.",
      );
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    const loadPageData = async () => {
      setIsLoading(true);
      setPageError(null);

      try {
        await Promise.all([loadReferences(), loadDetails()]);
      } catch {
        setPageError(
          "Не удалось загрузить детали. Проверьте, что backend запущен.",
        );
        setIsLoading(false);
      }
    };

    void loadPageData();
  }, [loadDetails, loadReferences]);

  const resetForm = () => {
    setForm(emptyForm);
    setEditingDetail(null);
    setFormError(null);
  };

  const validateForm = (): string | null => {
    const name = form.name.trim();
    const article = form.article.trim();
    const material = form.material.trim();

    if (!name) {
      return "Название детали обязательно.";
    }

    if (name.length < 2) {
      return "Название детали должно содержать минимум 2 символа.";
    }

    if (name.length > 150) {
      return "Название детали не должно превышать 150 символов.";
    }

    if (!article) {
      return "Артикул обязателен.";
    }

    if (article.length < 2) {
      return "Артикул должен содержать минимум 2 символа.";
    }

    if (article.length > 100) {
      return "Артикул не должен превышать 100 символов.";
    }

    if (material.length > 100) {
      return "Материал не должен превышать 100 символов.";
    }

    if (form.price.trim() === "") {
      return "Цена обязательна.";
    }

    const price = Number(form.price);
    if (!Number.isFinite(price) || price < 0) {
      return "Цена должна быть числом больше или равным 0.";
    }

    if (form.weight.trim() !== "") {
      const weight = Number(form.weight);
      if (!Number.isFinite(weight) || weight < 0) {
        return "Вес должен быть числом больше или равным 0.";
      }
    }

    const quantity = Number(form.quantity);
    if (!Number.isInteger(quantity) || quantity < 0) {
      return "Количество должно быть целым числом больше или равным 0.";
    }

    if (!form.category_id) {
      return "Категория обязательна.";
    }

    return null;
  };

  const buildPayload = (): DetailCreate => ({
    name: form.name.trim(),
    article: form.article.trim(),
    material: form.material.trim() || null,
    weight: form.weight.trim() === "" ? null : Number(form.weight),
    price: Number(form.price),
    quantity: Number(form.quantity),
    category_id: Number(form.category_id),
    supplier_id: form.supplier_id ? Number(form.supplier_id) : null,
    warehouse_id: form.warehouse_id ? Number(form.warehouse_id) : null,
  });

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    const validationError = validateForm();
    if (validationError) {
      setFormError(validationError);
      return;
    }

    setIsSaving(true);
    setFormError(null);

    try {
      const payload = buildPayload();

      if (editingDetail) {
        await updateDetail(editingDetail.id, payload);
      } else {
        await createDetail(payload);
      }

      resetForm();
      await loadDetails();
    } catch (error) {
      setFormError(getMutationErrorMessage(error));
    } finally {
      setIsSaving(false);
    }
  };

  const handleEdit = (detail: Detail) => {
    setEditingDetail(detail);
    setForm({
      name: detail.name,
      article: detail.article,
      material: detail.material ?? "",
      weight: detail.weight === null ? "" : String(detail.weight),
      price: String(detail.price),
      quantity: String(detail.quantity),
      category_id: String(detail.category_id),
      supplier_id: detail.supplier_id === null ? "" : String(detail.supplier_id),
      warehouse_id:
        detail.warehouse_id === null ? "" : String(detail.warehouse_id),
    });
    setFormError(null);
  };

  const handleDelete = async (detail: Detail) => {
    const confirmed = window.confirm(`Удалить деталь «${detail.name}»?`);

    if (!confirmed) {
      return;
    }

    setDeletingId(detail.id);
    setPageError(null);

    try {
      await deleteDetail(detail.id);
      if (editingDetail?.id === detail.id) {
        resetForm();
      }
      await loadDetails();
    } catch (error) {
      setPageError(getMutationErrorMessage(error));
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <section className="page-section">
      <div className="page-heading">
        <p className="eyebrow">Номенклатура</p>
        <h1>Детали</h1>
        <p className="lead">
          Управление деталями, артикулами, ценами и складскими остатками.
        </p>
      </div>

      <div className="entity-grid">
        <form className="entity-form" onSubmit={handleSubmit}>
          <div>
            <h2>{editingDetail ? "Редактирование детали" : "Новая деталь"}</h2>
          </div>

          <label className="field">
            <span>Название</span>
            <input
              value={form.name}
              maxLength={150}
              placeholder="Например: Болт М8"
              onChange={(event) =>
                setForm((current) => ({ ...current, name: event.target.value }))
              }
            />
          </label>

          <label className="field">
            <span>Артикул</span>
            <input
              value={form.article}
              maxLength={100}
              placeholder="Например: BOLT-M8-001"
              onChange={(event) =>
                setForm((current) => ({
                  ...current,
                  article: event.target.value,
                }))
              }
            />
          </label>

          <label className="field">
            <span>Материал</span>
            <input
              value={form.material}
              maxLength={100}
              placeholder="Сталь, пластик, алюминий"
              onChange={(event) =>
                setForm((current) => ({
                  ...current,
                  material: event.target.value,
                }))
              }
            />
          </label>

          <label className="field">
            <span>Вес</span>
            <input
              value={form.weight}
              min="0"
              step="0.001"
              type="number"
              placeholder="0.25"
              onChange={(event) =>
                setForm((current) => ({
                  ...current,
                  weight: event.target.value,
                }))
              }
            />
          </label>

          <label className="field">
            <span>Цена</span>
            <input
              value={form.price}
              min="0"
              step="0.01"
              type="number"
              placeholder="120.50"
              onChange={(event) =>
                setForm((current) => ({ ...current, price: event.target.value }))
              }
            />
          </label>

          <label className="field">
            <span>Количество</span>
            <input
              value={form.quantity}
              min="0"
              step="1"
              type="number"
              onChange={(event) =>
                setForm((current) => ({
                  ...current,
                  quantity: event.target.value,
                }))
              }
            />
          </label>

          <label className="field">
            <span>Категория</span>
            <select
              value={form.category_id}
              onChange={(event) =>
                setForm((current) => ({
                  ...current,
                  category_id: event.target.value,
                }))
              }
            >
              <option value="">Выберите категорию</option>
              {categories.map((category) => (
                <option key={category.id} value={category.id}>
                  {category.name}
                </option>
              ))}
            </select>
          </label>

          <label className="field">
            <span>Поставщик</span>
            <select
              value={form.supplier_id}
              onChange={(event) =>
                setForm((current) => ({
                  ...current,
                  supplier_id: event.target.value,
                }))
              }
            >
              <option value="">Без поставщика</option>
              {suppliers.map((supplier) => (
                <option key={supplier.id} value={supplier.id}>
                  {supplier.name}
                </option>
              ))}
            </select>
          </label>

          <label className="field">
            <span>Склад</span>
            <select
              value={form.warehouse_id}
              onChange={(event) =>
                setForm((current) => ({
                  ...current,
                  warehouse_id: event.target.value,
                }))
              }
            >
              <option value="">Без склада</option>
              {warehouses.map((warehouse) => (
                <option key={warehouse.id} value={warehouse.id}>
                  {warehouse.name}
                </option>
              ))}
            </select>
          </label>

          {formError && <div className="alert alert-error">{formError}</div>}

          <div className="form-actions">
            <button className="button button-primary" type="submit" disabled={isSaving}>
              {isSaving
                ? "Сохранение..."
                : editingDetail
                  ? "Сохранить"
                  : "Добавить"}
            </button>
            {editingDetail && (
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

        <div className="entity-panel">
          <div className="panel-heading">
            <div>
              <h2>Список деталей</h2>
            </div>
            <button
              className="button button-secondary"
              type="button"
              onClick={() => void loadDetails()}
              disabled={isLoading}
            >
              Обновить
            </button>
          </div>

          {pageError && <div className="alert alert-error">{pageError}</div>}

          {isLoading ? (
            <div className="state-box">Загрузка деталей...</div>
          ) : details.length === 0 ? (
            <div className="state-box">Детали пока не добавлены.</div>
          ) : (
            <div className="table-wrap">
              <table className="data-table data-table-extra-wide">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Название</th>
                    <th>Артикул</th>
                    <th>Материал</th>
                    <th>Цена</th>
                    <th>Количество</th>
                    <th>Категория</th>
                    <th>Поставщик</th>
                    <th>Склад</th>
                    <th>Дата создания</th>
                    <th>Действия</th>
                  </tr>
                </thead>
                <tbody>
                  {details.map((detail) => (
                    <tr key={detail.id}>
                      <td>{detail.id}</td>
                      <td>{detail.name}</td>
                      <td>{detail.article}</td>
                      <td>{detail.material || "—"}</td>
                      <td>{formatNumber(detail.price)}</td>
                      <td>{detail.quantity}</td>
                      <td>{getCategoryName(detail, categories)}</td>
                      <td>{getSupplierName(detail, suppliers)}</td>
                      <td>{getWarehouseName(detail, warehouses)}</td>
                      <td>{formatDate(detail.created_at)}</td>
                      <td>
                        <div className="row-actions">
                          <button
                            className="button button-secondary"
                            type="button"
                            onClick={() => handleEdit(detail)}
                          >
                            Редактировать
                          </button>
                          <button
                            className="button button-danger"
                            type="button"
                            disabled={deletingId === detail.id}
                            onClick={() => void handleDelete(detail)}
                          >
                            {deletingId === detail.id ? "Удаление..." : "Удалить"}
                          </button>
                        </div>
                      </td>
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

function formatNumber(value: number | string | null): string {
  if (value === null) {
    return "—";
  }

  const parsedValue = Number(value);

  if (!Number.isFinite(parsedValue)) {
    return String(value);
  }

  return new Intl.NumberFormat("ru-RU", {
    maximumFractionDigits: 3,
  }).format(parsedValue);
}

function getCategoryName(detail: Detail, categories: Category[]): string {
  if (detail.category?.name) {
    return detail.category.name;
  }

  return categories.find((category) => category.id === detail.category_id)?.name ?? "—";
}

function getSupplierName(detail: Detail, suppliers: Supplier[]): string {
  if (detail.supplier?.name) {
    return detail.supplier.name;
  }

  if (detail.supplier_id === null) {
    return "—";
  }

  return suppliers.find((supplier) => supplier.id === detail.supplier_id)?.name ?? "—";
}

function getWarehouseName(detail: Detail, warehouses: Warehouse[]): string {
  if (detail.warehouse?.name) {
    return detail.warehouse.name;
  }

  if (detail.warehouse_id === null) {
    return "—";
  }

  return warehouses.find((warehouse) => warehouse.id === detail.warehouse_id)?.name ?? "—";
}

function getMutationErrorMessage(error: unknown): string {
  if (isAxiosError(error)) {
    if (error.response?.status === 409) {
      const detail = getBackendDetail(error);

      if (!detail || detail.includes("артикул")) {
        return "Деталь с таким артикулом уже существует.";
      }

      return detail;
    }

    const detail = getBackendDetail(error);

    if (detail && hasReferenceError(detail)) {
      return detail;
    }

    return detail ?? "Не удалось выполнить действие.";
  }

  return "Не удалось выполнить действие.";
}

function hasReferenceError(message: string): boolean {
  const normalizedMessage = message.toLowerCase();

  return (
    normalizedMessage.includes("категор") ||
    normalizedMessage.includes("поставщик") ||
    normalizedMessage.includes("склад")
  );
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
