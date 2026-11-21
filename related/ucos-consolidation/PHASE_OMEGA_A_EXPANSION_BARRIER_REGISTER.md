# UCOS Ω∞ — PHASE Ω∞-A, DELIVERABLE 3
## Expansion Barrier Register

**AUTHORITY = NONE (DERIVED TRUTH).** Discovery only.

**DEFINITION.** An expansion barrier is any condition under which supporting a new reality requires
source modification, schema modification, enum modification, switch modification, registry
modification, migration, recompilation, governance rewrite or certification rewrite.

**THE DISTINCTION THE DIRECTIVE'S OWN LIST BLURS, and it matters for every row below.** The directive
lists "registry modification" as a barrier alongside "source modification". They are not equivalent,
and treating them as one would make every open-world architecture fail its own test — a registry
*exists* to be modified at runtime. This register therefore separates:

| Kind | Meaning | Barrier? |
|---|---|---|
| **REGISTRATION** | A runtime `declare()` call. No file changes | **No** — this is the mechanism, not the barrier |
| **RECORD BACKFILL** | Existing stored records become incomplete and must be re-derived | **Yes**, and it is unavoidable for some extensions (A-17) |
| **SOURCE EDIT** | A `.py` file must change | **Yes** |
| **SCHEMA EDIT** | A declared shape must change, invalidating stored records | **Yes** |
| **REWRITE** | A subsystem's control flow must be restructured | **Yes**, most severe |

A measured consequence: **eleven kinds of extension were exercised at runtime this session with zero
source edits** (capability, reference domain, reference frame, time scale, ordering relation, ordering
strategy, clock, calendar, governance axis + states, authority tier, codec + transformation). Those
eleven are *not* barriers. What follows is what remains.

---

## 1. BARRIERS IN THE PHASE 2 TREE

### X-01 — A governance rule of an unsupported shape → SOURCE EDIT

| Field | Content |
|---|---|
| **Trigger** | A governance model whose rules are not expressible as "requires a reason" or "blocked while state S is held" |
| **Location** | `engine/omega_governance/state.py`, `Transition` (**measured: exactly 2 guard kinds**), consumed by `state.check` |
| **Examples that fail** | N-of-M approvals; quorum of a federation; permitted only within a declared window; conditional on *another artifact's* state; requires the concurrence of a peer registry |
| **Modification required** | SOURCE EDIT to `Transition` and to `check` |
| **Severity** | **BLOCKING.** Rule 8's "previously unknown governance models" enter only if their rules happen to fit two shapes |
| **Removal** | `Guard` protocol with `evaluate(status, context) -> (bool, reason)`; the present two become registered guards. After this, a new rule shape is a REGISTRATION |

### X-02 — A structured justification → SOURCE EDIT

| Field | Content |
|---|---|
| **Trigger** | A deployment requiring that a reduction of obligation carry a signature, an approver identity, a quorum record or a citation |
| **Location** | `state.Transition.requires_reason`; `state.check` tests `not reason.strip()` |
| **Evidence** | **Measured: edge Ω²-S-12 (`UNGOVERNED → EXEMPTED`) accepted `reason="x"`** |
| **Modification required** | SOURCE EDIT — `reason: str` must become a domain value |
| **Severity** | **BLOCKING** |
| **Removal** | `Justification` as a `Value` in a registered domain with a declared schema and invariants |

### X-03 — An n-ary relationship between domains → SCHEMA EDIT

| Field | Content |
|---|---|
| **Trigger** | A relationship taking more than one source domain — position + time + frame → velocity |
| **Location** | `reference/transformation.py`, `_edges: dict[tuple[str, str], str]`; `Transformation(source, target)` |
| **Modification required** | SCHEMA EDIT to `Transformation`, and `path` must become hypergraph resolution |
| **Workaround, and why it is itself a barrier** | Invent a composite intermediate domain. That is a schema modification with a new authority, so the workaround *is* the barrier |
| **Severity** | **BLOCKING** for Rule 8's "previously unknown science" |
| **Removal** | `sources: tuple[str, ...] -> target` |

### X-04 — A relation needing a fourth semantic property → SOURCE EDIT

| Field | Content |
|---|---|
| **Trigger** | An ordering outcome carrying a weight, a probability or a degree |
| **Location** | `temporal/ordering.py`, `Relation(decided, ordered, coincident)` |
| **Evidence** | A `SUPERPOSED` relation and a `QuantumOrdering` strategy registered successfully this session — **because superposition happened to be expressible as the three existing booleans.** A *weighted* ordering would not have been |
| **Modification required** | SOURCE EDIT to `Relation` and to `assert_consistent` |
| **Severity** | EXPANDABLE. Real, and narrower than X-01 |
| **Removal** | Let a relation carry a declared `properties: Mapping[str, object]` interpreted by the strategy that declared it |

### X-05 — A federated vocabulary → REWRITE

