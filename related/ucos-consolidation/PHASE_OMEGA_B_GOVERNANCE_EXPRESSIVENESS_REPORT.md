# UCOS Ω∞ — PHASE Ω∞-B, DELIVERABLE 5
## Governance Expressiveness Report (B-02)

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


**AUTHORITY = NONE (DERIVED TRUTH).** Analysis and classification only. No certification, no seal, no
ratchet advancement, no closure declaration, no readiness claim, and no modification to any active
governance, validation or certification process.

**INPUT.** Ω∞-A findings A-09 (BLOCKING), A-10 (BLOCKING), G-01, G-02, X-01, X-02, and Deliverable 7
§3.3 (the Guard proposal). Treated as authoritative; not re-discovered.

**EVIDENCE ARTIFACTS.**

| Artifact | Purpose |
|---|---|
| `probes/b02_b05_governance_certification.py` + `b02-b05-output.txt` | measures what the shipped model can express, and attempts each capability against it |
| `probes/b07_removability_validation.py` §H1 + `b07-output.txt` | tests whether the eight capabilities are expressible as guards over shipped types |

```
cd /Users/bipin/Desktop/UCOS-CONSOLIDATION
.ec1-venv/bin/python 00-MASTER/UCOS-OMEGA-B-001/probes/b02_b05_governance_certification.py
.ec1-venv/bin/python 00-MASTER/UCOS-OMEGA-B-001/probes/b07_removability_validation.py
```

`b02_b05` re-executed against current repository state is **byte-identical** to its stored output.

---

## 1. THE MEASURED CEILING

### Observation

`Transition` has six fields; exactly two bear a guard.

```
Transition fields    : source, target, rule, justification, requires_reason, blocked_by
GUARD-BEARING fields : requires_reason, blocked_by            -> guard kinds = 2
Transition is frozen : True
```

And the two are narrower than their names suggest:

- **`blocked_by: tuple[GovernanceState, ...]`** is consumed by `state.check` as
  `state in transition.blocked_by` — **a membership test and nothing else.** It can express "forbidden
  while holding X". It cannot express a count, a threshold, a predicate, a context, a peer artifact, or
  a window.
- **`requires_reason: bool`** is consumed as `not reason.strip()` — **a non-blankness test.** It
  detects the absence of *text*; it cannot detect the absence of *argument*.

Reproduced exactly, on the shipped edge Ω²-S-12 (`UNGOVERNED → EXEMPTED`, `requires_reason=True`):

| reason | shipped `check()` |
|---|---|
| `'x'` | **ACCEPTED** |
| `'.'` | **ACCEPTED** |
| `'0'` | **ACCEPTED** |
| `'no'` | **ACCEPTED** |
| `'TODO'` | **ACCEPTED** |
| `'  see ticket  '` | **ACCEPTED** |

And on Ω²-S-22 (`UNCERTIFIED → CERTIFIED`): `check()` **ACCEPTED a reason naming one approver where
three were required.** The shortfall is undetectable, because the only carrier is `reason: str`.

### Reproduction

`b02_b05` §B-02.1, §B-02.2, §B-02.3.

---

## 2. THE EIGHT CAPABILITIES, AS BUILT — every one measured against `authority.py`

### Observation

| # | Capability | As built | Measured cause |
|---|---|---|---|
| 1 | **N-of-M approvals** | **REFUSED** | Three sources claimed `art` at OWNER (BOB twice, ALICE once). `AuthorityLink.__post_init__` applies `set()` to claims → `('ALICE','BOB')`; BOB's two votes became one. `selected = sorted(set(claims))[0]` — an **alphabetical pick**. Multiplicity survives only as `contested=True` |
| 2 | **Quorum** | **REFUSED** | Same cause. There is no count, threshold or roster anywhere in the model |
| 3 | **Delegation** | **REFUSED** | No authority→authority relation exists. `MappingSource.claims` is subject→authority |
| 4 | **Weighted authority** | **REFUSED** | `set()` destroys vote multiplicity *before* any aggregation could occur. Weight has no field to live in |
| 5 | **Conditional authority** | **REFUSED** | `AuthoritySource.claim(subject: str) -> str`. No context, no as-of, no domain. `resolve()` passes nothing else |
| 6 | **Time-bounded authority** | **REFUSED** | No `valid_from`/`valid_until` on any type; `resolve()` has no as-of parameter. Only `FallbackEvent` carries a `TemporalCoordinate`, and only on fallback arrivals |
| 7 | **Revocable authority** | **REFUSED** | `AuthorityResolver` has no `unregister`/`revoke`; `register()` only appends. The single mutation channel (`MappingSource.claims` dict aliasing) **emits no event** |
| 8 | **Multi-domain authority** | **PARTIAL** | Scope-by-SUBJECT works via `ABSTAIN`. Scope-by-DOMAIN does not: `AuthoritySource.tier()` returns exactly one tier and `AuthorityChain` has no domain or scope field |

