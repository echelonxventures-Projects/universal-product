// UCOS platform-layer policies (U03 §5.3, A-28). Layer: platform. Cannot be overridden by tenant policies (POL-L3).
// Conventions: action groups are Action entities named "group:<name>" (Cedar requires Action-typed parents);
// an @obligation annotation holds a comma-separated list because Cedar forbids repeating an annotation.
// CI parses these files and runs spec/policies/tests/*.yaml (gate SEC-POLICY-01).

// P-001 Tenant isolation: no cross-tenant access without an explicit TenantLink scope (ORG-L2).
@id("P-001") @obligation("audit:full")
forbid (principal, action, resource)
when {
  resource has tenant && principal has tenant &&
  resource.tenant != principal.tenant &&
  !(context has tenantLink && context.tenantLink.actions.contains(action))
};

// P-002 Only active principals may act.
@id("P-002")
forbid (principal, action, resource)
when { principal has status && principal.status != "active" };

// P-003 Agents act only within delegated authority and budget (L17, U51).
@id("P-003")
forbid (principal is Agent, action, resource)
unless { principal.authority.actions.contains(action) && context.agent.budgetRemaining > 0 };

// P-004 Reality isolation (generalised simulation isolation, A-28).
@id("P-004")
forbid (principal, action in Action::"group:external-side-effect", resource)
when {
  context.frame.sideEffectPolicy != "full" &&
  !(context has realityBridge && context.realityBridge.allows.contains(action))
};

// P-005 asOf (time travel) is read-only outside simulation (CTX-L5).
@id("P-005")
forbid (principal, action in Action::"group:write", resource)
when { context.time has asOf && !context.simulation };

// P-006 Separation of duties: nobody approves what they created (U01 AUTH, U02, U09 SoD).
@id("P-006")
forbid (principal, action in Action::"group:approve", resource)
when { resource has createdBy && resource.createdBy == principal };

// P-007 Unknown risk is treated as medium: step-up for sensitive actions (U16 Appendix P1).
@id("P-007") @obligation("stepUpAuth:AAL2")
permit (principal, action in Action::"group:sensitive", resource)
when { context.risk.band == "unknown" || context.risk.band == "medium" } ;
