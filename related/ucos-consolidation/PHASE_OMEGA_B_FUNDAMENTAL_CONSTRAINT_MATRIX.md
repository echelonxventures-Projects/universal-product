# UCOS Ω∞ — PHASE Ω∞-B, DELIVERABLE 3
## Fundamental Constraint Matrix

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


**AUTHORITY = NONE (DERIVED TRUTH).** No certification, no seal, no ratchet advancement, no closure
declaration, no readiness claim. No active governance, validation or certification process is modified.

**WHAT THIS DOCUMENT IS FOR.** The Blocker Resolution Matrix lists what can be removed. This one lists
what cannot, and — because Ω∞-B is a *closure evidence* phase rather than a discovery phase — it does
something Ω∞-A could not: **it tests each claimed fundamental constraint against an attempt to falsify
it.**

**THE STANDARD APPLIED, inherited from Ω∞-A Deliverable 8 and unchanged.** A constraint is FUNDAMENTAL
only if removing it would require abandoning the idea of a governance record. Everything else is work.

**WHY TESTING MATTERS MORE HERE THAN ANYWHERE ELSE IN Ω∞-B.** A blocker wrongly classified as removable
costs effort. **A limitation wrongly classified as fundamental costs the capability permanently**, because
nobody attempts what the architecture has declared impossible. Ω∞-A understood this and wrote five
falsification criteria for its own core proposal. Ω∞-B tested three of them.

| Ω∞-A falsification criterion | Ω∞-A's predicted likelihood | Ω∞-B outcome |
|---|---|---|
| **3.** A reference domain whose values cannot be fingerprinted under any encoding — showing C-01 is *mis-placed* rather than merely fundamental | **Ranked MOST LIKELY to occur** | **DID NOT FIRE.** The proxy relationship for a non-encodable artifact **is declarable** as a lossy, authority-bearing, non-computable `Transformation`. No sixth mechanism is needed for physical reference |
| **1.** A governance rule not expressible as a composition of guards | Ranked second | **DID NOT FIRE.** All eight capabilities plus cross-artifact conditionality were written as guards over shipped types |
| **5.** Two deployments agreeing on every vocabulary digest and still disagreeing about a record's validity | Not ranked | **FIRED, exactly as written.** Two registries with byte-identical digests attached different meanings to one field and both validated the record |
| **2.** A governance concept needing a sixth mechanism | Not tested | untested |
| **4.** A relation between values that is neither a `Relation` nor a `Transformation` | Not tested | untested |

**An architecture whose stated falsification criteria fire where predicted and stay silent where
predicted is behaving as a falsifiable artifact should.** That is the strongest single result of Ω∞-B,
and it belongs in this document rather than the blocker matrix, because it is a statement about the
*constraints* rather than about the work.

**EVIDENCE BASE.** `00-MASTER/UCOS-OMEGA-B-001/probes/` — five probes, all re-executed against current
repository state.

---

## 1. SUMMARY

| Constraint | Ω∞-A verdict | Ω∞-B test | Ω∞-B verdict |
|---|---|---|---|
| **C-01** Only encodable things can be governed | FUNDAMENTAL, one open action | **Falsification criterion 3 attempted** | **CONFIRMED FUNDAMENTAL.** Mitigation now measured **available and untaken**. New residual: fidelity unquantified |
| **C-02** Widening the vocabulary invalidates prior records | FUNDAMENTAL, directive amendment recommended | Compounding effect measured | **CONFIRMED FUNDAMENTAL, and its scope is wider than recorded** |
| **C-03** Distributed order is chosen, not recovered | FUNDAMENTAL, one design decision with a deadline | DAG prototype executed | **CONFIRMED FUNDAMENTAL. The A-24 *exposure* is removable at zero cost; the constraint is not** |
| **C-04** Meaning cannot be fully mechanised | FUNDAMENTAL, ratchet recommended | **Falsification criterion 5 attempted** | **CONFIRMED FUNDAMENTAL, and its reach is broader than recorded — it now surfaces in five places** |
| **C-05** This implementation is Python | FUNDAMENTAL (residue) + CRITICAL fixable emitter | Module presence measured | **CONFIRMED FUNDAMENTAL (residue). The fixable part is larger than recorded: 9 of 11 documented modules are absent, not 1** |

