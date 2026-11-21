# UCOS Ω∞ — UNIVERSAL ASSUMPTION REGISTER

| Field | Value |
|---|---|
| ARTIFACT | `UCOS-OMEGA-INFINITY-UNIVERSAL-ASSUMPTION-REGISTER.md` |
| CLASSIFICATION | `EVIDENCE` — derived assumption inventory |
| AUTHORITY | **NONE — DERIVED TRUTH.** Legislates nothing, ratifies nothing, certifies nothing, assigns no ownership, allocates no identity, changes no certification state. **This register creates no second assumption authority** — `UISD-000001` owns closure disclosure and `engine/infinite_scope/` is the detector. Where this register and a located instrument differ, **the located instrument governs.** |
| DISPOSITION | **ASSIMILATION ONLY.** Locates and classifies existing disclosures. No artifact deleted, removed, renamed or merged. No code, configuration, registry or ledger modified. No identity minted. No ADR created. No new gap id allocated — every `*-G-*` id below is **quoted from its owner**, not coined here. |
| COMPANION TO | `…-ASSIMILATION-COVERAGE-DETERMINATION.md` · `…-ASSIMILATION-COVERAGE-MATRIX.md` |
| BASELINE | HEAD `bae59755` · branch `integration/recovery-001` |
| MODE | Read-only |

> **Governing doctrine, quoted from the detector itself** (`engine/infinite_scope/contract.py:16-20`): **closure is not a defect; *undisclosed* closure is.** `engine/uckp/facets.py` closes 33 facets on purpose. Accordingly this register separates **disclosed** assumptions (governed, with a closing invariant and an admission path) from **undisclosed or unenforced** ones (the actual findings). A count in this register is a currently discovered population, never a boundary.

---

## 1 — ASSUMPTION TAXONOMY

| Class | Meaning | Count |
|---|---|---|
| **A — Disclosed closed enumeration** | A closed set, declared with a closing invariant, an admission path, and intent | 11 (`ISD-CE-01…11`) |
| **B — Declared gap** | A named, owner-held gap in a declaration | 11 (`ISD-G-01…11`) |
| **C — Detection-scope assumption** | An assumption about what the detector itself can see | 7 (`AD-G-01…07`) |
| **D — Persistence assumption** | A capability correct in memory whose durability is unowned | 4 (`P4-F-002/006/008/009`) |
| **E — Population-identity assumption** | Two planes assumed to describe one population, with no join | 2 (`RU-G-01`, `PA-G-04`) |
| **F — Uncodified governance assumption** | A rule cited as binding with no executable enforcement | 6 |
| **G — Structural duplication assumption** | One invariant expressed twice, assumed to stay in agreement | 4 |
| **H — Measurement assumption of this pass** | An assumption this assimilation itself relies on | 7 |

**Total located: 52.** Of these, **11 are governed by design** (class A), **11 are owner-held and declared** (class B), and **30 are findings** (classes C–H).

---

## 2 — CLASS A: DISCLOSED CLOSED ENUMERATIONS

Source: `00-MASTER/UISD-000001/uisd-declaration.json` → `closed_enumeration_disclosures[]`. **This is the repository's machine-readable assumption registry.** `ISD-L-01` requires each entry to name a `closing_invariant`, an `admission` path, and intent-or-gap-id; a closure that is *silent* is the violation.

| ID | Closed set | Population | Intentional? | Note |
|---|---|---|---|---|
| `ISD-CE-01` | Facet (`engine/uckp/facets.py`) | 33 | **yes** | Amendment-bound. A new facet is a constitutional amendment; deliberately out of scope for `ISD-L-11` exercise, because "a law that demanded exercisability of `ISD-CE-01` would be false, and a false law gets disabled" |
| `ISD-CE-02` | CMG `closed_enumerations` | — | yes | |
| `ISD-CE-03` | `RelationType` | — | yes | The relationship *type space* stays open by pattern (`ISD-L-02`); this is the governed vocabulary |
| `ISD-CE-04` | `RelationshipKind` | — | yes | |
| `ISD-CE-05` | UGA `object_classes` | — | yes | |
| `ISD-CE-06` | UICM `closure_dimensions` | — | yes | |
| `ISD-CE-07` | `RegistryKind` | — | yes | |
| `ISD-CE-08` | `ClosureState` | — | yes | |
| `ISD-CE-09` | **`KnowledgeCapability`** (`ukip/constitution.py`) | **11** | **NO** | `closing_invariant: "NONE DECLARED IN CODE"` → **gap `ISD-G-01`**. The one live undisclosed-intent closure |
| `ISD-CE-10` | UGA evidence classes | — | yes | |
| `ISD-CE-11` | **`ADMISSION_FORMS`** (`infinite_scope/contract.py`) | **2** | yes | The detector discloses its **own** closure — the openness prover is itself a closed set of 2 admission forms |

