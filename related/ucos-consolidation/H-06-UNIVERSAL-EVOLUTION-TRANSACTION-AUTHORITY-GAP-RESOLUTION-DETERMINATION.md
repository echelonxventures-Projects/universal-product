# H-06 UNIVERSAL EVOLUTION TRANSACTION AUTHORITY GAP RESOLUTION DETERMINATION

| Field | Value |
|---|---|
| **ID** | H-06-UETAGRD |
| **Authority** | READ-ONLY DETERMINATION. **No authority created. No identity allocated. No registry entry created. No repository mutation. No commit. No implementation.** This document analyses and specifies; it creates nothing. |
| **Objective** | Resolve the missing authority required for the cross-class atomic evolution transaction without violating existing mutation ownership boundaries (findings **AT-1**, **AT-1a**) |
| **Resolves** | Question 1 (A / B / C) · Question 2 (minimum constitutional boundary) · Question 3 (is a canonical object required first) · Question 4 (ownership model) · Question 5 (required owner decisions) |
| **HEAD** | `1f869865d5ff709c03cb4eb595524820d55d0be6` · branch `integration/recovery-001` · **86 commits ahead of `origin/integration/recovery-001`, 0 created here** |
| **Produced** | 2026-08-17 |
| **VERDICT** | **C — TRANSACTION ORCHESTRATION CAPABILITY UNDER AN EXISTING CONSTITUTIONAL FRAMEWORK**, with A embedded as a precondition and **B rejected on measured grounds** |
| **STATUS** | **AUTHORITY GAP RESOLVED — READY FOR CONSTITUTIONAL CREATION** |

**Instruments read, hash-verified unchanged:**

```
00-BOOK/DATA/mutation-governance-boundary.json          509d1a4d3f9af6e0c85cdf8cb098f29a80736aef9b0ec8e7a9c876fd73002165
00-BOOK/DATA/constitutional-authority-alignment.json    fd4f465166939b79743e7c2c7fea945b1f8cdb7ef0cc962026d3b7f297fbb3ae
engine/uckp/law.py                                      1597b041969bc64de7d3db6afb49f44a8c6013197f1b481ca226f03aac7aa795
engine/constitution/gateway.py                          dea311d0e8d9a5f1a19b3e8b7e0dcdecb1edf384679084dcbf73236a264b7ce6
engine/constitution/catalog.py                          4e288f5b64b0a011f2e4e3e8c31a9a1f9c128b7b7f4a0f669c58163c469655d1
00-CEP/CEP-003-CONSTITUTIONAL-EXECUTION-CONSTITUTION.md 956e02b1f095f31a58cb1907f730b97730cb56a3e7e6f147a46a3624be8eba29
00-CMG/CMG-000001-...-META-GOVERNANCE-CONSTITUTION.md   9b33335fee3135b21de77f2bb8f9b7fc50aa9e28d266aecbad2b8f30d7638cf5
platform/tests/test_mutation_governance_boundary.py     44385f12c5eeabf4f11ff8277b734d9de18174c69eeae367399596cdae3e9149
```

Also read: `engine/uckp/facets.py` · `engine/uckp/identity.py` · `engine/uckp/ucko.py` · `engine/uckp/evolution.py` ·
`engine/uckp/capabilities.py` · `engine/uckp/vocabulary.py` · `engine/constitution/metadata.py` ·
`engine/constitution/state.py` · `00-MASTER/UCOS-UGA-001/uga-declaration.json` · `00-BOOK/tools/ukb.py` ·
`H-06-ATOMIC-EVOLUTION-TRANSACTION-AUTHORITY-DETERMINATION.md` ·
`H-06-UNIVERSAL-EVOLUTION-TRANSACTION-OBJECT-DETERMINATION.md`.

---

## 0. Headline — The Requested Capability Cannot Be An Authority, And The Corpus Says So In Data

**`00-BOOK/DATA/constitutional-authority-alignment.json` publishes an eight-member `authority_roles`
vocabulary. Exactly one member may hold authority, and it is already occupied:**

| Role | `may_hold_authority` | `cardinality` | Article |
|---|:--:|---|---|
| **SUPREME** | **`true`** | **`EXACTLY_ONE`** | UCKP-ART-01 |
| PROJECTION | `false` | MANY | UCKP-ART-11 |
| PERSISTENCE | `false` | MANY | UCKP-ART-09 |
| **EXECUTION** | `false` | MANY | **UCKP-ART-10** |
| EVIDENCE | `false` | MANY | UCKP-ART-16 |
| OBSERVATION | `false` | MANY | UCKP-ART-13 |
| DERIVED | `false` | MANY | UCKP-ART-15 |
| ORTHOGONAL | `false` | FEW | UCKP-ART-01 |

`CAA-INV-01` — *"Exactly one instrument holds role SUPREME, it is UCKP-LAW-0001, and its declared home
exists."* `fails_closed: true`.

**Consequence, and it is decisive: there is no role a new instrument could take that permits it to hold
authority.** The single authority-holding role has cardinality `EXACTLY_ONE` and is held. `CAA-INV-03`
requires every bound instrument to carry a `constitutional_superior` block naming UCKP-LAW-0001. The
register's own `extension_rule` states the principle without qualification:

> *"Every future capability becomes an EXTENSION of the Universal Constitutional Object Model, **never a
> competing authority beside it**."*

and its `non_goals[0]`:

> *"Creating an authority. This binding confers none, ratifies nothing and occupies no tier."*

**Therefore the missing element is not an authority and must not be built as one. It is a capability with a
declared role, and the role the requirement's own MUST-NOT list describes is `EXECUTION` under
UCKP-ART-10 — *"a technology that acts on objects; execution never owns knowledge."***

This **corrects** `H-06-ATOMIC-EVOLUTION-TRANSACTION-AUTHORITY-DETERMINATION.md`, which affirmed *"B. A new
orchestration authority is required."* That determination read `mutation-governance-boundary.json` and
`law.py` and did not reach the `authority_roles` table. Its structural analysis stands in full; its
disposition does not. §6 records the correction.

---

## 1. Question 1 — A, B, or C

### 1.1 The Requirement, Restated As A Measured Set

Six capabilities required, five prohibitions. Nothing added, nothing dropped.

| # | MUST | Nearest existing mechanism | Present? |
|--:|---|---|:--:|
| R1 | Coordinate a multi-class evolution transaction | none — `ALL THREE = ∅` across the class chains | **NO** |
| R2 | Maintain transaction identity | `engine/uckp/identity.py` (pure URN) · `ukb.py` (`category_seq`) | mechanism yes, subject no |
| R3 | Maintain population boundary | no field in any object holds a path population | **NO** |
| R4 | Reference participating authorities | `mutation-governance-boundary.json` `governed_by` chains | referenceable |
| R5 | Maintain evidence lineage | `change-ledger.json` (per-artifact) · UCOS-EVIDENCE-UNIVERSE-001 | per-artifact only |
| R6 | Maintain validation and certification state | `Attestation` facets on UCKO · CEP-004 / CEP-005 | referenceable |

| # | MUST NOT | Enforced by |
|--:|---|---|
| N1 | Write source files | SOURCE chain: pre-commit → verify.sh → RIB-001 → AEE-001 → Phase 8 → Phase 9 |
| N2 | Generate artifacts | UCOS-GENERATED-ARTIFACT-REGISTRY-001 → producer → Phase 8 → Phase 9 |
| N3 | Modify registries | each register's own owner |
| N4 | Modify repository state | UCOS-RIB-001 GATE-02 / GATE-12 |
| N5 | Replace existing authority chains | boundary invariant *"No mutation class is claimed by two authorities as primary"* |

**N1–N4 remove every mutating act. What remains is: declare, reference, record, and refuse.** That is the
shape of the answer, and it is why the answer is a capability rather than an authority.

