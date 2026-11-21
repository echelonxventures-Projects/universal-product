# UCRD-001 — Constitutional Relationship Determination

**Checkpoint:** `00bd45f` (integration/recovery-001)
**Determination date:** 2026-08-06
**Predecessors:** `UCOD-001` (ownership), `UCOS-MOD-001` (meta-ontology), `CEP-MOD-002` (vocabulary migration)
**Authority:** Repository Truth only.
**Posture:** Determination of the constitutional model. No implementation, no redesign, no CEP drafted. **Zero files modified.**

---

## Preamble — the determination, stated first

The mission offers two candidate abstractions: **independent ownership dimensions**, or **constitutional relationships**.

> **Repository Truth legislates neither. It legislates a third model that already contains both — and both candidates are subordinate members of it.**

The model is the **Universal Facet Model** (`UCKP-ART-06`, implemented at `engine/uckp/facets.py`): **thirty-three mandatory questions** every constitutional object must be able to answer.

- **Ownership is Facet 7** — *"Who is accountable for it?"*
- **Relationships is Facet 9** — *"How is it bound to everything else?"*

Ownership is **not** the correct abstraction. That much the mission anticipated. But promoting *relationship* in its place would repeat the identical category error in the other direction, because `relationships` is one facet of thirty-three, exactly as `ownership` is. **The recommendation to replace `CEP-OWN-001` with `CEP-REL-001` is therefore declined on Repository Truth evidence**, and §7 states what should happen instead.

---

## 1. The three-tier model Repository Truth actually legislates

`engine/uckp/facets.py:8-13` states the tiering explicitly, and it is the single most load-bearing passage in this determination:

> *"The enumeration is **closed on purpose** while the **vocabularies inside** facets are **open**. Adding a thirty-fourth facet is a **constitutional amendment** — a new question every object in the universe must suddenly answer — and amendments belong in the law, not in a data file. Adding a new knowledge kind, authority tier, persistence technology or **relationship class** is **registration**, and registration must never require an amendment."*

| Tier | What it is | Cardinality | How it grows | Authority |
|---|---|---|---|---|
| **1 · Facet** | The **question** every object must answer | **33 — CLOSED** | Constitutional **amendment** | `UCKP-ART-06`; `facets.py:23-58` |
| **2 · Relationship class** | The **register** a binding belongs to | **12 — OPEN** | **Registration** | `RELATIONSHIP_CLASS_VOCABULARY`, `vocabulary.py:304-323` |
| **3 · Relation type** | **How** one object is bound to another | **17 — OPEN** | **Registration** | `RELATION_TYPE_VOCABULARY`, `vocabulary.py:280-302` |

This is not an inferred hierarchy. It is declared, and the closed/open asymmetry is deliberate: the *questions* are fixed so that no object can escape one; the *answers* are open so that no future answer requires amending the law. That is `UCKP-ART-17` (*"admitted by registration, never by amendment"*) and `UCKP-ART-06` (*"a facet may be unattested, but it may never be absent"*) working as a pair.

---

## 2. The fifteen concerns, measured against all four declared vocabularies

Executed at `00bd45f` against `engine/uckp/facets.py`, `RELATIONSHIP_CLASS_VOCABULARY`, `RELATION_TYPE_VOCABULARY`, and `ROOT_LAW.GOVERNED_CATEGORIES`.

| Concern | Facet (closed, 33) | Rel-class (open, 12) | Relation type (open, 17) | Governed category |
|---|---|---|---|---|
| **Ownership** | `ownership` | `ownership` | `owns` | — |
| **Authority** | `authority` | `authority` | — | ✔ |
| **Responsibility** | `ownership` | `ownership` | `owns` | ✔ |
| **Execution** | `runtime-bindings` | `runtime` | — | — |
| **Generation** | `projection-bindings` | — | `generated-from` | — |
| **Composition** | `dependencies` | — | `depends-on` | ✔ *(as `dependency`)* |
| **Validation** | `validation` | `validation` | `validates` | ✔ |
| **Verification** | `verification` | — | — | ✔ |
| **Certification** | `certification` | — | `certifies` | ✔ |
| **Governance** | `governance-context` | `governance` | `governs` | ✔ |
| **Configuration** | `context` | — | — | — |
| **Evolution** | `evolution-history` | `evolution` | — | — |
| **Commercialization** | **— NONE —** | **—** | **—** | **—** |
| **Security** | `security-context` | — | — | — |
| **Lifecycle** | `lifecycle` | — | — | — |

