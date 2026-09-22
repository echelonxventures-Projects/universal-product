export interface AudienceMonetization {
  id: string;
  audienceId: string;
  revenue: number;
  currency: string;
  createdAt: string;
}

export interface PublisherNetwork {
  id: string;
  name: string;
  status: 'active' | 'inactive';
  createdAt: string;
}

export interface AdvertiserPlatform {
  id: string;
  name: string;
  status: 'active' | 'inactive';
  createdAt: string;
}

export interface MeasurementPlatform {
  id: string;
  name: string;
  status: 'active' | 'inactive';
  createdAt: string;
}
