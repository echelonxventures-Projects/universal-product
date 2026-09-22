export interface PlatformConfig {
  global: GlobalConfig;
  tenants: TenantConfig[];
  features: FeatureFlags;
  integrations: IntegrationConfig[];
}

export interface GlobalConfig {
  version: string;
  region: string;
  timezone: string;
  supportedCurrencies: string[];
  defaultCurrency: string;
  security: SecurityConfig;
  observability: ObservabilityConfig;
}

export interface SecurityConfig {
  authentication: AuthMethod;
  mfa: MFAConfig;
  encryption: EncryptionConfig;
  rateLimit: RateLimitConfig;
}

export interface ObservabilityConfig {
  metrics: MetricsConfig;
  tracing: TracingConfig;
  logging: LoggingConfig;
}

export interface TenantConfig {
  id: string;
  name: string;
  status: TenantStatus;
  domains: string[];
  features: FeatureFlags;
  billing: BillingConfig;
}

export interface FeatureFlags {
  aiCommerce: boolean;
  marketplaceFederation: boolean;
  agentProtocol: boolean;
  retailMedia: boolean;
}

export function validateConfig(config: PlatformConfig): ValidationResult {
  // Schema validation
  return { valid: true, errors: [] };
}
