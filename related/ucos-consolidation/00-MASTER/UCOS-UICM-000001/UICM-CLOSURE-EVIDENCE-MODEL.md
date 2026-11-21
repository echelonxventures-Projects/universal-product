# UICM — Closure Evidence Model

> **Artifact:** `UICM-CLOSURE-EVIDENCE-MODEL`
> **Programme:** UCOS-UICM-000001 — Phase 4 discovery
> **AUTHORITY = NONE — DERIVED TRUTH.**
> **Disposition:** DISCOVERY ONLY. No evidence produced. No registry created. No gap resolved.

---

## 1. Two evidence layers that must not be confused

The word "evidence" carries two different subjects in this programme, and merging them would let
a classification masquerade as a proof.

| | **Closure evidence** | **Capability evidence** |
|---|---|---|
| Subject | one capability × dimension coordinate | the capability itself |
| Question | what did the probe read? | does this capability *produce* evidence? |
| Form | `tuple[str, ...]` of references into located sources | a producer module or a declared format |
| Held by | `Observation.evidence`, sealed by `evidence_digest` | the capability's own source tree |
| Closes | the coordinate it belongs to | dimension 15 (`evidence`) only |
| Owner | UCOS-UICM-000001 (measurement) | the capability's own package |

Dimension 15 is the one place they meet: closure evidence *for the evidence dimension* is a
reference to the capability evidence producer. Everywhere else they are independent.

## 2. Closure evidence — structurally mandatory

Evidence is not a convention here; it is enforced in three separate places, and none of them can
be satisfied by prose.

**A `CLOSED` result cannot be constructed without evidence.** `ProbeResult.closed` raises
`MeasurementError` when the evidence tuple is empty. So an unevidenced closure is not a bad
record — it is an unconstructable one.

**Every state above `DISCOVERED` requires evidence.** `ClosureState.requires_evidence` is true
for `MEASURED`, `OPEN`, `BLOCKED`, `CLOSED`, `CERTIFIED` and `SUPERSEDED`, and the declaration and
the enum are compared for agreement at load (`require_state_conformance`, UICM-INV-01).

**The absence is measured, not trusted.** UICM-INV-04 counts offending cells, and that count is
submitted to the certifier as `uicm.unevidenced_closure` with threshold 0 and severity
`BLOCKING`.

**Evidence is a reference, never an assertion.** Every emitted value is a colon-delimited
reference into a located source — `identified:25`, `coverage_source:engine`,
`interface_surface:engine/ceu`, `replay_binding:gate uaue-gate.yml`. `evidence_digest` seals the
set: `digest({"cell": key, "evidence": [...]})`, empty string when unevidenced.

## 3. Required closure evidence per dimension

Read from the probes. Each row is what the probe emits on `CLOSED` — the evidence that must come
to exist for the coordinate to close.

| Dimension | Evidence kind | Emitted on closure |
|---|---|---|
| identity | identity-reference | `identified:<n>`, `identity_sample:<UCOS-…>` |
| governance | governance-status | `governance_status:<statuses>`, `validation_contract:<contract>` |
| registry | registration-reference | `capability_register:<UCKO-CAP-…>`, `coverage_source:<location>`, `coverage_addopts:<name>` |
| coverage | denominator-membership | `coverage_source:<location>`, `coverage_addopts:<name>` |
| contract | interface-surface | `interface_surface:<location>`, `module_count:<n>` |
| evidence | producer-reference | `evidence_producer:<location>/evidence.py` or `evidence_producer:emits <format>` |
| certification | instrument-reference | `certification_instrument:gate <workflow>` |
| determinism | replay-obligation | `replay_binding:verification entry point` or `replay_binding:gate <workflow>` |
| evolution | safety-net | three simultaneous `safety_net:<member>` references |

**Coverage is measured as denominator membership, never as a percentage.** The declaration is
explicit about why: a percentage is an observation of an execution rather than repository content,
so a committed register holding one would have no fixed point.

## 4. Capability evidence — what actually counts as a producer

Dimension 15 has the second-largest gap population (39) because the bar is deliberately high.
The probe accepts exactly two things, and explicitly refuses two others.

**Route 1 — a producer module.** A module named by the declared `producer_module` parameter
(`evidence`) among the capability's own module names.

**Route 2 — a declared evidence format** emitted by the capability's own code:

```python
_EVIDENCE_FORMAT = re.compile(r"\"(ucos-[a-z0-9-]*evidence[a-z0-9/.-]*)\"")
```

Matched against the concatenation of every artifact in the capability. The pattern is stricter
than it first appears, and each constraint matters:

| Constraint | Consequence |
|---|---|
| double quotes required | `'ucos-x-evidence/1.0.0'` does **not** match |
| lowercase only | any uppercase letter breaks the match |
| must contain the literal `evidence` | `"ucos-x-report/1.0.0"` does not qualify |
| must be a literal | f-strings and concatenations do not match |
| version suffix optional | `"ucos-ucxi-context-evidence-index"` qualifies |

