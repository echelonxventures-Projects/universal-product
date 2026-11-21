# RTR-001 · Output 02 — CONCEPT-LAYER DETERMINATION

| Field | Value |
|-------|-------|
| MISSION | RTR-001 — Repository Truth Reconciliation · Concept Layer |
| AUTHORITY | **NONE — DERIVED TRUTH.** Determinations below are read from committed evidence; nothing is enacted. |
| BASELINE | HEAD `ab78f350` · branch `governance-reconciliation` |
| PURPOSE | Answer the eight PRIMARY QUESTIONS strictly from committed repository evidence. |

---

## Answers to the eight primary questions

### Q1 — Which document is the current canonical authority for concept-layer closure?

**NONE exists in committed Repository Truth.**

Every candidate authority (`19-…`, `20-…`, `21-…`, `22-…`) is **gitignored generated output** (`.gitignore:52`) and self-declares `AUTHORITY = NONE (DERIVED TRUTH)`. The only *committed* documents in the program (`CHARTER`, `README`) also declare `AUTHORITY = NONE` and state the program "creates no competing canonical store." 

Therefore there is **no committed, ratified document that carries authority over concept-layer closure.** The concept layer is, in committed truth, an *un-adjudicated dimension* served only by an out-of-corpus audit tool. The nearest committed governing principle is `UCKO-PRIN-0001` (Knowledge Once) — a principle, not a closure authority.

### Q2 — Is UAKOS-CLOSURE-002 current, superseded, obsolete, or incorrect?

**CURRENT — but AUTHORITY = NONE.** The program's committed files declare it `ACTIVE · LIVING`. It is not superseded and not obsolete. It is *not incorrect* — it correctly, honestly reports what it measures. What is incorrect is any reading that treats its **generated numbered outputs** as Repository Truth or as a closure certificate. The program is a valid subordinate audit tool; it is not a source of authority.

### Q3 — Is `19-REPOSITORY-TRUTH-DETERMINATION.md` current, superseded, obsolete, or historical?

**HISTORICAL / STALE (and non-authoritative).**
- **Non-authoritative:** gitignored, `AUTHORITY = NONE`.
- **Stale:** frozen at baseline `b67a720`; the live engine state (`closure.json`) has since advanced to `ab78f35`. It has not been regenerated to match current HEAD.
- Its FAIL-CLOSED verdict was a *correct, honest* determination **for its baseline and its scope** (it refused to certify closure without evidence). It is best read as a **historical determination record**, not as the current state of the tool.

### Q4 — Is `20-CANONICAL-CONCEPT-REGISTER.md` current?

**NO — stale and non-authoritative.** Its header pins baseline `b67a720` and reports 506/396/110; the live engine state at HEAD `ab78f35` reports 431/431/0. It is a superseded regeneration of a gitignored artifact. It is neither current nor canonical.

### Q5 — What is the actual current concept inventory?

There is **no committed concept inventory.** The only *current* (HEAD-baseline) machine inventory is the gitignored `closure.json`, which is derived, non-authoritative operational memory. Reported *as derived data only*:

| Property | Value (derived, non-authoritative) | Source |
|----------|-----------------------------------|--------|
| Baseline | `ab78f35` (current HEAD) | `closure.json` |
| Determination (concept-homing gate) | `CLOSED` | `closure.json` |
| Distinct canonical concepts | **431** | `closure.json.concept_total` |
| Gap total | **0** | `closure.json.gap_total` |
| Families recognized | 26 (ID-namespace families) | `21-…` / engine |
| Families NOT recognized | `REF`, `CAT`, `GEN` | `21-…` (family regex) |

The **stale** register (`20-…`, baseline `b67a720`) reports 506/396/110. The delta (506→431, 110→0) is explained in `01-…` §4 (sentinel exclusion + commit advance).

### Q6 — How many concepts currently exist?

- **Committed Repository Truth:** concepts are not enumerated in the committed corpus; the answer is **not committed**.
- **Current derived tool (`closure.json`, HEAD):** **431** distinct canonical concept anchors.
- **Stale derived report (`20-…`, `b67a720`):** 506.

The only *defensible current number* is the HEAD-baseline derived value **431**, and it must carry the caveat "derived, non-authoritative."

### Q7 — How many concepts are canonically homed?

- **Current derived tool (HEAD):** **431 of 431** (`gap_total=0`, `in_repo_unhomed=0`, `not_homed_concepts=0`).
- **Stale report (`b67a720`):** 396 of 506.

### Q8 — How many concept gaps currently exist?

- **Current derived tool (HEAD):** **0** (all gap sub-counts zero).
- **Stale report (`b67a720`):** 110.
- **RA-002 (04-REFERENCE scope, concept-ledger layer):** **≥ 15** un-homeable REF-family concepts (M-00 prerequisite + M-01…M-14), which the engine cannot even inventory because `REF` is not a recognized family. These are invisible to `closure.json` — they are outside its extraction namespace, so `gap_total=0` does **not** mean "no REF gaps"; it means "no gaps *among the IDs the engine chooses to extract*."

**Reconciled answer to Q8:** The honest gap count depends on the closure question being asked:
- *"Are the extracted ID-bearing concepts homed?"* → **0** (current tool).
- *"Is every architectural concept from every authoritative source homed at the concept layer?"* → **at least 15 REF-family gaps + the whole REF/CAT/GEN family namespace**, per RA-002, plus the fact that this predicate is **UNPROVEN** because Phases 2–4 (extraction/normalization/matching) were never run against the REF corpus.

---

## Determination summary (concept layer)

| Dimension | Committed Repository Truth | Current derived tool (`closure.json`@HEAD) | Stale report (`19/20`@`b67a720`) |
|-----------|:--------------------------:|:------------------------------------------:|:--------------------------------:|
| Authority | none over concept layer | AUTHORITY = NONE | AUTHORITY = NONE |
| Concept closure claim | **silent (none)** | CLOSED (homing gate) | FAIL-CLOSED (with traceability) |
| Concept count | not committed | 431 | 506 |
| Homed | not committed | 431 | 396 |
| Gaps | not committed | 0 (extraction-scoped) | 110 |
| REF family | 7 REF **artifacts** committed + registered; REF **concepts** not homed | REF not extracted | REF not extracted |

**Bottom line:** the committed repository is silent on concept-layer closure by design; the two derived signals differ only because they are regenerations at different commits with different scopes; and neither carries authority. The concept layer is an **un-ratified, tool-served dimension**, not a closed constitutional layer.

*END — RTR-001 · Output 02 · AUTHORITY = NONE (DERIVED TRUTH). Read-only.*
