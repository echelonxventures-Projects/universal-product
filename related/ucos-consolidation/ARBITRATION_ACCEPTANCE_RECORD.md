# PHASE 0 — ARBITRATION ACCEPTANCE RECORD

**AUTHORITY = NONE (DERIVED TRUTH).** No certification, no seal, no ratchet advancement, no identity
minting, no ledger mutation, no closure declaration.

**Baseline:** `HEAD` = `77798202d2df43285760b3277f230ebde4b52bbc` on `integration/recovery-001`,
plus 91 uncommitted entries, working-tree fingerprint `807104baf749fd2614afed1bf080c249`.

**Procedural note governing this record.** The named input *PHASE 2 CLOSURE ARBITRATION
DETERMINATION* does not exist in this repository (finding F-N5; `grep -ril "closure arbitration"`
returns nothing). No arbitration findings could therefore be adjudicated as such. This record
adjudicates the **23 findings actually present in the closure evidence**, numbered F-1 … F-23 in the
decision table and cross-referenced to the derived IDs in `IMPLEMENTATION_BASELINE_ACCEPTED.md`.

---

## 1. GOVERNANCE DECISION TABLE

| # | Finding ID | Accepted | Owner | Action Required | Blocking Status | Notes |
|---|---|---|---|---|---|---|
| F-1 | F-Ω1 | **Y** | UGA-001 + Repository Owner | Allocate 25 Universal IDs via `register.sh`, then re-run UGA gate | **BLOCKING — CLOSURE** | Tier 1. 25 not 24 (F-C1). Requires owner authorization; **NOT authorized now** (D5) |
| F-2 | F-Ω2 | **Y** | UCI-000001 | Make attribution independent of gitignored `coverage.xml`, or declare the dependency and gate on it | **BLOCKING — TEST** | Tier 1, isolation reproduced both directions |
| F-3 | F-Ω4 | **Y** | UVI-000001 (stage registry) | None directly — clears when F-1 clears | **BLOCKING — CLOSURE** | Tier 1. Stage 9 fails in isolation; dispositive of `verify.sh --full` |
| F-4 | F-Ω5 | **Y** | Repository Owner | Adjudicate 23 `A ` + 17 `M ` staged, 19 ` M` modified, 2 `AM`, 30 `??` untracked; commit or revert each class | **BLOCKING — INVARIANT** | Tier 1. 91 entries. Gates D5 |
| F-5 | F-C1 | **Y** | UCOS-OMEGA-001 | Correct §7 and evidence row 10: 24 → 25; add `OMEGA-CLOSURE-REPORT.md` to the list | **BLOCKING — CORRECTNESS** | Tier 1 over tier 4. Report under-reports its blocker by itself |
| F-6 | F-C2 | **Y** | UCOS-OMEGA-001 | Correct §5: 19 → 20 stages, "Passed (13)" → "Passed (14)" | NON-BLOCKING | Tier 1. Named list already correct; only the count is wrong |
| F-7 | F-C3 | **Y** | UCOS-OMEGA-B-001 | Withdraw or rewrite the provenance warning in all 11 `PHASE_OMEGA_B_*.md` preambles | NON-BLOCKING | Tier 1. Tree present, probe b01 exit 0. Correction *restores* standing |
| F-8 | F-C4 / R-2 | **N — REJECTED** | Repository Owner | Do not use as baseline; re-assert only after F-1, F-3, F-4 are green | **BLOCKING — GOVERNANCE** | Tier 1 refutes 5 of 10 rows; contradicts the report it summarises |
| F-9 | F-N1 | **Y** | UGA-001 | `run` must refuse on a dirty tree; report allocations truthfully; gate hint must not name it unguarded | **BLOCKING — SAFETY** | Tier 1, demonstrated and reverted by this phase. `minted=0` was false |
| F-10 | F-N2 | **Y** | UEC-000001 / UCON-000001 | Extend lint governance to the 613 ungated tracked files, or declare the boundary and count it | CRITICAL — NON-BLOCKING | Tier 1. 9,894 violations across 9 roots. Gate passes legitimately at its own scope |
| F-11 | F-N3 | **Y** | UEC-000001 | Route `ucos_ruff_gate` through the Ω root derivation instead of the literals `engine/ platform/` | MEDIUM — NON-BLOCKING | Tier 2. Same enumeration defect Ω exists to remove, in verify.sh stage 1 |
| F-12 | F-N4 | **Y** | UCOS-RFP-001 | Import `NoReturn` or drop the annotation | COSMETIC | Tier 1. Static-only — quoted annotation is never evaluated; **no runtime defect** |
| F-13 | F-N5 | **Y** | Repository Owner | Supply the arbitration determination if it exists elsewhere, or accept this baseline as substitute | **BLOCKING — PROCEDURAL** | Tier 1 absence. Phase 2 is unstarted, so no Phase 2 closure exists to arbitrate |
| F-14 | F-N6 | **Y** | Repository Owner | **Preserve as-is.** Do not track, do not wire, do not register | **BLOCKING — D5 INPUT** | Tier 1. 34 untracked `.py`; P-7 verified holding — no gate reference |
| F-15 | F-B1 (E-1) | **Y — DEFERRED** | Phase 2 / Ω∞-C | Mechanical check that every module named in a package's own docs exists | DEFERRED | Tier 1 on the fact: 9 of 11 named modules absent; `state.py:58` asserts an absent proof |
| F-16 | F-B2 (E-2) | **Y — DEFERRED** | Phase 2 / Ω∞-C | Record register shape (DAG vs chain) before `registry.py` is written | DEFERRED | Zero cost now, rising later. `registry.py` absent |
| F-17 | F-B3 (E-3) | **Y — DEFERRED** | Governance Authority | Amend Ω∞ Rule 9 to separate code migration from record backfill | DEFERRED | An unmeetable criterion makes every assessment against it dishonest |
| F-18 | F-B4 (E-4) → F-B7 | **REQUIRES REVIEW** | Phase 2 / Ω∞-C | Re-measure the 4 defects if `omega_governance` is adopted | DEFERRED — CONDITIONAL | Tier 4. Confined to untracked code no gate reaches |
| F-19 | F-B5 (E-5) | **Y — DEFERRED** | Phase 2 / Ω∞-C | Treat guards + certification inputs as one item; **retain `blocked_by`** | DEFERRED | B-01 and B-05 pull opposite ways on one field |
| F-20 | F-B6 (E-6) | **Y — DEFERRED** | Phase 2 / Ω∞-C | Any vocabulary-identity work must state it closes *detection*, not *agreement* | DEFERRED | Guards against false assurance; A-14 agreement half is FUNDAMENTAL |
| F-21 | V-1 | **REQUIRES REVIEW** | UCON-000001 / UCAF-001 | Execute both gates on the frozen baseline; re-run with untracked trees stashed; compare | **UNVERIFIED** | Not executed this phase. Neither PASS nor FAIL may be claimed |
| F-22 | V-2 | **REQUIRES REVIEW** | UVI-000001 | Run `verify.sh --full` + full coverage once, on a clean tree, read-only properties established first | **UNVERIFIED** | 95.26 % not reproduced. FAIL verdict on verify.sh does **not** depend on this |
| F-23 | V-3 | **REQUIRES REVIEW** | UCOS-OMEGA-001 | Compare index vs working tree for the two `AM` seal files; re-run gate against index | MINOR | Committing the index as-is would seal a state no gate run validated |

