# DISCOVERY CONSOLIDATION REPORT — MCRF / STREAM-00 / WP-001A

| Field | Value |
|---|---|
| WORK PACKAGE | `MCRF / STREAM-00 / WP-001A` — Discovery Reconciliation |
| AUTHORITY | **NONE (DERIVED ANALYSIS ONLY)** |
| COMPANION | `DISCOVERY-REGISTER.md` — 981 canonical discoveries, `DR-0001`…`DR-0981` |
| SOURCE SET | 14 determination artifacts, **7,878 lines** |
| CLASSIFICATION | Every statement carries `[F]` Fact · `[I]` Inference · `[A]` Assumption · `[GAP]` · `[UNKNOWN]` |
| WHAT THIS DOCUMENT DOES | Deduplicates. It closes nothing, ratifies nothing, allocates nothing, amends nothing, and admits nothing into any constitutional instrument. |
| REPRODUCE | `python3 .runtime/wp-001a/extract.py && python3 .runtime/wp-001a/reconcile.py && python3 .runtime/wp-001a/render.py` |

---

## 0 — HEADLINE RESULT

**`[F]` 1,161 discovery occurrences reduce to 981 canonical discoveries, and the 981 reduce
further — to 2 meta-causes.**

The reduction is not this report's construction. It is the fourteen artifacts' own arithmetic,
reproduced from the outside and found consistent:

```
3,775  enumerated uncertainty items         (R0.1, machine sweep over 293 JSON registers)
  281  OPEN                                 (R0.1.2)
  249  after removing 7 mirror pairs         (R0.2.1)
   61  after instance→pattern reduction      (R0.2.2 · UICM 158→9, RPI 30→1)
   10  independent roots                     (R0.4.1)
    6  irreducible blocker basis, unique     (R1.9 — 10→6 in four steps)
    2  ontological basis {META-A, META-B}    (R2.7, floor proved at 2)
```

**`[I]` The consolidation's single most useful finding is that the corpus's duplication is
lexical, not logical.** The corpus holds **nine** distinct located class names for one divergence
failure and **eight** for one standing failure, drawn from a vocabulary of **148** located failure
classes (`A06`:213). Nine recognitions, nine names, zero generalisations. Every large equivalence
class in §3 below has the same shape: one defect, recognised repeatedly, renamed each time, and
never reduced.

**`[F]` And the duplication does not shrink the open set.** Of 981 canonical discoveries,
**150 are OPEN**, **59 are undischarged assumptions**, **35 are conflicts**, and **18 are
blockers**. Deduplication removed 180 occurrences and **zero** obligations.

---

## 1 — EXACT DUPLICATES

**`[F]` 180 exact duplicate occurrences, all of one kind: a phase-scoped identifier carried
forward verbatim into a later phase's residue table.**

An occurrence is an exact duplicate when the identifier string, its declaring namespace and its
subject are identical to an earlier occurrence. Every one of the 180 is bound in the register to
the `DR-ID` of its declaring occurrence.

| Carried identifier | Declared in | Carried through | Occurrences |
|---|---|---|---:|
| `UNK-R3-02` | `A07` PHASE-R3 | `A08` → `A09` → `A10` → `A11` → `A12` | 9 |
| `FB-2` | `A14` FOUNDATION | within `A14` (verdict · matrix · §3.2 · §6.1 · §9) | 8 |
| `FB-1` | `A14` FOUNDATION | within `A14` (verdict · matrix · §3.2 · §6.1 · §9) | 8 |
| `UNK-R4-01` | `A08` PHASE-R4 | `A08` → `A09` → `A10` → `A11` | 7 |
| `FB-3` | `A14` FOUNDATION | within `A14` | 7 |
| `UNK-R5-01` | `A09` PHASE-R5 | `A09` → `A10` → `A11` → `A12` | 6 |
| `UNK-R4-02` | `A08` PHASE-R4 | `A08` → `A09` → `A10` → `A11` | 6 |
| `GAP-R4-02` | `A08` PHASE-R4 | `A08` → `A09` → `A10` → `A11` | 6 |
| `GAP-R4-04` | `A08` PHASE-R4 | `A08` → `A09` → `A10` → `A11` | 6 |
| `UNK-R3-01` | `A07` PHASE-R3 | `A08` → `A09` (resolved at `A09`) | 5 |
| `UNK-R3-05` | `A07` PHASE-R3 | `A08` → `A09` → `A10` (discharged at `A10`) | 5 |
| `GAP-R3-01` | `A07` PHASE-R3 | `A08` → `A09` → `A10` → `A11` → `A12` | 5 |
| `GAP-R3-02` | `A07` PHASE-R3 | `A08` → `A09` → `A10` | 5 |

