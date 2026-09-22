export interface Partner {
  id: string;
  name: string;
  type: 'affiliate' | 'distributor' | 'reseller' | 'agent';
  status: 'active' | 'inactive';
  commissionRate: number;
  contactEmail: string;
  metadata: Record<string, unknown>;
  createdAt: string;
}

export interface PartnerCommission {
  id: string;
  partnerId: string;
  orderId: string;
  amount: number;
  status: 'pending' | 'settled';
  createdAt: string;
}
