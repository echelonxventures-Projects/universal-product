# UICM — Secured Entry Context Report

> **Artifact:** `UICM-SECURED-ENTRY-CONTEXT-REPORT`
> **Programme:** UCOS-UICM-000001 — Phase 5 discovery (USE-STEER-000001)
> **AUTHORITY = NONE — DERIVED TRUTH.**
> **Disposition:** DISCOVERY ONLY. No implementation. No registry created. No UICM dimension added.
> **Constraint compliance:** no duplicate identity system, no duplicate authorization system, no
> mutable registry, no invented authority. Every conclusion cites a located owner.

---

## 1. The finding that reframes the question

**Nothing in this repository serves a network request.** Verified directly:

```
[project.scripts]                        31 entry points
  not "<pkg>.cli:main"                    2  — ec1-frozen-guard, ec1-determinism (both CLI tools)
dependencies = []
  "# Runtime dependencies: none. Foundation is stdlib-only by constitutional intent
   (TP-04 Vendor Neutrality of Core, TP-05 Least Sufficient Technology)."
listeners in engine/ platform/ service/ application/ infrastructure/ intelligence/
  fastapi | flask | uvicorn | aiohttp | starlette | django | tornado | sanic
  | socketserver | http.server                                            none
  socket.socket | .serve_forever( | HTTPServer | asyncio.start_server | .bind((
                                                                        none
```

The repository does not merely lack a server — it **forbids** one. Governance suites assert the
absence in source (`assert "http.server" not in source` across
`platform/tests/test_projects_governance.py`, `test_artifact_explorer_governance.py`,
`test_execution_dashboard_governance.py`, `test_generation_governance.py`).

**Consequence.** USE-STEER-000001 describes an "External Request" arriving at a Universal Entry
Gateway. There is no external request, because there is no surface one could arrive on. Every
"gateway", "admission" and "authorization" component located below is an **in-process,
deterministic decision function over Python objects** — not a network perimeter. A programme
framed as a request entry boundary would be guarding a surface the repository has constitutionally
declined to have.

This does not dismiss the directive. It relocates it: the directive's substance is about
**admission to execution**, and admission to execution is already implemented five times over.

## 2. Discovery 1 — capabilities that already implement secured entry

Five admission points exist. Each is fail-closed. None is a network boundary.

| # | Admission point | Owner | Subject admitted | Fail-closed rule | Refusal form |
|---:|---|---|---|---|---|
| 1 | `UniversalPipelineGateway.submit` | **UAPF-000001** `platform/universal_pipeline/gateway.py` | a unit of pipeline work | 4 ordered checks; refusal recorded then **raised** | error |
| 2 | `AuthorizationService.authorize` | **EC2-EPIC-002** `platform/identity/service.py` | a session-bearing capability request | 3 deny reasons before policy is consulted | data (`AccessDecision`) |
| 3 | `PortalAccessGateway.admit` | EC2-TASK-000074 `platform/portal/access.py` | a portal session | READ on `PORTAL_NAVIGATION` | data (`PortalAdmission`) |
| 4 | `RuntimeAdmissionGuard.evaluate` | EC2-TASK-000166 `platform/runtime_operations/guard.py` | a `RuntimeUnit` + certification | all 7 `ADMISSION_CRITERIA` must pass | data (`AdmissionDecision`) |
| 5 | `authorize(composition)` | EPIC-RTE-002 `engine/runtime/execution/authorization.py` | a `RuntimeComposition` | EC-1 disclosure present | raise |

### The strongest candidate already claims the directive's exact role

`platform/universal_pipeline/gateway.py` opens: *"**UAPF-000001 — the Universal Integration
Gateway (the single admission point for work).** Nothing executes in UAPF without a gateway
admission… bypassing the gateway is not a rule someone might forget — **it is impossible**,
because a caller cannot manufacture a valid authorization without performing the same checks the
gateway performs."*

And on the class: *"**The one door into execution.** Every unit of work enters through `submit`…
It executes nothing itself: admission and execution are separate acts, so the thing that decides
is not the thing that runs."*

