# PHASE O — RESIDUAL UNCERTAINTY ELIMINATION & CARDINALITY CLOSURE

| Field | Value |
|---|---|
| AUTHORITY | **NONE (DERIVED TRUTH)** |
| METHOD | Exhaustive corpus analysis at HEAD. No assumptions, no amendments, no proposed solutions, no normative recommendations. |
| BASELINE | branch `integration/recovery-001`, HEAD `1e3e4ba9`; 13,945 files (3,885 `.md`, 3,224 `.py`, 915 `.json`) |
| CLASSIFICATION | Every statement carries `[F]` Fact · `[I]` Inference · `[A]` Assumption · `[GAP]` · `[UNKNOWN]` |
| EXECUTABLE EVIDENCE | `00-CMG/tools/cmg_validate.py` executed at HEAD: **0 findings**, `READY-PROVISIONAL`, 44 artifacts, 1 vacancy, 9 gaps, 7 open questions |
| WHAT THIS DOCUMENT DOES | Derives. It closes nothing, ratifies nothing, allocates nothing, and nominates no occupant for any tier (`CMG-000001` XVII.4, LXXXI.5; `GD-21-C1`, `GD-21-C4`). |

---

## O0 — SCOPE CORRECTION (READ FIRST)

**`[F]` The finding statements of Phase N are not present in the repository at HEAD.**
An exhaustive search for a Phase N output artifact, and for a finding identifier `D-14`
bound to `CMG-000001` Article XVI, returns nothing. The token `D-14` occurs in 46 files, in
seven mutually unrelated identifier spaces — `GD-14` (`UCCEP-000008` migration sequence),
`D-14` (UAF directive categories), `D-14` (UGA lifecycle states), `D-14` (URRC executability
gaps), `D-14` (MOD-001 create-unavailable), `D-14` (S-1 invariants), and the substring
`…-14` inside `UICM-OBL-*` obligation identifiers. **None binds to `CMG-000001` XVI.2/XVI.3/XVI.4.**

**`[UNKNOWN] UNK-01` — the literal statement of Phase N's `D-14` is not recoverable from HEAD.**

**`[I]` Consequence for O3.** O3 is therefore answered *over the artifact set the instruction
names* — `CMG-000001` XVI.2, XVI.3, XVI.4, the CMG registry projection, and `cmg_validate.py` —
by deriving the complete defect set over that quadruple from primary text and executed code,
rather than by adopting an unverifiable restatement of a finding this repository does not carry.
Where the derived defect set is offered as the referent of `D-14`, that identification is `[I]`,
never `[F]`.

The same caution applies to O1's `A ≡ B`: the instruction does not bind `A` and `B` to specific
entities, so §O1.B produces the **complete** equality matrix over the seven named references and
§O1.D answers the decidability question for every pair, not for one assumed pair.

---

## O1 — IDENTITY COLLAPSE ANALYSIS

### O1.A — Complete identity graph

Every located reference resolves to one of eleven distinct entities. The decisive column is
**TYPE**: the corpus mixes *lattice slots*, *artifacts*, *authorities*, *roles* and *acts* under
overlapping names, and several apparent identity questions are dissolved by type alone.

| # | Entity | TYPE | Located definition | Status at HEAD |
|---|---|---|---|---|
| `E1` | **Tier T1** | LATTICE SLOT | `CMG-000001` XVI.2 row T1 — "Constitutional Authority" | **VACANT** `[F]` |
| `E2` | **VAC-01** | VACANCY RECORD over `E1` | `CMG-REGISTRY.json → vacancies[0]`; `CMG-000001` IV.11 | `located: false` `[F]` |
| `E3` | **The T1 occupant** | **ARTIFACT** | `VAC-01.declared_superior` = *"The ratified UCOS Ω∞ Constitution presupposed at CEP-000 §5.5 Tier 1 and §6.4"*; `CEP-000` §5.5 Tier 1 = *"the ratified UCOS Ω∞ Constitution and its concerns"* | does not exist as normative law `[F]` |
| `E4` | **CMG-OQ-02** | QUESTION over `E3` | *"Which **artifact**, if any, occupies Tier T1"* | OPEN `[F]` |
| `E5` | **CMG-OQ-01 referent** | **AUTHORITY** | *"Which **authority** is competent to ratify CMG-000001?"* | OPEN, undetermined `[F]` |
| `E6` | **Out-of-corpus finality authority** | **AUTHORITY** (exogenous) | `CEP-006` I.4, XII.2; `CEP-000` §6.5, §28.2 | identity *"undetermined"* — `CMG-000001` XLIV.4 `[F]` |
| `E7` | **In-corpus finality authority** | **AUTHORITY** (endogenous) | `CEP-006` XII.2 first limb; `CEP-000` §28.2 first limb | located as `CEP-006::RATIFICATION` (`URAT-REC-02…05`) `[F]` |
| `E8` | **AUTH-13** — Constituent Authority (sovereign seat) | **AUTHORITY** (exogenous) | `01-WORKING/AUTHORITY-REGISTER.md:24`; `UCOS-RAT-001` §2.1 / AMD-01 | identified; holds `CAC-01/02/07` `[F]` |
| `E9` | **AUTH-14** — `RA-Ω∞` | **AUTHORITY** (constituted, derived from `E8`) | `01-WORKING/AUTHORITY-REGISTER.md:25` — *"chartered by and deriving authority from AUTH-13"* | chartered `[F]` |
| `E10` | **EC-1** | **ACT** | `UCOS-RAT-001` §1 — the exogenous constituent act | **PERFORMED** `[F]` |
| `E11` | **SRC-02** | **ARTIFACT** (frozen, binary) | `00-SOURCE/CONSTITUTIONS/UCOS Ω∞ ABSOLUTE ARCHITECTURAL CONSTITUTION.docx`; `01-WORKING/CONSOLIDATION-MATRIX.md:15` | declared *supreme, ratified* by `UCOS-RAT-001` §2.4; recorded *non-normative frozen source* by `VAC-01` `[F]` — **the collision** |

#### Edge set

```
E10 (EC-1) ──performed-by──▶ E8 (AUTH-13)
E8  ──charters──▶ E9 (AUTH-14)                       [AUTHORITY-REGISTER:25]
E10 ──fixes-supremacy-of──▶ E11 (SRC-02)             [UCOS-RAT-001 §2.4]
E2  ──records-vacancy-of──▶ E1                       [CMG-REGISTRY vacancies[0]]
E2  ──declared_superior──▶ E3                        [VAC-01]
E4  ──asks-identity-of──▶ E3
E5  ──competence-over──▶ CMG-000001                  [CMG-OQ-01]
E6  ──sole-mover-of──▶ (PROVISIONAL → FINALIZED)     [CEP-006 XII.2]
E7  ──sole-mover-of──▶ (ACCEPTED → FINALIZED)        [CEP-006 XII.2]
E3  ⟵──is-the-referent-of?──▶ E11                    ** UNPROVED **
E8  ⟵──is-the-same-as?──▶ E6                         ** UNPROVED **
E9  ⟵──is-the-same-as?──▶ E7                         ** UNPROVED **
```

**`[F]` The corpus records the collision explicitly and leaves it undisposed.**
`00-MASTER/UCOS-UCAF-001/04-RECONCILIATION-REPORT.md` opens: *"Where a recorded claim of
authority absence and located evidence of authority presence both stand, **both are Repository
Truth**."* It then records three reconciliations, **all `RECONCILIATION-REQUIRED`, none disposed**:

| Id | Claim | Claim owner | Evidence against |
|---|---|---|---|
| `UCAF-RC-01` | no located authority is competent to ratify | `uccep-bindings.json` | `AUTHORITY-REGISTER`, `UCOS-RAT-001`, `09-DR-RAT-11-ASSESSMENT` |
| `UCAF-RC-02` | no ratified normative artifact occupies the vacant constitutional tier | `CMG-REGISTRY.json` | `AUTHORITY-REGISTER`, `SUPERSESSION-REGISTER`, `UCOS-RAT-001` |
| `UCAF-RC-03` | the corpus contains no authority competent to ratify anything | `00-CMG/README.md` | `AUTHORITY-REGISTER` |

`[F]` A repository-wide search for any disposal of `UCAF-RC-01/02/03` returns **zero disposals**;
every one of the fourteen citing artifacts re-cites the conflict as standing
(`UCAF-F-002 = STANDING-CONSTITUTIONAL-CONFLICT`).

### O1.B — Equality matrix

Complete over the named set. `≡` proved identical · `≠` proved distinct · `?` UNPROVED.

