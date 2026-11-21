# UCOS Ω∞ — PHASE Ω∞-A, DELIVERABLE 4
## Closed-World Dependency Register

**AUTHORITY = NONE (DERIVED TRUTH).** Discovery only. No enum in any legacy tree was modified.

**THE TEST APPLIED.** Ω∞ Rule 4 requires every closed list be *challenged*, and separating true
invariants from accidental limitations needs a test rather than an opinion. The test used here:

> **A closed list is a TRUE INVARIANT if and only if a consumer must handle every member, and a new
> member would change what every consumer is obliged to do.**

By that test a two-valued verdict is a true invariant: adding a third outcome to `PASS`/`FAIL`
genuinely changes every caller's obligation, so the closedness is carrying real meaning. A taxonomy of
33 facets is an accidental limitation: no consumer branches on all 33, so the enum is a *namespace*
wearing an enum's clothing — and a namespace that cannot be extended at runtime is the structural limit
Ω∞ exists to remove.

**A SECOND TEST, for the cases the first leaves ambiguous:**

> If the list grew by one, would existing code be *wrong*, or merely *incomplete*? Wrong ⇒ invariant.
> Incomplete ⇒ accidental.

---

## 1. MEASURED INVENTORY

2,178 Python files walked. **264 enumerations, 1,372 members.**

| Tree | Enums | Members |
|---|---|---|
| `platform/` | 128 | 651 |
| `engine/` | 74 | 468 |
| `application/` | 22 | 98 |
| `data/` | 18 | 59 |
| `service/` | 14 | 47 |
| `infrastructure/` | 4 | 19 |
| `intelligence/` | 4 | 30 |
| **Total** | **264** | **1,372** |

Member-count distribution — **the shape is the finding**:

| Members | Enums | Reading |
|---|---|---|
| 1 | 2 | Degenerate. A one-member enum is a constant with ceremony |
| **2** | **49** | Binary verdicts. **Mostly TRUE INVARIANTS** |
| **3** | **72** | The largest bucket. Verdict-plus-unknown, or three-way dispositions. **Mixed** |
| 4–7 | 95 | Dispositions and stages. **Mixed, leaning accidental** |
| 8–12 | 28 | Taxonomies. **ACCIDENTAL** |
| 13–33 | 16 | Vocabularies. **ACCIDENTAL, highest expansion risk** |

**121 of 264 enums (46%) have two or three members.** That concentration is evidence that most of this
codebase's closed lists are genuinely small decision vocabularies rather than taxonomies — which is
better news than the headline count of 264 suggests, and it is why the triage below matters more than
the total.

---

## 2. TRUE INVARIANTS — closed for a reason, keep closed

| Pattern | Instances | Why closed is correct |
|---|---|---|
| `Verdict = PASS \| FAIL` | `platform/validation_intelligence/contracts.py`, `platform/universal_assurance/contracts.py`, `platform/commercial_intelligence/contracts.py`, `engine/validation/contracts.py`, `platform/universal_validation/contracts.py` (`RuleStatus`) | A gate either refuses or does not. A third value changes every caller's obligation, so the closedness is load-bearing |
| `Severity = BLOCKING \| ADVISORY` | 5 sites, identical membership | Whether a finding stops a run is binary by construction: it stops it or it does not |
| `CertificationStatus = CERTIFIED \| NOT_CERTIFIED` | `engine/certification/contracts.py`, `engine/universal_certification/contracts.py` | Fail-closed by design |
| `GovernanceStatus = GOVERNED \| NOT_GOVERNED` | `engine/governance/contracts.py` | As above |
| `Verdict = OPEN \| CLOSED \| FAULT` | `engine/certification_integrity/model.py` | Three-valued *on purpose*: FAULT distinguishes "no verdict reachable" from "verdict is no". **The best-designed closed list in the repository**, and the pattern Phase 2 imitated with `decided`/`ordered` |
| `Selection = IMPACT \| WHOLE_SUITE` | `engine/verification_intelligence/model.py` | A run either narrows or does not |
| `RATCHET_KINDS`, 4 values | `engine/universal_discovery/model.py` | Argued in place: "the four honest shapes a *this must not get worse* claim can take; a fifth shape would be a number somebody chose." **A closed list with a written argument for its closedness — the standard the other 263 should be held to** |

