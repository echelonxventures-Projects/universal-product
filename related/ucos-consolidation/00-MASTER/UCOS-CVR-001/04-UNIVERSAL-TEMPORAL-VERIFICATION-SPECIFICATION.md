# UCOS-CVR-001 · 04 — UNIVERSAL TEMPORAL VERIFICATION SPECIFICATION

> **Satisfies:** Task 5. **Anchor:** commit `898ef8d`.
> **Status of the subject:** the Universal Temporal Framework **does not exist**. It is chartered
> as `SPEC/PLANNED` in `00-MASTER/UCOS-NUCLEUS-001/04-TIME-CALENDAR-COMMISSION-SCOPE.md` with
> owners `UNI-006` (Time Universe / `DOM-0020` Temporal Modeling) and `DOM-0021` (Calendars). The
> planetary, coordinate-system, reference-system, synchronization and precision items are tagged
> `[N]` — net-new realization scope. This document specifies what verification requires of it; it
> does not implement it and must not be read as evidence that it exists.

---

## PART A — THE CENTRAL CONFLICT

Two ratified properties are, as currently implemented, **mutually exclusive**:

| Property | Where it is enforced | What it demands |
|---|---|---|
| **Reproducibility** | `urrc/uer/uei/uccep --check-determinism`, CI step name: *"Self-determinism (byte-identical rendering across runs, **no timestamps**)"*; `engine/determinism/hermetic.py` `SOURCE_DATE_EPOCH = 0` | identical inputs ⇒ identical bytes ⇒ **no wall-clock in output** |
| **Temporal provenance** (Task 5) | — | every verification artifact must record *when* it was produced, in a frame-aware, calendar-configurable form |

Today the conflict is resolved by **deleting provenance**: the newest programme engines emit no
timestamp at all, while the older ones (`00-BOOK/tools/*`, 9 × `00-MASTER/*/*_engine.py`,
`engine/graph/evidence.py`, `engine/registry/universal/audit.py`) emit
`datetime.now(timezone.utc)` and then defend determinism with a *stamp-neutralizing comparator*
(`ukb.py::_stamp_eq_json` / `_neutralize_stamps`, which replaces stamp values with `<STAMP>`
before equality).

That comparator is the correct insight, applied ad-hoc. **This specification generalizes it into
an architecture.**

### Measured inventory of temporal call sites (17 files)

| Site | Form | Class |
|---|---|---|
| `00-BOOK/tools/connectors/base.py:57`, `governance_telemetry.py:100`, `ukb.py:64`, `ukbx.py:56,299,316` | `datetime.now(timezone.utc).replace(microsecond=0).isoformat()` | registration / telemetry |
| `engine/graph/evidence.py:67`, `engine/graph/architecture/evidence.py:78` | `"generated_at": datetime.now(tz=UTC).isoformat()` | **verification evidence** |
| `engine/registry/universal/audit.py:35` | `datetime.now(UTC).isoformat()` | registration audit |
| 9 × `00-MASTER/*/*_engine.py` | `NOW = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")` — **module-level constant** | certification / determination |
| `engine/determinism/hermetic.py:66` | `SOURCE_DATE_EPOCH = 0` | determinism normalization |

Every one is: UTC-only · Gregorian-only · Earth-only · single-plane (stamp embedded in the content
being hashed) · no frame, location, coordinate or calendar parameter. The module-level `NOW`
constants are additionally *import-time* clocks, which makes the stamp a function of process start
rather than of the event.

---

## PART B — THE DUAL-PLANE ARCHITECTURE

Every verification artifact is split into two planes with a **one-way** dependency.

```
        ┌─────────────────────────────────────────────┐
        │ DETERMINISTIC PLANE  (the artifact)         │   contains: findings, verdicts, digests,
        │   content_hash = H(canonical(plane))        │   universe digest, commit anchor
        │   ZERO temporal values                      │   → byte-identical across runs, forever
        └───────────────────┬─────────────────────────┘
                            │ referenced by content_hash (one way)
        ┌───────────────────▼─────────────────────────┐
        │ TEMPORAL PLANE  (sidecar record)            │   contains: the full temporal record
        │   subject = content_hash of the plane above │   → varies per run, by design
        └─────────────────────────────────────────────┘
```

**Invariants**

