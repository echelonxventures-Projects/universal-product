# IMPLEMENT-001 · DELIVERABLE 04 — GATE-PREREQUISITE REGISTER (`B-1`, `B-2`)

| Field | Value |
|---|---|
| MISSION | `IMPLEMENT-001` — First Production Implementation Mission |
| AUTHORITY | `NONE — DERIVED TRUTH` |
| AUTHORED BY | `IMPLEMENT-001E` — IMPLEMENT-001 Closeout (Phase 2) |
| CITED BY | Deliverable 00 — **every one of the 9 backlog items**: *"Blocking conditions: `B-1`, `B-2` (**see Deliverable 04**)"* |
| ALSO CITED BY | Deliverable 01 §2 (`⇒ GATE-PREREQ` box) · §4 (critical path origin) · §5 (topological order 0) · §6 |
| REPOSITORY ANCHOR | the containing commit — owned by version control, never restated here (`UCOS-RFP-001` RFP-2) |
| MEASURED AT | `8aede74` · working tree clean (0 entries) · `verify.sh` GREEN 5/5 · coverage 94.28% |
| VERDICT | **`B-1` DISCHARGED · `B-2` OPEN** → the gate-prerequisite conjunct is **NOT MET** |
| DISCLOSURE | `CERTIFIED-PROVISIONAL`; Tier T1 VACANT (`VAC-01` · `CMG-OQ-02` · `UCCEP-F-004`) |

> This is the deliverable whose absence made D00 **readable but not executable**: nine items cited
> blocking conditions against a definition that did not exist (`IMPLEMENT-001A` D00 §3.3). It
> defines them, states their discharge criteria, and measures their current state. It discharges
> nothing itself.

---

## 1. WHAT A GATE-PREREQUISITE IS

D01 §1 declares three edge kinds. `B-1` and `B-2` are the only members of the second:

| Edge | Meaning | Consequence if unsatisfied |
|---|---|---|
| `⇒ GATE-PREREQ` | Repository-state condition that must hold before *any* item executes | **blocks the whole wave set** |

Two properties follow, and both matter for the verdict:

1. **Uniform.** A gate-prerequisite is not a property of an item. It is a property of the
   repository. It cannot be discharged "for `EB-07`" and left open for `EB-06`.
2. **Conjunctive.** D00 attaches `B-1` **and** `B-2` to all nine items. One open prerequisite
   blocks all nine, whatever their individual readiness. This is why D02 §4 makes the
   gate-prerequisite conjunct part of the wave-admission test.

**There are exactly two.** D00 attaches no third condition to any item; the only item-specific
blocker in the backlog is `EB-09`'s `CEP-009` governance prerequisite, which D01 §1 classifies as
`⇒ GOVERNANCE-PREREQ` — a different edge kind, blocking only its own item. **Cardinality: 2,
closed.**

---

## 2. `B-1` — AUTHORITY WITNESS

| Field | Determination |
|---|---|
| **Identifier** | `B-1` (`T-M`, `NF-3` — mission-local, allocates nothing, never presented to `REG-AUTO-001`) |
| **Name** | Authority Witness |
| **Condition** | Every instrument on which `IMPLEMENT-001`'s determinations rest must exist **in Repository Truth**, not merely on one disk |
| **Why it is a gate** | `IMPLEMENT-001A` D00 §2 stated it plainly: *"All four authorities are themselves **uncommitted**. Every determination in this mission — and in `IMPLEMENT-001` — rests on artifacts that the repository does not yet contain."* An item executed under an uncommitted authorization is unauditable: the authorization could change or vanish without trace. |
| **Instruments in scope** | `UCOS-BASELINE-001` (`BASELINE-001/`) · `EVOLUTION-001` (classification) · `RELEASE-001` (lifecycle) · `OAA-001` (`IMR-001/01-…` — the execution authorization itself) · `CAEM-001` (assimilation + the anti-duplication instrument) |
| **STATUS** | ✅ **DISCHARGED** |

### 2.1 Discharge criterion

