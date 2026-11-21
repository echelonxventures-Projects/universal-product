# UICM — Resolution Authority Determination

> **Artifact:** `UICM-RESOLUTION-AUTHORITY-DETERMINATION`
> **Programme:** UCOS-UICM-000001 — Phase 4 discovery
> **AUTHORITY = NONE — DERIVED TRUTH.**
> **Disposition:** DISCOVERY ONLY. No implementation. No registry created. No gap resolved.
> **Constraint compliance:** `ObservationRegistry` remains the immutable source of history. No
> remediation registry. No mutable update. No gap status edited. Every closure is a new
> observation.

---

## 1. Determination

**AN AUTHORIZATION PATH EXISTS FOR EVERY LAYER EXCEPT ONE, AND THE MISSING LAYER IS NOT AN
AUTHORITY — IT IS A BINDING.**

Six located instruments already govern change. None needs to be created, and none is a
remediation registry. What no instrument does is bind a **UICM gap identifier** to an
authorization record, so a resolution today is authorized *as a change* but never *as the
discharge of a specific measured gap*.

## 2. The authorization path, as it already exists

| Layer | Question it answers | Located owner | Instrument | Append-only |
|---:|---|---|---|---|
| 1 | May this concept be admitted at all, and under which disposition? | CMG-000001 | Art LXXVI.2 (a–h admission procedure), Art LXXVII.2 (totality rule) | yes — LXXVI.3 |
| 2 | Is the decision dispositioned, with located evidence? | CEP-002 Art 28 | `00-MASTER/UCDA-000001/ucda-decisions.json` | yes — Art 28.15 |
| 3 | Is successor work authorized at all? | CEP-002 Art 28.17–28.21 | Implementation Evidence Gate, UCCEP **G-14** / `CK-DECISION-EVIDENCE` | gate, not a record |
| 4 | Is *this* change authorized, evidenced, gated? | UAUE-000001 | `engine/uaue/execution.py` AUE-P-05 `execute_evolution` | yes — `UAUE-EVOLUTION-HISTORY.json` |
| 5 | Does the change become constitutional truth? | UCOS-CMG-EXEC-000001 | `engine/constitution/gateway.py` `propose` / `apply` | yes — `MutationRecord` hash chain |
| 6 | Is the resulting artifact registered? | REG-AUTO-001 | `00-BOOK/tools/register.sh` (+ `ukb.py enforce`) | yes — immutable id ledger |
| 7 | Is the outcome certified, and by whom? | UCOS-EPIC-006 | `engine/universal_certification` `ApprovalWorkflow` | yes — hash-chained `ApprovalRecord` |

### Layer 3 is currently OPEN — verified, not assumed

CEP-002 Art 28.18 is categorical: *"No subsequent implementation programme, architectural work,
or successor stage SHALL be authorized while any previously ratified or recorded decision IS
undispositioned."* Art 28.20 adds that a CLOSED gate places the programme in HALTED and *"SHALL
NOT be waived, deferred, bypassed, or overridden."*

Executed:

```
UCDA-000001: ASSIMILATED | decisions=113 | undispositioned=0 | conversation_only=0
             | evidence=423 | coverage=94% (278/295) | gate=OPEN | seal=6f4bd4230c7d8e75
```

**`gate=OPEN`, `undispositioned=0`.** Successor work is authorized, so Phase 4 is not blocked at
its root. The run wrote no bytes (`git status` clean for `00-MASTER/UCDA-000001/`) — the engine
is at its fixed point, so this is an observation and not a change.

Had this gate read CLOSED, the correct Phase-4 output would have been a halt, not a design.

## 3. Correction — the mutation gateway is narrower than it appears

`engine/constitution/gateway.py` describes itself as governing *"every mutation of repository
truth"*, and it is genuinely the only producer of a clean `StateSeal`:

> "A population assembled outside this pipeline therefore exists, and can be read, and can be
> printed — and can do none of the five things that would let it become repository truth. The
> bypass path is not blocked by a rule; it is blocked by there being nothing at the end of it."

But its **subject** is a `Population` of `ConstitutionalMetadata` records, and its stages are
pure by construction. Verified:

```
grep -E "open\(|Path\(|read_text|write_text|subprocess" engine/constitution/gateway.py
  -> none — stages are pure, so the gateway cannot edit a source file
```

`StageFunction` is documented as *"Pure — a stage reads no clock, no filesystem and no
network, so a mutation record replays identically."*

