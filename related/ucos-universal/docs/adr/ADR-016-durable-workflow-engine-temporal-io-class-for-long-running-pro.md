# ADR-016: Durable workflow engine (Temporal.io class) for long-running processes

| Field | Value |
|---|---|
| Status | Accepted (master v1.0; U60) |
| Deciders | Architecture Board (U01 root authority) |
| References | U60 Workflow; KERNEL-DESIGN |

## Context
Many processes wait on time, humans or external systems, and need retries and compensation (order lifecycle, dunning, onboarding, disputes).

## Decision
Long-running processes run on a **durable execution engine** (Temporal.io or an equivalent) behind the U60 abstraction. Workflow definitions are versioned metadata, and human tasks, timers and signals are first-class. Timers are U13 triggers. Packs never implement state machines plus cron.

## Alternatives considered
- Hand-rolled state machines with cron: fragile and invisible.
- BPMN engines (Camunda): strong modelling, but heavier, and code-first durability is a better fit for packs.

## Consequences
**Positive**
- Reliable retries, timeouts, compensation and visibility.

**Negative / costs**
- Operating the engine is critical-path (tier T0).

## Enforcement
`ARCH-WF-01`, `ARCH-TMP-01`.
