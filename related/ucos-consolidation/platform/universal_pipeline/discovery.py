"""UAPF-000001 — the Universal Discovery Engine (pipelines discovered from declarations).

Every pipeline UAPF runs is *discovered from a declaration catalogue*, never imported from a
module and never listed in code. This is the module that makes that true: a catalogue is a
document, :func:`load_catalog` normalizes it, and :class:`PipelineDiscovery` admits what it
declares into the registry. Adding a pipeline to the repository is therefore an entry in a
catalogue, and adding a *category* of pipeline is an entry in the same catalogue's
``pipeline_types`` — neither is a code change.

Purity, and where the filesystem lives
--------------------------------------
:func:`load_catalog` accepts a JSON *document* (text) or an already-parsed mapping. It does
not open files. That is not an oversight: every module in this package is pure over its
inputs so an identical declaration yields an identical outcome in every environment, and the
moment discovery read a path, "what did we discover" would depend on the machine. Reading
bytes is the caller's concern — the same posture
:meth:`platform.foundation.dag_ledger.EventDag.export` takes toward persistence.

Idempotent admission
--------------------
Re-reading the same catalogue admits nothing new and refuses nothing: an already-registered
pipeline version is reported as ``already-registered`` rather than raised, and an
already-registered pipeline *type* is skipped. A continuous evolution pipeline re-reads its
catalogue constantly, so a second read must be a no-op (AIF-L13) — while a *conflicting*
declaration (same id and version, different content) is a refusal, because that is a real
disagreement and not a retry.

Refusals are reported, not raised
---------------------------------
Discovery is the one place a failure is a *finding* rather than an exception: a catalogue
with one malformed entry among fifty must admit the forty-nine and name the one. So
:class:`DiscoveryReport` carries refusals with reasons. Malformed *input to discovery
itself* — a catalogue that is not a document, or has no ``pipelines`` key — still fails
closed, because that is not a finding about a pipeline.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from platform.foundation.contracts import content_hash
from platform.universal_pipeline.contracts import (
    PipelineDefinition,
    pipeline_types,
    register_pipeline_type,
)
from platform.universal_pipeline.errors import PipelineDiscoveryError, UniversalPipelineError
from platform.universal_pipeline.events import PipelineEventBus
from platform.universal_pipeline.identity import Identity, mint
from platform.universal_pipeline.registry import PipelineRegistry
from typing import Any

#: The catalogue format tag. Semantic, so the format can widen append-only.
CATALOG_FORMAT = "uapf-pipeline-catalog/1.0.0"


def load_catalog(document: str | Mapping[str, Any]) -> dict[str, Any]:
    """Normalize a pipeline declaration catalogue from JSON text or a mapping.

    Returns a mapping with a stable shape — ``catalog_id``, ``format``, ``pipeline_types``,
    ``pipelines`` — so every consumer sees the same structure regardless of what the author
    omitted.

    Raises:
        PipelineDiscoveryError: if the document is not valid JSON, is not a mapping, declares
            no ``pipelines`` key, or declares ``pipelines`` / ``pipeline_types`` as something
            other than a list. These are defects in the catalogue *as a document*, so they
            fail closed rather than becoming findings.
    """
    if isinstance(document, str):
        try:
            parsed: Any = json.loads(document)
        except json.JSONDecodeError as exc:
            raise PipelineDiscoveryError(
                "catalogue is not valid JSON", reason=exc.msg, line=exc.lineno
            ) from exc
    else:
        parsed = document
    if not isinstance(parsed, Mapping):
        raise PipelineDiscoveryError("catalogue must be a mapping")
    if "pipelines" not in parsed:
        raise PipelineDiscoveryError("catalogue declares no 'pipelines' key")
    pipelines = parsed["pipelines"]
    if not isinstance(pipelines, list):
        raise PipelineDiscoveryError("catalogue 'pipelines' must be a list")
    declared_types = parsed.get("pipeline_types", [])
    if not isinstance(declared_types, list):
        raise PipelineDiscoveryError("catalogue 'pipeline_types' must be a list")
    return {
        "catalog_id": str(parsed.get("catalog_id", "uapf.catalog")),
        "format": str(parsed.get("format", CATALOG_FORMAT)),
        "description": str(parsed.get("description", "")),
        "pipeline_types": list(declared_types),
        "pipelines": list(pipelines),
    }


@dataclass(frozen=True, slots=True)
class DiscoveryReport:
    """The complete, auditable outcome of one discovery pass over one catalogue."""

    catalog_id: str
    admitted: tuple[str, ...] = ()
    already_registered: tuple[str, ...] = ()
    refused: tuple[tuple[str, str], ...] = ()
    types_registered: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.catalog_id, str) or not self.catalog_id:
            raise PipelineDiscoveryError("discovery report catalogue id is required")
        for label, values in (
            ("admitted", self.admitted),
            ("already_registered", self.already_registered),
            ("refused", self.refused),
            ("types_registered", self.types_registered),
        ):
            if not isinstance(values, tuple):
                raise PipelineDiscoveryError(
                    f"discovery report {label} must be a tuple", catalog_id=self.catalog_id
                )

    @property
    def identity(self) -> Identity:
        return mint("discovery-report", self.catalog_id, self.fingerprint())

    @property
    def clean(self) -> bool:
        """True iff nothing in the catalogue was refused."""
        return not self.refused

    @property
    def considered(self) -> int:
        """How many pipeline declarations the pass looked at."""
        return len(self.admitted) + len(self.already_registered) + len(self.refused)

    def to_dict(self) -> dict[str, Any]:
        return {
            "catalog_id": self.catalog_id,
            "considered": self.considered,
            "admitted": list(self.admitted),
            "already_registered": list(self.already_registered),
            "refused": [{"declaration": ref, "reason": reason} for ref, reason in self.refused],
            "types_registered": list(self.types_registered),
            "clean": self.clean,
        }

    def fingerprint(self) -> str:
        return content_hash(
            {
                "catalog_id": self.catalog_id,
                "admitted": list(self.admitted),
                "already_registered": list(self.already_registered),
                "refused": [list(pair) for pair in self.refused],
                "types_registered": list(self.types_registered),
            }
        )

    def require_clean(self) -> None:
        """Fail closed if anything was refused.

        The opt-in strict mode: a continuous pipeline tolerates refusals and reports them,
        while a CI gate calls this and fails the build.

        Raises:
            PipelineDiscoveryError: naming every refused declaration and its reason.
        """
        if self.refused:
            raise PipelineDiscoveryError(
                "catalogue contains refused declarations",
                catalog_id=self.catalog_id,
                refused=[list(pair) for pair in self.refused],
            )


class PipelineDiscovery:
    """Admits declared pipelines (and declared pipeline types) into a registry."""

    __slots__ = ("_registry", "_bus")

    def __init__(self, registry: PipelineRegistry, *, bus: PipelineEventBus | None = None) -> None:
        if not isinstance(registry, PipelineRegistry):
            raise PipelineDiscoveryError("discovery requires a PipelineRegistry")
        if bus is not None and not isinstance(bus, PipelineEventBus):
            raise PipelineDiscoveryError("bus must be a PipelineEventBus")
        self._registry = registry
        self._bus = bus

    def discover(self, document: str | Mapping[str, Any]) -> DiscoveryReport:
        """Normalize ``document``, admit every declaration it holds, and report.

        Pipeline *types* are registered before pipelines, because a pipeline declaring a type
        the same catalogue introduces must be admissible — that is precisely how an unlimited
        set of future pipeline categories is opened without touching code.

        Raises:
            PipelineDiscoveryError: only if the catalogue is malformed *as a document*
                (see :func:`load_catalog`). Per-declaration problems become refusals.
        """
        catalog = load_catalog(document)
        types_registered = self._register_types(catalog["pipeline_types"])
        admitted: list[str] = []
        already: list[str] = []
        refused: list[tuple[str, str]] = []
        for index, declaration in enumerate(catalog["pipelines"]):
            reference = self._reference(declaration, index)
            try:
                definition = PipelineDefinition.from_dict(declaration)
            except UniversalPipelineError as exc:
                refused.append((reference, f"{exc.code}: {exc.message}"))
                continue
            key = (definition.pipeline_id, definition.version)
            if key in self._registry:
                existing = self._registry.get(*key)
                if existing.definition.fingerprint() == definition.fingerprint():
                    already.append(f"{key[0]}@{key[1]}")
                else:
                    refused.append(
                        (
                            f"{key[0]}@{key[1]}",
                            "a different declaration is already registered at this version",
                        )
                    )
                continue
            try:
                entry = self._registry.register(definition)
            except UniversalPipelineError as exc:
                refused.append((f"{key[0]}@{key[1]}", f"{exc.code}: {exc.message}"))
                continue
            admitted.append(f"{entry.pipeline_id}@{entry.version}")
        report = DiscoveryReport(
            catalog_id=catalog["catalog_id"],
            admitted=tuple(admitted),
            already_registered=tuple(already),
            refused=tuple(refused),
            types_registered=tuple(types_registered),
        )
        if self._bus is not None:
            self._bus.emit("uapf.catalog.discovered", report.catalog_id, payload=report.to_dict())
        return report

    # -- internals --------------------------------------------------------------------

    def _register_types(self, declared: list[Any]) -> list[str]:
        """Register every declared type not already registered; return the new ones.

        Skipping an existing type rather than raising is what makes re-reading a catalogue
        idempotent.
        """
        registered: list[str] = []
        known = set(pipeline_types())
        for declaration in declared:
            if isinstance(declaration, Mapping):
                name = str(declaration.get("pipeline_type", ""))
                description = str(declaration.get("description", ""))
            else:
                name = str(declaration)
                description = ""
            if not name:
                raise PipelineDiscoveryError("declared pipeline type must name a type")
            if name in known:
                continue
            register_pipeline_type(name, description)
            known.add(name)
            registered.append(name)
        return sorted(registered)

    @staticmethod
    def _reference(declaration: Any, index: int) -> str:
        """A stable human reference for a declaration that may be too malformed to name."""
        if isinstance(declaration, Mapping):
            pipeline_id = str(declaration.get("pipeline_id", "")) or f"#{index}"
            version = str(declaration.get("version", "")) or "?"
            return f"{pipeline_id}@{version}"
        return f"#{index}"


__all__ = ["CATALOG_FORMAT", "DiscoveryReport", "PipelineDiscovery", "load_catalog"]
