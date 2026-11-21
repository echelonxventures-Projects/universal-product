# UCOS Ω∞ — UNIVERSAL ASSIMILATION FABRIC DETERMINATION

| Field | Value |
|---|---|
| ARTIFACT | `UCOS-OMEGA-INFINITY-UNIVERSAL-ASSIMILATION-FABRIC-DETERMINATION.md` |
| CLASSIFICATION | `EVIDENCE` — derived analysis. Not an instrument, not a certificate, not a design authorization. |
| AUTHORITY | **NONE — DERIVED TRUTH.** Legislates nothing, ratifies nothing, certifies nothing, assigns no ownership, mints no identifier, creates no requirement, creates no ADR, authorizes no engine. Where this determination and a located instrument differ, **the located instrument governs.** |
| MODE | **ASSIMILATION ONLY** — determination of required architecture. No implementation. |
| MUTATION | **READ ONLY OBSERVATION.** Single mutation is the creation of this file. |
| BASELINE | HEAD `bae59755` · branch `integration/recovery-001` · working tree 66 uncommitted entries |
| REUSE CONSTRAINT | Binding on this determination: **no new engine is proposed unless reuse is demonstrated impossible.** Every gap below names the existing surface that would carry it. |
| DISPOSITION | No finding is a requirement. No gap is an implementation task. No recommendation is authorized for execution. |

---

## 1 — EXECUTIVE SUMMARY

### 1.1 The question

Can any entity, artifact, capability, principle, requirement, technology, API, UI/UX, infrastructure, knowledge object, intelligence, or future unknown construct be assimilated through **one universal pathway**?

### 1.2 The determination

**No — and the obstacle is not a missing engine. It is a missing binding layer between fourteen engines that already exist.**

The repository contains **fourteen distinct admission surfaces**, each individually well-built, most fail-closed, several genuinely excellent. What it does not contain is anything that makes them one pathway. Measured at code level:

- **Two independent identity mints**, neither importing the other, with disjoint keyspaces — `engine/uckp/identity.py:73 mint()` producing `urn:ucos:ucko:<ns>:<local>`, and `engine/registry/universal/identity.py:257 deterministic_id()` producing `UCOS-<CODE>-<12 hex>`. Verified directly: neither file references the other.
- **Four duplication-prevention stores**, none of which can see another's contents.
- **Three unjoined kind vocabularies** (assimilation source kinds, provider categories, schema families) with no mapping between them.
- **`platform/universal_assimilation/` — the module whose docstring claims "one road for every source" — contains zero imports from `engine/` in either direction.** It is a total island.
- **`engine/object_birth/` — the "identity before existence" contract — has zero production importers.** It is reachable only as a CLI gate subprocess (`python -m engine.object_birth.gate`). Nothing in the system calls `birth()` to actually mint an object.

### 1.3 The three structural findings that decide the answer

**Finding A — every admission path terminates in a document normaliser.** All seven adapters in `platform/universal_assimilation/adapters.py` convert *bytes of a document* into text or records. There is no adapter for a UI screen, an API surface, an infrastructure resource, or a technology. The declared kind vocabulary is open (`contracts.py:122 declare_kind`), but a declared kind with no adapter fails closed at `adapters.py:724 select()`. **So the pathway is universal in its vocabulary and document-shaped in its capability.**

**Finding B — the categories the directive names are, with one exception, unadmittable.** API/protocol: no `ProtocolAdapter` exists, and concrete protocol tokens are *actively rejected* by `_TECHNOLOGY_MARKERS` in `service/service.py:64-83`, replicated in `application/` and `infrastructure/`. UI/UX: `00-BOOK/SCHEMAS/ui-artifact.schema.json` exists and governs **zero instances** (`grep -c "UCOS-UI-" 00-BOOK/DATA/artifacts.json` → 0); the whole tree contains one `.html` file and no `.tsx/.jsx/.vue`. Infrastructure: no registry, no IaC, no instance data. Technology: three code-or-schema-bound paths. **The one exception is provider categories** (`engine/provider/metatypes.py:29 CATEGORY_ROLE`), which are genuinely admitted by declaration — and 13 of 14 declared providers are dead stubs because none names an `entry_point`.

**Finding C — there is no security gate on admission, at all.** This is the sharpest finding and it is not a nuance. No authentication, no authorization, no trust check, no provenance verification, and no integrity verification anywhere on the assimilation path. The trust engine exists (`platform/foundation/trust.py`, HMAC-SHA256, delegation chains, revocation) and its `require_trusted` has exactly **one** caller in the entire codebase: `platform/foundation/admission.py:393` inside `migrate_authority()` — i.e. renaming an authority requires a trusted key; admitting content does not. The default-deny `PolicyEngine` exists (`platform/identity/policy.py:200` `"no-grant"`) and is instantiated in exactly one non-test place, never on an admission path. And `platform/universal_provider/discovery.py:372 resolve_entry_point` performs unrestricted `importlib.import_module` on a module name taken from a JSON descriptor — **a data file is sufficient to get arbitrary code imported and called, with no signature check, no allowlist, and no sandbox.** Digests are computed *from* the submitted payload and become its identity, so there is no expected value to compare against and upstream tampering is undetectable by construction.

### 1.4 What already exists and is genuinely strong

This determination is not a negative assessment. Four properties are better-built than most systems achieve:

1. **Identity as computation, not allocation.** `UniversalIdentity.mint` is pure — no clock, no path, no counter, no I/O (`engine/uckp/identity.py:73`). Two callers asking for the same name get the same identity rather than two identities. Duplication by contention is impossible by construction.
2. **Content-addressed everything, with meaning separated from integrity.** `content_sha256` over all 33 facets is the tamper check; `semantic_digest()` over casefolded concept+definition alone is the *duplicate-detection* identity (`engine/uckp/ucko.py:322`). That distinction is the correct one and most systems do not make it.
3. **Openness measured rather than asserted.** `engine/infinite_scope/contract.py:733 check_admission_path_exercisability` **performs a live in-memory admission of a synthetic probe** and reconciles declared refusals against measured ones in both directions (`_reconcile:770`). A stale recorded refusal fails just as an undeclared one does. `ISD-AE-03` is deliberately a positive control because "a law that can only ever fail is indistinguishable from a broken law."
4. **Fail-closed as the default posture.** Almost every door refuses rather than degrades. The exceptions are catalogued in §4 and are exceptions, not the rule.

### 1.5 The fabric determination in one paragraph

The required architecture is **not a fifteenth engine**. It is a **binding layer** with five elements, every one of which has an existing owner that could carry it: (i) a **subject-kind register** joining the three existing kind vocabularies — the mechanism exists at `engine/provider/metatypes.py` (category-as-registered-meta-type) and needs no new engine; (ii) a **kind → obligations relation**, for which the raw material already exists as declared stage read-sets (`UVI-L-12`) plus the unused query `selection.py:372 stages_reading`; (iii) **admission-time impact**, for which both engines exist and one (`engine/graph/architecture/impact.py`) is entirely unwired; (iv) a **trust/authorization binding on admission**, for which the complete machinery exists and is orphaned; (v) a **cross-store identity and duplication reconciliation**, for which four stores each already hold the correct local mechanism. In every case reuse is not merely possible — the component exists and is unwired. **No new engine is determined necessary. One is determined possibly-necessary and is named in §11.3.**

### 1.6 Answer to each sub-question the directive poses

| Question | Determination |
|---|---|
| What already exists? | Fourteen admission surfaces, two mints, four duplication stores, one measured-openness prover. §3 |
| What overlaps? | Identity minting (2×), duplication detection (4×), assimilation naming (2× identically-named `AssimilationReport`), lifecycle/stage models (4×), kind vocabularies (3×). §6 |
| What should be unified? | Subject-kind identity, obligation derivation, admission-time impact, trust binding, cross-store duplication view. Five items. §7 |
| What should remain specialized? | The seven document adapters, the four disjoint relationship planes, the per-class mutation authority chains, the domain registries' `required_attributes`, band-11/12/13 technology neutrality. §8 |
| What universal substrate is missing? | Ten named absences, §9, of which the security binding (§4.9) is the most consequential and the subject-kind register (§9.1) is the keystone. |
| Are new engines needed? | **No, for nine of ten gaps.** §11 |


---

## 2 — METHOD AND EVIDENCE BOUNDARY

### 2.1 Method

Read-only investigation at HEAD `bae59755`. Admission surfaces were located by reading the modules, then their interconnection was measured by import grep in both directions rather than inferred from docstrings. Where a module's stated purpose and its measured wiring disagreed, **the measured wiring is reported.**

### 2.2 Evidence boundary

| Limit | Statement |
|---|---|
| Working tree | 66 uncommitted entries. All measurements are working-tree evidence at `bae59755`, not clean-checkout evidence. |
| No execution | No gate, test or engine was run. Counts quoted from declarations and comments (151/390/541 ownership subjects, 36 Ω-A12 siblings, 142 store objects, 1,233 registry artifacts) are declaration-derived, not live-run derived. Exception: `closure.json` and `git` state were read directly. |
| Corrected citation | A prior analysis pass cited `engine/security/zones.py`. **`engine/security/` does not exist.** Verified: `find . -type d -name security` returns only `./platform/security`. The security tree is `platform/security/` (11 modules). This determination uses the verified path. |
| Not read in depth | `platform/universal_provider/validation.py` (1,009 lines) beyond `EffectsDeclaredGate`; the 7 birth stages as data in `uobc-birth-contract.json`; `00-BOOK/tools/ukb.py` / `ukbx.py` internals; `engine/registry/universal/core.py` full gate order; the four `SEARCHES` bodies in `engine/constitution/assimilation.py`. Each is flagged where relied upon. |
| Two surfaces identified but not traced | `platform/runtime_platform/{core,service}.py admit(attestation)` and `engine/uaue/controller.py:805 admit(candidate)`. Recorded as located-but-unanalysed. |

---

## 3 — EXISTING ASSIMILATION MECHANISMS

### 3.1 The fourteen admission surfaces

