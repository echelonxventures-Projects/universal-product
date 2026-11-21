# UCOS Ω∞ — UNIVERSAL FINITE-TO-INFINITE TRANSFORMATION MASTER DETERMINATION

| Field | Value |
|---|---|
| Artifact | `UCOS-OMEGA-INFINITY-FINITE-TO-INFINITE-TRANSFORMATION-MASTER-DETERMINATION.md` |
| Authority | **NONE — DERIVED TRUTH.** This determination creates no identifier, no requirement, no ADR, no phase, no roadmap. It authorizes no implementation, confers no certification, and closes no scope. |
| Mode | READ-ONLY TRANSFORMATION DETERMINATION |
| Baseline commit (HEAD) | `bae59755d7e2d3566c93b89c722b68847145269a` |
| Baseline branch | `integration/recovery-001` |
| Baseline working tree | 333 `git status --porcelain` lines (38 tracked-modified, remainder untracked). Pre-existing; not produced by this determination. |
| Predecessor | `UCOS-OMEGA-INFINITY-UNIVERSAL-INFINITE-EXISTENCE-REALITY-KNOWLEDGE-CAPABILITY-EVOLUTION-COMPLETENESS-DETERMINATION.md` — verdict **PARTIALLY PROVEN** |
| Scope | 19 transformation domains, 63 transformation analyses, finite constraint register, runtime authority register, ownership dependency analysis, implementation dependency graph, validation and certification requirements, risk register, readiness assessment |
| Transformation classification vocabulary | READY FOR TRANSFORMATION · REQUIRES AUTHORITY DECISION · REQUIRES FOUNDATION CHANGE · REQUIRES NEW CAPABILITY · BLOCKED |
| Discovery | **Not repeated.** All evidence is inherited from the determinations listed in §2. |

---

## 1. Objective

Determine the complete transformation path required to evolve UCOS Ω∞ from its measured **PARTIALLY PROVEN** state into a truly infinite and unlimited evolutionary substrate.

This determination establishes, for every known limitation:

- the finite constraint and why it is finite
- the universal target state
- the architectural transformation required
- the existing capability that can be reused
- the extension required
- the dependency order
- the validation and certification requirements
- the risk of transformation
- whether transformation is an engineering act or an authority act

### 1.1 What this determination deliberately does not do

It does not implement, plan, schedule, sequence into phases, create identifiers, or authorize work. It does not convert a gap into a fix. Where a limitation is a **constitutional intent rather than a defect**, it says so and refuses to treat its removal as an engineering task.

### 1.2 The correction this determination must make first

The directive frames every finite boundary as a limitation to be removed. That framing is incorrect for three classes of constraint, and proceeding on it would produce an implementation programme that damages the architecture:

1. **Some finite boundaries are the architecture working.** `SystemType.UNKNOWN`, the requirement that an unregistered serialization must always remain unregistered, the refusal to build a predictive engine, the refusal of a rollback path, and the refusal of an evolution registry are all deliberate. Removing them reduces the system's universality.
2. **Some finite boundaries are constitutional intent, not defect.** The protocol prohibition (`USL-15`) and the absence of a UI runtime are declared design positions. Transforming them is an **amendment**, requiring an authority decision about what UCOS Ω∞ is for — not a remediation.
3. **Some finite boundaries are true invariants.** The 4 root primitives and the 7-level hierarchy grammar are ratified. A determination that lists them as defects to be opened is proposing to dissolve the constitution.

Accordingly, every transformation analysis below carries an explicit judgment on whether the constraint **should** be transformed, separate from whether it **can** be.

---

## 2. Evidence Baseline

### 2.1 Determinations relied upon

Discovery is not repeated. Conclusions are inherited, with cross-references preserved.

| Determination | Inherited conclusion |
|---|---|
| `UCOS-OMEGA-INFINITY-UNIVERSAL-INFINITE-EXISTENCE-REALITY-KNOWLEDGE-CAPABILITY-EVOLUTION-COMPLETENESS-DETERMINATION.md` | **PARTIALLY PROVEN.** 0 ASSIMILATED / 19 PARTIALLY / 7 NOT YET at dimension level; 90 findings; 50 enumeration constraints, 13 pattern constraints, 15 technology assumptions; 24 architectural defects; 30 contradictions (27 live); 2 of 13 expansions DISPROVEN |
| `UCOS-OMEGA-INFINITY-UNIVERSAL-TRUTH-AUTHORITY-RUNTIME-INDEPENDENCE-DETERMINATION.md` | **PARTIALLY PROVEN.** TA-01…TA-26, TX-01…TX-20; 13 truth objects: 4 SUPPORTED / 2 PARTIALLY / 7 UNSUPPORTED; second mutable authority `DEFAULT_VOCABULARIES`; UCAF binds 1 decider of 14 capabilities |
| `UCOS-OMEGA-INFINITY-CANONICAL-KNOWLEDGE-RUNTIME-TRUTH-BOUNDARY-DETERMINATION.md` | **PARTIALLY PROVEN.** CR-01…CR-24; 43 of 72 admissible kinds (59.7%) runtime-dependent; CR-04 root cause = no committed existence document; CR-23 230 of 238 closed enums undisclosed; CR-24 data-only admission disproved with one exception |
| `UCOS-OMEGA-INFINITY-UNIVERSAL-IDENTITY-CAPABILITY-EVOLUTION-DETERMINATION.md` | Identity capability evolution scope and constraints |
| `UCOS-OMEGA-INFINITY-IDENTITY-DETERMINISTIC-VALIDATION-BOUNDARY-DETERMINATION.md` | Identity validation boundary; deterministic validation limits |
| `UCOS-OMEGA-INFINITY-UNIVERSAL-ASSIMILATION-FABRIC-DETERMINATION.md` | **No.** 14 admission surfaces; three islands / one bridge / one one-way street; 6 of 13 categories admissible; *"the obstacle is not a missing engine. It is a missing binding layer between fourteen engines that already exist"* |
| `UCOS-OMEGA-INFINITY-ASSIMILATION-FABRIC-AUTHORITY-BOUNDARY-DETERMINATION.md` | Assimilation authority boundary |
| `UCOS-OMEGA-INFINITY-UNIVERSAL-IMPLEMENTATION-PLANNING-DETERMINATION.md` | Implementation planning constraints |
| `UCOS-OMEGA-INFINITY-100-PERCENT-CLOSURE-MASTER-REGISTER.md` | Closure register; ID-06 GOVERNED with code constrained to 2–8 uppercase ASCII |
| `UCOD-001-UNIVERSAL-CONSTITUTIONAL-OWNERSHIP-DETERMINATION.md` | Ownership **27.86% closed** — 151/542 owned, 391 unowned, **0% ratified**; machinery production-ready, data 27.86% populated |
| `CANONICAL-AUTHORITY-DETERMINATION.md` | No single canonical-authority artifact; three mutually disclaiming planes; declaration and enforcement *"do not share a key"* |
| `UNAF-001-UNIVERSAL-NUCLEUS-ARCHITECTURE-FREEZE.md` | 36-facet contract frozen; NUC-ZF **CONDITIONAL** on ZF-1…ZF-5; *"ZF-1..ZF-5 are the ONLY items requiring code change"* |
| `RTBD-001-REPOSITORY-TRUTH-BOUNDARY-DETERMINATION.md` | Artifact-layer reconstruction proven byte-identical from fresh clone |
| `UNIVERSAL-EVOLUTION-MODEL-DETERMINATION.md` | Evolution Registry REFUSED; Rollback Point REFUSED — both with reasons |
| `GOVERNED-EVOLUTION-STATE-DETERMINATION.md` | Governed evolution state defined; motivating incident: 140 identifiers minted as a side effect of a drift check |
| `UNIVERSAL-ARTIFACT-LIFECYCLE-DETERMINATION.md` | Six incompatible lifecycle models; determination artifacts in governance void |
| `REQ-43-STORAGE-NEUTRALITY-DETERMINATION-REPORT.md` | Storage neutrality for `KnowledgeStore` **declined**, four criteria fail |
| `03-CONSTITUTIONAL-UNBOUNDEDNESS-CERTIFICATION.md` | 16 axes CERTIFIED UNBOUNDED on prose evidence only — **cannot support the property**; Axes 13–14 contradicted by measurement |

### 2.2 The three measurements that anchor this determination

Reproduced independently in the predecessor determination, not taken on report:

- **M-B — Runtime-dependent validity.** Same commit, zero file changes: `is_well_formed("UCOS-CLSS-8966ca9e8d02")` → `False` before `engine.ceu.catalog.bootstrap()`, `True` after.
- **M-C — Mutation classification non-functional.** `RULE_PREDICATES` = R-01…R-08; `validate_rule_coverage` → `("rule 'R-09' is declared but no predicate implements it",)`; `classify()` returns `status='ERROR'` for **every** subject.
- **M-A — Closed enumeration census.** 239 closed `Enum` subclasses in production trees; 230 undisclosed.

### 2.3 Evidence limits carried forward

- Numeric findings quoted from prior determinations were not re-executed except M-A/M-B/M-C.
- The working tree carries 38 pre-existing tracked modifications not analysed as intended change.
- No claim is made about surfaces neither read nor executed.

---

## 3. Current Architectural State

### 3.1 The measured position

UCOS Ω∞ is an **open evolutionary substrate at the population layer and a bounded one at the schema layer**. It accepts unlimited new *instances* of things it already knows how to describe, in frames it has never met, without redesign. It cannot accept a new *kind of description* without constitutional amendment, cannot durably retain what it admits, cannot presently classify anything new at all, cannot represent a technology or protocol, and cannot locate the authority owning most of what it already contains.

### 3.2 What is sound and must not be disturbed

Twelve independently sound foundations, each carrying its own evidence and unaffected by the defect chains:

| # | Foundation | Property that must survive transformation |
|---|---|---|
| S-01 | Location/frame resolver | No axis value in code; no defaults; UNRESOLVED with derivation path; off-world/orbital/virtual/distributed/interstellar frames already resolve |
| S-02 | Temporal model | No clock; never normalises; refuses bare values; INCOMPARABLE reachable |
| S-03 | Measurement registry | 9 peer systems, SI *"never the default"*, `non-human` and `unknown` first-class; conversions as relationships carrying string terms |
| S-04 | Serialization registry | Openness enforced bidirectionally — fails if nothing is left to admit |
| S-05 | Persistence suite | 10 interchangeable backends, interchangeability measured by digest equality, 52 passing tests |
| S-06 | Capability register | Machine-checked zero-enumeration; governing modules named as data; admission by measurement, not declaration |
| S-07 | Pipeline contract | Pipelines declared as data; order derived; handler registry open; unregistered handler fails closed |
| S-08 | Non-termination | `is_terminal` returns `False` because no state could return `True` |
| S-09 | Evolution refusals | No predictive engine; no rollback; no second identity authority |
| S-10 | Certification integrity | Content-addressed, digest-anchored, deterministic ordering, rules and frames injectable |
| S-11 | Ownership resolution | Fail-closed; `OwnershipFabricationError` rather than inference; grain declared not hardcoded |
| S-12 | Artifact-layer reconstruction | Every gitignored product regenerates byte-identically from a bare fresh clone |
| S-13 | Vocabulary mechanism | Append-only, refuses redefinition, register-then-use, openness **proved by probe** (`is_extensible`) |
| S-14 | Anti-closure gate | `check_open_world` fails on bound tokens, closed registries, claimed terminal states |

S-13 and S-14 are the two mechanisms every transformation below reuses. They are the reason no transformation in this determination requires a new capability of the kind the repository does not already possess.

### 3.3 The seven defect chains

Inherited from the predecessor §34.1, restated as transformation inputs:

| Chain | Root | Consequence |
|---|---|---|
| CH-1 | No committed existence document | Existence/entity/knowledge/capability admission is non-durable; 43 of 72 kinds; 9 enforcement sites |
| CH-2 | Single-process determinism harness; zero of 29 gates vary initialization order | CH-1 is undetectable by any existing gate |
| CH-3 | One missing mutation predicate (R-09) | **Nothing new can be classified anywhere, in any dimension, right now** |
| CH-4 | 391/542 unowned; 0% ratified; three disclaiming planes; UKAP/UREE blocked on Article 28 | No located authority can admit a change |
| CH-5 | Unrestricted import from unvalidated JSON, pre-validation | The sole open-kind mechanism is an execution-trust hole |
| CH-6 | 33 facets / 15 stages / 1 certification class / 16 context kinds / 6 evidence kinds / 13 reasoning kinds | A new dimension of description is an amendment in every dimension |
| CH-7 | Frames open, computation absent | The system can address any future spatial/temporal/measurement/value reality and cannot compute in most |

### 3.4 The structural asymmetry to be transformed

```
CURRENT
  population layer  →  OPEN     (unbounded instances, registered vocabularies, data-driven frames)
  schema layer      →  CLOSED   (239 enums; new kinds are amendments)
  durability layer  →  ABSENT   (admitted kinds live in process memory)
  authority layer   →  UNOWNED  (72% of concepts have no owner of record)
  detection layer   →  BLIND    (no gate varies initialization order)
```

Transformation must close the durability, authority and detection layers before touching the schema layer. Opening the schema layer first would multiply undurable, unowned, undetectable kinds.

---

## 4. Universal Target Architecture

### 4.1 The target, stated structurally

```
                        CANONICAL KNOWLEDGE (committed, tracked, human-authored)
                                    │
                        DETERMINISTIC RECONSTRUCTION
                                    │
                              VALIDATION
                                    │
                         RUNTIME PROJECTION (never authoritative)
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
   MEANING LAYER              CAPABILITY LAYER            EVOLUTION LAYER
   (what a thing is)          (what can be done)          (how it changes)
        │                           │                           │
   registered kinds           registered capabilities     registered stages
   registered dimensions      registered handlers         registered transitions
   registered vocabularies    registered providers        append-only ledger
        │                           │                           │
        └───────────────────────────┼───────────────────────────┘
                                    │
                        OWNERSHIP + AUTHORITY RESOLUTION
                            (every subject owned, ratified)
                                    │
                        TRUST → VALIDATION → IMPACT → EXECUTION
                                    │
                        EVIDENCE → CERTIFICATION → EVOLUTION
                                    │
                              (re-entry, never terminal)
```

### 4.2 The five target invariants

Every transformation below is measured against these. They are stated as properties an instrument could test, not as aspirations.

| # | Target invariant | Testable form |
|---|---|---|
| TI-1 | **Durability** — anything admitted survives process death | Delete runtime memory, reload canonical knowledge, reconstruct, compare: identical |
| TI-2 | **Initialization independence** — no verdict depends on process history | The same subject yields the same verdict in a fresh interpreter and in a bootstrapped one |
| TI-3 | **Kind openness** — a new kind of description enters by registration | A probe kind, never seen by the release, is admitted, persisted, and honoured by a fresh validator |
| TI-4 | **Owned admission** — nothing is admitted without a resolvable owner | Every admitted subject resolves to exactly one ratified owner, or admission fails closed |
| TI-5 | **Trusted admission** — nothing executes before it is trusted and validated | No code path imports or invokes from an unverified descriptor |

TI-1, TI-2 and TI-5 are **achievable with existing capability**. TI-4 requires an authority act. TI-3 requires a constitutional decision about whether the 33-facet frame is an invariant or a limitation.

### 4.3 What the target explicitly does not include

Recording this prevents the transformation programme from acquiring scope the architecture has already refused:

- **No predictive engine.** The refusal at `engine/uaue/simulation.py:1-25` is correct and is retained in the target.
- **No rollback path.** The refusal in `UNIVERSAL-EVOLUTION-MODEL-DETERMINATION.md` §1 is correct and is retained.
- **No second identity authority.** `CAA-INV-04` is retained.
- **No corpus-tuned thresholds.** The discipline at `engine/uckp/intelligence.py:9-13` is retained.
- **No autonomous source self-modification** unless an authority decides otherwise. The three confinements are a safety property, not a gap.

---

## 5. Transformation Principle

### 5.1 The transformation under determination

```
FINITE IMPLEMENTATION  →  UNIVERSAL CAPABILITY  →  AUTONOMOUS EVOLUTION
```

### 5.2 Answer to the primary question

> *Can every currently finite implementation boundary be transformed into an open universal capability without architectural redesign?*

**No — and the distinction matters more than the answer.** Partitioning the 78 constraints in §25:

| Partition | Count | Transformable without redesign? |
|---|---|---|
| True invariants — must not be transformed | 7 | Not applicable; transformation would be regression |
| Representation choices — transformable by registration | 22 | **Yes**, using S-13 |
| Implementation limitations — transformable by extension | 25 | **Yes**, using S-13/S-14 and existing engines |
| Architectural defects — transformable, 21 of 24 without redesign | 24 | **21 yes, 3 no** |

The three requiring more than extension:

- **C-36 protocol prohibition** — not a defect to fix but a **constitutional position to amend**. Removing it changes what UCOS Ω∞ is. REQUIRES AUTHORITY DECISION.
- **CH-4 ownership authority** — the act that would ratify ownership has **no competent authority inside the repository**. BLOCKED on an external act.
- **CH-6 the 33-facet frame** — opening it is, by the repository's own doctrine, a constitutional amendment. REQUIRES AUTHORITY DECISION on whether 33 is invariant or limitation.

So: **75 of 78 constraints are transformable without architectural redesign. 3 are not, and none of those 3 is an engineering problem.**

### 5.3 The principle that governs ordering

> **Durability before openness. Detection before durability. Authority before admission. Trust before execution.**

Each clause is forced by evidence rather than preference:

- **Detection before durability**, because CH-2 means a durability fix cannot be verified as effective.
- **Durability before openness**, because opening the schema layer first (CH-6) multiplies kinds that evaporate at process exit (CH-1).
- **Authority before admission**, because CH-4 means an admitted subject cannot be owned, and unowned admission accumulates ungoverned state.
- **Trust before execution**, because CH-5 means the one open-kind mechanism is also the one arbitrary-execution mechanism.

### 5.4 The autonomous evolution question

`AUTONOMOUS EVOLUTION` as the third term is not reachable from the current state by extension, and this determination declines to treat it as an engineering target. Evidence: evolution is externally triggered, candidates are not self-generated, the controller *"conducts; it does not decide"*, no parameters are updated by any run, and source self-modification is prevented by three independent confinements. Making evolution autonomous is a **change of kind**, not of degree, and it depends on TI-1 through TI-5 all holding first — because an autonomous system operating on undurable, unowned, undetectable, untrusted state is the worst configuration available. Classification: **REQUIRES AUTHORITY DECISION**, dependent on all five target invariants.

---

## 6. Identity Transformation

**Target:** Identity Meaning → Authority → Namespace → Representation → Lineage → Evolution

### T-6.1 — Validation verdict depends on process history

1. **Current finite state.** An identifier's well-formedness is decided against mutable module globals populated only by `bootstrap()`.
2. **Evidence.** M-B (reproduced): `is_well_formed("UCOS-CLSS-8966ca9e8d02")` → `False` before bootstrap, `True` after, same commit, zero file changes. `engine/registry/universal/identity.py:156,159` empty globals with no persistence writer; `:162-199` `register_kind` writes only to memory; `:286-309` readers. Populator `engine/ceu/existence.py:898-910`, whose docstring concedes *"this function never stores one."* Leak vector `engine/nucleus/authority.py:66-76` (`@cache roles_holding` calls `bootstrap()` then hides it). 43 of 72 kinds (59.7%) affected; 9 enforcement sites inherit the predicate, including the sole constitutional mutation gateway (`engine/constitution/gateway.py:203`) and a live property call in the legality proof (`engine/constitution/metadata.py:301-303`).
3. **Why it is finite.** The kind space has no persisted representation. Truth is a side effect of an import order.
4. **Universal target state.** TI-1 + TI-2: identity kinds are canonical knowledge; a fresh validator honours every registered kind; no verdict varies with initialization.
5. **Required architectural transformation.** Persist the kind space as canonical knowledge and resolve it deterministically on load. **No new engine.** The mechanism already exists and is journal-verifying.
6. **Existing reusable capability.** `engine/ceu/existence.py:733 to_document()` / `:773 from_document()` (replays verbatim, refuses re-derivation, fails closed on `verify_audit()`) / `:868 reconstruct()` (measures losslessness). Tests at `engine/tests/ceu/test_reconstruction.py`.
7. **Required extension.** A committed existence document, plus a production load path invoked before any validation. **REUSE + wire**, not build.
8. **Dependency.** Requires T-19.1 (initialization-independence measurement) to be verifiable. Blocks T-7.1, T-14.1, T-17.1, and every kind-openness transformation.
9. **Validation requirement.** VR-01, VR-02 (§29).
10. **Certification requirement.** CR-01 (§30).
11. **Risk.** R-01 (§31) — the reconstruction test's own fixture calls `bootstrap()`, so the existing test cannot detect failure of this transformation.
12. **Classification.** **READY FOR TRANSFORMATION**

### T-6.2 — Three mutually irreconcilable mint pathways, plus a fourth

1. **Current finite state.** Identity is minted by three independent schemes; a fourth exists in the assimilation framework whose identity no registry can resolve.
2. **Evidence.** `engine/uckp/identity.py` (URN + UUIDv5), `engine/registry/universal/identity.py` (`UCOS-<CODE>-<12hex>`), `engine/kernel/identity.py` (`UMK-<SLUG>-<12hex>`, open metatype), plus the assimilation content-addressed `source_id`. `…ASSIMILATION-INFINITE-INTELLIGENCE-INTEGRATION-DETERMINATION.md` §1.4 — *"structurally unreconcilable with any constitutional identity."* Governance model is `MULTIPLE_INDEPENDENT_BOUNDED_NAMESPACES` with *"No universal identity authority created"*.
3. **Why it is finite.** Not finite in count — finite in *resolvability*. An identity from one plane cannot be interpreted by another.
4. **Universal target state.** Identity Meaning is resolvable across planes: a crosswalk exists, or one plane is declared governing.
5. **Required architectural transformation.** Either a declared crosswalk (federation) or a declared governing mint. **This is a decision, not a build.**
6. **Existing reusable capability.** `engine/registry/universal/dictionary.py` (reproducibility verification, `"closed_set": False`); lineage projection.
7. **Required extension.** A crosswalk registry, if federation is chosen.
8. **Dependency.** Requires T-22.2 (authority plane resolution) — the same missing-shared-key problem.
9. **Validation requirement.** VR-03.
10. **Certification requirement.** CR-02.
11. **Risk.** R-02 — declaring one mint governing may invalidate identifiers already issued by the others; `CAA-INV-04` forbids a second identity authority, so federation must not become one.
12. **Classification.** **REQUIRES AUTHORITY DECISION**

### T-6.3 — Identifier width bounded at 10⁶ per family (ZF-1)

1. **Current finite state.** `^UCOS-[A-Z][A-Z0-9]{1,11}-[0-9]{6}$`.
2. **Evidence.** `00-BOOK/SCHEMAS/artifact.schema.json:20`; `engine/uckp/alignment.py:89`; `UNAF-001:141-147` names it ZF-1 and unfixed.
3. **Why it is finite.** A fixed-width numeric field. The family prefix is open; the sequence is not.
4. **Universal target state.** Identifier representation carries no cardinality ceiling.
5. **Required architectural transformation.** Widen or make variable-width the numeric field, in schema and in the pattern constant, coherently.
6. **Existing reusable capability.** 117 append-only per-category counters; self-opening path-derived classifier (`00-BOOK/tools/config.py:488-494`); `dictionary.py` emits `"closed_set": False, "upper_limit": None` — the claim already exists.
7. **Required extension.** Schema pattern change plus every mirrored constant, in lockstep.
8. **Dependency.** Requires T-15.1 (artifact schema openness), since both edit the same schema. Depends on T-6.1 for durability of any new family.
9. **Validation requirement.** VR-04 — all 1,461 existing artifact records must remain valid.
10. **Certification requirement.** CR-03.
11. **Risk.** R-03 — the pattern is mirrored in at least three places; divergence produces the C-34/C-35 drift failure mode already on record.
12. **Classification.** **READY FOR TRANSFORMATION**

### T-6.4 — Extension kind code constrained to 2–8 uppercase ASCII

1. **Current finite state.** `[A-Z][A-Z0-9]{1,7}`.
2. **Evidence.** `engine/registry/universal/identity.py:189`; `UCOS-OMEGA-INFINITY-100-PERCENT-CLOSURE-MASTER-REGISTER.md:111` rates ID-06 GOVERNED with this caveat.
3. **Why it is finite.** A code-space bound: 26 × 36⁷ is large but the alphabet excludes non-ASCII, so a civilisation with a different script cannot supply a native code.
4. **Universal target state.** Codes are opaque registered tokens, not constrained glyph sequences.
5. **Required architectural transformation.** Relax the alphabet, or declare the code a display projection of an opaque identity.
6. **Existing reusable capability.** `engine/kernel/identity.py` already accepts **any Unicode** non-whitespace segment — the pattern to follow exists in-repo.
7. **Required extension.** Alphabet relaxation, or a declared projection boundary.
8. **Dependency.** T-6.1.
9. **Validation requirement.** VR-05.
10. **Certification requirement.** CR-03.
11. **Risk.** R-04 — low; but collision semantics must be re-verified under a wider alphabet.
12. **Classification.** **READY FOR TRANSFORMATION**

