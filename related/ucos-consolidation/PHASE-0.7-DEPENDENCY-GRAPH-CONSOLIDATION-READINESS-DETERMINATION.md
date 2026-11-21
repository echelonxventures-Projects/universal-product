# PHASE-0.7 DEPENDENCY GRAPH CONSOLIDATION READINESS DETERMINATION

> **Mission:** UCOS Ω∞ Universal Evolution Foundation, Phase 0.7 — Dependency Graph Consolidation Discovery
> **Mode:** READ-ONLY discovery and determination. No implementation, no graph rewriting, no new dependency system, no registration, no modification of certified fixed-point evidence.
> **HEAD at time of determination:** `ed74d2d9090ab6056722342ebe5d501ee729cb9e`
> **Date:** 2026-08-13
> **Method:** Direct repository reads — source code, git history per candidate artifact, Makefile targets, `.gitignore` — not inference from the earlier Phase 0 gap analysis, which this determination corrects on one material point (see §2).

---

## Executive Summary

The Dependency Graph capability is **not fragmented in the way Phase 0's original gap analysis described.** That analysis characterized it as "one live authority plus 25+ static, competing snapshots." Direct investigation this phase finds something more precise and less alarming: **one governed, canonical object-level model, two additional live and actively-maintained systems that answer genuinely different questions at different grains from different sources, and a body of static historical documents that are evidence of closed programmes, not competing truth.** The real gap is narrower than originally stated: **the two additional live systems are not recognized by the existing Constitutional Authority Alignment (CAA) governance framework**, the same class of gap Phase 0.6 found and closed for CMG↔UCKP — not a missing capability, not a duplicate registry, and not something requiring a new federation layer.

---

## 1. Current State

The object-level dependency knowledge Phase 0 identified (~9,550 dependency-typed edges) is real, live, and already governed: it lives inside `engine/uckp/graph.py` (the declared model owner under `UCKP-ART-07`) and its population, `00-MASTER/UCOS-UGA-001/04-RELATIONSHIP-GRAPH.json`, protected by the standing invariant `CAA-INV-05 EXACTLY_ONE_RELATIONSHIP_GRAPH_MODEL_OWNER` (0 violations, confirmed live this session). This part of the capability was never actually missing an owner.

What Phase 0 did not check closely enough: whether the 25+ other files carrying "dependency graph" in their name are all the same kind of thing. They are not.

---

## 2. Dependency Source Inventory

