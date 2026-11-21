# PHASE 9 — TERMINAL DETERMINATION

| Field | Value |
|---|---|
| Question | Does proposition `U-M` have a **uniquely correct interpretation derivable from the existing determination chain**? |
| Answer | **YES.** The chain defines the term, applies it, and returns a verdict on it — in **Phase 3**, four phases before `U-M` was named. `PHASE3:§F.1` and `§G.4` define *"unconditional readiness"* by its defeaters, list residual survival as an **independent, non-removable** one, and answer **NO** — and `PHASE3:§F.2` states the answer as a **count**: **0 of the 12 admissible models reach UNCONDITIONAL READY**. `PHASE4:§0.2` and `§I.3` affirm that ground and explicitly disclaim conflict. Nothing in Phases 5–8 retracts it. |
| The error being corrected | `PHASE7:§11.5` asserts, verbatim: *"a determination this phase is constrained against making, and **which no artifact in Phases 0-7 makes**."* **That assertion is false.** `PHASE3:§G.4` makes it. `PHASE8` inherited the false premise and built `§5.3` on it. |
| Terminal verdict | **A — `U-M` resolved uniquely; terminal outcome determined.** |
| Terminal outcome | **Outcome B — UNCONDITIONAL READY DOES NOT EXIST** — which is the content of `PHASE3:§G.4`, unretracted. |
| Inputs | The nine named documents. `PHASE05-GOVERNANCE-INDEPENDENT-REMEDIATION.md` is **not** in this phase's input list; every Phase-0.5 fact relied on below is taken from its restatement in `PHASE1:§R-7` or `PHASE3:§E.1`–`§E.3`, which are inputs. |
| Method | **Read-only, documentary.** No source file read, no probe executed, no measurement taken. Nine `grep`/`sed` reads of the input documents and a five-command baseline check. |
| Repository files modified | **NONE.** This document is the only addition. |

### 0.1 Compliance with the stated constraints

| # | Constraint | Compliance |
|---|---|---|
| 1 | Read-only | **MET.** Only the nine inputs were read. |
| 2 | No source modification | **MET.** No source file opened or written. |
| 3 | No mutating command | **MET.** `shasum`, `git rev-parse`, `git status --porcelain`, `git ls-files --cached`, `ls`, `grep`, `sed` only. |
| 4 | No governance recommendation | **MET, and the distinction is load-bearing.** This phase does **not** adopt a reading. It **reports** that `PHASE3` adopted one and that no later phase retracted it. Reporting a determination already in the record is not making one. §4.4 states the boundary explicitly. |
| 5 | No new closure items unless logically unavoidable | **MET.** **Zero** introduced. One is **removed** — `U-M` resolves. |
| 6 | Every assertion classified | **MET.** **[MEASURED]** = quoted or line-verified from an input this phase read. **[DERIVED]** = follows deductively from two or more MEASURED items, with both named. **[INFERRED]** = a judgment exceeding strict deduction, and labelled as such. |
| — | Do not search for new blockers · propose remediations · propose governance · expand the closure set | **MET on all four.** §§1–9 contain no blocker search, no remedy, no governance proposal, and no closure-set expansion. |

---

## 1. Executive determination

```
================================================================================
  DOES U-M HAVE A UNIQUELY CORRECT INTERPRETATION DERIVABLE FROM
  THE EXISTING DETERMINATION CHAIN?                                    Y E S
================================================================================

  IT WAS ALREADY DECIDED, IN PHASE 3, AND THE DECISION WAS NEVER RETRACTED.

  PHASE3 §F.1  "'Unconditional' admits two readings.  Both are answered,
                because conflating them is how this question gets answered
                wrongly."
               Reading 2 ... "fails PERMANENTLY rather than pending a
                decision.  Two grounds: ... 2. Three residuals survive every
                admissible model by construction."                [MEASURED]

  PHASE3 §G.4  "UNCONDITIONAL READY FOR IMPLEMENTATION?      N O
                Why not unconditional -- three independent reasons, none
                removable by any governance answer:
                  ...
                  3. RES-3, RES-4 and R-7w survive every admissible model
                     by construction ...
                Governance completion yields DECISION-completeness.
                Implementation completion yields BLOCKER-completeness.
                Neither yields UNCONDITIONAL readiness, and no combination
                does."                                            [MEASURED]

  PHASE4 §0.2  "Phase 3 asked whether readiness could be *unconditional* and
                answered NO ... Phase 4 asks whether the *execution gate* can
                be reached -- a weaker ... target.  THE TWO ANSWERS DO NOT
                CONFLICT; THEY ANSWER DIFFERENT QUESTIONS."        [MEASURED]

  PHASE4 §I.3  "The third ground -- three residuals surviving every model --
                REMAINS TRUE and is carried into the target state."[MEASURED]

  ── THE ARITHMETIC OF THE WORD ─────────────────────────────────────────────

  Occurrences of "unconditional" as a READINESS PREDICATE, Phases 0-6:

      PHASE0 ...  0 of 1  (its hit is "constructed unconditionally")
      PHASE1 ...  0 of 1  (its hit is "unconditionally refused")
      PHASE2 ...  2 of 4  §G.4 heading · §I stop condition
      PHASE3 ... 13 of 16 §F.1 · §F.2 · §G.3 · §G.4 · §I — the definitional
                          treatment and its counted verdict
      PHASE4 ...  2 of 2  §0.2 · §I.3 — both AFFIRM Phase 3's residual ground
      PHASE5 ...  0
      PHASE6 ...  0
                          ────────────────────────────────────────
      TOTAL uses as a readiness predicate ............ 17
      uses that ADOPT residual-freedom ............... 17
      uses that ADOPT outcome-freedom ................  0        [MEASURED]

  AND THE COUNTED VERDICT, PHASE3 §F.2:

      ZERO-NEW-BLOCKER FULL-CLOSURE MODELS ...  12  <- admissible here
          reaching READY-CONDITIONAL-ON-SELECTION  12  <- all of them
          reaching UNCONDITIONAL READY .........   0  <- none of them

      "All 12 reach conditional readiness.  NONE REACHES UNCONDITIONAL
       READINESS.  The count is 12 and not fewer because the blocking
       factors (governance selection, UK-1, UK-2, THREE RESIDUALS) are
       invariant across the admissible set."                    [MEASURED]

      That is Outcome B, QUANTIFIED OVER THE ADMISSIBLE MODEL SET, in
      PHASE3 — with the three residuals named among the blocking factors.

  Reading (i) "outcome-freedom" has ZERO antecedents.  It first appears at
  PHASE7 §11.1, constructed there, and is inherited by PHASE8 §5.3.

  ── THE VERDICT ────────────────────────────────────────────────────────────

  U-M RESOLVES UNIQUELY TO RESIDUAL-FREEDOM.
      attested   4x    PHASE2 §G.4 r4 · PHASE3 §F.1 R2g2 · PHASE3 §F.2
                       (counted: 0 of 12) · PHASE3 §G.4 r3
      affirmed   2x    PHASE4 §0.2 · PHASE4 §I.3
      computed   1x    PHASE6 §11.1(b): residual-freedom => UNREACHABLE
      retracted  0x

  THE ALTERNATIVE IS NOT MERELY UNATTESTED.  IT IS CONTRADICTED.
      Under outcome-freedom, governance + implementation + successful
      execution WOULD yield unconditional readiness.  PHASE3 §G.4's
      closing sentence denies exactly that, and PHASE4 §0.2's own
      diagram shows the EXECUTED column at "0 blockers · 3 residuals ·
      0 unknowns" -- residuals surviving the successful run.      [DERIVED]

  TERMINAL OUTCOME = B.  UNCONDITIONAL READY DOES NOT EXIST.
  It has been the chain's answer since PHASE3 §G.4.
================================================================================
```

