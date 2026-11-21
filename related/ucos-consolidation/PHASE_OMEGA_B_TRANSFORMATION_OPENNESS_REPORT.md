# UCOS Ω∞ — PHASE Ω∞-B, DELIVERABLE 7
## Transformation Openness Report (B-04)

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

**INPUT.** Ω∞-A findings A-21 (BLOCKING), A-22 (EXPANDABLE), G-03, G-04, X-03, X-04, C-01
(FUNDAMENTAL, with one open action). Treated as authoritative.

**EVIDENCE ARTIFACTS.**

| Artifact | Purpose |
|---|---|
| `probes/b03_b04_semantic_transformation.py` + `b03-b04-output.txt` | measures the four arity assumptions and attempts n-ary declaration three ways |
| `probes/b07_removability_validation.py` §H4 + `b07-output.txt` | tests whether a hypergraph representation preserves conjunction and admits competing authorities |

```
cd /Users/bipin/Desktop/UCOS-CONSOLIDATION
.ec1-venv/bin/python 00-MASTER/UCOS-OMEGA-B-001/probes/b03_b04_semantic_transformation.py
.ec1-venv/bin/python 00-MASTER/UCOS-OMEGA-B-001/probes/b07_removability_validation.py
```

`b03_b04` re-executed against current repository state is **byte-identical** to its stored output.

---

## 1. THE FOUR ASSUMPTIONS THE DIRECTIVE ASKS ABOUT — all four present, all four structural

### Observation

```
Transformation fields : identifier, source, target, authority, description, invertible, lossy
  source: str  (exactly ONE)      target: str  (exactly ONE)
registry edge index   : dict[tuple[str, str], str]   -> ONE edge per ordered pair
register signature    : (transformation: Transformation,
                         computation: Callable[[Value], Value] | None = None) -> Transformation
computation type      : Callable[[Value], Value]     -> ONE value in, ONE value out
apply signature       : (value: Value, target: str) -> TransformationOutcome
path signature        : (source: str, target: str)  -> tuple[Transformation, ...]
```

| Directive's question | Present? | Where it is enforced |
|---|---|---|
| **fixed inputs** | **YES** | `Transformation.source` is a single `str`; `Callable` takes one `Value` |
| **fixed outputs** | **YES** | `Transformation.target` is a single `str`; `Callable` returns one `Value` |
| **fixed cardinality** | **YES — 1:1** | enforced by the `dict[tuple[str,str], str]` edge index |
| **fixed topology** | **YES — a directed graph searched by BFS** | `path()` is BFS over ordered pairs; **a hyperedge has no representation** |

All four are structural — they are properties of the type and of the index, not of a policy, a
validator or a default. That matters for classification: they cannot be worked around by configuration.

### Reproduction

`b03_b04` §B-04.1.

---

## 2. N-ARY DECLARATION, ATTEMPTED THREE WAYS

### Observation

**Attempt 1 — declare a 3-source transformation directly.**

```
REFUSED   AttributeError: 'tuple' object has no attribute 'strip'
```

Reproduced independently in `b07` §H4. The refusal is *incidental* — a `str` method failing on a
`tuple` — rather than a refusal that names the limitation. **That is itself a finding:** the
architecture refuses n-ary transformations with an `AttributeError`, not with a governance message, so
a caller learns that the code broke rather than that the model does not admit the concept. Every other
refusal in this package names its reason and cites a rule.

**Attempt 2 — the documented workaround: invent a composite intermediate domain.**

```
ACCEPTED — but SPACE_TIME_FRAME must now be DECLARED as a reference domain with its own schema.
That is a SCHEMA MODIFICATION, i.e. the workaround IS the barrier.
And the composite loses the fact that it has three parts: 'SPACE_TIME_FRAME'
```

Ω∞-A X-03 predicted this ("the workaround *is* the barrier"). Confirmed, and with an addition Ω∞-A did
not state: **the composite is opaque.** `SPACE_TIME_FRAME` is a single name; nothing records that it
decomposes into three domains, so no consumer can discover the arity that was flattened away.

**Attempt 3 — fan-in as multiple 1:1 edges. Is conjunction distinguishable from alternative?**