### T-6.5 — The birth contract has zero production callers

1. **Current finite state.** `engine/object_birth/` implements identity-before-existence and nothing calls `birth()`.
2. **Evidence.** Importers are two tests only; sole non-test reach is the CLI gate subprocess at `verify.sh:502`.
3. **Why it is finite.** Not a representational bound — an **adoption** bound. The contract cannot govern what does not use it.
4. **Universal target state.** Every first-class entity is born through the declared contract.
5. **Required architectural transformation.** Wire the contract into the mint paths. Reuse only.
6. **Existing reusable capability.** `engine/object_birth/birth.py:50 birth()`; the object-birth ledger is one of the four reconstruction-SUPPORTED objects.
7. **Required extension.** Call sites.
8. **Dependency.** Requires T-6.2 (which mint governs) before wiring, or the contract will be wired to one of three irreconcilable planes.
9. **Validation requirement.** VR-06.
10. **Certification requirement.** CR-02.
11. **Risk.** R-05 — `GOVERNED-EVOLUTION-STATE-DETERMINATION.md` §1 records the precedent: a drift check minted 140 permanent identifiers as a side effect. Wiring birth into hot paths risks repeating it.
12. **Classification.** **REQUIRES AUTHORITY DECISION** (blocked behind T-6.2)

**Domain verdict: 3 READY FOR TRANSFORMATION · 2 REQUIRES AUTHORITY DECISION.** Identity is the highest-leverage domain: T-6.1 alone unblocks CH-1 and nine enforcement sites.

---

## 7. Entity Transformation

**Target:** Unknown Existence → Entity Recognition → Identity → Context → Evolution

### T-7.1 — Root primitives are not instantiable

1. **Current finite state.** `EXISTENCE`, `RELATIONSHIP`, `TRANSFORMATION` exist as string ids in a declaration a gate cross-checks against prose. No `Primitive` class; nothing anchors to them.
2. **Evidence.** `P1-A-01-ROOT-ONTOLOGY-DISCOVERY-REPORT.md` §3 GAP A-1 — *"appear in no `.py` and no `.json` file… only as markdown prose."* `00-MASTER/UCPA-000001/ucpa-declaration.json` declares `"authority": "NONE — DERIVED TRUTH."` No UCKO references `ONT-01…ONT-04`.
3. **Why it is finite.** The ontology is *measured*, never *instantiated*. Entity recognition has nothing to recognise against.
4. **Universal target state.** An unknown existence is recognised by anchoring to a root primitive, then acquires identity, context and an evolution path.
5. **Required architectural transformation.** Make primitives representable objects that instances reference. This is additive to the existing measurement gate.
6. **Existing reusable capability.** `engine/root_ontology/{model,contract,gate}.py` (no hardcoded reality); the 33-row `facet_reduction` mapping already binds every facet to a primitive; `UCKO.ontology: OntologyRef` already exists as a reference field.
7. **Required extension.** A primitive object model, and a UCKO anchor to it.
8. **Dependency.** Requires T-6.1 (durability) — otherwise anchors evaporate. Blocks nothing else, but is blocked by CH-6 if a fifth primitive is ever needed.
9. **Validation requirement.** VR-07.
10. **Certification requirement.** CR-04.
11. **Risk.** R-06 — the four primitives are **ratified**. Instantiating them must not become a path to amending them. `UCPA-L-04` (nothing reduces to the axiom) must continue to hold.
12. **Classification.** **READY FOR TRANSFORMATION**

### T-7.2 — Graph-node entity types are a closed 6-tuple

1. **Current finite state.** `ENTITY_TYPES = ("Context","ContextDimension","ContextValue","ContextFrame","Observer","ContextTaxon")` — *"Nothing else may be a graph node."*
2. **Evidence.** `engine/context/ontology.py:37-44`.
3. **Why it is finite.** A closed tuple with no registration path.
4. **Universal target state.** Node types registered; an unforeseen node class admissible.
5. **Required architectural transformation.** Convert to a registered vocabulary.
6. **Existing reusable capability.** S-13 — `engine/uckp/vocabulary.py`, append-only, refuses redefinition, `is_extensible` probe.
7. **Required extension.** Vocabulary conversion plus acyclicity re-verification.
8. **Dependency.** T-6.1. Related to T-9.3 (context vocabularies).
9. **Validation requirement.** VR-08.
10. **Certification requirement.** CR-04.
11. **Risk.** R-07 — the closure currently guarantees the graph's shape; opening it requires the relation rules to remain total over the wider node set, or unbounded edges become possible (the exact condition `ContextOntology.__init__` refuses).
12. **Classification.** **READY FOR TRANSFORMATION**

### T-7.3 — Entity kinds admitted only in process memory

1. **Current finite state.** `register_kind()` is *"the only extension mechanism"* and writes to empty module globals.
2. **Evidence.** As T-6.1. `_EXTENSION_KIND_CODES` / `_EXTENSION_CODE_KINDS`; no production caller; no data file; no loader.
3. **Why it is finite.** Extension is real but non-durable.
4. **Universal target state.** TI-3 — a probe kind never seen by the release is admitted, persisted, and honoured by a fresh validator.
5. **Required architectural transformation.** Same as T-6.1 — this is the same defect seen from the entity dimension.
6. **Existing reusable capability.** As T-6.1.
7. **Required extension.** As T-6.1.
8. **Dependency.** **Identical to T-6.1.** Confirms the directive's question *"does identity precede entity expansion?"* — **yes, and by the same artifact.**
9. **Validation requirement.** VR-01, VR-02.
10. **Certification requirement.** CR-01.
11. **Risk.** R-01.
12. **Classification.** **READY FOR TRANSFORMATION**

**Domain verdict: 3 READY FOR TRANSFORMATION.** Entity expansion is entirely downstream of identity durability.

---

## 8. Reality Transformation

**Target:** Reality capability without predefined realities

### T-8.1 — The mandatory reality-axis chain is code, not data

1. **Current finite state.** `REALITY_CONTEXT_AXES = ("existence","reality","observer","spatial","temporal")`; `AXIS_DERIVATION` is a ~19-row module tuple whose comment claims *"the set is open"*.
2. **Evidence.** `engine/context/location.py:84-90`, `:90-116`. `introduced_axes()` (`:649-658`) lets ontology extension change axis *ownership* but not the chain.
3. **Why it is finite.** The derivation graph is a Python constant, in a module whose stated property is that no axis *value* appears in it — the values are data, the **structure** is not.
4. **Universal target state.** A future reality requiring a sixth mandatory axis is a data change.
5. **Required architectural transformation.** Move `AXIS_DERIVATION` and `REALITY_CONTEXT_AXES` into the frame catalogue that already holds every axis value.
6. **Existing reusable capability.** `engine/context/catalog/reference-frames.json` — already declares 14 frames including a zero-axis root and a deliberately partial frame; `FrameRegistry.resolve` already reports UNRESOLVED with the derivation path.
7. **Required extension.** Declaration of the derivation graph as data; resolver reads it.
8. **Dependency.** T-6.1 for durability of a new axis. Enables T-9.2, T-10.1, T-11.1.
9. **Validation requirement.** VR-09 — all 14 existing frames must resolve identically before and after.
10. **Certification requirement.** CR-05.
11. **Risk.** R-08 — `require_reality_context` is the fail-closed gate preventing interpretation without reality. Moving its axis list to data means a data edit can weaken a constitutional gate. The gate must refuse an *empty or shrinking* axis set.
12. **Classification.** **READY FOR TRANSFORMATION**

### T-8.2 — Two coexisting truth models, neither governing

1. **Current finite state.** Two truth models coexist; neither is declared governing.
2. **Evidence.** TA-01. `CANONICAL-AUTHORITY-DETERMINATION.md:17-32,34` — three planes, *"the two do not share a key. This is the root of every conflict in §5."*
3. **Why it is finite.** A new reality entering cannot be told which truth model admits it.
4. **Universal target state.** One declared governing truth model, or declared federation with machine-readable crosswalks.
5. **Required architectural transformation.** A declaration. No build.
6. **Existing reusable capability.** `engine/uckp/law.py` `GOVERNED_CATEGORIES` (35 members, open by Article 17); the CMG registry lattice.
7. **Required extension.** A governing declaration.
8. **Dependency.** Same root as T-6.2 and T-22.2. **All three resolve together or not at all.**
9. **Validation requirement.** VR-10.
10. **Certification requirement.** CR-06.
11. **Risk.** R-09 — declaring one model governing may orphan artifacts authored under the other.
12. **Classification.** **REQUIRES AUTHORITY DECISION**

### T-8.3 — Reality modes are declarable and inert

1. **Current finite state.** `reality_mode` is an open string (*"actual · modelled · simulated · planned · hypothetical"*). Nothing computes over it.
2. **Evidence.** `engine/context/ontology.py:152`; `engine/context/taxonomy.py:361`.
3. **Why it is finite.** Not finite in representation — finite in **consequence**. Declaring a reality simulated has no effect on how it is treated.
4. **Universal target state.** Reality mode is consequential: a simulated reality's assertions cannot be certified as actual.
5. **Required architectural transformation.** Bind reality mode to admission and certification rules.
6. **Existing reusable capability.** `engine/universal_certification/rules.py` — rules are injectable; compliance frames are injectable.
7. **Required extension.** A reality-mode rule set.
8. **Dependency.** T-23.2 (certification subject genericity), since a simulated subject is arguably a different certification class.
9. **Validation requirement.** VR-11.
10. **Certification requirement.** CR-06.
11. **Risk.** R-10 — coupling reality mode to certification could make the existing single-class certification refuse subjects it currently accepts.
12. **Classification.** **READY FOR TRANSFORMATION**

**Domain verdict: 2 READY FOR TRANSFORMATION · 1 REQUIRES AUTHORITY DECISION.**

---

## 9. Context Transformation

**Target:** Dynamic universal context capability across all fifteen named dimensions

### T-9.1 — `ContextKind` is a closed 16-member enum

1. **Current finite state.** 16 members; `coerce()` raises with an `allowed` list. The docstring argues openness from having moved 15→16 — which was a code edit.
2. **Evidence.** `engine/context/taxonomy.py:64-79`, `:82-95`, `:58-62`.
3. **Why it is finite.** Membership is an enum. **The stated openness argument is invalid**: it is true of control flow (nothing branches on a kind) and false of type membership.
4. **Universal target state.** A seventeenth *universal* kind enters by registration.
5. **Required architectural transformation.** Convert the universal kind set to a registered vocabulary; retain `coerce` as a fail-closed *registered-membership* check rather than an enum check.
6. **Existing reusable capability.** S-13. Also `ContextTaxon.kind` is **already** an open string, and `ContextTaxonomy.extend()` already admits future taxa under bounded rules — the mechanism exists one layer down.
7. **Required extension.** Vocabulary conversion; `universal_kinds()` / `future_kinds()` separation preserved.
8. **Dependency.** T-6.1 for durability. Part of CH-6.
9. **Validation requirement.** VR-12 — all 16 existing kinds resolve identically; a probe kind is admitted and honoured by a fresh validator.
10. **Certification requirement.** CR-07.
11. **Risk.** R-11 — universality currently *stamps* records (`registry.py:184`). If universality becomes registrable, a data edit could declare an arbitrary kind universal. The registration path must require constitutional authority for the universal flag specifically.
12. **Classification.** **READY FOR TRANSFORMATION**

### T-9.2 — Context authority, lifecycle and relation vocabularies have no extension mechanism at all

1. **Current finite state.** `ContextAuthority` (5), `ContextLifecycle` (8, with transition graph), `ContextRelation` (11, closed **by construction** — a relation without a rule cannot exist).
2. **Evidence.** `engine/context/taxonomy.py:107-140`, `:152-214`, `:240-275`; `engine/context/ontology.py:250-318`, `:372-374`.
3. **Why it is finite.** Three closed enums with **no** `extend()` counterpart, unlike kinds and dimensions.
4. **Universal target state.** A future governance model with a different authority gradation, or a future relation semantics, is representable.
5. **Required architectural transformation.** Registered vocabularies with rules registered alongside members, preserving the total-precedence and rule-totality invariants.
6. **Existing reusable capability.** S-13; `RELATION_RULES` already pairs each relation with a rule — the pairing discipline to preserve is already expressed.
7. **Required extension.** Vocabulary conversion for three vocabularies plus rule co-registration.
8. **Dependency.** T-9.1. Related to T-13.2 (relationship types) and T-22.1 (evidence kinds) — all four are the same pattern.
9. **Validation requirement.** VR-13 — precedence remains total; every relation retains a rule; no unbounded edge becomes possible.
10. **Certification requirement.** CR-07.
11. **Risk.** R-12 — `ContextAuthority` precedence is **total** and ordering-sensitive. Registering a new authority level requires a declared position in the order, or precedence becomes partial and resolution non-deterministic.
12. **Classification.** **READY FOR TRANSFORMATION**

### T-9.3 — `VALUE_TYPES` is a closed 5-tuple

1. **Current finite state.** `("string","number","boolean","list","mapping")`; `DimensionSpec.__post_init__` refuses unknown types.
2. **Evidence.** `engine/context/ontology.py:47`, `:76`.
3. **Why it is finite.** A future dimensional structure requiring a tensor, interval, partial order, distribution or incomparable lattice value cannot be typed.
4. **Universal target state.** Value types registered with their own validators.
5. **Required architectural transformation.** A value-type registry where each type registers a check function.
6. **Existing reusable capability.** `check_values()` / `require_values()` already dispatch on type; S-13 for the registry.
7. **Required extension.** Type registry with co-registered validators.
8. **Dependency.** T-9.1. Enables T-12.2 (measurement magnitudes) and T-10.2 (coordinates as typed values).
9. **Validation requirement.** VR-14.
10. **Certification requirement.** CR-07.
11. **Risk.** R-13 — a registered type whose validator is unsound admits malformed dimension values; validators must be pure and total, matching the existing rule discipline.
12. **Classification.** **READY FOR TRANSFORMATION**

### T-9.4 — Context is populated with the repository's self-description; one instance per kind

1. **Current finite state.** All 16 kinds populated with UCOS describing itself. Proven context coverage measured at **6/15 = 40%**; the `linguistic→language` crosswalk unasserted.
2. **Evidence.** `engine/context/catalog.py:37+`; `UCOS-MIP-000003-MASTER-IMPLEMENTATION-PLAN-V3.md:232-234`.
3. **Why it is finite.** Openness is **asserted, not exercised**. A single instance cannot demonstrate a second, alien instance resolves.
4. **Universal target state.** ≥2 instances per kind, at least one non-self-describing.
5. **Required architectural transformation.** Population, not code. Data only.
6. **Existing reusable capability.** The entire context subsystem; the 14 declared reference frames provide ready alien contexts (planetary-b4, orbital-station-o2, virtual-realm-v9, distributed-mesh-d3, interstellar-corridor-i1).
7. **Required extension.** A second context set declared against an existing alien frame.
8. **Dependency.** T-8.1 (axis derivation as data) makes this materially easier; not strictly blocking.
9. **Validation requirement.** VR-15 — resolution succeeds for two disjoint context sets without code change.
10. **Certification requirement.** CR-07.
11. **Risk.** R-14 — lowest risk transformation in this determination; it is a data addition whose failure mode is a failed resolve, not a corrupted verdict.
12. **Classification.** **READY FOR TRANSFORMATION**

**Domain verdict: 4 READY FOR TRANSFORMATION.** T-9.4 is the cheapest proof-of-openness available anywhere in the programme and should be understood as the empirical test of T-9.1 through T-9.3.

---

## 10. Spatial Transformation

**Target:** Universal spatial representation with no fixed locations or coordinate assumptions

### T-10.1 — No fixed locations exist to remove

1. **Current finite state.** **Already universal.** No axis value appears in `location.py`; frames are data; there is no default, no built-in, no inference; an undeclared axis becomes UNRESOLVED with its derivation path.
2. **Evidence.** `engine/context/location.py` docstring property #1 — *"Grep this module for a calendar name and you will not find one."* `engine/context/catalog/reference-frames.json` — 14 frames including a zero-axis root *"the proof that the resolver has no built-in assumptions to fall back on"*, plus `planetary-b4` (*"required no code change"*), `orbital-station-o2`, `virtual-realm-v9`, `distributed-mesh-d3`, `interstellar-corridor-i1`, `partial-frame-p0`. Backstop `engine/kernel/compliance.py:37-56` `PROHIBITED_TOKENS` includes `country`, `earth`, `calendar`, `timezone`.
3. **Why it is finite.** **It is not.** The directive's instruction to *"remove fixed locations"* has no target: there are none. Earth/Mars/Moon are demonstrably examples, not architecture, in this layer.
4. **Universal target state.** Already achieved for addressing.
5. **Required architectural transformation.** **None. Preserve.** Any transformation here is regression risk.
6. **Existing reusable capability.** S-01. This is the pattern every other domain should follow.
7. **Required extension.** None.
8. **Dependency.** None. T-8.1 improves it (axis derivation as data) without changing this property.
9. **Validation requirement.** VR-09 — regression protection only.
10. **Certification requirement.** CR-05.
11. **Risk.** R-15 — the risk is *transforming it*. `PROHIBITED_TOKENS` must continue to hold; the zero-axis root frame must continue to exist.
12. **Classification.** **READY FOR TRANSFORMATION** (as preservation; no change required)

### T-10.2 — No coordinate systems, geometry, or spatial-relation algebra

1. **Current finite state.** The `spatial` axis value is an opaque authority reference string. No `latitude`, `longitude`, `EPSG`, `WGS84`, `CoordinateSystem`, or `geodetic` anywhere in `engine/` or `platform/`. SPATIAL's three dimensions are free strings; space is documented as *"path space"*.
2. **Evidence.** `engine/context/ontology.py:169-174`; `engine/context/catalog.py:77-86`; documented intent at `00-MASTER/UCOS-CVR-001/04-…-SPECIFICATION.md:92-119` specifying `body_id`, `location_id`, `coordinate_system_id` + `coordinates` arrays, all marked `[N]` — *"declared, unrealized."*
3. **Why it is finite.** Space is addressable but not computable. There is no registry of coordinate systems, no conversion analogue to `TemporalRegistry`, and no containment/adjacency/distance algebra.
4. **Universal target state.** Coordinate systems registered as peers, conversions declared and refused when undeclared, spatial relations declared with rules.
5. **Required architectural transformation.** Apply the temporal pattern to space. **The design already exists in a sibling module.**
6. **Existing reusable capability.** `engine/temporal/operations.py` `TemporalRegistry` (register systems and conversions, never infer, raise on undeclared pair) is a direct template. `engine/ceu/catalog.py SEED_CONVERSIONS` shows conversions as relationships with string terms. `FrameRegistry` supplies the frame chain.
7. **Required extension.** A spatial coordinate registry, a conversion registry, and a relation rule set — all EXTEND, patterned on existing code.
8. **Dependency.** T-9.3 (typed values) for coordinate magnitudes; T-8.1 for axis structure.
9. **Validation requirement.** VR-16 — a coordinate in an invented system is representable; conversion between two systems with no declared rule is **refused, not improvised**.
10. **Certification requirement.** CR-08.
11. **Risk.** R-16 — the temptation to normalise. If a spatial registry ever adopts a canonical frame, it destroys the property S-01 protects. The `TemporalCoordinate` rule (*"`primary` is never normalised"*) must be replicated exactly.
12. **Classification.** **READY FOR TRANSFORMATION**

**Domain verdict: 2 READY FOR TRANSFORMATION,** one of them as pure preservation. Spatial is the clearest case where the directive's premise (remove fixed assumptions) is already satisfied and the actual gap is elsewhere (computation, not representation).


---

## 11. Temporal Transformation

**Target:** Universal temporal capability

### T-11.1 — No transformation of the model is required; adoption is the gap

1. **Current finite state.** The model is **already universal**: no clock, `primary` never normalised, bare values refused, `Precision` units a free string, `INCOMPARABLE` reachable, conversions registered never inferred, `SystemType.UNKNOWN` making an uninvented reference system representable today. But only **three** non-test production importers exist.
2. **Evidence.** `engine/temporal/coordinate.py:29-41,67-107,110-123,169-253,257-287,291-330`; `operations.py:50-124,127-155,158-183`; no-clock enforced by `engine/tests/unit/test_temporal_contract.py:112-119`. Importers: `engine/knowledge/ukip/relationships.py:43-44`, `contracts.py:50`, and `engine/temporal` itself.
3. **Why it is finite.** Not finite in capability — finite in **reach**. Calendars, clocks, timelines and temporal relations are all representable; almost nothing uses them.
4. **Universal target state.** Identity, birth, baseline, UCKO temporal fields and evidence emitters all carry qualified coordinates.
5. **Required architectural transformation.** Migration. **Zero new capability.** Pure REUSE.
6. **Existing reusable capability.** S-02 in full, plus `engine/temporal/facets.py` (8 lifecycle facets, declared precedence as data, `violations()` reporting incomparable pairs) and `SEED_TEMPORAL_MODELS` (historical, predicted, alternative, simulated, branching, recursive, unknown).
7. **Required extension.** Call-site migration only.
8. **Dependency.** T-11.2 must be decided first — `P4-F-007` records that re-typing `UCKO.temporal_history` would force a default frame at mint, violating REQ-22. The migration is blocked on a **frame-at-mint** decision, not on code.
9. **Validation requirement.** VR-17.
10. **Certification requirement.** CR-09.
11. **Risk.** R-17 — a migration that forces a default frame destroys the property being adopted. This is why non-adoption was deliberate, per `P4-F-007:91-95`.
12. **Classification.** **REQUIRES AUTHORITY DECISION** (frame-at-mint policy)

### T-11.2 — The baseline authority is temporally unaware and certifies dates its own contract refuses

1. **Current finite state.** `baseline_engine.py` (84 KB) contains zero occurrences of `temporal`, `TemporalCoordinate`, `datetime`, `utcnow` or `now(`, and the dates it certifies (`2026-07-30`) are **refused by the repository's own temporal contract**.
2. **Evidence.** `UNIVERSAL-BASELINE-TEMPORAL-CERTIFICATION-DETERMINATION.md:38-53` — recorded as a hidden finite assumption, **not remediated**.
3. **Why it is finite.** A certification authority asserting unqualified Gregorian dates while the constitution requires qualified coordinates. The authority and the contract disagree.
4. **Universal target state.** Baseline temporal claims are qualified coordinates, or the baseline declares itself outside the temporal contract with a stated reason.
5. **Required architectural transformation.** One of two declarations, then either migration or an explicit boundary.
6. **Existing reusable capability.** S-02.
7. **Required extension.** Either qualification of baseline dates, or a declared exemption.
8. **Dependency.** Blocks T-11.1 (the frame-at-mint decision is the same decision). Depends on T-23.3 (what a certification may assert).
9. **Validation requirement.** VR-17, VR-18.
10. **Certification requirement.** CR-09 — this transformation touches a certification and must not be performed as an engineering act.
11. **Risk.** R-18 — re-qualifying already-certified baseline dates changes certified content. An exemption is lower-risk but records a permanent contract hole.
12. **Classification.** **REQUIRES AUTHORITY DECISION**

### T-11.3 — Five evidence emitters assume UTC/ISO-8601

1. **Current finite state.** `datetime.now(UTC).isoformat()` at five sites.
2. **Evidence.** `engine/registry/universal/audit.py:33-35`; `engine/execution_environment/evidence.py:59`; `engine/graph/evidence.py:67`; `engine/graph/architecture/evidence.py:78`; `engine/foundation/obs/logging.py:59`.
3. **Why it is finite.** Unqualified wall-clock strings. In a frame where UTC is meaningless, the evidence timestamps cannot be interpreted.
4. **Universal target state.** Evidence timestamps are qualified coordinates, or evidence time is declared a projection outside the temporal contract.
5. **Required architectural transformation.** Qualification at five sites, or a declared boundary.
6. **Existing reusable capability.** `ReferenceSystem` with `system_identifier` required; the `repository` measurement system and `commit-ordinal` unit already exist as a non-wall-clock alternative.
7. **Required extension.** Five call sites.
8. **Dependency.** T-11.2 (same policy decision).
9. **Validation requirement.** VR-17.
10. **Certification requirement.** CR-09.
11. **Risk.** R-19 — low; these are timestamps *about runs*, not modelled existence. The risk is scope creep into treating them as constitutional temporal claims.
12. **Classification.** **READY FOR TRANSFORMATION** (pending T-11.2 policy)

**Domain verdict: 1 READY FOR TRANSFORMATION · 2 REQUIRES AUTHORITY DECISION.** Temporal is the clearest instance of a **built and unadopted** universal capability; the blocker is a policy question (frame at mint), not engineering.

---

## 12. Measurement Transformation

**Target:** Universal measurement capability

### T-12.1 — The registry is already universal; conversions do not execute