**Roughly 60 of 264 enums** pass the invariant test. They are not expansion barriers, and Ω∞ Rule 4 is
satisfied by *challenging* them and recording why they stay.

---

## 3. ACCIDENTAL LIMITATIONS — highest expansion risk

Ranked by member count, which correlates with taxonomy-ness:

| Enum | Members | Location | Why accidental |
|---|---|---|---|
| `Facet` | **33** | `engine/uckp/facets.py` | A facet vocabulary. No consumer branches on 33 arms; a 34th facet is a fact about the world, not a change to anyone's obligation |
| `RegistryKind` | **29** | `engine/registry/universal/identity.py` | A list of *kinds of registry* — the most self-referentially closed thing found. A new kind of governed thing cannot be registered without editing the registry of registry kinds |
| `ConstitutionalLayer` | 21 | `engine/knowledge/integration/contracts.py` | An architectural layering. Adding a layer is exactly the expansion Ω∞ exists to permit |
| `KnowledgeKind` | 18 | `engine/knowledge/model.py` | Rule 8's "previously unknown categories" lands precisely here |
| `RelationType` | 17 | `engine/knowledge/model.py` | Rule 8's "previously unknown relationship models" lands precisely here |
| `LifecycleStatus` | 17 | `engine/registry/models.py` | A 17-member lifecycle is a state machine in an enum; a new governed lifecycle requires a source edit |
| `ContextKind` | 16 | `engine/context/taxonomy.py` | Named `taxonomy`, which is the tell |
| `CapabilityGroup` | 16 | `platform/identity/contracts.py` | Capability grouping should be a registry — Phase 1 and Phase 2 both demonstrate the pattern |
| `EvolutionStage` | 15 | `engine/uckp/evolution.py` | Evolution stages are the thing most likely to grow |
| `ProviderKind` | 14 | `engine/knowledge/ukip/contracts.py` | A closed list of *provider kinds* inside a provider abstraction — the abstraction's own extensibility is bounded by an enum |
| `MaturityAxis` | 14 | `platform/universal_foundation/constitution.py` | Axes, closed. The same defect Phase 2 fixed in its own `AXES` |
| `ReasoningKind` | 13 | `engine/uckp/intelligence.py` | Rule 8's "previously unknown mathematics" |
| `ConstitutionalDomain` | 13 | `platform/universal_foundation/constitution.py` | Rule 2 requires domains be registrations |
| `DataType` | 12 | `engine/compiler/types.py` | A type system in an enum |
| `ArtifactClass` / `ArtifactKind` / `ArtifactFamily` | 10 / 10 / 7 | `intelligence/kernel/ids.py`, `platform/universal_generator/contracts.py`, `intelligence/realization/contracts.py` | **Three independent closed artifact taxonomies that must agree and have no mechanism to.** Phase 1 replaced this pattern with `ArtifactTypeRegistry` |
| `AdministrativeDomain` | 11 | `platform/administration/contracts.py` | A domain list |

**Highest-risk single finding: `RegistryKind` (29 members).** A registry of registry kinds, closed at
the language level, is the tightest expansion ceiling in the repository — every other extensibility
mechanism that routes through it inherits its closedness.

**Second-highest: the three artifact taxonomies.** `ArtifactClass`, `ArtifactKind` and `ArtifactFamily`
are independently closed, must agree, and cannot be reconciled by any mechanism. Divergence between
them is undetectable today.

---

## 4. NON-ENUM CLOSED WORLDS

Closed lists that are *not* enums are the ones Ω∞ Rule 4 is most needed for, because they do not look
like closed lists. Ω-1's own five assumptions (Deliverable 1, §preamble) were all of this kind.