| | `E1` T1 | `E3` occupant | `E5` OQ-01 auth | `E6` out-of-corpus | `E7` in-corpus | `E8` AUTH-13 | `E9` AUTH-14 | `E11` SRC-02 |
|---|---|---|---|---|---|---|---|---|
| **`E1` T1 (slot)** | ≡ | **≠** ¹ | **≠** ¹ | **≠** ¹ | **≠** ¹ | **≠** ¹ | **≠** ¹ | **≠** ¹ |
| **`E3` occupant (artifact)** | ≠ | ≡ | **≠** ² | **≠** ² | **≠** ² | **≠** ² | **≠** ² | **?** ³ |
| **`E5` OQ-01 authority** | ≠ | ≠ | ≡ | **?** ⁴ | **≠** ⁵ | **?** ⁶ | **?** ⁷ | ≠ ² |
| **`E6` out-of-corpus finality** | ≠ | ≠ | ? | ≡ | **≠** ⁸ | **?** ⁹ | **?** ¹⁰ | ≠ ² |
| **`E7` in-corpus finality** | ≠ | ≠ | ≠ | ≠ | ≡ | **≠** ¹¹ | **?** ¹² | ≠ ² |
| **`E8` AUTH-13** | ≠ | ≠ | ? | ? | ≠ | ≡ | **≠** ¹³ | ≠ ² |
| **`E9` AUTH-14** | ≠ | ≠ | ? | ? | ? | ≠ | ≡ | ≠ ² |
| **`E11` SRC-02** | ≠ | ? | ≠ | ≠ | ≠ | ≠ | ≠ | ≡ |

**Proof notes**

1. **`[F]` Type disproof — slot vs occupant.** `CMG-000001` IV.11 defines a Vacant Authority Slot
   as *"a declared superior authority that **no located artifact presently occupies**"*. A slot is
   not its occupant; XVI.8 makes tier identifiers *"symbolic"*. `E1 ≠` everything else by type.
2. **`[F]` Type disproof — artifact vs authority.** `CMG-OQ-02` asks which **artifact** occupies
   T1; `CMG-OQ-01` asks which **authority** is competent to ratify. `VAC-01.declared_superior` is
   a document ("The ratified UCOS Ω∞ Constitution"), not an agent. `CEP-000` §5.5 Tier 1 is
   likewise *"the ratified UCOS Ω∞ Constitution and its concerns"*. **`E3` is a document; `E5`–`E9`
   are agents. No agent can occupy T1 and no document can ratify.** This is the single most
   consequential result of O1: *the two headline open questions are not the same question, and
   closing one cannot close the other.*
3. **`[?]` `E3 ≟ E11`** — the live collision. `UCOS-RAT-001` §2.4 determines *"SRC-02 is the
   supreme governing document, **ratified** (no longer pro tempore)"*. `VAC-01` records the T1
   referent as existing *"only as frozen non-normative source material under
   `00-SOURCE/CONSTITUTIONS/` (.docx). No ratified normative artifact occupies the tier."*
   Both stand. `UCAF-RC-02` is exactly this pair, **undisposed**. **UNPROVED.**
4. **`[?]` `E5 ≟ E6`** — `CMG-000013` R-01 records the owner of `CMG-OQ-01` as *"the out-of-corpus
   finality authority, **or an authority empowered to designate it**"*. The disjunction is
   unresolved and `CMG-000013` is `AUTHORITY = NONE`. **UNPROVED.**
5. **`[F]` `E5 ≠ E7`.** `CMG-000001` XLIV.7 prohibits self-ratification and provides that *"no
   authority SHALL grant itself ratification competence"*; `CEP-000` §5.4 provides that *"no CEP
   agent SHALL grant itself ratification authority"*. `E7` = `CEP-006::RATIFICATION` is in-corpus,
   so it cannot be competent to confer the competence `CMG-OQ-01` seeks. **DISPROVED.**
6/7. **`[?]`** Follow from 4 and 9/10; no located clause identifies or distinguishes them.
8. **`[F]` `E6 ≠ E7`.** `CEP-006` XII.2 uses both terms in one sentence with **different
   consequents** — *"An ACCEPTED determination MAY reach FINALIZED upon **in-corpus** finality
   authority; a PROVISIONAL determination SHALL reach FINALIZED only upon the act of the
   **out-of-corpus** finality authority."* Distinctness is definitional. **DISPROVED.**
9. **`[?]` `E8 ≟ E6`** — **the load-bearing unproved pair.** Discussed at O1.D.
10/12. **`[?]`** `AUTH-14` is chartered by an exogenous act yet operates in-corpus; `URAT`
    records its outputs at `PROVISIONAL` with the note *"in-corpus ratification authority is
    engineering-readiness only"*. Neither identity nor distinctness is stated. **UNPROVED.**
11. **`[F]` `E8 ≠ E7`.** `AUTHORITY-REGISTER:24` — `AUTH-13` is *"exogenous by construction"*;
    `E7` is in-corpus by definition. **DISPROVED.**
13. **`[F]` `E8 ≠ E9`.** `AUTHORITY-REGISTER:25` — `AUTH-14` is *"chartered by and deriving
    authority from AUTH-13 (per AUTH-03)"*. A derivation relation is irreflexive over identity;
    the register classifies `E8` **Constituent** and `E9` **Constituted (derived from AUTH-13)**.
    **DISPROVED.**

### O1.C — Minimal clause set preventing proof

**`[F]`** For the load-bearing pair `E8 ≟ E6`, the proof is blocked by exactly **eight** clauses.
Removing any one does not unblock it; removing the set would unblock it. This is the minimal set.

| # | Clause | What it forecloses |
|---|---|---|
| 1 | `CMG-000001` **XLIV.4** — *"the identity of any out-of-corpus finality authority **is undetermined**"* | Denies `E6` an identity predicate at all |
| 2 | `CEP-006` **XII.2 / I.4** | Names `E6` by **role**, never by identity; supplies no membership test |
| 3 | `09-DR-RAT-11-ASSESSMENT.md` §5 ¶88 — *"**CEP-006 finality binding (S2-08) is a distinct track and is NOT altered here** … It makes **no** claim about CEP-006 absolute FINALIZED state, which S2-08 binds to the out-of-corpus finality authority (CEP-006 Art XII.2)."* | The one document that could have asserted `E8 ≡ E6` **expressly declines** |
| 4 | `UCOS-RAT-001` front matter — *"HELD AUTHORITY: CONSTITUENT + RATIFICATION (exogenous), **governance-only**"* | Bounds `E8`'s exercised competence below constitutional finality |
| 5 | `UCOS-URAT-001/01-RATIFICATION-REGISTER.md` `URAT-REC-01` — state **PROVISIONAL**; *"RATIFIED **at the derived-truth layer** … **constitutional finality not claimed**"* | The canonical ratification record itself withholds the identification |
| 6 | `UCAF-F-003` — competence to ratify and the ratifying act are distinct, and *"only the first is closable by measurement"* | Forecloses derivation of the act from the competence |
| 7 | `CMG-000001` **XIX.2 / LXXXI.5 / XVII.4** | Bars the meta instrument from deciding it; forbids promoting any lower instrument |
| 8 | `CEP-002` **Article 23** referral of `UCAF-RC-01/02/03` | Routes the question to a claim owner who has **not acted** `[F]` |

**`[F]`** The same eight clauses block `E3 ≟ E11` (via 1, 3, 5, 7, 8) and `E5 ≟ E6` (via 1, 2, 6).

### O1.D — Can `A ≡ B` be proved, disproved, or is it permanently undecidable?

**The answer is not uniform across the matrix.** `[I]` It partitions exactly three ways:

**(i) DISPROVED — 7 pair classes, decided at HEAD.**
All type-level pairs (note 1, 2), `E6 ≠ E7` (note 8), `E8 ≠ E9` (note 13), `E8 ≠ E7` (note 11),
`E5 ≠ E7` (note 5). `[F]` These require no external act; the corpus already decides them.

**(ii) UNDECIDABLE AT HEAD, DECIDABLE BY EXTERNAL ACT — `E8 ≟ E6`, `E5 ≟ E6`, `E9 ≟ E7`.**
`[I]` Proof is foreclosed because an identity claim about `E6` would have to be issued by an
authority competent over `E6` — which is `E6` itself (circular, and barred as self-conferral by
`CMG-000001` XLIV.7 and `CEP-000` §5.4) or by the occupant of `E1`, which is `VACANT`.
`[I]` **Disproof is equally foreclosed, and this is the less obvious half:** disproving `E8 ≡ E6`
requires exhibiting a capability `E6` holds that `E8` lacks. The corpus enumerates `E8`'s
capabilities exhaustively (`CAC-01…CAC-07`, all *"PRESENT and EXERCISED"* per `UCOS-RAT-001` §1.1)
but **never enumerates `E6`'s capabilities at all** `[GAP]`. With one side of the comparison
undefined, neither branch is derivable.
`[F]` Both branches are therefore closed *by the state of the corpus, not by logic* — so this is
**undecidability relative to HEAD, not absolute undecidability.** A single commit recording the
identification decides it. Phrasing it as "permanently undecidable" would overstate the finding.

