# Context continuity system

A repository-native, model-agnostic system that lets an agent of any capability or context-window size find the context a task needs, prove it loaded it, do bounded work, and hand off to a later session through the repository alone. Agents start at [`AGENTS.md`](AGENTS.md). This document is for the people and agents who maintain the system.

Status: **operational**. CI-gated (`node _registry/context.js check`) and covered by `test/context.js` (85 assertions). The open items are in the [gap register](#gap-register).

---

## 1. Architecture and canonical ownership

The repository already has one rule for knowledge: **truth lives in `_registry/`, and everything else is a projection** (Laws 002/003, `README.md`). The context system follows that rule and adds no second registry of what already exists.

| Layer | Path | Kind | Owner | Notes |
|---|---|---|---|---|
| Authored context registry | `_registry/context.json` | canonical | repository owner | Classes, lifecycles, authority levels, edge types, units, sequences, constraints (verbatim quotes), decisions, conflicts, supersessions, hygiene thresholds. **The only authored input.** |
| Handoff records | `_registry/handoffs/<TASK>/<NNNN>.json` | agent note, append-only | recording session | Hash-chained. Tool-verified facts are kept separate from agent assertions. |
| Engine | `_registry/context-graph.js`, `context-packs.js`, `context-hygiene.js`, `context.js` | implementation | platform engineering | Same location and conventions as `project.js` / `compile.js` / `audit.js`. |
| Generated context | `_context/manifest.json`, `_context/MAP.md`, `_context/packs/*.md` | derived, committed | regenerated | Committed like the 93 projected artifacts; CI fails when it is stale (DEC-CTX-002). |
| Agent entry point | `AGENTS.md` | repository governance | repository owner | Vendor-neutral file name; the protocol is commands, not a model feature. |

**What it reuses instead of redefining:**
- **Artifact identity.** UCOS artifacts keep their `UCOS-XXX-NNNNNN` ids and are validated against `_registry/manifest.json`. Every other file is `file:<path>`. Authored nodes use their own ids (`LAW-002`, `DEC-CTX-003`, `CNF-001`).
- **The registry → document pipeline.** The edges come from `project.js`'s own `load()` calls and from `content-map.json` routes.
- **The runtime compile.** The edges come from the `INPUT_FILES` / `REGISTRY_INPUTS` / `COMPILER_INPUTS` arrays in `lib/canonical.js`. The sealed `canonical.lxr` is modelled as a virtual derived node, because it is keyed per deployment and never committed.
- **Code dependencies.** The `require()` graph, extracted through a lexical mask so a require inside a string or comment is never mistaken for a dependency.
- **Verification.** The `npm test` script in `package.json`: which suites CI actually runs, and which modules each one exercises.

No file is listed by hand in the engine. Discovery is `git ls-files -co --exclude-standard`, minus `exclude[]`, so gitignored secrets and build output never register. The first class whose glob matches a file claims it. A file that no class claims is an error.

### Source-of-truth conflicts found during assimilation (recorded, not resolved)

These were reproduced on 2026-10-22. Each is a `conflicts[]` record and a node in the graph, appears in every bootstrap, and is ranked in the hygiene plan.

| Id | Finding | Decision needed |
|---|---|---|
| CNF-001 | `node _registry/project.js` rewrites all 93 committed artifacts (notice text in all 93; `Owns:` changes in two). Nothing gates it. Hygiene measures it on every run (`derivedDrift = 93`). | Re-project in its own reviewed commit, or revert the generator text. |
| CNF-002 | `lib/canonical.js` hashes `UCOS-Zero-Hardcoding-Constitution.md`, which does not exist. The parser reads `UCRS-…`, so that corpus is outside the seal's drift detection. Likely the **G1 seal fix**, kept separate as instructed. | Approve the one-line fix as its own change, then delete the acknowledgement. |
| CNF-003 | Three documents marked SUPERSEDED ("do not derive implementations from this file") are live compile inputs. | Whether superseded documents may stay declaration sources. |
| CNF-004 | The text of Laws 001–005 exists only in a SUPERSEDED document. The registry has no law entries. | Whether to add laws to the registry through governance. |
| CNF-005 | The README says `_registry/*.json` is the SSOT; `canonical.js` says the sealed `.lxr` is "THE runtime source of truth". No precedence is declared. | Adopt "both are projections of the same inputs" as a decision. |

**Authorization.** The capability is authorized by existing governance (DEC-CTX-001). It is additive registry data plus a projection: it introduces no primitive (the only change `primitives.json` reserves for constitutional amendment) and redefines no concept. The decisions that change authority (CNF-001…005) are left to the owner.

---

## 2. Schemas

### 2.1 `_registry/context.json` (`ucos.context.spec.v1`)

| Field | Purpose |
|---|---|
| `lifecycles[]` | The seven lifecycle states (§15.2): `active-canonical`, `active-operational`, `derived`, `consolidatable`, `superseded`, `historical-evidence`, `retired`. |
| `authorityLevels[]` | Ordered precedence, highest first (DEC-CTX-003). |
| `edgeTypes[]` | `{id, prereq: "to"\|"from"\|null, closure: "mandatory"\|"relevant"\|null, acyclic}`. Gives each edge's direction a meaning, so traversal never treats relationships as interchangeable. |
| `classes[]` | `{id, match[], except[], kind, authority, lifecycle, owner, idFrom?, generatedBy?}`. The first match wins. |
| `statusMarkers[]` | A content marker that overrides lifecycle (`# [SUPERSEDED` → `superseded`). |
| `extractors[]` | Which canonical sources to read relationships from (`js-require`, `ucos-projection`, `js-array-inputs`, `npm-test-script`, `handoff-records`). |
| `edges[]`, `edgeRules[]` | Authored typed edges, plus class-to-class rules (e.g. CON artifacts constrain every other specification). |
| `constraints[]` | `{id, source, anchor, quote, appliesTo}`. The quote must stay verbatim in its source, or validation fails (`CONSTRAINT_QUOTE_MISSING`). |
| `decisions[]`, `conflicts[]` | Authored nodes. A conflict may `acknowledge` a specific finding, which keeps it visible as a warning without blocking. |
| `supersessions[]` | `{artifact, successors, effective, reason, disposition, referenceMigration, retention}`. Required for every superseded artifact (§15.6). |
| `units[]` | Pack groupings: `{id, title, purpose, scope, tags, prerequisites, select, optional}`. `forEach: "ucos-categories"` expands a template over the UCOS manifest. |
| `sequences[]` | Authored (`units: [globs]`) or computed (`dependency-first`, `by-tag`). |
| `budgets` | `packChars` (default 12000 ≈ 3k tokens), `reserveChars`, `bootstrapChars`. |
| `hygiene` | Duplication parameters, `derivedChecks[]`, ratchet `thresholds`, `ceilings`. |
| `security` | `denyPaths[]` (never registrable) and `secretPatterns[]` (never in a pack or handoff). |

**Selectors** (`select`, `appliesTo`, `governs`, `between`, `successors`) match a node by `class`, `notClass`, `category`, `notCategory`, `ids`, `pathGlob`, `edgeFrom: {node, type}`, or a bare id or path. They never match by position.

### 2.2 Edge types

| Type | Direction (prerequisite → dependent) | Closure | Acyclic |
|---|---|---|---|
| requires | to → from | mandatory | yes |
| must-read-before | from → to | mandatory | yes |
| defines | from → to | mandatory | yes |
| implements | to (spec) → from (code) | mandatory | yes |
| constrains | from (law/decision) → to | mandatory | yes |
| derived-from | to (source) → from (derived) | mandatory | yes |
| continues / hands-off-to | earlier record → later record | mandatory | yes |
| depends-on | to → from (runtime require) | relevant | no — CommonJS cycles collapse |
| verified-by | — (impact follows it one hop) | — | no |
| supersedes | — (successor → old) | — | yes |
| conflicts-with | — (conflict → subject) | — | no |

Traversal is iterative with a visited set. Ordering collapses strongly connected components (Tarjan) and breaks ties by primary-sequence position and then by id, so it is deterministic and cannot loop. Cycles over acyclic types are `ILLEGAL_CYCLE` unless listed in `allowedCycles[]`.

### 2.3 Pack (`ucos.context.pack.v1`)

Each pack carries:
- an HTML generated-file banner;
- a title;
- a JSON header (`id`, `unit`, `part`/`parts`, member counts, `sourcesDigest`);
- the not-authority notice, plus a HISTORICAL banner when relevant;
- purpose, scope and domains;
- a **position table** (previous/next in every sequence it belongs to);
- **prerequisite packs**, declared and derived from mandatory edges;
- one entry per artifact: path, class, authority, lifecycle, owner, digest, size, extracted navigational summary, outgoing edges (with the **digest of each prerequisite**, so upstream changes invalidate the pack), incoming-edge counts, and the supersession record;
- **completeness** (members of the unit, every pack of the unit);
- **continue** (next pack, or an explicit `END OF SEQUENCE`).

Constraints are rendered as verbatim block quotes with their source and digest. Units larger than the budget split at artifact boundaries. An artifact larger than a pack splits at line boundaries with `(continued: chunk k of n)` headings. A single line that cannot fit is emitted whole and reported (`OVERSIZE_LINE`/`OVERSIZE_PACK`); nothing is ever truncated.

### 2.4 Manifest (`_context/manifest.json`, `ucos.context.manifest.v1`)

Contents:
- `inputsDigest` over every node's (id, digest);
- counts and the budget;
- `sequences[]`: ordered pack ids, `count`, `end: "END:<id>"`, and a digest of the order;
- `units[]` with packs and derived prerequisites;
- `packs[]` with file, chars, digest, sourcesDigest and members;
- every node (id, path, class, authority, lifecycle, kind, owner, digest, unit);
- every edge `[from, type, to, origin]`;
- non-blocking findings.

It is deterministic. It contains no timestamps or commit ids, because those would change on every commit; the commit that last validated the context is `git log -1 -- _context/manifest.json`, which `bootstrap` reports.

### 2.5 Handoff record (`ucos.context.handoff.v1`)

```text
taskId, seq, previousDigest (sha256 of record seq-1; null for the first), status (in-progress|interrupted|blocked|completed),
objective, authority {instruction, governedBy[]},
verified {revisions {start, end, branch}, changedFiles[{path,status,state}], commands[{cmd, exitCode, ms, outputSha256, outputTail}], contextManifestDigest},   ← produced by the tool
asserted {decisions[], results[], failures[], limitations[], risks[], unresolved[], notDone[]},                                             ← the agent's claims
context {packsUsed[], sourcesUsed[]}, resume {prerequisites[], nextAction}, references {pullRequest}
```

Records are append-only. Editing or deleting a past record breaks the chain (`HANDOFF_INVALID`), and `resume` refuses. Only the latest record of an unfinished task is `active-operational`; every other record is `historical-evidence`.

### 2.6 Assimilation receipt (`ucos.context.receipt.v1`, `bootstrap --json`)

Fields: `status` (READY | ASSIMILATED | REFUSE), `reasons[]`, repository (sanitized remote, branch, commit, dirty count, last context commit), registry (fresh, error/warning counts, inputs digest), task, the staged plan (pack id, file, chars, digest), governing constraints and decisions, open and task-touching conflicts, historical items in the closure, sources to open on demand, and loaded / not loaded.

Exit code `2` means REFUSE.

---

## 3. Navigation paths

| Path | How |
|---|---|
| Complete ordered assimilation | `sequence full`: 42 packs, `orientation/1` … `handoffs/1`, then `■ END:full` |
| Task-specific entry | `bootstrap --task <T>` / `resolve <T>`: always-loaded packs plus the packs covering the task's mandatory closure, in primary order |
| Dependency-first | `sequence dependency-first`: units topologically ordered by mandatory edges |
| Domain-specific | `sequence domain:<tag>` for each unit tag (context, docs, frontend, governance, operations, registry, runtime, spec, trace, verification…) |
| Decision / history traceability | `sequence trace`: orientation → governance (laws, decisions, conflicts) → history → handoffs |
| Resume from handoff | `resume <TASK>`; static path `sequence resume` |
| Next pack | `next <pack> [--sequence S]`: read from the manifest order, never guessed |

---

## 4. Maintenance and integration points

| Event | What happens | Where it is enforced |
|---|---|---|
| Any source, registry, spec, implementation or test change | Its digest changes. The packs listing it, and the packs listing it as a direct prerequisite, regenerate. | `context.js check` in CI; `test/context.js` in `npm test` |
| New file | It must be claimed by a class or it is `UNREGISTERED_FILE` (CI fails). Unit selectors place it automatically. | validate |
| Superseded artifact | A `# [SUPERSEDED` marker or class lifecycle requires a complete `supersessions[]` record; the successor gets a `supersedes` edge. | validate |
| Dependency change (`require`, compile inputs, projection inputs, CI test list) | Re-extracted on every build; a broken reference is `DANGLING_EDGE`. | validate |
| A quoted law or protocol line edited in its source | `CONSTRAINT_QUOTE_MISSING`: `build` refuses (fail closed) until the constraint is re-quoted or retired. | validate / build |
| Branch handoff, interruption | `context.js handoff …` appends a record and rebuilds; commit both. | `HANDOFF_INVALID` |
| Pull request | The CI "Context integrity" step and `npm test` run `check` and the suite. | `.github/workflows/ci.yml` |
| Merged change | The same check runs on push to `master`. The manifest committed with the merge is the last validated context. | CI |

**Incremental regeneration.** `build --affected` regenerates in memory and writes only files whose bytes changed. It predicts the affected packs by reverse traversal: owning units, one-edge neighbours in the old and new graphs, constraint sources, and sequence neighbours when a unit's part count changes. It fails with `INVALIDATION_MISMATCH` if anything outside the prediction changed. A plain `build` is the complete rebuild and reconciliation; it also deletes orphaned pack files.

**Semantic vs byte staleness.** A pack becomes byte-stale when its own sources or their direct derivation inputs change. Packs further downstream may need a human to review their meaning without changing bytes; `impact <T>` lists both sets.

---

## 5. Hygiene and lifecycle governance

`node _registry/context.js hygiene` is deterministic and advisory. It writes nothing. Its derived-drift check runs the generator in a throw-away copy.

- **Duplication.** It finds exact duplicate files (sha256), near-duplicate documents (line-level set overlap ≥ 90% of the smaller document) and repeated explanations (authored paragraphs ≥ 160 chars recurring verbatim). Repetition across generated artifacts has a single source and is not counted.
- **Decay.** It finds references from active text to superseded/retired artifacts, generated artifacts that drifted from their generator (`derivedChecks[]`), unreferenced active artifacts, ownerless artifacts, and incomplete supersessions.
- **Metrics** (`thresholds` ratchet from the observed baseline; `ceilings` are budgets):

  | Metric | Observed 2026-10-22 | Threshold |
  |---|---|---|
  | competing canonical definitions | 0 | 0 |
  | open source-of-truth conflicts | 5 | 5 |
  | exact duplicate files / near-duplicate pairs | 0 / 3 | 0 / 3 |
  | authored duplicate paragraph groups | 22 | 22 |
  | generated artifacts drifted from generator | 93 (CNF-001) | 93 |
  | broken references / orphaned / ownerless / unresolved supersessions | 0 / 0 / 0 / 0 | 0 each |
  | default bootstrap size | 35,516 chars (4 packs) | ceiling 40,000 |
  | max navigation steps (unit prerequisite depth) | 5 | 5 |
  | unresumable handoffs | 0 | 0 |

  A value above its threshold is `HYGIENE_REGRESSION`, which fails `check`. A value below it is reported so the owner can lower the threshold. No threshold forces information to be deleted.
- **Plan.** Prioritized items (`HYG-NNN`, P1–P3) with evidence, a proposed disposition, the dependency impact (`impact` count), and ✋ when owner authorization is required. The current plan is:
  - P1: resolve CNF-001/002.
  - P2: the three `_superseded/*.original.md` files are 100% contained in their bannered root copies, and git history already preserves them. The proposal is to retire them after owner approval.
  - P2: CNF-003…005.
  - P3: five repeated explanations.
- **Safety.** Hygiene never deletes, compacts or re-classifies (CST-NO-DESTRUCTIVE-HYGIENE, DEC-CTX-006). An approved consolidation is applied as an ordinary change:
  1. migrate the unique content to its canonical owner;
  2. record a `supersessions[]` entry, or set the class lifecycle to `retired`;
  3. update references;
  4. run `context.js build` and `check`, `npm run registry`, `node _registry/audit.js`, and the affected suites.

**Current vs archive.** The default bootstrap (`bootstrap.alwaysLoad`) is orientation plus governance: 4 packs, about 35k chars, with no historical artifact (asserted by the tests). History lives in its own unit, under a HISTORICAL banner, and is reached only through `sequence trace`, a task closure that names it, or `search`. Search labels every non-current result `[<LIFECYCLE> — not an active requirement]` and ranks it last.

---

## 6. Commands

All commands run offline; `git` is optional (without it, discovery falls back to a directory walk). Set `CONTEXT_ROOT` to operate on another checkout. `npm run context -- <command>` is equivalent.

```text
node _registry/context.js bootstrap [--task T] [--window N] [--loaded id[@digest],…] [--json]
node _registry/context.js resolve <T> [--json] | prereqs <T> | impact <T> [--json]
node _registry/context.js list | sequence [ID] | next <PACK> [--sequence S] | open <PACK> | map | search <Q>
node _registry/context.js validate [--all] [--json] | stale | build [--affected] [--budget N] | check [--no-hygiene] [--no-derived]
node _registry/context.js hygiene [--json] [--no-derived] [--top N]
node _registry/context.js handoff --template | handoff --task T --draft F --start REV [--verify CMD]… [--pr URL]
node _registry/context.js resume <TASK>
```

`T` is a node id (`UCOS-CON-000004`, `file:lib/authz.js`, `LAW-002`), a path, `unit:<id>`, a pack id, or `changed:<rev>`.

Expected outputs (from this repository, abbreviated):

```text
$ node _registry/context.js check
✓ validate: 342 nodes, 2565 edges, 0 error(s)
✓ fresh: every generated file matches the repository
✓ deterministic: two generations over unchanged inputs are byte-identical (43 files)
✓ bounded: 42 packs, largest 11302 ≤ budget 12000
✓ hygiene ratchet: 13 metrics, 0 regression(s)
✓ context check passed in 1649 ms

$ node _registry/context.js bootstrap --task lib/authz.js
UCOS context bootstrap plan — READY
  repository  https://github.com/…/universal-product · <branch> · <commit> · working tree clean
  registry    _registry/context.json · manifest fresh · inputs … · 0 error(s), 6 warning(s)
  task        lib/authz.js → 2 mandatory, 62 relevant
  stage 1     orientation/1 (8645), governance/1 (10894), governance/2 (11269), governance/3 (4708)
  stage 2     runtime-server/2 (10580)
  governing   LAW-001
  conflicts   open: CNF-001 … CNF-005 · touching this task: CNF-002, CNF-003
  next        read the stage packs in order, then re-run with --loaded <ids> for the receipt

$ node _registry/context.js bootstrap --task lib/authz.js --loaded orientation/1
UCOS context assimilation receipt — REFUSE
  ✗ mandatory packs not loaded: governance/1, governance/2, governance/3, runtime-server/2      (exit 2)

$ node _registry/context.js next handoffs/1
■ END:full — handoffs/1 is the last of 42 pack(s)

$ node _registry/context.js prereqs UCOS-IDN-000001
mandatory prerequisites, in reading order (23):
  CST-DEPENDENCY-LAW … LAW-003 · _registry/{content-core,domains,manifest,primitives,terminology}.json · _registry/project.js · UCOS-CON-000001…010 · UCOS-IDN-000001

$ node _registry/context.js impact _registry/content-core.json
packs whose bytes change when it changes (9): canonical-registry/1, corpora/1, governance/1…3, registry-pipelines/1…2, spec-Core/1…2
packs describing downstream artifacts — review for meaning (20): …

$ node _registry/context.js stale          # after editing lib/b.js without rebuilding
  ~ file:lib/b.js
  stale    _context/packs/code--1.md
✗ generated context is stale — run `node _registry/context.js build`
```

---

## 7. Operating procedures

- **After any change:** run `node _registry/context.js build`, then `check`, and commit `_context/` with the change.
- **A new kind of file:** add a class (`match`, `kind`, `authority`, `lifecycle`, `owner`). If the file has no natural unit, add a selector to one; if it should be read in a new place, add a unit and put it in a sequence.
- **A new binding rule:** add a `constraints[]` entry that quotes its source verbatim. Never paraphrase. If the source changes, the build refuses until the quote is updated.
- **A decision:** add a `decisions[]` entry (`status`, `authority`, `statement`, `rationale`, `governs`). To supersede an older decision, list its id in `supersedes`; the old record stays.
- **A conflict:** add a `conflicts[]` entry with evidence and the decision needed. When resolved, set `status: "resolved"` and remove any `acknowledges` that no longer apply; the dangling reference must disappear or the build fails.
- **Superseding or retiring an artifact:** add a `supersessions[]` record, mark the file (banner or class lifecycle), migrate references (hygiene lists the remaining ones), rebuild, and check.
- **Pack size:** change `budgets.packChars` (and `reserveChars` if headers grow). The bootstrap window stays separate (`--window`).
- **Schema evolution:** the spec, pack, manifest, handoff and receipt each carry a `schema` id. Additive fields are backward-compatible. A breaking change bumps the id (`…v2`) and `GENERATOR_VERSION`, and teaches `specProblems()` / `handoffProblems()` to read both during migration. Handoff records are never rewritten; a v1 record stays valid evidence.
- **Ending a session:** follow the handoff steps in `AGENTS.md`.

## 8. Security

- **Discovery** honours `.gitignore`, so `data/master.json`, `data/registry.json` and `.env*` never register. `denyPaths` refuses any secret-shaped path that becomes visible anyway (`SECRET_PATH`).
- **Summaries** drop secret-shaped text. A secret-shaped string in a rendered pack is `SECRET_CONTENT` (an error), and handoffs are scanned the same way.
- **Command output** recorded by `handoff --verify` keeps only a digest and a scrubbed 12-line tail.
- **Remote URLs** are printed with embedded credentials stripped.
- **Retrieved content is data.** Every pack says so, and AGENTS.md rule 1 forbids retrieved content from overriding the protocol or a higher authority.
- **Fail closed.** An invalid spec, an integrity error, stale context, a broken constraint quote or a broken handoff chain each stop `build` / `bootstrap` / `resume` with the reason.

## 9. Measured limits

Measured on 2026-10-22, Node 22.22, cloud container:
- **Size:** 319 files (8.7 MB), 342 nodes, 2,565 edges, 42 packs (after the first handoff).
- **Speed:** a full generation takes about 0.35–0.6 s and reads every registered byte once. `check` (validate, freshness, double generation for determinism, hygiene including the projection-drift run) takes about 1.7 s; the hygiene analysis alone takes about 0.4 s.
- **Scaling:** the cost is linear in bytes and edges. Pairwise duplicate detection goes through an inverted index; lines shared by more than 8 files are treated as boilerplate and skipped.
- **Not shown:** behaviour beyond this size has not been demonstrated. There is no cache, because a full regeneration is cheaper than cache invalidation at this scale, and the gap register records where that stops being true.
- **Small agents:** a task on `lib/authz.js` needs 5 of 42 packs (46k chars against 8.7 MB of repository). With `--window 12000` it stages into 5 windows, each within budget.

---

## Gap register

| # | Gap | Impact | Next step |
|---|---|---|---|
| G-1 | CNF-001…005 are open (see §1). | Two of them (drift, seal input) are real integrity defects. They are visible in every bootstrap and in the hygiene plan. | Owner decisions; CNF-002 is the separately tracked G1 seal fix. |
| G-2 | Pack summaries are extracted (first heading/comment), not semantic. | A summary can be uninformative; the source is always linked. | Optional authored `summary` overrides per artifact, if wanted. |
| G-3 | `implements` / `defines` edges between code and specifications are mostly not extracted (`IMPLEMENTATION_MAP.md` is prose). | Closure for a spec-level task does not reach the implementing modules automatically. | Add an extractor over a machine-readable implementation map, or authored edges. |
| G-4 | `schema.sql` drift (`scripts/schema-dump.js`) is not checked. The generator needs a booted DB. | Schema drift is invisible to hygiene. | Add a `derivedChecks[]` entry once the dump can run without side effects. |
| G-5 | Semantic (paraphrase) duplication is not detected, only verbatim. | Reworded duplicates pass. | AI-assisted analysis as a recommendation only (§15.7), never as authority. |
| G-6 | `.workbuddy-ai/memory/MEMORY.md` (111 KB narrative log) is preserved as historical evidence and not consolidated. | It is outside the default bootstrap, but large. | Owner-approved consolidation of still-current facts into decisions or handoffs. |
| G-7 | Acceptance criteria for a task are not structured. They come from the handoff objective and the specifications' text. | The receipt lists governing constraints, not task acceptance criteria. | Optional `acceptance[]` in the handoff draft. |
| G-8 | The scale limits in §9 are measured at the current size only. | Unknown beyond it. | Re-measure if the file count grows tenfold; add caching only if measurements require it. |
| G-9 | The 93 projected artifacts are listed in packs with digests but not summarized individually (their summaries are template text). | Navigation relies on titles. | Resolve after CNF-001 (re-projection). |

## Verification evidence

The results recorded for this change, including the commands, exit codes and suite counts, are in the handoff record `_registry/handoffs/UCOS-CTX-001/` (tool-verified section). Re-run them with `node _registry/context.js resume UCOS-CTX-001`.