It is a **composer**, exactly as the directive requires: it composes the registry (does this
pipeline exist?), the security declaration (may this principal run it?) and governance (do the
obligations permit it?). It owns none of those truths. Its authorization is *recomputable* —
`authorization_for(core)` is a module function rather than a method *"so the gateway (which mints)
and the transaction (which verifies) provably use the same rule — there is only one"* — and
`require_authorized()` raises `PipelineGatewayError("gateway authorization does not match the
transaction (bypass attempt)")`. Idempotent by construction: *"There is no counter, no clock and
no nonce, which is also what makes the authorization recomputable"* (AIF-L13).

**It is declared REUSE with replacement prohibited.** `00-MASTER/UAEP-000001/uaep-platform.json`:

```json
{ "id": "UAEP-CAP-03",
  "name": "Universal Autonomous Pipeline Framework",
  "disposition": "REUSE",
  "reuse": "Already realised as UAPF-000001 and registered as a capability
            whose replacement is prohibited." }
```

## 3. Discovery — the eight directive stages, mapped to located owners

USE-STEER-000001 requires eight validations. Seven have located owners. One does not exist.

| Stage | Located owner | Evidence |
|---|---|---|
| Identity Validation | AIF `A/G-AUTH` (law) → `platform/foundation/durable_identity.py` `IdentityRegistry` + `admission.py` `AdmissionBinder` (P2 plane); `engine/registry/universal/identity.py` `deterministic_id` (registry plane) | G-24 gate register: *"Part III A/G-AUTH **exactly one identity authority**"* |
| **Authentication Validation** | **NONE — does not exist** | §4 |
| Authority Validation | `engine/nucleus/ownership.py`; CEP-003 Art I/VIII vesting; UCOS-UCAF-001 (G-18) | gate G-18 owner prose |
| Context Validation | `engine/context/` — `resolution.py`, `validation.py`, `registry.py` | Context Layer (UCXI-000001) |
| Governance Validation | CMG-000001 Art L via `00-CMG/tools/cmg-gate.sh`; `platform/universal_pipeline/governance.py` | `verify.sh` stage 6 |
| Integrity Validation | `engine/uckp/canonical.py` `content_hash` — UCKP Layer Zero, Art-13 | UCKP-INV-03; non-duplication enforced by AST scan |
| Policy Validation | `platform/identity/policy.py` `PolicyEngine`; `platform/universal_assurance/policy.py` | — |
| Evidence Generation | `engine/registry/universal` `EvidenceRegistry`; `IdentityEvidence`; `GatewayTransaction.fingerprint()` | `required_attributes = {"subject"}` |

The gateway's declared prohibition — *"SHALL NOT own identity / authority / context / governance /
certification / evidence truth"* — is therefore already satisfied by every existing gateway,
because none of them owns any of it.

## 4. Authentication does not exist, and cannot be trivially added

This is the only stage with no owner, and its absence is deliberate rather than accidental.

`platform/identity/service.py:20-21` states it outright:

> "It authenticates nothing itself — sessions are established from already-authenticated
> principals — and holds no secret material (SEC-04)."

`platform/identity/sessions.py` confirms it structurally. `Session.establish` takes an
**already-constructed `Principal`**; there is no credential argument, no challenge, no comparison.
The only credential-shaped field is `credential_ref`, validated only as *"a non-empty reference
string (SEC-04)"* — an opaque reference to externally-held material, never a secret value.
Lifetimes are caller-supplied logical ticks, not wall-clock. `SessionRegistry.validate` raises on
absent/expired/revoked, with revocation taking precedence over expiry.

Repository-wide, no password hashing, no token signature verification, no TLS, no identity-provider
integration exists in `engine/` or `platform/`.

**Three constraints collide on any attempt to add it:**

1. **SEC-04** — "holds no secret material". Honoured by never having a secret.
2. **`dependencies = []`** — stdlib-only *by constitutional intent* (TP-04, TP-05). No crypto,
   JWT or TLS library is admissible without amending that posture.
3. **Nothing to authenticate to** — §1.

So authentication is the one genuine CREATE the directive implies, and it is not a capability gap
to be filled — it is a **constitutional question** about SEC-04 and the zero-dependency posture.
It must not be smuggled in as part of a gateway.

## 5. Discovery — the security domain explicitly disclaims enforcement

