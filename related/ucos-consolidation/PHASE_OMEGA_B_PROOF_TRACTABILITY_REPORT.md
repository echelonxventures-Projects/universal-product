# UCOS Ω∞ — PHASE Ω∞-B, DELIVERABLE 4
## Proof Tractability Report (B-01)

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


**AUTHORITY = NONE (DERIVED TRUTH).** This document analyses and classifies. It issues no
certification, seals no artifact, advances no ratchet, declares no closure and modifies no active
governance, validation or certification process. No readiness claim is made anywhere in it.

**INPUT.** Ω∞-A findings A-16, G-09, X-07 (all recorded CRITICAL, open), treated as authoritative and
not re-discovered.

**EVIDENCE ARTIFACTS.**

| Artifact | Purpose |
|---|---|
| `00-MASTER/UCOS-OMEGA-B-001/probes/b01_proof_tractability.py` | measures the growth function, the assurance content per vector, and the failure threshold |
| `00-MASTER/UCOS-OMEGA-B-001/probes/b01-output.txt` | its recorded output |
| `00-MASTER/UCOS-OMEGA-B-001/probes/b07_removability_validation.py` §H7 | tests whether a tractable proof preserving assurance can be written over shipped types |
| `00-MASTER/UCOS-OMEGA-B-001/probes/b07-output.txt` | its recorded output |

**REPRODUCTION, for every measurement in this document:**

```
cd /Users/bipin/Desktop/UCOS-CONSOLIDATION
.ec1-venv/bin/python 00-MASTER/UCOS-OMEGA-B-001/probes/b01_proof_tractability.py
.ec1-venv/bin/python 00-MASTER/UCOS-OMEGA-B-001/probes/b07_removability_validation.py
```

**REPRODUCTION FIDELITY, MEASURED.** `b01` was re-executed against current repository state and
diffed against its stored output. **Every structural count is byte-identical** — state-space sizes,
enumerated counts, UNKNOWN-held counts, violation counts, edge counts, axis positions. The only
differing lines are wall-clock timings (6 lines of 110). `b07` re-executed twice differs in 6 lines,
all timings. So the measurements below are deterministic and the timings are indicative.

---

## 1. FINDING B-01.1 — the growth function is exponential in axis count, and it is exactly Θ(3ⁿ)

### Observation

| Axes | State space | Ω∞-A reported | Match |
|---|---|---|---|
| 6 (shipped) | 900 | 900 | yes |
| 7 | 1,800 | 1,800 | yes |
| 10 | 48,600 | 48,600 | yes |
| 20 | 2,869,781,400 | 2,869,781,400 | yes |

The shipped axis profile is measured, not assumed: ATTRIBUTION 2, CERTIFICATION 5, CONSISTENCY 2,
CUSTODY 5, GOVERNANCE 3, MEASUREMENT 3 → product **900**, edges **36**.

Ω∞-A quoted four figures without stating the registration profile that produced them. Exactly one
simple profile fits all four points, and `b01` states it: the shipped six, a 7th axis with two
positions, and every axis from the 8th onward with three. That gives

> **|S|(n) = 900 · 2 · 3^(n−7) for n ≥ 7 — Θ(3ⁿ), exponential in the number of registered axes.**

**A correction to Ω∞-A, and it makes the finding worse rather than better.** Ω∞-A's 20-axis figure of
2,869,781,400 assumes the 7th axis has two positions. `b07` §H7 registers 20 axes with three
positions each from the 7th onward and measures **4,304,672,100** — 1.5× larger. At 40 axes the
measured space is **15,009,463,529,699,912,100** (1.5 × 10¹⁹). The exponent, not the constant, is the
finding, and both profiles agree on the exponent.

### Reproduction

`b01` §B-01.2 (growth function re-derived and checked against all four Ω∞-A data points) and `b07`
§H7 (20 and 40 axes registered at runtime).

### Architectural cause

**PROOF-INDUCED.** Not a defect in any type, function or registry. `state.py:58` specifies the proof
method:

