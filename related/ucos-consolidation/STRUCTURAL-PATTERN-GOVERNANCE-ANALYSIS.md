# UNIVERSAL STRUCTURAL PATTERN GOVERNANCE DETERMINATION

| Field | Value |
|---|---|
| ARTIFACT | `UNIVERSAL-STRUCTURAL-PATTERN-GOVERNANCE-DETERMINATION.md` |
| CLASSIFICATION | `EVIDENCE` |
| AUTHORITY | **NONE — DERIVED TRUTH.** Supersedes nothing, reclassifies nothing, ratifies nothing. Reclassification of a structural term is a visible admission act reserved to a governing authority; this determination records what is currently bound and by what text. |
| DISPOSITION | **DETERMINATION ONLY.** No law edited. No enum widened. No supersession enacted. |
| SUBJECT | Classification of Nucleus, Micro-Nucleus, Universe, Layer, Domain, Module, Platform, Service, Network, Ecosystem as Structural Pattern / Projection / Composition / Contextual Representation rather than Universal Primitive / Permanent Boundary / Mandatory Container / Fixed Hierarchy |
| BASELINE | HEAD `03179308f5cb` · branch `integration/recovery-001` · working tree unchanged |
| MODE | Read-only measurement. No registry mutation. No identity minting. No certification claim. |
| GOVERNING INSTRUMENTS | `UCPA-001` §5 (primitives remain open) · `UCOS-MOD-001` §3.2/§4 · `CMG-000001` XIII.2, XIV.7, LXXVI.1, LXXVI.5, LXXVI.6 · `CEP-007 XIII` (supersession is the forward channel) · `UCPA-L-05` (a supersession that does not name its subject is not a supersession) |
| REFUSES | Reclassifying any term by reinterpretation. Editing `engine/nucleus/law.py`. Asserting that the CEU demotion is constitutionally grounded when its cited law has no located text. |

> **Headline.** The repository holds **two live and mutually contradictory statements about the same terms.** `engine/ceu/catalog.py` has already demoted nucleus, layer, domain, platform and service to **data rows**, describing `layer` as *"Owns nothing, and is optional"* and `layered` as *"One arrangement among many, never mandatory"* — while `engine/nucleus/law.py` simultaneously binds *"Capabilities are owned by Nuclei and by nothing else … or the repository is in violation."* The directive's requested reclassification is therefore **half-executed**, and the unexecuted half is guarded by zero-tolerance invariants. Separately, the executed half cites `CEU-002` and `CEU-005` as its authority, and **neither identifier has any text anywhere in the repository outside Python comments.**

---

## 0. What was measured, and with what

| Question | Command / file | Result |
|---|---|---|
| Is nucleus still mandatory in code? | `engine/nucleus/law.py:41-46` | `SUPREMACY_CLAUSE` — *"Capabilities are owned by Nuclei and by nothing else. A Layer organises and owns nothing. A Composition selects Nuclei and owns nothing. Every capability resolves to exactly one owning Nucleus, or the repository is in violation."* |
| Is layer-ownership forbidden by clause? | `engine/nucleus/law.py:160-166` | `NL-02` *"Layers own nothing"* — *"A Layer SHALL NOT own a capability, truth, an authority, a registry, governance, a contract, an identity, a runtime, intelligence or an evolution path."* `refuses="any ownership assignment whose owner holds the LAYER role"` |
| Is it measured? | `engine/nucleus/law.py:238-260` | `OWNERSHIP_INVARIANTS`, preceded by *"The invariants the authority must measure. Zero-tolerance by construction."* — `NUC-INV-01` layer_owned_capabilities = 0 · `NUC-INV-02` composition_owned = 0 · `NUC-INV-03` unowned = 0 · `NUC-INV-04` multi_owned = 0 (`NUC-INV-05..09` also present) |
| How many structural roles can a record carry? | `engine/nucleus/law.py:69,71,73` | exactly three — `NUCLEUS`, `LAYER`, `COMPOSITION` |
| Is that enum still an authority? | `engine/nucleus/law.py:49-52` | *"A **projection** of the CEU classifications … This enum is no longer an authority … Legacy values derive from CEU; never the reverse."* |
| What has already been demoted to data? | `engine/ceu/catalog.py:195-212` | 10 classification rows; header comment: *"Nucleus and Layer appear here as rows — the demotion CEU-002 and S-012 require … neither is privileged by anything except what this data says."* |
| Is `layer` optional in data? | `engine/ceu/catalog.py:202` | `("layer", "An organising stratum. Owns nothing, and is optional (CEU-005).", {})` |
| Is a layerless arrangement declarable? | `engine/ceu/catalog.py:121-122` | `("layered", "Ordered strata. One arrangement among many, never mandatory (CEU-005).")` and `("layerless", "The explicit absence of strata, so 'no layers' is declarable.")` |
| Do `CEU-002` / `CEU-005` have located text? | `grep -rl 'CEU-005' --include='*.md'` → 0 · `--include='*.json'` → 0 · `--include='*.py'` → 2 | **No constitutional text. Python comments and one test docstring only.** |
| Is the openness template proven elsewhere? | `engine/context/taxonomy.py` `ContextKind` | 16 members; `MEASUREMENT` admitted as the sixteenth by `ADR-0005` in commit `7b7d0fd9` |

