"""UCOS-UFC-001 — Executable conformance against the Universal Foundation Constitution.

The Constitution is only law if it is *measured*. This module measures it: one probe per
declared gate, executed against every Foundation capability the **capability register**
declares, producing a determination in which every verdict is traceable to the article that
demanded it and to the evidence that decided it.

What makes this an honest measurement rather than a status board
---------------------------------------------------------------
Every probe executes a real, deterministic observation over the *live* capability and
records what it observed:

    * contracts are **resolved and version-checked**, not asserted;
    * services are **registered into a fresh registry, validated and resolved**;
    * extension points are **introspected** for abstractness and declared methods;
    * declared catalogues are **read and parsed**;
    * import-time purity is measured by **AST inspection of module-level calls**;
    * determinism is measured by **building twice and comparing fingerprints**;
    * composition is measured by **resolving declared dependencies and the real import graph**;
    * specialisation is measured by **searching module sources for repository locators**.

A probe that cannot execute is a **FAULT**, never a pass. Absence of evidence is never
evidence (UFC-10).

Zero enumeration
----------------
This module names no capability. The population is the register
(``catalog/foundation-capabilities.json``), and UFC-09 is itself measured by proving that no
governing module — this one included — contains any capability identity from that register.
"""

from __future__ import annotations

import ast
import importlib
import json
import re
import tomllib
from abc import ABC, abstractmethod
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from platform.foundation.contracts import ContractRef, content_hash
from platform.foundation.errors import PlatformError
from platform.foundation.services import ServiceDescriptor, ServiceRegistry
from platform.universal_foundation.constitution import (
    MATURITY_GATES,
    ConstitutionalDomain,
    FoundationArticle,
    FoundationConstitution,
    MaturityAxis,
    foundation_constitution,
    require_gates,
)
from platform.universal_foundation.errors import FoundationConformanceError
from typing import Any

#: The packaged catalogue directory holding the declared capability register.
CATALOG_DIRNAME = "catalog"

#: The declared Foundation capability register (data, not code).
DEFAULT_REGISTER_FILENAME = "foundation-capabilities.json"

#: Semantic-version shape every declared contract surface must satisfy (UFC-08).
_SEMVER = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")

#: Callables whose appearance at *module level* proves an import-time side effect (UFC-07).
IMPORT_PURITY_FORBIDDEN: tuple[str, ...] = (
    "open",
    "read_text",
    "read_bytes",
    "write_text",
    "write_bytes",
    "load",
    "loads",
    "run",
    "urlopen",
    "connect",
    "system",
)

#: Package sub-paths never inspected as source (compiled residue and declared data).
_SOURCE_EXCLUDED = ("__pycache__",)

#: Callables whose appearance *anywhere* in a capability's source proves that the capability
#: emits an artifact — that is, that its determinations can become Repository Truth (UFC-11).
#: This is the write half of :data:`IMPORT_PURITY_FORBIDDEN`, which measures the same
#: vocabulary at module level for a different article; the two are deliberately disjoint in
#: scope and share no verdict. Every name here is an unambiguous filesystem artifact
#: operation: ``replace`` and ``dumps`` are deliberately absent, because ``str.replace`` and
#: ``json.dumps`` are pure and would make the measurement lie — and a measurement that lies is
#: worse than no measurement at all (UFC-10).
ARTIFACT_WRITE_CALLS: tuple[str, ...] = (
    "write_text",
    "write_bytes",
    "mkdir",
    "touch",
    "rename",
    "unlink",
    "rmdir",
    "dump",
)


class Verdict(str, Enum):
    """The outcome of one probe. There is deliberately no fourth, softer value."""

    #: The article is satisfied by observed evidence.
    PASS = "PASS"  # noqa: S105 - a constitutional verdict, not a credential
    #: The article is not satisfied; the finding names what is missing.
    FAIL = "FAIL"
    #: The probe could not execute, so no verdict may be asserted (fail-closed).
    FAULT = "FAULT"

    @property
    def satisfied(self) -> bool:
        """Whether this verdict discharges the article."""
        return self is Verdict.PASS


@dataclass(frozen=True, slots=True)
class SymbolRef:
    """A declared ``module:attribute`` reference, resolved on demand and never at import."""

    module: str
    attribute: str

    @classmethod
    def parse(cls, value: Any, *, context: str = "symbol") -> SymbolRef:
        """Parse ``module:attribute`` (fail-closed on any other shape)."""
        if not isinstance(value, str) or value.count(":") != 1:
            raise FoundationConformanceError(
                "symbol reference must be 'module:attribute'", subject=context, value=str(value)
            )
        module, attribute = value.split(":", 1)
        if not module.strip() or not attribute.strip():
            raise FoundationConformanceError(
                "symbol reference is incomplete", subject=context, value=value
            )
        return cls(module=module.strip(), attribute=attribute.strip())

    def resolve(self) -> Any:
        """Import the module and return the attribute (fail-closed)."""
        try:
            module = importlib.import_module(self.module)
        except Exception as exc:  # noqa: BLE001 - contained by design (fail-closed)
            raise FoundationConformanceError(
                "declared module could not be imported", module=self.module, detail=str(exc)
            ) from exc
        try:
            return getattr(module, self.attribute)
        except AttributeError as exc:
            raise FoundationConformanceError(
                "declared attribute is absent",
                module=self.module,
                attribute=self.attribute,
            ) from exc

    def __str__(self) -> str:
        return f"{self.module}:{self.attribute}"


@dataclass(frozen=True, slots=True)
class ExtensionPointDeclaration:
    """A declared extension point through which a capability admits new authority (UFC-03)."""

    symbol: SymbolRef
    abstract: bool = True
    methods: tuple[str, ...] = ()

    @classmethod
    def from_document(cls, payload: Mapping[str, Any]) -> ExtensionPointDeclaration:
        """Build from a declared mapping."""
        if not isinstance(payload, Mapping) or "symbol" not in payload:
            raise FoundationConformanceError("extension point requires 'symbol'")
        return cls(
            symbol=SymbolRef.parse(payload["symbol"], context="extension point"),
            abstract=bool(payload.get("abstract", True)),
            methods=tuple(str(item) for item in payload.get("methods", ())),
        )

    def to_dict(self) -> dict[str, Any]:
        """A JSON-serialisable projection."""
        return {
            "symbol": str(self.symbol),
            "abstract": self.abstract,
            "methods": list(self.methods),
        }


@dataclass(frozen=True, slots=True)
class RegistryDeclaration:
    """A declared deterministic, fail-closed registry surface (UFC-05)."""

    symbol: SymbolRef
    ordered: str
    require: str

    @classmethod
    def from_document(cls, payload: Mapping[str, Any]) -> RegistryDeclaration:
        """Build from a declared mapping."""
        if not isinstance(payload, Mapping):
            raise FoundationConformanceError("registry declaration must be a mapping")
        missing = [key for key in ("symbol", "ordered", "require") if key not in payload]
        if missing:
            raise FoundationConformanceError(
                "registry declaration is incomplete", missing=",".join(missing)
            )
        return cls(
            symbol=SymbolRef.parse(payload["symbol"], context="registry"),
            ordered=str(payload["ordered"]),
            require=str(payload["require"]),
        )

    def to_dict(self) -> dict[str, Any]:
        """A JSON-serialisable projection."""
        return {"symbol": str(self.symbol), "ordered": self.ordered, "require": self.require}


@dataclass(frozen=True, slots=True)
class ReplayDeclaration:
    """A declared replay posture: whether a capability's outputs become Repository Truth.

    UFC-11 requires a capability that emits artifacts to be re-measurable at the commit that
    carries them, because a committed artifact cannot carry the sha of the commit that carries
    it — so a register rendered before its own commit drifts by exactly one field forever.

    The declaration is never trusted. :func:`probe_certifiable` measures the capability's own
    source against :data:`ARTIFACT_WRITE_CALLS` and fails the article when the declaration and
    the measurement disagree in *either* direction: an undeclared writer is an ungated
    register, and a phantom writer is a replay obligation nobody can discharge.
    """

    writes_tracked_artifacts: bool = False
    target: SymbolRef | None = None

    @classmethod
    def from_document(cls, payload: Mapping[str, Any], *, capability_id: str) -> ReplayDeclaration:
        """Build from a declared mapping (fail-closed)."""
        if not isinstance(payload, Mapping):
            raise FoundationConformanceError(
                "replay declaration must be a mapping", capability_id=capability_id
            )
        if "writes_tracked_artifacts" not in payload:
            raise FoundationConformanceError(
                "replay declaration must state 'writes_tracked_artifacts'",
                capability_id=capability_id,
            )
        writes = bool(payload["writes_tracked_artifacts"])
        target = payload.get("target")
        if writes and not target:
            raise FoundationConformanceError(
                "a capability that writes tracked artifacts must declare a replay target",
                capability_id=capability_id,
            )
        if target and not writes:
            raise FoundationConformanceError(
                "a replay target is declared but the capability declares no tracked output",
                capability_id=capability_id,
            )
        return cls(
            writes_tracked_artifacts=writes,
            target=SymbolRef.parse(target, context=capability_id) if target else None,
        )

    def to_dict(self) -> dict[str, Any]:
        """A JSON-serialisable projection."""
        return {
            "writes_tracked_artifacts": self.writes_tracked_artifacts,
            "target": str(self.target) if self.target else "",
        }