```
two edges now target VELOCITY: ['Ω∞-PROBE-A', 'Ω∞-PROBE-B', 'Ω∞-PROBE-VEL-2']
But nothing records that BOTH are required. path('SPACE','VELOCITY') returns ['Ω∞-PROBE-A']
— a COMPLETE route, so apply() would convert from SPACE alone and report success.
Conjunction is indistinguishable from ALTERNATIVE.
```

**This is the most serious consequence in B-04, and it is worse than inexpressibility.** An
inexpressible concept produces a refusal. Here the model produces a *successful conversion from
insufficient inputs*: `path()` reports a complete route from `SPACE` alone, and `apply()` would
produce a `VELOCITY` value having never consulted time or frame.

### Reproduction

`b03_b04` §B-04.2; `b07` §H4.

---

## 3. FINDING B-04.3 — exactly one authority may relate any two domains

**New in Ω∞-B. Not in the Ω∞-A registers.**

### Observation

```
declared MARS_SOL -> SI_SECOND on authority IAU
  a SECOND authority for the same pair: REFUSED
    "MARS_SOL -> SI_SECOND is already declared as 'Ω∞-PROBE-IAU'; a second declaration as
     'Ω∞-PROBE-NASA' would make the applicable authority and loss statement depend on
     registration order"
```

The edge index is keyed by `(source, target)`, so **exactly one authority may relate any two domains.**

### Architectural cause

**ARCHITECTURE-INDUCED, and the refusal is individually correct.** The message is right: two
declarations for one key *would* make the applicable authority depend on registration order, and
order-dependent authority is worse than no second authority. The defect is not the refusal; it is the
**key**. `(source, target)` cannot hold two authorities, so the only available response to a second
one is to refuse it.

### Consequence if unresolved

Two ephemeris publishers, two precisions, or a superseded factor alongside its replacement are all
inexpressible. **A registry built to remove "a factor nobody answers for" cannot hold "a factor two
bodies answer for differently" — which is the normal condition in physical metrology.** Every real
unit-conversion authority (BIPM, IAU, NIST, NASA SPICE) publishes values that others revise; the model
admits exactly one of them at a time.

This directly affects Ω∞ Rule 8's "previously unknown science" case: a new civilisation's ephemeris
cannot coexist with a terrestrial one for the same pair.

### Resolution

Widen the key to `(frozenset(sources), target, authority)`. Measured in `b07` §H4:

```
edges into VELOCITY: ['Ω∞-B-VEL-1', 'Ω∞-B-VEL-2', 'Ω∞-B-VEL-ALT']
TWO authorities (IAU, NASA) for the SAME source set: ACCEPTED
```

**And the original refusal's concern is preserved**, because the authority is part of the key: nothing
is order-dependent, since resolving a transformation now requires naming the authority (or accepting
that the population of candidates is reported rather than silently reduced to one).

---

## 4. THE FALSIFICATION TEST — hypergraph representation, written and executed

### Observation

A `Hyperedge` with `sources: tuple[str, ...] -> target`, and a registry keyed on the source **set**:

```
available=['SPACE']
  satisfiable : []
  shortfall   : {'transformation': 'Ω∞-B-VEL-1', 'authority': 'IAU',
                 'missing': ['FRAME', 'TIME']}
  shortfall   : {'transformation': 'Ω∞-B-VEL-2', 'authority': 'NASA',
                 'missing': ['FRAME', 'TIME']}
  shortfall   : {'transformation': 'Ω∞-B-VEL-ALT', 'authority': 'ESO',
                 'missing': ['DOPPLER_SHIFT']}

available=['FRAME', 'SPACE', 'TIME']
  satisfiable : ['Ω∞-B-VEL-1', 'Ω∞-B-VEL-2']
```

Three properties the shipped model cannot produce, all measured:

1. **`SPACE` alone is UNSATISFIABLE**, where the shipped fan-in reported a complete route.
2. **The shortfall is named per transformation** — which domains are missing, and which authority is
   waiting for them.
3. **Two authorities for one source set coexist**, and the alternative route (`DOPPLER_SHIFT →
   VELOCITY`, authority ESO) is correctly distinguished from the conjunctive ones.

> **Conjunction is distinguishable from alternative. Ω∞-A Step 9's exit criterion — "position AND time
> AND frame → velocity declared as one transformation, with one authority and one loss statement" — is
> MET BY PROTOTYPE.**