1. **Current finite state.** 13 quantities, 9 peer measurement systems (SI documented as *"one system among many, never the default"*, plus `non-human` and `unknown`), 15 units, 8 scales, conversions as **relationship instances carrying string terms**. But no conversion executor, no dimensional analysis, and no `Quantity`/`Measurement` value type.
2. **Evidence.** `engine/ceu/catalog.py:313-330,332-345,347-363,370-379,269-280`, relationship type `converts-to` at `:186-190`. `engine/context/taxonomy.py:51-57` concedes *"no measurement engine exists behind it."*
3. **Why it is finite.** Declarable, not computable. A future measurement system can be declared but cannot be used to validate a measured claim.
4. **Universal target state.** A magnitude bound to a unit; conversion executed only where declared; refusal where undeclared.
5. **Required architectural transformation.** A conversion executor and a magnitude+unit value type, patterned on the temporal registry.
6. **Existing reusable capability.** `engine/temporal/operations.py convert()` — raises `no declared conversion between reference systems` rather than improvising. That is exactly the required semantics. `SEED_CONVERSIONS` terms are already strings so *"the substrate never has to interpret a float it did not compute."*
7. **Required extension.** Executor + value type. EXTEND.
8. **Dependency.** T-9.3 (typed values) for the magnitude type.
9. **Validation requirement.** VR-19 — a conversion between two systems with no declared rule is refused; a declared conversion is reproducible.
10. **Certification requirement.** CR-10.
11. **Risk.** R-20 — an executor that evaluates string terms is an expression-evaluation surface. It must not become a code-execution path (cf. CH-5). Terms must be interpreted by a total, pure, non-eval evaluator.
12. **Classification.** **READY FOR TRANSFORMATION**

### T-12.2 — Currency is hardcoded to a three-letter code, contradicting frames already declared

1. **Current finite state.** `_CURRENCY_PATTERN = ^[A-Z]{3}$`; `Money(currency: str, minor_units: int)`. Cannot express `currency.i1-energy-quantum`, `currency.v9-token`, `currency.o2-allocation-credit`, `currency.d3-mesh-unit` — **all four already declared in `reference-frames.json`**. No currency registry, no currency conversion model. **Absent from the closed-enumeration disclosure register** while every comparable closure is disclosed.
2. **Evidence.** `platform/commercial_intelligence/contracts.py:53,154-176`; `UCOS-OMEGA-INFINITY-UNIVERSAL-EVOLUTIONARY-ENTITY-FABRIC-DETERMINATION.md:339-343`.
3. **Why it is finite.** ISO-4217 shape baked into the type. This is the sharpest single case in the repository of an example (USD-shaped currency) being treated as architecture.
4. **Universal target state.** Currency is a registered axis; value is a magnitude in a registered unit of a registered value system.
5. **Required architectural transformation.** Replace the pattern with a registered-currency reference; conversions declared as relationships.
6. **Existing reusable capability.** `reference-frames.json` **already declares four non-human currencies** — the data exists and the code cannot read it. `SEED_CONVERSIONS` supplies the relationship pattern. `Money` already applies the correct discipline internally (refuses cross-currency arithmetic, mirroring the temporal no-common-frame rule) and that discipline must be preserved.
7. **Required extension.** Currency registry + conversion relationships + `Money` re-typing.
8. **Dependency.** T-12.1 (conversion executor); T-26.1 (disclosure of the closure, since it is currently undisclosed).
9. **Validation requirement.** VR-20 — a non-human currency from an existing declared frame becomes expressible; cross-currency arithmetic remains refused.
10. **Certification requirement.** CR-10.
11. **Risk.** R-21 — `Money` is used in the only real value engine. Re-typing it touches priced commitments. Also: the closure must be **disclosed before it is fixed**, or the disclosure register remains incomplete for the intervening period.
12. **Classification.** **READY FOR TRANSFORMATION**

**Domain verdict: 2 READY FOR TRANSFORMATION.**

---

## 13. Relationship Transformation

**Target:** Universal relationship capability

### T-13.1 — Relationship model is sound; one ordering defect

1. **Current finite state.** One canonical owner (`engine/uckp/graph.py`, invariant `CAA-INV-05` PASS, violations 0), real SCC and transitive-closure algorithms, temporal validity adopted. But a cyclic relationship is **registered, then refused** — the edge stays registered after refusal.
2. **Evidence.** `DEPENDENCY-CLOSURE-DETERMINATION.md:14-17`; `engine/graph/architecture/dependency_intelligence.py:1-43`; `engine/ceu/existence.py:989-1006`.
3. **Why it is finite.** Not finite — **incorrectly ordered**. Refusal after registration leaves state the refusal claims does not exist.
4. **Universal target state.** Refusal precedes registration; a refused relationship leaves no trace.
5. **Required architectural transformation.** Reorder validation before mutation at one site.
6. **Existing reusable capability.** The acyclicity check already exists and already fires; only its position is wrong.
7. **Required extension.** One reordering.
8. **Dependency.** None. Independent.
9. **Validation requirement.** VR-21 — after a refused cyclic registration, the registry contains no edge.
10. **Certification requirement.** CR-11.
11. **Risk.** R-22 — low, but this is the same pattern as CH-5 (`validate()` calls `realize()` first). Both are validate-after-mutate defects; fixing one should establish the pattern for the other.
12. **Classification.** **READY FOR TRANSFORMATION**

### T-13.2 — Relationship types are open in UCKP and closed by construction in context

1. **Current finite state.** `uckp.relation-type` and `uckp.relationship-class` are registered vocabularies (open). `ContextRelation` is 11 members, closed by construction — `ContextOntology.__init__` refuses a relation without a rule, so no relation can be added.
2. **Evidence.** `engine/uckp/vocabulary.py:40-48`; `engine/context/taxonomy.py:240-275`; `engine/context/ontology.py:372-374`.
3. **Why it is finite.** Two vocabularies with opposite openness postures for the same concept. A future relationship semantics is representable in the knowledge graph and not in the context graph.
4. **Universal target state.** One posture: relations registered **with** their rules, so rule-totality is preserved while membership opens.
5. **Required architectural transformation.** Co-registration of member and rule. The invariant to preserve is *"no relation without a rule"*, not *"no new relation"*.
6. **Existing reusable capability.** `RELATION_RULES` already pairs them; S-13 supplies the registry.
7. **Required extension.** Vocabulary conversion with co-registration.
8. **Dependency.** T-9.2 — identical pattern, should be transformed together.
9. **Validation requirement.** VR-13, VR-22 — rule totality holds after every registration; no unbounded edge becomes possible.
10. **Certification requirement.** CR-07.
11. **Risk.** R-23 — the construction-time refusal is currently what guarantees bounded edges. Moving it to registration time must not create a window in which an unruled relation exists.
12. **Classification.** **READY FOR TRANSFORMATION**

### T-13.3 — Relationship traversal is deliberately partial; substrate coverage is one tenth

1. **Current finite state.** `PATH_BEARING_KINDS = ("depends_on","produces")`; class-token hub edges deliberately not traversed. 66.2% of tracked files carry no import edge; 421 of 4,057 non-code files (10.4%) reachable by any declared substrate.
2. **Evidence.** `engine/verification_intelligence/selection.py:51,24-27`; `UCOS-UVI-000001-…-DETERMINATION.md` §1.3-§1.4.
3. **Why it is finite.** A reasoned compromise: *"a selector that always escalates is not a selector, it is a slower way of running everything."* The consequence is that relationship-derived intelligence covers a tenth of the tree.
4. **Universal target state.** Substrate coverage sufficient that fail-wide is the exception, not the rule.
5. **Required architectural transformation.** Additional declared substrates for non-code files, and read-set declarations for the 7 of 15 stages lacking them.
6. **Existing reusable capability.** The five-substrate projection; `StageSpec.read_set` already exists and was added additively.
7. **Required extension.** Substrate declarations.
8. **Dependency.** None blocking. Improves T-21.1 (impact analysis reach).
9. **Validation requirement.** VR-23 — coverage measured before and after; fail-wide remains the default for uncovered subjects.
10. **Certification requirement.** CR-11.
11. **Risk.** R-24 — narrowing selection is only safe if coverage genuinely improves. A coverage claim that is wrong converts fail-wide into fail-silent. This is the single most dangerous class of change in the programme and must never precede T-19.1.
12. **Classification.** **READY FOR TRANSFORMATION** (strictly after detection is established)

**Domain verdict: 3 READY FOR TRANSFORMATION.**

---

## 14. Knowledge Transformation

**Target:** Universal knowledge evolution

### T-14.1 — Canonical declaration is 25.5% while homing is 100%

1. **Current finite state.** 549/549 homed with 0 gaps by the session hook; canonical declaration measured at **140/549 = 25.5% FULLY ASSIMILATED**, baseline WITHHELD; a counter-determination records NOT ARCHITECTURALLY COMPLETE.
2. **Evidence.** `UAKOS-CLOSURE-002` hook output; `UCOS-OMEGA-INFINITY-UNIVERSAL-KNOWLEDGE-ASSIMILATION-COMPLETENESS-DETERMINATION.md:20-40`; `00-MASTER/UAKOS-CLOSURE-006/15-FINAL-CONSTITUTIONAL-DETERMINATION.md`.
3. **Why it is finite.** "Homed" and "canonical" are different properties and the gap is three-quarters wide. Homing is a location claim; declaration is a truth claim.
4. **Universal target state.** Homing and declaration converged; baseline released.
5. **Required architectural transformation.** Declaration population. Data, not code.
6. **Existing reusable capability.** The UKDA canonical store; `knowledge/canonical-knowledge.json` (byte-identically regenerable).
7. **Required extension.** Declaration of the remaining 409 concepts.
8. **Dependency.** Requires T-22.1/T-22.3 — a concept cannot be canonically declared without a resolvable owner, and 391 of 542 have none. **This is the tightest coupling in the determination: knowledge declaration is gated on ownership ratification.**
9. **Validation requirement.** VR-24.
10. **Certification requirement.** CR-12.
11. **Risk.** R-25 — declaring knowledge canonical without a ratified owner creates canonical truth nobody can amend, which is worse than undeclared knowledge.
12. **Classification.** **BLOCKED** (on T-22.3)

### T-14.2 — The headline closure verdict depends on an out-of-repository corpus and an environment variable

1. **Current finite state.** `CLOSED | concepts=549 | gaps=0` is produced with `scan_mode: "repo-only (declared)"`, corpus scan disabled. `CORPUS = REPO.parent / "UCOS"` is out-of-tree; `CLOSURE_SKIP_CORPUS` gates it. Counter-measurement: 437/0 → **528/91** without the env var.
2. **Evidence.** `00-MASTER/UAKOS-CLOSURE-002/closure_engine.py:74,176`; `UNIVERSAL-ASSIMILATION-FEEDBACK-LOOP-DETERMINATION.md` §2. The hook ran in exactly this configuration at this session's start.
3. **Why it is finite.** A gitignored, untracked, out-of-tree input decides a tracked verdict. The most-cited number in the corpus is not reproducible from the repository alone.
4. **Universal target state.** Closure verdict derived solely from Repository Truth, or the external dependency declared as a constitutional boundary with its effect on the number stated.
5. **Required architectural transformation.** Either remove the external input or declare it. Both are small; the second is a declaration.
6. **Existing reusable capability.** `RTBD-001`'s definition of Repository Truth (tracked, non-ignored, human-authored) is the test to apply.
7. **Required extension.** Declaration or removal.
8. **Dependency.** None blocking, but this **must precede** any use of the 549/0 number as evidence for anything.
9. **Validation requirement.** VR-25 — the verdict is reproducible from a bare fresh clone with no environment variables set.
10. **Certification requirement.** CR-12.
11. **Risk.** R-26 — resolving it will change the headline number from `gaps=0` to a non-zero value (evidence suggests 91). Every artifact citing `gaps=0` becomes stale. This is a **truth-restoring** change with wide documentary consequence.
12. **Classification.** **READY FOR TRANSFORMATION**

### T-14.3 — The assimilation↔intelligence edge does not exist; the feedback loop is prose

1. **Current finite state.** Two complete, mutually unreachable planes. `platform/universal_assimilation/` imports `engine/` exactly once, for an exception type. Assimilation *"terminates in a measurement of itself"*. The Feedback flow is prose — *"no engine implements it. DOCUMENTED-ONLY."*
2. **Evidence.** `…ASSIMILATION-INFINITE-INTELLIGENCE-INTEGRATION-DETERMINATION.md` §0.2, §1.5; `cli.py:33`.
3. **Why it is finite.** Unknown knowledge can be admitted and cannot become understood. This is the defining gap of knowledge evolution.
4. **Universal target state.** Admitted knowledge reaches the reasoning population and the reasoning population reaches admission.
5. **Required architectural transformation.** A binding layer. **COMPOSE.** The fabric determination states it exactly: *"the obstacle is not a missing engine. It is a missing binding layer between fourteen engines that already exist."*
6. **Existing reusable capability.** All fourteen admission surfaces; `engine/uckp/intelligence.py` (13 reasoners); `engine/uckp/evolution.py` (15-stage cycle with `KNOWLEDGE_ASSIMILATION` as stage 14 — **the cycle already names the missing edge**).
7. **Required extension.** Binding layer only.
8. **Dependency.** Requires T-6.1 (identity on the path), T-9.x (context on the path), T-21.x (security on the path), T-13.x (impact reachable). **This is the convergence point of five domains** and cannot precede them.
9. **Validation requirement.** VR-26 — an admitted source reaches a reasoner and produces a recorded consequence.
10. **Certification requirement.** CR-12.
11. **Risk.** R-27 — binding two planes that currently cannot reach each other means unvalidated, unidentified, unowned, unsecured input reaches reasoning. **The binding layer must be built last among its dependencies, not first.** Building it early is the highest-severity sequencing error available in this programme.
12. **Classification.** **REQUIRES FOUNDATION CHANGE** (dependent on five domains)

### T-14.4 — `KnowledgeStore` is filesystem-bound; storage neutrality declined

1. **Current finite state.** Four heterogeneous streams with different write disciplines; the frozen-corpus guard *"does not fail — it silently succeeds"* under substitution; REQ-14/REQ-34 implemented as filesystem ordering and sibling-file semantics; no other consumer of `PersistenceAdapter` exists.
2. **Evidence.** `REQ-43-STORAGE-NEUTRALITY-DETERMINATION-REPORT.md` §3.1-§3.4; `adr/0028-…-decline.md`; warning at `:349` against claiming technology independence.
3. **Why it is finite.** Deliberately. The decline is reasoned and correct on all four criteria.
4. **Universal target state.** Either a richer contract that can carry heterogeneous streams and transaction ordering, or a **disclosed permanent boundary**.
5. **Required architectural transformation.** A declaration of the boundary is sufficient and is the lower-risk path.
6. **Existing reusable capability.** S-05 (10 backends, 52 tests) — proves the pattern works where the contract fits.
7. **Required extension.** Boundary declaration; or a stream-aware contract if an authority decides neutrality is required.
8. **Dependency.** None.
9. **Validation requirement.** VR-27 — the frozen-corpus guard must fail, not silently succeed, under any substitution.
10. **Certification requirement.** CR-12.
11. **Risk.** R-28 — the silent-success guard is the dangerous part and is independent of the neutrality question. It should be fixed regardless of the neutrality decision.
12. **Classification.** **REQUIRES AUTHORITY DECISION**

**Domain verdict: 1 READY · 1 REQUIRES AUTHORITY DECISION · 1 REQUIRES FOUNDATION CHANGE · 1 BLOCKED.** Knowledge is the most dependency-entangled domain in the determination.

---

## 15. Data Transformation

**Target:** Universal data capability

### T-15.1 — The artifact schema is closed in four independent ways (ZF-1…ZF-4)

1. **Current finite state.** `additionalProperties: false`; `universal_id` 10⁶ ceiling; `volume` 1000 ceiling; `status` 17 closed values; `traceability` exactly 13 fixed stages with `additionalProperties: false`. Mirrored in `engine/registry/models.py` (`LifecycleStatus` 17 with raising `coerce`, `TRACE_STAGES` 13-tuple). Only `category` and `program` are open.
2. **Evidence.** `00-BOOK/SCHEMAS/artifact.schema.json:20,44` and status/traceability blocks; `engine/registry/models.py:25-44,57+`; `UNAF-001:134-147` names ZF-1…ZF-5 and states *"ZF-1..ZF-5 are the ONLY items requiring code change"* — **all remain unfixed**.
3. **Why it is finite.** A new artifact form needing a new lifecycle state, a new traceability stage, an extra field, volume #1000, or ID #1000000 cannot be admitted without a schema **and** code change in lockstep. 19 sibling schemas are the historical evidence that a new form has always been a hand-written file.
4. **Universal target state.** Artifact form admissible by registration; status and traceability stages registered vocabularies; no cardinality ceiling.
5. **Required architectural transformation.** Convert status and traceability to registered vocabularies; widen identifier and volume patterns; replace `additionalProperties: false` with a declared-extension mechanism.
6. **Existing reusable capability.** S-13 for the vocabularies. `category`'s open pattern is the in-schema precedent.
7. **Required extension.** Schema + mirrored constants, coherently.
8. **Dependency.** T-6.3 (same identifier pattern). Requires T-15.3 (lifecycle model reconciliation) — converting `status` to a vocabulary is meaningless while six incompatible lifecycle models coexist.
9. **Validation requirement.** VR-28 — all 1,461 existing records remain valid; a probe artifact form is admitted without code change.
10. **Certification requirement.** CR-13.
11. **Risk.** R-29 — `additionalProperties: false` currently prevents silent schema drift. Replacing it with an extension mechanism must not permit unvalidated fields, or the schema stops being a contract.
12. **Classification.** **READY FOR TRANSFORMATION** (after T-15.3)

### T-15.2 — `DiscoveryKind` is a closed 8-member enum (ZF-5)

1. **Current finite state.** Eight universal discovery dimensions, `coerce()` raising.
2. **Evidence.** `engine/discovery/contracts.py:42-71`.
3. **Why it is finite.** A ninth discovery dimension is a code edit. The docstring's own framing — *"never from hard-coded patterns, regex, or a filesystem walk"* — is about *how* dimensions are discovered, not about whether the dimension set is open.
4. **Universal target state.** Discovery dimensions registered.
5. **Required architectural transformation.** Vocabulary conversion.
6. **Existing reusable capability.** S-13.
7. **Required extension.** Conversion.
8. **Dependency.** T-6.1.
9. **Validation requirement.** VR-29.
10. **Certification requirement.** CR-13.
11. **Risk.** R-30 — low.
12. **Classification.** **READY FOR TRANSFORMATION**

### T-15.3 — Six mutually incompatible lifecycle models; determination artifacts have no lifecycle

1. **Current finite state.** UCL 49-stage, UCDA 9-stage, ACEE Goal→Obligation→Invariant, Evolution 15-stage, Requirement 6-state, and *"Determination artifacts: NO LIFECYCLE DEFINED"*. Plus `LifecycleStatus` 17, `Lifecycle` 10, `ContextLifecycle` 8.
2. **Evidence.** `UNIVERSAL-ARTIFACT-LIFECYCLE-DETERMINATION.md:19,43-52`; §3.1 proposes a taxonomy explicitly labelled **"Proposed"**; authority `NONE — DERIVED ANALYSIS`.
3. **Why it is finite.** An unknown artifact form cannot be told which lifecycle governs it. **This determination artifact is itself in that void.**
4. **Universal target state.** One lifecycle authority, or declared federation with machine-readable crosswalks.
5. **Required architectural transformation.** An authority decision, then either consolidation or crosswalks.
6. **Existing reusable capability.** `require_transition` in `engine/knowledge/model.py` shows the enforced-transition pattern; `_LIFECYCLE_TRANSITIONS` shows the graph-as-data pattern.
7. **Required extension.** Consolidation or crosswalk registry.
8. **Dependency.** Blocks T-15.1 (status vocabulary), T-24.2 (evolution stages), T-9.2 (context lifecycle). **Four transformations wait on this one decision.**
9. **Validation requirement.** VR-30.
10. **Certification requirement.** CR-13.
11. **Risk.** R-31 — consolidating six models will invalidate stage assignments across the corpus. Federation is lower-risk and preserves existing assignments.
12. **Classification.** **REQUIRES AUTHORITY DECISION**

### T-15.4 — Serialization and storage are already open; adapters are document-shaped

1. **Current finite state.** Serialization registry openness enforced **bidirectionally** — the gate fails if nothing is left to admit. Ten interchangeable persistence backends, interchangeability measured by digest equality, 52 passing tests. But all six assimilation adapters convert *bytes of a document*; there is no adapter for a UI screen, an API surface, an infrastructure resource, or a technology. Adding a *reader* still edits the `READERS` dict.
2. **Evidence.** `00-MASTER/ACEE-000001/acee-declaration.json:169-231`; `acee_engine.py:246-266,3372-3400`; `engine/uckp/persistence.py:101,169-574`; `platform/universal_assimilation/adapters.py:742-753`.
3. **Why it is finite.** Data universality is currently document universality.
4. **Universal target state.** Non-document data forms admissible; reader registration a data act.
5. **Required architectural transformation.** Additional adapters for the non-document categories the fabric determination records as absent (API/protocol, UI/UX, infrastructure); reader registration moved to declaration.
6. **Existing reusable capability.** S-04, S-05, and the adapter contract itself (`units()`).
7. **Required extension.** Adapters. Note: the **declared-but-unregistered** format requirement must be preserved — `check_open_world` fails if nothing is left to admit.
8. **Dependency.** Non-document adapters for API/UI depend on T-17.x and T-18.x having a target at all.
9. **Validation requirement.** VR-31 — at least one non-document form admitted; an unregistered format still exists after transformation.
10. **Certification requirement.** CR-13.
11. **Risk.** R-32 — a reader registered as data implies code loaded as data. This must not reproduce CH-5.
12. **Classification.** **READY FOR TRANSFORMATION** (partially blocked by T-17/T-18 targets)

**Domain verdict: 3 READY · 1 REQUIRES AUTHORITY DECISION.** T-15.3 is a decision gating four transformations.

---

## 16. Language Transformation

**Target:** Universal communication capability

### T-16.1 — One hardcoded language, no resolver

1. **Current finite state.** `LINGUISTIC` is a first-class universal kind whose only value is `"language": "en"`, `"encoding": "UTF-8"`. No resolver. Zero i18n machinery anywhere (`gettext|babel|i18n|Accept-Language` → zero hits).
2. **Evidence.** `engine/context/catalog.py:178-186`; `UCOS-ACC-001-…:437-442` (tracked R-9 at `:473`); `STAGE-0-IMPLEMENTATION-COMPLETION-PLAN.md:106` M-9, acceptance *"≥2 languages resolve; no `en` default in code"*.
3. **Why it is finite.** Declaration without resolution. Note the language *axis* is properly open in the location layer — `reference-frames.json` already declares alien language axes. The defect is the hardcoded default, not the model.
4. **Universal target state.** Language resolved from LOCATION + observer; ≥2 languages resolving; no default in code.
5. **Required architectural transformation.** A resolver, patterned on the existing frame resolution.
6. **Existing reusable capability.** `FrameRegistry.resolve` (no defaults, UNRESOLVED with derivation path); `AXIS_DERIVATION` already includes `language` as a location-derived axis.
7. **Required extension.** Resolver + a second linguistic context. Both small.
8. **Dependency.** T-8.1 (axis derivation as data) makes it cleaner; T-9.4 (second context set) is the same work.
9. **Validation requirement.** VR-32 — two languages resolve; no `en` appears as a default in code.
10. **Certification requirement.** CR-14.
11. **Risk.** R-33 — low. The remediation is already specified with an acceptance criterion.
12. **Classification.** **READY FOR TRANSFORMATION**

### T-16.2 — Machine languages are fixed tuples with infinity as a named placeholder

1. **Current finite state.** `KNOWN_EXECUTION_KINDS` = 10 members including `FUTURE_LANGUAGE` and `FUTURE_COMPUTE`, commented *"Open by registration (Article 17)"* while being a tuple; `FUTURE_LANGUAGE` is bound to a concrete adapter class. `SOURCE_EXTENSIONS` is ~30 extensions and language identity is the **file extension string**.
2. **Evidence.** `engine/uckp/execution.py:37-60,280`; `engine/knowledge/integration/repository.py:51-80,747-764`.
3. **Why it is finite.** Unboundedness is represented by a **named finite slot**. Two future languages are indistinguishable — both are `FUTURE_LANGUAGE`. This is the `KNOWN EXAMPLES → FIXED ENUMERATION` pattern in its purest form, with the placeholder disguising it.
4. **Universal target state.** Execution kinds registered; each future language has its own identity.
5. **Required architectural transformation.** Vocabulary conversion; retire the placeholder members.
6. **Existing reusable capability.** S-13. `SOURCE_EXTENSIONS` is already injectable — the override pattern exists.
7. **Required extension.** Conversion.
8. **Dependency.** T-6.1. Same pattern as T-15.4's `FUTURE_STORAGE` and T-20.2's `ReasoningKind.FUTURE` — **all three placeholder slots should be transformed together as one pattern**.
9. **Validation requirement.** VR-33 — two distinct unforeseen execution kinds are separately registrable and distinguishable.
10. **Certification requirement.** CR-14.
11. **Risk.** R-34 — `FUTURE_LANGUAGE` is bound to a live adapter class. Retiring the member requires re-homing that binding.
12. **Classification.** **READY FOR TRANSFORMATION**

### T-16.3 — No symbolic-system axis

