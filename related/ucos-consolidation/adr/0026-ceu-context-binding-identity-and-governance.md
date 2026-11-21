# ADR-0026: CEU units bind IDENTITY and GOVERNANCE context through UCXI-000001

| Field | Value |
|-------|-------|
| Status | Accepted |
| Date | 2026-08-21 |
| Deciders | Constitutional Authority · UCOS Ω∞ |
| Technology Constitution refs | `adr/0019-residual-phase4-finding-disposition.md` (`WP-UCDA-028`), `P4-F-009` remainder |
| Supersedes | none — discharges one more of `WP-UCDA-028`'s six independent sub-obligations |

## Context

`P4-F-009` named the remainder finding that UCXI-000001's `ContextRegistry` had exactly
one real call site anywhere in the repository before this session: `engine/knowledge/
ukip/confidence.py` (`ADR-0016`), binding the `KNOWLEDGE` kind for UKIP's knowledge
objects. Every other one of the sixteen universal context kinds, and every other
entity substrate in the platform, remained unexercised — proof the registry exists and
works for one kind and one substrate, not evidence it generalizes.

CEU-001's `ExistenceUnit` (`engine/ceu/existence.py`) is the platform's "everything is
an entity" substrate: a form, a classification, a relationship, a topology are all this
one record type. It already owns exactly the data two more universal kinds need:

- `IDENTITY` (`subject`/`identifier`/`authority`) — a unit's own `title`, its
  EPIC/REG-AUTO-001-minted `universal_id`, and the `identity_kind` that authority
  minted it under.
- `GOVERNANCE` (`authority`/`policy`/`decision_rights`) — `ExistenceRegistry.
  supersede()`'s own recorded `authority`/`note` (`ADR-0023`'s append-only
  `_supersessions` history), the answer to "who governs this unit's admissibility."

## Decision

We **implement** `engine/ceu/context_binding.py`, following `confidence.py`'s exact
proven shape (declaration builder projecting owned data → `bind_*()` register call →
`resupersede_*()` correction path → `*_of()` point lookup → `*_history()` full
reconstruction) for two kinds against one substrate:

1. **IDENTITY** — bound once per unit (`bind_identity`), keyed by `(form, key)`, stable
   across a unit's own supersession/resurrection cycle (a unit's constitutional
   identity is permanent once minted — the same discipline CEU-001 already applies to
   the unit itself, not something this binding invents).
2. **GOVERNANCE** — re-derived from CEU's own supersession history on every call
   (`bind_governance`/`resupersede_governance`), natural-keyed `(form:key)@{history
   length}` exactly as `confidence.py` keys by `@{version}` — `ContextRegistry.
   supersede` requires a successor's identity to differ from its predecessor's, so a
   real state change (a new `supersede()`/`resurrect()` on the unit) must earn a new
   natural key before its governance projection can be re-asserted.

A resurrection is projected as a state distinct from the supersession it reverses
(governance moves to whoever resurrected the unit) rather than collapsed into the same
assertion — asserting identical substance under two different identities would itself
violate UCXI's own Context Once rule (CXL-06), a real constraint discovered while
designing the resurrection test, not assumed in advance.

Both bindings go through `engine.context.registry.ContextRegistry` — no new registry,
no new taxonomy, no hardcoded category list. `engine.context.taxonomy.ContextTaxonomy.
extend()` (already proven, `ADR-0005`) remains the sole admission path for a future
kind neither this decision nor `confidence.py` declares.

## Consequences

Positive: one CEU unit can now carry more than one bound context kind at once (proven,
not asserted — `test_one_unit_carries_two_bound_context_kinds_at_once`), and the
registry has exercised three of sixteen universal kinds against two of the platform's
entity substrates, direct evidence the mechanism generalizes rather than being a
one-off integration.

Neutral: `ContextRegistry` persistence remains the same pre-existing, disclosed gap
`confidence.py` already named (`engine/lineage/memory-layers.json`, the "context" layer
note) — this decision does not claim to close it; the registry passed to every function
here is the caller's, in memory.

Negative: none identified for the implemented scope. Fourteen of sixteen universal
kinds, and every entity substrate besides CEU and UKDA, remain unexercised — this
decision closes `P4-F-009`'s remainder finding (multi-kind, multi-substrate viability),
not universal coverage, which no finding claims is required.

Reversible: one new module plus one new test file; deleting both fully reverts, and no
other code depends on either existing.

## Compliance

- [x] Non-contradiction with the constitutional/EES corpus asserted (CC-02) — no new
      authority; UCXI-000001 remains sole owner of context registration, CEU-001 sole
      owner of existence.
- [x] Rollback / migration path recorded (CC-04) — see Consequences.
- [x] Traceability links to affected artifacts recorded (CC-05) — `adr/0019`,
      `engine/ceu/context_binding.py`, `engine/tests/ceu/test_context_binding.py`.
- [x] No secret material embedded (SEC-04).

## Validation evidence

- `engine/tests/ceu/test_context_binding.py` — 13 tests: IDENTITY bind/idempotence/
  point-lookup, GOVERNANCE default-to-root-authority, evolution after a real
  `supersede()`, full history reconstruction across supersede+resurrect+resupersede,
  idempotent re-registration, multi-context binding on one unit, no cross-unit
  collision, ontology-shape enforcement not bypassed, duplicate-content refusal not
  bypassed, and unknown-future-context-kind admission re-exercised as this phase's
  acceptance evidence. All passing.
- `engine/tests/ceu/`, `engine/tests/context/`, `engine/tests/knowledge/` — 1177 tests,
  no regression.