| Artifact ID / Location | Owner | Purpose | Data Model / Grain | Source | Consumers | Evidence of liveness | Duplication relationship |
|---|---|---|---|---|---|---|---|
| **Object relationship graph** — `engine/uckp/graph.py` + `00-MASTER/UCOS-UGA-001/04-RELATIONSHIP-GRAPH.json` | `engine/uckp` (model), UGA (population) | The canonical object-to-object dependency/relationship truth | Object-level; every object a node, every dependency an edge (`UCKP-ART-07`) | Declared metadata in the object registry | `verify.sh` UGA gate, CAA alignment binding, RIB's substrate references | Actively regenerated every `uga_engine.py run`, e.g. this session | **Canonical.** No rival exists at this grain. |
| **RIE program-dependency graph** — `intelligence/rie/engine.py::_dependency_graph()` → `intelligence/UCOS-RIE-DEPENDENCY-GRAPH.json` | `intelligence.rie` (RIE — Repository Intelligence Engine) | Program→program dependency rollup for repository-health/progress reporting | Program-level (aggregated); `authority: "NONE (derived truth)"` | `00-BOOK/DATA/artifacts.json`'s declared `dependencies` field per artifact, independently re-aggregated | Part of the automatic BOOTSTRAP/prerequisite chain (`-m intelligence.rie build`); watched change repeatedly across this session's `verify.sh`/Phase-8 runs | **Live, distinct grain, distinct source.** Not bound into the CAA framework. |
| **RPI module-import graph** — `platform/repository_intelligence/substrate.py` (AST-based) + `graph.py` → `.runtime/repository-intelligence/UCOS-RPI-DEPENDENCY-GRAPH.{json,dot,mmd}` | `platform.repository_intelligence` (RPI, UCOS-EPIC-014) | Module-to-module dependency graph from actual source-code imports | Module-level; parsed via Python `ast` from real `import` statements — not declared metadata | `make repo-intel-emit/scan/certify/verify` (manual, **not** part of the automatic `verify.sh`/Phase-8 chain) | Last touched 2026-08-12 (one day before this determination) — actively maintained, but its output directory (`.runtime/`) is explicitly `.gitignore`d | **Live, distinct grain, distinct and arguably more ground-truth source (actual imports, not declared metadata).** Output self-disclaims as non-canonical by never being tracked. Not bound into the CAA framework. |
| **~20 static per-programme snapshots** — e.g. `00-MASTER/UAKOS-CLOSURE-002/29-CONCEPT-DEPENDENCY-GRAPH.md`, `39-IMPLEMENTATION-DEPENDENCY-GRAPH.md`; `00-MASTER/UAKOS-PHASE-004/10-UNIVERSAL-GAP-DEPENDENCY-GRAPH.md`; `00-MASTER/UCOS-USIS-WAVE1/03-WAVE1-DEPENDENCY-GRAPH.md` (+3 mission-level siblings); `00-MASTER/UCOS-RIB-001/05-DEPENDENCY-GRAPH.md`; root `03-DEPENDENCY-GRAPH.md`, `03-IMPLEMENTATION-DEPENDENCY-GRAPH.md`; and ~12 further programme-specific files | Each now-closed or completed programme, individually | Point-in-time dependency snapshot at that programme's own closure | Ad hoc per document; markdown, hand-structured | Whatever the closed programme measured at the time, never re-derived since | None currently consumes these live | Confirmed via git history: `UAKOS-PHASE-004`'s copy last touched 2026-08-01, `UCOS-USIS-WAVE1`'s last touched 2026-07-24 — both untouched since, no regeneration path exists for either. `00-MASTER/UCOS-RIB-001/05-DEPENDENCY-GRAPH.md` is confirmed **not** part of RIB's own live-regenerated surface set (unlike `rib.json`, `01-REPOSITORY-INVENTORY.md`, etc., which this session watched RIB rewrite repeatedly) — despite sitting inside RIB's active programme directory, this specific file is itself frozen. | **Historical evidence, not live truth.** Not duplicates of the canonical graph in the sense of competing for the same present-tense answer — they document what a now-closed programme measured, once. |

---

## 3. Canonical Ownership Determination

- **Does canonical ownership already exist?** Yes, for the object-level question — `engine/uckp/graph.py` + UGA's population, governed by `CAA-INV-05`. This has not changed and required no new determination.
- **Is ownership fragmented?** Not in the sense of two owners competing to answer the *same* question. It is **unrecognized**, not fragmented, for the two other live systems (RIE, RPI) — each answers a different, real question (program-level declared rollup; module-level actual-import scan) that the object-level graph does not answer and was never meant to.
- **Is a consolidation owner required?** No new owner is required. What is required is a **governance recognition act** — the same shape of fix Phase 0.6 applied to CMG↔UCKP — declaring each live system's scope and non-competing status inside the existing CAA framework, so "is this a rival authority" stops being an open question answerable only by reading source code (as this determination just did).

---

## 4. Dependency Graph Comparison

| | Object graph | RIE rollup | RPI scan |
|---|---|---|---|
| Grain | Object | Program | Module |
| Source | Declared metadata (registry) | Declared metadata (`artifacts.json`) | Actual source code (AST) |
| Governed by CAA? | Yes (`CAA-INV-05`) | No | No |
| Tracked/canonical output? | Yes | Yes | **No** — `.gitignore`d |
| Gate-integrated? | Yes (UGA gate) | Yes (`verify.sh` prerequisite chain) | No (manual `make repo-intel-*` only) |
| Overlap with the other two | — | Could, in principle, diverge from the object graph's rolled-up-to-program view; not currently cross-checked | Could diverge from *both* declared-metadata views, since it measures actual imports; this divergence would be a genuinely useful signal (stale declared dependencies), not noise, but nothing currently surfaces it |
| Missing edges / stale representations | None found | None found — actively regenerated | None found — actively regenerated |
| Authoritative source | **For the object-level question: yes, unambiguously.** For "what does the code actually import" or "what do programs depend on in aggregate": no single instrument claims final authority, and none has been asked to. |

