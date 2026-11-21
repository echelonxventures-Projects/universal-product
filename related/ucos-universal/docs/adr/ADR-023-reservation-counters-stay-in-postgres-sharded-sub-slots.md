# ADR-023: Reservation counters stay in Postgres (sharded sub-slots)

| Field | Value |
|---|---|
| Status | Accepted |
| Deciders | Architecture Board (U01 root authority) |
| References | U13 Temporal; open decision U13 |

## Context
Slot reservations (deliveries, appointments, flash-sale stock) need atomic counters under peak contention. Redis is fast but adds a second source of truth for availability.

## Decision
Keep reservation counters in **Postgres**. Hot slots are split into N sub-slot rows chosen by hash, so contention spreads, and `remaining` is the sum. Reservations remain transactional with the command that creates them. Redis is introduced only if the P1 load test (`PERF-SLO-01`) shows p99 above target at the declared peak, and then only as a lease cache in front of Postgres.

## Alternatives considered
- Redis counters as the source of truth: fastest, but split-brain and recovery semantics complicate audit and replay.

## Consequences
**Positive**
- One transactional store; reservations are audited and bitemporal like everything else.

**Negative / costs**
- Sub-slot sharding logic in the Temporal service.

## Enforcement
`PERF-SLO-01` with a flash-sale profile; U13 property tests (`ARCH-TMP-03`).
