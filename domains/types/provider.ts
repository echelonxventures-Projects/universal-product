export interface Provider {
  id: string;
  name: string;
  type: 'payment' | 'shipping' | 'email' | 'analytics' | 'other';
  status: 'active' | 'inactive';
  apiEndpoint: string;
  apiKey?: string;
  configuration: Record<string, string>;
  metadata: Record<string, unknown>;
  createdAt: string;
}

export interface ProviderIntegration {
  id: string;
  providerId: string;
  customerId: string;
  enabled: boolean;
  status: 'active' | 'inactive';
  createdAt: string;
}