**(iii) UNDECIDABLE AT HEAD, BLOCKED ALSO BY A JURISDICTION BAR — `E3 ≟ E11`.**
`[F]` Beyond (ii), this pair carries an additional block: `GD-21-C3` forbids any consolidation act
from treating `00-SOURCE/CONSTITUTIONS/` `.docx` material as normative, and `GD-21-C1` forbids
nominating a T1 candidate. `[I]` So even an in-corpus actor who *believed* `E3 ≡ E11` is
prohibited from recording it. The disposal owner named by `UCAF-RC-02` is `CMG-REGISTRY.json` —
a **derived projection** (`AUTHORITY = NONE`) `[F]`, which by `CMG-000001` XII.6 asserts nothing.
`[GAP] GAP-O-01` — **`UCAF-RC-02` is referred for disposal to an artifact constitutionally
incapable of disposing anything.** The referral cannot terminate.

---

## O2 — ACT ATOMICITY EXHAUSTIVE SEARCH

Searched: `act`, `constitutional act`, `single act`, `compound act`, `transaction`, `event`,
`operation`, `procedure`, `ratification act`, `acceptance act`, `closure act`, `authority act`
across `00-CEP/`, `00-CMG/`, `00-MASTER/`, and repository-wide.

### O2.A — Is constitutional act atomicity defined? **NO.**

**`[F] GAP-O-02` — atomicity is defined for five *other* subjects and never for an act.**

| Subject | Atomicity clause | Is it an act? |
|---|---|---|
| **Transition** | `CMG-000001` **XXVI.5** — *"Every transition SHALL be evidenced and **atomic**. A transition that leaves the artifact in no state, or in two states, IS a defect."* | No — a state change |
| **Execution unit** | `CEP-003` III.1 — *"the atomic granted work of execution"* | No — a work unit |
| **Domain transition** | `CEP-003` V.5 — *"A transition SHALL be atomic"* | No |
| **Ownership transfer** | `CMG-000001` XX.5 — *"transfer IS atomic"* | No |
| **Concern / Law** | `CMG-000001` XIV.4, `CMG-K-04` | No — entities |
| **Registration** | `REG-AUTO-001` §7/§16.3 Atomic Registration Transaction | No — machinery |
| **CONSTITUTIONAL ACT** | — | **ABSENT** |

`[F]` `CMG-000001` Article IV (Definitions, IV.1–IV.11) defines *Constitution*, *Constitutional
Artifact*, *Meta-Constitutional Matter*, *Vacant Authority Slot* — **and no term "act".**

**`[F]` The two clauses that appear to define it do not.**
`CEP-006` **P.2**: *"Ratification SHALL be **the single constitutional act** through which a
validated and certified artifact becomes an officially accepted member…"*
`CMG-000001` **XLIV.1**: *"**Ratification** IS the single constitutional act by which a validated
and certified artifact becomes an accepted member of the corpus."*
`[I]` Both are **uniqueness-of-kind** claims — *ratification is the only kind of act that confers
membership* — reinforced by `XLIV.5` (*"Ratification SHALL NOT be inferred from certification,
freeze, publication, registration, age, use, or absence of objection. **Each of those is a
distinct act**"*). Neither is a **cardinality** or **indivisibility** claim about a performance.
Reading "single" as "one act" is a category error the corpus nowhere licenses.

### O2.B — Is any implicit atomicity model derivable? **One is derivable; it is unsound.**

`[I]` The only candidate: **acts are individuated by the transitions they license** (XXVI.5
atomicity + XXV.5 *"An artifact SHALL hold exactly one state at any instant"* + `CMG-INV-07`).
`[F]` This model is **refuted by the corpus's own arithmetic**:

- Under it, `PROVISIONAL → RATIFIED` is **one** act (`CMG-T-07`, a single transition).
- `CMG-000007` §5 states `READY` is reachable *"by **exactly two acts**"*.
- `[F]` One transition ≠ two acts. The implicit model contradicts the located count.

**`[I]`** No atomicity model is derivable that is consistent with the corpus. **`GAP-O-02` stands.**

### O2.C — Is there a conflict between XLIV.1, CMG-T-07, DEF-02 and XII.2? **YES — four-way, and it is structural.**

| Instrument | What it says about reaching final acceptance | Act count implied |
|---|---|---|
| `CMG-000001` **XLIV.1** | Ratification IS *the single constitutional act* conferring membership | 1 (of a kind) |
| `CMG-000001` **CMG-T-07** | `PROVISIONAL → RATIFIED`: *"**The vacant authority closes and accepts**"* | **2 events, 1 atomic transition** |
| `UCCEP-000008` **DEF-02** | Exit `UNDER-REVIEW → RESOLVED` requires: *"An external constituent act occurs: an authority **is identified** by explicit ratification **and** `VAC-01` **closes**"* | **2 events, 1 exit** |
| `CEP-006` **XII.2** | `PROVISIONAL → FINALIZED` **only** upon the act of the out-of-corpus finality authority — an act distinct from the acceptance that produced `PROVISIONAL` (VII.2) | **≥ 2 acts in sequence** |

**`[F]` The root of the conflict is a lifecycle-mapping defect, located and self-declared.**

`CMG-000001` **XXV.3** maps the meta-lifecycle onto the located model, and maps
**`CMG-S-07 ↔ RATIFIED / FINALIZED`** — *one meta-state onto two located states.*
`CEP-006` **VI.1** declares nine ratification states — `NOT_ELIGIBLE, ELIGIBLE, DELIBERATING,
ACCEPTED, PROVISIONAL, DEFERRED, REJECTED, APPEALING, FINALIZED` — in which:
- `RATIFIED` **is not a state at all**; and
- `FINALIZED` is a **distinct terminal state** (VI.2) reachable from `PROVISIONAL` **only** by the
  `E6` act (XII.2).

`[F]` Consequences, each independently checkable:

1. **The mapping is non-injective at exactly the state where cardinality is decided.**
   `CMG-S-07` absorbs both `RATIFIED` and `FINALIZED`, collapsing the very distinction `XII.2`
   uses to require a second act. `XXV.5` then requires *exactly one* state — so a `CMG-S-07`
   artifact is simultaneously mapped to two located conditions, which `XXVI.5` calls *"a defect"*.
2. **The mapping is not total.** Six of `CEP-006`'s nine states — `NOT_ELIGIBLE`, `ELIGIBLE`,
   `DELIBERATING`, **`ACCEPTED`**, `DEFERRED`, `APPEALING` — have **no image** in `XXV.3`.
   `ACCEPTED` is the critical omission: `XII.2`'s *first limb* turns on it (`ACCEPTED` → one act;
   `PROVISIONAL` → two). **The CMG lifecycle cannot express the distinction that decides the count.**
3. **`CMG-T-07` compounds two `CEP-006` acts into one atomic transition** — vacancy closure
   (a `CMG-OQ-02` matter) and acceptance (a `CMG-OQ-01` matter) — which `GD-21-C7` separately
   forbids bundling (see O2.D).
4. **`XXV.3` contains its own conflict rule, and it is unsatisfied.** *"Where the located model
   and this mapping disagree, **the located model governs** and this mapping **SHALL be corrected
   by amendment**."* `[F]` The located model (`CEP-006` VI.1) and the mapping **do** disagree.
   `[F]` No such amendment exists at HEAD. **`GAP-O-03` — a self-declared mandatory amendment is
   outstanding.** `[I]` This is the strongest single candidate for the referent of `D-14`.

### O2.D — Admissible cardinality models

`[F]` **Acts already performed:** exactly one — `EC-1`, by `AUTH-13` (`UCOS-RAT-001` §1;
`09-DR-RAT-11-ASSESSMENT` §5; `URAT-REC-01`). `[F]` **It did not close `VAC-01`**: the registry
records `located: false` at HEAD and the validator reports `vacancies recorded : 1`.

| Model | Claim | Located support | Eliminated? |
|---|---|---|---|
| **Model 0** | **0 further external acts** — `EC-1` sufficed | `UCOS-RAT-001` §7 *"All entry criteria are satisfied"*; `DR-RAT-11 BLOCKED → RATIFIED` | **`[F]` ELIMINATED.** `CMG-REGISTRY.json` `VAC-01.located=false`; `URAT-REC-01` state `PROVISIONAL`, *"constitutional finality not claimed"*; `09-DR-RAT-11` §5 ¶88 *"makes **no** claim about CEP-006 absolute FINALIZED state"*; `UCCEP-F-004` **RETAINED as blocking** after amendment |
| **Model A** | **1 external act** — one act identifies the ratifier, decides T1 and finalizes | `UCOS-Ω∞-CONSTITUENT-AUTHORITY-DETERMINATION-REPORT` §8 — *"if an exogenous authority possessing CAC-01…CAC-07 performs **the single founding act** (identify sovereign seat + charter ratifier + fix precedence)"*; `CMG-T-07` (*"closes **and** accepts"* as one transition) | **`[F]` NOT ELIMINATED** as an act structure. `[F]` But **eliminated as a recordable in-corpus disposition** — see below |
| **Model B** | **2 external acts** — R-01 (close `CMG-OQ-01`) then R-02 (close `CMG-OQ-02` + `VAC-01`) | `CMG-000007` §5 *"`READY` is reachable by **exactly two acts**"*; `CMG-000013` R-01/R-02 | **`[F]` NOT ELIMINATED**, but **not authoritative** — both sources are `AUTHORITY = NONE (DERIVED TRUTH)`, and §O6/`DIV-02` shows the "two acts" arithmetic is **false against the executed validator** |
| **Model C** | **3 external acts** — `EC-1` (done) + T1 occupancy (`DEF-02`) + `CEP-006` XII.2 finality | `09-DR-RAT-11` §5 ¶88 — finality is *"a **distinct track**"*; `DEF-02` element 6; `S2-08` F-05 | **`[F]` NOT ELIMINATED.** `[I]` The **only** model simultaneously consistent with every located instrument |
| **Model C′** | **up to 5 external decisions** — adding `CMG-OQ-03` and `CMG-OQ-07`, each `"requires": "EXPLICIT RATIFICATION"` and each owned by *"an authority above both axes (presently vacant)"* | `CMG-REGISTRY.json → open_questions`; `CMG-000013` R-03 | **`[F]` NOT ELIMINATED** |

