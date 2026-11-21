# UAKOS-CLOSURE-002 · PHASE-002 — Universal Concept Extraction, Canonical Matching, Knowledge-Graph Reconciliation & Repository Enrichment

| Field | Value |
|-------|-------|
| PROGRAM | UAKOS-CLOSURE-002 · PHASE-002 |
| CLASSIFICATION | Concept-graph reconciliation layer over PHASE-001 (derived-truth tooling) |
| AUTHORITY | **NONE — DERIVED TRUTH.** Reflects only evidence physically present at the baseline commit. Fail-closed (TRACK-001). |
| ANSWERS | *Does every constitutional concept exist inside Repository Truth exactly once, with a canonical home, a disposition, traceability, a place in the knowledge graph, and a deterministic enrichment plan for every gap?* |
| GENERATOR | `phase2_engine.py` (stdlib-only, deterministic, re-runnable) |
| INPUTS (reused, read-only) | `closure.json` (PHASE-001 concept model) · `00-BOOK/DATA/relationships.json` (canonical typed knowledge graph) |
| MACHINE MODEL | `phase2.json` |
| DETERMINATION | **FAIL-CLOSED — NOT CLOSED** while any concept is unhomed / duplicated / orphaned. Self-certifies when gaps reach zero. |

---

## 1. Method (Knowledge Once, no fabrication)

PHASE-002 performs **no** new extraction, normalization, or matching. Those are executed once by
`closure_engine.py` (PHASE-001) and serialized to `closure.json`. PHASE-002 **reuses** that single
canonical model and the repository's **existing** canonical typed graph
(`00-BOOK/DATA/relationships.json`, ~11.8k edges) and projects them into the reconciliation views
below. It creates no competing concept store and no second relationship store (UCKO-PRIN-0001).

- **Determinism (UCKO-PRIN-0005):** identical inputs produce byte-identical outputs; the git commit
  is the only baseline stamp (no wall-clock in content).
- **Fail-closed (TRACK-001):** the determination mirrors the PHASE-001 machine determination. No green
  certificate is issued while gaps remain.
- **Boundary (Charter §5):** equivalence is decided **only** by canonical-ID identity. No
  natural-language / embedding semantic inference is performed; ID-less prose is left for human
  canonicalization rather than fabricated into records.
- **Enrichment is a PLAN, never an action:** PHASE-002 never mutates Repository Truth automatically.

## 2. Regenerate

```
make closure-phase2        # runs `closure` then `phase2` (deterministic)
make closure-phase2-gate   # fail-closed gate: non-zero exit while concept gaps remain
# or directly:
python3 00-MASTER/UAKOS-CLOSURE-002/phase2_engine.py [--gate]
```

## 3. Outputs 20-35 (mapping to mission phases 2.1-2.10)

| # | Output | Mission phase | Basis / reuse |
|---|--------|---------------|---------------|
| 20 | Canonical Concept Register | 2.1 extraction | `closure.json` concepts (one row per canonical ID) |
| 21 | Concept Normalization Register | 2.2 normalization | documents the deterministic normalization rules applied by `closure_engine.py` |
| 22 | Canonical Home Register | 2.3 matching | homed/def_homes/exact_homes per concept |
| 23 | Semantic Equivalence Matrix | 2.3/2.4 | ID-identity equivalence classes; NLP boundary disclosed |
| 24 | Duplicate Concept Report | 2.4 | reconciles `07-DUPLICATE-KNOWLEDGE-REPORT.md` at concept level |
| 25 | Concept Reconciliation Matrix | 2.4 | per-concept state + required action |
| 26 | Concept Traceability Matrix | 2.5 | reuses trace tiers (see `05-VISION-TO-REPOSITORY-MATRIX.md`) |
| 27 | Concept Coverage Matrix | 2.8 | family × disposition + homed ratio |
| 28 | Knowledge Graph | 2.6 | reuses `relationships.json` typed graph + evidence-backed concept co-occurrence |
| 29 | Concept Dependency Graph | 2.6 | reuses `relationships.json` dependency edge classes |
| 30 | Concept Relationship Graph | 2.6 | reuses full `relationships.json` typed-edge histogram |
| 31 | Concept Ownership Register | 2.4 | owning zone/program derived from each canonical home |
| 32 | Conversation & Upload Reconciliation | 2.7 | conversation-only / upload-only / in-repo-unhomed; corpus-scan disclosure |
| 33 | Concept Enrichment Register | 2.10 | deterministic PLAN routing every gap to one canonical destination (PLAN ONLY) |
| 34 | Closure & Universal Dashboard | 2.9 coverage | single-pane rollup (closure + universal coverage) |
| 35 | PHASE-002 Completeness Determination | 2.10 certification | fail-closed verdict + success-criteria audit + seal |