### Tally

| Disposition | Count | IDs |
|---|---|---|
| **Accepted** | 18 | F-1 … F-7, F-9 … F-17, F-19, F-20 |
| **Accepted — Deferred to Phase 2** | 6 | F-15, F-16, F-17, F-19, F-20 (+F-18 conditional) |
| **Rejected** | 1 | F-8 |
| **Requires Review** | 4 | F-18, F-21, F-22, F-23 |
| **Blocking** | 9 | F-1, F-2, F-3, F-4, F-5, F-8, F-9, F-13, F-14 |

---

## 2. EVIDENCE HIERARCHY CONFLICTS — RECORDED AND RESOLVED

Applied strictly: reproduced execution > source inspection > artifact inspection > report statement.

| # | Conflict | Lower claim | Higher evidence | Resolution |
|---|---|---|---|---|
| 1 | Registration status | Table row: "Registration Complete PASS" (tier 4) | UGA gate exit 1, 25 violations (tier 1) | **Tier 1 wins.** 25 anonymous objects |
| 2 | `verify.sh --full` | Table row: "PASS" (tier 4) | Stage 9 fails in isolation (tier 1) + verify.sh source (tier 2) | **Tier 1 wins.** FAILS |
| 3 | Tree cleanliness | Table row: "Tree Clean PASS" (tier 4) | `git status --porcelain` = 91 (tier 1) | **Tier 1 wins.** Not clean |
| 4 | Ω verification | Table row: "Ω Verification PASS" (tier 4) | Ω report "CLOSURE INCOMPLETE" (tier 3) + stage 9 (tier 1) | **Tier 1 wins.** Incomplete |
| 5 | Violation count | Report §7: 24 (tier 4) | UGA gate: 25 (tier 1) | **Tier 1 wins.** 25, incl. the report itself |
| 6 | Stage census | Report §5: 19 stages, 13 pass (tier 4) | 20 `run_stage` sites incl. verify.sh:798 (tier 2); report's own list names 14 (tier 3) | **Tier 2 wins.** 20 stages, 14 passes |
| 7 | Ω∞-B reproducibility | Preamble: tree "NO LONGER PRESENT", probes "no longer execute" (tier 4) | `ls` shows tree; probe b01 exit 0 (tier 1) | **Tier 1 wins.** Warning is stale |
| 8 | Ledger safety | `uga_engine.py run` prints `minted=0` (tier 4) | Ledger diff: +25 IDs, 5 counters incremented (tier 1) | **Tier 1 wins.** `minted=0` is false |
| 9 | Ruff cleanliness | *This phase's own initial repo-wide reading:* 9,988 errors | `ucos-env.sh:321` scope = tracked `.py` under `engine/`+`platform/` = 1,584 (tier 2) | **NO CONFLICT.** Scopes differ. The report's claim is **correct and reproduced**. Recorded because a false conflict was nearly filed; source inspection prevented it |

