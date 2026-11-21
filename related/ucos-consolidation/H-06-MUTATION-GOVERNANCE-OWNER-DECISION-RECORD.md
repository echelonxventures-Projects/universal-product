# H-06 MUTATION GOVERNANCE OWNER DECISION RECORD

| Field | Value |
|---|---|
| **ID** | H-06 |
| **Registered as** | CR-09 in `ASSESSMENT-CONFLICT-REGISTER.md` |
| **Authority** | OWNER DECISION RECORDED. RATIFICATION PENDING. No implementation authorized. |
| **Phase** | Foundation Closure — Mutation Governance Boundary Resolution |
| **Baseline** | HEAD `1f869865` · branch `integration/recovery-001` |
| **Depends on** | `GATE-PURITY-DETERMINATION.md` · `H-06-MUTATION-GOVERNANCE-DECISION-PACKAGE.md` |
| **Blocks** | Foundation Freeze eligibility (mutation-boundary dimension) |
| **Status** | OPTION B SELECTED — AWAITING RATIFICATION |

---

## 1. Decision Context

### Why H-06 exists

`mutation-governance-boundary.json` names `UCCEP-000000`, `UCOS-RIB-001`, and `UCOS-AEE-001` as
**gates** — governing authorities. Measured behaviour contradicts this: `uccep --gate` wrote 47
tracked files across 4 programme homes; `ufep/urat/utce --gate` wrote 5 each; `ucaf --gate` wrote
10. The label "gate" implies observation; the behaviour is production. Neither label nor behaviour
is wrong in isolation; the problem is that they have never been reconciled into a declared policy.

CR-09 registered this as a human decision because the reconciliation is a constitutional policy
choice, not a measurement gap. Two valid positions exist:

- Require that the word "gate" always mean "write-free observation" and rename/split the
  writing entry points.
- Accept that some gate paths are producers by design, declare them explicitly, and enforce the
  declaration.

No evidence collected during Gate Purity assessment can choose between these. The choice belongs
to the mutation-governance owner.

### Relationship to GP-1 through GP-11

H-06 is the root policy question that makes GP-1 through GP-11 remediable. The findings are:

| Finding | Relationship to H-06 |
|---|---|
| GP-1 (15 engines write unconditionally) | Under Option A: code change required. Under Option B: reclassification as PRODUCER, if replay enforced. |
| GP-2 (write before gate branch, 3 engines) | Defect under either option; order must be corrected. |
| GP-3 (8 replay targets write before comparing) | Defect under either option; replay contract required. |
| GP-4 (3 dead `--render` flags) | Defect under either option; flags must be wired or removed. |
| GP-5 (audit write on labelled read-only stage) | Mode must be corrected to `OBSERVE_WITH_DECLARED_AUDIT_EMISSION` under either option. |
| GP-6 (closure_engine PRODUCER boundary) | Resolved as PRODUCER under either option; stage 1b collision risk unverified. |
| GP-7 (CI reverts mutation) | Option A: workaround becomes unnecessary. Option B: workaround remains until write order is correct. |
| GP-8 (misleading self-guard) | Option A: self-guard becomes accurate. Option B: guard label must be corrected. |
| GP-9 (undeclared gitignored writes) | Requires `OBSERVE_WITH_DECLARED_AUDIT_EMISSION` classification under either option. |
| GP-10 (aee-observe calls emit unconditionally) | Code fix required under either option; label is false regardless. |
| GP-11 (4 of 46 gates declare mode) | The structural finding H-06 directly resolves; mode vocabulary must be ratified first. |

### Why Foundation Freeze depends on this decision

Foundation Freeze requires three conditions on the gate-purity dimension (assessed as of baseline
`1f869865`):

1. Mutation boundaries declared — **NO** (42/46 gates undeclared)
2. Replay integrity proven — **NO** (8 targets write before compare; 3 dead replay flags)
3. Evidence chain trustworthy — **PARTIAL** (4 confirmed-observe gates trustworthy; remainder not)

None of these three conditions can be satisfied without first knowing what a "declared mode" means
— that is precisely what H-06 must establish. Implementation of mode declarations is not
authorized until the policy exists.

