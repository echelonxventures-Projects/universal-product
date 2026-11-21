# ADR-007: Transactional outbox and sagas; no distributed two-phase commit

| Field | Value |
|---|---|
| Status | Accepted (master v1.0) |
| Deciders | Architecture Board (U01 root authority) |
| References | master §13.3; KERNEL-DESIGN outbox; U60 Workflow |

## Context
Universes own their data (Law L4) and communicate by events. Business processes span universes (order → payment → fulfilment → ledger). 2PC across services is fragile at scale.

## Decision
Each command commits its state change and its events atomically through a **transactional outbox**; a relay publishes to the event bus. Cross-universe processes are **sagas** on the durable workflow engine with explicit compensations. Commands are idempotent (`cmd_idempotency`), and consumers are idempotent by event id.

## Alternatives considered
- 2PC/XA: couples availability and complicates operations.
- Event sourcing everywhere: powerful, but heavy for every universe. It is used selectively (Ledger is append-only).

## Consequences
**Positive**
- Reliable delivery and reliable failure handling.
- Universes stay independently deployable.

**Negative / costs**
- Eventual consistency must be designed into the UX (pending states).
- Compensations must be specified and tested.

## Enforcement
Pack review; `ARCH-WF-01`; contract tests for events.
