# UCOS Ω∞ — PHASE Ω∞-A, DELIVERABLE 1
## Architectural Assumption Register

**AUTHORITY = NONE (DERIVED TRUTH).** This document discovers and records. It issues no
certification, seals no artifact, advances no ratchet and modifies no active governance, validation
or certification process.

**METHOD.** Mechanical census by AST walk over 2,178 Python files across `engine/`, `platform/`,
`service/`, `data/`, `application/`, `infrastructure/`, `intelligence/`, `realization/`, `scripts/`,
plus a runtime open-world probe attempting eleven kinds of registration against the Phase 2 tree.
Every entry below cites what was measured, not what was believed. Where a claim could not be
measured, the entry says so.

**THE ONE FINDING THAT VALIDATES THE METHOD.** The audit was first run against code written *by this
session, specifically to eliminate hardcoded assumptions*. It found five. None of them was an enum,
and none would have been caught by review:

| # | Assumption | Where it was | Why it survived |
|---|---|---|---|
| 1 | `json.dumps` + `hashlib.sha256` | `temporal/coordinate.py` `identity()` | Representation and Identity hardcoded as requirements. Looks like plumbing, not policy |
| 2 | `Position = tuple[int, ...]` | `temporal/ordering.py` | Measurement assumed numeric. Chosen *because* it made determinism easy |
| 3 | `RULES: dict[int, str]` keyed 1–7 | `authority.py` | An eighth authority tier raised `KeyError` inside `resolve` |
| 4 | `AXES` quantified over in `__post_init__` | `state.py` | A seventh governance axis would refuse construction of every new status |
| 5 | `default_ordering: Ordering = TOTAL` | `temporal/frames.py` | A *default* reinstated the single-ordering assumption for every scale declared without thought |

All five are now closed and each closure is measured in Deliverable 8. They are listed first because
they set the register's confidence level: **assumption discovery by inspection has a demonstrated
false-negative rate above zero, so every "CLOSED" entry below should be read as "closed against the
tests that exist", not "closed".**

---

## 1. CLASSIFICATION LEGEND

| Class | Meaning |
|---|---|
| **FUNDAMENTAL** | Cannot be removed without abandoning the idea of a governance record. Must be *stated*, not fixed |
| **CRITICAL** | Removable, and its presence currently prevents a named future reality |
| **BLOCKING** | Prevents a specific Ω∞ Rule 8 scenario from entering without architectural replacement |
| **REPLACEABLE** | Removable by a bounded, local change |
| **EXPANDABLE** | Not removable, but its capacity is a parameter rather than a constant |
| **HIDDEN** | Not visible as a list, a type or a switch. Discovered only by asking what a future reality would invalidate |
| **UNKNOWN** | Suspected; not measured. Named so it is not mistaken for absent |

---

## 2. REGISTER

### 2.1 Temporal assumptions

| ID | A-01 |
|---|---|
| **Name** | Wall-clock time is available and authoritative |
| **Location** | `engine/construct/evidence.py`, `engine/execution_environment/evidence.py`, `engine/foundation/obs/logging.py`, `engine/graph/evidence.py`, `engine/graph/architecture/evidence.py`, `engine/recursive_knowledge/evidence.py`, `engine/registry/universal/audit.py` (7 files import `datetime`); `engine/certification_integrity/immutable.py`, `engine/certification_integrity/suite.py`, `engine/determinism/hermetic.py`, `engine/foundation/obs/telemetry.py` (4 import `time`) |
| **Description** | Evidence and audit records are stamped from the host clock, in an unstated frame, on an unstated scale, with a total order implied by string sortability |
| **Evidence** | Measured: 11 files. `engine/omega_governance/**` imports neither (measured: 0 occurrences) |
| **Risk** | Two runs over an unchanged population produce different evidence bytes, so a digest difference cannot distinguish a governance change from a scheduling one |
| **Expansion impact** | Blocks simulation replay, historical re-measurement, non-Earth frames, and any two observers without a shared clock |
| **Replacement strategy** | `temporal.clocks.ClockProvider` + `TemporalCoordinate`. Legacy sites reached only through adapters; **not** rewritten |
| **Class** | CRITICAL (legacy) / CLOSED in the Phase 2 tree |

