# PHASE 0 — GOVERNANCE SAFETY BASELINE

**AUTHORITY = NONE (DERIVED TRUTH).** Evidence collection, root-cause determination and safety
analysis only. No closure work, no irreversible action, no registration, no commit, no stage, no
rebaseline, no certification. Nothing below was fixed or patched.

**Forbidden commands were not executed.** `uga_engine.py run` and `register.sh` (any mode) were **not
invoked in this phase**. Every determination about them rests on source inspection.

---

## 0. PHASE 0 STARTING STATE

| Property | Value |
|---|---|
| HEAD | `77798202d2df43285760b3277f230ebde4b52bbc` |
| Branch | `integration/recovery-001` |
| Total `git status --porcelain` entries | 94 |
| Tracked entries (non-`??`) | 61 |
| **Tracked-only fingerprint — the invariant** | **`a6494c55662ecf93874115bf9f900b11`** |
| Full fingerprint | `ac0cd8adff063f1b2eeeb0155dafc7e8` |
| `00-BOOK/` status | **clean** |
| `00-MASTER/UCOS-UGA-001/` status | **clean** |

The 94 comprise the 91-entry implementation baseline plus the 3 Phase 0 deliverables written
previously. The tracked-only fingerprint is the quantity this phase must preserve: new untracked
analysis documents do not modify, stage, or mutate governance state.

**Verified after every investigation block.** `git status --short` was executed after each block; the
tracked fingerprint returned `a6494c55662ecf93874115bf9f900b11` every time. **No stop condition
fired.**

---

# D0.1 — UGA MUTATION ROOT CAUSE ANALYSIS

## Evidence chain

All line numbers in `00-MASTER/UCOS-UGA-001/uga_engine.py` (1,936 lines).

### 1 · CLI ENTRYPOINT

`main()` at **1925–1933**. Three subcommands, dispatched by dict:

```python
sub.add_parser("run",   help="mint identities and emit all surfaces")
sub.add_parser("gate",  help="verify invariants, mutate nothing")
sub.add_parser("stats", help="print measured state")
return {"run": cmd_run, "gate": cmd_gate, "stats": cmd_stats}[args.cmd](args)
```

`cmd_run` at **1864**. Its first statement is `st = build(mint=True)` at **1865** — the mint flag is
bound to the verb with no interposed check of any kind.

### 2 · ELIGIBILITY SELECTION

`build()` at **1587**. Population at **1613**: `paths = _git_ls()`. `_git_ls()` at **165** invokes
`git ls-files` with fixed argv. **Eligibility is tracked files only** — narrower than `register.sh`,
which also admits untracked-not-ignored paths.

Mint stamp at **1619–1621**: derived from `git rev-parse HEAD`, not the clock, so `first_seen` is a
function of the commit.

### 3 · OBJECT DISCOVERY

`epoch0_discovery(paths, registered_docs, generated_paths)` at **1625**, defined at **232**.
Classification via `classify_object` (**187**), ownership via `derive_owner` (**218**).

### 4 · ID ALLOCATION — **TWO SITES, ONLY ONE COUNTED**

**Site A — `epoch1_identity`, defined 258, called at 1626.** Allocation at **291–303**:

```python
cat = ID_CATEGORY[o["object_class"]]
n = seq.get(cat, 0) + 1
seq[cat] = n                                   # 293  shared category_seq
uid = f"UCOS-{cat}-{n:06d}"
by_object[rel] = {...}                         # append-only map
minted.append(rel)                             # 303  COUNTED
```

Pre-existing entries take the `existing` branch at **283–286** and `continue` — **nothing is appended
to `minted`**. With `mint=False`, **288–290** appends to `anonymous` instead.

**Site B — `mint_observation`, defined 464, reached via `epoch_observation_universe` (512), called at
1651.** Allocation at **483–491**:

```python
seq = ledger.setdefault("category_seq", {})
n = seq.get("OBS", 0) + 1
seq["OBS"] = n                                 # 485  SAME shared counter
oid = f"UCOS-OBS-{n:06d}"
by_obs[key] = {...}                            # append-only map
return oid                                     # returned — NEVER counted
```

