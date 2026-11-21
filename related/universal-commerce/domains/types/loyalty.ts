export interface LoyaltyAccount {
  id: string;
  customerId: string;
  points: number;
  tier: string;
  earnedPoints: number;
  redeemedPoints: number;
  status: 'active' | 'inactive' | 'suspended';
  createdAt: string;
  updatedAt: string;
}

export interface LoyaltyTier {
  id: string;
  name: string;
  minPoints: number;
  benefits: string[];
  color?: string;
}

export interface LoyaltyTransaction {
  id: string;
  accountId: string;
  type: 'earned' | 'redeemed' | 'expired' | 'adjusted';
  points: number;
  referenceId: string;
  createdAt: string;
}

export interface LoyaltyRule {
  id: string;
  name: string;
  trigger: string;
  points: number;
  conditions: Record<string, unknown>;
  status: 'active' | 'inactive';
}
