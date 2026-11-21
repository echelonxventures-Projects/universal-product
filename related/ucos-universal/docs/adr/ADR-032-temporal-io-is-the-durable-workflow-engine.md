# ADR-032: Temporal.io is the durable workflow engine

| Field | Value |
|---|---|
| Status | Accepted (confirmed by spike S-05) |
| Deciders | Architecture Board (U01 root authority) |
| References | U60 Workflow; ADR-016; open decision U60 |

## Context
ADR-016 chose a Temporal.io-class durable engine; the product had to be named.

## Decision
Use **Temporal.io** (open source, self-hosted per cell) behind the U60 abstraction. BPMN models are imported by a converter into the UCOS workflow definition format, not executed by a BPMN engine.

## Alternatives considered
- Camunda 8: strong BPMN tooling, but a heavier stack and licensing constraints for self-hosted production use.

## Consequences
**Positive**
- Code-first durability, versioning and replay; large community.

**Negative / costs**
- Operating Temporal clusters per cell.

## Enforcement
S-05; `ARCH-WF-01`.