> "AND NOTHING RETURNS TO UNKNOWN — it has no inbound edge — which makes the invariant provable by
> **exhaustive search rather than by argument**. `invariants.unknown_never_certifies` enumerates all
> 900 vectors."

The cost is a property of the *method chosen*, and the method's input is the axis product. Registering
an axis is the advertised extension mechanism (Ω∞ Rule 3), so the extension mechanism multiplies the
proof's cost by the new axis's position count. Nothing in the code is wrong; the *proof strategy* does
not survive the extensibility the same architecture advertises.

### Consequence if unresolved

Measured failure threshold, by registration, same machine, same code:

| Axes | State space | Seconds |
|---|---|---|
| 6 | 900 | 0.0026 |
| 10 | 72,900 | 0.365 |
| 13 | 1,968,300 | 13.49 |
| 20 | 2,869,781,400 | ~19,672 (≈5.5 h, extrapolated at the measured per-vector rate) |
| 25 | 697,356,880,200 | ~4,780,280 (≈55 days, extrapolated) |

**The consequence is not slowness. It is a silent expiry.** No exception is raised, no test fails, no
migration is demanded, and no document stops claiming the proof. A deployment that registers fourteen
axes — using the architecture exactly as instructed — holds an architecture that still *advertises* a
machine-proven invariant it can no longer run. Ω∞-A called this "the only gap the architecture creates
for itself by being used correctly", and that assessment is confirmed.

---

## 2. FINDING B-01.2 — the enumerated vectors carry almost no assurance, and a new axis adds exactly none

**This is the measurement Ω∞-A did not take, and it changes the recommendation from "make the proof
cheaper" to "the enumeration was never the assurance".**

### Observation

For each invariant target, `b01` §B-01.3 computes the axes any guard on any inbound edge can actually
read, and therefore how many of the enumerated vectors are *distinguishable* to the invariant:

| Invariant target | Axes readable by inbound guards | Distinguishable cases | Vectors enumerated | Redundancy |
|---|---|---|---|---|
| `CERTIFIED` | ATTRIBUTION, CERTIFICATION, CONSISTENCY, CUSTODY, GOVERNANCE | 300 | 900 | **3×** |
| `GOVERNED` | ATTRIBUTION, CUSTODY, GOVERNANCE | 30 | 900 | **30×** |
| `EXEMPTED` | CUSTODY, GOVERNANCE | 15 | 900 | **60×** |

And the mechanism behind it, stated as a rule: **a newly registered axis appears in no existing edge's
`blocked_by`, so it cannot enter any guard's relevant set.** Registering an axis with k positions
multiplies the enumeration by k and adds **exactly zero** distinguishable cases.

Redundancy for `UNKNOWN never certifies` as axes are registered:

| Axes | Enumerated | Distinguishing | Redundancy |
|---|---|---|---|
| 6 | 900 | 300 | 3× |
| 7 | 1,800 | 300 | 6× |
| 10 | 48,600 | 300 | 162× |
| 20 | 2,869,781,400 | 300 | **9,565,938×** |

### Reproduction

`b01` §B-01.3.

### Architectural cause

**PROOF-INDUCED, and the cause is a mismatch between the proof's domain and the invariant's domain.**
The invariant quantifies over *vectors*; the guards that make it true read only the *axes named in
`blocked_by`*. The enumeration therefore re-tests the same guard decision once per combination of axes
the guard cannot see.

### Consequence if unresolved

The exponential cost buys nothing. At 20 axes the proof would spend 5.5 hours re-deciding 300 cases
9.5 million times each. **A resolution that declines to enumerate loses no assurance whatsoever**, and
that is a measured claim rather than an argument.

---

## 3. FINDING B-01.3 — the exhaustive proof does not exist

**The most consequential finding in B-01, and it is not in Ω∞-A.**

### Observation

`state.py:58` asserts `invariants.unknown_never_certifies` enumerates all 900 vectors.
`engine/omega_governance/__init__.py:34` lists `invariants.py` as "Ω-2.9 — seven executable proofs,
two of them exhaustive".

Measured contents of `engine/omega_governance/`, against the eleven modules the docstring's own
"READ IN THIS ORDER" table names:

| Module named in the `__init__.py` table | Present |
|---|---|
| `state.py` | **yes** |
| `authority.py` | **yes** |
| `clock.py` | **ABSENT** — and it appears superseded by `temporal/clocks.py` |
| `contradiction.py` | **ABSENT** |
| `certification.py` | **ABSENT** |
| `registry.py` | **ABSENT** |
| `selfverify.py` | **ABSENT** |
| `invariants.py` | **ABSENT** |
| `adapters.py` | **ABSENT** |
| `evidence.py` | **ABSENT** |
| `__main__.py` | **ABSENT** |

**Nine of the eleven modules the docstring's own table presents are absent; two are present.**

Two further facts about the same table, and each is a separate defect:

- **`schema.py` is absent and is not in the table at all.** Ω∞-A names it (G-06, C-05) as designed and
  not written, so it is a **tenth** absent module, documented elsewhere and unlisted here.
- **The table omits what does exist.** `reference/` (5 modules) and `temporal/` (6 modules) are present
  and absent from the table. So the table is stale **in both directions** — it names nine modules that
  do not exist and omits eleven that do.

`b01` had to *reconstruct* the exhaustive proof inside the probe in order to measure it at all.

### Reproduction

`b07` §H9 (mechanical: the eleven table names checked, plus the unlisted-absent and unlisted-present
populations); `b01` §B-01.7 (the nine DESIGN names). Also `sed -n '18,40p'
engine/omega_governance/__init__.py` and `sed -n '50,60p' engine/omega_governance/state.py`.

### Architectural cause

**GOVERNANCE-INDUCED, not proof-induced.** A design document and a module docstring were written in
the present tense for modules that were designed and not built. Nothing detects the divergence,
because the claim lives in prose and the absence lives in the filesystem.

### Consequence if unresolved

The B-01 blocker as Ω∞-A framed it — "the proof expires as axes are registered" — is **not the
current condition**. The current condition is that **the proof has never run**. Those need different
responses:

- if the proof expires, the fix is a better proof method;
- if the proof does not exist, the first fix is to **stop claiming it**, and only then to build it.

Reversing that order would build a tractable proof while the docstring's false claim about the
intractable one remains in the tree — and the false claim is the part that misleads a reader today.

**This also reclassifies Ω∞-A A-11 and A-24.** Both were recorded as "designed, not yet built" and
therefore zero-cost to fix. That is confirmed and it is *broader* than recorded: the same is true of
contradiction handling, self-verification, the register, the adapters, the evidence document, the CLI
and the schema emitter.

### Resolution options

| Option | Change | Cost | Risk | Architectural impact |
|---|---|---|---|---|
| **Minimal** | Amend `state.py:58` and `__init__.py:34` to the future tense, and add an `ABSENT` column to the package docstring's module table | ~10 lines of prose in 2 files | **Very low.** No behaviour changes | **None.** Corrects a documentation claim |
| **Moderate** | The above, plus a mechanical check that every module named in `__init__.py`'s table exists, failing loudly if not | above + ~20 lines + 1 test | Low | **Positive.** Makes the class of error self-detecting. This is the same discipline `REQUIRED_STATE_NAMES` already applies to states |
| **Maximal** | Build `invariants.py` with the structural proof of §4, the declining exhaustive cross-check, and the module-presence check | ~200 lines + tests | Medium — it is new code in a package with no test harness of its own yet | **Positive**, and it is the only option that makes the assurance claim true rather than merely honest |

**Recommended: MODERATE now, MAXIMAL as a Ω∞-C entry item.** The minimal option alone leaves the
divergence undetectable, and the same mistake recurs the moment another module is designed.

### Residual risk

The module-presence check verifies existence, not correctness. A stub `invariants.py` returning `True`
would satisfy it. That residual is C-04 (meaning cannot be fully mechanised) in a new location, and
the mitigation is the same one Ω∞-A recommends there — count what is unexecutable, do not assume it.

---

## 4. FINDING B-01.4 — a proof independent of axis count exists, holds, and preserves all assurance

### Observation

