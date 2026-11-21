# UNIVERSAL IDENTITY UNIVERSE DETERMINATION (UCOS-UID-000001)

> **Mission:** UCOS Ω∞ Universal Unique Identity Universe Constitutional Alignment
> **Baseline:** `5eb1a704` · **Branch:** `integration/recovery-001` · **Date:** 2026-08-17
> **Mode:** Determination. Steps 1–5 of the mandated execution order (discovery → repository truth → reuse analysis → gap analysis → determination). No implementation precedes this document.
> **Authority:** NONE (DERIVED TRUTH). This determination locates owners and refuses duplication. It legislates no identity.

---

## 1. Executive determination

**`UCOS-UID-000001` is NOT created as a new universe.** The Universal Identity Universe already exists as a **federation of six mechanisms across five planes**, legislated by AIF, made unbounded by AUTH-INF-001, rooted in UCKP Article 5, and already measured for conformance by an existing programme.

The decisive evidence is the repository's own prior refusal. `00-MASTER/UIS-001/` — the Universal Identity System Conformance programme — carries this disclosure in its declaration and in all seven of its registers:

> "This measurement holds no identity authority. It is not an identifier engine, not a registry, not a dictionary, not a resolver and not a namespace allocator. AIF governs the law of identity; ENG-001 is the engineering architecture of record; UMB-003/004/005/008/009/010 realize them in the artifact plane. **This programme adds no sixth registry and no fifth identifier scheme.**"

Creating `UCOS-UID-000001` with its own constitution, ontology, taxonomy, dictionary, registry and certificate authority would be **exactly the sixth registry and fifth identifier scheme** that UIS-001 refused to add. It would breach `CAA-INV-04` (exactly one identity authority) and `CAA-INV-07` (no instrument declares a rival object model), and it would contradict the steering's own constraint: *"Do not create competing lifecycle, registry, or authority. Universal Identity is a capability layer. Authority remains with constitutional governance."*

**Determination:** `UCOS-UID-000001` is admitted as a **capability-completion identifier, not a universe** — a name for the bounded set of gaps enumerated in §5, each closed in the located owner that already holds the concern. Where a gap has no owner, exactly one new owner is created, and only one gap qualifies.

---

## 2. Repository truth: the identity architecture that exists

### 2.1 The legislating instruments

| Instrument | Location | Owns |
|---|---|---|
| **UCKP-ART-05** | `engine/uckp/law.py`, `engine/uckp/identity.py` | Universal Identity itself. Declared `role: SUPREME — this IS UCKP-ART-05` |
| **AIF** | `02-MASTER/UCOS-Ω∞-ABSOLUTE-IDENTITY-FEDERATION-AND-CONTINUITY-CONSTITUTION.md` | The law of identity; pinned parameter law `AIF-L24` |
| **AUTH-INF-001** | `00-BOOK/CONTROL-TOWER/UCOS-Ω∞-AUTH-INF-001-INFINITE-EVOLUTION-UNIVERSAL-IDENTITY-AND-UNBOUNDED-EXPANSION-CONSTITUTION.md` | Unbounded expansion, `CR-INF-001…012` |
| **ENG-001** | `07-ENGINEERING/…UNIVERSAL-IDENTITY-SYSTEM-MASTER-ARCHITECTURE.md` | Engineering architecture of record |
| **UMB-003/004/005** | `00-BOOK/MASTER-BOOK/` | Identity, nomenclature and registry architecture in the artifact plane |
| **CMG-000006** | `00-MASTER/CMG-000006/` | Authority identity model |
| **UIS-001** | `00-MASTER/UIS-001/` | Conformance **measurement** of all of the above |

### 2.2 The two authority planes (already declared)

`00-BOOK/DATA/constitutional-authority-alignment.json` → `identity_authority_resolution`:

```
one_authority = "UCKP-ART-05 — Universal Identity. Every other identity
                 mechanism in the repository is a persistence or projection
                 binding of it."

CONSTITUTIONAL_OBJECT   home engine/uckp/identity.py
                        shape urn:ucos:ucko:<namespace>:<local_name>
                        pure, total, clock-free, storage-free, repository-free
                        role SUPREME — this IS UCKP-ART-05

REPOSITORY_OBJECT       home 00-BOOK/DATA/id-ledger.json
                        shape UCOS-<CATEGORY>-<NNNNNN>
                        maps by_path, by_object, by_observation
                        append-only; first_seen frozen; never reissued
                        role PERSISTENCE — the ONE such binding
```

