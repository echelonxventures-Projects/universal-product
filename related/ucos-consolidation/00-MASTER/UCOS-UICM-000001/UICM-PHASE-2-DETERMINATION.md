# UICM — Phase 2 Determination

> **Artifact:** `UICM-PHASE-2-DETERMINATION`
> **Programme:** UCOS-UICM-000001 — Phase 2: Gap Resolution Assimilation
> **AUTHORITY = NONE — DERIVED TRUTH.** This determination creates nothing and authorizes
> nothing beyond what §6 explicitly reserves for approval.
> **Disposition:** DISCOVERY COMPLETE. HALTED PENDING APPROVAL.

---

## 1. Determination

**PHASE 2 DISCOVERY IS COMPLETE. NO RESOLUTION REGISTRY IS REQUIRED. NO CODE WAS WRITTEN.**

The objective was *"every implementation gap is known, owned, measurable, and closable"*.
Measured against the committed registers:

| Requirement | Result | Evidence |
|---|---|---|
| Every gap is **known** | 158/158 | `04-CLOSURE-GAP-REGISTER.json` `gap_total: 158`; UICM-INV-10 satisfied (gap count == non-pass cell count), so a hidden gap is structurally impossible |
| Every gap is **owned** | 158/158, exactly one owner each | `UICM-GAP-OWNER-MATRIX.md` §5 — full enumeration; 43 located owners (3 central + 40 capability-local) across 6 instrument classes |
| Every gap is **measurable** | 158/158 | 17 probes in bijection with 17 declared dimensions (UICM-INV-02); 0 cells `BLOCKED`, so no gap is unmeasurable |
| Every gap is **closable** | 158/158 | `UICM-RESOLUTION-GAP-REGISTER.md` §3 — each has an instrument, closing evidence, validation route and declared observation transition |
| No gap requires a **new capability** | confirmed | `UICM-RESOLUTION-CAPABILITY-MATRIX.md` §2 — 14 of 16 requirements already owned |

## 2. What discovery found that changes the plan

Five findings alter what the brief assumed. Each is grounded in a measurement, not an opinion.

**1. The resolution architecture already exists.** `engine/uicm/observation.py`
`ObservationRegistry` satisfies every stated requirement — append-only (measured by
UICM-INV-16, not asserted), immutable frozen records, deterministic derived identity,
explicit lineage, `SUPERSEDED` terminal and *derived* rather than stamped, replay
deterministic. `OPEN → CLOSED` and `CLOSED → CERTIFIED` are already declared transitions.
Creating `09-IMPLEMENTATION-CLOSURE-REGISTER.json` as originally specified would have
duplicated it — and the later steering prohibition against a remediation registry points the
same way.

**2. The only genuine absence is cross-run continuity, and it is small.**
`lineage.max_revision = 3` for all 1054 coordinates, `observation_total = 3162 = 1054 × 3`,
and no loader exists. The register is regenerated whole each run, so a gap that closes leaves
no record it was ever open. This is a loader, not a capability.

**3. Two dimensions have a resolution owner that diverges from their declared source.**
`contract` and `evidence` declare `owner_reference: SRC-CAPABILITY-IDENTITY`, but their
probes read the capability's own package. Editing `knowledge/canonical-knowledge.json` cannot
close either — and it is generated and gitignored. Their resolution owner is the capability's
own UGA path owner.

**4. `UCOS-<CATEGORY>-AUTHORITY` is not an authority.** These strings are synthesized from the
catalogue's `category` field at `engine/knowledge/capability.py:229-232`. They appear nowhere
in `00-CMG/CMG-REGISTRY.json` or any constitutional instrument. Assigning resolution
authority to one would invent an authority, violating principle 10. They are retained as
*accountability* labels only.

**5. The measured state differs from the brief.** 4/62 capabilities are fully closed
(`engine.graph`, `engine.knowledge`, `platform.coverage`, `platform.measurement` — all 17
dimensions `CLOSED`), not 0/62. `fully_closed: false` holds at the population level, which is
what the brief was reporting. The four are the existence proof that the bar is achievable.

