# SCOPE B — Universal Birth Governance Determination

| Field | Value |
|---|---|
| ARTIFACT | Scope B · Workstream 2 — Birth Population Boundary, Historical / Derived / Future Object Treatment |
| MODE | **DETERMINATION ONLY.** No implementation, no birth record generated, no identifier minted, no migration executed. |
| CONSTITUENT AUTHORITY | **NONE** |
| PREDECESSOR | `SCOPE-B-DISCOVERY-REPORT.md` · `SCOPE-B-IDENTITY-CONTAINMENT-DETERMINATION.md` |
| BINDING PRIOR | `UNIVERSAL-IDENTITY-MIGRATION-DETERMINATION.md` — G11 disposition governs |

---

## 0. The measurement that governs every determination below

**35 birth records. 6,079 governed objects. 0 anonymous objects.**

Those three numbers are not in tension, and reading them as "6,044 missing birth records" would be the central error this determination exists to prevent.

`UNIVERSAL-IDENTITY-MIGRATION-DETERMINATION.md` already measured the population: 1,371 eligible artifacts, 1,233 registered in `artifacts.json`, **138 unregistered-but-not-anonymous** — every one holds UGA identity as `EXCLUDED_DOCUMENT`. **Anonymity is already zero.** Birth records are not the only way an object holds identity; they are how an object holds identity **on the constitutional plane**.

The mandate's own instruction is the operative constraint: **"Do not blindly generate."**

---

## 1. Birth Population Boundary

### 1.1 The distinction that decides the boundary

| | Repository plane | Constitutional plane |
|---|---|---|
| Identity shape | `UCOS-<CATEGORY>-<NNNNNN>` | `urn:ucos:ucko:<namespace>:<local_name>` |
| Granted by | UGA classification of a version-controlled file | UOBC birth, from **birth facts** |
| Answers | "which file is this" | "which constitutional object is this" |
| Coverage | 6,079 / 6,079 | 35 |

UOBC's own rationale states the difference precisely: *"A path-derived identity is an **address**, not an identity — UCKP Article 5 says so in its own first sentence — and an address changes when a file moves."*

**A birth record is therefore required exactly when an object's identity must survive the loss of its address.** A file that is only ever a file needs an address. A constitutional object needs an identity.

### 1.2 Determination by object class

| UGA class | Count | Birth identity | Birth record | Lifecycle activation | Basis |
|---|---|---|---|---|---|
| `DOCUMENT_ARTIFACT` | 1,233 | **NOT REQUIRED** | not required | already `AUTHORED` | Governed by UMB-IMP-001 with its own `parent` lineage; a second identity plane over it would be duplicate authority |
| `EXECUTABLE_OBJECT` | 1,254 | **REQUIRED at package granularity** | **REQUIRED — package, not file** | required | A capability is the constitutional object; a module file is its address. Precedent: `engine.infinite_scope`, `engine.root_ontology` are born as packages |
| `TEST_OBJECT` | 821 | **REQUIRED at suite granularity** | **REQUIRED — suite, not file** | required | Precedent: `test_infinite_scope`, `test_root_ontology` |
| `DATA_OBJECT` | 122 | **REQUIRED when it is a declaration** | **REQUIRED for declarations only** | required | A programme declaration is a constitutional object (`ucpa-declaration.json`). A derived `.json` surface is not |
| `CONFIGURATION_OBJECT` | 31 | **NOT REQUIRED** | not required | `AUTHORED` | Parameterises execution; holds no constitutional standing |
| `TOOLING_OBJECT` | 36 | **NOT REQUIRED** | not required | `AUTHORED` | *"a registry must not register itself"* — declared exclusion, "NOT therefore exempt from identity", which it holds on the repository plane |
| `EXCLUDED_DOCUMENT` | 2,582 | **NOT REQUIRED** | not required | `AUTHORED` | Holds UGA identity; explicitly the class that makes anonymity zero |
| **Determinations / registers** | — | **REQUIRED** | **REQUIRED** | required | Precedent: 14 `ucos.determination` births already exist |

**DETERMINED: the in-scope birth population is capabilities, test suites, programme declarations and determinations — not files.** Granularity is the constitutional object, never the path.

### 1.3 What this is not

**This determination does not authorize generating birth records for the classes marked REQUIRED above.** It determines *which classes are in scope*. Corpus-wide adoption remains pre-existing gap **G11**, whose disposition is already determined and is **not** reopened here: *"an explicit `register.sh` migration transaction, not a verification-time backfill."*

---

## 2. Historical Object Treatment

