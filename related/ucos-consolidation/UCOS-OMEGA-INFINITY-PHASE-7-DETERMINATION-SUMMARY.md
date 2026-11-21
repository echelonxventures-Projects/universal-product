# UCOS Ω∞ — PHASE 7 DETERMINATION SUMMARY

**Checkpoint:** `03179308` (integration/recovery-001)
**Compiled:** 2026-08-22
**Posture:** Discovery, determination and preparation only. **No implementation performed. No identity minted. No irreversible action executed. No final certification claimed.**

**Companion reports produced this pass:**
- `REQ-43-STORAGE-NEUTRALITY-DETERMINATION-REPORT.md` (Phase 7A)
- `REQ-28-CORPUS-REGISTRATION-READINESS-REPORT.md` (Phase 7B)
- `P4-F-007-TEMPORAL-EVENT-OWNERSHIP-DETERMINATION.md` (Phase 7C)

---

## 1 — Counts

### 1.1 Current, verified — unchanged by this pass

Nothing was implemented and no decision was registered, so no requirement changed status.

| Status | Count |
|---|---|
| **CERTIFIED** | **43** |
| **GOVERNED CLOSURE** | **0** |
| **OPEN GAP** | **2** — `REQ-28`, `REQ-43` |
| **SUPPORTED** | **2** — `REQ-46`, `REQ-47` |
| **NOT APPLICABLE** | **2** — `REQ-44`, `REQ-45` |
| **Total** | **49** |

### 1.2 Certification-integrity flag raised this pass

**`REQ-38` and `REQ-39` are `CERTIFIED` on evidence affected by a defect found during Phase 7B.**

`platform/repository_intelligence/mutation_classification.py:139-146` calls `git ls-files`
without `-z` or `-c core.quotePath=false`. Git C-quotes and octal-escapes non-ASCII paths, so
**117 tracked files whose names contain `Ω∞` never appear in `Repository.tracked` as their
real paths**. Because `_r01_repository_state` claims any existing path *not* in `tracked`, all
117 are absorbed into `REPOSITORY_STATE` before any later rule runs.

| | Current (defective) | Corrected `tracked` set |
|---|---|---|
| `REPOSITORY_STATE` | **117** | 0 |
| `AUTHORED_DOCUMENT` | 0 | 19 |
| `UNRESOLVED` (fail-closed) | 0 | 98 |

The certification claims themselves are real — `classify()` **is** data-driven and **does**
fail closed. But 117 real artifacts are currently assigned a **wrong** authority
(`UCOS-RIB-001` GATE-02/12 instead of their own), and REQ-38's "0 unresolved" holds partly
because the defect routes them into a class before the fail-closed terminal is reached.
`platform/tests/test_mutation_classification.py` (44 passing) never drives the real
`git ls-files` path against a non-ASCII name, so nothing catches it.

**These two are not being downgraded here** — that is the matrix owner's call on corrected
evidence. They are **flagged**, and re-assessment on corrected output is a prerequisite in
§5. Also corrected: REQ-39's cited test count is **44**, not the 53 the matrix states.

### 1.3 Projected, once §5 completes — not claimed, stated as a target

| Status | Count | Change |
|---|---|---|
| **CERTIFIED** | 44 | `REQ-28` closes on real mint evidence |
| **GOVERNED CLOSURE** | 1 | `REQ-43` — abstraction declined by decision |
| **OPEN GAP** | 0 | — |
| **SUPPORTED** | 2 | unchanged |
| **NOT APPLICABLE** | 2 | unchanged |
| **Total** | **49** | |

Contingent on REQ-38/REQ-39 surviving re-assessment on corrected classification output. If
either does not, the CERTIFIED figure drops accordingly and this projection is wrong.

---

## 2 — REQ-43 determination

### **B — forced abstraction causing architectural damage.**

Measured, not assumed: `PersistenceAdapter`'s **only** production consumers are inside
`engine/uckp` (`universe.py`, `cli.py`, `validation.py`). `KnowledgeStore`'s 14 production
call sites all point at the repository's one canonical knowledge directory.

Against the directive's five proceed-criteria:

| Criterion | Verdict | Why |
|---|---|---|
| No duplicate persistence authority | **FAIL** | `_guard_writable()` enforces **DP-03** via a repo-relative path. Under a memory/database/cloud adapter it does not fail — it **silently succeeds**. The rule is not repealed; the surface it applies to dissolves. |
| No behavior regression | **FAIL** | REQ-14 (archive-before-overwrite ordering) and REQ-34 (keyed provenance sibling stream) — both certified by `DEC-ADR-0025` **this session** — live exactly at the boundary an adapter replaces. `PersistenceAdapter` has no ordering or multi-stream concept. |
| UCKP tests unchanged | pass | Non-discriminating; noted, not used as support. |
| KnowledgeStore gains real capability | **FAIL** | Nominal only. Zero second consumers. The Knowledge Once Principle makes the store singular **by law**. |
| Abstraction stays technology-independent | **FAIL** | Mutually exclusive with fidelity: preserving DP-03 + REQ-14/34 requires repo-relative paths, write ordering and keyed sibling streams — all filesystem-and-git shaped. |

**A finding the roadmap missed.** `UCOS-ARCHITECTURAL-OPENNESS-ROADMAP.md` Phase 3 named one
obstacle — hard-typing to `UCKO`. The larger one is **cardinality**: `PersistenceAdapter`
models one homogeneous collection; `KnowledgeStore` persists **four streams of three types
with three different write disciplines** (canon/decisions overwrite, history appends,
provenance is independently keyed). Neither mapping survives — four adapters break `save()`'s
archive-then-write ordering; one composite adapter voids `universe_digest`,
`require_integrity` and the equality check that give the contract its entire fail-closed
value. The roadmap's "genuine candidate" classification was made on type-shape similarity
before the four-stream structure and the DP-03 coupling were read, and is **superseded**.

**Recommended disposition:** a `CEP-002 Article 28` decision recording the decline
(`adr/0028`), moving REQ-43 `OPEN GAP` → `GOVERNED CLOSURE`, **never `CERTIFIED`** — nothing
was built. Precedent exists: REQ-15 (`disclosed non-openness by design`) and REQ-48
(`correctly closed, not a gap`).

**Re-open condition, stated so this is not read as permanent:** a real second storage target.
This is a determination about the present consumer set, not a prohibition.

**Narrower option, recorded but not recommended:** if the intent is "less coupling to JSON"
rather than "swappable storage," `_read_json`/`_write_json` are the only two methods naming
an encoding. An injected `KnowledgeCodec` would keep DP-03 and the archive ordering inside
`KnowledgeStore` and trip none of the four failures above. It still has no second consumer,
so it is on the table with an honest label rather than proposed.

---

## 3 — REQ-28 registration readiness

### **NOT READY TO MINT.** Population exact; authority mapping not.

**Population — verified, individually enumerated** (all 192 listed in the companion report §4):

- `1425 eligible − 1233 registered = 192`, independently recomputed against
  `ukb._iter_files()` and `artifacts.json`.
- 189 `.md` + 3 `.json`; 178 repository root, 11 `adr/`, 3 `engine/`.
- **All 192 are version-controlled** (`git ls-files --cached`).
- **Intersection with the 25 VCS-unbound candidates = 0.** The 25 are a disjoint advisory
  set and are correctly excluded — they include this pass's own untracked reports.
- `ukb` classification is total: **0 unclassified**.

**Blocker 1 — 172 of 192 have no resolvable governing authority.** Under the repository's own
resolver: 172 `UNRESOLVED`, 19 `AUTHORED_DOCUMENT`, 1 `REPOSITORY_STATE`. Isolated cause
across the 189 markdown members: **170 fail `self-declared-authority`** (no `Authority:` or
`Deciders:` field), 1 fails `repository-controlled`. This is Class 7 correctly refusing and
`classify()` correctly failing closed — designed behaviour, not a bug. It does **not** block
`ukb` registration; it blocks writing the decision **truthfully**, because the directive
requires an authority per artifact.

*Resolution:* the decision names `REG-AUTO-001` as registering authority for the whole
population and **discloses** the 172-artifact mutation-authority residual as explicitly out
of scope. Editing 170 files to add headers is correct follow-on work, not a precondition.

**Blocker 2 — the §1.2 defect**, which currently puts a *wrong* authority on 117 files
repo-wide, one of them inside this very population
(`UCOS-Ω∞-FINAL-REPOSITORY-READINESS-DETERMINATION.md`). **Must be fixed before minting**, or
192 permanent identities get bound to a decision whose authority column is wrong.

