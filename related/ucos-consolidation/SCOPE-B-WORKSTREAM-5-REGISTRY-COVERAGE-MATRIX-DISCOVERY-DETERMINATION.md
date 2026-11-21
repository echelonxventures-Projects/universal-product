# Scope B · Workstream 5 — Registry Coverage Matrix · Discovery Determination

| Field | Value |
|---|---|
| MODE | **DISCOVERY ONLY.** No implementation, no registry change, no registry created, no authority changed. |
| CONSTITUENT AUTHORITY | **NONE** |
| PRIOR BASELINE | `B-01` · `B-02` · Universal Lineage Projection — all CERTIFIED, **unmodified** |
| PRINCIPLE UNDER TEST | *A registry is not an authority. A registry is a governed projection or index of owned reality.* |

---

## 1. Objective

Answer: **"What governed objects exist, where are they registered, and is every canonical object discoverable through the correct authority?"**

Every number below was measured at this baseline.

---

## 2. Registry Inventory

**140 registry-shaped artifacts** (a JSON carrying a population of ≥3). The twelve largest:

| Registry | Owner | Purpose | Population | Update mechanism |
|---|---|---|---|---|
| `UCOS-UGA-001/04-RELATIONSHIP-GRAPH.json` | UCOS-UGA-001 | object relationship graph | **34,682** | `uga_engine.py run` |
| `UAKOS-CLOSURE-008/assimilation.json` | UAKOS-CLOSURE-008 | assimilation rows | 23,859 | `assimilation_engine.py` |
| `00-BOOK/DATA/relationships.json` | UCOS-UKB-TOOLING | typed corpus edge graph | **12,899** | `ukb build` |
| `UCOS-UGA-001/00-EXISTENCE-INVENTORY.json` | UCOS-UGA-001 | existence inventory | 6,107 | `uga_engine.py run` |
| `UCOS-UGA-001/02-UNIVERSAL-OBJECT-REGISTRY.json` | UCOS-UGA-001 | **the governed object universe** | **6,107** | `uga_engine.py run` |
| `00-BOOK/DATA/id-ledger.json` | UCKP-ART-05 persistence binding | repository identity | 4,876 paths | `ukb build --mint` (register.sh only) |
| `UCOS-UGA-001/03-AUDIT-UNIVERSE.json` | UCOS-UGA-001 | audit events | 4,876 | `uga_engine.py run` |
| `UCOS-UGA-001/01-EXECUTABLE-OBJECT-REGISTRY.json` | UCOS-UGA-001 | executable subset | 4,874 | `uga_engine.py run` |
| `UCOS-UICM-000001/02-CLOSURE-OBSERVATION-REGISTRY.json` | UCOS-UICM-000001 | closure observations | 3,162 | UICM engine |
| `00-BOOK/DATA/change-ledger.json` | UMB-008 | change/version/lineage | 1,358 events | `ukb build` |
| `00-BOOK/DATA/artifacts.json` | UMB-IMP-001 | **the corpus artifact register** | **1,233** | `ukb build` |
| `00-BOOK/DATA/generated-artifact-registry.json` | UCOS-GENERATED-ARTIFACT-REGISTRY-001 | derived-artifact declaration | 345 | **authored** |

Named categories, all located: artifact registry (`artifacts.json`) · identity dictionary (`UCOS-NUCLEUS-IDENTIFIER-DICTIONARY.json`, 212, B-02) · relationship registries (`relationships.json`, UGA graph) · capability registries (`UCOS-RIE-CAPABILITY-CATALOG.json`, 130) · governance registries (`ucaf.json`, `ucda.json`, `mutation-governance-boundary.json`) · evidence registries (`evidence-universe.json`, `certification.json`) · knowledge registries (`knowledge/canonical-knowledge.json`, 141).

**Producers, all under `UCOS-UKB-TOOLING`:** `ukb.py` writes 6 corpus files (`id-ledger`, `artifacts`, `volumes`, `relationships`, `control-tower`, `change-ledger`); `ukbx.py` writes `twin.json`, `signals.json`; `governance_telemetry.py` writes `certification.json`; `connectors/base.py` writes `connector-cursors.json`.

---

## 3. Authority Classification

Authority is declared through **five different mechanisms**, measured across all 140:

| Mechanism | Count |
|---|---|
| Top-level `authority` key | **71** |
| Entry in the generated-artifact registry | 17 |
| Domain-specific key (`authorities`, `authority_sources`, `classification_authority`, …) | 14 |
| `constitutional-authority-alignment.json` / `mutation-governance-boundary.json` | 3 |
| **None located** | **35** |

**Correction to a crude first measurement, recorded because it changes the finding:** a naïve top-level-key scan reported **69** undeclared. That instrument was wrong — the same error made in Scope B. Searching all five mechanisms reduces it to **35**, and `artifacts.json` and `id-ledger.json` are *not* among them (both are declared externally).

