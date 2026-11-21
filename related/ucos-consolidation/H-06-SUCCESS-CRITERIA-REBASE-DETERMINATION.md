# H-06 SUCCESS CRITERIA REBASE DETERMINATION

| Field | Value |
|---|---|
| **ID** | H-06-SCRD |
| **Authority** | DETERMINATION ONLY. No implementation authorized. No policy selected. No surface created. |
| **Phase** | Foundation Closure — Gate Purity — Acceptance Criteria Rebase |
| **Baseline** | HEAD `1f869865` · branch `integration/recovery-001` · working tree DIRTY |
| **Rebases** | GATE-PURITY-DETERMINATION.md §1, §2.1, §2.3, D-3.5, GP-11, §6 |
| | H-06-IAR-AUTHORIZATION-MATRIX-CORRECTION.md §5 (supersedes its S-1..S-5) |
| | H-06-CONTROLLED-IMPLEMENTATION-EXECUTION-PLAN-v2.md §6 |
| **Reads** | H-06-R4-GRANDFATHERING-POLICY-DECISION-RECORD.md · H-06-DOCUMENT-CANONICALITY-CLEANUP-DETERMINATION.md |
| **Produced** | 2026-08-16 |
| **Status** | REBASE COMPLETE — GP-11 AND FREEZE CRITERIA BOTH REQUIRE MODIFICATION |

---

## 0. Headline

Every gate-population figure in the H-06 chain was measured against the **dirty working
tree**, not the authorized baseline. Proof: GATE-PURITY §1 reports 170 Makefile targets;
HEAD has **166**, and the working tree has **170** — the difference is exactly the four
uncommitted UAUE targets. The same offset explains the 46 gate targets (HEAD: 45), the 16
replay/render targets (HEAD: 14), and the 28 workflows (HEAD: 27).

The consequence compounds: **two of the four gates GATE-PURITY credits with a declared
mode are themselves uncommitted.** `engine/uaue/gate.py` is not in HEAD. At the authorized
baseline, the declared-mode count inside the `*-gate` plane is **2 of 45**, not 4 of 46.

Both GP-11's closure criteria and the Foundation Freeze gate-purity criteria require
modification. Neither is satisfiable as written — not because remediation is hard, but
because both are keyed to a population that does not exist at the baseline they cite.

One finding is resolved read-only in this determination: **GP-10 moves from APPARENT to
CONFIRMED** (§8).

---

## 1. Method

Every figure below was measured directly, twice — once against `HEAD:` via `git show`, once
against the working tree — so that baseline-dependent quantities are separated from
baseline-independent ones. Where the two differ, both are reported and the HEAD value
governs, because HEAD `1f869865` is the authorized baseline named in every H-06 document.

No file was modified. No declaration was written. No engine was read for the purpose of
changing it.

---

## 2. Question 1 — Correct Denominator of Gate Entry Points

### 2.1 The Question Is Plane-Scoped

"Gate entry point" is not one population. The repository exposes gate behaviour on six
distinct planes, and a single denominator is meaningful only once the plane is named.
GP-11 states "4 of 46 `*-gate` targets; 26 `*-self` guards read-only but undeclared" —
mixing two planes in one finding, which is part of why it cannot be closed cleanly.

### 2.2 Plane Measurements — HEAD vs Working Tree

| Plane | GATE-PURITY §1 | **HEAD (authoritative)** | Working tree | Command |
|---|---|---|---|---|
| Makefile targets, total unique | 170 | **166** | 170 | `grep -oE '^[a-zA-Z0-9][a-zA-Z0-9._-]*:' \| sort -u \| wc -l` |
| Makefile `*-gate` targets | 46 | **45** | 46 | `grep -cE '^[a-z0-9._-]+-gate:'` |
| Makefile `*-self` guard targets | 26 | **26** | 26 | `grep -cE '^[a-z0-9._-]+-self:'` |
| Makefile `*-replay` + `*-render` | 16 | **14** (14 replay + 0 render) | 16 | `grep -cE '^[a-z0-9._-]+-(replay\|render):'` |
| `verify.sh` `run_stage` invocations | 9 default + 1 opt-in | **9** | 11 | `grep -c '^run_stage'` |
| GitHub workflows | 28 | **27** | 28 | `git ls-tree --name-only HEAD .github/workflows/` |

### 2.3 GATE-PURITY §1 Is a Mixed-Baseline Measurement — Proven