**Irreversible footprint — quantified:** +192 permanent Universal IDs (`by_path` 1,264 →
1,456; **0 of the 192 hold a prior entry**, so all are fresh), ≈**+865** permanently allocated
pages (`page_cursor` 9,826 → ≈10,691), append-only by construction.

**Rollback limitation — there is none.** `git revert` restores the ledger *files* but does not
un-mint: it re-opens `page_cursor` to re-allocate the same pages, breaking the append-only
invariant `ukb.py validate` asserts, and orphans any minted ID captured downstream. A revert
is a constitutional-invariant violation, not a recovery. The only mitigation is verifying the
population is still exactly 192 immediately before minting.

**Decision draft prepared** — exact population, authority, irreversible-action disclosure,
V1–V10 validation criteria, rollback limitation, E1–E8 evidence requirements — in the
companion report §6. **Not registered. `register.sh --mint` not executed.**

---

## 4 — TemporalEvent ownership determination

### **B — valid specialized projection. Not a duplicate authority. Nothing to remove.**

| | `engine.temporal` (CMG-000002) | `engine.uckp.values.TemporalEvent` |
|---|---|---|
| Question answered | *when*, in which reference frame | *in what order*, within one object's lifecycle |
| Ordering | frame-qualified coordinate; `compare()` → `INCOMPARABLE` across frames | integer `sequence`, single-object scope |
| Frame | required — that is the point | **none — `at = TIMELESS`** |
| Keyed by | `subject_identity` (a Universal Identity) | position in `UCKO.temporal_history` |

`engine/uckp` imports nothing from `engine.temporal` and vice versa — **zero coupling, no
shadowing.** `TemporalEvent` is constructed at exactly three sites, all in `ucko.py`
(mint, `transition_to`, `from_dict`), and **`at` is never assigned at any of them.**

**The decisive point:** `TIMELESS` is REQ-22 (*no default temporal reference frame*, CERTIFIED)
being **honoured**, not a weakness. Re-typing `UCKO.temporal_history` to `TemporalCoordinate`
would force a reference system at mint time — where none is available — leaving only two
outcomes: supply a default frame (**violates REQ-22**, the exact defect `adr/0012` removed),
or fail the mint. Recording the ordinal fact without asserting a frame is the third, correct
answer. The "weaker" model is weaker **on purpose**, and merging it would regress a certified
requirement.

Ownership is therefore already unambiguous: frame-qualified time → CMG-000002; per-object
constitutional state ordering (Facet 11) → UCKP Layer Zero. Neither owner's registry contains
the other's concept.

**The one real residue.** `TemporalEvent.at` is an unconstrained `str`. Nothing prevents a
record carrying `"2026-08-22"` — a bare, unqualified time with no reference system, exactly
what REQ-22 forbids. No current site does this and no on-disk record contains it, but the
**type permits it**. Recommended closure, integration-shaped and small: a `__post_init__`
accepting `TIMELESS` or requiring `engine.temporal.coordinate.parse_qualified` (which already
exists, `coordinate.py:291`) to succeed — the same shape as `DEC-ADR-0015`'s fix, adding the
first `engine/uckp` → `engine/temporal` edge. ~3 tests, no new capability.

**Stale text to correct:** `PHASE-4-CAPABILITY-GAP-MATRIX.md:176`'s "no call site outside its
own package" has been false since `DEC-ADR-0015`; its "weaker rival" framing is superseded;
`FINAL-UNIVERSAL-INFINITE-EXPANSION-FOUNDATION-CERTIFICATION-REPORT.md:100`'s "retire or
reconcile" is answered by **neither** — bound it.

---

## 5 — Exact implementation sequence to reach 100%

Ordered by dependency. **Steps 1–5 are prerequisites, not follow-ups** — they change what
later decisions may truthfully assert.

