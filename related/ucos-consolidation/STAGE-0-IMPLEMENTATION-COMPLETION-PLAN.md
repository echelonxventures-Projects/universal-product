# STAGE-0 IMPLEMENTATION COMPLETION PLAN

**Baseline:** HEAD `a5ff49a` · branch `integration/recovery-001`
**Basis:** existing repository truth, existing engines, existing registries, existing evidence. No new discovery performed.
**Rule applied throughout:** REUSE BEFORE CREATE. Every row names an existing owner where one exists. `CREATE` appears only where a repository-wide search returned nothing.

**Reuse ratio of this plan: 71 of 86 work items are EXTEND or REFACTOR of a located asset. 15 are CREATE.**

---

## 1. EXISTING ASSETS TO REUSE

These are built, tested and measured. Stage-1 consumes them unchanged. **Nothing here is to be rebuilt.**

| Asset | Canonical Owner | Existing Implementation | Reuse As |
|---|---|---|---|
| Entity model | `engine/uckp/law.py:424` | `GOVERNED_CATEGORIES` 35 members, open by Art. 17, fail-closed at `ucko.py:392` | The one definition of "constitutional entity" |
| Universal object model | `engine/uckp/ucko.py` | `UniversalConstitutionalKnowledgeObject`, 34 facets | The record every nucleus/capability/object instantiates |
| Identifier minting | `engine/registry/universal/identity.py:154` | `deterministic_id` → `UCOS-<CODE>-<12hex>`, `parse_kind` verifier | The single minting path |
| Canonical hashing | `engine/uckp/canonical.py` | `canonical_json`, `content_hash` (UCKP-LAW-0001 Art-13) | The only serialization primitive |
| Registration authority | `engine/registry/universal/core.py`, `registries.py:267` | `RegistryCore` + `UniversalRegistryPlatform`, 13 typed registries, hash-chained audit | The single write authority |
| Term dictionary | `engine/uckp/vocabulary.py` | 13 vocabularies, 204 terms, append-only, `require()` fail-closed, `verify_vocabulary_alignment` | The only vocabulary authority |
| Ordering authority | `engine/foundation/composition/ordering.py` | `derive_order`, `dependency_layers`, `parallel_waves`, `unresolved_keys`, strategy registry | The only composition ordering |
| Context resolution | `engine/context/` (UCXI-000001) | 14 parts, `ContextKind` 15, `ContextAuthority` 5-level total order, equal-authority refused | The context substrate all axes plug into |
| Nucleus contract | `platform/universal_foundation/catalog/foundation-nucleus.json` | `UCOS-UNC-001`, 36 facets NF-01…NF-36, gate `FG-17-NUCLEUS-COMPLETE` | The nucleus completeness contract |
| Capability register | `platform/universal_foundation/catalog/foundation-capabilities.json` | 7 capabilities, 100% CONFORMANT | The Ω Nucleus register to expand |
| Capability intelligence | `intelligence/UCOS-RIE-CAPABILITY-CATALOG.json` | 110 capabilities discovered, `authority: NONE` | The discovery input for register expansion |
| Lifecycle engine | `00-MASTER/UCL-000001/ucl_engine.py` | 45 stages discovered, ordered, 0 cycles, all owned+authorized | The lifecycle every object runs |
| Composition root | `platform/universal_control_plane/discovery.py:194` | `ControlPlane.discover()`, `REQUIRED_ENGINES` completion gate | The single boot path |
| Durable replay | `platform/universal_control_plane/durable.py` | hash-chained NDJSON journal, state reconstructed | Replay for every object |
| Linkage | `platform/universal_control_plane/linkage.py` | 9 linkages per subject, each a target identity | Per-object closure check |
| Anti-lock-in proof | `engine/civilization/compliance.py:47`, `engine/kernel/compliance.py:42`, `engine/provider/compliance.py:34` | 21 + 21 + 12 prohibited tokens, 11 `PROOF_CATEGORIES`, 8 `FORBIDDEN_DIMENSION_KEYS` | The zero-hardcoding enforcement |
| Provider framework | `engine/provider/` | 11 categories govern-registered, kernel byte-unchanged | Technology neutrality for all Stage-1 adapters |
| Dimension registry | `engine/civilization/dimensions.py` | open registry; no dimension may legislate its own bound | Where Location/Calendar/Unit register |
| Micro-nucleus contract | `UMN-001` §Deliverable 6 | rules C-1…C-9, 7-level configuration inheritance | Composition law for nuclei→universes→platforms |
| Nucleus taxonomy | `UNAF-001` §2.2–§2.8 | 79 nuclei (11 REUSE, 55 EXTEND, 1 CREATE, 12 UNIVERSE) | The nucleus population to realize |
| Implementation order | `UNAF-001` Deliverable 10 | Tier 0 → Tier 7 topological order | **The Stage-1→Production sequence. Do not re-derive.** |
| Test + coverage harness | `pyproject.toml`, `verify.sh` | 9,562 tests, 94.64%, gate ≥ 90% | Success-criteria measurement for every item |
| Determinism harness | `engine/determinism/reproduce.py` | hermetic double-build; absent category forced `False` | Fixed-point proof for every item |
| 27 CI gates | `.github/workflows/` | per-programme fail-closed gates | Where new gates are added, not invented |

---

## 2. CANONICAL COMPONENTS

The declared single authority per concern. Every Stage-1 artifact must reach these and no substitute.