No divergence between the three live systems was checked numerically in this pass (that would be implementation, not discovery) — the finding here is that **no mechanism currently checks for divergence at all**, which is itself part of the governance gap.

---

## 5. Gap Classification

| Class | Finding |
|---|---|
| **A. Missing capability** | **None.** Every dependency question this phase examined already has at least one live, working answer. |
| **B. Duplicate capability** | **Borderline, not confirmed.** RIE and RPI both compute "a dependency graph" and RPI's broader module set (gap detection, duplicate detection, ownership determination, conflict detection) substantially overlaps RIE's own analytical scope by name and intent, even though their concrete outputs differ in grain and method. This is a real *engineering-effort* duplication risk — two independently coded systems performing the same *class* of analysis — even though it is not byte-level output duplication. Worth a dedicated, separate look; **not resolved by this phase**. |
| **C. Fragmented capability** | **Yes, for the ~20 static historical snapshots specifically** — genuinely fragmented across many programme directories with no index. Per instruction, this is **not** classified as missing capability: the historical data is not needed live, and nothing currently needs it consolidated into one place to function. |
| **D. Governance gap** | **Yes — the primary finding.** Neither RIE's program-rollup nor RPI's module-scan is bound into the CAA framework the way the object-relationship-graph model is. No declared rule states which of the three live views answers which question, or that the historical snapshots are deliberately non-live rather than accidentally neglected. |
| **E. Evidence gap** | **Minor.** The historical snapshots are evidence of past programme states in substance, but none is formally classified that way (contrast with RIB/AEE, which already hold an explicit `EVIDENCE` role in the CAA binding). |
| **F. Ownership gap** | **Yes, specifically for RIE's and RPI's dependency-view outputs** — no CAA-bound owner declaration exists for either, even though both have located, active, identifiable owning modules. |

---

## 6. Architecture Assessment — Consolidation Strategy Options

### Option A — Promote the existing live relationship graph as sole canonical source

- **Architectural correctness:** High for the object-level question (already true). Incomplete as a full answer: it does not and should not try to answer the program-level or module-level questions RIE and RPI already answer differently and legitimately.
- **Migration impact:** Low — no data movement; would require RIE and RPI to either defer to it (impossible without collapsing their distinct grains) or be formally recognized as subordinate projections of it (partially true for RIE's declared-metadata view; not true for RPI's independently-sourced AST scan, which answers a different question entirely).
- **Duplication risk:** Low if scoped correctly; high if forced to make the object graph "the" answer to questions it doesn't actually answer.
- **Governance impact:** Extends `CAA-INV-05`'s existing role.
- **Implementation complexity:** Low, but only partially solves the actual finding.

### Option B — Create a dependency federation layer

