# Output 2 — Decision Family **GDR-B** · Ownership Allocation and Consolidation Mapping

> **STATUS DOMAIN:** GOVERNANCE (determination) · **STATUS BASIS:** located ownership records reproduced by `UCCEP-000007` Output 9, and the located clauses of `CMG-000001` Articles XV/XVII/XX/LII/LVII and `GOV-INT-001` §2.14

| Field | Value |
|---|---|
| PROGRAMME | `UCCEP-000008` · OUTPUT 2 |
| FAMILY | **GDR-B** — Ownership Allocation and Consolidation Mapping |
| DECISIONS | `GD-05` (DDI-02) · `GD-06` (DDI-03) · `GD-07` (DDI-14) · `GD-08` (DDI-15 — **HELD**) |
| FAMILY SUBJECT | Which ownership rows the consolidation adds or changes; which programmes map onto which canonical owner; where the consolidation determination is authored; and the disagreement among located ownership records. |
| AUTHORITY | None of its own. `GD-05`–`GD-07` are rendered within the located Owner's declared law; `GD-08` is **not decided** and is routed to its owners (Output 0 §2 clause 3, §5). |
| DISCLOSURE | `CERTIFIED-PROVISIONAL`; Tier T1 VACANT; every determination PROVISIONAL under `CMG-L-12` (condition **C-3**, constraint **K-09**). |

---

## GD-05 — Ownership matrix rows

| Field | Record |
|---|---|
| **Decision ID** | `GD-05` |
| **Title** | Which ownership rows the consolidation adds or changes, and their canonical owners |
| **Resolves** | `DDI-02` |
| **Family** | GDR-B |

### Problem Statement

`UCCEP-000007` Output 16 records that the located ownership records are reproduced in Output 9, but **which rows the consolidation adds or changes is nowhere recorded**. `CMG-000001` XX.7 provides that where such records disagree, the disagreement is a finding for the concern owner — never for a measuring instrument — so measurement could not settle it either.

### Repository Evidence

| Evidence | What it establishes | Located at |
|---|---|---|
| Canonical Ownership Matrix — single canonical owner per concept domain; `duplicate_canonical_homes = 0`, `orphan_concepts = 0` | Concept-level ownership is total and unambiguous | `/02-CANONICAL-OWNERSHIP-MATRIX.md` *(repository root)* |
| `CMG-REGISTRY.json → concerns[]` — **60 concerns**: 49 delegated (`CMG-DLG-01…49`, disposition REUSE) + 11 retained (`CMG-RET-01…11`, RETAIN); **0 concerns with more than one owner** (`CMG-INV-02` holds); 0 findings from the meta-constitutional gate | Concern-level ownership is total, single-valued and gate-verified | `00-CMG/CMG-REGISTRY.json` |
| `artifacts.json[*].owner` over **1,199** artifacts | Artifact-level ownership is total | `00-BOOK/DATA/artifacts.json` |
| Canonical-home register — concept → canonical home | Concept homing is total | `00-MASTER/UAKOS-CLOSURE-002/` outputs |
| Session-start closure line: `UAKOS-CLOSURE-002: CLOSED | concepts=434 | gaps=0` with `not_homed_concepts 0`, `orphan_concepts 0`, `duplicate_canonical_homes 0`, `in_repo_unhomed 0` | No unowned or doubly-owned concept exists to allocate | `00-MASTER/UAKOS-CLOSURE-002/` |
| Architectural Decision Assimilation Matrix — integration method per decision (REUSE/EXTEND/MERGE/REFERENCE/NEW) | The located mechanism for recording *how* a decision integrates, without changing ownership | `/03-ARCHITECTURAL-DECISION-ASSIMILATION-MATRIX.md` |
| `CMG-000001` XX.7 — *"those records ARE the located ownership facts. This instrument SHALL consume them and SHALL NOT restate them."* | Ownership is consumed, never restated | `00-CMG/CMG-000001-…md` |

### Constitutional Authority

**`CMG-000001`** — sole canonical owner for this decision, by Article XV (the Constitution Registry) and Article XX (ownership consumption and disagreement routing). Resolution terminates at XVII.2 Step 1. `CEP-002` 7.2 / 14.2 (Governance Authority assigns and registers owners by governed determination) and 14.3 (duplication is a finding) are cited as the constraints on any future row change.

### Decision

**The consolidation ADDS NO OWNERSHIP ROW and CHANGES NO CANONICAL OWNER.**

The four located records — `/02-CANONICAL-OWNERSHIP-MATRIX.md`, `CMG-REGISTRY.json → concerns[]` (60 concerns: 49 delegated, 11 retained), `artifacts.json[*].owner` (1,199 artifacts), and the canonical-home register of `UAKOS-CLOSURE-002` — **ARE** the ownership facts of the consolidation, unamended and unextended.

Three corollaries are bound:

1. **The consolidation owns no concern.** It is not admitted to `CMG-REGISTRY.json → concerns[]` as an Owner, and neither is `UCCEP-000008`.
2. **Where consolidation touches a concern, it acts through that concern's located Owner** — by citing the Owner's clause (recognition), by invoking the Owner's prohibition (rejection), or by registering work to the Owner (work package). It never acts beside the Owner.
3. **Any future row change is reserved.** Adding or changing an ownership row is an act of Governance Authority by governed determination under `CEP-002` 7.2 / 14.2, requiring the admission procedure of `CMG-000001` LXXVI.2. No such act is performed or authorized here.

