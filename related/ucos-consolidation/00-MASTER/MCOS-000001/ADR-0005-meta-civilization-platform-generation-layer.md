# ADR-0005: Meta-Civilization Platform — a generation layer, not a constitutional authority

> **Home note.** Homed in the PROGRAM-004 operational-memory directory
> (`00-MASTER/MCOS-000001/`, registration-excluded) rather than the corpus `adr/` family, so
> the certification commit is self-contained and introduces no corpus-registration drift. It
> may be promoted into the corpus `adr/` family later through the normal registration
> transaction (`register.sh --guard`).

| Field | Value |
|-------|-------|
| Status | Accepted |
| Date | 2026-07-31 |
| Deciders | UCOS Ω∞ Constitutional Architecture Evolution (PROGRAM-004, WAVE-2) |
| Technology Constitution refs | TP-04 (Vendor Neutrality of Core), TP-05 (Least Sufficient Technology), AR-03 (versioned contracts), DP-03 (frozen corpus read-only), CC-02 (non-contradiction), CC-05 (traceability) |
| Supersedes | none |
| Baseline | PROGRAM-002 Universal Meta-Kernel (immutable); PROGRAM-003 Universal Provider Framework |
| Registered decisions | `DEC-MCOS-01` … `DEC-MCOS-13`, `DEC-MCOS-00R`, `DEC-MCOS-02R` (`03-ARCHITECTURAL-DECISION-ASSIMILATION-MATRIX.md` §8) |

## Context

A Constitutional Architecture Evolution mandate required the repository to institutionalize
ten constructs: a Universal Meta Kernel, MCOS, a Universal Engineering Platform, a Universal
Registry Architecture, Universal Capability Discovery, a Universal Dimension Model, a
Universal Open-World Expansion Model, a Constitutional Generation Model, Dynamic Capability
Composition, and Unlimited Constitutional Evolution — under the explicit prohibitions **DO
NOT duplicate concepts**, **DO NOT introduce competing architectures** and **DO NOT create
parallel constitutional authorities**, with Repository Truth as the only implementation
authority.

Mandatory pre-implementation discovery established that **seven of the ten already exist**:

- The **Universal Meta Kernel** is implemented at `engine/kernel/` v1.0.0 under
  `UMK-000001` / PROGRAM-002, with `ADR-0003` Accepted. It already removes the closed
  `RegistryKind` enumeration from the substrate.
- The **Universal Registry Architecture** is the kernel's `UniversalRegistry` plus
  `engine/registry/**`; `DEC-CAEM-07` records that **a second registry is prohibited**.
- **Universal Capability Discovery** is `engine/discovery/` — eight registry-driven
  dimensions with zero hard-coded patterns.
- The **Universal Open-World Expansion Model** is certified across 16 axes
  (`03-CONSTITUTIONAL-UNBOUNDEDNESS-CERTIFICATION.md`) and 23 axes
  (`04-HIDDEN-FINITE-ASSUMPTION-CERTIFICATION.md`).
- **Unlimited Constitutional Evolution** is owned by `00-CEP/CEP-009` and `UEI-000001`.
- The **Universal Engineering Platform** exists in substance as `09-PLATFORM/PLATFORM-005`
  (meta-model) and `PLATFORM-010` (composition), recorded as *CONCEPTUAL / UNNAMED* in
  `02-CANONICAL-OWNERSHIP-MATRIX.md`. `UCOS-NUCLEUS-001/02` §6 explicitly forbids making
  Meta-Platform or Platform Builder a new nucleus.
- **"MCOS"** has zero occurrences in the tracked corpus. `DEC-CAEM-13` dispositions it
  **RESOLVE-NAME** onto `MCS-000`, and `DEC-CAEM-13R` **rejects** vesting the Engineering
  Constitution / Governance / Intelligence / Validation / Certification / Evolution roles in
  it, because `MCP-001` §06 declares *no duplicate authority — MCS holds none*.

Three constructs were genuinely absent **as executable mechanism**:

1. The **dimension space** had no open registry. `engine/context/**` (UCXI-000001) owns
   context frames, values and the twelve `CXL-01…CXL-12` laws — *what a situation is* — and
   its `ContextKind` is a closed set of kinds. Nothing owned *which axes exist at all*.