---

## 1. Current state

### 1.1 Where the reclassification has already happened

`UCOS-MOD-001` already made the negative determination the directive asks for, in terms that leave nothing to interpret:

> *"`UCKP-ART-20` binds the law to remain valid across future civilizations. A law that named `Universe`, `Domain`, and `Component` as permanent could not satisfy that clause… **The permanence is in the shape, never in the noun.**"*

> *"**Determination:** The Permanent Constitutional Ontology consists of object-existence, identity, facet, relationship, authority, determinism, immutability, and open registration. `Universe`, `Domain`, `Capability`, `Component` are **not** members of it."*

And its evidence row E-01 answers the question directly: *"Does any law state Universe/Domain/Capability/Component are permanently immutable? … **No such clause exists.**"*

`UCPA-001` settles the primitives and holds them open. The ratified set is exactly four: `ONT-01` BEING (axiom, non-layer, unanchorable), `ONT-02` EXISTENCE, `ONT-03` RELATIONSHIP, `ONT-04` TRANSFORMATION. **No structural container is among them.** §5 states: *"**Determination 4 — The primitives remain open.** The set is not closed by this determination"*, resting on `CMG-000001` LXXVI.5, under which expansion is *"unbounded in count… any apparent limit SHALL be read as a **defect**."*

The `00-CEP` constitution series does not bind the vocabulary at all: a search of `00-CEP/CEP-00*.md` for an article making Nucleus, Layer or Domain mandatory returns one incidental hit using "domain" in its ordinary sense.

### 1.2 Where it has not

`engine/nucleus/law.py` remains in force and is measured with zero tolerance. This is not dormant prose — `NL-02` carries an executable `refuses` clause, and `NUC-INV-01..04` assert exact zero counts. A capability owned by anything other than a nucleus is a violation today.

`UNAF-001` still frames Nucleus as *"the atomic unit of canonical ownership"* and fixes a three-term containment relation (Nucleus / Universe / Platform) with the preface that these *"are constitutionally distinct and must not be confused"*. `UMN-001` still carries the decomposition chain `Universe → Domain → Capability → Component`, though its line-501 hierarchy diagram is already **SUPERSEDED** by `UCPA-001` §3.3 as to owner and as to BEING's standing.

### 1.3 The prior migration determination is decided and unexecuted

`CEP-MOD-002` decided a single migration act — each engine **contributes** its structural vocabulary to `engine/uckp/vocabulary.py::VocabularyRegistry` and **retains** its local type as a checked projection guarded by `verify_vocabulary_alignment`, failing closed — across six sites `H-01..H-06` in order `M-0..M-6`. Its own closing line: *"Files modified: none. Code changed: none. Engines edited: none."* Verdict: **READY, BLOCKED ON M-0**, because the named verifier `verify_vocabulary_alignment` **does not exist**. It also recorded that `KNOWLEDGE_KIND_VOCABULARY` declares 18 terms while `KnowledgeKind` has 17 — *"The divergence the docstring promised would fail closed is already present and silent."*

Critically for this determination: **`CEP-MOD-002`'s six sites do not include `engine/nucleus/law.py` or `engine/ceu/catalog.py`** — the actual seats of the structural vocabulary. The population addressed here was never reached by that migration.

---

## 2. Classification of the ten requested terms, as currently bound

Measured against `engine/ceu/catalog.py`'s three seed populations.

