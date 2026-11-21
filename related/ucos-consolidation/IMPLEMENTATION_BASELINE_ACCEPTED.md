# PHASE 0 — IMPLEMENTATION BASELINE ACCEPTED

**AUTHORITY = NONE (DERIVED TRUTH).** This document classifies and accepts. It issues no
certification, generates no seal, advances no ratchet, mints no identity, mutates no ledger, and
declares no closure. Every verdict below names the command that produced it.

**Phase 0 mandate:** determine what is accepted, what is rejected, what needs more evidence, what
repository state is authoritative, and whether implementation may proceed. **Not to fix anything.**

---

## 0. AUTHORITATIVE IMPLEMENTATION BASELINE

| Property | Value | Command |
|---|---|---|
| Branch | `integration/recovery-001` | `git rev-parse --abbrev-ref HEAD` |
| HEAD commit | `77798202d2df43285760b3277f230ebde4b52bbc` | `git log -1` |
| HEAD date | 2026-08-28 22:26:03 +0530 | `git log -1` |
| HEAD subject | "Point the certification report at the SHA it actually describes" | `git log -1` |
| Working tree | **NOT CLEAN — 91 entries** | `git status --porcelain \| wc -l` |
| Working-tree fingerprint | `807104baf749fd2614afed1bf080c249` | `git status --porcelain \| md5` |
| Tracked Python artifacts | 2,197 | `git ls-files '*.py' \| wc -l` |

**THE AUTHORITATIVE BASELINE IS `HEAD` (77798202) PLUS THE 91 UNCOMMITTED ENTRIES, WITH THE
FINGERPRINT ABOVE.** The fingerprint was captured at Phase 0 entry, verified stable across every
read-only measurement, broken once by an operation this phase performed in error (F-10), and
**restored byte-exactly** — `git status --porcelain | md5` returns `807104baf749fd2614afed1bf080c249`
at Phase 0 exit. Any implementation work must begin from this fingerprint.

**Composition of the 91 — measured, `git status --porcelain | awk '{print substr($0,1,2)}' | sort | uniq -c`:**

| Code | Count | Meaning |
|---|---|---|
| `A ` | 23 | staged additions — the Ω change |
| `M ` | 17 | staged modifications — the Ω change |
| `AM` | 2 | staged **then modified** — `omega-ratchet.json`, `omega-surface.json` (V-3) |
| ` M` | 19 | modified, unstaged — regenerated UAKOS-CLOSURE-008 / UCAF registers |
| `??` | 30 | untracked — 25 root `PHASE1_*`/`PHASE_OMEGA_A_*`/`PHASE_OMEGA_B_*` documents, 4 directories (`00-MASTER/UCOS-OMEGA-B-001/`, `engine/omega_governance/`, `engine/omega_infinite/`, `engine/tests/omega_infinite/`), 1 script (`scripts/omega-infinite.sh`) — **all Ω∞-A/Ω∞-B, none part of the Ω change** |
| | **91** | |

Note this corrects Ω Closure Report §6.3, which states "40 staged … 22 modified". Measured: **42
entries carry staged content** (23 `A ` + 17 `M ` + 2 `AM`) and **19** are modified-unstaged. Recorded
as part of F-C2's accounting class rather than as a separate finding.

---

## 1. MISSING NAMED INPUTS — RECORDED BEFORE ANY FINDING IS CLASSIFIED

The Phase 0 directive names inputs that **do not exist in this repository.** Their absence is a
finding, not a formatting problem, and it governs the scope of everything below.

| Named input | Status | Command |
|---|---|---|
| **PHASE 2 CLOSURE ARBITRATION DETERMINATION** | **DOES NOT EXIST** | `find . -iname '*ARBITRATION*'` returns 3 files, all `UCOS-OMEGA-INFINITY-*IDENTITY-ARBITRATION*`, none a Phase 2 closure arbitration; `grep -ril "closure arbitration"` returns **nothing** |
| **Phase 2 Closure Report** | **DOES NOT EXIST** | no such file; and Phase 2 has not begun — §1.1 |
| Ω Closure Report | **EXISTS** | `00-MASTER/UCOS-OMEGA-001/OMEGA-CLOSURE-REPORT.md` |
| Supporting verification artifacts | **EXIST** | `00-MASTER/UCOS-OMEGA-001/omega-{surface,ratchet}.json`, `00-MASTER/UCOS-OMEGA-B-001/probes/` |
| Supporting gate outputs | **REPRODUCED** | §2 |

