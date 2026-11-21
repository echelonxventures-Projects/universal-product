# 17 — Risk Assessment

**Anchor** `c6c20fb` · risks are rated on measured exposure, not opinion

Severity = consequence if realized · Likelihood = probability under Wave-2 conditions as planned

---

## Critical risks

### R-01 · A freeze taken now seals a provably false evidence binding

| | |
|---|---|
| Severity | **CRITICAL** |
| Likelihood | **CERTAIN if freeze proceeds** — the condition already exists |
| Source | B-1 |
| Exposure | 10 of 1,204 registered artifacts, including the capability catalogue that RIB, UCCEP and this programme all bind by pointer |

`content_hash` is how the registry asserts what an artifact *is*. Ten artifacts are bound to content
that does not exist at the anchor (0/10 HEAD hashes correct). `CEP-007` freeze law makes the freeze
record constitutional; freezing over B-1 makes a false assertion permanent and every downstream
certification that cites the freeze inherits it.

**Mitigation:** one atomic re-registration commit before any freeze. Cost: minutes. Verify with
`register.sh --guard` exit 0.

### R-02 · Wave-2 builds on 105,998 LOC that no gate exercises

| | |
|---|---|
| Severity | **CRITICAL** |
| Likelihood | **HIGH** |
| Source | B-4 |
| Exposure | 43.1% of LOC · 47.5% of test functions · 6 code roots · 12 subpackages |

The EC-3 Band 10–13 realizations (90,381 LOC) are the declared execution frontier — `data` is the
`single_active_frontier` — and they sit outside `testpaths`, the coverage source, the lint target and
the wheel. Their 3,828 test functions exist but are never run by `make test`. A regression introduced
in Wave-2 against any band surface is invisible to CI.

**Sharpest exposure:** `intelligence/` — 15,617 LOC, 115 test functions, no coverage, no lint. It
computes the derived truth every governance verdict consumes. A silent defect there corrupts the
measurement system itself, and the corruption would be self-consistent.

**Mitigation:** extend scope in `pyproject.toml` and the `lint` target **before** Wave-2 opens.
Expect failures on first run; that is the value.

### R-03 · The measurement system reports PASS for propositions it did not test

| | |
|---|---|
| Severity | **CRITICAL** |
| Likelihood | **REALIZED — already occurred twice** |
| Source | B-2, `UCCEP-F-006`, B-4 |

Three measured instances of a gate reporting PASS for a narrower proposition than the one its verdict
text claims:

1. `UAKOS-CLOSURE-002` reports `CLOSED | gaps=0` while `CLOSURE_SKIP_CORPUS=1` excludes the source
   corpus. True scope: **NOT-CLOSED, 91 gaps.** Wave-1 discovered this only by re-running with the
   flag removed.
2. `ukb validate` reports success while skipping schema validation when `jsonschema` is absent, and
   CI installs it with `|| true`.
3. `CK-VERIFY` reports coverage 94.11% — true of 34 packages, not of the repository.

This is the highest-order risk in the programme, because it degrades the trustworthiness of every
other verdict. The repository's governance model rests on gates being propositions about reality; a
gate whose scope is narrower than its claim converts governance into ceremony.

**Mitigation:** every gate must emit its **denominator** alongside its verdict, and a verdict string
must not assert more than the executed scope. `UCCEP` already models this correctly with
`certification_ceiling` and `unavailable` — extend the pattern.

---

## High risks

### R-04 · Traceability cannot be reconstructed later at acceptable cost

| | |
|---|---|
| Severity | **HIGH** |
| Likelihood | **HIGH** |
| Source | B-3 |
| Exposure | 1,204 artifacts × 13 dimensions at 2.2%; 969 unbound evidence artefacts |

Trace links are cheapest to record at the moment of authorship. 1,204 artifacts already exist with
10 of 13 dimensions empty; Wave-2 adds more. The gap grows monotonically with every wave, and
retrofitting requires re-reading each artifact to infer what it satisfies.

Mitigating factor, and it is significant: the evidence **already exists** — 490 `_evidence/` files,
433 certification instruments, 46 band completion reports. Closing B-3 is largely mechanical
binding rather than fresh authoring.