- **T-1** The deterministic plane contains no temporal value of any kind. Determinism guards run
  against it unchanged — the existing `--check-determinism` guards keep passing **without
  modification**.
- **T-2** The temporal plane is never an input to any verification decision (L8 has no edge into
  L1–L7 — see `03`).
- **T-3** The temporal plane is *append-only* and keyed by the deterministic plane's content hash.
  N runs of an unchanged verification produce **1** artifact and **N** temporal records — which is
  exactly the provenance that is lost today.
- **T-4** A verification artifact without a resolvable temporal record is **incomplete** (`TMP`
  Mandatory in `01` Part B for classes 1–6, 10, 11, 12).
- **T-5** `SOURCE_DATE_EPOCH` remains the normalizing instant for the deterministic plane
  (`engine/determinism/hermetic.py` unchanged); it is *not* provenance and must never be presented
  as one.

---

## PART C — REQUIREMENT MAPPING (Task 5's nine requirements)

| # | Requirement | Design element | Reuse anchor / status |
|---|---|---|---|
| 1 | **Native local timestamp** | `native.instant` + `native.frame` — the observer's own frame, whatever it is | `engine/runtime/context.py` `ReferenceFrame`; `UNI-008` Observer |
| 2 | **Universal reference timestamp** | `universal.instant` in the declared reference standard; the *pivot* for all conversion | `[N]` — Temporal Reference System registry does not exist |
| 3 | **Configurable calendar** | `calendar_id` resolved from a calendar registry (Gregorian, Julian, lunar, fiscal, mission, planetary, …) | `DOM-0021` `CAP-0088/0089/0090` declared, unrealized |
| 4 | **Configurable time standard** | `standard_id` (e.g. an atomic standard, a coordinate time, a mission elapsed time) — an entry in a registry, never an enum in code | `[N]` |
| 5 | **Planet-aware** | `body_id` — the gravitational/rotational body the native frame belongs to; **no default** | `[N]` (non-Earth frames over `UNI-005` Space + `UNI-050` Astronomy) |
| 6 | **Location-aware** | `location_id` — a registered place on/near `body_id` | `[N]` |
| 7 | **Coordinate-aware** | `coordinates` + `coordinate_system_id` (spatial) and the temporal coordinate system | `DOM-0020` (coordinate frame, RAT-03) declared |
| 8 | **Bidirectional conversion** | `convert(instant, from_frame, to_frame)` with round-trip loss declared: `exact` \| `bounded(ε)` \| `undefined` | `CAP-0089` Conversion declared, unrealized |
| 9 | **Configurable formatting** | `format_profile_id` → rendering only; **formatting never changes the recorded instant** | `[N]` |
| — | **No Earth-specific assumptions** | `UTC`, `Z`, `Gregorian`, `timezone.utc` may not appear as *defaults* anywhere; they are ordinary registry entries | **violated in all 17 sites today** |

### The Earth-neutrality test (mechanically checkable)

> A temporal record is Earth-neutral iff replacing `body_id` with a non-Earth body, and
> `calendar_id` with a non-Gregorian calendar, requires **no source change** — only different
> registry entries.

Today every one of the 17 sites fails this test, because `timezone.utc` is hard-coded as the
frame, `isoformat()` hard-codes the calendar and the rendering, and no `body_id` concept exists.

---

## PART D — THE TEMPORAL RECORD (shape only; not created by this mission)

```jsonc
{
  "record": "ucos-temporal-record/1.0.0",
  "subject": { "artifact": "<relative path>", "content_hash": "<sha256 of deterministic plane>" },
  "anchor":  { "vcs_commit": "898ef8d", "universe_digest": "<sha256>" },
  "native":  { "instant": "<opaque, standard-relative>", "standard_id": "…",
               "calendar_id": "…", "body_id": "…", "location_id": "…",
               "coordinate_system_id": "…", "coordinates": [ … ], "frame_id": "…" },
  "universal": { "instant": "<opaque>", "standard_id": "…", "reference_system_id": "…" },
  "conversion": { "native_to_universal": { "fidelity": "exact|bounded|undefined",
                                           "epsilon": null, "algorithm_id": "…" },
                  "universal_to_native": { … } },
  "rendering": { "format_profile_id": "…", "rendered": "<display only, never compared>" },
  "provenance": { "producer": "<engine qualified name>", "producer_version": "…",
                  "clock_source_id": "…", "precision": "…", "uncertainty": "…" }
}
```