### 1.1 What "Phase 2" actually denotes — source-inspected, not assumed

`PHASE_OMEGA_A_ROADMAP.md:184` and `PHASE_OMEGA_B_PHASE_C_ENTRY_CRITERIA.md:165` (P-7) both use
"Phase 2" to mean **the Ω∞ implementation phase that has not started**:

> P-7 · **Do not wire any Phase 2 code into `verify.sh`, a gate stage, a seal or a ratchet** —
> Forbidden by the directive sequence.

Phase 2 is therefore **prospective**. There is no Phase 2 Closure Report because there is no Phase 2
closure. **A Phase 2 closure arbitration cannot be accepted, rejected or reviewed, because no Phase 2
closure exists to arbitrate.**

**Consequence for this phase.** Phase 0 cannot classify "every arbitration finding" against a
non-existent arbitration. It instead classifies the **complete finding set actually present in the
closure evidence**, derived from four sources and labelled by origin:

| Prefix | Source | Count |
|---|---|---|
| `F-Ω` | Ω Closure Report — evidence table + §11 outstanding | 5 |
| `F-C` | Corrections this phase established against the closure evidence | 4 |
| `F-N` | New findings this phase measured | 6 |
| `F-B` | Ω∞-B hard entry criteria and active defects (Phase 2 scope) | 8 |

**23 findings total.** Nothing is inherited on assertion.

---

## 2. EVIDENCE REPRODUCED THIS PHASE (TIER 1)

Every row was executed against the baseline fingerprint. Rows marked ✅ match the Ω Closure Report
exactly; ✳ corrects it; ❌ refutes a claim made elsewhere.

| # | Claim under test | Reproduced result | Verdict |
|---|---|---|---|
| 1 | Ruff clean, 0 violations | `ucos_ruff_gate` → `All checks passed! 1584 files already formatted`, exit 0 | ✅ |
| 2 | Ω test suite green | `198 passed, 1 skipped in 126.58s` | ✅ |
| 3 | UCI suite 62 pass / 1 pre-existing fail | `1 failed, 62 passed` — the failure is exactly `test_statement_attribution_partitions_rather_than_nests` | ✅ |
| 4 | That failure depends on gitignored `coverage.xml` | present → **FAIL** (`104 != 112`); moved aside → **`1 passed in 4.43s`**; restored 5,139,413 bytes | ✅ |
| 5 | Ω gate PASS, all five criteria | `PASS — all five Ω criteria hold`, exit 0 | ✅ |
| 6 | Ω gate is read-only | `git status --porcelain \| md5` identical before/after | ✅ |
| 7 | Two `--json` renders byte-identical | both `1281418` bytes, `cmp` identical, SHA-256 `601e4772d5fc9d48fe7ccff00fe3e31b624fab7a7dc0f0344245547f4e4f844a` — **matches the report to the character** | ✅ |
| 8 | Ω measurements (2,197 / 11 roots / 7 test roots / 80 packages / 100 % authority / 2,144 reachable / 22 dynamic / 90.3034 % / 9 ratchets) | every value identical | ✅ |
| 9 | UGA reports **24** violations | UGA reports **25** — `UGA-INV-01` 25, `UGA-INV-10` 25 | ✳ **F-C1** |
| 10 | `verify.sh --full` has 19 stages, 13 pass | **20** stages; the report's own named list contains **14** passes (14+6=20) | ✳ **F-C2** |
| 11 | `engine/omega_governance/` is absent and unrecoverable | **PRESENT**; probe `b01` executes, exit 0 | ✳ **F-C3** |
| 12 | `verify.sh --full` PASS | **FAILS** — mandatory stage 9 (UGA) fails independently | ❌ **F-C4** |
| 13 | Working tree clean | **91 entries** | ❌ **F-C4** |
| 14 | UGA gate read-only | md5 identical before/after | ✅ |

**Not reproduced in this phase, and therefore NOT certified:** the full coverage run
(17,121 tests / 4,370 s / 95.26 %) and the end-to-end `verify.sh --full` (4,379 s). Both are recorded
**UNVERIFIED** — see §5, R-1.

---

## 3. ACCEPTED FINDINGS

### F-Ω1 — 25 artifacts have no Universal ID

