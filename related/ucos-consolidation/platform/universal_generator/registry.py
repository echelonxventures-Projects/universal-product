"""UCOS-UNG-001 — The deterministic, fail-closed generation registries (UFC-05).

Two populations, two registries, one discipline: order by declared identity and never by
insertion, refuse a redefinition that conflicts with itself, and report an unknown member
rather than substituting a default.

The discipline matters more here than it looks. A generator that quietly substituted a default
template for a missing one would emit an artifact nobody declared — and that artifact would
then carry the authority of the declaration it claims to derive from.
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping
from pathlib import Path
from platform.foundation.contracts import content_hash
from platform.universal_generator.contracts import GenerationTarget
from platform.universal_generator.errors import GenerationTargetError, GenerationTemplateError
from platform.universal_generator.templates import ArtifactTemplate
from typing import Any

#: The packaged catalogue directory holding the declared generation targets.
CATALOG_DIRNAME = "catalog"

#: The declared generation target register (data, not code).
DEFAULT_TARGETS_FILENAME = "ucos-generation-targets.json"


class TemplateRegistry:
    """The registered authorities that render each declared obligation."""

    __slots__ = ("_templates",)

    def __init__(self, templates: Iterable[ArtifactTemplate] = ()) -> None:
        self._templates: dict[str, ArtifactTemplate] = {}
        for template in templates:
            self.add(template)

    def add(self, template: ArtifactTemplate) -> ArtifactTemplate:
        """Register a template, refusing a conflicting redefinition."""
        if not isinstance(template, ArtifactTemplate):
            raise GenerationTemplateError("only an ArtifactTemplate may be registered")
        name = template.name
        existing = self._templates.get(name)
        if existing is not None and type(existing) is not type(template):
            raise GenerationTemplateError(
                "template name is already registered by a different renderer",
                template=name,
                registered=type(existing).__name__,
                offered=type(template).__name__,
            )
        self._templates[name] = template
        return template

    def extend(self, templates: Iterable[ArtifactTemplate]) -> tuple[ArtifactTemplate, ...]:
        """Register several templates, in the order supplied."""
        return tuple(self.add(template) for template in templates)

    def get(self, name: str) -> ArtifactTemplate | None:
        """The template ``name``, or ``None`` when it is not registered."""
        return self._templates.get(name)

    def require(self, name: str) -> ArtifactTemplate:
        """The template ``name``; raises when unknown (fail-closed)."""
        template = self._templates.get(name)
        if template is None:
            raise GenerationTemplateError(
                "unknown template", template=name, registered=",".join(self.names())
            )
        return template

    def ordered(self) -> tuple[ArtifactTemplate, ...]:
        """Every registered template, ordered by declared name — never by insertion."""
        return tuple(self._templates[key] for key in sorted(self._templates))

    def names(self) -> tuple[str, ...]:
        """Every registered template name, in canonical order."""
        return tuple(sorted(self._templates))

    @property
    def count(self) -> int:
        """How many templates are registered."""
        return len(self._templates)

    def to_dict(self) -> dict[str, Any]:
        """A JSON-serialisable projection of this registry."""
        return {
            "count": self.count,
            "templates": [item.descriptor().to_dict() for item in self.ordered()],
        }

    def fingerprint(self) -> str:
        """The deterministic content fingerprint of this registry."""
        return content_hash(self.to_dict())


class TargetRegister:
    """The declared obligations the generator discharges for every nucleus."""

    __slots__ = ("_register_id", "_version", "_targets")

    def __init__(
        self,
        register_id: str = "",
        *,
        version: str = "",
        targets: Iterable[GenerationTarget] = (),
    ) -> None:
        self._register_id = str(register_id)
        self._version = str(version)
        self._targets: dict[str, GenerationTarget] = {}
        for target in targets:
            self.add(target)

    @property
    def register_id(self) -> str:
        """The declared identity of this register."""
        return self._register_id

    @property
    def version(self) -> str:
        """The declared semantic version of this register."""
        return self._version

    @property
    def count(self) -> int:
        """How many targets are declared."""
        return len(self._targets)

    def add(self, target: GenerationTarget) -> GenerationTarget:
        """Register a target, refusing a conflicting redefinition."""
        if not isinstance(target, GenerationTarget):
            raise GenerationTargetError("only a GenerationTarget may be registered")
        existing = self._targets.get(target.target_id)
        if existing is not None and existing != target:
            raise GenerationTargetError(
                "target is already declared with a different definition",
                target_id=target.target_id,
            )
        self._targets[target.target_id] = target
        return target

    def get(self, target_id: str) -> GenerationTarget | None:
        """The target ``target_id``, or ``None`` when it is not declared."""
        return self._targets.get(target_id)

    def require(self, target_id: str) -> GenerationTarget:
        """The target ``target_id``; raises when unknown (fail-closed)."""
        target = self._targets.get(target_id)
        if target is None:
            raise GenerationTargetError("unknown generation target", target_id=target_id)
        return target

    def ordered(self) -> tuple[GenerationTarget, ...]:
        """Every declared target, ordered by identity — never by insertion."""
        return tuple(self._targets[key] for key in sorted(self._targets))

    def ids(self) -> tuple[str, ...]:
        """Every declared target identity, in canonical order."""
        return tuple(sorted(self._targets))

    def templates(self) -> tuple[str, ...]:
        """Every template name the declared targets require, in canonical order."""
        return tuple(sorted({target.template for target in self._targets.values()}))

    @classmethod
    def from_document(cls, document: Mapping[str, Any]) -> TargetRegister:
        """Build a target register from a declared document (fail-closed)."""
        if not isinstance(document, Mapping):
            raise GenerationTargetError("generation target document must be a mapping")
        targets = document.get("targets")
        if not isinstance(targets, list) or not targets:
            raise GenerationTargetError("generation target document declares no target")
        return cls(
            str(document.get("register_id", "")),
            version=str(document.get("version", "")),
            targets=(GenerationTarget.from_document(item) for item in targets),
        )

    def to_dict(self) -> dict[str, Any]:
        """A JSON-serialisable projection of this register."""
        return {
            "register_id": self._register_id,
            "version": self._version,
            "count": self.count,
            "targets": [target.to_dict() for target in self.ordered()],
        }

    def fingerprint(self) -> str:
        """The deterministic content fingerprint of this register."""
        return content_hash(self.to_dict())


def catalog_path(filename: str = DEFAULT_TARGETS_FILENAME) -> Path:
    """The packaged catalogue path for ``filename``."""
    return Path(__file__).resolve().parent / CATALOG_DIRNAME / filename


def load_target_register(path: Path | str) -> TargetRegister:
    """Load a declared target register from ``path`` (fail-closed)."""
    target = Path(path)
    try:
        document = json.loads(target.read_text("utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise GenerationTargetError(
            "generation target register could not be read", path=str(target), detail=str(exc)
        ) from exc
    return TargetRegister.from_document(document)


def default_target_register(filename: str = DEFAULT_TARGETS_FILENAME) -> TargetRegister:
    """The target register shipped in the packaged catalogue."""
    return load_target_register(catalog_path(filename))


__all__ = [
    "CATALOG_DIRNAME",
    "DEFAULT_TARGETS_FILENAME",
    "TargetRegister",
    "TemplateRegistry",
    "catalog_path",
    "default_target_register",
    "load_target_register",
]
