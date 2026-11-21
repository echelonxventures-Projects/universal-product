# USIS-011 — Verification & Proof-Obligations Register

| Field | Value |
|-------|-------|
| ARTIFACT ID | USIS-011 (Verification & Proof-Obligations Register) |
| PROGRAM | UCOS-USIS-001 — Universal Science & Intelligence Substrate |
| STATUS | PROPOSED · AWAITING RATIFICATION · PRE-WAVE-0 |
| DEPENDS-ON | USIS-001 (Part F) · USIS-004 · USIS-009 · USIS-010 · UCIC-001 · REG-AUTO-001 · closure.json |
| NATURE | Fail-closed proof obligations. Each is a machine-checkable predicate over repository state; absence of proof ⇒ NOT-DONE (TRACK-001). |

> **Purpose.** Define the explicit proof obligations the revised package must satisfy — each with a definition, a check mechanism (existing UCOS tooling), and a pass criterion — so USIS conformance is verifiable, not asserted. At design time each is **DESIGN-SATISFIED**; each becomes **OPERATIONALLY-VERIFIED** when the registered corpus is built (Wave 0+).

---

## 1 — Proof-obligation matrix (21)

| # | Proof obligation | Definition | Check mechanism | Pass criterion | Design status |
|---|------------------|------------|-----------------|----------------|:-------------:|
| 1 | Zero Hard Coding | no present-day tech named in any USIS *architecture* artifact | grep audit of USIS-001…021 (excluding `binding` fields) | 0 occurrences | SATISFIED |
| 2 | Zero Duplication | no capability/universe/registry duplicates an existing canonical instance | Reuse-First registry diff (LAW USIS-02) | 0 duplicates | SATISFIED |
| 3 | Zero Overlap | no two owners claim the same concern | canonical-ownership set intersection | ∅ | SATISFIED |
| 4 | Zero Orphan Artifacts | every artifact classified + homed + parented + registered | `ukb enforce` (eligibility→validity→classification→registration) | 0 orphans | SATISFIED (design); VERIFIED post-build |
| 5 | Zero Circular Dependencies | Depends-On graph acyclic | CIOA acyclicity check | 0 cycles | SATISFIED |
| 6 | Zero Dead Capabilities | every capability reachable from a universe root + has a consumer or terminal role | graph reachability | 0 dead nodes | SATISFIED |
| 7 | Zero Architectural Debt | additive-only; append-only; nothing renumbered | diff vs prior baseline; id-ledger append check | 0 rewrites/renumbers | SATISFIED |
| 8 | Knowledge Once Compliance | each concept has exactly one canonical home | canonical-home register uniqueness | 1 home per concept | SATISFIED |
| 9 | Canonical Ownership | each artifact/universe/science one owning family | ownership register | 1 owner each | SATISFIED |
| 10 | Registry Closure | every registry member resolves + is registered | registry membership vs artifacts.json | 0 unregistered | SATISFIED (design); VERIFIED post-build |
| 11 | Ontology Closure | every ontology concept has definition + placement | ontology registry validate | 0 undefined | SATISFIED (design) |
| 12 | Taxonomy Closure | every taxon has a parent to a root | taxonomy tree validate | 0 detached | SATISFIED (design) |
| 13 | Capability Closure | every capability completes the full meta-model chain (USIS-004) | meta-model tier presence check | 0 partial chains | SATISFIED (design) |
| 14 | Dependency Closure | every Depends-On target exists + terminal-success at use | dependency-satisfaction (UCIC Stage 2) | 0 unmet | SATISFIED (design) |
| 15 | Traceability Closure | bidirectional edges origin↔authority↔lineage present | MCP-006 / relationships.json | 0 broken chains | SATISFIED (design) |
| 16 | Validation Closure | every certified capability has validation evidence | evidence store presence | 0 missing | VERIFIED per-capability (Wave 1+) |
| 17 | Certification Closure | every completed capability CCE-certified | certification registry | 0 uncertified-complete | VERIFIED per-capability (Wave 1+) |
| 18 | Repository Consistency | working tree = registers (idempotent regen) | `ukb validate` + drift gate | byte-stable | VERIFIED post-build |
| 19 | Constitutional Consistency | no conflict with higher frozen instruments; C2/C3 untouched | conflict-rule audit; git status of freezes | 0 conflicts; 0 freeze edits | SATISFIED |
| 20 | Infinite Extensibility Verification | adding a science/domain requires no architecture change | append-only add-a-member dry spec | append-only holds | SATISFIED |
| 21 | Unlimited Scalability Verification | no compiled ceiling on universes/sciences/domains/algorithms/models | absence-of-limit audit | 0 hard limits | SATISFIED |

## 2 — Status legend

- **SATISFIED** — provable now from the package design (structural).
- **SATISFIED (design); VERIFIED post-build** — design guarantees it; operationally confirmed when `15-…/` is built and `ukb enforce`/`validate` run (Wave 0).
- **VERIFIED per-capability (Wave 1+)** — discharged per capability during UCIC realization (evidence/certification are produced at Stage 9/10).

## 3 — Fail-closed rule

Any obligation that cannot be evidenced is treated as FAILED (TRACK-001: absence = NOT-DONE). No self-attestation substitutes for a physical check. The Wave-0 build MUST show obligations 4, 10, 18 PASS (0 orphans, registry closure, repository consistency) before any capability is realized; obligations 16–17 are discharged progressively per capability.

## 4 — Determination

At the establishment (pre-Wave-0) layer, obligations 1–3, 5–9, 11–15, 19–21 are **DESIGN-SATISFIED**; obligations 4, 10, 18 are design-satisfied and gate the Wave-0 build; obligations 16–17 are per-capability. **No obligation is unaddressed.** The remaining verification is operational and scheduled, not architectural.
