export interface Referral {
  id: string;
  code: string;
  customerId: string;
  referredCustomers: string[];
  status: 'active' | 'inactive';
  createdAt: string;
}

export interface ReferralReward {
  id: string;
  referralId: string;
  customerId: string;
  type: 'referrer' | 'referred';
  value: number;
  currency: string;
  status: 'pending' | 'completed';
  createdAt: string;
}

export interface ReferralProgram {
  id: string;
  name: string;
  referrerReward: number;
  referredReward: number;
  currency: string;
  maxReferrals: number;
  status: 'active' | 'inactive';
}
