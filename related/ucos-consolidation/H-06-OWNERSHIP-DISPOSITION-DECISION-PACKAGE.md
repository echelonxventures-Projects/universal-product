# H-06 OWNERSHIP DISPOSITION DECISION PACKAGE

| Field | Value |
|---|---|
| **ID** | H-06-ODDP |
| **Authority** | DECISION PREPARATION ONLY. No implementation authorized. No policy selected. No declaration modified. |
| **Phase** | Foundation Closure — Gate Purity — Ownership Disposition |
| **Baseline** | HEAD `1f869865` · branch `integration/recovery-001` · working tree DIRTY |
| **Purpose** | Present the complete 45-target ownership register and the decision fields required to finalise the H-06 ownership model |
| **Reads** | H-06-GATE-OWNERSHIP-MODEL-RESOLUTION-DETERMINATION.md · H-06-SUCCESS-CRITERIA-REBASE-DETERMINATION.md · H-06-R4-GRANDFATHERING-POLICY-DECISION-RECORD.md |
| **Produced** | 2026-08-16 |
| **Status** | PACKAGE PREPARED — AWAITING OWNER DISPOSITION |

---

## 0. What This Package Asks

Five decisions (§9). Everything before §9 is the evidence they rest on.

The central finding that shapes all five: **the `--check-declaration` guard population is
exactly Class A ∪ Class B ∪ {`uar-gate`} = 23 gate targets.** The other **22 gate targets
have no guard that reads a declaration at all.**

This is decisive. Declaring a `gate_mode` for a gate whose engine carries no
`--check-declaration` guard produces a claim that **nothing verifies** — structurally
identical to GP-5, where `verify.sh` stage 4's "Read-only" label was false and undetected
because no guard read it. For those 22 targets, a declared mode would be no more trustworthy
than a comment.

Adding a guard is engine modification, which is outside authorized scope. Therefore the
honest disposition for the 22 guardless targets is a **governed gap**, not a declaration.
That conclusion rests on enforcement reachability, not merely on the absence of a surface.

---

## 1. Method and Provenance

Every figure was measured against `HEAD:` via `git show`, per rebase determination D-1.4.
Class assignment used two independent axes: (a) presence of a non-generated JSON carrying a
`programme` **object** in the gate's home; (b) presence of the gate's engine as a `producer`
or `owner` in `00-BOOK/DATA/generated-artifact-registry.json`.

Additional attributes measured for this package: `--check-declaration` guard presence per
engine, CI workflow coverage per gate, `verify.sh` invocation per gate, and GP finding
membership per gate.

No file was modified. Column legend for §2:

| Column | Meaning |
|---|---|
| **Cls** | Ownership class — A / B / C / D |
| **Canonical owning surface** | The authored, non-generated artifact that owns this programme's declaration |
| **pt** | `programme` value type — `obj` (field insertable) · `str` (not insertable) · `—` (absent) |
| **fwp** | `forbidden_write_prefixes` present in the `programme` object (the placement anchor) |
| **prod** | Registered generated artifacts attributed to this engine |
| **chk** | Engine carries a `--check-declaration` self-guard — i.e. enforcement can reach it |
| **CI** | Gate target or its engine referenced by ≥1 CI workflow at HEAD |
| **GP** | GP findings this gate participates in |
| **Ext** | `gate_mode` extension applicability — see §4 |

---

## 2. Complete Register — All 45 Baseline Gate Targets

Questions 1, 2, 3 and 4 answered in one register.

### 2.1 Class A — `*-declaration.json` Owning Surface (9)

| # | Gate target | Canonical owning surface | pt | fwp | prod | chk | CI | GP | Ext |
|--:|---|---|---|:-:|--:|:-:|:-:|---|---|
| 1 | `acee-gate` | `00-MASTER/ACEE-000001/acee-declaration.json` | obj | Y | 17 | Y | Y | GP-1 | **APPLICABLE** |
| 2 | `aee-gate` | `00-MASTER/UCOS-AEE-001/aee-declaration.json` | obj | Y | 15 | Y | Y | GP-1, GP-10 | **APPLICABLE** |
| 3 | `baseline-gate` | `00-MASTER/BASELINE-001/baseline-declaration.json` | obj | Y | 8 | Y | Y | GP-1 | **APPLICABLE** |
| 4 | `rfp-gate` | `00-MASTER/UCOS-RFP-001/rfp-declaration.json` | obj | **n** | 0 | Y | Y | — | APPLICABLE — no `fwp` anchor |
| 5 | `ucl-gate` | `00-MASTER/UCL-000001/ucl-declaration.json` | obj | Y | 15 | Y | Y | GP-1, GP-4 | **APPLICABLE — authorized** |
| 6 | `ufep-gate` | `00-MASTER/UCOS-UFEP-001/ufep-declaration.json` | obj | Y | 5 | Y | n | GP-1, GP-4 | **APPLICABLE — authorized** |
| 7 | `uis-gate` | `00-MASTER/UIS-001/uis-declaration.json` | obj | Y | 10 | Y | Y | GP-1, GP-4 | **APPLICABLE** |
| 8 | `urat-gate` | `00-MASTER/UCOS-URAT-001/urat-declaration.json` | obj | Y | 5 | Y | n | GP-1 | **APPLICABLE — authorized** |
| 9 | `utce-gate` | `00-MASTER/UCOS-UTCE-001/utce-declaration.json` | obj | Y | 5 | Y | n | GP-1 | **APPLICABLE — authorized** |

