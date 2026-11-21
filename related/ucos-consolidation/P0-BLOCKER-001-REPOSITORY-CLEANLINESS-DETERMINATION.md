# P0-BLOCKER-001 — REPOSITORY CLEANLINESS DETERMINATION

| Field | Value |
|-------|-------|
| ARTIFACT | P0 Blocker 001 — Repository Cleanliness Determination (Step 1) |
| **AUTHORITY** | **NONE — DERIVED TRUTH.** This document CLASSIFIES. It deletes nothing, commits nothing, moves nothing, and stages nothing. |
| **STATUS** | **BLOCKING · OPEN · NOT RESOLVABLE BY THIS PROGRAM** |
| BASELINE | HEAD `bae59755` · branch `integration/recovery-001` · snapshot `2026-08-25T05:10:09Z` |
| DEPENDS ON | `P0-BASELINE-REPOSITORY-STATE.md` (Step 0) |
| POPULATION | 390 pre-program uncommitted paths (38 modified + 352 untracked) + 3 stash entries |
| MODE | READ-ONLY · EVIDENCE-ONLY · FAIL-CLOSED |

---

## §1 — CLEANLINESS DETERMINATION

```
$ git status --porcelain | head -1
 M .gitignore
```

**`git status` is NOT clean.**

| Population | Count |
|---|---:|
| Staged | 0 |
| Modified tracked | 38 |
| Untracked (pre-program baseline) | 352 |
| Deleted | 0 |
| Renamed | 0 |
| **Total uncommitted paths** | **390** |
| Stash entries | 3 |

Under **PRIMARY RULE 8 — Git cleanliness is mandatory**, this is a **BLOCKING CONDITION**.

---

## §2 — METHOD

The 390 paths were not classified by appearance. They were resolved into **coherent work
units** by measuring what each change is, because a classification that splits one atomic act
across five buckets is not a classification — it is a way to lose the act.

Six units were measured. Every one of the 390 paths belongs to exactly one, and the six are
disjoint.

| Unit | Name | Paths | Classification |
|---|---|---:|---|
| **U-1** | UEG-000001 executable change-set (MIP Part 52) | 19 | **COMMIT-CANDIDATE** (verification-gated) |
| **U-2** | UVI verification-intelligence corrections (UVI-L-08 / UVI-L-10) | 6 | **COMMIT-CANDIDATE** (verification-gated) |
| **U-3** | Residual formatter reflow | 1 | **COMMIT-CANDIDATE** |
| **U-4** | 00-BOOK regeneration carrying a 228-identity mint | 250 | **REQUIRES-HUMAN-DECISION** |
| **U-5** | UEG-000001 documentary record (self-claimed, unregistered IDs) | 3 | **REQUIRES-HUMAN-DECISION** |
| **U-6** | Unregistered repository-root determination corpus | 111 | **REQUIRES-HUMAN-DECISION** |
| | **TOTAL** | **390** | |

Arithmetic: 19 + 6 + 1 + 250 + 3 + 111 = **390**.

**ARCHIVE-CANDIDATE: 0. DELETE-CANDIDATE: 0. IGNORE-CANDIDATE: 0.** — each tested and rejected
against evidence in §8.

---

## §3 — UNIT U-1 · UEG-000001 EXECUTABLE CHANGE-SET — **COMMIT-CANDIDATE**

**19 paths — 10 modified, 9 untracked.**

### §3.1 — Membership evidence

Three independent statements in the repository bind these files into one unit:

1. `00-MASTER/UEG-000001/ueg-declaration.json` declares the programme, names findings
   `F-1` and `F-2`, and names `UCOS-EXECUTION-ENVIRONMENT-ASSESSMENT.md` as its source.
2. `UCOS-MIP-000003-MASTER-IMPLEMENTATION-PLAN-V3.md` (+56 lines) admits **amendment A12 —
   Part 52 Universal Execution Governance**, attributed to `UEG-000001`.
3. `pyproject.toml` adds `engine.execution_environment` to the pytest coverage `addopts`
   **and** to `[tool.coverage.run] source` — the package enters the measured denominator,
   which is this repository's stated admission condition.

### §3.2 — Paths (complete)