1. **Current finite state.** No dimension distinguishes symbolic or notational systems from measurement. Classified UNKNOWN in the predecessor determination.
2. **Evidence.** Searched; `MEASUREMENT` is the nearest kind. Absent.
3. **Why it is finite.** A future non-linguistic symbolic communication system has no declared home. It is not clear whether this is a gap or a correct subsumption.
4. **Universal target state.** A determination on whether symbolic systems require their own axis.
5. **Required architectural transformation.** Determination first, then either an axis or a documented subsumption.
6. **Existing reusable capability.** T-9.1 (if kinds become registrable, this becomes a registration rather than an amendment).
7. **Required extension.** Unknown until determined.
8. **Dependency.** T-9.1 would make this cheap. Currently it is an amendment.
9. **Validation requirement.** VR-34.
10. **Certification requirement.** CR-14.
11. **Risk.** R-35 — adding an axis speculatively is worse than determining first. The `unknown`-as-valid-member discipline suggests the honest current answer is to record it as unresolved rather than invent an axis.
12. **Classification.** **REQUIRES AUTHORITY DECISION**

**Domain verdict: 2 READY · 1 REQUIRES AUTHORITY DECISION.**

---

## 17. API Protocol Transformation

**Target stated by the directive:** transform *"No protocol assumption"* into *"Universal Protocol Capability"*

### 17.0 — Correction the evidence requires

The directive treats the DISPROVEN protocol verdict as a defect to remediate. The evidence does not support that reading, and proceeding on it would amend the constitution by engineering action.

The absence of protocol representation is **not an oversight**. It is enforced by `USL-15`, implemented as `_TECHNOLOGY_MARKERS` / `_TECH_MARKERS` scanning the canonical identity core, converted into hard validation failure at seven sites, and enforced at construction time in two more. `pyproject.toml:19-22` states the intent: *"stdlib-only by constitutional intent (TP-04 Vendor Neutrality of Core, TP-05 Least Sufficient Technology)."*

So the transformation question is not *how do we open the protocol dimension* but **which of two different things is wanted**:

- **Option A — protocol-neutral core, protocol-representable periphery.** The core continues to select no technology; a declared boundary layer may name protocols. This preserves `USL-15` and closes the representational gap.
- **Option B — protocols representable anywhere.** Requires weakening or repealing `USL-15`. This is a constitutional amendment.

This determination does not choose. It records that **Option A is achievable by extension and Option B is an amendment**, and that the current state is neither — because the API registry exists, requires a `protocol` attribute, and has never held a record.

### T-17.1 — No protocol is representable anywhere

1. **Current finite state.** `_TECHNOLOGY_MARKERS` (17 tokens incl. URL schemes) and the stricter `_TECH_MARKERS` (20 tokens incl. **bare** `http`, `grpc`, `mqtt`, `amqp`, `rest`, `websocket`) scan the identity core; a match becomes `_failed` at `model_validation.py:364-366`, `band11_validation.py:279-282,308-312`, `band11_freeze_validation.py:330-332,359-363`, `capability_validation.py:301-304`, `composition_validation.py:353-356`, `contract_validation.py:93`; construction raises at `application/interaction.py:221-224` and `application/state.py:213-221`. `Interface.endpoint_ref` is *"abstract only — no URL/protocol/port"*; `InterfaceKind` is an interaction *style*.
2. **Evidence.** `service/service.py:63-83,219-222`; `service/model.py:101-122,362-364,502-504`; the seven enforcement sites above.
3. **Why it is finite.** **Closed by taboo, not open by data.** The model can say *"request-response"*; it structurally cannot say *"over HTTP/2"*.
4. **Universal target state.** Under Option A: a declared periphery where protocols are registered members, with the core prohibition intact. Under Option B: protocols representable throughout.
5. **Required architectural transformation.** Option A: a protocol registry plus a declared boundary that the marker scan does not apply to. Option B: repeal or narrow `USL-15`.
6. **Existing reusable capability.** `ApiRegistry` already exists with `required_attributes = {"contract","protocol"}` — the slot is built. S-13 supplies the registry semantics. The frame/axis pattern supplies the boundary pattern.
7. **Required extension.** Option A: registry population + boundary declaration. Option B: constitutional amendment.
8. **Dependency.** Requires an authority decision between A and B before any work. Blocks T-15.4 (API adapters) and T-18.2.
9. **Validation requirement.** VR-35 — under Option A, the core still fails on a protocol token while the periphery admits one.
10. **Certification requirement.** CR-15 — this touches a constitutional gate and cannot be an engineering act.
11. **Risk.** R-36 — the marker check is a **naive lowercased substring scan**: `"lambda"` false-positives on identifiers, `"rest"` on `restore`/`restriction`/`forest`. Any change to this mechanism must fix the matching semantics, or narrowing the taboo will silently narrow it in unintended places.
12. **Classification.** **REQUIRES AUTHORITY DECISION**

### T-17.2 — The API registry has never held a record

1. **Current finite state.** `ApiRegistry` wired at `registries.py:299`, exported, requiring `contract` and `protocol`. Zero `ucos.api` records; zero `UCOS-API-######`; no `.apis.register` call. `protocol` is untyped `Any`, validated for **presence only**. No `ProtocolKind`, `TransportKind`, adapter, transport abstraction or dispatcher exists.
2. **Evidence.** M-D measurements; `engine/registry/universal/registries.py:172-177,60-66`.
3. **Why it is finite.** The one place the word "protocol" is a required field has never been satisfied. Protocol representation is nominally available and factually nonexistent.
4. **Universal target state.** Populated, or withdrawn with a stated reason.
5. **Required architectural transformation.** Population (Option A) or withdrawal.
6. **Existing reusable capability.** The registry itself; `TypedRegistry` attribute validation.
7. **Required extension.** Records, and a typed `protocol` attribute.
8. **Dependency.** T-17.1 decision.
9. **Validation requirement.** VR-36.
10. **Certification requirement.** CR-15.
11. **Risk.** R-37 — populating it while `USL-15` stands creates records the validators would reject if they were scanned, i.e. an inconsistency between registry and validation planes.
12. **Classification.** **BLOCKED** (on T-17.1)

### T-17.3 — Connector schema closed and already drifted from code

1. **Current finite state.** `sources` enum of 11; `mode` and `status` enums closed; `additionalProperties: false`; **no `protocol` field at all**. Runtime `SOURCES` was extended twice (`GIT`, `EXECUTION`) and **neither appears in the schema**. `make_signal` raises `unknown source` fail-closed. Zero connector instances. Six connectors are fixture replay; only `git_repository.py` touches a real source, via local `subprocess`.
2. **Evidence.** `00-BOOK/SCHEMAS/connector.schema.json`; `00-BOOK/tools/connectors/base.py:27-40` — whose comment claims *"Sources are pluggable… append-only addition to the open source set"* while being a closed Python set.
3. **Why it is finite.** A concrete, already-realised case where a closed enumeration became a limitation and the response was **silent drift rather than amendment**. This is the exemplar failure mode for the whole programme.
4. **Universal target state.** One authority for the source vocabulary; schema and code cannot diverge.
5. **Required architectural transformation.** Single source of truth for the vocabulary, generated into or validated against the schema.
6. **Existing reusable capability.** S-13; the `is_extensible` probe would have caught this.
7. **Required extension.** Vocabulary + schema generation or cross-validation.
8. **Dependency.** Independent of T-17.1 — this is a consistency defect, not a protocol-representation question.
9. **Validation requirement.** VR-37 — schema and runtime vocabulary provably agree.
10. **Certification requirement.** CR-15.
11. **Risk.** R-38 — low risk, high diagnostic value. Fixing this establishes the drift-prevention pattern needed for T-15.1 and T-6.3, both of which mirror constants across schema and code.
12. **Classification.** **READY FOR TRANSFORMATION**

**Domain verdict: 1 READY · 1 REQUIRES AUTHORITY DECISION · 1 BLOCKED.** Protocol is the domain where the directive's framing most needs correction: the gap is real, but its removal is an amendment, not a fix.

---

## 18. UI UX Transformation

**Target:** Universal Experience Capability

### 18.0 — Correction the evidence requires

As with protocol: the absence of a UI is not obviously a defect. There is no frontend, no interaction runtime, and `application/interaction.py` *"selects no technology, UI framework, design system, or rendering technology."* Whether UCOS Ω∞ **should** have an experience capability is an authority question about scope. What can be determined without that answer is that the current UI *representation* is internally inconsistent — schemas exist, are weaker than their neighbours, and have zero instances.

### T-18.1 — UI representation exists with zero instances and no runtime

1. **Current finite state.** `ui-artifact.schema.json` is 21 lines with **no enums**, nullable `wireframe`/`design`, `components: array[string]` with no component model, and `derived_status` as an unconstrained string — **strictly weaker** than the neighbouring `page.schema.json` which carries a real 17-value enum. `journey.schema.json` likewise has no enums. Zero `UCOS-UI-######` / `UCOS-UX-######` instances. No tool references the schemas. `12-APPLICATION/` is 22 `.md`, zero source. Zero frontend files; one generated `.html`. `intelligence/portal.py` is a Markdown generator despite its name.
2. **Evidence.** M-D, M-F; the schema files; `intelligence/portal.py:65-81,1028,1070`.
3. **Why it is finite.** Representation with no instances and no runtime. **Nothing in this dimension can evolve because nothing exists to evolve.**
4. **Universal target state.** Either a populated interaction model, or an explicit declaration that experience is out of scope with the schemas withdrawn.
5. **Required architectural transformation.** A scope decision, then population or withdrawal.
6. **Existing reusable capability.** The schema and registration infrastructure; `page.schema.json` as the quality bar.
7. **Required extension.** Depends entirely on the scope decision.
8. **Dependency.** Requires the same class of decision as T-17.1.
9. **Validation requirement.** VR-38.
10. **Certification requirement.** CR-16.
11. **Risk.** R-39 — building an experience capability speculatively adds a dimension with no consumer. Withdrawing the schemas removes a declared-but-empty surface, which is honest but forecloses a direction.
12. **Classification.** **REQUIRES AUTHORITY DECISION**

### T-18.2 — `InteractionKind` is a closed 4-member vocabulary

1. **Current finite state.** `InteractionKind` ∈ {Input, Command, Query, Response} is the entire interaction vocabulary; `Interaction` is a frozen typed record with a lifecycle state, not an event loop or widget tree; data presented *by reference*.
2. **Evidence.** `application/interaction.py:1-45`.
3. **Why it is finite.** A future interaction model outside input/command/query/response — neural, spatial, agentic, non-human observer — is unrepresentable.
4. **Universal target state.** Interaction kinds registered.
5. **Required architectural transformation.** Vocabulary conversion.
6. **Existing reusable capability.** S-13; the `Observer` concept already exists in the context layer and is the natural anchor for a non-human interaction model.
7. **Required extension.** Conversion.
8. **Dependency.** T-18.1 scope decision. Cheap if the decision is to retain the dimension.
9. **Validation requirement.** VR-39.
10. **Certification requirement.** CR-16.
11. **Risk.** R-40 — low. The refusal to select a rendering technology is correct and must be preserved; only the *kind* set opens.
12. **Classification.** **READY FOR TRANSFORMATION** (pending T-18.1)

**Domain verdict: 1 READY (conditional) · 1 REQUIRES AUTHORITY DECISION.**

---

## 19. Software Transformation

**Target:** Autonomous validated software evolution

### T-19.1 — No gate varies initialization order; the determinism harness cannot detect statefulness

1. **Current finite state.** `double_build` runs both builds **in one interpreter**, sharing `hermetic_env()`, one resolved document, one `RegistryAdapter`, one signer — only the output directory differs. The two cross-process gates diff two invocations of the **same** entry point with the **same** arguments, so both reach the same bootstrap state and a runtime-dependent verdict is equally wrong in both. **Zero of 29 gates vary initialization order.**
2. **Evidence.** `engine/determinism/reproduce.py:275-330`; `.github/workflows/uaue-gate.yml:189-197`; `uisd-gate.yml:231-241`.
3. **Why it is finite.** Not finite — **blind**. This is why 24 architectural defects coexist with green verification.
4. **Universal target state.** TI-2 measurable: the same subject yields the same verdict in a fresh interpreter and a bootstrapped one, and a gate fails if not.
5. **Required architectural transformation.** An initialization-independence measurement. Small, and it is the **highest-priority transformation in the entire programme** because nothing else can be verified without it.
6. **Existing reusable capability.** `engine/determinism/reproduce.py` exists; it needs cross-process invocation, not a new engine. M-B demonstrates the measurement in three lines.
7. **Required extension.** Cross-process comparison; a gate that fails on divergence.
8. **Dependency.** **None. This is the root of the dependency graph.** It must precede T-6.1, because otherwise the durability fix cannot be shown to work.
9. **Validation requirement.** VR-01, VR-02.
10. **Certification requirement.** CR-01.
11. **Risk.** R-41 — introducing this measurement will turn currently-green gates red, exposing the 43-of-72 kinds already known to be affected. That is the intended effect and must be expected rather than treated as regression.
12. **Classification.** **READY FOR TRANSFORMATION**

### T-19.2 — The mutation classifier returns ERROR for every subject

1. **Current finite state.** Register declares 9 rules including R-09 `GOVERNED_ANALYSIS`; only 8 predicates exist; `classify()` returns `status='ERROR'` while coverage problems are non-empty. `UNRESOLVED` **fails closed** and is documented as never a permissive default. The test suite asserting coverage is failing. Root cause: `mutation_class_extension.py:117-125` wrote the rule into the register without adding a predicate.
2. **Evidence.** M-C (reproduced); `platform/repository_intelligence/mutation_classification.py`; `platform/tests/test_mutation_classification.py`, whose preamble names precisely this failure mode — *"a rule nobody evaluates is prose, and prose is what let `uisd-declaration.json` be authored, owned, engine-consumed and unclassified while six of its mutations were certified."*
3. **Why it is finite.** **Not finite — non-functional.** Any new kind of artifact is unclassifiable, and unclassified fails closed. This gates every dimension simultaneously, including the implementation of every transformation in this determination.
4. **Universal target state.** Coverage total; every subject classifiable; mutation authority determinate.
5. **Required architectural transformation.** One predicate. Eight siblings exist to pattern from.
6. **Existing reusable capability.** `RULE_PREDICATES` R-01…R-08.
7. **Required extension.** One function.
8. **Dependency.** **None.** But **everything depends on it**: no transformation can be governed while classification returns ERROR. It is co-root of the dependency graph with T-19.1.
9. **Validation requirement.** VR-40 — `validate_rule_coverage` returns empty; `classify()` returns a class for every subject sampled across all nine classes.
10. **Certification requirement.** CR-17.
11. **Risk.** R-42 — restoring classification will begin classifying subjects that have been unclassified, potentially revealing mutations that were certified while unclassified (the exact incident the module documents). Expect disclosure, not silence.
12. **Classification.** **READY FOR TRANSFORMATION**

### T-19.3 — Mutation class extension is a specification, not an implementation

1. **Current finite state.** `add_dynamic_class_extension_mechanism()` returns a dict describing a `HYPOTHETICAL_CLASS`; docstring — *"This is a SPECIFICATION, not an implementation… status: SPECIFIED (implementation deferred to Phase 3-4)"*; the extension registry `00-BOOK/DATA/mutation-class-extensions.json` **does not exist**.
2. **Evidence.** `mutation_class_extension.py:138-152`.
3. **Why it is finite.** Adding a mutation class requires a human source edit to `RULE_PREDICATES`. A genuinely new kind of artifact cannot be classified without human intervention.
4. **Universal target state.** Mutation classes registered with co-registered predicates, on the same co-registration discipline as T-13.2.
5. **Required architectural transformation.** Implement the specified mechanism.
6. **Existing reusable capability.** The specification itself names the two required pieces (registry + loader/merge); S-13 supplies the registry.
7. **Required extension.** Registry + merge, with predicate co-registration.
8. **Dependency.** T-19.2 must be fixed first — extending a broken classifier extends the breakage.
9. **Validation requirement.** VR-41 — a probe class with a predicate is admitted; a class without a predicate is **refused at registration**, not silently accepted (the R-09 failure mode).
10. **Certification requirement.** CR-17.
11. **Risk.** R-43 — the current defect exists precisely because a class was registered without a predicate. The extension mechanism must make that impossible by construction, or it institutionalises the defect.
12. **Classification.** **READY FOR TRANSFORMATION** (after T-19.2)

### T-19.4 — Source self-modification is prevented by three confinements

1. **Current finite state.** `_resolve` rejects absolute paths and `..` traversal and confines writes to `<repo>/realization`; the only textual reference to self-modification in the codebase is a **negation**; `SOURCE` mutation authority is `pre-commit → verify.sh → UCOS-RIB-001 → UCOS-AEE-001 → Phase 8 → Phase 9` — human/CI with no autonomous agent. Generated output is gitignored with zero tracked files. Generated APIs have **no POST/PUT/PATCH/DELETE** because *"URI has no authority to author knowledge."*
2. **Evidence.** `intelligence/realization/implementation.py:63-78,100-109`; `.gitignore:128-137`; `intelligence/realization/generators/base.py:1-16,44-48`; `00-MASTER/UCL-000001/ucl_engine.py:2341`.
3. **Why it is finite.** **Deliberately.** This is a safety property, not a gap. Software cannot evolve autonomously, by design.
4. **Universal target state.** Under the directive's framing: autonomous validated software evolution. Under the evidence: an authority decision on whether autonomy is wanted at all.
5. **Required architectural transformation.** If autonomy is chosen: a governed mutation path with trust, validation, impact and certification **before** write — i.e. the full §21 chain applied to source. If not: retain and document.
6. **Existing reusable capability.** The generation contract (no filesystem/network/clock, no self-sealing, no non-derivable facts) is already the right shape for a governed generator. `engine/constitution/gateway.py` is the existing single authorised mutation path.
7. **Required extension.** Only under an autonomy decision.
8. **Dependency.** Depends on **all five target invariants** (TI-1…TI-5). An autonomous system operating on undurable, unowned, undetectable, untrusted state is the worst available configuration.
9. **Validation requirement.** VR-42.
10. **Certification requirement.** CR-17.
11. **Risk.** R-44 — **the highest-severity risk in this determination.** Granting self-modification before durability, ownership, detection and trust hold would produce ungoverned, unrecorded, unattributable change. The recorded precedent (140 identifiers minted as a side effect of a drift check) is the small version of this failure.
12. **Classification.** **REQUIRES AUTHORITY DECISION**

### T-19.5 — Impact analysis exists and is unwired

1. **Current finite state.** `engine/graph/architecture/impact.py` implemented; importers are only its own package (`__init__.py:68`, `engine.py:41`) and its test.
2. **Evidence.** As stated; predecessor X-30.
3. **Why it is finite.** The Impact stage of the assimilation chain has code that nothing calls.
4. **Universal target state.** Impact reachable from every admission path.
5. **Required architectural transformation.** Wiring. COMPOSE.
6. **Existing reusable capability.** The module itself, plus `blast_radius.py`, `reachability.py`, `critical_path.py`.
7. **Required extension.** Call sites.
8. **Dependency.** T-13.3 (substrate coverage) determines how much of the tree impact can actually reach.
9. **Validation requirement.** VR-43.
10. **Certification requirement.** CR-11.
11. **Risk.** R-45 — wiring impact analysis whose substrate covers 10.4% of non-code files produces confident-looking impact reports with wide blind spots. Coverage must be disclosed alongside every impact verdict.
12. **Classification.** **READY FOR TRANSFORMATION**

**Domain verdict: 4 READY · 1 REQUIRES AUTHORITY DECISION.** T-19.1 and T-19.2 are jointly the root of the entire dependency graph.

---

## 20. Intelligence Transformation

**Target:** Universal Intelligence Capability

### 20.0 — Correction the evidence requires

The absence of statistical intelligence is a **documented refusal with a stated reason**, not a gap: *"A predictive engine would produce an impact estimate that could not be falsified: it would be believed, and belief is what this programme exists to replace."* Any transformation that introduces model inference must answer that argument rather than ignore it. This determination retains the refusal in the target architecture (§4.3) and treats its removal as an authority decision.

### T-20.1 — Intelligence is re-derivation; the AI adapter layer is a declared HIGH-severity gap

1. **Current finite state.** No ML libraries at all across 1,709 production files — not even numpy. "Intelligence" means deterministic rule evaluation and graph traversal. `intelligence/UCOS-RIE-MODEL.json` → `aeos_readiness.known_spine_gaps` records **`G-09` "AI adapter layer (multi-executor)" — HIGH — NOT IMPLEMENTED**, alongside `G-01`, `G-02`, `G-03`. `15-UNIVERSAL-SCIENCE-INTELLIGENCE/` is **36 `.md`, 0 code** — holding exactly the registries that would carry algorithms, models, insights, reasoning traces, learned changes and self-evolution.
2. **Evidence.** As stated; `…ASSIMILATION-INFINITE-INTELLIGENCE-INTEGRATION-DETERMINATION.md` §0.4, §0.6 — *"The constitutional objective is documented at full length and carries no mechanism."*
3. **Why it is finite.** Intelligence expansion is achieved by **refusing to conclude**, not by learning. That is a safety property, not a growth property. The system's own instrument reports the integration point unimplemented.
4. **Universal target state.** Either the registries are implemented under the existing falsifiability discipline, or the refusal is declared permanent and the registries withdrawn.
5. **Required architectural transformation.** A decision, then implementation or withdrawal.
6. **Existing reusable capability.** The falsifiability discipline itself; `engine/verification_intelligence/cost_model.py` as the one honest feedback loop (measurement-fed, verdict-neutral by declaration).
7. **Required extension.** Depends on the decision.
8. **Dependency.** T-14.3 (the assimilation↔intelligence edge) must exist for intelligence to have inputs. Depends on TI-1…TI-5.
9. **Validation requirement.** VR-44 — any introduced intelligence must produce falsifiable output; a non-falsifiable estimate must be refused.
10. **Certification requirement.** CR-18.
11. **Risk.** R-46 — introducing a model whose output cannot be re-derived reintroduces exactly the belief-over-evidence failure the architecture was built to eliminate.
12. **Classification.** **REQUIRES AUTHORITY DECISION**

### T-20.2 — The reasoner set is a closed 13-member enum with hardcoded dispatch

1. **Current finite state.** `ReasoningKind` 13 members including `FUTURE`; `reasoners()` returns a **hardcoded dict literal**; `reason()` indexes it. No `register_reasoner`, no `ReasonerProtocol`, no entry-point discovery — zero matches repo-wide.
2. **Evidence.** `engine/uckp/intelligence.py:39-53,1035-1050,1052-1054`.
3. **Why it is finite.** A future intelligence form **cannot register as a reasoner**. Each reasoner is written to stay correct as the corpus grows (an excellent internal discipline), but the *set* cannot grow without a source change. `FUTURE` is the same named-placeholder pattern as `FUTURE_LANGUAGE` and `FUTURE_STORAGE`.
4. **Universal target state.** A reasoner protocol with registration, preserving the anti-hardcoded-threshold discipline.
5. **Required architectural transformation.** Protocol + registry.
6. **Existing reusable capability.** S-13; the `Provider` protocol pattern (`@runtime_checkable`) shows the shape; the existing 13 reasoners define the interface empirically.
7. **Required extension.** Protocol + registry; retire `FUTURE`.
8. **Dependency.** T-16.2 and T-15.4 share the placeholder pattern — transform together.
9. **Validation requirement.** VR-45 — a registered reasoner never seen by the release contributes, and a reasoner with a corpus-tuned threshold is refused.
10. **Certification requirement.** CR-18.
11. **Risk.** R-47 — an open reasoner registry is a code-loading surface. It must not reproduce CH-5. Reasoners must be registered, not imported from data.
12. **Classification.** **READY FOR TRANSFORMATION**

### T-20.3 — A future intelligence may supply data but never a conclusion

1. **Current finite state.** Provider `kind` is genuinely open — *"validates its form and never its membership, which is precisely why a provider class that does not exist yet needs no framework change (PC-02 / PC-14)"*. But the protocol is fixed at six operations: `describe / capabilities / health / query / fetch / verify`. **No `reason()`, no `infer()`, no `propose()`, no `evolve()`.**
2. **Evidence.** `platform/universal_provider/contracts.py:109-118,124-131,717-747`.
3. **Why it is finite.** Unknown intelligence can contribute **data**, never a **conclusion**.
4. **Universal target state.** A determination on whether conclusions may enter through a provider, and under what evidence obligation.
5. **Required architectural transformation.** Either a `propose()` operation whose output is treated as a claim requiring validation, or a documented refusal.
6. **Existing reusable capability.** `ProviderAttestation` already exists — the notion of a provider making a verifiable claim is already modelled.
7. **Required extension.** Protocol extension, only under decision.
8. **Dependency.** **Requires T-21.1 first.** Admitting conclusions through the provider path while that path executes arbitrary code from unvalidated JSON would be the worst possible ordering.
9. **Validation requirement.** VR-46.
10. **Certification requirement.** CR-18.
11. **Risk.** R-48 — a provider conclusion that bypasses validation becomes belief. The falsifiability discipline must extend to provider output.
12. **Classification.** **REQUIRES AUTHORITY DECISION**

