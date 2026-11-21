# CONST-02 — Repository Integrity Constitution (DOMAIN A)

> PROGRAM UAKOS-CLOSURE-006 · PHASE-001 · Read-only · Baseline `b67a720`
> Canonical evidence: `00-MASTER/UAKOS-CLOSURE-002/closure.json` (derived, AUTHORITY=NONE)
> Fail-Closed · Evidence Before Conclusion

---

## 1. Definition

**Repository Integrity** is the internal canonical correctness of the governed repository,
measured *only* against governed repository artifacts. It answers: "Is the repository itself
internally sound, duplicate-free, orphan-free, fully homed, and traceable?"

It is **independent** of Vision Assimilation (CONST-03). A CLOSED Repository Integrity does
**not** imply Vision is assimilated.

## 2. Purpose

Guarantee that Repository Truth is internally consistent so that all downstream governance,
validation, and certification rests on a sound base.

## 3. Scope

- IN: governed artifacts across the 17 truth/code/spec roots (`00-BOOK`, `00-CEP`, `00-MASTER`,
  `02-MASTER`, `06-IMPLEMENTATION`–`14-SECURITY`, `adr`, `knowledge`, and code roots
  `engine`/`platform`/`data`/`service`/`application`/`infrastructure`/`intelligence`).
- OUT: unassimilated external knowledge (conversations/uploads not yet homed) — that is Domain B.

## 4. Authority

- **Analytical authority:** `closure_engine.py` → `closure.json`. The engine self-declares
  `AUTHORITY = NONE (DERIVED TRUTH)`, never mutates the frozen corpus, and is fail-closed
  (TRACK-001). It is NOT an authority; it is a derived analytical pipeline.
- **Governing authority:** UKB (`00-BOOK/tools/ukb.py`) — sole owner of Repository Truth.

## 5. Must-Verify Invariants

| Invariant | Metric (closure.json) | Required |
|-----------|-----------------------|----------|
| Canonical homes | `not_homed_concepts` | 0 |
| Duplicate-free | `duplicate_canonical_homes`, `ukda_content_hash_duplicates` | 0 |
| Orphan-free | `orphan_concepts` | 0 |
| In-repo homed | `in_repo_unhomed` | 0 |
| Conversation gap (repo scope) | `conversation_only` | 0 |
| Upload gap (repo scope) | `upload_only` | 0 |
| Knowledge Once | duplicate detail arrays empty | ✓ |
| Determinism | re-run reproduces `closure.json` | ✓ |

## 6. Evidence Requirements

A deterministic `closure.json` present at the baseline commit, with empty `detail` arrays for
`conversation_only`, `duplicate_homes`, `in_repo_unhomed`, `orphans`, `ukda_hash_duplicates`,
`unclassified`, and `upload_only`.

## 7. Success Criteria

- `concept_total = 398`
- `determination = CLOSED`
- `gap_total = 0` with **all** gap subcounts = 0
- Dispositions cover 100% of concepts.

## 8. Failure Criteria

Any gap subcount > 0, any non-empty `detail` array, missing/non-deterministic `closure.json`,
or an unclassified concept.

## 9. Dependencies

UKB registry · Canonical Home Register (CLOSURE-002 doc 22) · Traceability matrices
(CLOSURE-002 docs 26–27) · Repository Truth Determination (CLOSURE-002 doc 19).

## 10. Lifecycle

Governed continuously. Re-verified on every baseline via `make closure`. Never speculative.

---

## 11. CURRENT EVIDENCE (baseline b67a720)

```
concept_total : 398
determination : CLOSED
gap_total     : 0
gaps          : { conversation_only:0, upload_only:0, in_repo_unhomed:0,
                  orphan_concepts:0, not_homed_concepts:0,
                  duplicate_canonical_homes:0, ukda_content_hash_duplicates:0 }
dispositions  : IMPLEMENTED 313 · SPECIFIED 60 · DEFERRED 21 · REJECTED 4  (Σ=398)
sources       : 3287 tracked · 1412 markdown · 6 docx uploads · 0 corpus files (corpus_present=true)
families      : 27
detail arrays : all empty
```

## 12. DETERMINATION

**Repository Integrity (Domain A) = CLOSED.** Zero gaps. This determination is evidence-backed by
`closure.json` and is reported independently of Domain B. It does not, and shall not, imply Vision
Assimilation closure.
