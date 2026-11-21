# UCOS Ω∞ — Verification Runbook

The operational runbook for verifying the repository. Pairs with
**ENVIRONMENT-SETUP.md** (which explains the canonical environment and root cause).

**Golden rule:** never `source .ec1-venv/bin/activate`. Run the canonical commands
below; they self-heal the environment and invoke every tool by absolute path.

---

## 1. Bootstrap (once per clone / after toolchain changes)

```bash
./bootstrap.sh            # create/repair .ec1-venv (Python 3.12) + pinned toolchain, then validate
./bootstrap.sh --verify   # also run full verification immediately
# or:  make bootstrap
```

Idempotent: safe to re-run. Recreates the venv only if it is missing or its Python
series drifted from 3.12.

---

## 2. Doctor (diagnose the environment)

```bash
./doctor.sh          # read-only report + pass/fail
./doctor.sh --fix    # report, then repair the venv/toolchain
# or:  make doctor
```

Sample healthy output:

```
COMPONENT      REQUIRED     INSTALLED    STATUS
python         3.12         3.12         OK
pytest         8.3.4        8.3.4        OK
pytest-cov     6.0.0        6.0.0        OK
coverage       7.15.2       7.15.2       OK
ruff           0.8.4        0.8.4        OK
✓ Doctor: ENVIRONMENT READY
```

Exit code is `0` only when the environment can reproduce repository verification;
otherwise non-zero, naming the exact defect (`DRIFT` / `MISSING`).

---

## 3. Verify (the canonical gate)

```bash
./verify.sh              # lint + tests/coverage + governance enforcement
./verify.sh --full       # also run the full registration + drift gate
./verify.sh --failfast   # stop at first failing stage
# or:  make verify   /   make verify-full
```

Stages, in order (each corresponds to a CI gate):

| Stage | Command (run via venv interpreter) | CI equivalent |
|-------|------------------------------------|---------------|
| 1. Lint | `python -m ruff check engine platform` | EC-1 CI → "Lint (ruff)" |
| 2. Tests + coverage | `python -m pytest` (drives `--cov …`, `--cov-fail-under=90`) | EC-1 CI → "Test + coverage gate" |
| 3. Coverage report | `python -m coverage report` | (coverage summary) |
| 4. Governance | `python 00-BOOK/tools/ukb.py enforce --pre` | Registration Gate → "Pre-registration enforcement" |
| 5. *(opt-in `--full`)* Registration + drift | `register.sh --guard` | Registration Gate → "Atomic Registration Transaction + drift gate" |

Ends with a summary and exits non-zero if any stage failed:

```
================ VERIFICATION SUMMARY ================
  PASS  ruff lint (engine + platform)
  PASS  pytest + coverage gate (--cov-fail-under=90)
  PASS  coverage report
  PASS  governance enforce --pre
======================================================
✓ VERIFICATION PASSED
```

> **Why stage 5 is opt-in:** `register.sh --guard` *regenerates* the synchronized
> registers (`00-BOOK/DATA|REGISTRIES|CONTROL-TOWER|PORTAL`) and then fails on drift.
> Because it mutates generated files, it is not part of the default local gate; use
> `--full` when you need full CI parity locally.

---

## 4. Focused commands

```bash
make lint     # ruff only (self-heals env first)
make test     # pytest + coverage gate only (self-heals env first)
```

---

## 5. Reproducibility guarantee

A brand-new terminal — no activated venv, with `ruff`/`coverage` **not** on `PATH`
and even a shadowing global `pytest` present — reproduces verification:

```bash
env -i HOME="$HOME" PATH="/opt/homebrew/bin:/usr/bin:/bin" /bin/zsh -c '
  cd <repo> && ./doctor.sh && ./verify.sh'
# → Doctor: ENVIRONMENT READY … VERIFICATION PASSED   (exit 0)
```

This holds because the scripts use `.ec1-venv/bin/python -m …` by absolute path and
never rely on shell activation or `PATH` ordering.

---

## 6. Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `pytest: error: unrecognized arguments: --cov…` | you ran a **global** `pytest` without `pytest-cov` | use `./verify.sh` / `make test` (never bare `pytest`) |
| `ruff: command not found` / `coverage: command not found` | tools only exist inside the venv; no venv activated | use the canonical commands — they don't need activation |
| Doctor shows `python … DRIFT` | `.ec1-venv` built with the wrong Python series | `./doctor.sh --fix` or `./bootstrap.sh` (auto-recreates at 3.12) |
| `No Python 3.12 interpreter found` | Python 3.12 not installed | `brew install python@3.12`, or set `UCOS_PYTHON=/path/to/python3.12` |
| Doctor shows a tool `MISSING`/`DRIFT` | toolchain not installed / drifted | `./doctor.sh --fix` (runs `pip install -e ".[dev]"`) |
| Need to start clean | corrupt venv | `make clean-venv && ./bootstrap.sh` |
| CI parity for registration | default verify skips the mutating registration gate | `./verify.sh --full` |

If a problem persists after `make clean-venv && ./bootstrap.sh`, run `./doctor.sh`
and share its output — it names the exact failing component.
