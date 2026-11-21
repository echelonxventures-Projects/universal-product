export interface Security {
  id: string;
  type: string;
  status: 'active' | 'inactive';
  createdAt: string;
}

export interface ZeroTrust {
  id: string;
  status: 'active' | 'inactive';
  createdAt: string;
}

export interface Authentication {
  id: string;
  provider: string;
  status: 'active' | 'inactive';
  createdAt: string;
}

export interface Authorization {
  id: string;
  provider: string;
  status: 'active' | 'inactive';
  createdAt: string;
}

export interface RBAC {
  id: string;
  role: string;
  permissions: string[];
  status: 'active' | 'inactive';
}

export interface ABAC {
  id: string;
  attribute: string;
  value: string;
  status: 'active' | 'inactive';
}

export interface PBAC {
  id: string;
  policy: string;
  status: 'active' | 'inactive';
}

export interface IdentityFederation {
  id: string;
  provider: string;
  status: 'active' | 'inactive';
  createdAt: string;
}

export interface APISecurity {
  id: string;
  type: string;
  status: 'active' | 'inactive';
  createdAt: string;
}

export interface ApplicationSecurity {
  id: string;
  type: string;
  status: 'active' | 'inactive';
  createdAt: string;
}

export interface RuntimeSecurity {
  id: string;
  type: string;
  status: 'active' | 'inactive';
  createdAt: string;
}

export interface InfrastructureSecurity {
  id: string;
  type: string;
  status: 'active' | 'inactive';
  createdAt: string;
}

export interface Encryption {
  id: string;
  algorithm: string;
  status: 'active' | 'inactive';
}

export interface Tokenization {
  id: string;
  token: string;
  status: 'active' | 'inactive';
}

export interface SecretsManagement {
  id: string;
  type: string;
  status: 'active' | 'inactive';
  createdAt: string;
}

export interface KeyManagement {
  id: string;
  type: string;
  status: 'active' | 'inactive';
  createdAt: string;
}

export interface HSM {
  id: string;
  provider: string;
  status: 'active' | 'inactive';
  createdAt: string;
}

export interface DataProtection {
  id: string;
  type: string;
  status: 'active' | 'inactive';
  createdAt: string;
}

export interface PIIProtection {
  id: string;
  type: string;
  status: 'active' | 'inactive';
  createdAt: string;
}

export interface PrivacyManagement {
  id: string;
  type: string;
  status: 'active' | 'inactive';
  createdAt: string;
}

export interface ThreatIntelligence {
  id: string;
  type: string;
  status: 'active' | 'inactive';
  createdAt: string;
}

export interface FraudPrevention {
  id: string;
  type: string;
  status: 'active' | 'inactive';
  createdAt: string;
}

export interface BehavioralSecurity {
  id: string;
  type: string;
  status: 'active' | 'inactive';
  createdAt: string;
}

export interface ComplianceControls {
  id: string;
  type: string;
  status: 'active' | 'inactive';
  createdAt: string;
}

export interface PCIDSS {
  id: string;
  level: string;
  status: 'compliant' | 'non-compliant';
  createdAt: string;
}

export interface SOC2 {
  id: string;
  type: 'Type I' | 'Type II';
  status: 'compliant' | 'non-compliant';
  createdAt: string;
}

export interface ISO27001 {
  id: string;
  status: 'compliant' | 'non-compliant';
  createdAt: string;
}

export interface GDPR {
  id: string;
  status: 'compliant' | 'non-compliant';
  createdAt: string;
}

export interface RegionalCompliance {
  id: string;
  region: string;
  status: 'compliant' | 'non-compliant';
  createdAt: string;
}

export interface AISecurity {
  id: string;
  type: string;
  status: 'active' | 'inactive';
  createdAt: string;
}

export interface AgentSecurity {
  id: string;
  type: string;
  status: 'active' | 'inactive';
  createdAt: string;
}

export interface SupplyChainSecurity {
  id: string;
  type: string;
  status: 'active' | 'inactive';
  createdAt: string;
}