| Concern | Canonical Component | Evidence of canonicity | Consumers today |
|---|---|---|---|
| Entity categories | `engine/uckp/law.py::GOVERNED_CATEGORIES` | Art. 2; open by Art. 17 | `ucko.py:392` fail-closed |
| Object record | `engine/uckp/ucko.py::UniversalConstitutionalKnowledgeObject` | 34 facets; 9/9 required attributes present | UCKO population 3,359 |
| Identifier grammar | `engine/registry/universal/identity.py` | `ID_PREFIX`, `_KIND_CODES` 13, digest 12 | `intelligence/kernel/ids.py:21`, `engine/context/model.py:187` |
| Hash primitive | `engine/uckp/canonical.py::content_hash` | "exactly one definition"; `identity.py:113` aliases, never forks | all |
| Registry write | `engine/registry/universal` | "the one place an artifact becomes Repository Truth" | 2 lawful consumers |
| Register union (derived) | `00-BOOK/MASTER-BOOK/UMB-005` 7 registers | "DERIVED, never authoritative"; "exactly one identity authority" | `00-BOOK/DATA/*` |
| Vocabulary | `engine/uckp/vocabulary.py` | append-only + fail-closed + alignment-verified | 9 engine projections |
| Ordering | `engine/foundation/composition/ordering.py` | "single ordering authority"; `register_strategy` raises on re-registration | 4 files |
| Context | `engine/context/` | `ContextAuthority` total order; equal authority refused (CXL-07) | catalog 15 kinds |
| Nucleus completeness | `platform/universal_foundation/nucleus.py:72` | `FG-17-NUCLEUS-COMPLETE`; "does not introduce a second registry" | `constitution.py:410` |
| Layer vocabulary | `ucos.architecture-layer` (14 terms) | governed, open, append-only | **to be named canonical — see §3** |
| Governance | `00-CMG/CMG-000001` → `00-CEP/CEP-000…010` → `engine.governance` | CEP-002:59 supremacy chain | `platform/universal_control_plane/governance.py` delegates |
| Lifecycle | `00-MASTER/UCL-000001` | 45 stages; "creates no stage"; `AUTHORITY = NONE` | ACEE-000001 consumes |
| Composition root | `platform/universal_control_plane::ControlPlane.discover` | "one call composes every engine below" | `REQUIRED_ENGINES` gate |
| Boot admission | `platform/runtime_platform/contracts.py` | `WorkloadAttestation` fail-closed on `VALIDATED ∧ CERTIFIED` | runtime consumers |

---

## 3. DUPLICATE COMPONENTS TO ELIMINATE

Measured by **dependency direction** (directory census over-counts ~2×). Every row is engine-closable unless marked.

| # | Duplicate | Canonical Owner | Existing Implementation | Gap | Required Action | Dependency | Success Criteria |
|---|---|---|---|---|---|---|---|
| D-1 | 6 of 7 orchestration surfaces bypass `derive_order` | `engine/foundation/composition` | only 4 files import it; `engine/factory/orchestrator.py` reaches it transitively via `phases.py` | 6 surfaces carry private ordering | REFACTOR `engine/runtime/execution/scheduler.py`, `engine/runtime/orchestration.py`, `platform/universal_assurance/orchestrator.py`, `platform/universal_pipeline/orchestrator.py`, `service/orchestration.py` onto `derive_order` | none — **start immediately** | `grep -l 'engine.foundation.composition'` returns 7/7 named surfaces; `FG-15` measures a non-trivial population; tests green |
| D-2 | 2 `DependencyGraph` (same name, different things) | `ordering.py:47` type alias | `platform/foundation/dependencies.py:39` is a mutable class with its own topological sort | UAPF scheduler and orchestrator order through two implementations | REFACTOR `platform/foundation/dependencies.py` to a declaration holder projecting into `ordering.DependencyGraph`; copy the pattern at `platform/universal_pipeline/contracts.py:596` | D-1 | one `derive_order` call path; `has_cycle` string-matching removed |
| D-3 | 5 cycle detectors, 3 contracts | `ordering.py:142` `unresolved_keys` | `platform/foundation/dependencies.py:127`, `engine/uckp/graph.py:265`, `engine/graph/architecture/algorithms.py:189`, `dependency_intelligence.py:78` | report-vs-raise inconsistency | KEEP `algorithms.py` (SCC, strictly more capable — documented reason) and `uckp/graph.py` (authority-cycle law). RETIRE the `platform/foundation` detector into D-2 | D-2 | ≤3 detectors, each with a written distinct contract |
| D-4 | 2 certification authorities | `engine/certification` | `engine/universal_certification` imports no `engine.certification.*` | 2 independent roots | MERGE or declare a scope split; `platform/certification` and `platform/universal_assurance` already layer correctly | none | 1 root, or 2 with a declared non-overlapping scope in `FG-14` |
| D-5 | 3 validation authorities | `engine/validation` | `platform/universal_validation`, `platform/validation_intelligence` import no `engine.validation.*` | 2 surplus roots | MERGE onto `engine/validation`; `platform/validation` is the correct layering pattern | none | 1 root; `FG-14` population includes all 4 surfaces |
| D-6 | 3 parallel identifier grammars | `engine/registry/universal/identity.py` | `UAPF-` (`platform/universal_pipeline/identity.py:50`); `UCOS-<CAT>-NNNNNN` (`00-BOOK/tools/ukb.py:868`) **collides on the `UCOS-` prefix with a non-digest segment**; 12 × `hex16` mirrors under `application/`, `service/` | 3 mints outside the authority; 1 prefix collision | CROSSWALK `UAPF-` and `hex16` mirrors onto `deterministic_id`. For the ledger family: **declare it a distinct namespace** (it is the append-only page authority) so the prefix stops colliding | none | `parse_kind` parses every minted id in the tree, or the id declares a non-`UCOS-` namespace |
| D-7 | 2 registry surfaces, no import edge | `engine/registry/universal` (write) | `engine/registry` (EPIC-002 read adapter) shares only `engine.registry.errors` | role split undeclared | DECLARE the write/read split in `UMB-005`; no code change needed if the split is legitimate | none | a written statement in `UMB-005`; `FG-15` records the split as intended |
| D-8 | 5 `platform/**` registries rooted on `content_hash` not on the identity authority | `engine/registry/universal` | `blueprints`, `measurement`, `universal_assurance`, `projects`, `universal_master_plan` | parallel registration | REFACTOR onto `deterministic_id`; pattern to copy is `intelligence/kernel/ids.py:21` | D-6 | all 5 mint via the authority; duplicate `CertificationRegistry` name resolved |
| D-9 | 6 unreconciled layer vocabularies | `ucos.architecture-layer` (14) | IMP-001 12-layer, IMP-001 8-layer tech, INFRASTRUCTURE-002 7-layer, ENGINEERING `EL-n`, CEP `L7–L10` | no canonical layer model | CANONICALIZE `ucos.architecture-layer`; crosswalk the other 5 as views | none | one governed layer vocabulary; 5 crosswalk tables; `require()` refuses unregistered layers |
| D-10 | 2 NUC-COMPLETE facet contracts | `UNAF-001` NF-01…NF-36 | `02-NUCLEUS-CONSTITUTIONAL-MODEL.md` §3 C01–C25 — **unmapped** | two populations both define NUC-COMPLETE | MAP C01–C25 → NF-01…NF-36; retire the losing enumeration | none | one contract; `FG-17` cites one population |
| D-11 | 3 runtime contract surfaces | `08-RUNTIME/RUNTIME-001` (declaration) | `engine/runtime/bridge/contracts.py`, `platform/runtime_platform/contracts.py`, `platform/runtime_operations/contracts.py` | no crosswalk | CROSSWALK the three; declare scope per surface | D-1 | one crosswalk document; no contract field defined twice |
| D-12 | 2 concept-population measurements | CLOSURE owner | CLOSURE-002 → 549 homed / 0 unhomed (repo-only); CLOSURE-006 → 506 / **108 unhomed**, verdict **FAIL** | contradictory totals | RECONCILE — **governance act** | closure scan-mode decision | one concept total; one verdict |
| D-13 | 2 repository-intelligence producers | unassigned | `platform/repository_intelligence/` and `intelligence/rie/` both produce `UCOS-RIE-*` | no canonical owner | ASSIGN one owner; other becomes consumer | none | one producer; `FG-14` PASS over both |
| D-14 | 3 near-identical evolution lanes | unassigned | `EVO-USIS-014`, `-015`, `-016` — same 9-report set | structural duplication | MERGE into one parameterized lane | none | one lane |
| D-15 | `FG-14` measures directories, not dependency direction | `UCOS-UFC-001` | `make convergence` → 6 models, `competing surfaces: 0` | cannot see D-4/D-5/D-1 | REFACTOR `FG-14` to the dependency-direction test | D-4, D-5 | `FG-14` reports the real authority count; population ≥ 110 |

