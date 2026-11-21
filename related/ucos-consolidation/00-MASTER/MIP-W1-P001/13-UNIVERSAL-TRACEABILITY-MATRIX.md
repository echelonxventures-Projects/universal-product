# 13 — Universal Traceability Matrix

**Anchor** `c6c20fb` · **Canonical owner of the obligation** `00-CEP/CEP-008` (Constitutional Evidence
& Traceability Constitution) · **Measured over** 1,204 registered artifacts × 13 declared dimensions

---

## 1 · Determination

> **The traceability spine is effectively absent.** Mean population across 13 dimensions is **2.2%**.
> Ten of thirteen dimensions are at **0.0%** — not sparse, empty. Vision → Runtime traceability
> **cannot be verified** from the registry at this anchor. This is blocker **B-3** and the single
> largest measured constitutional gap in the repository.

## 2 · Measured population, per dimension

| # | Dimension | Populated | of 1,204 | Verdict |
|---|---|---|---|---|
| 1 | `requirement` | 80 | **6.6%** | CRITICAL |
| 2 | `architecture` | 251 | **20.8%** | CRITICAL |
| 3 | `design` | 0 | **0.0%** | **ABSENT** |
| 4 | `implementation` | 17 | **1.4%** | CRITICAL |
| 5 | `source_code` | 0 | **0.0%** | **ABSENT** |
| 6 | `unit_test` | 0 | **0.0%** | **ABSENT** |
| 7 | `integration_test` | 0 | **0.0%** | **ABSENT** |
| 8 | `functional_test` | 0 | **0.0%** | **ABSENT** |
| 9 | `security_test` | 0 | **0.0%** | **ABSENT** |
| 10 | `certification` | 0 | **0.0%** | **ABSENT** |
| 11 | `deployment` | 0 | **0.0%** | **ABSENT** |
| 12 | `production` | 0 | **0.0%** | **ABSENT** |
| 13 | `operations` | 0 | **0.0%** | **ABSENT** |
| | **Mean** | | **2.2%** | |

Artifacts with a `traceability` object present: 1,204 / 1,204 (100%). The **structure** is universal;
the **content** is not.

## 3 · Independent corroboration — three engines agreeing

| Engine | Shares code with others | Reported |
|---|---|---|
| Wave-1 direct measurement (this output) | — | 13 dimensions, mean 2.2% populated |
| `platform.measurement.cli gaps` (UCOS-UMA-001) | no | `total=1198`, `by_type={'incomplete-traceability': 1198}`, `structural_count=0`; `health --strict` exits 1 |
| REG-AUTO-001 `ukb` build (UMB-IMP-002) | no | 272 / 1,199 artifacts carry a populated traceability spine = **22.7%** |
| `UAKOS-CLOSURE-002` doc 68 | no | traceability ~21% |

Three independent measurements converge on the same magnitude. The discrepancy between "2.2% mean
per-dimension" and "22.7% carry *any* spine" is not a contradiction — it is the shape of the gap:
about a fifth of artifacts have *one or two* dimensions filled (almost always `architecture`), and
essentially none have a complete chain.

## 4 · The mandated chain, evaluated link by link

```
Vision → Objectives → Requirements → Capabilities → Architecture → Repository
      → Implementation → Validation → Certification → Runtime → Knowledge
```

| Link | Traceable? | Evidence | Verdict |
|---|---|---|---|
| **Vision → Objectives** | **partial** | `00-SOURCE/VISION/` (3 docx) + `VSN` category (3 artifacts) + MIP v2 (28 universes · 25 directives). No machine-readable vision→objective edge type exists. | **BROKEN — no edge** |
| **Objectives → Requirements** | **partial** | `requirement` dimension populated for 80 artifacts (6.6%) | **BROKEN — 93.4% missing** |
| **Requirements → Capabilities** | **yes** | 66 capabilities, 100% evidence present, RIB GATE-07 PASS: every capability record resolves to a unit and every unit is covered | **INTACT** |
| **Capabilities → Architecture** | **partial** | `architecture` dimension 20.8%; band instrument pattern is complete for 6 of 7 bands | **BROKEN — 79.2% missing** |
| **Architecture → Repository** | **yes** | 1,204/1,204 artifact paths resolve; 236 units all owned; `GAP-OWNER` = 0 | **INTACT** |
| **Repository → Implementation** | **partial** | `implementation` dimension 1.4%; but `implementation` progress dimension = 100% IMPLEMENTED and 246,066 LOC exists | **BROKEN in registry, INTACT in fact** |
| **Implementation → Validation** | **partial** | 8,307 test functions exist; `unit_test`/`integration_test`/`functional_test`/`security_test` dimensions all **0.0%**; RIB `GAP-VERIFICATION` = 207 units | **BROKEN — no edge** |
| **Validation → Certification** | **partial** | `certification.json` verdict CERTIFIED 10/10 domains; `certification` dimension **0.0%**; RIB `GAP-CERTIFICATION` = 170 units | **BROKEN — no edge** |
| **Certification → Runtime** | **no** | `deployment` 0.0%, `production` 0.0%, `operations` 0.0%; progress dimensions: execution 0%, release 0%, production BLOCKED, operational BLOCKED | **BROKEN — absent** |
| **Runtime → Knowledge** | **partial** | closure feeds back into the corpus (437 concepts homed), but no runtime signal reaches it — twin/signals stale since 2026-07-16/17 | **BROKEN — stale** |