`second_authority_test`: "A second identity authority would be a second **APPEND-ONLY MINT** — a file other than the ledger that issues repository identifiers. A mint is recognised by the counter it advances." The declared `mint_markers` are `["category_seq"]`.

**This is the constraint every gap closure below must satisfy: derive, never count.**

### 2.3 The six identity mechanisms (already declared by UIS-001)

| Mechanism | Home | Identity form |
|---|---|---|
| `MECH-UKB` | `00-BOOK/DATA/id-ledger.json` | `UCOS-<CATEGORY>-<NNNNNN>`, counter-allocated |
| `MECH-NOMENCLATURE` | UMB-004 two-name model | universal id ⇄ native name crosswalk |
| `MECH-EPIC001` | `engine/registry/universal/identity.py` | `UCOS-<CODE>-<12 hex>` content-derived, **version-independent** |
| `MECH-UCKP` | `engine/uckp/identity.py` | `urn:ucos:ucko:<ns>:<local>` + UUIDv5 |
| `MECH-UKIP` | `engine/knowledge/ukip/` | content identity over knowledge units |
| `MECH-UCXI` | `engine/context/` | context identity from identity tuple (`CXL-05`) |

Five identity planes `PLANE-P1…P5` are declared in `00-MASTER/UIS-001/uis-declaration.json`.

**`MECH-EPIC001` already satisfies the steering's identity-evolution principle.** `engine/registry/universal/identity.py::deterministic_id(kind, namespace, natural_key)` is *explicitly version-independent*, so every version of an artifact shares one identity — the `ID-A → v1 → v2 → v3 → ∞` shape the steering requires is already the implemented behaviour, not a gap.

### 2.4 Infinite scalability is already owned

`AUTH-INF-001` `CR-INF-002` declares that a numeric width is **FORMATTING**, widened append-only if a namespace approaches it, **renumbering nothing**. `engine/registry/universal/identity.py::register_kind()` is append-only and collision-free, so a new kind is a registration rather than a code edit. `engine/registry/universal/dictionary.py::to_document()` emits `"closed_set": false, "upper_limit": null`.

The steering's "do not design fixed tables / fixed ranges / sequential assumptions / manually allocated namespaces" is therefore **already discharged** — by declaration (`CR-INF-002`), by mechanism (`register_kind`), and by schema (`closed_set: false`).

---

## 3. Reuse map: the fourteen requested components

| # | Requested component | Located owner | Status |
|---|---|---|---|
| 1 | Universal Identity Constitution | UCKP-ART-05 (`engine/uckp/law.py`) + AIF | **EXISTS — SUPREME** |
| 2 | Universal Identity Ontology | `engine/registry/universal/identity.py` `RegistryKind` (30 kinds); UCKO 33 facets (`engine/uckp/ucko.py`) | **EXISTS** |
| 3 | Universal Identity Taxonomy | `_KIND_CODES` + `register_kind()` (append-only open extension) | **EXISTS** |
| 4 | Universal Identity Dictionary | `engine/registry/universal/dictionary.py` — `IdentifierEntry`, `IdentifierDictionary`, schema `ucos-universal-identifier-dictionary` | **EXISTS (in-memory)** → gap G3, G4 |
| 5 | Universal Identity Registry | `00-BOOK/DATA/id-ledger.json` (PERSISTENCE) + `engine/registry/universal/registries.py` (13 typed registries) | **EXISTS** |
| 6 | Universal Identity Index Engine | `engine/graph/queries.py` (BFS, closure, ancestors, topo, cycles); `engine/knowledge/store.py` `by_kind/by_authority/by_lifecycle/by_universe/by_owner`; `ukip/graph.py` | **EXISTS (4 of 6 indexes)** → gap G8 |
| 7 | Universal Identity Search Engine | lexical `engine/uckp/registry.py:239`, `ukip/discovery.py:249`, `knowledge/intelligence.py:175`; IDF-cosine `knowledge/integration/reuse.py` | **EXISTS (exact + lexical + relationship)** → gap G8 (semantic) |
| 8 | Universal Identity Certificate Authority | `engine/universal_certification/` — `Certificate`, `UCOS-UCERT-{blueprint}-{digest16}`, `CertificationPipeline`, hash-chained audit | **EXISTS** → gap G6 (not keyed on identity) |
| 9 | Universal Identity Temporal Engine | **NONE.** CMG-000002 is document-only (1020 lines of prose; zero importing code) | **GAP G1 — no owner** |
| 10 | Universal Identity Lineage Engine | `engine/nucleus/lineage.py` — hash-chained append-only `LineageLedger`, `is_intact()`, `orphans()`, `unrecorded()`; `ukb.py::derive_lineage` | **EXISTS** → gaps G5, G9 |
| 11 | Universal Identity Evolution Engine | `engine/uckp/evolution.py` Article-14 (15 stages, non-terminal) + `engine/uaue/` | **EXISTS** |
| 12 | Universal Identity Validation Engine | `engine/validation/` — subject-normalised, no per-type branches | **EXISTS** |
| 13 | Universal Identity Discovery Engine | `engine/discovery/` — 8 registry-driven dimensions | **EXISTS** |
| 14 | Universal Identity Governance Model | CMG-000001 (law owner) + `constitutional-authority-alignment.json` | **EXISTS** |