**`[I]` The carrying discipline is sound and is worth recording as such.** Every later phase
restates the inherited residue rather than assuming it, and every restatement either carries the
item unchanged, reduces it, or discharges it with named evidence. No inherited item is silently
dropped anywhere in the fourteen artifacts. That is the reason a 981-row register can be built
mechanically at all.

**`[F]` One structural exception.** `A14` FOUNDATION-UNCONDITIONAL-READINESS re-states each of its
own three blockers up to eight times inside one document (executive verdict, readiness matrix,
blocker audit, architectural analysis, decision table, distance-to-READY). These are intra-artifact
duplicates, not cross-phase carries, and they are bound to the same `DR-ID`.

---

## 2 — NEAR DUPLICATES

**`[F]` Six near-duplicate pairs — same subject, different scope or rank, where the later item is a
strict refinement rather than a restatement.** The distinction matters because a refinement changes
what would discharge the item.

| # | Earlier | Later | Relation | Located ground |
|---|---|---|---|---|
| 1 | `GAP-R3-02` — `XLIX.5` routes `CMG-L-01…14` to the Article L validator while `L.2` restricts criteria to `CMG-INV-01…12` | `GAP-R4-03` — `L.2`'s criteria set and `L.3`'s procedure enumeration do not correspond: 2 mandated-unimplemented, 2 unenumerated-implemented | **REFINEMENT one rank deeper**; `GAP-R4-03` absorbed into `GAP-R3-02` | `A08`:545 |
| 2 | `GAP-R3-02` | `GAP-R6-03` — no located instrument declares which invariant verifies which design law | **REFINEMENT**; inherits `GAP-R3-01` | `A10`:322 |
| 3 | `GAP-R2-01` — no located clause classifies constitutional defects by logical type | `GAP-R3-01` — no located instrument classifies obligations by deontic sign | **GENERALISATION**; `GAP-R3-01` is the wider absence and the one the floor rests on | `A07`:387 |
| 4 | `GAP-R1-01` — no entailment register between constitutional defects | `GAP-R3-04` — no entailment register between meta-causes | **SAME ABSENCE AT META RANK**; `A07` records it as *"`GAP-R1-01` inherited and unresolved at meta rank"* | `A07`:390 |
| 5 | `GAP-O-05` — no content-hash binding between constitutional text and any projection | `DIV-01` — the text binding is a `VERSION` string comparison | **SAME DEFECT, TWO STATEMENTS**; both retired by `A02`, which locates a current, gate-enforced anchor | `A02`:458 |
| 6 | `GAP-R7-02` — 11 artifacts `FROZEN` while `RATIFIED` = 0 | `GAP-R6-01` — the Registry records 10 of the 17 `XV.2` fields | **COMPOUNDING, not duplication**; `A11` records `GAP-R7-02` as *"compounded by `GAP-R6-01`"* | `A11`:458 |

**`[I]` Near-duplication in this corpus runs in the direction of increasing precision.** In every
one of the six pairs the later statement is narrower, and in four of six the later statement names
a clause the earlier one did not. A deduplication that merged these pairs would lose the clause
citation that makes the later item falsifiable.

---

## 3 — EQUIVALENT DISCOVERIES UNDER DIFFERENT WORDING

**`[F]` Seventeen equivalence classes. 96 identifiers collapse to 17 subjects.** Each class below is
asserted by the artifacts themselves, not inferred here.