## 4. Relationship to PHASE-001 (outputs 01-19)

PHASE-002 **extends**, and does not replace, PHASE-001. Outputs 20-35 cross-reference the PHASE-001
canonical outputs (`04`, `05`, `06`, `07`, `09`, `10`, `14`, `19`) rather than duplicating their
content. If PHASE-001 re-runs (e.g. after external-corpus ingestion changes `closure.json`),
`make closure-phase2` re-projects outputs 20-35 automatically from the new model.

---

*END — UAKOS-CLOSURE-002 · PHASE-002 · AUTHORITY = NONE (DERIVED TRUTH). Concept layer remains fail-closed until every gap is homed; no certificate, traceability, or evidence was fabricated.*



---

# UAKOS-CLOSURE-002 · PHASE-003 — Canonical Implementation Planning, Repository Enrichment & Knowledge Closure Execution (Planning)

| Field | Value |
|-------|-------|
| PROGRAM | UAKOS-CLOSURE-002 · PHASE-003 |
| PURPOSE | Determine HOW every remaining gap becomes Repository Truth without violating Knowledge Once — constitutional PLANS only, never automatic implementation. |
| GENERATOR | `phase3_engine.py` (stdlib-only, deterministic, re-runnable) |
| INPUT (frozen, read-only) | `closure.json` (the ONLY authoritative Phase-003 input) + `phase2.json` (cross-consistency) |
| MACHINE MODEL | `phase3.json` |
| DETERMINATION | **PLANNING-COMPLETE · REPOSITORY NOT-CLOSED (fail-closed).** Repository Truth unchanged. |

## Regenerate

```
make closure-phase3        # runs closure -> closure-phase2 -> phase3 (deterministic)
make closure-phase3-gate   # fail-closed gate: non-zero exit while repository NOT-CLOSED
```

## Outputs 36-48 (mapping to mission STEPS 3.1-3.9)

| # | Output | Mission step | Basis (reuse) |
|---|--------|--------------|---------------|
| 36 | Gap Classification Register | 3.1 | one class per unhomed concept, evidence-precedence (Rejected→Deferred→family) |
| 37 | Canonical Destination Register | 3.2 | one permanent constitutional destination + owner per concept |
| 38 | Dependency Register | 3.3 | wave-gated predecessor per concept |
| 39 | Implementation Dependency Graph | 3.3 | acyclic class/wave DAG (no cycles) |
| 40 | Execution Wave Register | 3.4 | one of Waves 1-7 / F per concept |
| 41 | Repository Impact Assessment | 3.5 | per-class impact estimates (Derived/Projected; no writes) |
| 42 | Priority Register | 3.6 | priority = pure function of constitutional wave |
| 43 | Implementation Contract Register | 3.7 | one contract per class, bound to every concept |
| 44 | Repository Enrichment Execution Plan | 3.8 | master per-concept plan (ID·dest·owner·deps·wave·priority·evidence·validation·cert·artifacts) |
| 45 | Closure Projection Report | 3.9 | wave-by-wave residual, labelled Measured / Derived / Projected |
| 46 | Repository Readiness Dashboard | — | readiness rollup |
| 47 | Knowledge Closure Roadmap | — | ordered wave-gated roadmap |
| 48 | Phase-003 Determination | — | fail-closed verdict + success-criteria audit + seal |

## Verified baseline (frozen input)

506 concepts · 396 homed · **110 unhomed** (108 conversation-only + 2 in-repo-unhomed) · 0 duplicate · 0 orphan.

## Plan summary (Derived)

- **Classes:** Deferred 96 · Missing Governance 4 · Missing Roadmap 3 · Missing Architecture 2 · Missing Constitution 2 · Missing Specification 2 · Missing Registry 1.
- **Waves:** W1 = 2 · W2 = 2 · W3 = 8 · W5 = 2 · W-F = 96.
- **Priorities:** Critical 2 · High 10 · Medium 2 · Future 96.
- **Projected (not measured):** active Waves 1-7 home 14 concepts; Wave F registers 96 as governed DEFERRED entries; projected unhomed at full authorized execution = 0. Repository stays **NOT-CLOSED** until measured after execution.

*END — PHASE-003 delivers the complete deterministic roadmap from NOT-CLOSED toward evidence-backed constitutional closure. Repository Truth unchanged; nothing implemented automatically; no certainty fabricated.*
