# PHASE R6 — FLOOR-2 FALSIFICATION-RISK EXHAUSTION AND THIRD-META-CAUSE DETERMINATION

| Field | Value |
|---|---|
| AUTHORITY | **NONE (DERIVED TRUTH)** — CMG-000001 XII.6 governs the standing of this document |
| HEAD | `1e3e4ba92c121ae3111637d4afbbfd258a5d4896`, branch `integration/recovery-001` |
| BASELINE | R3 (floor 2) · R4 (META-A movable, META-B immovable) · R5 (`UNK-R3-05` deferred as the sole live falsification risk) |
| COMMISSION | Resolve `UNK-R3-05`: does a third independent meta-cause hide behind the unrealized design laws? |
| METHOD | Read-only. Substantive coverage measured, not identifier occurrence. Every law tested in three worlds |
| CLASSIFICATION | `[F]` measured · `[I]` inferred · `[A]` assumption · `[GAP]` · `[UNKNOWN]` |
| RESULT | **FLOOR-2 CONFIRMED · ZERO RESIDUE · META-C REJECTED · the residue collapses into META-B through a located amendment-ineligibility chain no prior phase had assembled** |

---

## R6.0 — METHOD: WHY R3's CENSUS WAS THE WRONG INSTRUMENT

`[F]` R3 measured design-law realization by **identifier occurrence** in the Article L validator and found 11 of 14 at zero. R6 reproduces that census exactly:

```
CMG-L-01 : 0   CMG-L-02 : 0   CMG-L-03 : 0   CMG-L-04 : 0
CMG-L-05 : 0   CMG-L-06 : 1   CMG-L-07 : 4   CMG-L-08 : 1
CMG-L-09 : 0   CMG-L-10 : 0   CMG-L-11 : 0   CMG-L-12 : 0
CMG-L-13 : 0   CMG-L-14 : 0
```

`[F]` And the invariant census, which R3 did not pair with it:

```
CMG-INV-01 : 0   CMG-INV-02 : 3   CMG-INV-03 : 5   CMG-INV-04 : 2
CMG-INV-05 : 3   CMG-INV-06 : 3   CMG-INV-07 : 3   CMG-INV-08 : 3
CMG-INV-09 : 5   CMG-INV-10 : 0   CMG-INV-11 : 2   CMG-INV-12 : 2
```

`[I]` **Identifier absence is not non-realization.** `CMG-L-02` (Single Authority) appears zero times, yet `CMG-INV-02` — whose verification is *"the concern-to-owner mapping is injective on concerns"*, which is `CMG-L-02` stated as a predicate — appears three times and is implemented in `check_concerns`. The law is enforced; its name is not cited. R6 therefore measures **substantive coverage**: for each design law, whether some implemented check asserts its predicate.

`[A]` `A-R6-01` — the law→invariant correspondence below is **derived from the clause texts, not located.** No instrument declares which invariant verifies which design law. `GAP-R3-02` is exactly this absence, and `GAP-R3-01` (no obligation taxonomy) compounds it. The mapping is defensible from the texts and it is not a reading.

---

## Q1 — EVERY STILL-UNREALIZED DESIGN LAW

`[F]` Substantive classification of all 14, superseding the identifier census.

| Class | Laws | Count |
|---|---|---|
| **A — REALIZED, identifier cited** | `CMG-L-06` (Acyclicity), `CMG-L-07` (Delegation Fidelity), `CMG-L-08` (Configuration-Driven Binding) | 3 |
| **B — REALIZED IN SUBSTANCE, identifier absent** | `CMG-L-02` (via `CMG-INV-02`), `CMG-L-11` (via `CMG-INV-11`), `CMG-L-13` (via `CMG-INV-12`) | 3 |
| **C — PARTIALLY COVERED** | `CMG-L-05` (Downward Precedence) — acyclicity and rank determinacy covered by `INV-05`/`INV-06`; the directional conjunct *"a superior SHALL NOT derive standing from a subordinate"* covered by nothing | 1 |
| **D — CRITERION EXISTS, UNIMPLEMENTED** | `CMG-L-01` (via `CMG-INV-01`, 0 occurrences), `CMG-L-10` (via `CMG-INV-10`, 0 occurrences) | 2 |
| **E — NO CRITERION EXISTS** | `CMG-L-03` (Bounded Scope), `CMG-L-09` (Neutrality), `CMG-L-14` (No Parallel Machinery) | 3 |
| **F — META-B's OWN LAWS** | `CMG-L-04` (Non-Self-Elevation), `CMG-L-12` (Provisional Standing) | 2 |

