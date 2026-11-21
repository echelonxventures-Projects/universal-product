# UCOS Ω∞ — PHASE Ω∞-A, DELIVERABLE 9
## Roadmap for Removing the Highest-Risk Ceilings

**AUTHORITY = NONE (DERIVED TRUTH).** A proposed sequence. Nothing here is authorised, scheduled, certified
or sealed. No ratchet is advanced and no active process is modified by this document.

**HOW THE ORDER WAS CHOSEN.** Not by severity. By **cost of delay** — how much more expensive each fix
becomes if the next foundation layer is built first. Two items cost nothing today and a rewrite later.

---

## RANKING BY COST OF DELAY

| Rank | Ceiling | Cost now | Cost after the next layer is built | Why |
|---|---|---|---|---|
| **1** | Register is a chain, not a DAG (C-03, A-24, X-11) | **zero** | rewrite + record migration | `registry.py` does not exist yet |
| **2** | Certification has a fixed input set (A-11) | **zero** | rewrite of the decision function | `certification.py` does not exist yet |
| **3** | Guards are hardcoded (A-10, G-01) | small | grows with every consumer | 3 subsystems will each grow a condition vocabulary |
| **4** | Proof is exponential in axis count (A-16, G-09) | small | **claim silently expires** | fails without an error |
| **5** | No vocabulary identity (A-14, G-10) | moderate | moderate | independent of build order |
| **6** | No storage provider (B-02, G-05) | moderate | moderate | independent |
| **7** | No emitted schema (B-03, G-06) | small | small | independent |
| **8** | Census is not mergeable (A-15, G-07) | moderate | grows with data | interface-compatible |
| **9** | Binary transformations (A-21, G-03) | moderate | moderate | independent |

**Steps 1 and 2 are free today and expensive in any other order.** They are the only items with a
deadline, and the deadline is "before the next module is written".

---

## STEP 1 — Decide the register's shape before writing it
**Closes:** C-03 exposure · A-24 · X-11 · G-09(register) — **cost of delay: a rewrite**

The Phase 2 design specifies a hash-chained `GovernanceRegistry`. A chain requires each entry to name
exactly one predecessor, which imposes a total order on records whose coordinates the same architecture
declares `CONCURRENT`. Two federated observers could not both append.

Build a **Merkle DAG** instead:

- an entry names *all* predecessors it observed;
- concurrent appends produce siblings rather than a conflict;
- `verify()` is a DAG traversal; tamper evidence is unchanged;
- **total order becomes a projection a caller may request, never a property the register asserts.**

Exit criterion: two independent writers append concurrently, the DAG verifies, and a requested total-order
projection is *labelled as a projection* in the record it produces.

---

## STEP 2 — Make certification inputs a registry before writing it
**Closes:** A-11 · X-01(certification) — **cost of delay: a rewrite**

The design names seven certification inputs. Seven fixed inputs is a closed list, and a domain whose
certification depends on an eighth would need a source edit — the barrier reappearing inside the module
built to remove barriers.

Express each input as a registered **guard** (Step 3), each declaring `required` or `conditional`. The
decision function quantifies over the registry and never over a tuple.

Exit criterion: an eighth certification input is registered at runtime, participates in a decision, and
appears in the decision's explanation — with zero source edits.

---

## STEP 3 — Promote guards to a registered mechanism
**Closes:** A-09 · A-10 · G-01 · G-02 · X-01 · X-02 · B-10 · B-11

```
Guard:
    identifier() -> name
    describes()  -> statement                       # language-neutral, for Rule 6
    evaluate(subject, status, context) -> (bool, Justification | None)
```

`blocked_by` and `requires_reason` become two registrations. `reason: str` becomes a `Justification` value
in a registered domain with a declared schema and invariants — closing the measured defect that edge
Ω²-S-12 accepted `reason="x"`.

**Why this is one step and not two:** state transition, certification and contradiction resolution are the
same operation — check conditions, permit or refuse, record why. One mechanism serves all three, and an
unknown governance model arriving tomorrow extends all three at once.

Exit criterion: a `QuorumGuard` ("3 of 5 named approvers") is registered at runtime and refuses a
transition, naming the shortfall — with zero source edits.

---

## STEP 4 — Replace the exhaustive proof with a structural argument
**Closes:** A-16 · B-09 · X-07 · G-09 — **the only ceiling that fails silently**

Measured: **6 axes → 900 vectors; 7 → 1,800; 10 → 48,600; 20 → 2,869,781,400.** Registering axes is the
advertised extension mechanism, so using the architecture as designed makes its strongest assurance
unrunnable — without an error, a failing test or a migration prompt.

Prove the invariant structurally, in O(edges), independent of axis count:

> `UNKNOWN` never certifies **because** (a) no declared edge targets `UNKNOWN`, so the unknown population
> only ever drains, and (b) every edge targeting `CERTIFIED` names `UNKNOWN` in its `blocked_by`.

Keep enumeration as a cross-check at small sizes. **And add a guard that refuses to *claim* an exhaustive
proof above a declared state-space size**, so the claim expires loudly instead of quietly.

Exit criterion: the invariant is proven with 20 registered axes in bounded time, and the exhaustive
cross-check *declines* with a stated reason rather than hanging.

---

## STEP 5 — Give vocabularies identity
**Closes:** A-14 · A-20 · B-07 · B-14 · X-05 · X-12 · G-10 — **highest severity, no deadline**

Today every registry is an in-process object with no digest, no version and no comparison operator. Two
nodes can validate the same record differently and **both report success.**