| Class | Population | Treatment | Basis |
|---|---|---|---|
| Frozen corpus (`00-BOOK/`, `00-SOURCE/`, `99-FREEZE/`) | — | **PRESERVE** | `DP-03` / `C-01`: read-only to implementation. *"rewriting it would falsify history rather than advance it"* |
| `RETIRED` ledger entries | **2** | **PRESERVE** — never reissue, never delete | Declared lifecycle state; append-only ledger |
| Pre-UOBC objects holding repository identity only | 6,044 | **DEFER** | G11 disposition; migration is an explicit transaction with a named owner |
| Superseded determinations (e.g. MIP-v2 root-ontology clause) | — | **ARCHIVE in place** — classify, never edit | Scope A precedent; `CEP-007 XIII` supersession is the forward channel |
| Deleted paths (`CURRENT-REPOSITORY-STATE.txt`) | 1 | **RETIRE** — identity retained, never reissued | Declared `RETIRED` semantics |

**Nothing is migrated by this determination. Nothing is archived by this determination. Nothing is retired by this determination.**

---

## 3. Derived Object Treatment

**344 objects carry `lifecycle: GENERATED`.**

| Attribute | How a generated artifact receives it |
|---|---|
| **Identity** | UGA classification at producer output; repository plane. **The producer does not mint** — it emits, UGA classifies |
| **Ownership** | Ownership rules resolve the owner from the path; the **producer** is additionally recorded in `producer` |
| **Lineage** | `generated-artifact-registry.json` names the `canonical_path` and its producer — the producer *is* the lineage edge |
| **Evidence** | `evidence_class` / `evidence_boundary` on the registry entry |
| **Lifecycle status** | `GENERATED` — *"Emitted by a declared producer. Named as a canonical_path in the generated-artifact registry"* |

**DETERMINED: a generated artifact shall never receive a birth record.** Its constitutional identity is its **producer's**. Giving a derived surface an independent constitutional identity would make it capable of diverging from what produced it — which is precisely what "derived truth" forbids. The Scope A derived registers (UGA, UAIE, UCAF, UAKOS surfaces) are governed correctly today under this rule.

**Consequence for replay:** a generated artifact must reach a **fixed point** under its producer. Scope A measured this discipline (fixed point at pass 2 across five producers) and it is hereby determined as the standing requirement for every derived surface.

---

## 4. Future Object Creation Model

**DETERMINED lifecycle for every object created after this determination:**

```
Intent
  ↓                         UCL-S-0010 Receive Goal            [judgement — unbound]
Discovery
  ↓                         UCL-S-0040…0100                    [bound]
Classification
  ↓                         UGA object_class (total, catch-all)
Ownership
  ↓                         UGA ownership rules (5, total)
Birth Determination
  ↓                         §1.2 of this determination
Identity Assignment
  ↓                         UCL-S-0310 · UCKP-ART-05 · derive, never count
Registration
  ↓                         UCL-S-0300/0330 · UGA producer run
Lifecycle Activation
                            UOBC initial_state ACTIVE · UCIC-001 owner
```

**Enforcement already exists and is not re-created:** `identity_exists` flips exactly once, at `UOBC-S-04` (ordinal 40); `UOBC-L-01` refuses any stage instantiating an artifact at or below it; `UOBC-L-06` refuses registration before identity. **"No anonymous existence" and "no later identity discovery" are structural, not aspirational.**

**Ordering constraint determined:** Birth Determination precedes Identity Assignment. An object whose class does not require a birth record still receives repository identity at Classification — it is never anonymous, it is simply addressed rather than born.

---

## 5. UELA consumption of this capability

| UELA need | Supplied by | Status |
|---|---|---|
| Which objects have constitutional identity | birth ledger, 35 | available |
| Which objects have repository identity | UGA registry, 6,079 | available |
| Whether a new object requires birth | **§1.2 of this determination** | **determined here** |
| Lifecycle activation state | UOBC `initial_state`, `lifecycle_binding` | available |
| Creation event / temporal coordinate | UOBC `creation_timestamp` (logical, never a clock) | available |
| Creator authority | UOBC `creation_context.governance` | available |
| Parent relationship | UOBC `parent_identity` | available |
| Evidence reference | UOBC `certification_boundary` | available |

**UELA blocking prerequisite from this workstream:** §1.2 must be **machine-readable** before UELA can automate Birth Determination. A determination that lives only in prose cannot be consumed by an orchestrator — the exact defect Scope A's `UCPA-000001` was built to close for the root ontology. **This is the strongest candidate for the first Scope B implementation.**

---

## 6. Validation of this determination

| Requirement | Status |
|---|---|
| No implementation performed | **CONFIRMED** |
| No identities minted | **CONFIRMED** — no producer run |
| No birth records generated | **CONFIRMED** — ledger remains at 35 |
| No migration executed | **CONFIRMED** — G11 not reopened |
| No registries changed | **CONFIRMED** |
| No duplicate authority proposed | **CONFIRMED** — UOBC extended in scope of application only |
| Existing capabilities reused | **CONFIRMED** — UOBC, UGA, UCL, UCKP-ART-05 |
| Infinite scope preserved | **CONFIRMED** — class table is open; a future class takes a row, not an engine change |
| Unknown future objects discoverable | **CONFIRMED** — UGA classification is total by catch-all, so an unknown class self-opens |

---

*End of SCOPE-B-BIRTH-GOVERNANCE-DETERMINATION.md*