The structural argument, executed on the shipped model (`b01` §B-01.5):

```
edges_inspected                            36
inbound_to_UNKNOWN                         []
inbound_to_CERTIFIED                       ['Ω²-S-26', 'Ω²-S-22']
inbound_to_CERTIFIED_not_guarding_UNKNOWN  []
holds                                      True
seconds                                    0.000045
```

Executed at 6, 20 and 40 registered axes (`b07` §H7):

| Axes | State space | Structural: holds | Structural: seconds | Exhaustive |
|---|---|---|---|---|
| 6 | 900 | **True** | 0.000072 | COMPLETED, 900 enumerated, 0 violations, 0.0026 s |
| 20 | 4,304,672,100 | **True** | 0.000068 | **DECLINED** with a stated reason |
| 40 | 15,009,463,529,699,912,100 | **True** | 0.000066 | **DECLINED** with a stated reason |

**The structural proof's cost does not move.** 36 edges at 6 axes, 36 edges at 40 axes, ~65
microseconds in both cases, because the edge set is what it reads and registering an axis adds no
edge.

### The argument, stated so it can be refused

> `UNKNOWN` never certifies **because**
> (a) no declared edge targets `UNKNOWN`, so the unknown population only ever drains, and
> (b) every edge targeting `CERTIFIED` names `UNKNOWN` in its `blocked_by`.
> Therefore no *reachable* vector holds both. Each fact is one pass over the edge set: **O(|E|),
> independent of axis count and of state-space size.**

### A defect in the exhaustive method that the structural method does not have

`b07` §H7 initially enumerated the product and tested "holds UNKNOWN and holds CERTIFIED". At 6 axes
that reports **36 violations**. All 36 are false: they are vectors *in the product* that are not
*reachable*. `b01`'s formulation is the correct one — for each vector holding `UNKNOWN`, ask whether
`check(status, CERTIFIED)` returns an edge — and it reports 0. Both probes now agree at 0.

**This is not a probe bug worth burying; it is evidence about the two methods.** The invariant is a
statement about **reachability**, and reachability is a property of the **edge set**. An enumeration
of the product does not prove it without consulting the graph — so the exhaustive method's inner loop
is *already* the structural argument, executed 900 times. The structural proof is not an
approximation of the exhaustive one. **It is what the exhaustive one was computing, minus the
repetition.**

### Architectural cause of the original choice

**PROOF-INDUCED, and defensible when it was made.** At six axes, 900 vectors is cheap and an
enumeration is easier to trust than an argument. The choice becomes wrong only in combination with
open-world axis registration, and that combination is exactly what Ω∞ Rule 3 mandates.

### Consequence if unresolved

Already stated in §1: silent expiry. Adding §2's measurement: the expiry costs nothing in assurance,
so an architecture that lets it happen is trading real cost for no benefit.

---

## 5. IS EXHAUSTIVE VERIFICATION FUNDAMENTALLY INCOMPATIBLE WITH OPEN-WORLD AXIS EXPANSION?

**Yes, and the incompatibility is mathematically unavoidable — for the method, not for the assurance.**

| Question the directive asks | Answer | Evidence |
|---|---|---|
| Is the growth exponential? | Yes, Θ(3ⁿ) in axis count | §1, four Ω∞-A points reproduced |
| Can any machine enumerate an open-world product? | **No.** An open world places no bound on n, and enumeration is Θ(kⁿ). No hardware, algorithm or parallelism changes an unbounded exponent | §1 |
| Is *assurance* therefore lost? | **No** | §2 (enumeration adds zero distinguishable cases), §4 (structural proof holds at 40 axes) |

So the honest statement has two halves and both matter:

> **Exhaustive enumeration is mathematically incompatible with open-world axis expansion. Assurance is
> not.** The incompatibility is confined to one proof *method*, and the method was carrying no
> assurance the structural argument does not carry.

**Consequence for the directive's own framing.** Ω∞-A recorded A-16 as CRITICAL because it "couples
indefinite domain diversity to loss of machine-proven invariants". That coupling is now measured to be
**an artefact of the method, not a property of the architecture.** A-16 is therefore *removable*, and
what is *unavoidable* is only the narrower claim that no enumeration can be exhaustive over an
unbounded product.

