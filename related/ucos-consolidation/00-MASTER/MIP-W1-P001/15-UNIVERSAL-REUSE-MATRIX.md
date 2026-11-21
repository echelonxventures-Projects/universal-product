# 15 — Universal Reuse Matrix

**Anchor** `c6c20fb` · **Canonical dispositions** `intelligence/UCOS-RIE-CAPABILITY-CATALOG.json`,
`00-MASTER/UCIC-001-UNIVERSAL-CAPABILITY-IMPLEMENTATION-CONTRACT.md`

---

## 1 · Declared reuse disposition — all 66 capabilities

| Disposition | Capabilities | Meaning | Replacement prohibited |
|---|---|---|---|
| `REUSE/COMPOSE` | **28** | compose as-is into new capability (all of `platform/`) | yes |
| `REUSE/EXTEND` | **19** | extend in place (EC-3 bands, intelligence, automation, MCS) | no |
| `REUSE_AS_IS/COMPOSE` | **17** | consume without modification (all of `engine/`) | yes |
| `REALIZE_BY_COMPOSITION` | **2** | realize from existing parts, write nothing new (CIOA, CCE) | no |
| **REPLACE / REWRITE / FORK** | **0** | — | — |

**45 of 66 (68%) are marked `replacement_prohibited`.** No capability anywhere carries a disposition
that permits rewriting. This is the strongest reuse posture measurable in a codebase of this size,
and it is enforced: RIB `DUP-CAPABILITY` = 0, `DUP-INTERFACE` = 0, `DUP-RUNTIME` = 0.

## 2 · Existing reusable capabilities — the reuse inventory

### Tier 1 — consume as-is, do not modify (17)

`engine/` EC-1, **CERTIFIED**, 52,668 LOC, 1,567 test functions, inside the coverage gate.

| Reusable for | Capability |
|---|---|
| Registry access | `engine.registry` (read-only adapter) |
| Graph / traceability | `engine.graph` |
| Determinism | `engine.determinism` (double-build, fail-on-divergence) |
| Discovery | `engine.discovery` |
| Compilation | `engine.compiler` |
| Runtime assembly | `engine.runtime` |
| Blueprint factory | `engine.factory` |
| Validation | `engine.validation` |
| Certification | `engine.certification`, `engine.universal_certification` |
| Acceptance | `engine.acceptance` |
| Governance pipeline | `engine.governance` |
| Knowledge & decisions | `engine.knowledge` |
| Ontology / taxonomy | `engine.context` |
| Foundation primitives | `engine.foundation` |

Every Wave-2 kernel concern already has an EC-1 owner. **Wave-2 should compose these, not
re-implement them.**

### Tier 2 — compose (28)

`platform/` EC-2, **CLOSED/FROZEN**, 87,400 LOC, 2,797 test functions.

High-leverage compose targets:

| Capability | Dependents | In coverage gate |
|---|---|---|
| `platform.observability` | **16** | **no** |
| `platform.universal_provider` | 2 | **no** |
| `platform.measurement` (UCOS-UMA-001 — health/gaps) | — | yes |
| `platform.universal_validation` | — | yes |
| `platform.repository_operations` | — | yes |
| `platform.validation_intelligence` | — | yes |
| `platform.runtime_platform` | — | yes |
| `platform.identity`, `platform.security`, `platform.certification` | — | yes |

### Tier 3 — extend (19)

EC-3 bands (8), intelligence (7), automation (3), MCS (1). Extension is permitted; replacement is not
prohibited. These are the correct surfaces for Wave-2 additive work.

## 3 · Code-reuse patterns already established

### 3.1 The EC-3 six-aspect module pattern — the strongest pattern in the codebase

Every band realizes every concern as six sibling modules:

```
<concern>.py  ·  <concern>_meta.py  ·  <concern>_realize.py
<concern>_validation.py  ·  <concern>_certification.py  ·  <concern>_traceability.py
```

| Band | Concerns | Modules | LOC | Tests |
|---|---|---|---|---|
| `data/` (Band 10) | ~12 | 73 | 23,577 | 887 |
| `service/` (Band 11) | ~13 | 79 | 20,464 | 1,038 |
| `application/` (Band 12) | ~11 | 67 | 23,741 | 1,082 |
| `infrastructure/` (Band 13) | ~11 | 67 | 22,599 | 821 |

