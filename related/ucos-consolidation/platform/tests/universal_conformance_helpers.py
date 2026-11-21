"""Specimen factories for the UCOS-UFC-001 conformance probe tests.

Every probe is a pure function of a declaration and a read-only context, so the honest way to
prove a probe *fails* is to hand it a capability that really is non-conformant — not to patch
the probe. These helpers build such capabilities as real, importable packages under
``tmp_path``: a probe that reads source, resolves symbols and walks a package tree gets a
genuine one to read.

Nothing here is written into the repository. Specimens live only for the test that asks for
one, so they can never become a second answer to what a Foundation capability is, and they can
never drift into a measurement of the repository's own population.
"""

from __future__ import annotations

import importlib
import sys
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from pathlib import Path
from platform.universal_foundation.conformance import (
    CapabilityDeclaration,
    CapabilityRegister,
    ProbeContext,
)
from typing import Any

#: A minimal, fully conformant specimen module. Import-pure, writes nothing, names no locator.
CONFORMANT_SOURCE = '''
"""A conformant specimen nucleus."""

from __future__ import annotations

from abc import ABC, abstractmethod

from platform.foundation.contracts import ContractRef, platform_contract
from platform.foundation.errors import PlatformError
from platform.foundation.services import ServiceDescriptor, ServiceRegistry

SPECIMEN_ID = "UCOS-SPEC-001"
SPECIMEN_VERSION = "1.0.0"
SPECIMEN_CONTRACTS: tuple[ContractRef, ...] = (ContractRef("specimen.determine", "1.0.0"),)
SERVICE_NAME = "specimen.service"


class SpecimenError(PlatformError):
    """Base class for specimen refusals."""

    code = "EC2-SPEC-000"


class SpecimenRegistryError(SpecimenError):
    """An unknown specimen member."""

    code = "EC2-SPEC-REGISTRY-001"


class SpecimenProvider(ABC):
    """The declared extension point."""

    @abstractmethod
    def provide(self) -> str:
        """Provide a member."""


class SpecimenRegistry:
    """A deterministic, fail-closed specimen registry."""

    def __init__(self) -> None:
        self._members: dict[str, str] = {}

    def ordered(self) -> tuple[str, ...]:
        return tuple(sorted(self._members))

    def require(self, name: str) -> str:
        if name not in self._members:
            raise SpecimenRegistryError("unknown specimen member", name=name)
        return self._members[name]

    def to_dict(self) -> dict[str, object]:
        return {"count": len(self._members), "members": list(self.ordered())}

    def fingerprint(self) -> str:
        return "specimen-fingerprint"


def bootstrap_specimen() -> SpecimenRegistry:
    """The one declared path into existence."""
    return SpecimenRegistry()


def specimen_descriptor() -> ServiceDescriptor:
    """The published service descriptor."""
    return ServiceDescriptor(
        name=SERVICE_NAME,
        contract=platform_contract("specimen.determine", SPECIMEN_VERSION, "Specimen."),
        capabilities=(SPECIMEN_ID,),
        description="Specimen",
    )


def register_specimen(registry: ServiceRegistry) -> ServiceDescriptor:
    """Register the specimen service."""
    return registry.register(specimen_descriptor(), bootstrap_specimen)


def specimen_cli(argv: object = None) -> int:
    """The one-command surface."""
    del argv
    return 0
'''


def declaration_document(package: str, **overrides: Any) -> dict[str, Any]:
    """The register-document form of a conformant specimen declaration."""
    document: dict[str, Any] = {
        "capability_id": "UCOS-SPEC-001",
        "name": "Specimen Capability",
        "domain": "contracts",
        "package": package,
        "identity": f"{package}.specimen:SPECIMEN_ID",
        "contracts": f"{package}.specimen:SPECIMEN_CONTRACTS",
        "version": f"{package}.specimen:SPECIMEN_VERSION",
        "service_name": "specimen.service",
        "service_descriptor": f"{package}.specimen:specimen_descriptor",
        "service_register": f"{package}.specimen:register_specimen",
        "bootstrap": f"{package}.specimen:bootstrap_specimen",
        "build": f"{package}.specimen:bootstrap_specimen",
        "errors_module": f"{package}.specimen",
        "errors_base": f"{package}.specimen:SpecimenError",
        "replay": {"writes_tracked_artifacts": False},
        "cli": f"{package}.specimen:specimen_cli",
        "entry_point": "ucos-specimen",
        "extension_points": [
            {"symbol": f"{package}.specimen:SpecimenProvider", "methods": ["provide"]}
        ],
        "registries": [
            {
                "symbol": f"{package}.specimen:SpecimenRegistry",
                "ordered": "ordered",
                "require": "require",
            }
        ],
        "catalogs": [],
        "policy_free": True,
        "dependencies": [],
        "description": "A specimen capability built for one test.",
    }
    document.update(overrides)
    return document


def declaration_for(package: str, **overrides: Any) -> CapabilityDeclaration:
    """A validated specimen declaration bound to an importable specimen package."""
    return CapabilityDeclaration.from_document(declaration_document(package, **overrides))


def register_for(
    *declarations: CapabilityDeclaration,
    governing_modules: tuple[str, ...] = ("platform.universal_foundation.conformance",),
    locator_pattern: str = r"UCOS-CONSOLIDATION",
) -> CapabilityRegister:
    """A register holding the supplied specimen declarations."""
    return CapabilityRegister(
        declarations,
        register_id="specimen.capabilities",
        locator_pattern=locator_pattern,
        governing_modules=governing_modules,
    )


def context_for(
    register: CapabilityRegister, console_scripts: Mapping[str, str] | None = None
) -> ProbeContext:
    """The read-only context a probe is given."""
    if console_scripts is None:
        first = register.ordered()[0]
        console_scripts = (
            {first.entry_point: str(first.cli)} if first.cli and first.entry_point else {}
        )
    return ProbeContext(register=register, console_scripts=dict(console_scripts))


@contextmanager
def specimen_package(
    root: Path, name: str, modules: Mapping[str, str] | None = None
) -> Iterator[str]:
    """Materialise an importable specimen package and remove it from the interpreter after.

    The package is created on disk because the probes read source: import purity, artifact
    writes and repository locators are all measured over real files, and a specimen that only
    existed in ``sys.modules`` would have none for the probe to read.
    """
    package_dir = root / name
    package_dir.mkdir(parents=True, exist_ok=True)
    (package_dir / "__init__.py").write_text('"""A specimen package."""\n', encoding="utf-8")
    payload = {"specimen.py": CONFORMANT_SOURCE} if modules is None else dict(modules)
    for filename, source in payload.items():
        (package_dir / filename).write_text(source, encoding="utf-8")
    sys.path.insert(0, str(root))
    importlib.invalidate_caches()
    try:
        yield name
    finally:
        sys.path.remove(str(root))
        for module in [key for key in sys.modules if key == name or key.startswith(f"{name}.")]:
            del sys.modules[module]
        importlib.invalidate_caches()


__all__ = [
    "CONFORMANT_SOURCE",
    "context_for",
    "declaration_document",
    "declaration_for",
    "register_for",
    "specimen_package",
]
