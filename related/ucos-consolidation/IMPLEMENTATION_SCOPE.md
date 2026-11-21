# PHASE 0 — IMPLEMENTATION SCOPE

**AUTHORITY = NONE (DERIVED TRUTH).** Defines scope. Authorizes no irreversible act, issues no
certification, mutates no ledger, declares no closure.

**Baseline this scope is defined against:** `HEAD` = `77798202d2df43285760b3277f230ebde4b52bbc`,
branch `integration/recovery-001`, 91 uncommitted entries, working-tree fingerprint
`807104baf749fd2614afed1bf080c249`.

---

## 1. IN SCOPE — authorized for implementation

Ordered by position in the critical path, not by severity. Each item names its owner, the reproduced
evidence that admits it, and the mechanical check that closes it.

### S-1 · Make `uga_engine.py run` safe — **FIRST, BEFORE ALL ELSE**

| Field | Content |
|---|---|
| Finding | F-9 (F-N1) |
| Owner | UGA-001 |
| Why first | This phase invoked the command the UGA gate's own output recommends. It printed `minted=0` and had allocated **25 permanent Universal IDs** into `00-BOOK/DATA/id-ledger.json`. Every subsequent remediation task involves invoking governance engines; while one of them can mutate an append-only ledger and report that it did not, no later task is safe |
| Change | (a) report allocations truthfully — the summary line must state the ledger delta; (b) **refuse when `git status --porcelain` is non-empty**; (c) separate the read-only census verb from the allocating verb; (d) the gate's remediation hint must not name an unguarded mutating command |
| Verification | On a dirty tree `run` exits non-zero and writes nothing — `git status --porcelain \| md5` identical before and after. On a clean tree its printed delta equals the measured `id-ledger.json` diff |
| Reversible | Yes — source change only |

### S-2 · Correct the closure report's violation count: 24 → 25

| Field | Content |
|---|---|
| Finding | F-5 (F-C1) |
| Owner | UCOS-OMEGA-001 |
| Why | `uga_engine.py gate` reports **25** violations on `UGA-INV-01` and `UGA-INV-10`. The report enumerates 24. The 25th is `00-MASTER/UCOS-OMEGA-001/OMEGA-CLOSURE-REPORT.md` — the report is itself an unregistered artifact and under-reports its own blocker by exactly itself. **A registration scoped to the report's 24 leaves one artifact anonymous and stage 9 still red.** This is a silent off-by-one on the closure critical path |
| Change | §7 and evidence row 10: 24 → 25; add the report's own path to the enumerated list |
| Verification | The enumerated list equals the gate's `UGA-INV-01` output, path for path |
| Reversible | Yes — document only |

### S-3 · Make the UCI attribution test independent of a gitignored artifact

| Field | Content |
|---|---|
| Finding | F-2 (F-Ω2) |
| Owner | UCI-000001 |
| Why | Reproduced both directions this phase: with `coverage.xml` present the test FAILS (`objects sum to 104, file has 112`); moved aside it passes in 4.43 s. A gate verdict is a function of an untracked, gitignored file, so any CI runner without it passes and any runner with it fails |
| Change | Either make attribution independent of `coverage.xml`, or make the dependency explicit and gate on the file's presence. **Root cause first:** determine whether the 8-statement gap is a defect in attribution or in the raw AST comparison before changing either |
| Verification | The test returns the same verdict with `coverage.xml` present and absent |
| Reversible | Yes |

### S-4 · Correct the stage census: 19 → 20 stages, 13 → 14 passes

| Field | Content |
|---|---|
| Finding | F-6 (F-C2) |
| Owner | UCOS-OMEGA-001 |
| Why | `verify.sh --full` has **20** stages — 19 at column 0 plus the `--full`-only `run_stage "registration observation (register.sh --observe, read-only)"` at `verify.sh:798`. The report's own named pass list contains **14** entries and 14 + 6 = 20. The prose count is wrong; the list is right |
| Change | §5: "19 stages" → 20; "Passed (13)" → "Passed (14)" |
| Verification | Count equals `grep -c run_stage verify.sh` less the function definition, in `--full` mode |
| Reversible | Yes — document only |