```text
Finding ID            F-Ω1  (Ω Closure Report §7, corrected by F-C1)
Classification        BLOCKING — closure blocker; irreversible act required to clear
Reason Accepted       Reproduced. `uga_engine.py gate` exits 1 with
                      "GATE FAILED — 2 blocking invariant(s)":
                      UGA-INV-01 EVERY_OBJECT_HAS_UNIVERSAL_ID  violations=25, measured=6802
                      UGA-INV-10 EVERY_MUTATION_HAS_AUDIT_EVENT violations=25, measured=5205
Evidence Tier         1 — Reproduced execution
Implementation Impact Clearing it requires `register.sh`, an append-only ledger allocation.
                      NOT AUTHORIZED in Phase 0 and NOT AUTHORIZED now (D5, F-N1).
                      Blocks verify.sh stage 9, therefore blocks verify.sh --full exit 0,
                      therefore blocks programme closure.
```

### F-Ω2 — a test verdict depends on a gitignored artifact

```text
Finding ID            F-Ω2  (Ω Closure Report §6.1)
Classification        PRE-EXISTING DEFECT — correctness; not attributable to the Ω change
Reason Accepted       Isolation reproduced exactly, both directions, this phase:
                      coverage.xml present -> FAILED (objects sum 104, file has 112)
                      coverage.xml absent  -> 1 passed in 4.43s
                      The report's attribution of cause is therefore sound, not argued.
Evidence Tier         1 — Reproduced execution (isolation experiment)
Implementation Impact A gate verdict is a function of an untracked, gitignored file. Any CI
                      runner without coverage.xml passes; any runner with it fails. Owner:
                      UCI-000001. In scope for implementation (IMPLEMENTATION_SCOPE.md).
```

### F-Ω4 — `verify.sh --full` does not exit 0

```text
Finding ID            F-Ω4
Classification        BLOCKING — closure blocker
Reason Accepted       Not inherited from the report; established independently. Stage 9
                      ("universal object governance (UGA-INV-01..10)") is a mandatory
                      run_stage in verify.sh and exits 1 when reproduced in isolation.
                      One failing mandatory stage is dispositive of the whole script:
                      verify.sh --full CANNOT exit 0 while F-Ω1 stands.
Evidence Tier         1 — Reproduced execution (stage), 2 — Source inspection (verify.sh:798
                      and the 20 run_stage sites establishing stage 9 is unconditional)
Implementation Impact Gates closure. Cleared only by clearing F-Ω1.
```

### F-Ω5 — working tree is not clean

```text
Finding ID            F-Ω5
Classification        BLOCKING — governance invariant violated
Reason Accepted       `git status --porcelain | wc -l` = 91 at Phase 0 entry and exit.
                      Measured composition: 23 `A ` + 17 `M ` + 2 `AM` staged, 19 ` M`
                      modified-unstaged, 30 `??` untracked. (This corrects Ω Closure Report
                      §6.3, which states "40 staged … 22 modified".)
Evidence Tier         1 — Reproduced execution
Implementation Impact The GIT CLEAN INVARIANT fails, so no irreversible governance operation
                      is authorized (D5). Also material to F-N1: 30 untracked entries sit
                      inside register.sh's eligibility universe.
```

### F-C1 — the violation count is 25, and the 25th is the closure report itself

```text
Finding ID            F-C1
Classification        CORRECTION to Ω Closure Report §7 and evidence row 10
Reason Accepted       Report states 24 violations and enumerates 24 paths. Reproduced
                      measurement is 25. The extra path is
                          00-MASTER/UCOS-OMEGA-001/OMEGA-CLOSURE-REPORT.md
                      i.e. the closure report is itself an unregistered artifact, and it
                      under-reports its own blocker by exactly itself. The report could not
                      have counted itself: it enumerated the blocker before it existed.
Evidence Tier         1 — Reproduced execution overrides 4 — Report statement
Implementation Impact The remediation set is 25 paths, not 24. Any registration scoped to
                      the report's 24 leaves one artifact anonymous and stage 9 still red.
                      This is a silent-off-by-one in the closure critical path.
```

### F-C2 — stage arithmetic in the closure report does not close

```text
Finding ID            F-C2
Classification        CORRECTION to Ω Closure Report §5
Reason Accepted       Report: "19 stages", "Passed (13)", "Failed (6)".
                      Measured: 20 stages in --full mode — 19 at column 0 plus the
                      conditional `run_stage "registration observation (register.sh
                      --observe, read-only)"` at verify.sh:798, which is --full only.
                      The report's own named pass list contains 14 entries, not 13, and
                      14 + 6 = 20 = the measured stage count. The prose count is wrong;
                      the named list is right.