### 2.2 Class B — Domain-Named Owning Surface (13)

| # | Gate target | Canonical owning surface | pt | fwp | prod | chk | CI | GP | Ext |
|--:|---|---|---|:-:|--:|:-:|:-:|---|---|
| 10 | `mcos-gate` | `00-MASTER/MCOS-000001/mcos-civilization.json` | obj | n | 9 | Y | Y | GP-1 | APPLICABLE — O-3 |
| 11 | `rib-gate` | `00-MASTER/UCOS-RIB-001/rib-blueprint.json` | obj | Y | 16 | Y | Y | GP-2 | APPLICABLE — O-3 |
| 12 | `ucaf-gate` | `00-MASTER/UCOS-UCAF-001/ucaf-authority.json` | obj | Y | 10 | Y | n | GP-1 | APPLICABLE — O-3 |
| 13 | `uccep-gate` | `00-MASTER/UCCEP-000000/uccep-bindings.json` | obj | Y | 0 | Y | Y | — | APPLICABLE — O-3 |
| 14 | `ucda-gate` | `00-MASTER/UCDA-000001/ucda-decisions.json` | obj | Y | 9 | Y | n | GP-1 | APPLICABLE — O-3 |
| 15 | `ucef-gate` | `00-MASTER/UCEF-000001/ucef-framework.json` | obj | Y | 14 | Y | Y | GP-1 | APPLICABLE — O-3 |
| 16 | `uei-gate` | `00-MASTER/UEI-000001/uei-evolution.json` | obj | Y | 24 | Y | Y | GP-1 | APPLICABLE — O-3 |
| 17 | `uer-gate` | `00-MASTER/UER-000001/uer-resilience.json` | obj | Y | 15 | Y | Y | GP-1 | APPLICABLE — O-3 |
| 18 | `umk-gate` | `00-MASTER/UMK-000001/umk-kernel.json` | obj | n | 9 | Y | Y | GP-1 | APPLICABLE — O-3 |
| 19 | `uprf-gate` | `00-MASTER/UPF-000001/upf-provider.json` | obj | n | 9 | Y | Y | GP-1 | APPLICABLE — O-3 |
| 20 | `urrc-gate` | `00-MASTER/URRC-000001/urrc-bindings.json` | obj | Y | 19 | Y | Y | GP-2 | APPLICABLE — O-3 |
| 21 | `uaep-gate` | `00-MASTER/UAEP-000001/uaep-platform.json` | obj | n | 0 | Y | Y | — | APPLICABLE — O-3 |
| 22 | `uaie-gate` | `00-MASTER/UAIE-000001/uaie-architecture.json` | obj | n | 10 | Y | Y | — | APPLICABLE — O-3 |

### 2.3 Class C — `00-MASTER` Home, No Capable Owning Surface (11)

| # | Gate target | Home | Surface present | pt | prod | chk | CI | GP | Ext |
|--:|---|---|---|---|--:|:-:|:-:|---|---|
| 23 | `assimilate-gate` | `UAKOS-CLOSURE-008` | none | — | 13 | n | Y | GP-3 | **NOT APPLICABLE** |
| 24 | `closure-gate` | `UAKOS-CLOSURE-002` | none | — | 0 | n | Y* | GP-3 | **NOT APPLICABLE** |
| 25 | `closure-phase2-gate` | `UAKOS-CLOSURE-002` | none | — | 0 | n | n | GP-3 | **NOT APPLICABLE** |
| 26 | `closure-phase3-gate` | `UAKOS-CLOSURE-002` | none | — | 0 | n | n | GP-3 | **NOT APPLICABLE** |
| 27 | `closure009-gate` | `UAKOS-CLOSURE-009` | none | — | 11 | n | Y | GP-3 | **NOT APPLICABLE** |
| 28 | `closure009-baseline-gate` | `UAKOS-CLOSURE-009` | none | — | 11 | n | Y | GP-3 | **NOT APPLICABLE** |
| 29 | `corpus-gate` | `UKAP-001` | none | — | 10 | n | Y | GP-3 | **NOT APPLICABLE** |
| 30 | `final-closure-gate` | `P0-FINAL-CLOSURE-002` | 9 certification JSONs | str | 0 | n | n | GP-3 | **NOT APPLICABLE** |
| 31 | `lifecycle-closure-gate` | `P0-LIFECYCLE-CLOSURE-001` | none | — | 10 | n | n | GP-3 | **NOT APPLICABLE** |
| 32 | `roadmap-gate` | `UCOS-MXR-001` | none | — | 11 | n | Y | GP-3, GP-7 | **NOT APPLICABLE** |
| 33 | `uar-gate` | `UCOS-UAR-001` | `uar-analyses.json` | **str** | 1 | **Y** | Y | GP-2 | **NOT APPLICABLE** — string blocks insertion |

