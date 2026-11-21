# UCOS Ω∞ — PHASE Ω∞-B, DELIVERABLE 1
## Blocker Resolution Matrix

> ## ⚠ EVIDENCE PROVENANCE AND CURRENT REPRODUCIBILITY — READ FIRST
>
> **The subject tree measured by this phase, `engine/omega_governance/`, is NO LONGER PRESENT in the
> working directory.** This note is recorded rather than the claims below being quietly left standing,
> because a claim that nothing checks is the precise defect class this phase was convened to document.
>
> **Timeline, from filesystem timestamps:**
>
> | Time (2026-08-29) | Event |
> |---|---|
> | 11:23–11:26 | `engine/omega_governance/**` last modified (predates this phase) |
> | 12:01–12:08 | probes `b01`, `b02_b05`, `b03_b04`, `b06` executed; outputs recorded |
> | 12:48:23 | probe `b07` executed; §H9 confirmed the tree present — `state.py`, `authority.py`, and the `reference/` and `temporal/` subpackages |
> | **12:50:02** | **`engine/` directory mtime changes — the subpackage is removed** |
> | 12:51:56 | absence detected during final verification |
>
> **What this does and does not affect.**
>
> - **The evidence artifacts survive.** All probe sources and their recorded outputs are preserved in
>   `00-MASTER/UCOS-OMEGA-B-001/probes/`. Every measurement cited in this document was taken against the
>   tree while it existed, and the recorded outputs are the evidence of record.
> - **The reproduction instructions in this document no longer execute.** They now fail with
>   `ModuleNotFoundError: No module named 'engine.omega_governance'`. Where this document says a probe
>   was "re-executed against current repository state" and found byte-identical, that was true when
>   written and is **not verifiable now**.
> - **The tree is not recoverable from version control.** It was never committed and never stashed
>   (`git status` reported it untracked; `git log --all --diff-filter=A` finds no such path).
> - **Nothing in this phase removed it.** Ω∞-B writes were confined to
>   `00-MASTER/UCOS-OMEGA-B-001/probes/` and the root `PHASE_OMEGA_B_*.md` deliverables. No Ω∞-B
>   operation targeted `engine/`.
>
> **Consequence for this document's standing.** Its classifications remain the honest record of what was
> measured. They are **no longer independently re-verifiable** until the tree is restored from a backup or
> another working copy. Restoring it is an owner decision and is not taken here.


**AUTHORITY = NONE (DERIVED TRUTH).** This document classifies. It issues **no certification**,
generates **no seal**, advances **no ratchet**, declares **no closure**, and makes **no readiness
claim**. It modifies no active governance, validation or certification process. Ω∞ readiness is not
claimed anywhere in it.

**SCOPE.** Every BLOCKING and CRITICAL finding in the Phase Ω∞-A registers, plus five findings Ω∞-B
measured that Ω∞-A did not record. Ω∞-A findings are authoritative inputs and are not re-discovered.

**WHAT A VERDICT MEANS HERE.** The directive asks whether each blocker is *removable, partially
removable, or fundamental*. A verdict is admissible in this matrix only if it rests on one of:

| Basis | Meaning |
|---|---|
| **MEASURED** | A probe observed the stated fact against current repository state |
| **MEASURED BY PROTOTYPE** | A prototype composing only over shipped types, in `probes/`, imported by nothing, demonstrated the resolution works — so the blocker is implementation-induced rather than architecture-induced |
| **STRUCTURAL** | Established by the shape of a shipped type or index, with the type cited |
| **ARGUED** | No measurement was possible. Stated as argued, and the reason measurement was impossible is given |

**Nothing in this matrix rests on preference.** Where Ω∞-A's determination and Ω∞-B's measurement
disagree, the measurement is recorded and the disagreement is named.

**EVIDENCE BASE.** Five probes, all re-executed against current repository state:

| Probe | Reproduction status |
|---|---|
| `b01_proof_tractability.py` | **every structural count byte-identical**; 6 of 110 lines differ, all wall-clock timings |
| `b02_b05_governance_certification.py` | **byte-identical** |
| `b03_b04_semantic_transformation.py` | **byte-identical** |
| `b06_temporal_neutrality.py` | **byte-identical** |
| `b07_removability_validation.py` | 18 hypotheses; 6 of ~355 lines differ across runs, all timings |

```
cd /Users/bipin/Desktop/UCOS-CONSOLIDATION
for p in b01_proof_tractability b02_b05_governance_certification \
         b03_b04_semantic_transformation b06_temporal_neutrality b07_removability_validation; do
  .ec1-venv/bin/python 00-MASTER/UCOS-OMEGA-B-001/probes/$p.py
done
```

**NO CODE IN `engine/` WAS MODIFIED.** Verified: `engine/omega_governance/**` file mtimes are
11:23–11:26, predating this phase's work; `git status --porcelain engine/omega_governance` reports the
tree as untracked and unchanged.

---

## 1. SUMMARY

