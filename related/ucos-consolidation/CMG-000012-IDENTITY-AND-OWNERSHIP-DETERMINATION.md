# CMG-000012 IDENTITY AND OWNERSHIP DETERMINATION

> **Mission:** UCOS Ω∞ Universal Lifecycle Evolution Alignment — Workstream 3
> **Baseline:** `5eb1a704` · **Branch:** `integration/recovery-001` · **Date:** 2026-08-17
> **Mode:** Determination. Prerequisite to any population of `CMG-000012`.
> **Authority:** NONE (DERIVED TRUTH). This determination locates owners and resolves a slot conflict. It legislates no model.

---

## 1. Executive determination

**The Universal Context Model already exists as executable law.** It is `UCXI-000001`, implemented in `engine/context/`, and it already declares **exactly the fifteen context kinds** Workstream 3 specifies — same set, no additions, no omissions.

`CMG-000012` therefore **must not define a Universal Context Model.** It is populated instead as the *constitutional declaration that binds to* the located owner: it cites the enumeration, cites the laws, and declares its own non-duplication. It creates no taxonomy, no registry, and no second context authority.

| Question | Determination |
|---|---|
| Canonical identity | `CMG-000012 — Universal Context Model (Constitutional Binding)` |
| Owner | **`engine/context/` (UCXI-000001)** owns the model. `CMG-000012` owns only the constitutional binding statement. |
| Namespace | `00-MASTER/` operational memory (`EXCLUDED_DOCUMENT`). **Not** the `CMG` corpus namespace, which is bound to zone `^00-CMG/`. |
| Authority | NONE — DERIVED TRUTH. Binds; asserts nothing of its own. |
| Relationship to existing CMG artifacts | Downstream of CMG-000001/2/6/11; supersedes CMG-000010's forward claim on the slot |
| Dependencies | CMG-000001, CMG-000002, CMG-000006, CMG-000011, UCXI-000001 |
| Lifecycle inheritance | UCIC-001 (owner) · UCL-000001 (derived truth) · CMG-000001 (law owner) |
| Certification boundary | Certifies the *binding*, never the model. Model conformance is certified by `engine/context/certification.py` and the `CXL-01…12` law checks. |

---

## 2. The located owner: UCXI-000001

`engine/context/` is a 20-module package whose own docstrings identify it as `UCXI-000001`, structured in parts:

| Part | Module | Subject |
|---|---|---|
| 01 | `constitution.py` | **The Context Constitution, as executable law** — twelve laws, each with a computable check |
| 02 | `taxonomy.py` | `ContextKind` — the fifteen universal kinds; `ContextAuthority`, `ContextLifecycle`, `ContextRelation` |
| 03 | `ontology.py` | `UNIVERSAL_DIMENSIONS` — the irreducible shape of each kind |
| — | `registry.py`, `resolution.py`, `composition.py`, `graph.py`, `catalog.py`, `location.py`, `evidence.py`, `validation.py`, `certification.py`, `runtime.py` | registration, resolution, composition, graph, evidence and certification surfaces |

**Verified by execution**, not by reading:

```
$ python -c "from engine.context.taxonomy import UNIVERSAL_KINDS; print(len(UNIVERSAL_KINDS))"
15
```

`engine.context` is already carried in the `pyproject.toml` coverage targets (line 218), so the model is measured on every `./verify.sh` run.

### 2.1 The twelve laws (`CXL-01…12`)

Each law carries a check; the constitution **refuses to construct itself if any law is unchecked** — "a law with no reachable check would be manual governance, which this repository forbids".

| Law | Title |
|---|---|
| CXL-01 | Universal Representability |
| CXL-02 | Bounded Extension |
| CXL-03 | Explicit Boundedness |
| CXL-04 | Context Isolation |
| CXL-05 | Deterministic Identity |
| CXL-06 | Context Once |
| CXL-07 | Explicit Precedence |
| CXL-08 | Mandatory Provenance |
| CXL-09 | Sealed Content |
| CXL-10 | Zero Authority |
| CXL-11 | Fail-Closed |
| CXL-12 | Append-Only History |

**`CXL-06` Context Once — "one canonical home per unit of context" — is dispositive.** A second Universal Context Model in `CMG-000012` would violate the model's own first-order law. `CAA-INV-07` (no instrument declares a rival object model) independently forbids it.