The four Makefile-derived counts and the workflow count match the **working tree**. The
`verify.sh` stage count matches **HEAD**. The document therefore measured different planes
at different tree states while declaring a single baseline.

Proof by exact difference:

```
HEAD unique Makefile targets:     166
WORKTREE unique Makefile targets: 170
targets present only in worktree: uaue, uaue-gate, uaue-render, uaue-replay
```

166 + 4 = 170. The delta is precisely the uncommitted UAUE target family. The same delta
accounts for `*-gate` 45→46, `*-replay/render` 14→16, and workflows 27→28
(`uaue-gate.yml`, staged-added, not in HEAD).

**This is a measurement-provenance defect, not a counting error.** GATE-PURITY's own header
declares the working tree DIRTY and its authority as "DERIVED TRUTH … read from executing
code." It read the code that was present on disk. The defect is that its counts were then
inherited by the authorization chain as baseline facts.

### 2.4 The Numerator Is Also Baseline-Dependent

GATE-PURITY §2.1 credits four gates with a declared OBSERVE mode. Committed status of each:

| # | Gate credited as declared | Declaring artifact | In HEAD? |
|---|---|---|---|
| 1 | Meta-constitutional conformance | `00-CMG/tools/cmg-gate.sh` | **YES** |
| 2 | Universal object governance — `uga_engine.py gate` | `00-MASTER/UCOS-UGA-001/uga_engine.py` | **YES** |
| 3 | Autonomous universal evolution — `--gate` | `engine/uaue/gate.py` | **NO — uncommitted** |
| 4 | Evolution surface replay — `--replay` | `engine/uaue/gate.py` | **NO — uncommitted** |

Verified: `git cat-file -e HEAD:engine/uaue/gate.py` fails. **Half the declared-mode
numerator does not exist at the authorized baseline.**

Restricting to the `*-gate` target plane — the plane GP-11's denominator names — only two
of the credited gates are `*-gate` targets at all:

| Declared mode within the 45 `*-gate` targets at HEAD | Mode | Basis |
|---|---|---|
| `cmg-gate` | OBSERVE | script header lines 3–13; `--emit` opt-in only (GATE-PURITY §2.1) |
| `rpi-gate` | EXECUTION | Makefile comment declares emission to gitignored `.runtime/repository-intelligence/` (GATE-PURITY §2.3) |

`uga_engine.py gate` / `run` are **subcommands, not `*-gate` targets** — UGA has no
`uga-gate` Makefile target. `register.sh --guard` is a `verify.sh` stage, not a `*-gate`
target. `make uaue-render` is uncommitted.

**Determination D-1.1: within the `*-gate` plane at HEAD, the declared-mode count is 2 of
45.** GP-11's "4 of 46" overstates the numerator by counting two uncommitted declarations
and two entry points outside the plane, and overstates the denominator by one uncommitted
target.

### 2.5 Determination — Canonical Denominators

**D-1.2.** The canonical denominator for H-06 gate-mode coverage is **45** — the Makefile
`*-gate` targets at HEAD `1f869865`. This plane is chosen because it is the plane GP-11
names, it is enumerable and stable, and every `*-gate` target is a documented operator
entry point.

**D-1.3.** Gate purity as a *property* is not bounded by that plane. Any claim that gate
purity is closed must state its plane scope explicitly. The full surface at HEAD:

| Plane | Count | In H-06 authorized scope |
|---|---:|---|
| Makefile `*-gate` targets | **45** | Partially — 4 declarations authorized |
| Makefile `*-self` guards | 26 | No — GATE-PURITY §2.2 finds them read-only by construction, undeclared |
| Makefile `*-replay` targets | 14 | Partially — GP-4 affects 3 |
| `verify.sh` stages | 9 (+1 opt-in) | Partially — GP-5 affects stage 4 |
| GitHub workflows | 27 | No — §2.5 of GATE-PURITY: mutation profile inherited from the engine CLI |
| Engine subcommand gates outside `*-gate` | ≥2 (`uga gate`, `uga run`) | No |

**D-1.4.** Every occurrence of 46, 170, 16, and 28 in the H-06 chain is superseded by
§2.2. Any future coverage arithmetic that yields a denominator of 46 has silently adopted
uncommitted UAUE work as baseline.

---

## 3. Question 2 — Canonical Ownership Surface for Each Gate

### 3.1 Method