| Verdict | Count | IDs |
|---|---|---|
| **REMOVABLE** | 8 | A-09, A-10, A-11, A-15, A-21, A-24, X-01, X-02 (and the X/G ids that resolve with them) |
| **PARTIALLY REMOVABLE** | 5 | A-14, A-16, A-18, A-22, A-27 |
| **FUNDAMENTAL** | 1 | the agreement half of A-14 (= C-04) |
| **OUT OF SCOPE BY DIRECTIVE** (classified, not resolved) | 5 | A-25, X-13, X-17, X-19, X-20 |

**Not one BLOCKING or CRITICAL finding is fundamental in its own right.** The single fundamental
element inside the set is C-04 (meaning cannot be fully mechanised), which surfaces inside A-14 and is
already recorded as a fundamental constraint rather than a blocker.

**Both falsification criteria Ω∞-A ranked most likely to fire were tested.** Criterion 3 (a domain with
no possible fingerprint) **did not fire**. Criterion 1 (a governance rule not expressible as guards)
**did not fire**. Criterion 5 (agreement despite identical digests) **fired, and is confirmed** — it is
the C-04 element above.

---

## 2. THE MATRIX — BLOCKING FINDINGS

### A-09 · A justification is any non-empty string

| Field | Content |
|---|---|
| **Area** | B-02 |
| **Ω∞-A class** | BLOCKING, open |
| **Observation** | `state.check` tests `not reason.strip()`. Edge `Ω²-S-12` (`UNGOVERNED → EXEMPTED`, `requires_reason=True`) **ACCEPTED** every one of `'x'`, `'.'`, `'0'`, `'no'`, `'TODO'`, `'  see ticket  '`. On `Ω²-S-22` it accepted a reason naming **one** approver where three were required, and the shortfall has no field to be recorded in |
| **Reproduction** | `b02_b05` §B-02.2, §B-02.3; `b07` §H1 |
| **Architectural cause** | **IMPLEMENTATION-INDUCED.** `reason: str` is a primitive. A `str` has no schema, so it cannot carry an approver, a citation or a quorum record. The architecture *has* a schema mechanism (`Schema`/`Field`/`Invariant`/`ReferenceDomain.validate`) and the transition guard does not use it |
| **Consequence** | Every deployment requiring signed authorisation, a named approver, a quorum or a citation degrades to free text. The claim "an exemption can never be silent" is true; the implied claim "an exemption must be justified" is false |
| **Minimal** | `Justification` value in a registered domain; the guard validates it. **Cost:** small (domain declaration + guard). **Risk:** low. **Impact:** none structurally |
| **Moderate** | `StateChange.reason` becomes the value, so the audit record carries the structure. **Cost:** moderate. **Risk:** medium — **record byte change**, a C-02 backfill; report the population of legacy string reasons rather than converting them. **Impact:** medium |
| **Maximal** | Justification domains declared per governance model, with executable invariants where checkable and a counted unexecutable population where not. **Cost:** high. **Risk:** medium — a declared-but-unverifiable approver is C-04. **Impact:** high |
| **Verdict** | **REMOVABLE** — MEASURED BY PROTOTYPE (`b07` §H1: all four accepted strings refused; a complete justification permitted via `Ω²-S-12`) |
| **Residual** | `Ω∞-B-J-02` ("the cited authority actually approved this") is **unexecutable**. Counted by `unexecutable_invariants()`, not hidden. C-04 |

### A-10 · Two guard kinds suffice for every governance rule

| Field | Content |
|---|---|
| **Area** | B-02 |
| **Ω∞-A class** | BLOCKING, open |
| **Observation** | `Transition` has 6 fields; exactly **2** bear a guard. `blocked_by` is consumed as `state in transition.blocked_by` — a membership test with no count, threshold, predicate or context. Against `authority.py`, **7 of 8** governance capabilities are REFUSED and the 8th is PARTIAL. `AuthorityLink.__post_init__` applies `set()` to claims, destroying vote multiplicity before any aggregation; `selected = sorted(set(claims))[0]` is an **alphabetical** pick |
| **Reproduction** | `b02_b05` §B-02.1, §B-02.4 |
| **Architectural cause** | **IMPLEMENTATION-INDUCED.** A guard is a **field on a frozen dataclass**, not a registry value. Eleven other extension points in the package are registries. Guards are the one mechanism not given one — Ω∞-A Deliverable 7's "four of five mechanisms exist" |
| **Consequence** | Ω∞ Rule 8 case 6 fails. An unknown governance model enters only if its rules fit two pre-decided shapes. Three subsystems (transition, certification, contradiction) will each grow an incompatible condition vocabulary — and **B-05 measures that one already has** |
| **Minimal** | `Guard` protocol + `GuardRegistry`; the two existing guards become registrations. **Cost:** small, ~120 lines, two call sites. **Risk:** low — but `check` must return a **population** of refusals, and preserving the old single-string signature would discard exactly the information the mechanism produces. **Impact:** this is the change that makes the five-mechanism core a measurement rather than a proposal. **Backward compatible**: `Transition` keeps both fields as the declarations the standard guards are built from; no record changes shape |
| **Moderate** | + `context` mapping + structured refusal records. **Cost:** moderate, ~300 lines. **Risk:** medium — a guard reading an absent context key must **refuse**, not default; defaulting reintroduces the silent state. **Impact:** high |
| **Maximal** | + repair `authority.py` (remove `set()`; deduplicate at report time), scoped tiers, revocation as an event, and **one guard registry serving certification and contradiction resolution**. **Cost:** high. **Risk:** medium-high — removing `set()` changes `AuthorityLink`/`AuthorityChain` record bytes and the `contested` computation; `assert_total`, `fallback_density` and `tier_census` all read chains. **This is the only non-backward-compatible item.** **Impact:** highest — an unknown governance model then extends all three subsystems at once |
| **Verdict** | **REMOVABLE** — MEASURED BY PROTOTYPE (`b07` §H1: 10 of 10 capabilities refused for their own stated reason; falsification criterion 1 did not fire) |
| **Residual** | A guard can be written that is wrong or always permits (C-04). `context` is an open vocabulary — C-04 one level down. **And a warning from the prototype's own first draft: it wrongly accepted an out-of-window coordinate because it tested `relation.ordered` instead of the declared precedence relation. A-02 re-enters through convenience** |

