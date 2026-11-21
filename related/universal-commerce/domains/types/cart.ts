import { OrderItem, Price } from './commerce';
import { Offer } from './incentive';

export interface Cart {
  id: string;
  customerId?: string;
  sessionId?: string;
  items: CartItem[];
  subtotal: number;
  tax: number;
  shipping: number;
  discounts: Discount[];
  total: number;
  currency: string;
  status: 'active' | 'abandoned' | 'converted';
  metadata: Record<string, unknown>;
  createdAt: string;
  updatedAt: string;
  expiresAt: string;
}

export interface CartItem {
  id: string;
  productId: string;
  variantId?: string;
  quantity: number;
  unitPrice: number;
  totalPrice: number;
  attributes: Record<string, string>;
  addedAt: string;
}

export interface Discount {
  id: string;
  type: 'coupon' | 'offer' | 'automatic' | 'promotional';
  code?: string;
  offerId?: string;
  amount: number;
  description: string;
}

export interface CartApplyDiscount {
  code: string;
  productId?: string;
  categoryId?: string;
  customerSegment?: string;
}

export interface CartValidateResult {
  valid: boolean;
  error?: string;
  appliedDiscount?: Discount;
}
