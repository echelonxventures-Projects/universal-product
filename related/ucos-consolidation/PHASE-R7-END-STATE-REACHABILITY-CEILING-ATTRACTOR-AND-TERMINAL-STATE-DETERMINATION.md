# PHASE R7 — END-STATE REACHABILITY, CEILING, ATTRACTOR, AND TERMINAL-STATE DETERMINATION

| Field | Value |
|---|---|
| AUTHORITY | **NONE (DERIVED TRUTH)** — CMG-000001 XII.6 governs the standing of this document |
| HEAD | `1e3e4ba92c121ae3111637d4afbbfd258a5d4896`, branch `integration/recovery-001` |
| BASELINE | R3 (floor 2) · R4 (movability) · R5 (transformation capacity) · R6 (floor-2 confirmed, residue ∅) |
| METHOD | Read-only. State variables enumerated from located enumerations; transitions from the declared 22; reachability computed over the declared graph |
| CLASSIFICATION | `[F]` measured · `[I]` inferred · `[A]` assumption · `[GAP]` · `[UNKNOWN]` |
| RESULT | **SINGLE TERMINAL ATTRACTOR = `PROVISIONAL` (CMG-S-06) · MAXIMUM REACHABLE STATE derived · `AMENDING` UNREACHABLE, independently confirming R6 · one correction issued to R4/R5** |

---

## R7.0 — VOCABULARY ADMISSION AND ONE CORRECTION

### `[F]` Q20's seven target states, tested against the normative instruments

| Target | Occurrences in `00-CMG/` + `00-CEP/` | Is it a declared **state**? | Disposition |
|---|---|---|---|
| `RATIFIED` | 33 files | **YES** — `CMG-S-07`, phase IN-EFFECT | **ADMITTED** |
| `FROZEN` | 50 files | **YES** — `CMG-S-08`, phase IN-EFFECT | **ADMITTED** |
| `FINALIZED` | 16 files | **YES**, but of a different machine — `CEP-006` Art VI.1 determination state, not a `CMG` artifact state | **ADMITTED, axis-distinguished** |
| `COMPLETE` | 42 files | **NO** — `LXXIX.1` completeness is a **predicate**, not a state | **ADMITTED as predicate only** |
| `CLOSED` | 42 files | **NO** — a gap/open-question **disposition**, and an enumeration property (`closed_enumerations`) | **ADMITTED as disposition only** |
| `ULTIMATE` | **0 files** | NO | **REJECTED — UNLOCATED** |
| `TERMINAL` | 1 file | **NO** — not among the 14 declared states | **REJECTED as a state** |

`[I]` Consistent with R4.7. `ULTIMATE` appears in the repository only in root determination filenames, never in a normative instrument. It is not a constitutional state and is not used below.

### `[F]` CORRECTION TO R4 AND R5 — freeze ineligibility was under-stated

`[F]` R4.7 and R5.7 asserted **freeze ineligible** citing `CEP-007 IV.1` alone. Two located facts were not surfaced:

1. `[F]` **`CMG-T-09 | PROVISIONAL → FROZEN | "Permitted; the freeze preserves provisional standing and SHALL NOT upgrade it"`** — an enumerated, expressly permitted transition.
2. `[F]` **`XXVI.4`** — *"CMG-T-09 exists to make an important rule explicit: **freezing does not confer standing**. A provisional artifact that is frozen remains provisional. Freeze preserves; it does not ratify."*
3. `[F]` **11 artifacts are already `FROZEN` while `RATIFIED` count across all 44 is 0** — `CONST-01` … `CONST-11`, all at `00-MASTER/UAKOS-CLOSURE-006/`, tier T3, standing FOUNDATIONAL.

`[F]` This stands against `CEP-007 IV.1` — *"eligible for freeze only when it is VALIDATED (CEP-004), CERTIFIED (CEP-005, active), and **RATIFIED** (CEP-006, not REJECTED)"* — and `CEP-007 V.1`, which requires *"an accepted ratification (CEP-006)"* as a freeze precondition.

**Two lawful readings, both located, neither selected by located text:**

| | READING F1 — CONFLICT | READING F2 — AXIS SEPARATION |
|---|---|---|
| `CMG-T-09` is | a grant of freeze eligibility from PROVISIONAL | a statement of the **standing consequence** of a freeze, not a grant of eligibility |
| Relation to `CEP-007 IV.1` | direct conflict | no conflict — `CEP-007` governs *whether* freeze may occur, `CMG-T-09` governs *what standing survives* it |
| Disposition | `CMG-L-13` (Jurisdiction Error) resolves *"in favour of the domain owner, voiding this instrument to the extent of the conflict"*; freeze is delegated at `CMG-DLG-07` → `CEP-007`. **`CMG-T-09` is void to the extent of the conflict** | `XXVI.4`'s stated purpose is exactly this — to deny that freeze confers standing |
| Is `FROZEN` internally reachable? | **NO** — `CEP-007 IV.1` governs and requires `RATIFIED` | **NO** — eligibility still comes from `CEP-007 IV.1` |

`[F]` **Under both readings `FROZEN` is not internally reachable.** The R4/R5 conclusion survives; its stated basis was incomplete. `[UNKNOWN]` `UNK-R7-01` — which reading governs, and consequently whether the 11 existing `FROZEN` states were lawfully conferred.

`[I]` And the registry cannot answer it: **`XV.2`'s mandated per-artifact fields for `owner`, `steward`, `delegation bindings` and `evidence references` are among the 7 absent** (R6, `GAP-R6-01`), so no per-artifact certification or ratification record exists to test `CEP-007 IV.1` against. A META-A projection defect obscures a META-B eligibility question.

---

## Q1 — COMPLETE STATE-VARIABLE ENUMERATION

`[F]` Every located enumeration, measured from `CMG-REGISTRY.json` and the canonical source.