**Two of ten links are intact. Eight are broken.** The two intact links
(Requirements→Capabilities, Architecture→Repository) are precisely the two that a *gate* enforces —
RIB GATE-07 and GATE-11. Every link with no gate is broken. That correlation is the actionable
finding.

## 5 · Where traceability *does* exist

Traceability is not absent from the repository — it is absent from the **registry**. It exists in
forms no gate reads as a trace:

| Form | Volume | Machine-readable trace edge? |
|---|---|---|
| `Traces-To` / `Traced-From` graph edges | **5 + 5** | yes — 0.04% of the graph |
| `Implements` / `Implemented-By` edges | 48 + 48 | partially |
| `Authorized-By` / `Authorizes` edges | 99 + 99 | authority chain, not trace |
| Band unit completion reports | **46** (B10: 11 · B11: 13 · B12: 11 · B13: 11) | **no** — prose |
| `_evidence/` artefacts | **490** | **no** — files, unlinked |
| Certification instruments | 433 | **no** — prose |
| Determination instruments | 134 | **no** — prose |
| Change events | 1,363 | temporal lineage, not requirement trace |
| Coverage report | `coverage.xml` (1.5 MB) | code→test, not artifact→test |

The repository holds **969 evidence-bearing artefacts** (490 evidence files + 433 certification +
46 completion reports) that are **not bound to any registered artifact's traceability field**. The
evidence exists; the binding does not.

## 6 · RIB traceability-adjacent gaps

| Gap ID | Class | Count | Subject |
|---|---|---|---|
| `GAP-EVIDENCE` | MISSING EVIDENCE | **228** | units with no bound evidence |
| `GAP-VERIFICATION` | MISSING VALIDATION | **207** | units with no validation obligation met |
| `GAP-CERTIFICATION` | MISSING CERTIFICATION | **170** | units with no certification record |
| `GAP-COVERAGE` | MISSING VERIFICATION | **26** | units with no coverage measurement — includes `application`, `data`, `engine`, `infrastructure`, `intelligence*`, `platform*`, `service` and their test packages |
| `GAP-OWNER` | MISSING OWNER | 0 | — |
| `GAP-CAPABILITY` / `GAP-REGISTRY` / `GAP-RUNTIME` / `GAP-DEAD-ENGINE` | — | 0 | — |

Note the shape: **ownership is complete (0), evidence binding is not (228).** The corpus knows who
owns everything and cannot prove what anything satisfies.

## 7 · Governance status of the gap

| Field | Value |
|---|---|
| Finding | `UCCEP-F-002` |
| Class | MEASURED-GOVERNANCE-GAP |
| Disposition | **REGISTERED** |
| Blocks certification | **YES** |
| Owner | `00-CEP/CEP-008` · `platform/measurement` (UCOS-UMA-001) · `engine/graph` |
| Violates | PR-13 Universal Traceability · IV-07 Traceable |
| Work package | `WP-UCCEP-002` — explicit authorization required |
| Acceptance | `platform.measurement.cli health --strict` exits 0; `CK-HEALTH` ceases to be advisory |
| Gate treatment | `CK-HEALTH` = **advisory FAIL** → `G-11` Certification Gate = PASS-WITH-ADVISORY |

The gap is correctly recorded as Repository Truth rather than left as an unread red exit code. But
note the consequence of the advisory demotion: **the largest constitutional gap in the repository
does not block any gate.** `G-11` passes with advisory; `PROGRAM-000007`, `-000012`, `-000014` all
return PASS-WITH-ADVISORY. Only `certification_ceiling` records it.

## 8 · Traceability matrix verdict

| Criterion | Verdict |
|---|---|
| Traceability structure present on every artifact | **PASS** — 1,204/1,204 |
| Requirements → Capabilities traceable | **PASS** — gated by RIB GATE-07 |
| Architecture → Repository traceable | **PASS** — gated by RIB GATE-11 |
| Every trace verified across the full chain | **FAIL** — 8 of 10 links broken |
| Design / source-code / test / certification / runtime traces present | **FAIL** — 10 of 13 dimensions at 0.0% |
| Evidence bound to artifacts | **FAIL** — 969 evidence artefacts unbound; `GAP-EVIDENCE` = 228 |
| Traceability gap blocks certification in practice | **FAIL** — demoted to advisory |

**The success criterion "Every trace verified" is NOT met.**
