# H-06 TASK-002 DECLARATION SCHEMA PREPARATION REPORT

| Field | Value |
|---|---|
| **ID** | H-06-T002-DSPR |
| **Authority** | SCHEMA PREPARATION ONLY. No declaration files modified. |
| **Phase** | Foundation Closure — Gate Purity Implementation — Task-002 |
| **Baseline** | HEAD `1f869865` · branch `integration/recovery-001` |
| **Produced** | 2026-08-16 |
| **Status** | SCHEMA PREPARATION COMPLETE |

---

## 1. Existing Schema Reality

### 1.1 Declaration File Inventory (Confirmed from Filesystem)

11 `*-declaration.json` files exist under `00-MASTER/`:

| File | Path | `programme` block present | `forbidden_write_prefixes` |
|---|---|---|---|
| `acee-declaration.json` | `00-MASTER/ACEE-000001/` | YES | YES |
| `aee-declaration.json` | `00-MASTER/UCOS-AEE-001/` | YES | YES |
| `baseline-declaration.json` | `00-MASTER/BASELINE-001/` | YES | YES |
| `rfp-declaration.json` | `00-MASTER/UCOS-RFP-001/` | YES | NO |
| `ucl-declaration.json` | `00-MASTER/UCL-000001/` | YES | YES |
| `ufep-declaration.json` | `00-MASTER/UCOS-UFEP-001/` | YES | YES |
| `uga-declaration.json` | `00-MASTER/UCOS-UGA-001/` | YES (empty `programme` block) | NO |
| `uis-declaration.json` | `00-MASTER/UIS-001/` | YES | YES |
| `urat-declaration.json` | `00-MASTER/UCOS-URAT-001/` | YES | YES |
| `urr-declaration.json` | `00-MASTER/UCOS-URR-001/` | YES (2206 lines; large) | UNCONFIRMED |
| `utce-declaration.json` | `00-MASTER/UCOS-UTCE-001/` | YES | YES |

**IAR §1.1 discrepancy recorded in Task-001 (anomaly A-3):** The IAR names 11 programmes
(uccep, ucaf, ucl, uga, uaie, uaue, ukb, ufep, urat, utce, cmg). Several of these
(uccep, ucaf, uaie, uaue, ukb, cmg) do not have a `*-declaration.json` under their
`00-MASTER/` directory. They may use a different declaration form or location. The
filesystem contains acee, aee, baseline, rfp, urr instead. This discrepancy is a
Task-002 finding; mode classification (Task-003) must use the actual file locations,
not the IAR §1.1 list.

### 1.2 Common `programme` Block Fields

Surveyed across all parseable declarations:

| Field | Present in | Notes |
|---|---|---|
| `id` | All | Programme identifier |
| `name` | All | Human-readable name |
| `version` | Most | Schema version string |
| `authority` | All | Constitutional authority statement |
| `operational_home` | Most | `00-MASTER/<PROGRAMME>/` path |
| `disclosure` | Most | Scope limitation disclosure |
| `governing_instruments` | Most | List of constitutional documents |
| `forbidden_write_prefixes` | 8/11 | Write-scope boundary — what this programme may NOT write |
| `law_owner` | acee, ucl, uis | Pointer to constitutional law document |
| `architecture_owner` | acee, ucl, uis | Pointer to architecture document |
| `terminal_state` | aee | Boolean |
| `evolution_owner` | aee | Evolution governance pointer |

### 1.3 `--check-declaration` Enforcement

The `check_declaration` function in `ucl_engine.py:2474` validates:
- Presence and uniqueness of `id` fields across all declaration sections
- `law_owner` and `architecture_owner` resolve to existing files
- Provider, adapter, kind, relation, graph, capability, record owners all resolve
- `forbidden_write_prefixes` used at runtime by `check_write_scope`

**Confirmed: `check_declaration` does NOT currently validate `gate_mode`.**
Adding `gate_mode` to a `programme` block will not cause `check_declaration` to fail.
The field is invisible to current enforcement. This means:
- Adding `gate_mode` is safe and will not break existing validation.
- Enforcement of `gate_mode` is a future step, separate from field addition.

### 1.4 Mutation Boundary Fields

`forbidden_write_prefixes` in each declaration answers: *what paths may this programme NOT write?*
It does not answer: *does this programme's gate path write, and was that intended?*

`gate_mode` answers the second question. The two fields are complementary and non-overlapping
in their authority claims.