`*` `closure-gate`'s engine is executed by `roadmap-gate.yml` as a gitignored derived-input
materialisation step (`closure_engine.py`, workflow line 75), not as an independently gated
step. Disclosed rather than counted as gate coverage.

**`uar-gate` is the sole Class C target whose engine carries a `--check-declaration` guard.**
Enforcement can reach it, but its `programme` value is a JSON string, so no field is
insertable without a structural change (forbidden by IADR §5).

### 2.4 Class D — No `00-MASTER` Home (12)

| # | Gate target | Implementation | Nearest authored surface | pt | prod | chk | CI | Ext |
|--:|---|---|---|---|--:|:-:|:-:|---|
| 34 | `cmg-gate` | `00-CMG/tools/cmg-gate.sh` | `00-CMG/CMG-REGISTRY.json` | — | 0 | n | n | **NOT APPLICABLE** |
| 35 | `constitution-gate` | `platform.universal_foundation.constitution_cli` | `catalog/foundation-*.json` | — | 0 | n | Y | **NOT APPLICABLE** |
| 36 | `convergence-gate` | same | `catalog/foundation-convergence.json` | — | 0 | n | Y | **NOT APPLICABLE** |
| 37 | `foundation-gate` | `platform.universal_foundation.cli` | `catalog/foundation-*.json` | — | 0 | n | n | **NOT APPLICABLE** |
| 38 | `freeze-gate` | `platform.universal_foundation.constitution_cli` | `catalog/foundation-freeze.json` | — | 0 | n | Y | **NOT APPLICABLE** |
| 39 | `homing-gate` | `platform.universal_ownership.cli` | `catalog/ucos-ownership-declarations.json` | — | 0 | n | n | **NOT APPLICABLE** |
| 40 | `publication-gate` | `intelligence.publication` | `intelligence/UCOS-UPI-001/*.json` | **str** | 0 | n | Y | **NOT APPLICABLE** |
| 41 | `research-gate` | `intelligence.research` | `intelligence/UCOS-URI-001/*.json` | **str** | 0 | n | Y | **NOT APPLICABLE** |
| 42 | `research-publication-gate` | aggregator (`research-gate publication-gate`) | none of its own | — | 0 | n | n | **NOT APPLICABLE** |
| 43 | `rpi-gate` | `platform.repository_intelligence.cli` | none | — | 0 | n | n | **NOT APPLICABLE** |
| 44 | `selfaware-gate` | `engine.knowledge.cli` | none | — | 0 | n | n | **NOT APPLICABLE** |
| 45 | `uapf-gate` | `platform.universal_pipeline.cli` | `catalog/uapf-pipelines.json` | — | 0 | n | n | **NOT APPLICABLE** |

### 2.5 Register Totals

| Measure | Value |
|---|---:|
| Gate targets at HEAD | **45** |
| Class A / B / C / D | **9 / 13 / 11 / 12** |
| Capable owning surface exists (`programme` object) | **22** |
| Registered producers | **26** |
| `--check-declaration` guard present | **23** |
| CI-referenced | **29** |
| Declared mode at HEAD | **2** (`cmg-gate` OBSERVE, `rpi-gate` EXECUTION) |
| Authorized for `gate_mode` today | **4** |

---

## 3. Ownership Class Summary

| Class | Count | Owning surface | Insertable | Enforceable | Disposition candidate |
|---|--:|---|:-:|:-:|---|
| **A** | 9 | `*-declaration.json` | YES | YES | **Declare** |
| **B** | 13 | `<prefix>-<domain>.json` | YES | YES | **Declare** (needs O-3) |
| **C** | 11 | absent (1 string-blocked) | NO | 1 of 11 | **Governed gap** |
| **D** | 12 | absent or wrong purpose | NO | NO | **Governed gap** (explicit exclusion) |

