"""Shared factories for the UCOS-UNG-001 Ω Nucleus generator tests.

Declarations are derived from the packaged register by :func:`dataclasses.replace` rather
than hand-built. A hand-built declaration would be a second answer to "what a declaration
is", and the generator's whole claim is that it renders from *the* declaration — so a test
that invented its own would stop measuring that claim.
"""

from __future__ import annotations

from dataclasses import replace
from platform.universal_foundation.conformance import (
    CapabilityDeclaration,
    default_capability_register,
)
from platform.universal_generator.contracts import ArtifactKind, GenerationTarget
from platform.universal_generator.templates import ArtifactTemplate, TemplateDescriptor

#: A declaration that answers every optional destination token.
COMPLETE_CAPABILITY = "UCOS-UNG-001"

#: A declaration that declares no catalogue, so ``{catalog_path}`` is unanswerable.
CATALOG_FREE_CAPABILITY = "UCOS-USAF-001"


def declaration(capability_id: str = COMPLETE_CAPABILITY) -> CapabilityDeclaration:
    """One declaration from the packaged register."""
    return default_capability_register().require(capability_id)


def minimal_declaration(**overrides) -> CapabilityDeclaration:
    """A declaration stripped of every optional part the templates fall back for.

    No CLI, no registries, no extension points, no catalogues, no entry point: the shape a
    nucleus takes before it has grown any of them. Every template must still render, because
    a template that only works for a fully-grown nucleus cannot generate a new one.
    """
    fields = {
        "cli": None,
        "registries": (),
        "extension_points": (),
        "catalogs": (),
        "entry_point": "",
    }
    fields.update(overrides)
    return replace(declaration(), **fields)


def target(
    target_id: str = "GT-99",
    *,
    kind: ArtifactKind = ArtifactKind.CONTRACT,
    template: str = "contract-surface",
    destination: str = "{package_path}/generated.py",
    rationale: str = "",
) -> GenerationTarget:
    """A declared generation target with sensible defaults; override any field."""
    return GenerationTarget(
        target_id=target_id,
        kind=kind,
        template=template,
        destination=destination,
        rationale=rationale,
    )


class StubTemplate(ArtifactTemplate):
    """A template that renders exactly what it was constructed with."""

    def __init__(
        self,
        name: str = "stub",
        content: str = "stub content",
        *,
        kind: ArtifactKind = ArtifactKind.CONTRACT,
    ) -> None:
        self._name = name
        self._content = content
        self._kind = kind

    def descriptor(self) -> TemplateDescriptor:
        return TemplateDescriptor(name=self._name, kind=self._kind, description="a stub")

    def render(self, declaration: CapabilityDeclaration, target: GenerationTarget) -> str:
        del declaration, target
        return self._content


class RaisingTemplate(ArtifactTemplate):
    """A template whose renderer raises, to prove faults are contained rather than escaping."""

    def __init__(self, error: BaseException, name: str = "raising") -> None:
        self._error = error
        self._name = name

    def descriptor(self) -> TemplateDescriptor:
        return TemplateDescriptor(name=self._name, kind=ArtifactKind.CONTRACT)

    def render(self, declaration: CapabilityDeclaration, target: GenerationTarget) -> str:
        del declaration, target
        raise self._error


class NonStringTemplate(ArtifactTemplate):
    """A template that returns something that is not rendered text."""

    def descriptor(self) -> TemplateDescriptor:
        return TemplateDescriptor(name="non-string", kind=ArtifactKind.CONTRACT)

    def render(self, declaration: CapabilityDeclaration, target: GenerationTarget) -> str:
        del declaration, target
        return None  # type: ignore[return-value]


__all__ = [
    "CATALOG_FREE_CAPABILITY",
    "COMPLETE_CAPABILITY",
    "NonStringTemplate",
    "RaisingTemplate",
    "StubTemplate",
    "declaration",
    "minimal_declaration",
    "target",
]
