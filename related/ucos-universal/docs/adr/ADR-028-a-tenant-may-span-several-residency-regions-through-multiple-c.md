# ADR-028: A tenant may span several residency regions through multiple cells

| Field | Value |
|---|---|
| Status | Accepted |
| Deciders | Architecture Board (U01 root authority) |
| References | U10 Organization & Tenant; U73; open decision U10 |

## Context
Some tenants operate in several jurisdictions that each require local storage (for example India and the EU).

## Decision
A tenant is **one logical tenant with data shards in several cells**. Each shard holds the data whose residency rule points to its region. Cross-shard operations go through the event backbone with only non-personal or transfer-approved data. Tenant-level views (analytics, admin) are federated queries over shards. The P2 spike measures cross-cell latency for admin views.

## Alternatives considered
- One cell per tenant, ignoring residency per data class: non-compliant.
- Separate tenants per region linked by TenantLink: works, but loses one customer identity and one admin.

## Consequences
**Positive**
- Residency is satisfied per data class without splitting the customer.

**Negative / costs**
- Federated admin queries are slower; some features are region-scoped.

## Enforcement
`CMP-RES-01`; placement checks in the composer.