`build()` returns `minted=minted` at **1683**, sourced **only** from `epoch1_identity` at **1626**.
Grep confirms `st["minted"]` is touched at exactly three places — **1868, 1880, 1881** — all in
`cmd_run`, all downstream of `build`. **No observation mint ever reaches `st["minted"]`.**

### 5 · LEDGER WRITE

`LEDGER_PATH` at **61** = `00-BOOK/DATA/id-ledger.json`. Written at **1869** in `cmd_run`:

```python
if _dump(LEDGER_PATH, st["ledger"]):
```

`_dump` (**130**) → `_write_text` (**136**), which is **change-detecting**:

```python
with open(path, encoding="utf-8") as fh:
    if fh.read() == text:
        return False          # bytes identical — NOT written
...
return True                   # written
```

### 6 · SUMMARY REPORTING

Two lines, with different conditions:

```python
minted = len(st["minted"])                               # 1868  true per-invocation count
if _dump(LEDGER_PATH, st["ledger"]):                     # 1869
    print(f"identity ledger updated: {minted} minted")   # 1870  CONDITIONAL
    st = build(mint=False)                               # 1878  full rebuild
changed = emit(st)                                       # 1879
st["minted"] = [None] * minted                           # 1880  count restored
print(f"UGA run — objects={...} minted={len(st['minted'])} "
      f"retired={len(st['retired'])}")                   # 1881  UNCONDITIONAL
```

Line **1880** is decisive: the rebuild at 1878 discards `minted`, and 1880 restores the count captured
at 1868. **The unconditional summary therefore reports the true count from the `mint=True` build.**

---

## ROOT CAUSE

**Two mechanisms. The first withdraws my prior finding; the second is the genuine defect.**

### Mechanism 1 — the observed `minted=0` was truthful. My prior attribution was wrong.

Because line 1880 faithfully restores the count, `minted=N` reports what *this invocation* minted.
`minted=0` means "this invocation minted nothing" — it is **not** a misreport.

The observed incident is fully explained by invocation count, not by the engine:

- **Invocation #1** was piped through `grep -iA40 "anonymous"`. It minted the 25 identities and printed
  both `identity ledger updated: 25 minted` and `minted=25`. Neither string contains "anonymous", so
  the filter discarded **the entire output**. The command returned empty and the allocation went
  unseen.
- **Invocation #2** ran against the now-current ledger. Every object hit the `existing` branch at
  283–286 and `continue`d, so `minted == []`. `_dump` found byte-identical content and returned
  `False`, so line 1870 did not fire and no rebuild occurred. Line 1881 printed `minted=0`
  **correctly**.

> **CORRECTION.** The central claim of prior finding F-N1 — that `uga_engine.py run` "reports
> `minted=0` while allocating permanent Universal IDs" — **is WITHDRAWN as to the observed incident.**
> The engine reported accurately on both invocations. The cause was my output filter on invocation #1
> and my failure to account for idempotency on invocation #2. Under the evidence hierarchy, source
> code (tier 2) overrides my own prior assertion (tier 6). The 25 IDs were genuinely allocated and
> genuinely reverted; only the *attribution of blame* was wrong.

### Mechanism 2 — the symptom IS reachable, by the observation-mint path

`mint_observation` (**464**) allocates a permanent `UCOS-OBS-NNNNNN` identity, increments the shared
`category_seq["OBS"]` at **485**, and writes `ledger["by_observation"]` — and its result reaches
`st["minted"]` **nowhere**.

Consequence, established by source: add an entry to `DECLARED_OBSERVATIONS` (**499–508**) while no
*object* is newly discovered, then run `run`. Then:

- a permanent OBS identity is allocated and the append-only ledger is written;
- `epoch1_identity` mints nothing, so `minted == []`;
- `_dump` returns `True` (ledger bytes changed), so line 1870 fires and prints
  **`identity ledger updated: 0 minted`** — self-contradicting: the ledger *was* updated, and the
  count printed is zero;
