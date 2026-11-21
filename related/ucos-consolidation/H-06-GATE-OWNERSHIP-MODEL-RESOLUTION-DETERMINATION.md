# H-06 GATE OWNERSHIP MODEL RESOLUTION DETERMINATION

| Field | Value |
|---|---|
| **ID** | H-06-GOMRD |
| **Authority** | DETERMINATION ONLY. No implementation authorized. No declaration modified. No registry created. No policy selected. |
| **Phase** | Foundation Closure — Gate Purity — Ownership Model Resolution |
| **Baseline** | HEAD `1f869865` · branch `integration/recovery-001` · working tree DIRTY |
| **Resolves** | Canonical ownership requirements prior to implementation |
| **Reads** | H-06-SUCCESS-CRITERIA-REBASE-DETERMINATION.md · H-06-IAR-AUTHORIZATION-MATRIX-CORRECTION.md · H-06-CONTROLLED-IMPLEMENTATION-EXECUTION-PLAN-v2.md · GATE-PURITY-DETERMINATION.md |
| **Produced** | 2026-08-16 |
| **Status** | RESOLUTION COMPLETE — NO NEW GOVERNANCE SURFACE REQUIRED FOR 33 OF 45 |

---

## 0. Headline

**A new governance surface is not constitutionally required for 33 of the 45 baseline gate
targets.** Ownership surfaces already exist for 22 of them and are structurally capable of
carrying the additive field. For a further 11, the surface *class* exists and is already
instantiated eleven times — covering them needs new *instances*, not a new authority layer.

The genuine gap is **12 Class D targets** with no `00-MASTER` home. For these, and only
these, coverage requires either a per-module declaration model that does not exist, or an
explicit constitutional exclusion. The exclusion route requires no new surface and is
available.

Two findings materially change the ownership picture established by the prior
determinations:

**`generated-artifact-registry.json` already declares producer-ness for 26 of 45 gate
targets.** Each of its 344 entries carries `producer`, `owner`, `deterministic`, and
`regeneration_command` — at 100% field coverage. For `acee-gate`, `ucl-gate` and 24 others,
the registry's `regeneration_command` is the same engine invocation the gate target runs,
differing only by the `--gate` flag that GP-1 proves does not gate the write. **The registry
already documents these gates as producers.** It is the evidence surface for PRODUCER
classification — it must not become the declaration surface.

**GP-5 is the proof that comment-level mode declaration cannot be the remedy.** `verify.sh`
stage 4's comment declared "Read-only" and was false. Extending comment-based declaration to
the 23 uncovered targets would reproduce GP-5 twenty-three times.

---

## 1. Method

For each of the 45 `*-gate` targets at HEAD, two independent axes were measured:

**Axis 1 — declaration surface.** Resolve the invoked engine or module from the Makefile
recipe; resolve its home; enumerate every JSON in that home that parses, carries a
`programme` block, and is **not** a registered generated artifact. A generated artifact is
derived truth and can never be an ownership surface.

**Axis 2 — registry producer evidence.** Determine whether the gate's engine or module
appears as a `producer` or `owner` in `00-BOOK/DATA/generated-artifact-registry.json`, and
with what `deterministic` value.

Every figure was measured against `HEAD:` via `git show`, per rebase determination D-1.4.
No file was modified.

---

## 2. Question 1 — Ownership Classification for All 45 Baseline Gate Targets

### 2.1 Two-Axis Classification

| Class | Axis-1 Definition | Count |
|---|---|---:|
| **A** | Home contains a `*-declaration.json` with a `programme` **object** | **9** |
| **B** | Home contains a non-generated JSON with a `programme` **object**, differently named | **13** |
| **C** | Home exists under `00-MASTER/`, but no non-generated JSON carries a `programme` object | **11** |
| **D** | No `00-MASTER/` home — `platform/`, `intelligence/`, `engine/`, or a shell script | **12** |
| | **Total** | **45** |

### 2.2 Cross-Tabulation Against Registry Producer Evidence

| Class | Targets | Engine is a registered producer | Not a registered producer |
|---|---:|---:|---:|
| A | 9 | **8** | 1 (`rfp-gate`) |
| B | 13 | **11** | 2 (`uccep-gate`, `uaep-gate`) |
| C | 11 | **7** | 4 (`closure-gate`, `closure-phase2-gate`, `closure-phase3-gate`, `final-closure-gate`) |
| D | 12 | **0** | 12 |
| **Total** | **45** | **26** | **19** |

