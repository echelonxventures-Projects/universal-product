# Work package for amazon-62 (sole repository writer), 2026-10-31

**From:** the Master session (amazon-44, now addressed as amazon-4f). **Authorized by** the owner, Bipin Kumar, on 2026-10-31: SRC-0026 §0.5 ("Yes, send it to amazon-62"), under the adopted decisions LXM-DEC-000009, 000010, 000011, 000012 and 000016. Owner's words: `intake/decisions/OWNER-APPROVAL-2026-10-31.txt` and `OWNER-APPROVAL-2026-10-31b.txt`.

**Candidate:** integration head `39ed4d64acc49513af05c647faa2d03dabd5f38e` (PR #6, draft). **Master:** `/private/tmp/claude-502/-Users-bipin-Desktop-Folders-Container-Desktop-10-Sept-26-Amazon/1a37ba67-4453-45e8-be27-77443fd1a14f/scratchpad/lxm/` (durable copy: `~/LUXORA-preservation/2026-10-31-lxm-master-candidate/lxm-latest/`).

**Caution:** the iCloud working tree (`feat/production-readiness`) has uncommitted changes and new files (coupons, gift cards, vouchers, grants, group buy). They are not on the candidate. Decide with the owner whether they belong to this release before you start. Work only in the approved workspace outside iCloud (LXM-REQ-000002).

Nothing here authorizes a merge, a deploy or a change of the release decision. Release stays NO-GO until `readiness.py` computes GO and the owner adopts LXM-DEC-000013.

## Clean working tree after each step (LXM-REQ-000237, owner directive SRC-0027)

- **Before step 1:** `intake/ci-package/step-check.sh <workspace>` must print `clean`. If it doesn't, stop and report. Never revert, stash or discard to get there (LXM-REQ-000030).
- **End of every step, automated (owner, SRC-0028):** tests green, then `python3 -I intake/ci-package/step_commit.py <workspace> --message "<step>: <what it closes>"`. It commits the step on its own branch, pushes it, and prints `clean and pushed at <sha>` only when the tree is clean and the remote head equals the local one. It refuses a protected or frozen branch (the integration branch while its acceptance CI runs), a force-push, a suspected secret and a present index lock, and in each case changes nothing. Its settings are in `step-commit.json`; its fixtures in `test_step_commit.sh`. Send the printed line with the step's evidence. A step without it is not finished.
- **CI** checks the same at the end of every run (`ci-check.sh` step 5).
- The iCloud checkout is not your workspace and is not made clean: its uncommitted Phase 1 changes are preserved as they are (LXM-REQ-000217).

## Order of work (each step: tests green, commit and push, clean tree, then the next)

| # | Work | Closes | Inputs |
|---|---|---|---|
| 1 | Install the Master at `governance/master/` as version 1.0.0 (an import is already pushed as branch `governance/lxm-master-2026-10-31`, from `39ed4d6`, by owner decision LXM-DEC-000017: start from it, point `gate.json` at the repository copies of the three external sources), with SRC-0002, SRC-0003 and the earlier 128-row matrix (LXM-DEC-000010). Wire the CI job. | R7; LXM-REQ-000191 | `intake/ci-package/` (README, `ci-check.sh`, `lxm-job.yml`) |
| 2 | Apply the runtime settings-trace patch, then regenerate `TECHNOLOGY_INVENTORY.generated.md` (the patch makes it stale). | runtime evidence for LXM-REQ-000198 | `intake/patches/settings-trace.patch` |
| 3 | Node lane (LXM-DEC-000011, option B): the full suite on Node 22.22.2 or later, the dev tooling re-resolved to fixed versions; production floor stays 22.13.0 with a runtime-only lane; a host-install security floor in the technology lock. Add the Python governance entries. | LXM-REQ-000048 | `intake/patches/python-governance/` |
| 4 | Release register: write **Bipin Kumar** in the Owner column of gates 2–9, 11–14 and 16–19 (SRC-0026 §0.4). Change no status. | 16 "unassigned" resolvers | `PRODUCTION_READINESS.md` |
| 5 | Money policy (LXM-DEC-000012): keep every money-moving domain outside the payment spine disabled (configuration); build MD-3 option B, pro-rata tax on partial refunds (`tax_minor` on `refunds`, the allocation in `lib/refunds.js`, the tax report, tests); record MD-1 to MD-5 in the sign-off table of `docs/money-decision-packet.md` as decided on 2026-10-31. Each launch market's rounding rule and tax basis still comes from the owner. | gate 4 (engineering part) | `docs/money-decision-packet.md` |
| 6 | Hard-coding: 113 embedded, 9 fallback and 25 literal code sites; declare the 44 undeclared settings. | configuration blockers (LXM-REQ-000199, 000074) | `config-findings-39ed4d6.md` |
| 7 | Duplicates (8), unowned modules (11), the unexecuted script (1), the untested module (1). | code blockers (LXM-REQ-000203, 000136, 000081) | `code-findings-39ed4d6.md` |
| 7b | Open-ended environments (LXM-REQ-000238): the order of work in `intake/decisions/ENVIRONMENT-MODEL-2026-10-31.md` — declare the settings, replace the 12 `NODE_ENV` branches, move provider modes into provider settings, the registry into the kernel, readiness per environment. | code blockers `environment-branch` (12), `environment-name` (32) | `ENVIRONMENT-MODEL-2026-10-31.md`, `code-findings-39ed4d6.md` |
| 8 | LXM-REQ-000086: record rate source, rate timestamp and spread on every currency conversion. | trace gap | `trace.txt` |
| 9 | Kernel migration: the 290 entity types stored outside the kernel derive through registry, entity, context, temporal and relationship. Do it domain by domain, and ratchet the baseline down each time. | LXM-REQ-000232 | `code-findings-39ed4d6.md` (outside-kernel) |
| 10 | Once the candidate is final: get two distinct green CI runs on its exact SHA by closing and reopening PR #6, with no commit made only to trigger CI (LXM-DEC-000009). | gate 1; K2 | — |

After each step, send the new head SHA, the `step-check.sh` line, its CI run ID and the test results, so the Master recomputes readiness (`readiness.py`) and records the evidence through the gate.

## What remains with the owner (not for amazon-62)

The 16 external gates now owned by Bipin Kumar (payment provider, staging, deployment target, TLS/domain/secrets, backups, DR, alerts, on-call, performance, privacy). Gate 20 and LXM-DEC-000013, release authorization, only after gates 1–19 pass.
