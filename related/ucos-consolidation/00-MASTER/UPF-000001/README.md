# UPF-000001 — Universal Provider Framework (PROGRAM-003, WAVE-2)

| Field | Value |
|-------|-------|
| Artifact ID | UPF-000001 |
| Mission class | Core Platform Foundation |
| Authority | NONE (DERIVED TRUTH) |
| Framework home | `engine/provider/` (v1.0.0) |
| Realizes over | `engine/kernel/` (PROGRAM-002, immutable baseline) |
| Executable proof | `engine/provider/compliance.py` |
| CLI | `ucos-uprf` (`engine/provider/cli.py`) |
| Gate | `make uprf-gate` / `make uprf-certify` |

## What this is

The constitutional **realization layer** between the immutable Universal Meta-Kernel and
every future implementation:

- The kernel defines **existence** (a governed, registered `MetaObject`).
- The Provider Framework defines **realization** (how a capability is provided, selected,
  negotiated, composed, versioned, governed).
- Concrete providers implement **behaviour** — and are future *registrations*, never
  framework modifications.

A provider **category** is a registered kernel meta-type (open set); a **provider** is a
kernel `MetaObject` classified by its category, carrying contract, capabilities, metadata,
health and lifecycle as open attributes and its dependencies / policy / context as governed
relationships. There is no closed set of provider kinds anywhere.

## Reuse / duplicate analysis

A distinct EC-2 Universal Provider Architecture exists at `platform/universal_provider/`
(Terminal-04). It is a higher-layer artifact that does not reference the PROGRAM-002 kernel
and contains a closed `ProviderState` enum. This framework is the **engine-layer** kernel
realization; the engine layer cannot depend on the platform layer, so the two coexist at
different layers over different substrates. `engine/provider` imports and modifies neither
the kernel nor `platform/universal_provider`.

## Layout

| Path | Purpose |
|------|---------|
| `upf-provider.json` | The DATA declaration — responsibilities, homes, gates, proof categories, outputs, certification dimensions. |
| `upf_engine.py` | Derived-truth engine: binds the declaration to Repository Truth, runs the framework's executable proof, emits deliverables + the Universal Certification Matrix. |
| `00-UPF-DASHBOARD.md` … `08-FINAL-CERTIFICATION-REPORT.md` | Generated deliverables (regenerate; do not hand-edit). |
| `ADR-0004-*.md` | The architecture decision (homed here in operational memory, registration-excluded). |
| `evidence/*.json` | Emitted validation + certification evidence (deterministic). |

## Commands

```bash
make uprf            # regenerate deliverables + evidence
make uprf-gate       # fail-closed constitutional gate
make uprf-self       # declaration + write-scope + determinism guards
make uprf-certify    # fail-closed UNCONDITIONAL certification (all 20 dimensions = 100%)
ucos-uprf prove      # constitutional gates + architectural proof
```