- line 1881 prints **`minted=0`**.

**This is the honest answer to the question posed.** `run` *can* allocate permanent Universal IDs while
reporting `minted=0` — not by the route first reported, but through the observation-mint path, whose
allocations are invisible to both printed lines.

---

## AFFECTED COMPONENTS

| Component | Location | Role |
|---|---|---|
| `cmd_run` | `uga_engine.py:1864–1886` | Binds `mint=True` to the verb; owns both report lines |
| `build` | `1587–1690` | Threads `mint` to both allocation sites; returns `minted` from one |
| `epoch1_identity` | `258–309` | Object allocation — **counted** (303) |
| `mint_observation` | `464–492` | Observation allocation — **uncounted** (485) |
| `epoch_observation_universe` | `512–538` | Calls Site B for every declared observation |
| `DECLARED_OBSERVATIONS` | `499–508` | 7 entries; adding one triggers Mechanism 2 |
| `_dump` / `_write_text` | `130–146` | Change-detecting ledger write; gates line 1870 |
| `cmd_gate` | `1889–1917` | Read-only; **emits the remediation hint naming `run`** (1543, 1908) |
| `LEDGER_PATH` | `61` | `00-BOOK/DATA/id-ledger.json` — append-only, irreversible |
| `OUT` (11 targets) | `69–84` | 10 files under `00-MASTER/UCOS-UGA-001/` + `00-BOOK/DATA/canonical-observation-audit.json` |

---

## RISK

| # | Risk | Severity | Basis |
|---|---|---|---|
| R1 | **No freeze guard whatsoever.** `cmd_run` performs append-only allocation with no dirty-tree check, no dry-run default, no confirmation prompt, no authorization token. Line 1865 is the first statement of the function | **CRITICAL** | Source: 1864–1869 |
| R2 | **A read-only gate advertises the irreversible verb.** `cmd_gate` prints `ANONYMOUS OBJECTS: N — run \`uga_engine.py run\`` (1908) and UGA-INV-01's remediation text is `"Run \`uga_engine.py run\` to mint identities…"` (1543). Neither states that the command writes an append-only ledger. **This is how the Phase 0 incident began** | **CRITICAL** | Source: 1543, 1908 |
| R3 | **Observation mints are unreported in both lines** (Mechanism 2). A permanent identity can be allocated with `minted=0` printed, and `identity ledger updated: 0 minted` is self-contradicting | **HIGH** | Source: 485 vs 1683 |
| R4 | **Allocation evidence lives on a conditional line.** After any repeat invocation, stdout contains no trace that allocation ever occurred. `minted=0` cannot be distinguished from "nothing was ever minted" | **HIGH** | Source: 1869–1870 |
| R5 | **Idempotency conceals history by design.** The comment at 1871–1877 makes the second run a no-op deliberately. Correct for determinism; it also means the summary is not a record of ledger state | **MEDIUM** | Source: 1871–1878 |
| R6 | **Ledger and 10 governed surfaces are written in one verb.** No way to regenerate surfaces without risking allocation | **MEDIUM** | Source: 1869, 1698, 1858 |
| R7 | **`retired` is computed but never acted on.** `retired=2` at 306–308 identifies identities for paths no longer tracked; entries are retained (correct, append-only) but the count is reported without disposition | **LOW** | Source: 306–308 |

---

# D0.2 — REGISTRATION SAFETY MATRIX

Every row cites source. No assumptions.

