# Implementation report: context continuity system (TASK-CTX-0001)

Session 2026-10-22 · branch `claude/modest-babbage-kyejdn` · start HEAD `441d772` (clean tree). The end HEAD is the commit that adds this file.

This report is evidence, written once and not regenerated. Live state comes from `npm run context:verify` and the generated views in `PROJECT-CONTEXT/`. The machine-readable companions in this folder are `coverage.json`, `hygiene.json` and `restore-check.json`.

## 1. Baseline (before any change)

| Check | Result |
|---|---|
| `git status` | clean, on `claude/modest-babbage-kyejdn` @ `441d772` |
| `npm run registry` | exit 0. 12 documents, 2919 universes, 32 220 concept rows, 15/15 gate checks, seal verified |
| `npm test` (full chain) | exit 0, every suite green (e.g. smoke 760, security 158), about 23 minutes |

Existing mechanisms found and reused, not replaced:

- `_registry/*.json` with projection, audit and gate. This is the "registry is truth, documents are projections" pattern.
- `lib/canonical.js`, the sealed compile.
- `.workbuddy-ai/memory/MEMORY.md`, a 111 KB narrative agent ledger.
- `_superseded/`, the provenance originals.
- `npm test` and the CI workflow.

There was no `AGENTS.md` or `CLAUDE.md`.

## 2. Architecture and ownership decisions

Three layers, one owner each:

- **A. Evidence.** `knowledge/sources.json` is the manifest. Bytes live in the git object store (pinned by blob id and sha256), or in the write-once private store `CONTEXT_ARCHIVE_DIR`, which is never committed.
- **B. Knowledge.** `knowledge/*.json` holds requirements, decisions, constraints, artifacts, issues, tasks and context specs. All are schema-validated, and lifecycle values come from a registry. The 93 UCOS artifacts are **imported read-only from `_registry/manifest.json`**, not copied.
- **C. Working context.** Generated views `00`–`10`, `contexts/` (packs) and `task-packs/` are deterministic, fingerprinted and drift-checked.

The design decisions are recorded as **proposed** (DEC-CTX-*). The owner has not approved them yet: see TASK-CTX-0002 and ISS-CTX-DECISIONS-UNAPPROVED. Each decision's rationale and rejected alternatives are in `03-DECISION-REGISTER.md`. The most consequential one: **continuity knowledge does not go into `_registry/`**. Those files are inputs to the sealed constitutional compile, so adding operational records there would change the seal.

## 3. Files

- **Created:**
  - `AGENTS.md` and `CLAUDE.md` (the entry points)
  - `lib/context/{util,schema,store,graph,packs,archive,coverage,hygiene,views,protocol,index}.js`
  - `scripts/context.js` (the CLI)
  - `test/context.js` (148 assertions)
  - `PROJECT-CONTEXT/` (`schemas/` with 6 files, `knowledge/` with 10, plus the generated views, packs, task packs and these reports)
- **Modified:**
  - `package.json`: 14 `context:*` scripts, and `test/context.js` plus `node --check scripts/context.js` added to `npm test`
  - `.github/workflows/ci.yml`: full-history checkout, and a continuity step running verify and restore-check before the suite
  - `.gitignore`: `.context-archive/`
- **Retired or deleted:** none. Product runtime, `_registry/`, and the constitutional documents are untouched.

## 4. Commands actually run and observed results

| Command | Observed |
|---|---|
| `node test/context.js` | **148/148 passed**, about 17 s |
| `npm run context:verify` | passed. 0 errors. Warnings and notes are listed, never folded into the pass |
| `npm run context:restore-check` | 22 restored and re-verified in an isolated temp dir, 2 skipped (not preserved), 0 failed, live repository untouched |
| `npm run context:coverage` / `context:hygiene` | see §5 and §7 |
| `node _registry/audit.js` | ALL CONSTITUTIONAL CHECKS PASSED (after the change) |
| `npm run registry` | compile, gate (15 checks) and seal verified (after the change) |
| `npm test` (full chain, with the change) | recorded in the TASK-CTX-0001 handoff with its observed exit code |

During development the verifier caught three of my own defects, all fixed before this report:

- Pack membership read the wrong object, so packs were empty.
- A pack's mandatory block was over budget. Fixed by splitting it into linked design and requirements packs, and by not re-including knowledge a prerequisite already carries.
- A shallow-clone check masked the "private store unavailable" warning.

## 5. Coverage (numerator ÷ denominator, from `coverage.json`)

| Metric | Value | Note |
|---|---|---|
| source inventory preserved | 22/24 (91.67%) | 2 conversation sources are inaccessible or not retained. They are **not** counted as preserved |
| checksum verification | 22/22 | archived bytes re-hash to the manifest |
| segment accounting | 5983/6006 (99.62%) | mostly corpora classified "preserved" (compiled by `lib/canonical.js` with line provenance). 23 segments remain **unprocessed** |
| segment representation | 16/6006 (0.27%) | segments actually cited by knowledge records. This low figure is the honest one: the corpora's knowledge is owned by the canonical compile, not duplicated here |
| requirement → source / implementation / test | 14/14 each | |
| decision → source or newly-proposed | 9/9 | |
| context dependency completeness / freshness | 6/6 each | |
| handoff completeness | 0/0 before the closing handoff | |
| broken links · orphans · dangling citations | 0 · 0 · 0 | |
| unresolved conflicts | 1 | ISS-RUNTIME-DEPENDENCY-CLAIM. Low severity, blocks nothing |

## 6. Packs (6, all status ok at the default 24 000 B budget)

