# UICM — Phase 5 Determination

> **Artifact:** `UICM-PHASE-5-DETERMINATION`
> **Programme:** UCOS-UICM-000001 — Phase 5 discovery (USE-STEER-000001)
> **AUTHORITY = NONE — DERIVED TRUTH.**
> **Disposition:** DISCOVERY COMPLETE. HALTED. Nothing implemented, admitted or authorized.

---

## 1. Determination

**THE UNIVERSAL SECURED ENTRY PRINCIPLE IS ALREADY LAW. THE GATEWAY IS ALREADY IMPLEMENTED FIVE
TIMES. NO CAPABILITY IS JUSTIFIED. THIS DOES NOT BELONG TO UICM.**

| Discovery item | Finding |
|---|---|
| 1. Existing capabilities implementing secured entry | **FIVE** fail-closed admission points, all in-process composers |
| 2. Missing universal boundary | **NONE** — one *binding* is missing, and it is not a boundary |
| 3. Is a new capability justified? | **NO** — four independent grounds, any one sufficient |
| 4. Inside or outside UICM? | **OUTSIDE, definitively** |
| 5. Canonical owner | **layered across 8 instruments; none is UICM** |
| 6. Evidence model | **EXISTS** — SECURITY-001 §16 + 5 located deterministic producers |
| 7. Verification model | **EXISTS** — BD-INV-1/2/3, RM-5, TRR-6, A-Bnd-1/2, UMB-INV-01, ARCH-SECURITY-001 §16/§19 |
| 8. Evolution lifecycle | **EXISTS** — SECURITY-001 §11/§20, append-only, supersession-only, USL-015 |

## 2. The finding that reframes the directive

**Nothing in this repository serves a network request.** Verified directly:

```
[project.scripts]              31 entry points; 29 are "<pkg>.cli:main"
                               the 2 exceptions are ec1-frozen-guard and ec1-determinism
                               — both CLI tools, neither a server
dependencies = []              "Runtime dependencies: none. Foundation is stdlib-only by
                                constitutional intent (TP-04, TP-05)."
listeners                      fastapi | flask | uvicorn | aiohttp | starlette | django
                               | tornado | sanic | socketserver | http.server  -> none
                               socket.socket | serve_forever | HTTPServer
                               | asyncio.start_server | .bind((               -> none
```

The absence is enforced, not incidental: governance suites assert `"http.server" not in source`.

USE-STEER-000001 begins with "External Request". **There is no external request, because there is no
surface one could arrive on.** Every located gateway is an in-process, deterministic decision
function over Python objects.

This does not dismiss the directive — it relocates it. Its substance is *admission to execution*,
and that is implemented five times over.

## 3. Evidence register

Executed against the live repository. Nothing was written except the four Phase-5 documents.

| # | Claim | Result |
|---:|---|---|
| E1 | No network surface exists | 31 entry points, 0 servers, `dependencies = []`, 0 listeners |
| E2 | Absence is enforced | `assert "http.server" not in source` in 4 governance suites |
| E3 | UAPF-000001 is "the single admission point for work" | *"the one door into execution"*; bypass *"is impossible"* because authorization is recomputable |
| E4 | Its replacement is prohibited | `UAEP-CAP-03`: `"disposition": "REUSE"`, *"a capability whose replacement is prohibited"* |
| E5 | Authentication does not exist | *"It authenticates nothing itself … holds no secret material (SEC-04)"* |
| E6 | Security disclaims enforcement | **USL-014** — *"any enforcement is delegated by reference to already-frozen, certified lower-layer mechanisms"* |
| E7 | Security may not invent | **USL-015** — *"introduces no new primitive, authority, registry system, identifier scheme, or lifecycle"* |
| E8 | No entry/gateway/admission/perimeter taxon exists | zero `ONT-E-*` / `TAX-L-*` matches in `14-SECURITY/` |
| E9 | `Boundary` already owns the concept | `ONT-E-24` / `TAX-L-24`, `defaultCrossing` **fixed = `deny`** |
| E10 | The enforcement point is already named | `EC2-CAP-SEC-001` §3.3 — `AuthorizationService`, *"the single, fail-closed access decision point"* |
| E11 | A second authorization logic is forbidden by name | `EC2-CAP-SEC-001` §4.3 — *"no second authorization logic"* |
| E12 | Two permission vocabularies are unconnected | UAPF compares opaque strings by set difference; never consults `AuthorizationService` |
| E13 | Gateways already compose rather than own | five independent docstring statements to that effect |
| E14 | An 18th UICM dimension is digest-moving | `1676f708…` → `bd1acb16…`; cells 1054 → 1116 (verified Phase 2) |
| E15 | The SECURITY chain is largely ungenerated | `14-SECURITY/` holds only GOV-000 + 001..004; SL-4 Meta-Model and all concern architectures absent |

## 4. Constraint compliance

