# UICM — Secured Entry Surface and Principle Determination

> **Artifact:** `UICM-SECURED-ENTRY-SURFACE-AND-PRINCIPLE-DETERMINATION`
> **Programme:** UCOS-UICM-000001 — Phase 5 discovery completion (USE-STEER-000001)
> **AUTHORITY = NONE — DERIVED TRUTH.**
> **Disposition:** DISCOVERY ONLY. No implementation. No gateway. No registry. No capability. No
> identity. No authority. No constitution created — see §5 for why the condition was not met.
> Completes `UICM-SECURED-ENTRY-CONTEXT-REPORT`, `UICM-UNIVERSAL-ENTRY-GATEWAY-DETERMINATION`,
> `UICM-SECURED-ENTRY-CAPABILITY-MATRIX`, `UICM-PHASE-5-DETERMINATION`.

---

## 1. Constitutional ownership of the Universal Secured Entry Principle

### 1.1 Existing law and source

The principle is fully stated across six instruments. Nothing about it is novel.

| Element of the principle | Existing law | Source |
|---|---|---|
| no implicit trust of any boundary | **USL-004 Zero Trust** — *"No principal, construct, **boundary**, or channel is trusted implicitly. Trust is explicitly established from evidence, scoped, and continuously re-verified."* | SECURITY-001 §6 |
| refusal is the default | **USL-005 Default Deny** — *"In the absence of an explicit, evaluable authorization, the decision is **deny**. Ambiguity resolves to denial, never to permit."* | SECURITY-001 §6 |
| every entry explicitly authorized | **USL-006 Explicit Authorization** — *"Every **access** is the result of an explicit, decidable authorization referencing a principal, a resource, an action, a context, and a policy."* | SECURITY-001 §6 |
| layered controls across boundaries | **USL-009 Defense in Depth** | SECURITY-001 §6 |
| the gateway owns no truth | **USL-002 Reuse by Reference** + **USL-013 Authority Non-Mintage** | SECURITY-001 §6 |
| no duplicate registry/identity/lifecycle | **USL-015 Non-Constitutive** | SECURITY-001 §6 |
| a boundary exists and denies by default | `Boundary` **`ONT-E-24`** — attribute `defaultCrossing` **fixed = `deny`**; `crossingPolicyRef` mandatory | SECURITY-003 §37 |
| crossing requires evidence | **BD-INV-2** *"Cross-boundary interaction requires an explicit, typed, evidenced reference; default-deny otherwise"* | SECURITY-003 §37 |
| crossing requires policy | **BD-INV-3** *"Every crossing is governed by an explicit `Policy`"* | SECURITY-003 §37 |
| exactly one boundary per domain | **A-Bnd-1**, **A-Bnd-2** | SECURITY-002 §24 |
| classification of the boundary | **`TAX-L-24`** Boundary (family `ProtectionObject`); `TAX-L-07` TrustBoundary; `TAX-L-23` Isolation | SECURITY-004 |
| trust boundaries as architecture | §7 Trust Architecture Model — *"All trust is explicitly validated — no implicit trust is granted"* | ARCH-SECURITY-001 |
| authorization as architecture | §6 Authorization Architecture Model (RBAC · ABAC · PBAC · least privilege · SoD · JIT) | ARCH-SECURITY-001 |
| zone/write-path entry control | Access control = *"zone membership + write path"*, under **UMB-INV-01** | UMB-015 §2 |

### 1.2 Canonical owner

**`14-SECURITY/SECURITY-001-UNIVERSAL-SECURITY-CONSTITUTION.md` — the declared supreme
constitutional document of the UCOS Ω∞ Universal Security Domain (SL-0).**

Its own header records the ownership posture that governs any successor work:

- all four authority fields are `NONE` — CONSTITUENT, GOVERNANCE, RATIFICATION, EC-1;
- *"Every conclusion recorded here is a **technical, non-constitutive** governance record (ID-01, AUTH-06)"*;
- *"It contains **no implementation, no runtime, no enforcement logic**"*;
- §6 closes the law set: *"USL-001…015 are complete over the domain … and non-overlapping in
  obligation. Any future law is admitted **additively** (USL-016…), never by rewrite."*

Subordinate owners, by layer:

```
LAW              SECURITY-001 §6            USL-004/005/006/009/002/013/015
SEMANTICS        SECURITY-003 §37           Boundary ONT-E-24 (defaultCrossing = deny)
THEORY           SECURITY-002 §24           A-Bnd-1, A-Bnd-2
CLASSIFICATION   SECURITY-004               TAX-L-24 / TAX-L-07 / TAX-L-23  (LR-1 bijection)
ARCHITECTURE     ARCH-SECURITY-001 §6/§7    Authorization · Trust Boundaries   (§21 no invention)
GOVERNANCE       UMB-015 §2 + UMB-INV-01    zone membership + write path  ->  SEC-ZONE (record-only)
API SURFACE      REF-API-001 §3             six gateways (architecture only)
CERTIFICATION    SECURITY-001 §13           five tiers, incl. Runtime Compliance  ->  SEC-CERT
```

### 1.3 Enforcement points

SECURITY explicitly does **not** enforce. **USL-014**: *"any enforcement is delegated **by
reference** to already-frozen, certified lower-layer mechanisms."* `EC2-CAP-SEC-001` §3.3 names the
delegate: `platform.identity.AuthorizationService`, *"the **single, fail-closed access decision
point**"*.

Five located enforcement points, each fail-closed:

| # | Enforcement point | Enforces | Refusal |
|---:|---|---|---|
| 1 | `platform/identity/service.py` `AuthorizationService.authorize` | typed permission over the §3.2 RBAC matrix | data (`AccessDecision`), 3 pre-policy deny reasons |
| 2 | `platform/universal_pipeline/gateway.py` `UniversalPipelineGateway.submit` | 4 ordered conditions on a work unit | error — recorded, then raised |
| 3 | `platform/portal/access.py` `PortalAccessGateway.admit` | READ on `PORTAL_NAVIGATION` | data (`PortalAdmission`) |
| 4 | `platform/runtime_operations/guard.py` `RuntimeAdmissionGuard.evaluate` | 7 `ADMISSION_CRITERIA`, all must pass | data (`AdmissionDecision`) |
| 5 | `engine/runtime/execution/authorization.py` `authorize` | EC-1 disclosure present; foreign authority rejected | raise |

## 2. Entry surface inventory

Seven surfaces. Enumerated empirically, not from documentation.

### 2.1 CLI — the only live entry surface, and it is unguarded

| Column | Value |
|---|---|
| **Entry Point** | 31 `[project.scripts]` console entry points; 29 are `<pkg>.cli:main`, plus `ec1-frozen-guard` and `ec1-determinism` (also CLI tools) |
| **Existing Guard** | **NONE.** 0 of 31 target modules reference any identity or authorization symbol. Three grep hits were prose, not guards: `ec1-determinism` matched a comment (*"never a production credential (SEC-04 — production uses `env://`)"*), `ucos-uapf` matched *"admits no new pipeline types"*, `ucos-provider` matched nothing on re-check |
| **Identity Owner** | none inside UCOS — the OS process identity is the de facto subject; no `Principal` is bound |
| **Authorization Owner** | none — filesystem permissions are the effective boundary |
| **Admission Owner** | none |
| **Evidence Source** | none at entry; each programme emits its own evidence after the fact |
| **Verification Method** | none at entry. `verify.sh` validates *outcomes*, not entries |

