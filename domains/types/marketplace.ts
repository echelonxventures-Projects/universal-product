import { Offer, Order } from '../commerce';

export interface Marketplace {
  id: string;
  name: string;
  description: string;
  status: 'draft' | 'active' | 'inactive';
  regions: string[];
  currencies: string[];
  categories: string[];
  commission: number;
  paymentTerms: number;
  createdAt: string;
}

export interface MarketplaceProduct {
  id: string;
  marketplaceId: string;
  merchantId: string;
  productId: string;
  status: 'pending' | 'approved' | 'rejected' | 'active';
  price: number;
  currency: string;
  createdAt: string;
}

export interface MarketplaceOrder {
  id: string;
  orderId: string;
  marketplaceId: string;
  merchantId: string;
  status: 'active' | 'settled' | 'refunded';
  marketplaceFee: number;
  merchantAmount: number;
  createdAt: string;
  settledAt?: string;
}

export interface MarketplaceCommission {
  id: string;
  marketplaceId: string;
  merchantId: string;
  orderId: string;
  amount: number;
  status: 'pending' | 'settled';
  createdAt: string;
  settledAt?: string;
}