| Operation | Writes Ledger | Reversible | Authorized | Source evidence |
|---|---|---|---|---|
| `register.sh` (bare) | **YES** | **NO** — append-only | **NO** | `register.sh:214` `ukb.py build --mint`; comment 208–213: "the one place permitted to allocate permanent Universal IDs and page ranges … the flag is what makes minting a decision rather than a side effect" |
| `register.sh --observe` | **NO** | n/a | **YES** | `:95` "VERIFICATION PLANE — --observe. Read-only."; `:108` `ukb.py enforce --pre`, `:111` `ukb.py validate` — verification verbs only, and the block returns before the transaction |
| `register.sh --guard` | **YES** | **NO** | **NO** | `:24` "transaction + drift gate (CI/pre-commit)"; `:28` "additionally fails (exit 3) if, **after registration**…". `OBSERVE=1` is the only early-exit; `--guard` falls through to `:214` |
| `register.sh --install-hooks` | NO | YES | conditional | `:72` "Writes a git pre-commit hook … never modifies" repository content |
| `uga_engine.py run` | **YES** | **NO** | **NO — FORBIDDEN** | `1865` `build(mint=True)`; `1869` `_dump(LEDGER_PATH, …)`; allocation at `293` and `485` |
| `uga_engine.py gate` | **NO** | n/a | **YES** | `1890` `build(mint=False)`; no `_dump`/`_write_text` anywhere in `cmd_gate` (1889–1917). Empirically confirmed in the prior phase: `git status` md5 identical across a run |
| `uga_engine.py stats` | **NO** | n/a | **YES** | `1919–1922` `build(mint=False)` then `print` only |
| `ucaf_engine.py --gate` | No ledger, **YES registers** | **YES** — tracked, `git checkout` restores | **NO — it writes** | `2103` `written = write_registers(model)` executes **UNCONDITIONALLY**, and `2127` `if args.gate:` is evaluated **after**. `write_registers` (`1872–1884`) calls `target.write_text(...)` with **no change detection** |
| `ucaf_engine.py --render` | No ledger, YES registers | YES | by intent | same path; `--render` is the honestly-named verb for it |
| `ucaf_engine.py --<guard-name>` | **NO** | n/a | **YES** | `2119–2135`: a non-empty `selected` list returns at 2135, **before** reaching 2103 |
| `ucon` gate (verify.sh stage 16) | No ledger | — | **REQUIRES REVIEW** | `verify.sh:674`. The engine was **not inspected** this phase. Not certified either way |
| `verify.sh` | **NO ledger** | Partly | **CONDITIONAL** | Invokes only read-only governance verbs: `:457` `uga_engine.py gate`, `:798` `register.sh --observe`. **But** `:344–345` runs `scripts/generate-prerequisites.sh`, which writes |

### Findings from the matrix

**M-1 · `ucaf_engine.py --gate` is not read-only.** A flag named `--gate` — which everywhere else in
this repository denotes fail-closed verification — regenerates and rewrites every UCAF register plus
`ucaf.json` before the verdict is computed. This is the most likely explanation for the 5 dirty
`00-MASTER/UCOS-UCAF-001/*` entries in the baseline, though this phase did not run it to confirm.
Compounding: `write_registers` writes unconditionally, unlike `uga_engine._write_text` which compares
first.

**M-2 · No ledger-writing command is reachable from `verify.sh` or from CI.** `verify.sh` uses
`uga_engine.py gate` and `register.sh --observe`, both read-only. `.github/workflows/ucos-registration-gate.yml:60`
runs `register.sh --observe`, and it is the **only** `register.sh` invocation across all 35 workflows.

**M-3 · Correction to the frozen hook's documentation.** `.kiro/hooks/auto-register-artifact.json`
states its freeze "does not alter `.github/workflows/ucos-registration-gate.yml`, which still runs
`register.sh --guard` on every push." **The workflow runs `--observe`, not `--guard`** (line 60,
sole invocation). Tier 2 (source) overrides tier 5 (documentation). **CI does not mint.** This is a
materially safer posture than the documentation asserts, and it should be corrected rather than left
to imply an exposure that does not exist.

---

# D0.3 — GOVERNANCE WRITE SURFACE INVENTORY

Exhaustive for discovered mutation paths into `00-BOOK/`, `00-MASTER/`, identity/registration ledgers
and audit/governance registries.

### W-1 · `register.sh` (bare or `--guard`)

