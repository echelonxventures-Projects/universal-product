# UICM — Resolution Context Report

> **Artifact:** `UICM-RESOLUTION-CONTEXT-REPORT`
> **Programme:** UCOS-UICM-000001 — Phase 2
> **AUTHORITY = NONE — DERIVED TRUTH.** This report legislates nothing, creates nothing and
> overrides no owner.
> **Disposition:** DISCOVERY ONLY. No engine code. No registry. No declaration edit. No
> existing registry modified.
> **Determinism:** every claim below cites a located file, an exact identifier, or a
> measurement recomputed from the committed registers. Nothing rests on recollection.

---

## 1. What this report settles

Phase 1 proved the measurement is honest: 62 capabilities × 17 dimensions = 1054 cells,
18/18 invariants satisfied, 158 gaps registered, 0 hidden. Phase 2 asks a different
question — **can every one of those 158 gaps be closed by an owner that already exists?**

The answer is yes for all 158, and the reason matters: the gap register already carries the
resolution seam. Every gap names both a `canonical_owner` (accountability) and a
`discharging_owner` (the source the probe reads). Phase 2 does not invent a resolution
architecture; it *reads the one that is already implied* and records where it is
incomplete.

### Measured-state correction

One figure in the Phase-2 brief does not match the committed registers and is corrected
here rather than carried forward:

| Claim in brief | Measured in `03-CLOSURE-MEASUREMENT-REPORT.json` |
|---|---|
| "0/62 capabilities fully closed" | **4/62 fully closed** — `engine.graph`, `engine.knowledge`, `platform.coverage`, `platform.measurement` each have all 17 dimensions `CLOSED` |
| 158 registered gaps | 158 — confirmed |
| 1054 closure cells | 1054 — confirmed (896 `CLOSED`, 158 `OPEN`, 0 `BLOCKED`) |
| 18/18 invariants | confirmed, `accepted: true` |

Also corrected: the gap distribution in the brief lists nine dimensions summing to 158,
which is confirmed exactly. But `by_class` is `UNSATISFIED-REQUIREMENT` 108,
`ABSENT-OBLIGATION` 42, `REGISTRY-DRIFT` 8 — the brief did not state these, and the
8 `REGISTRY-DRIFT` gaps (not 6) are the ones with a single-action remedy.

The four fully closed capabilities matter to the programme: they are the existence proof
that the 17-dimension bar is *achievable* rather than aspirational. `fully_closed: false`
at the population level is what the brief's "0/62" was reporting.

## 2. Discovery 1 — existing resolution and remediation mechanisms

Nine candidates were examined. **None tracks a gap-resolution lifecycle**, and the reasons
are structural rather than incidental.

| Candidate | Subject of its records | State vocabulary | Why it is not gap resolution |
|---|---|---|---|
| `engine/uckp/evolution.py` `EvolutionLedger` | the constitution (free-text `subject`) | 15 `EvolutionStage` members: `OBSERVE … IMPLEMENTATION, VALIDATION, VERIFICATION, REPLAY, CERTIFICATION …` | One *global* strictly-monotone chain — `append` admits only `next_stage(previous)`, so 158 gaps cannot interleave. `is_terminated()` always returns `False`: there is no closed state to reach. No `gap_id` field. |
| `engine/uicm/observation.py` `ObservationRegistry` | a capability × dimension coordinate | `ClosureState` ×7 with a real transition algebra | **This is the closest match, and it already does the job** — append-only, hash-chained, supersession derived. Its one limitation is cross-run continuity (§5). |
| `engine/uicm/obligation.py` `ObligationRegister` | what a capability owes | none | Records the debt, never the repayment. |
| `engine/uicm/gap.py` `GapRegister` | a non-pass cell | none | Derived per run by total function, in-memory, no cross-run read. A fixed gap simply *stops appearing*; the resolution goes unrecorded. |
| `engine/universal_certification/approval.py` `ApprovalWorkflow` | a `CertificationDecision` | `draft → pending → approved / rejected / withdrawn` | Right shape (hash-chained, append-only, actor + rationale) but wrong subject: human sign-off on a verdict already reached. No plan, implementation, validation or verification stage. |
| `00-MASTER/UAKOS-CLOSURE-009/requirement_engine.py` | a requirement | 5 orthogonal statuses + `gap_classes[]` / `baseline_conditions[]` | Five *independent measurements re-derived every run*, not transitions of a tracked record. `required_action` is the closest thing to a plan anywhere — and it is a free-text sentence. |
| `00-MASTER/UAKOS-CLOSURE-002/closure_engine.py` | a constitutional concept and its canonical home | dispositions, typed gap-count map | Measures homing and duplication of concepts. `gaps` is a dict of counts by category, not per-gap state. |
| `00-MASTER/UCL-000001` | the lifecycle stage graph, and which obligation binds to which stage | stage/obligation binding | Answers "which stage owes what property", not "how is defect X being resolved". |
| `04-REMEDIATION-GRAPH.md`, `02-GAP-CLASSIFICATION.md` | remediation actions (R1, R2, D1–D3), severities | none | The closest *conceptual* precedent for a resolution plan in the repository — and it is hand-written markdown at baseline `ab78f35` with no JSON sidecar and no parser. Records ordering, never progress. |