#### The decisive derivation: **act cardinality and record cardinality are different quantities, and the corpus constrains only the second**

`[F]` `GD-21-C7`: *"`CMG-OQ-01`, `CMG-OQ-03`, `CMG-OQ-05` and `CMG-OQ-07` SHALL NOT be treated as
resolved, narrowed, or **bundled** with this matter."*

`[F]` `GD-21` **disclaims jurisdiction over the matter itself** — `DEF-02` element 3:
*"It claims **no** jurisdiction over the matter"*; element 6 names the owner as *"an external
constituent authority"*, *"expressly **not** any located instrument"*.
`[I]` A constraint cannot bind beyond its issuer's jurisdiction (`CMG-000001` XVII.8, XIX.4).
Therefore `GD-21-C7` **cannot** forbid an external authority from performing one bundled act.

`[I]` **Result:**
- **External-act cardinality** — minimum **1**, and *not bounded above by any located clause*.
- **In-corpus record cardinality** — **at least 2 separate governed determinations**, because
  `GD-21-C7` forbids recording `CMG-OQ-01` and `CMG-OQ-02` as bundled, and `GD-21-C5` forbids exit
  by silence, and `CEP-002` 27.11 forbids `RECORDED → RESOLVED` directly.

`[I]` **This dissolves the apparent contradiction between Model A and Model B.** They are not
competing answers to one question; they answer two different questions the corpus never
distinguishes. Model A is admissible as an *act*; Model B is mandatory as a *record*.

`[F]` **No model in {A, B, C, C′} is eliminated by corpus text.** Only Model 0 is eliminated.

---

## O3 — `D-14` ROOT CAUSE DETERMINATION

*Answered over the named quadruple; see O0 for the `UNK-01` scope correction.*

### O3.A — Which artifact is authoritative?

**`[F]` `CMG-000001` — the constitutional text — is authoritative, unambiguously and by four
independent declarations:**

| Clause | Text |
|---|---|
| `CMG-000001` XVI.2 col. "Located status" | The tier table is constitutional content |
| `CMG-REGISTRY.json` `authority` field | `NONE (DERIVED TRUTH)` — self-declared |
| `CMG-000001` XII.6 / L.6 | Derived truth *"asserts nothing on its own authority"* |
| `cmg_validate.py` module docstring | *"This tool **IS DERIVED TRUTH** … It recomputes what CMG-000001 already declares"* |
| `CMG-000001` XVI.2 row T5 | *"State, checkpoints, evidence, reports, registries, **projections** — **assert nothing**"* |

`[I]` The hierarchy is total and uncontested: **text ▸ projection ▸ validator.**

### O3.B — Is `D-14` a drafting, projection, registry, or constitutional defect?

**`[F]` The tier lattice itself is CLEAN.** Machine-verified this session: the registry's
`subordinate_to` graph is an exact **transitive reduction** of XVI.3's *"every tier subordinate to
every tier above it, except where an orthogonality is declared in XVI.4"*. All 16 relations that
XVI.3 requires but the projection omits directly are recoverable by transitive closure
(`tier_reachable`); **zero** are unrecoverable. `orthogonal_tier_pairs` matches XVI.4's *"exactly"*
three pairs. **No cardinality defect exists in XVI.2/XVI.3/XVI.4 vs. the registry.**

`[I]` **The defect is therefore not in the lattice. It is a DRAFTING DEFECT in `CMG-000001`
XXV.3, amplified into a PROJECTION DEFECT and rendered undetectable by a VALIDATOR SCOPE
DEFECT** — a three-layer compound, classified per layer:

| Layer | Classification | Evidence |
|---|---|---|
| `CMG-000001` **XXV.3** maps `CMG-S-07 ↔ RATIFIED / FINALIZED`; omits `ACCEPTED` and five other `CEP-006` VI.1 states | **DRAFTING DEFECT** — and **self-declared**: XXV.3's own conflict rule requires correction by amendment `[F]` | O2.C |
| `CMG-REGISTRY.json` `states[]` carries only `{id, state, phase}`; **no `XXV.3` mapping at all**. `transitions[]` carries only `{id, from, to}`; **no condition** — `CMG-T-07`'s *"the vacant authority closes and accepts"* is **absent from the projection** | **PROJECTION DEFECT** — lossy `[F]` | machine-verified |
| `cmg_validate.py` compares the projection to the canonical **text** on only four axes: identifier families, closed-enumeration *closing-invariant strings*, article headings, and the `VERSION` string. It never compares tier members, state members, transition members, orthogonal pairs, vacancy records, `blocks` strings, or the readiness ceiling | **VALIDATOR SCOPE DEFECT** `[F]` | source read + executed |

`[F]` **A constitutional inconsistency also exists, and it is separate:** `CMG-000001` has **no
`FINALIZED` state** (one occurrence in 2,000+ lines, inside the XXV.3 mapping itself), while
`CEP-006` VI.2 makes `FINALIZED` **terminal**. `[I]` The meta layer cannot represent the terminal
state of the ratification lifecycle it recognizes.

### O3.C — Exact minimum artifact set affected

`[F]` **Five artifacts. No more, no fewer.**

| # | Artifact | Change class required (not proposed here) |
|---|---|---|
| 1 | `00-CMG/CMG-000001-…md` XXV.3 | Amendment — mandated by XXV.3's own conflict rule; **MAJOR** under XXIX.4 (a lifecycle-mapping correction), so the full `XLIV` path applies |
| 2 | `00-CMG/CMG-REGISTRY.json` `states[]` | Regeneration to carry the mapping |
| 3 | `00-CMG/CMG-REGISTRY.json` `transitions[]` | Regeneration to carry conditions |
| 4 | `00-CMG/tools/cmg_validate.py` | New check binding projected enumerations to canonical text |
| 5 | `00-CMG/CMG-000007-…md` §5 | Its *"exactly two acts"* arithmetic is false against the validator (`DIV-02`) |

`[F]` **Blast radius beyond the minimum set:** `CMG-000001` **LXXX.6 / LI.5** — *"Amendment to
CMG-000001 → **Automatic revocation** [of certification]"* (`CMG-000007` §6). `[I]` Any correction
of item 1 revokes the meta layer's certification and requires full re-validation of all 44
recognized artifacts. `[I]` This is why the defect has survived: **correcting it is more expensive
than recording it**, and `CMG-000001` VIII.5 (*honesty over completeness*) permits recording.

### O3.D — Do hidden inconsistencies exist because validators consume projections instead of constitutional text?

**`[F]` YES — and the count is bounded and exactly derivable.**

`[F]` `cmg_validate.py`'s docstring states the design intent explicitly:
> *"`CMG-L-08` / LXVI.5 **zero hard coding** — this module contains **NO** member of any
> constitutional enumeration. Every kind, standing, reach, phase, state, transition, relationship
> type, tier, namespace, artifact, concern, vacancy, gap and open question **is read from
> `CMG-REGISTRY.json`**."*

`[I]` **The clause that guarantees the validator cannot hard-code the constitution is the same
clause that guarantees it cannot check the constitution.** `CMG-L-08` compliance and text-binding
are, as currently realized, mutually exclusive. This is the systemic root, not an oversight.

`[F]` **Impact radius — exhaustive, by projection collection:**

