# ADR-006: Composition rules in Datalog over the knowledge graph

| Field | Value |
|---|---|
| Status | Accepted (master v1.0) |
| Deciders | Architecture Board (U01 root authority) |
| References | master §11.3; U58 Composition; spec/rules/core/closure.dl |

## Context
Composition must derive required capabilities, adapters, controls and gaps from a platform definition plus facts (jurisdictions, industries, channels, regulations). The result must be deterministic, explainable and extendable as data, without code changes for new countries or industries.

## Decision
Composition and gap discovery are **Datalog rules over facts**. Generic rules (closure.dl) mention no country, vendor or industry; all specifics are facts governed by stewards. Blueprints are content-addressed (SHA-256), and the same inputs always yield the same hash. Every derived item carries its derivation trace ("because").

## Alternatives considered
- Imperative composer code: fast to start, but every new rule is a code change and harder to explain.
- General rule engine (Drools-class): less declarative, and termination and determinism are weaker.

## Consequences
**Positive**
- Explainable gaps (each gap shows its derivation).
- New regions or industries are added as data.
- Determinism is provable (`TEST-COMP-01`).

**Negative / costs**
- The team needs Datalog skills.
- The engine choice (Soufflé or an embeddable Rust engine) is still open; the reference checker implements the semantics in the meantime.

## Enforcement
tools/ucos_check.py reference semantics; `TEST-COMP-01`; `GAP-000`.