class FacetStatus(str, Enum):
    """How a declared nucleus facet stands. There is deliberately no third, softer value."""

    #: The facet is realised, and the declaration names the evidence that realises it.
    PRESENT = "present"
    #: The facet does not apply to this nucleus, and the declaration says why.
    NOT_APPLICABLE = "not-applicable"

    @classmethod
    def coerce(cls, value: Any, *, subject: str) -> FacetStatus:
        """Coerce ``value`` to a status, failing closed (never silently)."""
        if isinstance(value, cls):
            return value
        if isinstance(value, str):
            try:
                return cls(value)
            except ValueError as exc:
                raise FoundationConformanceError(
                    "unknown nucleus facet status", subject=subject, value=value
                ) from exc
        raise FoundationConformanceError("nucleus facet status must be a string", subject=subject)


@dataclass(frozen=True, slots=True)
class FacetDeclaration:
    """One leaf of a nucleus profile: a facet path, its status, and the reason for it."""

    path: str
    status: FacetStatus
    detail: str

    @property
    def present(self) -> bool:
        """Whether the facet is declared realised rather than declared inapplicable."""
        return self.status is FacetStatus.PRESENT

    def to_dict(self) -> dict[str, Any]:
        """A JSON-serialisable projection."""
        return {"path": self.path, "status": self.status.value, "detail": self.detail}


@dataclass(frozen=True, slots=True)
class NucleusProfile:
    """A nucleus's declared facet profile, flattened to dotted paths.

    The profile is the only place a capability may answer a facet that no constitutional gate
    already proves. It is deliberately *flat*: the declaration document may nest for
    readability, but a facet is addressed by one dotted path, so the contract can name a facet
    without knowing how the document happens to be grouped.

    Every leaf SHALL state a status and the reason for it — ``evidence`` when the facet is
    present, ``rationale`` when it does not apply. A leaf that states one without the other is
    refused at construction: "somebody wrote a key" is not a determination.
    """

    entries: tuple[FacetDeclaration, ...] = ()

    @classmethod
    def from_document(cls, payload: Any, *, capability_id: str) -> NucleusProfile:
        """Flatten a declared profile document into dotted facet paths (fail-closed)."""
        if payload is None:
            return cls()
        collected: list[FacetDeclaration] = []
        if isinstance(payload, Sequence) and not isinstance(payload, str | bytes):
            # The projection form emitted by :meth:`to_dict` — already flat, already resolved.
            # Accepting it is what makes the declaration round-trip: a register entry read,
            # projected and read back SHALL yield the same declaration, or the register cannot
            # be re-derived from its own output (UFC-11).
            collected = [cls._projected(item, capability_id=capability_id) for item in payload]
        elif isinstance(payload, Mapping):
            # The authoring form — nested for readability, flattened here.
            cls._walk(payload, (), collected, capability_id=capability_id)
        else:
            raise FoundationConformanceError(
                "nucleus profile must be a mapping or a projected sequence",
                capability_id=capability_id,
            )
        return cls(entries=tuple(sorted(collected, key=lambda item: item.path)))

    @staticmethod
    def _projected(value: Any, *, capability_id: str) -> FacetDeclaration:
        """Rebuild one leaf from the projected form (fail-closed, never guessing)."""
        if not isinstance(value, Mapping):
            raise FoundationConformanceError(
                "projected nucleus facet must be a mapping", capability_id=capability_id
            )
        missing = [key for key in ("path", "status", "detail") if key not in value]
        if missing:
            raise FoundationConformanceError(
                "projected nucleus facet is incomplete",
                capability_id=capability_id,
                missing=",".join(missing),
            )
        path = str(value["path"]).strip()
        detail = str(value["detail"]).strip()
        if not path or not detail:
            raise FoundationConformanceError(
                "projected nucleus facet states no path or no reason",
                capability_id=capability_id,
                subject=path,
            )
        return FacetDeclaration(
            path=path,
            status=FacetStatus.coerce(value["status"], subject=f"{capability_id}:{path}"),
            detail=detail,
        )

    @classmethod
    def _walk(
        cls,
        payload: Mapping[str, Any],
        prefix: tuple[str, ...],
        collected: list[FacetDeclaration],
        *,
        capability_id: str,
    ) -> None:
        """Recurse into the declared document, collecting leaves. Comment keys are skipped."""
        for key in sorted(str(name) for name in payload):
            if key.startswith("$"):
                continue
            value = payload[key]
            path = ".".join((*prefix, key))
            if not isinstance(value, Mapping):
                raise FoundationConformanceError(
                    "nucleus profile entry must be a mapping",
                    capability_id=capability_id,
                    subject=path,
                )
            if "status" not in value:
                cls._walk(value, (*prefix, key), collected, capability_id=capability_id)
                continue
            collected.append(cls._leaf(value, path, capability_id=capability_id))

    @staticmethod
    def _leaf(value: Mapping[str, Any], path: str, *, capability_id: str) -> FacetDeclaration:
        """Build one validated leaf. The reason a facet stands as it does is mandatory."""
        status = FacetStatus.coerce(value["status"], subject=f"{capability_id}:{path}")
        key = "evidence" if status is FacetStatus.PRESENT else "rationale"
        detail = str(value.get(key, "")).strip()
        if not detail:
            raise FoundationConformanceError(
                f"nucleus facet declared '{status.value}' states no {key}",
                capability_id=capability_id,
                subject=path,
            )
        return FacetDeclaration(path=path, status=status, detail=detail)

    def get(self, path: str) -> FacetDeclaration | None:
        """The declaration at ``path``, or ``None`` when the profile is silent about it."""
        for entry in self.entries:
            if entry.path == path:
                return entry
        return None

    def paths(self) -> tuple[str, ...]:
        """Every declared facet path, in canonical order."""
        return tuple(entry.path for entry in self.entries)

    def to_dict(self) -> list[dict[str, Any]]:
        """A JSON-serialisable projection."""
        return [entry.to_dict() for entry in self.entries]


