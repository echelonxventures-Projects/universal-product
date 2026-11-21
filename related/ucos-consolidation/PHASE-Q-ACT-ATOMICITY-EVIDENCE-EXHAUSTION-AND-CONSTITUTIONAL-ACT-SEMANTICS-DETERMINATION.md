# PHASE Q — ACT ATOMICITY EVIDENCE EXHAUSTION & CONSTITUTIONAL ACT SEMANTICS

| Field | Value |
|---|---|
| AUTHORITY | **NONE** |
| BASELINE | `integration/recovery-001` @ `1e3e4ba9` |
| RULE OBSERVED | Invent nothing · define nothing · author nothing · assume nothing · repair nothing |
| CORPUS | 81 artifacts (44 CMG-recognized on disk ∪ 48 `00-CEP/*.md`), **23,480 lines** |
| EXTRACTION | **5,663 occurrences** of 18 terms — complete, no sampling — `.runtime/phase-q/Q1-COMPLETE-TERM-INVENTORY.csv` (1.65 MB) and `.runtime/phase-q/Q1-ALL-ACT-OCCURRENCES.txt` |
| EXECUTED | `urat_engine.py --gate` → **OPEN**, 5/5 records, 13 transitions, seal `1717a90977e3abfd`; byte-identical regeneration (`git diff` empty) |
| CLASSIFICATION | `[F]` · `[I]` · `[GAP]` · `[UNKNOWN]` · `[UNPROVABLE]` · `[IMPOSSIBLE]` |

---

## Q0 — CORRECTION ISSUED FIRST

**`[F]` Phase O's `GAP-O-02` — *"constitutional act atomicity is nowhere defined"* — and the End-State Determination's `K-12` / `B-03` are OVERSTATED, and `K-12`'s classification as *"eliminable in-corpus"* is WRONG.**

`[F]` Exhaustive extraction locates **eleven components of an act model**, one of which is **executable and passing**. `[F]` The real defect is not absence. It is a **scope boundary** — every act-governing clause in the CEP corpus is scoped *"of the Program"*, and the act whose cardinality Phase O needed is by definition not of the Program.

`[I]` The corrected finding is **narrower, harder, and changes the eliminability verdict from in-corpus to externally blocked.** §Q8 and §Q9 carry it.

---

## Q1 — TERM EXHAUSTION

### Q1.1 Complete occurrence census — `[F]` executed, no sampling

| Term | Occurrences | Artifacts |
|---|---:|---:|
| certification | 1,230 | 78 |
| execution | 864 | 73 |
| determination | 729 | 73 |
| ratification | 695 | 58 |
| closure | 504 | 60 |
| transition | 379 | 57 |
| decision | 264 | 37 |
| **act** | **216** | **45** |
| operation | 187 | 33 |
| verification | 148 | 44 |
| action | 113 | 43 |
| disposition | 100 | 16 |
| event | 85 | 18 |
| acceptance | 76 | 23 |
| approval | 36 | 13 |
| **atomic** | **34** | **13** |
| **atomicity** | **3** | **2** |
| **finalization** | **0** | **0** |
| **TOTAL** | **5,663** | — |

**`[F]` "finalization" has ZERO occurrences in the constitutional corpus.** `[F]` The state `FINALIZED` exists (`CEP-006` VI.1, `URAT-ST-09`); the nominalisation of the act that produces it does not.

### Q1.2 Complete `atomic` / `atomicity` inventory — **all 37, enumerated**

| # | Artifact | Line | Clause | Subject of the atomicity claim |
|---|---|---|---|---|
| 1 | `CEP-003` | 59 | **III.1** | **execution unit** — *"the **atomic** granted work of execution: the **single next authorized action** of the active stage"* |
| 2 | `CEP-003` | 104 | **V.5** | **transition** — *"A transition SHALL be atomic; a partially applied transition SHALL be resolved by the Recovery Model"* |
| 3 | `CMG-000001` | 714 | **XXVI.5** | **transition** — *"Every transition SHALL be evidenced and **atomic**. A transition that leaves the artifact in no state, or in two states, IS a defect."* |
| 4 | `CMG-000001` | 574 | **XX.5** | **ownership transfer** — *"transfer IS atomic"* |
| 5 | `CMG-000001` | 440 | **XIV.4** | **Concern** — *"named, atomic, and non-overlapping"* |
| 6 | `CMG-000001` | 386 | CMG-K-04 | **Law** — *"Substantive, atomic"* |
| 7–21 | `REG-AUTO-001` | 12,14,62,91,110,131,270,298,403,458,464 | **P5, §7** | **registration transaction** — *"Registration across the seven registers is **all-or-nothing** (§7). Partial registration is a failed transaction, not a partial success."* |
| 22–27 | `GOV-INT-001` | 25,42,178×2,282,344×2 | — | **registration/sync transaction `T`** — *"One transaction, atomic, idempotent"* |
| 28 | `AUTH-INF-001` | 159 | — | registration transaction (reference) |
| 29–30 | `CEP-009` | 481, 484 | — | Atomic Creation Law / Atomic Registration Transaction (reference) |
| 31–34 | `STAGE-*` | 16,27,48,53,243 | — | Atomic Registration Transaction (reference) |
| 35 | `NUCLEUS-001-02` | 10 | — | **Nucleus** — *"the atomic unit of canonical ownership"* |
| 36–39 | `DATA-001` 63 · `SERVICE-001` 65 · `APPLICATION-001` 67 · `INFRASTRUCTURE-001` 70 | — | — | **domain root concepts** — *"the atomic unit of …"* |

