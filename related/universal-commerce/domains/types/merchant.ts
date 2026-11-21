import { Order, Product } from '../commerce';

export interface Merchant {
  id: string;
  name: string;
  legalName: string;
  email: string;
  phone?: string;
  status: 'pending' | 'active' | 'suspended';
  plan: string;
  commissionRate: number;
  taxId?: string;
  metadata: Record<string, unknown>;
  createdAt: string;
  updatedAt: string;
}

export interface MerchantProfile {
  merchantId: string;
  totalSales: number;
  totalOrders: number;
  averageOrderValue: number;
  productsCount: number;
  ratings: { average: number; count: number };
  lastOrderAt: string;
}

export interface MerchantPayout {
  id: string;
  merchantId: string;
  amount: number;
  currency: string;
  status: 'pending' | 'processing' | 'completed';
  periodStart: string;
  periodEnd: string;
  createdAt: string;
  completedAt?: string;
}
