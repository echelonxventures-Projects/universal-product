# PHASE-0.7 DEPENDENCY GRAPH GOVERNANCE BINDING DETERMINATION

> **Mission:** UCOS Ω∞ Universal Evolution Foundation, Phase 0.7 — Dependency Projection Governance Binding
> **Mode:** Governance alignment only. No new dependency system, no graph rewriting, no migration, no change to certified fixed-point evidence.
> **HEAD before this change:** `ed74d2d9090ab6056722342ebe5d501ee729cb9e`
> **Date:** 2026-08-13
> **Precondition satisfied:** Phase 0.7 discovery (`PHASE-0.7-DEPENDENCY-GRAPH-CONSOLIDATION-READINESS-DETERMINATION.md`) — Option C selected.

---

## 1. Implementation Summary

Before editing anything, the existing registration pattern from Phase 0.6 was re-inspected directly (not from memory): `00-BOOK/DATA/constitutional-authority-alignment.json`'s `relationship_graph_resolution` section already carries a `projections` array, purpose-built for exactly this case, currently holding one entry (UGA's `04-RELATIONSHIP-GRAPH.json`). Both candidate files were checked for their actual current `authority` field before deciding a mechanism:

- `intelligence/UCOS-RIE-DEPENDENCY-GRAPH.json` → `"authority": "NONE (derived truth)"` — already matches the `NONE` disclaiming prefix.
- `.runtime/repository-intelligence/UCOS-RPI-DEPENDENCY-GRAPH.json` → `"authority": "ENGINEERING-EXECUTION-ONLY"` — already matches the `ENGINEERING-EXECUTION-ONLY` disclaiming prefix.

This ruled out the `subordinate_instruments` + `constitutional_superior` binding mechanism (the one used for CMG in Phase 0.6): that mechanism requires the bound file itself to carry a `constitutional_superior` block, which would require modifying the RIE/RPI generators — out of scope, and unnecessary, since both already self-disclaim correctly under the existing scan. The correct, existing, already-designed mechanism was the `projections` array — confirmed, before editing, to be pure descriptive data with zero references anywhere in `alignment.py`'s `verify_binding()`, so extending it carries no risk of a new validation requirement appearing unexpectedly.

## 2. Registrations Created

**A. RIE Dependency Projection** and **B. RPI Dependency Projection** — both appended to the existing `relationship_graph_resolution.projections` array (now 3 entries, was 1):

| Field | RIE entry | RPI entry |
|---|---|---|
| `projection` | `intelligence/UCOS-RIE-DEPENDENCY-GRAPH.json` | `.runtime/repository-intelligence/UCOS-RPI-DEPENDENCY-GRAPH.json` |
| `producer` | `intelligence/rie/engine.py` | `platform/repository_intelligence/substrate.py` |
| `role` | `PROJECTION` (existing role, unchanged) | `PROJECTION` (existing role, unchanged) |
| `measures` | Program-to-program rollup from declared `dependencies` in `artifacts.json` | Module-to-module graph from actual source imports (AST) |
| `$disclaim` | Cites the live `NONE` field and its CMG-000001 XVI.2 basis | Cites the live `ENGINEERING-EXECUTION-ONLY` field, its CEP-003 I.3 basis, and the `.gitignore` exclusion |

No new `AuthorityRole` was created — `PROJECTION` already existed and fits exactly (per its own definition: "a generated or authored view of what the objects already are; it may state repository reality and may never state law").

**Historical Dependency Evidence Index** — a new `dependency_evidence_index` object added as a sibling to `relationship_graph_resolution` (same file, same nesting level, matching house style). Declares, verbatim: *"No historical snapshot listed here may serve as a dependency authority."* Uses the existing `EVIDENCE` role (`UCKP-ART-16`) — no new role created. Catalogues all ~20 static files found in Phase 0.7 discovery, grouped by location, each carrying a `programme_state` note. Two entries' frozen status is backed by cited git history (`UAKOS-PHASE-004`: last touched 2026-08-01; `UCOS-USIS-WAVE1`: last touched 2026-07-24).

## 3. Files Changed

| File | Change |
|---|---|
| `00-BOOK/DATA/constitutional-authority-alignment.json` | Two entries appended to `relationship_graph_resolution.projections`; one new `dependency_evidence_index` object added |

No other file touched. No source code modified. No `.py` file changed.

## 4. Ownership Confirmation

