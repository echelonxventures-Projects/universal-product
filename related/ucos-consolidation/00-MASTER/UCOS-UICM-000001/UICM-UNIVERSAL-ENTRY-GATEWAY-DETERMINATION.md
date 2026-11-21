# UICM — Universal Entry Gateway Determination

> **Artifact:** `UICM-UNIVERSAL-ENTRY-GATEWAY-DETERMINATION`
> **Programme:** UCOS-UICM-000001 — Phase 5 discovery (USE-STEER-000001)
> **AUTHORITY = NONE — DERIVED TRUTH.** This determination allocates no ownership and admits no
> construct. It records what existing owners already hold.
> **Disposition:** DISCOVERY ONLY. Not implemented. Not admitted. No UICM dimension added.

---

## 1. Determination

**THE UNIVERSAL SECURED ENTRY PRINCIPLE IS ALREADY LAW. THE UNIVERSAL ENTRY GATEWAY IS ALREADY
IMPLEMENTED FIVE TIMES. NEITHER IS A NEW CONSTRUCT.**

The concept is not one thing. It decomposes across seven layers, and **every layer already has a
canonical owner**. Admitting it as a single new construct would collapse seven owned concerns into
one — which is the parallel authority CMG-INV-02 and USL-015 both forbid.

## 2. Classification — the seven questions, answered

| # | Is it a…? | Verdict | Canonical owner | Citation |
|---:|---|---|---|---|
| 1 | **Constitutional principle** | **NO — already law, no new principle** | SECURITY-001 §6 | USL-004 Zero Trust · USL-005 Default Deny · USL-006 Explicit Authorization · USL-009 Defense in Depth |
| 2 | **Capability** | **NO — already registered** | 02-MASTER catalogs | `DOM-0455` Access Control → `CAP-1842/1843/1844/1845` (Policy Definition · **Enforcement** · Review · Revocation) |
| 3 | **Governance control** | **YES — and owned** | UMB-015 §2 | Access control = *"zone membership + write path"*, under UMB-INV-01; realized record-only as **SEC-ZONE** |
| 4 | **Runtime boundary** | **YES — and owned** | `platform/identity/service.py` | `AuthorizationService` — *"the **single, fail-closed access decision point**"* (EC2-CAP-SEC-001 §3.3) |
| 5 | **Security architecture** | **YES — and owned twice** | ARCH-SECURITY-001 §6/§7; SECURITY-003 §37 | `Boundary` `ONT-E-24` · `TrustBoundary` `ONT-E-07` · `IsolationDomain` `ONT-E-23`; classified `TAX-L-24/07/23` |
| 6 | **Verification requirement** | **YES — and owned** | ARCH-SECURITY-001 §16, §19 | Security/Identity/Authorization testing gates merges (CD-02); §19 fails generation without Identity Model, Trust Model, Traceability, Testing, Observability, Certification, Governance |
| 7 | **Certification requirement** | **YES — and owned** | SECURITY-001 §13; ARCH-SECURITY-001 §18 | Five tiers; the **Runtime Compliance** tier is exactly *"does referenced enforcement occur only via frozen, certified lower-layer mechanisms?"*; realized as **SEC-CERT** |

**Four of seven readings are real and owned. Two are already discharged (principle, capability).
None is unowned.**

## 3. Why it is not a new constitutional principle

`SECURITY-001` §6 closes the law set: *"USL-001…015 are complete over the domain … and
non-overlapping in obligation. Any future law is admitted **additively** (USL-016…), never by
rewrite."*

The directive's own principles map one-to-one onto existing laws:

```
"No capability execution … may enter UCOS execution space
 without passing through a validated boundary"          -> USL-004 + USL-006
"refusal behaviour validated"                            -> USL-005 (default deny)
"gateway SHALL NOT own identity/authority/context/
 governance/certification/evidence truth"                -> USL-013 + USL-002
"No duplicate identity/permission/policy registry"        -> USL-015
"layered validation"                                      -> USL-009
```

`Boundary` (`ONT-E-24`) already carries `defaultCrossing` **fixed = `deny`**, and BD-INV-2 already
requires *"an explicit, typed, evidenced reference; default-deny otherwise"*. The Universal Secured
Entry Principle is a restatement of law that already exists at strictly greater precision.

## 4. Why a new capability is not justified — four independent grounds

Any one of these is sufficient. All four hold.

**1. USL-015 forbids it.** *"Security introduces no new primitive, authority, registry system,
identifier scheme, or lifecycle."* A Universal Entry Gateway owning entry decisions would be a new
authority; owning entry records would be a new registry.