| Collection | Members | Bound to text? | Silently mutable? |
|---|---|---|---|
| `identifier_families` (11) | prefixes | **YES** — `CMG_MEMBER_RE` over canonical text | No |
| `closed_enumerations` (4) | closing-invariant strings | **PARTIAL** — invariant *name* must appear in text; **members are never compared** | **Yes (members)** |
| `conformance_map` (80) | article ordinals | **YES** — `ARTICLE_RE` + roman ordinal | No |
| `closing_articles` (6) | numerals | **YES** | No |
| `canonical_source_version` | version string | **YES (string equality only)** | See `DIV-01` |
| `namespaces` (17) | tokens, owners, widths | **NO** | **Yes** |
| `kinds` (24) | `CMG-K-*` | **NO** | **Yes** |
| `standings` (6) · `reaches` (5) · `phases` (3) | members | **NO** | **Yes** |
| `states` (14) | `CMG-S-*` | **NO** | **Yes** |
| `transitions` (22) | `CMG-T-*` | **NO** | **Yes** |
| `relationship_types` (16) | types | **NO** | **Yes** |
| `tiers` (8) | `T*` + `subordinate_to` | **NO** | **Yes** |
| `orthogonal_tier_pairs` (3) | pairs | **NO** | **Yes** |
| `vacancies` (1) | `VAC-01.located` | **NO** | **Yes — governance-critical** |
| `artifacts` (44) | id/path/tier/state | **PARTIAL** — path existence only | **Yes (tier, state)** |
| `concerns` (61) · `gaps` (9) | records | **NO** | **Yes** |
| `open_questions` (7) | `blocks` strings | **NO** | **Yes — governance-critical** |
| `readiness.declared_ceiling` | ceiling | **NO** | **Yes — governance-critical** |

**`[F]` 14 of 19 collections are unbound to constitutional text. 3 are governance-critical.**

---

## O4 — `CMG-OQ-03` DEPENDENCY ANALYSIS

`[F]` **`CMG-OQ-03`** — *"Is the meta axis (T1M) correctly declared orthogonal to the process axis
(T2), rather than superior or subordinate?"* · `requires: EXPLICIT RATIFICATION` ·
`blocks: "Finality of the precedence lattice"`.

`[F]` **Its owner is stated and is downstream, not upstream.** `CMG-000013` R-03:
> *"**Owner:** an authority above both axes (**presently vacant — depends on R-01/R-02**)."*

And `CMG-000001` LXXVIII.3: *"Declaring rank between the axes would require an authority above
both, which **is presently vacant**."*

### Dependency DAG

```
                    ┌──────────────────────────────────────────┐
                    │  EXTERNAL CONSTITUENT / FINALITY DOMAIN  │
                    └──────────────────────────────────────────┘
                                      │
              ┌───────────────────────┴───────────────────────┐
              ▼                                               ▼
        CMG-OQ-01                                       CMG-OQ-02
   (competent ratifier)                              (T1 occupancy)
              │                                               │
              │                                    ┌──────────┴──────────┐
              │                                    ▼                     ▼
              │                                VAC-01              CMG-GAP-04
              │                                    │                     │
              │                                    ▼                     │
              │                                 DEF-02  ◀────────────────┘
              │                                    │
              └────────────────┬───────────────────┘
                               ▼
                     "authority above both axes"
                               │
                               ▼
                          CMG-OQ-03  ──────▶  finality of the XVI lattice
                               │
                               ▼   (validator readiness path only)
        UCCEP-F-004  ◀── CEP-006 I.4 / XII.2  (INDEPENDENT ROOT — see O5)
                               │
                               ▼
                     Governance Completion
```

### Edge classification

| Edge | Class | Basis |
|---|---|---|
| `CMG-OQ-01` → `CMG-OQ-03` | **REQUIRED** (`CMG-OQ-03` is downstream) | `CMG-000013` R-03 *"depends on R-01/R-02"* `[F]` |
| `CMG-OQ-02` → `CMG-OQ-03` | **REQUIRED** (downstream) | same `[F]` |
| `CMG-OQ-03` → `D-14` *(as derived in O3)* | **UNRELATED** | `[I]` `D-14` is a lifecycle-mapping defect (Article XXV) and the tier lattice (Article XVI) is machine-verified clean; the two share no clause |
| `CMG-OQ-03` → `DEF-02` | **UNRELATED**, with one contingent edge | `[F]` `GD-21-C7` expressly bars bundling `CMG-OQ-03` with `DEF-02`. `[F]` The **only** link is `DEF-02`'s `UNDER-REVIEW → WITHDRAWN` trigger — *"the matter is displaced by a later canonical definition of the tier model … **adjacent to** open question `CMG-OQ-03`"*. `[I]` "Adjacent", contingent, and non-blocking |
| `CMG-OQ-03` → `UCCEP-F-004` | **UNRELATED** | `[F]` `UCCEP-F-004`'s surviving basis after amendment is `CEP-006` I.4 alone; it cites no Article XVI clause |
| `CMG-OQ-03` → Governance Completion | **BLOCKING** *(machine)*, **NOT REQUIRED** *(text)* | See the split below |

### **`[F]` The determinative result: `CMG-OQ-03` must NOT resolve before `D-14`, `DEF-02` or `UCCEP-F-004` — but it DOES block Governance Completion, and only because of a validator defect.**

`[F]` Executed this session. `readiness()` in `cmg_validate.py` classifies an open question as
blocking iff `blocks` is non-empty and does not begin with the literal string `"Nothing"`:

```
CMG-OQ-01  blocking=True    CMG-OQ-05  blocking=True
CMG-OQ-02  blocking=True    CMG-OQ-06  blocking=False  ("Nothing; recognition is achieved…")
CMG-OQ-03  blocking=True    CMG-OQ-07  blocking=True
CMG-OQ-04  blocking=False   ("Nothing; CMG-GAP-02 IS CLOSED…")
```

`[F]` **Simulation — close only `CMG-OQ-01`, `CMG-OQ-02` and `VAC-01` (Model B, the corpus's own
"exactly two acts"):**

```
readiness()  ->  READY-PROVISIONAL
remaining blocking OQs:  ['CMG-OQ-03', 'CMG-OQ-05', 'CMG-OQ-07']
```

`[F]` **`CMG-000007` §5's claim — *"On completion of both … the computed outcome becomes `READY`"*
and *"No other act shortens this path"* — is FALSE against the executed validator.**
`[I]` `CMG-OQ-03` is thereby promoted from a downstream ratification question into a *de facto*
blocker of Governance Completion — **not by any constitutional clause, but by a string-prefix
comparison in derived-truth code.**

---

## O5 — IMPOSSIBILITY BASIS MINIMIZATION

### O5.A — Are `{DEF-02}` and `{UCCEP-F-004}` truly irreducible? **YES — but not for the expected reason.**

`[F]` **`UCCEP-F-004` has been AMENDED, and the amendment narrowed its basis.**
`00-MASTER/UCCEP-000000/17-ASSIMILATION-FINDINGS-REGISTER.md` §`UCCEP-F-004`:
> *"**AMENDED, and deliberately RETAINED as blocking.** It is retained because it IS the finality
> ceiling and the ceiling is correct: **`CEP-006` I.4 caps every in-corpus determination at
> provisional acceptance** … It is amended because its original wording — *that no located
> authority is competent to ratify* — **is contradicted by committed Repository Truth**."*

`[I]` **Post-amendment, the two bases are disjoint:**

| Basis | Ground | Survives closure of the other? |
|---|---|---|
| `DEF-02` | T1 occupancy — `CMG-000001` XVII.4 + `CMG-L-12` + `VAC-01` + `CMG-OQ-02` | — |
| `UCCEP-F-004` | **`CEP-006` I.4 alone** — finality reserved to an out-of-corpus authority | **YES** |

### O5.B — Are they independent? **NO — and the asymmetry is the whole result.**

`[I]` **`DEF-02 ⟹ UCCEP-F-004`.** If T1 is vacant, `CMG-000001` XVII.4 requires *"every dependent
determination"* to be PROVISIONAL under `CMG-L-12`. `[F]` `VAC-01.provisional_consequence` states
this in terms: *"Every determination depending on T1 — **including the standing of `CMG-000001`
itself** — is PROVISIONAL."* That **is** a finality ceiling. **The implication holds.**

`[I]` **`UCCEP-F-004 ⇏ DEF-02`.** `CEP-006` I.4 caps in-corpus determinations at PROVISIONAL
*whenever* finality is out-of-corpus. That is true **whether or not** T1 is occupied: a fully
occupied T1 with out-of-corpus finality still yields the ceiling. **The converse fails.**

### O5.C — Does one imply the other? **One-way only: `DEF-02 ⟹ UCCEP-F-004`, not conversely.**

### The proof that minimization is impossible

**`[I]` Theorem.** The impossibility basis `{DEF-02, UCCEP-F-004}` cannot be reduced to a
singleton, in either direction.

**Proof.**
Let `P` = *"a determination in this corpus reaches FINALIZED / READY at HEAD"*.