| # | Path | State | Role |
|---|---|---|---|
| 1 | `00-MASTER/UEG-000001/ueg-declaration.json` | untracked | programme declaration (the authority) |
| 2 | `engine/execution_environment/__init__.py` | untracked | package |
| 3 | `engine/execution_environment/__main__.py` | untracked | CLI entry |
| 4 | `engine/execution_environment/model.py` | untracked | the entity |
| 5 | `engine/execution_environment/discovery.py` | untracked | the only module that touches the machine |
| 6 | `engine/execution_environment/contract.py` | untracked | the 8 declared checks |
| 7 | `engine/execution_environment/fingerprint.py` | untracked | cache |
| 8 | `engine/execution_environment/evidence.py` | untracked | execution-evidence emitter |
| 9 | `engine/execution_environment/gate.py` | untracked | fail-closed gate |
| 10 | `engine/tests/unit/test_execution_environment.py` | untracked | the suite that admits it |
| 11 | `UCOS-MIP-000003-MASTER-IMPLEMENTATION-PLAN-V3.md` | modified | admits Part 52 (A12) |
| 12 | `pyproject.toml` | modified | coverage denominator + source list |
| 13 | `.gitignore` | modified | ignores `.ucos/` |
| 14 | `verify.sh` | modified | Stage 0 wired to `ucos_env_gate`; install capability removed |
| 15 | `bootstrap.sh` | modified | creation/installation relocated here |
| 16 | `doctor.sh` | modified | diagnosis path |
| 17 | `Makefile` | modified | entry points |
| 18 | `scripts/ucos-env.sh` | modified | canonical series owner |
| 19 | `ENVIRONMENT-SETUP.md` | modified | operator documentation |

### §3.3 — Why COMMIT-CANDIDATE

- **Complete.** Declaration, implementation, tests, documentation, coverage registration and
  ignore rule all present. Nothing in the unit references a file that does not exist.
- **Self-describing.** Each changed file carries in-file rationale naming the finding it
  discharges.
- **Mints nothing.** No identity, no counter, no registry namespace. `ueg-declaration.json`
  states it "owns no version pin, no test, no stage and no lifecycle other than its own."
- **Disjoint.** Shares no path with U-2…U-6.

### §3.4 — The one open question inside U-1 (does not block classification)

`00-MASTER/UEG-000001/ueg-declaration.json` is a `.json` file, and `.json` **is** a registrable
type — the ledger holds **545** of them:

```
ledger path extensions: md=915, json=545, docx=28, txt=4
'00-MASTER/UEG-000001/ueg-declaration.json' in ledger: False
```

So committing U-1 introduces **one** unregistered object. This is a 1-object instance of the
§9 question, not a separate one; it is recorded so the commit is not made believing it is
registration-neutral.

### §3.5 — Verification gate (NOT executed)

```
$ ./verify.sh          # NOT RUN
```

Running it writes `.ucos/environment-fingerprint.json` and `.ucos/execution-evidence.json`,
and Step 0 forbids modification. **`.ucos/` already exists on disk with both files present**,
so a run occurred outside this program. The commit of U-1 must be gated on a fresh green run.
**This determination does not supply that evidence and does not claim it.**

---

## §4 — UNIT U-2 · UVI VERIFICATION-INTELLIGENCE CORRECTIONS — **COMMIT-CANDIDATE**

**6 paths — all modified, all tracked.**

| Path | Δ |
|---|---:|
| `engine/verification_intelligence/registry.py` | +73 |
| `engine/verification_intelligence/selection.py` | +32/− |
| `engine/verification_intelligence/model.py` | +11 |
| `engine/verification_impact/changes.py` | +64/− |
| `engine/tests/unit/test_verification_impact.py` | +155 |
| `engine/registry_coverage/declarations.json` | +1 |

### §4.1 — Membership evidence

`registry.py` adds `TestObjectRegistry.unregistered`, whose own docstring names the
measurement it exists for:

> "this is the population whose absence UVI-L-08 measured as 130 tests in no shard."