### 1.2 Option A — A New Constitutional Object Only

| Test | Result |
|---|---|
| Does ART-02 require an object? | **YES** — *"Every governed category of entity shall exist exactly once as a canonical Universal Constitutional Knowledge Object. Nothing exists constitutionally until it has become one."* |
| Does an object satisfy R1 (coordinate)? | **NO.** UCKP-ART-11: *"Generated output never owns truth; truth originates in an object."* An object is the truth-holder. It is not the thing that computes a discharge set and refuses on an incomplete one |
| Does an object satisfy R6 (maintain state)? | **PARTIALLY** — it can *carry* validation and certification attestations; it cannot *maintain* them, because maintenance is an act |
| Would the boundary artifact be extensible with an object alone? | **NO.** A transaction category added with no named discharger leaves invariant 3 — *"No mutation class is ungoverned — there is no class whose `governed_by` is empty"* — unsatisfiable for the new entry, and `platform/tests/test_mutation_governance_boundary.py` is the test that fails |
| Does UCKP-STOP-12 permit a capability without an object? | **NO** — *"Every capability derives from a canonical knowledge object."* |

**Verdict on A: NECESSARY BUT NOT SUFFICIENT.** ART-02 and STOP-12 make the object mandatory, and A is
therefore not an alternative to C — it is contained in C. Standing alone, A yields a specified category that
nothing performs.

### 1.3 Option B — A New Canonical Authority Object

Five independent grounds, each measured.

| # | Ground | Evidence |
|--:|---|---|
| **B-1** | No role permits holding authority | `authority_roles` — 7 of 8 roles carry `may_hold_authority: false`; the eighth is `SUPREME`, `cardinality: EXACTLY_ONE` |
| **B-2** | The one authority-holding role is occupied | `CAA-INV-01`, `fails_closed: true` — *"it is UCKP-LAW-0001"* |
| **B-3** | A subordinate instrument may not claim independent authority | `CAA-INV-03` — every bound instrument *"carries a `constitutional_superior` block naming UCKP-LAW-0001"*, `fails_closed: true` |
| **B-4** | The corpus's own extension procedure forbids it in terms | `extension_rule.principle` — *"never a competing authority beside it"*; `extension_rule.what_this_forbids` — *"A second registry, engine, lifecycle, identity authority, relationship graph or evolution system standing beside the ones that exist… UCKP-ART-03 makes a second definition of an existing primitive void, and CAA-INV-01..07 make that voidness measurable"* |
| **B-5** | A new authority would additionally require a tier admission that no instrument can perform | CMG-000001 XVI.8 — *"The tier set IS OPEN. A new tier SHALL be admitted under Article LXXVI"*; but LXXVI.2(b) — *"A substantive concept SHALL NOT be admitted here"*; LXXXI.2 — *"This instrument holds **no substantive authority**"*; XVIII.1 — *"Delegation under this instrument IS recognition, not transfer… holds no substantive authority and therefore has none to transfer"*; XIX.3 — *"Its only operations on other instruments are **recognize**, **record**, **rank**, and **refer**"* |

**Verdict on B: REJECTED.** Not on preference — on `fails_closed` invariants and on the register's own
stated non-goal. An authority object would be void under UCKP-ART-03 and measurable as void by CAA-INV-01
and CAA-INV-03.

**A note on why B looked correct.** The gap *is* an authority gap in the sense that no authority spans the
three classes — `H-06-AETAD` proved `ALL THREE = ∅` and that is not disturbed here. The error is in the
inference from *"no authority covers this"* to *"a new authority is required."* The corpus admits a third
possibility, written down in `extension_rule`: an instrument that covers the concern **while holding no
authority at all**. `mutation-governance-boundary.json` is itself exactly that instrument — role
`EXECUTION`, `derives_under: ["UCKP-ART-10", "UCKP-ART-16"]`, and it says of itself *"it does not create a
new authority and governs nothing itself."*

### 1.4 Option C — A Capability Under An Existing Constitutional Framework

Two candidate host frameworks exist. They must be tested separately, because only one of them can hold it.

#### 1.4.1 Candidate C1 — CEP-003 Constitutional Execution Constitution · **REJECTED**

CEP-003 is the strongest-looking candidate in the corpus. Article II.1 legislates, verbatim:

> *"the execution lifecycle, states, transitions, **sequencing**, dependencies, authorization, permissions,
> **coordination**, **orchestration**, checkpointing, suspension, resumption, restart, failure handling,
> recovery entry, isolation, concurrency, serialization, determinism, completion, and handoff."*

Article XI is titled EXECUTION ORCHESTRATION. CMG-000001 `CMG-DLG-03` independently delegates *"Execution
operation: authorization, dispatch, **sequencing**, concurrency, checkpointing…"* to CEP-003. On its face,
transaction-level orchestration is already legislated and already owned.

**It fails on four measured grounds, and the first two are structural rather than jurisdictional.**

| # | Ground | CEP-003 text | The transaction as measured |
|--:|---|---|---|
| **C1-a** | **Write-area singularity** | II.3 — *"Every execution act SHALL be attributable to exactly one execution unit, one stage, and **one write area**"*; IX.2 — *"a cross-area write IS PROHIBITED and SHALL be void"* | the population spans `engine/uaue/`, `engine/uckp/`, `engine/tests/`, `platform/tests/`, `00-MASTER/UAUE-000001/`, `00-MASTER/UAIE-000001/`, `00-MASTER/UCOS-RIB-001/`, `00-MASTER/UCOS-UGA-001/`, `00-BOOK/DATA/`, `.github/workflows/`, and three root build files — **many write areas**. As one execution unit it is a prohibited cross-area write |
| **C1-b** | **Acyclicity** | VII.2 — *"The execution dependency graph SHALL be acyclic; a dependency that would form a cycle IS PROHIBITED"*; VII.5 — a discovered cycle *"SHALL place the Program in HALTED until eliminated"*; VII.3 — a unit *"SHALL NOT enter DISPATCHED until every unit it depends upon has reached HANDED_OFF"* | `H-06-AETAD` §1 measured the cycle **E1→E2→E3→E4→E1** and **7 of 7 candidate first commits invalid**. As many execution units it is a prohibited cycle, and VII.3 is unsatisfiable in a cycle |
| **C1-c** | **A deterministic order is required and does not exist** | VI.1 — *"Execution SHALL proceed along the governed forward stage graph… in **topological order**"*; XI.2 — orchestration *"SHALL produce a single, deterministic, reproducible execution order"*; XI.4 — *"SHALL halt and report rather than proceed when a deterministic order cannot be derived"* | *"no topological order exists."* **CEP-003's correct response to this transaction is XI.4 — halt and report.** It is not equipped to admit it; it is equipped to refuse it |
| **C1-d** | **Jurisdiction and excluded subject matter** | I.1 — Execution Authority *"SHALL act only within a stage that is in the EXECUTING condition"*; II.4 — *"An act outside a stage in the EXECUTING condition IS PROHIBITED and SHALL be void"*; II.2 and XXIV.3 — *"SHALL NOT legislate governance, validation criteria, certification method, evidence content, or **repository content**"* | the transaction is a repository act, not a Program stage act, and R3/R5/R6 require it to carry population (repository content), evidence lineage, and certification state — three of the five subjects CEP-003 excludes |

**C1-a and C1-b together are the precise statement of the gap.** CEP-003 can express *a sequence of
single-area atomic units*. The transaction is *one multi-area atomic unit*. Those are different shapes, and
no amount of orchestration converts the second into the first — which is why the missing capability is a
**grouping and discharge** capability, not a sequencing one. The word "orchestration" in the request is
therefore slightly misleading, and the misreading is worth recording: **sequencing is already owned by
CEP-003 and must not be re-owned; atomic multi-class grouping is owned by nothing.**