Evidence Tier         1 — Reproduced execution / 2 — Source inspection (verify.sh:9, :798)
Implementation Impact Low severity, high governance significance: a closure report whose
                      stage census disagrees with the script it certifies. Correct the
                      count, not the list.
```

### F-C3 — the Ω∞-B provenance warning is stale

```text
Finding ID            F-C3
Classification        CORRECTION to every PHASE_OMEGA_B_*.md preamble
Reason Accepted       All Ω∞-B deliverables open with a boxed warning stating that
                      engine/omega_governance/ "is NO LONGER PRESENT", that reproduction
                      "no longer executes" with ModuleNotFoundError, and that the tree "is
                      not recoverable from version control".
                      Reproduced: `ls engine/omega_governance/` returns __init__.py,
                      authority.py, state.py, reference/, temporal/ — the exact composition
                      §H9 recorded. `probes/b01_proof_tractability.py` runs to completion,
                      exit 0, and prints its findings.
                      The tree is present and the evidence base IS reproducible.
Evidence Tier         1 — Reproduced execution overrides 4 — Report statement
Implementation Impact Ω∞-B's classifications regain independent re-verifiability, which the
                      warning had surrendered. The warning must be withdrawn or rewritten;
                      leaving it standing understates the evidence base. Note this cuts
                      AGAINST the report's own interest, which is why it is credible.
```

### F-C4 — the ten-row all-PASS status table is refuted

```text
Finding ID            F-C4
Classification        REJECTED AS BASELINE — false status claim (see also §4, R-2)
Reason Accepted       A ten-row table asserting PASS for Ω Implementation, Ω Verification,
                      UCON, UCAF, UGA, UCI, Contract Alignment, verify.sh --full, Tree Clean
                      and Registration Complete was presented as the closure position.
                      Five rows are refuted by reproduced execution:
                        verify.sh --full     claimed PASS -> FAILS (F-Ω4)
                        Tree Clean           claimed PASS -> 91 entries (F-Ω5)
                        Registration Complete claimed PASS -> 25 anonymous objects (F-Ω1)
                        UGA                  claimed PASS -> exit 1, 2 blocking invariants
                        Ω Verification       claimed PASS -> the Ω report itself says
                                             "CLOSURE INCOMPLETE — PROVISIONAL"
                      The table also contradicts the primary closure artifact it summarises.
Evidence Tier         1 — Reproduced execution overrides 4 — Report statement
Implementation Impact This table MUST NOT be used as the implementation baseline. §0 is the
                      baseline. Accepting the table would authorize registration against a
                      dirty tree with a failing gate — the precise sequence D5 refuses.
