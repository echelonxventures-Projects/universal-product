# UNIVERSAL EVOLUTION MODEL DETERMINATION

> **Mission:** UCOS Ω∞ Universal Identity Capability Completion — Workstream 8 (completing WS6)
> **Baseline:** `5eb1a704` · **Branch:** `integration/recovery-001` · **Date:** 2026-08-17
> **Mode:** Determination. Reconciles the requested evolution fields against declared refusals.
> **Authority:** NONE (DERIVED TRUTH). Legislates no evolution model.

---

## 1. Executive determination

**The required shape is already satisfied, and two of the originally requested fields must NOT be added.**

The requirement is:

```
Identity
 |
 +-- Evolution 1
 +-- Evolution 2
 +-- Evolution ∞
```

`engine/registry/universal/identity.py::deterministic_id(kind, namespace, natural_key)` is **explicitly version-independent**: every version of an artifact derives the same identifier. `engine/object_birth/birth.py::evolve()` re-derives identity from namespace and local name and **refuses** if the result differs. So identity stability across unbounded evolution is enforced by recomputation, not asserted.

Two requested fields from the earlier framing are refused, because the located owner refuses them in its own declaration:

| Requested | Determination | Declared refusal |
|---|---|---|
| **Evolution Registry** | **REFUSED** | `uaue-evolution.json` `identity.basis`: "Nothing is minted, no corpus serial is consumed and **no registry is written**, so this register cannot become a second identity authority." Adding one would breach `CAA-INV-04`. |
| **Rollback Point** | **REFUSED** | `plan_contract.rollback_strategy`: "a mutation that fails any gateway stage never reaches truth, so the prior state is not restored but never left… **this register records no delete path and no out-of-band revert**." |

Refusing these is not a gap. An evolution registry would be a second identity authority; a rollback point would be an out-of-band mutation path around the constitutional gateway. Both are prohibited by the architecture the steering also instructs me not to compete with.

---

## 2. What evolution changes, and what it never changes

**Never changes: identity.** Identity inputs are exactly two — namespace and local name (`uobc-birth-contract.json` `identity_inputs`). Owner, state, timestamp, context, parent, path and content are all *recorded* and none is an identity input. That is what makes the invariant provable rather than aspirational.

**Changes under the same identity:**

| Dimension | Owner | Mechanism |
|---|---|---|
| **State** | `engine/knowledge/model.py` `Lifecycle` | 10 stages with an enforced transition graph; no "frozen" terminal state |
| **Capability** | `engine/uaue/` | `EvolutionObject` chain, 15 Article-14 stages, non-terminal |
| **Implementation** | `engine/uckp/evolution.py` | Article-14 `implementation` stage |
| **Evidence** | `engine/uicm/`, CMG-000011 | append-only observations |
| **Understanding** | `engine/uaue/understanding.py` | `EvolutionUnderstanding` per cycle |

---

## 3. The ten originally requested baseline fields, reconciled

| Field | Status | Owner / determination |
|---|---|---|
| Baseline Version | Located elsewhere | `00-MASTER/BASELINE-001/baseline-declaration.json` `baseline_register` (`UCOS-BASELINE-NNN`) |
| Evolution Registry | **REFUSED** | §1 — would be a second identity authority |
| Evolution Cycle ID | **PRESENT** | `EvolutionRecord.cycle` (`engine/uckp/evolution.py`), advanced once per 15-stage wrap; `history.py` assigns one chain per cycle |
| Evolution Reason | **PRESENT** | `AUE-FLD-05`; also an identity input of the evolution object |
| Evidence Boundary | **PRESENT, renamed** | `evidence_boundary` on every UGA registry entry (`CANONICAL` / `NON_CANONICAL`) |
| Certification Record | **PRESENT** | `engine/universal_certification/contracts.py::Certificate`, `UCOS-UCERT-{blueprint}-{digest16}`; UAUE carries the verdict summary and delegates issuance (`AUE-BND-07`) |
| Parent Baseline | **PRESENT for objects** | `BirthRecord.parent_identity`; `BASELINE-001` `succession_source` measures baseline predecessors and reports the population as vacuous |
| Child Evolution | **DERIVED, not stored** | Inverting the parent edge — `engine/graph/queries.py` `descendants`. Storing a forward list would be a second answer to the same question |
| Rollback Point | **REFUSED** | §1 — rollback is a further evolution through the same gateway |
| Replay Capability | **PRESENT, strongest** | `EvolutionSimulation.fixed_point`, `UAUE-GATE-05` double-conduct digest equality, `--replay` byte comparison of 19 files |

**Eight of ten present or properly located; two refused with cause.**

---

## 4. Closing the inheritance-edge vacuity

`BASELINE-001` measures `CMG-INV-11` (explicit inheritance, implicit prohibited) over a population where "no artifact records a predecessor and no artifact declares an inheritance edge" — so the invariant is **vacuously satisfied**, and the engine already reports the vacuity rather than hiding it.

**This cycle makes it non-vacuous for the objects born under UOBC-000001.** Seven of the eight birth records declare `parent_identity`, rooted at
`urn:ucos:ucko:ucos.determination:UNIVERSAL-IDENTITY-UNIVERSE-DETERMINATION`. That is a real, single-origin, acyclic inheritance edge set — the first in the repository.

**Determination:** vacuity is closed *for objects with birth records* and remains open for the pre-existing corpus. Closing it corpus-wide requires the G11 migration, determined separately.

---

## 5. Evolution event vocabulary

Workstream 5 requires nine ledger events. `engine/nucleus/lineage.py` declares an **open** vocabulary — `record()` accepts any non-empty event name — and already declares seven of the nine:

| Required | Status |
|---|---|
| Created | `genesis` |
| Registered | `registered` |
| Certified | `certified` |
| Validated | `validated` |
| Linked | `context-bound` |
| Evolved | `evolved` |
| Superseded | `ownership-superseded` |
| **Archived** | **absent** — addable by call, not by edit |
| **Restored** | **absent, and currently unreachable** |

`Restored` is unreachable for a structural reason: `_LIFECYCLE_TRANSITIONS` makes `ARCHIVED` and `HISTORICAL` terminal, with no edge back. `TemporalFacet.RESTORATION` exists in `engine/temporal/facets.py` and `TemporalRecord.violations()` reports a restoration without an archive — so the *facet* is representable while the *transition* is not.

**Determination:** adding the `ARCHIVED → …` reverse edge is a change to the knowledge lifecycle owner (`engine/knowledge/model.py`) and is deferred to that owner. It is recorded as gap G10, not silently added here, because a reverse edge in a lifecycle transition graph is a substantive lifecycle change and this determination holds no lifecycle authority.

---

## 6. Determination summary

| Item | Determination |
|---|---|
| Identity stable across evolution | **ENFORCED** by re-derivation, not assertion |
| Evolution creates a replacement identity | **IMPOSSIBLE** — no path, timestamp or state is an identity input |
| Evolution Registry | **REFUSED** — second identity authority |
| Rollback Point | **REFUSED** — out-of-band revert |
| Child Evolution | **DERIVED** by edge inversion, never stored |
| Inheritance vacuity | **CLOSED** for birth-record objects; open corpus-wide (G11) |
| Archived / Restored events | **DEFERRED** to the lifecycle owner (G10) |
| New evolution model created | **NONE** |

---

**END UNIVERSAL EVOLUTION MODEL DETERMINATION**

**Status:** Evolution Baseline Established v1.0
**Lifecycle Authority:** UCIC-001 (owner) · UCL-000001 (derived) · CMG-000001 (law)
**Governed Evolution:** ENABLED — CEP-009 · Article-14
