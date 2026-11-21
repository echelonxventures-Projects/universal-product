# 06 — Discovery Coverage Matrix

> PROGRAM **UAKOS-CLOSURE-007** · PHASE-001 · BASELINE `b67a720` · AUTHORITY = **NONE (DERIVED TRUTH)** · READ-ONLY.
> Coverage of the discovery apparatus across the axes of the measurement universe.

## 1. Coverage by axis

| Axis | In scope | Out of scope (blind) | Verdict | Evidence |
|---|---|---|:---:|---|
| **Identifier family** | 26 curated families | all other namespaces | **PARTIAL** | `FAMILIES`, report 02 |
| **Source location** | git-tracked repo + `00-SOURCE` + corpus + `knowledge/*.json`,`knowledge/handbooks` | untracked files, other git-ignored generated stores | PARTIAL | `discover_sources()` |
| **File type** | `.md .txt .py .json .toml .sh .yml .yaml .cfg .docx` | `.pdf .png .jpg .jpeg .zip .xlsx` etc. | PARTIAL | `TEXT_EXT` |
| **Document internals** | body text (`word/document.xml`) | docx headers/footers/notes/images; images as diagrams | PARTIAL | `_read_text` |
| **File size** | first 4 MB | remainder of larger files | PARTIAL | `limit=4_000_000` |
| **Conversation corpus** | scanned in full-corpus mode | **skipped** in `CLOSURE_SKIP_CORPUS=1` | **CONDITIONAL** | line 120; hook |
| **Concept expression** | ID-bearing tokens | prose concepts w/o IDs | PARTIAL | homing needs ID |
| **Duplicate / hash** | UKDA store objects | non-store knowledge | PARTIAL | `_ukda_hash_dups` |

## 2. Coverage headline

No axis is FULL. Every axis has a declared or de-facto exclusion. The apparatus is **broad on the ID-anchored, git-tracked, text layer** and **blind everywhere else**.

## 3. Determination

**COVERAGE COMPLETENESS: PARTIAL (trending FAIL).** Discovery covers one well-defined slice (ID-anchored git-tracked text) with high fidelity, but no axis reaches full coverage and several (namespace, file type, prose, corpus-mode) leave material architectural knowledge unmeasured. Evidence: `closure_engine.py`; reports 02–04, 08.

*END — 06 · AUTHORITY = NONE · READ-ONLY.*
