# Governed Python for the Master tooling (prepared, not applied)

SRC-0011 and SRC-0015 say technologies are declared by the capabilities they must provide, and the governance resolves a verified release. The Master's tools currently assume an undeclared `python3`.

- **What the tools need,** measured from their source:
  - `shutil.copytree(dirs_exist_ok=…)`, available since Python 3.8;
  - `date.fromisoformat`, available since 3.7.

  The floor is therefore derived as 3.8 from those capabilities. Nobody writes the number.
- **The change (for `amazon-62`, after LXM-DEC-000010):**
  1. Merge `technology-additions.json` into `lib/seed/technology.json`.
  2. Declare the Python releases under `python-release-declaration`, with their provenance. A python.org discovery adapter is new executable code and a later step.
  3. Regenerate `technology.lock.json` (`npm run technology:lock`).
  4. Have the CI `master` job (`intake/ci-package/lxm-job.yml`) install the runtime the lock names for `ci.master`, as the Node lanes already do.
- **Not verified here:** applying this needs the repository's technology tooling and a declared Python release. This prepares the declaration only.
