# UCPA-001 — Constitutional Primitive Alignment Determination

| Field | Value |
|---|---|
| ARTIFACT ID | `UCPA-000001` |
| ARTIFACT | Universal Constitutional Primitive Alignment — Reconciliation Determination |
| PHASE | PHASE 1 — FOUNDATION COMPLETION · Scope A |
| CHECKPOINT | `bb9c27d2` (integration/recovery-001) |
| CLASSIFICATION | Reconciliation Determination — **DERIVED TRUTH** |
| CONSTITUENT AUTHORITY | **NONE** |
| GOVERNANCE AUTHORITY | **NONE** |
| RATIFICATION AUTHORITY | **NONE** |
| PREDECESSORS | `P1-A-01-ROOT-ONTOLOGY-DISCOVERY-REPORT.md`, `P1-A-02-ROOT-ONTOLOGY-IMPLEMENTATION-PLAN.md` |
| POSTURE | Reconciliation only. No model replaced. No primitive created. No register edited. |

---

## Preamble — what this determination is not

It does not create, rename, reinterpret or renumber a constitutional primitive. It does
not amend the 33-facet model. It does not edit the canonical register or the ratification
record. Scope A instructs: *"Do not replace existing models. Create reconciliation
determination."* This is that determination, and its entire substance is the assignment of
**roles** to artifacts that already exist and the making **computable** of an adjudication
that was already **ratified**.

Every conclusion below was decided by Repository Truth already on the record. Nothing here
is a new architectural choice, and this artifact holds no authority to make one.

---

## 1. The settled law this determination applies

`02-MASTER/UCOS-RAT-001-REPOSITORY-RATIFICATION-DETERMINATION.md` §4, recorded at
`01-WORKING/SUPERSESSION-REGISTER.md` and reflected at `01-WORKING/ONTOLOGY-REGISTER.md`
Part A:

| Decision | Supersession | Content | Status |
|---|---|---|---|
| `RAT-01` | `SUP-01` | **BEING = axiom-only (non-layer)** — "supreme as the ground of the order… but is **not** an addressable node in the layered derivation tree" | **RATIFIED** |
| `RAT-02` | `SUP-07` | **4-primitive** canonical form — `EXISTENCE → RELATIONSHIP → TRANSFORMATION`, beneath the BEING axiom | **RATIFIED** |
| `RAT-03` | `SUP-02` | **SPACE-TIME is a coordinate**, not a root primitive; `Ω-LAW-02` retired as a root law | **RATIFIED** |

This determination changes none of it and derives everything from it.

---

## 2. Determination 1 — Ownership (disposition of SC-A-01)

Three artifacts made an ownership claim over the root ontology. They are **not** three
competing owners; two of them are claims about **different roles**, and exactly one is a
genuine conflict.

| Claimant | Claim | Role determined | Disposition |
|---|---|---|---|
| `02-MASTER/UCOS-RAT-001-…md:88` | Root ontology's source is `SRC-02` | **CONSTITUENT SOURCE** | **UPHELD.** Source is origin. `SRC-02` is frozen corpus (`00-SOURCE/`), read-only to implementation under `DP-03`. Origin is not repository-truth ownership; the roles do not compete. |
| `00-MASTER/URRC-000001/urrc-bindings.json` `D-24` | `canonical_owner` is `01-WORKING/ONTOLOGY-REGISTER.md` | **AUTHORITY** | **UPHELD as the single canonical owner.** It is the only claim expressed as a machine-readable binding, and it is the claim every conformant projection already defers to. |
| `UMN-001-…md:245` (Deliverable 3) | Root ontology is `OWNED` by MIP-v2 | **SUPERSEDED** | **NOT UPHELD.** See §3. |

**DETERMINED:** the root ontology has exactly one canonical owner —
`01-WORKING/ONTOLOGY-REGISTER.md` — sourced from `SRC-02` and adjudicated by
`UCOS-RAT-001`. Every other site that states the root ontology is a **projection** and
must reduce to it.

`UCPA-L-06` makes this non-restatable: it requires exactly one projection to hold role
`AUTHORITY`, and requires that projection's path to equal the `canonical_owner` the
binding file itself records under `D-24`, read at measurement time. If the binding ever
changes, the gate follows it or closes. This determination therefore creates no second
record of who the owner is.

---

## 3. Determination 2 — Contradiction (disposition of SC-A-02)

### 3.1 The contradiction

