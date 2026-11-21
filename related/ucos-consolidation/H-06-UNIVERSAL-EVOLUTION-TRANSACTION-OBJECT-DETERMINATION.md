# H-06 UNIVERSAL EVOLUTION TRANSACTION OBJECT DETERMINATION

| Field | Value |
|---|---|
| **ID** | H-06-UETOD |
| **Authority** | READ-ONLY DETERMINATION. **No implementation. No registry mutation. No authority creation. No commit.** This document *specifies*; it creates nothing. |
| **Objective** | Determine whether UCOS requires a canonical object representing multi-class evolutionary transactions (finding **AT-1a**) |
| **Instruments read** | `engine/uckp/law.py` (UCKP-LAW-0001) · `engine/uckp/evolution.py` · `00-BOOK/DATA/mutation-governance-boundary.json` `509d1a4d…2165` · `00-BOOK/DATA/change-ledger.json` · `00-BOOK/tools/config.py` · `00-BOOK/DATA/generated-artifact-registry.json` |
| **HEAD** | `1f869865d5ff709c03cb4eb595524820d55d0be6` · branch `integration/recovery-001` · **0 commits created** |
| **Produced** | 2026-08-16 |
| **VERDICT** | **C. NEW CANONICAL OBJECT REQUIRED** |

---

## 0. Headline

**Two existing objects come close, and both fail on the same structural point: their subject is singular.**

| Candidate | Subject field | Carries a mutation class? | Groups a population? |
|---|---|:--:|:--:|
| `EvolutionRecord` (UCKP-ART-14) | `subject: str` — **one** | **NO** | **NO** |
| `change_event` (change-ledger.json) | `subject: "UCOS-ARCH-000001"` — **one** | **NO** | **NO** — though it carries a `commit` field |

A multi-class evolution transaction has a **population** (74–88 paths), a **class set** (three), and
**seven owners**. Neither object has a field that can hold any of the three. Extension is also foreclosed:
extending `EvolutionRecord` would give UCKP primacy over `SOURCE`, `GENERATED_ARTIFACT` and
`REPOSITORY_STATE`, breaching the boundary invariant, and `change-ledger.json` is a **derived view** —
UCKP-ART-11 forbids a projection from originating truth.

**Cross-class evolution events are therefore not representable, and cannot be made representable by
extension. A new canonical object is required.** Per UCKP-ART-02 it must be minted exactly once, and per
CMG's own scope that minting is a `CONSTITUTIONAL_TRUTH` act through the Constitutional Mutation Gateway —
**not performed here.**

---

## 1. Existing Authority Model

| Layer | Instrument | Governs |
|---|---|---|
| Constitutional supremacy | **UCKP-LAW-0001** (`engine/uckp/law.py`) — 20 articles | the whole corpus; ART-01 Supremacy |
| Constitutional truth mutation | **UCOS-CMG-EXEC-000001** (`engine/constitution/gateway.py`) | Population · ConstitutionalMetadata · registration · truth update. Sole producer of a clean StateSeal |
| Mutation-class boundary | `mutation-governance-boundary.json` — **authored projection**, *"declares the boundary; it does not create a new authority and governs nothing itself"* | which class is governed by which chain |
| Evolution law | **UCKP-ART-14** Append-Only Evolution, realized in `engine/uckp/evolution.py` | the perpetual cycle: 15 stages, `EvolutionLedger`, `EvolutionRecord` |
| Evolution instance plane | **UAUE-000001** — `authority: NONE (DERIVED TRUTH)` | one transaction traversing the cycle for one subject |
| Identity | **`ukb.py`** — THE ONE append-only Universal Identity ledger | `by_path`, `by_object`, `category_seq` |
| Derived change view | `change-ledger.json` — *"derived views"* per `config.py:1170`, *"like control-tower.json / change-ledger.json"* as a non-authoritative store (`config.py:1403`) | per-artifact change events and lineage |

### 1.1 Articles That Bear on the Question