### 1.1 The eight questions, one line each

| Q | Answer |
|---|---|
| **Q1** | `U-M` is stated exactly at `PHASE8:§8.G`, quoted verbatim in §2.1. Its subject term *"unconditional ready"* is defined in the chain at `PHASE3:§F.1` and `§G.4`. §2 |
| **Q2** | **7** distinct interpretations present or implied, collapsing to **2** candidates for the terminal predicate plus **3** readings of adjacent predicates and **2** non-assertions. §3 |
| **Q3** | Per-interpretation table with originating phase, dependencies, A/B/C consequence and execution requirement. **2 of 7 require an execution run; 5 do not.** §4.1 |
| **Q4** | **YES — residual-freedom dominates**, on three independent grounds: attestation (**4×**, one of them a counted verdict over all 12 models), downstream affirmation (2×), and contradiction of the alternative. §4.2–§4.3 |
| **Q5** | **YES — outcome-freedom is contradicted** by `PHASE3:§G.4`'s closing sentence read with `PHASE4:§0.2`'s EXECUTED column. §5 |
| **Q6** | **NO.** Exactly one interpretation of the terminal predicate survives the record. §6 |
| **Q7** | **Outcome B follows deductively, adding no new premise.** Every premise is a sentence already in an input document. §7 |
| **Q8** | **NO — and it was not underdetermined after Phase 3 either.** Phases 7 and 8 believed it was, because neither searched Phases 2–4 for an antecedent definition of the term they were treating as undefined. §8 |

---

## 2. `U-M` stated exactly as it exists in the chain — Q1

### 2.1 The proposition, verbatim

**[MEASURED]** `PHASE8:§8.G`, verbatim:

> **`U-M` — Does *"unconditional ready"* mean `0 blockers ∧ 0 unknowns` with the three residuals accepted under `GA-5` (outcome-freedom), or `0 blockers ∧ 0 unknowns ∧ 0 residuals` (residual-freedom)?**

**[MEASURED]** Its two values are stated at `PHASE7:§11.1`:

| Reading | *"Unconditional ready"* means |
|---|---|
| **(i) outcome-freedom** | `0 blockers ∧ 0 unknowns`, with the 3 residuals **accepted** under `GA-5` |
| **(ii) residual-freedom** | `0 blockers ∧ 0 unknowns ∧ **0 residuals**` |

**[MEASURED]** The claim that makes it open, `PHASE7:§11.5` lines 1405–1410, verbatim:

> ```
>   THE DECIDING FACTOR IS NOT EVIDENCE.  It is which reading of
>   "unconditional ready" is adopted — a determination this phase is
>   constrained against making, and which no artifact in Phases 0-7 makes.
>   Under reading (ii) the answer is B and costs nothing.  Under reading (i)
>   the answer is A or C and costs two irreversible mutating runs.
>   BOTH READINGS ARE STATED.  NEITHER IS PREFERRED.
> ```

### 2.2 The single testable clause

**[INFERRED]** `U-M`'s openness rests entirely on one embedded factual claim: **"which no artifact in Phases 0-7 makes."** That is not a normative statement and not a construction. It is a claim about the contents of eight documents, and it is decidable by reading them. **Phase 9's whole task reduces to testing it.**

### 2.3 The test

**[MEASURED]** Occurrences of *"unconditional"* used as a **readiness predicate** across Phases 0–6, counted this phase:

| Document | Total hits | As a readiness predicate | Reading adopted |
|---|---:|---:|---|
| `PHASE0` | 1 | **0** | — (its hit is *"constructed unconditionally"*, `§2.4`) |
| `PHASE1` | 1 | **0** | — (its hit is *"unconditionally refused"*, `§R-5`) |
| `PHASE2` | 4 | **2** | `§G.4` heading, `§I` stop condition — **residual-freedom** |
| `PHASE3` | 16 | **13** | `§F.1`, **`§F.2`**, `§G.3`, `§G.4`, `§I` — **residual-freedom**; the other 3 hits describe `audit_events` construction |
| `PHASE4` | 2 | **2** | `§0.2`, `§I.3` — **affirms Phase 3's residual ground** |
| `PHASE5` | **0** | 0 | — the term does not appear |
| `PHASE6` | **0** | 0 | — the term does not appear |
| | | **17** | **17 residual-freedom · 0 outcome-freedom** |