For each of the 45 `*-gate` targets at HEAD: resolve the invoked engine or module from the
Makefile recipe, resolve its `00-MASTER/<PROGRAMME>/` home, then enumerate every JSON in
that home that (a) parses, (b) carries a `programme` block, and (c) is **not** a registered
generated artifact in `00-BOOK/DATA/generated-artifact-registry.json`. Condition (c) is
essential: a generated artifact is derived truth and can never be an ownership surface.

### 3.2 Ownership Taxonomy — All 45 Gate Targets

| Class | Definition | Count |
|---|---|---:|
| **A** | Home contains a `*-declaration.json` with a `programme` object — the surface D-3.3 names | **9** |
| **B** | Home contains a non-generated JSON with a `programme` object under a **different** name | **13** |
| **C** | Home contains no non-generated JSON with a `programme` object — **no ownership surface exists** | **11** |
| **D** | No `00-MASTER/` home — `platform/`, `intelligence/`, `engine/`, or a shell script | **12** |
| | **Total** | **45** |

**Class A (9)** — `acee-gate`, `aee-gate`, `baseline-gate`, `rfp-gate`, `ucl-gate`,
`ufep-gate`, `uis-gate`, `urat-gate`, `utce-gate`.

**Class B (13)** — the canonical surface exists but is named by domain, not by `declaration`:

| Gate | Ownership surface | `programme` | `forbidden_write_prefixes` |
|---|---|---|---|
| `rib-gate` | `rib-blueprint.json` | object | yes |
| `ucaf-gate` | `ucaf-authority.json` | object | yes |
| `uaie-gate` | `uaie-architecture.json` | object | no |
| `uccep-gate` | `uccep-bindings.json` | object | yes |
| `urrc-gate` | `urrc-bindings.json` | object | yes |
| `uei-gate` | `uei-evolution.json` | object | yes |
| `uer-gate` | `uer-resilience.json` | object | — |
| `umk-gate` | `umk-kernel.json` | object | — |
| `uprf-gate` | `upf-provider.json` | object | — |
| `ucda-gate` | `ucda-decisions.json` | object | — |
| `mcos-gate` | `mcos-civilization.json` | object | — |
| `ucef-gate` | `ucef-framework.json` | object | — |
| `uaep-gate` | `uaep-platform.json` | object | — |

**Class C (11)** — `closure-gate`, `closure-phase2-gate`, `closure-phase3-gate`,
`closure009-gate`, `closure009-baseline-gate`, `corpus-gate`, `assimilate-gate`,
`roadmap-gate`, `lifecycle-closure-gate`, `final-closure-gate`, `uar-gate`.

`uar-gate` is in Class C for a distinct reason: `uar-analyses.json` exists and is
non-generated, but its `programme` value is a **JSON string**, so no field can be added
inside it.

**Class D (12)** — `cmg-gate` (`00-CMG/tools/cmg-gate.sh`), `selfaware-gate`
(`engine.knowledge.cli`), `rpi-gate`, `homing-gate`, `constitution-gate`,
`convergence-gate`, `freeze-gate`, `foundation-gate`, `uapf-gate` (all `platform.*`),
`research-gate`, `publication-gate`, `research-publication-gate` (`intelligence.*`;
the last is an aggregator with no engine of its own).

### 3.3 Two Declarations Own No Gate

Of the 11 `*-declaration.json` files, only 9 correspond to a `*-gate` target.
`uga-declaration.json` and `urr-declaration.json` have **no `*-gate` target** — UGA gates
through a subcommand, URR has no gate target at all. Both are therefore **outside the
45-target denominator entirely**, in addition to being structurally incapable of receiving
the field (AMC D-4, D-5).

**Consequence:** the two structurally blocked declarations were never in the coverage
denominator. Resolving owner decisions O-4 and O-5 would not increase `*-gate` coverage by
a single target. This materially reduces their priority.

### 3.4 Determination

**D-2.1.** The canonical ownership surface is **per-programme and heterogeneously named**.
D-3.3's premise — "Each programme already ships a `*-declaration.json`" — holds for **9 of
45** gate targets. It does not hold for 36.

**D-2.2.** For Class B, the ownership surface **exists and is structurally capable**; only
its name differs from the IAR's assumption. For Class C and D, **no ownership surface
exists** — coverage there is a creation problem, not a naming problem.

**D-2.3.** Class D gates fall outside the programme declaration model altogether. Nine
invoke `platform.*` or `intelligence.*` modules and one is a shell script. There is no
`00-MASTER` programme to own their mode. Extending `gate_mode` to them requires an
ownership model that does not currently exist — a governance design question, not an
implementation step.

---