Conflict 9 is retained deliberately. The Root Cause Rule required establishing the gate's declared
scope before comparing numbers; doing so converted an apparent contradiction into finding F-N2, a
genuine and previously unrecorded governance scope gap.

---

## 3. REQUIRED DETERMINATIONS

### D1 — Is Ω implementation complete?

```text
YES
```

Scoped precisely: **the Ω programme's own implementation is complete.** Registration of its outputs is
a separate act (D5) and its absence is not an implementation defect.

Supporting evidence, all tier 1 and all reproduced this phase:

| Evidence | Result |
|---|---|
| `python -m engine.universal_discovery.gate` | `PASS — all five Ω criteria hold`, exit 0 |
| Ω-1 discovery | 2,197 tracked modules → 11 roots, 7 test roots, 80 packages; **0** `--cov=` flags, **0** `testpaths`, **0** `source` entries |
| Ω-2 authority | 100.0 % coverage, 81 authorities, `Ω-A-07` fallback fires **0** times |
| Ω-3 graph | 2,144 / 2,197 reachable, 22 unresolved dynamic sites, relocation invariance holds for all 2,197 |
| Ω-4 ratchets | 9 bounds — 3 JUSTIFIED at declared floors, 6 HELD, **0 REGRESSED** |
| Ω-5 disposition | 2,118 + 61 + 5 + 13 + 0 = 2,197; orphans **0** |
| Measured surface | 90.3034 % |
| Test suite | `198 passed, 1 skipped in 126.58s` |
| Determinism | two renders `1281418` bytes, `cmp` identical, SHA-256 `601e4772…f844a` — **matches the report to the character** |
| Read-only | `git status --porcelain \| md5` identical across a gate run |
| Lint (declared scope) | `All checks passed! 1584 files already formatted`, exit 0 |

