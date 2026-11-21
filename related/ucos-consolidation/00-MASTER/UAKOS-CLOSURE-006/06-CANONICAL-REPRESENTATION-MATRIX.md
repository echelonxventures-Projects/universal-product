# 06 — Canonical Representation Matrix

> PROGRAM **UAKOS-CLOSURE-006** · PHASE-001 · BASELINE `b67a720` · AUTHORITY = **NONE (DERIVED TRUTH)** · READ-ONLY.

Tests the "exactly one canonical home / one authority / one disposition" invariants.

## 1. Invariant results (full-corpus canonical model)

| Invariant | Target | Observed | Verdict | Evidence |
|---|:---:|:---:|:---:|---|
| Every concept has **exactly one** canonical home | 0 unhomed | **108 unhomed** | **FAIL** | `33-…`; `closure.json` (repo-only masks this) |
| No concept has **>1** canonical home | 0 dup homes | 0 | PASS | `closure.json` `duplicate_canonical_homes=0` |
| Every concept has **exactly one** disposition | 0 UNCLASSIFIED | 108 UNCLASSIFIED (canonical) | **FAIL** | disposition rule in `closure_engine.py:assign` |
| One governing authority per concept | 1 | 1 for homed set | PARTIAL | catalog owner columns; unhomed have none |
| No competing canonical stores | 1 | 1 (`00-BOOK` + `knowledge/`) | PASS | single UKDA store, `_ukda_hash_dups=0` |

## 2. Canonical home assignment (homed set)

For homed concepts the canonical-home model is sound: `def_homes`/`exact_homes` resolve to a single truth-root file, and the `phase2_engine.py` home-selection prefers implementation > constitution > spec > book. No duplicate-home or hash-duplicate violations exist (report 08).

## 3. The failing invariant

The "exactly one canonical home" invariant fails **only because of the 108-concept residue**, and is **masked** in the frozen `closure.json` because that file was written in repo-only mode (`concept_total=398`), where the 108 corpus-only concepts are never introduced. The invariant is red under the canonical (full-corpus) measurement the program itself designates authoritative.

## 4. Determination

**CANONICAL REPRESENTATION: FAIL for the "one home / one disposition" invariant** (108 unhomed under canonical scan); **PASS for the "no duplicate / no competing store" invariants**. Net: the *uniqueness* half of canonicality holds; the *totality* half does not.

*END — 06 · AUTHORITY = NONE · READ-ONLY AUDIT.*
