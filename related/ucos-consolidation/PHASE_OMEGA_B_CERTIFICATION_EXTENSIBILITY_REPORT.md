# UCOS Ω∞ — PHASE Ω∞-B, DELIVERABLE 8
## Certification Extensibility Report (B-05)

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


**AUTHORITY = NONE (DERIVED TRUTH).** Analysis and classification only. **No certification is issued
by this document**, no seal is generated, no ratchet is advanced, no closure is declared, no readiness
is claimed, and no active governance, validation or certification process is modified.

**INPUT.** Ω∞-A finding A-11, recorded as **UNKNOWN (unbuilt), designated BLOCKING if built as
designed**, with the note "Design inspection only. **Not measured — the module does not exist.**"
Treated as authoritative.

**EVIDENCE ARTIFACTS.**

| Artifact | Purpose |
|---|---|
| `probes/b02_b05_governance_certification.py` §B-05 + `b02-b05-output.txt` | locates the as-built certification coupling and attempts an eighth input at runtime |
| `probes/b07_removability_validation.py` §H2 + `b07-output.txt` | tests whether a registry-driven decision admits an eighth input with zero source edits |

```
cd /Users/bipin/Desktop/UCOS-CONSOLIDATION
.ec1-venv/bin/python 00-MASTER/UCOS-OMEGA-B-001/probes/b02_b05_governance_certification.py
.ec1-venv/bin/python 00-MASTER/UCOS-OMEGA-B-001/probes/b07_removability_validation.py
```

`b02_b05` re-executed against current repository state is **byte-identical** to its stored output.

---

## THE HEADLINE FINDING — A-11 is not unbuilt, and its measurement changes its rank

Ω∞-A could not measure A-11 because `certification.py` does not exist. **It does not need to exist.**
The certification precondition set is already present, already fixed, and already enumerated — in
`state.py`, as the `blocked_by` tuples on the two edges that reach `CERTIFIED`.

> **A-11 is reclassified from UNKNOWN (unbuilt) to MEASURED (present today, as a fixed enumeration of
> four).**

That is the single most important sentence in this report, because Ω∞-A's cost-of-delay ranking placed
A-11 at rank 2 on the grounds that the barrier could be *designed out before it exists*. Half of that
is still true — the *decision function* does not exist. The other half is not: **the barrier already
exists in the graph.**

---

## 1. FINDING B-05.1 — the current coupling points, measured

### Observation

`certification.py` present: **False**.

The de facto certification input set, as built — every edge inbound to a `CERTIFICATION`-axis position,
with its guards:

| Rule | → target | `requires_reason` | `blocked_by` |
|---|---|---|---|
| **Ω²-S-26** | **CERTIFIED** | False | **CONTRADICTED, UNATTRIBUTED, UNGOVERNED, UNKNOWN** |
| **Ω²-S-22** | **CERTIFIED** | False | **CONTRADICTED, UNATTRIBUTED, UNGOVERNED, UNKNOWN** |
| Ω²-S-29 | CONDITIONALLY_CERTIFIED | True | (none) |
| Ω²-S-23 | CONDITIONALLY_CERTIFIED | True | CONTRADICTED, UNATTRIBUTED, UNKNOWN |
| Ω²-S-30 | REJECTED | True | (none) |
| Ω²-S-27 | REJECTED | True | (none) |
| Ω²-S-24 | REJECTED | True | (none) |
| Ω²-S-34 | REJECTED | True | (none) |
| Ω²-S-32 | UNCERTIFIED | True | (none) |
| Ω²-S-33 | UNCERTIFIED | False | (none) |
| Ω²-S-31 | UNVERIFIABLE | True | (none) |
| Ω²-S-28 | UNVERIFIABLE | True | (none) |
| Ω²-S-25 | UNVERIFIABLE | True | (none) |

**The coupling point, stated precisely:**