**10 intentional · 1 unintentional.** Additional closed enumerations located outside this register (each a class-A-shaped assumption, only some disclosed): `MeasurementKind` 4 · `MaturityAxis` 14 · `TruthClass` 9 · `SelectorKind` 7 · `Stage` 9 · `LifecycleStatus` 16 · `FROZEN_PREFIXES` 3 · `WRITE_PERMISSIONS` 3 · `_BUILTIN_GUARDS` 4 · `freeze_scan` classes 5 · maturity lattice 8 · expansion axes 10 (enforced as a contract) · `PROVIDER_FACETS` 11.

**A note that matters for reading this class.** The kernel itself is provably free of closed enumerations: `engine/kernel/compliance.py:91` `_kernel_has_no_closed_enum()` proves **no source in `engine/kernel/` defines any `enum.Enum` at all** — "the absence of *any* Enum subclass in the kernel package is a strong, mechanised proof" — and it takes `directory` as a parameter *only so the proof is itself testable against a control sample*. Every closure above therefore sits **outside** the meta-kernel by construction.

---

## 3 — CLASS B: DECLARED GAPS (`ISD-G-01…11`)

Owner-held, quoted. Not coined here.

| ID | Assumption | Status |
|---|---|---|
| `ISD-G-01` | `KnowledgeCapability` is closed with **no closing invariant declared in code** and `intentional: false` | **live** |
| `ISD-G-04` | The relationship model has **no gate** — "enforcement machinery over a 12,899-edge surface owned by UKB… NOT closed by this cycle" | **live, scoped out by its owner** |
| `ISD-G-05` | A Class-C permanence site awaits an `ARTIFACT-RENAME-DETERMINATION.md` **that does not exist** | **live** |
| `ISD-G-06` | `FROZEN` status values sit on derived generated surfaces inside guarded prefixes **and under `00-MASTER`, which is excluded from the scan roots** | **live** |
| `ISD-G-07` | `KNOWN_PERSISTENCE_KINDS` is "a closed module tuple whose own comment claims 'Open by registration (Article 17)' while **no registry holds it**" | **live — a claim exceeding its mechanism** |
| `ISD-G-08` | `KNOWN_EXECUTION_KINDS` closed "on the same terms as `ISD-G-07`, and would be resolved by the same single technology-kind vocabulary registration" | **live** |
| `ISD-G-09` | `engine/tests/unit/test_infinite_scope.py` asserts `len(unintentional) == 1` over the live declaration, so **disclosing a newly located undisclosed closure requires an engine-plane edit** | **live — a meta-assumption about disclosure cost** |
| `ISD-G-02/03/10/11` | Declared in `uisd-declaration.json`; not individually read in this pass | **NOT YET ASSESSED** |

`ISD-G-07` deserves emphasis: it is the register's own example of the failure mode this whole document exists to surface — **a comment asserting openness over a mechanism that does not provide it.** The detector caught it in its own dependency.

---

## 4 — CLASS C: DETECTION-SCOPE ASSUMPTIONS (`AD-G-01…07`)

Source: `ARCHITECTURAL-ASSUMPTION-DETECTION-DESIGN-ANALYSIS.md`. These are assumptions about **what the assumption detector can see** — the highest-leverage class, because they bound every other class.

| ID | Assumption | Consequence |
|---|---|---|
| **`AD-G-01`** | **Detection is declaration-bound, not discovery-bound.** `ISD-L-01`/`ISD-L-10` audit only the 11 already-disclosed closures. Nothing sweeps the repository for an *undeclared* `Enum`, `frozenset` or literal tuple | **A closed enumeration added tomorrow is invisible until a human discloses it.** The largest single assumption in the system |
| `AD-G-02` | `ISD-L-09` is a **manifest** check only — it reads `pyproject.toml`, never an import statement. The repo-wide stdlib-only audit was done by hand with grep and **no gate re-runs it** | Import-level technology coupling is unmonitored |
| `AD-G-03` | **4 of 7 technology categories have no executable check** — INFRASTRUCTURE, COMMUNICATION, EXPERIENCE, TOOLS (**confirmed** in this pass) | Two have surface and no check; two have no surface, and building one "would be manufacturing evidence, not discovering it" |
| `AD-G-04` | "Example becoming law" and "current implementation becoming constitutional dependency" have **no detector and are not declared axes** | The two most insidious drift modes are unmonitored |
| `AD-G-05` | = `ISD-G-01` (`KnowledgeCapability`) | live |
| `AD-G-06` | `baseline_surfaces_qualified: 1` of 4 — three baseline surfaces cannot parse a temporal coordinate | Temporal qualification of baselines is 25% |
| `AD-G-07` | `check_no_enumeration` is **replicated across ~20 engines with non-identical bodies** | Graded APPARENT by its own source; ~20 bodies were not diffed in this pass |

