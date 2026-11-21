# PHASE R1 — ROOT-SET INDEPENDENCE, REDUCTION, MINIMALITY, AND CANONICAL BASIS

| Field | Value |
|---|---|
| AUTHORITY | **NONE (DERIVED TRUTH)** |
| BASELINE | `integration/recovery-001` @ `1e3e4ba9` |
| METHOD | PROVE OR REFUTE · exhaustive over all 2⁸ subsets |
| RULE OBSERVED | Invent nothing · assume nothing · skip nothing · sample nothing · **normalize nothing without proof** |
| MODEL | `.runtime/phase-r0/r1_basis.py` — every entailment edge cites a located clause; absence of an edge is an explicit independence claim tested by counterfactual |
| CLASSIFICATION | `[F]` · `[I]` · `[A]` · `[GAP]` · `[UNKNOWN]` |

---

## R1.0 — TWO CORRECTIONS TO PHASE R0, ISSUED FIRST

**`[F]` CORRECTION 1 — R0 conflated the UNCERTAINTY root set with the BLOCKER root set.** Measured at HEAD:

```
R9  UICM : state_counts.BLOCKED = 0 · validation.blocking_violated = 0
           validation.blocking_failures = [] · accepted = true
           NOT WIRED to any .sh, .yml or Makefile target (grep: zero hits)
R10 RPI  : blocking_failures = []  ·  passed = True  ·  verdict = "pass"
           all 30 findings severity = "advisory"
```

`[I]` **R9 and R10 block nothing.** They are roots of *recorded uncertainty* and not of *blocked work*. **10 uncertainty roots ⇒ 8 blocking roots.**

**`[F]` CORRECTION 2 — R0's over-determination claim was made at the wrong level.** R0 argued R1 ⊥ R2 because *"`DEF-02` ⟹ `UCCEP-F-004` but not conversely."* `[I]` That compares `VAC-01` (an **instance**) with the ceiling — not `ROOT-Ω` (the **principle**) with `CEP-006` I.4. Re-tested at root level in §R1.4, **R2 absorbs into R1.**

---

## R1.1 — CORRECTED ROOT INVENTORY

| ID | Type | Owner | Authority | Location | Status | Dependents | Blocking |
|---|---|---|---|---|---|---|---|
| **R1** | PRINCIPLE | none located | out-of-corpus | `XLIV.7` · `CEP-000` §5.4 · `XVII.4` | **ACTIVE** | **28** | **YES** |
| **R2** | CLAUSE | `CEP-006` | T2 | `CEP-006` I.4 | **ACTIVE** | 3 | YES → **absorbed** |
| **R3** | PRINCIPLE | `CMG-000001` | T1M | `CMG-L-08` / `LXVI.5` | **ACTIVE** | **41** | **YES** |
| **R4** | DEFECT | `CMG-000001` | T1M | `CMG-000001` XXV.3 | **ACTIVE** | 6 | **YES** |
| **R5** | RELATION | split | split | `CEP-00x` P.3–P.5 · `CEP-000` §6.4 | **ACTIVE** | 6 | YES → **absorbed** |
| **R6** | CONFIG | `REG-AUTO-001` | T2-adjacent | `00-BOOK/tools/config.py:885` | **ACTIVE** | 6 | **YES** |
| **R7** | CONTRADICTION | `UCKP` / `CMG` | disputed | `engine/uckp/law.py:41` + `alignment.py` | **ACTIVE** | 6 | **YES** |
| **R8** | RECORD DEFECT | `CMG-000001` | T1M | `CMG-REGISTRY.json → artifacts[CMG-000001].state` | **ACTIVE** | 4 | **YES** |
| **R9** | MEASUREMENT | 5 discharging owners | derived | `04-CLOSURE-GAP-REGISTER.json` | **ACTIVE** | 158 | **NO** |
| **R10** | HEURISTIC | capability owners | derived | `UCOS-RPI-GAPS.json` | **ACTIVE** | 30 | **NO** |

