# UICM — Lineage Gap Determination

> **Artifact:** `UICM-LINEAGE-GAP-DETERMINATION`
> **Programme:** UCOS-UICM-000001 — Phase 3 preparation
> **AUTHORITY = NONE — DERIVED TRUTH.**
> **Disposition:** DETERMINATION ONLY. Nothing implemented, nothing authorized.
> **Purpose:** state what cross-run continuity does *not* solve, so no gap is closed by silence.

---

## 1. The lineage gap, measured

| Property required | Held today | Gap |
|---|---|---|
| Append-only within a run | yes (UICM-INV-16) | none |
| Immutable records | yes (frozen dataclasses) | none |
| Deterministic derived identity | yes (L7 verified over 3162 records) | none |
| Lineage within a run | yes (`max_revision = 3`, chain intact) | none |
| **Lineage across runs** | **no** | **LG-01** |
| Retirement of a departed coordinate | no | **LG-02** |
| Revival of a retired coordinate | no | **LG-03** |
| Identifier format stability past `r99` | partial | **LG-04** |
| Bounded register growth | no (monotone by design) | **LG-05** |
| Lineage-depth bound in the rendered matrix | no | **LG-06** |

LG-01 is resolved by the continuity model. LG-02 is resolved by retirement. LG-03 through LG-06
are **not resolved** and are determined below.

## 2. LG-01 — Cross-run lineage · RESOLVED BY DESIGN

**Finding.** `build_registry` constructs a fresh registry each run; no loader exists. Every
coordinate reads `max_revision = 3`, so a coordinate moving `OPEN -> CLOSED` leaves no record it
was ever open. The 2108 `SUPERSEDED` records are within-run procedural markers, not history.

**Resolution.** Rehydrate the committed register and append only on difference. Verified
byte-exact; all eleven load-time invariants pass. **Zero migration** — the committed register is
already a valid genesis.

**Residual risk.** The loader must fail closed on a defective register rather than regenerate.
Silently discarding an unreadable register and rebuilding would destroy exactly the history this
gap exists to preserve, and would do so at the moment the register is least trustworthy.

## 3. LG-03 — Revival after retirement · UNRESOLVED, BOUNDED

**Finding.** Retirement appends `SUPERSEDED`, which is terminal. If a capability leaves the
boundary and later returns, its coordinate key (`capability:dimension`) is unchanged, and
`record` refuses every transition out of `SUPERSEDED`:

```
  attempt to revive: REFUSED — ClosureStateError:
      undeclared closure transition SUPERSEDED -> CLOSED
```

A returning capability is therefore **unrepresentable**. This is not a hypothetical: a package
renamed away and back, or split and re-merged, produces exactly this.

**Why it is not resolved here.** The only fixes both breach the freeze:

| Option | Cost |
|---|---|
| Permit `SUPERSEDED -> DISCOVERED` | **Digest-moving.** Verified: declaration digest `1676f708…` -> `53ff2204…`. `may_transition_to` is inside `ClosureDeclaration.to_dict()`, so the state list is sealed. Also breaks the "history does not move" property the declaration states explicitly |
| Make the coordinate key revision-generational | Changes `observation_id` for every future record and breaks the coordinate key that 3162 committed records share |
| Leave the returning capability out of the population | Violates the population rule (a rule over the boundary, never a list) and would make `require_total()` fail |

**Determination.** LG-03 is **ACCEPTED AS A BOUNDED LIMITATION** for Phase 3. A retired
coordinate is permanently retired. Re-admission requires its own architectural determination
against the frozen state machine, and must not be smuggled in as part of continuity. The
practical exposure is low — no capability has left the boundary in the measured history — but it
is real and must not be discovered later as a surprise.

**Detection requirement.** If a run finds a coordinate in the population whose current
observation is `SUPERSEDED`, it must **fail closed** with an explicit "retired coordinate
returned to the population" refusal, not attempt a transition and not silently exclude it. A
gap nobody can express must at least be a gap nobody can hide.

## 4. LG-04 — Identifier format past `r99` · UNRESOLVED, LATENT

**Finding.** `f"r{revision:02d}"` widens rather than overflows:

```
  revision  99 -> …-04-r99        revision 100 -> …-04-r100
  injective across 1..149            : True
  lexicographic order == numeric order: False
```

Identity remains injective, so there is no collision and no correctness defect. What breaks is
lexicographic ordering: `r100 < r99` as a string. Nothing in the engine currently sorts by
identifier — `coordinates()` sorts by coordinate key, `lineage()` uses insertion order, and
`_observations` is in append order — so the defect is **latent**.

**Determination.** LG-04 is **ACCEPTED AS A BOUNDED LIMITATION**, recorded rather than fixed.
Widening the field to `r{revision:03d}` would change all 3162 committed identifiers and force a
migration that §8 of the continuity model exists to avoid. The 99-revision ceiling is
approximately 99 state changes for a single coordinate; at the measured rate (one change per
resolution) it is far out of reach.

**Standing requirement.** Any future code that sorts, parses or range-scans observation
identifiers must sort by `(coordinate, revision)` and never by identifier string. This is the
kind of hidden finite assumption the repository already gates against
(`04-HIDDEN-FINITE-ASSUMPTION-CERTIFICATION.md`), and cross-run continuity is what activates it:
today every revision is 3, so the assumption is invisible.