**Consequence.** The gateway cannot add `__all__` to a package root, cannot create an
`evidence.py`, cannot add a `--cov=` entry to `pyproject.toml`, and cannot append a `run_stage`
line to `verify.sh`. Those are **source-file changes**, and the gateway's subject is
constitutional metadata. Reading the gateway as a general repository-write authority would be a
category error, and it would be the kind of error that produces a design nothing can implement.

So the honest position is: layers 1–4, 6 and 7 apply to a UICM resolution; **layer 5 applies
only to resolutions whose subject is constitutional metadata** — which, of the nine gap
dimensions, is only `identity` and `governance` (both discharged through UGA's own minting
path, not through the gateway directly).

## 4. Where authorization actually binds, per dimension

| Dimension | Gaps | Change is a… | Governing layers | Layer 5 applies? |
|---|---:|---|---|---|
| identity | 1 | constitutional metadata mint (`id-ledger.json` `by_object`) | 1,2,3,4,6,7 | via UGA's own authority |
| governance | 1 | free rider on identity | as above | as above |
| registry | 3 | root config edit (`pyproject.toml`) | 1,2,3,4,7 | **no** |
| coverage | 3 | free rider on registry | as above | **no** |
| contract | 4 | source edit (`__init__.py`) | 1,2,3,4,6,7 | **no** |
| evidence | 39 | new source module | 1,2,3,4,6,7 | **no** |
| certification | 35 | workflow + `uccep-bindings.json` append | 1,2,3,4,7 | **no** |
| determinism | 42 | `verify.sh` `run_stage` append | 1,2,3,4,7 | **no** |
| evolution | 30 | composite of the above | as above | **no** |

**156 of 158 gaps resolve by source-file change, which no engine mediates.** Execution is a
file edit; the gates validate it *after the fact* (`verify.sh` stages 1–7, `ec1-ci.yml`,
`register.sh --guard`). That is not a defect to fix — post-hoc validation by deterministic
gates is the repository's chosen model — but it must be stated plainly, because it means
"authorized" and "executed correctly" are established by different mechanisms.

## 5. The one thing AUE-P-05 already does, and why it is the right seam

`engine/uaue/execution.py` is the closest existing instrument to a per-resolution authorization
record, and it is explicitly designed to authorize without executing:

> "**This module performs no mutation, and that is its entire security property.** … What this
> phase produces is the *authorisation record*: which mutation path is authorised, under which
> authority, behind which gate, and whether that path resolves with its declared symbols bound."

`EvolutionExecution.mutation_performed` is **always `False`**. Seven preconditions are measured
and every failure is named individually in `refusals` rather than collapsed into a boolean:

```
  no mutation path is declared: there is no authorised way to execute this plan
  the declared mutation path does not resolve: <path>
  … so the authorised path is not the path declared
  the execution gate is not wired: <command>
  the execution phase names no authority
  the object carries no plan, so nothing is authorised to be executed
  the object carries no evidence
  the object is anonymous
```

On success it emits `authorised via <mutation_path> behind <gate> under <authority>`.

**This is the shape a UICM resolution authorization takes.** It names an authority, a path and a
gate; it refuses an anonymous or unevidenced object; and it never writes. UICM would supply the
gap identifier as the subject — it would not build a second authorization engine.

## 6. Disposition vocabulary — correcting an earlier error

Phase 2 (`UICM-RESOLUTION-CAPABILITY-MATRIX.md` §1) referred to the disposition set as
"REUSE/EXTEND/COMPOSE/CREATE". That is wrong. **`COMPOSE` is not in the constitutional set.**
CMG-000001 Art LXXVII.2 declares a five-outcome totality rule, exactly one of which holds for
any concept:

| Outcome | Condition |
|---|---|
| **REUSE** | already owned |
| **EXTEND** | within an existing owner's scope but unaddressed — **EXTEND is the default** |
| **CREATE** | meta-constitutional and unowned; requires the recorded discovery of LXXVI.2(a) |
| **RECORD AS GAP** | substantive and unowned — orphan; route to the competent allocating authority |
| **REJECT** | not constitutional, with recorded reason |

Art LXXVII.4 is the operative constraint on Phase 4: *"An unknown concept SHALL NOT be admitted
by default routing to the nearest owner, the most active program, or the meta layer. Default
routing manufactures parallel authority; explicit disposition prevents it."*

