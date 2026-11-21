# UCOS Ω∞ — PHASE Ω∞-A, DELIVERABLE 2
## Boundary Register

**AUTHORITY = NONE (DERIVED TRUTH).** Discovery only. No certification, no seal, no ratchet
advancement, no modification of any active process.

**WHAT A BOUNDARY IS, AS DISTINCT FROM AN ASSUMPTION.** An assumption is a belief embedded in code.
A boundary is the *edge of the world the system can see*. An assumption can be removed; a boundary can
only be moved outward or made explicit. The distinction matters because the register in Deliverable 1
lists things to fix, and this one lists things to **know the shape of** — several boundaries below are
correct and should stay, and their danger is that they are currently invisible rather than that they
exist.

**ORIGIN COLUMN.** Every boundary was created by something. Recording the origin is what makes a
boundary *attributable*, which the directive's success criterion requires.

---

## B-01 — Repository boundary

| Field | Content |
|---|---|
| **Description** | The governed universe is what a single git working tree contains. Population is `git ls-files '*.py'`; scope is a repository root; identity is a repo-relative path |
| **Origin** | `engine/universal_discovery/discovery.py:tracked_python`. Phase 1 recorded the origin precisely: `root: str = "."` on `build`, `evaluate`, `derived_scope` |
| **Current enforcement** | 42 files invoke git through `subprocess` (measured). `pytest_scope.py` injects the coverage denominator from `derived_scope(_repository_root())`. `verify.sh` runs from `cd "$(dirname "$0")/.."` |
| **Scalability impact** | Governance capacity is bounded by one clone. A population held in a bucket, a registry or a federation is not merely unsupported — it is *uncountable*, so its absence cannot appear as a finding |
| **Ω∞ impact** | Blocks Rule 7 outright for the legacy path. Phase 1 moved the boundary for the *discovery layer* (`KnowledgeSpace` admits `BUCKET`, `REGISTRY`, `FEDERATION`, `GRAPH`) and the consumers still assume a repository |
| **Elimination feasibility** | **Partial and already begun.** The seam exists (Phase 1); the work is migrating consumers onto it. Cost is high because 42 sites and the entire verification plan sit inside the boundary. **Not eliminable in this phase — and must not be, since Phase 2 forbids modifying active validation** |

## B-02 — Storage boundary

| Field | Content |
|---|---|
| **Description** | Persistence means a local filesystem: paths, `open()`, directory hierarchies |
| **Origin** | 364 files import `os`, `pathlib`, `shutil` or `glob` (measured) |
| **Current enforcement** | Direct, unmediated calls. There is no storage provider interface anywhere in the legacy trees |
| **Scalability impact** | Governance records cannot be sharded, replicated or held behind a network without a parallel implementation |
| **Ω∞ impact** | Rule 7 names filesystem, object store, database, graph, ledger and distributed memory. Only the first exists |
| **Elimination feasibility** | **Feasible but NOT DONE, and this register must be honest about the gap.** The Phase 2 tree imports no filesystem module at all (measured: 0) and reduces every record to primitives via `as_record()`. That makes it storage-*neutral*; it does not make it storage-*capable*. **There is no `StorageProvider` protocol, no persistence adapter and no append-only store.** `STORAGE_DOMAIN` declares the vocabulary for talking about storage and implements none. The boundary has been made explicit and has not been crossed |

## B-03 — Language boundary

| Field | Content |
|---|---|
| **Description** | A governance engine must be Python to participate |
| **Origin** | The implementation. 2,178 Python files; the plugin mechanism is a pytest hookwrapper; the contracts are `typing.Protocol` |
| **Current enforcement** | Import-time. A non-Python engine cannot call `DomainRegistry.declare` |
| **Scalability impact** | None on throughput. Total on *participation* |
| **Ω∞ impact** | Rule 6 requires interfaces describable as contracts, schemas, capabilities and invariants. The Phase 2 tree satisfies the *description* requirement — every protocol is four or fewer methods over names, integers and mappings, and `Schema`/`Invariant`/`Capability` are declarative values — but **no schema document is emitted**, so a non-Python implementer has nothing to implement against except the source |
| **Elimination feasibility** | **Feasible and unstarted.** The designed `schema.py` (contract emission) was not written. Until it exists, Rule 6 compliance is a property of the design that cannot be consumed. Note the residual: even with emitted schemas, *this artifact* remains Python. The architecture becomes language-neutral; the implementation does not, and conflating those would be the assumption |

## B-04 — Operating-system and platform boundary

| Field | Content |
|---|---|
| **Description** | POSIX process model, POSIX paths, a shell, exit codes 0/1/2, environment variables |
| **Origin** | `verify.sh`, `Makefile`, `scripts/*.sh`, `bootstrap.sh`, `doctor.sh`; `ucos_venv_python` resolving `.ec1-venv` by absolute path |
| **Current enforcement** | Shell invocation and `subprocess` |
| **Scalability impact** | Bounded to one host per run. The plan/stage machinery in `verify.sh` is single-process with background job draining |
| **Ω∞ impact** | Rule 1 forbids Bash, Make and a CI system as architectural assumptions. All three are load-bearing for *governance execution*, though not for the governance *model* |
| **Elimination feasibility** | Low value, high cost. `EXECUTION_DOMAIN` makes planes registrable, which is the part that matters: the model can *describe* a non-POSIX plane even though this repository's own gates run on one. **Recommend making this boundary explicit and leaving it in place** |

