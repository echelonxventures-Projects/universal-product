# UCOS Ω∞ — ASSIMILATION COVERAGE MATRIX

| Field | Value |
|---|---|
| ARTIFACT | `UCOS-OMEGA-INFINITY-ASSIMILATION-COVERAGE-MATRIX.md` |
| CLASSIFICATION | `EVIDENCE` — derived measurement register |
| AUTHORITY | **NONE — DERIVED TRUTH.** Legislates nothing, ratifies nothing, certifies nothing, assigns no ownership, allocates no identity, changes no certification state. Where this matrix and a located instrument differ, **the located instrument governs.** |
| DISPOSITION | **ASSIMILATION ONLY.** No artifact deleted, removed, renamed or merged. No code, configuration, registry or ledger modified. No identity minted. No ADR created. |
| COMPANION TO | `UCOS-OMEGA-INFINITY-ASSIMILATION-COVERAGE-DETERMINATION.md` (Parts I–XII) — the narrative and mechanism; this artifact is the item-level classification |
| BASELINE | HEAD `bae59755` · branch `integration/recovery-001` |
| MODE | Read-only |

---

## 0 — CLASSIFICATION VOCABULARY USED, AND ITS PROVENANCE

The directive supplies six tokens. **Five are the repository's own; one is not.** Disclosed rather than absorbed, because closure by assumption is forbidden.

| Token | Definition | Provenance |
|---|---|---|
| `CERTIFIED` | Implementation + executable evidence + validation passes | **Declared** — `UCOS-OMEGA-INFINITY-COMPLETE-REQUIREMENT-MASTER-INDEX.md:8`, "strict, one per requirement" |
| `IMPLEMENTED` | Implementation exists, evidence incomplete | same declaration |
| `VERIFIED` | Executable evidence exists and passes, but no certification instrument claims it | Directive token; the repository's nearest code peers are `GateStatus.PASS` and `M4 TEST-EVIDENCED` / `M5 VALIDATED-OR-VERIFIED` |
| `GOVERNED CLOSURE` | An approved decision exists; implementation is intentionally pending | same declaration. **Zero Python representation** — prose token only |
| `OPEN GAP` | No implementation and no approved decision | same declaration. **Zero Python representation** |
| `NOT YET ASSESSED` | Not measured in this or any located pass | **Not a repository token — zero occurrences repo-wide.** Mapped below to the repository's own words |

**`NOT YET ASSESSED` → the repository's own vocabulary**, so this matrix introduces no seventh vocabulary: `TruthClass.UNCLASSIFIED` (code, "an honest absence rather than defaulting a locator into Truth") · `ABSENT` (a declared-but-missing optional input) · `UNDECIDABLE` ("recorded as such, never guessed") · `WITHHELD` (deliberately not granted) · `FAULT` (no verdict reachable — distinct from a negative verdict).

**Plurality of verdict vocabularies is an adjudicated position, not a defect.** `PHASE-VERDICT-VOCABULARY-TAXONOMY-DETERMINATION.md` surveyed twelve certification surfaces and determined **(C) independent vocabularies with documented relationships**, rejecting both a universal taxonomy authority and a translation layer, because no consumer anywhere reads two surfaces' verdicts and reconciles them semantically — every cross-surface dependency is a process exit code. This matrix therefore classifies against the Master Index axis and **does not** attempt to map certification surfaces onto each other.

**Interpretation rule, binding on every count in this matrix.** No number here is a boundary. Each is a currently discovered population; the `Enum?` column states whether the code **enumerates** it as a closed set (a change requires a code edit) or **discovers** it as data (a change is a declaration edit).

---

## 1 — DIMENSION MATRIX (14 dimensions)