**`[F]` DECISIVE NEGATIVE RESULT, exhaustively established:**
- occurrences of **`"atomic act"`** — **0**
- occurrences of **`"act atomicity"`** — **0**
- occurrences of atomicity predicated of a **constitutional act** — **0**

`[F]` Atomicity is asserted of **seven subject classes**: execution unit, transition, ownership transfer, concern, law, registration transaction, and domain root concept. **An act is not among them.**

### Q1.3 Complete `act` inventory — 216 occurrences

`[F]` Distribution: `STAGE-*` 72 · `CMG-000001` 25 · `CEP-002` 14 · `CEP-006` 11 · `CEP-003` 10 · `CEP-010` 10 · `CEP-001` 9 · `CEP-007` 9 · `CEP-009` 9 · `CEP-008` 8 · `CEP-005` 7 · `RUNTIME-001` 7 · `CEP-004` 6 · `SECURITY-001` 3 · nine others 2 or fewer.
`[F]` **Constitutional core (`CMG-*` + `CEP-*`): 118 of 216.** Full listing: `.runtime/phase-q/Q1-ALL-ACT-OCCURRENCES.txt`.

---

## Q2 — SEMANTIC CLASSIFICATION MATRIX

`[I]` The classification below is a **derived index over located text**. The occurrences are `[F]`; the class assignment is `[I]`.

| Class | Definition applied | Count (of 118 core `act` occurrences) | Representative located clauses |
|---|---|---|---|
| **PRIMITIVE** | The clause states what an act *is* or how it is *individuated* | **9** | `CMG` XXIII.1, XLVI.1, XLVI.3, XLIV.1, XLIV.5, XLVII.1, CMG-K-19; `CEP-004` P.2; `CEP-007` P.2 |
| **PROCEDURAL** | Constrains *how* an act is performed | **21** | `CEP-001` II.2/II.5/IV.1; `CEP-003` I.4/II.3; `CMG` XLVI.4/XLVI.6 |
| **GOVERNANCE** | Binds acts to jurisdiction, authority, scope | **34** | `CEP-002` 4.4/4.5/8.4/9.1/9.2/9.4/17.1/19.4/24.3; `CMG` XLVI.2, LXV.7 |
| **LIFECYCLE** | Ties an act to a state or transition | **6** | `CEP-006` XII.2/XII.4/XIX.1; `CEP-002` 27.10 |
| **CONSTITUTIONAL** | Predicated of a *constitutional* act specifically | **8** | `CEP-006` P.2; `CMG` XLIV.1, XXIII.1, XXIII.3, XXIII.5, XLVI.2, XLI.1 |
| **EXECUTIONAL** | Predicated of execution/operational acts | **18** | `CEP-003` P.4/I.1/II.4/X.4/XIII.3/XIV.2/XXIII.2/XXIII.3; `CEP-001` II.2–II.5 |
| **EVIDENTIARY** | Concerns recording, audit, provenance of acts | **22** | `CEP-001` XVII.1/XVII.4; `CEP-002` 18.4; `CEP-004`–`CEP-009` XIX.4/XXI.4/XX.3 family; `CEP-008` V.5/X.3 |
| **DERIVED** | Cites another instrument's act rule without adding | **~98** (of the 216 total, incl. `STAGE-*`) | `STAGE-*` bindings, `CEP-010` X–XV assurance rows |

`[I]` **The PRIMITIVE row is the material finding: nine clauses state what an act *is*, and Phase O did not locate them.**

---

## Q3 — ACT MODEL DISCOVERY

