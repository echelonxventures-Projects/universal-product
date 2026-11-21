# UCOS Ω∞ — PHASE Ω∞-A, DELIVERABLE 8
## Remaining Fundamental Constraints

**AUTHORITY = NONE (DERIVED TRUTH).** Discovery only.

**WHAT THIS DOCUMENT IS FOR.** Deliverables 1–6 list things to fix. This one lists things that **cannot be
fixed**, and argues why each is a genuine edge of the world rather than a defect not yet understood.

**WHY IT MATTERS MORE THAN THE FIXABLE LIST.** An architecture that claims no remaining constraints has
either finished or stopped looking, and the second is far more common. Ω∞ Rule 9 sets the goal as
"support unknown future things without architectural replacement" — that is a claim about *capacity*, and
a capacity claim with no stated limit is unfalsifiable. Naming the limits is what makes the rest of the
claim testable.

**THE STANDARD APPLIED.** A constraint is FUNDAMENTAL only if removing it would require abandoning the
idea of a governance record. Everything else is work. Five constraints meet that standard. Two of them
are corrections to the directive's own success criteria.

---

## C-01 — Only what can be reduced to bytes can be governed

**Statement.** A governance record's integrity rests on a fingerprint. A fingerprint requires an encoding.
An encoding requires the value to be reducible to a finite byte string. Therefore anything not so
reducible — a physical specimen, a live process, a continuous field, an unbounded stream, an unrepeatable
observation — **cannot itself enter a governance register.** It can only be *represented* by something
that can.

**Why it cannot be removed.** Not an implementation limit. Tamper evidence *is* "the bytes did not
change"; without bytes there is nothing for tamper evidence to be about. An architecture that governed
non-encodable things would be governing claims about them, which is what this constraint says.

**How the architecture responds honestly.** `reference/domain.assert_encodable` **refuses** rather than
stringifying. The refusal names the component and its type and tells the caller to register a codec. A
`repr()` fallback would have produced bytes that depend on a Python memory address — governance records
that differ between runs for a reason no reader could find. **Refusing is the whole mitigation, and it is
the correct one.**

**The remaining exposure, stated plainly.** When a non-encodable thing is governed by proxy, the proxy's
*fidelity* is currently unstated. The recommendation is to require the proxy relationship to be a declared
`Transformation` with an authority and `lossy=True`, so the substitution is a recorded governance fact
rather than an assumption in whoever built the proxy. **This is not yet done**, and it is the one
actionable item attached to a constraint that is otherwise permanent.

**Classification.** FUNDAMENTAL · mitigated by refusal · one open action.

---

## C-02 — New knowledge about what must be governed invalidates prior records

**Statement.** Registering a seventh governance axis makes every record built under six axes *incomplete*.
No source edit is required; no schema is broken; the existing records simply do not answer a question the
model now requires them to answer.

**Measured.** After registering a `PROVENANCE` axis, `assert_total` on a status built under six axes raises
and names the gap.

**Why it cannot be removed.** The three alternatives are each worse:

| Alternative | Consequence |
|---|---|
| Refuse the registration | Closes the world. Ω∞ Rule 3 fails at the constructor |
| Auto-fill the new axis with its initial position | Fabricates a governance fact. Every legacy record would silently claim "UNPROVENANCED" as a *measurement* when it is an absence — the exact silent state Phase 2 exists to eliminate |
| Accept incomplete records silently | The same silence, one level up: the concern becomes unmeasurable on the day it is introduced |

Reporting the population is the only option that neither closes the world nor invents facts.

**This is a correction to Ω∞ Rule 9.** The directive's success chain reads:

> New Domain Added → Registration Only → No Source Modification → **No Migration** → No Recompilation …

For vocabulary *widening*, the first three links hold and the fourth cannot. **Rule 9 should distinguish
code migration from record backfill.** Code migration is avoidable and this architecture avoids it —
measured across eleven registration kinds. Record backfill is not avoidable for any architecture that
permits its governed questions to grow, and an architecture claiming otherwise is either not growing its
questions or fabricating answers to the new ones.

**Classification.** FUNDAMENTAL · correctly handled · **directive amendment recommended**.

---

## C-03 — A total order over distributed events cannot be recovered, only chosen

**Statement.** When two observers have no shared frame, no relation between their frames, or genuinely
concurrent causal histories, **no ordering exists to be discovered.** An order can be *imposed* — and the
imposition is a decision, not a measurement.

**Why it cannot be removed.** It is a property of the world, not of software. The architecture's job is to
stop pretending otherwise.

**How the architecture responds.** Three separations, each measured:

- `CONCURRENT` (an answer: neither dominates) is distinct from `INCOMPARABLE` (a refusal: nothing is
  declared that would let them be compared). Two `VectorClock` coordinates compare `CONCURRENT`; a Mars
  coordinate and a logical coordinate compare `INCOMPARABLE` with a cited rule.
- `canonical_key()` — the serialisation order — is **named so it cannot be mistaken for a temporal
  claim**, and `TemporalCoordinate` deliberately has **no `<` operator**, because `<` on a time type
  asserts totality.
- `FrameRelation` carries **no arithmetic**. Relating Mars local solar time to a terrestrial scale needs
  an ephemeris, a site and a leap-second table; shipping a factor would make a governance vocabulary the
  authority for an astronomical fact it cannot verify. Two of three shipped transformations carry no
  computation and say so.

**The remaining exposure.** The designed hash-chained register would re-impose exactly the total order this
constraint forbids (A-24). The remedy is a Merkle DAG, and it is **free today because the module does not
exist**. This is the only constraint in this document with a deadline attached.