**Domain verdict: 1 READY · 2 REQUIRES AUTHORITY DECISION.**


---

## 21. Security Transformation

**Target:** Input → Trust → Validation → Impact → Execution
**Current:** Input → Execution risk

### T-21.1 — Unrestricted import from unvalidated JSON, invoked before validation

1. **Current finite state.** `CatalogSource.discover()` globs `*.json` and `json.loads` it; `ProviderDescriptor.from_dict` accepts `entry_point` with **no validation whatsoever** — no allowlist, no namespace prefix, no signature, no hash pin; `resolve_entry_point` splits on `:` then `importlib.import_module(module_name)` — **module-level code executes here, before any callable check** — then invokes the attacker-named callable with the descriptor and caller config. `realize()` calls this with **no certification gate** although `authorizes_activation()` exists; `validate()` calls `realize()` **first**, then runs the constitutional gates. The docstring asserts *"no code executes during discovery, which is what keeps discovery safe over untrusted catalogs"* — true of `discover()` only.
2. **Evidence.** `platform/universal_provider/discovery.py:171-201,203-225,372-435` (import at `:404`, invoke at `:424`, claim at `:48-50`); `contracts.py:445`; `framework.py:205-216,224-240`; `certification.py:98,349`.
3. **Why it is finite.** The chain is `Input → Execution`. There is no trust step, no validation step, and no impact step before execution. **Validation cannot protect against a malicious descriptor because the payload has already run.**
4. **Universal target state.** TI-5: `Input → Trust → Validation → Impact → Execution`, with no code path importing or invoking from an unverified descriptor.
5. **Required architectural transformation.** Three ordered changes: (a) verify the descriptor before import; (b) gate realization behind certification; (c) reorder `validate()` to validate before realizing. **All three are REUSE — the machinery exists.**
6. **Existing reusable capability.** `platform/foundation/trust.py` (signing, verification, key hierarchy, delegation, revocation, notary); provider `certification.py:98,349 authorizes_activation()`. Both sit **two modules away and unwired**.
7. **Required extension.** Wiring plus a signature or allowlist requirement on `entry_point`.
8. **Dependency.** **None. Independent root.** Must precede T-14.3 (assimilation binding), T-20.3 (provider conclusions), T-15.4 (data-registered readers) and any transformation that widens what may be admitted as data.
9. **Validation requirement.** VR-47 — an unsigned or non-allowlisted descriptor is refused **before** import; a malicious descriptor cannot reach `getattr`.
10. **Certification requirement.** CR-19.
11. **Risk.** R-49 — **the openness/trust tension.** This is the *only* mechanism that admits a genuinely unforeseen kind without a code change (PC-14). Hardening it narrows the one open path, so the hardening must preserve legitimate open admission while requiring verification. Doing this wrong closes the architecture's most open surface.
12. **Classification.** **READY FOR TRANSFORMATION**

### T-21.2 — No threat model as data; the entire security vocabulary is closed enums

1. **Current finite state.** `14-SECURITY/` is 5 markdown files, no code, no data. `FindingKind` (7) with *"no new kind is invented"*; `ClassificationKind` (6) with *"No new kind is introduced"*; `SecurityZone` (5) and `SecurityControl` (7) plus **four parallel hand-maintained dicts** requiring lockstep edits; `BLOCKING_SEVERITIES`, `OPEN_FINDING_STATES`, `EXPOSURE_KINDS` hardcoded; `Permission` a closed 4-verb enum whose closure is **test-enforced**. Repo-wide `*threat*` file search → **zero**. `RegistryKind.THREAT` maps to a generic append-only registry keyed by free-text `record_type` — instances only, no taxonomy.
2. **Evidence.** `platform/security/contracts.py:244-259,50-66,613-670,296-303,373-400`; `intelligence.py:64-68`; `platform/foundation/identity.py:41-47`; `platform/tests/test_blueprints_governance.py:60`; `00-BOOK/SCHEMAS/finding.schema.json`.
3. **Why it is finite.** New threat *instances* are admissible; new threat *classes* are not. **Security cannot evolve against an unknown threat class without a code change** — a hard ceiling on the dimension the directive most needs open.
4. **Universal target state.** Threat classes, severities, zones and controls are registered vocabularies with a declared threat/attack-surface/trust-boundary model as data.
5. **Required architectural transformation.** Vocabulary conversion for six enums plus a threat model expressed as data.
6. **Existing reusable capability.** S-13; the append-only registry already used for instances; `finding.schema.json` as the shape to generalise.
7. **Required extension.** Conversion + threat model data. The four parallel dicts must become co-registered attributes, or the lockstep-edit defect persists in registered form.
8. **Dependency.** T-21.1 first — a threat vocabulary is of little use while the largest known hole is unfixed.
9. **Validation requirement.** VR-48 — a probe threat class is admitted and honoured by the roll-up; `BLOCKING_SEVERITIES` remains total over the widened severity set.
10. **Certification requirement.** CR-19.
11. **Risk.** R-50 — roll-up semantics are currently guaranteed by closed sets. Opening severities without a declared ordering makes blocking non-deterministic — the same total-order hazard as T-9.2.
12. **Classification.** **READY FOR TRANSFORMATION**

### T-21.3 — Adversarial-input handling is one narrow scanner with an adjacent bypass

1. **Current finite state.** `_SECRET_PATTERNS` is 7 regexes; `record_finding()` scans three fields and rejects on hit, recording a location-only `SECRET-LEAK` CRITICAL instead. But `record()` accepts a pre-built finding with **no secret scan**, despite a docstring claiming fail-closed. Elsewhere ingestion validation is type/shape only: no size limit, no depth limit, no rate limit, no canonicalization of untrusted refs, no path-traversal check on locators, no signature requirement on ingested data files. Trust root is **HMAC-SHA256 only** — symmetric, so verification requires the same secret.
2. **Evidence.** `platform/security/intelligence.py:74-92,574-620,621-627,629-648`; `platform/foundation/trust.py:46,61-68,12-17`.
3. **Why it is finite.** The one real defence targets **accidental leakage, not an adversary**. Unknown malicious input has no modelled defence.
4. **Universal target state.** Uniform adversarial-input discipline on every admission path, with asymmetric verification where a verifier must not hold the signing secret.
5. **Required architectural transformation.** Close the `record()` bypass; add bounds and canonicalization to admission paths; determine whether asymmetric signing is required.
6. **Existing reusable capability.** `scan_for_secret()`; `SecretRef` (keys by reference, never embedded); the fail-closed typed-error discipline already used throughout.
7. **Required extension.** Bypass closure + bounds; asymmetric algorithm only under decision.
8. **Dependency.** T-21.1.
9. **Validation requirement.** VR-49 — `record()` and `record_finding()` behave identically on secret content; oversized and deeply-nested inputs are refused.
10. **Certification requirement.** CR-19.
11. **Risk.** R-51 — the docstring/implementation mismatch means any current reliance on `record()` being safe is unfounded. Fixing it may reject content currently accepted.
12. **Classification.** **READY FOR TRANSFORMATION**

**Domain verdict: 3 READY FOR TRANSFORMATION.** Security is fully transformable by extension and wiring; **no new capability is required**, which makes CH-5 the most disproportionate risk in the repository — a critical hole with the fix already built two modules away.

---

## 22. Governance Transformation

**Target:** Universal ownership and authority resolution

### T-22.1 — Evidence kinds, standings, reasons and grains are closed fail-closed enums

1. **Current finite state.** `EvidenceKind` closed 6-member with `coerce` **raising** on unknown; `CONSTITUTIVE_EVIDENCE_KINDS` vs `CORROBORATIVE_EVIDENCE_KINDS` hardcoded — **which evidence may establish ownership is not configurable**. `OwnershipStanding` (3) with a *"complete, closed reason vocabulary"* of 5. `OwnershipGranularity` (2). Authority tiers exist **only** in `00-CMG/CMG-REGISTRY.json` and prose — repo-wide search for `class AuthorityTier|AUTHORITY_TIERS` → **zero results**, so tiers are neither a code enum nor enforced by a code contract.
2. **Evidence.** `platform/universal_ownership/contracts.py:42-84,74-84,87-114,116-147`.
3. **Why it is finite.** A future governance model with a novel evidence basis cannot be represented. Note `OwnershipGranularity`'s docstring is the strongest openness *argument* in the repository (*"both grains are defensible so neither is hardcoded. The grain is declared"*) while remaining a 2-member closed enum — argument and implementation diverge.
4. **Universal target state.** Evidence kinds registered with their constitutive/corroborative role declared per kind; authority tiers bound to a contract.
5. **Required architectural transformation.** Vocabulary conversion plus role co-registration; tier contract.
6. **Existing reusable capability.** S-13; the constitutive/corroborative split is already expressed and only needs to move from constant to attribute.
7. **Required extension.** Conversion + tier binding.
8. **Dependency.** T-9.2 shares the pattern (authority vocabularies). Should be transformed together.
9. **Validation requirement.** VR-50 — a probe evidence kind participates; a kind registered without a declared role is **refused**.
10. **Certification requirement.** CR-20.
11. **Risk.** R-52 — if evidence kinds become registrable, a data edit could declare a weak evidence kind constitutive, fabricating ownership. Constitutive status must require constitutional authority, mirroring the universality hazard in T-9.1.
12. **Classification.** **READY FOR TRANSFORMATION**

### T-22.2 — Authority is partitioned across three mutually disclaiming planes with no shared key

1. **Current finite state.** *"The repository has no single canonical-authority artifact. Authority is partitioned across three planes, each of which explicitly disclaims the others."* The ownership-declaration plane is recorded `Machine-readable? NO` — *"every ownership row was authored by a human and is unreadable by machine."* D-2.1: *"the Canonical Ownership Principle is declared in one place and enforced in another, and the two do not share a key. This is the root of every conflict in §5."* UCAF binds **1 decider of 14 capabilities**.
2. **Evidence.** `CANONICAL-AUTHORITY-DETERMINATION.md:17-32,34`; TA-N8.
3. **Why it is finite.** A future governance structure cannot be told which plane admits it. This is the same missing-shared-key defect as T-6.2 (identity) and T-8.2 (truth models) — **one root, three surfaces**.
4. **Universal target state.** One authority key, or declared federation with machine-readable crosswalks.
5. **Required architectural transformation.** A declaration plus a machine-readable key. The declaration is an authority act; the key is small engineering.
6. **Existing reusable capability.** `deterministic_id` already supplies a machine-readable key format; the CMG lattice supplies the tier data.
7. **Required extension.** Crosswalk registry keyed machine-readably.
8. **Dependency.** **Co-root with T-6.2 and T-8.2.** Blocks T-22.3.
9. **Validation requirement.** VR-51 — every ownership row resolves to a machine-readable key; declaration and enforcement planes join on it.
10. **Certification requirement.** CR-20.
11. **Risk.** R-53 — making human-authored ownership rows machine-readable will expose rows that do not resolve, converting silent assumption into visible failure. That is the intended effect.
12. **Classification.** **REQUIRES AUTHORITY DECISION**

### T-22.3 — 391 of 542 concepts unowned; assignment catalogue empty; 0% ratified

1. **Current finite state.** Ownership **27.86% closed** — 151 owned, 391 not; *"the exit criterion 'every constitutional object has ownership' is NOT MET"*; *"27.86% closed / 100% determined / 100% diagnosed / **0% ratified**"*. The governed assignment catalogue is literally `"assignments": {}`, conceding *"an empty catalogue is an honest statement that no assignment has been governed yet, never a licence to guess"* — so the constitutive `DECLARED_ASSIGNMENT` provider contributes **nothing** and all declared ownership comes from locator inference. `UNASSIGNED_OWNER = "UNASSIGNED"` — *"Never a real owner."* The Nucleus model is recorded `UNOWNED (genuine gap)`. The **20 ownership dimensions** are *"not legislated over constitutional concepts anywhere in Repository Truth"*, and `OWN-REQ-002` legislates **at most one** owner per subject, so multi-dimensional ownership is constitutionally **excluded**.
2. **Evidence.** `UCOD-001:19,190,315,332,391,397,401`; `platform/universal_ownership/catalog/ucos-ownership-declarations.json`; `02-CANONICAL-OWNERSHIP-MATRIX.md:44,48-51,103`.
3. **Why it is finite.** *"The ownership machinery is production-ready and constitutionally sound. The ownership data is 27.86% populated."* **The gap is ratification, not engineering.**
4. **Universal target state.** TI-4: every subject resolves to exactly one ratified owner, or admission fails closed.
5. **Required architectural transformation.** **None architecturally.** Population and ratification of the catalogue.
6. **Existing reusable capability.** S-11 in full — fail-closed, anti-fabricating, grain-declared.
7. **Required extension.** Governed assignments, ratified.
8. **Dependency.** Requires T-22.2 (shared key) to be resolvable. **Blocks T-14.1 (knowledge declaration) and gates the entire evolution question**, because an unowned subject cannot be admitted, changed, or certified by any located authority.
9. **Validation requirement.** VR-52 — ownership closure measured; unowned subjects fail closed on admission rather than defaulting to `UNASSIGNED`.
10. **Certification requirement.** CR-20.
11. **Risk.** R-54 — ratifying 391 assignments is an act of judgment at scale. `UCOD-001:401` states the correct posture: it *"will not fabricate them to close it."* Any automated population would be exactly the fabrication the machinery refuses.
12. **Classification.** **BLOCKED** — requires an owner act; no engineering path exists

### T-22.4 — The capability admission authority is unregistered and externally blocked

1. **Current finite state.** UKAP and UREE are *"proposed and unregistered"*; the requirement register is `Owner: UNCLEAR / Authority: UNCLEAR`, UNOWNED *"with no authority competent to modify it"*; UKAP registration is **blocked on CEP-002 Article 28**, *"an act no derived-truth cycle may perform, with **no competent ratifying authority located within the repository**"*; every closure criterion needing an Article 28 act *"is an owner decision awaiting an external act"*. Contradicted by a reassessment claiming *"ALREADY OPERATIONAL… Phase 3 blocked status was a misdiagnosis"* (F-20). `UCOS-URR-001` stands `PROPOSED — NOT ADMITTED`.
2. **Evidence.** `…COMPLETE-ASSIMILATION-COVERAGE-DETERMINATION.md:273,316,329,478,512`; `PHASE-3-EXECUTION-READINESS-DETERMINATION.md:15,47-53`; `…KNOWLEDGE-ASSIMILATION-COMPLETENESS…:859-864`.
3. **Why it is finite.** Even where capability data is open (S-06 is machine-checked), **the governance act admitting a capability has no located owner**, and the two determinations describing it disagree on whether it is blocked.
4. **Universal target state.** A registered admission authority, or an explicitly declared external-act dependency with the contradiction resolved.
5. **Required architectural transformation.** Resolve F-20 first (which determination governs), then register or declare.
6. **Existing reusable capability.** S-06 (the capability register is ready to receive); the programme registration pattern used by 29 other programmes.
7. **Required extension.** Registration, contingent on an external act.
8. **Dependency.** Terminates **outside the repository**. Blocks nothing technically, but bounds what may legitimately be admitted.
9. **Validation requirement.** VR-53.
10. **Certification requirement.** CR-20.
11. **Risk.** R-55 — proceeding under the reassessment's *"already operational"* reading while the blocking determination stands unretracted would admit capabilities under contested authority.
12. **Classification.** **BLOCKED** — external act required

**Domain verdict: 1 READY · 1 REQUIRES AUTHORITY DECISION · 2 BLOCKED.** Governance is the domain where the transformation path **exits the repository**, and it is the binding constraint on the programme's completion.

---

## 23. Certification Transformation

**Target:** How unknown future capabilities receive evidence, validation and certification

### T-23.1 — Certification mechanics are sound and must be preserved

1. **Current finite state.** Subject is *"a pure projection"*; rules *"aggregate the upstream verdicts rather than re-judging any artifact"*; `digests()` anchors evidence **by reference**; `Certificate` frozen, content-addressed, `verify_integrity()` makes mutation detectable; findings sorted by `rule_id` for determinism; fail-closed; rules and frames **injectable**.
2. **Evidence.** `engine/universal_certification/contracts.py:451-502,503-510,597-700`; `engine.py:112-118,117,128-175`; `rules.py:1-70`.
3. **Why it is finite.** It is not. Certification *logic* is already open.
4. **Universal target state.** Preserved.
5. **Required architectural transformation.** **None. Preserve.**
6. **Existing reusable capability.** S-10.
7. **Required extension.** None.
8. **Dependency.** None.
9. **Validation requirement.** VR-54 — regression protection.
10. **Certification requirement.** CR-21.
11. **Risk.** R-56 — the risk is degrading it while opening the subject type (T-23.2). Content-addressing and deterministic ordering must survive.
12. **Classification.** **READY FOR TRANSFORMATION** (as preservation)

### T-23.2 — Subject type fixed by `isinstance`; attestation class is a one-member enum

1. **Current finite state.** `CertificationClass` has **exactly one** member, `UNIVERSAL_READINESS` — *"It records readiness only."* No registry, no data catalog of classes. `UniversalCertificationSubject.create` hard-enumerates composition by `isinstance` — requires a `ValidationInput`, a `MeasurementInput`, a `RepositoryTruthInput` and a `CertificationClass`. The subject is not a protocol, not generic, not `Any`. Five compliance frames are concrete built-ins, each typed against the same fixed subject.
2. **Evidence.** `engine/universal_certification/contracts.py:86-90,478-489,199,275,344,493-496`; `compliance.py:41-170`.
3. **Why it is finite.** **A novel system type cannot be certified as its own kind of thing** — only if it can be flattened into a blueprint-keyed validation+measurement+repository-truth triple. This directly answers the directive's question: an unknown future capability receives certification **only by projection into a known shape**.
4. **Universal target state.** Certification generic over subject type; certification classes registered.
5. **Required architectural transformation.** Replace the `isinstance` triple with a declared subject protocol; convert `CertificationClass` to a registered vocabulary.
6. **Existing reusable capability.** Rules and frames are **already injectable** — the extensibility pattern exists and only the subject is closed. S-13 for the class vocabulary.
7. **Required extension.** Subject protocol + class vocabulary.
8. **Dependency.** T-8.3 (reality-mode-aware certification) depends on this. T-11.2 depends on what a certification may assert.
9. **Validation requirement.** VR-55 — a novel subject type is certifiable without flattening; existing certificates remain verifiable and their digests unchanged.
10. **Certification requirement.** CR-21.
11. **Risk.** R-57 — the `isinstance` checks currently guarantee that a certificate's inputs are the three things its rules expect. A protocol-typed subject must preserve that guarantee, or rules will evaluate against inputs they cannot interpret and produce confident wrong verdicts.
12. **Classification.** **READY FOR TRANSFORMATION**

### T-23.3 — Machine certificates confer no finality; ~15 root certifications are self-asserted prose

1. **Current finite state.** `UCERT_AUTHORITY = "ENGINEERING-EXECUTION-ONLY"`; certificates *"confer no constitutional finality (DE-05)"*. So **no machine-issued certificate in the system certifies anything constitutional**. Meanwhile `03-CONSTITUTIONAL-UNBOUNDEDNESS-CERTIFICATION.md` marks all 16 unboundedness axes UNBOUNDED on **prose citation alone** — no axis cites executable code, a test, a digest, or a reproducible instrument — and its Axis 13 (Unlimited Governance Models) and Axis 14 (no schema ceiling) are **directly contradicted** by M-A and M-G. ~15 further self-issued certifications sit at repo root without evidence binding of the kind `Certificate` requires.
2. **Evidence.** `engine/universal_certification/contracts.py:54,606-608`; `03-CONSTITUTIONAL-UNBOUNDEDNESS-CERTIFICATION.md:5,14-33`; contrast `UCOD-001:401` — *"this determination will not fabricate them to close it."*
3. **Why it is finite.** The weakest evidence class in the repository is the one certifying the property this programme exists to achieve. **The existing unboundedness certification cannot be used as evidence for or against any transformation here.**
4. **Universal target state.** Every unboundedness axis bound to an executable instrument.
5. **Required architectural transformation.** Convert each of the 16 axes into a probe, on the pattern already proven twice in-repo.
6. **Existing reusable capability.** `VocabularyRegistry.is_extensible()` (probe term, invariant failure on refusal) and `check_open_world` (fails on bound tokens, closed registries, claimed terminal states) are **exactly** the required instrument shape. `UCPA-L-07` shows the idiom applied to a primitive set.
7. **Required extension.** 16 probes, plus withdrawal or re-issuance of prose certifications.
8. **Dependency.** Requires T-19.1 (detection) to be meaningful. **Should precede any claim that a transformation succeeded** — otherwise success is asserted in the same prose form now shown to be unreliable.
9. **Validation requirement.** VR-56 — each axis has a probe that fails when the axis is closed. Axes 13 and 14 must **currently fail**, proving the instrument works.
10. **Certification requirement.** CR-21 — replacing a certification is a certification act.
11. **Risk.** R-58 — instrumenting the axes will demonstrate that several are currently closed, invalidating a standing certification. That is the point, and it must be expected rather than treated as a defect introduced by the transformation.
12. **Classification.** **READY FOR TRANSFORMATION**

### T-23.4 — Certification chains unverified on load; one registry non-monotonic; a re-mint disguised as replay

1. **Current finite state.** Assurance certification registry `__init__` performs **no chain verification**; `require_intact()` only on write. `platform/foundation/durable_identity.py:539-563` `from_dict` **re-mints instead of replaying**, and `verify()` returns `True` unconditionally for adopted records — the exact failure `ExistenceRegistry.from_document` refuses. One registry non-monotonic (TA-17); a relationship registered before refusal (TA-18).
2. **Evidence.** `platform/universal_assurance/registry.py:178-182`; `platform/foundation/durable_identity.py:539-563,186-194`; TA-16/17/18.
3. **Why it is finite.** Load-time trust asymmetry: a certification of an unknown future system could be trusted without its chain being checked.
4. **Universal target state.** Verify on load; re-mint is never presented as replay; `verify()` never returns unconditional truth.
5. **Required architectural transformation.** Apply the `from_document` discipline (*"Re-deriving would let the rebuilt registry differ from the recorded one and still look healthy"*) to these three sites.
6. **Existing reusable capability.** `engine/ceu/existence.py:773` is the reference implementation, in-repo.
7. **Required extension.** Load-time verification at three sites.
8. **Dependency.** Related to T-6.1 — same discipline, different objects. Same validate-before-mutate pattern as T-13.1 and T-21.1.
9. **Validation requirement.** VR-57 — a tampered chain fails on load; `verify()` returns `False` for a record whose chain does not verify.
10. **Certification requirement.** CR-21.
11. **Risk.** R-59 — an unconditional `True` in a `verify()` means any current reliance on it is unfounded. Fixing it may invalidate adopted records.
12. **Classification.** **READY FOR TRANSFORMATION**

**Domain verdict: 4 READY FOR TRANSFORMATION.** T-23.3 is a prerequisite for credibly asserting that any later transformation succeeded.

---

## 24. Evolution Transformation

**Target:** Safe continuous evolution across software, architecture, knowledge, intelligence, governance

### T-24.1 — Non-termination is achieved and must be preserved

1. **Current finite state.** `next_stage` wraps modulo cycle length; `is_terminal` **always returns `False`**; `EvolutionLedger.is_terminated` always `False` — *"there is no state it could return `True` from"*; `append` *"admits only the stage the cycle says comes next"*. `check_open_world` fails if *"a terminal state is claimed"*. CMG-000001 LXXVI.5: *"Expansion SHALL be unbounded in count… any apparent limit SHALL be read as a defect."*
2. **Evidence.** `engine/uckp/evolution.py:81-85,88-91,303,248`; `acee_engine.py:3372-3403`.
3. **Why it is finite.** It is not. This is the strongest structural guarantee in the repository — but note it guarantees the cycle **cannot stop**, not that it **can grow**.
4. **Universal target state.** Preserved.
5. **Required architectural transformation.** **None. Preserve.**
6. **Existing reusable capability.** S-08.
7. **Required extension.** None.
8. **Dependency.** None.
9. **Validation requirement.** VR-58 — regression protection; no terminal state becomes claimable.
10. **Certification requirement.** CR-22.
11. **Risk.** R-60 — opening the stage set (T-24.2) must not introduce a stage from which the cycle cannot continue.
12. **Classification.** **READY FOR TRANSFORMATION** (as preservation)

### T-24.2 — The stage set is a closed 15-member enum; the module states a sixteenth is a code edit