| # | Question | Verdict | Located basis |
|---|---|---|---|
| **1** | **What is an act?** | **`[F]` PARTIALLY ANSWERED — by role, not by genus.** | `CMG` XXIII.1 — *"**Responsibility** IS the assigned duty to perform a specific constitutional act… always **bounded by a named act**."* XXIII.3 — *"Every constitutional act that this instrument requires SHALL have a **named responsible role**."* XXIII.5 — *"An act with no responsible role IS an **unperformable obligation** and IS a defect under Article LII."* `CMG-K-19` — Ratification = *"An **act** of acceptance into the corpus"*, kind **Constitutive**. **No genus definition ("an act IS …") exists.** |
| **2** | **What constitutes an act?** | **`[F]` ANSWERED — a 4-tuple identity is located.** | `CMG` **XLVI.3** — *"Approval SHALL be **specific**: it SHALL name **the act, the subject, the version, and the conditions**. Blanket or standing approval for a class of future acts IS PROHIBITED."* `[I]` ⟨act, subject, version, conditions⟩ is an individuation criterion. `CMG` **XLIV.5** — *"Each of those is a **distinct act with a distinct owner**"* → owner is individuating. |
| **3** | **What begins an act?** | **`[F]` ANSWERED for in-corpus acts.** | `CMG` **XLVI.4** — *"Approval SHALL be **recorded before the act**, never reconstructed after it."* `CEP-003` **I.4** — *"Execution Authority SHALL NEVER self-authorize an action, and SHALL act only upon an **authorization granted under Article VIII**."* `[I]` An act begins on a recorded prior authorization. |
| **4** | **What ends an act?** | **`[F]` ANSWERED for operational acts — with a cardinality clause.** | `CEP-001` **II.5** — *"Every operational act SHALL **conclude** by advancing program state and emitting **exactly one** next authorized action."* |
| **5** | **Can an act contain subacts?** | **`[GAP]`** | No located clause admits, forbids, or mentions subacts. Zero occurrences of "subact", "sub-act". |
| **6** | **Can multiple events form one act?** | **`[F]` YES — LOCATED.** | `CEP-002` **27.10** — *"a **new** declared review point SHALL be recorded **in the same act**, and the prior review SHALL be retained."* Two recorded effects, one act. Corroborated: `UCOS-Ω∞-CONSTITUENT-AUTHORITY-DETERMINATION-REPORT` §8 — *"the **single founding act** (identify sovereign seat + charter ratifier + fix precedence)"* — three effects, one act. |
| **7** | **Can one event form multiple acts?** | **`[F]` NO — the converse is located instead.** | `CMG` **XLIV.5** — certification, freeze, publication, registration, age, use, absence of objection — *"Each of those is a **distinct act** with a **distinct owner**"*. `[I]` Distinct owners force distinct acts; a single event with one owner does not decompose. |
| **8** | **Can one authority perform multiple acts simultaneously?** | **`[GAP]`** | No located clause addresses simultaneity. `CEP-001` II.5's *"exactly one next authorized action"* constrains **sequence**, not concurrency. |
| **9** | **Can one record represent multiple acts?** | **`[I]` NOT PROHIBITED by text; CONTRADICTED by implementation.** | Text: `CEP-001` **XVII.1** — *"Every governed act, finding, deferral, determination, ratification, and freeze SHALL be recorded in an **append-only, content-addressed record**"* — total, not injective. Implementation: `urat_engine.py` binds **one record ↔ one located act ↔ one content digest** (`binding["record"]`, `digest(act)[:16]`), gate **OPEN**. |
| **10** | **Can one act produce multiple state transitions?** | **`[F]` YES — LOCATED.** | Same as (6): `CEP-002` 27.10. Also `CMG` **CMG-T-07** — `PROVISIONAL → RATIFIED`: *"The vacant authority **closes and accepts**"* — two events, one transition, one act. |

**`[F]` Six of ten answered from located text. Two `[GAP]` (subacts, simultaneity). One split text/implementation. One answered by its converse.**

---

## Q4 — CARDINALITY DEPENDENCY ANALYSIS

### Q4.1 The eleven located act-model components

```
EXISTENCE     "An act that cannot be audited SHALL be treated as if it did not
              lawfully occur."  — 9 instruments, 10 clauses (verified exactly):
              CEP-001 XVII.4 · CEP-002 18.4 · CEP-004 XXI.4 · CEP-005 XXI.4 ·
              CEP-006 XIX.4 · CEP-007 XIX.4 · CEP-008 XIX.4 AND V.5 ("An action
              that produces no evidence") · CEP-009 XIX.4 · CEP-003 X.4 (variant
              wording: "cannot be recorded and reproduced").
              CEP-010 carries voidability (XXI.3) but NOT the existence rule.
VOIDABILITY   "A void act SHALL have no effect and SHALL be recorded as void."
              — CEP-002 24.3 + 8 parallels. Acts can be void AND recorded.
RECORD        CEP-001 XVII.1 — append-only, content-addressed record
ATTRIBUTION   CEP-001 II.2  — exactly one stage, one write area
              CEP-003 II.3  — exactly one execution unit, one stage, one write area
TERMINATION   CEP-001 II.5  — concludes by emitting exactly one next authorized action
ATOMICITY     CEP-003 III.1 — execution unit is atomic: the single next authorized action
IDENTITY      CMG XLVI.3    — ⟨act, subject, version, conditions⟩
OWNERSHIP     CMG XLIV.5    — distinct act ⇒ distinct owner
AUTHORIZATION CMG XLVI.4    — approval recorded before the act
SEPARATION    CMG XLVI.6    — approver ≠ actor; coincidence forces escalation
RESPONSIBILITY CMG XXIII.1/3/5 — every act has a named role; none ⇒ defect
```

