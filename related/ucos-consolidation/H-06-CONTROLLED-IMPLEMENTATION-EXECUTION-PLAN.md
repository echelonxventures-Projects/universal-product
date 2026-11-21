# H-06 CONTROLLED IMPLEMENTATION EXECUTION PLAN

| Field | Value |
|---|---|
| **ID** | H-06-CIEP |
| **Authority** | PLANNING ONLY. No implementation authorized in this document. |
| **Phase** | Foundation Closure — Gate Purity Controlled Implementation |
| **Baseline** | HEAD `1f869865` · branch `integration/recovery-001` |
| **Depends on** | H-06-IMPLEMENTATION-AUTHORIZATION-DECISION-RECORD.md (§8 unsigned) |
| | H-06-IMPLEMENTATION-AUTHORIZATION-DECISION-VALIDATION-DETERMINATION.md |
| | H-06-IMPLEMENTATION-AUTHORIZATION-REQUEST.md |
| | H-06-RATIFICATION-VALIDATION-REVALIDATION-DETERMINATION.md |
| | H-06-MUTATION-GOVERNANCE-OWNER-DECISION-RECORD.md |
| **Status** | PLAN PREPARED — EXECUTION NOT STARTED |

---

## 1. Authority Boundary

### 1.1 Ratified Decision

Option B — Explicit Multi-Mode Gate Model is ratified.
H-06-RATIFICATION-VALIDATION-REVALIDATION-DETERMINATION.md §8 — all 5 checks PASS.
Mode vocabulary is authoritative: OBSERVE · PRODUCER · EXECUTION · OBSERVE_WITH_DECLARED_AUDIT_EMISSION.

### 1.2 Implementation Scope

Implementation is limited to the scope defined in H-06-IMPLEMENTATION-AUTHORIZATION-REQUEST.md
§§1 and 4, as validated by H-06-IMPLEMENTATION-AUTHORIZATION-DECISION-VALIDATION-DETERMINATION.md.
No scope element may be added or reinterpreted during execution.

Permitted changes:
- Additive `gate_mode` field on 11 `*-declaration.json` files
- Per-programme mode values after measurement
- PRODUCER replay contracts
- GP-2 write-order correction (3 engines)
- GP-4 dead flag resolution (3 engines)
- GP-5/GP-9 audit classification label correction
- GP-10 `aee_engine.py:1807` tier guard
- Post-implementation verification

### 1.3 No New Architecture

No new registry, no new governance surface, no new authority layer, no new constitutional
document is created under this plan. `mutation-governance-boundary.json`,
`generated-artifact-registry.json`, and `*-declaration.json` files are reused without
structural change beyond the additive `gate_mode` field.

### 1.4 No New Registry

The `gate_mode` field is placed exclusively in each programme's `*-declaration.json`.
The Knowledge Once Principle is observed: mode is not recorded in any other surface.

### 1.5 No New Governance Authority

The three existing authority surfaces remain non-overlapping:
- `mutation-governance-boundary.json` — mutation class governance
- `generated-artifact-registry.json` — generated artifact registration
- `*-declaration.json` — per-programme execution mode declaration

---

## 2. Implementation Phases

### Pre-Condition Gate

Before Phase 1 begins, the following must be true:

| Condition | Required State |
|---|---|
| H-06-IMPLEMENTATION-AUTHORIZATION-DECISION-RECORD.md §8 | AUTHORIZED — signed and dated by implementation authority |
| P-3 — R-4 grandfathering policy | Owner selects Option 1 or Option 2 |
| Baseline commit | Confirmed as `1f869865` on `integration/recovery-001` |

No phase may begin until all three conditions are met.

---

### Phase 1 — Discovery and Baseline Capture

**Purpose:** Establish a clean, evidenced starting state before any file is modified.

**Steps:**

1.1 Confirm working tree cleanliness at the authorized baseline.
```
git status --porcelain
git rev-parse HEAD  # must equal 1f869865
```

1.2 Inventory the 11 affected declaration files. Verify each exists and contains no
existing `gate_mode`, `execution_mode`, or `mode` field.
```
find 00-BOOK -name "*-declaration.json" | sort
# grep gate_mode / execution_mode / mode in each — expect zero hits
```

1.3 Inventory the GP-2 engine candidates (3 engines — write before gate branch).
Locate and record file paths and line numbers from `GATE-PURITY-DETERMINATION.md` GP-2.