**Five constraints. All five confirmed. Not one was found to be mis-placed.** And two are now measured to
be *broader* than Ω∞-A recorded — which is the opposite of the failure mode this document exists to
catch, and worth stating plainly rather than presenting as a clean confirmation.

---

## 2. THE MATRIX

### C-01 — Only what can be reduced to bytes can be governed

| Field | Content |
|---|---|
| **Statement** | A governance record's integrity rests on a fingerprint; a fingerprint requires an encoding; an encoding requires a finite byte string. Anything not so reducible — a physical specimen, a live process, a continuous field, an unbounded stream, an unrepeatable observation — **cannot itself enter a governance register.** It can only be *represented* by something that can |
| **Why it cannot be removed** | Not an implementation limit. Tamper evidence **is** "the bytes did not change"; without bytes there is nothing for tamper evidence to be about. An architecture governing non-encodable things would be governing *claims* about them, which is what this constraint says |
| **Classification** | **MATHEMATICALLY UNAVOIDABLE** (given that integrity is defined by content identity) |
| **Observation** | `reference/domain.assert_encodable` **refuses** rather than stringifying, naming the component and its type and telling the caller to register a codec. A `repr()` fallback would have produced bytes depending on a Python memory address — governance records differing between runs for a reason no reader could find. **The refusal is the whole mitigation and it is the correct one** |
| **Ω∞-B test — falsification criterion 3** | Attempted: declare the proxy relationship for a non-encodable artifact as a `Transformation`. Result: **ACCEPTED** — `PHYSICAL_SPECIMEN → ARTIFACT`, authority `PROBE-LAB`, `invertible=False`, `lossy=True`, `computable here: False` |
| **Reproduction** | `b03_b04` §B-04.4 |
| **Determination** | **Criterion 3 — the one Ω∞-A ranked most likely to fire — does NOT fire.** C-01 is correctly placed as fundamental rather than mis-placed, and the architectural core survives its own most-likely falsification test. **C-01's open action is MECHANICALLY AVAILABLE and simply UNTAKEN: no shipped declaration uses it** |
| **Consequence if the open action stays untaken** | Non-software artifacts continue to be governed by proxy with the proxy's fidelity **unstated**, so the substitution is an assumption inside whoever built the proxy rather than a recorded governance fact |
| **Resolution options for the open action** | **Minimal:** declare one lossy proxy transformation for each non-encodable artifact class the deployment governs. *Cost:* small, per declaration. *Risk:* low. *Impact:* none structurally — it uses a shipped mechanism. **Moderate:** require it — refuse a governance record whose subject is non-encodable unless a lossy proxy transformation is declared. *Cost:* moderate. *Risk:* medium — it makes an omission an error, which is right, and it needs a way to *know* a subject is non-encodable, which is a caller's declaration and therefore C-04-adjacent. **Maximal:** fidelity as a declared **value** with invariants rather than a boolean. *Cost:* high, and partly a domain-modelling problem: fidelity of what, measured how, on whose authority. *Risk:* **high — fabricated precision.** A declared fidelity nobody can check is C-04 where it does most damage. *Impact:* significant — proxy quality becomes a governed measurement rather than a flag |
| **Residual risk** | **NEW IN Ω∞-B:** `lossy: bool` states **that** fidelity is lost, never **how much.** A calibrated measurement record standing in for a specimen and a photograph of its label both declare `lossy=True` and are indistinguishable. **This residual is not in Ω∞-A** |
| **Verdict** | **CONFIRMED FUNDAMENTAL** · mitigated by refusal · **one open action, now measured available** · one new residual |

### C-02 — New knowledge about what must be governed invalidates prior records