---

## 2. Current Constitutional Reality

### What exists

**`00-BOOK/DATA/mutation-governance-boundary.json`**
Defines five repository-level mutation classes (`CONSTITUTIONAL_TRUTH`, `SOURCE`,
`GENERATED_ARTIFACT`, `EXCLUSION`, `REPOSITORY_STATE`), each with a governing authority chain.
Enforced by `test_mutation_governance_boundary.py`. Invariants include: every class has exactly
one authority; no class is ungoverned; every named authority resolves to an existing
implementation. This surface is complete and tested.

**`*-declaration.json` files (11 programmes)**
Each carries a `forbidden_write_prefixes` array: a write-scope boundary declaring what the
programme may not write. This answers *"what is outside this programme's write authority?"*
It does not answer *"does this programme's gate path write, and was that intended?"*

**No declaration carries a `gate_mode`, `execution_mode`, or `mode` field.**
Verified by survey of all 11 declaration files. The mode dimension is absent from the current
schema across the entire surface.

### What this means

This is an **incomplete governance declaration problem, not missing architecture.**

- The ownership model exists and is tested.
- The write-scope boundary model exists per programme.
- The mutation class model exists at repository level.
- The missing dimension is: *declared execution intent per gate entry point.*

The gap is one additive field on an existing surface. It cannot be filled without first deciding
what values that field may take — which is H-06.

---

## 3. Decision Options

### Option A — Pure Observation Gate Model

**Definition:** Every entry point labelled or named as a `*-gate` target is by constitutional
definition a write-free observation path. Mutation of any kind — tracked files, gitignored files,
audit logs — requires a separate, explicitly named and labelled entry point (`*-render`,
`*-run`, `*-produce`, or equivalent). The word "gate" in UCOS means and can only mean:
measurement without mutation.

**Required invariants under Option A:**

1. Every `*-gate` Makefile target and every CI workflow step labelled as a gate exits with zero
   filesystem writes to any path.
2. Every `*-replay` target regenerates in memory and compares committed bytes; it never writes
   first.
3. Every `*-render` / `*-run` target is the sole write path for its programme and is explicitly
   separated from the gate target by flag, subcommand, or distinct Make target.
4. No flag declared in a parser is unread (closes GP-4).
5. Always-on audit writes are labelled `OBSERVE_WITH_DECLARED_AUDIT_EMISSION` and listed as
   exceptions in the programme declaration.

**Benefits:**

- Observation is unconditionally safe; running any gate cannot alter Repository Truth.
- Evidence produced by a gate is trustworthy by construction — the measuring path cannot
  have altered what it measured.
- CI requires no workarounds (GP-7 resolved by policy).
- Replay integrity is enforced by the gate/render separation.
- Naming contract is universally enforceable: `*-gate` = measure; `*-render` = generate.
- `aee-observe` label becomes accurate without ambiguity.

**Risks:**

- Significant code change scope: ≥18 engines must separate their write from their gate verdict.
- Derived truth in CI never updates unless a `*-render` step is explicitly added to each
  affected workflow.
- Bootstrap ordering in `verify.sh` stage 1b must be explicitly labelled as a generation step
  separate from any gate that follows.
- GP-10 requires a code change regardless: `aee_engine.py` must suppress `emit()` on
  `--tier observe`.

**Migration impact:**

- Code changes required in ≥18 engines before mode declarations can be made truthful.
- CI workflow changes required in ≥15 workflows.
- Implementation cannot begin until this decision is recorded and implementation is
  separately authorized.
- During the migration window, gates remain in violation; a temporary grandfathering decision
  may be required.

---

### Option B — Explicit Multi-Mode Gate Model

**Definition:** Gate entry points may be classified as OBSERVE, PRODUCER, or EXECUTION when
explicitly declared in the programme's `*-declaration.json`. Undeclared mutation remains the
defect class and is prohibited. The word "gate" in UCOS names the primary entry point for a
programme; its mode is a declared property, not implied by its name.

**Required invariants under Option B:**

1. Every programme declaration carries a `gate_mode` field with exactly one of: `OBSERVE`,
   `PRODUCER`, `EXECUTION`.
