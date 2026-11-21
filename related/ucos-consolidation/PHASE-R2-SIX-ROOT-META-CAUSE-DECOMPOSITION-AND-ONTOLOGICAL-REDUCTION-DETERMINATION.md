# PHASE R2 — SIX-ROOT META-CAUSE DECOMPOSITION AND ONTOLOGICAL REDUCTION

| Field | Value |
|---|---|
| AUTHORITY | **NONE (DERIVED TRUTH)** |
| BASELINE | `integration/recovery-001` @ `1e3e4ba9` |
| INPUT | Phase R1 basis **{R1, R3, R4, R6, R7, R8}**, size 6, unique |
| MANDATE | Search only for deeper causality. No new defects, blockers, or gaps. |
| CLASSIFICATION | `[F]` · `[I]` · `[A]` · `[GAP]` · `[UNKNOWN]` |

---

## R2.0 — CORRECTION TO PHASE R1, ISSUED FIRST

**`[F]` Phase R1 attributed R3 to `CMG-L-08` (*zero hard coding*). That attribution is WRONG, and `CMG-L-08` is exculpated.**

`[F]` Phase P reasoned: `CMG-L-08` forbids the validator from containing enumeration members, therefore it must read them from the projection, therefore it can only be as strict as the projection. `[I]` The inference is invalid, because it assumes the only alternative to reading the projection is hard-coding the constitution. **There is a third path, and the corpus mandates it:**

`[F]` `CMG-000001` **XV.5** — *"The Registry SHALL be **recomputable**. It SHALL be **regenerable from repository state alone by the validator of Article L**, and a Registry that cannot be regenerated **IS invalid**."*

`[I]` A validator that **regenerates** the projection from the text and compares the result contains **no** enumeration member — it derives both sides. **Regeneration satisfies `CMG-L-08` and reconciliation simultaneously.** `CMG-L-08` therefore does not cause R3, and R1's basis element R3 is misnamed.

`[F]` **And XV.5 is violated on its own terms.** Measured: `cmg_validate.py` contains **no regeneration path**. Its only write is the evidence file at line 725 (`--emit`); it never writes `REGISTRY_RELPATH`. **By XV.5's own test, `CMG-REGISTRY.json` IS invalid** — and the validator returns 0 findings.

`[F]` **`XV.5` is never mentioned in the validator: 0 occurrences.**

---

## R2.1 — ROOT SEMANTIC DECOMPOSITION

| | **R1** | **R3** | **R4** | **R6** | **R7** | **R8** |
|---|---|---|---|---|---|---|
| **Definition** | A corpus cannot confer on itself the standing it lacks | Projected enumerations are not compared to canonical text | `CMG-S-07 ↔ RATIFIED / FINALIZED`; 6 of 9 `CEP-006` states unmapped | Registration universe ≠ constitutional corpus | `UCKP-LAW-0001` role `SUPREME` vs `CMG` `tier: T4` | `CMG-000001` `state: DECLARED` (PRE-EFFECT) while exercising META force |
| **Trigger** | Any attempt to reach RATIFIED/FINALIZED in-corpus | Any divergence between `CMG-REGISTRY.json` and `CMG-000001` | Any use of `CEP-006` `ACCEPTED` or `FINALIZED` | Any artifact in `00-MASTER/` or `00-BOOK/CONTROL-TOWER/` | Any authority resolution crossing tier↔role | Any citation of `CMG-000001` as authority |
| **Failure mode** | **Standing unobtainable** | **Divergence undetected** | **Divergence undetected** | **Divergence undetected** | **Divergence undetected** | **Divergence undetected** |
| **Affected scope** | corpus-wide standing | 14 of 19 collections | ratification lifecycle | 21 of 44 artifacts | authority lattice | 1 artifact, 401 references |
| **Authority source** | `XLIV.7` · `CEP-000` §5.4 · `XVII.4` | `XV.5` (unimplemented) · `L.3` (no mandate) | `XXV.3` (self-mandated amendment) | `LX.2` (unenforced) | **none — no mapping declared** | `XXVII.5` (unenforced) |
| **Dependency source** | out-of-corpus authority | `cmg_validate.py` | `CMG-000001` text | `00-BOOK/tools/config.py:885` | `engine/uckp/law.py:41` | `CMG-REGISTRY.json` field |
| **Preconditions** | an exogenous constituent act | a regeneration or comparison path | an amendment | a universe reconciliation | a tier↔role mapping | a record correction |
| **Violation type** | **INCOMPLETENESS** | **UNSOUNDNESS** | **UNSOUNDNESS** | **UNSOUNDNESS** | **UNSOUNDNESS** | **UNSOUNDNESS** |
| **Blocking mechanism** | `LXXX.4` ceiling; `CMG-L-12` | gate returns 0 findings over a divergent state | mapping cannot express `ACCEPTED` | drift gate cannot see 48 % of the corpus | `CAA-INV-01` passes over a contradiction | `XXVII.3` requires a block that is not raised |

`[I]` **The Violation-type row is the result of this Phase.** Five roots produce **unsoundness** — the machine affirms what the constitution denies. One produces **incompleteness** — the constitution cannot obtain what it requires. These are categorially different failures.

---

## R2.2 — FAILURE-MODE NORMALIZATION

**`[F]` Five of six roots express one underlying failure: an unverified correspondence between two representations of the same constitutional fact.**