---

## 4. MISSING COMPONENTS

Repository-wide search returned nothing for these. **These are the only true CREATEs in Stage-0.**

| # | Missing | Canonical Owner (to hold it) | Existing Implementation | Gap | Required Action | Dependency | Success Criteria |
|---|---|---|---|---|---|---|---|
| M-1 | **The rule: capabilities belong to Nuclei; layers do not own capabilities** | `00-MASTER/UCOS-NUCLEUS-001/02-NUCLEUS-CONSTITUTIONAL-MODEL.md` | §1 declares Nucleus "the atomic unit of canonical ownership" — affirmative only; **no negative clause about layers exists anywhere in the tree** | rule absent, ungated | CREATE the clause in §1; CREATE gate `FG-18-NUCLEUS-OWNS-CAPABILITY` in `platform/universal_foundation/` | D-9 | grep returns the rule; gate fails on any layer-held capability |
| M-2 | `Nucleus` and `Layer` as governed entity categories | `engine/uckp` | both absent from `GOVERNED_CATEGORIES`; `Nucleus` exists only as `NucleusStratum` | the system governing everything does not govern its own structural units | EXTEND via `VocabularyRegistry.extend` (Art. 17 — **no code edit**) | M-1 | `GOVERNED_CATEGORIES` ≥ 37; `require_term` accepts both |
| M-3 | **Location Nucleus** | `engine/context/` | `ContextKind` has **no LOCATION**; `SPATIAL` = *"repository-relative POSIX paths … Space here is path space"* | reality is not location-derived | CREATE `ContextKind.LOCATION` + resolver + reference-frame declaration; register `location` as a dimension | `engine/civilization/dimensions.py` | `LOCATION` resolves; a frame change re-resolves every dependent axis |
| M-4 | **Calendar Nucleus** | `engine/context/` | absent; `calendar` is a *prohibited hardcode token* and a registrable dimension only | no calendar system | CREATE `ContextKind.CALENDAR` + resolver, derived from `LOCATION` | M-3 | ≥2 calendar systems registered; neither hardcoded |
| M-5 | **Timezone / Time-offset resolver** | `engine/context/` | `TEMPORAL` exists but frame is commit order; `timezone` prohibited token | no wall-clock frame at all | CREATE resolver under `TEMPORAL`, derived from `LOCATION` | M-3 | offset resolved from location; determined path still reads no clock |
| M-6 | **Unit Nucleus** | `platform/universal_measurement` | governs metrics and policies; grep `unit` in its `contracts.py` → **0 hits** | no unit system, no dimensional analysis, no conversion | CREATE unit registry + conversion, derived from `LOCATION` | M-3 | ≥2 unit systems; conversion is exact and reversible |
| M-7 | **Tax Nucleus** | `engine/context/` | repo-wide grep for tax/VAT → no owner | no tax context | CREATE `ContextKind.TAX` + resolver from jurisdiction | M-3, M-8, M-10 | tax resolves from location; zero rates in code |
| M-8 | **Jurisdiction promotion** | `engine/context/` | a *value* inside `REGULATORY`: *"External statutory regimes are out of scope and are not claimed"* | jurisdiction is not an axis | EXTEND `REGULATORY` → first-class `JURISDICTION` axis derived from `LOCATION` | M-3 | jurisdiction resolves independently of the internal regime |
| M-9 | **Language resolver** | `engine/context/` | `LINGUISTIC` declares one language: `language: "en"` | declaration without resolution | EXTEND to a resolver derived from `LOCATION` + observer | M-3 | ≥2 languages resolve; no `en` default in code |
| M-10 | **Currency resolver + de-hardcode `Money`** | `platform/commercial_intelligence` | `contracts.py:152-175` `Money` requires an ISO-4217-shaped code — **the single hardcode in the repository**, self-reported at `00-MASTER/CAEM-001/00-ASSIMILATION-RECORD.md:63` | currency shape hardcoded; no FX | REFACTOR `Money` to a registered value-system reference; CREATE currency resolver from `LOCATION` | M-3, M-6 | `Money` accepts a registered non-ISO value system; `PROHIBITED_TOKENS` scan clean |
| M-11 | **Assigned-identifier dictionary** | `engine/registry/universal` | term dictionary exists (`vocabulary.py`); `id-ledger.json` covers only the `NNNNNN` family | no register enumerates assigned `deterministic_id` identifiers | CREATE the UCI dictionary as a projection of the registry | D-6 | every minted id appears exactly once; UCL stage 32 binds |
| M-12 | **Security gate** | `14-SECURITY/SECURITY-001` | `14-SECURITY` stops at `004-TAXONOMY`; `platform/security` is **record-only**, "no enforcement is performed"; **0 of 27 workflows** | security is unenforced and unmeasured | CREATE `14-SECURITY/005+` (registries, engine, validation, certification) + the 28th workflow | M-2 | `security-gate.yml` fail-closed; `FG-17` NF-28 resolves by GATE not PROFILE |
| M-13 | **Nucleus register (machine-readable, cross-repository)** | `02-MASTER/` | `foundation-nucleus.json` covers the 7 Foundation entries; `02-MASTER/UCOS-Ω∞-NUCLEUS-REGISTER.md` mandated by `03-CANONICAL-NUCLEI-CATALOG…` §5 and `UNAF-001` Tier-1 item 8 — **not on disk** | 79 nuclei exist only as Markdown tables | CREATE the register as JSON, one row per nucleus × NF-01…NF-36 | D-10, M-2 | 79 rows; `FG-17` runs over all of them |
| M-14 | **Universe composition catalog + platform blueprints** | `02-MASTER/` | `UCOS-Ω∞-UNIVERSE-COMPOSITION-CATALOG.md` and `UCOS-Ω∞-UNIVERSAL-UNIVERSE-CATALOG.md` (ARCH-001) — **neither on disk**; composition rules exist as prose C-1…C-9 | no machine-readable blueprint; Amazon/Uber/ERP cannot be *configured* | CREATE the catalog as JSON: `Universe := compose(nuclei) + configuration` | M-13, D-1 | Commerce Universe composes from registered nuclei with zero new code |
| M-15 | **`.gitignore` determination over the twelve Truth zones** | Ignore authority (`W0-1`) | `.gitignore:49` excludes `/knowledge/`; `:52-63` excludes `closure.json` — **the declared `population_document`**; `:65-68` excludes `intelligence/die/` | Repository Truth is not durable; tracked registers read untracked state | DETERMINE which zones are Truth and track them (or track digests) | none — **root cause of 4 symptoms** | tracked registers read only tracked sources; closure reproducible from committed history |

