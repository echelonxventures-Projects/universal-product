# ADR-026: Cedar only; OpenFGA is not adopted

| Field | Value |
|---|---|
| Status | Accepted (revisit at P6) |
| Deciders | Architecture Board (U01 root authority) |
| References | U03 Policy; open decision U03; ADR-005 |

## Context
Relationship-heavy authorisation (social graphs, deep sharing hierarchies) can strain an attribute-based PDP.

## Decision
Stay on **Cedar** with relationship facts supplied as entities. Revisit only if a P6 vertical needs relationship queries deeper than four hops, or authorisation p99 above 10 ms at the declared scale. If so, OpenFGA would be added behind the same PDP port as a relationship source, not a second policy language.

## Alternatives considered
- Adopt OpenFGA now: premature; two authorisation systems to audit.

## Consequences
**Positive**
- One policy language and one audit trail.

**Negative / costs**
- Very large sharing graphs may need precomputed relationship entities.

## Enforcement
`SEC-POLICY-01`; PDP latency SLO.