| Root | Representation A | Representation B | Correspondence rule | Verified? |
|---|---|---|---|---|
| R3 | `CMG-000001` text | `CMG-REGISTRY.json` | **II.4** *"Where the derived form and the canonical form disagree, the canonical form governs and the derived form SHALL be regenerated"* · **XV.3** *"Where the projection and an input disagree, the input governs"* · **XV.5** regenerable | **NO** |
| R4 | `CMG` states XXV.1 | `CEP-006` states VI.1 | **XXV.3** *"Where the located model and this mapping disagree, the located model governs and this mapping SHALL be corrected by amendment"* | **NO** |
| R6 | constitutional corpus (44) | registration universe (1,579) | **LX.2** *"Generated output IS derived truth and SHALL be reconciled against its constitutional input; where they disagree, the input governs"* | **NO** |
| R7 | `CMG` tiers T0–T5 | `UCKP` roles SUPREME/PROJECTION/ORTHOGONAL/PERSISTENCE | **none declared** (`GAP-P-03`) | **NO — no rule exists** |
| R8 | `LXXXI.6` standing *"IS PROVISIONAL"* | `CMG-REGISTRY` `state: DECLARED` | **XXVII.5** *"resolved from the artifact's declaration **reconciled against the located registries**, and irreconcilable inputs produce a finding rather than a guess"* | **NO** |
| **R1** | — | — | **not a correspondence failure** | n/a |

### `[F]` The corpus declares the reconciliation rule EIGHT times

| Article | Clause | Mentioned in `cmg_validate.py`? |
|---|---|---|
| **II.4** | derived vs canonical → canonical governs, derived regenerated | mentioned 3×, **cited as a clause 0×** |
| **XII.6** | *"Derived truth SHALL always be reconciled against repository reality"* | cited — but for the `AUTHORITY = NONE` string only |
| **XV.3** | projection vs input → input governs | cited — but for `check_source_binding` only |
| **XV.5** | Registry regenerable, else **invalid** | **0 occurrences** |
| **XXV.3** | located model governs; mapping corrected by amendment | **0 occurrences** |
| **XXVII.5** | declaration reconciled against registries; irreconcilable → finding | **0 occurrences** |
| **LX.2** | generated reconciled against constitutional input | **0 occurrences** |
| **LXXIV.6** | restored derived store disagreeing with sources IS a **drift defect** | **0 occurrences** |

`[F]` **Six of the eight are never mentioned in the validator at all.**

### `[F]` And Article L.3 — the validator's exhaustive mandate — contains no reconciliation clause

```
L.3(a) conformance map → present Article        L.3(g) INV-05 topological sort
L.3(b) identifier families used as declared     L.3(h) INV-06 rank or orthogonality
L.3(c) Registry entries → present home          L.3(i) INV-07 states/transitions
L.3(d) INV-02 injective concern→owner           L.3(j) INV-08 identifier injectivity
L.3(e) INV-03 total concern↔owner               L.3(k) INV-11 lineage resolves
L.3(f) INV-04 superiors resolve                 L.3(l) exit non-zero on any finding
```

`[I]` **Twelve sub-clauses. Not one requires comparing projected content to canonical text.** The obligation is declared in eight Articles and mandated in none.

---

## R2.3 — META-CAUSE SEARCH

`[F]` All 15 unordered pairs tested. `[F]` **No root derives from another root** — Phase R1 already proved the entailment relation over the basis is empty. `[I]` The search therefore had to be for a **common cause above** the roots, not a derivation between them.

| Pair | Common cause located? | Evidence |
|---|---|---|
| {R3, R4} | **YES — META-A** | R3's rule is II.4/XV.3/XV.5; R4's is XXV.3. Both are *"where X and Y disagree, X governs"* with no check. |
| {R3, R6} | **YES — META-A** | R6's rule is LX.2, same form, same absence. |
| {R3, R7} | **YES — META-A** (degenerate case) | R7 has **no** declared correspondence rule — the limiting case of an unverified mapping is an undeclared one. |
| {R3, R8} | **YES — META-A** | R8's rule is XXVII.5, which *explicitly* demands a finding on irreconcilable inputs; none is produced. |
| {R4, R6}, {R4, R7}, {R4, R8}, {R6, R7}, {R6, R8}, {R7, R8} | **YES — META-A** | all five are correspondence pairs with an unenforced or absent rule |
| {R1, R3}, {R1, R4}, {R1, R6}, {R1, R7}, {R1, R8} | **NO common cause** | R1 involves **no pair of representations**. Its failure is that a required standing cannot be **received**, not that two records disagree. |

`[F]` **Result: 5 roots share one common cause; the sixth shares none with any.**

---

## R2.4 — ONTOLOGICAL REDUCTION

### 6 → 5 · 6 → 4 · 6 → 3 · 6 → 2 — **`[F]` ALL SUCCEED, in one step**

**`[I]` META-A — THE UNMANDATED RECONCILIATION.**
> The corpus declares, in at least eight Articles, that a derived representation disagreeing with its source is governed by the source and must be regenerated or corrected. `XV.5` makes regenerability the validity condition of the Registry itself. **Article L.3 — the exhaustive mandate of the only meta-constitutional validator — contains no clause requiring any such comparison, and six of the eight Articles are never mentioned in the validator.**

`[F]` **META-A generates R3, R4, R6, R7, R8.** Each is one instance: R3 the general projection, R4 the lifecycle mapping, R6 the universe mapping, R7 the tier↔role mapping (undeclared), R8 the standing↔state mapping.

**`[I]` META-B — `ROOT-Ω`.**
> A corpus cannot confer on itself the standing it lacks. Min proof set `{XLIV.7, CEP-000 §5.4, XVII.4}`; disjoint second proof at `AUTH-03/04/06` + `Ω-010` + `CM-007`.

`[F]` **META-B generates R1.**