`[F]` **Genuinely unrealized after R5: classes C (residual conjunct), D, E, F — 8 laws, of which 6 are wholly unrealized and 2 partially.** `[F]` R3's figure of 11 over-counted by conflating identifier absence with non-enforcement in classes B and C.

---

## Q2 — PER-LAW ANALYSIS

| Law | Governing clauses | Owning authority | Validator coverage | Dependency chain | **Root dependency** |
|---|---|---|---|---|---|
| **`CMG-L-01`** Recognition | `X.1`, `XI.1` (`INV-01`), `XV.3`, `L.2` | `CMG-000001` retained, `CMG-RET-11` | **NONE.** `INV-01` absent; verification requires *"artifacts cited as constitutional authority **anywhere in the corpus**"* — the validator performs no corpus walk (`os.walk\|rglob\|glob(` = 0) | criterion exists inside `L.2`'s closed set → implementable without amendment (`-09`/`-12` precedent) | **META-A** |
| **`CMG-L-10`** Evidence Binding | `X.10`, `XI.10` (`INV-10`), `LIII.3`, `LXXXIII.9`, `VII.7` | `CMG-000001` retained; evidence delegated `CMG-DLG-08` → `CEP-008` | **NONE.** `INV-10` absent. `XI.10`'s predicate — *"validator exit status zero with zero findings"* — is satisfied at HEAD by a run that never evaluates it | as above | **META-A** |
| **`CMG-L-03`** Bounded Scope | `X.3`, **`XV.2`**, `XIX.1`, `XIX.2`, `XLII.7` | `CMG-000001` retained | **NONE, and the data is absent.** `XV.2` mandates the Registry record *"declared positive scope, declared negative scope"* per artifact; **neither field exists on any of 44 entries** | (i) projection incomplete vs `XV.2` → `XV.3` *"the input governs"*, undetected · (ii) even with data, no invariant covers scope → new criterion required | **META-A** primary (projection), **META-B** secondary (criterion) |
| **`CMG-L-09`** Neutrality | `X.9` | `CMG-000001` retained | **NONE.** No invariant addresses technology naming; no registry field carries it. Verification is a textual predicate over constitutional artifacts | no criterion exists → requires a new invariant → `XI.13` amendment-only → **ineligibility chain** | **META-B** |
| **`CMG-L-14`** No Parallel Machinery | `X.14`, `LXXXIII.8`, `L.1`, `LXVI.7` | `CMG-000001` retained | **NONE.** `INV-02` is adjacent (concern-owner injectivity) but addresses *authority*, not *machinery* | as above | **META-B** |
| **`CMG-L-05`** residual conjunct | `X.5`, `IX.7`, `XI.5`, `XI.6` | `CMG-000001` retained | **PARTIAL.** `check_acyclicity` + `check_precedence` implemented; direction of standing-derivation unchecked | acyclicity ≠ directionality; no invariant covers the latter → new criterion | **META-B** |
| **`CMG-L-04`** Non-Self-Elevation | `X.4`, `VI.4`, `IX.16`, `XLIV.7`, `LXXXI.6`, `LXXXIII.3`, `CEP-000 §5.4` | **none located** — the referent of `VAC-01` | **NONE.** `check_superiors` records the vacancy; it does not detect self-elevation | R3.0: enforcement **entrenches** rather than discharges | **META-B** |
| **`CMG-L-12`** Provisional Standing | `X.12`, `XLIV.3`, `LXXX.4`, `XXII.5`, `CEP-006 I.4` | none located | **PARTIAL AND VACUOUS.** `readiness()` caps at `READY-PROVISIONAL`; `check_superiors:348` requires `located is False` — the gate passes *because* the vacancy stays unlocated | consequence of the vacancy, not a repairable mandate | **META-B** |

### `[F]` NEW MEASURED DIVERGENCE — `XV.2` vs the Registry

`XV.2` verbatim: *"The Registry SHALL record, per artifact, **exactly**: identity, kind, standing, reach, precedence rank, declared positive scope, declared negative scope, owner, steward, lifecycle state, version, lineage predecessor, superior references, dependency references, delegation bindings, evidence references, and canonical home path."*

`[F]` Measured: **10 of 17 mandated fields present; 7 absent** — `precedence rank`, `declared positive scope`, `declared negative scope`, `owner`, `steward`, `delegation bindings`, `evidence references`. `[F]` Nothing detects this: no invariant checks `XV.2` field completeness, and `INV-01` is unimplemented. `[I]` Pure META-A — a projection diverging from its constitutional input under `XV.3`'s *"the input governs"*, unverified.