```

### F-N1 — `uga_engine.py run` performs irreversible ledger allocation while reporting `minted=0`

```text
Finding ID            F-N1  (new; measured by this phase, at this phase's own cost)
Classification        BLOCKING — irreversible-operation safety defect
Reason Accepted       Demonstrated, not argued. This phase invoked
                          python 00-MASTER/UCOS-UGA-001/uga_engine.py run
                      on the strength of the gate's own remediation hint ("ANONYMOUS
                      OBJECTS: 25 — run `uga_engine.py run`"). Its summary line printed:
                          UGA run — objects=6802 minted=0 retired=2
                          invariants 29/29 passing
                      "minted=0" is FALSE. The command mutated 11 tracked files and
                      allocated 25 PERMANENT Universal IDs into the append-only ledger
                      00-BOOK/DATA/id-ledger.json. Measured from the diff, the category
                      counters moved:
                          CONFIG  36 -> 37   (+1)
                          DATAOBJ 136 -> 139 (+3)
                          EXDOC   2994 -> 2995 (+1)
                          ENGINE  1330 -> 1342 (+12)
                          TESTOBJ 842 -> 850  (+8)
                      = +25, exactly the 25 anonymous objects. New ledger entries include
                      UCOS-CONFIG-000037 (.github/workflows/omega-gate.yml) and
                      UCOS-DATAOBJ-000137 (uci-ratchet.json).
                      Working-tree fingerprint moved 807104ba -> 3090b336 (91 -> 102).
                      FULLY REVERTED: `git checkout --` on the 11 paths restored
                      fingerprint 807104baf749fd2614afed1bf080c249 byte-exactly.
Evidence Tier         1 — Reproduced execution (performed, measured, reverted)
Implementation Impact SEVERE and directly on the closure critical path. The gate that reports
                      the blocker recommends, in its own output, a command that silently
                      performs the irreversible act while reporting that it minted nothing.
                      Anyone following the gate's advice during a freeze breaks the freeze
                      and cannot tell from the output. Corroborated independently: the
                      frozen hook .kiro/hooks/auto-register-artifact.json documents the same
                      defect class already causing measured damage — "166 registered-but-
                      untracked ledger sources (62 minted in a single hour)", "one artifact
                      holding two identities", "29 identities minted for paths the
                      .gitignore declares NON-ARTIFACTS".
                      REQUIRED: `run` must refuse on a dirty tree, must report allocations
                      truthfully, and the gate's remediation hint must not name it unguarded.
```

### F-N2 — 613 tracked Python files across 9 roots are outside the lint gate

```text
Finding ID            F-N2  (new)
Classification        GOVERNANCE SCOPE GAP — CRITICAL
Reason Accepted       ucos_ruff_gate lints tracked *.py under engine/ and platform/ only:
                          git ls-files '*.py'                     = 2197
                          gate scope (engine+platform)            = 1584   <- gate PASSES
                          outside gate scope                      =  613
                      Ruff run over exactly those 613 tracked files reports 9,894 violations:
                          7977 S101, 1702 E501, 55 E702, 31 F401, 22 I001, 21 F541,
                          17 S603, 13 UP015, 11 UP038, 8 F841, 6 UP017, ... 1 F821
                      Affected roots: service 132, data 122, infrastructure 112,
                      application 112, intelligence 71, 00-MASTER 49, 00-BOOK 13,
                      scripts 1, 00-CMG 1.
Evidence Tier         1 — Reproduced execution
Implementation Impact Ω governs 2,197 artifacts; lint governs 1,584. 28 % of the tracked
                      Python surface has no lint gate. The ruff gate PASSES legitimately at
                      its declared scope — this is not a false pass, it is an undeclared
                      boundary. NOTE: this phase initially measured 9,988 violations
                      repo-wide and nearly recorded a conflict against the report's "ruff
                      clean" claim; source inspection of ucos-env.sh:321 showed the scopes
                      differ, so no conflict was recorded. The report's claim is correct.
```

### F-N3 — the lint gate enumerates its scope, contradicting the Ω thesis

```text
Finding ID            F-N3  (new)
Classification        ARCHITECTURAL INCONSISTENCY — MEDIUM
Reason Accepted       Ω-1's entire thesis, and the Ω Closure Report's headline achievement,
                      is that scope must be DERIVED and never enumerated: 78 `--cov=` flags,
                      7 testpaths and 78 source paths were deleted for exactly this reason,
                      and the gate prints "no list was consulted".
                      ucos_ruff_gate hardcodes the two roots `engine/ platform/` as literals
                      (scripts/ucos-env.sh, UCOS-GOV-LINT-BOUNDARY block). It is the same
                      enumeration defect the Ω programme was convened to remove, in the
                      stage that runs FIRST in verify.sh.
Evidence Tier         2 — Source inspection
Implementation Impact A new tracked root gains Ω governance automatically and lint governance
                      never. The Ω derivation already computes the 11 roots the gate would
                      need. Cost of routing the gate through it is small; the inconsistency
                      is the finding.
```

### F-N4 — `NoReturn` is never imported in `rfp_engine.py`

```text
Finding ID            F-N4  (new)
Classification        COSMETIC / STATIC-ONLY — explicitly NOT a runtime defect
Reason Accepted       00-MASTER/UCOS-RFP-001/rfp_engine.py:61
                          def fail_closed(reason: str) -> "NoReturn":  # type: ignore
                      `NoReturn` appears nowhere else in the file and is not imported
                      (grep: single occurrence, line 61).
                      SEVERITY VERIFIED DOWNWARD, NOT ASSUMED: the annotation is a STRING
                      literal, so Python never evaluates it. `ast.parse` succeeds. There is
                      no latent NameError and the fail-closed path executes correctly. It is
                      a static/typing defect only.
Evidence Tier         1 — Reproduced execution (parse + grep)
Implementation Impact Negligible functionally. Recorded because it sits in a FAIL-CLOSED
                      abort path inside a governance engine, and because it is one of the
                      613 files F-N2 shows nothing lints. It is the cheapest possible
                      demonstration that F-N2 is a real gap and not a theoretical one.
```

### F-N5 — the named Phase 0 inputs do not exist

```text
Finding ID            F-N5  (new)
Classification        BLOCKING (procedural) — governance input missing
Reason Accepted       "PHASE 2 CLOSURE ARBITRATION DETERMINATION": absent.
                      `grep -ril "closure arbitration"` -> no matches repository-wide.
                      "Phase 2 Closure Report": absent, and cannot exist — Phase 2 is the
                      UNSTARTED implementation phase (PHASE_OMEGA_A_ROADMAP.md:184,
                      Ω∞-B P-7). See §1.1.
Evidence Tier         1 — Reproduced execution (exhaustive absence search)
Implementation Impact Phase 0 could not perform the task as literally specified: there is no
                      arbitration to accept or reject. It instead classified the 23 findings
                      actually present in the closure evidence. If a real arbitration
                      determination exists outside this repository it must be supplied, and
                      this baseline re-run against it.
```

### F-N6 — `engine/omega_governance/` and `engine/omega_infinite/` are untracked and ungoverned

```text
Finding ID            F-N6  (new)
Classification        CRITICAL — governance boundary
Reason Accepted       34 Python files across engine/omega_governance/,
                      engine/omega_infinite/ and engine/tests/omega_infinite/.
                          git ls-files 'engine/omega_infinite/*' 'engine/omega_governance/*'
                          = 0
                      They are therefore outside Ω's population by construction (Ω's
                      boundary is `git ls-files`, chosen so a verdict cannot depend on a
                      working copy) and outside every coverage denominator, ratchet and
                      disposition. They carry no Universal ID and no authority.
                      P-7 COMPLIANCE HOLDS: grep across verify.sh, Makefile,
                      .github/workflows/ and pyproject.toml finds NO reference. Only the
                      (also untracked) scripts/omega-infinite.sh invokes the package. No
                      gate stage, seal or ratchet touches Phase 2 code.