Every quantitative claim the Ω Closure Report makes about the Ω programme itself was re-measured and
matched exactly. **The two corrections found (F-C1, F-C2) are both in the report's accounting of
*other* systems, not in Ω's own measurements.**

---

### D2 — Is Ω verification complete?

```text
NO
```

Two independent reasons, neither resting on a report:

1. **A mandatory verification stage fails.** `verify.sh` stage 9, "universal object governance
   (UGA-INV-01..10)", is an unconditional `run_stage`. Reproduced in isolation it exits 1:
   `GATE FAILED — 2 blocking invariant(s)`, `UGA-INV-01` 25 violations, `UGA-INV-10` 25 violations.
   `verify.sh --full` cannot exit 0 while this stands.
2. **The largest evidence item is unreproduced.** The 17,121-test / 4,370-second coverage run and the
   4,379-second end-to-end `verify.sh --full` were **not executed** this phase (V-2). The 95.26 %
   figure is therefore **UNVERIFIED** and may not be certified: per the Certification Rule a statement
   requires command, output, evidence *and* reproduction, and reproduction is absent.

The Ω Closure Report reaches the same verdict on its own evidence — 8 of 10 items PASS, 1 BLOCKED,
1 FAILS, "**CLOSURE INCOMPLETE — PROVISIONAL**". This determination agrees with the primary artifact
and disagrees only with the summary table (F-8).

---

### D3 — Is Phase 2 complete?

```text
NO
```

**Phase 2 has not started.** This is a statement about programme sequence, established by source
inspection rather than inferred:

- `PHASE_OMEGA_A_ROADMAP.md:184` lists "Wiring any Phase 2 code into `verify.sh` or CI" under
  **Forbidden**: "No gate stage, no seal, no ratchet advancement."
- Ω∞-B prohibition **P-7**: "Do not wire any Phase 2 code into `verify.sh`, a gate stage, a seal or a
  ratchet — Forbidden by the directive sequence, and Ω∞-B has not changed it."
- `PHASE_OMEGA_B_PHASE_C_ENTRY_CRITERIA.md` §6: "**Phase Ω∞-B is not declared complete by this
  document. Phase Ω∞-C is not authorised by this document.**"
- Phase 2 code exists only as **untracked prototype**: 34 `.py` files in `engine/omega_governance/`,
  `engine/omega_infinite/`, `engine/tests/omega_infinite/`;
  `git ls-files 'engine/omega_infinite/*' 'engine/omega_governance/*'` returns **0**.
- Its designed core is largely unbuilt: 9 of the 11 modules named in
  `engine/omega_governance/__init__.py`'s own table are **absent**, including `invariants.py` and
  `registry.py`, and `state.py:58` asserts a proof that module would contain.

**P-7 compliance verified holding (tier 1):** `grep` across `verify.sh`, `Makefile`,
`.github/workflows/` and `pyproject.toml` finds **no reference** to either package. Only the
also-untracked `scripts/omega-infinite.sh` invokes it. **This is the correct state and must be
preserved.**

A Phase 2 Closure Report cannot exist, and neither can a Phase 2 closure arbitration (F-13).

---

### D4 — Is Program Closure complete?

```text
NO
```

| Closure requirement | Status | Evidence |
|---|---|---|
| All gates open | **NO** — UGA gate exit 1 | tier 1 |
| All registrations complete | **NO** — 25 anonymous objects | tier 1 |
| `verify.sh --full` exit 0 | **NO** — stage 9 fails | tier 1 |
| Git status clean | **NO** — 91 entries | tier 1 |
| All tests passing | **NO** — 1 failure (F-2), reproduced | tier 1 |
| All evidence reproduced | **NO** — V-1, V-2 unverified | tier 1 (absence) |
| All reports updated | **NO** — F-5, F-6, F-7 corrections outstanding | tier 1 |
| Phase 2 complete | **NO** — not started (D3) | tier 2 |

