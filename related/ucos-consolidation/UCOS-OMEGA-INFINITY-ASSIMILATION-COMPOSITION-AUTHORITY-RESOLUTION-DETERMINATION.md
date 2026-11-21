# UCOS Ω∞ — ASSIMILATION COMPOSITION AND AUTHORITY VACANCY RESOLUTION DETERMINATION

| Field | Value |
|---|---|
| ARTIFACT | `UCOS-OMEGA-INFINITY-ASSIMILATION-COMPOSITION-AUTHORITY-RESOLUTION-DETERMINATION.md` |
| KIND | `CMG-K-17` — Determination |
| STANDING | **DECLARATIVE** (`CMG-000001` XII.6) |
| AUTHORITY | **NONE — DERIVED TRUTH.** Assigns no ownership, creates no authority, creates no identifier, creates no requirement, creates no ADR, modifies no registry, alters no certification, resolves no vacant authority. Not registered in `CMG-REGISTRY.json`; **SHALL NOT be cited as constitutional authority** (`CMG-L-01`). |
| MODE | **OBSERVE.** Determination only. |
| MUTATION | **READ-ONLY OBSERVATION.** Single mutation is the creation of this file. |
| BASELINE | HEAD `bae59755` · branch `integration/recovery-001` · working tree 70 entries |
| DISPOSITION VOCABULARY | Restricted to the constitutional set: **REUSE · EXTEND · CREATE · RECORD AS GAP · REJECT** (`LXXVII.2`, closed by `LXXVII.3`) plus **HOLD** (`LXXVII.5`). No other term is used as a disposition. |
| PRESERVATION | Preserves existing authority ownership · `CMG-INV-02` injectivity · no duplicate authority · no ownership absorption · no unauthorized consolidation. Verified per concern in §2 and §9. |
| PRIOR ART | Fourth in chain. Extends `…ASSIMILATION-FABRIC-AUTHORITY-BOUNDARY-DETERMINATION.md` and `…UNIVERSAL-ASSIMILATION-AUTHORITY-OWNERSHIP-DETERMINATION.md`. **Materially revises the second's outlook** — §10.4. |

---

## 1 — EXECUTIVE DETERMINATION

### 1.1 The determination

**Universal Assimilation is a Composition. This is a derivation, not a proposal, and it requires no new authority and no T1 act.**

The prior determination in this chain concluded that a Universal Assimilation *Authority* is unavailable — correctly. What it did not locate is that the repository already legislates the alternative as a **first-class constitutional structural role with its own registered faculty**, enforced at admission and measured by five blocking invariants.

`engine/nucleus/law.py`, `SUPREMACY_CLAUSE`, verbatim:

> *"Capabilities are owned by Nuclei and by nothing else. A Layer organises and owns nothing. **A Composition selects Nuclei and owns nothing.** Every capability resolves to exactly one owning Nucleus, or the repository is in violation."*

Two disjoint faculties exist in CEU data, not in code:

| Faculty | Held by | Grants |
|---|---|---|
| `own-capability` | `nucleus` (+ specializations) | the right to own a capability |
| `select-units` | `composition` (+ `platform`) | *"the right to select units into a composition"* |

`engine/ceu/catalog.py` registers `("composition", "A selection of nuclei plus configuration. **Owns nothing.**", {ATTR_FACULTIES: ("select-units",)})`. Ownership and selection are therefore **separate registered rights**, and a composition holds only the latter.

### 1.2 The precedent that decides it

`engine/nucleus/catalog.py` opens with the constitutional correction that is the exact analogy:

> *"**Commerce is not a Nucleus. Commerce is a Composition.** So are Amazon, Uber, PayTM, WhatsApp, Facebook, Instagram, X, LinkedIn, YouTube, ERP, CRM, LMS, EdTech, and every sector, banking, insurance, healthcare, government, defence, industrial, scientific, research and civilisational platform. None of them appears in `SEED_NUCLEI`. Each appears in `SEED_COMPOSITIONS`, where it exists **only as a selection of registered nuclei plus configuration**."*

And the mechanism that makes it a derivation rather than a label — `engine/nucleus/model.py::derive_role()`:

> *"The rule is total and has no default: a subject that selects nuclei composes; a subject that owns exactly one canonical concept operates; a subject that does neither only organises. This is the clause that makes 'Commerce is a Composition' a **derivation** rather than an opinion — Commerce selects nuclei, therefore Commerce composes, therefore Commerce owns nothing."*

Universal Assimilation selects Identity, Context, Relationship, Knowledge, Security, Trust, Authority, Lifecycle, Validation and Evolution. **It selects. Therefore it composes. Therefore it owns nothing. Therefore no ownership is allocated, and no allocating authority is required.**

The classification is not optional either. `SubjectDeclaration.__post_init__` refuses the hybrid outright: `MisclassificationError("a subject may own a concept or compose nuclei, never both (NL-05/NL-06)")`. A Universal Assimilation Authority is not merely unavailable for want of a T1 act — **a subject that selects cannot be registered as an owner.**

### 1.3 The six primary questions

| # | Question | Determination |
|---|---|---|
| 1 | **Lawful composition model** | The located CEU/nucleus composition role: **select registered units, add configuration, author nothing.** Six located precedents (§3.2) converging on a seven-element test (§3.3). Bounded by `NL-03`, `NL-05`, `NL-07`, `NL-08` and measured by `NUC-INV-02/05/06/07/08`, all blocking |
| 2 | **Who owns the composition relationship** | **`UCOS-CEU-001`** owns *what a composition is* — a registered instrument whose declared `owns` includes existence representation, relationship and topology instances. The composition **subject** holds `select-units`; it owns no concern. **No new authority.** The relationship itself is an ordinary registration under an owned role |
| 3 | **Single-click without a new authority** | **Already constitutional, and already built four times.** `CMG-000001` **XVIII.1** — *"Delegation under this instrument IS recognition, not transfer"*; **LXXXII.7** — *"No entry… confers, alters, limits, or conditions the authority of the named owner."* The nearest working instance is `ucos-foundation determine`, which already composes truth + ownership + assimilation + measurement into one content-addressed `CLOSED`/`NOT-CLOSED` verdict (§8) |
| 4 | **How the vacant T1 tier is handled** | **It is not on the composition path.** T1 is the tier that allocates a **new substantive concern**. A composition allocates none — it owns nothing. `VAC-01` is recorded, its provisional consequence is carried, and per `XVII.4` no instrument is promoted into it. **The vacancy blocks four decisions, not the composition** (§5) |
| 5 | **Decisions requiring T1** | **Four**, all of which would allocate or decide a concern: a Universal Assimilation Authority (independently refused); trust-decision-at-admission ownership; the supply-chain trust boundary's owner; the unregistered surface's authority standing (§10) |
| 6 | **Decisions that can proceed** | **Eleven.** All ten concern REUSEs, plus the composition declaration itself — none requires an allocation. Four EXTENDs against located owners are additionally available (§12) |

### 1.4 The single constraint that governs everything below

`NL-07` — **No platform-specific capability**:

> *"No capability SHALL be specific to a composition. A capability that names a composition in its own domain is a **configuration** of a nucleus capability, not a capability."*

And `CEP-009` ADDENDUM B **B.4.3**, the constitutional core of the composition doctrine:

> *"**This Addendum introduces no lifecycle.** Every stage of B.4.1 is owned elsewhere and is consumed by reference; **this Addendum declares the composition and nothing else.** Where a stage has no located owner, this Addendum IS **void as to that stage**, and the absence SHALL be recorded as a gap under `CMG-000001` LXXVIII **rather than remedied by authoring a stage here.**"*

