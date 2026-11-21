# Final Certification Report

**Programme** UCI-000001 Universal Certification Integrity
**Certification SHA** `74d9f8443acd76302e3826bfda47323b0cbe8772`
**Frozen-extraction seal** `2d66530608871bab06ab3f334169c971df3f8c4e` (content-addressed)
**Branch** `integration/recovery-001`
**Inventory digest** `b9a9f3221d1179c4`
**Authority** NONE — DERIVED TRUTH. Every figure is reproducible with `make uci`.

---

## VERDICT: CERTIFICATION REFUSED

The mandate's Rule 14 permits acceptance only if eleven conditions hold simultaneously. **Four
hold. Seven do not.** No certificate is issued.

| Rule 14 condition | required | measured | verdict |
|---|---|---|---|
| Measured test coverage | 100.00% | **97.08%** | ✗ |
| Executable-surface coverage | 100.00% | **~79.9%** (see §3) | ✗ |
| Governance-surface coverage | 100.00% | **0%** of 39 gate engines measured | ✗ |
| Verification coverage | 100.00% | 20 of 20 verify.sh stages invoked | ✓ |
| Mutation coverage | 100.00% | **not measured** | ✗ |
| Invocation coverage | 100.00% | 14 engines below 2 planes | ✗ |
| Certification reproducibility | 100.00% | A==B==C on measured scope | ✓ (bounded, §5) |
| UEC debt counters | all 0 | **18 / 6 / 15 / 3 / 0** | ✗ |
| Declared exceptions governed | yes | 1 (`engine.uicm`), reasoned + tested | ✓ |
| Clean-clone run from immutable SHA | reproduces | seal deterministic, suite runs | ✓ (§4) |
| No unresolved findings A-4…A-13 | closed | **identifiers unresolvable** (§8) | ✗ |

Refusing is the result, not a failure to produce one. A certificate issued against these
measurements would be the precise artifact the mandate exists to prevent.

---

## 1. What the reported coverage figure was actually a figure of

At session start `coverage.xml` reported **97.9% of 83,142 statements**. That was arithmetically
correct and answered a question about **49.4% of the executable surface**.

| | session start | now |
|---|---|---|
| tracked non-test Python files | 1,524 | 1,335 |
| executable statements | 183,310 | 156,787 |
| statements in the denominator | 96,070 | **128,682** |
| **denominator share of surface** | **52.4%** | **82.07%** |
| files in the denominator | 905 | **1,259** |
| executable files outside it | 607 | **65** |
| files claimed by no authority | 570 | **27** |

The denominator grew by **34%** and the reported percentage went *down* (97.9% → 97.08%). Nothing
was excluded to achieve it. That direction is what separates correcting a denominator from
laundering one.

---

## 2. Total coverage

From the sharded certification run at `78b62b30`, `coverage combine` + `coverage report` over the
union of 12 shards:

```
TOTAL   125,217 statements   3,654 missing   27,488 branches   96%
coverage.xml root:  lines-valid 125,217   lines-covered 121,563   line-rate 0.9708
```

**97.08% line coverage over 125,217 statements.** Branch coverage 25,148 / 27,488 = 91.5%.

The run had failures in 5 of 12 shards. Three were `test_certification_integrity` failures fixed
in `d190fb19`, one was `test_closure009`'s testpaths scrape fixed in the same commit, and one was
`test_constitutional_authority_alignment` refusing my unregistered objects, fixed in `4f590dda` by
UGA registration. All are green now, but **no full sharded run has been executed since those
fixes**, so the 97.08% figure is from a run with known failures and is not itself a certification.

---

## 3. Executable coverage

**Executable-governed surface: 156,787 statements. Inside the denominator: 128,682 (82.07%).**

Coverage *of the surface* cannot be stated exactly from the current artifact, for the reason in
§7: `coverage.xml`'s body describes 67,279 of the 125,217 statements it claims. Bounding it:

- measured statements covered: 121,563 of 128,682 → **94.5% of the denominator**
- as a fraction of the whole executable surface: 121,563 / 156,787 → **77.5% lower bound**
- the 28,105 unmeasured statements are of unknown coverage, so the true figure lies between
  **77.5% and 95.4%**, and **~79.9%** using the denominator's own rate for the unmeasured part.

A single number is not available and is not invented here.

---

## 4. Immutable-run proof (Rule 7)

Implemented in `engine/certification_integrity/immutable.py`. Verified:

- `git archive <sha>` piped directly into `tar`, so a partial archive cannot be extracted as whole
- extraction sealed into a git repository with author, committer and both dates pinned
- **seal is content-addressed:** two independent extractions of one commit produced
  `b2c9f886d56b462b71133c18193a149f1a39a9cd` **both times**