> The certification precondition set is the frozen `blocked_by` tuple on **two frozen dataclass
> instances** (`Ω²-S-22`, `Ω²-S-26`) held in the **module-level constant** `INITIAL_TRANSITIONS` in
> `engine/omega_governance/state.py`. It is a **fixed enumeration of four preconditions**, and it
> exists **today** — before `certification.py` is written.

Three properties compound to make it a barrier rather than a configuration:

1. `Transition` is `@dataclass(frozen=True)` → `blocked_by` cannot be assigned.
2. `INITIAL_TRANSITIONS` is a module constant → it cannot be extended at runtime.
3. `TransitionGraph.register` refuses a second declaration of the same edge → a replacement edge cannot
   be substituted.

### Reproduction

`b02_b05` §B-05.1.

### Architectural cause

**ARCHITECTURE-INDUCED, and it arises from a decision that is individually correct.** Ω∞-A Deliverable
Ω-2.4 requires the certification obligations to be *structural* — "the obligations are edges, not
advice". Expressing them as `blocked_by` on the edges into `CERTIFIED` is exactly how that requirement
was discharged, and it is why `UNKNOWN never certifies` is provable from the graph at all (B-01 §4).

**The correct decision has a cost that was not recorded: making an obligation structural also makes the
obligation set closed.** A structural guarantee lives in the immutable declaration, and an immutable
declaration cannot admit a ninth obligation. B-01 and B-05 are therefore two consequences of one
design choice, pulling in opposite directions — and that tension is the substance of this finding.

---

## 2. FINDING B-05.2 — an eighth certification input, attempted at runtime

### Observation

Step 1 — widen the vocabulary. This is what Ω∞ Rule 3 promises, and it works:

```
registered a 7th axis at runtime: PROVENANCE  (axes now 7)
Rule 3 holds for the VOCABULARY: zero source edits required. ✓
```

Step 2 — make the new concern *bind* a certification decision, i.e. make it an eighth certification
input:

```
existing edge Ω²-S-22 blocked_by = ['CONTRADICTED','UNATTRIBUTED','UNGOVERNED','UNKNOWN']

ATTEMPT 1 (assign blocked_by)     : REFUSED   FrozenInstanceError: cannot assign to field 'blocked_by'
ATTEMPT 2 (register replacement)  : REFUSED   StateError: the edge UNCERTIFIED -> CERTIFIED is
                                              already declared as Ω²-S-22, and a second declaration
                                              as Ω²-S-22-v2 would make the applicable guard depend
                                              on table order
ATTEMPT 3 (does it gate a decision?): CERTIFIED PERMITTED via Ω²-S-22
```

> **The vocabulary widened — 7 axes, `UNPROVENANCED` declared — and the artifact still certifies.**
> The new governance concern is **registrable and NON-BINDING.** Making it bind requires editing
> `INITIAL_TRANSITIONS` in `state.py`.

**Ω∞-A Step 2's exit criterion — "an eighth certification input is registered at runtime, participates
in a decision, and appears in the decision's explanation, with zero source edits" — FAILS on current
code.**

### The compounding effect, measured

Registering the axis does not merely fail to bind. It also invalidates the existing population:

```
assert_total RAISED : "these artifacts hold no position on at least one registered axis, so their
                      governance record is silent about a concern the model requires them to answer"
```

So the *same* registration produces two outcomes simultaneously:

| Outcome | Which finding |
|---|---|
| Prior records become incomplete and are **reported** | C-02 / A-17 — **FUNDAMENTAL, and correctly handled** |
| The new concern **does not bind** certification | A-11 / B-05 — **REMOVABLE, and currently open** |

**This pairing is the sharpest statement of the certification problem available.** On the day a
deployment introduces a new governance concern, the architecture correctly reports every prior record as
silent about it — and simultaneously certifies new artifacts as if the concern did not exist. The
architecture is *more* rigorous about the past than about the present.

### Reproduction

`b02_b05` §B-05.2.

---

## 3. THE FALSIFICATION TEST — a registry-driven decision, written and executed

### Observation