`UCOS-OMEGA-INFINITY-MASTER-IMPLEMENTATION-PLAN-V2.md` §ROOT ONTOLOGY renders the chain
with BEING **as a layer**, and then states:

> "Every registered entity is anchored to **exactly one point on this ontology** and
> inherits the obligations of every level above it"

Under that sentence BEING is an anchorable point. `RAT-01` ratified that it is not.
`UMN-001-…md:501` repeats the same form.

The contradiction is material, not cosmetic: it decides whether an object may declare
BEING as its ontology anchor.

### 3.2 The resolution, and why it required no architectural decision

MIP-v2 supplies the governing rule in its own preamble:

> "Where any rule herein conflicts with a higher frozen constitutional instrument, the
> higher instrument governs and this rule is **void to the extent of the conflict**."

`UCOS-RAT-001` is the constituent act of the UCOS Ω∞ Constituent Authority (`AUTH-13`) via
Terminal T4, enacted at Phase 10. MIP-v2 carries `BASELINE DATE 2026-07-17`, which
**precedes** it.

**DETERMINED:** MIP-v2's §ROOT ONTOLOGY is **void to the extent that it renders BEING as an
anchorable layer**, by MIP-v2's own terms. The remainder of §ROOT ONTOLOGY — the ordering
`EXISTENCE → RELATIONSHIP → TRANSFORMATION` and the inheritance rule "to transform, a thing
must relate; to relate, it must exist; to exist, it must be" — is **conformant and
retained**.

### 3.3 `UMN-001` is drift, not supersession

The artifact determined here is
`UMN-001-UNIVERSAL-MICRO-NUCLEUS-CONSTITUTIONAL-DETERMINATION.md`.

It carries `Determination date: 2026-08-06`, which **postdates** the ratification.
It restates both the superseded chain and the superseded owner. It is therefore not an
older instrument overtaken by a newer one; it is a later instrument that did not carry the
ratification forward.

**DETERMINED:** `UMN-001` Deliverable 3's row *"Root ontology (BEING→TRANSFORMATION) |
MIP-v2 | … | OWNED"* and its line-501 hierarchy diagram are **SUPERSEDED** by this
determination as to the owner and as to BEING's standing. Every other conclusion in
`UMN-001` — its REUSE/EXTEND findings, its micro-nucleus profile set, its other 15
owner-matrix rows — is untouched and stands.

### 3.4 Neither artifact is edited

