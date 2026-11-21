# UICM — Observation Continuity Model

> **Artifact:** `UICM-OBSERVATION-CONTINUITY-MODEL`
> **Programme:** UCOS-UICM-000001 — Phase 3 preparation
> **AUTHORITY = NONE — DERIVED TRUTH.**
> **Disposition:** DESIGN ONLY. Not implemented. Not authorized.
> **Constraint compliance:** `ObservationRegistry` remains the only registry. No remediation
> registry. No mutable update. No deletion. No historical observation replaced.

---

## 1. Design in one statement

The committed observation registry becomes an **input** to the run. The registry is rehydrated
from it, the measurement is compared against each coordinate's current reading, and an
observation is appended **only where the two differ**. Everything else — identity, sealing,
lineage, supersession, transition legality — is the existing mechanism, unchanged.

```
  02-CLOSURE-OBSERVATION-REGISTRY.json  (prior history, sealed)
                |
                v
          rehydrate + verify  ------------> refuse the run if any of L1..L11 fails
                |
                v
      ObservationRegistry (revisions 1..r)
                |
                +<---- measure(repo)          17 probes over live tracked content
                +<---- discover_population()   capability identity, re-derived never loaded
                |
                v
       reconcile: append only on difference
                |
                v
      ObservationRegistry (revisions 1..r')   r' = r  when nothing changed
                |
                v
        project matrix -> gaps -> validate -> certify -> render
```

## 2. Cross-run observation identity model

Identity is unchanged. It is already cross-run correct:

```python
observation_id = f"UICM-OBS-{capability.short_id}-{dimension.ordinal:02d}-r{revision:02d}"
```

| Component | Source | Cross-run behaviour |
|---|---|---|
| `capability.short_id` | capability register (`UCKO-CAP-*` digest fragment) | stable while the capability exists |
| `dimension.ordinal` | declaration, unique by `require_unique_dimensions` | stable |
| `revision` | **lineage depth of the coordinate** | continues across runs — the only component that moves |

**Injective, and re-derivable rather than trusted.** All 3162 committed identifiers were
recomputed from `(capability_id, dimension, revision)` and matched exactly (invariant L7). So a
loader can validate every identifier instead of accepting the file's word for it.

**No counter, no clock, no global sequence.** Revision is per-coordinate depth, so measuring
unrelated coordinates in a different order cannot change any identifier. This is precisely why
the existing scheme needs no change for continuity: it was already defined against lineage
depth rather than run count.

**Bounded format limitation.** The `r{revision:02d}` field widens rather than overflowing:

```
  revision  99 -> UICM-OBS-8E3F86206048-04-r99
  revision 100 -> UICM-OBS-8E3F86206048-04-r100
  injective across 1..149            : True
  lexicographic order == numeric order: False
```

Identity stays injective past 99; only *lexicographic* ordering breaks. Nothing in the engine
sorts by identifier string — `coordinates()` sorts by coordinate key and `lineage()` uses
insertion order — so the defect is latent, not active. It is recorded as a bounded finding in
`UICM-LINEAGE-GAP-DETERMINATION.md` §4 rather than fixed here, because changing the format
would invalidate all 3162 committed identifiers.

## 3. Observation continuity resolution — the reconciliation function

For each coordinate, exactly one of four cases applies. The function is total over the union of
(register coordinates) and (population x dimensions), so no coordinate is unhandled.

| # | Register | Population | Measured vs current | Action | Records appended |
|---:|---|---|---|---|---:|
| 1 | present | present | same | **nothing** | 0 |
| 2 | present | present | differs | append the measured state | 1 |
| 3 | absent | present | n/a | genesis: `DISCOVERED -> MEASURED -> state` | 3 |
| 4 | present | absent | n/a | retire: append `SUPERSEDED` | 1 |

Case 1 is what preserves the fixed point. Case 3 is the existing `build_registry` behaviour,
now scoped to new coordinates only. Case 4 is new and is the subject of §5.

### Case 2 — the closure transition

```
  revision r    OPEN        carries the gap; stays readable forever
  revision r+1  CLOSED      appended; supersedes r; r becomes SUPERSEDED by derivation
```