`[F]` **Liveness verification — none discharged, superseded, withdrawn or merged.** All ten remain recorded at HEAD. Two (R9, R10) are re-classified **non-blocking on their own recorded fields**, not on judgement.

`[F]` **Dependent re-assignment, corrected under proof:** `GAP-P-01` (XXVII.3 implemented POST-EFFECT only) and `GAP-P-02` (no cross-register reconciliation) were assigned to R8 in Phase R0. `[I]` Both are **validator** defects, not record defects; they persist whether or not `CMG-000001`'s state field is corrected. **Re-assigned to R3.** R8: 6 → **4**. R3: 40 → **41**.

**`[F]` Corrected totals: 10 roots · 8 blocking · 289 dependents · 100 live blocking dependents.**

---

## R1.2 — PAIRWISE INDEPENDENCE MATRIX

`[F]` Complete, 10 × 10, no sampling. `ENT` = entailment **proved from located text**; `.` = independence claimed and tested by counterfactual (§R1.4).

```
          R1    R2    R3    R4    R5    R6    R7    R8    R9   R10
R1         —   ENT     .     .   ENT     .     .     .     .     .
R2         .     —     .     .     .     .     .     .     .     .
R3         .     .     —     .     .     .     .     .     .     .
R4         .     .     .     —     .     .     .     .     .     .
R5         .     .     .     .     —     .     .     .     .     .
R6         .     .     .     .     .     —     .     .     .     .
R7         .     .     .     .     .     .     —     .     .     .
R8         .     .     .     .     .     .     .     —     .     .
R9         .     .     .     .     .     .     .     .     —     .
R10        .     .     .     .     .     .     .     .     .     —
```

`[F]` **Exactly two entailment edges exist: R1 ⟹ R2 and R1 ⟹ R5.** The relation is **acyclic** and has **depth 1** — no chained absorption is possible.

### The eight questions, per pair (representative — full matrix above)

| Question | R1/R2 | R1/R7 | R3/R8 |
|---|---|---|---|
| Can A exist if B resolved? | R1 yes, R2 **no** | both yes | both yes |
| Can B exist if A resolved? | R2 **no** | R7 **yes** | both yes |
| Can A be derived from B? | R2 from R1 **yes** | **no** | **no** |
| Can A subsume B? | R1 subsumes R2 | **no** | **no** |
| Can A make B irrelevant? | **yes** | **no** | **no** |

---

## R1.3 — ROOT REDUCTION IMPACT TABLE

`[F]` Baseline: **8 blocking roots, 100 live dependents.**

| Resolve | Roots left | Deps left | Deps removed | Roots collapsed | Deps unaffected |
|---|---:|---:|---:|---:|---:|
| **R3** | 7 | **59** | **41** | 1 | 59 |
| **R1** | **5** | 63 | 37 | **3** | 63 |
| R4 | 7 | 94 | 6 | 1 | 94 |
| R5 | 7 | 94 | 6 | 1 | 94 |
| R6 | 7 | 94 | 6 | 1 | 94 |
| R7 | 7 | 94 | 6 | 1 | 94 |
| R8 | 7 | 96 | 4 | 1 | 96 |
| R2 | 7 | 97 | 3 | 1 | 97 |
| **R9** | **8** | **100** | **0** | **0** | **100** |
| **R10** | **8** | **100** | **0** | **0** | **100** |

`[I]` **R9 and R10 remove zero blocking dependents and collapse zero roots.** Their 188 items are real recorded uncertainty carrying **no blocking effect**.

---

## R1.4 — `ROOT-Ω` ABSORPTION TEST

