# 08 — Discovery Blind Spot Register

> PROGRAM **UAKOS-CLOSURE-007** · PHASE-001 · BASELINE `b67a720` · AUTHORITY = **NONE (DERIVED TRUTH)** · READ-ONLY.
> Every mechanism by which architectural knowledge can escape measurement. Each row is an evidenced blind spot.

| ID | Blind spot | Mechanism | Evidence | Severity |
|---|---|---|---|:---:|
| BS-01 | **Unknown namespaces** | concept discovery limited to 26 hard-coded `FAMILIES` | `closure_engine.py:FAMILIES` | **HIGH** |
| BS-02 | **Corpus skipped** | `CLOSURE_SKIP_CORPUS=1` short-circuits corpus scan; used by session hook | `closure_engine.py:120`, `.kiro/hooks/uakos-closure-002.json` | **HIGH** |
| BS-03 | **Prose-only concepts** | homing/recognition requires an ID token; ID-less architecture invisible | `_scan` logic | **HIGH** |
| BS-04 | **Non-text sources** | `.pdf`, `.png/.jpg/.jpeg` (diagrams e.g. `Architechtural Diagram.jpeg`), `.zip`, `.xlsx` excluded | `TEXT_EXT` | MEDIUM |
| BS-05 | **Untracked files** | only `git ls-files` (+2 explicit `knowledge/*.json`) scanned; untracked/ignored generated knowledge invisible | `discover_sources()` | MEDIUM |
| BS-06 | **4 MB read cap** | IDs beyond 4,000,000 chars of a large file unread | `_read_text(limit=4_000_000)` | MEDIUM |
| BS-07 | **docx internals** | headers/footers/footnotes/text-boxes/images and docx without `word/document.xml` unread | `_read_text` docx branch | MEDIUM |
| BS-08 | **Sentinel exclusion** | IDs ending `-99/-999/-U99` dropped as examples (may drop real IDs) | `_SENTINEL` | LOW |
| BS-09 | **Rigid widths / case** | wrong-width (`MCS-1`, `AD-0016`) and uppercase `PHASE-` never match | regex widths; `Phase` case-sensitivity | MEDIUM |
| BS-10 | **Scan-mode ambiguity** | one `closure.json` encodes either 398/0 or 506/108; no `scan_mode` stamp | `PHASE-INTERFACE-CONTRACT.md §5` | **HIGH** |
| BS-11 | **Derived-path suppression** | occurrences under `_evidence/ outputs/ CHECKPOINTS/ __pycache__ .egg-info` never count as homes | `DERIVED_SEG` | LOW (intended) |

## Aggregate

11 blind spots: **4 HIGH, 5 MEDIUM, 2 LOW.** Any one of BS-01/02/03 alone permits architectural knowledge to exist uncounted.

## Determination

**BLIND SPOTS: MATERIAL AND MULTIPLE.** The discovery apparatus has at least 11 distinct escape paths, four of them high-severity. Evidence: cited inline. No blind spot is repaired by this audit (read-only).

*END — 08 · AUTHORITY = NONE · READ-ONLY.*
