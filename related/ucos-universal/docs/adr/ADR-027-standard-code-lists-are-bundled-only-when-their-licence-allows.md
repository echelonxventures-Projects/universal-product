# ADR-027: Standard code lists are bundled only when their licence allows multi-tenant redistribution

| Field | Value |
|---|---|
| Status | Accepted (S-06 records the per-source outcome) |
| Deciders | Architecture Board (U01 root authority) |
| References | U08 Reference Data; U12 Geography; open decisions U08, U12; PHASE1-READINESS S-06 |

## Context
UCOS ships reference data (GS1 GPC, UNSPSC, HS, ISIC, boundaries). Licences differ, and some forbid redistribution or impose share-alike terms.

## Decision
A code list or dataset is **bundled in the platform only if its licence permits use and redistribution in a multi-tenant SaaS**. The licence is recorded as a fact on the CodeListRelease. Otherwise it becomes a **bring-your-own-licence data pack** that a tenant activates with its own licence reference. OpenStreetMap boundaries (ODbL) may be used with attribution, and any derived database is kept separate from tenant data so share-alike obligations stay contained. Spike S-06 records the legal outcome per source as a DecisionRecord.

## Alternatives considered
- Bundle everything and sort licences out later: legal exposure.
- Bundle nothing: poor out-of-the-box experience.

## Consequences
**Positive**
- Clear rule; licence status is data that the checker and U67 can see.

**Negative / costs**
- Some tenants must supply licences before using certain classifications.

## Enforcement
CodeListRelease requires `licence`; data packs without a licence reference cannot activate.