- **Architectural correctness:** Low. A new, fourth (or fifth) independently-built aggregation system is precisely the anti-pattern — "Reuse Before Create," "Zero Duplication" — this whole mission exists to prevent, and precisely what this phase's own instructions forbid ("Do NOT create duplicate dependency registries... introduce new graph models without ownership determination").
- **Migration impact:** High — would need to wrap or ingest all three existing producers.
- **Duplication risk:** High — ironically becomes the "eighth root" the CAA philosophy (`engine/uckp/alignment.py`'s own docstring) was built specifically to prevent.
- **Governance impact:** Requires an entirely new authority declaration.
- **Implementation complexity:** High.
- **Not recommended**, and inconsistent with this phase's own constraints.

### Option C — Maintain the current model, add stronger governance

- **Architectural correctness:** Highest. Matches what this investigation actually found: three systems that do not compete, sitting undocumented as if they might.
- **Migration impact:** Lowest — zero data movement, zero code change to any of the three systems.
- **Duplication risk:** Lowest — resolved by declaration, the same proven mechanism Phase 0.6 used for CMG↔UCKP (`ORTHOGONAL` role + `CAA-INV-08`-style safeguard), reused rather than re-invented.
- **Governance impact:** Extends the existing CAA framework only; no new registry, no new authority.
- **Implementation complexity:** Lowest.
- **Recommended.**

---

## 7. Recommended Direction

**Option C, precisely scoped:**

1. Extend the CAA binding (`00-BOOK/DATA/constitutional-authority-alignment.json` + `engine/uckp/alignment.py`) with two new `subordinate_instruments` entries — one for RIE's dependency-graph producer, one for RPI's — each declared with a role that accurately reflects what this determination found: a bounded, non-competing derived view (the existing `PROJECTION` role fits both; no new role is needed this time, unlike CMG which genuinely needed the new `ORTHOGONAL` role because it claimed a *different kind* of authority, not a *derived view*).
2. Produce a single, lightweight index of the ~20 historical snapshots (a table, not a registry) so they are discoverable as evidence rather than silently scattered — this document's own §2 inventory is close to a first draft of that index.
3. Explicitly **defer** the RIE/RPI capability-overlap question (Gap Class B) to its own, separate, dedicated look — it is a different question (engineering-effort duplication) from dependency-graph consolidation (data/authority duplication), and conflating them risks the same scope growth this session saw in the CMG/UCKP work.
4. Do **not** build a federation layer, do not move any data, do not touch certified Phase-8/9 evidence.

---

## 8. Required Preconditions

- None blocking. Unlike the CMG↔UCKP reconciliation, this does not depend on Tier T1 or any external ratification — it is a same-tier extension of an already-active, already-proven binding mechanism (`CAA-INV-01..08`), which is entirely within this repository's own authority to maintain.
- The only prerequisite is explicit approval of the recommended direction in §7 before any file is touched, consistent with this phase being discovery-only.

---

## 9. Implementation Readiness

| Item | Ready? |
|---|---|
| Pattern to reuse (CAA binding extension) | **Yes** — proven twice this session (identity plane, CMG↔UCKP) |
| Exact insertion points | **Not yet confirmed** — would need the same "read current code, confirm exact insertion points, do not guess" pass Phase 0.6 applied before any edit |
| Risk of scope growth | **Moderate** — flagged explicitly in §7; recommend implementing strictly the two `PROJECTION` bindings and the index, nothing more, in one pass |
| Dependency on other open gaps | **None** — independent of Certification taxonomy and Knowledge Registry reconciliation |

---

## 10. Risks

1. **Scope creep into Gap Class B** (RIE/RPI capability overlap) — the two questions are adjacent enough that an implementer could drift from "bind the existing outputs" into "should RPI even exist as a separate system," which is a materially larger and different decision this phase does not make.
2. **The historical-snapshot index could be read as itself a new registry** if not scoped carefully as a plain descriptive table (matching how `00-BOOK/DATA/generated-artifact-registry.json` and the CAA binding already coexist as data, not new authorities).
3. **RPI's non-canonical (`.gitignore`d) status might be intentional-but-undocumented **or** accidental drift** — this determination could not establish which from the evidence available; the CAA binding entry for RPI should record this as an open question rather than assert either reading with more confidence than the evidence supports.

---

## Answer to the phase's stated question

**"Where does dependency truth belong, and what is the minimum evolution required to make it canonical?"**

Object-level dependency truth already belongs, unambiguously, to `engine/uckp/graph.py` and its UGA population — that was never actually in question. Program-level and module-level dependency views belong, respectively, to RIE and RPI, each legitimately, at their own grain, from their own source. The minimum evolution required is not consolidation of data or authority — it is **two `PROJECTION`-role entries in the already-existing CAA binding**, plus a plain descriptive index of the historical snapshots. No new registry, no new graph model, no migration, and no change to certified fixed-point evidence.

**This phase ends here, with determination only.** Waiting for direction on whether to proceed with the two-binding-plus-index implementation in §7, or hold.