**Deliberately NOT created:** an `operation` governed category (`UCOM-002:207` rejects it as breaching ART-10/INV-08); a Universal Kernel layer (`UMN-001:470` — "Foundation IS the kernel"); a second lifecycle, registry, dictionary or identifier scheme.

---

## 5. CANONICAL NUCLEUS ARCHITECTURE

**Definition (reuse, do not restate):** `02-NUCLEUS-CONSTITUTIONAL-MODEL.md` §1 — a Nucleus is the complete constitutional universe of exactly one canonical concept, the atomic unit of canonical ownership. `Nucleus(concept) ≡ Universe/concern-unit(concept)`. Anti-duplication guard §6: Commerce/Retail/Marketplace/ERP/CRM are **Universes**, not Nuclei.

**Contract (reuse):** NF-01…NF-36 in `foundation-nucleus.json`, gated by `FG-17-NUCLEUS-COMPLETE`. Resolution kinds: DECLARATION, GATE, PROFILE. An unstated facet is MISSING and blocks freeze.

### The 18 mandated nucleus properties vs what is declared at Nucleus level

| Property | Declared at Nucleus level? | Where it currently lives | Required Action |
|---|---|---|---|
| Independent · Composable · Reusable | partial | "independently composable/reusable" §1 | KEEP |
| Governed · Certifiable · Evolvable | **YES** | §1 invariants | KEEP |
| Sellable | NO | Product property `UMN-001:359` | RAISE to Nucleus invariant |
| Billable · Metered | NO | Micro-Nucleus `UMN-001:61-62`; NF-31; MN-40 | RAISE |
| Auditable | facet only | NF-23/NF-24 | RAISE |
| Observable | facet only | NF-20/NF-22 | RAISE |
| Secure | facet only | NF-28 (PROFILE) | RAISE + **M-12** makes it a GATE |
| Self-describing | partial | NF discovery descriptor | RAISE |
| Self-registering | NO | registry is external | RAISE — bind to `deterministic_id` |
| Self-measuring · Self-validating · Self-verifying | NO | external gates | RAISE |
| Infinitely extensible | **YES** | Zero-Finite §4; 32/32 axes bound | KEEP |

| Item | Canonical Owner | Existing Implementation | Gap | Required Action | Dependency | Success Criteria |
|---|---|---|---|---|---|---|
| N-1 | NUCLEUS-001 | 4 of 18 properties are Nucleus invariants | 14 declared at wrong level or as facets | EXTEND §1 to declare all 18 | D-10 | all 18 in §1; `FG-17` asserts each |
| N-2 | NUCLEUS-001 | rule M-1 absent | layers may hold capabilities | CREATE clause + `FG-18` | M-1, D-9 | gate fails on layer-held capability |
| N-3 | `platform/universal_foundation` | 7 of 79 nuclei registered; 100% CONFORMANT | 6.4% jurisdiction | EXTEND register 7 → 110 in waves | M-13, D-15 | conformance published **with its denominator** |
| N-4 | `02-MASTER/` | 79 nuclei in Markdown only | no machine-readable register | CREATE (M-13) | M-2 | 79 × 36 facet matrix |
| N-5 | `UMN-001` | 2,027 micro-nuclei declared, 0 MNC-profiled | no micro-nucleus gate runs | EXTEND MNC gate over the population | N-4 | ≥1 wave profiled |
| N-6 | `00-NUCLEUS-001` §4 | ZF-1…ZF-5 CONDITIONAL: `^UCOS-[A-Z]{2,6}-[0-9]{6}$` (10⁶), `^VOL-[0-9]{3}$` (1000), closed `LifecycleStatus`/`TRACE_STAGES`/`DiscoveryKind` | 5 finite ceilings — **the only code changes the nucleus architecture requires** | REFACTOR all 5 to open registration | none | `limit_tokens_present = 0` holds with ceilings removed |

---

## 6. UNIVERSAL IDENTIFIER ARCHITECTURE

**Reuse:** `UniversalConstitutionalKnowledgeObject` already carries **all 9** required attributes — `identity`, `ontology`+`taxonomy`, `ownership`, `provenance`+`traceability`+`temporal_history`, `relationships`, `dependencies`, `evidence`, `certification`+`validation`+`verification`, `evolution_history` — plus `replay`, `audit`, `constraints`, `policies`, 3 bindings and 6 context bindings. **The model is complete. Do not redesign it.**

