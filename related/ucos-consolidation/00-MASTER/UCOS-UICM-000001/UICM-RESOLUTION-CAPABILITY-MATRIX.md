# UICM — Resolution Capability Matrix

> **Artifact:** `UICM-RESOLUTION-CAPABILITY-MATRIX`
> **Programme:** UCOS-UICM-000001 — Phase 2 (discovery)
> **AUTHORITY = NONE — DERIVED TRUTH.**
> **Disposition:** DISCOVERY ONLY. Reuse-before-create determination. No code written.
> **Reuse order applied:** existing engine → existing registry → existing framework →
> existing owner → only then create.

---

## 1. Method

The resolution model the brief specifies has six stages. Each stage is treated as a
*capability requirement*, and each requirement is run through the reuse order before any
creation is considered:

```
Gap Observation
      |
      v
Canonical Owner Resolution Plan
      |
      v
Implementation Evidence
      |
      v
Validation Observation
      |
      v
Verification Observation
      |
      v
Closure Observation
```

`CREATE` appears twice in the table below, both times as an *additive extension of an
existing module or declaration* rather than a new capability — and both times verified
digest-neutral against the committed registers.

## 2. Reuse determination — the six lifecycle stages

| # | Stage the model requires | Canonical owner | Existing implementation | Decision | Gap |
|---:|---|---|---|---|---|
| 1 | **Gap Observation** | UCOS-UICM-000001 | `engine/uicm/gap.py` `GapRegister` + `engine/uicm/observation.py` `ObservationRegistry`; committed as `04-CLOSURE-GAP-REGISTER.json` / `02-CLOSURE-OBSERVATION-REGISTRY.json` | **REUSE AS-IS** | none — 158 gaps already registered, 0 hidden |
| 2 | **Canonical Owner Resolution Plan** | — | `04-REMEDIATION-GRAPH.md` (dead markdown, baseline `ab78f35`, no parser); `requirement_engine.py` `required_action` (free-text sentence); `PlanNode.lifecycle` (free-text, no state machine) | **CREATE (declarative, additive)** | **yes** — no artifact declares, per dimension, the resolution owner and closing evidence |
| 3 | **Implementation Evidence** | Universal Registry Platform | `engine/registry/universal` `EvidenceRegistry` (`kind = RegistryKind.EVIDENCE`, `required_attributes = {"subject"}`) | **REFERENCE ONLY** — a `prohibited_creation`; UICM opens no registry | none |
| 4 | **Validation Observation** | UCOS-UICM-000001 | `engine/uicm/validation.py` — 18 invariants over the run's own artifacts; `engine/uicm/measurement.py` — 17 probes | **REUSE AS-IS** | none — a resolution is validated by re-measurement, which already exists |
| 5 | **Verification Observation** | UCOS-UICM-000001 + EPIC-004 | `UicmController.replay` (byte comparison), `ObservationRegistry.verify` (chain recompute), `engine/determinism` (`hermetic_env`, `double_build`, `compare_builds`) | **REUSE AS-IS** | none |
| 6 | **Closure Observation** | UCOS-UICM-000001 | `ObservationRegistry.record` + `ClosureState` `OPEN → CLOSED → CERTIFIED`; verdict from `engine/universal_certification` | **REUSE AS-IS**, with one limitation | **partial** — history does not survive across runs (§4) |

**Result: 4 REUSE AS-IS, 1 REFERENCE ONLY, 1 CREATE.** Five of six stages are already owned.

## 3. Reuse determination — supporting capabilities