@dataclass(frozen=True, slots=True)
class CapabilityDeclaration:
    """One declared Foundation capability — the complete data a probe needs to measure it.

    Every field is a *declaration*, so registering a capability is an entry in the register
    document and never a change to this module (UFC-09).
    """

    capability_id: str
    name: str
    domain: ConstitutionalDomain
    package: str
    identity: SymbolRef
    contracts: SymbolRef
    version: SymbolRef
    service_name: str
    service_descriptor: SymbolRef
    service_register: SymbolRef
    bootstrap: SymbolRef
    build: SymbolRef
    errors_module: str
    errors_base: SymbolRef
    replay: ReplayDeclaration = ReplayDeclaration()
    nucleus: NucleusProfile = NucleusProfile()
    extension_points: tuple[ExtensionPointDeclaration, ...] = ()
    registries: tuple[RegistryDeclaration, ...] = ()
    entry_point: str = ""
    cli: SymbolRef | None = None
    catalogs: tuple[str, ...] = ()
    policy_free: bool = False
    dependencies: tuple[str, ...] = ()
    description: str = ""

    @classmethod
    def from_document(cls, payload: Mapping[str, Any]) -> CapabilityDeclaration:
        """Build a validated declaration from the register document (fail-closed)."""
        if not isinstance(payload, Mapping):
            raise FoundationConformanceError("capability declaration must be a mapping")
        required = (
            "capability_id",
            "name",
            "domain",
            "package",
            "identity",
            "contracts",
            "version",
            "service_name",
            "service_descriptor",
            "service_register",
            "bootstrap",
            "build",
            "errors_module",
            "errors_base",
            "replay",
        )
        missing = [key for key in required if key not in payload]
        if missing:
            raise FoundationConformanceError(
                "capability declaration is incomplete",
                capability_id=str(payload.get("capability_id", "")),
                missing=",".join(missing),
            )
        capability_id = str(payload["capability_id"]).strip()
        if not capability_id:
            raise FoundationConformanceError("capability_id must be non-empty")
        catalogs = tuple(str(item) for item in payload.get("catalogs", ()))
        policy_free = bool(payload.get("policy_free", False))
        if not catalogs and not policy_free:
            raise FoundationConformanceError(
                "capability declares no catalogue and is not declared policy_free",
                capability_id=capability_id,
            )
        cli_value = payload.get("cli")
        return cls(
            capability_id=capability_id,
            name=str(payload["name"]),
            domain=ConstitutionalDomain.coerce(
                payload["domain"], context=f"capability {capability_id}"
            ),
            package=str(payload["package"]),
            identity=SymbolRef.parse(payload["identity"], context=capability_id),
            contracts=SymbolRef.parse(payload["contracts"], context=capability_id),
            version=SymbolRef.parse(payload["version"], context=capability_id),
            service_name=str(payload["service_name"]),
            service_descriptor=SymbolRef.parse(
                payload["service_descriptor"], context=capability_id
            ),
            service_register=SymbolRef.parse(payload["service_register"], context=capability_id),
            bootstrap=SymbolRef.parse(payload["bootstrap"], context=capability_id),
            build=SymbolRef.parse(payload["build"], context=capability_id),
            errors_module=str(payload["errors_module"]),
            errors_base=SymbolRef.parse(payload["errors_base"], context=capability_id),
            replay=ReplayDeclaration.from_document(payload["replay"], capability_id=capability_id),
            nucleus=NucleusProfile.from_document(
                payload.get("nucleus"), capability_id=capability_id
            ),
            extension_points=tuple(
                ExtensionPointDeclaration.from_document(item)
                for item in payload.get("extension_points", ())
            ),
            registries=tuple(
                RegistryDeclaration.from_document(item) for item in payload.get("registries", ())
            ),
            entry_point=str(payload.get("entry_point", "")),
            cli=SymbolRef.parse(cli_value, context=capability_id) if cli_value else None,
            catalogs=catalogs,
            policy_free=policy_free,
            dependencies=tuple(sorted(str(item) for item in payload.get("dependencies", ()))),
            description=str(payload.get("description", "")),
        )

    def package_path(self, *, root: Path | str = ".") -> Path:
        """The filesystem directory of this capability's package."""
        try:
            module = importlib.import_module(self.package)
        except Exception as exc:  # noqa: BLE001 - contained by design (fail-closed)
            raise FoundationConformanceError(
                "capability package could not be imported",
                capability_id=self.capability_id,
                package=self.package,
                detail=str(exc),
            ) from exc
        location = getattr(module, "__file__", None)
        if not location:
            raise FoundationConformanceError(
                "capability package has no filesystem location",
                capability_id=self.capability_id,
                package=self.package,
            )
        del root  # the package location is authoritative; no repository path is assumed
        return Path(location).resolve().parent

    def source_files(self) -> tuple[Path, ...]:
        """Every Python source file of this capability's package, deterministically ordered."""
        base = self.package_path()
        return tuple(
            sorted(
                path
                for path in base.rglob("*.py")
                if not any(part in _SOURCE_EXCLUDED for part in path.parts)
            )
        )

    def to_dict(self) -> dict[str, Any]:
        """A JSON-serialisable projection of this declaration."""
        return {
            "capability_id": self.capability_id,
            "name": self.name,
            "domain": self.domain.value,
            "package": self.package,
            "identity": str(self.identity),
            "contracts": str(self.contracts),
            "version": str(self.version),
            "service_name": self.service_name,
            "service_descriptor": str(self.service_descriptor),
            "service_register": str(self.service_register),
            "bootstrap": str(self.bootstrap),
            "build": str(self.build),
            "errors_module": self.errors_module,
            "errors_base": str(self.errors_base),
            "replay": self.replay.to_dict(),
            "nucleus": self.nucleus.to_dict(),
            "extension_points": [item.to_dict() for item in self.extension_points],
            "registries": [item.to_dict() for item in self.registries],
            "entry_point": self.entry_point,
            "cli": str(self.cli) if self.cli else "",
            "catalogs": list(self.catalogs),
            "policy_free": self.policy_free,
            "dependencies": list(self.dependencies),
            "description": self.description,
        }

    def fingerprint(self) -> str:
        """The deterministic content fingerprint of this declaration."""
        return content_hash(self.to_dict())


@dataclass(frozen=True, slots=True)
class GateResult:
    """The measured outcome of one gate against one subject, with its evidence."""

    gate: str
    article_id: str
    subject: str
    verdict: Verdict
    summary: str = ""
    findings: tuple[str, ...] = ()
    result_id: str = ""

    @classmethod
    def create(
        cls,
        gate: str,
        article_id: str,
        subject: str,
        verdict: Verdict,
        *,
        summary: str = "",
        findings: Iterable[str] = (),
    ) -> GateResult:
        """Build a content-addressed gate result."""
        found = tuple(sorted({str(item) for item in findings}))
        core = {
            "gate": gate,
            "article_id": article_id,
            "subject": subject,
            "verdict": verdict.value,
            "findings": list(found),
        }
        return cls(
            gate=gate,
            article_id=article_id,
            subject=subject,
            verdict=verdict,
            summary=summary,
            findings=found,
            result_id=f"UCOS-UFCG-{content_hash(core)[:16]}",
        )

    @property
    def satisfied(self) -> bool:
        """Whether this result discharges its article."""
        return self.verdict.satisfied

    def to_dict(self) -> dict[str, Any]:
        """A JSON-serialisable projection of this result."""
        return {
            "result_id": self.result_id,
            "gate": self.gate,
            "article_id": self.article_id,
            "subject": self.subject,
            "verdict": self.verdict.value,
            "summary": self.summary,
            "findings": list(self.findings),
        }


@dataclass(frozen=True, slots=True)
class CapabilityConformance:
    """Every gate result for one capability, plus its measured maturity."""

    capability_id: str
    name: str
    domain: ConstitutionalDomain
    results: tuple[GateResult, ...]
    conformance_id: str = ""

    @classmethod
    def create(
        cls,
        declaration: CapabilityDeclaration,
        results: Iterable[GateResult],
    ) -> CapabilityConformance:
        """Build a content-addressed conformance record."""
        ordered = tuple(sorted(results, key=lambda item: item.gate))
        core = {
            "capability_id": declaration.capability_id,
            "results": [item.result_id for item in ordered],
        }
        return cls(
            capability_id=declaration.capability_id,
            name=declaration.name,
            domain=declaration.domain,
            results=ordered,
            conformance_id=f"UCOS-UFCC-{content_hash(core)[:16]}",
        )

    @property
    def conformant(self) -> bool:
        """Whether every measured gate passed."""
        return all(item.satisfied for item in self.results)

    def by_gate(self) -> dict[str, GateResult]:
        """Gate identity → result."""
        return {item.gate: item for item in self.results}

    def failures(self) -> tuple[GateResult, ...]:
        """Every result that did not pass, in gate order."""
        return tuple(item for item in self.results if not item.satisfied)

    def maturity(self) -> dict[str, bool]:
        """Whether each declared maturity axis is reached, measured from gate results.

        An axis proven by a gate this capability was not measured against is **not**
        reached: an unmeasured axis is an absence, never a pass.
        """
        index = self.by_gate()
        reached: dict[str, bool] = {}
        for axis, gates in MATURITY_GATES.items():
            reached[axis.value] = all(gate in index and index[gate].satisfied for gate in gates)
        return reached

    @property
    def maturity_percentage(self) -> float:
        """The share of declared maturity axes this capability reached."""
        reached = self.maturity()
        if not reached:  # pragma: no cover - MATURITY_GATES is a non-empty literal
            # maturity() emits exactly one key per MATURITY_GATES entry, and that name is a
            # module-level dict literal every production reference only ever reads. No
            # assignment, rebinding or removal exists, so len(reached) is the declared axis
            # count and this division can never be by zero. The guard stays because the axis
            # population is declared data: were it ever emptied, 0% is the honest reading.
            return 0.0
        return round(sum(1 for value in reached.values() if value) / len(reached) * 100, 4)

    def to_dict(self) -> dict[str, Any]:
        """A JSON-serialisable projection of this record."""
        return {
            "conformance_id": self.conformance_id,
            "capability_id": self.capability_id,
            "name": self.name,
            "domain": self.domain.value,
            "conformant": self.conformant,
            "maturity": self.maturity(),
            "maturity_percentage": self.maturity_percentage,
            "results": [item.to_dict() for item in self.results],
        }