All 26 registered producers carry `deterministic: true`. All 344 registry entries carry
`lifecycle: REGENERATED` and `registration_status: EXCLUDED_FROM_CORPUS_REGISTRATION`.

### 2.3 Derived Ownership Tiers

Combining both axes yields four actionable tiers:

| Tier | Definition | Count | Members |
|---|---|---:|---|
| **O-1** | Declaration surface **and** registry producer evidence | **19** | A: acee, aee, baseline, ucl, ufep, uis, urat, utce · B: rib, ucaf, uaie, urrc, uei, uer, umk, uprf, ucda, mcos, ucef |
| **O-2** | Declaration surface, **no** registry evidence | **3** | rfp (A), uccep (B), uaep (B) |
| **O-3** | **No** declaration surface, registry producer evidence exists | **7** | corpus, assimilate, roadmap, uar, lifecycle-closure, closure009, closure009-baseline |
| **O-4** | Neither declaration surface nor registry evidence | **16** | C: closure, closure-phase2, closure-phase3, final-closure · D: all 12 |

**D-1.1.** Tier O-1 (19 targets) is the strongest position in the repository: a capable
declaration surface exists *and* the registry independently corroborates producer-ness. Mode
classification here is evidence-backed before a single measurement run.

**D-1.2.** Tier O-3 (7 targets) is the inverse asymmetry: the repository already treats these
gates as producers of 67 registered artifacts, yet none has a surface on which to declare it.
The knowledge exists; the declaration location does not.

**D-1.3.** Tier O-4 (16 targets) is the true unknown. Sixteen gate targets are neither
declared nor registered. GATE-PURITY §2.2 classifies several as read-only by construction
(`selfaware-gate`, `homing-gate`, `constitution`/`convergence`/`freeze` report paths), but
"by construction" is precisely the undeclared status GP-11 records.

---

## 3. Question 2 — Existing Canonical Surface for Each Target

### 3.1 Class A — `*-declaration.json` (9)

| Gate | Canonical surface | `programme` | `fwp` | Registry producer |
|---|---|---|---|---:|
| `acee-gate` | `00-MASTER/ACEE-000001/acee-declaration.json` | object | yes | 17 artifacts |
| `aee-gate` | `00-MASTER/UCOS-AEE-001/aee-declaration.json` | object | yes | 15 |
| `baseline-gate` | `00-MASTER/BASELINE-001/baseline-declaration.json` | object | yes | 8 |
| `rfp-gate` | `00-MASTER/UCOS-RFP-001/rfp-declaration.json` | object | **no** | 0 |
| `ucl-gate` | `00-MASTER/UCL-000001/ucl-declaration.json` | object | yes | 15 |
| `ufep-gate` | `00-MASTER/UCOS-UFEP-001/ufep-declaration.json` | object | yes | 5 |
| `uis-gate` | `00-MASTER/UIS-001/uis-declaration.json` | object | yes | 10 |
| `urat-gate` | `00-MASTER/UCOS-URAT-001/urat-declaration.json` | object | yes | 5 |
| `utce-gate` | `00-MASTER/UCOS-UTCE-001/utce-declaration.json` | object | yes | 5 |

### 3.2 Class B — Domain-Named Declaration Surface (13)

| Gate | Canonical surface | `programme` | `fwp` | Registry producer |
|---|---|---|---|---:|
| `rib-gate` | `rib-blueprint.json` | object | yes | 16 |
| `ucaf-gate` | `ucaf-authority.json` | object | yes | 10 |
| `uaie-gate` | `uaie-architecture.json` | object | no | 10 |
| `uccep-gate` | `uccep-bindings.json` | object | yes | 0 |
| `urrc-gate` | `urrc-bindings.json` | object | yes | 19 |
| `uei-gate` | `uei-evolution.json` | object | yes | 24 |
| `uer-gate` | `uer-resilience.json` | object | — | 15 |
| `umk-gate` | `umk-kernel.json` | object | — | 9 |
| `uprf-gate` | `upf-provider.json` | object | — | 9 |
| `ucda-gate` | `ucda-decisions.json` | object | — | 9 |
| `mcos-gate` | `mcos-civilization.json` | object | — | 9 |
| `ucef-gate` | `ucef-framework.json` | object | — | 14 |
| `uaep-gate` | `uaep-platform.json` | object | — | 0 |

