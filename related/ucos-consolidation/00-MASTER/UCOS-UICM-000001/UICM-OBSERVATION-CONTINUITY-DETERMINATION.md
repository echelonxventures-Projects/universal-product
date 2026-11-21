# UICM — OBSERVATION CONTINUITY DETERMINATION

| Field | Value |
|---|---|
| **ARTIFACT** | `UICM-OBSERVATION-CONTINUITY-DETERMINATION.md` |
| **PROGRAMME** | `UCOS-UICM-000001` — Foundation Closure Phase 1 (Observation Continuity Closure) |
| **AUTHORITY** | **NONE — DERIVED TRUTH.** No capability is created, no registry is minted, no ownership is allocated. Every owner named below is read from a located instrument. |
| **CLASSIFICATION** | `EVIDENCE` |
| **CANONICAL OWNER REUSED** | `engine/uicm/observation.py` (`ObservationRegistry`) · `engine/uicm/controller.py` (`UicmController`) · `00-MASTER/UCOS-UICM-000001/UICM-OBSERVATION-CONTINUITY-MODEL.md` (design, already owned) |
| **BASELINE** | HEAD `1f869865` · branch `integration/recovery-001` · working tree DIRTY (35 untracked entries) |
| **DISPOSITION** | **DETERMINATION ONLY.** No code written. No register modified. No implementation authorized by this document. |
| **COMPANION** | `UICM-REPLAY-VERIFICATION-DETERMINATION.md` (Phase 2) · `GATE-PURITY-DETERMINATION.md` (Phase 3) · `FOUNDATION-CLOSURE-IMPLEMENTATION-READINESS.md` (Phase 6) |

---

## 0. Knowledge-Once statement

The **design** of observation continuity is already owned by `UICM-OBSERVATION-CONTINUITY-MODEL.md`
(§1 design, §2 identity, §3 reconciliation cases 1–4, §4 lineage reconstruction, §5 retirement,
§6 replay compatibility, §7 digest impact, §8 migration M1–M6, §9 non-goals). **This document does
not restate it and does not supersede it.** It supplies only what the model does not contain and
what Phase 1 requires: the **owner mapping**, the **reuse decision with its refusals**, the
**implementation boundary**, the **affected-artifact set**, and the **validation approach** —
including one blocking precondition the model does not address.

---

## 1. Existing capability owner — the five discovery targets

Determination **D-1.0:** every one of the five capabilities Phase 1 names **already has a located
owner**. Nothing is unowned. Therefore no observation universe, history engine or registry may be
created.

| # | Capability | Canonical owner (located) | State on this baseline |
|---:|---|---|---|
| 1 | **Observation storage** | `engine/uicm/observation.py` → `ObservationRegistry` (append-only, hash-chained, `__slots__`-sealed) | **IMPLEMENTED, in-memory only.** Constructed fresh per run by `build_registry()` (`observation.py:434`). |
| 2 | **History tracking across executions** | `ObservationRegistry` — same owner, by the model's verdict "continuity is a loader, not a capability" | **NOT IMPLEMENTED.** No `from_document`, no `rehydrate`, no `load`. Verified: the only `load` symbols in the package are `ClosureDeclaration.load` and `CanonicalOwners.load` (`controller.py:170-171`). |
| 3 | **Lineage** | Per-coordinate: `ObservationRegistry.lineage()` / `supersedes` / `previous_hash` / `lineage_report()`. Corpus-wide artifact lineage: `00-BOOK` (`derive_lineage()` in `00-BOOK/tools/ukb.py`; `02-CANONICAL-OWNERSHIP-MATRIX.md` rows 30–31 → UMB-010, UMB-008, UCI-001) | **IMPLEMENTED within a run.** Truncated at the run boundary by target 2. |
| 4 | **Replay** | Repository-wide: `engine/determinism/reproduce.py` (`double_build`, `compare_builds`). Programme-local: `UicmController.measure_twice()` + `replay()` + `UICM-INV-13`. Byte-replay reference pattern: `engine/uaue/gate.py --replay` | **IMPLEMENTED.** See `UICM-REPLAY-VERIFICATION-DETERMINATION.md` for whether it is *sufficient*. |
| 5 | **Evidence persistence** | `engine/validation/evidence.py` (`ValidationEvidence`) · `engine/certification/evidence.py` (`CertificationEvidence`) · `engine/certification/ledger.py` (`CertificationLedger`) · UICM's own per-cell `evidence` + `evidence_digest` in `03-CLOSURE-MEASUREMENT-REPORT.json` | **IMPLEMENTED as value objects; NOT persisted by the engine.** `CertificationLedger` docstring: it "never writes to the certified corpus (DP-03); persistence, if any, is the caller's concern via `to_dict()`." |

