import { Cart, ShippingAddress, BillingAddress } from './cart';

export interface Checkout {
  id: string;
  cartId: string;
  customerId: string;
  status: 'active' | 'payment-processing' | 'completed' | 'failed' | 'abandoned';
  shippingAddress: ShippingAddress;
  billingAddress: BillingAddress;
  shippingMethod?: ShippingMethod;
  paymentMethod?: PaymentMethod;
  tax: number;
  shipping: number;
  total: number;
  metadata: Record<string, unknown>;
  createdAt: string;
  updatedAt: string;
  completedAt?: string;
}

export interface ShippingAddress {
  name: string;
  line1: string;
  line2?: string;
  city: string;
  state: string;
  postalCode: string;
  country: string;
  phone?: string;
  type: 'home' | 'work' | 'other';
}

export interface BillingAddress {
  name: string;
  line1: string;
  line2?: string;
  city: string;
  state: string;
  postalCode: string;
  country: string;
  taxId?: string;
}

export interface ShippingMethod {
  id: string;
  name: string;
  carrier: string;
  serviceLevel: 'standard' | 'expedited' | 'overnight' | 'same-day';
  price: number;
  currency: string;
  estimatedDays: number;
}

export interface PaymentMethod {
  id: string;
  type: 'card' | 'bank-transfer' | 'digital-wallet' | 'invoice' | 'cash-on-delivery';
  provider?: string;
  lastFourDigits?: string;
  expiryMonth?: number;
  expiryYear?: number;
  status: 'active' | 'expired';
}

export interface CheckoutValidationResult {
  valid: boolean;
  errors: CheckoutError[];
}

export interface CheckoutError {
  field: string;
  code: string;
  message: string;
}