1. **Current finite state.** 15 members; `coerce` raising. The docstring states the limitation itself: *"`EvolutionStage` is a closed enumeration, so on its own it would fix the cycle at the fifteen stages that happened to be known when it was written, and a sixteenth would be a code edit. INV-14 requires that every vocabulary admit an unknown future member, so the stage set is also published as a vocabulary."* But `evolution_stage_vocabulary()` is *"a projection of the cycle and not a second list of stages"* — **openness is measured, not achieved**.
2. **Evidence.** `engine/uckp/evolution.py:44-62,64-72,19-31,114`.
3. **Why it is finite.** A future evolution path requiring a stage nobody has conceived is an amendment. **The module is self-aware of violating INV-14 and documents the violation rather than resolving it** — the most honest finite constraint in the repository.
4. **Universal target state.** Stages registered, with the cycle's ordering and wrap preserved.
5. **Required architectural transformation.** Convert the stage set to the single registered home; make the cycle a projection **of the vocabulary** rather than the vocabulary a projection of the cycle.
6. **Existing reusable capability.** S-13; the existing projection function shows the ordering contract that must be preserved.
7. **Required extension.** Inversion of the projection direction.
8. **Dependency.** T-15.3 (lifecycle reconciliation) — six lifecycle models must not become seven. Part of CH-6.
9. **Validation requirement.** VR-59 — a probe stage is admitted, ordered, and the cycle still wraps with no terminal state; `append` still admits only the next stage.
10. **Certification requirement.** CR-22.
11. **Risk.** R-61 — the cycle's ordering is what makes `append` fail-closed. A registered stage without a declared position breaks the ordering and therefore the append discipline.
12. **Classification.** **READY FOR TRANSFORMATION**

### T-24.3 — Evolution is externally triggered recording with no self-modification and no learning

1. **Current finite state.** The controller *"conducts; it does not decide… It knows nothing about its subject… It performs no mutation."* Candidates are **not self-generated** — *"a candidate this engine invented would have no source to name."* Observation *"asserts nothing about repository state."* "Learning" is a **record**, not a model update. Triggering is external: *"A gate invoked only by hand discharges nothing."*
2. **Evidence.** `engine/uaue/controller.py:1-38`; `discovery.py:1-18`; `observation.py:1-17`; `history.py:260`; `engine/constitution/stages.py:465`; `gate.py:38-41`.
3. **Why it is finite.** **UCOS evolves safely and does not evolve itself.** Safety achieved; autonomy absent. Whether autonomy is wanted is not an engineering question.
4. **Universal target state.** Under the directive: safe continuous evolution. Under the evidence: a decision on autonomy, gated on all five target invariants.
5. **Required architectural transformation.** If autonomy is chosen: candidate self-generation, decision authority, and a governed mutation path — each a change of kind.
6. **Existing reusable capability.** The full UAUE machinery; `engine/constitution/gateway.py` as the single authorised mutation path; the 15-stage cycle already naming `OBSERVE`, `LEARN`, `REASON`.
7. **Required extension.** Only under decision.
8. **Dependency.** **TI-1 through TI-5 must all hold.** Same dependency as T-19.4.
9. **Validation requirement.** VR-60.
10. **Certification requirement.** CR-22.
11. **Risk.** R-44 (shared with T-19.4) — **the highest-severity risk in the determination.** An autonomous system operating on undurable, unowned, undetectable, untrusted state is the worst available configuration. The recorded precedent — 140 identifiers minted as a side effect of a drift check — is the small version.
12. **Classification.** **REQUIRES AUTHORITY DECISION**

### T-24.4 — Five scale-local closure clauses contradict the expansion mandate

1. **Current finite state.** *"no ninth root"*, *"no eleventh root"*, eleven runtime concepts — in `PLATFORM-003`, `DATA-003`, `SERVICE-003`, `APPLICATION-003`, `RUNTIME-003`, flagged as **an unexplained asymmetry**.
2. **Evidence.** `UCOS-MOD-001` E-15 against E-08 (CMG-000001 LXXVI.5).
3. **Why it is finite.** Five documents assert bounds that the constitution says must be read as defects.
4. **Universal target state.** Each clause classified as true invariant, representation choice, or defect.
5. **Required architectural transformation.** Classification, then removal or justification.
6. **Existing reusable capability.** The four-way classification used in §25.
7. **Required extension.** Five determinations.
8. **Dependency.** None.
9. **Validation requirement.** VR-61 — no bound token survives unclassified; `check_open_world` already fails on *"architectural bound token present"* and should therefore already be failing on these if they were in its scope.
10. **Certification requirement.** CR-22.
11. **Risk.** R-62 — low engineering risk; the finding is that an existing anti-closure gate does not cover documents it should.
12. **Classification.** **READY FOR TRANSFORMATION**

### T-24.5 — Evolution Registry and Rollback Point were refused, correctly

1. **Current finite state.** Both **REFUSED** with reasons: a registry *"cannot become a second identity authority"* (breaching `CAA-INV-04`); rollback because *"a mutation that fails any gateway stage never reaches truth, so the prior state is not restored but never left."*
2. **Evidence.** `UNIVERSAL-EVOLUTION-MODEL-DETERMINATION.md` §1-§2; `GOVERNED-EVOLUTION-STATE-DETERMINATION.md` §2.
3. **Why it is finite.** Deliberately, and the reasoning is sound.
4. **Universal target state.** Refusals preserved (§4.3).
5. **Required architectural transformation.** **None. Preserve.**
6. **Existing reusable capability.** S-09.
7. **Required extension.** None.
8. **Dependency.** None.
9. **Validation requirement.** VR-58.
10. **Certification requirement.** CR-22.
11. **Risk.** R-63 — a transformation programme under pressure will be tempted to add rollback. It must not. Note the consequence to accept: **there is no rollback for an evolution that reaches truth incorrectly**, which raises the bar on pre-admission validation rather than lowering it.
12. **Classification.** **READY FOR TRANSFORMATION** (as preservation)

**Domain verdict: 4 READY (three as preservation) · 1 REQUIRES AUTHORITY DECISION.**

---

## 25. Finite Constraint Register

Complete inventory, inherited from the predecessor determination §30 and re-classified against transformation targets. Classification: **invariant** (must not be transformed) · **representation** (defensible, could be otherwise) · **implementation limitation** (no architectural justification) · **architectural defect** (contradicts a stated constitutional property).

### 25.1 Enumerations and fixed categories

| # | Constraint | Location | N | Class | Transformation |
|---|---|---|---|---|---|
| C-01 | All closed `Enum` subclasses (M-A) | production trees | **239** | defect in aggregate (230 undisclosed) | T-26.1 |
| C-02 | `Facet` | `engine/uckp/facets.py` | 33 | representation | CH-6 decision |
| C-03 | `ContextKind` | `context/taxonomy.py:64-79` | 16 | representation | T-9.1 |
| C-04 | `ContextAuthority` | `taxonomy.py:107-140` | 5 | implementation limitation | T-9.2 |
| C-05 | `ContextLifecycle` | `taxonomy.py:152-214` | 8 | implementation limitation | T-9.2 |
| C-06 | `ContextRelation` | `taxonomy.py:240-275` | 11 | implementation limitation | T-13.2 |
| C-07 | `ENTITY_TYPES` | `context/ontology.py:37-44` | 6 | implementation limitation | T-7.2 |
| C-08 | `VALUE_TYPES` | `ontology.py:47` | 5 | implementation limitation | T-9.3 |
| C-09 | `REALITY_CONTEXT_AXES` | `location.py:84-90` | 5 | representation | T-8.1 |
| C-10 | `AXIS_DERIVATION` | `location.py:90-116` | ~19 | implementation limitation | T-8.1 |
| C-11 | `LifecycleStatus` (ZF-3) | `registry/models.py:25-44` | 17 | **defect** (named unfixed) | T-15.1 |
| C-12 | `TRACE_STAGES` (ZF-4) | `models.py:57+` | 13 | **defect** (named unfixed) | T-15.1 |
| C-13 | `DiscoveryKind` (ZF-5) | `discovery/contracts.py:42-71` | 8 | **defect** (named unfixed) | T-15.2 |
| C-14 | `Lifecycle` | `knowledge/model.py:108-153` | 10 | implementation limitation | T-15.3 |
| C-15 | `EvolutionStage` | `uckp/evolution.py:44-62` | 15 | **defect** (self-declared INV-14 breach) | T-24.2 |
| C-16 | `ReasoningKind` | `uckp/intelligence.py:39-53` | 13 | **defect** (hardcoded dispatch) | T-20.2 |
| C-17 | `CertificationClass` | `universal_certification/contracts.py:86-90` | **1** | **defect** | T-23.2 |
| C-18 | `FindingKind` (threat classes) | `security/contracts.py:244-259` | 7 | **defect** | T-21.2 |
| C-19 | `Severity`/`FindingState`/`RollupState` | `contracts.py:244-289` | — | implementation limitation | T-21.2 |
| C-20 | `ClassificationKind` | `contracts.py:50-66` | 6 | implementation limitation | T-21.2 |
| C-21 | `SecurityZone`/`SecurityControl` + 4 parallel dicts | `contracts.py:613-670` | 5/7 | implementation limitation | T-21.2 |
| C-22 | `Permission` | `foundation/identity.py:41-47` | 4 | representation (test-enforced) | T-21.2 |
| C-23 | `EvidenceKind` | `universal_ownership/contracts.py:42-84` | 6 | **defect** | T-22.1 |
| C-24 | `OwnershipStanding`/`UNRESOLVED_REASONS` | `contracts.py:87-114` | 3/5 | representation | T-22.1 |
| C-25 | `OwnershipGranularity` | `contracts.py:116-147` | 2 | representation | T-22.1 |
| C-26 | `Selection`/`Coverage`/`Action` | `verification_intelligence/model.py:32-57` | 2/2/3 | representation (fail-safe) | none |
| C-27 | `KeyStatus` | `foundation/trust.py:61-68` | 3 | representation | T-21.3 |
| C-28 | `InteractionKind` | `application/interaction.py` | 4 | implementation limitation | T-18.2 |
| C-29 | `AssimilationState` | `universal_assimilation/contracts.py:340-348` | 5 | representation | none |
| C-30 | `RegistryKind` | `registry/universal/identity.py:49-107` | 30+ext | representation | T-6.1 |
| C-31 | `KNOWN_EXECUTION_KINDS` (incl. `FUTURE_LANGUAGE`) | `uckp/execution.py:37-60` | 10 | implementation limitation | T-16.2 |
| C-32 | `KNOWN_PERSISTENCE_KINDS` (incl. `FUTURE_STORAGE`) | `uckp/persistence.py:59-70` | — | implementation limitation | T-16.2 pattern |
| C-33 | `SOURCE_EXTENSIONS` | `knowledge/integration/repository.py:51-80` | ~30 | representation (injectable) | T-16.2 |
| C-34 | `SOURCES`/`DIMENSIONS` | `00-BOOK/tools/connectors/base.py:27-40` | closed sets | **defect** (drifted) | T-17.3 |
| C-35 | `connector.schema.json` `sources` | `00-BOOK/SCHEMAS/` | 11 | **defect** (out of sync) | T-17.3 |
| C-36 | `_TECHNOLOGY_MARKERS`/`_TECH_MARKERS` | `service/service.py:63-83`, `service/model.py:101-122` | 17/20 | **defect** for protocol dimension | T-17.1 (amendment) |
| C-37 | `FOUNDATION_ARTICLES` UFC-01…17 | `universal_foundation/constitution.py:206-410` | 17 | representation (law as code) | CH-6 decision |
| C-38 | `ConstitutionalDomain` | `constitution.py:68` | 13 | representation | CH-6 decision |
| C-39 | Mutation classes/rules | `mutation-governance-boundary.json` | 9/9 (8 impl) | **defect** (non-functional) | T-19.2, T-19.3 |
| C-40 | Hierarchy grammar (7/7/7) | `UMN-001:22-32,195-206` | 7/7/7 | **invariant** | none |
| C-41 | Root primitives | `01-WORKING/ONTOLOGY-REGISTER.md` | 4 (+1 demoted) | **invariant** | T-7.1 (instantiate, not open) |
| C-42 | `PATH_BEARING_KINDS`/`SELF_PREFIXES` | `selection.py:51-60` | 2/4 | representation | T-13.3 |
| C-43 | Substrate list | `verification_intelligence/registry.py:38-45` | 5 | implementation limitation | T-13.3 |
| C-44 | `Provider` protocol operations | `universal_provider/contracts.py:717-747` | 6 | **defect** for intelligence | T-20.3 |
| C-45 | Compliance frames | `universal_certification/compliance.py:41-170` | 5 | representation (injectable) | T-23.2 |
| C-46 | Serialization readers | `acee_engine.py:246` | 3 of 6 | **invariant** (gate requires an unregistered format) | none |
| C-47 | Five scale-local closure clauses | `*-003` scale docs | 5 | **defect** | T-24.4 |
| C-48 | 29 gate workflows / 46 Makefile targets | `.github/workflows/`, `Makefile` | 29/46 | **defect** (anti-closure mechanism is closed) | T-26.2 |
| C-49 | `EXPOSURE_KINDS`/`BLOCKING_SEVERITIES`/`OPEN_FINDING_STATES` | `platform/security/` | — | implementation limitation | T-21.2 |
| C-50 | `SystemType` (incl. `UNKNOWN`) | `temporal/coordinate.py:29-41` | 5 | **invariant** | none |

### 25.2 Regex, identifier and namespace constraints

| # | Constraint | Location | Class | Transformation |
|---|---|---|---|---|
| P-01 | `^UCOS-[A-Z][A-Z0-9]{1,11}-[0-9]{6}$` (ZF-1) | `artifact.schema.json:20`; `uckp/alignment.py:89` | **defect** | T-6.3, T-15.1 |
| P-02 | `^VOL-[0-9]{3}$` (ZF-2) | `artifact.schema.json:44` | **defect** | T-15.1 |
| P-03 | `^[A-Z]{3}$` currency | `commercial_intelligence/contracts.py:53` | **defect** (undisclosed) | T-12.2 |
| P-04 | `^UCOS-CONN-[0-9]{6}$` | `connector.schema.json` | implementation limitation | T-17.3 |
| P-05 | `^UCOS-UI-[0-9]{6}$`, `^UCOS-FLOW-[0-9]{6}$` | UI/flow schemas | implementation limitation | T-18.1 |
| P-06 | `^UCOS-RUN-.+-[0-9a-f]{16}$` | `validation/checks.py:31`; `universal_validation/rules.py:48` | representation | none |
| P-07 | Identity namespace/local regexes | `uckp/identity.py:49-50` | **invariant** (open by pattern, no allow-list) | none |
| P-08 | Registry namespace/natural-key regexes | `registry/universal/identity.py:43,46` | **invariant** | none |
| P-09 | Extension kind code `[A-Z][A-Z0-9]{1,7}` | `identity.py:189` | representation | T-6.4 |
| P-10 | `^[0-9]+\.[0-9]+\.[0-9]+$` semver | multiple schemas | representation | none |
| P-11 | `additionalProperties: false` on artifact/connector/flow/ui/finding | `00-BOOK/SCHEMAS/` | **defect** for form openness | T-15.1 |
| P-12 | `_SECRET_PATTERNS` (7 regexes) | `security/intelligence.py:74-92` | implementation limitation | T-21.3 |
| P-13 | `DERIVED_CATEGORY_MAXLEN = 6` | `00-BOOK/tools/config.py:488-494` | representation | T-6.3 |

### 25.3 Fixed technology and reality assumptions

| # | Assumption | Location | Class | Transformation |
|---|---|---|---|---|
| T-01 | UTC/ISO-8601 in 5 evidence emitters | five sites | implementation limitation | T-11.3 |
| T-02 | Baseline temporally unaware; certifies refused dates | `baseline_engine.py` | **defect** | T-11.2 |
| T-03 | ISO-4217 currency shape | `commercial_intelligence/contracts.py` | **defect** | T-12.2 |
| T-04 | `language: "en"` hardcoded | `context/catalog.py:178-186` | implementation limitation | T-16.1 |
| T-05 | HMAC-SHA256 only | `foundation/trust.py:46` | implementation limitation | T-21.3 |
| T-06 | Filesystem-bound canonical knowledge; guard silently succeeds | `knowledge/store.py`; REQ-43 §3.2 | representation + **defect** (guard) | T-14.4 |
| T-07 | CPython/venv is the only modelled environment | `execution_environment/model.py` | implementation limitation | §26 note |
| T-08 | Space = repository path space | `context/catalog.py:77-86` | representation | T-10.2 |
| T-09 | No coordinate system/geometry/algebra | absent; `[N]` in UCOS-CVR-001 §04 | implementation limitation | T-10.2 |
| T-10 | No conversion executor / no `Quantity` | absent | implementation limitation | T-12.1 |
| T-11 | Out-of-repo corpus + env var decide headline closure | `closure_engine.py:74,176` | **defect** | T-14.2 |
| T-12 | Document-shaped adapters only | `universal_assimilation/adapters.py` | implementation limitation | T-15.4 |
| T-13 | Unrestricted `importlib` pre-validation | `universal_provider/discovery.py:404,424` | **defect (critical)** | T-21.1 |
| T-14 | Single-process determinism harness | `determinism/reproduce.py:275-330` | **defect** | T-19.1 |
| T-15 | Default execution subject `"engineering"` | `runtime/execution/authorization.py:61` | implementation limitation | §27 note |

### 25.4 Classification totals and transformation partition

| Class | Count | Transformable without redesign |
|---|---|---|
| Invariant — must not be transformed | 7 | n/a (transformation = regression) |
| Representation choice | 22 | Yes, by registration (S-13) |
| Implementation limitation | 25 | Yes, by extension |
| Architectural defect | 24 | 21 yes; 3 require amendment or external act |

**75 of 78 constraints are transformable without architectural redesign.** The three that are not: C-36 (protocol prohibition — amendment), C-02/C-37/C-38 as CH-6 (facet frame — amendment), and T-22.3/T-22.4 (ownership ratification and capability admission authority — external act).

---

## 26. Runtime Authority Register

Twenty violations inherited from the predecessor §31.3, mapped to transformations. Chain in force on the open surfaces is **B** (`CANONICAL KNOWLEDGE → BOOTSTRAP → MUTABLE RUNTIME STATE → TRUTH`); chain **A** holds at the artifact layer only.

| # | Site | Violation | Transformation |
|---|---|---|---|
| RA-01 | `registry/universal/identity.py:156,159` | Mutable globals sole store for 43 of 72 kinds; no persistence writer | T-6.1 |
| RA-02 | `identity.py:162-199` | `register_kind` — the only extension mechanism — writes to memory only | T-6.1 |
| RA-03 | `identity.py:286-309` | Readers make validity a function of process history (M-B) | T-6.1 |
| RA-04 | `ceu/existence.py:898-910` | `_register_identity_kind` mutates global grammar as a side effect | T-6.1 |
| RA-05 | `ceu/catalog.py:396` | `bootstrap()` is the de facto authority-creating act | T-6.1 |
| RA-06 | `nucleus/authority.py:66-76` | `@cache roles_holding` calls `bootstrap()` then hides it | T-6.1 |
| RA-07 | `constitution/gateway.py:203` | Constitutional mutation gateway refuses legitimate mutations in a fresh process | T-6.1 |
| RA-08 | `nucleus/ownership.py:211,215` | NUC-INV-09 verdict depends on bootstrap | T-6.1 |
| RA-09 | `registry/universal/dictionary.py:57` | Raises pre-bootstrap, succeeds post-bootstrap | T-6.1 |
| RA-10 | `dictionary.py:221` | `unparsed()` flips governance PASS/FAIL | T-6.1 |
| RA-11 | `constitution/metadata.py:301-303` | Legality proof inherits the stateful predicate by live call | T-6.1 |
| RA-12 | `uckp/vocabulary.py:542` | `DEFAULT_VOCABULARIES` decides UCKO lawfulness; process-wide mutation; no loader | **T-26.1** |
| RA-13 | `ceu/existence.py:773` + absent document | Loader works; zero committed JSON (M-D) | T-6.1 |
| RA-14 | `determinism/reproduce.py:275-330` | Both builds in one interpreter | T-19.1 |
| RA-15 | `uaue-gate.yml:189-197`, `uisd-gate.yml:231-241` | Same entry point, same args; zero of 29 gates vary init order | T-19.1 |
| RA-16 | `closure_engine.py:74,176` | Out-of-repo corpus + env var decide the most-quoted verdict | T-14.2 |
| RA-17 | `foundation/durable_identity.py:539-563` | `from_dict` re-mints instead of replaying; `verify()` unconditionally `True` | T-23.4 |
| RA-18 | `universal_assurance/registry.py:178-182` | No chain verification on load | T-23.4 |
| RA-19 | `ceu/existence.py:989-1006` | Cyclic relationship registered, then refused | T-13.1 |
| RA-20 | `mutation_classification.py` | `classify()` ERROR for every subject (M-C) | T-19.2 |

### T-26.1 — The second mutable authority and the undisclosed closure register

1. **Current finite state.** `DEFAULT_VOCABULARIES` is a module singleton that decides UCKO lawfulness; `extend()` mutates it process-wide; there is no loader and no persistence. Mutating a UCKP vocabulary changes the **nucleus subject population** (83→84). Separately, 230 of 239 closed enums are **undisclosed** (CR-23).
2. **Evidence.** `engine/uckp/vocabulary.py:542`; TA-N1/N1b/N6; CR-23; M-A.
3. **Why it is finite.** The same defect as RA-01 in a second location, and the register that would make all closures visible is 4% complete.
4. **Universal target state.** Vocabularies persisted and reconstructed; every closed enumeration disclosed.
5. **Required architectural transformation.** Persistence for vocabularies; automated closure discovery feeding the disclosure register.
6. **Existing reusable capability.** `is_extensible` already enumerates vocabularies; `check_open_world` already fails on *"a surface declares a closed enumeration"* — the detector exists and is not pointed at the whole codebase.
7. **Required extension.** Persistence + discovery sweep.
8. **Dependency.** T-19.1 for verification; parallel to T-6.1.
9. **Validation requirement.** VR-02, VR-62.
10. **Certification requirement.** CR-01.
11. **Risk.** R-64 — disclosure will reveal ~230 closures, several of which will contradict standing certifications (notably T-23.3 Axes 13–14). Expect the register to get worse before it gets better.
12. **Classification.** **READY FOR TRANSFORMATION**

### T-26.2 — The anti-closure mechanism is itself a closed enumeration

1. **Current finite state.** 29 hand-authored gate workflows, each invoking a bespoke engine (one exceeds 3,600 lines); 46 Makefile gate targets; only 4 gates declare their mutation mode; no gate register, no generator, and **no `check_open_world` applied to the gate population**.
2. **Evidence.** `.github/workflows/`; `uaie-gate.yml:79-100`; `acee-gate.yml:72-136`; `GATE-PURITY-DETERMINATION.md:33,38`.
3. **Why it is finite.** Openness holds **inside** each gate and not **across** gates. **The meta-level is not self-similar** — the mechanism forbidding closed enumerations is built from them.
4. **Universal target state.** Gates are a registered, generated population subject to the same openness test they enforce.
5. **Required architectural transformation.** A gate register plus generation or cross-validation; `check_open_world` applied to the gate population.
6. **Existing reusable capability.** All 29 engines share a declaration + check structure; `check_open_world` exists in four engines already.
7. **Required extension.** Register + self-application.
8. **Dependency.** T-19.2 (gates classify mutations, and classification is currently broken).
9. **Validation requirement.** VR-63 — the gate population passes the openness test it applies to others.
10. **Certification requirement.** CR-23.
11. **Risk.** R-65 — self-application will likely fail initially. That is the correct outcome and the reason to do it.
12. **Classification.** **READY FOR TRANSFORMATION**

---

## 27. Ownership Dependency Analysis

### 27.1 The directive's question answered directly

> *Does ownership precede evolution?*

**Yes, necessarily.** Evidence: `require_owner()` raises `OwnershipFabricationError` rather than infer; admission checks registration and canonical-home admissibility before accepting evidence; and 391 of 542 concepts have no owner. An evolution transaction against an unowned subject has no authority to authorise it. `UCOD-001:332` separates the two cleanly — machinery ready, data 27.86% populated — so the dependency is on **data and ratification**, not on capability.

### 27.2 Ownership as a gate on other domains

| Dependent transformation | Why ownership precedes it |
|---|---|
| T-14.1 knowledge declaration | A concept cannot be canonically declared without a ratified owner; declaring it creates canonical truth nobody can amend |
| T-24.3 autonomous evolution | An autonomous mutation of an unowned subject is ungoverned by construction |
| T-19.4 source self-modification | Same, applied to source |
| T-14.3 assimilation binding | The Ownership stage of the chain currently resolves against an empty catalogue |
| T-22.4 capability admission | The admitting authority is itself unowned (`Owner: UNCLEAR / Authority: UNCLEAR`) |
| T-23.2 certification subject | A certificate names a target; an unowned target has no accountable subject |

### 27.3 The ownership chain

```
T-22.2  machine-readable authority key  (AUTHORITY DECISION)
   │
   ├──► T-6.2  identity mint federation      (same missing key)
   ├──► T-8.2  governing truth model         (same missing key)
   │
   ▼
T-22.1  evidence kinds registered  (READY)
   │
   ▼
T-22.3  391 assignments populated and ratified  (BLOCKED — owner act)
   │
   ├──► T-14.1  knowledge declaration 25.5% → 100%   (BLOCKED)
   ├──► T-24.3  autonomous evolution                  (AUTHORITY DECISION)
   └──► T-22.4  capability admission authority        (BLOCKED — external, Article 28)
```

### 27.4 What ownership does not block

Ownership does **not** gate the detection, durability, or trust transformations. T-19.1, T-19.2, T-6.1 and T-21.1 are all independent of ownership and are all READY. This matters: the programme is not stalled by CH-4, because the four highest-impact transformations sit upstream of it.

