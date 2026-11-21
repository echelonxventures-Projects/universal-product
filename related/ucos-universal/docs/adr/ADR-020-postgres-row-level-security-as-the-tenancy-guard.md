# ADR-020: Postgres row-level security as the tenancy guard

| Field | Value |
|---|---|
| Status | Accepted (KERNEL-DESIGN §4) |
| Deciders | Architecture Board (U01 root authority) |
| References | engineering/KERNEL-DESIGN.md; Law L8 |

## Context
Shared-schema multi-tenancy is required for cost, and a missing `WHERE tenant_id` in one query must not leak data.

## Decision
Every tenant-scoped table has `tenant_id` and an **RLS policy** bound to a session variable set by the object service from the context envelope. Service roles cannot bypass RLS. Caches, search indexes, event topics and object storage use tenant-prefixed keys. A cross-tenant leak suite runs in CI.

## Alternatives considered
- Application-level filtering only: one bug away from a leak.
- Database per tenant: too costly for SMB tenants. Available as dedicated cells.

## Consequences
**Positive**
- Defence in depth for tenant isolation.

**Negative / costs**
- Connection pooling must reset session variables (pgbouncer transaction mode with SET LOCAL).

## Enforcement
`SEC-TENANT-01`.