**Reuse verdict: 13 of 14 components have located owners. One has none.**

### 3.1 Dictionary reuse note

The steering's 17 required dictionary fields map as follows against `IdentifierEntry` (`universal_id`, `kind`, `namespace`, `natural_key`, `owner`, `lineage`, `attributes`) and `CanonicalKnowledgeObject` (`cko_id`, `kind`, `owner`, `authority`, `lifecycle`, `version`, `content_sha256`, `parent`, `children`, `dependencies`, `consumers`, `supersedes`, `superseded_by`, `evidence`, `certification`, `validation`, `created`, `updated`):

| Required field | Present in | Gap |
|---|---|---|
| Universal ID, Object type, Namespace, Owner | `IdentifierEntry` | — |
| Object classification | `uga_engine.py::classify_object` | — |
| Authority relationship | `KnowledgeAuthority` (4 tiers) | — |
| Parent identity | `CanonicalKnowledgeObject.parent`; `BirthRecord.parent_identity` | — |
| Child identities | `CanonicalKnowledgeObject.children` only | **G9** for the identifier plane |
| Dependencies | `CanonicalKnowledgeObject.dependencies`; UGA `depends_on` (9 758 edges) | — |
| Creation timestamp | `CanonicalKnowledgeObject.created`; `id-ledger` `first_seen` | — |
| Temporal validity | **nowhere** | **G2** |
| Lifecycle state | `Lifecycle` (10 stages, enforced transitions) | **G4** on `IdentifierEntry` |
| Evolution state | `engine/uaue` | **G4** |
| Certification state | `CertificationStatus` | **G4** |
| Evidence references | `CanonicalKnowledgeObject.evidence` | — |
| Integrity proof | `content_sha256` / `content_hash` | — |
| Lineage history | `engine/nucleus/lineage.py` | — |

**Two dictionaries already exist** (assigned-identifier and term/vocabulary) plus a 549-concept canonical concept register and a 134-object UKDA store at `knowledge/canonical-knowledge.json`. A third would be a duplicate.

---

## 4. The one component with no owner: temporal

`CMG-000002 — Universal Temporal Existence Contract` is 1020 lines declaring:

- a `temporal_coordinate` object: `coordinate_id`, `reference_system{system_type ∈ physical|logical|contextual|simulated|unknown, system_identifier, system_version}`, `value{primary, precision, uncertainty}`, `ordering_model{total_order, partial_order, causality_tracking}`, `conversion_history[]`, `provenance{creation_authority, creation_method ∈ clock|oracle|consensus|computation, evidence_id, confidence}`
- five required operations: current coordinate, compare, convert, validate ordering, preserve context
- ten laws, including Law 4 Representation Independence, Law 6 Ordering Within Reference System, **Law 7 Incomparability Across Systems**, Law 3 Conversion Provenance Preservation
- an explicit `DOES NOT MANDATE` list: UTC, ISO 8601, Unix epoch, GPS, TAI, Gregorian, 24-hour clock, Earth time zones, leap seconds

**No code imports, loads, parses or enforces any of it.** The only machine references to `CMG-000002` are corpus bookkeeping rows.

**And the repository currently contradicts it.** `00-BOOK/tools/ukb.py::_now()` produces ISO-8601 UTC, and every `at` value in `00-BOOK/DATA/change-ledger.json` (1 353 change events, 1 233 version records, 1 233 lineage nodes) is Earth UTC. That is precisely the hard-coding CMG-000002 §3.1 forbids and the steering forbids again.