### 2 → 1 — **`[F]` FAILS. Proof:**

1. `[F]` META-A's failure mode is **unsoundness**: a gate affirms a state the constitution denies. Demonstrated — `cmg-gate.sh` exits 0 while `XXVII.3` requires certification blocked (`CE-01`).
2. `[F]` META-B's failure mode is **incompleteness**: a required standing cannot be derived. Demonstrated — *"a **missing seed**, not a **contradiction**"* (`UCOS-Ω∞-CONSTITUENT-AUTHORITY-DETERMINATION-REPORT` §8).
3. `[I]` **Counterfactual A→B:** implement every reconciliation the corpus declares. Tier T1 remains `VACANT`; `XLIV.7` still forbids self-conferral. **META-B survives.**
4. `[I]` **Counterfactual B→A:** an external authority occupies T1 and confers finality on everything. `cmg_validate.py` still contains no regeneration path; `XV.5` is still unimplemented; the 14 unbound collections are still unbound. **META-A survives.**
5. `[I]` A verification failure and a derivation failure have no common cause: the first is about **representing what exists**, the second about **obtaining what does not**. ∎

**`[F]` FLOOR = 2.**

---

## R2.5 — CONSTITUTIONAL FAILURE TAXONOMY

`[F]` Derived from the corpus's own class vocabulary — **148 distinct located failure classes** extracted from 904 JSON registers. No category is invented here.

### Category 1 — **DIVERGENCE / DRIFT** (the corpus has **nine** names for it)

```
REGISTRY-DRIFT (9)                          STANDING-LEDGER-DIVERGENCE (2)
REPOSITORY-DRIFT (1)                        STANDING-RESOLUTION-DIVERGENCE (2)
REGISTRATION DRIFT — CERTIFICATION REGRESSION (1)   STANDING-REGISTER-DIVERGENCE (2)
CONSTITUTIONAL COMPLIANCE — STALE DETERMINATION (1) DISCLOSED-PINNED-PARAMETER-DIVERGENCE (2)
MERGE / DIVERGENCE RISK (1)
```
`[I]` **Nine located class names for one failure, and zero checks for it.** `[I]` The taxonomy's redundancy is itself evidence: the corpus recognised the failure repeatedly, named it each time it recurred, and never generalised it into a rule the validator enforces.

### Category 2 — **STANDING / EXTERNAL** (the corpus has **eight** names for it)

```
STANDING-CONSTITUTIONAL-CEILING (5)    STRUCTURAL-EXTERNAL (8)
STANDING-CONSTITUTIONAL-CONFLICT (2)   DEFECT-EXTERNAL (1)
MECHANISM-ABSENT (2)                   HISTORICAL-EXTERNAL (1)
EXTERNAL (1)                           STANDING-EXTERNAL (1)
```

**`[F]` Smallest set of failure categories required to generate all six roots: TWO — `DIVERGENCE/DRIFT` and `STANDING/EXTERNAL`. Both are named by the corpus; neither is authored here.**

`[I]` Every other located class (`UNSATISFIED-REQUIREMENT`, `ABSENT-OBLIGATION`, `MEASURED-GOVERNANCE-GAP`, `MISSING OWNER`, `MISSING VALIDATION`, …) attaches to R9/R10 — the **non-blocking** roots — or to programme-local measurement, not to the basis.

---

## R2.6 — ROOT GENERATION MODEL

| Root | Model | Evidence |
|---|---|---|
| **R1** | **INDEPENDENT** *(= META-B itself)* | Not generated by anything located; doubly proved from disjoint clause sets |
| **R3** | **GENERATED** by META-A | The general case: `XV.5` unimplemented, `L.3` silent |
| **R4** | **MANIFESTED** from META-A | A specific mapping (XXV.3) whose own conflict rule is unenforced |
| **R6** | **PROJECTED** from META-A | A universe boundary (`EXCLUDE_DIR_PREFIXES`) never reconciled against `LX.2` |
| **R7** | **INHERITED** from META-A | The degenerate case — the correspondence rule was never declared at all |
| **R8** | **DERIVED** from META-A | A field value diverging from `LXXXI.6`, with `XXVII.5` demanding a finding that is never raised |

`[I]` **Only R1 is independent. The other five are the same failure at five altitudes** — general projection, lifecycle mapping, universe mapping, vocabulary mapping, field value.

---

## R2.7 — MINIMUM ONTOLOGICAL BASIS

**`[F]` The six-root basis CAN be reduced. Smallest generating basis: { META-A, META-B }, size 2.**

### Proof of irreducibility at 2

- `[F]` **Generation:** META-A ⟹ {R3, R4, R6, R7, R8} (§R2.3, all five with located correspondence rules). META-B ⟹ {R1}. Union = the full basis. ✔
- `[I]` **Non-redundancy:** neither generates the other (§R2.4 counterfactuals 3 and 4). ✔
- `[I]` **No smaller basis:** a size-1 basis would require one cause generating both an unsoundness and an incompleteness. `[F]` Phase O established these are of opposite logical character — *"a missing seed, not a contradiction"* for META-B; `[F]` Phase P established a live unsoundness for META-A (`CE-01`). ∎

`[GAP]` **`GAP-R2-01` — the corpus contains no clause classifying its own defects by logical type.** The unsoundness/incompleteness distinction is derived here from located failure modes, not read from a located taxonomy.

---

## R2.8 — TERMINAL DETERMINATION

