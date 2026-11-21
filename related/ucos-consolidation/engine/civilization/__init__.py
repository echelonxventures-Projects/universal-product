"""UCOS Ω∞ — Universal Meta-Civilization Platform (PROGRAM-004, WAVE-2).

The layer that generates constitutional operating systems. It stands to the Universal
Meta-Kernel exactly as the Universal Provider Framework does — as a **realization layer**,
holding no authority of its own:

    * The kernel (PROGRAM-002, ``engine/kernel``) defines **existence** — what a thing is: a
      governed, registered ``MetaObject`` classified by an open ``MetaType``.
    * The Provider Framework (PROGRAM-003, ``engine/provider``) defines **realization** — how
      a capability is provided.
    * This layer defines **generation** — how a whole constitutional system comes into being,
      within what dimensions it is contextualized, and in what order its capabilities compose.

Three components, one kernel:

    * :class:`~engine.civilization.dimensions.DimensionRegistry` — the **Universal Dimension
      Model**. A dimension (language, currency, country, calendar, jurisdiction, cloud,
      region, tenant, reality, existence, or an axis nobody has named) is admitted by
      registration. Two invariants are enforced at admission: every dimension satisfies every
      mandatory facet, and no dimension may legislate its own ceiling.
    * :class:`~engine.civilization.composition.CompositionPlanner` — **Dynamic Capability
      Composition**. There is no workflow and no pipeline here. A plan is derived from
      capability declarations, the requesting context, the policies in force and the available
      evidence; and the rule by which it is derived is itself a registered, replaceable
      strategy.
    * :class:`~engine.civilization.generation.ConstitutionalGenerator` — the **Constitutional
      Generation Model**. An ordered chain of registered strata through which a constitutional
      operating system is generated, every record carrying one derivation edge so the whole
      lineage roots at the kernel's reflective root.

:class:`~engine.civilization.mcos.MetaCivilizationPlatform` binds the three over a single
kernel, which is the whole of the claim that this layer adds no second registry, no second
identity scheme and no second source of truth.

Why this is not a duplicate of anything already owned:

    * It does not re-implement the kernel; it *registers into* it. No meta-model, no identity
      minting, no governance engine, no audit journal and no registry is defined here.
    * It does not duplicate ``engine/context`` (UCXI-000001), which owns context **frames,
      values and laws** — what a situation *is*. This layer owns the **dimension space** —
      which axes exist at all. The two compose: a dimension registered here is the axis a
      context value there is measured along, and neither module imports the other.
    * It does not duplicate ``05-GENERATION`` / ``platform/blueprints`` / ``engine/factory``,
      which generate **artefacts within** one operating system across six frozen families.
      This layer generates **operating systems**, one stratum above them, and touches neither.
    * It vests **no authority** in "MCOS". Authority remains where the constitution puts it;
      ``MetaCivilizationPlatform.authority`` is ``"NONE"`` and a quality gate proves it.

Everything is deterministic and content-addressed (the kernel guarantees it): no wall-clock,
no RNG, no network. An identical catalogue of registrations yields an identical platform state.
"""

from __future__ import annotations

from engine.civilization.composition import (
    CompositionPlan,
    CompositionPlanner,
    CompositionStep,
    CompositionStrategy,
    dependency_order,
    parallel_waves,
    register_strategy,
    strategy_names,
)
from engine.civilization.dimensions import DimensionRegistry
from engine.civilization.errors import (
    BlueprintUnknownError,
    CapabilityUnknownError,
    CivilizationError,
    CompositionCycleError,
    CompositionStrategyError,
    CompositionUnsatisfiedError,
    DerivationError,
    DimensionClosedError,
    DimensionUnknownError,
    StratumOrderError,
    StratumUnknownError,
)
from engine.civilization.generation import (
    GENERATION_STRATA,
    ConstitutionalGenerator,
    GenerationResult,
)
from engine.civilization.mcos import MetaCivilizationPlatform
from engine.civilization.metatypes import CIVILIZATION_FACETS, DIMENSION_FACETS
from engine.civilization.seeding import seed_facets

__layer_version__ = "1.0.0"

__all__ = [
    "MetaCivilizationPlatform",
    "DimensionRegistry",
    "CompositionPlanner",
    "CompositionPlan",
    "CompositionStep",
    "CompositionStrategy",
    "ConstitutionalGenerator",
    "GenerationResult",
    "GENERATION_STRATA",
    "CIVILIZATION_FACETS",
    "DIMENSION_FACETS",
    "dependency_order",
    "parallel_waves",
    "register_strategy",
    "strategy_names",
    "seed_facets",
    "CivilizationError",
    "DimensionUnknownError",
    "DimensionClosedError",
    "CapabilityUnknownError",
    "CompositionCycleError",
    "CompositionStrategyError",
    "CompositionUnsatisfiedError",
    "StratumUnknownError",
    "StratumOrderError",
    "BlueprintUnknownError",
    "DerivationError",
    "__layer_version__",
]
