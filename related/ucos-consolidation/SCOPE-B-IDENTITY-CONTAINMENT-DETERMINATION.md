# SCOPE B — Universal Identity Containment Determination

| Field | Value |
|---|---|
| ARTIFACT | Scope B · Workstreams 1, 3, 4 — Identity Containment, Authority Alignment, UELA Readiness |
| PHASE | PHASE 1 — FOUNDATION COMPLETION · Scope B |
| MODE | **DETERMINATION ONLY.** No implementation, no code change, no registry mutation, no identifier minted, no migration executed, no authority created. |
| CONSTITUENT AUTHORITY | **NONE** |
| GOVERNANCE AUTHORITY | **NONE** |
| PREDECESSOR | `SCOPE-B-DISCOVERY-REPORT.md` |
| BINDING PRIORS | `UNIVERSAL-IDENTITY-UNIVERSE-DETERMINATION.md` · `UNIVERSAL-IDENTITY-DICTIONARY-DETERMINATION.md` · `UNIVERSAL-IDENTITY-MIGRATION-DETERMINATION.md` — where any conflicts with this, **they govern** |

---

## 1. Identity Authority Map

Located owner of this question: `00-BOOK/DATA/constitutional-authority-alignment.json` → `identity_authority_resolution`.

> `one_authority`: "UCKP-ART-05 — Universal Identity. Every other identity mechanism in the repository is a persistence or projection binding of it."

| Component | Owner | Authority level | Persistence role | Projection role |
|---|---|---|---|---|
| **UCKP Identity Authority** | `engine/uckp/identity.py` | **SUPREME — this IS UCKP-ART-05** | none — pure, total, clock-free, storage-free, repository-free | none; it is the function others project from |
| **ID Ledger** | `00-BOOK/DATA/id-ledger.json` | **PERSISTENCE — the ONE such binding** | append-only; `first_seen` frozen at mint; never reissued, never renumbered | `by_path` (1,264) · `by_object` (4,848) · `by_observation` (7) are indexes over it |
| **Registry Identity** | `engine/registry/universal/identity.py` | DERIVED | none | `deterministic_id` mints by derivation from `(kind, namespace, natural_key)` |
| **Object Identity** | `00-MASTER/UCOS-UGA-001/uga_engine.py` | DERIVED TRUTH — current-state authority over the governed population | writes 10 surfaces, all producer-owned | `02-UNIVERSAL-OBJECT-REGISTRY` (6,079) is the authority view; `01-EXECUTABLE` (4,846) and `04-RELATIONSHIP-GRAPH` are projections of it |
| **Dictionary Capability** | `engine/registry/universal/dictionary.py` | DERIVED — **projection, not authority** | **NONE — in-memory only.** `__slots__ = ("_entries",)` | `IdentifierDictionary.lookup` / `entries` / `by_kind`; `verify()` re-mints every entry and fails closed |

**Mint marker.** `second_authority_test` recognises a second identity authority *by the counter it advances*; the declared `mint_markers` set is `["category_seq"]`, held solely by the ID Ledger. **DETERMINED: every Scope B extension shall derive, never count.** Nothing determined below opens a counter.

---

## 2. Object Population Analysis

| Population | Home | Measured | Classification |
|---|---|---|---|
| Book artifacts | `00-BOOK/DATA/artifacts.json` | **1,233** | **AUTHORITATIVE** for `DOCUMENT_ARTIFACT`, owned by UMB-IMP-001 |
| Book relationships | `00-BOOK/DATA/relationships.json` | 12,899 edges | **DERIVED** |
| ID ledger paths (`by_path`) | `id-ledger.json` | 1,264 | **PROJECTED** (index) |
| ID ledger objects (`by_object`) | `id-ledger.json` | 4,848 | **HISTORICAL** (append-only record) |
| ID ledger `history` | `id-ledger.json` | 1,264, keyed by identity | **HISTORICAL** |
| ID ledger `category_seq` | `id-ledger.json` | 117 counters | **AUTHORITATIVE** — the sole mint marker |
| UGA governed objects | `02-UNIVERSAL-OBJECT-REGISTRY.json` | **6,079** | **AUTHORITATIVE** (current state), derived truth |
| Registry objects (executable) | `01-EXECUTABLE-OBJECT-REGISTRY.json` | 4,846 | **PROJECTED** |
| Test objects | UGA class `TEST_OBJECT` | 821 | **PROJECTED** subset |
| Derived / generated objects | `generated-artifact-registry.json`; UGA `lifecycle=GENERATED` | 344 | **GENERATED** |
| Birth records | `00-MASTER/UOBC-000001/birth-ledger.json` | **35** | **AUTHORITATIVE** on the constitutional plane |
| Capability catalogue | `intelligence/UCOS-RIE-CAPABILITY-CATALOG.json` | 129 | **DERIVED** |