## B-05 — Calendar and chronology boundary

| Field | Content |
|---|---|
| **Description** | Time is Gregorian civil time on Earth |
| **Origin** | 11 files importing `datetime` or `time` (measured) |
| **Current enforcement** | Direct import at record-construction sites |
| **Scalability impact** | Non-determinism: two runs cannot produce identical evidence, so digests cannot be compared |
| **Ω∞ impact** | Rule 5 |
| **Elimination feasibility** | **Crossed in the Phase 2 tree, measured.** Zero `datetime`/`time` imports; Gregorian arithmetic confined to one deletable class implemented in integers; a Mars coordinate and a non-numeric civilisational epoch both round-trip. **Not crossed in the legacy trees, and correctly so — Phase 2 forbids rewriting them** |

## B-06 — Unit and reference-system boundary

| Field | Content |
|---|---|
| **Description** | Magnitudes are SI, and comparisons between systems are inline arithmetic |
| **Origin** | Diffuse. No single site; conversions appear where needed |
| **Current enforcement** | None. The absence of enforcement *is* the boundary — nothing records that a conversion happened, on whose authority, or with what loss |
| **Scalability impact** | Low |
| **Ω∞ impact** | Rule 1 names SI, metric, imperial, three temperature scales and three speed units |
| **Elimination feasibility** | **Crossed in vocabulary.** `UNITS_DOMAIN`, `TEMPERATURE_DOMAIN` and `VELOCITY_DOMAIN` are registrations with no privileged system, and `TransformationRegistry` makes conversion a declared, authority-bearing edge carrying `lossy` and `invertible`. Two of the three shipped transformations deliberately carry **no computation**, because the arithmetic belongs to bodies publishing ephemerides. **The boundary is now visible and honest rather than crossed by approximation** |

## B-07 — Governance-vocabulary boundary  ⚠ HIGHEST SEVERITY

| Field | Content |
|---|---|
| **Description** | The set of governance concerns is whatever one process has registered. There is no shared, versioned or verifiable vocabulary |
| **Origin** | Every registry in `engine/omega_governance/**` is an in-memory, process-local object |
| **Current enforcement** | Python object identity. Two processes share nothing |
| **Scalability impact** | **Total for federation.** Two nodes can hold divergent vocabularies, each validate the same record differently, and both report success. No digest, no version, no comparison operator exists on any registry |
| **Ω∞ impact** | Blocks Rule 8's "previously unknown civilizations" at the point where two of them must *agree*. Registration works; consensus does not exist |
| **Elimination feasibility** | **Feasible, unstarted, and it is the single highest-value remaining item.** Give every registry a content digest; make the vocabulary itself an artifact with a governance status and an authority chain; declare vocabulary divergence a contradiction class. See A-14 and Deliverable 9 step 1 |

## B-08 — Population-cardinality boundary

| Field | Content |
|---|---|
| **Description** | A governed population must fit in memory and be walkable in a single pass |
| **Origin** | `state.census`, `state.assert_total`, `state.separation_report`, `authority.resolve_all`, `authority.fallback_density` |
| **Current enforcement** | Structural: every reporting function takes an `Iterable` and exhausts it |
| **Scalability impact** | **The vocabulary is open-world and the census is closed-world.** Rule 9's "indefinite growth" holds for what can be *described* and fails for what can be *counted* |
| **Ω∞ impact** | Direct. A federation of a billion artifacts cannot be governed by these functions |
| **Elimination feasibility** | Feasible: express every census as a commutative, mergeable monoid so partial censuses compose without a global pass. Moderate cost, no interface break |

## B-09 — Proof-tractability boundary  ⚠ SELF-INFLICTED

| Field | Content |
|---|---|
| **Description** | Machine-proven invariants are proven by enumerating the product of all axis positions |
| **Origin** | The Phase 2 design's own strongest feature: exhaustive rather than sampled proof |
| **Current enforcement** | Arithmetic. **Measured: 6 axes → 900 vectors; 7 → 1,800; 10 → 48,600; 20 → 2,869,781,400** |
| **Scalability impact** | The boundary tightens *as the architecture is used as intended*. Registering axes is the advertised extension mechanism, and doing it fourteen times makes the invariant unprovable by this method |
| **Ω∞ impact** | Couples "indefinite domain diversity" to "loss of the machine proof that justifies trusting the model" — the worst possible coupling, because the failure is silent: the proof does not become wrong, it becomes unrunnable |
| **Elimination feasibility** | **Feasible and cheap.** The invariant does not need enumeration. It follows from two O(edges) facts: nothing targets `UNKNOWN`, and `CERTIFIED`'s guard names `UNKNOWN`. Both are independent of axis count. Keep enumeration as a small-size cross-check. See Deliverable 9 step 2 |

## B-10 — Justification-semantics boundary

