# UCOS Ω∞ — PHASE Ω∞-B, DELIVERABLE 10
## Cost-of-Delay Prioritization Table

> ## ⚠ EVIDENCE PROVENANCE AND CURRENT REPRODUCIBILITY — READ FIRST
>
> **The subject tree measured by this phase, `engine/omega_governance/`, is NO LONGER PRESENT in the
> working directory.** This note is recorded rather than the claims below being quietly left standing,
> because a claim that nothing checks is the precise defect class this phase was convened to document.
>
> **Timeline, from filesystem timestamps:**
>
> | Time (2026-08-29) | Event |
> |---|---|
> | 11:23–11:26 | `engine/omega_governance/**` last modified (predates this phase) |
> | 12:01–12:08 | probes `b01`, `b02_b05`, `b03_b04`, `b06` executed; outputs recorded |
> | 12:48:23 | probe `b07` executed; §H9 confirmed the tree present — `state.py`, `authority.py`, and the `reference/` and `temporal/` subpackages |
> | **12:50:02** | **`engine/` directory mtime changes — the subpackage is removed** |
> | 12:51:56 | absence detected during final verification |
>
> **What this does and does not affect.**
>
> - **The evidence artifacts survive.** All probe sources and their recorded outputs are preserved in
>   `00-MASTER/UCOS-OMEGA-B-001/probes/`. Every measurement cited in this document was taken against the
>   tree while it existed, and the recorded outputs are the evidence of record.
> - **The reproduction instructions in this document no longer execute.** They now fail with
>   `ModuleNotFoundError: No module named 'engine.omega_governance'`. Where this document says a probe
>   was "re-executed against current repository state" and found byte-identical, that was true when
>   written and is **not verifiable now**.
> - **The tree is not recoverable from version control.** It was never committed and never stashed
>   (`git status` reported it untracked; `git log --all --diff-filter=A` finds no such path).
> - **Nothing in this phase removed it.** Ω∞-B writes were confined to
>   `00-MASTER/UCOS-OMEGA-B-001/probes/` and the root `PHASE_OMEGA_B_*.md` deliverables. No Ω∞-B
>   operation targeted `engine/`.
>
> **Consequence for this document's standing.** Its classifications remain the honest record of what was
> measured. They are **no longer independently re-verifiable** until the tree is restored from a backup or
> another working copy. Restoring it is an owner decision and is not taken here.


**AUTHORITY = NONE (DERIVED TRUTH).** No certification, no seal, no ratchet advancement, no closure
declaration, no readiness claim. **Nothing here is authorised, scheduled or approved.** No active
governance, validation or certification process is modified. This is a proposed ordering, offered so it
can be refused.

**WHAT COST OF DELAY MEANS HERE.** Not severity, and not effort. **How much more expensive the fix
becomes if other work happens first.** An item whose cost is identical today and in a year has zero cost
of delay however severe it is; an item that is free today and a rewrite tomorrow ranks first however
minor it looks.

**WHAT Ω∞-B CHANGES ABOUT Ω∞-A'S RANKING.** Ω∞-A ranked nine ceilings by cost of delay from design
inspection. Ω∞-B measured them. Four ranks change, and one entirely new item enters at the top.

| Ω∞-A rank | Item | Ω∞-B rank | Change and why |
|---|---|---|---|
| — | **Eight documented modules are absent while the tree claims they exist** | **1** | **NEW.** Not in Ω∞-A. It costs ten lines of prose today and it is the precondition for every statement about the others being meaningful |
| 1 | Register is a chain, not a DAG | **3** | Confirmed zero-cost-today by prototype. Demoted only because two items are now cheaper still |
| 2 | Certification has a fixed input set | **4** | **Ω∞-A recorded this as unbuilt. It is built** — as a frozen enumeration of four in `state.py`. Half the zero-cost window has already closed |
| 3 | Guards are hardcoded | **5** | Confirmed, and merged with rank 4: one consumer has **already** grown its condition vocabulary |
| 4 | Proof is exponential in axis count | **2** | **Promoted.** Not because the proof expires, but because it **has never run** — and the correction is prose |
| 5 | No vocabulary identity | **6** | Confirmed moderate and flat. **Now known to be half-closable only** |
| 6 | No storage provider | **8** | Unchanged. **Not tested in Ω∞-B** |
| 7 | No emitted schema | **9** | Unchanged. **Not tested in Ω∞-B**; folded into item 1's finding |
| 8 | Census is not mergeable | **7** | Confirmed interface-compatible. Ratio caveat added |
| 9 | Binary transformations | **Split: 4½ and 10** | **The correctness half is promoted sharply.** `path()` returns a complete route from insufficient inputs — a wrong answer today, not a future barrier |