`[F]` Two ancillary measured facts of the same class: `CMG-000001` records `version: 1.2` while `XI.13` declares the invariant set *"CLOSED for version 1.0"*; and `lineage_predecessor: None` at version 1.2, so `check_lineage` (`INV-11`, `CMG-L-11`) has nothing to resolve and passes vacuously over the meta instrument's own version history.

---

## Q3 / Q4 / Q5 — THE THREE-WORLD TEST

`[F]` For each unrealized law: can it be violated in each world?

| Law | **Q3** violable with META-A fully discharged? | **Q4** violable with META-B remaining? | **Q5** violable with META-B hypothetically removed? | Survives all three? |
|---|---|---|---|---|
| `CMG-L-01` | **NO** — `INV-01` implemented ⇒ corpus-wide recognition checked | YES | YES | **NO** — dies in Q3 |
| `CMG-L-10` | **NO** — `INV-10` implemented ⇒ recomputability checked | YES | YES | **NO** — dies in Q3 |
| `CMG-L-03` | **PARTLY** — `XV.2` projection repaired, scope fields projected and reconciled; but no invariant *evaluates* the scope pair | YES | **NO** — ratification permits amendment, invariant addable, criterion created | **NO** — dies in Q5 |
| `CMG-L-09` | **YES** — no META-A clause creates a criterion | YES | **NO** — amendment becomes eligible | **NO** — dies in Q5 |
| `CMG-L-14` | **YES** — as above | YES | **NO** — as above | **NO** — dies in Q5 |
| `CMG-L-05` residual | **YES** | YES | **NO** — as above | **NO** — dies in Q5 |
| `CMG-L-04` | **YES** — reconciliation cannot occupy T1 | YES | **NO** — T1 occupied, self-elevation moot | **NO** — dies in Q5 |
| `CMG-L-12` | **YES** | YES | **NO** — standing conferred, PROVISIONAL ceiling lifts | **NO** — dies in Q5 |

### `[F]` The Q5 mechanism — the AMENDMENT-INELIGIBILITY CHAIN

`[I]` Q5 is decisive for six of eight laws, and it turns on a chain no prior phase assembled. Every link is located and measured.

```
 1. XI.13          "The invariant set IS CLOSED for version 1.0 by this clause
                    and IS extensible by amendment only."
 2. [F] MEASURED   CMG-REGISTRY.json closed_enumerations contains
                    {enumeration: "invariants", article: "XI.13",
                     closing_invariant: "CMG-INV-09"}
                    — and CMG-INV-09 IS IMPLEMENTED (5 occurrences,
                      check_closed_enumerations). The closure of the invariant
                      set is ACTIVELY ENFORCED at HEAD.
 3. XLIII.6        Article XI is "immutable ground"; amendment of it "SHALL
                    require the full MAJOR path".
 4. XXIX.4         "A MAJOR change SHALL require the full ratification path of
                    Article XLIV."
 5. CEP-009 V.1    "An artifact SHALL be eligible for amendment only when it is
                    RATIFIED or FROZEN and its lineage is intact."
 6. [F] MEASURED   CMG-000001 state = DECLARED  (not RATIFIED, not FROZEN;
                    RATIFIED count across all 44 artifacts = 0)
 7. CEP-009 V.4    "An ineligible amendment SHALL NOT proceed; an attempted
                    amendment of an ineligible artifact SHALL be void."
 8. CEP-007 IV.1   Freeze eligibility requires RATIFIED — so the FROZEN branch
                    of V.1 is closed too.
 9. XLIV.3 / XLIV.7  No located competent ratifier; self-ratification IS PROHIBITED.
 ────────────────────────────────────────────────────────────────────────────
 ⇒ [F] THE INVARIANT SET CANNOT BE EXTENDED IN-CORPUS.
   Any design law whose verification requires a criterion that does not exist
   is unverifiable until META-B is resolved — not because verification is hard,
   but because the corpus cannot lawfully add a check to itself.
```

`[I]` **This is the mechanism R3 lacked.** R3 proved floor-2 by showing no candidate ancestor generates both causes. R6 shows *why the residue cannot form a third cause*: the missing seed reaches into the verification apparatus. `L.2` fixes the criteria at twelve *"and nothing else"*; `XI.13` closes the set; `CMG-INV-09` enforces the closure; and amendment — the only declared route to extension — is barred because `CMG-000001` is `DECLARED` rather than `RATIFIED`, and cannot become `RATIFIED` because T1 is vacant.

