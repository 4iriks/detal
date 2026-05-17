import { apiClient } from "./client";
import type {
  Detail,
  DetailCreate,
  DetailFilters,
  DetailPatch,
  DetailQuantityUpdate,
  DetailUpdate,
} from "../types/detail";

export async function getDetails(params?: DetailFilters): Promise<Detail[]> {
  const response = await apiClient.get<Detail[]>("/details", { params });
  return response.data;
}

export async function getDetail(id: number): Promise<Detail> {
  const response = await apiClient.get<Detail>(`/details/${id}`);
  return response.data;
}

export async function createDetail(data: DetailCreate): Promise<Detail> {
  const response = await apiClient.post<Detail>("/details", data);
  return response.data;
}

export async function updateDetail(
  id: number,
  data: DetailUpdate,
): Promise<Detail> {
  const response = await apiClient.put<Detail>(`/details/${id}`, data);
  return response.data;
}

export async function patchDetail(
  id: number,
  data: DetailPatch,
): Promise<Detail> {
  const response = await apiClient.patch<Detail>(`/details/${id}`, data);
  return response.data;
}

export async function deleteDetail(id: number): Promise<void> {
  await apiClient.delete(`/details/${id}`);
}

export async function getLowStockDetails(threshold = 5): Promise<Detail[]> {
  const response = await apiClient.get<Detail[]>("/details/low-stock", {
    params: { threshold },
  });
  return response.data;
}

export async function updateDetailQuantity(
  id: number,
  quantity: number,
): Promise<Detail> {
  const payload: DetailQuantityUpdate = { quantity };
  const response = await apiClient.patch<Detail>(
    `/details/${id}/quantity`,
    payload,
  );
  return response.data;
}