### A-11 · Certification has a fixed input set

| Field | Content |
|---|---|
| **Area** | B-05 |
| **Ω∞-A class** | **UNKNOWN (unbuilt)**, designated BLOCKING if built as designed |
| **Observation** | **Ω∞-A's classification is wrong and the correction matters.** `certification.py` is absent — and the certification precondition set **exists today**, as the frozen `blocked_by` tuple `(CONTRADICTED, UNATTRIBUTED, UNGOVERNED, UNKNOWN)` on the two edges reaching `CERTIFIED` (`Ω²-S-22`, `Ω²-S-26`) inside the module constant `INITIAL_TRANSITIONS`. A fixed enumeration of **four**. Extension attempted three ways: assignment → `FrozenInstanceError`; replacement edge → `StateError`; and registering a 7th axis leaves the new concern **registrable and non-binding** — the artifact still certifies |
| **Reproduction** | `b02_b05` §B-05.1, §B-05.2 |
| **Architectural cause** | **ARCHITECTURE-INDUCED, from a decision that is individually correct.** Deliverable Ω-2.4 requires the obligations to be structural — "edges, not advice" — which is *why* `UNKNOWN never certifies` is provable from the graph. Making an obligation structural also makes the obligation set **closed**. B-01 and B-05 are two consequences of one choice, pulling opposite ways |
| **Consequence** | On the day a deployment introduces a new governance concern, the architecture correctly reports every prior record as silent about it (C-02) **and simultaneously certifies new artifacts as if the concern did not exist.** It is more rigorous about the past than the present |
| **Minimal** | Write the decision quantifying over a `CertificationInputRegistry`. **Cost: zero relative to building it as designed** — different work of the same size. **Risk:** low, with one hazard: **`blocked_by` must be retained** as the declaration the standard state-exclusion inputs are built from, because the structural proof of B-01 reads it. A migration that *replaces* it silently destroys that proof. **Impact:** low; makes A-11 impossible rather than deferred |
| **Moderate** | Inputs carry guards (A-10); the explanation is a record naming every input, every satisfied one and every shortfall. **Cost:** moderate, **shared with A-10**. **Risk:** medium — explanation becomes structured; no consumer exists yet. **Impact:** high; closes the three-vocabulary divergence before it occurs |
| **Maximal** | + inputs carry their own authority; the input **set** has a digest; a decision cites the digest it was decided under; an unexecutable input yields `UNVERIFIABLE` **naming the input**. **Cost:** high. **Risk:** medium-high — citing the input-set digest implies vocabulary **retention**, hence a storage obligation (G-05) that does not exist. **Impact:** highest; certification becomes auditable across time, so widening obligations cannot silently change what CERTIFIED meant |
| **Verdict** | **REMOVABLE** — MEASURED BY PROTOTYPE (`b07` §H2: the same 8th-input registration that was non-binding **bound immediately** and named itself in the explanation, zero source edits) |
| **Residual** | Nothing links axis registration to input registration, and nothing should — not every concern is a certification precondition. Auto-binding fabricates an obligation; ignoring it is the current failure. **The only honest response is to report the population of axes no certification input reads** |

### A-14 · The governance vocabulary is a single in-process object