| # | Surface | Admits | Fail-closed | Mints identity | Wired to |
|---|---|---|---|---|---|
| A1 | `platform/universal_assimilation/pipeline.py:164 assimilate_source` | any source *as bytes*, via 14 declared kinds | by **state**, not exception (5-state ladder) | **no** — content-addressed `source_id` only | `platform/universal_{foundation,measurement}` only. **Island vs all of `engine/`** |
| A2 | `engine/uckp/assimilation.py:337 assimilate_artifact` | one native artifact record → one UCKO | only on empty `universal_id` | yes, via `urn_for` (**unvalidated** — bypasses mint()'s regexes) | `engine/uckp/*` only |
| A3 | `engine/knowledge/ukip/registry.py:396 submit` | a classified knowledge unit | **yes** — `DuplicateHomeError` both directions | no — content-derived `knowledge_id` | `engine/knowledge/*` |
| A4 | `engine/knowledge/capability.py:388 assimilate_capabilities` | capability records → knowledge base | **no** — merge projection, no gate | no | `engine/knowledge/*` |
| A5 | `engine/object_birth/birth.py:50 birth` | any object, pre-existence | **yes** — 4 laws before identity derivation | yes, mint #1 (full `mint()` + `require_intact()`) | `engine/uckp/identity` — **the one real bridge**. Zero production importers of its own |
| A6 | `engine/ceu/existence.py:291 register` | any `ExistenceUnit` of any form | **yes** — 4 gates | yes, **mint #2** | `engine/registry/universal/identity`; consumed by `engine/nucleus/authority.py:43` |
| A7 | `engine/ceu/existence.py:357 declare_form` | a new *form* of existence | yes, transitively via `register_kind` | issues a kind code | writes **process-global** `_EXTENSION_KIND_CODES` |
| A8 | `engine/registry/universal/registries.py:43 TypedRegistry.register` | one version of one artifact, 12 kinds | **yes** — `required_attributes` | yes, mint #2 | `core.py` Knowledge-Once index |
| A9 | `engine/constitution/gateway.py:475 apply` | a `Mutation` over constitutional metadata | **yes** — `MutationRefused`, clause CEL-04 | no | only caller: `engine/constitution/evolution.py:43` |
| A10 | `00-BOOK/tools/register.sh` (10 phases) | corpus artifacts | **yes** — any phase failure ⇒ transaction INCOMPLETE | **yes** — Phase 1 `ukb.py build --mint`, the only corpus mint site | nothing in `engine/`; no constitutional seal in the loop |
| A11 | `platform/universal_provider/framework.py:177 admit` | a provider descriptor | yes on registry refusal (PC-13 additive) | no | `discovery.py:372 resolve_entry_point` → **arbitrary `importlib`** |
| A12 | `platform/foundation/admission.py:207 AdmissionBinder.admit` | an artifact binding | yes — duplicate key/name | yes (mints via authority) | `trust.require_trusted` **only** in `migrate_authority` |
| A13 | `engine/context/taxonomy.py:516 extend` | a new context taxon | yes — must name existing parent; may not self-declare `universal` | no | `engine/context/*` |
| A14 | `engine/infinite_scope/contract.py:733` | *nothing* — it **proves** other doors are exercisable | yes — vacuity refusal first | no; registers nothing (ISD-BND-08) | reads other owners' documents and readers |

### 3.2 The topology: three islands, one bridge, one one-way street

```
        ┌─────────────────────── ISLAND 1 ────────────────────────┐
        │  platform/universal_assimilation/   (A1)                │
        │  "one road for every source"                            │
        │  zero imports to or from engine/  ── measured, not assumed│
        └─────────────────────────────────────────────────────────┘

        ┌─────────────────────── ISLAND 2 ────────────────────────┐
        │  engine/uckp/assimilation (A2) ── engine/uckp/identity  │
        │                                        │ MINT #1        │
        │                                        │                │
        │                        ┌───────────────┘  ◄── THE ONE   │
        │                        │      BRIDGE          BRIDGE    │
        │            engine/object_birth/ (A5)                    │
        │            (zero production importers)                  │
        └─────────────────────────────────────────────────────────┘

        ┌─────────────────────── ISLAND 3 ────────────────────────┐
        │  engine/ceu/existence (A6,A7) ──one-way──►  MINT #2     │
        │                            engine/registry/universal/   │
        │                                    identity + (A8)      │
        └─────────────────────────────────────────────────────────┘

   A9 gateway ── caller: evolution.py only.  No filesystem at all.
   A10 register.sh ── mints corpus IDs. Knows no gateway, no mint #1 or #2.
   A11 provider ── own registry. importlib from a JSON string.
   A14 infinite_scope ── the only surface that reads across doors, and it
       writes nothing: it proves admission paths work, in memory.
```

### 3.3 The two mints — verified independent

| | Mint #1 | Mint #2 |
|---|---|---|
| Home | `engine/uckp/identity.py:73 mint()` | `engine/registry/universal/identity.py:257 deterministic_id()` |
| Form | `urn:ucos:ucko:<ns>:<local>` + RFC-4122 v5 UUID | `UCOS-<CODE>-<12 hex>` |
| Validation | `_NAMESPACE_RE` + `_LOCAL_RE`, both raising `IdentityError` | `is_well_formed`, code `[A-Z][A-Z0-9]{1,7}` |
| Purity | pure — no clock, no path, no counter, no I/O | deterministic; version-independent by design |
| Used by | `engine/uckp/*` + `engine/object_birth/birth.py:30` | `engine/ceu/existence.py`, all 12 typed registries |
| Cross-import | **none** — verified by direct grep in both directions | **none** |

**The `second_authority_test` is counter-shaped, not keyspace-shaped.** Its text lives in data at `00-BOOK/DATA/constitutional-authority-alignment.json:363`, with `"mint_markers": ["category_seq"]` at `:364` — i.e. the test is operationalised as *a grep for the token `category_seq`*, enforced at `engine/object_birth/ledger.py:34,70` and `engine/object_birth/contract.py:105`. Mint #2 advances **no counter**, so it **passes the test as written** while being, in plain terms, a second identifier-issuing authority over a different population. The same declaration acknowledges this at `:581` by declaring `MULTIPLE_INDEPENDENT_BOUNDED_NAMESPACES` rather than one.

**This is recorded as an observation, not an error.** The declaration is internally consistent and honest. But it means "one universal pathway" cannot be claimed at the identity layer, because two conforming mints exist by declared design.

### 3.4 What the fabric can actually admit today

| Category named in the directive | Admission surface | By declaration alone? | Verdict |
|---|---|---|---|
| Knowledge object | A1/A2/A3 | kind yes, adapter no | **ADMISSIBLE** |
| Entity | A5/A6 | form yes (`declare_form`) | **ADMISSIBLE** |
| Artifact | A10/A12 | no — transaction/binding | **ADMISSIBLE** |
| Capability | A4/A8 | yes (`required_attributes={"summary"}`) | **ADMISSIBLE, ungated** |
| Principle | A9 (constitutional metadata) | via gateway only | **ADMISSIBLE** |
| Requirement | derived from concepts (`RR-<CONCEPT-ID>`) | derived, not admitted | **DERIVED** |
| Intelligence (form) | `adr/0011` + stage manifest declaration | yes, stage as declaration | **ADMISSIBLE (learning); NOT ASSESSED (reasoning)** |
| Future unknown construct | A7 `declare_form` + A13 `extend` + A14 proof | **yes, and measured** | **ADMISSIBLE — the best-evidenced case** |
| Technology / external dependency | 3 paths, all code-or-schema-bound; provider `kind` is the only declarative one | provider kind yes; realisation no | **PARTIAL** |
| Provider / source of record | A11 + `platform/providers/catalog/*.json` | yes for declaration; **no for activation** | **PARTIAL — 13 of 14 dead stubs** |
| API / interface / protocol | **none.** No `ProtocolAdapter`. `_TECHNOLOGY_MARKERS` actively rejects `openapi`, `grpc`, `graphql`, `http://` in bands 11/12/13 | no | **ABSENT** |
| UI / UX / experience | schema only (`ui-artifact.schema.json`), zero instances, no writer, no adapter kind | schema exists, nothing writes it | **ABSENT (schema-only)** |
| Infrastructure | no registry, no IaC, no instance data; observation schemas only, unbacked | no | **ABSENT** |

**Six of thirteen categories are fully admissible. One is derived. Three are partial. Three are absent.**

---

## 4 — THE TWELVE REQUIRED ANALYSES

### 4.1 Existing assimilation mechanisms

Determined in §3. Fourteen surfaces. The load-bearing observation is that **the module named "universal assimilation" is the most isolated of the fourteen**: `grep -rn "uckp|object_birth|ceu\." platform/universal_assimilation/*.py` returns no matches, and nothing in `engine/` imports it. Its five-state terminal ladder (`REJECTED` / `DEFERRED` / `NORMALIZED` / `ADMITTED` / `ASSIMILATED`, `pipeline.py:180-283`) is well-designed and honest — it distinguishes "no adapter" from "no destination" from "destination not a home" — but it terminates in a record, not in a minted, homed, governed object.

A second observation with fabric consequences: **two different classes named `AssimilationReport` exist** — one in `platform/universal_assimilation/contracts.py`, one in `engine/uckp/assimilation.py` — with no relation between them. The near-identical naming across the island boundary is itself a duplication-detection blind spot, because neither surface's duplication machinery can see the other.

### 4.2 Missing universal binding layer

**This is the determination's core and it is a binding problem, not an engine problem.**

What is missing is a layer that answers four questions for *any* subject, regardless of kind:

1. *What kind of thing is this?* — three kind vocabularies exist (`SourceKindRegistry` 14 kinds; provider `kind` open string; schema families), **with no join key.**
2. *What identity does it get?* — two mints, **no arbitration.**
3. *What must be true of it?* — obligations attach to *stages*, never to *kinds* (§4.8).
4. *Who may admit it?* — no authorization check exists on any admission path (§4.9).

Reuse assessment: element (1) has a working precedent — `engine/provider/metatypes.py:29 CATEGORY_ROLE` makes a category an *open kernel meta-type registration*, and `engine/provider/compliance.py:176-231` proves at runtime that a never-seen category is admitted, discoverable and resolvable. That is exactly the mechanism a universal subject-kind register needs. **It exists. It is scoped to providers.**

### 4.3 Identity integration

**Two mints, both correct, unarbitrated.** §3.3. Additionally:

- `engine/uckp/assimilation.py:307 artifact_urn` calls `urn_for` (`identity.py:57`), which is **unvalidated string interpolation** — it bypasses `_LOCAL_RE`/`_NAMESPACE_RE`. So assimilated artifact identities are not subject to the same well-formedness law as minted ones. Recorded as **F-03**.
- Corpus identity is a *third* allocation path: `register.sh` Phase 1 (`ukb.py build --mint`) allocates permanent Universal IDs and page ranges into `00-BOOK/DATA/id-ledger.json`. It advances a counter — which is precisely what `second_authority_test` looks for — and it is the *declared* holder, so this is consistent, not a violation. But it means identity arrives by **three mechanisms**: computed (mint #1), derived (mint #2), allocated (`ukb --mint`).
- **Nothing cross-checks the four stores.** An object could simultaneously hold a birth record, a CEU existence unit, a typed registration and a corpus ID — under three different identifiers — and no surface would detect it. Recorded as **F-01**.

Reuse: `engine/infinite_scope/contract.py:733` already demonstrates the pattern for cross-owner reconciliation — it reads other owners' documents through the owners' own readers and reconciles declared against measured. A cross-store identity reconciliation would reuse that pattern, not a new engine.

### 4.4 Context integration

`engine/context/` is the most complete package in the repository (18 modules) and its admission surface `taxonomy.py:516 extend()` is properly bounded-open: a future taxon must name an existing parent and **may not self-declare `universal`, because universality is constitutional and cannot be granted by extension** (`CXL-02`). Absence is an explicit unknown value, never a missing kind (`taxonomy.py:48-49`).

Three integration gaps, all previously located and unchanged:

- **`ContextRegistry` is not persisted** (`P4-F-009`). `bind_context` at `engine/ceu/existence.py:653` is a runtime journal action with no corpus record. So a context binding does not survive the process that made it.
- **The taxon has no lifecycle.** No `supersede(taxon)`, no `deprecate(kind)`, no lineage between kinds. The mechanism that would provide it — `engine/ceu/existence.py supersede/resurrect/ancestry` — exists and **is not wired to `ContextTaxonomy`.** This is the single clearest reuse-available gap in the repository.
- **Six-plus ad-hoc `Context` classes bypass the model**: `platform/blueprints/context.py`, `platform/projects/context.py`, `platform/workspace/context.py`, `platform/artifact_explorer/context.py`, `StageContext`, `engine/constitution/{gateway,stages}.py class Context`, plus `engine/runtime/context.py RuntimeContext`, `engine/factory/factories/base.py:44 ExecutionContext`, `engine/uaue/controller.py:116 EvolutionContext`, `engine/uckp/values.py:406 ContextBinding`.

Only `engine/ceu/existence.py:653` treats context as constitutionally load-bearing — it requires `frame` + `resolution_digest` and **refuses rebase** ("a registry is bound to one reality; rebasing produces a new registry"). That refusal is the right law. It applies to one registry.

### 4.5 Relationship integration

Four disjoint planes, `UCRD-001` §5 declaring them disjoint and **explicitly rejecting** "everything is a relationship". Coverage, per plane:

| Property | CEU | UKIP | Projection | DATA |
|---|---|---|---|---|
| Existence | yes | yes | yes (`Edge`) | yes |
| Ownership | yes | yes | partial | partial |
| Per-edge context | **yes** | OPEN GAP | OPEN GAP | OPEN GAP |
| Temporal validity | OPEN GAP | **yes** | OPEN GAP | **refused** (fail-closed; `TemporalCoordinate.from_dict` absent) |
| Evidence linkage | journaled | in-memory only (`P4-F-006`) | partial | partial |
| Evolution | **yes** (the substrate) | inherited | not wired | not wired |

The located reading — which this determination adopts — is that the two partials are **one gap seen twice**: no new capability is required, **propagation is**. `engine/ceu/existence.py` holds supersede/resurrect/ancestry; `engine/knowledge/ukip/relationships.py` holds the temporal algebra with fail-closed `Ordering.INCOMPARABLE` handling. Neither is missing. Neither reaches the other three planes.

Two admission-relevant details: `RelationshipView.relate` (`existence.py:951`) requires a non-optional `authority` keyword — the only admission surface that does — and its symmetric mirror at `:1067-1085` is registered **directly**, bypassing `_check_admissible` and the acyclicity re-check (documented, with reasoning). Unknown relationship types are admitted and the admission is **measured every run** by `ISD-L-06`: *"A comment claiming a vocabulary is append-only is not evidence; a non-mutating extension is."*

### 4.6 Ownership discovery

Ownership is discoverable but by **different mechanisms per store**, and the canonical matrix does not cover the dimension owners.

- `engine/nucleus/model.py:300` makes `owner` **mandatory** — the strongest ownership law located.
- `TypedRegistry.register` defaults `owner="UNASSIGNED"` (`registries.py:43`) — admitted without an owner.
- `engine/uckp/assimilation.py:383` defaults `owner="UCOS-PROGRAM-CUSTODIAN"` — a placeholder owner is minted into the object.
- `platform/universal_truth/policy.py:228 is_canonical_home` answers *"may this location own?"* and contains **no duplicate detection** — eligibility, never uniqueness.
- `engine/knowledge/ukip/registry.py:90 created_home` is the real homing decision: first unit with an identity establishes the canonical home (`REGISTERED`), later units from any provider attach as corroborating sources (`CORROBORATED`). N providers never produce N records. `authoritative`/`priority` affect only *which source is named canonical* — "a second record is not representable."
- `02-CANONICAL-OWNERSHIP-MATRIX.md` contains **no entries** for `UISD-000001`, `UCXI-000001`, `UOBC-000001`, `UCRD-001`, `UAP-001`, `CEU-001`, and its own canonicality is disputed (`CR-04`, `H-01` HUMAN DECISION REQUIRED).

**Determination: ownership discovery works per-store and has no universal view.** The best located mechanism — `created_home` with corroboration rather than duplication — is the one that should be the fabric pattern, and it is scoped to UKIP knowledge.

### 4.7 Authority discovery

Authority is **declared in data and discoverable**, which is a genuine strength. `00-BOOK/DATA/mutation-governance-boundary.json` is the only artifact where the doors acknowledge each other: nine mutation classes, eight authority chains, the determination *"OPTION B — SOURCE MUTATIONS ARE OUTSIDE THE CONSTITUTIONAL MUTATION GATEWAY"*, and a structural (not interpretive) argument for it — including the *measured* absence of `Path`, `open(`, `read_text`, `write_text` and `git` from `gateway.py` and `state.py`.

Three findings:

1. **Cross-door authority is declarative, not executable.** The boundary declares which authority governs which class. `platform/repository_intelligence/mutation_classification.py` makes those rules *decidable*. And **nothing consumes the classifier** — no gate in `verify.sh`, `Makefile`, `.github/workflows`, `scripts`, `platform` or `engine`. Its only importers are its own tests and `engine/verification_impact/changes.py:61`, which reuses `Repository.tracked` and not the classification.
2. **`R-09` `GOVERNED_ANALYSIS` is declared with no implementing predicate** — `validate_rule_coverage()` reports it live. So the class governing derived analyses (including this document) is undecidable.
3. **Two self-recorded vacuity admissions**, quoted because they are the clearest statement of the fabric problem the repository makes about itself:
   - `CORPUS_REGISTRATION` *"was not a declared class at all, so this register's own invariant 'no mutation class is ungoverned' was VACUOUSLY satisfied for it … register.sh --guard duly minted 140 permanent identities from inside ./verify.sh --full"*.
   - `GOVERNED_DECLARATION` — `uisd-declaration.json` *"matched no example in any of the six classes … Six certified mutations to it proved execution validity and could not prove governance validity, because no stage of verify.sh evaluates mutation class. This is the same vacuity … relocated rather than closed."*

The gateway itself is architecturally excellent: seven stages derived by dependency order (`pipeline_order():266` raises if the pipeline declares a cycle), an unevaluable stage coerced to a failed stage, break-at-first-refusal, and — the key design — **a seal monopoly**. It is the only producer of a clean `StateSeal`, and `state.py` refuses to verify/certify/register/measure/govern under a dirty seal. Bypass is not blocked by a rule; *there is nothing at the end of the bypass path.* That is the correct way to make a pathway mandatory, and it governs one mutation class of nine.

### 4.8 Validation discovery

**Validations are discovered per declared *stage*, never per *subject*. A new kind of subject acquires no validations.**

What is declaration-driven and works: the stage registry is data in `uvi-declaration.json`; `constitution.py:290 load_constitution` refuses incoherence (undeclared phase/plane, `depends_on` naming an undeclared stage, duplicate ids, duplicate labels); law↔check binding is bidirectional, so a law naming an unimplemented check and a check no law claims are **both** faults. That bidirectional refusal is the pattern the fabric needs.

What is missing: there is **no `subject_kind → required_obligations` table anywhere.** To make a new subject validated requires hand-authoring in three to five places: an engine module, a stage entry in `uvi-declaration.json`, a `run_stage "<exact label>"` line in `verify.sh`, usually a law entry, plus the label digest in `UAKOS-CLOSURE-008/validation-record.json` and re-derivation in `uisd-gate.yml` (the "three-reader contract").

**The join key is free text.** `plan_tsv` writes `action\tphase\tdigest\tlabel`; `verify.sh:157-171` looks the stage up by the literal string passed to `run_stage`; an unknown label answers `RUN`. `constitution.execution_contract(label)` re-parses `verify.sh` for `run_stage "<label>"` and returns `None` when the label appears zero or more than once. **A stage has no machine identity.**

The relation that would carry obligation derivation **already exists and schedules nothing**: `selection.py:372 stages_reading(stages, substrates, paths)` answers "which declared stages does this change reach", and its own docstring says *"It is a QUERY, not a scheduler. Nothing here decides what runs."* `UVI-L-12` mandates that every stage declare a read-set precisely because *"a stage with no read-set is a stage no impact analysis can relate a change to."* The inputs exist. The consumer does not.

Also relevant: `engine/registry_coverage/matrix.py:245` — a brand-new object class has **no plane** (`plane_of_class.get(klass)` → `None`) and lands in `PARTIALLY_COVERED`, which `validate()` at `:391-424` does **not** refuse. **A new subject class degrades silently.** And `registry_coverage` is not a `run_stage` in `verify.sh` and not invoked by any workflow — its only non-package reference is its own test.

### 4.9 Security analysis

**Determination: there is no security gate on assimilation admission. Not a weak one — none.**

The complete admission contract for arbitrary bytes becoming canonical repository Truth is: *the caller declares a kind that has a registered adapter, supplies a locator the truth policy does not classify TRANSIENT, and names an eligible destination.* All three are **assertions by the submitter**. `SourceInput.create` (`pipeline.py:78-81`) validates only that `payload` is `bytes`; its docstring states outright *"Payload acquisition is the caller's business."*

Grepping `signature|trust|authoriz|authentic|credential|permission` across `platform/universal_assimilation/*.py`, `engine/uckp/assimilation.py`, `engine/constitution/assimilation.py`, `engine/knowledge/ukip/assimilation.py` returns exactly **one incidental hit**: the word "signature" at `engine/uckp/assimilation.py:781`, meaning a *function* signature.

| Control | Status | Evidence |
|---|---|---|
| Authentication | **ABSENT** | no caller identity is established at any admission boundary |
| Authorization on admission | **ABSENT in practice** | `platform/identity/policy.py:200` default-deny `"no-grant"` exists; `PolicyEngine(` is constructed in exactly one non-test place (`platform/identity/service.py:345`); no admission path builds a `Principal`/`AccessRequest`. The frozen-corpus write ban (`FROZEN_CORPUS_PREFIXES = ("00-BOOK","00-SOURCE","99-FREEZE")`, `policy.py:47`) is therefore **advisory within the identity capability only** |
| Trust / provenance | **ORPHANED** | `platform/foundation/trust.py` is complete (genesis, delegation, rotation, revocation, `verify_chain`, fail-closed). `require_trusted` has **one** caller: `admission.py:393` in `migrate_authority`. Renaming an authority requires trust; admitting content does not |
| Signature model | **STRUCTURALLY LIMITED** | symmetric HMAC-SHA256 only; `verify()` re-signs and compares (`trust.py:361`), so the verifier must hold the signing secret. A signature therefore **cannot attest external provenance to a third party**. Keyring is in-memory. No asymmetric crypto, no certificates, no X.509, no GPG anywhere |
| Integrity on admission | **ABSENT BY CONSTRUCTION** | digests are computed *from* the submitted payload and become its identity (`contracts.py:245 source_id = UCOS-USAS-<hash>`). There is no expected value, so upstream tampering is undetectable. `seal_sha256` does not exist as a Python symbol |
| Seal verification | **self-consistency only** | real re-hash-and-compare exists at `intelligence/realization/implementation.py:187` and `generation.py:113` — over artifacts **the system itself generated**. `verify_seal` result is a *report field* (`evidence.py:275`), not a gate |
| Effect enforcement | **DECLARATION-ONLY** | providers declare `fs:read`, `net:send`, `api:read`. `validation.py:619 EffectsDeclaredGate` (PC-08) checks only that each parses as `domain:action` and that `deterministic` does not co-occur with a mutating action. **No interception layer.** `constitution.py:77-78` claims the framework "refuses undeclared effects"; the code surfaces the declaration and does not refuse. A provider declaring `fs:read` may open sockets |
| Execution sandbox | **ABSENT** | `engine/runtime/execution/isolation.py` is a **dependency-graph assertion** (`isolate()` raises if an edge crosses a partition without an authorising reference frame), self-described as *"a structure only"*. No process, container, seccomp, chroot, subinterpreter or namespace boundary |
| Arbitrary code from data | **PRESENT** | `platform/universal_provider/discovery.py:372 resolve_entry_point` → `importlib.import_module(module_name)` where the name comes from a JSON descriptor field. Validation is syntactic: one `":"`, both halves non-empty, importable, callable. No allowlist, no signature, no sandbox. Reachable from CLI at `cli.py:123` |
| Security capability | **RECORD-ONLY BY DECLARATION** | `platform/security/zones.py:18-21` — *"Posture evaluation is record-only: it authorizes, ratifies, and enacts nothing (RG-02 / AR-04)"*. `zone_may_mutate()` returns a dict carrying `"enacts": False` (`:78`). `PostureRecord.non_enacting: bool = True` (`:98`). The only actual refusal in the file is a secret-shape regex on evidence text (`:130-135`) |
| Security documentation | **PROSE ONLY** | `14-SECURITY/` is exactly 5 Markdown files, no code, no schema, no gate. No security workflow among the 29 CI gates |
| Rate/size/quota limits | **ABSENT** | no bound on admission volume or payload size |
| Revocation / quarantine | **ABSENT** | all ledgers are append-only by design with no supersession-by-security-verdict path |

**Can an untrusted or unverified source be assimilated? Yes, trivially, and nothing in the codebase would stop it.**

The honest framing: **the admission fabric is a declaration-integrity and uniqueness system, not a security system.** It reliably prevents duplicate identities, non-additive provider evolution, in-place rewriting of its own sealed outputs, and silent dropping of unhomed sources. Those are real properties, competently built. They are orthogonal to trust.

Reuse assessment: **complete. `platform/foundation/trust.py` and `platform/identity/policy.py` together contain the machinery for admission authorization and provenance chaining. Both are built. Both are unwired from admission.** The one thing genuinely absent is asymmetric verification — a symmetric-HMAC scheme where verifier == signer cannot attest third-party provenance, so external-source trust is not merely unwired but not expressible with the current primitive. That is the single place in this determination where reuse may be impossible; see §11.3.

### 4.10 Duplication prevention

This is the **strongest** dimension of the fabric and also the one with the most instructive blind spots.

**`UFC-14` "Exactly Once"** (`platform/universal_foundation/constitution.py:357-372`, gate `FG-14-EXACTLY-ONCE`, scope PLATFORM) is quoted in full because its second clause is the fabric-relevant one:

> "Each constitutional model … SHALL have exactly one canonical implementation holding exactly one contract surface. Two implementations of one model is a duplicate architecture, not a choice. Within a governed package no two artifacts SHALL be byte-identical: a copy declares nothing, and therefore competes for no model and is caught by no declaration, so **duplication SHALL be measured by content and never by declaration alone.**"

The version history at `constitution.py:53-61` records that this byte-content clause was an **amendment** (1.1.0) added after a declaration-only measurement missed 36 byte-identical siblings. That is the system correcting its own blind spot — and the correction is the right one.

Companion articles: `UFC-15` "No Parallel Authority" (`:373-384`, `FG-15`) and `UFC-16` "One Subject, One Measurement" (`:385-396`, `FG-16`). All 17 articles bind their gate **inside the article**, so law and enforcement cannot drift; `__post_init__` refuses two articles declaring the same gate.

**What IS detected:**

| Class | Scope | Mechanism | Gate |
|---|---|---|---|
| Byte-identical artifacts | inside the 6 derived governed roots, grouped **globally across them** | `content_hash` of raw bytes over `rglob("*")` (`convergence.py:775-812`) | `FG-14` / `make convergence-gate` |
| Two implementations of one model | the 6 declared models | canonical owner must import-resolve and publish contracts | `FG-14` |
| Resurrected superseded surface | declared subordinates | locator must be absent from tree | `FG-15` |
| Competing constitutional definition | declared subordinates | `delegates` → import-graph check; `projection` → no executable determination; `governed` → source may contain no Foundation article/gate/constitution id | `FG-15` |
| **Semantic duplicate (same meaning, different id)** | in-memory UCKP universe | `semantic_digest` = hash of casefolded concept+definition; `registry.py:120-152` raises `DuplicateAuthorityError("this knowledge already exists under another identity")` | UCKP INV-01 probe |
| Semantic + ownership overlap + capability conflict + **near-identical parallel implementation (Jaccard ≥ 0.85)** | proposed intent vs UKDA base | `engine/knowledge/integration/duplication.py:33-34,100-175` | **no Makefile gate** |
| Duplicate canonical home | UKIP registry | `_install()` raises `DuplicateHomeError` in **both** directions | fail-closed at call |
| Stored-hash duplicates | `knowledge/canonical-knowledge.json` only | buckets the **stored** `content_sha256` field | `closure-gate` |
| Concept id as exact basename of >1 file | git-tracked repo zone | filename-stem == concept id | `closure-gate` |

**Semantic duplication IS detected — in two places — and near-duplicates too.** That is better than most systems achieve.

**What is NOT detected, and this is where the fabric gap shows:**

1. **Cross-plane duplication.** `governed_roots()` (`convergence.py:748-773`) derives roots from the 6 canonical packages' directories. `00-MASTER/`, `00-BOOK/`, `engine/`, `intelligence/`, `knowledge/` and `.github/workflows/` are **never byte-hashed by `FG-14`**. A byte-identical copy of a platform module dropped into `engine/` passes `convergence-gate`.
2. **Near-identical source duplication.** `FG-14` is exact-bytes only. One changed comment, a re-indent or a renamed symbol makes a copy invisible. The 0.85 Jaccard check exists only for CKO prose, not for code.
3. **Semantic duplication of implementations.** All semantic dedup operates on declared knowledge objects. Two modules implementing the same behaviour under different names, in different packages, with no CKO registration, are detected by nothing. *This is exactly the class that produced the two mints and the six ad-hoc `Context` classes.*
4. **Semantic duplication in the persisted store.** The 142 objects in `knowledge/canonical-knowledge.json` carry `content_sha256` but **no `semantic_digest` field** — verified by reading the store's key set. `closure_engine._ukda_hash_dups` groups by `content_sha256`, which *includes identity*, so two store objects expressing identical knowledge under different `cko_id`s are **not reported**. `CanonicalKnowledgeObject.semantic_hash()` exists and could find them; it is not wired to the standing gate.
5. **The `DuplicationEngine` is not gated.** Fail-closed only on paths that call `require`. No Makefile target invokes it; a hand-edit of the store bypasses it.
6. **Duplication among undeclared subordinates.** `FG-15` measures only surfaces listed in `foundation-convergence.json`. An undeclared parallel authority is caught only if it happens to be byte-identical to something inside a governed root.
7. **Four stores, no cross-store view.** Each of `object_birth/ledger`, `ceu/existence._admit`, `registry/universal/core` (Knowledge-Once content index) and `ukip/registry._install` holds the correct *local* mechanism. None can see another's contents.

Reuse assessment: **`engine/registry/universal/core.py:72` already maintains a `content_hash → owning universal_id` Knowledge-Once index with deny-by-default.** That is the exact data structure a cross-store duplication view requires. It is scoped to one store.

### 4.11 Impact analysis

**Two impact engines exist, they share no substrate, and only one is wired.**

`engine/verification_impact/` is the executed engine. It inverts the forward import edges of `00-MASTER/UCOS-UGA-001/01-EXECUTABLE-OBJECT-REGISTRY.json` into a reverse-dependency closure and computes affected objects, tests, evidence, certification, owners and a `Scope` (`NONE|CHANGED|INTEGRATION|FULL`). Its policy is **fail-wide**: anything not bounded by import edges escalates to `FULL`. `is_computable` distinguishes "could not compute" from "computed wide" — an honest distinction. The CLI exits 2 on escalation *so a shell cannot mistake "verify everything" for "verify nothing."*

`engine/graph/architecture/impact.py` is the richer engine: multi-source BFS over the Universal Knowledge Graph `Affects` closure, propagation-distance ranking, architectural layers reached, `capabilities_disrupted` via `CONSUMES` edges, disturbed certified surface, and a bounded 0–100 risk score. **Grep for consumers finds only its own package and its own test.** No CLI, no `verify.sh` stage, no workflow invokes it. The semantically richer blast radius is inert.

Three fabric-relevant limits:

1. **`BOUNDED_SUFFIXES = (".py",)`.** Any non-`.py` file escalates. Combined with `UNBOUNDED_PREFIXES` (`00-BOOK/DATA/`, `00-BOOK/SCHEMAS/`, `00-BOOK/tools/`, `00-CMG/`, `00-CEP/`, `pyproject.toml`, `verify.sh`, `Makefile`, `scripts/`), this means **the blast radius of adding a declaration is literally uncomputable by the executed engine** — and declarations are precisely how new subjects are admitted.
2. **Impact is triggered only by a git diff.** `changed_paths(base)` is reached once per run from `verify.sh:143`. `EvolutionController.admit`, the birth gate and `register.sh --observe` compute **no** blast radius. "Something new is added" is the case impact analysis cannot bound.
3. **It maps change → tests only.** There is no change → *validation/obligation* relation in the engine. `affected_certification` is the certification-status strings carried by touched objects, not a set of validations to run.

### 4.12 Evolution lifecycle

Four stage/position vocabularies exist with **no relation between them**:

| Vocabulary | Arity | Home | Open? |
|---|---|---|---|
| UCKP subject types | 6 | `evolution.py:138-165` | claimed open (INV-14), **materially closed** — hardcoded `Term`s, no `successors`, no validation |
| UCKP evolution stages | 15 | `evolution.py:47-79` closed `str` Enum | closed in code; published as vocabulary so extensibility is *measured* |
| UAUE loop positions | 11 | `controller.py:83-94` + `_LOOP:707` | closed in code; phase *names* come from the declaration |
| UCL lifecycle stages | 45 | `nucleus/lifecycle.py:119-166` as Python data | manifest declares itself **open**; engine contradicts it — see below |

**Three findings:**

1. **The `EvolutionLedger` is a single global successor chain.** `append` requires the first record be stage 0 of cycle 0 and every later record be exactly `next_stage(previous)`. **There is no per-subject cursor, so two subjects cannot legally occupy different stages in one ledger.** This alone makes a universal per-subject evolution lifecycle unrepresentable in the current ledger.
2. **A data/code contradiction on openness.** `ucl-stage-manifest.json` declares `open: true`, `closed_enumeration: false`, and admission as *"Append a node record to `nodes` … No engine change."* But `verify_manifest_alignment` (`lifecycle.py:204-238`) diffs the manifest against `STAGE_DECLARATIONS` **in both directions**, so appending a node without editing Python **reports a divergence**. The manifest's "no engine change" promise is not honoured by the engine that projects it. This is not a hidden bug — it is the *declared, exercised* content of `ISD-AE-01`, whose `expected: "refused"` with `expected_refusal: "present in manifest, absent from STAGES"` and gap `ISD-G-10` means **the system tests this contradiction every run and records it honestly.** That is the correct treatment of a known gap.
3. **A lifecycle for an arbitrary subject is available but vacuous.** `lifecycle.execute(subject, ...)` takes an opaque subject string and runs all 45 stages in derived order, journalling a hash chain. But the default `stage_function=satisfied_by_declaration` returns `SATISFIED` for every stage with the declaration itself as evidence and **performs no work**. Real per-stage work requires a caller-supplied `StageFunction`, and **nothing maps a subject or subject type to a stage function.** There is no stage-function registry, so *"the lifecycle ran"* and *"the lifecycle did anything"* are indistinguishable without hand-written code.

The `UAUE` loop's universality is worth quoting because it is both the strength and the limit: *"Any candidate: nothing about its class, source, owner or subject changes what happens to it."* That is universality of **shape** — and simultaneously the absence of any subject-type-specific obligation. No position consults a subject kind to decide what must be measured.


---

## 5 — WHAT ALREADY EXISTS (CONSOLIDATED)

Recorded so that no gap below is read as an absence when the component is in fact present and unwired. **This distinction is the determination's central practical claim.**

| Fabric requirement | Exists? | Located at | Wired to admission? |
|---|---|---|---|
| Pure, contention-free identity computation | **YES** | `engine/uckp/identity.py:73` | yes, for UCKP + birth |
| Deterministic derived identity | **YES** | `engine/registry/universal/identity.py:257` | yes, for CEU + 12 registries |
| Open subject-form admission | **YES** | `engine/ceu/existence.py:357 declare_form` | yes |
| Open kind-as-meta-type registration | **YES** | `engine/provider/metatypes.py:29 CATEGORY_ROLE` | yes, **providers only** |
| Bounded-open taxonomy extension | **YES** | `engine/context/taxonomy.py:516` | yes, **context only** |
| Content-addressed integrity digest | **YES** | `engine/uckp/ucko.py content_sha256` | computed, **not verified on admission** |
| Meaning-only duplicate digest | **YES** | `engine/uckp/ucko.py:322 semantic_digest` | yes in-memory; **absent from persisted store** |
| Knowledge-Once content index | **YES** | `engine/registry/universal/core.py:72` | yes, **one store only** |
| Canonical-home-with-corroboration | **YES** | `engine/knowledge/ukip/registry.py:396` | yes, **UKIP only** |
| Duplicate-home refusal both directions | **YES** | `ukip/registry.py:375 _install` | yes |
| Byte-duplication measurement | **YES** | `convergence.py:775` | yes, **6 governed roots only** |
| Near-duplicate similarity (Jaccard) | **YES** | `knowledge/integration/duplication.py:33` | **ungated** |
| Seal monopoly making a pathway mandatory | **YES** | `engine/constitution/gateway.py` + `state.py` | yes, **1 of 9 mutation classes** |
| Mutation-class decidability | **YES** | `platform/repository_intelligence/mutation_classification.py` | **no consumer anywhere** |
| Trust: genesis, delegation, revocation, chain verify | **YES** | `platform/foundation/trust.py` | **one caller, not admission** |
| Default-deny authorization | **YES** | `platform/identity/policy.py:200` | **one instantiation, not admission** |
| Frozen-corpus write ban | **YES** | `platform/identity/policy.py:47,62` | **advisory only** |
| Import-edge blast radius | **YES** | `engine/verification_impact/impact.py` | yes, **git-diff triggered only** |
| Graph blast radius with layers/capabilities/risk | **YES** | `engine/graph/architecture/impact.py` | **no consumer anywhere** |
| Change→stage relation | **YES** | `selection.py:372 stages_reading` | **"a QUERY, not a scheduler"** |
| Declared read-sets per stage | **YES** | `UVI-L-12` in `uvi-declaration.json` | yes |
| Bidirectional law↔check refusal | **YES** | `verification_intelligence/constitution.py:370` | yes |
| Supersede / resurrect / ancestry substrate | **YES** | `engine/ceu/existence.py:458,521` | yes for CEU; **not wired to taxonomy or registries** |
| Temporal validity algebra, fail-closed | **YES** | `engine/knowledge/ukip/relationships.py` | yes, **1 of 4 planes** |
| Live admission-path exercisability proof | **YES** | `engine/infinite_scope/contract.py:733` | yes — **and it is the model for the fabric** |
| Declarative onboarding by JSON manifest | **YES** | `platform/universal_provider/discovery.py:152 CatalogSource` | yes, **providers only** |
| Ten-phase atomic registration transaction | **YES** | `00-BOOK/tools/register.sh` | yes, **corpus only** |
| Subject-kind → obligations relation | **NO** | — | — |
| Cross-store identity/duplication view | **NO** | — | — |
| Admission-time impact | **NO** | — | — |
| Trust/authorization on admission | **NO** | machinery exists, binding does not | — |
| Non-document adapters (UI/API/infra/tech) | **NO** | — | — |
| Per-subject evolution cursor | **NO** | single global chain | — |
| Stage-function binding registry | **NO** | — | — |
| Machine identity for a stage | **NO** | free-text label, triple-authored | — |
| Asymmetric provenance verification | **NO** | symmetric HMAC only | — |
| Runtime effect enforcement | **NO** | declaration validated for syntax only | — |

**Count: 27 fabric components exist. 11 are absent. Of the 27 present, 9 are built and unwired.**

---

## 6 — WHAT OVERLAPS

Overlap is recorded as evidence, not corrected. Each row states whether the overlap is **duplication** (one model, two implementations — a `UFC-14` concern) or **legitimate specialization** (disjoint subjects sharing a name).

| # | Overlap | Instances | Assessment |
|---|---|---|---|
| O-1 | **Identity minting** | `engine/uckp/identity.py:73`; `engine/registry/universal/identity.py:257`; `ukb.py build --mint` | **DUPLICATION of model, legitimated by declaration.** `MULTIPLE_INDEPENDENT_BOUNDED_NAMESPACES` is declared at `constitutional-authority-alignment.json:581`. Consistent, but incompatible with "one universal pathway" at the identity layer |
| O-2 | **Duplication detection** | `object_birth/ledger.append`; `ceu/existence._admit`; `registry/universal/core:72`; `ukip/registry._install`; plus `convergence.measure_duplication`, `closure_engine` ×2, `knowledge/integration/duplication` | **PARTLY LEGITIMATE.** Each store must guard its own writes. What is missing is not fewer guards but **one view across them** |
| O-3 | **`AssimilationReport` class name** | `platform/universal_assimilation/contracts.py`; `engine/uckp/assimilation.py` | **NAME COLLISION across the island boundary.** Two unrelated types, identical name, no relation. Neither surface's duplication machinery can see the other |
| O-4 | **Assimilation pathway** | `platform/universal_assimilation/pipeline.py`; `engine/uckp/assimilation.py`; `engine/knowledge/ukip/assimilation.py`; `00-MASTER/UAKOS-CLOSURE-008/assimilation_engine.py` | **FOUR implementations of "assimilation."** `MODEL-ASSIMILATION` in `foundation-convergence.json` names only the first as canonical, with `adapters.py` as its sole delegating subordinate. The other three are **not declared subordinates**, so `FG-15` does not measure them |
| O-5 | **Stage / lifecycle vocabularies** | 6 subject types · 15 evolution stages · 11 UAUE positions · 45 UCL stages (+ 9 UCDA decision, 8 wave, 26-step chain) | **LEGITIMATE SPECIALIZATION, ILLEGITIMATELY UNJOINED.** `ucl-gate.yml` crosswalks five lifecycle owners deliberately. What is absent is the join key, not a merge |
| O-6 | **Kind vocabularies** | `SourceKindRegistry` (14); provider `kind` (open string, 14 declared); schema families (19 schemas) | **DUPLICATION of the *concept* "kind of thing", three times, unjoined** |
| O-7 | **Context types** | universal `engine/context/` + ≥10 ad-hoc `Context`/`*Context` classes | **DUPLICATION.** `MODEL-TRUTH`/`MODEL-ASSIMILATION` do not list these as subordinates, so `FG-15` cannot see them |
| O-8 | **Impact engines** | `engine/verification_impact/`; `engine/graph/architecture/impact.py` | **DUPLICATION of model** (blast radius), different substrates, one unwired |
| O-9 | **Capability lifecycle** | 7 band-local sites (`application/`, `service/`, `infrastructure/`, `platform/foundation/`, `platform/universal_control_plane/`, `engine/nucleus`, `engine/uicm`) | **DUPLICATION**, recorded as ownership-ambiguous in the coverage matrix |
| O-10 | **Maturity models** | 8-level lattice; 14-axis vector; 7-state claim of exclusivity | **DUPLICATION**, registered as `G-19`; `IMPLEMENTED`/`VALIDATED`/`CERTIFIED` appear in more than one with different arities and nothing maps them |
| O-11 | **`FROZEN_PREFIXES`** | `engine/foundation/guards/frozen_paths.py:33`; `platform/identity/policy.py:47` (as `FROZEN_CORPUS_PREFIXES`) | **DUPLICATION**, registered as `G-18` |
| O-12 | **Entity-kind vocabularies** | `birth-scope-policy.json` kinds; `engine/uaue ObjectKind` | **DUPLICATION**, no reconciling registry |
| O-13 | **Registration planes** | CORPUS (`artifacts.json`) and REPOSITORY (`id-ledger.json`) | **LEGITIMATE** — declared as two planes in `registry_coverage/declarations.json`, with `object_class → plane` mapping |

---

## 7 — WHAT SHOULD BE UNIFIED

Five items. For each: what unifies, **which existing surface would carry it**, and why unification is warranted rather than optional. No new engine is named in this section.

### 7.1 Subject-kind identity — the keystone

**Unify:** the three kind vocabularies (O-6) into one register where a *kind* is a first-class registered subject with an identity, an owner, an authority path, and a declared realisation requirement.

**Existing carrier: `engine/provider/metatypes.py`.** The mechanism is already correct and already proven open at runtime: `CATEGORY_ROLE = "provider-category"` marks a meta-type as a category; `framework.py:139-142 categories()` *derives* the category set by filtering kernel meta-types rather than enumerating them; `register_category()` admits any key; and `engine/provider/compliance.py:176-231` registers `"NeverSeenProviderCategory"` and `"WhollyNovelProviderCategory"` every run and asserts they are admitted, discoverable and resolvable. **That is a working universal kind register whose scope is the word "provider."**

**Why unification is warranted, not optional:** without a kind identity, obligation derivation (§7.2), impact on admission (§7.3) and cross-store reconciliation (§7.5) each have no key to hang on. Every other unification depends on this one.

### 7.2 Kind → obligations derivation

**Unify:** obligation discovery so that admitting a *kind* determines which validations apply, instead of validations being hand-authored per stage in three to five places with a free-text label as the join key.

**Existing carriers, both already built:**
- `UVI-L-12` already **mandates** that every stage declare a read-set, with the stated reason *"a stage with no read-set is a stage no impact analysis can relate a change to."*
- `selection.py:372 stages_reading` already **computes** which declared stages a change reaches, and declares itself *"a QUERY, not a scheduler."*
- `verification_intelligence/constitution.py:370-381` already implements the **bidirectional refusal** pattern that the fabric needs: a law naming an unimplemented check and a check no law claims are both faults. Applied to kinds, this reads: *a kind naming an unimplemented obligation, and an obligation no kind claims, are both faults.*

**Why warranted:** today a new subject kind acquires **no** validations, and `registry_coverage/matrix.py:245` places an unknown object class in `PARTIALLY_COVERED`, which `validate()` does not refuse. **A new kind degrades silently.** That is the precise inverse of the fail-closed posture the rest of the system maintains.

### 7.3 Admission-time impact

**Unify:** blast radius so that it is computed when something is *admitted*, not only when a `.py` file changes in a git diff.

**Existing carriers:** both engines exist. `engine/graph/architecture/impact.py` — layers, capabilities disrupted, certified surface disturbed, bounded risk score — is **entirely unwired** and is the semantically appropriate one for admission, because admission changes the knowledge graph rather than the import graph.

**Why warranted:** the executed engine's own policy makes admission uncomputable — `BOUNDED_SUFFIXES = (".py",)` plus `UNBOUNDED_PREFIXES` covering `00-BOOK/DATA/`, `00-BOOK/SCHEMAS/` and `00-CMG/` means **every declaration-shaped admission escalates to FULL rather than resolving.** Fail-wide is honest but undifferentiated: it runs *more of the existing* validations and never derives a *new* obligation. Meanwhile the engine that could bound a knowledge-graph change is inert.

### 7.4 Trust and authorization binding on admission

**Unify:** one authorization decision point on every admission surface, and one provenance requirement on every external source.

**Existing carriers:** `platform/identity/policy.py` (default-deny `"no-grant"`, four hard invariant guards, frozen-corpus write ban) and `platform/foundation/trust.py` (genesis anchor, delegation, rotation, revocation, `verify_chain`, fail-closed). **Both complete. Both unwired from admission.** `require_trusted` guards authority renaming and nothing else.

**Why warranted:** this is the only dimension where the current state is not merely incomplete but *inverted*. The system enforces that an authority cannot be renamed without a trusted key, while any caller may submit arbitrary bytes for assimilation as canonical Truth, and a JSON descriptor field is sufficient to trigger `importlib.import_module` of a named module with no allowlist and no sandbox (`discovery.py:372`). The asymmetry is not defensible on any threat model.

**Partial reuse limit:** the trust primitive is symmetric HMAC where verification re-signs and compares, so the verifier must hold the signing secret. **External provenance is not expressible with it.** See §11.3.

### 7.5 Cross-store identity and duplication view

**Unify:** one read-only view across the four admission stores answering *"is this subject, or this content, or this meaning, already present anywhere?"*

**Existing carriers:**
- `engine/registry/universal/core.py:72` already holds a `content_hash → owning universal_id` Knowledge-Once index with deny-by-default — the exact data structure required, scoped to one store.
- `engine/uckp/ucko.py:322 semantic_digest` already separates meaning from integrity — the correct key for cross-store *semantic* reconciliation. It is **absent from the persisted store's schema**, which is why `closure-gate` cannot see semantic duplicates among the 142 objects.
- `engine/infinite_scope/contract.py:733` already demonstrates the *pattern* for reading across owners: resolve the other owner's document, deliver it through **the owner's own declared reader**, and reconcile declared against measured in both directions.

**Why warranted:** an object can today hold a birth record, a CEU existence unit, a typed registration and a corpus ID under three different identifiers with no surface detecting it. `UFC-14` forbids two implementations of one model; nothing forbids four identities of one subject, because no measurement spans the stores.

---

## 8 — WHAT SHOULD REMAIN SPECIALIZED

Equally important to the determination, and stated with the same weight. Unification here would be a regression.

| # | Should remain specialized | Why |
|---|---|---|
| S-1 | **The seven document adapters** | `SourceAdapter.can_handle` + fail-closed `select()` is the right shape. A docx and a PDF genuinely need different normalisers. The gap is *missing* adapters for non-document kinds, **not** a missing universal adapter. A single universal normaliser would be a god-object |
| S-2 | **The four relationship planes** | `UCRD-001` §5 declares them disjoint and **explicitly rejects** "everything is a relationship". That rejection is a considered architectural position. The gap is *propagation* of validity and context across planes, not a merge of the planes |
| S-3 | **Per-class mutation authority chains** | Nine mutation classes with eight authority chains, each naming exactly one primary. Collapsing them would put source edits, corpus registration and constitutional truth under one gate — which the `mutation-governance-boundary.json` Option B determination explicitly argues against on structural grounds (`gateway.py` has no filesystem at all) |
| S-4 | **`required_attributes` per typed registry** | 12 registries with domain-specific required attributes (`api → {contract, protocol}`, `infrastructure → {provider}`, `dependency → {source, target}`). This is exactly correct: a universal required-attribute set would be either empty or wrong |
| S-5 | **Band 11/12/13 technology neutrality** | `_TECHNOLOGY_MARKERS` rejecting `openapi`, `grpc`, `kubernetes`, `http://` in `service/`, `application/`, `infrastructure/` is a *deliberate* constitutional position (USL-15 / UIL-15). The fabric gap is that **no other zone can hold a concrete technology either** — the answer is a place for concrete technology, not weakening the ban |
| S-6 | **The gateway's absence of a filesystem** | `engine/constitution/gateway.py` reads no clock, no filesystem, no network. That purity is what makes its seal monopoly sound. Extending it to govern source files would destroy the property that makes it trustworthy |
| S-7 | **`register.sh` as a separate transactional plane** | Ten phases with declared atomicity and a two-plane split (`--observe` read-only vs the mutating transaction) correctly separates "is registration valid?" from "perform registration". Its own header states *"a verification path that writes is not a verification path"* |
| S-8 | **Two-plane registration (CORPUS / REPOSITORY)** | Documents and executable objects have genuinely different registration semantics; the declared `object_class → plane` mapping is the right abstraction |
| S-9 | **Verdict vocabulary plurality** | Already adjudicated as intentional (option C) by `PHASE-VERDICT-VOCABULARY-TAXONOMY-DETERMINATION.md`, on the reasoning that no consumer reads two surfaces' verdicts and reconciles them semantically |
| S-10 | **`platform/security/` as record-only** | A posture ledger that authorizes nothing is a legitimate and honest design *if* an enforcement point exists elsewhere. The gap is the missing enforcement point (§7.4), **not** that the ledger should start enacting |

---

## 9 — MISSING UNIVERSAL SUBSTRATE

Ten absences, ordered by whether the fabric can exist without them.

### 9.1 Foundational — the fabric cannot exist without these

**M-1 — A subject-kind register.** No universal answer to "what kind of thing is this?" Three unjoined vocabularies. **Keystone: every other item depends on it.** Existing pattern: `engine/provider/metatypes.py`.

**M-2 — A kind → obligations relation.** Obligations attach to stages, never to kinds. A new kind acquires no validations and degrades to non-blocking `PARTIALLY_COVERED`. Existing raw material: declared read-sets + `stages_reading` + the bidirectional law↔check refusal pattern.

**M-3 — An admission authorization point.** No authn, no authz, no trust, no provenance, no integrity verification on any admission path. Existing machinery: `platform/identity/policy.py` + `platform/foundation/trust.py`, both orphaned.

### 9.2 Structural — the fabric would be unsound without these

**M-4 — A cross-store identity and duplication view.** Four stores, four correct local mechanisms, no shared view. Semantic duplicates in the persisted store are undetectable because `semantic_digest` is absent from its schema.

**M-5 — Admission-time impact.** Impact runs on git diff only; declaration-shaped admissions are uncomputable by the executed engine; the engine that could bound them is unwired.

**M-6 — Adapters for non-document categories.** Every admission path terminates in a document/record normaliser. UI, API, infrastructure and technology have no normaliser, so declaring their kinds leaves `select()` failing closed. **This is the one gap that may require new code rather than new wiring** — though not a new *engine*; see §11.2.

### 9.3 Operational — the fabric would work but not scale or evolve

**M-7 — A per-subject evolution cursor.** `EvolutionLedger` is a single global successor chain; two subjects cannot occupy different stages. A universal per-subject lifecycle is unrepresentable in it.

**M-8 — A stage-function binding registry.** `lifecycle.execute` accepts any subject and the default stage function performs no work, so *"the lifecycle ran"* and *"the lifecycle did anything"* are indistinguishable. Nothing maps a kind to its per-stage work.

**M-9 — A machine identity for a stage.** The join key is a free-text label triple-authored across `uvi-declaration.json`, `verify.sh run_stage`, `validation-record.json` and `uisd-gate.yml`; an unmatched label degrades to `RUN`/`None` rather than to a bound obligation.

**M-10 — A closing ratchet for new object classes.** `registry_coverage` is the only coverage instrument, is not executed by `verify.sh` or any workflow, and classifies an unknown class as non-blocking.

### 9.4 The realisation dead end — cross-cutting

Present in both the provider catalog and the assimilation registry, and worth naming separately because it is the same shape twice:

**Declaration can admit; only code can activate.** `platform/providers/catalog/declared-providers.json` declares 14 provider kinds; its own `manifest_note` states *"none declares an entry_point yet, so each certifies CERTIFIED-PROVISIONAL and is refused activation until an implementation is pointed at it."* `TEMPLATE.provider.json` documents onboarding as *"no framework module changes, no interface is added, no kind is registered anywhere in code"* — and then requires `entry_point` to point at a module exposing `build(descriptor, config)`. Likewise a declared source kind with no adapter class is admitted to the vocabulary and cannot be assimilated.

**This is not necessarily a defect.** Declaring a thing and implementing it are legitimately different acts, and 13 provisional stubs refused activation is *correct* fail-closed behaviour. It is recorded because it bounds what "admission by declaration" can mean: **declaration reaches identity, capability surface and governance; it does not reach behaviour.**

---

## 10 — DETERMINATION REGISTER

Findings `D-01` … `D-14`. Observations, not requirements. Not resolved here.

**D-01 — Four admission stores, no cross-store view.** An object may hold a birth record, a CEU unit, a typed registration and a corpus ID under three identifiers; no surface detects it. Sources: `object_birth/ledger.py:93`, `ceu/existence.py:333`, `registry/universal/core.py:72`, `ukip/registry.py:375`. Impact: `UFC-14` forbids two implementations of one model but nothing forbids four identities of one subject. Disposition: RECORDED.

**D-02 — Two identity mints, verified independent.** `engine/uckp/identity.py:73` and `engine/registry/universal/identity.py:257`; neither imports the other (verified by grep in both directions). `second_authority_test` is counter-shaped (`mint_markers: ["category_seq"]`), so mint #2 passes it while issuing identifiers. The declaration acknowledges this as `MULTIPLE_INDEPENDENT_BOUNDED_NAMESPACES`. Disposition: RECORDED. Consistent by declaration; incompatible with a single universal pathway at the identity layer.

**D-03 — Assimilated identities bypass identity validation.** `engine/uckp/assimilation.py:307` uses `urn_for` (`identity.py:57`), unvalidated string interpolation, rather than `mint()` with `_NAMESPACE_RE`/`_LOCAL_RE`. Impact: assimilated artifact identities are not subject to the well-formedness law that minted ones are. Disposition: RECORDED.

**D-04 — The universal assimilation module is an island.** `grep -rn "uckp|object_birth|ceu\." platform/universal_assimilation/*.py` → no matches; nothing in `engine/` imports it. Its docstring claims "one road for every source." Disposition: RECORDED.

**D-05 — `engine/object_birth/` has zero production importers.** Reachable only as `python -m engine.object_birth.gate`. Nothing calls `birth()` to mint an object. Impact: the "identity before existence" contract is measured but not exercised by the system it governs. Disposition: RECORDED.

**D-06 — No security control on admission.** No authn, authz, trust, provenance or integrity verification on any admission path. `require_trusted` has one caller (`admission.py:393`, authority migration). `PolicyEngine` has one instantiation (`identity/service.py:345`). `discovery.py:372 resolve_entry_point` imports a module named in a JSON field with no allowlist or sandbox. Declared provider effects are validated for *syntax* only. Disposition: RECORDED. **Highest-consequence finding in this determination.**

**D-07 — Digest verification is structurally impossible on admission.** Digests are computed from the submitted payload and become its identity; no expected value exists to compare against. Real re-hash-and-compare exists only over the system's own generated outputs. `seal_sha256` is not a Python symbol. Disposition: RECORDED.

**D-08 — Cross-plane duplication is undetected.** `governed_roots()` derives roots from six canonical packages; `00-MASTER/`, `00-BOOK/`, `engine/`, `intelligence/`, `knowledge/` are never byte-hashed by `FG-14`. A byte-identical copy of a platform module placed in `engine/` passes `convergence-gate`. Disposition: RECORDED.

**D-09 — Semantic duplication in the persisted store is undetected.** The 142 objects in `knowledge/canonical-knowledge.json` carry `content_sha256` but no `semantic_digest`. `_ukda_hash_dups` groups by `content_sha256`, which includes identity. `CanonicalKnowledgeObject.semantic_hash()` exists and is not wired to the standing gate. Disposition: RECORDED.

**D-10 — The mutation classifier has no consumer.** `mutation_classification.py` is decidable and ungated; `UNRESOLVED` *"must never be read as a permissive default"* yet no consumer exists to read it. `R-09 GOVERNED_ANALYSIS` is declared with no implementing predicate. Disposition: RECORDED.

**D-11 — Two impact engines, one substrate each, one unwired.** `engine/graph/architecture/impact.py` (layers, capabilities, certified surface, risk) has no CLI, no stage, no workflow. The executed engine declares declaration-shaped changes uncomputable. Disposition: RECORDED.

**D-12 — Openness data/code contradiction, honestly exercised.** `ucl-stage-manifest.json` declares `open: true` and admission as "append a node, no engine change"; `verify_manifest_alignment` diffs it against 45 Python literals in both directions, so appending refuses. This is the declared content of `ISD-AE-01` with `expected: "refused"` and gap `ISD-G-10`. Disposition: RECORDED. **Noted as exemplary treatment of a known gap** — the contradiction is measured every run rather than hidden.

**D-13 — A universal lifecycle for an arbitrary subject is available but vacuous.** `lifecycle.execute` accepts any subject; the default stage function returns SATISFIED with the declaration as its own evidence and performs no work; nothing maps a kind to a stage function. `EvolutionLedger` has no per-subject cursor. Disposition: RECORDED.

**D-14 — Four of thirteen directive categories are absent or schema-only.** API/protocol ABSENT and actively rejected by `_TECHNOLOGY_MARKERS`; UI/UX schema-only with zero instances and no writer; infrastructure ABSENT; technology partial and code-or-schema-bound. Disposition: RECORDED.

**Prior findings carried unchanged, not re-numbered:** `ISD-G-04` (no enforcement over the 12,899-edge UKB surface), `ISD-G-10`, `P4-F-002`, `P4-F-006`, `P4-F-009`, `AD-G-01`, `AD-G-03`, `AD-G-05`, `G-18`, `G-19`, `RU-G-01`, `CR-04`, `CR-09`, `CR-10`, `H-01`, `H-06`, `UCL-F-006`.

---

## 11 — REUSE DETERMINATION

The directive binds this determination: **no new engine unless reuse is impossible.** Assessed per gap.

### 11.1 Reuse sufficient — wiring only, no new component (7 of 10)

| Gap | Existing component to carry it | Nature of the work |
|---|---|---|
| M-1 subject-kind register | `engine/provider/metatypes.py` (category-as-meta-type, proven open at runtime) | **generalise scope**, from "provider" to "subject" |
| M-2 kind → obligations | `UVI-L-12` read-sets + `selection.py:372 stages_reading` + `constitution.py:370` bidirectional refusal | **wire the existing query to a scheduler**; apply the existing refusal pattern to kinds |
| M-3 admission authorization | `platform/identity/policy.py` + `platform/foundation/trust.py` | **wire two complete, orphaned components to the admission surfaces** |
| M-4 cross-store view | `registry/universal/core.py:72` Knowledge-Once index + `ucko.py:322 semantic_digest` + `infinite_scope` cross-owner reading pattern | **widen an existing index; add the existing digest to the persisted schema** |
| M-5 admission-time impact | `engine/graph/architecture/impact.py` (complete, inert) | **wire an existing engine to an existing trigger point** |
| M-7 per-subject cursor | `engine/uckp/evolution.py` ledger; `engine/ceu/existence.py` supersede/ancestry already per-subject | **the per-subject mechanism exists in CEU; the ledger needs a key, not an engine** |
| M-10 new-class ratchet | `engine/registry_coverage/` (built, unexecuted) | **execute the existing instrument and make its unknown-class case blocking** |

### 11.2 Reuse partial — new code, but not a new engine (2 of 10)

**M-6 non-document adapters.** The `SourceAdapter` contract, the registry and the fail-closed `select()` all exist and are the right shape. What is missing is *instances* — a normaliser for a UI screen, an API contract, an infrastructure resource. **This is new adapter code inside an existing framework, not a new engine.** It also has a prerequisite this determination must flag: `_TECHNOLOGY_MARKERS` currently rejects concrete API/UI/infra tokens in bands 11/12/13, so there is no zone permitted to *hold* the admitted result. That is a governance question reserved to the band owners, not an engineering one.

Note the one-way asymmetry that makes this tractable: `intelligence/realization/generators/api.py` already **emits** OpenAPI contracts from canonical knowledge, and `realization/api/*_routes.py` are framework-neutral route tables. The system can already express an interface; it has no inverse of `_openapi()`.

**M-8 stage-function binding.** `lifecycle.execute` already accepts a caller-supplied `StageFunction`, and `_LOOP` already resolves phase names through the declaration. What is absent is a **lookup table** from kind to stage function. A registry of functions is not an engine.

**M-9 machine identity for a stage.** Stages already have `id`, `label`, `phase`, `plane`, `depends_on`, `read_set`, `owner` in `uvi-declaration.json`. The `id` exists; the *join* uses the label. **Using the existing id as the join key is a wiring change**, with a documented cost: the "three-reader contract" means the label appears in four places by design, and changing the join key touches all four.

### 11.3 Reuse possibly impossible — one candidate, and only one

**Asymmetric provenance verification.** `platform/foundation/trust.py` is symmetric HMAC-SHA256 where `verify()` re-signs and compares, requiring the verifier to hold the signing secret. This is sound for internal delegation chains, which is what it is used for. It **cannot** attest that an *external* source is what it claims to be, because there is no separation between signer and verifier. External-source provenance is therefore not merely unwired but **not expressible with the existing primitive.**

Determination: **this is the only gap in the analysis where reuse appears genuinely impossible.** Whether it warrants a new component depends on a question this determination does not have the authority to answer — whether UCOS Ω∞ is required to assimilate sources it does not itself produce. If every source is internally produced, the symmetric primitive is sufficient and no new component is needed. If external sources are in scope (and the presence of `conversation-export`, `document-pdf`, `api-response` and 14 provider kinds among the declared source kinds suggests they are), then a verification primitive that does not require the verifier to hold the signer's secret is required.

**Recorded as a question reserved to authority, not as a proposal.** No component is named, no design is offered, no work is authorized.

### 11.4 Summary

| Category | Count | Items |
|---|---|---|
| Wiring only, component exists | **7** | M-1, M-2, M-3, M-4, M-5, M-7, M-10 |
| New code inside an existing framework | **3** | M-6, M-8, M-9 |
| Possibly requires a new primitive | **1** | asymmetric provenance verification (§11.3) |
| **New engines determined necessary** | **0** | — |

**The fabric is not missing engines. It is missing wiring between engines that exist, and nine of its twenty-seven present components are built and unconnected.**

---

## 12 — FINAL DETERMINATION

```
UNIVERSAL ASSIMILATION FABRIC — STATE AT HEAD bae59755

  One universal pathway .................... DOES NOT EXIST
      admission surfaces located ............ 14
      structurally independent islands ...... 3
      genuine bridges between them .......... 1
        (object_birth → uckp/identity)
      identity mints ........................ 2, verified independent
      duplication stores .................... 4, no shared view
      kind vocabularies ..................... 3, no join key

  Categories admissible today .............. 6 of 13 fully
      entity · artifact · capability ·
      principle · knowledge object ·
      future unknown construct
    derived ................................. 1  (requirement)
    partial ................................. 3  (technology · provider · intelligence)
    absent .................................. 3  (API/protocol · UI/UX · infrastructure)

  Security on admission .................... NONE
      authentication ........................ ABSENT
      authorization ......................... machinery exists, unwired
      trust / provenance .................... machinery exists, one unrelated caller
      integrity on admission ................ impossible by construction
      effect enforcement .................... declaration validated for syntax only
      execution sandbox ..................... ABSENT
      arbitrary code from a data file ....... PRESENT (resolve_entry_point)

  Duplication prevention ................... STRONGEST DIMENSION
      byte-identical, semantic, near-dup .... all three detected
      cross-plane ........................... NOT detected
      semantic in persisted store ........... NOT detected
      implementation-level semantic ......... NOT detected

  Unknown-space admission .................. MEASURED OPEN
      by 4 independent instruments, over the declared surface
      undeclared surface .................... NOT ASSESSED (AD-G-01)

  Missing universal substrate .............. 10 items
      foundational .......................... 3  (M-1, M-2, M-3)
      structural ............................ 3  (M-4, M-5, M-6)
      operational ........................... 4  (M-7, M-8, M-9, M-10)

  New engines determined necessary ......... 0
      wiring only ........................... 7
      new code, existing framework .......... 3
      possibly a new primitive .............. 1  (asymmetric provenance)

  Fabric determination ..................... BINDING LAYER MISSING,
                                             ENGINES SUFFICIENT
```

### 12.1 The determination in plain terms

The repository has built the hard parts. Identity as pure computation, meaning separated from integrity, openness measured by live probe rather than asserted in a comment, fail-closed as the default, and a seal monopoly that makes a pathway mandatory by leaving nothing at the end of the bypass path — these are not common properties and they are correctly built here.

What it has not built is the thin layer that makes those parts one thing. The evidence for this is specific rather than rhetorical: **nine complete components sit unwired** — two orphaned security engines, an inert impact engine, an unconsumed mutation classifier, an unexecuted coverage ratchet, an unscheduled change→stage query, an ungated duplication engine, a supersession substrate not connected to the taxonomy it could serve, and a semantic digest absent from the store that needs it.

A fabric determination that responded to this by proposing a fifteenth engine would be adding a fifth implementation of assimilation to a repository that already has four, and `UFC-14` names that outcome precisely: *"Two implementations of one model is a duplicate architecture, not a choice."*

### 12.2 What this determination does not determine

- It does not determine that the missing substrate **should** be built. That is reserved to authority.
- It does not determine priority, sequence, or ownership for any gap.
- It does not resolve any contradiction, alter any classification, or change any certification state.
- It does not determine whether external-source assimilation is in scope — the question on which §11.3 turns.
- It does not determine that the absent categories (API, UI, infrastructure) *ought* to be admissible. Their absence may be intentional; `_TECHNOLOGY_MARKERS` suggests at least part of it is. **Three located positions in the repository recommend against building a surface merely to become certifiable**, and that reasoning applies here unchanged.

### 12.3 Self-assimilation observation

This document is derived analysis, authority NONE, untracked and unregistered at creation — absent from `artifacts.json`, both `id-ledger.json` indices, and `generated-artifact-registry.json`, consistent with the `CR-10` pattern. Its applicable mutation class would be `GOVERNED_ANALYSIS`, whose rule `R-09` **has no implementing predicate**, so its class is **UNDECIDABLE by located machinery at this HEAD**. It does not self-classify. It sits inside the governance void that `UNIVERSAL-ARTIFACT-LIFECYCLE-DETERMINATION.md` §3.2 declares over determination documents. Registration was not performed, because registration mints an identity and allocates a page range, which the mode of this determination forbids.

---

## 13 — STOP

Determination written. Execution halted here.

**Not performed and not authorized:** implementation · new engine creation · remediation · wiring of any orphaned component · security binding · adapter authoring · registry creation · identity minting · programme-ID creation · requirement creation · ADR creation · contradiction resolution · classification change · certification change · any modification to source, configuration, registry, ledger, declaration or workflow.

**Awaiting explicit authorization.**

---

*End of determination. Authority: NONE — DERIVED TRUTH. Mode: ASSIMILATION ONLY. Mutation: READ ONLY OBSERVATION (single file created). Baseline: HEAD `bae59755` · branch `integration/recovery-001`.*
