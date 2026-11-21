# STRUCTURAL PATTERN GOVERNANCE CONSOLIDATION DETERMINATION

| Field | Value |
|---|---|
| ARTIFACT | `STRUCTURAL-PATTERN-GOVERNANCE-CONSOLIDATION-DETERMINATION.md` |
| CLASSIFICATION | `EVIDENCE` |
| AUTHORITY | **NONE — DERIVED TRUTH.** Reclassifies nothing, supersedes nothing, edits no law, widens no enumeration. Reclassification is a visible admission act reserved to an owner. |
| DISPOSITION | **DETERMINATION ONLY.** No law edited. No supersession enacted. |
| SUBJECT | Classification of Nucleus · Micro-Nucleus · Universe · Layer · Domain · Capability · Entity · Object · Component into (A) universal primitive, (B) structural pattern, (C) contextual projection, (D) implementation representation |
| BASELINE | HEAD `03179308f5cb` · branch `integration/recovery-001` · working tree unchanged |
| MODE | Read-only measurement. No registry mutation. No identity minting. No certification claim. |
| SUPERSEDES | Nothing. **Updates** `STRUCTURAL-PATTERN-GOVERNANCE-ANALYSIS.md` (earlier this session; originally authored as `UNIVERSAL-STRUCTURAL-PATTERN-GOVERNANCE-DETERMINATION.md` and renamed by the identity-correction directive recorded in `IDENTITY-CORRECTION-EXECUTION-REPORT.md`) by extending its 10-term table to the 9 terms this directive names, adding Capability, Entity, Object and Component, and adding one new confirmed violation. |
| GOVERNING INSTRUMENTS | `UCPA-001` §1 (RAT-01/02/03), §5 (primitives remain open) · `UCOS-MOD-001` §3.2/§4 · `CMG-000001` XIV.7, LXXVI.5, LXXVI.6 · `CEP-007 XIII` (supersession is the forward channel) · `UCPA-L-05` |
| REFUSES | Reclassifying by reinterpretation. Editing `engine/nucleus/law.py` or `engine/civilization/generation.py`. Admitting a term that has no definition. |

> **Headline.** **None of the nine terms is a universal primitive.** The ratified primitive set is exactly four — `BEING` as an axiom plus `EXISTENCE`, `RELATIONSHIP`, `TRANSFORMATION` — and `UCOS-MOD-001` already determined the structural vocabulary is *"not"* a member of the Permanent Constitutional Ontology, because *"the permanence is in the shape, never in the noun."* Five of the nine are already data rows. **Three of the nine — Object, Component and Module-class terms — have no definition in the CEU plane at all.** And this pass confirms a second hardcoded hierarchy the previous determination did not reach: `engine/civilization/generation.py` fixes a stratum chain in executing code with literal parents, `NucleusStratum → UniverseStratum → CapabilityStratum`, which is the plainest instance of *"all future structures must fit existing layers"* in the repository.

---

## 1. Evidence

