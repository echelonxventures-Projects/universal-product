# PHASE 8 — MINIMUM CLOSURE-SET DETERMINATION

| Field | Value |
|---|---|
| Question | If `U-B` … `U-H` are all closed exactly as Phase 7 contemplates, does any unresolved proposition remain that prevents final closure? |
| Answer | **YES — six remain in Phase 7's own scope, and thirty-nine across the chain.** Four of the five were never enumerated by any phase; one was enumerated by Phase 7 and then **excluded from its own closure set**. |
| Are `U-B…U-H` exhaustive? | **NO.** Four unresolved propositions sit outside the set, and three dependency leaks inside Phase 7 §10.4 require artifacts that are not U-items (`IA-12`, `O-3`, `GA-2`). |
| Are they minimal? | **NO.** Three of the seven — `U-D`, `U-F`, `U-H` — are partially or conditionally redundant. `U-D`'s completion half is closed by `U-C`'s own closure `CC-4`/`CC-5`; `U-F`'s first and fourth limbs are closed by `CC-2` and by `UK-1`; `U-H` arises under only **3 of the 7** `U-B` closure classes. |
| Are they sufficient? | **NO.** Sufficiency fails on two independent grounds: the three leaks above, and the fact that **the necessity of all seven is itself conditional on a proposition none of them contains** — `U-M`. |
| The decisive finding | **Phase 7 identified the proposition that decides the Phase-9 outcome, proved that it decides it, and then did not put it in the closure set.** `PHASE7:§11.5` — *"THE DECIDING FACTOR IS NOT EVIDENCE. It is which reading of 'unconditional ready' is adopted."* That proposition is `U-M`. It has **in-degree 0**, it **dominates every other node**, and under one of its two readings **none of `U-B…U-H` is required at all**. |
| Inputs | The nine named documents. `PHASE0-GOVERNANCE-BLOCKER-DETERMINATION.md` **does not exist** — see §0.1. |
| Method | **Documentary only.** No source file was read, no probe was executed, no measurement was taken. Every fact is cited to one of the nine inputs. This is the first phase in the chain that adds no measurement, and that is the constraint's instruction, not a limitation this phase chose. |
| Repository files modified | **NONE.** This document is the only addition. Ledger `sha256 8471e709…c20b`; HEAD `77798202`; four guard directories **0** dirty; register absent; lock absent; `git ls-files --cached` **6804** — verified at the open and the close. |

### 0.1 One input substitution, recorded before anything rests on it

The task names `PHASE0-GOVERNANCE-BLOCKER-DETERMINATION.md`. **That file does not exist.** The Phase-0 document every phase in this chain cites — `PHASE6:§2.1`, `PHASE7:§2.1`, `PHASE5:§0.1`, `PHASE3:§H`, `PHASE2:§0` — is `PHASE0-GOVERNANCE-INDEPENDENT-DETERMINATION.md`, and it is the document that determines the blocker set: it enumerates `E1-F1…F7`, `E2-F1…F7`, `E-3`, `E-4A`, partitions them 12/3 by remedy class, and names the four subordinate blocker reports (`PHASE0-E1`, `-E2`, `-E3`, `-E4A`). **That document is used here, and the substitution is recorded rather than assumed.** If a document under the named title exists elsewhere and differs, every count in §1 that derives from Phase 0 would need re-checking; nothing else in this determination would move, because §§2–7 rest on Phases 2–7.

### 0.2 Compliance with the stated constraints

| Constraint | Compliance |
|---|---|
| Read and use only the nine documents | **MET.** No source file read. No probe run. Every claim carries a citation to one of the nine. Where this phase re-uses a *measurement*, it cites the phase that took it, never the source. |
| Do not modify repository files | **MET.** This document only. Baseline re-verified at open and close. |
| Do not execute mutating commands | **MET.** The only commands run were `shasum`, `git rev-parse`, `git status --porcelain`, `git ls-files --cached` and `ls`, for the compliance check above. |
| Do not issue permits · do not run `register.sh` · do not run allocation workflows | **MET.** Zero invocations of any kind. |
| Do not select governance | **MET.** No axis assigned. §5 and §7 identify a determination that must be made and state both of its values without preferring either. `U-M` and `U-I` are named as open, not answered. |
| Determination only | The scope of §§1–7. |

---

## 1. Executive determination

### 1.1 The headline

```
================================================================================
  IF U-B … U-H ARE ALL CLOSED EXACTLY AS PHASE 7 CONTEMPLATES, DOES ANY
  UNRESOLVED PROPOSITION REMAIN THAT PREVENTS FINAL CLOSURE?          Y E S
================================================================================

  SIX remain inside Phase 7's own scope.  THIRTY-NINE across the chain.

  U-I   THE MODEL-SPACE READING — 12 models or 24.                 [NEW HERE]
        Deferred by PHASE2 §D.3, PHASE3 §A, PHASE5 §B.4 (as GA-4),
        PHASE6 and PHASE7.  Five deferrals.
        PHASE3 §A states the consequence in its own words: under the
        24-model reading the forced set CHANGES SHAPE — F-1's register
        producer is replaced by an admission-predicate rewrite — and
        "it is therefore NOT a superset relation, and the 12-model
        results below do not transfer unchanged."
        => U-B's entire analysis is register-based.  Under I-D there is
           no register.  ALL SEVEN of U-B's closure classes CB-1…CB-7
           are register-based and NONE of them applies.
        => {U-B…U-H} is exhaustive only CONDITIONAL on a declaration
           that no artifact in Phases 0-7 makes.

  U-J   EV-25 HAS NO PRODUCER — and it is not inside U-H.           [NEW HERE]
        PHASE7 §6.3 measured that ledger_authority.py contains ZERO
        print/logging statements, so nothing can witness that the lock
        was taken, that R-2's re-check ran, or that R-7's comparison ran.
        PHASE7 §10.4 then folded EV-25's closure into "U-H's scope".
        U-H is about the SENTINEL's accounting.  EV-25 is about RESIDUAL
        CONTROL activation.  They are disjoint.  The assignment is wrong,
        and it is why PHASE7's reduction proof appears to close a surface
        it does not close.
        => PHASE4 §G's claim that execution REDUCES RES-3 and RES-4 is
           unobtainable.  PHASE7 §12.8 noticed this and did not carry it
           into the closure set.

  U-K   NO TRUST RULE EXISTS FOR EVIDENCE.                          [NEW HERE]
        The chain fixes a trust anchor for the permit register — modifier
        R = R1, "presence in the register is sufficient", forced in all 12
        (PHASE2 §C.3, PHASE3 §A) — and fixes NONE for the four evidence
        items PHASE7 §6.1 classifies UNSAFE: EV-7, EV-17, EV-18, EV-26.
        UK-1 items 2 and 3 rest entirely on EV-17, a transcript.
        PHASE7 §10.4 dismissed this as "a property of transcripts, not an
        uncertainty."  The dismissal is sound ONLY under a single-operator
        threat model, which ledger_authority.py:490-497 states and which
        NO PHASE ADOPTS AS A PREMISE.

  U-M   THE TERMINAL-PREDICATE READING.                             [NEW HERE]
        Which of {outcome-freedom, residual-freedom} defines
        "unconditional ready" and EXECUTION-CERTIFIED.
        PHASE7 §11.5 IDENTIFIED THIS, PROVED IT DECIDES THE PHASE-9
        OUTCOME, AND DID NOT PUT IT IN THE CLOSURE SET:
           "THE DECIDING FACTOR IS NOT EVIDENCE.  It is which reading of
            'unconditional ready' is adopted — a determination this phase
            is constrained against making, and which no artifact in
            Phases 0-7 makes."
        It has IN-DEGREE 0.  It DOMINATES every other node.
        Under residual-freedom, NONE of U-B…U-H is required.

  + THREE DEPENDENCY LEAKS INSIDE PHASE7 §10.4 ITSELF.              [NEW HERE]
        Its surface-3 reduction requires IA-12, O-3 (under B2) and GA-2's
        answer on modifier T.  None is a U-item.  PHASE7 conceded GA-2 in
        a parenthesis — "it is one of PHASE2's existing 13 decisions, so
        it is not a NEW governance dependency" — which is true and does
        not make it closed.  A pre-existing open proposition is still open.

  ── THE THREE VERDICTS ─────────────────────────────────────────────────────

  EXHAUSTIVE ....... NO.  4 propositions outside the set + 3 leaks inside it.
  MINIMAL .......... NO.  3 of the 7 are partially or conditionally redundant.
  SUFFICIENT ....... NO.  And the failure is structural, not additive: the
                     NECESSITY of all seven is conditional on U-M, which is
                     not one of them.

  ── THE RESULT THAT MATTERS ────────────────────────────────────────────────

  THE MINIMUM CLOSURE SET FOR A TERMINAL PHASE 9 HAS CARDINALITY  1.

      It is { U-M }.

      Under U-M = residual-freedom, Outcome B follows DEDUCTIVELY from three
      premises already committed in PHASES 1, 3 and 4 — with zero runs, zero
      permits, zero governance selection, and NONE of U-B … U-H closed.
      Proof in §5.3.  No proper subset suffices, because the empty set leaves
      the terminal predicate undefined and an undefined predicate has no truth
      value.  Hence exactly 1.                                              ∎
================================================================================
```

### 1.2 The ten questions, one line each

| Q | Answer |
|---|---|
| **Q1 Inventory** | **60 identifiers** across Phases 0–7. **12 closed** (Phase 1), **48 open identifiers**, **46 distinct open propositions**. By primary class: 5 blocker · 3 residual · 2 unknown · 18 governance dependency · 5 definition gap · 5 evidence gap · 3 implementation gap · 2 authorization gap · 2 accounting gap · 3 closure gap. §2 |
| **Q2 Exhaustive?** | **NO.** 4 propositions outside the set (`U-I`, `U-J`, `U-K`, `U-M`), 3 dependency leaks inside Phase 7 §10.4, 1 unresolved item Phase 6 raised and no phase closed (the poisoned `permit_id`), and 1 under-enumerated surface (Phase 7 compared **5** terminal-state names; the chain defines **13**). §3 |
| **Q3 Necessity** | For **outcome-A closure**: 4 necessary (`U-B`, `U-C`, `U-E`, and `U-D`'s authorization half), 3 conditionally necessary (`U-D`-completion, `U-F`, `U-G`, `U-H`), **0 sufficient**, **0 both**. For **decidability closure**: **0 of 7 necessary** — all seven are dominated by `U-M`. §4 |
| **Q4 Dependency graph** | **18 nodes, 21 edges.** Two sources with in-degree 0: `U-M` and `U-I`. One isolated node: `U-J`. Two overlap relations that are not edges: `U-C ∩ U-D` and `U-C ∩ U-F`. Three edges leaving the set entirely: to `IA-12`, `O-3`, `GA-2`. §5.1 |
| **Q5 Minimum closure set** | **Cardinality 1** for a terminal Phase 9: `{U-M}`. Minimality proved by the empty-set argument; sufficiency proved by deduction from three committed measurements. For outcome A the minimum set is **not finite-and-closable** — it terminates at `U-A` and `GA-7`, neither of which any determination closes. §5 |
| **Q6 Terminal states** | **17**, unchanged in count and changed in composition: `T-1b` (the false success) becomes **unreachable**, and `T-1f` **splits in two** because closing `U-D` makes a previously-conflated pair distinguishable. **1** reaches 0 blockers ∧ 0 unknowns; **0** reach it falsely. Paths fall **106 → 66**. §6.1 |
| **Q7 Can A fail?** | **YES — five causes**, of which **two are closable by no determination**: `U-A` (16 of 17 terminal states are not `T-1a`) and `GA-7` (the authorization no phase in this chain can produce). §6.2 |
| **Q8 Can B be reached?** | **YES, and the seven closures are entirely orthogonal to it.** None of `U-B…U-H` touches `R-7w`, which is what B's proof rests on. B is reachable before the closures, after them, and independently of them. §6.3 |
| **Q9 Can C be reached?** | **YES, and it is the correct outcome for any Phase 9 that has not first decided `U-M`.** The unresolved proposition is exactly `U-M`, with `U-I` as a secondary. §6.4 |
| **Q10 Terminal Phase 9?** | **YES — provably, by one route, and the route requires no execution.** §7 |

### 1.3 What this phase checked and did not find

Recorded first, because a phase whose entire output is *"your predecessor missed five things"* owes an account of what it checked and found sound.

| Checked | Result |
|---|---|
| Is Phase 7's **106**-path count sound? | **YES.** Re-derived from Phase 7's own factors: 2 orderings × 6 run-A classes × 3 run-B classes = 36 base; the single `A✓B✓` combination per ordering expands by 3×3×2×2 = 36; 34 + 2×36 = 106. Phase 7's correction of Phase 6's 58 is arithmetically sound and its stated cause — `EV-22` omitted as a branch factor while `PHASE6:§8.1` counts `T-1f` — is verified against both documents. |
| Is Phase 7's **8/98** reversibility correction sound? | **YES.** 14 of each ordering's 18 base combinations land an allocation; the 4 that do not are `{A∅, A⊥, A⊘p, A⊘a} × B⊘`; × 2 orderings = 8, and none of the 8 expands. Phase 6's 28/30 does not decompose under Phase 6's own stated criterion. |
| Is Phase 7's **`EXECUTION-CERTIFIED(b)` = ∅** proof sound? | **YES, and it is the load-bearing proof of the whole chain.** All three premises are prior-phase measurements: `PHASE3:§E.7` (all 3 residuals invariant across all 12), `PHASE4:§G` + `PHASE6:§7.2` (`R-7w` is a failure-path property; 4 of `commit()`'s 8 refusal points enter it, a success enters none), `PHASE1:§R-7` (closing it was declined as out of scope). §5.3 rests on it. |
| Is `U-B`'s three-class partition sound? | **YES.** It follows from two facts each recorded twice: `history ∈ NON_ALLOCATION_KEYS` (`PHASE7:§2.3`, and `PHASE1:§R-5` which put it there), and the sentinel's **two** checks (`PHASE7:§4.1`, `PHASE05:§C.9` which specified the second). Phase 6's `C-1` covering only `M1` is a correct consequence. |
| Does Phase 7's *"no path produces a new blocker"* survive? | **YES**, now confirmed at a fourth resolution. `PHASE4:§H.4`, `PHASE6:§7.5` (58), `PHASE7:§9.5` (106), and §6.1 here (66 after closure). Four independent path-space cardinalities, one answer. |
| Does the chain's blocker arithmetic reconcile end to end? | **YES.** 15 (Phase 0) − 12 (Phase 1) = 3, + `RES-1` + `RES-2` (Phase 0.5 §F.4, derived not discovered) = **5**, which is `PHASE1:§6.2`, `PHASE2:§A.1`, `PHASE3:§G.1` and `PHASE6:§10.1` — four documents, one number, no drift. |
| Is `U-A` genuinely irreducible, or is it an artifact of the chain's caution? | **IRREDUCIBLE, and independently grounded.** `PHASE4` **P4-6** measured that `--plan` is absent from `ukbx.py` entirely, so `register.sh` phases 2, 3, 4 and 8 have **no dry-run mode**. That is a property of the tools, not of the chain's declination policy. Six phases declined execution; the seventh reason is mechanical and would hold even if none had. |