| # | Question | Answer |
|---|---|---|
| **1** | **Are the six roots fundamental?** | **`[F]` NO.** Five of six are manifestations of one cause. Only R1 is fundamental. |
| **2** | **Are any roots manifestations of deeper causes?** | **`[F]` YES — five.** R3 (generated), R4 (manifested), R6 (projected), R7 (inherited), R8 (derived) all instantiate **META-A**. |
| **3** | **Smallest constitutional failure basis** | **`[F]` TWO categories, both located in the corpus's own vocabulary: `DIVERGENCE/DRIFT` (9 class names) and `STANDING/EXTERNAL` (8 class names).** |
| **4** | **Smallest ontological failure basis** | **`[F]` { META-A, META-B }, size 2.** META-A = the reconciliation rule declared in 8 Articles and mandated in none. META-B = `ROOT-Ω`. |
| **5** | **Can all remaining blockers be generated from a smaller set?** | **`[F]` YES — 6 → 2.** All 100 live blocking dependents: **63 from META-A**, **37 from META-B**. |
| **6** | **Is `ROOT-Ω` truly fundamental?** | **`[F]` YES.** Doubly proved from disjoint clause sets — `{XLIV.7, CEP-000 §5.4, XVII.4}` and `{AUTH-03/04/06, Ω-010, CM-007}` — proved exactly minimal in Phase P §P7, and it survives every counterfactual in which META-A is fully resolved. `[I]` It is the **only** fundamental root in the repository. |
| **7** | **Deepest located cause** | **`[F]` `CMG-000001` XV.5** — *"The Registry SHALL be recomputable. It SHALL be **regenerable from repository state alone by the validator of Article L**, and a Registry that cannot be regenerated **IS invalid**."* `[F]` `cmg_validate.py` has **no regeneration path**; `XV.5` has **0 occurrences** in it; `L.3(a)–(l)` never mandates it. `[I]` **This one clause, unimplemented, is the deepest located cause of META-A — and by its own terms the Registry is already invalid.** For META-B the deepest located cause is `XLIV.7`. |

---

## CLASSIFIED RESIDUE

### FACTS `[F]`
1. `cmg_validate.py` contains **no regeneration path**; its only write is the `--emit` evidence file (line 725). It never writes `REGISTRY_RELPATH`.
2. `XV.5` — the clause making regenerability the Registry's **validity condition** — has **0 occurrences** in the validator.
3. `L.3(a)–(l)` enumerates 12 validator duties; **none** compares projected content to canonical text.
4. The reconciliation rule is declared in **8 Articles** (II.4, XII.6, XV.3, XV.5, XXV.3, XXVII.5, LX.2, LXXIV.6); **6 are never mentioned** in the validator.
5. The corpus carries **9 distinct located class names** for divergence/drift and **8** for standing/external, from a vocabulary of **148** located failure classes.
6. R7 is the degenerate case: **no** tier↔role correspondence rule is declared anywhere (`GAP-P-03`).
7. `XXVII.5` explicitly requires *"a finding rather than a guess"* on irreconcilable inputs; four vocabularies disagree about `CMG-000001`'s state and no finding is raised.
8. Regeneration satisfies `CMG-L-08` and reconciliation simultaneously — a validator that derives both sides holds no enumeration member.

### INFERENCES `[I]`
1. Phase R1's attribution of R3 to `CMG-L-08` is **wrong**; `CMG-L-08` is exculpated and the true cause is `XV.5` unimplemented.
2. Five roots are one failure at five altitudes: general projection, lifecycle mapping, universe mapping, vocabulary mapping, field value.
3. META-A yields **unsoundness**; META-B yields **incompleteness**; the two cannot merge.
4. The ontological floor is **2**, proved by two-way counterfactual.
5. The taxonomy's redundancy is diagnostic: nine names for one failure indicates repeated recognition without generalisation.
6. `ROOT-Ω` is the only fundamental root in the repository.
7. By `XV.5`'s own test, `CMG-REGISTRY.json` **IS invalid** — and the gate reports 0 findings over it.

### ASSUMPTIONS `[A]`
`A-R2-01` The 8 reconciliation clauses are the complete set in `CMG-000001`; located by pattern search over its 2,000+ lines, not by exhaustive clause-by-clause reading.
`A-R2-02` The generation relation META-A ⟹ {R3,R4,R6,R7,R8} rests on each root having a located correspondence rule; R7's membership rests on the *absence* of a rule being the degenerate case.
`A-R2-03` The unsoundness/incompleteness distinction is derived from located failure modes, not from a located taxonomy (`GAP-R2-01`).
`A-R2-04` Dependent counts are inherited from Phases R0/R1 and were not re-derived.
`A-R2-05` Measured at `1e3e4ba9` in this environment.

### GAPS `[GAP]`
| Id | Gap |
|---|---|
| `GAP-R2-01` | No located clause classifies constitutional defects by logical type (unsoundness vs incompleteness) |
| `GAP-R2-02` | `XV.5` declares a validity condition for the Registry that no gate evaluates; the condition is currently unmet and unreported |
| `GAP-R2-03` | The corpus has 9 class names for divergence and no generalised divergence rule |
| `GAP-R2-04` | `L.3` is an exhaustive mandate that omits the obligation 8 other Articles impose |

### UNKNOWNS `[UNKNOWN]`
`UNK-R2-01` Whether further reconciliation clauses exist outside `CMG-000001` that would widen META-A's declared basis.
`UNK-R2-02` Whether `XV.5`'s omission from `L.3` is a drafting oversight or a deliberate scope limit — no located record states either.
`UNK-R2-03` Whether any of the 148 located failure classes names a third meta-cause not represented in the basis.
`UNK-R2-04` Whether R7's undeclared mapping is an omission or a deliberate refusal to rank two vocabularies.

---

