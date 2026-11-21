# 16 — Gap Analysis

**Anchor** `c6c20fb` · every gap is measured, attributed to a located owner, and classed as
BLOCKING / MAJOR / MINOR

---

## Blocking gaps

### B-1 · Registry integrity is broken at the anchor commit

| Field | Value |
|---|---|
| Class | BROKEN EVIDENCE BINDING |
| Owner | `00-BOOK/tools/register.sh` (REG-AUTO-001 §16.3) · repository operator |
| Gate | `CK-REG-DRIFT` exit **3** → `G-07` Registry Gate **FAIL** → `UCCEP-000000` **NOT-CERTIFIED** |
| Related finding | `UCCEP-F-007` (declared non-blocking — **misclassified**) |
| Reversible | yes, by one atomic re-registration commit |

**Proof.** A detached `git worktree` was created at `c6c20fb` with a verified **100% clean tree**
(`git status --porcelain` → 0 entries). `bash 00-BOOK/tools/register.sh --guard` reported:

```
ENFORCEMENT PASSED — no unregistered or invalid artifact can silently enter the corpus.
TRANSACTION COMPLETE — every artifact on disk is registered, classified, validated, and synchronized.
-- Guard: checking committed synchronized state for drift
REGISTRATION DRIFT DETECTED — synchronized state was not committed:
 M 00-BOOK/DATA/artifacts.json          M 00-BOOK/DATA/id-ledger.json
 M 00-BOOK/DATA/certification.json      M 00-BOOK/REGISTRIES/CERTIFICATION-REGISTRY.md
 M 00-BOOK/DATA/change-ledger.json      M 00-BOOK/REGISTRIES/CHANGE-VERSION-LINEAGE-REGISTRY.md
An artifact was created or modified without committing its registration.
```