@dataclass(frozen=True, slots=True)
class ConformanceDetermination:
    """The immutable determination of the whole platform against the whole Constitution."""

    constitution_id: str
    constitution_fingerprint: str
    capabilities: tuple[CapabilityConformance, ...]
    platform_results: tuple[GateResult, ...] = ()
    determination_id: str = ""

    @classmethod
    def create(
        cls,
        constitution: FoundationConstitution,
        capabilities: Iterable[CapabilityConformance],
        platform_results: Iterable[GateResult] = (),
    ) -> ConformanceDetermination:
        """Build a content-addressed determination."""
        ordered = tuple(sorted(capabilities, key=lambda item: item.capability_id))
        platform = tuple(sorted(platform_results, key=lambda item: item.gate))
        core = {
            "constitution": constitution.fingerprint(),
            "capabilities": [item.conformance_id for item in ordered],
            "platform": [item.result_id for item in platform],
        }
        return cls(
            constitution_id=constitution.constitution_id,
            constitution_fingerprint=constitution.fingerprint(),
            capabilities=ordered,
            platform_results=platform,
            determination_id=f"UCOS-UFCD-{content_hash(core)[:16]}",
        )

    @property
    def total(self) -> int:
        """How many capabilities were measured."""
        return len(self.capabilities)

    @property
    def conformant(self) -> bool:
        """Whether every capability and every platform gate passed."""
        return all(item.conformant for item in self.capabilities) and all(
            item.satisfied for item in self.platform_results
        )

    def failures(self) -> tuple[GateResult, ...]:
        """Every non-passing result across capabilities and the platform."""
        found: list[GateResult] = []
        for capability in self.capabilities:
            found.extend(capability.failures())
        found.extend(item for item in self.platform_results if not item.satisfied)
        return tuple(sorted(found, key=lambda item: (item.subject, item.gate)))

    def blockers(self) -> tuple[str, ...]:
        """``subject/gate`` identities of every non-passing result."""
        return tuple(f"{item.subject}/{item.gate}" for item in self.failures())

    @property
    def maturity_percentage(self) -> float:
        """Platform maturity: the mean measured maturity across capabilities.

        Platform-scoped articles participate as a capability-equivalent term, so an
        unconverged platform can never report full maturity however mature its parts are.
        """
        if not self.capabilities:
            return 0.0
        terms = [item.maturity_percentage for item in self.capabilities]
        if self.platform_results:
            passed = sum(1 for item in self.platform_results if item.satisfied)
            terms.append(round(passed / len(self.platform_results) * 100, 4))
        return round(sum(terms) / len(terms), 4)

    def maturity_by_axis(self) -> dict[str, float]:
        """For each declared axis, the share of capabilities that reached it."""
        if not self.capabilities:
            return {axis.value: 0.0 for axis in MaturityAxis}
        tally: dict[str, int] = {axis.value: 0 for axis in MaturityAxis}
        for capability in self.capabilities:
            for axis, reached in capability.maturity().items():
                if reached:
                    tally[axis] += 1
        return {
            axis: round(count / len(self.capabilities) * 100, 4) for axis, count in tally.items()
        }

    def counts(self) -> dict[str, int]:
        """Headline counts over every measured result."""
        results = [item for capability in self.capabilities for item in capability.results]
        results.extend(self.platform_results)
        return {
            "capabilities": self.total,
            "results": len(results),
            "passed": sum(1 for item in results if item.verdict is Verdict.PASS),
            "failed": sum(1 for item in results if item.verdict is Verdict.FAIL),
            "faulted": sum(1 for item in results if item.verdict is Verdict.FAULT),
        }

    def to_dict(self) -> dict[str, Any]:
        """A JSON-serialisable projection of this determination."""
        return {
            "determination_id": self.determination_id,
            "constitution_id": self.constitution_id,
            "constitution_fingerprint": self.constitution_fingerprint,
            "conformant": self.conformant,
            "counts": self.counts(),
            "maturity_percentage": self.maturity_percentage,
            "maturity_by_axis": self.maturity_by_axis(),
            "blockers": list(self.blockers()),
            "capabilities": [item.to_dict() for item in self.capabilities],
            "platform_results": [item.to_dict() for item in self.platform_results],
        }

    def summary(self) -> dict[str, Any]:
        """A compact projection without the per-result detail."""
        return {
            "determination_id": self.determination_id,
            "constitution_id": self.constitution_id,
            "conformant": self.conformant,
            "counts": self.counts(),
            "maturity_percentage": self.maturity_percentage,
            "maturity_by_axis": self.maturity_by_axis(),
            "blockers": list(self.blockers()),
            "capabilities": [
                {
                    "capability_id": item.capability_id,
                    "domain": item.domain.value,
                    "conformant": item.conformant,
                    "maturity_percentage": item.maturity_percentage,
                }
                for item in self.capabilities
            ],
        }

    def fingerprint(self) -> str:
        """The deterministic content fingerprint of this determination."""
        return content_hash(self.to_dict())


class CapabilityRegister:
    """A deterministic, fail-closed registry of declared Foundation capabilities."""

    __slots__ = ("_declarations", "_register_id", "_locator_pattern", "_governing_modules")

    def __init__(
        self,
        declarations: Iterable[CapabilityDeclaration] = (),
        *,
        register_id: str = "foundation.capabilities",
        locator_pattern: str = "",
        governing_modules: Iterable[str] = (),
    ) -> None:
        self._declarations: dict[str, CapabilityDeclaration] = {}
        self._register_id = register_id.strip() or "foundation.capabilities"
        self._locator_pattern = locator_pattern
        self._governing_modules = tuple(sorted(str(item) for item in governing_modules))
        for declaration in declarations:
            self.add(declaration)

    @property
    def register_id(self) -> str:
        """The declared identity of this register."""
        return self._register_id

    @property
    def locator_pattern(self) -> str:
        """The declared regex whose match in module source is a repository locator (UFC-13)."""
        return self._locator_pattern

    @property
    def governing_modules(self) -> tuple[str, ...]:
        """The modules that govern the platform and therefore may name no capability (UFC-09)."""
        return self._governing_modules

    @property
    def count(self) -> int:
        """How many capabilities are declared."""
        return len(self._declarations)

    def add(self, declaration: CapabilityDeclaration) -> CapabilityDeclaration:
        """Declare ``declaration``; fail-closed on an identity collision."""
        if not isinstance(declaration, CapabilityDeclaration):
            raise FoundationConformanceError("register accepts only CapabilityDeclaration values")
        existing = self._declarations.get(declaration.capability_id)
        if existing is not None:
            if existing.fingerprint() == declaration.fingerprint():
                return existing
            raise FoundationConformanceError(
                "capability already declared with a different body",
                capability_id=declaration.capability_id,
            )
        self._declarations[declaration.capability_id] = declaration
        return declaration

    def get(self, capability_id: str) -> CapabilityDeclaration | None:
        """The declared capability ``capability_id``, or ``None``."""
        return self._declarations.get(capability_id)

    def require(self, capability_id: str) -> CapabilityDeclaration:
        """The declared capability ``capability_id`` (fail-closed)."""
        declaration = self.get(capability_id)
        if declaration is None:
            raise FoundationConformanceError(
                "unknown Foundation capability", capability_id=str(capability_id)
            )
        return declaration

    def ordered(self) -> tuple[CapabilityDeclaration, ...]:
        """Every declaration in deterministic identity order."""
        return tuple(sorted(self._declarations.values(), key=lambda item: item.capability_id))

    def ids(self) -> tuple[str, ...]:
        """Every declared capability identity, in order."""
        return tuple(item.capability_id for item in self.ordered())

    def of_domain(self, domain: ConstitutionalDomain | str) -> tuple[CapabilityDeclaration, ...]:
        """Every declaration whose primary governed domain is ``domain``."""
        resolved = ConstitutionalDomain.coerce(domain)
        return tuple(item for item in self.ordered() if item.domain is resolved)

    def dependency_order(self) -> tuple[str, ...]:
        """A total, deterministic dependency-honest order (fail-closed on a cycle)."""
        pending = {item.capability_id: set(item.dependencies) for item in self.ordered()}
        unknown = {
            f"{name}->{dep}" for name, deps in pending.items() for dep in deps if dep not in pending
        }
        if unknown:
            raise FoundationConformanceError(
                "capability declares an unregistered dependency", missing=",".join(sorted(unknown))
            )
        order: list[str] = []
        while pending:
            ready = sorted(name for name, deps in pending.items() if not deps - set(order))
            if not ready:
                raise FoundationConformanceError(
                    "capability dependency graph contains a cycle",
                    remaining=",".join(sorted(pending)),
                )
            order.extend(ready)
            for name in ready:
                del pending[name]
        return tuple(order)

    @classmethod
    def from_document(cls, document: Mapping[str, Any]) -> CapabilityRegister:
        """Build a register from the declared register document (fail-closed)."""
        if not isinstance(document, Mapping):
            raise FoundationConformanceError("capability register document must be a mapping")
        capabilities = document.get("capabilities")
        if not isinstance(capabilities, Sequence) or isinstance(capabilities, str | bytes):
            raise FoundationConformanceError(
                "capability register requires a 'capabilities' sequence"
            )
        register = cls(
            register_id=str(document.get("register_id", "")),
            locator_pattern=str(document.get("locator_literal_pattern", "")),
            governing_modules=document.get("governing_modules", ()),
        )
        for declaration in capabilities:
            register.add(CapabilityDeclaration.from_document(declaration))
        if register.count == 0:
            raise FoundationConformanceError("capability register declares no capability")
        register.dependency_order()
        return register

    def to_dict(self) -> dict[str, Any]:
        """A JSON-serialisable projection of this register."""
        return {
            "register_id": self._register_id,
            "capability_count": self.count,
            "locator_literal_pattern": self._locator_pattern,
            "governing_modules": list(self._governing_modules),
            "dependency_order": list(self.dependency_order()),
            "capabilities": [item.to_dict() for item in self.ordered()],
        }

    def fingerprint(self) -> str:
        """The deterministic content fingerprint of this register."""
        return content_hash(self.to_dict())


