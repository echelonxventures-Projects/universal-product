export interface CompetitiveIntelligence {
  id: string;
  competitor: string;
  products: string[];
  prices: PricePoint[];
  status: string;
  lastUpdated: string;
}

export interface PricePoint {
  productId: string;
  price: number;
  timestamp: string;
}