---

## 1. THE TABLE

Cost columns state what the fix costs **now**, **after the next module is written**, and **after the
subsystem is consumed by a gate, ratchet or CI stage** (a state currently forbidden for all Phase 2
code).

| # | Item | Findings | Cost now | Cost after next module | Cost after consumption | Delay multiplier | Basis |
|---|---|---|---|---|---|---|---|
| **1** | **Correct the nine absent-module claims** | B-N-01, C-05 | **~10 lines of prose in 2 files** | same | **reputational and unbounded** — every prior statement about the proof, the register and certification described modules that do not exist | **∞ / 1** — the cost does not rise, but **everything below is unverifiable until it is done** | MEASURED (`b07` §H9, `b01` §B-01.7) |
| **2** | **Replace the exhaustive proof with the structural argument** | A-16, G-09, X-07 | **~15 lines**, plus keeping enumeration as a declining cross-check | small | the claim silently expires while documents assert it | **1 → ∞** — it fails **without an error** | MEASURED BY PROTOTYPE (`b07` §H7: holds at 40 axes, ~66 µs) |
| **3** | **Write the register as a DAG, not a chain** | A-24, X-11, C-03 exposure | **ZERO** — `registry.py` does not exist | **rewrite + record migration** | rewrite + migration + every consumer of an ordering | **0 → high** | MEASURED BY PROTOTYPE (`b07` §H5) |
| **4** | **Make certification inputs a registry** | A-11, B-N-02, K-01…K-09 | **ZERO for the decision function** — `certification.py` does not exist. **NON-ZERO for the graph** — four preconditions are already a frozen enumeration | rewrite of the decision function | rewrite + every ratchet whose population depends on a disposition | **0.5 → high** — **half the window has closed** | MEASURED BY PROTOTYPE (`b07` §H2) |
| **4½** | **Distinguish conjunction from alternative in transformations** | A-21, B-N-04 | **small, and it is a live correctness defect** — `apply()` would succeed on insufficient inputs **today** | same | wrong `VELOCITY` values in governance records, and no way to tell which | **1 → 1, but the defect is ACTIVE** | MEASURED (`b03_b04` §B-04.2) |
| **5** | **Promote guards to a registered mechanism** | A-09, A-10, G-01, G-02, X-01, X-02 | **small** — one protocol, two guards re-expressed | grows per consumer | three incompatible condition vocabularies to reconcile | **1 → 3** — **one consumer has already grown, measured in item 4** | MEASURED BY PROTOTYPE (`b07` §H1: 10 of 10) |
| **6** | **Give vocabularies identity** | A-14, A-20, G-10, X-05, X-12 | **moderate** — digest is derivable with zero registry changes | moderate | moderate + a record backfill for every unqualified rule citation | **1 → 1.5** — flat, except the identifier half | MEASURED BY PROTOTYPE (`b07` §H3), and **half-closable only** |
| **7** | **Make the census mergeable** | A-15, G-07, X-06 | **small** — the result type is already a monoid | small | grows with stored data | **1 → 2** | MEASURED BY PROTOTYPE (`b07` §H6) |
| **8** | **Storage as a provider** | G-05, A-12, Rule 7 | moderate | moderate | high — every record site | **1 → 1** flat | **ARGUED, not measured.** No `StorageProvider` exists to probe |
| **9** | **Emit the contracts** | G-06, C-05, X-10 | small | small | small | **1 → 1** flat | **ARGUED, not measured.** `schema.py` absent |
| **10** | **N-ary transformation arity (the expressiveness half)** | A-21, G-03, X-03, B-N-03 | moderate | moderate | moderate + `as_record()` backfill | **1 → 1.2** | MEASURED BY PROTOTYPE (`b07` §H4) |
| **11** | **Local defects with no dependencies** | B-N-05, B-N-06, B-N-11, N-10, N-12, N-16, R-1, R-2 | **very small each** | same | **B-N-06 is a silent corruption entering records now** | **1 → 1, but one is ACTIVE** | MEASURED (`b06`, `b07` §H8) |
| **12** | **Directive amendment: Rule 9 code-migration vs record-backfill** | C-02, A-17, G-08 | **a directive edit** | same | same | **1 → 1** flat | MEASURED (`b02_b05` §B-05.2) |
| **13** | **C-04's convergent ratchet on unexecutable invariants** | C-04, A-18, A-19 | **very small** — the reporter exists | same | rises with declared invariants | **1 → 1.3** | Present; **not done** |
| **14** | **C-01's lossy proxy declarations** | C-01, A-06 | **small per declaration** | same | same | **1 → 1** flat | MEASURED available and **untaken** (`b03_b04` §B-04.4) |