`b07` §H2 declares a `CertificationInput` record (identifier, statement, guard, `required`) and a
`CertificationInputRegistry` whose `decide()` **quantifies over the registry and never over a tuple.**
The four preconditions currently frozen into `Ω²-S-22`'s `blocked_by` are re-expressed as four
registrations, plus one conditional quorum input:

```
inputs declared: 5
decision with 5 inputs: CERTIFIED
  satisfied=['CI-NOT-CONTRADICTED','CI-NOT-UNATTRIBUTED','CI-NOT-UNGOVERNED','CI-NOT-UNKNOWN',
             'CI-QUORUM']
```

Then the eighth input, registered at runtime after the 7th axis:

```
registered a 7th axis at runtime; axes now 7
decision with 6 inputs (the 8th just registered): REJECTED
  failed_required=['CI-NOT-UNPROVENANCED: artifact holds UNPROVENANCED']
  the 8th input APPEARS in the explanation: True
```

> **The same registration that was NON-BINDING against the shipped graph BINDS IMMEDIATELY against a
> registry-driven decision, and names itself in the explanation. Zero source edits. Ω∞-A Step 2's exit
> criterion is MET BY PROTOTYPE.**

The decision also preserves the distinction Ω-2.6 requires: a failed **required** input yields
`REJECTED`; a failed **conditional** input with all required inputs satisfied yields
`CONDITIONALLY_CERTIFIED`; all satisfied yields `CERTIFIED`. The disposition is *computed from the
registry*, not selected from a branch.

### Reproduction

`b07` §H2.

### Determination

**A-11 is IMPLEMENTATION-INDUCED and REMOVABLE.** The registry, the guard protocol and the explanation
were written over shipped types with no change to `engine/`.

**And the cost-of-delay claim is confirmed for the decision function specifically:** `certification.py`
still does not exist, so nothing was rewritten to obtain this result.

---

## 4. FUTURE FAILURE MODES

Ordered by how badly each fails.

| # | Failure mode | Mechanism | Severity |
|---|---|---|---|
| F-1 | **A new governance concern is registrable and non-binding** | Measured §2. The vocabulary widens; certification ignores it | **BLOCKING.** It is the A-11 failure, and it is live today rather than hypothetical |
| F-2 | **The decision function is built quantifying over a tuple** | If `certification.py` is written as designed — "seven inputs" — the barrier moves from the graph into the decision function, where it is *harder* to remove because a decision has branches and a graph has edges | **BLOCKING, with a deadline.** Free to avoid today |
| F-3 | **Certification grows a condition vocabulary incompatible with state transition's** | State transition uses `blocked_by` + `requires_reason`. A separately built certification module will invent its own way of saying "blocked because", and contradiction resolution a third. Ω∞-A Deliverable 7 §3.3 predicts exactly this | **CRITICAL.** This is the cost-of-delay mechanism for B-02, and B-05 is the evidence it has already begun |
| F-4 | **A conditional input cannot be expressed at all** | `blocked_by` is a membership test with no notion of required-versus-conditional. `CONDITIONALLY_CERTIFIED` is reachable only via `Ω²-S-23`, whose "condition" is an unstructured `reason` string (B-02 §1: `'x'` accepted) | **CRITICAL.** The disposition exists; the mechanism to justify it does not |
| F-5 | **The explanation cannot name what failed** | `check()` returns the first refusal as a string. A decision that "must explain itself" (Ω-2.6) cannot enumerate a shortfall population | **CRITICAL.** Measured in B-02 §4: the registry-driven version returns **seven simultaneous refusals** |
| F-6 | **An input requiring N-of-M, a window, a peer state or a quorum is inexpressible** | B-02 §2: seven of eight governance capabilities refused | **BLOCKING**, and it is B-02's finding surfacing in certification |
| F-7 | **A deployment cannot make an input conditional per domain** | One graph, one `blocked_by` per edge, no scope | **REPLACEABLE** |
| F-8 | **Certification cannot decline** | The `CERTIFICATION` axis has `UNVERIFIABLE`, and reaching it requires `requires_reason` text. A structured "could not evaluate input X" is not expressible | **REPLACEABLE**, and it interacts with B-01 §3: an invariant that cannot run should yield `UNVERIFIABLE`, and there is no mechanism to carry which input was unevaluable |

