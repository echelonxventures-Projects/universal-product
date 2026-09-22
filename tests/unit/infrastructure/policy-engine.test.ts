import { describe, it, expect, beforeEach } from 'vitest';
import { PolicyEngine } from '../../core/policy-engine';
import { Policy } from '../../core/types/policy';

describe('PolicyEngine', () => {
  let engine: PolicyEngine;

  beforeEach(() => {
    engine = new PolicyEngine();
  });

  describe('registerPolicy', () => {
    it('should register a policy', async () => {
      const policy: Policy = {
        id: 'policy-1',
        name: 'Minimum Order Value',
        description: 'Require minimum order value',
        version: '1.0.0',
        active: true,
        conditions: [
          { field: 'order.total', operator: 'gte', value: 50 },
        ],
        actions: [{ type: 'allow', parameters: {} }],
        priority: 1,
      };

      await engine.registerPolicy(policy);

      const retrieved = await engine.getPolicy('policy-1');
      expect(retrieved).toEqual(policy);
    });
  });

  describe('evaluatePolicy', () => {
    it('should evaluate conditions', async () => {
      const policy: Policy = {
        id: 'policy-2',
        name: 'Discount Eligibility',
        description: '',
        version: '1.0.0',
        active: true,
        conditions: [
          { field: 'order.total', operator: 'gte', value: 100 },
          { field: 'customer.tier', operator: 'in', value: ['premium', 'vip'] },
        ],
        actions: [{ type: 'allow', parameters: {} }],
        priority: 1,
      };

      await engine.registerPolicy(policy);

      // Test passing context
      const passingResult = await engine.evaluatePolicy('policy-2', {
        order: { total: 150 },
        customer: { tier: 'premium' },
      });

      expect(passingResult.allowed).toBe(true);
      expect(passingResult.conditionsMatched.length).toBe(2);

      // Test failing context
      const failingResult = await engine.evaluatePolicy('policy-2', {
        order: { total: 50 },
        customer: { tier: 'regular' },
      });

      expect(failingResult.allowed).toBe(false);
    });

    it('should return error for non-existent policy', async () => {
      const result = await engine.evaluatePolicy('non-existent', {});
      expect(result.allowed).toBe(false);
      expect(result.reason).toBe('Policy not found');
    });
  });
});