| # | Step | Owner | Gate / acceptance |
|---|---|---|---|
| **A — Restore classification soundness** ||||
| 1 | Fix `Repository.tracked` → `git -c core.quotePath=false ls-files -z`, split on `\0` (`mutation_classification.py:139-146`) | `platform.repository_intelligence` | 44 existing tests still pass |
| 2 | Add a regression test using a **non-ASCII** filename fixture against the real `git ls-files` path | same | new test passes; defect cannot recur |
| 3 | Re-run classification repo-wide; record the corrected distribution | same | 117 no longer `REPOSITORY_STATE` |
| 4 | Re-assess **REQ-38 / REQ-39** against corrected output; adjust status if warranted | matrix owner | matrix carries real numbers |
| 5 | Correct REQ-39's cited test count **53 → 44** | matrix owner | matrix diff |
| **B — Close REQ-43 by decision** ||||
| 6 | Author `adr/0028-req-43-knowledgestore-storage-neutrality-decline.md`, citing the determination report's five-criterion scorecard and its re-open condition | UKDA + Constitutional Authority | decision in the UCDA register |
| 7 | REQ-43 → **`GOVERNED CLOSURE`** (never `CERTIFIED`) | matrix owner | matrix diff |
| 8 | Correct `UCOS-ARCHITECTURAL-OPENNESS-ROADMAP.md` Phase 2/3's superseded "genuine candidate" line | roadmap owner | roadmap diff |
| 9 | Confirm zero source change | `git diff --stat engine/` empty; 618 / 52 / 21 baselines hold |
| **C — Close P4-F-007 remainder** ||||
| 10 | Bind `TemporalEvent.at` to `TIMELESS`-or-`parse_qualified` via `__post_init__` | `engine/uckp` ← `engine/temporal` (CMG-000002) | ~3 new tests; full `engine/tests/uckp/` green |
| 11 | Record the ownership determination against `WP-UCDA-028`'s P4-F-007 sub-obligation | UCDA | work-package register updated |
| 12 | Correct the stale text in `PHASE-4-CAPABILITY-GAP-MATRIX.md:176` and `FINAL-…-CERTIFICATION-REPORT.md:100` | respective owners | document diffs |
| **D — Close REQ-28** (only after A completes) ||||
| 13 | Register `DEC-ADR-0029` from the readiness report §6, with the 172-artifact residual disclosed | Constitutional Authority | decision in the UCDA register |
| 14 | Re-run `ukb.py enforce --pre`; **confirm still exactly 192** | REG-AUTO-001 | V1 — any `git add` since authoring invalidates the count |
| 15 | Execute `register.sh` (10 phases) — **the irreversible step** | REG-AUTO-001 | V2–V7; `TRANSACTION COMPLETE` |
| 16 | Capture E2–E7; commit artifacts **and** regenerated registers in one commit | REG-AUTO-001 | `register.sh --guard` passes |
| 17 | REQ-28 → **`CERTIFIED`** on mint evidence | matrix owner | `enforce` reports 0 unregistered eligible |
| **E — Final** ||||
| 18 | Full regression + 10-gate re-execution | all | V9, V10 |
| 19 | Recompute the matrix from row-level truth, not the summary table | matrix owner | tally matches §1.3 or is corrected to what it is |
| 20 | Only then consider a certification claim | Constitutional Authority | every OPEN GAP is CERTIFIED or GOVERNED-CLOSED by a registered decision |

### Ordering constraints, explicitly

- **A before D.** Minting binds 192 permanent identities to a decision; that decision's
  authority column must be right first.
- **Step 14 immediately before step 15.** The population is a function of the working tree.
  Authoring these four Phase 7 reports already moved the VCS-unbound count 25 → 29; `git add`
  them and the population is no longer 192.
- **B and C are independent** of A and D and of each other; either can proceed in parallel.
- **Step 15 is the only irreversible action in the sequence.** Everything before it is
  revertible; nothing after it restores the ledger.

---

## 6 — Boundary statement

This pass performed discovery, determination and preparation. **No code changed. No test
changed. No decision registered. No identity minted. No gate re-run beyond the read-only
verification cited.** REQ-28 and REQ-43 both remain **OPEN GAP** at this checkpoint; the
determinations above are the evidence that closing decisions would be built on, not the
closures themselves.

The re-executed evidence cited here is: `engine/tests/knowledge/test_store.py` **21 passed**,
`engine/tests/knowledge/` **618 passed**,
`engine/tests/uckp/test_projection_persistence_execution.py` **52 passed**,
`platform/tests/test_mutation_classification.py` **44 passed**,
`ukb.py enforce --pre` **ENFORCEMENT PASSED, 192 unregistered eligible**. The full regression
suite and the 10 gates were **not** re-run in this pass and no claim is made about them
beyond the prior baseline.

**No final certification is claimed.**