**[DERIVED]** From the table: `PHASE7:§11.5`'s clause *"which no artifact in Phases 0-7 makes"* is **false**. **Seventeen** uses of the predicate exist across three documents, every one of them treating residual survival as a defeater, and none of them treating residuals as accepted-and-therefore-compatible.

---

## 3. Every distinct interpretation present or implied — Q2

**[MEASURED]** Seven interpretations appear or are implied across Phases 0–8. Three are readings of the terminal predicate; two are readings of **adjacent** predicates that Phase 7 and Phase 8 did not distinguish from it; two are non-assertions that could be mistaken for interpretations.

| # | Interpretation | Predicate it reads | First appearance |
|---|---|---|---|
| **I-1** | *"Unconditionally ready to **begin** implementation, with no unmet precondition"* | **readiness-to-begin** — not the terminal predicate | `PHASE3:§F.1` Reading 1 |
| **I-2** | *"Unconditionally ready such that implementation completes with no unknown remaining"*, with **residual survival as an independent, permanent defeater** | **the terminal predicate** | `PHASE3:§F.1` Reading 2; **`§F.2` (counted: 0 of 12)**; `§G.4` reason 3; antecedent at `PHASE2:§G.4` reason 4 |
| **I-3** | `T-1` as *"0 blockers, 0 unknowns, 3 accepted residuals"* | **a terminal STATE, not the predicate** | `PHASE4:§I.5`; `PHASE5:§I.1` |
| **I-4** | `EXECUTION-CERTIFIED` **(a)** — gate-greenness | **certification**, not readiness | `PHASE6:§11.1` |
| **I-5** | `EXECUTION-CERTIFIED` **(b)** — residual-freedom | **certification**, and **coextensive with I-2** on the residual clause | `PHASE6:§11.1` |
| **I-6** | **(i) outcome-freedom** — `0 blockers ∧ 0 unknowns`, residuals accepted | **the terminal predicate** | `PHASE7:§11.1` — **constructed there; no antecedent** |
| **I-7** | **(ii) residual-freedom** — `0 blockers ∧ 0 unknowns ∧ 0 residuals` | **the terminal predicate** | `PHASE7:§11.1` — **= I-2 = I-5, relabelled** |

### 3.1 The collapse

**[DERIVED]**

```
  I-2  ≡  I-5  ≡  I-7        one interpretation under three labels
                             PHASE3 called it "Reading 2"
                             PHASE6 called it "EXECUTION-CERTIFIED (b)"
                             PHASE7 called it "reading (ii) residual-freedom"

  I-1  and  I-4              readings of ADJACENT predicates
                             (readiness-to-begin; certification-as-gate-greenness)
                             neither is a candidate for the terminal predicate

  I-3                        NOT AN ASSERTION.  PHASE4 §I.5 states in the same
                             breath: "T-1 is NOT 'everything closed.'"
                             A description of a state, explicitly withheld from
                             being a claim that the state satisfies the predicate

  I-6                        THE ONLY GENUINE ALTERNATIVE, and it has zero
                             antecedents in Phases 0-6

  => DISTINCT CANDIDATES FOR THE TERMINAL PREDICATE .......... 2
         residual-freedom  (I-2 / I-5 / I-7)   attested 4x, affirmed 2x
         outcome-freedom   (I-6)               attested 0x, constructed at PHASE7
```

---

## 4. Per-interpretation analysis and domination — Q3, Q4

### 4.1 The interpretation table — Q3

| # | Originating phase | Dependencies | Outcome A | Outcome B | Outcome C | Execution run required? |
|---|---|---|---|---|---|---|
| **I-1** readiness-to-begin | `PHASE3:§F.1` R1 | `GA-1` only. **[MEASURED]** *"Exactly one precondition is irreducible: governance selection on the five closure axes"* | **becomes YES once `GA-1` exists** | no | no | **NO** |
| **I-2 / I-5 / I-7** residual-freedom | `PHASE3:§F.1` R2, **`§F.2`**, `§G.4` r3; `PHASE2:§G.4` r4; `PHASE6:§11.1(b)` | `RES-3`, `RES-4`, `R-7w`. **[MEASURED]** `PHASE3:§E.7` — *"no — all 12 identical"* in every row | **impossible** | **YES, permanently** | no | **NO** — `PHASE6:§11.1(b)` computes UNREACHABLE without one |
| **I-3** `T-1` description | `PHASE4:§I.5`; `PHASE5:§I.1` | `A✓ ∧ B✓` | **not asserted** — *"T-1 is not 'everything closed'"* | not asserted | — | **YES** (both runs) — but the interpretation is withheld |
| **I-4** gate-greenness | `PHASE6:§11.1(a)` | the register **committed**; `uga_engine gate` at target | reachable | no | no | **YES** (both runs) |
| **I-6** outcome-freedom | `PHASE7:§11.1` | `GA-5`; `T-1a`; hence `U-A` and `GA-7` | reachable in principle | no | yes, while undecided | **YES** (both runs) |

```
INTERPRETATIONS REQUIRING AN EXECUTION RUN ........................ 3   I-3, I-4, I-6
INTERPRETATIONS REQUIRING NONE .................................... 2   I-1, I-2/5/7
INTERPRETATIONS YIELDING OUTCOME B ................................ 1   I-2/5/7
INTERPRETATIONS ATTESTED IN PHASES 0-6 ............................ 4   I-1, I-2, I-4, I-5
INTERPRETATIONS OF THE TERMINAL PREDICATE ATTESTED IN PHASES 0-6 .. 1   I-2  (= I-5, = I-7)
```

