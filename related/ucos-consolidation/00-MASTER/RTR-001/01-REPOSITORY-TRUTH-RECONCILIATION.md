# RTR-001 · Output 01 — REPOSITORY TRUTH RECONCILIATION

| Field | Value |
|-------|-------|
| MISSION | RTR-001 — Repository Truth Reconciliation · Concept Layer (READ • ANALYZE • DETERMINE) |
| CLASSIFICATION | Constitutional reconciliation — evidence-based determination (operational memory) |
| AUTHORITY | **NONE — DERIVED TRUTH.** This mission reads and reconciles committed repository evidence. It enacts nothing, ratifies nothing, repairs nothing, implements nothing. |
| SCOPE | The concept layer of UCOS Ω∞ Repository Truth, and the apparent contradiction surfaced by RA-002. |
| BASELINE | git repo `UCOS-CONSOLIDATION` · branch `governance-reconciliation` · HEAD `ab78f350` · working tree pre-dirty at capture (49 porcelain entries, pre-existing) |
| METHOD | `git ls-files` / `git check-ignore` / `git status` + full read of committed authority docs + read of derived (ignored/untracked) artifacts + read-only execution of `ukb`/`ukbx` verifiers |
| DISPOSITION | **RECONCILIATION REQUIRED** (governance/tooling scope only — NO concept-layer implementation mandated). See `05-FINAL-DETERMINATION.md`. |

---

## 1. The one rule that decides everything

The mission's absolute rule: *"Everything SHALL be derived exclusively from committed repository evidence."*

Applying that rule mechanically to the concept layer produces the entire determination, because the concept-layer artifacts split cleanly into two classes:

| Class | What it contains | Committed to git? | Repository Truth? |
|-------|------------------|:-----------------:|:-----------------:|
| **Committed authority** | `UAKOS-CLOSURE-002-CHARTER.md`, `README.md`, `PHASE-002-README.md`, `PHASE-INTERFACE-CONTRACT.md`, `CONSOLIDATION-PLAN.md`, `closure_engine.py`, `phase2_engine.py`, `phase3_engine.py` (8 files) | **YES** | **YES** |
| **Derived output** | `19-…`, `20-…`, `21-…`, `22-…`, `31-…` … `68-…` (all numbered `.md`), `closure.json`, `phase2.json`, `phase3.json` | **NO — gitignored** | **NO** |

Evidence (`git check-ignore -v`):

```
.gitignore:52:00-MASTER/UAKOS-CLOSURE-002/[0-9][0-9]-*.md   →  19,20,21,22,31,34,…68  (ALL numbered docs)
```

The `.gitignore` stanza states the intent verbatim:

> "UAKOS-CLOSURE-002 — deterministic engine OUTPUT (GOV-005 §5.3, re-derivable). The authored sources … remain tracked; the numbered reports and JSON state are regenerated each run (`make closure` …) and must never be tracked or seen as drift."

**Consequence:** every numbered concept-layer document — including `19-REPOSITORY-TRUTH-DETERMINATION.md`, `20-CANONICAL-CONCEPT-REGISTER.md`, `21-CONCEPT-NORMALIZATION-REGISTER.md`, and `22-CANONICAL-HOME-REGISTER.md` — is a **generated, non-committed, non-authoritative artifact**. None of them is Repository Truth. They are re-derivable projections of the engine over the corpus, explicitly declared out-of-corpus.

## 2. What the committed authority actually says about itself

Both committed governing documents (CHARTER + README) declare, without ambiguity:

- **`AUTHORITY = NONE — DERIVED TRUTH.`** "Records only what evidence in the repository proves."
- **`HOME = 00-MASTER/UAKOS-CLOSURE-002/` — operational memory, excluded from the corpus** (`RECON-C1`: `00-MASTER/` is never UKB-registered). "Creates **no** competing canonical store."
- **Fail-closed** — "absence of evidence = NOT-DONE"; the program "never issues a green closure certificate that evidence does not support."

So the concept-closure program is, by its own committed charter, a **subordinate audit/reconciliation tool** — not a source of constitutional authority and not a canonical concept store.

## 3. The RA-002 contradiction, located precisely

RA-002 §7 ("CONTRADICTION NOTICE") recorded the exact conflict this mission was chartered to reconcile:

| Signal | Claim | Source | Baseline | Committed? |
|--------|-------|--------|:--------:|:----------:|
| Session-start hook | `UAKOS-CLOSURE-002: CLOSED \| concepts=431 \| gaps=0` | `closure.json` (via `closure_engine.py`) | **HEAD `ab78f35`** (current) | No (gitignored) |
| Numbered reports | `FAIL-CLOSED`; **506** concepts / 396 homed / **110** gaps | `19-…`, `20-…` (via engines) | **`b67a720`** (older) | No (gitignored) |