## 4. Question 3 — Which Surfaces May Receive `gate_mode`

### 4.1 Permitted Now — Authorized and Structurally Capable

| Surface | Gate | Authority |
|---|---|---|
| `00-MASTER/UCL-000001/ucl-declaration.json` | `ucl-gate` | IAR §1.1 ∩ exists (AMC Tier A) |
| `00-MASTER/UCOS-UFEP-001/ufep-declaration.json` | `ufep-gate` | same |
| `00-MASTER/UCOS-URAT-001/urat-declaration.json` | `urat-gate` | same |
| `00-MASTER/UCOS-UTCE-001/utce-declaration.json` | `utce-gate` | same |

**4 surfaces. 4 of 45 gate targets = 8.9% coverage.** This is the whole of what H-06 may
write today.

### 4.2 Structurally Capable, Not Authorized

| Group | Surfaces | Gate targets reached if extended | Blocking decision |
|---|---|---|---|
| Class A remainder | `acee`, `aee`, `baseline`, `rfp`, `uis` declarations | +5 → 9 of 45 | O-3 |
| Class B | 13 domain-named surfaces (§3.2) | +13 → 22 of 45 | O-3 / O-6 |

`aee` and `uis` remain the sharpest inconsistency (AMC D-9): H-06 authorizes modifying
`aee_engine.py` and `uis_engine.py` but not declaring the modes of the programmes those
engines belong to.

**Maximum coverage reachable without creating any new file: 22 of 45 (48.9%).**

### 4.3 No Surface Exists — Creation Required, Not Authorized

Class C (11) and Class D (12) = **23 gate targets** have no surface capable of carrying a
`gate_mode`. Reaching them requires creating a governance surface, which is:

| Prohibition | Source |
|---|---|
| "Creation of any new governance surface or authority layer" | IADR §5 |
| "Creating any new governance file not listed in Phase outputs" | CIEP §4 |
| "Creating any new registry or authority surface" | CIEP §4 |
| Refusal of ITBP Task-008 §4's creation claim | AMC §4.6 |

**D-3.1: 23 of 45 gate targets cannot receive a `gate_mode` under any currently authorized
action.** Full coverage is not an execution problem. It is a governance design decision
that has not been made.

### 4.4 Forbidden Write Targets — Reaffirmed and Extended

| Surface | Reason |
|---|---|
| `rib.json`, `ucaf.json`, `uaie.json`, `urrc.json`, `uar.json`, `ucda.json`, `ucl.json`, `uis.json` | **Registered generated artifacts** — verified present in `generated-artifact-registry.json`. Derived truth. |
| `uga-declaration.json` | No `programme` block; insertion requires structural change (IADR §5) |
| `urr-declaration.json` | `programme` is a string; insertion impossible without restructure |
| `uar-analyses.json` | `programme` is a string; same |
| `00-BOOK/DATA/mutation-governance-boundary.json` | Authority chains — IAR §4, IADR §5 |
| Any Class C or D surface | Would constitute creation — §4.3 |

### 4.5 Adjacent Finding — Registry Coverage Gap

Three `<prefix>.json` gate outputs exist but are **not** registered as generated artifacts:

| Programme | Artifact | Registered |
|---|---|---|
| UCCEP-000000 | `uccep.json` | **NO** |
| UCOS-RFP-001 | `rfp.json` | **NO** |
| UAEP-000001 | `uaep.json` | **NO** |

Their siblings (`rib.json`, `ucaf.json`, `uaie.json`, `urrc.json`, `uar.json`,
`ucda.json`, `ucl.json`, `uis.json`) **are** registered. The registry is therefore
inconsistent about the same artifact class.

**This gap must not be closed under H-06.** IADR §5 forbids modifying
`generated-artifact-registry.json` "beyond what GP-2/GP-4 fixes strictly require," and
registering three artifacts is not required by either. Recorded as a gap for a separate
authority. It is noted here because a Phase 3 measurement of `uccep-gate`, `rfp-gate`, or
`uaep-gate` will observe writes to an unregistered artifact, and the correct response is to
record the anomaly — **not** to register it.

---

## 5. Question 4 — Governance Surfaces That Must Remain Unchanged