| ID | A-02 |
|---|---|
| **Name** | Every pair of events has an agreed order |
| **Location** | Every `sorted()` over a timestamp; structurally, any `timestamp: str` field |
| **Description** | A sortable timestamp asserts totality. `sorted()` never refuses, so causally unrelated events acquire an order no observation produced |
| **Evidence** | Phase 2 measurement: two `VectorClock` coordinates compare `CONCURRENT`, an outcome no string timestamp can represent. Verified this session |
| **Risk** | A contradiction engine reading a sorted log reports a sequence the sort algorithm invented |
| **Expansion impact** | Blocks distributed governance, forked histories, quantum/probabilistic ordering |
| **Replacement strategy** | `Ordering` as a provider; `Relation` as a registry with `decided`/`ordered`/`coincident` semantics; `INCOMPARABLE` distinct from `CONCURRENT` |
| **Class** | CRITICAL / CLOSED in the Phase 2 tree |

| ID | A-03 |
|---|---|
| **Name** | Gregorian rendering is identity |
| **Location** | Any stored ISO-8601 string |
| **Description** | Storing a rendering makes the calendar part of the record's identity: a format change invalidates a hash chain, and a non-Gregorian observer cannot be recorded |
| **Evidence** | Phase 2 measurement: `assert_presentation_only` holds under both shipped encodings — rendering a coordinate leaves equality and fingerprint unchanged. Gregorian arithmetic exists in exactly one deletable class (`ProlepticCivilCalendar`), implemented without `datetime` |
| **Risk** | Calendar registration becomes a data migration |
| **Class** | REPLACEABLE / CLOSED in the Phase 2 tree |

### 2.2 Measurement, identity and representation assumptions

| ID | A-04 |
|---|---|
| **Name** | Measurement is numeric |
| **Location** | Was `Position = tuple[int, ...]`; broadly, any metric typed `int`/`float` |
| **Description** | A measurement architecture requiring magnitude excludes symbols, grades, lattice elements and ordinal civilisational epochs |
| **Evidence** | Phase 2 measurement: a coordinate with position `("EPOCH-ALPHA",)` compares, encodes and fingerprints. `MEASUREMENT_DOMAIN` deliberately does **not** declare `QUANTITATIVE` |
| **Risk** | A non-numeric measurement system cannot enter without replacing the value type |
| **Replacement strategy** | Opaque components; determinism delegated to the codec's declared `REPRODUCIBLE`; magnitude expressed as the `QUANTITATIVE` capability a consumer *requires by name* |
| **Class** | CRITICAL / CLOSED in the Phase 2 tree |

| ID | A-05 |
|---|---|
| **Name** | JSON is the representation; SHA-256 is the identity |
| **Location** | 404 files import `json`; 56 import `hashlib`; 4 import `uuid` |
| **Description** | Both are architectural requirements rather than registered systems. Ω∞ Rule 1 names all three |
| **Evidence** | Measured. In `engine/omega_governance/**` both are confined to `reference/encoding.py`, where they are two of four shipped providers; the whole pipeline was exercised under `TagLengthValueCodec` + `PolynomialIdentity` this session |
| **Risk** | A deployment whose storage or regulator mandates another representation or digest must edit every record-producing site |
| **Replacement strategy** | `Codec` / `IdentityProvider` protocols; `Encoding` pair passed as a **required argument with no default**, so there is nothing to fall back to |
| **Class** | CRITICAL (legacy, 404 sites) / CLOSED in the Phase 2 tree |

