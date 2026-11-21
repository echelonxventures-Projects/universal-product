export interface Analytics {
  id: string;
  type: string;
  status: 'active' | 'inactive';
  createdAt: string;
}

export interface Forecasting {
  id: string;
  type: string;
  forecast: Record<string, unknown>;
  accuracy: number;
  createdAt: string;
}

export interface Simulation {
  id: string;
  type: string;
  parameters: Record<string, unknown>;
  status: 'pending' | 'completed';
  result?: Record<string, unknown>;
  createdAt: string;
}

export interface Optimization {
  id: string;
  type: string;
  status: 'active' | 'inactive';
  createdAt: string;
}

export interface DecisionIntelligence {
  id: string;
  type: string;
  status: 'active' | 'inactive';
  createdAt: string;
}

export interface FraudIntelligence {
  id: string;
  type: string;
  status: 'active' | 'inactive';
  createdAt: string;
}

export interface RiskIntelligence {
  id: string;
  type: string;
  status: 'active' | 'inactive';
  createdAt: string;
}

export interface MarketIntelligence {
  id: string;
  type: string;
  status: 'active' | 'inactive';
  createdAt: string;
}

export interface PricingIntelligence {
  id: string;
  type: string;
  status: 'active' | 'inactive';
  createdAt: string;
}

export interface CommerceIntelligence {
  id: string;
  type: string;
  status: 'active' | 'inactive';
  createdAt: string;
}
