export interface Warehouse {
  id: number;
  name: string;
  address: string;
  responsible_person: string | null;
  created_at: string;
  updated_at: string;
}

export interface WarehouseCreate {
  name: string;
  address: string;
  responsible_person?: string | null;
}

export type WarehouseUpdate = WarehouseCreate;

export type WarehousePatch = Partial<WarehouseCreate>;