| ID | A-06 |
|---|---|
| **Name** | Everything governed is reducible to bytes |
| **Location** | `reference/encoding.py`; every fingerprint, every hash chain |
| **Description** | A value that cannot be encoded cannot be fingerprinted, so it cannot enter an append-only register. A physical specimen, a live process, a continuous field or an unbounded stream must be *summarised* before it can be governed, and the summary is a different thing from the artifact |
| **Evidence** | Structural. `assert_encodable` refuses rather than stringifying — the refusal is the honest form of the limit |
| **Risk** | Non-software, non-digital artifacts are governed by proxy, and the proxy's fidelity is unstated |
| **Replacement strategy** | None available. The correct response is to make the proxy relationship a **declared transformation** with an authority and a `lossy` flag, so the substitution is visible |
| **Class** | **FUNDAMENTAL** |

### 2.3 Governance and certification assumptions

| ID | A-07 |
|---|---|
| **Name** | A governance state is a scalar |
| **Location** | `engine/universal_discovery/model.py:50-70` — `DISPOSITIONS`, five values, one field |
| **Description** | One field carries custody, scope and measurement at once, so the answers compete for the slot and the loser becomes unrecordable. This is why `MEASURED` came to mean `GOVERNED` |
| **Evidence** | Exhaustive membership tests at 8 sites: `classification.py:197`, `gate.py:70`, `gate.py:81`, `surface.py:340`, `surface.py:351`, `surface.py:395`, `ratchet.py:153`, `certification_integrity/contract.py:130` |
| **Risk** | Every combination Ω-2.5 names is unrepresentable; the silent state is invisible by construction |
| **Replacement strategy** | Six orthogonal axes; `GovernanceStatus` holds one position per axis. Legacy reached by adapter only |
| **Class** | CRITICAL / CLOSED in the Phase 2 tree (legacy untouched, as required) |

| ID | A-08 |
|---|---|
| **Name** | Authority may resolve to nothing |
| **Location** | `engine/universal_discovery/model.py` — `authority: str`, `""` legal for `TRANSIENT`; `authority.py:177-223` |
| **Description** | One artifact class may have no owner, making "every artifact has an authority chain" false, so no invariant can assert it and nothing measures where it fails |
| **Evidence** | `AUTHORITY_REQUIRED` excludes `TRANSIENT` (`model.py`); `gate.py:81` tests only the included dispositions |
| **Replacement strategy** | Unconditional fallback tier constructed by the resolver from a constant, unregisterable and unremovable; arrival recorded as a `FallbackEvent`, measured as a density, ratcheted as CONVERGENT |
| **Class** | CRITICAL / CLOSED in the Phase 2 tree |

| ID | A-09 |
|---|---|
| **Name** | A justification is any non-empty string |
| **Location** | `state.py` `Transition.requires_reason`; also Ω-1 `ratchet.py` justifications and `pyproject.toml` exemption reasons |
| **Description** | The guard is **syntactic**. A reduction of obligation is permitted by any non-blank text |
| **Evidence** | **Measured this session:** the edge `UNGOVERNED → EXEMPTED` (Ω²-S-12) was taken with `reason="x"` and accepted |
| **Risk** | A governance model requiring a signed authorisation, a quorum, a named approver or a citation cannot express it; every such requirement degrades to "somebody typed something" |
| **Expansion impact** | Blocks "previously unknown governance models" (Rule 8) that rest on structured authorisation |
| **Replacement strategy** | Replace `reason: str` with a `Justification` value in a registered domain, whose schema and invariants a deployment declares. The transition guard then requires a *valid* justification, not a non-empty one |
| **Class** | **BLOCKING**, open |

| ID | A-10 |
|---|---|
| **Name** | Two guard kinds suffice for every governance rule |
| **Location** | `state.py` `Transition` — `requires_reason`, `blocked_by` |
| **Description** | **Measured: exactly 2 guard kinds.** A rule of the form "requires N of M approvals", "requires a quorum of a federation", "permitted only within a declared window", or "requires the concurrence of another artifact's state" is not expressible |
| **Evidence** | Measured this session by field inspection |
| **Risk** | An unknown governance model is admitted only if its rules happen to be expressible as a reason plus a state exclusion |
| **Replacement strategy** | Promote guards to a registry: `Guard` protocol with `evaluate(status, context) -> (bool, reason)`; `blocked_by` and `requires_reason` become two registered guards among many |
| **Class** | **BLOCKING**, open |