1. `[F]` `DEF-02` ⟹ ¬`P` — by `CMG-000001` XVII.4 + `CMG-L-12` + `VAC-01`.
2. `[F]` `UCCEP-F-004` ⟹ ¬`P` — by `CEP-006` I.4 + XII.2 + XII.3.
3. `[I]` **`¬P` is overdetermined:** two *independently sufficient* grounds.
4. `[I]` **Drop `DEF-02`:** `UCCEP-F-004` still yields ¬`P` (step 2 cites no T1 clause). Basis
   does not shrink. **Reduction to `{UCCEP-F-004}` fails to preserve `DEF-02`'s distinct content**
   (T1 occupancy is a live matter with its own owner, exit conditions and review point per
   `CEP-002` 27.4).
5. `[I]` **Drop `UCCEP-F-004`:** `DEF-02` still yields ¬`P` (step 1). But `CEP-006` I.4 remains in
   force **independently**, so `¬P` would survive `DEF-02`'s closure — which the reduced basis
   could not express. **Reduction to `{DEF-02}` fails to preserve the residual ceiling.**
6. `[I]` A set of independently-sufficient causes admits **no** minimization that preserves the
   consequence *and* its persistence conditions. ∎

`[F]` **Corroboration from located text.** `DEF-02` element 6 and `07-DEFERRAL-ENTRIES.md` §4 keep
them separate for exactly this reason: *"`DEF-01` … because located records genuinely disagree …
`DEF-02` because **no authority exists at all**. **Neither resolves the other.**"*

### O5.D — Can either be rewritten as a deeper constitutional root? **YES — both reduce to one root, which is itself irreducible.**

`[I]` **`ROOT-Ω` — a corpus cannot confer on itself the standing it lacks.**
Instantiated, without remainder, by:

| Instantiation | Clause |
|---|---|
| Program non-self-elevation | `CEP-000` §5.4 — *"no CEP agent SHALL grant itself ratification authority"* |
| Meta non-self-elevation | `CMG-000001` LXXXI.6, `CMG-L-04` |
| Self-ratification prohibition | `CMG-000001` XLIV.7 — *"no authority SHALL grant itself ratification competence"* |
| Vacancy non-promotion | `CMG-000001` XVII.4 — *"SHALL NOT skip the tier and SHALL NOT promote a lower instrument into it"*; voided by LXXXI.5 |
| Standing ceiling | `CMG-L-12` — conferred standing never exceeds the conferrer's |
| Finality externality | `CEP-000` §6.5; `CEP-006` I.4, XII.2 |

`[F]` **`ROOT-Ω` is proved irreducible by the corpus itself.**
`02-MASTER/UCOS-Ω∞-CONSTITUENT-AUTHORITY-DETERMINATION-REPORT.md`:
> *"Constituent power is by definition non-derived … Derivation would require: authorization
> (`AUTH-04`) → from sovereignty (`AUTH-03`) → which cannot be assumed/fabricated (`AUTH-06`) — a
> **closed circle with no internal seed**. INVARIANT `Ω-010` + `CM-007` make the founding act
> itself a ratification-requiring structural change, so any internally-derived candidate is
> trapped by the very rule it would need to bypass. **Derivation is therefore logically foreclosed.**"*

`[I]` **But the same report bounds the impossibility, and this bound is the most important
positive result in Phase O:**
> *"The deadlock is **breakable** because it is a **missing seed**, not a **contradiction**."*

`[I]` `ROOT-Ω` therefore yields **incompleteness, not inconsistency**. `[F]` `EC-1` demonstrates
the seed can be supplied: `AUTH-13` supplied it once, and the corpus accepted it without
paradox (`AUTH-06` honored — *"not fabricated from within the constituted order"*).

### **`[I]` The strongest form of the impossibility proof available at HEAD**

> Not: *"finality is impossible."*
> But: **"finality is underivable, and exactly one class of input — an exogenous act of the kind
> `EC-1` instantiates — resolves it. That class is non-empty at HEAD, proven by `EC-1`'s
> performance. What remains open is not whether the class can be exercised, but **how many
> exercises the corpus requires** — and that is undecidable because act atomicity is undefined
> (`GAP-O-02`)."**

`[I]` `[O5 answer to "can the proof be strengthened"]` **The impossibility proof cannot be
strengthened; it can only be weakened, and correctly so.** `EC-1`'s performance already converted
it from *"no authority exists"* to *"one authority acted, in a bounded capacity, and the residue is
a cardinality question."* Any restatement asserting categorical impossibility is now
**contradicted by committed Repository Truth**, exactly as the `UCCEP-F-004` amendment records.

---

## O6 — MACHINE / CORPUS DIVERGENCE AUDIT

Ranked by governance impact. **Located** = demonstrated at HEAD. **Potential** = mechanism proven,
instance not present. **Undetectable** = no gate could observe it.

### Located divergences

| Id | Divergence | Impact | Evidence |
|---|---|---|---|
| **`DIV-01`** | **The registry↔text binding is a VERSION-STRING comparison, not a content hash.** `check_source_binding` compares `canonical_source_version` to the `VERSION` front-matter row. `[F]` Verified: `cmg_validate.py` contains **no** `hashlib`, `sha256`, `digest` or `content_hash`. **The entire constitutional text may change arbitrarily with `VERSION` held fixed and the gate stays green.** | **CRITICAL** | source read; grep |
| **`DIV-02`** | **`CMG-000007` §5's "exactly two acts" is false against the validator.** Closing `CMG-OQ-01` + `CMG-OQ-02` + `VAC-01` yields `READY-PROVISIONAL`, not `READY`; `CMG-OQ-03/05/07` remain blocking. | **CRITICAL** — the corpus's own published closure path does not work | executed simulation |
| **`DIV-03`** | **`CMG-000001` XXV.3's mandatory self-correction is outstanding** (`GAP-O-03`); `CMG-S-07 ↔ RATIFIED / FINALIZED`; six `CEP-006` VI.1 states unmapped, `ACCEPTED` among them. | **CRITICAL** — root of the O2 cardinality conflict | O2.C |
| **`DIV-04`** | **`LXXX.4`'s ceiling is enforced from the projection, not the text.** `run()` reads `registry.readiness.declared_ceiling`. Amending `LXXX.4` alone does **not** lift the ceiling; editing the JSON alone **does**. | **CRITICAL** — the anti-drift mechanism is itself drift-prone | source read + simulation |
| **`DIV-05`** | **Governance state is switched by a string prefix.** `readiness()` blocks on `not str(blocks).startswith("Nothing")`. `CMG-OQ-04` and `CMG-OQ-06` are non-blocking **solely** because their prose begins with the word "Nothing". Rewording either — with no change of meaning — re-blocks the corpus. | **HIGH** | source read |
| **`DIV-06`** | **The projection is lossy at the semantic layer.** `transitions[]` carry no condition — `CMG-T-07`'s *"the vacant authority closes and accepts"* exists **only** in prose. `states[]` carry no XXV.3 mapping. | **HIGH** — the acts in question are literally not in the machine model | machine-verified |
| **`DIV-07`** | **Three incompatible "tier" vocabularies collide in the identity chain.** (i) `CMG-000001` XVI.2 `T0…T5`; (ii) `CEP-000` §5.5 `Tier 1…4` (four tiers, no `T1M`/`T2I`); (iii) `UCOS-RAT-001` `Tier-0/1/2` capability-closure tiers **and** *"Terminal **T4**"* **and** *"sealed reconciled **T2→T1→T3→T4→T5** baseline"*. `[F]` `CMG-000001` XVI.5 asserts `CEP-000` §5.5 *"IS a refinement within a tier of this lattice"* — but §5.5's Tier 3 (Execution) is XVI.2's `T4`, and §5.5's Tier 4 (Derived-Truth) is XVI.2's `T5`. | **HIGH** — "Terminal T4" in the ratification act is *not* XVI.2's `T4` Execution Authority; nothing in the corpus says so | text comparison |
| **`DIV-08`** | **`UCAF-RC-02` is referred for disposal to `CMG-REGISTRY.json`** — a `AUTHORITY = NONE` projection that by XII.6 asserts nothing (`GAP-O-01`). | **HIGH** — the referral cannot terminate | `04-RECONCILIATION-REPORT.md` |
| **`DIV-09`** | **`CMG-000007` §5 and `CMG-000013` R-01/R-02 assert an identity the corpus elsewhere refuses** — *"Owner: **the same authority as R-01**"* for `CMG-OQ-02`. `[F]` Both artifacts are `AUTHORITY = NONE`. This is `E5 ≡ E6 ≡` the T1 decider, asserted by derived truth. | **MEDIUM** — an unauthorized identity claim in the closure path | O1.B note 4 |

### Potential divergences

| Id | Mechanism | Why not located |
|---|---|---|
| `DIV-P-01` | 14 of 19 registry collections unbound to text (O3.D) — any member may be silently added, removed or altered | No instance found; all 19 currently agree by inspection |
| `DIV-P-02` | `check_closed_enumerations` verifies the *closing invariant name* appears in text but **never compares members** — a CLOSED enumeration may silently gain a member | `closed_enumerations` (4) currently consistent |
| `DIV-P-03` | `artifacts[].tier` and `.state` unbound — an artifact could be projected into a tier it does not claim | 44 artifacts currently consistent; note **0** at `T0` and **0** at `T1` `[F]` |
| `DIV-P-04` | `vacancies[].located` unbound — flipping it to `true` closes `VAC-01` in the machine with no textual act, exactly what `GD-21-C4` forbids | Currently `false` |

