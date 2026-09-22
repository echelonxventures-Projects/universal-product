import { Product } from './commerce';

export interface Catalog {
  id: string;
  name: string;
  description: string;
  status: 'draft' | 'active' | 'archived';
  products: Product[];
  hierarchy: CatalogHierarchy[];
  tenantId: string;
  createdAt: string;
}

export interface CatalogHierarchy {
  id: string;
  name: string;
  parentId?: string;
  children: string[];
  sortOrder: number;
}

export interface CatalogProduct {
  catalogId: string;
  productId: string;
  position: number;
  featured: boolean;
  status: 'active' | 'hidden';
}

export interface CatalogVersion {
  id: string;
  catalogId: string;
  version: number;
  products: CatalogProduct[];
  published: boolean;
  publishedAt?: string;
  createdAt: string;
}

export interface CatalogFilter {
  type: 'category' | 'price' | 'brand' | 'attribute';
  name: string;
  options: FilterOption[];
  multiSelect: boolean;
}

export interface FilterOption {
  value: string;
  label: string;
  count?: number;
}
