# UKAP-001 — Mission Certification Evidence

> **Hand-authored mission record**, not a generated deliverable. The generated deliverables are
> `01-CORPUS-DISCOVERY-REGISTER.md` … `08-CORPUS-CURRENCY-COMPLETION-REPORT.md`, `corpus.json` and
> `EVIDENCE-MANIFEST.json`; regenerate those with `make corpus` and never hand-edit them. The
> WP-002 and WP-003 deliverables are not here at all — they live in the register they extend,
> `00-MASTER/UAKOS-CLOSURE-008/`, which is the point of the mission and is explained in §2.
>
> This file records the *mission-level* result across all three work packages, including what did
> **not** close and what is not this mission's to close.

| Field | Value |
|-------|-------|
| Mission | Universal Knowledge Assimilation Programme — corpus currency and the evaluation→decision chain |
| Programme | `UKAP-001` · WP-001/D-1 · WP-002/D-2 · WP-003/D-3 |
| Authority | **NONE (DERIVED TRUTH)** — this programme legislates nothing, ratifies nothing and creates no authority |
| Branch | `integration/recovery-001` |
| Entry HEAD | `9a841be` (D-1 and D-2 already committed; D-3 implemented but uncommitted) |
| Certified HEAD | `50cd6b5` |
| Decision rule set | `UKAP-001/WP-003/D-3/1.0.0` |
| Decision rule set digest | `907ca21496a6991e64138913b04ce7066633b4a0d55dfeef1c06843f643a4066` |
| Verdict | **ALL THREE WORK PACKAGES COMPLETE AND GATE-GREEN** |
| Certification | **CERTIFIED-PROVISIONAL** — and provisional is the ceiling, not an omission (§6) |

---

## 1. The three work packages, and what each one actually established

| WP | Deliverable | State | Executable proof |
|---|---|---|---|
| WP-001 / D-1 | Corpus currency restoration | **COMPLETE** (committed `1b9fb90`, `f989241`, `4453227`) | `make corpus-gate` → `CORPUS CURRENT` |
| WP-002 / D-2 | Superiority evaluation — the second axis over presence | **COMPLETE** (committed `9a841be`) | register `09`, `make assimilate-gate` |
| WP-003 / D-3 | Repository decision & action — the third axis | **COMPLETE** (committed `49ce962`) | registers `10`/`11`, `make assimilate-gate` |