---

## Q6 — DOES ANY LAW SURVIVE ALL THREE TESTS?

**`[F]` NO. Zero of eight.** Two die in Q3 (generated by META-A). Six die in Q5 (generated by META-B). None is violable in every world, which is the necessary condition for independence from both causes.

---

## Q7 — DOES ANY UNREALIZED LAW REQUIRE ASSUMPTIONS ABSENT FROM META-A AND META-B?

**`[F]` NO.** Every law's non-realization reduces to exactly one of two located assumption sets:

| Assumption set | Content | Laws it explains |
|---|---|---|
| **META-A** — *assertion without verification* | A criterion exists within `L.2`'s closed set and is not evaluated; or a projection diverges from its input and nothing compares them (`XV.2`, `XV.3`, `II.4`) | `CMG-L-01`, `CMG-L-10`, `CMG-L-03` (projection leg) |
| **META-B** — *external authority ceiling / missing seed* | A criterion does not exist, and creating one requires amendment, which requires ratification, which requires the vacant authority; or the law is itself a standing prohibition | `CMG-L-03` (criterion leg), `CMG-L-09`, `CMG-L-14`, `CMG-L-05` residual, `CMG-L-04`, `CMG-L-12` |

`[F]` No third assumption was required to explain any law. `[I]` Notably `CMG-L-03` requires **both** sets and neither alone — which is not residue but overdetermination, and R3's non-redundancy test treats a doubly-explained dependent as explained.

---

## Q8 — REMAINING BLOCKER CLASSES

`[F]` Every class named in the commission, mapped exhaustively.

| Class | Measured content at HEAD | Generated by |
|---|---|---|
| **Blockers** | 100 live blocking dependents | 63 META-A · 37 META-B (`A-R6-02`, carried) |
| **Gaps** | 9 recorded: `CMG-GAP-01/02/03/05/07/08/09` **CLOSED**; `CMG-GAP-04` `STRUCTURAL-EXTERNAL`, `RECORDED-AS-VACANCY`, `closed_by VAC-01`; `CMG-GAP-06` `NOT-CLOSED`, `MINOR` | `-04` → **META-B** · `-06` → substantive process concern outside meta jurisdiction (`XIX.2`), routed to `CMG-OQ-05` → **META-B** (ownership allocation by an unnamed process owner) · rest closed |
| **Open questions** | 7: `OQ-01/02/03/07` OPEN, each `requires: EXPLICIT RATIFICATION`; `OQ-05` OPEN (`OWNERSHIP ALLOCATION BY THE PROCESS OWNER`); `OQ-04`, `OQ-06` CLOSED | all OPEN → **META-B** |
| **Vacancies** | 1: `VAC-01`, T1, `located: false` | **META-B** |
| **Contradictions** | Registry `INVALID` by `XV.5` while the gate is green; `XV.2` field set vs actual; `version 1.2` vs `XI.13`'s *"CLOSED for version 1.0"*; PROBE-3 forged closure passing | **META-A** — each is an unreconciled projection |
| **Inconsistencies** | `L.2` mandates 12 criteria, `L.3` enumerates 8, validator implements 10 (`GAP-R4-03`) | **META-A** realization leg · **META-B** design-law-routing leg (`GAP-R3-02`) |
| **Divergences** | 7 of 17 `XV.2` fields absent; 14 of 19 collections text-unbound; no content hash on any of 44 artifacts | **META-A** |
| **Orphans** | `CMG-INV-03` total over 61 concerns and passing. **T1 occupancy is not a registered concern**, so it cannot be an ownerless owner | **META-B** — a vacuous pass, per R4 |
| **Unbound projections** | 14 of 19 registry collections; `vacancies`, `open_questions`, `readiness` among them | **META-A** |
| **Lifecycle defects** | `lineage_predecessor: None` at version 1.2 ⇒ `check_lineage` vacuous; 32 PROVISIONAL, 1 DECLARED, 0 RATIFIED | vacuity → **META-A** · 0 RATIFIED → **META-B** |
| **Authority defects** | T1 `VACANT`; 4 artifacts rooted in `VAC-01`; `CMG-000001` `DECLARED` with `superiors: ["VAC-01"]` | **META-B** |
| **Validation defects** | `INV-01`, `INV-10` absent; no corpus walk; no regenerator; `L.5` byte-identity unchecked for the meta layer | **META-A** |

`[F]` **Every class maps. No class required a third cause.**

