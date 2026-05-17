export interface Supplier {
  id: number;
  name: string;
  email: string;
  phone: string | null;
  address: string | null;
  created_at: string;
  updated_at: string;
}

export interface SupplierCreate {
  name: string;
  email: string;
  phone?: string | null;
  address?: string | null;
}

export type SupplierUpdate = SupplierCreate;

export type SupplierPatch = Partial<SupplierCreate>;
