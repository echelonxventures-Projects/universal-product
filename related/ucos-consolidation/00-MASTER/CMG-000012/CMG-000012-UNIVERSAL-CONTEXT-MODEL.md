# CMG-000012 — UNIVERSAL CONTEXT MODEL (CONSTITUTIONAL BINDING)

**Document Type:** Constitutional Meta-Governance — Binding Declaration
**Version:** 1.0
**Status:** Evolution Baseline Established
**Lifecycle State:** ACTIVE
**Evolution State:** ENABLED
**Baseline Date:** 2026-08-17
**Scope:** 0 → Ω∞

**Authority:** NONE — DERIVED TRUTH. This instrument binds; it declares no model of its own.
**Universal Identity:** `urn:ucos:ucko:ucos.cmg:CMG-000012`
**Identity Plane:** UCKP-ART-05 (`engine/uckp/identity.py`, role SUPREME) — derived, not minted
**Birth Record:** `00-MASTER/UOBC-000001/birth-ledger.json` under UOBC-000001
**Creation Coordinate:** `logical:ucos-repository-history@1#484` (CMG-000002; clock-free logical time)
**Model Owner:** `engine/context/` — UCXI-000001
**Authorised by:** `CMG-000012-IDENTITY-AND-OWNERSHIP-DETERMINATION.md`

---

## LIFECYCLE METADATA

**Governance Inheritance:**
- UCIC-001 Universal Capability Implementation Contract v1.0 — lifecycle owner
- UCL-000001 Universal Constitutional Lifecycle — derived lifecycle truth (not supreme authority)
- CEP-009 Constitutional Amendment & Evolution Constitution — governed evolution channel
- CMG-000001 Constitutional Meta-Governance v1.0 — law owner

**Lifecycle Compliance:**
- ✓ Inherits the universal lifecycle
- ✓ No independent lifecycle defined
- ✓ No independent evolution authority
- ✓ Evolution enabled from baseline

---

## PREAMBLE

This instrument establishes, at constitutional level, that **context in UCOS Ω∞ is universal, bounded, representation-independent, and owned by exactly one home.**

It does not define that context. The Universal Context Model exists as **executable law** in `engine/context/` under UCXI-000001, where fifteen universal context kinds, their irreducible dimensional shapes, and twelve context laws are declared as data and measured by computable checks.

**Critical principle:**

> **Context describes. It never grants.**

Observation is not permission. A context may record that an observer occupies a vantage, that a subject falls under a jurisdiction, or that an assertion carries a confidence — and none of those facts confers authority on anything. This is `CXL-10` (Zero Authority), and it applies to this instrument as much as to any context instance.

**Why this instrument is a binding and not a model.**

`CXL-06` — *Context Once: one canonical home per unit of context* — is a law of the model itself. A second Universal Context Model declared here would violate the first-order law of the thing it purported to define, and would additionally breach `CAA-INV-07` (no instrument declares a rival object model). The constitutionally correct act is therefore to **name the home**, not to duplicate it.

---

## SECTION 1: BINDING DECLARATION

### 1.1 What is bound

| Element | Bound to | Never redeclared here |
|---|---|---|
| Context kinds | `engine/context/taxonomy.py` — `ContextKind`, `UNIVERSAL_KINDS` | ✓ |
| Dimensional shapes | `engine/context/ontology.py` — `UNIVERSAL_DIMENSIONS` | ✓ |
| Context laws | `engine/context/constitution.py` — `CXL-01…12`, `LAW_CHECKS` | ✓ |
| Authority ranking | `engine/context/taxonomy.py` — `ContextAuthority` | ✓ |
| Context lifecycle | `engine/context/taxonomy.py` — `ContextLifecycle` | ✓ |
| Relations | `engine/context/taxonomy.py` — `ContextRelation` | ✓ |
| Registration & identity | `engine/context/registry.py` under `CXL-05` | ✓ |
| Resolution & composition | `engine/context/resolution.py`, `composition.py` | ✓ |
| Evidence & certification | `engine/context/evidence.py`, `certification.py` | ✓ |

### 1.2 Binding law

**Law C-1 — Single Context Home**

**Statement:** Context has exactly one canonical home in UCOS Ω∞, and that home is UCXI-000001 (`engine/context/`).