### Q4.2 Dependency graph

```
                    ┌───────────────────────────────────┐
                    │  ACT↔TRANSITION RELATION          │
                    │  located as MANY-TO-MANY (Q7)     │
                    └───────────────┬───────────────────┘
             ┌──────────────────────┼──────────────────────┐
             ▼                      ▼                      ▼
      act count            transition count         determination count
    ⛔ NOT A FUNCTION      ✔ COMPUTABLE             ✔ COMPUTABLE
                          (URAT: 13 declared,       (URAT: 5 records)
                           11 in-corpus,
                           2 out-of-corpus)
             │                      │                      │
             ▼                      ▼                      ▼
   ┌─────────────────────────────────────────────────────────────┐
   │ BLOCKED: "how many external ACTS remain"                    │
   │ NOT BLOCKED: "how many external TRANSITIONS remain" = 5     │
   └─────────────────────────────────────────────────────────────┘
```

### Q4.3 What is blocked, and what is not — `[F]` corrected against Phase O

| Consumer | Blocked by missing act semantics? | Evidence |
|---|---|---|
| `CMG-000007` §5 *"exactly two acts"* | **`[F]` YES — and independently FALSE** | Phase O `DIV-02`: closing `CMG-OQ-01`+`02`+`VAC-01` yields `READY-PROVISIONAL`, not `READY` |
| **URAT transition count** | **`[F]` NO — COMPUTED** | `urat.json → counts`: `transitions_declared: 13`, `transitions_in_corpus: 11`, therefore **out-of-corpus: 2** |
| **URAT outstanding external transitions** | **`[F]` NO — COMPUTED = 5** | `by_state: {"PROVISIONAL": 5}`; `PROVISIONAL→FINALIZED` carries `requires_out_of_corpus: true` |
| `DEF-02` exit cardinality | **`[F]` YES** | *"an authority **is identified** … **and** `VAC-01` **closes**"* — two events, act-count unfixed |
| `CMG-OQ-01` + `CMG-OQ-02` bundling | **`[F]` YES** | `GD-21-C7` forbids bundling as a **record**; no clause reaches the **act** |
| Article LXXX certification | **`[F]` NO** | LXXX.3 computes from findings, not acts |
| `cmg_validate.py` | **`[F]` NO** | Zero `act`/`atomic` mentions in 733 lines (Q6) |
| `CEP-002` 28.20 HALTED gate | **`[F]` NO** | Predicated on *undispositioned decisions*, which are counted, not acts |

---

## Q5 — IMPLICIT ATOMICITY DETECTION

`[F]` Exhaustive phrase census over `00-CEP/`, `00-CMG/`, `00-MASTER/UCCEP-000008/` (74 files):

| Phrase | Hits | Requires atomicity? | Implies? | Contradicts? | Independent? |
|---|---:|---|---|---|---|
| `"act is"` | 90 | — | — | — | mostly copular/derived |
| `"acts are"` | 21 | — | — | — | derived |
| `"act of the"` | 15 | — | — | — | — |
| **`"every act"`** | **5** | **`[I]` YES** — universal quantification presupposes individuation | YES | no | no |
| **`"single act"`** | **3** | **`[I]` NO** — see below | **NO** | no | **YES** |
| **`"single constitutional act"`** | **2** | `[I]` NO | NO | no | YES |
| **`"distinct act"`** | **2** | **`[I]` YES** — distinctness presupposes identity | YES | no | no |
| **`"same act"`** | **2** | **`[I]` YES** — and **CONTRADICTS one-act-one-transition** | YES | **YES** | no |
| **`"one act"`** | **2** | `[I]` YES | YES | no | no |
| **`"two acts"`** | **2** | `[I]` YES — presupposes a count | YES | no | no |
| **`"second act"`** | **1** | `[I]` YES | YES | no | no |
| `"act sequence"` | 1 | `[I]` YES | YES | no | no |
| `"multiple acts"` · `"each act"` · `"act completion"` · **`"atomic act"`** · **`"act atomicity"`** | **0** | — | — | — | — |