| # | Surface | Constraint | Basis |
|---|---|---|---|
| U-1 | `00-BOOK/DATA/mutation-governance-boundary.json` | No modification of authority chains or mutation classes | IAR §4; IADR §5; CIEP §4 |
| U-2 | `00-BOOK/DATA/generated-artifact-registry.json` | No modification beyond what GP-2/GP-4 strictly require. **Includes not closing the §4.5 gap.** | IADR §5 |
| U-3 | The 8 registered `<prefix>.json` artifacts | Derived truth; no `gate_mode`, no hand edit | §4.4 |
| U-4 | `00-MASTER/UCOS-UICM-000001/`, `00-MASTER/UCOS-UICO-000001/`, `engine/uicm/` | Standing constraint — untouched by H-06 | IADR §5; CIEP §4 |
| U-5 | All Class C and Class D homes | No surface may be created in them | §4.3 |
| U-6 | `uga-declaration.json`, `urr-declaration.json`, `uar-analyses.json` | No structural change to make them writable | §4.4; AMC D-4/D-5 |
| U-7 | UAUE / UAIE / UCKP / UGA / platform deltas in the working tree | H-06 holds no authority to commit or alter them | H-06-PIRSV §4.2 |
| U-8 | `H-06-MUTATION-GOVERNANCE-OWNER-DECISION-RECORD.md` | Canonical signed record; §7 numbering fix requires owner acknowledgement | DCCD R-3 |
| U-9 | Every `*-self` guard (26) | Read-only by construction; H-06 does not modify guard behaviour | GATE-PURITY §2.2 |
| U-10 | `H-06-CONTROLLED-IMPLEMENTATION-EXECUTION-PLAN.md` (v1) | Retained as superseded record; cited by ITBP and PIRSV | DCCD §4.4 |

### 5.1 Special Status — `GATE-PURITY-DETERMINATION.md`

`GATE-PURITY-DETERMINATION.md` declares itself **`CLASSIFICATION: EVIDENCE`** with
**"AUTHORITY: NONE — DERIVED TRUTH"**. It is the only surface H-06 is expected to *update*
(CIEP §6.4, ITBP Task-010). Two constraints follow from its own §4:

1. **No finding may be marked CLOSED without re-measurement** — D-3.6 refuses resolution
   "by assumption."
2. Its §1 plane counts must be **re-measured against HEAD** when updated, per §2.2 of this
   document. Updating findings while leaving mixed-baseline counts in place would propagate
   the defect.

---

## 6. Question 5 — Does GP-11 Closure Criteria Require Modification?

### 6.1 Determination: YES — MATERIALLY

GP-11 as written: *"Mode declared for only 4 of 46 `*-gate` targets; 26 `*-self` guards
read-only but undeclared."* Expected closure (CIEP §6.4, ITBP Task-010): *"CLOSED when
46/46 carry verified mode."*

Four independent defects:

| # | Defect | Evidence |
|---|---|---|
| 1 | **Denominator wrong.** 46 counts uncommitted `uaue-gate`. | §2.2 — HEAD is 45 |
| 2 | **Numerator wrong and inflated.** Of 4 credited, 2 are uncommitted and 2 are not `*-gate` targets. Within the plane at HEAD: **2**. | §2.4 |
| 3 | **Two planes conflated.** The finding names `*-gate` targets and `*-self` guards in one statement with one closure criterion; they have different populations (45 vs 26) and different remediation. | §2.1 |
| 4 | **Closure unreachable.** 23 of 45 targets have no surface that can carry the field; creation is forbidden. Max reachable without creation is 22 of 45; max authorized today is 4 of 45. | §4.3 |

Defect 4 alone is decisive: **no sequence of authorized actions makes GP-11's closure
criterion true.** A criterion that cannot be satisfied by permitted action is not a
criterion — it is an unfalsifiable claim of the exact kind GP-11 was raised to eliminate.

### 6.2 Rebased GP-11

**Split into two findings, each with an achievable criterion and a measured population.**

| Finding | Statement at HEAD `1f869865` | Closure Criterion | Reachable |
|---|---|---|---|
| **GP-11a** — `*-gate` plane | Mode declared for **2 of 45** `*-gate` targets. Ownership surface exists for 22; absent for 23. | Every `*-gate` target whose ownership surface **exists and is structurally capable** carries a measured `gate_mode`; every target without such a surface is registered as a named scope gap with an owner. | **YES** — 22 declarable + 23 registered = 45 accounted |
| **GP-11b** — `*-self` plane | 26 `*-self` guards are read-only by construction and undeclared. | Each `*-self` guard family is declared read-only, **or** registered as a named gap. No behavioural change required — GATE-PURITY §2.2 already establishes they are read-only by construction. | **YES** |