| Field | Content |
|---|---|
| **Area** | B-03 |
| **Ω∞-A class** | BLOCKING, open. Recorded as "highest-severity open finding" |
| **Observation** | **0 of 7 registries expose `digest()`, `declared_by()` or `diverges_from()`.** `grep -rn 'def digest' engine/omega_governance/` returns nothing. Two registries declaring `MASS` differently produced a **divergent verdict on one record — A=INVALID, B=VALID, identical fingerprint — with neither able to detect the other.** The registry's own conflict check is **intra-process only**. A merge raises on the **first** conflict and so cannot report a population |
| **Reproduction** | `b03_b04` §B-03.1–§B-03.4; `b07` §H3 |
| **Architectural cause** | **IMPLEMENTATION-INDUCED for detection; ONTOLOGY-INDUCED for agreement.** A `ReferenceDomain` has an authority, schema, invariants and provenance; the `DomainRegistry` holding it has none. The architecture's governance model was never applied to the vocabulary that implements it |
| **Consequence** | Federation is impossible **and its impossibility is invisible**: both nodes report success. Ω∞ Rule 8 case 5 fails. Compounds with A-20 into silent semantic divergence |
| **Minimal** | Derive `digest(registry, encoding) = encoding.fingerprint(registry.report())`. **Cost:** very small, one free function, **zero registry changes**. **Risk:** low, with a real caveat — only 2 of 7 registries expose `report()`; a digest over the other five needs a canonical serialisation, and a careless one yields false agreement (omission) or false divergence (ordering). **Impact:** none, purely additive |
| **Moderate** | `diverges_from(peer)` returning a **population**. **Cost:** small. **Risk:** low, read-only. **Impact:** positive — the first mechanism comparing two vocabularies rather than two values |
| **Maximal** | + the vocabulary carries a `GovernanceStatus` and an authority chain; `VOCABULARY_CONTRADICTION` as a class; identifiers become `(authority, identifier)`. **Cost:** high. **Risk:** medium-high — qualified identifiers change the identity of every rule reference and therefore every record citing one; a C-02 backfill that must **report** unqualified citations rather than fabricate authorities. **Impact:** highest; the mechanism that eliminates silent states becomes subject to it |
| **Verdict** | **PARTIALLY REMOVABLE.** Detection: **REMOVABLE** — MEASURED BY PROTOTYPE (3 divergence kinds, both authorities named; Step 5 exit criterion met). Agreement: **FUNDAMENTAL** — MEASURED (two registries with **byte-identical digests** attaching different meanings to `magnitude`, both VALID) |
| **Residual** | **A digest cannot see a registered predicate.** `Invariant.predicate` is a `Callable` with no content digest, so two registries can agree on every digest and execute different checks — and the predicate is precisely what gives a `kind` mechanical meaning. **New in Ω∞-B; the sharpest limit on the digest proposal.** Also: divergence detection needs a transport, and none exists (G-05) |

### A-21 · Transformations are binary and directed

| Field | Content |
|---|---|
| **Area** | B-04 |
| **Ω∞-A class** | BLOCKING, open |
| **Observation** | All four assumptions present and **structural**: `source: str`, `target: str`, `dict[tuple[str,str], str]` (1:1), BFS over ordered pairs (no hyperedge representation). n-ary declaration refused with `AttributeError: 'tuple' object has no attribute 'strip'`. The composite-domain workaround is a schema modification **and is opaque** — `SPACE_TIME_FRAME` records nothing about having three parts. **And fan-in as multiple 1:1 edges makes conjunction indistinguishable from alternative: `path('SPACE','VELOCITY')` returns a COMPLETE route, so `apply()` would convert from SPACE alone and report success** |
| **Reproduction** | `b03_b04` §B-04.1–§B-04.3; `b07` §H4 |
| **Architectural cause** | **ARCHITECTURE-INDUCED**, removable by a type widening local to two fields and one index |
| **Consequence** | **Not a missing capability but a wrong answer.** The model produces a successful conversion from insufficient inputs. Separately: **exactly one authority may relate any two domains** — two ephemeris publishers, two precisions, or a superseded factor beside its replacement are all inexpressible, which is the normal condition in physical metrology |
| **Minimal** | `sources: tuple[str, ...]`; key `(frozenset(sources), target, authority)`; satisfiability over available domains reporting a **shortfall population**; refuse a non-`str` source with a governance message rather than an `AttributeError`. **Cost:** small-to-moderate. **Risk:** medium — `as_record()` byte change (C-02 backfill; a 1-source transformation is a 1-tuple, so the *concept* migrates cleanly and stored records do not), and callers may now receive **several** satisfiable routes and must choose. **Impact:** medium, positive; converts a false success into a named shortfall |
| **Moderate** | + `Relation.properties`, `Comparison.coincident`, and a **declared lossy proxy transformation** for every non-encodable artifact governed. **Cost:** moderate. **Risk:** low-to-medium. **Impact:** medium — turns C-01's mitigation from a recommendation into a recorded fact |
| **Maximal** | + fidelity as a declared **value** with invariants rather than a boolean. **Cost:** high, and partly a domain-modelling problem. **Risk:** **high — fabricated precision.** A declared fidelity nobody can check is C-04 where it does most damage. **Impact:** significant; proxy quality becomes a governed measurement |
| **Verdict** | **REMOVABLE** — MEASURED BY PROTOTYPE (`b07` §H4: `SPACE` alone UNSATISFIABLE with a named shortfall; two authorities for one source set accepted; conjunction distinguished from alternative; Step 9 exit criterion met) |
| **Residual** | A hyperedge's callable is not inspectable — it may declare three sources and read one. `lossy` remains unquantified. The composite-domain workaround stays legal, and should |

### A-24 · An append-only register imposes a total order on records