| Field | Content |
|---|---|
| **Statement** | Registering a seventh governance axis makes every record built under six axes *incomplete*. No source edit is required; no schema is broken; the existing records simply do not answer a question the model now requires them to answer |
| **Why it cannot be removed** | The three alternatives are each worse: **refuse the registration** closes the world and Rule 3 fails at the constructor; **auto-fill the new axis with its initial position** fabricates a governance fact, making every legacy record silently claim a *measurement* where there is an *absence*; **accept incomplete records silently** makes the concern unmeasurable on the day it is introduced. Reporting the population is the only option that neither closes the world nor invents facts |
| **Classification** | **ONTOLOGY-INDUCED** (a property of any system whose governed questions may grow) |
| **Observation** | Measured again: after registering a `PROVENANCE` axis, `assert_total` on a status built under six axes **raises and names the gap** |
| **Ω∞-B test — the compounding effect, measured for the first time** | The *same* registration produces two outcomes simultaneously: prior records are correctly reported incomplete, **and** the new concern is **registrable and non-binding** — the artifact still certifies |
| **Reproduction** | `b02_b05` §B-05.2 |
| **Determination — and this is the sharpest finding in the matrix** | **C-02's scope is wider than Ω∞-A recorded.** Ω∞-A framed it as being about *records*. The measurement shows it is also about *decisions*: on the day a deployment introduces a new governance concern, **the architecture is more rigorous about the past than about the present.** It correctly reports every prior record as silent about the concern, and simultaneously certifies new artifacts as if the concern did not exist |
| **The part that is fundamental, separated from the part that is not** | **FUNDAMENTAL:** prior records cannot answer a question that did not exist when they were written. **NOT FUNDAMENTAL, and it is A-11:** a newly registered concern failing to bind a certification decision. The first is the world; the second is a fixed enumeration of four preconditions |
| **Resolution options** | **This constraint is not to be resolved; the directive is to be amended.** **Minimal:** amend Ω∞ Rule 9's success chain to distinguish **code migration** (avoidable, and this architecture avoids it — measured across eleven registration kinds) from **record backfill** (not avoidable for any architecture permitting its governed questions to grow). *Cost:* a directive edit. *Risk:* **low, and lower than leaving it** — an unamendable criterion that cannot be met makes every readiness assessment against it dishonest. *Impact:* none on code. **Moderate:** + report the population of **axes that no certification input reads**, so a registered-but-non-binding concern is countable. *Cost:* small once A-11 is resolved. *Risk:* low. *Impact:* medium — it extends `assert_total`'s discipline from vectors to obligations. **Maximal:** + a certification decision cites the **digest of the input set it was decided under**, so widening obligations cannot silently change what CERTIFIED meant. *Cost:* high; depends on A-14's digest and on a storage obligation (G-05) that does not exist. *Impact:* highest — C-02's record-backfill honesty extends to certification decisions across time |
| **Residual risk** | Nothing links axis registration to input registration, **and nothing should** — not every concern is a certification precondition. Auto-binding fabricates an obligation; ignoring it is the current failure. **Reporting the population is the only response that neither invents an obligation nor hides its absence** |
| **Verdict** | **CONFIRMED FUNDAMENTAL** · correctly handled for records · **directive amendment recommended** · **scope wider than recorded: the certification half is A-11 and is removable** |

### C-03 — A total order over distributed events cannot be recovered, only chosen

