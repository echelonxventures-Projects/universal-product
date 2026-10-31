# Master import (not yet installed)

The LXM Master, frozen and verified on 2026-10-31 (checkpoint CP25), imported once by owner decision LXM-DEC-000017 on its own branch from the candidate `39ed4d6`. It is the starting point for LXM-DEC-000010 (the Master at `governance/master/`, version 1.0.0), which amazon-62 installs.

- **Self-contained:** the owner's sources SRC-0002 and SRC-0003 and the earlier 128-row matrix are in `external/`; `gate.json` names them relative to this folder (`root_relative`).
- **Only what is needed:** files that verification, replay, readiness and the install need. The rest (conversation excerpts, test logs, regenerable reports, set-aside copies, refused attempts, generated proposals) stays in the owner's preservation copy; `OMITTED.sha256` lists each with its SHA-256.
- **Verified here, in this tree:** `intake/ci-package/ci-check.sh governance/master .` passes, including the clean-tree check.
- **Not done, by design:** the CI job is not yet wired into the workflows; nothing outside this folder changed; the integration branch and PR #6 are untouched.

Work package for amazon-62: `intake/handover/AMAZON-62-WORK-PACKAGE-2026-10-31.md`. Every step ends with `intake/ci-package/step_commit.py` (LXM-REQ-000237).