**Insertable ∧ Enforceable = 22.** This is the maximum honestly declarable population under
the existing model. It matches the ownership-resolution determination's §5.1 figure exactly,
now corroborated by a second, independent axis: enforcement reachability.

---

## 4. Question 4 — `gate_mode` Extension Applicability

### 4.1 Applicability Test

A gate target is `gate_mode`-extension applicable only if **all three** hold:

| # | Condition | Rationale |
|---|---|---|
| T-1 | An authored, non-generated owning surface exists | A declaration cannot live in generated output |
| T-2 | Its `programme` value is a JSON **object** | A field cannot be added inside a string or absent block |
| T-3 | The engine carries a `--check-declaration` guard | Otherwise the declaration is an unverified claim — the GP-5 defect class |

### 4.2 Results

| Result | Count | Members |
|---|--:|---|
| **APPLICABLE** — all three satisfied | **22** | Class A (9) + Class B (13) |
| **NOT APPLICABLE — T-2 fails** (string) | 3 | `uar-gate`, `research-gate`, `publication-gate` |
| **NOT APPLICABLE — T-1 fails** (no surface) | 20 | Class C 10 + Class D 10 |
| **Total not applicable** | **23** | |

### 4.3 T-3 Is the Novel Constraint

T-1 and T-2 were established by the ownership-resolution determination. **T-3 is new to this
package** and it changes nothing about the applicable set — but it changes the *reason* the
other 23 are excluded, and therefore the strength of the governed-gap disposition.

Measured: the 23 engines carrying `--check-declaration` are **exactly** Class A (9) ∪ Class B
(13) ∪ {`uar-gate`}. The correspondence is total — not approximate.

| Population | Count | Overlap with `chk` |
|---|--:|--:|
| Class A ∪ Class B | 22 | **22 of 22** |
| Class C | 11 | 1 (`uar-gate`) |
| Class D | 12 | **0** |

**D-4.1.** The repository has already, implicitly, drawn exactly the boundary H-06 needs. The
gates that carry a declaration guard are precisely the gates that have a declaration surface.
The 22 declarable targets are the 22 enforceable targets. This is not a coincidence to be
exploited but a coherence to be preserved: **the ownership model should follow the enforcement
boundary that already exists rather than assert coverage beyond it.**

**D-4.2.** For the 22 guardless targets, declaring a mode without also adding a guard would
create 22 unverifiable claims. Adding guards is engine modification — outside authorized
scope, and for Class D there is no programme declaration model for a guard to read. This makes
the governed gap the *correct* disposition, not merely the available one.

---

## 5. Question 5 — Governed Gap Candidates

### 5.1 Definition

A **governed gap** is a gate target with no declarable mode, recorded in the existing
`ASSESSMENT-CONFLICT-REGISTER.md` with a named owner and a stated reason, per R-4 control C-5.
It creates no surface. It is an owned, falsifiable statement of absence — the honest
alternative to a fabricated declaration.

### 5.2 Candidates — 23 Targets in Four Reason Groups

**G-1 — No owning surface; `00-MASTER` home exists (10)**

`assimilate-gate` · `closure-gate` · `closure-phase2-gate` · `closure-phase3-gate` ·
`closure009-gate` · `closure009-baseline-gate` · `corpus-gate` · `final-closure-gate` ·
`lifecycle-closure-gate` · `roadmap-gate`

Reason: no authored JSON with a `programme` object; no `--check-declaration` guard.
**Escalation path available:** a declaration instance could be created in the existing home —
this is instantiation of an existing class, not a new surface (ownership-resolution D-5.1) —
but it requires authorization and a guard to read it. 6 of these 10 are registered producers
(66 artifacts total), so their PRODUCER character is already documented.

**G-2 — Surface exists but `programme` is a string (1)**

`uar-gate`

Reason: `uar-analyses.json` is authored and non-generated, and the engine **does** carry a
`--check-declaration` guard — the only Class C target that does. Blocked solely by T-2.
**Cheapest theoretical fix, most constitutionally awkward:** converting string → object is a
structural change to an authored governance surface. Requires owner decision.

**G-3 — No `00-MASTER` home; authored surface exists but differently purposed (7)**

`cmg-gate` · `constitution-gate` · `convergence-gate` · `foundation-gate` · `freeze-gate` ·
`homing-gate` · `uapf-gate`

Reason: nearest surfaces are a criteria register, a pipeline catalog, an ownership-assignment
catalog, and an identifier registry. None has a `programme` object; none is a mode surface.
Note `cmg-gate` already declares OBSERVE in its script header and `verify.sh` stage 6 — one of
only two declared modes at HEAD. Its gap is machine-readability, not undeclaredness.