**Sequencing constraint recorded by the source, and it is a genuine engineering insight:** the undeclared-closure discovery law must land in **observe-and-disclose mode first**, because introducing it as blocking "would fail the gate on legitimately-closed enumerations that have simply never been disclosed — converting a true finding into a false law, which the codebase's own doctrine says *gets disabled*."

Also from the same source, and load-bearing: `04-HIDDEN-FINITE-ASSUMPTION-CERTIFICATION.md` performs a **23-axis** finite-assumption scan with every verdict `NONE`, but it is headed "Design Only · Read-Only" and **no gate re-runs it**. Its own §4 admits no exhaustive line-by-line proof of absence was performed and confines residual risk to the realization layers.

---

## 5 — CLASS D: PERSISTENCE ASSUMPTIONS (`P4-F-*`)

Source: `engine/lineage/memory-layers.json` → `$disclosures`. Each is a capability **correct in memory whose durability no owner holds**.

| ID | Assumption |
|---|---|
| `P4-F-002` | No relationship representation in the memory plane carries temporal validity, a version, or a supersession pointer. Relationship memory resolves the *current* edge set, not a history of edge states |
| `P4-F-006` | UKIP provenance chains are hash-chained and correct **in memory but not persisted**. Evidence memory resolves only the evidence a CKO records, not the full chain |
| `P4-F-008` | Learning is **deliberately not a layer** — "a separate layer would imply a learning store that no owner holds." **Governed by design, not a defect**; reconciled with `adr/0011` (Accepted), which likewise refuses a second evolution engine |
| `P4-F-009` | `UCXI-000001` owns the context *kind* vocabulary but persists **no per-subject context binding**; CEU's `bind_context` is a runtime journal action with no corpus record. Echoed verbatim by `ukip/confidence.py`: "**no owner persists it to disk today**" |

**Two further persistence assumptions located in this pass, not in that `$disclosures` block:**

| # | Assumption |
|---|---|
| D-5 | `engine/runtime/execution/persistence.py` **serialises to a string only — no file write, no path, no store.** Runtime `Checkpoint`/`Snapshot` and the `AuditLog` have no durable sink, so cross-process replay of a real run has no on-disk input |
| D-6 | `make rpi` writes to `.runtime/repository-intelligence/`, which `.gitignore:12` excludes. Self-disclosed in the Makefile as an **HONEST LIMIT**: "re-running refreshes them locally but commits nothing a clone can reproduce. Staleness returns the moment this is not run." Closing it requires `W0-1`, a constitutional determination on `.gitignore` against the twelve Truth zones |

---

## 6 — CLASS E: POPULATION-IDENTITY ASSUMPTIONS

The assumption that two registers describe the same population, when nothing declares that they do. **Both are CONFIRMED and both are deliberately reserved to a governing authority under `CEP-002` 14.2 — they are not open work items.**

| ID | Assumption | Measured divergence |
|---|---|---|
| `RU-G-01` | 49 hand-maintained `REQ-NN` rows and 549 engine-generated `RR-<concept_id>` records are assumed to be the same population | "**Nothing in the repository states whether these are the same population**"… "the repository cannot currently tell whether UFC-16 is satisfied or breached." The reconciliation determination holds they are "not duplicates — different object classes measuring different subjects" that "should coexist… **joined by a declared relation rather than merged**" — and **that relation is not declared** |
| `PA-G-04` | 22 principles in `uccep-bindings.json` and 5 principle objects on the CKO plane are assumed to be the same population | 22 vs 5 |

A third, adjacent: `100-PERCENT-CLAIM-VALIDATION-DETERMINATION.md` adjudicates a claim of 59 requirements / 76 items down to **54** — a worked instance of the interpretation principle applied against the repository's own prior count, and a third number in the same neighbourhood as 49 and 549.

