# ADR-005: Single PDP (Cedar) for RBAC, ABAC, ReBAC and PBAC

| Field | Value |
|---|---|
| Status | Accepted (master v1.0) |
| Deciders | Architecture Board (U01 root authority) |
| References | master §18.5; U03 Policy; spec/policies/ |

## Context
Authorisation needs roles, attributes, relationships and policy conditions (jurisdiction, time, risk) across all universes, and it must be analysable for audits and least privilege.

## Decision
All application authorisation goes through one **policy decision point using Cedar**, layered as platform → universe defaults → tenant. Partial evaluation pre-filters queries. OPA/Rego is used only for infrastructure admission (Kubernetes, CI). Policies are versioned and tested, and the platform baseline P-001…P-007 cannot be overridden by tenants.

## Alternatives considered
- OPA/Rego for everything: flexible, but less analysable and slower to evaluate for fine-grained application checks.
- Zanzibar-style ReBAC only (OpenFGA): strong on relationships, weak on attribute conditions. Kept as a possible P6 complement for social graphs (open decision U03).

## Consequences
**Positive**
- One language, formal analysis (no-overlap, never-permits checks).
- Uniform audit of decisions.

**Negative / costs**
- Cedar's ecosystem is younger than OPA's.
- Relationship-heavy graphs may need OpenFGA later.

## Enforcement
`SEC-POLICY-01`; policy tests required in packs; P-001…P-007 locked.