| Term | Current representation | Directive's target class | Delta |
|---|---|---|---|
| **Nucleus** | CEU **classification** row, holds faculty `own-capability`; also `StructuralRole.NUCLEUS` | Structural Pattern | Row exists, **but** `SUPREMACY_CLAUSE` + `NUC-INV-01..04` still make it the exclusive ownership container |
| **Micro-Nucleus** | CEU classification row, `specializes: nucleus` | Structural Pattern | Aligned in data; `UMN-001` prose still binds it to `Capability(CAP-NNNN)` |
| **Universe** | CEU **form** row (an existence form), **not** a classification | Contextual Representation | Broadly aligned; `UNAF-001` §1.4 still fixes it as a governed composition of Nuclei |
| **Layer** | CEU classification row — *"Owns nothing, and is optional"*; plus topologies `layered` (*"never mandatory"*) and `layerless` | Projection | **Already aligned.** Strongest precedent in the repository. |
| **Domain** | CEU classification row, no faculties | Structural Pattern | Aligned in data; `UMN-001` chain still positions it |
| **Module** | **ABSENT** — not a classification, form or topology | Structural Pattern | No binding text found anywhere; nothing to supersede |
| **Platform** | CEU classification row, `specializes: composition` | Composition | Aligned |
| **Service** | CEU classification row, `specializes: nucleus` | Structural Pattern | Aligned |
| **Network** | CEU **topology** row | Projection | Aligned |
| **Ecosystem** | **ABSENT** as a defined container | Composition | Reported as appearing in `UNAF-001:12` only as a generation target, never defined — **APPARENT** |

**Finding: seven of ten terms are already data rows or absent.** The directive's reclassification is largely satisfied in the data plane. The unsatisfied residue is concentrated almost entirely on **Nucleus**, and specifically on ownership exclusivity.

---

## 3. Discovered gaps

| ID | Finding | Grade |
|---|---|---|
| **SP-G-01** | **A live contradiction between two executing surfaces.** `engine/ceu/catalog.py:202` declares layer optional and ownerless-by-data; `engine/nucleus/law.py:42-46` declares nucleus the sole owner *"or the repository is in violation"*, measured at zero tolerance. Both execute. Nothing reconciles them. | **CONFIRMED** |
| **SP-G-02** | **The executed demotion cites law that has no located text.** `CEU-002` and `CEU-005` are cited in `engine/ceu/catalog.py` as the authority for demoting nucleus and layer. A repository-wide search finds **zero** occurrences in markdown or JSON — only Python comments and one test docstring. The demotion that already happened rests on an unlocatable citation. | **CONFIRMED** |
| **SP-G-03** | **`StructuralRole` is closed at three members and this is self-declared as a limitation.** A fourth classification can be registered in the CEU catalogue and discovered through `registered_roles`, but **cannot be carried by a legacy `SubjectRecord`**. So a new structural pattern is representable in the registry and unrepresentable on the record — precisely the "fixed hierarchy" condition the directive targets. | **CONFIRMED** |
| **SP-G-04** | **Two terms have no definition to reclassify.** `Module` and `Ecosystem` are absent from all three CEU seed populations. Reclassifying them would be *admission*, not supersession, and would require a different instrument. | **CONFIRMED** |
| **SP-G-05** | **`CEP-MOD-002` is blocked on a function that was never written.** `verify_vocabulary_alignment` is *"designated, named, and unbuilt."* Any vocabulary contribution depending on it inherits the block. | **CONFIRMED** |
| **SP-G-06** | **`INV-14` has a measurement blind spot.** Per `CEP-MOD-002` Output 10, `_probe_infinite_extensibility` iterates only *registered* vocabularies, so INV-14 *"currently returns satisfied while six closed vocabularies in the same repository hard-refuse an unknown future member."* Extensibility is reported satisfied on an unrepresentative sample. | **APPARENT** — quoted from the determination; `engine/uckp/validation.py` was not re-read in this pass. |

---

## 4. Affected artifacts

**Bound and would require a governed supersession act:** `engine/nucleus/law.py` (`SUPREMACY_CLAUSE`, `StructuralRole`, `OWNERSHIP_CLAUSES` `NL-01..NL-10`, `OWNERSHIP_INVARIANTS` `NUC-INV-01..09`), `engine/nucleus/registry.py` (hardcodes `StructuralRole.NUCLEUS.value` when resolving `composes` targets), `engine/nucleus/cli.py` (gate `FG-18-NUCLEUS-OWNS-CAPABILITY`), `UNAF-001` §1.1/§1.3/§1.4, `UMN-001` SHALL/SHALL-NOT blocks.