This is decisive for ownership. `14-SECURITY/SECURITY-001-UNIVERSAL-SECURITY-CONSTITUTION.md` says
it three times, and the third is a law:

> **USL-014 — Assurance, Not Enforcement (architecture layer).** "At the architecture layer
> security is **evaluative and assuring**: it classifies, evaluates, and attests. It selects no
> technology and executes no runtime; any enforcement is delegated **by reference** to
> already-frozen, certified lower-layer mechanisms."

§1: *"Security in UCOS is **assurance, not enforcement**."* §4 USA-6: *"Security enacts nothing at
the architecture layer."* All four authority fields read `NONE` — CONSTITUENT, GOVERNANCE,
RATIFICATION, EC-1.

§2's scope table puts the enforcement layer **out of scope by reference**:

> "Execution/state/policy runtime (RL-F2); platform security service (PL-F2 `platform/security`);
> … infrastructure security facet (Band-13 U08 SecurityFacet) — **reused by reference, never
> redefined**"

And `platform/security` itself is record-only throughout. `platform/security/zones.py`: *"Posture
evaluation is **record-only**… it authorizes, ratifies, and enacts nothing (RG-02 / AR-04); it
stores no secret value (SEC-04 / RR-07)."* `EC2-CAP-SEC-001-DETERMINATION.md` §4.3 draws an
absolute boundary: *"no new authority · no new security model · … · **no second authorization
logic** · no second audit-of-record"*, and §3.3 names the existing enforcement point:
`platform.identity.AuthorizationService` as *"the **single, fail-closed access decision point**"*.

**Conclusion.** A gateway that *enforces* entry cannot be owned by the SECURITY domain. Security
may classify and attest it; enforcement belongs to the already-located runtime point.

## 6. The concept is already in the ontology — under a different name

There is no ontology entity or taxonomy leaf for *entry*, *gateway*, *admission* or *perimeter*
anywhere in `14-SECURITY/`. Verified: zero matches.

What exists is **`Boundary`**:

| Layer | Owner | Entity |
|---|---|---|
| Ontology | SECURITY-003 §37 BOUNDARY ONTOLOGY | `Boundary` (`ONT-E-24`) ⊑ `ProtectionObject`, attribute `defaultCrossing` **fixed = `deny`** |
| Ontology | SECURITY-003 (Trust) | `TrustBoundary` (`ONT-E-07`) |
| Ontology | SECURITY-003 (Isolation) | `IsolationDomain` (`ONT-E-23`) |
| Taxonomy | SECURITY-004 canonical leaf register | `TAX-L-24` Boundary · `TAX-L-07` TrustBoundary · `TAX-L-23` Isolation |
| Theory | SECURITY-002 §24 | `A-Bnd-1` exactly one declared boundary per isolation domain; `A-Bnd-2` cross-boundary interaction requires an explicit, typed, evidenced reference |

Crossing invariants already exist: **BD-INV-1** single demarcation, **BD-INV-2** *"Cross-boundary
interaction requires an explicit, typed, evidenced reference; default-deny otherwise"*, **BD-INV-3**
every crossing governed by an explicit `Policy`, plus `RM-5` and `TRR-6` boundary default-deny.

So "Secured Entry Boundary" **classifies to `TAX-L-24 Boundary`** whose crossing is governed by
`Policy` and `Authorization`. It is not a new taxon — and `SECURITY-004 LR-1` forbids one:
*"`TAX-L-nn ↔ ONT-E-nn` is a bijection over the 32 catalog entities… no invented leaf."*

## 7. The directive's principles are already law

| Directive requirement | Existing law | Instrument |
|---|---|---|
| no implicit trust | **USL-004 Zero Trust** — "No principal, construct, **boundary**, or channel is trusted implicitly" | SECURITY-001 §6 |
| refusal is the default | **USL-005 Default Deny** — "Ambiguity resolves to denial, never to permit" | SECURITY-001 §6 |
| every entry explicitly authorized | **USL-006 Explicit Authorization** — "referencing a principal, a resource, an action, a context, and a policy" | SECURITY-001 §6 |
| layered controls at boundaries | **USL-009 Defense in Depth** | SECURITY-001 §6 |
| gateway owns no truth | **USL-013 Authority Non-Mintage** + **USL-002 Reuse by Reference** | SECURITY-001 §6 |
| no duplicate registry/identity | **USL-015 Non-Constitutive** — "introduces no new primitive, authority, registry system, identifier scheme, or lifecycle" | SECURITY-001 §6 |

