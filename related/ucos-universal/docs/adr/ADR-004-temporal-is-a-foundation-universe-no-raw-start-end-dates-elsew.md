# ADR-004: Temporal is a foundation universe; no raw start/end dates elsewhere

| Field | Value |
|---|---|
| Status | Accepted (master v1.0; strengthened by A-46, A-63) |
| Deciders | Architecture Board (U01 root authority) |
| References | master §9; U13 Temporal App. E; TEMPORAL-BINDING-MATRIX.md |

## Context
Scheduling, availability, validity, deadlines, SLAs, recurrences and calendars appeared in almost every domain of the source material, each implemented differently. Ad-hoc date maths causes time-zone, DST and business-calendar bugs that surface at the worst times (billing, legal deadlines).

## Decision
Time is owned by **U13 Temporal**. Every universe uses kernel value types (`TimePoint`, `TimeRange`, `Duration`, `Recurrence`, `TemporalRef`) and, for service behaviour (calendars, policies, triggers, reservations, SLA clocks, waitlists, feeds), calls U13 and declares the dependency. Field names follow the canonical naming table (U13 App. E.3). Packs never run their own schedulers.

## Alternatives considered
- Each universe handles its own dates: duplicates logic and causes inconsistent behaviour.
- Use a scheduling library inside each pack: no shared calendars, no audit of triggers.

## Consequences
**Positive**
- One implementation of calendars, holidays, business time and time zones.
- Every deadline and trigger is visible, auditable and simulatable (simulated clocks).
- Non-Earth calendar systems are possible (U77).

**Negative / costs**
- U13 is on the critical path for many universes and is therefore tier T0.
- Spec authors must follow the naming rule (lint-enforced).

## Enforcement
Gates `ARCH-TMP-01`…`ARCH-TMP-05`; TMP-LINT-002; checker temporal rule.