This is the sharpest finding in the inventory. The one surface a caller can actually reach has no
entry guard, no principal, and no admission record. For a local developer toolchain that is
defensible — but no instrument states that it is intended, and USL-006 ("every access is the result
of an explicit, decidable authorization") is unsatisfied here on its face.

### 2.2 API — does not exist

| Column | Value |
|---|---|
| **Entry Point** | **none.** 0 listeners; `dependencies = []`; absence asserted by 4 governance suites (`assert "http.server" not in source`) |
| **Existing Guard** | N/A |
| **Identity / Authorization / Admission Owner** | REF-API-001 §3 (six gateways) and ARCH-API-001 §6 (*"No network-exposed API ships without authentication and authorization (SEC-02)"*) — **architecture for a surface that does not exist** |
| **Evidence Source** | N/A |
| **Verification Method** | N/A — the governance suites verify the surface stays absent |

### 2.3 Runtime — two distinct boundaries

**(a) Execution authorization**

| Column | Value |
|---|---|
| **Entry Point** | `engine/runtime/execution/authorization.py::authorize(composition, subject=…)` |
| **Existing Guard** | EC-1 provisional-state disclosure must be present, else `ExecutionAuthorizationError`; `require_authorization` rejects `not granted` **or** a foreign authority |
| **Identity Owner** | content-addressed — `sha256(composition_id ‖ subject ‖ authority)[:16]` → `UCOS-EXEC-AUTH-…`; `subject` documented as *"a non-secret identifier"* |
| **Authorization Owner** | EPIC-RTE-002; `EXECUTION_AUTHORITY = "ENGINEERING-EXECUTION-ONLY"` |
| **Admission Owner** | same module — admission and execution are separate (*"grants no capability and runs nothing"*, ORL-15) |
| **Evidence Source** | `Authorization` record, `AUTHORIZATION_FORMAT = "ucos-execution-authorization/1.0.0"`; logged `runtime.execution.authorized` |
| **Verification Method** | `require_authorization`; ORL-22 / IP-01 / DE-05 — confers no constitutional finality |

**(b) Deploy / rollback admission**

| Column | Value |
|---|---|
| **Entry Point** | `platform/runtime_operations/guard.py::RuntimeAdmissionGuard.evaluate` |
| **Existing Guard** | 7 ordered `ADMISSION_CRITERIA`: `certification-present · certified · target-matches-unit · blueprint-matches-unit · disclosure-present · package-pinned · closure-present`; `admitted = all(...)` |
| **Identity Owner** | `runtime_id` / `target_id` / `blueprint_id` equality checks; identity supplied by the assembled `RuntimeUnit` |
| **Authorization Owner** | the Certification Console (`CertificationConsoleRecord`), consumed **by reference** |
| **Admission Owner** | EC2-TASK-000166 |
| **Evidence Source** | `AdmissionDecision` — ordered `blockers`, `fingerprint()`, `UCOS-ROAD-<hash16>` |
| **Verification Method** | pure function of unit + certification; no wall clock, so re-evaluation is deterministic |

### 2.4 Portal

| Column | Value |
|---|---|
| **Entry Point** | `platform/portal/access.py::PortalAccessGateway.admit` (data) / `require_admission` (raises) |
| **Existing Guard** | `Permission.READ` on `CapabilityGroup.PORTAL_NAVIGATION` — §3.2 row 0 |
| **Identity Owner** | `platform/identity` `PrincipalRegistry` + `SessionRegistry` — **composed, never owned**: *"There is **no duplicate identity implementation**"* |
| **Authorization Owner** | `AuthorizationService` (L7, EC2-EPIC-002) |
| **Admission Owner** | EC2-TASK-000074 |
| **Evidence Source** | `PortalAdmission` carrying the full `AccessDecision`; `identity.access.evaluated` event; append-only decision log; `IdentityEvidence` (`UCOS-IDEV-<hash16>`) |
| **Verification Method** | portal governance suites; *"denials are data, not exceptions"* — so a denial is inspectable |

### 2.5 Workflow — two distinct boundaries

**(a) Pipeline work admission**

| Column | Value |
|---|---|
| **Entry Point** | `platform/universal_pipeline/gateway.py::UniversalPipelineGateway.submit` — *"the one door into execution"* |
| **Existing Guard** | 4 checks in fixed order: `unit_id` well-formed → pipeline **version registered** → **permissions** held → **governance approved** |
| **Identity Owner** | `platform/universal_pipeline/identity.py::mint("transaction", …)`; idempotent, no counter/clock/nonce (AIF-L13) |
| **Authorization Owner** | **the gateway itself, over opaque strings** — `missing = sorted(required - set(permissions))`. It does **not** consult `AuthorizationService`. This is the located gap (§3.5) |
| **Admission Owner** | UAPF-000001 — declared `REUSE`, *"replacement is prohibited"* |
| **Evidence Source** | `GatewayTransaction` with recomputable `authorization_for(core)`; `fingerprint()`; events `uapf.gateway.admitted` / `uapf.gateway.refused` (refusal recorded **before** raising, so the attempt is auditable) |
| **Verification Method** | `require_authorized()` → `PipelineGatewayError("gateway authorization does not match the transaction (bypass attempt)")`. Bypass is *"impossible"* because a caller cannot manufacture a valid authorization without performing the same checks |

**(b) CI gate execution**

| Column | Value |
|---|---|
| **Entry Point** | 28 `.github/workflows/*.yml` |
| **Existing Guard** | per-check binding in `uccep-bindings.json` — `write_scope` ∈ {`read-only`, `own-memory`, `projections`}, `tier`, `fail_closed`, `exit_semantics` (`0` PASS · `1` FINDINGS · `2` FAIL-CLOSED ABORT) |
| **Identity Owner** | the CI runner — outside UCOS |
| **Authorization Owner** | CMG-DLG-40 enforcement machinery |
| **Admission Owner** | UCCEP-000000 aggregate gates (G-14, G-15, G-18, G-22..G-26) |
| **Evidence Source** | gate reports and `findings[]` |
| **Verification Method** | `uccep-gate.yml` as *"the AGGREGATE constitutional gate, and the authoritative backstop"*; a gate with no bound check is itself a finding |

### 2.6 Repository mutation — four boundaries, one of them absent

| Sub-surface | Entry Point | Existing Guard | Evidence | Verification |
|---|---|---|---|---|
| constitutional metadata | `engine/constitution/gateway.py` `propose` / `apply` | 7-stage pipeline; `Mutation.authority` **mandatory** (*"a mutation must name the authority it acts under"*); sole producer of a clean `StateSeal` | `MutationRecord` hash chain, `refused_at`, `MutationRefused` clause CEL-04 | `require_fixed_point`; `chain_is_intact()` |
| frozen corpus | any write to `00-BOOK/` `00-SOURCE/` `99-FREEZE/` | `find_frozen_writes` / `assert_no_frozen_write` → `SecurityViolation` (DP-03); CLI `ec1-frozen-guard` | the guard's violation list | `ec1-ci.yml` DP-03 step over the resolved diff, **fails closed** if no base resolves |
| artifact registration | `00-BOOK/tools/register.sh` | REG-AUTO-001 atomic 10-phase; `ukb.py enforce --pre` then post; `--guard` **exit 3** on drift | immutable id ledger; enforcement audit record | `ukb.py validate` — duplicate ids, page overlap, referential integrity |
| **source files** | any edit to `engine/**`, `platform/**`, `pyproject.toml`, `verify.sh` | **NONE** — verified Phase 4. These paths are unfrozen and (for `.toml`/`.sh`) unregistered | none at entry | post-hoc only: `verify.sh`, `ec1-ci.yml`, `register.sh --guard` |

Identity / Authorization / Admission owners for the first three: UCOS-CMG-EXEC-000001,
`engine/foundation/guards`, and REG-AUTO-001 respectively. For the fourth: **none** — this is the
surface through which 156 of 158 UICM gap resolutions must pass.

### 2.7 External integration

| Column | Value |
|---|---|
| **Entry Point** | `git` invoked via `subprocess` (35 modules, mostly tests). **No other external boundary exists** |
| **Existing Guard** | argv-fixed invocation; **no `shell=True` anywhere** — `platform/repository_operations/commands.py`: *"The runner never uses `shell=True` and only ever receives an argv resolved from…"* a fixed table |
| **Identity Owner** | none — inherits the OS process identity |
| **Authorization Owner** | none |
| **Admission Owner** | none |
| **Evidence Source** | none at the boundary; command outputs feed programme evidence |
| **Verification Method** | absence of shell interpolation is the guarantee; injection is structurally unavailable |
| **Outbound network** | **none** — no `urllib`, `http.client`, `requests`, `ssl`, `smtplib`, `ftplib`, `paramiko` or `boto3` in production code |

### 2.8 Inventory summary

| Surface | Live? | Guarded? | Identity bound? | Admission record? |
|---|---|---|---|---|
| CLI | **yes** | **no** | no | no |
| API | no | n/a | n/a | n/a |
| Runtime — execution | yes | yes | content-addressed | yes |
| Runtime — deploy/rollback | yes | yes | unit identity | yes |
| Portal | yes | yes | principal + session | yes |
| Workflow — pipeline | yes | yes | transaction identity | yes |
| Workflow — CI | yes | yes | runner (external) | gate report |
| Repo — metadata | yes | yes | authority named | yes |
| Repo — frozen corpus | yes | yes | n/a (path rule) | violation list |
| Repo — registration | yes | yes | id ledger | audit record |
| **Repo — source files** | **yes** | **no** | no | no |
| External — git | yes | argv-fixed | no | no |

**Ten of twelve boundaries are guarded. The two that are not are the two that are actually used by a
human or an agent: the CLI, and direct source-file editing.**

## 3. Gap determination

Classified only as REUSE / EXTEND / CREATE / RECORD AS GAP / REJECT, per the constraint.

| # | Concern | Classification | Owner it routes to |
|---:|---|---|---|
| 1 | Universal Secured Entry **Principle** | **REUSE** | SECURITY-001 §6 — USL-004/005/006/009 |
| 2 | Entry **boundary** as an entity | **REUSE** | SECURITY-003 §37 `Boundary` `ONT-E-24` / `TAX-L-24` |
| 3 | Boundary **crossing** rule | **REUSE** | BD-INV-2 / BD-INV-3 / `TRR-6` / `RM-5` / A-Bnd-1 / A-Bnd-2 |
| 4 | Entry **enforcement** | **REUSE** | `AuthorizationService` — the single fail-closed decision point |
| 5 | **Work** admission | **REUSE** | UAPF-000001 (replacement prohibited) |
| 6 | **Portal** admission | **REUSE** | `PortalAccessGateway` |
| 7 | **Runtime** admission | **REUSE** | `RuntimeAdmissionGuard` (7 criteria) |
| 8 | **Execution** boundary | **REUSE** | EPIC-RTE-002 `EXECUTION_AUTHORITY` |
| 9 | **Metadata** mutation boundary | **REUSE** | UCOS-CMG-EXEC-000001 |
| 10 | **Frozen corpus** boundary | **REUSE** | `FROZEN_PREFIXES` / DP-03 / `ec1-frozen-guard` |
| 11 | **Registration** boundary | **REUSE** | REG-AUTO-001 |
| 12 | **Zone / write-path** control | **REUSE** | UMB-015 §2 + UMB-INV-01 → SEC-ZONE |
| 13 | Entry **evidence** model | **REUSE** | SECURITY-001 §16 + 5 located deterministic producers |
| 14 | Entry **verification** model | **REUSE** | ARCH-SECURITY-001 §16/§19 + the boundary invariants |
| 15 | Entry **certification** | **REUSE** | SECURITY-001 §13 Runtime tier / SEC-CERT / `engine/universal_certification` |
| 16 | Entry **evolution** lifecycle | **REUSE** | SECURITY-001 §11/§20 — append-only, supersession-only |
| 17 | **Identity ↔ UAPF permission binding** | **EXTEND** | `platform/identity` + `platform/universal_pipeline` — referred, not queued |
| 18 | **CLI entry guard** | **RECORD AS GAP** | substantive, unowned — §3.4 |
| 19 | **Source-file mutation guard** | **RECORD AS GAP** | substantive, unowned — Phase 4 EG-02 |
| 20 | **Authentication** | **RECORD AS GAP** | blocked by SEC-04 + `dependencies = []` + no surface |
| 21 | API entry boundary | **REJECT** | no surface exists; REF-API-001 §3 already fixes the set at six |
| 22 | A Universal Entry **Gateway construct** | **REJECT** | duplicates 5 located admission points; 4 independent grounds |
| 23 | A second authorization logic | **REJECT** | `EC2-CAP-SEC-001` §4.3 forbids by name |
| 24 | A `Gateway` ontology entity / taxonomy leaf | **REJECT** | `SECURITY-004 LR-1` bijection over 32 entities |
| 25 | A new Universal Security Law by rewrite | **REJECT** | USL-001..015 complete; additive as USL-016+ only |

**Totals: 16 REUSE · 1 EXTEND · 0 CREATE · 3 RECORD AS GAP · 5 REJECT.**

### 3.4 The two newly-recorded gaps

**GAP-USE-01 — CLI entry is unguarded.** 31 entry points, zero identity binding, zero admission
record. No instrument states whether this is intended. USL-006 requires every access to be *"the
result of an explicit, decidable authorization referencing a principal, a resource, an action, a
context, and a policy"*; the CLI satisfies none of the five. Disposition **RECORD AS GAP** (Art
LXXVII.2(d)) — substantive and unowned. Must **not** be routed by default (Art LXXVII.4). The likely
correct resolution is a *declaration* that the CLI is a trusted-operator surface whose boundary is
the OS process — but that is a determination for a security concern architecture, not for UICM.