```text
COMMAND                 bash 00-BOOK/tools/register.sh [--guard] [--strict]
TARGETS                 00-BOOK/DATA/id-ledger.json  (identity + page ledger)
                        00-BOOK/** derived registries, portal pages, control tower
WRITE PATH              register.sh:214 -> ukb.py build --mint -> append-only ledger
OWNER                   REG-AUTO-001 (declared authority for CORPUS_REGISTRATION mutation)
REVERSIBLE?             NO — permanent identity + page-range allocation
AUTHORIZATION REQUIRED? YES — owner decision. NOT AUTHORIZED. Aggravated by eligibility:
                        `git ls-files --cached --others --exclude-standard` admits
                        untracked paths (70 currently, 30 corpus-matching)
```

### W-2 · `uga_engine.py run`

```text
COMMAND                 python 00-MASTER/UCOS-UGA-001/uga_engine.py run
TARGETS                 00-BOOK/DATA/id-ledger.json                  (append-only)
                        00-BOOK/DATA/canonical-observation-audit.json
                        00-MASTER/UCOS-UGA-001/  (10 files: 00,01,02,03,04,05,06,07,08 + dashboard)
WRITE PATH              1869 _dump(LEDGER_PATH) ; 1698 _dump(OUT[key]) ; 1858 _write_text(dashboard)
                        allocation: 293 seq[cat] (objects) ; 485 seq["OBS"] (observations)
OWNER                   UCOS-UGA-001
REVERSIBLE?             Ledger NO (append-only). The 10 surfaces YES (tracked)
AUTHORIZATION REQUIRED? YES. **FORBIDDEN THIS PHASE — not executed.**
```

### W-3 · `ucaf_engine.py` without a guard flag (includes `--gate` and `--render`)

```text
COMMAND                 python 00-MASTER/UCOS-UCAF-001/ucaf_engine.py [--gate|--render]
TARGETS                 00-MASTER/UCOS-UCAF-001/** registers + ucaf.json (MODEL)
WRITE PATH              2103 write_registers(model) -> 1872-1884 target.write_text (NO
                        change detection) ; MODEL.write_text
OWNER                   UCOS-UCAF-001
REVERSIBLE?             YES — tracked; `git checkout --` restores
AUTHORIZATION REQUIRED? Yes for --gate, because the name implies verification and the
                        behaviour is mutation (M-1). Not currently gated
```

### W-4 · SessionStart hook `uakos-closure-002` — **the only ACTIVE hook**

```text
COMMAND                 CLOSURE_SKIP_CORPUS=1 python3 \
                          00-MASTER/UAKOS-CLOSURE-002/closure_engine.py
TRIGGER                 SessionStart — fires AUTOMATICALLY, no human action
TARGETS                 00-MASTER/UAKOS-CLOSURE-002/**
                          - 32 files are git-TRACKED
                          - closure.json is gitignored (.gitignore:59)
                        Observed this session: "wrote 15 artifacts"
WRITE PATH              closure_engine.py:519 p.write_text ; :746 closure.json write_text
OWNER                   UAKOS-CLOSURE-002
REVERSIBLE?             YES — tracked outputs restorable
AUTHORIZATION REQUIRED? Currently NONE. Fires unconditionally at session start
LEDGER REACH            NONE — verified: no `id-ledger`, `register.sh`, `ukb.py` or `mint`
                        reference in the engine. It reads 00-BOOK but never writes it.
                        `CLOSURE_SKIP_CORPUS=1` (:177) further narrows it to repo-only
```

**Assessment.** Byte-idempotent at this commit — `00-MASTER/UAKOS-CLOSURE-002/` is clean in the
baseline despite 15 writes. The residual risk is that an automatic, ungated write path into **tracked
governance content** exists at all: should its output ever differ, tracked registers are silently
dirtied before the operator issues a single command, and the GIT CLEAN INVARIANT is broken by session
start rather than by any action.

### W-5 · `scripts/generate-prerequisites.sh` (reached by `verify.sh` stage 1b)

