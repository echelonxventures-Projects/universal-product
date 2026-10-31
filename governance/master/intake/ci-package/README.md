# CI installation package for the Master (prepared by amazon-44; not installed)

This package is prepared, not applied. Installing it is a repository change for `amazon-62`, the sole writer. It needs the owner's decision **LXM-DEC-000010**: the Master's repository location, its version and its authority.

## What it does

`ci-check.sh` runs on every pull request:
1. The committed Master equals a fresh generation.
2. `validate.py` passes.
3. The tool fixtures pass.
4. The configuration and code adapters do not get worse than their baselines. Findings only go down.
5. The working tree is clean.

Readiness (`readiness.py`) is computed as a report. It does not fail pull requests, because NO-GO is expected until release.

## To install (amazon-62, after LXM-DEC-000010)

1. Copy the Master directory to the decided location (recommended: `governance/master/`). That includes the canonical files, the tools, `out/`, `sources/`, `intake/`, the baselines and the configuration.
2. **Commit the three files `gate.json` points to**, and change its paths to repository-relative ones:
   - SRC-0002 and SRC-0003: the owner's original files, verbatim (the validator checks their SHA-256);
   - the earlier 128-row reconciliation matrix.

   They are owner material, so adding them to the repository is part of adopting the Master (LXM-DEC-000010).
3. Add the job in `lxm-job.yml` to `.github/workflows/ci.yml`. Pin `actions/checkout` the way the technology lock requires.
4. Register the new job with the technology governance (`scripts/technology.js check` validates CI against the lock). CI needs `python3`, which the runner image provides; declare it in the lock as a runner bootstrap tool.
5. Run `ci-check.sh` locally, then commit and push. Count CI only on the exact SHA.

## Rehearsal

`ci-check.sh` was rehearsed on a scratch clone of `39ed4d6` with the Master placed at `governance/master/`. The result is in the evidence of the freeze that contains this package.

## step-check.sh

The end-of-step check for the canonical writer (LXM-REQ-000237): exit 0 only when `git status` is clean. It only reads; it never commits, stashes, reverts or deletes, and never removes `.git/index.lock`. Run it after each step's commit: `intake/ci-package/step-check.sh <workspace>`.

## step_commit.py

The end-of-step commit and push (LXM-REQ-000237, owner direction SRC-0028), configured by `step-commit.json`, with fixtures in `test_step_commit.sh <scratch dir>`. It commits the step on its own branch and pushes it; it refuses, changing nothing, a protected or frozen branch, a force-push, a suspected secret, a present `.git/index.lock` (never deleted) and a detached HEAD.
