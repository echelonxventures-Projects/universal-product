# GATE PURITY DETERMINATION

| Field | Value |
|---|---|
| **ARTIFACT** | `GATE-PURITY-DETERMINATION.md` |
| **PHASE** | Foundation Closure Phase 3 — Gate Purity Analysis |
| **AUTHORITY** | **NONE — DERIVED TRUTH.** No gate is modified. No mode is legislated. No mutation-governance register is created. Every classification below is read from executing code, not from a comment. |
| **CLASSIFICATION** | `EVIDENCE` |
| **CANONICAL OWNER REUSED** | `verify.sh` (single entry point, `CMG-000001` Art. LXVI.7) · each programme's `*-declaration.json` (`forbidden_write_prefixes`) · `00-BOOK/DATA/generated-artifact-registry.json` (generated population) · `00-BOOK/DATA/mutation-governance-boundary.json` |
| **BASELINE** | HEAD `1f869865` · branch `integration/recovery-001` · working tree DIRTY |
| **DISPOSITION** | **DETERMINATION ONLY.** No gate behaviour changed. |
| **COMPANION** | `ASSESSMENT-CONFLICT-REGISTER.md` `CR-09` / decision `H-06` (the same defect, already registered) · `UICM-REPLAY-VERIFICATION-DETERMINATION.md` D-2.8 (the dependency) |

---

## 1. The structural finding

**Determination D-3.0.** The repository does not lack write discipline — it lacks a **declared
mode**. What gates declare instead is a write **scope**: a `forbidden_write_prefixes` list plus a
`--check-write-scope` self-guard (e.g. `00-MASTER/UCL-000001/ucl_engine.py:1236, 2564, 2709-2719`).

**Write scope is not observe mode.** An engine passes `--check-write-scope` while rewriting its own
register directory on every gate invocation, because its own home is inside its permitted scope. The
guard answers *"did you write outside your boundary?"* It never answers *"were you supposed to write
at all?"*

Measured surface on this baseline:

| Plane | Count |
|---|---:|
| `verify.sh` stages | 9 default + 1 opt-in (`--full`) |
| Makefile targets total | 170 |
| Makefile `*-gate` targets | **46** |
| Makefile `*-self` guard targets | 26 |
| Makefile `*-replay` / `*-render` targets | 16 |
| GitHub workflows | 28 |

**Gates that declare their mode in code or in a script header: 4.** All other gate entry points are
silent on the question.

**D-3.1 — the defect is measured, not theoretical.** `git status --porcelain` on this baseline shows
tracked register files staged or modified under `00-MASTER/UAIE-000001/`,
`00-MASTER/UAUE-000001/`, `00-MASTER/UAKOS-CLOSURE-008/` and `00-BOOK/DATA/`. Gate runs have
mutated Repository Truth, not scratch space.

---

## 2. Classification

Mode vocabulary used throughout, per the Phase-3 requirement:

- **OBSERVE MODE — READ ONLY.** Measures and reports. Writes nothing anywhere.
- **EXECUTION MODE — EXPLICIT MUTATION.** Writes, and the write is the declared purpose, reachable
  only through an explicit flag or subcommand.
- **UNDECLARED MUTATION.** Writes on a path named or labelled as a gate, with no declared mode.
  **This is the defect class.**

### 2.1 OBSERVE MODE — declared (4)