| Article | Text (abridged) | Bearing |
|---|---|---|
| **ART-02 Canonical Existence** | *"Every governed category of entity shall exist exactly once as a canonical Universal Constitutional Knowledge Object. **Nothing exists constitutionally until it has become one.**"* | the transaction category does not exist; zero `atomic`/`transaction` tokens in `law.py` or the boundary artifact |
| **ART-10 Execution Abstraction** | *"Execution never owns knowledge."* | git, the commit object, and `verify.sh` cannot own the transaction |
| **ART-11 Document Abstraction** | *"Documents are generated views… Generated output never owns truth; truth originates in an object."* | neither the boundary artifact nor `change-ledger.json` can originate the authority |
| **ART-12 Immutable Constitutional State** | *"Every transition creates a new state that references its parent and its knowledge, evidence, authority, capability and certification deltas. No previous state ever changes."* | **the closest existing analogue** — but confined to constitutional state, which CMG `OPTION B` places apart from source, generated artifacts, working tree and git |
| **ART-14 Append-Only Evolution** | *"Evolution observes, learns… assimilates, forever. It appends; it never rewrites; it never terminates."* | supplies the lifecycle the new object must reuse |
| **ART-16 Executable Governance** | *"Every governance decision is discoverable, replayable, deterministic, auditable, traceable, machine-verifiable and human-understandable."* | the article the present gap offends |

---

## 2. Existing Mutation Classes

| Class | Chain | Terminal |
|---|---|---|
| `SOURCE` | pre-commit → verify.sh → UCOS-RIB-001 → UCOS-AEE-001 → Phase 8 → Phase 9 | Phase 9 |
| `GENERATED_ARTIFACT` | UCOS-GENERATED-ARTIFACT-REGISTRY-001 → producer → Phase 8 → Phase 9 | Phase 9 |
| `REPOSITORY_STATE` | UCOS-RIB-001 GATE-02 / GATE-12 | RIB-001 |
| `CONSTITUTIONAL_TRUTH` | UCOS-CMG-EXEC-000001 | CMG |
| `EXCLUSION` | UCOS-EXCLUSION-REGISTER-001 → RIB GATE-12 | RIB-001 |

**Measured intersections:** `SOURCE ∩ GENERATED_ARTIFACT = {Phase 8, Phase 9}` · **`ALL THREE = ∅`**.

**Invariants that constrain any answer:**

> *"Every mutation class names exactly one governing authority chain."*
> *"No mutation class is claimed by two authorities as primary."*
> *"No mutation class is ungoverned."*

**Note:** the transaction being unowned breaches none of these — it is not a class. **It is unrepresented,
not ungoverned.** That distinction is why the answer is an ontology question rather than an authority
reassignment.

---

## 3. Are Cross-Class Evolution Events Representable?

### 3.1 Candidate 1 — `EvolutionRecord` / `EvolutionLedger` (UCKP-ART-14)

Measured fields:

```
EvolutionRecord:  cycle: int · stage: EvolutionStage · subject: str · outcome: str
                  digest: str · findings: tuple[str, ...]
EvolutionLedger:  append-only list of EvolutionRecord — "It appends; it never rewrites"
EVOLUTION_CYCLE:  15 stages — observe · learn · reason · simulate · impact-analysis ·
                  dependency-analysis · authority-resolution · implementation · validation ·
                  verification · replay · certification · state-transition ·
                  knowledge-assimilation · continuation
```

| Requirement of a cross-class transaction | Present? |
|---|:--:|
| A population — an ordered set of 74–88 paths | **NO** — `subject` is a single `str` |
| A class set — the mutation classes engaged | **NO** — no class field |
| An owner set — seven programmes | **NO** |
| Per-class chain references | **NO** |
| Atomicity / grouping semantics | **NO** |
| Append-only, staged lifecycle | **YES** |
| Content digest | **YES** — `digest` |

**Verdict on candidate 1: cannot represent.** Its docstring is exact — *"One appended step of the perpetual
cycle"* — a **step**, for a **subject**, not a transaction over a population.

