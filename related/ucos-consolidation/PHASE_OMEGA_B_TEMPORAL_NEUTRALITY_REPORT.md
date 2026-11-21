# UCOS Ω∞ — PHASE Ω∞-B, DELIVERABLE 9
## Temporal Neutrality Report (B-06)

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

**INPUT.** Ω∞-A findings A-01, A-02, A-03 (all CRITICAL/REPLACEABLE, recorded CLOSED in the Phase 2
tree), A-22 (EXPANDABLE), A-24 (BLOCKING), A-27 (HIDDEN, partially closed), C-03 (FUNDAMENTAL), G-04.
Treated as authoritative.

**WHAT THIS REPORT IS FOR.** Ω∞-A recorded the replacement temporal architecture as closing the four
privileged assumptions it set out to close. This report does not re-verify those closures. It attempts
to **break** the replacement by registering temporal models hostile to it, and reports what the
architecture accepted, refused, or accepted-when-it-should-have-refused.

**EVIDENCE ARTIFACTS.**

| Artifact | Purpose |
|---|---|
| `probes/b06_temporal_neutrality.py` + `b06-output.txt` | seven hostile temporal model registrations, and a residual-assumption sweep |
| `probes/b07_removability_validation.py` §H8 + `b07-output.txt` | tests whether each residual is removable over shipped types |

```
cd /Users/bipin/Desktop/UCOS-CONSOLIDATION
.ec1-venv/bin/python 00-MASTER/UCOS-OMEGA-B-001/probes/b06_temporal_neutrality.py
.ec1-venv/bin/python 00-MASTER/UCOS-OMEGA-B-001/probes/b07_removability_validation.py
```

`b06` re-executed against current repository state is **byte-identical** to its stored output.

---

## 1. HOSTILE TEMPORAL MODELS — seven attempts

### (a) A clock with no ordering at all — **ACCEPTED**

Registered and passed `assert_consistent`. Totality is skipped (`total=False`) and antisymmetry holds
because `INCOMPARABLE` is self-inverse.

**Residual:** the ordering *field* is still mandatory. `ClockProvider.ordering()` and
`TemporalCoordinate.ordering` have no default, so "no ordering" must be spelled as **an ordering that
refuses**. That is a defensible design — a coordinate that declines to state its discipline would be
worse — but it means the architecture has no representation for "this clock has no notion of order",
only for "this clock's notion of order answers INCOMPARABLE".

**Classification:** ONTOLOGY-INDUCED, and correctly handled. Not a barrier.

### (b) Cyclic / recurring time — **PARTIAL, LOSSY, and it exposes a real gap**

Two results, and the second is the finding.

**A naive cyclic ordering is REFUSED by the antisymmetry check** at the antipodal pair:

```
PROBE_CYCLIC_NAIVE compares (3,) vs (9,) as AFTER but (9,) vs (3,) as AFTER,
where BEFORE was required by the declared inverse
```

**This is a valuable refusal that Ω∞-A did not record.** The architecture caught a genuinely
inconsistent temporal model without knowing anything about cycles, purely from the declared inverse
relation. That is the self-checking property Ω∞ Rule 8 asks for, observed a second time (Ω∞-A A-27 was
the first).

**A repaired — antisymmetric — cyclic ordering is ACCEPTED even though it violates transitivity:**

```
compare(0,5)=BEFORE  compare(5,10)=BEFORE  compare(0,10)=AFTER   -> transitivity VIOLATED
assert_consistent accepted it anyway: TRANSITIVITY IS NEVER CHECKED.
```

And two distinct occurrences at one recurring position are the **same coordinate**:

```
tick 3 vs tick 15 (same face position, next revolution): equal=False  identity differs=True
tick 3 rev-0 vs tick 3 rev-1, modelled WITHOUT a revolution component:
  equal=True  identity identical=True
```

The revolution count must be carried as a position component — **a modelling obligation nothing states
and nothing enforces.** A caller who omits it produces two governance records that are byte-identical
and describe different instants.