### 2.2 The fifteen kinds and their declared shapes

Every kind declares three required dimensions plus one optional `note`. Unknown dimensions are refused, "because an undeclared field is an unbounded assumption".

| # | WS3 context | `ContextKind` | Required dimensions |
|---|---|---|---|
| 1 | Existence Context | `EXISTENCE` | `existence_mode` · `substrate` · `boundary` |
| 2 | Reality Context | `REALITY` | `reality_mode` · `fidelity` · `verifiability` |
| 3 | Observer Context | `OBSERVER` | `observer_id` · `vantage` · `epistemic_access` |
| 4 | Spatial Context | `SPATIAL` | `reference_frame` · `extent` · `locality` |
| 5 | Temporal Context | `TEMPORAL` | `reference_frame` · `ordering` · `resolution` |
| 6 | Identity Context | `IDENTITY` | `subject` · `identifier` · `authority` |
| 7 | Knowledge Context | `KNOWLEDGE` | `source` · `provenance` · `confidence` |
| 8 | Governance Context | `GOVERNANCE` | `authority` · `policy` · `decision_rights` |
| 9 | Security Context | `SECURITY` | `classification` · `trust_boundary` · `controls` |
| 10 | Computational Context | `COMPUTATIONAL` | `substrate` · `execution_model` · `resources` |
| 11 | Environmental Context | `ENVIRONMENTAL` | `medium` · `conditions` · `constraints` |
| 12 | Regulatory Context | `REGULATORY` | `jurisdiction` · `obligations` · `compliance_state` |
| 13 | Economic Context | `ECONOMIC` | `cost_model` · `value_basis` · `scarcity` |
| 14 | Cultural Context | `CULTURAL` | `locale` · `norms` · `conventions` |
| 15 | Linguistic Context | `LINGUISTIC` | `language` · `register` · `encoding` |

**Coverage of the WS3 requirement: 15 / 15, exact.** No context requested by Workstream 3 is missing, and the model declares none beyond them.

---

## 3. The slot conflict

`CMG-000012` carried **four mutually inconsistent claims** before this determination:

| Source | Claim |
|---|---|
| Disk | `00-MASTER/CMG-000012/CMG-000012-UNIVERSAL-CONTEXT-MODEL.md` — **0 bytes** |
| `CMG-000010` ×6 (lines 71, 1408, 1436, 1469, 1966, 1991) | "Future CMG-000012: **Decision-Making Model** (will use trust in decisions)" |
| `CMG-000001` §1.1 line 63 | `CMG-000012+ (To Be Defined)` |
| `00-CMG/CMG-000012-…` | **Constitutional Implementation Readiness Assessment** — the namespace owner's occupant of ID 12 |

### 3.1 Namespace resolution

`00-BOOK/tools/config.py` `RECONCILED_SETS` binds namespace `CMG` to **zone `^00-CMG/`** under `namespace_owner: CMG-000001`. `00-MASTER/CMG-000012/…` lies outside that zone and is classified `EXCLUDED_DOCUMENT` (`UCOS-EXDOC-002424`), authority tier advisory.

**Determination:** the two artifacts do not collide, because they are not in the same namespace. `00-CMG/CMG-000012` holds corpus identity `CMG-000012`; `00-MASTER/CMG-000012` is operational memory whose directory name is a *label*, not a namespace claim. This determination does not alter either. The pre-existing dual-series condition remains a reported risk, unchanged by this cycle.

### 3.2 Subject resolution

**Determination: slot `CMG-000012` in the `00-MASTER` CMG Foundation series resolves to Universal Context Model (Constitutional Binding).**

Grounds:
1. The **filename on disk** already declares Universal Context Model, and the directory was created for that subject.
2. The subject **has a located owner** (`UCXI-000001`) with a complete, executable, gate-measured model. Decision-Making has no located owner.
3. `CMG-000001` §1.1 records the slot as *undefined*, so no prior definition is displaced.
4. `CMG-000010`'s claim is explicitly **forward-looking** ("Future CMG-000012"), i.e. a reservation, not an allocation. A reservation yields to an allocation with a located owner.