**Seven refused, one partial. Zero fully expressible.**

### Reproduction

`b02_b05` §B-02.4, which prints the field list of every authority type and the signature of every
resolver method alongside each refusal.

---

## 3. ARCHITECTURAL CAUSE

**IMPLEMENTATION-INDUCED. Not architecture-induced, and the distinction is now measured rather than
argued.**

The cause has three layers, and only the first is a design decision:

1. **A guard is a field, not a value.** `requires_reason` and `blocked_by` are *fields on a frozen
   dataclass*. Because a guard is a field, the set of expressible guard *kinds* is the set of fields,
   and adding a kind is a source edit to `Transition` **and** to `check`. Every other extension point
   in the package is a *registry* (`StateRegistry`, `DomainRegistry`, `CapabilityRegistry`,
   `CodecRegistry`, `IdentityRegistry`, `TransformationRegistry`, `FrameRegistry`, `ClockRegistry`,
   `CalendarRegistry`, `OrderingRegistry`, `RelationRegistry`). **Guards are the one mechanism that was
   not given a registry**, which is exactly Ω∞-A Deliverable 7's finding: four of five mechanisms
   exist, and the fifth is the gap.

2. **A justification is a primitive, not a domain value.** `reason: str` cannot carry an approver, a
   citation, a signature or a quorum record, because a `str` has no schema. The architecture *has* a
   schema mechanism — `Schema`, `Field`, `Invariant`, `ReferenceDomain.validate` — and the transition
   guard does not use it.

3. **Authority multiplicity is destroyed at construction.** `set()` in
   `AuthorityLink.__post_init__` is the sharpest instance, because it is *deliberate* deduplication
   that happens to make weighting and quorum unrepresentable downstream. Nothing later can recover
   what the constructor discarded.

**Why this is implementation-induced and not architecture-induced.** If the architecture forbade these
capabilities, writing them would require changing a shipped type. §4 measures that it does not: all
eight were written against a `Guard` protocol composing over `GovernanceStatus`, `ReferenceDomain`,
`TemporalCoordinate` and the ordering registry **exactly as shipped**.

---

## 4. THE FALSIFICATION TEST — all eight capabilities, written and executed

**Ω∞-A Deliverable 7 §7 falsification criterion 1: "a governance rule that is not expressible as a
composition of guards".** This is the only way to test it, and it is why implementation was permitted
here: the classification of B-02 as removable-or-fundamental is not decidable by inspection.

### Observation

Eleven guards were declared at runtime against a `Guard` protocol identical to Ω∞-A's proposal, and
`check_with_guards` replaced the two built-in guards with registry quantification. **Zero edits to
`engine/`** (verified: `engine/omega_governance/` mtimes unchanged, 11:23–11:26, predating this
session).

With an empty context, the shipped `check()` **PERMITS** certification. The guarded check returns
**seven simultaneous refusals** — a population, not a first failure:

```
GUARD-QUORUM: 0 of 3 required approvals present (eligible=[], ignored_non_roster=[],
              missing=['ALICE','BOB','CAROL','DAVE','ERIN'])
GUARD-FEDERATION-QUORUM: 0 of 2 nodes concur (concurring=[])
GUARD-WEIGHTED-AUTHORITY: approving weight 0 < required 4 (from [])
GUARD-DELEGATION: no acting authority named
GUARD-MULTI-DOMAIN-AUTHORITY: an authority and a domain must both be named
GUARD-PEER-STATE: peer 'baseline' is not in the supplied population
GUARD-TEMPORAL-WINDOW: no temporal coordinate supplied, and none may be invented
```