### Rationale

The premise of the question — that a consolidation must re-allocate ownership — is not borne out by Repository Truth. Ownership is measured **total** at every level: 0 concerns with more than one owner, 0 orphan concepts, 0 unhomed concepts, 0 duplicate canonical homes, `owner` present on all 1,199 artifacts. There is no unowned concern for the consolidation to claim and no doubly-owned concern for it to arbitrate.

Adding a row would therefore have to *displace* an existing owner. That is barred three ways: `CMG-INV-02` (which the gate currently verifies holds) forbids parallel authority; `CEP-002` 14.3 makes two owners for one subject a duplication finding; and `CMG-000001` XX.7 reserves any resulting disagreement to the affected concern's owner, *"never by this instrument"* — a reservation this programme is equally bound by.

The lawful content of the decision is thus the **explicit nil return**, recorded so that it cannot later be mistaken for an omission. Output 16 recorded the absence of a row list; this records that the correct row list is empty, with the reason.

`GD-05` deliberately does **not** address the disagreement `DG-6` records among those same located records. That is `GD-08`, and it is held, not decided. Recognizing the records as the ownership facts does not adjudicate a contradiction *within* them.

### Dependencies

| Direction | Item | Nature |
|---|---|---|
| Depends on | `GD-11` | The admission default (EXTEND over CREATE) is why no new owner is admitted |
| Depends on | `GD-21` / `DEF-02` | Registry standing is PROVISIONAL while T1 is vacant; this recognition inherits that |
| Strictly separated from | `GD-08` / `DEF-01` | `GD-05` recognizes the records; `GD-08` holds their internal disagreement. Neither resolves the other. |
| Depended on by | `GD-06` | Identity mapping presupposes no owner is displaced |
| Depended on by | `GD-07` | The authoring locus is itself resolved by concern lookup against these records |

### Affected Programmes

All 45 measured programme directories, in the negative sense: none gains or loses ownership of anything. `UAKOS-CLOSURE-002` is cited as the canonical-home register and is not edited.

### Affected Registries

None mutated. `CMG-REGISTRY.json`, `artifacts.json`, `/02-CANONICAL-OWNERSHIP-MATRIX.md`, `/03-ARCHITECTURAL-DECISION-ASSIMILATION-MATRIX.md` are all read as evidence. `00-CMG/` is boundary **X-3**; `00-BOOK/DATA/*` is append-only under **X-5**; neither is touched.

### Affected Constitutions

None amended. `CMG-000001` XV / XVII.2 / XX and `CEP-002` 7.2/14.2/14.3 are cited.

### Affected Implementations

None. No engine, no `config.py` declaration, no schema.

### Constraints

| Id | Constraint |
|---|---|
| `GD-05-C1` | No consolidation artifact SHALL declare itself, or any consolidation programme, the Owner of a concern. |
| `GD-05-C2` | A consolidation act requiring an ownership change SHALL halt and route to Governance Authority under `CEP-002` 7.2/14.2 and `CMG-000001` LXXVI.2; it SHALL NOT proceed on an inferred owner. |
| `GD-05-C3` | The located ownership records SHALL be consumed, never restated, in consolidation artifacts (`CMG-000001` XX.7). A consolidation artifact that copies an ownership table creates a second ownership record and is void to that extent. |
| `GD-05-C4` | This decision SHALL NOT be cited as resolving, narrowing, or prejudging `DG-6` / `GD-08` / `DEF-01`. |

### Acceptance Criteria

1. `CMG-REGISTRY.json → concerns[]` contains **60** entries with the same owners before and after the consolidation, unless changed by a separate Governance Authority determination that cites `GD-05-C2`.
2. `duplicate_canonical_homes`, `orphan_concepts`, `not_homed_concepts` remain **0**; `CMG-INV-02` continues to hold with 0 concerns having more than one owner.
3. No consolidation artifact appears as an Owner in any located ownership record.
4. No consolidation artifact restates an ownership table.

### Traceability

`DDI-02` → `GD-05`. Upstream: Output 16 §2 row DDI-02; `UCCEP-000007/09-OWNERSHIP-INVENTORY.md` §1–§4. Authority chain: `CMG-000001` XVII.2 → Articles XV / XX → the four located records. Onward: `08-DISPOSITION-ROUTING-TABLE.md` row `GD-05`; separation from `07-DEFERRAL-ENTRIES.md` `DEF-01`.

### Future Impact

Fixes that consolidation is **ownership-neutral**. Every later step must find an existing owner or halt, which prevents the classic consolidation failure of accreting a coordinating authority that shadows the real owners. It also preserves the gate-verified invariants (`CMG-INV-02`, zero duplicate homes) that any later certification claim depends on.

### Disposition

**`CEP-002` 28.13(b) — REPRESENTED BY AN EXISTING CANONICAL CAPABILITY.**
Single canonical owner: **`CMG-000001`** (`00-CMG/CMG-000001-CONSTITUTIONAL-META-GOVERNANCE-CONSTITUTION.md`, Articles XV and XX), whose located artifact is the Registry projection `00-CMG/CMG-REGISTRY.json`. Evidence: the four located ownership records above. No realization required; stage reached is REPOSITORY MAPPING.

---

## GD-06 — Consolidation mapping