| Clause | Criterion | Met? | Evidence |
|---|---|---|---|
| **B-1.a** | Every named instrument is tracked by version control | ✅ | Commit **`f201bab`** — *"commit the authority witness"* — **12 files, 1,446 insertions, 0 deletions**: `BASELINE-001/` ×2, `CAEM-001/` ×7, `EVOLUTION-001/` ×1, `RELEASE-001/` ×1, `IMR-001/01-OPERATOR-AUTHORIZATION-DECISION.md` ×1 |
| **B-1.b** | No authority artifact remains untracked | ✅ | `git status --short` → **0 entries**. `ukb.py enforce --pre` → *"awaiting VCS binding: 0"* |
| **B-1.c** | The commit is durable and published | ✅ | `f201bab` is an ancestor of `8aede74`; remote `integration/recovery-001` = `8aede74`, 0 ahead / 0 behind. `df763bf` remains an ancestor — baseline preserved, no force-push, no rewrite |
| **B-1.d** | *"…and registered"* — D01 §2's additional clause | ⚫ **VOID — see §2.3** | Registration of these artifacts is constitutionally prohibited, not merely unnecessary |

### 2.2 Count reconciliation — three figures, one measurement

D01, `IMPLEMENT-001A`/`B`, and the executed commit disagree. The discrepancy is resolved, not
papered over, because `B-1`'s discharge depends on knowing what is in scope.

| Source | Figure | Assessment |
|---|---|---|
| D01 §2 | *"9 untracked authority artifacts"* | **Entries, not files.** D00's own header records the same measurement as *"95 uncommitted paths: 86 modified, **9 untracked**"* — 9 was the count of untracked `git status` **entries**, where a directory collapses to one entry. D01 carried the number across as though it counted artifacts. Arithmetically consistent with D00; **mis-labelled**. |
| `IMPLEMENT-001A` D02 · `IMPLEMENT-001B` D07 | *"19 authority files"* | **Not reproducible** against any commit. Superseded by measurement. |
| `IMPLEMENT-001C` D06 §4 commit 4 | 12 files | ✅ **Correct** — matches the executed commit exactly |
| **Executed: `f201bab`** | **12 files** | ✅ **AUTHORITATIVE** |

**`B-1`'s scope is 12 files.** The earlier figures are recorded here so the discrepancy is history
rather than a live ambiguity. No instrument was omitted: all five named authority programmes are
present in `f201bab`.

### 2.3 Why D01's *"and registered"* clause is VOID

D01 §2 requires the authority witness be *"committed **+ registered**"*. **The second half cannot
be satisfied, and must not be attempted.**

`00-BOOK/tools/config.py` `EXCLUDE_DIR_PREFIXES` lists `00-MASTER/` among the paths *"the generator
must not register"*, with this stated rationale:

> *"Operational Memory (`UCOS-RECON-C1`) — the Master Context System is execution state, not
> corpus: it must never consume permanent corpus identities, never appear in generated books, and
> never enter the portal unless explicitly projected. Covers the `00-MASTER/` subsystem…"*

Consequences, each measured:

| Consequence | Evidence |
|---|---|
| The 12 files are **ineligible** for registration by the registration authority's own declaration | `EXCLUDE_DIR_PREFIXES` contains `00-MASTER/` |
| Registration would **consume permanent corpus identities** for execution state — the defect `UCOS-RECON-C1` was convened to close | `config.py` rationale, verbatim above |
| Nothing is silently unregistered | `enforce --pre`: 1193 eligible ≡ 1193 registered · **0** unregistered · **0** awaiting VCS binding |
| No identifier was allocated by the entire `UCOS-EVO-001-W01` release | `00-BOOK/DATA/id-ledger.json` last modified at commit `214c1a9` (2026-07-28), i.e. **before** `df763bf` — untouched by all 9 release commits |

> **Determination.** `B-1` is discharged by `git add` alone. D01's *"+ registered"* clause is
> **void ab initio** — it required an act the registration authority prohibits. `IMPLEMENT-001C`
> D06 §5 reached the same conclusion (*"registration is neither required nor possible"*); D04
> supplies the primary evidence and the constitutional reason.

---

## 3. `B-2` — REGISTRATION FIXED POINT

| Field | Determination |
|---|---|
| **Identifier** | `B-2` (`T-M`, `NF-3`) |
| **Name** | Registration Fixed Point |
| **Condition** | The registration projection zone must be a **fixed point** of the registration transaction: running it must change nothing |
| **Why it is a gate** | `REG-AUTO-001` holds that source is never split from its projections; `CK-REG-DRIFT` exists to detect the split. If the projections are stale **before** a wave starts, every artifact the wave creates lands on a drifted base, and no later run can tell wave-induced drift from pre-existing drift. The wave would destroy its own evidence. |
| **D01's statement** | *"`CK-REG-DRIFT` FAIL at tier=full (745 generated files drift)"* |
| **STATUS** | ⛔ **OPEN** |