| Item | Canonical Owner | Existing Implementation | Gap | Required Action | Dependency | Success Criteria |
|---|---|---|---|---|---|---|
| I-1 | `engine/registry/universal/identity.py` | `deterministic_id`, `parse_kind`, 13 kind codes | 3 parallel grammars mint outside it | REFACTOR (D-6) | none | `parse_kind` parses every id in the tree |
| I-2 | same | `_KIND_CODES` 13 | `Nucleus`, `Layer`, `Location` have no kind code | EXTEND `RegistryKind` (open) | M-2, M-3 | ≥16 kinds; kind recoverable from id |
| I-3 | `engine/uckp/ucko.py` | 34 facets, 3,359 UCKOs | nuclei are not yet UCKO instances | EXTEND — instantiate one UCKO per nucleus | N-4, I-2 | 79 nuclei each hold a UCKO with 9/9 attributes |
| I-4 | `engine/uckp/canonical.py` | one hash primitive, aliased not forked | none | KEEP | — | one definition |
| I-5 | `00-BOOK/tools/ukb.py:868` | sequential `UCOS-<CAT>-NNNNNN`, append-only page authority | collides on the `UCOS-` prefix | DECLARE a distinct namespace | D-6 | no prefix ambiguity |

---

## 7. UNIVERSAL DICTIONARY ARCHITECTURE

**Reuse:** `engine/uckp/vocabulary.py` — 13 vocabularies, 204 terms, append-only, fail-closed at use, with `verify_vocabulary_alignment` proving nine engine projections never diverge. **This is the dictionary mechanism. Do not build another.**

| Required dictionary | Canonical Owner | Existing Implementation | Gap | Required Action | Dependency | Success Criteria |
|---|---|---|---|---|---|---|
| Vocabulary | `engine/uckp/vocabulary.py` | 13 vocabularies / 204 terms | none | KEEP; admit new terms via `extend` | — | `require()` refuses unregistered terms |
| Concept | CLOSURE owner | 549 anchors / 26 families | 549 ∥ 506+108 contradiction | RECONCILE (D-12) | M-15 | one total, one verdict |
| Capability | `UCOS-UFC-001` | `foundation-capabilities.json` 7 ∥ RIE 110 | 6.4% jurisdiction | EXTEND 7 → 110 (N-3) | M-13 | denominator published |
| Knowledge | `engine/knowledge/store.py` | 121 objects | **gitignored** | TRACK (M-15) | M-15 | store in Repository Truth |
| **Identifier (UCI)** | `engine/registry/universal` | **ABSENT** — term dictionary ≠ assigned-identifier dictionary | UCL stage 32 unbound to a real dictionary | CREATE (M-11) | D-6 | every assigned id enumerated once |

---

## 8. UNIVERSAL REGISTRY ARCHITECTURE

**Reuse:** `RegistryCore` + `UniversalRegistryPlatform` (13 typed registries, deterministic ids, no duplicate registration, Knowledge-Once, version-aware, hash-chained audit, acyclic dependencies DC-2). Derived union: `UMB-005` seven registers, "DERIVED, never authoritative".

**All 8 mission-required registries are already located.** The work is consolidation and eligibility, not construction.

| Item | Canonical Owner | Existing Implementation | Gap | Required Action | Dependency | Success Criteria |
|---|---|---|---|---|---|---|
| R-1 | `engine/registry/universal` | 13 typed registries; docstring says 12 | count inconsistency (CONTEXT added by UCXI) | EXTEND docstring to 13 | none | doc = code |
| R-2 | same | 5 `platform/**` registries root on `content_hash` | parallel registration | REFACTOR (D-8) | D-6 | all mint via the authority |
| R-3 | same | `engine/registry` read adapter, no import edge | undeclared role split | DECLARE (D-7) | none | split recorded in `UMB-005` |
| R-4 | `00-BOOK/tools/config.py` | `INCLUDE_EXTENSIONS = (.md,.txt,.docx,.json)`; no `.py`, no `.sh`, no directories; `EXCLUDE_DIR_PREFIXES` bars `00-MASTER/`, `intelligence/UCOS-RIE-` | **engines and code carry no registered constitutional identity** | DETERMINE whether engines are registrable entities. If yes, extend eligibility; if no, declare code a non-authoritative view (`source-code` is already a `NON_AUTHORITATIVE_CATEGORY`) | M-15 | every relationship target either registrable or declared non-authoritative |
| R-5 | UCL / `UMB-005` | `UCL-V-41` counts 208 unregistered-target relations against a bound of 98 | the measure asks no applicability question, while `OBL-REGISTRATION` in the same file **does** ("absence from the registry is the exclusion authority working — not an unbound obligation") and binds 14/14 | RE-SPECIFY `UCL-V-41` with the same applicability predicate | R-4 | `blocking_failures` empty; `uccep` no longer blocked by `CK-UCL` |
| R-6 | Governance Authority | `assignments = 0`; 549 / 151 / 398; 212 ratifiable | 72.5% ownership undeclared | RATIFY 212 assignments | M-15 | coverage 27.5% → ~67% with **zero code change** |

---

## 9. UNIVERSAL LINEAGE ARCHITECTURE

**Reuse:** already complete on every measured axis — 1,251 lineage records, `ckos_without_provenance = 0`, `dangling_relations = 0`, `graph_cycles = 0`, `capabilities_unowned = 0`, hash-chained `AuditEntry(prev_hash, entry_hash)`, `ProvenanceStep` / `TraceLink` / `TemporalEvent` / `EvidenceRef` / `Attestation` / `ReplayProof` facets on every UCKO.

| Item | Canonical Owner | Existing Implementation | Gap | Required Action | Dependency | Success Criteria |
|---|---|---|---|---|---|---|
| L-1 | `engine/uckp/ucko.py` | 7/7 lineage dimensions present, 0 orphans | **durability only** — lineage rests partly on a gitignored store | TRACK (M-15) | M-15 | lineage reproducible from committed history |
| L-2 | `platform/universal_control_plane/durable.py` | hash-chained NDJSON journal | not yet the lineage backing store for nuclei | EXTEND to nuclei | N-4 | every nucleus event journaled |
| L-3 | `platform/universal_control_plane/linkage.py` | 9 linkages per subject | nuclei not yet subjects | EXTEND | N-4 | 9/9 closed per nucleus |
| L-4 | CLOSURE-009 | `RG-S04` 0 executions ledgered; `RG-S06` 0 tracked test-result artifacts | self-verification is CONDITIONAL | EXTEND — ledger executions | M-15 | ≥1 execution ledgered per gate run |

---

## 10. UNIVERSAL CONTEXT ARCHITECTURE

**Reuse:** `engine/context/` (UCXI-000001) — 14 parts, `ContextKind` 15 open kinds, `ContextAuthority` total order `CONSTITUTIONAL > ARCHITECTURAL > OPERATIONAL > OBSERVED > INFERRED`, equal-authority disagreement **refused** (CXL-07), extension data-only, "no control flow branches on a particular kind". **This is the correct substrate. Every missing axis plugs into it.**