| Root | Verdict | Located evidence |
|---|---|---|
| **R2** | **DIRECT MANIFESTATION — ABSORBED** | `CEP-006` I.4 is **conditional**: *"**Where** final constitutional finality **requires** an authority residing outside the corpus…"*. `ROOT-Ω` supplies the antecedent — finality is the highest standing, and `XLIV.7` (*"no authority SHALL grant itself ratification competence"*) with `CEP-000` §5.4 forbid conferring it in-corpus. **Counterfactual:** were `ROOT-Ω` false, an in-corpus authority could confer finality, I.4's antecedent would never trigger, and I.4 would be **vacuous law**. R2 has no content independent of R1. |
| **R5** | **INDIRECT MANIFESTATION — ABSORBED (blocking content only)** | R5's blocking content is the unbindability of an **out-of-corpus** act count. **Counterfactual:** once R1 resolves, the act has been performed, and `CEP-001` XVII.1 plus `urat_engine.py` record it as a content-addressed act — demonstrated at HEAD: `EC-1` carries digest `3625ea5f92c8acc1` at `URAT-REC-01`. The count becomes observable *post hoc*. Residual content (future acts) blocks nothing at HEAD. |
| **R3** | **INDEPENDENT** | **Counterfactual:** with T1 occupied and every artifact RATIFIED, `cmg_validate.py` still reads **14 of 19** collections from the projection with no text binding (Phase P, measured). Standing does not bind enumerations. |
| **R4** | **INDEPENDENT** | **Counterfactual:** ratification does not rewrite XXV.3. `CMG-S-07 ↔ RATIFIED / FINALIZED` remains one meta-state onto two located states; six `CEP-006` VI.1 states remain unmapped; XXV.3's own conflict rule still mandates an uncorrected amendment. |
| **R6** | **INDEPENDENT** | **Counterfactual:** `EXCLUDE_DIR_PREFIXES` is a tuple in `00-BOOK/tools/config.py`. Ratifying T1 does not alter it; `00-MASTER/` and `00-BOOK/CONTROL-TOWER/` remain outside the registration universe; 21 of 44 artifacts remain unhashed. |
| **R7** | **INDEPENDENT — NON-OBVIOUS** | R7 *looks* like a `ROOT-Ω` violation (*"its authority derives from itself"*). But `ROOT-Ω` constrains what the corpus **may receive**; R7 is what code **claims**. **Counterfactual:** with T1 lawfully occupied, `engine/uckp/alignment.py` still declares `UCKP-LAW-0001` role `SUPREME` while `CMG-REGISTRY.json` still records `tier: T4`, `superiors: ["VAC-01"]`. The records still contradict; `CAA-INV-01` still passes. |
| **R8** | **INDEPENDENT — CLOSEST CALL** | Resolving R1 would **enable** `CMG-000001` to reach RATIFIED. But (a) it does not **effect** it — `CMG-T-03…T-05` must still be traversed; and (b) **R8 is independently resolvable without R1**: `LXXXI.6` states the standing **IS** PROVISIONAL (`CMG-S-06`, IN-EFFECT), so correcting the record needs no external act. Two-way independence holds. |

---

## R1.5 — `CEP-006` I.4 ABSORPTION TEST

`[F]` **No root absorbs into R2.** R2's dependent set is `{UCCEP-F-004, CERTIFIED-PROVISIONAL ceiling, FR-02}` — three items, all consequences of the finality reservation and of nothing else.

