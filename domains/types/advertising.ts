export interface Advertising {
  id: string;
  type: 'display' | 'search' | 'sponsored' | 'native';
  status: 'active' | 'paused' | 'completed';
  budget: number;
  currency: string;
  startDate: string;
  endDate?: string;
  createdAt: string;
}

export interface AdCreative {
  id: string;
  adId: string;
  type: 'image' | 'video' | 'text';
  url: string;
  altText?: string;
}

export interface AdTargeting {
  audiences: string[];
  products: string[];
  keywords: string[];
  locations: string[];
}