## PHASE R2 TERMINAL VERDICT

> **DETERMINATION-COMPLETE · SIX-ROOT BASIS NOT FUNDAMENTAL · ONTOLOGICAL BASIS = 2 · FLOOR PROVED AT 2 · ONE FUNDAMENTAL ROOT IN THE REPOSITORY**

**`[F]` Five of the six roots are one failure wearing five costumes.** R3 is the general projection, R4 the lifecycle mapping, R6 the universe mapping, R7 the vocabulary mapping, R8 a single field value. Each is a correspondence between two representations of one constitutional fact, and in each the correspondence rule is either **declared and unenforced** or **never declared**.

**`[F]` The corpus declares that rule eight times and mandates it zero times.** `II.4`, `XII.6`, `XV.3`, `XV.5`, `XXV.3`, `XXVII.5`, `LX.2`, `LXXIV.6` all say some version of *"where the derived form and the source disagree, the source governs."* `L.3(a)–(l)` — the exhaustive mandate of the only meta-constitutional validator — requires **none** of them, and six of the eight appear nowhere in its code. **META-A is not a missing rule. It is a rule declared to redundancy and realized nowhere.**

**`[I]` And Phase R1 blamed the wrong clause.** `CMG-L-08` (*zero hard coding*) was charged with forcing the validator to be no stricter than its projection. The charge assumed the only alternative was hard-coding the constitution. `XV.5` names a third path — **regeneration** — which holds no enumeration member and therefore satisfies `CMG-L-08` and reconciliation at once. `CMG-L-08` is exculpated; **`XV.5`, unimplemented, is the deepest located cause.**

**`[F]` By `XV.5`'s own words the Registry is already invalid.** *"A Registry that cannot be regenerated **IS invalid**."* `cmg_validate.py` has no regeneration path and never mentions `XV.5`. The gate reports **0 findings** over a Registry its own constitution classifies as invalid — which is `META-A` demonstrating itself on the very clause that defines it.

**`[I]` The floor is two, and the two cannot merge.** META-A produces **unsoundness** — the machine affirms what the constitution denies. META-B (`ROOT-Ω`) produces **incompleteness** — the constitution cannot obtain what it requires. Resolve every reconciliation and T1 is still vacant; occupy T1 and the projections are still unverified. A verification failure and a derivation failure have no common cause: one is about representing what exists, the other about obtaining what does not.

**`[I]` `ROOT-Ω` is the only fundamental root in this repository.** Everything else reduces. It is doubly proved from disjoint clause sets, exactly minimal, survives every counterfactual, and is bounded by the corpus's own honest phrase — *a missing seed, not a contradiction*.

**`[I]` The most telling evidence is lexical.** The corpus holds **nine distinct class names** for divergence — `REGISTRY-DRIFT`, `REPOSITORY-DRIFT`, `STANDING-LEDGER-DIVERGENCE`, `STANDING-REGISTER-DIVERGENCE`, `STANDING-RESOLUTION-DIVERGENCE`, and four more — out of 148 located failure classes. **It recognised the same failure nine times, named it nine times, and generalised it into an enforced rule zero times.** That is META-A stated in the corpus's own vocabulary, without a word of interpretation added.

**This determination decomposes, reduces and proves. It recommends nothing, designs nothing, amends nothing, and eliminates nothing.**

---

*PHASE R2 · AUTHORITY = NONE (DERIVED TRUTH) · Reports; determines nothing.*
*`CERTIFIED-PROVISIONAL`; Tier T1 VACANT; `CMG-L-12` applies to every statement herein.*


---

# PHASE R2 ADDENDUM — VERIFICATION RE-EXECUTION, CORRECTIONS, AND DEEPER LOCUS

| Field | Value |
|---|---|
| AUTHORITY | **NONE (DERIVED TRUTH)** |
| BASELINE | `integration/recovery-001` @ `1e3e4ba9` — **re-confirmed**, `git rev-parse` matches |
| MANDATE | Re-execute every load-bearing measurement of Phase R2. Correct what fails. Search only for deeper causality. |
| RESULT | **Basis unchanged at 2. Floor unchanged at 2. Deepest located cause CORRECTED — it is deeper than `XV.5`.** |

---

## A.1 — MEASUREMENTS RE-EXECUTED AND CONFIRMED

`[F]` Every measurement below was re-run at `1e3e4ba9` and reproduced.

| # | Claim | Re-measured | Verdict |
|---|---|---|---|
| 1 | `XV.5` verbatim at canonical line 460 | *"SHALL be **recomputable** … regenerable from repository state alone by the validator of Article L, and a Registry that cannot be regenerated IS invalid"* | ✔ |
| 2 | `XV.5` has 0 occurrences in the validator | `grep -c` = **0** | ✔ |
| 3 | No regeneration path | `regenerat*` = **0**; `REGISTRY_RELPATH` appears 3× (lines 36, 85, 87) — **all reads**; only write is line 725 `--emit` evidence | ✔ |
| 4 | `L.3` = exactly (a)–(l), 12 sub-clauses, none compares projection to text | canonical lines 1170–1183 read in full | ✔ |
| 5 | **14 of 19** registry collections not bound to canonical text | independently reproduced: 19 list collections; **5 text-bound** (`identifier_families`, `closed_enumerations`, `conformance_map`, `closing_articles`, `namespaces`) → **14 unbound** | ✔ **exact** |
| 6 | R4 — `XXV.3` `CMG-S-07 ↔ RATIFIED / FINALIZED`, conflict rule mandates amendment | canonical line 671, verbatim | ✔ |
| 7 | R6 — `EXCLUDE_DIR_PREFIXES` at `00-BOOK/tools/config.py:885`, excludes `00-MASTER/` and `00-BOOK/CONTROL-TOWER/` | both prefixes present in the tuple | ✔ |
| 8 | R7 — `UCKP-LAW-0001` role `SUPREME`, *"its authority derives from itself"* (`alignment.py:152-153`) vs registry `tier: T4`, `superiors: ["VAC-01"]`, `state: PROVISIONAL` | both located | ✔ |
| 9 | R8 — `CMG-000001` `state: DECLARED` vs `LXXXI.6` *"Its standing IS PROVISIONAL"* | registry: **the only `DECLARED` of 44 artifacts** (32 `PROVISIONAL`, 11 `FROZEN`); `LXXXI.6` at line 1834 | ✔ **strengthened** |
| 10 | Gate reports 0 findings over this state | `cmg_validate.py` → `findings: 0`, `EXIT=0`, `readiness outcome: READY-PROVISIONAL` | ✔ |
| 11 | 9 divergence + 8 standing/external class names are located, not authored | all 13 strings located in non-`.git` JSON registers | ✔ |