| Field | Content |
|---|---|
| **Trigger** | Two nodes must agree on which domains, states, axes and rules exist |
| **Location** | Every registry in `engine/omega_governance/**` — all in-memory, process-local, with no digest, no version and no comparison operator |
| **Modification required** | **GOVERNANCE REWRITE.** Registries must become governed artifacts with identity, and divergence must become a contradiction class |
| **Severity** | **BLOCKING — highest severity in this register.** Registration works; agreement does not exist. Two nodes will validate the same record differently and both report success |
| **Removal** | Deliverable 9 step 1 |

### X-06 — An unbounded or streaming population → REWRITE

| Field | Content |
|---|---|
| **Trigger** | More artifacts than fit in memory, or a population that never ends |
| **Location** | `state.census`, `state.assert_total`, `state.separation_report`, `state.population_of`, `authority.resolve_all`, `authority.fallback_density` |
| **Modification required** | REWRITE of every reporting function to a mergeable form |
| **Severity** | **CRITICAL.** Rule 9's "indefinite growth" holds for the vocabulary and fails for the population |
| **Removal** | Express each census as a commutative monoid so partial censuses compose |

### X-07 — Many governance axes → PROOF LOSS (no code change, and worse for it)

| Field | Content |
|---|---|
| **Trigger** | Registering enough axes that the exhaustive invariant proof stops terminating usefully |
| **Location** | Phase 2 design, `invariants.unknown_never_certifies` |
| **Evidence** | **Measured: 6 axes → 900 vectors; 7 → 1,800; 10 → 48,600; 20 → 2,869,781,400** |
| **Modification required** | **None — and that is precisely why this is the most dangerous entry here.** No error is raised, no test fails, no migration is demanded. The proof simply stops being runnable, and the architecture continues to advertise it |
| **Severity** | **CRITICAL, self-inflicted.** The barrier tightens as the extension mechanism is used as intended |
| **Removal** | Replace enumeration with a per-axis argument: nothing targets `UNKNOWN`, and `CERTIFIED`'s guard names `UNKNOWN`. Both O(edges), independent of axis count. Keep enumeration as a small-size cross-check. Deliverable 9 step 2 |

### X-08 — A new governance axis → RECORD BACKFILL

| Field | Content |
|---|---|
| **Trigger** | Registering a seventh governance concern |
| **Location** | `state.assert_total` |
| **Evidence** | **Measured: after registering a 7th axis, a status built under 6 axes causes `assert_total` to raise and name the gap** |
| **Modification required** | RECORD BACKFILL. **No source edit and no schema edit** — the code needs nothing; the stored records need a position on the new axis |
| **Severity** | **FUNDAMENTAL, and a correction to Rule 9.** The directive's success chain reads "Registration Only → No Source Modification → No Migration". For axis registration the first two hold and the third cannot. New knowledge about what must be governed necessarily makes prior records incomplete. Reporting that population is the honest behaviour, and it is what happens |
| **Removal** | None. Rule 9 should distinguish *code* migration from *record* backfill |

### X-09 — A non-encodable artifact → NO PATH

| Field | Content |
|---|---|
| **Trigger** | Governing something not reducible to bytes: a physical specimen, a live process, a continuous field |
| **Location** | `reference/domain.assert_encodable`; every fingerprint |
| **Modification required** | None available |
| **Severity** | **FUNDAMENTAL.** See Deliverable 8 |
| **Mitigation** | Make the proxy relationship a declared transformation with an authority and `lossy=True`, so the substitution is recorded rather than assumed |

### X-10 — A non-Python governance engine → SOURCE PORT

| Field | Content |
|---|---|
| **Trigger** | An engine in another language participating |
| **Location** | The whole tree; contracts are `typing.Protocol` |
| **Modification required** | A port. **And the schema document a porter would implement against does not exist** — `schema.py` was designed and not written |
| **Severity** | CRITICAL for Rule 6 as *consumable*; the design satisfies Rule 6 as *describable* |
| **Removal** | Emit the contracts as language-neutral schema documents. The residual — that this artifact is Python — is not removable, and conflating "the architecture is language-neutral" with "the implementation is" would itself be the assumption |

### X-11 — A total-order register meeting concurrent events → DESIGN CHANGE BEFORE BUILD

| Field | Content |
|---|---|
| **Trigger** | Two federated observers appending concurrently |
| **Location** | Phase 2 design's hash-chained `GovernanceRegistry` — **unbuilt** |
| **Description** | A hash chain requires each entry to name exactly one predecessor, imposing a total order on records whose *coordinates* the same architecture declares `CONCURRENT` |
| **Modification required** | If built as chained: REWRITE. If designed now: none |
| **Severity** | **BLOCKING**, and the cheapest item in this register to fix because the code does not exist yet |
| **Removal** | Merkle **DAG**: an entry names all predecessors it observed; concurrent appends produce siblings; total order becomes a projection a caller may request, never a property the register asserts |

### X-12 — Cross-deployment identifier collision → REWRITE

