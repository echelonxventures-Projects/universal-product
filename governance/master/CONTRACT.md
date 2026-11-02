# Common assimilation contract — design (not implemented beyond requirements)

Status: **design, partly implemented.** The implemented kinds are the ones `kinds.json` registers, each with its adapter and fixtures (GATE.md); the envelope is read in any format `contribution-formats.json` registers (LXM-REQ-000253). Every other type below counts as implemented only once its adapter exists and its fixtures pass.

This is the complete intended design of the assimilation contract for every object type SRC-0009 §4.3 names, set down before any further sequencing (SRC-0009 §1.3, LXM-REQ-000227). The order of work in §5 follows from its dependencies (LXM-REQ-000230).

## 1. The common envelope

Every contribution, of any type, carries:

| Field | Meaning |
|---|---|
| `id` | Contribution ID; with the content SHA-256, its identity in the ledger and the exception log |
| `type` | requirement · decision · evidence · stage-action · prose-section · source · specification · configuration · implementation-artifact · any registered future type |
| `source`, `section` | Registered source and clause; mandatory for every type |
| `payload` | Type-specific content (text for requirements; fields for decisions or evidence) |
| `target` | For change operations: the canonical object it changes |
| `relations` | extends · supersedes (+ `reason`) · depends-on · supports · recognized-as · distinct-from |
| `decision` | Adopted LXM-DEC authorizing an owner-reserved change |

## 2. The common pipeline (type-independent; already in `assimilate.py`)

1. Recover any interrupted commit.
2. Receive, then run the common checks: source, authority, references and owner holds.
3. Run the type adapter (§3).
4. Stage the mutation, then `build.py` + `validate.py` + the adapter's own checks.
5. Commit through the journal.
6. Exception and ledger.

These outcomes stay common to every type: RECOGNIZE, COMPOSE, EXTEND, PARTIAL, NEW, SUPERSEDE, NOOP, QUARANTINED, REJECTED and ERROR. A type may declare some of them not applicable.

## 3. The type adapter interface

| Hook | Requirement adapter (implemented) |
|---|---|
| `load(root)` → canonical objects of this type | `blocks(reqs.txt)` |
| `index(objects)` | lexical profiles + titles |
| `classify(part, objects)` | EXACT / COVERED / CONFLICT / RELATED / NOVEL |
| `plan(contribution, classification)` | minimum mutation |
| `apply(plan, files)` → new file texts | surgical record rewrite + stage citation |
| `checks(staged)` | clause expressed; no duplicate |
| `owner_decided(object)` | owner-decision lineage or LXM-DEC reference |

## 4. Every object type: canonical home, prerequisite and rules

A new object type joins by registering an adapter (§3) and its fixtures; the envelope, pipeline and outcomes do not change (SRC-0009 §3.2, §4.1).

| Type | Canonical home today | Prerequisite (dependency) | Type-specific rules |
|---|---|---|---|
| requirement | `reqs.txt` | Present | **Implemented** (GATE.md) |
| decision | `decisions.txt`, rendered as Part C; status, normative effect and mutation-authorization scope kept separate | **Done** (2026-10-30): the register is data, read by gate, generator and validator through one parser, and the decision adapter gates opening and adopting a decision (approval on file, naming the decision; adopted decisions immutable). Supersession is not implemented yet | Only the owner adopts; an adopted decision is never edited, only superseded by a later decision |
| stage-action | `stages.txt` | **Stable action IDs done** (2026-10-30): `STG-NN.A-k`, permanent, shown in Part E. **Gated** (2026-10-31): kind `stage-action` | Every action cites ≥ 1 requirement; no requirement prose; the 17-stage and per-stage checks in `validate.py` become adapter rules, so adding a stage is a governed change |
| source | `sources.txt` + `sources/` | **Gated** (2026-10-31): kind `source`, with `capture.py` as the way in | Only the owner moves a source to owner-confirmed, citing an adopted decision; a new text version of a ledgered source is re-assimilated clause by clause (ledger diff first) |
| evidence | `evidence.txt`, rendered as G.3 | **Done** (2026-10-30): the register is data, and the evidence adapter gates additions and supersessions | Evidence is never edited, only superseded by newer observations; it must name what it verifies; stale evidence is flagged by age and SHA, never silently reused |
| prose-section | `frame.md` | **Gated** (2026-10-31): kind `prose`, by exact heading or anchor; section IDs are still to come | No normative text outside Part D (prose may only explain or point); changed prose is diffed and validated; owner-authored sections (C, G.4) need `decision:` |
| specification | Repository (`docs/domains/*`, `volumes/*`, `UCOS-MASTER.md`) | A repository adapter that runs where the writer works (`amazon-62`); this candidate cannot write there | One specification per domain (Knowledge Once); each section cites the requirements it specifies; generated sections are never edited by hand |
| configuration | Repository (seed and registry data) | **Static adapter built** (2026-10-30): `config_adapter.py`, driven by `config_adapter.json`, 11 fixtures, baseline on `39ed4d6`. It covers every configuration source: 14 settings files and the documented environment variables, with 21 catalogue or governed files classified and none unaccounted. It reports each setting's reader (explicit, plausible, none or undeclared) and every copy of its value in code, with a ratchet. Runtime proof of use: `--runtime-trace` consumes the paths running code reads, recorded by the settings engine under `LX_SETTINGS_TRACE`. The patch is prepared (`intake/patches/settings-trace.patch`) and was exercised on a scratch copy; installing it is the sole writer's. **Still needed:** a configuration schema per definition (LXM-REQ-000074), and running it in CI (LXM-DEC-000010) | A configuration value never proves its engine applies it (LXM-REQ-000198); changes are versioned and reversible (LXM-REQ-000202) |
| implementation-artifact | Repository (code, tests) | **Static adapter built** (2026-10-30): `code_adapter.py`, driven by `code_adapter.json`, 7 fixtures, baseline on `39ed4d6`. It checks that every gate is executed by CI, every test is run, every module is reached by a test and owned exactly once (read from the repository's own ownership registry), that no function body is duplicated, and with `--git-clean` that the tree is clean. Traceability (LXM-REQ-000204): `trace.txt`, rendered as Part H.4, links 42 product requirements to their code, configuration and tests, and records 1 known gap; `--trace` checks every path and reports untraced modules (112 of 152, mostly product features whose requirements live in the repository's specifications, not in this Master). **Still needed:** the specification adapter that traces those, test results rather than reachability, and running in CI (LXM-DEC-000010) | Accepted only with its tests and evidence (LXM-REQ-000229); never certified by its own existence (SRC-0009 §8.2) |