This is the gap that justifies work. Everything else is reuse.

---

## 5. Gap analysis

| Gap | Description | Owner to close it | Severity |
|---|---|---|---|
| **G1** | No temporal engine: no coordinate type, no reference-system registry, no compare/convert/validate-ordering, no validity period | **NEW** — `engine/temporal/` under CMG-000002 | **BLOCKING** — "every identity must be time-aware" is unmeetable |
| **G2** | 7 of 8 time facets absent (only Creation Time exists). No Existence, Validity, Evolution, Certification, Retirement, Archive, Restoration time | `engine/temporal/` + lifecycle owners | HIGH |
| **G3** | `IdentifierDictionary` is in-memory only; no persisted `identity-dictionary.json` | `engine/registry/universal/dictionary.py` | MEDIUM |
| **G4** | `IdentifierEntry` lacks temporal validity, lifecycle_state, evolution_state, certification_state | `engine/registry/universal/dictionary.py` | MEDIUM |
| **G5** | No identity-scoped append-only event ledger with the 8 declared events (Created, Certified, Validated, Linked, Evolved, Superseded, Archived, Restored) | `engine/nucleus/lineage.py` (vocabulary is open — `record()` accepts any event) | MEDIUM |
| **G6** | No certificate keyed on a `universal_id`; `Certificate` is keyed on `target_id`/`blueprint_id` | `engine/universal_certification/` | MEDIUM |
| **G7** | `cko_id` hand-assigned, not joined to `deterministic_id` — two identity spaces unjoined | `engine/knowledge/` | LOW |
| **G8** | Temporal index, lifecycle-state index and semantic (vector) index absent; exact, lexical and relationship search exist | `engine/graph/`, `engine/knowledge/` | LOW |
| **G9** | No child index on the identifier plane (children derivable only by inverting edges) | `engine/registry/universal/dictionary.py` | LOW |
| **G10** | `ARCHIVED`/`HISTORICAL` are terminal; no restoration transition, so Restoration Time is unreachable | `engine/knowledge/model.py` `_LIFECYCLE_TRANSITIONS` | MEDIUM |
| **G11** | Identity-at-creation is **not enforced**: `ukb.py cmd_enforce --pre` deliberately excludes `unregistered` from blocking (`ukb.py:1959-1966`), and `uga_engine.py cmd_gate` only *prints* anonymous objects | `00-BOOK/tools/ukb.py`, `uga_engine.py` | **HIGH** |
| **G12** | `SEMANTIC-LIFECYCLE-RECONCILIATION-REGISTER.md` cites `UNIVERSAL-IDENTITY-AT-CREATION-DETERMINATION.md`, which does not exist | this determination | LOW — closed here |

### 5.1 G11 is the substantive constitutional gap

The steering's core claim — "the repository currently allows identified-but-unregistered artifacts" — is **correct and measurable**. The live gate output is:

```
eligible on-disk artifacts : 1368
registered (in registers)  : 1233
unregistered eligible      : 135
ENFORCEMENT PASSED
```

135 artifacts hold Universal IDs (as `EXCLUDED_DOCUMENT`/`EXDOC`) but are absent from the corpus registers, and the gate passes. In `--pre` mode `unregistered` is the *scope selector*, not a violation. `REG-AUTO-001` P1 states "Creation is registration" and L2 states "Created ≡ Registered" — so the standard already requires what the gate does not enforce.

**This is a gap between a declared standard and its enforcement, not a missing architecture.** Closing it is a gate change in `ukb.py`/`uga_engine.py`, not a new universe.

---

## 6. Determination

| Item | Determination |
|---|---|
| Create `UCOS-UID-000001` as a new universe | **REFUSED** — would be the sixth registry / fifth identifier scheme UIS-001 explicitly refused; breaches `CAA-INV-04`, `CAA-INV-07` |
| Create a 14-component identity universe | **REFUSED** — 13 components have located owners |
| Create a second identity authority | **REFUSED** — `one_authority = UCKP-ART-05` |
| Create a third dictionary | **REFUSED** — two exist plus a 549-concept register |
| `UCOS-UID-000001` standing | **A capability-completion identifier** naming gaps G1–G12, closed in existing owners |
| Authority role, were a declaration ever bound | `DERIVED` or `PROJECTION`, `relation: PROJECTION`, `derives_under: [UCKP-ART-05]`. **Never `SUPREME`** |
| New owner created | **Exactly one** — `engine/temporal/` for G1/G2, under CMG-000002 |
| Identity evolution principle | **ALREADY SATISFIED** — `deterministic_id` is version-independent by construction |
| Infinite scalability | **ALREADY SATISFIED** — `CR-INF-002`, `register_kind()`, `closed_set: false` |
| Self-application | Discharged by the located owners: UCKO mints its own identity; `LineageLedger.is_intact()` verifies itself; `UniversalIdentity.verify()` detects post-hoc edits |