**F-2 is the only one with a deadline, and it is the reason this report exists before the module does.**

---

## 5. MIGRATION COMPLEXITY

Assessed against the three states the module can be in.

### State A — today: `certification.py` absent, coupling in the graph

| Aspect | Assessment |
|---|---|
| **Migration cost** | **Near zero for the decision function.** It does not exist; writing it registry-driven costs the same as writing it enumerated |
| **What must still change** | The four `blocked_by` entries on `Ω²-S-22`/`Ω²-S-26` become four **registered inputs**. `Transition.blocked_by` is **retained** as the declaration from which the standard state-exclusion guard is constructed |
| **Record impact** | **None.** `Transition.as_record()` is unchanged; `blocked_by` still serialises. The guard is derived from the field, not a replacement for it |
| **B-01 interaction — and it matters** | The structural proof reads `blocked_by` on edges into `CERTIFIED`. If the four preconditions moved *out* of `blocked_by` into a registry only, **the structural proof would lose its input** and `UNKNOWN never certifies` would no longer be provable from the graph. **The correct migration keeps `blocked_by` as the declaration and adds the registry for inputs the graph cannot express.** Anything else trades B-05 for B-01 |
| **Complexity** | **LOW** |

### State B — `certification.py` built as designed (seven fixed inputs)

| Aspect | Assessment |
|---|---|
| **Migration cost** | **Rewrite of the decision function.** A decision quantifying over a tuple has the tuple's length in its control flow — disposition branches, explanation construction, and any per-input special case |
| **Record impact** | The decision record's shape depends on the input set. Adding an eighth input changes the explanation's shape, so **stored decision records become non-comparable with new ones** |
| **Complexity** | **MEDIUM-HIGH**, and it is Ω∞-A's "cost of delay: a rewrite of the decision function" — confirmed |

### State C — `certification.py` built and consumed by gates, ratchets or CI

| Aspect | Assessment |
|---|---|
| **Migration cost** | **Rewrite plus every consumer.** A certification disposition that acquires a new input changes which artifacts certify, which changes a ratchet's population |
| **Record impact** | Every consumer of a decision record; every ratchet whose numerator or denominator depends on a disposition |
| **Complexity** | **HIGH.** Ω-1's ratchets are the precedent: `certification_integrity/contract.py:130` already validates dispositions against a closed membership test (Ω∞-A X-13, 8 sites) |
| **Note** | **This state is currently forbidden.** No Phase 2 code is wired into `verify.sh`, any gate stage, any seal or any ratchet — and this document does not change that |

---

## 6. CERTIFICATION EXTENSIBILITY REGISTER

