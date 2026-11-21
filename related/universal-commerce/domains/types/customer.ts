import { Order } from './commerce';

export interface Customer {
  id: string;
  email: string;
  phone?: string;
  firstName?: string;
  lastName?: string;
  displayName?: string;
  status: 'active' | 'inactive' | 'blocked';
  segments: string[];
  tags: string[];
  metadata: Record<string, unknown>;
  addresses: Address[];
  defaultShippingAddress?: string;
  defaultBillingAddress?: string;
  createdAt: string;
  updatedAt: string;
}

export interface CustomerProfile {
  customerId: string;
  lifetimeValue: number;
  totalOrders: number;
  averageOrderValue: number;
  favoriteProducts: string[];
  favoriteCategories: string[];
  preferredPaymentMethod: string;
  preferredShippingMethod: string;
  lastOrderAt: string;
}

export interface CustomerPreferences {
  customerId: string;
  newsletter: boolean;
  promotions: boolean;
  sms: boolean;
  language: string;
  currency: string;
  timezone: string;
}

export interface CustomerActivity {
  customerId: string;
  events: CustomerEvent[];
  lastActivityAt: string;
}

export interface CustomerEvent {
  type: 'view' | 'add-to-cart' | 'purchase' | 'return' | 'review';
  productId?: string;
  timestamp: string;
  metadata: Record<string, unknown>;
}