| # | Equivalence class | Member identifiers | Canonical statement | Ground |
|---|---|---|---|---|
| E-01 | **The reconciliation mandate, unrealized** | `META-A` · `XV.5` · `XI.10`/`CMG-INV-10` · `CMG-L-10` · `R3` · `R4` · `R6` · `R7` · `R8` · `GAP-R2-02` · `GAP-R2-04` | One correspondence duty between a constitutional fact and its projection, declared at invariant rank in a closed criteria set and realized nowhere | `A06`:256 · `A06`:402 |
| E-02 | **`ROOT-Ω` — a corpus cannot self-confer standing** | `META-B` · `K-01` · `K-10` · `K-11` · `K-14` · `RES-05` · `RES-06` · `RES-07` · `RES-08` · `B-10` · `B-11` · `B-12` · `B-13` · `DEF-02` · `UCCEP-F-004` · `VAC-01` · `CMG-OQ-02` | One prohibition, doubly proved from disjoint clause sets, yielding incompleteness rather than inconsistency | `A02`:463 · `A08`:490 |
| E-03 | **Nine names for one divergence failure** | `REGISTRY-DRIFT` · `REPOSITORY-DRIFT` · `STANDING-LEDGER-DIVERGENCE` · `STANDING-REGISTER-DIVERGENCE` · `STANDING-RESOLUTION-DIVERGENCE` + 4 more | The corpus recognised the same failure nine times, named it nine times, generalised it zero times | `A06`:266 |
| E-04 | **Eight names for one standing/external failure** | 8 located class names of 148 | As above, for external standing | `A06`:213 |
| E-05 | **`UCKP-LAW-0001` T4 versus SUPREME** | `SC-01` · `C-02` · `B-07` · `R7` (basis root) · `GAP-P-09` · `SOUND-01` | A tier-4 execution artifact declaring self-derived supreme authority, with a passing gate enforcing it | `A02`:513 |
| E-06 | **Registration universe ≠ constitutional corpus** | `SC-02` · `C-05` · `K-13` · `R6` (basis root) · `GAP-P-06` · `GAP-R3-03` | 48% of the constitutional corpus lies outside every hash-bearing register; `EXCLUDE_DIR_PREFIXES` excludes exactly what `register.sh --guard` reconciles | `A07`:415 |
| E-07 | **`CMG-000001` PRE-EFFECT while exercising META force** | `CE-01` · `C-03` · `B-06` · `SOUND-02` · `GAP-P-01` · `R8` (basis root) · `AMB-09` | The committed state is its own counterexample: constitutional truth `NOT-READY`, validator truth `READY-PROVISIONAL` | `A02`:505 |
| E-08 | **Act semantics** | `GAP-O-02` · `K-12` · `B-03` · `AMB-01` · `AMB-08` · `UD-04` · `ACT-ATOMICITY-GAP` → superseded by `ACT-SEMANTICS-EXTERNAL-SCOPE-GAP` · `G-Q-01` · `G-Q-02` | Not *"atomicity is undefined"*: atomicity is located for seven subject classes and for none of them an act; the residual gap is external scope and is unclosable by amendment | `A03`:337 |
| E-09 | **`XXV.3`'s outstanding self-mandated amendment** | `GAP-O-03` · `GAP-O-06` · `AMB-02` · `AMB-03` · `C-04` · `B-04` · `R4` (basis root) | Six of nine `CEP-006` VI.1 states unmapped, `ACCEPTED` among them, and the conflict rule mandates an amendment that does not exist | `A01`:756 |
| E-10 | **No tier↔role correspondence rule** | `GAP-P-03` · `AMB-06` · `R7` (basis root, degenerate case) | The absence is total; `A06` records it as *"the degenerate case — no rule is declared anywhere"* | `A06`:214 |
| E-11 | **The T1 vacancy, in readiness vocabulary** | `RU-19` · `RU-20` · `MP2-C-04` · `RES-01` · `RES-02` · `D-01` · `D-03` | Re-measured `VACANT`; a ceiling on certification standing, and — under `A14`'s strict rule — not a foundation blocker | `A14`:183 |
| E-12 | **Supersession legislated and never exercised** | `G-11` (`A14`) · `RU-18` · `FB-2` (corpus-plane half) | 0 `SUPERSEDED` of 1,579 artifacts; 0 of 1,822 history events; the vocabulary exists at `ukb.py:344` | `A14`:197 |
| E-13 | **The competence question** | `UNK-R7B-01` · `K-5` (`A12`) · `P-5` · `GAP-R7B-02` · `CMG-OQ-01` · `RES-02` · `UNK-R7A-01` | `A12` states the identity explicitly: *"`= K-5 = P-5`"*. One undecidable reading, five names | `A12`:724 |
| E-14 | **Self-verification cannot ground itself** | `K-02` · `U-02` · `UP-01` · `GAP-P-09` · `GAP-R2-05` · `CAA-INV-01` | The verifier is inside the verified system; `CMG-INV-10`'s verification condition is the exit status of the program that omits it | `A06`:446 |
| E-15 | **Objective terms with no located criterion** | `G-01`…`G-10` · `I-01`…`I-07` · `U-01`…`U-03` · `B-01` | Ten undefined terms; five impossible to define under clauses the corpus already holds | `A13`:678 |
| E-16 | **Unowned scopes** | `G-11`…`G-18` (`A13`) · `B-02` · `UC-06` · `D-10` | Eight scopes with no recorded discovery, classification or disposition under `LXXVI.2(a)`–`(c)` | `A13`:679 |
| E-17 | **Determinism and reproducibility of measurement** | `A-03` (`A01`) · `A-P-05` · `A-R-05` · `A-R1-05` · `A-R2-05` · `A-R4-06` · `A-R5-06` · `A-R6-05` · `A-R7-05` | Nine artifacts each record the same undischarged assumption: measurements hold for `1e3e4ba9` **in this environment**; cross-environment hermeticity untested | `A01`:781 |