**G-4 — No `00-MASTER` home; no surface or string-typed (5)**

`publication-gate` · `research-gate` · `research-publication-gate` · `rpi-gate` ·
`selfaware-gate`

Reason: `research`/`publication` have string-typed `programme`; `rpi-gate` and
`selfaware-gate` have no authored JSON surface; `research-publication-gate` is a pure
aggregator with no engine of its own. Note `rpi-gate` already declares EXECUTION in the
Makefile "HONEST LIMIT" comment at line 266 — the second of the two declared modes at HEAD.

### 5.3 Gap Register Requirements

Each governed gap entry must carry, at minimum:

| Field | Content |
|---|---|
| Gate target | e.g. `roadmap-gate` |
| Ownership class | A / B / C / D |
| Reason group | G-1 … G-4 |
| Blocking condition | no surface · string-typed `programme` · no guard · no `00-MASTER` home |
| Named owner | the party who can discharge it |
| Escalation path | instantiate declaration · restructure surface · new module model · permanent exclusion |
| Registry evidence | producer artifact count, where present |

**D-5.1.** A gap without a named owner and an escalation path is indistinguishable from the
pre-H-06 status quo. The R-4 evidence determination records the precedent: GP-11 reached 42
undeclared "after years of development" precisely because absence was never owned.

---

## 6. Question 6 — Migration Impact

### 6.1 Enforcement Activation Impact

If `gate_mode` becomes a required field validated by `--check-declaration`:

| Population | Count | Effect on activation |
|---|--:|---|
| Engines carrying `--check-declaration` | **23** | **All 23 fail their self-guard** until their surface carries `gate_mode` |
| Of those, with a capable surface | 22 | Can be made compliant by an additive field |
| Of those, **cannot** be made compliant | **1** (`uar-gate`) | `programme` is a string — compliance requires a structural change |
| Engines with no guard | 22 | Unaffected — and unreachable by enforcement in either direction |

**D-6.1.** Activation is bounded and knowable: **23 engines**, of which 22 are remediable
additively and 1 is structurally blocked. `uar-gate` is therefore a hard blocker to any
Option 2 (immediate non-compliance) activation, independent of scope authorization.

**D-6.2.** This is materially better than the R-4 decision record's worst case, which sized
activation impact at 45 gate targets. The true enforcement surface is 23, and 22 of them are
one additive field away from compliance. It is also materially worse in one respect: one of
the 23 cannot comply at all without a forbidden structural change.

### 6.2 `verify.sh` Exposure — Low

`verify.sh` at HEAD invokes 9 stages. Of the 45 gate targets it directly invokes **only
`cmg-gate`** (stage 6, `bash 00-CMG/tools/cmg-gate.sh`). It also invokes
`uga_engine.py gate`, which is not a `*-gate` target.

| Path | Exposure |
|---|---|
| Direct `*-gate` invocation | **1 of 45** (`cmg-gate`) |
| Indirect via stage 1b `generate-prerequisites.sh` | closure/phase2/phase3 engines execute |
| `--full` only | `register.sh --guard` |

**D-6.3.** Enforcement activation would **not** break `verify.sh` through the gate-target
plane, because `verify.sh` does not run the 23 guarded engines. `cmg-gate` is Class D and
carries no `--check-declaration` guard. This substantially de-risks activation relative to the
R-4 determination's assumption that "`verify.sh` fails until all 24 engines are declared."

### 6.3 CI Exposure — High

**29 of 45** gate targets are referenced by ≥1 of the 27 CI workflows at HEAD.

| Overlap | Count | Consequence |
|---|--:|---|
| Guarded (`chk`) **and** CI-referenced | **18** | Enforcement activation breaks 18 CI workflows simultaneously |
| Guarded, not CI-referenced | 5 | Local failure only |
| Unguarded, CI-referenced | 11 | Unaffected by activation |

**D-6.4. CI, not `verify.sh`, is the migration risk surface.** Any activation must be
sequenced against the 18 guarded-and-CI-referenced targets. This inverts the risk model
assumed in the R-4 evidence determination.

### 6.4 GP Remediation Interaction

| GP | Population | Gate targets affected | Interaction with ownership disposition |
|---|---|---|---|
| GP-1 | **16 engines** (see §8) | 16 | 12 in Class A/B (declarable) · 4 elsewhere |
| GP-2 | 3 engines | `rib-gate`, `urrc-gate`, `uar-gate` | 2 declarable; **`uar-gate` is string-blocked** |
| GP-3 | 8+ targets | 10 Class C targets | **None declarable** — all governed gaps |
| GP-4 | 3 engines | `ucl-gate`, `ufep-gate`, `uis-gate` | All Class A — all declarable |
| GP-10 | 1 engine | `aee-gate` | Class A — declarable |

