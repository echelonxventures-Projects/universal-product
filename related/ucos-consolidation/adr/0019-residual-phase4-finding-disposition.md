# ADR-0019: Formal disposition of every PHASE-4 capability finding not closed by ADR-0015/0016

| Field | Value |
|-------|-------|
| Status | Accepted |
| Date | 2026-08-21 |
| Deciders | Constitutional Authority · UCOS Ω∞ (directive: "ABSOLUTE UNIVERSAL EXPANSION CLOSURE DIRECTIVE", Phase 3) |
| Technology Constitution refs | `PHASE-4-CAPABILITY-GAP-MATRIX.md`, `adr/0013`, `adr/0015`, `adr/0016` |
| Supersedes | none |

## Context

Phase 3 of the closure directive requires every prior finding to end this session either **implemented, tested and certified**, or **explicitly closed by constitutional decision** — never left as informal prose ("referred") with no governance record. Ten findings were catalogued in `PHASE-4-CAPABILITY-GAP-MATRIX.md`. Their status, re-verified against current code at this checkpoint rather than assumed from the matrix's original text:

**Correction to the directive's own labeling, stated plainly rather than silently followed:** the directive names *"P4-F-004 knowledge confidence"* — this is incorrect. `P4-F-003` is knowledge confidence (closed by `ADR-0016`); `P4-F-004` is `KnowledgeStore.save()`'s destructive whole-file rewrite, a distinct finding, still open. This decision dispositions the finding by its correct number, not the directive's mislabel, because acting on the wrong finding under the right name would itself be an undocumented assumption.

| Finding | Owner | Status at this checkpoint |
|---|---|---|
| `P4-F-001` | CEU-001 | Open — `_supersessions` still mutated in place, `engine/ceu/existence.py:531-534` (re-read, unchanged) |
| `P4-F-002` | UCKP ART-07 | **CLOSED** — `DEC-ADR-0015`, IMPLEMENTED |
| `P4-F-003` | UKDA/UKIP | **CLOSED** — `DEC-ADR-0016`, IMPLEMENTED |
| `P4-F-004` | UKDA | Open — re-verified this session (Task 3): `engine/knowledge/store.py:175-180` (`replace_object`) and `:287-293` (`save`) unchanged |
| `P4-F-005` | UCDA | Open — `00-MASTER/UCDA-000001/ucda-decisions.json`'s own decisions carry a mutable `stage`/`disposition` field with no supersession chain; this session's own `DEC-ADR-0017`/`DEC-ADR-0018` updates were in-place edits, which is itself a live instance of this finding |
| `P4-F-006` | UKIP, certification owners | Open — `engine/knowledge/ukip/provenance.py`'s chains remain in-memory-only |
| `P4-F-007` | engine/temporal owner | **PARTIALLY CLOSED** — the "no call site outside its own package" clause is now false: `engine/knowledge/ukip/relationships.py` and its tests import and call `engine.temporal.coordinate`/`operations` directly (`ADR-0015`). The second clause — a rival `TemporalEvent` at `engine/uckp/values.py:269-293` — re-read this checkpoint and confirmed still present, still open |
| `P4-F-008` | UAUE | Open — no learning object model or evolution transaction object exists in code, re-confirmed by absence (no such class found in `engine/uaue/` or `engine/uckp/`) |
| `P4-F-009` | UCXI | **PARTIALLY CLOSED** — `engine/knowledge/ukip/confidence.py` (`ADR-0016`) gives `ContextRegistry` a real per-subject binding call site for the `KNOWLEDGE` context kind specifically. The broader claim — CEU's `bind-context` remains a journal action with no corpus record, and `engine/lineage/memory-layers.json`'s "context" layer still resolves via the corpus artifact register rather than UCXI for every *other* context kind — re-read this checkpoint and confirmed still true |
| `P4-F-010` | UCL-000001, ACEE-000001 | **CLOSED** — `DEC-ADR-0014`, IMPLEMENTED, retightened the ratchet to the measured value. Its carved-out sub-finding, the 192-document corpus-registration drift (`UCL-F-006`'s wider population), remains explicitly out of scope — see below |

**Also re-opened, named honestly rather than left implicit:**
- The 192-document `CORPUS_REGISTRATION` population (`UMB-IMP-001` authority) is **distinct** from the 26 objects `ADR-0017`/`ADR-0018` minted (`UGA-001` authority, a different identity plane for non-document objects). `ADR-0017` explicitly excluded it. It remains open, unregistered, and is not dispositioned by this decision — a different owner (`REG-AUTO-001` acting as `UMB-IMP-001`, via `00-BOOK/tools/register.sh (ukb.py build --mint)`) must act, and that action mints permanent corpus-document identities at a scale (192, not 26) this session has not enumerated object-by-object the way `ADR-0017` did.
- `00-CMG/tools/cmg-gate.sh`'s own measured output (re-run this checkpoint): 9 gaps recorded, 7 open questions, 1 vacancy, standing `READY-PROVISIONAL`. These are pre-existing meta-constitutional housekeeping items, not part of the principle set this conversation has discussed (Tasks 2-5's sixteen certified principles); they are named here so this decision does not imply they were investigated, and left to their own owner's cadence.
- `engine.infinite_scope.gate`'s own disclosure, `ISD-G-01`: one enumeration disclosed as unintentionally closed. Pre-existing, not part of this session's discussed scope, named rather than hidden.