| Gate | Entry point | Where the mode is declared | Verified |
|---|---|---|---|
| Meta-constitutional conformance `CMG-INV-01..12` | `00-CMG/tools/cmg-gate.sh` → `cmg_validate.py --repo-root …` | script header lines 3–13; `verify.sh:150-158` ("Read-only and fail-closed (L.4): the validator writes nothing") | the only write is opt-in `--emit` (`cmg_validate.py:692, 725-726`); `verify.sh` stage 6 passes no `--emit` |
| Universal object governance `UGA-INV-01..10` | `00-MASTER/UCOS-UGA-001/uga_engine.py gate` | argparse help, verbatim: `"verify invariants, mutate nothing"` (`uga_engine.py:42, 1929`) | `cmd_gate` (`:1889`) calls `build(mint=False)`; every `_dump`/`emit` call is in `cmd_run` (`:1864-1886`: `_dump(LEDGER_PATH,…)` `:1869`, `emit(st)` `:1879`) |
| Autonomous universal evolution | `python -m engine.uaue.gate --gate` | docstrings `gate.py:677-683, 697-701`; `verify.sh:196-220` | writes are strictly behind `if args.render:` (`:824-826` → `render()` `:684-685`) |
| Evolution surface replay | `python -m engine.uaue.gate --replay` | `verify.sh:222` ff. stage 6d | regenerates in memory, compares committed **bytes**; `make uaue-render` is the mutating twin |

Plus one partial: **UCCEP** is the only engine that models emission as an *authority* rather than a
flag — `authority = emission_authority(decl, args.tier, args.authorize_emission)`
(`uccep_engine.py:1360`), `if authority["authorized"]: written = emit(...)` (`:1364-1365`), and it
prints `"OBSERVATION ONLY — emission withheld: …"` when it does not write. Its per-check evidence
logs are nonetheless written unconditionally (`:647-648`) into a gitignored path.

### 2.2 OBSERVE MODE — structural, undeclared

Read-only by construction, but nothing states it, so nothing holds them to it:

- **All 26 `*-self` guard families** (`--check-declaration`, `--check-no-enumeration`,
  `--check-write-scope`, `--check-determinism`, `--check-open-world`, `--check-knowledge-once`,
  `--check-record-immutability`, `--check-no-elevation`). In every engine read, the guard branch
  returns before measurement or write (`ucl_engine.py:2996-3014`, `ufep_engine.py:1095-1112`).
- **`uaep-gate`, `uaie-gate`** — the *correct* engine pattern: `if args.render: written =
  write_registers(model)` (`uaep_engine.py:656-659`, `uaie_engine.py:1538-1541`).
- `format-check`, `lint` (`ruff check` / `ruff format --check`; `make format` is the mutating twin),
  `selfaware-gate`, `homing-gate`, `constitution/convergence/freeze` report paths.

### 2.3 EXECUTION MODE — declared (correct)

| Gate | Declaration |
|---|---|
| `bash 00-BOOK/tools/register.sh --guard` (`verify.sh` stage 7, `--full` only) | `verify.sh:222-224`: *"it mutates generated DATA/REGISTRIES/CONTROL-TOWER/PORTAL, so it is opt-in for local runs."* Writes: 10 phases of `ukb build` / `ukbx sync\|twin\|portal\|certify` into tracked `00-BOOK/DATA`, `REGISTRIES`, `CONTROL-TOWER`, `PORTAL`; a lock file (`register.sh:103`); with `--install-hooks`, files inside the git dir (`:70-88`). |
| `make uaue-render` | Renders the 19 UAUE surfaces; separated from the gate by flag. |
| `make rpi-gate` | Declares its own limit in the Makefile comment: emission writes to `.runtime/repository-intelligence/`, which `.gitignore:12` excludes. |
| `uga_engine.py run` | Explicit subcommand, distinct from `gate`. |

### 2.4 UNDECLARED MUTATION — the defect class (≥24 gate paths)

Every entry in this section writes into **tracked** `00-MASTER/<PROGRAMME>/` register surfaces, on a
path whose name is `gate`, with no declared mode.

**GP-1 — write called unconditionally in `main()` (15 engines).** `--gate` measures *and* rewrites
the whole register surface. Canonical, fully verified example — `UCL-000001`:

```
Makefile:1779-1780      python3 00-MASTER/UCL-000001/ucl_engine.py --gate
ucl_engine.py:2983      parser.add_argument("--render", …, help="regenerate the registers")
                        ← no reference to args.render anywhere in the file (verified)
ucl_engine.py:3030      written = write_registers(model)          ← unconditional
ucl_engine.py:3058      if args.gate and model["gate"] != "OPEN": return 1   ← verdict AFTER the write
ucl_engine.py:2461-2466 HERE.mkdir(parents=True, exist_ok=True)
                        (HERE / name).write_text(text, encoding="utf-8")
                        MODEL.write_text(json.dumps(model, indent=2, sort_keys=True, …))
```

