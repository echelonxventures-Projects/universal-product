# UCOS Ω∞ — CAAR ARCHITECTURE CORRECTION DETERMINATION

**Resolving `CIR-1`…`CIR-12` by correcting the architecture that produced them — not by scheduling twelve repairs**

| Field | Value |
|---|---|
| Artifact | `UCOS-OMEGA-INFINITY-CAAR-ARCHITECTURE-CORRECTION-DETERMINATION.md` |
| Authority | **NONE — DERIVED TRUTH.** Creates no identifier, schema, vocabulary, registry, class, owner, lifecycle or certification of record. Adopts nothing. Authorizes nothing. Every correction below requires the authority named in §16 before it may be built. |
| Mode | ANALYSIS AND DESIGN ONLY · **NO CODE CHANGE · NO REGISTRY CHANGE · NO CERTIFICATION CHANGE · NO COMMIT** |
| Baseline commit (HEAD) | `bae59755d7e2d3566c93b89c722b68847145269a` |
| Baseline branch | `integration/recovery-001` |
| Subject | `…CANONICAL-ARTIFACT-AUTHORITY-RECORD-IMPLEMENTATION-DESIGN.md` (530 lines) as gated by `…CAAR-IMPLEMENTATION-READINESS-DETERMINATION.md` (523 lines, verdict `NOT READY`, 12 blockers) |
| Predecessors | BC-6 Steps 1–6 (26 findings) · CAAR Implementation Design · CAAR Implementation Readiness Determination (`CIR-1`…`CIR-12`) |
| New sources read | `00-MASTER/UCOS-UGA-001/` (declaration, engine, 6,145-entry object registry) · `00-BOOK/DATA/constitutional-authority-alignment.json` · `00-BOOK/DATA/id-ledger.json` `by_object` / `by_observation` planes · `engine/uckp/vocabulary.py` · `engine/uckp/law.py` · `AUTH-INF-001` constitution text — **none read by any of the eight prior artifacts in this chain** |
| Root cause identified | **1** (`ACD-ROOT`) · from which **10 of 12** `CIR` blockers derive |
| CIR disposition | 8 **CORRECTED BY ARCHITECTURE** · 1 **REFRAMED** (`CIR-7`) · 1 **DOWNGRADED** (`CIR-2`) · 4 **UNCHANGED** (`CIR-6`, `CIR-8`, `CIR-9`, `CIR-10`) — a correction is not a closure; see §20 |

---

## 1. Objective, Method, and Why a Correction Rather Than a Repair List

### 1.1 Objective

The Readiness Determination graded twelve dimensions and found zero clear. Its §19 then
proposed an execution order that treats the twelve as twelve work items. This determination
tests a different hypothesis: **that most of the twelve are one defect observed twelve
times, and that scheduling twelve repairs against an uncorrected architecture would encode
the defect twelve ways instead of removing it once.**

That hypothesis is confirmed (§2). Ten of the twelve blockers follow from a single
architectural decision the Implementation Design made in its §1–§3 and never stated as a
decision.

### 1.2 Method

Reads only, at one commit. Two classes of source are opened that no prior artifact in this
chain opened:

1. **The constitutional layer the design must be lawful under.** `AUTH-INF-001`'s twelve
   rules and eight interpretive laws; `UCKP-LAW-0001`'s invariants `UCKP-INV-11`,
   `UCKP-INV-13`, `UCKP-INV-14`; `engine/uckp/vocabulary.py`'s open-vocabulary mechanism;
   and `00-BOOK/DATA/constitutional-authority-alignment.json`, which declares the identity,
   lifecycle, existence, category and namespace resolution models the whole repository is
   already bound to, plus seven fail-closed alignment invariants `CAA-INV-01…07`.

2. **The live implementation the design proposed to build from scratch.** `UCOS-UGA-001`
   (`00-MASTER/UCOS-UGA-001/`) — a running engine, gated blocking in `verify.sh` Stage 6b
   (`verify.sh:435-436`, "All ten invariants block"), emitting a **6,145-entry Universal
   Object Registry** whose per-entry record carries `universal_id`, `object_class`, `owner`,
   `producer`, `identity_authority`, `lifecycle`, `dependencies`, `produces`,
   `evidence_class`, `evidence_boundary`, `validation_contract`, `certification_status`,
   `content_hash` and `first_seen`.

Every count below is a direct read or a computed set operation at this baseline, recorded
inline. No count is carried forward from a prior artifact without being recomputed.

### 1.3 Standing limitation

`classify()` still returns `ERROR` for every subject; `R-09` is declared in
`mutation-governance-boundary.json` but unimplemented in the classifier. Nothing below is a
classification, ownership, or certification of record. This determination corrects a
design; it does not execute one.

---

## 2. Current CAAR Defects

### 2.1 `ACD-ROOT` — CAAR was designed as a new authority beside the object model, where the repository's own extension law requires an extension of it

**Severity: CRITICAL — root cause of `CIR-3`, `CIR-4`, `CIR-5`, `CIR-11`, `CIR-12`, and materially of `CIR-1`, `CIR-2`, `CIR-7`.**

`00-BOOK/DATA/constitutional-authority-alignment.json` declares an `extension_rule` binding
every future capability in this repository:

> **"Every future capability becomes an EXTENSION of the Universal Constitutional Object
> Model, never a competing authority beside it."** (`UCKP-ART-17`, `UCKP-ART-18`,
> `UCKP-ART-14`)

and states what that forbids:

> **"A second registry, engine, lifecycle, identity authority, relationship graph or
> evolution system standing beside the ones that exist. Not because expansion is untidy,
> but because `UCKP-ART-03` makes a second definition of an existing primitive void, and
> `CAA-INV-01..07` make that voidness measurable."**

The Implementation Design proposes, in four separate sections and without naming any of
them as a decision:

| Design section | What it creates | Which existing primitive it redefines |
|---|---|---|
| §2.2 | A new identity minting authority (`CAAR-<16hex>`, `sha256(class:path:commit)`) | Universal Identity — `UCKP-ART-05`, persisted in `id-ledger.json` |
| §1.1 `class` | A new six-member object taxonomy, citing no object model | `UCKO` — `UCKP-ART-02`, taxonomy facet, `uckp.governed-category` |
| §1.2 | A new per-class lifecycle vocabulary, citing no lifecycle axis owner | `UCL-000001` (process axis) / knowledge-lifecycle (state axis) |
| §3.1 | "A **seventh**, GENERATED artifact… authoritative *for lookups*" | The object registry that already answers lookups |

Four of the six items in `what_this_forbids` — a second registry, a second lifecycle, a
second identity authority, a second engine — appear in one design. This is not a criticism
of the design's craftsmanship: the design traces every decision to a numbered BC-6 finding
(its §11), and BC-6's six steps never read the constitutional layer or the live object
registry, so the design inherited a view of the repository in which none of these
primitives existed. **The defect is that the design's evidence base was bounded to six
registries the directive happened to name, and the naming was never tested against what the
repository actually runs.**

### 2.2 `ACD-1` — The identity join CAAR was built to supply already exists and was never read

**Severity: CRITICAL. Directly falsifies the premise of `CAAR-1` and `CAAR-5`, and therefore of Design §2 in its entirety.**

`CAAR-1` measured, correctly:

```
overlap(GAR.artifact_id,    artifacts.universal_id) = 0 of 345
overlap(GAR.canonical_path, artifacts.path)         = 0 of 345
```

and concluded that "the two registries the directive names first partition the repository by
directory" and that "building CAAR is a repair, not a composition." The measurement is
sound. The inference is not, because it compares two **derived** registries to each other
rather than either to the ledger that mints for both. `00-BOOK/DATA/id-ledger.json` holds
three identity maps, not one. Recomputed at this baseline:

```
id-ledger by_path         : 1,492 entries
id-ledger by_object       : 4,914 entries
id-ledger by_observation  :     7 entries

artifacts.json path  ∩ by_path    = 1,461 of 1,461   (100%)
GAR canonical_path   ∩ by_object  =   345 of   345   (100%)
GAR canonical_path   ∩ by_path    =    11
artifacts.json path  ∩ by_object  =   192

(artifacts.json ∪ GAR) covered by (by_path ∪ by_object) = 1,806 of 1,806  (100%)
```

**Every path in both registries the directive named already holds a Universal ID from one
identity authority.** The join key CAAR's §2 was designed to invent has existed throughout,
in the file BC-6 Step 6 listed in its own header table as read (`id-ledger.json`) but
inspected only for its `by_path` map. The two registries do not partition the repository by
directory in any way that matters to identity; they partition it by *which projection lists
them*, over a population that is already fully identified.

`CAAR-5`'s composability verdict — "**No.** The six registries do not compose into CAAR by
any join the repository currently declares" — is therefore false as stated. The join is
declared, in `constitutional-authority-alignment.json` `identity_authority_resolution`, and
it is populated to 100% over the union of the two candidate populations.

### 2.3 `ACD-2` — Five of CAAR's seven columns are already produced, gated, and blocking

**Severity: HIGH. Changes `CIR-2`, `CIR-5` and `CIR-9` from "no data exists" to "data exists and was not read."**

`00-MASTER/UCOS-UGA-001/02-UNIVERSAL-OBJECT-REGISTRY.json`, regenerated by
`uga_engine.py run` and verified by `uga_engine.py gate` as a **blocking** stage of
`verify.sh`, carries 6,145 entries of this shape:

```jsonc
{ "universal_id": "UCOS-CONFIG-000001", "path": ".github/workflows/acee-gate.yml",
  "object_class": "CONFIGURATION_OBJECT", "owner": ".github/workflows",
  "producer": "HUMAN_AUTHORED", "identity_authority": "UCOS-UGA-001",
  "lifecycle": "AUTHORED", "dependencies": [], "produces": [],
  "evidence_class": "VALIDATION", "evidence_boundary": "NON_CANONICAL",
  "validation_contract": "UCOS-UGA-001 §UGA-INV-01..10",
  "certification_status": "GOVERNED", "content_hash": "e6e97ec4…",
  "first_seen": "commit:e98f59cd22e9" }
```

Measured field cardinality across all 6,145 entries at this baseline:

| CAAR column (Step 6 §2.1) | UGA field | Distinct values | Assessment |
|---|---|---|---|
| Artifact Identity | `universal_id` | 6,145 | **Present**, one per entry, from the one authority |
| Artifact Class | `object_class` | **7** | **Present**, non-degenerate |
| Authority | `identity_authority` + `validation_contract` | 2 / 1 | **Partial** — names the minting authority, not a per-column canonical register |
| Owner | `owner` | **276** | **Present and non-degenerate** — contrast `artifacts.json`'s 1 (`CAAR-2`) |
| Lifecycle | `lifecycle` | **2** of 3 declared (`RETIRED` unpopulated) | **Present but thin** — `AV-3`'s pattern, one axis short |
| Visibility | — | — | **ABSENT.** No field. Population is version-controlled objects only |
| Certification | `certification_status` | **1** (`GOVERNED`) | **Degenerate** — the exact defect gate 8.4 was written to catch |

Also measured: `producer` carries 33 distinct values; `evidence_class` and
`evidence_boundary` are single constants (1 each) across all 6,145 entries.

So the honest statement is neither "CAAR exists" nor "CAAR is new work." It is: **five of
seven columns are produced and gated over the tracked population; one column (Visibility)
is absent by construction; one column (Certification) is present but degenerate; and the
population excludes every ignored and untracked path — which is precisely where `AV-6`,
`AAR-1`, `AAR-2`, `AAT-3` and `AAR-4` live.** CAAR is a bounded extension of a running
registry, not a seventh one.

### 2.4 `ACD-3` — The closed `class` enum violates a fail-closed root-law invariant, and the lawful form of a closed enum was already available

**Severity: CRITICAL. This is `CIR-11`, restated with its mechanism and its remedy.**

`CIR-11` correctly identified tension between Design §1.1's closed six-value enum and
`AUTH-INF-001`. The tension is stronger than "precedent," and the remedy is more specific
than "make it open."

`engine/uckp/law.py` declares `UCKP-INV-14`, **infinite-extensibility**: *"Every
vocabulary, adapter set and relationship class admits an unknown future member."* It is one
of seventeen root-law invariants, not an aspiration.

`engine/uckp/vocabulary.py` implements the mechanism and states its two properties
verbatim:

> *"**Append-only.** `Vocabulary.extended_with` returns a new vocabulary; it never mutates.
> Redefining an existing term raises, because a term whose meaning can change retroactively
> invalidates every digest computed under the old meaning."*
>
> *"**Closed at the point of use.** `Vocabulary.require` refuses an unregistered term, so
> the openness is 'register then use', not 'anything goes.'"*

This is the resolution of the apparent conflict between `AUTH-INF-001` (never close a
vocabulary) and CAAR Design Constraint 2 (never accept an unresolved value): **registered-
term openness is both.** Membership is unbounded; every member is registered before use;
an unregistered term fails closed at admission. `uckp.governed-category` is such a
vocabulary — 35 terms, owner `UCKP-LAW-0001`, enforced at `engine/uckp/ucko.py:392`
(`require_lawful` → `vocabularies.require_term`) on every admission, extended by appending
a term in DATA and never by amending `law.py` (`extension_rule.how_to_extend`).

Crucially, `vocabulary.py` also states the lawful way to keep a closed enum:

> *"Nine closed term sets elsewhere in the engine are a **checked projection** of one of
> them… `verify_vocabulary_alignment` fails closed if any projection and its vocabulary ever
> diverge, so there is one authority and one verified view rather than two competing
> declarations."*

**A six-value `class` enum is therefore not forbidden. An *unbound* six-value enum is.** The
design's enum is unlawful not because it has six members but because it is declared by
nobody, projects nothing, and no mechanism refuses a seventh value or admits one.

The repository already demonstrates both halves of this distinction:

| Vocabulary | Members | Form | Lawful because |
|---|---|---|---|
| `relationship.schema.json` `type` | unbounded | Open regex, `$comment` lists materialized values | `CR-INF-007`, self-declaring |
| `uckp.governed-category` | 35 | Registered terms, refused if unregistered | Owner `UCKP-LAW-0001`, `UCKP-ART-17` |
| Evidence classes (`UCOS-EVIDENCE-UNIVERSE-001`) | **5, deliberately closed** | *"No sixth class is created"* | **Closed by a named owner who holds authority to close it** |
| `mutation_classes` | 9, grown from 5 | Append, each with `$why_this_class_was_added` | Documented extension acts |
| CAAR Design §1.1 `class` | 6 | Bare JSON enum | **Nothing. Closed by omission.** |