**Containment determination.** The 4,848 − 4,846 = **2** difference is *correct*, not drift: both are `RETIRED`, a declared lifecycle state — *"Previously minted an identity, no longer carried by version control. Identity is retained (append-only) and never reissued."* One is a gitignored verification-evidence cache file outside the UGA eligibility boundary; one is deleted. **The ledger is a historical record; the registry is current-state authority. The difference is the proof they are correctly different kinds of thing, and shall not be "reconciled" away.**

---

## 3. Identity Invariant Assessment

Measured over all **6,079** governed objects.

| Invariant | Coverage | Evidence | Status |
|---|---|---|---|
| **Universal ID** | 6,079 / 6,079 | `universal_id` on every entry | **PASS** |
| **Owner** | 6,079 / 6,079 | `owner`; 5 ownership rules ending in a total catch-all | **PASS** |
| **Type** | 6,079 / 6,079 | `object_class`; 7 declared classes | **PASS** |
| **Namespace** | 6,079 / 6,079 (**derived**) | `engine.uckp.alignment.repository_local_urn` executed over the whole population → `urn:ucos:ucko:ucos-repository:<ID>`, **0 failures** | **PASS** |
| **Lifecycle** | 6,079 / 6,079 | `AUTHORED` 5,735 · `GENERATED` 344 (+`RETIRED` retained in ledger) | **PASS** |
| **Lineage** | plane-split — §4 | `parent` 1,232/1,233 · `first_seen` 4,846/4,846 · `parent_identity` 35/35 | **PARTIAL** |

**Namespace is PASS, not GAP.** It is *derivable*, and deliberately not stored per-entry. A derivable fact stored redundantly on 6,079 rows is a second truth that can disagree with the first. **DETERMINED: namespace shall remain derived. No namespace field shall be added to the object registry.**

**`first_seen` is absent for exactly 1,233 objects, and that set is exactly the `DOCUMENT_ARTIFACT` class** — the one class UGA declares it does not mint for (*"governed_by UMB-IMP-001 … This programme registers NOTHING here"*). The absence aligns precisely with a declared plane boundary rather than cutting across one. **This is a boundary, not a hole.**

---

## 4. Lineage Composition Determination

### 4.1 The law already decides this

`UCL-000001` stage `UCL-S-0350` "Update Universal Lineage" carries its authority verbatim:

> **"UCI-001 Part XVI.5 — lineage and evolution are DERIVED projections over recorded history; no new store is created."**
> *(authority owner: `00-BOOK/CONTROL-TOWER/UCOS-Ω∞-UCI-001-…-STANDARD.md`)*

**DETERMINED: lineage shall be composed as a derived projection. No lineage database, no lineage authority, no lineage store shall be created.** This is not a Scope B choice — it is ratified law, and Scope B's only job is to obey it.

### 4.2 The three shapes, and the composition over them

| Plane | Lineage mechanism | Coverage |
|---|---|---|
| Document (1,233) | `parent` in `artifacts.json` | 1,232 / 1,233 — the 1 is the declared root `UCOS-BOOK-000000` |
| Repository (4,846) | `first_seen` origin + `dependencies` (1,920) / `produces` (41) + 12,899 relationship edges | origin 4,846 / 4,846 |
| Constitutional (35) | `parent_identity` (`UOBC-F-06`) | 35 / 35 |

**GAP B-1 restated precisely: no defect of data, a defect of composition.** Each plane answers correctly in its own shape; nothing answers uniformly across all three.

### 4.3 The determined model

```
        EXISTING AUTHORITIES                     (unchanged, unmoved, unwrapped)
  artifacts.json · id-ledger.json · UGA registry · birth-ledger.json
                   │
                   ▼
        UNIVERSAL LINEAGE PROJECTION             (read-only, derived, stores nothing)
                   │
                   ▼
        DISCOVERY CAPABILITY                     (the six questions, §4.4)
```