**D-2.1.** The Class B naming convention is consistent and legible: `<prefix>-<domain>.json`
is the authored declaration; `<prefix>.json` is the generated output. This is not disorder —
it is a convention the IAR did not observe.

### 3.3 Class C — No Declaration Surface (11)

| Gate | Home | Surfaces present | Why not an ownership surface |
|---|---|---|---|
| `closure-gate` | `UAKOS-CLOSURE-002` | `closure.json`, `phase2.json`, `phase3.json` | no `programme` object |
| `closure-phase2-gate` | `UAKOS-CLOSURE-002` | same | same |
| `closure-phase3-gate` | `UAKOS-CLOSURE-002` | same | same |
| `closure009-gate` | `UAKOS-CLOSURE-009` | — | none with `programme` object |
| `closure009-baseline-gate` | `UAKOS-CLOSURE-009` | — | same |
| `corpus-gate` | `UKAP-001` | `corpus.json`, `EVIDENCE-MANIFEST.json` | no `programme` object |
| `assimilate-gate` | `UAKOS-CLOSURE-008` | — | none |
| `roadmap-gate` | `UCOS-MXR-001` | `roadmap.json` | no `programme` object |
| `lifecycle-closure-gate` | `P0-LIFECYCLE-CLOSURE-001` | — | none |
| `final-closure-gate` | `P0-FINAL-CLOSURE-002` | 9 certification JSONs | `programme` is a **string** where present |
| `uar-gate` | `UCOS-UAR-001` | `uar-analyses.json` | `programme` is a **string** — no field insertable |

### 3.4 Class D — No `00-MASTER` Home (12)

| Gate | Implementation | Nearest authored surface | Has `programme` object |
|---|---|---|---|
| `cmg-gate` | `00-CMG/tools/cmg-gate.sh` | `00-CMG/CMG-REGISTRY.json` | **no** — identifier families, conformance map, namespaces |
| `selfaware-gate` | `engine.knowledge.cli` | **none** | — |
| `rpi-gate` | `platform.repository_intelligence.cli` | **none** | — |
| `homing-gate` | `platform.universal_ownership.cli` | `catalog/ucos-ownership-declarations.json` | **no** — `provider_id`, `assignments` |
| `constitution-gate` | `platform.universal_foundation.constitution_cli` | `catalog/foundation-*.json` | **no** — `register_id`, `criteria` |
| `convergence-gate` | same | `catalog/foundation-convergence.json` | **no** |
| `freeze-gate` | same | `catalog/foundation-freeze.json` | **no** |
| `foundation-gate` | `platform.universal_foundation.cli` | `catalog/foundation-*.json` | **no** |
| `uapf-gate` | `platform.universal_pipeline.cli` | `catalog/uapf-pipelines.json` | **no** — `catalog_id`, `pipelines` |
| `research-gate` | `intelligence.research` | `intelligence/UCOS-URI-001/*.json` | `programme` is a **string** |
| `publication-gate` | `intelligence.publication` | `intelligence/UCOS-UPI-001/*.json` | `programme` is a **string** |
| `research-publication-gate` | aggregator (`research-gate publication-gate`) | **none of its own** | — |

**D-2.2.** Class D surfaces are not missing — they are **differently purposed**. A criteria
register, a pipeline catalog, an ownership-assignment catalog, and an identifier registry each
serve a distinct function. None is a programme execution-mode declaration, and none has a slot
for one.

### 3.5 The Two Declarations That Own No Gate

`uga-declaration.json` and `urr-declaration.json` correspond to **no** `*-gate` target. UGA
gates through the `uga_engine.py gate` subcommand; URR has no gate target. Both are outside
the 45-target denominator, in addition to being structurally incapable (AMC D-4, D-5).

**D-2.3.** Resolving owner decisions O-4 (UGA) and O-5 (URR) would raise `*-gate` coverage by
**zero** targets. Their priority is correspondingly low. Confirms rebase §3.3.

---

## 4. Question 3 — Targets Without Ownership Surface

### 4.1 Count and Composition

**23 of 45 gate targets have no surface capable of carrying a `gate_mode`.**