- different content produces a different seal (asserted)
- `git status` inside a sealed extraction is clean; harness artifacts excluded via
  `.git/info/exclude`, which is untracked, so the sealed commit stays pristine
- outer-repository HEAD, porcelain digest and tracked-file digest sampled before and after every
  run; `require_stable` discards any measurement whose tree moved

**A measured discovery that Rule 7 could not have anticipated:** the suite **cannot be collected
from a bare `git archive` extraction at all.**
`engine/execution_environment/discovery.py:79` raises *"no repository root could be resolved … git
did not answer and no .git was found"* and pytest aborts. `enforcement_closure.tracked_paths`
treats a missing work tree as a FAULT by design, and every gate deriving its population from
`git ls-files` does the same. An extraction with no git is not a stricter measurement — it is an
unmeasurable one. Hence the seal, which is *stricter* than the working tree: no untracked files,
no ignored files, clean by construction, and nothing else knows the repository exists so nothing
can advance HEAD.

---

## 5. Reproducibility proof (Rules 8 and 11)

Three independent runs inside one frozen extraction, compared as **covered-line sets per file**,
never as percentages:

```
A == B  : True
B == C  : True
digests : identical across all three
```

Scope: `data/tests`, 954 tests, 7,536 statements, `--cov=data`. **Bounded, and stated as bounded.**
Extending to the full suite is a parameter change (`runs=3`, no target filter); the cost is the
constraint, not the capability — one single-process full run exceeded 55 minutes without
completing, and the repo's own sharded path takes ~9 minutes per wave across 6 waves.

Percentages are deliberately not used for the comparison: two runs that executed *different* lines
routinely report the same ratio, so a percentage comparison passes on exactly the divergence being
tested for. `test_the_comparison_detects_a_single_moved_line` proves the primitive detects a
one-line difference between two reports whose percentages are equal.

---

## 6. Order independence (Rule 9)

`engine/certification_integrity/pytest_shuffle.py`, 40 governed lines, no new dependency.

```
seeds run              : 25
failures               : 0
coverage drift         : 0
identical to declared  : True
```

Opt-in twice over (`-p` **and** `UCI_SHUFFLE_SEED`), so the default order is untouched and
UVI-L-08's deterministic-sharding contract stays measurable. `pytest-randomly` was rejected
deliberately: it reseeds collection by default, which would change the meaning of every existing
green run.

Verified non-vacuous: seed 7 genuinely reorders, reproduces across invocations, differs from seed
8, loses no items, does not disturb the global `random` stream, and echoes its seed into the run
header so a failing permutation is replayable.

**N = 25, not 100.** At ~3.5s per run over this scope, N=100 is ~6 minutes and reachable; over the
full suite it is ~90 hours. The harness takes N as a parameter.

---

## 7. Shard equivalence (Rule 10) — and the defect it found

Round-robin partition over sorted test modules, deliberately **not** UVI's cost-weighted LPT
assignment, because an audit that ran the audited code would be a tautology.

```
                 statements  covered   percent  branches_valid
whole run              7,536    7,347   97.492           1,384
combine(4 shards)      7,536    7,347   97.492           1,384
files with differing lines: 0
```

**Every quantitative claim Rule 10 names holds exactly.** File-*identity* equality could not be
verified, and the reason is a real defect:

> **`coverage.xml` describes less than half of what it claims.**
>
> ```
> coverage report (terminal)   1,259 files   125,217 statements   96%
> coverage.xml root element                  125,217 statements
> coverage.xml body              644 files    67,279 statements
> absent from the body                         57,938 statements (46.27%)
> ```
>
> `[tool.coverage.run] source` names 78 roots, and the five admitted layers share module
> basenames. `coverage xml` emits one `<class filename=…>` per distinct *relative* name, so
> `data/governance.py` and `application/governance.py` both reduce to `governance.py` and the
> loser is dropped from the body. The `.coverage` data file is correct — a two-layer probe holds
> 140 distinct measured files — so this is purely a rendering defect.
>
> **The percentage is unaffected, which is what makes it dangerous.** Every summary agrees. Only a
> per-file consumer sees 644 files where there are 1,259, and absence renders as nothing rather
> than as zero. `ec1-ci.yml` uploads this file as the `coverage-xml` artifact, so any dashboard,
> IDE gutter or external quality gate reading it has been reading half the repository.

Now detected and reported by `make uci` (`CoverageReport.body_is_incomplete`). Not ratcheted: the
defect is in `coverage xml`, so a ceiling here would be a ceiling on someone else's bug. The fix
is to give coverage a single source root, which changes the governed denominator's mechanics and
belongs in its own measured change.

