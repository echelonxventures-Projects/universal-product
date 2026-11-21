# ADR-024: Cells are provisioned with OpenTofu modules wrapped by Crossplane

| Field | Value |
|---|---|
| Status | Accepted |
| Deciders | Architecture Board (U01 root authority) |
| References | U73 Infrastructure; open decision U73; ADR-002 |

## Context
Cells must be created repeatably per region, by the control plane, with drift detection.

## Decision
Infrastructure is written as **OpenTofu modules** (portable, reviewable). **Crossplane** compositions wrap them so the control plane can request a cell as a Kubernetes resource and Crossplane reconciles drift. Argo CD deploys workloads into cells.

## Alternatives considered
- Plain OpenTofu runs from CI: simple, but no continuous reconciliation and no API for the control plane.
- Crossplane-native providers only: less mature for some services; lock-in to provider coverage.

## Consequences
**Positive**
- Cells become an API; drift is corrected automatically.

**Negative / costs**
- Two tools to learn; module and composition versions must move together.

## Enforcement
`ARCH-INF-01`; DR rehearsal (`DR-01`).