**Classification.** FUNDAMENTAL · honestly represented · **one design decision must be made before the
register is built**.

---

## C-04 — Meaning cannot be fully mechanised

**Statement.** `Field.kind` is a free string this architecture deliberately never interprets. That
openness is required — interpreting kinds here would make the set of expressible kinds a closed list in
one file — and it has an unavoidable cost: **two parties can agree on a name and disagree on what it
means, with nothing able to detect it.** The registry's conflict check catches differing *descriptions*;
it cannot catch differing *interpretations of identical descriptions*.

**Why it cannot be removed.** Grounding every term in another term is regress; grounding them in a fixed
base vocabulary is a closed world. Executable invariants narrow the gap — a `kind` bound to a domain with
checkable invariants has *some* mechanical meaning — and they cannot close it, because an invariant is
itself stated in terms that need grounding.

**How the architecture responds, and where it stops.** `Invariant` is three-valued: `True`, `False`, and
`None` for "not checkable here". `DomainRegistry.unexecutable_invariants()` makes the unchecked population
**countable rather than absent**, and `TIME_DOMAIN` ships one deliberately unexecutable invariant
(`Ω∞-D-T-02`, "corresponds to a real instant in its declared frame") as a worked example.

**The remaining exposure.** A deployment could declare every invariant unexecutable and pass validation
with zero real checking. The mitigation is a **ratchet, not a fix**: hold `unexecutable_invariants()` as a
CONVERGENT population that may fall or hold and never rise. **Not yet done.**

**Classification.** FUNDAMENTAL · partially mitigated · ratchet recommended.

---

## C-05 — This implementation is Python, and that is not the same as the architecture being Python

**Statement.** The interfaces are describable as contracts, schemas, capabilities and invariants — every
protocol is four or fewer methods over names, integers and mappings; `Schema`, `Field`, `Invariant` and
`Capability` are declarative values. **And this artifact is Python.** A non-Python engine can implement the
contracts and cannot reuse the code.

**Why the residue cannot be removed.** Some language runs. A reference implementation is in a language.
The claim "the architecture is language-neutral" is defensible; the claim "there is no language boundary"
is not, and conflating them would itself be the assumption this phase exists to find.

**The remaining exposure, honestly.** The designed schema-emission module was **not written**. Until it
exists, Rule 6 compliance is a property of the design that **cannot be consumed** — a non-Python
implementer has nothing to implement against except Python source. That part *is* fixable and is listed as
G-06. What survives after it is fixed is only the residue above.

**Classification.** FUNDAMENTAL (residue) · CRITICAL and fixable (the missing emitter).

---

## 2. WHAT IS **NOT** FUNDAMENTAL — candidates rejected

Recorded because a constraints document is only credible next to what was considered and refused. Each of
these could plausibly be called fundamental and is not:

| Candidate | Why it is not fundamental |
|---|---|
| "Governance needs a wall clock" | Measured false. Zero `datetime`/`time` imports in the Phase 2 tree; a logical clock orders events and declines to locate them, and declining visibly beats answering wrongly |
| "Determinism requires numeric values" | Measured false. Determinism is the codec's declared `REPRODUCIBLE` obligation. A position of `("EPOCH-ALPHA",)` fingerprints deterministically |
| "Tamper evidence requires SHA-256" | Measured false. The pipeline ran under a 61-bit rolling digest computed without `hashlib`. Cryptographic strength is a *capability a caller requires by name*, not an architectural premise |
| "A governance state is one value" | The specific defect Phase 2 replaced with six orthogonal axes |
| "Authority may be absent" | Measured false. An unconditional fallback tier the resolver constructs from a constant, unregisterable and unremovable |
| "Two guard kinds are enough" | **Measured false, and it is the core proposal.** Exactly 2 exist; N-of-M, quorum, windowed and cross-artifact rules are all inexpressible |
| "Exhaustive proof is the strongest assurance" | **False in the way that matters.** Measured: 900 vectors at 6 axes, 2,869,781,400 at 20. A structural O(edges) argument is *both* cheaper and stronger, because it does not expire as the model grows |
| "A register must be a chain" | Not fundamental. A DAG is append-only, tamper-evident, and does not fabricate an order the temporal model declares absent |

---

## 3. SUMMARY

| ID | Constraint | Handled by | Open action |
|---|---|---|---|
| C-01 | Only encodable things can be governed | refusal, not fallback | declare proxy relationships as lossy transformations |
| C-02 | Widening the vocabulary invalidates prior records | reported, not auto-filled | **amend Ω∞ Rule 9** |
| C-03 | Distributed order is chosen, not recovered | CONCURRENT ≠ INCOMPARABLE; no `<`; no frame arithmetic | **register must be a DAG — decide before building** |
| C-04 | Meaning cannot be fully mechanised | three-valued invariants; unchecked population counted | ratchet the unexecutable count |
| C-05 | The implementation is Python | contracts are ≤4 declarative methods | emit language-neutral schemas |

**Five fundamental constraints. Four carry an open action; none of the four is a removal.**

Two of the five are corrections to the directive rather than to the code (C-02 amends Rule 9's success
chain; C-05 distinguishes a language-neutral architecture from a language-free artifact). One has a
deadline (C-03: the register's shape must be decided while the module still does not exist). One is
mitigated only by a ratchet and not by a fix (C-04).

**This is the honest ceiling.** Ω∞ readiness is not blocked by these five — they are the shape of the
world, and an architecture that states them is more trustworthy than one that does not. Ω∞ readiness is
blocked by the five BLOCKING assumptions and two CRITICAL ones in Deliverable 1, which are work.
