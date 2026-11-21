# UCOS Ω∞ — PHASE Ω∞-A, DELIVERABLE 7
## Architectural Core Proposal

**AUTHORITY = NONE (DERIVED TRUTH).** A proposal. Nothing here is built, certified, sealed or wired into
any gate. It is the design that Deliverables 1–6 argue for, stated so it can be refused.

---

## 1. THE ONE-PARAGRAPH PROPOSAL

The Ω∞ core is **five mechanisms and nothing else**: a *declaration* (something is registered, by an
authority, with a schema), a *capability* (what may be asked of it), a *guard* (a condition on a
transition), a *relation* (how two values stand), and a *fingerprint* (an identity under a named
encoding). Every governance concept the system will ever hold is expressed as a composition of those
five. **No sixth mechanism, and no privileged instance of any of the five.** Time is a declaration.
Storage is a declaration. Certification is a set of guards. A contradiction is a relation that fails a
guard. The architecture's completeness claim is not "it supports everything" — it is "it has five
extension points and no sixth kind of thing needs one".

---

## 2. WHAT THE AUDIT PROVED ABOUT THE CURRENT CORE

Four mechanisms already exist and are measured to work; **one is missing, and its absence accounts for
four of the ten failed Rule 8 cases.**

| Mechanism | Present? | Evidence |
|---|---|---|
| Declaration | **yes** | 15th reference domain, 7th governance axis, 8th authority tier, new frame, scale, relation, ordering, clock, calendar, codec, transformation — 11 kinds, runtime, zero source edits |
| Capability | **yes** | `CapabilityRegistry` + `CapabilitySet.require`/`refuse`. Resolution by capability, never by name |
| Relation | **yes** | `Relation` with `decided`/`ordered`/`coincident`/`inverse`; a registered 6th relation verified by unchanged code |
| Fingerprint | **yes** | `Encoding` required with no default; pipeline exercised under a non-JSON codec and a non-SHA-256 digest |
| **Guard** | **NO** | **Measured: exactly 2 hardcoded guard kinds.** This is the gap |

**The proposal is therefore not a new architecture.** It is: promote guards to the same status the other
four already have, add the one property none of the five currently has (identity of the vocabulary
itself), and replace one proof method.

---

## 3. THE FIVE MECHANISMS

### 3.1 Declaration — exists, keep

```
Declaration = (name, authority, schema, invariants, provenance, capabilities, transformations)
```

Invariants that must hold and currently do:
- **No registry branches on a member name.** Measured: `DomainRegistry` cannot distinguish a shipped
  domain from a registered one.
- **Authority is never empty.** Enforced in `__post_init__`, not by convention.
- **Open to extension, closed to redefinition.** One name with two meanings is refused, because a rule
  requiring that name would otherwise be silently satisfied by something else.
- **The vocabulary set is derived, never held twice.** `StateRegistry.axes()` is computed from the
  declared states — the fix for the `AXES` closed list found in this session's own code.

**One property to add: `digest()`.** See §4.

### 3.2 Capability — exists, keep

The load-bearing detail is that `CapabilitySet` has **both** `require` and `refuse`. `refuse` is not
symmetry for its own sake: an append-only register must reject storage declaring `MUTABLE`, and
expressing that as `not supports(MUTABLE)` would pass for a provider that never declared either way —
turning "unknown" into "safe". That asymmetry is the whole reason capability declaration is honest rather
than decorative.

### 3.3 Guard — **the missing mechanism, and the core of this proposal**

```
Guard:
    identifier() -> name
    describes()  -> statement            # language-neutral, for Rule 6
    evaluate(subject, status, context) -> (permitted: bool, reason: Justification | None)
```

`blocked_by` and `requires_reason` become **two registered guards among many**. Then:

| Governance model | Today | With guards |
|---|---|---|
| "blocked while UNKNOWN" | built in | `StateExclusionGuard` — a registration |
| "requires a written reason" | built in | `JustificationGuard` — a registration |
| "requires 3 of 5 approvals" | **source edit** | `QuorumGuard` — a registration |
| "requires a federation quorum" | **source edit** | `FederationQuorumGuard` — a registration |
| "only within a declared window" | **source edit** | `TemporalWindowGuard` — a registration |
| "conditional on another artifact's state" | **source edit** | `PeerStateGuard` — a registration |

**Why this is the core and not a feature.** Certification, contradiction resolution and state transition
are all *the same operation*: check conditions, permit or refuse, record why. Today they would be three
subsystems with three condition vocabularies. With guards they are one mechanism with three registries of
guards, and an unknown governance model that arrives tomorrow extends all three at once.

**Closes:** G-01, G-02, X-01, X-02, A-09, A-10, B-10, B-11. **Also makes A-11 impossible** — certification
inputs become registered guards rather than a fixed set of seven, so the barrier is designed out before
the module exists.

### 3.4 Relation — exists, generalise slightly

Add `properties: Mapping[str, object]` interpreted by the declaring strategy, so a weighted or
degree-valued ordering needs no source edit. **Recorded honestly:** the `QuantumOrdering` case passed
because superposition happened to fit three booleans, not because the mechanism is general (G-04).