**Mitigation:** make traceability population a **precondition of registration** for every new
artifact (`CK-REG-ENFORCE` already gates classification — extend it to the spine), and run a one-time
binding pass over the 969 existing artefacts.

### R-05 · Sequential identity allocation collides under parallel development

| | |
|---|---|
| Severity | **HIGH** |
| Likelihood | **HIGH once Wave-2 parallelises** |
| Source | G-ID-1 |
| Exposure | 95 category sequences, one mutable cursor each; `max_parallel` = 26 |

`id-ledger.json` holds `category_seq` as a single integer per category and `page_cursor` as one global
integer. Two branches that each register an artifact in the same category both take the next sequence
and collide on merge. RIB computes `max_parallel = 26`; Wave-2 is expected to exploit it.

Wave-1 measured **0 duplicate `universal_id`** — the invariant holds *today*, under serial
development. It is not merge-safe.

**Mitigation:** decide the identity strategy explicitly before parallel work — either serialise
registration through a single lane, or introduce a globally unique component (which is also what
`UCOS-Ω∞-ABSOLUTE-IDENTITY-FEDERATION-AND-CONTINUITY-CONSTITUTION` requires for the declared 28
universes).

### R-06 · No ratification path exists, so no work can ever be declared final

| | |
|---|---|
| Severity | **HIGH** |
| Likelihood | **CERTAIN** |
| Source | B-5 |

Tier T1 VACANT, `CMG-000001` PROVISIONAL, no competent ratifying authority. Every certification in
the repository — including a perfect Wave-2 — caps at PROVISIONAL. 1,103 of 1,204 artifacts remain
ACTIVE; only 1.3% have reached FINAL or CERTIFIED, and that ceiling is structural, not effort-limited.

**Risk of inaction:** indefinite accumulation of provisional work with no closure mechanism.
**Risk of wrong action:** inventing an internal authority creates a parallel constitution — the exact
failure `CMG-000001` exists to prevent.

**Mitigation:** escalate to an authority external to the artefact set via the `CEP-006` route. This
is a decision for the programme owner, not an engineering task.

### R-07 · Building above an unimplemented control plane

| | |
|---|---|
| Severity | **HIGH** |
| Likelihood | **MEDIUM** |
| Source | G-SPINE-1, G-SPINE-2 |

CIOA and CCE are **layer 5** of an 11-layer architecture. Layers 6–9 (`engine/`, `platform/`, UKB,
MCS) are built and certified. The orchestrator that is supposed to govern them does not exist, and
neither do layers 10–11 (AEOS spine, adapters, CLI). Twelve declared gaps, four HIGH.

The consequence is already visible: coordination that CIOA would perform is instead distributed
across 57 `00-MASTER/` programme directories, 7 session hooks, 9 CI workflows and 49 Makefile
targets. It works, and it is not a control plane. Each additional wave increases the coordination
surface that must eventually be migrated onto CIOA/CCE.

**Mitigation:** honour the declared disposition `REALIZE_BY_COMPOSITION` — build CIOA/CCE from the
existing substrate (AEOS `ready_because` confirms the substrate is present) rather than adding more
coordination alongside them.

---

## Medium risks

