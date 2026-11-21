# EVO-USIS-W3-FOUNDATION-001 · 05 — Dependency Graph

| Field | Value |
|-------|-------|
| ARTIFACT ID | EVO-USIS-W3-F-001-DEP (Dependency Graph) |
| PROGRAMME | EVO-USIS-W3-FOUNDATION-001 — Wave-3 Constitutional Foundation |
| PROGRAM | UCOS-USIS-001 — Universal Science & Intelligence Substrate |
| CLASSIFICATION | Governed operational-memory determination record. **GOVERNANCE ONLY · READ-ONLY.** Not a corpus artifact. |
| DEPENDS-ON (read-only) | `01`…`04` of this programme · `relationships.json` (12,493 edges) · USIS-004 (tier order) · roadmap §Wave 3 · UCIC-001 Stage 2 |
| INVARIANT ASSERTED | downward-only · acyclic (CIOA) · no forward reference (obligation 14) · zero circular dependencies (obligation 5) |
| AUTHORITY | **NONE — DERIVED.** |
| CONFLICT RULE | Higher frozen/governing instruments prevail. |

> **Purpose.** Determine **every** dependency governing Wave-3 — internal, external, logical, runtime, governance, validation, certification, evidence — fix the constitutional ordering, and identify the critical path. The existing (verified) Wave-2 graph is the immutable substrate; Wave-3 dependencies are stated as edges founded downward-only on it.

---

## PART A — Verified baseline graph (immutable substrate)

| Property | Observed | Method |
|----------|:--------:|--------|
| Total corpus edges | 12,493 | `00-BOOK/DATA/relationships.json` |
| Unresolved endpoints | **0** | every `from`/`to` resolved against 1164 registered universal IDs |
| USIS-touching edges | 369 | Depends-On 92 · Required-By 91 · Authorized-By 47 · Authorizes 47 · Parent 27 · Child 27 · Implements 19 · Implemented-By 19 |
| Acyclicity | **acyclic** | `ukbx twin --check` C-07 |
| Referential integrity | **all endpoints resolve** | C-05 |
| Navigability | all reachable + return path | C-08 |

### A.1 — The frozen USIS internal spine (92 Depends-On edges, observed)

```
UCOS-SVC-000018 (SERVICE terminal) ◄── CROSS_PROGRAM
UCOS-SEC-000001 (SECURITY root)    ◄── self-declared founding edge
        ▲
   000001  USIS-GOV-000                      [2 deps]
        ▲
   000002  USIS-001 Constitution             [→000001]
        ▲
   000003  USIS-002 Universe Catalog          [→000002]
        ▲
   000004  USIS-004 Meta-Model                [→000002,000003]
        ▲
   000005  USIS-003 Science Catalog           [→000003,000004]
   000006  USIS-005 Theory/Ontology/Taxonomy  [→000003,000004]
        ▲
   000007  USIS-007 Domain                    [→000003,000004,000005,000006]
   000008  USIS-006 Capability                [→000003,000004,000005,000006,000007]
   000009  USIS-009 Model                     [→000003,000004,000008]
   000010  USIS-008 Algorithm                 [→000003,000004,000008,000009]
   000011  USIS-010 Pattern                   [→000003,000004,000009,000010]
   000012  USIS-011 Engine                    [→000003,000004,000009,000010,000011]
   000013  USIS-013 Runtime                   [→000003,000004,000012]
   000014  USIS-012 Service                   [→000003,000004,000012,000013]
   000015  USIS-017 API/SDK                   [→000003,000004,000014]
        ▲
   000016  USIS-INT-001 Implementation        [→10 spine layers]
   000017  USIS-014 Validation                [→11]
   000018  USIS-015 Certification             [→12]
   000019  USIS-016 Evidence                  [→14, incl. UCOS-CON-000040]
```

Every edge points to a **strictly lower** universal ID: downward-only founding is structurally proven, not asserted. **Wave-3 attaches only above `000019`.**

