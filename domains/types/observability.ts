export interface Observability {
  id: string;
  type: string;
  status: 'active' | 'inactive';
  createdAt: string;
}

export interface Metrics {
  id: string;
  name: string;
  value: number;
  tags: Record<string, string>;
  timestamp: string;
}

export interface Logs {
  id: string;
  level: string;
  message: string;
  context: Record<string, unknown>;
  timestamp: string;
}

export interface Traces {
  id: string;
  spanId: string;
  traceId: string;
  operation: string;
  duration: number;
  status: string;
  timestamp: string;
}

export interface Events {
  id: string;
  type: string;
  payload: Record<string, unknown>;
  timestamp: string;
}

export interface BusinessKPIs {
  id: string;
  name: string;
  value: number;
  target: number;
  period: string;
}

export interface RevenueKPIs {
  id: string;
  name: string;
  value: number;
  target: number;
  period: string;
}

export interface CommerceKPIs {
  id: string;
  name: string;
  value: number;
  target: number;
  period: string;
}

export interface OfferMonitoring {
  id: string;
  offerId: string;
  status: 'active' | 'inactive';
}

export interface PricingMonitoring {
  id: string;
  productId: string;
  status: 'active' | 'inactive';
}

export interface SettlementMonitoring {
  id: string;
  batchId: string;
  status: 'active' | 'inactive';
}

export interface BillingMonitoring {
  id: string;
  customerId: string;
  status: 'active' | 'inactive';
}

export interface FraudMonitoring {
  id: string;
  riskLevel: string;
  status: 'active' | 'inactive';
}

export interface RiskMonitoring {
  id: string;
  type: string;
  status: 'active' | 'inactive';
}

export interface AITMonitoring {
  id: string;
  modelId: string;
  status: 'active' | 'inactive';
}

export interface AuditMonitoring {
  id: string;
  type: string;
  status: 'active' | 'inactive';
}

export interface DependencyMapping {
  id: string;
  source: string;
  target: string;
  status: 'active' | 'inactive';
}

export interface LineageTracking {
  id: string;
  data: string;
  source: string;
  transformations: string[];
}
