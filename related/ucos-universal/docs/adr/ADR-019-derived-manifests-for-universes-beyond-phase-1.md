# ADR-019: Derived manifests for universes beyond Phase 1

| Field | Value |
|---|---|
| Status | Accepted (A-69) |
| Deciders | Architecture Board (U01 root authority) |
| References | tools/gen_manifests.py; spec/capabilities/packs/ |

## Context
Phases 2–6 universes had constitutions but no manifests, so their object types and events were not in the registry and could not be checked for ownership collisions.

## Decision
Each universe without a hand-authored manifest gets a **derived `<slug>.core` manifest** (maturity `experimental`), parsed from its constitution and the Temporal binding matrix. Dependencies in a later phase, or ones that would close a requires-cycle, become optional. A steward replaces it with a hand-authored manifest (adapters, decisions, controls, views) before that phase starts.

## Alternatives considered
- Hand-author all manifests now: slower, and premature for later phases.

## Consequences
**Positive**
- The whole platform's ownership and event model is checked today.

**Negative / costs**
- Derived manifests are coarse: one core capability per universe.

## Enforcement
Checker; maturity `experimental` blocks certification above beta.