## PART B — Internal dependencies (Wave-3 → frozen corpus)

Each Wave-3 element and the frozen artifacts it must have in terminal-success state before entry (UCIC-001 Stage 2: "every dependency in a terminal-success state; acyclic").

| Wave-3 element | Depends-On (frozen corpus) | Tier authority |
|----------------|----------------------------|----------------|
| `02-ONTOLOGY/` home + owning artifact | USIS-005 (framework O-1…O-4 + Ontology Closure), USIS-004 (tier 7) | tier 7 |
| `03-TAXONOMY/` home + owning artifact | USIS-005 (X-1…X-4 + Taxonomy Closure), USIS-002/003 (root taxa), USIS-004 (tier 8) | tier 8 |
| `04-REGISTRIES/` home + 12 registry catalogs | USIS-002, USIS-003, USIS-006, USIS-007, USIS-008, USIS-009, USIS-010, USIS-011, USIS-013, USIS-004 (tier 9) | tier 9 |
| `19-DOCUMENTATION/` home | structure spec §2 (no corpus dependency) | — |
| USIS-021 Master Registry | `04-REGISTRIES/`, USIS-002, USIS-003, all tier catalogs | area 04 |
| USIS-018 Foundation Freeze | **all 19 registered artifacts**, FREEZE C4 closure reconciliation (G-11) | governance |
| USIS-019 Readiness | USIS-018, USIS-021, G-01/G-02 closed | governance |
| USIS-020 Completion | all Wave-3 member missions terminal-success | governance |
| Science-tier instance (`USIS-SCI-<X>`) | USIS-003 (row), USIS-002 (`USIS-U-SCI`), USIS-004 (tier 1) | tier 1 |
| Domain instance (`USIS-DOM-<X>`) | USIS-007, parent Discipline, USIS-005 placement, `04-REGISTRIES/` | tiers 3–4 |
| Capability instance (`USIS-CAP-<X>`) | USIS-006, parent Domain/Sub-Domain, UCIC-001 Output-2 | tier 5 |
| Theory instance | USIS-005 T-1…T-5, parent Capability | tier 6 |
| Ontology concept + relations | USIS-005 Part D, `02-ONTOLOGY/`, owning Theory (`Derives-From`) | tier 7 |
| Taxon | USIS-005 Part E, `03-TAXONOMY/`, ontology concept (`Derives-From`) | tier 8 |
| Registry row | `04-REGISTRIES/`, taxon | tier 9 |
| Knowledge Object | U24 / MIP Part 19 (reference), registry row | tier 10 |
| Model row (+`binding`) | USIS-009, Knowledge Object | tier 11 |
| Algorithm row (+`binding`) | USIS-008, Model / Capability | tier 12 |
| Pattern | USIS-010, Algorithm | tier 13 |
| Engine instance | USIS-011, Pattern, Algorithm/Model registries resolvable | tier 14 |
| Runtime binding | USIS-013, Engine, platform runtime (reference) | tier 15 |
| Service instance | USIS-012, Runtime | tier 16 |
| API surface | USIS-017, Service | tier 17 |
| SDK surface | USIS-017, API | tier 18 |
| Implementation (code) | USIS-INT-001 Part E composition contract, SDK | tier 19 |
| Validation record | USIS-014 (Parts F/G/M/O), Implementation | tier 20 |
| Certification record | USIS-015, Validation record | tier 21 |
| Evidence bundle | USIS-016, Certification record, TRACK-001 | tier 22 |
| Governing determination | USIS-019 / Wave-3 authorization | tier 23 |
| Lifecycle state | EXEC-REG-001 (7th stream), UCIC-001 states | tier 24 |

## PART C — External dependencies (referenced, never re-homed)