Eight of eight closure requirements fail. The primary closure artifact independently declares
"**CLOSURE INCOMPLETE — PROVISIONAL**".

---

### D5 — Are irreversible registration operations authorized?

```text
NOT AUTHORIZED
```

This is a stronger verdict than "conditionally authorized", and the reason is that **this phase
demonstrated the hazard experimentally rather than reasoning about it.**

**Ground 1 — every stated prerequisite fails.**

| Prerequisite (Registration Safety Rule) | Status |
|---|---|
| Git clean | **FAILS** — 91 entries |
| All prior phases complete | **FAILS** — Phase 2 not started (D3) |
| Verification complete | **FAILS** — D2 = NO |
| Validation complete | **FAILS** — V-1, V-2 unverified |
| Authorization recorded | **FAILS** — no owner authorization exists |

Per that rule: **`OPERATION REFUSED`.**

**Ground 2 — a measured eligibility defect would mint identities for unadjudicated artifacts.**

`register.sh` derives its eligibility universe from
`git ls-files --cached --others --exclude-standard` — tracked **union** untracked-not-ignored.
Measured against the frozen baseline:

| Measurement | Value |
|---|---|
| Total eligible paths | 6,872 |
| Of which **untracked** | 70 |
| Untracked `.md`/`.txt`/`.docx` matching the corpus matcher | **30** |

Those 30 are **not part of any accepted change**: 5 probe output `.txt` files under
`00-MASTER/UCOS-OMEGA-B-001/probes/`, and 25 root `PHASE1_*` / `PHASE_OMEGA_A_*` /
`PHASE_OMEGA_B_*` documents belonging to Ω∞-A and Ω∞-B. Running `register.sh` now would allocate
**permanent, append-only identities to 30 unadjudicated documents** in order to clear 25 legitimate
ones.

**Ground 3 — the repository has already sustained this exact damage, and it is documented.**

`.kiro/hooks/auto-register-artifact.json` is frozen with `"hooks": []` specifically because the hook
it preserves fired `register.sh` on any `.md`/`.txt`/`.docx` creation. Its own record of measured
consequences: *166 registered-but-untracked ledger sources (62 minted in a single hour), 7
unresolvable ledger sources, one artifact holding two identities, 29 identities minted for paths the
`.gitignore` declares non-artifacts, `page_cursor` advanced to 10732.* The file states the freeze holds
until "the registration eligibility policy is reconciled … and the append-only ledger damage has been
dispositioned." **Neither condition is met.**

**Ground 4 — decisive. The remediation command misreports what it does.**

This phase invoked `uga_engine.py run`, named in the UGA gate's **own remediation hint**. It printed
`UGA run — objects=6802 minted=0 retired=2` and `invariants 29/29 passing`. It had in fact mutated 11
tracked files and written **25 permanent Universal IDs into `00-BOOK/DATA/id-ledger.json`** —
`CONFIG 36→37`, `DATAOBJ 136→139`, `EXDOC 2994→2995`, `ENGINE 1330→1342`, `TESTOBJ 842→850`, summing to
exactly 25. **`minted=0` was false.** Reverted; fingerprint restored byte-exactly.

**An irreversible operation cannot be authorized while the command that performs it reports that it
performed nothing.** Ground 4 alone is sufficient, and it is tier-1 evidence produced under
controlled conditions rather than a concern.

#### Prerequisites that would convert this to CONDITIONALLY AUTHORIZED

All eight, in order, each verified by reproduced execution:

1. **F-9 fixed.** `uga_engine.py run` reports allocations truthfully and **refuses on a dirty tree**;
   the gate's remediation hint no longer names an unguarded mutating command.