| Group | Count | Character of the gap |
|---|---:|---|
| Class C — `00-MASTER` home, no capable surface | 11 | Location exists; surface instance absent |
| Class D — no `00-MASTER` home | 12 | Neither location nor surface model |

Subdivided by whether the repository nonetheless holds producer evidence:

| Group | Count | Position |
|---|---:|---|
| No declaration surface, **but** registry producer evidence (Tier O-3) | **7** | Producer-ness is documented; the declaration has nowhere to live |
| No declaration surface **and** no registry evidence (Tier O-4) | **16** | Genuinely undetermined |

### 4.2 The Structural-String Sub-Case

Three surfaces exist, are authored, and are non-generated, yet cannot receive a field because
`programme` is a **JSON string** rather than an object:

| Surface | Gate | Class |
|---|---|---|
| `00-MASTER/UCOS-UAR-001/uar-analyses.json` | `uar-gate` | C |
| `intelligence/UCOS-URI-001/*.json` | `research-gate` | D |
| `intelligence/UCOS-UPI-001/*.json` | `publication-gate` | D |

Plus `urr-declaration.json`, which owns no gate. **D-3.1.** These are the cheapest
theoretical fixes and the most constitutionally awkward: converting a string to an object is a
**structural change** to an authored governance surface, which IADR §5 and CIEP §1.3 forbid
("reused without structural change beyond the additive `gate_mode` field").

---

## 5. Question 4 — Whether Existing Surfaces Can Be Extended

### 5.1 Per-Class Determination

| Class | Extendable? | Basis |
|---|---|---|
| **A** (9) | **YES** — purely additive | `programme` is an object; 8 of 9 already carry `forbidden_write_prefixes` as the placement anchor. `rfp` lacks the anchor but the object exists. |
| **B** (13) | **YES structurally** — purely additive | All 13 carry a `programme` object; 6 carry `forbidden_write_prefixes`. Identical operation to Class A; only the filename differs. |
| **C** (11) | **NO** | There is no surface to extend. Coverage requires a new file instance. |
| **D** (12) | **NO** | Surfaces exist but none carries a `programme` object. Extension means adding a mode block to a surface whose purpose is unrelated. |

**Extendable without any structural change: 22 of 45.** Authorized today: 4.

### 5.2 Candidate Shared Surfaces — Each Assessed and Refused

Four existing surfaces could in principle host modes for the uncovered 23. Each was examined
directly.

#### 5.2.1 `00-BOOK/DATA/mutation-governance-boundary.json` — **CANNOT**

Measured structure: `authorities` (7 entries, keys `authority` / `implementation` / `governs`
/ `does_not_govern` / `enforcement`), `mutation_classes` (5 entries, keys `class` / `examples`
/ `governed_by`), `invariants` (5), `recurrence_prevention` (6).

The 7 authorities resolve to 6 implementations: `engine/constitution/gateway.py`,
`scripts/ucos-env.sh::ucos_ruff_gate`, `verify.sh`, `rib_engine.py`, `aee_engine.py`,
`final_closure_engine.py`.

| Finding | Consequence |
|---|---|
| Keyed by **authority**, not by gate entry point | No per-gate slot exists |
| Covers at most **3 of 45** gate targets (`rib-gate`, `aee-gate`, `final-closure-gate`) | 42 targets have no entry to extend |
| No mode field, no mode vocabulary | Hosting modes requires a new collection |

**D-4.1.** Adding a per-gate mode collection to this file is a structural change to an
authority surface, forbidden by IAR §4 and IADR §5. **REFUSED.**

#### 5.2.2 `00-BOOK/DATA/generated-artifact-registry.json` — **MUST NOT**

This surface is materially richer than the H-06 chain assumed. All 344 entries carry:

| Field | Coverage | Relevance |
|---|---:|---|
| `producer` | 344/344 | names the producing engine or command |
| `owner` | 344/344 | names the owning programme |
| `deterministic` | 344/344 | all `true` |
| `regeneration_command` | 344/344 | the command that rewrites the artifact |
| `lifecycle` | 344/344 | all `REGENERATED` |
| `input_closure`, `input_classification`, `consumers`, `validation_owner`, `certification_role` | present | full provenance |

It is technically the most capable candidate. It must nonetheless not be used, for three
independent reasons:

| # | Reason | Source |
|---|---|---|
| 1 | CIEP §1.5 assigns it exactly one role: *generated artifact registration*. Mode declaration is assigned to the programme declaration. Hosting both collapses two authority surfaces into one. | CIEP §1.3–1.5 |
| 2 | IADR §5 forbids modification "beyond what GP-2/GP-4 fixes strictly require" | IADR §5 |
| 3 | GATE-PURITY D-3.6 explicitly refuses reclassifying engines as producers *in the registry* as a way of making current behaviour conformant | GATE-PURITY D-3.6 |

**D-4.2. The registry is the EVIDENCE surface for PRODUCER classification, not the
DECLARATION surface for `gate_mode`.** This distinction is the resolution of the apparent
Knowledge Once conflict — see §7.

#### 5.2.3 Makefile target comments and script headers — **REFUSED ON EVIDENCE**

This is the existing precedent for Class D. Two of the four modes GATE-PURITY credits are
declared exactly this way:

- `cmg-gate`: `00-CMG/tools/cmg-gate.sh` header lines 1–13 — declares the single permitted
  meta gate, fail-closed exit semantics, and `--emit` as optional usage.
- `rpi-gate`: Makefile line 266 — *"HONEST LIMIT: emit writes to
  `.runtime/repository-intelligence/`, and `.gitignore:12` excludes `.runtime/`."*

GATE-PURITY D-3.4 lists "Mode declared at the pipeline level: `verify.sh` per-stage headers"
as a reference implementation.

**And GP-5 is the counter-proof.** `verify.sh` stage 4's header declared *"Read-only
eligibility/validity/classification gate"* and the stage performs an always-on audit write
via `ukb.py:1997` → `_enforcement_audit()`. The comment was **false**, and nothing detected
it because a comment is not machine-readable and no guard reads it.

**D-4.3.** Comment-level declaration is unenforceable by construction. Extending it to 23
targets would create 23 unverified mode claims — reproducing GP-5 at scale and defeating the
purpose of GP-11. **REFUSED as the primary mechanism.** It remains acceptable as
*documentation accompanying* a machine-readable declaration, never as a substitute.

#### 5.2.4 `platform/providers/catalog/declared-providers.json` — **WRONG OBJECT CLASS**

The provider model is the closest existing analogue to a mode declaration. `TEMPLATE.provider.json`
defines `identity`, `interface`, `entry_point`, `capabilities`, and each capability carries
`deterministic` and **`effects`**. The declared vocabulary across the 13 providers is:

```
net:read x24 · api:read x9 · fs:read x6 · net:send x1
```

**This is a working declared-effects model already in the repository.** It proves the pattern
is native, not novel.

**D-4.4.** It governs **providers** — external data sources (`ucos.documentation`,
`ucos.research`, `ucos.patent`, `ucos.financial`, …) — not gate entry points. None of the 13
corresponds to any of the 45 gate targets. Using it would mean declaring gates as providers,
a category error. **REFUSED as a host; CITED as precedent** that effect declaration is an
established repository pattern.

---

## 6. Question 5 — Whether Any New Governance Surface Is Constitutionally Required

### 6.1 The Determinative Distinction

IADR §5 forbids "Creation of any new governance surface or authority layer." CIEP §4 forbids
"Creating any new registry or authority surface." Neither phrase distinguishes two materially
different acts:

| Act | Character | Example |
|---|---|---|
| **New surface class** | Introduces a schema family, an authority, and a new place where truth lives | A `gate-mode-registry.json` |
| **New surface instance** | Adds another member to a schema family already instantiated *n* times | A 12th `*-declaration.json` |

**D-5.1.** Instantiating an existing surface class is **not** creating a new governance
surface. The `*-declaration.json` class exists, is instantiated 11 times, is read by the
`--check-declaration` guard in 23 engines, and carries an established schema. A 12th instance
adds no authority layer, no schema family, and no new place where truth lives. It adds a
member to a population the constitution already recognises.

This distinction is not a loophole. The prohibition exists to prevent *duplicate governance
surfaces* — two places where the same truth is recorded. A per-programme declaration for a
programme that has none creates no duplication; it fills a hole in an existing model.

### 6.2 Determination Per Class

| Class | Targets | New surface **class** required? | What is required |
|---|---:|---|---|
| **A** | 9 | **NO** | Additive field only. Authorized for 4. |
| **B** | 13 | **NO** | Additive field only. Requires owner extension O-3 for the naming difference. |
| **C** | 11 | **NO** | New **instances** of the existing `*-declaration.json` class in existing `00-MASTER` homes. Requires authorization (IAR §1.1 covers amendment, not creation) — but is not constitutionally novel. |
| **D** | 12 | **CONDITIONALLY YES** | See §6.3 |