**`[I]` E-17 is the equivalence class with the widest reach and the least attention.** Nine of the
fourteen artifacts independently record that their quantitative claims are environment-local. No
artifact discharges it, and no artifact treats it as a blocker. It is the single assumption on which
every executed measurement in the whole set rests.

---

## 4 — CONFLICTING DISCOVERIES

**`[F]` 35 conflicts registered. They partition into three kinds, and the kinds have different
remedies.**

### 4.1 Constitutional conflicts — primary text against primary text

| Conflict | Sides | Resolution rule located? |
|---|---|---|
| `GAP-R7B-01` | `CMG-000001` `P.6` s1 (*ratification occurs under `CEP-006`*) versus `P.6` s3 (*the competent authority is an open question*) — **one clause, internally contradictory** | `LIV.3(d)` classifies it; nothing resolves it |
| `GAP-R7B-02` = `K-5` = `P-5` | `XLIV.2` (tier-competence condition) versus `LXXXII.7` + `XIX.2` (delegation conditions nothing; ratification outside CMG scope) | `XIX.6`/`X.13`/`LXXXI.7` supply the **rule**; no located text applies it |
| `GAP-R7B-03` | `CEP-006` scope *"of the Program"* versus `LXXXI.3` (`CMG-000001` orthogonal to Program Authority) | none |
| `GAP-R7-01` | `CMG-T-09` (`PROVISIONAL → FROZEN` permitted) versus `CEP-007` `IV.1`/`V.1` (freeze requires `RATIFIED`) | `CMG-L-13` supplies a rule; no located text selects the reading |
| `GAP-R4-02` | `XV.5` names the Article L validator as regenerating agent versus `CEP-004` `XIV.2`/`XIV.3`/`XXI.3` forbidding it to write | `L.6` supplies a disposition rule, not the reading |
| `GAP-R2-06` | `L.2` (*criteria are `CMG-INV-01…12` **and nothing else***, 12) versus `L.3` (realization sub-clauses for 8) | none |
| `C-06` | `CMG-INV-09` (no finite ceiling) versus `XI.13` (invariant set **IS CLOSED**) | confined by `XI.13` to the checking apparatus; **confined, not resolved** |
| `C-01` / `SC-04` | percentage completeness scoring versus `LXXIX.6`'s prohibition on scores | `LXXIX.6` governs; the scoring artifact stands |

### 4.2 Representation conflicts — machine against text

| Conflict | Statement | Detected by any gate? |
|---|---|---|
| `SOUND-01` | Five-tier authority inversion effected in `engine/uckp/alignment.py`, enforced by a green gate | **NO** — invisible to `cmg_validate.py` |
| `SOUND-02` | `PRE-EFFECT` artifact exercising `META` force; `XXVII.3` requires it to block certification | **NO** — `check_lifecycle` tests `POST-EFFECT` only |
| `SOUND-03` | Constitutional law classified as non-artifact | **NO** |
| `CE-01` | Constitutional truth `NOT-READY` versus validator truth `READY-PROVISIONAL` — **the committed state** | **NO** — 0 findings, exit 0 |
| `GAP-R2-05` | `CMG-INV-10`'s verification condition satisfied by the validator that omits it | **NO** — self-certifying by construction |
| `GAP-R4-01` | Complete forged closure of `META-B` produces `findings 0`, `readiness READY`, `exit 0` | **NO** — detection fails on referent removal |
| `GAP-P-07` | `ukb.py` infers lifecycle status from status strings, contrary to `XXVII.5` | **NO** |
| `C-09` / `UCAF-RC-01…03` | Recorded authority absence and located authority presence both stand as Repository Truth, undisposed | **NO** |

**`[F]` Every located divergence is permissive.** `A02`:460 — no over-strict instance exists in the
whole corpus. `CMG-L-08` makes this structural: a validator forbidden to hard-code the constitution
can only ever be as strict as its projection.

### 4.3 Register conflicts — this report's own layer

**`[F]` 20 identifier namespace clashes.** The same string denotes different discoveries in
different artifacts: `A-01`…`A-08` (`A12` authority edges versus `A13` assumptions), `UNK-01`…`UNK-06`
(`A01` unknowns versus `A13` unknowns), `K-1`…`K-5` (`A12` circular dependencies versus `A14` READY
criteria), `G-11` (`A13` unowned scope *Economics* versus `A14` supersession-unused).

**`[I]` These clashes are `GAP-R-01` observed from the outside.** `A04`:415 records that no global
identifier-namespace registry exists and that short-form identifiers are mechanically ambiguous.
Building this register required exactly the disambiguation `GAP-R-01` says is unavailable, and the
disambiguation had to be reconstructed from each artifact's surrounding text. **The gap is not
theoretical; it was encountered.**