Confirmed by repository-wide grep over `*.py`: no `RemediationRegistry`,
`ResolutionLedger`, `PlanRegistry`, `ImplementationClosureRegister`, `remediation_state` or
`resolution_state` exists. `RegistryKind` in `engine/registry/universal/identity.py` has 29
members and contains no `REMEDIATION`, `RESOLUTION`, `GAP` or `PLAN` kind — though
`register_kind(kind, code)` is an explicit, append-only extension point ("the only
extension mechanism"), so a kind *could* be admitted without editing the enum.

**Finding.** Resolution history has no dedicated owner, but it does not need a new one:
`ObservationRegistry` already provides append-only resolution history over exactly the
right subject. See §5.

## 3. Discovery 2 — canonical owner for each UICM dimension

All 17 dimensions already declare an `owner_reference` in `uicm.json`. The claim that
this field is absent or null is incorrect — it is populated for every dimension, and
`engine/uicm/obligation.py` `build_register` defaults each obligation's
`discharging_owner` to `dimension.owner_reference`.

| # | Dimension | `owner_reference` | Located instrument | Gaps |
|---:|---|---|---|---:|
| 1 | existence | SRC-CAPABILITY-IDENTITY | `knowledge/canonical-knowledge.json` | 0 |
| 2 | architecture | SRC-CAPABILITY-IDENTITY | same | 0 |
| 3 | ownership | SRC-CAPABILITY-IDENTITY | same | 0 |
| 4 | identity | SRC-ARTIFACT-IDENTITY | `00-MASTER/UCOS-UGA-001/01-EXECUTABLE-OBJECT-REGISTRY.json` | 1 |
| 5 | registry | SRC-REGISTRATION | `pyproject.toml` | 3 |
| 6 | dependency | SRC-REGISTRATION | same | 0 |
| 7 | implementation | SRC-IMPLEMENTATION | `intelligence/UCOS-RIE-CAPABILITY-CATALOG.json` | 0 |
| 8 | contract | SRC-CAPABILITY-IDENTITY | *diverges* — see below | 4 |
| 9 | validation | SRC-REGISTRATION | `pyproject.toml` | 0 |
| 10 | verification | SRC-ARTIFACT-IDENTITY | UGA registry | 0 |
| 11 | testing | SRC-REGISTRATION | `pyproject.toml` | 0 |
| 12 | coverage | SRC-REGISTRATION | same | 3 |
| 13 | determinism | SRC-VERIFICATION-BINDING | `verify.sh` | 42 |
| 14 | governance | SRC-ARTIFACT-IDENTITY | UGA registry | 1 |
| 15 | evidence | SRC-CAPABILITY-IDENTITY | *diverges* — see below | 39 |
| 16 | certification | SRC-GATE-BINDING | `.github/workflows` | 35 |
| 17 | evolution | SRC-GATE-BINDING | same | 30 |

### The divergence discovery finds

For `contract` and `evidence`, the declared `owner_reference` is **not** the artifact that
must change:

- `probe_contract` reads the capability's own `__init__.py` for an `__all__` assignment
  (`_publishes_interface`, accepting `ast.Assign` or `ast.AnnAssign`).
- `probe_evidence` reads the capability's own module names for an `evidence` module, or the
  concatenated package body for a declared evidence format.

Editing `knowledge/canonical-knowledge.json` cannot close either — and that file is
generated and gitignored besides, regenerated per clone by `ucos-knowledge capabilities
--write`. So for those two dimensions the resolution owner is the capability's own package,
resolved through the UGA `ownership_rules` (declared TOTAL, so "unowned" is structurally
unreachable). Recorded as a finding rather than smoothed over.

### The two owner vocabularies are incompatible and must stay separate

| Vocabulary | Example | Where it comes from | Fit as resolution owner |
|---|---|---|---|
| `UCOS-<CATEGORY>-AUTHORITY` | `UCOS-ENGINE-AUTHORITY` | **synthesized** at projection time from the catalogue's `category` field, `engine/knowledge/capability.py:229-232` | **No** — not declared in `00-CMG/CMG-REGISTRY.json` nor any constitutional instrument. Ten such strings exist; all are derived. Treating one as an authority invents an authority. |
| UGA path owner | `engine/uckp`, `UCOS-REPOSITORY-ROOT` | UGA `ownership_rules`, TOTAL over the tracked boundary | **Yes** — located, total, and already the basis of `01-EXECUTABLE-OBJECT-REGISTRY.json` |
| `SRC-*` | `SRC-GATE-BINDING` | `uicm.json` `canonical_sources` | **Yes** — already the recorded `discharging_owner` |

`02-CANONICAL-OWNERSHIP-MATRIX.md` §5 states plainly that every ownership row in §2 "was
authored by a human and is unreadable by machine", and that the reuse engine "refuses to
assert a single owner". Phase 2 therefore derives resolution ownership from machine-readable
instruments only, and cites §2 as authority for *which* owner without parsing it.

## 4. Discovery 3 — existing instruments capable of closing each gap

Six instrument classes cover all 158 gaps, resolving to 43 distinct owners (3 central
programmes/authorities covering 115 gaps, plus 40 capability-local package owners covering
the 43 `contract` and `evidence` gaps). Every one already exists.

| Instrument | Owner | Closes | Gaps | Executable today? |
|---|---|---|---:|---|
| `00-MASTER/UCOS-UGA-001/uga_engine.py run` | UCOS-UGA-001 | identity, governance | 2 | **yes** |
| `pyproject.toml` coverage denominator | UCOS-REPOSITORY-ROOT | registry, coverage | 6 | no — Task-5 freeze |
| capability `__init__.py` (`__all__`) | UGA path owner of the package | contract | 4 | yes |
| capability evidence producer | UGA path owner of the package | evidence | 39 | yes |
| `.github/workflows` + `00-MASTER/UCCEP-000000/uccep-bindings.json` | CMG-DLG-40 machinery | certification, evolution | 65 | yes (evolution partly blocked) |
| `verify.sh` `run_stage` | UCOS-REPOSITORY-ROOT under CMG-DLG-40 | determinism | 42 | no — Task-5 freeze |

Instruments to **reuse rather than rebuild** when closure begins:
`engine/determinism` (`hermetic_env`, `double_build`, `compare_builds`) for the replay
question; `engine/registry/universal` `EvidenceRegistry` for evidence storage;
`engine/universal_certification` for every verdict; `engine/uckp/canonical` for every
digest; `engine/registry/universal/identity.py` `deterministic_id` / `register_kind` for any
identity. Five of these are named in `uicm.json` `prohibited_creations` — recreating one is
not merely redundant, it fails a live gate (`engine/uckp/validation.py`
`_probe_zero_duplication` scans every module in `engine` and `platform` by AST).

## 5. Discovery 5 — is any resolution capability missing?

**One, and it is smaller than expected.**

`ObservationRegistry` already satisfies every requirement the resolution model needs:
append-only (`record` / `record_transition` / read / `verify` — no update, delete or setter
anywhere, measured by UICM-INV-16 over the package's own source), immutable (`Observation`
is a frozen dataclass), deterministic identity (`observation_id` derived from capability
identity + dimension ordinal + revision depth, no counter), explicit lineage (`supersedes`
+ `previous_hash`), and `SUPERSEDED` derived rather than stamped. `OPEN → CLOSED` and
`CLOSED → CERTIFIED` are already declared transitions.

What it lacks is **cross-run continuity**, and this is measurable:

```
02-CLOSURE-OBSERVATION-REGISTRY.json  lineage.max_revision = 3
                                      = DISCOVERED -> MEASURED -> OPEN|CLOSED
```

`max_revision` is exactly 3 for every one of the 1054 coordinates. `build_registry`
constructs a fresh `ObservationRegistry()` on each run and records three observations per
coordinate; there is **no loader** — grep for `from_document` across `engine/uicm/*.py`
returns nothing, and `ClosureDeclaration.load` / `CanonicalOwners.load` are the only `load`
methods in the package. So the committed register is regenerated whole every run, and a
resolution that moves a coordinate from `OPEN` to `CLOSED` leaves **no trace that it was
ever open**. The 2108 `SUPERSEDED` records are all *within-run* procedural steps, not
history.

| Candidate capability | Verdict |
|---|---|
| A resolution/remediation registry | **REFUSED** — duplicates `ObservationRegistry`, violates the steering prohibition, and `prohibited_creations` forbids a parallel register |
| A resolution state machine | **REFUSED** — `ClosureState` already declares `OPEN → CLOSED → CERTIFIED` |
| A resolution identity scheme | **REFUSED** — `observation_id` already derives identity without a counter |
| Cross-run observation continuity | **CANDIDATE — genuinely absent.** Read the committed observation registry as an input and append only where the measured state differs from the current reading |
| A per-dimension resolution declaration | **CANDIDATE — genuinely absent.** No artifact declares, per dimension, the resolution owner and the evidence that closes it |

### Both candidates are digest-neutral, and this was verified rather than assumed

An additive `resolution` key on each `closure_dimensions` record does **not** perturb the
declaration digest, because `DimensionDeclaration.from_record` reads only its eleven
required keys and `to_dict` emits only those. Verified in memory against the committed
declaration:

```
committed declaration digest: 1676f70892b6af25aef666e3853b87e019a7a767500e2120c12656699ea12920
additive   declaration digest: 1676f70892b6af25aef666e3853b87e019a7a767500e2120c12656699ea12920
DIGEST NEUTRAL: True
```

By contrast, adding an **18th dimension** is not digest-neutral and would move every
committed register (digest `bd1acb16…`, cells 1054 → 1116). That is the constraint governing
the `SECURED_ENTRY` directive — see `UICM-PHASE-2-DETERMINATION.md` §5.

Cross-run continuity is also compatible with replay determinism, which is the property most
at risk: because a run appends only where the measured state *differs*, a run over an
unchanged repository appends nothing and rewrites no byte — exactly the `fixed_point`
property `uicm.json` `determinism` already declares.

## 6. Discovery 4 — evidence required to prove closure

Per-dimension evidence requirements are specified in `UICM-RESOLUTION-GAP-REGISTER.md` §3.
Three properties govern all of them:

1. **Evidence is a reference into a located source, never prose.** `ClosureCell.evidence` is
   a tuple of references sealed by `evidence_digest`; a cell in a state that requires
   evidence and carries none is refused by UICM-INV-04.
2. **No `CLOSED` without evidence.** Every state above `DISCOVERED` has
   `requires_evidence: true`, and declaration/enum agreement is itself measured
   (UICM-INV-01) rather than trusted.
3. **No `CERTIFIED` without the located certifier.** `CERTIFIED` is reachable only from
   `CLOSED`, and only with a decision from `engine/universal_certification`. UICM has no
   code path that can upgrade, retry or reinterpret a refusal.

Two probes deserve a caveat that discovery surfaced and that closure work must respect:

- **`probe_determinism` is a substring test.** It searches `verify.sh` and workflow text for
  the declared markers `--replay` and `determinism`. A mention without a real replay
  comparison would close the dimension while proving nothing. The declared remedy is to
  tighten `replay_markers` in the declaration, not to work around the probe.
- **`probe_certification` accepts a capability-local `certification` module.** Taking that
  route for 35 capabilities would create 35 parallel certification instruments. It is
  refused as the canonical route in favour of gate binding, on the authority of
  `certification_binding` and CMG-INV-02.

## 7. Constraints Phase 2 operated under

1. UICM architecture is **FROZEN**. No file under `engine/uicm/` was modified. `uicm.json`
   was not modified. No committed register was modified.
2. No parallel registry, no duplicate identity, no modified canonical ownership.
3. `verify.sh`, `Makefile`, `pyproject.toml` and the existing certification gates were not
   touched.
4. Discovery only — no engine code, per the standing instruction that code waits until
   discovery proves a missing capability.
5. Only the five requested markdown artifacts were written, all under
   `00-MASTER/UCOS-UICM-000001/`.

## 8. Determination

**ASSIMILATION COMPLETE. NO RESOLUTION REGISTRY IS REQUIRED.**

All 158 gaps point to an existing canonical owner. Six located instruments cover the
population. Capability ownership and resolution ownership are structurally separate. The
resolution lifecycle the brief specified — plan → implementation evidence → validation →
verification → closure — maps onto machinery that already exists, with a single genuine
absence (cross-run observation continuity) and one declarative gap (per-dimension
resolution declaration), both of which are digest-neutral extensions rather than new
capabilities.

Proceed to `UICM-PHASE-2-DETERMINATION.md`. Do not begin gap elimination without explicit
approval.
