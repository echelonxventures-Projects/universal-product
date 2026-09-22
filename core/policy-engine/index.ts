import { Policy, PolicyRegistry, PolicyEvaluationResult } from '../types/policy';

interface ConditionEvaluator {
  eq: (actual: unknown, expected: unknown) => boolean;
  neq: (actual: unknown, expected: unknown) => boolean;
  gt: (actual: number, expected: number) => boolean;
  lt: (actual: number, expected: number) => boolean;
  in: (actual: unknown, expected: unknown[]) => boolean;
  contains: (actual: string, expected: string) => boolean;
}

const evaluators: ConditionEvaluator = {
  eq: (a, e) => a === e,
  neq: (a, e) => a !== e,
  gt: (a, e) => (a as number) > (e as number),
  lt: (a, e) => (a as number) < (e as number),
  in: (a, e) => (e as unknown[]).includes(a),
  contains: (a, e) => (a as string).includes(e as string),
};

export class PolicyEngine implements PolicyRegistry {
  private policies: Map<string, Policy> = new Map();

  async getPolicy(id: string): Promise<Policy | null> {
    return this.policies.get(id) || null;
  }

  async registerPolicy(policy: Policy): Promise<void> {
    this.policies.set(policy.id, policy);
  }

  async evaluatePolicy(policyId: string, context: Record<string, unknown>): Promise<PolicyEvaluationResult> {
    const policy = this.policies.get(policyId);
    if (!policy) return { allowed: false, reason: 'Policy not found', conditionsMatched: [] };

    const matched: string[] = [];
    let allowed = true;

    for (const cond of policy.conditions) {
      const actual = this.getValue(context, cond.field);
      const matches = evaluators[cond.operator](actual, cond.value);
      
      if (!matches) {
        allowed = false;
        break;
      }
      matched.push(cond.field);
    }

    return { allowed, reason: allowed ? 'All conditions satisfied' : 'Condition failed', conditionsMatched: matched };
  }

  private getValue(context: Record<string, unknown>, path: string): unknown {
    return path.split('.').reduce((obj, key) => 
      (obj as Record<string, unknown>)?.[key], context);
  }

  getPolicyIds(): string[] {
    return Array.from(this.policies.keys());
  }
}

export const policyEngine = new PolicyEngine();
