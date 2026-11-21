# UICM — REPLAY VERIFICATION DETERMINATION

| Field | Value |
|---|---|
| **ARTIFACT** | `UICM-REPLAY-VERIFICATION-DETERMINATION.md` |
| **PROGRAMME** | `UCOS-UICM-000001` — Foundation Closure Phase 2 (Replay Verification Determination) |
| **AUTHORITY** | **NONE — DERIVED TRUTH.** No replay capability is created. No second determinism authority is vested. Every instrument named below is located. |
| **CLASSIFICATION** | `EVIDENCE` |
| **CANONICAL OWNER REUSED** | `engine/determinism/reproduce.py` · `engine/determinism/hermetic.py` · `engine/uicm/controller.py` (`measure_twice`, `replay`) · `engine/uaue/gate.py` (`--replay`) · `engine/validation/*` · `engine/certification/*` |
| **BASELINE** | HEAD `1f869865` · branch `integration/recovery-001` · working tree DIRTY |
| **DISPOSITION** | **DETERMINATION ONLY.** No code. No gate wired. No register modified. |
| **COMPANION** | `UICM-OBSERVATION-CONTINUITY-DETERMINATION.md` (Phase 1) · `GATE-PURITY-DETERMINATION.md` (Phase 3) |

---

## 1. The question, and the answer

**Question.** Can the existing validation engine, certification engine, evidence engine and replay
mechanisms provide deterministic replay, such that:

```
Repository State  +  Execution Context  +  Observation History     =    Determination
        (same)              (same)                 (same)                    (same)
```

**Determination D-2.0 — split answer, and the split is the finding.**

| Sub-question | Answer | Basis |
|---|---|---|
| Do the located instruments provide **deterministic byte-replay of derived surfaces**? | **YES.** Three independent instruments already do it. | §2 |
| Do they provide **deterministic replay of a determination over the full three-term input**? | **NO — not on this baseline.** Two of the three input terms are not inputs. | §3 |
| Is the missing part a **missing capability**? | **NO.** It is three missing *bindings* over existing capability. | §4 |

So: replay verification is **possible with zero new capability**, and is **not achieved today**.

---

## 2. What already exists — three located replay instruments

**D-2.1:** replay is owned three times, at three scopes, and the three do not duplicate each other.
No fourth instrument may be created.

| Scope | Owner | Mechanism | Comparison basis |
|---|---|---|---|
| **Repository-wide reproducibility** | `engine/determinism/reproduce.py` | `double_build()`, `compare_builds()`, `ReproducibilityResult`, `FileDiff`; `hermetic.py` supplies `hermetic_env()`, `HermeticEnvironment`, `DependencyLockReport` | file-level diff between two builds |
| **Programme-local measurement determinism** | `engine/uicm/controller.py` | `measure_twice()` runs the lifecycle twice and compares matrix digests; `replay()` compares **bytes** of the rendered record set | digest + bytes |
| **Derived-surface byte replay (reference pattern)** | `engine/uaue/gate.py` | `--replay` regenerates the history projection and 18 registers **in memory** and compares committed bytes; writes are reserved to `--render` | bytes, not parsed structures |

**D-2.2 — the UAUE pattern is the correct one and is already in `verify.sh`.** Stage 6d ("evolution
surface replay") states the rule this determination adopts verbatim: *byte comparison, not parsed
comparison — a projection that only matches after normalisation is a projection whose canonical
form nobody is holding to*, and *the remedy for a drift report is never to edit the file*. That
stage is the located precedent for binding any replay check. No new pattern is needed.

**D-2.3 — fail-closed is already correct in UICM.** `UICM-INV-13`
(`_inv_measurement_determinism`) reports **VIOLATED**, not SKIPPED, when `replay_digest is None`.
An unmeasured determinism question is a violation, not a pass. This is the behaviour
`CMG-000001` Art. XLIX.7 requires and it must not be weakened.

---

## 3. Why the three-term equation does not hold today

Each term is examined for whether it is (a) an input to the determination and (b) sealed into the
determination's own bytes.

### Term 1 — Repository State: **INPUT, SEALED.** ✅

`uicm.json` carries five `source_digests`; the matrix digest seals both content and structure; the
population is re-derived from live tracked content by `discover_population()` and 17 probes.
Two-pass agreement is asserted by `measure_twice()`. This term is sound.

### Term 2 — Execution Context: **NOT AN INPUT.** ❌

**D-2.4:** there is no context term in the determination. The engine reads the tree; it does not
record *under what conditions* it read it. The repository already owns the primitive that would
supply this term — `engine/constitution/gateway.py` (`UCOS-CMG-EXEC-000001`) is the **sole producer
of a clean `StateSeal`**, and `engine.constitution.state` "refuses to verify, certify, register,
measure or govern under a dirty seal" (quoted in
`00-MASTER/UCOS-UICO-000001/UCOS-UICO-OWNER-BOUNDARY-DETERMINATION.md` §2). UICM does not consume
it.