and `_collectible_on_disk`, whose docstring names **UVI-L-10** ("two plans over one state
[must] produce identical bytes"). `declarations.json` adds exactly one entry,
`knowledge/canonical-knowledge-history.json`.

### §4.2 — Why COMMIT-CANDIDATE

Source and tests ship together (+155 test lines against ~+180 implementation lines). Additive
over existing types; claims no namespace; mints nothing. **Same unexecuted verification gate
as §3.5 applies.**

---

## §5 — UNIT U-3 · RESIDUAL FORMATTER REFLOW — **COMMIT-CANDIDATE**

**1 path — modified.**

`platform/tests/test_mutation_classification.py` — 6 lines; one `assert not any(...)` reflowed
from parenthesized-message to trailing-message form. Semantically identical.

HEAD (`bae59755`) is titled *"POST-CERTIFICATION: Code formatting cleanup (Phase 1B and Phase 2)"*.
This is one hunk of that same cleanup left behind in the tree. **Lowest-risk path in the 390.**

---

## §6 — UNIT U-4 · 00-BOOK REGENERATION CARRYING A 228-IDENTITY MINT — **REQUIRES-HUMAN-DECISION**

**250 paths — 22 modified, 228 untracked.**

### §6.1 — What was measured

Comparing `HEAD:00-BOOK/DATA/id-ledger.json` against the working tree:

```
by_path:        HEAD=1264   WORK=1492   delta=+228
history:        HEAD=1264   WORK=1492   delta=+228
by_object:      HEAD=4914   WORK=4914   delta=0
by_observation: HEAD=7      WORK=7      delta=0
category_seq:   HEAD=117    WORK=200    delta=+83
page_cursor:    HEAD=9826   WORK=10840  delta=+1014
new paths: 228   removed paths: 0
```

All 228 new ledger entries carry the identical timestamp **`2026-08-23T13:32:44+00:00`** — a
single atomic generator run, dated **one day after** the HEAD commit (2026-08-22 18:29 +0530).

Correlation is exact and complete:

| Check | Result |
|---|---|
| New `by_path` entries | 228 |
| Distinct new `universal_id` values | 228 |
| Untracked `00-BOOK/PORTAL/*.md` pages | 228 |
| Portal basenames that ARE new universal IDs | **228 / 228** |
| Portal basenames that are NOT new IDs | **0** |
| New ledger paths that are **tracked** source documents | **228 / 228** |
| New ledger paths that are untracked | **0** |

The 22 modified files are the same run's other outputs: `00-BOOK/tools/ukb.py:829` names its
own output trees (`tools/, DATA/, REGISTRIES/, CONTROL-TOWER/, VOLUMES/, PORTAL/`), and five
carry an in-file `AUTO-GENERATED by 00-BOOK/tools/ukb.py` banner.

**This is one coherent, internally consistent generator run. It is not corrupt, and no claim
of corruption is made.**

### §6.2 — Why it is nevertheless BLOCKING: two standing statements in direct conflict

**(A) `00-MASTER/MCP-003-MASTER-EXECUTION.md`, row MEP-07 — reads as authorization:**

| # | Capability | Readiness | State | Acceptance | Exit criteria |
|---|---|---|---|---|---|
| MEP-07 | REG-AUTO-001 registration commit | READY | **AUTHORIZED (PENDING commit)** | Registries/portal/control-tower/data regeneration committed | **Clean working tree** |

**(B) `REG-AUTO-001-REGISTRATION-DETERMINATION-REPORT.md` — reads as prohibition, and still stands:**

| Field | Value |
|---|---|
| STATUS | **PREPARED · AWAITING GOVERNED DECISION. NO IDENTITY HAS BEEN MINTED.** |
| PREPARED BY | UEG-000001 closure cycle, under the Category B rule (irreversible ⇒ determination package only) |
| §9 | "**This determination is complete and awaits a governed decision by `REG-AUTO-001`.**" |

That report scopes **23 objects** (P-1: 10 + P-2: 2 + P-3: 12, less one counted twice) at
baseline HEAD `03179308` — a **verified ancestor**, seven commits back:

```
$ git merge-base --is-ancestor 03179308 HEAD && echo YES
YES
$ git log --oneline 03179308..HEAD | wc -l
7
```

**The mint that occurred covers 228 objects, not 23 — and it swallowed the report's own P-1 population:**

```
KNOWLEDGE-CONFIDENCE-COMPLETION-DETERMINATION-REPORT.md   in_HEAD_ledger=False  in_NEW_mint=True
P4-F-007-TEMPORAL-EVENT-OWNERSHIP-DETERMINATION.md        in_HEAD_ledger=False  in_NEW_mint=True
RELATIONSHIP-TEMPORAL-VALIDITY-DETERMINATION-REPORT.md    in_HEAD_ledger=False  in_NEW_mint=True
REQ-43-STORAGE-NEUTRALITY-DETERMINATION-REPORT.md         in_HEAD_ledger=False  in_NEW_mint=True
```

The act the report reserved for a governed decision **has been executed in the working tree,
at roughly ten times the scope the report defined, and the report has not been amended to
record it.**

### §6.3 — Why repository truth cannot resolve it

The repository's own registration doctrine, quoted from that report:

> "Minting one consumes a monotonic counter in `00-BOOK/DATA/id-ledger.json` and appends to an
> append-only history. **There is no unmint.**"

and its account of the precedent:

> "`verify.sh`'s own Stage 7 comment records what happened the one time a verification path was
> permitted to mint: ~140 permanent identities and ~140 portal pages emitted as a side effect
> of a run believed to be read-only."

The present situation is that precedent's exact shape, at 228. Repository truth establishes
**that** the mint happened, **when**, **what** it covered, and that it is internally
consistent. Repository truth does **not** establish **whether it was the governed decision
REG-AUTO-001 awaited, or a second unauthorized side-effect mint.** No file in the repository
records that decision.

Committing ratifies an act whose authorization is unproven. Discarding destroys 228
identities and 1,014 page allocations that the repository's own doctrine says cannot be
unmade. **Both are irreversible. Neither is available to this program.**

### §6.4 — The exact question for the human

> Was the generator run of **`2026-08-23T13:32:44+00:00`**, which minted **228 universal
> identities** and allocated pages **9827–10840**, the governed `REG-AUTO-001` decision that
> `REG-AUTO-001-REGISTRATION-DETERMINATION-REPORT.md §9` awaits — or an unauthorized
> side-effect mint of the kind `verify.sh` Stage 7 records?

| If | Then |
|---|---|
| **Authorized** | U-4 becomes COMMIT-CANDIDATE. `REG-AUTO-001-REGISTRATION-DETERMINATION-REPORT.md` must first be amended to record the executed decision, or it will sit in the corpus asserting "NO IDENTITY HAS BEEN MINTED" against a ledger holding 228. MEP-07 then closes on its stated exit criterion. |
| **Unauthorized** | A governed reversal determination is required. It is **not** a `git checkout`: "no unmint" applies to the act, not merely to the file. |

### §6.5 — Path list

The 22 modified paths are the `00-BOOK/` entries in `P0-BASELINE-REPOSITORY-STATE.md §3.1`.
The 228 untracked portal pages are the `00-BOOK/PORTAL/UCOS-*.md` entries in §4.2 of the same
document. Not reprinted here.

---

## §7 — UNIT U-5 · UEG-000001 DOCUMENTARY RECORD — **REQUIRES-HUMAN-DECISION**

**3 paths — all untracked repository-root `*.md`.**

| Path | Self-claimed ARTIFACT ID | In id-ledger? |
|---|---|---|
| `UCOS-EXECUTION-ENVIRONMENT-ASSESSMENT.md` | `UCOS-EEA-000001` | **NO** |
| `UCOS-EXECUTION-GOVERNANCE-CERTIFICATION.md` | `UCOS-EGC-000001` | **NO** |
| `REG-AUTO-001-REGISTRATION-DETERMINATION-REPORT.md` | `UCOS-RDR-000001` | **NO** |

Membership is stated in each header: the first two name
`00-MASTER/UEG-000001/ueg-declaration.json` as their governing declaration; the third names
"UEG-000001 closure cycle" as its preparer.

### §7.1 — Why separated from U-1

These three are the **documentary** half of the same programme, and they carry a defect the
executable half does not: **each asserts an ARTIFACT ID that the identity ledger does not
hold.** Measured:

```
UCOS-EEA-000001 in ledger: False
UCOS-EGC-000001 in ledger: False
UCOS-RDR-000001 in ledger: False
total registered ids: 1492
```

Committing them publishes three identity claims the registrar has not granted. That is a
registration act, not a code act, and it is governed by **§6.4**, not by §3.5's verification
gate. Splitting them out lets the executable half proceed on its own merits without carrying
an identity question it does not itself raise.

---

## §8 — UNIT U-6 · UNREGISTERED REPOSITORY-ROOT DETERMINATION CORPUS — **REQUIRES-HUMAN-DECISION**

**111 paths — all untracked repository-root `*.md`.**

(114 pre-program untracked root `*.md`, less the 3 assigned to U-5.)

### §8.1 — Measured status

```
untracked root *.md present in the WORKING id-ledger:  0
untracked root *.md minted in the 2026-08-23 run:      0
```

**Not one carries a universal identity.** The 228-identity mint registered *tracked* documents
exclusively. This corpus is invisible to the Universal Artifact Registry, the Knowledge Graph
Registry, and the Program Control Tower — all of which project from `00-BOOK/DATA/`.

### §8.2 — Why not COMMIT-CANDIDATE

These are substantive governance determinations — among them
`UCOS-OMEGA-INFINITY-100-PERCENT-CLOSURE-MASTER-REGISTER.md`,
`FINAL-IMPLEMENTATION-ADMISSION-PACKAGE.md` and `MASTER-EXECUTION-ADMISSION-MATRIX.md`.
Committing them registers 111 unidentified objects into a repository whose stated law is
*no anonymous objects, no post-creation registration* (`UOBC-000001`, cited in `pyproject.toml`).
Same class of act as U-4, at scope 111, foreclosed by the identical unresolved question.

### §8.3 — Why the three remaining buckets are empty (tested, not assumed)

| Bucket | Test | Result |
|---|---|---|
| **DELETE-CANDIDATE** | Is any path unreferenced build residue? | **NO.** These documents are cited by name from tracked, committed files — e.g. `UCOS-EXECUTION-ENVIRONMENT-ASSESSMENT.md` is named as the source of MIP Part 52 inside a modified tracked file. Deletion breaks live references. |
| **ARCHIVE-CANDIDATE** | Would moving them be neutral? | **NO.** Archiving is a move; the ledger keys on `by_path`. Moving an unregistered document changes the path a future mint would key on, converting an open question into a silently different one. |
| **IGNORE-CANDIDATE** | Is any path machine-local or regenerable? | **NO.** The one machine-local population that exists — `.ucos/` (fingerprint cache + per-run evidence) — is **already ignored** by the `.gitignore` change inside U-1, with an in-file rationale, and therefore never appears among the 390. Ignoring 111 governance determinations would make Rule 8 satisfiable by concealment. |

---

## §9 — STASH ENTRIES — **REQUIRES-HUMAN-DECISION (out-of-band)**

```
$ git stash list
stash@{0}: On integration/recovery-001: ProgB post-cbd7c51 partial: caps+pyproject+generator
stash@{1}: On integration/recovery-001: A+B working tree at boundary
stash@{2}: On integration/recovery-001: a07
```

**None was applied, dropped, or inspected.** `git stash show` was not run: a stash is
out-of-tree state, and its existence and undispositioned status are established without
reading it.

`stash@{0}` names "pyproject+generator", overlapping **U-1** (`pyproject.toml`) and **U-4**
(the generator). Whether it is superseded by the working tree or holds unmerged work is
**not determinable without inspecting it**, and that is deferred.

Stashes are not part of `git status` and do not themselves breach Rule 8. They are recorded
because a program certifying a clean tree while three undispositioned stashes sit beside it
has certified less than it appears to.

---

## §10 — CLASSIFICATION SUMMARY

| Classification | Paths | Units |
|---|---:|---|
| **COMMIT-CANDIDATE** | **26** | U-1 (19), U-2 (6), U-3 (1) |
| **ARCHIVE-CANDIDATE** | **0** | — (tested, §8.3) |
| **DELETE-CANDIDATE** | **0** | — (tested, §8.3) |
| **IGNORE-CANDIDATE** | **0** | — (tested, §8.3) |
| **REQUIRES-HUMAN-DECISION** | **364** | U-4 (250), U-5 (3), U-6 (111) |
| **TOTAL** | **390** | |
| *out-of-band* | 3 stashes | §9 |

---

## §11 — DETERMINATION

**BLOCKER-001 IS OPEN. It is not resolvable by this program.**

Rule 8 cannot be satisfied without dispositioning **364 paths whose disposition turns on a
single governance question no file in the repository answers**: whether the 228-identity mint
of `2026-08-23T13:32:44+00:00` was authorized.

The remaining **26 paths** (U-1, U-2, U-3) are commit-ready in substance and blocked only on a
verification run this program is forbidden to perform. Committing them alone would **not**
clear Rule 8 — 364 paths would remain — but it would reduce the blocker to its genuine core.

**Actions taken by this step: none.** No file was deleted, committed, moved, staged, or
modified. No stash was applied, dropped or read. No generator, engine or `verify.sh` was run.