#### 1.4.2 Candidate C2 — UCKP-LAW-0001 via the CAA `extension_rule` · **AFFIRMED**

`extension_rule.how_to_extend` bullet 3 is the written procedure for precisely this situation:

> *"A new repository capability declares its role and its articles in `subordinate_instruments` here, and
> gains a `constitutional_superior` block. **It does not declare a root.**"*

bullet 2:

> *"A new vocabulary member, relationship class, adapter or authority role is one appended entry in DATA.
> `engine/uckp/law.py` is never amended to fit the data (UCKP-ART-17)."*

bullet 4:

> *"Before creating anything, its canonical object is located and reused, extended or referenced
> (UCKP-ART-18)."*

| Test | Result | Evidence |
|---|:--:|---|
| Is the host framework already located? | **YES** | UCKP-LAW-0001, role SUPREME, `engine/uckp/law.py` |
| Is `capability` a governed category? | **YES** | `GOVERNED_CATEGORIES` member — 35 members, `capability` among them |
| Does a capability require an object? | **YES** | UCKP-STOP-12 — *"Every capability derives from a canonical knowledge object"*; realized in `engine/uckp/capabilities.py::_capability` |
| Is there an authorising article for an execution-family capability? | **YES** | `capabilities.py::AUTHORISING_ARTICLES` — `"execution": "UCKP-ART-10"`, annotated *"Derived authority, not assumed: a capability whose article is not named has no constitutional basis to exist"* |
| Is admission by registration rather than amendment? | **YES** | UCKP-ART-17 — *"an unknown future category is admitted by registration, never by amendment"*; sole mechanism `VocabularyRegistry.extend` |
| Is there a role precedent with the right prohibitions? | **YES** | `UCOS-MUTATION-GOVERNANCE-BOUNDARY-001`, role `EXECUTION`, `derives_under: ["UCKP-ART-10","UCKP-ART-16"]` — an instrument that disposes of mutation classes while *"governing nothing itself"* |
| Does the registration shape already carry a prohibition field? | **YES** | every `subordinate_instruments` entry carries `owns` and **`may_never_own`** — N1–N5 have a declared home with no schema change |
| Does any amendment become necessary? | **NO** | no 21st article, no 34th facet, no new tier, no new mutation class, no reassignment — §3.3 and §8 |

**Verdict on C: AFFIRMED, in one form only — C2.** The capability is hosted by UCKP-LAW-0001 through the
CAA extension rule, with role `EXECUTION` under UCKP-ART-10, and it derives from a new canonical knowledge
object created under UCKP-ART-02.

### 1.5 Resolution Of Question 1

| Option | Determination | Ground |
|---|---|---|
| **A. New constitutional object only** | **NECESSARY, NOT SUFFICIENT — subsumed into C** | ART-02 and STOP-12 mandate the object; ART-11 denies an object the capacity to act; the boundary artifact cannot be extended without a named discharger (§1.2) |
| **B. New canonical authority object** | **REJECTED** | `authority_roles` permits no new authority-holding role; SUPREME is `EXACTLY_ONE` and held; CAA-INV-01 and CAA-INV-03 `fails_closed`; `extension_rule.what_this_forbids`; `non_goals[0]`; and CMG-000001 cannot confer a tier (§1.3) |
| **C. Transaction orchestration capability under an existing constitutional framework** | **AFFIRMED — C2, under UCKP-LAW-0001 via the CAA `extension_rule`. C1 (CEP-003) rejected.** | §1.4 |

# **VERDICT: C — with A as its embedded precondition and B rejected**

---

## 2. Question 2 — The Minimum Required Constitutional Boundary

Named here for the record. **Not declared, not registered, not created.**

### 2.1 Purpose

