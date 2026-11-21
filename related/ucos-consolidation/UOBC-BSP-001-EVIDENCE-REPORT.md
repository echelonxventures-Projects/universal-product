# UOBC-BSP-001 Certification Evidence Report

| Field | Value |
|---|---|
| CAPABILITY | `UOBC-BSP-001` — Universal Birth Scope Policy |
| ITEM | Scope B · B-01 — Machine-Readable Birth Scope Governance |
| EXTENDS | `UOBC-000001` (scope of application only) |
| CONSTITUENT AUTHORITY | **NONE** |
| POLICY | `00-MASTER/UOBC-000001/birth-scope-policy.json` |
| DETERMINATION | `B-01-BIRTH-SCOPE-GOVERNANCE-DETERMINATION.md` |
| PLAN | `B-01-IMPLEMENTATION-PLAN.md` |

---

## 1. Objective

`SCOPE-B-BIRTH-GOVERNANCE-DETERMINATION.md` §1.2 determined which object kinds require a birth record and which must never hold one independently. **That determination lived only in prose, so nothing computed it.** A generated artifact could be given an independent constitutional identity; a birth record could name a subject that does not exist; the adoption gap could widen with no signal.

B-01 converts that rule into data and measures it — the same upgrade `UCPA-000001` performed in Scope A for the root ontology.

Two obligations, both now enforced:

* *Every object that requires constitutional existence must have governed birth identity.*
* *Objects that are derived projections or generated artifacts must not receive independent birth identity.*

---

## 2. Existing Authority Reused

| Claim | Evidence |
|---|---|
| **Existing UOBC authority reused** | Policy lives under `00-MASTER/UOBC-000001/`; measurement lives in `engine/object_birth/`; gated by the **existing** UOBC stage in `verify.sh`. No new stage, no new programme. |
| **No new identity authority** | Structural check over the policy's *data* fields: **no counter-shaped field exists**. The only integers are the four coverage floors, which do not advance on mint. `category_seq` appears in prose only. The ledger's counters are **unchanged at 117**. |
| **No new registry** | The policy declares kinds; it stores no objects. Classification is evaluated over registries that already exist — UGA object registry, generated-artifact registry, birth ledger. |
| **No duplicate lifecycle** | Lifecycle binding remains `UCIC-001` (owner) · `UCL-000001` (derived). B-01 declares none. |

---

## 3. Implementation Summary

### Files added
| Path | Lines | Role |
|---|---|---|
| `00-MASTER/UOBC-000001/birth-scope-policy.json` | ~200 | 10 kinds · 5 subject-resolution rules · 4 coverage floors · 6 laws |
| `engine/object_birth/scope.py` | 378 stmts | Model, ordered classification, six law checks, public API |
| `engine/tests/unit/test_birth_scope.py` | 51 tests | Both directions per law |
| `B-01-BIRTH-SCOPE-GOVERNANCE-DETERMINATION.md` | 92 | The determination |
| `B-01-IMPLEMENTATION-PLAN.md` | — | The change contract |

### Files modified
| Path | Change |
|---|---|
| `engine/object_birth/gate.py` | Measures the 6 BSP laws alongside the 8 UOBC laws — one report, one exit code |
| `engine/object_birth/__init__.py` | Public surface export |
| `engine/tests/unit/test_object_birth.py` | One pinned literal replaced by a derived expectation (§5, D-5) |
| `00-MASTER/UOBC-000001/birth-ledger.json` | 3 birth records for the objects B-01 creates (35 → 38) |
| `00-MASTER/UVI-000001/uvi-declaration.json` | +5 lines — one isolation declaration (§5, D-6) |

### Public APIs added
```
evaluate(path, policy, ctx) -> Verdict(path, object_kind, birth_required, verdict, reason, authority)
load_policy() · load_context() · classify() · resolve_subject() · assess_scope() · summarize()
```
`Verdict.verdict` ∈ `{PASS, FAIL, EXCEPTION}` — answering the three mandated questions: does this object require birth; if yes does a valid birth exist; if no is the absence correct.

### Laws implemented
| Law | Statement |
|---|---|
| `BSP-L-01` | The policy is structurally usable — every kind complete, every `validation_rule` implemented **and consistent with its enforcement**, both directions |
| `BSP-L-02` | Classification is total and single-valued — exactly one catch-all, declared last |
| `BSP-L-03` | No derived object holds an independent birth |
| `BSP-L-04` | Every birth record names a subject that exists and may be born |
| `BSP-L-05` | Adoption is disclosed, never silent — a `DEFERRED` kind must name its gap |
| `BSP-L-06` | Birth coverage is a ratchet — it may rise or hold, never fall |

---

## 4. Governance Validation

Every row below was **executed**, not asserted.

