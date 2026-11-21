export interface Taxonomy {
  id: string;
  name: string;
  description: string;
  status: 'active' | 'inactive';
  entries: TaxonomyEntry[];
  createdAt: string;
}

export interface TaxonomyEntry {
  id: string;
  name: string;
  parentId?: string;
  children: string[];
  metadata: Record<string, unknown>;
}
