# 07 — Semantic Conflict Report

> PROGRAM **UAKOS-CLOSURE-006** · PHASE-001 · BASELINE `b67a720` · AUTHORITY = **NONE (DERIVED TRUTH)** · READ-ONLY.

Detects semantic duplicates, renamed/superseded concepts, competing authorities, and parallel stores.

## 1. Findings

| Conflict class | Observed | Verdict | Evidence |
|---|---|:---:|---|
| Semantic duplicates / equivalent concepts | corpus concepts re-expressed under repo IDs (e.g. Commerce Universe ≡ `UNI-062`) — declared **lineage**, not conflict | CONTROLLED | catalog "SRC-04 lineage" tags |
| Renamed concepts | corpus `UCOS-COM/EDU/MED/…` → repo `UNI-###` | CONTROLLED (lineage documented) | `02-MASTER` universe catalog |
| Superseded concepts | `99-FREEZE`, `00-SOURCE` frozen set | CONTROLLED | freeze directory |
| **Competing canonical stores** | single UKDA store (`knowledge/canonical-knowledge.json` + `00-BOOK`) | **NONE** | `closure.json` `ukda_content_hash_duplicates=0` |
| **Competing governance** | one fail-closed governance + `REG-AUTO-001` | **NONE** | registries |
| **Parallel measurement modes** | repo-only vs full-corpus produce different `closure.json` numbers from one file | **CONFLICT** | `PHASE-INTERFACE-CONTRACT.md §5` |
| Conflicting definitions | none located | NONE | — |

## 2. The one material semantic conflict — measurement identity

`closure.json` is a **single canonical artifact** that can hold **two different truths** depending on `CLOSURE_SKIP_CORPUS`:
- repo-only: 398 concepts / gaps 0
- full-corpus: 506 concepts / gaps 108

`PHASE-INTERFACE-CONTRACT.md §5` records this as a live defect ("`closure.json` moved 398→506 mid-session") and classifies the fix as "**Recommended resolution (post-freeze, needs authorization)** … designate the full-corpus run as canonical … add explicit `scan_mode` + `schema_version`. **Not executed.**"

This is a **determinism/idempotency conflict**, not a concept-naming conflict. It is the mechanism by which a red measurement is presented as green.

## 3. Determination

**SEMANTIC CONFLICT: PASS for concept-level semantics** (lineage is documented; no competing stores/governance/duplicate definitions); **FAIL for measurement identity** (one canonical file yields two determinations by scan mode). Evidence: `02-MASTER` catalogs, `closure.json`, `PHASE-INTERFACE-CONTRACT.md §5`.

*END — 07 · AUTHORITY = NONE · READ-ONLY AUDIT.*
