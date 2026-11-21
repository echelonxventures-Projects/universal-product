# ADR-014: Frames of reference (U77) make every foundation frame-aware

| Field | Value |
|---|---|
| Status | Accepted (A-23…A-28) |
| Deciders | Architecture Board (U01 root authority) |
| References | U77 Existence, Reality & Frame; U12; U13; U14; U15 |

## Context
The platform must be extensible to any region, planet, reality (physical, simulated, virtual), calendar, currency system, unit system and language without changing consuming universes.

## Decision
**U77** registers realities, bodies, spatial frames, time scales, calendar, monetary, unit and language systems, and governing authorities. Value types carry an optional `frame` with an earth-physical default. New frames are registry entries plus certified conversion packs. Reality isolation (policy P-004) forbids side effects across realities, and simulated realities use simulators.

## Alternatives considered
- Hard-code Earth assumptions and extend later: cheap now, but expensive and risky later.
- Frame support in each universe separately: inconsistent.

## Consequences
**Positive**
- Future extension is data, not code.
- Simulation and sandbox realities fall out naturally.

**Negative / costs**
- Slight overhead in value types.
- Golden tests must run under a synthetic frame (`ARCH-FRM-02`, `ARCH-TMP-04`).

## Enforcement
`ARCH-FRM-01`, `ARCH-FRM-02`, `ARCH-CTX-02`.