### 27.5 The unavoidable conclusion

Two ownership transformations (T-22.3, T-22.4) **terminate outside the repository**. `UCOD-001:401` states the correct posture — the determination *"will not fabricate them to close it"* — and any automated population would be precisely the fabrication the machinery is built to refuse. **Full transformation cannot complete without an owner act, and no engineering sequence removes that dependency.**

---

## 28. Implementation Dependency Graph

### 28.1 The directive's ordering questions answered

| Question | Answer | Basis |
|---|---|---|
| Does ownership precede evolution? | **Yes** | §27.1 |
| Does truth authority precede runtime independence? | **Inverted — detection precedes both** | T-19.1 must exist first or neither fix is verifiable (CH-2) |
| Does security precede assimilation? | **Yes** | T-21.1 must precede T-14.3, or the binding layer routes untrusted input into arbitrary import |
| Does identity precede entity expansion? | **Yes, and by the same artifact** | T-7.3 is T-6.1 seen from the entity dimension |

### 28.2 The graph

```
LAYER 0 — DETECTION  (no dependencies; nothing else is verifiable without these)
  ┌──────────────────────────────────┐   ┌──────────────────────────────────┐
  │ T-19.1 initialization-           │   │ T-19.2 R-09 predicate            │
  │        independence measurement  │   │        (classification restored) │
  └───────────────┬──────────────────┘   └───────────────┬──────────────────┘
                  │                                       │
LAYER 1 — DURABILITY + TRUST + INTEGRITY                  │
  ┌───────────────▼──────────────┐  ┌────────────────┐  ┌─▼───────────────┐
  │ T-6.1 committed existence    │  │ T-21.1 trust   │  │ T-19.3 mutation │
  │       document + loader wire │  │  before import │  │  class extension│
  │  ⇒ resolves RA-01…RA-11,RA-13│  │  ⇒ CH-5        │  └─────────────────┘
  └───────┬──────────────────────┘  └────┬───────────┘
          │                              │
          │  ┌───────────────────────────┴──────────┐
          │  │ T-26.1 vocabulary persistence +      │
          │  │        closure disclosure            │
          │  └──────────────────────────────────────┘
          │
          │  ┌──────────────────────────────────────┐
          │  │ T-13.1 refuse-before-register        │  (independent)
          │  │ T-23.4 verify-on-load                │  (independent)
          │  │ T-14.2 closure verdict provenance    │  (independent)
          │  │ T-17.3 connector schema/code sync    │  (independent)
          │  │ T-24.4 scale-local closure clauses   │  (independent)
          │  └──────────────────────────────────────┘
          │
LAYER 2 — INSTRUMENTATION OF CLAIMS
  ┌───────▼──────────────────────────────────────────┐
  │ T-23.3  16 unboundedness axes → executable probes│
  │   (required before any success claim is credible) │
  └───────┬──────────────────────────────────────────┘
          │
LAYER 3 — KIND OPENNESS  (all depend on Layer 1 durability)
  T-7.2 entity types      T-9.1 context kinds       T-9.2 authority/lifecycle/relation
  T-9.3 value types       T-13.2 relation co-reg    T-15.2 discovery kinds
  T-16.2 execution kinds  T-20.2 reasoner protocol  T-21.2 threat vocabulary
  T-22.1 evidence kinds   T-23.2 certification subject + class
          │
          │  ┌─────────────────────────────────────────┐
          │  │ T-15.3 lifecycle reconciliation         │ (AUTHORITY)
          │  │   gates ⇒ T-15.1, T-24.2, T-9.2         │
          │  └─────────────────────────────────────────┘
          │
LAYER 4 — COMPUTATION  (frames exist; computation added)
  T-10.2 spatial coordinates + conversions
  T-12.1 measurement conversion executor
  T-12.2 currency as registered axis
  T-7.1  root primitives instantiable
  T-8.1  axis derivation as data
  T-8.3  reality mode consequential
  T-16.1 language resolver
  T-9.4  second context set  ⇐ the empirical proof of Layer 3
  T-13.3 substrate coverage  ⇐ MUST follow Layer 0
  T-19.5 impact wiring
          │
LAYER 5 — CONVERGENCE
  ┌───────▼──────────────────────────────────────────┐
  │ T-14.3 assimilation ↔ intelligence binding layer │
  │  requires: identity, context, relationship,      │
  │            security, impact all on the path      │
  └──────────────────────────────────────────────────┘

AUTHORITY TRACK  (parallel; does not block Layers 0–4)
  T-22.2 authority key ──► T-22.3 ratification (BLOCKED) ──► T-14.1 (BLOCKED)
      └──► T-6.2 identity federation    └──► T-22.4 (BLOCKED, Article 28, external)
  T-17.1 protocol A-or-B ──► T-17.2 (BLOCKED)
  T-18.1 experience scope ──► T-18.2
  T-11.2 frame-at-mint ──► T-11.1, T-11.3
  T-20.1 intelligence scope   T-20.3 provider conclusions   T-16.3 symbolic axis
  T-14.4 storage boundary     CH-6 facet frame invariant-or-limitation

TERMINAL — requires TI-1…TI-5 all holding
  T-19.4 / T-24.3 autonomous evolution  (AUTHORITY DECISION; highest risk)
```

### 28.3 Critical path

```
T-19.1 + T-19.2  →  T-6.1  →  T-23.3  →  Layer 3 kind openness  →  Layer 4  →  T-14.3
```

Six ordered steps. Everything else is parallel or in the authority track.

### 28.4 Hard sequencing constraints

| # | Constraint | Consequence of violating it |
|---|---|---|
| SQ-1 | T-19.1 before T-6.1 | The durability fix cannot be shown to work; CH-2 persists |
| SQ-2 | T-19.2 before anything governed | Every change is unclassifiable and fails closed |
| SQ-3 | T-19.2 before T-19.3 | Extending a broken classifier extends the breakage |
| SQ-4 | T-21.1 before T-14.3 | The binding layer routes untrusted input into arbitrary import |
| SQ-5 | T-21.1 before T-20.3 | Provider conclusions enter through an execution hole |
| SQ-6 | T-6.1 before all Layer 3 | Opening kinds multiplies non-durable kinds |
| SQ-7 | T-19.1 before T-13.3 | Narrowing selection without verified coverage converts fail-wide into fail-silent |
| SQ-8 | T-15.3 before T-15.1 / T-24.2 | A status vocabulary is meaningless while six lifecycle models coexist |
| SQ-9 | T-23.3 before any success claim | Success asserted in prose form already shown unreliable |
| SQ-10 | TI-1…TI-5 before T-19.4 / T-24.3 | Autonomy over undurable, unowned, undetectable, untrusted state |
| SQ-11 | T-17.1 decision before T-17.2 | Records the validators would reject if scanned |
| SQ-12 | T-22.2 before T-22.3 | Ownership rows cannot be joined to enforcement |

### 28.5 What must happen first

**T-19.1 and T-19.2, jointly and before anything else.** Neither depends on anything. Both are small — one cross-process measurement and one predicate function. Together they restore the two faculties the programme cannot proceed without: the ability to **detect** that a fix worked, and the ability to **classify** what is being changed. Every other transformation in this determination is unverifiable or ungovernable until they exist.

---

## 29. Validation Requirements

Each requirement is stated as a test an instrument could execute. `VR-nn` references appear throughout §6–§26.

| # | Requirement | Satisfies |
|---|---|---|
| VR-01 | The same subject yields the same verdict in a fresh interpreter and a bootstrapped one, for all 72 admissible kinds | TI-2 |
| VR-02 | Delete runtime memory → reload canonical → reconstruct → compare: identical for all 13 truth objects (currently 4/2/7) | TI-1 |
| VR-03 | An identifier minted by any plane resolves in every other plane, or the federation crosswalk names the boundary | T-6.2 |
| VR-04 | All 1,461 artifact records remain valid after identifier widening | T-6.3 |
| VR-05 | A non-ASCII extension kind code is admissible and collision-free | T-6.4 |
| VR-06 | Every first-class entity in a sample resolves to a birth record | T-6.5 |
| VR-07 | A UCKO anchors to a root primitive; `UCPA-L-04` still holds (nothing reduces to the axiom) | T-7.1 |
| VR-08 | A probe node type is admissible; relation rules remain total; no unbounded edge exists | T-7.2 |
| VR-09 | All 14 reference frames resolve identically before and after axis-derivation migration; the zero-axis root frame still resolves nothing | T-8.1, T-10.1 |
| VR-10 | Every artifact resolves to exactly one governing truth model | T-8.2 |
| VR-11 | A simulated-reality assertion cannot be certified as actual | T-8.3 |
| VR-12 | All 16 context kinds resolve identically; a probe kind is admitted, persisted, honoured by a fresh validator; the universal flag requires constitutional authority | TI-3, T-9.1 |
| VR-13 | Authority precedence remains total; every relation retains a rule; no unruled relation exists at any instant | T-9.2, T-13.2 |
| VR-14 | A probe value type with a registered validator is admissible; an unvalidated type is refused | T-9.3 |
| VR-15 | Two disjoint context sets resolve without code change | T-9.4 |
| VR-16 | A coordinate in an invented system is representable; an undeclared conversion is **refused, not improvised**; `primary` is never normalised | T-10.2 |
| VR-17 | Baseline, birth, UCKO and evidence temporal claims carry qualified coordinates, or a declared exemption exists | T-11.1/2/3 |
| VR-18 | No certification asserts a date its own contract refuses | T-11.2 |
| VR-19 | Declared conversions reproduce; undeclared pairs are refused; the term evaluator is total, pure and non-eval | T-12.1 |
| VR-20 | A non-human currency from an existing declared frame is expressible; cross-currency arithmetic remains refused | T-12.2 |
| VR-21 | After a refused cyclic registration the registry contains no edge | T-13.1 |
| VR-22 | Rule totality holds after every relation registration | T-13.2 |
| VR-23 | Substrate coverage measured before and after; fail-wide remains default for uncovered subjects | T-13.3 |
| VR-24 | Canonical declaration coverage measured; no concept declared canonical without a ratified owner | T-14.1 |
| VR-25 | The closure verdict is reproducible from a bare fresh clone with no environment variables set | T-14.2 |
| VR-26 | An admitted source reaches a reasoner and produces a recorded consequence | T-14.3 |
| VR-27 | The frozen-corpus guard **fails**, never silently succeeds, under any substitution | T-14.4 |
| VR-28 | A probe artifact form is admitted without code change; all existing records remain valid | T-15.1 |
| VR-29 | A ninth discovery dimension is admissible | T-15.2 |
| VR-30 | Every artifact resolves to exactly one lifecycle authority | T-15.3 |
| VR-31 | A non-document form is admitted; an unregistered serialization still exists after transformation | T-15.4 |
| VR-32 | Two languages resolve; no `en` default appears in code | T-16.1 |
| VR-33 | Two distinct unforeseen execution kinds are separately registrable and distinguishable | T-16.2 |
| VR-34 | Symbolic systems either have an axis or a documented subsumption | T-16.3 |
| VR-35 | Under Option A the core still fails on a protocol token while the declared periphery admits one | T-17.1 |
| VR-36 | Every API record carries a typed protocol attribute | T-17.2 |
| VR-37 | Schema and runtime source vocabularies provably agree | T-17.3 |
| VR-38 | Either ≥1 UI instance exists, or the UI schemas are withdrawn | T-18.1 |
| VR-39 | A probe interaction kind is admissible; no rendering technology is selected | T-18.2 |
| VR-40 | `validate_rule_coverage` returns empty; `classify()` returns a class for a sample spanning all nine classes | T-19.2 |
| VR-41 | A class registered without a predicate is **refused at registration** | T-19.3 |
| VR-42 | No source mutation occurs outside the declared governed path | T-19.4 |
| VR-43 | Impact verdicts disclose their substrate coverage | T-19.5 |
| VR-44 | Any introduced intelligence produces falsifiable output; non-falsifiable estimates are refused | T-20.1 |
| VR-45 | A registered reasoner never seen by the release contributes; a corpus-tuned threshold is refused | T-20.2 |
| VR-46 | Provider conclusions are treated as claims requiring validation | T-20.3 |
| VR-47 | An unsigned or non-allowlisted descriptor is refused **before** import | TI-5, T-21.1 |
| VR-48 | A probe threat class is admitted; blocking severities remain total | T-21.2 |
| VR-49 | `record()` and `record_finding()` behave identically on secret content; oversized/deep inputs refused | T-21.3 |
| VR-50 | A probe evidence kind participates; a kind without a declared role is refused | T-22.1 |
| VR-51 | Every ownership row resolves to a machine-readable key; declaration and enforcement join on it | T-22.2 |
| VR-52 | Ownership closure measured; unowned subjects fail closed rather than defaulting to `UNASSIGNED` | TI-4, T-22.3 |
| VR-53 | The capability admission authority is registered, or the external dependency is declared | T-22.4 |
| VR-54 | Certificate content-addressing and deterministic ordering survive subject genericity | T-23.1 |
| VR-55 | A novel subject type is certifiable without flattening; existing certificate digests unchanged | T-23.2 |
| VR-56 | Each of the 16 unboundedness axes has a probe; **Axes 13 and 14 currently fail** | T-23.3 |
| VR-57 | A tampered chain fails on load; `verify()` returns `False` for an unverifiable record | T-23.4 |
| VR-58 | No terminal state becomes claimable; no rollback path is introduced | T-24.1, T-24.5 |
| VR-59 | A probe stage is admitted and ordered; the cycle still wraps; `append` still admits only the next stage | T-24.2 |
| VR-60 | Autonomous evolution occurs only where TI-1…TI-5 all hold | T-24.3 |
| VR-61 | No architectural bound token survives unclassified | T-24.4 |
| VR-62 | Every closed enumeration in the codebase appears in the disclosure register | T-26.1 |
| VR-63 | The gate population passes the openness test it applies to others | T-26.2 |

**63 validation requirements.** VR-01, VR-02, VR-40 and VR-47 are prerequisites for the rest: without them, satisfaction of any other requirement cannot be established.

---

## 30. Certification Requirements

Certification is required where a transformation changes what the system asserts, not merely how it computes. Each `CR-nn` names the obligation, not a certificate.

| # | Obligation | Applies to | Notes |
|---|---|---|---|
| CR-01 | Runtime-independence certification: chain A demonstrated for all truth objects, with the instrument reproducible cross-process | T-6.1, T-19.1, T-26.1 | Must replace, not supplement, the current single-process determinism evidence |
| CR-02 | Identity certification: mint federation or governing declaration, with lineage preserved for already-issued identifiers | T-6.2, T-6.5 | `CAA-INV-04` must continue to hold |
| CR-03 | Identifier-space certification: widened patterns valid across schema and code with no divergence | T-6.3, T-6.4 | Drift check mandatory (cf. C-34/C-35) |
| CR-04 | Ontology certification: primitives instantiable while remaining ratified; `UCPA-L-04` intact | T-7.1, T-7.2 | Instantiation must not become an amendment path |
| CR-05 | Frame certification: axis derivation as data with the fail-closed reality gate refusing a shrinking axis set | T-8.1, T-10.1 | Preservation-critical |
| CR-06 | Truth-model certification: one governing model declared, or federation with crosswalks | T-8.2, T-8.3 | Authority act |
| CR-07 | Context certification: kind, authority, lifecycle, relation and value-type vocabularies open with invariants intact | T-9.1–T-9.4, T-13.2 | Universal flag must require constitutional authority |
| CR-08 | Spatial certification: coordinates representable, conversions refused when undeclared, no canonical frame adopted | T-10.2 | Must replicate the temporal no-normalisation rule |
| CR-09 | Temporal certification: no certification asserts an unqualified date, or the exemption is declared | T-11.1–T-11.3 | Touches an existing certification |
| CR-10 | Measurement certification: conversions reproducible; currency axis registered; closure disclosed before fixed | T-12.1, T-12.2 | Disclosure precedes remediation |
| CR-11 | Relationship certification: refuse-before-register; substrate coverage disclosed with every impact verdict | T-13.1, T-13.3, T-19.5 | |
| CR-12 | Knowledge certification: declaration coverage stated; closure verdict reproducible from a bare clone; every declared concept owned | T-14.1–T-14.4 | Will change the headline number |
| CR-13 | Artifact certification: form admissible by registration; lifecycle authority singular; existing records valid | T-15.1–T-15.4 | |
| CR-14 | Language certification: ≥2 languages resolve; execution kinds individually identified | T-16.1–T-16.3 | |
| CR-15 | Protocol certification: **constitutional** — the Option A/B decision recorded, `USL-15` status explicit | T-17.1–T-17.3 | Cannot be an engineering act |
| CR-16 | Experience certification: scope declared; schemas populated or withdrawn | T-18.1, T-18.2 | |
| CR-17 | Mutation certification: classification total; extension refuses predicate-less classes; source mutation path declared | T-19.2–T-19.4 | Must disclose mutations certified while unclassified |
| CR-18 | Intelligence certification: falsifiability preserved for any introduced reasoning; reasoners registered not imported | T-20.1–T-20.3 | |
| CR-19 | Security certification: trust before import; threat vocabulary open; adversarial bounds uniform | T-21.1–T-21.3 | Highest urgency |
| CR-20 | Governance certification: ownership closure measured and **ratified**; authority key machine-readable | T-22.1–T-22.4 | Blocked on owner and external acts |
| CR-21 | Certification-of-certification: subject genericity without loss of integrity; 16 axes instrumented; verify-on-load | T-23.1–T-23.4 | Replaces prose certifications |
| CR-22 | Evolution certification: non-termination preserved; stage set open with ordering intact; refusals preserved | T-24.1–T-24.5 | |
| CR-23 | Gate certification: the gate population passes its own openness test | T-26.2 | Self-application |

### 30.1 The overriding certification constraint

**CR-21 must be discharged before any other certification is credible.** The repository's standing unboundedness certification rests on prose citation, no machine certificate confers constitutional finality (`UCERT_AUTHORITY = "ENGINEERING-EXECUTION-ONLY"`), and ~15 root-level certifications assert completeness without evidence binding. Until the 16 axes are instrumented (T-23.3), any claim that a transformation succeeded would be recorded in the same evidential form this determination has shown to be unreliable — including a claim about this programme.


---

## 31. Risk Register

Risks are of **transformation**, not of the current state. Severity reflects consequence if the risk materialises during transformation.

| # | Risk | Severity | Transformation | Mitigation constraint |
|---|---|---|---|---|
| R-01 | The existing reconstruction test's fixture calls `bootstrap()`, so it cannot detect failure of the durability fix | **HIGH** | T-6.1, T-7.3 | T-19.1 must exist first (SQ-1) |
| R-02 | Declaring one mint governing invalidates identifiers issued by the others; federation may itself become a second identity authority | **HIGH** | T-6.2 | `CAA-INV-04` must hold |
| R-03 | Identifier pattern is mirrored in ≥3 places; divergence reproduces the C-34/C-35 drift failure | MEDIUM | T-6.3 | Single source of truth (T-17.3 pattern) |
| R-04 | Wider code alphabet changes collision semantics | LOW | T-6.4 | Re-verify collision refusal |
| R-05 | Wiring birth into hot paths may mint identifiers as a side effect — precedent: 140 minted by a drift check | **HIGH** | T-6.5 | Birth only on declared intent, never as a side effect |
| R-06 | Instantiating root primitives becomes a path to amending them | **HIGH** | T-7.1 | `UCPA-L-04` and ratified standing must hold |
| R-07 | Opening node types permits unbounded edges — the condition `ContextOntology.__init__` refuses | **HIGH** | T-7.2 | Rule totality over the widened set |
| R-08 | Axis list as data means a data edit can weaken a constitutional gate | **HIGH** | T-8.1 | Gate must refuse an empty or shrinking axis set |
| R-09 | Declaring one truth model governing orphans artifacts authored under the other | MEDIUM | T-8.2 | Migration or federation |
| R-10 | Reality-mode-aware certification refuses subjects currently accepted | MEDIUM | T-8.3 | Sequence after T-23.2 |
| R-11 | If universality becomes registrable, a data edit could declare an arbitrary kind universal | **HIGH** | T-9.1 | Universal flag requires constitutional authority |
| R-12 | Registering an authority level without a declared position makes precedence partial and resolution non-deterministic | **HIGH** | T-9.2 | Position mandatory at registration |
| R-13 | A registered value type with an unsound validator admits malformed values | MEDIUM | T-9.3 | Validators pure and total |
| R-14 | Lowest-risk transformation; failure mode is a failed resolve, not a corrupted verdict | LOW | T-9.4 | — |
| R-15 | **The risk is transforming what is already correct.** Spatial addressing is universal today | **HIGH** | T-10.1 | `PROHIBITED_TOKENS` and the zero-axis root frame must survive |
| R-16 | A spatial registry that adopts a canonical frame destroys the property S-01 protects | **HIGH** | T-10.2 | Replicate *"`primary` is never normalised"* exactly |
| R-17 | A temporal migration that forces a default frame destroys the property being adopted | **HIGH** | T-11.1 | This is why non-adoption was deliberate (`P4-F-007`) |
| R-18 | Re-qualifying certified baseline dates changes certified content | **HIGH** | T-11.2 | Authority act; exemption is lower-risk but records a permanent hole |
| R-19 | Scope creep: treating run timestamps as constitutional temporal claims | LOW | T-11.3 | Declare the boundary |
| R-20 | A conversion executor evaluating string terms becomes a code-execution surface | **HIGH** | T-12.1 | Total, pure, non-eval evaluator; must not reproduce CH-5 |
| R-21 | Re-typing `Money` touches priced commitments; and the closure must be **disclosed before fixed** | MEDIUM | T-12.2 | Disclosure precedes remediation |
| R-22 | Same validate-after-mutate pattern as CH-5 | MEDIUM | T-13.1 | Fix establishes the pattern for T-21.1 |
| R-23 | Moving refusal to registration time may create a window where an unruled relation exists | **HIGH** | T-13.2 | Atomic co-registration |
| R-24 | **Narrowing selection without verified coverage converts fail-wide into fail-silent** | **CRITICAL** | T-13.3 | Must never precede T-19.1 (SQ-7) |
| R-25 | Declaring knowledge canonical without a ratified owner creates canonical truth nobody can amend | **HIGH** | T-14.1 | Blocked on T-22.3 |
| R-26 | Resolving the closure verdict changes `gaps=0` to non-zero (evidence: 91); every citing artifact becomes stale | MEDIUM | T-14.2 | Truth-restoring; expect wide documentary consequence |
| R-27 | **Binding the planes early routes unvalidated, unidentified, unowned, unsecured input into reasoning** | **CRITICAL** | T-14.3 | Must be last among its five dependencies (SQ-4) |
| R-28 | The frozen-corpus guard silently succeeds under substitution — independent of the neutrality question | **HIGH** | T-14.4 | Fix regardless of the storage decision |
| R-29 | Replacing `additionalProperties: false` may permit unvalidated fields, so the schema stops being a contract | **HIGH** | T-15.1 | Declared-extension mechanism, not open shape |
| R-30 | Low | LOW | T-15.2 | — |
| R-31 | Consolidating six lifecycle models invalidates stage assignments corpus-wide | **HIGH** | T-15.3 | Federation is the lower-risk path |
| R-32 | A reader registered as data implies code loaded as data | **HIGH** | T-15.4 | Must not reproduce CH-5 |
| R-33 | Low; remediation already specified with an acceptance criterion | LOW | T-16.1 | — |
| R-34 | `FUTURE_LANGUAGE` is bound to a live adapter class; retiring it requires re-homing that binding | MEDIUM | T-16.2 | — |
| R-35 | Adding a symbolic axis speculatively is worse than determining first | MEDIUM | T-16.3 | Record as unresolved (the `unknown`-as-valid discipline) |
| R-36 | The marker check is a **naive substring scan** — `"lambda"`, `"rest"` false-positive; narrowing it narrows unintended places | **HIGH** | T-17.1 | Fix matching semantics as part of any change |
| R-37 | Populating the API registry while `USL-15` stands creates records the validators would reject | **HIGH** | T-17.2 | Blocked on T-17.1 (SQ-11) |
| R-38 | Low risk, high diagnostic value | LOW | T-17.3 | Establishes drift prevention for T-15.1, T-6.3 |
| R-39 | Building experience speculatively adds a dimension with no consumer; withdrawing forecloses a direction | MEDIUM | T-18.1 | Scope decision first |
| R-40 | Low; the rendering-technology refusal must survive | LOW | T-18.2 | — |
| R-41 | Introducing initialization-independence measurement **turns green gates red** | MEDIUM | T-19.1 | Intended effect; not a regression |
| R-42 | Restoring classification may reveal mutations certified while unclassified | **HIGH** | T-19.2 | Expect disclosure, not silence |
| R-43 | The current defect exists because a class was registered without a predicate; extension must make that impossible | **HIGH** | T-19.3 | Refuse at registration (VR-41) |
| R-44 | **Autonomy over undurable, unowned, undetectable, untrusted state** | **CRITICAL** | T-19.4, T-24.3 | TI-1…TI-5 must all hold (SQ-10) |
| R-45 | Impact analysis over 10.4% substrate coverage produces confident reports with wide blind spots | **HIGH** | T-19.5 | Disclose coverage with every verdict |
| R-46 | A model whose output cannot be re-derived reintroduces belief over evidence | **CRITICAL** | T-20.1 | Falsifiability mandatory |
| R-47 | An open reasoner registry is a code-loading surface | **HIGH** | T-20.2 | Register, never import from data |
| R-48 | Provider conclusions bypassing validation become belief | **HIGH** | T-20.3 | Sequence after T-21.1 (SQ-5) |
| R-49 | **Hardening the provider path narrows the one genuinely open admission mechanism (PC-14)** | **CRITICAL** | T-21.1 | Preserve open admission while requiring verification |
| R-50 | Opening severities without declared ordering makes blocking non-deterministic | **HIGH** | T-21.2 | Same total-order hazard as R-12 |
| R-51 | The `record()` docstring/implementation mismatch means current reliance is unfounded; fixing may reject accepted content | MEDIUM | T-21.3 | — |
| R-52 | Registrable evidence kinds could let a data edit declare weak evidence constitutive, fabricating ownership | **CRITICAL** | T-22.1 | Constitutive status requires constitutional authority |
| R-53 | Making ownership rows machine-readable exposes rows that do not resolve | MEDIUM | T-22.2 | Intended effect |
| R-54 | **Automated population of 391 assignments is exactly the fabrication the machinery refuses** | **CRITICAL** | T-22.3 | `UCOD-001:401` — will not fabricate to close |
| R-55 | Proceeding under *"already operational"* while the blocking determination stands admits capabilities under contested authority | **HIGH** | T-22.4 | Resolve F-20 first |
| R-56 | Degrading certification integrity while opening the subject type | **HIGH** | T-23.1, T-23.2 | Content-addressing and determinism must survive |
| R-57 | A protocol-typed subject whose rules cannot interpret its inputs produces confident wrong verdicts | **HIGH** | T-23.2 | Preserve the input guarantee |
| R-58 | Instrumenting the axes will invalidate a standing certification | MEDIUM | T-23.3 | Expected; the point of the exercise |
| R-59 | An unconditional `True` in `verify()` means current reliance is unfounded; fixing may invalidate adopted records | **HIGH** | T-23.4 | — |
| R-60 | Opening the stage set may introduce a stage from which the cycle cannot continue | **HIGH** | T-24.1, T-24.2 | No terminal state claimable (VR-58) |
| R-61 | A registered stage without a declared position breaks `append`'s fail-closed ordering | **HIGH** | T-24.2 | Position mandatory |
| R-62 | Low; the finding is that an existing gate does not cover documents it should | LOW | T-24.4 | — |
| R-63 | **A programme under pressure will be tempted to add rollback. It must not** | **HIGH** | T-24.5 | Consequence: no rollback for an evolution that reaches truth incorrectly — raises the pre-admission bar |
| R-64 | Disclosure reveals ~230 closures, several contradicting standing certifications | MEDIUM | T-26.1 | Register gets worse before better |
| R-65 | Gate self-application will likely fail initially | LOW | T-26.2 | Correct outcome; the reason to do it |