**GAP-USE-02 — source-file mutation is unguarded.** Already surfaced in Phase 4 as EG-02 and
re-recorded here as an entry-surface gap. `pyproject.toml` and `verify.sh` are outside every frozen
prefix and are not registered artifacts, so no mechanism objects to an edit. 48 UICM gaps sit behind
those two files.

### 3.5 The one EXTEND

`UniversalPipelineGateway` — *"the one door into execution"* — admits work by comparing **opaque
strings** (`missing = sorted(required - set(permissions))`) and never consults
`AuthorizationService`, the repository's *single fail-closed access decision point*. Two permission
vocabularies exist and nothing joins them. `PipelineSecuritySpec` confirms the seam is deliberate:
*"**Declared, not enforced here**."*

Disposition **EXTEND** (Art LXXVII.2(b)). Owners: `platform/identity` (EC2-EPIC-002) and
`platform/universal_pipeline` (UAPF-000001). **Referred to them; not authorized here, and not
UICM's to allocate.**

## 4. Is a constitutional artifact missing?

Tested honestly in both directions.

### 4.1 The case that something is missing

- No single instrument states the **composite** proposition "no execution entry without a validated
  boundary" as one normative claim. USL-004/005/006/009 are *per-property*, not *per-surface*.
- No instrument **enumerates entry surfaces**. §2 of this document appears to be the first such
  inventory.