**The bright line: composition is constitutional if and only if it (a) selects, orders, gates or configures, and (b) authors nothing.**

This has a sharp and unwelcome consequence for the surface presently claiming to be the universal substrate. See §9.4 — **`platform/universal_assimilation` as currently built exceeds what a composition may do**, because its seven adapters transform content that no located nucleus owns. That is authorship, not selection.

---

## 2 — CONCERN OWNERSHIP MATRIX

The directive's ten concerns, decomposed. Each retains its canonical owner; the composition selects and owns none of them.

| # | Concern | Existing owner | Authority instrument | Evidence | Current implementation | Composition requirement | Dependency | Disposition |
|---|---|---|---|---|---|---|---|---|
| 1 | **Identity** | `UCKP-ART-05` — one authority, two planes | `UCKP-LAW-0001` (SUPREME) | `identity_authority_resolution`; **`CAA-INV-04 EXACTLY_ONE_IDENTITY_AUTHORITY`** | `engine/uckp/identity.py` (SUPREME plane, pure/total/clock-free) · `00-BOOK/DATA/id-ledger.json` (PERSISTENCE, *"the ONE such binding"*) · derivation `repository_local_urn` (total, pure, injective) | Selected: the composition **requests** an identity; it mints none | Layer-Zero `engine/uckp/canonical.py`, guarded by `UCKP-INV-03` | **REUSE** |
| 2 | **Context** | `UCXI-000001` | Registered instrument, role `PROJECTION`, under `ART-04/07/13` | `subordinate_instruments`; declared `may_never_own`: **Permission** — *"CXL-10 is that context describes and never grants"* | `engine/context/` — 18 modules; `resolution.py:149 resolve()`; `taxonomy.py:516 extend()` bounded-open; 5 prod importers | Selected: resolve a reference frame | Declared frames as package data | **REUSE** |
| 3 | **Relationship** | `UCKP-ART-07` — model owner `engine/uckp/graph.py` | `UCKP-LAW-0001` | `relationship_graph_resolution`; **`CAA-INV-05`** checks emitted kinds against declared classes **in both directions** | `engine/knowledge/ukip/relationships.py` (temporal validity, fails closed on `Ordering.INCOMPARABLE`) · `engine/lineage/` (4 families, 12,899 edges, 44/44 classified, zero persistence) | Selected: create edges through an authority-requiring surface | `engine/ceu/existence.py:951 relate(authority=…)` | **REUSE** |
| 4 | **Knowledge** | `RA-003` + `CEP-001` LAW-4 Single Canonicity | `CEP-001` (T2, Program Authority) | Matrix knowledge rows; `UKIP-LAW-001…011`; `identity_namespace_resolution` names `engine/knowledge/store.py` | `engine/knowledge/ukip/` — 7-stage pipeline, canonical-home registry (`REGISTERED`/`CORROBORATED`), hash-chained `ProvenanceChain` verifying **without the original** | Selected: submit a unit for homing | Providers, unbounded by `UKIP-LAW-001` | **REUSE** |
| 5 | **Security** | `PHASE-008 SECURITY` — *"the only new ownership"* | `SECURITY-001` (`SL-0`), supreme **within the `SECURITY-*` chain only** | `SECURITY-GOV-000` OUTPUT 6 · **`02-CANONICAL-OWNERSHIP-MATRIX.md` contains zero occurrences of "security"** (verified) | `14-SECURITY/` = 5 documents, **0 code**. `platform/security/` (11 modules) is declared **frozen at `PL-F2`, by reference** — and is a **test-only orphan, 0 production importers** | Selected — but the owner *"enacts nothing at the architecture layer"* (`USA-6`) | Downward-only chain `EL-1 → … → SECURITY` | **EXTEND** (record the row) |
| 6 | **Trust** | **Split; unowned at the point of use** | None for the decision | `trust` is a declared CEU form (`("trust","TRST","Trust",("governance","evidence"))`) — representable, not holdable. **No trust faculty exists** | `platform/foundation/trust.py::TrustEngine` — HMAC, delegation chains, revocation, notary. `require_trusted` at `:539`, six call sites (five in-module guards + `admission.py:398`) | Selected — **but no role holds a right to decide trust** | `platform/security/` (frozen, orphaned) | **RECORD AS GAP** |
| 7 | **Authority** | Three non-competing levels | `CMG-000001` Art. XVII (procedure) · `UCOS-CAA-001` (instrument) · `engine.ceu` via `engine/nucleus/authority.py` (faculty) | `CAA-INV-01…08`; `holds()` **fails closed** — *"a role the substrate does not register holds nothing"* | Art. XVII five steps; eight roles, only `SUPREME` may hold authority, cardinality `EXACTLY_ONE` | Selected: `AUTHORITY_RESOLUTION` is **mandatory stage 7** of Article 14 | `engine/ceu/catalog.py` faculty data | **REUSE** |
| 8 | **Lifecycle** | `UCL-000001`; `UCIC-001` owns the capability lifecycle | Reused verbatim from `UCKP-ART-14`'s 15-stage cycle | Gate `G-25`; `verify_manifest_alignment` diffs `STAGES` against `ucl-stage-manifest.json` in **both directions** | `engine/nucleus/lifecycle.py` — 45 stages as DATA, derived ordering, hash-chained `StageOutcome`, `replay()` fixed point | Selected: route via the `StageFunction` seam; **owner lives in the manifest, not the engine** | `engine.foundation.composition.ordering.derive_order` | **REUSE** |
| 9 | **Validation** | `CEP-004` (operation); 48 checks / 26 gates as data | `CEP-004` via `CMG-DLG-04` | `uccep-bindings.json` — 48 checks, 26 gates `G-01…G-26`, 21 programs; tiers 25 boot / 19 standard / 4 full | `uccep_engine.py::aggregate()` — pure conjunction; *"absence of evidence is never evidence"*; out-of-tier disclosed as a **ceiling**, never dropped | Selected: register a check; the gate reports over checks **it does not own** | `ALLOWED_KEYS` fails closed on undeclared fields | **REUSE** |
| 10 | **Evolution** | `CEP-009`; `UCKP-ART-14` owns the stages | `CEP-009` via `CMG-DLG-09`; `AUTH-INF-001 CR-INF-001` (non-terminality) | `engine/uaue/__init__.py` reads the stage set from Art. 14 because *"a second copy… would be a second authority over one subject"* | 15 stages, append-only, `is_terminal()` ≡ `False`, `next_stage()` wraps | Selected: append at stage 14; re-enter at stage 1 | Blocked on `F-3` (ledger never persisted) | **REUSE** |

**Eight REUSE · one EXTEND · one RECORD AS GAP. Zero CREATE. Zero ownership absorbed.**

### 2.1 Injectivity preserved

`CMG-INV-02` requires the concern→owner mapping be **injective on concerns**. The composition model preserves it by construction, because a composition is not in the mapping's range: it owns no concern, so it appears as no concern's owner. `NUC-INV-02` measures this directly — *"The count of capabilities owned by a COMPOSITION-role subject is zero"*, blocking.

**Determination: composition is the one model that satisfies the directive's preservation requirements simultaneously.** Allocation would have breached injectivity; consolidation would have absorbed ownership; composition does neither.

---

## 3 — COMPOSITION MODEL

### 3.1 Ownership versus composition

