# 03 — USIS-003 CERTIFICATION REPORT

**Certification runtime:** `ukbx certify` (UMB-IMP-006 / UMB-017) — 10 integrity
domains over the real post-registration state. Twin hard checks: `ukbx twin
--check` (7/7). Logs: `evidence/06-ukbx-twin.log`, `evidence/07-ukbx-certify.log`.

---

## 1 — Digital-twin hard checks (`ukbx twin --check`)

**RESULT: CERTIFIED (hard checks 7/7)** — scope 1006 artifacts, 15 signals.

| Check | Result | Note |
|---|:--:|---|
| C-05 referential | **PASS** | all endpoints resolve (incl. USIS-003 → USIS-002, USIS-003 → USIS-004) |
| C-06 coverage (advisory) | PASS | subjects carry testing signals |
| **C-07 graph acyclic** | **PASS** | acyclic — USIS-003 added as dependent of USIS-002/004 preserves acyclicity |
| C-08 navigation | PASS | all reachable + return path (portal `UCOS-USIS-000005.md`) |
| C-09 control-tower | PASS | computed dimensions automated |
| C-10 export | PASS | PROGRAM/ADV export non-empty |
| C-11 search | PASS | index intact |

## 2 — Certification runtime (`ukbx certify`) — 10 integrity domains

**RESULT: CERTIFIED (integrity domains 10/10)** — scope **1006** artifacts,
15 signals, 1099 change events.

| # | Domain | Result | | # | Domain | Result |
|---|---|:--:|---|---|---|:--:|
| 1 | Identity | **PASS** | | 6 | Version | **PASS** |
| 2 | Registry | **PASS** | | 7 | Lineage | **PASS** |
| 3 | Traceability | **PASS** | | 8 | Synchronization | **PASS** |
| 4 | Knowledge Graph | **PASS** | | 9 | Twin Intelligence | **PASS** |
| 5 | Change Intelligence | **PASS** | | 10 | Execution | **PASS** |

Evidence: `00-BOOK/DATA/certification.json`; audit
`.runtime/governance/certification-audit.json`; report
`00-BOOK/REGISTRIES/CERTIFICATION-REGISTRY.md`.

## 3 — Certification scope delta (USIS-004 → USIS-003)

| Metric | USIS-004 baseline | USIS-003 |
|---|---|---|
| Certified artifacts (scope) | 1005 | **1006** |
| Twin hard checks | 7/7 | **7/7** |
| Integrity domains | 10/10 | **10/10** |
| Change events | 1098 | **1099** |
| Signals | 15 | 15 |

Scope grew by exactly one artifact (the Science Catalog); no domain regressed.

## 4 — USIS-011 certification obligations

- **Obl. 16 (validation evidence present):** discharged — `evidence/` logs + `ukbx
  validate` PASS.
- **Obl. 17 (certification recorded):** discharged — `certification.json` +
  `CERTIFICATION-REGISTRY.md` + append-only certification audit updated.
- **FREEZE integrity (C2/C3/C4):** immutable; no new freeze; 0 edits to any frozen path.

## 5 — Determination

**USIS-003 is CERTIFIED** — digital-twin hard checks 7/7 (incl. C-07 acyclic) and
certification runtime 10/10 integrity domains over the real state (scope 1006). The
SCIENCE_INTELLIGENCE lifecycle (USIS-008) reaches **CERTIFIED** for this capability.
