import { Offer } from './incentive';

export interface Cashback {
  id: string;
  offerId: string;
  type: 'percentage' | 'fixed';
  value: number;
  currency: string;
  minPurchase: number;
  maxCashback: number;
  eligibility: CashbackEligibility;
  payout: CashbackPayout;
  status: 'active' | 'inactive';
}

export interface CashbackEligibility {
  customerSegments: string[];
  categories: string[];
  products: string[];
}

export interface CashbackPayout {
  method: 'wallet' | 'bank' | 'statement';
  minimum: number;
  schedule: 'instant' | 'monthly' | 'quarterly';
}

export interface CashbackTransaction {
  id: string;
  orderId: string;
  customerId: string;
  amount: number;
  status: 'pending' | 'completed' | 'cancelled';
  createdAt: string;
  completedAt?: string;
}