| Field | Content |
|---|---|
| **Statement** | When two observers have no shared frame, no relation between their frames, or genuinely concurrent causal histories, **no ordering exists to be discovered.** An order can be *imposed*, and the imposition is a decision, not a measurement |
| **Why it cannot be removed** | A property of the world, not of software. The architecture's job is to stop pretending otherwise |
| **Classification** | **MATHEMATICALLY UNAVOIDABLE** |
| **Observation — three separations, each measured** | `CONCURRENT` (an answer: neither dominates) is distinct from `INCOMPARABLE` (a refusal: nothing is declared that would let them be compared). Two `VectorClock` coordinates compare `CONCURRENT`; a Mars coordinate and a logical coordinate compare `INCOMPARABLE` with a cited rule; **branch 0 vs branch 1 compares `INCOMPARABLE`, never `CONCURRENT` — the correct distinction, measured on a forked history.** `canonical_key()` is **named so it cannot be mistaken for a temporal claim**, and `TemporalCoordinate` has **no `<` operator**. `FrameRelation` carries **no arithmetic**, because shipping a factor would make a governance vocabulary the authority for an astronomical fact it cannot verify |
| **Ω∞-B test — the A-24 exposure** | Ω∞-A recorded the designed hash-chained register as re-imposing exactly the total order this constraint forbids, and noted the remedy is free **because the module does not exist**. Tested: a Merkle DAG admitted a concurrent **sibling pair** from two writers each observing only the root; a third entry named **both** predecessors; `verify()` passed; **tampering was detected after mutation**, so tamper evidence is unchanged by the DAG shape; and total order was emitted as a record whose own `kind` is `PROJECTION`, whose `asserted_by_register` is `False`, and whose tie-break basis is stated as *"a choice, not a measurement"* |
| **Reproduction** | `b07` §H5; `b06` §(d); `b01` §B-01.7 (module absence) |
| **Determination** | **The constraint is confirmed and untouched. The A-24 *exposure* to it is removable at zero cost, and remains removable only while `registry.py` does not exist.** The DAG's contribution is not to recover an order — it cannot — but to make the *choice* visible in the record that carries it |
| **Resolution options for the exposure** | **Minimal:** write the register as a DAG. *Cost:* **zero relative to writing it as a chain.** *Risk:* low — measured. *Impact:* high; removes the deepest recorded internal contradiction before it exists. **Moderate:** + projections as self-declaring records with their basis named. *Cost:* small. *Risk:* low. *Impact:* positive. **Maximal:** + each entry carries the `TemporalCoordinate` its writer observed, so the DAG's causal structure and the temporal model's are **comparable and their disagreement reportable**. *Cost:* moderate. *Risk:* **medium — sibling-in-DAG together with `INCOMPARABLE`-in-coordinates is a real disagreement that must be reported, not reconciled**, and a report that fires constantly gets ignored. *Impact:* highest; the only option under which the register and the temporal model are held to each other |
| **Residual risk** | A DAG grows heads without bound absent merges — head count becomes a governed population. And **the constraint itself is untouched by every option**: an order is still chosen |
| **Verdict** | **CONFIRMED FUNDAMENTAL** · honestly represented · **the exposure has a deadline, and the deadline has not passed** |

### C-04 — Meaning cannot be fully mechanised