**Formal:**
```
∀ c ∈ Context: home(c) = UCXI-000001
∧ ¬∃ M ≠ UCXI-000001 : declares_context_model(M)
```

**Proof:** By `CXL-06` (Context Once), enforced by its own computable check; and by `CAA-INV-07`, measured over the version-controlled boundary by `uga_engine.py gate`. This instrument declares no model, so it is not a counterexample.

**Law C-2 — Binding Carries No Authority**

**Statement:** This instrument grants no authority to itself, to context, or to any consumer of context.

**Formal:**
```
authority(CMG-000012) = ∅
∀ c ∈ Context: grants(c) = ∅
```

**Proof:** By `CXL-10` (Zero Authority), which the model applies to its own constitution module. This instrument's declared authority is `NONE — DERIVED TRUTH`.

**Law C-3 — Bounded Openness**

**Statement:** The set of context kinds is closed at fifteen and open only to declared extension; no kind is invented at a call site.

**Formal:**
```
|UNIVERSAL_KINDS| = 15
∧ admit(k_new) ⟹ declared_as_data(k_new) ∧ has_shape(k_new)
```

**Proof:** By `CXL-01` (Universal Representability) and `CXL-02` (Bounded Extension). `ontology.extend()` admits a future kind's dimensions and returns a new immutable ontology; unknown dimensions are refused at construction.

---

## SECTION 2: THE FIFTEEN UNIVERSAL CONTEXTS

Bound from `UNIVERSAL_KINDS` and `UNIVERSAL_DIMENSIONS`. Each kind declares three required dimensions and one optional `note`. **This table is a citation, not a declaration** — the authority is the code.

| # | Context | Kind | Required dimensions | What it answers |
|---|---|---|---|---|
| 1 | Existence | `EXISTENCE` | `existence_mode` · `substrate` · `boundary` | In what mode does the subject exist, in what, and bounded how |
| 2 | Reality | `REALITY` | `reality_mode` · `fidelity` · `verifiability` | Actual, modelled, simulated or hypothetical — and checkable how |
| 3 | Observer | `OBSERVER` | `observer_id` · `vantage` · `epistemic_access` | Who observes, from where, and what they can know |
| 4 | Spatial | `SPATIAL` | `reference_frame` · `extent` · `locality` | In which frame, occupying what, where relative to the observer |
| 5 | Temporal | `TEMPORAL` | `reference_frame` · `ordering` · `resolution` | Against which clock, ordered how, at what granularity |
| 6 | Identity | `IDENTITY` | `subject` · `identifier` · `authority` | Who the subject is, under which identifier, minted by whom |
| 7 | Knowledge | `KNOWLEDGE` | `source` · `provenance` · `confidence` | Where the claim came from, through what chain, held how firmly |
| 8 | Governance | `GOVERNANCE` | `authority` · `policy` · `decision_rights` | Under whose authority, which policy, who may decide |
| 9 | Security | `SECURITY` | `classification` · `trust_boundary` · `controls` | Classified how, inside which boundary, under what controls |
| 10 | Computational | `COMPUTATIONAL` | `substrate` · `execution_model` · `resources` | On what substrate, under which execution model, with what resources |
| 11 | Environmental | `ENVIRONMENTAL` | `medium` · `conditions` · `constraints` | In what medium, under which conditions, against what constraints |
| 12 | Regulatory | `REGULATORY` | `jurisdiction` · `obligations` · `compliance_state` | Under which jurisdiction, owing what, currently compliant or not |
| 13 | Economic | `ECONOMIC` | `cost_model` · `value_basis` · `scarcity` | Costed how, valued on what basis, scarce in what way |
| 14 | Cultural | `CULTURAL` | `locale` · `norms` · `conventions` | In which locale, under what norms and conventions |
| 15 | Linguistic | `LINGUISTIC` | `language` · `register` · `encoding` | In what language, at what register, under which encoding |

**Coverage:** 15 / 15 of the contexts required of this instrument. Verifiable by execution:

```
python -c "from engine.context.taxonomy import UNIVERSAL_KINDS; print(len(UNIVERSAL_KINDS))"
→ 15
```

---

## SECTION 3: INDEPENDENCE PROPERTIES

### 3.1 Technology independence

Kinds and dimensions are declared as **data**. The ontology's own constraint: *"No control flow here branches on a specific kind."* Adding a substrate, protocol, language or platform requires no change to context logic, because no context logic names a technology.

