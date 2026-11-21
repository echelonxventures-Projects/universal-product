# UICM — Secured Entry Capability Matrix

> **Artifact:** `UICM-SECURED-ENTRY-CAPABILITY-MATRIX`
> **Programme:** UCOS-UICM-000001 — Phase 5 discovery (USE-STEER-000001)
> **AUTHORITY = NONE — DERIVED TRUTH.**
> **Disposition:** DISCOVERY ONLY. Reuse-first determination. No code. No registry. No admission.
> **Reuse order applied:** existing engine → existing registry → existing framework → existing
> owner → only then create.

---

## 1. The ten requested owners

Every one is located. None needs to be created.

| # | Concern | Canonical owner | Located implementation | Decision |
|---:|---|---|---|---|
| 1 | **Identity** | AIF `A/G-AUTH` (law) — *"exactly one identity authority"* | `platform/foundation/durable_identity.py` `IdentityRegistry` (P2 plane, AIF-L02/L06/L13/L17); `platform/foundation/admission.py` `AdmissionAuthority`/`AdmissionBinder` (AIF-L09/L14); `engine/registry/universal/identity.py` `deterministic_id` (registry plane); `00-MASTER/UIS-001` conformance (G-24) | **REUSE AS-IS** — the two planes are orthogonal and non-substitutable; a merge would amend four owners at once |
| 2 | **Authentication** | **none located** | — | **RECORD AS GAP** — §5 |
| 3 | **Authorization** | EC2-EPIC-002 | `platform/identity/service.py` `AuthorizationService` — L7, composes `PrincipalRegistry · RoleRegistry · PermissionEngine · PolicyEngine · SessionRegistry`; `ACCESS_EVENT = "identity.access.evaluated"` | **REUSE AS-IS** — *"the single, fail-closed access decision point"*; a second is forbidden by name |
| 4 | **Access Gateway** | EC2-TASK-000074 | `platform/portal/access.py` `PortalAccessGateway.admit` → `PortalAdmission`; requires READ on `PORTAL_NAVIGATION` | **REUSE AS PATTERN** — already the compose-never-own pattern the directive mandates |
| 5 | **Runtime Admission** | EC2-TASK-000166 | `platform/runtime_operations/guard.py` `RuntimeAdmissionGuard`; 7 ordered `ADMISSION_CRITERIA`, all must pass | **REUSE AS-IS** — pure function, no wall clock, mutates nothing |
| 6 | **API Gateway** | REF-API-001 §3 | six declared gateways: External · Internal · Partner · Agent · Administrative · Certification | **REFERENCE ONLY** — architecture for a surface that does not exist |
| 7 | **Portal Gateway** | same as #4 | `PortalAccessGateway` | **REUSE AS PATTERN** |
| 8 | **Execution Boundary** | EPIC-RTE-002 | `engine/runtime/execution/authorization.py`; `EXECUTION_AUTHORITY = "ENGINEERING-EXECUTION-ONLY"` | **REUSE AS-IS** — *"grants no capability and runs nothing"* (ORL-15) |
| 9 | **Constitution Gateway** | UCOS-CMG-EXEC-000001 | `engine/constitution/gateway.py`; sole producer of a clean `StateSeal` | **REFERENCE ONLY** — subject is `ConstitutionalMetadata`; stages are pure, so it cannot govern a request or a file (Phase 4 §3) |
| 10 | **Certification Engine** | UCOS-EPIC-006 (Terminal T6) | `engine/universal_certification` — `UniversalCertificationEngine`, `ComplianceEngine`, `ApprovalWorkflow`, `OP-CERT-001` | **INVOKE** — never reimplement |

**Plus the one the request did not name, and which matters most:**

| — | **Work Admission** | **UAPF-000001** | `platform/universal_pipeline/gateway.py` `UniversalPipelineGateway.submit`; *"the single admission point for work"*, *"the one door into execution"* | **REUSE — REPLACEMENT PROHIBITED** |

## 2. The eight directive validation stages