| ID | Finding | Observation | Architectural cause | Classification | Verdict |
|---|---|---|---|---|---|
| K-01 | The certification input set is a **fixed enumeration of four**, present today | frozen `blocked_by` on `Ω²-S-22`, `Ω²-S-26` in `INITIAL_TRANSITIONS` | ARCHITECTURE-INDUCED (a correct structural decision with an unrecorded cost) | **REMOVABLE.** A-11 **reclassified from UNKNOWN to MEASURED** |
| K-02 | An eighth input cannot be added at runtime — three ways | `FrozenInstanceError`; duplicate-edge `StateError`; and the concern is simply ignored | ARCHITECTURE-INDUCED | **REMOVABLE** — measured binding immediately when the decision quantifies over a registry |
| K-03 | A new concern is **registrable and non-binding** | 7 axes registered, `UNPROVENANCED` declared, artifact still CERTIFIED | ARCHITECTURE-INDUCED | **REMOVABLE** |
| K-04 | required-vs-conditional is inexpressible | `blocked_by` is a membership test | ARCHITECTURE-INDUCED | **REMOVABLE** — measured: `required=False` yields CONDITIONALLY_CERTIFIED |
| K-05 | The explanation cannot enumerate a shortfall | `check()` returns the first refusal | IMPLEMENTATION-INDUCED | **REMOVABLE** — measured: 7 simultaneous refusals |
| K-06 | `CONDITIONALLY_CERTIFIED`'s condition is an unstructured string | `Ω²-S-23` `requires_reason=True`; `'x'` accepted | IMPLEMENTATION-INDUCED | **REMOVABLE** by the B-02 justification domain |
| K-07 | `certification.py` and 7 other documented modules are **absent** while the package docstring presents them | `__init__.py:28-40` vs `ls` | GOVERNANCE-INDUCED | **REMOVABLE** — see Proof Tractability Report §3 |
| K-08 | Moving preconditions out of `blocked_by` would **break the structural proof** | B-01 §4 reads `blocked_by` on inbound-to-`CERTIFIED` edges | ARCHITECTURE-INDUCED | **CONSTRAINT ON THE RESOLUTION, not a defect.** **New in Ω∞-B** |
| K-09 | Certification cannot record **which** input was unevaluable | `UNVERIFIABLE` reached by free text only | IMPLEMENTATION-INDUCED | **REMOVABLE** |

---

## 7. RESOLUTION OPTIONS

### Minimal change — do not build the barrier

Write `certification.py` with the decision quantifying over a `CertificationInputRegistry`. Retain
`Transition.blocked_by` as the declaration from which the four standard state-exclusion inputs are
constructed (K-08).

- **Cost.** **Zero relative to building it as designed.** The registry version is not more work than
  the tuple version; it is different work of the same size. Measured working in `b07` §H2.
- **Risk.** **Low, with one hazard.** The hazard is item K-08: a naive migration that *replaces*
  `blocked_by` rather than *reading* it silently destroys the structural proof's input. The
  resolution must be additive.
- **Architectural impact.** **Low and positive.** No shipped type changes. It makes A-11 impossible
  rather than deferred, which is Ω∞-A Deliverable 7 §3.3's claim.

### Moderate change — inputs are guards

Each `CertificationInput` carries a `Guard` (B-02 §6). The decision's explanation is a **record**
naming every input considered, every one satisfied, and every shortfall with its reason.

- **Cost.** Moderate, and **shared with B-02** — the guard protocol serves both, so the marginal cost
  here is the input record and the explanation record.
- **Risk.** **Medium.** The explanation becomes a structured record rather than a string, so any
  consumer expecting a message must change. Since no consumer exists yet, the risk is confined to the
  design.
- **Architectural impact.** **High and positive.** It makes certification, state transition and
  contradiction resolution one mechanism with three registries — the argument for guards being the core
  rather than a feature. It also closes F-3 before it can occur.

### Maximal correctness — the input set is itself governed

The above, plus:

1. every `CertificationInput` declares `required`/`conditional` **and its own authority**;
2. the input **set** is a vocabulary with a digest (B-03 §1), so two deployments can detect that they
   certify against different obligations;
3. a certification decision record cites the **digest of the input set** it was decided under, so a
   past decision remains interpretable after the obligations widen;
4. an input whose guard is unexecutable yields `UNVERIFIABLE` **naming the input** (K-09).

- **Cost.** High. Item 3 makes a decision record depend on a vocabulary digest, and item 2 depends on
  the whole of B-03's minimal option.
- **Risk.** **Medium-high, and item 3 carries a subtle one.** Citing the input-set digest is the right
  way to keep past decisions interpretable — and it means a decision record's meaning depends on
  retaining the vocabulary it cites. A vocabulary that is discarded leaves an uninterpretable decision.
  So item 3 implies vocabulary *retention*, which is a storage obligation (G-05) that does not exist.