| Question | Command / file | Result |
|---|---|---|
| What are the ratified primitives? | `UCPA-001` §1 | `RAT-01` BEING = axiom-only, non-layer · `RAT-02` 4-primitive form `EXISTENCE → RELATIONSHIP → TRANSFORMATION` · `RAT-03` SPACE-TIME is a coordinate, not a root |
| Are primitives closed? | `UCPA-001` §5 | *"**Determination 4 — The primitives remain open.** The set is not closed by this determination"* · `CMG-000001` LXXVI.5: expansion *"unbounded in count… any apparent limit SHALL be read as a **defect**"* |
| Is the structural vocabulary permanent? | `UCOS-MOD-001:112` | *"`Universe`, `Domain`, `Capability`, `Component` are **not** members of it"* · `:110` *"The permanence is in the shape, never in the noun."* · `:39` E-01 *"**No such clause exists.**"* |
| CEU classifications | `engine/ceu/catalog.py:198-212` | 10 rows: `nucleus`, `micro-nucleus`, `nano-nucleus`, `layer`, `composition`, `service`, `engine`, `platform`, `domain`, `agent` |
| CEU forms | `engine/ceu/catalog.py` `SEED_FORMS` | includes `entity`, `capability`, `universe`, `reality`, `civilization`, `knowledge`, `governance`, `evidence`, … |
| CEU topologies | `engine/ceu/catalog.py:119-137` | 17 rows incl. `layered` (*"never mandatory"*), `layerless` (*"the explicit absence of strata, so 'no layers' is declarable"*), `network`, `graph`, `mesh`, `fractal`, `swarm` |
| Is `component` in CEU? | `grep -c 'component' engine/ceu/catalog.py` | **0** |
| Is `object` in CEU? | `grep -c '"object"' engine/ceu/catalog.py` | **0** |
| Is nucleus still mandatory? | `engine/nucleus/law.py:41-46` | `SUPREMACY_CLAUSE` — *"Capabilities are owned by Nuclei and by nothing else… or the repository is in violation."* |
| Measured how? | `engine/nucleus/law.py:238-260` | *"The invariants the authority must measure. Zero-tolerance by construction."* `NUC-INV-01..09` |
| Is the role enum closed? | `engine/nucleus/law.py:69,71,73` | exactly three — `NUCLEUS`, `LAYER`, `COMPOSITION` |
| Is it self-declared a projection? | `engine/nucleus/law.py:49-52` | *"A **projection** of the CEU classifications… no longer an authority… Legacy values derive from CEU; never the reverse."* |
| **NEW:** fixed stratum chain? | `engine/civilization/generation.py:80-100` | Literal tuple with literal parents: `BlueprintStratum → OperatingSystemStratum → NucleusStratum → UniverseStratum → CapabilityStratum → …` |
| Do `CEU-002`/`CEU-005` have text? | `grep -rl` over `*.md` → 0, `*.json` → 0, `*.py` → 2 | **No located constitutional text.** Python comments and one test docstring only. |
| Capability namespaces | `grep` over `00-MASTER/`, `intelligence/` | **9** parallel `*-CAP-*` namespaces; 131-entry catalog |
| Openness template | `engine/context/taxonomy.py:59-62` | *"That the list moved from fifteen to sixteen is itself the evidence the taxonomy is open"* |

---

## 2. Classification of the nine terms

Universal primitive status is settled and exclusive: **A = `{BEING(axiom), EXISTENCE, RELATIONSHIP, TRANSFORMATION}` only.** No term below qualifies.

| Term | Current representation | Class | Basis | Currently enforced as a container? |
|---|---|---|---|---|
| **Nucleus** | CEU classification row holding faculty `own-capability` | **B** structural pattern | `catalog.py:199` — a row, *"privileged by nothing except what this data says"* | **YES — and this is the primary defect.** `SUPREMACY_CLAUSE` + `NUC-INV-01/02` |
| **Micro-Nucleus** | CEU classification, `specializes: nucleus` | **B** structural pattern | `catalog.py:200` | Partly — `UMN-001` prose binds it to `Capability(CAP-NNNN)` |
| **Universe** | CEU **form** row (an existence form) | **C** contextual projection | `SEED_FORMS`; `UCOS-MOD-001:204` calls it *"current canonical Repository Truth vocabulary"* | Partly — `UNAF-001` §1.4 fixes it as a governed composition of Nuclei; `UniverseStratum` fixes it in code |
| **Layer** | CEU classification + topologies `layered`/`layerless` | **C** contextual projection | `catalog.py:202` *"Owns nothing, and is optional"*; `:121` *"never mandatory"* | **NO — already fully declassified.** Strongest precedent in the repository. |
| **Domain** | CEU classification row, no faculties | **B** structural pattern | `catalog.py:211` | No clause found; `UMN-001` chain positions it |
| **Capability** | CEU **form** row · 9 parallel `*-CAP-*` namespaces · 131-entry catalog · `KnowledgeCapability` (11, closed, `ISD-CE-09`/`ISD-G-01`) · `CapabilityStratum` | **C** projection in the CEU plane, **D** implementation representation in practice | `SEED_FORMS` vs the nine namespaces | Partly — `FG-18` asserts single-nucleus ownership over a population never proven to equal the capability population |
| **Entity** | CEU **form** row | **C** contextual projection | `SEED_FORMS`; `engine/ceu/existence.py:4-8` records that *"the repository had an entity model with a fixed root"* — now demoted | **NO — already declassified** |
| **Object** | **absent from CEU** (0 hits). Exists as `UCKO` / `CanonicalKnowledgeObject` | **D** implementation representation | `UCOS-UCOM-001` names the UCKO the universal object model; no CEU row | No, but it is the universal carrier, so its *schema* constrains everything |
| **Component** | **absent from CEU** (0 hits). Appears only in the MIP chain and as `ComponentStratum` | **not classifiable — undefined** | `grep -c 'component' engine/ceu/catalog.py` = 0 | Yes, implicitly, via the fixed stratum chain |