## Decision

We **formally close** `P4-F-002`, `P4-F-003`, and `P4-F-010` as already IMPLEMENTED (no new action; confirmed by re-verification above).

We **register** the six still-open findings — `P4-F-001`, `P4-F-004`, `P4-F-005`, `P4-F-006`, `P4-F-007` (remainder), `P4-F-008`, `P4-F-009` (remainder) — as `WP-UCDA-028`, one consolidated work package carrying seven distinct, individually-acceptance-bound obligations (one per finding), disposition `REGISTERED-AS-IMPLEMENTATION-WORK-PACKAGE`. This is a **formal governance closure of the finding as a tracked, owned obligation** — it is not a claim of implementation, and this decision does not represent it as one. Per `CEP-002 Art 28.13(c)`, this disposition is lawful precisely because it is agreed, owned, routed and acceptance-bound rather than left as prose.

We explicitly **decline** to implement all seven in this pass. Each is a substantive, independent architectural change against a different owner (`CEU-001`, `UKDA`, `UCDA`, `UKIP`, `engine/temporal`, `UAUE`, `UCXI`) — the same category of work `ADR-0015` and `ADR-0016` each took as a dedicated, individually-tested, individually-registered decision. Batching seven such changes into one untested implementation to force a COMPLETE status would itself violate the closure directive's own rule against converting a referred item into a completed one by assertion rather than evidence.

We **name, rather than silently absorb**, the two out-of-scope items above (192-document corpus registration; `CMG`/`ISD` pre-existing housekeeping): disclosure is the closure mechanism the directive requires for anything not fully resolved, and silence would be the actual violation.

## Consequences

Positive: every finding this session touched or discovered now carries an explicit governance record and a named status — `CLOSED`, `PARTIALLY CLOSED` (with the remaining clause stated), or `REGISTERED-AS-IMPLEMENTATION-WORK-PACKAGE` with a real owner and acceptance condition. Nothing remains as informal prose only.

Neutral: seven findings remain unimplemented; this decision changes their governance status, not their code state.

Negative: `WP-UCDA-028` is a large work package (seven sub-obligations); a future session executing it should likely split it into seven independent decisions at implementation time, the same granularity `ADR-0015`/`ADR-0016` used.

Reversible: this decision registers no mutation of source; reverting it removes only the governance record, not any code change.

## Compliance

- [x] Non-contradiction with the constitutional/EES corpus asserted (CC-02).
- [x] Rollback / migration path recorded (CC-04) — no code changed; N/A beyond removing the record.
- [x] Traceability links to affected artifacts recorded (CC-05) — `PHASE-4-CAPABILITY-GAP-MATRIX.md`, `adr/0013`, `adr/0014`, `adr/0015`, `adr/0016`.
- [x] No secret material embedded (SEC-04).