- **Architectural impact.** **Highest available, and it is the point at which certification becomes
  auditable across time.** Without item 3, widening the obligation set silently changes what
  "CERTIFIED" meant, and no record says so. With it, C-02's record-backfill honesty extends from
  governance vectors to certification decisions.

---

## 8. RESIDUAL RISK

| # | Residual | Why it survives | Severity |
|---|---|---|---|
| R-1 | An input can be registered whose guard always permits | C-04. Meaning is not mechanisable | **MEDIUM.** Countable: an input that never refuses is a measurable population |
| R-2 | The structural proof depends on `blocked_by`, so the four state-exclusion obligations must stay **declared on the edge** even after inputs become a registry | K-08 | **MEDIUM as a design constraint.** It must be stated in the module, or a later refactor will remove it |
| R-3 | Past decision records remain interpretable only if the input-set vocabulary is retained | §7 maximal item 3, and there is no storage provider (G-05) | **MEDIUM.** A dependency, not a defect |
| R-4 | The seven designed inputs have never been enumerated in code, so "the design named seven" cannot be checked | `certification.py` absent | **LOW, and it is a documentation gap.** The four in `blocked_by` are the only measurable ones |
| R-5 | A deployment can widen the axis set and never register the corresponding input, leaving the concern registrable and non-binding **even after the registry exists** | Nothing links axis registration to input registration, and nothing should — not every concern is a certification precondition | **MEDIUM, and it is the honest residual.** The correct mitigation is to **report** axes that no certification input reads, not to bind them automatically |

**R-5 is the residual worth dwelling on.** It is the same shape as C-02: the architecture cannot know
whether a newly registered concern *ought* to gate certification, and guessing either way is wrong.
Auto-binding would fabricate an obligation; ignoring it silently is the current failure. **Reporting the
population of axes that no certification input reads** is the only response that neither invents an
obligation nor hides its absence — and it is precisely the discipline `assert_total` already applies to
governance vectors and `unexecutable_invariants` to invariants.

---

## 9. DETERMINATION

**No closure is declared and no certification is issued.** Established mechanically:

| Question | Determination | Basis |
|---|---|---|
| Is B-05 removable? | **REMOVABLE** | §3: registry-driven decision written and executed; 8th input bound at runtime with zero source edits |
| Classification | **ARCHITECTURE-INDUCED** as built (K-01, a correct structural decision with an unrecorded cost); **IMPLEMENTATION-INDUCED** for the resolution | §1, §3 |
| Are certification inputs registry-driven today? | **No.** A fixed enumeration of four, present in `state.py` | §1 |
| Must they be? | **Yes**, on the evidence of §2: otherwise a new governance concern is registrable and non-binding | §2 |
| Is any part mathematically unavoidable? | **No.** R-5 is governance-induced and its honest form is a report | §8 |
| Cost of delay | **Zero today for the decision function; a rewrite once built; a rewrite plus consumers once wired.** Ω∞-A rank 2 is confirmed for the decision function and **understated for the graph**, where the enumeration already exists | §5 |

**Three corrections to Ω∞-A.**

1. **A-11 was measurable and is now measured.** It is not UNKNOWN. The fixed enumeration of four
   certification preconditions exists today in `INITIAL_TRANSITIONS`, and the three attempts to extend
   it at runtime were each refused for a different reason.

2. **A-11 and A-10 are one item, not two.** Ω∞-A Deliverable 7 §3.3 already argued that guards "make
   A-11 impossible"; B-05 supplies the evidence, since the eighth input was bound by a *guard* in a
   registry. Sequencing them separately would build a certification input registry whose inputs cannot
   express N-of-M, a window or a peer state — F-6.

3. **The resolution has a constraint Ω∞-A did not record (K-08).** The four preconditions must remain
   *declared on the edge* even after the input registry exists, because the structural proof of
   `UNKNOWN never certifies` reads `blocked_by`. B-01 and B-05 pull in opposite directions on the same
   field, and a resolution that ignores this trades one blocker for the other.