| | Ownership | Composition |
|---|---|---|
| Faculty | `own-capability` | `select-units` |
| Held by | `nucleus` (+ specializations `micro-nucleus`, `nano-nucleus`, `service`, `engine`) | `composition` (+ `platform`) |
| What it may do | Own exactly one canonical concept; *"a nucleus that owned two would be two nuclei"* | Select registered units; add configuration |
| What it may not do | — | Own a capability; *"introduce capability logic of its own"* (`NL-03`) |
| Determined by | Declaring a `concept` | Declaring `composes` |
| Refusal | `MisclassificationError` on a NUCLEUS-role subject declaring composed nuclei (`NL-05`) | `CompositionOwnershipViolation("a composition selects nuclei and owns nothing (NL-03)")` at admission |
| Measured | — | `NUC-INV-02/05/06/07/08`, all blocking |

`registry.compose(key)` is the whole realisation of a composition, and its docstring records that it is **structurally incapable** of adding anything:

> *"Realise a composition: its selected nuclei and the capabilities they bring. **This is the whole of 'Commerce'. No commerce-specific code runs;** the result is derived from registered nuclei and their registered capabilities. **A composition contributes no capability of its own, and this method has no way to let it.**"*

It returns a dict containing the literal `"owns_capabilities": False`, with every capability attributed to its owning nucleus (`"owner": c.owner_key`).

### 3.2 The six located precedents

| # | Precedent | Composes | Adds exactly | Disclaimer, verbatim |
|---|---|---|---|---|
| 1 | **`UCIC-001`** (documentary, frozen) | CIOA, CCE, GOV-002, GOV-001-T3, TRACK-001, MCP-003, MCP-006 — enumerated in a `COMPOSES (authoritative sources)` metadata row | a repeatable 15-stage procedure | *"UCIC **composes** existing authorities into a repeatable procedure. **It creates no new authority;** bindingness flows from the instruments it composes."* Self-check row 9: *"No new authority created (composes existing instruments) ✓ (AUTHORITY=NONE)"* |
| 2 | **`CEP-009` ADDENDUM B** (constitutional) | 15 stages, each with a *"Located owner (reused; not restated)"* column | the ordering, *"declared once"* | `B.4.3` (§1.4). `B.11.1` — *"**B.4 binds; it does not author.**"* `B.8.3` — *"creates no authority, no registry, no lifecycle, and no namespace"* |
| 3 | **`ConstitutionalPipeline`** (code) | Discovery, Ownership, DuplicatePrevention, Reuse, Dependency, Composer, Certifier | *"only sequencing and fail-closed gating"* | *"Every engine is **reused verbatim**."* `assimilate()` — *"adds only repository probing and assimilation, **never a second execution controller**"* |
| 4 | **`UniversalFoundation`** (code) | `COMPOSED_CAPABILITIES = ("UCOS-URTF-001","UCOS-UOF-001","UCOS-USAF-001","UCOS-UMPF-001")` — declared as module data | ordering, optionality, content-addressing | Engines are **injected, never constructed**; five-way fail-closed type gate; every method a one-line delegation. *"It never substitutes an empty population for a missing one."* |
| 5 | **`engine/nucleus/`** | — | **this is the constitutional home of composition itself** | `SUPREMACY_CLAUSE`; `NL-03/05/07/08`; `NUC-INV-02/05/06/07/08`; role derived by `derive_role()`, so *"the label cannot be self-asserted"* |
| 6 | **`MetaCivilizationPlatform`** (code) | DimensionRegistry + CompositionPlanner + ConstitutionalGenerator over one MetaKernel | a facade | class attribute `authority = "NONE"`, emitted in its own `certify()`. *"**Authority: NONE. The kernel governs; this layer composes.**"* Gated by `_gate_no_parallel_authority()` |

Further instances: `platform/security/observability.py` (*"adds only the security-specific signal shaping"*, refuses construction without a certified L8 service), `platform/universal_assurance/orchestrator.py`, `engine/graph/adapter.py`, `AutonomousComposer`.

### 3.3 The seven-element constitutional test for a composition

Derived from what all six precedents satisfy. A composition is lawful when and only when:

| # | Element | Located enforcement |
|---|---|---|
| 1 | **Authority is declared NONE, in the artifact's own identity surface** | UCIC-001 metadata row + footer; `B.8.3`/`B.11.3`; `MetaCivilizationPlatform.authority = "NONE"` |
| 2 | **The composed set is enumerated as DATA** | `COMPOSES` row; `B.4.1` table; `COMPOSED_CAPABILITIES`; `SEED_COMPOSITIONS`; `composes: tuple[str, ...]`. *"Adding a member is an edit to a tuple — never to a rule"* |
| 3 | **Each member names its located owner, and the owner lies outside the composition** | `ucef-framework.json`: `owner` *"MUST lie outside this programme's own home, otherwise the stage would be authored here rather than bound — the duplication B.4.3 forbids"* |
| 4 | **The composition adds exactly one thing, and names it** | sequencing+gating · ordering · signal shaping · selection+configuration. Anything beyond the named addition is authorship |
| 5 | **Ownership is affirmatively disclaimed, with a refusal path attached** | `NL-03` `refuses=`; `CompositionOwnershipViolation`; the recurring *"no second registry / identifier / lifecycle / hash primitive / execution controller"* formula |
| 6 | **Closed, acyclic, fail-closed** | `NL-08` — *"a composition that selects an unregistered nucleus is not composable and does not exist"*; `NUC-INV-07` cycles; `B.4.4` dependency closure; `seed_subjects()` orders layers → nuclei → compositions so selections exist before admission |
| 7 | **The disclaimer is MEASURED, not asserted** | `NUC-INV-02` = 0 blocking; `UCEF-VAL-13`/`UCEF-LAW-08`; `_gate_no_parallel_authority()`; `test_classification_convergence.py` fails if a second classification rule appears |

### 3.4 The proposed model, evaluated

The directive's model:

```
Existing Authorities
  Identity · Context · Knowledge · Security · Lifecycle  (and Relationship, Trust, Authority, Validation, Evolution)
        ↓  selected by reference, owned by their owners
Assimilation Composition Layer     ← select-units · AUTHORITY = NONE · owns nothing
        ↓  adds exactly: selection + ordering + gating + configuration
Single User Experience: ASSIMILATE
```

**Determination: constitutional, on elements 1–7, provided element 4 holds — and element 4 is where the present implementation fails (§9.4).**

**Disposition: REUSE.** The concerns are owned (`LXXVII.2(a)` — *"C is already owned — the owner governs"*). The composition role is owned by CEU. Registering an instance of an owned role through the ordinary registration path is not the admission of a new concept — which is exactly how `commerce`, `retail`, `marketplace` and `amazon` were admitted, none of which required an allocation.

**It is not EXTEND**, because no owner's scope is being widened. **It is not CREATE**, because nothing new is authored. **It is not HOLD**, because the totality rule applies cleanly. **It requires no authority decision**, because no authority is conferred — `LXXXII.7`: *"No entry… confers, alters, limits, or conditions the authority of the named owner. Each entry IS a recognition."*

---

## 4 — AUTHORITY DEPENDENCY MAP