### 3.2 Candidate 2 — `change_event` (`change-ledger.json`)

Measured shape, from a live entry:

```json
{ "change_id": "UCHG-000000001", "subject": "UCOS-ARCH-000001", "kind": "Created",
  "at": "2026-07-15T02:26:52+00:00", "snapshot_seq": 1,
  "from": null, "to": "FROZEN", "commit": null }
```

Ledger scale: **1353 change_events · 1233 versioned_artifacts · 1233 lineage_nodes**, plus an
`evolution_timeline` and a `lineage` map with `predecessors`/`successors`/`ancestor_chain`.

| Requirement | Present? |
|---|:--:|
| Population grouping | **NO** — one `subject` per event |
| Mutation class | **NO** |
| **Transaction anchor** | **PARTIAL** — a `commit` field exists |
| Lineage | **YES** — per artifact |
| Append-only | **YES** — monotonic `snapshot_seq` |

**Verdict on candidate 2: cannot represent, and its `commit` field is a trap.** Grouping a transaction by
commit SHA would make the git object database the grouping authority. **ART-10** — *"Execution never owns
knowledge"* — and the boundary artifact's placement of the git object database under RIB `GATE-02` both
forbid that. A commit SHA is evidence of a transaction, never its identity.

**Decisive additional fact:** `change-ledger.json` is **not a registered artifact** — it appears in no
`canonical_path` among the 344 registry entries, and `config.py` classifies it among *"the derived views"*
and as a non-authoritative store. **Under ART-11 a derived view cannot originate the object.**

### 3.3 Candidate 3 — UAUE-000001, the Evolution Transaction Plane

UAUE's declared mission is *"Make autonomous universal evolution a measurable **transaction** rather than a
described intention."* It is the nearest thing in the corpus by name.

| Property | Value | Bearing |
|---|---|---|
| Declared authority | **`NONE (DERIVED TRUTH)`** | cannot own anything |
| Scope | *"one transaction traversing that cycle **for one subject**"* (`AUE-BND-01`) | single-subject, as with candidate 1 |
| Self-limitation | *"legislates nothing… mutates no repository state and owns no capability"* · *"records that an execution was AUTHORISED to travel [the gateway] and never that a mutation happened"* | it records authorisation, never the mutation event |

**Verdict on candidate 3: cannot represent.** UAUE is a *measurement* plane over the cycle, explicitly not a
record of repository mutation, and holds no authority. It is also the **cause** of the transaction under
analysis, which cannot then be its own governing object.

### 3.4 Candidate 4 — ART-12 Constitutional State Transition

The only object whose shape genuinely fits: *"references its parent and its knowledge, evidence, authority,
capability and certification deltas. No previous state ever changes."* That is a transaction with a parent
and typed deltas.

**Verdict: right shape, wrong domain.** It is enforced through CMG's `Population` / `StateSeal`, and CMG's
own `OPTION B` determination states it does **not** govern *"source files on disk · generated artifacts · the
working tree · the git object database"* — the four things this transaction consists of. **The concept
exists; its application to these classes does not.**

### 3.5 Answer to Question 3

**NO. Cross-class evolution events are not representable by any existing canonical object.** Four
candidates examined; each fails on subject cardinality, domain, or authority standing.

---

## 4. Determination — A / B / C

| Option | Determination | Ground |
|---|---|---|
| **A. Existing canonical object is sufficient** | **REJECTED** | §3 — no candidate carries a population, a class set, or an owner set |
| **B. Existing object requires extension** | **REJECTED — on constitutional grounds, not convenience** | Extending `EvolutionRecord` would give UCKP primacy over three classes it does not govern, breaching *"No mutation class is claimed by two authorities as primary."* Extending `change-ledger.json` asks a **derived view** to originate truth, breaching **ART-11**. Extending ART-12 state would require CMG to grow a filesystem it *"deliberately does not have."* |
| **C. New canonical object required** | **AFFIRMED** | §3.5 plus **ART-02**: the category does not exist constitutionally until minted exactly once |

