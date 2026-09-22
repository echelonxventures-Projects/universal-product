export interface SubscriptionBenefits {
  id: string;
  name: string;
  description: string;
  status: 'active' | 'inactive';
  createdAt: string;
}

export interface SubscriptionBenefit {
  id: string;
  benefitsId: string;
  name: string;
  type: 'discount' | 'free-shipping' | 'early-access' | 'bonus-points';
  value: string;
}
