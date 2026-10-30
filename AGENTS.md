# AGENTS.md — start here

This repository keeps its working knowledge in **`PROJECT-CONTEXT/`**, so any agent (any model, client or context size) can continue the work without the previous conversation. You need a shell with Node ≥ 22.13 and git. No other tool, command or client feature is assumed.

## The protocol (every session)

1. **Know where you are.** `git status` and `git log -1`. Never reset, clean or overwrite uncommitted changes you did not make.
2. **Check the context is sound.** `npm run context:verify`. Errors mean the knowledge or generated packs are broken or stale: fix them first (usually `npm run context:build`). Warnings are listed so you can read them; they are not success.
3. **Read the master index.** `PROJECT-CONTEXT/00-MASTER-INDEX.md`, then the bootstrap pack `PROJECT-CONTEXT/contexts/CTX-BOOTSTRAP.md` (mandatory rules + current state).
4. **Resolve your task.** Find it in the master index's task table and open `PROJECT-CONTEXT/task-packs/<TASK-ID>.md`. If your work has no task, add one to `PROJECT-CONTEXT/knowledge/tasks.json` first.
5. **Pass the gate.** `npm run context:assimilate -- <TASK-ID> --agent <your-name> --budget <bytes> --write`. Use your real budget (a small model might use 8000). `BLOCKED` means stop and fix what it lists. It writes a receipt to `PROJECT-CONTEXT/receipts/`.
6. **Load only what the gate lists**, in its reading order. Load supplementary parts and source evidence only when you need them.
7. **Follow canonical owners.** A pack is a summary. Every item names its `Owner:`, and the owner wins. Superseded and historical material is evidence, never authority.
8. **Do bounded work** within the task's scope and exclusions. Change knowledge by editing `PROJECT-CONTEXT/knowledge/*.json`, then `npm run context:build`. Never hand-edit generated files (views `00`–`10`, `contexts/`, `task-packs/`).
9. **Verify.** Run the task's verification commands plus `npm run context:verify`. Report only what you observed. A test passed only if you ran it and saw it pass.
10. **Hand off.** Write a JSON file listing objective, completed work with evidence, what is not done, unverified claims, commands and tests with results, and the exact next action. Then run `npm run context:handoff -- <TASK-ID> --from <file>`. It rejects claims without evidence.

## Rules that always apply

These are enforced by `context:verify` and listed in `PROJECT-CONTEXT/01-PROJECT-CONSTITUTION.md`:

- **Knowledge Once.** One owner per concept. **Projection Law:** generated documents are never edited by hand. That covers `_registry/` → `00-constitutions/`…`13-implementation/`, and `PROJECT-CONTEXT/knowledge/` → its views and packs.
- No secrets in the repository or in derived context. Private conversation exports go to `CONTEXT_ARCHIVE_DIR` via `npm run context:import`, never into git.
- Nothing is deleted to tidy up. Retire knowledge through `npm run context:transition`, which needs approval for destructive steps, and merge it through `npm run context:consolidate`.
- No commit, push, merge, release or deployment without the owner's authorisation.

## Useful commands

`npm run context:query -- prerequisites <ID>` · `affected-by <ID>` · `tests-for <REQ>` · `decisions-for-task <TASK>` · `npm run context:coverage` · `npm run context:hygiene` · `npm run context:restore-check` · `node scripts/context.js help`

The repository's own checks are still the law for product code: `npm test` (full suite, ~18 min), `npm run registry`, `node _registry/audit.js`.