| # | Dimension | Class | Owner | Evidence (code) | Gate | Gap ref |
|---|---|---|---|---|---|---|
| 1 | Universal Infinite Expansion | **CERTIFIED** | `UISD-000001` | `engine/infinite_scope/{model,contract,gate}.py`; `LAW_CHECKS:796` binds 11 laws↔11 checks bijectively | `uisd-gate.yml` + `verify.sh:539`; **live exit 0 = OPEN** | `ISD-G-01`, `AD-G-01` |
| 2 | Universal Agnostic Architecture | **IMPLEMENTED** | `UAP-001` + `UPF-000001` | `uckp/persistence.py:101`; `platform/universal_provider/`; `provider/metatypes.py` | provider plane only (`uprf-gate.yml`) | self-disclosed in `adr/0021` |
| 3 | Universal Entity Model | **CERTIFIED** | `UCOS-UCOM-001` · `UOBC-000001` | `uckp/ucko.py` (33 facets total); `uckp/identity.py` (SUPREME); `object_birth/` | `verify.sh:502,435`; **live exit 0** | `G11` adoption |
| 4 | Universal Relationship Evolution | **VERIFIED** | `CEU-001` · `UCKP-ART-07` | `ceu/existence.py:918,951`; `ukip/relationships.py` | **none** — tests only | `ISD-G-04`, `P4-F-002` |
| 5 | Universal Context Evolution | **VERIFIED** | `UCXI-000001` | `engine/context/` (18 modules); `resolution.py:112,122,149` | **none** — tests only | `P4-F-009` |
| 6 | Universal Capability Evolution | **IMPLEMENTED** | `UCIC-001` · `UAUE-000001` · `URI-000001` | `uaue/controller.py:707,757`; `uckp/evolution.py:238`; `realization/` | `uaue`/`uaep`/`ufc`; **live exit 0** | `AEOS-001` AC-1…6 |
| 7 | Universal Knowledge Evolution | **CERTIFIED** | `UKIP` · `UCKP` · `USAF-001` | `knowledge/ukip/`; `platform/universal_assimilation/pipeline.py:112` | `assimilation-gate.yml` + `corpus-currency-gate.yml`; **live CLOSED gaps=0** | qualified — see §4 |
| 8 | Universal Memory Evolution | **GOVERNED CLOSURE** | `ULP Part 05` (`adr/0013`) | `lineage/memory.py`; `memory-layers.json` (7 layers as data) | none | `P4-F-002/006/008/009` |
| 9 | Universal Requirement Evolution | **IMPLEMENTED** | `UAKOS-CLOSURE-009` | `requirement_engine.py`; `uckp/evolution.py:138,163` | `closure009-gate.yml`; **live 25.5%, baseline WITHHELD** | `RU-G-01` |
| 10 | Universal Execution Governance | **CERTIFIED** (2 owners) | `UEG-000001` · `EPIC-RTE-002` | `execution_environment/`; `runtime/execution/` (23 modules) | `verify.sh` Stage 0; `determinism.yml`; **live exit 0** | UIEC controller = `OPEN GAP` |
| 11 | Universal Lifecycle Governance | **CERTIFIED** | `UCIC-001` → `UCL-000001` → Art 14 | `nucleus/lifecycle.py` (45 stages as data, `verify_manifest_alignment:204`) | `ucl-gate.yml` incl. `--check-no-parallel-authority` | 145 determinations unbound; dangling authority |
| 12 | Universal Verification Governance | **CERTIFIED** | `UVI-000001` | `verification_intelligence/selection.py:56,117`; `verification_impact/changes.py` | `ec1-ci.yml:151`; `uisd-gate.yml:260-282` | no `gate_mode` field |
| 13 | Universal Artifact Governance | **IMPLEMENTED** | generated-artifact registry · `UCOS-UGA-001` | `generated_artifacts.py:56-91,240,281`; `uga_engine.py` | `verify.sh` 6b + ~9 per-owner replay gates | drift gate not universal |
| 14 | Universal Mutation Governance | **IMPLEMENTED** | mutation-governance-boundary | `mutation_classification.py:403,415,427`; `frozen_paths.py`; `identity/policy.py` | `ec1-ci.yml:40,147` | **R-09 predicate absent — live finding** |

**Distribution:** `CERTIFIED` 7 · `IMPLEMENTED` 5 · `VERIFIED` 2 · `GOVERNED CLOSURE` 1 (dimension 8, whose partial state is constitutionally intended) · `OPEN GAP` 0 · `NOT YET ASSESSED` 0.

Note on 4 and 5: both hold complete, tested models but **no gate**. Under the strict Master Index reading they are `VERIFIED`, not `CERTIFIED` — executable evidence exists and passes, but no certification instrument claims them. This distinction is the matrix's most consequential judgement and is deliberately not softened.

