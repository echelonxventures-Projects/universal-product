export interface Personalization {
  id: string;
  customerId: string;
  preferences: Record<string, unknown>;
  segments: string[];
  features: PersonalizationFeature[];
  status: 'active' | 'inactive';
}

export interface PersonalizationFeature {
  id: string;
  name: string;
  enabled: boolean;
  configuration: Record<string, unknown>;
}