**Refused: `catalogue evidence_present` and `artifact evidence_class`.** Both are declared as
`reference_only_fields`, and the reason given is decisive: accepting either "would close this
dimension for every capability in the repository, which is how a measurement stops measuring
anything". They are recorded in the finding and do not close the dimension.

## 5. Evidence contract shape — reuse, do not invent

Three located evidence contracts already exist. They differ in scope, not in construction:

| Owner | Format constant | Scope |
|---|---|---|
| `engine/governance/evidence.py` | `ucos-governance-evidence/1.0.0` | aggregate of aggregates |
| `engine/acceptance/evidence.py` | `ucos-acceptance-evidence/1.0.0` | one decision, one record |
| `engine/context/evidence.py` | `ucos-ucxi-context-evidence-index` | whole-layer document |

The shared construction — which any new capability evidence producer should follow rather than
re-derive:

1. a **frozen dataclass**, no setters;
2. a `blocking_failures` / `advisory_failures` split, so *why* it failed is inside the record;
3. `*_ref` content hashes to every subordinate record, so the root hash commits over the chain;
4. a `*_sha256` self-hash plus `verify_integrity()` that re-derives it;
5. **no wall clock** — byte-identical across identical runs;
6. writes routed through `find_frozen_writes` before touching disk
   (`_assert_writable` raises rather than writing into the certified corpus).

**Storage is not UICM's.** `EvidenceRegistry` (`engine/registry/universal/registries.py`) is the
located home: `kind = RegistryKind.EVIDENCE`, `default_namespace = "ucos.evidence"`,
`required_attributes = frozenset({"subject"})`. It is a `prohibited_creation` for UICM —
REFERENCE only. Identity there is derived (`deterministic_id(kind, namespace, natural_key)`), and
versions supersede rather than overwrite (`RegistrationState`: `ACTIVE` / `SUPERSEDED` /
`DEPRECATED` / `RETIRED`, with `superseded_by` and an `AuditAct.SUPERSEDE` entry).

## 6. Certification handoff

UICM projects three inputs and reports the decision unchanged. It holds no rule, no criterion, no
verdict logic and no certificate type.

```
closure measurement ->  ValidationInput       did the closure claims validate?
                    ->  MeasurementInput      decidable closure metrics
                    ->  RepositoryTruthInput  population homed? gaps closed?
                              |
                              v
              UniversalCertificationEngine (UCOS-EPIC-006)
                              |
                              v
                    Certificate + evidence
```

**Ten metrics, every one BLOCKING, every threshold zero-tolerance but one:**

| Metric | Threshold | Comparator |
|---|---:|---|
| `uicm.hidden_gaps` | 0 | EQ |
| `uicm.duplicate_ownership` | 0 | EQ |
| `uicm.invented_capability` | 0 | EQ |
| `uicm.orphan_artifact` | 0 | EQ |
| `uicm.unevidenced_closure` | 0 | EQ |
| `uicm.mutable_registry_operation` | 0 | EQ |
| `uicm.matrix_totality` | expected cell count | EQ |
| `uicm.observation_chain_intact` | 1 | EQ |
| `uicm.blocking_invariant_violations` | 0 | EQ |
| **`uicm.closed_cell_ratio`** | **`matrix.cell_count`** | EQ |

Three properties make this a projection rather than a claim:

- **verdicts are computed, not asserted** — `Measurement.evaluate` derives `satisfied` from value,
  comparator and threshold, so UICM cannot submit a metric claiming a satisfaction it did not
  measure;
- **consistency is the certifier's own conjunction** — `RepositoryTruthInput.consistent` requires
  closed, fully homed and zero open gaps; UICM supplies counts only;
- **a refusal is reported as-is** — there is no branch that upgrades, retries or reinterprets it.

The certifier's rule vocabulary: `compliance-conformant`, `validation-accepted`,
`validation-evidence-present`, `measurements-present`, `measurements-satisfied`,
`repository-truth-consistent`, `disclosure-present`, `version-pinned`, `measurement-complete`,
`validation-complete`.

### The structural finding: `CERTIFIED` is population-wide, not per-cell

`uicm.closed_cell_ratio` is submitted as BLOCKING with threshold equal to the **total** cell
count, and the code comments the choice deliberately: "a closure certificate that ignored
unclosed cells would certify the opposite of what it measured."

`project_certification` produces **one** `CertificationDecision` for the whole programme. There is
no per-cell decision and no per-capability certificate. Since `CERTIFIED` is reachable only from
`CLOSED` and only with a decision from the located certifier, it follows that:

> **No individual cell can reach `CERTIFIED` until all 158 gaps are closed.**

Current state: `certification_status = "not-certified"`, 3 blocking rules failed, 2 blocking
non-conformant frames. This is the correct measurement, not a defect — but it means the 896
already-closed cells and the 4 fully closed capabilities cannot be certified individually. The
`CLOSED → CERTIFIED` transition is legal in the algebra and unreachable in practice for any
proper subset of the population.