### S-5 · Withdraw the stale Ω∞-B provenance warning

| Field | Content |
|---|---|
| Finding | F-7 (F-C3) |
| Owner | UCOS-OMEGA-B-001 |
| Why | All 11 `PHASE_OMEGA_B_*.md` files open by stating that `engine/omega_governance/` "is NO LONGER PRESENT", that reproduction "no longer executes" with `ModuleNotFoundError`, and that the tree "is not recoverable from version control". Reproduced this phase: the tree **is present** with the exact composition §H9 recorded, and `probes/b01_proof_tractability.py` runs to completion, exit 0. The correction **restores** Ω∞-B's standing rather than diminishing it |
| Change | Withdraw or rewrite the warning; record that the tree is present and re-executable, and that it remains **untracked** and therefore still at risk |
| Verification | Each of the five probes executes, exit 0 |
| Reversible | Yes — document only |

### S-6 · Close the lint governance scope gap

| Field | Content |
|---|---|
| Findings | F-10 (F-N2), F-11 (F-N3) |
| Owner | UEC-000001 / UCON-000001 |
| Why | `ucos_ruff_gate` lints tracked `.py` under `engine/` and `platform/` only: 1,584 of 2,197 tracked files. The other **613**, across 9 roots, carry **9,894** violations. The gate PASSES legitimately at its declared scope — the finding is the undeclared boundary, not a false pass. Separately, the gate hardcodes `engine/ platform/` as literals, which is the same enumeration defect the Ω programme deleted 78 `--cov=` flags and 7 `testpaths` to remove — in `verify.sh` stage 1 |
| Change | Route the gate through the Ω root derivation (which already computes all 11 roots). Then either bring the 613 files up to standard, or declare per-root exemptions with written reasons and a **ratchet** so the population may fall and never rise |
| Verification | Adding a tracked root gains lint governance with no edit to `ucos-env.sh`. The violation count is bounded by a declared ratchet |
| Note | Do **not** bulk-autofix. 7,977 of the 9,894 are `S101` (assert in non-test paths) and each needs a judgement, not a rewrite |
| Reversible | Yes |

### S-7 · Import `NoReturn` in `rfp_engine.py`

| Field | Content |
|---|---|
| Finding | F-12 (F-N4) |
| Owner | UCOS-RFP-001 |
| Why | `00-MASTER/UCOS-RFP-001/rfp_engine.py:61` annotates `-> "NoReturn"` and never imports it. **Static-only: the annotation is a quoted string, never evaluated, so there is no runtime defect** — verified by `ast.parse` this phase, not assumed. Included because it sits in a fail-closed abort path and is the cheapest demonstration that S-6's gap is real |
| Change | `from typing import NoReturn`; drop the `# type: ignore` |
| Verification | `ruff check --select F821` on the file is clean |
| Reversible | Yes |

### S-8 · Resolve the two `AM` seal files

| Field | Content |
|---|---|
| Finding | F-23 (V-3) |
| Owner | UCOS-OMEGA-001 |
| Why | `omega-ratchet.json` and `omega-surface.json` are staged **and then modified**, so index content ≠ working-tree content. The Ω gate passes against the working tree (verified, digest `601e4772…`); it was **not** tested against the index. Committing as-is would seal a state no gate run has validated |
| Verification | `git diff --cached` vs `git diff` on both paths; gate re-run against index content, exit 0 |
| Reversible | Yes |

### S-9 · Execute the two unverified evidence items