**D-1.1 — the matrix does not name targets 1, 2 and 4.** `02-CANONICAL-OWNERSHIP-MATRIX.md` carries
no row for *observation storage*, *observation continuity* or *replay*. Ownership for those was
derived from code and from the UICM determinations, not read from the matrix. This is consistent
with `CR-04` / `H-01` in `ASSESSMENT-CONFLICT-REGISTER.md` (the matrix's 53 rows are unreadable by
machine and bound by no executing check). **No row is added here** — adding one is an act of the
matrix's owner, not of a measurement.

---

## 2. Current gap — measured on this baseline

Direct measurement of `00-MASTER/UCOS-UICM-000001/02-CLOSURE-OBSERVATION-REGISTRY.json`
(2 089 867 bytes):

```
format             ucos-uicm-observation-registry/1.0.0
keys               format · authority · mutability · lineage · effective_state_counts · observations
observations       3162
max_revision       3
```

Determination **D-1.2:** the register is a **write-only projection**. It is produced by
`UicmController.render()` → `_record_set()` → `_render_observations()` → `_write_text()` and is read
by nothing. Verified: the string `02-CLOSURE-OBSERVATION-REGISTRY` occurs in **zero** `.py`, `.sh`
or `.yml` files.

Four mechanical facts constitute the gap. Each erases run 1 at the start of run 2:

| # | Mechanism | Location | Consequence |
|---:|---|---|---|
| G-1 | `build_registry()` constructs `ObservationRegistry()` | `observation.py:434` | `_observations`, `_by_id`, `_by_coordinate` all empty |
| G-2 | `revision = len(lineage) + 1` over an empty lineage | `observation.py:205` ff. | every coordinate restarts at revision 1; `predecessor is None`, so **no transition-legality check against run 1's state runs at all** |
| G-3 | `head_hash` returns `GENESIS_HASH` (`"0"*64`) | `observation.py` | run 2's chain is a *parallel* chain over the same coordinates, not a continuation |
| G-4 | `render()` overwrites the register in place | `controller.py:228` ff. | the prior chain is replaced, not extended |

**The observable consequence, stated exactly.** `max_revision` is permanently 3 for all 1054
coordinates, because every coordinate always walks `DISCOVERED → MEASURED → <measured state>` at
`r01, r02, r03`. A coordinate read `OPEN` in run 1 and `CLOSED` in run 2 appears in run 2 as
`DISCOVERED → MEASURED → CLOSED`: **the fact that it was ever OPEN, and the evidence that justified
the OPEN reading, are gone.** The 2108 `SUPERSEDED` records in the committed register are therefore
**not history** — they are the current run's own `DISCOVERED` and `MEASURED` markers, derived as
superseded because a third record followed them inside the same process.

**D-1.3 — what is *not* broken.** The identifier scheme is already cross-run correct:
`observation_id(capability, dimension, revision)` uses no counter and no clock, and revision is
per-coordinate lineage depth. Revisions never exceed 3 only because depth always starts at zero.
The append path (`record()` with `require_transition_to`) needs no change. `UICM-INV-16`
(`_inv_append_only_registers`, AST-scanning the package for mutating methods) is real but scoped:
it proves no code *can* mutate a record, while the registry holding those records is discarded and
rebuilt each process.

---

## 3. Reuse decision

**RD-1 — ACCEPTED: reuse `ObservationRegistry`; add a verifying loader to it.**
The owner of observation storage is the owner of observation history. Continuity is the inverse of
`to_document()` and nothing else. The mechanism, the schema, the identity scheme, the transition
algebra and the seal are all unchanged. Basis: `UICM-CROSS-RUN-LINEAGE-CONTEXT.md` §9 —
*"cross-run continuity is a loader, not a capability; migration is a no-op"* — supported there by a
throwaway prototype in which all 3162 records rehydrated, `verify()` returned True, `head_hash`
matched, re-render was **byte-identical**, and load invariants **L1–L11 all passed** against the
committed register.