---

## 5 — SUPERSEDED DISCOVERIES

**`[F]` 14 identifiers superseded, every one by a named later artifact on named evidence.** No
supersession in this table is this report's own finding.

| Superseded | Disposition | By | The correcting artifact's ground |
|---|---|---|---|
| `GAP-O-02` | **REJECTED-CORRECTED** | `A03` | Atomicity IS located for 7 subject classes and predicated of no act; the real gap is `ACT-SEMANTICS-EXTERNAL-SCOPE-GAP`, externally blocked rather than internally eliminable |
| `GAP-O-05` | **REJECTED-FALSIFIED** | `A02` | The content anchor exists, is current, and is gate-enforced on every push. *"Phase O called this 'no hash exists'; that was wrong, and the true shape is worse, because the remedy was already present and unused."* |
| `K-12` | **REJECTED-REVERSED** | `A03` | The `internally blocked` classification is reversed by the nine `"of the Program"` scoping clauses plus `CEP-000` §6.4 |
| `A-R2-01` | **REJECTED-REFUTED** | `A06` addendum | `A-R2-08` records the 8-clause reconciliation set demonstrably incomplete: `XI.1` and `XI.10` are additions to it |
| `UNK-R3-01` | **CLOSED-RESOLVED** (negatively) | `A09` | 42 META-A clauses located in `CMG-000001` alone; 14 outside `A07`'s 18-clause set |
| `UNK-R3-03` | **CLOSED-RESOLVED** | `A09` | Post-discharge the predicate contains its own subject; exit-zero becomes non-vacuous for `CMG-INV-10` |
| `UNK-R3-05` | **CLOSED-DISCHARGED** | `A10` | Exhaustive three-world test over all 14 design laws: no third meta-cause exists |
| `UNK-R4-03` | **CLOSED-RESOLVED** | `A09` | Regenerate-and-compare *is* the comparison discharge performs |
| `UNK-R7A-01` | **CLOSED-RESOLVED AS UNDECIDABLE** | `A12` | Superseded by `UNK-R7B-01`, which states the residue precisely |
| `GAP-R4-01` | **ABSORBED** into `META-A` | `A08`, then `A09` | Instance of `R1`-basis roots `R6`/`R7`; revealed then discharged under full META-A discharge |
| `GAP-R4-03` | **ABSORBED** into `GAP-R3-02` | `A08` | A strict refinement one rank deeper, not an independent gap |
| `GAP-R6-01` | **ABSORBED** into `META-A` | `A10` | `XV.2` field projection — the same unverified correspondence |
| `GAP-R6-02` | **ABSORBED** into `META-A` | `A10` | Vacuous `check_lineage` over the meta instrument |
| `GAP-O-01` | **CARRIED-OPEN** | `A04` | Re-derived at `R0.1` `[F]`13 as still standing: the referral cannot terminate |

### 5.1 Re-attributed roots — supersession of cause rather than of item

| Root | Disposition | By | Ground |
|---|---|---|---|
| `R2` | **REDUCED** — absorbed by `ROOT-Ω` at root level | `A05` | `CEP-006` I.4 is a conditional whose antecedent `ROOT-Ω` supplies; strip `ROOT-Ω` and I.4 never triggers |
| `R5` | **REDUCED** — absorbed by `ROOT-Ω` | `A05` | as above |
| `R9` | **REDUCED** — not blocking | `A05` | Its own register records `blocking_failures: []` |
| `R10` | **REDUCED** — not blocking | `A05` | Its own register records `verdict: pass` |
| `R3` | **RE-ATTRIBUTED** | `A06` | `CMG-L-08` is exculpated; regeneration satisfies zero-hard-coding and reconciliation at once. The cause is `XV.5` unimplemented — itself re-attributed once more, to `XI.10` |

### 5.2 Corrections that changed a cause without retiring an identifier

| Correction | From | To | By |
|---|---|---|---|
| Deepest located cause of META-A | `XV.5` (falsifiable) | `XI.10` / `CMG-INV-10` (circular) | `A06` addendum §A.5 |
| META-A's constitutional force | *"declared in 8 Articles, mandated in none"* | **mandated at invariant rank** inside a closed criteria set | `A06` addendum §A.3 |
| META-A's clause corpus | 18 clauses | **51 clauses**, 42 in `CMG-000001` alone | `A09` §R5.1 |
| Unrealized design laws | 11 of 14 | **8 of 14** (6 wholly, 2 partially) | `A10` Q1 |
| `WORLD-A` post-discharge state | asserted as occupancy | downgraded to a **ceiling** statement | `A09` §R5.9 |
| Freeze ineligibility | under-stated in `A08`, `A09` | corrected and widened | `A11` §R7.0 |
| `II.4` validator mentions | 3 | **0** (the 3 were `XII.4`/`XVII.4` substring artifacts) | `A06` addendum §A.2 |
| pytest stage failure cause | coverage floor | **tests** — coverage is 97% against a floor of 90 | `A14` §8.1 |
| *"23 failing tests"* | standing figure | a stale `pytest` `lastfailed` cache | `A14` §8.3 |
| `ISD-G-07`/`ISD-G-08` | closed technology enumerations | **not a closure** — documentary lists that gate nothing | `A14` §3.1 |
| `RU-11`, `RU-17` | blocking | **misclassified** | `A14` §3.1 |

