# 02 — Validation Summary

| Field | Value |
|-------|-------|
| ARTIFACT ID | WAVE0-ACC-02 (Validation Summary) |
| MISSION | Wave-0 Acceptance / Baseline Certification |
| STATUS | COMPLETE · AUTHORITY = NONE (DERIVED) · READ-ONLY |
| METHOD | Fresh re-run of every applicable repository validation + enforcement mechanism. No fabricated results. |

---

## 1 — Gate results (re-run this mission)

| # | Mechanism | Command | Result | Evidence |
|---|-----------|---------|:------:|----------|
| 1 | Repository / registry / graph / dependency validation | `ukb validate` | **PASS** | "VALIDATION PASSED — 1002 artifacts, append-only page ledger intact, referential integrity OK; 0 execution(s)" |
| 2 | Enforcement (eligibility/validity/classification/registration) | `ukb enforce` | **PASS** | 1002 eligible = 1002 registered; 0 unregistered; 0 unclassified (OTHER/MISC); 0 invalid (audit run #178) |
| 3 | Twin signal-ledger validation | `ukbx validate` | **PASS** | 15 signals, append-only, every subject resolves, provenance present, no embedded secrets |
| 4 | Digital-twin certification (hard checks) | `ukbx twin --check` | **PASS** | CERTIFIED — hard checks 7/7 (incl. control-tower automated, export non-empty, search) |
| 5 | Certification runtime (9+1 integrity domains) | `ukbx certify` | **PASS** | CERTIFIED — integrity domains 10/10 (identity, registry, traceability, knowledge-graph, change, version, lineage, synchronization, twin-intelligence, execution); scope 1002 artifacts / 15 signals / 1094 change events |
| 6 | Full atomic transaction | `register.sh --guard` | **TRANSACTION COMPLETE** (10/10 phases) + expected uncommitted-drift signal | Phases 0–10 all PASS; guard reports uncommitted regeneration (no commit authorized) |
| 7 | Determinism | FREEZE C4 engine ×2 + `ukb build` ×2 | **PASS** | see 03-DETERMINISM-CERTIFICATION |
| 8 | Freeze validation | FREEZE C4 seal vs C2/C3 | **PASS** | C4 `710769fc…` distinct; C2 `f966c8e0…` recomputed byte-identical; C2/C3 unmodified |

**Every applicable gate PASSES.** No gate result was fabricated.

## 2 — Optional-dependency impact (precise)

| Dependency | State | Impact |
|-----------|-------|--------|
| `jsonschema` | **NOT installed** | `ukb validate` runs **structural checks only** and prints: "jsonschema not installed — ran structural checks only." Full JSON-schema (`artifact.schema.json`) validation of each artifact record is **NOT executed**. This is the **same condition as the pre-Wave-0 baseline** (not a Wave-0 regression). **Residual risk:** schema-level field validation is unverified; structural integrity (append-only ledger, referential integrity, registration parity, graph acyclicity) IS verified. **To close:** `pip install jsonschema` then re-run `ukb validate`. |

## 3 — Critical caveat — a real defect the gates did not catch

All gates above PASS, yet the baseline is **REJECTED** (see 01 / 04). The passing gates **do not assert volume-list uniqueness**, so the duplicate `VOL-023` (blocking issue **B1**) passes `validate`/`enforce`/`certify` while being a genuine duplication in `volumes.json` / `VOLUME-REGISTRY.md`. **Gate PASS is necessary but not sufficient** for baseline acceptance; the working-tree review (04) is the control that surfaced B1.

## 4 — Determination

Validation mechanisms: **ALL PASS** (with the `jsonschema` structural-only caveat). Independent of the gates, the working-tree review found blocking defect **B1**. Net acceptance = **REJECT** pending B1 remediation.

*END — 02 · VALIDATION SUMMARY · ALL GATES PASS · B1 OUTSTANDING · AUTHORITY = NONE (DERIVED).*
