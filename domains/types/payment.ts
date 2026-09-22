import { Order } from './commerce';

export interface Payment {
  id: string;
  orderId: string;
  customerId: string;
  amount: number;
  currency: string;
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'refunded' | 'partial-refund';
  method: PaymentMethod;
  provider: string;
  providerTransactionId: string;
  metadata: Record<string, unknown>;
  createdAt: string;
  updatedAt: string;
  completedAt?: string;
}

export interface PaymentMethod {
  type: 'card' | 'ach' | 'wire' | 'crypto' | 'digital-wallet';
  provider: string;
  accountNumber?: string;
  routingNumber?: string;
  walletId?: string;
}

export interface PaymentIntent {
  id: string;
  orderId: string;
  amount: number;
  currency: string;
  status: 'created' | 'awaiting_confirmation' | 'succeeded' | 'failed' | 'canceled';
  clientSecret: string;
  createdAt: string;
  expiresAt: string;
}

export interface Refund {
  id: string;
  paymentId: string;
  orderId: string;
  amount: number;
  currency: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  reason: 'customer_request' | 'defective' | 'duplicate' | 'fraud' | 'other';
  createdAt: string;
  completedAt?: string;
}

export interface PaymentGateway {
  id: string;
  name: string;
  provider: string;
  status: 'active' | 'inactive';
  features: string[];
  configuration: Record<string, string>;
}