### 2.1 What the measurement shows

**Fourteen of fifteen concerns already have a legislated constitutional home** — as a facet. Not one of them is an "ownership dimension." Not one of them required inventing anything.

**One concern — Commercialization — has no home anywhere:** no facet, no relationship class, no relation type, no governed category. `UCOD-001` §1.5 independently measured *"Commercialization Owner: **0** occurrences"* repository-wide. This is the only genuine gap among the fifteen, and §6 determines its disposition.

**`Responsibility` is not distinct from `Ownership`.** Facet 7's declared question is *"**Who is accountable for it?**"* (`facets.py:97`) — accountability *is* responsibility. Correspondingly, relation type `owns` is defined as *"**is accountable for**"* (`vocabulary.py:296`). Two names, one legislated concept. Modelling them as two independent dimensions would create the duplicate authority `UCKP-ART-03` forbids.

---

## 3. Why "independent ownership dimensions" is constitutionally unavailable

### 3.1 The structural proof

`engine/uckp/ucko.py:107-136` shows every facet's carrier type. The distinction between them is the whole answer:

| Facet | Carrier on the UCKO | Cardinality |
|---|---|---|
| `ownership` | `ownership: Ownership` | **Exactly one** — `Ownership` holds one `owner` + stewards (`values.py:215-225`) |
| `authority` | `authority: AuthorityBinding` | Exactly one |
| `lifecycle` | `lifecycle: str` | Exactly one |
| `certification` / `validation` / `verification` | `Attestation` | One attestation each |
| **`relationships`** | **`relationships: tuple[Relationship, ...]`** | **Many** |
| `runtime_bindings` / `projection_bindings` | `tuple[...]` | Many |
| `security_context` / `governance_context` | `ContextBinding` | One each |

**Ownership is singular by construction.** `Ownership` carries one `owner` field. This is why `OWN-REQ-002` reads *"at most one canonical owner per subject"* — it is a **structural fact of the value type**, not a policy choice that a proposal could relax.

`UCOD-001` §1.4 measured the consequence precisely: a second ownership dimension *"can only be expressed today by mangling the subject key (`CONCEPT::runtime`), which Repository Truth nowhere legislates and which would silently defeat `OWN-REQ-002`'s contest detection."*

### 3.2 The determination

> **Ownership cannot carry fifteen dimensions because ownership is a singular-valued facet. Fifteen ownership dimensions would require fifteen owners per subject, which `OWN-REQ-002` forbids structurally and `UCKP-ART-03` forbids constitutionally.**

The abstraction fails not because it is undesirable but because **the value type cannot hold it**. `UCOD-001` reached the same conclusion from the ownership side and recorded eleven of its twenty requested dimensions as `NOT LEGISLATED` rather than fabricate them.

### 3.3 What the "missing" ownership dimensions actually are

`UCOD-001` recorded these as unlegislated ownership dimensions. Measured against the facet model, every one resolves — as a **different facet or relation**, never as a second owner:

| Claimed "ownership dimension" | Its actual constitutional home |
|---|---|
| Generator Owner | Facet `projection-bindings` + relation `generated-from` |
| Runtime Owner | Facet `runtime-bindings` + rel-class `runtime` |
| Validation Owner | Facet `validation` + rel-class `validation` + relation `validates` |
| Certification Owner | Facet `certification` + relation `certifies` |
| Governance Owner | Facet `governance-context` + rel-class `governance` + relation `governs` |
| Evolution Owner | Facet `evolution-history` + rel-class `evolution` |
| Security Owner | Facet `security-context` |
| Lifecycle Owner | Facet `lifecycle` |
| Policy Owner | Facet `policies` |
| Registry Owner | Facet `discovery` + rel-class `knowledge` |