Applied to the two Phase-3 candidates: cross-run continuity is **EXTEND** of UCOS-UICM-000001
(within its own scope, unaddressed), not CREATE. The per-dimension resolution declaration is
likewise **EXTEND**. Neither is a CREATE, and neither may be routed by default.

CEP-002 Art 28.13 carries a **separate and narrower** closed set for *decision* dispositions —
`IMPLEMENTED`, `REPRESENTED-BY-EXISTING-CANONICAL-CAPABILITY`,
`REGISTERED-AS-IMPLEMENTATION-WORK-PACKAGE`, `REJECTED-WITH-CONSTITUTIONAL-JUSTIFICATION`,
`SUPERSEDED` — each with declared `requires_fields`, `located_fields` and `minimum_stage`. The
two vocabularies are different subjects and must not be merged.

## 7. Reuse-before-create determination

| Capability Phase 4 might need | Existing owner | Decision |
|---|---|---|
| Disposition determination | CMG-000001 Art LXXVI/LXXVII | **REUSE AS-IS** — CMG-GAP-09 is already CLOSED by these articles |
| Decision + evidence record | CEP-002 Art 28 / UCDA-000001 | **REUSE AS DATA** — appending a decision requires no engine change |
| Successor-work gate | UCCEP G-14 | **REUSE AS-IS** — verified OPEN |
| Per-change authorization record | UAUE AUE-P-05 | **REUSE AS PATTERN** — supply the gap id as subject |
| Constitutional truth mutation | `engine/constitution/gateway.py` | **REFERENCE** — applies to metadata subjects only |
| Artifact registration | REG-AUTO-001 | **REUSE AS-IS** — "Artifact Creation = Artifact Registration" |
| Certification act + rejection | `engine/universal_certification` | **INVOKE** — `ApprovalWorkflow`, OP-CERT-001 |
| Gate binding for a new check | `uccep-bindings.json` | **REUSE AS DATA** — append `CK-UICM` + a `G-27` entry in the G-22..G-26 form |
| Write-scope vocabulary | `uccep-bindings.json` `checks[].write_scope` | **REUSE AS-IS** — `read-only` / `own-memory` / `projections` |
| Negative write authority | `programme.forbidden_write_prefixes` | **REUSE AS-IS** |
| **Gap-to-authorization binding** | **none located** | **GAP — see §8** |

## 8. The single gap

**No instrument binds a UICM gap identifier to an authorization record.**

`UICM-GAP-*` identifiers exist and are deterministic. `AUE-P-05` produces authorization records
for an *evolution object*. `ucda-decisions.json` records dispositions for a *decision*.
`uccep-bindings.json` binds *checks* to *gates*. Nothing anywhere states "gap
`UICM-GAP-8E3F86206048-04` is authorized for resolution under authority X behind gate Y".

Consequences today:

- a resolution cannot be refused for lacking authorization, because no authorization is required;
- a closed gap carries no record of *who was authorized* to close it — only that it closed;
- two owners could in principle act on the same gap, and nothing would detect it.

The third is the most serious, because Phase 2 established exactly one resolution owner per gap.
That determination is currently a document, not an enforced property.

**This is a binding, not an authority.** Every authority already exists. What is absent is a
declarative statement — of the same kind as `uccep-bindings.json` `checks[]` — connecting a gap
to the owner, path and gate already determined for it in `UICM-GAP-OWNER-MATRIX.md`.

**Disposition under Art LXXVII.2: EXTEND** — of UCOS-UICM-000001, within its own declared scope
and unaddressed. Not CREATE, and not routed by default to UAUE or UCCEP.

## 9. Determination summary

| Discovery item | Finding |
|---|---|
| Resolution authorization path | **EXISTS** as a 7-layer composite; layer 3 (G-14) verified OPEN |
| Constitutional mutation gateway applicability | **NARROW** — metadata subjects only; 156/158 gaps are source changes it cannot govern |
| Per-change authorization record | **EXISTS** — AUE-P-05, `mutation_performed` always False, 7 measured preconditions |
| Disposition vocabulary | **REUSE/EXTEND/CREATE/RECORD-AS-GAP/REJECT** — `COMPOSE` does not exist; Phase 2 corrected |
| Missing capability | **one binding** — gap id → (owner, path, gate). Disposition: EXTEND |
| New authority required | **none** |
| New registry required | **none** |

**No authorization instrument may be created.** The composite is complete and each piece has a
located owner. Phase 4 proposes one declarative binding and nothing else.