**RD-2 — REFUSED: a new observation universe, history engine or registry.**
Prohibited by the phase mandate and unnecessary under RD-1. It would also breach
`uicm.json.prohibited_creations` and the zero-duplication principle.

**RD-3 — REFUSED: reuse `engine.uckp.evolution.EvolutionLedger` as the carrier.**
It is the only append-only primitive in the repository that already performs
**verification-on-read** (`from_document` replays every record through `append`), and that property
is exactly right — but the class is hard-bound to the 15-stage `EVOLUTION_CYCLE` and cannot carry
closure observations. **Its *pattern* is adopted by RD-1; its *code* is not reused.** Adopting the
pattern is reuse; instantiating a second ledger type would be duplication.

**RD-4 — REFUSED: store observation history in `00-BOOK/DATA/id-ledger.json`.**
It is the repository's only genuinely disk-persisted, cross-run append-only history, and
`record_snapshots()` in `00-BOOK/tools/ukb.py:313` already implements the exact
append-on-difference semantics the model's §3 cases 1–3 require. Refused on two independent
grounds: (a) it is the corpus **identity** authority's own ledger — writing closure observations
into it makes UICM a second author of the identity register and breaches `CAA-INV-04
EXACTLY_ONE_IDENTITY_AUTHORITY`; (b) it stamps wall-clock `_now()`, which
`uicm.json.determinism.forbidden_in_emitted_bytes` prohibits. **The append-on-difference mechanism
is adopted as precedent; the storage location is not.**

**RD-5 — REFUSED: add the observation register to `source_digests`.**
`observation_head` already seals it. A sixth source entry would move the matrix digest at genesis
for no added guarantee. Basis: `UICM-OBSERVATION-CONTINUITY-MODEL.md` §7 decision 1.

**RD-6 — REFUSED: discard a defective register and regenerate.**
A register whose seal, sequence, `supersedes`, revision, transition, identifier, format or
dimension fails verification **refuses the run**. Silent regeneration destroys precisely the
history continuity exists to preserve. Basis: model §4.

**RD-7 — ACCEPTED: population is re-derived, never loaded.**
`Capability.to_dict()` is lossy by design (emits `artifact_count`, omits the `artifacts` tuple).
`discover_population()` keeps re-deriving it. The division is: **observations rehydrate; population
does not.**

---

## 4. Implementation boundary

### 4.1 Blocking precondition — disclosed, and not resolvable inside UICM

**D-1.4:** the entire UICM capability is **outside Repository Truth** on this baseline. Measured:

```
git ls-files engine/uicm                 → 0 files      (10 .py files on disk)
git check-ignore engine/uicm/…           → NOT IGNORED
00-MASTER/UCOS-UICM-000001/              → untracked in its entirety
grep -rn "engine.uicm|UICM" verify.sh Makefile .github/workflows/  → no matches
```

Consequences, stated without mitigation:

- Code written into `engine/uicm/` produces **no Repository Truth**: it is invisible to
  `verify.sh` stage 6b (UGA governs the *version-controlled* boundary), to the registration
  boundary, and to every certification authority.
- No gate, workflow or Makefile target executes the closure lifecycle. Continuity implemented
  today would be **executable but never executed** — the condition `XLIX.7` classifies as UNKNOWN
  compliance rather than satisfied.
- This is already recorded as **`CR-10` / decision `R-B5`** in `ASSESSMENT-CONFLICT-REGISTER.md`
  (class UNKNOWN, fails closed; "`git add` + `register.sh`, or explicit exclusion").

**Therefore the implementation boundary of Phase 1 is gated on decision `R-B5`, which is not
UICM's to make.** UICM cannot admit itself to version control; that is an act of the repository
root and of the registration authority. See `FOUNDATION-CLOSURE-IMPLEMENTATION-READINESS.md` §3
decision **D-1**.

### 4.2 Files inside the boundary (when authorized)

