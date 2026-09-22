export interface Logistics {
  id: string;
  carrier: string;
  serviceLevel: string;
  zones: Zone[];
  rates: Rate[];
  constraints: Constraints;
  status: 'active' | 'inactive';
}

export interface Zone {
  id: string;
  name: string;
  countries: string[];
  states?: string[];
}

export interface Rate {
  zoneId: string;
  minWeight: number;
  maxWeight: number;
  basePrice: number;
  perUnitPrice: number;
  currency: string;
}

export interface Constraints {
  maxWeight: number;
  maxDimensions?: { length: number; width: number; height: number };
  prohibitedItems: string[];
}

export interface CarrierConfig {
  id: string;
  name: string;
  apiKey?: string;
  apiKeyId?: string;
  status: 'active' | 'inactive';
}