The concrete cost is measurable on this baseline: the working tree is **DIRTY** (35 untracked
entries, plus staged and modified tracked registers), yet nothing in the UICM determination records
that fact. Two determinations produced from the same commit under different working-tree states are
therefore **indistinguishable by their own bytes** — which is exactly the failure mode that
produced findings `F-A` and `F-B` in `FINAL-FREEZE-ELIGIBILITY-DETERMINATION.md` §1.1.

`hermetic.py` bounds the *environment* (no clock, no network, pinned dependencies). It does not
bound the *tree state*. These are different terms and only the first is held.

### Term 3 — Observation History: **NOT AN INPUT.** ❌

Established and measured in `UICM-OBSERVATION-CONTINUITY-DETERMINATION.md` §2 (findings G-1..G-4):
the committed register is a write-only projection; the registry is rebuilt from `GENESIS_HASH` each
process. **A term that is overwritten by the run that consumes it is not an input.**

**D-2.5 — this is why replay today is weaker than it appears.** `measure_twice()` proves
*intra-process* agreement: two passes in one process over one tree. It does not and cannot prove
*inter-run* agreement, because the second run does not see the first run's history. Under
continuity (Phase 1), byte-identical genesis (0 appends, 0 differing coordinates) becomes the
*fixed-point* proof that closes this term.

### Term 4 (implied) — Determination: **PRODUCED, but never executed by any gate.** ❌

Measured: `grep -rn "engine.uicm|UICM" verify.sh Makefile .github/workflows/` → **no matches.**
There is no `uicm-gate.yml` among the 28 workflows. Committed UICM registers are refreshed only by
a manual `python -m engine.uicm.controller --render`.

**D-2.6:** a replay check that exists but is never run yields **UNKNOWN**, not PASS. This is the
same class as `UICM-INV-13`'s own fail-closed rule, applied one level up. Corroborated from the
programme's own measurements: **42 of the 158 registered gaps are `determinism` gaps** reading *"no
located instrument asks the replay question of this capability"*, resolution owner
`UCOS-REPOSITORY-ROOT`, instrument `verify.sh` (`UICM-GAP-OWNER-MATRIX.md` §3 row 8, §5 dimension
13). The programme has already classified its own replay gap and assigned it to the repository
root.

---

## 4. What is required — three bindings, no new capability

**D-2.7:** the equation closes with three bindings over instruments that already exist. Each is a
binding, not a build.

| # | Binding | Reuses | Term closed | New capability? |
|---:|---|---|---|---|
| **R-1** | Observation register becomes a **declared input**, rehydrated and verified (L1–L11) before measurement | `ObservationRegistry` + loader (Phase 1, M1) | Term 3 | none |
| **R-2** | **Execution context is recorded in the determination**: the `StateSeal` from `engine/constitution/gateway.py`, plus the `hermetic.py` environment report | `engine/constitution/gateway.py`, `engine/determinism/hermetic.py` | Term 2 | none — consume the sole existing producer |
| **R-3** | **A gate executes replay**: a read-only `--gate` stage and a separate byte-comparison `--replay` stage bound into `verify.sh`, rendering reserved to `--render` | `engine/uaue/gate.py` pattern; `verify.sh` stages 6c/6d as the located precedent | Term 4 | none |

### 4.1 Refusals

- **REFUSED: a new replay engine, determinism authority, replay registry or evidence store.** Three
  located instruments already cover the three scopes (D-2.1).
- **REFUSED: adding the observation register to `source_digests` to "make it an input".**
  `observation_head` already seals it; see `UICM-OBSERVATION-CONTINUITY-DETERMINATION.md` RD-5.
- **REFUSED: satisfying R-2 by stamping a timestamp, hostname or run counter.** Forbidden by
  `uicm.json.determinism.forbidden_in_emitted_bytes`. The context term must be a **content-derived
  seal**, which is precisely what `StateSeal` is.
- **REFUSED: normalising before comparison.** Byte comparison only (D-2.2).
- **REFUSED: a second pipeline, scheduler or daemon for R-3.** `CMG-000001` Art. LXVI.7 permits
  exactly one entry point, and it is `verify.sh`.