Each capability, isolated, refusing for its own stated reason — **10 of 10 fired**:

| Capability | Refusal produced |
|---|---|
| N-of-M | `2 of 3 required approvals present (eligible=['ALICE','BOB'], missing=['CAROL','DAVE','ERIN'])` |
| Federation quorum | `1 of 2 nodes concur (concurring=['NODE-A'])` |
| Weighted authority | `approving weight 2 < required 4 (from [('BOB',1),('CAROL',1),('DAVE',0)])` |
| Delegation (cycle) | `delegation from LOOP-A terminates at LOOP-A, which is not a permitted terminal authority ['BOARD']` |
| Conditional authority | `DEPUTY's authority is conditional on delegated_scope=='CERTIFY' and it is 'READ-ONLY'` |
| Time-bounded (outside) | `outside the declared window: required BEFORE on both bounds and got opens->at=BEFORE, at->closes=AFTER` |
| Time-bounded (incomparable) | `the coordinate is not comparable with the window (opens: INCOMPARABLE by Ω²-C-04) — REFUSED rather than assumed inside` |
| Revocable | `MALLORY's grant was revoked: Ω∞-B-REV-01 grant withdrawn` |
| Multi-domain | `DEPUTY holds authority in ['CERTIFICATION','CUSTODY'] and not in 'TREASURY'` |
| Peer state (cross-artifact) | `peer 'baseline' is not in the supplied population` |

With every guard satisfied, the transition is **PERMITTED** via Ω²-S-22 — so the guards are not merely
refusing everything.

### Determination