| Field | Content |
|---|---|
| **Area** | B-06 |
| **Ω∞-A class** | BLOCKING, open. "The deepest internal contradiction found" |
| **Observation** | The temporal model admits `CONCURRENT`; a hash chain requires each entry to name exactly one predecessor. `registry.py` is **absent** |
| **Reproduction** | `b01` §B-01.7 (module absence); `b07` §H5 (the DAG alternative) |
| **Architectural cause** | **ARCHITECTURE-INDUCED, designed and unbuilt** |
| **Consequence** | Two federated observers could not both append, and the chain would manufacture the ordering A-02 exists to eliminate |
| **Minimal** | Write it as a Merkle **DAG**. **Cost: zero relative to writing it as a chain.** **Risk:** low — measured: `verify()` is a DAG traversal and **tamper evidence is unchanged** (detected after mutation). **Impact:** high; removes the deepest recorded internal contradiction before it exists |
| **Moderate** | + total order emitted as a record declaring itself a `PROJECTION` with its tie-break basis named. **Cost:** small. **Risk:** low. **Impact:** positive; an order cannot be mistaken for a measurement |
| **Maximal** | + each entry carries the `TemporalCoordinate` its writer observed, so DAG structure and temporal structure are **comparable and their disagreement reportable**. **Cost:** moderate. **Risk:** medium — sibling-in-DAG and `INCOMPARABLE`-in-coordinates is a real disagreement that must be reported, not reconciled. **Impact:** highest; the only option under which register and temporal model are held to each other |
| **Verdict** | **REMOVABLE AT ZERO COST** — MEASURED BY PROTOTYPE (`b07` §H5: concurrent sibling pair, third entry naming both predecessors, `verify()` ok, tampering detected, total order labelled `kind=PROJECTION`, `asserted_by_register=False`; Step 1 exit criterion met) |
| **Residual** | A DAG grows heads without bound absent merges — head count becomes a governed population. **C-03 is untouched: a total order over distributed events remains chosen, not recovered.** The DAG's contribution is that the choice is visible in the record |

---

## 3. THE MATRIX — CRITICAL FINDINGS

### A-15 · The governed population is finite and materialisable

| Field | Content |
|---|---|
| **Area** | B-01 (partitioned verification) |
| **Ω∞-A class** | CRITICAL, open |
| **Observation** | `census`, `assert_total`, `separation_report`, `population_of`, `resolve_all`, `fallback_density` all take an `Iterable` and exhaust it. No streaming, no sampling, no incremental digest |
| **Reproduction** | STRUCTURAL (single-pass materialisation at all six sites); `b07` §H6 |
| **Architectural cause** | **IMPLEMENTATION-INDUCED.** The *result type* of `census` is already a monoid under pointwise addition; only the aggregation is written as one pass |
| **Consequence** | Rule 9's "indefinite growth" holds for the **vocabulary** and fails for the **population**. A federation of a billion artifacts cannot be governed by these functions |
| **Minimal** | A `merge` over the existing return value. **Cost:** very small. **Risk:** low. **Impact:** **none — no interface break**, the merge is additive over the existing type |
| **Moderate** | Every reporter expressed as a mergeable summary. **Cost:** moderate. **Risk:** medium — **`fallback_density` is a RATIO and a ratio is not a monoid**; it must be carried as a `(numerator, denominator)` pair and divided only at the end. `assert_total` and `separation_report` are likewise not additive in the same way |
| **Maximal** | + partial censuses as first-class governed artifacts with their own digests, so a merge is auditable. **Cost:** high. **Risk:** medium. **Impact:** significant; makes an unbounded population's census reproducible from parts |
| **Verdict** | **REMOVABLE** — MEASURED BY PROTOTYPE (`b07` §H6: three disjoint shard censuses merged **equal** the census of the union, in any merge order, identity `{}`; a one-artifact-at-a-time stream reproduces it exactly) |
| **Residual** | The ratio problem above. **New in Ω∞-B** |

### A-16 · Invariants can be proven by exhaustive enumeration

| Field | Content |
|---|---|
| **Area** | B-01 |
| **Ω∞-A class** | CRITICAL, open. "Most important finding in this register" |
| **Observation** | Growth is **Θ(3ⁿ)** in axis count — `\|S\|(n) = 900 · 2 · 3^(n−7)`, reproducing all four Ω∞-A data points (900 / 1,800 / 48,600 / 2,869,781,400). Measured threshold: 13 axes = 13.5 s; 20 ≈ 5.5 h; 25 ≈ 55 days. **And the measurement Ω∞-A did not take: the enumerated vectors carry almost no assurance.** `CERTIFIED` has **300** distinguishable cases against 900 enumerated (3× redundancy at 6 axes, **9,565,938×** at 20), because a newly registered axis appears in **no** existing edge's `blocked_by` and therefore adds **exactly zero** distinguishable cases. **And: `invariants.py` is ABSENT** — 9 of the 11 modules `__init__.py`'s own table documents do not exist, so the exhaustive proof is a documented claim, not a built artifact |
| **Reproduction** | `b01` §B-01.2, §B-01.3, §B-01.4, §B-01.6, §B-01.7; `b07` §H7 |
| **Architectural cause** | **PROOF-INDUCED** for tractability; **GOVERNANCE-INDUCED** for the false claim (`state.py:58` and `__init__.py:34` assert a module that does not exist) |
| **Consequence** | **A silent expiry.** No exception, no failing test, no migration prompt — the proof becomes unrunnable while every document continues to claim it. And §2's measurement makes it worse: the exponential cost buys nothing |
| **Minimal** | **Correct the false claims first**, then replace enumeration with the structural argument. **Cost:** small (~15 lines + prose). **Risk:** low — the argument is executable and was executed at 6, 20 and 40 axes. **Impact:** none; no type or record changes |
| **Moderate** | + an exhaustive cross-check that **DECLINES above a declared limit with a stated reason**; + a mechanical check that every module named in `__init__.py` exists. **Cost:** moderate. **Risk:** low — declining is the safe path. **Impact:** positive; the claim expires **loudly**, the same discipline `Invariant.predicate is None` already applies |
| **Maximal** | + every invariant's proof method and complexity declared as **data**, an intractable method refused at registration, incremental re-proof on edge registration. **Cost:** high. **Risk:** medium — a declared complexity nobody checks is C-04; mitigate by holding the declared class against measured runtime at two sizes. **Impact:** significant; assurance becomes a governed value rather than a paragraph |
| **Verdict** | **PARTIALLY REMOVABLE.** Tractability: **REMOVABLE** — MEASURED BY PROTOTYPE (structural proof holds at 40 axes over 15,009,463,529,699,912,100 vectors in ~66 µs; exhaustive DECLINED with a stated reason; Step 4 exit criterion met). **The remaining part is that six of the seven designed invariants have no proof of any kind, because the module does not exist** |
| **Residual** | R-1 above. Also: the structural argument is a claim about the **declared** edge set, so an edge registered later that targets `CERTIFIED` without naming `UNKNOWN` breaks it and nothing re-checks. **And a finding about the two methods: a naive product enumeration reports 36 false violations at 6 axes, because the invariant is about REACHABILITY, which is a property of the edge set. The exhaustive method's inner loop already *was* the structural argument, executed 900 times** |