---

## 6. ASSURANCE PRESERVATION OPTIONS — the six models the directive names, each assessed against measurement

| Model | Verdict | Evidence and reasoning |
|---|---|---|
| **Exhaustive** | **UNUSABLE above a declared size, and no loss** | Θ(3ⁿ); 13 axes = 13.5 s, 20 axes ≈ 5.5 h, 25 axes ≈ 55 days. Redundancy 9.5 million× at 20 axes. Keep **only** as a cross-check at small sizes, and make it **decline loudly** above a declared limit |
| **Structural (symbolic)** | **RECOMMENDED — strictly stronger and cheaper** | O(\|E\|), measured at 36 edges and ~65 µs for 6, 20 and 40 axes. Holds in all three. Loses nothing, because §2 shows the extra vectors were indistinguishable and §4 shows the enumeration's inner loop *was* this argument |
| **Compositional** | **AVAILABLE and appropriate for cross-axis laws** | The shipped `blocked_by` mechanism is already compositional: a cross-axis law is a property of one edge. A per-axis argument composes because axes are orthogonal by construction (`GovernanceStatus` enforces one position per axis). Not separately needed for this invariant; needed for invariants over *combinations* of axes |
| **Incremental** | **AVAILABLE, and the natural companion to registration** | Registering an axis adds no edge, so the structural proof's input is unchanged and needs **no** re-proof. Registering an *edge* requires re-checking that one edge — O(1) per registration. This is the strongest available answer to "the proof must survive extension" |
| **Partitioned** | **PROVEN AVAILABLE for populations** (`b07` §H6) | Measured: three disjoint shard censuses merged equal the census of the union, in any merge order, and a one-artifact-at-a-time stream reproduces it exactly. So *population* assurance partitions cleanly. **Does not apply to this invariant**, which is about the graph rather than the population |
| **Probabilistic** | **REJECTED, and the rejection is a finding** | Sampling 10⁶ of 2.87 × 10⁹ vectors would give a confidence, not a proof — and it would be a *worse* trade than the structural proof, which gives certainty at lower cost. Probabilistic verification is the right answer when no structural argument exists; here one does, so accepting probability would be paying assurance for nothing. **Recorded so the option is refused explicitly rather than omitted** |

**The ranking is not a preference.** Structural + incremental dominates every other option on both
axes simultaneously — cheaper *and* stronger — which is unusual and is the reason this finding is
tractable at all.

---

## 7. RESOLUTION OPTIONS FOR B-01 AS A WHOLE

### Minimal change

Replace the enumeration with the structural argument for `unknown_never_certifies`, and correct the
two prose claims in §3.