2. **Declarative composition** was an outstanding decision, not a capability:
   `DEC-ADAM-14`, carried by work package `WP-UCDA-006`.
   `engine/factory/orchestrator.py::execute()` is a fixed six-step sequence, which is
   precisely what the mandate forbids ("It shall NOT be a fixed workflow. It shall NOT be a
   predefined pipeline.").
3. **Generation existed only within an operating system.** The six frozen `05-GENERATION`
   families (`BlueprintFamily`: DATA → EVENT → API → WORKFLOW → SERVICE → APPLICATION)
   produce artefacts. Nothing generated *operating systems*.

The architecture is frozen (`ARCHITECTURE_FREEZE_CERTIFIED` at `ab78f35`), and the freeze
certificate §5 permits growth only "by registration, composition, configuration, extension,
certification, and supersession — never by foundational redesign."

## Decision

We will implement the **Universal Meta-Civilization Platform** at the engine layer
(`engine/civilization/`) as a **realization layer over the immutable kernel**, in exactly the
sense PROGRAM-003 is — and it will hold **no constitutional authority**.

1. **MCOS is a generation mechanism, not an authority.**
   `MetaCivilizationPlatform.authority` is the literal string `"NONE"`, and the blocking gate
   `no-parallel-constitutional-authority` fails if that ever changes. This honours
   `DEC-CAEM-13R` while giving the name a located, executable home. Authority remains where
   the constitution puts it.

2. **One kernel, not three.** The dimension registry, the composition planner and the
   constitutional generator all admit through a single `MetaKernel`. The same gate asserts
   identity of the shared registry, so no second registry, identity scheme, governance engine
   or audit journal is introduced. `DEC-CAEM-07` is not breached.

3. **A dimension is a registered kernel meta-type.** There is no list of dimensions and no
   enumeration of dimension kinds anywhere in the layer. Two invariants are bound into the
   kernel's *existing* open admission policy as registered `Constraint`s — never by editing
   the kernel: every dimension satisfies every mandatory facet, and **no dimension may
   legislate its own ceiling** (a declaration carrying `closed_values`, `allowed_values`,
   `enum`, `max_cardinality` or `upper_bound` is refused at admission). `engine/context` is
   neither imported nor modified; the two compose, a dimension being the axis a context value
   is measured along.

4. **A plan is derived, never scripted.** Capability declarations carry requirements,
   dimension bindings, governing policies and evidence; a plan is computed from them together
   with the requesting context, the policies in force and the supplied evidence. The
   derivation rule is itself an open registry of named strategies. Requirements are declared
   by capability *key*, not minted identity, so declarations are order independent — which
   makes a declared cycle possible, so the planner detects cycles itself rather than relying
   on the kernel's relationship acyclicity. Plans are derived truth: computed, never
   registered, because registering a derivation of registered knowledge would itself breach
   Knowledge Once.

5. **An operating system is a registered kernel meta-type, and generation runs through an
   open chain of registered strata.** The nine ratified strata (Meta Kernel →
   Meta-Civilization OS → Constitutional Blueprint → Domain Constitutional OS → Nucleus →
   Universe → Capability → Component → Configured Solution) ship as DATA ordered by declared
   predecessor; a tenth is a registration. No list of operating systems appears anywhere, so
   UCOS, GCOS, HCOS, ECOS, ICOS and systems nobody has named are admitted identically.

6. **Nothing bypasses the Meta Kernel — as a graph property.** Every generated record carries
   exactly one `derives-from` edge (enforced by a registered constraint), and
   `verify_derivation` walks the lineage and refuses any result that does not root at the
   kernel's reflective root meta-type.

7. **Reuse is measured, not asserted.** Every declared responsibility carries a disposition of
   `REUSED`, `EXTENDED` or `NEW`, and `--check-reuse-before-create` fails closed if a
   responsibility claims `REUSED` while being homed inside this layer, or claims `NEW` while
   being homed outside it. Present distribution: **REUSED 9 · EXTENDED 5 · NEW 12**.

8. **The Universal Engineering Platform is named, not authored.** `MetaCivilizationPlatform`
   is the named surface of the previously *CONCEPTUAL / UNNAMED* Meta-Platform — an EXTEND of
   the located `PLATFORM-005` / `PLATFORM-010` owners, and expressly **not** a new nucleus.

## Consequences

- The mandate's success criterion is now an executed proof rather than a claim. Twelve
  previously unknown model categories (capability, dimension, universe, reality, existence,
  engineering, commercial, governance, runtime, temporal, value-exchange, observer) and five
  previously unknown constitutional operating systems are admitted by registration, bracketed
  by source fingerprints of both the layer and the kernel, proving no source byte changed.
- `WP-UCDA-006` (declarative composition, `DEC-ADAM-14`) is discharged by a located
  mechanism. `WP-UCDA-005`-adjacent naming of the Meta-Platform is discharged by EXTEND.
- The layer is stdlib-only, deterministic (no wall-clock, no RNG, no network), 100% covered on
  statement and branch, and carries no third-party or `platform.*` import — so the engine
  layer never depends on the platform layer.
- **Reversibility (CC-04).** The layer is additive and imports nothing from it exist elsewhere
  in the repository. Deleting `engine/civilization/`, `engine/tests/civilization/`,
  `00-MASTER/MCOS-000001/`, the three `pyproject.toml` lines, the Makefile block, the CI
  workflow, and the `uccep-bindings.json` / `rfp-declaration.json` entries returns the
  repository to its prior state. No existing file's behaviour is altered.
- **Exit path (TP-04).** No vendor, technology, language, currency, country, calendar,
  jurisdiction, cloud or Earth assumption exists in the layer; 21 prohibited tokens are
  proven absent from the vocabulary yet all 21 proven representable by registration.
- A future stratum inserted mid-chain requires that the affected successors' `after`
  declarations be re-registered; the ambiguity and unreachability cases are refused rather
  than silently ordered.

## Compliance

- [x] **CC-02 non-contradiction** — creates no second registry (`DEC-CAEM-07`), vests no
      authority in MCOS (`DEC-CAEM-13R`), creates no new nucleus
      (`UCOS-NUCLEUS-001/02` §6), authors no parallel architecture (`DEC-CAEM-00R`), and
      grows the frozen foundation only by registration, composition, extension and
      certification (freeze certificate §5).
- [x] **CC-04 rollback** — additive and self-contained; see Consequences.
- [x] **CC-05 traceability** — 26 responsibilities each bound to a located mechanism with a
      reuse disposition (`05-TRACEABILITY.md`); decisions registered in
      `03-ARCHITECTURAL-DECISION-ASSIMILATION-MATRIX.md` §8 and dispositioned in
      `00-MASTER/UCDA-000001/ucda-decisions.json` under CEP-002 Article 28.13.
- [x] **SEC-04 no secrets** — none introduced.
- [x] **DP-03 frozen corpus read-only** — no file under `00-BOOK/`, `00-SOURCE/`, `99-FREEZE/`
      or `05-GENERATION/` is modified; `engine/kernel/` and `engine/provider/` are unmodified
      and provably so.
