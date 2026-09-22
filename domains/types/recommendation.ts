export interface Recommendation {
  id: string;
  type: 'personalized' | 'trending' | 'related' | 'similar' | 'recently-viewed';
  customerId?: string;
  context: Record<string, unknown>;
  items: RecommendationItem[];
}

export interface RecommendationItem {
  productId: string;
  score: number;
  reason?: string;
}

export interface RecommendationAlgorithm {
  id: string;
  name: string;
  status: 'active' | 'inactive';
  parameters: Record<string, unknown>;
}