| Field | Record |
|---|---|
| **Decision ID** | `GD-06` |
| **Title** | Which programmes and trackers map onto which canonical owner |
| **Resolves** | `DDI-03` |
| **Family** | GDR-B |

### Problem Statement

Output 16 records that **no artifact records a source→target mapping**: Output 2 measures 45 programme directories and Output 4 measures the register set, and the mapping between them is a decision, not a measurement.

### Repository Evidence

| Evidence | What it establishes | Located at |
|---|---|---|
| Output 2 §1 — **45 directories, 646 tracked files**, enumerated with per-directory tracked-file counts | The exact source population | `00-MASTER/UCCEP-000007/02-PROGRAMME-INVENTORY.md` |
| Output 2 §1 — `00-MASTER/` is excluded from corpus registration by `config.py :: EXCLUDE_DIR_PREFIXES` per the exclusion determination, *"so nothing below holds a registered corpus identity"* | The source population holds **no registered identity**, so there is no register row to re-point | same; `00-BOOK/tools/config.py`; `00-MASTER/UCOS-RECON-C1-OPERATIONAL-MEMORY-EXCLUSION.md` |
| Output 2 §4 — the `UCCEP-000000` roster: **16/16 PASS**, 4 PASS-WITH-ADVISORY | The programme roster is already aggregated by its located owner | `00-MASTER/UCCEP-000007/02-PROGRAMME-INVENTORY.md`; `00-MASTER/UCCEP-000000/uccep.json → programs[]` |
| `GOV-INT-001` §2.14 — *"UCI-001 is authored **once** and inherited … **by reference** (a program/phase cites UCI-001; it does not copy it). This is the mechanism that satisfies 'no duplicate governance.'"* | The located mechanism for relating programmes to a canonical owner: reference, not relocation | `00-BOOK/CONTROL-TOWER/UCOS-Ω∞-GOV-INT-001-…md` |
| `REG-AUTO-001` P4 — identity *"allocated once and never reused, renumbered, or reordered"*; L5 — append-only correction, *"never by editing frozen artifacts, renumbering, or rewriting history"* | Relocation of a registered artifact is barred | `00-BOOK/CONTROL-TOWER/UCOS-Ω∞-REG-AUTO-001-…md` |
| Output 7 §3 — each programme engine writes only within its own directory, under a fail-closed write-scope guard | Programme homes are mechanically enforced boundaries | `00-MASTER/UCCEP-000007/07-GENERATED-ARTIFACT-INVENTORY.md` |
| Boundary **X-9** — *"No cross-programme edits."* | Folding one programme into another is outside any authorization | `00-MASTER/UCCEP-000006/06-IMPLEMENTATION-BOUNDARY-SPECIFICATION.md` §2 |

### Constitutional Authority