---

## 2 — PHASE MATRIX (17 phases)

| Phase | Subject | Class | Basis |
|---|---|---|---|
| 1a | Infinite entity expansion | **CERTIFIED** | catch-all kind makes classification total (`BSP-L-02`); `declare_form` open; `test_unknown_entity_form…:29` |
| 1b | Infinite capability expansion | **IMPLEMENTED** | parts exist, pipeline unwired (§4.6) |
| 1c | Infinite context expansion | **VERIFIED** | `taxonomy.extend()` bounded open-world; `test_unknown_context_kind…:55` |
| 1d | Infinite relationship expansion | **VERIFIED** | `ISD-L-06` performs a live extension every run; `test_unknown_relationship_type…:77` |
| 1e | Infinite knowledge expansion | **CERTIFIED** | provenance chain hash-verified; gate-enforced closure |
| 1f | **Infinite intelligence expansion** | **GOVERNED CLOSURE** | `adr/0011` **Accepted**: self-learning/self-evolution "represented by existing canonical capability"; `test_unknown_intelligence_form…:188` |
| 2 | Agnostic architecture (7 categories) | **IMPLEMENTED** | 3 executable / 2 declaration / 2 no surface — §3 below |
| 3 | Universal entity + relationship model | **CERTIFIED** | one identity mint; relationship is a form of entity, not a second registry |
| 4 | Ownership and authority | **CERTIFIED** | ownership total (14/14); 4-tier authority uniform; two defects located |
| 5 | Temporal evolution | **IMPLEMENTED** | fail-closed-on-incomparable across 6 sites; validity in 1 of 4 relationship planes |
| 6 | **Truth, confidence, evidence** | **IMPLEMENTED** | 3 unmapped enums; **no confidence scale**; no uncertainty metric |
| 7 | Memory and knowledge | **GOVERNED CLOSURE** | store constitutionally forbidden (`UCI-001` XVI.5) |
| 8 | Requirement evolution | **IMPLEMENTED** | 25.5% assimilated, baseline WITHHELD |
| 9 | Execution governance | **CERTIFIED** | 5 declared modes; `UVI-L-01`/`L-04`/`L-05`/`L-06`/`L-08`; no cost cap by design |
| 10 | **Self-correction** | **CERTIFIED** | 4 report/act/gate triads; `convergence-gate` fails if a retired module reappears |
| 11 | **Composition and emergence** | **CERTIFIED** | kernel provably enum-free; 11 alien categories admitted with fingerprint unchanged |
| 12 | **Boundaries** | **IMPLEMENTED** | 10 executable kinds; `ISD-BND-01…07` uncomputed |
| 13 | **Unknown space** | **CERTIFIED** | two-sided rule; admission *measured* by 4 instruments, not asserted |
| 14 | **Knowledge-source boundary** | **IMPLEMENTED** | origin + lineage executable; confidence per source unscaled |
| 15a | Lifecycle chain — Intent → Certify | **CERTIFIED** | 45-node graph as data; manifest alignment fails closed |
| 15b | Lifecycle chain — Learn | **GOVERNED CLOSURE** | `adr/0011`; `ADAPTATION` left open as a named stage |
| 15c | Lifecycle chain — **Reason · Challenge · Predict · Simulate · Optimize** | **NOT YET ASSESSED** | nearest located: `superiority_engine.py` (`UNDECIDABLE`), `graph/architecture/impact.py`, `H-06-DECISION-IMPACT-SIMULATION-DETERMINATION.md`, `make verify-cost-model` (ungated). No forward-state projector and no inference engine located. **Not absent, not proven** |
| 16 | **Measurement model** | **IMPLEMENTED** | 4 closed measurement kinds; **2 unreconciled maturity models**; UFC-16 uncodified |
| 17 | **Final classification** | **IMPLEMENTED** | canonical 4-token vocabulary declared but **prose-only** |

---

## 3 — SEVEN-CATEGORY NEUTRALITY MATRIX