| Field | Content |
|---|---|
| **Trigger** | Two deployments minting `Ω²-S-37` for different edges |
| **Location** | Flat identifier namespaces throughout |
| **Modification required** | REWRITE of identifier resolution to `(authority, identifier)` |
| **Severity** | REPLACEABLE alone; **BLOCKING in combination with X-05**, where it produces silent semantic divergence |

---

## 2. BARRIERS IN THE LEGACY TREES

Recorded for completeness. **None is actionable in this phase** — Phase 2's constraint is integration
through adapters with no rewriting of existing systems, and the directive forbids modifying active
governance, certification, validation and ratchets.

| ID | Trigger | Location | Modification | Severity |
|---|---|---|---|---|
| X-13 | A sixth Ω-1 disposition | `engine/universal_discovery/model.py:50-70`; exhaustive membership at 8 sites (`classification.py:197`, `gate.py:70`, `gate.py:81`, `surface.py:340`, `surface.py:351`, `surface.py:395`, `ratchet.py:153`, `certification_integrity/contract.py:130`) | SOURCE EDIT at 8 sites | CRITICAL |
| X-14 | A fifth ratchet kind | `model.py` `RATCHET_KINDS`; validated in `ratchet.py:153` and `certification_integrity/contract.py:130` | SOURCE EDIT | REPLACEABLE |
| X-15 | A ninth UCI object kind, or file class, or seventh plane type | `engine/certification_integrity/model.py:27,51,67,84,117` | SOURCE EDIT + declaration update | REPLACEABLE |
| X-16 | An eighth uncovered-line class | `model.py:117` `REMEDY` dict — a closed mapping *with a mandatory remedy per key*, which is a good design and still a closed list | SOURCE EDIT | REPLACEABLE |
| X-17 | Any new value in any of 264 enumerations | 264 enums / 1,372 members: `platform/` 128/651, `engine/` 74/468, `application/` 22/98, `data/` 18/59, `service/` 14/47, `infrastructure/` 4/19, `intelligence/` 4/30 | ENUM MODIFICATION, sometimes + migration | CRITICAL (aggregate) |
| X-18 | A new verification stage | `verify.sh` hard-coded `run_stage` literals; the stage label is a three-reader contract (`verify.sh`, `00-MASTER/UAKOS-CLOSURE-008/validation-record.json`, `.github/workflows/uisd-gate.yml`) | SOURCE EDIT in 3 places + declaration | EXPANDABLE by design — the triple-binding is deliberate and refuses silent skipping |
| X-19 | A governance surface outside one repository | 42 git-invoking files; `pytest_scope.py`; `verify.sh` | REWRITE | CRITICAL |
| X-20 | A representation other than JSON, or an identity other than SHA-256 | 404 `json` imports, 56 `hashlib`, 4 `uuid` | SOURCE EDIT at every record site | CRITICAL |

---

## 3. WHAT IS **NOT** A BARRIER — measured

Recorded because a register of barriers is only credible next to what was tested and passed. All
eleven exercised at runtime this session, zero source edits, against `engine/omega_governance/**`:

| Extension | Result |
|---|---|
| New capability (`SUPERPOSED`) | registered |
| New reference domain (`QUANTUM_ORDERING`, 15th) | registered; value validated with **no findings**; fingerprinted under a non-JSON codec and a non-SHA-256 digest |
| New reference frame (`INTERSTELLAR`, barycentric) | registered |
| New time scale (`PARSEC_TRANSIT`, non-numeric) | registered |
| New ordering relation (`SUPERPOSED`) | registered |
| New ordering strategy (`QuantumOrdering`) | registered |
| New clock (`civ-herald`, non-numeric position) | registered; `assert_provider` passed |
| New calendar (`civilization-epochal`) | registered |
| **New governance axis + 2 states (`PROVENANCE`, 7th axis)** | registered; registry reports 7 axes |
| **New authority tier (`INTERCIVILIZATION`, rank 8)** | registered; resolved `CIV-COUNCIL` by `Ω²-A-08` — the case that raised `KeyError` before the A-03 fix |
| New codec + new transformation | registered; the transformation correctly reports as **uncomputable** rather than approximating |

---

## 4. SEVERITY SUMMARY

| Severity | Phase 2 tree | Legacy | Total |
|---|---|---|---|
| BLOCKING | X-01, X-02, X-03, X-05, X-11 (5) | — | 5 |
| CRITICAL | X-06, X-07, X-10 (3) | X-13, X-17, X-19, X-20 (4) | 7 |
| FUNDAMENTAL | X-08, X-09 (2) | — | 2 |
| EXPANDABLE / REPLACEABLE | X-04, X-12 (2) | X-14, X-15, X-16, X-18 (4) | 6 |

**Cheapest high-value fixes, in order:** X-11 (the code does not exist yet), X-07 (replace a proof
method, no interface change), X-01 + X-02 (one `Guard` protocol closes both), X-05 (registry digests).
Sequenced in Deliverable 9.