2. OBSERVE declarations: no write on any path reachable from the gate entry point.
3. PRODUCER declarations: outputs are registered in `generated-artifact-registry.json` under
   the programme's producer home; the engine is deterministic; a replay path (regenerate
   in memory, compare bytes, no write) exists and is named in the declaration.
4. EXECUTION declarations: mutation class resolves to a named authority in
   `mutation-governance-boundary.json`; an explicit flag or subcommand is required to trigger
   the write; an audit trail exists.
5. No declaration may carry `gate_mode: PRODUCER` or `gate_mode: EXECUTION` without a
   corresponding entry in `generated-artifact-registry.json` or `mutation-governance-boundary.json`
   respectively.
6. Always-on audit writes to gitignored paths require an explicit `audit_emission` sub-field
   in the declaration (closes GP-5 and GP-9 class).

**Benefits:**

- Truthful to the current design intent of engines that were built as generators.
- Lower immediate implementation cost: declaration change is additive; code structure
  need not change for PRODUCER engines (though replay contract still requires a path).
- `generated-artifact-registry.json` and `mutation-governance-boundary.json` are reused
  without duplication — PRODUCER mode points into the existing generated-artifact surface;
  EXECUTION mode points into the existing mutation-class surface.
- `baseline-gate.yml` pattern (gate writes, then explicit replay step compares) is
  formalised as the reference implementation rather than eliminated.
- No new registry or authority surface is required.

**Risks:**

- Evidence trustworthiness ceiling is lower for PRODUCER gates unless replay integrity is
  strictly enforced as a co-obligation of PRODUCER classification. If replay contracts are
  not enforced simultaneously, Option B formalises the current defect rather than closing it.
- Mode inflation: programmes may claim PRODUCER to avoid write discipline. Decision criteria
  must define what qualifies.
- `aee-observe` label remains false without a code fix even under Option B — the mode
  classification addresses the gate target, not the observe target. GP-10 is a labelling
  problem that exists under either option.
- Trust model is more complex: a PRODUCER gate simultaneously measures and alters. Consumers
  of its evidence must know this.
- GP-2 (write before gate branch) is a structural defect — write order must be corrected
  regardless of mode classification, because a gate that writes before it decides cannot
  report a pre-write verdict.

**Migration impact:**

- Mode field added to existing `*-declaration.json` files: additive, no schema breakage.
- Replay contract paths must be implemented or named for each PRODUCER programme.
- Code change still required for GP-2 engines (write-before-gate-branch) and GP-10
  (`aee-observe`).
- Lower total code-change count than Option A, but replay enforcement is a hard dependency
  that must be scheduled explicitly.

---

## 4. Proposed Mode Vocabulary

*Presented as decision material. Not ratified. Subject to owner revision.*

### OBSERVE

**Definition:** The gate entry point measures, evaluates, and reports. It performs no write to
any filesystem path — tracked or untracked — except through an explicitly declared audit
emission. The gate is hermetic and deterministic: the same repository state produces the
same output on every invocation.

**Required properties:**

| Property | Requirement |
|---|---|
| Tracked file writes | ZERO |
| Gitignored file writes | ZERO unless declared as `audit_emission` |
| Determinism | REQUIRED — same inputs → byte-identical output |
| Hermeticity | REQUIRED — no clock, no network, no external state |
| Evidence quality | HIGHEST — measuring path cannot alter measured state |
| Replay contract | Not applicable — no output to compare |

**Existing confirmed examples:** CMG (`cmg-gate.sh`), UGA (`uga_engine.py gate`),
UAUE `--gate`, UAUE `--replay`.

---

### PRODUCER

**Definition:** The gate entry point creates deterministic derived artifacts as its declared
purpose. The write is the declared output, not a side-effect of measurement. The output is
reproducible: given the same repository state, re-running the engine produces byte-identical
artifacts.

**Required properties:**