| Axis | Canonical Owner | Existing Implementation | Gap | Required Action | Dependency | Success Criteria |
|---|---|---|---|---|---|---|
| Existence | `engine/context` | `EXISTENCE` `existence_mode: actual` | one frame only | EXTEND frames | M-3 | ≥2 frames resolve |
| Reality | `engine/context` | `REALITY` `reality_mode: actual` | one frame | EXTEND | M-3 | ≥2 frames |
| Observer | `engine/context` | `OBSERVER` `engine/foundation/obs/context.py` | none | KEEP | — | resolves |
| Temporal | `engine/context` | `TEMPORAL` commit-order frame, reads no clock | no wall-clock/offset frame | EXTEND (M-5) | M-3 | offset from location |
| **Location** | `engine/context` | **ABSENT** — `SPATIAL` is *path space* | **the axis everything else derives from** | CREATE (M-3) | dimensions registry | frame change re-resolves dependents |
| Spatial | `engine/context` | path space | conflated with location | KEEP as path space; separate from `LOCATION` | M-3 | two distinct axes |
| Identity | `engine/context` | `IDENTITY` → `deterministic_id`; `uis-gate.yml` | none | KEEP | — | resolves |
| Governance | `engine/context` | `GOVERNANCE` → CEP-002 | none | KEEP | — | resolves |
| Security | `engine/context` | `SECURITY` declared; runtime record-only | no enforcement, no gate | EXTEND (M-12) | M-12 | gate fail-closed |
| Knowledge | `engine/context` | `KNOWLEDGE` | store gitignored | TRACK (M-15) | M-15 | durable |
| Computational | `engine/context` | `COMPUTATIONAL` | none | KEEP | — | resolves |
| Environmental | `engine/context` | `ENVIRONMENTAL` | none | KEEP | — | resolves |
| Economic | `engine/context` | `ECONOMIC` `cost_model` = engineering cost | monetary value lives outside the context layer | EXTEND — bind `Money` to `ECONOMIC` | M-10 | value system resolves from context |
| Regulatory | `engine/context` | `REGULATORY`, internal regime only | jurisdiction is a value, not an axis | EXTEND (M-8) | M-3 | jurisdiction first-class |
| Linguistic | `engine/context` | `LINGUISTIC` `language: "en"` | declaration, no resolver | EXTEND (M-9) | M-3 | ≥2 languages |
| Cultural | `engine/context` | `CULTURAL` | none | KEEP | — | resolves |
| **Calendar** | `engine/context` | **ABSENT** | no calendar system | CREATE (M-4) | M-3 | ≥2 systems |
| **Measurement/Unit** | `platform/universal_measurement` | **ABSENT** | no units, no conversion | CREATE (M-6) | M-3 | exact reversible conversion |
| **Tax** | `engine/context` | **ABSENT** | no tax context | CREATE (M-7) | M-3, M-8, M-10 | resolves from location |

---

## 11. UNIVERSAL LOCATION-DERIVED REALITY ARCHITECTURE

**Present state, measured:** reality is **not** location-derived. `SPATIAL` is path space; there is no `LOCATION` axis; and Calendar, Timezone, Unit and Tax have no owner. What *is* already in place is the enforcement that prevents the wrong answer: `earth`, `country`, `region`, `calendar`, `timezone`, `language`, `currency`, `jurisdiction`, `reality`, `existence` are all **prohibited hardcode tokens** (21 in `engine/civilization/compliance.py`, mirrored at kernel level), `FORBIDDEN_DIMENSION_KEYS` (8) forbids any dimension legislating its own bound, `unboundedness_violations = 0`, `limit_tokens_present = 0`, `expansion_axes 32/32 bound`. **So the axes cannot be hardcoded — they can only be registered. The mechanism is right; the resolvers are absent.**

**Required derivation chain — this is the architecture to implement:**

```
LOCATION (M-3)  ← the single root axis; a registered dimension, never a literal
   ├── TEMPORAL offset / civil time      (M-5)
   ├── CALENDAR system                   (M-4)
   ├── LINGUISTIC language               (M-9)
   ├── JURISDICTION                      (M-8)
   │      └── TAX                        (M-7)   ← also needs value system
   ├── UNIT / MEASUREMENT system         (M-6)
   │      └── CURRENCY / value system    (M-10)  ← de-hardcodes Money
   ├── CULTURAL                          (extend)
   ├── REGULATORY                        (extend)
   └── GOVERNANCE                        (extend)
```

| Item | Canonical Owner | Existing Implementation | Gap | Required Action | Dependency | Success Criteria |
|---|---|---|---|---|---|---|
| LR-1 | `engine/context` + `engine/civilization/dimensions.py` | dimension registry open; `location` not registered | no root axis | CREATE `LOCATION` as a registered dimension with declared reference frames | none | Earth, Mars, Moon, Orbital, Virtual, Simulation registrable **without code change** |
| LR-2 | `engine/context/resolution.py` | precedence-ordered resolution with provenance | no derivation edges between axes | EXTEND — declare the derivation chain above as data | LR-1 | changing `LOCATION` re-resolves all 9 dependent axes; provenance records the chain |
| LR-3 | `engine/civilization/compliance.py` | 21 prohibited tokens enforced | Money is the one violation | REFACTOR (M-10) | M-6 | token scan clean including `currency` |
| LR-4 | `engine/context/certification.py` | context certification exists | no gate proves location-derivation | CREATE `context-gate.yml` (28th/29th workflow) | LR-2 | gate fails if any axis resolves without a location-derived provenance chain |
| LR-5 | `engine/context/taxonomy.py` | frames are declarations | non-Earth frames unproven | EXTEND — register ≥3 non-Earth frames as the proof | LR-1, LR-2 | Mars + Orbital + Simulation each resolve all 9 axes; kernel byte-unchanged (the `engine/provider` proof pattern) |

---

## 12. STAGE-1 IMPLEMENTATION SEQUENCE

**Entry condition (one item, and it is the only thing blocking Stage-1 today):** `R-5` — re-specify `UCL-V-41`. `uccep --tier boot` is `NOT-CERTIFIED | blocking=CK-UCL`, and `CK-UCL` resolves to `UCL-V-41` (208 > 98). The measure counts every relationship whose target lacks a registered identity; measured against `00-BOOK/tools/config.py`, **181 of 208 targets are barred from registration by declared authority, 20 are directories, 7 are `.py`/`.sh` outside `INCLUDE_EXTENSIONS`, and 0 are eligible-and-unregistered.** `OBL-REGISTRATION` in the same UCL file already applies the correct applicability test and binds 14/14. This is a governance act by the UCL owner under `UMB-005`.