---

## Q9 — MINIMAL GENERATING SET FOR THE REMAINING UNREALIZED LAWS

```
G = { META-A , META-B }        |G| = 2

  META-A ⊢ CMG-L-01, CMG-L-10, CMG-L-03(projection leg)
  META-B ⊢ CMG-L-03(criterion leg), CMG-L-09, CMG-L-14,
           CMG-L-05(residual conjunct), CMG-L-04, CMG-L-12

  covered  = 8 of 8 unrealized laws
  residue  = ∅
```

`[F]` **Minimality.** No proper subset generates the set:
- `{META-A}` alone fails — `CMG-L-09` and `CMG-L-14` are violable in the world where META-A is fully discharged (Q3 = YES), because no META-A clause creates a criterion.
- `{META-B}` alone fails — `CMG-L-01` and `CMG-L-10` are violable in the world where META-B remains **and** in the world where it is removed (Q4 = Q5 = YES), because ratification writes no code. This is R3's constructive `META-B ⇏ META-A`, reconfirmed on a set R3 never tested.

`[F]` `|G| = 2` and `G` is minimal.

---

## Q10 — EXHAUSTIVE SEARCH FOR A THIRD INDEPENDENT META-CAUSE

`[F]` Every candidate was tested against R3's three non-collapse criteria — deontic sign, modality, direction of repair — plus independent grounding and non-redundancy.

| # | Candidate META-C | Deontic sign | Modality | Direction of repair | Verdict |
|---|---|---|---|---|---|
| 1 | **Closure of the invariant set** (`XI.13` + `INV-09` enforcement) | prohibition, **in force and honored** | necessary-until-ratification | enforcement entrenches | **`[F]` REJECTED — this IS META-B's signature.** Same sign, same modality, same direction as `XLIV.7`. It is the missing seed expressed in the verification apparatus, not a distinct cause. Its repeal requires amendment, which requires ratification |
| 2 | **Amendment ineligibility** (`CEP-009 V.1` + `DECLARED` state) | prohibition, in force | necessary-until-ratification | entrenches | **`[F]` REJECTED — derivative of META-B.** `DECLARED` obtains *because* `RATIFIED` is unreachable (`XLIV.3`, `CEP-006 XII.2`) |
| 3 | **`L.2`'s *"and nothing else"*** | prohibition on criteria, in force | contingent under the permissive reading (R4.3) | ambiguous (`UNK-R3-02`) | **`[F]` REJECTED — one-sided.** Under the permissive reading it blocks nothing (`-09`/`-12` precedent). Under the restrictive reading it collapses into candidate 1 |
| 4 | **`XV.2` field divergence** — 7 of 17 absent | mandate, unrealized | contingent | enforcement **eliminates** | **`[F]` ABSORBED into META-A.** META-A's exact signature |
| 5 | **No content hash on 44 of 44 artifacts** | mandate (`CEP-008 XVI.3`, `XLVIII.4`), unrealized | contingent | eliminates | **`[F]` ABSORBED into META-A** |
| 6 | **Vacuous `check_lineage`** — `lineage_predecessor: None` at v1.2 | mandate (`X.11`, `XI.11`), unrealized in substance | contingent | eliminates | **`[F]` ABSORBED into META-A** |
| 7 | **`GAP-R4-02`** — `XV.5` vs `CEP-004 XIV.2`/`XIV.3` | mandate vs prohibition, cross-instrument | contingent | owner reading disposes | **`[F]` REJECTED — one-sided.** Bears on *who may act*; confers and withholds no standing; creates no mandate |
| 8 | **`GAP-R3-01`** — no obligation taxonomy | recording absence | contingent | recording eliminates | **`[F]` REJECTED — generates neither** |
| 9 | **`CMG-GAP-06` / `CMG-OQ-05`** — process-ceremony ownership, outside meta jurisdiction | allocation absence | contingent on an unnamed owner | allocation eliminates | **`[F]` ABSORBED into META-B** — delegated-by-role to an unnamed party; the `OQ-04`/`OQ-06` control cases show that a *named* owner discharges such a question, and this one has none |
| 10 | **Jurisdictional bar** (`XIX.2`, `XIX.5`, `LXXVIII.3`) — the corpus declining questions outside its boundary | prohibition, in force | necessary | entrenches | **`[F]` REJECTED — derivative of META-B.** Declining is `XIX.5`'s *"correct constitutional act"*; the questions declined are the `EXPLICIT RATIFICATION` set |
| 11 | **`version 1.2` vs `XI.13`'s *"version 1.0"*** | mandate, unreconciled | contingent | eliminates | **`[F]` ABSORBED into META-A** |
| 12 | **Certification currency** (`GAP-R4-04`) | observational deficit | contingent | re-running eliminates | **`[F]` REJECTED — not an obligation** |