1.4 Inventory the GP-4 engine candidates (3 engines — dead `--render` flag).
Locate and record file paths and line numbers from `GATE-PURITY-DETERMINATION.md` GP-4.

1.5 Confirm `aee_engine.py:1807` unconditional `emit()` call exists at that line.

1.6 Confirm `verify.sh` stage 4 carries the "Read-only" label to be corrected (GP-5).

1.7 Run `verify.sh` at baseline. Record 10/10 PASS as pre-implementation evidence.

1.8 Produce a baseline evidence snapshot document recording all findings above.

**Output:** Baseline evidence snapshot with all file:line confirmations.
**Gate:** All 1.1–1.8 steps confirmed before Phase 2 begins.

---

### Phase 2 — Declaration Schema Preparation

**Purpose:** Confirm schema compatibility before any declaration is written.

**Steps:**

2.1 Review each of the 11 `*-declaration.json` programme block structures.
Confirm the `gate_mode` field position (within the `programme` block, alongside
`forbidden_write_prefixes`).

2.2 Define the JSON schema addition for peer review:
```json
"gate_mode": "<OBSERVE | PRODUCER | EXECUTION>",
// for OBSERVE_WITH_DECLARED_AUDIT_EMISSION programmes only:
"audit_emission": {
  "path": "<gitignored path>",
  "type": "append-only"
}
```

2.3 Confirm no existing `--check-declaration` enforcement will reject the new field
before all 11 declarations are updated. If R-4 grandfathering policy selected is
Option 1 (Temporary Compliance Window), confirm the migration tracking mechanism
before proceeding.

2.4 No declaration file is modified in this phase.

**Output:** Schema addition definition and compatibility confirmation.
**Gate:** Schema confirmed compatible before Phase 3 begins.

---

### Phase 3 — Programme Mode Classification

**Purpose:** Measure each of the 11 programmes' actual gate behaviour and assign a
verified mode. No mode is declared speculatively.

For each programme, complete the following before writing any declaration:

| Step | Action |
|---|---|
| 3.x.1 | Run the programme's gate entry point in a controlled environment |
| 3.x.2 | Capture tracked file writes (`git status --porcelain` before and after) |
| 3.x.3 | Capture gitignored writes (targeted `find` on known write paths) |
| 3.x.4 | Assign measured mode from evidence |
| 3.x.5 | Write `gate_mode` field to the declaration only after step 3.x.4 is confirmed |

Mode assignment criteria:

| Measured Behaviour | Assigned Mode |
|---|---|
| Zero tracked writes; zero gitignored writes | OBSERVE |
| Zero tracked writes; always-on gitignored append-only audit write | OBSERVE_WITH_DECLARED_AUDIT_EMISSION |
| Writes deterministic tracked artifacts as declared purpose; replay path exists | PRODUCER |
| Writes via explicit flag/subcommand; mutation is authorized governance act | EXECUTION |

**Programmes and expected classification direction** (subject to measurement — not pre-assigned):

| Programme | Declaration File | Pre-measurement indication from GATE-PURITY-DETERMINATION.md |
|---|---|---|
| UCCEP | `uccep-declaration.json` | GP-1 unconditional write; UCCEP emission-authority pattern partial OBSERVE; likely PRODUCER or EXECUTION |
| UCAF | `ucaf-declaration.json` | GP-1 unconditional write; likely PRODUCER |
| UCL | `ucl-declaration.json` | GP-1 unconditional write (`ucl_engine.py:3030`); likely PRODUCER |
| UGA | `uga-declaration.json` | `gate` is confirmed OBSERVE (`mint=False`); `run` is confirmed PRODUCER |
| UAIE | `uaie-declaration.json` | `if args.render: write_registers()` pattern — gate path is OBSERVE |
| UAUE | `uaue-declaration.json` | Confirmed OBSERVE (`--gate`) and replay OBSERVE; `render` is PRODUCER |
| UKB | `ukb-declaration.json` | `ukb enforce --pre` carries always-on audit write — OBSERVE_WITH_DECLARED_AUDIT_EMISSION |
| UFEP | `ufep-declaration.json` | GP-1 unconditional write; GP-4 dead `--render` flag; likely PRODUCER |
| URAT | `urat-declaration.json` | GP-1 unconditional write; likely PRODUCER |
| UTCE | `utce-declaration.json` | GP-1 unconditional write; likely PRODUCER |
| CMG | `cmg-declaration.json` | Confirmed OBSERVE (script header lines 3–13; `--emit` is opt-in only) |