| Condition | Evidence |
|---|---|
| Rules are data-driven | 10 kinds declared in JSON; **0** kind names or gap ids in executable code (AST scan of non-docstring string literals) |
| `validation_rule` is executable | Refuses an unimplemented rule; refuses a rule whose enforcement contradicts the kind's; refuses an implemented rule no kind claims |
| Mandatory birth classes enforced | Same object, same absence: `adoption: DEFERRED` → `EXCEPTION`; `adoption: MANDATORY` → **`FAIL`** |
| Generated artifacts | 344 classified; no birth → `PASS`; forged birth → **`FAIL`** |
| Derived artifacts | `DERIVED_REGISTER` declared `MANDATORY_ABSENCE` as a second net for objects UGA marks `GENERATED` before the generated registry lists them |
| Deferred exceptions | `EXCEPTION` verdict carries the gap id: *"birth required; adoption deferred under G11"* — 1,152 disclosed |
| Unknown object kind | Catch-all removed → `FAIL`, and `BSP-L-02` refuses |

**Measured population:** 6,079 objects at implementation time → `PASS 4,927 · FAIL 0 · EXCEPTION 1,152`, **0 unresolved**.

**Backfill refused.** `G11`'s disposition — *"an explicit `register.sh` migration transaction, not a verification-time backfill"* — is not reopened. Measured coverage before writing the policy: capability packages **6/43**, test suites **7/821**, determinations **17/253**. No kind is at 100%, so a blanket mandate would have closed the gate on the whole repository on day one. The enforceable honest form is UISD's: **refuse the undisclosed gap, not every gap.**

---

## 5. Defects Discovered

### D-1 — `local_name_pattern` matched as a literal prefix, not a regex
* **Detection** — `BSP-L-06` refused: `PACKAGE: 0 birth records, below the declared floor of 6`.
* **Root cause** — the policy declares `local_name_pattern` as a regular expression (`^engine\.`). The first implementation stripped the anchor and compared string prefixes, so the escaped `\.` never matched. **Zero of six** capability births resolved.
* **Fix** — match with `re.search`, failing closed on `re.error`.
* **Regression prevention** — `test_every_declared_namespace_resolves_a_real_birth` asserts every committed birth resolves; `BSP-L-06` fails closed on any regression below the measured floor.

### D-2 — `validation_rule` was decorative
* **Detection** — reading `BSP-L-01`'s statement against its implementation: the law *claimed* to check `validation_rule` against implemented checks; the code checked only selector operators.
* **Root cause** — a law asserting more than its check measured — the exact defect class `UCPA-000001` exists to prevent, reproduced inside B-01.
* **Fix** — `VALIDATION_RULES` maps each rule to the enforcement it implements. `BSP-L-01` now refuses an unimplemented rule, a rule contradicting its kind's `enforcement`, and an implemented rule no kind claims.
* **Regression prevention** — three tests, one per refusal direction, plus `test_every_implemented_rule_and_operator_is_reachable`.

### D-3 — O(n²) evaluation
* **Detection** — the test suite exceeded a 120-second timeout.
* **Root cause** — `evaluate()` recomputed `_born_paths()` per object, and that scanned all 6,079 objects per birth to resolve test-suite basenames.
* **Fix** — path and basename indexes built once in `load_context()`; `_born_paths` memoised. **>120 s → 0.11 s.**
* **Regression prevention** — the UOBC gate runs on every `--change`/`--integration`/`--full`; a return to quadratic cost is immediately visible in stage time.

### D-4 — memo keyed on presence, not content
* **Detection** — reasoning about the negative tests: they build a forged context with `dict(ctx)`, which **copies the memo**, so a forged ledger would have been answered about the ledger it replaced — the tests would have passed vacuously.
* **Root cause** — `ctx.get("_born_paths")` returned any cached value regardless of which births produced it.
* **Fix** — the memo is keyed on `frozenset(ctx["births"])` and recomputed when that changes.
* **Regression prevention** — verified directly: forging one birth moves the count 35 → 36, proving invalidation.

### D-5 — an existing test pinned a law count
* **Detection** — `test_gate_measures_the_committed_ledger` failed `assert 14 == 8` after the gate gained the 6 BSP laws.
* **Root cause** — the expectation was a literal.
* **Fix** — replaced by `test_gate_measures_every_law_both_instruments_declare`, deriving the count and the id set from both declarations. Re-pinning to 14 was rejected: *an expectation that must be edited to stay true stops being checked.*
* **Regression prevention** — the test now cannot go stale when either instrument gains a law.

