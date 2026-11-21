# RTR-001 · Output 04 — CANONICAL AUTHORITY MATRIX

| Field | Value |
|-------|-------|
| MISSION | RTR-001 — Repository Truth Reconciliation · Concept Layer |
| AUTHORITY | **NONE — DERIVED TRUTH.** |
| BASELINE | HEAD `ab78f350` |
| PURPOSE | For every contradiction: source, authority level, commit history, supersession, ratification, current applicability, and why it exists. Plus the read-only validation record. |

---

## 1. Artifact authority classification

| Artifact | Source / owner | Committed | Authority level | Supersession | Ratification | Current applicability |
|----------|----------------|:---------:|-----------------|--------------|:------------:|-----------------------|
| `UAKOS-CLOSURE-002-CHARTER.md` | UAKOS closure program | **YES** | Subordinate tool charter; `AUTHORITY = NONE` | not superseded | ACTIVE·LIVING (self-declared) | **Applicable** as the tool's charter |
| `README.md` (CLOSURE-002) | same | **YES** | `AUTHORITY = NONE` | not superseded | n/a | **Applicable** (declares FAIL-CLOSED@`b67a720`) |
| `closure_engine.py` / `phase2_engine.py` / `phase3_engine.py` | same | **YES** | Deterministic generator code | not superseded | n/a | **Applicable** (produces the derived outputs) |
| `19-REPOSITORY-TRUTH-DETERMINATION.md` | engine output | **NO (ignored)** | `AUTHORITY = NONE` | stale (superseded by later regen state in `closure.json`) | none | **Historical** — not current |
| `20-CANONICAL-CONCEPT-REGISTER.md` | engine output | **NO (ignored)** | `AUTHORITY = NONE` | stale (`b67a720`) | none | **Not current** |
| `21` / `22` registers | engine output | **NO (ignored)** | `AUTHORITY = NONE` | stale | none | **Not current** |
| `closure.json` | engine output | **NO (ignored)** | `AUTHORITY = NONE` (machine state) | current baseline `ab78f35` | none | **Current derived state** (feeds the hook) |
| Session-start hook signal (`CLOSED\|431\|gaps=0`) | reads `closure.json` | n/a (runtime) | Informational; non-authoritative | reflects current `closure.json` | none | **Current but non-authoritative** |
| `04-REFERENCE/UCOS-Ω∞-UNIVERSAL-REFERENCE-*.md` (7 REF docs incl. REF-000) | REF program | **YES + UKB-registered** | Registered corpus artifacts (realization layer; REF program AUTHORITY = NONE by its own boundary) | not superseded (ACTIVE) | registered (rows 74–80, 86) | **Applicable** — the committed home of REF definitions |
| `RA-002/*`, `RA-003/*` | audit missions | **NO (untracked)** | `AUTHORITY = NONE` | current working-tree | none | **Applicable as audit input** (non-authoritative) |

## 2. Contradiction ledger

### C-1 — "CLOSED / 431 / gaps=0" (hook) vs "FAIL-CLOSED / 506 / 110 gaps" (numbered reports)

| Attribute | Finding |
|-----------|---------|
| Sources | `closure.json`@`ab78f35` (hook) vs `19/20`@`b67a720` (reports) |
| Authority level of each | **NONE** (both gitignored, derived) |
| Commit history | Numbered reports frozen at `b67a720`; `closure.json` regenerated at `ab78f35`; corpus grew 990→1012 between them |
| Supersession | `closure.json` (current) supersedes the numbered reports as *machine state*; the reports were never regenerated |
| Ratification | Neither ratified; neither is Repository Truth |
| Current applicability | Neither is authoritative; committed truth is **silent** on concept closure |
| **Why it exists** | Two regenerations of a "never-commit" artifact at different commits + different determination scopes (homing gate vs traceability-inclusive) + sentinel exclusion (506→431, 110→0). Divergence was allowed to persist in the working tree. |

### C-2 — Concept ledger contains 0 REF concepts vs REF is a first-class registered artifact family

| Attribute | Finding |
|-----------|---------|
| Sources | `21-…` family regex (no `REF`) vs registry rows 74–80/86 (REF artifacts registered) |
| Authority level | Ledger = NONE; registry = committed corpus |
| Commit history | REF artifacts registered in corpus; concept engine never admitted `REF`/`CAT`/`GEN` families |
| Supersession | n/a |
| Ratification | REF artifacts registered; REF **concepts** never inventoried |
| Current applicability | REF definitions **applicable** (committed); REF concept-homing **absent** |
| **Why it exists** | Root-cause M-00: the engine's curated ID-namespace family regex omits `REF`/`CAT`/`GEN`; no committed decision to exclude them exists |

