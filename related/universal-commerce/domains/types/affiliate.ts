export interface Affiliate {
  id: string;
  affiliateId: string;
  code: string;
  status: 'active' | 'inactive';
  commissionRate: number;
  createdAt: string;
}

export interface AffiliateClick {
  id: string;
  affiliateId: string;
  customerId: string;
  source: string;
  createdAt: string;
}

export interface AffiliateSale {
  id: string;
  affiliateId: string;
  orderId: string;
  amount: number;
  commission: number;
  status: 'pending' | 'completed' | 'cancelled';
  createdAt: string;
}

export interface AffiliateDashboard {
  affiliateId: string;
  totalClicks: number;
  totalSales: number;
  totalCommission: number;
  pendingCommission: number;
}