**D-5.1.** Under H-06 as currently authorized, GP-11a terminates **OPEN (residual —
scope-bounded)** at 4 of 45 declared, 41 registered as gap. It reaches CLOSED only after
owner decisions O-3 and O-6. GP-11b is untouched by H-06 authorized scope and terminates
**OPEN (residual)**.

**D-5.2.** GP-11 must not be marked CLOSED. Neither must it be marked closed "in
principle," "for the authorized scope," or with any qualifier that reads as closure in a
summary table. The honest terminal state is OPEN (residual — scope-bounded), with the
numbers stated.

---

## 7. Question 6 — Do Foundation Freeze Gate-Purity Criteria Require Modification?

### 7.1 The Three Conditions

| # | Condition | Original Test | Rebased Verdict |
|---|---|---|---|
| 1 | Mutation boundaries declared | "YES if all 46 gates carry verified mode" | **NO.** Denominator is 45; 2 declared at HEAD; 4 after authorized H-06; 23 targets cannot carry the field at all. **Unreachable under authorized scope.** |
| 2 | Replay integrity proven | "YES if all PRODUCER gates have tested replay" | **Conditionally reachable** — but only for declared PRODUCERs. With 4 declarations possible, this tests ≤4 of 14 `*-replay` targets. GP-3 (8 targets) and GP-4 (3 engines) are the real population; GP-4 is authorized, GP-3 largely is not. |
| 3 | Evidence chain trustworthy | "YES for all declared surfaces" | **Vacuously satisfiable, and therefore defective as written.** "For all declared surfaces" is trivially true when almost nothing is declared. A criterion that gets easier the less you declare is inverted. |

### 7.2 Condition 3 Is Inverted — Determination

**D-6.1.** Condition 3 as phrased rewards under-declaration. If one surface is declared and
is trustworthy, the condition reads YES. Rebase to make the population explicit:

> **Condition 3 (rebased):** every declared surface is trustworthy **and** the count of
> undeclared surfaces is stated. Trustworthiness is asserted only over the declared set,
> and the undeclared remainder is reported alongside it, never omitted.

### 7.3 Rebased Foundation Freeze Gate-Purity Criteria

| # | Rebased Condition | Test | State after authorized H-06 |
|---|---|---|---|
| F-1 | Mutation boundaries declared, with population stated | Declared count / 45, plus registered gap count | **NO** — 4 of 45 declared, 41 registered |
| F-2 | Replay integrity proven for every declared PRODUCER | Byte-compare replay, no write first, tested both directions | Reachable for declared PRODUCERs only (≤4) |
| F-3 | Evidence chain trustworthy over the declared set, with the undeclared remainder reported | Per-surface trust + explicit undeclared count | Reachable, with 41 reported |
| F-4 **(new)** | No gate-purity claim rests on uncommitted work | Every count re-measured against HEAD | **Currently FAIL** — GATE-PURITY §1 counts, and 2 of its 4 declared modes, are uncommitted |

**F-4 is added because its absence is what let this class of defect propagate** from
GATE-PURITY §1 through the IAR, IADR, CIEP, and ITBP without detection.

### 7.4 Determination

**D-6.2.** Foundation Freeze gate-purity criteria require modification. Condition 1 is
unreachable under authorized scope, condition 3 is inverted, and a fourth condition is
needed to prevent uncommitted work from being counted as baseline.

**D-6.3. Gate purity cannot be declared closed by executing H-06 as authorized.** After
every authorized action succeeds, 4 of 45 `*-gate` targets carry a declared mode. Freeze
condition F-1 remains NO. Gate purity remains a Foundation Freeze blocker.

**D-6.4.** This does not diminish authorized H-06 execution. GP-2, GP-4, GP-5 and GP-10 are
genuine defects with genuine fixes inside scope — 8 code and label targets, all verified
present and unmodified. Closing them is real progress on gate *correctness*. It is not
closure of gate *purity*, and the two must not be reported as one.

---

## 8. Finding Resolved Read-Only — GP-10: APPARENT → CONFIRMED

GATE-PURITY GP-10 was recorded as **APPARENT**, with the explicit reason: *"`emit()`'s body
was not read for an internal tier suppression."* D-3.6 refused to resolve it by assumption.
That read is a read-only act and is performed here.

**Evidence:**

```
00-MASTER/UCOS-AEE-001/aee_engine.py:1683   def emit(decl: dict, model: dict) -> list[Path]:
00-MASTER/UCOS-AEE-001/aee_engine.py:1807       written = emit(decl, model)
Makefile (HEAD) :1369-1370                  aee-observe:
                                              @python3 …/aee_engine.py --tier observe
```