**`GOV-INT-001`** (`CMG-DLG-16`) §2.14 — sole canonical owner, as the instrument that owns the inheritance/integration mechanism. Constraints cited: `REG-AUTO-001` P4/L5 (`CMG-DLG-13`), boundary **X-9**, and `CMG-000001` XX.7 (each mapped concern's owner concurs through its own clause, not through this programme).

### Decision

**The consolidation mapping is IDENTITY. No programme is folded into another, renamed, moved, re-homed, or retired.**

Concretely:

1. **Each of the 45 measured programme directories retains its own operational-memory home** under `00-MASTER/<PROGRAMME-ID>/`, and each remains the sole writer of its own outputs.
2. **Each programme maps to the located Owner of every concern it touches, by reference** — it cites the Owner; it does not copy the Owner, absorb the Owner, or stand between the Owner and the corpus (`GOV-INT-001` §2.14).
3. **Aggregation, where required, is already located**: `UCCEP-000000`'s roster (`uccep.json → programs[]`, 16/16) is the programme-level aggregation and is not duplicated. The register set is aggregated by `REG-AUTO-001`'s transaction `T`. Neither is re-pointed.
4. **Therefore no source→target mapping table exists to author**, beyond the identity mapping recorded above, and no such table SHALL be authored — one would be a second ownership record barred by `GD-05-C3`.

### Rationale

Two located facts collapse the question.

First, **there is nothing to re-point.** `00-MASTER/` is outside registration scope, so no directory in the source population holds a registered corpus identity, and no register row names it. A source→target mapping presupposes rows that resolve to identities; here there are none. Any mapping table would therefore be a *new* record of relationships that no register consumes — inert at best, a competing ownership claim at worst.

Second, **relocation is barred for anything that does hold an identity.** `REG-AUTO-001` P4 forbids renumbering or reordering identity; L5 forbids repair by renaming or history rewrite; **X-9** forbids editing another programme's outputs at all. So the only lawful consolidation of registered artifacts is by reference, which is exactly the mechanism `GOV-INT-001` §2.14 declares and names as *"the mechanism that satisfies 'no duplicate governance.'"*

The decision consequently records consolidation-by-reference as the mapping, and the identity mapping as its extension. This is the substantive answer, not an evasion: it determines that the consolidation's unit of work is a **citation**, not a **move** — which is what makes `GD-13` (no deletion) and `GD-14` (no migration) coherent rather than merely restrictive.

### Dependencies

| Direction | Item | Nature |
|---|---|---|
| Depends on | `GD-05` | No owner is displaced, so no target exists to map onto other than the located Owner |
| Depends on | `GD-09` | Binding by reference is the mechanism this mapping uses |
| Depends on | `GD-03` | Each engine keeps its own write scope, so each home is preserved |
| Depended on by | `GD-14` | "Nothing moves" is the premise of the migration-sequence rejection |
| Depended on by | `GD-13` | Identity mapping is what makes append-only sufficient |
| Depended on by | `GD-18` | Programme lineage numbering presupposes homes are stable and forward-only |

### Affected Programmes

All 45 measured directories — each confirmed in place. `UCCEP-000000` retains roster aggregation. `UCCEP-000005`, `UCDA-000001`, `UAKOS-*`, `UCOS-USIS-*` and every other programme are unchanged. `UCCEP-000008` is added as a **new** home under P-5, not as a target for any existing programme's content.

### Affected Registries

None mutated. The register set is read via Output 4. `id-ledger.json` (**X-4**) is untouched: no identity is allocated, reused or renumbered.

### Affected Constitutions

None amended. `GOV-INT-001` §2.14, `REG-AUTO-001` P4/L5 cited.

### Affected Implementations

None. `config.py`'s exclusion prefixes are read as evidence, not modified.

### Constraints

| Id | Constraint |
|---|---|
| `GD-06-C1` | No consolidation act SHALL move, rename, re-home, fold, or retire a programme directory or a registered artifact. |
| `GD-06-C2` | No consolidation act SHALL author a source→target mapping table; consolidation is expressed as citations from a programme to a located Owner. |
| `GD-06-C3` | A programme SHALL cite an Owner, never copy it (`GOV-INT-001` §2.14). A copied Owner clause in a consolidation artifact is duplicate governance and is void to that extent. |
| `GD-06-C4` | Cross-programme edits remain outside the boundary (**X-9**), including edits presented as consolidation. |

### Acceptance Criteria

1. The 45 programme directories measured by Output 2 §1 are all present, with the same names, at any later HEAD — plus `UCCEP-000008`, and plus any future programme created forward-only under `GD-18`.
2. No `git mv`, rename, or deletion of a programme directory appears in the consolidation's history.
3. `id-ledger.json` shows no reused, renumbered, or reordered identity.
4. No consolidation artifact contains a source→target programme mapping table.
5. Each consolidation artifact that invokes an Owner does so by citation, verifiable by the presence of the Owner's path and clause reference.

### Traceability

`DDI-03` → `GD-06`. Upstream: Output 16 §2 row DDI-03; `UCCEP-000007/02-PROGRAMME-INVENTORY.md` §1/§4/§5; `UCCEP-000007/04-REGISTRY-INVENTORY.md` §4; `UCCEP-000007/07-GENERATED-ARTIFACT-INVENTORY.md` §2–§3. Authority chain: `CMG-000001` XVII.2 → `CMG-DLG-16` → `GOV-INT-001` §2.14; constraints `REG-AUTO-001` P4/L5, **X-9**. Onward: `08-DISPOSITION-ROUTING-TABLE.md` row `GD-06`; premise of `GD-14`.

### Future Impact

Determines the **shape of consolidation for all later missions**: additive citation rather than structural rearrangement. This is why the rollback anchor stays meaningful — no history is rewritten, so recovery is a checkout rather than a reconstruction. It also means the consolidation's completeness is testable by counting citations, not by auditing moves.

### Disposition

**`CEP-002` 28.13(b) — REPRESENTED BY AN EXISTING CANONICAL CAPABILITY.**
Single canonical owner: **`GOV-INT-001`** (`00-BOOK/CONTROL-TOWER/UCOS-Ω∞-GOV-INT-001-…-DETERMINATION.md` §2.14). Evidence: §2.14; Output 2 §1/§4; `config.py` exclusion; the exclusion determination; `REG-AUTO-001` P4/L5. No realization required; stage reached is REPOSITORY MAPPING.

---

## GD-07 — Authoring locus and form of the consolidation determination

| Field | Record |
|---|---|
| **Decision ID** | `GD-07` |
| **Title** | Where the consolidation determination is authored, and in what form |
| **Resolves** | `DDI-14` |
| **Family** | GDR-B |

### Problem Statement

Output 16 records DDI-14 as **half-resolved**: location authority *was* resolvable from Repository Truth and was resolved by concern lookup to `GOV-INT-001` (`CMG-DLG-16`, disposition REUSE), terminating at `CMG-000001` XVII.2 Step 1. *"The **content** is not, which is why DDI-01…13 remain open."* What remained undetermined is the **form** the content takes, and whether authoring it requires amending `GOV-INT-001` or creating a new instrument.

### Repository Evidence

| Evidence | What it establishes | Located at |
|---|---|---|
| `CMG-REGISTRY.json → concerns[]` `CMG-DLG-16`, owner `GOV-INT-001`, disposition REUSE, basis *"GOV-INT-001 §2.3"* | Exactly one Owner; lookup terminates at Step 1 | `00-CMG/CMG-REGISTRY.json` |
| Output 16 §3 row DDI-14 — location authority *"resolved"*; content *"not"* | The residual question is form, not locus | `00-MASTER/UCCEP-000007/16-DECISION-DERIVED-INPUTS.md` |
| `CMG-000001` LXXVI.2(c) — *"EXTEND IS the default; CREATE requires the recorded discovery of (a)"* | The admission disposition rule for new artifacts | `00-CMG/CMG-000001-…md` |
| Output 16 §1 — exhaustive enumeration of every candidate host with **0 hits**; `00-MASTER/UCCEP-000001…000004` absent | The recorded discovery LXXVI.2(a) requires | same as Output 16 |
| `REG-AUTO-001` §21 — an open constitutional question (`CMG-OQ-06`) answered by **appending a new SECTION to the Owner instrument**, closing the question with *"NO amendment of any located registration or classification instrument is required"* and zero new machinery | The located precedent form for rendering a referred determination | `00-BOOK/CONTROL-TOWER/UCOS-Ω∞-REG-AUTO-001-…md` |
| `GOV-INT-001` §7.2 — the located precedent form for an implementation sequence | The Owner's own form vocabulary | `00-BOOK/CONTROL-TOWER/UCOS-Ω∞-GOV-INT-001-…md` |
| `GOV-INT-001` front matter: `AUTHORITY = NONE (decides architecture; ratifies nothing; authorizes no EC-series step)`; `CMG-REGISTRY.json` records it `CMG-K-17` (Determination, *Decisional* binding), state PROVISIONAL, v1.0 | Its standing and kind, which any authored content inherits | both |
| `CEP-009` V.1 — *"An artifact SHALL be eligible for amendment only when it is ratified or frozen"* | `GOV-INT-001`, being PROVISIONAL and unratified, is **not amendment-eligible**; so amendment is not an available form | `00-CEP/CEP-009-…md` |
| Boundary **P-5** — programme-owned outputs under `00-MASTER/<PROGRAMME-ID>/` | The authorized location for programme-authored determinations | `00-MASTER/UCCEP-000006/06-IMPLEMENTATION-BOUNDARY-SPECIFICATION.md` §1 |

### Constitutional Authority

**`GOV-INT-001`** (`CMG-DLG-16`) as the located locus authority, already resolved. Form is governed by `CMG-000001` LXXVI.2(a)/(c) (admission), `CEP-009` V.1 (amendment eligibility), and boundary **P-5** (authorized output location).

### Decision

**Locus is affirmed as already resolved: `GOV-INT-001` (`CMG-DLG-16`) is the authority for the consolidation determination, and no other instrument competes for it.**

**Form is determined as follows:** the determination is rendered as a **family of governance determinations recorded under `00-MASTER/UCCEP-000008/`**, each decision citing the located Owner clause that governs it, and each taking one of the three lawful shapes of Output 0 §2 — recognition, rejection, or registration of work.

Three consequences are bound:

1. **`GOV-INT-001` is NOT amended, and no new constitutional instrument is created.** Amendment is unavailable in any case: `CEP-009` V.1 makes only ratified or frozen artifacts amendment-eligible, and `GOV-INT-001` is recorded PROVISIONAL and unratified.
2. **No new law is authored.** Because every decision is a recognition, a rejection on cited grounds, or a registration of work, the family creates no rule that its citing Owner has not already declared. This is what makes authoring it lawful without occupying `CMG-DLG-16`.
3. **The determinations carry `GOV-INT-001`'s standing, not a higher one.** They are decisional in character (the kind `CMG-REGISTRY.json` records for `GOV-INT-001` is `CMG-K-17`), they ratify nothing, and they are PROVISIONAL under `CMG-L-12` while T1 is vacant.

### Rationale

The residual question is whether the content can be authored at all without either amending the Owner or creating a rival instrument. Repository Truth supplies a precedent that answers it: `REG-AUTO-001` §21 disposed a referred open question by **appending a determination section** and expressly concluding that *no amendment of any located instrument is required* — recognition achieved without editing shared machinery. This programme takes the same shape, differing only in location, and it differs there for two located reasons: `GOV-INT-001` is not amendment-eligible under `CEP-009` V.1, and **P-5** already designates `00-MASTER/<PROGRAMME-ID>/` as the authorized home for programme-authored determinations.

Creating the artifacts is consistent with `GD-11`'s no-new-documents policy because LXXVI.2(c)'s condition is satisfied, not bypassed: CREATE requires the recorded discovery of LXXVI.2(a), and Output 16 §1 **is** that discovery — every candidate host enumerated and searched, 0 hits, with `00-MASTER/UCCEP-000001…000004` recorded absent. Extending an existing host was examined and is insufficient: `UCCEP-000007` declares itself *"Not a determination … Not a governance decision"*, and editing it or any other programme's outputs is barred by **X-9**.

### Dependencies

| Direction | Item | Nature |
|---|---|---|
| Depends on | `GD-11` | Supplies the admission rule this decision satisfies |
| Depends on | `GD-05` | The family owns no concern; it cites Owners |
| Depends on | `GD-18` | Supplies the basis for the identifier `UCCEP-000008` |
| Depended on by | `GD-01` … `GD-21` | Every decision in the register depends on this form being lawful |
| Blocks | nothing | No realization required |

### Affected Programmes

`UCCEP-000008` (constituted as the recording home) · `UCCEP-000007` (cited as input, not edited) · `UCCEP-000006` (cited for **P-5** and boundaries, not edited).

### Affected Registries

None. `00-MASTER/` is outside registration scope, so these outputs allocate no identity, appear in no register, and cause no register drift.

### Affected Constitutions

**None amended — explicitly including `GOV-INT-001`.** `CMG-000001` LXXVI.2 and `CEP-009` V.1 are cited.

### Affected Implementations

None.

### Constraints

| Id | Constraint |
|---|---|
| `GD-07-C1` | No output of this family SHALL be presented as an amendment, extension, successor, or replacement of `GOV-INT-001`, nor of any `00-CEP/` or `00-CMG/` instrument. |
| `GD-07-C2` | No output of this family SHALL declare a standing higher than `GOV-INT-001`'s recorded standing (`CMG-K-17`, PROVISIONAL) — `CMG-L-12`. |
| `GD-07-C3` | Every decision SHALL cite the located Owner clause it rests on. A decision without such a citation is not a decision of this family and is void to that extent. |
| `GD-07-C4` | This family SHALL NOT be cited as constitutional authority by any other artifact; it is a record of determinations, not an instrument. |

### Acceptance Criteria

1. `git diff` for this programme's commit touches **only** paths under `00-MASTER/UCCEP-000008/`.
2. `00-BOOK/CONTROL-TOWER/UCOS-Ω∞-GOV-INT-001-…md` is byte-identical before and after.
3. `00-CEP/**` and `00-CMG/**` are byte-identical before and after (**X-2**, **X-3**).
4. Every `GD-nn` carries a `Constitutional Authority` field naming a located Owner and clause.
5. Every `GD-nn` carries the provisional disclosure required by condition **C-3** / constraint **K-09**.

### Traceability

`DDI-14` → `GD-07`. Upstream: Output 16 §3 row DDI-14 and §1 (the recorded discovery); `UCCEP-000007/00-DISCOVERY-INDEX.md` (P-5 citation, and the declaration that the programme is not a determination). Authority chain: `CMG-000001` XVII.2 → `CMG-DLG-16` → `GOV-INT-001`; form from `CMG-000001` LXXVI.2, `CEP-009` V.1, **P-5**; precedent `REG-AUTO-001` §21. Onward: governs the form of every other output of this programme.

### Future Impact

Establishes the reusable form for every later consolidation determination: recorded under the programme's own home, citing located Owners, creating no law, claiming no tier. It also records why amendment of the control-tower determinations is currently unavailable — `CEP-009` V.1 plus the T1 vacancy — which is a standing constraint on all future governance work and is carried forward as a gap in `10-REMAINING-GOVERNANCE-GAPS.md`.

### Disposition

**`CEP-002` 28.13(b) — REPRESENTED BY AN EXISTING CANONICAL CAPABILITY.**
Single canonical owner: **`GOV-INT-001`** (`CMG-DLG-16`), whose ownership of the locus was already resolved by concern lookup and is affirmed, not created, here. Evidence: `CMG-REGISTRY.json → concerns[] CMG-DLG-16`; Output 16 §3 row DDI-14; `CMG-000001` LXXVI.2; `CEP-009` V.1; **P-5**. No realization required; stage reached is REPOSITORY MAPPING.

---

## GD-08 — The `AUTHORITY = NONE` versus Registry-Owner tension · **HELD, NOT DECIDED**

| Field | Record |
|---|---|
| **Decision ID** | `GD-08` |
| **Title** | Disposition of the `AUTHORITY = NONE` vs Registry-Owner tension (DG-6) |
| **Resolves** | `DDI-15` — **by holding**, under `CMG-000001` XX.7, LII.3 and LVII.3 |
| **Family** | GDR-B |
| **Deferral entry** | `DEF-01` (`07-DEFERRAL-ENTRIES.md`) |

### Problem Statement

Four Registry Owners declare `AUTHORITY = NONE`, which `CMG-000001` XX.8 states may not appear as an Owner. Output 16 records the owning authority as *"the owner of each affected concern, per `CMG-000001` XX.7 and Article LII — explicitly **'never by this instrument'** and, by the same reasoning, never by a measuring programme"*, and records why measurement cannot settle it: *"A disagreement among located ownership records is a finding for disposition, not a fact to be measured true or false."*

### Repository Evidence

| Evidence | What it establishes | Located at |
|---|---|---|
| `DG-6` verbatim: *"Four Registry Owners declare `AUTHORITY = NONE`, which `CMG-000001` XX.8 states may not appear as an Owner: `STATUS-001`, `REG-AUTO-001`, `UCI-001`, `GOV-INT-001`"*; measured state *"disagreement among located records"*; owning authority *"per XX.7 / Article LII: **the owner of the affected concern**, never `CMG-000001` and never this programme"* | The finding, its members, and its reserved disposition | `00-MASTER/UCCEP-000007/13-KNOWN-GAPS.md` §2 |
| `CMG-000001` XX.8 — *"The repository's `AUTHORITY = NONE (DERIVED TRUTH)` convention SHALL be read as declaring **no ownership** … A derived-truth artifact owns no concern and SHALL NOT appear as an Owner in the Registry."* | One side of the disagreement | `00-CMG/CMG-000001-…md` |
| `CMG-REGISTRY.json → concerns[]` — `CMG-DLG-13` owner `REG-AUTO-001`; `CMG-DLG-14` owner `STATUS-001`; `CMG-DLG-15` owner `UCI-001`; `CMG-DLG-16` owner `GOV-INT-001` | The other side: four such Owners are recorded | `00-CMG/CMG-REGISTRY.json` |
| Each of the four instruments' own front matter declaring `AUTHORITY = NONE` | The declarations are real, not inferred | `00-BOOK/CONTROL-TOWER/UCOS-Ω∞-{STATUS-001,REG-AUTO-001,UCI-001,GOV-INT-001}-…md` |
| `CMG-000001` XX.7 — the disagreement *"IS a finding under Article LII and SHALL be disposed by the owner of the affected concern, never by this instrument"* | The reserved disposition route | `00-CMG/CMG-000001-…md` |
| `CMG-000001` LII.3 — *"Audit SHALL be **read-only**. It SHALL emit findings and SHALL decide nothing. Disposition rests with the owner of the affected concern"*; LII.6 — *"An undispositioned finding SHALL block certification under Article LXXX."* | Read-only detection; and the consequence of leaving it undisposed | same |
| `CMG-000001` LVII.3 — a genuine contradiction *"SHALL be recorded as an **open constitutional question** … It SHALL NOT be decided by default, by the detector, by the most convenient authority, or by silence."* | Holding is the lawful response | same |
| `CMG-000001` XV.7 / `CMG-P-06` — concealing a vacancy or an unrecorded gap is PROHIBITED | Holding must be recorded as first-class, not omitted | same |

### Constitutional Authority

**The owner of each affected concern** — `REG-AUTO-001` (`CMG-DLG-13`), `STATUS-001` (`CMG-DLG-14`), `UCI-001` (`CMG-DLG-15`), `GOV-INT-001` (`CMG-DLG-16`) — under `CMG-000001` XX.7 and Article LII. **Not** `CMG-000001` itself, and **not** this programme.

### Decision

**HELD. Not decided here.**

`GD-08` records that the matter is **routed, unresolved, to the owner of each of the four affected concerns**, and is entered in the Deferral Register as `DEF-01` with a deferring condition, an owner on return, and a declared review point.

Four things are recorded, and nothing more:

1. **The disagreement is a finding**, not a fact. Two located records — `CMG-000001` XX.8 and `CMG-REGISTRY.json → concerns[]` — are both authoritative and both stand.
2. **Its disposition is reserved to four owners, individually.** No single act disposes it, because four distinct concerns are affected.
3. **No default is adopted.** Neither reading is preferred, narrowed, or assumed. Specifically: this programme does **not** hold that the four instruments lose ownership, and does **not** hold that XX.8 is inoperative.
4. **The hold is visible.** It is recorded as a first-class entry (`DEF-01`) and carried forward as a remaining governance gap (`GG-2`), satisfying XV.7 / `CMG-P-06`.

**This is a disposition of the matter, not a disposition under `CEP-002` 28.13.** `GD-08` therefore carries **no** Art 28.13 disposition, is **not** registered as a decision in any located register, and does **not** enter the Art 28 decision population. See §Disposition below for why that is deliberate and why it cannot close the Implementation Evidence Gate.

### Rationale

Deciding this matter would require exercising four owners' jurisdictions simultaneously — precisely what XVII.8 forbids (*"an instrument SHALL NOT determine its own jurisdiction"*, and a fortiori not another's) and what XX.7 reserves in terms that name the reservation twice: *"never by this instrument"*, extended by Output 16 to *"never by a measuring programme"*, and extended here, on the same reasoning, to **never by a determining programme that does not own the concern**. A determination has no more licence than a measurement to take another owner's decision.