| Field | Content |
|---|---|
| Findings | F-21 (V-1), F-22 (V-2) |
| Owner | UCON-000001 / UCAF-001 / UVI-000001 |
| Why | Neither the UCON/UCAF gates nor the full coverage run nor end-to-end `verify.sh --full` was executed this phase. 95.26 % is **UNVERIFIED** and may not be certified |
| Change | None — execution and evidence capture only |
| Method | **Establish each gate's read-only property first**, by md5-comparing `git status --porcelain` across it, exactly as was done for the Ω and UGA gates. F-9 proves a governance engine here can mutate a ledger while reporting it did not. Then: UCON and UCAF on the frozen baseline; re-run with untracked trees stashed; compare. Then `verify.sh --full` once, on a clean tree, stdout captured |
| Reversible | Read-only if the precondition holds; **that is what makes the precondition mandatory** |

### S-10 · Adjudicate the 91 working-tree entries

| Field | Content |
|---|---|
| Finding | F-4 (F-Ω5) |
| Owner | Repository Owner |
| Why | The GIT CLEAN INVARIANT fails and gates D5. 30 of the 91 entries are untracked and sit inside `register.sh`'s eligibility universe |
| Change | Adjudicate by class, per the measured composition: **23 `A ` + 17 `M ` staged** (the Ω change) — commit; **19 ` M`** UAKOS-CLOSURE-008 / UCAF registers — confirm producer-regenerated, then commit or revert; **2 `AM`** — S-8 first; **30 `??` untracked** — 25 root `PHASE1_*`/`PHASE_OMEGA_A_*`/`PHASE_OMEGA_B_*` documents, 4 directories and 1 script, **all belonging to Ω∞-A/Ω∞-B and none to the Ω change** — disposition separately, **never** via a blanket `git add` |
| Verification | `git status --porcelain` is empty |
| Caution | A blanket `git add` would track the Phase 2 prototype trees, violating P-7 and F-14. The Ω report §6.3 records this already happening once mid-session |

---

## 2. OUT OF SCOPE — explicitly excluded

| # | Item | Reason |
|---|---|---|
| O-1 | **`register.sh`, ledger allocation, identity minting, any append-only governance write** | **D5 = NOT AUTHORIZED** on four independent grounds. Forbidden until all eight prerequisites are reproduced |
| O-2 | **`uga_engine.py run` in its current form** | Allocates 25 permanent IDs while reporting `minted=0` (F-9). Forbidden until S-1 lands |
| O-3 | **Tracking `engine/omega_governance/`, `engine/omega_infinite/`, `engine/tests/omega_infinite/`, `scripts/omega-infinite.sh`** | F-14. 34 untracked `.py`. Tracking them admits them to Ω's population, every coverage denominator and every ratchet, and makes them registration-eligible. **Their untracked state is correct, not a defect** |
| O-4 | **Wiring any Phase 2 code into `verify.sh`, a gate stage, a seal or a ratchet** | Ω∞-B **P-7** and `PHASE_OMEGA_A_ROADMAP.md:184`. Verified holding this phase — no reference in `verify.sh`, `Makefile`, `.github/workflows/`, `pyproject.toml`. **Preserve** |
| O-5 | **Ω∞-B hard entry criteria E-1 … E-6** | F-15 … F-20. Deferred (§3). They govern Ω∞-C entry, not Ω closure |
| O-6 | **The four Ω∞-B active correctness defects** | F-18. Confined to untracked code no gate reaches. Conditional on adoption, which is not decided |
| O-7 | **Re-seeding or rebaselining any Ω-4 ratchet** | All 9 bounds verified HELD or JUSTIFIED with 0 regressions. Re-seeding is forbidden by the freeze and unnecessary |
| O-8 | **Publishing closure certification or declaring completion** | D4 = NO. Eight of eight closure requirements fail |
| O-9 | **New Ω functionality** | The closure mandate admits defect fixes, consumer updates, registrations and recorded seals only |
| O-10 | **Bulk `ruff --fix` across the 613 ungated files** | 7,977 of 9,894 are `S101`; each needs judgement. A bulk rewrite of 613 files during closure is unreviewable |
| O-11 | **Re-arming `.kiro/hooks/auto-register-artifact.json`** | Frozen for cause. Its own record: 166 registered-but-untracked ledger sources, 62 minted in one hour, 29 identities for gitignored non-artifacts. Both stated lift conditions are unmet |

