# UCOS Ω∞ — Remaining Implementation Roadmap

**Baseline:** Production Foundation checkpoint `873ef19e42242a9588d28e4a511c3f5a11a707f2`.

This roadmap is derived only from what is implemented in the repository at the
checkpoint. Nothing below exists yet unless a "Present in repository" line says
so. Each phase builds strictly on the previous one; no phase assumes future
implementation.

---

## 1. Ω Nucleus Registry

**Present in repository:** the Foundation capability register
(`foundation-capabilities.json`) loaded by
`platform.universal_foundation` — a static, catalogue-backed register of the
seven Foundation nuclei.

**To implement:** a first-class registry nucleus — registration contracts,
append-only registration lifecycle for nuclei beyond the Foundation seven,
a registry CLI, and conformance of the registry itself against
`foundation-nucleus.json`. Must reuse the existing register loading
(`load_capability_register` / `default_capability_register`) as the single
authority — no parallel register.

## 2. Ω Nucleus Discovery

**Present in repository:** `platform.repository_intelligence.discovery`
(repository-level discovery) and `engine.discovery` (registry-driven
discovery over Registry Truth).

**To implement:** discovery of Ω Nuclei specifically — measuring the
repository for packages that satisfy the nucleus contract and reconciling
discovered nuclei against the registry (phase 1). Discovery emits measured
declarations; it never registers on its own authority.

## 3. Ω Nucleus Composition

**Present in repository:** service descriptors and bootstrap functions per
nucleus (`bootstrap.*`, `service_register`), and FZ-10's proof that Foundation
dependencies resolve to a total composition order.

**To implement:** a composition engine that assembles registered nuclei into a
running composition using their declared descriptors and the total order FZ-10
already measures — dependency resolution, lifecycle ordering, fail-closed
refusal on unresolvable compositions.

## 4. Universal Generator (execution phase)

**Present in repository:** `platform.universal_generator` — 10 targets,
10 templates, deterministic plan (`ucos-generate plan`), readiness gate
(`ucos-generate readiness`). AUTHORITY = NONE (derived truth); it plans but
does not write.

**To implement:** the write phase — materializing a plan's rendered artifacts
into the repository under the registration transaction (generated artifacts
must enter through `register.sh`, like every other artifact), plus replay
evidence that generation is byte-deterministic. Resolve or formally record the
UCOS-USAF-001 GT-07 declared-absence (either USAF declares a catalogue, or the
targets document gains a declared-absence mechanism — a constitutional decision,
not a code patch).

## 5. Universal Runtime

**Present in repository:** per-nucleus CLIs (`ucos-foundation`,
`ucos-constitution`, `ucos-generate`, `ucos-measure`, …) and the EC-1 engine
runtime primitives under `engine/`.

**To implement:** a runtime that hosts composed nuclei as one operable system —
service resolution at run time, health/status surfaces (extending
`platform/*/health.py` patterns), and runtime conformance measurement (the
running system re-measured against the same constitution that froze it).

## 6. Universal Platform Composition

**Present in repository:** the platform packages themselves and the
verification pipeline that proves them individually.

**To implement:** the terminal phase — composing the full platform (Foundation
+ registry + discovery + composition + generator + runtime) into a single
certified deliverable, with a platform-level freeze determination equivalent to
FZ-01..FZ-13 measured over the whole composition.

---

## Ordering constraint (measured, not assumed)

Registry → Discovery → Composition → Generator execution → Runtime → Platform
Composition. Each phase's gate is the existing pattern: implement under the
constitution, register through the transaction, measure with
`ucos-constitution`, and only then freeze.