```text
COMMAND                 bash scripts/generate-prerequisites.sh   (verify.sh:344-345)
TARGETS                 knowledge/                       (gitignored)
                        determinism-evidence/            (gitignored)
                        00-MASTER/UAKOS-CLOSURE-002/*.md (MIXED: 32 tracked)
WRITE PATH              4 producers, incl. :65 closure_engine.py
OWNER                   P0-FINAL-CONVERGENCE-001
REVERSIBLE?             YES
AUTHORIZATION REQUIRED? No — but it makes `verify.sh` a WRITING operation, which matters
                        when running it under a governance freeze
LEDGER REACH            NONE
```

### W-6 · `auto-register-artifact` hook — **INERT**

```text
STATUS                  FROZEN. "hooks": [] — verified by JSON parse
PRESERVED PAYLOAD       $frozen_hook_B01a: PostFileCreate on \.(md|txt|docx)$
                        -> bash 00-BOOK/tools/register.sh   (i.e. W-1, unguarded)
REVERSIBLE?             Re-arming is a deliberate edit
AUTHORIZATION REQUIRED? YES — two conditions stated in-file, BOTH UNMET:
                        (1) eligibility policy reconciled (config.py REGISTRATION_SCOPE
                            vs ukb.py:697); (2) prior ledger damage dispositioned
```

### Inventory summary

| Surface | Reaches an append-only ledger | Gated today |
|---|---|---|
| W-1 `register.sh` bare/`--guard` | **YES** | **NO** |
| W-2 `uga_engine.py run` | **YES** | **NO** |
| W-3 `ucaf_engine.py --gate`/`--render` | No | No |
| W-4 SessionStart hook | No | **NO — fires automatically** |
| W-5 `generate-prerequisites.sh` | No | No |
| W-6 frozen hook | Would (via W-1) | **YES — inert** |

**Exactly two commands can reach an append-only identity ledger: W-1 and W-2. Neither has any guard.**
That is the whole attack surface for irreversible allocation, and its smallness is what makes D0.4
tractable.

---

# D0.4 — REGISTRATION SAFETY BARRIER DESIGN

**Design only. Nothing below is implemented.**

**Requirement.** Prevent accidental execution of irreversible registration, where "accidental" is
defined by the observed incident: an operator follows a read-only gate's own remediation hint and
allocates permanent identities without intending to.

### Option 1 — Authorization token enforcement

A ledger write requires a token artifact naming the expected allocation set (paths + counts), which
the writer must match before committing bytes.

```text
BENEFITS       Authorization becomes an artifact, reviewable and auditable. Naming the
               expected set converts the post-condition into a CHECKABLE claim — a
               mismatch (e.g. 25 vs the report's 24) fails closed rather than proceeding.
FAILURE MODES  Token goes stale as the tree moves; operators generate a token reflexively,
               making it ceremony; a token committed to the repository authorizes forever.
BYPASS RISK    LOW-MEDIUM. Bypassable by generating a token, which is a deliberate act —
               and that is the point. Must not be creatable by the same command it gates.
COMPLEXITY     MEDIUM. Token schema, generator, validator, expiry-by-commit-SHA.
```

### Option 2 — Dry-run prerequisite

`run` refuses unless a preceding `--dry-run` produced a plan digest that matches current state.

```text
BENEFITS       Directly addresses the incident: the first invocation would have PRINTED
               the 25 allocations and written nothing. Cheap; reuses the existing
               mint=False path, which already computes `anonymous` exactly.
FAILURE MODES  Two-step flows get scripted into one (`--dry-run && run`), restoring the
               hazard. Plan digest must cover the ledger, or a concurrent change slips in.
BYPASS RISK    MEDIUM. Trivially chained in a shell one-liner.
COMPLEXITY     LOW. `build(mint=False)` already yields the plan.
```

### Option 3 — Freeze guard (dirty-tree refusal)

Any ledger writer refuses when `git status --porcelain` is non-empty.

