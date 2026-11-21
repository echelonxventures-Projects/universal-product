# UCOS Ω∞ — EXECUTION ENVIRONMENT ASSESSMENT

| Field | Value |
|-------|-------|
| ARTIFACT ID | `UCOS-EEA-000001` |
| ARTIFACT | Execution Environment Assessment — Phase 1 discovery for Universal Execution Governance |
| **AUTHORITY** | **NONE — DERIVED TRUTH.** This document measures; it legislates nothing. The governing declaration is `00-MASTER/UEG-000001/ueg-declaration.json`. |
| BASELINE | HEAD `03179308` · branch `integration/recovery-001` |
| MACHINE | `darwin` arm64 · macOS (Darwin 27.0.0) |
| METHOD | Direct measurement of the working tree. Every claim below was executed, not inferred. |
| STATUS | **DISCOVERY COMPLETE.** Phases 2–10 proceed from these findings. |

> **What this document is for.** The directive asked for discovery before implementation, and
> discovery changed the plan. The headline expectation going in was that verification was slow
> and had to be optimised. It is not slow: the environment step costs **0.11–0.15 s** on the
> healthy path and full planning costs **0.66 s**. The real exposure is **correctness** — the
> repository can execute verification against an environment it never checked, and did so on
> this machine. What follows separates the two.

---

## §1 — CURRENT EXECUTION MODEL, AS MEASURED

### 1.1 Runtime

| Property | Value | Source |
|---|---|---|
| Canonical Python series | `3.12` | `scripts/ucos-env.sh:36` (`UCOS_PYTHON_SERIES`) |
| Canonical venv | `<repo>/.ec1-venv` | `scripts/ucos-env.sh:46` |
| Venv interpreter | `/Users/bipin/Desktop/UCOS-CONSOLIDATION/.ec1-venv/bin/python` → **Python 3.12.13** | measured |
| Global interpreter | `/opt/homebrew/bin/python3` → **Python 3.14.4** | measured |
| Global pytest | `/opt/homebrew/bin/pytest` — **present on PATH** | measured |
| Requires-python | `>=3.12` | `pyproject.toml` |

The global interpreter is **two minor series ahead** of the canonical one, and a global
`pytest` shadows the canonical one on PATH. Both conditions exist on this machine right now.

### 1.2 Pinned toolchain (single source of truth)

`pyproject.toml [project.optional-dependencies].dev` is the only place versions are declared;
`ucos_expected_deps()` parses that exact list, so nothing is restated anywhere:

```
pytest==8.3.4   pytest-cov==6.0.0   coverage==7.15.2   ruff==0.8.4   jsonschema==4.26.0
```

### 1.3 Entry points and what each is allowed to do

| Entry point | Sources `ucos-env.sh` | Creates venv | Installs packages | Network |
|---|---|---|---|---|
| `./bootstrap.sh` | yes | **yes** (`ucos_ensure_venv`) | **yes** | yes |
| `./doctor.sh` | yes | only with `--fix` | only with `--fix` | with `--fix` |
| `./verify.sh` | yes | **yes** (`ucos_ensure_venv`, line 105) | **yes** | **yes** |
| `make verify` | delegates to `verify.sh` | — | — | — |
| `.github/workflows/ec1-ci.yml` | no | `actions/setup-python` + `pip install -e ".[dev]"`, then `./verify.sh --full` | yes | yes |

### 1.4 Verification pipeline

`./verify.sh` has five modes (`--fast`, `--change` (default), `--integration`, `--full`,
plus `--explain`), declared in `00-MASTER/UVI-000001/uvi-declaration.json`
(`mode_constitution`) and classified stage-by-stage in its `stage_registry`. Fourteen
`run_stage` literals exist. Those literals are a **three-reader contract**:

1. `verify.sh` executes them,
2. `00-MASTER/UAKOS-CLOSURE-008/validation-record.json` digests them
   (`platform/tests/test_canonical_validation_evidence.py:88-90` re-derives them by regex),