---

## A.2 — CORRECTION 1: THE `II.4` MENTION COUNT WAS A SUBSTRING ARTIFACT

`[F]` R2.2's table recorded `II.4` as *"mentioned 3×, cited as a clause 0×"*. **The 3 hits are false positives.** Anchored re-measurement locates them as `XII.4` (line 247, `"XII.1-XII.4"`) and `XVII.4` (lines 341, 345) — `II.4` is a substring of both.

`[F]` **Corrected reconciliation-clause measurement — genuine occurrences in `cmg_validate.py`:**

```
II.4      0        XXV.3     0
XII.6     2        XXVII.5   0
XV.3      2        LX.2      0
XV.5      0        LXXIV.6   0
```

`[I]` **6 of the 8 clauses have zero genuine occurrences; only `XII.6` and `XV.3` are cited at all.** R2's residue `[F]` 4 (*"6 are never mentioned"*) is **correct as stated**; only the R2.2 table row for `II.4` was wrong, and the correction **strengthens** META-A rather than weakening it.

---

## A.3 — CORRECTION 2: META-A IS **MANDATED**, NOT UNMANDATED — AND THE MANDATE IS SELF-CERTIFYING

**`[F]` R2's framing — *"a rule declared in 8 Articles and mandated in none"* — is imprecise. The reconciliation obligation IS mandated, at invariant rank, inside the closed criteria set.**

`[F]` `XI.10` — **`CMG-INV-10` — Evidence reproducibility.**
> *"Every assertion of this instrument is **recomputable from repository state** by the validator of Article L. **Verification: validator exit status zero with zero findings.**"*

`[F]` `XI.1` — **`CMG-INV-01` — Recognition totality.**
> *"Every artifact exercising constitutional force IS recognized in the Constitution Registry. Verification: **registry membership equals the set of artifacts cited as constitutional authority anywhere in the corpus**."*

`[F]` `L.2` — *"The criteria SHALL be `CMG-INV-01` through `CMG-INV-12` **and nothing else**."*
`[F]` `XLIX.5` — meta-constitutional compliance *"IS realized by the validator of Article L."*
`[F]` `XI.13` — the invariant set **IS CLOSED**, *"the immutable ground against which every other part of this instrument is checked."*

### `[F]` Measured coverage of the closed criteria set

| Invariant | Occurrences in `cmg_validate.py` | `L.3` sub-clause |
|---|---:|---|
| `CMG-INV-01` **Recognition totality** | **0** | **none** |
| `CMG-INV-02` | 3 | (d) |
| `CMG-INV-03` | 5 | (e) |
| `CMG-INV-04` | 2 | (f) |
| `CMG-INV-05` | 3 | (g) |
| `CMG-INV-06` | 3 | (h) |
| `CMG-INV-07` | 3 | (i) |
| `CMG-INV-08` | 3 | (j) |
| `CMG-INV-09` | 5 | **none** (implemented anyway) |
| `CMG-INV-10` **Evidence reproducibility** | **0** | **none** |
| `CMG-INV-11` | 2 | (k) |
| `CMG-INV-12` | 2 | **none** (implemented anyway) |

`[F]` **`L.3` names sub-clauses for 8 of the 12 invariants. The validator implements 10. The two it does not implement are exactly `CMG-INV-01` and `CMG-INV-10` — the only two whose verification conditions require comparing the corpus to the projection.**

`[F]` **The validator performs no corpus walk** — no `os.walk`, no `rglob`, no `glob(`. `check_homes` verifies each registry entry resolves to a present file; **the converse direction `CMG-INV-01` requires — every artifact cited as authority is registered — is never evaluated.** `[I]` This is R6 at invariant rank.

`[F]` **`verify.sh:410` runs the stage under the label *"meta-constitutional conformance (CMG-INV-01..12)"***, and its comment asserts *"the criteria are `CMG-INV-01..12` and nothing else, evaluated by the validator Article L.3 names as its realization."* `[I]` **The gate's label claims 12; the realization covers 10.**

### `[I]` The circularity — this is the deeper cause

`CMG-INV-10` requires every assertion to be recomputable from repository state. **Its declared verification condition is `"validator exit status zero with zero findings"`.** The validator exits zero. It exits zero *without ever recomputing anything*. `[I]` **The invariant that mandates reconciliation is verified by the exit status of the program that omits it.** The omission is therefore not merely unmandated — it is **self-certifying**: the check that would detect it is the check that is missing, and the constitution defines the missing check's own success as proof that it ran.