---

## 3. DEFERRED — requiring later governance action

| # | Item | Finding | Gate on it |
|---|---|---|---|
| D-1 | E-1 — mechanical check that every module named in a package's own docs exists | F-15 | Ω∞-C entry. Fact reproduced: 9 of 11 named modules absent; `state.py:58` asserts an absent proof. Ω∞-B calls this the single most important criterion because it makes the others checkable |
| D-2 | E-2 — record the register shape (DAG vs chain) before `registry.py` is written | F-16 | Ω∞-C entry. **Cost is zero now and rises after.** `registry.py` is absent |
| D-3 | E-3 — amend Ω∞ Rule 9 to separate code migration from record backfill | F-17 | Governance Authority. An unmeetable criterion makes every assessment against it dishonest |
| D-4 | E-4 — close the four active correctness defects | F-18 | Conditional on adopting `omega_governance` |
| D-5 | E-5 — guards + certification inputs as one item, **`blocked_by` retained** | F-19 | Ω∞-C entry. B-01 and B-05 pull opposite ways on one field; a naive migration destroys the structural proof |
| D-6 | E-6 — no vocabulary-identity work described as closing A-14 | F-20 | Ω∞-C entry. Guards against false assurance; the agreement half is FUNDAMENTAL |
| D-7 | Registration eligibility policy reconciliation (`config.py REGISTRATION_SCOPE` vs `ukb.py:697`) | F-9, D5 | **Prerequisite to D5.** 70 untracked paths, 30 corpus-matching, currently registration-eligible |
| D-8 | Disposition of prior append-only ledger damage | D5 | **Prerequisite to D5** and to lifting the hook freeze |
| D-9 | Ω-4 declared floors — `unexplained_exemptions` 2, `unnameable_exemptions` 49, `unreachable_artifacts` 53 | — | Owner decisions about dead code and script importability, not settings. All three currently JUSTIFIED; each floor names what would close it |
| D-10 | Supply the *PHASE 2 CLOSURE ARBITRATION DETERMINATION* if it exists outside this repository | F-13 | If supplied, re-run Phase 0 against it. This baseline stands as substitute meanwhile |

---

## 4. AUTHORIZATION

```text
IMPLEMENTATION AUTHORIZED WITH CONDITIONS
```

**Authorized** because the Ω programme's implementation is complete and independently verified at
tier 1 (D1: gate PASS, 198 tests green, determinism matching to the exact byte and SHA-256, read-only
confirmed), because every closure blocker now has a reproduced measurement and a named owner, and
because S-1 … S-10 are reversible source and document changes touching no append-only ledger.

**Conditions — all five bind before any work begins:**

1. **The ten-row all-PASS table is void as a baseline** (F-8). Five of ten rows are refuted by
   reproduced execution and it contradicts the report it summarises. The baseline is
   `IMPLEMENTATION_BASELINE_ACCEPTED.md` §0, fingerprint `807104baf749fd2614afed1bf080c249`.
2. **S-1 lands first.** No governance engine may be invoked for remediation until
   `uga_engine.py run` reports truthfully and refuses on a dirty tree.
3. **D5 = NOT AUTHORIZED.** No `register.sh`, no ledger allocation, no identity minting, no
   append-only write, until all eight prerequisites in `ARBITRATION_ACCEPTANCE_RECORD.md` §3/D5 are
   reproduced.
4. **Phase 2 stays out** (O-3, O-4). P-7 verified holding; preserve it.
5. **Unverified stays unverified** (S-9). 95.26 %, the per-stage census and the UCON/UCAF verdicts may
   not appear in any certification until reproduced.

---

## 5. SEQUENCING RULE

Per item, without exception:

```text
ANALYZE → IMPLEMENT → VERIFY → VALIDATE → REVIEW → COMMIT → GIT CLEAN → BASELINE → CONTINUE
```