**Constraints the projection shall satisfy, determined now so implementation cannot drift:**

1. **Reads only.** It writes no file, opens no counter, mints no identifier, and holds no `mint_marker`.
2. **Composes, never copies.** Every answer cites the authority it came from. A cached lineage table would be a new store, which XVI.5 forbids.
3. **Total over the population, honest about shape.** For any of the 6,079 objects it returns lineage *and the plane that supplied it*. Where a plane has no parent edge, it returns origin (`first_seen`) and says so — never a fabricated parent.
4. **Deterministic.** Two queries over one repository state return identical bytes. No clock, no network.
5. **Open.** A fourth plane admitted later is a declaration change, not an engine change.

### 4.4 The six questions the discovery capability must answer

| Question | Composed from |
|---|---|
| What is this? | UGA `object_class` · `artifacts.json` `category`/`name` |
| Who owns this? | UGA `owner` · `artifacts.json` `owner` · UOBC `owner` |
| Where did this originate? | `first_seen` (commit) · `artifacts.json` `parent` · UOBC `parent_identity` |
| When was it created? | `id-ledger.history[].at` · UOBC `creation_timestamp` |
| What has it become? | `id-ledger.history[]` (append-only snapshots keyed by identity) |
| What depends on it? | UGA `dependencies` / `produces` · `relationships.json` (12,899 edges) |

**Supported subjects:** objects, capabilities, nuclei, registries, artifacts, configurations, generated realities — all seven already carry a UGA `object_class` or a capability-catalogue entry, so none requires a new model.

---

## 5. Universal UID Dictionary Determination

### 5.1 Classification: **EXTEND. NOT CREATE.**

`engine/registry/universal/dictionary.py` exists — `IdentifierDictionary`, 346 lines, schema `ucos-universal-identifier-dictionary`. `UNIVERSAL-IDENTITY-UNIVERSE-DETERMINATION.md` §6 refuses **"a third dictionary"** by name. **A new dictionary is REJECTED.**

### 5.2 A mis-binding located, and left for its owner

`UCL-S-0320` "Update Universal Constitutional Identifier **Dictionary**" declares its evidence as `engine/uckp/vocabulary.py` — the **term** vocabulary — not `engine/registry/universal/dictionary.py`, the **assigned-identifier** dictionary. The two are different objects: one governs which *words* may be used, the other enumerates which *identifiers* were minted.

**DETERMINED: this is a finding, not a Scope B repair.** `UCL-000001` owns the stage manifest; correcting a stage's evidence binding is that owner's act, not this determination's. Recorded as **GAP B-4** and referred.

### 5.3 The required projection chain

```
Identity Authority (UCKP-ART-05)
        ↓
UID Dictionary Capability            ← IdentifierDictionary, EXTENDED
        ↓
Semantic Discovery
        ↓
Global Search
        ↓
Knowledge Discovery
```

### 5.4 Persistence, replay, determinism — the G3 decision

`UNIVERSAL-IDENTITY-DICTIONARY-DETERMINATION.md` already states the compliance fork verbatim: a persisted dictionary is **either** derived truth (⇒ replay-gated, byte-stable, producer-owned) **or** governed evolution state (⇒ declared in `mutation-governance-boundary.json` with a named transaction owner), and either path *"is a capability addition requiring its own determination and its own mutation-class registration."*

**DETERMINED — G3 shall be closed on the DERIVED-TRUTH path**, for a reason that is not convenience: the dictionary's entire content is re-mintable from `(kind, namespace, natural_key)` by `deterministic_id`, and `IdentifierDictionary.verify()` already re-mints every entry and fails closed. A body of facts that can be recomputed from its inputs **is** derived truth; declaring it governed evolution state would claim a mutation authority over something no one may mutate independently, and would open a transaction owner where none is needed.

| Requirement | Determined obligation |
|---|---|
| Persistence | One producer-owned file. **No counter.** Content re-derivable in full from existing authorities |
| Projection model | Projection of the ID Ledger + registry identity plane. **Deleting it changes no verdict**, only the cost of reaching one |
| Replay | Two producer runs over one repository state produce **byte-identical** output (the `--render` + drift-check discipline UAIE/UCAF/UAKOS already use) |
| Determinism | No clock, no network, no subprocess in the producer |
| Fixed point | Must reach a fixed point under the producer loop, as measured for the Scope A derived registers |

