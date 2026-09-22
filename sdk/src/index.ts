export * from './rest';
export * from './graphql';
export * from './agent';

export interface UCIClientConfig {
  baseUrl: string;
  tenantId: string;
  apiKey: string;
  timeout?: number;
  retryAttempts?: number;
}

export class UCIClient {
  constructor(private config: UCIClientConfig) {}

  async request<T>(method: string, path: string, body?: unknown): Promise<T> {
    // Implementation
    throw new Error('Not implemented');
  }
}
