# 55 — Pipeline Evolution Strategy (Phase-004)

| Field | Value |
|-------|-------|
| PROGRAM | UAKOS-CLOSURE-002 · PHASE-004 |
| STATUS | PLANNING / GOVERNANCE — no implementation artifact modified |
| AUTHORITY | NONE — DERIVED TRUTH |
| BASELINE | HEAD `b67a720` |

> How future phases extend the pipeline without violating Knowledge Once, Repository Truth, Fail-Closed governance, Canonical Authority, or Backward Compatibility.

## 1. The extension pattern (proven by Phase-002)

A new phase SHALL:
1. **Consume** the prior phase's JSON model **read-only** (e.g. Phase-002 reads `closure.json`) — no re-extraction (**Knowledge Once**).
2. **Reuse** authoritative stores (`relationships.json`, registries, `MCP-006`) — never fork them (**Canonical Authority**).
3. **Emit** its own numbered outputs + its own JSON model in its own number band; **never rename/delete/move** upstream artifacts (**Backward Compatibility**, concurrency rule).
4. **Be deterministic + fail-closed** (`UCKO-PRIN-0005`, `TRACK-001`).
5. **Write nothing to Repository Truth** — only S0 (ukb) does (**Repository Truth**).

## 2. Number-band allocation (avoids collisions)

| Band | Phase | Owner |
|------|-------|-------|
| 01–19 | Phase-001 (EKI + ukb-grounded determination) | `closure_engine.py` + ukb pass |
| 20–35 | Phase-002 (graph reconciliation) | `phase2_engine.py` |
| 36–48 | Phase-003 (reserved) | future |
| 49–57 | Phase-004 (governance/ratification) | this set |
| 58+ | future phases | allocate a new band per phase |

Each phase owns a disjoint band ⇒ concurrent phases never collide.

## 3. Compatibility governance

- The `closure.json` interface is versioned (contract v1). **Additive** fields are backward-compatible. **Renames/removals/retyping** require a **major version bump** + downstream sign-off.
- New disposition states or new gap classes require a version bump (they change consumer semantics).
- A deprecation window: old + new fields coexist for ≥1 release before removal.

## 4. What evolution may NOT do

- May not introduce a second repository engine, registry, ID system, graph, or traceability store.
- May not make any phase write Repository Truth directly.
- May not weaken fail-closed (no phase may assert closure the evidence does not support).
- May not re-extract concepts a prior phase already produced (must reuse the model).

## 5. Retirement / supersession

A phase is retired via a `UKDA` decision record (supersession rule: superseded only by a ratified successor preserving Knowledge Once). Retired outputs are archived (not deleted while any consumer remains), following the `Lifecycle` supersession path (`ratified→…→superseded→archived→historical`).

---

*END — 55 · Pipeline Evolution · AUTHORITY = NONE.*