def catalog_path(filename: str = DEFAULT_REGISTER_FILENAME) -> Path:
    """The packaged catalogue path for ``filename``."""
    return Path(__file__).resolve().parent / CATALOG_DIRNAME / filename


def load_capability_register(path: Path | str) -> CapabilityRegister:
    """Load a declared capability register from ``path`` (fail-closed)."""
    target = Path(path)
    try:
        document = json.loads(target.read_text("utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise FoundationConformanceError(
            "capability register could not be read", path=str(target), detail=str(exc)
        ) from exc
    return CapabilityRegister.from_document(document)


def default_capability_register(
    filename: str = DEFAULT_REGISTER_FILENAME,
) -> CapabilityRegister:
    """The capability register shipped in the packaged catalogue."""
    return load_capability_register(catalog_path(filename))


def _called_names(tree: ast.Module) -> tuple[str, ...]:
    """Every callable name invoked at *any* depth — the write half of UFC-11.

    :func:`_module_level_calls` deliberately stops at the first function or class because
    UFC-07 asks a question about import time. UFC-11 asks a question about the whole
    capability, so this walk does not stop.
    """
    found: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Name):
            found.add(func.id)
        elif isinstance(func, ast.Attribute):
            found.add(func.attr)
    return tuple(sorted(found))


def _module_level_calls(tree: ast.Module) -> tuple[str, ...]:
    """Every callable name invoked at module level (never inside a function or class)."""
    found: list[str] = []
    for statement in tree.body:
        if isinstance(statement, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
            continue
        for node in ast.walk(statement):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            if isinstance(func, ast.Name):
                found.append(func.id)
            elif isinstance(func, ast.Attribute):
                found.append(func.attr)
    return tuple(sorted(set(found)))


def _imported_modules(tree: ast.Module) -> frozenset[str]:
    """Every module name this source imports, at any depth."""
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module)
    return frozenset(names)


def _string_literals(tree: ast.Module) -> tuple[str, ...]:
    """Every string constant in this source, deterministically ordered."""
    return tuple(
        sorted(
            {
                node.value
                for node in ast.walk(tree)
                if isinstance(node, ast.Constant) and isinstance(node.value, str)
            }
        )
    )


def _parse(path: Path) -> ast.Module:
    """Parse ``path`` as Python source (fail-closed)."""
    try:
        return ast.parse(path.read_text("utf-8"), filename=str(path))
    except (OSError, SyntaxError, ValueError) as exc:
        raise FoundationConformanceError(
            "capability source could not be parsed", path=str(path), detail=str(exc)
        ) from exc


#: What a probe returns: a verdict, a human summary, and the findings that decided it.
ProbeOutcome = tuple[Verdict, str, tuple[str, ...]]

# Public aliases over the source-inspection primitives. Convergence measurement verifies
# delegation the same way conformance verifies composition — by reading the real import graph
# — so the primitive is shared rather than reimplemented (Reuse Before Create).
parse_source = _parse
imported_modules = _imported_modules
string_literals = _string_literals
module_level_calls = _module_level_calls
called_names = _called_names


class ConformanceProbe(ABC):
    """The extension point for every constitutional probe, present or future (UFC-03).

    A probe binds one declared gate to one executable measurement. Adding a gate — for a new
    article, or a stricter measurement of an existing one — is a registered probe, never a
    change to :class:`ConformanceEngine`.
    """

    @abstractmethod
    def gate(self) -> str:
        """The constitutional gate identity this probe proves."""
        raise NotImplementedError  # pragma: no cover - abstract

    @abstractmethod
    def measure(self, declaration: CapabilityDeclaration, context: ProbeContext) -> ProbeOutcome:
        """Measure ``declaration`` and report a verdict with its findings."""
        raise NotImplementedError  # pragma: no cover - abstract

    def apply(self, declaration: CapabilityDeclaration, context: ProbeContext) -> ProbeOutcome:
        """Protocol enforcement: verify the outcome's shape, contain nothing silently."""
        outcome = self.measure(declaration, context)
        if (
            not isinstance(outcome, tuple)
            or len(outcome) != 3
            or not isinstance(outcome[0], Verdict)
        ):
            raise FoundationConformanceError("probe produced a malformed outcome", gate=self.gate())
        return outcome[0], str(outcome[1]), tuple(str(item) for item in outcome[2])


class CallableProbe(ConformanceProbe):
    """Wraps any callable as a probe — the seam for a project's own constitutional gate."""

    __slots__ = ("_gate", "_callable")

    def __init__(
        self, gate: str, measure: Callable[[CapabilityDeclaration, ProbeContext], ProbeOutcome]
    ) -> None:
        if not isinstance(gate, str) or not gate.strip():
            raise FoundationConformanceError("a probe must declare its gate")
        if not callable(measure):
            raise FoundationConformanceError("callable probe requires a callable", gate=gate)
        self._gate = gate.strip()
        self._callable = measure

    def gate(self) -> str:
        """The gate this probe proves."""
        return self._gate

    def measure(self, declaration: CapabilityDeclaration, context: ProbeContext) -> ProbeOutcome:
        """Delegate to the wrapped callable."""
        return self._callable(declaration, context)


class ProbeRegistry:
    """A deterministic, fail-closed registry of constitutional probes."""

    __slots__ = ("_probes",)

    def __init__(self, probes: Iterable[ConformanceProbe] = ()) -> None:
        self._probes: dict[str, ConformanceProbe] = {}
        for probe in probes:
            self.add(probe)

    def add(self, probe: ConformanceProbe) -> ConformanceProbe:
        """Register ``probe``; idempotent by object, fail-closed on gate collision."""
        if not isinstance(probe, ConformanceProbe):
            raise FoundationConformanceError("registry accepts only ConformanceProbe values")
        gate = probe.gate()
        existing = self._probes.get(gate)
        if existing is not None:
            if existing is probe:
                return existing
            raise FoundationConformanceError("gate already has a bound probe", gate=gate)
        self._probes[gate] = probe
        return probe

    def extend(self, probes: Iterable[ConformanceProbe]) -> tuple[ConformanceProbe, ...]:
        """Register every probe in ``probes``, returning them in gate order."""
        for probe in probes:
            self.add(probe)
        return self.ordered()

    def get(self, gate: str) -> ConformanceProbe | None:
        """The probe bound to ``gate``, or ``None``."""
        return self._probes.get(gate)

    def require(self, gate: str) -> ConformanceProbe:
        """The probe bound to ``gate`` (fail-closed)."""
        probe = self.get(gate)
        if probe is None:
            raise FoundationConformanceError("no probe is bound to this gate", gate=str(gate))
        return probe

    @property
    def count(self) -> int:
        """How many probes are registered."""
        return len(self._probes)

    def ordered(self) -> tuple[ConformanceProbe, ...]:
        """Every probe in deterministic gate order — never insertion order."""
        return tuple(self._probes[gate] for gate in self.gates())

    def gates(self) -> tuple[str, ...]:
        """Every bound gate identity, in deterministic order."""
        return tuple(sorted(self._probes))

    def to_dict(self) -> dict[str, Any]:
        """A JSON-serialisable projection of this registry."""
        return {"probe_count": self.count, "gates": list(self.gates())}

    def fingerprint(self) -> str:
        """The deterministic content fingerprint of this registry."""
        return content_hash(self.to_dict())