### 1.5 Generated Artifact References

`generated-artifact-registry.json` (in `00-BOOK/DATA/`) owns generated artifact registration
at repository level. It is not read by `check_declaration` directly. PRODUCER mode
declarations will point into it via the `replay_path` field — but the registry itself
is not modified by declaration schema additions.

---

## 2. Proposed Addition

### 2.1 `gate_mode` Field Definition

**Field name:** `gate_mode`
**Location:** Inside the `programme` block of each `*-declaration.json`
**Type:** String (enum)
**Permitted values:** `OBSERVE` · `PRODUCER` · `EXECUTION`
**Required:** YES — for all 11 declarations; no speculative assignment

**JSON schema addition (per programme block):**

```json
"gate_mode": "OBSERVE"
```

or

```json
"gate_mode": "PRODUCER",
"replay_path": "<make target or script path>"
```

or

```json
"gate_mode": "EXECUTION"
```

### 2.2 `audit_emission` Sub-field

For programmes classified as `OBSERVE` that carry an always-on, append-only write
to a gitignored audit path:

```json
"gate_mode": "OBSERVE",
"audit_emission": {
  "path": "<gitignored path>",
  "type": "append-only"
}
```

This sub-field does NOT create a new mode. `OBSERVE_WITH_DECLARED_AUDIT_EMISSION` is
a human-readable classification label applied to an OBSERVE declaration that carries
`audit_emission`. The `gate_mode` value remains `"OBSERVE"` in the JSON; the
sub-classification is conveyed by the presence of the `audit_emission` sub-field.

**Applies to:** programmes with always-on gitignored audit writes (e.g., `ukb enforce --pre`
writing to `.runtime/governance/enforcement-audit.json`).

### 2.3 `replay_path` Co-field for PRODUCER

```json
"gate_mode": "PRODUCER",
"replay_path": "<named make target or script invocation>"
```

`replay_path` is mandatory for every PRODUCER declaration. A PRODUCER declaration
without `replay_path` is constitutionally incomplete and must not be committed.

---

## 3. Ownership Boundary Validation

| Question | Answer |
|---|---|
| Where does `gate_mode` belong? | `*-declaration.json` `programme` block — per-programme, one declaration per programme |
| Does it belong in `mutation-governance-boundary.json`? | NO — that surface owns repository-level mutation class governance (CONSTITUTIONAL_TRUTH, SOURCE, GENERATED_ARTIFACT, EXECUTION, REPOSITORY_STATE). Mode is per-programme, not per-class. |
| Does it belong in `generated-artifact-registry.json`? | NO — that surface owns artifact-level output registration. Mode is about the gate entry point, not the artifact. |
| Does it require a new registry? | NO — `*-declaration.json` is the correct and existing surface. Adding `gate_mode` is additive; no new surface is needed. |

**Knowledge Once Principle satisfied:** `gate_mode` occupies a vacant semantic position in
`*-declaration.json`. It is not present in either of the other two authority surfaces.
No duplication is introduced.

**Canonical Ownership Principle satisfied:**
- `mutation-governance-boundary.json` continues to own mutation class governance.
- `generated-artifact-registry.json` continues to own artifact registration.
- `*-declaration.json` owns per-programme execution mode.
- The three surfaces remain non-overlapping.

---

## 4. Compatibility Analysis

| Check | Finding |
|---|---|
| Is `gate_mode` additive? | YES — no existing declaration carries this field; adding it changes no existing field, no existing validation, no existing behaviour |
| Does any `check_declaration` logic reject unknown `programme` fields? | NO — confirmed from `ucl_engine.py:2474–2580`; the function checks specific named fields and section IDs, not the programme block for unknown keys |
| Does adding `gate_mode` break JSON parsing? | NO — JSON objects accept additional key-value pairs without breakage |
| Does adding `gate_mode` affect `forbidden_write_prefixes` enforcement? | NO — `check_write_scope` reads `forbidden_write_prefixes` only |
| Does adding `gate_mode` affect any existing gate behaviour? | NO — no engine currently reads `gate_mode`; adding the field changes no runtime behaviour until enforcement is activated |
| Will enforcement activation (future) be a breaking change? | YES — activating `--check-declaration` validation for `gate_mode` will fail engines lacking the field. This is the R-4 grandfathering policy question (P-3). It must be resolved before enforcement is activated, not before the field is added. |

**Schema change classification: ADDITIVE. No breaking change.**

---