## 5. Dependency order (SRC-0009 §6)

1. **Decision register** (`decisions.txt` + adapter). *The register is done; the adapter is next.* Every owner-reserved path, including SRC-0008 §7.1 and SRC-0009 §7.2, depends on reading adopted decisions reliably.
2. **Stable stage-action IDs** (data change, then switch `applied-in`). *Done*: the positional-reference limit is removed.
3. **Source adapter**, which owner confirmation of SRC-0004 to SRC-0009 needs.
4. **Evidence** (*done*), then **prose sections**.
5. **Repository adapters** (specification, configuration, implementation artifact). They need 1–4, the owner's adoption of this master and its repository location (LXM-DEC-000010), and the sole writer to run them.

Each increment is permanent (LXM-REQ-000230):
- No temporary substitute becomes an authority. For example, Part C stays the decision authority until `decisions.txt` replaces it in one validated step.
- Each step is done only when:
  - its adapter passes fixtures for every applicable outcome;
  - `validate.py` passes on the real candidate;
  - replay is idempotent;
  - regeneration is byte-identical.

## 6. The assimilation capability's own lifecycle (SRC-0009 §5, LXM-REQ-000229)

| Layer | State today |
|---|---|
| Constitution | LXM-REQ-000220 to 000230 (SRC-0008, SRC-0009) |
| Specification | GATE.md (implemented behaviour), this contract (design) |
| Canonical model | `reqs.txt`, `stages.txt`, `sources.txt`, `decisions.txt`, `sources/`, `frame.md` |
| Implementation | `assimilate.py`: requirement adapter; `config_adapter.py` and `code_adapter.py`: static conformance of configuration and code (not yet gated contribution types) |
| Configuration | `lexicon.txt`, `gate.json` |
| Runtime enforcement | **Partial.** The gate enforces every check for contributions submitted to it. Nothing stops a direct edit of a canonical file; `validate.py` detects structural breaks afterwards, not semantic duplication. |
| Testing | `test_assimilate.py`, 38 scenarios; `test_config_adapter.py`, 12 scenarios; `test_code_adapter.py`, 9 scenarios; `test_knowledge.py`, 7 scenarios; `test_readiness.py`, 10 scenarios; negative controls against the previous gates |
| Observability | `intake/ledger.jsonl` (every run), `intake/exceptions.txt` |
| Release readiness | Computed, not declared: `readiness.py` (rules in `readiness.json`, 10 fixtures), also reading test results summarised by `test_results.py` derives GO or NO-GO from the decision register, the release register's gates, CI runs on the candidate SHA, both adapters run on the same tree, and traceability gaps. It fails closed and cross-checks the register's declared verdict. Not yet run in CI (LXM-DEC-000010) |
| Evolution | Record versions and history (`v:`/`h:`); `gate_version` in every ledger line |
| CI installation | Prepared, not installed: `intake/ci-package/` (`ci-check.sh`, the CI job, instructions), rehearsed on a scratch clone of `39ed4d6`. Installing needs LXM-DEC-000010, the owner's source files committed, and the sole writer |

The capability is therefore **not complete**: one of nine types is implemented, and runtime enforcement does not cover direct edits.