**33 of 45 require no new governance surface class.**

### 6.3 Class D — The Only Genuine Constitutional Question

Class D has no `00-MASTER` programme home. Every candidate host was examined and refused
(§5.2). Three dispositions exist:

| Option | Mechanism | New surface class? | Assessment |
|---|---|---|---|
| **D-α** | Create a per-module declaration model for `platform/*` and `intelligence/*` | **YES** | A genuinely new governance surface. Requires an owner decision that H-06 does not hold and this determination cannot supply. |
| **D-β** | Declare Class D **explicitly out of scope** of the programme declaration model; govern its modes at the pipeline level and record the exclusion as a named, owned gap | **NO** | Available immediately. Uses the existing `ASSESSMENT-CONFLICT-REGISTER.md` gap mechanism (R-4 control C-5). Honest, falsifiable, creates nothing. |
| **D-γ** | Extend an unrelated existing surface (foundation catalogs, CMG registry, provider catalog) | Effectively yes | Refused in §5.2 — category error and structural change. |

**D-5.2. A new governance surface is NOT constitutionally required.** Option D-β covers Class
D without creating anything, by recording 12 named gaps with owners rather than fabricating
coverage. Option D-α is *elective* — it buys machine-enforceable coverage for 12 targets at
the cost of a new surface class and an owner decision.

**D-5.3.** The constitutionally minimal path to a coherent ownership model:

```
22 targets (A+B)  → extend existing surfaces, additive field, no new anything
11 targets (C)    → new INSTANCES of the existing declaration class  [owner authorization]
12 targets (D)    → explicit scoped exclusion + named gap registration  [no new surface]
────────────────────────────────────────────────────────────────────────────
45 targets accounted for; zero new governance surface classes created
```

**D-5.4.** Under this path the ownership model is *complete* — every gate target is either
declared or explicitly excluded with a named owner — while creating no registry, no authority
layer, and no schema family. That is the strongest available reading of Knowledge Once and
Canonical Ownership simultaneously.

---

## 7. Knowledge Once Analysis — `replay_path` vs `regeneration_command`

The registry's richness raises a genuine duplication question: if
`generated-artifact-registry.json` already records `regeneration_command` for all 344
artifacts, does adding `replay_path` to a PRODUCER declaration duplicate it?

**Measured `regeneration_command` values:**

```
python3 00-MASTER/ACEE-000001/acee_engine.py
python3 00-MASTER/UCL-000001/ucl_engine.py
python3 00-MASTER/UAKOS-CLOSURE-008/assimilation_engine.py --render
make uaie
make uaue-render
```

These are **write** commands. They regenerate the artifact on disk.

`replay_path`, per IAR §1.6 and IADR §4.3, must "regenerate in memory, compare committed
bytes **without writing first**, and exit non-zero on any difference."

**D-6.1. `regeneration_command` and `replay_path` are different obligations.**
One writes; the other proves without writing. Recording both is not duplication — it is the
render/verify separation that GATE-PURITY D-3.4 identifies as the correct pattern
(`engine/uaue/gate.py`: `--gate`/`--replay` vs `--render`). **Knowledge Once is preserved.**

### 7.1 Adjacent Finding — The Registry Asserts Determinism It Cannot Prove

All 344 entries carry `deterministic: true`. GP-4 establishes that three `*-replay` targets
(`ucl-replay`, `ufep-replay`, `uis-replay`) are indistinguishable from their gates because the
`--render` flag is declared and never read — so they render then diff, and cannot prove
reproduction. GP-3 adds 8 further targets that write before comparing.

**D-6.2.** `deterministic: true` in the registry is, for at least 11 targets, an **unverified
assertion of the same class as GP-5's false "Read-only" label**. It is recorded here as an
observation, not a finding: raising it as a new GP finding is outside this determination's
question set, and **correcting the registry is forbidden** by IADR §5. It bears on H-06 only
in this respect: a PRODUCER's replay contract must be tested, never inferred from the
registry's `deterministic` field.

---

## 8. Question 6 — Revised GP-11 Closure Criteria

### 8.1 Basis for Revision