| External anchor | Canonical home | Referenced by | Wave-3 obligation |
|-----------------|----------------|---------------|-------------------|
| SERVICE program terminal | `UCOS-SVC-000018` | `USIS-GOV-000` (CROSS_PROGRAM) | unchanged; founding edge preserved |
| SECURITY program root | `UCOS-SEC-000001` | `USIS-GOV-000` | unchanged |
| DATA program + U07 | `10-DATA/`, `data/` | `USIS-U-DAT` members | reference only (LAW USIS-02) |
| Security concerns | `14-SECURITY/` | Security domain | reference only |
| Governance universe U03 | governance corpus | Governance domain | reference only |
| Runtime | `08-RUNTIME/`, `platform/runtime_platform`, RIE | tier 15 bindings | reference only |
| Simulation U26 / MIP Part 25 | simulation corpus | `USIS-U-SIM` | reference only |
| Knowledge U24 / MIP Part 19 | knowledge ontology registry | tiers 7, 10 | reference only |
| Analytics U16 / Intelligence U25 / Part 20 | analytics + intelligence corpus | `USIS-U-ANL/INT/RSN/PRD` | reference only |
| Learning MIP Part 21 | learning corpus | `USIS-U-LRN` | reference only |
| Evolution U28 / Part 22/32 | evolution corpus | `USIS-U-EVO` (Wave-4) | reference only |
| Future constructs MIP Part 49 | — | `USIS-U-FUT` | reserved receptor |
| LAW Ω∞-000 | constitutional corpus | all USIS artifacts | supreme; unchanged |
| Frozen streams | `engine/**` (EC-1), `platform/**` (EC-2), `00-CEP/**`, `99-FREEZE/**`, `00-BOOK/**` source | tier 19 | **0 writes** (DP-03) |
| Extendable streams | `service/`, `application/`, `infrastructure/`, `knowledge/` | tier 19 | additive only |
| Toolchain | python3, git, bash, ruff, pytest/pytest-cov/coverage (canonical venv via `scripts/ucos-env.sh`) | all gates | reuse; `jsonschema` optional (G-13) |

**External-dependency invariant:** every external edge is `References`/`Realizes`/`Depends-On` **downward** into an already-established program. Wave-3 introduces **no upstream change** and **no new external program**.

## PART D — Logical dependencies (rule-level, not artifact-level)

| Logical dependency | Rule | Consequence if violated |
|--------------------|------|-------------------------|
| Registration-over-redesign | LAW USIS-00 / USIS-03 — a member enters by append, never by architecture change | any architecture edit during Wave-3 ⇒ obligation 7 (architectural debt) failure |
| Reuse-First precedence | LAW USIS-02 + USIS-004 Part F — search canonical instance before creating a node | duplicate node ⇒ obligations 2/3 failure |
| Meta-model conformance | LAW USIS-08 + USIS-004 Part D — all 24 tiers present, owned, edged, evidenced | partial chain ⇒ member NOT realized (no partial state exists) |
| Single canonical ownership | LAW USIS-05 — one home, one owner | orphan/overlap ⇒ obligations 4/9 failure |
| Recursion is a forest | LAW USIS-09 + USIS-005 X-2 — `parent-universe`, sub-domain, sub-theory chains acyclic | cycle ⇒ obligation 5 failure |
| Technology neutrality | LAW USIS-04 — tiers 6–13 name no vendor/framework; technology only as `binding` on tiers 11–12 | named technology in architecture ⇒ obligation 1 failure |
| Intelligence-stream purity | USIS-004 Part E — only tier 19 produces code, in the Software stream, referenced | code inside `15-…/` ⇒ USIS-INT-001 invariant 2 failure |
| Fail-closed evidence | TRACK-001 — absence of evidence = NOT-DONE | missing evidence ⇒ INVALID verdict |
| Non-projection | STATUS-001 — existence ≠ completion | claiming completion from file presence ⇒ status invalidity |
| One capability per mission | UCIC-001 Stage 4 gate | scope spanning >1 capability ⇒ NON-RECOVERABLE, rollback |
| Separation of duties | UCIC-001 Stage 3/10 — executor ≠ CIOA ≠ CCE | SoD violation ⇒ NON-RECOVERABLE |
| Frontier-derived selection | UCIC-001 Stage 1 — selection must be CIOA-derived, not manual | manual sequencing ⇒ Stage 1 gate fail (basis of G-06 sub-gap) |
| Append-only identity | REG-AUTO-001 + `id-ledger.json` | reuse/renumber of an ID ⇒ obligation 7 failure |

