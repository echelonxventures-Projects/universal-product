# ADR-003: Hybrid physical model: generated tables for core types, JSONB for tenant extensions

| Field | Value |
|---|---|
| Status | Accepted (master v1.0) |
| Deciders | Architecture Board (U01 root authority) |
| References | master §14.2; KERNEL-DESIGN §4.1; U04 Meta |

## Context
Object types are defined as metadata, but they need relational performance, constraints and indexes at scale. Tenants also need custom fields without schema changes per tenant.

## Decision
Core object types (owned by certified packs) are stored in **generated physical tables** with typed columns, constraints and indexes, evolved by expand/contract migrations. Tenant custom attributes go into a `custom JSONB` column validated against the tenant's ExtensionSchema; tenants may request expression indexes within quotas. Low-volume registry-only types use a generic `objects` table. Every table carries `tenant_id` with Postgres row-level security.

## Alternatives considered
- Pure EAV: flexible but slow and hard to constrain.
- Pure JSONB for everything: simple, but weak constraints and poor planner statistics on hot paths.
- Schema per tenant: strong isolation, but migrations multiply by tenant count.

## Consequences
**Positive**
- Hot paths are typed and indexed.
- Tenant extensibility needs no DDL per tenant.
- RLS gives a uniform tenancy guard.

**Negative / costs**
- Two storage shapes to support in the object service.
- Core-type migrations must be rehearsed (`ARCH-META-02`).

## Enforcement
U04 lint (`ARCH-META-01`), migration rehearsal (`ARCH-META-02`), tenant isolation suite (`SEC-TENANT-01`).