**Consequence for Decision-Making:** its slot reservation is **withdrawn without reallocation**. Minting a replacement number would be a namespace act this determination has no authority to perform, and an unowned forward reservation is precisely the dangling-reference defect Workstream 1 remedied. `CMG-000010` is corrected to name Decision-Making as an *unallocated* future subject.

---

## 4. Non-duplication boundary

`CMG-000012` is bounded by what it must not do:

| `CMG-000012` does NOT | Owner that does |
|---|---|
| Declare context kinds | `engine/context/taxonomy.py` (`ContextKind`) |
| Declare dimensional shapes | `engine/context/ontology.py` (`UNIVERSAL_DIMENSIONS`) |
| Declare context laws | `engine/context/constitution.py` (`CXL-01…12`) |
| Register or resolve contexts | `engine/context/registry.py`, `resolution.py` |
| Mint context identity | `engine/context/registry.py` under `CXL-05` |
| Certify context conformance | `engine/context/certification.py` |
| Grant authority from context | **Nobody** — `CXL-10` Zero Authority: context describes, never grants |

What `CMG-000012` *does*: state, at constitutional level, that context in UCOS Ω∞ is universal, bounded, representation-independent, and owned by exactly one home — and name that home.

---

## 5. Independence requirements

Workstream 3 requires technology-, instance- and representation-independence. Each is already discharged by the located owner, and `CMG-000012` cites rather than restates:

| Requirement | Mechanism | Location |
|---|---|---|
| **Technology-independent** | Kinds and dimensions are DATA; "no control flow here branches on a specific kind" | `ontology.py` docstring |
| **Instance-independent** | Identity is "a pure function of its identity tuple" (`CXL-05`); every context bound to exactly one frame (`CXL-03`) | `constitution.py` |
| **Representation-independent** | `LINGUISTIC` carries `encoding` as a *dimension of the subject*, not of the model; `REALITY` separates `reality_mode`/`fidelity` from the actual | `ontology.py` |
| **Open to the unknown** | `CXL-02` Bounded Extension — "a future context type is admitted as data, never invented at a call site"; `ontology.extend()` returns a new immutable ontology | `constitution.py`, `ontology.py` |

The fifteen kinds are therefore a **closed set that is open to declared extension** — the same discipline UCL-000001's stage manifest uses.

---

## 6. Lifecycle inheritance and certification boundary

| Property | Binding |
|---|---|
| Universal Identity | `UCOS-EXDOC-002424` (already minted, path-keyed) |
| Temporal existence | CMG-000002 Universal Temporal Existence Contract |
| Certified Temporal Baseline | This cycle's commit; CEP-005 certification channel |
| Immutable historical lineage | Append-only ledgers; `CXL-12` for context history |
| Governed evolution | CEP-009 amendment · Article-14 perpetual cycle |
| Lifecycle authority | UCIC-001 (owner) · UCL-000001 (derived truth, not supreme) |
| Independent lifecycle defined | **None** |

**Certification boundary.** `CMG-000012` certifies exactly one proposition: *that the binding it declares is accurate.* It certifies nothing about context conformance — that is measured by `CXL-01…12` and `engine/context/certification.py`, and a divergence there is a failure in `engine/context/`, never in `CMG-000012`.

---

## 7. Determination summary

| Item | Determination |
|---|---|
| Define a new Universal Context Model in CMG-000012 | **REFUSED** — `UCXI-000001` owns it; would breach `CXL-06` and `CAA-INV-07` |
| Canonical subject of the slot | **Universal Context Model (Constitutional Binding)** |
| Model owner | `engine/context/` — `UCXI-000001` |
| Fifteen contexts covered | **15 / 15**, verified by execution |
| Decision-Making reservation | **Withdrawn without reallocation**; `CMG-000010` corrected |
| `CMG-000001` §1.1 slot record | Updated from "To Be Defined" to the resolved subject |
| Namespace | `00-MASTER/` operational memory; no `00-CMG` collision created |
| Authorisation to populate | **GRANTED**, bounded by §4 |

**Population of `CMG-000012` is authorised under this determination and bounded by §4.**

---

**END CMG-000012 IDENTITY AND OWNERSHIP DETERMINATION**

**Status:** Evolution Baseline Established v1.0
**Lifecycle Authority:** UCIC-001 (owner) · UCL-000001 (derived) · CMG-000001 (law)
**Governed Evolution:** ENABLED
