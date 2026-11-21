export interface RetailMedia {
  id: string;
  name: string;
  status: 'active' | 'inactive';
  createdAt: string;
}

export interface SponsoredProduct {
  id: string;
  productId: string;
  campaignId: string;
  status: 'active' | 'paused';
  bid: number;
  currency: string;
  createdAt: string;
}

export interface SponsoredBrand {
  id: string;
  brandId: string;
  campaignId: string;
  status: 'active' | 'paused';
  bid: number;
  currency: string;
  createdAt: string;
}

export interface SponsoredCampaign {
  id: string;
  name: string;
  type: 'product' | 'brand' | 'display';
  status: 'active' | 'paused' | 'completed';
  budget: number;
  currency: string;
  startDate: string;
  endDate?: string;
  createdAt: string;
}
