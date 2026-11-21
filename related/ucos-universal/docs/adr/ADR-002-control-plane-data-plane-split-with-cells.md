# ADR-002: Control plane / data plane split with cells

| Field | Value |
|---|---|
| Status | Accepted (master v1.0) |
| Deciders | Architecture Board (U01 root authority) |
| References | master §5.4, §27.1; U73 Infrastructure; U10 Tenant |

## Context
UCOS serves tenants in many jurisdictions with different residency rules and very different scale. A single shared deployment makes every incident global and cannot meet data-residency requirements.

## Decision
A global **control plane** holds registries, composition, governance and certification. Tenant data and traffic run in **data-plane cells**: independent stacks pinned to a region and jurisdiction, each with its own databases, event bus and caches. A tenant's shards are placed in cells that satisfy its residency rules. Global registries replicate read-only to cells.

## Alternatives considered
- Single multi-region cluster: simpler, but the blast radius is global and residency is hard to prove.
- Silo per tenant: strongest isolation, but the cost is prohibitive for SMB tenants. Kept only as a dedicated-cell option for large or regulated tenants.

## Consequences
**Positive**
- Bounded blast radius; cell-by-cell progressive rollout.
- Residency becomes a placement fact that can be checked (`CMP-RES-01`).
- Scale out by adding cells.

**Negative / costs**
- Cross-cell queries need the analytics plane (U72/U93).
- Tenant moves between cells are migrations (U73 runbook).
- There is more infrastructure to operate, so automation (OpenTofu/Crossplane, Argo CD) is mandatory.

## Enforcement
U73 placement engine; gates `CMP-RES-01`, `ARCH-INF-01`, `DR-01`.