The evidence-class row is the decisive comparison. Closure is lawful in this repository —
`AUTH-INF-001` `CR-INF-001.3` reads "closed" as *complete for current scope*, and an owner
may declare a set complete for its scope. What is unlawful is closure that no owner
declared and no mechanism enforces, because that is indistinguishable from an omission and
cannot be extended without a rewrite (`IL-INF-06`: *"Every construct SHALL be read as
admitting a next member without rewrite, renumber, or migration"*).

### 2.5 `ACD-4` — The path-only identity formula contradicts a subject-domain rule the source register already wrote down

**Severity: CRITICAL. This is `CIR-12`, with the remedy already present in the repository.**

`CIR-12` found that Design §2.2's minting formula requires `canonical_path_at_mint_time`,
which `CONSTITUTIONAL_TRUTH` subjects do not have. The register CAAR draws its classes from
anticipated exactly this and declared against it. `mutation-governance-boundary.json`
`classification_rules.$subject_domain`, verbatim:

> *"The domain is MUTATION SUBJECTS, not only paths. Most subjects are tracked paths;
> `CONSTITUTIONAL_TRUTH` is not — its subjects are `Population` and
> `ConstitutionalMetadata` objects reached through `engine/constitution/gateway.py`. **A
> rule set written over paths alone would silently exclude class 0, so the domain is stated
> rather than assumed.**"*

The design wrote a rule set over paths alone. And the identity plane for non-path subjects
also already exists: `id-ledger.json` `by_observation`, keyed
`<observer>::<subject>::<kind>` with minted `UCOS-OBS-######` identifiers:

```jsonc
"UCOS-AEE-001::actuator-execution-residue::EXECUTION_RESIDUE":
   { "observation_id": "UCOS-OBS-000001", "observer": "UCOS-AEE-001",
     "subject": "actuator-execution-residue", "kind": "EXECUTION_RESIDUE",
     "first_seen": "commit:c087882cfd0a" }
```

Seven entries, two `kind` values, minted from the same `category_seq` counter as `by_path`
and `by_object`, declared in `identity_authority_resolution` as one of three maps of the
single `REPOSITORY_OBJECT` plane. A composite, non-path subject key with a minted stable
identity is not a thing CAAR must invent; it is a thing CAAR must **use**.

### 2.6 The twelve blockers, re-derived from four defects

| Blocker | Derives from | Nature |
|---|---|---|
| `CIR-3` (third identity authority) | `ACD-ROOT` + `ACD-1` | Architectural — dissolves under correction |
| `CIR-11` (closed class enum) | `ACD-ROOT` + `ACD-3` | Architectural — dissolves under correction |
| `CIR-12` (path-only identity) | `ACD-ROOT` + `ACD-4` | Architectural — dissolves under correction |
| `CIR-4` (no `constitutional_superior`) | `ACD-ROOT` | Architectural — `CAA-INV-02` requires it, fail-closed |
| `CIR-5` (unprecedented lifecycle enums) | `ACD-ROOT` + `ACD-2` | Architectural — a third lifecycle axis, unowned |
| `CIR-1` (H-06 coordination) | `ACD-ROOT` | Partly architectural — a correct design needs fewer owner acts |
| `CIR-2` (no ownership test data) | `ACD-2` | **Downgraded** — 276 distinct owners exist; 0 *ratified* |
| `CIR-7` (no certification vocabulary) | `ACD-ROOT` | **Reframed** — see §10; scope plurality is declared, not defective |
| `CIR-6` (`AV-6` / `R-01` unrepaired) | — | **Unchanged.** A real repository defect, not a design defect |
| `CIR-8` (gates unimplemented) | — | **Unchanged.** Implementation work |
| `CIR-9` (0 of 9 prerequisites) | — | **Unchanged**, though §17 shows the count is measured against stages the correction reduces |
| `CIR-10` (rollback unexercised) | — | **Unchanged.** Implementation work |

**Eight of twelve are consequences of one architectural decision. Four are real work that no
redesign removes.** The Readiness Determination's §19 execution order allotted eight
sequential owner and implementation acts to the eight; §16 below allots them one adoption
act, because they are one decision.

---

## 3. Redesign 1 — Closed Vocabulary Elimination

### 3.1 Every closed vocabulary in the design, and its disposition

| # | Design site | Closed set | Disposition |
|---|---|---|---|
| 1 | §1.1 `class.value` | 6 values | **ELIMINATE** — becomes a registered term of a governed vocabulary (§3.2) |
| 2 | §1.1 `identity.origin` | `AUTHORED\|PRODUCED\|OBSERVED` | **ELIMINATE** — registered vocabulary; `OBSERVED` already has a live plane (`by_observation`), and a fourth origin (e.g. `ASSIMILATED`) must not require a schema edit |
| 3 | §1.1 `class.resolution_confidence` | `CLASSIFIED\|UNRESOLVED` | **RETAIN CLOSED** — a two-valued decision procedure outcome, not a taxonomy. `UNRESOLVED` is `mutation-governance-boundary.json`'s declared terminal, `is_diagnostic_only`, `FAILS CLOSED`. Bounded by construction |
| 4 | §1.1 `authority.authority_confidence` | `SINGLE\|CONTESTED\|NONE` | **RETAIN CLOSED, with declaration** — a lattice over "how many authorities claim this," complete over its own scope. Requires an explicit closure declaration naming its owner (§3.3) |
| 5 | §1.1 `owner.resolution_method` | 5 values | **ELIMINATE** — §5.2 of the design itself already proposes a sixth (`SELF_DECLARED_STABLE`), which is proof the set is not complete for its scope |
| 6 | §1.1 `visibility.expected` / `actual` | 3 each | **ELIMINATE `expected`** (see §7.2 — per-surface declaration is already a value, so the set is open); **RETAIN `actual` CLOSED** — it is git's own state space, a physical-reality bound under `CR-INF-003` |
| 7 | §1.2 lifecycle enums | 6 sets | **ELIMINATE** — subordinated to a declared lifecycle axis owner (§11) |
| 8 | §1.1 `certification.state` | deferred | Already open in the design; **bind to the chosen vocabulary's registry**, not to an enum (§10) |

Four eliminations, three principled retentions, one binding. **The test applied to each is
not "is it closed?" but the test `IL-INF-06` states: can a next member be admitted without
rewrite, renumber, or migration?** A set that fails that test is eliminated. A set that
passes it because its scope is genuinely bounded — a boolean-like decision outcome, git's
own state space — is retained, and must say so.

### 3.2 The corrected `class` field

`class.value` becomes a member of a registered, append-only vocabulary rather than a JSON
enum:

```jsonc
"class": {
  "vocabulary": "ucos.caar-artifact-class",     // registered; membership unbounded
  "value": "<a registered term of that vocabulary>",
  "term_registered_at": "<the DATA entry that admitted this term>",
  "resolved_by": "<rule id from the classifier's declared, ordered rule set>",
  "resolution_confidence": "CLASSIFIED | UNRESOLVED",   // closed, §3.1 item 3
  "classified_at_commit": "<sha>"
}
```

with three obligations on the vocabulary itself, each matching an existing mechanism rather
than inventing one:

1. **Registered before use.** Admission calls the equivalent of
   `VocabularyRegistry.require_term`; an unregistered term raises rather than defaulting.
   This is how `uckp.governed-category` is enforced today at `engine/uckp/ucko.py:392`.
2. **Append-only, non-redefining.** A term's meaning may never change, because
   `content_hash` digests computed under the old meaning would be retroactively invalidated
   — `vocabulary.py`'s stated reason, which applies identically to CAAR records carrying
   `classified_at_commit`.
3. **Extended by a DATA append, never a code edit.** `extension_rule.how_to_extend`: *"A new
   vocabulary member, relationship class, adapter or authority role is one appended entry in
   DATA. `engine/uckp/law.py` is never amended to fit the data."*

The six terms the design proposed are then the vocabulary's *seed*, not its definition — the
same relationship `GOVERNED_CATEGORIES`' 35-tuple in `law.py` has to `uckp.governed-category`,
annotated in-source as *"Open by Article 17: an unknown future category is admitted through
`VocabularyRegistry.extend`, not by editing this tuple."*

### 3.3 Closure requires an owner, and a declaration

For the two retained closed sets (§3.1 items 4 and 6-`actual`), the schema must carry an
explicit closure declaration in the form the evidence universe already uses:

```jsonc
"$closure": {
  "closed": true,
  "closed_by": "<the authority that holds standing to close this set>",
  "scope": "<what the set is complete FOR>",
  "basis": "AUTH-INF-001 CR-INF-001.3 — 'closed' means complete for current scope",
  "extension_path": "<the act that would admit a further member, if scope changes>"
}
```

**A closed set with no `$closure` block is a defect by construction under this correction**,
and is the specific, checkable form of the defect `CIR-11` named in prose. This converts
"closed enum" from a judgement call into a schema-validatable condition.

---

## 4. Redesign 2 — Infinite Extensibility Model

### 4.1 The five extension axes, each bound to an existing mechanism

`AUTH-INF-001` `IL-INF-06` requires that every construct admit a next member without
rewrite, renumber, or migration. Applied to CAAR, five things must be able to grow:

| Axis | What grows | Extension act | Existing mechanism | Requires code change? |
|---|---|---|---|---|
| **A1 · Class** | A seventh artifact class | Append a term to `ucos.caar-artifact-class` | `VocabularyRegistry.extend` (`vocabulary.py:161`) | **No** |
| **A2 · Subject kind** | A subject that is neither file nor object (§6) | Append a `kind` to the observation plane | `id-ledger.json` `by_observation` (`kind` field, live) | **No** |
| **A3 · Authority column** | An eighth CAAR column | Append a column with its own declared authority (§16.2) | The per-column authority table's own shape | **No** |
| **A4 · Lifecycle state** | A new state in an axis | The axis owner appends (`UCL-000001` / state-axis owner) | `lifecycle_resolution.axes` (`ORTHOGONAL_AXES`) | **No** — owner act, not CAAR act |
| **A5 · Rule** | A tenth classification rule | Append to the ordered rule set in DATA | `mutation-governance-boundary.json` grew `R-09` this way | **Declarative** |

`R-09` is the worked example for A5: `GOVERNED_ANALYSIS` was added to the register with a
`$why_this_class_was_added` field recording the act — *"Phase 1B Violation 4 resolution"* —
and its `membership_criteria`, without amending the register's schema. Two classes before it
(`CORPUS_REGISTRATION`, `GOVERNED_DECLARATION`) carry `$why_this_class_was_missing` fields
recording their own admission. **The class vocabulary CAAR proposed to freeze at six has, in
its own source register, grown from five to nine and documented each growth.**

### 4.2 The non-terminality obligation on CAAR's own record

`CR-INF-001.2` and `CR-INF-011`: *"Certification closes scope. Certification never closes
evolution."* Applied to a CAAR record:

- No CAAR record may hold a state from which no transition is legal. A `SUPERSEDED` or
  `DEPRECATED` artifact retains its identity, its record, and its eligibility for
  append-only successors (`IL-INF-07`: *no reading shall invalidate, renumber, mutate or
  close any existing… identity*).
- The precedent is already implemented: UGA's `RETIRED` lifecycle state is defined as
  *"Previously minted an identity, no longer carried by version control. **Identity is
  retained (append-only) and never reissued.**"* Retirement is not deletion, and the
  ledger's `id_preservation` rule makes it measurable (`CAA-INV-04` *"recomputes the
  derivation over every ledger id and fails on any collision or any id it cannot carry
  through verbatim"*).
- `version: "0.1.0-design"` in Design §1.1 must not become a ceiling. Under `CR-INF-002`
  (*numbers indicate sequence, never limits*) the schema version is a sequence alias; the
  design's §9.3 versioned-snapshot mechanism is compatible with this and needs no change.

### 4.3 The extensibility self-test

A schema is `IL-INF-06`-compliant when, for each axis A1–A5, the answer to *"what file
changes to admit member N+1?"* is a DATA append and nothing else. Stated as a gate
(specification only; see §14 gate `G-C3`): for each axis, a synthetic N+1 member is admitted
in a scratch copy and the diff is asserted to touch only declared DATA paths. **An
extensibility claim that is not exercised is `CIR-10`'s defect applied to openness** — an
architectural assertion, not a verified property — and this determination declines to make
it without naming the exercise that would verify it.

---

## 5. Redesign 3 — Universal Identity Alignment

### 5.1 CAAR mints nothing

The correction is total and follows from `CAA-INV-04` (`EXACTLY_ONE_IDENTITY_AUTHORITY`,
`fails_closed: true`) and `identity_authority_resolution`'s declaration that
`id-ledger.json` is *"PERSISTENCE — the storage binding of `UCKP-ART-05`, and the ONE such
binding in this repository."*

**Design §2.2's minting formula is withdrawn in its entirety.** `caar_id` does not exist.
A CAAR record is keyed on the identity the subject already holds:

| Subject kind | Ledger plane | Key shape | Live population |
|---|---|---|---|
| Corpus document | `by_path` | `UCOS-<CATEGORY>-<NNNNNN>` | 1,492 |
| Repository object (code, config, data, excluded doc) | `by_object` | `UCOS-<CATEGORY>-<NNNNNN>` | 4,914 |
| Non-file subject (observation, constitutional truth — §6) | `by_observation` | `UCOS-OBS-<NNNNNN>` over `<observer>::<subject>::<kind>` | 7 |

Design §2.1's argument for a new key — *"path is unstable under rename"* — is correct about
paths and wrong about the ledger, which is append-only, `first_seen`-frozen, *"never
reissued; never renumbered"*, and already survives retirement by keeping the identity while
dropping the path.

### 5.2 A subject with no ledger identity is an admission request, not a mint

The fail-closed rule that replaces minting:

```
CAAR record admission for subject S:
  1. Resolve S in id-ledger  (by_path → by_object → by_observation)
  2. Found      → key the record on that universal_id.
  3. Not found  → emit an ADMISSION REQUEST to the authority that governs S's plane
                  (REG-AUTO-001 for corpus, UCOS-UGA-001 for objects,
                   the observing programme for observations),
                  and write the record with identity.state = UNADMITTED,
                  class.resolution_confidence = UNRESOLVED,
                  every downstream field at its own UNRESOLVED value (Design §1.3).
  4. NEVER      → mint, derive, hash, or synthesize a key.
```

This preserves Design Constraint 2 (fail closed, never a silent default) while removing the
second authority. It also makes CAAR's coverage gap *visible as a queue of admission
requests* rather than invisible behind a locally-minted id — which is the same correction
`AV-6` needs for visibility (§7) and `AAR-2` needs for the 48 unregistered ignored paths.

### 5.3 Representation of the key

`identity_authority_resolution.derivation` declares a total, already-implemented mapping
from a ledger id to a constitutional URN:

```
UCOS-ENGINE-000496  →  urn:ucos:ucko:ucos-repository:UCOS-ENGINE-000496
        function: engine.uckp.alignment.repository_local_urn
        id_shape: ^UCOS-[A-Z0-9]+-[0-9]{6}$
```

CAAR records carry the ledger id as the key and the URN as the cross-plane reference. This
gives CAAR one key readable by both the repository plane and the constitutional-object plane
without CAAR declaring a namespace of its own — and it is why §5.4's alternative is
rejected.

### 5.4 The rejected alternative, and why it is rejected

`identity_namespace_resolution` declares the model
`MULTIPLE_INDEPENDENT_BOUNDED_NAMESPACES`, so a CAAR namespace is not *prima facie*
forbidden. It would require, per that section's own five principles: a bounded population,
an owned identifier pattern, declared admission semantics, its own registry, and — decisively
— *"Cross-namespace relationships require explicit declaration; an undeclared relationship
is not assumed to exist."*

It is rejected for three measured reasons:

1. `UCKP-ART-18` requires that before creating anything, its canonical object is located and
   reused, extended, or referenced. §2.2 locates it, at 100% coverage of the union
   population. **REUSE is available, so CREATE is unavailable** — the same disposition test
   `02-CANONICAL-OWNERSHIP-MATRIX.md` records applying to `Ω-E02` and `Ω-E03`, where 48
   REUSE + 6 EXTEND + **zero CREATE** was the recorded outcome of the identical question.
2. Namespaces are plural; *authorities* are not. A namespace that mints is an authority, and
   `CAA-INV-04` admits one.
3. A declared CAAR namespace would require a declared relation to three existing planes,
   which is strictly more governance work than using the planes.

---

## 6. Redesign 4 — Non-File Object Identity

### 6.1 The subject domain, stated rather than assumed

CAAR's subject domain is corrected to match its source register's, verbatim in structure:

> **CAAR's domain is ARTIFACT SUBJECTS, not only paths.** A subject is anything that holds,
> produces, or observes a governed thing. Most subjects are repository paths; some are
> objects reached through an engine and never written to disk; some are observations, which
> are readings with value-independent identity and no bytes of their own.

### 6.2 Three subject kinds, each with an existing identity plane and an existing truth class

`evidence_observation_separation` in the alignment register already partitions truth four
ways, with `may_be_canonical` set per class. CAAR's subject kinds map onto it exactly:

| Subject kind | Example | Identity plane | Truth class | `may_be_canonical` | Path? |
|---|---|---|---|---|---|
| `FILE_SUBJECT` | `engine/uckp/law.py` | `by_path` / `by_object` | Identity truth (`UCKP-ART-02`) | **true** | Yes |
| `OBJECT_SUBJECT` | a `Population` mutated via `engine/constitution/gateway.py` | `engine/uckp/identity.py` URN, referenced from ledger | Identity truth | **true** | **No** |
| `OBSERVATION_SUBJECT` | `UCOS-RIB-001::working-tree-cleanliness-verdict::WORKING_TREE_STATE` | `by_observation` | Observation truth (`UCKP-ART-13`) | **false** | **No** |

The third row carries a constraint the design could not have known to state and that matters
for certification: an observation *may not be canonical*, because — quoting the register —
*"`UCKP-ART-13` requires identical inputs to produce identical bytes. A reading taken outside
the commit boundary is not an input the commit contains, so admitting one into a canonical
digest destroys the fixed point by construction — which is exactly how one stale digest
became a permanently non-convergent Phase 8."*

**Therefore: a CAAR record whose subject is an `OBSERVATION_SUBJECT` may never carry
`certification.may_affect_certification: true`.** This is a new, mechanically checkable
invariant that neither the design nor the readiness determination could state, and it
strengthens `AV-8` from "3 untracked evidence surfaces claim certification effect" to a
structural prohibition on a whole subject kind.

### 6.3 What this closes and what it does not

`CIR-12` is closed as an architectural defect: `CONSTITUTIONAL_TRUTH` subjects are
representable, because `OBJECT_SUBJECT` exists and `by_observation` demonstrates the
composite-key construction. **It is not closed as data**: `by_observation` holds 7 entries
across 2 `kind` values, none of which is a `Population` or `ConstitutionalMetadata` subject.
The plane exists and is unpopulated for this use. Populating it is `UCOS-CMG-EXEC-000001`'s
act, not CAAR's — which is the correct outcome, since CAAR minting for that class was the
defect.

---

## 7. Redesign 5 — Representation Independence

### 7.1 The record is a projection, not a file

`UCKP-INV-11`, **zero-storage-lock-in**: *"Two or more persistence technologies round-trip
the universe byte-identically."* Design §3.1's phrase "**the CAAR store**" (§9.1: *"delete
the CAAR store"*) treats a JSON file as the record's identity. Corrected:

- A CAAR record is defined by its **columns and their authorities** (§16.2), not by a file
  format or a location.
- `caar.json` — if one exists — is a *materialization*, exactly as
  `02-UNIVERSAL-OBJECT-REGISTRY.json` is a materialization of what `uga_engine.py` computes,
  declared in `evidence_binding` with a class, a retention, and an `input_classification`.
- No consumer may key on the file path. Consumers resolve through the identity plane.

This also repairs an unnoticed inconsistency: Design §9.1 claims rollback is *"delete the
CAAR store; no source registry was ever written"* while Design §2.2 mints identities into
that same store. **Under the design as written, deleting the store destroys identities that
exist nowhere else** — the rollback claim and the minting claim are incompatible. With
minting withdrawn (§5.1), the rollback claim becomes true for the first time, because every
identity survives in the ledger. `CIR-10` remains open as an exercise; its *architectural
premise* is repaired here.

### 7.2 Visibility is a property of the subject, not of the representation

Design §6.1 makes `visibility.expected` a pure function of class, which is correct
(Constraint 1) but under-specified: its own `PER_SURFACE_DECLARATION` value for EVIDENCE
proves the set is not three-valued, because a per-surface declaration is a *pointer to a
declaration*, not a state. Corrected shape:

```jsonc
"visibility": {
  "expected": { "source": "CLASS_DEFAULT | PRODUCER_DECLARATION | SURFACE_DECLARATION | EXCLUSION_REGISTER",
                "declared_by": "<the register or producer that declares it>",
                "value": "<a registered term of ucos.caar-visibility-expectation>" },
  "actual":   "TRACKED | UNTRACKED | IGNORED",     // closed: git's own state space, CR-INF-003 physical bound
  "reconciled": true,
  "unreconciled_since_commit": "<sha or null>"
}
```

`unreconciled_since_commit` is added because Design §6.2's core insight — that a mismatch
must be *recorded and queryable*, not corrected — is weakened if the record cannot say how
long the mismatch has stood. Without it, `AV-6`'s defect becomes visible but not
prioritizable.

### 7.3 The measured need for a visibility column

UGA's population is the version-controlled boundary, so it cannot host this column as it
stands. Measured at this baseline:

```
git ls-files                              : 6,188
UGA object registry entries               : 6,145
UGA paths ∩ tracked                       : 6,028
  → tracked paths absent from UGA         :   160
  → UGA paths no longer tracked at HEAD   :   117
```

The 117 are UGA's own `RETIRED` case, undetected because the registry is stale relative to
HEAD — **the same drift pattern `AAT-4` measured for population counts**, now measured for
the object registry, and independently visible in the alignment register, which records
UGA's population as *"5,789 objects (measured)"* against 6,145 today. Two consequences: the
visibility column is genuinely new work (§13), and any CAAR build must treat its own
staleness as a first-class measured quantity rather than an assumption.

---

## 8. Redesign 6 — Registry Authority Alignment

### 8.1 CAAR is a projection with a declared superior, not a seventh register

Every instrument bound by `constitutional-authority-alignment.json` carries a
`constitutional_superior` block; `CAA-INV-02`
(`EVERY_AUTHORITY_CLAIM_NAMES_ITS_CONSTITUTIONAL_SUPERIOR`) is fail-closed. CAAR's schema
must carry one. `CIR-4` graded this MEDIUM as a "header convention"; it is a blocking
alignment invariant.

The form is established by the two registers CAAR reads. `mutation-governance-boundary.json`:

```jsonc
"constitutional_superior": {
  "authority": "UCKP-LAW-0001", "home": "engine/uckp/law.py",
  "role": "EXECUTION", "relation": "PROJECTION",
  "articles": ["UCKP-ART-10", "UCKP-ART-16"],
  "binding": "00-BOOK/DATA/constitutional-authority-alignment.json",
  "effect": "This artifact already said of itself that it creates no authority and governs
             nothing. UCKP-ART-10 — execution never owns knowledge — is the article that
             sentence is true UNDER."
}
```

CAAR's equivalent must state `relation: "PROJECTION"` and an `effect` clause that names
the article under which CAAR's own "authoritative for lookups" claim (Design §3.1) is true.
That claim is the one most in need of it: **a projection may be authoritative for lookups
only in the sense that it is a verified view of authorities that remain elsewhere** — which
is what UGA's declaration says of itself (*"It remains upstream of the engine that reads it
and must never be produced by one; what it is not, and never was, is the top of its own
chain"*).

### 8.2 The rival-object-model hazard

`CAA-INV-07` (`NO_INSTRUMENT_DECLARES_A_RIVAL_OBJECT_MODEL`) is fail-closed. UGA's
declaration carries an `object_model` block for exactly this reason, and says so:

> *"Seven object classes named in a declaration that cites no model read exactly like a
> rival object model. `CAA-INV-07` measures that no instrument declares one, and this block
> is what makes the measurement pass truthfully rather than by absence of a keyword."*

The CAAR design declares six classes and cites no model. It requires the same block: naming
`UCKO` (`engine/uckp/ucko.py`, `UCKP-ART-02`) as the model, and declaring CAAR's classes a
**projection onto the artifact-authority question**, answering *"what governs this
subject"* — not *"what is an object."*

This also disposes of Design §3.1's own stated worry, *"CAAR must not become a seventh
ungoverned vocabulary — the exact failure mode `AV-1` measured."* The design correctly
identified the hazard and then addressed it with a self-conformance gate (8.9) that checks
CAAR against a six-column model of its own devising. The repository's existing answer —
declare the model you project, and let `CAA-INV-07` measure it — is stronger, because it is
checked by an authority CAAR does not control.

### 8.3 Vocabulary census

Six class-like vocabularies are live at this baseline; CAAR would have been the seventh:

| Vocabulary | Members | Owner | Population | Answers |
|---|---|---|---|---|
| `mutation_classes` | 9 | `UCOS-MUTATION-GOVERNANCE-BOUNDARY-001` | mutation subjects | Which authority governs a *change* |
| UGA `object_classes` | 7 | `UCOS-UGA-001` | 6,145 version-controlled objects | Which *kind* of repository thing |
| UGA `lifecycle_states` | 3 (2 populated) | `UCOS-UGA-001` | same | Authored / generated / retired |
| Evidence classes | 5, closed by owner | `UCOS-EVIDENCE-UNIVERSE-001` | evidence surfaces | Which record class |
| `uckp.governed-category` | 35 | `UCKP-LAW-0001` | constitutional objects | Which category of entity |
| `uckp.relation-type` etc. | open | `UCKP-LAW-0001` | edges | Which relationship |
| **CAAR `class`** | **6** | **none** | **undefined** | **ambiguous — see below** |

The census exposes a question the design never resolved: CAAR's six values conflate two
axes that the repository keeps separate. `AUTHORED`, `GENERATED` and `DERIVED` are
*provenance* (UGA's `lifecycle` axis and its `producer` field); `EVIDENCE`, `CACHE` and
`TEMPORARY` are *disposition* (evidence class, exclusion register). Under `UCKP-ART-03` a
second definition of an existing primitive is void, so the corrected `class` field must
either (a) declare which existing axis it projects and derive from it, or (b) declare itself
a genuinely new axis with its own bounded question, in the form `existence_resolution` uses
for its four existence authorities (*"bounded_question"*). **Option (b) is recommended**,
with the bounded question stated as: *"which authority answers for this subject's
governance, and under what expectation of visibility and certification?"* — a question none
of the six existing vocabularies asks.

---

## 9. Redesign 7 — Ownership Integration

### 9.1 The measured correction

`CIR-2` (HIGH) held that ownership resolution has *"zero live test cases."* Recomputed:

| Source | Populated | Distinct values | Usable? |
|---|---|---|---|
| `ucos-ownership-declarations.json` `assignments` | 0 | 0 | No — empty, as measured four times |
| `artifacts.json` `owner` | 1,461 / 1,461 | **1** (`UCOS-PROGRAM-CUSTODIAN`) | No — degenerate (`CAAR-2`) |
| GAR `owner`/`validation_owner` | 345 / 345 | 32 | Yes, for 345 paths |
| **UGA `owner`** | **6,145 / 6,145** | **276** | **Yes, for 6,145 paths** |

The design's §5.1 resolution order resolves against tiers 1–2 above and never reads tier 4.
Corrected order, inserting the measured tier and preserving fail-closed:

```
1. RATIFIED        — ucos-ownership-declarations.json assignments[uid]        (0 today)
2. REGISTRY        — GAR owner/validation_owner, non-degenerate               (345)
3. DERIVED_TOTAL   — UGA derive_owner, a declared TOTAL function over the
                     version-controlled boundary, 276 distinct values         (6,145)
                     → resolution_method = DERIVED_TOTAL, DERIVED flag set
4. SELF_DECLARED   — artifact's own Authority/Deciders field, UNVERIFIED      (AAT-2)
5. NON_UCOS        — exclusion register names a tool, not a UCOS authority    (AAT-3)
6. UNRESOLVED      — none of the above; never fabricated
```

Tier 3 sits below registry data and above self-declaration because it is *structural but
unratified*: `derive_owner` is a pure function of path shape (*"Operational Memory is
organised by programme; the programme directory IS the owner"*), so it is reproducible and
non-fabricated, but it is a **derivation, not an assignment** — nobody consented to it.

### 9.2 `OwnershipFabricationError` is not violated, and the distinction must be carried in the record

Design Constraint 3 forbids inferring an owner to close a metric. Tier 3 is compatible only
if the record never presents a derivation as an assignment. Two obligations:

- `owner.resolution_method: "DERIVED_TOTAL"` and a permanent `derived: true` flag, on the
  model of the design's own `UNVERIFIED` treatment of `SELF_DECLARED` (§5.2).
- **Ownership-coverage metrics report three numbers, never one:** ratified, declared,
  derived. A single "97% owned" figure computed over tier 3 would be exactly the false
  coverage `CAAR-2` and Step 3 §3.6 warned against, arrived at from a new direction.

`CIR-2` is therefore **downgraded from HIGH to MEDIUM**, not closed: the resolution algorithm
now has 6,145 live cases at tiers 3–5 and can be exercised, while tier 1 — the constitutional
act `CEP-OWN-004` — remains empty and untestable. The blocker was "the algorithm cannot be
exercised at all"; it is now "the ratified tier cannot be exercised," which is a smaller,
truer statement.

---

## 10. Redesign 8 — Certification Integration

### 10.1 One-directionality is retained unchanged

Design §7.1 and Constraint 4 are correct and are carried forward without modification.
`evidence_observation_separation` independently confirms the direction: certification is a
consumer of identity truth, and identity truth is *"a pure function of the commit."*

### 10.2 `CAAR-3`'s three totals are not a defect — they are four bounded questions, one of which is stale

`CIR-7`'s framing (and `CAAR-3`'s, and Design §7.2's) assumes the three population totals
must be reconciled into one. `existence_resolution` declares the opposite, as a model:

> **`MULTIPLE_INDEPENDENT_AUTHORITIES`** — *"Existence-tracking in UCOS is plural by design.
> Each authority answers a different bounded question about 'what exists'; holding
> undisputed authority over one does not compete with another holding undisputed authority
> over a different one."*

with four authorities named, each carrying an explicit `bounded_question` and a measured
population. Recomputing the disputed figures against that model:

| Figure | Bounded question | Authority | Status at this baseline |
|---|---|---|---|
| 1,233 | Which corpus documents are in certified scope? | certification chain | Matches UGA's `DOCUMENT_ARTIFACT` count exactly: **1,233** |
| 1,461 | Which artifacts are corpus-registered? | `UMB-IMP-001` / `REG-AUTO-001` | 228 more than 1,233 — the long-standing gap |
| 6,145 | Which version-controlled objects exist and who owns them? | `UGA-EXISTENCE-REGISTRY` | Registry says 6,145; **the alignment register still records 5,789** |
| 6,188 | Which paths does version control carry? | git | 43 more than UGA's registry; 160 absent from it |

Two findings from this recomputation. First, the 1,233 figure is not an isolated
certification-side number: it is the *same* population UGA independently classifies as
`DOCUMENT_ARTIFACT`, reached by a different route. That agreement was invisible while the
figures were compared as bare totals rather than as answers to stated questions. Second, the
alignment register's own recorded UGA population (5,789) is stale against the live registry
(6,145) — **`AAT-4`'s drift, measured for a third time, now inside the register that
declares how existence is resolved.**

**Corrected obligation.** `certification.proof_population_scope` does not name one of three
totals. It names **a bounded question and its authority**, and carries the population digest
at claim time:

```jsonc
"proof_population_scope": {
  "bounded_question": "<verbatim from existence_resolution, or a newly declared one>",
  "authority": "<the existence authority that answers it>",
  "population_digest": "<content digest of the population at claim time>",
  "measured_at_commit": "<sha>"
}
```

The digest is what makes drift detectable rather than discoverable-by-determination; its
absence is why 5,789 could stand against 6,145 unnoticed.

### 10.3 `CIR-7` reframed

`CIR-7` said `certification.state` has no populatable value until one of `AV-5`'s four
vocabularies is chosen. That remains true and remains a certification-authority act outside
this determination. What changes is scope: `AV-5` is about **which state vocabulary** a
certification uses. `CAAR-3`/`CIR-7`'s population question is separable, has a declared
model, and does not require the vocabulary choice to be made first. The two were coupled by
the design's §7 and are hereby decoupled — **`CIR-7`'s vocabulary half stays blocking on
Stage 10; its population half is answerable now, by declaration.**

Also carried in from §6.2: no `OBSERVATION_SUBJECT` record may set
`may_affect_certification: true`, because observation truth is `may_be_canonical: false`.

---

## 11. Redesign 9 — Lifecycle Integration

### 11.1 CAAR declares no lifecycle vocabulary

`lifecycle_resolution` declares the model `ORTHOGONAL_AXES` and names two axis owners:

| Axis | Owner | Home | Scope |
|---|---|---|---|
| PROCESS | `UCL-000001` | `engine/nucleus/lifecycle.py` | 45-stage universal work-cycle, declared to apply to *"nuclei, layers, compositions, capabilities, artifacts, knowledge, registries, policies, evidence, executions, contexts, universes, civilisations and realities alike"* |
| STATE | `KNOWLEDGE-LIFECYCLE` | `engine/knowledge/model.py` | 10-stage standing vocabulary, bounded to knowledge objects |

and warns explicitly that these *"are not the same vocabulary"* and that neither is a
projection of the other. Design §1.2 invents six per-class state vocabularies citing
neither. Under `UCKP-ART-03` that is a third lifecycle axis by construction — the defect
`CIR-5` named as "unprecedented proposals," with its mechanism now identified.

**Correction:** CAAR carries a lifecycle *reference*, not a lifecycle *vocabulary*:

```jsonc
"lifecycle": {
  "axis": "PROCESS | STATE | <a newly declared axis, by its owner>",
  "axis_owner": "<UCL-000001 | KNOWLEDGE-LIFECYCLE | ...>",
  "state": "<a term of that axis's own vocabulary>",
  "entered_at_commit": "<sha>",
  "legal_transitions": "<resolved from the axis owner, never restated here>"
}
```

`legal_transitions` becomes a resolution rather than a stored list, for the reason
`engine/uckp/law.py` gives about the evolution stage set: a second copy of a vocabulary is a
second authority over one subject.

### 11.2 What the design's six enums become

They are not discarded — they are a **proposal to an axis owner**, which is what
`CIR-5` asked for. Their disposition, per class:

- The `STATE` axis is bounded to knowledge objects and does not cover artifacts. The
  `PROCESS` axis declares artifacts in scope. So the design's `AUTHORED`
  (`DRAFTED → REVIEWED → COMMITTED → SUPERSEDED|DEPRECATED`) is most plausibly a projection
  of `UCL-000001`'s 45-stage cycle onto authored artifacts, and must be reviewed as such
  by `UCL-000001`'s owner rather than adopted as a new axis.
- `GENERATED`'s cycle already has two live values (UGA `AUTHORED`/`GENERATED`) plus a third
  declared and unpopulated (`RETIRED`). The design's proposal (`REGENERATED → STALE →
  REGENERATED → PRODUCER_REMOVED → ORPHANED`) extends UGA's, and is an extension request to
  `UCOS-UGA-001`.
- `EVIDENCE`'s `CAPTURED → RETAINED → EXPIRED` overlaps `evidence-universe.json`'s retention
  field, which already governs that population.
- `CACHE` and `TEMPORARY` cover the ignored population that no axis currently reaches —
  genuinely new, and the only two of six for which a new declaration is the right answer.

Restated: **four of six proposed lifecycle vocabularies are extension requests to existing
owners; two are new.** `CIR-5`'s remedy is thereby reduced from "six unreviewed inventions
require owner review" to "two new declarations plus four extension requests" — smaller, and
routed to owners who exist.

---

## 12. Redesign 10 — Backward Compatibility

### 12.1 What is preserved, without exception

`IL-INF-07` (*"No reading under this constitution SHALL invalidate, renumber, mutate, or
close any existing certification, freeze, registry, program, domain, artifact, identity,
page, edge, or signal"*) and `id_preservation` (*"Every identifier that existed before this
binding exists after it, unchanged"*) bind this correction as strictly as they bind any
other change. Under the correction:

| Preserved | Why the correction cannot disturb it |
|---|---|
| All 1,492 `by_path` + 4,914 `by_object` + 7 `by_observation` identities | CAAR mints nothing and writes to no ledger map (§5.1) |
| `page_cursor` (10,840) and corpus page layout | No page range is consumed; CAAR is not a BOOK concept |
| `artifacts.json`, GAR, exclusion register, evidence universe, certification registry | Read-only, as in Design §4.3 — unchanged by this correction |
| UGA's 6,145 entries and `UGA-INV-01..10` | The correction extends UGA's columns; it removes none |
| Every existing certification and freeze | `CR-INF-008`, `CR-INF-011`: scope closed, evolution open |

### 12.2 The correction *reduces* the compatibility surface

Design §4's dual-read model exists because CAAR would hold identities and classifications
that consumers must learn to prefer over their existing registry reads. With minting
withdrawn:

- A consumer reading `id-ledger` today and a consumer reading CAAR tomorrow resolve the
  **same key**. There is no identity cutover, so §4.2's per-class dual-read window
  collapses to a *column* dual-read: only the two genuinely new columns (visibility,
  non-degenerate certification) need observation before use.
- §9.2's per-class rollback becomes per-column rollback, which is strictly finer-grained.
- §9.1's rollback claim becomes true rather than self-contradictory (§7.1).

### 12.3 One backward-compatibility risk the correction introduces

Binding CAAR's class field to a registered vocabulary means **CAAR's admission path can now
fail closed on a term that a source register already uses.** The mutation register's nine
classes, UGA's seven, and the design's six are three different sets; if the seeded CAAR
vocabulary omits a term some register emits, records that would previously have carried a
wrong-but-populated class now carry `UNRESOLVED`. That is the correct behavior under
Constraint 2 and it will make coverage *appear* to drop at first build. This must be
declared in advance, in the form the exclusion register's `input_classifications` already
uses for `UNKNOWN` (*"FAILS CLOSED — a canonical artifact may not depend on an input nobody
has classified"*), so that a first-build coverage drop is read as the gate working rather
than as a regression.

---

## 13. Corrected Target Architecture

### 13.1 Statement

> **CAAR is a fail-closed projection that adds an artifact-authority view over the one
> identity authority, extending the Universal Object Registry with the two columns it lacks
> and the populations it excludes. It mints no identity, declares no object model, owns no
> lifecycle vocabulary, and stores nothing that is authoritative anywhere else.**

### 13.2 Layers

```
 CONSTITUTIONAL   UCKP-LAW-0001 · UCKP-ART-02 (UCKO) · UCKP-ART-05 (identity)
      AUTHORITY   AUTH-INF-001 (CR-INF-001…012) · CAA-INV-01…07 (fail-closed)
                        │
                        │ constitutional_superior: PROJECTION            [CAA-INV-02]
                        ▼
      IDENTITY    00-BOOK/DATA/id-ledger.json  — THE one persistence binding
        PLANE     by_path 1,492 · by_object 4,914 · by_observation 7     [CAA-INV-04]
                        │
                        │ every CAAR record is keyed here; none is minted here
                        ▼
    VOCABULARY    ucos.caar-artifact-class      (registered, append-only, §3.2)
        PLANE     ucos.caar-visibility-expectation
                  lifecycle: REFERENCED from UCL-000001 / state axis      [UCKP-INV-14]
                        │
                        ▼
      COLUMN      identity → id-ledger        │  owner      → §9.1 six-tier
   AUTHORITIES    class    → vocabulary owner │  lifecycle  → axis owner
                  authority→ source register  │  visibility → exclusion reg. + repaired R-01
                                              │  certification → CEP-005 chain
                        │
                        ▼
     MATERIAL-    UGA 02-UNIVERSAL-OBJECT-REGISTRY.json  (6,145, live, gated)
     IZATIONS     + visibility column          (new — §7.3)
                  + certification column       (new — replaces degenerate constant)
                  + non-tracked population      (new — AV-6/AAR-2/AAT-3 territory)
                  = the CAAR view.  A file is a materialization, never the record [UCKP-INV-11]
```

### 13.3 The four constraints, re-examined

Design §0's four constraints survive the correction. Two are strengthened by it:

| Constraint | Status under correction |
|---|---|
| 1 · Visibility never determines classification | **Unchanged**, and now enforceable: the class comes from a vocabulary resolved before the visibility column is computed |
| 2 · Fail closed, never a default | **Strengthened**: `UNRESOLVED` is not merely CAAR's convention but the source register's declared terminal (`is_diagnostic_only`, *"must never be read as a permissive default"*), and unregistered vocabulary terms now also fail closed |
| 3 · Ownership never fabricated | **Strengthened**: tier 3 is a declared derivation carrying a permanent `derived` flag, and coverage reports three numbers rather than one (§9.2) |
| 4 · Certification never feeds back | **Unchanged**, plus a new structural prohibition on observation subjects (§6.2, §10.3) |

---

## 14. Schema Changes Required

| # | Field | Design §1.1 | Corrected | Closes |
|---|---|---|---|---|
| S-01 | `identity.caar_id` | `CAAR-<16hex>`, minted by formula | **REMOVED.** Replaced by `identity.universal_id` (ledger) + `identity.urn` | `CIR-3` |
| S-02 | `identity.plane` | — | **NEW.** `by_path \| by_object \| by_observation` | `CIR-3` |
| S-03 | `identity.subject_kind` | — | **NEW.** `FILE_SUBJECT \| OBJECT_SUBJECT \| OBSERVATION_SUBJECT`, registered vocabulary | `CIR-12` |
| S-04 | `identity.state` | — | **NEW.** `ADMITTED \| UNADMITTED` — fail-closed replacement for minting (§5.2) | `CIR-3` |
| S-05 | `identity.origin` | 3-value enum | Registered vocabulary term | `CIR-11` |
| S-06 | `class.value` | 6-value enum | Registered term of `ucos.caar-artifact-class` + `vocabulary` + `term_registered_at` | `CIR-11` |
| S-07 | `class.bounded_question` | — | **NEW.** States what the class axis answers, in `existence_resolution`'s form (§8.3) | `CIR-11` |
| S-08 | `owner.resolution_method` | 5-value enum | Registered vocabulary; adds `DERIVED_TOTAL` tier (§9.1) | `CIR-2`, `CIR-11` |
| S-09 | `owner.derived` | — | **NEW.** Permanent flag on tier-3 resolutions | `CIR-2` |
| S-10 | `lifecycle.state` | per-class invented enums | `axis` + `axis_owner` + term of that axis's vocabulary; `legal_transitions` resolved, not stored | `CIR-5` |
| S-11 | `visibility.expected` | 3-value enum | Object: `{source, declared_by, value}` (§7.2) | `CIR-11` |
| S-12 | `visibility.unreconciled_since_commit` | — | **NEW.** Makes an `AV-6` mismatch prioritizable | — |
| S-13 | `certification.proof_population_scope` | "one of CAAR-3's three totals" | Object: `{bounded_question, authority, population_digest, measured_at_commit}` (§10.2) | `CIR-7` (population half) |
| S-14 | `certification.may_affect_certification` | boolean | Boolean, **prohibited true** for `OBSERVATION_SUBJECT` | `AV-8` |
| S-15 | `constitutional_superior` | absent | **NEW, top level.** `{authority, home, role, relation: PROJECTION, articles, binding, effect}` | `CIR-4` |
| S-16 | `object_model` | absent | **NEW, top level.** Names `UCKO`/`UCKP-ART-02`; declares classes a projection (§8.2) | `CIR-11` |
| S-17 | `$closure` | absent | **NEW, per retained closed set.** `{closed, closed_by, scope, basis, extension_path}` (§3.3) | `CIR-11` |
| S-18 | `materialization` | implied "the CAAR store" | **NEW.** Declares emitted surfaces with class/retention/`input_classification`, as `evidence_binding` does | `UCKP-INV-11` |

**Eighteen changes: 4 removals or replacements, 9 additions, 5 shape changes. None adds a
register, a counter, a sequence, or a namespace.**

### 14.1 Gate changes

The design's ten gates are retained. Four are added, each checking a correction that would
otherwise be an unverified assertion:

| Gate | Fails when | Checks |
|---|---|---|
| `G-C1` | Any CAAR record carries an identifier not resolvable in `id-ledger` | §5.1 — no second authority |
| `G-C2` | Any vocabulary-bound field holds an unregistered term, or any closed set lacks `$closure` | §3.2, §3.3 |
| `G-C3` | Admitting a synthetic N+1 member on any axis A1–A5 requires a diff outside declared DATA paths | §4.3 — extensibility exercised, not asserted |
| `G-C4` | Any `OBSERVATION_SUBJECT` record sets `may_affect_certification: true` | §6.2 |

Gate 8.4 (degenerate-field detection) is noted as already failing against live data if
applied to UGA today: `evidence_class`, `evidence_boundary` and `certification_status` each
hold **one distinct value across 6,145 entries**. This is disclosed, not repaired here.

---

## 15. Identity Model

### 15.1 Rules

| # | Rule | Basis |
|---|---|---|
| I-1 | CAAR mints no identifier, in any namespace, under any condition | `CAA-INV-04`, fail-closed |
| I-2 | A record's key is the Universal ID the subject already holds | `identity_authority_resolution` |
| I-3 | Resolution order is `by_path` → `by_object` → `by_observation`, first hit wins | Ledger plane structure |
| I-4 | A subject with no identity produces an **admission request** and an `UNADMITTED` record, never a key | Constraint 2 + `UCKP-ART-18` |
| I-5 | Path is an attribute (`current_path`, `path_history`), never a key | Design §2.3, retained |
| I-6 | Cross-plane reference is `urn:ucos:ucko:ucos-repository:<UCOS-ID>` | `repository_local_urn`, `id_shape ^UCOS-[A-Z0-9]+-[0-9]{6}$` |
| I-7 | An identity is never reissued, renumbered, or reclaimed on retirement | `id_preservation`, `IL-INF-03`, UGA `RETIRED` |
| I-8 | A subject kind with no plane is a **request to the plane's authority**, not a new plane | `extension_rule.what_this_forbids` |

### 15.2 Rename, move, and retirement

Design §2.3's requirement — *"a rename never produces two CAAR records for one artifact, and
never silently merges two artifacts into one"* — is retained verbatim and is now satisfiable
without a detection heuristic, because the ledger is the arbiter: same `universal_id` under a
new path is a rename; a path with no ledger entry is an admission request; a ledger entry
whose path no longer resolves is `RETIRED` with its identity retained. **The design left
detection unspecified as an implementation decision; the correction removes the decision.**

### 15.3 What this model does not solve

`by_object` is keyed on the repository-relative path today. An identity is stable across
*retirement* (path drops, id kept) but a rename is not distinguishable from a
retire-plus-admit by the ledger alone at this baseline. Design §2.3's three candidate
detection methods therefore still apply — to the *ledger's* rename handling, which is
`UCOS-UGA-001`'s and `REG-AUTO-001`'s concern, not CAAR's. **This is a real, measured
limitation of the corrected model and is disclosed rather than designed around.**

---

## 16. Authority Model

### 16.1 CAAR's own standing

| Property | Value |
|---|---|
| Authority | **NONE.** CAAR is a projection |
| Constitutional superior | `UCKP-LAW-0001`, home `engine/uckp/law.py`, relation `PROJECTION`, binding `00-BOOK/DATA/constitutional-authority-alignment.json` |
| Object model projected | `UCKO` — `engine/uckp/ucko.py`, `UCKP-ART-02` |
| Identity authority | `UCKP-ART-05`, persisted `00-BOOK/DATA/id-ledger.json` — **not CAAR** |
| May create | A view, a vocabulary registration request, an admission request, a divergence report |
| May never create | An identifier, a namespace, a counter, a sequence, a lifecycle axis, an object model, a second definition of any existing primitive |

### 16.2 Per-column authority

| Column | Authority | Where it lives | CAAR's role |
|---|---|---|---|
| Identity | `UCKP-ART-05` / `REG-AUTO-001` / `UCOS-UGA-001` | `id-ledger.json` | **Reader** |
| Class | Vocabulary owner (`UCKP-LAW-0001` pattern) | Registered vocabulary in DATA | **Reader + requester** |
| Authority | The source register per class | 6 registers | **Reader; records `CONTESTED`, never resolves it** |
| Owner | `CEP-OWN-004` (ratified) → GAR → `UCOS-UGA-001` (derived) | §9.1 six-tier | **Resolver, fail-closed** |
| Lifecycle | `UCL-000001` (process) / state-axis owner | `engine/nucleus/lifecycle.py` etc. | **Referencer, never declarer** |
| Visibility | Exclusion register + repaired `R-01` | `exclusion-register.json` | **Reconciler; records mismatch, never corrects** |
| Certification | `CEP-005` chain | `certification.json` + chain | **One-directional supplier** |

**Seven columns, seven authorities, none of them CAAR.** This is the concrete form of §13.1's
claim, and the table is the artifact `CIR-4` and `CAA-INV-02` require.

### 16.3 Owner acts required, before and after correction

| | Readiness Determination §19 | Under this correction |
|---|---|---|
| Schema revision adoption | 1 (mutation governance owner) | 1 (mutation governance owner) — **same act, different content** |
| Identity scheme reconciliation | 1 | **0** — no new scheme to reconcile |
| Lifecycle enum review | 1 (6 vocabularies) | **2 new declarations + 4 extension requests**, routed to existing axis owners |
| Certification vocabulary choice | 1 | 1 (unchanged) + **population scope declarable now, separately** |
| Vocabulary registration | not contemplated | **1 new act** — register `ucos.caar-artifact-class` and its seed terms |

Net: the correction removes one owner act, splits one into routed requests, adds one, and
leaves the rest unchanged. `CIR-1`'s coordination problem (H-06's standing unratified
decision holding the same owner's attention) is **reduced but not removed** — the adoption
act still belongs to the mutation governance owner, and still needs sequencing against H-06.

---

## 17. Migration Impact

### 17.1 Design §10's twelve stages, re-scoped

| Stage | Design action | Impact of correction |
|---|---|---|
| 0 | Freeze schema + minting rule | **CHANGED.** Minting rule withdrawn; schema is the 18 changes in §14; adds vocabulary registration |
| 1 | Repair `_r01_repository_state` (`AV-6`) | **UNCHANGED.** Still the floor. `CIR-6` stands |
| 2 | `ignored_unclassified` live measurement | **UNCHANGED** |
| 3 | Declare precedence for `AAR-1`'s 3 prefixes | **UNCHANGED** |
| 4 | Register `AAR-2`'s 48 ignored paths | **UNCHANGED** |
| 5 | Register 1,468 `00-BOOK` GENERATED paths | **RE-MEASURE FIRST.** UGA already carries 6,145 objects incl. `EXCLUDED_DOCUMENT` (2,620) covering `00-BOOK/PORTAL` (owner `00-BOOK/PORTAL`, 1,240 objects). The GAR gap is real; the *identity* gap this stage assumed is not |
| 6 | Implement `R-09` | **UNCHANGED.** `classify()` still `ERROR` |
| 7 | First CAAR build | **REDUCED.** Extends a running registry rather than composing six from scratch |
| 8 | Validate against gates | **EXTENDED.** 10 gates + `G-C1…G-C4` |
| 9a–9f | Per-class promotion, dual-read | **RE-SCOPED to per-column** (§12.2) |
| 10 | `CEP-005` Art VI + wire certification | **SPLIT.** Vocabulary blocking; population scope declarable independently (§10.3) |
| 11 | Reconcile `CAAR-3`'s three totals | **REPLACED.** Not a reconciliation — a declaration of bounded questions + digests (§10.2). Includes correcting the alignment register's stale 5,789 |

Two stages materially reduce (5, 7), two split or re-scope (9, 10), one is replaced (11),
one changes content (0). **Six of nine "not ready" dimensions were graded against stages that
the correction alters.**

### 17.2 Impact on the nine Step 6 prerequisites (`CIR-9`)

Unchanged in count: **0 of 9 met at this baseline**, re-verified — `assignments: {}`,
`classify()` `ERROR`, 0 of 345 GAR entries under `00-BOOK`, `AAR-1`'s three prefixes
unreconciled. The correction does not meet any prerequisite. It does change what two of them
are for: prerequisites keyed to identity composition (`CAAR-1`/`CAAR-5`) are now keyed to
*column extension*, because the composition question is answered (§2.2).

### 17.3 New migration work the correction introduces

Honesty requires naming what the correction *adds*:

1. **Vocabulary registration** — a new declarative act, with an owner, before first build.
2. **A first-build coverage drop** — §12.3's fail-closed effect, which must be declared in
   advance so it is not read as a regression.
3. **UGA staleness reconciliation** — 117 registry paths untracked at HEAD, 160 tracked
   paths absent from the registry, and the alignment register's 5,789 against a live 6,145.
   Not caused by the correction; **surfaced by it**, and now on CAAR's critical path because
   the corrected architecture reads UGA rather than replacing it.

---

## 18. Implementation Prerequisites

| # | Prerequisite | Authority | Closes / enables |
|---|---|---|---|
| P-1 | Adopt this correction's §13 architecture, §14's 18 schema changes, §15's identity model and §16's authority model as the revised Stage 0 | Mutation governance owner | `CIR-3`, `CIR-4`, `CIR-11`, `CIR-12`; enables all below |
| P-2 | Sequence P-1 explicitly against H-06's standing unratified decision | Mutation governance owner (same role) | `CIR-1` |
| P-3 | Register `ucos.caar-artifact-class` with its seed terms, its bounded question, and its extension path | Vocabulary owner (`UCKP-LAW-0001` pattern) | `CIR-11` (mechanism) |
| P-4 | Route the four lifecycle extension requests and two new declarations to their axis owners | `UCL-000001` owner · `UCOS-UGA-001` · evidence-universe owner | `CIR-5` |
| P-5 | Declare the bounded questions and population digests for every existence figure; correct the alignment register's stale UGA population | Certification owner + `00-BOOK`, jointly | `CIR-7` (population half), `CAAR-3` |
| P-6 | Repair `_r01_repository_state` to consult the exclusion register | Implementation authority | `CIR-6`, `AV-6` — **unchanged floor** |
| P-7 | Meet all nine Step 6 prerequisites, re-verified at implementation time | Per prerequisite | `CIR-9` |
| P-8 | Implement the 10 + 4 gates and run them observationally | Implementation authority | `CIR-8` |
| P-9 | Exercise one deliberate rollback | Implementation authority | `CIR-10` |
| P-10 | Obtain ≥1 ratified ownership assignment to exercise tier 1 | `CEP-OWN-004`'s ratifying authority | `CIR-2` (residual) |
| P-11 | Choose one certification state vocabulary among `AV-5`'s four | Certification authority | `CIR-7` (vocabulary half) |

**P-1 through P-5 have no dependency on any migration stage** — they are declarations and
routings, executable at this baseline. P-6 through P-11 are the residue the correction does
not touch: real repository repair and real owner acts.

---

## 19. Acceptance Criteria

The corrected architecture may be considered adopted, and CAAR implementation authorized to
begin, only when all of the following hold. None holds at this baseline.

**Architecture (P-1 – P-5):**

- [ ] A-1 · No CAAR schema field mints, derives, or hashes an identifier. `G-C1` passes over the whole record set
- [ ] A-2 · Every vocabulary-bound field names its vocabulary; every retained closed set carries `$closure` with a named `closed_by`. `G-C2` passes
- [ ] A-3 · The schema carries `constitutional_superior` (`relation: PROJECTION`) and `object_model` (naming `UCKO`). `CAA-INV-02` and `CAA-INV-07` pass with CAAR bound
- [ ] A-4 · `identity.subject_kind` admits a non-path subject, demonstrated on at least one live `by_observation` entry
- [ ] A-5 · For each axis A1–A5, admitting a synthetic N+1 member touches only declared DATA paths. `G-C3` passes — **extensibility exercised, not asserted**
- [ ] A-6 · `lifecycle` references an axis owner and stores no transition list of its own
- [ ] A-7 · Every existence figure cited by any CAAR-derived claim names a bounded question, an authority, and a population digest

**Repository (P-6 – P-9):**

- [ ] A-8 · `_r01_repository_state` no longer absorbs a declared-excluded or declared-authored path
- [ ] A-9 · 9 of 9 Step 6 prerequisites met, re-verified at implementation time — not assumed from this baseline
- [ ] A-10 · All 14 gates implemented and run at least once observationally
- [ ] A-11 · One rollback exercised deliberately and verified clean
- [ ] A-12 · UGA staleness reconciled: registry population, tracked population, and the alignment register's recorded figure agree, or their disagreement is declared with digests

**Owner acts (P-10 – P-11):**

- [ ] A-13 · ≥1 ratified ownership assignment exists; ownership coverage reports three numbers (ratified / declared / derived), never one
- [ ] A-14 · One certification state vocabulary is canonical among `AV-5`'s four
- [ ] A-15 · No `OBSERVATION_SUBJECT` record carries `may_affect_certification: true`. `G-C4` passes

**15 criteria · 0 met at this baseline.**

---

## 20. CIR Disposition Register

A **correction** changes what a blocker requires. It does not close it. Nothing below is
closed; `Corrected by architecture` means the blocker's remedy is now a declaration in §14
rather than an open design question.

| ID | Severity (was) | Disposition | Where corrected | Residual |
|---|---|---|---|---|
| `CIR-1` | CRITICAL | **REDUCED** | §16.3 | Sequencing against H-06 still an owner act |
| `CIR-2` | HIGH | **DOWNGRADED → MEDIUM** | §9.1 | Tier 1 (ratified) still empty and untestable |
| `CIR-3` | CRITICAL | **CORRECTED BY ARCHITECTURE** | §5, §14 S-01/S-02/S-04 | Adoption (P-1) |
| `CIR-4` | MEDIUM | **CORRECTED — and re-graded HIGH** | §8.1, §14 S-15 | `CAA-INV-02` is fail-closed, not a convention |
| `CIR-5` | HIGH | **CORRECTED BY ARCHITECTURE** | §11, §14 S-10 | 2 declarations + 4 extension requests (P-4) |
| `CIR-6` | CRITICAL | **UNCHANGED** | — | `R-01` repair (P-6) |
| `CIR-7` | HIGH | **REFRAMED — split** | §10.2, §10.3 | Vocabulary half blocking; population half declarable now |
| `CIR-8` | MEDIUM | **UNCHANGED, scope grew** | §14.1 | 10 → 14 gates (P-8) |
| `CIR-9` | HIGH | **UNCHANGED** | §17.2 | 0 of 9 met, re-verified |
| `CIR-10` | LOW | **PREMISE REPAIRED** | §7.1 | Exercise still required (P-9); the claim is now self-consistent |
| `CIR-11` | CRITICAL | **CORRECTED BY ARCHITECTURE** | §3, §4, §14 S-06/S-07/S-17 | Vocabulary registration (P-3) |
| `CIR-12` | CRITICAL | **CORRECTED BY ARCHITECTURE** | §6, §14 S-03 | `by_observation` unpopulated for this use |

**8 corrected or reduced · 1 reframed · 1 downgraded · 4 unchanged · 0 closed.**

### 20.1 New findings raised by this determination

| ID | Finding | Severity |
|---|---|---|
| `ACD-ROOT` | CAAR was designed as a new authority beside the object model, where `extension_rule` requires an extension of it; four of six items in `what_this_forbids` appear in one design | **CRITICAL** |
| `ACD-1` | `CAAR-1`/`CAAR-5`'s composability verdict is falsified: `id-ledger` covers 1,806 of 1,806 of the union population across `by_path` + `by_object`; the join was declared and unread | **CRITICAL** |
| `ACD-2` | Five of CAAR's seven columns are already produced and blocking-gated by `UCOS-UGA-001` over 6,145 objects; no artifact in this chain read it | **HIGH** |
| `ACD-3` | The closed `class` enum violates `UCKP-INV-14` (fail-closed root law); the lawful form of a bounded enum (checked projection of a registered vocabulary) was available and unused | **CRITICAL** |
| `ACD-4` | The path-only identity formula contradicts `$subject_domain`, a rule the design's own source register wrote down against exactly this error | **CRITICAL** |
| `ACD-5` | UGA is stale at HEAD: 117 registered paths untracked, 160 tracked paths unregistered, and the alignment register records 5,789 against a live 6,145 — `AAT-4`'s drift, third occurrence | **HIGH** |
| `ACD-6` | `evidence_class`, `evidence_boundary` and `certification_status` each hold one distinct value across all 6,145 UGA entries — gate 8.4's defect, present in the registry CAAR would extend | **MEDIUM** |
| `ACD-7` | CAAR's six class values conflate provenance and disposition, two axes the repository keeps separate; the class axis needs a declared bounded question | **MEDIUM** |

**8 raised · 0 resolved.** BC-6's 26 and `CIR-1`…`CIR-12` remain open and unaffected except
as dispositioned above.

---

## 21. Verification

| Check | Result |
|---|---|
| Artifact exists | ✅ `UCOS-OMEGA-INFINITY-CAAR-ARCHITECTURE-CORRECTION-DETERMINATION.md` |
| Line count | ✅ **1,323** |
| Required sections — current CAAR defects | ✅ §2 (`ACD-ROOT`, `ACD-1`…`ACD-4`, §2.6 re-derivation) |
| Required sections — the ten redesign areas | ✅ §3 closed vocabulary · §4 infinite extensibility · §5 universal identity · §6 non-file object identity · §7 representation independence · §8 registry authority · §9 ownership · §10 certification · §11 lifecycle · §12 backward compatibility |
| Required sections — corrected target architecture | ✅ §13 |
| Required sections — schema changes required | ✅ §14 (18 changes + 4 gates) |
| Required sections — identity model | ✅ §15 (I-1…I-8, incl. §15.3 disclosed limitation) |
| Required sections — authority model | ✅ §16 (per-column table, owner-act delta) |
| Required sections — migration impact | ✅ §17 |
| Required sections — implementation prerequisites | ✅ §18 (P-1…P-11) |
| Required sections — acceptance criteria | ✅ §19 (A-1…A-15) |
| All CIR-1…CIR-12 addressed | ✅ §20, each with a disposition and a residual |
| HEAD unchanged | ✅ `bae59755d7e2d3566c93b89c722b68847145269a` |
| Branch unchanged | ✅ `integration/recovery-001` |
| Analysis/design only — implementation performed | ✅ **0** |
| Code changes | ✅ **0** — `uga_engine.py`, `vocabulary.py`, `law.py`, `verify.sh` read, none written |
| Registry changes | ✅ **0** — `id-ledger.json`, `artifacts.json`, GAR, `mutation-governance-boundary.json`, `constitutional-authority-alignment.json`, UGA registries read, none written |
| Vocabulary / identity / class / owner / lifecycle created | ✅ **0** — every one proposed, none registered |
| Certification changes | ✅ **0** |
| Commits | ✅ **0** |
| Tracked modifications unchanged | ✅ 38 modified — identical set to session start |
| Only one new artifact | ✅ the single delta is this file (untracked count 308 → 309) |
| Findings closed | ✅ **0** — 12 dispositioned, 8 newly raised, none closed |

### 21.1 Measurement provenance

Every quantity in this determination was computed at this baseline, not carried forward:

```
id-ledger by_path / by_object / by_observation      1,492 / 4,914 / 7
artifacts.json entries                              1,461
generated-artifact-registry.json entries              345
artifacts.path ∩ by_path                            1,461  (100%)
GAR.canonical_path ∩ by_object                        345  (100%)
(artifacts ∪ GAR) ∩ (by_path ∪ by_object)          1,806 of 1,806  (100%)
UGA object registry entries                         6,145
  distinct object_class / owner / producer          7 / 276 / 33
  distinct lifecycle                                2 (of 3 declared)
  distinct evidence_class / cert_status             1 / 1
  DOCUMENT_ARTIFACT                                 1,233
git ls-files                                        6,188
UGA paths ∩ tracked                                 6,028
uckp.governed-category terms                           35
mutation classes (grown from 5)                         9
AUTH-INF-001 rules / interpretive laws              12 / 8
CAA alignment invariants (all fail-closed)              7
git status: modified / untracked / total            38 / 308 / 346
  (untracked after this artifact's creation)          309
this artifact, lines                                1,323
```

---

*This determination modified no file, changed no code or configuration, wrote to no
registry, altered no certification, committed nothing, registered no vocabulary term, minted
no identifier, and adopted no architecture. It corrects a design; adoption of the correction
is `P-1`, and belongs to the mutation governance owner, not to this artifact. Its central
finding is that ten of the twelve `CIR` blockers are consequences of one architectural
decision — building CAAR as a new authority beside the Universal Constitutional Object Model
where `extension_rule` requires an extension of it — and that the three things the design
proposed to invent (an identity scheme, a class vocabulary mechanism, a non-path subject
model) each already exist in this repository, live, gated, and measured: `id-ledger.json`'s
three planes covering 1,806 of 1,806 of the disputed population, `engine/uckp/vocabulary.py`'s
register-then-use openness, and `by_observation`'s composite non-path key. Eight new findings
(`ACD-ROOT`, `ACD-1`…`ACD-7`) are raised. Twelve blockers are dispositioned; **none is
closed**, because a correction is not a repair and this artifact holds no authority to
perform one. The single repository mutation is the creation of this file.*

**END DETERMINATION — CAAR ARCHITECTURE CORRECTION ISSUED · NOT ADOPTED · NO BLOCKER CLOSED · STOPPED AFTER ARTIFACT CREATION.**