```
digest(encoding) -> fingerprint        # content identity of the vocabulary itself
declared_by()    -> authority          # who answers for this vocabulary
diverges_from(peer) -> tuple[Divergence, ...]
```

Then: the vocabulary becomes an artifact governed by the same six axes as anything else; identifiers become
`(authority, identifier)`; and **vocabulary divergence becomes a contradiction class** rather than two
successful validations.

Exit criterion: two registries differing by one declaration report a `VOCABULARY_CONTRADICTION` naming the
divergent declaration and both authorities.

---

## STEP 6 — Storage as a provider
**Closes:** B-02 · G-05 · Rule 7

The Phase 2 tree imports no filesystem module (measured: 0) and reduces every record to primitives. That is
storage-*neutral*, not storage-*capable*: no `StorageProvider` protocol, no adapter, no append-only store.

Add the protocol, an in-memory reference implementation, and one adapter. The capability layer already has
`APPEND_ONLY` and `MUTABLE`, and `CapabilitySet.refuse` already exists — so a register can **reject
storage declaring `MUTABLE`** before any damage, rather than discovering an overwrite in an audit.

Exit criterion: the register writes to two providers with different capability declarations, and refuses a
`MUTABLE` one by name.

---

## STEP 7 — Emit the contracts
**Closes:** B-03 · G-06 · Rule 6 (consumable)

Every protocol is ≤4 methods over names, integers and mappings, and `Schema`/`Field`/`Invariant`/
`Capability` are already declarative values. Walk them and emit language-neutral contract documents.

Exit criterion: the emitted schema is sufficient for an implementer who has not read the Python source.
The residue — that this artifact is Python — is C-05 and is not removable.

---

## STEP 8 — Mergeable census
**Closes:** A-15 · B-08 · G-07 · Rule 9 (indefinite growth)

Every census is a single-pass full materialisation. Express each as a commutative, mergeable monoid so
partial censuses compose. No interface break.

Exit criterion: a census computed over three disjoint shards and merged equals the census over the union.

---

## STEP 9 — N-ary transformations
**Closes:** A-21 · B-12 · X-03 · G-03

`sources: tuple[str, ...] -> target`; `path` becomes hypergraph resolution. Removes the need to invent
composite intermediate domains, which is itself a schema modification.

Exit criterion: "position **and** time **and** frame → velocity" is declared as one transformation, with
one authority and one loss statement.

---

## NOT ON THIS ROADMAP, DELIBERATELY

| Item | Reason |
|---|---|
| Converting the 264 legacy enumerations | Deliverable 4 triages them: **~60 are true invariants and should stay closed.** The recommendation is not conversion but that **every closed list carry a written argument for its closedness** — `RATCHET_KINDS` is the standard, and the absence of the argument is the finding |
| Moving the repository boundary | 42 git sites and the entire verification plan sit inside it. Phase 1 built the seam; migrating consumers is a programme |
| Rewriting Ω-1, UCI, coverage governance, ratchets, certification flows | Forbidden by every directive in this sequence, and correctly so |
| Removing C-01 (encodability) | Cannot be done. Attached action is to declare proxy relationships as lossy transformations |
| Wiring any Phase 2 code into `verify.sh` or CI | Forbidden. No gate stage, no seal, no ratchet advancement |

---

## WHAT WOULD MAKE THIS ROADMAP WRONG

1. If a governance rule is found that guards cannot express, Step 3 is insufficient and the core proposal
   (Deliverable 7) needs a sixth mechanism.
2. If two deployments agree on every vocabulary digest and still disagree about a record's validity, Step 5
   is insufficient and consensus needs more than identity.
3. If a non-encodable artifact's proxy relationship turns out not to be expressible as a declared lossy
   transformation, C-01 is *mis-placed* rather than merely fundamental — and that is the finding most
   likely to actually occur.

---

## STATUS

**Phase Ω∞-A is discovery and it is complete.** Nine registers delivered. The success criterion was that
every remaining architectural ceiling be explicit, measurable, attributable and governable:

| Property | How it is met |
|---|---|
| **Explicit** | 26 assumptions, 14 boundaries, 20 barriers, 12 closed-world dependencies, 10 gaps, 5 fundamental constraints |
| **Measurable** | Every entry carries a measurement or says it was not measured. 2,178 files walked; 264 enums / 1,372 members counted by tree; 11 registration kinds exercised at runtime; state-space growth measured to 20 axes |
| **Attributable** | Every boundary carries an origin; every assumption carries a location |
| **Governable** | Each has a classification, a severity and a named replacement strategy; the roadmap sequences them by cost of delay |

**Ω∞ readiness is NOT claimed.** Five BLOCKING and two CRITICAL assumptions are open. Two of them would be
built *into* the next foundation layer if it were written as currently designed, which is why Steps 1 and 2
precede everything else.

**The finding that most justifies this phase having happened:** the audit's first target was code written
in this same session *specifically to eliminate hardcoded assumptions*, and it found five —
`json`/`sha256` as requirements, `tuple[int, ...]` assuming numeric measurement, a rule table keyed 1–7, a
closed axis list quantified over inside a domain model, and a default that reinstated total ordering. None
was an enum. None would have been caught by review. **The two most severe findings in the whole audit
(proof tractability, vocabulary consensus) were in neither the directive's thirty assumption categories nor
its nine readiness dimensions** — which is the strongest available evidence for the instruction not to treat
any such list, including these nine registers, as complete.
