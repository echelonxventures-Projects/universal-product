"""UCOS-CTRL-000001 — Control Plane Registration (Wave 8).

A control plane that governs everything except itself has an exemption at its
centre. This module removes it: every engine in the package is discovered,
registered, owned, versioned and linked into the same registries the control
plane uses for everything else.

The engine list is *measured, not declared*. Nothing here — and nothing in the
manifest — names ``PlanEngine`` or ``VersionEngine``. The package's own modules
are enumerated, each is imported, and every class it defines whose name matches a
declared suffix becomes a registered control-plane object. Adding a new engine
therefore registers it; deleting one deregisters it; and a registration list can
never quietly drift from the code it claims to describe, because there is no list.

Each registration carries the six things the constitution requires an object to
have:

    identity      content-addressed from the object's own coordinates
    registration  a record in the capability registry
    lineage       the containment chain universe → layer → module → engine
    ownership     a binding in the ownership registry
    governance    resolved by the Governance Engine over the registration
    certification assessed by the Certification Engine over that governance

The last two are not performed here — they are performed *on* what this module
produces, which is the point: registration makes an engine a subject like any
other rather than a special case.
"""

from __future__ import annotations

import importlib
import inspect
import pkgutil
from collections.abc import Iterable
from dataclasses import dataclass, field
from platform.universal_control_plane.errors import ObjectNotFoundError, RegistrationError
from platform.universal_control_plane.manifest import ControlPlaneManifest, default_manifest
from platform.universal_control_plane.ontology import (
    LIFECYCLE_ACTIVE,
    Capability,
    DependencyRecord,
    OwnershipRecord,
    RegistrationRecord,
)
from platform.universal_control_plane.registry import (
    CapabilityRegistry,
    DependencyRegistry,
    OwnershipRegistry,
)
from typing import Any

#: The package whose engines are registered. Resolved from this module's own
#: position so the control plane cannot be pointed at the wrong package by a typo.
CONTROL_PLANE_PACKAGE = __name__.rsplit(".", 1)[0]

#: Modules excluded from engine discovery: they define no engine, and importing a
#: CLI during discovery would run argument parsing machinery for nothing.
EXCLUDED_MODULES: frozenset[str] = frozenset({"cli", "__main__"})

SUBJECT_KIND_ENGINE = "Engine"


@dataclass(frozen=True, slots=True)
class EngineDescriptor:
    """One discovered control-plane engine class."""

    name: str
    module: str
    layer: str
    description: str = ""
    version: str = "1.0.0"

    @property
    def subject_id(self) -> str:
        """The engine's stable identifier: its fully qualified class path."""
        return f"{self.module}.{self.name}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "module": self.module,
            "layer": self.layer,
            "subject_id": self.subject_id,
            "description": self.description,
            "version": self.version,
        }


def discover_engines(
    manifest: ControlPlaneManifest | None = None, *, package: str = CONTROL_PLANE_PACKAGE
) -> tuple[EngineDescriptor, ...]:
    """Enumerate every control-plane engine class by introspecting *package*.

    A class is admitted when its name matches a declared suffix **and** it is
    defined in the module being inspected. The second condition is what keeps
    re-exports from registering the same engine once per module that imports it.
    """
    resolved = manifest or default_manifest()
    taxonomy = resolved.engine_taxonomy
    root = importlib.import_module(package)

    descriptors: dict[str, EngineDescriptor] = {}
    for info in sorted(pkgutil.iter_modules(root.__path__), key=lambda m: m.name):
        if info.ispkg or info.name in EXCLUDED_MODULES or info.name.startswith("_"):
            continue
        module_name = f"{package}.{info.name}"
        module = importlib.import_module(module_name)
        layer = taxonomy.layer_for(module_name)
        for name, obj in sorted(vars(module).items()):
            if not inspect.isclass(obj) or obj.__module__ != module_name:
                continue
            if not taxonomy.is_engine_class(name):
                continue
            descriptor = EngineDescriptor(
                name=name,
                module=module_name,
                layer=layer,
                description=_docline(obj),
            )
            descriptors[descriptor.subject_id] = descriptor
    return tuple(descriptors[key] for key in sorted(descriptors))


def _docline(obj: type) -> str:
    """The first line of a class docstring — its self-description, if it has one."""
    doc = inspect.getdoc(obj) or ""
    return doc.splitlines()[0].strip() if doc else ""