**Root cause, exactly.** Commit `b47f5b9` (2026-07-28 00:57 — *"UCOS-RIE-001: regenerate the
capability catalogue at the committed anchor"*) rewrote ten derived artifacts under `intelligence/`.
`00-BOOK/DATA/artifacts.json` was last registered at `898ef8d` (2026-07-27 22:01). Source and
projections were committed separately, violating REG-AUTO-001's own rule that source is never split
from projections.

**Measured consequence.** Of the ten recorded `content_hash` values at HEAD, **0 of 10 match the
committed bytes**; after re-registration **10 of 10** match (full table in output 06 §5.5). The
Universal Artifact Registry's evidence binding for the entire derived-intelligence plane is stale.

**Why this is blocking rather than cosmetic.** `content_hash` is the mechanism by which the registry
asserts *what an artifact is*. Ten artifacts — including the capability catalogue that RIB, UCCEP and
this programme all bind by pointer — are bound to content that no longer exists. Any freeze taken
now would seal a provably incorrect evidence binding into the constitutional record.

**Remediation.** Run `make repo-ops` (or `bash 00-BOOK/tools/register.sh`), stage the regenerated
`00-BOOK/DATA/` and `00-BOOK/REGISTRIES/` outputs **together with** any source change, and commit
atomically. Then reclassify `UCCEP-F-007` from non-blocking to blocking in `uccep-bindings.json`,
since its own acceptance criterion is the one that fails.

**Standing prevention.** The coupling `intelligence/` regeneration → registry re-registration is real
and unenforced. Either the RIE regeneration path must invoke registration, or a pre-commit check must
refuse a commit that touches a registered path without its projections.

---

### B-2 · Knowledge assimilation is not closed against the source corpus

| Field | Value |
|---|---|
| Class | UNASSIMILATED KNOWLEDGE + BLIND GATE |
| Owner | `00-MASTER/UAKOS-CLOSURE-002` (FROZEN spec) → successor `UAKOS-CLOSURE-003/006` · `.kiro/hooks/uakos-closure-002.json` |
| Gate | `CK-CLOSURE-P1` PASS at repo scope · **exit 1 at true scope** |
| Related findings | `UCCEP-F-008` (CF-01/CF-03) |

| Scope | Corpus files | Concepts | Gaps | Determination |
|---|---|---|---|---|
| Repository-only (standing gate) | 0 | 437 | 0 | CLOSED |
| **Corpus-inclusive** | **1,944** | **528** | **91** | **NOT-CLOSED** |

**The 91.** All family `UCOS-COMP`, identifiers `UCOS-COMP-001001`…`UCOS-COMP-009009`, disposition
`UNCLASSIFIED`, zero canonical homes. Sourced from `UCOS Ω∞ - Universal Civilization Operating
System_Part-001(Phase-000-019).docx` and `UCOS Ω∞ - Universal Platform.docx` plus eight derived
extraction outputs. The repository homes only `UCOS-COMP-000000` and `-000001`; the entire component
decomposition series is unassimilated — **95% of the family**.

**Why the standing gate cannot see it.** `.kiro/hooks/uakos-closure-002.json` invokes the engine with
`CLOSURE_SKIP_CORPUS=1`; `closure_engine.py:120` short-circuits the corpus scan on that variable.
The gate measures the repository against itself, so a `gaps=0` verdict is structurally guaranteed and
carries no information about assimilation.

**Remediation.** Home the 91 concepts (classify → destination → owner → disposition), then remove
`CLOSURE_SKIP_CORPUS=1` from the standing hook so the gate measures the proposition it claims. If the
corpus must stay out of the fast session tier for performance, the corpus-inclusive run belongs in
CI — but the *verdict text* must then state its scope.

---

### B-3 · The traceability spine is effectively absent

| Field | Value |
|---|---|
| Class | MEASURED GOVERNANCE GAP |
| Owner | `00-CEP/CEP-008` · `platform/measurement` (UCOS-UMA-001) · `engine/graph` |
| Gate | `CK-HEALTH` **advisory** FAIL → `G-11` PASS-WITH-ADVISORY — **does not block** |
| Finding / WP | `UCCEP-F-002` / `WP-UCCEP-002` |

Mean population **2.2%** over 1,204 artifacts × 13 dimensions. Ten dimensions at **0.0%** (design,
source_code, unit_test, integration_test, functional_test, security_test, certification, deployment,
production, operations). 8 of 10 mandated chain links broken. `Traces-To` edges: **5 of 12,851**.

Corroborated by three independent engines (output 13 §3).

**The compounding gap:** 969 evidence-bearing artefacts exist (490 `_evidence/` files, 433
certification instruments, 46 band completion reports) and **none is bound** to any registered
artifact's traceability field. The evidence was produced; the binding was never made. Closing B-3 is
therefore substantially a *binding* exercise, not an authoring exercise.

**Secondary gap:** the largest constitutional gap in the repository blocks no gate. Advisory
demotion was the right call while the number was unread; it is the wrong call now that it is
measured three ways.

---

### B-4 · Canonical verification covers 56.9% of the code

| Field | Value |
|---|---|
| Class | SCOPE GAP — DECLARED, NOT DEFECTIVE |
| Owner | `pyproject.toml` · `Makefile` (`lint` target) |
| Gate | `CK-VERIFY` **PASS** — over the declared scope only |

Declared scope: `testpaths = ["engine/tests", "platform/tests"]`; coverage source = 34 packages;
`packages.find include = ["engine*", "platform*"]`; `make lint` = `ruff check engine platform`.

| | In gate | Outside gate |
|---|---|---|
| LOC | 140,068 (**56.9%**) | 105,998 (**43.1%**) |
| Test functions | 4,364 (**52.5%**) | 3,943 (**47.5%**) |

**Entirely outside:** `data/` (23,577 LOC · 887 tests) · `service/` (20,464 · 1,038) ·
`application/` (23,741 · 1,082) · `infrastructure/` (22,599 · 821) · `intelligence/` (15,617 · 115) ·
`realization/` (1,314 · 0).

**Also outside the coverage source (12 subpackages):** `platform.observability` (16 dependents),
`platform.workspace`, `platform.portal`, `platform.providers`, `platform.universal_provider`,
`platform.repository_intelligence`, `platform.commercial_intelligence`, `intelligence.kernel`,
`intelligence.publication`, `intelligence.realization`, `intelligence.research`, `intelligence.rie`.

**Sharpest instance:** `intelligence/` produces the derived truth that every governance
determination consumes — 15,617 LOC with **115 test functions** (0.0074 tests/LOC vs 0.032 for
`platform/`), zero coverage measurement, and no lint enforcement. The engines that compute the
verdicts are the least verified code in the repository.

**Remediation is configuration, not code.** Extend `testpaths`, coverage `source`, `packages.find`,
and the `lint` target. Expect initial failures — that is the point.

---

### B-5 · Standing constitutional vacancy — not remediable internally

| Field | Value |
|---|---|
| Class | STANDING CONSTITUTIONAL VACANCY |
| Owner | `00-CMG/CMG-000014` · `00-CEP/CEP-006` |
| Finding | `UCCEP-F-004` |
| Remediable inside the corpus | **NO** |

`CMG-000001` is PROVISIONAL, constitutional Tier **T1 is VACANT**, and no located authority is
competent to ratify. `cmg-gate`: 0 findings, `READY-PROVISIONAL`, 1 vacancy, 9 gaps, 7 open questions
(6 open).

**Consequence:** the maximum attainable verdict anywhere in this repository is
**CERTIFIED-PROVISIONAL**. `UCCEP-000000` correctly refuses to assert more even with all gates green.

**Wave-1 takes no action.** Manufacturing a ratifying authority from inside the corpus would create
the parallel constitution `CMG-000001` exists to prevent. Resolution requires an authority external
to the artefact set via the `CEP-006` route.

---

## Major gaps

| ID | Gap | Measure | Owner |
|---|---|---|---|
| **G-SPINE-1** | AEOS execution spine absent — 12 declared gaps, 4 HIGH (`G-01` executable CCE, `G-02` executable CIOA, `G-03` scheduler, `G-09` AI adapter layer) | 0 of 12 implemented | AEOS (separately authorized) |
| **G-SPINE-2** | CIOA and CCE are layer 5 of an 11-layer stack and exist only as prose | 2 capabilities `PLANNED` | `02-MASTER/UCOS-COMP-000000/-000001` |
| **G-SEC-1** | `14-SECURITY` truncated at `-004`; every peer band reaches `-018` | 14 instruments absent, incl. Master Registry | `SECURITY-GOV-000` |
| **G-DICT-1** | No universal dictionary, term registry or controlled vocabulary at platform scope | 10 de-facto vocabularies undeclared; 1 glossary buried in a programme; 1 register in `01-WORKING/` | unowned |
| **G-TEST-1** | 4 lifecycle test dimensions never started | functional / integration / performance testing + execution all 0% | `00-CEP/CEP-004` |
| **G-RT-1** | Runtime / production dimensions absent or blocked | deployment 50% (stale), release 0%, production BLOCKED, operational BLOCKED, build BLOCKED, security BLOCKED | connectors + `08-RUNTIME` |
| **G-STALE-1** | 6 of 15 progress dimensions stale; twin (2026-07-16), signals (2026-07-17), connector cursors (2026-07-15) | 4 dimensions report BLOCKED from staleness alone, not measured failure | UMB / operator |
| **G-RIB-1** | Repository Integration Blueprint two commits stale — `head: bde5ffa`, `tracked_files: 4894` vs anchor `c6c20fb`, 4,895 | its 12 PASS verdicts describe a prior state | `UCOS-RIB-001` |
| **G-USIS-1** | USIS: 36 instruments, 21 zones, 12 registries, **no code root** | specification-only programme | `USIS-GOV-000` |
| **G-DEP-1** | `engine` — the CERTIFIED root — has no measured dependency edge in either direction | RIB `GAP-DEPENDENCY` = 1 | `engine/` · `engine.graph` |
| **G-EVID-1** | RIB unit-level obligations unmet: evidence 228 · validation 207 · certification 170 · coverage 26 | of 236 units | per-unit owners |

## Minor gaps

| ID | Gap | Measure |
|---|---|---|
| **G-ID-1** | No UUID on any object; sequential category cursors are a merge hazard under parallel development; identity is repository-scoped while the architecture declares 28 federated universes | 0 of 1,204 |
| **G-ID-2** | `native_id` null for 825 objects (68.5%); 7 collision groups / 22 objects (`EC2-CAP-SEC-001` ×7, `UCOS-COMP-000000` ×4, `EC2-EPIC-006` ×3) | — |
| **G-DOC-1** | `description` empty for every registered object | 0 of 1,204 |
| **G-VER-1** | `version` = `1.0.0` for every object — non-differentiating; real lineage only in `change-ledger.json` | 1,204 of 1,204 |
| **G-DEP-2** | Programme-scope 2-cycles `ARCH↔CAT` and `CEP↔IMP`; no gate asserts acyclicity at programme granularity | 2 |
| **G-DEP-3** | 77 `Depends-On` edges have no `Required-By` inverse — reverse-impact queries incomplete | 4,774 vs 4,697 |
| **G-DEP-4** | 1,014 of 1,204 artifacts declare no dependencies; edge store and artifact records are not cross-validated | 84.2% |
| **G-VOL-1** | 62.0% of artifacts default to `VOL-000`; `VOL-013` and `VOL-014` declared but empty | — |
| **G-CAT-1** | 4 category labels truncated at 12 chars (`INFRASTRUCTU`, `IMPLEMENTATI`, `ARCHITECTURA`); several unexpanded abbreviations | 94 categories |
| **G-VAL-1** | `ukb validate` silently degrades to structural-only when `jsonschema` absent and still exits 0; CI installs it with `\|\| true` (`UCCEP-F-006`) | — |
| **G-CLOS-1** | `phase3_engine.py` returns a constant `NOT-CLOSED` with no reachable PASS state, contradicting `closure.json`'s `CLOSED` in the same directory (`UCCEP-F-001`) | — |
| **G-REG-1** | `UCCEP-F-003` remains in `certification_ceiling` as blocking although it is factually discharged (validator now fails closed; cycle eliminated at `6dae436`) | register staleness |
| **G-DUP-1** | Freeze-boundary copy: `SOURCE-FILES.txt` / `SOURCE-HASHES.txt` duplicated between `00-SOURCE-MANIFEST/` and `99-FREEZE/` | 2 pairs |
| **G-DEAD-1** | `engine/identity/` contains only `__pycache__` — residual empty package, absent from the capability catalog | 1 |
| **G-ORPH-1** | 1 isolated node in the 437-node co-occurrence graph | 1 |
| **G-HIDDEN-1** | Closure verdicts depend on an untracked, unversioned, unhashed external directory (`<repo>/../UCOS`, 6,332 files) | — |

## Gaps explicitly determined ABSENT (verified clean)

| Class | Count |
|---|---|
| Missing owner (`GAP-OWNER`) | 0 |
| Missing capability (`GAP-CAPABILITY`) | 0 |
| Missing registry (`GAP-REGISTRY`) | 0 |
| Missing runtime interface (`GAP-RUNTIME`) | 0 |
| Dead engine (`GAP-DEAD-ENGINE`) | 0 |
| Duplicate capability / interface / runtime / registry / constitution / knowledge | 0 each |
| Orphan units | 0 |
| Architectural (cross-unit) cycles | 0 |
| Typed `Depends-On` cycles | 0 |
| Unresolved / dangling / malformed dependency edges | 0 |
| Unregistered eligible artifacts | 0 |
| Unclassified artifacts | 0 |
| Artifact paths not resolving on disk | 0 |
| Duplicate `universal_id` | 0 |
| Unversioned artifacts | 0 |
| Merge conflicts / detached HEAD / broken symlinks / interrupted operations | 0 |

## Gap totals

| Severity | Count |
|---|---|
| BLOCKING | **5** (B-1…B-5; B-5 not internally remediable) |
| MAJOR | **11** |
| MINOR | **16** |
| Verified absent | 16 classes |

## Missing implementation planning

The mandated "missing implementation planning" gap resolves as follows: implementation planning
**exists and is extensive** — `UCOS-Ω∞-IMPLEMENTATION-MASTER-PLAN.md`, `04-IMPLEMENTATION-WAVES.md`,
`05-IMPLEMENTATION-ORDER.md`, `08-IMPLEMENTATION-READINESS-MATRIX.md`,
`09-IMPLEMENTATION-BACKLOG.md`, the RIB implementation queue (8 ranked units, `max_parallel` 26,
10-node critical path), and the 158 KB MIP v2. What is missing is **executable** planning: the
planning register that would drive it (`phase3.json`) contains 0 plans, 0 waves, 0 classes, 0
priorities and returns a constant verdict (`G-CLOS-1`). Planning is documented, not operative.
