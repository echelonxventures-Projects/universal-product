# UCOS Ω∞ — Blocker Eradication and Implementation Readiness Determination

| Field | Value |
|---|---|
| Authority | **NONE — DERIVED TRUTH.** This determination legislates nothing, owns no gate and creates no registry. Every number below is a measurement, and the command that reproduces it is named beside it. |
| Constitutional superior | The instruments measured. |
| Method | Execution over documentation. Mutation over assertion. Deletion over coverage claims. Hostile audit over friendly verification. |
| Canonical gate | `./verify.sh --full` — **PASSED**, all 18 stages, whole suite under the 90% floor |
| Standing | ISSUED — findings recorded, closures implemented and re-attacked, residual blockers named with owners |

---

## 0. Determination

The repository is **not** UNCONDITIONAL READY FOR IMPLEMENTATION. Three blockers remain open,
each measured, named and owned. Eleven were found and closed, and every closure was attacked
afterwards rather than trusted.

The two most consequential findings were not missing features. They were **silences**:

1. An entire enforcement programme — a declaration, a sixteen-module engine, thirty-two laws
   and a passing suite — existed and was invoked by nothing, and **no gate in the repository
   could see it**, because it was untracked and every closure mechanism quantifies over tracked
   paths. Thirty-two laws measured nothing while every gate reported green.
2. Three certification identities did not move when the values deciding their verdicts moved.
   Flipping `blocking` on `UCON-L-01` — the flag its own contract reads to choose OPEN or
   CLOSED — left the declaration digest byte-identical at `192c63af…`.

Neither was hypothesised. Both were executed.

---

## 1. Phase 1 — baseline reality, recorded before any work began

| Measurement | Result at committed `HEAD` |
|---|---|
| `./verify.sh --full` | **FAILED** — 2 of 18 stages red |
| Full pytest suite | **41 failures** across 5 modules |
| `ruff check` / `ruff format --check` | clean over the *tracked* set; **101 violations** in an untracked package no gate could see |
| All 48 gate engines | measured — see §2 |
| All 32 workflows | enumerated — see §2 |
| `mypy` | **not installed, not configured, not invoked by anything.** `pyproject` pins exactly five dev tools: pytest, pytest-cov, coverage, ruff, jsonschema. UEG-000001 refuses an environment carrying an undeclared executable, so a type baseline cannot be produced without amending the declared toolchain. **Recorded as an owner decision, not silently skipped.** |

The 41 failures were **pre-existing and not caused by this campaign** — proven by running each
failing module against a pristine `HEAD` worktree before touching anything.

---

## 2. Phase 2 — enforcement set discovery

Cardinality is not asserted; it is derived on every run by rule, over `git ls-files`.

```
enforcement plane : 172 artifacts (172 governed, 0 withdrawn)
  DECLARATION        20     GATE_ENGINE     39
  MAKE_GATE_TARGET   54     MODULE_GATE      9
  VERIFY_STAGE       18     WORKFLOW        32
gate engines 48 · declarations 20 · test modules 604 · tracked paths 6,751
```

Reproduce with `make uec`. A hand-written list was refused as a design: it would agree with
itself forever.

---

## 3. Blocker inventory

Severity answers one question: **can certification stay green while the protection is absent?**

| # | Blocker | State |
|---|---|---|
| B-01 | Certification identity is a hand-written projection — a value that decides the verdict sits outside the digest certifying it | **CLOSED** |
| B-02 | The detector for B-01 was scoped to its own author and could never fire for anyone else | **CLOSED** |
| B-03 | An entire enforcement programme (URKE-000001) exists, passes, is invoked by nothing, and is invisible to every closure mechanism | **CLOSED** |
| B-04 | A declared classification rule (R-09) has no predicate — `classify()` returns `ERROR` for **every** subject | **CLOSED** |
| B-05 | Two declarations have no certification identity at all: their gates return verdicts attributable to no state | **CLOSED** |
| B-06 | 192 objects registered in two planes at once — the coverage matrix never read the `holds_object_classes` its own declaration carries | **CLOSED** |
| B-07 | 21 of URKE's 32 laws could be deleted outright with every gate green and the suite passing | **CLOSED** |
| B-08 | 2 of UCON's 16 laws likewise — including UCON-L-01, the foundational law | **CLOSED** |
| B-09 | Invocation matched on package names, so a gate pointed at a nonexistent module still read as invoked | **CLOSED** |
| B-10 | Every discovery floor could be lowered to 1, voiding the non-vacuity guarantee, with no refusal | **CLOSED** |
| B-11 | Any law could be switched off by setting `blocking: false` in data | **CLOSED** |
| B-12 | 18 gate engines have no test; 6 engines are invoked by nothing; 16 reachable from one plane | **OPEN — ratcheted, named, capped** |
| B-13 | 3 declarations no code loads; one terminates an authority chain | **OPEN — owner decision** |
| B-14 | `mypy` is absent from the declared toolchain, so no type baseline exists | **OPEN — owner decision** |