`[F]` **Twelve candidates. Zero admitted. Four absorbed into META-A, two into META-B, six rejected as one-sided, derivative, or not obligations.**

`[I]` Candidate 1 is the one that had to be refused carefully, and it is the mirror of the trap R3 documented. R3 refused *validator non-enforcement* as a common ancestor because it conceals both causes while enforcement moves them in opposite directions. R6 refuses *invariant-set closure* as a third cause for the converse reason: it looks like a distinct blocker on verification, but its deontic sign, modality and repair direction are identical to `XLIV.7`'s. **It is not a new cause. It is the missing seed reaching one layer further than R3 measured — into the corpus's capacity to add a check to itself.**

---

## REQUIRED PROOFS

### Proof 1 — Every unrealized design law is generated by META-A or META-B

`[F]` By Q1's exhaustive partition of all 14 laws into classes A–F; by Q2's per-law root-dependency column; by Q3–Q5's three-world test in which every law is non-violable in at least one world; and by Q9's coverage of 8 of 8 with `residue = ∅`. ∎

### Proof 2 — At least one unrealized design law is generated by neither

**`[F]` FAILED. No such law exists.** Twelve candidate third causes tested in Q10; zero admitted. Q6 returns zero survivors of the three-world test. Success condition **B is not met**. ∎

### Proof 3 — Minimal basis proof

`[F]` `G = {META-A, META-B}`, `|G| = 2`. Generation shown in Q9. Minimality shown by two counterexamples: `{META-A}` fails on `CMG-L-09`/`CMG-L-14` (Q3 = YES); `{META-B}` fails on `CMG-L-01`/`CMG-L-10` (Q4 = Q5 = YES). No size-1 subset generates the set. ∎

### Proof 4 — Counterfactual proof

`[F]` Three worlds executed per law (Q3/Q4/Q5). `WORLD(META-A discharged)` is non-empty — `CMG-L-09`, `CMG-L-14`, `CMG-L-05` residual, `CMG-L-04`, `CMG-L-12` all remain violable. `WORLD(META-B removed)` is non-empty — `CMG-L-01`, `CMG-L-10` remain violable, since ratification writes no code. **Both worlds non-empty ⇒ neither cause is derivable from the other over the unrealized-law set.** ∎

### Proof 5 — Entailment proof

`[F]` `META-A ⊬ CMG-L-09`: full discharge realizes criteria within `L.2`'s closed set and creates no new criterion; `CMG-L-09` has none. `META-B ⊬ CMG-L-10`: `CMG-INV-10` lies inside `L.2`'s exhaustive set, so its realization engages no amendment and never reaches `XXIX.4`'s ratification path — R3's constructive falsification, reconfirmed. **The entailment relation over `G` remains EMPTY.** ∎

### Proof 6 — Independence proof

`[F]` Each member carries laws the other cannot explain: META-A carries `CMG-L-01`, `CMG-L-10`; META-B carries `CMG-L-09`, `CMG-L-14`, `CMG-L-04`, `CMG-L-12`. Removing either leaves ≥2 laws unexplained. `[F]` The members remain categorially distinct on all three R3 axes — META-A an unrealized **mandate**, contingent, eliminated by enforcement; META-B an in-force **prohibition**, necessary, entrenched by enforcement. ∎

### Proof 7 — Exhaustive residue proof

`[F]` 14 of 14 design laws classified. 8 unrealized, 8 generated, residue `∅`. 13 blocker classes in Q8, all mapped. 12 basis-expansion candidates in Q10, none admitted. 9 recorded gaps, 7 open questions, 1 vacancy — all attributed. **No unattributed obligation, blocker, gap, contradiction, divergence, orphan, unbound projection, lifecycle defect, authority defect or validation defect was located.** ∎

---

## OUTPUT

# `FLOOR-2 CONFIRMED`

`[F]` **Success condition A obtains: every unrealized design law maps to META-A or META-B with no residue. Success condition B fails: no law is generated by neither.** `META-C` is **REJECTED**.

### `UNK-R3-05` — DISCHARGED

`[F]` R3 asked whether a third meta-cause hid behind the unrealized design laws. **It does not.** R5 identified this as the sole live falsification risk to floor-2. R6 resolves it in the negative, and the resolution supplies R3's proof with a mechanism it did not have.