**D-6.5.** GP-3's entire population falls in Class C. Every GP-3 target is a governed gap
candidate. GP-3 therefore cannot be closed by declaration under any disposition short of
authorizing 10 new declaration instances plus guards.

**D-6.6.** `uar-gate` appears in both GP-2 (authorized code fix) and G-2 (string-blocked
declaration). Its code fix can proceed; its mode declaration cannot. It is the clearest single
case of a gate whose *behaviour* is remediable while its *declaration* is not.

### 6.5 Migration Sequencing Constraint

The GP-4 fix changes `ucl-gate` and `ufep-gate` behaviour (wiring or removing `--render`).
Both are Class A and both are in the authorized 4. **Their mode measurement must follow their
GP-4 fix**, or the declaration will describe pre-fix behaviour. Carried from CIEP v2 §3
Phase 3; restated here because it is a disposition-relevant ordering constraint, not merely an
execution detail.

---

## 7. Question 7 — Revised GP-11 Acceptance Criteria

### 7.1 Basis

Rebase §6.1 established four defects; ownership resolution D-7.1 added a fifth (GP-11 presumes
a uniform ownership model). This package adds a sixth.

**D-7.1 — sixth defect: GP-11 presumes enforcement reachability it does not measure.**
Its criterion counts *declared* modes. It does not require that anything *read* the
declaration. Under the original criterion, declaring a mode for a guardless gate would count
toward closure while remaining unverifiable — reproducing GP-5. A coverage criterion that
credits unenforceable declarations is measuring the wrong thing.

### 7.2 Revised GP-11 — Final Form

| Finding | Statement at HEAD `1f869865` | Acceptance Criterion | Reachable |
|---|---|---|---|
| **GP-11a** | `*-gate` plane: mode declared for **2 of 45**. Extension applicable to **22**; not applicable to **23**. Enforcement reachable for **23** engines, of which 1 is structurally blocked. | (i) Every extension-applicable target (22) carries a measured `gate_mode` in its canonical owning surface; (ii) every non-applicable target (23) is a **governed gap** with named owner, reason group, and escalation path; (iii) `22 + 23 = 45` with no target unclassified and none fabricated. | **YES** — after O-3 and a Class C/D disposition |
| **GP-11b** | `*-self` plane: 26 guard families read-only by construction, undeclared. | Each guard family declared read-only **or** registered as a governed gap. GATE-PURITY §2.2 already establishes read-only by construction; no behavioural change required. | **YES** |

### 7.3 Acceptance Criteria — Explicit

| # | Criterion | Test |
|---|---|---|
| **A-1** | Declared count = extension-applicable count | 22 of 22 |
| **A-2** | Every declared mode is within the ratified vocabulary | `OBSERVE` · `PRODUCER` · `EXECUTION` · `OBSERVE_WITH_DECLARED_AUDIT_EMISSION` |
| **A-3** | Every declared mode is **enforcement-reachable** | The owning engine carries `--check-declaration` — satisfied for all 22 by construction |
| **A-4** | Every PRODUCER names a replay path tested in both directions | Not inferred from the registry's `deterministic` field |
| **A-5** | Every non-applicable target is a governed gap with owner + reason + escalation | 23 of 23 |
| **A-6** | Declared + gap = 45, no overlap, no omission | Sum test |
| **A-7** | No count derived from uncommitted work | Re-measured against HEAD |

**A-3 is new** and is the direct consequence of D-7.1. It costs nothing to satisfy — the
applicable set and the reachable set are identical (§4.3) — but it forecloses the failure mode
of crediting unverifiable declarations.

### 7.4 State Under Current Authorization

| Finding | After authorized H-06 | Terminal |
|---|---|---|
| GP-11a | **OPEN (residual — scope-bounded)** — 4 declared, 41 requiring disposition | CLOSED after O-3 + Class C/D disposition |
| GP-11b | **OPEN (residual)** — outside authorized scope | CLOSED when 26 families declared or registered |

GP-11 must not be marked CLOSED. Confirms rebase D-5.2 and ownership-resolution D-7.2.

---

## 8. Question 8 — Revised Foundation Freeze Gate-Purity Criteria

### 8.1 Final Form

Carries F-1 through F-5 from the ownership-resolution determination; adds F-6.