**Classification:** the transitivity gap is IMPLEMENTATION-INDUCED and removable (§3, R-4). The
modelling obligation is ONTOLOGY-INDUCED and can only be documented.

### (c) Reversed arrow of time — **ACCEPTED**

```
compare((1,),(2,)) = AFTER   (the shipped lexicographic strategy answers BEFORE)
```

No code asserts an arrow direction. The `<` means BEFORE convention lives only inside the four shipped
strategies, which a new registration does not touch.

**Determination: the architecture holds NO privileged chronology.** This is a genuine neutrality
result, and it is stronger than "no wall clock" — it means the *direction* of time is a strategy's
declaration rather than an architectural premise.

### (d) Branching / forked history — **ACCEPTED, and it ships**

`BranchingStrategy` + `BRANCHING` ordering + `SIMULATION_FRAME` + `SIMULATION_STEP`/`BLOCK_HEIGHT`
scales all ship.

```
branch 0 vs branch 1: INCOMPARABLE
same branch, later step: BEFORE
```

Divergent branches answer `INCOMPARABLE`, never `CONCURRENT` — **the correct distinction**, and the one
C-03 rests on. `CONCURRENT` is an answer ("both are real and neither precedes"); `INCOMPARABLE` is a
refusal ("nothing is declared that would let these be compared"). Two forked histories are the second,
not the first.

### (e) Interval-valued (non-point) coordinates — **ACCEPTED**

```
interval coordinate encodes: 9e3c647a561efcaf18901b58
DURING: PROBE_DURING   CONTAINS: PROBE_CONTAINS   OVERLAP: CONCURRENT
```

`Position = tuple[object, ...]` with no arity cap, and Allen interval relations register as mutually
inverse `Relation` values.

**Residual:** an interval relation declared `ordered=True` with no inverse is refused
(`ordering.py` `Relation.__post_init__`), so Allen relations must be declared **in inverse pairs**. That
is a correct constraint — antisymmetry is uncheckable without an inverse — but **nothing documents it**,
so a caller declaring `DURING` alone learns of the requirement from an exception.

### (f) Probabilistic / weighted ordering with a confidence degree — **PARTIAL, LOSSY**

```
Relation fields: name, description, decided, ordered, coincident, inverse
OrderingStrategy.compare returns: str  (a relation NAME, no payload)
Comparison fields: relation, rule, reason, left, right, decided, ordered
bucketed relation PROBE_BEFORE_P90: ACCEPTED (degree encoded in the NAME)
stochastic strategy: assert_consistent PASSED  <- unexpected
```

A numeric degree has **nowhere to be stored** except inside the relation *name* or the free-text
`reason`. Bucketing works and does not scale; a genuinely stochastic strategy is refused by the
antisymmetry check.

**Ω∞-A A-22/G-04 confirmed: the `QuantumOrdering` pass was a FIT, not generality.**

**And a loss Ω∞-A did not record:** `Comparison` carries `decided` and `ordered` but **not
`coincident`**, so a consumer of a comparison *record* must string-match the relation name to tell
coincidence from concurrency — the exact name-based reasoning `assert_consistent` exists to avoid. The
record is lossier than the relation it cites.

### (g) Opaque symbolic position with no numeric magnitude — **ACCEPTED**

```
symbolic coordinate   : ('PROBE_FRAME','PROBE_SYMBOLIC','TOTAL',('EPOCH-ALPHA',),'probe-symbolic')
identity under default: 6829d28d29e24b40eb1e4ba2
vs numeric, cross-shape: INCOMPARABLE
EMPTY position: REFUSED — "a coordinate with an empty position locates nothing"
BARE STRING position: ACCEPTED and SPLIT into ('E','P','O','C','H')  <- silent corruption
```

`_shape_of` gives symbols their own shape class so totality is not demanded against integers, and
cross-shape comparison answers `INCOMPARABLE`.

**Residual, and it is the only silent corruption in the whole sweep:** a bare `str` is exploded into
per-character components by `tuple(self.position)` — a coordinate the caller did not intend, accepted
**without a refusal**. It then **fingerprints**, so it enters a governance record as a legitimate
position. An empty position is correctly refused; a five-character accident is not.