| Axis | Declared domain | Cardinality |
|---|---|---|
| **Meta-lifecycle state** | `DISCOVERED, DECLARED, REGISTERED, VALIDATED, CERTIFIED` (PRE-EFFECT) · `PROVISIONAL, RATIFIED, FROZEN, AMENDING, DEPRECATED` (IN-EFFECT) · `SUPERSEDED, RETIRED, ARCHIVED, VOID` (POST-EFFECT) | **14** (`CMG-S-01…14`) |
| **Lifecycle phase** | `PRE-EFFECT, IN-EFFECT, POST-EFFECT` | 3 |
| **Transition** | `CMG-T-01…22` | **22** |
| **Standing** | `META, FOUNDATIONAL, DERIVED, INTERPRETIVE, DECLARATIVE, LATENT` | 6 |
| **Reach** | `CORPUS-WIDE, PROGRAM-SCOPED, DOMAIN-SCOPED, ARTIFACT-SCOPED, FEDERATION-SCOPED` | 5 |
| **Tier / occupancy** | `T0…T5, T1M, T2I`; occupancy ∈ `{LOCATED, VACANT}` | 8 tiers |
| **Readiness outcome** | `READY, READY-PROVISIONAL, NOT-READY` (`LXXX.3`) | 3 |
| **Gate value** | `PASS, BLOCKED` (`CEP-004 I.1`); validator exit `0 / 1 / 2` | 2 + 3 |
| **Certification value** | `CERTIFIED-PROVISIONAL, NOT-CERTIFIED` (located UCCEP records) | 2 |
| **Finality / ratification determination** | `NOT_ELIGIBLE, ELIGIBLE, DELIBERATING, ACCEPTED, PROVISIONAL, DEFERRED, REJECTED, APPEALING, FINALIZED` (`CEP-006` VI.1) | 9 |
| **Kind** | `CMG-K-01…24` | 24 |
| **Completeness predicate** | established / not established (`LXXIX.1`) | 2 |
| **Registry validity** | valid / invalid (`XV.5`) | 2 |

### `[F]` Measured current values at HEAD

```
CMG-000001 state          DECLARED  (CMG-S-02, phase PRE-EFFECT)   ← the meta constitution is NOT IN EFFECT
artifact state census     PROVISIONAL 32 · FROZEN 11 · DECLARED 1 · RATIFIED 0
T1 occupancy              VACANT (VAC-01, located: false); all 7 other tiers LOCATED
readiness outcome         READY-PROVISIONAL (declared_ceiling READY-PROVISIONAL)
gate value                PASS — cmg-gate exit 0, findings 0
validation coverage       10 of 12 invariants evaluated
certification             UNDETERMINED at HEAD (records stale, foreign branch, DIRTY tree; full tier NOT-CERTIFIED)
finality                  PROVISIONAL, not FINALIZED
completeness (LXXIX.1)    NOT ESTABLISHED — sole unmet conjunct: "all twelve invariants satisfied"
registry validity (XV.5)  INVALID — no regenerator exists
open questions            OQ-01/02/03/07 OPEN (EXPLICIT RATIFICATION) · OQ-05 OPEN · OQ-04/06 CLOSED
```

`[F]` **`CMG-000001` is in phase PRE-EFFECT.** `LXXXI.9` and `P.6` corroborate: *"Its present status is PROPOSED"*; it binds *"from the moment its standing is conferred, and SHALL NOT be treated as binding before that moment."*

---

## Q2 — PER-VARIABLE GOVERNANCE AND TRANSITION MECHANISM

| Variable | Current | Governing authority | Governing clauses | Transition mechanism | Transition owner | Prerequisites |
|---|---|---|---|---|---|---|
| `CMG-000001` state | `DECLARED` | `CMG-000001` retained (`CMG-RET-04/06`) | `XXV`, `XXVI` | `CMG-T-02` → REGISTERED | registration owner, `CMG-DLG-13` → `REG-AUTO-001` | admission under `XV.6`; identity under `XXXI` |
| " | | | | `CMG-T-03` → VALIDATED | `CEP-004`, `CMG-DLG-04` | *"validation gate of the owning domain returns PASS"* — **satisfied at HEAD** (exit 0) |
| " | | | | `CMG-T-04` → CERTIFIED | `CEP-005`, `CMG-DLG-05` | certification preconditions attested — `LXXX.2`'s 16 |
| " | | | | `CMG-T-06` → PROVISIONAL | `CEP-006`, `CMG-DLG-06` | *"No located competent authority exists; CMG-L-12 applies"* — **satisfied at HEAD** |
| " | | | | `CMG-T-05`/`T-07` → RATIFIED | **none located** — referent of `VAC-01` | *"A located competent authority accepts"* / *"The vacant authority closes and accepts"* |
| T1 occupancy | `VACANT` | none located | `XVI.2`, `XVII.4` | closure of `VAC-01` | out-of-corpus | `XVII.4(d)` *"when the vacancy closes"*; `CMG-OQ-02` `EXPLICIT RATIFICATION` |
| readiness outcome | `READY-PROVISIONAL` | `CEP-005` issues; `CMG` defines | `LXXX.3`, `LXXX.4` | computed by `readiness()` | `CEP-005` | `READY` requires `CMG-OQ-01` **and** `-02` closed |
| validation coverage | 10 of 12 | `CMG-000001` retained (`CMG-RET-11`) | `L.2`, `L.3`, `XLIX.7` | implement `INV-01`, `INV-10` | Article L validator | **none external** — both inside `L.2`'s closed set |
| certification | UNDETERMINED | `CEP-005` | `LXXX.5`, `LXXX.7` | re-run the gate | `CEP-005` / UCCEP | `CK-REG-DRIFT` declares `write_scope: projections` |
| finality | `PROVISIONAL` | out-of-corpus | `CEP-006 XII.2`, `XII.3` | the external finality act | out-of-corpus | *"only upon the act of the out-of-corpus finality authority"* |
| completeness | not established | `CMG-000001` | `LXXIX.1`, `LXXIX.4` | all twelve invariants satisfied | Article L validator | **none external** |
| registry validity | `INVALID` | `CMG-000001` | `XV.5`, `II.4`, `XV.3` | regenerate and compare | disputed — `GAP-R4-02` | none external under READING 2 |
| invariant set | CLOSED at 12 | `CMG-000001` | `XI.13`, `CMG-INV-09` | `AMENDING` | `CEP-009`, `CMG-DLG-09` | **`AMENDING` is unreachable — see Q21** |