This defect also produced a **false Rule 10 finding** first: resolving a bare filename as "the
first source root where a file of that name exists" reported 19 files present in one run and
absent in the other with every line set identical. The coverage was right and the reader was
wrong. `_relative` now refuses to guess.

---

## 8. False-green audit (Rule 12)

Five distinct false-green paths were found and measured. Four are closed.

| # | false green | measured | status |
|---|---|---|---|
| 1 | **3,995 tests that no runner collected.** `service/tests`, `data/tests`, `application/tests`, `infrastructure/tests` — 188 modules, all passing, in no `testpaths`, no Makefile target, no verify.sh stage, no workflow. A reader who opens `data/tests` and finds 954 passing tests reads evidence no gate ever executed. | 3,995 tests, 14.7s, 29,970 statements at 98% | **CLOSED** |
| 2 | **`intelligence/` collected but unmeasured.** UCOS-CL-008 admitted its tests and recorded the denominator as "a separate question, answered separately below". The separate answer was never given. | 5,363 statements at 87% | **CLOSED** |
| 3 | **A namespace package invisible to the scope gate.** `engine/recursive_knowledge` — URKE-000001, a verify.sh stage with workflow and Makefile target and 135 tests — was in neither scope list nor the exclusion list, and every scope test passed, because enumeration asked whether `__init__.py` existed. | 2,849 statements at 83% | **CLOSED** |
| 4 | **A coverage.xml with a valid document inside it.** Two processes wrote one path concurrently; the result had a complete valid document at lines 1–90,556, a second process's content after it, and a second `</coverage>` at the end. A consumer reading the first document gets a valid-but-wrong report; one checking the tail sees a proper closing tag. Preserved at `.uci-evidence/coverage.xml.truncated-by-concurrent-run`. | 3.85 MB | **CLOSED** — reader refuses unparseable input instead of salvaging |
| 5 | **coverage.xml describing 46% of what it claims** (§7). | 57,938 statements absent | **DETECTED**, not fixed |

A sixth, structural: **39 of 39 governance gate engines are measured by nothing** (20,359
statements). A gate whose own executed fraction is unknown can rot into a no-op and keep reporting
OPEN. Not closed — those files are executable as scripts but not importable as modules, so
admitting them requires a real change.

**Rule 13 (findings A-4…A-13) is unresolved for a different reason:** the identifier `A-n` is
reused as a generic list label across dozens of determination documents (`00-MASTER/UCOS-EG-001`,
`H-06-PRE-IMPLEMENTATION-REPOSITORY-STATE-VALIDATION.md`, `UCCEP-000006`, `EC2-EPIC-005/006`, …).
No single register defines A-4 through A-13 with A-9 absent. **I could not identify the intended
source and did not guess.** Naming it would let me close these items in prose, which Rule 13
explicitly forbids.

---

## 9. Governance coverage and self-enforcement (Rule 3)

Six laws, all blocking, all two-sided, declared in `00-MASTER/UCI-000001/uci-declaration.json`:

```
UCI-L-01  coverage_scope_equals_executable_scope     65 / 65
UCI-L-02  every_file_has_a_governing_authority       27 / 27
UCI-L-03  governance_engines_are_measured            39 / 39
UCI-L-04  every_engine_has_a_test                    25 / 25
UCI-L-05  every_engine_has_two_invocation_planes     14 / 14
UCI-L-06  measured_files_have_execution_paths        10 / 10
UCI-L-07  every_ceiling_binds_a_measurement           0
STATUS: OPEN
```

Every ceiling is a **ceiling to be driven to zero, not a budget**. The ratchet refuses in both
directions: above is new debt, below is debt repaid without tightening — slack a future regression
could occupy in silence. That lower side fired for real during this session, refusing at 65/607
and forcing `78b62b30`.

The programme governs itself under the rules it imposes: four new enforcement artifacts, all four
registered in UEC-000001's inventory (178 → 182) in the same commit that created them, two
invocation planes, 62-test non-vacuity suite, and UGA-001 identities minted for all 13 objects.
UGA-INV-01/INV-10 correctly refused them until registered — self-enforcement working, not an
obstacle.

**UEC-000001: OPEN**, 182 artifacts, all five ratchets at equality.

**UCON-000001** refused this work and was satisfied properly rather than
accommodated. The twelve closure constructs the new package introduced pushed four
outside-scope populations above their baselines, and UCON's rule is that such a
population "may hold, and it may fall" but never rise. The sanctioned remedy —
widen `governed_scope`, never raise the baseline — was taken: all twelve are now
disclosed with a closing invariant and an admission path, and the baseline is
untouched. Raising it would have bought silence for someone else's future closure
as well as mine.