To make a **multi-class repository evolution transaction** a declared, replayable, machine-verifiable unit:
one population of paths, spanning more than one mutation class and more than one owning programme, grouped
into a single atomic evolution event carrying an identity, a parent, and a per-class discharge record — so
that the transaction boundary satisfies UCKP-ART-16 (*"discoverable, replayable, deterministic, auditable,
traceable, machine-verifiable and human-understandable"*), which an undeclared boundary cannot.

### 2.2 Scope — Exactly Six Functions

| # | Function | Article of derivation |
|--:|---|---|
| S1 | **Group** an ordered population of paths into one declared transaction | ART-02 · ART-12 |
| S2 | **Derive and hold** the transaction identity, content-addressed, clock-free | ART-05 · ART-13 |
| S3 | **Reference** the mutation classes engaged and, per class, the governing chain that must discharge it | ART-07 (*"a relationship that cannot be resolved is not a relationship"*) |
| S4 | **Reference** the participating programmes and their per-class discharge outcome | ART-07 · ART-10 |
| S5 | **Reference** the parent transaction or state, and the evidence lineage of each participating surface | ART-12 · ART-16 |
| S6 | **Refuse** — report the transaction as undischarged while any referenced class discharge is absent | ART-16 · the boundary artifact's `recurrence_prevention` clause |

**S6 is the whole enforcement mechanism, and it must be built on the pattern the gateway already
established:** *"The bypass path is not blocked by a rule; it is blocked by there being nothing at the end of
it."* The capability produces one artifact — the transaction record — and the transaction is complete only
when that record shows every referenced class discharged. It blocks nothing directly.

### 2.3 Non-Scope — Exactly What It May Never Do

| # | Prohibition | Why, and where it is enforced instead |
|--:|---|---|
| P1 | Write a source file | SOURCE remains `pre-commit → verify.sh → RIB-001 → AEE-001 → Phase 8 → Phase 9` |
| P2 | Generate or register an artifact | GENERATED_ARTIFACT remains `UCOS-GENERATED-ARTIFACT-REGISTRY-001 → producer → Phase 8 → Phase 9`. **Its own transaction record is a generated artifact governed by that chain, not by itself** |
| P3 | Modify any registry | each register keeps its owner; UCKP-ART-03 makes a second definition of an existing primitive void |
| P4 | Modify repository state | REPOSITORY_STATE remains `UCOS-RIB-001 GATE-02 / GATE-12` |
| P5 | Replace, supersede, or duplicate an authority chain | boundary invariant *"No mutation class is claimed by two authorities as primary"* |
| P6 | Claim a mutation class as primary | the new invariant in §2.4 states this positively |
| P7 | Allocate an identity | `CAA-INV-04` EXACTLY_ONE_IDENTITY_AUTHORITY — it derives, `ukb.py` allocates |
| P8 | Constitute evidence or certification | `CAA-INV-06` EVIDENCE_AND_OBSERVATION_REMAIN_SEPARATE_TRUTHS; role EVIDENCE definition — *"evidence supports truth and never constitutes it"*. It references both, holds neither |
| P9 | Sequence, dispatch, suspend, resume, or serialize execution | **CEP-003 owns all of these (Articles VI, X, XI, XIII, XIV, XIX, XX). §1.4.1 rejected CEP-003 as the host; it does not thereby vacate the concern** |
| P10 | Declare a root, a new tier, or an authority | `extension_rule` — *"It does not declare a root"*; `non_goals[0]` |
| P11 | Declare a new evolution stage | UCKP-ART-14 owns the 15-stage cycle; a 16th stage is a constitutional amendment |
| P12 | Emit a wall clock into its identity or its canonical digest | ART-13; the UAUE precedent — *"a timestamp would make two projections of one state differ and destroy every measurement above it"* |

**P9 is the boundary that keeps C1 and C2 from colliding.** The capability declares *what belongs to one
atomic act*; CEP-003 governs *in what order authorized units execute*. Neither reaches into the other.

### 2.4 Authority Limits

| Property | Value |
|---|---|
| Role | **`EXECUTION`** — `may_hold_authority: false`, `cardinality: MANY` |
| Relation | **`PROJECTION`** of the object model onto the transaction boundary |
| Constitutional superior | **UCKP-LAW-0001**, and no other — `CAA-INV-03` |
| `derives_under` | **UCKP-ART-10** (execution never owns knowledge) · **UCKP-ART-12** (parent and typed deltas) · **UCKP-ART-14** (append-only evolution) · **UCKP-ART-16** (executable governance) |
| Authority held | **NONE.** It governs nothing, ratifies nothing, and occupies no tier |
| `owns` | *the declaration of which paths, classes, owners and discharges constitute one atomic evolution transaction* |
| `may_never_own` | *a mutation class; a path; a programme's surface; an identity allocation; evidence; certification; execution sequencing* |
| New invariant it introduces | *"Every mutation spanning more than one class belongs to exactly one declared transaction, and no transaction claims a class as primary."* |
| Existing invariants disturbed | **NONE** — all five boundary invariants and all eight CAA invariants continue to hold unchanged (§8) |

### 2.5 Relationships

**A disambiguation first, because the prior determinations conflate two instruments that share the token
`CMG`, and the conflation produces an unexecutable step (§6.2).**

| | `CMG-000001` | `UCOS-CMG-EXEC-000001` |
|---|---|---|
| Name | Constitutional **Meta Governance** Constitution | Constitutional **Mutation Gateway** |
| Home | `00-CMG/CMG-000001-…md` | `engine/constitution/gateway.py` |
| Nature | meta-constitutional instrument, tier **T1M**, `PROPOSED · PROVISIONAL` | Python pipeline, `GATEWAY_ID = "UCOS-CMG-EXEC-000001"` |
| Operates on | recognition of constitutionality | `Population` of `ConstitutionalMetadata` |
| Cross-references the other | **none** — measured: zero hits for `UCOS-CMG-EXEC-000001` across `00-CMG/` | none |

| Counterparty | Required relationship |
|---|---|
| **CMG-000001** (T1M) | **RECOGNITION ONLY.** Its operations are *"recognize, record, rank, and refer"* (XIX.3); it *"holds no substantive authority"* (LXXXI.2) and *"has none to transfer"* (XVIII.1). It may recognize the capability under `CMG-K-15 Capability` and record it in the Constitution Registry. **It may not create it, confer it, or host it.** Note that CMG-000001 has already delegated orchestration away twice — `CMG-DLG-37` to `06-IMPLEMENTATION/` and `CMG-DLG-03` to CEP-003 — so hosting it there would breach XIX.2 and void the clause under XIX.6 |
| **UCOS-CMG-EXEC-000001** (the gateway) | **ADMISSION OF THE DECLARATION, NOTHING FURTHER.** It governs *"creation or amendment of ConstitutionalMetadata"* and is *"sole producer of a clean StateSeal."* It `does_not_govern` *"source files on disk · generated artifacts · the working tree · the git object database"* — so it can admit the capability's declaration into the Population and can never give it reach over the transaction's four constituents. Its `_evidence` stage will refuse a subject whose `outputs` duplicate an existing subject's; measured, the 13 existing declarations in `engine/constitution/catalog.py` output only `constitutional-*` names, so an `evolution-transaction-record` output collides with nothing |
| **UCKP** (UCKP-LAW-0001) | **CONSTITUTIONAL SUPERIOR.** ART-01 supremacy; ART-02 mandates the object; ART-10 supplies the role; ART-12 supplies parent-and-deltas; ART-14 supplies the lifecycle; ART-16 is the article the present gap offends; ART-17 makes admission a registration; ART-18 requires the object be located before creation; ART-03 voids a rival. **The capability reads the stage set, the delta vocabulary, the category vocabulary and the class list from their owners at run time and fails closed on an unrecognised member** — the `AUE-BND-01` discipline |
| **UAUE-000001** | **`root_cause` REFERENCE ONLY.** `authority: NONE (DERIVED TRUTH)`; *"mutates no repository state and owns no capability"*; scope is *"one transaction traversing that cycle for one subject"*. It is the cause of the present transaction and constitutionally incapable of owning it. The capability records `engine/uaue` as root cause and takes nothing from UAUE |
| **UAIE-000001** | **PARTICIPANT, REFERENCED.** Contributes 6 paths and one seal rotation. Its registers remain its own. **Defect U-3 — UAIE has no read-only replay path — is a constraint on the capability's design, not on UAIE's participation: the capability must expose a read-only replay and must not repeat that mistake** |
| **UCOS-UGA-001** | **PARTICIPANT, REFERENCED.** Owns the REPOSITORY REALITY PROJECTION under ART-04/05/07/11 and *"may never own: What an OBJECT is; what an IDENTITY is; what a RELATIONSHIP is."* The capability reads its object-class declaration and never writes its registers |
| **UCOS-RIB-001** | **PRIMARY FOR REPOSITORY_STATE, UNCHANGED.** GATE-02 and GATE-12 remain its own. The capability references RIB's discharge as one entry in the discharge record. **The `governed_by` chain for REPOSITORY_STATE is not amended, extended, or shared** |
| **Identity Ledger** (`ukb.py`, THE ONE mint) | **DERIVATION ONLY, NO ALLOCATION.** `CAA-INV-04` EXACTLY_ONE_IDENTITY_AUTHORITY, `fails_closed`. On the UCKP plane the transaction identity is a pure URN — `urn_for` + `uuid_for`, no counter, no ledger write. On the repository plane, **if** a `UCOS-<CATEGORY>-<NNNNNN>` serial is wanted, only `ukb.py` may allocate it and only the owner may choose the category (decision **D-3**). Precedent for a non-file append-only register exists: `by_execution` (`EXEC-REG-001`) and `by_observation` (`OBS`) |

---

## 3. Question 3 — Is A New Canonical Object Required Before Authority Creation?

### 3.1 Answer

**YES — and the ordering question dissolves, because there is no authority to create.**

| Chain | Consequence |
|---|---|
| UCKP-ART-02 | the governed category does not exist constitutionally until it is a canonical object |
| UCKP-STOP-12 | *"Every capability derives from a canonical knowledge object."* No object ⇒ no lawful capability |
| `capabilities.py::_capability` | realizes STOP-12 in code — every capability is minted as a UCKO with `derives_from` naming its authorising article |
| UCKP-ART-18 | the object must first be *located*; `H-06-UETOD` performed that search and rejected four candidates on subject cardinality, domain, and authority standing |

**Therefore: object first, capability second, registration third, projection fourth.** The prior framing —
*"a canonical object required before authority creation"* — presupposed an authority. There is none. The
sequence is object → capability → registration → projection, and no step of it is an amendment.

### 3.2 Universal Evolution Transaction Object — Specification

**Specified, not created. No identity derived, no term registered, no facet written.**

#### 3.2.1 Identity Model

| Property | Requirement |
|---|---|
| Derivation | **DERIVED, never allocated** — content-addressed over `(ordered population, mutation-class set, parent identity)` |
| Mechanism | `engine/uckp/identity.py` — `urn_for(namespace, local_name)` then `uuid_for(urn)`, UUIDv5, *"Pure and total: the same arguments always yield the same identity, in every process, on every storage medium, at every time"* |
| Excluded from the input | **wall clock, arrival order, commit SHA, environment** — ART-13; and a commit SHA is *evidence* of a transaction, never its identity (ART-10; finding AT-1b) |
| Consequence | re-measuring the same population under the same parent yields the **same** identity — a re-measurement does not fork the history |
| Repository serial | **OPTIONAL AND UNDECIDED** — decision D-3. `CAA-INV-04` reserves allocation to `ukb.py` |
| Uniqueness | ART-02 — exactly once |

#### 3.2.2 Lifecycle

**Reused verbatim from UCKP-ART-14. No stage declared, no stage renamed, no 16th stage.**

```
observe · learn · reason · simulate · impact-analysis · dependency-analysis ·
authority-resolution · implementation · validation · verification · replay ·
certification · state-transition · knowledge-assimilation · continuation
```

Read at run time from `EVOLUTION_CYCLE`, which is itself `tuple(EvolutionStage)` — *"Derived from the enum
so the two can never disagree."* `is_terminal` is *"Always false"*; ART-14 — *"it never terminates."*

**Position of the present transaction: `authority-resolution`.** That is the stage AT-1 blocks, and this
determination is work performed *at* that stage, not past it.

**One measured constraint on reuse.** `EvolutionLedger.append` enforces a single global stage pointer —
first record must be stage 0 of cycle 0, thereafter `next_stage(previous.stage)`, raising *"evolution stages
may not be skipped or reordered."* It has **no per-subject streams**; `subject` is a plain field. A
transaction ledger with concurrent transactions therefore cannot be `EvolutionLedger`, and under ART-03 and
ART-18 a second ledger must be justified as an **extension of** rather than a **rival to** it. This is
decision **D-6**.

#### 3.2.3 Parent Lineage

| Property | Requirement |
|---|---|
| `parent` | the prior transaction identity, or the prior constitutional state where none exists — ART-12, *"references its parent… No previous state ever changes"* |
| `root_cause` | the artifact whose introduction produced the event; here `engine/uaue` |
| Deltas | **ART-12 vocabulary reused verbatim, not restated**: knowledge · evidence · authority · capability · certification |
| Relationship to `change-ledger.json` | **complementary, not replacing.** 1233 lineage nodes with predecessor/successor chains stay where they are. The transaction object **groups**; the change ledger **itemises**. Two granularities, one truth |
| Retirement | superseded transactions are **`RETAINED-BUT-RETIRED`**, never deleted — the id-ledger precedent |

#### 3.2.4 Evidence Model

| Property | Requirement |
|---|---|
| Holding | **references only.** Role EVIDENCE definition — *"evidence supports truth and never constitutes it"*; `CAA-INV-06` forbids either register declaring the other's subject |
| Per-surface lineage | referenced from the surface's own evidence class |
| Input closure | **must be declared in full.** Defects **U-1** (UAIE's `input_closure` omits the catalog that drives its output) and **U-2** (the catalog's closure says *"tracked corpus at HEAD"* while `git ls-files` reads the **index**) are both under-declared closures. An object grouping a whole transaction is the most exposed of all to that error |
| Replay | **must expose a read-only replay path** — defect **U-3** is the counter-example: UAIE's replay proof requires a write |

#### 3.2.5 Authority References

| Property | Requirement |
|---|---|
| Superior | UCKP-LAW-0001, exactly once, via the `constitutional_superior` block — `CAA-INV-03` |
| Participating authorities | **referenced by name from `mutation-governance-boundary.json`, never restated.** Referencing is not claiming |
| Own authority | **NONE.** Role `EXECUTION`, `may_hold_authority: false` |
| Articles | ART-10 · ART-12 · ART-14 · ART-16 — *"every declared authority role resolves to an article of the root law"* (`CAA-INV-07`) |

#### 3.2.6 Capability References

| Property | Requirement |
|---|---|
| Authorising article | **UCKP-ART-10** — `AUTHORISING_ARTICLES["execution"]` |
| `derives_from` | the ART-10 object's URN, per the `_capability` pattern |
| `outputs` | one name not declared by any existing subject — measured: the 13 declarations in `catalog.py` output only `constitutional-*` names |
| `lifecycle` at mint | **`implemented`, never `operational`** — *"The lawful route to `operational` runs through an attestation, so minting there directly would be asserting a judgement nobody has made"* |
| Capability catalog entry | a row in `intelligence/UCOS-RIE-CAPABILITY-CATALOG.json` is **`authority: NONE (derived truth)`** and generator-discovered. Appending there mints nothing and declares nothing |

#### 3.2.7 Mutation-Class References

| Property | Requirement |
|---|---|
| Form | a `mutation_classes` field holding **references** to the five declared classes |
| Per class | the `governed_by` chain that must discharge it, copied by reference from the boundary artifact |
| Prohibition | **no class is named as owned, primary, shared, or delegated** |
| Classes engaged by the present transaction | SOURCE · GENERATED_ARTIFACT · REPOSITORY_STATE. Not engaged: CONSTITUTIONAL_TRUTH, EXCLUSION |
| Fail-closed rule | if the boundary artifact declares a sixth class the object does not reference, the object **fails closed** rather than defaulting |

#### 3.2.8 Validation State

| Property | Requirement |
|---|---|
| Form | per-class discharge outcome, sourced from each class's own terminal verifier — Phase 9 for SOURCE and GENERATED_ARTIFACT, RIB-001 for REPOSITORY_STATE |
| Ownership | **referenced.** CEP-004 owns validation method; the object owns none of it |
| Aggregate | the transaction is `UNDISCHARGED` while any referenced class discharge is absent — the S6 refusal |
| Determinism | must be re-derivable in two independent processes, as UAUE's `deterministic-replay` job already measures |

#### 3.2.9 Certification State

| Property | Requirement |
|---|---|
| Form | reference to the certification record of each participating surface |
| Ownership | **referenced.** CEP-005 owns certification method; `certification_authority_resolution` carries a `second_authority_test` the object must not trip |
| Prohibition | the object **never certifies**, and **never records itself as certified** |
| Phase 0 effect | **NONE.** 0.5 and 0.6 remain FAIL until the transaction lands; this object does not clear them |

### 3.3 Proof That No Amendment Is Required

Every requested attribute maps onto an existing facet. The 33-facet enumeration is closed and *"Adding a
thirty-fourth facet is a constitutional amendment."* **None is needed.**

| Requested aspect | Existing facet | Amendment? |
|---|---|:--:|
| Identity model | `identity` · `semantic-identity` | **NO** |
| Lifecycle | `lifecycle` | **NO** |
| Parent lineage | `provenance` · `temporal-history` · `evolution-history` | **NO** |
| Evidence model | `evidence` · `traceability` · `audit` | **NO** |
| Authority references | `authority` · `ownership` | **NO** |
| Capability references | `dependencies` · `relationships` | **NO** |
| Mutation-class references | `relationships` · `taxonomy` | **NO** |
| Validation state | `validation` · `verification` | **NO** |
| Certification state | `certification` | **NO** |
| Replay | `replay` | **NO** |
| Population boundary | **UNDECIDED — `metadata`, `constraints`, `context`, or `existence-context`** | **NO**, but see **D-4** |
| Governed category term | `transition` · `event` · `state` · `timeline` already exist; a distinct term is a **registration** under ART-17 | **NO**, see **D-2** |

**No 21st article. No 34th facet. No 16th evolution stage. No new tier. No sixth mutation class. No
reassignment.** Closure is registration throughout — which is the whole reason status is RESOLVED rather
than REMAINS.

---

## 4. Question 4 — The Ownership Model

### 4.1 The Five Answers

| Question | Owner | Basis | Changes? |
|---|---|---|:--:|
| **Transaction definition** | **The Universal Evolution Transaction canonical object**, under UCKP-LAW-0001 — created by the owner, ART-02 | truth originates in an object (ART-11) | **NEW** |
| **Transaction coordination** | **The transaction orchestration capability**, role `EXECUTION`, under UCKP-ART-10 — holding **no authority** | `authority_roles.EXECUTION.may_hold_authority: false`; `extension_rule` bullet 3 | **NEW** |
| **Mutation execution** | **UNCHANGED, per class.** SOURCE → `pre-commit → verify.sh → RIB-001 → AEE-001 → Phase 8 → Phase 9`. GENERATED_ARTIFACT → `GENERATED-ARTIFACT-REGISTRY-001 → producer → Phase 8 → Phase 9`. REPOSITORY_STATE → `RIB-001 GATE-02 / GATE-12` | boundary invariants 1 and 2 | **NO** |
| **Validation** | **UNCHANGED.** Per-class terminal verifiers — Phase 9; RIB-001. Method owned by CEP-004 | CEP-004 II.1; boundary artifact `enforcement` fields | **NO** |
| **Certification** | **UNCHANGED.** Phase 9 pristine-clone certification; `constitution.acceptance`; method owned by CEP-005 | CEP-005 II.1; `certification_authority_resolution` | **NO** |
| *(also)* **Execution sequencing** | **UNCHANGED — CEP-003**, Articles VI, X, XI, XIX, XX. The capability never sequences | CEP-003 II.1; `CMG-DLG-03` | **NO** |
| *(also)* **Identity allocation** | **UNCHANGED — `ukb.py`, THE ONE mint** | `CAA-INV-04` | **NO** |

**Two new owners. Zero reassignments. Zero shared primacies.**

### 4.2 The Maxim, And Its Sharper Form

> **Transaction authority ≠ mutation authority.**

Maintained throughout, and the evidence permits a stronger statement:

> **There is no transaction authority. Transaction orchestration holds no authority at all.**

Every non-SUPREME role in `authority_roles` carries `may_hold_authority: false`, and the role the
capability must take is `EXECUTION` — *"execution never owns knowledge."* The capability disposes of nothing.
It declares what belongs to one atomic act, references who must discharge each part, records whether they
did, and reports `UNDISCHARGED` until they all have. **A record that refuses is not an authority that
governs**, and this distinction is what keeps boundary invariant 2 — *"No mutation class is claimed by two
authorities as primary"* — true after the capability exists.

---

## 5. Question 5 — Required Owner Decisions

**Identified, not created. No decision record is opened by this determination and no field is presented for
marking.**

| # | Decision required | Decision owner | Evidence required | Impact if unresolved |
|---|---|---|---|---|
| **D-1** | Adopt disposition **C2** — capability under UCKP-LAW-0001 via the CAA `extension_rule`, role `EXECUTION` — or reject it | Mutation Governance Owner | this determination §1; `authority_roles`; `extension_rule`; CEP-003 II.3/VII.2/XI.2/XI.4 | AT-1 stays OPEN; no transaction may be coordinated under a declared instrument; Phase 0 stays at 4 of 6 |
| **D-2** | Governed category for the object: reuse `transition`, `event`, `state`, or `timeline` — or register a new term via `VocabularyRegistry.extend` | UCKP owner | `GOVERNED_CATEGORIES` (35 members, no `transaction`); ART-17 registration rule; ART-03 rival-definition void | the object cannot be minted; `ucko.require_lawful` calls `require_term(GOVERNED_CATEGORY, …)` and fails closed |
| **D-3** | Whether a repository-plane serial is minted at all, and if so under which `category_seq` prefix | **`ukb.py` identity authority only** — `CAA-INV-04` | `category_seq` map; `by_execution`/`by_observation` precedent; `ID_CATEGORY` (6 file-shaped classes, none fits a transaction) | either no repository identity, or a prefix invented outside the one mint — the second breaches `CAA-INV-04` |
| **D-4** | Which facet carries the ordered path population — `metadata`, `constraints`, `context`, or `existence-context` | UCKP owner | 33-facet enumeration and per-facet questions in `facets.py`; the facet set is closed | the population has no declared home; R3 unsatisfied; a 34th facet would be an amendment |
| **D-5** | Whether the new invariant binds **prospectively only**. The act that creates the capability is itself a cross-class transaction — SOURCE (new module, appended `Declaration`) + CONSTITUTIONAL_TRUTH (gateway admission) + GENERATED_ARTIFACT (registry and ledger projections) + REPOSITORY_STATE (the commit) — and would violate its own invariant if that invariant were retroactive | Mutation Governance Owner | §7; `H-06-R4-GRANDFATHERING-POLICY-DETERMINATION.md` precedent | **bootstrap deadlock** — the capability cannot lawfully be created by the act that creates it |
| **D-6** | Whether the transaction ledger extends `EvolutionLedger` or is a separately identified append-only register | UCKP owner | `EvolutionLedger.append` single global stage pointer, no per-subject streams; ART-03; ART-18 | a second evolution system standing beside the first — void under ART-03, measurable by `CAA-INV-07` |
| **D-7** | Sequence and authority for the four closure acts: mint object · declare capability · register in CAA `subordinate_instruments` · project into `mutation-governance-boundary.json` + `platform/tests/test_mutation_governance_boundary.py` | Mutation Governance Owner, with each artifact's owner | §3.1 ordering; `extension_rule.how_to_extend`; the boundary artifact's `recurrence_prevention` clause | the invariant is declared but untested — *"A future mutation class added without an authority fails that test"* would not extend to transactions |
| **D-8** | Disposition of **AT-2** before the CAA registration lands: `constitutional-authority-alignment.json` is the registration target and carries an unresolved delta, 2 of the 59 paths in it | its owner | `H-06-IEPBODR` §1.3; AT-2 | the registration act would be entangled with an unresolved delta in the same file |

**Not a decision, and recorded so it is not mistaken for one:** the option `B` disposition is unavailable, so
no owner decision can select it. `authority_roles` and `CAA-INV-01`/`CAA-INV-03` are `fails_closed`
invariants, not preferences.

---

## 6. Corrections To Prior Determinations

### 6.1 `H-06-ATOMIC-EVOLUTION-TRANSACTION-AUTHORITY-DETERMINATION.md` — disposition corrected

| Element | Prior | Corrected | Basis |
|---|---|---|---|
| Verdict | *"B. A NEW ORCHESTRATION AUTHORITY IS REQUIRED"* | **a new orchestration CAPABILITY is required; no new authority is possible** | `authority_roles` — 7 of 8 roles `may_hold_authority: false`, SUPREME `EXACTLY_ONE` and held; `CAA-INV-01`, `CAA-INV-03`; `extension_rule.what_this_forbids`; `non_goals[0]` |
| §5.1 step 2 | *"Designate its authority, scoped to sequencing only"* | **unexecutable as written, twice over** — no authority may be designated, and sequencing is already owned by CEP-003 (II.1, VI, XI) and delegated to it by `CMG-DLG-03`. The capability owns **atomic multi-class grouping**, not sequencing | §1.3, §1.4.1, §2.3 P9 |
| §3 candidate set | nine candidates, all mutation-class authorities | **CEP-003 was not among them.** It is the strongest candidate host and is rejected here on four measured grounds, not omitted | §1.4.1 |
| §0 and §3 set arithmetic | `ALL THREE = ∅`; best coverage 2 of 3 | **UNCHANGED — reconfirmed.** The measurement is sound; only the inference from it is corrected | — |

### 6.2 Both prior determinations — a plane conflation in the creation path

Both state the object is *"minted as a canonical UCKO"* **through** `UCOS-CMG-EXEC-000001`. Measured, that
is two planes:

| Plane | Object | Created by | Governed as |
|---|---|---|---|
| UCKP | `UniversalConstitutionalKnowledgeObject`, **33 facets** | `UCKO.mint` — a **pure function**, no gateway, no allocator | writing the module is a **SOURCE** mutation, and OPTION B places SOURCE outside the gateway entirely |
| Constitution | `ConstitutionalMetadata`, **15 mandated blocking facets** | `ConstitutionalMetadata.declare` → `gateway.apply` | **CONSTITUTIONAL_TRUTH** |

`gateway.apply` accepts `records: tuple[ConstitutionalMetadata, ...]`. **It cannot mint a UCKO.** So the
creation path is not one act through the gateway; it is two acts on two planes, in two different mutation
classes — which is precisely why §7 finds the creating act to be itself a cross-class transaction. The prior
step 1 is not wrong in intent; it is under-specified in a way that hides the bootstrap.

### 6.3 Two citation corrections

| Claim | Correction |
|---|---|
| *"CMG's **own** `OPTION B` determination"* (AETAD §3; UETOD §3.4) | OPTION B lives in `00-BOOK/DATA/mutation-governance-boundary.json`, an **authored third-party projection** that says of itself *"it does not create a new authority and governs nothing itself."* Measured: zero hits for `OPTION B`, `working tree`, or `git object database` across CMG-000001's 2043 lines. The scope limitation is correct and well-evidenced; the attribution is not |
| `test_mutation_governance_boundary.py` cited without a path | it is at **`platform/tests/test_mutation_governance_boundary.py`**, sha256 `44385f12…9149` |

**Neither correction disturbs any measurement.** The 74/88 populations, the 14-path delta, the cycle, the
empty three-way intersection, and the append-only compliance findings all stand.

---

## 7. The Bootstrap, And Why It Is A Decision Rather Than A Gap

**The act that creates the capability is itself a multi-class evolution transaction.**

```
new module + appended Declaration in engine/constitution/catalog.py   → SOURCE
ConstitutionalMetadata declared and admitted via gateway.apply        → CONSTITUTIONAL_TRUTH
id-ledger, UGA registers, generated-artifact-registry projections     → GENERATED_ARTIFACT
the commit object                                                     → REPOSITORY_STATE
```

Four classes. If the new invariant — *"Every mutation spanning more than one class belongs to exactly one
declared transaction"* — binds retroactively, the creating commit violates it, because no declared
transaction can exist before the capability that declares transactions.

**Two properties make this resolvable without further constitutional machinery.**

1. **Nothing is currently breached.** The transaction being unowned violates no existing invariant. Boundary
   invariant 3 says *"No mutation class is ungoverned"* — and a transaction is not a class. As
   `H-06-UETOD` §2 put it: **it is unrepresented, not ungoverned.** So the creating act is lawful under the
   rules in force at the moment it occurs, discharged per class exactly as all 86 commits on this branch
   were.
2. **Prospective scoping is an ordinary owner decision with a precedent in this very programme.**
   `H-06-R4-GRANDFATHERING-POLICY-DETERMINATION.md` and its decision record already establish how this
   corpus scopes a new rule against pre-existing acts.

**This is decision D-5, not an additional constitutional instrument.** It requires no amendment, no new
tier, and no new authority — which is why it does not move the status to REMAINS.

---

## 8. Validation

### 8.1 No Authority Created Or Designated

| Check | Result |
|---|--:|
| Does this determination create an authority? | **NO** |
| Designate one? | **NO** |
| Recommend that one be created? | **NO — it determines that none may be** |
| Create a canonical object? | **NO** |
| Derive or allocate an identity? | **NO** |
| Register a vocabulary term? | **NO** |
| Create a registry entry? | **NO** |
| Amend `law.py`, `facets.py`, or any article, invariant or stop condition? | **NO — read, unmodified** |
| Basis for restraint | UCKP-ART-11 — *"Generated output never owns truth; truth originates in an object."* A determination is a document |

### 8.2 Mutation-Class Ownership Preserved Verbatim

| Class | `governed_by` after this determination |
|---|---|
| `CONSTITUTIONAL_TRUTH` | `UCOS-CMG-EXEC-000001` — **unchanged** |
| `SOURCE` | `pre-commit → verify.sh → UCOS-RIB-001 → UCOS-AEE-001 → Phase 8 → Phase 9` — **unchanged** |
| `GENERATED_ARTIFACT` | `UCOS-GENERATED-ARTIFACT-REGISTRY-001 → producer → Phase 8 → Phase 9` — **unchanged** |
| `EXCLUSION` | `UCOS-EXCLUSION-REGISTER-001 → UCOS-RIB-001 GATE-12` — **unchanged** |
| `REPOSITORY_STATE` | `UCOS-RIB-001 GATE-02 / GATE-12` — **unchanged** |

**Zero reassignments. Zero classes added. Zero authorities claiming an additional class.**

### 8.3 Invariants Tested Against The Proposed Disposition

| Invariant | Source | Holds under C2? | Why |
|---|---|:--:|---|
| Every mutation class names exactly one governing authority chain | boundary | **YES** | no chain touched |
| No mutation class is claimed by two authorities as primary | boundary | **YES** | the capability references classes and claims none |
| No mutation class is ungoverned | boundary | **YES** | five classes, five chains, unchanged |
| Every named authority resolves to an implementation that exists | boundary | **YES** | the capability's implementation must exist before registration — an obligation, and D-7 orders it |
| EXCLUSION governed by a register, never the mechanism | boundary | **YES** | untouched |
| `CAA-INV-01` EXACTLY_ONE_SUPREME | CAA | **YES** | no second authority-holding instrument — the ground on which B was rejected |
| `CAA-INV-02` EVERY_AUTHORITY_CLAIM_NAMES_ITS_SUPERIOR | CAA | **YES** | the capability is bound in `subordinate_instruments` with a role and ≥1 article, or it disclaims |
| `CAA-INV-03` NO_INDEPENDENT_AUTHORITY | CAA | **YES** | `constitutional_superior` names UCKP-LAW-0001 |
| `CAA-INV-04` EXACTLY_ONE_IDENTITY_AUTHORITY | CAA | **YES** | derives; never allocates. D-3 reserves allocation to `ukb.py` |
| `CAA-INV-05` EXACTLY_ONE_RELATIONSHIP_MODEL_OWNER | CAA | **YES** | every relationship kind it emits binds to a UCKO class and an article |
| `CAA-INV-06` EVIDENCE_AND_OBSERVATION_SEPARATE | CAA | **YES** | it references both truths and constitutes neither |
| `CAA-INV-07` NO_RIVAL_OBJECT_MODEL | CAA | **YES** | it names UCKO as the model it projects and declares no classes of its own |
| `CAA-INV-08` ORTHOGONAL_ROLE_SCOPE_BOUNDED | CAA | **N/A** | role is `EXECUTION`, not `ORTHOGONAL` |
| UCKP-ART-03 Zero Duplication | law | **YES** | no second registry, engine, lifecycle, identity authority, relationship graph, or evolution system — subject to D-6 |
| UCKP-ART-14 Append-Only | law | **YES** | records append; `RETAINED-BUT-RETIRED`, never deleted |
| UCKP-STOP-12 | law | **YES** | the capability derives from a canonical knowledge object — the reason A is a precondition |

### 8.4 Append-Only And Lineage

| Surface | Effect of this determination |
|---|--:|
| `id-ledger.json` | **0 reads mutated · 0 identities allocated** |
| `generated-artifact-registry.json` | **untouched** |
| UGA object registries | **untouched** |
| `change-ledger.json` | **untouched** — and explicitly not superseded; it itemises, the transaction object groups |
| `EvolutionLedger` | **untouched** — no record appended, no stage advanced |

### 8.5 What Was Verified, And What Was Not

**Verified by direct measurement:** the `authority_roles` table and all 8 CAA invariants; the 35-member
`GOVERNED_CATEGORIES` tuple and the absence of `transaction` from it; the 33-facet closed enumeration; the
13 `catalog.py` declarations and their `outputs`, establishing no duplicate-capability collision; zero
`transaction`/`atomic`/`orchestrat` tokens across `engine/constitution/*.py`; CEP-003 Articles I–XXIV in
full; the five mutation classes and five boundary invariants; `platform/tests/test_mutation_governance_boundary.py`
exists at that path; HEAD, branch, and eight instrument hashes.

**Not verified, and stated as such:** the runtime behaviour of the proposed capability — nothing was
executed, no gateway run was performed, `verify.sh` was not run, and no producer was invoked. Whether
`gateway.apply` would in fact admit a declaration of this shape is **asserted from reading the seven-stage
pipeline, not observed**. The gate refusal semantics of stages 2–7 were read at their `gateway.py` call
sites rather than inside `assimilation.py`, `planner.py`, `legality.py`, `authority.py` and `replay.py`.
`ROOT_LAW.governed_categories` was read as the `law.py` tuple; the live `VocabularyRegistry` was not
instantiated to confirm no term has already been registered at run time.

---

## 9. Boundary Attestation

| Property | State |
|---|---|
| HEAD before / after | `1f869865d5ff709c03cb4eb595524820d55d0be6` — **unchanged** |
| Branch | `integration/recovery-001` — 86 commits ahead of origin, **0 created here** (P-5 push strategy remains unselected) |
| Commits · pushes · staging changes | **0 · 0 · 0** |
| Files written | **1** — this document |
| Authorities created or designated | **0** |
| Canonical objects created | **0** |
| Identities derived or allocated | **0** |
| Vocabulary terms registered | **0** |
| Registry entries created | **0** |
| Declarations added or amended | **0** |
| Engine mutations | **0** |
| Mutation classes added, reassigned, or shared | **0** |
| Implementation executed | **NONE** — `verify.sh` not run · no `make` target · no producer run · no gateway run |
| `mutation-governance-boundary.json` | `509d1a4d…2165` — read, unchanged |
| `constitutional-authority-alignment.json` | `fd4f4651…b3ae` — read, unchanged |
| `engine/uckp/law.py` | `1597b041…a795` — read, unchanged |
| `engine/constitution/gateway.py` · `catalog.py` | `dea311d0…7ce6` · `4e288f5b…55d1` — read, unchanged |
| CEP-003 · CMG-000001 | `956e02b1…ba29` · `9b33335f…8cf5` — read, unchanged |
| `platform/tests/test_mutation_governance_boundary.py` | `44385f12…9149` — read, unchanged |
| Owner decision records touched | **0** — `H-06-IEPBODR` remains OPEN at 0 of 14, unmodified |

### 9.1 Open Items After This Determination

| ID | Item | Owner | State |
|---|---|---|--:|
| **AT-1** | Cross-class transaction boundary has no declared owner | Mutation Governance Owner | **RESOLVED IN DESIGN — the disposition is determined and requires no new constitutional instrument. OPEN IN FACT until D-1 is taken and the four closure acts are performed** |
| **AT-1a** | The gap is a missing canonical object | owner | **SPECIFIED — §3.2; creation not performed** |
| **AT-1b** | `change-ledger.json` `commit` field could be mistaken for a transaction anchor | boundary artifact owner | **OPEN — reaffirmed; a commit SHA is evidence, never identity (ART-10)** |
| **AT-1c** | *(new)* Prior determination affirmed a new *authority*; `authority_roles` permits none | recorded here | **CORRECTED — §6.1** |
| **AT-1d** | *(new)* The creation act is itself a cross-class transaction — bootstrap | Mutation Governance Owner | **OPEN — D-5** |
| **AT-1e** | *(new)* "Mint a UCKO through the gateway" conflates the 33-facet UCKP plane with the 15-facet ConstitutionalMetadata plane | recorded here | **CORRECTED — §6.2** |
| **AT-2** | `constitutional-authority-alignment.json` unresolved delta — and it is the registration target | its owner | **OPEN — now on the critical path, D-8** |
| **P-1** | Committed population undecided — 74 or 88 | Mutation Governance Owner | **OPEN — `H-06-IEPBODR` at 0 of 14** |
| **P-3** | Projections regenerated against a larger population than any decided boundary | ledger · UGA producers | OPEN |
| **P-5 / AT-3** | Push strategy S-1 / S-2 unselected; 86 commits unpushed | owner | OPEN |
| **U-1 · U-2 · U-3** | Under-declared input closures · index-vs-HEAD closure mismatch · no read-only UAIE replay | UAIE · RIB | **OPEN — §3.2.4 requires the new object avoid all three** |
| **D-1 … D-8** | The eight owner decisions | §5 | **OPEN — none opened as a record here** |

### 9.2 Effect On H-06

**None.** Phase 0 remains **4 of 6**, blocking on **0.5** and **0.6**, both satisfied only when the
transaction lands. H-06 cannot perform any closure act: minting the object is a SOURCE plus
CONSTITUTIONAL_TRUTH mutation and H-06's authorized scope excludes engine and registry (IADR §5, IAR §5).

---

*This determination is read-only with respect to every surface except itself. It measures the
`authority_roles` vocabulary and finds that seven of eight roles carry `may_hold_authority: false` while the
eighth is `EXACTLY_ONE` and held, and on that basis rejects the creation of a new authority and corrects the
prior determination that affirmed one; it tests CEP-003 as the strongest candidate host and rejects it on
write-area singularity, acyclicity, the requirement of a topological order that does not exist, and excluded
subject matter; it affirms the corpus's own written extension procedure — a capability with a declared role
and named articles, bound under UCKP-LAW-0001 — as the disposition, with role `EXECUTION` under UCKP-ART-10;
it establishes on UCKP-ART-02 and UCKP-STOP-12 that a canonical knowledge object is required first and
specifies that object across identity, lifecycle, parent lineage, evidence, authority references, capability
references, mutation-class references, validation state and certification state; it proves by facet mapping
that no amendment is required at any point; it resolves the five ownership questions with two new owners and
zero reassignments; it discloses the bootstrap by which the creating act is itself a cross-class transaction
and shows it resolvable by prospective scoping; and it identifies eight owner decisions without opening a
decision record or presenting a field for marking. It creates no authority, creates no object, allocates no
identity, registers no term, mutates no registry, reassigns no class, and confers nothing.*

---

# FINAL STATUS

# **AUTHORITY GAP RESOLVED — READY FOR CONSTITUTIONAL CREATION**

**On these grounds, each measured:**

| # | Ground |
|--:|---|
| 1 | The disposition is determined: **C2** — a transaction orchestration capability, role `EXECUTION` under UCKP-ART-10, bound under UCKP-LAW-0001 through the CAA `extension_rule`, deriving from a new canonical knowledge object under UCKP-ART-02 |
| 2 | **B is not merely unselected but unavailable** — `authority_roles` admits no new authority-holding role, so the gap cannot be closed by creating an authority and no further search for one is warranted |
| 3 | **No additional constitutional work is required.** Closure is registration throughout: no 21st article, no 34th facet, no 16th evolution stage, no new tier under CMG-000001 Article LXXVI, no sixth mutation class, no reassignment. UCKP-ART-17 — *"admitted by registration, never by amendment"* |
| 4 | The minimum constitutional boundary is defined — purpose, six scope functions, twelve prohibitions, authority limits, and the relationship to each of CMG-000001, `UCOS-CMG-EXEC-000001`, UCKP, UAUE, UAIE, UGA, RIB and the identity ledger |
| 5 | The required canonical object is specified across all nine requested aspects, with every attribute mapped to an existing facet |
| 6 | The ownership model is resolved with **two new owners and zero reassignments**; all five class chains, CEP-003 sequencing, CEP-004 validation, CEP-005 certification and the one identity mint are preserved verbatim |
| 7 | The bootstrap is disclosed and shown resolvable by a prospective-scoping decision with an in-programme precedent — not by a new instrument |

**What "READY" means, stated precisely so it is not over-read:** the constitutional analysis is complete and
the creation act is specified. **Creation has not occurred and is not authorized by this document.** It
requires **D-1** and the eight decisions of §5, and it remains gated on **AT-2**, on **P-1**, and on the
per-class discharge of the creating transaction itself.

---

Universal evolution transaction authority gap resolved in design.
Disposition: **C — transaction orchestration capability under UCKP-LAW-0001; no new authority is possible.**
Prior verdict **B** corrected on measured grounds.
No authority created.
No identity allocated.
No registry entry created.
No repository mutation.
No commit.
No implementation.