| ID | A-11 |
|---|---|
| **Name** | Certification has a fixed input set |
| **Location** | Designed, **not yet built** (`certification.py` unwritten at the time of this audit) |
| **Description** | The Phase 2 design named seven certification inputs. Seven fixed inputs is a closed list; a domain whose certification depends on an eighth would require a source edit |
| **Evidence** | Design inspection only. **Not measured — the module does not exist.** Recorded so the barrier is designed out before it is built |
| **Replacement strategy** | Certification inputs must be a *registry* of `CertificationInput` providers, each declaring `required`/`conditional`; the decision function quantifies over the registry, never over a tuple |
| **Class** | UNKNOWN (unbuilt), designated BLOCKING if built as designed |

### 2.4 Discovery, storage, execution and repository assumptions

| ID | A-12 |
|---|---|
| **Name** | Storage is a local filesystem |
| **Location** | 364 files import `os`, `pathlib`, `shutil` or `glob` |
| **Evidence** | Measured. `engine/omega_governance/**` imports none of them (measured: 0) |
| **Risk** | Object stores, databases, graphs, ledgers and distributed memory require a parallel implementation rather than a registration |
| **Replacement strategy** | `STORAGE_DOMAIN` with `provider` + `locator`; records reduce to primitives only (`as_record()`), so the same bytes are writable anywhere |
| **Class** | CRITICAL (legacy) / CLOSED in the Phase 2 tree (**by absence, not by a storage provider — see B-02**) |

| ID | A-13 |
|---|---|
| **Name** | Discovery is `git ls-files`; the world is a repository |
| **Location** | 42 files invoke git through `subprocess`, including `engine/universal_discovery/discovery.py`, `engine/certification_integrity/surface.py`, `engine/enforcement_closure/discovery.py`, `engine/execution_environment/discovery.py` |
| **Description** | Phase 1 addressed this for the discovery *layer*; the assumption remains in the systems that consume it |
| **Evidence** | Measured. Phase 1's `GitDiscoveryProvider` is one provider declaring `TRACKED_CONTENT`; the filesystem provider declares neither `TRACKED_CONTENT` nor `VERSIONED_CONTENT` |
| **Class** | CRITICAL (legacy consumers) / addressed for discovery in Phase 1 |

| ID | A-14 |
|---|---|
| **Name** | The governance vocabulary is a single in-process object |
| **Location** | Every registry in `engine/omega_governance/**` |
| **Description** | `DomainRegistry`, `StateRegistry`, `FrameRegistry`, `ClockRegistry`, `CalendarRegistry`, `OrderingRegistry`, `CodecRegistry`, `IdentityRegistry`, `TransformationRegistry` are in-memory and process-local. **Two nodes can hold divergent vocabularies with no detection.** There is no vocabulary consensus, no version, no digest of the registry itself |
| **Evidence** | Structural. No registry exposes a `digest()`; none is comparable to a peer's |
| **Risk** | A federation in which one node has registered a domain the other has not will silently disagree about whether a record is valid, and both will report success |
| **Expansion impact** | **Blocks federation outright** — Rule 8's "previously unknown civilizations" can register locally and cannot agree |
| **Replacement strategy** | Give every registry a content digest; make the vocabulary itself an artifact with a governance status and an authority chain; declare vocabulary divergence a contradiction class |
| **Class** | **BLOCKING**, open. Highest-severity open finding in this register |

### 2.5 Scale, finiteness and proof-method assumptions