| File | Permitted change | Forbidden |
|---|---|---|
| `engine/uicm/observation.py` | add `ObservationRegistry.from_document()` + the L5–L11 load checks; add the four reconciliation cases; add the `SUPERSEDED` filter in `cells()` | any change to `record()`'s append semantics, to identity derivation, to the transition table, or to `to_document()`'s emitted shape |
| `engine/uicm/controller.py` | pass the located register into `build_registry`; make the "both `measure_twice` passes complete before `render`" ordering explicit and asserted | writing between passes; adding a second render path |
| `engine/uicm/model.py` | **none** | any new state, transition or dimension |
| `uicm.json` | at most an additive, digest-neutral `continuity` documentation block | any change to `states`, `dimensions`, `programme`, `source_digests`, `record_set` |
| `02-CLOSURE-OBSERVATION-REGISTRY.json` | **read as input; appended to by the engine only** | hand edit, truncation, archival, compaction, reordering |

### 4.3 Explicitly outside the boundary

New universe · new registry · new engine · new state · new transition · new identifier scheme ·
new constitution · schema/`format` bump · any change to `00-BOOK`, `00-CMG`, `00-MASTER/UIS-001`,
`00-MASTER/BASELINE-001`, `00-MASTER/UCL-000001` · any frozen artifact · Wave-1 gap closure
(model step **M6**, the first irreversible step, deliberately last).

---

## 5. Affected artifacts

| Artifact | Effect at genesis | Effect on first real state change | Class |
|---|---|---|---|
| `engine/uicm/observation.py` | modified (loader + L5–L11 + cases) | — | IMPLEMENTATION (untracked — see §4.1) |
| `engine/uicm/controller.py` | modified (input wiring + ordering assertion) | — | IMPLEMENTATION (untracked) |
| `02-CLOSURE-OBSERVATION-REGISTRY.json` | **byte-identical** — 0 appends | +1 record (~669 bytes) per changed coordinate | DERIVED |
| `03-CLOSURE-MEASUREMENT-REPORT.json` | unchanged | matrix digest moves | DERIVED |
| `04-CLOSURE-GAP-REGISTER.json` | unchanged | gap set moves as coordinates close | DERIVED |
| `00-UNIVERSAL-IMPLEMENTATION-CLOSURE-MATRIX.md` | unchanged | re-rendered | DERIVED |
| `05-CLOSURE-CERTIFICATION.md` | unchanged | re-rendered | DERIVED |
| `01-CLOSURE-OBLIGATION-REGISTER.json` | unchanged | unchanged | DERIVED |
| `uicm.json` | unchanged (or digest-neutral additive block) | unchanged | CANONICAL (programme declaration) |
| declaration digest · `source_digests` (5) | **unchanged** | unchanged | — |
| `observation_head` · matrix digest | unchanged | **move** | — |

Zero-migration is a measured property, not a plan: the committed register is a valid genesis, no
data transformation exists, and `format` stays `ucos-uicm-observation-registry/1.0.0`.

---

## 6. Validation approach

### 6.1 Load-time invariants — fail closed, every one

L1–L4 are already covered by the existing `verify()`. L5–L11 are the new checks and are the load
gate: **revision equals lineage position · every transition is declared · every identifier
re-derives from `(capability, dimension, revision)` · format matches · every dimension is declared
· derived fields (`current`, `effective_state`) recompute losslessly · exactly one current
observation per coordinate.** All eleven were measured against the committed register and all pass
(`UICM-CROSS-RUN-LINEAGE-CONTEXT.md`). A defect refuses the run (RD-6). An **absent** register is
genesis, not an error — which is what makes the change safe to land: with no register present, the
new path reduces to the current path exactly.

### 6.2 Determinism and fixed point

| Property | Assertion | Expected result at genesis |
|---|---|---|
| Fixed point | unchanged repository rewrites no byte | 0 differing coordinates · 0 appends · byte-identical |
| Two-pass determinism | `measure_twice()` passes agree | identical heads and matrix digests |
| Ordering constraint | both passes complete **before** `render()` writes | asserted explicitly, not left to statement order in `main()` |
| Byte replay | `--replay` compares bytes, not parsed structures | unchanged |
| `UICM-INV-13` | `_inv_measurement_determinism` | VIOLATED (not skipped) if `replay_digest is None` — the existing fail-closed behaviour is preserved |

