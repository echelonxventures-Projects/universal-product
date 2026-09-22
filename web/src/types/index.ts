export interface Product {
  id: string;
  sku: string;
  name: string;
  description: string;
  categoryIds: string[];
  attributes: Record<string, unknown>;
  variants: ProductVariant[];
  status: 'draft' | 'active' | 'archived';
  tenantId: string;
  createdAt: string;
}

export interface ProductVariant {
  id: string;
  productId: string;
  sku: string;
  attributes: Record<string, string>;
  prices: Price[];
}

export interface Price {
  currency: string;
  amount: number;
}

export interface Order {
  id: string;
  orderNumber: string;
  customerId: string;
  status: OrderStatus;
  items: OrderItem[];
  subtotal: number;
  tax: number;
  discount: number;
  total: number;
  tenantId: string;
  createdAt: string;
}

export interface OrderItem {
  productId: string;
  quantity: number;
  unitPrice: number;
  totalPrice: number;
}

export type OrderStatus = 'pending' | 'confirmed' | 'processing' | 'shipped' | 'delivered' | 'cancelled';

export interface Offer {
  id: string;
  code: string;
  name: string;
  description: string;
  type: 'discount' | 'cashback' | 'free_item';
  value: number;
  currency: string;
  status: 'draft' | 'active' | 'paused' | 'expired';
  tenantId: string;
}

export interface Coupon {
  id: string;
  code: string;
  offerId: string;
  status: 'unused' | 'redeemed' | 'expired';
}

export interface Tenant {
  id: string;
  name: string;
  status: 'active' | 'inactive';
}
