# CAEM-001 · OUTPUT 01 — MANDATE-TO-CANONICAL-HOME MAP

> **AUTHORITY = NONE — DERIVED TRUTH.** · **`CERTIFIED-PROVISIONAL`; Tier T1 VACANT** (`VAC-01` · `CMG-OQ-02` · `UCCEP-F-004`).

**This is the anti-duplication instrument.** The mission mandates concepts under new names. The closure engines cannot detect that a new name duplicates an existing concept — `21-CONCEPT-NORMALIZATION-REGISTER.md` and `23-SEMANTIC-EQUIVALENCE-MATRIX.md` state the boundary explicitly: *no natural-language or embedding semantic matching is performed, because doing so would fabricate equivalence; equivalence is decided only by canonical-ID identity.* Therefore the mapping below was performed manually and is the deliverable that keeps `duplicate_canonical_homes` at 0.

**Rule applied** (from root `04-REPOSITORY-GAP-ANALYSIS.md` §1): *a gap exists only where no canonical owner exists **and** EXTEND/REFERENCE would distort the owner's single responsibility.* Everything else is a rename, an alias, or an extension.

**Vocabulary finding.** The token `Fabric` has **zero** occurrences across all 4,981 tracked files. The token `MCOS` has **zero** occurrences. `Universal Constitutional Asset` and `UCA-` have zero occurrences. These are new *labels*, not new *concepts*.

---

## §1 — THE MAP