---

## 2. Complete unresolved-proposition inventory — Q1

### 2.0 Classification scheme

The ten classes the task names, defined so that each proposition lands in exactly one **primary** class. Secondary classes are recorded where a proposition genuinely spans two; the counts in §2.6 are over primary classes only.

| Class | Definition used here |
|---|---|
| **blocker** | Prevents a required operation from completing, or leaves a false claim standing in source. Must be closed. (`PHASE3:§E.0`) |
| **residual** | A bounded, known, accepted property, not closable within the current architecture without a change nobody has authorized. (`PHASE3:§E.0`) |
| **unknown** | A question whose answer is not established and cannot be established by any non-mutating act. (`PHASE3:§E.0`) |
| **governance dependency** | Satisfiable only by a decision on FD-1…FD-5 or on a modifier. |
| **definition gap** | A term is used load-bearingly and is undefined, or defined twice incompatibly. |
| **evidence gap** | An evidence item is unproducible, non-discriminating, or lacks a trust basis. |
| **implementation gap** | A named artifact or code path does not exist. |
| **authorization gap** | A write class or act has no authorization path, or an authorization is unattributable. |
| **accounting gap** | An authorization event cannot be tracked through issuance, consumption, invalidation, expiry, mismatch or replay. |
| **closure gap** | A closure claim rests on an unverified fact, an under-enumerated surface, or a conditioning proposition. |

### 2.1 Propositions from Phase 0 and Phase 0.5 — the original defect set

| ID | Proposition | Primary class | Status | Source |
|---|---|---|---|---|
| **P-01** | `E1-F1` TOCTOU verification → write | blocker | **CLOSED** — `R-2` | `PHASE0:§2.2`; `PHASE1:§6.1` |
| **P-02** | `E1-F2` no concurrency control | blocker | **CLOSED** — `R-3` | as above |
| **P-03** | `E1-F4` record bodies unchecked | blocker | **CLOSED** — `R-4` | as above |
| **P-04** | `E1-F5` `history` unclassified, erasure unrefused | blocker | **CLOSED** — `R-5` | as above |
| **P-05** | `E1-F6` minting arithmetic vs verification read | blocker | **CLOSED** — `R-6` | as above |
| **P-06** | `E1-F7` `raw_before` unreconciled | blocker | **CLOSED** — `R-1` | as above |
| **P-07** | `E2-F1` divergent writer | blocker | **CLOSED** — `R-7` | as above |
| **P-08** | `E2-F2` silent writer | blocker | **CLOSED** — `R-7` | as above |
| **P-09** | `E2-F3` `bytes_changed` unenforced, unrendered | blocker | **CLOSED** — `R-8` | as above |
| **P-10** | `E2-F4` `NO_ALLOCATION` permits mutation | blocker | **CLOSED** — `R-9` | as above |
| **P-11** | `E2-F5` `LEDGER-INV-01` lexically blind | blocker | **CLOSED** — `R-10` | as above |
| **P-12** | `E2-F6` serializer equivalence unproven | blocker | **CLOSED** — `R-11` | as above |
| **P-13** | `E1-F3` permit replay after ledger restore | **blocker** *(also governance dependency — FD-2, FD-3′)* | **OPEN** | `PHASE0:§5`; `PHASE1:§6.2`; `PHASE2:§A.1` |
| **P-14** | `E-3` `UGA-INV-10` tautology — `audited ≡ set(by_object.keys())` | **blocker** *(also governance dependency — FD-5)* | **OPEN** | `PHASE0:§2.4`; `PHASE2:§A.1` |
| **P-15** | `E-4A` no permit issuance path — 4 of 5 operations MISSING | **blocker** *(also implementation gap, governance dependency)* | **OPEN — a total block on every ledger write** | `PHASE0:§2.5`; `PHASE2:§A.3` |
| **P-16** | `RES-1` a permit binds a six-field projection, not the document | **blocker** *(also governance dependency — FD-2)* | **OPEN** | `PHASE05:§F.4`; `PHASE2:§A.1` |
| **P-17** | `RES-2` empty-manifest permits not refused, contra `:519` | **blocker** *(also governance dependency — FD-2)* | **OPEN** | `PHASE05:§F.4`; `PHASE2:§A.1` |
| **P-18** | `RES-3` MW-3 read-to-lock window, bounded not closed | **residual** | **OPEN-ACCEPTED**, pending `GA-5` | `PHASE05:§F.4`; `PHASE3:§E.1` |
| **P-19** | `RES-4` `flock` advisory and filesystem-dependent | **residual** | **OPEN-ACCEPTED**, pending `GA-5` | `PHASE05:§F.4`; `PHASE3:§E.2` |
| **P-20** | `R-7w` post-hoc detection window `:893`→`:921` | **residual** | **OPEN-ACCEPTED**, pending `GA-5`. **Closable by no admissible model** | `PHASE1:§R-7`; `PHASE3:§E.3`, `§E.7` |

### 2.2 Propositions from Phase 2 — the governance layer

| ID | Proposition | Primary class | Status | Source |
|---|---|---|---|---|
| **P-21** | `FD-1` WHO may authorize | governance dependency | **OPEN** — provably vacuous in effect (`M1`), still required for specification completeness → `GA-2` | `PHASE2:§0`, `§C.1`, `§E.4` |
| **P-22** | `FD-2` WHAT an authorization means | governance dependency | **OPEN** — the load-bearing root; 3 of 5 blockers resolve here → `GA-1` axes `A`, `B`, `D` | `PHASE2:§B.1` |
| **P-23** | `FD-3′` WHEN an authorization expires | governance dependency | **OPEN** → `GA-1` + modifier `T` | `PHASE2:§0`, `§C.1 M3/M4` |
| **P-24** | `FD-4` WHICH AUTHORITY owns the ledger | governance dependency | **OPEN** — provably vacuous (`M2`) → `GA-2` | `PHASE2:§C.1` |
| **P-25** | `FD-5` WHICH DOMAIN RULE — mutation, audit event | governance dependency | **OPEN** → `GA-1` axis `Aud` | `PHASE2:§0` |
| **P-26** | **The 12-vs-24 model-space reading** — does `I-D`'s `NB-6` count as a blocker? | **closure gap** *(also governance dependency)* | **OPEN — deferred FIVE times.** `= U-I`, §3.2 | `PHASE2:§D.3`; `PHASE3:§A`; `PHASE5:§B.4`; `PHASE6`; `PHASE7` |
| **P-27** | Modifier `R` — register trust | governance dependency | **OPEN** → `GA-3`. `R1` forced in all 12 (`R2` → `NB-2`) | `PHASE2:§C.3`; `PHASE3:§A` |
| **P-28** | **Modifier `T` — expiry instant** | **accounting gap** *(also governance dependency)* | **OPEN → `GA-2`. Required by Phase 7's own reduction proof and absent from its closure set.** §3.4 | `PHASE2:§C.3`, `§E.1`; `PHASE7:§7.2`, `§10.4` |
| **P-29** | `B2a` / `B2b` — use-record location | governance dependency | **OPEN** → `GA-2`. Changes `R-B`'s rollback scope | `PHASE2:§E.1`; `PHASE5:§B.2` |
| **P-30** | The `Aud1` pair selection among 6 sub-variants | governance dependency | **OPEN** → `GA-2` | `PHASE2:§C.2`, `§E.1` |
| **P-31** | The `I-R` issuance mechanism among 3 sub-variants; the bounded-reuse threshold `n` | governance dependency | **OPEN** → `GA-2`. Provably closure-redundant (`M5`, `M4`) | `PHASE2:§E.1`, `§E.4` |

### 2.3 Propositions from Phases 3–5 — unknowns, artifacts, sequencing

| ID | Proposition | Primary class | Status | Source |
|---|---|---|---|---|
| **P-32** | `UK-1` `register.sh` end-to-end completion — **6** components | **unknown** | **OPEN — irreducible.** Not closable by any of the 12 models; not dischargeable without a mutating run | `PHASE3:§E.4`; `PHASE4:§I.1`; `PHASE6:§9.1` |
| **P-33** | `UK-2` post-mint clearance and gate greenness — **4** components | **unknown** | **OPEN — irreducible.** Item 2 alone is resolvable negatively from a partial path | `PHASE3:§E.5`; `PHASE4:§I.2`; `PHASE6:§9.2` |
| **P-34** | `GA-1` closure-model selection record | governance dependency | **OPEN.** The first act; task content undefined without it | `PHASE5:§B.1` |
| **P-35** | `GA-2` redundant-decision completion record — **8** answers | governance dependency | **OPEN.** Carries `P-21`, `P-24`, `P-27`…`P-31` | `PHASE5:§B.2` |
| **P-36** | `GA-3` zero-new-blocker attestation | governance dependency | **OPEN** | `PHASE5:§B.3` |
| **P-37** | `GA-4` model-space reading declaration | governance dependency | **OPEN — the artifact form of `P-26`** | `PHASE5:§B.4` |
| **P-38** | `GA-5` residual acceptance instrument (`RES-3`, `RES-4`, `R-7w`) | governance dependency | **OPEN.** Carries `P-18`, `P-19`, `P-20` | `PHASE5:§B.5` |
| **P-39** | `GA-6` unknown acknowledgment + closure-evidence adoption | governance dependency | **OPEN.** Must be adopted **before** the runs or the runs cannot fail | `PHASE5:§B.6` |
| **P-40** | **`GA-7` irreversible-mutation authorization** | governance dependency | **OPEN — and the one artifact no phase of this chain can produce for itself.** Absence stopped seven consecutive phases | `PHASE5:§B.7`, `§K.4`; `PHASE7:§14.5` |
| **P-41** | `GA-8` rollback authorization + `reset`-class prohibition | governance dependency | **OPEN** | `PHASE5:§B.8` |
| **P-42** | `GA-9` axis-parameterized condition record | governance dependency | **OPEN.** Phase 6 adds a 6th item; Phase 7 adds a 4th content item | `PHASE5:§B.9`; `PHASE6:§6.9`; `PHASE7:§4.4` |
| **P-43** | `IA-1 … IA-11` — 11 implementation artifacts carrying 17–20 tasks | **implementation gap** | **OPEN.** 3 new files, 8 modifications, **0** migration | `PHASE5:§C.1`, `§J.2` |
| **P-44** | `IA-C1` / `IA-C2` — the two pre-gate versioning acts | **implementation gap** | **OPEN.** Minimum states measured and asymmetric: staged vs committed | `PHASE5:§C.2`, `§C.3` |

### 2.4 Propositions from Phase 6

