"""UCOS-UNG-001 — The Ω Nucleus generator: declarations in, artifact plans out.

One object, one rule: **a declaration is the only input**. The generator never reads a
filesystem, never imports the nucleus it generates for, and never consults anything about the
world other than the declaration it was handed and the targets and templates it was composed
from. Anything else would let a generated artifact depend on a fact that is not written down,
and an artifact that depends on an unwritten fact cannot be re-derived.

It also never writes. :class:`~platform.universal_generator.contracts.GenerationPlan` is a
determination — a complete, content-addressed statement of what would exist and where — and
materialising it is a separate constituent act performed by whatever authority governs the
Truth it would enter. This is the same separation the Foundation already makes between
measuring freeze readiness and freezing, and it is what lets this nucleus declare truthfully,
and provably against its own source, that it emits no tracked artifact.

Destinations are resolved from **declared tokens** rather than from any repository layout. A
token that the declaration cannot answer is a refusal, never a guess: a plan with a destination
nobody declared is worse than no plan at all.
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from pathlib import PurePosixPath
from platform.foundation.contracts import content_hash
from platform.universal_foundation.conformance import CapabilityDeclaration, CapabilityRegister
from platform.universal_generator.contracts import (
    GeneratedArtifact,
    GenerationPlan,
    GenerationTarget,
)
from platform.universal_generator.errors import GenerationDestinationError
from platform.universal_generator.registry import TargetRegister, TemplateRegistry
from platform.universal_generator.templates import ArtifactTemplate, shipped_templates
from typing import Any

#: The shape of a destination token. Anything else in a destination is a literal path segment.
_TOKEN = re.compile(r"\{([a-z_]+)\}")


def _module_path(module: str) -> str:
    """The source path a dotted module name occupies, as a POSIX-relative locator."""
    return str(PurePosixPath(*module.split("."))) + ".py"


def destination_tokens(declaration: CapabilityDeclaration) -> dict[str, str]:
    """Every destination token this declaration can answer.

    Each token is derived from something the declaration *already says*, which is what keeps
    destinations free of repository knowledge: the contract artifact belongs wherever the
    declaration says its contract surface lives, not wherever a convention would have put it.
    """
    package_path = str(PurePosixPath(*declaration.package.split(".")))
    tokens = {
        "capability_id": declaration.capability_id,
        "slug": declaration.package.rsplit(".", 1)[-1],
        "package": declaration.package,
        "package_path": package_path,
        "contracts_path": _module_path(declaration.contracts.module),
        "errors_path": _module_path(declaration.errors_module),
        "bootstrap_path": _module_path(declaration.bootstrap.module),
        "service_name": declaration.service_name,
    }
    if declaration.cli is not None:
        tokens["cli_path"] = _module_path(declaration.cli.module)
    if declaration.registries:
        tokens["registry_path"] = _module_path(declaration.registries[0].symbol.module)
    if declaration.catalogs:
        tokens["catalog_path"] = str(PurePosixPath(package_path, declaration.catalogs[0]))
    if declaration.entry_point:
        tokens["entry_point"] = declaration.entry_point
    return tokens


def resolve_destination(pattern: str, declaration: CapabilityDeclaration) -> str:
    """Resolve a declared destination pattern against a declaration (fail-closed)."""
    tokens = destination_tokens(declaration)
    unresolved = sorted({name for name in _TOKEN.findall(pattern) if name not in tokens})
    if unresolved:
        raise GenerationDestinationError(
            "destination pattern names a token this declaration cannot answer",
            capability_id=declaration.capability_id,
            pattern=pattern,
            unresolved=",".join(unresolved),
            available=",".join(sorted(tokens)),
        )
    return _TOKEN.sub(lambda match: tokens[match.group(1)], pattern)


class NucleusGenerator:
    """Determines the complete constitutional artifact set for any Ω Nucleus declaration."""

    __slots__ = ("_targets", "_templates")

    def __init__(self, targets: TargetRegister, templates: TemplateRegistry) -> None:
        if not isinstance(targets, TargetRegister):
            raise GenerationDestinationError("generation requires a TargetRegister")
        if not isinstance(templates, TemplateRegistry):
            raise GenerationDestinationError("generation requires a TemplateRegistry")
        self._targets = targets
        self._templates = templates
        # Fail at composition rather than at render: a target naming a template nobody
        # registered is a plan that would have been silently short by one artifact.
        for name in targets.templates():
            templates.require(name)

    @property
    def targets(self) -> TargetRegister:
        """The declared obligations this generator discharges."""
        return self._targets

    @property
    def templates(self) -> TemplateRegistry:
        """The registered authorities that render those obligations."""
        return self._templates

    def unbound_targets(self) -> tuple[str, ...]:
        """Declared targets whose template is not registered. Always empty after composition."""
        return tuple(
            target.target_id
            for target in self._targets.ordered()
            if self._templates.get(target.template) is None
        )

    def render(
        self, declaration: CapabilityDeclaration, target: GenerationTarget
    ) -> GeneratedArtifact:
        """Render one declared obligation for one nucleus."""
        template = self._templates.require(target.template)
        destination = resolve_destination(target.destination, declaration)
        return GeneratedArtifact.create(target, destination, template.apply(declaration, target))

    def generate(self, declaration: CapabilityDeclaration) -> GenerationPlan:
        """Determine the complete artifact set for one nucleus."""
        if not isinstance(declaration, CapabilityDeclaration):
            raise GenerationDestinationError(
                "generation requires a CapabilityDeclaration — the nucleus's own declaration"
            )
        return GenerationPlan.create(
            declaration.capability_id,
            (self.render(declaration, target) for target in self._targets.ordered()),
        )

    def generate_all(self, register: CapabilityRegister) -> tuple[GenerationPlan, ...]:
        """Determine the artifact set for every nucleus in a register, in declared order."""
        if not isinstance(register, CapabilityRegister):
            raise GenerationDestinationError("generation over a population requires a register")
        return tuple(self.generate(declaration) for declaration in register.ordered())

    def can_generate(self, declaration: CapabilityDeclaration) -> tuple[str, ...]:
        """Every declared target this declaration cannot answer, in canonical order.

        Empty means the Foundation can generate this nucleus in full. This is the Phase 6
        question — *can* the Foundation generate — asked without generating anything.
        """
        findings: list[str] = []
        for target in self._targets.ordered():
            try:
                resolve_destination(target.destination, declaration)
            except GenerationDestinationError as exc:
                findings.append(f"{target.target_id}: {exc}")
        return tuple(findings)

    def to_dict(self) -> dict[str, Any]:
        """A JSON-serialisable projection of this generator's composition."""
        return {
            "targets": self._targets.to_dict(),
            "templates": self._templates.to_dict(),
            "unbound_targets": list(self.unbound_targets()),
        }

    def fingerprint(self) -> str:
        """The deterministic content fingerprint of this generator's composition."""
        return content_hash(self.to_dict())


def build_generator(
    targets: TargetRegister, templates: Iterable[ArtifactTemplate] | None = None
) -> NucleusGenerator:
    """Compose a generator over ``targets``, seeded with the shipped templates by default."""
    registry = TemplateRegistry(shipped_templates() if templates is None else templates)
    return NucleusGenerator(targets, registry)


__all__ = [
    "NucleusGenerator",
    "build_generator",
    "destination_tokens",
    "resolve_destination",
]
