# H-06 DECISION BOUNDARY VALIDATION

| Field | Value |
|---|---|
| **Authority** | NONE — SIMULATION ONLY |
| **Phase** | Foundation Closure — Mutation Governance Boundary Resolution |
| **Baseline** | HEAD `1f869865` · branch `integration/recovery-001` |
| **Input** | `H-06-MUTATION-GOVERNANCE-OWNER-DECISION-RECORD.md` · Gate Purity findings GP-1–GP-11 |

---

## 1. Is H-06 Correctly Scoped?

**Assessment: YES, with four embedded sub-decisions that require separation.**

The core question — "should `*-gate` entry points be constitutionally required to be write-free (Option A) or may they declare a mutation mode (Option B)?" — is the correct policy question. It is not conflating two unrelated questions. The distinction between a single-mode and a multi-mode model is a single constitutional rule that governs the entire gate surface. The question is correctly binary.

However, the decision record embeds four sub-decisions that could be decided independently of Option A/B and should be noted as such:

---

## 2. Required Inputs Available?

| Input | Available | Source |
|---|---|---|
| GP-1 through GP-11 findings | YES | `GATE-PURITY-DETERMINATION.md` |
| Mutation governance boundary | YES | `00-BOOK/DATA/mutation-governance-boundary.json` |
| Declaration file survey (11 files) | YES | Direct survey — all 11 files enumerated |
| Mode field absence confirmed | YES | Survey — `gate_mode`, `execution_mode`, `mode` all absent |
| Confirmed-observe reference implementations | YES | CMG, UGA, UAUE `--gate`, UAUE `--replay` |
| Generated-artifact-registry.json role | YES | 344 entries, 30 producer homes, `bootstrap_gaps: []` |
| Freeze condition current state | YES | Assessed: NO / NO / PARTIAL |
| Irreversible loss evidence | YES | `FINAL-FREEZE-ELIGIBILITY-DETERMINATION.md §1.1 F-A` |

**All required inputs are available for the owner to make the Option A/B decision.**

Two evidence gaps exist but do not block the decision — they block ratification:

- **R-1:** GP-6 stage 1b collision with `!`-negated tracked files — unverified.
- **R-2:** EXECUTION audit trail destination — unspecified.

---

## 3. Hidden Decisions Embedded in H-06

### Sub-decision S-1: Field name (`gate_mode` vs alternative)

**Classification: SUB-DECISION — separable.**

The decision record proposes `gate_mode` as the field name. This is a naming choice, not a policy choice. The Option A/B decision can be recorded without committing to a field name. Ratification of the vocabulary requires a field name; the owner decision does not.

**Disposition:** Separate into ratification phase. Owner decides Option A/B now; field name is ratified alongside the vocabulary.

---

### Sub-decision S-2: OBSERVE_WITH_DECLARED_AUDIT_EMISSION classification

**Classification: CONSEQUENCE, not a separate decision.**

`OBSERVE_WITH_DECLARED_AUDIT_EMISSION` is a sub-classification of OBSERVE — it applies under either Option A or Option B for paths that are structurally read-only but carry always-on audit writes (GP-5, GP-9 class). It does not affect the Option A/B question. Whether the owner selects A or B, this sub-classification exists and is required.

**Disposition:** Not a separate decision. It is a definitional consequence of the mode vocabulary, applicable under either option. Include in ratification, not in the Option A/B decision.

---

### Sub-decision S-3: EXECUTION audit trail destination (R-2)

**Classification: SUB-DECISION — separable, blocks ratification not decision.**

The EXECUTION mode requires an audit trail but the record does not specify where it is recorded. The owner can select Option B without resolving this — but EXECUTION mode cannot be declared on any programme until R-2 is resolved. If the owner selects Option A, R-2 is moot (EXECUTION mode does not exist as a gate mode under Option A; it exists only as a separate named entry point, and audit trail governance for that is outside H-06 scope).

**Disposition:** Separate into ratification phase, conditioned on Option B selection.

---

### Sub-decision S-4: Grandfathering policy during migration window

**Classification: SUB-DECISION — separable, required for implementation authorization.**

During the period between the owner's decision and completion of mode declarations, 42 gate entry points remain undeclared. The owner must decide whether:

- (a) Existing undeclared mutation is temporarily grandfathered (gates continue to pass CI despite no declared mode), or
- (b) Declaration is required before any gate passes the `--check-declaration` self-guard.

This is a migration governance question, not a mode policy question. It does not affect the Option A/B choice but must be decided before implementation authorization is granted.

**Disposition:** Separate into implementation authorization phase. Not part of the Option A/B decision.

---

## 4. Decisions Incorrectly Delegated to H-06

The following are **not** policy questions and should not be resolved by the H-06 owner decision:

### GP-2 write-order correction (3 engines)

**Classification: CODE DEFECT — not a policy question.**

`rib_engine.py`, `urrc_engine.py`, and `uar_engine.py` write before the gate branch. This is a structural ordering error: a gate that writes before it decides cannot report a pre-write verdict. This is wrong under either Option A or Option B. The owner's mode selection does not affect whether this must be fixed. It is a code change, not a declaration change.

**Disposition:** Remove from H-06 scope. Route to implementation authorization as a mandatory fix under either option.

---

### GP-10 aee-observe emit() suppression

**Classification: CODE DEFECT — not a policy question.**

`aee_engine.py` calls `emit()` unconditionally regardless of `--tier observe`. The Makefile labels `aee-observe` a "fast read-only pass." This label is false under either option. Fixing it requires suppressing `emit()` on the observe tier — a code change, not a mode declaration. The owner's decision does not resolve this.

**Disposition:** Remove from H-06 scope. Route to implementation authorization as a mandatory fix under either option.

---

### GP-6 stage 1b collision verification

**Classification: EVIDENCE GAP — not a policy question.**

Whether `closure_engine.emit()` output filenames collide with `.gitignore` `!`-negated tracked files is an empirical question answerable by read-only evidence collection. The owner cannot decide it; it must be measured. It does not affect the Option A/B policy choice.

**Disposition:** Remove from H-06 scope. Route to evidence collection (R-1) before ratification.

---

## 5. Decision Boundary Verdict

**PARTIALLY SCOPED**

The core Option A/B question is correctly identified and scoped. Four embedded sub-decisions (S-1 through S-4) and three incorrectly delegated items (GP-2, GP-10, GP-6) should be separated. The owner can record their Option A/B selection without resolving these — but they must be routed to the correct subsequent phase (ratification, implementation authorization, or evidence collection) before implementation can begin.

A clean H-06 decision record states the Option A/B choice and nothing more. All sub-decisions and code defects are downstream of that choice, not part of it.