**~47 concerns × 6 aspects × 4 bands.** The pattern is uniform enough to be **template-generatable** —
and `05-GENERATION/` already contains six universal generation frameworks (API, Application, Data,
Event, Service, Workflow) plus a generation constitution, and `platform.generation` (RC-40) is an
implemented capability.

**Highest-value consolidation opportunity in the repository:** the six-aspect pattern is currently
hand-replicated across 286 modules and 90,381 LOC. It should be *generated* from the located
generation framework. That is a Wave-3 opportunity, not a Wave-1 action.

### 3.2 The band instrument pattern

`-001` Constitution → `-002` Theory → `-003` Ontology → `-004` Taxonomy → `-005` Meta-Model →
`-006…-014` domain architectures → `-015` Freeze → `-016` Readiness → `-017` Completion →
`-018` Master Registry.

Applied identically across Runtime, Platform, Data, Service, Application, Infrastructure —
**6 of 7 bands complete**. `14-SECURITY` implements only `-001…-004`.

**Consolidation opportunity:** `14-SECURITY` needs 14 instruments. Every one has six precedents to
template from. This is the cheapest large gap in the corpus to close.

### 3.3 The derived-truth programme pattern

Eight programmes follow one identical contract — `AUTHORITY = NONE (DERIVED TRUTH)`, deterministic
regeneration, own-memory write scope, fail-closed gate, `--gate` / `--self` modes, sealed output:

| Programme | Engine | Gate | Seal |
|---|---|---|---|
| `UCCEP-000000` | `uccep_engine.py` | aggregate (14 gates) | `12a33bff8c2d1778` |
| `UCOS-RIB-001` | `rib_engine.py` | 12 gates | `3ba75cb6d9965869` |
| `UAKOS-CLOSURE-002` | 3 engines | 3 gates | `5f60ff67b87c7601`, `0d816d967cec` |
| `UCDA-000001` | `ucda_engine.py` | Implementation Evidence Gate | — |
| `UEI-000001` | — | Evolution Intelligence Gate | — |
| `UER-000001` | — | Execution Resilience Gate | — |
| `URRC-000001` | — | RRC Gate | — |
| `UCOS-RIE-001` | `intelligence/rie` | determinism check | content hashes |

**This pattern is the repository's principal reusable engineering asset.** Any Wave-2 programme
should instantiate it rather than invent a new shape. Note that `UCCEP` extends rather than replaces:
it binds every located gate through `uccep-bindings.json` and required **no change to any engine** to
add one.

## 4 · Knowledge reuse

| Reusable knowledge asset | Volume | Reuse mode |
|---|---|---|
| Typed relationship graph | 12,851 edges · 16 types | query substrate for any new programme |
| Concept register | 437 homed concepts · 26 families · 4 dispositions | classification substrate |
| Co-occurrence graph | 437 nodes · 92,717 edges | semantic-equivalence substrate |
| Change / lineage ledger | 1,363 events · 1,204 lineage chains | provenance substrate |
| JSON schemas | 19 | structural contracts |
| Reference architectures | 7 | design templates |
| Generation frameworks | 7 | code templates |
| Canonical catalogs | 7 | API/App/Data/Event/Runtime/Service/Workflow inventories |
| Digital twin | 8 subjects · 8 dimensions | state projection |
| Universal catalogs | Capability, Component, Domain, Universe | 4 in `02-MASTER/` |

## 5 · Architecture reuse

| Asset | Reuse |
|---|---|
| 11-layer layered model | binding constraint for every new capability; acyclicity is gated |
| CEP 11-constitution function decomposition | each constitutional function has exactly one owner — extend by amendment (`CEP-009`), never by parallel instrument |
| `UCIC-001` Universal Capability Implementation Contract | the governing instrument for capability disposition; already the authority RIB binds |
| Ordered total disposition rule set | 11 rules; every capability disposition is **computed**, never asserted |
| Forbidden-write-prefix discipline | each derived programme declares the prefixes it may not write; enforced by `CK-SELF-WRITE-SCOPE` |
| Non-derivable declaration (`ND-01/02/03`) | the practice of declaring an unmeasurable fact rather than fabricating it |

