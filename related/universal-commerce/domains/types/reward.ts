export interface Reward {
  id: string;
  name: string;
  description: string;
  points: number;
  cost: number;
  currency: string;
  stock: number;
  image?: string;
  status: 'available' | 'limited' | 'discontinued';
  createdAt: string;
}

export interface RewardCatalog {
  id: string;
  name: string;
  status: 'active' | 'inactive';
  rewards: string[];
}

export interface RewardRedemption {
  id: string;
  rewardId: string;
  customerId: string;
  orderId?: string;
  points: number;
  status: 'pending' | 'fulfilled' | 'cancelled';
  createdAt: string;
  fulfilledAt?: string;
}
