# ADR-008: Global product master separated from tenant listings

| Field | Value |
|---|---|
| Status | Accepted (master v1.0) |
| Deciders | Architecture Board (U01 root authority) |
| References | master §10.1; U18 Product Intelligence; U21 Catalog |

## Context
Many tenants sell the same real-world products. Re-entering product data per tenant wastes effort and lowers quality, but tenant commercial data must never leak to other tenants.

## Decision
**U18** holds a platform-scope Global Product (GPID) with attributes, identifiers, provenance and recalls. Tenants create **Listings** (U21) that reference a GPID and add their own commercial data (price, stock, content overrides). Contributions from tenants to the global master pass matching and governance and carry no tenant-commercial data.

## Alternatives considered
- Per-tenant product tables only: simple, but duplicated and low quality.
- A shared mutable product table: leaks tenant data and causes edit conflicts.

## Consequences
**Positive**
- Shared enrichment, recalls and identifiers.
- Cross-tenant features (comparison, recalls) without leaking data.

**Negative / costs**
- Data-sourcing licences are needed (open decision U18).
- Matching quality must be managed.

## Enforcement
Ownership checks (L4); policy P-00x tenant isolation; U18 governance workflow.
