export interface Membership {
  id: string;
  customerId: string;
  plan: string;
  status: 'active' | 'expired' | 'cancelled';
  startedAt: string;
  expiresAt: string;
  autoRenew: boolean;
  createdAt: string;
}

export interface MembershipPlan {
  id: string;
  name: string;
  description: string;
  price: number;
  currency: string;
  duration: number;
  durationUnit: 'months' | 'years';
  benefits: string[];
  status: 'active' | 'inactive';
}

export interface MembershipBenefit {
  id: string;
  name: string;
  description: string;
  value: string;
}