---

## 4. Root-cause hierarchy

Eleven of the fourteen reduce to three causes.

**Cause A — a boundary that decides visibility, applied to itself.**
Every closure mechanism quantifies over `git ls-files`. That is the correct boundary and it has
one consequence nobody had measured: *an artifact outside it is not merely ungoverned, it is
unobservable*. URKE-000001 sat in that blind spot. It was also outside the lint boundary, which
is scoped to tracked files for good and documented reasons, so it carried 101 invisible lint
violations too. **The moment it was tracked, three independent gates refused it within one
command** (UVI-L-11, UVI-L-13, UGA-INV-01/10). Nothing was wrong with those gates. They had
simply never been shown the subject. (B-03)

**Cause B — the necessary condition measured, the sufficient condition assumed.**
A property checked in its weak form cannot see the defect.
- UEC-L-08 asked *does an identity exist*. A stable digest over a projection passes it while
  certifying two different declarations with one value. (B-01, B-05)
- `validate_rule_coverage` computed that R-09 had no predicate, and **nothing gated on the
  result**, so the classifier failed open into `ERROR` for every subject. (B-04)
- `holds_object_classes` was loaded and used for one purpose, and the duplicate-registration
  rule never read it — so "appears in two files" was measured as "governed by two planes". (B-06)
- Invocation reused the generous needles written to answer *does a test name this engine*.
  (B-09)

**Cause C — a test that asserts only that the law holds.**
`assert law(probe) == []` is satisfied trivially by a law that has been deleted. These laws are
unusually good at forging their own hostile states internally, and **that is exactly why the gap
was invisible**: deleting the function deletes its internal forgery too, and no external observer
notices. 23 of 61 law mutants survived on that pattern alone. (B-07, B-08)

---

## 5. Phase 8 — mutation resistance

Every law check in every programme was replaced, one at a time, with `return []` — the
`return True` of a law engine — and the owning suite re-run against the mutant in an isolated
worktree.

| Programme | Laws | Before | After |
|---|---|---|---|
| UCPA-000001 | 8 | 8 killed, 0 survived | unchanged |
| UISD-000001 | 11 | 11 killed, 0 survived | unchanged |
| UCON-000001 | 16 | 14 killed, **2 survived** | **16 killed, 0 survived** |
| URKE-000001 | 32 | 11 killed, **21 survived** | **32 killed, 0 survived** |
| UEC-000001 | 13 | 12 killed, **1 survived** | **13 killed, 0 survived** |

**Mutant survival rate: 0 of 80.**

The two UCON survivors were `every_construct_is_disposed` (UCON-L-01, the foundational law) and
`measurement_is_deterministic` (UCON-L-16). Both could be deleted outright while every gate
reported OPEN.

Closing them required 26 new forged-violation tests: 13 forge the declaration, 3 empty the
ledger, 5 forge the collaborator the law delegates its refusal to, and 5 forge a population above
a ratchet ceiling. Each was verified to kill its mutant by re-running the campaign, not by
inspection.

A **class-level guard** was added to both suites so the next law arriving without a test fails
immediately: every name in `LAW_CHECKS` must appear in the suite that owns it. Naming is
necessary, not sufficient — it is the strongest property available in-process, and it closes the
door the survivors came through.

## 6. Phase 9 — deletion resistance

| Deletion | Result |
|---|---|
| The CI entry point (`ec1-ci.yml`) | REFUSED |
| The UEC / UCON / URKE workflow, individually | REFUSED |
| **Seven workflows at once** | REFUSED |
| A gate engine (construct, recursive-knowledge, UGA) | REFUSED |
| A governed declaration | REFUSED |
| The whole `Makefile` | REFUSED (fault) |
| `verify.sh` itself | REFUSED (fault) |
| A governed test module | REFUSED |
| **Every `run_stage` line stripped from `verify.sh`** | REFUSED |