- Two live surfaces (CLI, source-file mutation) are unguarded and **no instrument says whether they
  should be**.

### 4.2 The case that nothing is missing — and why it prevails

1. **The law set is declared complete.** SECURITY-001 §6: *"USL-001…015 are complete over the domain
   … and non-overlapping in obligation."* A completeness claim by the supreme instrument of the
   domain is not something a derived-truth programme may contradict.
2. **The default-deny posture is already universal.** `Boundary.defaultCrossing` is **fixed** at
   `deny`, and BD-INV-2/BD-INV-3 already bind *every* boundary to evidenced, policy-governed
   crossing. Universality is already the case; it does not need re-declaring.
3. **The extension mechanism is already specified, and it is not a new constitution.** *"Any future
   law is admitted **additively** (USL-016…), **never by rewrite**."* The lawful form of a composite
   entry law is **USL-016 inside SECURITY-001's successor**, not a standalone instrument.
4. **A second security constitution would be parallel authority.** SECURITY-001 is *"the supreme
   constitutional document of the UCOS Ω∞ Universal Security Domain"*. A "Universal Secured Entry
   Principle Constitution" would sit beside it, restating USL-004/005/006/009 — the parallel
   authority CMG-INV-02 forbids and CMG-L-14 forbids as parallel machinery.