| Check | Result |
|---|---|
| Does `emit()` accept a tier parameter? | **NO** — signature is `(decl, model)` only |
| Does `emit()`'s body reference `tier` anywhere? | **NO** — zero occurrences in the function body |
| Is the call site guarded? | **NO** — `written = emit(decl, model)` at `main()` indentation |
| Does `emit()` write unconditionally? | **YES** — `target.write_text(body, "utf-8")` per rendered artifact, plus the state file, the learning ledger, and `aee-evidence-index.json` |
| Does `make aee-observe` reach it? | **YES** — passes `--tier observe`; nothing suppresses the write |

**D-7.1: GP-10 is CONFIRMED.** There is no internal tier suppression. `make aee-observe`,
documented in the Makefile as a fast read-only pass, writes tracked files under
`00-MASTER/UCOS-AEE-001/`. The severity recorded in GATE-PURITY (MEDIUM) is unchanged; only
the status moves.

**Scope note:** this strengthens the case for the GP-10 fix (IAR §1.2, authorized, Tier E-1)
and confirms the fix must guard the **call site** — `emit()` has no tier parameter to switch
on, so a guard inside `emit()` would require changing its signature, which is a larger change
than authorized. The authorized minimal fix is the call-site guard.

GP-6 remains **OPEN**: resolving it requires reading `closure_engine.emit()`'s filename table
against the `!`-negated `.gitignore` entries. Not performed here — out of this
determination's question set.

---

## 9. Rebased Acceptance Criteria Register

Supersedes AMC §5 S-1..S-5 and CIEP v2 §6 S-1..S-7. GATE-PURITY D-3.5's five minimum
criteria are rebased in place.

### 9.1 D-3.5 Rebased

| # | D-3.5 Original | Rebase |
|---|---|---|
| 1 | "Every gate entry point resolves to exactly one declared mode: OBSERVE or EXECUTION" | **Plane-scoped and gap-aware:** every `*-gate` target with a structurally capable ownership surface resolves to exactly one declared mode; every target without one is a registered gap. Vocabulary is the ratified four, not two — `PRODUCER` and `OBSERVE_WITH_DECLARED_AUDIT_EMISSION` were added by the Option B decision after D-3.5 was written. |
| 2 | "No OBSERVE path performs any write … or the write is declared as an audit obligation and the label is corrected" | **Unchanged.** Directly satisfiable; GP-5 is the authorized instance. |
| 3 | "No EXECUTION path is reachable without an explicit flag, subcommand or emission authority" | **Unchanged.** |
| 4 | "No flag is declared and unread (closes GP-4)" | **Unchanged and fully authorized** — 3 engines, Tier E-5..E-7. |
| 5 | "A `*-replay` target regenerates in memory and compares bytes; it never writes first" | **Scoped:** applies to the 14 `*-replay` targets at HEAD, of which GP-4 authorizes 3. The remaining 11 are outside authorized scope. |

Criteria 2, 3 and 4 are reachable in full. Criteria 1 and 5 are scope-bounded.

### 9.2 Rebased H-06 Success Criteria

| # | Criterion | Measurement | Required |
|---|---|---|---|
| **R-1** | 4 of 4 authorized declarations carry a measured `gate_mode`, inside the `programme` object | §4.1 surfaces; `find 00-MASTER -name "*-declaration.json" -exec grep -l '"gate_mode"' {} +` | YES |
| **R-2** | 41 of 45 `*-gate` targets registered as named scope gaps with owners | `ASSESSMENT-CONFLICT-REGISTER.md`, per R-4 control C-5 | YES |
| **R-3** | Every declared PRODUCER names a replay path tested in both directions, co-committed | Phase 4 tests | YES |
| **R-4** | Tier E complete: GP-2 (3 engines), GP-4 (3), GP-5 (1), GP-10 (1) | Per-target verification | YES |
| **R-5** | No verification regression against a captured pre-implementation baseline | `verify.sh` vs Phase 0.5 log; stage denominator from the log, not from any document | YES |
| **R-6** | GP findings re-measured: GP-2/GP-4/GP-5/GP-10 → CLOSED; GP-1/GP-3/GP-11a/GP-11b → OPEN (residual); GP-6 → OPEN | Individual re-measurement; no closure by assumption | YES |
| **R-7** | GATE-PURITY §1 plane counts re-measured against HEAD when the document is updated | §2.2 values | YES |
| **R-8** | Gate purity recorded **NOT CLOSED**; Foundation Freeze remains blocked on it | §7 rebased conditions | YES |
| **R-9** | No criterion, count, or claim rests on uncommitted work | Freeze condition F-4 | YES |