| ID | A-15 |
|---|---|
| **Name** | The governed population is finite and materialisable |
| **Location** | `state.census`, `state.assert_total`, `state.separation_report`, `state.population_of`, `authority.resolve_all`, `authority.fallback_density` |
| **Description** | Every reporting function takes an `Iterable` and walks it to completion. `fallback_density` refuses an empty population — correctly — but there is no path for an *unbounded* one |
| **Evidence** | Structural: all are single-pass full materialisations. No streaming, no sampling, no incremental digest |
| **Risk** | "Indefinite growth" (Rule 9) is supported in *vocabulary* and not in *population*: the vocabulary is open-world, the census is closed-world |
| **Replacement strategy** | Incremental, mergeable summaries (counts as commutative monoids) so a census composes from partial censuses without a global pass |
| **Class** | **CRITICAL**, open |

| ID | A-16 |
|---|---|
| **Name** | Invariants can be proven by exhaustive enumeration |
| **Location** | Phase 2 design: `invariants.unknown_never_certifies` enumerates the axis product |
| **Description** | The proof method is exponential in the number of axes. **This is the strongest proof in the design and it is itself a ceiling** |
| **Evidence** | **Measured this session:** 6 axes → 900 vectors. 7 axes → 1,800. Ten axes → 48,600. Twenty axes → **2,869,781,400** |
| **Risk** | A deployment that exercises the open-world extension the architecture advertises destroys the proof that makes it trustworthy. Registering axes is *encouraged*; doing it 14 times makes the invariant unprovable by this method |
| **Expansion impact** | Directly couples "indefinite domain diversity" to "loss of machine-proven invariants" |
| **Replacement strategy** | Replace enumeration with a **per-axis argument**: prove that no edge targets `UNKNOWN` (so the unknown population only drains) and that `CERTIFIED`'s guard names `UNKNOWN`. Both are O(edges) and independent of axis count. Exhaustive enumeration remains as a cross-check at small sizes |
| **Class** | **CRITICAL**, open. Most important finding in this register |

| ID | A-17 |
|---|---|
| **Name** | Registration is free |
| **Location** | Implicit in Ω∞ Rule 3 as stated, and in every registry |
| **Description** | Adding an axis is a registration with **no source edit** — and it retroactively makes every previously-built status incomplete |
| **Evidence** | **Measured this session:** after registering a 7th axis, `assert_total` on a status built under 6 axes raises and names the gap. This is the designed behaviour and it is correct — but it means "registration only, no migration" is **false**: the code needs no migration; the *data* does |
| **Risk** | Rule 9's success condition ("Registration Only → No Migration") cannot be met for axis registration, and claiming otherwise would be the assumption |
| **Replacement strategy** | None. The honest form is to **report** the incomplete population, which is what happens. Rule 9 should be amended to distinguish *code* migration from *record* backfill |
| **Class** | **FUNDAMENTAL** — and a correction to the directive's own success condition |

### 2.6 Human-centric, language and semantic assumptions

| ID | A-18 |
|---|---|
| **Name** | Meaning is carried by English prose |
| **Location** | Every `description`, `statement`, `justification`, `reason` and `Invariant.statement` in `engine/omega_governance/**` |
| **Description** | Descriptions are unstructured English. A non-human or non-English consumer receives an opaque string. The *schema* is machine-readable; the *semantics* are not |
| **Evidence** | Structural: `Field.kind` is a free string this architecture deliberately never interprets (correct for openness) — which means kind semantics live only in prose |
| **Risk** | Two independently-developed extensions can agree on a `kind` name and disagree on its meaning, with nothing to detect it. The registry's conflict check catches differing *descriptions*, not differing *interpretations of identical descriptions* |
| **Expansion impact** | Blocks non-language systems and machine-to-machine vocabulary negotiation |
| **Replacement strategy** | Bind each `kind` to a declared domain with executable invariants, so meaning is *checkable* rather than *readable*. Partial: A-19 limits this |
| **Class** | **HIDDEN**, open |