5. **`ARCH-SECURITY-001` §21: *"No security invention is authorized."***
6. **USL-015** — a new constitution declaring its own lifecycle would introduce a new lifecycle,
   which is forbidden by name.

### 4.3 The decisive point — UICM cannot author a constitution

Even if §4.1 prevailed, UICM would be the wrong author, and provably so:

| Constraint | Value | Consequence |
|---|---|---|
| `programme.authority` | `"NONE (DERIVED TRUTH)"` | cannot legislate |
| `programme.classification` | `"SUBSTANTIVE"` | CMG Art LXXVI.2(b) — *"a substantive concept SHALL NOT be admitted"* to the meta-constitutional layer |
| `programme.namespace_token` | `None` | *"the programme is SUBSTANTIVE, so CMG-000001 Article LXXVI.2(b) forbids its admission"* |
| `programme.disclosure` | *"This programme **legislates no lifecycle**, mints no identifier, opens no registry"* | a constitution is precisely a lifecycle-legislating instrument |
| `programme.disposition` | `"MEASUREMENT AND CERTIFICATION LAYER ONLY"` | out of scope |

A constitution authored by a programme whose authority is NONE would be void on its face — and
worse, it would be the first instrument in the corpus to claim authority it had declared it did not
have.

### 4.4 Determination