**`[I]` The correction pattern is monotone in one direction and it is worth stating plainly.**
Every correction in §5.2 makes a claim *narrower and better grounded*, and several make the
underlying defect *worse* while making the statement of it *weaker* — `A02`'s treatment of
`GAP-O-05` is the clearest case: the remedy turned out to exist and be unused, which is a more
serious finding than its absence. **`A01`:831 anticipates this and states it as a rule: the
impossibility proofs in this corpus have been getting weaker, and correctly so.**

---

## 6 — DISCOVERY CHAINS

**`[F]` The fourteen artifacts form one provenance chain with a strictly forward evidence flow and
a strictly backward correction flow.**

```
A01 PHASE-O ──▶ A02 PHASE-P ──▶ A03 PHASE-Q ──▶ A04 R0 ──▶ A05 R1 ──▶ A06 R2(+addendum)
      ──▶ A07 R3 ──▶ A08 R4 ──▶ A09 R5 ──▶ A10 R6 ──▶ A11 R7 ──▶ A12 R7B
A13 ABSOLUTE-END-STATE   (consumes A01, A02; corrected by A03 on K-12)
A14 FOUNDATION-UNCONDITIONAL-READINESS   (independent evidence base; 20 standing conditions)

corrections (backward edges):
  A02 ──corrects──▶ A01 (GAP-O-05)
  A03 ──corrects──▶ A01 (GAP-O-02), A13 (K-12)
  A05 ──corrects──▶ A04 (root-set level confusion; R9/R10 non-blocking)
  A06 ──corrects──▶ A05 (CMG-L-08 exculpated)
  A06 ──corrects──▶ A06 (addendum: II.4 count; deepest cause XV.5 → XI.10)
  A08 ──corrects──▶ its own phase input (state vocabulary; certification claim)
  A09 ──corrects──▶ A07 (WORLD-A modality; 18 → 51 clauses)
  A10 ──corrects──▶ A07 (census was the wrong instrument; 11 → 8 laws)
  A11 ──corrects──▶ A08, A09 (freeze ineligibility under-stated)
  A12 ──corrects──▶ A11/R7A (B_min characterisation; competence versus authority)
  A14 ──corrects──▶ prior readiness registers (5 reclassifications, 2 stale figures)
```

**`[F]` Eleven backward correction edges across fourteen artifacts.** Not one artifact accepts its
predecessor's conclusions without re-measuring at least one load-bearing claim, and `A02`:515 states
the discipline as a rule that binds itself: *"no prior phase result — this one included — may be
accepted without independent constitutional verification."*

### 6.1 The reduction chain — the spine of the whole set

| Step | From | To | Instrument | Artifact |
|---|---|---|---|---|
| 1 | 3,775 enumerated items | 281 OPEN | status fields, machine sweep | `A04` |
| 2 | 281 | 249 | 7 declaration↔projection mirror pairs removed | `A04` |
| 3 | 249 | 61 | UICM 158 → 9 patterns; RPI 30 → 1 | `A04` |
| 4 | 61 | 10 roots | independence proof | `A04` |
| 5 | 10 | **6** | `R9`/`R10` non-blocking by own register; `R2`/`R5` entailed by `ROOT-Ω` | `A05` |
| 6 | 6 | **2** | five roots are one failure at five altitudes | `A06` |
| 7 | 2 | **2** | ten attack paths; both entailment directions falsified; no common ancestor | `A07` |
| 8 | 2 | **1** *under full META-A discharge* | vacated by discharge, not by collapse | `A09` |

**`[I]` Step 8 is the only step that is conditional, and it is the most consequential.** The floor
of 2 is not falsified anywhere in the set. It is *vacated* — post-discharge the blocker set reduces
to META-B's 37 dependents, whose minimum basis is `{META-B}`, size 1. `UNK-R5-01` records that
whether discharge yields zero findings is unknowable without performing it.

### 6.2 The correction chain on one subject — act semantics