Nor is either reading obviously correct, which is the test LVII.3 sets. Both are internally coherent: XX.8 can be read as prospective (a *new* Owner may not be derived-truth) or as absolute (the four recorded Owners are irregular). Choosing between them changes the standing of four instruments that between them own registration, status, change intelligence and execution architecture — the load-bearing quarter of the corpus. LVII.3 forbids resolving that *"by default … or by the most convenient authority."*

Holding is therefore not a failure to decide but the decision the located law requires. Its cost is recorded honestly: LII.6 provides that an undispositioned finding blocks certification under Article LXXX, so `DG-6` remains a live constraint on any non-provisional certification claim, and the current ceiling of `CERTIFIED-PROVISIONAL` already reflects an unresolved constitutional layer.

### Dependencies

| Direction | Item | Nature |
|---|---|---|
| Related to | `GD-05` | `GD-05` recognizes the ownership records as facts; it does **not** resolve their internal disagreement. Strict separation, recorded at `GD-05-C4`. |
| Related to | `GD-02` | Both concern the `AUTHORITY = NONE` convention on **different facts**: `GD-02` concerns an artifact *absent* from the Registry (decidable, decided); `GD-08` concerns artifacts *present* as Owners (reserved, held). |
| Depends on | `GD-21` / `DEF-02` | While T1 is vacant, the four instruments' standing is PROVISIONAL regardless of how this resolves, which is part of why the matter is not urgent-but-unresolvable rather than urgent |
| Blocks | non-provisional certification | `CMG-000001` LII.6 / Article LXXX, as `DG-6` already records |
| Does **not** block | `M-1A` or any consolidation step | The matter is held, carries no Art 28.13 disposition, and is therefore outside the population `CEP-002` 28.18 governs (see §Disposition) |