**The gap `UCOD-001` identified dissolves under the correct model.** Nineteen additional owners were never needed. The questions were always answerable — by reading the facet that already carries the answer. `CEP-005`'s formulation was right all along: *"issued by the **located** certification owner"* — located, not separately owned.

---

## 4. Why "constitutional relationships" is also not the top-level model

The mission's second candidate is closer to correct but still misplaces the abstraction.

| Test | Finding |
|---|---|
| Is `relationships` the top-level concept? | **No.** It is Facet 9 of 33 (`facets.py:34`), peer to `ownership` at Facet 7 |
| Can every concern be expressed as a relationship? | **No.** `lifecycle` is a *stage* (a `str` from `LIFECYCLE_STAGE_VOCABULARY`), not a binding to another object. `security-context` is a `ContextBinding`. `validation` is an `Attestation`. Forcing these into `Relationship(relation, target, class)` would require inventing a target that does not exist |
| Would promoting it be lawful? | **No.** `CMG-000001` LXXVI.6 — *"Expansion SHALL NOT be achieved by **reinterpretation** of an existing member to mean something new. Reinterpretation is invisible to validation"* |

**Determination:** relationships model the *bindings between* objects. They do not model *properties of* an object (its lifecycle stage, its security context, its attestations). A model that recognised only relationships would lose the eight facets that are intrinsic rather than relational.

**Both candidate abstractions are members of the same set. Neither is the set.**

---

## 5. Final Constitutional Determination

> ### The constitutional model is the Universal Facet Model, and it is already legislated, already implemented, and already sole.
>
> **Thirty-three mandatory facets** (`UCKP-ART-06`; `engine/uckp/facets.py`), closed by amendment, carrying **open vocabularies** inside (`UCKP-ART-17`; `engine/uckp/vocabulary.py`).
>
> **Ownership is one facet of thirty-three.** It is singular-valued by construction and cannot bear dimensional expansion.
>
> **Relationship is one facet of thirty-three.** It is multi-valued and classified by an open twelve-member register, of which `ownership` is itself one member.
>
> **Fourteen of the fifteen named concerns are already facets. None is an ownership dimension. One — Commercialization — has no constitutional home at all.**

### 5.1 Disposition matrix

| # | Question | Disposition | Authority |
|---|---|---|---|
| 1 | Model the 15 as independent ownership dimensions | **REJECTED** | `OWN-REQ-002`; `Ownership` holds one owner; `UCKP-ART-03` |
| 2 | Model the 15 as constitutional relationships | **REJECTED as the top-level model** | `relationships` is Facet 9 of 33; 8 facets are non-relational; `CMG` LXXVI.6 |
| 3 | The correct model | **PASS — already legislated** | `UCKP-ART-06`; `facets.py` |
| 4 | Ownership's true place | **PASS** — Facet 7, and rel-class 1 of 12 | `facets.py:32,97`; `vocabulary.py:304-323` |
| 5 | 14 of 15 concerns | **PASS / REUSE** — each has a located facet | §2 |
| 6 | Commercialization | **CEP** — the only genuine gap | §6 |
| 7 | `CEP-OWN-001` | **WITHDRAW** — premised on a model Repository Truth does not hold | §7 |
| 8 | `CEP-REL-001` | **DO NOT CREATE** | §7 |
| 9 | Any new facet | **AMENDMENT — not registration** | `facets.py:9-11` |
| 10 | Any new relationship class or relation type | **REGISTRATION — never amendment** | `UCKP-ART-17`; `facets.py:11-13` |

**CREATE count: 0.** Every concept examined except Commercialization has a located owner.

---

## 6. The single genuine gap — Commercialization

The only one of the fifteen with no constitutional home: no facet, no relationship class, no relation type, no governed category, and (per `UCOD-001` §1.5) zero repository occurrences.

**Its correct disposition is registration, not amendment.** `facets.py:9-13` is explicit: adding a 34th facet is *"a constitutional amendment — a new question every object in the universe must suddenly answer."* Commercialization is not a question every constitutional object must answer; most objects have no commercial aspect at all. Making it a facet would force all 542 concepts to answer it.

