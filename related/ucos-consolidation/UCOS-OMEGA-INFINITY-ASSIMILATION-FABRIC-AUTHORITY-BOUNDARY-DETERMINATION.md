# UCOS Ω∞ — UNIVERSAL ASSIMILATION FABRIC AUTHORITY BOUNDARY DETERMINATION

| Field | Value |
|---|---|
| ARTIFACT | `UCOS-OMEGA-INFINITY-ASSIMILATION-FABRIC-AUTHORITY-BOUNDARY-DETERMINATION.md` |
| CLASSIFICATION | `EVIDENCE` — derived analysis. Not an instrument, not a certificate, not a design authorization. |
| AUTHORITY | **NONE — DERIVED TRUTH.** Legislates nothing, ratifies nothing, certifies nothing, assigns no ownership, selects no authority, mints no identifier, creates no requirement, creates no ADR, alters no registry, creates no engine, changes no certification state. Where this determination and a located instrument differ, **the located instrument governs.** |
| MODE | **OBSERVE.** Determination only. |
| MUTATION | **READ-ONLY OBSERVATION.** The single mutation is the creation of this file. No code, declaration, registry, ledger or certificate was modified. |
| BASELINE | HEAD `bae59755` · branch `integration/recovery-001` · working tree 68 entries (67 pre-existing + this file) |
| CONSTITUTIONAL FRAME | Read against `UCKP-LAW-0001` (supreme), `UCOS-CAA-001` (authority alignment), `UCOS-MUTATION-GOVERNANCE-BOUNDARY-001` (mutation classes), `02-CANONICAL-OWNERSHIP-MATRIX.md` (concept ownership), `RTBD-001` (truth boundary), `GATE-PURITY-DETERMINATION.md` (mode) |
| REUSE CONSTRAINT | Binding: **no CREATE unless reuse is demonstrated impossible.** |
| DISPOSITION | No finding is a requirement. No gap is a task. No recommendation is authorized. Awaiting explicit authorization. |
| PRIOR ART | Extends `UCOS-OMEGA-INFINITY-UNIVERSAL-ASSIMILATION-FABRIC-DETERMINATION.md` and `UCOS-OMEGA-INFINITY-ASSIMILATION-INFINITE-INTELLIGENCE-INTEGRATION-DETERMINATION.md`. **Corrects four claims in the latter** — see §9.3. Supersedes nothing. |

---

## 1 — EXECUTIVE DETERMINATION

### 1.1 The seven primary questions, answered

| # | Question | Determination |
|---|---|---|
| 1 | Who owns universal assimilation? | **NO ONE.** `02-CANONICAL-OWNERSHIP-MATRIX.md` contains **no row for assimilation as a substrate**. Only two narrow rows exist: *Context Assimilation Gate* → `USIS-WAVE1`, and *Constitutional decision assimilation* → `CEP-002 Art. 28` / `UCDA-000001`. `platform/universal_assimilation/` appears in **no** authority register: it is absent from `UCOS-CAA-001`'s eleven `subordinate_instruments` and absent from `uccep-bindings.json`. It is governed only as mutation class `SOURCE` (rule R-07) — i.e. as *code*, never as an *authority*. **The declared universal substrate is constitutionally unowned.** |
| 2 | Who owns identity resolution? | **`UCKP-ART-05` — definitively, singularly, and already measured.** `CAA-INV-04` is literally named `EXACTLY_ONE_IDENTITY_AUTHORITY`. Two declared planes: `CONSTITUTIONAL_OBJECT` (`engine/uckp/identity.py`, role **SUPREME** — *"this IS UCKP-ART-05"*) and `REPOSITORY_OBJECT` (`00-BOOK/DATA/id-ledger.json`, role **PERSISTENCE** — *"the ONE such binding in this repository"*), joined by a declared total, pure, injective derivation `engine.uckp.alignment.repository_local_urn`. **This question is closed. My prior determination framed it as an open owner decision; that framing was wrong (§9.3).** |
| 3 | Who owns trust determination? | **Split three ways and unowned at the point of use.** Domain owner: `PHASE-008 SECURITY` (per `SECURITY-GOV-000` OUTPUT 6, *"the only new ownership"*) — which declares itself **non-enacting**: *"Security enacts nothing at the architecture layer"* (`USA-6`). Mechanism: `platform/foundation/trust.py` (cryptographic) plus `platform/security/**`, declared **frozen and reused-by-reference** at `PL-F2`. Representation: `trust` is a declared CEU form of existence (`("trust","TRST",…)`). **And `02-CANONICAL-OWNERSHIP-MATRIX.md` contains zero occurrences of the word "security" — verified, `grep -ci` returns 0.** No role holds a trust faculty. |
| 4 | Who owns intelligence contribution? | **Measurement is owned; contribution is not.** The matrix row for architectural intelligence declares **"no new owner"** and composes seven surfaces, with *"measured binding only"* at `00-MASTER/UAIE-000001` (`AUTHORITY = NONE`). `UCKP-ART-15` owns reasoning; `UKIP` owns knowledge admission; `UCKP-ART-14` owns the cycle. **Contribution is the edge between them and belongs to no one.** |
| 5 | Who owns evolution decisions? | **`CEP-009 AMENDMENT-EVOLUTION-CONSTITUTION`** (matrix: OWNED, extended by ADDENDUM B), with `UCKP-ART-14` owning the cycle, `UAUE-000001` measuring it (`AUTHORITY = NONE`), and `AUTH-INF-001 CR-INF-001` owning Ω∞ non-terminality. **But a cross-class evolution transaction has no authority** (`H-06` open item `AT-1`), and mutation classes 6–8 `grants_only_mutation_ownership` — expressly *no certification, ratification or freeze authority*. |
| 6 | Who owns continuous feedback loops? | **NO ONE.** No matrix row. `UNIVERSAL-ASSIMILATION-FEEDBACK-LOOP-DETERMINATION.md` names the loop and has no engine and no registered authority. `CONTINUATION` (stage 15) is owned by Article 14 *as a stage*; nothing executes the edge from it back to intake. |
| 7 | How does any new existence become part of Infinite Intelligence? | **By CEU registration — not by assimilation.** `engine/ceu/existence.py` is the admission surface that requires a non-optional `authority` argument; registered units enter the existence substrate; Article 15 reasoners read the registry and therefore reach them. **This path works today and the assimilation fabric is not on it.** The fabric bypasses CEU entirely, terminating in an `AssimilationRecord` that no existence authority recognises. |

### 1.2 The boundary determination

**The correct boundaries are almost entirely already declared. The defect is that the assimilation fabric sits outside every one of them.**

Measured: `UCOS-CAA-001` declares eight authority roles, eleven registered subordinate instruments, one supreme authority, and explicit non-competing resolutions for identity, identity-namespace, relationship graph, existence, lifecycle, category ownership and certification. `mutation-governance-boundary.json` declares nine mutation classes under ordered precedence `R-01…R-09` with a fail-closed `UNRESOLVED` terminal and the invariant *"No mutation class is claimed by two authorities as primary."* `engine/nucleus/authority.py` resolves ownership faculties from CEU data, fails closed on unregistered roles, and declares the faculty set open (`closed_set: False`).

This is a mature, measured, plural-but-non-competing authority architecture. Against it, the fabric is:

- **unregistered** as an authority instrument (not in CAA-001's eleven);
- **unowned** as a concept (no matrix row);
- **unbound** in identity (its `UCOS-USA*-<16hex>` ids match neither declared plane shape — the repository plane requires `^UCOS-[A-Z0-9]+-[0-9]{6}$`);
- **ungated** (no `uccep-bindings.json` entry, no `verify.sh` stage, no evidence key);
- **unfacultied** (no role holds a right to assimilate, because no such faculty is registered);
- **unsecured** (verified: zero references to trust, security, ownership, authentication or authorization anywhere in `platform/universal_assimilation/*.py`).

**Determination: the fabric is not a competing authority. It is an unregistered one — which is worse, because `UCOS-CAA-001`'s scan rule admits no third outcome.** Its own rule: any instrument whose `authority` matches no disclaiming prefix MUST appear in `subordinate_instruments` with a role and ≥1 article. *"There is no third outcome."* A Python package is not a `.json` instrument and so is not swept — the fabric escapes the scan by file type, not by conformance.

### 1.3 The single most consequential finding

**Security ownership is absent from the canonical ownership matrix, and the one document that does declare it declares an owner that cannot enforce.**

Three verified facts in combination:

1. `02-CANONICAL-OWNERSHIP-MATRIX.md` — **zero occurrences of "security."**
2. `SECURITY-GOV-000` OUTPUT 6 names `PHASE-008 SECURITY` as the security domain owner and *"the only new ownership."*
3. `SECURITY-001` `USA-6`: *"Security enacts nothing at the architecture layer"*; `§1`: security *"describes, classifies, evaluates, and attests… it never executes, never selects technology, and enforces only by reference to lower-layer mechanisms already frozen and certified."*

The lower-layer mechanism it must enforce by reference to is `platform/security/**`, declared **frozen at `PL-F2`** — and measured as a **TEST-ONLY orphan: zero production importers.** The only non-test mention anywhere is a Sphinx docstring cross-reference in `platform/blueprints/provenance.py:23`, which is not an import.

**So: the declared security owner may not enforce; the mechanism it would delegate to is frozen and inert; and the concept has no canonical home at all.** This is the answer to Phase 4's *"Where must security occur?"* — **the placement is undeclared, and no located authority currently has standing to declare it.**

### 1.4 What must not be done

Three tempting moves are constitutionally unavailable, and naming them is part of the determination:

| Tempting move | Forbidden by |
|---|---|
| Make `platform/universal_assimilation` the canonical assimilation authority by declaring it so | `CMG-000001` Art. LXXVII.2(a)/LXXVII.4 — CREATE is unavailable where a located owner exists for any part of the concept; two owners exist (`USIS-WAVE1`, `CEP-002 Art. 28`). The disposition space is REUSE / EXTEND / COMPOSE, and the matrix's own `Ω-E04` addendum records the identical situation resolved as **five REUSE, three EXTEND, zero CREATE** |
| Pick a canonical identity mint | Already decided. `CAA-INV-04`, two declared planes, one derivation. Selecting again would be *"a second APPEND-ONLY MINT"* — the declared `second_authority_test`, detected by sweeping for `category_seq` |
| Add a security gate inside the assimilation pipeline | `USA-6`/`USA-7`/`USL-010` — security is non-enacting and non-constitutive at the architecture layer; and `platform/security/**` is frozen at `PL-F2`. Enforcement requires a lower-layer mechanism and an authority that may enact, neither of which is presently located |

### 1.5 Reuse verdict

Across the twenty-one boundary elements analysed in §8: **EXISTS AND CONNECTED 6 · EXISTS BUT NOT CONNECTED 9 · EXISTS BUT NEEDS EXTENSION 5 · TRULY MISSING 1.**

The one truly missing element is **a registered faculty for admission** — the faculty vocabulary (`own-capability`, `select-units`, `observe`, `act`) contains nothing that grants the right to assimilate. Because that vocabulary is open by registration and declared `closed_set: False`, **admitting one is an EXTEND of CEU data, not a new engine.** So even the single missing element resolves without CREATE.

**This determination originates zero CREATE decisions.**

---

## 2 — CURRENT AUTHORITY MAP

### 2.1 The declared authority-level model

`UCOS-CAA-001` declares eight roles, verified as a **checked projection** of `engine/uckp/alignment.py::AUTHORITY_ROLES` (compared verbatim by `verify_binding`). Only one may hold authority.

| Role | Cardinality | may_hold_authority | Article |
|---|---|---|---|
| `SUPREME` | **EXACTLY_ONE** | **true** | `UCKP-ART-01` |
| `PROJECTION` | MANY | false | `ART-11` |
| `PERSISTENCE` | MANY | false | `ART-09` |
| `EXECUTION` | MANY | false | `ART-10` |
| `EVIDENCE` | MANY | false | `ART-16` |
| `OBSERVATION` | MANY | false | `ART-13` |
| `DERIVED` | MANY | false | `ART-15` |
| `ORTHOGONAL` | **FEW** | false | `ART-01` |

Supreme: `UCKP-LAW-0001`, home `engine/uckp/law.py`, object model `UCKO` (33 facets, `ART-02`), self-grounding at `engine/uckp/constitution.py::law_object`. *"A second instrument declaring role SUPREME is a competing root and is void under UCKP-ART-03."* The role set is **open by registration** (`ART-17`) — a new standing is one appended entry.

### 2.2 The seven authorities the directive names

#### A-1 · ASSIMILATION AUTHORITY

| Field | Value |
|---|---|
| Name | Universal assimilation |
| Current owner | **NONE for the substrate.** Two partial owners: `USIS-WAVE1` (Context Assimilation Gate), `CEP-002 Art. 28` + `UCDA-000001` (constitutional decision assimilation) |
| Implementation location | 14 surfaces. Principal: `platform/universal_assimilation/`, `00-MASTER/UAKOS-CLOSURE-008/assimilation_engine.py`, `engine/knowledge/ukip/assimilation.py`, `engine/uckp/assimilation.py`, `engine/constitution/assimilation.py` (`UCOS-RTAG-000001`) |
| Evidence | `02-CANONICAL-OWNERSHIP-MATRIX.md` lines 32, 46 (the only assimilation rows); absence from CAA-001 `subordinate_instruments`; absence from `uccep-bindings.json` |
| Authority level | **UNREGISTERED.** Governed as `SOURCE` (R-07) only |
| Dependencies | `platform/universal_truth` (15 importers), `platform/foundation`, `engine.foundation.obs.errors` |
| Conflicts | Two admission surfaces answer one question (framework vs closure engine) — `CMG-INV-02` territory. Matrix line 43 records the *Constitutional Reuse Gate* as **WEAK / TO FORMALIZE** |
| Unknowns | Which surface is canonical. Whether the fabric is intended as an instrument at all |

#### A-2 · IDENTITY AUTHORITY

| Field | Value |
|---|---|
| Name | Universal Identity |
| Current owner | **`UCKP-ART-05`. One authority, two planes.** |
| Implementation location | `engine/uckp/identity.py` (SUPREME); `00-BOOK/DATA/id-ledger.json` (PERSISTENCE, *"the ONE such binding"*); derivation `engine.uckp.alignment.repository_local_urn` |
| Evidence | `identity_authority_resolution`; `CAA-INV-04 EXACTLY_ONE_IDENTITY_AUTHORITY`; `identity_namespace_resolution` (`MULTIPLE_INDEPENDENT_BOUNDED_NAMESPACES`); matrix identity rows (AIF · ENG-001 · UMB-003 · UMB-004 · UIS-001, all REUSE) |
| Authority level | **SUPREME** (constitutional plane) / **PERSISTENCE** (repository plane) |
| Dependencies | `engine/uckp/canonical.py` Layer-Zero primitive, guarded by `UCKP-INV-03` |
| Conflicts | **None declared.** Two live emitted forms match neither declared plane shape (§4.3) |
| Unknowns | Whether `deterministic_id()` and the fabric's ids are intended as a third plane or are unbound by oversight |

#### A-3 · KNOWLEDGE AUTHORITY

| Field | Value |
|---|---|
| Name | Knowledge Once |
| Current owner | `RA-003` KNOWLEDGE-ONCE-CERTIFICATION + closure engine + `CEP-001`. Decision store: `knowledge/decisions.json`. Capability register: `engine/knowledge/capability.py`. Reuse determination: `engine/knowledge/integration/reuse.py::ReuseEngine` |
| Implementation location | `engine/knowledge/` (22 prod importers), `engine/knowledge/ukip/`, `engine/knowledge/store.py` |
| Evidence | Matrix knowledge rows; `UKIP-LAW-001…011`; `identity_namespace_resolution` names `engine/knowledge/store.py` as the knowledge-identity authority |
| Authority level | OWNED (concept) / AUTHORITY (certification surfaces #4, #5) |
| Dependencies | `engine/uckp` (Layer Zero) |
| Conflicts | None declared |
| Unknowns | `ISD-CE-09` / `ISD-G-01` — `KnowledgeCapability` is a closed 11-member enum with `closing_invariant: "NONE DECLARED IN CODE"`. The one live undisclosed-intent closure, sitting in the knowledge plane |

#### A-4 · INTELLIGENCE AUTHORITY

| Field | Value |
|---|---|
| Name | Architectural intelligence / architectural reasoning over Repository Truth |
| Current owner | **"no new owner"** — composed of seven surfaces; *measured binding only* at `00-MASTER/UAIE-000001` |
| Implementation location | `engine/uckp/intelligence.py` (Art. 15, 13 reasoners), `engine/graph/architecture`, `engine/graph` + `platform/repository_intelligence`, `engine/knowledge/integration`, `platform/measurement`, `platform/validation_intelligence`, `UEI-000001`, `UCOS-UAR-001` |
| Evidence | Matrix intelligence row (explicit *"no new owner"*, `AUTHORITY = NONE` at UAIE) |
| Authority level | **DERIVED / measured.** No constitutive authority |
| Dependencies | `engine/uckp` registry population |
| Conflicts | `CONFLICT-06` — ten validation authorities, no reconciling verdict |
| Unknowns | Who owns *contribution* to intelligence, as distinct from measurement of it. Unanswered anywhere |

#### A-5 · EVOLUTION AUTHORITY

| Field | Value |
|---|---|
| Name | Evolution / amendment / extension |
| Current owner | `CEP-009 AMENDMENT-EVOLUTION-CONSTITUTION` (OWNED, extended by ADDENDUM B); `EVOLUTION-001` (post-baseline history); `AUTH-INF-001 CR-INF-001` (Ω∞ non-terminality) |
| Implementation location | `engine/uckp/evolution.py` (Art. 14 — the stage authority); `engine/uaue/` (20 modules, measurement); `UAUE-EVOLUTION-HISTORY.json` (~1.3 MB, append-only, 52 cycles / 780 records / 8,580 findings, `terminated: false`) |
| Evidence | Matrix evolution rows; `AUE-BND-01…10`; `engine/uaue/__init__.py` — the stage set is *read from* Article 14, never restated |
| Authority level | OWNED (concept) / `AUTHORITY = NONE` (measurement) |
| Dependencies | `engine/uckp/evolution.py` (sole stage authority) |
| Conflicts | **Cross-class evolution transaction has no authority** — `H-06 AT-1` OPEN. Mutation classes 6–8 `grants_only_mutation_ownership` |
| Unknowns | Whether `EvolutionLedger` may be persisted (`F-3`); population 74 vs 88 (`P-1`) |

#### A-6 · CERTIFICATION AUTHORITY

| Field | Value |
|---|---|
| Name | Certification gate |
| Current owner | Concept: `CEP-005` + CERTIFICATION-REGISTRY. Surfaces: **`MULTIPLE_INDEPENDENT_AUTHORITIES` — 14 registered (13 AUTHORITY + 1 PROJECTION)** |
| Implementation location | `engine/certification/` (178 prod importers), `engine/universal_certification/`, `platform/certification/` (the one PROJECTION), `engine/knowledge/certification.py`, `engine/knowledge/ukip/certification.py`, `platform/universal_assurance/certification.py`, RIB, AEE, CMG, Phase 8, Phase 9, UCEF, UMB-017, `platform/repository_intelligence/certification.py` |
| Evidence | `certification_authority_resolution`; six declared principles incl. *"Coexistence does not represent duplication"* and *"Evidence integrity rules remain globally governed"* |
| Authority level | AUTHORITY ×13, PROJECTION ×1 |
| Dependencies | `00-BOOK/DATA/evidence-universe.json` `CERTIFICATION_EVIDENCE_CLASS` — `DEBUG`/`IMPROVEMENT` evidence may never influence any certification, anywhere |
| Conflicts | Surface #2 `engine/universal_certification` is a **registered AUTHORITY whose four importers are all themselves orphans** (§9.1 C-7) |
| Unknowns | Whether #2 is a dormant duplicate or a dormant generalization — undecided in the corpus |

#### A-7 · SECURITY AUTHORITY

| Field | Value |
|---|---|
| Name | Security domain architecture (trust / authority / policy / control / assurance) |
| Current owner | `PHASE-008 SECURITY` — *"the only new ownership"* per `SECURITY-GOV-000` OUTPUT 6 |
| Implementation location | **None owned.** `14-SECURITY/` is 5 documents, 0 code. `platform/security/**` is named as a **frozen, by-reference, lower-layer** dependency (`PL-F2`), not as the implementation |
| Evidence | `SECURITY-001` front matter (`CONSTITUENT / GOVERNANCE / RATIFICATION / EC-1 AUTHORITY = NONE`), `USA-1…7`, `USL-001…006`; `SECURITY-GOV-000` OUTPUT 6/7 |
| Authority level | **Supreme within the `SECURITY-*` chain only** (`SL-0`); subordinate to the frozen constitutional corpus, Technology Constitution, `ENG-000`, `AUTH-INF-001`; **explicitly non-enacting and non-constitutive** |
| Dependencies | Downward-only acyclic chain `EL-1 → RL-F2 → PL-F2 → DF-2 → SF-2 → AF-3 → IF-3 → SECURITY` |
| Conflicts | **`02-CANONICAL-OWNERSHIP-MATRIX.md` has zero occurrences of "security"** (verified). The concept has no canonical home |
| Unknowns | **Where security must occur.** No pre-admission / during / pre-promotion boundary is declared anywhere in `14-SECURITY/`. Grep-confirmed absent |

### 2.3 The mutation-authority map — who may mutate what

`UCOS-MUTATION-GOVERNANCE-BOUNDARY-001` (role `EXECUTION`, relation `PROJECTION`, under `ART-10`/`ART-16`). Determination: **Option B — source mutations are outside the constitutional mutation gateway**, proved structurally (`engine/constitution/gateway.py` and `state.py` never touch `pathlib`, `open(`, `read_text`, `write_text` or git).

| # | Mutation class | Primary authority |
|---|---|---|
| 0 | `CONSTITUTIONAL_TRUTH` | `UCOS-CMG-EXEC-000001` (`engine/constitution/gateway.py`) |
| 1 | `SOURCE` | pre-commit → `verify.sh` → RIB → AEE → Phase 8 → Phase 9 |
| 2 | `GENERATED_ARTIFACT` | `UCOS-GENERATED-ARTIFACT-REGISTRY-001` → producer → Phase 8/9 |
| 3 | `EXCLUSION` | `UCOS-EXCLUSION-REGISTER-001` → RIB GATE-12 |
| 4 | `REPOSITORY_STATE` | `UCOS-RIB-001` GATE-02 / GATE-12 |
| 5 | `CORPUS_REGISTRATION` | `REG-AUTO-001` → `00-BOOK/tools/register.sh` |
| 6 | `GOVERNED_DECLARATION` | *owner-parameterised* — the owning programme the artifact declares |
| 7 | `AUTHORED_DOCUMENT` | *owner-parameterised* — the artifact's own Authority field |
| 8 | `GOVERNED_ANALYSIS` | *owner-parameterised* — Authority field → Repository Intelligence |

Classification is **ordered precedence `R-01…R-09`**, deterministic, total, unique, with terminal class `UNRESOLVED` that **fails closed** and *"is not a mutation class and confers no authority."* Nine invariants, including *"No mutation class is claimed by two authorities as primary"* and *"Every tracked artifact resolves to exactly one mutation class."*

Two limits directly load-bearing for any future assimilation binding:

- Classes 6–8 carry `grants_only_mutation_ownership`: *"It grants no certification authority, no ratification authority and no freeze authority. CEP-009 I.1 reserves those."*
- `verify.sh` *"observes … and may never author"* — **a verification path that allocates a Universal ID is a boundary violation regardless of flag.** This is the codified response to the recorded incident in which a drift check minted 140 permanent identifiers.

### 2.4 The faculty map — who may act

`engine/nucleus/authority.py` (`UCOS-NUC-001` Part 11) is an **adapter, not a third authority**: it exists because `StructuralRole.may_own_capability` once hardcoded `return self is StructuralRole.NUCLEUS`, making source code an ownership authority. Direction: *"Legacy values derive from CEU. Never the reverse."* `holds()` **fails closed** — *"a role the substrate does not register holds nothing."* Emits `authority_digest`, `closed_set: False`, `upper_limit: None`.

Faculties, held as CEU data in `engine/ceu/catalog.py::SEED_CLASSIFICATIONS`:

| Faculty | Held by |
|---|---|
| `own-capability` | `nucleus` (and specializations `micro-nucleus`, `nano-nucleus`, `service`, `engine`) |
| `select-units` | `composition` (and `platform`) |
| `observe`, `act` | `agent` |
| — | `layer`, `domain` hold **nothing** — *"Owns nothing, and is optional (CEU-005)"* |

**There is no faculty for admission, assimilation, trust or evolution.** `trust` exists as a *form of existence* (`("trust","TRST","Trust",("governance","evidence"))`) but not as a *faculty*. Consequence: **no role can be said to hold the right to assimilate, and no role can be said to hold the right to determine trust.** The vocabulary is open, so this is an absence, not a prohibition.

---

## 3 — ASSIMILATION BOUNDARY MAP

### 3.1 Entry → Validation → Governance → Evolution, measured

```
ENTRY                     VALIDATION            GOVERNANCE              EVOLUTION
─────                     ──────────            ──────────              ─────────
documents  ─┐
code       ─┤ platform/universal_assimilation
data       ─┤   7 doc adapters ──▶ TruthPolicy ──▶ zone/authority ──▶ AssimilationReport ──▶ ✗
external   ─┘   (no adapter for API/UI/infra/runtime/technology)          coverage number

knowledge  ──▶ engine/knowledge/ukip  ──▶ classify/screen ──▶ canonical home ──▶ knowledge/*.json ──▶ ✗
                7 stages, providers        (total, no          REGISTERED /
                                            unknown bucket)     CORROBORATED

artifacts  ──▶ engine/uckp/assimilation ──▶ verify_invertible ──▶ UCKO registry ──▶ Art.15 reasoners ──▶ ✓
                Art.19 lossless             require_lossless

creation   ──▶ engine/constitution/assimilation (UCOS-RTAG-000001)
                4 searches must ALL return empty ──▶ require_creatable() ──▶ ✓ gated

existence  ──▶ engine/ceu/existence.relate(authority=…)  ──▶ existence substrate ──▶ Art.15 ──▶ ✓
                ★ THE ONLY SURFACE REQUIRING NON-OPTIONAL AUTHORITY

corpus     ──▶ 00-MASTER/UAKOS-CLOSURE-008 ──▶ 6 states, 16-dim superiority ──▶ 6 actions ──▶ ✓ CI-gated
                (the only CI-gated admission path)
```

**Determination: three of six paths reach the intelligence plane. The two "universal" paths do not.**

### 3.2 Duplicate admission paths

| Duplication | Surfaces | Standing |
|---|---|---|
| Generic assimilation | `platform/universal_assimilation` (general, not CI-gated) vs `UAKOS-CLOSURE-008` (specific, CI-gated) | Two answers to one question. `CMG-INV-02` no-parallel-authority applies in principle; neither is a registered instrument, so neither is measured by `CAA-INV-03` |
| `AssimilationReport` | Two identically-named classes: `platform/universal_assimilation/contracts.py` and `engine/knowledge/ukip/assimilation.py` | Name collision across planes; no crosswalk |
| Ownership answer | `TruthClassification.authority or zone_id` (fabric) vs `OwnershipDeterminationEngine` (constitutional) | Two independent answers; `OWN-REQ-002` exists to prevent exactly this |
| Duplication detection | ~15 mechanisms, none cross-visible | Correct locally; no reconciling projection |

### 3.3 Missing security boundaries

Verified by grep across `platform/universal_assimilation/*.py` for `trust|security|Ownership|authenticat|authoriz` — **zero matches.** No authentication, no authorization, no signature verification, no provenance verification, no secret scan, no integrity comparison. Digests are computed **from** the submitted payload and become its identity, so there is no expected value against which tampering could be detected.

### 3.4 Isolated capabilities and orphan engines

Census method: for each top-level package, count importers outside its own package excluding `/tests/` and `test_`.

| Category | Packages |
|---|---|
| **HARD ORPHAN** (0 prod, 0 test, no entry point) | `engine/uicm` (10 modules), `intelligence/die`, `platform/project-management` |
| **TEST-ONLY orphan** (no entry point) | `engine/infinite_scope`, `engine/lineage`, `engine/root_ontology`, `engine/object_birth`, `engine/registry_coverage`, `engine/uaue`, `engine/factory`, `platform/security`, `platform/universal_assurance`, `platform/universal_portal`, `platform/runtime_operations`, `platform/runtime_platform`, `platform/artifact_explorer`, `platform/execution_dashboard`, `platform/providers`, `platform/universal_master_plan` |
| **CLI-ONLY** | `engine/execution_environment`, `engine/verification_intelligence`, `engine/verification_impact`, `intelligence/publication`, `intelligence/realization`, `platform/universal_generator`, `platform/universal_pipeline`, `platform/commercial_intelligence` |
| **TRANSITIVE ORPHAN** (importers exist, all dead) | `engine/universal_certification` (4 importers: `engine/uicm/certification.py` + 3 in `platform/universal_assurance/` — all orphans), `platform/universal_project_state`, `platform/universal_validation` (3 importers, all in `universal_assurance`) |

Four orphan **clusters** — this is the part a per-package count hides:

1. **Certification/assurance** — `platform/universal_assurance` (0 prod / 15 test) and `engine/uicm` (0/0) are the only importers of `engine/universal_certification`. A registered certification AUTHORITY with no reachable consumer.
2. **Portal shell** — `platform/universal_portal/service.py` tops a large tree and has 0 importers and no entry point. It is the sole prod importer of `platform/administration`, `coverage`, `validation`, `portal`. A large slice of the platform's non-zero counts is rooted in an orphan.
3. **Verification** — `engine/verification_intelligence` (0 prod, `__main__` only) → `engine/verification_impact` (1). Reachable only via `python -m`.
4. **Control plane** — `platform/universal_master_plan` (0/1) is the only importer of `platform/universal_project_state`.

Two findings deserve separate emphasis:

- **`engine/uckp` is the largest inbound hub (53 prod importers) and many of its consumers are orphans** — `object_birth/birth.py`, `lineage/projection.py`, `registry_coverage/matrix.py`, `root_ontology/contract.py`, all ten `uaue/*` modules, `uicm/model.py`. Dependency arrows point *into* the live core from inert leaves, which is why the core looks healthy while the leaves are dead.
- **`intelligence/die/imports.py` — the repository's own dead-code and reachability analyzer — is itself a hard orphan and currently unimportable:** no `__init__.py`, and line 26 does `from .evidence_bridge import DiscoveryEvidence` where `evidence_bridge` does not exist anywhere in the tree. **The measurement that would have found all of the above cannot run.**

### 3.5 Note on the fabric's isolation, stated precisely

`platform/universal_assimilation` has **four** production importers, all inside `platform/`: `universal_foundation/{bootstrap,service}.py` and `universal_measurement/{contracts,policies}.py`. It is published as `ucos-assimilate`. **It is therefore not an orphan.** The accurate statement is narrower and still decisive: **zero importers from `engine/` or `intelligence/`, and it imports `engine/` only for an exception type (`cli.py:33`).** It is connected within its own cluster and disconnected from the constitutional planes.

---

## 4 — IDENTITY AUTHORITY ANALYSIS

### 4.1 The correct constitutional ownership model — already declared

The directive asks for the correct model, not a selection. **The correct model exists and is measured.**

```
UCKP-ART-05 · Universal Identity  ── one authority ──▶ "Every other identity mechanism
                                                        in the repository is a persistence
                                                        or projection binding of it."
        │
        ├── PLANE 1 · CONSTITUTIONAL_OBJECT      role: SUPREME — "this IS UCKP-ART-05"
        │     home:  engine/uckp/identity.py
        │     shape: urn:ucos:ucko:<namespace>:<local_name>
        │     props: pure · total · clock-free · storage-free · repository-free
        │
        └── PLANE 2 · REPOSITORY_OBJECT          role: PERSISTENCE — "the ONE such binding"
              home:  00-BOOK/DATA/id-ledger.json
              shape: UCOS-<CATEGORY>-<NNNNNN>
              maps:  by_path · by_object · by_observation
              props: append-only · first_seen frozen · never reissued · never renumbered

        DERIVATION (declared, TOTAL · PURE · INJECTIVE · verbatim)
              engine.uckp.alignment.repository_local_urn
              ^UCOS-[A-Z0-9]+-[0-9]{6}$  ──▶  urn:ucos:ucko:ucos-repository:<UCOS-ID>
              e.g. UCOS-ENGINE-000496 → urn:ucos:ucko:ucos-repository:UCOS-ENGINE-000496
              "any reshaping would be a re-mint wearing a projection's clothes"
```

Alongside it, `identity_namespace_resolution` declares `MULTIPLE_INDEPENDENT_BOUNDED_NAMESPACES` — non-competing because bounded, sharing only the Layer-Zero primitive `engine/uckp/canonical.py` (guarded by `UCKP-INV-03`):

| Pattern | Owner |
|---|---|
| `urn:ucos:ucko:*` | `engine/uckp/identity.py` |
| `UCKO-<KIND>-<NNNN>` | `engine/knowledge/seed.py` / `capability.py` |
| `UKID-<digest12>` | `engine/knowledge/ukip/contracts.py` |

### 4.2 The measured guarantee

`CAA-INV-04 EXACTLY_ONE_IDENTITY_AUTHORITY`, measured in `uga_engine.py`, fails on: malformed maps, unshaped identities, **identity collisions**, **rival mints** (whole-tree sweep for a second `category_seq` — exactly one file holds it), a missing mint home, an unknown article, or zero identities (*"the derivation is UNMEASURED"*). It recomputes `repository_local_urn` over every id in all three maps — **injectivity is a count, not a claim.** `ids_preserved: ALL`.

### 4.3 The actual defect — unbound emitted forms, not competing authorities

The declared repository shape is `^UCOS-[A-Z0-9]+-[0-9]{6}$` — **six decimal digits.** Two live emitted forms do not satisfy it:

| Emitted form | Producer | Matches Plane 1? | Matches Plane 2? |
|---|---|---|---|
| `UCOS-<CODE>-<12 hex>` | `engine/registry/universal/identity.py::deterministic_id()` | No | **No** — 12 hex ≠ 6 digits |
| `UCOS-USAS/USAU/USAR/USAP-<16 hex>` | `platform/universal_assimilation/contracts.py` | No | **No** — 16 hex ≠ 6 digits |

**Determination: these are not rival authorities. They are unregistered forms outside both declared planes.** They are not mints (no `category_seq`, no allocation, no append-only ledger), so `CAA-INV-04`'s rival-mint test correctly does not fire. They are content-addressed derivations — which is the *right* technique — that simply have no declared plane to belong to.

The consequence is precise: `CAA-INV-04` measures the **declared** identity population (the three `id-ledger.json` maps). It does not sweep the **emitted** population. So the invariant is satisfied and unbound identities coexist with it. This is a scope property of the measurement, not a violation of it — and it is exactly the gap through which an assimilated object becomes unresolvable.

### 4.4 Object → Identity → Lineage → Relationship → Evolution History

| Link | Owner | Fabric participation |
|---|---|---|
| Object | `UCKO`, `engine/uckp/ucko.py`, 33 facets, `ART-02`; `CAA-INV-07` forbids a rival object model | **None.** An `AssimilationUnit` is not a UCKO |
| Identity | `ART-05`, two planes | **Unbound** (§4.3) |
| Lineage | `engine/lineage/` — 4 families + events, 12,899 edges, 44/44 relations classified, 0 invented, zero persistence, digest `9f7a4b87d827b986…` | **None.** Reads six governed sources; `AssimilationRecord` is not among them |
| Relationship | `ART-07`, model owner `engine/uckp/graph.py`; 6 declared kind bindings; `CAA-INV-05` requires every *emitted* kind be bound to a class | **None.** The fabric emits no edges |
| Evolution history | `ART-14` `EvolutionLedger`; `UAUE-EVOLUTION-HISTORY.json` | **None.** No append |

**Determination: the fabric participates in zero of the five links.** An assimilated source has no constitutional object, no bound identity, no lineage, no relationship and no evolution record. It exists only as a row in a coverage measurement.

Note the asymmetry with `CAA-INV-05`: for relationships, the invariant checks **emitted** kinds against declared classes and fails on *"a kind bound in the register but emitted by nothing"* and on an emitted kind bound to nothing — a both-directions test. **The same both-directions discipline applied to identity would have caught §4.3.** That is the single most useful structural observation in this section, and the mechanism to do it already exists one section away in the same file.

---

## 5 — SECURITY TRUST BOUNDARY ANALYSIS

### 5.1 Where must security occur? — UNDECLARED

Grep-confirmed: `14-SECURITY/SECURITY-001` and `SECURITY-GOV-000` contain **no** pre-admission, during-assimilation, or pre-promotion placement boundary. What they declare instead:

- **A layering boundary** (OUTPUT 7): downward-only, acyclic `EL-1 → RL-F2 → PL-F2 → DF-2 → SF-2 → AF-3 → IF-3 → SECURITY(PHASE-008)`. Prohibited: upward, forward or cyclic dependency; redefinition of infrastructure/platform/application security; new primitive, authority, registry, identifier or lifecycle; concrete technology binding.
- **A modality boundary** (`§1`, `USA-6`, `USA-7`, `USL-010`): security *describes, classifies, evaluates and attests*; it *never executes, never selects technology*, and *enforces only by reference to lower-layer mechanisms already frozen and certified*; it *mints no new primitive, authority, registry, identifier scheme or lifecycle*.

**Determination: temporal placement of security acts is undeclared, and the declared owner is constitutionally barred from enacting it.** Phase 4's question cannot be answered from Repository Truth as it stands. It is a gap, and it is the correct gap to surface.

### 5.2 The four-way split

| Aspect | Owner | Standing |
|---|---|---|
| Domain architecture | `PHASE-008 SECURITY` | *"the only new ownership"* — non-enacting, non-constitutive |
| Mechanism (crypto) | `platform/foundation/trust.py` | `TrustEngine`, HMAC keys, delegation chains, revocation, notary |
| Mechanism (composition) | `platform/security/**` | Declared **FROZEN** at `PL-F2`, reused by reference — and a **TEST-ONLY orphan** |
| Representation | `engine/ceu/catalog.py` | `trust` is a declared form of existence (`TRST`, classes `governance`+`evidence`) |
| Canonical home | **NONE** | Matrix contains zero occurrences of "security" |
| Faculty | **NONE** | No trust faculty in the open vocabulary |

### 5.3 Trust mechanism — measured, and a prior claim corrected

`platform/foundation/trust.py::require_trusted` is defined at `:539` and delegates to `verify_chain`. **Six call sites, not one:** five in-module invariant guards — `delegate()` `:414`, `rotate()` `:442`, `notarize()` `:460`, `revoke()` `:480` (conditional on `witness_key_id != key_id`) — plus exactly one external caller, `platform/foundation/admission.py:398`, inside authority migration.

**Correction:** my prior determination repeated the earlier claim of a single caller. It is a load-bearing internal guard, not a stub. The accurate finding is unchanged in consequence and narrower in fact: **trust is enforced on authority migration and on its own key lifecycle, and on nothing else. No content-admission path consults it.**

### 5.4 Supply-chain boundary — the precise finding

`platform/universal_provider/discovery.py::resolve_entry_point` is *"the whole bridge from data to a live provider."* It splits `"package.module:attribute"` from a JSON descriptor, calls `importlib.import_module(module_name)`, resolves the attribute, and calls it with the descriptor and config.

It **fails closed** on absent, malformed, unimportable and non-callable entry points, and isolates construction faults as typed errors (`PC-07` / `PC-09`). That is correct engineering and should be credited.

What it does **not** do — verified by grep across `platform/universal_provider/*.py` for `allowlist|allow_list|signature|verify_chain|require_trusted|trusted` (only hit: a comment): **no allowlist, no signature verification, no trust-chain check, no sandbox.** The descriptor carries a `content_hash()`, which gives **integrity of the descriptor** and no **authenticity of the module it names**.

The sharpest point is a claim boundary inside the module itself. Line 49 comments that descriptors are not resolved during discovery, *"which is what keeps discovery safe over untrusted catalogs."* **That claim is true of discovery and is not true of resolution.** Discovery is safe because it does not import; `resolve_entry_point` is the trust boundary, and it has no trust check. **Determination: the trust boundary is correctly located in exactly one function and is unguarded at that location.** That is a far better position than a diffuse problem — it is one function, and the mechanism it would call (`require_trusted`) already exists in the same package tree.

### 5.5 The eight aspects Phase 4 names

| Aspect | State |
|---|---|
| Integrity validation | **EXISTS, self-referential on admission.** `payload_digest()` computes identity *from* the payload; `content_sha256` over 33 facets is the UCKO tamper check; `ProvenanceChain.verify()` detects insertion/reorder/deletion **without the original** — the strongest integrity mechanism in the repository, and it is in the knowledge plane, not the fabric |
| Provenance | **EXISTS (knowledge plane), ABSENT (fabric).** `ukip/provenance.py` hash-chains each step to its predecessor |
| Source trust | **ABSENT.** No trust scoring anywhere; trust is cryptographic only |
| Authentication | **ABSENT on every admission path** |
| Authorization | **EXISTS, unwired.** `platform/identity/policy.py` default-deny `PolicyEngine` (`"no-grant"`); instantiated in one non-test place, never on an admission path |
| Malicious input handling | **ABSENT.** `scan_for_secret()` exists in an orphan package; no admission path calls it |
| Dependency safety | **PARTIAL.** `resolve_entry_point` fails closed on resolution errors; no provenance or signature check (§5.4) |
| Supply-chain risk | **UNGUARDED AT ONE LOCATED FUNCTION** (§5.4) |

### 5.6 Determination on the boundary

Reasoning from what *is* declared rather than inventing a placement:

- `engine/constitution/assimilation.py` already places a **pre-creation** boundary: `require_creatable()` demands four searches return empty *before* creation is permitted. Precedent exists for gating **before** admission.
- `engine/ceu/existence.py::relate()` already requires a **non-optional `authority`** argument. Precedent exists for requiring authority **at** admission.
- `evidence-universe.json` `CERTIFICATION_EVIDENCE_CLASS` already bars `DEBUG`/`IMPROVEMENT` evidence from influencing certification **anywhere**. Precedent exists for a **global** integrity rule at promotion.

**Determination: the three placements the directive asks about each already have a structural precedent in Repository Truth — pre-admission (`require_creatable`), at-admission (`relate(authority=…)`), and pre-promotion (evidence class). What is missing is not a model but an authority with standing to bind them to the assimilation path, since `PHASE-008 SECURITY` may not enact and `platform/security/**` is frozen.**

---

## 6 — INTELLIGENCE CONTRIBUTION MODEL

### 6.1 Assimilation → Knowledge → Reasoning → Learning → Discovery → Evolution

| Link | Owner | Mechanism | State |
|---|---|---|---|
| Assimilation → Knowledge Representation | `UKIP` / `RA-003` | `ukip/assimilation.py` 7 stages → canonical home; classification **total**, no unknown bucket (`UKIP-LAW-005`) | **EXISTS, entered by providers only** |
| Knowledge Representation → Reasoning | `UCKP-ART-15` | 13 reasoners over the registry; each reasoner is itself a UCKO; `AUTHORISING_ARTICLES["intelligence"]="UCKP-ART-15"` | **EXISTS AND CONNECTED** |
| Reasoning → Learning | `UCKP-ART-14` `LEARN` | Re-derivation, not parameter fitting; `cost_model.py` is the one closed loop | **EXISTS, one instance** |
| Learning → Discovery | `engine/discovery/` | 8 dimensions as pure functions over read-only registry views; **no regex, no glob, no filesystem walk** — a shortfall is a referential gap in the substrate, never a discovery limit | **EXISTS.** One prod importer, and it is *function-local* (`engine/uckp/assimilation.py:650`, deliberately) |
| Discovery → Evolution | `CEP-009` / `ART-14` | `engine/uaue/discovery.py`; the **declared unknown probe** (no class, no registry, no owner) traverses the same code path as a known gap | **EXISTS** |
| Fabric → any of the above | **NO OWNER** | — | **ABSENT** |

### 6.2 How new existence actually reaches Infinite Intelligence today

```
new thing ──▶ engine/ceu/existence.py  .register() / .relate(authority=…)
                       │                  ★ non-optional authority
                       ▼
              existence substrate  (CEU: 154 units, 51 forms)
                       │
                       ▼
              engine/uckp/registry.py  (193 completeness objects)
                       │
                       ▼
              engine/uckp/intelligence.py  13 reasoners read the registry
                       │
                       ▼
              INFINITE INTELLIGENCE  ✓ reached
```

`existence_resolution` declares **four non-competing existence authorities**: `UCKP-COMPLETENESS-REGISTRY` (193 objects), `UGA-EXISTENCE-REGISTRY` (5,789), `CEU-EXISTENCE-SUBSTRATE` (154 units / 51 forms), `REPOSITORY-INTELLIGENCE`.

**Determination — the answer to primary question 7: new existence becomes part of Infinite Intelligence by being *registered with a named authority*, not by being *assimilated*. The path is real, gated, and working. The assimilation fabric is not on it.**

This reframes the integration problem correctly. The fabric does not need to be taught how to contribute to intelligence. **It needs to terminate at the CEU registration surface that already requires exactly what is missing from it: a named authority.** The one admission surface in the repository that demands authority is the one the fabric does not use.

### 6.3 Required future boundaries

| Boundary | Why | Existing precedent |
|---|---|---|
| Fabric output must present a named authority | `relate()` already requires it; unauthored existence is what `CAA-INV-02` forbids for instruments | `engine/ceu/existence.py:951` |
| Fabric output must be a UCKO or declare its reduction | `CAA-INV-07` forbids a rival object model; `engine/root_ontology/` shows the reduction pattern (*"if a thirty-fourth facet is ever admitted, this gate closes until the reduction covers it"*) | `UCPA-000001` |
| Emitted identities must bind to a declared plane | §4.3; `CAA-INV-05` shows the both-directions test that would enforce it | `identity_authority_resolution` + `repository_local_urn` |
| Contribution must be measurable, not asserted | House standard: every claim carries a measurement | `AssimilationCoveragePolicy` (precedence 600, blocking) |

---

## 7 — EVOLUTION LOOP ANALYSIS

### 7.1 The directive's loop against Article 14

| Directive | Article 14 stage | # | Owner | Edge |
|---|---|---|---|---|
| Observe | `OBSERVE` | 1 | `ART-14` | ✓ |
| Understand | `OBSERVE` / `engine/uaue/understanding.py` | 1 | `ART-14` / UAUE | ✓ |
| Assimilate | `KNOWLEDGE_ASSIMILATION` | 14 | **unowned as substrate** | **✗** |
| Reason | `REASON` | 3 | `ART-15` | ✓ |
| Generate | `IMPLEMENTATION` | 8 | `CEP-009` | ✓ |
| Validate | `VALIDATION` | 9 | 10 authorities, no reconciling verdict (`CONFLICT-06`) | ⚠ |
| Certify | `CERTIFICATION` | 12 | 14 declared surfaces | ✓ |
| Evolve | `STATE_TRANSITION` | 13 | `CEP-009` / `ART-14` | ✓ |
| Observe Again | `CONTINUATION` → wrap | 15 → 1 | `ART-14` owns the stage; **nothing executes the edge** | **✗** |

Intervening stages the directive omits but Article 14 enforces: `LEARN` (2), `SIMULATE` (4), `IMPACT_ANALYSIS` (5), `DEPENDENCY_ANALYSIS` (6), `AUTHORITY_RESOLUTION` (7), `REPLAY` (11).

**`AUTHORITY_RESOLUTION` at stage 7 is the finding that matters most here: the constitutional cycle already places authority resolution as a mandatory stage of every evolution.** An assimilation pathway that never resolves authority is not merely under-secured — it is skipping a legislated stage.

### 7.2 Non-termination

`is_terminal()` returns `False` unconditionally (`evolution.py:88-91`); `next_stage()` wraps modulo `CYCLE_LENGTH`; the ledger is append-only and the first record must be stage 1, cycle 0. The closed 15-member enum is **published as an open vocabulary** (`evolution.py:115`) so it is measured against `INV-14` — *"instead of being the one constitutional vocabulary nothing probed."*

### 7.3 Missing loop edges

| Edge | State | Owner who would decide |
|---|---|---|
| Fabric → stage 14 | Missing. Blocked on `F-3` (`EvolutionLedger` never persisted) and on the `GOVERNED_EVOLUTION_STATE` classification question already deferred | `ART-14` (read-only authority) + `CEP-009` |
| Stage 15 → stage 1 re-intake | Missing in execution. `engine/constitution/stages.py::begin_next_cycle` **already asserts the required property**: `record.next_input().digest() == ctx.population.digest()` | `CEP-009` |
| Cross-class transaction | Object specified, never created; `AT-1` OPEN — *no declared authority owns a cross-class transaction boundary* | `H-06` owner |
| Replay provability | `GP-4`: `--render` declared and never read in 3 engines, so `*-replay` ≡ `*-gate`. *A gate that writes before it compares can only compare a file against itself* | `H-06` / `CR-09` |

### 7.4 Evidence

Evidence key: `sha256(EVIDENCE_VERSION "2.0" ‖ stage_id ‖ stage_label ‖ "argc:"len ‖ ordered argv ‖ sorted reuse-input digests)`. The contract is the source text of `verify.sh`, tokenised with `shlex`; `"$PY"` stays literal so keys are machine-independent. The `contract` parameter is **keyword-only and non-defaultable** — implementation deliberately departed from the architecture's `extra=()` seam because an optional key component reintroduces the defect it fixes. Every refusal returns `None` and causes the stage to **run** (fail wide, `UVI-L-07`).

**The fabric has no `verify.sh` stage, therefore no evidence key, therefore no reuse and no evidence that assimilation ever ran.**

---

## 8 — CAPABILITY REUSE MATRIX

| # | Boundary element | Classification | Located surface | Note |
|---|---|---|---|---|
| 1 | Identity authority model | **EXISTS AND CONNECTED** | `identity_authority_resolution` + `CAA-INV-04` | Closed question |
| 2 | Identity derivation repo→constitutional | **EXISTS AND CONNECTED** | `repository_local_urn` — total, pure, injective | Reusable verbatim |
| 3 | Relationship model + emitted-kind binding | **EXISTS AND CONNECTED** | `ART-07` + `CAA-INV-05` both-directions | The pattern to copy for identity |
| 4 | Mutation class governance | **EXISTS AND CONNECTED** | 9 classes, `R-01…R-09`, fail-closed `UNRESOLVED` | Fabric already classifies as `SOURCE` |
| 5 | Existence registration requiring authority | **EXISTS AND CONNECTED** | `engine/ceu/existence.py::relate(authority=…)` | The correct terminal for the fabric |
| 6 | Evidence key contract | **EXISTS AND CONNECTED** | `verification_intelligence/evidence.py` | Reusable as-is |
| 7 | Ownership determination | **EXISTS BUT NOT CONNECTED** | `OwnershipDeterminationEngine` (27.86% closed) | Fabric answers independently |
| 8 | Context resolution | **EXISTS BUT NOT CONNECTED** | `engine/context/resolution.py` (5 prod importers) | Fabric never calls it |
| 9 | Impact / blast radius | **EXISTS BUT NOT CONNECTED** | `blast_radius.py`, `verification_impact/impact.py` | In-package only |
| 10 | Secret scan / security findings | **EXISTS BUT NOT CONNECTED** | `platform/security/` — TEST-ONLY orphan, frozen `PL-F2` | Zero prod importers |
| 11 | Authorization (default-deny) | **EXISTS BUT NOT CONNECTED** | `platform/identity/policy.py` `"no-grant"` | Never on an admission path |
| 12 | Trust chain verification | **EXISTS BUT NOT CONNECTED** | `require_trusted` — 6 sites, none content-admission | Correction to prior claim |
| 13 | Provenance chain | **EXISTS BUT NOT CONNECTED** | `ukip/provenance.py` — verifies without the original | Knowledge plane only |
| 14 | Lineage projection | **EXISTS BUT NOT CONNECTED** | `engine/lineage/` — TEST-ONLY orphan, zero persistence | The shape to reuse |
| 15 | Lifecycle execution + replay | **EXISTS BUT NOT CONNECTED** | `engine/nucleus/lifecycle.py` `UCL-000001`, 45 stages | Fabric terminates in a record |
| 16 | Emitted-identity plane binding | **EXISTS BUT NEEDS EXTENSION** | Extend the `CAA-INV-05` both-directions test to identity | Mechanism one section away |
| 17 | Assimilation reason vocabulary | **EXISTS BUT NEEDS EXTENSION** | `ASSIMILATION_REASONS` — closed 6-tuple, all structural | 0 of 7 directive reasons expressible |
| 18 | Held (Quarantine) disposition | **EXISTS BUT NEEDS EXTENSION** | `DEFERRED` is terminal; `uccep_engine.py::emission_authority` is the reference shape | — |
| 19 | Non-document adapter | **EXISTS BUT NEEDS EXTENSION** | `RecordSetAdapter` declared-schema seam | The intended extension point |
| 20 | Assimilation concept ownership | **EXISTS BUT NEEDS EXTENSION** | Matrix addendum over `USIS-WAVE1` + `CEP-002 Art. 28`; precedent `Ω-E03`/`Ω-E04` (0 CREATE) | Matrix line 43 already says *TO FORMALIZE* |
| 21 | Faculty granting the right to admit | **TRULY MISSING** | `engine/ceu/catalog.py::SEED_CLASSIFICATIONS` — open, `closed_set: False` | EXTEND of data, not a new engine |

**Totals: CONNECTED 6 · NOT CONNECTED 9 · NEEDS EXTENSION 5 · TRULY MISSING 1.**

**Zero CREATE.** Even element 21 resolves by appending a faculty to CEU data — the same mechanism by which `engine/ceu/catalog.py` admits ~55 forms of existence *"without a line of new code."*

---

## 9 — CONTRADICTION REGISTER

### 9.1 Contradictions located in Repository Truth

| ID | Contradiction | Evidence | Severity |
|---|---|---|---|
| **C-1** | `platform/universal_assimilation` presents itself as the universal admission substrate while the canonical ownership matrix has **no row for assimilation as a substrate** and CAA-001 does not register it among its eleven instruments | Matrix lines 32/46 only; CAA-001 `subordinate_instruments`; absent from `uccep-bindings.json` | **HIGH** |
| **C-2** | `02-CANONICAL-OWNERSHIP-MATRIX.md` contains **zero occurrences of "security"** while `SECURITY-GOV-000` OUTPUT 6 declares `PHASE-008 SECURITY` the owner. Two instruments, one silent | `grep -ci security` → 0 | **HIGH** |
| **C-3** | The declared security owner **may not enforce** (`USA-6` *"enacts nothing at the architecture layer"*), yet an admission-time security boundary is enforcement by definition | `SECURITY-001` §1, `USA-6`, `USA-7`, `USL-010` | **HIGH** |
| **C-4** | `platform/security/**` is declared **frozen and reused-by-reference** at `PL-F2` — the mechanism security must enforce through — and is a **TEST-ONLY orphan with 0 production importers** | Census; only non-test mention is a docstring at `platform/blueprints/provenance.py:23` | **HIGH** |
| **C-5** | `discovery.py:49` claims descriptors are unresolved during discovery *"which is what keeps discovery safe over untrusted catalogs"* — true of discovery, **not true of `resolve_entry_point`**, which imports a JSON-named module with no allowlist, signature or trust check | Verified: grep for allowlist/signature/trusted in `platform/universal_provider/*.py` returns only that comment | **HIGH** |
| **C-6** | `CAA-INV-04` guarantees exactly one identity authority over the **declared** population; at least two **emitted** forms (`UCOS-<CODE>-<12hex>`, `UCOS-USA*-<16hex>`) match neither declared plane shape `^UCOS-[A-Z0-9]+-[0-9]{6}$`. The sibling invariant `CAA-INV-05` performs exactly the both-directions emitted-vs-declared test that would catch this | `identity_authority_resolution.derivation.id_shape`; `uga_engine.py` CAA-INV-04/05 bodies | **MEDIUM-HIGH** |
| **C-7** | `engine/universal_certification` is a **registered certification AUTHORITY** (surface #2 of 14) whose **four importers are all themselves orphans** (`engine/uicm` 0/0; `platform/universal_assurance` 0/15) | Census; `certification_authority_resolution` | **MEDIUM** |
| **C-8** | 14 certification authorities are declared non-competing *"bounded by purpose"*, while `CANONICAL-AUTHORITY-DETERMINATION.md` `CONFLICT-06` registers *"ten validation authorities, no reconciling verdict"* and `CONFLICT-07` *"aggregate gates mutate the homes they judge"* | Both instruments | **MEDIUM** |
| **C-9** | `mutation-governance-boundary.json`: `verify.sh` *"observes … and may never author"*, yet the recorded incident is *"a verification command minted 140 permanent Universal Identifiers as a side effect of a drift check"*; and `GATE-PURITY` measures **4 of 46** gate targets declaring a mode with **≥24** mutating tracked truth | `mutation-governance-boundary.json`; `GOVERNED-EVOLUTION-STATE-DETERMINATION.md`; `GATE-PURITY` `GP-1…GP-11` | **HIGH** |
| **C-10** | The faculty vocabulary is open and contains **no faculty for admission, assimilation, trust or evolution** — so no role holds the right to assimilate, while 14 surfaces assimilate | `engine/ceu/catalog.py::SEED_CLASSIFICATIONS`; `engine/nucleus/authority.py` | **MEDIUM** |
| **C-11** | `intelligence/die/imports.py` — the repository's own reachability and dead-code analyzer — is a hard orphan and **currently unimportable**: no `__init__.py`, and it imports a nonexistent `.evidence_bridge`. The measurement that would locate every orphan above cannot run | Verified | **MEDIUM** |
| **C-12** | `engine/uckp` is the largest inbound hub (53 prod importers) and a large share of those importers are orphans, so a naive per-package count reports the core as healthy while its leaves are inert | Census, clusters 1–4 | **INFORMATIONAL** |
| **C-13** | Matrix line 43 records the **Constitutional Reuse Gate** as *"WEAK / TO FORMALIZE"*, and line 104 prescribes closing it by **EXTEND** of the Context Assimilation Gate rather than a parallel gate — a disposition recorded and not executed | `02-CANONICAL-OWNERSHIP-MATRIX.md` | **LOW-MEDIUM** |

### 9.2 Contradictions that are not contradictions

Recorded so they are not mistaken for defects:

- **Plural authority is lawful.** `MULTIPLE_INDEPENDENT_AUTHORITIES` (certification, 14), `MULTIPLE_INDEPENDENT_BOUNDED_NAMESPACES` (identity namespaces), four existence authorities. The declared test is *"a rival = a second authority over the SAME bounded question"*, and none is found. Multiplicity alone is not duplication.
- **`CMG-000001` is ORTHOGONAL, not subordinate.** Self-bounded (*"Supreme over META-CONSTITUTIONAL MATTER ONLY… Confers NO authority over constitutional content"*), exempt from `CAA-INV-02/03` and measured instead by `CAA-INV-08`. Not a competing root.
- **Refusing a predictive engine is not a missing capability.** `engine/uaue/simulation.py:1-25`; prediction is admissible as a CEU form with `verifies` as the path to truth.
- **`engine/discovery`'s single function-local importer is deliberate**, documented at `engine/uckp/assimilation.py:635-641`. Weak coupling by design, not by accident.

### 9.3 Corrections to my prior determination

Offered as evidence. The located instrument governs.

| # | Prior claim | Correction |
|---|---|---|
| 1 | *"Four disjoint identity namespaces… an owner decision is needed on which mint is canonical"* and listed this as a critical-path prerequisite | **Wrong framing.** `UCKP-ART-05` is the single declared identity authority, with two declared planes and a total/pure/injective derivation, measured by `CAA-INV-04 EXACTLY_ONE_IDENTITY_AUTHORITY`. **No selection is required.** The real defect is narrower: two *emitted* forms are bound to neither declared plane (§4.3). This removes one of the two decisions I previously placed on the critical path |
| 2 | *"12 certification surfaces (11 AUTHORITY + 1 PROJECTION)"* | **14 surfaces: 13 AUTHORITY + 1 PROJECTION.** The added entries are `UKIP-KNOWLEDGE-CERTIFICATION` and `REPOSITORY-INTELLIGENCE-CERTIFICATION` |
| 3 | *"`platform/foundation/trust.py` `require_trusted` has exactly one caller"* (inherited from the earlier fabric determination) | **Six call sites** — five in-module guards (`delegate`, `rotate`, `notarize`, `revoke`) plus one external (`admission.py:398`). The consequence is unchanged: no content-admission path consults it |
| 4 | *"`engine/universal_certification` has zero consumers"* | **Four importers**, all themselves orphans. It is a transitive orphan inside a three-package dead cluster, not a zero-importer module. The corrected finding is stronger, because a registered AUTHORITY with only dead consumers is a governance issue, not merely dead code |

---

## 10 — OWNERSHIP RECOMMENDATIONS

**No ownership is assigned here. Each row names the located authority who would decide, and the disposition the corpus's own precedent implies.**

| # | Subject | Route to | Implied disposition | Precedent |
|---|---|---|---|---|
| 1 | Assimilation as a concept | `USIS-WAVE1` (Context Assimilation Gate) + `CEP-002 Art. 28`/`UCDA-000001`, via a matrix addendum | **EXTEND** (CREATE unavailable — located owners exist for parts of the concept) | `Ω-E03` identity: 48 REUSE / 6 EXTEND / 0 CREATE, after the matrix *"contained zero occurrences of the word identity"*. `Ω-E04`: 5 REUSE / 3 EXTEND / 0 CREATE |
| 2 | Which assimilation surface is canonical | The authority that would hold row 1 | **CONSOLIDATE or CROSSWALK** — `Ω-E04` records six owners of the word "lifecycle" *"CROSSWALKED, never merged"*, because a merge amends every owner at once | `Ω-E04` |
| 3 | Security as a concept | `PHASE-008 SECURITY`, via a matrix addendum | **EXTEND**, mirroring row 1 | `Ω-E03` |
| 4 | Where security must occur | Requires an authority that **may enact**. `PHASE-008 SECURITY` may not (`USA-6`). Unresolved by construction | **REFER** — no located authority has standing | §5.6 |
| 5 | Emitted-identity plane binding | `UCKP-ART-05` holder + `UCOS-CAA-001` | **EXTEND** the `CAA-INV-05` both-directions pattern to identity | `CAA-INV-05` |
| 6 | Faculty for admission | CEU (`engine/ceu/catalog.py` data) via `engine/nucleus/authority.py`'s declared-open vocabulary | **EXTEND** (append a faculty; `closed_set: False`) | ~55 CEU forms admitted as data |
| 7 | Assimilation reason vocabulary | `platform/universal_assimilation` owner, once row 1 resolves | **EXTEND** a closed tuple | Its own fail-closed constructor |
| 8 | Intelligence *contribution* ownership | `UAIE-000001` holds measurement only, *"no new owner"*. Route to `CEP-009` (evolution) as the nearest constitutive owner | **REFER** | Matrix intelligence row |
| 9 | Feedback loop ownership | `UNIVERSAL-ASSIMILATION-FEEDBACK-LOOP-DETERMINATION.md` owner + `ART-14` (`CONTINUATION`) | **REFER** | — |
| 10 | Cross-class evolution transaction | `H-06` owner; `AT-1` OPEN | **HOLD** — CREATE already determined by its proper authority | `H-06` verdict C |
| 11 | Gate mode | `H-06` / `CR-09` | **HOLD** — remediation specified, explicitly unauthorized | `GATE-PURITY` D-3.3–3.5 |
| 12 | `engine/universal_certification` standing | Its registered owner, jointly with `platform/universal_assurance`'s | **REFER** — dormant duplicate vs dormant generalization is undecided | `CERT-ARCH-DRAFT` §5 |
| 13 | Six USIS Infinite Intelligence registries | USIS programme owner (`USIS-GOV-000`) | **REFER** — programme scope | 36 md / 0 code |
| 14 | `intelligence/die` reparability | Its owner | **REFER** — the reachability measurement cannot currently run | C-11 |

### 10.1 The ordering the corpus's own precedent implies

Rows 1 and 3 are **ownership acts that precede every technical binding.** Until assimilation and security have canonical homes, any wiring would be performed by an unregistered authority — which is the defect, not the fix. `Ω-E03` and `Ω-E04` are the templates: measure Repository Truth first, find a located owner for every part, and record REUSE/EXTEND with zero CREATE.

Rows 4, 8, 9 are **genuinely unownable as things stand** and are the honest residue of this determination.

---

## 11 — FUTURE UNKNOWN HANDLING

### 11.1 Verdict per unknown

| Unknown | Supported without kernel redesign? | Mechanism |
|---|---|---|
| Entities | **Yes** | `engine/ceu/catalog.py` — ~55 forms as data rows through the ordinary registration path; Nucleus and Layer are rows, not privileged types; `engine/ceu/sufficiency.py` measures per row *"could this have been data?"* |
| Technologies | **Yes** | `ISD-L-09` *Technology Is An Evolutionary State*; `_TECHNOLOGY_MARKERS` rejection keeps bands 11/12/13 neutral; `SECURITY-001` forbids concrete technology binding |
| APIs | **Yes in vocabulary, No in capability** | `declare_kind` is open; **no protocol adapter exists** and a declared kind without an adapter fails closed. `RecordSetAdapter` is the intended seam |
| Interfaces (UI/UX) | **Yes in vocabulary, No in capability** | `00-BOOK/SCHEMAS/ui-artifact.schema.json` governs zero instances |
| Intelligence forms | **Yes** | `engine/provider/metatypes.py` — provider category is an open kernel meta-type tagged `CATEGORY_ROLE`; 11 provider facets as data; *"nothing here names a vendor, a technology, or a concrete provider"* |
| Civilizations | **Yes** | `engine/civilization` (2 prod importers); `MCOS-000001` gated at 100% branch coverage with an **open-world** gate (`G-16`) |
| Environments | **Yes** | `engine/execution_environment` (CLI); `UEG-000001`; `ISD-AX-07` |
| Contexts | **Yes** | `engine/context/taxonomy.py:516 extend()` — bounded-open: a new taxon must name an existing parent and may not self-declare `universal`. `UCXI-000001` owns the reference frame and **may never own Permission** — *"CXL-10 is that context describes and never grants"* |
| Relationships | **Yes, and measured in both directions** | `ART-07` model owner + `CAA-INV-05`; but `ISD-G-04`: 12,899 edges materialized with **no gate validating them against `relationship.schema.json`** |

**Kernel redesign is not required. Verified structurally: `engine/kernel/compliance.py:91` proves no source in `engine/kernel/` defines any `enum.Enum` at all** — the proof takes `directory` as a parameter only so it can be tested against a control sample. Every closure sits outside the meta-kernel by construction.

### 11.2 The authority-side openness guarantee

Openness is not only a substrate property here; it is an **authority** property, and that is the more important finding for this determination:

- `authority_roles` is **open by registration** (`UCKP-ART-17`) — *"a new standing is one appended entry, never a law amendment."*
- The faculty vocabulary is open — `closed_set: False`, `upper_limit: None`, `owning_roles()` *"discovered, not enumerated."*
- Mutation classes 6–8 are **owner-parameterised** — the authority is whatever the artifact declares of itself, so a future programme needs no new class.
- `existence_resolution`, `certification_authority_resolution` and `identity_namespace_resolution` are all **plural-and-bounded**, so a future authority over a genuinely new bounded question is an appended entry, not a conflict.

**Determination: an unknown future intelligence form can acquire a role, a faculty, a mutation class and an authority standing without amending any law.** That is the strongest single guarantee located in this determination, and it is what makes the assimilation binding a wiring problem rather than a constitutional one.

### 11.3 The four disclosed ceilings

| ID | Ceiling |
|---|---|
| `ISD-CE-11` | **`ADMISSION_FORMS` has exactly two members**, both document-append shaped. The openness prover is itself a closed set of 2. A future subject class outside that shape can be *asserted* open, never *probed* open |
| `ISD-G-09` | `test_infinite_scope.py` asserts `len(unintentional) == 1`, so **disclosing a newly located undisclosed closure requires an engine-plane edit.** Self-described as *"a meta-assumption about disclosure cost"* |
| `ISD-CE-09` / `ISD-G-01` | `KnowledgeCapability`, 11 members, `closing_invariant: "NONE DECLARED IN CODE"`, `intentional: false`. The one live undisclosed-intent closure — and it sits in the knowledge plane, the plane Infinite Intelligence expands through. Its own disclosure names the remedy: `ProviderKind`'s fail-closed coercer |
| `ISD-G-07` / `ISD-G-08` | `KNOWN_PERSISTENCE_KINDS` / `KNOWN_EXECUTION_KINDS` claim *"Open by registration (Article 17)"* in their own comments while **no registry holds them** — *a claim exceeding its mechanism* |

Items 3 and 4 are the pattern to watch: **openness asserted in a comment rather than carried by a coercer.** A universal assimilation fabric would propagate that pattern fastest, because every new kind would inherit the assertion. `CAA-INV-05`'s both-directions test is the located antidote.

---

## 12 — PRECONDITIONS BEFORE IMPLEMENTATION

Ordered. Each names who decides. None is a task.

### 12.1 Ownership preconditions — must precede all technical work

| P | Precondition | Decider | Blocks |
|---|---|---|---|
| **P-1** | Assimilation has a canonical home in `02-CANONICAL-OWNERSHIP-MATRIX.md` | `USIS-WAVE1` + `CEP-002 Art. 28` holders | Everything. Without it, any wiring is performed by an unregistered authority |
| **P-2** | Exactly one assimilation surface is canonical; the others are crosswalked or consolidated | Holder of P-1 | All wiring |
| **P-3** | Security has a canonical home in the matrix | `PHASE-008 SECURITY` | P-6 |
| **P-4** | If the fabric is to be an authority-claiming instrument, it is registered in `UCOS-CAA-001` with a role and ≥1 article | `UCOS-CAA-001` holder | Gate registration |

### 12.2 Boundary preconditions

| P | Precondition | Decider | Note |
|---|---|---|---|
| **P-5** | Emitted identity forms are bound to a declared plane, or a third plane is declared | `UCKP-ART-05` holder | Not a selection — the authority is settled; the binding is not |
| **P-6** | The temporal placement of security acts is declared, by an authority that **may enact** | Unresolved — `PHASE-008 SECURITY` may not enact | The hardest precondition. §5.6 gives three located precedents |
| **P-7** | A faculty granting the right to admit is registered, or it is determined that admission requires no faculty | CEU / `engine/nucleus/authority.py` | `holds()` fails closed, so today no role may assimilate |
| **P-8** | `resolve_entry_point`'s trust boundary is declared owned | `PHASE-008 SECURITY` (domain) + `platform/universal_provider` owner | One function; mechanism already adjacent |

### 12.3 Governance preconditions

| P | Precondition | Decider |
|---|---|---|
| **P-9** | Gate mode is declared (`OBSERVE` / `EXECUTION`) for any new gate | `H-06` / `CR-09` |
| **P-10** | Whether `EvolutionLedger` may be persisted, and under which mutation class | `GOVERNED-EVOLUTION-STATE` owner; blocked because `classify_object` is **total** with an unconditional terminal branch, so admitting a class reclassifies every object |
| **P-11** | Whether a cross-class evolution transaction boundary has an authority | `H-06` `AT-1` |
| **P-12** | `engine/universal_certification`'s standing resolved before anything new binds to certification | Its owner + `platform/universal_assurance` owner |

### 12.4 Measurement preconditions

| P | Precondition | Why |
|---|---|---|
| **P-13** | `intelligence/die` is importable | The repository's own reachability measurement cannot run, so the orphan census in §3.4 cannot be reproduced by the repository itself — only by hand |
| **P-14** | `ISD-CE-09` / `ISD-G-01` is disclosed with a closing invariant, or the enum acquires a coercer | It is the one live undisclosed-intent closure and it is in the knowledge plane |
| **P-15** | `ISD-G-04` — a gate validates the 12,899 relationship edges | If the fabric begins emitting edges, it emits into an unmeasured surface |

### 12.5 The critical path

**Two ownership acts (P-1, P-3) and one unresolvable-as-things-stand question (P-6).**

Everything technical in §8 is wiring or extension of located surfaces. Nothing technical is blocked by engineering difficulty. **The critical path is entirely constitutional**, and P-6 is the one precondition with no located authority — because the declared security owner is barred from enacting, and the mechanism it would delegate to is frozen and inert.

---

## 13 — FINAL DETERMINATION

**The correct integration boundaries are, with two exceptions, already declared, measured and fail-closed. The assimilation fabric sits outside all of them.**

The repository's authority architecture is stronger than the integration gap suggests: one supreme law with eight open roles; eleven registered instruments each naming its superior and articles, checked in both directions; a single identity authority with two planes and an injective derivation; nine mutation classes under total ordered precedence with a fail-closed terminal; plural-but-bounded resolutions for existence, certification, namespaces and relationships; a faculty model resolved from data that fails closed on unregistered roles. **This is not a system that needs a new authority. It is a system with one substrate that never joined it.**

The two exceptions are the honest residue:

1. **Assimilation and security have no canonical home** — verified: the matrix has two narrow assimilation rows and zero occurrences of "security."
2. **The declared security owner may not enforce, and the mechanism it must enforce through is frozen and orphaned** — so *where security must occur* cannot be answered by any located authority.

Everything else resolves as EXTEND or WIRE against surfaces that exist. The answer to primary question 7 is the practical key: **new existence reaches Infinite Intelligence today by CEU registration with a named authority, and `engine/ceu/existence.py::relate()` is the one admission surface in the repository that requires authority non-optionally.** The fabric's defect and its remedy are the same fact — it does not use the door that asks the question it never answers.

**Zero new engines. Zero new identifiers. Zero new requirements. Zero new ADRs. Zero registry changes. Zero certification changes. Zero CREATE originating here.**

---

## 14 — STOP

**DETERMINATION COMPLETE. NO IMPLEMENTATION AUTHORIZED.**

No phase created. No roadmap created. No repository state changed beyond this file. The fifteen preconditions in §12 are decisions reserved to located authorities, and three of them (P-4, P-6, P-8) may require an authority act before any decision is even admissible.

Awaiting explicit authorization.