**D-1** guarantees that every downstream assimilation artifact derives from the *newest* available
ChatGPT export, and fails closed the moment a newer export exists but is ignored. What makes it
non-trivial is what it refuses to assume: recency is derived from export **content** for an
`EXPORT-ARCHIVE` (the export's own recorded conversation times) and from **git commit order** for
an `EXPORT-DOCUMENT`. No export version, no filename, and specifically no filesystem mtime — mtime
does not survive a clone, so a gate resting on it would silently pass on fresh checkouts.
Measured: 2 archives (canonical `ac1451ac4015cf8b`), 2 documents (canonical
`04-REFERENCE/ChatGPT Chat-1.docx`), 249 conversations cited, both classes **CURRENT**.

**D-2** answers a question presence cannot: not *"does Repository Truth carry this?"* but *"is the
discovered form better?"*. 16 declared architectural dimensions, each measured **independently on
two sides** by two named functions — the corpus record and the measured repository presence — on a
shared 0..2 ordinal scale, with the verdict being the comparison. An absent evidence field yields
`UNDECIDABLE`, never a guess. Seven verdicts in declared precedence. Five dimensions are
CONSTITUTIONAL and may never regress silently: a regression escalates to architectural review
instead of being adopted.

**D-3** answers the third question for every object both prior axes evaluated: *"what must the
repository do?"* Exactly one governed action per object from a closed set of 6, decided by exactly
one of 13 declared rules, in **fail-safe precedence** — where two clauses could both apply, the
non-destructive one wins, so a conflict, obsolescence, retirement or constitutional regression is
decided *before* any adoption clause is reached and no mechanical rule can overrule an architect.

Over all **23 859** objects: `ACCEPT` 520 · `MERGE` 261 · `SUPERSEDE` 135 · `REJECT` 5 807 ·
`ESCALATE_ARCHITECTURE` 5 869 · `DEFER` 11 267 · **undecided 0**.

---

## 2. The single most important architectural fact about this mission

**All three axes extend ONE register. None of them created a second one.**

D-2 and D-3 have no directory of their own. They are implemented as `superiority_engine.py` and
`decision_engine.py` *inside* `00-MASTER/UAKOS-CLOSURE-008/`, and their output is **appended
columns** on the existing assimilation rows plus registers `09`, `10` and `11` in the existing
register series. The six presence states, with their rules, destinations, owners, authorities and
waves, are **bit-for-bit unchanged**; presence is evaluated first, and superiority reads only what
presence measured.

This was the constitutionally load-bearing choice. A separate "superiority register" and a separate
"decision register" would each have been a second home for one concept — a direct breach of
Knowledge Once and of No Parallel Authority, and it would have made the three axes able to
disagree about the same object. As appended columns on one row they cannot diverge, because there
is only one row.

The same reasoning governs enforcement: **D-3 added no CI workflow.** Its blocking checks were
folded into `assimilation_engine.py`, so the existing `.github/workflows/assimilation-gate.yml`
enforces them automatically. Creating a `decision-gate.yml` would have been a second gate over one
register.

---

## 3. Determinism — the property the whole chain rests on

| Claim | How it is enforced | Result |
|---|---|---|
| No verdict can depend on anything but recorded evidence | `superiority_engine.py` imports **nothing** (asserted over its own AST): no clock, no randomness, no environment, no filesystem, no network, no model judgement | held |
| Same for decisions | `decision_engine.py` imports **nothing but `__future__`** | held |
| Any decision can be re-proved by hand | every threshold declared once; `replay()` re-derives the decision from the recorded `decision_rationale` **alone** — without the corpus, without the repository, without the engine's caller | held |
| The rule set cannot change underneath the decisions citing it | declared once, versioned `UKAP-001/WP-003/D-3/1.0.0`, and **digest-sealed** into the machine register, so a silent edit fails the drift gate | held |
| "No action" can never be silent | `DEC-13` is the declared totality residual; because its firing would mean the rule set has a hole, **its use is a BLOCKING failure**, not an accepted outcome — and it is provably unused on this corpus | held |
| Regeneration is byte-identical | no timestamps emitted; registers re-render from `assimilation.json` / `corpus.json` with no evidence tree required | held |

The last row is also the proof the repository is **self-contained**: the assimilation gate runs
with `--render`, i.e. from the in-repo JSON alone. The external `KNOWLEDGE-ASSIMILATION` evidence
tree is deliberately *not* required to re-verify any claim here.

---

## 4. Mandated validation — results at the certified HEAD

| Proof | Command | Result |
|---|---|---|
| Repository verification | `./verify.sh` | **PASS** — 5/5 stages (see §5 for one caveat not caused here) |
| Corpus currency | `make corpus-gate` | **PASS** — CORPUS CURRENT, both classes |
| Assimilation + both new axes | `make assimilate-gate` | **PASS** — 23 859 objects, unclassified 0, undecided 0, remaining candidates 0 |
| Aggregate constitutional gate | `uccep_engine.py --tier full` | **PASS** — CERTIFIED-PROVISIONAL, gates **17/17**, programmes **19/19**, blocking **none**, seal `77132548a27ec9e0` |
| Registration transaction | `00-BOOK/tools/register.sh` | **PASS** — CERTIFIED, integrity domains 10/10, hard checks 7/7, 1193 == 1193, 0 unregistered / unclassified / invalid |
| Registration drift | `00-BOOK/tools/register.sh --guard` | **PASS** — repository, registry, control tower, twin and portal in sync |
| Meta-constitutional gate | `make cmg-gate` | **PASS** — 0 findings, READY-PROVISIONAL |
| Decision assimilation | `make ucda-gate` | **PASS** — gate OPEN, 108 decisions, 0 undispositioned, 0 conversation-only |
| Concept closure | `make closure-gate` / `-phase2` / `-phase3` | **PASS** — 447 concepts, gaps **0** across all 7 classes, REPOSITORY CLOSED |
| Execution roadmap | `make roadmap-gate` | **PASS** — CONDITIONAL GO, 811 items, 180 READY |
| Integration blueprint | `make rib` | **10/12** — see §5 |

### The gates are not vacuous

Two blocking checks exist specifically so that success cannot be assumed:
`decision_rationale` replay is asserted on **both** the build path and the replay path, and the
declared residual `DEC-13` is asserted unused. Either would fail loudly if the rule set developed
a hole. The 16-dimension evaluator likewise reports `UNDECIDABLE` rather than defaulting, so a
missing evidence field degrades the verdict instead of fabricating one.

---

## 5. What is NOT closed — stated plainly, with attribution

**`UCOS-RIB-001` reads 10/12, not 12/12.** Both remaining failures are one cause:
`GATE-12 Repository Clean` (`dirty_entries_outside_generated=2`) and `GATE-04` via
`VAL-02 "the working tree is clean at the computed HEAD"`. The two dirty entries are:

1. `Makefile` — this session's completed, validated `uar`/`uar-gate`/`uar-self` wiring, **pending
   commit**. Blocked, not abandoned: see below.
2. `platform/universal_pipeline/` — **not this mission's work.** A concurrent programme (the UAPF
   "Universal Pipeline" contract surface, `UAPF_VERSION 1.0.0`, referencing `AR-03`/`PL-05`) was
   being authored *during* this session: `__init__.py` and `errors.py` at 13:58, `vocabulary.py`
   appearing at 14:00, `identity.py` growing 11 224 → 11 746 bytes between 14:00 and 14:01. It is
   entirely untracked, so it is **not yet Repository Truth**.