`[I]` `XV.5` is the **Registry-scoped restatement** of `CMG-INV-10`. It is a consequence, not the origin. `XV.5` at least states a falsifiable condition (*"a Registry that cannot be regenerated IS invalid"*); `XI.10` states a **circular** one. **The circular clause is the deeper cause.**

---

## A.4 — DEEPER CAUSALITY LOCATED: META-A OPERATING ON THE CLOSURE APPARATUS

`[F]` `check_closed_enumerations` (validator lines 536–554) verifies exactly three things: that a `closing_invariant` is recorded, that the cited invariant string **occurs in the canonical text**, and that a `reason` is recorded. **It never verifies that the closed enumeration is itself projected.**

`[F]` Measured — `closed_enumerations` names four enumerations; **three name collections absent from the Registry:**

```
identifier_families            present in registry : True
invariants                     present in registry : False
lifecycle_phases               present in registry : False
unknown_concept_dispositions   present in registry : False
```

`[I]` The Registry declares the invariant set CLOSED while **not projecting the invariant set at all** — `CMG-INV-01` appears in `CMG-REGISTRY.json` only inside the text of `CMG-OQ-07`. `[I]` **META-A is operating on the apparatus that `XI.13` calls *"the immutable ground against which every other part of this instrument is checked."*** This is not a new defect; it is the same unverified correspondence, located one level beneath the five roots — on the ground itself.

---

## A.5 — EFFECT ON THE PHASE R2 DETERMINATION

| R2 result | Status after re-execution |
|---|---|
| Six roots are not fundamental | **`[F]` UNCHANGED** |
| Five roots manifest one cause (META-A) | **`[F]` UNCHANGED — strengthened.** R6 now folds via `CMG-INV-01`, R3 via `CMG-INV-10`; both at invariant rank rather than by inference |
| Ontological basis = `{META-A, META-B}`, size 2 | **`[F]` UNCHANGED** |
| Floor = 2, unsoundness ≠ incompleteness | **`[F]` UNCHANGED** — both counterfactuals re-tested and hold |
| `ROOT-Ω` is the only fundamental root | **`[F]` UNCHANGED** |
| Smallest constitutional failure basis = 2 located categories | **`[F]` UNCHANGED** — all 13 class names re-located |
| `CMG-L-08` exculpated; `XV.5` is the deepest located cause | **`[F]` FIRST HALF UNCHANGED · SECOND HALF CORRECTED** |

### `[F]` CORRECTED ANSWER TO R2.8 Q7 — DEEPEST LOCATED CAUSE

> **`CMG-000001` `XI.10` (`CMG-INV-10` — Evidence reproducibility), whose declared verification condition is *"validator exit status zero with zero findings."***

`[F]` Supporting chain, every link located and measured:
1. `XI.10` mandates recomputability of **every assertion** of the instrument.
2. `L.2` closes the criteria set to `CMG-INV-01…12` **"and nothing else"**; `XI.13` makes that set immutable ground; `XLIX.5` routes the whole evaluation to the Article L validator.
3. `L.3(a)–(l)` provides realization sub-clauses for **8** invariants and **none** for `CMG-INV-01` or `CMG-INV-10`.
4. `cmg_validate.py` contains **0** occurrences of either, and performs **no corpus walk** and **no regeneration**.
5. `XI.10`'s verification condition is satisfied — `findings: 0`, `EXIT=0` — **by the very program that omits it**.
6. `XV.5` restates the same obligation for the Registry and is likewise unimplemented, making the Registry **invalid by its own terms** while the gate reports zero findings.

`[I]` **`XV.5` is where the failure becomes falsifiable. `XI.10` is where it becomes invisible.** For META-B the deepest located cause is unchanged: `XLIV.7`.

---

## ADDENDUM CLASSIFIED RESIDUE

### FACTS `[F]`
1. `CMG-INV-01` and `CMG-INV-10` have **0 occurrences** in `cmg_validate.py`; the other ten invariants are all present.
2. `L.3` provides realization sub-clauses for 8 of 12 invariants; `CMG-INV-01`, `-09`, `-10`, `-12` have none. The validator implements `-09` and `-12` regardless, and not `-01` or `-10`.
3. `CMG-INV-10`'s declared verification condition is the validator's own exit status — measured `findings: 0`, `EXIT=0`.
4. The validator performs no `os.walk`, `rglob`, or `glob(`; `CMG-INV-01`'s converse direction is never evaluated.
5. `verify.sh:410` labels the stage `CMG-INV-01..12` while the realization covers 10 of 12.
6. 19 registry collections; **5** text-bound, **14** not — reproducing Phase P exactly.
7. `II.4` has **0** genuine occurrences in the validator; R2.2's "3×" were `XII.4` / `XVII.4` substring matches. 6 of 8 reconciliation clauses are absent, as R2's residue stated.
8. 3 of 4 `closed_enumerations` (`invariants`, `lifecycle_phases`, `unknown_concept_dispositions`) name collections absent from the Registry; `check_closed_enumerations` passes.
9. `CMG-000001` is the **sole `DECLARED` artifact** among 44 (32 `PROVISIONAL`, 11 `FROZEN`) while `LXXXI.6` states its standing **IS PROVISIONAL**.
10. Baseline re-confirmed: `1e3e4ba92c121ae3111637d4afbbfd258a5d4896`; the six phase determinations are untracked working-tree files.