**2. The taxonomy is a closed bijection.** `SECURITY-004 LR-1`: *"`TAX-L-nn ↔ ONT-E-nn` is a
bijection over the 32 catalog entities; the taxonomy classifies every Ontology entity and no more
(**no invented leaf**)."* Its coverage proof records *"All 25 constitutional concepts map to a
distinct leaf ⇒ **no constitutional gap**."* A `Gateway` leaf would break the bijection.

**3. `ARCH-SECURITY-001` §21 states it flatly:** *"**No security invention is authorized.**"* §1
adds that security *"invents no new asset, boundary, or trust relationship outside registered
authority."*

**4. Replacement of the admission gateway is explicitly prohibited.**
`00-MASTER/UAEP-000001/uaep-platform.json` `UAEP-CAP-03`: `"disposition": "REUSE"`, *"Already
realised as UAPF-000001 and registered as a capability **whose replacement is prohibited**."* And
UAPF-000001 already self-describes as *"the single admission point for work"* and *"the one door
into execution."*

## 5. The disposition, under the totality rule

CMG-000001 Art LXXVII.2 admits exactly one outcome per concept. Applied concept by concept:

| Concept | Outcome | Owner it routes to |
|---|---|---|
| Universal Secured Entry **Principle** | **REUSE** | USL-004/005/006/009 — already owned |
| Entry **boundary** as an entity | **REUSE** | `Boundary` `ONT-E-24` / `TAX-L-24` |
| Entry **admission** for work | **REUSE** | UAPF-000001 `UniversalPipelineGateway` |
| Entry **enforcement** | **REUSE** | `AuthorizationService` (L7) |
| Entry **zone/write-path control** | **REUSE** | UMB-015 §2 + UMB-INV-01 / SEC-ZONE |
| Entry **certification** | **REUSE** | SECURITY-001 §13 Runtime tier / SEC-CERT / `engine/universal_certification` |
| **Identity ↔ UAPF permission binding** | **EXTEND** | the two existing owners (§7) |
| **Authentication** | **RECORD AS GAP** | substantive and unowned → route to the competent allocating authority |
| A universal entry gateway *construct* | **REJECT** | duplicates five located admission points; §4 |

Art LXXVII.4 governs the last three: *"An unknown concept SHALL NOT be admitted by default routing
to the nearest owner, the most active program, or the meta layer. Default routing manufactures
parallel authority."* So authentication must **not** be routed to UICM, to UAPF, or to
`platform/security` by convenience. It is recorded as a gap, which Art LXXVII.5 confirms is a valid
disposition: *"Holding IS a valid disposition; silent adoption IS not."*

## 6. Canonical owner — layered, and none of them is UICM

There is no single canonical owner, because there is no single concept. The owner depends on which
reading is meant:

```
LAW              SECURITY-001 §6 — USL-004 / 005 / 006 / 009 / 013 / 015
   |
SEMANTICS        SECURITY-003 §37 — Boundary ONT-E-24 (defaultCrossing = deny)
   |             classified SECURITY-004 TAX-L-24
   |
ARCHITECTURE     ARCH-SECURITY-001 §6 Authorization · §7 Trust Boundaries
   |
GOVERNANCE       UMB-015 §2 Access control + UMB-INV-01  ->  SEC-ZONE (record-only)
   |
ENFORCEMENT      platform/identity/service.py AuthorizationService  (the single decision point)
   |
WORK ADMISSION   UAPF-000001 UniversalPipelineGateway  (replacement prohibited)
   |
API SURFACE      REF-API-001 §3 — six gateways, if a network surface ever exists
   |
CERTIFICATION    SECURITY-001 §13 Runtime tier · SEC-CERT · engine/universal_certification
```

**The only lawful slot for a new artifact** is an additive `SECURITY-*` **concern architecture**
under `SECURITY-GOV-000` OUTPUT 13, which authorizes *"Constitution → Theory → Ontology → Taxonomy →
Meta-Model → **concern architectures** → Freeze/Readiness/Completion → Registry."* Its capability
catalogue already names the nearest three concerns: **Authorization & Access**, **Trust Model**, and
**Secure Execution Model**.

Note the chain is authorized but largely ungenerated: `14-SECURITY/` contains only `SECURITY-GOV-000`
and `SECURITY-001..004`. `SECURITY-005` (SL-4 Meta-Model) does not exist, and no concern
architecture exists. So the lawful slot is real but **downstream of two unwritten artifacts**.

Any such artifact must be additive, **evaluative, non-enforcing**, and mint no entity, leaf,
registry, identifier or lifecycle.

## 7. The one genuine gap — a binding, not a boundary

Two permission vocabularies exist and nothing joins them:

```
platform/identity/                        platform/universal_pipeline/
  CapabilityGroup + Permission              PipelineSecuritySpec.required_permissions
  typed, §3.2 RBAC matrix                   opaque strings
  PolicyEngine.evaluate(principal, req)     missing = sorted(required - set(permissions))
  AuthorizationService = L7 decision point  gateway = "the one door into execution"
                    \                      /
                     \                    /
                      NOTHING CONNECTS THESE
```

`UniversalPipelineGateway._require_permissions` never consults `AuthorizationService`, has no
notion of principal or session, and `PipelineSecuritySpec` confirms the seam is intentional:
*"**Declared, not enforced here** … the single enforcement point stays the gateway and this type
stays a declaration."*

So the repository has *the one door into execution* admitting work on opaque permission strings,
while its *single fail-closed access decision point* evaluates typed permissions against a role
matrix — and the door does not ask the decision point.

| Property | Value |
|---|---|
| Nature | a **binding** between two located owners |
| Disposition | **EXTEND** (Art LXXVII.2(b)) — within existing scope, unaddressed |
| Not | a new gateway, a new registry, a new authority, a new leaf, a new law |
| Owners | `platform/identity` (EC2-EPIC-002) and `platform/universal_pipeline` (UAPF-000001) |
| Owned by UICM? | **no** — UICM measures; it cannot bind two platform capabilities |

**This determination does not authorize that binding.** It records it as the only located gap, for
its two owners to dispose of.

## 8. Inside or outside UICM — outside, definitively

| Test | Result |
|---|---|
| Is UICM an authority? | **No** — `programme.authority = "NONE (DERIVED TRUTH)"` |
| Is UICM allowed to enforce? | **No** — `disposition: MEASUREMENT AND CERTIFICATION LAYER ONLY` |
| May UICM open a registry? | **No** — `prohibited_creations` names five; identity and evidence registries among them |
| May UICM own identity? | **No** — capability identity is READ from canonical knowledge; artifact identity from UGA |
| Could UICM *measure* secured entry? | **In principle yes** — as a closure dimension |
| May it add that dimension now? | **No** — verified in Phase 2: an 18th dimension moves the declaration digest (`1676f708…` → `bd1acb16…`) and expands the matrix 1054 → 1116 cells, and UICM-INV-02 requires a matching probe |

A gateway is an **enforcing runtime capability**. UICM is a measurement layer with authority NONE.
The only relationship UICM can ever have to secured entry is to *measure whether it is closed* —
and even that is a Phase-6+ determination against a frozen declaration, not a Phase-5 action.

**USE-FWD-03 stands unchanged:** `SECURED_ENTRY` as a UICM closure dimension remains REGISTERED and
blocked on USE-FWD-02.

## 9. What would have gone wrong

Recording this because the failure mode was close and plausible.

Read at face value, USE-STEER-000001 asks for a Universal Entry Gateway composing eight validations.
Building it would have:

- created a **sixth** admission point beside five fail-closed ones;
- **replaced** UAPF-000001's gateway, whose replacement is explicitly prohibited;
- introduced a **second authorization logic**, which `EC2-CAP-SEC-001` §4.3 forbids by name;
- invented a `Gateway` **taxonomy leaf**, breaking the `TAX-L ↔ ONT-E` bijection;
- required **authentication**, colliding with SEC-04 and `dependencies = []`;
- guarded a **request surface that does not exist**.

The directive's own Non-Goals anticipated most of this: no immediate implementation, no new
registries, no modification of existing ownership models, no replacement of existing security
capabilities. Discovery confirms those constraints were not cautionary — they were load-bearing.

## 10. Determination summary

| Question | Answer |
|---|---|
| Constitutional principle? | already law — USL-004/005/006/009; law set complete |
| Capability? | already registered — DOM-0455, CAP-1842..1845 |
| Governance control? | yes, owned — UMB-015 §2 + UMB-INV-01 / SEC-ZONE |
| Runtime boundary? | yes, owned — `AuthorizationService`, the single decision point |
| Security architecture? | yes, owned twice — ARCH-SECURITY-001 §6/§7; `Boundary` `ONT-E-24` |
| Verification requirement? | yes, owned — ARCH-SECURITY-001 §16, §19 |
| Certification requirement? | yes, owned — SECURITY-001 §13 Runtime tier / SEC-CERT |
| New capability justified? | **NO** — four independent grounds |
| Belongs inside UICM? | **NO** — outside, definitively |
| Canonical owner? | **layered; none is UICM.** Lawful new slot: an additive `SECURITY-*` concern architecture |
| Genuine gap? | **one binding** (Identity ↔ UAPF permissions, EXTEND) + **authentication** (RECORD AS GAP) |
