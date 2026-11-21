# 01 — USIS-005 CONTEXT ASSIMILATION

**Mission:** UCOS Ω∞ Wave 1 · Mission 5 — USIS-005 Context Assimilation Gate
(READ • ANALYZE • DERIVE — **no implementation**).
**Nature:** Read-only constitutional governance. Outputs are operational memory
under `00-MASTER/` (scan-excluded; not registered; not committed).
**Baseline:** `governance-reconciliation` @ **`ab78f35`** (USIS-003 canonically
established), founding chain USIS-GOV-000 → USIS-001 → USIS-002 → USIS-004 → USIS-003.

---

## 1 — Assimilated repository state (verified this session, committed evidence)

| Fact | Value | Evidence |
|---|---|---|
| HEAD | `ab78f35` (`USIS-003: register Universal Science Catalog`) | `git log` |
| Registered artifacts | **1006** | `ukb enforce` |
| Unregistered / unclassified / invalid | **0 / 0 / 0** | `ukb enforce` |
| `register.sh --guard` | **PASS (exit 0)** | this session |
| Certification / twin | `ukbx certify` **10/10** · `ukbx twin --check` **7/7** (C-07 acyclic) | this session |
| Determinism (guard scope) | SHA-256 `4d97626235722c2bdbc61ca431b813c462a5af3f00425d620470651c3d86504d` | byte-stable |
| Registered USIS artifacts | `USIS-GOV-000`(…001), `USIS-001`(…002), `USIS-002`(…003), `USIS-004`(…004), `USIS-003`(…005) | `artifacts.json` |

## 2 — Derived constitutional identity of USIS-005 (no assumptions — committed evidence)

The mission supplied **no content descriptor** for USIS-005; its identity is
**derived** from committed evidence. Three independent committed sources agree:

1. **Canonical artifact sequence** (structure-spec blueprint §3): `USIS-005 |
   …-THEORY / …-ONTOLOGY / …-TAXONOMY (foundation) | areas 01/02/03`.
2. **Roadmap USIS-012 Wave 1** (USIS-001…005): "Constitution → Universe Catalog →
   Science Catalog → Meta-Model → **Theory/Ontology/Taxonomy**. Establishes the
   substrate hypergraph and the meta-model spine."
3. **USIS-011 proof obligations 11 (Ontology Closure) & 12 (Taxonomy Closure)** —
   the closure predicates USIS-005 discharges at the foundation level.

**Determination (D-B):** **USIS-005 = the Theory / Ontology / Taxonomy Foundation
of USIS** — the substrate meaning foundation authored under areas `01-THEORY/`,
`02-ONTOLOGY/`, `03-TAXONOMY/`. It is the fifth and final capability of the Wave-1
**Substrate Foundation** (USIS-001…005).

### 2.1 — Naming-ambiguity resolution (structure spec vs T/O/T)

The establishment-package file `05-USIS-CANONICAL-REPOSITORY-STRUCTURE-SPECIFICATION.md`
is titled "Repository Structure Specification," which could be mistaken for the
canonical USIS-005 artifact. Committed evidence resolves this decisively:

- The **canonical artifact-number → content** mapping (§3) is NOT 1:1 with the
  package file numbers after USIS-004 (e.g. canonical USIS-021 = Master-Registry).
  §3 assigns canonical **USIS-005 to Theory/Ontology/Taxonomy**, not to the
  structure spec.
- The structure-spec file's own **§6** states it "performs no registration … the
  authoritative blueprint the governed Wave-0 build follows." It is **build
  guidance**, already consumed by Wave 0 (committed `config.py` routing +
  the physical `15-…/` tree), **not** a canonical corpus artifact.
- The repository structure is **already canonically encoded** in committed
  `config.py` (`^15-UNIVERSAL-SCIENCE-INTELLIGENCE/ → USIS/USIS/VOL-024`) and the
  physical tree. Registering a structure-spec corpus artifact would **duplicate**
  that canonical encoding (violating Knowledge-Once / LAW USIS-02).

Therefore the structure spec is **REFERENCE-ONLY operational memory**; the
canonical USIS-005 capability is the **Theory/Ontology/Taxonomy foundation**.

## 3 — Constitutional purpose (derived)

USIS-005 establishes the **substrate meaning foundation** — the constitutional
homes and governing rules for:
- **`01-THEORY/`** — the theory of universal science & intelligence (the substrate's
  explanatory foundation);
- **`02-ONTOLOGY/`** — the substrate ontology (concepts, relations) — **Ontology
  Closure** (USIS-011 obl 11);
- **`03-TAXONOMY/`** — the taxonomy of sciences/universes/domains/algorithms/models
  — **Taxonomy Closure** (USIS-011 obl 12).

It provides the **hypergraph of meaning** over which the universes (USIS-002) and
sciences (USIS-003) are organized, conforming to the USIS-004 meta-model tiers
6 (Theory) / 7 (Ontology) / 8 (Taxonomy). It **populates no individual concept,
theory, or taxon of a specific universe/science** — those are per-member Wave-3
work; USIS-005 establishes the foundation/framework and its closure rules.

## 4 — Canonical ownership & parent universe

| Aspect | Determination | Evidence |
|---|---|---|
| Owning program / family | USIS / UNIVERSAL-SCIENCE-INTELLIGENCE / VOL-024 | `config.py:275` |
| Ownership scope | the substrate **Theory/Ontology/Taxonomy foundation** — a constitutional foundation instrument spanning areas 01/02/03; owns the meaning-foundation, not any single universe's content | §3; roadmap; USIS-011 obl 11/12 |
| Parent (structural) | USIS program root `USIS-GOV-000` (`UCOS-USIS-000001`), non-chained (USIS-001…004 precedent) | `config.py` PROGRAM_ROOTS |
| Reuse anchor (ontology) | U24 Knowledge / MIP Part 19 knowledge ontology registry — **REFERENCE**, never fork (LAW USIS-02) | USIS-002 row 17; USIS-009 §2 |
| Authority | **NONE — DERIVED.** Operationalizes LAW USIS-00 (ontology/taxonomy integration facets) + USIS-004 meta-model tiers 6/7/8 | USIS-001; USIS-004 |

## 5 — Assimilation completeness

Every fact is derived from committed repository evidence re-verified this session
(git state, guard run, `config.py`, `artifacts.json`, corpus tree, and
operational-memory blueprints 04/05/11/12 + USIS-001 laws). Context Assimilation
for USIS-005 is **complete**; its identity, purpose, ownership, and dependency
closure are established (see `02`–`05`).