### 4.2 Does one interpretation dominate? — Q4. **YES.**

**[DERIVED]** Residual-freedom dominates on three independent grounds, each established from a different document.

**Ground 1 — attestation.** **[MEASURED]** Four independent statements adopt it, the third of which is a **counted verdict over the admissible model set**:

| # | Statement |
|---|---|
| `PHASE2:§G.4` reason 4 | *"**Three documented bounds survive every model**, because none of them is a governance question"* — offered as a ground for answering **NO** to *"Is governance sufficient for unconditional implementation readiness?"* |
| `PHASE3:§F.1` Reading 2 ground 2 | *"**Three residuals survive every admissible model by construction**, because none is a governance question … All three are governance-**independent** and were declined by authorization scope"* — the ground on which Reading 2 *"fails **permanently** rather than pending a decision"* |
| **`PHASE3:§F.2`** | **The counted verdict.** *"ZERO-NEW-BLOCKER FULL-CLOSURE MODELS … **12** · reaching READY-CONDITIONAL-ON-SELECTION … **12** ← all of them · **reaching UNCONDITIONAL READY … 0 ← none of them**"*, and in prose: *"All 12 reach conditional readiness. **None reaches unconditional readiness.** The count is 12 and not fewer because the blocking factors (governance selection, UK-1, UK-2, **three residuals**) are **invariant across the admissible set**."* |
| `PHASE3:§G.4` reason 3 | *"RES-3, RES-4 and R-7w survive every admissible model by construction"* — one of *"three independent reasons, none removable by any governance answer"* |

**Ground 2 — downstream affirmation.** **[MEASURED]** Two statements in the phase that most plausibly could have overturned it, and neither does:

| # | Statement |
|---|---|
| `PHASE4:§0.2` | *"Phase 3 asked whether readiness could be **unconditional** and answered NO … Phase 4 asks whether the **execution gate** can be reached — a weaker … target. **The two answers do not conflict; they answer different questions.**"* |
| `PHASE4:§I.3` | *"The third ground — three residuals surviving every model — **remains true and is carried into the target state**, which is why READY-FOR-EXECUTION carries 3 residuals rather than 0."* |

**[INFERRED]** `PHASE4:§0.2` is the strongest single item in the record, because it is Phase 4 pre-empting exactly the misreading Phases 7 and 8 later made: it says its own **YES** and Phase 3's **NO** are answers to different questions, and it declines to let its YES be read as a retraction.

**Ground 3 — the alternative is contradicted**, not merely unattested. §5.

### 4.3 The asymmetry, quantified

```
                                  residual-freedom       outcome-freedom
  attested in Phases 0-6 ......         4x                     0x
  affirmed downstream .........         2x                     0x
  computed to a verdict .......         1x  (PHASE6 §11.1b)     0x
  retracted anywhere ..........         0x                      —
  contradicted by the record ..         no                     YES  (§5)
  first appearance ............    PHASE2 §G.4            PHASE7 §11.1
```

### 4.4 The boundary this phase does not cross

**[INFERRED]** and stated plainly, because it is the difference between a determination and a governance act.

> This phase establishes that **the chain's own record fixes the reading**. It does **not** establish that residual-freedom is the *better* definition of readiness, and it takes no position on that. A party with authority over the program may define readiness however it likes; if it defines it as outcome-freedom, it will be **making a new determination that departs from `PHASE3:§G.4`**, and it should do so explicitly rather than by inheriting `PHASE7:§11.1`'s unattested construction.
>
> The Phase-9 question is *"derivable from the existing determination chain"*. That question is about the record, and the record answers it.

---

## 5. Is any interpretation contradicted by established measurements? — Q5

**YES — I-6 (outcome-freedom) is contradicted.**

**[MEASURED]** `PHASE3:§G.4`, closing sentence, verbatim:

> *"Governance completion yields DECISION-completeness. Implementation completion yields BLOCKER-completeness. **Neither yields UNCONDITIONAL readiness, and no combination does.**"*

**[MEASURED]** `PHASE4:§0.2`'s own transition diagram, the terminal column:

```
  PHASE 3 terminal state            PHASE 4 target                  PHASE 4 outcome
  READY-CONDITIONAL-ON-      ──►    READY-FOR-EXECUTION      ──►    EXECUTED
  GOVERNANCE-SELECTION              (all preconditions               (UK-1, UK-2
                                     verified)                        closed)
  0 blockers                         0 blockers                      0 blockers
  3 residuals                        3 residuals                     3 residuals   ◄──
  2 unknowns                         2 unknowns                      0 unknowns
```