```text
BENEFITS       Enforces the GIT CLEAN INVARIANT mechanically at the only place it matters.
               Would have refused the Phase 0 incident outright — the tree had 91 entries.
               Makes the ledger delta of a run reviewable in isolation, because it is the
               only change present.
FAILURE MODES  Refuses legitimate registration of a change not yet committed — the normal
               case, since new artifacts are what need identities. Needs a narrow, declared
               allowance (e.g. staged-only, or paths named in the token).
BYPASS RISK    LOW. Bypass requires committing or stashing, both deliberate and recorded.
COMPLEXITY     LOW. One subprocess call, one comparison.
```

### Option 4 — Dual authorization

Two distinct approvals recorded before allocation.

```text
BENEFITS       Strongest defence against a single mistaken actor.
FAILURE MODES  Unworkable for a single-operator repository; degrades to one person
               approving twice, which is theatre and worse than nothing because it
               manufactures an audit trail implying review that did not occur.
BYPASS RISK    HIGH in practice, precisely because of the above.
COMPLEXITY     HIGH. Identity, non-repudiation, approval storage.
```

### Option 5 — Mutation interlock

A process-wide flag that must be explicitly armed; all write helpers assert it.

```text
BENEFITS       Catches every writer, including future ones, at one assertion.
FAILURE MODES  In-process only — no protection against a second invocation or another
               tool. Arming is one line, so it drifts into being armed by default.
BYPASS RISK    HIGH. Same-file, same-process; trivially set.
COMPLEXITY     LOW-MEDIUM.
```

### Option 6 — Ledger write protection at the choke point

The barrier lives **below** the callers: a single guarded write function is the only code path that may
open an append-only ledger for writing, and it enforces the preconditions itself.

```text
BENEFITS       COMPLETE BY CONSTRUCTION over the measured surface. D0.3 establishes there
               are exactly TWO ledger-reaching commands (W-1, W-2), each with ONE ledger
               path constant (uga_engine.py:61; ukb.py's ledger path). A choke point is
               therefore small and total, whereas guarding CLI verbs is O(verbs) and
               silently misses every future caller — including a re-armed W-6.
               Also fixes the reporting defects: the choke point is the one place that
               knows the true byte delta, so it can report allocations UNCONDITIONALLY and
               truthfully, closing R3 and R4 and Mechanism 2 in the same change.
FAILURE MODES  A new writer that does not route through it (mitigable: a test asserting no
               other module opens the ledger path for writing — the repository already
               uses this pattern, cf. REQUIRED_STATE_NAMES at state.py:340).
               Refusing inside a low-level helper yields poor error locality unless the
               refusal names the calling verb.
BYPASS RISK    LOWEST of the six. Bypass requires writing new code that deliberately
               avoids the helper, which is not an accident.
COMPLEXITY     MEDIUM. One guarded writer, two call-site migrations, one no-other-writer
               test.
```

---

## RECOMMENDATION

**Adopt Option 6 as the barrier, composed with Option 3 as its precondition and Option 1 as its
release mechanism.** Reject Options 4 and 5. Retain Option 2 as a usability affordance, not a control.

```text
Option 6  the single guarded ledger writer          <- WHERE the barrier lives
  enforces Option 3  clean tree, else REFUSE        <- DEFAULT state is refusal
  released by Option 1  token naming expected set   <- HOW an authorized run proceeds
  reports the true byte delta UNCONDITIONALLY       <- closes R3, R4, Mechanism 2
```

### Justification

**Placement is the whole decision.** The incident did not occur because a check was missing from
`cmd_run`; it occurred because *no layer between the operator and the append-only ledger refuses by
default*. Guarding `cmd_run` alone would leave W-1 unguarded, and re-arming W-6 would restore the
original exposure through a path no verb-level guard covers. Option 6 sits beneath both W-1 and W-2, so
one barrier covers the entire measured surface.

**The surface is small enough for completeness to be provable, and this is measured, not hoped.** D0.3
enumerates every governance write path; exactly two reach an append-only ledger, each through a single
path constant. A "no other module opens this path for writing" test makes the choke point's totality a
mechanical property rather than a convention — and that is the same discipline the repository already
applies at `state.py:340`, which is the pattern Ω∞-B named as the cheapest structural improvement
available anywhere in the programme.

