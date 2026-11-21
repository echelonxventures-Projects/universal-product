# ADR-0004: Universal Provider Framework — kernel realization over the immutable kernel

> **Home note.** Homed in the PROGRAM-003 operational-memory directory
> (`00-MASTER/UPF-000001/`, registration-excluded) rather than the corpus `adr/` family, so
> the certification commit is self-contained and introduces no corpus-registration drift.

| Field | Value |
|-------|-------|
| Status | Accepted |
| Date | 2026-07-28 |
| Deciders | UCOS Ω∞ Provider Framework (PROGRAM-003, WAVE-2) |
| Technology Constitution refs | TP-04 (Vendor Neutrality of Core), TP-05 (Least Sufficient Technology), AR-03 (versioned contracts), DP-03 (frozen corpus read-only) |
| Supersedes | none |
| Baseline | PROGRAM-002 Universal Meta-Kernel (immutable) |

## Context

PROGRAM-003 requires the Universal Provider Framework: the constitutional realization layer
between the immutable Universal Meta-Kernel and every future implementation — kernel defines
existence, framework defines realization, providers implement behaviour. The framework must
be technology / vendor / domain independent, contain no finite provider categories, and
require no framework redesign for a previously unknown provider category.

Pre-implementation discovery (mandatory) found an existing, comprehensive **platform-layer**
Universal Provider Architecture at `platform/universal_provider/` (EC-2 "Terminal-04"):
constitution, contracts, SDK, registry, discovery, lifecycle, validation, certification,
composition, evidence, CLI. However: (a) it predates and does not reference the PROGRAM-002
kernel; (b) it contains a **closed** `ProviderState` enum — a finite enumeration PROGRAM-003
forbids; and (c) the engine layer (where the kernel lives) cannot depend on the platform
layer without inverting the architecture.

## Decision

We will implement the Universal Provider Framework at the **engine layer**
(`engine/provider/`) as the kernel realization layer, built entirely **on** the immutable
kernel and importing neither the kernel's internals-for-modification nor
`platform/universal_provider`:

1. A provider **category** is a registered kernel meta-type (open set) tagged with a
   `provider-category` role. A **provider** is a kernel `MetaObject` classified by its
   category, carrying its facets as open attributes and relationships.
2. Universal provider mechanisms — discovery, resolution, an open selection-strategy
   registry, negotiation, semantic-version compatibility, composition, open-string
   lifecycle, an open health model, metadata, policy/context binding, validation,
   certification, and traceability — are expressed generically over the kernel.
3. Provider governance is injected into the kernel's **open** governance extension point as
   constraints scoped to provider instances; the kernel package is not modified.

## Consequences

- Positive: a previously unknown provider category is admitted by registration alone; the
  kernel and framework sources are provably unchanged across the mandatory architectural
  proof (eleven categories). No finite provider categories exist; no vendor/technology token
  is baked in. Stdlib + engine only; deterministic.
- Neutral: two provider frameworks now exist at different layers. This is not duplication —
  they serve different substrates (governed kernel meta-objects vs platform descriptors) and
  the engine layer cannot depend on the platform layer. A future programme may bridge the
  platform UPA onto this kernel realization without changing this ADR.
- Reversible: providers and categories are data (registrations); nothing is frozen.

## Compliance

- [x] Non-contradiction with the constitutional corpus (CC-02) — additive; frozen corpus
      (00-BOOK, 00-SOURCE, 99-FREEZE) and the PROGRAM-002 kernel untouched (DP-03).
- [x] Rollback / migration path recorded (CC-04) — see Consequences.
- [x] Traceability recorded (CC-05) — `00-MASTER/UPF-000001/` (`upf-provider.json`,
      `05-TRACEABILITY.md`) binds every responsibility to its home.
- [x] No secret material embedded (SEC-04).