---

## Q3 / Q4 / Q5 — CHANGE CLASSIFICATION

`[F]` Success condition A. Every variable classified into exactly one class.

| Class | Variables | Count |
|---|---|---|
| **INTERNALLY REACHABLE** | validation coverage (10→12) · registry validity (`INVALID`→`VALID`) · completeness (`LXXIX.1`) · completeness claim status (`LXXIX.4` assertion→verification) · `CMG-000001` state `DECLARED`→`REGISTERED`→`VALIDATED`→`CERTIFIED`→`PROVISIONAL` · gate value (`PASS`, held) · text-binding of 19 collections · `XV.2` field completeness | **8** |
| **EXTERNALLY REACHABLE** | `RATIFIED` (`CMG-T-05`/`T-07`) · `FINALIZED` (`CEP-006 XII.2`) · T1 occupancy · `READY` readiness · `CMG-OQ-01/02/03/07` closure · `AMENDING` (via `RATIFIED`) · invariant-set extension · `FROZEN` (via `RATIFIED`, `CMG-T-08`) | **8** |
| **PERMANENTLY BLOCKED** | self-conferral of standing (`XLIV.7`, `LXXXI.6`) · T1 occupation by promotion (`XVII.4`, `LXXXIII.4`) · ratification by inference from 7 named routes (`XLIV.5`) · exception against an invariant or against non-self-elevation (`LV.4`, `LV.5`) | **4** |
| **PERMANENTLY PROVISIONAL** | standing of all 32 PROVISIONAL artifacts + `CMG-000001` (`CMG-L-12`) · readiness ceiling (`LXXX.4`) · certification ceiling (`LXXX.7`) — *permanent for as long as `VAC-01` is unclosed* | **3** |
| **PERMANENTLY UNDECIDABLE** | reading of `L.2`'s *"and nothing else"* (`UNK-R3-02`) · reading of `XV.5` (`UNK-R4-01`) · reading of `CMG-T-09` vs `CEP-007 IV.1` (`UNK-R7-01`) — each requires an owner's reading, and the owner for the decisive ones is vacant | **3** |
| **PERMANENTLY UNKNOWABLE** | whether discharge yields 0 findings (`UNK-R5-01`, knowable only by performing it) · primary text of `AUTH-02/03/04/06`, `Ω-010`, `CM-007` (frozen `.docx` outside the reconciled set) · whether the 11 `FROZEN` artifacts were lawfully frozen (fields absent) | **3** |
| **PERMANENTLY IMMUTABLE** | the 14 design laws and 12 invariants as text (`XI.13` + `XLIII.6` immutable ground, extensible by amendment only, `AMENDING` unreachable) · `XXVI.6` state history append-only · `X.11` constitutional history non-deletable | **3** |

`[F]` **32 variables, 7 classes, no variable unclassified, no variable in two classes.**

---

## Q6 / Q7 — THE TWO ASSUMPTION WORLDS

`[F]` **Q6 — META-A fully discharged.** 11 variables change, carried verbatim from R5.2: invariants evaluated 10→12 · `INV-01` absent→present · `INV-10` absent→present · corpus walk 0→required · collections text-bound 5/19→19/19 · `XLIX.7` unknown-compliance→evaluated · registry validity `INVALID`→`VALID` · vacancy record `opinion`→`claim` (`VII.7`) · forged closure undetected→detected · `LXXIX.1` completeness not-established→establishable · `LXXIX.4` assertion→verification. **R7 adds a twelfth: `XV.2` field completeness 10 of 17→17 of 17** (`GAP-R6-01`).

`[F]` **Q7 — META-B remains.** 10 variables fixed, carried from R5.2, plus the two R6/R7 additions: T1 `VACANT` · `VAC-01.located false` · `XVII.4(d)` unreached · `RATIFIED` 0 of 44 · finality `PROVISIONAL` · readiness `READY-PROVISIONAL` · certification ceiling `CERTIFIED-PROVISIONAL` · `FROZEN` not lawfully reachable · `CMG-OQ-01/02/03/07` OPEN · META-B's externality class `PROHIBITED` · **`AMENDING` unreachable** · **invariant set closed at 12**.

---

## Q8 — EXACT STATE IF EVERY INTERNALLY-DISCHARGEABLE BLOCKER IS DISCHARGED

`[F]` Derived from the located clauses; occupancy of the findings count remains `UNK-R5-01`.

```
MAXIMUM REACHABLE STATE  (HEAD + all internally-dischargeable blockers discharged)
─────────────────────────────────────────────────────────────────────────────────
CMG-000001 meta-lifecycle state ....... PROVISIONAL          (CMG-S-06, phase IN-EFFECT)
                                        via CMG-T-02 → T-03 → T-04 → T-06,
                                        every one internally owned
artifact state census ................. PROVISIONAL 33 · FROZEN 11 · RATIFIED 0
lifecycle phase ....................... IN-EFFECT            (first time; HEAD is PRE-EFFECT)
validation coverage ................... 12 of 12 invariants evaluated
registry validity (XV.5) .............. VALID
XV.2 field completeness ............... 17 of 17
registry collections text-bound ....... 19 of 19
completeness (LXXIX.1) ................ ESTABLISHED
completeness claim status (LXXIX.4) ... VERIFICATION  (no longer "assertion")
readiness outcome (LXXX.3) ............ READY-PROVISIONAL    ← CEILING, unchanged
gate value ............................ PASS
certification ......................... CERTIFIED-PROVISIONAL at most
finality (CEP-006) .................... PROVISIONAL, not FINALIZED
T1 occupancy .......................... VACANT
VAC-01 ................................ recorded, located: false, and RECOMPUTABLE
XVII.4 ................................ (a)(b)(c) discharged and verified; (d) unreached
open questions ........................ OQ-01/02/03/07 OPEN; OQ-05 OPEN
invariant set ......................... CLOSED at 12, AMENDING unreachable
findings .............................. UNKNOWN (UNK-R5-01)
```