| Root | Verdict | Evidence |
|---|---|---|
| R1 | **INDEPENDENT (and R2's superior)** | The entailment runs R1 ⟹ R2, never R2 ⟹ R1. |
| R3 · R4 · R6 · R7 · R8 | **INDEPENDENT** | None cites `CEP-006` I.4; none is a finality rule. XXV.3 maps **states**; `EXCLUDE_DIR_PREFIXES` bounds a **universe**; `SUPREMACY_CLAUSE` asserts **rank**; the record defect is a **field value**. |
| R5 | **INDEPENDENT OF R2** | I.4 says nothing about act individuation; R5 absorbs into R1, not R2. |

`[I]` **R2 is a leaf.** It absorbs upward into R1 and absorbs nothing itself — the least load-bearing member of the original set.

---

## R1.6 — MINIMAL BASIS SEARCH

`[F]` **Exhaustive over all 2⁸ = 256 subsets of the blocking set.**

| Attempted size | Generating sets found | Blocking evidence |
|---|---|---|
| 10 → 9 | ✔ | R9 removed: `blocking_failures = []`, `BLOCKED: 0`, not gate-wired |
| 9 → 8 | ✔ | R10 removed: `blocking_failures = []`, `verdict = pass`, all `advisory` |
| 8 → 7 | ✔ | R2 removed: absorbed into R1 (§R1.4) |
| 7 → 6 | ✔ | R5 removed: blocking content absorbed into R1 (§R1.4) |
| **6 → 5** | ✘ | **0 generating sets.** Each of R1, R3, R4, R6, R7, R8 has a dependent set no other root entails. Removing any leaves ≥4 dependents unexplained. |
| 5 → 4 · 4 → 3 · 3 → 2 · 2 → 1 | ✘ | 0 generating sets at every size |

```
size 1: 0 generating sets      size 4: 0 generating sets
size 2: 0 generating sets      size 5: 0 generating sets
size 3: 0 generating sets      size 6: 1 generating set  →  {R1, R3, R4, R6, R7, R8}
                               BASIS IS UNIQUE
```

---

## R1.7 — IRREDUCIBILITY TEST

**Hypothesis under falsification: *"The root set is minimal."***

`[F]` **The 10-root set is NOT minimal — falsified, and a smaller basis is produced.**
`[F]` **The 6-root basis IS minimal, and it is UNIQUE.**

### Proof of irreducibility

1. `[F]` The entailment relation contains exactly two edges, both from R1, and is acyclic of depth 1.
2. `[I]` A root is removable from a generating set **iff** some retained root entails it.
3. `[F]` Only R2 and R5 are entailed. Every other blocking root is entailed by nothing.
4. `[I]` Therefore the minimum generating set is exactly the set of non-entailed blocking roots: **8 − 2 = 6**.
5. `[F]` Exhaustive search confirms: **one** size-6 generating set, **zero** at sizes 1–5. ∎

### `[I]` The load-bearing caveat — stated because it bounds the whole result

**Minimality is relative to the located entailment relation, and that relation is not proved complete.** Two edges were derived from located text; six independence claims rest on **counterfactuals** (§R1.4). `[I]` **If any counterfactual is wrong, the basis shrinks.** The most fragile is **R8 → R1** (marked *closest call*): it survives only because `LXXXI.6` makes the record correctable without an external act. `[GAP]` **`GAP-R1-01` — the corpus contains no entailment register between constitutional defects, so entailment must be derived per pair and cannot be mechanically verified.**

---

## R1.8 — LEVERAGE ANALYSIS

| Root | Direct dependents | Indirect (via entailment) | **Total impact** | Roots collapsed | INT/EXT |
|---|---:|---:|---:|---:|---|
| **R3** | **41** | 0 | **41** | 1 | **INTERNAL** |
| **R1** | 28 | **9** (R2:3 + R5:6) | **37** | **3** | **EXTERNAL** |
| R7 | 6 | 0 | 6 | 1 | INTERNAL |
| R4 | 6 | 0 | 6 | 1 | INTERNAL |
| R6 | 6 | 0 | 6 | 1 | INTERNAL |
| R5 | 6 | 0 | 6 | 1 | absorbed |
| R8 | 4 | 0 | 4 | 1 | INTERNAL |
| R2 | 3 | 0 | 3 | 1 | absorbed |
| *R9* | *158* | *0* | *158* | **0** | *non-blocking* |
| *R10* | *30* | *0* | *30* | **0** | *non-blocking* |

| Measure | Root | Value |
|---|---|---|
| **Most impactful (blocking dependents)** | **R3** | 41 |
| **Highest dependency-collapse (roots)** | **R1** | 3 roots (itself + R2 + R5) |
| **Highest reduction-per-act** | **R3** | 41 dependents, **no external act required** |
| **Highest uncertainty-reduction (raw items)** | *R9* | 158 — but **zero** blocking effect |
| **Least impactful blocking root** | **R2** | 3 dependents, and absorbed |
| **Least value overall** | **R10** | 30 items, all advisory, `verdict = pass` |

`[I]` **The decisive asymmetry: the most impactful blocking root is INTERNAL.** R3 removes 41 of 100 live dependents and requires no external authority. R1 removes 37 and is **provably impossible** at HEAD.

---

## R1.9 — CANONICAL BASIS DETERMINATION

| | Quantity | Value |
|---|---|---|
| **A** | Current root set size | **10** |
| **B** | Minimal **blocker** basis size | **6** |
| **C** | Independent root count | **6** — R1, R3, R4, R6, R7, R8 |
| **D** | Derived / absorbed root count | **2** — R2 → R1, R5 → R1 |
| **E** | Subsumed (non-blocking) root count | **2** — R9, R10 |
| **F** | **Irreducible blocker basis** | **{ R1, R3, R4, R6, R7, R8 }** |
| **G** | Unique or non-unique | **UNIQUE** — exactly one size-6 generating set over 256 subsets |
| **H** | Single highest-leverage root | **R3** (`CMG-L-08`) — 41 dependents, internal |
| **I** | Exact blocker-collapse sequence | below |

### `[F]` Blocker-collapse sequence (greedy by dependents removed)

```
start                    8 blocking roots   100 dependents
step 1  collapse R3      INTERNAL           −41   →  7 roots,  59 deps
step 2  collapse R1      EXTERNAL/IMPOSSIBLE −37  →  4 roots,  22 deps   (removes R1, R2, R5)
step 3  collapse R7      INTERNAL            −6   →  3 roots,  16 deps
step 4  collapse R4      INTERNAL            −6   →  2 roots,  10 deps
step 5  collapse R6      INTERNAL            −6   →  1 root,    4 deps
step 6  collapse R8      INTERNAL            −4   →  0 roots,   0 deps
```

**`[I]` Partitioned by actionability:**
```
INTERNAL segment  5 roots  R3(41) R4(6) R6(6) R7(6) R8(4)   = 63 of 100 dependents,  no external act
EXTERNAL segment  1 root   R1(28) + absorbed R2(3) R5(6)    = 37 of 100 dependents,  IMPOSSIBLE at HEAD
NON-BLOCKING      2 roots  R9(158) R10(30)                  = 188 items, zero blocking effect
```

`[I]` **63 % of live blocking dependents lie behind internally eliminable roots. The sequence does not require the external act until step 2, and steps 3–6 do not require it at all.**

---

## R1.10 — TERMINAL DETERMINATION

| # | Question | Answer |
|---|---|---|
| **1** | **Are the 10 roots genuinely independent?** | **`[F]` NO.** Two absorb (R2 → R1, R5 → R1); two are non-blocking (R9, R10). **6 of 10 are genuinely independent blocking roots.** |
| **2** | **Can the root set be reduced?** | **`[F]` YES — 10 → 6**, in four proved steps: −R9, −R10 (non-blocking, on their own recorded fields), −R2, −R5 (absorbed into R1). |
| **3** | **Smallest provable blocker basis** | **`[F]` { R1, R3, R4, R6, R7, R8 } — size 6, UNIQUE**, verified exhaustively over all 256 subsets. |
| **4** | **Root eliminating the greatest remaining work** | **`[F]` R3 (`CMG-L-08`)** — 41 of 100 live dependents, **internal, no external act**. |
| **5** | **Root collapsing the greatest number of dependencies** | **`[F]` R1 (`ROOT-Ω`)** — collapses **3 roots** (itself + R2 + R5) and 37 dependents. `[I]` R3 wins on *dependents*, R1 wins on *roots*. |
| **6** | **Root contributing the least value** | **`[F]` R10** — 30 items, all `severity: advisory`, `blocking_failures: []`, `verdict = pass`; removes **0** blocking dependents. Among blocking roots: **R2** (3 dependents, and absorbed). |
| **7** | **Is the remaining-work package over-specified?** | **`[F]` YES — by 4 of 10 roots (40 %).** R9 and R10 are non-blocking; R2 and R5 are entailed. `[I]` A package of 10 over-states the irreducible obligation by four members. |
| **8** | **Is the current blocker model minimal?** | **`[F]` NO for the 10-root model. `[F]` YES for the 6-root basis** — proved irreducible and unique, **relative to the located entailment relation** (caveat at §R1.7). |
| **9** | **Mathematically irreducible basis** | **`[F]` { R1, R3, R4, R6, R7, R8 }.** Of these, **5 are internal and eliminable**; **1 (R1) is external and provably impossible** — `ROOT-Ω`, min proof set `{XLIV.7, CEP-000 §5.4, XVII.4}`, with a disjoint second proof at `AUTH-03/04/06` + `Ω-010` + `CM-007`. |
| **10** | **Canonical next elimination target** | **`[I]` DERIVED, not recommended: R3 (`CMG-L-08` / the projection-validator binding).** It is the unique maximum on **all three** measures that admit action: most blocking dependents (41), highest reduction-per-act, and **internal** — requiring no external authority, no amendment (unlike R4, whose XXV.3 self-mandate triggers `LXXX.6` automatic revocation), and no jurisdiction the corpus lacks. **This determination performs no elimination and proposes no method.** |

---

## CLASSIFIED RESIDUE

### FACTS `[F]`
1. R9 (UICM): `BLOCKED: 0`, `blocking_violated: 0`, `blocking_failures: []`, `accepted: true`, **not wired to any gate** — zero blocking effect.
2. R10 (RPI): `blocking_failures: []`, `passed: True`, `verdict: "pass"`, all 30 `severity: advisory` — zero blocking effect.
3. The entailment relation contains **exactly two edges**, both from R1, acyclic, depth 1.
4. Exhaustive search over 256 subsets: **one** size-6 generating set, **zero** at sizes 1–5.
5. `CEP-006` I.4 is conditional; `ROOT-Ω` supplies its antecedent; without `ROOT-Ω` it is vacuous law.
6. `EC-1` carries content digest `3625ea5f92c8acc1` at `URAT-REC-01` — the external act **is** recorded as a content-addressed act.
7. R3 has 41 dependents; R1 has 28 direct + 9 indirect = 37.
8. 63 of 100 live blocking dependents lie behind internally eliminable roots.
9. `GAP-P-01`/`GAP-P-02` are validator defects and were mis-assigned to R8 in Phase R0; R8 falls 6 → 4, R3 rises 40 → 41.
10. R7 survives R1's resolution: `tier: T4` + `superiors: ["VAC-01"]` versus role `SUPREME` remains contradictory regardless of who occupies T1.

### INFERENCES `[I]`
1. Phase R0 conflated the uncertainty root set with the blocker root set; the distinction removes 2 roots.
2. R0's over-determination argument compared an **instance** (`VAC-01`) with a **principle** (`CEP-006` I.4); re-tested at root level, R2 absorbs.
3. The minimum generating set equals the set of non-entailed blocking roots — **structurally forced at 6**.
4. The most impactful blocking root (R3) is **internal**; the second (R1) is **provably impossible**.
5. The 10-root package over-specifies the irreducible obligation by 40 %.
6. R7's independence is non-obvious and is the most instructive result: a clause that *looks* like a `ROOT-Ω` violation is not a `ROOT-Ω` manifestation, because `ROOT-Ω` governs what may be **received**, not what may be **claimed**.
7. Minimality is relative to the located entailment relation, which is not proved complete.

### ASSUMPTIONS `[A]`
`A-R1-01` The dependent sets carried forward from Phases O/P/Q are complete for each root; an unlisted dependent changes leverage but not the basis.
`A-R1-02` Independence claims rest on counterfactuals derived from located clauses, not on an executable entailment oracle — none exists.
`A-R1-03` "Blocking" means what each register's own `blocking_failures` / `BLOCKED` / `verdict` field records.
`A-R1-04` The greedy collapse sequence orders by dependents removed; other orderings are equally valid and this determination privileges none.
`A-R1-05` Measurements are for `1e3e4ba9` in this environment.

### GAPS `[GAP]`
| Id | Gap |
|---|---|
| `GAP-R1-01` | No entailment register between constitutional defects exists; entailment must be derived per pair and cannot be mechanically verified |
| `GAP-R1-02` | No located instrument distinguishes a *blocking* uncertainty item from a *recorded* one; the distinction had to be reconstructed from each register's own fields |
| `GAP-R1-03` | R9's 158 gaps name five validating gates, **none of which is wired to any entrypoint** — the discharge path is declared but not connected |

### UNKNOWNS `[UNKNOWN]`
`UNK-R1-01` Whether additional entailment edges exist that no located clause expresses — if any do, the basis is smaller than 6.
`UNK-R1-02` Whether R8's independence survives scrutiny by the owner of `CMG-000001` (the *closest call*).
`UNK-R1-03` Whether R9's five named gates were intended to be wired and were not, or were never intended to be.
`UNK-R1-04` Whether the 188 non-blocking items would become blocking if R9's gates were wired.

---

## PHASE R1 TERMINAL VERDICT

> **DETERMINATION-COMPLETE · 10-ROOT SET NOT MINIMAL · IRREDUCIBLE BLOCKER BASIS = 6, UNIQUE · 5 INTERNAL, 1 EXTERNAL AND IMPOSSIBLE · PACKAGE OVER-SPECIFIED BY 40 %**

**`[F]` The reduction succeeds and is proved exhaustively.** Ten roots reduce to six in four steps, each justified by located evidence rather than by judgement: R9 and R10 fall out because **their own registers record `blocking_failures: []` and `verdict: pass`**; R2 and R5 fall out because `ROOT-Ω` entails them. The resulting basis **{R1, R3, R4, R6, R7, R8}** is the unique size-6 generating set among all 256 subsets, and no subset of size 1–5 generates.

**`[I]` Phase R0's error was one of level, not of fact.** It proved `DEF-02 ⟹ UCCEP-F-004` and concluded R1 ⊥ R2 — but that compares an *instance* of the vacancy with the *ceiling*, not the *principle* with the *clause*. At root level, `CEP-006` I.4 is a **conditional whose antecedent `ROOT-Ω` supplies**: strip `ROOT-Ω` and I.4 never triggers. R2 is vacuous without R1 and is the least load-bearing member of the original set.

**`[F]` The most consequential structural result is the actionability split.** Of 100 live blocking dependents, **63 lie behind five internally eliminable roots** and **37 behind one that is provably impossible**. The collapse sequence reaches step 6 with only step 2 requiring an external act — and steps 3 through 6 never require it.

**`[I]` The single highest-leverage root is R3, and it is internal.** `CMG-L-08` — *zero hard coding* — carries **41 of 100** dependents: every divergence, every blind spot, every false pass, and `CE-01` itself. It is the unique maximum on all three actionable measures, needs no external authority, and unlike R4 carries no self-mandated amendment that would trigger `LXXX.6` automatic revocation. **The corpus's central anti-drift principle is also its single largest blocker basis element.**

**`[I]` And the most instructive result is a negative one.** R7 — `UCKP-LAW-0001` declaring that *"its authority derives from itself"* — reads exactly like a `ROOT-Ω` violation, and is **not** a `ROOT-Ω` manifestation. `ROOT-Ω` constrains what a corpus may **receive**; R7 is what code **claims**. Occupying T1 lawfully would leave `tier: T4` and role `SUPREME` contradicting each other, with `CAA-INV-01` still passing. **Absorption by resemblance is not absorption by entailment, and the difference is one basis element.**

**`[F]` Minimality is proved relative to the located entailment relation, which is itself not proved complete** (`GAP-R1-01`). Two edges were derived from text; six independence claims rest on counterfactuals. If any counterfactual fails, the basis is smaller than six — the closest call being R8.

**This determination reduces, proves and refutes. It recommends nothing, designs nothing, amends nothing, and eliminates nothing.**

---

*PHASE R1 · AUTHORITY = NONE (DERIVED TRUTH) · Reports; determines nothing.*
*`CERTIFIED-PROVISIONAL`; Tier T1 VACANT; `CMG-L-12` applies to every statement herein.*
*Reproduce: `python3 .runtime/phase-r0/r1_basis.py`*