### 3.2 Instance independence

`CXL-05` (Deterministic Identity): a context's identity is a pure function of its identity tuple, minted by the single registration authority. Two observers deriving the same tuple derive the same identity. `CXL-03` (Explicit Boundedness) binds every context to exactly one frame, so an instance never leaks into another's frame — `CXL-04` (Context Isolation) requires explicit federation for any crossing.

### 3.3 Representation independence

Representation is modelled as a **property of the subject, never of the model**:

- `LINGUISTIC.encoding` carries the encoding of the subject; the model itself is encoding-neutral.
- `REALITY.reality_mode` and `REALITY.fidelity` separate the representation from the actual, so a simulated subject and an actual one are distinguishable *within* the model rather than requiring two models.
- `TEMPORAL.reference_frame` and `SPATIAL.reference_frame` name the frame instead of assuming one, matching CMG-000002's rule that no specific time representation is mandated.

### 3.4 Openness to the unknown

`CXL-02` (Bounded Extension): the taxonomy is open, but only through declaration. A future context kind — including one no present technology or civilisation would name — is admitted as data with a declared shape. An undeclared field is refused, "because an undeclared field is an unbounded assumption".

---

## SECTION 4: DEPENDENCIES

### 4.1 Upstream

| Dependency | Provides |
|---|---|
| **CMG-000001** Constitutional Meta-Governance | Constitutional framework; law owner |
| **CMG-000002** Universal Temporal Existence Contract | Temporal coordinate model underlying `TEMPORAL` |
| **CMG-000006** Universal Authority Identity Model | Authority identity underlying `IDENTITY` |
| **CMG-000011** Universal Evidence Existence Model | Evidence model underlying `KNOWLEDGE` provenance |
| **UCXI-000001** (`engine/context/`) | **The Universal Context Model itself** |

### 4.2 Downstream

| Dependent | Uses |
|---|---|
| All authorities asserting context | The fifteen kinds and their shapes |
| `engine/uicm` closure measurement | Context dimensions as closure dimensions |
| Future constitutional objects | Context as a described, never-granting substrate |

### 4.3 External

None. `engine/context/` is in-repository and gate-measured.

---

## SECTION 5: BOUNDARIES

### 5.1 What this instrument defines

✓ That context has exactly one canonical home, and which home that is
✓ That the binding carries no authority
✓ That the kind set is closed at fifteen and open only to declared extension

### 5.2 What this instrument does NOT define

❌ Context kinds — `engine/context/taxonomy.py`
❌ Dimensional shapes — `engine/context/ontology.py`
❌ Context laws — `engine/context/constitution.py`
❌ Registration, resolution, composition — `registry.py`, `resolution.py`, `composition.py`
❌ Context identity minting — `registry.py` under `CXL-05`
❌ Context certification — `certification.py`
❌ Any grant of authority — forbidden to everyone by `CXL-10`
❌ Decision-making frameworks — no located owner; slot reservation withdrawn by determination

---

## SECTION 6: EVOLUTION MODEL

| Property | Binding |
|---|---|
| Baseline | Evolution Baseline Established v1.0 |
| Universal Identity | `urn:ucos:ucko:ucos.cmg:CMG-000012` — derived at birth under UCKP-ART-05, before this artifact existed |
| Repository serial | `UCOS-EXDOC-002424` — the PERSISTENCE binding, path-keyed, issued by the one mint |
| Certified Temporal Baseline | `logical:ucos-repository-history@1#484` — clock-free logical coordinate resolved through `engine/temporal/` under CMG-000002; CEP-005 certification channel |
| Immutable historical lineage | Append-only; birth record in `00-MASTER/UOBC-000001/birth-ledger.json` keyed by identity; context history hash-chained under `CXL-12` |
| Governed evolution | CEP-009 amendment · Article-14 perpetual cycle (`engine/uckp/evolution.py`) |
| Identity across evolution | **Unchanged.** Identity has no path input and no timestamp input, so neither a move nor an amendment can replace it (UOBC-L-07) |
| Uncontrolled mutation | Refused — `CXL-11` Fail-Closed |