## 3. Deliverables produced

Five markdown artifacts under `00-MASTER/UCOS-UICM-000001/`. No JSON register was created. No
engine module was created or modified.

| Artifact | Contents |
|---|---|
| `UICM-RESOLUTION-CONTEXT-REPORT.md` | Discovery 1–5: existing mechanisms, per-dimension owners, instruments, evidence, missing-capability determination |
| `UICM-GAP-OWNER-MATRIX.md` | All 158 gaps enumerated, one located resolution owner each; the two-vocabulary separation |
| `UICM-RESOLUTION-CAPABILITY-MATRIX.md` | Reuse-before-create over 16 requirements; two CREATE candidates; nine explicit refusals |
| `UICM-RESOLUTION-GAP-REGISTER.md` | Per-dimension resolution specification: approach, evidence, validation, verification, expected observation transition; dependency-ordered waves |
| `UICM-PHASE-2-DETERMINATION.md` | This determination |

## 4. Acceptance measured against the stated PASS criteria

| Criterion | Verdict | How measured |
|---|---|---|
| All gaps have owners | **PASS** | 158/158 resolve to exactly one of 43 located owners by a total function of dimension (3 central programmes/authorities cover 115 gaps; 40 capability-local package owners cover 43) |
| All gaps have deterministic IDs | **PASS** | `gap_id = obligation_id.replace("UICM-OBL", "UICM-GAP", 1)`; `obligation_id` derived from capability short identity + dimension ordinal — no counter, no clock, no insertion order |
| No hidden gaps | **PASS** | UICM-INV-10: gap count == count of cells not in a pass state, 158 == 158 |
| No duplicate resolution authority | **PASS** | dimension → resolution owner is a function; 0 gaps with two owners; certification verdict remains solely with `engine/universal_certification` |
| No mutable operations | **PASS** | no existing register was read-modified-written; no file under `engine/uicm/` was touched; `uicm.json` unchanged; UICM-INV-16 still measures mutator absence |
| Replay identical | **PASS (unperturbed)** | none of the five `source_digests` changed, so the matrix digest `8ce37cd19fe42adf26d8832d84bd7106d0c0ccac9e12637727c35f81446c87dc` is unmoved. The five new artifacts are outside the declared `record_set` and are not replay inputs |
| Lineage complete | **PASS within run; INCOMPLETE across runs** | `chain_intact: true`, 1054 coordinates each with full `DISCOVERED → MEASURED → state` lineage. Cross-run lineage is the absence recorded as CREATE-1 — reported rather than claimed |

The last row is deliberately not reported as PASS. Claiming complete lineage while
`max_revision` is 3 on every coordinate would be the unverified claim this programme exists
to refuse.

## 5. USE-STEER-000001 — Universal Secured Entry Boundary

Registered as a **forward architectural obligation**. Not implemented, per the directive's own
non-goals.

### 5.1 Why `SECURED_ENTRY` cannot be added as an 18th dimension now

Adding a dimension is **not** digest-neutral. Verified against the committed declaration:

| Change | Declaration digest | Cells | Effect |
|---|---|---:|---|
| committed (17 dimensions) | `1676f708…12920` | 1054 | baseline |
| additive `resolution` block | `1676f708…12920` | 1054 | **neutral** |
| 18th dimension `secured_entry` | `bd1acb16…3a668` | **1116** | every committed register moves |

An 18th dimension would add 62 cells, require a matching `probe_secured_entry` (UICM-INV-02
enforces probe/dimension bijection, so a declared dimension with no probe fails closed),
re-render all six artifacts in the `record_set`, and move the matrix digest. That is a
Phase-3 architectural determination, not an additive edit, and the frozen UICM architecture
forbids it here.

### 5.2 Secured-entry prior art located — reuse before create

The directive's mandatory discovery requirement is partially discharged here. Substantial
machinery exists; a new gateway would duplicate it.