| ID | A-19 |
|---|---|
| **Name** | An invariant that cannot be executed is still an invariant |
| **Location** | `reference/domain.py` `Invariant.predicate: Callable \| None`; `DomainRegistry.unexecutable_invariants()` |
| **Description** | A domain may declare an invariant with no predicate. The three-valued `check()` returns `None` for "not checkable here", and `validate()` emits a finding saying so |
| **Evidence** | Designed and measured: `TIME_DOMAIN` ships `Ω∞-D-T-02` ("corresponds to a real instant in its declared frame") as deliberately unexecutable |
| **Risk** | An unexecutable invariant is a *documented* gap, which is far better than an omitted one and far worse than a checked one. A deployment could declare every invariant unexecutable and pass validation with zero real checking |
| **Replacement strategy** | Ratchet `unexecutable_invariants()` as a CONVERGENT population so the count may fall or hold and never rise |
| **Class** | EXPANDABLE, open — mitigation is a ratchet, not a fix |

| ID | A-20 |
|---|---|
| **Name** | Rule identifiers occupy one flat global namespace |
| **Location** | `Ω²-S-01`..`Ω²-S-36`, `Ω²-A-01`..`Ω²-A-07`, `Ω²-C-01`..`Ω²-C-05`, `Ω∞-X-*`, `Ω∞-D-*` |
| **Description** | Two independently-developed extensions can mint colliding rule ids. `TransitionGraph.register` refuses a duplicate *within one graph*; nothing prevents two federated deployments minting `Ω²-S-37` for different edges |
| **Evidence** | Structural. No namespace authority, no prefix registry |
| **Class** | REPLACEABLE, open — bind rule ids to the declaring authority |

### 2.7 Relationship, causality and truth assumptions