## 5. LG-05 — Monotone growth · UNRESOLVED BY DESIGN

**Finding.** Deletion, truncation and compaction are all forbidden, so the register grows
without bound. Measured: ~669 bytes per appended observation.

| Scenario | Records | Register size | Delta |
|---|---:|---|---|
| genesis (today) | 3,162 | 2,089,806 B | — |
| Wave 1 (2 closures) | 3,164 | 2,091,145 B | +0.064% |
| all 158 gaps closed (variant A) | 3,320 | ~2,195,508 B | +5.1% |
| all 158 closed (variant B) | 3,478 | ~2,301,210 B | +10.1% |

**Determination.** LG-05 is **ACCEPTED AS INTENDED BEHAVIOUR**. Monotone growth is the direct
consequence of the append-only guarantee, and 5.1% for full closure is not a problem worth
trading that guarantee for. Variant A is recommended partly on this basis.

**Deferred question.** At what size, if ever, does archival become necessary — and can it be
done at all without breaking the chain? No answer is proposed here. Any archival scheme would
have to preserve `previous_hash` linkage across the archive boundary, and designing that before
there is a size problem would be speculative. Recorded as an open question, not a plan.

## 6. LG-06 — Lineage depth inside the rendered matrix · UNRESOLVED, MONITORED

**Finding.** `ClosureCell.to_dict()` emits `transition` (every state the coordinate passed
through) and `observation_lineage` (every observation id). Both are full lineage, so
`03-CLOSURE-MEASUREMENT-REPORT.json` grows with lineage depth as well as with population — and
it already carries all 1054 cells at 872 KB.

Today every cell carries exactly 3 lineage entries. Under continuity, a coordinate that has
closed, regressed and re-closed carries 6 or more, and the growth lands in the *measurement
report* rather than the observation registry.

**Determination.** LG-06 is **MONITORED, NOT RESOLVED**. It is not a correctness defect: full
lineage in the cell is what lets a reader reconstruct the coordinate's history without joining
against the registry. But it is a second growth vector in a different artifact, and it was not
visible before continuity because depth was constant.

**Requirement.** Measure the measurement-report size at M2 and after Wave 1, so the growth rate
is known rather than assumed. Do not truncate `observation_lineage` to bound it — a truncated
lineage is a lineage that cannot be verified, which defeats the purpose.

## 7. What is explicitly *not* a gap

| Considered | Verdict | Ground |
|---|---|---|
| A remediation/resolution registry | **NOT A GAP** | `ObservationRegistry` covers it; refused in Phase 2 and prohibited by steering |
| A new `RegistryKind` member | **NOT A GAP** | No new artifact kind; `register_kind` stays unused |
| A resolution state machine | **NOT A GAP** | `OPEN -> CLOSED -> CERTIFIED` already declared |
| A new identifier scheme | **NOT A GAP** | Existing scheme verified cross-run correct (L7) |
| A schema version bump | **NOT A GAP** | Schema unchanged; `format` stays `ucos-uicm-observation-registry/1.0.0` |
| Data migration / backfill | **NOT A GAP** | Committed register rehydrates byte-identically |
| Changes to the append path | **NOT A GAP** | `record` already enforces transition legality and derives identity from depth |
| Adding the register to `source_digests` | **REFUSED** | `observation_head` already seals it; would move the genesis digest for no gain |

## 8. Population instability — a live scheduling matter, not a lineage gap

`engine.uicm` is untracked and therefore outside its own population (62 capabilities, not 63).
Committing it adds 17 genesis coordinates and moves the matrix digest.

This is **not** a lineage gap — case 3 of the reconciliation function handles it, and it is the
existing behaviour. It is recorded here because the digest movement it causes could be
misread as a continuity defect. Whoever commits `engine/uicm` should expect the matrix digest to
move and the cell count to go 1054 -> 1071, and should not treat that as drift.

The reverse direction is the hazard, and it is resolved: a departing capability triggers
retirement (LG-02) rather than the hard `require_total()` failure it would otherwise cause.

## 9. Determination summary

| Gap | Status | Blocking Phase 3? |
|---|---|---|
| LG-01 cross-run lineage | **RESOLVED BY DESIGN** — zero-migration loader | no |
| LG-02 retirement of departed coordinates | **RESOLVED BY DESIGN** — append `SUPERSEDED`, filter `cells()` | no |
| LG-03 revival after retirement | **ACCEPTED, BOUNDED** — must fail closed on detection | no |
| LG-04 identifier format past `r99` | **ACCEPTED, LATENT** — never sort by identifier string | no |
| LG-05 monotone growth | **ACCEPTED, INTENDED** — +5.1% at full closure | no |
| LG-06 lineage depth in the measurement report | **MONITORED** — measure at M2 and after Wave 1 | no |

**No unresolved gap blocks Phase 3.** Two are resolved by design, three are accepted as bounded
with explicit detection or coding requirements, and one is monitored with a measurement
obligation. Every acceptance is recorded with its cost, and none is closed by assertion.

The two acceptances that carry a **hard requirement** on the implementation, and must not be
dropped:

1. **LG-03** — a retired coordinate found back in the population must fail the run closed with
   an explicit refusal. It must never be silently transitioned or silently excluded.
2. **LG-04** — no code may sort, parse or range-scan observation identifiers lexicographically.
   Order by `(coordinate, revision)`.