# **VERDICT: C — NEW CANONICAL OBJECT REQUIRED**

---

## 5. Specification of the Required Object

**This section defines what the object must be. It does not create it.** Creation is a
`CONSTITUTIONAL_TRUTH` act through UCOS-CMG-EXEC-000001 and belongs to the owner.

### 5.1 Purpose

To make a **multi-class repository evolution transaction** a governed, replayable object: the unit that
groups one population of paths, spanning more than one mutation class and more than one owning programme,
into a single atomic evolution event with an identity, a parent, and a per-class discharge record.

It exists so that a transaction is **discoverable, replayable, deterministic, auditable, traceable and
machine-verifiable** — the ART-16 properties an unowned boundary cannot supply.

### 5.2 Ontology

| Attribute | Requirement | Derivation |
|---|---|---|
| `population` | ordered set of repository paths | must be explicit, not implied by a commit |
| `mutation_classes` | the classes engaged, **by reference** | classes are **referenced, never claimed** — §6.2 |
| `owners` | the owning programmes and their per-class chains | from the boundary artifact |
| `root_cause` | the artifact whose introduction produced the event | here `engine/uaue` |
| `projections` | the derived surfaces the transaction updates | ledger, UGA, artifact registry, RIB outputs |
| `parent` | the prior transaction or state | **ART-12** — every transition references its parent |
| `deltas` | knowledge · evidence · authority · capability · certification | **ART-12** vocabulary reused verbatim, not restated |
| `discharge` | per-class chain outcome | each class discharged by its own chain |
| `stage` | current position in the cycle | **read** from `EvolutionStage`, never enumerated |

**Non-duplication rule.** The stage set, the delta vocabulary and the class list must each be **read from
their existing owners at run time** and fail closed if an owner adds a member the object does not claim —
the discipline `AUE-BND-01` already applies to UAUE.

### 5.3 Identity Model

| Property | Requirement |
|---|---|
| Derivation | **DERIVED, never minted arbitrarily** — content-addressed over the ordered population, the class set, and the parent identity |
| Precedent | UAUE derives identity *"from meaning, so the same candidate observed twice does not fork the history"*, reusing the nucleus rule's content-addressed prefix and width |
| Consequence | the same population under the same parent yields the **same** identity — a re-measurement does not fork the record |
| Category allocation | the category prefix and sequence must be allocated by **THE ONE identity authority** (`ukb.py`, `category_seq`); **this determination allocates none and proposes no prefix** |
| Uniqueness | **ART-02** — exactly once |
| Wall clock | **excluded from the identity input.** UAUE's precedent: *"No wall-clock is emitted into the projection"*, because *"a timestamp would make two projections of one state differ and destroy every measurement above it"* |

### 5.4 Lifecycle

**Reused, not invented.** The 15 stages of `EVOLUTION_CYCLE` already describe it:

```
observe · learn · reason · simulate · impact-analysis · dependency-analysis ·
authority-resolution · implementation · validation · verification · replay ·
certification · state-transition · knowledge-assimilation · continuation
```

| Stage group | Application to the present transaction |
|---|---|
| observe → simulate | the determinations already produced |
| impact-analysis · dependency-analysis | the 10 measured edges and the proven cycle |
| **authority-resolution** | **the stage this transaction is currently blocked at — AT-1** |
| implementation | the commit itself |
| validation · verification · replay | per-class chains, Phase 8, Phase 9 |
| certification · state-transition | Phase 9 and the parent-referencing state record |
| knowledge-assimilation · continuation | ART-14 — *"it never terminates"* |

**No new stage may be declared.** If the object needed a stage the cycle lacks, that would be a change to
UCKP-ART-14, a separate and larger constitutional act.

### 5.5 Ownership Relationship

| Relationship | Requirement |
|---|---|
| Owns | **the transaction — its identity, population, parent, and discharge record. Nothing else.** |
| Does **not** own | any mutation class · any path · any programme's surface |
| Relationship to programme owners | **references** them and records each class's discharge; it does not supersede them |
| Relationship to the root cause | records `engine/uaue` as `root_cause`; UAUE holds `authority: NONE` and cannot own the transaction it caused |

