export interface Federation {
  id: string;
  type: string;
  status: 'active' | 'inactive';
  createdAt: string;
}

export interface OrganizationFederation {
  id: string;
  organizationId: string;
  status: 'active' | 'inactive';
  createdAt: string;
}

export interface MarketplaceFederation {
  id: string;
  marketplaceId: string;
  status: 'active' | 'inactive';
  createdAt: string;
}

export interface CountryFederation {
  id: string;
  country: string;
  status: 'active' | 'inactive';
  createdAt: string;
}

export interface RegionalFederation {
  id: string;
  region: string;
  status: 'active' | 'inactive';
  createdAt: string;
}

export interface PlanetaryFederation {
  id: string;
  status: 'active' | 'inactive';
  createdAt: string;
}

export interface InterplanetaryFederation {
  id: string;
  status: 'active' | 'inactive';
  createdAt: string;
}

export interface CivilizationalFederation {
  id: string;
  status: 'active' | 'inactive';
  createdAt: string;
}