Zero edits to `engine/`.

### Reproduction

`b07` §H4.

### Architectural cause of the original limitation

**ARCHITECTURE-INDUCED, and removable by a type widening.** `source: str` and
`dict[tuple[str,str], str]` are the whole cause. Ω∞-A A-21 classified this as BLOCKING and structural,
which is confirmed; what B-04 adds is that the widening is **local to two declarations and one index**,
and that the consequence of *not* doing it is a false success rather than a refusal.

---

## 5. FINDING B-04.4 — C-01's open action is available and untaken

### Observation

Ω∞-A C-01 (only encodable things can be governed) carries one open action: make the proxy relationship
for a non-encodable artifact a **declared transformation** with an authority and `lossy=True`, so the
substitution is a recorded governance fact rather than an assumption.

Attempted:

```
declared: {'transformation': 'Ω∞-PROBE-PROXY', 'source': 'PHYSICAL_SPECIMEN',
           'target': 'ARTIFACT', 'authority': 'PROBE-LAB',
           'description': 'a specimen is governed by proxy through its catalogue record',
           'invertible': False, 'lossy': True}
computable here: False
```

**The proxy relationship IS declarable** as a lossy, authority-bearing, non-computable transformation.
**Ω∞-A C-01's open action is therefore MECHANICALLY AVAILABLE and simply UNTAKEN** — no shipped
declaration uses it.

### Determination — the falsification criterion Ω∞-A ranked most likely does not fire

Ω∞-A Deliverable 7 §7 criterion 3: *"A reference domain whose values cannot be given a fingerprint
under any registered encoding — which would show the encodability boundary is not merely fundamental
but mis-placed."* Ω∞-A ranked this **most likely to actually occur.**

> **Criterion 3 does NOT fire.** No sixth mechanism is needed for physical reference. C-01 is correctly
> placed as fundamental, and the architectural core survives its own most-likely falsification test.

### Residual, and it is real

`lossy: bool` states **that** fidelity is lost, never **how much**. Two proxies of very different
quality are indistinguishable: a calibrated measurement record standing in for a specimen and a
photograph of its label both declare `lossy=True`.

---

## 6. FINDING B-04.5 — a relation's fourth property, and a loss in the comparison record

### Observation (from B-06, recorded here because it is a relation-arity finding)

`Relation` has exactly three semantic booleans plus an inverse:

```
Relation fields: name, description, decided, ordered, coincident, inverse
OrderingStrategy.compare returns: str   (a relation NAME, no payload)
Comparison fields: relation, rule, reason, left, right, decided, ordered
```

A probabilistic ordering was attempted:

```
bucketed relation PROBE_BEFORE_P90: ACCEPTED (degree encoded in the NAME)
stochastic strategy: assert_consistent PASSED  <- unexpected
```

Bucketing works and does not scale — a confidence must be encoded in the relation *name* or in
free-text `reason`. **Ω∞-A A-22/G-04 confirmed: the `QuantumOrdering` pass was a FIT, not generality.**

**And a loss Ω∞-A did not record:** `Comparison` carries `decided` and `ordered` but **not
`coincident`**. So a consumer of a comparison *record* must string-match the relation name to tell
coincidence from concurrency — which is exactly the name-based reasoning `assert_consistent` exists to
avoid. The record is lossier than the relation it cites.

### Architectural cause

**ARCHITECTURE-INDUCED, narrow.** Three booleans is a closed property set on a value type. `Comparison`
omitting `coincident` is an ordinary omission.

### Resolution

`Relation.properties: Mapping[str, object]`, interpreted by the declaring strategy; and
`Comparison.coincident` added alongside the two flags already carried.

- **Cost.** Small for both.
- **Risk.** Low. `Comparison.coincident` is additive to a record and therefore a byte change to stored
  comparison records — a C-02 backfill, not a code migration. `Relation.properties` risks becoming an
  uninterpreted bag, which is C-04 in a new location; mitigation is that only the **declaring strategy**
  interprets it, which is the same discipline `Field.kind` already uses.
- **Architectural impact.** Low. It generalises one value type and completes one record.

---

## 7. TRANSFORMATION OPENNESS REGISTER

