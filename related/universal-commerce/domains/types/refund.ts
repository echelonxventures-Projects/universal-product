import { Order, Product } from './commerce';

export interface RefundRequest {
  id: string;
  orderId: string;
  itemId: string;
  customerId: string;
  amount: number;
  currency: string;
  reason: string;
  status: 'pending' | 'approved' | 'processing' | 'completed' | 'denied';
  createdAt: string;
  decisionAt?: string;
}

export interface Exchange {
  id: string;
  orderId: string;
  originalItems: ExchangeItem[];
  replacementItems: ExchangeItem[];
  reason: string;
  status: 'pending' | 'approved' | 'processing' | 'completed';
  priceDifference: number;
  shippingCost: number;
  createdAt: string;
  completedAt?: string;
}

export interface ExchangeItem {
  productId: string;
  variantId?: string;
  quantity: number;
  price: number;
}

export interface ReturnPolicy {
  id: string;
  name: string;
  window: number;
  windowUnit: 'days' | 'weeks' | 'months';
  restockFee: number;
  allowedConditions: string[];
  excludedCategories: string[];
  status: 'active' | 'inactive';
}

export interface RefundPolicy {
  id: string;
  name: string;
  types: string[];
  timeLimits: Record<string, number>;
  status: 'active' | 'inactive';
}