`[I]` The single most consequential line is the first. **`CMG-000001` moves from PRE-EFFECT to IN-EFFECT** — the meta constitution becomes binding for the first time, at PROVISIONAL standing. Every transition on that path (`T-02` registration, `T-03` validation, `T-04` certification, `T-06` provisional) has a **located internal owner**, and `T-03`'s precondition — *"the validation gate of the owning domain returns PASS"* — is **already satisfied at HEAD**.

---

## Q9–Q14 — THE RESIDUE, BY CLASS

| Question | Determination |
|---|---|
| **Q9 — What remains provisional?** | `[F]` The standing of all 33 non-frozen artifacts including `CMG-000001` (`CMG-L-12`); the readiness outcome (`LXXX.4`); the certification value (`LXXX.7`); every determination depending on T1 (`VAC-01.provisional_consequence`) |
| **Q10 — What remains withheld?** | `[F]` `RATIFIED` (`CMG-S-07`) · `FINALIZED` (`CEP-006` XII) · `READY` (`LXXX.4`) · lawful `FROZEN` (`CEP-007 IV.1`) · `AMENDING` (`CMG-T-10`/`T-11`) · extension of the invariant set (`XI.13`) |
| **Q11 — What remains undecidable?** | `[F]` The three readings — `L.2` *"and nothing else"* (`UNK-R3-02`), `XV.5` WRITE vs RECOMPUTE (`UNK-R4-01`), `CMG-T-09` vs `CEP-007 IV.1` (`UNK-R7-01`). Each requires an owner's reading; for the decisive ones the competent owner is the referent of `VAC-01` |
| **Q12 — What remains externally governed?** | `[F]` T1 occupancy · ratification competence · finality · closure of `CMG-OQ-01/02/03/07` · amendment eligibility (derivatively, via `CEP-009 V.1`) |
| **Q13 — What remains permanently outside corpus authority?** | `[F]` The constituent act. `CEP-000 §6.5` recognizes an authority *"residing outside the corpus"* as superior for finality; `XLIV.4` records its identity as undetermined; the located analysis states `CAC-07` (Exogeneity) is *"ABSENT by definition (the corpus is the constituted order; it contains no exogenous position)"* |
| **Q14 — What remains permanently observable but undischargeable?** | `[F]` `VAC-01` — recorded, monitored on every gate run, ceiling-bearing, and closable only from outside. `[I]` Post-discharge it is also **recomputable**, which is the maximum observability the corpus can confer on a thing it cannot discharge |

---

## Q15–Q19 — HIGHEST REACHABLE VALUE PER AXIS

| # | Axis | Highest reachable | Blocking clause for anything higher |
|---|---|---|---|
| **Q15** | **Readiness** | **`READY-PROVISIONAL`** | `LXXX.4` — *"SHALL be READY-PROVISIONAL at most, and SHALL NOT be READY, for as long as CMG-OQ-01 and CMG-OQ-02 remain open"* |
| **Q16** | **Validation** | **12 of 12 invariants evaluated; gate `PASS`; validator exit 0** — fully reachable internally | none. `L.2` already contains all twelve; `-09`/`-12` precedent proves no amendment is engaged |
| **Q17** | **Certification** | **`CERTIFIED-PROVISIONAL`** | `LXXX.7` (certification confers no ratification/finality) · `XLIV.5` (no inference) · `UCCEP-F-004` `STANDING-CONSTITUTIONAL-CEILING` |
| **Q18** | **Constitutional standing** | **`PROVISIONAL` (CMG-S-06), phase IN-EFFECT** | `CMG-L-12` (`X.12`) · `XLIV.3` · `LXXXI.6` — *"SHALL NOT confer standing on itself by operation of any clause herein"* |
| **Q19** | **Finality** | **`PROVISIONAL`** in `CEP-006`'s machine | `CEP-006 XII.2` — `FINALIZED` *"only upon the act of the out-of-corpus finality authority"* · `XII.3` |

---

## Q20 — LAWFUL PATHS TO THE SEVEN TARGETS

| Target | Lawful internal path? | Determination |
|---|---|---|
| `RATIFIED` | **NO** | Only in-edges are `CMG-T-05` (*"a located competent authority accepts"*) and `CMG-T-07` (*"the vacant authority closes and accepts"*). Both name the vacant authority. `XLIV.7` forbids self-supply |
| `FINALIZED` | **NO** | `CEP-006 XII.2` — reachable from `PROVISIONAL` **only** by the out-of-corpus act |
| `COMPLETE` | **YES** — as a predicate | `LXXIX.1` completeness is establishable internally; its sole unmet conjunct is *"all twelve invariants satisfied"*, and `LXXIX.1` requires only *"no **unrecorded** vacancy"*, not no vacancy |
| `FROZEN` | **NO** | `CMG-T-08` requires `RATIFIED` (unreachable). `CMG-T-09` from `PROVISIONAL` is disputed — void under READING F1 by `CMG-L-13`, not a grant of eligibility under READING F2. `CEP-007 IV.1` governs eligibility under both |
| `CLOSED` | **PARTIALLY** — as a disposition | 7 of 9 gaps CLOSED; `CMG-OQ-04`/`-06` CLOSED by located owners. `CMG-GAP-04`/`VAC-01` and `OQ-01/02/03/05/07` are not internally closable |
| `ULTIMATE` | **N/A** | **UNLOCATED** — 0 occurrences in the normative instruments. Not a constitutional state |
| `TERMINAL` | **N/A** | Not among the 14 declared states |