**Gate:** Each programme's declaration is written only after its own measurement is complete.
Declarations are committed individually per programme, not batched.

---

### Phase 4 — Replay Contract Closure

**Purpose:** For every programme classified as `gate_mode: PRODUCER`, implement and
test the named replay path before the PRODUCER declaration is finalized.

A replay path must:
- regenerate outputs in memory without writing to disk first
- compare the regenerated bytes against the committed artifacts
- exit non-zero if any byte differs
- be named in the programme's `*-declaration.json` under `replay_path`

**Steps for each PRODUCER programme:**

4.x.1 Identify the existing output artifacts registered in `generated-artifact-registry.json`.
4.x.2 Implement or locate the in-memory regeneration path.
4.x.3 Implement the byte-comparison step.
4.x.4 Test: run replay against current committed artifacts — must exit zero.
4.x.5 Test: introduce a synthetic byte difference — replay must exit non-zero.
4.x.6 Add `"replay_path": "<path or make target>"` to the programme's declaration.
4.x.7 Commit declaration and replay path together in a single commit.

**Determinism requirement:** PRODUCER replay must produce byte-identical output on
identical input state. Non-determinism in a PRODUCER is a blocking defect; it must be
resolved before the PRODUCER declaration is written.

**Gate:** No PRODUCER declaration is committed without a tested replay path in the
same commit.

---

### Phase 5 — Defect Remediation

**Purpose:** Apply the five GP code and label fixes. Each is independently committed.

#### 5.1 GP-10 — `aee_engine.py` emit() Suppression (P0 — implement first)

File: `00-MASTER/UCOS-AEE-001/aee_engine.py`
Line: 1807

Change: Add a tier guard so `emit()` is not called when invoked under `--tier observe`.

```python
# Before (line 1807 area — exact syntax confirmed at implementation time):
emit(...)

# After:
if args.tier != "observe":
    emit(...)
# (exact guard condition confirmed against args namespace at implementation time)
```

Verification: Run `aee_engine.py --tier observe` post-fix; confirm zero tracked writes.
Commit independently. Do not batch with other changes.

#### 5.2 GP-2 — Write-Order Correction (3 engines)

Precondition P-4: Confirm each engine's identity from `GATE-PURITY-DETERMINATION.md` GP-2
before modifying any file.

For each of the 3 engines:
- Identify the unconditional write call occurring before the gate verdict branch.
- Resequence: gate verdict branch first; write call after (or conditionally gated).
- The gate must be able to report a pre-write verdict.
- Commit per engine independently.
- Verify: gate verdict is established before any write on the corrected path.

#### 5.3 GP-4 — Dead Flag Resolution (3 engines)

Precondition P-5: Confirm each engine's identity from `GATE-PURITY-DETERMINATION.md` GP-4
before modifying any file.

For each of the 3 engines carrying an unread `--render` flag:
- Determine intended path: does the flag have a defined purpose or is it vestigial?
- If purpose exists: wire the flag to its intended code path.
- If vestigial: remove the flag from the argument parser and any references.
- No flag declared in a parser may be unreachable after this phase.
- Commit per engine independently.
- Verify: `--render` flag reaches its declared path (or is absent from the parser).

#### 5.4 GP-5 — verify.sh Stage 4 Label Correction

File: `verify.sh`

Change: Correct stage 4 label from `"Read-only"` to `"OBSERVE_WITH_DECLARED_AUDIT_EMISSION"`.

This is a single string correction. Commit independently.
Verify: `grep -n "OBSERVE_WITH_DECLARED_AUDIT_EMISSION" verify.sh` returns the corrected line.

#### 5.5 GP-9 — Gitignored Audit Path Classification

For each programme identified as carrying always-on, append-only gitignored audit writes
(UCCEP evidence logs; `determinism.yml` → `determinism-evidence/`):
- Confirm the write path is gitignored.
- Confirm the write is append-only.
- Add `audit_emission` sub-field to the programme's declaration if not already present
  from Phase 3.
- No new governance surface created. This is a declaration addition only.

**Ordering note:** GP-10 and GP-2 are P0 — implement before all other Phase 5 items.
GP-4, GP-5, and GP-9 follow.

---