| # | Condition | Test | State after authorized H-06 |
|---|---|---|---|
| **F-1** | Mutation boundaries declared **or explicitly owned as absent**, population stated | declared/45 + governed gaps/45 = 45 | **NO** — 4 declared, 41 undispositioned |
| **F-2** | Replay integrity proven for every declared PRODUCER | In-memory regeneration + byte compare, both directions. **Never inferred** from registry `deterministic` | Reachable for ≤4 |
| **F-3** | Evidence chain trustworthy over the declared set, **remainder reported** | Per-surface trust + explicit undeclared count | Reachable, 41 reported |
| **F-4** | No gate-purity claim rests on uncommitted work | Every count re-measured at HEAD | **FAIL** — GATE-PURITY §1 counts and 2 of its 4 declared modes are uncommitted |
| **F-5** | Every gate target has a resolved ownership disposition | 45 × one disposition; none unclassified | **NO** — 23 undispositioned |
| **F-6** **(new)** | Every declared mode is enforcement-reachable | Owning engine carries a guard that reads the declaration | Satisfied for all 4 authorized |

**D-8.1 — why F-6.** F-1 and F-5 count dispositions. Neither requires that a declaration be
*read* by anything. Without F-6, the freeze could be satisfied by declaring modes for gates
nothing verifies — the GP-5 pattern at scale. F-6 makes enforceability a freeze precondition
rather than an implementation detail.

### 8.2 Determination

**D-8.2. Gate purity cannot be closed by executing H-06 as authorized.** After every
authorized action: 4 of 45 declared; F-1, F-4, F-5 all NO.

**D-8.3. Closure is reachable, and cheaper than previously determined.** Under §9's
recommended disposition — 22 declared, 23 governed gaps — F-1, F-5 and F-6 all reach YES with
**zero new governance surface classes** and **zero engine modifications beyond authorized GP
fixes**. F-4 requires only re-measuring GATE-PURITY §1 against HEAD. F-2 and F-3 are bounded
by the declared set.

---

## 9. Owner Decision Fields

Five decisions. None is selected here.

### D-1 — Class B Extension (13 targets)

Extend `gate_mode` applicability to the 13 Class B surfaces (`rib-blueprint.json`,
`ucaf-authority.json`, `uei-evolution.json`, `umk-kernel.json`, and 9 more). All 13 carry a
`programme` object and a `--check-declaration` guard. Raises declarable coverage from 9 to 22.

```
[ ] AUTHORIZED — Class B surfaces are within gate_mode scope
[ ] NOT AUTHORIZED — Class B remains outside scope (declarable coverage stays at 9)
```

**Recommendation: AUTHORIZE.** These are the same kind of surface as Class A, differing only
in filename. Both applicability tests and the enforcement test are satisfied. Excluding them
leaves 13 gates undeclared for a naming reason alone.

### D-2 — Class A Remainder (5 targets)

Extend to `acee`, `aee`, `baseline`, `rfp`, `uis` declarations — currently unnamed by IAR §1.1.

```
[ ] AUTHORIZED
[ ] NOT AUTHORIZED
```

**Recommendation: AUTHORIZE.** `aee` and `uis` are the GP-10 and GP-4 target programmes. H-06
already authorizes modifying their engines; leaving their declarations unauthorized closes the
behaviour and leaves the declaration open.

### D-3 — Class C Disposition (11 targets)

```
[ ] GOVERNED GAP — register all 11 with owner, reason group, escalation path. Creates nothing.
[ ] INSTANTIATE — authorize creation of declaration instances in existing 00-MASTER homes
                  (requires guards to read them: engine modification, separate authorization)
[ ] MIXED — instantiate for the 6 registered producers; governed gap for the remainder
```

**Recommendation: GOVERNED GAP.** No Class C engine except `uar-gate` carries a guard, so a
declaration there would be unverifiable. Instantiation without guards produces 10 unenforced
claims.

### D-4 — Class D Disposition (12 targets)

```
[ ] EXPLICIT SCOPED EXCLUSION + governed gap — Class D is outside the programme
    declaration model; modes governed at pipeline level. Creates no surface.
[ ] NEW PER-MODULE DECLARATION MODEL for platform/* and intelligence/*  (new surface class)
```

**Recommendation: EXPLICIT SCOPED EXCLUSION.** No Class D target has a `programme` object or a
guard. `cmg-gate` and `rpi-gate` already declare modes in header/comment form — their gap is
machine-readability, which a scoped exclusion records honestly.

### D-5 — Acceptance Criteria (O-7)

```
[ ] ACCEPTED — GP-11a/GP-11b split (§7.2), criteria A-1..A-7 (§7.3),
               Freeze conditions F-1..F-6 (§8.1), GP-11 terminating OPEN (residual)
[ ] NOT ACCEPTED
```

**Signed By:** ________________   **Date:** ________________

### 9.1 Coverage Outcome Per Combination