### `[F]` The "single act" clauses do NOT assert atomicity — proved from the corpus's own disambiguator

`CEP-006` **P.2** — *"Ratification SHALL be **the single constitutional act** through which a validated and certified artifact becomes an officially accepted member…"*
`CMG` **XLIV.1** — *"**Ratification** IS the single constitutional act by which a validated and certified artifact becomes an accepted member of the corpus."*

`[F]` **XLIV.5 disambiguates them in the same Article:** *"Ratification SHALL NOT be inferred from certification, freeze, publication, registration, age, use, or absence of objection. **Each of those is a distinct act with a distinct owner**, and none confers acceptance."*

`[I]` **"Single" therefore quantifies over KINDS of act that confer membership (exactly one: ratification), not over PERFORMANCES.** Reading it as "one performance" is a category error XLIV.5 forecloses. `[I]` Phase O reached this conclusion; Phase Q confirms it exhaustively — the reading survives inspection of all 216 `act` occurrences.

### `[F]` The clause that CONTRADICTS one-act-one-transition

`CEP-002` **27.10** (and `UCCEP-000008/07-DEFERRAL-ENTRIES.md` restating it): *"`UNDER-REVIEW → RECORDED` — … a **new** declared review point SHALL be recorded **in the same act**, and the prior review SHALL be retained."*
`[I]` One act, two recorded effects. **MODEL A is not universal.**

---

## Q6 — VALIDATOR ANALYSIS — executable evidence

| Executable | `act`/`atomic` mentions | Assumes atomicity? | Implements it? | Contradicts it? |
|---|---:|---|---|---|
| `00-CMG/tools/cmg_validate.py` (733 ln) | **0** | **NO** | **NO** | **NO** — act-blind |
| `00-MASTER/UCOS-UCAF-001/ucaf_engine.py` | **0** | NO | NO | NO |
| `00-MASTER/UCOS-UGA-001/uga_engine.py` | **0** | NO | NO | NO |
| `00-BOOK/tools/ukb.py` | 4 | `[I]` YES — registration transaction | `[F]` YES, **for transactions** (`REG-AUTO-001` P5) | NO |
| `00-MASTER/UCCEP-000000/uccep_engine.py` | 6 | NO | NO | NO |
| **`00-MASTER/UCOS-URAT-001/urat_engine.py`** | **20** | **`[F]` YES** | **`[F]` YES — the only act model in executable form** | NO |

### `[F]` `urat_engine.py` implements act individuation — executed evidence

```
L241  act = read_text(binding["record"])              ← an act IS a located document
L246  verdict_located = binding["verdict_anchor"] in act   ← verified in the act's OWN text
L327  "record_digest": digest(act)[:16]               ← content-addressed (CEP-001 XVII.1)
L846  "Where this registry and a located ratification act differ, THE ACT GOVERNS."
```

`[F]` **Executed this session:** `urat_engine.py --gate` → `RATIFICATION-REGISTRY-BOUND | records=5/5 | attribution=1rec/4der | coverage=16/16 | unaccounted=0 | gate=OPEN | seal=1717a90977e3abfd`. `[F]` Regeneration was **byte-identical** (`git diff` empty after the run) — determinism confirmed.

`[F]` **And it declares out-of-corpus performability as machine data:**

```
transitions_declared : 13
transitions_in_corpus: 11
requires_out_of_corpus: 2   →  ACCEPTED   → FINALIZED
                               PROVISIONAL → FINALIZED
by_state             : {"PROVISIONAL": 5}
finality_ceiling     : in_corpus_ceiling=[PROVISIONAL]; unreachable_in_corpus=[FINALIZED]
```

`[I]` **This is the strongest act-semantics artifact in the repository, and Phase O did not consult it.** Its own docstring states the mechanism: *"this engine holds **no authority to perform any transition**, so the in-corpus ceiling is enforced **structurally rather than described**."*

---

## Q7 — SATISFIABILITY ANALYSIS