| ID | A-21 |
|---|---|
| **Name** | Transformations are binary and directed |
| **Location** | `reference/transformation.py` — `Transformation(source, target, ...)`, edges keyed `(source, target)` |
| **Description** | An n-ary relationship — "position in space **and** time **and** frame yields a velocity" — cannot be declared. Only pairwise chains |
| **Evidence** | Structural: `_edges: dict[tuple[str, str], str]` |
| **Risk** | Genuinely multi-domain science (Rule 8's "previously unknown science") is representable only by inventing intermediate composite domains, which is a schema modification |
| **Class** | **BLOCKING**, open |

| ID | A-22 |
|---|---|
| **Name** | A relation between two positions has exactly three semantic properties |
| **Location** | `temporal/ordering.py` — `Relation(decided, ordered, coincident)` |
| **Description** | A registered sixth relation is checked by the same `assert_consistent` with no edit — a genuine improvement over the previous hardcoded pair table. But a relation needing a *fourth* property (a probability weight, a confidence, a partial degree) requires a source edit |
| **Evidence** | Measured: a `SUPERPOSED` relation and a `QuantumOrdering` strategy registered successfully this session — *because* superposition happened to be expressible as "decided, not ordered, not coincident". A *weighted* ordering would not have been |
| **Class** | EXPANDABLE, open |

| ID | A-23 |
|---|---|
| **Name** | Truth is binary at the record level |
| **Location** | `Invariant.check() -> bool \| None`; `Schema.validate() -> tuple[str, ...]` |
| **Description** | An invariant holds, fails, or is uncheckable. There is no *degree*, no confidence and no evidential weight. The three-valued return is a real improvement on two-valued; it is still not graded |
| **Risk** | An evidence model resting on probability or on accumulating weak evidence (Rule 8's "previously unknown evidence models") cannot be expressed |
| **Class** | EXPANDABLE, open |

| ID | A-24 |
|---|---|
| **Name** | An append-only register imposes a total order on records |
| **Location** | Phase 2 design: hash-chained `GovernanceRegistry` (**unbuilt at audit time**) |
| **Description** | **The deepest internal contradiction found.** The temporal model admits `CONCURRENT`; a hash chain requires each entry to name exactly one predecessor. So the register would impose a total order on records whose *coordinates* the same architecture declares unordered |
| **Evidence** | Design inspection. Not measured — the module does not exist. Recorded so it is designed out rather than built in |
| **Risk** | Two federated observers cannot both append without consensus, and the chain would silently manufacture the ordering that A-02 exists to eliminate |
| **Replacement strategy** | Merkle **DAG**, not chain: an entry names *all* predecessors it observed. Concurrent appends produce sibling nodes; `verify_chain` becomes a DAG traversal. Total order becomes a *projection* a caller may request, not a property the register asserts |
| **Class** | **BLOCKING**, open. Must be resolved before the register is implemented |

| ID | A-27 |
|---|---|
| **Name** | Totality is a property of a comparison, not of a value domain |
| **Location** | `temporal/ordering.py` — `Ordering.total: bool`, and `assert_consistent`'s first draft |
| **Description** | `Ordering.total` is an unconditional boolean. But `LexicographicStrategy` is total over positions of **one shape** — same arity, mutually comparable component types — and correctly answers `INCOMPARABLE` across shapes. An unconditional `total=True` is therefore either a lie or an unstated precondition |
| **Evidence** | **Found by the architecture's own self-check, not by inspection.** `assert_consistent` refused `LexicographicStrategy` — a strategy telling the truth — because the checker demanded totality over a heterogeneous sample: `(0,)` vs `(0,1)` (different arity) and `(0,)` vs `("A",)` (different component type) both answer `INCOMPARABLE`. The checker was wrong, not the strategy |
| **Risk** | A consumer requiring a total order would trust `total=True` and receive `INCOMPARABLE` for a cross-shape pair. The label promises more than any strategy can deliver across domains |
| **Expansion impact** | Directly affects Rule 8's non-numeric measurement case: a symbolic position and a numeric one are not orderable, and a totality claim that ignored shape would make that failure look like a strategy defect |
| **Replacement strategy** | Applied: `_shape_of` gives arity plus component type names; the totality obligation is enforced **within** a shape class, and antisymmetry is enforced **everywhere** — because a refusal that depends on argument order is not a refusal. The deeper fix, not applied, is for `total` to name the precondition it holds under rather than being a bare boolean |
| **Class** | HIDDEN (discovered by execution) · partially closed |

**Why A-27 is the most encouraging entry in this register.** Every other assumption here was found by a
human reading code or by a mechanical scan for known-bad patterns. This one was found by the
architecture's own consistency checker refusing a component of the architecture, and the resolution
required deciding *which of the two was wrong* — a question that could not even be asked before the
checker existed. That is the property Ω∞ Rule 8 is asking for, observed once, on a small scale.

### 2.9 Closed-world inventory in the legacy trees

| ID | A-25 |
|---|---|
| **Name** | 264 enumerations across the repository |
| **Location** | Measured by tree: `platform/` 128 enums / 651 members; `engine/` 74 / 468; `application/` 22 / 98; `data/` 18 / 59; `service/` 14 / 47; `infrastructure/` 4 / 19; `intelligence/` 4 / 30. **Total 264 enums, 1,372 members** |
| **Description** | Every one is a closed list that cannot be extended at runtime. Ω∞ Rule 4 requires each be *challenged*; this register challenges them collectively and defers per-enum triage to Deliverable 4 |
| **Evidence** | Measured by AST walk |
| **Expansion impact** | Each is a potential expansion barrier. Deliverable 4 classifies which are true invariants and which are accidental |
| **Replacement strategy** | **Not in this phase.** Phase 2's constraint is that legacy systems are reached through adapters and never rewritten |
| **Class** | CRITICAL (aggregate), triage in Deliverable 4 |

| ID | A-26 |
|---|---|
| **Name** | The Phase 2 tree's own residual closed list |
| **Location** | `engine/omega_governance/state.py` — `REQUIRED_STATE_NAMES`, 13 items |
| **Description** | The only module-level closed literal collection in the entire Phase 2 tree (measured: 1). It is **not a vocabulary** — it is a conformance assertion that the thirteen states the directive names are declared. Nothing resolves through it and nothing is validated against it |
| **Evidence** | Measured. `engine/omega_governance/**`: 0 enums, 0 `datetime`/`time`/`os`/`pathlib`/`uuid` imports, `json`+`hashlib` confined to `reference/encoding.py`, 1 closed literal tuple |
| **Class** | Accepted. A directive-conformance check, correctly closed |

---

## 3. CATEGORY COVERAGE

The directive named thirty assumption categories and said not to assume the list complete. Coverage,
with the two categories this register found that the list did not name:

| Category | Entries | Category | Entries |
|---|---|---|---|
| Concept | A-07, A-23 | Contradiction | A-24, A-14 |
| Domain | A-11, A-21 | Causality | A-02, A-24 |
| Category | A-25, A-26 | Expansion | A-17, A-16 |
| Hierarchy | A-10, A-20 | Scalability | A-15, A-16 |
| Identity | A-05, A-06 | Boundary | see Deliverable 2 |
| Relationship | A-21, A-22 | Language | A-18 |
| Measurement | A-04, A-15 | Platform | A-12, A-13 |
| Temporal | A-01, A-02, A-03 | Repository | A-13 |
| Spatial | A-01 (frames), A-12 | Human-centric | A-18, A-09 |
| Governance | A-07, A-09, A-10 | Earth-centric | A-01, A-03 |
| Certification | A-11, A-08 | Software-centric | A-06 |
| Discovery | A-13 | Finite-model | A-15, A-16, A-17 |
| Storage | A-12, A-14 | Unknown-domain | A-14, A-21 |
| Execution | A-13 | **Proof-method** *(not in the list)* | **A-16** |
| Representation | A-05, A-06 | **Vocabulary-consensus** *(not in the list)* | **A-14** |
| Evidence | A-19, A-23 | | |
| Truth | A-23, A-19 | | |

Three entries (A-16, A-14, A-27) fall outside the thirty categories the directive names.

**Two categories the directive's thirty did not name, and both produced high-severity findings.**
Proof-method assumptions (A-16) and vocabulary-consensus assumptions (A-14) are the two most severe
open items in this register. That is direct evidence for the directive's own instruction not to treat
its list as complete — and grounds for treating *this* list as incomplete too.

---

## 4. SUMMARY BY CLASS

| Class | Count | IDs |
|---|---|---|
| FUNDAMENTAL | 2 | A-06, A-17 |
| BLOCKING (open) | 5 | A-09, A-10, A-14, A-21, A-24 |
| CRITICAL (open) | 2 | A-15, A-16 |
| CRITICAL (closed in Phase 2 tree, legacy untouched) | 7 | A-01, A-02, A-04, A-05, A-07, A-08, A-12, A-13, A-25 |
| HIDDEN (open) | 2 | A-18, A-27 (partially closed) |
| EXPANDABLE (open) | 3 | A-19, A-22, A-23 |
| REPLACEABLE (open) | 2 | A-03 (closed), A-20 |
| UNKNOWN | 1 | A-11 |

**Ω∞ readiness cannot be claimed.** Five BLOCKING and two CRITICAL assumptions are open, two of which
(A-14 vocabulary consensus, A-24 total-order register) would be built *into* the next layer if it were
implemented as currently designed. Deliverable 9 sequences their removal.

---

## 5. COMPANION DELIVERABLES

| # | Document |
|---|---|
| 2 | `PHASE_OMEGA_A_BOUNDARY_REGISTER.md` |
| 3 | `PHASE_OMEGA_A_EXPANSION_BARRIER_REGISTER.md` |
| 4 | `PHASE_OMEGA_A_CLOSED_WORLD_REGISTER.md` |
| 5 | `PHASE_OMEGA_A_OPEN_WORLD_READINESS.md` |
| 6 | `PHASE_OMEGA_A_INFINITE_EXPANSION_GAP_ANALYSIS.md` |
| 7 | `PHASE_OMEGA_A_ARCHITECTURAL_CORE_PROPOSAL.md` |
| 8 | `PHASE_OMEGA_A_REMAINING_FUNDAMENTAL_CONSTRAINTS.md` |
| 9 | `PHASE_OMEGA_A_ROADMAP.md` |