@dataclass(frozen=True, slots=True)
class ProbeContext:
    """Everything a probe may read, supplied explicitly so no probe reaches ambient state."""

    register: CapabilityRegister
    console_scripts: Mapping[str, str]

    def dependency_package(self, capability_id: str) -> str:
        """The declared package of a dependency capability (fail-closed)."""
        return self.register.require(capability_id).package


class ConformanceEngine:
    """Executes the Constitution against a declared capability register.

    Probes are supplied by a :class:`ProbeRegistry`, so an article whose gate has no bound
    probe is reported as a FAULT rather than silently skipped, and a project may bind a
    stricter probe without editing this class (UFC-03).
    """

    __slots__ = ("_constitution", "_register", "_project_root", "_probes")

    def __init__(
        self,
        register: CapabilityRegister,
        *,
        constitution: FoundationConstitution | None = None,
        project_root: Path | str = ".",
        probes: ProbeRegistry | None = None,
    ) -> None:
        if not isinstance(register, CapabilityRegister):
            raise FoundationConformanceError("conformance requires a CapabilityRegister")
        self._register = register
        self._constitution = constitution or foundation_constitution()
        self._project_root = Path(project_root)
        self._probes = probes if probes is not None else default_probe_registry()

    @property
    def constitution(self) -> FoundationConstitution:
        """The law this engine executes."""
        return self._constitution

    @property
    def register(self) -> CapabilityRegister:
        """The declared capability population this engine measures."""
        return self._register

    @property
    def probes(self) -> ProbeRegistry:
        """The registered probes that prove the articles."""
        return self._probes

    # ------------------------------------------------------------- execution

    def _console_scripts(self) -> dict[str, str]:
        """The declared console entry points of the build (read once, deterministically)."""
        manifest = self._project_root / "pyproject.toml"
        try:
            raw = manifest.read_bytes()
        except OSError as exc:
            raise FoundationConformanceError(
                "build manifest could not be read", path=str(manifest), detail=str(exc)
            ) from exc
        try:
            document = tomllib.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, tomllib.TOMLDecodeError) as exc:
            raise FoundationConformanceError(
                "build manifest is not valid TOML", path=str(manifest), detail=str(exc)
            ) from exc
        project = document.get("project", {})
        scripts = project.get("scripts", {}) if isinstance(project, Mapping) else {}
        if not isinstance(scripts, Mapping) or not scripts:
            raise FoundationConformanceError(
                "build manifest declares no console scripts table", path=str(manifest)
            )
        return {str(key): str(value) for key, value in scripts.items()}

    def context(self) -> ProbeContext:
        """The read-only context every probe is given. Nothing else is reachable."""
        return ProbeContext(register=self._register, console_scripts=self._console_scripts())

    def measure_gate(
        self,
        declaration: CapabilityDeclaration,
        article: FoundationArticle,
        context: ProbeContext | None = None,
    ) -> GateResult:
        """Execute one article's probe against one capability, containing every fault."""
        try:
            probe = self._probes.require(article.gate)
            verdict, summary, findings = probe.apply(
                declaration, context if context is not None else self.context()
            )
        except FoundationConformanceError as exc:
            return GateResult.create(
                article.gate,
                article.article_id,
                declaration.capability_id,
                Verdict.FAULT,
                summary="probe could not execute",
                findings=(str(exc),),
            )
        except Exception as exc:  # noqa: BLE001 - contained by design (fail-closed)
            return GateResult.create(
                article.gate,
                article.article_id,
                declaration.capability_id,
                Verdict.FAULT,
                summary="probe raised an uncontained fault",
                findings=(f"{type(exc).__name__}: {exc}",),
            )
        return GateResult.create(
            article.gate,
            article.article_id,
            declaration.capability_id,
            verdict,
            summary=summary,
            findings=findings,
        )

    def measure_capability(
        self, declaration: CapabilityDeclaration, context: ProbeContext | None = None
    ) -> CapabilityConformance:
        """Execute every capability-scoped article against one capability."""
        resolved = context if context is not None else self.context()
        return CapabilityConformance.create(
            declaration,
            (
                self.measure_gate(declaration, article, resolved)
                for article in self._constitution.capability_articles()
            ),
        )

    def measure(self, *, platform_results: Iterable[GateResult] = ()) -> ConformanceDetermination:
        """Execute the whole Constitution over the whole declared population."""
        context = self.context()
        return ConformanceDetermination.create(
            self._constitution,
            (
                self.measure_capability(declaration, context)
                for declaration in self._register.ordered()
            ),
            platform_results,
        )

    def unbound_gates(self) -> tuple[str, ...]:
        """Capability-scoped gates the Constitution declares but no probe proves."""
        bound = set(self._probes.gates())
        return tuple(
            article.gate
            for article in self._constitution.capability_articles()
            if article.gate not in bound
        )

    def to_dict(self) -> dict[str, Any]:
        """A JSON-serialisable projection of this engine's composition."""
        return {
            "constitution": self._constitution.to_dict(),
            "register": self._register.to_dict(),
            "probes": self._probes.to_dict(),
            "unbound_gates": list(self.unbound_gates()),
        }

    def fingerprint(self) -> str:
        """The deterministic content fingerprint of this engine's composition."""
        return content_hash(self.to_dict())


# --------------------------------------------------------------------------- probes
# One probe per constitutional gate. Each is a module-level function so it can be bound,
# rebound or superseded by declaration; none of them reaches ambient state — everything a
# probe may read arrives in its ``ProbeContext``.


def probe_contract_published(
    declaration: CapabilityDeclaration, context: ProbeContext
) -> ProbeOutcome:
    """UFC-01 — the capability publishes a named, semantically versioned contract surface."""
    del context
    contracts = declaration.contracts.resolve()
    version = declaration.version.resolve()
    findings: list[str] = []
    if not isinstance(contracts, tuple) or not contracts:
        findings.append(f"{declaration.contracts} is not a non-empty tuple of contracts")
    else:
        findings.extend(
            f"published contract is not a ContractRef: {ref!r}"
            for ref in contracts
            if not isinstance(ref, ContractRef)
        )
    if not isinstance(version, str) or not _SEMVER.match(version):
        findings.append(f"{declaration.version} is not a semantic version: {version!r}")
    if findings:
        return Verdict.FAIL, "contract surface is not published", tuple(findings)
    return Verdict.PASS, f"{len(contracts)} contracts published at version {version}", ()


def probe_service_registered(
    declaration: CapabilityDeclaration, context: ProbeContext
) -> ProbeOutcome:
    """UFC-02 — the capability registers, validates and resolves as a service."""
    del context
    descriptor = declaration.service_descriptor.resolve()()
    if not isinstance(descriptor, ServiceDescriptor):
        return (
            Verdict.FAIL,
            "declared service descriptor is not a ServiceDescriptor",
            (str(declaration.service_descriptor),),
        )
    if descriptor.name != declaration.service_name:
        return (
            Verdict.FAIL,
            "declared service name does not match the published descriptor",
            (f"declared={declaration.service_name} published={descriptor.name}",),
        )
    registry = ServiceRegistry()
    declaration.service_register.resolve()(registry)
    if declaration.service_name not in registry:
        return (
            Verdict.FAIL,
            "registration did not publish the declared service",
            (declaration.service_name,),
        )
    registry.validate()
    if registry.resolve(declaration.service_name) is None:
        return Verdict.FAIL, "declared service resolved to nothing", (declaration.service_name,)
    return (
        Verdict.PASS,
        f"service '{declaration.service_name}' registered, validated and resolved "
        f"({len(registry)} services published)",
        (),
    )