## PART E — Runtime dependencies

| Runtime dependency | Provider (reused) | Consumed by |
|--------------------|-------------------|-------------|
| Execution hosting | platform runtime (`platform/runtime_platform`, `runtime_operations`), `engine/runtime`, `08-RUNTIME`, RIE | tier 15 runtime bindings |
| Execution-mode semantics (on-demand + continuous) | USIS-013 Parts E/I | every runtime binding |
| Governed-autonomy gate | USIS-013 Part I + LAW USIS-06 | every self-* pathway (fully realized in Wave-4) |
| Runtime-validation contract | USIS-014 Part J — every self-* pathway gated; explanation coverage present | tier 20 |
| Execution register | EXEC-REG-001 (`ukb exec`), currently 0 instances (G-10) | tier 24 |
| Execution stream | FREEZE C4 stream 7 "Universal Science & Intelligence" (`science-intelligence-eligible`), closure currently 0 (G-11) | tier 24 |
| Context propagation / state evolution | USIS-013 Parts F/H | tiers 15–16 |
| Frontier / progress telemetry | `intelligence/UCOS-RIE-EXECUTION-FRONTIER.json`, `-PROGRESS.json`, `-HEALTH.json` | UCIC Stages 1, 11 |

**Runtime-independence constraint:** tiers 1–13 must be fully definable with **no runtime present** (USIS-007 Part I, USIS-006 Part K). Runtime dependencies therefore begin only at tier 15 — this is what makes the ordering in Part I feasible.

## PART F — Governance dependencies

| Governance dependency | Instrument | Gate it controls |
|-----------------------|-----------|------------------|
| Implementation methodology | UCIC-001 (FROZEN v1.0) — 15 stages | all Wave-3 work |
| Authority for each member | Wave-3 authorization determination (**G-06, absent**) + USIS-019 (**G-04, absent**) | Stage 3 READY_TO_IMPLEMENT |
| Constitutional anchor per member | Wave-3 blueprint (**G-05, absent**) | Stage 3 |
| Registration law | REG-AUTO-001 §7 Atomic Creation Law | Stages 13–14 |
| No-Orphan | GOV-001-T3 | `ukb enforce` |
| Traceability | GOV-002 | relationship edges |
| Evidence | TRACK-001 | Stages 9/10 |
| Status validity / non-projection | STATUS-001 | completion claims |
| Change discipline | UCI-001 | additive/supersession |
| Infinite evolution | AUTH-INF-001 (CR-INF-001/007/008/009/010) | append-only growth |
| Sequencing frontier | CIOA `UCOS-COMP-000000` | Stage 1 |
| Certification gates | CCE `UCOS-COMP-000001` (10 gates) | Stage 10 |
| Validation law | CEP-004 | Stages 5–9 |
| Provisional tier | CEP-006 (USIS standing is PROVISIONAL; DR-RAT-11 external, non-blocking) | program standing |
| Freeze lineage | FREEZE C2/C3 immutable → C4 certified successor → C5 (Wave-6) | stream model |
| Operational-memory exclusion | UCOS-RECON-C1 + `config.py:745` | where programme records live (G-14) |

## PART G — Validation, certification, and evidence dependencies

