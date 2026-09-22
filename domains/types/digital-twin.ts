export interface DigitalTwin {
  id: string;
  type: string;
  source: string;
  status: 'active' | 'inactive';
  createdAt: string;
}

export interface CustomerTwin {
  id: string;
  customerId: string;
  profile: Record<string, unknown>;
  createdAt: string;
}

export interface MerchantTwin {
  id: string;
  merchantId: string;
  profile: Record<string, unknown>;
  createdAt: string;
}

export interface SellerTwin {
  id: string;
  sellerId: string;
  profile: Record<string, unknown>;
  createdAt: string;
}

export interface CatalogTwin {
  id: string;
  catalogId: string;
  profile: Record<string, unknown>;
  createdAt: string;
}

export interface OfferTwin {
  id: string;
  offerId: string;
  profile: Record<string, unknown>;
  createdAt: string;
}

export interface MarketplaceTwin {
  id: string;
  marketplaceId: string;
  profile: Record<string, unknown>;
  createdAt: string;
}

export interface SupplyChainTwin {
  id: string;
  type: string;
  profile: Record<string, unknown>;
  createdAt: string;
}

export interface EnterpriseTwin {
  id: string;
  enterpriseId: string;
  profile: Record<string, unknown>;
  createdAt: string;
}

export interface EconomicTwin {
  id: string;
  type: string;
  profile: Record<string, unknown>;
  createdAt: string;
}

export interface PlatformTwin {
  id: string;
  type: string;
  profile: Record<string, unknown>;
  createdAt: string;
}