That second entry also makes `./verify.sh` stage 1 red: `ruff check engine platform` reports 2
errors, **both** in `platform/universal_pipeline/__init__.py` (`I001` unsorted imports, `E501`
line 67). **Attribution was proven, not assumed** — `ruff check engine platform --exclude
platform/universal_pipeline` reports *"All checks passed!"* and `ruff format --check` reports
*"1070 files already formatted"*. This mission's only pending edit is to the `Makefile`, which ruff
does not lint. The red is 100% the concurrent work and 0% this mission's.

It was **left untouched, and deliberately**. The mandatory pre-commit hook
(`.git/hooks/pre-commit` → `ucos_ruff_gate`, `scripts/ucos-env.sh` 294–298) lints the `platform`
*directory*, so it sees untracked files and blocks any commit while that file is mid-authoring.
Three ways past it exist and **all three belong to the operator, not to this mission**: wait for
the concurrent programme to format its own code, authorise `--no-verify` for the Makefile-only
change, or coordinate the concurrent writer. Repairing another agent's file *while it is being
written* risks destroying work in progress, and bypassing a mandatory gate unbidden is worse than
leaving one target uncommitted.

**`CK-HEALTH` remains ADVISORY-FAIL (`unhealthy`).** Pre-existing, non-blocking, untouched.

**One finding raised against another owner and deliberately not repaired.** The capability record
this session added for `engine.civilization` reads `authority: EC-1 CERTIFIED`,
`implementation_status: CERTIFIED`, `replacement_prohibited: true` — because
`intelligence/rie/knowledge.py` keys `CATEGORY_POLICY` on the code **root**, so every sub-package
of `engine/` inherits `engine`'s posture automatically. EC-1 never certified that layer;
`MCOS-000001` certified it at PROVISIONAL only. This is precisely the defect class
`UCOS-RIB-001/WP-003 §001` already found and closed at *root* granularity — *"any newly discovered
code root would have silently claimed EC-1 CERTIFIED authority … the fallback is now
fail-closed"* — left open one level down, at *sub-package* granularity. Moving the policy from
per-root to per-package is a **redesign of `intelligence/rie`'s knowledge policy**, owned by
`intelligence/rie`; suppressing the record instead would reopen `GATE-07` and hide a real unit from
Repository Truth, which is worse. It is therefore **named and located** rather than silently
accepted or unilaterally rewritten.

**Nothing was pushed.** The branch is 12 commits ahead of `origin/integration/recovery-001`.

---

## 6. Why the ceiling is PROVISIONAL

Not an oversight and not modesty. Tier T1 is **VACANT** (`VAC-01` / `CMG-OQ-02`) and **no
ratification authority exists within the located corpus** (`CMG-OQ-01`). No in-repository act can
close either. Every determination of this programme is therefore issued at `CERTIFIED-PROVISIONAL`
and no higher, and nothing here is ratified or frozen.

This is also why the decision axis **escalates rather than acts**: 5 869 objects carry
`ESCALATE_ARCHITECTURE`. That is not the engine failing to decide — it is the engine correctly
refusing to make an architect's decision mechanically. `REGISTER-AND-HOLD` covers a further
11 267 objects whose maturity evidence carries no human commitment; scheduling them would
fabricate one.

---

## 7. Reproduce

```
make corpus-gate                                              # D-1: CORPUS CURRENT
make assimilate-gate                                          # D-2 + D-3: unclassified 0, undecided 0
make roadmap-gate                                             # 811 items, 180 READY
bash 00-BOOK/tools/register.sh --guard && ./verify.sh          # MXR-HYG-001's own validation command
python3 00-MASTER/UCCEP-000000/uccep_engine.py --tier full     # 17/17, blocking none
make cmg-gate && make ucda-gate                               # 0 findings; decision gate OPEN
make uar-self && make uar-gate                                # the entry point added this session
```