Targets are tracked (`git ls-files 00-MASTER/UCL-000001` lists them) and not gitignored. The gate
even prints `wrote {len(written)} artifacts to …` — the mutation is visible in the gate's own
stdout and still undeclared as a mode.

Same shape, same conclusion:

| Engine | Unconditional write | Makefile gate target |
|---|---|---|
| `00-MASTER/UCOS-UFEP-001/ufep_engine.py` | `:1119` | `ufep-gate` |
| `00-MASTER/UIS-001/uis_engine.py` | `:1814` | `uis-gate` |
| `00-MASTER/BASELINE-001/baseline_engine.py` | `:1896` | `baseline-gate` |
| `00-MASTER/UCOS-UCAF-001/ucaf_engine.py` | `:2104` | `ucaf-gate` |
| `00-MASTER/UCOS-URAT-001/urat_engine.py` | `:1009` | `urat-gate` |
| `00-MASTER/UCOS-UTCE-001/utce_engine.py` | `:855` | `utce-gate` |
| `00-MASTER/ACEE-000001/acee_engine.py` | `:3730` | `acee-gate` |
| `00-MASTER/UCDA-000001/ucda_engine.py` | `:1419` | `ucda-gate` |
| `00-MASTER/UEI-000001/uei_engine.py` | `:1367` | `uei-gate` |
| `00-MASTER/UER-000001/uer_engine.py` | `:1043` | `uer-gate` |
| `00-MASTER/UCEF-000001/ucef_engine.py` | `:1519` | `ucef-gate` |
| `00-MASTER/UCOS-AEE-001/aee_engine.py` | `:1807` | `aee-gate` **and `aee-observe`** |
| `00-MASTER/MCOS-000001/mcos_engine.py` | `:852` | `mcos-gate`, `mcos-certify` |
| `00-MASTER/UMK-000001/umk_engine.py` | `:641` | `umk-gate` |
| `00-MASTER/UPF-000001/upf_engine.py` | `:594` | `uprf-gate` |

**GP-2 — write executes before the gate branch (3 engines).** The engine writes, *then* decides
whether to fail:

- `00-MASTER/UCOS-RIB-001/rib_engine.py:3925` `written = write_outputs(decl, model)` → `:3942 if not
  args.gate:`
- `00-MASTER/URRC-000001/urrc_engine.py:2041` → `:2056 if not args.gate:`
- `00-MASTER/UCOS-UAR-001/uar_engine.py` — the write is **inside the gate function**: `_run_gate()`
  at `:118-125` (`out_path = _OUT_DIR / "uar.json"; out_path.write_text(output + "\n", …)`), and
  `main()` routes both `--gate` and the bare invocation to `_run_gate()` (verified).

**GP-3 — `--render` mode still writes the rendered surface (8 targets).**
`roadmap-gate` (no `--render` at all; `roadmap_engine.py:1513-1522` writes `ROADMAP_JSON` then calls
`render(payload)` unconditionally) · `corpus-gate` · `assimilate-gate` · `closure-gate` ·
`closure-phase2-gate` · `closure-phase3-gate` · `closure009-gate` / `closure009-baseline-gate`
(`requirement_engine.py:1753-1760`, unconditional, evaluated before the baseline verdict) ·
`lifecycle-closure-gate` · `final-closure-gate` (`final_closure_engine.py:496,500` before
`:513 if args.gate and not all(verdicts.values())`).

**GP-4 — dead `--render` flags (3 engines, verified by grep).** `--render` is declared and **never
read**:

```
00-MASTER/UCL-000001/ucl_engine.py:2983       add_argument("--render", …)   ← only occurrence
00-MASTER/UCOS-UFEP-001/ufep_engine.py:1082   add_argument("--render", …)   ← only occurrence
00-MASTER/UIS-001/uis_engine.py:1777          add_argument("--render", …)   ← only occurrence
```

Consequence: `make ucl-replay`, `make ufep-replay` and `make uis-replay` are **indistinguishable
from their gates** — both write. Any claim that these replay targets prove the committed registers
reproduce is a *render-then-diff-in-CI*, not a non-mutating replay check.

**GP-5 — hidden write inside a stage `verify.sh` documents as read-only (1, confirmed).**
`verify.sh:139-141` labels stage 4 *"Read-only eligibility/validity/classification gate"*. But
`cmd_enforce` (`00-BOOK/tools/ukb.py:1896`) calls `_enforcement_audit(record)` at `:1997`, which
appends to `.runtime/governance/enforcement-audit.json` via
`governance_telemetry.py:210-217` (`json.dump(...)` into a temp file, then `os.replace`). The
comment at `ukb.py:1948` is explicit that the audit *"is ALWAYS enforced — never conditional on an
invocation flag."* The path is gitignored (`.gitignore:12`), so it cannot dirty the tree — **but the
read-only label is false.** An append-only audit is a legitimate and arguably necessary write; the
defect is the undeclared label, not the write.

**GP-6 — `./verify.sh` is a mutating command overall.** Stage 1b (`verify.sh:104-119`) runs
`scripts/generate-prerequisites.sh`, which executes twelve generators (`engine.knowledge.cli init
--force` / `capabilities --write` / `docs`; `engine.determinism.reproduce`; `closure_engine.py`,
`phase2_engine.py`, `phase3_engine.py`; `intelligence.research build`; `intelligence.publication
build`; `provenance_engine.py`; `intelligence.realization realize`). The script header asserts it
*"Writes ONLY to the four ignored trees … can never dirty the working tree."* That claim requires
re-verification against `.gitignore:82-104`, which **re-includes ~24 closure filenames by `!`
negation** (`!…/02-AUTHORITATIVE-SOURCE-REGISTER.md`, `!…/13-CONSTITUTIONAL-GAP-REGISTER.md`,
`!…/15-CLOSURE-EVIDENCE-REPORT.md`, `!…/19-REPOSITORY-TRUTH-DETERMINATION.md`, …). If
`closure_engine.emit()` renders any of those ordinals, stage 1b dirties tracked files.
**Status: OPEN — unverified in both directions.**

**GP-7 — CI reverts gate mutation, in writing.** `.github/workflows/roadmap-gate.yml:81` runs
`git checkout -- 00-MASTER/UCOS-MXR-001` after the gate. This is the clearest existing admission
that the gate mutates: the pipeline has to undo it.

**GP-8 — a read-only *self-guard* on an engine whose own gate writes.** `make utce-self
--check-read-only` exists (Makefile 1669) while `utce_engine.py:855` rewrites its registers on every
non-guard invocation. The guard measures the **corpus**, not the engine.

**GP-9 — mutating into gitignored paths only** (lower severity; recorded for completeness):
`ukb enforce` audit (`.runtime/`), `rpi-gate` (`.runtime/`), UCCEP evidence logs
(`00-MASTER/**/evidence/`), `determinism.yml` → `determinism-evidence/`. These cannot dirty the
tree but are still undeclared writes.

**GP-10 — `make aee-observe` is documented in the Makefile as a "fast read-only pass"** while
`aee_engine.py:1807` calls `emit(...)` at module-`main` indentation, i.e. not guarded at the call
site. **Status: APPARENT — `emit()`'s body was not read for an internal tier suppression.** Recorded
as apparent rather than confirmed.

### 2.5 Workflows (28)

Mutation profile is inherited from the engine CLI each workflow invokes, so §2.4 applies unchanged
to `ucl-gate.yml`, `rib-gate.yml`, `ucef-gate.yml`, `mcos-gate.yml`, `aee-gate.yml`,
`closure009-gate.yml`, `assimilation-gate.yml`, `corpus-currency-gate.yml`, `urat`/`utce`/`ucaf`
gates. Three are distinguishable:

- `uaue-gate.yml:112` — `--quiet --json`, **no `--render`**: genuinely read-only, consistent with
  the engine.
- `baseline-gate.yml` — the **best-practice shape in the repository**: 7 fail-closed self-guards,
  then `--gate`, then a *replay* step (`--render --quiet` followed by `git diff --exit-code`), then
  an *append-only proof* over four named records, with artifact upload `if: always()`. Note the
  ordering makes the render explicit and separate. It nonetheless inherits GP-1 (its `--gate` writes
  5 files under `00-MASTER/BASELINE-001/`).
- `ucos-registration-gate.yml:54-60` — the most mutating workflow: `eligibility --unbound` →
  `enforce --pre` (GP-5 audit write) → `register.sh --guard` (full transaction).

---

## 3. Consequence — the cost is already recorded

**D-3.2:** the cost of undeclared gate mutation has already been paid once, and the loss is
documented.

`FINAL-FREEZE-ELIGIBILITY-DETERMINATION.md` §1.1 records that a gate-purity probe of
`assimilation_engine.py --gate` **wrote 11 tracked files**; two were already dirty pre-session and
were therefore left overwritten; the operator's uncommitted bytes for those two files are
**unrecoverable** (finding `F-A`). It also records finding `F-B`: HEAD's committed
`06-VALIDATION-REPORT.md` is stale against the working tree's `validation-record.json`.

`ASSESSMENT-CONFLICT-REGISTER.md` `CR-09` states the same defect from the governance side:
`00-BOOK/DATA/mutation-governance-boundary.json` names `UCCEP-000000`, `UCOS-RIB-001` and
`UCOS-AEE-001` as **gates** (governing authorities), while measured behaviour is that `uccep --gate`
wrote 47 tracked files across 4 programme homes and `ufep`/`urat`/`utce --gate` wrote 5 each. It is
registered as **human decision `H-06`**.

**Three downstream effects, stated plainly:**

1. **Replay verification is not trustworthy in this regime.** A gate that writes before it compares
   can only compare a file against itself. This is the hard dependency recorded as `D-2.8` in
   `UICM-REPLAY-VERIFICATION-DETERMINATION.md`.
2. **Observing the repository is destructive.** Running the gates locally to *check* state changes
   state, which then makes `rib` GATE-12 fail. Diagnosis and mutation are not separable today.
3. **Two committed derived artifacts record verdicts their own producers no longer compute** —
   `00-MASTER/UCL-000001/ucl.json` (`UCL-V-41: 217 / UCL-V-42: 84, satisfied`, versus 264/85
   measured) and `00-MASTER/UIS-001/uis.json` (`ungoverned_namespaces: 74`, verified by direct read,
   versus 81 measured). Stale projections are the *predictable* product of a surface that is
   rewritten by whichever gate ran last.

---

## 4. Determination

**D-3.3 — every gate SHALL declare exactly one mode, in the declaration surface that already
exists.** Each programme already ships a `*-declaration.json` carrying `forbidden_write_prefixes`.
The mode belongs there, beside the scope it complements. **No new registry, no new authority, no new
schema family** — this is an additive field on a located declaration, read by the guard that already
runs.

**D-3.4 — the reference implementations already exist. Adopt, do not invent.**

| Property | Reference |
|---|---|
| Observe / emit separated by flag | `engine/uaue/gate.py` (`--gate` / `--replay` vs `--render`) |
| Observe / emit separated by subcommand | `uga_engine.py` (`gate` vs `run`) |
| Emission as an authority with a withheld state | `uccep_engine.py` `emission_authority(...)` + `"OBSERVATION ONLY — emission withheld"` |
| Render-then-byte-diff as a separate CI step | `.github/workflows/baseline-gate.yml` replay + append-only proof |
| Mode declared at the pipeline level | `verify.sh` per-stage headers |