| Gateway concern | Existing owner | Located implementation |
|---|---|---|
| Access decision point (the composition seam) | EC2-EPIC-002 | `platform/identity/service.py` `AuthorizationService` — composes `PrincipalRegistry · RoleRegistry · PermissionEngine · PolicyEngine · SessionRegistry`; fail-closed; append-only decision log; emits `identity.access.evaluated` |
| Entry gateway (a *composing* gateway, exactly the pattern the directive describes) | EC2-TASK-000074 | `platform/portal/access.py` `PortalAccessGateway` + `PortalAdmission` — "does **not** implement identity — it composes the certified EC-2 Identity Layer"; "there is **no duplicate identity implementation**" |
| Admission gate as a pure fail-closed function | EC2-TASK-000166 | `platform/runtime_operations/guard.py` `RuntimeAdmissionGuard` + `AdmissionDecision` — 7 ordered `ADMISSION_CRITERIA`, admitted only when every criterion passes, no wall clock |
| Identity truth | UCOS-UGA-001 · AIF · UMB-003 · UIS-001 | `00-MASTER/UCOS-UGA-001`, `platform/foundation/durable_identity.py`, `platform/foundation/admission.py` `AdmissionAuthority` / `AdmissionBinder` (AIF-L06/L07/L09/L14) |
| Authentication | EC2-EPIC-002 | `platform/identity/sessions.py` `SessionRegistry` — sessions established from already-authenticated principals; holds no secret material (SEC-04) |
| Authority truth | UCOS-NUC-001 · CEP-003 | `engine/nucleus/ownership.py`; `engine/runtime/execution/authorization.py` `Authorization` (`EXECUTION_AUTHORITY = "ENGINEERING-EXECUTION-ONLY"`) |
| Context truth | Context Layer | `engine/context/` — `resolution.py`, `validation.py`, `evidence.py`, `registry.py` |
| Governance truth | CMG-000001 · UCOS-UGA-001 | `00-CMG/tools/cmg-gate.sh`; `uga_engine.py gate` |
| Integrity truth | UCKP Layer Zero | `engine/uckp/canonical.py` `content_hash` |
| Policy truth | multiple, per domain | `platform/identity/policy.py` `PolicyEngine`; `platform/universal_assurance/policy.py`; `platform/security/` (classification, zones, registries) |
| Evidence truth | Universal Registry Platform | `engine/registry/universal` `EvidenceRegistry` |
| Certification truth | UCOS-EPIC-006 | `engine/universal_certification` |
| Security constitution | SECURITY-001..004 | `14-SECURITY/` |

**Preliminary reuse finding.** Every one of the eight validation stages the directive names
(identity, authentication, authority, context, governance, integrity, policy, evidence) has a
located owner, and two existing gateways already implement the *compose-never-own* pattern
the directive mandates — `PortalAccessGateway` explicitly so. The plausible gap is **not** a
gateway; it is that the existing gateways are scoped to their own surfaces (portal,
runtime operations) with no universal composition boundary across all entry points. That
determination requires its own discovery phase.

**No registry may be created for this.** The directive's own prohibition list — identity
registry, permission registry, security policy registry, authorization database,
authentication authority — matches `uicm.json` `prohibited_creations` and is consistent with
this report.

### 5.3 Registered forward obligations

| ID | Obligation | Status | Blocked by |
|---|---|---|---|
| USE-FWD-01 | Full secured-entry discovery: entry-point inventory, security capability inventory, canonical owner map, reuse analysis, gap determination, creation determination | REGISTERED | own discovery phase |
| USE-FWD-02 | Architectural determination on whether a universal entry composition boundary is a genuine gap given `PortalAccessGateway` / `RuntimeAdmissionGuard` / `AuthorizationService` | REGISTERED | USE-FWD-01 |
| USE-FWD-03 | `SECURED_ENTRY` as an 18th UICM closure dimension, with the seven measured attributes the directive names | REGISTERED | USE-FWD-02; requires unfreezing the UICM declaration (digest-moving, 1054 → 1116 cells) |
| USE-FWD-04 | Inheritance rule: future capabilities inherit secured-entry requirements automatically | REGISTERED | USE-FWD-03 |