Whether per-capability certification is desirable is **not determined here**. It would require a
per-subject projection and a change to what is submitted, which is a Phase-5 question.

## 7. Failed resolution — evidence of an attempt does not exist

A resolution attempt that fails to change the measured state produces **no observation**.
Reconciliation case 1 applies (measured state equals current reading), so zero records are
appended. The register records outcomes, not attempts.

This is a real limitation and it is **accepted as intended**:

| Option | Verdict |
|---|---|
| Record the attempt in the observation registry | **REFUSED** — an attempt is not an observation of repository state, and recording *who tried when* requires an actor and a clock, both forbidden in every emitted byte |
| Record it in a new attempt register | **REFUSED** — no new registry |
| Record it in `ucda-decisions.json` as a work package | **AVAILABLE** — append-only, `authorization_required`, `route`, and `DP-3 REGISTERED-AS-IMPLEMENTATION-WORK-PACKAGE` already exists for exactly this |
| Leave it in the gate output | **AVAILABLE** — the failing gate names the refusal |

A failed attempt that *breaks measurability* is different, and it **is** recorded: a probe that
cannot execute yields `BLOCKED`, and `MEASURED → BLOCKED` / `OPEN → BLOCKED` are declared
transitions. So an attempt that makes a dimension unmeasurable leaves a visible trace, while an
attempt that simply does not work does not.

## 8. Rollback and rejection without mutation

**Regression is already a declared transition** — verified against the live algebra:

```
  CLOSED     -> BLOCKED, CERTIFIED, OPEN, SUPERSEDED
  CERTIFIED  -> BLOCKED, OPEN, SUPERSEDED
  SUPERSEDED terminal: True
```

The docstring states the intent: "Every pass state can fall back to `OPEN` or `BLOCKED`, because
closure is a measurement of the current tree and a regression must be expressible."

So rollback needs no new mechanism. A reverted change is re-measured, the coordinate reads `OPEN`
again, and a **new observation** is appended at the next revision. The prior `CLOSED` observation
is untouched and becomes `SUPERSEDED` by derivation. Nothing is edited, nothing deleted.

**There is no rollback concept for repository artifacts anywhere in the repository.** The only
`rollback` implementations are for modelled runtime executions
(`engine/runtime/execution/rollback.py`, which "reverses records, not live effects") and
deployment descriptors (`engine/runtime/deploy.py`, `ROLLBACK_STRATEGY =
"reversible-checkpoint"`). For repository artifacts the entire reversal vocabulary is
**supersession**. Git revert is the actual file-level mechanism, and it sits outside UICM — the
register simply observes the reverted tree.

**Rejection of a certification** is likewise already modelled, append-only:

```
ApprovalState : draft -> pending -> {approved | rejected | withdrawn}     terminal: last three
ApprovalAction: submit, approve, reject, withdraw
```

Each transition **appends** a frozen `ApprovalRecord(sequence, certification_id,
certificate_sha256, action, from_state, to_state, actor, rationale, prev_hash, record_hash)`. The
prior record is never touched — the new record carries `from_state`. `OP-CERT-001` is fail-closed:
approving a NOT-CERTIFIED decision raises `ApprovalWorkflowError`, so today's `not-certified`
decision **cannot** be approved by any path.

This is the pattern UICM should point at rather than reproduce: failure as an appended record
carrying `from_state` / `to_state` / `actor` / `rationale`, chained by `prev_hash`.

## 9. Determination

| Item | Finding |
|---|---|
| Closure evidence | **STRUCTURALLY MANDATORY** — unevidenced `CLOSED` is unconstructable; enforced in 3 places |
| Evidence is a reference | **HELD** — colon-delimited references into located sources, sealed by `evidence_digest` |
| Capability evidence bar | **HIGH BY DESIGN** — producer module or quoted `"ucos-…evidence…"` literal; classifications refused |
| Evidence storage | **OWNED ELSEWHERE** — `EvidenceRegistry`, a `prohibited_creation` for UICM |
| Certification handoff | **EXISTS AND IS A PROJECTION** — 10 BLOCKING metrics, computed verdicts, refusal reported as-is |
| Per-cell certification | **NOT POSSIBLE** — `closed_cell_ratio` is population-wide; no cell certifies until all 158 close |
| Failed resolution evidence | **DOES NOT EXIST** — accepted; attempts belong in UCDA work packages or gate output |
| Rollback | **NO NEW MECHANISM NEEDED** — `CLOSED → OPEN` declared; supersession is the only reversal vocabulary |
| Rejection | **ALREADY MODELLED** — `ApprovalWorkflow`, append-only, OP-CERT-001 fail-closed |

**No evidence capability may be created.** Every layer has a located owner. The only open design
question surfaced here — whether certification should ever be per-capability rather than
population-wide — is deferred to Phase 5 and explicitly not answered.
