import { apiClient } from "./client";
import type {
  Warehouse,
  WarehouseCreate,
  WarehousePatch,
  WarehouseUpdate,
} from "../types/warehouse";

export async function getWarehouses(): Promise<Warehouse[]> {
  const response = await apiClient.get<Warehouse[]>("/warehouses");
  return response.data;
}

export async function getWarehouse(id: number): Promise<Warehouse> {
  const response = await apiClient.get<Warehouse>(`/warehouses/${id}`);
  return response.data;
}

export async function createWarehouse(data: WarehouseCreate): Promise<Warehouse> {
  const response = await apiClient.post<Warehouse>("/warehouses", data);
  return response.data;
}

export async function updateWarehouse(
  id: number,
  data: WarehouseUpdate,
): Promise<Warehouse> {
  const response = await apiClient.put<Warehouse>(`/warehouses/${id}`, data);
  return response.data;
}

export async function patchWarehouse(
  id: number,
  data: WarehousePatch,
): Promise<Warehouse> {
  const response = await apiClient.patch<Warehouse>(`/warehouses/${id}`, data);
  return response.data;
}

export async function deleteWarehouse(id: number): Promise<void> {
  await apiClient.delete(`/warehouses/${id}`);
}