### 6.1 Disposition of `engine/object_birth/` (UOBC-000001)

Partially built earlier in this cycle: `model.py`, `birth.py`, `ledger.py`. **Determination: RETAINED and completed**, with its scope narrowed by this document.

It is *not* a second identity authority — it derives identity by delegating to `engine/uckp/identity.py` (the SUPREME plane), holds no `category_seq`, and issues no repository serial. It is the **creation-time binding** of UCKP Article 5: the one thing no existing mechanism does, because all six existing mechanisms identify things that already exist.

Its `creation_timestamp` must become a **temporal coordinate** resolved through `engine/temporal/` rather than an opaque string — which is why G1 is a prerequisite for completing it, and why the ordering the steering imposed ("do not implement CMG-000012 until identity-at-creation governance is established") is correct and extends one step further: **temporal → birth → CMG-000012**.

---

## 7. Implementation plan

| Step | Work | Gap | Verification |
|---|---|---|---|
| 1 | `engine/temporal/` — coordinate, reference system, compare/convert/validate-ordering, validity period, 8 time facets. No UTC mandate; no clock inside the engine | G1, G2 | unit tests; `--cov=engine.temporal` ≥ 90 % |
| 2 | Complete `engine/object_birth/` — contract loader, 8 law checks, fail-closed gate, CLI; `creation_timestamp` becomes a temporal coordinate | G1→birth | unit tests; gate exit 0/1/2 |
| 3 | Re-populate `CMG-000012` under the birth contract with a conforming birth record | WS3 | birth gate green |
| 4 | Persist the identity dictionary; add temporal/lifecycle/certification fields and a child index | G3, G4, G9 | dictionary `verify()` |
| 5 | Identity event ledger over the 8 events using the open `record()` vocabulary | G5 | `is_intact()` |
| 6 | Certificate keyed on `universal_id` | G6 | integrity verify |
| 7 | Restoration transition out of `ARCHIVED` | G10 | transition tests |
| 8 | **Enforce identity-at-creation**: make `unregistered` blocking and anonymous objects fail the UGA gate | G11 | full gate suite |
| 9 | Temporal, lifecycle and semantic indexes | G8 | index tests |
| 10 | Join `cko_id` to `deterministic_id` | G7 | round-trip tests |

**Steps 1–3 are executed in this cycle.** Steps 4–10 are scoped, owned and sequenced but not started; step 8 in particular changes a passing gate into a failing one for 135 existing artifacts and must not be landed without a migration determination.

---

## 8. Verification requirements status

| # | Requirement | Status |
|---|---|---|
| 1 | Every created artifact receives identity at creation | Contract exists (UOBC-000001); **enforcement deferred to step 8** |
| 2 | No anonymous artifacts remain | 0 anonymous in the committed tree; 135 unregistered-but-identified remain (G11) |
| 3 | Registry and dictionary consistency | `ukb.py validate` green — 1 233 artifacts, referential integrity OK |
| 4 | Identity uniqueness | `CAA-INV-04` green, injectivity recomputed over 6 051 identifiers |
| 5 | Certificate validity | Existing `Certificate.verify_integrity()`; identity-keyed certificate is G6 |
| 6 | Temporal metadata completeness | **G1/G2 — closed by step 1** |
| 7 | Lineage completeness | Hash-chained ledger intact; child index is G9 |
| 8 | Evolution replay compatibility | `engine.uaue.gate --replay` byte-identical |
| 9 | Self-application compliance | Discharged by located owners (§6) |
| 10 | All existing gates remain green | Re-verified at the end of this cycle |

---

**END UNIVERSAL IDENTITY UNIVERSE DETERMINATION**

**Status:** Evolution Baseline Established v1.0
**Identity Authority:** UCKP-ART-05 — unchanged, unrivalled, and not extended by this determination
**Lifecycle Authority:** UCIC-001 (owner) · UCL-000001 (derived) · CMG-000001 (law)
**Governed Evolution:** ENABLED — CEP-009 · Article-14