**This is the constraint that keeps the answer legal**: sequencing authority is not class authority.

### 5.6 Authority Relationship

| Relationship | Requirement |
|---|---|
| Constitutional superior | **UCKP-LAW-0001** — ART-01 Supremacy |
| Enforced articles | **ART-02** (canonical existence) · **ART-12** (parent + deltas) · **ART-14** (append-only) · **ART-16** (executable governance) |
| Creation path | **UCOS-CMG-EXEC-000001** — *"creation or amendment of ConstitutionalMetadata"* is inside CMG's declared scope |
| Projection | after minting, projected into `mutation-governance-boundary.json` as a declared category with its own invariant, and into `test_mutation_governance_boundary.py` so an undeclared transaction fails the test |
| What it must **not** be | a sixth mutation class **claiming** SOURCE, GENERATED_ARTIFACT or REPOSITORY_STATE |

### 5.7 Mutation Boundary Relationship

| Aspect | Requirement |
|---|---|
| Existing five classes | **UNCHANGED** — every `governed_by` chain preserved verbatim |
| New element | a **governed category** for transactions that *reference* classes |
| New invariant to add | *"Every mutation spanning more than one class belongs to exactly one declared transaction, and no transaction claims a class as primary."* |
| Effect on the existing invariants | none — all three continue to hold |
| Test obligation | extend `test_mutation_governance_boundary.py`, honouring the artifact's own `recurrence_prevention` clause |

---

## 6. Validation

### 6.1 No Dual Authority

| Check | Result |
|---|--:|
| Does the object claim a mutation class? | **NO** — §5.5, §5.7 |
| Would any class gain a second primary? | **NO** — chains unchanged |
| Does it supersede UCKP-ART-14 or CMG? | **NO** — it is enforced *by* ART-14 and created *through* CMG |
| Does this determination designate an authority? | **NO** |
| Does it allocate an identity category? | **NO** — allocation belongs to `ukb.py` |

### 6.2 No Mutation-Class Ownership Conflict

All five class chains are reproduced unchanged in §2. **Zero reassignments.** The object references classes
in a `mutation_classes` field and records their discharge; referencing is not claiming.

### 6.3 Append-Only Evolution

| Requirement | Satisfaction |
|---|---|
| ART-14 — *"It appends; it never rewrites; it never terminates"* | transaction records append to a ledger; none is rewritten |
| ART-12 — *"No previous state ever changes"* | each transaction references its parent; parents immutable |
| Existing surfaces | current deltas already compliant — ledger `by_object` +59 with **0 removals**, `by_path` byte-identical, `category_seq` monotonic, artifact registry +864/−0, UGA +59 with no removals |
| Retirement semantics | must follow the ledger precedent — superseded transactions are **`RETAINED-BUT-RETIRED`**, never deleted |

### 6.4 Lineage Preservation

| Requirement | Satisfaction |
|---|---|
| Per-artifact lineage | remains with `change-ledger.json` — 1233 lineage nodes with predecessor/successor chains. **The new object does not replace it** |
| Transaction-level lineage | supplied by `parent`, which per-artifact events cannot express |
| Root attribution | `root_cause` preserves the single-rooted lineage measured for the present event |
| Relationship | the transaction object **groups**; the change ledger **itemises**. Two granularities, one truth, no duplication |

### 6.5 Replay Determinism

| Requirement | Satisfaction |
|---|---|
| Same input ⇒ same identity | content-addressed identity over population + classes + parent (§5.3) |
| No wall clock in the identity | excluded, per the UAUE precedent |
| Cross-process reproducibility | must be measured in two independent processes, as UAUE's `deterministic-replay` job already does |
| Drift detection | must expose a **read-only** replay path — the defect **U-3** shows UAIE lacks one, so its proof requires a write. **The new object must not repeat that mistake** |
| Input closure completeness | must declare its **full** input closure — defects **U-1** and **U-2** are both under-declared closures, and an object grouping a whole transaction is the most exposed of all to that error |

