export interface UCDID {
  id: string;
  domain: string;
  version: string;
  tenantId: string;
}

export interface Entity extends UCDID {
  createdAt: string;
  updatedAt: string;
  status: 'active' | 'inactive' | 'archived';
}

export interface CatalogEntity extends Entity {
  catalogId: string;
  hierarchyPath: string[];
}

export interface PricingEntity extends Entity {
  currency: string;
  validFrom: string;
  validTo: string;
}

export type CommerceEntity = 
  | ProductEntity
  | OrderEntity
  | CustomerEntity
  | IncentiveEntity;