| Model | Verdict | Proof from located evidence |
|---|---|---|
| **MODEL A** — one authority + one record + one transition = one act | **`[F]` PERMITTED · NOT REQUIRED · CONTRADICTED AS UNIVERSAL** | Permitted: `CEP-003` II.3 + III.1 + `CEP-001` II.5 jointly describe exactly this for execution acts. Contradicted as universal: `CEP-002` **27.10** — *"recorded in the **same act**"* with two effects. |
| **MODEL B** — one authority may perform multiple acts in one record | **`[I]` NOT PROHIBITED BY TEXT · CONTRADICTED BY IMPLEMENTATION** | Text: `CEP-001` XVII.1 requires every act to be recorded; it does not require injectivity. Implementation: `urat_engine.py` binds one record to one act with one digest, and the gate is **OPEN** at 5/5. `[GAP]` **G-Q-01** — the text/implementation divergence is unadjudicated. |
| **MODEL C** — one act may contain multiple transitions | **`[F]` PERMITTED · LOCATED** | `CEP-002` 27.10 (new review point + prior retained, one act). `CMG-T-07` (*"the vacant authority **closes and accepts**"*). `UCOS-Ω∞-CONSTITUENT-AUTHORITY-DETERMINATION-REPORT` §8 (*"the **single founding act** (identify sovereign seat + charter ratifier + fix precedence)"*). |
| **MODEL D** — one transition may require multiple acts | **`[F]` PERMITTED · LOCATED · INSTANTIATED** | `UCCEP-000008/07-DEFERRAL-ENTRIES.md` — *"Four concerns are affected, so **no single act disposes it**"*; *"**no single act resolves all four**"* (`DEF-01`, four owners individually). `CMG` XX.7. `CMG` XLIV.5 (distinct owner ⇒ distinct act). |
| **MODEL E** — act semantics absent | **`[F]` CONTRADICTED** | Eleven located components (Q4.1) + one executable implementation (Q6). |

### `[I]` The formal result — this is the Phase Q core

**`[F]` MODEL C and MODEL D are BOTH permitted and BOTH located and instantiated.**

`[I]` C states the act→transition map is not injective. D states it is not functional in the reverse direction either. **Together they establish that the act↔transition relation is MANY-TO-MANY.**

`[I]` **Therefore act count is not a function of transition count in either direction — and this, not the absence of an atomicity definition, is the exact reason cardinality cannot be derived.** No arithmetic exists over a many-to-many relation without a further individuating input, and the corpus supplies that input (XLVI.3's 4-tuple, XLIV.5's owner) **only for acts of the Program**.

---

## Q8 — GAP DETERMINATION

### `ACT-ATOMICITY-GAP` — determination

| Candidate classification | Verdict | Proof |
|---|---|---|
| **Real** | **`[F]` YES — but misnamed and mislocated** | The gap is not *atomicity*; atomicity is located for seven subject classes (Q1.2). |
| **Apparent** | **`[F]` NO** | Eleven components + one implementation are located; the model is not merely apparent. |
| **Already solved** | **`[F]` PARTIALLY — for in-corpus acts, and in executable form** | `urat_engine.py`; `CEP-001` II.2/II.5/XVII.1; `CEP-003` II.3/III.1; `CMG` XLVI.3/XLIV.5 |
| **Derivable** | **`[F]` PARTIALLY** | Transition cardinality **IS** derivable (URAT: 2 out-of-corpus transition types, 5 outstanding). Act cardinality is **NOT**, by Q7's many-to-many result. |
| **Internally blocked** | **`[F]` NO — and this REVERSES `K-12`** | See the scope proof below. |
| **Externally blocked** | **`[F]` YES** | See the scope proof below. |

### `[F]` THE SCOPE PROOF — the exact locus of the gap

1. `[F]` Every act-governing instrument scopes itself to the Program, verbatim and verified across all nine:

```
CEP-002 P.3  "SHALL bind every governance act of the Program"
CEP-003 P.4  "SHALL bind every execution act of the Program"
CEP-004 P.4  "SHALL bind every validation act of the Program"
CEP-005 P.5  "SHALL bind every certification act of the Program"
CEP-006 P.5  "SHALL bind every ratification act of the Program"
CEP-007 P.5  "SHALL bind every freeze act of the Program"
CEP-008 P.5  "SHALL bind every evidence and traceability act of the Program"
CEP-009 P.5  "SHALL bind every amendment and evolution act of the Program"
CEP-010 P.5  "SHALL bind every audit and assurance act of the Program"
```
`[F]` `CEP-001` is Program-scoped by the same construction in different words —
**XXIV.4**: *"This Constitution SHALL bind every remaining **Stage of the Program**"* —
and `CEP-001` II.2/II.4 attach every operational act to a stage. **Ten instruments, zero
exceptions.**

2. `[F]` `CEP-000` **§6.4** — *"This Charter SHALL NOT override, suspend, or amend the UCOS Ω∞ Constitution, any frozen corpus, or **any authority residing outside the Program**."*
3. `[F]` `CEP-006` **XII.2** — the act that moves `PROVISIONAL → FINALIZED` is *"the act of the **out-of-corpus** finality authority."*
4. `[I]` By (1) and (3), that act is **not an act of the Program**, so **no clause in (1) binds it**.
5. `[I]` By (2), **no clause could be written to bind it** without exceeding the Charter's own limit.
6. `[F]` `CMG-000001` reaches the same boundary from the other side: **XLIV.7** — *"no authority SHALL grant itself ratification competence"*; **LXXXI.6** — no self-elevation.