The ordering constraint is the one property that changes character under continuity: writing
between passes would make pass 2 read pass 1's output, and the determinism check would compare a
register against its own successor and always agree. It must become a **tested** property.

### 6.3 Two hard requirements carried forward as refusals

- **LG-03** — a retired coordinate found back in the population **fails the run closed** with an
  explicit refusal. It is never silently transitioned (`SUPERSEDED` is terminal) and never silently
  excluded.
- **LG-04** — observation identifiers are **never** sorted, parsed or range-scanned
  lexicographically (`"r100" < "r99"` as strings). Order by `(coordinate, revision)`.

### 6.4 Validation approach for the execution gap — the part no code change fixes

`engine.uicm` is invoked by no gate, no Makefile target and no workflow (measured, §4.1). The
validation approach is therefore incomplete until the closure lifecycle is **bound to an existing
entry point**. Determination **D-1.5:** the binding must reuse `verify.sh` (the single canonical
entry point) in the manner `UAUE` already demonstrates — a read-only `--gate` stage plus a separate
`--replay` byte-comparison stage, with rendering reserved to an explicit `--render` invocation.
**No second pipeline, scheduler or daemon.** This binding is a Phase-3-dependent act: it must not
land while the gate-mode question is open, because a stage that writes on its gate path reproduces
the defect `GATE-PURITY-DETERMINATION.md` records. Sequencing is set in
`FOUNDATION-CLOSURE-IMPLEMENTATION-READINESS.md` §5.

### 6.5 Migration mapping — reused, not restated

Steps **M1–M6** are owned by `UICM-OBSERVATION-CONTINUITY-MODEL.md` §8. This determination adds
only their authorization class:

| Step | Content (owned by the model) | Reversible | Digest effect | Authorization class |
|---:|---|---|---|---|
| M1 | loader + L5–L11 | yes (delete the loader) | none | **bounded** — gated on decision `R-B5`/`D-1` |
| M2 | `--matrix --replay`, expect 0 appends, no drift | yes | none | bounded |
| M3 | reconciliation cases 1–3 | yes | none while nothing changes | bounded |
| M4 | case 4 (retirement) + `SUPERSEDED` filter in `cells()` | yes | none while population is stable | bounded |
| M5 | two-pass ordering made explicit and tested | yes | none | bounded |
| M6 | execute Wave 1 (2 gaps) — first recorded transition | **NO — mints 2 identities** | matrix digest moves | **EXPLICIT AUTHORIZATION REQUIRED, separately** |

---

## 7. Determination summary

| # | Determination |
|---|---|
| **D-1.0** | All five Phase-1 capabilities have located owners. No capability is missing. No universe, engine or registry may be created. |
| **D-1.1** | Ownership of *observation storage*, *observation continuity* and *replay* is absent from `02-CANONICAL-OWNERSHIP-MATRIX.md` and was derived from code. No row is added here (`H-01` is the matrix owner's decision). |
| **D-1.2** | The committed observation register is a **write-only projection**, read by nothing. |
| **D-1.3** | Identity, the append path and the transition algebra are **already cross-run correct**. Only lineage depth's origin is wrong. |
| **D-1.4** | **BLOCKING:** `engine/uicm/` (10 files) and `00-MASTER/UCOS-UICM-000001/` are **untracked and not ignored**; no gate executes them. Implementation here produces no Repository Truth until `CR-10`/`R-B5` is decided. |
| **D-1.5** | The closure lifecycle must be bound to `verify.sh` using the UAUE observe/replay/render separation. This binding is sequenced after Phase 3. |
| **RD-1..RD-7** | Reuse `ObservationRegistry` + verifying loader. Refuse a new registry, `EvolutionLedger` as carrier, `id-ledger.json` as store, a sixth `source_digest`, silent regeneration. Population is re-derived, never loaded. |

**Phase 1 verdict: observation continuity is DETERMINED and DESIGNED, reuse-only, zero-migration,
digest-neutral at genesis, and NOT AUTHORIZED for implementation on this baseline.** The single
blocking item is not technical: it is that the capability being closed is not yet part of the
repository whose truth it measures.