### Phase 6 — Verification

**Purpose:** Confirm all implementation is complete and correct before closure.

#### 6.1 Structural Validation

| Check | Method |
|---|---|
| All 11 `*-declaration.json` files carry `gate_mode` | `grep -l "gate_mode" 00-BOOK/**/∗-declaration.json` — expect 11 |
| No `gate_mode` value outside vocabulary | Script or manual audit: OBSERVE / PRODUCER / EXECUTION only |
| Every PRODUCER declaration names `replay_path` | Manual audit of each PRODUCER declaration |
| Every EXECUTION declaration has a resolving `mutation-governance-boundary.json` entry | Cross-reference per engine |
| Every OBSERVE + `audit_emission` declaration names a gitignored path | Manual audit; confirm `.gitignore` entry |

#### 6.2 Behaviour Validation

| Check | Method |
|---|---|
| `aee_engine.py --tier observe` produces zero tracked writes | `git status --porcelain` before/after run |
| GP-2 engines: gate verdict before any write | Trace execution path per engine post-fix |
| GP-4 engines: `--render` flag reaches declared path | Invoke flag; confirm code path reached |
| `verify.sh` stage 4 label | `grep -n "OBSERVE_WITH_DECLARED_AUDIT_EMISSION" verify.sh` |
| PRODUCER replay paths: byte-identical output | Run replay per engine; compare against committed bytes |

#### 6.3 Verification Run

```
bash verify.sh
```

Required result: **10/10 PASS**

Any stage failure blocks closure. Do not proceed to §6.4 until 10/10 PASS is confirmed.

#### 6.4 Gate Purity Re-Assessment

After 10/10 PASS is confirmed, re-assess GP-1 through GP-11 individually:

| Finding | Re-assessment Method | Expected Outcome |
|---|---|---|
| GP-1 (15 unconditional writes) | Verify each engine now carries a declared mode | CLOSED — PRODUCER/EXECUTION declared |
| GP-2 (write before gate branch) | Verify write order corrected in 3 engines | CLOSED |
| GP-3 (8 replay targets write before compare) | Verify replay contracts implemented | CLOSED or OPEN (residual) per engine |
| GP-4 (3 dead `--render` flags) | Verify flags wired or removed | CLOSED |
| GP-5 (audit write on read-only label) | Verify `verify.sh` stage 4 label | CLOSED |
| GP-6 (closure_engine PRODUCER boundary) | Verify PRODUCER declaration + boundary entry | CLOSED or OPEN (residual) |
| GP-7 (CI reverts mutation) | Assess whether write-order correction resolves | CLOSED or OPEN (residual) |
| GP-8 (misleading self-guard) | Verify guard label accurate post-mode-declaration | CLOSED or OPEN (residual) |
| GP-9 (undeclared gitignored writes) | Verify `audit_emission` sub-fields present | CLOSED |
| GP-10 (aee-observe unconditional emit) | Verify tier guard present and effective | CLOSED |
| GP-11 (42/46 undeclared modes) | Count declarations carrying `gate_mode` | CLOSED when 46/46 carry verified mode |

No finding may be marked CLOSED without re-measurement. Each re-assessment is committed
as an update to `GATE-PURITY-DETERMINATION.md`.

---

## 3. Change Authorization Matrix

Every planned change must satisfy all three columns before execution.