### Affected Programmes

`UCCEP-000007` (recorded `DG-6`; not edited) · `UCCEP-000008` (records the hold) · any programme that would claim non-provisional certification while the finding is undisposed.

### Affected Registries

None mutated. `CMG-REGISTRY.json` is read; **X-3** forbids editing `00-CMG/` and no edit is required, because holding changes nothing.

### Affected Constitutions

None amended. `CMG-000001` XX.7, XX.8, LII.3, LII.6, LVII.3, XV.7 cited. The four control-tower instruments are cited, unedited.

### Affected Implementations

None.

### Constraints

| Id | Constraint |
|---|---|
| `GD-08-C1` | No consolidation artifact SHALL adopt, imply, or rely on either reading of XX.8 as settled. |
| `GD-08-C2` | No consolidation artifact SHALL treat any of the four instruments as having lost ownership, nor as having acquired standing beyond `CMG-L-12` PROVISIONAL. |
| `GD-08-C3` | `DEF-01` SHALL NOT exit by silence or lapse of time; every exit is a reviewed, governed determination (`CEP-002` 27.11, 27.12). |
| `GD-08-C4` | `GD-08` SHALL NOT be registered in any located decision register, because it carries no `CEP-002` 28.13 disposition; registering it would create an undispositioned decision under 28.14. |
| `GD-08-C5` | Any non-provisional certification claim SHALL first account for `DG-6` under `CMG-000001` LII.6 / Article LXXX. |