| Constraint | Held | How |
|---|---|---|
| No duplicate identity system | **yes** | AIF `A/G-AUTH` reused; both planes REUSE AS-IS; nothing minted |
| No duplicate authorization system | **yes** | `AuthorizationService` reused; a second is refused, citing `EC2-CAP-SEC-001` §4.3 |
| No mutable registry | **yes** | no registry designed or touched |
| No invented authority | **yes** | zero CREATE; every conclusion cites a located owner |
| Canonical owners only | **yes** | 8-instrument ownership stack, each with a citation |
| Every conclusion cites owner evidence | **yes** | E1–E15 |
| No implementation | **yes** | no code written |
| No new registries | **yes** | none |
| No UICM dimensions added | **yes** | `uicm.json` unmodified; USE-FWD-03 still blocked |

## 5. Why no capability is justified — four independent grounds

1. **USL-015** — security introduces no new primitive, authority, registry system, identifier
   scheme or lifecycle. A gateway owning entry decisions is a new authority; owning entry records is
   a new registry.
2. **`SECURITY-004 LR-1`** — `TAX-L ↔ ONT-E` is a bijection over 32 entities, *"no invented leaf"*,
   with a coverage proof recording *"no constitutional gap"*. A `Gateway` leaf breaks it.
3. **`ARCH-SECURITY-001` §21** — *"No security invention is authorized."*
4. **`UAEP-CAP-03`** — UAPF-000001's replacement is explicitly prohibited, and it already claims the
   role: *"the single admission point for work"*.

## 6. Classification result

| Reading | Verdict | Owner |
|---|---|---|
| Constitutional principle | already law | USL-004 / 005 / 006 / 009 (set declared complete) |
| Capability | already registered | `DOM-0455` → `CAP-1842/1843/1844/1845` |
| Governance control | owned | UMB-015 §2 + UMB-INV-01 → SEC-ZONE (record-only) |
| Runtime boundary | owned | `platform/identity/service.py` `AuthorizationService` |
| Security architecture | owned twice | ARCH-SECURITY-001 §6/§7; SECURITY-003 §37 `Boundary` |
| Verification requirement | owned | ARCH-SECURITY-001 §16, §19 |
| Certification requirement | owned | SECURITY-001 §13 Runtime tier; SEC-CERT; `engine/universal_certification` |

**Four of seven readings are real and owned; two are already discharged; none is unowned.**

## 7. The two genuine findings

Neither is a gateway. Neither belongs to UICM. Neither is authorized here.

### 7.1 Identity ↔ UAPF permission binding — **EXTEND**

The repository's *one door into execution* admits work against **opaque permission strings**
(`missing = sorted(required - set(permissions))`), while its *single fail-closed access decision
point* evaluates **typed permissions** against the §3.2 RBAC matrix. The door does not ask the
decision point, and has no notion of principal or session.

Disposition **EXTEND** (Art LXXVII.2(b)) — within existing scope, unaddressed. Owners to dispose:
`platform/identity` (EC2-EPIC-002) and `platform/universal_pipeline` (UAPF-000001).

### 7.2 Authentication — **RECORD AS GAP**

Does not exist anywhere. Not a missing module but a constitutional question, blocked three ways:
**SEC-04** (holds no secret material), **`dependencies = []`** (no crypto/JWT/TLS library
admissible), and **nothing to authenticate to**.

Disposition **RECORD AS GAP** (Art LXXVII.2(d)) — substantive and unowned; route to the competent
allocating authority. Art LXXVII.4 forbids routing it by default to UICM, UAPF or
`platform/security`. Art LXXVII.5 confirms holding is valid: *"Holding IS a valid disposition;
silent adoption IS not."*

## 8. Inside or outside UICM