| # | Mandated concept | Status | Canonical home (located) | Canonical ID | Correct treatment |
|---|---|---|---|---|---|
| 1 | **Universal Idea Box** — one immutable intake for every idea/bug/question/proposal/feedback/AI-suggestion; **no direct routing, no premature classification** | **ABSENT** | nearest: `UCIC-001` Stage 1 (Discovery) + `00-CEP/STAGE-04-…FACTORY-PLAN.md` Output 4 (Capability Intake Model) | — | **GENUINE GAP.** Existing intake is *classified-on-entry* — the exact inverse of the mandate. See Output `02` GAP-1. |
| 2 | **Universal Analysis Fabric** | **PRESENT-PARTIAL** (4 owners, no single registry) | `platform/validation_intelligence/analyzers.py` (7 dimensions, explicitly open) · `intelligence/rie/analysis.py` · `00-MASTER/UCOS-RIB-001/{06,08,09}-*-ANALYSIS.md` · `00-MASTER/UAKOS-CLOSURE-002/{closure,phase2,phase3}_engine.py` | `UCOS-EPIC-013` · `UCOS-RIE-001` · `UCOS-RIB-001` · `UAKOS-CLOSURE-002` | **EXTEND** via a binding DATA declaration over existing analyzers (the `uei-evolution.json` pattern). **Do NOT build a new analysis engine** — `AEOS-001` deny-list. See Output `02` GAP-3. |
| 3 | **Universal Validation Fabric** | **PRESENT-CANONICAL** (three-tier) | `engine/validation/**` · `platform/universal_validation/engine.py` · `platform/validation_intelligence/engine.py`; gates `UCIC-001` Output 3; evidence model `UCIC-001` Output 5; completeness authority **CCE** | `UCOS-EPIC-007` · `EC2-EPIC-005/010` · `UCOS-EPIC-013` · `UCOS-COMP-000001` | **REFERENCE.** `AEOS-001`: *"No second completeness/certification engine. CCE (E5) owns the ten-gate completeness verdict."* Missing sub-concepts (confidence, assumptions, alternatives, human review, revalidation scheduler) are EXTENSIONS of the evidence model, not a new fabric. Output `02` GAP-5. |
| 4 | **Universal Innovation Fabric** — research/patent/journal/conference/standards/commercial candidates | **PRESENT-CANONICAL** | `intelligence/research/**` + `intelligence/UCOS-URI-001/` · `intelligence/publication/**` + `intelligence/UCOS-UPI-001/` · `15-UNIVERSAL-SCIENCE-INTELLIGENCE/` · gate `.github/workflows/research-publication-gate.yml` | `UCOS-URI-001` · `UCOS-UPI-001` · `USIS-GOV-000` | **REFERENCE.** Already includes `generate_patent_draft` (`intelligence/publication/generators.py`) and `NOVELTY_PRIOR_ART_LINKED` (`intelligence/research/model.py`). "Research MUST precede classification" is already the enforced order. |
| 5 | **Universal Commercial Fabric** | **PRESENT-PARTIAL** — discovery/licensing/marketplace realized; **metering/billing specification-only** | code `platform/commercial_intelligence/**` (marketplace, licensing, pricing, packages, customer, investment, portfolio, approval) · declaration `00-MASTER/UCMI-000001/commercial-surface.json` · spec `UCOS-MIP-000002` **Part 13** (U10 Metering, U11 Billing) | `UCMI-000001` · MIP Part 13 | **EXTEND** Part 13 into code under an authorized capability. Output `02` GAP-4. **Also carries the mission's worst hard-coding** — Output `03` RG-10. |
| 6 | **Universal Context Fabric** — replace Earth/country/language/currency/calendar/tax/technology assumptions with registered Context | **PRESENT-CANONICAL** | `engine/context/**` — `constitution.py` (12 laws `CXL-01…CXL-12`), `catalog.py`, `taxonomy.py`, `ontology.py`, `registry.py`, `resolution.py`, `composition.py`, `certification.py`; coordinate model `UCOS-MIP-000002` **Universal Coordinates** (SPACE/TIME/SCALE/OBSERVER/PERSPECTIVE, all unbounded/open) | `UCXI-000001` | **REFERENCE.** `CXL-02` Bounded Extension already states the mandate verbatim: *"a future context type is admitted as data, never invented at a call site."* `CXL-06` is Context Once. The mandate is satisfied **in law**; two seeded values leak (Output `03` IG-06). |
| 7 | **Universal Registry Fabric** — everything registered with identity/ownership/lifecycle/relationships/dependencies/version/governance/validation/certification/evidence/traceability | **PRESENT-CANONICAL** | spec `UCOS-MIP-000002` **Part 7**; standard `REG-AUTO-001`; implementation `00-BOOK/tools/ukb.py` + `register.sh`; state authority `engine/registry/**`; gate `.github/workflows/ucos-registration-gate.yml` | MIP Part 7 · `REG-AUTO-001` · `UCOS-EPIC-002` | **REFERENCE.** Part 7 `LAW P7-001/002/003` already state the mandate. *"Every other registry is a projection over the Meta-Registry; no parallel truth."* A "Registry Fabric" would be a second registry — prohibited. |
| 8 | **Universal Knowledge Fabric** — Knowledge Once, single canonical source, knowledge/semantic/relationship/dependency graphs | **PRESENT-CANONICAL** | `00-BOOK/UCOS-BOOK-000000` (UKB root) · Knowledge Once = `UCKO-PRIN-0001` (named constitutional principle, gate-enforced) · graphs `engine/graph/**`, `00-BOOK/REGISTRIES/KNOWLEDGE-GRAPH-REGISTRY.md`, `UMB-006`, `UAKOS-CLOSURE-002/28`,`29`,`30` | `UCOS-BOOK-000000` · `UCKO-PRIN-0001` · `UCOS-EPIC-002` | **REFERENCE.** The mandate's "Knowledge Once principle" **is** `UCKO-PRIN-0001` by name. Restating it elsewhere would itself breach it. |
| 9 | **Universal Evolution Fabric** | **PRESENT-CANONICAL** | binding declaration `00-MASTER/UEI-000001/uei-evolution.json` + `uei_engine.py` + `.github/workflows/uei-gate.yml` · aggregate `UCCEP-000000` · amendment law `00-CEP/CEP-009` · spec MIP Parts 22/32/35/37 | `UEI-000001` · `UCCEP-000000` · `CEP-009` | **REFERENCE.** `uei-gate.yml` already *binds* observation, learning, optimization, recommendation, impact analysis, simulation, improvement discovery, evolution planning/execution, continuous improvement/optimization, future prediction, and repository/knowledge/architecture evolution. |
| 10 | **Universal Digital Twin** — twin of architecture/knowledge/capabilities/runtime/ideas/analysis/validation/innovation/commercialisation/relationships | **PRESENT-CANONICAL, NARROW SUBJECT SET** | `00-BOOK/DATA/twin.json` + `signals.json` · engine `00-BOOK/tools/ukbx.py` · `VOL-021` · standard `UMB-017` · certification `UCOS-CVER-001/04` · projection `intelligence/UCOS-RIE-DIGITAL-TWIN.json` | `VOL-021` · `UMB-017` | **EXTEND, DO NOT RECREATE** — this is already a ratified determination: `adr/0002` DELIVERABLE 10. Constraint: the twin *"MUST project the registry, not fork it"* (`AEOS-001` deny-list #3). Currently twins the corpus, largely from fixture data; does not yet twin ideas/analysis/validation/innovation/commercialisation. Output `02` GAP-6. |
| 11 | **Universal Constitutional Asset (UCA)** — a blueprint every asset inherits (31 listed facets) | **PRESENT-PARTIAL, SPLIT ACROSS TWO INSTRUMENTS** | design half: `UCOS-MIP-000002` **Cross-Cutting Capability Contract** (the 22 interfaces) + **Per-Part Structure Contract** (the 24 fields) + **Root Ontology** (BEING→EXISTENCE→RELATIONSHIP→TRANSFORMATION); lifecycle half: `UCIC-001` (15 stages, 6 gates, evidence model) | `UCOS-MIP-000002` · `UCIC-001` | **REFERENCE both; do not author a third.** Inheritance is automatic **at registration** (MIP Part 34). Facets *not* in the 22-interface contract (ontology, taxonomy, API, SDK, events, AI interface, twin, marketplace, licensing, documentation, traceability, confidence, versioning) are owned by **other located parts/programmes** (Parts 7/8/19/34, `UCMI-000001`, `VOL-021`, USIS `02-ONTOLOGY`/`03-TAXONOMY`) — they are already covered, just not by that one contract. Output `02` GAP-2. |
| 12 | **Operational Ecosystem Model** — unlimited operational ecosystems; hard-code no business domain | **PRESENT-CANONICAL as specification; ABSENT as runtime** | `UCOS-MIP-000002` **Part 43 — Industry Generation Framework** (+ Parts 38–44 Platform/Application/Experience/Enterprise/Government/Industry/Civilization Generation); generic runtime `platform/generation/**` | MIP Part 43 · `EC2-EPIC-007` | **REFERENCE the law; realize the code later.** `LAW P43-001` already states the mandate: *"industries are data-driven ontologies, never hard-coded."* **Verified: zero hard-coded verticals anywhere** — no commerce/healthcare/banking/ERP/CRM schema exists. Declared components (Industry Generator, Sector Ontology Loader, Standards Generator, Value-Chain Modeler) are not yet code. Output `02` GAP-7. |
| 13 | **MCOS** — "refactor MCOS into a Universal Engineering Civilization" | **DOES NOT EXIST** | `MCS-000-MASTER-CONTEXT-SYSTEM-ARCHITECTURE.md` + `MCP-001…MCP-007` | `MCS-000` · `MCP-001…007` | **RESOLVE THE NAME; DO NOT CREATE.** `grep MCOS` → 0 matches repo-wide. `MCOS` ≡ **MCS** (Master Context System). Critically, MCS declares **`AUTHORITY = NONE — DERIVED TRUTH`**: it is *operational memory*, never corpus, and it *"creates no authority, redefines no architecture, supersedes nothing."* The mandate's seventeen "Engineering Constitution / Governance / Intelligence / … / Self-Evolution" roles are therefore **NOT MCS's to hold** — each already has a located owner (see §2). Refactoring MCS to hold them would invert the authority hierarchy in `MCP-001` §02 — an architectural regression the mission forbids. |

## §2 — WHERE THE SEVENTEEN "MCOS" ROLES ALREADY LIVE

The mandate asks MCOS to *become* seventeen things. Each already has exactly one owner. Reassigning them to MCS would create duplicate authority — prohibited by `MCP-001` §06 (*"No duplicate authority — MCS holds none"*).

| Mandated MCOS role | Existing located owner |
|---|---|
| Engineering Constitution | `00-CEP/CEP-000…010`; band constitutions |
| Engineering Governance | UCGF + Governance Operating Model; `UCOS-GOV-001…006`; `CEP-002` |
| Engineering Intelligence | `intelligence/**`; Engineering Intelligence Layer Constitutional Policy |
| Engineering Knowledge | `00-BOOK` UKB (`UCOS-BOOK-000000`) |
| Engineering Validation | `engine/validation/**`; `platform/universal_validation/**`; `CEP-004` |
| Engineering Certification | CCE `UCOS-COMP-000001`; `CEP-005` |
| Engineering Evolution | `UEI-000001`; `CEP-009`; `UCCEP-000000` |
| Engineering Automation | `platform/generation/**`; `REG-AUTO-001`; the 12 CI gates |
| Engineering Digital Twin | `VOL-021` / `ukbx.py` |
| Engineering Analysis | `platform/validation_intelligence/**` (+ 3 co-owners — GAP-3) |
| Engineering Innovation · Research | `UCOS-URI-001` / `UCOS-UPI-001` / USIS |
| Engineering Self-Improvement | `UEI-000001` (improvement discovery, continuous improvement) |
| Engineering Self-Validation | `UCOS-RFP-001` Repository Fixed-Point (G-15) + the self-guard pattern |
| Engineering Self-Documentation | `REG-AUTO-001` projections; portal/control-tower generation |
| Engineering Self-Governance | `UCCEP-000000` aggregate gate (16 G-gates) |
| Engineering Self-Evolution | `UEI-000001` + `CEP-009` |
| *(operational memory / "what next")* | **← this, and only this, is MCS's** (`MCP-001` §03) |

## §3 — DETERMINATION

| Treatment | Count | Items |
|---|---|---|
| **REFERENCE** (exists canonically; cite it, build nothing) | **6** | 3 Validation · 4 Innovation · 6 Context · 7 Registry · 8 Knowledge · 9 Evolution |
| **EXTEND** (exists; widen under authorization) | **4** | 2 Analysis · 5 Commercial · 10 Digital Twin · 12 Operational Ecosystem |
| **RESOLVE NAME** (label collision, not a concept) | **1** | 13 MCOS → MCS |
| **SPLIT-OWNER REFERENCE** (exists across two instruments) | **1** | 11 UCA → MIP v2 + `UCIC-001` |
| **GENUINE GAP** (nothing exists) | **1** | 1 Universal Idea Box |

**Zero of the thirteen mandated concepts justifies a new parallel architecture.** Twelve are satisfied by reference, extension, or renaming. One — the Universal Idea Box — is genuinely absent and is the only green-field item in the entire mandate.

---

*END — `CAEM-001` OUTPUT 01 · AUTHORITY = NONE · `CERTIFIED-PROVISIONAL` · Tier T1 VACANT*
