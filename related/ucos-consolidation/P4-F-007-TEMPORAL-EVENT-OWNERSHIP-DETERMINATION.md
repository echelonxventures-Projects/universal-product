# P4-F-007 (remainder) — TEMPORAL EVENT OWNERSHIP DETERMINATION

**Checkpoint:** `03179308` (integration/recovery-001)
**Compiled:** 2026-08-22
**Phase:** 7C — **read-only analysis.** Nothing removed, nothing changed.
**Finding under analysis:** `PHASE-4-CAPABILITY-GAP-MATRIX.md:176` — *"The temporal model has no call site outside its own package; a weaker rival `TemporalEvent` competes at `engine/uckp/values.py:269-293`."*
**Work package:** `WP-UCDA-028`, sub-obligation *P4-F-007 remainder*, owner **`engine/temporal` owner (CMG-000002)**.

---

## 1 — Status of the finding's two clauses

| Clause | Status | Evidence |
|---|---|---|
| "no call site outside its own package" | **FALSE since `DEC-ADR-0015`** | `engine/knowledge/ukip/contracts.py:50`, `engine/knowledge/ukip/relationships.py:43-44` import `engine.temporal.coordinate` / `.operations` directly. Already recorded in `adr/0019`. |
| "a weaker rival `TemporalEvent` competes" | **still present** — this report adjudicates it | `engine/uckp/values.py:269-293`, re-read this checkpoint |

---

## 2 — The two models, read side by side

### 2.1 `engine.temporal` — the canonical model (CMG-000002)

| Type | Location | What it is |
|---|---|---|
| `ReferenceSystem` | `coordinate.py:68` | a named time system |
| `TemporalCoordinate` | `coordinate.py:170` | a **reference-system-qualified** point in time, with `Precision`, `Provenance`, `Conversion` |
| `ValidityPeriod` | `coordinate.py:258` | an interval over coordinates |
| `Ordering` | `coordinate.py:44` | includes **`INCOMPARABLE`** |
| `TemporalRegistry` / `convert` / `compare` | `operations.py` | cross-system comparison that **fails closed** rather than assuming a shared timeline |
| `TemporalFacet` (8 members) | `facets.py:32` | `CREATION, EXISTENCE, VALIDITY, EVOLUTION, CERTIFICATION, RETIREMENT, ARCHIVE, RESTORATION` |
| `TemporalRecord` | `facets.py:69` | keyed by **`subject_identity`** (a Universal Identity, explicitly *"not a path… so the temporal history of an object must survive the object moving"*); holds `(facet_name, TemporalCoordinate)` pairs plus a `ValidityPeriod`; enforces facet precedence and rejects duplicate facets |

**The question this model answers: _when did this happen, in which reference frame, and is
that comparable to another frame?_**

### 2.2 `engine.uckp.values.TemporalEvent` — the alleged rival

```
@dataclass(frozen=True, slots=True)
class TemporalEvent:
    """Something that happened to an object, ordered by constitutional state (Facet 11)."""
    sequence: int
    event: str
    state_id: str = ""
    at: str = TIMELESS          # TIMELESS = "timeless"
```

Four fields. `to_dict` / `from_dict`. No methods, no comparison, no registry, no frame.

**Every construction site — three, all in `engine/uckp/ucko.py`:**

| Site | Construction |
|---|---|
| `ucko.py:245` (mint) | `TemporalEvent(sequence=0, event=f"minted:{lifecycle}")` |
| `ucko.py:413` (`transition_to`) | `TemporalEvent(sequence=len(self.temporal_history), event=f"transition:{self.lifecycle}->{stage}", state_id=state_id)` |
| `ucko.py:568` (`from_dict`) | reconstruction from a record |

**`at` is never assigned at any construction site.** It is `TIMELESS` in every object this
codebase creates. Ordering is carried entirely by `sequence` — a per-object ordinal — and
attribution by `state_id`, a **constitutional state**, not a clock reading.

### 2.3 Coupling — measured

`grep` for `engine.temporal` across `engine/uckp/`: **zero hits.** The two modules do not
import each other in either direction. There is no shadowing, no re-export, no fallback path.

---

## 3 — Determination

### **B — valid specialized projection. Not a duplicate authority.**

The two types are not competing implementations of one concept. They answer different
questions, and the difference is load-bearing:

| | `TemporalRecord` / `TemporalCoordinate` | `TemporalEvent` |
|---|---|---|
| Question | *when*, in which frame | *in what order*, within one object's own lifecycle |
| Ordering basis | reference-system coordinate, cross-frame comparison | integer `sequence`, single object scope |
| Cross-object comparable? | yes, via `convert`/`compare`, `INCOMPARABLE` when frames differ | **no, and deliberately not** |
| Frame | required — that is the point | **none — `TIMELESS`** |
| Keyed by | `subject_identity` (external) | position inside `UCKO.temporal_history` (internal) |
| Vocabulary | 8 closed `TemporalFacet` members | open `event` string (`minted:…`, `transition:A->B`) |