### 4.2 One hard dependency on Phase 3

**D-2.8 — R-3 must not land while the gate-mode question is open.** `GATE-PURITY-DETERMINATION.md`
measures ≥24 gates that write tracked register surfaces on their `--gate` path, and three engines
(`ucl`, `ufep`, `uis`) whose `--render` flag is parsed and never read — so their "replay" targets
**render and then diff**, which is a *render-and-compare*, not a replay. Binding a UICM replay
stage into that regime would reproduce the defect rather than close a gap.

Concretely: a stage that writes before it compares can only ever compare a file against itself.
`.github/workflows/roadmap-gate.yml` already contains the admission — it runs
`git checkout -- 00-MASTER/UCOS-MXR-001` after the gate, i.e. **CI reverts the gate's own
mutation**. Replay verification built on top of that is not verification.

**Sequence is therefore fixed: Phase 3 mode declaration → R-3 → R-1/R-2 measurement.**

---

## 5. Replay verification acceptance criteria

When R-1..R-3 are authorized and landed, replay verification is achieved when **all six** hold. All
six are measurements over existing instruments; none requires a new one.

| # | Criterion | Instrument | Expected |
|---:|---|---|---|
| A-1 | Rehydrate the committed register and re-render: bytes identical | `ObservationRegistry.from_document` + `render` | byte-identical |
| A-2 | Unchanged repository → 0 appends, 0 differing coordinates, register unchanged (fixed point) | reconciliation case 1 | fixed point holds |
| A-3 | `measure_twice()` passes agree on `observation_head` and matrix digest | `UicmController.measure_twice` | identical |
| A-4 | Both passes complete **before** any write | explicit assertion (Phase 1, M5) | asserted and tested |
| A-5 | Same commit + same `StateSeal` + same register → identical determination bytes on a **second process and a second machine** | `hermetic.py` + `reproduce.double_build` | identical |
| A-6 | The check is **executed** by `verify.sh`, fail-closed; deleting the stage closes the gate rather than silently unbinding the check | `verify.sh` stage, UAUE pattern | non-zero exit on drift |

**A-6 is the criterion the current baseline fails outright**, and it is the one that converts the
other five from *measurable* into *measured*. Note the UAUE stage-6c comment already states the
self-referential property A-6 requires: the gate measures that the pipeline actually invokes it, so
removing the stage fails the gate instead of quietly disabling it.

---

## 6. Answer to the mandated form

```
Input:
   Repository State        SEALED   — 5 source_digests + matrix digest      ✅
 + Execution Context       ABSENT   — StateSeal exists, is not consumed     ❌  → R-2
 + Observation History     ABSENT   — write-only projection, rebuilt each run ❌ → R-1

Expected:
   Same Input = Same Determination

Measured today:
   Same commit, two runs        →  same determination, by re-derivation, not by replay
   Same commit, dirty vs clean  →  INDISTINGUISHABLE  (no context term)
   Same commit, history moved   →  history silently discarded  (no history term)
   Any run under a gate         →  NEVER MEASURED  (no gate invokes engine.uicm)  ❌ → R-3
```

---

## 7. Determination summary

| # | Determination |
|---|---|
| **D-2.0** | Deterministic byte-replay of derived surfaces: **YES**, three located instruments. Deterministic replay of the three-term determination: **NO** on this baseline. |
| **D-2.1** | Replay is owned three times at three non-overlapping scopes. No fourth instrument may be created. |
| **D-2.2** | Byte comparison, never normalised comparison. `verify.sh` stage 6d is the located precedent. |
| **D-2.3** | An unmeasured determinism question is a **violation**, not a pass. Existing fail-closed behaviour is preserved. |
| **D-2.4** | Execution Context is not an input. The sole `StateSeal` producer exists and is unconsumed. |
| **D-2.5** | `measure_twice()` proves intra-process agreement only. Inter-run agreement requires Phase 1. |
| **D-2.6** | No gate, target or workflow executes `engine.uicm`. The programme's own gap register already assigns 42 determinism gaps to `UCOS-REPOSITORY-ROOT` with instrument `verify.sh`. |
| **D-2.7** | Closure requires exactly three **bindings** (R-1 history as input · R-2 context as seal · R-3 gate execution). Zero new capability. |
| **D-2.8** | **R-3 is blocked on Phase 3.** A replay stage bound into a write-on-gate regime compares a file against itself. |

**Phase 2 verdict: deterministic replay is ACHIEVABLE by reuse and is NOT ACHIEVED. Three bindings
are specified; none is authorized here; R-3 is sequenced after gate-mode declaration.**