| Change | Owner | Authority | Validation |
|---|---|---|---|
| `gate_mode` field — `uccep-declaration.json` | Implementation authority | H-06-IADR §8 (signed) + Phase 3 P-2 measurement | Phase 6.1 structural check |
| `gate_mode` field — `ucaf-declaration.json` | Implementation authority | H-06-IADR §8 + Phase 3 P-2 measurement | Phase 6.1 structural check |
| `gate_mode` field — `ucl-declaration.json` | Implementation authority | H-06-IADR §8 + Phase 3 P-2 measurement | Phase 6.1 structural check |
| `gate_mode` field — `uga-declaration.json` | Implementation authority | H-06-IADR §8 + Phase 3 P-2 measurement | Phase 6.1 structural check |
| `gate_mode` field — `uaie-declaration.json` | Implementation authority | H-06-IADR §8 + Phase 3 P-2 measurement | Phase 6.1 structural check |
| `gate_mode` field — `uaue-declaration.json` | Implementation authority | H-06-IADR §8 + Phase 3 P-2 measurement | Phase 6.1 structural check |
| `gate_mode` field — `ukb-declaration.json` | Implementation authority | H-06-IADR §8 + Phase 3 P-2 measurement | Phase 6.1 structural check |
| `gate_mode` field — `ufep-declaration.json` | Implementation authority | H-06-IADR §8 + Phase 3 P-2 measurement | Phase 6.1 structural check |
| `gate_mode` field — `urat-declaration.json` | Implementation authority | H-06-IADR §8 + Phase 3 P-2 measurement | Phase 6.1 structural check |
| `gate_mode` field — `utce-declaration.json` | Implementation authority | H-06-IADR §8 + Phase 3 P-2 measurement | Phase 6.1 structural check |
| `gate_mode` field — `cmg-declaration.json` | Implementation authority | H-06-IADR §8 + Phase 3 P-2 measurement | Phase 6.1 structural check |
| PRODUCER replay path — per PRODUCER programme | Implementation authority | H-06-IADR §8 + Phase 4 replay test | Phase 6.2 byte-compare test |
| GP-10 tier guard — `aee_engine.py:1807` | Implementation authority | H-06-IADR §8 | Phase 6.2 zero-write check |
| GP-2 write-order — engine 1 (P-4 confirmed) | Implementation authority | H-06-IADR §8 + P-4 identity confirmation | Phase 6.2 write-order check |
| GP-2 write-order — engine 2 (P-4 confirmed) | Implementation authority | H-06-IADR §8 + P-4 identity confirmation | Phase 6.2 write-order check |
| GP-2 write-order — engine 3 (P-4 confirmed) | Implementation authority | H-06-IADR §8 + P-4 identity confirmation | Phase 6.2 write-order check |
| GP-4 flag resolution — engine 1 (P-5 confirmed) | Implementation authority | H-06-IADR §8 + P-5 identity confirmation | Phase 6.2 flag-path check |
| GP-4 flag resolution — engine 2 (P-5 confirmed) | Implementation authority | H-06-IADR §8 + P-5 identity confirmation | Phase 6.2 flag-path check |
| GP-4 flag resolution — engine 3 (P-5 confirmed) | Implementation authority | H-06-IADR §8 + P-5 identity confirmation | Phase 6.2 flag-path check |
| GP-5 label — `verify.sh` stage 4 | Implementation authority | H-06-IADR §8 | Phase 6.2 label grep |
| GP-9 `audit_emission` sub-fields | Implementation authority | H-06-IADR §8 + Phase 3 OBSERVE classification | Phase 6.1 gitignore check |
| `GATE-PURITY-DETERMINATION.md` re-assessment | Implementation authority | Phase 6.3 10/10 PASS confirmed | All GP findings re-measured |

---

## 4. Forbidden Actions

The following actions are explicitly prohibited during and after implementation.
No instruction, artifact, or authority chain supersedes these prohibitions within
the H-06 implementation scope.

| Forbidden Action | Reason |
|---|---|
| Modifying H-01 through H-05 scope items | Outside H-06 implementation scope |
| Modifying R-B1 through R-B5 scope items | Outside H-06 implementation scope |
| Creating any new governance file not listed in Phase outputs | Violates No new governance authority boundary |
| Creating any new registry or authority surface | Violates Knowledge Once and Canonical Ownership principles |
| Declaring a mode for any engine before Phase 3 measurement | Violates Evidence before conclusion principle |
| Declaring `gate_mode: PRODUCER` without a tested replay path committed in the same commit | Replay contract is a hard co-obligation |
| Declaring `gate_mode: EXECUTION` without a resolving entry in `mutation-governance-boundary.json` | Option B invariant 4 |
| Modifying `mutation-governance-boundary.json` authority chains | IAR §4 Out of Scope; IAR §5 Forbidden |
| Bypassing declaration ownership by editing a declaration without authorization | H-06-IADR §8 required |
| Manual edits to generated artifacts in `00-BOOK/DATA/` not required by approved scope | IAR §4 Out of Scope |
| Changing constitutional boundaries (mutation-governance-boundary.json classes) | Outside H-06 scope |
| Modifying UICO or UICM artifacts | Standing governance constraint |
| Activating `--check-declaration` enforcement for `gate_mode` before all affected declarations are updated (if R-4 Option 2 selected) | Immediate non-compliance requires batch readiness |
| Skipping any phase gate listed in §2 | Each gate is a hard dependency |