### 3.5 Fingerprint — exists, keep

`Encoding` is a required argument with no default at every byte-producing site. That is what makes "the
architecture does not require JSON" a measurement rather than an intention: there is nothing to fall back
to. **Keep the no-default discipline** — it is the single most effective anti-assumption device found in
this work, and it cost one argument per call site.

---

## 4. THE ONE PROPERTY NONE OF THE FIVE HAS: VOCABULARY IDENTITY

The most severe open finding (A-14 / G-10 / X-05 / B-07). Every registry is an in-process object with no
digest, no version and no comparison operator, so **two nodes can validate the same record differently
and both report success.**

```
VocabularyRegistry:
    digest(encoding) -> fingerprint      # content identity of the vocabulary itself
    declared_by()    -> authority        # who answers for this vocabulary
    diverges_from(peer) -> tuple[Divergence, ...]
```

Three consequences, each closing a separate finding:

1. **The vocabulary becomes an artifact.** It gets a governance status, an authority chain and a
   certification disposition, governed by the same six axes as anything else. A vocabulary nobody answers
   for is exactly the silent governance state Phase 2 exists to eliminate — currently present in the
   mechanism that eliminates it.
2. **Divergence becomes a contradiction class.** `VOCABULARY_CONTRADICTION` joins the ten designed
   classes. Two civilizations disagreeing about what `GOVERNED` means becomes a *reportable finding*
   rather than two successful validations.
3. **Identifiers become `(authority, identifier)`.** Closes A-20 / X-12 / B-14: two deployments minting
   `Ω²-S-37` is then itself a detectable contradiction rather than silent semantic divergence.

---

## 5. TWO METHOD CHANGES, NOT MECHANISM CHANGES

### 5.1 Assurance must not be exponential in the extension mechanism

**Measured: 6 axes → 900 vectors; 20 → 2,869,781,400.** Registering axes is the advertised extension
mechanism, so using the architecture correctly destroys its strongest assurance — silently, because the
proof becomes unrunnable rather than wrong.

Replace enumeration with a structural argument, O(edges) and independent of axis count:

> `UNKNOWN` never certifies **because** (a) no declared edge targets `UNKNOWN`, so the unknown population
> only ever drains, and (b) every edge targeting `CERTIFIED` names `UNKNOWN` in its `blocked_by`.
> Therefore no reachable vector holds both. Both facts are single passes over the edge set.

Keep enumeration as a cross-check at small sizes, and **add a guard that refuses to claim an exhaustive
proof above a declared state-space size** — so the claim expires rather than quietly becoming false.

### 5.2 The register must be a DAG, not a chain

A hash chain requires each entry to name exactly one predecessor, imposing a total order on records whose
coordinates the same architecture declares `CONCURRENT` (A-24 / X-11). Two federated observers could not
both append.

Merkle **DAG**: an entry names *all* predecessors it observed; concurrent appends produce siblings;
`verify` becomes a DAG traversal; total order becomes a **projection a caller may request**, never a
property the register asserts. **This is free to fix today and expensive after the register is written** —
the module does not exist yet. It is the only item in this proposal with a deadline.

---

## 6. WHAT THIS PROPOSAL DELIBERATELY DOES NOT DO

| Not proposed | Why |
|---|---|
| Rewrite the 264 legacy enumerations | Phase 2's constraint is adapters, not rewrites. Deliverable 4 triages them: ~60 are true invariants and should stay closed |
| Open every closed list | Wrong goal. `RATCHET_KINDS` is *correctly* closed and says why. The standard proposed is that **every closed list carry a written argument for its closedness**, and that the absence of the argument is the finding |
| Move the repository boundary | 42 git sites and the whole verification plan sit inside it. Phase 1 built the seam; migrating consumers is a programme, not a core change |
| Eliminate the encodability boundary | Cannot be done. See Deliverable 8 |
| Add a sixth mechanism | The audit found no concept requiring one. If a future finding does, that is the signal this core is wrong |

---

## 7. FALSIFICATION CRITERIA

A proposal that cannot fail is not a proposal. This core is **wrong** if any of the following is
demonstrated:

1. A governance rule that is not expressible as a composition of guards.
2. A governance concept that needs a sixth mechanism rather than a declaration of an existing one.
3. A reference domain whose values cannot be given a fingerprint under *any* registered encoding —
   which would show the encodability boundary is not merely fundamental but *mis-placed*.
4. A relation between values that is neither a `Relation` nor a `Transformation`.
5. Two deployments that agree on every vocabulary digest and still disagree about a record's validity —
   which would show vocabulary identity is insufficient for consensus.

**Ranked by likelihood of actually occurring: 3, then 1.** (3) is the one to watch: non-software artifacts
are governed by proxy today, and if the proxy relationship turns out not to be expressible as a declared
lossy transformation, the core needs a sixth mechanism for *physical reference* — and this proposal would
be wrong in the way that matters.