| Pack | Size |
|---|---|
| CTX-BOOTSTRAP | 8.8 KB |
| CTX-GOVERNANCE | 10.7 KB |
| CTX-CONTINUITY-DESIGN | 13.4 KB |
| CTX-CONTINUITY-SYSTEM | 22.0 KB |
| CTX-EVIDENCE-ARCHIVE | 18.6 KB |
| CTX-PLATFORM-QUALITY | 8.9 KB |

No pack is stale. Token figures are estimates at 3 B/token.

Graph: 367 typed edges over 209 nodes. Edges are derived from record fields, and there are 0 broken references and 0 cycles.

## 7. Hygiene findings (nothing deleted or merged)

- **14 near-duplicate pairs:**
  - 3 are the `_superseded/` originals against their successors. These are expected and already governed.
  - 11 are a new finding: constitutions share a content block with a core-domain artifact in `_registry/content-map.json`. Recorded as **ISS-CONTENT-MAP-SHARED-KEYS**, for the owner to decide.
- 0 exact duplicates, 0 broken local links. 6 files are over 60 KB (the corpora and MEMORY.md); none of them is on the active read path.

## 8. Fresh-agent recovery (test §G)

The test uses a disposable copy of the repository and no conversation history. Starting from `AGENTS.md` alone, the agent:

- finds the master index and the task, and passes the gate at 24 KB;
- loads only the listed files;
- recovers the governing constraints, task state and next action, the decisions and their *proposed* status, the open issues, the verification commands, the verified-versus-unverified facts, and the exclusions;
- writes a valid handoff, after which the repository still verifies.

Under failure conditions:

- A 4 KB agent is **blocked** (exit 2, over-budget) rather than handed partial context.
- An unbuilt knowledge change is blocked as stale.

Other simulated failures, each detected (§C and §E): corrupted, missing, stale, conflicting and oversized packs, archive tamper, duplicate ids, broken references, cycles, and historical evidence used as authority.

## 9. Known limitations and inaccessible sources

- The owner's 2026-10-22 prompt is **not archived**. REQ-CTX-* paraphrase it by section (ISS-MASTER-PROMPT-NOT-ARCHIVED, TASK-CTX-0003).
- The conversations behind the sessions of 2026-09-17 → 2026-10-07 are **inaccessible**. Only MEMORY.md's agent-written summaries survive (ISS-PRIOR-CONVERSATIONS-INACCESSIBLE).
- Representation of the corpora in continuity knowledge is deliberately thin. Their owner is the canonical compile.
- The assimilation receipt proves what was loaded, not that it was understood.
- Hygiene detects similarity, not meaning. Consolidation always needs a human-approved plan.
- In a shallow clone, git-history and superseded-version evidence can only produce a warning. CI uses `fetch-depth: 0`.
- Changing a file-hashed artifact (for example `lib/context/*.js`, `AGENTS.md`) stales its packs until `npm run context:build` runs. This is intended.

## 10. Pre-existing issues, tracked separately (not caused by this work)

- ISS-CANONICAL-INPUT-MISNAMED / TASK-REG-0001: the seal hashes a non-existent file name.
- ISS-CONTENT-MAP-SHARED-KEYS
- ISS-REVIEW-FINDINGS-UNRECONCILED / TASK-SEC-0001
- ISS-PG-CUTOVER-STATUS
- ISS-RUNTIME-DEPENDENCY-CLAIM

## 11. Next actions

1. **TASK-CTX-0002.** The owner reviews DEC-CTX-* in `03-DECISION-REGISTER.md`.
2. **TASK-CTX-0003.** Export and import the session transcript into an access-controlled `CONTEXT_ARCHIVE_DIR`.
3. **TASK-REG-0001**, then TASK-SEC-0001.

## 12. Corrections recorded after this report (TASK-CTX-0004, same day)

The body of this report is kept as written. Two of its statements were wrong.

- **§5 and §10: "ISS-RUNTIME-DEPENDENCY-CLAIM" was not a real conflict.** `lib/queue.js:51` requires `bull` and `lib/metrics.js:121` requires `prom-client`, both lazily, exactly as README S0001 says. The original observation ("no file requires them") was this agent's error: the grep output was truncated by `| head`. The issue is now resolved, and fact F-005 is corrected in place, with the error noted.
- **§10: "ISS-REVIEW-FINDINGS-UNRECONCILED" overstated the gap.** REVIEW.md S0001 already maps each finding to its fix location. What remains open is independent per-finding verification, and the issue's severity is now medium.

Also from reading the 23 previously unprocessed segments:

- **ISS-PG-CUTOVER-STATUS** is resolved by code inspection.
- **ISS-IMPLEMENTATION-MAP-STALE** is newly opened.
- **Coverage now separates segments read individually (43/6006) from those covered only by a source-wide rule (5963/6006).**

## 13. Correction: git-history archive (TASK-CTX-0005)

- **§5 counted SRC-GIT-HISTORY among the "22/22" verified checksums. That only held in the capturing shallow clone.** The record came from a legacy serializer that ran in a shallow clone with boundary `3577ace`, which yields 61 commits. In any full clone the ancestry of `441d772` is 79 commits, so the record failed verification there.
- **The record keeps its original identity and is now `not-retained`.** It is never reported as verified.
- **Its exact bytes were recovered and are preserved as SRC-GIT-HISTORY-LEGACY-RECOVERED.** The SHA-256 matches the recorded one.
- **The complete history is captured canonically as SRC-GIT-HISTORY-441D772-V1** (`ctx-git-history/1`, 79 commits).
