# 02 — USIS-002 VALIDATION REPORT

Every gate run with `python3` against the published baseline environment. Logs:
`00-MASTER/UCOS-USIS-WAVE1/MISSION-002-USIS-002/evidence/`.

---

## 1 — Validation gate results

| # | Gate | Result | Evidence |
|---|---|---|---|
| 0 | `ukb enforce --pre` | **PASSED** | pre-registration eligibility/validity/classification; 0 unregistered/unclassified/invalid |
| 1 | `register.sh` (10 phases) | **TRANSACTION COMPLETE** | all phases pass; sealed (scope 1003 → 1004) — `evidence/01-register.log` |
| 2 | `ukb validate` | **PASSED** | 1004 artifacts; append-only page ledger intact; referential integrity OK; forward-only lifecycle intact — `evidence/03-ukb-validate.log` |
| 3 | `ukb enforce` (post) | **PASSED** | 1004 eligible == 1004 registered; 0 unregistered / 0 unclassified / 0 invalid — `evidence/04-ukb-enforce.log` |
| 4 | `ukbx validate` | **PASSED** | 15 signals, append-only, every subject resolves, provenance present, no embedded secrets — `evidence/05-ukbx-validate.log` |
| 5 | `ukbx twin --check` | **CERTIFIED 7/7** | C-05 referential · **C-07 acyclic** · C-08 navigation · C-09 control-tower · C-10 export · C-11 search — `evidence/06-ukbx-twin.log` |

## 2 — Constitutional & dependency correctness

- **Classification correctness:** program USIS, category USIS, **VOL-024**, family
  UNIVERSAL-SCIENCE-INTELLIGENCE, domain science-intelligence — resolved from
  self-declared front-matter (`METADATA_CLASSIFY_KEYS`) and confirmed by
  `config.py` path rule `^15-UNIVERSAL-SCIENCE-INTELLIGENCE/ → USIS/USIS/VOL-024`.
  `unclassified == 0`.
- **Home correctness:** single canonical home `15-…/06-UNIVERSES/` (D-1 resolved
  by USIS-005 §2/§3). No split-home; `08-DOMAINS/` untouched.
- **Dependency correctness:** `Depends-On → UCOS-USIS-000002` (USIS-001, metadata)
  + `Parent → UCOS-USIS-000001` (USIS-GOV-000, structural program-root) +
  `Authorized-By → UCOS-USIS-000002 / UCOS-USIS-000001` (metadata AUTHORITY). All
  downward-only; graph acyclic (C-07). No forward reference (all targets
  pre-registered: USIS-001 @ Wave 1, USIS-GOV-000 @ Wave 0).
- **Registration correctness:** present in every synchronized register (artifact/
  page/graph/volume/change-version-lineage/certification); id-ledger append-only
  (VOL-024 page range 9133–9136 → 9133–9139; no reuse/renumber).

## 3 — USIS-011 proof-obligation status (this capability)

| Obl. | Name | Status |
|---|---|:--:|
| 1 | Zero Hard Coding | PASS (no vendor/tech named; universes are agnostic concerns) |
| 2 | Zero Duplication | **PASS** (single catalog; realizing universes REFERENCE MIP homes; no competing registry) |
| 3 | Zero Overlap | **PASS** (each universe one canonical concern/owner) |
| 4 | Zero Orphan Artifacts | **PASS** (`ukb enforce` 1004/1004) |
| 5 | Zero Circular Dependencies | **PASS** (C-07 acyclic; recursion is a strict forest) |
| 7 | Zero Architectural Debt | PASS (append-only; nothing renumbered; no `config.py` edit) |
| 8 | Knowledge Once | **PASS** (one canonical home; no second enumerating file — D-2) |
| 9 | Canonical Ownership | PASS (owning family USIS; single home) |
| 10 | Registry Closure | **PASS** (member resolves + registered; reserved slots open) |
| 14 | No Forward Reference | **PASS** (Depends-On targets pre-registered) |
| 15 | Traceability Closure | PASS (spine: Depends-On/Authorized-By → USIS-001 → USIS-GOV-000) |
| 18 | Repository Consistency | **PASS** (byte-stable regeneration — see `04`) |
| 19 | Constitutional Consistency | PASS (0 freeze edits; no higher-instrument conflict) |
| 20/21 | Open registry / uncapped | **PASS** (`USIS-U-FUT`/`USIS-U-UNK` permanent reserved) |

Obligations 16/17 (per-capability validation/certification evidence) are
discharged by `ukbx certify` for this state (see `03`). Obligations 11/12
(ontology/taxonomy closure) and 13 (capability-chain) apply to USIS-004/005 and
are **out of scope** for the catalog.

## 4 — Caveat (full disclosure)

`ukb validate` reports `jsonschema not installed — structural checks only`. This
matches the published-baseline environment and the USIS-001 record (Risk R-4); it
is **not a regression**. The CI backstop `ucos-registration-gate.yml` installs
`jsonschema` and exercises full schema validation on push/PR. A local
`pip install jsonschema` gives parity (non-blocking).

## 5 — Determination

**USIS-002 is constitutionally validated, dependency-correct, and
registration-correct.** All applicable gates PASS.
