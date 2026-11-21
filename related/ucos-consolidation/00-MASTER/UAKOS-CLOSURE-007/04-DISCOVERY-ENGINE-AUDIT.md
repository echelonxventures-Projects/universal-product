# 04 — Discovery Engine Audit

> PROGRAM **UAKOS-CLOSURE-007** · PHASE-001 · BASELINE `b67a720` · AUTHORITY = **NONE (DERIVED TRUTH)** · READ-ONLY.
> Audits every discovery mechanism: what it CAN discover, what it CANNOT, and why.

## 1. `closure_engine.py` (Phase-001 discovery)

| Capability | CAN discover | CANNOT discover | Why (evidence) |
|---|---|---|---|
| Concept anchors | 26 curated ID families | any ID outside `FAMILIES` | closed regex list (`FAMILIES`) |
| Source scope | git-tracked repo files + `00-SOURCE` + external corpus | anything **not git-tracked** (except explicit `knowledge/*.json`, `knowledge/handbooks`) | `git ls-files` in `discover_sources()` |
| Corpus | conversation/upload material at `../UCOS` | **nothing, when `CLOSURE_SKIP_CORPUS=1`** | line 120 guard |
| File types | `.md .txt .py .json .toml .sh .yml .yaml .cfg .docx` | `.pdf`, `.png/.jpg/.jpeg` (diagrams), `.zip`, `.xlsx`, other | `TEXT_EXT` set; `.docx` special-cased |
| `.docx` parsing | `word/document.xml` text | headers/footers, footnotes, embedded objects, images, `.docx` w/o `document.xml` | `_read_text()` docx branch |
| Read size | first 4,000,000 chars | anything beyond the 4 MB truncation | `_read_text(limit=4_000_000)` |
| Homing | ID under a TRUTH_ROOT / in filename | conceptual homing without an ID token | `_scan` zone==repo rules |
| Sentinels | — | `…-99/-999/-U99` (dropped) | `_SENTINEL` |

## 2. `phase2_engine.py` (concept-graph reconciliation)

- **Reuses `closure.json` only** — does **no** re-extraction. Inherits every Phase-001 blind spot verbatim. Also reads `00-BOOK/DATA/relationships.json` (homed graph). Cannot discover anything Phase-001 missed. (`phase2_engine.py` header: "does NOT re-extract or re-match concepts.")

## 3. `phase3_engine.py` (implementation planning)

- Consumes `closure.json` + `phase2.json` only; "does NOT discover, extract, re-inventory, or rebuild graphs." Zero discovery capability by design.

## 4. UKB / registries / knowledge graph

- `knowledge/canonical-knowledge.json`, `00-BOOK/DATA/{artifacts,id-ledger,relationships}.json` are **authoritative stores**, populated by `REG-AUTO-001` on artifact creation. They record what has been **homed**; they are not discovery mechanisms over un-homed/corpus knowledge.

## 5. Net discovery-capability envelope

The **union** of all mechanisms can discover: *git-tracked or corpus text in the allowed extensions, that contains an ID matching one of 26 curated families, within the first 4 MB, when the corpus is not skipped.* Everything outside that envelope is undiscoverable.

## 6. Determination

**DISCOVERY ENGINE AUDIT: the discovery envelope is narrow and closed.** Discovery is gated by (a) a hand-curated 26-family regex set, (b) git-tracking, (c) an extension allow-list excluding PDF/image/zip, (d) a 4 MB read cap, (e) a runtime corpus-skip switch, (f) sentinel exclusions. Downstream engines add no discovery. Evidence: `closure_engine.py`, `phase2_engine.py`, `phase3_engine.py` headers + code.

*END — 04 · AUTHORITY = NONE · READ-ONLY.*