```
A13 END-STATE   : "act atomicity undefined" (K-12), classified ELIMINABLE IN-CORPUS
A01 PHASE-O     : GAP-O-02 — "constitutional act atomicity is undefined"; the question
                  "has no truth conditions"; cardinality NOT CLOSABLE
A02 PHASE-P     : reaches the same defect from the representation side — ACCEPTED unmapped
A03 PHASE-Q     : exhaustive extraction (5,663 occurrences, 81 artifacts, 23,480 lines):
                  atomicity IS located for 7 subject classes and predicated of NO act;
                  an 11-component act model exists with one passing executable;
                  the question HAS truth conditions but is not evaluable in-corpus;
                  the gap is ACT-SEMANTICS-EXTERNAL-SCOPE-GAP and is UNCLOSABLE BY AMENDMENT
```

**`[F]` Four artifacts, one subject, three corrections, and the final statement is the narrowest.**
This chain is the clearest evidence that the set's method works: the earliest and strongest claim
(*no truth conditions*) is the one that did not survive.

---

## 7 — DISCOVERY HIERARCHIES

**`[F]` The 981 canonical discoveries occupy six levels. The level of a discovery determines what
can move it.**

| Level | Population | Members | What moves it |
|---|---:|---|---|
| **L0 — ontological basis** | 2 | `META-A` (unrealized reconciliation mandate) · `META-B` (`ROOT-Ω`) | L0-A: internal work. L0-B: **nothing located** |
| **L1 — irreducible blocker basis** | 6 | `{R1, R3, R4, R6, R7, R8}` — unique size-6 generating set among all 256 subsets | discharging its generating meta-cause |
| **L2 — independent roots** | 10 | `R1`…`R10` (`A04`) | 7 internally eliminable, 2 external, 1 split |
| **L3 — normalized open items** | 61 | survivors of mirror and instance reduction | root elimination |
| **L4 — register-level open items** | 281 | OPEN across 293 JSON registers | mostly mirrors and instances of L3 |
| **L5 — enumerated items** | 3,775 | every uncertainty item in every register | recorded, not individually actionable |

**`[F]` A parallel hierarchy governs the readiness plane and does not intersect the above.**

| Level | Population | Members |
|---|---:|---|
| **RA — truly blocking under the strict rule** | 3 | `FB-1` mutation classification inoperative · `FB-2` identity plane has no lifecycle binding · `FB-3` closed capability enumeration outside the extension mechanism |
| **RB — non-blocking** | 16 | `RU-02`, `RU-04`, `RU-06`, `RU-07`, `RU-09`, `RU-12`, `RU-13`, `RU-15`, `RU-16`, `RU-18`, `G-11`, and 5 more |
| **RC — already resolved** | 4 | `RU-01`, `RU-03`, `RU-14`, `EEG-1` |
| **RD — outside readiness scope** | 6 | `RU-05`, `RU-08`, `RU-10`, `RU-19`, `RU-20`, `MP2-C-04` |
| **RE — misclassified** | 3 | `RU-11`, `RU-17`, `ISD-G-07`/`-08` |
| **RF — superseded** | 0 | *empty, and the emptiness is itself `RU-18`/`G-11`* |
| **RG — architecturally irrelevant** | 1 | stash entries |

**`[I]` The two hierarchies are disjoint and that is the most important structural fact in the
consolidation.** `A14` measures the T1 vacancy — the whole of `META-B` — as **outside foundation
readiness scope**: it caps certification standing and obstructs no admission, governance,
evolution, validation or assimilation. `A11` Q28 measures the converse: **all** of the minimum
permanent residue traces to `META-B` and **zero** members trace to `META-A`. So the corpus's
deepest constitutional blocker constrains none of its foundation capability, and its foundation
blockers constrain none of its constitutional standing. **Neither plane can discharge the other,
and no artifact in the set claims otherwise.**

---

## 8 — DISCOVERY DEPENDENCIES

**`[F]` Ten located dependency edges at corpus level (`A13` Phase 8), reproduced verbatim.**

| Edge | Statement |
|---|---|
| `D-01` | all standing → `T1` (VACANT) |
| `D-02` | `CMG-OQ-03` → `CMG-OQ-01` + `CMG-OQ-02` |
| `D-03` | `DEF-02` → external constituent authority |
| `D-04` | `UCCEP-F-004` → `CEP-006` I.4 (independent of `D-01`) |
| `D-05` | `CMG-GAP-06` → `CMG-OQ-05` |
| `D-06` | certification → `CEP-005` |
| `D-07` | evolution step (h) → `VAC-01` |
| `D-08` | completeness verification → Article L validator |
| `D-09` | trust anchor → `REG-AUTO-001`, itself unregistered |
| `D-10` | 8 unowned scopes → `CEP-002` Governance Authority, whose allocations are standing-contested |