### A-18 · Meaning is carried by English prose

| Field | Content |
|---|---|
| **Area** | B-03 |
| **Ω∞-A class** | HIDDEN, open |
| **Observation** | `MASS` = kilograms on node A, pounds on node B: **both VALID**. Two registries with **byte-identical digests** attach different meanings to `magnitude`: **both VALID** |
| **Reproduction** | `b03_b04` §B-03.3; `b07` §H3 |
| **Architectural cause** | **ONTOLOGY-INDUCED, and the openness is required.** Interpreting `Field.kind` inside `domain.py` would make the expressible kinds a closed list in one file — Rule 4's target |
| **Consequence** | **The consequence is not that federation fails; it is that after A-14's detection half is resolved, federation will appear to work.** A successful digest comparison becomes evidence for a consensus never established |
| **Minimal** | Ratchet `unexecutable_invariants()` as CONVERGENT. **Cost:** very small; the reporter exists. **Risk:** low. **Impact:** none structurally. **This is a mitigation, not a fix** |
| **Moderate** | Require kinds naming a domain to resolve, and **count** those that do not. **Cost:** moderate. **Risk:** medium — **count, do not refuse**, or an unknown civilisation's kind is rejected instead of made visible |
| **Maximal** | Behavioural agreement: exchange test vectors with agreed verdicts. **Cost:** high. **Risk:** **high — it still does not close the gap.** Agreement on a finite sample is not agreement on meaning |
| **Verdict** | **PARTIALLY REMOVABLE**; the residue is **FUNDAMENTAL** (C-04) — MEASURED |
| **Residual** | A deployment could declare every invariant unexecutable and pass validation with zero real checking. Mitigated only by the ratchet — **still not done** |

### A-22 · A relation has exactly three semantic properties · A-27 · Totality is a property of a comparison