- **Cost.** Small. The argument is ~15 lines (`b07` §H7's `structural_proof`), plus prose edits.
- **Risk.** **Low, and lower than it appears.** The structural argument is *executable* and was
  executed at three axis counts. The residual risk is that a reader trusts an argument less than an
  enumeration, which is addressed by keeping the enumeration as a cross-check at small sizes.
- **Architectural impact.** **None.** No type, protocol, registry or record changes. `state.py` is
  untouched except for one docstring sentence.

### Moderate change

The above, plus:

1. an exhaustive cross-check that **declines above a declared state-space limit with a stated reason**
   (measured working at 20 and 40 axes: `outcome=DECLINED`, reason names the size and the limit);
2. a mechanical check that every module named in `__init__.py` exists;
3. the limit itself declared as a value, not a literal, so a deployment may raise it and own the
   consequence.

- **Cost.** Moderate. ~120 lines plus tests.
- **Risk.** Low. The declining path is the safe path — it refuses to claim, rather than claiming
  falsely.
- **Architectural impact.** **Positive.** It converts a claim that expires silently into one that
  expires loudly, which is the same discipline `Invariant.predicate is None` already applies to
  unexecutable invariants: **make the gap countable rather than absent.**

### Maximal correctness

The above, plus:

4. every invariant in the designed `invariants.py` given a structural or compositional proof, with its
   proof method and complexity **declared as data** in the invariant record;
5. an invariant declaring an intractable method **refused at registration**, not at proof time;
6. incremental re-proof on edge registration;
7. the proof method's complexity class carried in the evidence record, so a reader sees O(\|E\|)
   rather than trusting "proven".

- **Cost.** High. This is the whole of designed Deliverable Ω-2.9 plus a complexity vocabulary.
- **Risk.** Medium. Declaring complexity classes as data invites a wrong declaration, which is C-04
  again — a declared complexity nobody can check. Mitigation: hold the declared class against the
  measured runtime at two sizes and report divergence.
- **Architectural impact.** **Significant and positive.** It makes "proof method" a first-class
  declared property, which is the same move Phase 2 made for time, storage and identity. It is also
  the first place in the architecture where an *assurance* claim becomes a governed value rather than
  a paragraph.

---

## 8. RESIDUAL RISK AFTER ANY OF THE ABOVE

| # | Residual | Why it survives | Severity |
|---|---|---|---|
| R-1 | The structural argument is specific to `unknown_never_certifies`. The other six designed invariants have **no proof of any kind**, because `invariants.py` does not exist | §3. Nothing has been proven about them, tractably or otherwise | **HIGH — and it is the true state of B-01.** The tractable-proof question is answered; the *existence* question is not |
| R-2 | A structural argument is a claim about the **declared** edge set. An edge registered later that targets `CERTIFIED` without naming `UNKNOWN` breaks the invariant, and nothing currently re-checks on registration | The proof is not yet incremental | MEDIUM. Closed by moderate option item (6) |
| R-3 | The exhaustive cross-check's declared limit is a judgement. Too high and it hangs; too low and the cross-check never runs | A threshold cannot be derived from the model | LOW. Visible, declared, and owned |
| R-4 | `assert_total` is **not** partitionable in the way `census` is, and neither is `fallback_density` — a **ratio is not a monoid** and must be carried as a (numerator, denominator) pair | Measured in `b07` §H6 | MEDIUM, and it belongs to A-15 rather than A-16 |
| R-5 | The transitivity of a registered ordering is checkable only by **sampling** (`b07` §H8: O(n³) in the sample, 6 violations found in a cyclic ordering, 0 in the shipped one). A sampled property is not a proof | No structural argument over an arbitrary registered `compare` function exists | MEDIUM, and it must be **labelled** as sampled wherever it is reported |

---

## 9. CLOSURE RECOMMENDATION

**No closure is declared.** What is established, mechanically:

| Question | Determination | Basis |
|---|---|---|
| Is B-01 removable? | **PARTIALLY REMOVABLE** | The *tractability* blocker is removable (§4, §6). The *absence* of the proof (§3) is a separate, larger, and also removable finding. R-1 is open |
| Classification | **PROOF-INDUCED** for tractability; **GOVERNANCE-INDUCED** for the false claim | §1, §3 |
| Is any part mathematically unavoidable? | **Yes, one part:** no enumeration can be exhaustive over an unbounded product. **This costs no assurance** | §2, §5 |
| Cost of delay | **The claim expires without an error.** Ω∞-A ranked this 4th; the ranking stands, and §3 makes the *first* action a prose correction, which has no cost of delay at all | §1, §3 |

**Recommended sequence, and the order is load-bearing:**

1. **Correct the false claims first** (§3, minimal). Until then, every other statement about B-01
   describes a proof that has not run.
2. **Then** replace the method (§4, minimal + moderate).
3. **Then** make it incremental (R-2) and extend to the remaining six invariants (R-1).

Proceeding in the reverse order would produce a tractable proof for one invariant while the tree
continues to claim seven, two of them exhaustive.

**What would make this report wrong.** If an invariant is found whose proof genuinely requires
enumerating the axis product — one whose guards read *every* axis, so no axis is indistinguishable —
then §2's redundancy argument fails for that invariant and the structural substitution is not
available. None of the seven designed invariants appears to be of that shape, **but six of them cannot
be examined, because they do not exist.** That is the honest limit of this report.