| Field | Content |
|---|---|
| **Statement** | `Field.kind` is a free string this architecture deliberately never interprets. The openness is required — interpreting kinds would make the expressible kinds a closed list in one file, Rule 4's target — and it has an unavoidable cost: **two parties can agree on a name and disagree on what it means, with nothing able to detect it** |
| **Why it cannot be removed** | Grounding every term in another term is infinite regress; grounding them in a fixed base vocabulary is a closed world. Executable invariants narrow the gap — a `kind` bound to a domain with checkable invariants has *some* mechanical meaning — and cannot close it, because an invariant is itself stated in terms that need grounding |
| **Classification** | **ONTOLOGY-INDUCED** |
| **Observation** | Three-valued `Invariant`: `True`, `False`, `None` for "not checkable here". `DomainRegistry.unexecutable_invariants()` makes the unchecked population **countable rather than absent**, and `TIME_DOMAIN` ships one deliberately unexecutable invariant (`Ω∞-D-T-02`, "corresponds to a real instant in its declared frame") as a worked example |
| **Ω∞-B test — falsification criterion 5** | Attempted: two registries with **byte-identical digests**, same authority, same description, declaring `LENGTH` with a `magnitude` field of kind `NUMBER`. Both validated the same value as VALID. **Nothing anywhere states whether `magnitude` means metres or feet.** Separately: `MASS` = kilograms on node A and pounds on node B — both VALID |
| **Reproduction** | `b07` §H3; `b03_b04` §B-03.3 |
| **Determination** | **Criterion 5 FIRES, exactly as Ω∞-A wrote it.** Vocabulary identity is **not** sufficient for semantic consensus. This does not defeat the digest proposal — digests close divergence *detection* — but it means **A-14 is PARTIALLY REMOVABLE rather than removable**, and the resolution must not be described as closing it |
| **The reach of C-04 is broader than Ω∞-A recorded. Five surfaces, four of them new:** | 1. **`Field.kind`** — the case Ω∞-A records. 2. **NEW: a digest cannot see a registered predicate.** `Invariant.predicate` is a `Callable` with no content digest, so two registries can agree on every digest and **execute different checks** — and the predicate is precisely what gives a kind its mechanical meaning. 3. **NEW: a guard's context vocabulary.** `context: Mapping[str, object]` is open, so two guards may expect the same key with different meanings. 4. **NEW: a declared fidelity.** C-01 maximal's quantified `lossy` is a claim nobody can check. 5. **NEW: a declared proof complexity.** B-01 maximal's declared complexity class is a claim nobody can check without measuring |
| **The most dangerous consequence, and it is a timing consequence** | **After A-14's detection half is resolved, federation will appear to work.** Two nodes will exchange digests, agree, and validate identically — while attaching different meanings to the fields they agreed on. **The successful digest comparison becomes evidence for a consensus that was never established.** This is why the resolution and the constraint must be stated in the same breath |
| **Resolution options** | **There is no resolution. Three mitigations, and each is a mitigation.** **Minimal:** ratchet `unexecutable_invariants()` as **CONVERGENT** — may fall or hold, never rise. *Cost:* very small; the reporter exists. *Risk:* low. *Impact:* none structurally. **Still not done.** **Moderate:** require kinds naming a domain to resolve, and **count** those that do not. *Cost:* moderate. *Risk:* **medium — count, do not refuse**, or an unknown civilisation's kind is rejected rather than made visible, trading Rule 8 for Rule 4. *Impact:* medium — it creates a graded notion of semantic grounding, which is the most a mechanical system can offer. **Maximal:** behavioural agreement — two nodes exchange test vectors with agreed verdicts, so consensus becomes "we agree on outcomes". *Cost:* high — a protocol, a corpus, and governance for the corpus. *Risk:* **high, and the risk is that it still does not close the gap.** Agreement on a finite sample is not agreement on meaning. It narrows sharply and must not be described as closing |
| **Residual risk** | A deployment could declare every invariant unexecutable and pass validation with **zero real checking**. Mitigated only by the minimal ratchet — **still not done** |
| **Verdict** | **CONFIRMED FUNDAMENTAL** · partially mitigated · **ratchet recommended and still not done** · **reach broader than recorded: five surfaces, four new** |

### C-05 — This implementation is Python, and that is not the same as the architecture being Python

