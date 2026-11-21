# 05 — Namespace Registry Model

> PROGRAM **UCOS-UMA-001** · PHASE-001 · UNIVERSAL MEASUREMENT AUTHORITY
> BASELINE `b67a720` · AUTHORITY = **NONE (DESIGN ONLY)** · MODE = DESIGN-ONLY · NON-IMPLEMENTING · FAIL-CLOSED.

---

## 0. Purpose

Define the **Namespace Registry** — the governed, self-registering catalog of every architectural namespace UMA can recognize. This model directly satisfies **MA-1** (registry-driven, not hard-coded) and **MA-2** (every namespace is discoverable or explicitly reserved/excluded with rationale). It replaces the closed `FAMILIES` regex block that CLOSURE-007 proved incomplete (26 discoverable vs 60+ in-repo, 50+ in corpus).

## 1. Principle: Namespaces are data, not code

CLOSURE-007 defect: a namespace was recognizable only by editing source code. UMA inverts this: **a namespace exists to UMA iff it has a Namespace Descriptor in the registry.** Adding a namespace is a governed data registration (doc 13), never a code change. Discovery reads families from the registry snapshot (doc 07).

## 2. Namespace Descriptor Schema

| Field | Meaning | Fail-closed rule |
|---|---|---|
| `namespace_id` | Canonical namespace token (e.g. `UMB`, `UCOS-RIE`, `WP-R`). | must be unique |
| `title` | Human name. | required |
| `status` | ∈ {Implemented, Specified, Reserved, Historical, Deprecated, Experimental, Excluded, Unknown}. | required; `Unknown` is a valid *declared* status, never a silent gap |
| `owner_authority` | Authority that governs the namespace's meaning (UKB / a program / external). | required |
| `issuing_authority` | Who mints identifiers in it (may be "none/prose"). | required |
| `identifier_families[]` | Links to Identifier Registry entries (doc 06). | may be empty for prose namespaces |
| `format_note` | Structural description. | required |
| `machine_representation` | Where/how it appears (filenames, content tokens, store keys). | required |
| `expected_locations[]` | Repo/corpus roots where members are expected. | required |
| `registry_link` | The canonical registry that governs its members, if any. | may be "none" |
| `exclusion_rationale` | Required iff `status = Excluded`. | fail-closed: no exclusion without rationale (MA-2/MA-7) |
| `evidence[]` | Artifacts proving the namespace exists. | required |
| `disposition` | Whether UMA measures it, reserves it, or excludes it. | required |

## 3. Status Semantics (the MA-2 completeness rule)

Every namespace observed anywhere SHALL resolve to exactly one status. The registry is **complete** when:

```
observed_namespaces  ⊆  registered_namespaces
∧  every registered namespace has status ≠ (silent/absent)
∧  every Excluded namespace has exclusion_rationale
```

If Discovery observes a namespace token with **no** descriptor, it emits an `UNCOVERED-NAMESPACE` observation and the Coverage/Discovery metrics report `PARTIAL`. This makes the CLOSURE-007 "50+ silent namespaces" condition *measurable and visible* instead of invisible.

## 4. Self-Registration Model

- **Sources of registration:** (a) governance action, (b) issuing authorities declaring their own namespace, (c) a Discovery *proposal* — when Discovery finds an unknown namespace it does not guess; it emits a **Registration Proposal** into a review queue (doc 13). Proposals are never auto-accepted (fail-closed, governed).
- **Versioning:** the registry is snapshotted; every measurement pins a `registry_version`. A namespace added later never retroactively changes a prior sealed measurement (replayability).

## 5. Worked Coverage (illustrative, from CLOSURE-007 evidence — not asserted truth)

| Observed namespace | CLOSURE-007 state | Target UMA descriptor status |
|---|:---:|---|
| `UCOS-SERVICE/DATA/INFRA/APP/PLATFORM` | discoverable | Implemented |
| `UMB` (Universal Master Build) | silent (✗) | Specified/Implemented — *must be registered* |
| `UKB-ADV`, `UCOS-ADV` | silent (✗) | Specified — *must be registered* |
| `UCOS-RIE-*` (Repository Intelligence Engine) | silent (✗) | Specified — *must be registered* |
| `UCOS-MISC` | silent (✗) | must resolve (likely Historical/Reserved) |
| `WP-R`, `PCAMG-RUNTIME`, `PI`, `AD`, `MEM`, `ONTO`, `RPF`, `NVF` (corpus) | silent (✗) | Historical/Experimental per governance |
| `CTRL, RULE, TIME, SPACE, EXISTENCE, REALITY` | absent (0 hits) | Reserved (declared, distinguishes "reserved" from "never named") |

> These are *design targets* for the registry, not measurements. UMA asserts nothing about them until a governed run executes. Their appearance here is illustrative of how the registry closes the census gap.

## 6. Registry Invariants

1. **Single registry** (Single Authority): exactly one Namespace Registry per repository.
2. **No knowledge** (Knowledge Once): descriptors carry metadata + pointers, never canonical content.
3. **Governed mutation** (doc 13): additions/deprecations are audited, versioned events.
4. **Fail-closed discovery:** unknown namespace ⇒ UNCOVERED observation + proposal, never silent inclusion or exclusion.
5. **Reserved ≠ Absent:** the model can represent "intentionally reserved but not yet used," which CLOSURE-007 could not distinguish.

## 7. Dependency Determination

- The Namespace Registry is the concrete realization of CLOSURE-007 §05's proposed "Namespace Registry" governance interface. → **NEW, owned by UMA.**
- The regex family list in `closure_engine.py` becomes a *seed import* into descriptors, then is **retired** as an authority (its content transfers; its authority does not). → discovery authority **TRANSFER** to UMA (doc 20).

*END — 05 · UCOS-UMA-001 · AUTHORITY = NONE (DESIGN ONLY) · MODIFIES NOTHING.*
