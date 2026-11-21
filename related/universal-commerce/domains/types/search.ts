export interface Search {
  query: string;
  results: SearchResult[];
  facets: Facet[];
  page: number;
  pageSize: number;
  total: number;
  took: number;
}

export interface SearchResult {
  id: string;
  type: 'product' | 'category' | 'brand';
  score: number;
  data: Record<string, unknown>;
}

export interface Facet {
  field: string;
  values: FacetValue[];
}

export interface FacetValue {
  value: string;
  count: number;
}

export interface SearchConfig {
  fields: string[];
  fuzzy: boolean;
  filters: Record<string, unknown>;
  sort: string;
}