2. **Eligibility reconciled.** `register.sh` is restricted to **tracked** artifacts, or the 70
   untracked paths are explicitly adjudicated. The `config.py REGISTRATION_SCOPE` /
   `ukb.py:697` contradiction named in the frozen hook is resolved.
3. **Prior ledger damage dispositioned** — the second condition the frozen hook sets for its own lift.
4. **F-4 cleared.** `git status --porcelain` is **empty**.
5. **V-3 resolved.** The two `AM` seal files are consistent between index and working tree.
6. **F-2 fixed** and the full suite green.
7. **V-1 and V-2 executed** and recorded, read-only properties established first.
8. **Owner authorization recorded** in writing, naming the exact 25 paths (per F-5, **not** the
   report's 24) and the exact ledger delta expected, so the post-condition is checkable.

Then, and only then: `register.sh` → `uga_engine.py gate` → `./verify.sh --full`, on a clean tree,
with the ledger diff reviewed before commit.

---

## 4. SUCCESS CRITERIA — PHASE 0

| Criterion | Status |
|---|---|
| **Governance** — arbitration reviewed | **PARTIAL.** The named arbitration does not exist (F-13). The 23 findings actually present were reviewed instead, and the substitution is recorded rather than silent |
| **Governance** — findings classified | **MET.** 23 findings: 18 accepted, 1 rejected, 4 requires-review |
| **Governance** — owners identified | **MET.** Every finding carries a named owner |
| **Governance** — critical path accepted | **MET.** `IMPLEMENTATION_SCOPE.md` §6 |
| **Technical** — implementation scope defined | **MET.** `IMPLEMENTATION_SCOPE.md` |
| **Technical** — closure blockers identified | **MET.** 9 blocking findings |
| **Technical** — registration authorization determined | **MET.** D5 = NOT AUTHORIZED, on four independent grounds |
| **Certification** — authoritative baseline established | **MET.** `HEAD` 77798202 + 91 entries, fingerprint `807104ba…`, verified restored at phase exit |
| **Certification** — future implementation sequence approved | **MET.** `IMPLEMENTATION_SCOPE.md` §6, conditions in §5 |

---

## 5. AUTHORIZATION DECISION

```text
IMPLEMENTATION AUTHORIZED WITH CONDITIONS
```

**Authorized** because the Ω programme's implementation is complete and independently verified at
tier 1 (D1), because every closure blocker is now named with a reproduced measurement and a named
owner, and because a non-destructive corrective path exists that does not touch any append-only
ledger.

**Conditioned** because five prerequisites must hold before *any* implementation work begins, and
because irreversible registration is separately refused:

1. **The ten-row all-PASS table is void as a baseline** (F-8). `IMPLEMENTATION_BASELINE_ACCEPTED.md`
   §0 is the baseline. Work proceeding from the table would register against a dirty tree with a
   failing gate.
2. **F-9 is fixed first.** No governance engine may be invoked for remediation until
   `uga_engine.py run` reports allocations truthfully and refuses on a dirty tree. This is the first
   task in the critical path because every later task is unsafe without it.
3. **No irreversible governance operation.** D5 = **NOT AUTHORIZED**. Forbidden until all eight
   prerequisites in §3/D5 are reproduced: `register.sh`, ledger allocation, identity minting,
   append-only writes, `uga_engine.py run` in its current form.
4. **Phase 2 stays out.** `engine/omega_governance/`, `engine/omega_infinite/`,
   `engine/tests/omega_infinite/`, `scripts/omega-infinite.sh` remain **untracked, unwired,
   unregistered** (F-14, P-7). Six Ω∞-B criteria (F-15 … F-20) are deferred, not inherited.
5. **Unverified stays unverified.** 95.26 % coverage, the per-stage `verify.sh` census, and the
   UCON/UCAF verdicts (V-1, V-2) must be cited as **UNVERIFIED** until reproduced. They may not
   appear in any certification.

**Not authorized under any condition in this phase:** irreversible registration, ledger mutation,
identity minting, closure certification, completion declaration, measurement rebaselining.
