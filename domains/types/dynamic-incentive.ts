export interface DynamicIncentive {
  id: string;
  name: string;
  algorithm: string;
  parameters: Record<string, unknown>;
  minDiscount: number;
  maxDiscount: number;
  status: 'active' | 'paused';
  createdAt: string;
}

export interface DynamicIncentiveRule {
  id: string;
  trigger: string;
  conditions: Record<string, unknown>;
  action: string;
  discountFactor: number;
}
