# UMK-000001 — Universal Meta-Kernel Foundation (PROGRAM-002, WAVE-2)

| Field | Value |
|-------|-------|
| Artifact ID | UMK-000001 |
| Mission class | Kernel Foundation |
| Authority | NONE (DERIVED TRUTH) |
| Kernel home | `engine/kernel/` (v1.0.0) |
| Executable proof | `engine/kernel/compliance.py` |
| CLI | `ucos-kernel` (`engine/kernel/cli.py`) |
| Gate | `make umk-gate` / `python3 00-MASTER/UMK-000001/umk_engine.py --gate` |

## What this is

The permanent, immutable engineering substrate on which every future capability,
provider, project, civilization, organization, technology, intelligence, domain, and
execution model is constructed. It contains **only** universal meta-abstractions and
**no** concrete domain, provider, technology, or Earth assumptions.

The kernel is the *smallest possible* open-world meta-model:

- **One thing** — the `MetaObject` (`engine/kernel/meta.py`). Everything the platform can
  ever represent is a `MetaObject`.
- **One reflective root** — `MetaType`. A meta-type is a `MetaObject` classified by
  `MetaType`; the root `MetaType` is classified by itself. This single fixed point lets a
  finite kernel represent an unbounded, open world of concept-categories.
- **Open by registration** — a previously unknown concept-category is admitted by
  registering its meta-type (DATA), never by editing kernel code (Engineering Rule 7).

## Why it exists (the gap it closes)

Before PROGRAM-002 the platform's concept-categories lived in a **closed** enumeration
(`engine/registry/universal/identity.py::RegistryKind`). Admitting a genuinely new
category (as CONTEXT once was) required editing that enum — a kernel redesign. The
Universal Meta-Kernel removes the closed enumeration from the substrate: categories are
registered meta-types, so the kernel never needs redesign for a future category.

## Layout

| Path | Purpose |
|------|---------|
| `umk-kernel.json` | The DATA declaration — abstractions, homes, quality gates, proof categories, outputs. |
| `umk_engine.py` | Derived-truth engine: binds the declaration to Repository Truth, runs the kernel's executable proof, emits deliverables. |
| `00-UMK-DASHBOARD.md` … `08-FINAL-CERTIFICATION-REPORT.md` | Generated deliverables incl. the Universal Certification Matrix (07) and Final Certification Report (08) — regenerate, do not hand-edit. |
| `evidence/*.json` | Emitted validation + certification evidence (deterministic). |

## Commands

```bash
make umk            # regenerate deliverables + evidence
make umk-gate       # fail-closed constitutional gate (exit 1 if non-compliant)
make umk-self       # the three self-guards (declaration, write-scope, determinism)
make umk-certify    # fail-closed UNCONDITIONAL certification (all 20 matrix dimensions = 100%)
ucos-kernel prove   # run the constitutional gates + architectural proof directly
ucos-kernel evidence <dir>   # write kernel evidence anywhere
```

## Guarantees

- **Deterministic** — no wall-clock; the deliverable set is byte-identical for an
  unchanged kernel.
- **Reuse before create** — the constitutional obligations bind to the code under
  `engine/kernel/`; this programme legislates nothing and freezes no architecture.
- **Fail-closed** — an unusable declaration or missing substrate aborts with exit 2; no
  verdict may be asserted on unusable inputs.