### 3.1 Discharge criterion

| Clause | Criterion | Met? |
|---|---|---|
| **B-2.a** | A registration transaction produces **zero** drift — `register.sh --guard` exits 0 | ⛔ **NO** — 731 tracked files change |
| **B-2.b** | Source and projections are committed atomically, never split | ⚪ n/a until B-2.a is reachable |
| **B-2.c** | `CK-REG-DRIFT` is **executed** and PASSES, not merely unexecuted | ⛔ **NO** — `verdict: NOT-EXECUTED`, `in_scope: false` |

### 3.2 Measurement at `8aede74`

Measured three times by running `00-BOOK/tools/register.sh` and restoring the tree after each run.
Identical every time.

| Measure | Value |
|---|---|
| Tracked files modified | **731** |
| Line delta | **+7,995 / −7,767** |
| Files **deleted** | **0** |
| Files **renamed** | **0** |
| **Untracked** files created | **0** |
| `git status` letter breakdown | `731 M` — modifications only, nothing else |
| Drift **outside** the four declared zones | **0** |

Zone distribution — exactly `STAGE-REGISTER`'s declared `writes` list in `UCOS-RFP-001`'s pipeline:

| Zone | Files |
|---|---|
| `00-BOOK/PORTAL/` | **717** |
| `00-BOOK/DATA/` | 7 |
| `00-BOOK/REGISTRIES/` | 6 |
| `00-BOOK/CONTROL-TOWER/` | 1 |

### 3.3 Cause — and why the drift is benign in kind but still blocking

The drift is **not corruption**. It is commit **`91a8b1d`** (`RG-09-A`, Wave-001) propagating into
projections that were never regenerated afterwards. That commit changed two registration **inputs**:

| Input changed | Effect on the projections |
|---|---|
| 12 new `CLASSIFY_RULES` (`^service/`, `^application/`, `^infrastructure/`, `^intelligence/`, `^knowledge/`, `^data/`, `^14-SECURITY/`, `^00-MASTER/`, `^00-CEP/`, `^00-CMG/`, `^EVO-USIS-`, `^IAC-001`) | Artifacts that previously fell through to `DEFAULT_CLASS = ("OTHER","MISC","VOL-000")` now route to real volumes. Sample: `00-BOOK/PORTAL/UCOS-APPLICATION-000001.md` — `Volume: VOL-000` → **`VOL-009`** |
| `DERIVED_CATEGORY_MAXLEN` **12 → 6** | Derived category codes narrow: `ARCHITECTURA` → `ARCHIT`, and distinct 12-char codes collapse into shared 6-char ones |

Corpus state confirming the pending reclassification is real and large:

| Measure | Value |
|---|---|
| Artifacts still homed in `VOL-000` | **736** of 1,193 |
| Distinct categories in use | 93 |
| Categories exceeding 6 characters | **62** of 93 |

**So the drift is a pending *beneficial reclassification* — 736 artifacts moving from "unhomed" to
real volumes.** That is precisely why it is still blocking: it is a **large, real, uncommitted
change to Repository Truth's classification**, and it must land as `REG-AUTO-001`'s deliberate act
with its own review, not as incidental residue discovered mid-wave.

### 3.4 Why the standard-tier gate cannot prove `B-2`

`CK-REG-DRIFT` is the check that would decide `B-2`. At the tier the repository runs by default it
does not execute:

| Check | `verdict` | `in_scope` |
|---|---|---|
| `CK-REG-DRIFT` | `NOT-EXECUTED` | `false` |
| `CK-VERIFY` | `NOT-EXECUTED` | `false` |
| `CK-DETERMINISM-BUILD` | `NOT-EXECUTED` | `false` |

This is **honest disclosure, not concealment** — it is `RO-F-06`, corrected in Wave-001 commit
`d208272`. Before that correction `uccep.json` reported these three as **fabricated `PASS`**. The
engine now emits `NOT-EXECUTED, in_scope=false` and degrades `G-07` to `PARTIAL` rather than
claiming a pass it never earned.

> **`make uccep-gate` exiting 0 with `blocking=none` therefore does not evidence `B-2`.** The check
> that would evidence it is out of tier and says so. `B-2` is decided by the §3.2 measurement, not
> by the aggregate gate.