### 9.3 Supportable Closure Statement

The only statement supported by measurement after full authorized execution:

> GP-2, GP-4, GP-5, GP-10 CLOSED (re-measured individually). GP-10 was additionally
> promoted APPARENT→CONFIRMED before remediation. GP-1, GP-3, GP-11a, GP-11b OPEN
> (residual — scope-bounded). GP-6 OPEN (unverified).
>
> Gate-mode coverage: **4 of 45** `*-gate` targets declared at HEAD `1f869865`; 41
> registered as named scope gaps. Ownership surface absent for 23 of 45; creating one is
> not authorized.
>
> Foundation Freeze gate-purity condition F-1 (mutation boundaries declared): **NO**.
> Gate purity dimension **NOT CLOSED**. Foundation Freeze remains blocked on gate purity
> pending owner decisions O-3 and O-6.

---

## 10. Determination Summary

| Q | Question | Determination |
|---|---|---|
| 1 | Correct denominator of gate entry points | **45** `*-gate` targets at HEAD (not 46). Plane-scoped: 45 gate / 26 self / 14 replay / 9 verify.sh stages / 27 workflows. GATE-PURITY §1 is a mixed-baseline measurement — 166+4 uncommitted UAUE targets = its reported 170. Numerator at HEAD within the plane: **2**, not 4 — two credited declarations are uncommitted. |
| 2 | Canonical ownership surface per gate | **Heterogeneous.** Class A 9 (`*-declaration.json`) · Class B 13 (domain-named, capable) · Class C 11 (no surface) · Class D 12 (no `00-MASTER` home). D-3.3's uniform-declaration premise holds for 9 of 45. `uga` and `urr` declarations own no gate target at all. |
| 3 | Which surfaces may receive `gate_mode` | **4 now** (authorized). 22 of 45 reachable without creating any file, pending O-3/O-6. **23 of 45 have no capable surface** — creation forbidden. Forbidden targets: 8 registered generated `<prefix>.json`, plus `uga`/`urr`/`uar-analyses` (string or absent `programme`). |
| 4 | Surfaces that must remain unchanged | U-1..U-10 (§5), including `generated-artifact-registry.json` — the §4.5 three-artifact registration gap **must not** be closed under H-06. `GATE-PURITY-DETERMINATION.md` is the sole updatable surface, under its own no-closure-by-assumption discipline. |
| 5 | Does GP-11 closure require modification | **YES — materially.** Four defects: wrong denominator, inflated numerator, two planes conflated, closure unreachable. Split into GP-11a (`*-gate`, 2 of 45) and GP-11b (`*-self`, 26). Both terminate OPEN (residual — scope-bounded). GP-11 must not be marked CLOSED. |
| 6 | Do Freeze gate-purity criteria require modification | **YES.** Condition 1 unreachable (4 of 45 max authorized). Condition 3 is **inverted** — it gets easier the less is declared. New condition F-4 added: no gate-purity claim may rest on uncommitted work. Gate purity **cannot** be closed by executing H-06 as authorized. |

### 10.1 What Changed and What Did Not

**Changed:** every population figure; the GP-11 finding structure; three of four Freeze
conditions; GP-10's status (APPARENT → CONFIRMED); the count of surfaces eligible to
receive `gate_mode`.

**Unchanged:** the ratified Option B vocabulary; the eight Tier E code and label targets,
all re-verified present and unmodified at HEAD; D-3.5 criteria 2, 3 and 4; the requirement
that no mode be declared before measurement; the PRODUCER replay co-obligation; every
forbidden action.

**Not done here:** no owner policy selected, no scope extended, no declaration written, no
engine modified, no surface created, no finding closed.

---

*This document is a determination artifact. It rebases H-06 acceptance criteria against
measured repository truth at HEAD `1f869865`. It authorizes nothing, selects nothing,
creates nothing, and closes nothing. Every figure was measured twice — against `HEAD:` and
against the working tree — and the HEAD value governs. No source file, declaration,
registry, engine, or workflow was modified during its production. The one finding advanced
here (GP-10, §8) was advanced by reading code, not by changing it.*

---

H-06 success criteria rebase complete.
No implementation authorized.
No repository mutation performed.
