import type { Category } from "./category";
import type { Supplier } from "./supplier";
import type { Warehouse } from "./warehouse";

export type NumericValue = number | string;

export interface Detail {
  id: number;
  name: string;
  article: string;
  material: string | null;
  weight: NumericValue | null;
  price: NumericValue;
  quantity: number;
  category_id: number;
  supplier_id: number | null;
  warehouse_id: number | null;
  created_at: string;
  updated_at: string;
}

export interface DetailFull extends Detail {
  category: Category;
  supplier: Supplier | null;
  warehouse: Warehouse | null;
}

export interface DetailCreate {
  name: string;
  article: string;
  material: string | null;
  weight: NumericValue | null;
  price: NumericValue;
  quantity: number;
  category_id: number;
  supplier_id: number | null;
  warehouse_id: number | null;
}

export type DetailUpdate = DetailCreate;

export type DetailPatch = Partial<DetailCreate>;

export interface DetailQuantityUpdate {
  quantity: number;
}

export interface DetailFilters {
  skip?: number;
  limit?: number;
  category_id?: number;
  supplier_id?: number;
  warehouse_id?: number;
  search?: string;
}