| ID | Proposition | Primary class | Status | Source |
|---|---|---|---|---|
| **P-45** | **`IA-12`** issuer specification record — actor literals + 3 elections | **implementation gap** *(also authorization gap)* | **OPEN. Required by Phase 7's reduction proof and absent from its closure set.** §3.4 | `PHASE6:§3.5`; `PHASE7:§10.4` |
| **P-46** | `EV-1` unproducible by the command `PHASE4:§D.1` names | **evidence gap** | **OPEN.** The correction was available in `PHASE05:§E.0` and lost between Phase 0.5 and Phase 4 | `PHASE6:§6.11` |
| **P-47** | **`U-B`** — the second `register.sh` run is unauthorizable | **authorization gap** | **OPEN.** 3 manifest classes; 7 closure classes; specification-, implementation- **and** model-dependent | `PHASE6:§3.6`; `PHASE7:§4` |
| **P-48** | **`U-C`** — execution completion can be falsely reported | **evidence gap** *(also definition gap)* | **OPEN.** 4 false-positive channels; 6 closure classes, all governance-independent | `PHASE6:§6.6`; `PHASE7:§5` |
| **P-49** | **A poisoned `permit_id` is permanently unusable and no rollback repairs it** | **accounting gap** *(also authorization gap)* | **OPEN — and closed by NO `U`-item.** `PHASE6:§8.4` calls it *"the only hidden damage that no rollback procedure addresses"*; `PHASE7:§9.3` path kind 9 restates it; neither assigns it a closure. §3.5 | `PHASE6:§6.13`, `§8.4`; `PHASE7:§9.3` |
| **P-50** | `EXECUTION-CERTIFIED` is undefined by every artifact in the chain | **definition gap** | **OPEN — the child of `U-M`.** Two readings; one **provably empty** | `PHASE6:§11.1`; `PHASE7:§8.4` |

### 2.5 Propositions from Phase 7, and the four this phase adds

| ID | Proposition | Primary class | Status | Source |
|---|---|---|---|---|
| **P-51** | **`U-D`** — the `by_object` population is index-derived; the anonymous set is set-identical to the staged-new set | **evidence gap** | **OPEN.** Partially redundant with `U-C` — §4.3 | `PHASE7:§5.3`, `§10.2` |
| **P-52** | **`U-E`** — two non-equivalent definitions of the terminal completion state | **definition gap** | **OPEN.** Worth exactly 4 completion paths | `PHASE7:§3.8`, `§9.4` |
| **P-53** | **`U-F`** — `REG-AUTO-001` §7 unconsumed, non-equivalent, stale, three-valued-reality-in-a-two-valued-law, §8 invariant violated by 9 | **definition gap** | **OPEN.** Partially redundant with `U-C` and `UK-1` — §4.3 | `PHASE7:§3.4`, `§10.2` |
| **P-54** | **`U-G`** — `EV-1` / `EV-24` bind a count, not a set | **evidence gap** | **OPEN.** Necessary only under `CD-30` — §4.2 | `PHASE7:§5.6`, `§10.2` |
| **P-55** | **`U-H`** — the sentinel path is unattributable; `CB-1` routes the third authorization event through it | **authorization gap** | **OPEN.** Arises under only 3 of 7 `U-B` closures — §4.2 | `PHASE7:§7.6`, `§10.2` |
| **P-56** | **`U-I`** — the model-space reading conditions the entire closure set | **closure gap** | **OPEN. NEW HERE.** `= P-26` promoted from a governance deferral to a closure conditioner. §3.2 | derived here from `PHASE2:§D.3` + `PHASE3:§A` + `PHASE7:§4.5` |
| **P-57** | **`U-J`** — `EV-25` has no producer anywhere; residual-control activation is unobservable | **evidence gap** | **OPEN. NEW HERE** as a set member. Phase 7 measured it and mis-assigned its closure to `U-H`. §3.3 | derived here from `PHASE7:§6.3`, `§10.4`, `§12.8` |
| **P-58** | **`U-K`** — no trust rule exists for evidence; `R = R1` covers the register and nothing covers the 4 UNSAFE items | **definition gap** *(also evidence gap)* | **OPEN. NEW HERE.** §3.6 | derived here from `PHASE2:§C.3` + `PHASE7:§6.1`, `§10.4` |
| **P-59** | **`U-M`** — the terminal-predicate reading: outcome-freedom or residual-freedom | **definition gap** | **OPEN. NEW HERE as a set member.** Phase 7 §11.5 identified it, proved it decisive, and excluded it. **In-degree 0. Dominates every node.** §3.7 | derived here from `PHASE7:§11.1`, `§11.5` |
| **P-60** | Phase 7 §10.4's surface-6 is under-enumerated — **5** terminal-state names compared, **13** defined in the chain | **closure gap** | **OPEN. NEW HERE.** §3.8 | derived here from `PHASE5:§0.4` (6) + `PHASE6:§11.1` (6, one shared) + `PHASE7:§8.1` (2 constructed) |

### 2.6 Inventory counts

```
PROPOSITION IDENTIFIERS ASSIGNED, PHASES 0-7 ...................... 60   P-01 … P-60
    CLOSED ......................................................... 12   P-01 … P-12, all by PHASE1
    OPEN, by identifier ............................................ 48   P-13 … P-60
    OPEN, DISTINCT PROPOSITIONS .................................... 46
        three identifiers name ONE proposition — P-26 (the PHASE2
        deferral), P-37 (its GA-4 artifact form) and P-56 (its role
        as a closure conditioner).  Counted once.

OPEN, BY PRIMARY CLASS  (one class per open identifier; sums to 48)
    blocker ......................................................... 5   P-13 … P-17
    residual ........................................................ 3   P-18, P-19, P-20
    unknown ......................................................... 2   P-32, P-33   (10 components)
    governance dependency .......................................... 18   P-21 … P-25, P-27,
                                                                          P-29 … P-31, P-34 … P-42
    definition gap .................................................. 5   P-50, P-52, P-53, P-58, P-59
    evidence gap .................................................... 5   P-46, P-48, P-51, P-54, P-57
    implementation gap .............................................. 3   P-43, P-44, P-45
    authorization gap ............................................... 2   P-47, P-55
    accounting gap .................................................. 2   P-28, P-49
    closure gap ..................................................... 3   P-26, P-56, P-60
                                                                    ─────
                                                                       48   ✓

OPEN, BY CLOSURE MECHANISM  (one entry per DISTINCT proposition; sums to 46)
    closable only by a governance DECISION .......................... 19
        the 5 FD roots · the 2 modifiers · 3 sub-variant decisions ·
        GA-1, GA-2, GA-3, GA-5, GA-6, GA-7, GA-8, GA-9 · and U-I,
        which is GA-4
    closable by DETERMINATION alone ................................. 10
        P-46 · P-48 · P-50 · P-51 · P-52 · P-53 · P-54 · P-58 · P-59 · P-60
    closable by an IMPLEMENTATION act ............................... 12
        the 5 artifact-level blockers (after governance) ·
        P-43 · P-44 · P-45 · P-47 · P-49 · P-55 · P-57
    closable by an EXECUTION act .................................... 2
        P-32 (UK-1) · P-33 (UK-2)
    ACCEPTED, never closed .......................................... 3
        P-18 · P-19 · P-20 — and PHASE3 §E.7 proves no model closes any
                                                                    ─────
                                                                       46   ✓

    OF THE 46, CLOSABLE BY NO ACT AVAILABLE TO THIS CHAIN ............ 1   P-40  (GA-7)
```

### 2.7 The three propositions that dominate the inventory

**[INFERRED]** Of the 46 distinct open propositions, three determine whether the rest matter.

| # | Proposition | Why it dominates |
|---|---|---|
| **1** | **`P-59` / `U-M`** — the terminal-predicate reading | Under residual-freedom, **44 of the 48 become irrelevant to the Phase-9 answer**, because Outcome B follows without them (§5.3). Under outcome-freedom, all 48 are on the critical path. One proposition swings 44. |
| **2** | **`P-40` / `GA-7`** — irreversible-mutation authorization | **No act available to this chain produces it.** `PHASE5:§K.4` and `PHASE7:§14.5` both state this. It gates every execution act, hence Outcome A entirely. |
| **3** | **`P-56` / `U-I`** — the model-space reading | **[MEASURED]** `PHASE3:§A`: under the 24-model reading *"the forced set changes shape … it is therefore not a superset relation, and the 12-model results below do not transfer unchanged."* Every count in Phases 3–7 — including Phase 7's 72 accounting cells and its 12-model quantifiers — is conditional on it. |

---

## 3. Exhaustiveness — Q2

### 3.1 The question, stated precisely

Phase 7 claims (`§10.4`) that closing `{U-B … U-H}` reduces the uncertainty set to exactly `{UK-1, UK-2}` over six enumerated surfaces. Exhaustiveness fails if **any** of the following holds: a proposition outside the set stands between `EXECUTION-AUTHORIZED` and a terminal proof; a closure inside the set requires an artifact outside it; or a surface is under-enumerated. **All three hold.**

### 3.2 `U-I` — the model-space reading. A closure claim resting on an unverified fact.

**Category: closure claim depending on an unverified fact.**

`PHASE2:§D.3` reports the admissible set as **12**, and immediately:

> *"Two counts are reported for zero-new-blocker closure because `I-D`'s NB-6 is a **dead-interface** blocker rather than an unauthorized-write blocker: **12** excluding `I-D`, **24** if `I-D`'s NB-6 is judged not to be a blocker. That judgment is itself a governance question and is therefore not made here; both numbers are given."*

`PHASE3:§A` inherits the decline **and states the consequence**:

> *"were the 24-model reading taken, the forced set in §D would **shrink by one** (`F-4` register.sh plumbing survives, but `F-1`'s register producer is replaced by an admission-predicate rewrite of `:714-721`) and gain **NB-6**. It is therefore **not a superset relation**, and the 12-model results below do not transfer to the 24-model reading unchanged."*

`PHASE5:§B.4` makes it `GA-4` and adds:

> *"every count in Phase 3, Phase 4 and this document is conditional on this declaration, and it has been deferred three times. **It cannot be deferred past the gate:** the transition package's own contents depend on it."*

**[INFERRED] The consequence for `U-B`, which no phase has drawn.** Under `I-D`:

- there is no permit register — `NB-6` is precisely *"`permit_id`, the register, `load_permit_register`, and the three `--permit` CLI flags lose their referents"* (`PHASE2:§C.9`);
- authorization is a **rule** admitting a class of manifests, evaluated per write, creating and consuming nothing (`PHASE2:§C.5`);
- therefore **the re-run's three manifest classes `M1`/`M2`/`M3` are classes of a register-based permit check that does not exist**, and Phase 7's seven closure classes `CB-1 … CB-7` — every one of which manipulates a permit, the register, or the sentinel — **have no referent**.

```
U-B's SEVEN CLOSURE CLASSES UNDER I-D

  CB-1  dispatch NO_ALLOCATION or a permit_id at the call site .... no permit_id exists
  CB-2  issue a third permit ..................................... no register exists
  CB-3  widen the sentinel's admissible domain ................... the sentinel is the
                                                                   admission rule itself
  CB-4  close by precondition (freeze the corpus) ................ SURVIVES
  CB-5  redefine EV-23 as a read-only measurement ................ SURVIVES
  CB-6  retire UK-1 item 5 ....................................... SURVIVES
  CB-7  give the re-run a non-mutating mode ...................... SURVIVES

  SURVIVING: 4 of 7 — and all four are the closures that DISSOLVE the
  problem rather than authorize the re-run.  Every closure that AUTHORIZES
  the re-run is register-based and vanishes.
```

**[INFERRED] Verdict.** `{U-B … U-H}` is exhaustive **conditional on the 12-model reading**. That reading has been deferred by five consecutive phases, each of which recorded that it must not be deferred further, and each of which deferred it. **`U-I` is therefore not merely a missing set member; it is the proposition on which the set's own well-formedness depends.**

### 3.3 `U-J` — `EV-25` has no producer, and Phase 7 assigned it to the wrong parent

**Category: dependency leak.**

`PHASE7:§6.3` establishes, by measurement:

> *"`ledger_authority.py` contains **ZERO** `print`, `logging` or `logger` statements. … A successful `commit()` and a `commit()` in which all three controls were removed produce **byte-identical operator output**. … `EV-25` is unproducible **at all**, not merely by its named method."*

`PHASE7:§10.4` surface 2 then writes:

> *"**`EV-25` remains UNPROVEN** — and it is not an unknown, it is an **absent producer**, so its closure is an implementation act inside `U-H`'s scope."*

**[INFERRED] The assignment is wrong, and the error is not cosmetic.** `U-H` is defined at `PHASE7:§7.6` as: *"The sentinel authorization path performs **no actor binding**, allocates **no `permit_id`**, and writes **no register entry**."* Its closure, stated in the same section, is: *"capture the re-run's `commit()` report; `UK-1` item 6 already requires it."*

Capturing the `commit()` report produces `authorization` and `bytes_changed`. It does **not** produce evidence that `_ledger_lock` was taken, that R-2's pre-write re-check ran, or that R-7's document comparison ran — which is what `EV-25` requires (`PHASE5:§D.3`). **The two are disjoint. Closing `U-H` closes none of `EV-25`.**