| Stage | Owner | Decision | Note |
|---|---|---|---|
| Identity Validation | AIF / `IdentityRegistry` / `deterministic_id` | **REUSE AS-IS** | minting a new identity here would be the forbidden fifth identifier scheme |
| **Authentication Validation** | **none** | **RECORD AS GAP** | first implementation in the repo; blocked — §5 |
| Authority Validation | `engine/nucleus/ownership.py`; CEP-003 Art I/VIII; UCAF-001 (G-18) | **REUSE AS-IS** | |
| Context Validation | `engine/context/` `resolution.py`, `validation.py` | **REUSE AS-IS** | |
| Governance Validation | CMG-000001 Art L (`cmg-gate.sh`); `platform/universal_pipeline/governance.py` | **REUSE AS-IS** | UAPF already calls `require_approved(verdict)` |
| Integrity Validation | `engine/uckp/canonical.py` `content_hash` | **REUSE AS-IS** | one definition only — UCKP-LAW-0001 Art-13, enforced by AST scan |
| Policy Validation | `platform/identity/policy.py` `PolicyEngine`; `platform/universal_assurance/policy.py` | **REUSE AS-IS** | |
| Evidence Generation | `EvidenceRegistry`; `IdentityEvidence`; `GatewayTransaction.fingerprint()`; SEC-ZONE posture evidence | **REFERENCE / REUSE** | `EvidenceRegistry` is a `prohibited_creation` for UICM |

**Seven of eight are REUSE AS-IS. One does not exist.**

## 3. The directive's ownership rule is already satisfied

USE-STEER-000001 requires that the gateway *"SHALL NOT own"* identity, authority, context,
governance, certification or evidence truth. Every located gateway already complies, and two say so
in their own docstrings:

- `PortalAccessGateway`: *"It does **not** implement identity — it composes the certified EC-2
  Identity Layer… There is **no duplicate identity implementation**."* `__slots__ =
  ("_authorization",)` — it holds no state of its own.
- `UniversalPipelineGateway`: *"It executes nothing itself: admission and execution are separate
  acts, so the thing that decides is not the thing that runs."*
- `RuntimeAdmissionGuard`: *"The guard implements no deployment and mutates nothing."*
- `engine/runtime/execution/authorization.py`: *"it **grants no capability and runs nothing**."*
- `platform/security/zones.py`: *"record-only … it authorizes, ratifies, and enacts nothing."*

The compose-never-own principle is not an aspiration to introduce. It is the existing convention,
stated five times independently.

## 4. Explicit refusals

| Proposed | Verdict | Ground |
|---|---|---|
| A Universal Entry Gateway construct | **REFUSED** | duplicates five located admission points; UAPF-000001 replacement prohibited |
| A second authorization logic | **REFUSED** | `EC2-CAP-SEC-001` §4.3 forbids by name: *"no second authorization logic"* |
| A `Gateway` ontology entity or taxonomy leaf | **REFUSED** | `SECURITY-004 LR-1` — `TAX-L ↔ ONT-E` is a bijection over 32 entities, *"no invented leaf"* |
| A new Universal Security Law | **REFUSED** | USL-001..015 declared *"complete over the domain"*; extensible only as USL-016+ additively |
| A new identity registry | **REFUSED** | AIF `A/G-AUTH` — exactly one identity authority; would be a fifth identifier scheme |
| A new permission registry | **REFUSED** | duplicates `RoleRegistry`/`PermissionEngine`; USL-015 |
| A new security policy registry | **REFUSED** | `platform/security/contracts.py` §17 registries exist, append-only and record-only |
| An authorization database | **REFUSED** | `AuthorizationService` holds an append-only decision log; USL-015 forbids a new registry system |
| An authentication authority | **REFUSED here** | not by merit — by constraint collision (§5). Requires its own determination |
| A seventh API gateway | **REFUSED** | REF-API-001 §3 fixes the set at six |
| `SECURED_ENTRY` as an 18th UICM dimension | **REFUSED (now)** | digest-moving: `1676f708…` → `bd1acb16…`, cells 1054 → 1116; UICM-INV-02 needs a matching probe. USE-FWD-03 remains blocked on USE-FWD-02 |
| Owning any of this inside UICM | **REFUSED** | UICM authority NONE, measurement-only, `prohibited_creations` |

## 5. Authentication — the one absent capability, and why it is not simply a gap to fill

| Property | Finding |
|---|---|
| Does it exist? | **No.** No credential verification anywhere in `engine/` or `platform/` |
| Canonical statement | `platform/identity/service.py:20-21` — *"It authenticates nothing itself — sessions are established from already-authenticated principals — and holds no secret material (SEC-04)."* |
| Structural proof | `Session.establish` takes an already-constructed `Principal`; no challenge, no comparison. `credential_ref` is validated only as *"a non-empty reference string (SEC-04)"* |
| Blocker 1 | **SEC-04** — holds no secret material. Currently honoured by never having a secret |
| Blocker 2 | **`dependencies = []`** — stdlib-only *by constitutional intent* (TP-04, TP-05). No crypto, JWT or TLS library is admissible |
| Blocker 3 | **Nothing to authenticate to** — 31 entry points, all CLI; zero listeners; absence asserted by governance tests |
| Disposition | **RECORD AS GAP** (Art LXXVII.2(d)) — substantive and unowned; route to the competent allocating authority |
| Must NOT be | routed by default to UICM, UAPF or `platform/security` (Art LXXVII.4) |

Authentication is not a missing module. It is a **constitutional question** about SEC-04 and the
zero-dependency posture, and it has no meaning until a request surface exists. Recording it as a
gap is the correct disposition — Art LXXVII.5: *"Holding IS a valid disposition; silent adoption IS
not."*

## 6. The one EXTEND — bind the two permission vocabularies

| | Identity Layer | UAPF |
|---|---|---|
| Owner | EC2-EPIC-002 | UAPF-000001 |
| Vocabulary | typed `CapabilityGroup` + `Permission` | opaque `required_permissions: tuple[str, ...]` |
| Evaluation | `PolicyEngine.evaluate(principal, request)` against the §3.2 RBAC matrix | `missing = sorted(required - set(permissions))` |
| Principal concept | yes — session → principal → policy → decision | **none** |
| Audit | append-only decision log + `identity.access.evaluated` | `uapf.gateway.admitted` / `uapf.gateway.refused` |
| Refusal form | data (`AccessDecision`) | error (recorded, then raised) |

`PipelineSecuritySpec` states the seam deliberately: *"**Declared, not enforced here** … the single
enforcement point stays the gateway and this type stays a declaration."* But the gateway enforces
against **strings it is handed**, not against a principal's actual grants. So the repository's *one
door into execution* does not consult its *single access decision point*.

| Property | Value |
|---|---|
| Nature | a **binding** between two located owners |
| Disposition | **EXTEND** — Art LXXVII.2(b), within existing scope, unaddressed |
| Owners to dispose | `platform/identity` and `platform/universal_pipeline` |
| Not | a new gateway, registry, authority, leaf or law |
| UICM's role | **none** — UICM cannot bind two platform capabilities |
| Authorized by this document? | **no** |

## 7. Evidence model (discovery 6)

Owned by SECURITY-001 §16 at the architecture layer, and already realized four times at the
implementation layer.

**Architecture-layer rules** — SECURITY-001 §16: content-addressed, hash-chained, and the decisive
clause: *"**Absence of evidence is treated as absence of the property** (default-deny, USL-005)."*
That is the same inversion UICM uses (an unasked question has no passing answer), reached
independently.

**Located entry-decision evidence:**

| Producer | Record | Determinism |
|---|---|---|
| `AuthorizationService` | `IdentityEvidence` — `principals_fingerprint`, `roles_fingerprint`, full decision log, derived `permit_count`/`deny_count`; `UCOS-IDEV-<hash16>` | *"the same registrations and the same ordered sequence of calls yield the same decisions and the same fingerprint"* |
| `PortalAccessGateway` | `PortalAdmission` carrying the `AccessDecision` | denials are data, not exceptions |
| `RuntimeAdmissionGuard` | `AdmissionDecision` — 7 criteria, ordered `blockers`, `fingerprint()`; `UCOS-ROAD-<hash16>` | pure function, no wall clock |
| `UniversalPipelineGateway` | `GatewayTransaction` — `authorization` recomputable via `authorization_for(core)`; `fingerprint()` | no counter, no clock, no nonce |
| SEC-ZONE | zone/control posture evidence | content-addressed, logical ticks |

Every one is deterministic and content-addressed. **No new evidence model is required** — and
`EvidenceRegistry` remains the storage owner, a `prohibited_creation` for UICM.

## 8. Verification model (discovery 7)

| Layer | Owner | Requirement |
|---|---|---|
| Boundary invariants | SECURITY-003 §37 | **BD-INV-1** single demarcation · **BD-INV-2** crossing requires an explicit, typed, evidenced reference, default-deny otherwise · **BD-INV-3** every crossing governed by an explicit `Policy` |
| Cross-cutting | SECURITY-003 | `RM-5` no relationship crosses a `Boundary` without an evidenced crossing · `TRR-6` boundary default-deny |
| Theory | SECURITY-002 §24 | `A-Bnd-1` exactly one declared boundary per isolation domain · `A-Bnd-2` cross-boundary interaction requires an evidenced reference |
| Zone direction | UMB-015 | **UMB-INV-01** — *"Higher zones may read outward; lower zones never mutate inward. Canon (ZONE-0/1/2) is never mutated by ZONE-3/4."* |
| Testing | ARCH-SECURITY-001 §16 | Security · Penetration · Vulnerability · Identity · Authorization testing; *"Tests gate merges (CD-02)"* |
| Failure conditions | ARCH-SECURITY-001 §19 | generation SHALL FAIL without Identity Model · Trust Model · Traceability · Testing · Observability · Certification · Governance |

**No new verification model is required.** The directive's seven measured attributes map onto
existing invariants: *entry boundary exists* → `A-Bnd-1`/`BD-INV-1`; *identity validated* → AIF
planes; *authority validated* → G-18; *context bound* → `BD-INV-3` policy-governed crossing;
*integrity verified* → UCKP Art-13; *evidence produced* → SECURITY-001 §16; *refusal behaviour
validated* → USL-005 + `defaultCrossing = deny`.

## 9. Evolution lifecycle (discovery 8)

Owned by SECURITY-001, and it is append-only in the same sense UICM's registers are.

| Aspect | Rule |
|---|---|
| Lifecycle (§11) | `DEFINED → SPECIFIED → VALIDATED → CERTIFIED → RATIFIED → FROZEN` |
| Freeze tiers | `SF-1 → SF-2 → SF-3`, forward-only |
| Correction | **supersession-only** — never edit |
| Evolution (§20) | append-only · supersession-only · backward traceability mandatory · **no constitutional mutation** · non-terminal and unbounded |
| USL-015 | no new primitive, authority, registry system, identifier scheme or lifecycle |
| Law extension | additively as `USL-016…`, *"never by rewrite"* |
| Admission slot | `SECURITY-GOV-000` OUTPUT 13 — concern architectures, after SL-4 Meta-Model |

**Current chain state:** `14-SECURITY/` holds only `SECURITY-GOV-000` and `SECURITY-001..004`.
`SECURITY-005` (SL-4 Meta-Model) **does not exist**, and no concern architecture exists. So the
lawful slot for a secured-entry concern architecture is real but sits **downstream of two unwritten
artifacts** — which is itself a reason not to attempt it now.

The directive's *"Unknown future capabilities SHALL automatically inherit Universal Secured Entry
requirements"* is already discharged: USL-004/005/006 are unconditional over the domain, and
`Boundary.defaultCrossing` is **fixed** at `deny`. Inheritance is not a mechanism to build — it is
the default-deny posture already in force.

## 10. Reuse summary

| Decision | Count |
|---|---:|
| REUSE AS-IS | 8 |
| REUSE AS PATTERN | 2 |
| REFERENCE ONLY | 3 |
| INVOKE | 1 |
| **EXTEND** | **1** — Identity ↔ UAPF permission binding |
| **RECORD AS GAP** | **1** — authentication |
| **CREATE** | **0** |
| **REJECT** | **1** — a Universal Entry Gateway construct |

## 11. Determination

**NO CAPABILITY MAY BE CREATED. FOURTEEN OF SIXTEEN CONCERNS ARE DISCHARGED BY AN EXISTING OWNER.**

The two that are not are neither of them a gateway: one is a **binding** between two located owners
(EXTEND, for those owners to dispose), and one is **authentication** (RECORD AS GAP, blocked by
SEC-04, the zero-dependency posture, and the absence of any surface to authenticate to).

Neither is authorized by this document, and neither belongs to UICM.