Verified machine evidence at current HEAD:

```
closure.json : baseline_commit=ab78f35 · determination=CLOSED · concept_total=431 · gap_total=0
               gaps={conversation_only:0, duplicate_canonical_homes:0, in_repo_unhomed:0,
                     not_homed_concepts:0, orphan_concepts:0, ukda_content_hash_duplicates:0, upload_only:0}
20-…header  : baseline b67a720 · 506 distinct · 396 homed · 110 unhomed
19-…header  : baseline b67a720 · FAIL-CLOSED — concept layer "has not been constructed"
```

## 4. Why the contradiction exists (root cause)

The two signals are **the same engine's output captured at two different commits and two different engine phases**, both persisted as regenerable artifacts and never reconciled:

1. **Different baselines.** The numbered reports are frozen at `b67a720`; `closure.json` (and therefore the hook) was last regenerated at `ab78f35`. The corpus grew from 990 → 1012 registered artifacts between those commits. Identical determinism holds only *at an identical commit* (CHARTER §2); across commits the counts legitimately differ.
2. **Different determination scopes.** `19-…` (FAIL-CLOSED) folds in the **vision-to-repository traceability** blocker (G-01) and the "concept store not built" state (Phases 2–4 NOT STARTED). `closure.json`'s `determination=CLOSED` reflects only the **concept-homing** gate (all gap sub-counts zero). They measure different predicates and were never expected to be numerically equal.
3. **Sentinel reclassification.** `20-…` carried ~90 `UCOS-COMP-00xxxx` rows as `UNCLASSIFIED / unhomed` plus a scattering of `ARCH/GOV/LAW/PHASE/RUNTIME` unclassified rows — the bulk of the 110 gaps. The later engine drops wildcard/sentinel IDs (CHARTER §5 / normalization "Sentinel exclusion"), which simultaneously lowers the count (506 → 431) and zeroes the gaps (110 → 0).
4. **Staleness of the persisted narrative.** The numbered markdown was never regenerated after `b67a720`; the hook reads the freshly-regenerated JSON. Two regenerations of a "must-never-be-committed" artifact were allowed to diverge in the working tree.

**None of this is a contradiction inside committed Repository Truth.** It is a divergence between two uncommitted regenerations of a subordinate tool, plus a hook that surfaces the newer of the two.

## 5. What committed Repository Truth actually asserts about the concept layer

**Nothing.** Because every concept register is gitignored, the committed corpus contains **no concept-layer closure claim at all** — neither CLOSED nor FAIL-CLOSED. What is committed and machine-verified is the **artifact/registration layer**, which is internally consistent and passes every gate (see `04-CANONICAL-AUTHORITY-MATRIX.md` §Validation):

```
ukb validate       PASS   (1012 artifacts, append-only ledger intact, ref-integrity OK)
ukb enforce --pre  PASS   (1012 eligible = 1012 registered; 0 unregistered/unclassified/invalid)
ukb enforce        PASS   (post-registration parity)
ukbx validate      PASS   (15 signals, provenance present, secret-free)
ukbx twin --check  CERTIFIED (hard checks 7/7)
ukbx certify       CERTIFIED (integrity domains 10/10)
```

## 6. Reconciliation statement

- The apparent contradiction is **explained and dissolved**: it is a staleness/scope divergence between two non-authoritative regenerations of the `UAKOS-CLOSURE-002` engine, not a conflict within Repository Truth.
- Committed Repository Truth is **internally consistent** at the layer it actually governs (artifacts/registration), and is **silent** at the concept layer by deliberate design (the concept store is out-of-corpus operational memory).
- Therefore no *implementation* is required to make Repository Truth consistent. However, the divergence is **currently unresolved in the working tree** and a live hook is emitting one side of it as if authoritative. That is a genuine governance/tooling defect requiring reconciliation — hence the final disposition **RECONCILIATION REQUIRED**, scoped to governance/tooling only.

See `02-CONCEPT-LAYER-DETERMINATION.md` (primary questions 1–8), `03-REF-CONCEPT-RECONCILIATION.md` (12 REF families), `04-CANONICAL-AUTHORITY-MATRIX.md` (authority + validation), and `05-FINAL-DETERMINATION.md` (verdict).

*END — RTR-001 · Output 01 · AUTHORITY = NONE (DERIVED TRUTH). Read-only; repository unchanged.*
