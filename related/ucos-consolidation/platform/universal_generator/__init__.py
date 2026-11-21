"""UCOS Ω∞ — Universal Ω Nucleus Generator (``platform.universal_generator``).

**UCOS-UNG-001.** The first production generator, and the capability that makes the Foundation
a *product* rather than a body of work: every future Ω Nucleus is **generated from a
declaration** instead of engineered by hand.

One rule governs everything here:

    A declaration is the only input, and a plan is the only output.

The generator reads no filesystem, imports no nucleus it generates for, and consults nothing
about the world beyond the declaration it was handed. Anything else would let a generated
artifact depend on a fact nobody wrote down — and an artifact that depends on an unwritten fact
cannot be re-derived, which is the property the whole Foundation exists to guarantee.

It also **writes nothing**. A :class:`~platform.universal_generator.contracts.GenerationPlan`
is a complete, content-addressed statement of what would exist and where; materialising it is a
constituent act performed by whatever authority governs the Truth it would enter. That is the
same separation the Foundation already makes between measuring freeze readiness and freezing,
and it is why this nucleus can declare — truthfully, and provably against its own source under
UFC-11 — that it emits no tracked artifact.

Three declared populations, none of them enumerated in code:

    * **targets** (``catalog/ucos-generation-targets.json``) — the obligations a generation
      discharges for every nucleus. Adding an artifact to every future nucleus is an entry
      here.
    * **templates** (:class:`~platform.universal_generator.templates.ArtifactTemplate`) — the
      registered authorities that render each obligation. A different language, format or test
      shape is a registration, never an edit to the generator.
    * **nuclei** — the Foundation capability register itself. There is deliberately no second
      register: "what is the atomic unit of canonical ownership" is one constitutional model,
      and UFC-14 permits it exactly one implementation.

Destinations are resolved from tokens the declaration can answer, so the contract artifact
lands wherever the nucleus says its contract surface lives — not wherever a convention would
have put it. A token no declaration can answer is a refusal at plan time, never a guess.
"""

from __future__ import annotations

from platform.universal_generator.bootstrap import (
    GENERATION_SERVICE_NAME,
    bootstrap_nucleus_generator,
    generator_service_descriptor,
    register_nucleus_generator,
)
from platform.universal_generator.contracts import (
    GENERATION_CONTRACT_VERSION,
    GENERATION_CONTRACTS,
    UNG_ID,
    ArtifactKind,
    GeneratedArtifact,
    GenerationPlan,
    GenerationTarget,
    generation_contract_names,
)
from platform.universal_generator.errors import (
    GenerationDestinationError,
    GenerationPlanError,
    GenerationTargetError,
    GenerationTemplateError,
    GeneratorError,
)
from platform.universal_generator.generator import (
    NucleusGenerator,
    build_generator,
    destination_tokens,
    resolve_destination,
)
from platform.universal_generator.registry import (
    TargetRegister,
    TemplateRegistry,
    catalog_path,
    default_target_register,
    load_target_register,
)
from platform.universal_generator.templates import (
    GENERATED_BANNER,
    SHIPPED_TEMPLATES,
    ArtifactTemplate,
    TemplateDescriptor,
    shipped_templates,
    template_fingerprint,
)

__all__ = [
    # identity and contracts
    "UNG_ID",
    "GENERATION_CONTRACTS",
    "GENERATION_CONTRACT_VERSION",
    "generation_contract_names",
    # vocabulary
    "ArtifactKind",
    "GeneratedArtifact",
    "GenerationPlan",
    "GenerationTarget",
    # the generator
    "NucleusGenerator",
    "build_generator",
    "destination_tokens",
    "resolve_destination",
    # populations
    "TargetRegister",
    "TemplateRegistry",
    "catalog_path",
    "default_target_register",
    "load_target_register",
    # templates
    "GENERATED_BANNER",
    "SHIPPED_TEMPLATES",
    "ArtifactTemplate",
    "TemplateDescriptor",
    "shipped_templates",
    "template_fingerprint",
    # lifecycle
    "GENERATION_SERVICE_NAME",
    "bootstrap_nucleus_generator",
    "generator_service_descriptor",
    "register_nucleus_generator",
    # errors
    "GeneratorError",
    "GenerationTargetError",
    "GenerationTemplateError",
    "GenerationDestinationError",
    "GenerationPlanError",
]