| ID | Finding | Observation | Architectural cause | Classification | Verdict |
|---|---|---|---|---|---|
| T-01 | Fixed inputs | `source: str`, one `Value` in | ARCHITECTURE-INDUCED | **REMOVABLE** — `sources: tuple[str, ...]`, measured |
| T-02 | Fixed outputs | `target: str`, one `Value` out | ARCHITECTURE-INDUCED | **REMOVABLE** — same widening |
| T-03 | Fixed cardinality 1:1 | `dict[tuple[str,str], str]` | ARCHITECTURE-INDUCED | **REMOVABLE** — key on a source set, measured |
| T-04 | Fixed topology (directed graph, BFS) | `path()` is pairwise BFS | ARCHITECTURE-INDUCED | **REMOVABLE** — satisfiability over available domains, measured |
| T-05 | n-ary declaration refused by `AttributeError` | `'tuple' has no attribute 'strip'` | IMPLEMENTATION-INDUCED | **REMOVABLE.** **New in Ω∞-B.** Every other refusal names its reason; this one leaks a type error |
| T-06 | The composite workaround is a schema modification, and is opaque | `SPACE_TIME_FRAME` must be declared; loses that it has 3 parts | ARCHITECTURE-INDUCED | **REMOVABLE** by T-01 |
| T-07 | **Conjunction indistinguishable from alternative** | `path('SPACE','VELOCITY')` returns a COMPLETE route; `apply()` would succeed from insufficient inputs | ARCHITECTURE-INDUCED | **REMOVABLE** — measured UNSATISFIABLE with a named shortfall. **Highest-severity row here** |
| T-08 | One authority per domain pair | second authority REFUSED | ARCHITECTURE-INDUCED | **REMOVABLE** — key includes authority, measured. **New in Ω∞-B** |
| T-09 | Relation has exactly 3 semantic properties | no `properties` mapping; degree lives in the name | ARCHITECTURE-INDUCED | **REMOVABLE** — `properties` mapping |
| T-10 | `Comparison` omits `coincident` | consumer must string-match the relation name | IMPLEMENTATION-INDUCED | **REMOVABLE.** **New in Ω∞-B** |
| T-11 | Proxy for a non-encodable artifact | declarable as lossy, non-computable, authority-bearing | — | **AVAILABLE AND UNTAKEN.** Ω∞-A criterion 3 does **not** fire |
| T-12 | `lossy: bool` states that, never how much | two proxies of different quality indistinguishable | **ONTOLOGY-INDUCED** | **PARTIALLY REMOVABLE.** A declared fidelity is a claim nobody can check — C-04 again |

**Ten removable. One available and untaken. One partially removable.**

---

## 8. RESOLUTION OPTIONS FOR B-04 AS A WHOLE

### Minimal change

`sources: tuple[str, ...]`; edge index keyed `(frozenset(sources), target, authority)`; `path()`
replaced by satisfiability over the set of available domains, reporting a **shortfall population** when
unsatisfiable. Refuse a non-`str` source with a **governance message** rather than an `AttributeError`.

- **Cost.** Small-to-moderate. Two field types, one index, one search function, one refusal message.
- **Risk.** **Medium, and the risk is a record-shape change.** `Transformation.as_record()` currently
  emits `source` as a string; a tuple changes the bytes of every stored transformation record. This is
  a C-02 record backfill: a single-source transformation is representable as a one-element tuple, so
  the *concept* migrates cleanly, but stored records do not. The honest response is to report the
  population of single-source records rather than silently rewriting them. A second risk: `path()`
  becoming set-based means a caller asking "how do I get to VELOCITY" may now receive **several**
  satisfiable routes from different authorities and must choose — the model can no longer pretend there
  is one answer. That is correct and it is a caller-visible change.
- **Architectural impact.** **Medium and positive.** It closes T-01 through T-08 in one widening, and
  it converts a false success (T-07) into a named shortfall.

### Moderate change

The above, plus `Relation.properties` (T-09), `Comparison.coincident` (T-10), and a **declared proxy
transformation** for every non-encodable artifact the deployment governs (T-11).

