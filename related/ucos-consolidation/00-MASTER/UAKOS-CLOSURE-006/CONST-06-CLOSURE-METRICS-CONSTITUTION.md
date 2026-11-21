# CONST-06 — Closure Metrics Constitution

> PROGRAM UAKOS-CLOSURE-006 · PHASE-001 · Read-only · Baseline `b67a720`
> Fail-Closed · Deterministic · Evidence Before Conclusion

---

## 1. Purpose

Freeze the canonical metric definitions so that "CLOSED vs NOT-CLOSED" is computed identically and
deterministically forever. Every metric names its source field and its closure semantics.

## 2. Domain A Metrics — source `closure.json`

| Metric | Field | Closure semantics | Current |
|--------|-------|-------------------|---------|
| Concept total | `concept_total` | Denominator of Domain A | 398 |
| Determination | `determination` | Must be `CLOSED` | CLOSED |
| Gap total | `gap_total` | Must be 0 | 0 |
| Not homed | `gaps.not_homed_concepts` | Must be 0 | 0 |
| In-repo unhomed | `gaps.in_repo_unhomed` | Must be 0 | 0 |
| Orphans | `gaps.orphan_concepts` | Must be 0 | 0 |
| Duplicate homes | `gaps.duplicate_canonical_homes` | Must be 0 | 0 |
| Hash duplicates | `gaps.ukda_content_hash_duplicates` | Must be 0 | 0 |
| Conversation-only (repo) | `gaps.conversation_only` | Must be 0 | 0 |
| Upload-only (repo) | `gaps.upload_only` | Must be 0 | 0 |
| Dispositions | `dispositions{}` | Σ must equal `concept_total` | 313+60+21+4=398 ✓ |

## 3. Domain B Metrics — source `phase2.json` / `phase3.json`

| Metric | Field | Closure semantics | Current |
|--------|-------|-------------------|---------|
| Concept total | `phase2.concept_total` | Denominator of Domain B | 506 |
| Graph nodes | `phase2.cooccurrence.nodes` | Must equal concept_total | 506 |
| Graph edges | `phase2.cooccurrence.edges` | Coverage indicator | 52276 |
| Determination | `phase2.determination` | Must be `CLOSED` | NOT-CLOSED |
| Gap total | `phase2.gap_total` | Must be 0 | 110 |
| Conversation-only | `phase2.gaps.conversation_only` | Must be 0 | 108 |
| Open enrichment | `phase2.open_enrichment_items` | Must be 0 | 110 |
| Planned total | `phase3.planned_total` | Items scheduled for enrichment | 110 |
| Planning complete | `phase3.planning_complete` | Planning gate | true |

## 4. Source Metrics — source `closure.json.sources`

| Metric | Field | Current |
|--------|-------|---------|
| Tracked total | `tracked_total` | 3287 |
| Markdown | `markdown` | 1412 |
| Docx uploads | `docx_uploads` | 6 |
| Corpus files | `corpus_files` | 0 (`corpus_present=true`) |

## 5. Determination Rules (frozen)

1. **Domain CLOSED** iff `determination == CLOSED` AND `gap_total == 0` for that domain's engine.
2. **Architectural Completeness** iff 0 UNKNOWN statuses (CONST-04).
3. **FULLY CLOSED** iff Domain A CLOSED AND Domain B CLOSED (never one alone).
4. **Fail-Closed:** any missing metric ⇒ NOT-CLOSED for that domain.
5. **Determinism:** metrics MUST reproduce on re-run (`make closure`) with identical values.

## 6. DETERMINATION

By the frozen rules: **Domain A CLOSED** (398/0). **Domain B NOT-CLOSED** (506/110). **System NOT
FULLY CLOSED.** Metrics are deterministic and evidence-sourced.