`IMPLEMENT → IMPLEMENT → VERIFY LATER` is prohibited. After each item
`git status --porcelain` must be **empty**; if not, the phase refuses and no next action is
authorized. Record the new fingerprint after each commit and carry it as the baseline for the next
item.

---

## 6. CRITICAL PATH — ordered implementation sequence

| Step | Item | Why here | Exit check |
|---|---|---|---|
| **1** | **S-1** — make `uga_engine.py run` safe | Every later step invokes governance engines. While one can mutate an append-only ledger reporting `minted=0`, no later step is safe. This is the only step that must precede all others | On a dirty tree: exits non-zero, `git status` md5 unchanged |
| **2** | **S-2** — 24 → 25 | The registration set must be correct **before** anyone registers. Registering the report's 24 leaves one artifact anonymous and stage 9 red | Enumerated list = gate output, path for path |
| **3** | **S-8** — resolve the two `AM` seal files | Must precede any commit; committing the index as-is seals a state no gate validated | Gate exit 0 against index content |
| **4** | **S-3** — UCI attribution independent of `coverage.xml` | The only reproduced test failure. Must be green before the full suite is meaningful | Same verdict with the file present and absent |
| **5** | **S-4, S-5, S-7** — document corrections + the `NoReturn` import | Independent, cheap, no dependants. Batch as one reviewed change | Counts match `verify.sh`; probes exit 0; `F821` clean |
| **6** | **S-10** — adjudicate the 91 entries | Requires steps 3–5 to have settled what is committable. **Adjudicate by class; never a blanket `git add`** — that would track the Phase 2 trees and breach P-7 | `git status --porcelain` **empty** |
| **7** | **S-9** — execute V-1 and V-2 | Needs a clean tree (step 6) to be meaningful. Establish each gate's read-only property **first** | Raw output captured; UCON/UCAF verdicts recorded; coverage figure reproduced or recorded UNVERIFIED |
| **8** | **S-6** — close the lint scope gap | Largest change, no closure blocker depends on it, and it must not destabilise steps 1–7 | New tracked root gains lint governance with no `ucos-env.sh` edit; ratchet declared |
| **9** | **STOP — owner decision gate** | D5 prerequisites 1–7 are now met. Prerequisite 8, written owner authorization naming the 25 paths and the expected ledger delta, **cannot be produced by implementation** | Written authorization exists, or the sequence halts here |
| **10** | Registration — `register.sh` → `uga_engine.py gate` → `verify.sh --full` | **ONLY after step 9.** On a clean tree, ledger diff reviewed before commit | UGA gate exit 0; `verify.sh --full` exit 0; `git status` empty |

**Step 9 is a hard stop.** Steps 1–8 are fully authorized and reversible. Step 10 is not authorized by
this document and cannot be authorized by any amount of implementation work — it requires a recorded
owner decision. **An implementation run that reaches step 9 and halts has succeeded, not failed.**

---

## 7. WHAT WOULD FALSIFY THIS SCOPE

Recorded so the scope can be refused on evidence rather than defended.

| # | Observation that would invalidate it |
|---|---|
| 1 | The *PHASE 2 CLOSURE ARBITRATION DETERMINATION* is produced from outside this repository and contains findings not among the 23 classified here. Then D-10 fires and Phase 0 re-runs |
| 2 | `uga_engine.py gate` reports a count other than 25 on a tree with fingerprint `807104ba…`. Then S-2's target is wrong and the discrepancy is a deeper defect |
| 3 | A `verify.sh` stage other than 9 fails on the frozen baseline. Then D2's single named cause is incomplete and V-2 must run before any scope is trusted |
| 4 | The UCON or UCAF gate fails over the **tracked** population. Then V-1 resolves against the report, the Ω report §6.2 is wrong, and two further blockers enter scope |
| 5 | `engine/omega_governance/` proves to be referenced by a tracked artifact. Then P-7 is already breached, F-14 changes from "preserve" to "remediate", and O-3/O-4 must be reopened |
| 6 | The full coverage run does not reproduce ≥ 90 %. Then the coverage gate is a second failing stage and D2's cause list grows |