### Classification

| Class | Registries |
|---|---|
| **SOURCE AUTHORITY** | `artifacts.json` (containment + corpus registration) · `id-ledger.json` (`category_seq`, the sole mint marker) · `generated-artifact-registry.json` (authored) · `birth-ledger.json` |
| **DERIVED PROJECTION** | all 10 UGA surfaces · `relationships.json` · `change-ledger.json` · `UCOS-RIE-*` · UICM closure registries · `UCOS-NUCLEUS-IDENTIFIER-DICTIONARY.json` |
| **EVIDENCE INDEX** | `evidence-universe.json` · `certification.json` · `canonical-observation-audit.json` · UAKOS `validation-record.json` |
| **DISCOVERY INDEX** | `id-ledger.by_path` · `by_object` · `control-tower.json` · `volumes.json` |

**Confirmed:**
* **No registry creates identity.** The sole mint marker is `category_seq`, held by the ID Ledger; `deterministic_id` derives without counting; `UOBC` births derive.
* **No registry creates ownership.** Ownership is resolved by the UGA path rule and recorded, never minted, by a registry.
* **No registry is a duplicate authority** — measured in §5.

---

## 4. Coverage Matrix

### Object universe: **6,107 governed objects**

| Object class | Count | `artifacts.json` | `id-ledger` | generated-reg | Coverage |
|---|---|---|---|---|---|
| `EXCLUDED_DOCUMENT` | 2,597 | 0 | **2,597** | 290 | **FULL** |
| `EXECUTABLE_OBJECT` | 1,260 | 0 | **1,260** | 0 | **FULL** |
| `DOCUMENT_ARTIFACT` | 1,233 | **1,233** | 0 | 0 | **FULL** |
| `TEST_OBJECT` | 825 | 0 | **825** | 0 | **FULL** |
| `DATA_OBJECT` | 125 | 0 | **125** | 55 | **FULL** |
| `TOOLING_OBJECT` | 36 | 0 | **36** | 0 | **FULL** |
| `CONFIGURATION_OBJECT` | 31 | 0 | **31** | 0 | **FULL** |

**1,233 + 4,874 = 6,107.** Every governed object is registered in **exactly one** plane:

* the **corpus plane** (`artifacts.json`) holds `DOCUMENT_ARTIFACT` and nothing else;
* the **repository plane** (`id-ledger`) holds all six other classes and no `DOCUMENT_ARTIFACT`.

**Fully covered: 6,107. Partially covered: 0. Unregistered: 0. Duplicate registrations: 0.**

Constitutional plane: **38 births** — a deliberate subset, governed by `UOBC-BSP-001` (CERTIFIED), where non-birth is `MANDATORY_ABSENCE` or disclosed `DEFERRED` under `G11`.

---

## 5. Duplicate Analysis

Measured, not assumed:

| Test | Result |
|---|---|
| `artifacts.json` paths ∩ `id-ledger` paths | **0** — a perfectly disjoint partition |
| generated-reg ∩ `artifacts.json` | **0** |
| generated-reg ∩ `id-ledger` | **345 / 345** |

The third overlap is **not** duplication: `id-ledger` answers *"what identity does this file hold"*, the generated-artifact registry answers *"what produced it, from what"*. Two questions, one population — the same distinction the Lineage Projection preserved between identity and lineage.

**No duplicate registry. No overlapping ownership. No shadow index. No manually maintained list found.**

### F-W5-1 — eight producer outputs with no located authority
* **Location** — `00-BOOK/DATA/`: `relationships.json` (12,899), `change-ledger.json` (1,358), `control-tower.json` (70), `volumes.json` (25), `certification.json`, `twin.json`, `signals.json`, `connector-cursors.json`.
* **Measured** — each carries `generated_at`/`generator_version` (a producer output), carries **no in-file `authority`**, appears in **no** generated-artifact registry entry (that registry covers **0 of 17** `00-BOOK/DATA` files), and is named by **no** mutation class — `CORPUS_REGISTRATION` names only `id-ledger.json` and `artifacts.json`.
* **Impact** — a reader cannot establish, from any declaration, who owns these registries or under what class they may be mutated. The largest carries 12,899 edges.
* **Authority risk** — **MEDIUM.** Not duplicate authority — *absent* declared authority. They are produced by located tools (`UCOS-UKB-TOOLING`), so ownership is inferable from the producer; it is nowhere declared.

### F-W5-2 — authority is declared five different ways
* **Impact** — no single instrument answers "what is this registry, who owns it, what is its standing" for all 140. This is `GAP B-2` from the Scope B containment determination, now quantified.
* **Authority risk** — **LOW.** Every mechanism is legitimate; the cost is discoverability, not correctness.

---

## 6. Lifecycle Analysis