| # | Category | Class | Executable check | Surface exists? |
|---|---|---|---|---|
| 1 | ENGINEERING | **CERTIFIED** | `ISD-L-09` — deps must be empty, no version ceiling, pins disclosed bidirectionally | yes |
| 2 | SOFTWARE | **VERIFIED** | platform-nucleus + platform-composition expansion tests (`adr/0010`) | partial — `11-SERVICE/` 0 `.py`, `12-APPLICATION/` 0 `.py` |
| 3 | DATA | **CERTIFIED** for `engine/uckp` · **OPEN GAP** elsewhere | `PersistenceAdapter` + 10 adapters + `InterchangeabilityReport` | yes. Gap named: `KnowledgeStore`, `ContextRegistry`, UCDA register, id-ledger do direct file I/O "with no seam a second storage technology could implement against" |
| 4 | INFRASTRUCTURE | **IMPLEMENTED** | none — no violation found, no proof built | yes. `adr/0012` "Earth" default **remediated**: `region: str \| None = None` (`persistence.py:489`) |
| 5 | COMMUNICATION | **NOT YET ASSESSED** | none — **and none is buildable** | **no.** No `ProtocolAdapter` analogue; grep for `fastapi\|flask\|http.server\|aiohttp\|uvicorn` yields only 2 test/governance mentions |
| 6 | EXPERIENCE | **NOT YET ASSESSED** | none — **and none is buildable** | **no.** 0 `.tsx`/`.jsx`/`.vue`; 1 `.html`, a published output. `portal/` is a domain model with no rendering layer |
| 7 | TOOLS | **IMPLEMENTED** | none over the surface | yes — `provider/metatypes.py` + `platform/universal_provider/` (15 modules), open by registration |

`AD-G-03` **confirmed**: 4 of 7 lack an executable check — **INFRASTRUCTURE, COMMUNICATION, EXPERIENCE, TOOLS**. The four split into two failure modes: INFRASTRUCTURE and TOOLS have surface and no check (buildable today); COMMUNICATION and EXPERIENCE have no surface, so a check requires first building an expression — and the located assessment **recommends against** doing so merely to pass: *"building one merely to pass a certification would be manufacturing evidence, not discovering it."* Recorded as the governed position.

---

## 4 — RELATIONSHIP PROPERTY MATRIX (6 properties × 4 planes)

| Property | CEU (`ceu/existence.py`) | UKIP (`ukip/relationships.py`) | UKG (`graph/model.py`) | DATA (`data/relationship.py`) |
|---|---|---|---|---|
| Entities connected through relationships | **CERTIFIED** | CERTIFIED | CERTIFIED | CERTIFIED |
| Relationships can evolve | **CERTIFIED** (`supersede`/`resurrect`/`ancestry`, `adr/0023`) | CERTIFIED (`COMPOSITION_RULES` with cited `path`) | IMPLEMENTED | IMPLEMENTED |
| Relationships have context | IMPLEMENTED (registry-granular via `bind_context`) | IMPLEMENTED | **OPEN GAP** | OPEN GAP |
| Relationships have validity | **OPEN GAP** (`P4-F-002`) | **CERTIFIED** (`valid_at()`, `adr/0015`) | OPEN GAP | OPEN GAP |
| Relationships have evidence | **CERTIFIED** (hash-chained `AuditEntry`) | CERTIFIED | IMPLEMENTED | IMPLEMENTED |
| Support unknown future types | **CERTIFIED — proven** (`test_…:74` + `ISD-L-06` live extension) | CERTIFIED | CERTIFIED (open string `type`) | IMPLEMENTED (open `type_tag`, closed `kind`/`cardinality`) |

**Reading:** the two partials are **one gap seen twice** — temporal validity and per-edge context landed in the knowledge-closure plane and were never propagated to the existence and graph planes. Both are named (`P4-F-002`, `P4-F-009`) with declared owners. **No new capability is required; propagation is.**

---

## 5 — OWNERSHIP AND AUTHORITY MATRIX