Design rules that follow from the record:

- `instant` values are **opaque and standard-relative**. There is no privileged epoch, so nothing
  in the record presumes Earth, the Gregorian calendar, or UTC.
- `rendered` is display-only and is excluded from every comparison and every hash.
- `fidelity: undefined` is a legal, *useful* value: a conversion that cannot be performed is
  declared rather than approximated. This is the same fail-closed honesty as
  `URRC --check-no-fabrication`.
- `precision` / `uncertainty` are mandatory fields, because an instant without a precision is an
  unfalsifiable claim.

---

## PART E — REVIEW OF EVERY EXISTING VERIFICATION ARTIFACT

| Artifact family | Current temporal handling | Verdict | Required action |
|---|---|---|---|
| `00-BOOK/DATA/*.json` (registers) | `generated_at` embedded; neutralized for drift comparison by `_neutralize_stamps` | **non-conformant, mitigated** | move stamp to temporal plane; `_neutralize_stamps` becomes unnecessary rather than load-bearing |
| `engine/graph/evidence.py`, `engine/graph/architecture/evidence.py` | `generated_at` embedded in the evidence document that is then hashed | **non-conformant** — provenance and content are entangled | split planes |
| `engine/registry/universal/audit.py` | wall-clock in the audit trail | **non-conformant** | audit entries are inherently temporal ⇒ they *are* temporal-plane records; re-home |
| 9 × `00-MASTER/*/*_engine.py` (`NOW` constants) | import-time UTC constant stamped into determinations | **non-conformant** | remove from determination bytes; emit a temporal record |
| `UCCEP / URRC / UER / UEI / UCDA` outputs | **no timestamp at all** (`--check-determinism` enforces it) | **conformant with T-1, missing provenance (T-4)** | keep the deterministic plane exactly as is; add the sidecar |
| `coverage.xml` | carries a millisecond epoch `timestamp="1785170011848"` produced by `coverage` itself, not by UCOS | **non-conformant, third-party** | do not patch the tool; record the run in a temporal record and treat the tool's stamp as unauthoritative |
| `.coverage` binary | tool-internal | out of scope | — |
| CI artifacts (`determinism-evidence`, `coverage-xml`, `*-determinations`) | inherit the above | derived | conformance follows from the producers |

**Count:** of the verification artifact families reviewed, **0** are conformant with the Universal
Temporal Framework, because the framework does not exist. **5 families** are already conformant
with the *deterministic plane* requirement (T-1) and need only the sidecar; **4 families** entangle
provenance with content and need the split; **1** (`coverage.xml`) is third-party and must be
wrapped rather than modified.

---

## PART F — SEQUENCING CONSTRAINT (this is a hard dependency, not a preference)

Temporal conformance **cannot** be implemented in this programme:

1. `UNI-006` / `DOM-0021` own Time and Calendar. Implementing a temporal framework inside a
   verification programme would create a **duplicate authority** — precisely the violation
   `03` §B.2 exists to prevent, and precisely what `URRC --check-reuse-before-create` forbids.
2. Six of the nine requirements are `[N]` net-new scope over `UNI-005` Space / `UNI-050` Astronomy
   / `UNI-046` Physics. They are commissions, not refactors.
3. Therefore the roadmap in `06` implements **only the plane split** (which is verification's own
   business and removes the entanglement), and declares the temporal record's *schema and
   obligation* while binding its *production* to the future `UNI-006`/`DOM-0021` realization.

Until that realization exists, `TMP` is satisfiable **only in its degenerate form**:

> **Degenerate temporal conformance (interim, and it must be labelled as interim):** the
> deterministic plane contains no temporal value; the artifact carries the VCS commit anchor and
> the universe digest as its *ordering* provenance; the temporal record is emitted with
> `native = universal`, `standard_id = "unowned-interim"`, and `body_id`/`location_id`/
> `coordinates` explicitly `null` with `fidelity: "undefined"`.

That interim state is honest: it records that provenance exists, that it is Earth-bound, and that
its frame is unowned — instead of pretending a UTC string is universal time.

*End of 04-UNIVERSAL-TEMPORAL-VERIFICATION-SPECIFICATION.md*