**∎ `[I]` Determination: the located act model is TOTAL over in-corpus acts and, by the corpus's own scoping and non-override clauses, CANNOT be extended to the out-of-corpus finality act. The gap is EXTERNALLY BLOCKED.**

`[F]` **This reverses the End-State Determination's `K-12` (*"eliminable in-corpus"*) and `B-03` (*"in-corpus blocker"*).** `[I]` What *is* eliminable in-corpus is the **recording** of external acts — and `urat_engine.py` has already eliminated it: `URAT-REC-01` carries `EC-1`'s act digest `3625ea5f92c8acc1`. **The recording side is solved; the performance side is unbindable.**

---

## Q9 — TERMINAL DETERMINATION

| # | Question | Answer |
|---|---|---|
| **1** | **Does a constitutional act model exist?** | **`[F]` YES — PARTIALLY.** Eleven located components (existence, voidability, record, attribution, termination, atomicity-of-execution-unit, identity, ownership, authorization, separation, responsibility), of which one is executable and passing (`urat_engine.py`, gate OPEN). **No genus definition ("an act IS …") exists** — `[GAP]` **G-Q-02**. |
| **2** | **Does a constitutional atomicity model exist?** | **`[F]` YES for seven subject classes; `[GAP]` for constitutional acts.** Exhaustively: 37 atomicity occurrences, **0** predicated of an act; **0** occurrences of `"atomic act"`; **0** of `"act atomicity"`. The nearest is `CEP-003` III.1 (**execution unit** atomic), scoped by `CEP-003` P.4 to acts *of the Program*. |
| **3** | **Can act cardinality be derived?** | **`[F]` NO — and the reason is now exact.** Not from missing atomicity, but because MODEL C and MODEL D are **both located and instantiated**, making the act↔transition relation **many-to-many** (Q7). No arithmetic exists over such a relation. |
| **4** | **Can external act count be derived?** | **`[F]` PARTIALLY — and this is new.** **External TRANSITION count IS derivable and computed: exactly 2 out-of-corpus transition types declared; exactly 5 outstanding** (`urat.json`: `transitions_declared 13`, `transitions_in_corpus 11`, `by_state {"PROVISIONAL": 5}`). **External ACT count is bounded `1 ≤ n ≤ 5` for URAT's scope** `[I]` — lower bound by MODEL C, upper by MODEL D — **and its exact value is at the discretion of an authority no in-corpus clause may bind** (Q8 scope proof). Outside URAT's scope, `VAC-01`, `CMG-OQ-01/02/03/07` add further externally-rooted items. |
| **5** | **Can completion cardinality be derived?** | **`[F]` NO.** `CMG-000001` **LXXIX.5** — a completeness result is valid *"only for the repository state that produced it"*; **LXXX.6** — any amendment automatically revokes certification. `[I]` Completion is a state predicate, never a terminal count. |
| **6** | **Is the question well-formed?** | **`[I]` PARTIALLY — and the partition is exact.** *"How many external **transitions**?"* — **WELL-FORMED and answered (5).** *"How many external **acts**?"* — **WELL-FORMED but UNDERDETERMINED**: the individuating criteria exist (XLVI.3 4-tuple, XLIV.5 owner) but are scoped away from out-of-corpus acts. `[I]` **Correction to Phase O**, which held the question had *no truth conditions*: it has truth conditions; they are **not evaluable in-corpus**. |
| **7** | **Is there a real gap?** | **`[F]` YES — `ACT-SEMANTICS-EXTERNAL-SCOPE-GAP`.** Precisely: *no clause individuates, bounds, or counts acts performed by an authority outside the Program, and `CEP-000` §6.4 forbids writing one.* **Not** *"act atomicity is undefined."* |
| **8** | **Is amendment justified?** | **`[I]` NOT DETERMINABLE HERE — and the corpus routes it away from this document.** `CMG-000001` **XIX.5** — *"Where a question falls outside XIX.1 and is not delegated, this instrument SHALL record it and SHALL **decline to answer it**. Declining IS the correct constitutional response."* `[F]` Justification of an amendment is an owner's determination under `CEP-009`; this determination makes none. |
| **9** | **Is amendment required?** | **`[F]` NO — for the external-scope gap.** `[I]` An amendment cannot close it: by Q8 steps (2) and (5), a clause binding an out-of-corpus authority would exceed `CEP-000` §6.4 and be void under `CEP-002` 4.4 (*"An act performed outside the actor's jurisdiction IS PROHIBITED and SHALL be void"*). **`[F]` For the in-corpus genus gap `G-Q-02` and the text/implementation divergence `G-Q-01`, no located clause states a requirement either way — `[GAP]`.** |
| **10** | **Is amendment prohibited?** | **`[F]` YES — for any clause purporting to bind the out-of-corpus authority.** `CEP-000` §6.4 (no override of outside authority); `CMG-000001` **XLIII.4** — *"A jurisdiction-expanding amendment to the meta layer IS PROHIBITED"*; **XIX.4**. `[F]` **NOT prohibited** for an in-corpus genus definition, which would fall within `CMG-000001` XIX.1 meta jurisdiction (Article IV, Definitions). |