**D-3.5 — the minimum acceptance criteria for gate purity.** All five are measurements, none is a
new capability:

1. Every gate entry point resolves to exactly one declared mode: `OBSERVE` or `EXECUTION`.
2. No `OBSERVE` path performs any write, including to gitignored paths — or the write is declared as
   an audit obligation and the label is corrected (this is the honest resolution of GP-5).
3. No `EXECUTION` path is reachable without an explicit flag, subcommand or emission authority.
4. No flag is declared and unread (closes GP-4).
5. A `*-replay` target regenerates in memory and compares bytes; it never writes first (closes
   GP-3, and is the precondition for `D-2.8`).

**D-3.6 — REFUSED here, explicitly:**

- Changing any gate's behaviour in this phase. This document determines; it does not remediate.
- Creating a mutation-mode registry. `mutation-governance-boundary.json` and the per-programme
  declarations already exist; a third surface would be duplication.
- Reclassifying the 24 engines as *producers* in `generated-artifact-registry.json` **as a way of
  making the current behaviour conformant**. That is one of the two options `H-06` offers, and it is
  the owner's choice, not a measurement's. Recorded, not selected.
- Resolving `GP-6` or `GP-10` by assumption. Both are marked OPEN/APPARENT and require a read of
  `closure_engine.emit()`'s filename table and `aee_engine.emit()`'s body respectively.

---

## 5. Findings register

| # | Finding | Severity | Count | Status |
|---|---|---|---:|---|
| **GP-1** | Write called unconditionally in `main()`; gate verdict returned after the write | HIGH — mutates tracked truth | 15 engines | CONFIRMED |
| **GP-2** | Write executes before the gate branch, or inside the gate function | HIGH | 3 engines | CONFIRMED |
| **GP-3** | `--render`-mode gates still rewrite the register surface | HIGH | 8 targets | CONFIRMED |
| **GP-4** | `--render` flag declared and never read; replay ≡ gate | HIGH — invalidates the replay claim | 3 engines | CONFIRMED |
| **GP-5** | Stage documented read-only performs an always-on audit write | MEDIUM — gitignored path, false label | 1 | CONFIRMED |
| **GP-6** | `verify.sh` stage 1b generation vs `.gitignore` `!`-negated closure filenames | MEDIUM | 1 | **OPEN** |
| **GP-7** | CI reverts gate mutation with `git checkout` | MEDIUM — admission of the defect | 1 | CONFIRMED |
| **GP-8** | `--check-read-only` self-guard on an engine whose gate writes | LOW — misleading | 1 | CONFIRMED |
| **GP-9** | Undeclared writes to gitignored paths | LOW | 4 families | CONFIRMED |
| **GP-10** | `aee-observe` labelled "read-only pass"; `emit()` called at `main` indentation | MEDIUM | 1 | **APPARENT** |
| **GP-11** | Mode declared for only 4 of 46 `*-gate` targets; 26 `*-self` guards read-only but undeclared | HIGH — the structural finding | repo-wide | CONFIRMED |

---

## 6. Phase 3 verdict

**Gate mutation boundaries are NOT explicit on this baseline.** Four gates declare a mode; the
remaining gate surface declares a write *scope* that its own home satisfies while it rewrites that
home. Twenty-four gate paths mutate tracked Repository Truth without a declared mode, three
`*-replay` targets cannot prove reproduction because they render first, one stage documented as
read-only writes an audit unconditionally, and `verify.sh` as a whole is a mutating command.

The remediation is **declaration inside existing surfaces plus flag discipline** — no new
capability, no new registry, no architectural change. It requires human decision `H-06` (already
registered as `CR-09`), because choosing between *"require `--gate` to be write-free"* and
*"reclassify these gate modes as producers"* is an act of the mutation-governance owner.

**Nothing in this phase is authorized for implementation.** See
`FOUNDATION-CLOSURE-IMPLEMENTATION-READINESS.md` §3 decision **D-2**.
