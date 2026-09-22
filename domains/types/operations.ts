export interface Operations {
  id: string;
  type: string;
  status: 'active' | 'inactive';
  createdAt: string;
}

export interface GlobalControlTower {
  id: string;
  name: string;
  status: 'active' | 'inactive';
  createdAt: string;
}

export interface TenantOperations {
  id: string;
  tenantId: string;
  status: 'active' | 'inactive';
  createdAt: string;
}

export interface MerchantOperations {
  id: string;
  merchantId: string;
  status: 'active' | 'inactive';
  createdAt: string;
}

export interface SellerOperations {
  id: string;
  sellerId: string;
  status: 'active' | 'inactive';
  createdAt: string;
}

export interface MarketplaceOperations {
  id: string;
  marketplaceId: string;
  status: 'active' | 'inactive';
  createdAt: string;
}

export interface OfferOperations {
  id: string;
  offerId: string;
  status: 'active' | 'inactive';
  createdAt: string;
}

export interface CampaignOperations {
  id: string;
  campaignId: string;
  status: 'active' | 'inactive';
  createdAt: string;
}

export interface SettlementOperations {
  id: string;
  type: string;
  status: 'active' | 'inactive';
  createdAt: string;
}

export interface BillingOperations {
  id: string;
  type: string;
  status: 'active' | 'inactive';
  createdAt: string;
}

export interface RevenueOperations {
  id: string;
  type: string;
  status: 'active' | 'inactive';
  createdAt: string;
}

export interface FraudOperations {
  id: string;
  type: string;
  status: 'active' | 'inactive';
  createdAt: string;
}

export interface RiskOperations {
  id: string;
  type: string;
  status: 'active' | 'inactive';
  createdAt: string;
}

export interface CapacityOperations {
  id: string;
  type: string;
  status: 'active' | 'inactive';
  createdAt: string;
}

export interface PlatformOperations {
  id: string;
  type: string;
  status: 'active' | 'inactive';
  createdAt: string;
}

export interface AIOperations {
  id: string;
  type: string;
  status: 'active' | 'inactive';
  createdAt: string;
}

export interface SLAOperations {
  id: string;
  type: string;
  status: 'active' | 'inactive';
  createdAt: string;
}

export interface BusinessOperations {
  id: string;
  type: string;
  status: 'active' | 'inactive';
  createdAt: string;
}