@dataclass
class RegistrationEngine:
    """Registers every discovered control-plane engine into the control plane."""

    manifest: ControlPlaneManifest = field(default_factory=default_manifest)
    capability_registry: CapabilityRegistry = field(default_factory=CapabilityRegistry)
    ownership_registry: OwnershipRegistry = field(default_factory=OwnershipRegistry)
    dependency_registry: DependencyRegistry = field(default_factory=DependencyRegistry)
    _registrations: dict[str, RegistrationRecord] = field(default_factory=dict)
    _descriptors: dict[str, EngineDescriptor] = field(default_factory=dict)

    # -- registration ----------------------------------------------------

    def register(self, descriptor: EngineDescriptor, *, tick: int = 0) -> RegistrationRecord:
        """Register one engine: capability, ownership, lineage and record."""
        subject_id = descriptor.subject_id
        if subject_id in self._registrations:
            raise RegistrationError(f"engine already registered: {subject_id}")

        universe_id = self.manifest.universe_id
        capability = Capability(
            capability_id=subject_id,
            universe_id=universe_id,
            name=descriptor.name,
            description=descriptor.description,
            state=LIFECYCLE_ACTIVE,
            version=descriptor.version,
            attributes={"layer": descriptor.layer, "module": descriptor.module},
            tick=tick,
        )
        self.capability_registry.register(capability)
        self.ownership_registry.register(
            OwnershipRecord(
                ownership_id=f"OWN-{subject_id}",
                capability_id=subject_id,
                owner_id=universe_id,
                owner_kind="Universe",
                rationale=(
                    f"{descriptor.name} is a constitutional capability of {universe_id} "
                    f"in the {descriptor.layer} layer"
                ),
                tick=tick,
            )
        )

        record = RegistrationRecord(
            registration_id=f"REG-{subject_id}",
            subject_id=subject_id,
            subject_kind=SUBJECT_KIND_ENGINE,
            name=descriptor.name,
            module=descriptor.module,
            layer=descriptor.layer,
            universe_id=universe_id,
            owner_id=universe_id,
            capability_id=subject_id,
            lineage=self.lineage_for(descriptor),
            description=descriptor.description,
            attributes={"version": descriptor.version},
            tick=tick,
        )
        self._registrations[subject_id] = record
        self._descriptors[subject_id] = descriptor
        return record

    def register_all(
        self, descriptors: Iterable[EngineDescriptor] | None = None, *, tick: int = 0
    ) -> tuple[RegistrationRecord, ...]:
        """Discover and register every engine, then wire the dependency graph."""
        pool = tuple(descriptors) if descriptors is not None else discover_engines(self.manifest)
        records = tuple(
            self.register(descriptor, tick=tick)
            for descriptor in sorted(pool, key=lambda d: d.subject_id)
        )
        self._wire_dependencies(tick=tick)
        return records

    def _wire_dependencies(self, *, tick: int = 0) -> None:
        """Register an edge from every engine to every engine in a layer it depends on.

        The edges are derived from the declared layer graph rather than from
        imports: a layer dependency is an architectural commitment, and measuring
        it from imports would record what the code happens to do instead of what
        the constitution requires it to do.
        """
        taxonomy = self.manifest.engine_taxonomy
        by_layer: dict[str, list[str]] = {}
        for subject_id, descriptor in self._descriptors.items():
            by_layer.setdefault(descriptor.layer, []).append(subject_id)

        for subject_id in sorted(self._descriptors):
            descriptor = self._descriptors[subject_id]
            for layer in taxonomy.dependencies_of(descriptor.layer):
                for target in sorted(by_layer.get(layer, ())):
                    if target == subject_id:
                        continue
                    dependency_id = f"DEP-{subject_id}->{target}"
                    if dependency_id in {d.dependency_id for d in self.dependency_registry.all()}:
                        continue
                    self.dependency_registry.register(
                        DependencyRecord(
                            dependency_id=dependency_id,
                            from_id=subject_id,
                            to_id=target,
                            kind="REQUIRES",
                            attributes={"from_layer": descriptor.layer, "to_layer": layer},
                            tick=tick,
                        )
                    )

    # -- lineage ---------------------------------------------------------

    def lineage_for(self, descriptor: EngineDescriptor) -> tuple[str, ...]:
        """The containment chain that places an engine in the constitution."""
        universe_id = self.manifest.universe_id
        return (
            universe_id,
            f"{universe_id}::{descriptor.layer}",
            f"{universe_id}::{descriptor.layer}::{descriptor.module}",
        )

    def lineage_of(self, subject_id: str) -> tuple[str, ...]:
        return self.registration_of(subject_id).lineage

    # -- queries ---------------------------------------------------------

    def registration_of(self, subject_id: str) -> RegistrationRecord:
        if subject_id not in self._registrations:
            raise ObjectNotFoundError(f"engine not registered: {subject_id}")
        return self._registrations[subject_id]

    def registrations(self) -> tuple[RegistrationRecord, ...]:
        return tuple(self._registrations[key] for key in sorted(self._registrations))

    def descriptors(self) -> tuple[EngineDescriptor, ...]:
        return tuple(self._descriptors[key] for key in sorted(self._descriptors))

    def by_layer(self, layer: str) -> tuple[RegistrationRecord, ...]:
        return tuple(r for r in self.registrations() if r.layer == layer)

    def layers(self) -> tuple[str, ...]:
        return tuple(sorted({r.layer for r in self.registrations()}))

    def names(self) -> tuple[str, ...]:
        """Every registered engine's class name — what the completion gate counts."""
        return tuple(sorted(r.name for r in self.registrations()))

    def is_registered(self, name: str) -> bool:
        """Whether an engine of this class *name* is registered, module-independent."""
        return any(r.name == name for r in self.registrations())

    def count(self) -> int:
        return len(self._registrations)

    def unclassified(self) -> tuple[RegistrationRecord, ...]:
        """Engines whose module the manifest assigns to no layer — a declaration gap."""
        return tuple(r for r in self.registrations() if r.layer == "UNCLASSIFIED")

    # -- projection ------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        return {
            "engine": "RegistrationEngine",
            "universe_id": self.manifest.universe_id,
            "counts": {
                "registered": self.count(),
                "layers": len(self.layers()),
                "capabilities": self.capability_registry.count(),
                "ownership": self.ownership_registry.count(),
                "dependencies": self.dependency_registry.count(),
                "unclassified": len(self.unclassified()),
            },
            "layers": list(self.layers()),
            "registrations": [r.to_dict() for r in self.registrations()],
        }


__all__ = [
    "CONTROL_PLANE_PACKAGE",
    "EXCLUDED_MODULES",
    "SUBJECT_KIND_ENGINE",
    "EngineDescriptor",
    "RegistrationEngine",
    "discover_engines",
]