Verified against the Wave-1 scenario:

```
  appended=2  chain_intact=True
  lineage: DISCOVERED -> MEASURED -> OPEN -> CLOSED
  revisions: [1, 2, 3, 4]   ids: [r01, r02, r03, r04]
  effective: [SUPERSEDED, SUPERSEDED, SUPERSEDED, CLOSED]
```

### Design decision — one record per change, not two

Genesis records `DISCOVERED -> MEASURED -> state` so that "nothing jumped straight to a verdict
without being measured first". The symmetric choice for case 2 would be
`OPEN -> MEASURED -> CLOSED`. Both were tested and both are legal:

| Variant | Records per change | Lineage | 158 closures cost |
|---|---:|---|---:|
| **A — direct `OPEN -> CLOSED`** (recommended) | 1 | `… OPEN -> CLOSED` | 158 records, +5.1% |
| B — via `MEASURED` | 2 | `… OPEN -> MEASURED -> CLOSED` | 316 records, +10.1% |

**Variant A is recommended.** `OPEN -> CLOSED` is a declared transition, and the intermediate
`MEASURED` record adds nothing: `record_transition` gives evidence only to the final state, so
the `MEASURED` record would carry `finding = "MEASURED"` and an **empty** evidence tuple. The
re-measurement is already evidenced by the `CLOSED` record itself, which cannot exist without
evidence (`requires_evidence: true`). Variant B doubles the register's growth to record a
marker that asserts nothing.

The genesis preamble keeps its three-step path because there the distinction is real: a
coordinate that has never been measured must be distinguishable from one measured and passing.

## 4. Historical lineage reconstruction

Reconstruction is a fold over the document in `sequence` order. Per-coordinate ordering follows
automatically because `revision` is monotone within a coordinate in sequence order — asserted
as L5 rather than assumed.

```
  for record in document["observations"]:            # sequence order
      discard record["current"], record["effective_state"]     # derived; L10 proves lossless
      rebuild the frozen Observation from the sealed body + entry_hash
      refuse the run unless entry_hash == expected_hash()      # L1, per record
      append to: _observations, _by_id, _by_coordinate[key]
  then assert L2..L11 over the whole register
```

**Fail closed on every defect.** A broken seal, a gap in the sequence, a wrong `supersedes`, a
revision that is not its lineage position, an undeclared transition, a non-re-derivable
identifier, an unknown format or an undeclared dimension all **refuse the run**. A register
that cannot be trusted yields no verdict — it must never be silently discarded and regenerated,
because regeneration is exactly the history loss continuity exists to prevent.

**Absent register is genesis, not an error.** A missing file means revision 0 for every
coordinate and case 3 applies throughout — which reproduces today's behaviour exactly. This is
what makes the change safe to land: with no register present, the new code path is the old one.

## 5. Retirement — the only new semantic

Case 4 exists because `require_total()` compares cell count against
`len(capabilities) x len(dimensions)`, and the register outlives the population.

```
  retire(coordinate) = record(state=SUPERSEDED,
                             finding="coordinate retired: capability left the population boundary",
                             evidence=("retired_from_boundary:<capability>",))
```

`cells()` then projects only coordinates whose **current** observation is not `SUPERSEDED`.
Verified: 1054 coordinates, one capability retired, `cells()` filtered returns 1037 = 61 x 17,
and `require_total()` passes.

Why this is the right construction rather than a workaround:

- it uses only the declared state vocabulary — no new state, no new transition;
- `<any live state> -> SUPERSEDED` is declared from all six live states;
- `SUPERSEDED` is terminal, so a retired coordinate cannot be quietly revived — the attempt
  raises `undeclared closure transition SUPERSEDED -> CLOSED`;
- the full prior lineage remains readable: retirement *adds* a record and deletes nothing.

This is the one place the design extends meaning rather than mechanism, and it does so by
reading `SUPERSEDED` as what the declaration already says it is: "a historical observation that
a later observation of the same coordinate replaced. Terminal."

## 6. Replay compatibility