| D-1 | D-2 | D-3 | D-4 | Declared | Governed gaps | F-1/F-5 |
|:-:|:-:|:-:|:-:|--:|--:|---|
| no | no | gap | excl | **4** | 41 | NO — 41 undeclared, dispositioned |
| yes | no | gap | excl | 17 | 28 | **YES** — all 45 dispositioned |
| yes | yes | gap | excl | **22** | 23 | **YES** — recommended |
| yes | yes | inst | excl | 32 | 13 | YES — requires guard authorization |

**D-9.1.** F-1 and F-5 reach YES in every row where D-3 and D-4 are dispositioned — because a
governed gap is a valid disposition. **The binding constraint is dispositioning all 45, not
declaring all 45.**

---

## 10. New Finding — GP-1 Population Is 16, Not 15

GATE-PURITY's findings register states GP-1 affects **15 engines**. Measured:

| Source | Count |
|---|--:|
| Rows in the GP-1 "same shape, same conclusion" table | **15** |
| `UCL-000001`, documented separately at line 101 as "Canonical, fully verified example" | **1** |
| **Total GP-1 engines** | **16** |

`ucl_engine.py` does not appear in the 15-row table — verified by direct search. Its GP-1
character is confirmed at HEAD by direct read:

```
00-MASTER/UCL-000001/ucl_engine.py:3030   written = write_registers(model)      ← unconditional
00-MASTER/UCL-000001/ucl_engine.py:3058   if args.gate and model["gate"] != "OPEN": return 1
                                                                                ← verdict AFTER write
```

**D-10.1.** GP-1's population is **16 engines**. The register undercounts by one because the
canonical example was documented outside the table. This does not change any H-06 authorized
action — GP-1 remediation is not in scope — but it must be corrected when
`GATE-PURITY-DETERMINATION.md` is updated at Task-010, alongside the §1 plane counts (rebase
R-7). Recorded here, not corrected: this package modifies no file.

---

## 11. Package Summary

| Q | Question | Answer |
|---|---|---|
| 1 | Complete list of 45 baseline gate targets | §2 — all 45 enumerated with 9 attributes each |
| 2 | Ownership class for each | **A 9 · B 13 · C 11 · D 12** |
| 3 | Canonical owning surface | §2 — Class A `*-declaration.json` · Class B `<prefix>-<domain>.json` · Class C absent (1 string) · Class D absent or differently purposed |
| 4 | `gate_mode` extension applicable | **22 APPLICABLE**, 23 not. Three-part test T-1 surface · T-2 `programme` object · **T-3 enforcement-reachable** (new). Applicable set and guard set are **identical** — 22 of 22. |
| 5 | Governed gap candidates | **23**, in four reason groups: G-1 no surface (10) · G-2 string-typed (1) · G-3 wrong-purpose surface (7) · G-4 no surface, no home (5) |
| 6 | Migration impact | Enforcement touches **23 engines**, 22 additively remediable, **`uar-gate` structurally blocked**. `verify.sh` exposure **1 of 45**. CI exposure **29 of 45**, with **18 guarded-and-CI-referenced** — **CI is the risk surface, not `verify.sh`**. GP-3's entire population is Class C. |
| 7 | Revised GP-11 acceptance criteria | Split GP-11a / GP-11b; criteria A-1..A-7 with **A-3 enforcement-reachability** new. Sixth defect identified: GP-11 credits declarations nothing reads. Both terminate OPEN (residual). |
| 8 | Revised Freeze gate-purity criteria | F-1..F-6, with **F-6 enforcement-reachability** new. Gate purity NOT closable under authorized scope; closure reachable with zero new surfaces under the recommended disposition. |

### 11.1 The Package In One Paragraph

Forty-five gate targets. Twenty-two have an owning surface that can carry a `gate_mode` and an
engine guard that would read it — and these two sets are **exactly identical**, which is the
strongest evidence in this package that the ownership model should follow the boundary the
repository already draws. Twenty-three cannot be declared honestly and should be recorded as
governed gaps with named owners. Four declarations are authorized today. Authorizing Class B
and the Class A remainder raises that to twenty-two at no constitutional cost; dispositioning
the remaining twenty-three as governed gaps completes the model without creating a single new
surface. Gate purity does not close, but for the first time it becomes reachable.

---

*This document is a decision preparation artifact. It presents the complete ownership register
and the decision fields required to finalise the H-06 ownership model. It authorizes nothing,
selects nothing, creates nothing, and closes nothing. No declaration was modified, no
`gate_mode` added, no engine modified, no registry created or altered, no implementation
executed. Every figure was measured read-only against HEAD `1f869865`.*

---

H-06 ownership disposition package complete.
No implementation authorized.
No repository mutation performed.
