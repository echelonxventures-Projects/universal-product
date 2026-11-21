# ADR-011: Bitemporal canonical objects

| Field | Value |
|---|---|
| Status | Accepted (master v1.0) |
| Deciders | Architecture Board (U01 root authority) |
| References | master §14.6; U13; U68 Audit |

## Context
Regulation, audit, dispute resolution and simulation need to know both what was true in the business world at a time (valid time) and what the system knew at a time (transaction time).

## Decision
Canonical objects carry **valid time** and **transaction time**. Queries support `asOf` on both axes, and corrections never overwrite history. Hot tables keep current state; history tables or partitions keep versions. Audit (U68) chains are separate and tamper-evident.

## Alternatives considered
- Current state plus an audit log only: cannot answer "what did we believe on date X about date Y".
- Full event sourcing for every type: more complex than needed for most universes.

## Consequences
**Positive**
- Reproducible decisions and reports.
- Late corrections are handled correctly (e.g. tax, ledger).

**Negative / costs**
- Storage overhead.
- Query complexity; the object service hides it behind `asOf`.

## Enforcement
U04 lint (bitemporal fields on persisted types); object-service conformance tests.
