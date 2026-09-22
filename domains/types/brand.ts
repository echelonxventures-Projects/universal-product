export interface Brand {
  id: string;
  name: string;
  description: string;
  logoUrl?: string;
  website?: string;
  status: 'active' | 'inactive';
  products: string[];
  createdAt: string;
}

export interface BrandProfile {
  brandId: string;
  totalProducts: number;
  totalSales: number;
  averageRating: number;
  followers: number;
}