| Property | Requirement |
|---|---|
| Output registration | REQUIRED — outputs listed in `generated-artifact-registry.json` |
| Determinism | REQUIRED — byte-identical output on identical input state |
| Replay path | REQUIRED — a separate path that regenerates in memory and compares committed bytes without writing first |
| Write scope | Constrained by `forbidden_write_prefixes` + declared output scope |
| Evidence quality | MEDIUM — evidence is the artifact produced; trustworthy only if determinism and replay are verified |
| Mutation class | `GENERATED_ARTIFACT` in `mutation-governance-boundary.json` |

**Existing confirmed examples (compliant shape):** `uga_engine.py run`, `make uaue-render`,
`register.sh --guard` (for generated-artifact outputs), `closure_engine.py` (via
`generate-prerequisites.sh`).

---

### EXECUTION

**Definition:** The gate entry point performs a controlled, authorized state transition that is
not re-derivable on demand. The mutation is an act of governance — registration, certification,
population amendment — and requires explicit invocation authority.

**Required properties:**

| Property | Requirement |
|---|---|
| Invocation gate | REQUIRED — explicit flag, subcommand, or emission-authority pattern |
| Mutation class | REQUIRED — resolves to a named authority in `mutation-governance-boundary.json` |
| Audit trail | REQUIRED — each invocation is recorded |
| Determinism | NOT REQUIRED — execution is an act, not a derivation |
| Replay | NOT APPLICABLE — the act is intentional and non-reproducible by design |
| Evidence quality | AUTHORITATIVE — the execution record is the evidence |

**Existing confirmed examples:** `register.sh --guard` (for CONSTITUTIONAL_TRUTH mutation),
`uga_engine.py run` (mints identity — GENERATED_ARTIFACT class), emission-authority pattern
in `uccep_engine.py` (`emission_authority(...)` + `"OBSERVATION ONLY — emission withheld"`).

---

### OBSERVE_WITH_DECLARED_AUDIT_EMISSION *(sub-classification)*

**Definition:** An OBSERVE path that performs an always-on, append-only write to a declared,
gitignored audit target. The write is a governance obligation, not a mutation of Repository
Truth. The label must accurately reflect this.

**Applies to:** `ukb enforce --pre` (GP-5), UCCEP evidence logs (GP-9 class),
`determinism.yml` → `determinism-evidence/` (GP-9 class).

---

## 5. Decision Constraints

The owner must apply the following non-negotiable principles to any decision:

**Knowledge Once Principle:** The mode declaration belongs in one place — the programme's
`*-declaration.json`. It must not be duplicated in `mutation-governance-boundary.json`
(repository-level classes), `generated-artifact-registry.json` (artifact-level outputs),
or a new surface.

**Canonical Ownership Principle:** `mutation-governance-boundary.json` owns mutation class
governance. `generated-artifact-registry.json` owns generated artifact registration.
Per-programme declarations own per-programme mode. These three surfaces must remain
non-overlapping in their authority claims.

**Evidence before conclusion:** No mode may be declared for an engine until its actual
behaviour has been measured. Declaration of a mode that does not match behaviour is a
false declaration.

**Observation before mutation:** During the transition period — between H-06 decision and
completion of mode declarations — no engine may be assumed to be safe to run observationally.
GP-1 through GP-10 findings remain active until remediation is authorized and completed.

**Explicit authority before change:** Implementation of mode declarations requires a separate
implementation authorization after this decision is recorded. The decision record is not itself
implementation authorization.

**No duplicate governance surfaces:** The decision must not create a mode registry, a mutation
registry, or any surface that duplicates the authority already held by the three existing
surfaces named above.

---

## 6. Required Future Closure Sequence

```
H-06 Owner Decision recorded
        ↓
Mode vocabulary ratified (OBSERVE / PRODUCER / EXECUTION /
OBSERVE_WITH_DECLARED_AUDIT_EMISSION)
        ↓
Declaration schema extension authorized
(additive `gate_mode` field on *-declaration.json programme block)
        ↓
Implementation authorized for mode declaration additions
        ↓
Per-programme declarations updated with verified mode
(measured behaviour → declared mode, evidence-first)
        ↓
Replay contracts implemented for PRODUCER declarations
(separate regenerate-in-memory + byte-compare path per programme)
        ↓
GP-2 write-order defects corrected (3 engines)
        ↓
GP-4 dead flags wired or removed (3 engines)
        ↓
GP-10 aee-observe emit() suppressed on observe tier
        ↓
GP-5 verify.sh stage 4 label corrected to
OBSERVE_WITH_DECLARED_AUDIT_EMISSION
        ↓
Gate purity findings GP-1 through GP-11 assessed as CLOSED
        ↓
Foundation Freeze gate-purity conditions re-assessed:
  (1) Mutation boundaries declared        → YES
  (2) Replay integrity proven             → YES
  (3) Evidence chain trustworthy          → YES (all declared surfaces)
        ↓
Foundation Freeze eligibility re-assessed for remaining blockers
(H-01..H-05, R-B1..R-B5)
```

