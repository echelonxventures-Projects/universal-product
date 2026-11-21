"""UCOS-UNG-001 — Ω Nucleus generator bootstrap & service registration.

Composes the generator from its **declared** targets and its **registered** templates, and
publishes it as a first-class platform service, so generation is something a project resolves
rather than something each programme re-implements.

The composition is declared end to end: which artifacts a generation produces is
``catalog/ucos-generation-targets.json``, and which authority renders each of them is a
template registration. Passing an explicit register specialises the first; passing explicit
templates specialises the second. With neither, the packaged declaration governs — never a
hardcoded artifact list.
"""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from platform.foundation.contracts import platform_contract
from platform.foundation.services import ServiceDescriptor, ServiceRegistry
from platform.universal_generator.contracts import GENERATION_CONTRACT_VERSION, UNG_ID
from platform.universal_generator.generator import NucleusGenerator, build_generator
from platform.universal_generator.registry import (
    TargetRegister,
    default_target_register,
    load_target_register,
)
from platform.universal_generator.templates import ArtifactTemplate

#: The service name under which Ω Nucleus generation is published.
GENERATION_SERVICE_NAME = "universal.generation.nucleus"


def bootstrap_nucleus_generator(
    targets: TargetRegister | Path | str | None = None,
    *,
    templates: Iterable[ArtifactTemplate] | None = None,
) -> NucleusGenerator:
    """Compose the Ω Nucleus generator from its declared targets and registered templates."""
    if targets is None:
        resolved = default_target_register()
    elif isinstance(targets, TargetRegister):
        resolved = targets
    else:
        resolved = load_target_register(targets)
    return build_generator(resolved, templates)


def generator_service_descriptor() -> ServiceDescriptor:
    """The published service descriptor for Ω Nucleus generation."""
    return ServiceDescriptor(
        name=GENERATION_SERVICE_NAME,
        contract=platform_contract(
            "generation.nucleus.plan",
            GENERATION_CONTRACT_VERSION,
            "Determine the complete constitutional artifact set for one Ω Nucleus declaration.",
        ),
        capabilities=(UNG_ID,),
        description="Universal Ω Nucleus Generator — declarations in, artifact plans out.",
    )


def register_nucleus_generator(
    registry: ServiceRegistry,
    *,
    targets: TargetRegister | Path | str | None = None,
    templates: Iterable[ArtifactTemplate] | None = None,
) -> ServiceDescriptor:
    """Register Ω Nucleus generation into ``registry`` (lazy, memoised)."""
    return registry.register(
        generator_service_descriptor(),
        lambda: bootstrap_nucleus_generator(targets, templates=templates),
    )


__all__ = [
    "GENERATION_SERVICE_NAME",
    "bootstrap_nucleus_generator",
    "generator_service_descriptor",
    "register_nucleus_generator",
]