- **Cost.** Moderate.
- **Risk.** Low-to-medium. `Comparison.coincident` is a record byte change. `Relation.properties`
  risks an uninterpreted bag; the mitigation is that only the declaring strategy reads it.
- **Architectural impact.** Medium. T-11 is the one item that turns a *fundamental constraint's*
  mitigation from a recommendation into a recorded governance fact.

### Maximal correctness

The above, plus a **declared fidelity** on lossy transformations: not a boolean but a value in a
declared domain with its own invariants, so two proxies of different quality are distinguishable.

- **Cost.** High, and it is partly a domain-modelling problem rather than a code problem: fidelity of
  *what*, measured *how*, on *whose* authority.
- **Risk.** **High, and the risk is fabricated precision.** A declared fidelity nobody can check is C-04
  in the place it does most damage — a governance record asserting a quantified fidelity that is
  actually a guess. The honest form is to let fidelity be a value with **executable invariants where
  possible and a counted unexecutable population where not**, exactly as `Invariant` already does.
- **Architectural impact.** Significant. It makes proxy quality a governed measurement rather than a
  flag, which is the difference between recording *that* a substitution happened and recording
  *whether it was adequate*.

---

## 9. RESIDUAL RISK

| # | Residual | Why it survives | Severity |
|---|---|---|---|
| R-1 | After T-01–T-04, a caller may receive several satisfiable routes from different authorities and must choose. The model cannot choose for them | Two authorities disagreeing is the real condition (T-08); picking one would reinstate the order-dependence the original refusal correctly avoided | **MEDIUM, and it is the correct residual.** It must be reported as a population, not resolved silently |
| R-2 | A hyperedge's `computation` is `Callable[[tuple[Value, ...]], Value]`, and nothing verifies that the callable actually reads all declared sources | A callable's behaviour is not inspectable | **MEDIUM.** A transformation could declare three sources and use one — conjunction restored in the declaration and violated in the computation |
| R-3 | `lossy` remains unquantified under minimal and moderate | §8 maximal is a domain-modelling problem | **MEDIUM.** C-01's residual exposure, now named |
| R-4 | Record backfill for `source` → `sources` and for `Comparison.coincident` | C-02: widening the model makes prior records incomplete | **LOW, and unavoidable.** Report the population; do not auto-convert |
| R-5 | The composite-domain workaround remains **legal** after the widening. A deployment can still flatten three domains into one opaque name | Nothing forbids declaring a composite domain, and nothing should | **LOW.** Detectable only by noticing an unexplained domain; not mechanisable |

---

## 10. DETERMINATION

**No closure is declared.** Established mechanically:

| Question | Determination | Basis |
|---|---|---|
| Is B-04 removable? | **REMOVABLE** | §4: hypergraph written and executed over shipped types; conjunction distinguishable; competing authorities admitted |
| Classification | **ARCHITECTURE-INDUCED** (removable by type widening), with T-05 and T-10 IMPLEMENTATION-INDUCED and T-12 ONTOLOGY-INDUCED | §1, §3, §5, §6 |
| Do all four named assumptions hold? | **Yes — fixed inputs, outputs, cardinality and topology are all present and all structural** | §1 |
| Is any part mathematically unavoidable? | **No.** T-12's residue is ontology-induced, not mathematical | §5, §7 |
| Does Ω∞-A falsification criterion 3 fire? | **No.** The proxy relationship is declarable; no sixth mechanism is needed | §5 |
| Cost of delay | **Moderate and flat**, per Ω∞-A rank 9 — **with one exception.** T-07 is a *live* correctness defect today, not a future barrier | §2, §7 |

**Two corrections to Ω∞-A.**

1. **A-21 is not only an expressiveness gap; it is a correctness defect.** Ω∞-A described binary
   transformations as blocking "genuinely multi-domain science". The measurement is sharper:
   `path('SPACE','VELOCITY')` returns a **complete route** when two of three required inputs are
   absent, so `apply()` would report success on insufficient inputs. The consequence of the gap is a
   **wrong answer**, not a missing capability, and that raises its priority above Ω∞-A's rank 9.

2. **T-08 (one authority per domain pair) is absent from every Ω∞-A register**, and it defeats the
   normal condition in physical metrology. It resolves in the same widening as A-21, so it costs
   nothing extra — but it would have been missed had the key not been examined.