No step in this sequence may be skipped. Each arrow is a dependency, not a preference.

---

## 7. Owner Decision Record

### Decision Authority

Mutation Governance Owner.

### Selected Governance Option

**Option B — Explicit Multi-Mode Gate Model**

### Decision Rationale

UCOS Ω∞ requires explicit governance of multiple legitimate execution behaviours:

- OBSERVE — measurement without mutation
- PRODUCER — deterministic generation of governed artifacts
- EXECUTION — authorized state transition

Option B preserves existing canonical ownership boundaries:

- `mutation-governance-boundary.json` owns mutation authority.
- `generated-artifact-registry.json` owns generated artifact registration.
- `*-declaration.json` owns programme-level execution mode declaration.

No new registry, authority surface, or duplicate governance model is introduced.

### Decision Impact

This decision:

- resolves the H-06 constitutional policy question;
- enables ratification validation;
- defines the implementation boundary;
- does not close GP-1 through GP-11 automatically.

### Implementation Authorization

NOT AUTHORIZED.

A separate implementation authorization step is required after ratification validation.

### Decision Recorded By

Bipin Kumar

### Date

2026-08-16

---

## 7. Foundation Freeze Impact

### Before H-06 decision

| Freeze Condition | Status | Root |
|---|---|---|
| Mutation boundaries declared | **NO** | GP-11: 42/46 undeclared |
| Replay integrity proven | **NO** | GP-3, GP-4 |
| Evidence chain trustworthy | **PARTIAL** | Stale projections; GP-10 |
| Implementation of gate mode authorized | **NO** | No policy exists to implement |

Gate purity is a **blocking** dimension of Foundation Freeze. It cannot be assessed as
satisfied while the mode vocabulary is unratified.

### After H-06 decision (before implementation)

| Change | Status |
|---|---|
| Policy boundary resolved | YES — owner has declared the constitutional model |
| Implementation scope defined | YES — affected engines and declarations are enumerable |
| Any gate purity finding closed | NO — declaration changes and code fixes are still unauthorized |
| Freeze conditions satisfied | NO — unchanged until implementation is authorized and completed |

H-06 decision alone does not satisfy any freeze condition. It enables the implementation
authorization that would permit satisfaction.

### After H-06 decision + implementation + validation

| Freeze Condition | Expected Status |
|---|---|
| Mutation boundaries declared | YES — if all 46 gates carry a verified mode declaration |
| Replay integrity proven | YES — if all PRODUCER gates have a tested replay path |
| Evidence chain trustworthy | YES — for all declared surfaces; stale projections corrected by PRODUCER runs |

### Remaining freeze blockers after gate purity closure

Gate purity closure satisfies one dimension of Foundation Freeze. The following remain in
their currently registered state and are outside the scope of H-06:

- **H-01 through H-05** — registered in `CANONICAL-AUTHORITY-DETERMINATION.md §6.2`
- **R-B1 through R-B4** — registered in `FINAL-FREEZE-READINESS-DETERMINATION.md §4.1`
- **R-B5** (CR-10) — 21 untracked working-tree entries requiring `git add` + registration
  or explicit exclusion
- Other open constitutional decisions recorded in `ASSESSMENT-CONFLICT-REGISTER.md`

These are independent of H-06 and must be addressed through their own decision sequences.

---

*This record contains the recorded mutation-governance owner decision. Option B has been
selected. Ratification validation is required before implementation authorization.
No implementation has been authorized. Any implementation activity requires a separate
constitutional authorization step after ratification.*
