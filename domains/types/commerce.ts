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
  effectiveFrom: string;
  effectiveTo: string;
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
  shippingAddress: Address;
  billingAddress: Address;
  paymentId?: string;
  fulfillmentId?: string;
  tenantId: string;
  createdAt: string;
  updatedAt: string;
}

export interface OrderItem {
  productId: string;
  variantId?: string;
  quantity: number;
  unitPrice: number;
  totalPrice: number;
}

export type OrderStatus = 
  | 'pending' 
  | 'confirmed' 
  | 'processing' 
  | 'shipped' 
  | 'delivered' 
  | 'cancelled' 
  | 'returned';
