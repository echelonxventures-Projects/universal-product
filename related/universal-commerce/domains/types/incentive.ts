export interface Offer {
  id: string;
  code: string;
  name: string;
  description: string;
  type: 'discount' | 'cashback' | 'free_item' | 'buy_x_get_y';
  value: number;
  currency: string;
  eligibility: OfferEligibility;
  conditions: OfferCondition[];
  schedule: OfferSchedule;
  usage: OfferUsage;
  status: 'draft' | 'active' | 'paused' | 'expired';
  tenantId: string;
  createdAt: string;
}

export interface OfferEligibility {
  customerSegments: string[];
  minOrderValue?: number;
  maxRedemptions?: number;
  applicableProducts?: string[];
  excludedProducts?: string[];
}

export interface OfferCondition {
  type: 'spend' | 'quantity' | 'product' | 'category';
  operator: 'eq' | 'gte' | 'lte';
  value: unknown;
}

export interface OfferSchedule {
  startDate: string;
  endDate: string;
  daysOfWeek?: number[];
}

export interface OfferUsage {
  totalRedemptions: number;
  maxRedemptions?: number;
  perCustomerLimit?: number;
}

export interface Coupon {
  id: string;
  code: string;
  offerId: string;
  customerId?: string;
  status: 'unused' | 'redeemed' | 'expired' | 'cancelled';
  usedAt?: string;
  orderId?: string;
}

export interface LoyaltyAccount {
  id: string;
  customerId: string;
  points: number;
  tier: string;
  earnedPoints: number;
  redeemedPoints: number;
  status: 'active' | 'inactive';
}