| Stage | Owner | Rule |
|---|---|---|
| **Creation** | producer, or authored declaration | `GENERATED_ARTIFACT` → declared in the generated-artifact registry |
| **Registration** | `REG-AUTO-001` → `register.sh` Phase 1 (`ukb build --mint`) | `CORPUS_REGISTRATION` is the only class that allocates identity |
| **Update** | the producer, by regeneration | `ukb build` **observes** by default; allocates only under `--mint` |
| **Validation** | `ukb validate` + UGA invariants | declared `verify.sh` stages |
| **Deprecation** | UGA lifecycle state `RETIRED` | identity retained append-only, never reissued |
| **Evolution** | `CEP-009` amendment · `CEP-007 XIII` supersession | append-only |

**Mutation rules are declared** at `mutation-governance-boundary.json` — six classes, each with a named governing authority, and an explicit `does_not_govern` clause stating *"verify.sh — the verification plane observes CORPUS_REGISTRATION and may never perform it."*

**Evidence requirement:** every mutation class names its authority; the register's own invariant is that no mutation class is ungoverned. **F-W5-1 is precisely a population that falls outside every declared class**, which is why it matters.

---

## 7. Verification Coverage

| Capability | Coverage | Mechanism |
|---|---|---|
| Registry completeness | **PARTIAL** | UGA classification is total (catch-all); nothing asserts every registry is declared |
| Registry consistency | **PARTIAL** | `ukb validate` — duplicate IDs, page ranges, parent/dep referential integrity, **projected-Parent backing (F-1)**, **relation-type correctness (ULP)** |
| Orphan detection | **PRESENT** | UGA `EVERY_CANONICAL_ARTIFACT_REGISTERED` — but only **inside declared producer homes**, and `00-BOOK/DATA/` is not one |
| Duplicate detection | **PRESENT** | `ukb validate` duplicate-ID check; `IdentifierDictionary.add` refuses re-binding |
| Stale entry detection | **PARTIAL** | UGA `RETIRED` state; no gate on staleness of a derived registry |
| Authority compliance | **ABSENT** | **Nothing measures that a registry declares its authority.** F-W5-1 survived every gate, which is the proof |

Declared stages that touch registries: `governance enforce --pre` · `registry validate (schema + integrity)` · `universal object governance (UGA-INV-01..10)`.

---

## 8. Evidence Coverage

| Proof | Evidence | State |
|---|---|---|
| Registry ownership | `constitutional-authority-alignment.json` · `mutation-governance-boundary.json` · `producer_homes` (31) | **PARTIAL** — 35 of 140 unlocated |
| Registration correctness | `ukb validate` PASS, 1,233 artifacts; UGA 29/29 | **STRONG** |
| Object coverage | 6,107 objects, exact partition, 0 unregistered | **STRONG** |
| Synchronization | producer fixed point at pass 1; byte-identical regeneration | **STRONG** |
| Historical evolution | `id-ledger.history` 1,470 snapshots; `change-ledger` 1,358 events | **STRONG** |

---

## 9. Identified Gaps

| ID | Gap | Class | Risk |
|---|---|---|---|
| **W5-G1** | 8 producer outputs in `00-BOOK/DATA/` with no located authority and no mutation class | **NEW** | MEDIUM |
| **W5-G2** | No verification that a registry declares its authority — F-W5-1 passed every gate | **NEW** | MEDIUM |
| **W5-G3** | Authority declared five ways; no single instrument answers it for all 140 (`GAP B-2`, quantified) | **NEW** | LOW |
| **W5-G4** | `EVERY_CANONICAL_ARTIFACT_REGISTERED` binds only inside declared producer homes; `00-BOOK/DATA/` is outside | **NEW** | LOW–MEDIUM |
| W5-G5 | No staleness gate on derived registries | NEW | LOW |

**No gap found in object coverage.** That question — the workstream's primary one — is answered cleanly: 6,107 governed objects, exactly one registration each, zero unregistered, zero duplicates.

---

## 10. Implementation Readiness

**READY.** The matrix is buildable now, and it is a **projection over declarations that already exist** — not a new registry.

| Precondition | Status |
|---|---|
| Registry population enumerable | **YES** — 140 measured |
| Authority locatable | **YES for 105**; 35 are the finding, not a blocker |
| Object coverage measurable | **YES** — exact partition proven |
| Duplicate detection possible | **YES** — measured at 0 |
| New authority required | **NONE** |
| New registry required | **NONE** — the matrix must be derived, or it becomes the 141st registry and the defect it was built to detect |

**Scope of an implementable increment**, stated so it cannot drift: a derived matrix over the five existing declaration mechanisms; a verification extension asserting every registry declares its authority (**W5-G2**, which would catch W5-G1); disposition of W5-G1 referred to `UCOS-UKB-TOOLING`.

**Out of scope:** creating any registry, moving any authority, changing any producer, and `G6`/`GAP B-4`.

---

# DISCOVERY COMPLETE