**[INFERRED] What the leak costs.** `PHASE4:§G` records `RES-3` **REDUCED** and `RES-4` **REDUCED** by execution. `PHASE7:§12.8` noticed the consequence:

> *"that reduction is evidenced by `EV-25` alone, and `EV-25` has no producer. So 'reduced' is a prediction the program cannot currently confirm."*

— and did not carry it into the closure set. So Phase 7's own §12.8 contains the refutation of Phase 7's own §10.4 surface 2. **`U-J` is the missing set member.**

**Scope, stated fairly.** `U-J` is **not** on the critical path to any of A/B/C. Under outcome-freedom the residuals are accepted, not reduced; under residual-freedom they must be **closed**, which reduction would not achieve either. `U-J` therefore changes the *characterization* of the terminal state — from *"3 residuals, 2 reduced"* to *"3 residuals, reduction unverifiable"* — and changes no outcome. It is a real unresolved proposition with **zero dependency edges into the closure set**, which is exactly why it could be mis-assigned without the error surfacing.

### 3.4 The three dependency leaks inside Phase 7 §10.4

**Category: closure claims depending on artifacts outside the set.**

`PHASE7:§10.4` surface 3 reads, verbatim:

> *"`IA-12` moves issuance and mismatch from PARTIAL to COMPLETE (12 + 12 cells); `O-3` moves `B2` consumption (6 cells); `GA-2`'s answer on modifier `T` moves expiry from AMBIGUOUS to COMPLETE (12 cells); `U-H` moves sentinel replay from UNDEFINED. **72 of 72 COMPLETE.** Note that `GA-2` is **[GOV-REQ]** — but it is one of `PHASE2`'s existing 13 decisions, so it is **not a new** governance dependency."*

| Leak | Artifact | Is it a `U`-item? | Phase 7's treatment | Assessment |
|---|---|---|---|---|
| **1** | **`IA-12`** — the issuer specification record | **NO.** A Phase 6 implementation artifact (`P-45`) | Named and not excused | **A genuine leak.** Without it no permit is constructible at all (`PHASE6:§5.6` puts it in the 6-artifact minimum to execute one run), so it gates `U-B`'s closure in classes `M2` and `M3` as well as the accounting surface |
| **2** | **`O-3`** — record permit consumption under the existing lock | **NO.** A Phase 3 conditional task, `B2` only (`PHASE3:§C.0`) | Named and not excused | **A genuine leak, in 6 of 12 models.** `PHASE7:§7.3` establishes that `B2`'s consumption accounting is complete *"at `O-3`, and not before"* |
| **3** | **`GA-2`** / modifier `T` | **NO.** A governance decision (`P-28`) | *"not a **new** governance dependency"* | **The excuse is true and irrelevant.** A pre-existing open proposition is still open. `PHASE7:§7.2` establishes expiry is **AMBIGUOUS in all 12 models** because `T` is free and `expires_at` has no producer. 12 of the 72 cells cannot reach COMPLETE without a governance answer |

**[INFERRED] Verdict.** Phase 7's reduction to `{UK-1, UK-2}` is not a consequence of closing `{U-B … U-H}`. It is a consequence of closing `{U-B … U-H} ∪ {IA-12, O-3, GA-2}`. **The seven are not sufficient, and the insufficiency is stated inside Phase 7's own proof.**

### 3.5 `P-49` — the poisoned `permit_id`, raised twice and closed by nothing

**Category: a proposition referenced but never resolved.**

`PHASE6:§6.13` establishes the mechanism and `PHASE6:§8.4` classifies it:

> *"a reused `permit_id` … becomes **permanently unusable**, and no amount of re-issuance recovers it. … **Not named in any prior phase**, and not repaired by `R-A`, `R-B`, `R-C` or `R-D`. … the third is new and is the only hidden damage that **no rollback procedure addresses**."*

`PHASE7:§9.3`, path kind 9, restates it and adds *"No rollback procedure repairs it"* and *"`R-D` is the one procedure that can create damage it cannot undo."*

**[INFERRED]** Two phases raised it; neither assigned it a closure; it is in no `U`-item. `PHASE6:§6.13` states the requirement — *"`IA-12` must fix the `permit_id` allocation rule, and it must be collision-free across issuance, lapse, re-issuance and rollback"* — so its closure lives inside `IA-12`, which is leak 1 of §3.4. **It is therefore a fourth reason the seven are insufficient, and it compounds the first leak rather than adding an independent one.**

### 3.6 `U-K` — the chain has a trust rule for permits and none for evidence

**Category: unstated assumption.**

`PHASE7:§6.1` classifies four evidence items **UNSAFE**, on the ground that each is *"a TRANSCRIPT or a GITIGNORED LOG — forgeable and replayable, with no binding to the run it describes"*: `EV-7`, `EV-17`, `EV-18`, `EV-26`. `PHASE7:§6.4` adds that `EV-7` and `EV-26` *"are the ONLY evidence that survives a full tracked rollback, and they are in this class."* `UK-1` items 2 and 3 rest on `EV-17` (`PHASE4:§I.1`).

`PHASE7:§10.4` surface 2 dismisses them:

> *"The 4 UNSAFE items … remain forgeable — **[INFERRED]** and that is a *property of transcripts*, not an uncertainty: nothing about them is unknown."*

**[INFERRED] The dismissal is sound, and it is sound only under a premise no phase states.** The chain does fix a trust anchor, and it fixes it for exactly one artifact: modifier **`R = R1`**, *"presence in the register is sufficient"*, forced in all 12 because `R2` requires *"a trust anchor the repository does not have"* (`PHASE2:§C.3`; `PHASE3:§A`). `R1` is a rule about the **permit register**. It says nothing about stdout transcripts, and `EV-17` is not in the register.

**[INFERRED]** So the chain's position is: *the permit register is trusted because a single operator issues and executes* — which `PHASE2:§C.1` `M1` proves is the operative model, since `_verify_permit` reads no `issuer` and no `signature`, making issuer identity mechanically undetectable — *and the transcripts are trusted because nobody says otherwise.* The first is a determination with a recorded basis. The second is an assumption.

**Verdict.** `U-K` is a definition gap: **the chain must state the trust rule under which an unbound transcript is admissible evidence for retiring an unknown, or must require that `UK-1` items 2–3 be re-derivable from committed artifacts.** It is closable by one determination and it is not in `{U-B … U-H}`.

### 3.7 `U-M` — the proposition Phase 7 proved decisive and then excluded

**Category: hidden precondition. The most consequential finding of this phase.**

`PHASE7:§11.1` states the two readings:

| Reading | *"Unconditional ready"* means |
|---|---|
| **(i) outcome-freedom** | 0 blockers ∧ 0 unknowns, with the 3 residuals **accepted** under `GA-5` |
| **(ii) residual-freedom** | 0 blockers ∧ 0 unknowns ∧ **0 residuals** |

`PHASE7:§11.5` then states, in a display block:

> *"THE DECIDING FACTOR IS NOT EVIDENCE. It is which reading of 'unconditional ready' is adopted — a determination this phase is constrained against making, and which **no artifact in Phases 0-7 makes**. Under reading (ii) the answer is B and costs nothing. Under reading (i) the answer is A or C and costs two irreversible mutating runs."*