**13 of 13 detected.** The seven-workflow case is the scenario UEC-000001 was written for: it
was measured surviving before this programme existed.

## 7. Phase 10 — hostile re-audit

Eleven attacks, chosen as the quiet routes rather than deletion.

| Attack | First pass | After closure |
|---|---|---|
| A gate engine / workflow / Make target added outside governance | REFUSED | REFUSED |
| A governed gate engine relocated | REFUSED | REFUSED |
| Every ratchet ceiling raised | REFUSED | REFUSED |
| A discovery pattern that matches nothing | REFUSED | REFUSED |
| Withdrawing a live artifact instead of deleting it | REFUSED | REFUSED |
| UEC removed from its own governed inventory | REFUSED | REFUSED |
| **Every discovery floor set to 1** | **SURVIVED** | REFUSED |
| **A gate pointed at a module that does not exist** | **SURVIVED** | REFUSED |
| **A law switched off with `blocking: false`** | **SURVIVED** | REFUSED |

**11 of 11 refused.** The three survivors were real bypasses and each is worth naming:

- **Floors.** Setting every floor to 1 left UEC-L-01 green: each rule still located far more than
  one artifact, so the non-vacuity guarantee evaporated while the measurement kept reporting
  satisfaction. Floors are now ratcheted on their total, two-sided.
- **Detachment.** Pointing the Makefile target, the `verify.sh` stage and the workflow of a live
  gate at `engine.recursive_knowledge.NOTHING` — all three at once — left UEC-L-04 green, because
  the bare package was still a needle and appeared in every one of those lines. The gate had
  stopped running and nothing said so. Invocation now requires an executable form.
- **Law disabling.** Written as a law first, and the audit walked straight through it: `measure()`
  closes only on a law that is refused *and* blocking, so flipping `blocking` on the law carrying
  the check made it report the violation and made the report unable to close anything. The
  detector was disabled by the exact mutation it detects. It is now refused at **load**, before
  any law is measured, as a fault rather than a verdict.

The detachment fix then exposed something the generous matcher had been hiding: **six engines
that nothing can actually run**, four of them "invoked" only because `make uakos-archive` checks
that their *directory* exists. They are now named, capped and ratcheted.

---

## 8. Certification identity evidence

| Declaration | Before | After |
|---|---|---|
| UCON-000001 | 11 keys, 10 collapsed to bare identifiers | 37 parsed fields, inclusion by default |
| URKE-000001 | 13 keys; **101 of 115** parsed fields outside the identity | 114 parsed fields |
| UCPA-000001 | **no identity at all**; name/version/authority/principle unparsed | complete; all four now parsed |
| UISD-000001 | **no identity at all** | complete |
| UEC-000001 | already inverted | unchanged |

Five of twenty governed declarations are now proven complete **by mutation, under a blocking
law, inside the canonical gate** (UEC-L-13). Fifteen are held to the necessary condition only,
and that limit is written into the declaration rather than left to be discovered.

The remedy is **inversion**: the payload is derived from `dataclasses.fields`, so a field is
inside the identity unless `DIGEST_EXCLUSIONS` names it and states why it cannot reach a verdict
— and the suites fail in *both* directions, on an undeclared omission and on a stale exclusion.

---

## 9. Non-vacuity evidence

Non-vacuity is computed everywhere it can be. `UCON-L-07` seeds an unattended unknown and an
escalation into a fresh registry and **refuses if discovery mints nothing**. `UEC-L-01` holds a
per-rule population floor, refuses a floor of zero at parse, and now ratchets the floor total.
`UEC-L-13` carries `IDENTITY_MUTATION_FLOOR = 2` and reports a declaration fewer than two
mutations reach as **unmeasured rather than passing**.

That last guard was itself found by execution: an early version of UEC-L-13 *invented* a
`blocking` key on declarations that carry none, and a parser that never reads the key left the
digest unchanged — the law reported a certification bypass that was its own artefact. Mutations
now carry a guard and unapplied ones are skipped and counted.

A related hole was found the day a ratchet first reached zero: the two-sided test read
`max(ceiling - 1, 0)`, which mutates nothing at a ceiling of zero, so the refusal being asserted
was the absence of a change. Every ratcheted law is now additionally tested by forging one more
offender than its ceiling allows — the half a neutered law cannot satisfy.