**`[F]` Adversarial demonstration, executed this session:** editing **only** `CMG-REGISTRY.json` —
setting all `blocks` to `"Nothing"`, `VAC-01.located = true`, and `declared_ceiling = "READY"` —
yields `FINAL -> READY` with **0 findings**, while `CMG-000001` LXXX.4 still textually declares
`READY-PROVISIONAL at most` and `XVII.4` still records T1 vacant.
`[I]` **The full governance posture of the meta layer is reachable by editing one derived file.**

### Undetectable divergences

| Id | Divergence | Why no gate can observe it |
|---|---|---|
| `DIV-U-01` | **Semantic drift of constitutional prose under a fixed `VERSION`.** | `DIV-01`: no content hash. Only a human diff detects it. |
| `DIV-U-02` | **Whether `E3 ≡ E11`** (is `SRC-02` the T1 occupant?). | `[F]` `SRC-02` is a 705 KB binary `.docx` outside every registry; `GD-21-C3` forbids treating it as normative; no tool parses it. |
| `DIV-U-03` | **Whether `EC-1` discharged `CEP-006` XII.2.** | `[F]` `09-DR-RAT-11` §5 ¶88 declines to say; no gate evaluates `FINALIZED`; `CMG-000001` has no `FINALIZED` state to evaluate (`DIV-03`). |
| `DIV-U-04` | **Whether `CMG-000001` XVI.5's claim that `CEP-000` §5.5 is "a refinement within a tier" is true.** | `[F]` `CEP-000` is a `T2` artifact; the claim is *about* it; `CMG-000013` R-05 routes confirmation to `CEP-000`'s steward, who has not confirmed. No machine check exists. |
| `DIV-U-05` | **Whether the `CMG-000001` prose and the registry describe the same 22 transitions.** | `[F]` `DIV-06`: conditions absent from the projection, so the comparison has no machine-readable right-hand side. |

`[I]` **Ranking summary.** `DIV-01` is the highest-impact single finding: it is the clause on which
every other projection guarantee rests, and it is a **string comparison**. `DIV-04` is the
highest-impact *governance* finding: the mechanism `CMG-000007` §4 describes as *"the mechanism
that prevents provisional readiness from silently becoming final readiness"* is itself stored in
the file it is meant to police.

---

## O7 — TERMINAL DETERMINATION

### 1. What remains unknown?

| Id | Unknown |
|---|---|
| `UNK-01` | The literal statement of Phase N's `D-14` (not present at HEAD) |
| `UNK-02` | Whether `AUTH-13` (`E8`) is the `CEP-006` XII.2 out-of-corpus finality authority (`E6`) |
| `UNK-03` | Whether `SRC-02` (`E11`) is the T1 occupant (`E3`) — `UCAF-RC-02`, undisposed |
| `UNK-04` | The **capability set of `E6`** — `CAC-01…07` enumerate `E8`'s; `E6`'s are never enumerated |
| `UNK-05` | Whether `AUTH-14` (`E9`) is the in-corpus finality authority (`E7`) |
| `UNK-06` | Whether one external act may lawfully close both `CMG-OQ-01` and `CMG-OQ-02` — `GD-21-C7` forbids the *record*, and cannot reach the *act* |

### 2. What remains unprovable?

`[I]` **Nothing is unprovable in the absolute sense.** Every open item is **undecidable relative
to HEAD** and decidable by an input the corpus can receive. Precisely:

| Item | Status | Decidable by |
|---|---|---|
| `E8 ≟ E6`, `E5 ≟ E6`, `E9 ≟ E7` | undecidable at HEAD — **both** branches foreclosed (O1.D(ii)) | one recorded identification |
| `E3 ≟ E11` | undecidable at HEAD **+ jurisdiction-barred** (O1.D(iii)) | disposal of `UCAF-RC-02` by a competent owner |
| Act cardinality | **not undecidable — UNDEFINED** (`GAP-O-02`) | defining act atomicity |
| `ROOT-Ω` | **irreducible**, proved (O5.D) | not applicable — it is a boundary, not a defect |

`[F]` The corpus's own characterization is exact and is adopted here: *"a **missing seed**, not a
**contradiction**."*

### 3. What remains externally rooted?

| Item | Root | Located classification |
|---|---|---|
| `CMG-OQ-01` | `E5`/`E6` | `requires: EXPLICIT RATIFICATION` |
| `CMG-OQ-02` / `VAC-01` / `CMG-GAP-04` / `DEF-02` | external constituent authority | `ED-1`, *"not manufacturable"*; `RU-19` *"NOT ACTIONABLE IN-REPOSITORY"* |
| `CMG-OQ-03` | *"an authority above both axes (presently vacant)"* | `requires: EXPLICIT RATIFICATION` |
| `CMG-OQ-07` | ratifying authority | `requires: EXPLICIT RATIFICATION` |
| `CEP-006` XII.2 finality | `E6` | *"a **distinct track**"* — `09-DR-RAT-11` §5 ¶88 |
| `UCCEP-F-004` | `CEP-006` I.4 | `STANDING-CONSTITUTIONAL-CEILING`, RETAINED as blocking |
| **NOT externally rooted** | `CMG-OQ-05` (`requires: OWNERSHIP ALLOCATION BY THE PROCESS OWNER` — in-corpus); `GAP-O-03` / `DIV-01…06` (all in-corpus engineering) | |

### 4. Minimum and maximum external acts

**`[I]` The question is ill-posed at HEAD, and the ill-posedness is the finding.**

| Quantity | Value | Basis |
|---|---|---|
| **External acts already performed** | **exactly 1** (`EC-1`) | `UCOS-RAT-001` §1; `URAT-REC-01` `[F]` |
| **Minimum further external acts** | **1** | Model 0 eliminated `[F]`; Model A not eliminated `[F]` |
| **Maximum further external acts** | **unbounded by any located clause**; **5 enumerable distinct external decisions** (`OQ-01`, `OQ-02`/`VAC-01`, `OQ-03`, `OQ-07`, `CEP-006` XII.2 finality) | `CMG-REGISTRY → open_questions`; `CEP-006` XII.2 `[F]` |
| **Minimum in-corpus governed determinations recording them** | **≥ 2** | `GD-21-C7` (no bundling), `GD-21-C5` + `CEP-002` 27.11/27.12 (no silent or direct exit) `[F]` |

`[I]` **Minimum ≠ maximum, and no located clause closes the interval**, because the corpus
constrains only how acts are **recorded**, never how they are **performed** — and never defines
what makes a performance one act.

### 5. Can cardinality be conclusively derived? **NO — and the reason is definitional, not evidential.**

`[F]` `GAP-O-02`: **constitutional act atomicity is nowhere defined.** Atomicity is defined for
transitions, transactions, execution units, ownership transfers, concerns and laws — never for an
act. `[F]` `CMG-000001` Article IV defines no term "act". `[F]` `XLIV.1` and `CEP-006` P.2's
*"the single constitutional act"* are uniqueness-of-**kind** claims, disambiguated by `XLIV.5`'s
*"Each of those is a **distinct act**"*.

`[I]` **Therefore "how many acts?" is not an unanswered question — it is a question that does not
yet have truth conditions.** No quantity of further corpus analysis derives it. Deriving it
requires an amendment defining act atomicity — a `MAJOR` change under `XXIX.4`, requiring the full
`XLIV` ratification path, which requires the competent authority `CMG-OQ-01` seeks.

`[I]` **`CIRC-01` — the corpus cannot define act atomicity without ratification, and cannot
determine how many acts ratification takes without defining act atomicity.** `[I]` This circle is
**not** an instance of `ROOT-Ω`: it is breakable *in-corpus* the moment any competent owner defines
the term, and no external act is logically required to define a definition.

### 6. Can any remaining impossibility proof be strengthened? **NO. Two can be weakened, correctly.**

| Proof | Verdict |
|---|---|
| `ROOT-Ω` (a corpus cannot self-confer standing) | **`[I]` Cannot be strengthened.** Already minimal, already proved *"logically foreclosed"*, already bounded as *"a missing seed, not a contradiction"* |
| `{DEF-02, UCCEP-F-004}` irreducibility | **`[I]` Cannot be strengthened.** Proved irreducible by overdetermination (O5). Cannot be reduced to a singleton in either direction |
| *"No authority is competent to ratify"* | **`[F]` ALREADY WEAKENED, correctly.** `UCCEP-F-004` amended: this wording *"is contradicted by committed Repository Truth"* |
| *"Cardinality is 2"* (`CMG-000007` §5) | **`[F]` REFUTED** by executed simulation (`DIV-02`) |

---

## CLASSIFIED RESIDUE