## 6 · Duplicate implementations — measured

| Class | Count | Blocking | Determination |
|---|---|---|---|
| `DUP-CAPABILITY` | **0** | yes | no two catalogue records resolve to one unit |
| `DUP-INTERFACE` | **0** | yes | no two entry points resolve to one unit |
| `DUP-RUNTIME` | **0** | yes | no two units claim one canonical location |
| `DUP-REGISTRY` | **0** | yes | no unintended content duplication |
| `DUP-CONSTITUTION` | **0** | yes | no two constitutional instruments share a content hash |
| `DUP-KNOWLEDGE` | **0** | yes | no concept in two canonical homes |
| Content-hash duplicate groups (measured over 1,204) | **2** | no | both are the declared freeze-boundary pair |
| `DUP-NAME` cross-layer | **4** | no | `certification`, `foundation`, `validation`, `identity` under both `engine/` and `platform/` — deliberate layering |
| `MULTI-ENGINE PROGRAMME` | **1** | no | `UAKOS-CLOSURE-002` runs 3 engines |

**There is no duplicate implementation in this repository.** For 246,066 LOC and 1,204 registered
artifacts, that is a genuinely unusual result and it is gate-verified.

## 7 · Consolidation opportunities (ranked)

| # | Opportunity | Basis | Value | Wave |
|---|---|---|---|---|
| 1 | **Generate the EC-3 six-aspect modules** from `05-GENERATION/` + `platform.generation` instead of hand-replicating | 286 modules · 90,381 LOC follow one exact template | very high | 3 |
| 2 | **Template `14-SECURITY-005…018`** from the six completed band precedents | 14 instruments missing, 6 precedents available | high | 2 |
| 3 | **Bind the 969 unlinked evidence artefacts** (490 evidence + 433 certification + 46 completion reports) into the traceability spine | evidence exists, binding does not; closes B-3 without authoring new evidence | very high | 2 |
| 4 | **Extend `pyproject.toml` scope** to the 6 uncovered roots and 12 uncovered subpackages | closes B-4 by configuration, adds no code | very high | 2 |
| 5 | **Instantiate the derived-truth programme pattern** for any new Wave-2 programme | 8 working precedents, one contract | high | 2 |
| 6 | **Reuse `UCCEP` binding declaration** to add gates without touching engines | `uccep-bindings.json` — zero-enumeration proven by `CK-SELF-NO-ENUMERATION` | high | 2 |
| 7 | **Consolidate `01-WORKING/ONTOLOGY-REGISTER.md` + `CONST-11` glossary** into a canonical dictionary | closes `G-DICT-1`; both inputs exist | medium | 2 |
| 8 | **Collapse the freeze-boundary copy** — single-source `SOURCE-FILES/HASHES.txt` | 2 duplicate pairs | low | 2 |
| 9 | **Retire `engine/identity/`** (only `__pycache__`) | residual empty package | trivial | 2 |
| 10 | **Realize CIOA/CCE by composition** as their disposition already mandates (`REALIZE_BY_COMPOSITION`) | substrate present per AEOS `ready_because` | very high | 3 |

## 8 · Reuse matrix verdict

| Criterion | Verdict |
|---|---|
| Every reuse opportunity identified | **PASS** — 66 capabilities dispositioned, 10 consolidation opportunities ranked |
| Zero duplicate implementations | **PASS** — all 6 blocking duplicate classes = 0 |
| Reuse disposition computed rather than asserted | **PASS** — 11-rule ordered total rule set |
| Existing reusable capabilities catalogued | **PASS** — 3 tiers, 64 built capabilities |
| Code / knowledge / architecture reuse patterns identified | **PASS** — 3 code patterns, 10 knowledge assets, 6 architecture assets |
| Reuse enforced against replacement | **PASS** — 45/66 replacement-prohibited; 0 REPLACE/REWRITE dispositions |
| Highest-value consolidation already exploited | **FAIL** — the six-aspect pattern is hand-replicated across 90,381 LOC while the generation framework sits unused |