### Acceptance Criteria

Acceptance here is acceptance of the **hold**, not of a resolution:

1. `DEF-01` exists in `07-DEFERRAL-ENTRIES.md` with all nine `CEP-002` 27.4 elements present (identity, matter, deferring authority and jurisdiction, basis, deferring condition, owner on return, declared review point, entry state, bound evidence).
2. `DEF-01` entry state is `RECORDED`, the initial state 27.9 requires.
3. `GD-08` appears in no located decision register and in no Art 28.13 disposition column.
4. `DG-6` is carried forward as a remaining governance gap in `10-REMAINING-GOVERNANCE-GAPS.md`.
5. No consolidation artifact asserts a resolution of XX.8.

### Traceability

`DDI-15` → `GD-08` → `DEF-01` → `GG-2`. Upstream: Output 16 §3 row DDI-15; `UCCEP-000007/13-KNOWN-GAPS.md` §2 `DG-6`; `UCCEP-000007/09-OWNERSHIP-INVENTORY.md` §5. Authority chain: `CMG-000001` XVII.2 → four concerns `CMG-DLG-13/14/15/16` → four owners, per XX.7 and Article LII. Onward: `07-DEFERRAL-ENTRIES.md` `DEF-01`; `10-REMAINING-GOVERNANCE-GAPS.md` `GG-2`; expressly **not** `08-DISPOSITION-ROUTING-TABLE.md`'s registration rows.