| Dimension | Canonical owner | Authority tier | Self-declared authority | Orphan? | Duplicate? |
|---|---|---|---|---|---|
| 1 | `engine/infinite_scope/` | DERIVED TRUTH | "legislates nothing… OBSERVE MODE — READ ONLY" | no | no |
| 2 | *distributed* — no single module | CONTRACT (provider) + direction | "DESIGN PRINCIPLE — not a certification" | no | **ambiguous by construction** |
| 3 | `uckp/ucko.py` + `uckp/identity.py` | **SUPREME SINGLETON** | "role: SUPREME — this IS UCKP-ART-05" | no | no — guarded by `second_authority_test` |
| 4 | `ceu/existence.py` | DERIVED TRUTH | registry-driven | no | no — 4 disjoint planes per `UCRD-001` §5 |
| 5 | `engine/context/` | model owns itself | `CMG-000012` owns **only** the binding (`CXL-06` Context Once) | no | no |
| 6 | `UCIC-001` | CONTRACT (FROZEN v1.0) | "no capability may bypass this contract or skip a gate" | no | **band-local duplicates** (7 sites) |
| 7 | `UKIP`/`UCKP`/`USAF-001` | CONTRACT | Knowledge Once Principle | no | no |
| 8 | `lineage/memory.py` | DERIVED TRUTH | "CREATES NO MEMORY STORE, NO MEMORY ENGINE… a RESOLUTION ORDER over those owners" | no | no |
| 9 | `UAKOS-CLOSURE-009` | DERIVED TRUTH | identity derived from concept identity | no | **2 planes, no join key** (`RU-G-01`) |
| 10 | `UEG-000001` + `EPIC-RTE-002` | CONTRACT | `EXECUTION_AUTHORITY = "ENGINEERING-EXECUTION-ONLY"` | no | no — UIEC is documents only |
| 11 | `CMG-000001`→`UCIC-001`→`UCL-000001`→`CEP-009` | LAW → CONTRACT → DERIVED | `UCL-000001`: "legislates no lifecycle, opens no registry, mints no identifier" | **145 determinations unowned** | no — merge forbidden (`CMG` LXXVI.6) |
| 12 | `UVI-000001` + `verify.sh` | DERIVED TRUTH | "MODES ARE NOT DECLARED HERE" | no | no |
| 13 | generated-artifact registry | **AUTHORED REPOSITORY TRUTH, upstream** | "must never be produced by one of them" | no | `EXCLUDE_DIR_PREFIXES` is a **second expression** |
| 14 | mutation-governance-boundary | subordinate under `UCKP-LAW-0001` | "declares the boundary; it does not create a new authority" | no | frozen-prefix literal **duplicated** in 2 modules |

**Ownership is total: 14/14 owned.** Detected: **1 orphan class** (145 determination documents — `NON_CANONICAL` evidence, kept, but lifecycle-unbound) · **0 duplicate ownership of a subject** · **3 ambiguous** (dimension 2 distributed; dimension 6 band-local; dimension 9 two planes) · **1 dangling authority** (`CMG-000008/9/10` inherit an instrument that does not exist — 21 unmeasured self-certifying claims) · **1 unenforced authority** (`UAP-001`, self-disclosed) · **0 unauthorized authority** located.

---

## 6 — BOUNDARY MATRIX

| Boundary kind | Class | Enforcer | Extensible via named channel? |
|---|---|---|---|
| Corpus write | **CERTIFIED** | `frozen_paths.py:33` + `ec1-frozen-guard`, CI `ec1-ci.yml:132` | **yes** — supersession (CEP-007 XIII) or amendment (CEP-009) |
| Trust / RBAC | **VERIFIED** | `identity/policy.py` — 4 ordered guards, default-deny | yes — `extra_rules=[NamedPolicyRule…]` |
| Security-zone direction | **IMPLEMENTED** | `security/zones.py` `zone_may_mutate` | yes — free-form future zone target. **Decides but does not intercept** |
| Context isolation | **VERIFIED** | `context/composition.py:128` `can_reference` | yes — federation |
| Execution isolation | **VERIFIED** | `runtime/execution/isolation.py` | yes — `federation.py` ENG-005 |
| Programme write scope | **IMPLEMENTED** | `forbidden_write_prefixes` + per-engine `check_write_scope` | declaration edit. **Absent from 3 of 11 declarations** |
| Execution-environment containment | **CERTIFIED** | `execution_environment/contract.py` EEG-01…08 | — (deliberately pinning) |
| Permanence ratchet (meta-boundary) | **CERTIFIED** | `check_no_active_permanence_declaration` | **class A inadmissible**: "forbidding future change with no channel named" |
| Gate's own mutation boundary (`ISD-BND-08`) | **CERTIFIED** | `uisd-gate.yml` — twice-run + `git status` diff | — |
| Governance boundaries `ISD-BND-01…07` | **GOVERNED CLOSURE** | declaration only — no computed refusal | owners named; refusal asserted, not computed |