Rebase determination §6.1 established four defects in GP-11 (wrong denominator, inflated
numerator, two planes conflated, closure unreachable). The ownership model adds a fifth:

**D-7.1 — fifth defect: GP-11 presumes a uniform ownership model that does not exist.**
Its closure criterion "46/46 carry verified mode" presumes every gate target has a surface on
which a mode can be carried. Measurement shows 22 do, 11 could via instantiation, and 12
cannot without a new surface class. A criterion cannot require a declaration where no
declaration location exists.

### 8.2 Revised GP-11 — Split by Plane, Scoped by Ownership Class

| Finding | Statement at HEAD `1f869865` | Closure Criterion | Reachable |
|---|---|---|---|
| **GP-11a** | `*-gate` plane: mode declared for **2 of 45**. Ownership surface exists for 22, instantiable for 11, absent for 12. | Every Class A and B target carries a measured `gate_mode` (22); every Class C target either carries one via an authorized new instance or is a registered gap (11); every Class D target is a registered gap under an explicit scoped exclusion (12). **45 accounted, none fabricated.** | **YES** — after O-3 and the Class C/D dispositions |
| **GP-11b** | `*-self` plane: 26 guard families read-only by construction, undeclared. | Each guard family is declared read-only **or** registered as a named gap. GATE-PURITY §2.2 already establishes read-only by construction, so no behavioural change is required. | **YES** |

### 8.3 Closure States Under Current Authorization

| Finding | State after authorized H-06 execution | Terminal condition |
|---|---|---|
| GP-11a | **OPEN (residual — scope-bounded)** — 4 of 45 declared, 41 registered as gaps | CLOSED only after O-3 (Class B), Class C instantiation authority, and a Class D disposition |
| GP-11b | **OPEN (residual)** — untouched by authorized scope | CLOSED when the 26 guard families are declared or registered |

**D-7.2.** GP-11 must not be marked CLOSED, nor closed with a qualifier that reads as closure
in a summary table. Confirms rebase D-5.2.

**D-7.3.** The revised criterion is *satisfiable* — which the original was not — because it
accepts a registered gap as a valid terminal state for a target with no ownership surface.
A declared mode and an owned, named absence are both honest. A fabricated mode is neither.

---

## 9. Question 7 — Revised Foundation Freeze Gate-Purity Acceptance Criteria

### 9.1 Revision Basis

Rebase §7 established that condition 1 is unreachable, condition 3 is inverted, and a fourth
condition (no claim resting on uncommitted work) is required. The ownership model refines
condition 1 and adds a fifth.

### 9.2 Revised Criteria

| # | Condition | Test | State after authorized H-06 |
|---|---|---|---|
| **F-1** | Mutation boundaries declared **or explicitly owned as absent**, with population stated | Declared count / 45 + registered-gap count / 45; sum must equal 45 | **NO** — 4 declared, 41 gaps not yet registered |
| **F-2** | Replay integrity proven for every declared PRODUCER | In-memory regeneration + byte compare, tested in both directions. **Not inferred from the registry's `deterministic` field** (§7.1) | Reachable for declared PRODUCERs only (≤4) |
| **F-3** | Evidence chain trustworthy over the declared set, **with the undeclared remainder reported** | Per-surface trust + explicit undeclared count. Never assert trust without the denominator. | Reachable, with 41 reported |
| **F-4** | No gate-purity claim rests on uncommitted work | Every count re-measured against HEAD | **FAIL currently** — GATE-PURITY §1 counts and 2 of its 4 declared modes are uncommitted |
| **F-5** **(new)** | Every gate target has a resolved **ownership disposition**: declared · instantiable-and-authorized · explicitly excluded | 45 targets × one disposition each; no target unclassified | **NO** — 12 Class D targets have no disposition |

**D-8.1 — why F-5 is necessary.** F-1 counts declarations and gaps. It does not require that
a gap be *resolvable*. Without F-5, 12 Class D targets could sit indefinitely as "gaps"
with no determination of whether they are ever declarable — which is how GP-11 reached 42
undeclared over years of development, as the R-4 evidence determination observes. F-5 forces
each target to a disposition, and "explicitly excluded" is an acceptable one. An unexamined
gap is not.

### 9.3 Determination