### 3.1 The decisive point: `TIMELESS` is REQ-22 being honoured, not a weakness

REQ-22 — *"No default temporal reference frame"* — is **CERTIFIED**, evidenced by
`TemporalCoordinate` and `compare() -> INCOMPARABLE`.

If `UCKO.temporal_history` were re-typed to `TemporalCoordinate`, then **minting an object
would require a reference system**. `UCKO`'s mint path (`ucko.py:245`) has no reference
system available and no way to obtain one. Only two outcomes exist:

- supply a default frame at mint → **directly violates REQ-22**, the exact defect
  `adr/0012-remove-residual-planetary-default.md` was written to remove; or
- fail the mint → the constitutional object model cannot create an object.

`TemporalEvent`'s `at = TIMELESS` is the third, correct answer: **record the ordinal fact
without asserting a frame.** The "weaker" model is weaker *on purpose*, and merging it into
the stronger one would regress a certified requirement.

### 3.2 Ownership is already unambiguous

| Concern | Owner |
|---|---|
| Reference-frame-qualified time, conversion, comparison, validity intervals, subject temporal records | **CMG-000002 — `engine/temporal`** |
| Per-object constitutional state-transition ordering inside a `UCKO` (Facet 11) | **UCKP Layer Zero — `engine/uckp`** |

Neither owner's registry contains the other's concept. `engine/temporal` has no
`sequence`-ordered per-object event log; `engine/uckp` has no `ReferenceSystem`,
`convert()` or `compare()`. **No duplicate authority exists to resolve.**

**Nothing is to be removed. `TemporalEvent` stays where it is, owned by `engine/uckp`.**

---

## 4 — The one real residue

Determination B closes the "rival authority" question. It does **not** close everything the
finding gestured at, and that difference is stated rather than glossed:

> **`TemporalEvent.at` is an unconstrained `str`.**

Nothing in the type, and nothing in `from_dict` (`values.py:292` —
`_text(record.get("at"), …, required=False) or TIMELESS`), prevents a record from carrying
`"2026-08-22"` — a bare, **unqualified** time value with no reference system. No current
construction site does this, and no on-disk record contains it. But the *type permits it*,
and an unqualified time value is precisely what REQ-22 exists to forbid.

That is the legitimate, narrow core of P4-F-007's second clause: not a rival authority, but
an **unbounded field** that could silently become one.

### 4.1 Recommended closure — narrow, integration-shaped, no new capability

Constrain `at` to *either* `TIMELESS` *or* a value parseable by the canonical owner's
existing primitive:

- `engine/temporal/coordinate.py:291` already provides
  `parse_qualified(qualified: str, *, authority: str) -> TemporalCoordinate`.
- A `__post_init__` validation on `TemporalEvent` that accepts `TIMELESS` and otherwise
  requires `parse_qualified` to succeed makes the field **bound** rather than open.

This is the same shape as `DEC-ADR-0015`'s fix — *integration with an existing owner's
primitive, not invention of a new one* — and it introduces the first
`engine/uckp` → `engine/temporal` edge, further retiring the finding's first clause.

**Cost:** one `__post_init__`, one import, ~3 tests. **Capability added:** none — the
constraint makes an existing invariant enforceable instead of merely intended.

**This report does not implement it.** Phase 7C is read-only, as directed.

### 4.2 Alternative, if the owner prefers zero code

Record in `values.py`'s docstring that `at` is `TIMELESS`-or-qualified by convention, and
close P4-F-007's remainder on the ownership determination alone. Honest, cheaper, and
**weaker** — a convention a future author can breach without any gate noticing. Stated so
the trade is visible; §4.1 is the recommendation.

---

## 5 — Documents carrying stale text about this finding

Not corrected by this read-only pass; listed so the correction is scheduled, not lost:

| Document | Stale claim |
|---|---|
| `PHASE-4-CAPABILITY-GAP-MATRIX.md:176` | *"no call site outside its own package"* — false since `DEC-ADR-0015` |
| `PHASE-4-CAPABILITY-GAP-MATRIX.md:176` | *"a weaker rival … competes"* — "rival" is superseded by determination B above |
| `FINAL-UNIVERSAL-INFINITE-EXPANSION-FOUNDATION-CERTIFICATION-REPORT.md:100` | *"Own decision: retire or reconcile"* — the answer is **neither**; it is a specialized projection to be **bounded** |

---

## 6 — Boundary statement

This determination is about **ownership**, made by reading both modules and all three
construction sites at checkpoint `03179308`. It does not claim `TemporalEvent` is complete,
that `engine/uckp`'s temporal handling is certified, or that §4's residue is closed. The
residue is open and named. Nothing was removed, and no ownership was reassigned.