### 3.5 Discharge route — one act, and whose it is

| Step | Act | Owner |
|---|---|---|
| 1 | Run the registration transaction: `00-BOOK/tools/register.sh` | **`REG-AUTO-001`** |
| 2 | Review the 731-file output as a deliberate reclassification — confirm 736 `VOL-000` → real-volume moves and the 62 category narrowings are intended, and that identity is preserved (`allocate()` is path-keyed; `id-ledger.json` unchanged; **0** deletions, **0** renames) | `REG-AUTO-001` |
| 3 | Commit source and projections **atomically** — never split (`REG-AUTO-001`; `CK-REG-DRIFT`) | `REG-AUTO-001` |
| 4 | Re-run: `register.sh --guard` must exit 0 with zero drift | verification |
| 5 | Confirm `verify.sh` GREEN, `uccep-gate` `blocking=none`, `closure-gate` `CLOSED gaps=0` | verification |

**Not `IMPLEMENT-001`'s act, and not `IMPLEMENT-001E`'s.** Re-deriving the classification of 1,193
artifacts is the registration authority's remit under its own admission route. `IMPLEMENT-001D`
measured this drift and deliberately restored rather than committed it, recording it as
`EVOLUTION-001` §6.2 **`W01-F-03`** with owner `REG-AUTO-001`. This mission's mandate is closeout
and authoring; committing a 731-file reclassification would be the unauthorized architecture change
its own header forbids.

### 3.6 `B-2` is `UCCEP-F-007`'s unmet acceptance clause

`WP-UCCEP-005` acceptance: *"`register.sh --guard` exits 0 with zero drift; `git status` reports no
uncommitted registration."*

| Clause | State | |
|---|---|---|
| `git status` reports no uncommitted registration | clean, 0 entries | ✅ |
| `register.sh --guard` exits 0 with zero drift | 731 files | ⛔ **= `B-2.a`** |

**`B-2` and `WP-UCCEP-005`'s first acceptance clause are one condition.** Discharging `B-2`
therefore also discharges `UCCEP-F-007` and permits its disposition to advance — see D03 §4.2,
which rejects `UCCEP-F-007` as a record correction for exactly this reason.

### 3.7 The 745 → 731 delta

D01 recorded 745; measurement now gives 731. The 14-file reduction is consistent with Wave-001
committing artifacts whose projections were previously drifted. **No claim is made that the
remaining 731 will shrink further without the §3.5 act** — the drift is caused by an *input change*
that only regeneration resolves.

---

## 4. CORRECTION OF D01 §2 AND §6

D01 states, twice, that both prerequisites are discharged by a single act:

- §2: *"discharged by ONE operator commit"*
- §6: *"2 gate-prerequisites (`B-1`, `B-2`) apply uniformly and are discharged by one act."*

> **False for `B-2`.** `B-1` is a commit act and was discharged by one (`f201bab`). `B-2` is a
> **regeneration-then-commit** act belonging to a different authority: no commit of existing bytes
> can make `register.sh` produce zero drift, because the drift is a function of `config.py` inputs
> that only a registration transaction propagates. Wave-001 executed nine commits — including the
> single largest commit sequence in the repository's history — and `B-2` is **still open**, which is
> the empirical disproof.

D01 is **not edited** (`EVOLUTION-001` principle 4 — predecessors preserved). This section
supersedes both statements. Corrected reading:

| Prerequisite | Discharge act | Owner | Acts required |
|---|---|---|---|
| `B-1` | commit the authority witness | repository operator | **1** — done at `f201bab` |
| `B-2` | run the registration transaction, review, commit source+projections atomically | **`REG-AUTO-001`** | **1** — not yet performed |

**Two prerequisites. Two distinct acts. Two distinct owners.** The claim that one act discharges
both is the reason `B-2` was believed closed when it was not.

---

## 5. RESIDUAL CONDITIONS — NOT GATE-PREREQUISITES

Recorded so no reader mistakes them for `B-3`. Each is real, each is open, none blocks the wave set.