```
                        UCKP-LAW-0001  ── SUPREME, EXACTLY_ONE ── engine/uckp/law.py
                               │
      ┌────────────────┬───────┼────────────────┬─────────────────┬──────────────┐
   ART-02          ART-05   ART-07          ART-14           ART-15         ART-16
   object model    identity relationship    evolution        intelligence   decision
   (CAA-INV-07)  (CAA-INV-04)(CAA-INV-05)   15 stages        13 reasoners   governance
      │                │        │                │                │             │
   UCKO           2 planes   graph model     CEP-009          UAIE-000001   CEP-002 Art.28
                  + id-ledger                 + UAUE           (measure)     + UCDA-000001
                       │
   UCOS-CEU-001 ── existence representation · relationship & topology INSTANCES
        │           ├── registers `composition` classification  ── faculty: select-units
        │           └── registers `nucleus` classification       ── faculty: own-capability
        │
        ▼
   ╔══════════════════════════════════════════════════════════════════════════╗
   ║  ASSIMILATION COMPOSITION   role: COMPOSITION   AUTHORITY = NONE          ║
   ║  holds: select-units          owns: NOTHING     NUC-INV-02 = 0 (blocking) ║
   ║  selects: identity · context · relationship · knowledge · security ·      ║
   ║           trust · authority · lifecycle · validation · evolution          ║
   ║  adds: selection + ordering + gating + configuration — and nothing else   ║
   ╚══════════════════════════════════════════════════════════════════════════╝
        │  bound by XVIII.1 delegation-as-recognition; LXXXII.7 confers nothing
        ▼
   ASSIMILATE   ← one user action, many owners, no new authority

   T1 — Constitutional Authority ......... VACANT (VAC-01, CMG-OQ-02)
        └── NOT on this path: a composition allocates no concern
   T1M — CMG-000001 ...................... may run the procedure; may not govern substance
   T2 — CEP-000…010 ...................... process only, single-subject each
   T3 — Domain Authority ................. where an owner sits
   T5 — Derived Truth .................... where the composition's measurement sits
```

### 4.1 The delegation mechanism

`CMG-000001` Article XVIII is the constitutional licence for invoking many authorities without becoming one:

- **XVIII.1** — *"Delegation under this instrument IS recognition, not transfer. This instrument holds no substantive authority and therefore has none to transfer. Every entry of Article LXXXII SHALL be read as 'this concern is already owned by X, and this instrument binds to X'."*
- **XVIII.2** — a record carries **exactly** identifier, concern, owner, **basis** (*the owner's own clause that establishes its ownership*), disposition (**EXTEND or REUSE**), revocation condition. *"A record missing any element IS void."*
- **XVIII.5** — *"Revocation withdraws the binding, not the ownership."*
- **XVIII.6** — delegation to an **unlocated** owner IS void and becomes a vacancy under `XVII.4` — dangling references become visible rather than inert.
- **XVIII.7** — *"Delegation SHALL be **total over the residue**. Every concern this instrument identifies SHALL be either delegated or retained; a concern that is neither IS a gap under `CMG-INV-03` and **blocks certification** under Article LXXX."*

Article LXXXII is the working register: **50 delegations `CMG-DLG-01…50`** plus **11 retained `CMG-RET-01…11`**, columns `ID | Concern | Located owner (existing, reused by reference) | Disposition | Basis`, every shipped disposition `REUSE`. **LXXXII.7** — *"No entry in LXXXII.2 confers, alters, limits, or conditions the authority of the named owner. Each entry IS a recognition."*

**`XVIII.7` is the one clause that constrains the composition sharply: if ASSIMILATE names a concern that is neither delegated nor retained, that is a `CMG-INV-03` gap and it blocks certification.** Concerns 5 (Security) and 6 (Trust) are presently in that position.

---

## 5 — T1 VACANCY IMPACT ANALYSIS

### 5.1 The vacancy, as recorded

Verified in `00-CMG/CMG-REGISTRY.json`:

```
tiers[T1] : { "name": "Constitutional Authority", "subordinate_to": ["T0"],
              "occupancy": "VACANT", "vacancy": "VAC-01" }

vacancies[VAC-01]:
  located                 : false
  evidence                : "The referent exists in the repository only as frozen
                             non-normative source material under 00-SOURCE/CONSTITUTIONS/
                             (.docx). No ratified normative artifact occupies the tier."
  closure_procedure       : "XVII.4: (a) record the vacancy; (b) record the determinations
                             rendered provisional; (c) refer identification of the occupying
                             authority to explicit ratification; (d) re-run authority
                             resolution on closure."
  open_question           : CMG-OQ-02
  provisional_consequence : "Every determination depending on T1 — including the standing
                             of CMG-000001 itself — is PROVISIONAL under CMG-L-12."
```

`XVII.4` — the procedure *"SHALL NOT skip the tier and SHALL NOT promote a lower instrument into it."* `LXXX.4` caps every certification at **READY-PROVISIONAL** at most while `CMG-OQ-01` and `CMG-OQ-02` remain open.

### 5.2 What depends on T1 — and what does not

**T1 allocates a new substantive concern to an owner. That is its function, and it is the only reason a composition would ever need it.**

| Decision | T1-dependent? | Why |
|---|---|---|
| Registering the assimilation composition | **No** | Owns no concern; allocates nothing; role is **derived** by `derive_role()`, not conferred |
| Selecting the ten concerns by reference | **No** | `LXXVII.2(a)` REUSE — each is already owned |
| Recording delegations per `XVIII.2` | **No** | *"Delegation IS recognition, not transfer"*; `LXXXII.7` confers nothing |
| Ordering, gating, configuring | **No** | `B.4.1` — the ordering *is* the composition |
| Aggregating a verdict from owners' verdicts | **No** | Pure conjunction; `uccep_engine.py` does this today with `AUTHORITY = NONE` |
| Recording the security row (concern 5) | **No** | `LXXVII.2(b)` EXTEND against a declared owner |
| Registering an admission faculty | **No** | CEU data; `closed_set: False` |
| Recognizing `UCOS-RTAG-000001` | **No** | EXTEND in `CEP-001` LAW-4's lane |
| **A Universal Assimilation Authority** | **Yes — and independently refused** | Would allocate a new concern **and** breach `NL-05`/`CMG-INV-02` |
| **Trust decision at admission (concern 6)** | **Yes** | Substantive, unowned, and the declared owner may not enact |
| **The `resolve_entry_point` trust boundary owner** | **Yes** | Same |
| **The unregistered surface's authority standing** | **Yes** | Recognition of an authority-claiming instrument |

### 5.3 Determination

**The vacancy blocks four decisions. It blocks none of the eleven that constitute the composition.**

This is the material finding of this determination, and it changes the outlook the prior determination left. Both located precedents confirm the reading: Ω-E03 and Ω-E04 each faced the same vacancy and each **proceeded** — declaring `Classification: SUBSTANTIVE`, claiming **no namespace token** in `CMG-REGISTRY.json`, consuming **no corpus identity**, and landing as a measurement with `AUTHORITY = NONE` in operational memory. Neither allocated ownership. Neither needed T1.

**A composition needs no allocation, therefore it needs no allocator, therefore the vacancy is not a blocker for it.** What must remain **HELD** is precisely and only what would allocate or decide a concern (§13).

---

## 6 — TRUST BOUNDARY DETERMINATION

### 6.1 The current state, in three parts

| Aspect | Owner | Standing |
|---|---|---|
| Security **domain** | `PHASE-008 SECURITY` | *"the only new ownership"* — but *"Security enacts nothing at the architecture layer"* (`USA-6`); *"mints no new primitive, authority, registry, identifier scheme, or lifecycle"* (`USA-7`/`USL-010`) |
| Trust **mechanism** | `platform/foundation/trust.py` | Cryptographic only — HMAC, delegation chains, revocation, notary. `require_trusted` at `:539`, **six call sites**: five in-module guards (`delegate`, `rotate`, `notarize`, `revoke`) + one external (`admission.py:398`, authority migration) |
| Trust **representation** | `UCOS-CEU-001` | `trust` is a registered form of existence (`TRST`, classes `governance`+`evidence`) |
| Trust **decision at admission** | **NO OWNER** | No trust faculty; the declared owner may not enact; the composition mechanism is frozen at `PL-F2` **and is a test-only orphan with 0 production importers** |
| Security in the ownership matrix | **NO ROW** | Verified: `grep -ci security` → **0** |

### 6.2 Is the trust decision an extension, a governance decision, or held?

Applying `LXXVII.2` to two distinct subjects:

**(a) Recording security as a concept → EXTEND.** An owner is declared in `SECURITY-GOV-000`; the matrix does not record it. This is `LXXVII.2(b)` — within an existing owner's scope but unaddressed. The precedent is exact: Ω-E03 found *"`02-CANONICAL-OWNERSHIP-MATRIX.md` contained **zero occurrences of the word identity** — seven authorities, no rows"* and dispositioned it EXTEND as a measurement over located owners. **Not T1-dependent. Available now.**

**(b) The trust decision at the point of admission → RECORD AS GAP, then HELD.** Substantive and unowned, so `LXXVII.2(d)` routes it *"to the authority competent to allocate"* — which is T1, vacant. And it is unowned for a structural reason, not an accidental one: **the only declared owner is constitutionally barred from deciding it.** `SECURITY-001` §1 — security *"describes, classifies, evaluates, and attests… it never executes… and enforces only by reference to lower-layer mechanisms already frozen and certified."*

### 6.3 What the composition may lawfully do about trust, now

**A composition may select a trust mechanism. It may not decide trust.** Selecting is `select-units`; deciding would be authoring a capability no nucleus owns, which `NL-03` and `NL-07` forbid.

Three placements already have a structural precedent in Repository Truth, so the *model* is not missing:

| Placement | Located precedent |
|---|---|
| **Pre-admission** | `engine/constitution/assimilation.py::require_creatable()` — four searches must all return empty **before** creation is permitted |
| **At admission** | `engine/ceu/existence.py::relate(authority=…)` — a **non-optional** authority argument |
| **Pre-promotion** | `evidence-universe.json` `R-EV-4` — `DEBUG`/`IMPROVEMENT` may never influence certification **anywhere**, enforced at `generated_artifacts.py::_check_evidence_input` |

**Determination: the trust model is located; the authority to bind it to the admission path is not. Disposition RECORD AS GAP, HELD pending T1. The composition may select `platform/foundation/trust.py` by reference today; it may not supply a trust decision, and it may not proceed as though one existed.**

Per `B.4.3`, if the composition names trust as a member with no located owner, the composition is **void as to that member**, and the absence *"SHALL be recorded as a gap… rather than remedied by authoring"* it. That is the operative constraint, and it is honest: **the assimilation composition would be lawfully incomplete rather than unlawfully complete.**

---

## 7 — INTELLIGENCE CONTRIBUTION BOUNDARY

### 7.1 The boundary, located

```
new existence
     │
     ▼
CEU EXISTENCE REGISTRATION ......... engine/ceu/existence.py  ·  register() / relate(authority=…)
  owner: UCOS-CEU-001 (registered instrument, role PROJECTION, ART-02/07/18)
  owns:  existence representation · registration · supersession · resurrection ·
         declaring new forms · relationship and topology INSTANCES
  may_never_own: what a relationship IS · the object model · identity allocation ·
         context resolution · lifecycle stages
     │
     ▼  ◄── THE BOUNDARY. Below this line CEU's authority ends and ART-15's begins.
     │
KNOWLEDGE CONTRIBUTION ............. engine/knowledge/ukip/  ·  canonical-home registry
  owner: RA-003 + CEP-001 LAW-4
     │
     ▼
REASONING SURFACES ................. engine/uckp/intelligence.py  ·  13 reasoners
  owner: UCKP-ART-15.  Each reasoner is itself a UCKO.
     │
     ▼
EVOLUTION .......................... engine/uckp/evolution.py  ·  15 stages, non-terminal
  owner: CEP-009 (concern) + UCKP-ART-14 (stages).  Measured by UAUE (AUTHORITY = NONE).
```

### 7.2 Determination

**The boundary is: CEU owns that a thing exists and what it is related to. `UCKP-ART-15` owns what may be inferred from it. `UCKP-ART-14` owns what happens next. Each is a registered, non-competing authority, and the seam between them is `engine/uckp/registry.py` — the population reasoners read.**

`existence_resolution` declares **four non-competing existence authorities**: `UCKP-COMPLETENESS-REGISTRY` (193 objects), `UGA-EXISTENCE-REGISTRY` (5,789), `CEU-EXISTENCE-SUBSTRATE` (154 units / 51 forms), `REPOSITORY-INTELLIGENCE`. Plurality here is lawful because each is bounded; the declared test is *"a rival = a second authority over the SAME bounded question"*, and none is found.

**No new intelligence authority is required, and none is available.** The matrix's architectural-intelligence row declares *"no new owner"* and composes seven surfaces with *measured binding only* at `UAIE-000001` (`AUTHORITY = NONE`) — which is itself the composition pattern applied to intelligence.

### 7.3 The missing relationship

**Not an ownership gap. A single missing edge.** The composition must terminate at CEU registration with a named authority. `relate()` requires a non-optional `authority`; the fabric produces an `AssimilationRecord` that names none. The fabric's defect and its remedy are one fact: **it does not use the door that asks the question it never answers.**

Two further consequences, both `CAA`-measured:

- `CAA-INV-05` checks **emitted** relationship kinds against declared classes **in both directions** — failing on an emitted kind bound to nothing *and* on a declared kind emitted by nothing. If the composition begins emitting edges, it emits into a measured surface. (Note `ISD-G-04`: 12,899 edges are materialized today and **no gate validates them** against `relationship.schema.json`.)
- `CAA-INV-04` measures the **declared** identity population only. The fabric's `UCOS-USA*-<16hex>` ids match neither declared plane shape (`^UCOS-[A-Z0-9]+-[0-9]{6}$`), so they are unbound rather than rival. **Applying `CAA-INV-05`'s both-directions discipline to identity would catch this**, and the mechanism sits one section away in the same file.

---

## 8 — SINGLE-CLICK ASSIMILATION MODEL

### 8.1 It already exists

**`ucos-foundation determine` is a working single action over four owners**, published in `pyproject.toml [project.scripts]` and annotated `AUTHORITY = NONE (DERIVED TRUTH); writes nothing`.

`UniversalFoundation.determine(subjects=…, locators=…, sources=…, destinations=…)` calls `classify` (truth) → `determine_ownership` → `assimilate` → builds one `MeasurementContext` → `measure` (the policy suite including `assimilation.coverage` at precedence 600, blocking) → returns a content-addressed `FoundationDetermination` whose headline verdict is `CLOSED`/`NOT-CLOSED` **derived purely from `suite.closed`**, with `blockers()` naming the withholding policies. Every input is optional; unmeasured inputs are reported as not measured. *"It never substitutes an empty population for a missing one."* CLI is fail-closed: 0 ok, 1 with `--gate` when NOT-CLOSED, 2 on fault.

**The single click is not a thing to be invented. It is a thing to be extended from four owners to ten.**

### 8.2 The five mechanisms, all located

| Mechanism | Located implementation | Property that keeps it from becoming an authority |
|---|---|---|
| **Orchestration** | `engine/uaue/controller.py` — eleven **ordinal** positions `(_ADMIT … _TRANSITION) = range(1,12)`; each a thin delegation; policies derived from the authority, never declared | *"**It conducts; it does not decide.** … A controller that re-measured anything would be a second opinion on a subject that already has an owner."* It claims no twelfth position: *"a twelfth would be this module legislating itself into the cycle it conducts."* An owner's refusal is recorded **against the position that called it** |
| **Delegation** | `CMG-000001` XVIII + LXXXII — 50 records, `basis` = *the owner's own clause* | `XVIII.1` recognition-not-transfer; `LXXXII.7` confers nothing; `XVIII.6` a delegation to an unlocated owner is **void**, becoming a visible vacancy |
| **Evidence aggregation** | `engine/certification/` — `status = NOT_CERTIFIED if blocking else CERTIFIED`, a pure conjunction over a **projection** of the owner's report (`CertificationSubject.from_validation` copies verdict, accepted, check ids, blocking failures, counts, evidence hash and **adds nothing**) | *"every criterion **aggregates the validation verdict** (it re-judges no artifact — TP-01)"*. Fails closed when evidence is absent. Content-addressed and clock-free |
| **Validation aggregation** | `uccep_engine.py::aggregate()` over 48 owner-owned checks into 26 gates; tiers boot/standard/full | *"This engine legislates nothing, registers nothing, and owns nothing. It is the **aggregation** of gates that already exist and are already owned."* Absence of evidence is never evidence; out-of-tier blocking checks are disclosed as a **certification ceiling**, never dropped. `emission_authority()` separates observation from emission — `--tier boot` leaves the tree byte-identical |
| **Lifecycle routing** | `engine/nucleus/lifecycle.py` — 45 stages as DATA, ordering **derived** by the single ordering authority, hash-chained `StageOutcome`, `replay()` fixed point | The engine **resolves no owner**: `Stage` carries only id/name/ordinal/group/depends_on. Owner lives in `ucl-stage-manifest.json`; the caller's `StageFunction` is the dispatch seam. `verify_manifest_alignment()` diffs both directions, so the module is a **verified projection**, not a second stage list. `StageStatus` has no UNKNOWN — *"silence is not a status"* |

### 8.3 The model

```
USER: ASSIMILATE
   │
   ▼
COMPOSITION (AUTHORITY = NONE · role COMPOSITION · holds select-units · owns nothing)
   │
   ├── reads a DECLARATION (data): which units, in what order, with what gating
   │      precedent: uccep-bindings.json · ucl-stage-manifest.json ·
   │                 ucos-measurement-policies.json · repo-operations.json
   │
   ├── for each declared position, DELEGATES to the owner named in the declaration
   │      per XVIII.2: identifier · concern · owner · basis · disposition · revocation
   │      the composition invokes; the owner decides
   │
   ├── AGGREGATES the owners' own verdicts by pure conjunction
   │      absence of evidence = failure · out-of-scope = disclosed ceiling
   │
   ├── ROUTES through the lifecycle by supplying a StageFunction
   │      the lifecycle never learns who the owners are
   │
   └── EMITS a content-addressed determination, not a ruling
          AUTHORITY = NONE · CLOSED / NOT-CLOSED · blockers named
   │
   ▼
Nothing is owned. Nothing is conferred. Nothing is authored.
```

### 8.4 The five self-protections the precedents ship

Each precedent carries these, and a successor inherits them:

1. **The invoked set is declared as data, never enumerated in the orchestrator.** `ALLOWED_KEYS` fails closed on any undeclared field, so no new field can smuggle a finite world into the declaration.
2. **Verdict is a conjunction over owners' verdicts.** `PolicyMeasurementEngine.measure()` **skips** a policy whose required determination is absent — *"a measurement that was not made is never a pass"* — while `measure_strict()` fails closed.
3. **Observation is separated from emission.** UCCEP tiers; `mutation_performed` carried *beside* `execution_authorized`, and a recorded mutation **refuses the run**.
4. **Self-inclusion is kept out of the graph.** `G-15` deliberately does not bind the fixed-point condition, *"because the fixed point engine runs this engine as a pipeline stage, so binding it here made this engine's emitted verdict depend on whether it had been invoked nested."* The gate graph stays a DAG.
5. **The composition's own role is derived, not declared.** `derive_role()` means the label cannot be self-asserted, and `test_classification_convergence.py` fails if a second classification rule appears.

---

## 9 — CONSTITUTIONAL COMPLIANCE ANALYSIS

### 9.1 Against the directive's preservation requirements

| Requirement | Satisfied? | Mechanism |
|---|---|---|
| Existing authority ownership preserved | **Yes** | Ten concerns REUSE to their owners; `LXXXII.7` — *"No entry… confers, alters, limits, or conditions the authority of the named owner"* |
| Constitutional injectivity (`CMG-INV-02`) | **Yes** | A composition owns no concern, so it appears as no concern's owner. `NUC-INV-02` = 0, blocking |
| No duplicate authority | **Yes** | No authority created. `B.9.9` records the same reasoning: `CMG-INV-02` holds *"because no authority is created"* |
| No ownership absorption | **Yes** | `NL-03` — a composition *"SHALL NOT own a capability and SHALL NOT introduce capability logic of its own"*, with a refusal path at admission |
| No unauthorized consolidation | **Yes** | Compositions **select**, never merge. Ω-E03/Ω-E04: *"CROSSWALKED, never merged, because a merge would amend every owner at once"* |
| No new Universal Assimilation Authority | **Yes** | Refused twice over: `NL-05` (a subject that selects cannot be registered as an owner) and `CMG-INV-02` |

### 9.2 Against the twelve `CMG` invariants

| Invariant | State |
|---|---|
| `CMG-INV-01` recognition totality | **At risk** — `platform/universal_assimilation` and `UCOS-RTAG-000001` exercise force and are recognized nowhere (§9.4, §9.5) |
| `CMG-INV-02` zero parallel authority | **Satisfied** — no authority created |
| `CMG-INV-03` zero orphan governance | **At risk** — concerns 5 and 6 are neither delegated nor retained; `XVIII.7` makes that a gap that **blocks certification** under Art. LXXX |
| `CMG-INV-04…08` | Unaffected by a composition |
| `CMG-INV-09` no finite ceiling | **Satisfied** — `SEED_COMPOSITIONS` is data; *"the ten-thousandth nucleus costs one tuple entry"* |
| `CMG-INV-10` evidence reproducibility | Requires the composition be recomputable and clock-free — the precedents all are |
| `CMG-INV-11` preservation | Unaffected |
| `CMG-INV-12` jurisdiction containment | **Satisfied** — this determination decides no substantive matter |

### 9.3 `CMG-L-14` — No Parallel Machinery

> *"This instrument SHALL NOT create a second registry, lifecycle, traceability store, evidence store, validation engine, certification engine, ratification mechanism, or governance body where one exists."*

A composition creates none of the eight by definition. The precedents each state the negative explicitly — *"no second registry, no second identity scheme and no second source of truth"* (`MetaCivilizationPlatform`), *"never a second execution controller"* (`ConstitutionalPipeline`), *"no second telemetry stack"* (`platform/security/observability.py`).

### 9.4 Where the present implementation exceeds what a composition may do

**This is the sharpest finding in this determination, and it is a finding against the surface the directive is trying to legitimize.**

Element 4 of the seven-element test requires that a composition add **exactly one named thing**. `platform/universal_assimilation/` adds more than selection, ordering, gating and configuration:

| What it adds | Constitutional character |
|---|---|
| **Seven adapters** that transform bytes into text or records (`TextAdapter`, `JsonAdapter`, `ConversationExportAdapter`, `DocxAdapter`, `PdfAdapter`, `RecordSetAdapter`, `CallableAdapter`) | Content transformation is **capability logic**. No located nucleus owns it. Under `NL-03` — *"SHALL NOT introduce capability logic of its own"* — this is **authorship** |
| **Its own identity namespace** `UCOS-USAS/USAU/USAR/USAP-<16hex>` | A composition may not mint. These match neither declared identity plane |
| **Its own closed reason vocabulary** `ASSIMILATION_REASONS` (6 structural reasons) | A verdict vocabulary of its own; `NL-07` would make it a *configuration* of an owner's vocabulary, not its own |
| **Its own state machine** `AssimilationState` (6 states) | A seventh lifecycle vocabulary; `CMG-L-14` forbids a second lifecycle where one exists |

**Determination: as built, the surface is not a lawful composition. It is a composition-shaped package that also authors four things.** Two lawful resolutions exist, both without CREATE:

1. **Locate an owner for each authored element** — a nucleus that owns content normalization, an identity plane binding, a reason vocabulary owner, a lifecycle owner. Where an owner is located, the element becomes a **selection**.
2. **Where no owner is located, `B.4.3` governs:** the composition is **void as to that element**, and the absence *"SHALL be recorded as a gap… rather than remedied by authoring"* it.

**The honest outcome is a lawfully incomplete composition, not an unlawfully complete one.**

### 9.5 The recognition defect

`UCOS-RTAG-000001` (`engine/constitution/assimilation.py`) is the corpus's real anti-duplication admission gate — four searches as extensible DATA, `require_creatable()` raising `DuplicateTruth`, naming the harm it prevents as *"a second truth"* — and it appears in **no authority register, no Makefile target and no `uccep-bindings.json` entry.**

`CMG-000001` **XII.5**: an artifact satisfying the conditions of a constitution but unregistered *"SHALL NOT be cited as constitutional authority, SHALL be recorded as a finding… **Latency IS a detectable defect, not a status.**"* `CMG-L-01`: *"An unrecognized artifact SHALL NOT be cited as constitutional authority."*

**Determination: the docstring claim of `platform/universal_assimilation` to be "one road for every source" is a citation of authority it does not hold. Disposition: RECORD AS GAP for the surface; EXTEND for RTAG's recognition in `CEP-001` LAW-4's lane.**

---

## 10 — DECISIONS REQUIRING FUTURE AUTHORITY ALLOCATION

**Four. Each would allocate or decide a concern; each routes to T1; T1 is vacant.**

| ID | Decision | Why it requires allocation | Route |
|---|---|---|---|
| **T1-D1** | A Universal Assimilation Authority as a single owner | Would allocate a new substantive concern **and** take six concerns from six owners | **MOOT** — independently refused by `NL-05` and `CMG-INV-02`. Recorded so it is not revisited |
| **T1-D2** | Ownership of the trust decision at admission | Substantive, unowned; the only declared owner may not enact (`USA-6`) | `LXXVII.2(d)` → competent allocator → T1 (`VAC-01`) |
| **T1-D3** | Ownership of the `resolve_entry_point` trust boundary | Same. One function, unguarded: `importlib.import_module` on a JSON-supplied module name with no allowlist, signature or trust check | Same |
| **T1-D4** | Authority standing of `platform/universal_assimilation` if it is to claim any | Recognition of an authority-claiming instrument (`IV.1(f)`, `XII.4`) | `CMG-000001` Art. XV / XII; blocked while its Kind is ambiguous (`XIII.4`) |

### 10.1 Not requiring allocation

For clarity, since the prior determination placed some of these on the critical path: registering the composition · selecting the ten concerns · recording delegations · ordering/gating/configuring · aggregating verdicts · recording the security row · registering an admission faculty · recognizing RTAG · binding emitted identities to a declared plane · terminating at CEU with an authority. **Ten items. None is T1-dependent.**

### 10.2 The vacancy's own closure procedure

`VAC-01` states it: (a) record the vacancy; (b) record the determinations rendered provisional; (c) refer identification of the occupying authority to explicit ratification; (d) re-run authority resolution on closure. **This determination performs (a) and (b) and refers (c). It does not perform (d) and does not resolve the vacancy.**

### 10.3 Why T1-D2 and T1-D3 cannot be routed elsewhere

`LXXVII.4` — *"An unknown concept SHALL NOT be admitted by **default routing** to the nearest owner, the most active program, or the meta layer. Default routing manufactures parallel authority; explicit disposition prevents it."* `XVII.4` — no skipping, no promotion. `LXXXI.2` and `CMG-INV-12` — `CMG` decides no substantive matter; `XIX.5` — *"Declining IS the correct constitutional act; answering would create parallel authority."*

### 10.4 Revision to the prior determination's outlook

`…UNIVERSAL-ASSIMILATION-AUTHORITY-OWNERSHIP-DETERMINATION.md` concluded that assimilation ownership *"cannot be allocated at this baseline"* and left the composition question open. **That conclusion stands and is now shown to be non-blocking.** The prior determination did not locate `select-units` as a registered faculty distinct from `own-capability`, nor `derive_role()` as the mechanism that makes composition a derivation. With those located: **the path forward never required allocation, because a composition owns nothing.** The prior determination's §12.3 prerequisite *"which of four identity forms is canonical"* is likewise narrowed — `CAA-INV-04` already settled the authority; only the binding of emitted forms remains, and that is not an allocation.

---

## 11 — REUSABLE CAPABILITIES

Every element a single-click ASSIMILATE requires, and the located surface that already carries it. **Nothing here requires a new engine.**

| Need | Reuse | Standing |
|---|---|---|
| What a composition IS | `engine/nucleus/law.py` `SUPREMACY_CLAUSE`, `NL-03/05/07/08` | Enforced at admission |
| Composition role derivation | `engine/nucleus/model.py::derive_role()` | Total, no default, refuses hybrids |
| `select-units` faculty | `engine/ceu/catalog.py` → `engine/nucleus/authority.py::may_select_units()` | Registered data, `closed_set: False` |
| Composition realisation | `engine/nucleus/registry.py::compose()` — returns `owns_capabilities: False` | *"has no way to let it"* |
| Composition invariants | `NUC-INV-02/05/06/07/08` | All blocking |
| Delegation-as-recognition | `CMG-000001` XVIII + LXXXII (50 records) | Normative |
| Orchestration without ownership | `engine/uaue/controller.py` | *"It conducts; it does not decide"* |
| Evidence aggregation | `engine/certification/` — conjunction over a projection | *"re-judges no artifact (TP-01)"* |
| Validation aggregation | `uccep_engine.py::aggregate()` + `uccep-bindings.json` | *"owns nothing"* |
| Observation/emission separation | `uccep_engine.py::emission_authority()` | The reference implementation |
| Measurement precedence | `platform/universal_measurement/` — `order_key = (-precedence, policy_id)`; blocking is **data** | Declared ladder |
| Lifecycle routing | `engine/nucleus/lifecycle.py` — 45 stages, `StageFunction` seam, hash chain, `replay()` | Gated `G-25` |
| Existence admission requiring authority | `engine/ceu/existence.py::relate(authority=…)` | `UCOS-CEU-001` |
| Duplication refusal before creation | `UCOS-RTAG-000001` — four searches as DATA, `closed_set: False` | Code, unregistered |
| Reuse evidence | `ReuseEngine.assess()` — deterministic, wired three ways | Discharges `LXXVI.2(a)` only |
| Ownership admissibility | `platform/universal_ownership/contracts.py` — `OWN-REQ-001…007`, three hard raises | Wired |
| Identity + derivation | `UCKP-ART-05`, two planes, `repository_local_urn` (total, pure, injective) | `CAA-INV-04` |
| Both-directions emitted-vs-declared test | `CAA-INV-05` | The pattern to copy for identity |
| Lineage as zero-persistence projection | `engine/lineage/` | 12,899 edges, 2 read-only `open()` calls |
| Existing single user action | `ucos-foundation determine` → `FoundationDetermination` | Published, fail-closed |
| Single-entry-point pattern | `verify.sh` (15 `run_stage`, Art. LXVI.7) · `make repo-ops` (5 stages) | `CMG-DLG-40` |
| Operational-memory landing pattern | Ω-E03 → `UIS-001`/`G-24` · Ω-E04 → `UCL-000001`/`G-25` | Executed twice |

---

## 12 — DECISIONS THAT CAN PROCEED

**Eleven, none requiring an allocation.** Recorded as available dispositions, **not** as authorized work.

| # | Decision | Disposition | Basis |
|---|---|---|---|
| 1 | Recognize Universal Assimilation as a **Composition**, not an authority | **REUSE** | `derive_role()`; `NL-03`; `SEED_COMPOSITIONS` precedent |
| 2–9 | Select the eight owned concerns by reference (Identity, Context, Relationship, Knowledge, Authority, Lifecycle, Validation, Evolution) | **REUSE** ×8 | `LXXVII.2(a)`; `XVIII.1`; `LXXXII.7` |
| 10 | Record delegations per `XVIII.2` (identifier · concern · owner · **basis** · disposition · revocation) | **REUSE** | `XVIII.1` recognition-not-transfer |
| 11 | Record the security row in the ownership matrix | **EXTEND** | `LXXVII.2(b)`; Ω-E03 precedent |

Additionally available as EXTENDs against located owners, all non-T1-dependent: recognize `UCOS-RTAG-000001` in `CEP-001` LAW-4's lane · register an admission faculty in CEU data · bind emitted identity forms to a declared plane via `repository_local_urn` · extend the `CAA-INV-05` both-directions test to identity · extend `RecordSetAdapter`'s declared-schema seam for non-document kinds.

**Constraint on all eleven:** `XVIII.7` — *"Delegation SHALL be total over the residue."* A composition naming Trust as a member while Trust has no owner produces a `CMG-INV-03` gap that **blocks certification** under Art. LXXX. Proceeding therefore means proceeding to a **lawfully incomplete** composition that discloses its incompleteness — which is what `B.4.3` requires and what both located precedents did (Ω-E03 referred six disclosures; Ω-E04 referred four).

---

## 13 — HELD DECISIONS

Held under `LXXVII.5` — *"Holding IS a valid disposition; silent adoption IS not."*

| ID | Held decision | Held because | Release condition |
|---|---|---|---|
| **H-1** | Ownership of the trust decision at admission | `LXXVII.2(d)`; competent allocator vacant; declared owner may not enact | T1 occupancy (`CMG-OQ-02`) **or** an authority competent to enact security |
| **H-2** | Ownership of the `resolve_entry_point` trust boundary | Same | Same |
| **H-3** | Authority standing of `platform/universal_assimilation` | Kind ambiguous under `XIII.4`; would require recognition | Its Kind resolved; the four authored elements dispositioned (§9.4) |
| **H-4** | Whether the seven adapters are selection or authorship | No located owner for content normalization | An owner located, **or** the element declared void per `B.4.3` |
| **H-5** | Which assimilation surface is canonical (framework vs `UAKOS-CLOSURE-008`) | Two surfaces answering one question; `CMG-L-02` resolves overlap under Art. LIV **before either advances** | Art. LIV resolution by the owner of row 1 |
| **H-6** | Persistence of `EvolutionLedger` (`F-3`) | `classify_object` is **total** with an unconditional terminal branch — admitting a mutation class reclassifies every object | `GOVERNED_EVOLUTION_STATE` disposition |
| **H-7** | Gate mode for any new gate | Specified and explicitly unauthorized | `H-06` / `CR-09` |
| **H-8** | Cross-class evolution transaction | Verdict C; `AT-1` — no declared authority owns a cross-class boundary | `AT-1` |
| **H-9** | Six USIS Infinite Intelligence registries (`REG-005/006/008/009/011/012`) | 36 documents, 0 code; programme scope | USIS programme owner |
| **H-10** | The `T1` vacancy itself (`VAC-01`) | `XVII.4` — no skipping, no promotion | Explicit ratification per `VAC-01(c)` |

**No held decision is resolved here. No vacancy is filled. No authority is assumed.**

---

## 14 — FINAL DETERMINATION

**The lawful resolution path is composition, and it was already legislated before the question was asked.**

`select-units` is a **registered faculty**, disjoint from `own-capability`. The `composition` role is **registered CEU data** carrying the description *"A selection of nuclei plus configuration. Owns nothing."* Role assignment is **derived from content** by `derive_role()`, so it cannot be self-asserted, and a subject that selects **cannot** be registered as an owner. Five blocking invariants measure the disclaimer. Six precedents implement it. The constitution states it in one line: *"A Composition selects Nuclei and owns nothing."*

Consequently:

- **Universal Assimilation is a Composition** — by derivation, as Commerce is, and for the same reason.
- **No new authority is required, requested or available.** A composition owns nothing, so there is nothing to allocate.
- **The T1 vacancy does not block it.** T1 allocates concerns; a composition allocates none. The vacancy blocks four decisions, and three of those four are about **trust**, not about composition.
- **The single click already exists** as `ucos-foundation determine`, over four owners; the work is extension to ten, not invention.
- **The composition would be lawfully incomplete**, because Trust has no owner and four elements of the present implementation are authored rather than selected. `B.4.3` requires that incompleteness be **recorded as a gap rather than remedied by authoring** — and that is the correct outcome, not a failure of it.

The finding that most changes the picture is the one against the surface in question: **`platform/universal_assimilation` as built is not a lawful composition.** It adds seven content-transforming adapters, its own identity namespace, its own reason vocabulary and its own state machine — four things a composition may not author. Making it lawful means locating an owner for each, or declaring the composition void as to each. Neither requires a new engine, and neither requires T1.

**Zero ownership assigned. Zero authority created. Zero identifiers. Zero requirements. Zero ADRs. Zero registry modifications. Zero certification changes. Zero vacancy resolved. Zero CREATE.**

---

## 15 — STOP

**DETERMINATION COMPLETE. NOTHING AUTHORIZED.**

This artifact is `DECLARATIVE` (`XII.6`), asserts no constitutional force, is not registered in `CMG-REGISTRY.json`, and **SHALL NOT be cited as constitutional authority** (`CMG-L-01`). Its standing is **PROVISIONAL** under `CMG-L-12` for the reason recorded at `VAC-01`.

Four decisions are routed to a vacant tier (§10). Ten held decisions are recorded (§13). Eleven dispositions are identified as available and **none is authorized** (§12).

Awaiting explicit authorization.