**D-8.2.** Foundation Freeze gate-purity criteria require modification: F-1 restated to admit
owned absence, F-3 de-inverted, F-4 and F-5 added, F-2 strengthened against registry
inference.

**D-8.3. Gate purity cannot be declared closed by executing H-06 as authorized.** After every
authorized action succeeds: 4 of 45 declared, F-1 NO, F-5 NO. Gate purity remains a Foundation
Freeze blocker. Confirms rebase D-6.3.

**D-8.4.** The ownership model makes closure *reachable* for the first time. Under §6.3's
minimal path — 22 extended, 11 instantiated, 12 explicitly excluded — F-1 and F-5 both reach
YES with **zero new governance surface classes**. The blocker is owner authorization, not
constitutional impossibility.

---

## 10. Determination Summary

| Q | Question | Determination |
|---|---|---|
| 1 | Ownership classification, all 45 | Two axes. Declaration surface: **A 9 · B 13 · C 11 · D 12**. Registry producer evidence: **26 of 45**, all `deterministic: true`. Combined tiers: **O-1 19 · O-2 3 · O-3 7 · O-4 16**. |
| 2 | Existing canonical surface per target | Tabulated §3. Class A: `*-declaration.json`. Class B: `<prefix>-<domain>.json` — a consistent convention the IAR did not observe. Class C: none capable. Class D: surfaces exist but are differently purposed, none with a `programme` object. `uga` and `urr` declarations own **no** gate target. |
| 3 | Targets without ownership surface | **23 of 45** — Class C 11 + Class D 12. Of these, **7 already have registry producer evidence** but nowhere to declare it; **16** have neither. Three surfaces are blocked solely because `programme` is a string. |
| 4 | Can existing surfaces be extended | **22 of 45 — YES**, purely additive, no structural change. Class C/D — NO. Four shared-host candidates examined and refused: `mutation-governance-boundary.json` (authority-keyed, ≤3 of 45, no per-gate slot) · `generated-artifact-registry.json` (evidence surface, not declaration surface) · Makefile/script comments (**GP-5 proves unenforceable**) · provider catalog (wrong object class, but cited as precedent for declared `effects`). |
| 5 | Is a new governance surface constitutionally required | **NO — not for 33 of 45, and not at all if Class D is explicitly excluded.** New *instances* of an 11×-instantiated class are not a new surface. Class D is the only genuine question, with a no-new-surface disposition available (D-β). Minimal complete path: 22 extended + 11 instantiated + 12 excluded = 45 accounted, zero new surface classes. |
| 6 | Revised GP-11 closure criteria | Split **GP-11a** (`*-gate`, 2 of 45) / **GP-11b** (`*-self`, 26). Fifth defect identified: GP-11 presumes a uniform ownership model that does not exist. Revised criterion accepts a **registered, owned gap** as a valid terminal state — making it satisfiable for the first time. Both terminate OPEN (residual) under current authorization. |
| 7 | Revised Freeze gate-purity criteria | **F-1** restated to admit owned absence · **F-2** strengthened: replay must be tested, never inferred from the registry's `deterministic` field · **F-3** de-inverted · **F-4** no claim on uncommitted work · **F-5 new**: every target must reach an ownership disposition. Gate purity **NOT closable** under authorized scope, but now **reachable** without new surfaces. |

### 10.1 What This Resolution Changes

**Improved:** the ownership picture is materially better than the prior determinations
concluded. 22 targets are extendable today rather than 9. The registry independently
corroborates producer-ness for 26 targets, so mode classification for those begins from
evidence rather than from a blank measurement. And a complete ownership model exists that
creates nothing.

**Unchanged:** 4 declarations remain the authorized limit. Class D remains the real gap.
GP-11 and the Freeze conditions remain unsatisfied. Every forbidden action remains forbidden.

**Not done here:** no declaration modified, no `gate_mode` added, no engine modified, no
registry created or altered, no owner policy selected, no implementation executed, no finding
closed.

---

*This document is a determination artifact. It resolves canonical ownership requirements by
measurement at HEAD `1f869865`. It authorizes nothing, creates nothing, selects nothing, and
closes nothing. Every surface named was read to determine its structure, never to change it.
The `generated-artifact-registry.json` and `mutation-governance-boundary.json` analyses in §5
were performed read-only and both surfaces remain byte-unchanged by this determination.*

---

H-06 ownership model resolution complete.
No implementation authorized.
No repository mutation performed.