**Aggregate:** 0 primitives · 3 structural patterns (B) · 4 contextual projections (C) · 1 implementation representation (D) · 1 undefined. Two terms (Layer, Entity) are already fully compliant with the directive's target classification and require no act.

---

## 3. Conflicts

| ID | Conflict | Grade |
|---|---|---|
| **SC-C-01** | **Live contradiction between two executing surfaces.** `catalog.py:202` declares `layer` ownerless and optional; `nucleus/law.py:42-46` declares nucleus the sole owner *"or the repository is in violation"*, measured at zero tolerance. Both execute; nothing reconciles them. | **CONFIRMED** |
| **SC-C-02** | **The completed demotion cites unlocatable law.** `CEU-002`/`CEU-005` have zero occurrences outside Python comments and one test docstring. | **CONFIRMED** |
| **SC-C-03** | **NEW — a second fixed hierarchy, in executing code.** `engine/civilization/generation.py:80-100` hardcodes a stratum chain, each entry naming its parent as a string literal: `NucleusStratum` parent `OperatingSystemStratum`, `UniverseStratum` parent `NucleusStratum`, `CapabilityStratum` parent `UniverseStratum`. This is a fixed hierarchy *and* a fixed ontology in one construct, and it is the literal form of the directive's invalid example *"all future structures must fit existing layers."* Not reached by the prior determination; it is not among `CEP-MOD-002`'s six sites either. | **CONFIRMED** |
| **SC-C-04** | **`StructuralRole` closed at three, self-declared as a limitation.** A fourth CEU classification is registrable and discoverable via `registered_roles` but *cannot be carried by a legacy `SubjectRecord`* — representable in the registry, unrepresentable on the record. | **CONFIRMED** |
| **SC-C-05** | **Capability has no single owner.** Nine parallel namespaces, a 131-entry catalog, and a CEU form row, with no register spanning them; `FG-18`'s invariant is measured over the nucleus registry, not over the capability population. | **CONFIRMED** |
| **SC-C-06** | **Object is the universal carrier yet has no CEU row.** The UCKO/CKO schema constrains every governed object, but `object` is not a declared form, so the carrier is outside the plane that declares what things are. | **CONFIRMED** |
| **SC-C-07** | **Component is undefined but structurally load-bearing.** Absent from CEU, present in the MIP decomposition chain and as `ComponentStratum`. It cannot be reclassified — reclassification presumes a definition. | **CONFIRMED** |
| **SC-C-08** | `KnowledgeCapability` (11) is closed with `intentional: false`, `closing_invariant: "NONE DECLARED IN CODE"`, gap `ISD-G-01`. | **CONFIRMED** |

---

## 4. Decision options

| Option | Description | Assessment |
|---|---|---|
| **A — Converge the projection to the source, per term, by named supersession** *(recommended)* | For each term, record its class in data; supersede only the specific clauses that bind it as mandatory; generalize the owning *role* while preserving ownership *integrity*. | Uses the established channel. `UCPA-001` §3.3 is the precision precedent — it superseded one row and one diagram and left everything else standing. |
| **B — Blanket declaration that all terms are patterns** | One statement reclassifying all nine. | **Rejected.** `UCPA-L-05`: *"a supersession that does not name its subject is not a supersession."* Unmeasurable, therefore void. Also cannot cover the three undefined terms. |
| **C — Abolish nucleus ownership** | Remove `SUPREMACY_CLAUSE` and `NUC-INV-01/02`. | **Rejected.** `NUC-INV-03`/`NUC-INV-04` (unowned = 0, multi-owned = 0) are genuine integrity invariants independent of what the owner is called. Removing exclusivity must not remove integrity. |
| **D — Reinterpret existing text as already meaning "pattern"** | Read the clauses charitably. | **Rejected.** `CMG-000001` LXXVI.6: *"Reinterpretation is invisible to validation; admission is visible."* |
| **E — Defer pending `CEP-MOD-002` M-0** | Wait for `verify_vocabulary_alignment`. | Partially unavoidable for the vocabulary-contribution mechanism, but SC-C-02 and SC-C-03 are independent of it and should not wait. |

**Recommended direction: A**, in this order, because the ordering is forced by dependency:

1. **Locate or correct `CEU-002`/`CEU-005`** (SC-C-02). Everything else converges *toward* CEU; converging toward an unlocatable citation compounds the defect rather than resolving it.
2. **Define or omit Object and Component** (SC-C-06, SC-C-07). A term cannot be reclassified into a taxonomy it does not appear in. Admission, not reclassification.
3. **Register the capability namespaces** (SC-C-05). Until the capability population is known, no ownership statement about capabilities is evidenced.
4. **Generalize the owning role, preserve ownership integrity** (SC-C-01, SC-C-04). The inversion is already half-built: `engine/nucleus/authority.py` states *"Remove `own-capability` from the `nucleus` classification and `may_own_capability` becomes `False` here, with no edit to this file."* The residue is the closed three-member enum and clause text naming nucleus specifically.
5. **Replace the literal stratum chain with declared data** (SC-C-03). The executed template is `engine/context/taxonomy.py`, whose precondition is explicit: *"no control flow in this layer branches on a specific kind."*

### 4.1 The mandatory rule, expressed as a measurable predicate

The directive's rule — *no current concept can become an infinite architectural limitation* — is only enforceable if stated as something a check can falsify. Proposed form, in the house idiom:

> For every structural term T, a synthetic sibling of T can be admitted into a copy of its declaring population, and the admission changes no control flow, no serialization, and no invariant outcome.

That is `ISD-L-06`/`ISD-L-11` applied to structural vocabulary. It converts the valid/invalid examples the directive gives into a per-term measurement:

- *"Everything must be a Nucleus"* → falsified by admitting a fourth classification holding `own-capability` and observing a capability owned under it.
- *"Nucleus is one compositional ownership pattern"* → confirmed by the same act succeeding.

---

## 5. Validation approach

| Obligation | Measurement | Precedent |
|---|---|---|
| No term is a primitive | The primitive population remains exactly the ratified four; a synthetic primitive is admissible into a copy | `UCPA-L-07` |
| A fourth structural role works end-to-end | Register a classification with `own-capability`; assign a capability; carry it on a record; run the gate | `ISD-L-06` in-memory extension |
| Ownership is data-driven | Withdraw `own-capability` from `nucleus` in a copy; observe `may_own_capability` become false with no file edit | `engine/nucleus/authority.py` docstring |
| Ownership integrity survives | `NUC-INV-03`/`NUC-INV-04` still zero after generalization | existing |
| A layerless structure passes | Declare topology `layerless` and run the nucleus gate | `catalog.py:122` |
| The stratum chain is data | Admit a stratum between two existing strata without editing `generation.py` | `taxonomy.py` fifteen→sixteen |
| No control flow branches on a term | AST scan for a structural literal used as an executable-governance operand | ACEE positional classifier |
| Every supersession names its subject | Check over supersession records | `UCPA-L-05` |
| Cited law resolves | Every cited law identifier resolves to located text; absence is a blocking finding | UCAF `scope_rules` |
| No cardinality assertion | No test asserts 3 roles, 10 classifications or 17 topologies unless cardinality is the invariant | commit `3e424148` |

---

## 6. Risk assessment

| ID | Risk | Severity | Mitigation |
|---|---|---|---|
| SP2-R-01 | Generalizing the owning role admits unowned or multi-owned capabilities | **HIGH** | Preserve `NUC-INV-03`/`04` unchanged. Generalize *who may own*, never *that exactly one owner exists*. |
| SP2-R-02 | Converging toward CEU imports the unlocatable `CEU-002`/`CEU-005` citation into the authoritative plane | **HIGH** | Step 1 before all others. |
| SP2-R-03 | Replacing the stratum chain breaks civilization generation, which currently depends on the literal parents | **HIGH** | Contribute-and-project per `CEP-MOD-002`; retain the local chain as a checked projection that fails closed. Blocked on M-0's missing `verify_vocabulary_alignment`. |
| SP2-R-04 | Widening `StructuralRole` breaks `SubjectRecord` serialization and `FG-18` | **MEDIUM** | Same contribute-and-project pattern. |
| SP2-R-05 | Blanket reclassification is unmeasurable and void | **HIGH** | Per-term named supersession only. |
| SP2-R-06 | Admitting `object`/`component` rows creates vocabulary by implication where none was intended | **MEDIUM** | Decide admit-or-omit explicitly; do not admit merely to complete a table. |
| SP2-R-07 | `UNAF-001`'s `NF-01..NF-36` freeze contract is treated as void because part of `UMN-001` was superseded | **MEDIUM** | Supersede per clause, citing `UCPA-001` §3.3's precision as the model. |
| SP2-R-08 | Reclassification proceeds while capability ownership remains unmeasured, so the fix cannot be validated | **HIGH** | Step 3 before step 4. |
| SP2-R-09 | The two already-compliant terms (Layer, Entity) are needlessly re-touched | **LOW** | Record as compliant; take no action. |