### D-6 — Research Intelligence gate non-determinism *(pre-existing, exposed by B-01)*
* **Detection** — `./verify.sh --fast` failed at `intelligence/tests/test_research_intelligence.py::test_gate_opens_and_reports_a_seal` with `assert 1 == 0`, reproducibly (3/3), while passing in every isolated run.
* **Root cause** — `intelligence/research/assimilation.py` derives research **findings** from `coverage.xml`, a gitignored run-scoped artifact. `ResearchIntelligenceEngine` caches `_corpus` on the instance while `verify_determinism()` re-reads fresh, and the fixture is `scope="module"`, holding that cache across ~20 tests. Twelve concurrent shards each rewrite `coverage.xml`, so a rewrite lands between the two reads.

  Proven three independent ways:
  1. **Live measurement** — `coverage.xml` changed **17 times in 80 seconds**, repeatedly to `e3b0c44298…`, verified as the empty-file digest (truncated).
  2. **Controlled experiment** — mutating `coverage.xml` between cache and re-read reproduced `deterministic: False`, the same 5 mismatched outputs and `gate` exit `1`; restored byte-identically afterwards.
  3. **The failing run's own locals** — `deterministic=false` with `checks=13/13 PASS`, **findings 18 → 14, records 203 → 198** — exactly the coverage-derived items, lost mid-read.

* **Classification — B: pre-existing verification lifecycle defect exposed by UOBC-BSP-001.** B-01 touches none of `coverage.xml`, the research engine, or its substrate; it added one test object (570 → 571), shifting shard composition so the cache window began overlapping a rewrite. Corroborated independently: `intelligence/tests/test_rie.py` **already guards this exact class** for the RIE model — *"canonical model carries coverage-derived fields, which makes its identity a function of test-execution state"*. The research corpus carries the same hazard with no such guard.
* **Fix** — declared `intelligence/tests/test_research_intelligence.py` isolated in the UVI constitution (**+5 lines, no code changed**). UVI's own words: isolation *"is SCHEDULING: it says an object may not run beside anything else, **never that it may not run**."* The determinism assertion is unchanged and still fail-closed; nothing is bypassed, retried or suppressed. The gate was never wrong — its premise of an unchanging repository state was being violated by the verification run itself, and isolation makes that premise true rather than weakening the claim.
* **Regression prevention** — `UVI-L-*` validates every isolation entry: the prefix must resolve to a currently collectible object (a stale prefix fails rather than sitting inert) and must carry a measurement justifying it. Wave 0 was then run as it will actually run — both isolated objects together, **40/40 green** — confirming co-location does not break the purity test's whole-tree guarantee.

**Two hypotheses discarded on evidence:** the `00-BOOK/DATA/artifacts.json` write-restore at t=52–53 is real but wave-0-confined and not the cause; and my substrate sampler reported "no change" because `coverage.xml` is not a *declared* substrate surface — I was watching the wrong file.

---

## 6. Test Evidence

| Measure | Value |
|---|---|
| New tests (`test_birth_scope.py`) | **51** |
| Existing UOBC tests | **95** (unchanged in intent; one derived, D-5) |
| Combined UOBC + BSP | **146 passed** |
| Whole suite, every mode | **11,888 passed · 0 failed · 3 skipped** |
| `engine/object_birth/scope.py` coverage | **93%** |
| Repository coverage | **97%** against a 90% floor |

---

## 7. Verification Evidence

| Mode | Exit | Stages passed | Stages failed | Tests | Coverage | UOBC+BSP stage |
|---|---|---|---|---|---|---|
| `./verify.sh --fast` | **0** | 3 | 0 | 11,888 | 97% | SKIP (declared: change/integration/full) |
| `./verify.sh --change` | **0** | 11 | 0 | 11,888 | 97% | **PASSED** |
| `./verify.sh --integration` | **0** | 14 | 0 | 11,888 | 97% | **PASSED** |
| `./verify.sh --full` | **0** | **15/15** | 0 | 11,888 | 97% | **PASSED** |

**Gate results:** UOBC + BSP `exit 0` (**14/14 laws**: 8 UOBC + 6 BSP) · UVI `exit 0` (10/10) · UCPA `exit 0` (8/8) · UGA 29/29 invariants.

**Derived state:** fixed point at pass 1 · **0 unstaged modifications** · **0 untracked** · births 38 · `category_seq` **117 (unchanged)** · governed objects 6,087.

---

## 8. Certification Decision

# CERTIFIED

`UOBC-BSP-001` is certified. All four verification modes exit 0, 15/15 stages pass under `--full`, 11,888 tests pass with zero failures, coverage holds at 97% against a 90% floor, all gates are green, the derived registers are at a fixed point, and the working tree carries no drift.

Six defects were found during implementation; all six are fixed, and each carries a regression control that is executed rather than asserted.

---

*End of UOBC-BSP-001-EVIDENCE-REPORT.md*