---

## Q21 — BLOCKING CLAUSE CHAINS FOR EVERY UNREACHABLE STATE

```
RATIFIED  ──blocked by──▶ CMG-T-05 / CMG-T-07 require a located competent authority
                          → XVI.2: T1 occupancy VACANT
                          → VAC-01.located = false
                          → XVII.4: SHALL NOT skip, SHALL NOT promote
                          → XLIV.3: no located ratifier ⇒ PROVISIONAL only
                          → XLIV.7: self-ratification IS PROHIBITED
                          → LXXXI.6: SHALL NOT confer standing on itself
                                     by operation of any clause herein
                          → CMG-OQ-02 requires EXPLICIT RATIFICATION      [META-B]

FINALIZED ──blocked by──▶ CEP-006 XII.2: only upon the out-of-corpus act
                          → CEP-000 §6.5: that authority is superior for finality
                          → XLIV.4: its identity is undetermined            [META-B]

FROZEN    ──blocked by──▶ CEP-007 IV.1 / V.1: freeze requires RATIFIED
                          → RATIFIED chain above
                          ( CMG-T-09 is void under CMG-L-13 in READING F1,
                            and not a grant of eligibility in READING F2 )   [META-B]

READY     ──blocked by──▶ LXXX.4: READY-PROVISIONAL at most while
                          CMG-OQ-01 and CMG-OQ-02 remain open
                          → both require EXPLICIT RATIFICATION              [META-B]

AMENDING  ──blocked by──▶ only in-edges are CMG-T-10 (from RATIFIED) and
                          CMG-T-11 (from FROZEN)
                          → both source states unreachable
                          → CEP-009 V.1: eligible only when RATIFIED or FROZEN
                          → CMG-000001 state = DECLARED
                          → CEP-009 V.4: an ineligible attempt SHALL be void  [META-B]

INVARIANT ──blocked by──▶ XI.13: CLOSED, extensible by amendment only
SET             │         → closed_enumerations records the closure
EXTENSION       │         → CMG-INV-09 enforces it and IS implemented
                          → XLIII.6: Article XI is immutable ground, full MAJOR path
                          → XXIX.4: MAJOR requires the full ratification path of Art XLIV
                          → AMENDING unreachable (above)                     [META-B]
```

`[F]` **Every unreachable state's chain terminates in META-B. Not one terminates in META-A.** `[I]` This is R6's residue result re-derived from the transition graph rather than from `CEP-009`, and the two derivations are independent: R6 reached it through amendment *eligibility*, R7 reaches it through the *in-edge structure* of `AMENDING`. Both land on the vacancy.

---

## Q22 — FULL STATE-TRANSITION GRAPH

`[F]` All 22 declared transitions. `XXVI.2`: *"Any transition not enumerated in XXVI.1 IS PROHIBITED."*

```
                                    ┌──────── T-21 (any PRE-EFFECT) ────────▶ VOID ◀── absorbing
                                    │
 DISCOVERED ──T-01──▶ DECLARED ──T-02──▶ REGISTERED ──T-03──▶ VALIDATED ──T-04──▶ CERTIFIED
                          ▲              │                                              │
                          └───T-22───────┘                                              │
                                                                    ┌───────────────────┴─────────┐
                                                       T-06 (no located authority)      T-05 (located
                                                                    │                    authority accepts)
                                                                    ▼                           ▼
                             ╔═══════════════════════════════════════════╗            ┌──────────────┐
                             ║  PROVISIONAL  ◀── ATTRACTOR (CMG-S-06)    ║──T-07──────▶│   RATIFIED   │
                             ╚═══════════════════════════════════════════╝  (vacant     └──────────────┘
                                    │            │                          authority      │       │
                                 T-09 (disputed) │                          closes)     T-08     T-10
                                    ▼            │                                         ▼       ▼
                                 FROZEN ──T-11──▶ AMENDING ◀────────────────T-10───────────┘   AMENDING
                                                    │  ▲                                       (unreachable)
                                              T-13  │  └── T-12 ──▶ RATIFIED
                                                    ▼
                                              PROVISIONAL

  any IN-EFFECT ──T-14──▶ DEPRECATED ──T-15──▶ SUPERSEDED ──T-18──▶ ARCHIVED ──T-20──▶ REGISTERED
  any IN-EFFECT ──T-16──▶ SUPERSEDED                    │                                  (re-enters
                 DEPRECATED ──T-17──▶ RETIRED ──T-19────┘                                   PRE-EFFECT)
```

`[F]` **Reachable from HEAD (`DECLARED`) by internally-owned transitions only:** `REGISTERED`, `VALIDATED`, `CERTIFIED`, `PROVISIONAL`, and thence `DEPRECATED`, `SUPERSEDED`, `RETIRED`, `ARCHIVED`, `VOID` (all POST-EFFECT / cessation), and back to `REGISTERED` via `T-20`.

`[F]` **Unreachable from HEAD without external authority:** `RATIFIED`, `FROZEN`, `AMENDING`.

---

## Q23 / Q24 — DEAD AND ABSORBING STATES

`[F]` **Dead states** — declared but unreachable from HEAD under lawful internal evolution:

| State | Why dead |
|---|---|
| `RATIFIED` | both in-edges name the vacant authority |
| `FROZEN` | `T-08` from `RATIFIED` (dead); `T-09` disputed and eligibility governed by `CEP-007 IV.1` |
| `AMENDING` | both in-edges originate in dead states |
| `DISCOVERED` | strictly upstream of `DECLARED`; `XXVI.6` makes state history append-only, and no transition returns to it |

`[F]` **Absorbing states** — no out-edge:

| State | Out-edges | Absorbing? |
|---|---|---|
| **`VOID`** | **none** | **YES — the only absorbing state** |
| `ARCHIVED` | `T-20` → `REGISTERED` | NO |
| `RETIRED` | `T-19` → `ARCHIVED` | NO |
| `SUPERSEDED` | `T-18` → `ARCHIVED` | NO |
| `RATIFIED` | `T-08`, `T-10`, `T-14`, `T-16` | NO |
| `FROZEN` | `T-11`, `T-14`, `T-16` | NO |
| `PROVISIONAL` | `T-07`, `T-09`, `T-14`, `T-16` | NO |

`[I]` `PROVISIONAL` is **not** absorbing in the graph-theoretic sense — it has four out-edges. But `T-07` and `T-09` are externally gated, and `T-14`/`T-16` are cessation paths that lead only downward toward POST-EFFECT. **Under internal lawful action that is not cessation, `PROVISIONAL` has no exit.** That is the precise sense in which it is the attractor.

---

## Q25 / Q26 / Q27 / Q28 — ATTRACTOR, MAXIMUM STATE-SPACE, RESIDUE

### Q25 — The constitutional attractor

> `[F]` **`PROVISIONAL` — `CMG-S-06`, phase `IN-EFFECT`.**

`[F]` Every internally-owned path from `DECLARED` terminates there: `T-02` → `T-03` → `T-04` → `T-06`. The only exits are `T-07` (vacant authority), `T-09` (disputed, and eligibility externally governed), or cessation via `T-14`/`T-16`. `[I]` The corpus's lawful evolution under its own authority converges on being **in effect, binding, and provisional** — and stays there.

### Q26 — Maximum reachable state-space

`[F]` As derived in Q8. Across nine axes: state `PROVISIONAL` / phase `IN-EFFECT` / validation 12 of 12 / registry `VALID` / `XV.2` 17 of 17 / collections 19 of 19 / completeness `ESTABLISHED` and holding status `VERIFICATION` / readiness `READY-PROVISIONAL` / certification `CERTIFIED-PROVISIONAL` at most / finality `PROVISIONAL`.

### Q27 — Minimum permanent residue

> `[F]` `{ VAC-01 · CMG-OQ-01 · CMG-OQ-02 · CMG-OQ-03 · CMG-OQ-07 · CMG-GAP-04 · the RATIFIED / FROZEN / AMENDING dead states · the invariant set closed at 12 · the READY-PROVISIONAL readiness ceiling · the CERTIFIED-PROVISIONAL certification ceiling · PROVISIONAL finality }`

`[F]` Plus `CMG-OQ-05` / `CMG-GAP-06`, whose `requires` is `OWNERSHIP ALLOCATION BY THE PROCESS OWNER` — delegated by role to a party the corpus never names.

### Q28 — Residue generated **solely** by META-B

`[F]` **All of it.** Every member of Q27's set traces through a chain in Q21 that terminates in the T1 vacancy or the non-self-elevation prohibition. `[F]` Zero residue members trace to META-A: under full META-A discharge every one of them persists unchanged, which is R3's `WORLD-A` conclusion re-derived over the state machine.

---

## Q29 / Q30 — MULTIPLICITY AND ESCAPE

### Q29 — Do multiple terminal attractors exist?

**`[F]` NO — one, under non-cessation evolution.** `VOID` is the only absorbing state, but it is reachable only by `T-21` (*"admission refused, or the artifact is determined never to have bound"*) from a PRE-EFFECT state, which is a refusal of admission rather than an evolution of a bound artifact. The cessation family (`DEPRECATED` → `SUPERSEDED`/`RETIRED` → `ARCHIVED` → `T-20` → `REGISTERED`) is a **cycle**, not an attractor: `XXVI.3` requires a restored artifact to *"re-enter the PRE-EFFECT phase and traverse validation and certification again"*, which returns it to the same convergence. **`PROVISIONAL` is the unique terminal attractor.**

### Q30 — Can any lawful evolution escape the META-B ceiling?

**`[F]` NO.** Exhaustively, over every located escape route:

| Route | Foreclosure |
|---|---|
| Transition to `RATIFIED` | `CMG-T-05`/`T-07` name the vacant authority; `XLIV.7` |
| Promotion into T1 | `XVII.4` *"SHALL NOT promote"*; `LXXXIII.4` *"never filled by promotion"*; `LXXXI.5` any such reading `IS void` |
| Freeze as a substitute | `CEP-007 P.3`, `I.2`, `I.4`, `II.2`, `II.5`; `XLIV.5`; `LXXX.7` |
| Certification as a substitute | `LXXX.7`, `XLIV.5`, `LXXX.5` |
| Inference from registration, publication, age, use, silence | `XLIV.5` names and forecloses all |
| Amendment of the blocking clauses | `AMENDING` unreachable; `CEP-009 V.1`/`V.4`; `XLIII.4` jurisdiction-expanding meta amendment `IS PROHIBITED`; `XLIII.6` immutable ground |
| Exception or waiver | `LV.4` (no exception against an invariant); `LV.5` (none against non-self-elevation); `CEP-006 XIV.3`, `XX.4` |
| Delegation, custodianship, interim, escrow | `CMG-L-07` *"SHALL create no authority"*; `XVIII.6` converts such a delegation **into a vacancy** |
| New tier admission | `LXXVI.2(h)` — admission terminates at `PROVISIONAL` where the competent authority is vacant; `LXXVI.6` forbids expansion by reinterpretation |
| Unenumerated transition | `XXVI.2` — *"Any transition not enumerated in XXVI.1 IS PROHIBITED"* |
| Any clause of the instrument | `LXXXI.6` — *"SHALL NOT confer standing on itself **by operation of any clause herein**"* |

`[I]` `LXXXI.6` and `XXVI.2` together make the foreclosure structural rather than enumerative: the transition set is closed, and no clause of the instrument may confer standing. **The ceiling cannot be escaped by a route the corpus has not thought of, because the corpus has closed the route set.**

