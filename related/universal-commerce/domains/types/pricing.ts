import { Price } from './commerce';

export interface PricingRule {
  id: string;
  name: string;
  description: string;
  type: 'flat' | 'percentage' | 'tiered' | 'formula';
  value: number;
  formula?: string;
  conditions: PricingCondition[];
  priority: number;
  status: 'draft' | 'active' | 'inactive';
  tenantId: string;
}

export interface PricingCondition {
  type: 'quantity' | 'customerSegment' | 'channel' | 'region' | 'time';
  operator: 'eq' | 'gte' | 'lte' | 'between';
  value: unknown;
}

export interface PriceList {
  id: string;
  name: string;
  currency: string;
  prices: PriceEntry[];
  validFrom: string;
  validTo: string;
  tenantId: string;
}

export interface PriceEntry {
  productId: string;
  variantId?: string;
  price: Price;
  cost?: Price;
  margin?: number;
}

export interface DynamicPricing {
  id: string;
  productId: string;
  algorithm: 'demand' | 'competition' | 'elasticity' | 'machine-learning';
  parameters: Record<string, unknown>;
  minPrice: number;
  maxPrice: number;
  status: 'active' | 'paused';
}
