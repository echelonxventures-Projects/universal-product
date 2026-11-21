export interface Creator {
  id: string;
  name: string;
  email: string;
  platform: string;
  audience: number;
  status: 'active' | 'inactive';
  createdAt: string;
}

export interface CreatorCampaign {
  id: string;
  creatorId: string;
  name: string;
  products: string[];
  status: 'active' | 'completed';
  createdAt: string;
}

export interface CreatorCommission {
  id: string;
  creatorId: string;
  orderId: string;
  amount: number;
  status: 'pending' | 'paid';
  createdAt: string;
}