Supersession is the forward channel (`CEP-007 XIII`;
`engine/foundation/guards/frozen_paths.py` states the same doctrine: "Identity is
immutable, history is append-only, and evolution is unlimited through those channels; only
in-place modification of a certified artifact is refused"). Rewriting `MIP-v2` or `UMN-001`
to say something they did not say would falsify the record rather than advance it. Both are
**classified**, in data, at
`00-MASTER/UCPA-000001/ucpa-declaration.json` → `projections[UCPA-PROJ-07, UCPA-PROJ-08]`,
role `SUPERSEDED`, `superseded_by` this file.

`UCPA-L-05` measures that this determination genuinely names each artifact it claims to
supersede — a supersession that does not name its subject is not a supersession.

---

## 4. Determination 3 — The canonical mapping (disposition of SC-A-03)

Scope A requires the primitives to be validated **against** the UCKP model and the 33-facet
model. Before this determination no artifact related the two: `engine/uckp/facets.py`
declared 33 universal questions and `ONT-01…ONT-04` declared four primitives, with nothing
connecting them.

### 4.1 The reduction rule

Stated once and applied uniformly, so that the mapping is auditable rather than asserted:

> A facet reduces to the primitive whose obligation it discharges — **EXISTENCE** if its
> question is answerable from the object alone; **RELATIONSHIP** if answering it requires
> naming a second entity; **TRANSFORMATION** if answering it requires a sequence of states.

This rule is the register's own inheritance chain read backwards: *to transform, a thing
must relate; to relate, it must exist.*

### 4.2 The mapping

Total, single-valued, and carried as data at `ucpa-declaration.json` → `facet_reduction`.
Each of the 33 rows cites the facet's own declared question from `engine/uckp/facets.py`
as its basis.

| Primitive | Facets | Count |
|---|---|---|
| `ONT-02` **EXISTENCE** | identity · semantic-identity · ontology · validation · context · metadata · constraints · persistence-bindings · existence-context | 9 |
| `ONT-03` **RELATIONSHIP** | taxonomy · authority · ownership · dependencies · relationships · certification · verification · traceability · evidence · discovery · security-context · governance-context · compliance-context · knowledge-context · observer-context | 15 |
| `ONT-04` **TRANSFORMATION** | provenance · lifecycle · temporal-history · evolution-history · replay · audit · policies · runtime-bindings · projection-bindings | 9 |
| `ONT-01` **BEING** | — none, and none is permitted | 0 |
| | **Total** | **33** |

### 4.3 Why BEING takes none

`RAT-01` is executable here. BEING is the ground of the order, not an addressable node, so
no facet may anchor to it. `UCPA-L-04` refuses any reduction that targets a primitive whose
standing is `AXIOM`. This is the precise point on which MIP-v2 was found void (§3.2), now
enforced rather than argued.

### 4.4 The mapping cannot drift

`UCPA-L-03` imports `engine.uckp.facets.Facet` and measures coverage in **both**
directions. A thirty-fourth facet admitted without a reduction closes the gate. That is
correct behaviour, not friction: `facets.py` states that a thirty-fourth facet "is a
constitutional amendment — a new question every object in the universe must suddenly
answer", and an amendment must not pass unnoticed.

---

## 5. Determination 4 — The primitives remain open

The set is **not** closed by this determination. `CMG-000001` XIV.7 holds the ontology open
to new entity types under Article LXXVI, and LXXVI.5 makes expansion "unbounded in count…
any apparent limit SHALL be read as a **defect**".

`UCPA-L-07` measures this rather than promising it: a synthetic primitive is admitted into
a copy of the binding, and the law requires the copy to remain usable with every existing
primitive unchanged — admission is an **append**, and an append that reclassifies a sibling
is not an append. A binding that refused a future member would close the gate as a closed
enumeration. The probe is never persisted.

This mirrors `UCKP-INV-14` (`engine/uckp/vocabulary.py` `is_extensible()`), which applies
the same discipline to the vocabularies.

---

## 6. Determination 5 — Self-application

A programme that measures reduction must itself reduce, or it claims an exemption from the
law it enforces. `UCPA-000001` reduces to `ONT-03` **RELATIONSHIP**: its question — *does
this artifact reduce to a declared primitive?* — cannot be answered without naming a second
entity. `UCPA-L-08` measures that the primitive named is one the declaration binds, that it
is not the axiom, and that the law named as its measure is a law that exists.

---

## 7. What is now enforced

| Law | What it makes impossible |
|---|---|
| `UCPA-L-01` | Naming a primitive the canonical register does not carry |
| `UCPA-L-02` | Giving a primitive a standing the ratification record does not give it |
| `UCPA-L-03` | A facet with no reduction, a reduction with no facet, or a double reduction |
| `UCPA-L-04` | Anchoring anything to BEING |
| `UCPA-L-05` | A classification pointing at a file nobody can open, or a supersession that never names its subject |
| `UCPA-L-06` | A second ontology authority, or an authority that disagrees with the owner binding |
| `UCPA-L-07` | Closing the primitive set |
| `UCPA-L-08` | This programme exempting itself |

Measured by `engine.root_ontology.gate` as a declared stage of `./verify.sh`, classified in
`00-MASTER/UVI-000001/uvi-declaration.json`.

---

## 8. Scope A acceptance

| Criterion | Before | After | Evidence |
|---|---|---|---|
| ✓ Canonical mapping exists | **UNMET** — no artifact related facets to primitives | **MET** | `ucpa-declaration.json` → `facet_reduction`, 33 rows, measured by `UCPA-L-03` |
| ✓ Ownership defined | **UNMET** — defined twice, differently | **MET** | §2; measured by `UCPA-L-06` against `URRC D-24` |
| ✓ No contradiction remains | **UNMET** — two sites carried the superseded form | **MET** | §3; classified in data, measured by `UCPA-L-05` |
| ✓ Validation exists | **UNMET** — `ONT-02/03/04` in no `.py`, no `.json` | **MET** | `engine/root_ontology/`, 8 laws, gated in `./verify.sh` |

---

## 9. Boundary

This determination certifies that eight declared laws were measured against the declared
surfaces at the declared paths. It certifies **no** ontology, **no** primitive, **no**
baseline, and **no** artifact other than this programme's own declaration. It does not
close Phase 1: Scopes B, C and D remain open.

---

*End of UCPA-001-CONSTITUTIONAL-PRIMITIVE-ALIGNMENT-DETERMINATION.md*