---

## 7 — UNKNOWN-SPACE MATRIX

**Admitted (open-world):** entity form `ceu/existence.py:357` · context kind `taxonomy.py:516` · entity kind `object_birth/scope.py:591` · memory subject `lineage/memory.py:450-478` · provider category `provider/metatypes.py` · storage mechanism `persistence.py:574` · location `persistence.py:489` (`region=None`) · security zone `zones.py:10-12`.

**Refused (fail-closed):** lifecycle status `registry/models.py:47-53` · artifact input class `generated_artifacts.py:281` · unregistered form `ceu/existence.py::form_of` · context tokens `taxonomy.py:90,137,179,263` · unreadable declaration `infinite_scope/contract.py::load_declaration` (exit 2) · law↔check mismatch `infinite_scope/model.py` · absent grant `identity/policy.py` · cross-partition dependency `isolation.py`.

**The rule, stated:** admitted at declaration/extension points where the unknown arrives as a new declared member with a named admission path and an identity authority; refused at coercion/read points where an unrecognised token arrives inside an already-governed record. `ceu/existence.py` holds both halves.

**Measured, not asserted — 4 instruments:** `kernel_source_fingerprint()` before/after in 10 tests · `ISD-L-06` performing a live non-mutating extension every run ("*a comment claiming a vocabulary is append-only is not evidence; a non-mutating extension is*") · `ISD-L-11` 3 admission exercises, one through the owner's own declared reader · journal verification.

**Eleven concretely alien categories admitted with the kernel unchanged** (`engine/kernel/compliance.py:63-73`): Xophar-Collective (`plasma-lattice`, `known: False`) · Glyphic-Resonance (`electromagnetic`) · Entropy-Credit (`reversible-negentropy`) · Gradient-Levy · Causal-Witness (`lightcone-attestation`) · Branching-Retrocausal (`non-linear`) · Consensus-Swarm (`emergent-quorum`) · Trans-Dimensional-Field · Substrate-Weaver (`unbounded`) · Reality-Compilation (`cross-universe`) · Superpositional-Dispatch (`amplitude`). Verdict `passed = all_ok and kernel_unchanged`, obligation `mandatory-architectural-proof`.

Class: **CERTIFIED**. Gap: `adr/0008` status **Proposed** while implemented; no dedicated CI workflow for `engine/tests/expansion/`.

---

## 8 — POPULATION REGISTER — enumerated vs discovered

**Every number below is a currently discovered population. None is a boundary.**