| Condition | Why not a gate-prerequisite | Owner |
|---|---|---|
| `rib-gate` exit 1 — `VER-09` orphan / `VER-11` dead engine, `orphan_units=1` | Single cause: `UCOS-UAR-001` unwired. **This is `EB-01`'s subject matter** — a wave *item*, not a precondition of the wave | `EB-01`, Wave-002 order 2 |
| `rfp-gate` exit 1 — 5/8 criteria, 22 × `CYC-OBSERVE`, 2 × `CYC-REGISTER` | `CLO-01` now **PASSES** (the abort is gone). Closing the rest means ceasing to persist tree observations — an architecture change with its own route | `UCOS-RIB-001` · `URRC-000001`, Wave-002 |
| `UCCEP-F-006` — `ukb.py` `ImportError` branch still reaches `VALIDATION PASSED` with exit 0 | Latent, not active: both interpreters on this machine carry `jsonschema 4.26.0`. Degrades likelihood, not possibility. D03 §4.1 | `00-BOOK/tools/ukb.py`, Wave-002 |
| `repo-ops.sh` `architecture-freeze` reports 14 paths | Bound to no gate; disclosed as `RB-04`. Narrowing `FROZEN_PREFIXES` would weaken 18 write-time guards to fix 1 review gate | Wave-002 P2 |
| `repo-ops.sh` `repository-acceptance` expected-FAIL | The gate can now fail — that was `RO-F-01`'s correction. Bound to no gate | Wave-002 P2 |
| Traceability 348/15,509 = **2.24%**; `CK-HEALTH` RED | **`EB-08`** — a wave item | `EB-08` |
| Tier T1 VACANT (`VAC-01` / `UCCEP-F-004`) | External constituent act requiring `DR-RAT-11`, outside the corpus. Non-blocking per `IMPDEC-004`; the standing reason every determination is `CERTIFIED-PROVISIONAL` | external |
| One unreproduced `uccep-gate` exit 2 under concurrency | 1 occurrence in 14 attempts; cause not established. Failing **closed** is the designed behaviour | Wave-002 P3 |

**8 residual conditions. 0 are gate-prerequisites. `B-1` and `B-2` remain the complete set.**

---

## 6. DETERMINATION

> ### ⛔ **THE GATE-PREREQUISITE CONJUNCT IS NOT MET. `B-1` DISCHARGED · `B-2` OPEN.**
>
> **`B-1` Authority Witness — DISCHARGED.** 12 files at commit `f201bab`, 0 deletions; working tree
> clean; `awaiting VCS binding: 0`; published and baseline-preserving. Its scope is **12 files**,
> not D01's 9 (which counted `git status` *entries*) and not `IMPLEMENT-001A`/`B`'s 19 (not
> reproducible). D01's *"+ registered"* clause is **VOID**: `00-MASTER/` sits in
> `EXCLUDE_DIR_PREFIXES` because *"the Master Context System is execution state, not corpus: it must
> never consume permanent corpus identities."* Registration is prohibited, not pending.
>
> **`B-2` Registration Fixed Point — OPEN.** A registration transaction rewrites **731** tracked
> files (**+7,995 / −7,767**; **0** deleted, **0** renamed, **0** untracked), confined entirely to
> the four declared projection zones. Cause: Wave-001 commit `91a8b1d` changed two registration
> inputs and the projections were never regenerated — **736** of 1,193 artifacts still sit in
> `VOL-000` and **62** of 93 categories still exceed 6 characters. The drift is a *pending
> beneficial reclassification*, which is exactly why it must land as `REG-AUTO-001`'s reviewed act
> rather than as mid-wave residue. `CK-REG-DRIFT` cannot evidence it: `NOT-EXECUTED`,
> `in_scope: false` at the standard tier, disclosed by `RO-F-06`.
>
> **D01 §2 and §6 are corrected.** Two prerequisites, **two distinct acts, two distinct owners** —
> not "one operator commit". Wave-001 ran nine commits and `B-2` survived them, which is the proof.
>
> **`B-2` is also `WP-UCCEP-005`'s unmet acceptance clause**, so one act discharges both `B-2` and
> `UCCEP-F-007`.
>
> **Consequence for the backlog.** D00 attaches `B-1` **and** `B-2` to all nine items and D01 §1
> makes an unsatisfied `⇒ GATE-PREREQ` block *"the whole wave set"*. With `B-2` open, **no `EB-*`
> item is admissible.** One act by `REG-AUTO-001` — §3.5 — changes that.

---

*END — `IMPLEMENT-001` Deliverable 04 · AUTHORITY = NONE · `CERTIFIED-PROVISIONAL` · Tier T1 VACANT*