### Summary of the seven

| Model | Outcome | Nature |
|---|---|---|
| (a) no ordering | **ACCEPTED** | correct; residual is a mandatory field |
| (b) cyclic / recurring | **PARTIAL, LOSSY** | naive form correctly refused; repaired form accepted despite violating transitivity |
| (c) reversed arrow | **ACCEPTED** | genuine neutrality — no privileged chronology |
| (d) branching | **ACCEPTED (ships)** | correct `INCOMPARABLE` vs `CONCURRENT` distinction |
| (e) interval-valued | **ACCEPTED** | residual: inverse pairs required, undocumented |
| (f) probabilistic | **PARTIAL, LOSSY** | A-22 confirmed; `Comparison` omits `coincident` |
| (g) symbolic | **ACCEPTED** | residual: bare `str` silently exploded and fingerprinted |

**Four accepted cleanly, two partial, one accepted with a silent corruption. No hostile model was
refused for a reason that revealed a privileged assumption about clocks, calendars, chronology,
timestamps or reference frames.**

---

## 2. THE DIRECTIVE'S SIX QUESTIONS, ANSWERED AGAINST MEASUREMENT

| Privileged assumption about… | Present? | Evidence |
|---|---|---|
| **clocks** | **NO** | `engine/omega_governance/**` imports neither `datetime` nor `time` (measured: 0). A clock with no ordering, a non-numeric clock and a reversed clock all registered. No module-level default clock instance exists |
| **calendars** | **NO** | `assert_presentation_only` holds under both encodings; rendering leaves equality and fingerprint unchanged. Gregorian arithmetic is confined to one deletable class implemented without `datetime` |
| **ordering** | **NO** | Five orderings ship and a sixth registers; `Ordering.total` is a declaration, and totality is enforced **within a shape class** (A-27's fix). **Residual R-1:** five ordering *names* are reserved |
| **chronology** | **NO** | (c) reversed arrow accepted. No code asserts an arrow direction |
| **timestamps** | **NO** | `TemporalCoordinate` has **no `<` operator** and **no field with a default**; `canonical_key()` is named so it cannot be mistaken for a temporal claim |
| **reference frames** | **NO, with one residual** | Seven frames ship; `INTERSTELLAR` registered at runtime; unrelated frames answer `INCOMPARABLE` with a cited rule; `FrameRelation` carries **no arithmetic**. **Residual R-2:** a frame cannot be declared incomparable with itself |

**The replacement temporal architecture holds no privileged assumption in any of the six categories the
directive names.** That is a strong result and it is measured, not asserted.

---

## 3. RESIDUAL PRIVILEGED ASSUMPTIONS — five, beyond the four Ω∞-A closed

### R-1 — five ordering names are reserved in every registry ever constructed

**Observation.**

```
OrderingRegistry(()) already declares 5 orderings: ['BRANCHING','CAUSAL','DISTRIBUTED','PARTIAL','TOTAL']
redeclaring TOTAL with different semantics: REFUSED
  ("ordering 'TOTAL' is already declared with a different meaning; choose a different name")
```

An `OrderingRegistry` constructed with **no strategies** still declares five orderings from a module
constant.

**Architectural cause.** IMPLEMENTATION-INDUCED. `OrderingRegistry.__init__` seeds `_orderings` from
`INITIAL_ORDERINGS` unconditionally, where `StateRegistry` takes its seed as a **parameter**. The
pattern for fixing it exists in the same package.

**Consequence.** A deployment whose ordering discipline happens to be called `TOTAL` but means
something else must choose a different name.

**Verdict: PARTIALLY REMOVABLE.** The removable part is the unconditional seed. **The irreducible part
is the refusal to redefine a name, and it must stay** — Ω∞-A records the principle as "open to
extension, closed to redefinition", and a rule citing a name that two parties define differently is
unenforceable. Cross-vocabulary name collision is A-20, closed by `(authority, identifier)`, not here.

### R-2 — a frame cannot be declared incomparable with itself

**Observation.** `comparable(EARTH, EARTH) -> Ω²-F-00` — a rule **fabricated by the registry**, which no
caller declared. `frames.py:399` states the reasoning: "IDENTITY IS ALWAYS COMPARABLE… requiring one
would mean every deployment starts by declaring seven reflexive relations, and a deployment that forgot
would find its own records incomparable with each other."

**Architectural cause.** ARCHITECTURE-INDUCED, and defensible for a *reference frame*.

**Consequence, and it is the part the reasoning does not cover.** It is **not** defensible for every
frame. A frame representing a measurement that cannot be repeated — a destructive test, a one-time
astronomical event, an unrepeatable observation — is **not** comparable with itself across two
observations, and the architecture has no way to say so. This is C-01's neighbourhood: an unrepeatable
observation is being treated as trivially self-relatable.

**Verdict: PARTIALLY REMOVABLE.** Let reflexivity be *declarable*, defaulting to declared-identity for
the shipped frames. Local change; no type change.

### R-3 — a refusal cites a relation the emitting registry cannot resolve

**Observation.**

```
RelationRegistry(seed=(BEFORE, AFTER)) -> 'INCOMPARABLE' resolvable: False
compare() emitted relation='INCOMPARABLE' rule=Ω²-C-04
that relation is resolvable in the registry that produced the record: False
```

`coordinate.compare`'s refusals cite `INCOMPARABLE` from a **module constant**, bypassing the relation
registry.

**Architectural cause.** IMPLEMENTATION-INDUCED. A convenience import.

**Consequence.** A registry seeded without `INCOMPARABLE` emits `Comparison` records naming a relation
the same registry cannot resolve — a governance record citing a vocabulary entry that does not exist in
the vocabulary that produced it.

**Verdict: REMOVABLE.** Resolve the refusal relation *through* the registry, and refuse the registry
itself at construction if it declares no undecided relation. No type changes.

### R-4 — no transitivity, reflexivity or irreflexivity check exists anywhere

**Observation.** `assert_consistent` verifies exactly three properties: relation-name membership,
within-shape totality, and antisymmetry. It accepted a cyclic ordering that violates transitivity
(§1(b)).

Is a check *writable* over shipped types? Measured in `b07` §H8:

```
transitivity check over the SHIPPED lexicographic strategy: 0 findings
transitivity check over the REPAIRED CYCLIC ordering:  6 findings
  (0,) BEFORE (5,) BEFORE (10,) but (0,) AFTER (10,)
  (10,) BEFORE (0,) BEFORE (5,) but (10,) AFTER (5,)
  ... 4 more
```

**Architectural cause.** IMPLEMENTATION-INDUCED. `Relation` already declares `ordered`, which is all a
transitivity check needs.

**Consequence.** An ordering that is inconsistent in a way antisymmetry does not catch passes
verification, and every comparison it produces enters a governance record as an ordering claim.

**Verdict: REMOVABLE**, with a residual that must be stated: the check is **O(n³) in the sample**, so it
is a **sampled property, not a proof**, and must be labelled as sampled wherever it is reported. Ω∞-A's
own standard — make the unchecked population countable rather than absent — applies directly.

### R-5 — `assert_provider` mutates the clock it verifies

**Observation.**

```
LogicalClock position before assert_provider=(0,) after=(3,)
```

`assert_provider(clock, *, readings: int = 2)` calls `read()` twice by default, so verifying a counting
clock advances it.

**Architectural cause.** IMPLEMENTATION-INDUCED.

**Consequence.** Any evidence run that verifies its own clock records a position that **depends on
whether verification ran** — a determinism defect in the module whose absence of `datetime` is its
headline deliverable. This is the same class of error as A-01, arriving through the verifier rather
than the clock.

**Verdict: REMOVABLE.** Verify a copy, or declare the reading count in the record.

---

## 4. TEMPORAL NEUTRALITY REGISTER

| ID | Finding | Observation | Architectural cause | Classification | Verdict |
|---|---|---|---|---|---|
| N-01 | No privileged clock | 0 `datetime`/`time` imports; clock with no ordering accepted | — | **CLOSED** (Ω∞-A A-01, re-confirmed) |
| N-02 | No privileged calendar | `assert_presentation_only` holds under both encodings | — | **CLOSED** (A-03) |
| N-03 | No privileged chronology | reversed arrow ACCEPTED | — | **CLOSED**, and stronger than Ω∞-A recorded |
| N-04 | No privileged timestamp | no `<`, no field defaults, `canonical_key()` named to disclaim | — | **CLOSED** (A-02) |
| N-05 | No frame arithmetic | `FrameRelation` carries none; 2 of 3 shipped transformations compute nothing and say so | — | **CLOSED** (C-03) |
| N-06 | `CONCURRENT` ≠ `INCOMPARABLE` | branch 0 vs 1 = INCOMPARABLE; two VectorClocks = CONCURRENT | — | **CLOSED**, and it is what C-03 rests on |
| N-07 | Naive cyclic ordering refused by antisymmetry | antipodal pair caught with no knowledge of cycles | — | **A CORRECT REFUSAL.** **New in Ω∞-B**; self-checking observed a second time |
| N-08 | **Transitivity is never checked** | repaired cyclic ordering ACCEPTED while violating it; 6 violations found by a written check | IMPLEMENTATION-INDUCED | **REMOVABLE** (sampled). **New in Ω∞-B** |
| N-09 | Recurrence requires an unstated modelling obligation | tick 3 rev-0 and rev-1 are byte-identical records | ONTOLOGY-INDUCED | **PARTIALLY REMOVABLE** — documentable, not enforceable. **New in Ω∞-B** |
| N-10 | Allen relations must be declared in inverse pairs, undocumented | `ordered=True` with no inverse refused | IMPLEMENTATION-INDUCED | **REMOVABLE** (documentation). **New in Ω∞-B** |
| N-11 | A degree has nowhere to live | `Relation` has 3 booleans; `compare` returns a bare `str` | ARCHITECTURE-INDUCED | **REMOVABLE** — `Relation.properties` (A-22 confirmed) |
| N-12 | `Comparison` omits `coincident` | consumer must string-match the relation name | IMPLEMENTATION-INDUCED | **REMOVABLE.** **New in Ω∞-B** |
| N-13 | Bare `str` position silently exploded and **fingerprinted** | `'EPOCH'` → `('E','P','O','C','H')`, accepted | IMPLEMENTATION-INDUCED | **REMOVABLE** — one `isinstance` refusal. **New in Ω∞-B** |
| N-14 | Five ordering names reserved unconditionally | `OrderingRegistry(())` declares 5 | IMPLEMENTATION-INDUCED | **PARTIALLY REMOVABLE** (R-1) |
| N-15 | Reflexive frame relation fabricated | `comparable(EARTH,EARTH)` → `Ω²-F-00`, undeclared | ARCHITECTURE-INDUCED | **PARTIALLY REMOVABLE** (R-2) |
| N-16 | Refusal cites a relation the registry cannot resolve | `INCOMPARABLE` from a module constant | IMPLEMENTATION-INDUCED | **REMOVABLE** (R-3) |
| N-17 | `assert_provider` advances the clock it verifies | `(0,)` → `(3,)` | IMPLEMENTATION-INDUCED | **REMOVABLE** (R-5) |
| N-18 | The register would impose a total order on `CONCURRENT` records | designed hash chain; **module absent** | ARCHITECTURE-INDUCED (designed, unbuilt) | **REMOVABLE AT ZERO COST** — see §5 |
| N-19 | A total order over distributed events cannot be *recovered* | property of the world | **MATHEMATICALLY UNAVOIDABLE** | **FUNDAMENTAL** (C-03) |

**Six closed. Nine removable. Three partially removable. One fundamental.**

---

## 5. A-24 / N-18 — the one temporal finding with a deadline, tested

### Observation

Ω∞-A A-24: "**The deepest internal contradiction found.** The temporal model admits `CONCURRENT`; a
hash chain requires each entry to name exactly one predecessor. So the register would impose a total
order on records whose *coordinates* the same architecture declares unordered." Recorded as design
inspection only — `registry.py` does not exist.

Tested in `b07` §H5 with a Merkle **DAG** prototype:

```
entries            : 4
concurrent siblings: [['379ff347a2ee','b196cf307650']]
heads              : ['df9499eba25a']
verify()           : ok=True problems=()
total order        : kind=PROJECTION  asserted_by_register=False
                     basis=topological, ties broken by digest — A CHOICE, NOT A MEASUREMENT
after tampering    : ok=False problems=1
```

Two writers appended concurrently, each observing only the root, producing a **sibling pair**. A third
entry named **both** predecessors. `verify()` passed, and detected tampering after mutation — so
**tamper evidence is unchanged by the DAG shape**, which is the property a chain was chosen for.

Total order is emitted as a record whose own `kind` is `PROJECTION` and whose `asserted_by_register` is
`False`, with the tie-break basis stated as a choice.

> **Ω∞-A Step 1's exit criterion — "two independent writers append concurrently, the DAG verifies, and
> a requested total-order projection is labelled as a projection in the record it produces" — is MET BY
> PROTOTYPE. Its cost-of-delay claim is CONFIRMED: `registry.py` still does not exist, so nothing was
> rewritten to obtain this result.**

### Resolution options

| Option | Change | Cost | Risk | Architectural impact |
|---|---|---|---|---|
| **Minimal** | Write the register as a DAG rather than a chain | **Zero relative to writing it as a chain.** Measured | **Low.** `verify()` is a DAG traversal; tamper evidence measured unchanged | **High and positive.** Removes the deepest recorded internal contradiction *before* it exists |
| **Moderate** | The above, plus total-order projections as records that declare themselves projections, with the tie-break basis named | Small | Low | **Positive.** A caller who needs an order gets one and cannot mistake it for a measurement |
| **Maximal** | The above, plus each entry carrying the `TemporalCoordinate` its writer observed, so the DAG's causal structure and the temporal model's are **comparable and their disagreement reportable** | Moderate | **Medium.** Two writers may produce entries whose DAG relation is sibling and whose coordinate relation is `INCOMPARABLE` — a real disagreement that must be *reported*, not reconciled | **Highest.** It is the only option under which the register and the temporal model can be held to each other |

**Residual risk.** A DAG with no merge grows heads without bound; head count becomes a governed
population. And C-03 is untouched by all three options: **a total order over distributed events remains
chosen, not recovered.** The DAG's contribution is that the choice is *visible in the record*.

---

## 6. RESOLUTION OPTIONS FOR B-06 AS A WHOLE

### Minimal change — close the four silent-corruption and citation defects

N-13 (bare `str` refusal), N-16 (resolve the refusal relation through the registry), N-17 (verify a
clock copy), N-10 (document the inverse-pair requirement).

- **Cost.** Very small. One `isinstance` refusal, one lookup change, one copy, one docstring.
- **Risk.** **Low, with one exception.** N-13's refusal is **breaking** for any caller currently passing
  a bare `str` and relying on the explosion. That population is likely zero and must be measured rather
  than assumed.
- **Architectural impact.** None. All four are local.

### Moderate change — add the missing checks and complete the records

N-08 (a **sampled** transitivity check, labelled as sampled), N-12 (`Comparison.coincident`), R-1 (seed
the ordering vocabulary from a parameter), R-2 (declarable reflexivity).

- **Cost.** Moderate. The transitivity check is the largest piece and is ~40 lines plus a sampling
  policy.
- **Risk.** **Medium, and two hazards.** First, `Comparison.coincident` changes stored comparison record
  bytes — a C-02 record backfill. Second, and more important: **a sampled check reported without its
  sampling caveat becomes a false assurance**, which is exactly B-01's G-09 failure mode arriving in a
  new location. The check must report its sample size and shape coverage in the same record as its
  verdict.
- **Architectural impact.** Medium and positive. It moves `assert_consistent` from three verified
  properties to four, and makes the unverified remainder (reflexivity, irreflexivity) **countable**
  rather than absent.

### Maximal correctness — degrees, and the register held to the temporal model

N-11 (`Relation.properties` interpreted by the declaring strategy), plus §5 maximal.

- **Cost.** High. §5 maximal is a register design; `Relation.properties` is small but its consumers
  are not.
- **Risk.** **Medium-high.** `Relation.properties` risks becoming an uninterpreted bag — C-04 in a new
  location — mitigated by only the declaring strategy reading it, the same discipline `Field.kind` uses.
  §5 maximal's risk is that DAG-vs-coordinate disagreements are **numerous and correct**, and a report
  that fires constantly gets ignored.
- **Architectural impact.** Significant. It is the only path under which a probabilistic evidence model
  (A-23) becomes expressible, and the only one under which the register cannot silently disagree with
  the temporal model it stamps records from.

---

## 7. RESIDUAL RISK

| # | Residual | Why it survives | Severity |
|---|---|---|---|
| R-a | A total order over distributed events remains **chosen, not recovered** | C-03. Property of the world | **FUNDAMENTAL** |
| R-b | Transitivity is checkable only by **sampling**; reflexivity and irreflexivity remain unchecked entirely | No structural argument over an arbitrary registered `compare` exists | **MEDIUM.** Must be labelled, and the unchecked properties counted |
| R-c | Recurrence's revolution-component obligation cannot be enforced | The architecture cannot know a caller's position semantics | **MEDIUM.** Two records that are byte-identical and describe different instants |
| R-d | A declared `Ordering.total` remains a bare boolean naming no precondition | A-27's deeper fix, explicitly not applied | **MEDIUM.** A consumer requiring totality trusts a label that holds only within a shape class |
| R-e | A DAG register grows heads without bound absent merges | A property of concurrent append | **LOW.** Countable, hence governable |
| R-f | `assert_provider` verifies a clock's *shape*, not its *truthfulness* | A clock claiming `EARTH_FRAME` and returning arbitrary positions passes | **MEDIUM.** C-04 again: `Ω∞-D-T-02` ("corresponds to a real instant in its declared frame") ships deliberately unexecutable |

---

## 8. DETERMINATION

**No closure is declared.** Established mechanically:

| Question | Determination | Basis |
|---|---|---|
| Do privileged assumptions remain about clocks, calendars, ordering, chronology, timestamps or reference frames? | **NO in all six categories** | §2 |
| Did any hostile temporal model reveal a privileged assumption? | **No.** Four accepted cleanly, two partial, one accepted with a silent corruption — and the corruption is a type-handling defect, not a temporal premise | §1 |
| Is B-06 removable? | **PARTIALLY REMOVABLE.** Nine residuals removable, three partially, one fundamental (C-03) | §4 |
| Classification | **IMPLEMENTATION-INDUCED** for seven residuals; **ARCHITECTURE-INDUCED** for three; **ONTOLOGY-INDUCED** for one; **MATHEMATICALLY UNAVOIDABLE** for C-03 | §4 |
| Cost of delay | **Zero for N-18 (the register does not exist) and flat for the rest** | §5 |

**Three corrections to Ω∞-A.**

1. **The temporal architecture is more neutral than Ω∞-A claimed, in one specific way.** Ω∞-A did not
   record that a **reversed arrow of time** registers and operates. No code asserts an arrow direction,
   so the architecture holds no privileged chronology at all — a stronger result than "no wall clock".

2. **`assert_consistent` verifies three of the properties an ordering can have, not all of them, and
   the gap admits an inconsistent model.** A repaired cyclic ordering violating transitivity passes.
   Ω∞-A's registers do not mention transitivity. The check is writable and its verdict is
   **sampled** — which must be stated, or it becomes the same silent-expiry failure as G-09.

3. **One silent corruption exists in the tree and Ω∞-A did not find it.** A bare `str` position is
   exploded into per-character components, accepted without refusal, and **fingerprinted** — entering a
   governance record as a legitimate position. The neighbouring case (an empty position) is correctly
   refused, which makes this an omission rather than a design position.