**[DERIVED] The contradiction.** Under I-6, the `EXECUTED` column — `0 blockers · 3 residuals · 0 unknowns`, with the residuals accepted under `GA-5` — **satisfies** unconditional readiness. `PHASE3:§G.4` says that no combination of governance completion and implementation completion yields it, and `PHASE3:§F.1` says Reading 2 *"fails **permanently** rather than pending a decision"* — permanence that cannot be defeated by adding a third term (execution) to the combination, because `PHASE4:§G` measures execution leaving `R-7w` **UNCHANGED** and `PHASE6:§7.2` supplies the mechanism (4 of `commit()`'s 8 refusal points enter the window; **a successful run enters none**).

**[DERIVED]** So the chain asserts of the very state I-6 would call unconditionally ready that it is **not** unconditionally ready. **I-6 is inconsistent with `PHASE3:§G.4` + `PHASE4:§0.2` + `PHASE4:§G` + `PHASE6:§7.2`.**

**[INFERRED] One caveat, stated so the finding is not overclaimed.** `PHASE3:§G.4`'s *"no combination"* names two terms — governance completion and implementation completion — and does not name execution. Read with maximum literalism, it does not quantify over a three-term combination. But `PHASE3:§F.1` Reading 2 does: it is a reading about *"implementation **completes**"* and it calls its failure **permanent**, and `PHASE3:§F.1`'s ground 1 explicitly contemplates the mutating run. **The literalist escape closes as soon as §F.1 is read alongside §G.4, which is how Phase 3 wrote them** — §G.4 is the answer block for §F.1's analysis.

### 5.1 Is any interpretation contradicted *other than* I-6?

**[DERIVED] NO.**

| # | Contradicted? | Basis |
|---|---|---|
| **I-1** | **NO** | It reads a different predicate (readiness-to-begin) and `PHASE3:§F.1` states its own answer for it — NO, *pending a decision* — which is consistent with everything downstream |
| **I-2 / I-5 / I-7** | **NO** | Attested 4×, affirmed 2×, computed to UNREACHABLE once, retracted 0× |
| **I-3** | **NO — because it is not an assertion.** `PHASE4:§I.5`: *"T-1 is **not** 'everything closed.'"* | A description that explicitly declines to be a claim cannot be contradicted |
| **I-4** | **NO** | It reads certification, not readiness. `PHASE6:§11.1` offers it as one of two candidates for a term it declares undefined, and Phase 6 does not assert it |

---

## 6. Do multiple interpretations remain simultaneously admissible? — Q6

**NO.**

**[DERIVED]** The candidate set for the terminal predicate is `{I-6, I-2/5/7}` (§3.1). By §5, `I-6` is inconsistent with four measurements spread across three documents. By §4.2, `I-2/5/7` is attested four times — once as a counted verdict over all 12 models — affirmed twice, and retracted nowhere. **A set of admissible interpretations from which one member is excluded by contradiction and the other is attested and unretracted has cardinality 1.**

```
CANDIDATES FOR THE TERMINAL PREDICATE ............................. 2
    excluded by contradiction with the record ...................... 1   I-6
    surviving ...................................................... 1   I-2 / I-5 / I-7
SIMULTANEOUSLY ADMISSIBLE INTERPRETATIONS ......................... 1
```

**[INFERRED]** `PHASE7:§11.1`'s framing — *"Two readings are live"* — was true of the **vocabulary** and false of the **record**. Two readings had been *named*; only one had ever been *applied*, and the naming happened three phases after the application.

---

## 7. Does an outcome follow deductively, with no new premise? — Q7

**YES. Outcome B.**

**[DERIVED]** The deduction, with every premise located in an input document. **No premise is supplied by this phase**, and π1 is not merely a definition but a **counted result**.

| # | Premise | Located at | Class |
|---|---|---|---|
| **π1** | *"Unconditional"* readiness is defeated by residual survival — and **0 of the 12 admissible models reach it**, with *"three residuals"* named among the invariant blocking factors | `PHASE3:§F.1` R2 g2; **`PHASE3:§F.2`**; `PHASE3:§G.4` r3; `PHASE2:§G.4` r4 | **[MEASURED]** |
| **π2** | `RES-3`, `RES-4`, `R-7w` are not closed by any of the 12 admissible models — *"no — all 12 identical"* in every row | `PHASE3:§E.7` | **[MEASURED]** |
| **π3** | Execution leaves `R-7w` **UNCHANGED**, because it is a failure-path property; 4 of `commit()`'s 8 refusal points enter the window and a successful run enters **none** | `PHASE4:§G`; `PHASE6:§7.2` | **[MEASURED]** |
| **π4** | Closing `R-7w` requires moving serialization inside the authority, declined as *"a larger change than this phase covers"* | `PHASE1:§R-7`; `PHASE3:§E.3` | **[MEASURED]** |
| **π5** | Phase 3's residual ground *"remains true and is carried into the target state"*; Phase 4's YES and Phase 3's NO *"do not conflict; they answer different questions"* | `PHASE4:§I.3`; `PHASE4:§0.2` | **[MEASURED]** |

**[DERIVED]** From π2, no governance answer closes `R-7w`. From π3, no execution outcome closes it — including the successful one, the only outcome Outcome A could rest on. From π4, no act within the chain's authorization closes it. From π5, nothing downstream retracts π1. Therefore, by π1, unconditional readiness is defeated **in every model and on every path**, and its satisfying set is **empty**.

**That is Outcome B — UNCONDITIONAL READY DOES NOT EXIST.** ∎

**[DERIVED]** The deduction adds nothing. It is the same argument `PHASE3:§G.4` states as its reason 3 and `PHASE8:§5.3` states as Lemmas 2–3, with π5 added to establish that the intervening five phases did not retract it.

### 7.1 What Outcome B does and does not mean

**[INFERRED]** Stated because *"unconditional ready does not exist"* invites a reading far darker than the record supports.

| Outcome B **does** mean | Outcome B **does not** mean |
|---|---|
| No reachable state has zero residuals | That the program cannot be executed |
| `R-7w` is permanent within this architecture and this authorization scope | That `R-7w` is dangerous — `PHASE4:§G.3` measures it as a **failure-path** property a successful run never enters |
| The chain's maximal honest claim is bounded | That the maximal claim is weak. `PHASE4:§0.2` puts the `EXECUTED` column at **0 blockers · 0 unknowns · 3 residuals** |
| `GA-5` — residual acceptance — is the operative instrument, permanently | That `GA-5` is a workaround. `PHASE5:§B.5` designs it for exactly this |

---

## 8. Is the chain underdetermined after Phase 8? — Q8

**NO. And it was not underdetermined after Phase 3 either.**

**[DERIVED]** `PHASE8:§5.3` Part 2 argues that with `U-M` undecided the terminal predicate has no extension and Phase 9 must return C. That argument is valid and its premise is false: the predicate **has** an extension, fixed at `PHASE3:§F.1`/`§G.4`. `PHASE8` took the premise from `PHASE7:§11.5`, which asserted it without testing it.

**[INFERRED] Why two consecutive phases missed it.** Both searched for a **declaration** — an artifact that says *"the terminal predicate is X"*. The chain contains no such artifact. What it contains is a **question asked and answered**: `PHASE3:§F.1` asks *"Is unconditional implementation readiness achievable?"*, distinguishes two readings, and answers both. A definition given by *application* rather than by *declaration* is invisible to a search for declarations, and both phases were searching for the wrong shape of object. `PHASE4:§0.2` — which anticipates the confusion explicitly and says the two answers *"do not conflict; they answer different questions"* — is the sentence either phase would have needed to read.

**[INFERRED] What the later phases nonetheless established, and it is not small.** Phase 3 fixed the predicate and returned the verdict. It did **not** establish how much is reachable **short of** unconditional readiness. Phases 4–8 mapped exactly that: `READY-FOR-EXECUTION` reachable under 12 of 12 models with 0 mutating runs (`PHASE4:§I.3`); `EXECUTION-AUTHORIZED` reachable, per-run and state-bound (`PHASE5:§K.4`); the 42-artifact transition package; 17 terminal states; 106 paths; 9 specification defects, all closable by determination. **The ceiling was fixed in Phase 3; the five phases after it measured everything underneath the ceiling.** That work stands undisturbed by this finding.

```
IS THE CHAIN UNDERDETERMINED ON U-M?                                   NO
    determined at ......................... PHASE3 §F.1 + §F.2 + §G.4
    affirmed at ........................... PHASE4 §0.2, §I.3
    computed to a verdict at .............. PHASE6 §11.1(b)
    mistakenly reopened at ................ PHASE7 §11.5
    mistakenly carried at ................. PHASE8 §5.3 Part 2, §8.G
    closed at ............................. here, by reading the record
```

---

## 9. The formal proof tree

Every node is classified. Every leaf cites an input document. No premise originates in this phase.

```
                    U-M : which reading defines "unconditional ready"?
                                        │
    ┌───────────────────────────────────┴───────────────────────────────────┐
    │  N1.  Is the term DEFINED anywhere in Phases 0-8?                     │
    │       YES.  PHASE3 §F.1 ("'Unconditional' admits two readings.        │
    │       Both are answered") and PHASE3 §G.4 (the answer block).         │
    │                                                        [MEASURED]     │
    │       => PHASE7 §11.5's clause "which no artifact in Phases 0-7       │
    │          makes" is FALSE.                              [DERIVED N1]   │
    └───────────────────────────────────┬───────────────────────────────────┘
                                        │
    ┌───────────────────────────────────┴───────────────────────────────────┐
    │  N2.  HOW does PHASE3 define it?                                      │
    │       By its DEFEATERS.  §G.4 lists three independent reasons,        │
    │       "none removable by any governance answer".  Reason 3 is         │
    │       residual survival.                               [MEASURED]     │
    └───────────────────────────────────┬───────────────────────────────────┘
                                        │
    ┌───────────────────────────────────┴───────────────────────────────────┐
    │  N3.  Are the three defeaters homogeneous in removability?            │
    │       NO.                                              [DERIVED]      │
    │         r1  A=A3 forced          -> removable by IMPLEMENTATION       │
    │         r2  UK-1, UK-2           -> removable by EXECUTION            │
    │         r3  RES-3, RES-4, R-7w   -> removable by NOTHING              │
    │       basis: PHASE3 §E.7 (all 12 identical)            [MEASURED]     │
    │              PHASE4 §G  (R-7w UNCHANGED by execution)  [MEASURED]     │
    │              PHASE6 §7.2 (a successful run enters none)[MEASURED]     │
    │              PHASE1 §R-7 (closure declined)            [MEASURED]     │
    └───────────────────────────────────┬───────────────────────────────────┘
                                        │
    ┌───────────────────────────────────┴───────────────────────────────────┐
    │  N4.  Does r3 survive governance + implementation + SUCCESSFUL        │
    │       execution?                                                       │
    │       YES.                                             [DERIVED N3]   │
    │       corroborated verbatim: PHASE3 §F.1 — Reading 2 "fails           │
    │       PERMANENTLY rather than pending a decision"      [MEASURED]     │
    │       and PHASE4 §0.2's diagram: EXECUTED column = 3 residuals        │
    │                                                        [MEASURED]     │
    └───────────────────────────────────┬───────────────────────────────────┘
                                        │
            ┌───────────────────────────┴───────────────────────────┐
            │                                                        │
  ┌─────────┴──────────────────────────┐      ┌────────────────────┴─────────┐
  │ N5. Is the ALTERNATIVE reading     │      │ N7. Is residual-freedom      │
  │     (outcome-freedom) attested     │      │     AFFIRMED downstream?     │
  │     anywhere in Phases 0-6?        │      │     YES, twice.  [MEASURED]  │
  │     NO.  Zero occurrences of the   │      │       PHASE4 §I.3 "remains   │
  │     predicate in PHASE5, PHASE6;   │      │         true and is carried  │
  │     all 20 predicate-uses in       │      │         into the target"     │
  │     PHASE2/3/4 adopt residual-     │      │       PHASE4 §0.2 "the two   │
  │     freedom.          [MEASURED]   │      │         answers DO NOT       │
  │     First appearance: PHASE7 §11.1 │      │         CONFLICT"            │
  └─────────┬──────────────────────────┘      │     and COMPUTED once:       │
            │                                  │       PHASE6 §11.1(b)        │
  ┌─────────┴──────────────────────────┐      │       residual-freedom =>    │
  │ N6. Is outcome-freedom             │      │       UNREACHABLE            │
  │     CONTRADICTED?                  │      └────────────────────┬─────────┘
  │     YES.               [DERIVED]   │                           │
  │     Under it, PHASE4 §0.2's        │                           │
  │     EXECUTED state IS uncondition- │                           │
  │     ally ready.  PHASE3 §G.4's     │                           │
  │     closing sentence + §F.1's      │                           │
  │     "permanently" deny it.         │                           │
  └─────────┬──────────────────────────┘                           │
            │                                                       │
            └───────────────────────┬───────────────────────────────┘
                                    │
    ┌───────────────────────────────┴───────────────────────────────────────┐
    │  N8.  U-M RESOLVES UNIQUELY TO RESIDUAL-FREEDOM.                      │
    │       [DERIVED from N1, N2, N4, N5, N6, N7]                           │
    │       attested 3x · affirmed 2x · computed 1x · retracted 0x ·        │
    │       alternative attested 0x and contradicted                        │
    └───────────────────────────────┬───────────────────────────────────────┘
                                    │
    ┌───────────────────────────────┴───────────────────────────────────────┐
    │  N9.  Under residual-freedom, is the satisfying set EMPTY?            │
    │       YES.                                             [DERIVED]      │
    │       π2 (PHASE3 §E.7) no model closes any residual                   │
    │       π3 (PHASE4 §G + PHASE6 §7.2) execution closes none              │
    │       π4 (PHASE1 §R-7) no authorized act closes R-7w                  │
    │       => R-7w present in every model, on every path                   │
    │       identical to PHASE8 §5.3 Lemmas 2-3                             │
    └───────────────────────────────┬───────────────────────────────────────┘
                                    │
    ┌───────────────────────────────┴───────────────────────────────────────┐
    │  N10. Is N9 invariant under closure of U-B…U-H, and under U-I?        │
    │       YES.                                             [DERIVED]      │
    │       No U-item proposes moving `writer` inside the authority, the    │
    │       unique remedy π4 names; PHASE8 §5.3 Lemmas 4-5.                 │
    │       => the entire closure programme is ORTHOGONAL to this result    │
    └───────────────────────────────┬───────────────────────────────────────┘
                                    │
    ┌───────────────────────────────┴───────────────────────────────────────┐
    │  N11. TERMINAL OUTCOME = B.  UNCONDITIONAL READY DOES NOT EXIST.      │
    │       [DERIVED from N8 + N9 + N10]                                    │
    │       and this is the content of PHASE3 §G.4, unretracted.            │
    └───────────────────────────────┬───────────────────────────────────────┘
                                    │
    ┌───────────────────────────────┴───────────────────────────────────────┐
    │  N12. VERDICT A — U-M resolved uniquely; terminal outcome determined. │
    │       [DERIVED from N8 + N11]                                         │
    └───────────────────────────────────────────────────────────────────────┘

  LEAF PREMISES USED ........................................ 10
      PHASE1 §R-7 · PHASE2 §G.4 · PHASE3 §E.7 · PHASE3 §F.1 · PHASE3 §F.2
      PHASE3 §G.4 · PHASE4 §0.2 · PHASE4 §G · PHASE4 §I.3 · PHASE6 §7.2
      (+ PHASE6 §11.1(b), corroborative rather than load-bearing)
  PREMISES ORIGINATING IN THIS PHASE ......................... 0
  NODES CLASSIFIED MEASURED .................................. 5   N1, N2, N5, N7, and
                                                                   the leaf set
  NODES CLASSIFIED DERIVED ................................... 7   N3, N4, N6, N8, N9,
                                                                   N10, N11, N12
  NODES CLASSIFIED INFERRED .................................. 0
      no node of the proof tree rests on a judgment exceeding
      deduction; the [INFERRED] tags in this document appear
      only in commentary (§4.4, §7.1, §8) and in no proof step
```

---

## 10. Terminal verdict

# **A. `U-M` resolved uniquely; terminal outcome determined.**

```
================================================================================
  U-M                        RESOLVED — residual-freedom
  basis                      PHASE3 §F.1, §F.2 and §G.4, attested by PHASE2 §G.4,
                             affirmed by PHASE4 §0.2 and §I.3, computed to a
                             verdict by PHASE6 §11.1(b), retracted nowhere.
                             PHASE3 §F.2 states it as a COUNT: 0 of 12 models
                             reach UNCONDITIONAL READY.
  the alternative            outcome-freedom — attested 0 times in Phases 0-6,
                             constructed at PHASE7 §11.1, CONTRADICTED by
                             PHASE3 §G.4 read with PHASE4 §0.2

  TERMINAL OUTCOME           B — UNCONDITIONAL READY DOES NOT EXIST

  established by             deduction from 10 leaf premises, all MEASURED,
                             none originating in this phase
  cost                       0 mutating runs · 0 permits · 0 register ·
                             0 governance selections · 0 of U-B…U-H closed
  new closure items          0
  closure items removed      1   (U-M)
================================================================================
```

**[INFERRED] Why this is not a disappointing answer.** Outcome B is a statement about a **definition**, not about the program's health. It says: *no reachable state has zero residuals*, and the residual that makes it so is `R-7w`, which `PHASE4:§G.3` measures as a property of the **failure** path that a successful run never enters. The program's reachable ceiling is unchanged and is exactly what `PHASE4:§0.2` draws — **0 blockers · 0 unknowns · 3 residuals**, with `GA-5` as the instrument that accepts them. What Phase 9 settles is that this ceiling should be **named honestly** rather than relabelled as unconditional readiness.

---

## 11. Corrections to Phases 7 and 8

Two corrections. Both are mine, both are to the same clause, and the second inherited the first.

| # | Claim | Correction | Consequence |
|---|---|---|---|
| **1** | `PHASE7:§11.5` — *"a determination this phase is constrained against making, and **which no artifact in Phases 0-7 makes**"* | **FALSE.** `PHASE3:§F.1`, **`§F.2`** and `§G.4` make it; `PHASE2:§G.4` anticipates it; `PHASE4:§0.2` and `§I.3` affirm it. **[MEASURED]** the predicate is used **17** times across Phases 2–4, every use adopts residual-freedom, and `PHASE3:§F.2` states the result as a **count**: *"reaching UNCONDITIONAL READY … 0 ← none of them"* | `PHASE7:§11`'s *"all three outcomes remain reachable"* becomes **Outcome B is determined**. `PHASE7:§11.5`'s *"BOTH READINGS ARE STATED. NEITHER IS PREFERRED"* is correct as a statement about Phase 7's own conduct and wrong as a statement about the chain |
| **2** | `PHASE8:§5.3` Part 2 and `§8.E`/`§8.G` — the terminal predicate is undefined, so Phase 9 must return C unless it first decides `U-M` | **The argument is valid and its premise is false.** It was taken from correction 1 without testing. `PHASE8:§8.G`'s *"exactly one proposition must Phase 9 decide"* is right about the cardinality and wrong about the status: Phase 9 must **read** it, not decide it | `PHASE8`'s minimum closure set `{U-M}` is correct in cardinality and its member is **already closed**. The minimum closure set for a terminal Phase 9 is therefore **∅** |

**[INFERRED] What both corrections leave standing.** Every measurement in Phase 7 and Phase 8 stands: the 106 paths, the 8/98 reversibility split, the three manifest classes of `U-B`, the set-identity of the anonymous and staged-new populations, the 10 lock states, `EV-25`'s absent producer, the 6-vs-39 remaining-proposition counts, the dependency graph, and the nine specification defects. What changes is one node's status — and because that node dominates the graph, its status changes the verdict.

**[INFERRED] The methodological lesson, recorded because the chain has recorded its others.** Phase 6 found 14 dependencies its predecessors missed; Phase 7 found 5 defects Phase 6 missed; Phase 8 found 4 propositions Phase 7 missed. Each of those was found by **looking harder at the source or at the artifacts**. This one was found by looking harder at **the chain's own earlier answers** — and it had been sitting in the answer block of Phase 3 for five phases. A chain that audits forward but not backward will re-open questions it has already closed.

---

## 12. Stop condition

- **Q1** — `U-M` stated verbatim from `PHASE8:§8.G`; its subject term defined in the chain at `PHASE3:§F.1` and `§G.4`. §2.
- **Q2** — **7** interpretations present or implied, collapsing to **2** candidates for the terminal predicate. §3.
- **Q3** — per-interpretation dependencies, A/B/C consequences and execution requirements tabulated; **3 of 7** require a run, **2 of 7** do not, **2** are not assertions of the predicate. §4.1.
- **Q4** — **residual-freedom dominates**, on attestation (3×), downstream affirmation (2×) and contradiction of the alternative. §4.2.
- **Q5** — **outcome-freedom is contradicted** by `PHASE3:§G.4` read with `PHASE4:§0.2`, `PHASE4:§G` and `PHASE6:§7.2`. §5.
- **Q6** — **NO.** Exactly one interpretation survives. §6.
- **Q7** — **Outcome B follows deductively** from 9 measured premises, none originating here. §7.
- **Q8** — **NO.** The chain has not been underdetermined on this point since `PHASE3:§G.4`. §8.
- **Verdict** — **A**. §10.
- **Proof tree** — 12 nodes, 10 leaf premises, 0 premises originating in this phase, 0 nodes resting on `[INFERRED]`. §9.

### 12.1 Constraint compliance

- **Read-only. No source modification. No mutating command.** Only the nine inputs were read; the only commands run were `shasum`, `git rev-parse`, `git status --porcelain`, `git ls-files --cached`, `ls`, `grep` and `sed`.
- **No governance recommendation.** None. §4.4 states the boundary: this phase reports the reading the record fixes and takes no position on which reading a governing party *ought* to adopt.
- **No new closure items.** **Zero** introduced; **one** removed.
- **No blocker search, no remediation, no governance proposal, no closure-set expansion.** None of the four appears.
- **Every assertion classified.** `[MEASURED]` / `[DERIVED]` / `[INFERRED]` applied throughout; the proof tree in §9 contains **no** `[INFERRED]` node.

**Non-mutation, verified at the open and the close:**

```
$ shasum -a 256 00-BOOK/DATA/id-ledger.json
8471e709b178a9a09909bca55f2e8eccb78161db8423026d1d26e4f35c41c20b        (unchanged)
$ git rev-parse --short HEAD                   -> 77798202              (unchanged)
$ git status --porcelain -- 00-BOOK/DATA 00-BOOK/REGISTRIES \
                            00-BOOK/CONTROL-TOWER 00-BOOK/PORTAL        (0 lines)
$ ls 00-BOOK/DATA/allocation-permits.json      -> No such file or directory
$ ls 00-BOOK/tools/.register.lock              -> No such file or directory
$ git ls-files --cached | wc -l                -> 6804                  (unchanged)
```

### 12.2 The terminal position

```
U-M ...................... RESOLVED — residual-freedom, from the record
TERMINAL OUTCOME ......... B — UNCONDITIONAL READY DOES NOT EXIST
                           (the content of PHASE3 §G.4, unretracted)

REACHABLE CEILING, unchanged and precisely known:
    0 blockers · 0 unknowns · 3 residuals          PHASE4 §0.2 EXECUTED column
    reachable under .................. 12 of 12 admissible models
    reachable only after ............. GA-1 … GA-9, IA-1 … IA-12,
                                       and two irreversible mutating runs
    the instrument that accepts the 3 residuals ......... GA-5

STILL OPEN, and untouched by this determination:
    open propositions ................ 45   (46 at PHASE8 §2.6, minus U-M)
    irreducible by any determination ..  2   UK-1, UK-2
    producible by no act available to
    this chain .......................  1   GA-7
    specification defects, all closable
    by determination .................  9   PHASE7 §14.5, PHASE8 §9.5

THE NEXT ACT IS UNCHANGED AND IS NOT AN ANALYSIS.
    It is GA-1 — a governance decision on the five closure axes —
    followed by implementation, versioning, Stage 0, and then GA-7.
    PHASE9 determines what the program may HONESTLY CLAIM at the end.
    It does not, and cannot, authorize the program to begin.
```

Phase 9 ends here. The determination chain is terminal.