The law set is declared *"complete over the domain … and non-overlapping in obligation. Any future
law is admitted **additively** (USL-016…), never by rewrite."* There is no law gap for entry.

## 8. Where "gateway" *is* owned by name

Only one instrument in canon owns gateways as a named set:
`04-REFERENCE/UCOS-Ω∞-UNIVERSAL-REFERENCE-API-ARCHITECTURE.md` (**REF-API-001**) §3 Canonical API
Gateway Architecture — six gateways: **External · Internal · Partner · Agent · Administrative ·
Certification**, with *"Gateway policies (authentication, rate limiting, quota, WAF, schema
validation, request signing) SHALL be centrally governed and versioned."*

`ARCH-API-001` §6 adds *"No network-exposed API ships without authentication and authorization
(SEC-02)."* Both are architecture references for a surface that does not yet exist. If "Universal
Entry Gateway" means an API surface, **REF-API-001 §3 already owns it and the count is fixed at
six** — a seventh would need its own determination.

Access control is also already a registered capability: `DOM-0455 Access Control`, realized by
`CAP-1842` Access Policy Definition, `CAP-1843` Access **Enforcement**, `CAP-1844` Access Review,
`CAP-1845` Access Revocation, on the declared chain *"DOM-0035 → DOM-0036 → DOM-0455 → DOM-0456
(Auth → Authz → Access Control → Encryption)"*.

## 9. Discovery 2 — is a universal boundary missing?

**No universal boundary is missing. One universal *binding* is.**

The five admission points are surface-scoped, and that is appropriate — each admits a different
subject. What is genuinely absent is a connection between two permission vocabularies:

| Vocabulary | Where | Form |
|---|---|---|
| Identity Layer | `platform/identity/contracts.py` | typed `CapabilityGroup` + `Permission`, evaluated against the §3.2 RBAC matrix by `PolicyEngine` |
| UAPF | `platform/universal_pipeline/contracts.py` `PipelineSecuritySpec` | **opaque strings** `required_permissions`, compared by set difference |

`UniversalPipelineGateway._require_permissions` computes
`missing = sorted(required - set(permissions))`. It **never consults `AuthorizationService`**, has
no notion of principal, session or capability group, and `PipelineSecuritySpec` says so plainly:
*"**Declared, not enforced here**: … the single enforcement point stays the gateway and this type
stays a declaration."*

So the repository has one gateway that admits work by opaque permission strings, and a separate
fail-closed access decision point that evaluates typed permissions against a role matrix — and
nothing joins them. **That is the located gap.** It is a binding between two existing owners, not
a new boundary, and not a new capability.

## 10. Determination

| Discovery item | Finding |
|---|---|
| 1. Existing capabilities implementing secured entry | **FIVE** fail-closed admission points, all in-process, all composers |
| 2. Missing universal boundary | **NONE** — but one **binding** is missing (Identity ↔ UAPF permission vocabularies) |
| Request surface | **DOES NOT EXIST** — 0 listeners, `dependencies = []`, absence asserted by governance tests |
| Authentication | **DOES NOT EXIST** — and blocked by SEC-04 + zero-dependency posture + no surface |
| Ontological home | **`Boundary` `ONT-E-24`** / `TAX-L-24`, `defaultCrossing` fixed = `deny` |
| Constitutional home | **USL-004/005/006/009**; law set declared complete |
| Enforcement owner | **`platform.identity.AuthorizationService`** — "the single, fail-closed access decision point" |
| Security domain's role | **assurance, not enforcement** (USL-014); cannot own an enforcing gateway |
| Named gateway owner | **REF-API-001 §3** — six gateways, if a network surface ever exists |

Proceed to `UICM-UNIVERSAL-ENTRY-GATEWAY-DETERMINATION.md` for the classification, and
`UICM-SECURED-ENTRY-CAPABILITY-MATRIX.md` for the reuse determination.