| ID | Closed world | Location | Members | Consumers | Verdict |
|---|---|---|---|---|---|
| CW-01 | `DISPOSITIONS` | `engine/universal_discovery/model.py:50-70` | 5 | Exhaustive membership at **8 sites**: `classification.py:197`, `gate.py:70`, `gate.py:81`, `surface.py:340`, `surface.py:351`, `surface.py:395`, `ratchet.py:153`, `certification_integrity/contract.py:130` | **ACCIDENTAL** — the specific defect Phase 2 replaced with six axes |
| CW-02 | `AUTHORITY_REQUIRED` | same | 4 of 5 | `gate.py:81` | ACCIDENTAL — the carve-out that makes `authority = ""` legal (A-08) |
| CW-03 | `SURFACE_DISPOSITIONS` | same | 2 of 5 | `surface.py:340`, `surface.py:395` | ACCIDENTAL — argued in place, and still a fixed pair |
| CW-04 | `RATCHET_KINDS` | same | 4 | `ratchet.py:153`, `contract.py:130` | **TRUE INVARIANT** — argued for its closedness |
| CW-05 | `OBJECT_KINDS` | `engine/certification_integrity/model.py:27` | 8 | inventory build | ACCIDENTAL |
| CW-06 | `FILE_CLASSES` + `CLASSES_REQUIRING_MEASUREMENT` | `model.py:51,67` | 8, 2 | classification | ACCIDENTAL |
| CW-07 | `PLANE_TYPES` | `model.py:84` | 6 | UCI-L-05 plane counting | ACCIDENTAL — a new execution plane is Rule 1's "Execution" category |
| CW-08 | `REMEDY` | `model.py:117` | 7 | uncovered-line classification | **MIXED.** The mapping is closed, and it *requires a remedy per class*, which is excellent design. A closed list whose closedness enforces completeness is far better than an open one that permits silence |
| CW-09 | `verify.sh` stage literals | `verify.sh` (20 stages) | 20 | 3 readers: `verify.sh`, `00-MASTER/UAKOS-CLOSURE-008/validation-record.json`, `.github/workflows/uisd-gate.yml` | **TRUE INVARIANT, deliberately.** The triple-binding exists so a stage cannot be silently skipped. Closedness is the enforcement mechanism |
| CW-10 | `FROZEN_PREFIXES` | `engine/foundation/guards/frozen_paths.py` | — | Ω-C-02 disposition | TRUE INVARIANT — a freeze list must be explicit |
| CW-11 | `excluded_packages` | `pyproject.toml` | 1 (`engine.uicm`) | `derive_measurable_packages` | **TRUE INVARIANT, exemplary.** Refused stale in both directions, requires a written reason, reviewed with a date |
| CW-12 | `REQUIRED_STATE_NAMES` | `engine/omega_governance/state.py` | 13 | nothing resolves through it | **ACCEPTED.** The only module-level closed literal collection in the entire Phase 2 tree (measured: 1). A directive-conformance assertion, not a vocabulary |

---

## 5. THE PHASE 2 TREE — measured closed-world dependency

| Property | Measurement |
|---|---|
| Enumerations | **0** |
| `datetime` / `time` imports | **0** |
| `os` / `pathlib` / `shutil` / `glob` imports | **0** |
| `uuid` imports | **0** |
| `json` / `hashlib` imports | **1 file** — `reference/encoding.py`, where both are 2 of 4 shipped providers behind protocols |
| Module-level closed literal collections | **1** — `REQUIRED_STATE_NAMES`, a conformance check |
| Runtime-extensible vocabularies | 11 kinds, all exercised this session with zero source edits |

**Residual closed worlds in the Phase 2 tree, all recorded as barriers in Deliverable 3:** guard kinds
(exactly 2, X-01), relation semantic properties (exactly 3, X-04), transformation arity (exactly 2,
X-03), justification structure (a string, X-02).

---

## 6. SUMMARY

| Classification | Count | Action |
|---|---|---|
| TRUE INVARIANT — keep closed, record the argument | ~60 enums + CW-04, CW-08, CW-09, CW-10, CW-11 | Ω∞ Rule 4 satisfied by challenging and documenting |
| ACCIDENTAL — closed by habit | ~200 enums + CW-01, CW-02, CW-03, CW-05, CW-06, CW-07 | Registry conversion. **Not in this phase** |
| ACCEPTED in new work | CW-12 | None |
| Residual in new work | 4 (X-01 to X-04) | Deliverable 9 |

**THE STANDARD THIS REGISTER PROPOSES.** One closed list in this repository is exemplary:
`RATCHET_KINDS` states, in place, *why a fifth value would be wrong*. That is what distinguishes an
invariant from a habit. The recommendation is not to open all 264 enums — most should stay closed — but
to require that **every closed list carry a written argument for its closedness**, and to treat the
absence of that argument as the finding. A closed list nobody defended is an accidental limitation
whether or not anyone has yet needed to extend it.
