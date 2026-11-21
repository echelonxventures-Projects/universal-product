# MCOS-000001 — Universal Meta-Civilization Platform (PROGRAM-004, WAVE-2)

| Field | Value |
|-------|-------|
| Artifact ID | MCOS-000001 |
| Mission class | Core Platform Foundation |
| Authority | NONE (DERIVED TRUTH) |
| Layer home | `engine/civilization/` (v1.0.0) |
| Realizes over | `engine/kernel/` (PROGRAM-002, immutable baseline) |
| Executable proof | `engine/civilization/compliance.py` |
| CLI | `ucos-mcos` (`engine/civilization/cli.py`) |
| Gate | `make mcos-gate` / `python3 00-MASTER/MCOS-000001/mcos_engine.py --gate` |
| Decision register | `03-ARCHITECTURAL-DECISION-ASSIMILATION-MATRIX.md` §8 (`DEC-MCOS-01`…) |
| ADR | `ADR-0005-meta-civilization-platform-generation-layer.md` |

## What this is

The layer that **generates constitutional operating systems**. It stands to the Universal
Meta-Kernel exactly as the Universal Provider Framework does — a *realization layer* holding
no authority of its own:

- The **kernel** (PROGRAM-002) defines **existence** — what a thing is.
- The **Provider Framework** (PROGRAM-003) defines **realization** — how a capability is
  provided.
- **This layer** defines **generation** — how a whole constitutional system comes into being,
  within what dimensions it is contextualized, and in what order its capabilities compose.

Three components over **one** kernel:

| Component | Mandated construct | What it makes open |
|---|---|---|
| `dimensions.py` → `DimensionRegistry` | Universal Dimension Model | Which axes exist at all. A dimension is a registered kernel meta-type; no list of dimensions exists anywhere. |
| `composition.py` → `CompositionPlanner` | Dynamic Capability Composition | The execution order *and the rule that derives it*. No workflow, no pipeline. |
| `generation.py` → `ConstitutionalGenerator` | Constitutional Generation Model | The stratum chain and the operating-system catalogue. Both extend by registration. |
| `mcos.py` → `MetaCivilizationPlatform` | MCOS / Universal Engineering Platform | Binds the three over a single kernel. `authority == "NONE"`. |

## What was NOT built, and why

Reuse-First was applied before a single file was authored. **Seven of the ten mandated
constructs already existed** and were referenced or extended, never re-implemented:

| Mandated construct | Already owned by | Method |
|---|---|---|
| Universal Meta Kernel | `engine/kernel/` · `UMK-000001` · `ADR-0003` | REUSE |
| Universal Registry Architecture | kernel `UniversalRegistry` · `engine/registry/**` (`DEC-CAEM-07`: a second registry is prohibited) | REUSE |
| Universal Capability Discovery | `engine/discovery/` (8 registry-driven dimensions) | REUSE |
| Universal Open-World Expansion Model | `03-CONSTITUTIONAL-UNBOUNDEDNESS-CERTIFICATION.md` (16 axes) · `04-HIDDEN-FINITE-ASSUMPTION-CERTIFICATION.md` (23 axes) | EXTEND (executed mechanism) |
| Unlimited Constitutional Evolution | `00-CEP/CEP-009` · `UEI-000001` | REUSE |
| Universal Engineering Platform | `09-PLATFORM/PLATFORM-005` + `PLATFORM-010` + `07-ENGINEERING` (recorded *CONCEPTUAL / UNNAMED*) | EXTEND — named, not authored |
| MCOS | `DEC-CAEM-13` RESOLVE-NAME → `MCS-000`; `DEC-CAEM-13R` **rejects** vesting authority in it | RESOLVE-NAME — realized with `authority == "NONE"` |

Three were genuinely absent **as executable mechanism** and are supplied here: the open
dimension **space** (`engine/context/**` owns context frames, values and the twelve `CXL` laws
— *what a situation is*; nothing owned *which axes exist*), declarative composition
(`DEC-ADAM-14` / `WP-UCDA-006`; `engine/factory/orchestrator.py::execute()` is a fixed
six-step sequence), and generation at the **operating-system** stratum (the six frozen
`05-GENERATION` families generate artefacts *within* one system).

Reuse is measured, not asserted — `make mcos-self` fails closed if a responsibility claims
`REUSED` while homed inside this layer. Current distribution: **REUSED 9 · EXTENDED 5 · NEW 12**.

## Layout

| Path | Purpose |
|------|---------|
| `mcos-civilization.json` | The DATA declaration — programme, substrate, 26 responsibilities with reuse dispositions, 12 quality gates, 12 proof categories, 5 unknown operating systems, 9 strata, 9 outputs, 20 certification dimensions. |
| `mcos_engine.py` | Derived-truth engine: binds the declaration to Repository Truth, runs the layer's executable proof, emits deliverables. |
| `00-MCOS-DASHBOARD.md` … `08-FINAL-CERTIFICATION-REPORT.md` | Generated deliverables incl. the Universal Certification Matrix (07) — regenerate, do not hand-edit. |
| `evidence/*.json` | Emitted validation + certification evidence (deterministic). |
| `ADR-0005-*.md` | The architectural decision record. |

## Commands

```bash
make mcos            # regenerate deliverables + evidence
make mcos-gate       # fail-closed constitutional gate (exit 1 if non-compliant)
make mcos-self       # the four self-guards (declaration, reuse, write-scope, determinism)
make mcos-certify    # fail-closed UNCONDITIONAL certification (all 20 dimensions = 100%)
ucos-mcos prove      # run the constitutional gates + architectural proof directly
ucos-mcos describe   # the platform's self-description
ucos-mcos evidence <dir>   # write platform evidence anywhere
```

## How the mandate's success criterion is proven

> No future capability, dimension, universe, reality, existence model, engineering model,
> commercial model, governance model, or runtime model shall require changes to the
> constitutional foundation.

The architectural proof takes each of those categories, admits a previously unknown instance
of it by registration, and fingerprints **both this layer's and the kernel's** source before
and after. A category that could only be admitted by editing code fails its own probe. It then
does the same for five previously unknown constitutional operating systems — deliberately not
UCOS/GCOS/HCOS/ECOS/ICOS, since naming a system the repository already knows would prove
nothing about an open catalogue — registering, generating and verifying each lineage end to
end.

Current state: **12/12 categories · 5/5 operating systems · layer unchanged · kernel
unchanged · 12/12 quality gates · 20/20 certification dimensions at 100%.**

## Guarantees

- **Deterministic** — no wall-clock, no RNG, no network; two independently constructed
  platforms are byte-identical, and the deliverable set is byte-identical across runs.
- **Reuse before create** — enforced by a self-guard, not by convention.
- **No parallel authority** — `authority == "NONE"` and one shared kernel registry, both
  asserted by a blocking gate.
- **Nothing bypasses the Meta Kernel** — every generated record roots at the kernel's
  reflective root, verified as a graph property.
- **Fail-closed** — an unusable declaration or missing substrate aborts with exit 2; no
  verdict may be asserted on unusable inputs.