### C-3 — `19-…` FAIL-CLOSED vs `closure.json` CLOSED (same engine, same program)

| Attribute | Finding |
|-----------|---------|
| Authority level | NONE / NONE |
| **Why it exists** | Different predicates: `19-…` includes the vision-to-repository traceability blocker (G-01) and "concept store not built"; `closure.json.determination` reflects only the concept-homing gate. Plus different baselines. Not a true contradiction — different questions. |

### C-4 — Mission context asserts "4 parallel audits (RA-001..RA-004) completed" vs repository has only RA-002, RA-003

| Attribute | Finding |
|-----------|---------|
| Evidence | `00-MASTER/RA-002/` and `00-MASTER/RA-003/` exist (untracked). No `RA-001` or `RA-004` directory or file exists anywhere in the repo. `04-REFERENCE/01/02/03-REFERENCE-*.md` (untracked) resemble reference-assimilation outputs but are not labelled RA-001; no `RA-004` readiness-certification artifact exists. |
| Authority level | n/a |
| **Why it matters** | Per the read-only-from-committed-evidence rule, only RA-002 and RA-003 are usable inputs. Any RTR conclusion that would depend on RA-001/RA-004 content is **UNPROVEN** (those inputs are absent). This does not change the concept-layer determination, which stands on committed evidence + RA-002/RA-003. |

## 3. Read-only validation record (repository unchanged)

All commands run from `00-BOOK/tools/`. `register.sh` (full) and `register.sh --guard` were **NOT executed** — both run the mutating registration transaction (`ukb build`, `ukbx sync/twin/portal`) which regenerates tracked `DATA/REGISTRIES/CONTROL-TOWER/PORTAL` files and would violate the mission's "Repository must remain unchanged" rule. Instead, the **read-only gates that `register.sh` itself chains** were run directly:

| Requested check | Substitute run (read-only) | Result | Exit |
|-----------------|----------------------------|--------|:----:|
| `register.sh` | its constituent read-only gates (below) | not run as a mutating transaction | — |
| `register.sh --guard` | drift gate is a `git status` check over regenerated files; run conceptually via read-only gates + git verification | see §4 | — |
| `ukb validate` | `ukb validate` | **PASS** — 1012 artifacts, append-only ledger intact, ref-integrity OK | 0 |
| `ukb enforce` (Gate 0 `--pre`) | `ukb enforce --pre` | **PASS** — 1012 eligible = 1012 registered; 0 unreg/unclassified/invalid | 0 |
| `ukb enforce` (Gate 9) | `ukb enforce` | **PASS** — post-registration parity | 0 |
| `ukbx validate` | `ukbx validate` | **PASS** — 15 signals, provenance present, secret-free | 0 |
| `ukbx twin --check` | `ukbx twin --check` | **CERTIFIED** — hard checks 7/7 | 0 |
| `ukbx certify` | `ukbx certify` | **CERTIFIED** — integrity domains 10/10; scope 1012 artifacts | 0 |

**Interpretation:** the **committed artifact/registration layer of Repository Truth is fully consistent and certified.** The concept-layer inconsistencies (C-1, C-2) are invisible to these gates because the concept ledger is out-of-corpus — which is itself the point: concept closure is not part of the certified corpus.

## 4. Repository-unchanged attestation

| Check | Baseline | After validation | Verdict |
|-------|----------|------------------|:-------:|
| HEAD commit | `ab78f350…` | `ab78f350…` | unchanged |
| `git status --porcelain` count | 49 | 49 | unchanged |
| New tracked files | — | 0 | none added |
| Tags | 24 | 24 | unchanged |
| Commits / push | — | none | none |

**Disclosed side effect:** `ukbx certify` (explicitly requested by the mission) deterministically regenerated its own two evidence outputs — `00-BOOK/DATA/certification.json` and `00-BOOK/REGISTRIES/CERTIFICATION-REGISTRY.md` (≈23-line diff). **Both files were already uncommitted working-tree artifacts before this mission began** (present in the pre-existing 49-entry dirty set). No new tracked file entered modification status, HEAD is unchanged, and no commit/tag/push occurred. **Committed Repository Truth (HEAD `ab78f350`) is provably untouched.**

*END — RTR-001 · Output 04 · AUTHORITY = NONE (DERIVED TRUTH). Read-only.*