**Already aligned, would be read only:** `engine/ceu/catalog.py`, `engine/ceu/existence.py`, `engine/nucleus/authority.py`, `UCOS-MOD-001`, `UCPA-001`.

**Related but out of scope:** the six `CEP-MOD-002` sites (`DiscoveryKind`, UKIP `Facet`, `cko.universe`, the civilization stratum chain, `LAYER_ORDER`, projection kinds).

**Must not be touched:** `00-BOOK/DATA/**`, `00-BOOK/REGISTRIES/**`, `00-MASTER/UCPA-000001/ucpa-declaration.json`, any generated `canonical_path`.

---

## 5. Implementation impact

**The channel is supersession, not editing.** `UCPA-001` §3.4 records the doctrine, quoting `engine/foundation/guards/frozen_paths.py`: *"Identity is immutable, history is append-only, and evolution is unlimited through those channels; only in-place modification of a certified artifact is refused."*

Two hard procedural constraints:

1. **Every supersession must name its subject.** `UCPA-L-05` measures exactly this — *"a supersession that does not name its subject is not a supersession."* A blanket statement that structural terms are patterns would be unmeasurable and therefore void.
2. **Reclassification by reading is forbidden.** `CMG-000001` LXXVI.6 — *"Reinterpretation is invisible to validation; admission is visible."* The reclassification must be an explicit, visible act, recorded in data.

**The executed template exists.** `engine/context/taxonomy.py` moved a universal population from fifteen to sixteen by adding a data row, admitting `MEASUREMENT` under `ADR-0005`. Its own docstring states the general principle: *"the seed is data, no control flow in this layer branches on a kind, and a seventeenth needs no more than another row."* The precise structural precondition it satisfies — *"no control flow in this layer branches on a specific kind"* — is exactly what `engine/nucleus/law.py` does **not** satisfy, since ownership exclusivity is asserted in clauses and measured in invariants.

**Sequencing.** SP-G-02 comes first. Locating or admitting the text of `CEU-002`/`CEU-005` is a prerequisite, because the already-executed demotion currently rests on an unlocatable citation; superseding `engine/nucleus/law.py` in favour of that demotion would compound the defect rather than resolve it.

**What reclassification does *not* require.** It does not require abolishing nucleus ownership. `NL-04` — every capability resolves to exactly one owner — is a sound integrity invariant independent of what the owner is *called*. The reclassification needed is narrower: that the **owning role is one registered classification among several holding the `own-capability` faculty**, rather than a hardcoded identity. `engine/nucleus/authority.py` already performs this inversion — *"Remove `own-capability` from the `nucleus` classification and `may_own_capability` becomes `False` here, with no edit to this file."* The residue is the closed three-member `StructuralRole` and the clause text that names nucleus specifically.

---

## 6. Validation approach

| Obligation | Measurement | Precedent |
|---|---|---|
| A fourth structural classification is representable end-to-end | Register a synthetic classification holding `own-capability`, then assign a capability to a subject carrying it, and observe the invariants pass | `ISD-L-06` in-memory extension |
| Ownership is data-driven, not code-driven | Withdraw `own-capability` from `nucleus` in a **copy** and observe `may_own_capability` become false with no file edit | `engine/nucleus/authority.py` docstring |
| A layerless arrangement is declarable and passes | Declare a subject graph with topology `layerless` and run the nucleus gate | `engine/ceu/catalog.py:122` |
| No control flow branches on a structural term | AST scan of `engine/nucleus/` for a literal `"nucleus"`/`"layer"` used as an executable-governance operand | ACEE positional classifier |
| Every supersession names its subject | `UCPA-L-07`-style check over the supersession records | `UCPA-L-05` |
| Integrity invariants survive reclassification | `NUC-INV-03`/`NUC-INV-04` (unowned, multi-owned) must still be zero after the owning role is generalized | existing |

Cardinality discipline applies: no test may assert that there are exactly three structural roles, or ten classifications, unless that count is itself the domain invariant.

---

## 7. Risk assessment

