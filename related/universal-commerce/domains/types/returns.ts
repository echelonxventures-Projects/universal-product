import { Order } from './commerce';

export interface Return {
  id: string;
  orderId: string;
  customerId: string;
  items: ReturnItem[];
  reason: string;
  reasonCode: string;
  status: 'pending' | 'approved' | 'in-transit' | 'received' | 'processed' | 'cancelled';
  rmaNumber: string;
  shippingLabel?: string;
  refundAmount: number;
  restockFee: number;
  createdAt: string;
  updatedAt: string;
  completedAt?: string;
}

export interface ReturnItem {
  productId: string;
  variantId?: string;
  quantity: number;
  reason: string;
  condition: 'unused' | 'opened' | 'damaged' | 'defective';
  refundAmount: number;
  restockFee: number;
}

export interface ReturnAuthorization {
  id: string;
  orderId: string;
  status: 'pending' | 'approved' | 'denied';
  allowedItems: ReturnItem[];
  deniedItems: ReturnItem[];
  createdAt: string;
  decisionAt?: string;
  decision: string;
}

export interface Restock {
  id: string;
  warehouseId: string;
  items: { productId: string; quantity: number; location: string }[];
  status: 'pending' | 'completed';
  createdAt: string;
  completedAt?: string;
}
