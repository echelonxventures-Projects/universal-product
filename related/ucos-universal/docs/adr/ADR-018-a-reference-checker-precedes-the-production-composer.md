# ADR-018: A reference checker precedes the production composer

| Field | Value |
|---|---|
| Status | Accepted (A-66, A-69) |
| Deciders | Architecture Board (U01 root authority) |
| References | tools/ucos_check.py; spec/ |

## Context
The specification is large, and inconsistencies (ownership collisions, phase inversions, missing simulators, undefined gates) are easy to introduce. The production composer is not built yet.

## Decision
A **reference checker** in Python implements the composition semantics, registry integrity, gate references and registry synchronisation over `spec/`. It runs in CI and must exit 0. The production composer must reproduce the golden blueprints byte-for-byte before it replaces the checker in CI.

## Alternatives considered
- Wait for the production composer: inconsistencies accumulate unseen.

## Consequences
**Positive**
- The specification is continuously consistent, and golden blueprints define the composer's acceptance tests.

**Negative / costs**
- Two implementations of the semantics exist until the composer lands.

## Enforcement
CI job `ucos_check`; golden expected files.