**Outside.** UICM's `authority` is `NONE (DERIVED TRUTH)`, its disposition is `MEASUREMENT AND
CERTIFICATION LAYER ONLY`, and its `prohibited_creations` names identity and evidence registries
among five. A gateway is an enforcing runtime capability.

The only relationship UICM can ever have to secured entry is **measuring whether it is closed**, and
that remains blocked: an 18th dimension moves the declaration digest and expands the matrix
1054 → 1116 cells, and UICM-INV-02 requires a matching probe in bijection.

**USE-FWD-03 stands unchanged: REGISTERED, blocked on USE-FWD-02.**

## 9. USE-STEER-000001 obligations — updated status

| ID | Obligation | Status after Phase 5 |
|---|---|---|
| USE-FWD-01 | Secured-entry discovery: entry-point inventory, security capability inventory, canonical owner map, reuse analysis, gap determination, creation determination | **DISCHARGED** — all six outputs produced across the four Phase-5 documents |
| USE-FWD-02 | Architectural determination on whether a universal entry composition boundary is a genuine gap | **DISCHARGED — determination is NO.** Five admission points exist; a sixth is refused on four grounds. The located gap is a binding, not a boundary |
| USE-FWD-03 | `SECURED_ENTRY` as an 18th UICM closure dimension | **REGISTERED, still blocked.** USE-FWD-02 resolved negatively, so there is no new capability to measure. Measuring the *existing* five admission points as a dimension remains possible but digest-moving |
| USE-FWD-04 | Future capabilities inherit secured-entry requirements automatically | **ALREADY DISCHARGED BY LAW** — USL-004/005/006 are unconditional over the domain and `Boundary.defaultCrossing` is **fixed = `deny`**. Inheritance is the default-deny posture already in force, not a mechanism to build |

Two of four obligations are discharged, one is discharged by pre-existing law, and one remains
registered and blocked. **None was implemented.**

## 10. What would have gone wrong

Recorded because the failure mode was plausible and close. Taken at face value, the directive asks
for a Universal Entry Gateway composing eight validations. Building it would have:

- created a **sixth** admission point beside five fail-closed ones;
- **replaced** UAPF-000001's gateway, whose replacement is explicitly prohibited;
- introduced a **second authorization logic**, forbidden by name in `EC2-CAP-SEC-001` §4.3;
- invented a `Gateway` **taxonomy leaf**, breaking the `TAX-L ↔ ONT-E` bijection;
- required **authentication**, colliding with SEC-04 and `dependencies = []`;
- guarded a **request surface that does not exist**.

The directive's own Non-Goals anticipated most of this. Discovery shows those constraints were
load-bearing rather than cautionary.

## 11. Reserved for approval — cumulative across phases

Nothing below has been executed. Phase 5 adds no implementation step of its own.

| # | Step | Phase | Reversible | Digest effect |
|---:|---|---|---|---|
| M1 | Observation loader + L5–L11 load-time checks | 3 | yes | none |
| M2 | Verify `--matrix --replay`: expect 0 appends, digest `8ce37cd1…` | 3 | yes | none |
| M3 | Reconciliation cases 1–3 | 3 | yes | none while unchanged |
| M4 | Case 4 retirement + `SUPERSEDED` filter + LG-03 fail-closed detection | 3 | yes | none while population stable |
| M5 | Two-pass-before-render made explicit and tested | 3 | yes | none |
| G1 | Declare the gap → (owner, target file, gate) binding, additively | 4 | yes | verify neutral first |
| G2 | Append `CK-UICM` + `G-27` to `uccep-bindings.json` | 4 | yes | none (data append) |
| M6 | Wave 1 — `uga_engine.py run`, closing 2 gaps | 3 | **no** | matrix digest moves |
| — | *Identity ↔ UAPF permission binding* | 5 | — | **not UICM's to propose** — referred to its two owners |
| — | *Authentication* | 5 | — | **recorded as a gap** — requires a constitutional determination |

## 12. Recommendation

**Approve M1 and M2 only. Phase 5 adds nothing to the queue.**

The recommendation is unchanged for the third consecutive phase, and that consistency is the point:
Phases 3, 4 and 5 each discovered that the thing being asked for either already exists or cannot
safely precede durable observation history.

Phase 5's own two findings are **referred, not queued**. The permission binding belongs to
`platform/identity` and `platform/universal_pipeline`; authentication belongs to whichever authority
is competent to dispose of SEC-04 and the zero-dependency posture. UICM measures; it does not
allocate other owners' work, and Art LXXVII.4 forbids default routing precisely to prevent that.

**Do not implement a Universal Entry Gateway.** **Do not add a `SECURED_ENTRY` dimension.** **Do not
execute resolution waves.** All 158 UICM gaps remain open.

## 13. Status

```
PHASE 5 DISCOVERY          COMPLETE
IMPLEMENTATION             NOT STARTED  (not authorized)
NEW CAPABILITY             NOT CREATED  (refused on 4 independent grounds)
NEW REGISTRY               NOT CREATED
NEW AUTHORITY              NOT CREATED
NEW ONTOLOGY / TAXON       NOT CREATED  (TAX-L <-> ONT-E bijection intact)
NEW SECURITY LAW           NOT CREATED  (USL-001..015 declared complete)
UICM DIMENSIONS            17           (unchanged; no 18th added)
uicm.json                  UNMODIFIED
FROZEN SURFACE             UNMODIFIED   (engine/uicm, all committed registers)
MATRIX DIGEST              8ce37cd19fe42adf26d8832d84bd7106d0c0ccac9e12637727c35f81446c87dc  (unmoved)

REQUEST SURFACE            DOES NOT EXIST  (31 CLI entry points, 0 listeners, dependencies = [])
ADMISSION POINTS LOCATED   5            (all fail-closed, all composers)
DIRECTIVE STAGES OWNED     7 / 8        (authentication absent)
TEN REQUESTED OWNERS       10 / 10 located
REUSE DECISIONS            8 AS-IS · 2 AS-PATTERN · 3 REFERENCE · 1 INVOKE
CREATE                     0
EXTEND                     1            (Identity <-> UAPF permission binding — referred)
RECORD AS GAP              1            (authentication — blocked by SEC-04 + zero-dependency)
REJECT                     1            (Universal Entry Gateway construct)

USE-FWD-01                 DISCHARGED
USE-FWD-02                 DISCHARGED — determination is NO
USE-FWD-03                 REGISTERED, BLOCKED
USE-FWD-04                 DISCHARGED BY EXISTING LAW (USL-004/005/006; defaultCrossing = deny)

UICM GAPS                  158 open, 0 closed this phase (by design)

HALTED PENDING EXPLICIT APPROVAL OF M1 + M2.
```