**Wave order — dependency-derived, not calendar-derived:**

| Wave | Items | Governance act? | Runs in parallel with |
|---|---|---|---|
| **W1.0 Unblock** | `R-5` | YES (UCL owner) | — |
| **W1.1 Engine convergence** *(no governance act — start now, in parallel with W1.0)* | `D-1`, `D-2`, `D-3`, `D-4`, `D-5`, `D-6`, `D-8`, `D-15` | No | W1.0 |
| **W1.2 Durability** | `M-15`, `L-1`, `L-4`, `D-12` | YES (ignore + closure authority) | W1.1 |
| **W1.3 Structural canonicalization** | `D-9`, `D-10`, `D-7`, `D-11`, `D-13`, `D-14`, `M-2`, `R-1`, `R-3`, `R-4` | partly | W1.2 |
| **W1.4 Nucleus law** | `M-1`, `N-1`, `N-2`, `N-6` | YES (NUCLEUS-001) | W1.3 |
| **W1.5 Identity + dictionary closure** | `M-11`, `I-1`, `I-2`, `I-5` | No | W1.4 |
| **W1.6 Ownership + jurisdiction** | `R-6`, `N-3` | YES (Governance + UFC) | W1.5 |
| **W1.7 Location-derived reality** | `M-3`/`LR-1`, `LR-2`, then `M-4`, `M-5`, `M-6`, `M-8`, `M-9` in parallel, then `M-10`, `M-7`; `LR-3`, `LR-4`, `LR-5` | No | W1.6 |
| **W1.8 Security** | `M-12`, `N-1` security facet DECLARATION→GATE | No | W1.7 |
| **W1.9 Nucleus registers** | `M-13`, `N-4`, `I-3`, `L-2`, `L-3`, `N-5` | No | W1.8 |

**Stage-1 exit criteria (all measured, no new instrument required):**

```
blocking_failures                      = []                     (ucl_engine --gate)
uccep --tier boot                      = CERTIFIED-PROVISIONAL  (T1 VACANT caps here — expected)
make freeze                            = 13 READY / 0 NOT READY / 0 UNMEASURED
make convergence                       = FG-14/15/16 PASS over the FULL population (≥110), not 6 models
make homing coverage                   ≥ 67%
make closure-gate                      = population_complete=True
make test                              = 0 failed, coverage ≥ 90%
derive_order direct consumers          = 7 of 7 named orchestration surfaces
parse_kind coverage                    = 100% of minted identifiers
context axes with location-derived provenance = 9 of 9
non-Earth reference frames resolving   ≥ 3, kernel byte-unchanged
security-gate.yml                      = present and fail-closed
```

---

## 13. STAGE-2 IMPLEMENTATION SEQUENCE

**Reuse `UNAF-001` Deliverable 10 Tiers 2–5 verbatim. Do not re-derive this order.**

| Tier | Items | Canonical Owner | Existing Implementation | Gap | Success Criteria |
|---|---|---|---|---|---|
| T0 pre-gates | `PP-1` Commission reuse-first adjudication · `PP-2` CEP-009 amendment for the Nucleus Constitution · `PP-3` ZF-1…ZF-5 (= `N-6`, done in W1.4) · `PP-4` CFG-1 configuration-first (EXTEND PLATFORM-010) | CEP-009 / NUCLEUS-001 | roadmap-declared | 4 pre-gates unsigned | all 4 signed |
| T2 | **Ω Nucleus Registry** — registration contracts + CLI | `platform/universal_foundation` | `foundation-nucleus.json` + `FG-17` | no registration CLI | register → validate → certify → freeze |
| T3 | **Ω Nucleus Discovery** | `engine/registry/universal` | 8 discovery dimensions; `ucos.discovery-dimension` (8 terms) | discovery not nucleus-scoped | any nucleus self-describes and is found without enumeration |
| T4 | **Ω Nucleus Composition engine** + Wave-5 foundational nuclei (Identity, Space, Time, Scale, Observer, Value, Language) | `engine/foundation/composition` | `derive_order` + `engine/runtime/composition.py` | no Universe assembly from registered nuclei | `Universe := compose(nuclei) + configuration` executes |
| T5 | **Universal Generator write phase** + resolve `GT-07` declared-absence + Wave-6 (Time/Calendar deep scope) + Wave-7 (12 commerce-domain nuclei) | `engine/factory` | generator plan-only (UNG-001 has no write phase) | write phase absent | generated artifact replays byte-identically |

**Per-unit definition of done — unchanged, reuse exactly:**
`owner EXTENDED/authored → register.sh → engine/validation → engine/certification + CERTIFICATION-REGISTRY → closure regenerated (gap_total=0, invariants=0) → traceability edge recorded`

**Stage-2 exit:** `M-14` universe composition catalog exists and is machine-readable; ≥1 Universe (Commerce) composed entirely from registered nuclei with **zero new architectural code**.

---

## 14. STAGE-3 IMPLEMENTATION SEQUENCE

**The platform-configuration stage. This is where Amazon / Uber / PayTM / ERP / WhatsApp / Facebook / EdTech / Healthcare / Banking / Insurance / Government / Logistics / Manufacturing become configurations.**

Reuse `UNAF-001` Tiers 6–7 and `UMN-001` rules C-4…C-8.