---

## 2. THE THREE ITEMS WITH A GENUINE DEADLINE

Everything else can be done later at roughly the same cost. These three cannot.

### Item 1 — the absent-module claims. Deadline: **before any further assessment**

`state.py:58` asserts `invariants.unknown_never_certifies` enumerates all 900 vectors.
`__init__.py:34` lists `invariants.py` as "seven executable proofs, two of them exhaustive". **The module
does not exist, and nor do seven others.**

**Why this is rank 1 despite costing ten lines.** Its cost of delay is not monetary; it is
**epistemic**. Every statement Ω∞-A and Ω∞-B make about proof tractability, certification architecture,
the register and self-verification is a statement about modules that do not exist. Ω∞-B could only
measure the exhaustive proof by **reconstructing it inside a probe**. Until the claims are corrected, a
reader cannot distinguish what is built from what is designed, and no ordering of the remaining work is
trustworthy.

**And the discipline that would have prevented it already exists in the same file.**
`REQUIRED_STATE_NAMES` holds thirteen names *so that an edit renaming one is refused by a test rather
than by a reviewer*. The identical pattern applied to the module table would have caught this. **The
finding is not that eight modules are missing — that is a schedule. The finding is that the tree makes a
present-tense claim nothing checks, in a package that already demonstrates the checking pattern for a
different claim — `REQUIRED_STATE_NAMES` at `state.py:340`, 282 lines below the false claim at
`state.py:58`, in the same file.**

### Item 3 — the register's shape. Deadline: **before `registry.py` is written**

A hash chain requires each entry to name exactly one predecessor, imposing a total order on records
whose coordinates the same architecture declares `CONCURRENT`. Measured: a DAG admits a concurrent
sibling pair, verifies, detects tampering, and emits total order as a record declaring itself a
`PROJECTION`.

**Cost now: zero. Cost after: a rewrite plus a record migration.** The deadline has not passed.

### Item 4 — certification inputs. Deadline: **partly passed**

**This is the one place Ω∞-A's assessment was wrong in a way that costs something.** Ω∞-A ranked it 2
and recorded the cost as zero "because `certification.py` does not exist". The module does not exist —
and the precondition set does. It is the frozen `blocked_by` tuple `(CONTRADICTED, UNATTRIBUTED,
UNGOVERNED, UNKNOWN)` on `Ω²-S-22` and `Ω²-S-26`, inside the module constant `INITIAL_TRANSITIONS`.

So the window is half closed: writing the *decision function* registry-driven is still free; the four
preconditions already in the graph must be re-expressed as registrations.

**And a constraint on doing so, which nothing else in this table shares.** `blocked_by` must be
**retained** as the declaration the standard state-exclusion inputs are constructed from, because the
structural proof of item 2 reads exactly that field on exactly those edges. **Items 2 and 4 pull in
opposite directions on one field.** A migration that moves the preconditions *out* of `blocked_by`
silently destroys item 2's proof input. Any sequencing that treats them as independent trades one
blocker for the other.

---

## 3. ITEMS WHOSE DEFECT IS ACTIVE RATHER THAN LATENT

Cost of delay is the wrong lens for two items. They are not barriers to future work; they are producing
wrong records now.

| Item | What is happening today | Severity |
|---|---|---|
| **4½** — conjunction indistinguishable from alternative | `path('SPACE','VELOCITY')` returns a **COMPLETE route** with two of three required inputs absent, so `apply()` would produce a `VELOCITY` value having consulted neither time nor frame, **and report success** | **A wrong answer, not a missing capability.** Ω∞-A ranked the containing item 9th as an expressiveness gap |
| **11** — bare `str` position exploded and fingerprinted | `TemporalCoordinate(..., position='EPOCH', ...)` is accepted and becomes `('E','P','O','C','H')` — a five-component coordinate the caller did not intend, which then **fingerprints** and enters a governance record as a legitimate position | **The only silent corruption found in the tree.** The neighbouring case (empty position) is correctly refused, so this is an omission rather than a design position. **One `isinstance` refusal closes it** |

**Both cost the same to fix now and later. Both should be fixed now, and the reason is not cost of
delay** — it is that every day they remain, more records may be written that nothing can distinguish
from correct ones.

---

## 4. WHAT MOVING FAST WOULD COST — the risks each item carries

Recorded because a prioritisation that lists only benefits is a schedule, not an assessment. Every
recommendation in the reports carries cost, risk and architectural impact; these are the risks that
survive into the ordering.