**[INFERRED]** Phase 7 therefore established three things about this proposition — that it is open, that no artifact resolves it, and that it **determines the Phase-9 outcome** — and then did not list it among the items whose closure is required. `PHASE7:§10.2` enumerates `U-D … U-H` and stops. `PHASE7:§10.4` surface 6 mentions its child (`EXECUTION-CERTIFIED`'s two readings) and disposes of it as *"a determination outstanding, not an uncertainty"*.

**[INFERRED] That disposal is the error.** A determination outstanding is precisely an unresolved proposition. The distinction Phase 7 draws — between an *uncertainty* (something unknown) and a *determination outstanding* (something undecided) — is real and does not exempt the latter from a closure set. The task the closure set exists to serve is *"can Phase 9 be terminal"*, and Phase 7's own §11.5 proves that this undecided item is the one that answers it.

**[INFERRED] `U-M` is not merely a missing member. It is the graph's dominating node** (§5.1), and §5.3 proves that under one of its two values it is a **sufficient** closure set on its own.

### 3.8 `P-60` — Phase 7's surface 6 is under-enumerated

**Category: closure claim resting on an under-enumerated surface.**

`PHASE7:§10.4` proves exhaustiveness over six surfaces, the sixth being *"Terminal-state names (§8) — cardinality **5**"*. The chain defines **13**:

| Source | Names defined |
|---|---|
| `PHASE5:§0.4` | `NOT-AUTHORIZABLE`, `AUTHORIZATION-WITHHELD`, `EXECUTION-AUTHORIZED`, `AUTHORIZATION-LAPSED`, `AUTHORIZATION-CONSUMED`, `EXECUTION-COMPLETE` — **6** |
| `PHASE6:§11.1` | `NOT READY`, `READY-CONDITIONAL-ON-GOVERNANCE-SELECTION`, `READY-FOR-EXECUTION`, `EXECUTION-AUTHORIZED`, `EXECUTION-COMPLETED`, `EXECUTION-CERTIFIED` — **6**, sharing `EXECUTION-AUTHORIZED` |
| `PHASE7:§8.2` | `EXECUTION-SUCCESSFUL`, `EXECUTION-VERIFIED` — **2**, constructed |
| | **union = 6 + 6 − 1 + 2 = 13** |

**[INFERRED]** Phase 7 compared the **5** the Phase-7 task named. Eight further names are defined in the chain and were not checked for the same defects Phase 7 found in the five — two incompatible definitions (`EXECUTION-COMPLETE` vs `EXECUTION-COMPLETED`) and one undefined term (`EXECUTION-CERTIFIED`). **The surface-6 exhaustiveness claim covers 38% of the surface it names.**

**Scope, stated fairly.** Six of the eight unchecked names are authorization states with single, consistent definitions in `PHASE5:§0.4`, and Phase 6 and Phase 7 both use them without conflict. **[INFERRED]** The probability that a further conflict lurks there is low. But *low* is not *checked*, and the claim in `§10.4` is exhaustiveness.

### 3.9 Q2 verdict

```
ARE U-B … U-H EXHAUSTIVE?                                              NO

  PROPOSITIONS OUTSIDE THE SET THAT STAND BETWEEN
  EXECUTION-AUTHORIZED AND A TERMINAL PROOF ......................  4
      U-I   the model-space reading            closure gap      §3.2
      U-J   EV-25 has no producer              evidence gap     §3.3
      U-K   no trust rule for evidence         definition gap   §3.6
      U-M   the terminal-predicate reading     definition gap   §3.7

  CLOSURES INSIDE THE SET REQUIRING ARTIFACTS OUTSIDE IT ..........  3
      IA-12 · O-3 (B2 models) · GA-2 / modifier T               §3.4

  PROPOSITIONS RAISED BY A PRIOR PHASE AND CLOSED BY NO U-ITEM ....  1
      P-49  the poisoned permit_id  — folds into IA-12          §3.5

  SURFACES UNDER-ENUMERATED IN THE EXHAUSTIVENESS PROOF ...........  1
      surface 6: 5 of 13 terminal-state names                   §3.8

  BY Q2's REQUESTED CATEGORIES
      unstated assumptions ......................................  1   U-K
      dependency leaks ..........................................  4   U-J's mis-assignment,
                                                                       + the 3 of §3.4
      hidden preconditions ......................................  1   U-M
      closure claims on unverified facts ........................  2   U-I, surface 6
      propositions referenced but never resolved ................  1   P-49
                                                                 ─────
                                                                    9
```

---

## 4. `U-B` … `U-H` sufficiency analysis — Q3

### 4.1 "Final closure" needs a target before necessity has a truth value

**[INFERRED]** *Necessary for what?* admits two answers in this chain, and they give opposite results. Both are evaluated.

| Target | Definition |
|---|---|
| **FC-A — outcome-A closure** | Terminal state `T-1a` is reached genuinely: 0 blockers, 0 unknowns, every confirmation item truly satisfied, and the evidence sound. |
| **FC-D — decidability closure** | Phase 9 can return a determinate outcome among A / B / C, with proof. This is what the Phase-8 question actually asks, since Q10 asks whether Phase 9 can be **terminal**, not whether the program **succeeds**. |

### 4.2 Per-item determination

| Item | Necessary for **FC-A**? | Sufficient for **FC-A**? | Necessary for **FC-D**? | Verdict | Proof |
|---|---|---|---|---|---|
| **`U-B`** | **YES** | no | **NO** | **NECESSARY (FC-A only)** | Without it `EV-23` is unproducible in all three manifest classes with `IA-4` static (`PHASE7:§4.2`), so `UK-1` item 5 is unreachable, so `UK-1` stays open, so `T-1a`'s *"0 unknowns"* fails. Not sufficient: `PHASE7:§9.4` measures **0** completion-valid paths on the package as specified for a **second, independent** reason — `EV-25`. |
| **`U-C`** | **YES** | no | **NO** | **NECESSARY (FC-A only)** | Without it 4 false-positive channels are reachable (`PHASE7:§5.2`), so *"genuinely"* in FC-A's definition cannot be established. Not sufficient: closing `U-C` leaves `EV-23` unproducible, which is `U-B`. |
| **`U-D`** | **PARTIALLY — its authorization half only** | no | **NO** | **CONDITIONALLY NECESSARY** | **[INFERRED] `U-D` is not one proposition.** Its **completion half** — `EV-22` satisfiable by an index operation — is `FP-B`, which `PHASE7:§5.2` lists as a **`U-C` channel** and which `PHASE7:§5.6b` closes with `CC-4` and `CC-5`, both **`U-C` closures**. Its **authorization half** — `EV-14`'s measurand is not a property of any commit, so a `git add` of any file invalidates permit B on two bindings — is independent and necessary. See §4.3. |
| **`U-E`** | **YES** | no | **NO** | **NECESSARY (FC-A only)** | `FC-A` names *"0 unknowns"*. Under `CD-30` a state with `UK-2` open (`T-1f`) is COMPLETED; under `CD-28` it is not (`PHASE7:§3.8` pair 3, `§9.4`). Until one definition holds, *"0 unknowns"* is not a determinate predicate. |
| **`U-F`** | **PARTIALLY — limbs (b) and (c) only** | no | **NO** | **CONDITIONALLY NECESSARY** | `U-F` has four limbs (`PHASE7:§3.4`). **(a)** no vocabulary for *"did not run"* — closed by `CC-2`, a **`U-C`** closure. **(d)** the §8 invariant violated by 9 — discharged by run A retiring `UK-1`, i.e. by `UK-1`, not by a determination. Only **(b)** the 8-register-vs-10-phase non-equivalence and **(c)** the stale 6-phase table are independent. See §4.3. |
| **`U-G`** | **CONDITIONAL on `U-E`** | no | **NO** | **NEITHER, unconditionally** | `EV-24` is a conjunct of `CD-30` and **absent from `CD-28`** (`PHASE7:§3.5`). Under `CD-28`, `FC-A` does not read `EV-24` at all and `U-G` is irrelevant to it. `U-G`'s necessity is therefore a **function of `U-E`'s resolution** — an edge, not a member. |
| **`U-H`** | **CONDITIONAL on how `U-B` is closed** | no | **NO** | **NEITHER, unconditionally** | `U-H` arises only where the re-run's authorization routes through the sentinel. Over `PHASE7:§4.5`'s seven `U-B` closure classes: `CB-1` **yes**, `CB-3` **yes**, `CB-4` **yes**, `CB-2` **no** (a permit, not the sentinel), `CB-5` **no**, `CB-6` **no**, `CB-7` **no** (no re-run occurs). **3 of 7.** |

```
FOR FC-A (outcome-A closure)
    NECESSARY, unconditionally ....................................  3   U-B, U-C, U-E
    NECESSARY in part, redundant in part ..........................  2   U-D, U-F
    NECESSARY only conditionally on another item ..................  2   U-G (on U-E)
                                                                        U-H (on U-B's closure)
    SUFFICIENT ....................................................  0
    BOTH ..........................................................  0
    NEITHER, unconditionally ......................................  2   U-G, U-H

FOR FC-D (decidability closure — what Q10 actually asks)
    NECESSARY .....................................................  0 of 7
    SUFFICIENT ....................................................  0 of 7
    BOTH ..........................................................  0 of 7
    NEITHER ....................................................... 7 of 7

    [INFERRED] All seven are DOMINATED by U-M.  Under U-M = residual-freedom,
    Outcome B follows from three committed measurements and NONE of the seven
    is required — §5.3.  Under U-M = outcome-freedom, all seven become
    necessary but still insufficient, because FC-A additionally requires
    IA-12, O-3, GA-2, GA-1…GA-9, IA-1…IA-12, U-A and GA-7.
```

### 4.3 The two partial redundancies, proved

**`U-D` ∩ `U-C`.** Phase 7 lists `FP-B` — *"`EV-22` satisfied by an index state that is not the minted set"* — as one of **`U-C`'s four false-positive channels** (`§5.2`), and closes it with `CC-4` (*compare minted sets, not counts*) and `CC-5` (*freeze the index across `S-3` → `S-9`*), both of which `§5.6b` lists as **`U-C` closure classes**. Phase 7 then lists `U-D` separately at `§10.2` with `FP-B` as its leading symptom.

```
  U-D  =  { EV-22 satisfiable by an index operation }   <-- IS FP-B, a U-C channel,
                                                             closed by CC-4 / CC-5
       ∪  { EV-14's measurand is not a property of      <-- INDEPENDENT: this is an
            any commit; any `git add` invalidates            AUTHORIZATION fact about
            permit B on two bindings }                       permit B, not a completion
                                                             fact about EV-22

  => the set {U-C, U-D} DOUBLE-COUNTS the first conjunct.
```

**`U-F` ∩ `U-C` ∩ `UK-1`.** `U-F`'s limb (a) — *"no vocabulary for a transaction that did not run"* — is closed by `CC-2`, which `PHASE7:§5.6b` lists as a **`U-C`** closure and whose entry explicitly says *"`CD-19` (`REG-AUTO-001` §7) would need the matching third value, which is `U-F`"*. Phase 7 thus records the overlap in `U-C`'s own closure table and does not deduct it from `U-F`. Limb (d) — the §8 invariant violated by 9 — is `UK-1`'s population, retired by run A.

**[INFERRED] Verdict.** The set as stated is **not a partition**. It is minimal after re-partitioning into:

```
  U-C'  =  U-C ∪ (U-D's completion half) ∪ (U-F's limb a)
  U-D'  =  U-D's authorization half only        (EV-14 / permit-B invalidation)
  U-F'  =  U-F's limbs (b) and (c) only         (8-register vs 10-phase; the stale table)
```

### 4.4 Q3 verdict

```
IS ANY OF U-B … U-H SUFFICIENT FOR FINAL CLOSURE?                      NO
    0 of 7, under either target.

IS EACH NECESSARY?                                    NOT AS A FLAT SET
    unconditionally necessary for FC-A ............................  3   U-B, U-C, U-E
    necessary in part ............................................  2   U-D, U-F
    conditionally necessary ......................................  2   U-G, U-H
    necessary for FC-D ...........................................  0

THE STRUCTURAL RESULT
    Necessity is not a property of the seven.  It is a property of the
    pair (item, target), and the target is chosen by U-M — which is not
    one of the seven.  A closure set that does not contain the proposition
    fixing its own target cannot be shown necessary or sufficient for
    anything, and that is the precise sense in which {U-B … U-H} fails.
```

---

## 5. Dependency graph and minimum closure set — Q4, Q5

### 5.1 The graph

18 nodes. Edge `X → Y` reads *"Y depends on X"*: `Y` cannot be closed, or its necessity cannot be determined, until `X` is.

```
  ┌──────────────────────────── SOURCES (in-degree 0) ────────────────────────────┐
  │                                                                                │
  │   U-M  terminal-predicate reading            U-I  model-space reading (12|24)  │
  │   [definition gap · DOMINATES ALL]           [closure gap · conditions U-B]    │
  └───────┬────────────────────────────────────────────┬───────────────────────────┘
          │ relevance: selects the TARGET               │ well-formedness
          │ (FC-A vs FC-B), hence whether any           │ (does U-B's closure
          │ item below is needed at all                 │  space have referents?)
          │                                             │
    ┌─────┴──────────────────────────────┐        ┌─────┴──────┐
    ▼                                    ▼        ▼            ▼
  U-K                                  U-E      U-B ─────────► U-H
  evidence trust                    definition   authorization  (conditional:
  (UK-1 items 2-3                    ▲     │      gap            3 of 7 closures)
   rest on EV-17)                    │     │       ▲
                                     │     ▼       │
                                     │   U-G       │  IA-12 ──────┐
                                     │  (necessity │  (leak 1)    │
                                     │   only if    │              ▼
                                     │   CD-30)     └────────► accounting
                                     │                            surface
    U-C ══════ overlap ══════ U-D    │              O-3 ──────────► (B2 only)
     ║  (FP-B: CC-4/CC-5)      │     │             (leak 2)         ▲
     ║                          │     │                              │
     ╚═ overlap ═ U-F(a)        │     │             GA-2 / T ────────┘
        (CC-2)     │            │     │            (leak 3)
                   │            │     │
                   ▼            ▼     ▼
              U-F(d) ◄──── UK-1     UK-2          U-J  ◄── ISOLATED
              (§8 invariant                        (EV-25 has no producer;
               retired by run A)                    0 in-edges, 0 out-edges)
                   ▲                 ▲
                   └────── U-A ──────┘
                            ▲
                            │
                          GA-7  ── produced by NO act available to this chain
```

### 5.2 Every edge, with its proof

| # | Edge | Class | Proof |
|---|---|---|---|
| **1** | `U-M → U-B` | **direct (relevance)** | Under residual-freedom the target is FC-B, which `§5.3` proves requires nothing from `U-B`. `U-B`'s necessity is therefore a function of `U-M`'s value. `PHASE7:§11.5` |
| **2–7** | `U-M → U-C, U-D, U-E, U-F, U-G, U-H` | **direct (relevance)** | As edge 1; identical argument for each |
| **8** | `U-M → U-K` | **direct** | `U-K` matters only where an unknown is retired on transcript evidence. Under FC-B no unknown is retired. `PHASE7:§8.4`, `§11.2` |
| **9** | `U-I → U-B` | **direct** | Under `I-D` the register does not exist, so 3 of `U-B`'s 7 closure classes lose their referents (`§3.2`). `PHASE2:§C.9` `NB-6`; `PHASE3:§A` |
| **10** | `U-I → U-H` | **direct** | `U-H` is about the **sentinel**; under `I-D` admission is a rule and the sentinel's role changes. `PHASE2:§C.5` |
| **11** | `U-I → U-D, U-E, U-F, U-G, U-J, U-K` | **NO DEPENDENCY** | Each is definitional or evidential and reads no axis-`I` value. `U-D` is index-derived under every `I` (`PHASE7:§5.3`); `U-E` and `U-F` are documentary conflicts; `U-G` is a test-set predicate; `U-J` is an absent producer; `U-K` is a trust rule |
| **12** | `U-E → U-G` | **direct** | `EV-24` is a conjunct of `CD-30` and absent from `CD-28`. `PHASE7:§3.5` |
| **13** | `U-E → U-C` | **direct (sub-cause)** | `FP-C` — *"completion asserted with `UK-2` open"* — is one of `U-C`'s four channels and its sole cause is the `CD-28`/`CD-30` conflict. `PHASE7:§5.2` |
| **14** | `U-B → U-H` | **conditional direct** | `U-H` arises under `CB-1`, `CB-3`, `CB-4` and not under `CB-2`, `CB-5`, `CB-6`, `CB-7`. `PHASE7:§4.5`, `§7.6` |
| **15** | `IA-12 → U-B` | **direct** | Classes `M2` and `M3` require a constructible permit; `PHASE6:§5.6` places `IA-12` in the 6-artifact minimum to execute one run |
| **16** | `IA-12 → P-49` | **direct** | `PHASE6:§6.13`: *"`IA-12` must fix the `permit_id` allocation rule … collision-free across issuance, lapse, re-issuance and rollback"* |
| **17** | `GA-2 → accounting` | **direct** | Expiry is AMBIGUOUS in **all 12** models until modifier `T` is answered. `PHASE7:§7.2`, `§7.4` |
| **18** | `O-3 → accounting` | **direct, 6 of 12** | `B2` consumption is PARTIAL *"at `O-3`, and not before"*. `PHASE7:§7.3` |
| **19** | `GA-7 → U-A` | **direct** | No run occurs without the irreversible-mutation authorization. `PHASE5:§B.7`, `§K.4` |
| **20** | `U-A → UK-1`, `U-A → UK-2` | **direct** | `U-A` is the label for their pre-run unmeasurability. `PHASE6:§1.1`; `PHASE4` **P4-6** |
| **21** | `UK-1 → U-F(d)` | **direct, reversed** | `U-F`'s §8-invariant limb is discharged **by** run A, not by a determination. `PHASE7:§3.4` `CD-22` |
| — | `U-J → anything` | **NO DEPENDENCY, in either direction** | `U-J` has no in-edges and no out-edges: `EV-25` gates no completion condition, no authorization, and no unknown. `PHASE5:§D.3`; `PHASE7:§12.8`. **Its isolation is why the mis-assignment in `PHASE7:§10.4` did not surface** |
| — | `U-C ↔ U-D`, `U-C ↔ U-F(a)` | **OVERLAP, not dependency** | Set intersection, proved in `§4.3`. Neither precedes the other; both are closed by the same act |

```
NODES ............................................................ 18
EDGES ............................................................ 21
    direct ........................................................ 19
    conditional direct ............................................  1   U-B → U-H
    reversed (a U-item depending on an UNKNOWN) ...................  1   UK-1 → U-F(d)
NON-EDGES PROVED .................................................  7   U-I ↛ {U-D, U-E, U-F,
                                                                        U-G, U-J, U-K}, and
                                                                        U-J ↛ everything
OVERLAP RELATIONS (not edges) ....................................  2   U-C ∩ U-D, U-C ∩ U-F(a)
SOURCES (in-degree 0) ............................................  2   U-M, U-I
ISOLATED NODES ...................................................  1   U-J
SINKS THAT NO DETERMINATION CLOSES ...............................  3   U-A, UK-1, UK-2
NODES OUTSIDE {U-B…U-H} ON A PATH TO A TARGET ....................  8   U-M, U-I, U-J, U-K,
                                                                        IA-12, O-3, GA-2, GA-7
```

### 5.3 The minimum closure set for a terminal Phase 9 — cardinality 1

**Claim.** `{U-M}` is a minimum closure set for **FC-D**, and `|{U-M}| = 1`.

**Part 1 — sufficiency.** Assign `U-M` the value **residual-freedom**. Then *"unconditional ready"* means `0 blockers ∧ 0 unknowns ∧ 0 residuals`, and Outcome **B** — *UNCONDITIONAL READY DOES NOT EXIST* — follows deductively from three premises, each a measurement already committed in an input document:

| # | Premise | Source |
|---|---|---|
| **1** | `RES-3`, `RES-4` and `R-7w` are invariant across **all 12** admissible models; **no model closes any of them** | `PHASE3:§E.7` |
| **2** | Execution **reduces** `RES-3` and `RES-4` in evidence class and leaves `R-7w` **unchanged**, because `R-7w` is the window `:893`→`:921` that only a refusal traverses — exactly **4 of `commit()`'s 8** refusal points enter it and a successful run enters **none** | `PHASE4:§G`; `PHASE6:§7.2` |
| **3** | Closing `R-7w` requires moving serialization inside the authority, which was **declined** as *"a larger change than this phase covers"* | `PHASE1:§R-7` |

From 1 and 2: no admissible model and no execution outcome closes `R-7w`. From 3: no act within the chain's authorization closes it. Therefore the set of states satisfying `0 residuals` is **empty**, in every model and on every path. Therefore Outcome **B** holds, and Phase 9 is terminal. ∎

**[INFERRED]** The proof requires **no mutating run, no permit, no register, no governance selection on any of the five axes, and none of `U-B` … `U-H` closed.** `PHASE7:§8.4` supplies the identical argument one level down, for `EXECUTION-CERTIFIED(b) = ∅`, which is `U-M`'s child `P-50`.

**Part 2 — minimality.** No proper subset of `{U-M}` suffices. The only proper subset is `∅`. With `∅`, the terminal predicate is undefined; `PHASE7:§11.1` establishes that two non-equivalent readings are live and that *"no artifact in Phases 0-7"* selects one. A predicate that is undefined has no extension, so the sentence *"an unconditionally-ready state exists"* has **no truth value**, and neither Outcome A nor Outcome B is assertable. Phase 9 must then return **C**, which is not terminal. Hence `|minimum| ≥ 1`. With Part 1, `|minimum| = 1`. ∎

**Part 3 — the set is not unique, and the alternative is not available to this chain.** The other value of `U-M` — outcome-freedom — also yields terminality, but only through Outcome A, which requires `T-1a`, which requires both runs to succeed, which requires `GA-7`, *"the one artifact no phase of this chain can produce for itself"* (`PHASE5:§K.4`; `PHASE7:§14.5`). **[INFERRED]** So of the two closure sets that make Phase 9 terminal, exactly one is reachable by determination.

### 5.4 The minimum closure set for Outcome A — not finite-and-closable

**[INFERRED]** For **FC-A**, the minimum closure set is the union of every node on a path to `T-1a`:

```
  { U-M(→ outcome-freedom) }                                             1
∪ { U-I }                                                                1
∪ { U-B, U-C', U-D', U-E, U-F', U-G, U-H }   (re-partitioned, §4.3)      7
∪ { U-J, U-K }                                                           2
∪ { IA-12, O-3, GA-2 }                       (the three leaks, §3.4)     3
∪ { GA-1 … GA-9 }                            (GA-2 and GA-4 already
                                              counted above)             7
∪ { IA-1 … IA-11, IA-C1, IA-C2 }                                        13
∪ { UK-1, UK-2 }                             ◄── CLOSED BY NO DETERMINATION
∪ { GA-7 }                                   ◄── PRODUCED BY NO ACT
                                                 AVAILABLE TO THIS CHAIN
                                                                      ─────
                                          determinable subtotal .......  34
                                          undeterminable ..............   3
```

**[INFERRED]** The set is finite but **not closable by this chain**, on two independent grounds that no phase disputes: `UK-1` and `UK-2` are dischargeable only by an irreversible mutating run (`PHASE3:§F.5`, four consecutive declinations for one consistent reason), and `GA-7` is dischargeable only by a party outside the determination chain (`PHASE5:§B.7`, whose basis is the repository's own voice at `register.sh:150-153`).

### 5.5 Q4 / Q5 verdict

```
DEPENDENCY GRAPH ......................... 18 nodes · 21 edges · 7 proved non-edges
    sources (in-degree 0) .................  2   U-M, U-I
    isolated ..............................  1   U-J
    sinks closable by no determination ....  3   U-A, UK-1, UK-2
    nodes outside {U-B…U-H} on a path .....  8

MINIMUM CLOSURE SET FOR A TERMINAL PHASE 9
    cardinality ...........................  1
    the set ............................... { U-M }
    proof of sufficiency .................. §5.3 Part 1 — three committed measurements
    proof of minimality ................... §5.3 Part 2 — the empty set leaves the
                                            terminal predicate undefined, and an
                                            undefined predicate has no truth value
    proof that no proper subset suffices .. the only proper subset is ∅, excluded above
    cost .................................. 0 runs · 0 permits · 0 governance selection
                                            · 0 of U-B…U-H

MINIMUM CLOSURE SET FOR OUTCOME A
    cardinality ........................... 37
    determinable by this chain ............ 34
    NOT determinable ......................  3   UK-1, UK-2 (require a run)
                                                 GA-7      (requires a party outside
                                                            the chain)
    => OUTCOME A IS NOT REACHABLE BY DETERMINATION AT ALL.
```

---

## 6. Reachable-outcome analysis — Q6, Q7, Q8, Q9

**Assumption for this whole section, per the task:** `U-B` … `U-H` are closed **exactly as Phase 7 contemplates** — including Phase 7's assignment of `EV-25`'s closure to `U-H`, which §3.3 shows is wrong. Where that assignment changes an answer, it is flagged.

### 6.1 Q6 — every remaining reachable terminal state

**[INFERRED]** Start from `PHASE6:§8.1`'s **17** and apply the seven closures.

| # | State | Reached by | After the seven closures |
|---|---|---|---|
| **Y-1** | `A∅` — lock no-op | lock states B, D, F | **REMAINS.** `CC-2`/`CC-3` make it *distinguishable*, not unreachable. The lock can still be stale |
| **Y-2** | `A⊥` — lock corrupt, exit 1 | lock state G | **REMAINS**, now with a governance message under `CC-2` |
| **Y-3** | `A⊘p` — Phase 0 gate fails | — | REMAINS |
| **T-6** | `A⊘a ∧ B⊘` — both refused cleanly | — | REMAINS. Both permits still verify |
| **T-7** | `A✗ ∧ B⊘` | — | REMAINS |
| **T-8** | `A⊘a ∧ B✗` | — | REMAINS |
| **T-9** | `A✗ ∧ B✗` | — | REMAINS |
| **T-2** | `A✓ ∧ B⊘` | — | REMAINS. `UK-2` open |
| **T-3** | `A✓ ∧ B✗` | — | REMAINS |
| **T-4** | `A⊘a ∧ B✓` | — | REMAINS. `UK-1` open |
| **T-5** | `A✗ ∧ B✓` | — | REMAINS |
| **T-1a** | `A✓ ∧ B✓`, confirmation clean | — | **REMAINS — and becomes reachable for the first time.** `PHASE7:§9.4` measures **0** completion-valid paths on the package as specified; closing `U-B` makes `EV-23` producible and `U-H` (per Phase 7) makes `EV-25` producible |
| **T-1b** | `A✓ ∧ B✓`, `V-12` **falsely** passes | lock B/D/F + `EV-23` as worded | **ELIMINATED.** `CC-1`'s four discriminators make the no-op path fail `EV-23`. `PHASE6:§8.2` predicted exactly this: *"With them, `T-1b` becomes unreachable and collapses into `T-1c`"* |
| **T-1c** | `A✓ ∧ B✓`, `V-12` genuinely fails | — | REMAINS, and **absorbs `T-1b`'s population** |
| **T-1d** | `A✓ ∧ B✓`, `V-13` fails | — | REMAINS. Under `U-G`'s closure `EV-24` becomes set-bound, so this state becomes **detectable** where it was not |
| **T-1e** | `A✓ ∧ B✓`, `V-14` fails | — | REMAINS — **but see §6.2 cause 4**: with `EV-25` unproducible in fact, `V-14` cannot pass or fail, so this state is **unreachable in reality and reachable on Phase 7's assumption** |
| **T-1f′** | `A✓ ∧ B✓`, `EV-22` short **because the population did not clear** | — | **NEW.** Closing `U-D` via `CC-4`/`CC-5` separates this — a genuine negative answer to `UK-2` — from `T-1f″` |
| **T-1f″** | `A✓ ∧ B✓`, `EV-22` short **because the index moved between the mint and `V-11`** | — | **NEW.** `PHASE7:§5.4` `FN-D(ii)` identified the conflation; closing `U-D` resolves it into two states |

```
TERMINAL STATES AFTER THE SEVEN CLOSURES ......................... 17

    carried unchanged .............................................. 15
    ELIMINATED ......................................................  1   T-1b — the only
                                                                          false-success state
    NEWLY DISTINGUISHED (T-1f splits) ...............................  2   T-1f′, T-1f″
    net ................ 17 - 1 + 1 = 17

  THE COUNT IS UNCHANGED AND THE COMPOSITION IS NOT.
    reaching 0 blockers AND 0 unknowns .............................  1   T-1a
    reaching it FALSELY ............................................  0   (was 1: T-1b)
    requiring rollback .............................................  5   T-3, T-5, T-7, T-8, T-9
    with residuals still LATENT ....................................  4   Y-1, Y-2, Y-3, T-6

  [INFERRED] Closure does not shrink the state space.  It REDISTRIBUTES it:
  one false state is removed and one conflated state is split.  That is the
  correct signature of added discrimination, and it is worth stating because
  a closure programme that shrank the state space would be hiding states
  rather than distinguishing them.

PATHS ............................................................ 106 -> 66
    the four confirmation branches lose their FALSE-pass values:
    EV-22 ∈ {pass, fail} · EV-23 ∈ {pass, fail} · EV-24 ∈ {pass, fail}
    · EV-25 ∈ {pass, fail}  =  16 per ordering
    34 + (2 x 16) = 66
    paths reaching EXECUTION-COMPLETED ..............................  2   one per ordering
    reaching it FALSELY .............................................  0   (was 10)
    reaching it GENUINELY ...........................................  2
```

### 6.2 Q7 — can Outcome A still fail? **YES, five causes**

| # | Cause | Closable by determination? | Basis |
|---|---|---|---|
| **1** | **`U-A`** — 16 of the 17 terminal states are not `T-1a`. `UK-1` or `UK-2` may simply come out negative, and four of `register.sh`'s ten phases have **no dry-run mode** so nothing establishes their behaviour in advance | **NO** | `PHASE4` **P4-6**; `PHASE6:§1.1`; `PHASE7:§10.5` |
| **2** | **`GA-7`** — the irreversible-mutation authorization. Without it no run occurs, so `T-1a` is unreachable | **NO — and by no act available to this chain** | `PHASE5:§B.7`, `§K.4`; `PHASE7:§14.5` |
| **3** | **`U-M` unresolved, or resolved to residual-freedom** — under residual-freedom, A is **impossible** regardless of every closure, because `R-7w` survives (§5.3) | **YES** — it is one determination | `PHASE7:§8.4`, `§11.2` |
| **4** | **`U-J`** — `EV-25` has no producer, so `V-14` can neither pass nor fail. Under Phase 7's own `CD-30`, `EV-25` is a **conjunct of `EXECUTION-COMPLETED`**, so an unproducible conjunct makes the conjunction unestablishable. `PHASE7:§9.5` states it: *"**PATHS EVIDENCE-VALID … 0** — `EV-25` is unproducible on EVERY path"* | **YES** — but **not by any of the seven**, per §3.3 | `PHASE7:§6.3`, `§9.5` |
| **5** | **`U-I`** — if the 24-model reading is declared, `U-B`'s closure must be re-derived and 3 of its 7 classes lose their referents | **YES** — it is one declaration | `PHASE3:§A`; §3.2 |

**[INFERRED]** Causes 3, 4 and 5 are closable and **none of the three is closed by `U-B` … `U-H`**. Causes 1 and 2 are closable by no determination whatsoever. **Therefore Outcome A can still fail after all seven closures, and it can fail for a reason no determination can remove.**

### 6.3 Q8 — can Outcome B still be reached? **YES, and the seven closures are orthogonal to it**

**Proof.** Outcome B under residual-freedom rests on exactly the three premises of §5.3. Examine each against the seven closures:

| Premise | Does any of `U-B` … `U-H` touch it? |
|---|---|
| `RES-3`, `RES-4`, `R-7w` invariant across all 12 models | **NO.** `PHASE3:§E.7` establishes this from the residuals' own construction; no `U`-item concerns a residual |
| `R-7w` is a failure-path property that a successful run never enters | **NO.** `PHASE6:§7.2` establishes it from `commit()`'s refusal enumeration; no `U`-item changes `commit()` |
| Closing `R-7w` requires serialization inside the authority, declined | **NO.** `PHASE1:§R-7`; no `U`-item proposes it, and `PHASE7:§4.5`'s `CB-3` — the only closure that touches `ledger_authority.py` — widens the *sentinel's admissible domain*, not the writer's location |

**[INFERRED]** Therefore **B's proof is invariant under the seven closures.** B is reachable before them, after them, and independently of them. **[INFERRED]** This is the sharpest structural result of Phase 8: the entire closure programme `U-B` … `U-H` — 13 closure classes, 9 defects, five phases of work — is **orthogonal to one of the three terminal outcomes**, and that outcome is the only one reachable without execution.

### 6.4 Q9 — can Outcome C still be reached? **YES, and it is the correct outcome by default**

**[INFERRED]** C — *INSUFFICIENT INFORMATION* — is reached whenever the terminal predicate is undefined, because neither A nor B is then a proposition with a truth value (§5.3 Part 2).

```
THE UNRESOLVED PROPOSITION THAT KEEPS C REACHABLE

    U-M   which of {outcome-freedom, residual-freedom} defines
          "unconditional ready" and EXECUTION-CERTIFIED.

    SECONDARY, and it does not on its own force C:

    U-I   the 12-vs-24 model-space reading.  Under U-M = outcome-freedom
          it conditions the whole closure set (§3.2).  Under U-M =
          residual-freedom it is IRRELEVANT, because §5.3's proof
          quantifies over "all admissible models" and PHASE3 §E.7's
          invariance holds for the 24-model reading too — I-D does not
          relocate the writer, so R-7w survives it as well.
```

**[INFERRED]** So `U-I`'s relevance is itself gated by `U-M`, which is a further instance of `U-M`'s dominance and a reason C collapses to a single proposition rather than two.

**[INFERRED] C is not merely reachable — it is correct.** A Phase 9 that returns A or B without first fixing `U-M` is returning a result whose premise it supplied itself, silently. `PHASE7:§11.2` states this directly: *"While the reading is undeclared, a Phase 9 that reports A or B is reporting a result whose premise it supplied itself. C is the correct outcome for a Phase 9 conducted before the reading is fixed."*

---

## 7. Terminal-phase determination — Q10

### 7.1 The two routes to terminality, and which is available

| Route | Requires | Available to Phase 9? |
|---|---|---|
| **R1 — via Outcome B** | `U-M` = residual-freedom. Then §5.3's three-premise deduction returns B | **YES.** Zero runs, zero permits, zero governance selection, zero closures. Every premise is a measurement already committed in `PHASE1`, `PHASE3`, `PHASE4` and `PHASE6` |
| **R2 — via Outcome A** | `U-M` = outcome-freedom, **and** all 34 determinable nodes of §5.4 closed, **and** `GA-7` granted by a party outside the chain, **and** both runs returning `T-1a` | **NO.** Two of the three undeterminable nodes — `GA-7` and `U-A` — lie outside every act this chain can perform |

**[INFERRED] One asymmetry decides the question.** Under R2, a failed run does **not** yield Outcome B. `PHASE4:§H.4` establishes that a validation failure is *"a **revealed defect** — a pre-existing implementation error surfaced by validation — not a new blocker"*, and `PHASE4:§I.6` that *"blockers do not return to 5"* and the failure is recoverable. A revealed defect is fixable, so a failed run establishes *"not yet"*, never *"does not exist"*. **Under outcome-freedom, therefore, a failed run returns C, not B** — and R2 is terminal only on success, which is `U-A`.

### 7.2 Is adopting a reading a legitimate act for Phase 9?

**[INFERRED]** It must be, or no phase can ever be terminal. Three grounds, each from the inputs:

1. **It is not a governance decision.** `U-M` touches none of the five closure axes and none of the two modifiers. `PHASE2:§E.1` enumerates the **13** decisions a complete governance specification must answer; the terminal-predicate reading is not among them, and `PHASE2:§D.3`'s own deferral concerned the model-space reading (`U-I`), not this.
2. **The chain already treats the sibling proposition as governance-independent.** `PHASE7:§5.6b` classifies `CC-6` — adjudicating `CD-28` against `CD-30`, which is `U-E` — as **governance-independent**, on the ground that it *"touches no axis"*. `U-M` is the same species one level up.
3. **`PHASE7:§11.2` names both readings and derives both consequences.** The work of characterising the choice is complete; only the choice is outstanding.

**[INFERRED] One caution, stated because it is the obvious objection.** Choosing residual-freedom *because* it makes Phase 9 terminal would be question-begging. The honest formulation is not *"choose the reading that terminates"* but: **the two readings have been fully characterised, exactly one of them is decidable without execution, and Phase 9's terminality is a property of which is adopted — not an argument for adopting either.** This phase states both and adopts neither.

### 7.3 Q10 verdict

```
CAN PHASE 9 BE TERMINAL?                                              YES

  by ROUTE R1, and R1 requires exactly one determination.

  PHASE 9 IS TERMINAL IF AND ONLY IF IT FIRST DECIDES U-M.
      U-M = residual-freedom  ->  Outcome B, proved, zero cost, terminal
      U-M = outcome-freedom   ->  terminal only after GA-7 and both runs;
                                  not terminal within the determination chain
      U-M undecided           ->  Outcome C; NOT terminal

  WHAT PHASE 9 DOES NOT NEED, UNDER R1
      U-B … U-H closed .......................... not needed  (§6.3)
      IA-12, O-3, GA-2 .......................... not needed
      GA-1 … GA-9 ............................... not needed
      IA-1 … IA-12 .............................. not needed
      a permit, a register, a mutating run ...... not needed
      a governance selection on any axis ........ not needed
```

---

## 8. Mandatory final verdict

### A. Are `U-B` … `U-H` exhaustive?

**NO.** Four unresolved propositions stand outside the set — `U-I` (§3.2), `U-J` (§3.3), `U-K` (§3.6), `U-M` (§3.7). Three closures inside the set require artifacts outside it — `IA-12`, `O-3`, `GA-2` (§3.4). One proposition raised twice by Phase 6 and restated by Phase 7 is closed by no `U`-item (`P-49`, §3.5). One surface in Phase 7's own exhaustiveness proof covers 5 of 13 members (§3.8). **Nine findings across Q2's five requested categories.**

### B. Are `U-B` … `U-H` minimal?

**NO.** Three of the seven are partially or conditionally redundant, and the redundancies are recorded inside Phase 7's own tables:

- **`U-D`** — its completion half is `FP-B`, listed by `PHASE7:§5.2` as a **`U-C`** channel and closed by `CC-4`/`CC-5`, both **`U-C`** closures. Only its authorization half (`EV-14` / permit-B invalidation) is independent.
- **`U-F`** — limb (a) is closed by `CC-2`, a **`U-C`** closure whose own entry names `U-F`; limb (d) is discharged by run A, i.e. by `UK-1`. Only limbs (b) and (c) are independent.
- **`U-H`** — arises under **3 of the 7** `U-B` closure classes and under none of the other four.

The set becomes minimal after re-partitioning into `{U-B, U-C′, U-D′, U-E, U-F′, U-G, U-H}` as §4.3 defines them.

### C. Are `U-B` … `U-H` sufficient?

**NO**, on two independent grounds:

1. **Additively** — the three dependency leaks of §3.4 plus the four propositions of §3.9 must also close.
2. **Structurally, and this is the stronger ground** — the *necessity* of all seven is conditional on `U-M`, which is not one of them. Under `U-M` = residual-freedom, **0 of 7** are necessary (§4.2). A closure set that does not contain the proposition fixing its own target cannot be shown sufficient for anything.

### D. If all seven close, how many unresolved propositions remain?

Two scopes, because the chain uses two and conflating them is how this question gets answered wrongly.

```
SCOPE 1 — PHASE 7's OWN SCOPE
          (between EXECUTION-AUTHORIZED and a terminal Phase-9 proof)

    UK-1   P-32   execution-time, irreducible
    UK-2   P-33   execution-time, irreducible
    U-J    P-57   EV-25 has no producer                            [§3.3]
    U-K    P-58   no trust rule for evidence                       [§3.6]
    U-M    P-59   the terminal-predicate reading                   [§3.7]
                  (carrying its child P-50, EXECUTION-CERTIFIED)
    P-49          the poisoned permit_id — arises at issuance,
                  repaired by no rollback, closed by no U-item     [§3.5]
                                                              ──────────
    REMAINING IN SCOPE ......................................... 6

    + 1 CONDITIONING proposition, upstream but governing the set's
      own well-formedness:  U-I  (P-26 / P-37 / P-56)          = 7

SCOPE 2 — THE WHOLE CHAIN TO FINAL CLOSURE

    distinct open propositions before the closures ................ 46
    closed by the seven ............................................ 7
        P-47 U-B · P-48 U-C · P-51 U-D · P-52 U-E ·
        P-53 U-F · P-54 U-G · P-55 U-H
                                                              ──────────
    REMAINING ................................................... 39

    grouped:
        artifact-level blockers ....................................  5   P-13 … P-17
        residuals, accepted and never closed .......................  3   P-18, P-19, P-20
        execution-time unknowns ....................................  2   P-32, P-33
        governance propositions .................................... 19   incl. U-I as GA-4
        implementation propositions ................................  5   P-43, P-44, P-45,
                                                                          P-49, P-57
        determination-closable propositions ........................  5   P-46, P-50, P-58,
                                                                          P-59, P-60
                                                              ──────────
                                                                     39   ✓

  OF THE 39:
      irreducible by any determination ....................  2   UK-1, UK-2
      producible by no act available to this chain ........  1   GA-7
      decisive for the Phase-9 outcome ....................  1   U-M
      on no path to any outcome ...........................  1   U-J
```

### E. Can Outcome C still exist?

**YES**, and it is the **correct** outcome for any Phase 9 conducted before `U-M` is decided. The unresolved proposition is exactly `U-M`; `U-I` is secondary and is itself gated by `U-M` (§6.4). A Phase 9 that returns A or B without first fixing the reading returns a result whose premise it supplied itself — which `PHASE7:§11.2` already states in its own words.

### F. Can Phase 9 be terminal?

**YES**, by route R1, and R1 requires exactly one determination and no execution.

### G. What exact proposition must Phase 9 decide, if any?

**Exactly one.**

> **`U-M` — Does *"unconditional ready"* mean `0 blockers ∧ 0 unknowns` with the three residuals accepted under `GA-5` (outcome-freedom), or `0 blockers ∧ 0 unknowns ∧ 0 residuals` (residual-freedom)?**

Everything else is downstream of that choice or irrelevant to it:

- under **residual-freedom**, Outcome B follows from three committed measurements and the other 25 open propositions are moot;
- under **outcome-freedom**, the other 25 all become live, two of them (`UK-1`/`UK-2` via `U-A`, and `GA-7`) are closable by no determination, and Phase 9 cannot be terminal within the chain.

**This phase states both values and adopts neither.**

---

## 9. Stop condition

### 9.1 Determinations made

- **Q1** — **60** identifiers inventoried across Phases 0–7; **12** closed by Phase 1; **48** open identifiers over **46** distinct propositions, classified across all ten required classes. §2.
- **Q2** — **NOT exhaustive.** Nine findings across Q2's five categories: 1 unstated assumption, 4 dependency leaks, 1 hidden precondition, 2 closure claims on unverified facts, 1 proposition referenced but never resolved. §3.
- **Q3** — **0 of 7 sufficient.** For outcome-A closure: 3 unconditionally necessary, 2 necessary in part, 2 conditionally necessary. For decidability closure: **0 of 7 necessary**. §4.
- **Q4** — **18 nodes, 21 edges, 7 proved non-edges, 2 overlap relations.** Two sources with in-degree 0 (`U-M`, `U-I`); one isolated node (`U-J`); three sinks no determination closes. §5.1–§5.2.
- **Q5** — **Minimum closure set for a terminal Phase 9 has cardinality 1: `{U-M}`.** Sufficiency proved from three committed measurements; minimality proved by the empty-set argument. For Outcome A the set has cardinality 37, of which **3 are not determinable by this chain**. §5.3–§5.4.
- **Q6** — **17** terminal states remain: `T-1b` eliminated, `T-1f` split. Paths **106 → 66**. Genuine completions **2**; false completions **0** (was 10). §6.1.
- **Q7** — Outcome A **can still fail**, for **5** causes, of which **2** (`U-A`, `GA-7`) are closable by no determination and **3** are closable but by none of the seven. §6.2.
- **Q8** — Outcome B **remains reachable and is orthogonal to all seven closures.** Its three premises are untouched by any `U`-item. §6.3.
- **Q9** — Outcome C **remains reachable and is correct by default.** The unresolved proposition is `U-M`. §6.4.
- **Q10** — Phase 9 **can be terminal**, by one route, requiring one determination and no execution. §7.

### 9.2 What was confirmed rather than corrected

| Confirmed | Basis |
|---|---|
| Phase 7's **106**-path count and its diagnosis of Phase 6's 58 | Re-derived from Phase 7's own factors; `EV-22`'s omission verified against `PHASE6:§7.4` and `§8.1` |
| Phase 7's **8 / 98** reversibility correction | Re-derived: 14 of each ordering's 18 base combinations land an allocation |
| Phase 7's `EXECUTION-CERTIFIED(b) = ∅` proof | All three premises verified in `PHASE1:§R-7`, `PHASE3:§E.7`, `PHASE4:§G` + `PHASE6:§7.2`. **§5.3 is built on it** |
| `U-B`'s three-class partition and `C-1`'s single-class coverage | Follows from `history ∈ NON_ALLOCATION_KEYS` (`PHASE1:§R-5`) and the sentinel's two checks (`PHASE05:§C.9`) |
| *"No path produces a new blocker"* | Now confirmed at a **fourth** cardinality: 10 (Phase 4), 58 (Phase 6), 106 (Phase 7), 66 (§6.1) |
| The chain's blocker arithmetic, end to end | 15 − 12 = 3, + `RES-1` + `RES-2` = **5**, identical in `PHASE1:§6.2`, `PHASE2:§A.1`, `PHASE3:§G.1`, `PHASE6:§10.1`. Four documents, one number, zero drift |
| `U-A`'s irreducibility | Independently grounded in `PHASE4` **P4-6** — four of ten phases have no dry-run mode — and therefore not an artifact of the chain's declination policy |
| All 12 admissible models, 13 forced tasks, 2-run minimum, disjoint populations, 14-condition gate, 4 rollback procedures, 3 residuals | Every one re-checked against §§2–7 and unaffected |

### 9.3 Corrections to Phase 7

| # | Claim | Correction | Consequence |
|---|---|---|---|
| **1** | `§10.2` — the remaining closure set is `{U-B … U-H}` | **4** propositions stand outside it: `U-I`, `U-J`, `U-K`, `U-M` | The set is not exhaustive |
| **2** | `§10.4` surface 2 — `EV-25`'s *"closure is an implementation act inside `U-H`'s scope"* | `U-H` is the sentinel's accounting; `EV-25` is residual-control activation. **Disjoint.** Closing `U-H` closes none of `EV-25`. Phase 7's own `§12.8` contains the refutation | `U-J` is a distinct member; `PHASE4:§G`'s *"REDUCED"* is unobtainable |
| **3** | `§10.4` surface 3 — *"72 of 72 COMPLETE"* after the seven | Requires `IA-12`, `O-3` and `GA-2`, none of which is a `U`-item. The parenthetical excuse — *"not a **new** governance dependency"* — is true and does not make it closed | The seven are not sufficient |
| **4** | `§10.4` surface 6 — terminal-state names, cardinality **5** | The chain defines **13**: 6 in `PHASE5:§0.4`, 6 in `PHASE6:§11.1` (one shared), 2 constructed in `PHASE7:§8.2` | The exhaustiveness claim covers 38% of the surface it names |
| **5** | `§10.2` — `U-D` and `U-F` as independent members | `U-D`'s completion half **is** `FP-B`, a `U-C` channel closed by `CC-4`/`CC-5`; `U-F`'s limb (a) is closed by `CC-2`, a `U-C` closure whose own entry names `U-F`; limb (d) is discharged by `UK-1` | The set is not minimal; §4.3 gives the re-partition |
| **6** | `§10.4` surface 6 — `EXECUTION-CERTIFIED`'s two readings are *"a determination outstanding, not an uncertainty"* | A determination outstanding **is** an unresolved proposition, and `PHASE7:§11.5` proves this particular one decides the Phase-9 outcome | `U-M` is the graph's dominating node and the minimum closure set |
| **7** | `§10.4` closing caveat — *"a Phase 8 at this resolution should expect to find between one and three more"* | **Four**, plus three leaks, plus one under-enumerated surface. The estimate was low, and the *character* changed again — from definitional conflicts to **scope conditions on the closure set itself** | The convergence Phase 7 reported is real in rate and not yet complete |

**[INFERRED]** None of the seven overturns a **structural** result of Phases 0–7. Every measurement in every input stands. What they overturn is the **boundary** Phase 7 drew around its closure set — and the boundary was drawn one level too low, at the items to be closed rather than at the proposition that decides whether closing them matters.

### 9.4 Constraint compliance

- **Determination only.** No implementation, no design, no task content. §§1–8 determine.
- **Read and use only the nine documents.** **MET.** No source file read; no probe executed; no measurement taken. Every fact carries a citation to one of the nine. Where a measurement is used, the phase that took it is cited, never the source line.
- **Governance selected: NONE.** No axis assigned. `U-M` and `U-I` are named as open and **both values of each are stated without preference**. §7.2 records explicitly why choosing residual-freedom *because* it terminates would be question-begging, and declines to choose.
- **No permits issued. `register.sh` not run. No allocation workflow run. No mutating command executed.** The only commands were `shasum`, `git rev-parse`, `git status --porcelain`, `git ls-files --cached` and `ls`, for the compliance check.
- **Repository files modified: NONE.** This document is the only addition.

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

### 9.5 The terminal position

```
POSITION ................. READY-CONDITIONAL-ON-GOVERNANCE-SELECTION   (unchanged)
AUTHORIZATION STATE ...... NOT-AUTHORIZABLE                            (unchanged)
BLOCKERS ................. 5 artifact-level · 0 introduced
UNKNOWNS ................. 2, comprising 10 components
RESIDUALS ................ 3, all latent, 0 closable by any model,
                           and 2 of the 3 REDUCTIONS unobtainable (U-J)
OPEN PROPOSITIONS ........ 46 distinct, over 48 identifiers, of 60 inventoried
    closable only by a governance decision ........... 19
    closable by determination alone .................. 10
    closable by an implementation act ................ 12
    closable by an execution act ......................  2   UK-1, UK-2
    accepted, never closed ............................  3   RES-3, RES-4, R-7w
    closable by NO act available to this chain ........  1   GA-7
CLOSURE SET {U-B … U-H} .. NOT exhaustive · NOT minimal · NOT sufficient
MINIMUM CLOSURE SET FOR A TERMINAL PHASE 9 ... { U-M },  cardinality 1
```

---

# PHASE9 TERMINAL CLOSURE IS PROVABLY POSSIBLE

## The complete proof

**Theorem.** There exists a route by which Phase 9 returns a determinate terminal outcome with proof, and that route requires exactly one determination, no mutating run, no permit, no register, no governance selection on any axis or modifier, and none of `U-B` … `U-H` closed.

---

**Definitions.** Let `U-M` be the proposition: *which of `{outcome-freedom, residual-freedom}` defines "unconditional ready"*. `PHASE7:§11.1` establishes that both readings are live and `PHASE7:§11.5` that **no artifact in Phases 0–7 selects one**.

Let `R = {RES-3, RES-4, R-7w}` be the residual set, fixed at three by `PHASE05:§F.4`, `PHASE1:§R-7`, `PHASE3:§E.7`, `PHASE4:§G`, `PHASE5:§K.6`, `PHASE6:§10.3` and `PHASE7:§12.8` — seven documents, one set, no drift.

---

**Lemma 1 — `U-M` is decidable by Phase 9.**
It touches none of the five closure axes and neither modifier; `PHASE2:§E.1` enumerates the **13** decisions a complete governance specification must answer and it is not among them. `PHASE7:§5.6b` classifies its sibling `CC-6` — adjudicating `CD-28` against `CD-30` — as **governance-independent** on exactly the ground that it *"touches no axis"*. Therefore adopting a reading is a determination, not a governance selection, and lies within Phase 9's powers. ∎

**Lemma 2 — under `U-M` = residual-freedom, `R-7w` is closed by no model, no path and no act available to this chain.**
Three premises, each a measurement committed in an input document:
- **(P1)** `PHASE3:§E.7` — `RES-3`, `RES-4` and `R-7w` are invariant across **all 12** admissible models; the table's *"Closed by any of the 12?"* column reads **no — all 12 identical** for every row.
- **(P2)** `PHASE4:§G` — execution leaves `R-7w` **UNCHANGED**, because it is a property of the **failure** path `:893`→`:921`; `PHASE6:§7.2` supplies the enumeration: exactly **4 of `commit()`'s 8** refusal points traverse it and a **successful run enters none**.
- **(P3)** `PHASE1:§R-7` — closing it requires moving serialization inside the authority, declined as *"a larger change than this phase covers"*.

From **(P1)**, no governance answer closes it. From **(P2)**, no execution outcome closes it — including the successful one, which is the only outcome Outcome A could rest on. From **(P3)**, no act within the chain's authorization closes it. ∎

**Lemma 3 — under `U-M` = residual-freedom, the set of unconditionally-ready states is empty.**
Residual-freedom requires `|R| = 0`. By Lemma 2, `R-7w ∈ R` in every model and on every path. Hence `|R| ≥ 1` everywhere, and the satisfying set is `∅`. ∎

**Lemma 4 — Lemma 3 is invariant under the closure of `U-B` … `U-H`.**
Each of the seven concerns a permit, an evidence item, a definition, a lock state or a sentinel. **None** proposes moving `writer` inside the authority, which **(P3)** identifies as the unique remedy. `PHASE7:§4.5`'s `CB-3` is the only closure in the entire programme that touches `ledger_authority.py`, and it widens the **sentinel's admissible domain**, not the writer's location. Therefore §6.3's three-row table holds: no premise of Lemma 2 is touched. ∎

**Lemma 5 — Lemma 3 is invariant under `U-I`.**
The 24-model reading admits `I-D`. `PHASE2:§C.5` establishes that `I-D` changes `_verify_permit`'s register lookup at `:714-721` and nothing else in the write path; it does not relocate `writer`. Therefore **(P1)** extends to the 24-model set and Lemma 2 holds under either reading. ∎

**Lemma 6 — the empty set does not suffice.**
With `U-M` undecided, *"unconditional ready"* has two non-equivalent extensions and therefore no extension. The sentence *"an unconditionally-ready state exists"* has no truth value; neither A nor B is assertable; Phase 9 must return **C**, which is not terminal. Hence any sufficient closure set has cardinality ≥ 1. ∎

---

**Theorem, proved.** Take `U-M` = residual-freedom, which Lemma 1 permits. By Lemmas 2 and 3, the unconditionally-ready set is empty in every admissible model and on every reachable path. That is **Outcome B — UNCONDITIONAL READY DOES NOT EXIST** — and it is established by deduction from **(P1)**, **(P2)** and **(P3)**, all of which are already committed in `PHASE1`, `PHASE3`, `PHASE4` and `PHASE6`. No mutating run, no permit, no register, no governance selection, and by Lemma 4 **none of `U-B` … `U-H`** is required. By Lemma 6 no smaller closure set exists. **Therefore the minimum closure set for a terminal Phase 9 is `{U-M}`, of cardinality 1, and terminal closure is provably possible.** ∎

---

**Three qualifications, stated because the proof is worthless without them.**

1. **The proof establishes possibility, not the answer.** It shows a route exists. It does **not** show that residual-freedom is the right reading, and this phase does not claim it is. Under outcome-freedom the theorem does not apply: Phase 9 is then terminal only after `GA-7` — *"the one artifact no phase of this chain can produce for itself"* (`PHASE5:§K.4`) — and both runs returning `T-1a`, which is `U-A` and which `PHASE4` **P4-6** measured to be unmeasurable in advance. **Under outcome-freedom, Phase 9 cannot be terminal within the determination chain.**

2. **The choice must be made on its merits, not on its terminality.** §7.2 records why: adopting residual-freedom *because* it terminates would be question-begging. What this phase establishes is the shape of the decision — two readings, both fully characterised, exactly one decidable without execution — and it adopts neither.

3. **`U-J`, `U-K`, `U-I` and the three leaks do not disturb the theorem, and they are not thereby closed.** Under residual-freedom they are moot; under outcome-freedom they are live and must close alongside the seven. They are recorded in §3 for the second case, not discharged by the first.

Phase 8 ends here.