| Field | Content |
|---|---|
| **Statement** | The interfaces are describable as contracts, schemas, capabilities and invariants — every protocol is four or fewer methods over names, integers and mappings; `Schema`, `Field`, `Invariant`, `Capability` are declarative values. **And this artifact is Python.** A non-Python engine can implement the contracts and cannot reuse the code |
| **Why the residue cannot be removed** | Some language runs. A reference implementation is in a language. "The architecture is language-neutral" is defensible; "there is no language boundary" is not, and conflating them would itself be the assumption this work exists to find |
| **Classification** | **MATHEMATICALLY UNAVOIDABLE** for the residue; **IMPLEMENTATION-INDUCED** for the missing emitter |
| **Observation** | The designed `schema.py` was **not written**. Until it exists, Rule 6 compliance is a property of the design that **cannot be consumed** — a non-Python implementer has nothing to implement against except Python source |
| **Ω∞-B test — module presence** | Measured against `engine/omega_governance/__init__.py`'s own module table: the table lists **11** modules, of which **2 are present** (`state.py`, `authority.py`) and **9 are ABSENT** — `clock.py`, `contradiction.py`, `certification.py`, `registry.py`, `selfverify.py`, `invariants.py`, `adapters.py`, `evidence.py`, `__main__.py`. `schema.py` is named in Ω∞-A but does not appear in the table at all, so it is a **tenth** absent module documented elsewhere. **And the table is stale in both directions**: it names `clock.py`, which appears superseded by `temporal/clocks.py`, and it omits the `reference/` and `temporal/` subpackages (11 modules) that do exist. And `state.py:58` asserts `invariants.unknown_never_certifies` enumerates all 900 vectors |
| **Reproduction** | `b07` §H9 (mechanical); `b01` §B-01.7; `sed -n '18,40p' engine/omega_governance/__init__.py` |
| **Determination** | **The residue is confirmed fundamental. The fixable part is substantially larger than Ω∞-A recorded.** Ω∞-A listed the missing emitter as one item (G-06). The measurement shows the emitter is one of **eight** absent modules that the package docstring presents in the present tense. **That is a governance finding, not a language finding**: a claim lives in prose and its falsity lives in the filesystem, and nothing detects the divergence |
| **Resolution options** | **Minimal:** amend `__init__.py`'s module table and `state.py:58` to the future tense, marking absent modules `ABSENT`. *Cost:* ~10 lines of prose in 2 files. *Risk:* very low. *Impact:* none — it corrects a claim. **Moderate:** + a mechanical check that every module named in the table exists, failing loudly if not. *Cost:* ~20 lines + 1 test. *Risk:* low. *Impact:* **positive, and it generalises a discipline the tree already has** — `REQUIRED_STATE_NAMES` does exactly this for states, so the pattern is present and was not applied to modules. **Maximal:** write the emitter, and have it emit **guard `describes()` statements** alongside schemas so a non-Python implementer can read the governance rules and not only the data shapes. *Cost:* high; depends on A-10's guard mechanism. *Risk:* medium — an emitted contract that drifts from the code is worse than none, so emission must be derived at build time rather than maintained. *Impact:* significant; it is the difference between Rule 6 being describable and being consumable |
| **Residual risk** | After the emitter exists, the residue stands: **this artifact is Python.** And a new residual: a *mechanical* module-presence check verifies existence, not correctness — a stub `invariants.py` returning `True` would satisfy it. That is C-04 in a new location, and the mitigation is C-04's: count what is unexecutable |
| **Verdict** | **CONFIRMED FUNDAMENTAL (residue)** · **fixable part larger than recorded: 9 absent modules, not 1** · the discipline that would have caught it already exists in the same file |

---

## 3. CANDIDATES RE-EXAMINED AND STILL REJECTED

Ω∞-A listed eight candidates that could plausibly be called fundamental and are not. Ω∞-B adds
measurement to three of them and rejects three new candidates.

