import { Product } from './commerce';

export interface SKU {
  id: string;
  productId: string;
  skuCode: string;
  description: string;
  status: 'active' | 'inactive';
  createdAt: string;
}

export interface SKUMapping {
  skuId: string;
  externalId: string;
  system: string;
}
