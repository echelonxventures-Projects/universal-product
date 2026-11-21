# 18 — Migration Strategy

> PROGRAM **UCOS-UMA-001** · PHASE-001 · UNIVERSAL MEASUREMENT AUTHORITY
> BASELINE `b67a720` · AUTHORITY = **NONE (DESIGN ONLY)** · MODE = DESIGN-ONLY · NON-IMPLEMENTING · FAIL-CLOSED.

---

## 0. Purpose

Define how measurement responsibility migrates from the current apparatus (`closure_engine.py` + `closure.json`/`phase2.json`/`phase3.json`, embedded in Closure Programs) to UMA — **without breaking any existing determination, and without modifying frozen constitutional text**. Migration is transfer-of-authority, executed as shadow → parity → cutover → retire.

## 1. Migration Principles

1. **No big bang.** UMA runs alongside the existing engine until proven equivalent.
2. **Evidence-gated.** Each phase advances only on measured parity evidence (fail-closed).
3. **History-preserving.** Sealed prior determinations remain valid and replayable; nothing is rewritten.
4. **Frozen text untouched.** CONST-*, CEP-*, and prior program artifacts are never edited (mission constraint).
5. **Decision stays put.** Only measurement transfers (Dependency Register, doc 10 §5); closure/validation/cert *decisions* remain with their owners.

## 2. Migration Phases

```
M0 SEED ─► M1 SHADOW ─► M2 PARITY ─► M3 CUTOVER ─► M4 RETIRE
```

### M0 — Seed
- Import CLOSURE-007 catalogs into UMA registries (doc 17 §5): namespaces, 26 families → declarative MatchRules, assumptions/exclusions.
- Register text source adapters mirroring current engine scope.
- Designate a Canonical Manifest reproducing the engine's current scan mode (repo-only vs full-corpus made explicit — closes MA-4).

### M1 — Shadow
- UMA runs in parallel; produces MeasurementResults but no consumer depends on them yet.
- The existing engine remains authoritative.

### M2 — Parity
- Compare UMA results to `closure.json`/`phase2.json` on the same baseline.
- **Parity metric:** for the overlapping 26 families + integrity counts, UMA MUST reproduce the engine's numbers exactly. Divergence is investigated as either (a) a UMA defect or (b) a previously-silent engine blind spot now surfaced as UNCOVERED (expected and desirable).
- Gate: parity on overlap + all new UNCOVERED items registered/dispositioned.

### M3 — Cutover
- Consumers (Closure/Validation/Cert) switch their *measurement read* to UMA API (doc 09). They keep their *decision* logic.
- `closure.json` etc. become UMA-produced (or thin UMA clients) rather than engine-produced.
- Determinism CI extended to assert UMA replay (D-12).

### M4 — Retire
- The discovery authority of `closure_engine.py` is formally retired (its content already lives in registries). The file may remain for historical replay but is no longer the authority.
- Governance records the authority transfer in the Governance Ledger + a freeze-style record consistent with existing program-freeze practice.

## 3. Parity & Divergence Handling (fail-closed)

| Outcome at M2 | Interpretation | Action |
|---|:---:|---|
| UMA = engine on overlap | parity | advance |
| UMA surfaces extra UNCOVERED | engine was silently blind | register namespace/family/adapter; NOT a regression |
| UMA < engine coverage | UMA defect | block cutover; fix UMA |
| Numeric mismatch on shared family | rule mismatch | reconcile MatchRule to engine regex; add test vectors |

Migration never *lowers* measured coverage; by construction UMA coverage ≥ engine coverage once registries are seeded, with the difference being newly-visible gaps.

## 4. Rollback

- Because UMA is read-only and additive, rollback at any phase = "stop consuming UMA, resume reading engine output." No source or truth mutation to undo (idempotence, doc 12).
- Sealed UMA results from shadow/parity remain as evidence even after rollback.

## 5. Data Migration

- No canonical knowledge migrates (UKB unchanged, Knowledge Once).
- Only *descriptors* (namespace/family/adapter/assumption) and *manifests* are created in UMA stores. These are derived and rebuildable from sources.

## 6. What Is Explicitly NOT Migrated

| Not migrated | Stays with | Why |
|---|---|---|
| Repository Truth | UKB | truth is never a measurement |
| Closure determination | Closure lineage | decision, not measurement |
| Enrichment actions | CLOSURE-003 lineage | mutation, not measurement |
| Planning | CLOSURE-002 phase3 | planning, not measurement |
| Governance authority | CEP/CONST | UMA defers, never assumes |

## 7. Dependency Determination

- This document operationalizes the TRANSFER/RETAIN decisions of doc 10 §5. It modifies no existing artifact; retirement of `closure_engine.py` discovery authority is a future governance action, evidence-gated, reversible until M4.

*END — 18 · UCOS-UMA-001 · AUTHORITY = NONE (DESIGN ONLY) · MODIFIES NOTHING.*