**No object is permanently frozen, including this one.** Extension of the context kind set is a governed evolution through `CXL-02` and `ontology.extend()`. Amendment of this binding is a governed evolution through CEP-009. Identity remains stable; history remains append-only.

---

## SECTION 7: CERTIFICATION BOUNDARY

This instrument certifies exactly one proposition: **that the binding declared in Section 1 is accurate.**

It certifies nothing about context conformance. That is measured by `CXL-01…12`, whose checks are computed from the registry, the graph and the composition, and by `engine/context/certification.py`. A conformance divergence is a failure in `engine/context/` — never in this document.

| Criterion | Measured by |
|---|---|
| Binding accuracy | `UNIVERSAL_KINDS` resolves to 15; `CONTEXT_LAWS` resolves to `CXL-01…12` |
| Model conformance | `LAW_CHECKS` in `engine/context/constitution.py` |
| Coverage | `pyproject.toml` `--cov=engine.context` |
| No rival model | `CAA-INV-07` via `uga_engine.py gate` |

---

## SECTION 8: CONSTITUTIONAL COMPLETENESS MATRIX

| Dimension | Status | Evidence |
|---|---|---|
| Ontology | ✓ Bound | §2; `engine/context/ontology.py` |
| Taxonomy | ✓ Bound | §2; `engine/context/taxonomy.py` (15 kinds) |
| Boundary | ✓ Complete | §5 — explicit, with owner named per exclusion |
| Dependency | ✓ Complete | §4 — 5 upstream, all resolving, none external |
| Evidence | ✓ Complete | §7 — every criterion has a named measurer |
| Governance | ✓ Complete | Law owner CMG-000001; model owner UCXI-000001 |
| Security | ✓ Bound | `SECURITY` kind; `CXL-10` Zero Authority |
| Evolution | ✓ Complete | §6 — CEP-009 · Article-14 · `CXL-02` |
| Laws | ✓ Complete | §1.2 — C-1, C-2, C-3 stated and proven |
| Proofs | ✓ Complete | §1.2 — each proof cites an enforced check or invariant |
| Implementation | ✓ Located | `engine/context/`, 20 modules, coverage-tracked |
| Certification | ✓ Complete | §7 — boundary explicit |
| Non-duplication | ✓ Complete | §5.2; `CXL-06`; `CAA-INV-07` |

**Completeness is completeness of the binding, not of the model.** The model's completeness is UCXI-000001's to hold.

---

## SECTION 9: EVOLUTION BASELINE DECLARATION

**I DECLARE:**

`CMG-000012` — Universal Context Model (Constitutional Binding) has achieved:

✓ **Binding accuracy** — 15 / 15 kinds, verified by execution
✓ **Dependency closure** — 5 upstream, all located, none external, no cycle introduced
✓ **Boundary integrity** — every exclusion names its owner
✓ **Non-duplication** — no rival model, no second context authority, no registry opened
✓ **Zero authority** — `CXL-10` applied to itself
✓ **Lifecycle inheritance** — UCIC-001 owner; UCL-000001 derived; no independent lifecycle

```
═══════════════════════════════════════════════════════════════════════════════
CMG-000012 — UNIVERSAL CONTEXT MODEL (CONSTITUTIONAL BINDING)
═══════════════════════════════════════════════════════════════════════════════

Status:              EVOLUTION BASELINE ESTABLISHED v1.0
Lifecycle State:     ACTIVE
Evolution State:     ENABLED
Baseline Date:       2026-08-17
Scope:               0 → Ω∞
Model Owner:         UCXI-000001 (engine/context/)
Governance:          UCIC-001 (owner) · UCL-000001 (derived) · CMG-000001 (law)
Authority:           NONE — DERIVED TRUTH
Contexts Bound:      15 / 15
Dependencies:        ALL LOCATED
Boundaries:          ALL ENFORCED
Evolution:           PERMITTED within constitutional constraints

═══════════════════════════════════════════════════════════════════════════════
```

---

**END CMG-000012 — UNIVERSAL CONTEXT MODEL (CONSTITUTIONAL BINDING)**

**Constitutional Lifecycle Status:** ✓ EVOLUTION BASELINE ESTABLISHED v1.0
**Certified Temporal Baseline:** 2026-08-17 (CMG-000002 coordinate · CEP-005 channel)
**Governed Evolution:** ENABLED — CEP-009 · Article-14 · `CXL-02`