| Field | Content |
|---|---|
| **Description** | The strongest thing the model can demand of a reduction of obligation is a non-empty string |
| **Origin** | `state.Transition.requires_reason`; mirrored in Ω-1's ratchet justifications and `pyproject.toml` exemption reasons |
| **Current enforcement** | `not reason.strip()` |
| **Scalability impact** | None |
| **Ω∞ impact** | **Measured: the edge `UNGOVERNED → EXEMPTED` was taken with `reason="x"`.** A governance model resting on signed authorisation, quorum, named approvers or citations degrades to "somebody typed something" |
| **Elimination feasibility** | Feasible. Promote `reason: str` to a `Justification` value in a registered domain whose schema and invariants a deployment declares |

## B-11 — Guard-expressiveness boundary

| Field | Content |
|---|---|
| **Description** | A transition rule can express exactly two kinds of condition |
| **Origin** | `state.Transition` — `requires_reason`, `blocked_by`. **Measured: exactly 2** |
| **Current enforcement** | `state.check` reads those two fields and nothing else |
| **Ω∞ impact** | An unknown governance model is admitted only if its rules happen to fit two shapes. "N of M approvals", "quorum of a federation", "within a declared window" and "conditional on another artifact's state" are all inexpressible |
| **Elimination feasibility** | Feasible and clean: a `Guard` protocol with `evaluate(status, context) -> (bool, reason)`, with the present two becoming registered guards among many |

## B-12 — Relationship-arity boundary

| Field | Content |
|---|---|
| **Description** | A declared relationship between reference domains is binary and directed |
| **Origin** | `reference/transformation.py` — `_edges: dict[tuple[str, str], str]` |
| **Current enforcement** | The edge key's shape |
| **Ω∞ impact** | Rule 8's "previously unknown science" is representable only by inventing composite intermediate domains, which is a schema modification — i.e. an expansion barrier |
| **Elimination feasibility** | Moderate: generalise to `sources: tuple[str, ...] -> target`, and generalise `path` from BFS over a graph to resolution over a hypergraph |

## B-13 — Encodability boundary  ⚠ FUNDAMENTAL

| Field | Content |
|---|---|
| **Description** | Only what can be reduced to bytes can be fingerprinted, and only what can be fingerprinted can enter an append-only register |
| **Origin** | The nature of tamper-evident records |
| **Current enforcement** | `reference/domain.assert_encodable`, which **refuses** rather than stringifying |
| **Ω∞ impact** | Non-software artifacts — a physical specimen, a live process, a continuous field, an unbounded stream — are governed by proxy |
| **Elimination feasibility** | **None.** This is a genuine edge of the world, not a defect. The correct response is what the architecture already does for frames: make the proxy relationship a **declared transformation** with an authority and a `lossy` flag, so the substitution is recorded rather than assumed. See Deliverable 8 |

## B-14 — Namespace boundary

| Field | Content |
|---|---|
| **Description** | Rule identifiers, domain names, capability names, state names and relation names occupy one flat global namespace with no minting authority |
| **Origin** | Convention. `Ω²-S-nn`, `Ω²-A-nn`, `Ω∞-X-*`, `Ω∞-D-*` |
| **Current enforcement** | Within one process, registries refuse conflicting redefinition — which is a real and useful guard. Across processes, nothing |
| **Ω∞ impact** | Two federated deployments will mint `Ω²-S-37` for different edges. Combined with B-07 (no vocabulary consensus) this produces silent semantic divergence |
| **Elimination feasibility** | Feasible: bind every identifier to its declaring authority, so the full name is `(authority, identifier)` and collision requires two bodies claiming one name — which is itself a contradiction the engine can report |

---

## SUMMARY

| Boundary | Crossed in Phase 2 tree | Crossed in legacy | Feasibility of elimination |
|---|---|---|---|
| B-01 repository | seam exists (Phase 1) | no | partial, expensive, deferred |
| B-02 storage | made explicit, **not crossed** | no | feasible, unstarted |
| B-03 language | described, **no schema emitted** | no | feasible, unstarted |
| B-04 OS / platform | n/a to the model | no | low value — keep, make explicit |
| B-05 calendar | **yes, measured** | no (correctly) | done for new work |
| B-06 units | **yes, in vocabulary** | no | done for new work |
| B-07 governance vocabulary | **no** ⚠ | no | feasible — **highest value** |
| B-08 population cardinality | **no** | no | feasible, moderate |
| B-09 proof tractability | **no** ⚠ | n/a | feasible, cheap — **do second** |
| B-10 justification semantics | **no** | no | feasible |
| B-11 guard expressiveness | **no** | no | feasible, clean |
| B-12 relationship arity | **no** | no | moderate |
| B-13 encodability | **cannot be** | cannot be | **none — FUNDAMENTAL** |
| B-14 namespace | **no** | no | feasible |

**Five boundaries were crossed or made explicit. Eight remain open. One cannot be eliminated.**

Two of the open boundaries (B-07, B-09) are the subject of Deliverable 9's first two steps, because
both would otherwise be *built into* the next foundation layer rather than designed out of it.