### Future Impact

The matter remains open and must be disposed by four owners before any non-provisional certification. Recording it as a held entry with a mandatory reviewed exit converts an indefinite ambiguity into a tracked obligation with a review cadence — the improvement `CEP-002` Article 27 exists to provide. It also sets the precedent that a determining programme, like a measuring one, refuses matters it does not own.

### Disposition

**NO `CEP-002` 28.13 DISPOSITION — HELD under `CEP-002` Article 27, `CEP-002` 28.16, and `CMG-000001` LVII.3.**

Recorded as deferral entry **`DEF-01`**, state `RECORDED`.

Why this is lawful and why it does not close the Implementation Evidence Gate, stated explicitly because the distinction is load-bearing:

- `CEP-002` 28.16 provides that recording a matter in the Deferral Register *"IS **not** a disposition under 28.13"* and does not satisfy Article 28's obligations. It follows that a matter so recorded is **not a dispositioned decision** — and equally that it is **not an undispositioned decision**, because it is not a *decision* at all: no competent authority has agreed it (28.8 CONSTITUTIONAL AGREEMENT is not reached), so it never enters the lifecycle.
- `CEP-002` 28.18 closes the Gate while a *"previously ratified or recorded decision IS undispositioned"*. `GD-08` is neither ratified nor registered as a decision, so it is outside that population. `GD-08-C4` forbids registering it, precisely so this remains true.
- `CMG-000001` LVII.3 makes holding the required response to an undecidable matter, and XV.7 / `CMG-P-06` make recording the hold mandatory.

The mechanical Gate value is therefore unchanged by `GD-08`; see `09-TRACEABILITY-VERIFICATION.md` §5 for the verification.

---

## Family summary — GDR-B

| GD | DDI | Decision in one line | Disposition | Realization required |
|---|---|---|---|---|
| `GD-05` | DDI-02 | The consolidation adds no ownership row and changes no owner; the four located records are the facts | (b) | none |
| `GD-06` | DDI-03 | The consolidation mapping is identity; programmes bind to Owners by reference, never by relocation | (b) | none |
| `GD-07` | DDI-14 | Locus is `GOV-INT-001` (already resolved); form is this determination family, amending nothing | (b) | none |
| `GD-08` | DDI-15 | **Held.** The XX.8 vs Registry-Owner disagreement is routed unresolved to four concern owners | **none** — `DEF-01` | none |

**Family properties:** 4 matters · 3 recognitions · 1 held · **zero** rejections · **zero** work packages · **zero** repository mutations outside `00-MASTER/UCCEP-000008/` · zero constitutions amended · zero registries touched. The one held matter carries no Art 28.13 disposition by design and is verified Gate-neutral in `09-TRACEABILITY-VERIFICATION.md` §5.

---

*`UCCEP-000008` Output 2, family GDR-B. Three decisions rendered within located law; one matter expressly refused as belonging to four other owners. No authority created, no law legislated, no ownership altered, no implementation performed. `CERTIFIED-PROVISIONAL`; Tier T1 VACANT; PROVISIONAL under `CMG-L-12`.*