**NO CONSTITUTIONAL ARTIFACT IS MISSING. THE CONDITION FOR CREATION IS NOT MET, SO
`UNIVERSAL SECURED ENTRY PRINCIPLE CONSTITUTION` HAS NOT BEEN CREATED.**

The instruction was conditional — *"If missing: create ONLY: UNIVERSAL SECURED ENTRY PRINCIPLE
CONSTITUTION"*. The condition evaluates false on six grounds, and the author would in any case be
constitutionally incapable. Creating it would have breached four of this phase's own constraints: no
invented authority, canonical owners only, no new capability, and every conclusion citing an existing
owner.

### 4.5 What would be created, by whom, if it is wanted anyway

Recorded so the request can be directed to the competent owner rather than refused flatly.

| Question | Answer |
|---|---|
| Lawful form | **`USL-016`** — an additive law inside SECURITY-001's successor, stating the composite entry proposition and binding it to the surface inventory. *Not* a standalone constitution |
| Alternative lawful form | a **`SECURITY-*` concern architecture** under `SECURITY-GOV-000` OUTPUT 13 — nearest declared concerns: **Authorization & Access**, **Trust Model**, **Secure Execution Model** |
| Lawful author | the **SECURITY programme** (SL-0 chain), never UICM |
| Prerequisite | the chain is largely ungenerated — `14-SECURITY/` holds only `SECURITY-GOV-000` and `SECURITY-001..004`. **`SECURITY-005` (SL-4 Meta-Model) does not exist**, and no concern architecture exists. A concern architecture is downstream of two unwritten artifacts |
| Mandatory properties | additive · evaluative · **non-enforcing** (USL-014) · mints no entity, leaf, registry, identifier or lifecycle (USL-015, LR-1) |
| What it may add | the **surface inventory** (§2) and dispositions for **GAP-USE-01** and **GAP-USE-02** — genuinely absent content that duplicates nothing |

That last row is the honest residue: the *principle* needs no new instrument, but the *surface
inventory and the two unguarded surfaces* have no home. That is a concern-architecture gap, and it
belongs to SECURITY.

## 5. Halt

```
PHASE 5 DISCOVERY              COMPLETE
CONSTITUTIONAL ARTIFACT        NOT MISSING  -> NOT CREATED (condition false; 6 grounds)
UNIVERSAL ENTRY GATEWAY        NOT IMPLEMENTED
GATEWAY ENGINE                 NOT CREATED
SECURITY REGISTRY              NOT CREATED
AUTHENTICATION SERVICE         NOT CREATED
AUTHORIZATION ENGINE           NOT CREATED
NEW REGISTRY / CAPABILITY /
  IDENTITY / AUTHORITY         NONE

ENTRY SURFACES INVENTORIED     7 categories, 12 distinct boundaries
  guarded                      10
  unguarded                    2   (CLI; direct source-file mutation)
  non-existent                 1   (API)

CLASSIFICATION                 16 REUSE · 1 EXTEND · 0 CREATE · 3 RECORD AS GAP · 5 REJECT
NEWLY RECORDED GAPS            GAP-USE-01 (CLI entry unguarded)
                               GAP-USE-02 (source-file mutation unguarded; = Phase-4 EG-02)
                               authentication (carried)
REFERRED, NOT QUEUED           Identity <-> UAPF permission binding (EXTEND)

PRINCIPLE OWNER                SECURITY-001 §6 (SL-0) — USL-004/005/006/009
ENFORCEMENT DELEGATE           platform/identity AuthorizationService (USL-014 by reference)
LAWFUL FUTURE FORM             USL-016 additive law, or a SECURITY-* concern architecture
LAWFUL AUTHOR                  the SECURITY programme — never UICM (authority = NONE)

uicm.json                      UNMODIFIED   (17 dimensions; no 18th)
FROZEN SURFACE                 UNMODIFIED
MATRIX DIGEST                  8ce37cd19fe42adf26d8832d84bd7106d0c0ccac9e12637727c35f81446c87dc
UICM GAPS                      158 open, 0 closed this phase (by design)

HALTED BEFORE IMPLEMENTATION. Prior approval request unchanged: M1 + M2 only.
```
