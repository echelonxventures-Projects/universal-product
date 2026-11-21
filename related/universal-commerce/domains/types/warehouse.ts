import { Inventory, InventoryTransfer } from './inventory';

export interface Warehouse {
  id: string;
  name: string;
  address: Address;
  zones: Zone[];
  bins: Bin[];
  operatingHours: OperatingHours;
  capacity: Capacity;
  status: 'active' | 'inactive';
  tenantId: string;
}

export interface Zone {
  id: string;
  name: string;
  type: 'receiving' | 'storage' | 'picking' | 'packing' | 'shipping';
  temperature?: 'ambient' | 'refrigerated' | 'frozen';
}

export interface Bin {
  id: string;
  zoneId: string;
  location: string;
  capacity: number;
  occupied: number;
  status: 'available' | 'reserved' | 'full';
}

export interface OperatingHours {
  mon: Range;
  tue: Range;
  wed: Range;
  thu: Range;
  fri: Range;
  sat: Range;
  sun: Range;
}

export interface Range {
  open: string;
  close: string;
  closed: boolean;
}

export interface Capacity {
  totalBins: number;
  availableBins: number;
  totalVolume: number;
  usedVolume: number;
  utilization: number;
}

export interface WarehouseOperation {
  id: string;
  warehouseId: string;
  type: 'receiving' | 'putaway' | 'picking' | 'packing' | 'shipping';
  status: 'pending' | 'in-progress' | 'completed';
  items: { productId: string; quantity: number }[];
  createdAt: string;
  completedAt?: string;
}
