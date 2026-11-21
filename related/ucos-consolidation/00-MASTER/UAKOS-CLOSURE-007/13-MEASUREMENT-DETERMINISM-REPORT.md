# 13 — Measurement Determinism Report

> PROGRAM **UAKOS-CLOSURE-007** · PHASE-001 · BASELINE `b67a720` · AUTHORITY = **NONE (DERIVED TRUTH)** · READ-ONLY.
> Distinguishes *engine determinism* (same inputs ⇒ same output) from *measurement determinism* (the determination is stable and mode-independent).

## 1. Engine determinism — PASS

`closure_engine.py` is deterministic by construction: stdlib-only, `sort_keys=True`, `concepts[]` sorted by `id`, sets serialized as sorted lists, no wall-clock/random inputs. A fixed input tree yields byte-identical `closure.json`. Evidence: `PHASE-INTERFACE-CONTRACT.md §2.1/§4.3`; determinism CI (`.github/workflows/determinism.yml`).

## 2. Measurement determinism — FAIL

The **determination** is not input-deterministic because a hidden environment switch changes the measured universe:

| Input variance | Result | Evidence |
|---|---|---|
| `CLOSURE_SKIP_CORPUS=1` | 398 concepts / gaps 0 / CLOSED | frozen `closure.json`; session hook |
| unset (full-corpus) | 506 concepts / gaps 108 / NOT-CLOSED | `PHASE-INTERFACE-CONTRACT.md §5` |

`PHASE-INTERFACE-CONTRACT.md §5` records the live symptom: *"`closure.json` moved 398→506 mid-session"* and classifies it as a known, unresolved risk (fix "needs authorization," "Not executed"). `closure.json` carries **no `scan_mode` or `schema_version` field**, so a reader cannot tell which universe a given file measured.

## 3. Reproducibility

Reproducibility holds **only if the scan mode is also pinned and communicated** — which it is not. Two operators following the documented commands (`make closure` vs the hook's `CLOSURE_SKIP_CORPUS=1`) obtain different determinations from the same commit. Reproducibility is therefore **conditional / unpinned**.

## 4. Determination

- **Discovery Determinism (engine): PASS.**
- **Measurement Determinism (determination): FAIL** — mode-dependent, unstamped, and the standing gate runs the mode that hides the gap. Evidence: `closure_engine.py`, `PHASE-INTERFACE-CONTRACT.md §5`, `.kiro/hooks/uakos-closure-002.json`.

*END — 13 · AUTHORITY = NONE · READ-ONLY.*