---

## 7. What This Determination Did Not Do

| Act | Performed? |
|---|--:|
| Create a canonical object | **NO** |
| Designate an authority | **NO** |
| Allocate an identity or category prefix | **NO** |
| Amend `mutation-governance-boundary.json` | **NO** — read, hash-verified unchanged |
| Amend `law.py` or declare a stage | **NO** — read, unmodified |
| Mutate any registry | **NO** |
| Commit or push | **NO** |

**The path to closure remains an owner act:** mint the object through CMG under ART-02, scope its authority
to sequencing only, project it into the boundary artifact and its test, then coordinate the 74/88-path
transaction under it.

---

## 8. Verdict and Open Items

# **C. NEW CANONICAL OBJECT REQUIRED**

| ID | Item | Owner | State |
|---|---|---|--:|
| **AT-1** | No declared authority owns a cross-class transaction boundary | owner, via CMG | **OPEN** |
| **AT-1a** | The gap is a missing canonical object — **now characterised in full: purpose, ontology, identity, lifecycle, ownership, authority, boundary relationship** | owner, via CMG | **SPECIFIED, NOT CREATED** |
| **AT-1b** | *(new)* `change-ledger.json` carries a `commit` field that could be mistaken for a transaction anchor. A commit SHA is evidence, never identity — ART-10 | boundary artifact owner | **OPEN — recorded to prevent the wrong fix** |
| **AT-2** | `constitutional-authority-alignment.json` — 2 of the 59 in its delta | its owner | OPEN |
| **P-1** | Population undecided — 74 or 88 | Mutation Governance Owner | OPEN |
| **P-3** | Projections regenerated against a larger population than any decided boundary | ledger · UGA producers | OPEN |
| **U-1 · U-2 · U-3** | Under-declared input closures; index-vs-HEAD closure mismatch; no read-only UAIE replay | UAIE · RIB | OPEN — §6.5 requires the new object avoid all three |

### 8.1 Effect on H-06

**None.** Phase 0 remains **4 of 6**, blocking on **0.5** and **0.6**. H-06's governance chain is complete
and its denominator delta is recorded at 16 of 16. **H-06 cannot mint the object** — that is a
`CONSTITUTIONAL_TRUTH` act and H-06's authorized scope excludes it (IADR §5, IAR §5).

---

## 9. Boundary Attestation

| Property | State |
|---|---|
| HEAD before / after | `1f869865d5ff709c03cb4eb595524820d55d0be6` — **unchanged** |
| Branch | `integration/recovery-001` |
| Commits · pushes · staging changes | **0 · 0 · 0** |
| Files written | **1** — this document |
| Canonical objects created · authorities designated · identities allocated | **0 · 0 · 0** |
| Mutation classes added or reassigned | **0** |
| `mutation-governance-boundary.json` | `509d1a4d3f9af6e0c85cdf8cb098f29a80736aef9b0ec8e7a9c876fd73002165` — **read, unchanged** |
| `engine/uckp/law.py` · `engine/uckp/evolution.py` · `change-ledger.json` | **read, unmodified** |
| Registry · declaration · engine mutations | **0 · 0 · 0** |
| `verify.sh` · `make` · producer runs | **NONE** |

*This determination is read-only with respect to every surface except itself. It examines four candidate
canonical objects and finds each fails on subject cardinality, domain, or authority standing; rejects
extension on constitutional grounds rather than convenience; establishes on UCKP-ART-02 that a new canonical
object is required and specifies its purpose, ontology, identity model, lifecycle, and its ownership,
authority and mutation-boundary relationships in full; and validates that specification against dual
authority, class-ownership conflict, append-only evolution, lineage preservation and replay determinism. It
creates no object, designates no authority, allocates no identity, and confers none.*

---

Universal evolution transaction object determined.
Verdict: **C. NEW CANONICAL OBJECT REQUIRED** — specified, not created.
No execution.
No commit.
No registry mutation.
No authority creation.