### FACTS `[F]`
1. Validator at HEAD: **0 findings**, `READY-PROVISIONAL`, 44 artifacts, **1 vacancy**, 9 gaps, 7 open questions.
2. `VAC-01.located = false`; `T1` `VACANT`; **0 artifacts at `T0`, 0 at `T1`**.
3. `EC-1` **was performed** by `AUTH-13`; `URAT-REC-01` records it **PROVISIONAL**, *"constitutional finality **not claimed**"*.
4. `09-DR-RAT-11-ASSESSMENT` §5 ¶88: `CEP-006` finality is *"a **distinct track**"*; the reconciliation *"makes **no** claim"* about `FINALIZED`.
5. `UCAF-RC-01/02/03` are `RECONCILIATION-REQUIRED` and **undisposed**; 14 artifacts re-cite them as standing.
6. `AUTH-13 ≠ AUTH-14` (derivation); `E6 ≠ E7` (`CEP-006` XII.2 uses both with different consequents); T1 occupant is an **artifact**, `CMG-OQ-01`'s referent an **authority**.
7. Tier lattice: registry `subordinate_to` is an **exact transitive reduction** of XVI.3; `orthogonal_tier_pairs` matches XVI.4's three. **No XVI defect.**
8. `CMG-000001` XXV.3 maps `CMG-S-07 ↔ RATIFIED / FINALIZED`; **six** `CEP-006` VI.1 states unmapped, including `ACCEPTED`; XXV.3's own conflict rule mandates an amendment that **does not exist**.
9. `CMG-000001` contains **one** occurrence of `FINALIZED`, inside XXV.3 itself.
10. `cmg_validate.py` contains **no** content hashing; text binding is a `VERSION` string comparison.
11. **14 of 19** registry collections are unbound to constitutional text; 3 are governance-critical.
12. Editing **only** `CMG-REGISTRY.json` yields `READY` with 0 findings, constitutional text unchanged.
13. Closing `CMG-OQ-01` + `CMG-OQ-02` + `VAC-01` yields `READY-PROVISIONAL` — `CMG-000007` §5's *"exactly two acts"* is **false** against the validator.
14. `GD-21-C7` forbids bundling `CMG-OQ-01/03/05/07` with `DEF-02`; `GD-21` disclaims jurisdiction over the matter.
15. Act atomicity is **defined for six subjects and never for a constitutional act**; Article IV defines no term "act".
16. `UCCEP-F-004` was **amended**; its competence limb was withdrawn as *"contradicted by committed Repository Truth"*; its surviving ground is `CEP-006` I.4 alone.

### INFERENCES `[I]`
1. `E3` and `E5` are categorially distinct — **closing one cannot close the other**. (O1.B note 2)
2. `E8 ≟ E6` is undecidable at HEAD on **both** branches: proof needs an authority above `E6`; disproof needs `E6`'s capability set, which is never enumerated (`UNK-04`).
3. `D-14`'s subject matter is a **three-layer compound defect** rooted in XXV.3 drafting, not in Article XVI.
4. `CMG-L-08` compliance and text-binding are, as realized, mutually exclusive — the systemic root of `DIV-P-01…04`.
5. `DEF-02 ⟹ UCCEP-F-004` but not conversely; the basis is **overdetermined** and therefore irreducible.
6. `ROOT-Ω` yields **incompleteness, not inconsistency**; `EC-1` proves the resolving input class non-empty.
7. **Act cardinality and record cardinality are distinct quantities**; the corpus constrains only the second. This dissolves the Model A / Model B contradiction.
8. `CMG-OQ-03` is **downstream** of `CMG-OQ-01`/`02` in text, yet **blocking** in the validator — a machine-induced ordering inversion.
9. `GAP-O-03` survives because correcting it revokes certification (LXXX.6) across all 44 artifacts — recording is cheaper than fixing, and VIII.5 permits recording.
10. `CIRC-01` is breakable in-corpus; it is **not** an instance of `ROOT-Ω`.

### ASSUMPTIONS `[A]`
`[A-01]` The `git` working tree at `1e3e4ba9` plus the one untracked determination is the complete corpus. Not independently verifiable from within.
`[A-02]` `00-SOURCE/CONSTITUTIONS/*.docx` were **not** parsed — `GD-21-C3` forbids treating them as normative. `UNK-03` is therefore assessed on in-corpus records only.
`[A-03]` `cmg_validate.py`'s determinism claim (L.5) is taken as declared. Two consecutive runs at HEAD produced byte-identical output (`md5 f76df8a8c90b65a9c7f4efeac253b4ac`), but **within one environment only** — hermeticity across environments was not tested.
`[A-04]` No hidden gate outside `00-CMG/tools/cmg-gate.sh` enforces the meta layer. `LXVI.7` declares it *"the SINGLE gate the meta layer is permitted"*; not exhaustively verified against all 32 workflow files.

### GAPS `[GAP]`
| Id | Gap |
|---|---|
| `GAP-O-01` | `UCAF-RC-02` referred for disposal to `CMG-REGISTRY.json`, an `AUTHORITY = NONE` projection that by XII.6 can dispose nothing. **The referral cannot terminate.** |
| `GAP-O-02` | **Constitutional act atomicity is undefined.** The load-bearing gap of Phase O. |
| `GAP-O-03` | `CMG-000001` XXV.3's self-mandated amendment (*"SHALL be corrected by amendment"*) is outstanding. |
| `GAP-O-04` | `E6`'s capability set is never enumerated, while `E8`'s (`CAC-01…07`) is — the asymmetry that blocks disproof of `UNK-02`. |
| `GAP-O-05` | No content-hash binding between constitutional text and any projection (`DIV-01`). |
| `GAP-O-06` | `CMG-000001` has no `FINALIZED` state, though it recognizes `CEP-006`, whose terminal state is `FINALIZED`. |
| `GAP-O-07` | `DIV-07` — three "tier" vocabularies collide inside the ratification chain; *"Terminal T4"* is not XVI.2's `T4`, and nothing records the distinction. |

### UNKNOWNS `[UNKNOWN]`
`UNK-01` … `UNK-06`, as tabulated at O7.1.

---

## PHASE O TERMINAL VERDICT

> **DETERMINATION-COMPLETE · RESIDUAL UNCERTAINTY PARTIALLY ELIMINATED · CARDINALITY NOT CLOSED — AND PROVED NOT CLOSABLE AT HEAD**

**`[F]` Eliminated by derivation (7 pair classes + 2 hypotheses):**
all type-level identity questions in O1.B; `E6 ≠ E7`; `E8 ≠ E9`; `E8 ≠ E7`; `E5 ≠ E7`;
**Model 0** (that `EC-1` sufficed); and **the hypothesis that the Article XVI tier lattice is
defective** — machine-verified clean.

**`[F]` Newly located (9 divergences + 7 gaps):**
`DIV-01…09`, `GAP-O-01…07`. Four are CRITICAL: the version-string text binding (`DIV-01`); the
false two-act closure path (`DIV-02`); the outstanding XXV.3 self-mandated amendment (`DIV-03`);
and the projection-stored ceiling that is supposed to prevent projection drift (`DIV-04`).

**`[I]` Not eliminated, and proved not eliminable at HEAD (6 unknowns):**
`UNK-01…06`. Each is undecidable **relative to HEAD**, not absolutely. The corpus's own
characterization — *"a missing seed, not a contradiction"* — is adopted as the exact statement of
the residue.

**`[I]` The terminal result of Phase O — the single sentence the whole analysis reduces to:**

> **Cardinality cannot be conclusively derived, because "how many acts" has no truth conditions in
> this corpus: constitutional act atomicity is nowhere defined (`GAP-O-02`). The question is not
> unanswered — it is not yet well-formed. What *is* derivable is that at least one further
> external act is required (Model 0 eliminated), that no located clause bounds the number above,
> and that at least two separate in-corpus governed determinations must record whatever is done
> (`GD-21-C7`) — so that act-cardinality and record-cardinality are different quantities, and the
> corpus governs only the second.**

**`[I]` And the correction Phase O makes to its own predecessors:**

> The impossibility proofs in this corpus have been getting **weaker, and correctly so**. `EC-1`
> was performed. `UCCEP-F-004`'s competence limb was withdrawn as contradicted by committed
> Repository Truth. What survives is not *"nothing can be ratified"* but a **bounded, structured,
> externally-rooted residue with a known resolving input class that has been exercised once
> already**. Any Phase P that restates the residue as categorical impossibility would be
> **regressing against located evidence**, not deriving.

**This determination decides nothing.** It closes no vacancy, disposes no reconciliation,
nominates no T1 occupant, allocates no authority, and proposes no remediation. It records what the
corpus at `1e3e4ba9` entails, and where it stops entailing.

---

*PHASE O · AUTHORITY = NONE (DERIVED TRUTH) · Reports; determines nothing.*
*`CERTIFIED-PROVISIONAL`; Tier T1 VACANT; `CMG-L-12` applies to every statement herein.*