3. `.github/workflows/uisd-gate.yml:260-277` re-derives them independently.

**Design consequence, recorded here because it constrains Phase 3.** An environment
integrity gate must NOT be added as a fourteenth-plus `run_stage`. Doing so would mutate
a digested contract read by three independent parties, and — more fundamentally — it is
the wrong ordering: a `run_stage` runs *through* `$PY`, and the gate's entire purpose is
to decide whether `$PY` may be trusted at all. The gate belongs in **Stage 0**, before the
plan is computed, as the existing `ucos_ensure_venv` call does today.

---

## §2 — FINDINGS

Seven findings. Four are defects, three are structural gaps. Severity is by what the
condition can cause, not by how likely it looked.

### F-1 · CRITICAL · `verify.sh` may create environments and install packages over the network

`verify.sh:105` calls `ucos_ensure_venv`, which will `rm -rf` a drifted venv, run
`python -m venv`, and run `pip install -e ".[dev]"` — and, on a second failure,
`pip install --force-reinstall`.

Why it is a defect rather than a convenience: a verification command that can *repair its
own subject* cannot report on it. If the toolchain drifted, the run that was supposed to
detect the drift silently removes the evidence and reports green. It also makes the
canonical gate depend on network reachability, so an offline machine gets an
infrastructure failure reported as a verification failure. The directive states this
directly: verify SHALL NOT create environments, install packages, or perform network calls.

**Disposition:** Phase 5/6 — `ucos_ensure_venv` moves out of `verify.sh`; `bootstrap.sh`
remains its only caller (plus `doctor.sh --fix`).

### F-2 · CRITICAL · Repository root is resolved from `BASH_SOURCE`, and it has already failed

`ucos_repo_root()` (`scripts/ucos-env.sh:40-44`) derives the repo root from
`${BASH_SOURCE[0]}`. Sourcing the library from a shell that does not populate that array —
zsh, which is this machine's login shell — resolves the root to the **parent of the current
directory** instead.

Measured, reproduced during this discovery:

```
$ zsh -c 'source scripts/ucos-env.sh && ucos_ensure_venv'
ucos_repo_root:2: BASH_SOURCE[0]: parameter not set
== Installing pinned toolchain into /Users/bipin/Desktop/.ec1-venv
ERROR: file:///Users/bipin/Desktop does not appear to be a Python project
```

This is not hypothetical damage. A venv created by exactly this mispath is on disk now:

```
$ ls -la /Users/bipin/Desktop/.ec1-venv
drwxr-xr-x  6 bipin  staff  192 Aug  6 08:21 .      <- created 2026-08-06
drwxr-xr-x 12 bipin  staff  384 Aug  6 08:21 bin
```

A stray, unowned, unversioned virtual environment was written **outside the repository**
sixteen days before this assessment, and nothing in the repository knows it exists. This is
precisely the Phase 3 item-1 obligation ("running from correct repository") failing in
production.

**Disposition:** Phase 3 — the gate resolves the root via `git rev-parse --show-toplevel`
and refuses when the venv is not inside it.

### F-3 · HIGH · The `--cov unrecognized` failure is live on this machine

The classic failure the environment library was written to eliminate is still one PATH
lookup away, because the library only protects the paths that go through it:

```
$ /opt/homebrew/bin/pytest
ERROR: pytest: error: unrecognized arguments: --cov=engine.foundation ... --cov-fail-under=90
  inifile: /Users/bipin/Desktop/UCOS-CONSOLIDATION/pyproject.toml
ModuleNotFoundError: No module named 'pytest_cov'
```

Note what makes this dangerous rather than merely annoying: the global pytest **finds and
loads this repository's `pyproject.toml`**, so it is not running some unrelated
configuration — it is attempting this repository's certified gate under an interpreter that
cannot satisfy it. Anyone who types `pytest` in this directory gets this.