def probe_provider_pluggable(
    declaration: CapabilityDeclaration, context: ProbeContext
) -> ProbeOutcome:
    """UFC-03 — new authority is admitted through a declared extension point."""
    del context
    if not declaration.extension_points:
        return Verdict.FAIL, "capability declares no extension point", (declaration.capability_id,)
    findings: list[str] = []
    for point in declaration.extension_points:
        target = point.symbol.resolve()
        if not isinstance(target, type):
            findings.append(f"{point.symbol} is not a class")
            continue
        if point.abstract and not getattr(target, "__abstractmethods__", frozenset()):
            findings.append(f"{point.symbol} declares no abstract method")
        findings.extend(
            f"{point.symbol} does not expose {method}()"
            for method in point.methods
            if not callable(getattr(target, method, None))
        )
    if findings:
        return Verdict.FAIL, "extension point is not pluggable", tuple(findings)
    return (
        Verdict.PASS,
        f"{len(declaration.extension_points)} extension points admit new authority",
        (),
    )


def probe_policy_declared(
    declaration: CapabilityDeclaration, context: ProbeContext
) -> ProbeOutcome:
    """UFC-04 — every determination is configured by a declared, parseable policy document."""
    del context
    if declaration.policy_free:
        return (
            Verdict.PASS,
            "declared policy-free: the capability holds no project-specific policy",
            (),
        )
    base = declaration.package_path()
    findings: list[str] = []
    for relative in declaration.catalogs:
        document = base / relative
        if not document.is_file():
            findings.append(f"declared catalogue is absent: {relative}")
            continue
        try:
            payload = json.loads(document.read_text("utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            findings.append(f"declared catalogue is unreadable: {relative} ({exc})")
            continue
        if not isinstance(payload, Mapping) or not payload:
            findings.append(f"declared catalogue is not a non-empty object: {relative}")
    if findings:
        return Verdict.FAIL, "declared policy is not resolvable", tuple(findings)
    return (
        Verdict.PASS,
        f"{len(declaration.catalogs)} declared policy documents resolve and parse",
        (),
    )


def probe_registry_deterministic(
    declaration: CapabilityDeclaration, context: ProbeContext
) -> ProbeOutcome:
    """UFC-05 — every population is held in a deterministic, fail-closed registry."""
    del context
    if not declaration.registries:
        return Verdict.FAIL, "capability declares no registry", (declaration.capability_id,)
    findings: list[str] = []
    for registry in declaration.registries:
        target = registry.symbol.resolve()
        if not isinstance(target, type):
            findings.append(f"{registry.symbol} is not a class")
            continue
        findings.extend(
            f"{registry.symbol} does not expose {method}()"
            for method in (registry.ordered, registry.require)
            if not callable(getattr(target, method, None))
        )
    if findings:
        return (
            Verdict.FAIL,
            "registry surface is not deterministic and fail-closed",
            tuple(findings),
        )
    return (
        Verdict.PASS,
        f"{len(declaration.registries)} registries order by declared precedence and refuse "
        "unknown members",
        (),
    )


def probe_runtime_invocable(
    declaration: CapabilityDeclaration, context: ProbeContext
) -> ProbeOutcome:
    """UFC-06 — the capability is invocable in one command through a declared entry point."""
    if declaration.cli is None or not declaration.entry_point:
        return (
            Verdict.FAIL,
            "capability declares no one-command runtime surface",
            (declaration.capability_id,),
        )
    findings: list[str] = []
    if not callable(declaration.cli.resolve()):
        findings.append(f"{declaration.cli} is not callable")
    declared = context.console_scripts
    target = str(declaration.cli)
    if declaration.entry_point not in declared:
        findings.append(f"entry point '{declaration.entry_point}' is not declared in the build")
    elif declared[declaration.entry_point] != target:
        findings.append(
            f"entry point '{declaration.entry_point}' resolves to "
            f"{declared[declaration.entry_point]}, not {target}"
        )
    if findings:
        return Verdict.FAIL, "runtime surface is not invocable", tuple(findings)
    return Verdict.PASS, f"invocable as '{declaration.entry_point}' -> {target}", ()


def probe_lifecycle_bootstrapped(
    declaration: CapabilityDeclaration, context: ProbeContext
) -> ProbeOutcome:
    """UFC-07 — the capability exists through a declared bootstrap and imports purely."""
    del context
    findings: list[str] = []
    if not callable(declaration.bootstrap.resolve()):
        findings.append(f"{declaration.bootstrap} is not callable")
    sources = declaration.source_files()
    for path in sources:
        impure = sorted(set(_module_level_calls(_parse(path))) & set(IMPORT_PURITY_FORBIDDEN))
        if impure:
            findings.append(f"{path.name} performs {','.join(impure)} at import time")
    if findings:
        return Verdict.FAIL, "capability is not bootstrap-only", tuple(findings)
    return Verdict.PASS, f"declared bootstrap resolves; {len(sources)} modules are import-pure", ()


def probe_compatibility_declared(
    declaration: CapabilityDeclaration, context: ProbeContext
) -> ProbeOutcome:
    """UFC-08 — one declared version governs the whole published surface."""
    del context
    version = declaration.version.resolve()
    contracts = declaration.contracts.resolve()
    findings: list[str] = []
    if not isinstance(version, str) or not _SEMVER.match(version):
        findings.append(f"declared version is not semantic: {version!r}")
    findings.extend(
        f"contract {ref.name} carries {ref.version}, declared {version}"
        for ref in (contracts if isinstance(contracts, tuple) else ())
        if isinstance(ref, ContractRef) and ref.version != version
    )
    descriptor = declaration.service_descriptor.resolve()()
    if isinstance(descriptor, ServiceDescriptor) and str(descriptor.contract.version) != version:
        findings.append(
            f"service contract carries {descriptor.contract.version}, declared {version}"
        )
    if findings:
        return Verdict.FAIL, "declared compatibility is inconsistent", tuple(findings)
    return Verdict.PASS, f"one contract version governs the whole surface: {version}", ()


def probe_evolution_additive(
    declaration: CapabilityDeclaration, context: ProbeContext
) -> ProbeOutcome:
    """UFC-09 — the identity is self-declared and no governing module enumerates it."""
    identity = declaration.identity.resolve()
    findings: list[str] = []
    if identity != declaration.capability_id:
        findings.append(
            f"{declaration.identity} is {identity!r}, not {declaration.capability_id!r}"
        )
    governing = context.register.governing_modules
    if not governing:
        raise FoundationConformanceError(
            "register declares no governing module; UFC-09 cannot be measured"
        )
    # A governing module may declare the identity of the capability it *is* — that is where a
    # self-declared identity lives. What UFC-09 forbids is a governing module naming a
    # capability it does not itself constitute, because that is the enumeration which makes
    # adding a capability require editing the governor.
    constituting = declaration.identity.module
    for module_name in governing:
        if module_name == constituting:
            continue
        try:
            module = importlib.import_module(module_name)
        except Exception as exc:  # noqa: BLE001 - contained by design (fail-closed)
            raise FoundationConformanceError(
                "declared governing module could not be imported",
                module=module_name,
                detail=str(exc),
            ) from exc
        location = getattr(module, "__file__", None)
        if not location:
            continue
        if declaration.capability_id in string_literals(parse_source(Path(location))):
            findings.append(f"governing module {module_name} enumerates this capability")
    if findings:
        return Verdict.FAIL, "capability identity is not evolution-additive", tuple(findings)
    return (
        Verdict.PASS,
        f"identity is self-declared and absent from every governing module it does not "
        f"constitute ({len(governing)} governing modules)",
        (),
    )


def probe_fail_closed(declaration: CapabilityDeclaration, context: ProbeContext) -> ProbeOutcome:
    """UFC-10 — the capability refuses through typed errors carrying distinct stable codes."""
    del context
    base = declaration.errors_base.resolve()
    if not isinstance(base, type) or not issubclass(base, PlatformError):
        return (
            Verdict.FAIL,
            "error taxonomy is not fail-closed",
            (f"{declaration.errors_base} is not a PlatformError subclass",),
        )
    module = importlib.import_module(declaration.errors_module)
    findings: list[str] = []
    codes: dict[str, str] = {}
    for name in sorted(dir(module)):
        candidate = getattr(module, name)
        if not (
            isinstance(candidate, type)
            and issubclass(candidate, PlatformError)
            and candidate.__module__ == declaration.errors_module
        ):
            continue
        code = getattr(candidate, "code", "")
        if not isinstance(code, str) or not code.strip():
            findings.append(f"{name} declares no stable error code")
            continue
        if code in codes:
            findings.append(f"{name} reuses the code of {codes[code]}: {code}")
        codes[code] = name
    if not codes:
        findings.append(f"{declaration.errors_module} declares no typed error")
    if findings:
        return Verdict.FAIL, "error taxonomy is not fail-closed", tuple(findings)
    return Verdict.PASS, f"{len(codes)} typed errors carry distinct stable codes", ()


def probe_certifiable(declaration: CapabilityDeclaration, context: ProbeContext) -> ProbeOutcome:
    """UFC-11 — two independent builds are content-addressed and byte-identical."""
    del context
    build = declaration.build.resolve()
    if not callable(build):
        return Verdict.FAIL, "declared build is not callable", (str(declaration.build),)
    first, second = build(), build()
    findings = [
        f"{label} build exposes no fingerprint()"
        for label, value in (("first", first), ("second", second))
        if not hasattr(value, "fingerprint")
    ]
    if findings:
        return Verdict.FAIL, "capability is not content-addressed", tuple(findings)
    left, right = first.fingerprint(), second.fingerprint()
    if not isinstance(left, str) or not left:
        return Verdict.FAIL, "fingerprint is empty", (str(declaration.build),)
    if left != right:
        return (
            Verdict.FAIL,
            "two independent builds produced different fingerprints",
            (f"{left} != {right}",),
        )

    # Register currency. A determination that becomes Repository Truth must be replayable at
    # the commit that carries it, so the declared replay posture is measured against the
    # capability's own source rather than taken on trust.
    observed: list[str] = []
    for path in declaration.source_files():
        called = set(_called_names(_parse(path)))
        observed.extend(
            f"{path.name} calls {name}()" for name in sorted(called & set(ARTIFACT_WRITE_CALLS))
        )
    declared = declaration.replay
    if observed and not declared.writes_tracked_artifacts:
        return (
            Verdict.FAIL,
            "capability emits artifacts but declares no replay obligation",
            tuple(observed),
        )
    if declared.writes_tracked_artifacts and not observed:
        return (
            Verdict.FAIL,
            "capability declares a replay obligation its source cannot discharge",
            (f"no call from {','.join(ARTIFACT_WRITE_CALLS)} appears in its source",),
        )
    if declared.writes_tracked_artifacts:
        if declared.target is None:  # pragma: no cover - construction refuses this pairing
            return Verdict.FAIL, "declared writer names no replay target", ()
        try:
            replay = declared.target.resolve()
        except FoundationConformanceError as exc:
            return Verdict.FAIL, "declared replay target does not resolve", (str(exc),)
        if not callable(replay):
            return Verdict.FAIL, "declared replay target is not callable", (str(declared.target),)
        return (
            Verdict.PASS,
            f"content-addressed, replay-identical ({left[:16]}) and re-measurable at its "
            f"own commit via {declared.target}",
            (),
        )
    return (
        Verdict.PASS,
        f"content-addressed and replay-identical: {left[:16]}; emits no tracked artifact, "
        "measured over its own source",
        (),
    )


def probe_composable(declaration: CapabilityDeclaration, context: ProbeContext) -> ProbeOutcome:
    """UFC-12 — declared dependencies resolve, are really imported, and the graph is acyclic."""
    known = set(context.register.ids())
    findings: list[str] = []
    imported: set[str] | None = None
    for dependency in declaration.dependencies:
        if dependency not in known:
            findings.append(f"declared dependency is not a Foundation capability: {dependency}")
            continue
        if imported is None:
            imported = set()
            for path in declaration.source_files():
                imported |= _imported_modules(_parse(path))
        package = context.dependency_package(dependency)
        if not any(name == package or name.startswith(f"{package}.") for name in imported):
            findings.append(f"declared dependency {dependency} is never imported: {package}")
    context.register.dependency_order()
    if findings:
        return Verdict.FAIL, "composition is not closed", tuple(findings)
    if not declaration.dependencies:
        return Verdict.PASS, "composes no dependency; available for composition by reference", ()
    return (
        Verdict.PASS,
        f"composes {len(declaration.dependencies)} capabilities by reference over an acyclic graph",
        (),
    )


def probe_specialized(declaration: CapabilityDeclaration, context: ProbeContext) -> ProbeOutcome:
    """UFC-13 — no module of the capability carries a repository locator literal."""
    pattern = context.register.locator_pattern
    if not pattern:
        raise FoundationConformanceError(
            "register declares no locator literal pattern; UFC-13 cannot be measured"
        )
    compiled = re.compile(pattern)
    findings: list[str] = []
    sources = declaration.source_files()
    for path in sources:
        findings.extend(
            f"{path.name} carries a repository locator: {literal}"
            for literal in _string_literals(_parse(path))
            if compiled.search(literal)
        )
    if findings:
        return Verdict.FAIL, "project literals are present in code", tuple(findings)
    return (
        Verdict.PASS,
        f"{len(sources)} modules carry no repository locator; specialisation is declared",
        (),
    )


#: The probes shipped with the Constitution — one per capability-scoped article. Binding a
#: stricter probe, or a probe for a newly legislated gate, is a registration (UFC-03).
ProbeBinding = tuple[str, Callable[[CapabilityDeclaration, ProbeContext], ProbeOutcome]]

SHIPPED_PROBES: tuple[ProbeBinding, ...] = (
    ("FG-01-CONTRACT-PUBLISHED", probe_contract_published),
    ("FG-02-SERVICE-REGISTERED", probe_service_registered),
    ("FG-03-PROVIDER-PLUGGABLE", probe_provider_pluggable),
    ("FG-04-POLICY-DECLARED", probe_policy_declared),
    ("FG-05-REGISTRY-DETERMINISTIC", probe_registry_deterministic),
    ("FG-06-RUNTIME-INVOCABLE", probe_runtime_invocable),
    ("FG-07-LIFECYCLE-BOOTSTRAPPED", probe_lifecycle_bootstrapped),
    ("FG-08-COMPATIBILITY-DECLARED", probe_compatibility_declared),
    ("FG-09-EVOLUTION-ADDITIVE", probe_evolution_additive),
    ("FG-10-FAIL-CLOSED", probe_fail_closed),
    ("FG-11-CERTIFIABLE", probe_certifiable),
    ("FG-12-COMPOSABLE", probe_composable),
    ("FG-13-SPECIALIZED-BY-DECLARATION", probe_specialized),
)


def default_probe_registry() -> ProbeRegistry:
    """A registry seeded with the shipped probes, validated against the Constitution."""
    registry = ProbeRegistry(CallableProbe(gate, measure) for gate, measure in SHIPPED_PROBES)
    require_gates(registry.gates())
    return registry


__all__ = [
    "CATALOG_DIRNAME",
    "DEFAULT_REGISTER_FILENAME",
    "ARTIFACT_WRITE_CALLS",
    "IMPORT_PURITY_FORBIDDEN",
    "SHIPPED_PROBES",
    "CallableProbe",
    "CapabilityConformance",
    "ReplayDeclaration",
    "CapabilityDeclaration",
    "CapabilityRegister",
    "ConformanceDetermination",
    "ConformanceEngine",
    "ConformanceProbe",
    "ExtensionPointDeclaration",
    "FacetDeclaration",
    "FacetStatus",
    "NucleusProfile",
    "GateResult",
    "ProbeContext",
    "ProbeOutcome",
    "ProbeRegistry",
    "RegistryDeclaration",
    "SymbolRef",
    "Verdict",
    "catalog_path",
    "default_capability_register",
    "imported_modules",
    "called_names",
    "module_level_calls",
    "parse_source",
    "string_literals",
    "default_probe_registry",
    "load_capability_register",
    "probe_certifiable",
    "probe_compatibility_declared",
    "probe_composable",
    "probe_contract_published",
    "probe_evolution_additive",
    "probe_fail_closed",
    "probe_lifecycle_bootstrapped",
    "probe_policy_declared",
    "probe_provider_pluggable",
    "probe_registry_deterministic",
    "probe_runtime_invocable",
    "probe_service_registered",
    "probe_specialized",
]