| ID | Risk | Severity | Mitigation |
|---|---|---|---|
| SP-R-01 | Generalizing the owning role weakens a genuine integrity invariant and admits unowned or multi-owned capabilities | **HIGH** | Preserve `NUC-INV-03`/`NUC-INV-04` unchanged. Generalize *who may own*, never *that exactly one owner exists*. |
| SP-R-02 | Superseding `engine/nucleus/law.py` in favour of a demotion whose cited law (`CEU-002`/`CEU-005`) has no located text compounds SP-G-02 | **HIGH** | Locate or admit the law text first. Do not build on an unlocatable citation. |
| SP-R-03 | Widening `StructuralRole` breaks `SubjectRecord` serialization and the `FG-18` gate | **MEDIUM** | Apply the `CEP-MOD-002` pattern: contribute to the registry, retain the local type as a **checked projection** that fails closed. |
| SP-R-04 | Reclassification is performed by reinterpretation, which `CMG-000001` LXXVI.6 makes invisible to validation | **HIGH** | Record every reclassification as a data row naming its superseded subject. |
| SP-R-05 | `UNAF-001`'s freeze contract (`NF-01..NF-36`, *"An unstated facet is MISSING and blocks freeze"*) is treated as void because parts of `UMN-001` were superseded | **MEDIUM** | Supersede explicitly and per-clause. `UCPA-001` §3.3 superseded one row and one diagram and left everything else standing — copy that precision. |
| SP-R-06 | Two live contradictory surfaces persist, and future work cites whichever suits it | **HIGH** | Treat SP-G-01 as the primary finding; converge, do not annotate. |
| SP-R-07 | `Module` / `Ecosystem` are "reclassified" though never defined, creating vocabulary by implication | **LOW** | Admit or omit. Do not reclassify an undefined term. |

---

## 8. Acceptance criteria

1. `CEU-002` and `CEU-005` either resolve to located constitutional text, or the citations in `engine/ceu/catalog.py` are corrected to name an instrument that exists. **Currently: 0 located occurrences.**
2. The contradiction in SP-G-01 is resolved by a single act naming both surfaces. No note reconciles them.
3. A synthetic fourth structural classification holding `own-capability` can own a capability end-to-end — registry through `SubjectRecord` through gate — with no engine edit.
4. `NUC-INV-03` (unowned = 0) and `NUC-INV-04` (multi-owned = 0) still hold after any generalization. Integrity is preserved while exclusivity is relaxed.
5. Each of the ten terms carries an explicit recorded class — Structural Pattern, Projection, Composition, or Contextual Representation — or is recorded as **not defined** (`Module`, `Ecosystem`).
6. Every supersession names its subject artifact and clause. Blanket supersession is refused.
7. A `layerless` structural declaration passes the nucleus gate.
8. No claim is made that the structural vocabulary is permanently open. Permitted wording, per the evidence rule: *no discovered fixed boundary exists in the validated dimensions.*

---

## 9. Refusals

- Editing `engine/nucleus/law.py`, `StructuralRole`, or any clause or invariant. Not performed.
- Enacting any supersession. `UNAF-001` and `UMN-001` remain in force as read.
- Asserting that `CEU-002`/`CEU-005` do not exist. Measured: they have **no located text in markdown or JSON**. Whether text exists outside this repository is unknown and is not asserted either way.
- Reading `00-CMG/CMG-000001` directly. Its Articles XIII.2, XIV.7 and LXXVI.1-6 are cited here **as quoted inside `UCOS-MOD-001` and `UCPA-001`**. Before any binding act, verify against the primary text.
- Re-reading `engine/uckp/validation.py`. SP-G-06 is graded **APPARENT** for that reason.
- Executing `make rib-gate`, `nucleus` gate targets, or any `*-gate` that writes tracked registers.

---

## 10. Determination

**HALF-EXECUTED — ONE CONTRADICTION AND ONE UNLOCATABLE CITATION BLOCK COMPLETION.**

The directive's requested reclassification is not a new idea in this repository; it is a partially-completed migration. The data plane has already demoted the vocabulary, in language stronger than the directive asks for — `layer` is *optional*, `layered` is *never mandatory*, `layerless` is *declarable*, and `nucleus` is *"privileged by nothing except what this data says."* `UCOS-MOD-001` and `UCPA-001` have already determined that no structural container is a permanent primitive.

What remains is not a reclassification exercise but a **convergence**: one law file still asserts exclusivity that the data plane has withdrawn, and the withdrawal cites an authority no one can locate. Until both are addressed, the terms are simultaneously patterns and mandatory containers, and any statement that they are "one or the other" would be true of one surface and false of the other.

**VERDICT: `DETERMINATION-COMPLETE · CONVERGENCE-REQUIRED · IMPLEMENTATION-NOT-AUTHORIZED`**

No law edited, no enum widened, no supersession enacted. Working tree unchanged.
