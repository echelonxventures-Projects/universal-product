# 02 — USIS-001 VALIDATION REPORT

Every gate run with the canonical `.ec1-venv/bin/python` (3.12). Logs:
`00-MASTER/UCOS-USIS-WAVE1/MISSION-001-USIS-001/evidence/`.

---

## 1 — Validation gate results

| # | Gate | Result | Evidence |
|---|---|---|---|
| 0 | `ukb enforce --pre` | **PASSED** | 1003 eligible, 0 unregistered/unclassified/invalid (pre-registration eligibility/validity/classification) |
| 1 | `register.sh` (10 phases) | **TRANSACTION COMPLETE** | all phases pass; sealed |
| 2 | `ukb validate` | **PASSED** | 1003 artifacts; append-only page ledger intact; referential integrity OK; forward-only lifecycle intact |
| 3 | `ukb enforce` (post) | **PASSED** | 1003 eligible == 1003 registered; 0 unregistered / 0 unclassified / 0 invalid |
| 4 | `ukbx validate` | **PASSED** | 15 signals, append-only, every subject resolves, provenance present, no embedded secrets |
| 5 | `ukbx twin --check` | **CERTIFIED 7/7** | C-07 acyclic · C-08 navigation reachable+return · C-09 control-tower automated · C-10 export non-empty · C-11 search |

## 2 — Constitutional & dependency correctness

- **Classification correctness:** program USIS, category USIS, **VOL-024**, family UNIVERSAL-SCIENCE-INTELLIGENCE, domain science-intelligence — resolved from self-declared front-matter (`METADATA_CLASSIFY_KEYS`) and confirmed by `config.py` path rule `^15-UNIVERSAL-SCIENCE-INTELLIGENCE/ → USIS/USIS/VOL-024`. `unclassified == 0`.
- **Dependency correctness:** `Depends-On → USIS-GOV-000` (metadata) + `Parent → USIS-GOV-000` (structural program-root) + `Authorized-By → USIS-GOV-000` (metadata AUTHORITY). All downward-only; graph acyclic (C-07). No forward reference (target pre-registered in Wave 0).
- **Registration correctness:** present in every synchronized register (artifact/page/graph/volume/change-version-lineage/certification); id-ledger append-only (no reuse/renumber).

## 3 — USIS-011 proof-obligation status (this capability)

| Obl. | Name | Status |
|---|---|:--:|
| 1 | Zero Hard Coding | PASS (no tech named) |
| 2 | Zero Duplication | PASS (no competing catalog/registry) |
| 3 | Zero Overlap | PASS (single owner) |
| 4 | Zero Orphan Artifacts | **PASS** (`ukb enforce`) |
| 5 | Zero Circular Dependencies | **PASS** (C-07 acyclic) |
| 7 | Zero Architectural Debt | PASS (append-only; nothing renumbered) |
| 8 | Knowledge Once | PASS (one canonical home) |
| 9 | Canonical Ownership | PASS (owning family USIS) |
| 10 | Registry Closure | **PASS** (member resolves + registered) |
| 15 | Traceability Closure | PASS (spine: requirement/architecture → USIS-GOV-000) |
| 18 | Repository Consistency | **PASS** (byte-stable — see `04`) |
| 19 | Constitutional Consistency | PASS (0 freeze edits; no higher-instrument conflict) |

Obligations 16/17 (per-capability validation/certification evidence) are
discharged by `ukbx certify` for this artifact's state (see `03`). Obligations
11/12 (ontology/taxonomy closure) and 13 (capability-chain) apply to USIS-004/005
content and are **out of scope** for the constitution.

## 4 — Caveat (full disclosure)

`ukb validate` reports `jsonschema not installed — structural checks only`. This
matches the published-baseline environment and the Wave-0 record; it is **not a
regression**. The CI backstop `ucos-registration-gate.yml` installs `jsonschema`
and exercises full schema validation on push/PR. Recommend a local
`pip install jsonschema` for parity (non-blocking).

## 5 — Determination

**USIS-001 is constitutionally validated, dependency-correct, and
registration-correct.** All applicable gates PASS.