---

## 5. Rollback Strategy

### 5.1 Evidence Preservation

Before Phase 1 begins:
- Record baseline commit SHA (`git rev-parse HEAD`).
- Record `verify.sh` 10/10 PASS output as pre-implementation evidence.
- Store baseline evidence snapshot from Phase 1.8 in the repository root as a
  dated artifact.

During implementation:
- Each change is committed independently (per programme, per engine, per fix).
- Commit messages reference the specific IAR section and GP finding being addressed.
- No batching of unrelated changes in a single commit.

### 5.2 Git Recovery

Each implemented change is independently reversible:

| Change Type | Recovery Method |
|---|---|
| `gate_mode` field addition to a declaration | `git revert <commit>` — additive field removed; no schema breakage |
| PRODUCER replay path addition | `git revert <commit>` per programme |
| GP-10 tier guard | `git revert <commit>` — single conditional |
| GP-2 write-order resequencing | `git revert <commit>` per engine |
| GP-4 flag wiring/removal | `git revert <commit>` per engine |
| GP-5 label correction | `git revert <commit>` — single string |
| GP-9 `audit_emission` sub-field | `git revert <commit>` — additive field removed |

`git revert` is preferred over `git reset --hard`. Reverting an individual commit
must not be assumed to revert others. Each revert is an independent, non-destructive act.

### 5.3 Rollback Triggers

Rollback of a specific change is required when:

| Trigger | Scope of Rollback |
|---|---|
| `verify.sh` stage fails post-change and cannot be resolved within authorized scope | Revert the introducing commit; restore 10/10 PASS |
| A declared mode is found to contradict measured engine behaviour | Revert the declaration commit; re-measure before re-declaring |
| A PRODUCER replay path fails byte-comparison | Revert the PRODUCER declaration commit; fix replay path before re-committing |
| Any implementation action was taken outside the boundaries in IAR §4 | Revert the out-of-scope commit immediately |

### 5.4 Failed Migration Handling

If a programme cannot be classified within the authorized scope (measurement reveals
behaviour not covered by OBSERVE/PRODUCER/EXECUTION):

1. Do not declare a mode for that programme.
2. Document the anomaly in `GATE-PURITY-DETERMINATION.md` as a new finding or
   annotation on the relevant existing GP finding.
3. Do not block other programmes' declarations on the anomaly.
4. Escalate to the mutation governance owner for a scope extension decision before
   proceeding with that programme.

If `verify.sh` cannot reach 10/10 PASS after all changes and within authorized scope,
stop. Do not declare gate purity closure. Record the residual failure in
`GATE-PURITY-DETERMINATION.md` as OPEN (residual) and escalate.

---

## 6. Success Criteria

Implementation is complete when all of the following are confirmed:

| Criterion | Confirmation Method | Required State |
|---|---|---|
| All 46 gates carry declared modes | `gate_mode` field present in all 11 declarations; all 46 gate targets map to a declared programme | YES — or R-4 grandfathering policy accounts for any remainder |
| All PRODUCER obligations satisfied | Each PRODUCER declaration names a tested replay path | YES |
| GP-1 through GP-11 re-assessed | Each finding updated to CLOSED or OPEN (residual) in `GATE-PURITY-DETERMINATION.md` | YES — no finding assumed closed without re-measurement |
| `verify.sh` passing | 10/10 PASS post-implementation | YES |
| Foundation Freeze gate-purity dimension re-assessed | Three conditions evaluated: (1) mutation boundaries declared → YES if 46/46; (2) replay integrity proven → YES if all PRODUCER gates have tested replay; (3) evidence chain trustworthy → YES for all declared surfaces | All three conditions confirmed or residual blockers documented |

Gate purity closure satisfies one dimension of Foundation Freeze only. H-01 through H-05
and R-B1 through R-B5 remain independent and are outside this implementation scope.

---

*This document is a planning artifact. It defines the ordered execution sequence,
change authorization matrix, forbidden actions, rollback strategy, and success criteria
for H-06 implementation. It does not authorize any implementation action. Execution
requires H-06-IMPLEMENTATION-AUTHORIZATION-DECISION-RECORD.md §8 to be signed and
dated by the implementation authority, and P-3 (R-4 grandfathering policy) to be
selected by the owner.*

---

Implementation plan prepared.
Execution not started.
Repository mutation not performed.