Evidence Tier         1 — Reproduced execution / 2 — Source inspection
Implementation Impact This is the correct state per P-7 and must be PRESERVED, not fixed.
                      The risk is the opposite of the usual one: these 34 files plus 30
                      untracked corpus files sit inside register.sh's eligibility universe
                      (F-N1, D5), so an unguarded registration would mint permanent
                      identities for unadjudicated prototype code. Do not track, do not
                      wire, do not register.
```

### F-B1 … F-B6 — Ω∞-B hard entry criteria E-1 … E-6

```text
Finding ID            F-B1 (E-1) no claim describes a module/proof/mechanism that doesn't exist
                      F-B2 (E-2) register shape decided before registry.py is written
                      F-B3 (E-3) Rule 9 distinguishes code migration from record backfill
                      F-B4 (E-4) every active correctness defect found in Ω∞-B is closed
                      F-B5 (E-5) guards + certification inputs as one item; blocked_by retained
                      F-B6 (E-6) no vocabulary-identity work described as closing A-14
Classification        ACCEPTED AS FINDINGS — DEFERRED, Phase 2 scope
Reason Accepted       F-B1's factual core is independently reproduced this phase: probe b01
                      executes and prints that state.py:58 asserts
                      `invariants.unknown_never_certifies` enumerates all 900 vectors and
                      that __init__.py:34 lists invariants.py among "seven executable
                      proofs" — while the module is ABSENT. 9 of the 11 modules the
                      package's own table names do not exist. A present-tense claim that
                      nothing checks is confirmed present in the tree.
Evidence Tier         1 — Reproduced execution (F-B1); 4 — Report statement (F-B2..F-B6,
                      resting on probe outputs preserved in probes/, now re-executable
                      per F-C3)
Implementation Impact ALL SIX ARE OUT OF SCOPE FOR THE CURRENT IMPLEMENTATION and are
                      recorded so they are not silently inherited. They govern entry to
                      Ω∞-C, not the Ω closure blockers. Ω∞-B declares neither itself
                      complete nor Ω∞-C authorized, and this phase does not overturn that.
                      They apply to untracked code (F-N6) that must not be wired in (P-7).