---

## 7 — CLASS F: UNCODIFIED GOVERNANCE ASSUMPTIONS

A rule cited as binding, with no executable enforcement. **These are the assumptions most likely to be mistaken for guarantees.**

| # | Assumption | Evidence |
|---|---|---|
| **F-1** | **`UFC-16` is enforced.** It is the rule most frequently cited to refuse a new register — "One subject population SHALL yield one measurement… SHALL be converged, never reconciled by note." **But `UCOS-UFC-001` does not exist as a directory in this tree**; the only full text is a blockquote inside `00-MASTER/UCOS-URR-001/00-URR-DISPOSITION-DETERMINATION.md:55-58`; **zero `.py` files mention UFC-16.** Cited by 9 markdown files and 1 JSON | verified by `find -type d -name "*UFC*"` → nothing, and grep |
| **F-2** | **`UAP-001` certifies agnosticism.** Its own status is "**DESIGN PRINCIPLE — not a certification**", and it self-discloses: "**no gate, invariant, or certification currently checks conformance to this statement, and none is created by this document**" | `adr/0021` |
| **F-3** | **`GOVERNED CLOSURE` / `OPEN GAP` are enforced statuses.** Both have **zero Python representation** (0 hits in `*.py`). Nothing mechanically prevents a document writing `CERTIFIED` where `GOVERNED CLOSURE` is correct; the only named check is `REQ-43`'s manual "matrix diff" | grep census |
| **F-4** | **`ISD-BND-01…07` refuse things.** Seven of eight declared governance boundaries carry **no computed refusal** — a violation is caught only if the named owner's own gate catches it. Only `ISD-BND-08` (the gate's own mutation boundary) is computed | `uisd-declaration.json` + `uisd-gate.yml` |
| **F-5** | **Gate mode is declared.** **No `gate_mode` field exists anywhere in code or JSON.** PRODUCER-vs-OBSERVE is per-gate prose, and `check_declaration` does not validate it. **This is why the live purity violation of §9 H-3 was possible** | grep across `engine/ platform/ 00-MASTER/ .github/` |
| **F-6** | **`adr/0008` is a ratified decision.** Its status is **Proposed**, though its 12-test suite is implemented and passing | `adr/0008` header |

---

## 8 — CLASS G: STRUCTURAL DUPLICATION ASSUMPTIONS

One invariant expressed twice, assumed to stay in agreement, with nothing enforcing the agreement.

| # | Assumption | Sites |
|---|---|---|
| G-1 | The frozen-prefix set is one invariant | `frozen_paths.py:33` `FROZEN_PREFIXES` and `identity/policy.py:50` `FROZEN_CORPUS_PREFIXES` — **two independent literals, no shared constant, free to drift** |
| G-2 | "This path is generated" has one expression | `00-BOOK/DATA/generated-artifact-registry.json` **and** `00-BOOK/tools/config.py::EXCLUDE_DIR_PREFIXES` — the very three-way drift the register's own `why_this_exists` says it was created to collapse |
| G-3 | Entity kind has one vocabulary | `birth-scope-policy.json` kinds (10, catch-all-terminated) **and** `engine/uaue/model.py:255` `ObjectKind` |
| G-4 | Maturity has one model | 8-level ordered lattice (`requirement_engine.py:103-115`) **and** 14-axis vector (`universal_foundation/constitution.py:126-142`). `IMPLEMENTED`, `VALIDATED`, `CERTIFIED` appear in **both with different arity**, and nothing maps them |

**Adjacent, and a live finding rather than a pure duplication:** `mutation-governance-boundary.json` declares 9 rules (`R-01…R-09`) while `RULE_PREDICATES` implements 8 (`R-01…R-08`). Verified live in this pass:

```
validate_rule_coverage(...) → ("rule 'R-09' is declared but no predicate implements it",)
```

`mutation_class_extension.py` builds the `GOVERNED_ANALYSIS` class and `R-09` rule dicts and an `extend_*` function appending them to the **document**, but registers **no predicate**. Because coverage validation is two-sided and fail-closed ("dead code wearing the appearance of enforcement"), this is a genuine finding. Related: **no CI step runs `classify_all` over a commit's changed paths and fails on `UNRESOLVED`** — the classifier is available to consumers rather than universally applied.

---

## 9 — CLASS H: MEASUREMENT ASSUMPTIONS OF THIS ASSIMILATION

