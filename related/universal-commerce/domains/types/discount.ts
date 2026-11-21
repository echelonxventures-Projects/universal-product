import { Offer } from './incentive';

export interface Discount {
  id: string;
  offerId: string;
  type: 'percentage' | 'fixed' | 'free-shipping' | 'bundle';
  value: number;
  currency?: string;
  maxDiscount: number;
  minPurchase: number;
  applicableProducts: string[];
  excludedProducts: string[];
  applicableCategories: string[];
  status: 'active' | 'inactive';
}

export interface DiscountStack {
  id: string;
  discounts: string[];
  order: string[];
  allowStacking: boolean;
}