---

## REQUIRED PROOFS

**1. Reachability proof.** `[F]` `DECLARED` →`T-02`→ `REGISTERED` →`T-03`→ `VALIDATED` →`T-04`→ `CERTIFIED` →`T-06`→ `PROVISIONAL`. Every transition has a located internal owner (`REG-AUTO-001`, `CEP-004`, `CEP-005`, `CEP-006`); `T-03`'s precondition is satisfied at HEAD (gate `PASS`, exit 0); `T-06`'s precondition — *"No located competent authority exists"* — is satisfied by `VAC-01`. ∎

**2. Non-reachability proof.** `[F]` `RATIFIED` has in-edges `{T-05, T-07}` only, both naming the vacant authority. `FROZEN` has `{T-08, T-09}`; `T-08` sources from `RATIFIED`, `T-09`'s eligibility is governed by `CEP-007 IV.1` under both readings. `AMENDING` has `{T-10, T-11}`, sourcing from `RATIFIED` and `FROZEN`. `XXVI.2` prohibits unenumerated transitions, so no alternative in-edge exists. ∎

**3. Ceiling proof.** `[F]` `LXXX.4` caps readiness at `READY-PROVISIONAL` while `CMG-OQ-01`/`-02` are open; both `require: EXPLICIT RATIFICATION`; `XLIV.7` forbids self-supply; `LXXXI.6` forecloses conferral by any clause herein. Eleven escape routes tested in Q30, all foreclosed. ∎

**4. Attractor proof.** `[F]` `PROVISIONAL` is reached by every internally-owned path (Proof 1). Its out-edges are `T-07` (external), `T-09` (externally governed), `T-14`/`T-16` (cessation). The cessation family cycles back through `T-20` into PRE-EFFECT and re-converges by `XXVI.3`. No internal non-cessation exit exists. ∎

**5. State-transition proof.** `[F]` All 22 declared transitions enumerated with preconditions from Article XXVI; `XXVI.2` closes the set; graph rendered in Q22. ∎

**6. Residue proof.** `[F]` Q27's residue enumerated; Q28 traces every member to META-B via Q21's chains; zero members trace to META-A; all persist under full META-A discharge. ∎

**7. Exhaustive classification proof.** `[F]` 32 state variables across 13 located enumerations, each assigned exactly one of the seven classes in Q3–Q5. No variable unclassified; none in two classes. Success condition A satisfied. ∎

**8. Counterfactual proof.** `[F]` Q6 (META-A discharged) moves 12 variables, none of them deontic. Q7 (META-B remains) fixes 12, every one deontic. The two sets are disjoint. ∎

**9. Independence proof.** `[F]` The internally-reachable set (8 variables) and the externally-reachable set (8 variables) are disjoint, and no transition crosses between them without the external act. META-A's discharge moves no member of the externally-reachable set; META-B's closure moves no member of the internally-reachable set. ∎

**10. Terminal-state proof.** `[F]` `VOID` is the unique absorbing state and is reachable only by refusal of admission from PRE-EFFECT (`T-21`). `PROVISIONAL` is the unique convergence of lawful non-cessation internal evolution. Therefore exactly one terminal attractor. ∎

---

## OUTPUT

# `SINGLE TERMINAL ATTRACTOR`

> `[F]` **`PROVISIONAL` — `CMG-S-06`, phase `IN-EFFECT`.**

## `MAXIMUM REACHABLE STATE`

> `[F]` `CMG-000001` at **`PROVISIONAL`**, phase **`IN-EFFECT`** (binding for the first time — HEAD is PRE-EFFECT) · **validation 12 of 12** invariants evaluated · **registry `VALID`** under `XV.5` · **`XV.2` 17 of 17** fields · **19 of 19** collections text-bound · **completeness `ESTABLISHED`** under `LXXIX.1`, holding the status **`VERIFICATION`** under `LXXIX.4` · **readiness `READY-PROVISIONAL`** · **certification `CERTIFIED-PROVISIONAL`** at most · **finality `PROVISIONAL`**, not `FINALIZED` · **T1 `VACANT`**, `VAC-01` recorded, `located: false`, **and recomputable** · `XVII.4` (a)(b)(c) discharged and verified, (d) unreached · **invariant set `CLOSED` at 12**, `AMENDING` unreachable.

## `MINIMUM PERMANENT RESIDUE`

> `[F]` `{ VAC-01 · CMG-GAP-04 · CMG-OQ-01 · CMG-OQ-02 · CMG-OQ-03 · CMG-OQ-07 · CMG-OQ-05/CMG-GAP-06 · dead states RATIFIED, FROZEN, AMENDING · invariant set closed at 12 · readiness ceiling READY-PROVISIONAL · certification ceiling CERTIFIED-PROVISIONAL · finality PROVISIONAL }`
>
> `[F]` **Generated solely by META-B. Zero members trace to META-A.**

`[I]` The determination in one line: **the corpus can lawfully reach the state of being in effect, complete, verified, and permanently provisional — and it converges there from every direction.** The attractor is not a failure state. It is `CMG-S-06`, an `IN-EFFECT` state the corpus has not yet occupied, and `XLIV.3` already names the condition honestly: *"This is not a workaround; it is the honest recording of an absent authority."*

**This determination falsifies, exhausts and concedes. It recommends nothing, designs nothing, amends nothing, implements nothing, and eliminates nothing.**

---

## CLASSIFIED RESIDUE