**Disposition:** Phase 3 item 4/5 — the gate asserts pytest resolves *inside the venv* and
that `pytest_cov` imports there, and names the global binary in the failure message.

### F-4 · MEDIUM · Toolchain executable duplicates are present in the venv

`.ec1-venv/bin` contains Finder-style duplicates:

```
coverage-3.12 2   coverage3 2   ec1-determinism 2   ec1-frozen-guard 2   pip 2   pip3 2   pip3.12 2
```

`ucos_deps_ok()` verifies that every executable a distribution's `RECORD` declares is
present and executable — a genuinely strong check, and the comment block explaining why
`Distribution.files` is insufficient is correct. But it is a check for **absence**, not for
**contamination**: an unexpected extra binary in the scripts directory is invisible to it.
These particular duplicates are inert, but the class is not: a stale `pytest 2` earlier in
resolution order is a silently different toolchain.

**Disposition:** Phase 3 item 8 — the gate reports unexpected executables in the scripts
directory as an advisory rather than blocking, since the current instances are harmless and
a blocking check would fail a healthy environment for a Finder artifact.

### F-5 · MEDIUM · No environment identity, and therefore no execution evidence

Nothing anywhere records *which* interpreter produced a certified result. `ucos_deps_ok`
answers "is the toolchain right?" as a boolean at one instant and discards the answer.
Certification therefore records what was verified but not what verified it, so two runs with
different interpreters are indistinguishable in the evidence.

**Disposition:** Phases 2, 4, 9 — an `ExecutionEnvironment` entity with a content identity,
a fingerprint cache, and per-run evidence carrying interpreter path, versions, dependency
fingerprint, repository commit and timestamp.

### F-6 · LOW · CI and local execution build different environments

`ec1-ci.yml` installs into the `actions/setup-python` interpreter, then invokes
`./verify.sh --full`, which builds `.ec1-venv` and runs every stage through *that*. CI
therefore installs the toolchain twice into two interpreters and verifies through the
second. This is not currently a correctness defect — both are 3.12 with the same pins — but
the first install is unused work and the two are free to drift.

**Disposition:** documented; not remediated in this cycle. Changing CI's install strategy is
outside the directive's scope and touching it would risk the certified pipeline for no
measured gain. Recorded as a standing observation.

### F-7 · LOW · `doctor.sh` checks versions but not identity

`doctor.sh` compares installed versions against the pins and reports a table. It never
checks that the interpreter it is reporting on is inside the repository, that pytest
resolves to the venv, or that no global tool shadows the canonical one — the three
conditions F-2 and F-3 actually failed on.

**Disposition:** Phase 3 — `doctor.sh` gains the gate as its identity section.

---

## §3 — WHAT IS ALREADY CORRECT (AND MUST NOT REGRESS)

Discovery is not only a defect list. These properties are already right and the
implementation is constrained to preserve them:

1. **Absolute-path tool invocation.** Every stage in `verify.sh` runs `"$PY" -m <tool>`, never
   a bare `pytest`/`ruff`/`coverage`. Phase 7's requirement is, for the pipeline itself,
   **already satisfied** — verified by reading all fourteen stage invocations.
2. **Pins have exactly one home.** `ucos_expected_deps()` parses `pyproject.toml [dev]`. No
   version literal is duplicated in any shell script.
3. **Executable-level dependency verification.** `ucos_deps_ok()` reads each distribution's
   `RECORD` directly rather than through `Distribution.files`, because the latter silently
   omits missing files — the exact condition being detected. This is subtle and correct.
4. **One ruff gate.** `ucos_ruff_gate()` is shared by `verify.sh` and the pre-commit hook,
   with NUL-delimited paths and an existence filter. Preserved untouched.
