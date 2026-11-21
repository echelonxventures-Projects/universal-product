export interface Policy {
  id: string;
  name: string;
  description: string;
  version: string;
  active: boolean;
  conditions: PolicyCondition[];
  actions: PolicyAction[];
  priority: number;
}

export interface PolicyCondition {
  field: string;
  operator: 'eq' | 'neq' | 'gt' | 'lt' | 'in' | 'contains';
  value: unknown;
}

export interface PolicyAction {
  type: string;
  parameters: Record<string, unknown>;
}

export interface PolicyRegistry {
  getPolicy(id: string): Promise<Policy | null>;
  evaluatePolicy(policyId: string, context: Record<string, unknown>): Promise<PolicyEvaluationResult>;
  registerPolicy(policy: Policy): Promise<void>;
}

export interface PolicyEvaluationResult {
  allowed: boolean;
  reason: string;
  conditionsMatched: string[];
}