**G3 is determined but NOT authorized.** Implementation requires the approval checkpoint at §9.

---

## 6. Workstream 3 — Authority Alignment Determination

### 6.1 Current declarations

| Authority | Declared where | Standing |
|---|---|---|
| Identity | `constitutional-authority-alignment.json` → `identity_authority_resolution` | UCKP-ART-05 SUPREME; one authority, one mint marker |
| Persistence | same → `planes[REPOSITORY_OBJECT]` | ID Ledger, **the ONE such binding** |
| Registry | UGA `uga-declaration.json`; `UMB-005-REGISTRY-ARCHITECTURE.md` | UGA = derived truth over the governed population |
| Governance | `CMG-000001`; `CEP-002` | law owner / governance constitution |

### 6.2 Multiple declarations — measured

38 registry-shaped artifacts. Authority standing is declared in **three different shapes**:

| Shape | Count / examples |
|---|---|
| Top-level `authority` key | UGA surfaces, `birth-ledger.json`, RIE catalogue, `exclusion-register.json`, `generated-artifact-registry.json` |
| Domain-specific key | `uis-declaration.json` → `classification_authority`; `ucl-declaration.json` → `lifecycle_authorities`; `ucaf-authority.json` → `authority_sources` |
| **Not in-file; declared externally** | `artifacts.json` (via UMB-IMP-001) · `id-ledger.json` (via `constitutional-authority-alignment.json`) · `relationships.json` · `volumes.json` |

**Correction to a finding drafted during discovery:** `id-ledger.json` is **not** an undeclared authority. Its standing is declared precisely, externally, as `PERSISTENCE`. The finding that survives is narrower.

**GAP B-2 (determined, not repaired here): authority standing is *discoverable in three places and three shapes*.** No single instrument answers "what is this registry, who owns it, what is its standing" for all 38. **No new authority is proposed.** The remedy is a **matrix that reads the existing declarations** — a projection, not a fourth declaration site.

**DETERMINED: no authority shall be created, moved, or re-declared. `REGISTRY-COVERAGE-MATRIX` shall be a derived read-only projection over the three existing shapes.**

---

## 7. Workstream 4 — UELA Lifecycle Automation Readiness

### 7.1 The central finding: UELA's lifecycle already exists and is already open

`00-MASTER/UCL-000001/ucl-stage-manifest.json` declares **45 stages** (`UCL-S-0010` … `UCL-S-0450`) with `open: true`, `closed_enumeration: false`, `ordinal_step: 10`, and admission = *"Append a node record to `nodes`… No engine change, no declaration change, no architectural redesign."*

The mandate's UELA cycle maps onto it **without a new stage**:

| UELA stage | UCL stage(s) |
|---|---|
| Discovery | `UCL-S-0040…0100` (Repository Truth · Knowledge · Canonical Owner · Capability · Dependency · Constraint · Gap) |
| Determination | `UCL-S-0190…0230` (Reason · Reflect · Challenge · Correct · Improve) |
| Planning | `UCL-S-0240` Architect |
| Authorization | `UCL-S-0270` Govern |
| Implementation | `UCL-S-0250` Engineer |
| Validation | `UCL-S-0160` Validate |
| Verification | `UCL-S-0170` Verify |
| Evidence | `UCL-S-0150` Evidence |
| Certification | `UCL-S-0280` Certify |
| Baseline Creation | `UCL-S-0290` Integrate · `UCL-S-0300` Register |
| Repository Truth Update | `UCL-S-0360` Update Repository Truth |
| Runtime Observation | `UCL-S-0120…0140` (Observe · Perceive · Measure) |
| Learning | `UCL-S-0180` Learn · `UCL-S-0390/0400` Extract/Register Engineering Knowledge |
| Next Evolution Cycle | `UCL-S-0450` Begin Next Elevated Engineering Cycle |

**DETERMINED: UELA shall not introduce a lifecycle model. It shall orchestrate `UCL-000001`.** A second lifecycle graph would be the parallel-governance defect this scope forbids.

### 7.2 Automated vs manual — measured

**39 of 45 stages carry an executable `binds`. 6 do not. All 45 carry `evidence`.**