| Population | Count | `Enum?` |
|---|---|---|
| Concepts under closure | 549 | **discovered** — walked from registers |
| Repository Requirements `RR-*` | 549 | **derived** — total injective function of concept identity |
| Requirements `REQ-NN` (manual plane) | 49 | **discovered** — hand-curated; adjudicated to 54 by `100-PERCENT-CLAIM-VALIDATION` |
| Requirement gap classes | 19 | **computed** by ~16 `add_gap()` calls |
| Generated artifacts | 345 · `bootstrap_gaps` empty | **discovered** — `load()` |
| Mutation classes / rules | 9 / 9 | **data** — no `MutationClass` enum exists |
| Rule predicates implemented | 8 | **code** — asymmetry is a live finding |
| CI gate workflows | 29 + 2 | files; 27 assert determinism/replay/audit |
| `verify.sh` stage literals | 14 + 1 | **re-derived by regex from source**, digest-matched |
| `verify.sh` modes | 5 | declared in `uvi-declaration.json`; `UVI-L-01` measures both directions |
| UCKO facets | 33 | **ENUMERATED CLOSED** — disclosed intentional |
| Entity kinds (birth scope) | 10 | data + **mandatory catch-all** → total by construction |
| Seed relationship types / topologies | 17 / 17 | data rows; type space constrained by pattern, never enum |
| Universal context kinds | 15–16 | `extend()` bounded open-world |
| Lifecycle stages | 45 / 15 / 15 | data (`ucl-stage-manifest.json`); manifest alignment fails closed |
| Expansion axes | 10 | **ENUMERATED as an enforced contract** — `test_suite_proves_every_principle_axis` asserts the axis→test map |
| Alien categories proven | 11 | code fixtures |
| `KNOWN_PERSISTENCE_KINDS` | 10 | **ENUMERATED CLOSED** — gap `ISD-G-07`: comment claims "Open by registration" while no registry holds it |
| `KNOWN_EXECUTION_KINDS` | — | **ENUMERATED CLOSED** — gap `ISD-G-08`, same terms |
| `ADMISSION_FORMS` | 2 | **ENUMERATED CLOSED** — honestly disclosed as closure #11 |
| `MeasurementKind` | 4 | **ENUMERATED CLOSED** |
| `MaturityAxis` | 14 | **ENUMERATED CLOSED** |
| Maturity lattice `M0…M7` | 8 | code-resident, declared "no ceiling in the model, only in the evidence" |
| `TruthClass` | 9 | **ENUMERATED CLOSED** |
| `Stage` (provenance) | 9 | **ENUMERATED CLOSED**, `coerce()` fails closed |
| `LifecycleStatus` | 16 | **ENUMERATED CLOSED**, fail-closed coercer |
| `FROZEN_PREFIXES` | 3 | **ENUMERATED CLOSED** — **duplicated** in `policy.py:50` |
| `_BUILTIN_GUARDS` | 4 | closed, extensible via `extra_rules` |
| `freeze_scan` classes / phrases | 5 (A–E) / 9 + 1 regex | declaration data; A inadmissible, E count-exempt |
| Closed-enumeration disclosures | 11 (10 intentional, 1 not) | declaration data |
| `ISD-BND` boundaries / `ISD-G` gaps | 8 / 11 | declaration data |
| Architectural catalog | 112 universes → 499 domains → 2027 capabilities | inventory, authority-neutral |
| Realized capability CKOs | 131 `UCKO-CAP-*` | generated, `knowledge_seal 71c65cf5…` |
| Identity ledger entries | 6,178 · monotonic cursor | append-only, retired entries retained |
| Documentation-only trees | `09-PLATFORM` 20 md · `11-SERVICE` 19 · `12-APPLICATION` 22 · `13-INFRASTRUCTURE` 20 · `14-SECURITY` 5 | **0 `.py` each** |

---

## 9 — LIVE MEASUREMENT REGISTER

Executed read-only with `.ec1-venv/bin/python` at HEAD `bae59755`.

| Instrument | Result | Class |
|---|---|---|
| `engine.infinite_scope.gate` | exit 0 → **OPEN** | CERTIFIED |
| `engine.object_birth.gate` | exit 0 | CERTIFIED |
| `engine.uaue.gate` | exit 0 | CERTIFIED |
| `engine.execution_environment.gate` | exit 0 + advisory `! EEG-08 … 38 condition(s)` | CERTIFIED (EEG-08 non-blocking) |
| `validate_rule_coverage(mutation-governance-boundary)` | `("rule 'R-09' is declared but no predicate implements it",)` | **OPEN GAP — live** |
| `requirement_engine.py --gate` | `fully=140 partially=409 not=0 (25.5009%)` · `open_gap_classes=12` · `baseline=WITHHELD(12 preconditions unproven)` | **IMPLEMENTED, not certified** |
| `UAKOS-CLOSURE-002` (session hook) | `CLOSED · concepts=549 · gaps=0` (7 classes) | CERTIFIED — **qualified** |
| `git status --porcelain \| wc -l` | 59 → 59 across the prior pass | preservation verified |

**The two closure numbers do not conflict and must not be conflated.** `UAKOS-CLOSURE-002` measures **concept homing** (549/549 homed). `UAKOS-CLOSURE-009` measures **requirement dimensional assimilation** (25.5%). Homing is complete; dimensional population is not. Additionally the `gaps=0` is qualified: `conversation_only` is measurable only from an external corpus at `REPO.parent/"UCOS"`, and absent it "measures 0 by ABSENCE rather than by closure."