**Recommended shape (not drafted, per mission constraint):** register a **relationship class** in the open twelve-member register — the same mechanism by which `runtime`, `governance`, and `evolution` are already carried. Cost: one `VocabularyRegistry.extend` call. Measured in `CEP-MOD-002` §Output 9: registration does not move the universe fingerprint, so it is replay-neutral.

This is the facet model working exactly as designed — the closed set stays closed, and the new concern enters through the open register.

---

## 7. Determination on `CEP-OWN-001` → `CEP-REL-001`

The mission instructs: *"If ownership is only one relationship, recommend replacing `CEP-OWN-001` with `CEP-REL-001`."*

**The antecedent is confirmed. The consequent is declined.**

**Ownership is only one relationship** — measurably. It is one of twelve relationship classes (`vocabulary.py:309`, *"ownership: who is accountable"*), and `owns` is one of seventeen relation types. The mission's premise holds.

**But `CEP-REL-001` should not be created, for three Repository Truth reasons:**

1. **It would create a model that already exists.** `UCKP-ART-18` — *"Before anything is created its canonical object shall be located. If it exists it is reused, extended or referenced. It is never duplicated and never given a rival."* The relationship model is fully implemented: `Relationship` (`values.py:237-265`), `RELATIONSHIP_CLASS_VOCABULARY`, `RELATION_TYPE_VOCABULARY`, `UniversalKnowledgeGraph`, `UCKP-ART-07`. A CEP creating it would be a rival to a located owner.
2. **It would promote a facet to the top level** — the same category error as ownership, mirrored. §4.
3. **`CEP-OWN-001` was never drafted.** Repository-wide grep returns exactly one occurrence: the recommendation inside `UCOD-001` itself. Nothing exists to replace.

### Recommended disposition

| Action | Disposition | Reason |
|---|---|---|
| `CEP-OWN-001` | **WITHDRAW the recommendation** | Premised on ownership-dimension expansion, which §3 proves structurally unavailable. Its underlying gap dissolves under the facet model (§3.3) |
| `CEP-REL-001` | **DO NOT CREATE** | `UCKP-ART-18`; the model exists and is implemented |
| A facet-model CEP | **NOT REQUIRED** | `UCKP-ART-06` already legislates it; `facets.py` already implements it; the construction-time guard at `facets.py:126-127` already enforces completeness |
| Commercialization | **CEP — registration of one relationship class** | §6. The only admissible new proposal arising from this determination |

**The determination is that the constitutional model needed no proposal. It needed to be located.**

---

## 8. What this determination changes about the three predecessors

| Predecessor | Finding | Status after this determination |
|---|---|---|
| `UCOD-001` | Ownership is 27.86% closed (151/542); 11 of 20 dimensions `NOT LEGISLATED` | **Confirmed and reframed.** The 391 unowned concepts remain unowned — that measurement stands. But the 11 "unlegislated dimensions" were never ownership dimensions; they are facets that already exist (§3.3). The ownership gap is real; the *dimensional* gap was a modelling artifact |
| `UCOD-001` §1.4 verdict *"EXTEND for ownership role dimensions"* | Recommended `CEP-OWN-001` | **Superseded.** No extension of ownership is required or possible; the roles are read from their own facets |
| `UCOS-MOD-001` §3.2 | Listed facet, relationship, identity, authority as permanent primitives | **Confirmed and sharpened.** The tiering (closed facets / open vocabularies) is now stated explicitly with its authority |
| `CEP-MOD-002` | Migration of six closed vocabularies | **Unaffected.** Those are Tier-2/3 vocabularies; this determination governs Tier 1 and does not alter the migration |

---

**Files modified: none. Code changed: none. CEP drafted: none. Model redesigned: none.**

Repository Truth artifacts cited: 11. Source files inspected: 6. Live measurements executed: 2 (15-concern × 4-vocabulary mapping; UCKO facet-carrier cardinality).

Recorded at commit `00bd45f`. Nothing herein is enacted.

---

*End of UCRD-001-CONSTITUTIONAL-RELATIONSHIP-DETERMINATION.md*