### What R6 adds beyond confirmation

1. `[F]` **R3's census over-counted.** 11 of 14 by identifier; 8 of 14 by substantive coverage. `CMG-L-02`, `CMG-L-11`, `CMG-L-13` are enforced through their invariants without being named.
2. `[F]` **The amendment-ineligibility chain.** `XI.13` closes the invariant set · `closed_enumerations` records the closure · `CMG-INV-09` **enforces** it and is implemented · `XLIII.6` makes Article XI immutable ground · `XXIX.4` routes MAJOR change to Article XLIV ratification · `CEP-009 V.1` requires `RATIFIED` or `FROZEN` for eligibility · `CMG-000001` is `DECLARED` · `CEP-009 V.4` voids ineligible attempts · `CEP-007 IV.1` closes the `FROZEN` branch · `XLIV.7` forbids self-ratification. **The corpus cannot lawfully add a check to itself.**
3. `[F]` **`XV.2` divergence** — the Registry records 10 of 17 mandated per-artifact fields; `precedence rank`, `positive scope`, `negative scope`, `owner`, `steward`, `delegation bindings`, `evidence references` are absent from all 44 entries, undetected.
4. `[F]` **Two further vacuous passes** — `check_lineage` has nothing to resolve (`lineage_predecessor: None` at version 1.2), and `version 1.2` stands against `XI.13`'s *"CLOSED for version 1.0"*.
5. `[I]` **The deepest located consequence of META-B.** R3 placed the missing seed at ratification competence. R4 placed it at the observability of the vacancy record. R6 places it inside the verification apparatus: **the set of things the corpus may check about itself is closed, its closure is actively enforced, and it can be reopened only by an authority that does not exist.** META-B does not merely withhold finality — it fixes the boundary of self-knowledge.

### Basis and floor

> `[F]` **At HEAD: `{ META-A , META-B }`, size 2, entailment relation EMPTY, residue ∅.**
>
> `[F]` **META-A** — assertion without verification. Generates `CMG-L-01`, `CMG-L-10`, `CMG-L-03`'s projection leg, every divergence, every unbound projection, every validation defect. **Movable, and now with three further measured instances.**
>
> `[F]` **META-B** — external authority ceiling / missing seed. Generates `CMG-L-03`'s criterion leg, `CMG-L-09`, `CMG-L-14`, `CMG-L-05`'s residual conjunct, `CMG-L-04`, `CMG-L-12`, every open question, the vacancy, every authority defect — **and the closure of the invariant set itself.** Immovable.
>
> `[F]` **Floor = 2. Confirmed, not merely unfalsified.**

**This determination falsifies, exhausts and concedes. It recommends nothing, designs nothing, amends nothing, implements nothing, and eliminates nothing.**

---

## CLASSIFIED RESIDUE

### FACTS `[F]`
1. Design-law identifier census reproduced exactly: 11 of 14 at zero; only `CMG-L-06` (1), `CMG-L-07` (4), `CMG-L-08` (1) appear.
2. Invariant census: `CMG-INV-01` and `CMG-INV-10` at **zero**; the other ten at 2–5 occurrences.
3. Substantive coverage: 8 of 14 laws genuinely unrealized, not 11. `CMG-L-02`, `CMG-L-11`, `CMG-L-13` are enforced via `INV-02`, `INV-11`, `INV-12`.
4. `XV.2` mandates 17 per-artifact fields *"exactly"*; **10 present, 7 absent** across all 44 artifacts.
5. `CMG-REGISTRY.json` `closed_enumerations` records `{enumeration: "invariants", article: "XI.13", closing_invariant: "CMG-INV-09"}`, and `CMG-INV-09` is implemented — **the closure of the invariant set is actively enforced**.
6. `CEP-009 V.1` — *"eligible for amendment only when it is ratified or frozen"*; `V.4` — an ineligible attempt *"SHALL be void"*.
7. `CMG-000001` state = `DECLARED`, version `1.2`, `lineage_predecessor: None`, `superiors: ["VAC-01"]`. `RATIFIED` across all 44 artifacts = **0**.
8. `XXIX.4` — *"A MAJOR change SHALL require the full ratification path of Article XLIV."* `XLIII.6` — Article XI is immutable ground requiring the full MAJOR path.
9. `XIX.1` and `XIX.2` declare `CMG-000001`'s positive and negative scope in text; **neither is projected into the Registry**, and no clause labelled *negative scope* appears in `CEP-000`.
10. `reach` carries three values over 44 artifacts (`DOMAIN-SCOPED` 20, `CORPUS-WIDE` 13, `PROGRAM-SCOPED` 11) against five declared; it is not the scope pair `X.3` requires.
11. 9 recorded gaps: 7 CLOSED, `CMG-GAP-04` recorded as vacancy, `CMG-GAP-06` NOT-CLOSED.
12. Three-world test: zero of eight laws violable in all three worlds.
13. Twelve candidate third causes tested; zero admitted.
14. HEAD unchanged; read-only throughout; validator re-verified at findings 0 / `READY-PROVISIONAL` / exit 0.