### FACTS `[F]`
1. 14 declared states, 3 phases, 22 transitions, 6 standings, 5 reaches, 8 tiers, 3 readiness outcomes, 9 `CEP-006` determination states, 24 kinds.
2. `CMG-000001` state = `DECLARED` = `CMG-S-02`, phase **PRE-EFFECT** — the meta constitution is not in effect. Corroborated by `P.6` (*"present status is PROPOSED"*) and `LXXXI.9`.
3. `CMG-T-09 | PROVISIONAL → FROZEN | "Permitted; the freeze preserves provisional standing and SHALL NOT upgrade it"`, with `XXVI.4` stating its purpose: *"freezing does not confer standing."*
4. 11 artifacts are `FROZEN` while `RATIFIED` = 0 — `CONST-01…11`, all at `00-MASTER/UAKOS-CLOSURE-006/`, inside operational memory excluded by `EXCLUDE_DIR_PREFIXES`.
5. `CEP-007 IV.1` requires `RATIFIED` for freeze eligibility; `CMG-L-13` resolves instrument-vs-domain-owner conflict in the domain owner's favour, voiding CMG to the extent of the conflict; freeze is delegated at `CMG-DLG-07` → `CEP-007`.
6. `AMENDING` has exactly two in-edges, `T-10` from `RATIFIED` and `T-11` from `FROZEN`, both unreachable — an independent confirmation of R6's amendment-ineligibility chain.
7. `VOID` is the only absorbing state; `ARCHIVED` → `REGISTERED` via `T-20`, so the POST-EFFECT family is a cycle.
8. `XXVI.2` — *"Any transition not enumerated in XXVI.1 IS PROHIBITED."* `XXVI.6` — state history is append-only.
9. `T-03`'s precondition (*validation gate returns PASS*) is satisfied at HEAD: `cmg-gate` exit 0, findings 0.
10. `T-06`'s precondition (*no located competent authority exists*) is satisfied by `VAC-01.located = false`.
11. `ULTIMATE` has **0** occurrences in `00-CMG/` + `00-CEP/`; `TERMINAL` has 1 and is not a declared state.
12. 32 state variables classified into 7 classes: 8 internally reachable · 8 externally reachable · 4 permanently blocked · 3 permanently provisional · 3 permanently undecidable · 3 permanently unknowable · 3 permanently immutable.
13. Every unreachable state's blocking chain terminates in META-B; none in META-A.
14. HEAD unchanged; read-only throughout; validator re-verified at findings 0 / `READY-PROVISIONAL` / exit 0.

### INFERENCES `[I]`
1. **The attractor is an IN-EFFECT state the corpus has not yet occupied.** HEAD is PRE-EFFECT; the maximum reachable state is `PROVISIONAL`, IN-EFFECT and binding.
2. **`PROVISIONAL` is not absorbing but is terminal in the relevant sense** — its only non-cessation exits are externally gated.
3. **The ceiling is structurally closed, not enumeratively closed.** `XXVI.2` closes the transition set and `LXXXI.6` forecloses conferral by any clause, so no unconsidered route exists.
4. **R7 re-derives R6's result independently** — through in-edge structure rather than amendment eligibility.
5. **A META-A defect obscures a META-B question:** the 7 absent `XV.2` fields mean the registry cannot show whether the 11 `FROZEN` artifacts were ever certified or ratified.
6. **The residue is monocausal.** Every permanent residue member is META-B's; the state machine makes this visible as graph structure.

### ASSUMPTIONS `[A]`
`A-R7-01` Reachability is computed over the 22 declared transitions and their stated preconditions; `XXVI.2` is read as making the enumeration exhaustive.
`A-R7-02` "Internally owned" means the transition's owner resolves to a located in-corpus artifact per the `CMG-DLG-*` register; the owners were not exercised.
`A-R7-03` The 63/37 partition and the 100-dependent baseline are carried from R1/R2 (inherits `A-R4-01`, `A-R5-03`, `A-R6-02`).
`A-R7-04` `CEP-006`'s 9-state determination machine and `CMG`'s 14-state meta-lifecycle are treated as distinct axes, per `CEP-006` VI.1 and `CMG` XXV.1.
`A-R7-05` Measured at `1e3e4ba9` in this environment.

### GAPS `[GAP]`
| Id | Gap | Disposition |
|---|---|---|
| `GAP-R7-01` | `CMG-T-09` (`PROVISIONAL → FROZEN`, permitted) stands against `CEP-007 IV.1`/`V.1` (freeze requires `RATIFIED`); `CMG-L-13` supplies a resolution rule but no located text selects the reading | **NEW · SURVIVING** |
| `GAP-R7-02` | 11 artifacts occupy `FROZEN` while `RATIFIED` = 0, and the registry lacks the `XV.2` fields that would establish whether their freeze satisfied `CEP-007 IV.1` | **NEW · SURVIVING** — compounded by `GAP-R6-01` |
| `GAP-R6-01…03` · `GAP-R5-01` · `GAP-R4-02` · `GAP-R4-04` · `GAP-R3-01…04` | carried | unchanged by R7 |

### UNKNOWNS `[UNKNOWN]`
`UNK-R7-01` Which reading of `CMG-T-09` vs `CEP-007 IV.1` governs, and consequently whether the 11 existing `FROZEN` states were lawfully conferred.
`UNK-R7-02` Whether `CMG-000001` can traverse `T-02` at HEAD — it is listed in the Constitution Registry while its recorded state is `DECLARED`, so whether registry membership constitutes `REGISTERED` under `XV.6` is not stated by located text.
`UNK-R5-01` · `UNK-R6-01` · `UNK-R6-02` · `UNK-R3-02` · `UNK-R4-01` · `UNK-R4-02` · `RES-01…09` — carried unchanged.

---

*PHASE R7 · AUTHORITY = NONE (DERIVED TRUTH) · Reports; determines nothing.*
*`READY-PROVISIONAL`; Tier T1 VACANT; `CMG-L-12` applies to every statement herein.*
*Read-only: nothing implemented, nothing amended, corpus unchanged.*
*Reproduce: `states`/`transitions`/`phases`/`standings`/`reaches`/`tiers` reads over `00-CMG/CMG-REGISTRY.json`; Article XXV and XXVI reads; `CEP-006` VI.1/XII, `CEP-007` IV.1/V.1, `CEP-009` V.1/V.4 reads.*