---

## SUCCESS CONDITION — DISCHARGED

The instruction admits two exits. **Both are reached, and they partition cleanly:**

**(A) `[F]` ACT SEMANTICS ARE LOCATED — for in-corpus acts.** Eleven components across `CEP-001` II.2/II.5/XVII.1/XVII.4, `CEP-002` 24.3, `CEP-003` II.3/III.1/I.4, `CMG-000001` XXIII.1/3/5, XLIV.5, XLVI.1/3/4/6, plus one **executable and passing** implementation in `urat_engine.py`. **Phase O's `GAP-O-02` is corrected.**

**(B) `[F]` A GAP IS PROVEN — for out-of-corpus acts.** `ACT-SEMANTICS-EXTERNAL-SCOPE-GAP`, established by the nine `"of the Program"` scoping clauses plus `CEP-000` §6.4, and shown **unclosable by amendment** rather than merely unclosed.

---

## PHASE Q TERMINAL VERDICT

> **DETERMINATION-COMPLETE · ACT MODEL LOCATED (11 COMPONENTS, 1 EXECUTABLE) · ATOMICITY LOCATED FOR 7 SUBJECT CLASSES, NONE OF THEM AN ACT · GAP PROVEN, REAL, AND EXTERNALLY BLOCKED · PHASE O CORRECTED**

**`[F]` The headline correction.** Phase O and the End-State Determination held that constitutional act atomicity is *nowhere defined* and that the gap is *eliminable in-corpus*. Exhaustive extraction — 5,663 occurrences, 81 artifacts, 23,480 lines, no sampling — shows **both claims are wrong in the same direction**: an act model exists in eleven located components and one passing executable, and the residual gap is **externally blocked, not internally eliminable**.

**`[F]` What atomicity actually is, exhaustively.** Thirty-seven occurrences. Atomicity is predicated of **execution units, transitions, ownership transfers, concerns, laws, registration transactions, and domain root concepts** — seven classes, none of which is an act. `"atomic act"`: **0**. `"act atomicity"`: **0**. The negative result is now total, not sampled.

**`[I]` Why cardinality still cannot be derived — the exact reason, which is not the one previously given.** `CEP-002` 27.10 locates one act producing two recorded effects (MODEL C). `UCCEP-000008` locates one matter requiring four acts by four owners (MODEL D). **Both are located and instantiated, so the act↔transition relation is many-to-many** — and no arithmetic exists over a many-to-many relation. The absence was never a missing definition of atomicity; it is a **non-functional relation between two things the corpus does define.**

**`[F]` What IS now derivable, and was not claimed before.** `urat_engine.py` declares out-of-corpus performability as machine data: **13 transitions, 11 in-corpus, exactly 2 requiring the out-of-corpus authority**, with **5 records outstanding at PROVISIONAL**. So *external transition count* is computed and equals **5**; *external act count* is bounded **1 ≤ n ≤ 5**, its exact value set by an authority no in-corpus clause may bind.

**`[I]` And the sharpest result — question 6.** Phase O held that *"how many acts"* has **no truth conditions**. That was too strong. The individuating criteria **exist and are located**: `CMG` XLVI.3's ⟨act, subject, version, conditions⟩ and XLIV.5's distinct-owner rule. They are simply scoped, by nine `"of the Program"` clauses and `CEP-000` §6.4, **away from the one act whose count is wanted**. **The question is well-formed and not evaluable in-corpus** — which is a different and more precise finding than ill-formedness, and it is why question 9 answers NO: an amendment cannot reach across a boundary the Charter forbids crossing.

**This determination defines nothing, authors nothing, amends nothing, repairs nothing, and closes nothing.** It records what the corpus at `1e3e4ba9` already contains, and — where the corpus contains nothing — records that instead.

---

*PHASE Q · AUTHORITY = NONE · Reports; determines nothing.*
*`CERTIFIED-PROVISIONAL`; Tier T1 VACANT; `CMG-L-12` applies to every statement herein.*
*Complete inventories: `.runtime/phase-q/Q1-COMPLETE-TERM-INVENTORY.csv` (5,663 rows) · `.runtime/phase-q/Q1-ALL-ACT-OCCURRENCES.txt` (216 rows).*