### INFERENCES `[I]`
1. **Identifier absence is not non-realization** — the instrument R3 used over-counted the unrealized set by three.
2. **The missing seed reaches into the verification apparatus.** The corpus cannot add a check to itself: the criteria set is closed, the closure is enforced, and reopening requires an authority that does not exist.
3. **Invariant-set closure is not META-C.** Its deontic sign, modality and repair direction are identical to `XLIV.7`'s — the mirror of the trap R3 documented for validator non-enforcement.
4. **`CMG-L-03` is overdetermined, not residual.** It requires both causes and neither alone; a doubly-explained dependent is explained.
5. **The two causes remain categorially distinct** on all three R3 axes over a law set R3 never tested.
6. **META-B fixes the boundary of the corpus's self-knowledge**, which is a stronger consequence than withholding finality.

### ASSUMPTIONS `[A]`
`A-R6-01` The design-law→invariant correspondence is derived from clause texts, not located. No instrument declares it; `GAP-R3-02` is that absence.
`A-R6-02` The 63/37 partition is carried from R1/R2, not re-derived (inherits `A-R4-01`, `A-R5-03`).
`A-R6-03` "Substantive coverage" is judged by whether an implemented check asserts the law's predicate; no located instrument defines coverage.
`A-R6-04` The three-world test treats "META-B removed" as ratification occurring; no located clause describes that world's mechanics beyond `CEP-006 XII.2`.
`A-R6-05` Measured at `1e3e4ba9` in this environment.

### GAPS `[GAP]`
| Id | Gap | Disposition |
|---|---|---|
| `GAP-R6-01` | The Registry records 10 of the 17 per-artifact fields `XV.2` mandates *"exactly"*; 7 absent across all 44 entries, undetected | **NEW · ABSORBED into META-A** |
| `GAP-R6-02` | `check_lineage` passes vacuously over the meta instrument: `lineage_predecessor: None` at version `1.2`; and `XI.13` declares the invariant set closed *"for version 1.0"* while the instrument stands at `1.2` | **NEW · ABSORBED into META-A** |
| `GAP-R6-03` | No located instrument declares which invariant verifies which design law, so design-law realization is unmeasurable except by derivation | **NEW · SURVIVING** — refines `GAP-R3-02`, inherits `GAP-R3-01` |
| `GAP-R4-02` · `GAP-R4-04` · `GAP-R5-01` · `GAP-R3-01…04` | carried | unchanged by R6 |

### UNKNOWNS `[UNKNOWN]`
`UNK-R3-05` **DISCHARGED** — no third meta-cause exists behind the unrealized design laws.
`UNK-R6-01` Whether `CMG-L-09` (Neutrality) is *substantively* satisfied at HEAD. R6 determined it is **unverifiable** — no criterion, no projected field — and did not attempt a textual audit of the corpus for technology naming; that would be discovery, barred here.
`UNK-R6-02` Whether the 7 absent `XV.2` fields are recoverable by projection from artifact text, or absent from the text as well. `XIX.1`/`XIX.2` show the scope pair exists for `CMG-000001`; the other 43 were not checked.
`UNK-R5-01` · `UNK-R3-02` · `UNK-R4-01` · `UNK-R4-02` · `RES-01…09` — carried unchanged.

---

*PHASE R6 · AUTHORITY = NONE (DERIVED TRUTH) · Reports; determines nothing.*
*`READY-PROVISIONAL`; Tier T1 VACANT; `CMG-L-12` applies to every statement herein.*
*Read-only: nothing implemented, nothing amended, corpus unchanged.*
*Reproduce: design-law and invariant identifier census over `00-CMG/tools/cmg_validate.py`; `XV.2` field comparison against `CMG-REGISTRY.json` `artifacts[]`; `closed_enumerations` read; `CEP-009 V.1`/`V.4`, `XXIX.4`, `XLIII.6`, `XI.13` reads.*