**Option 3 supplies the default, and it is the one control that would have stopped the actual
incident.** The tree had 91 entries. A clean-tree precondition refuses unconditionally in exactly that
situation, with no judgement required from the operator. It also makes any authorized allocation
reviewable, because the ledger diff is then the only change in the tree.

**Option 1 supplies the release, and it repairs a real defect rather than adding ceremony.** A token
naming the expected allocation set converts the post-condition into something checkable. Applied to the
current blocker it would have caught the 24-versus-25 discrepancy mechanically: a token naming the
closure report's 24 paths would **fail closed** against an engine that allocates 25, instead of
silently leaving one artifact anonymous and stage 9 red.

**Options 4 and 5 are rejected on evidence, not preference.** Dual authorization degrades to one person
approving twice in a single-operator repository, which is worse than no control because it fabricates
an audit trail implying review that never happened. A mutation interlock is same-process and
same-file — it offers no protection against the second invocation, which is precisely the shape of the
observed incident.

**Option 2 is retained but demoted.** A dry-run is genuinely useful and nearly free, since
`build(mint=False)` already computes the exact `anonymous` set. But it is chainable into one shell line
and therefore cannot be the control.

### Two changes outside the barrier, both prerequisites

1. **R2 — `cmd_gate` must stop advertising an unguarded irreversible verb.** The remediation strings at
   `1543` and `1908` should name the guarded, token-requiring path and state that it writes an
   append-only ledger. **The incident began by following the gate's own advice**, so leaving this
   unchanged leaves the most likely trigger intact regardless of the barrier.
2. **M-1 — `ucaf_engine.py --gate` must not write.** A flag named `--gate` that regenerates registers
   before computing its verdict will keep producing unexplained dirty trees and defeating the clean-tree
   precondition the barrier depends on. `--gate` should return `gate_exit` without calling
   `write_registers`; `--render` already exists for the writing behaviour.

---

# PHASE 0 SUCCESS CRITERIA — VALIDATION

| Criterion | Result |
|---|---|
| D0.1 UGA mutation root cause analysis | **COMPLETE** — full chain, two mechanisms, prior finding corrected |
| D0.2 Registration safety matrix | **COMPLETE** — 12 operations, every row source-cited |
| D0.3 Governance write surface inventory | **COMPLETE** — 6 surfaces; exactly 2 reach a ledger |
| D0.4 Registration safety barrier design | **COMPLETE** — 6 options evaluated, 1 recommended |
| Forbidden commands not executed | **HELD** — `uga_engine.py run` and `register.sh` not invoked |
| No governance mutation | **HELD** — `00-BOOK/` and `00-MASTER/UCOS-UGA-001/` clean |
| No registration activity | **HELD** |
| No new modifications to tracked files | **HELD** — tracked fingerprint `a6494c55662ecf93874115bf9f900b11` unchanged |
| No new staged files | **HELD** — staged set unchanged |
| Repository state unchanged | **HELD for tracked state.** One new untracked deliverable (this file), 94 → 95 entries. No modification, no staging, no governance mutation |

**Stop conditions: none fired.** No governance file mutation, no ledger mutation, no registration
attempt, no append-only write, no unexpected git status delta at any checkpoint.

## Outstanding, and not certified by this phase

| Item | Status |
|---|---|
| `ucon` gate write behaviour | **REQUIRES REVIEW** — engine not inspected |
| `ucaf_engine.py --gate` writing | **Source-established (tier 2), not executed.** Predicted to write; not confirmed by run |
| Mechanism 2 (observation-mint undercount) | **Source-established (tier 2), not executed.** Confirming it requires `run`, which is forbidden |
| Cause of the 19 modified register files in the baseline | **UNVERIFIED.** M-1 and W-4 are candidates; neither confirmed |

**Phase 1 authorization:** the four deliverables are complete and tracked state is unchanged, so the
Phase 0 success criteria are satisfied. Registration remains **NOT AUTHORIZED** — the barrier of D0.4
does not exist yet, and R2 and M-1 are open.