## 5. Migration Requirements

### 5.1 Files Requiring `gate_mode` Addition (Task-004)

All 11 declaration files confirmed at baseline require `gate_mode` addition:

| Declaration | Programme | Evidence Required Before Assignment | Expected Mode Direction |
|---|---|---|---|
| `acee-declaration.json` | ACEE-000001 | Measure `acee-gate` tracked+gitignored writes | Confirm from GP-1 list (not listed in GP-1 top 15; measure to verify) |
| `aee-declaration.json` | UCOS-AEE-001 | Measure `aee-gate` and `aee-observe` tier writes | GP-10: emit() unconditional — likely PRODUCER; observe tier should be OBSERVE |
| `baseline-declaration.json` | BASELINE-001 | Measure `baseline-gate` tracked writes | GP-1 listed (`baseline_engine.py:1896`); likely PRODUCER |
| `rfp-declaration.json` | UCOS-RFP-001 | Measure rfp gate entry point writes | Requires measurement |
| `ucl-declaration.json` | UCL-000001 | Measure `ucl-gate` tracked writes | GP-1 (`ucl_engine.py:3030`); GP-4 dead flag — likely PRODUCER |
| `ufep-declaration.json` | UCOS-UFEP-001 | Measure `ufep-gate` tracked writes | GP-1 (`ufep_engine.py:1119`); GP-4 dead flag — likely PRODUCER |
| `uga-declaration.json` | UCOS-UGA-001 | Measure `uga gate` subcommand | Confirmed OBSERVE (`mint=False`); `run` is PRODUCER — gate_mode: OBSERVE |
| `uis-declaration.json` | UIS-001 | Measure `uis-gate` tracked writes | GP-1 (`uis_engine.py:1814`); GP-4 dead flag — likely PRODUCER |
| `urat-declaration.json` | UCOS-URAT-001 | Measure `urat-gate` tracked writes | GP-1 (`urat_engine.py:1009`); likely PRODUCER |
| `urr-declaration.json` | UCOS-URR-001 | Measure `urr` gate entry point | Large declaration (2206 lines); requires measurement |
| `utce-declaration.json` | UCOS-UTCE-001 | Measure `utce-gate` tracked writes | GP-1 (`utce_engine.py:855`); GP-8 misleading self-guard — likely PRODUCER |

**IAR §1.1 programmes not found as declaration files** (require Task-003 survey):
uccep, ucaf, uaie, uaue, ukb, cmg — these may use a different declaration mechanism.
Task-003 must locate their declaration surfaces before classifying them.

### 5.2 Evidence Required Before Each Mode Assignment

| Mode | Evidence Required |
|---|---|
| OBSERVE | `git status --porcelain` before/after gate run shows zero tracked writes AND zero gitignored writes |
| OBSERVE (with audit_emission) | Same as OBSERVE + identified gitignored path confirmed append-only |
| PRODUCER | Zero unintended tracked writes; outputs in `generated-artifact-registry.json`; deterministic; replay path tested (exit 0 on match, exit non-zero on diff) |
| EXECUTION | Write reachable only via explicit flag/subcommand; resolving entry in `mutation-governance-boundary.json` |

### 5.3 Validation Required After `gate_mode` Updates

Per IAR §6 and Task Breakdown §5 verification gates:

| Gate | Check |
|---|---|
| VG-7 | `gate_mode` value in declaration matches Task-003 measurement exactly |
| VG-8 | PRODUCER replay exits zero on identical input |
| VG-9 | PRODUCER replay exits non-zero on byte difference |
| VG-15 | All 11 declarations carry `gate_mode` (post-Task-004) |
| VG-14 | `bash verify.sh` 10/10 PASS post-implementation |

---

## 6. Forbidden Actions

| Action | Status |
|---|---|
| Declaration edits performed in this task | NONE — all analysis is read-only |
| Registry changes performed | NONE |
| Implementation performed | NONE |
| `gate_mode` values written to any file | NONE |
| `check_declaration` enforcement activated | NONE — no engine modified |

All steps in this task were read and analysis operations only. No file in the repository
was modified.

---

*This document is the Task-002 schema preparation artifact. It defines the exact JSON
field addition, confirms ownership boundary, validates compatibility, and lists
migration requirements. No declaration file has been modified. Task-003 (programme mode
classification measurements) may proceed.*

---

Task-002 schema preparation complete.
No declaration changes executed.
Implementation mutation not performed.