| Dependency | Provider | Dependent |
|------------|----------|-----------|
| Structural / append-only / acyclic / referential validation | `ukb validate` | every registration |
| Registration parity + classification | `ukb enforce --pre` / `enforce` | every registration |
| Signal / provenance / secret-free validation | `ukbx validate` | twin state |
| Twin hard checks (C-04/05/07/08/09/10/11) | `ukbx twin --check` | twin certification |
| 10 integrity domains | `ukbx certify` | whole-corpus certification per mission |
| Quality gates (lint, tests, coverage ≥ 90) | `verify.sh` | tier-19 implementation |
| Per-capability validation stages | UCIC-001 Stages 5–9 | tier 20 record |
| Obligation set + verdict semantics | USIS-014 Part F | tier 20 record |
| Cross-layer surfaces (8) | USIS-014 Part M | tier 20 record |
| Coverage dimensions (6) | USIS-014 Part O | coverage certificate |
| Certification gates + SoD | USIS-015 + CCE | tier 21 record |
| Evidence contract (UCIC Output-5) | USIS-016 + TRACK-001 | tier 22 bundle |
| Drift gate | `register.sh --guard` | commit readiness |
| Determinism proof | `engine/determinism`, `determinism-evidence/`, double-run registration | obligation 18 |

**Strict ordering (fail-closed, USIS-014 Part I):** structural → semantic → cross-layer. A lower defect short-circuits before higher checks run. **Validation founds Certification founds Evidence** (tiers 20 → 21 → 22) — never reversed.

## PART H — Wave-3 dependency layering (the constitutional ordering)

```
L0  FROZEN BASELINE 527485a — 19 registered artifacts, 12,493 edges, 0 unresolved
     │   (immutable; Wave-3 attaches above UCOS-USIS-000019 only)
     ▼
L1  GOVERNANCE FOUNDATION      this programme (01–08)  ·  no repository dependency beyond L0
     ▼
L2  STRUCTURAL CLOSURE         G-01 02-ONTOLOGY + 03-TAXONOMY · G-02 04-REGISTRIES (12 catalogs)
                               G-03 19-DOCUMENTATION · G-11 FREEZE C4 closure reconciliation
     ▼
L3  REGISTRY + FREEZE CLOSURE  USIS-021 Master Registry · USIS-018 Foundation Freeze (G-04)
     ▼
L4  BLUEPRINT + AUTHORIZATION  G-05 blueprint schema + set · G-06 authorization + member
                               catalogue + frontier binding · G-14 record-placement convention
                               · USIS-019 Readiness (G-04) · G-10 execution-stream activation rule
     ▼
L5  PRIORITY GROUP 1 — Universal Science Universe: USIS-U-SCI sub-home + 28 realizable
                               sciences (+2 receptors); tiers 1–2 then full chains
     ▼
L6  PRIORITY GROUP 2 — Intelligence + Human Intelligence: U-INT, U-HUM, U-COG, U-BEH,
                               U-PSY, U-LRN + 38 HI capability families
     ▼
L7  PRIORITY GROUP 3 — Data · Analytics · Algorithm · Model: U-DAT(15), U-ANL(26),
                               U-ALG(26+), U-MDL(open)
     ▼
L8  PRIORITY GROUP 4 — Reasoning · Decision · Prediction · Simulation · Knowledge:
                               U-RSN, U-DEC, U-PRD, U-SIM, U-KNW
     ▼
L9  PRIORITY GROUP 5 — Autonomous · Multi-Agent: U-AUT, U-MAS
     ▼
L10 INTEGRATION                Wave-3 integration readiness → integration (tier 19 composition
                               realization per USIS-INT-001 Part E)
     ▼
L11 WAVE-3 CLOSURE             whole-corpus certification · USIS-020 Completion · Wave-3 freeze
     ▼
L12 SUCCESSOR                  Wave-4 (USIS-U-EVO, 24 self-*) → Wave-5 → Wave-6 (FUT/UNK, C5)
```