| Field | Content |
|---|---|
| **Area** | B-04, B-06 |
| **Ω∞-A class** | A-22 EXPANDABLE, open; A-27 HIDDEN, partially closed |
| **Observation** | `Relation(decided, ordered, coincident, inverse)`; `compare` returns a bare `str`; `Comparison` has fixed fields. A degree lives only in the relation **name** (bucketing works, does not scale) or in free text. A-22 **confirmed: the `QuantumOrdering` pass was a FIT, not generality.** **And a loss Ω∞-A did not record: `Comparison` carries `decided` and `ordered` but NOT `coincident`, so a consumer must string-match the relation name to tell coincidence from concurrency** — the name-based reasoning `assert_consistent` exists to avoid |
| **Reproduction** | `b06` §(f) |
| **Architectural cause** | **ARCHITECTURE-INDUCED**, narrow (a closed property set on a value type); the `Comparison` omission is IMPLEMENTATION-INDUCED |
| **Consequence** | A probabilistic or degree-valued evidence model (A-23) is inexpressible. A comparison record is lossier than the relation it cites |
| **Minimal** | `Comparison.coincident`. **Cost:** trivial. **Risk:** low — record byte change (C-02 backfill). **Impact:** none |
| **Moderate** | + `Relation.properties: Mapping[str, object]` read only by the declaring strategy. **Cost:** small. **Risk:** medium — an uninterpreted bag is C-04 in a new location; the declaring-strategy discipline is the same one `Field.kind` uses. **Impact:** low-medium |
| **Maximal** | + `Ordering.total` names the **precondition** it holds under rather than being a bare boolean (A-27's unapplied deeper fix). **Cost:** moderate. **Risk:** medium. **Impact:** medium — a consumer requiring totality stops trusting a label that holds only within a shape class |
| **Verdict** | **PARTIALLY REMOVABLE** — MEASURED. The properties mapping is removable; a *degree* that any consumer can interpret without prior agreement is C-04 |
| **Residual** | `Ordering.total` remains a bare boolean under minimal and moderate |

---

## 4. THE MATRIX — BARRIERS THAT RESOLVE WITH THE ABOVE

Recorded so the barrier register's BLOCKING and CRITICAL rows are all accounted for. None is an
independent finding.

| Barrier | Ω∞-A severity | Resolves with | Verdict |
|---|---|---|---|
| X-01 governance rule of an unsupported shape | BLOCKING | A-10 | **REMOVABLE** — measured, incl. X-01's fourth shape (cross-artifact) via `PeerStateGuard` |
| X-02 structured justification | BLOCKING | A-09 | **REMOVABLE** — measured |
| X-03 n-ary relationship between domains | BLOCKING | A-21 | **REMOVABLE** — measured |
| X-05 federated vocabulary | BLOCKING (highest in register) | A-14 | **PARTIALLY REMOVABLE** — detection measured; agreement fundamental |
| X-11 total-order register meets concurrent events | BLOCKING (cheapest to fix) | A-24 | **REMOVABLE AT ZERO COST** — measured |
| X-06 unbounded / streaming population | CRITICAL | A-15 | **REMOVABLE** — measured; ratio caveat |
| X-07 many governance axes → proof loss | CRITICAL, self-inflicted | A-16 | **REMOVABLE** — measured at 40 axes |
| X-10 non-Python governance engine | CRITICAL | G-06 (schema emitter, **absent**) | **PARTIALLY REMOVABLE**; residue is C-05 and is not removable |
| X-04 relation needing a fourth property | EXPANDABLE | A-22 | **REMOVABLE** |
| X-12 cross-deployment identifier collision | REPLACEABLE alone, BLOCKING with X-05 | A-14 maximal / A-20 | **REMOVABLE**; record backfill required |
| G-01, G-02 | priority 1, 2 | A-10, A-09 | **REMOVABLE** — measured |
| G-03, G-04 | 4, 5 | A-21, A-22 | **REMOVABLE / PARTIALLY** |
| G-05 storage described not implemented | 3 | — | **REMOVABLE.** ARGUED only: no `StorageProvider` exists to probe. **Not tested in Ω∞-B** |
| G-06 contracts language-neutral in design only | 6 | — | **REMOVABLE.** ARGUED only: `schema.py` absent. **Not tested in Ω∞-B** |
| G-07 | 7 | A-15 | **REMOVABLE** — measured |
| G-09 | 1 | A-16 | **REMOVABLE** — measured |
| G-10 | 1 | A-14 | **PARTIALLY REMOVABLE** — measured |

**Two priority items were not tested in Ω∞-B and are recorded as ARGUED, not measured:** G-05
(storage) and G-06 (schema emission). Both are *absences* rather than *limitations*, so a probe can
only confirm the absence — which `b01` §B-01.7 does. Their removability rests on the same reasoning as
A-11's: nothing exists to be rewritten.

---

## 5. FINDINGS Ω∞-B MEASURED THAT Ω∞-A DID NOT RECORD

| ID | Finding | Classification | Verdict | Why it matters |
|---|---|---|---|---|
| **B-N-01** | **9 of the 11 modules listed in `engine/omega_governance/__init__.py`'s own "READ IN THIS ORDER" table are ABSENT** (2 present: `state.py`, `authority.py`), while `state.py:58` asserts a proof from one of the absent ones. The table is stale **in both directions**: it names `clock.py`, superseded by `temporal/clocks.py`, and omits the 11 modules of `reference/` and `temporal/` that do exist. `schema.py` is a tenth absent module, named in Ω∞-A and unlisted here. Measured mechanically in `b07` §H9 | GOVERNANCE-INDUCED | **REMOVABLE** | It reframes B-01: the proof does not *expire*, it has **never run**. And it broadens A-11/A-24's zero-cost window to six more modules |
| **B-N-02** | **The certification precondition set exists today** as a fixed enumeration of four in `INITIAL_TRANSITIONS` | ARCHITECTURE-INDUCED | **REMOVABLE** | A-11 was recorded UNKNOWN/unbuilt. It is measurable and measured |
| **B-N-03** | **Exactly one authority may relate any two domains** (`dict[tuple[str,str], str]`) | ARCHITECTURE-INDUCED | **REMOVABLE** | Two ephemeris publishers are inexpressible — the normal condition in metrology. Absent from every Ω∞-A register |
| **B-N-04** | **Conjunction is indistinguishable from alternative**: `path()` returns a complete route from insufficient inputs | ARCHITECTURE-INDUCED | **REMOVABLE** | Raises A-21 from an expressiveness gap to a **correctness defect producing wrong answers today** |
| **B-N-05** | **Transitivity is never checked.** A cyclic ordering violating it passes `assert_consistent` | IMPLEMENTATION-INDUCED | **REMOVABLE** (sampled) | `assert_consistent` verifies 3 of the properties an ordering can have. Absent from Ω∞-A |
| **B-N-06** | **A bare `str` position is silently exploded per character and fingerprinted** | IMPLEMENTATION-INDUCED | **REMOVABLE** | The only silent corruption found. It enters a governance record as a legitimate position. The neighbouring case (empty position) is correctly refused |
| **B-N-07** | **A digest cannot see a registered predicate.** `Invariant.predicate` is a `Callable` | IMPLEMENTATION-INDUCED with an ontology-induced residue | **PARTIALLY REMOVABLE** | The sharpest limit on A-14's digest resolution |
| **B-N-08** | **`fallback_density` is a ratio, and a ratio is not a monoid** | IMPLEMENTATION-INDUCED | **REMOVABLE** | A-15's mergeable-census resolution does not extend to it unchanged |
| **B-N-09** | **A reversed arrow of time registers and operates.** No code asserts an arrow direction | — | **CLOSED, and stronger than recorded** | The architecture holds **no privileged chronology**, a stronger result than "no wall clock" |
| **B-N-10** | **A naive cyclic ordering is refused by antisymmetry**, with no knowledge of cycles | — | **A CORRECT REFUSAL** | The architecture's self-checking catching a hostile model. Second observation of the A-27 property |
| **B-N-11** | **`assert_provider` advances the clock it verifies** — `(0,)` → `(3,)` | IMPLEMENTATION-INDUCED | **REMOVABLE** | A determinism defect in the module whose absence of `datetime` is its headline deliverable |
| **B-N-12** | **Moving certification preconditions out of `blocked_by` would break the structural proof** | ARCHITECTURE-INDUCED | **A CONSTRAINT ON THE RESOLUTION** | B-01 and B-05 pull opposite ways on one field. A resolution ignoring this trades one blocker for the other |

---

## 6. OUT OF SCOPE BY DIRECTIVE — classified, not resolved

Phase 2's constraint is integration through adapters with no rewriting of existing systems, and the
directive forbids modifying active governance, certification, validation and ratchets. These are
classified for completeness and **no resolution is proposed**.

| ID | Finding | Ω∞-A severity | Classification |
|---|---|---|---|
| A-25 / X-17 | 264 enumerations, 1,372 members across 7 trees | CRITICAL (aggregate) | IMPLEMENTATION-INDUCED. Ω∞-A Deliverable 4 triages: **~60 are true invariants and should stay closed.** The recommendation is not conversion but that **every closed list carry a written argument for its closedness** — and the absence of the argument is the finding |
| X-13 | A sixth Ω-1 disposition requires a source edit at **8 sites** | CRITICAL | ARCHITECTURE-INDUCED (legacy) |
| X-19 | A governance surface outside one repository — 42 git-invoking files | CRITICAL | ARCHITECTURE-INDUCED (legacy) |
| X-20 | A representation other than JSON or an identity other than SHA-256 — 404 `json`, 56 `hashlib` | CRITICAL | ARCHITECTURE-INDUCED (legacy) |
| A-01, A-05, A-12, A-13 | wall clock, JSON/SHA-256, filesystem, git — in the **legacy** trees | CRITICAL, closed in the Phase 2 tree | ARCHITECTURE-INDUCED (legacy); measured as **0 occurrences** in `engine/omega_governance/**` |

---

## 7. DETERMINATION

**No closure is declared. No readiness is claimed. No certification is issued. No seal is generated.
No ratchet is advanced.**

What is established, mechanically:

| Question the directive asks | Determination |
|---|---|
| Is every BLOCKING and CRITICAL finding's architectural source located? | **Yes**, with a cited type, field, index or module for each |
| Is each classified? | **Yes**: 8 implementation-induced, 7 architecture-induced, 1 proof-induced, 2 governance-induced, 3 ontology-induced, 1 mathematically unavoidable |
| Is each verdict evidenced? | **Yes**: 15 MEASURED BY PROTOTYPE, the rest MEASURED or STRUCTURAL. **Two exceptions recorded as ARGUED: G-05 and G-06** |
| Is any blocker fundamental? | **No BLOCKING or CRITICAL finding is fundamental in its own right.** One element inside A-14 is (C-04), and it is already a fundamental constraint rather than a blocker |
| Minimum-change and maximum-correctness paths for each? | **Yes**, three options each, with cost, risk and architectural impact |

**The single most important thing this matrix establishes.** Ω∞-A's central worry was that the two most
severe findings (proof tractability, vocabulary consensus) fell outside the directive's own categories,
and that a list which misses its worst items is probably still incomplete. Ω∞-B tested both. **Proof
tractability is removable and the resolution is strictly cheaper and stronger than what it replaces.
Vocabulary consensus is half removable and half fundamental — and the fundamental half was already
predicted by Ω∞-A's own falsification criterion 5, which fired exactly as written.** An architecture
whose stated falsification criteria fire where predicted and stay silent where predicted is behaving as
a falsifiable artifact should.

**What would make this matrix wrong.** A prototype that works in `probes/` is not a resolution in
`engine/`. Every "MEASURED BY PROTOTYPE" verdict establishes that a blocker is *implementation-induced*
— it does not establish that the implementation will be correct, complete, or free of the record-shape
consequences named in each row's risk column. **Six of the twelve resolutions require a record backfill
(C-02), and one (A-10 maximal) is not backward compatible.** Those costs are real and are stated in the
rows rather than in this conclusion.