```

### F-B7 — four active correctness defects in the Ω∞-B subject tree

```text
Finding ID            F-B7  (Ω∞-B E-4)
Classification        ACCEPTED AS FINDING — DEFERRED (conditional on adoption)
Reason Accepted       Reported as producing wrong records now: (a) a complete transformation
                      route returned from insufficient inputs, so apply() converts from
                      SPACE alone and reports success; (b) a bare str position exploded to a
                      character tuple, accepted, and FINGERPRINTED into a governance record;
                      (c) assert_provider advances the clock it verifies, (0,)->(3,);
                      (d) compare() emits INCOMPARABLE citing a relation the emitting
                      registry cannot resolve.
Evidence Tier         4 — Report statement, resting on probe outputs in probes/ that are
                      re-executable again per F-C3. NOT independently re-measured by this
                      phase.
Implementation Impact Confined to UNTRACKED code (F-N6) that no gate reaches. Zero effect on
                      the tracked baseline, on verify.sh, or on the Ω closure blockers.
                      Becomes in-scope only if and when omega_governance is adopted into the
                      tracked tree — an owner decision not taken here.
```

---

## 4. REJECTED FINDINGS

### R-2 — the ten-row all-PASS status table (rejected as baseline)

```text
Finding ID            R-2  (the claim rejected; the underlying facts are F-C4)
Classification        FALSE STATUS CLAIM
Reason Rejected       Five of its ten rows are refuted by tier-1 reproduced execution
                      (F-C4). It also contradicts the primary artifact it purports to
                      summarise: OMEGA-CLOSURE-REPORT.md states "Verdict: CLOSURE INCOMPLETE
                      — 8 of 10 required evidence items PASS, 1 BLOCKED on owner
                      authorization, 1 FAILS" and "CLOSURE INCOMPLETE — PROVISIONAL".
                      A summary cannot upgrade its source. Report statement is tier 4; it
                      cannot override tier 1.
Required Additional   NONE THAT WOULD RESCUE IT. The table is not short of evidence, it is
Evidence              contradicted by it. To become true, the repository must change:
                      F-Ω1 cleared (25 registrations), F-Ω4 cleared (verify.sh exit 0),
                      F-Ω5 cleared (tree clean). Re-assert only after all three are
                      reproduced green, and never as a substitute for §0.
```

### R-3 — "the Ω∞-B evidence base is not reproducible" (rejected)

```text
Finding ID            R-3
Classification        SUPERSEDED CLAIM
Reason Rejected       Refuted by F-C3 at tier 1: the subject tree is present and probe b01
                      runs to completion, exit 0. The claim was true when written and is
                      false now.
Required Additional   None. The claim is withdrawn on reproduced execution. The Ω∞-B
Evidence              preambles carrying it require correction (F-C3), which is a document
                      change deferred out of Phase 0 by the governance freeze.
```

---

## 5. REQUIRES REVIEW

### V-1 — UCON and UCAF populate from the filesystem, not from git

```text
Finding ID            V-1  (Ω Closure Report §6.2)
Classification        PRE-EXISTING DEFECT — governance boundary
Conflicting Evidence  REPORT (tier 4, unreproduced here): UCON and UCAF walk the filesystem,
                      so untracked content enters their populations. Restricted to tracked
                      files, UCON is at or below baseline on every closure form
                      (ENUM_CLASS 246/246, FIXED_DISPATCH_TABLE 440/446,
                      FIXED_VOCABULARY_TUPLE 462/477, FROZEN_MEMBERSHIP_SET 239/239,
                      POPULATION_ASSERTION 35/35) and both gates are OPEN; all 26 excess
                      closures and 4 of 5 unclassified authority tokens are untracked.
                      THIS PHASE: not re-measured. The UCON and UCAF gates were NOT executed.
                      CORROBORATING (tier 1): F-N6 confirms 34 untracked Python files exist
                      in exactly the trees the report blames, which is consistent with the
                      explanation but does not verify the counts.
                      COUNTER-PRESSURE (tier 1): the ten-row table claimed UCON PASS and
                      UCAF PASS; the report says both fail on the filesystem population and
                      pass only on the tracked one. Those cannot both be unconditional.
Resolution Path       Execute both gates against the frozen baseline and record raw output:
                        verify.sh stage 16 (UCON-000001) and the UCAF gate in isolation.
                      Then re-run with untracked trees stashed, and compare. Two runs settle
                      it. READ-ONLY ONLY — verify each gate's read-only property by
                      md5-comparing `git status --porcelain` across it FIRST, as was done
                      for the Ω and UGA gates, because F-N1 proves a governance engine in
                      this repository can mutate a ledger while reporting that it did not.
                      Until then V-1 is UNVERIFIED and neither PASS nor FAIL may be claimed.