| Unbound stage | Group | Why it matters to UELA |
|---|---|---|
| `UCL-S-0010` Receive Goal | GOAL | The entry point — intent arrives from outside the system |
| `UCL-S-0020` Understand | GOAL | Comprehension of intent |
| `UCL-S-0190` Reason | COGNITION | Impact analysis |
| `UCL-S-0200` Reflect | COGNITION | Simulation |
| `UCL-S-0210` Challenge | CORRECTION | Conflict detection |
| `UCL-S-0230` Improve | CORRECTION | Improvement discovery |

**These six are exactly the judgement stages** — goal comprehension, reasoning, simulation, challenge, improvement. That they are unbound is a finding UELA must plan around, not a defect to paper over: **UELA can automate orchestration of 39 bound stages and must model the 6 as decision points requiring an authority, not as steps to be silently skipped.**

### 7.3 Engine → UELA signal map

| Engine | Lifecycle signal it already provides | UELA consumes as |
|---|---|---|
| **UVI-000001** | which verification a change requires; stage registry; mode constitution; evidence registry | Validation/Verification orchestration + assurance floor |
| **UGA-001** | 6,079 objects with ID/owner/type/lifecycle; relationship graph; 29 invariants | Discovery + Classification + Registration state |
| **UOBC-000001** | birth records; identity-before-existence; 8 laws | Identity Assignment + Lifecycle Activation |
| **UCAF-001** | authority tiers, delegations, successions, token classification | Authorization |
| **UAUE-000001** | evolution candidates/plans/simulation/execution registers, 18 registers | Evolution cycle state |
| **UAKOS-CLOSURE-008** | assimilation, traceability, validation record, `stages_digest` | Repository Truth Update + Baseline |
| **UISD-000001** | unboundedness; no closed enumeration; openness performed | Infinite-scope guarantee across cycles |
| **UCPA-000001** (Scope A) | root ontology measured; facet reduction | Constitutional conformance of new objects |
| **Certification** | CEP-005 channel; `universal_certification` | Certification stage |

### 7.4 What every future capability must expose for UELA

**DETERMINED — the UELA interface contract.** Each item is required, and each already has a located owner, so no new mechanism is implied:

| Required | Existing owner |
|---|---|
| Identity | UCKP-ART-05 / UGA `universal_id` |
| Ownership | UGA `owner` / ownership rules |
| Authority | UCAF authority tiers |
| Dependencies | UGA `dependencies`/`produces`; `relationships.json` |
| Evidence | UVI evidence registry; programme `evidence` fields |
| Verification status | `verify.sh` stage result; UVI |
| Certification status | UAKOS `validation-record.json`; CEP-005 |
| Baseline relationship | `BASELINE-001`; `stages_digest` |
| Evolution history | `id-ledger.history`; UAUE `EVOLUTION-HISTORY.json` |

**Nine required signals, nine located owners, zero new stores.** UELA is therefore an **orchestration** capability, not a data capability.

### 7.5 UELA dependency on this scope

UELA cannot automate `UCL-S-0320` while the identifier dictionary is unpersisted (**G3**) and while the stage's evidence names the term vocabulary rather than the identifier dictionary (**GAP B-4**). **These two are UELA's blocking prerequisites from Scope B.**

---

## 8. Validation of this determination

| Requirement | Status |
|---|---|
| No implementation performed | **CONFIRMED** — no source file written or modified |
| No identities minted | **CONFIRMED** — no producer run; no counter touched |
| No registries changed | **CONFIRMED** — read-only measurement only |
| No duplicate authority proposed | **CONFIRMED** — §6 creates none; matrix is a projection |
| No duplicate dictionary proposed | **CONFIRMED** — §5.1 EXTEND, third dictionary REJECTED |
| Existing capabilities reused | **CONFIRMED** — §7.3, nine signals from nine existing owners |
| Infinite scope preserved | **CONFIRMED** — UCL `open: true`, `closed_enumeration: false`; no enumeration closed here |
| Unknown future objects discoverable | **CONFIRMED** — UGA classification is total (catch-all rule); `category_seq` opens by classification, not by enum |
| UELA alignment captured | **CONFIRMED** — §7 |
| Future automation path defined | **CONFIRMED** — §7.2 (39 bound / 6 judgement), §7.5 (blocking prerequisites) |

---

## 9. Approval checkpoint

**Nothing below §9 is authorized.** Implementation prerequisites, risks and the decision requested are consolidated in the Scope B final output accompanying this determination.

---

*End of SCOPE-B-IDENTITY-CONTAINMENT-DETERMINATION.md*