| Candidate | Ω∞-A verdict | Ω∞-B measurement |
|---|---|---|
| "Governance needs a wall clock" | Measured false | **Re-confirmed and strengthened.** A clock with **no ordering at all** registered; a **reversed arrow of time** registered. No code asserts an arrow direction, so the architecture holds no privileged chronology — a stronger result than "no wall clock". **And a time-bounded governance guard was written with no wall clock** |
| "Exhaustive proof is the strongest assurance" | "False in the way that matters" | **Re-confirmed with the measurement Ω∞-A lacked.** A registered axis adds **exactly zero** distinguishable cases, so redundancy reaches **9,565,938×** at 20 axes. And the exhaustive method's inner loop **already was** the structural argument, executed 900 times — so the structural proof is not an approximation of the exhaustive one |
| "Two guard kinds are enough" | "Measured false, and it is the core proposal" | **Re-confirmed by construction.** All eight capabilities written and executed |
| "A register must be a chain" | Not fundamental | **Re-confirmed by construction.** DAG verified, tampering detected, concurrent siblings admitted |
| **NEW: "Transitivity cannot be checked for an arbitrary registered ordering"** | not considered | **Rejected.** A check written over the shipped `Relation` properties found 6 violations in a cyclic ordering and 0 in the shipped strategy. **Residual: it is O(n³) in the sample, so it is SAMPLED and must be labelled as such** — otherwise it becomes G-09's silent-expiry failure in a new location |
| **NEW: "A census over an unbounded population is impossible"** | not considered | **Rejected.** The census result type is already a monoid under pointwise addition: three shard censuses merged equal the union's census in any order, and a one-at-a-time stream reproduces it. **Residual: `fallback_density` is a RATIO, and a ratio is not a monoid** |
| **NEW: "Only one authority can relate two domains without order-dependence"** | not considered | **Rejected.** The shipped refusal's reasoning is correct — two declarations on one `(source, target)` key *would* make the applicable authority depend on registration order — but the defect is the **key**, not the refusal. Including the authority in the key preserves the concern and admits both authorities |

**Three new candidates considered and all three rejected.** That is a good sign about the constraint
list's tightness, and it is also a warning: the two new candidates most easily mistaken for fundamental
(transitivity, unbounded census) were both dispatched by a prototype of a few dozen lines. **A
limitation that has not been attempted should not be recorded as fundamental.**

---

## 4. WHAT THIS MATRIX DOES NOT ESTABLISH

| Claim | Why the evidence does not support it |
|---|---|
| "The fundamental constraint list is complete" | **No.** Two of Ω∞-A's five falsification criteria (2 and 4) were **not tested**. Ω∞-B found four new C-04 surfaces and one new C-01 residual, which is direct evidence that this list is incomplete too |
| "The five constraints are fully mitigated" | **No.** C-01's open action is available and **untaken**. C-02's directive amendment is **not made**. C-04's ratchet is **not done**. C-05's emitter is **not written** — along with seven other documented modules |
| "Confirming a constraint is fundamental settles it" | **No.** C-02 and C-05 were confirmed *and found broader than recorded*. Confirmation of the constraint is compatible with the fixable part being larger than believed |
| "C-03's exposure is closed" | **No.** It is removable at zero cost **while `registry.py` does not exist**. Nothing has been built |

---

## 5. DETERMINATION

**No closure is declared. No readiness is claimed. No constraint is removed.**

| Question | Determination |
|---|---|
| Are all five Ω∞-A constraints genuinely fundamental? | **Yes, all five confirmed. None mis-placed** |
| Was any limitation wrongly classified as fundamental? | **No** — and this was tested rather than assumed, via Ω∞-A's own falsification criterion 3, the one it ranked most likely to fire |
| Did any constraint prove broader than recorded? | **Two. C-02** extends from records to *decisions* (the certification half, which is A-11 and is removable). **C-04** surfaces in five places, four of them new |
| Did any constraint's *fixable* part prove larger? | **C-05.** Eight absent modules rather than one |
| How many open actions attached to constraints are done? | **Zero of four.** C-01's proxy declaration (available, untaken), C-02's directive amendment (not made), C-04's ratchet (not done), C-05's emitter (not written) |
| Are new fundamental constraints proposed? | **None.** Three new candidates were considered and all three rejected |

**The observation that best justifies this document having been written.** Ω∞-A's most likely
falsification criterion was that C-01 is *mis-placed* — that a non-encodable artifact's proxy
relationship would turn out not to be expressible, and the architectural core would need a sixth
mechanism for physical reference. **It is expressible.** The mechanism exists, the declaration succeeds,
the transformation correctly reports itself as uncomputable rather than approximating, and no shipped
declaration uses it. The constraint was placed correctly and its mitigation was simply never taken up —
which is a far better position than the one Ω∞-A thought most likely, and it is only knowable because
the attempt was made.
