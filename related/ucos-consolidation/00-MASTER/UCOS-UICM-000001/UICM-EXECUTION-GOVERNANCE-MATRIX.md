# UICM — Execution Governance Matrix

> **Artifact:** `UICM-EXECUTION-GOVERNANCE-MATRIX`
> **Programme:** UCOS-UICM-000001 — Phase 4 discovery
> **AUTHORITY = NONE — DERIVED TRUTH.** This matrix confers no write right. Every scope
> below is *read* from a located instrument.
> **Disposition:** DISCOVERY ONLY. No gap resolved. No registry created.

---

## 1. Write-scope vocabulary — reused, not invented

Three located vocabularies already express execution boundaries, and Phase 4 uses them
rather than coining a fourth:

| Vocabulary | Values | Located in |
|---|---|---|
| check write scope | `read-only`, `own-memory`, `projections` | `uccep-bindings.json` `checks[].write_scope` |
| negative write authority | 11-prefix deny list | each declaration's `programme.forbidden_write_prefixes` |
| immutability proof | `write set ∩ located record set = ∅` | asserted by gates G-23..G-26 |

The frozen corpus is a separate, mechanical guard:

```
FROZEN_PREFIXES = ("00-BOOK/", "00-SOURCE/", "99-FREEZE/")
  engine/foundation/guards/frozen_paths.py:16  ->  ec1-frozen-guard  ->  ec1-ci.yml (DP-03)
```

**`pyproject.toml` and `verify.sh` are not frozen.** They sit at the repository root, outside
every frozen prefix, and neither is a registered artifact (`INCLUDE_EXTENSIONS` covers only
`.md`, `.txt`, `.docx`, `.json`, so editing them cannot trip the `register.sh --guard` exit-3
drift gate either). The Phase-2 hold on those two files is therefore a **programme
constraint, not a mechanical one** — nothing in the repository will stop an edit to them. That
makes the hold a discipline that has to be observed rather than a guard that can be relied on.

## 2. Execution boundary per dimension

| Dimension | Gaps | Resolution owner | Instrument | Write scope | Validating gate | Gateway (layer 5) |
|---|---:|---|---|---|---|---|
| `identity` | 1 | UCOS-UGA-001 | `00-MASTER/UCOS-UGA-001/uga_engine.py run` | `00-MASTER/UCOS-UGA-001/*` + `00-BOOK/DATA/id-ledger.json` (`by_object`) | `verify.sh` 6b — `uga_engine.py gate`, UGA-INV-01..10 all blocking | yes — the subject is constitutional metadata (a minted identity) |
| `registry` | 3 | UCOS-REPOSITORY-ROOT | edit `pyproject.toml` | `pyproject.toml` — `[tool.coverage.run] source`, `[tool.pytest.ini_options] addopts` | `verify.sh` 2 (`--cov-fail-under=90`) + 3 | no — source config, not metadata |
| `governance` | 1 | UCOS-UGA-001 | none — free rider on `identity` | same as `identity`; no independent write | `verify.sh` 6b | as `identity` |
| `contract` | 4 | the capability's own package | add `__all__` | exactly `<location>/__init__.py` | `verify.sh` 1 (ruff) + 2 | no |
| `coverage` | 3 | UCOS-REPOSITORY-ROOT | none — free rider on `registry` | same as `registry`; no independent write | `verify.sh` 2 + 3 | no |
| `evidence` | 39 | the capability's own package | add an evidence producer | exactly `<location>/evidence.py`, or a `"ucos-…evidence…"` literal in its own artifacts | `verify.sh` 2 + the capability suite | no |
| `certification` | 35 | CMG-DLG-40 / UCCEP-000000 | bind a gate | `.github/workflows/*.yml` + `uccep-bindings.json` `checks[]`/`gates[]` | the bound workflow; `uccep-gate.yml` as aggregate backstop | no |
| `determinism` | 42 | UCOS-REPOSITORY-ROOT under CMG-DLG-40 | add a `run_stage` line or a workflow replay marker | `verify.sh` or `.github/workflows/*.yml` | the added stage itself | no |
| `evolution` | 30 | CMG-DLG-40 / UCCEP-000000 | gate binding + prerequisites | union of `registry`, the capability suite, and gate binding — **no new scope of its own** | `verify.sh` 1,2,3 + the bound gate | no |

Two dimensions (`governance`, `coverage`) hold **no independent write scope**: they close as a
side effect of `identity` and `registry` respectively. Recording that explicitly prevents two
owners from being authorized for one edit.

## 3. Boundary disjointness — a defect found and resolved

Principle 1 requires exactly one owner per gap. That is necessary but not sufficient: two
owners with *overlapping write scopes* can collide even when each gap has one owner. Tested,
and the naive scoping fails:

```
capability-local write scopes as SUBTREES (<location>/**):   40
NESTING CONFLICTS:                                           38
  engine/**   contains engine/ceu/**, engine/constitution/**, … (14 descendant gaps)
  platform/** contains platform/identity/**, platform/portal/**, … (25 descendant gaps)
```

`engine` and `platform` are themselves capabilities (depth-0 namespace roots), so a subtree
scope for `engine` would authorize its owner to write inside 14 other capabilities' packages —
and `platform` inside 25. That is duplicate write authority arriving through the back door.

**Resolution: scope is the specific target file, never the subtree.** Both probes read exactly
one file per capability, so a file-level scope is sufficient and disjoint:

| Dimension | Target file | Probe that reads it |
|---|---|---|
| `contract` | `<location>/__init__.py` | `_publishes_interface` — an `__all__` `Assign`/`AnnAssign` at module level |
| `evidence` | `<location>/evidence.py` | `producer_module` parameter, declared as `evidence` |

```
distinct target files: 43     collisions: 0     DISJOINT: True
```

The `evidence` dimension admits a second route — a `"ucos-…evidence…"` literal anywhere in the
capability's own artifacts — which is *inside* the capability's own package and so remains
disjoint from every other owner.

## 4. Central owner boundaries

| Owner | Write scope | Gaps | Overlaps any other scope? |
|---|---|---:|---|
| UCOS-UGA-001 | `00-MASTER/UCOS-UGA-001/*`, `00-BOOK/DATA/id-ledger.json` | 2 | no |
| UCOS-REPOSITORY-ROOT | `pyproject.toml`, `verify.sh` | 48 | no |
| CMG-DLG-40 / UCCEP-000000 | `.github/workflows/*.yml`, `uccep-bindings.json` | 65 | no |
| 40 capability packages | one target file each | 43 | no |

```
central x capability-local overlaps: 0
```

Note the asymmetry worth planning around: **two central owners hold 113 of 158 gaps.**
UCOS-REPOSITORY-ROOT alone covers 48, and both of its files are the ones Phase 2 held.

## 5. What each owner may NOT do

| Owner | Explicitly forbidden | Ground |
|---|---|---|
| every owner | write `00-BOOK/`, `00-SOURCE/`, `99-FREEZE/` | DP-03, mechanically enforced by `ec1-frozen-guard` |
| every owner | edit a committed UICM register | append-only; correction is by supersession |
| every owner | edit a gap record or a gap state | gaps are derived per run by total function |
| UCOS-UGA-001 | write `engine/`, `platform/` | `forbidden_write_prefixes` |
| namespace roots `engine`, `platform` | write inside a descendant capability | §3 — file-level scope |
| a capability package | mint an identity | UGA is the sole identity authority |
| a capability package | add its own `certification.py` as the closure route | 35 parallel certifiers; `certification_binding` + CMG-INV-02 |
| UICM itself | resolve any gap | `AUTHORITY = NONE`; measurement layer only |

## 6. Execution is post-hoc validated, not mediated

For 156 of 158 gaps the change is a source edit, and **no engine mediates it**. The
constitutional mutation gateway cannot: its stages are pure and its subject is
`ConstitutionalMetadata`, not files. So the enforcement model is:

```
  owner edits a file within its declared scope
        |
        v
  verify.sh stages 1,2,3,4,5,6,6b,6c,6d (+7 with --full)   deterministic, fail-closed
        |
        v
  ec1-ci.yml: frozen-path guard (DP-03), lint, coverage, build
        |
        v
  register.sh --guard  ->  exit 3 on registration drift
        |
        v
  UICM re-measures  ->  probe returns CLOSED  ->  new observation appended
```

The closure itself is never asserted by the owner. It is *measured*, and the measurement is
what becomes the observation. An owner cannot close a gap by claiming to have closed it —
which is the property that makes the whole model safe despite execution being unmediated.

## 7. Determination

**EXECUTION BOUNDARIES ARE DISJOINT AND TOTAL, GIVEN FILE-LEVEL SCOPING.**

43 write scopes, 0 overlaps, every gap inside exactly one. Two dimensions correctly hold no
independent scope. Three findings must carry forward:

1. **Subtree scoping is unsafe** — it would grant `engine` and `platform` write authority over
   39 descendant gaps. Scope by target file.
2. **The Phase-2 hold on `pyproject.toml` and `verify.sh` is unenforced** — those paths are
   unfrozen and unregistered, so nothing mechanically prevents an edit.
3. **Execution is unmediated; closure is not.** No engine gates the edit, but the closure is
   only ever a measurement, so a false closure claim is not expressible.