```

### V-2 — the full coverage run and end-to-end `verify.sh --full`

```text
Finding ID            V-2
Classification        UNVERIFIED MEASUREMENT — the largest evidence item in the closure set
Conflicting Evidence  REPORT (tier 4): 17,121 passed / 4 skipped in 4,370 s; TOTAL 126,541
                      statements, 95.26 %; "Required test coverage of 90% reached";
                      verify.sh --full 4,379 s, 13 of 19 stages pass.
                      THIS PHASE: NOT REPRODUCED. Neither the ~73-minute coverage run nor
                      the ~73-minute verify.sh --full was executed. Cost was not the only
                      reason: verify.sh contains a "prerequisite generation" stage that
                      writes artifacts, and F-N1 establishes that a governance engine here
                      can mutate an append-only ledger while reporting minted=0. Running it
                      under a governance freeze was refused as unsafe.
                      PARTIALLY SETTLED (tier 1): the FAIL verdict on verify.sh --full does
                      NOT depend on this. Stage 9 fails in isolation, and one failing
                      mandatory stage is dispositive. F-Ω4 is ACCEPTED on that basis alone.
                      What remains unverified is the 95.26 % figure and the per-stage census.
Resolution Path       Run `./verify.sh --full` and the full coverage run ONCE, on a clean
                      tree, AFTER F-Ω5 is cleared and with the read-only property of every
                      stage established first. Capture stdout to an evidence artifact.
                      Until then 95.26 % must be cited as UNVERIFIED and must not appear in
                      any certification. Per the CERTIFICATION RULE, a statement may be
                      certified only if command, output, evidence and reproduction all
                      exist; for this item output and reproduction do not.
```

### V-3 — is the Ω change's `AM` state internally consistent?

```text
Finding ID            V-3
Classification        MINOR — baseline hygiene
Conflicting Evidence  Two paths are staged-and-then-modified:
                        AM 00-MASTER/UCOS-OMEGA-001/omega-ratchet.json
                        AM 00-MASTER/UCOS-OMEGA-001/omega-surface.json
                      The staged content and the working-tree content therefore differ, so
                      the committed Ω seal would not equal the seal the gate currently
                      reproduces. The gate passes against the WORKING TREE (verified this
                      phase, exit 0, digest 601e4772…). Whether it passes against the INDEX
                      was not tested.
Resolution Path       `git diff --cached` vs `git diff` on both paths; re-run the gate
                      against index content. Resolve before any commit, since committing the
                      index as-is would seal a state no gate run has validated.
```

---

## 6. WHAT THIS PHASE CHANGED

**Intended:** nothing. Phase 0 is inspection, analysis and classification only.

**Actual:** one unintended mutation, disclosed in full as F-N1 — `uga_engine.py run` allocated 25
permanent Universal IDs across 11 tracked files, including the append-only ledger. **Reverted with
`git checkout --` on exactly those 11 paths. The working-tree fingerprint is restored byte-exactly to
`807104baf749fd2614afed1bf080c249`, verified by `git status --porcelain | md5`.** No other tracked
file was touched. `coverage.xml` was moved aside for 4.43 s during the F-Ω2 isolation test and
restored at its original 5,139,413 bytes.

**Added:** three untracked Phase 0 deliverables — this file, `ARBITRATION_ACCEPTANCE_RECORD.md`,
`IMPLEMENTATION_SCOPE.md`. They take the untracked count 30 → 33 and the total 91 → 94, verified by
measurement. Creating them is the Phase 0 mandate; committing them is a separate act not taken here.
**The 61 tracked entries are unchanged.**

**Confirmed safe:** `.kiro/hooks/auto-register-artifact.json` has `"hooks": []`, so creating `.md`
files cannot fire `register.sh`. Checked before writing anything.

---

## 7. AUTHORIZATION

```text
IMPLEMENTATION AUTHORIZED WITH CONDITIONS
```

Justification, prerequisites and the ordered critical path are in `IMPLEMENTATION_SCOPE.md` §4–§6.
The determinations D1–D5 are in `ARBITRATION_ACCEPTANCE_RECORD.md` §3.

**Irreversible registration operations are NOT AUTHORIZED.** See D5.