| Property | Requirement | Result |
|---|---|---|
| Fixed point | unchanged repository rewrites no byte | **holds** — 0 differing coordinates, 0 appends, byte-identical |
| Two-pass determinism | `measure_twice()` passes agree | **holds** — identical heads and digests |
| Convergence | render, then re-measure, reaches a fixed point | **holds** — converges in one step |
| Byte comparison | `--replay` compares bytes, not parsed structures | **unchanged** |

**One ordering constraint is now load-bearing.** `measure_twice()` must complete both passes
*before* `render` writes. It does today (`main` calls `measure_twice()` then `--render`), but
under continuity this stops being incidental: writing between passes would make pass 2 read
pass 1's output, and the determinism check would compare a register against its own successor
and always agree. This must become an explicit, tested property, not a side effect of statement
order.

## 7. Digest impact

| Digest | Effect at genesis | Effect on state change |
|---|---|---|
| declaration digest | **unchanged** — continuity needs no declared vocabulary change | unchanged |
| `source_digests` (5 entries) | **unchanged** — the register is deliberately not a sixth source | unchanged |
| `observation_head` | unchanged | moves |
| matrix digest | unchanged | moves (`8ce37cd1…` -> `a7831b0b…` for Wave 1) |
| register bytes | unchanged | +669 per observation |

Genesis is byte-identical, so landing continuity moves nothing. Thereafter the matrix digest
moves when and only when a coordinate's state changes, which is the correct semantics for a
digest that seals both content and history.

Two digest decisions are deliberate:

1. **The register is not added to `source_digests`.** `observation_head` already seals it. A
   sixth entry would move the matrix digest at genesis and add no guarantee.
2. **No declaration change is required.** If a `continuity` section is later declared for
   documentation, it is digest-neutral: `ClosureDeclaration.to_dict()` emits only `programme`,
   `states` and `dimensions`, and `DimensionDeclaration.from_record` ignores unknown keys —
   verified in Phase 2 (`1676f708…` unchanged under an additive block).

## 8. Migration strategy

**Zero-migration.** The committed register is a valid genesis: rehydration re-renders it
byte-identically, and all eleven load-time invariants pass against it. There is no data
transformation, no backfill, no rewrite, and no version field to bump — the document `format`
(`ucos-uicm-observation-registry/1.0.0`) is unchanged because the schema is unchanged.

| Step | Action | Reversible | Digest effect |
|---:|---|---|---|
| M1 | Add the loader and the L5–L11 checks. Absent register = genesis | yes — delete the loader | none |
| M2 | Run `--matrix --replay`. Expect 0 appends, no drift, digest `8ce37cd1…` | yes | none |
| M3 | Add reconciliation cases 1–3 (append-on-difference, genesis for new) | yes | none while nothing changes |
| M4 | Add case 4 (retirement) and the `SUPERSEDED` filter in `cells()` | yes | none while population is stable |
| M5 | Make the two-pass ordering constraint explicit and tested | yes | none |
| M6 | Only then: execute Wave 1 (2 gaps) as the first recorded transition | **no** — mints 2 identities | matrix digest moves |

M1–M5 are digest-neutral and individually reversible. M6 is the first irreversible step and is
deliberately last, so the architecture is proven before any gap closes.

**Sequencing hazard.** `engine.uicm` is untracked and therefore outside its own population.
Committing it takes the population to 63 and adds 17 genesis coordinates. Committing it
*before* M3 lands is safe (the register is regenerated today). Committing it *between* M1 and
M3 is also safe (case 3 is the existing behaviour). There is no ordering in which it is unsafe,
but the 17 new coordinates will move the matrix digest whenever it happens, and that should not
be confused with a continuity defect.

## 9. What this model does not do

- It does not create a registry, a state, a transition, an identifier scheme or a kind.
- It does not modify the append path, the transition algebra, or any committed record.
- It does not delete, truncate, archive or compact anything — growth is monotone by design, and
  the archival question is deferred (`UICM-LINEAGE-GAP-DETERMINATION.md` §5).
- It does not make `CLOSED` reachable without evidence or `CERTIFIED` reachable without the
  located certifier. Both remain exactly as declared.
- It does not resolve coordinate revival after retirement (§3 of the gap determination).