**`[F]` Two dependency inversions are located, and both are machine-induced.**

1. **`CMG-OQ-03` ordering inversion** (`CIRC-01`, `A01`:774) — `CMG-OQ-03` is **downstream** of
   `CMG-OQ-01`/`02` in constitutional text and **blocking** in the validator. `A01`:479 states the
   determinative result: it must not resolve before `D-14`, `DEF-02` or `UCCEP-F-004`, yet it
   blocks Governance Completion, *"and only because of a validator defect."*
2. **`D-09` — the trust anchor is unregistered.** The one current, gate-enforced content anchor is
   held by `REG-AUTO-001`, which lies inside an excluded tree and is itself unregistered. `A02`:466
   states the consequence: *"the trust anchor cannot vouch for itself: its governing standard is
   excluded by its own rule."*

**`[F]` One dependency is asymmetric and was newly determined, not inherited.** `A08`:490 —
META-A's non-realization governs the **integrity of META-B's observation**; META-B's vacancy does
not expose META-A's mandate. It is a capacity relation, not an entailment, and it leaves both
members irreducible. **The entailment relation over the basis is EMPTY** (`A07`, unchanged through
`A09`).

**`[F]` Discharge-path dependencies that are declared and not connected.** `GAP-R1-03` — `R9`'s 158
gaps name five validating gates, **none wired to any entrypoint**. `A05`:296 records the discharge
path as *"declared but not connected."* `UNK-R1-04` records the consequence as unknown: whether the
188 non-blocking items would become blocking if those gates were wired.

---

## 9 — WHAT CONSOLIDATION DID NOT ACHIEVE

**`[F]` Deduplication removed 180 occurrences and zero obligations.** Every gap, unknown,
assumption, conflict and blocker that entered the analysis leaves it, except the 14 the artifacts
themselves retire in §5 — and of those 14, six are *absorbed* (the obligation moves, it does not
vanish) and five are *resolved* (the obligation is discharged with evidence).

**`[F]` Three items could not be reduced, absorbed, or referred.**

| Item | Why it stands |
|---|---|
| `META-B` / `ROOT-Ω` | 18 located clauses across ≥6 instruments; zero located transformation paths across all six tested verbs (remove, transform, absorb, supersede, discharge, bypass); `LXXXI.6` forecloses self-conferral *"by operation of any clause herein"* |
| `GAP-R5-01` | No located instrument enumerates the corpus of a meta-cause, so the completeness of any such clause set is **unverifiable by construction** — and this was demonstrated, not assumed: `A07`'s 18-clause set was under-capture by 14 |
| `GAP-R-01` / the 20 namespace clashes | No global identifier-namespace registry exists; disambiguation had to be reconstructed per artifact, and this register is the record of having done so |

**`[I]` And one negative result deserves recording because it bounds every count in this report.**
`A04` proves the uncertainty space **open by construction**: `LXXVII.1` governs unknown concepts
*"not by anticipating them"* but by a procedure applied *"for any concept presented to the
corpus."* A reactive total procedure closes **dispositions**, never **discovery**. `A04` then
demonstrated it by finding five new classes while testing whether new classes could be found.
**981 is therefore a complete count of what these fourteen artifacts contain, and not a complete
count of what exists.** `I.5` forbids declaring otherwise, and `LXXVI.5` would make the claim a
recorded defect.

---

## 10 — CONSOLIDATION TALLY

| Measure | Value |
|---|---:|
| Discovery occurrences located | 1,161 |
| Canonical discoveries | **981** |
| Exact duplicate occurrences | 180 |
| Near-duplicate pairs | 6 |
| Equivalence classes (different wording, one subject) | 17 |
| Identifiers collapsing into those classes | 96 |
| Conflicting discoveries | 35 |
| Identifier namespace clashes | 20 |
| Superseded / retired identifiers | 14 |
| Re-attributed roots | 5 |
| Corrections of cause without retirement | 11 |
| Backward correction edges between artifacts | 11 |
| Reduction-chain steps (3,775 → 2) | 8 |
| Hierarchy levels (constitutional plane) | 6 |
| Hierarchy levels (readiness plane) | 7 |
| Located dependency edges | 10 |
| Dependency inversions | 2 |
| Referenced-but-unlocated discoveries | 5 |
| **Obligations removed by consolidation** | **0** |

---

*MCRF / STREAM-00 / WP-001A · DISCOVERY CONSOLIDATION REPORT · AUTHORITY = NONE (DERIVED ANALYSIS ONLY).*
*Deduplicates; determines nothing. Valid for the fourteen artifacts as extracted, and for no later state.*