---

## 10 — DUPLICATE ANALYSIS

**Reuse-before-create was applied to every dimension. Zero new capabilities were identified as required.** Three independent instruments reached the same conclusion: `OMEGA-E06` §27 (**18 REUSE, 0 CREATE**) · `UNIVERSAL-LIFECYCLE-INHERITANCE-RECONCILIATION` §1 ("*all five already exist under different names*") · `CMG-000012-IDENTITY-AND-OWNERSHIP` §1 ("*must not define a Universal Context Model*").

| Apparent duplication | Verdict | Basis |
|---|---|---|
| 4 lifecycle instruments | **NOT duplication** | disjoint subjects; merge forbidden `CMG` LXXVI.6; `--check-no-parallel-authority` enforces |
| 4 relationship planes | **NOT duplication** | `UCRD-001` §5 — relationships bind *between*, facets are *of*; "everything is a relationship" deliberately rejected |
| 3 `CertificationStatus` definitions | **NOT duplication** | `PHASE-VERDICT-VOCABULARY` determined (C) independent vocabularies; no consumer reconciles them |
| `UCOS-URR-001` vs `UAKOS-CLOSURE-009` | **duplication REFUSED** | `URR-001` stands `PROPOSED — NOT ADMITTED`; a second register is the competing measurement UFC-16 forbids |
| Assumption detector (proposed second) | **duplication REFUSED** | "*Do not build a second detector*" — a parallel detector is a gate violation |
| `engine/knowledge/homing.py` | **duplication RETIRED** | two determinations over one population gave different numbers; `convergence-gate` fails if it reappears |
| 2 entity-kind vocabularies | **unreconciled** | `birth-scope-policy.json` kinds vs `uaue` `ObjectKind` |
| 7 band-local capability lifecycles | **unreconciled** | no single universal capability lifecycle type |
| 2 requirement planes | **unreconciled — reserved** | `RU-G-01`, reserved to authority under CEP-002 14.2 |
| 2 principle planes (22 vs 5) | **unreconciled — reserved** | `PA-G-04` |
| 2 maturity models | **unreconciled** | 8-level lattice vs 14-axis vector; shared token names, different arity |
| Frozen-prefix literal ×2 | **unreconciled** | `frozen_paths.py:33` and `policy.py:50`, no shared constant |
| `EXCLUDE_DIR_PREFIXES` vs generated-artifact registry | **unreconciled** | second expression of "this path is generated" |
| 6+ ad-hoc `Context` classes | **unreconciled** | bypass `UCXI-000001` |

**Pattern:** every *refused* duplication was refused by a located instrument with a stated reason. Every *unreconciled* plurality is a missing **join**, not a missing capability.

---

## 11 — CLASSIFICATION SUMMARY

| Class | Dimensions | Phases | Neutrality categories | Total items |
|---|---|---|---|---|
| `CERTIFIED` | 7 | 9 | 2 (1 scoped) | 18 |
| `IMPLEMENTED` | 5 | 8 | 3 | 16 |
| `VERIFIED` | 2 | 3 | 1 | 6 |
| `GOVERNED CLOSURE` | 1 | 3 | 0 | 4 |
| `OPEN GAP` | 0 | 0 | 1 (DATA outside `uckp`) | 1 + 2 live findings |
| `NOT YET ASSESSED` | 0 | 1 | 2 | 3 |

**No dimension is `MISSING`. No dimension is `DOCUMENTATION ONLY`.**

The three `NOT YET ASSESSED` items are the honest residue: **COMMUNICATION** and **EXPERIENCE** neutrality (no surface exists to assess, and manufacturing one is advised against) and the lifecycle chain's **Reason · Challenge · Predict · Simulate · Optimize** segment (nearest mechanisms located, none claimed). Closure was not forced on these.

---

*END · `UCOS-OMEGA-INFINITY-ASSIMILATION-COVERAGE-MATRIX.md` · AUTHORITY = NONE (DERIVED TRUTH) · Where this matrix and a located instrument differ, the located instrument governs.*