| Item | Principal risk if done carelessly |
|---|---|
| 1 | A *mechanical* module-presence check verifies existence, not correctness. A stub returning `True` satisfies it — C-04 in a new location |
| 2 | The structural argument is a claim about the **declared** edge set. An edge registered later targeting `CERTIFIED` without naming `UNKNOWN` breaks it, and nothing re-checks on registration. **Incremental re-proof is part of the fix, not an enhancement** |
| 3 | A DAG grows heads without bound absent merges. Head count becomes a governed population |
| 4 | **Moving preconditions out of `blocked_by` destroys item 2's proof input.** See §2 |
| 4½ / 10 | `as_record()` byte change — a C-02 record backfill. And callers may now receive **several** satisfiable routes from different authorities and must choose; the model can no longer pretend there is one answer |
| 5 | `check` must return a **population** of refusals. Preserving the single-string signature discards exactly the information the mechanism produces. And the maximal option's removal of `set()` from `AuthorityLink` is **the only non-backward-compatible change in the whole programme** |
| 6 | A digest over five registries needs a canonical serialisation that does not yet exist; a careless one yields false agreement (omission) or false divergence (ordering). **And a digest cannot see a registered predicate**, so identical digests do not imply identical checks |
| 7 | **`fallback_density` is a ratio, and a ratio is not a monoid.** It must be carried as `(numerator, denominator)` and divided at the end |
| 11 | The `str` refusal is **breaking** for any caller relying on the explosion. That population is likely zero and must be **measured** rather than assumed |
| 13 | A ratchet on unexecutable invariants is a mitigation, not a fix, and must not be reported as closing C-04 |
| 14 | Fidelity quantified beyond `lossy: bool` risks **fabricated precision** — a declared fidelity nobody can check, which is C-04 where it does most damage |

---

## 5. RECOMMENDED ORDERING, AND WHY THE ORDER IS LOAD-BEARING

```
  1.  Correct the absent-module claims                   (prose; unblocks interpretation of everything)
  2.  Structural proof + declining exhaustive cross-check (must follow 1, or it fixes a proof the tree
                                                           misdescribes)
  3.  Register as a DAG                                   (free only while registry.py is absent)
  4.  Guards as a registered mechanism                    ) ONE ITEM, not two —
  5.  Certification inputs as a registry                  ) and 5 must RETAIN blocked_by for 2
  6.  Conjunction vs alternative + n-ary arity            (an active defect)
  7.  Local defects: bare-str refusal, transitivity check,
      Comparison.coincident, refusal-relation resolution,
      clock-copy verification                             (all independent; one is an active corruption)
  8.  Vocabulary identity: digest + divergence            (detection only — NOT a closure of A-14)
  9.  Mergeable census, ratio caveat carried
 10.  Directive amendment (Rule 9), C-04 ratchet,
      C-01 proxy declarations                             (three cheap items attached to fundamentals)
 11.  Storage provider, schema emitter                    (untested in Ω∞-B; ARGUED only)
```

**Three ordering constraints that are not preferences:**

1. **1 before 2.** Replacing a proof method while the tree misdescribes the proof leaves the false claim
   in place, and the false claim is the part that misleads a reader today.
2. **4 and 5 together, with 5 retaining `blocked_by`.** They are one mechanism (Ω∞-A Deliverable 7 §3.3:
   guards "make A-11 impossible"), and 5 done independently would build an input registry whose inputs
   cannot express N-of-M, a window or a peer state.
3. **3 before anything writes `registry.py`.** The only item in the table whose cost is genuinely zero
   and genuinely rises.

---

## 6. DETERMINATION

**No work is authorised, scheduled or approved by this document. No closure is declared. No readiness is
claimed.**

| Question | Determination |
|---|---|
| Does every item carry cost, risk and architectural impact? | **Yes** — cost and delay multiplier here, risk in §4, architectural impact in the per-area reports |
| Which items have a genuine deadline? | **Three.** Item 1 (epistemic, immediate), item 3 (before `registry.py`), item 4 (**partly passed**) |
| Which items are active defects rather than future barriers? | **Two.** 4½ (a complete route from insufficient inputs) and 11's bare-`str` corruption |
| How many ranks changed from Ω∞-A? | **Four, plus one new item at rank 1, plus one item split in two** |
| Which items rest on argument rather than measurement? | **Two: items 8 and 9** (storage, schema emitter). Both are absences rather than limitations, and both are recorded as ARGUED |

**The correction that most changes the plan.** Ω∞-A's rank 1 and 2 were chosen because both modules were
unbuilt and therefore free to get right. **One of them is not unbuilt.** The certification precondition
set exists today as a fixed enumeration of four, so the "design it out before it exists" window is half
closed — and the half that remains carries a constraint (retain `blocked_by`) that Ω∞-A did not record,
because Ω∞-A could not measure a module it believed absent.