**Per-member internal ordering (inside any of L5–L9), fixed by USIS-004 Part C:**

```
1 Science → 2 Discipline → 3 Domain → 4 Sub-Domain → 5 Capability → 6 Theory →
7 Ontology → 8 Taxonomy → 9 Registry → 10 Knowledge Object → 11 Model → 12 Algorithm →
13 Pattern → 14 Engine → 15 Runtime → 16 Service → 17 API → 18 SDK → 19 Implementation →
20 Validation → 21 Certification → 22 Evidence   (23 Governance and 24 Lifecycle span all)
```

Note the **numbering-vs-dependency distinction** already determined by `UCOS-USIS-WAVE2/00` §5.3: area/artifact numbering is a thematic index and intentionally differs from dependency order (Model founds Algorithm; Runtime founds Service; Domain founds Capability). Dependency order is carried by `Depends-On` metadata, never inferred from file numbers. Wave-3 inherits that rule.

## PART I — Ordering constraints (hard, machine-checkable)

| # | Constraint | Basis | Violation consequence |
|---|-----------|-------|-----------------------|
| O-1 | No Wave-3 artifact may be authored before L2 structural closure if it resolves into `02-ONTOLOGY/`, `03-TAXONOMY/`, or `04-REGISTRIES/` | G-01/G-02; USIS-004 tiers 7–9 | tier closure undischargeable ⇒ member NOT realized |
| O-2 | No member mission may enter Stage 4 before L4 (blueprint + authorization exist) | UCIC-001 Stage 3 | NON-RECOVERABLE authority failure |
| O-3 | Tier *n* may not be authored before tier *n−1* is present and edged | USIS-004 Part C parent-edge contract | broken chain ⇒ Capability Closure (obl 13) failure |
| O-4 | No forward reference: a node may depend only on an already-registered node | UCIC-001 Stage 2; obligation 14 | dependency-closure failure ⇒ rejected |
| O-5 | Validation before Certification before Evidence | USIS-014 Part N / USIS-015 / USIS-016 | certification without validation ⇒ fail-closed |
| O-6 | Whole-corpus re-certification after every member mission | `EVO-USIS-01[456]/08` precedent | regression undetected ⇒ obligation 18 risk |
| O-7 | Registration is part of the same transaction as creation | REG-AUTO-001 §7 | unregistered artifact ⇒ completion claim INVALID |
| O-8 | Priority groups execute 1 → 5 | roadmap §Wave 3 mission-priority order | sequencing not constitutionally founded |
| O-9 | `USIS-U-EVO` content deferred to Wave-4; `USIS-U-FUT`/`UNK` content to Wave-6 | roadmap Waves 4/6 | scope leakage across waves |
| O-10 | USIS-018 (freeze) should precede member realization so the founding baseline is corpus-evidenced | TRACK-001; structure spec §3 sequence | Wave-3 members founded on a freeze that has no corpus instrument |
| O-11 | One logical capability per mission | UCIC-001 Stage 4 | NON-RECOVERABLE ⇒ rollback |
| O-12 | 0 writes to `engine/**`, `platform/**`, `00-CEP/**`, `99-FREEZE/**`, `00-BOOK/**` source | DP-03 | NON-RECOVERABLE ⇒ rollback |

## PART J — Critical path

The critical path is the longest chain of **strictly serial** dependencies from the frozen baseline to the first certified Wave-3 member:

```
527485a baseline (L0)
  → EVO-USIS-W3-FOUNDATION-001 (this programme: 01→02→03→04→05→06→07→08)   [serial, 8 determinations]
  → EVO-USIS-W3-STRUCTURE-001  (02-ONTOLOGY · 03-TAXONOMY · 04-REGISTRIES + 12 catalogs
                                · 19-DOCUMENTATION · FREEZE C4 closure reconciliation)   [G-01,02,03,11]
  → USIS-021 Master Registry                                                   [G-04]
  → USIS-018 Foundation Freeze Determination                                   [G-04, closes F-1]
  → EVO-USIS-W3-BP-001  (blueprint schema + coverage determination)            [G-05]
  → EVO-USIS-W3-BPA-001 (blueprint authoring)                                  [G-05]
  → EVO-USIS-W3-AUTH-001 (authorization + catalogue + frontier binding
                          + USIS-019 Readiness + record-placement convention)  [G-06,G-04,G-14]
  → EXEC-REG-001 stream activation rule                                        [G-10]
  → EVO-USIS-W3-M-001  (first member: USIS-U-SCI + first science, full 24-tier chain,
                        validation → certification → evidence → whole-corpus re-certification)
  = FIRST CERTIFIED WAVE-3 MEMBER
```

**Critical-path length: 9 serial programme steps** before the first member can be certified. Every step is mandated by a gate that cannot be bypassed (O-1, O-2, O-5, O-7, O-10).

### J.1 — Parallelisable work (off the critical path)
| Can run in parallel | With | Why safe |
|---------------------|------|----------|
| `19-DOCUMENTATION/` materialization (G-03) | any step | 0 corpus artifacts reference it |
| `jsonschema` install (G-13) | any step | tooling only, raises depth |
| `EVO-UNI-005` disposition (G-12) | L4 authorization | documentation/traceability only |
| Blueprint authoring for later priority groups | earlier groups' missions | blueprints are source, not dependents of each other |
| Independent members **within** one priority group | each other | distinct concerns, distinct homes, no shared parent below the group root |

### J.2 — Serial bottlenecks (cannot be parallelised)
| Bottleneck | Reason |
|-----------|--------|
| L2 structural closure | 19 artifacts' tier 7/8/9 references all resolve into it |
| L4 authorization | UCIC-001 Stage 3 is a hard gate for every member |
| Per-member tier chain | USIS-004 Part C parent edges are strictly ordered |
| Whole-corpus re-certification | shared global state (`ukbx certify` over the whole corpus) after each member |
| Registration transaction | `register.sh` holds a re-entrancy lock — one transaction at a time by design |

## PART K — Dependency-closure determination

| Closure check | Result | Evidence |
|---------------|:------:|----------|
| Baseline unresolved endpoints | **0** of 12,493 | `relationships.json` resolved against `artifacts.json` |
| Baseline acyclicity | **acyclic** | `twin --check` C-07 |
| Wave-3 internal dependencies enumerated | **28 element classes** | Part B |
| Wave-3 external dependencies enumerated | **16 anchors** | Part C |
| Logical dependencies enumerated | **13 rules** | Part D |
| Runtime dependencies enumerated | **8** | Part E |
| Governance dependencies enumerated | **16 instruments** | Part F |
| Validation / certification / evidence dependencies enumerated | **14** | Part G |
| Ordering constraints fixed | **12 hard constraints** | Part I |
| Layering determined | **L0…L12** | Part H |
| Critical path determined | **9 serial steps** | Part J |
| Forward references in the Wave-3 plan | **0** — every Wave-3 element depends only on frozen or earlier-layer elements | Parts B/H |
| Circular dependencies in the Wave-3 plan | **0** — layering is strictly increasing; per-member chain is a linear tier order; recursion is a forest | Parts D/H/I |
| Unsatisfiable dependencies | **3 currently unsatisfied and scheduled**: tier 7/8 (needs G-01), tier 9 (needs G-02), Stage 3 authority (needs G-05/G-06) | Part B; `04` |

**DEPENDENCY GRAPH: DETERMINED — closure complete over 8 dependency classes; 0 forward references; 0 cycles; critical path = 9 serial steps to the first certified Wave-3 member.**

*END — 05 Dependency Graph · EVO-USIS-W3-FOUNDATION-001 · READ-ONLY · AUTHORITY = NONE (DERIVED).*
