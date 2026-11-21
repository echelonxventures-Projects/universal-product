# ADR-001: Interpret metadata at runtime; generate only external artifacts

| Field | Value |
|---|---|
| Status | Accepted (master v1.0) |
| Deciders | Architecture Board (U01 root authority) |
| References | master §12.1, §12.2; U59 Generation |

## Context
UCOS must turn a platform definition into running software for many tenants. The source material asked for UI, API, database, workflow, infrastructure and test generation. Generating code per tenant would leave N tenants × M versions of code to patch and secure, and every tenant would drift from the platform.

## Decision
The runtime **interprets** blueprints for data, API, workflow, policy, decision and UI. Generation (U59) is limited to artifacts consumed **outside** the runtime or that benefit from static compilation: SDKs, documentation, physical migrations for core types, mobile shells, IaC for cells, test suites, dashboards and alerts, evidence packs and diagrams. Generation never produces tenant-specific business code.

## Alternatives considered
- Per-tenant code generation with eject: familiar, but turns every security fix into an N×M rollout and breaks Laws L2 and L6.
- Hybrid with optional eject: same drift problem for ejected tenants; rejected for v1.

## Consequences
**Positive**
- One codebase to secure, scale and certify.
- Configuration changes are data and take effect instantly through governed change.
- Tenants never fork, so platform upgrades reach everyone.

**Negative / costs**
- Runtime engines (object service, workflow, policy, UI renderer) must be excellent; performance work concentrates there.
- Tenants who need custom logic use extension points (WASM, webhooks, packs), not code edits.

## Enforcement
GEN-L2/GEN-L3 (U59); certification `ARCH-GEN-01`; no generated business code accepted in pack review.