**Gate sweep at this SHA**, all exit 0: `certification_integrity`,
`enforcement_closure`, `recursive_knowledge`, `construct`, `object_birth`,
`root_ontology`, `uaue`, `verification_intelligence`, `infinite_scope`, `uga`,
`mutation`.

---

## 10. Test count, engine count, invocation count

| | |
|---|---|
| tests collected (all roots) | ~15,000 (11,031 pre-existing + 3,995 newly wired) |
| tests in the last sharded run | 8,448 across 12 shards |
| executable objects enumerated | 24,515 |
| tracked non-test Python files | 1,335 |
| governance engines | 49 (39 `00-MASTER/*_engine.py` + 10 `engine/*/gate.py`) |
| verify.sh stages | 20 |
| UEC governed enforcement artifacts | 182 |
| invocation plane types | 6 (`make`, `verify`, `env`, `ci`, `python`, `test`) |

---

## 11. Remaining exclusions

Exactly one declared coverage exclusion: **`engine.uicm`** — 1,893 statements, ten modules, zero
test files, imported by nothing. Reasoned in `[tool.ucos.coverage_scope]`, and
`platform/tests/test_coverage_scope.py` refuses it in both directions (stale if it becomes
measured, stale if it disappears). The open question it records — retired and deletable, or live
and testable — is an owner decision.

**No exclusion was added during this work. One was removed** (`engine.recursive_knowledge`, which
was an *undeclared* omission rather than an exclusion).

---

## 12. What must happen for certification to be permitted

In dependency order, with the honest cost:

1. **Give coverage a single source root** so `coverage.xml` stops dropping 46% of its body.
   Everything downstream reads that artifact. Small change, needs care: `source` is the governed
   denominator.
2. **Make the 39 `00-MASTER` engines importable under test.** Closes
   `unmeasured_governance_engines` (39 → 0), most of `executable_outside_denominator` (65 → ~17),
   and is the prerequisite for their coverage to exist at all.
3. **Write direct, behaviour, failure-path and integration tests** for the 18 UEC-untested and 25
   UCI-untested engines. Rule 5 additionally requires mutation tests, which nothing here measures
   yet.
4. **Give the 6 uninvoked and 14 single-plane engines their planes** — a Makefile target plus a
   workflow each, registered in UEC's inventory.
5. **Dispose of the 3 inert declarations** — consume them or withdraw them with a reason.
6. **Add mutation coverage measurement.** Rule 5 and Rule 14 both require it; it does not exist.
7. **Run Rules 8/9/10 at full-suite scope.** The harness is built and parameterised; the cost is
   ~90 hours for N=100 seeds and needs sharding to be practical.
8. **Identify the A-4…A-13 register**, then close each with implementation, tests and evidence.
9. **Then** 1,762 classified executable uncovered lines owe tests (see `coverage_100_plan.md`).

---

## 13. Evidence index

| artifact | contents |
|---|---|
| `coverage_gap_inventory.json` | 1,335 files + 24,515 objects, per-file classification, execution paths, invocation sources, governing authority, exclusion reason. 12.7 MB, generated by `make uci-inventory`, gitignored as derived. Digest `b9a9f3221d1179c4`. |
| `missing_execution_surface_report.md` | Every counter with its full offender list, before and after. |
| `coverage_100_plan.md` | 1,777 classified uncovered lines; 742 undescribed files reported separately with coverage stated UNKNOWN. |
| `final_certification_report.md` | This document. |
| `.uci-evidence/subset-equivalence.json` | Rules 8/9/10/11 raw run records, digests and diffs. |
| `.uci-evidence/coverage.xml.truncated-by-concurrent-run` | The concurrent-write false green, preserved. |
| `00-MASTER/UCI-000001/uci-declaration.json` | The governed expectation: 7 laws, 6 two-sided ceilings, every rationale. |
| `engine/tests/unit/test_certification_integrity.py` | 62 tests; every law forged into failure in both directions. |

### Reproduce

```sh
make uci            # the measurement and the six laws
make uci-gate       # fail-closed
make uci-inventory  # writes coverage_gap_inventory.json
python -m pytest engine/tests/unit/test_certification_integrity.py --no-cov
```

---

## 14. Note on the measurement environment

For part of this session a second agent process ran `./verify.sh --full` in this same working
tree, advanced HEAD twice, and committed my uncommitted edits into its own commit `2ad1efcf`
while deleting untracked files I had created. The concurrently-written `coverage.xml` is false
green #4 above.

This is recorded because it bears directly on Rule 7. A measurement taken while another process
mutates the tree is attributable to no commit, and the frozen-extraction mechanism in §4 was
built partly in response to it. Every figure in this report was measured either from a sealed
extraction or from a tree whose HEAD and porcelain digest were sampled before and after.
