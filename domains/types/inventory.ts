import { OrderItem } from './commerce';

export interface Inventory {
  id: string;
  productId: string;
  variantId?: string;
  locationId: string;
  quantity: number;
  available: number;
  reserved: number;
  incoming: number;
  reorderPoint: number;
  reorderQuantity: number;
  updatedAt: string;
}

export interface InventoryLocation {
  id: string;
  name: string;
  type: 'warehouse' | 'store' | 'drop-ship' | 'virtual';
  address: Address;
  coordinates?: { lat: number; lng: number };
}

export interface InventoryTransfer {
  id: string;
  sourceLocationId: string;
  destinationLocationId: string;
  items: { productId: string; variantId?: string; quantity: number }[];
  status: 'pending' | 'transit' | 'completed' | 'cancelled';
  scheduledAt: string;
  completedAt?: string;
}

export interface InventoryReservation {
  id: string;
  orderId: string;
  items: { productId: string; variantId?: string; quantity: number }[];
  status: 'pending' | 'confirmed' | 'released' | 'converted';
  expiresAt: string;
}

export interface StockAlert {
  id: string;
  productId: string;
  locationId: string;
  type: 'low-stock' | 'out-of-stock' | 'overstock' | 'expiry';
  threshold: number;
  createdAt: string;
  acknowledged: boolean;
}

export interface Availability {
  productId: string;
  variantId?: string;
  available: boolean;
  availableQuantity: number;
  availableFrom: string;
  availableUntil?: string;
  deliveryEstimate?: { minDays: number; maxDays: number };
}