| # | Capability needed | Canonical owner | Existing implementation | Decision |
|---:|---|---|---|---|
| 7 | Canonical serialization + content digest | UCKP Layer Zero | `engine/uckp/canonical.py` — `canonical_json`, `content_hash` | **REUSE AS-IS** — a second definition is a measured violation (`_probe_zero_duplication`, AST scan over all of `engine` and `platform`) |
| 8 | Deterministic identity + kind vocabulary | Universal Registry Platform | `engine/registry/universal/identity.py` — `deterministic_id`, `RegistryKind` (29 members), `register_kind(kind, code)` | **REUSE AS-IS** — extend by registration only. No new kind is needed (§4) |
| 9 | Append-only hash-chained ledger | five existing homes | `engine/registry/universal/audit.py`, `engine/certification/ledger.py`, `engine/universal_certification/audit.py` + `approval.py`, `engine/context/registry.py`, and UICM's own `obligation.py` / `observation.py` | **REUSE the nearest** — a seventh implementation is the duplication Article 3 forbids |
| 10 | Artifact identity admission | UCOS-UGA-001 | `00-MASTER/UCOS-UGA-001/uga_engine.py run`; ledger `00-BOOK/DATA/id-ledger.json` `by_object` | **REUSE AS-IS** — closes the identity and governance gaps |
| 11 | Certification verdict | UCOS-EPIC-006 | `engine/universal_certification` — `UniversalCertificationEngine`, `ComplianceEngine`, `ApprovalWorkflow` | **INVOKE** — never reimplement; `CERTIFIED` is unreachable without it |
| 12 | Capability lifecycle | UCIC-001 | 15 stages, crosswalked by `ucic_stages` on every dimension | **BIND, DO NOT FORK** — a second lifecycle was already REFUSED once (Ω-E04) |
| 13 | Evolution stage vocabulary | UCKP Article 14 | `engine/uckp/evolution.py`, published as `EVOLUTION_STAGE = "uckp.evolution-stage"` | **REFERENCE** the vocabulary (`IMPLEMENTATION`, `VALIDATION`, `VERIFICATION`, `CERTIFICATION`); do not coin synonyms and do not reuse the ledger (single global chain, never terminates) |
| 14 | Gate binding per check | CMG-DLG-40 / UCCEP-000000 | `00-MASTER/UCCEP-000000/uccep-bindings.json` — `CK-<PROG>` checks under aggregate gates `G-18`, `G-22`–`G-26` | **REUSE AS-IS** — closes the certification and evolution gaps |
| 15 | Replay / fixed-point convergence | UCOS-ARE-000001 + EPIC-004 | `engine/constitution/replay.py` (`converge`, `require_fixed_point`); per-programme `--replay` | **REUSE AS PATTERN** |
| 16 | Reuse-before-create determination | UKIP | `engine/knowledge/integration/reuse.py` `ReuseEngine`; `engine/ceu/sufficiency.py` `assess` | **REUSE AS-IS** — this matrix is its output |

## 4. The two CREATE rows, stated at minimum scope

### CREATE-1 — Cross-run observation continuity

**Not a new capability. A loader for a register that already exists.**

