# 10 — Discovery Rule Catalog

> PROGRAM **UAKOS-CLOSURE-007** · PHASE-001 · BASELINE `b67a720` · AUTHORITY = **NONE (DERIVED TRUTH)** · READ-ONLY.
> Every rule the discovery engine applies, catalogued for constitutional visibility. Source: `00-MASTER/UAKOS-CLOSURE-002/closure_engine.py`.

## 1. Source-selection rules

| R | Rule | Code |
|---|---|---|
| R-01 | Sources = `git ls-files` | `discover_sources()` |
| R-02 | Plus explicit `knowledge/canonical-knowledge.json`, `knowledge/decisions.json`, `knowledge/handbooks/**.md` | `build_concepts()` |
| R-03 | Plus corpus `../UCOS/**` **iff** `CLOSURE_SKIP_CORPUS != 1` | line 120 |
| R-04 | Only extensions in `TEXT_EXT ∪ {.docx}` | `discover_sources`, `_read_text` |
| R-05 | `00-SOURCE/*` routed to `source` zone; rest to `repo` zone | `build_concepts` |

## 2. Extraction rules

| R | Rule | Code |
|---|---|---|
| R-06 | Match 26 `FAMILIES` regexes, line-by-line | `_scan` |
| R-07 | Drop IDs matching `_SENTINEL` (`-U?9{2,3}$`) | `_scan` |
| R-08 | `.docx` → strip XML tags from `word/document.xml`, collapse whitespace | `_read_text` |
| R-09 | Read at most 4,000,000 chars/file | `_read_text` |
| R-10 | Disposition markers (`REJECT/DEFER/PLAN/CERT`) attributed **line-locally** | `_scan` |

## 3. Homing rules

| R | Rule | Code |
|---|---|---|
| R-11 | `top ∈ TRUTH_ROOTS` ⇒ homed | `_scan` |
| R-12 | `top ∈ CODE_ROOTS` (non-derived) ⇒ homed + `in_code` | `_scan` |
| R-13 | ID substring in file path ⇒ homed | `_scan` (`cid in name_upper`) |
| R-14 | Definitional home = truth-root file whose basename is/starts-with ID, excluding `DERIVED_SEG` | `_is_def_home` |
| R-15 | Derived/evidence/checkpoint paths never definitional homes | `DERIVED_SEG` |

## 4. Disposition rules (precedence)

| R | Rule |
|---|---|
| R-16 | not homed ⇒ `UNCLASSIFIED` |
| R-17 | `in_code` or `certified` ⇒ `IMPLEMENTED` |
| R-18 | else `rejected` ⇒ `REJECTED` |
| R-19 | else `deferred` ⇒ `DEFERRED` |
| R-20 | else constitution/spec/filename/book ⇒ `SPECIFIED` |
| R-21 | else `in_plan` ⇒ `PLANNED` |
| R-22 | else ⇒ `SPECIFIED` |

## 5. Gap / invariant rules

| R | Rule |
|---|---|
| R-23 | `upload_only` = unhomed ∧ source-only ∧ not in repo zone |
| R-24 | `conversation_only` = unhomed ∧ corpus-only |
| R-25 | `in_repo_unhomed` = unhomed ∧ seen in repo zone |
| R-26 | `orphan` = homed ∧ no constitution/spec/impl trace |
| R-27 | `duplicate_canonical_homes` = >1 exact-basename home |
| R-28 | `ukda_content_hash_duplicates` = shared `content_sha256` in store |
| R-29 | blocking = distinct(unclassified ∪ orphans) + dup_homes + hash_dups; CLOSED iff 0 |

## Determination

**DISCOVERY RULES: FULLY CATALOGUED (29 rules).** The rule set is now explicit and auditable. It is internally deterministic but scope-limited (§1–§2 rules R-03, R-04, R-06 are the primary limiters). Evidence: `closure_engine.py` verbatim.

*END — 10 · AUTHORITY = NONE · READ-ONLY.*