| Item | Canonical Owner | Existing Implementation | Gap | Required Action | Dependency | Success Criteria |
|---|---|---|---|---|---|---|
| S3-1 | `08-RUNTIME/RUNTIME-001` | 3 runtime surfaces (crosswalked in W1.3) + `ControlPlane.discover` | no Universal Runtime deliverable | Implement Universal Runtime (Tier 6) | Stage-2 T5 | runtime hosts any composed Universe |
| S3-2 | `UMN-001` C-5 | prose: `Platform = blueprint(selected Universes) + configuration`; CFG-1 forbids platform-specific code | no blueprint catalog | CREATE platform blueprints (Wave 9) | `M-14` | ≥3 blueprints declared |
| S3-3 | NUCLEUS-001 §6 | 12 sector verticals classified **UNIVERSE**, 0 implemented | verticals unrealized | Compose each vertical from registered nuclei | S3-2 | **Amazon, Uber, PayTM, ERP, WhatsApp, Facebook, EdTech, Healthcare each declared as configuration only — zero new architectural code, zero new nucleus** |
| S3-4 | `UMN-001` §Deliverable 10 | 7-level configuration inheritance (Micro Nucleus → Domain → Nucleus/Universe → Platform → Enterprise → Organization → Runtime), "every level EXTENDS; no level REPLACES" | not exercised | Exercise the full chain | S3-3 | a runtime-level override resolves through all 7 levels |
| S3-5 | `UMN-001` C-8 | federated civilization-scale composition declared | unexercised | Compose across ≥2 reference frames | `LR-5`, S3-3 | one platform runs in two frames (e.g. Earth + Orbital) with **no code delta** |
| S3-6 | `platform/universal_foundation/freeze.py` | FZ-01…FZ-13 over Foundation | not run over a full composition | Platform-level freeze determination | S3-5 | FZ-01…FZ-13 all READY over the whole composition |
| S3-7 | NF-31 / MN-40 | billing/metering as facets | not enforced per nucleus | Implement per-nucleus billing + metering | `N-1` | every nucleus independently sellable, billable, metered |

**Stage-3 exit — the mission's stated goal, expressed as a measurement:**
`a new platform (any of the 13, or an unknown 14th) is stood up by (a) selecting registered nuclei, (b) writing configuration, (c) declaring a reference frame — with zero new architectural code, zero new nucleus, zero redesign, and FZ-01…FZ-13 READY.`

---

## 15. STAGE-N INFINITE EVOLUTION SEQUENCE

**Nothing freezes permanently.** Reuse the 45-stage lifecycle (`00-MASTER/UCL-000001`) as the resident cycle for every object; it is already discovered, ordered, acyclic, and fully owned (`stages=45`, `order=45`, `cycles=0`, `stage_nodes_unowned=0`, `stage_nodes_unauthorized=0`).

| Item | Canonical Owner | Existing Implementation | Gap | Required Action | Dependency | Success Criteria |
|---|---|---|---|---|---|---|
| SN-1 | `00-MASTER/UCL-000001` | 45 stages; **only 8 carry a completion invariant**, 37 dispositioned REUSE | 37 stages unmeasured | EXTEND invariants to all 45 | Stage-1 | 45/45 invariant-measured |
| SN-2 | UCL | 4 obligations unbound: Gap Discovery (`OBL-VALIDATION`, `OBL-VERIFICATION`, `OBL-CERTIFICATION`) + Certify (`OBL-REPLAY`) | 4 unbound | Bind — declare a gate over the Gap Discovery owner; resolve Certify re-entrancy | SN-1 | `stage_obligation_failures = 0` |
| SN-3 | `ACEE-000001` / `UCOS-AEE-001` | elevation **measured** with 5 located facets, `elevations_unevidenced=0` — but **not actuated**: nothing *causes* capability to increase | evolution observes, does not act | Implement actuation — the loop that runs the 45 stages and elevates | SN-1, SN-2 | a cycle completes and provably elevates without human initiation |
| SN-4 | `AEE-F-003` | cadence is CI, not a resident process | no resident evolution process | Implement the resident cycle | SN-3 | cycle N+1 begins from cycle N's fixed point automatically |
| SN-5 | `00-MASTER/UCOS-RFP-001` | fixed point over the **observation vector**, not over bytes (`AEE-F-002`) | byte-level fixed point unavailable | Reach byte-level after `M-15` | `M-15` | `closure009-replay` no drift; fixed point from committed history |
| SN-6 | `engine/uckp/vocabulary.py` | append-only; a term can be deprecated/superseded, never deleted | layers/nuclei cannot be *removed* | KEEP — supersession is the lawful equivalent of deletion | `D-9` | a superseded layer stops resolving while its lineage survives |
| SN-7 | `15-USIS` `USIS-REG-000…012` | 13 evolution registers incl. Self-Evolution | no corpus miner; self-learning PARTIAL | EXTEND — learn from the corpus | SN-3 | knowledge extracted and registered without instruction |
| SN-8 | `T1` Constitutional Authority | **VACANT** (`VAC-01`, `CMG-OQ-02`); caps every verdict at `CERTIFIED-PROVISIONAL`; `FINALIZED` held by 0 baselines | no authority competent to ratify | Cannot be self-cleared — T1 is presupposed, not appointed. **Operate at `CERTIFIED-PROVISIONAL` indefinitely; this is a known, recorded ceiling, not a defect to engineer around** | none | every baseline honestly labelled `CERTIFIED-PROVISIONAL` |

**Infinite-evolution invariants to hold on every future cycle — all already measured, all currently satisfied:**

```
unboundedness_violations = 0     limit_tokens_present     = 0     closed_enumerations_declared = 0
expansion_axes           = 32/32 graph_cycles             = 0     parallel_authority_claims    = 0
capabilities_unowned     = 0     dangling_relations       = 0     writes_outside_home          = 0
runs_nondeterministic    = 0     derived_artifacts_used_as_truth = 0
```

Any future cycle that moves one of these off zero is a constitutional violation, recorded as such — not architecture evolution.

---

## Critical path, end to end

```
R-5 (re-specify UCL-V-41)          ← the ONE item blocking Stage-1 today
  └─ M-15 (.gitignore / durability) ← root cause of 4 downstream symptoms
       └─ D-9, D-10 (canonicalize layer + nucleus contracts)
            └─ M-1, M-2 (the nucleus ownership rule + Nucleus/Layer as entities)
                 └─ LR-1 / M-3 (LOCATION — the root context axis)
                      └─ LR-2 (derivation chain) → M-4…M-10 (the 6 absent resolvers)
                           └─ M-13, M-14 (nucleus register + universe catalog)
                                └─ Stage-2 T2…T5 (registry → discovery → composition → generator)
                                     └─ Stage-3 (platforms as configuration)
                                          └─ Stage-N (resident evolution, CERTIFIED-PROVISIONAL ceiling)
```

**W1.1 (8 engine-convergence items) has no dependency on `R-5` and no governance act. It can start immediately and in parallel.**

---

*Plan only. Reuse before create: 71 of 86 items EXTEND or REFACTOR a located asset; 15 CREATE, each justified by a repository-wide search that returned nothing. No new authority, registry, dictionary, identifier scheme, lifecycle or gate is proposed where one exists. Every row is evidence-backed against HEAD `a5ff49a`.*