### 31.1 Risk concentration

**Eight CRITICAL risks**, and they cluster in three patterns:

1. **Sequencing violations** (R-24, R-27, R-44) — each is a case of doing correct work in the wrong order. All three are prevented by SQ-4, SQ-7 and SQ-10 respectively.
2. **Openness without authority** (R-49, R-52) — opening a vocabulary whose members carry authority (constitutive evidence, provider execution) converts a data edit into an authority act. Both require an authority gate on the specific privileged attribute, not on registration generally.
3. **Fabrication and belief** (R-46, R-54) — introducing non-falsifiable output, or populating ownership automatically, would both defeat the architecture's founding purpose. Both are explicitly refused by existing determinations and must remain refused.

### 31.2 The risk this determination itself creates

Recorded for completeness: this determination classifies 30 transformations as READY FOR TRANSFORMATION. That classification is a statement about **architectural feasibility**, not authorization. Reading it as a work list — particularly beginning at Layer 3 kind openness, which is the most visible and most satisfying work — would violate SQ-1, SQ-2 and SQ-6 simultaneously and produce a larger population of non-durable, unclassifiable kinds than exists today. **The determination's value is the ordering, not the inventory.**

---

## 32. Reuse Analysis

### 32.1 Reuse classification across the 67 transformations

A transformation may carry more than one reuse mode (a preservation item is both REUSE and a constraint), so the column sums exceed 67 by design; the point of the table is the absence of CREATE, not the arithmetic.

| Classification | Count | Transformations |
|---|---|---|
| **REUSE** — capability exists; wire or adopt | 11 | T-6.1, T-6.5, T-7.3, T-11.1, T-11.3, T-19.5, T-21.1, T-23.4, T-14.2, T-10.1 (preserve), T-24.1/T-24.5 (preserve) |
| **EXTEND** — pattern exists; extend it | 33 | T-6.3, T-6.4, T-7.1, T-7.2, T-8.1, T-8.3, T-9.1, T-9.2, T-9.3, T-10.2, T-12.1, T-12.2, T-13.1, T-13.2, T-13.3, T-15.1, T-15.2, T-15.4, T-16.1, T-16.2, T-19.1, T-19.2, T-19.3, T-20.2, T-21.2, T-21.3, T-22.1, T-23.2, T-23.3, T-24.2, T-24.4, T-26.1, T-26.2 |
| **COMPOSE** — engines exist; bind them | 2 | T-14.3, T-9.4 |
| **HOLD** — awaiting decision or external act | 19 | the 15 REQUIRES AUTHORITY DECISION items, the 4 BLOCKED items, and CH-6 as the governing open question |
| **TRUE MISSING** — no in-repo pattern | 6 | Threat model as data (partial), economic/value model, possibility-space capability, experience runtime, protocol representation, reasoner conclusions |
| **CREATE** | **0** | — |

### 32.2 No CREATE is required

Every transformation resolves to reuse, extension, composition, a decision, or an acknowledged absence. This is the strongest evidence that UCOS Ω∞ is an **incomplete substrate rather than a mis-designed one**, and it is the single most important input to any implementation decision: there is no missing engine to build.

### 32.3 The two mechanisms that carry the programme

Nearly every EXTEND above reduces to one of two existing mechanisms:

**S-13 — `engine/uckp/vocabulary.py`.** Append-only, refuses redefinition, register-then-use, openness proved by probe (`is_extensible` admits `uckp.future-probe` and fails INV-14 on refusal). **Nineteen** transformations are vocabulary conversions against this mechanism: T-7.2, T-9.1, T-9.2, T-9.3, T-13.2, T-15.1, T-15.2, T-16.2, T-18.2, T-20.2, T-21.2, T-22.1, T-23.2, T-24.2, and the placeholder retirements in T-15.4/T-16.2.

**S-14 — `check_open_world`.** Fails closed on bound tokens, closed registries, absent re-entry, claimed terminal states, and *"no unregistered serialization is admitted, so the registry is closed in practice."* **Four** transformations are applications of this instrument to surfaces it does not currently cover: T-23.3 (16 axes), T-24.4 (scale clauses), T-26.1 (closure disclosure), T-26.2 (gate self-application).

### 32.4 The three highest-impact transformations are the smallest

| Transformation | Size | Unblocks |
|---|---|---|
| T-19.2 — one predicate function | ~1 function | Classification of every change in every dimension (CH-3) |
| T-6.1 — one committed document + one load call | 1 artifact + wiring | CH-1, RA-01…RA-11, RA-13; 43 of 72 kinds; 9 enforcement sites |
| T-21.1 — one verification call + one reorder | ~3 edits | CH-5, the sole critical security defect |

Approximately three small changes address three of the seven defect chains, including the two that gate everything else. This asymmetry — smallest work, largest consequence — is the determination's principal practical finding.

### 32.5 Reusable patterns already proven in-repo

Each is a template a transformation should copy rather than reinvent:

| Pattern | Reference implementation | Applied by |
|---|---|---|
| Registered vocabulary with probe-proved openness | `engine/uckp/vocabulary.py` | 19 transformations |
| No default, UNRESOLVED with derivation path | `engine/context/location.py` | T-8.1, T-16.1 |
| Never normalise; refuse bare values; INCOMPARABLE | `engine/temporal/coordinate.py` | T-10.2, T-12.1 |
| Register systems and conversions, never infer | `engine/temporal/operations.py` | T-10.2, T-12.1 |
| Replay verbatim, refuse re-derivation, fail on audit | `engine/ceu/existence.py:773` | T-6.1, T-23.4 |
| Openness that fails if nothing remains to admit | `acee_engine.py check_open_world` | T-23.3, T-26.1, T-26.2 |
| Zero-enumeration governing module, machine-checked | `platform/universal_foundation/` | T-17.2, T-22.1 |
| Data-declared stages with derived ordering | `platform/universal_pipeline/contracts.py` | T-24.2 |
| Anti-fabrication refusal | `require_owner()` | T-22.3 (as constraint) |
| Co-registration of member and rule | `RELATION_RULES` | T-9.2, T-13.2, T-19.3, T-22.1 |

---

## 33. Gap Analysis

### 33.1 True gaps, and whether they are defects

| Gap | Present state | Is it a defect? |
|---|---|---|
| Threat model as data | No threat/attack-surface/trust-boundary/adversary model exists anywhere; `14-SECURITY/` is 5 prose files | **Yes.** Security is the one dimension where openness is unambiguously required and unambiguously absent |
| Economic/value model | Nuclei are declared names; only a self-facing quote calculator exists; currency shape contradicts declared frames | **Yes** for currency (T-12.2); **scope question** for the wider value model |
| Possibility-space capability | Deliberately refused; no branching, scenario or counterfactual machinery; `reality_mode` inert | **No** — the refusal is reasoned. But `GOVERNED_CATEGORIES` includes `simulation` with no engine, which is a **declaration/mechanism mismatch** |
| Experience runtime | Zero instances, zero frontend, 4-member interaction vocabulary, schemas weaker than neighbours | **Scope question**, plus an internal inconsistency (declared-but-empty schemas) |
| Protocol representation | Prohibited by gate; registry empty; admitting one weakens a constitutional gate | **No** — constitutional intent. The **inconsistency** (a registry requiring `protocol` with zero records) is a defect |
| Reasoner conclusions | Closed 13-member enum, hardcoded dispatch, provider protocol has no `propose()` | **Yes** for the closed dispatch (T-20.2); **scope question** for conclusions |
| Spatial computation | No coordinates, geometry or algebra; specified `[N]` in UCOS-CVR-001 §04 | **Yes** — declared and unrealized |
| Measurement computation | No conversion executor, no `Quantity` type | **Yes** — declarable, not computable |
| Unified lifecycle | Six incompatible models; determination artifacts have none | **Yes** — and this artifact is itself in that void |
| Assimilation↔intelligence edge | Two complete, mutually unreachable planes; feedback loop is prose | **Yes** — the defining knowledge-evolution gap |

### 33.2 Gaps that close themselves under other transformations

| Gap | Closed by |
|---|---|
| Entity kind durability | T-6.1 (identical defect) |
| Nine enforcement-site verdict instability | T-6.1 |
| Undetectable statefulness | T-19.1 |
| Unclassifiable new artifact kinds | T-19.2 + T-19.3 |
| Symbolic-system axis cost | T-9.1 (becomes a registration rather than an amendment) |
| Alien context resolution | T-9.4 (data only) |
| Language resolution | T-16.1 (the axis is already open in the location layer) |

### 33.3 Gaps that cannot be closed inside the repository

| Gap | Terminus |
|---|---|
| 391 ownership ratifications | Owner act; `UCOD-001:401` refuses fabrication |
| UKAP/UREE registration | CEP-002 Article 28; *"no competent ratifying authority located within the repository"* |
| Protocol Option A vs B | Constitutional decision on `USL-15` |
| Facet frame invariant-or-limitation (CH-6) | Constitutional decision on whether 33 facets is invariant |
| Autonomy of evolution | Authority decision, gated on TI-1…TI-5 |
| Experience scope | Authority decision on what UCOS Ω∞ is for |

### 33.4 The gap that most changes the answer

**CH-6 — whether the 33-facet frame is a true invariant or a limitation — is unresolved, and it determines whether "infinite evolution" is achievable at all.**

If 33 facets is an invariant, then UCOS Ω∞ can be infinite in *population* and is permanently bounded in *description*, and the honest target is "unbounded within a fixed descriptive frame." If it is a limitation, then the frame must open, and the doctrine at `engine/uckp/facets.py` (*"Adding a thirty-fourth facet is a constitutional amendment"*) must be amended.

**No engineering work resolves this, and no transformation below Layer 3 depends on it.** But the final answer to the directive's overall objective does. This determination records it as the single most consequential open question and does not decide it.

---

## 34. Implementation Readiness Assessment

### 34.1 The question

> *What is required before implementation can safely begin?*

### 34.2 Readiness by prerequisite

| # | Prerequisite | State | Blocking? |
|---|---|---|---|
| P-1 | Classification functional — every change classifiable | **NOT MET.** `classify()` returns ERROR for every subject (M-C) | **YES** — no change can be governed |
| P-2 | Detection functional — a fix can be shown to work | **NOT MET.** Zero of 29 gates vary initialization order; the determinism harness runs both builds in one interpreter | **YES** — no fix is verifiable |
| P-3 | Claims instrumented — success can be credibly asserted | **NOT MET.** 16 unboundedness axes certified on prose; no machine certificate confers constitutional finality | **YES** for any completion claim |
| P-4 | Ownership resolvable — a change has an owner | **NOT MET.** 391/542 unowned, catalogue empty, 0% ratified | **YES** for governed change; **NO** for Layer 0–1 work |
| P-5 | Authority key machine-readable — declaration joins enforcement | **NOT MET.** Three disclaiming planes, no shared key | **YES** for P-4 |
| P-6 | Trust before execution — no arbitrary import | **NOT MET.** CH-5 unfixed | **YES** for any widening of admission |
| P-7 | Durability — admitted kinds survive process death | **NOT MET.** No committed existence document | **YES** for Layer 3 |
| P-8 | Lifecycle authority singular | **NOT MET.** Six incompatible models | **YES** for T-15.1, T-24.2 |
| P-9 | Facet frame status decided (CH-6) | **NOT MET.** Undecided | **YES** for the completion claim; **NO** for Layers 0–2 |
| P-10 | Protocol Option A/B decided | **NOT MET.** Undecided | **YES** for domain O only |
| P-11 | Experience scope decided | **NOT MET.** Undecided | **YES** for domain P only |
| P-12 | Autonomy decision | **NOT MET.** Undecided | **YES** for T-19.4/T-24.3 only |
| P-13 | Contradictions resolved | **NOT MET.** 27 live, incl. F-20 on UKAP/UREE status | **YES** for the affected domains |
| P-14 | External act (Article 28) | **NOT AVAILABLE IN-REPO** | **YES** for T-22.3/T-22.4 |
| P-15 | Complete architectural understanding of the constraint space | **MET.** 78 constraints inventoried and classified; 67 transformations analysed; dependency graph derived; no CREATE required | — |

**One prerequisite met of fifteen.**

### 34.3 What is ready

Layer 0 and most of Layer 1 are ready **now**, and they are the only work that is:

| Ready | Why it is safe to begin |
|---|---|
| T-19.1 initialization-independence measurement | No dependencies; restores detection |
| T-19.2 R-09 predicate | No dependencies; restores classification |
| T-6.1 committed existence document + loader wire | After T-19.1; resolves 13 of 20 runtime-authority violations |
| T-21.1 trust before import | No dependencies; closes the sole critical security defect |
| T-13.1 refuse-before-register | Independent, single-site |
| T-23.4 verify-on-load | Independent, three sites |
| T-14.2 closure verdict provenance | Independent; truth-restoring |
| T-17.3 connector schema/code sync | Independent; establishes drift prevention |
| T-24.4 scale-clause classification | Independent |
| T-23.3 axis instrumentation | After T-19.1; prerequisite for any success claim |

Ten transformations. All are REUSE or EXTEND. None requires an authority decision. Three are approximately one function, one document, and three edits respectively.

### 34.4 What is not ready and why

- **Layer 3 kind openness (11 transformations)** — blocked on P-7 (durability). Opening kinds first multiplies non-durable kinds. This is the most attractive and most dangerous starting point.
- **Layer 4 computation (10 transformations)** — mostly blocked on Layer 3, and T-13.3 is blocked on P-2 with a CRITICAL risk (R-24) if started early.
- **Layer 5 binding (T-14.3)** — blocked on five domains; starting it early is the highest-severity sequencing error available (R-27).
- **Authority track (17 transformations)** — blocked on decisions no engineering act supplies.
- **Terminal autonomy (T-19.4/T-24.3)** — blocked on all five target invariants; R-44 is CRITICAL.

### 34.5 Readiness determination

**NOT READY** — for implementation of the transformation programme as a whole.

**READY** — for the ten Layer 0/1 transformations in §34.3, which are precisely the work that restores the faculties required to judge everything else.

The distinction is not a hedge. Beginning the programme at Layer 0 is safe and unblocks the rest; beginning it anywhere else is unsafe regardless of engineering quality, because the system currently cannot classify what is being changed (P-1) or detect whether a change worked (P-2).

---

## 35. Final Architectural Determination

### 35.1 Answer to the primary question

> *Can every currently finite implementation boundary be transformed into an open universal capability without architectural redesign?*

**No — but 75 of 78 can, and the three that cannot are not engineering problems.**

| Partition | Count | Verdict |
|---|---|---|
| True invariants | 7 | Must not be transformed; transformation is regression |
| Representation choices | 22 | Transformable by registration (S-13) |
| Implementation limitations | 25 | Transformable by extension |
| Architectural defects | 24 | 21 transformable; 3 require amendment or external act |

The three exceptions: **C-36** (protocol prohibition — a constitutional position, not a defect), **CH-6** (the 33-facet frame — an amendment by the repository's own doctrine), **T-22.3/T-22.4** (ownership ratification and capability admission — external acts with no competent in-repo authority).

### 35.2 Answer to the transformation chain

```
FINITE IMPLEMENTATION  →  UNIVERSAL CAPABILITY  →  AUTONOMOUS EVOLUTION
```

- **FINITE IMPLEMENTATION → UNIVERSAL CAPABILITY: reachable.** 47 transformations are classified READY, all REUSE/EXTEND/COMPOSE, **zero CREATE**. The two mechanisms that carry the work (S-13, S-14) already exist and are already proven by probe. Reachable does not mean available now: only the ten in §34.3 may begin, the rest being gated by dependency order.
- **UNIVERSAL CAPABILITY → AUTONOMOUS EVOLUTION: not reachable by extension.** Autonomy is a change of kind requiring TI-1…TI-5 to hold first, and the architecture's three confinements against self-modification are a safety property rather than a gap. Classification: REQUIRES AUTHORITY DECISION.

### 35.3 Transformation classification roll-up

Across the **67** transformation analyses in §6–§26:

| Classification | Count | Share |
|---|---|---|
| READY FOR TRANSFORMATION | 47 | 70% |
| REQUIRES AUTHORITY DECISION | 15 | 22% |
| REQUIRES FOUNDATION CHANGE | 1 | 2% |
| REQUIRES NEW CAPABILITY | **0** | **0%** |
| BLOCKED | 4 | 6% |

Two qualifications on the 47 READY, so the figure is not read as overstating available work. Four are READY **as preservation** — T-10.1, T-23.1, T-24.1, T-24.5 require no change and are classified READY only to record that transformation would be regression. A further set is READY-but-sequenced: only the ten in §34.3 are ready **now**; the rest are blocked by dependency order (SQ-1…SQ-12), not by capability.

**Zero transformations require a new capability.** Four are BLOCKED — T-14.1, T-17.2, T-22.3, T-22.4 — and every one is blocked on an authority or external act, never on missing engineering.

### 35.4 What the determination establishes

1. **Every finite constraint is inventoried and classified** — 50 enumerations, 13 patterns, 15 technology assumptions, four-way classified (§25).
2. **Every runtime authority leakage is registered and mapped to a transformation** — 20 violations, 13 of which resolve through a single artifact (§26).
3. **Every missing universal capability is classified for reuse** — 11 REUSE, 27 EXTEND, 2 COMPOSE, 17 HOLD, 6 TRUE MISSING, **0 CREATE** (§32).
4. **Every required transformation has a target, a reuse path, a dependency, a validation and certification requirement, and a risk** — 63 analyses across 19 domains (§6–§26).
5. **Dependency order is derived from evidence, not preference** — a six-step critical path and 12 hard sequencing constraints (§28).
6. **Validation requirements are stated as executable tests** — 63 requirements, four of them prerequisites for the rest (§29).
7. **Certification obligations are identified, with one overriding constraint** — CR-21 must precede any credible success claim (§30).
8. **Risks are concentrated and named** — 65 risks, 8 CRITICAL, clustering into sequencing violations, openness-without-authority, and fabrication/belief (§31).

### 35.5 The four corrections this determination makes to the directive's premises

Recorded because acting on the directive as written would damage the architecture:

1. **Not every finite boundary is a limitation.** Seven are true invariants; three of the sound foundations (spatial addressing, non-termination, the evolution refusals) would be *degraded* by transformation. §10 documents a domain where the instruction to "remove fixed locations" has no target because there are none.
2. **The protocol verdict is not a defect to remediate.** It is `USL-15` working as designed. Opening it is an amendment about what UCOS Ω∞ is for, not a fix.
3. **"Truth authority precedes runtime independence" is inverted.** Detection precedes both: without T-19.1, neither can be shown to work.
4. **Autonomous evolution is not the third step of a gradient.** It is a change of kind, dependent on all five target invariants, and carrying the highest-severity risk in the register (R-44).

### 35.6 Final test

> *Can UCOS Ω∞ now proceed from discovery into implementation without discovering additional foundational architectural gaps?*

# NOT READY

### 35.7 Basis for NOT READY

Four reasons, each independently sufficient:

1. **The system cannot presently classify what would be changed.** `classify()` returns ERROR for every subject in the repository (M-C, reproduced). `UNRESOLVED` fails closed and is documented as never a permissive default. Every transformation in this determination would itself be an unclassifiable mutation. This is not a foundational *gap* — it is a **live outage** in the mechanism that governs change, and it is one missing predicate.

2. **The system cannot detect whether a fix worked.** Zero of 29 gates vary initialization order; the only reproducibility harness builds twice in one interpreter sharing env, adapter and signer. Implementing T-6.1 today would produce no verifiable evidence of success, and the existing reconstruction test cannot detect its failure because its own fixture calls `bootstrap()` (R-01).

3. **Two foundational questions are undecided, and both change the target.** CH-6 — whether 33 facets is an invariant or a limitation — determines whether "infinite evolution" means unbounded population within a fixed descriptive frame, or an open frame. The protocol Option A/B decision determines whether an entire dimension is in scope. Beginning implementation before these are decided means discovering, mid-programme, that the target was wrong. That is precisely the discovery the directive seeks to avoid.

4. **Ownership terminates outside the repository, and 27 contradictions remain live.** 391 of 542 concepts unowned with 0% ratified; the assignment catalogue empty; UKAP/UREE blocked on an act with *"no competent ratifying authority located within the repository"*; and two determinations disagree on whether that block exists (F-20). Governed implementation of anything cannot begin while the authority to govern it is unlocated and contested.

### 35.8 What NOT READY does not mean

It does not mean the architecture is unsound. §32.2 is the counter-evidence: **no transformation requires a new capability**, and the three highest-impact fixes are approximately one predicate function, one committed document, and three edits. The substrate is incomplete, not mis-designed.

It does not mean no work may begin. Ten Layer 0/1 transformations are READY (§34.3), independent of every blocked prerequisite, and they are exactly the work that restores the faculties needed to judge the rest.

### 35.9 The determination stated precisely

UCOS Ω∞ has a **complete and correct architectural understanding of its own finite constraint space** — that is what P-15 records and what this determination establishes. What it lacks is the **operational capacity to change itself under governance**: it cannot classify a change, cannot detect whether a change worked, cannot durably retain what it admits, cannot locate the owner of most of what it contains, and has not decided two questions that define the target.

Implementation of the transformation programme is therefore **NOT READY**. Implementation of the ten transformations that restore classification, detection, durability and trust is **READY**, and no further discovery is required to begin them.

The remaining foundational gaps are not architectural. They are **four decisions and one external act**:

- CH-6 — is the 33-facet frame an invariant or a limitation?
- T-17.1 — Option A or Option B for protocol representation?
- T-18.1 — is experience in scope?
- T-19.4 / T-24.3 — is autonomy wanted, and under what invariants?
- T-22.3 / T-22.4 — the Article 28 act, which no derived-truth cycle may perform.

Until those are settled, further discovery will keep returning the same answer, because the unresolved items are not findable by analysis. They are choices.

# FINAL DETERMINATION: NOT READY

---

*This determination modified no code, configuration, registry, schema, constitution, law, identifier, requirement, ADR, phase, roadmap, or certification. It creates no identity and confers no authority. It authorizes no implementation, closes no scope, and claims no completion. Every gap recorded here remains a gap; no gap has been converted into a fix; and no implementation decision has been made. Where a constraint is constitutional intent rather than defect, this determination records it as such and declines to propose its removal.*
