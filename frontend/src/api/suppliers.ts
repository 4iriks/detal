import { apiClient } from "./client";
import type {
  Supplier,
  SupplierCreate,
  SupplierPatch,
  SupplierUpdate,
} from "../types/supplier";

export async function getSuppliers(): Promise<Supplier[]> {
  const response = await apiClient.get<Supplier[]>("/suppliers");
  return response.data;
}

export async function getSupplier(id: number): Promise<Supplier> {
  const response = await apiClient.get<Supplier>(`/suppliers/${id}`);
  return response.data;
}

export async function createSupplier(data: SupplierCreate): Promise<Supplier> {
  const response = await apiClient.post<Supplier>("/suppliers", data);
  return response.data;
}

export async function updateSupplier(
  id: number,
  data: SupplierUpdate,
): Promise<Supplier> {
  const response = await apiClient.put<Supplier>(`/suppliers/${id}`, data);
  return response.data;
}

export async function patchSupplier(
  id: number,
  data: SupplierPatch,
): Promise<Supplier> {
  const response = await apiClient.patch<Supplier>(`/suppliers/${id}`, data);
  return response.data;
}

export async function deleteSupplier(id: number): Promise<void> {
  await apiClient.delete(`/suppliers/${id}`);
}