---

## 7. Acceptance criteria

1. Each of the nine terms carries a **recorded class** (A/B/C/D) or is recorded as **undefined**. `Object` and `Component` are admitted or explicitly omitted; neither is silently classified. **Currently: 0 recorded, 2 undefined.**
2. `CEU-002` and `CEU-005` resolve to located text or the citations are corrected. **Currently 0 located occurrences.**
3. The contradiction in SC-C-01 is closed by one act naming both surfaces. No note reconciles them.
4. A synthetic fourth structural classification holding `own-capability` owns a capability end-to-end — registry, record, gate — with no engine edit.
5. `NUC-INV-03` and `NUC-INV-04` still hold after generalization. Integrity preserved, exclusivity relaxed.
6. A stratum is admissible between two existing strata in `engine/civilization/generation.py` without editing the module. **Currently impossible — literal tuple with literal parents.**
7. Topology `layerless` passes the nucleus gate.
8. The nine capability namespaces are registered and their union is proven equal to the 131-entry catalog, both directions.
9. `ISD-CE-09` / `ISD-G-01` is closed by an owner act or re-disclosed unchanged with its gap id. It is not quietly marked intentional.
10. Every supersession names its subject artifact and clause. Blanket supersession refused.
11. No claim that the structural vocabulary is permanently open. Permitted wording: *no discovered fixed boundary exists in the validated dimensions.*
12. Working tree unchanged; no law, enum or declaration written. **Verified at close.**

---

## 8. Refusals

- Editing `engine/nucleus/law.py`, `engine/ceu/catalog.py`, `engine/civilization/generation.py`, or `StructuralRole`. Not performed.
- Enacting any supersession. `UNAF-001` and `UMN-001` remain in force as read.
- Classifying `Object` or `Component` into the CEU taxonomy. They are absent from it; assigning a class would be admission disguised as classification.
- Asserting `CEU-002`/`CEU-005` do not exist. Measured: **no located text in markdown or JSON**. Existence outside this repository is unknown and not asserted either way.
- Reading `engine/civilization/generation.py` beyond lines 80–100, and reading `engine/uckp/validation.py`. The `INV-14` blind spot is therefore carried forward as **APPARENT**, quoted from `CEP-MOD-002` Output 10, not re-measured.
- Reading `00-CMG/CMG-000001` primary text. Its articles are cited **as quoted inside** `UCOS-MOD-001` and `UCPA-001`. Verify against the primary instrument before any binding act.
- Executing any `*-gate` target, including the nucleus gate and `rib-gate`. Refused: they write tracked registers.

---

## 9. Determination

**ZERO PRIMITIVES · FIVE ALREADY DATA · TWO UNDEFINED · TWO FIXED HIERARCHIES STILL IN CODE.**

The consolidated answer to the directive's classification question is that the repository has already decided the hard part. The primitive set is four and open. `UCOS-MOD-001` has already ruled the structural vocabulary out of the Permanent Constitutional Ontology on the durable ground that permanence belongs to shape, not to nouns. `Layer` and `Entity` are fully declassified, and `layerless` exists precisely so that "no layers" is declarable — which is stronger than the directive requires.

What remains is not a classification exercise but three concrete defects. One law file still enforces exclusivity that its own source withdrew, and its withdrawal cites law nobody can locate. A second fixed hierarchy sits in `engine/civilization/generation.py` as a literal chain of literal parents — the exact construct the directive names invalid, and one that no prior determination or migration plan has reached. And `Capability`, the term most entangled in ownership claims, is spread across nine parallel namespaces with no register, so the invariant asserting single capability ownership is measured over a population that has never been shown to be the capability population.

Until those three are addressed, the terms are simultaneously patterns and mandatory containers, and any single statement about which they are would be true of one surface and false of another.

**VERDICT: `DETERMINATION-COMPLETE · NINE TERMS CLASSIFIED · THREE DEFECTS OPEN · IMPLEMENTATION-NOT-AUTHORIZED`**

No law edited, no enumeration widened, no supersession enacted, no term admitted. Working tree unchanged.