**Nothing under USE-FWD-* was implemented.** The directive states implementation requires
completion of discovery and architecture determination; neither is complete.

## 6. What is reserved for explicit approval

Nothing below has been executed. Each requires approval before any action.

| # | Action | Scope | Risk |
|---:|---|---|---|
| A1 | **CREATE-1** — cross-run observation continuity | a loader in `engine/uicm/observation.py`; makes the committed observation registry an input | Touches frozen UICM code. Changes what `--replay` compares. Must preserve the fixed-point property |
| A2 | **CREATE-2** — additive `resolution` block per dimension in `uicm.json` | declaration only, no code | Verified digest-neutral. Lowest risk of anything reserved here |
| A3 | **Wave 1 closure** — `uga_engine.py run` admitting `engine/uckp/resolution.py` and `engine/uckp/uga_projection.py` | closes 2 gaps (identity + governance); the only wave executable today | Mints 2 identities in `00-BOOK/DATA/id-ledger.json`. Append-only, but ledger-affecting and not trivially reversible |
| A4 | **Wave 2** — `pyproject.toml` coverage denominator for `engine`, `engine.constitution`, `platform` | closes 6 gaps (registry + coverage) | **Blocked by the Task-5 freeze.** High blast radius: two are namespace roots, so the denominator enlarges over every subpackage and interacts with `--cov-fail-under=90` |
| A5 | **Wave 6** — `verify.sh` replay bindings | closes up to 42 gaps (determinism) | **Blocked by the Task-5 freeze.** Also: the probe is a substring test, so a binding that does not actually re-run and compare would close the dimension while proving nothing |
| A6 | Waves 3–5, 7 — contract, evidence, certification, evolution | 108 gaps | Wave 7 depends on A4. Wave 5 must use gate binding, not capability-local certification modules |
| A7 | Acceptance tests for the resolution architecture | after A1/A2 only | Per the brief: tests come after the architecture is stable, not before |

## 7. Recommendation

**Approve A2, then A1, then A3. Hold A4–A7.**

The order is not arbitrary. A2 is declarative and digest-neutral, so it can be validated
without risk. A1 makes resolution history durable — and until it exists, closing a gap
destroys the evidence that it was ever open, which is the one outcome this programme cannot
accept. A3 then becomes the first resolution whose before-and-after is actually recorded,
making it the correct proof-of-architecture: two gaps, one owner, one instrument, a
verifiable observation transition.

A4 and A5 should stay held until A1 has demonstrated a durable `OPEN → CLOSED` transition,
because they are the two changes the Task-5 freeze names explicitly and the two with the
largest blast radius.

**Do not begin mass gap elimination.** 146 of 158 gaps sit in four dimensions
(determinism 42, evidence 39, certification 35, evolution 30) whose resolution is genuinely
per-capability work. Attempting them before the architecture is proven would produce 146
changes with no durable record of what they resolved — which is indistinguishable, after the
fact, from making the matrix show closure artificially.

## 8. Status

```
PHASE 2 DISCOVERY          COMPLETE
RESOLUTION REGISTRY        NOT CREATED  (refused - duplicates ObservationRegistry)
ENGINE CODE                NOT WRITTEN
EXISTING REGISTERS         UNMODIFIED
uicm.json                  UNMODIFIED
MATRIX DIGEST              8ce37cd19fe42adf26d8832d84bd7106d0c0ccac9e12637727c35f81446c87dc  (unmoved)
GAPS OWNED                 158 / 158
GAPS CLOSABLE              158 / 158
GAPS CLOSED THIS PHASE     0            (by design)
MISSING CAPABILITIES       2            (both additive, both digest-neutral, neither authorized)
USE-STEER-000001           REGISTERED   (4 forward obligations, 0 implemented)

HALTED PENDING EXPLICIT APPROVAL.
```