- Object-level dependency graph: `engine/uckp/graph.py` (model), `00-MASTER/UCOS-UGA-001/04-RELATIONSHIP-GRAPH.json` (population) — **unchanged, still sole owner.**
- RIE's program-level rollup: now explicitly recognized as a `PROJECTION` of that same model, at a different grain — **not a rival, not a second owner.**
- RPI's module-level scan: now explicitly recognized as a `PROJECTION` of that same model, at a different grain and from a different source (actual imports) — **not a rival, not a second owner.**
- ~20 historical snapshots: now explicitly recognized as `EVIDENCE`, never authority.

**One dependency authority. Three recognized, non-competing projections/evidence classes. Zero new owners.**

## 5. Projection Boundaries

Per the `may_never` clause on both new entries: neither RIE's nor RPI's dependency output may declare a relationship kind absent from the model, or claim authority over the object-level question the model already answers. Both boundaries were already true in practice (confirmed by their own `authority` fields); this determination makes them explicit and discoverable rather than something only visible by reading source code.

## 6. Historical Evidence Classification

All ~20 files classified as `EVIDENCE` (`UCKP-ART-16`), never `PROJECTION` and never any authority-holding role. The explicit declaration — *"No historical snapshot listed here may serve as a dependency authority"* — is the literal text requested, present verbatim in the binding.

## 7. Validation Results

| Check | Result |
|---|---|
| JSON well-formed | **PASS** |
| `engine.uckp.alignment.verify_binding()` (direct call) | **PASS** — `()`, zero findings |
| `uga_engine.py gate` — `CAA-INV-01` through `07` | **PASS**, 0 violations each. `CAA-INV-05` (`EXACTLY_ONE_RELATIONSHIP_GRAPH_MODEL_OWNER`) unchanged at 0 violations, 6 measured — confirms the new projections did not disturb single-ownership. `CAA-INV-02`/`03` unchanged — confirms the new entries created no false "claims authority" or "subordinate claims independence" findings. | 
| `00-BOOK/tools/ukb.py enforce --pre` | **PASS** — `ENFORCEMENT PASSED`, no unregistered/invalid artifact, no reconciled-set drift |
| `00-BOOK/tools/ukb.py validate` | **PASS** — schema and referential integrity intact |
| Phase-8/9 fixed-point suite | **Not rerun** — not required for a pure-data governance addition with zero effect on measured identities; explicitly excluded by your instruction |

**Governance validation against the four stated requirements:**
1. Exactly one dependency relationship-graph owner — **confirmed, `CAA-INV-05` unchanged, 0 violations.**
2. Projections do not claim authority — **confirmed by their own pre-existing `authority` fields (`NONE`, `ENGINEERING-EXECUTION-ONLY`), now also explicitly recorded.**
3. Evidence remains separate from truth — **confirmed; the new evidence index is role `EVIDENCE`, explicitly disclaimed from authority, structurally separate from `relationship_graph_resolution`.**
4. No duplicate object model introduced — **confirmed; zero new roles, zero new registries, zero new files, zero code changes.**

## 8. A finding surfaced during validation (out of scope for this change, flagged not fixed)

Running the live gate to validate this change surfaced something unrelated to dependency projections: `uga_engine.py`'s stdlib-only production gate hard-codes `CAA-INV-01` through `CAA-INV-07` (`grep 'add("CAA-INV'` shows exactly seven `add()` calls) — **`CAA-INV-08`, the `ORTHOGONAL`-role safeguard added in Phase 0.6, has no corresponding check in the live gate.** It is currently enforced only via `engine.uckp.alignment.verify_binding()`, which is exercised by pytest but is not part of the stdlib-only path `verify.sh`/`make rib-gate` actually run in production. This is a real, live coverage gap from the earlier Phase 0.6 work, discovered as a side effect of this phase's validation, not introduced by it. Left unfixed per this task's explicit scope ("only implement governance alignment [for dependency projections]"); recorded here so it isn't lost.

## 9. Final State

- **One dependency authority**: `engine/uckp/graph.py` + `04-RELATIONSHIP-GRAPH.json`, unchanged.
- **Multiple governed projections**: 3 (UGA population, RIE rollup, RPI scan), all role `PROJECTION`, all self-disclaiming, all now explicitly recorded.
- **Historical evidence, formally classified**: ~20 files, role `EVIDENCE`, explicitly barred from serving as authority.
- **Zero duplicate truth sources, zero new architecture**: confirmed by validation.

Phase 0.7 is complete — discovery and governance binding both closed. Not proceeding further without direction.