---

## 10. Remaining blockers

### B-12 — 18 engines with no test, 6 with no invoker, 16 on a single plane (ratcheted)

Six are the severe case: no test **and** no invoker. The repository has already measured what
this costs — a one-line `return True` in `UIS-001/uis_engine.py` and `ACEE-000001/acee_engine.py`
flipped both gates from CLOSED to OPEN, all nine of UIS's own self-guards still passed, and no
test file anywhere referenced either programme.

Every count is named, capped and two-sided. None can grow. Reducing them is ordinary work.

### B-13 — three declarations no code loads (owner decision)

`ceu-declaration.json`, `urr-declaration.json`, `ucxi-declaration.json`. Not a missing loader —
a **second declaration form**: an `implementation` block naming modules and five `invariants`
written as English sentences, with no parser and no bound check. `engine/ceu/catalog.py`
hardcodes the ten CEU seed populations in Python while `ceu-declaration.json` describes them and
is loaded by nothing, so the artifact calling itself the CEU vocabulary is not the authority —
the Python file is. And `ucon-declaration.json` names `UCXI-000001` as its constitutional
superior, so **one authority chain terminates in a document nothing loads**.

A closure exists and was **deliberately not implemented**: a law could load all three and enforce
their structural fields. It was rejected because the closure detector would become their only
consumer, and "consumed by the thing that measures consumption" is not governance — it would
turn UEC-L-07 green while changing nothing about who enforces the five prose invariants. That is
metric repair, not defect repair.

### B-14 — no type-check baseline (owner decision)

`mypy` is not installed, not configured and invoked by nothing. Adding it means amending the
pinned toolchain UEG-000001 enforces, which is a governance act.

### Recorded and NOT closed by unilateral action

The 192 two-plane registrations (B-06) were closed by making the matrix read the
`holds_object_classes` its declaration already carries — **not** by deleting entries from a
permanent append-only identity ledger. Deleting them would have violated identity immutability
(UOBC-L-03/L-08) and the single-identity-authority invariant (CAA-INV-04): repairing a
measurement by mutating the thing it measures is the shape of fix this campaign exists to refuse.
The residual raw overlap is held as a two-sided ratchet at 192 so it cannot grow silently.

---

## 11. Readiness determination

**NOT UNCONDITIONAL READY FOR IMPLEMENTATION. NOT CERTIFIED.**

Phase 12 admits that declaration only if every condition holds. Three do not: B-12, B-13, B-14
are open. Two of them are owner decisions and one is ordinary work.

The highest state the evidence supports, and nothing stronger:

> **ADVERSARIALLY CLOSED OVER THE ENFORCEMENT SURFACE, WITH THREE RECORDED BLOCKERS.**
>
> - Mutation survival: **0 of 80** law mutants.
> - Deletion detection: **13 of 13**.
> - Hostile attacks refused: **11 of 11**.
> - Enforcement-set closure: two-way, over 172 artifacts; addition and deletion both fail closed.
> - Certification identity: complete and mutation-proven for 5 of 20 declarations; the
>   remaining 15 are held to the necessary condition and that limit is declared, not implied.
> - Self-coverage: UEC is inside UEC (UEC-L-09); the extensibility audit refused its own
>   author's code and the three new closures are disclosed as UCON-CL-18/19/20.
>
> Three blockers remain open, each named, owned and — for two of them — carrying a designed
> closure that was deliberately not implemented because implementing it would have been metric
> repair rather than defect repair.

**What would change the verdict**, in ascending cost: a toolchain decision on `mypy`; a decision
on whether the three descriptive declarations become executable or are withdrawn; tests and
invokers for the engines that have neither.

---

## 12. Reproducing every claim

```bash
./verify.sh --full                       # the certification contract, 18 stages
make uec                                 # 13 laws, 5 ratchets, every offender named
make ucon urke ucpa uga                  # the other fail-closed gates
python -m engine.enforcement_closure.gate --gate --law UEC-L-13
python -m pytest engine/tests/unit/test_enforcement_closure.py -k "l13 or non_blocking or floor"
python -m pytest engine/tests/unit/test_recursive_knowledge.py -k refuses
python -m pytest engine/tests/unit/test_registry_coverage_matrix.py
```

Every number in this determination came from one of those commands, from the mutation harness,
or from the deletion and hostile batteries. Where a claim could not be produced by execution, it
is written above as unproven.