Disclosed because a register that audits others while exempting itself is the failure mode it is auditing for.

| # | Assumption | Disclosure |
|---|---|---|
| **H-1** | **`gaps=0` means closure.** It does not, unconditionally: `UAKOS-CLOSURE-002`'s `conversation_only` class is measurable only from an external corpus at `REPO.parent/"UCOS"`, and absent it "measures 0 by **ABSENCE** rather than by closure" (`closure_engine.py:19-33`; historical residue 91). Reported as qualified throughout |
| **H-2** | **Two closure numbers are comparable.** `UAKOS-CLOSURE-002` (549/549 homed) and `UAKOS-CLOSURE-009` (25.5% assimilated) measure **different subjects** — homing vs dimensional population. Anyone citing the first as evidence of overall completeness misreads its scope |
| **H-3** | **A `--gate` flag observes.** **Falsified live in this assimilation.** `requirement_engine.py --gate` wrote 11 registers plus `requirements.json`, regenerating against live HEAD instead of the recorded baseline. Restored via `git checkout --` on exactly those paths; tree count returned to 59. **The measurement is retained (§ live register); the mutation was reverted.** Root cause is F-5: no declared `gate_mode` |
| **H-4** | **A subagent's "NOT FOUND" means absent.** **Falsified twice.** Four lifecycle determinations and three `realization/` capability files were reported absent and **all seven exist** — verified by direct `test -f`. Corrected in Part XII §12.15 |
| **H-5** | **Reading a `$disclosures` block verifies the disclosed condition.** It does not. Class D is quoted from its owner; the absence of persistence at each named owner was **not independently re-measured** in this pass |
| **H-6** | **A named gate file enforces what its name suggests.** Only 5 gates were executed live. For the remainder, enforcement is read from workflow text and engine docstrings, not observed |
| **H-7** | **`AD-G-07` is confirmed.** It is **APPARENT** by its own source's grading; the ~20 replicated `check_no_enumeration` bodies were **not diffed** here |

**Two coverage limits of this pass, stated plainly.** (1) `engine/infinite_scope/contract.py` (818 lines) was read to ~line 644 in one investigation; law checks beyond that are cited by symbol, not by verified line. (2) Nine boundary-determination markdown documents, `00-BOOK/tools/config.py` (1540 lines), and roughly a dozen evidence reports named as leads were **not read** — their self-declared authority is unassessed.

---

## 10 — REGISTER SUMMARY

| Class | Count | Standing |
|---|---|---|
| A — Disclosed closed enumerations | 11 | **10 governed by design · 1 undisclosed intent** (`ISD-CE-09`) |
| B — Declared gaps | 11 | 7 read and live · 4 `NOT YET ASSESSED` |
| C — Detection-scope | 7 | all live; **`AD-G-01` is the dominant one** |
| D — Persistence | 4 + 2 | 1 governed by design (`P4-F-008`) · 5 live |
| E — Population identity | 2 | both CONFIRMED, both **reserved to authority** — not open work |
| F — Uncodified governance | 6 | all live; **F-1 and F-5 are the most consequential** |
| G — Structural duplication | 4 + 1 live finding | all live |
| H — This pass's own | 7 | 2 **falsified during the pass** and corrected |

### The three assumptions that bound everything else

1. **`AD-G-01` — detection is declaration-bound.** Every class-A entry is trustworthy *because someone disclosed it*. Nothing sweeps for undisclosed closures. The system's openness guarantee is therefore **as good as its disclosure discipline**, not better.
2. **`F-1` — `UFC-16` has no source instrument in this tree and no code enforcement**, while being the rule most often invoked to refuse a new register. Two confirmed breaches sit open beneath it.
3. **`F-5` — no `gate_mode` field exists.** The distinction between a gate that observes and an engine that produces is prose. This pass falsified it empirically (H-3).

### What this register deliberately does not do

It allocates no new gap id, creates no second assumption authority, proposes no remediation, and sequences nothing. Every id is quoted from its owner. The detector remains `engine/infinite_scope/`; the disclosure home remains `uisd-declaration.json`. Building a second detector is a gate violation under `--check-no-parallel-authority`, and the located design analysis refused exactly that: **"Do not build a second detector."**

---

*END · `UCOS-OMEGA-INFINITY-UNIVERSAL-ASSUMPTION-REGISTER.md` · AUTHORITY = NONE (DERIVED TRUTH) · Where this register and a located instrument differ, the located instrument governs.*