5. **Performance is not the problem.** Measured on the healthy path:

   | Operation | Runs | Measured |
   |---|---|---|
   | `ucos_ensure_venv` (healthy) | 3 | **0.15 s · 0.11 s · 0.11 s** |
   | `./verify.sh --explain` (full plan) | 1 | **0.66 s** |

   The directive's budget is < 5 s for the gate and < 1 min of verify overhead. The starting
   point is already inside both by two orders of magnitude. **The implementation's
   performance obligation is therefore to not lose this**, and Phase 4's fingerprint cache is
   justified by determinism and evidence rather than by a speed problem it does not have.

---

## §4 — DUPLICATE PATHS, LEAKAGE AND NON-DETERMINISM

| Class | Instance | Verdict |
|---|---|---|
| Duplicate execution path | `bootstrap.sh` / `doctor.sh --fix` / `verify.sh` all call `ucos_ensure_venv` | **Defect (F-1).** Three owners of one act; verify must not be one of them. |
| Duplicate execution path | CI installs the toolchain, then `verify.sh` installs it again | Observation (F-6). Wasteful, not incorrect. |
| Global tool leakage | `/opt/homebrew/bin/pytest` shadows the canonical pytest for any bare invocation | **Defect (F-3).** Not reachable through the pipeline; fully reachable by hand. |
| Global tool leakage | `python3` → 3.14.4 is what `ucos_find_interpreter` falls back to under `UCOS_ALLOW_PYTHON_MISMATCH=1` | Accepted: it is opt-in, warns, and is the documented escape hatch. |
| Missing dependency check | `pytest_cov` importability is never asserted — only its distribution version | **Defect.** Version metadata present and module unimportable is F-4's class of failure. |
| Non-determinism | `pip install` at verify time makes the run's result depend on index availability and resolution | **Defect (F-1).** Removed by Phase 5. |
| Non-determinism | `rm -rf "$UCOS_VENV_DIR"` on series drift, inside the gate | **Defect (F-1).** A gate that deletes its subject. |
| Slow operation | none found | The pipeline's cost is tests and governance gates, not environment work. |

---

## §5 — HIDDEN ASSUMPTIONS

Assumptions the current model makes without stating them:

- **A1.** That the library is sourced from `bash`. Violated by zsh; caused F-2.
- **A2.** That the repository root is the parent of `scripts/`. True, but derived from file
  layout rather than from git, so it cannot detect being run from a different checkout.
- **A3.** That a venv at the expected path *is* the canonical venv. Nothing checks that
  `sys.prefix` matches, so a symlink or a copied tree passes.
- **A4.** That version metadata implies a working module. `ucos_deps_ok` closes this for
  executables but not for importability.
- **A5.** That nobody invokes tools by hand. False by construction — F-3 is what happens.
- **A6.** That `.ec1-venv` is the only venv associated with this repository. False — see F-2.

---

## §6 — WHAT PHASES 2–10 MUST DELIVER

Derived from the findings above, not from the directive restated:

| Phase | Obligation | Closes |
|---|---|---|
| 2 | `ExecutionEnvironment` entity: identity · runtime · toolchain · dependencies · repository · validation | F-5, A3 |
| 3 | Fail-closed integrity gate, < 5 s, deterministic message naming expected vs detected | F-2, F-3, F-4, F-7, A1–A6 |
| 4 | `.ucos/environment-fingerprint.json` with declared invalidation triggers | F-5 |
| 5 | `verify.sh` loses the ability to create or install | F-1 |
| 6 | `verify.sh` Stage 0 becomes gate-only, overhead preserved under budget | F-1 |
| 7 | Direct tool resolution — already satisfied in the pipeline; must be **measured** so it stays true | §3.1 |
| 8 | Register the capability in the Master Implementation Plan | — |
| 9 | Per-run execution evidence bound to certification | F-5 |
| 10 | Executable regression proof: wrong-Python, missing-dependency, fresh-terminal | all |

**Scope boundary.** F-6 is documented and deliberately not remediated; the reasoning is in
its disposition. Everything else in §2 is closed by this cycle.