> **Ω∞-A falsification criterion 1 DID NOT FIRE.** All eight capabilities B-02 enumerates, plus
> cross-artifact conditionality (X-01's fourth inexpressible shape), are expressible as compositions of
> one registered mechanism over shipped types. **B-02 is IMPLEMENTATION-INDUCED and REMOVABLE.**

Two capabilities deserve separate note because they were the ones most likely to require a new
mechanism:

**Time-bounded authority did not reintroduce a wall clock.** A naive window guard would call
`time.time()` and reinstate A-01 inside the mechanism built to remove assumptions. The prototype takes
a `TemporalCoordinate` from the caller and compares it through the registered ordering strategy. Given
an `EARTH_FRAME`/`SI_SECOND` coordinate against a `LOGICAL_FRAME`/`LOGICAL_TICK` window it **refused,
citing rule Ω²-C-04**, rather than assuming inside-the-window. It imports neither `time` nor
`datetime`. **And it resolves its precedence relation by declared name rather than testing for the
literal `"BEFORE"`** — a guard hardcoding `"BEFORE"` would privilege one ordering's vocabulary, which
is A-02 reappearing inside the guard mechanism. This detail was a *defect in the first draft of the
prototype*, caught because an out-of-window coordinate was wrongly accepted; it is recorded because it
demonstrates how easily the assumption re-enters.

**Delegation gained a property the shipped model cannot express at all: cycle refusal.** The prototype
resolves the delegation chain transitively and refuses a cycle by name. A subject→authority mapping
cannot express a cycle, so it cannot refuse one.

### Semantic justification — A-09 closed by prototype

| reason | shipped `check()` | guarded `check()` |
|---|---|---|
| `'x'` | ACCEPTED | **REFUSED** — `missing required field 'approver'; missing required field 'citation'` |
| `'.'` | ACCEPTED | **REFUSED** — same |
| `'TODO'` | ACCEPTED | **REFUSED** — same |
| `'  see ticket  '` | ACCEPTED | **REFUSED** — same |
| a complete `Justification` value (statement + approver + citation) | — | **PERMITTED** via Ω²-S-12 |

The `JUSTIFICATION` domain was declared at runtime with a three-field schema and two invariants. **The
domain machinery needed no change.** One invariant (`Ω∞-B-J-02`, "the cited authority actually approved
this reduction") is declared **deliberately unexecutable** — C-04 in miniature — and is therefore
**counted** by `unexecutable_invariants()` rather than hidden.

---

## 5. CONSEQUENCE IF UNRESOLVED

| Consequence | Concretely |
|---|---|
| **Ω∞ Rule 8 case 6 fails** | An unknown governance model is admitted only if its rules happen to fit two pre-decided shapes. Ω∞-A stated this; it is now measured against all eight named shapes, seven of which do not fit |
| **Every reduction of obligation degrades to "somebody typed something"** | Measured: six strings including `'x'`, `'.'` and `'TODO'` accepted on the exemption edge. A deployment requiring a signed authorisation, a named approver, a quorum record or a citation cannot express any of them |
| **An approval shortfall is undetectable, not merely unenforced** | Ω²-S-22 accepted a reason naming one approver where three were required. There is no field in which the shortfall could be recorded, so no report can count it |
| **Three subsystems will each grow their own condition vocabulary** | State transition, certification and contradiction resolution are the same operation — check conditions, permit or refuse, record why. Built separately, each acquires an incompatible way of saying "blocked because". This is the cost-of-delay mechanism, and B-05 confirms it has already begun: the certification precondition set exists **today** as a frozen tuple |
| **Authority multiplicity is irrecoverable, not just unused** | `set()` in the constructor. Any later feature needing weight or count must first undo a discard that already happened |

---

## 6. RESOLUTION OPTIONS

### Minimal change — promote guards to a registry

Add a `Guard` protocol and a `GuardRegistry`; re-express `blocked_by` and `requires_reason` as two
registered guards; `check` quantifies over the registry for the edge.

```
Guard:
    identifier() -> name
    describes()  -> statement                          # language-neutral, for Rule 6
    evaluate(subject, status, context) -> (bool, Justification | None)
```

- **Cost.** Small, and bounded by two call sites. The protocol plus the two re-expressed guards is
  ~120 lines; `check` changes from two inline tests to one loop. Measured working in `b07` §H1.
- **Risk.** **Low, with one real hazard.** `check` currently returns the *first* refusal; a registry
  returns a *population*. Callers expecting one string must handle a tuple. The hazard is not the
  change but the temptation to preserve the old signature by returning only the first refusal — which
  would discard exactly the information the mechanism exists to produce. `b07` returns the population.
- **Architectural impact.** **This is the one change that makes the five-mechanism core true.** Ω∞-A
  measured four of five mechanisms present with a registry each and guards as the exception. After
  this change, "the architecture has five extension points and no sixth kind of thing needs one" is a
  measurement rather than a proposal.
- **Compatibility.** `Transition` keeps both fields; they become the *declarations from which the two
  standard guards are constructed*. **No stored record changes shape**, and `as_record()` is
  unaffected. Backward compatible.

### Moderate change — the above, plus a justification domain and a context

1. `reason: str` → `Justification` value in a registered domain with a declared schema and invariants.
2. `evaluate` receives a `context: Mapping[str, object]` so a guard may read approvals, an acting
   authority, a temporal coordinate or a peer population.
3. The guard's refusal is a **record**, not a string: guard identifier, statement, and the named
   shortfall.

- **Cost.** Moderate. Domain declaration + `check`/`advance` signature change + `StateChange.reason`
  becomes a value. ~300 lines with tests.
- **Risk.** **Medium, and the risk is a record-shape change.** `StateChange.reason: str` is part of
  the audit record; making it a domain value changes the bytes of every stored change. Ω∞-A C-02 is
  the relevant precedent: this is a **record backfill**, not a code migration, and the honest response
  is to report the population of records carrying a legacy string reason rather than to auto-convert
  them. A second risk: `context` is a `Mapping[str, object]`, so a guard reading a key nobody supplies
  must **refuse** rather than default — the prototype does (`"no temporal coordinate supplied, and
  none may be invented"`), and a guard that defaulted would reintroduce the silent state.
- **Architectural impact.** **High and positive.** It closes A-09/G-02/X-02 and makes the same
  validation machinery serve values and justifications. It also creates the first place where a
  *governance act's own argument* is a governed value.

### Maximal correctness — the above, plus authority repair and one mechanism for three subsystems

4. `AuthorityLink` preserves claim multiplicity (remove `set()`; deduplicate **by name at report
   time**, not at construction) so weight and count are recoverable.
5. `AuthoritySource.claim` takes a context; `AuthorityTier` gains declared scope; grants gain
   revocation as a recorded **event** rather than a mutation.
6. Certification (B-05) and contradiction resolution consume the **same** guard registry.
7. Guard `describes()` output participates in the schema emission of G-06, so a non-Python
   implementer can read the rule.

- **Cost.** High. It touches `authority.py` structurally, and it is the design of two unbuilt modules.
- **Risk.** **Medium-high, concentrated in item 4.** Removing `set()` changes `AuthorityLink.claims`
  and therefore `AuthorityChain`'s record bytes and the `contested` computation. `assert_total`,
  `fallback_density` and `tier_census` all read chains. This is the only item in this report that is
  **not** backward compatible, and it should be sequenced with that stated.
- **Architectural impact.** **Highest available.** It is the difference between a guard mechanism and a
  governance mechanism: after item 6, an unknown governance model arriving tomorrow extends state
  transition, certification and contradiction resolution **at once**, which is Ω∞-A's argument for why
  guards are the core rather than a feature.

---

## 7. COMPATIBILITY IMPACT PER CAPABILITY

| Capability | Required abstraction | Compatibility impact |
|---|---|---|
| N-of-M, quorum | `Guard` + `context["approvals"]` + a declared roster | **None.** Additive; no shipped type changes |
| Federation quorum | `Guard` + a declared node set | **None.** Additive |
| Weighted authority | `Guard` + declared weights — **and** removal of `set()` if the weights are to come from `AuthorityLink` rather than the guard's own declaration | **None** if the guard declares its own weights; **BREAKING** for `AuthorityLink`/`AuthorityChain` record bytes if authority is the source of truth. The prototype takes the first path, deliberately |
| Delegation | `Guard` + an authority→authority relation | **None** in a guard. A first-class delegation relation on `authority.py` would add a field, changing chain records |
| Conditional authority | `Guard` + `context` | **None** in a guard. `AuthoritySource.claim(subject, context)` is a **protocol signature change** — breaking for any external implementer |
| Time-bounded | `Guard` + `TemporalCoordinate` + registered ordering, precedence relation resolved **by declared name** | **None.** Measured: no wall clock, refuses on incomparable frames |
| Revocable | `Guard` + a revocation record | **None** in a guard. `AuthorityResolver.revoke()` emitting an event is additive; the existing silent mutation channel (`MappingSource.claims` aliasing) should be **closed**, which is breaking for anyone relying on it |
| Multi-domain | `Guard` + declared scopes | **None** in a guard. `AuthorityTier` gaining scope changes tier records |

**The pattern is worth stating.** Every capability is **non-breaking as a guard** and **breaking as a
change to `authority.py`**. That is a strong argument for the minimal/moderate path: put the
expressiveness in the registered mechanism, and change `authority.py` only where the *authority model
itself* is wrong — which is item 4, the `set()` that destroys multiplicity.

---

## 8. RESIDUAL RISK

| # | Residual | Why it survives | Severity |
|---|---|---|---|
| R-1 | A guard can be written that is wrong, or that always permits. The mechanism makes rules expressible; it cannot make them correct | C-04 — meaning cannot be fully mechanised | **MEDIUM.** Mitigation is the C-04 mitigation: `describes()` is reviewable, and a guard population that never refuses is countable |
| R-2 | `Ω∞-B-J-02` ("the cited authority actually approved this") is **unexecutable**. A justification can name an approver who never approved | Verifying an external approval needs an external authority | **MEDIUM.** Counted by `unexecutable_invariants()`, not hidden. Ω∞-A recommends ratcheting that count; still not done |
| R-3 | `context: Mapping[str, object]` is an **open** vocabulary. Two guards may expect the same key with different meanings | The same free-string openness as `Field.kind`, and it is C-04 again | **MEDIUM.** Reducible by declaring context keys as a domain; not eliminable |
| R-4 | The prototype's first draft **wrongly accepted an out-of-window coordinate** because it tested `relation.ordered` rather than the declared precedence relation | An ordering-neutral guard is harder to write than it looks | **LOW as a defect, HIGH as a warning.** It is direct evidence that A-02 re-enters through convenience, and it argues for the guard protocol requiring the precedence relation to be *declared* |
| R-5 | Authority multiplicity remains destroyed by `set()` until maximal item 4 | It is a constructor, and the discard has already happened for every stored chain | **MEDIUM.** Any weighted model must either declare its own weights or accept a record-shape change |

---

## 9. GOVERNANCE EXPRESSIVENESS REGISTER

| Cap | Capability | As built | Architectural cause | Required abstraction | Classification | Verdict |
|---|---|---|---|---|---|---|
| E-01 | N-of-M approvals | **REFUSED** | guard is a field; `set()` destroys multiplicity | `Guard` + roster + threshold | IMPLEMENTATION-INDUCED | **REMOVABLE** (measured) |
| E-02 | Quorum | **REFUSED** | as E-01 | `Guard` + declared quorum set | IMPLEMENTATION-INDUCED | **REMOVABLE** (measured) |
| E-03 | Delegation | **REFUSED** | no authority→authority relation | `Guard` + delegation mapping + cycle refusal | IMPLEMENTATION-INDUCED | **REMOVABLE** (measured, and it gained cycle refusal) |
| E-04 | Weighted authority | **REFUSED** | `set()` in `AuthorityLink.__post_init__` | `Guard` + weights; optionally repair `AuthorityLink` | IMPLEMENTATION-INDUCED | **REMOVABLE** (measured) |
| E-05 | Conditional authority | **REFUSED** | `claim(subject)` takes no context | `Guard` + `context` | IMPLEMENTATION-INDUCED | **REMOVABLE** (measured) |
| E-06 | Time-bounded authority | **REFUSED** | no validity bounds; no as-of | `Guard` + `TemporalCoordinate` + declared precedence relation | IMPLEMENTATION-INDUCED | **REMOVABLE** (measured, without a wall clock) |
| E-07 | Revocable authority | **REFUSED** | append-only `register()`; silent mutation channel | `Guard` + revocation event | IMPLEMENTATION-INDUCED | **REMOVABLE** (measured) |
| E-08 | Multi-domain authority | **PARTIAL** | `tier()` returns one tier; no scope field | `Guard` + declared scopes | IMPLEMENTATION-INDUCED | **REMOVABLE** (measured) |
| E-09 | Structured justification | **REFUSED** (syntactic) | `reason: str` has no schema | `Justification` domain value | IMPLEMENTATION-INDUCED | **REMOVABLE** (measured) |
| E-10 | Cross-artifact conditionality | **REFUSED** | `blocked_by` reads only this artifact's vector | `Guard` + peer population in context | IMPLEMENTATION-INDUCED | **REMOVABLE** (measured) |
| E-11 | A *correct* guard | **N/A** | meaning is not mechanisable | none available | **ONTOLOGY-INDUCED** | **FUNDAMENTAL** (C-04) |

**Ten of eleven removable by one mechanism. The eleventh is C-04 and is not a B-02 finding.**

---

## 10. DETERMINATION

**No closure is declared.** Established mechanically:

| Question | Determination | Basis |
|---|---|---|
| Is B-02 removable? | **REMOVABLE** | §4: all ten capabilities written and executed over shipped types, zero edits to `engine/` |
| Classification | **IMPLEMENTATION-INDUCED** | §3: guards are the one mechanism given a field instead of a registry |
| Is any part architecture-induced? | **No.** No shipped type needed to change | §4 |
| Is any part mathematically unavoidable? | **No.** E-11 is ontology-induced (C-04) and is not a governance-expressiveness limit | §9 |
| Does Ω∞-A falsification criterion 1 fire? | **No** | §4 |
| Cost of delay | **Grows with every consumer.** B-05 measures the growth already begun: the certification precondition set exists today as a frozen tuple on two frozen instances | B-05 §1 |

**One correction to Ω∞-A.** Ω∞-A ranked guards 3rd by cost of delay, behind the DAG register and
certification inputs, on the grounds that guards cost "small now, grows with every consumer". The
measurement supports the ranking but sharpens it: **the certification consumer already exists as a
frozen enumeration**, so one of the three consumers Ω∞-A anticipated has already grown its condition
vocabulary. Guards and certification inputs are not sequential items; they are one item, exactly as
Ω∞-A Deliverable 7 §3.3 argues ("Also makes A-11 impossible").