### INFERENCES `[I]`
1. META-A is **mandated at invariant rank** (`XI.1`, `XI.10`) inside a **closed** criteria set — not merely declared in prose. R2's "mandated in none" understated the constitutional force of the obligation.
2. The omission is **self-certifying**: `CMG-INV-10` defines its own verification as the exit status of the program that omits it.
3. `XV.5` is the Registry-scoped consequence of `XI.10`, not the origin; the deepest cause is the circular clause, not the falsifiable one.
4. R6 reduces to META-A through `CMG-INV-01` directly, tightening R2.6's classification of R6 from *projected* to *invariant-rank unimplemented*.
5. META-A is demonstrable on the invariant apparatus itself — the ground `XI.13` calls immutable is closed but unprojected.
6. Every R2 conclusion about basis, floor, generation and fundamentality survives; only the deepest-locus answer moves.

### ASSUMPTIONS `[A]`
`A-R2-06` Invariant coverage is measured by identifier occurrence in the validator plus reading each check's body; a check enforcing an invariant without naming it would be missed.
`A-R2-07` Text-binding is measured by whether a collection is accessed inside a function receiving the canonical text or parsed articles; a binding performed indirectly would be missed.
`A-R2-08` `A-R2-01` (the 8 reconciliation clauses are complete) is **not** discharged by this addendum; `XI.1` and `XI.10` are additions to that set, so the set was demonstrably incomplete.

### GAPS `[GAP]`
| Id | Gap |
|---|---|
| `GAP-R2-05` | `CMG-INV-10`'s verification condition is circular — satisfied by the exit status of the validator that omits it. No located clause detects a self-certifying verification condition. |
| `GAP-R2-06` | `L.3` provides no realization sub-clause for `CMG-INV-01`, `-09`, `-10`, `-12`, while `L.2` declares the criteria set exhaustive at 12. |
| `GAP-R2-07` | `closed_enumerations` closes three enumerations that the Registry does not project, and `CMG-INV-09`'s check cannot detect it. |

### UNKNOWNS `[UNKNOWN]`
`UNK-R2-05` Whether `CMG-INV-01`/`-10`'s omission from `L.3` is deliberate scope limitation or drafting omission — no located record states either.
`UNK-R2-06` Whether `CMG-INV-10`'s circular verification condition was intended as a shorthand for "the validator recomputes everything" or as the literal test it reads as.
`UNK-R2-07` How many further invariant-rank obligations lack an `L.3` realization clause beyond the four measured here — bounded at 4 for `CMG-INV-*`, unbounded for `CMG-L-01…14`, which `XLIX.5` also routes to the Article L validator and which were not measured.

---

## ADDENDUM TERMINAL VERDICT

> **VERIFICATION-COMPLETE · ALL R2 STRUCTURAL RESULTS HOLD · ONTOLOGICAL BASIS = 2, UNCHANGED · DEEPEST LOCATED CAUSE CORRECTED FROM `XV.5` TO `XI.10` (`CMG-INV-10`) · META-A IS MANDATED AT INVARIANT RANK AND SELF-CERTIFYING**

**`[F]` Phase R2's reduction survives re-execution intact.** Six roots are not fundamental; five manifest META-A; one (`ROOT-Ω`) is fundamental; the floor is two and the two cannot merge. Every counterfactual was re-tested and every structural claim reproduced, including Phase P's 14-of-19 measurement, which this addendum derives independently and matches exactly.

**`[I]` But R2 located META-A one level too high.** It reported an obligation *"declared in eight Articles and mandated in none."* The obligation is in fact mandated at **invariant rank**, inside a set `L.2` declares exhaustive and `XI.13` declares immutable: `CMG-INV-01` requires registry membership to equal the set of artifacts cited as authority anywhere in the corpus, and `CMG-INV-10` requires every assertion to be recomputable from repository state. **Both have zero occurrences in the validator. They are the only two of the twelve that do.**

**`[F]` And they are the only two whose verification requires comparing the corpus to its projection.** The validator implements ten invariants, including two (`-09`, `-12`) that `L.3` never mandates. It omits exactly the two that would look outward from the projection to the corpus. `L.3` names realization clauses for eight and is silent on all four remaining.

**`[I]` The deepest cause is a circularity, not an omission.** `CMG-INV-10`'s declared verification condition is *"validator exit status zero with zero findings."* The validator exits zero. It exits zero without recomputing anything, without walking the corpus, and without a single write outside its own evidence file. **The constitution defines the success of the missing check as proof that it ran.** `XV.5` — *"a Registry that cannot be regenerated IS invalid"* — is the same failure stated falsifiably, and by its terms `CMG-REGISTRY.json` is already invalid. `XI.10` is the same failure stated unfalsifiably. **That is why it is deeper: `XV.5` is where META-A becomes provable, `XI.10` is where it became invisible.**

**`[I]` The corpus closed the ground it never projected.** `XI.13` calls the invariant set *"the immutable ground against which every other part of this instrument is checked."* `closed_enumerations` records it CLOSED. The Registry does not project it — `invariants`, `lifecycle_phases` and `unknown_concept_dispositions` are all named as closed and all absent — and `CMG-INV-09`'s check, which verifies only that the closing invariant's identifier appears somewhere in the canonical text, passes. **META-A is not merely a failure the corpus has; it is a failure operating on the apparatus by which the corpus checks itself.**

**This addendum verifies, corrects and re-locates. It recommends nothing, designs nothing, amends nothing, and eliminates nothing.**

---

*PHASE R2 ADDENDUM · AUTHORITY = NONE (DERIVED TRUTH) · Reports; determines nothing.*
*`CERTIFIED-PROVISIONAL`; Tier T1 VACANT; `CMG-L-12` applies to every statement herein.*
*Reproduce: `python3 00-CMG/tools/cmg_validate.py --repo-root .` → `findings: 0`, `EXIT=0`*