| ID | Risk | Severity | Likelihood | Exposure / mitigation |
|---|---|---|---|---|
| R-08 | **Stale connector data masquerades as measured failure.** 4 dimensions (build, operational, production, security) report `BLOCKED` at 0% purely because 5 connector cursors have not advanced since 2026-07-15. `build` reports BLOCKED while `ec1-ci.yml` passes and `make build` works. | MEDIUM | REALIZED | Distinguish `NOT_MEASURED` from `BLOCKED` in the dimension model; re-advance cursors or mark the source unavailable |
| R-09 | **Derived-truth artifacts are read as authority.** Every RIE/RIB/UCCEP output correctly declares `AUTHORITY = NONE (DERIVED TRUTH)`, but they are the most convenient documents to cite. Wave-1 found RIB's 12 PASS verdicts stale by 2 commits (`G-RIB-1`) — a reader citing them would assert a verdict about a prior state. | MEDIUM | MEDIUM | Bind derived artifacts to an anchor commit in their own filename or refuse to serve them when their anchor ≠ HEAD |
| R-10 | **Hand-replicated pattern drift.** 286 modules across 4 bands follow one exact six-aspect template, hand-maintained, while `05-GENERATION/` (7 frameworks) and `platform.generation` sit unused. Divergence between bands is undetectable by any gate. | MEDIUM | MEDIUM | Generate from the located framework (output 15, opportunity 1) |
| R-11 | **Security is architecturally under-specified.** `14-SECURITY` stops at Taxonomy; security responsibility is split across `INFRASTRUCTURE-013`, `platform.security` and per-band `security.py` modules with no master registry. The `security` progress dimension is BLOCKED at 0%. | MEDIUM | MEDIUM | Complete `SECURITY-005…018` from the six band precedents; re-establish the Trivy connector |
| R-12 | **Two engines, two contradictory verdicts, one programme.** `closure.json` says CLOSED while `phase3.json` says NOT-CLOSED at the same baseline, and phase-3's verdict is a literal constant with no reachable PASS. A reader can cite either. | MEDIUM | REALIZED | `WP-UCCEP-001` — make the verdict measured; until then the contradiction must be stated wherever either is cited |
| R-13 | **Closure depends on an untracked external directory.** `<repo>/../UCOS` (6,332 files) is not tracked, versioned or hash-pinned, yet it determines the closure verdict. Anyone cloning the repository gets `gaps=0` by construction. | MEDIUM | HIGH | Pin the corpus by manifest + hash (the `99-FREEZE/SOURCE-HASHES.txt` pattern already exists), or vendor it |
| R-14 | **Findings register drifts from reality in both directions.** `UCCEP-F-003` is declared blocking but is discharged; `UCCEP-F-007` is declared non-blocking but is the sole blocking failure. Both are declaration-data errors in `uccep-bindings.json`. | MEDIUM | REALIZED | Correct the two entries; add a check that a finding's declared blocking status agrees with its gate outcome |
| R-15 | **No lexicon.** 94 categories (4 truncated), 10 undeclared enumerated vocabularies, 7 native-ID collision groups, no dictionary. Terminology drift is undetectable. | MEDIUM | MEDIUM | Establish the dictionary from the two existing inputs (output 11) |

## Low risks

| ID | Risk | Note |
|---|---|---|
| R-16 | 62% of artifacts default to `VOL-000`; `VOL-013`/`VOL-014` empty — volume classification is largely nominal | cosmetic until volumes drive behaviour |
| R-17 | 77 `Depends-On` edges lack an inverse — reverse-impact queries incomplete by 1.6% | affects analysis, not correctness |
| R-18 | `engine` has no measured dependency edge — impact analysis on the certified root is blind | RIB `GAP-DEPENDENCY` = 1 |
| R-19 | Freeze-boundary duplicate pair (`SOURCE-FILES/HASHES.txt`) — two sources of one truth | declared, non-blocking |
| R-20 | `engine/identity/` residual empty package (`__pycache__` only) | untracked; trivial cleanup |
| R-21 | All 1,204 artifacts at `version 1.0.0` and with empty `description` — records are not self-describing | lineage recoverable from `change-ledger.json` |

## Risk concentration

Three root causes generate 15 of the 21 risks:

| Root cause | Risks generated |
|---|---|
| **Gate scope narrower than gate claim** | R-02, R-03, R-04, R-08, R-13, R-15 |
| **Derived state not re-anchored after source change** | R-01, R-09, R-12, R-14 |
| **Control plane specified but unbuilt** | R-05, R-07, R-10, R-11 |

Addressing these three causes — rather than the 21 symptoms — is the efficient Wave-2 entry
condition. Each has a located owner and none requires architectural change.

## Residual risk after remediation of B-1…B-4

| Residual | Rating |
|---|---|
| R-06 ratification vacancy (B-5) | **HIGH — irreducible internally** |
| R-07 unimplemented control plane | **HIGH — Wave-3 scope by design** |
| R-05 identity merge hazard | **MEDIUM — requires an explicit decision** |
| all others | LOW–MEDIUM, mechanically closable |