`ObservationRegistry` satisfies every structural requirement already: append-only (three
verbs — append, read, verify; no update, delete or setter, and the absence is *measured* by
UICM-INV-16 over the package's own source), immutable (frozen dataclass), deterministic
identity (`observation_id(capability, dimension, revision)`, no counter, no clock), explicit
lineage (`supersedes` + `previous_hash`), and `SUPERSEDED` derived rather than stamped.

What is absent is measurable and exact:

```
02-CLOSURE-OBSERVATION-REGISTRY.json   lineage.max_revision = 3
                                       observation_total    = 3162  (= 1054 x 3)
                                       superseded_total     = 2108  (all within-run)
```

Every coordinate has exactly three observations — `DISCOVERED → MEASURED → OPEN|CLOSED` —
because `build_registry` constructs a fresh registry each run. No loader exists: grep for
`from_document` across `engine/uicm/*.py` returns nothing, and the only `load` methods in the
package are `ClosureDeclaration.load` and `CanonicalOwners.load`. The consequence is that a
gap moving from `OPEN` to `CLOSED` leaves **no record that it was ever open** — the
resolution itself is invisible.

| Property | Requirement | Already satisfied? |
|---|---|---|
| append-only | no mutating operation | **yes** — measured by UICM-INV-16 |
| immutable | frozen dataclass records | **yes** |
| deterministic IDs | derived from owned identity + revision depth | **yes** |
| derived identity | capability register + dimension ordinal | **yes** |
| lineage references | `supersedes`, `previous_hash` | **yes** |
| no mutable status updates | state change = new observation | **yes** |
| `SUPERSEDED` terminal only | no outgoing transition | **yes** |
| replay deterministic | byte comparison via `--replay` | **yes** |
| **cross-run history** | prior register read as an input | **NO — the sole absence** |

**Scope:** read the committed observation registry as an input alongside the five canonical
sources, and append only where the measured state differs from the coordinate's current
reading. **Compatible with replay:** a run over an unchanged repository appends nothing and
rewrites no byte, which is exactly the `fixed_point` property `uicm.json` already declares.
**Not required:** no new register, no new kind (`register_kind` unused), no state-machine
change, no identity scheme.

### CREATE-2 — Per-dimension resolution declaration

**Declarative only. No engine code.**

No artifact declares, per dimension, *who resolves* and *what evidence closes it*. The gap
register carries `discharging_owner` per gap, but that is the source the probe reads — and
for `contract` and `evidence` it is demonstrably not the artifact that must change.

**Scope:** an additive `resolution` block on each `closure_dimensions` record in
`uicm.json`, naming the resolution owner and the closing evidence.

**Verified digest-neutral.** `DimensionDeclaration.from_record` reads only its eleven
required keys and `to_dict` emits only those, so an unknown key is ignored by the digest
path. Tested in memory against the committed declaration:

| Declaration | Digest |
|---|---|
| committed | `1676f70892b6af25aef666e3853b87e019a7a767500e2120c12656699ea12920` |
| with additive `resolution` block on all 17 dimensions | `1676f70892b6af25aef666e3853b87e019a7a767500e2120c12656699ea12920` |
| **neutral** | **yes** |
| with an 18th dimension added | `bd1acb16edd73e267e3ee4f45847aef35fbc7bfdb2d5a6150d2bcf0a95a3a668` — **not neutral**, cells 1054 → 1116 |

So CREATE-2 can be declared without moving a single committed byte, while a new *dimension*
cannot. This distinction governs the `SECURED_ENTRY` directive.

## 5. Explicit refusals

| Proposed | Verdict | Ground |
|---|---|---|
| `ImplementationClosureRegister` (new JSON register) | **REFUSED** | Duplicates `ObservationRegistry`; steering prohibits a remediation registry; `prohibited_creations` forbids a parallel register |
| `RemediationRegistry` in `engine/registry/universal` | **REFUSED** | Would modify an existing registry, which steering forbids |
| New `RegistryKind` member via `register_kind` | **REFUSED — not needed** | No new artifact kind is introduced; the extension point stays unused |
| Resolution state machine | **REFUSED** | `ClosureState` already declares `OPEN → CLOSED → CERTIFIED` with a transition algebra |
| Resolution identity scheme | **REFUSED** | `observation_id` already derives identity without a counter |
| Editing `04-CLOSURE-GAP-REGISTER.json` to add resolution fields | **REFUSED** | Committed registers are immutable; correction is by supersession, never by edit |
| Forking the UCIC-001 lifecycle | **REFUSED** | Already refused once (Ω-E04); `ucic_stages` binds instead |
| Capability-local `certification.py` for 35 capabilities | **REFUSED** | Would create 35 parallel certification authorities; violates `certification_binding` and CMG-INV-02 |
| Recording a coverage *percentage* in any register | **REFUSED** | A percentage is an observation of an execution, so a committed register holding one has no fixed point |

## 6. Determination

**NO NEW CAPABILITY IS REQUIRED TO OWN GAP RESOLUTION.**

Fourteen of sixteen requirements are discharged by an existing owner. The two CREATE rows
are a loader for an existing register and an additive block in an existing declaration —
both verified digest-neutral, neither a new registry, neither requiring a new identity, state
machine or kind.

**Neither CREATE row is authorized by this document.** Both are candidates pending the
explicit approval reserved in `UICM-PHASE-2-DETERMINATION.md`.
