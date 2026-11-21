"""UCOS-EPIC-001 — Typed registries and the Universal Registry Platform facade.

The mission requires a single registration authority expressed through thirteen
registries: the **Registry Core** (:class:`~engine.registry.universal.core.RegistryCore`)
plus twelve typed registries. Each typed registry is a thin, kind-bound
specialisation over the shared core: it fixes the :class:`RegistryKind`, a default
namespace, and the kind-specific *required attributes*, then delegates the
constitutional enforcement (deterministic ids, no duplicates, Knowledge Once,
versioning, audit) to the one core.

:class:`UniversalRegistryPlatform` composes the core, one shared audit trail, and
all twelve typed registries behind a single, versioned interface contract
(``registry.platform`` v1.0.0), so the whole platform is one auditable authority.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, ClassVar

from engine.foundation.contracts.contract import Contract, ContractRegistry, Version
from engine.registry.universal.audit import AuditJournal, Clock
from engine.registry.universal.core import DEFAULT_ACTOR, RegistryCore
from engine.registry.universal.errors import RegistrationValidationError
from engine.registry.universal.identity import RegistryKind, deterministic_id, normalize_namespace
from engine.registry.universal.records import Registration, RegistrationRequest


class TypedRegistry:
    """Base class for a kind-bound registry over a shared :class:`RegistryCore`."""

    kind: ClassVar[RegistryKind]
    default_namespace: ClassVar[str]
    required_attributes: ClassVar[frozenset[str]] = frozenset()

    __slots__ = ("_core",)

    def __init__(self, core: RegistryCore) -> None:
        self._core = core

    # -- write -----------------------------------------------------------------

    def register(
        self,
        *,
        natural_key: str,
        name: str,
        version: str | Version = "1.0.0",
        namespace: str | None = None,
        attributes: dict[str, Any] | None = None,
        description: str = "",
        owner: str = "UNASSIGNED",
        dependencies: Any = None,
        tags: Any = None,
        provenance: Any = None,
        actor: str | None = None,
    ) -> Registration:
        """Register (a version of) an artifact of this registry's kind."""
        attrs = dict(attributes or {})
        missing = self.required_attributes - set(attrs)
        if missing:
            raise RegistrationValidationError(
                "missing required attributes for kind",
                kind=self.kind.value,
                missing=sorted(missing),
            )
        request = RegistrationRequest.build(
            kind=self.kind,
            namespace=namespace or self.default_namespace,
            natural_key=natural_key,
            name=name,
            version=version,
            attributes=attrs,
            description=description,
            owner=owner,
            dependencies=dependencies,
            tags=tags,
            provenance=provenance,
        )
        return self._core.register(request, actor=actor)

    # -- read ------------------------------------------------------------------

    def id_for(self, natural_key: str, namespace: str | None = None) -> str:
        """The deterministic ``universal_id`` for a natural key in this registry."""
        return deterministic_id(self.kind, namespace or self.default_namespace, natural_key)

    def get(self, natural_key: str, namespace: str | None = None) -> Registration:
        """Return the current head registration for a natural key."""
        return self._core.get(self.id_for(natural_key, namespace))

    def get_by_id(self, universal_id: str) -> Registration:
        """Return the current head registration for an explicit id."""
        return self._core.get(universal_id)

    def exists(self, natural_key: str, namespace: str | None = None) -> bool:
        """True iff a registration exists for the natural key."""
        return self._core.exists(self.id_for(natural_key, namespace))

    def history(self, natural_key: str, namespace: str | None = None) -> tuple[Registration, ...]:
        """Every registered version for the natural key, in version order."""
        return self._core.history(self.id_for(natural_key, namespace))

    def all(self) -> tuple[Registration, ...]:
        """Every head registration of this registry's kind."""
        return self._core.by_kind(self.kind)

    def count(self) -> int:
        """Number of distinct identities registered under this kind."""
        return len(self.all())


# --------------------------------------------------------------------------- #
# The twelve typed registries. Required attributes keep each kind meaningful    #
# without over-constraining an open, forward-compatible vocabulary (UMB-006).   #
# --------------------------------------------------------------------------- #


class NamespaceRegistry(TypedRegistry):
    """Registers namespaces — the addressing roots other artifacts register into."""

    kind = RegistryKind.NAMESPACE
    default_namespace = "ucos.namespace"
    required_attributes = frozenset({"scope"})

    def declare(self, path: str, *, scope: str = "internal", **kwargs: Any) -> Registration:
        """Declare a namespace ``path`` (validated) as a first-class artifact."""
        normalized = normalize_namespace(path)
        attributes = dict(kwargs.pop("attributes", {}) or {})
        attributes.setdefault("scope", scope)
        attributes.setdefault("path", normalized)
        return self.register(
            natural_key=normalized,
            name=kwargs.pop("name", normalized),
            attributes=attributes,
            **kwargs,
        )


class CapabilityRegistry(TypedRegistry):
    """Registers platform capabilities (CAP-*) — what the system can do."""

    kind = RegistryKind.CAPABILITY
    default_namespace = "ucos.capability"
    required_attributes = frozenset({"summary"})


class DocumentRegistry(TypedRegistry):
    """Registers governed documents — each bound to a Repository-Truth path."""

    kind = RegistryKind.DOCUMENT
    default_namespace = "ucos.document"
    required_attributes = frozenset({"path"})


class EngineRegistry(TypedRegistry):
    """Registers computational engines (ENG-*) — declared by entrypoint."""

    kind = RegistryKind.ENGINE
    default_namespace = "ucos.engine"
    required_attributes = frozenset({"entrypoint"})


class ComponentRegistry(TypedRegistry):
    """Registers components (CMP-*) — placed in an architecture layer."""

    kind = RegistryKind.COMPONENT
    default_namespace = "ucos.component"
    required_attributes = frozenset({"layer"})


class ApiRegistry(TypedRegistry):
    """Registers APIs — each declaring its versioned contract and protocol."""

    kind = RegistryKind.API
    default_namespace = "ucos.api"
    required_attributes = frozenset({"contract", "protocol"})


class ServiceRegistry(TypedRegistry):
    """Registers services (SVC-*) — each owned by a domain."""

    kind = RegistryKind.SERVICE
    default_namespace = "ucos.service"
    required_attributes = frozenset({"domain"})


class ApplicationRegistry(TypedRegistry):
    """Registers applications (APP-*) — each with a user-facing surface."""

    kind = RegistryKind.APPLICATION
    default_namespace = "ucos.application"
    required_attributes = frozenset({"surface"})


class InfrastructureRegistry(TypedRegistry):
    """Registers infrastructure (INF-*) — each with a provider."""

    kind = RegistryKind.INFRASTRUCTURE
    default_namespace = "ucos.infrastructure"
    required_attributes = frozenset({"provider"})


class DependencyRegistry(TypedRegistry):
    """Registers dependency edges (DEP-*) as first-class, auditable artifacts."""

    kind = RegistryKind.DEPENDENCY
    default_namespace = "ucos.dependency"
    required_attributes = frozenset({"source", "target"})

    def link(
        self,
        *,
        source: str,
        target: str,
        relation: str = "Depends-On",
        version: str | Version = "1.0.0",
        **kwargs: Any,
    ) -> Registration:
        """Register a directed dependency edge ``source -> target``."""
        if not source or not target:
            raise RegistrationValidationError("source and target are required", field="edge")
        if source == target:
            raise RegistrationValidationError(
                "a dependency edge cannot be a self-loop", node=source
            )
        attributes = dict(kwargs.pop("attributes", {}) or {})
        attributes.update({"source": source, "target": target, "relation": relation})
        return self.register(
            natural_key=f"{source}->{target}",
            name=kwargs.pop("name", f"{source} {relation} {target}"),
            version=version,
            attributes=attributes,
            **kwargs,
        )


class EvidenceRegistry(TypedRegistry):
    """Registers evidence artifacts (EVD-*) — each bound to a subject."""

    kind = RegistryKind.EVIDENCE
    default_namespace = "ucos.evidence"
    required_attributes = frozenset({"subject"})


class CertificationRegistry(TypedRegistry):
    """Registers certifications (CERT-*) — a determination over a subject."""

    kind = RegistryKind.CERTIFICATION
    default_namespace = "ucos.certification"
    required_attributes = frozenset({"subject", "determination"})


#: The versioned interface contract the whole platform satisfies (AR-03, PL-05).
REGISTRY_PLATFORM_CONTRACT = Contract(
    name="registry.platform",
    version=Version(1, 0, 0),
    description=(
        "Write-side single registration authority for UCOS artifacts: deterministic "
        "ids, no-duplicate + Knowledge-Once enforcement, version chains, acyclic "
        "dependencies, and a tamper-evident append-only audit trail. Composes twelve "
        "typed registries over one Registry Core."
    ),
)


class UniversalRegistryPlatform:
    """The single registration authority: Registry Core + twelve typed registries."""

    __slots__ = (
        "_core",
        "namespaces",
        "capabilities",
        "documents",
        "engines",
        "components",
        "apis",
        "services",
        "applications",
        "infrastructure",
        "dependencies",
        "evidence",
        "certifications",
    )

    def __init__(
        self,
        *,
        journal: AuditJournal | None = None,
        actor: str = DEFAULT_ACTOR,
        clock: Clock | None = None,
    ) -> None:
        self._core = RegistryCore(journal=journal, actor=actor, clock=clock)
        self.namespaces = NamespaceRegistry(self._core)
        self.capabilities = CapabilityRegistry(self._core)
        self.documents = DocumentRegistry(self._core)
        self.engines = EngineRegistry(self._core)
        self.components = ComponentRegistry(self._core)
        self.apis = ApiRegistry(self._core)
        self.services = ServiceRegistry(self._core)
        self.applications = ApplicationRegistry(self._core)
        self.infrastructure = InfrastructureRegistry(self._core)
        self.dependencies = DependencyRegistry(self._core)
        self.evidence = EvidenceRegistry(self._core)
        self.certifications = CertificationRegistry(self._core)

    # -- core + contract -------------------------------------------------------

    @property
    def core(self) -> RegistryCore:
        """The underlying single registration authority."""
        return self._core

    @property
    def contract(self) -> Contract:
        """The versioned interface contract this platform satisfies (AR-03)."""
        return REGISTRY_PLATFORM_CONTRACT

    def register_contract(self, registry: ContractRegistry) -> None:
        """Publish this platform's contract into a Foundation contract registry."""
        registry.register(REGISTRY_PLATFORM_CONTRACT)

    def registries(self) -> dict[str, TypedRegistry]:
        """The twelve typed registries keyed by name (deterministic order)."""
        return {
            "namespace": self.namespaces,
            "capability": self.capabilities,
            "document": self.documents,
            "engine": self.engines,
            "component": self.components,
            "api": self.apis,
            "service": self.services,
            "application": self.applications,
            "infrastructure": self.infrastructure,
            "dependency": self.dependencies,
            "evidence": self.evidence,
            "certification": self.certifications,
        }

    # -- validation + evidence -------------------------------------------------

    def validate(self) -> bool:
        """Validate registry invariants and audit-chain integrity."""
        return self._core.verify()

    def summary(self) -> dict[str, Any]:
        """A deterministic, loggable summary of the platform state."""
        return {
            "contract": f"{self.contract.name}@{self.contract.version}",
            "identities": self._core.count(),
            "versions": self._core.count_versions(),
            "audit_entries": len(self._core.journal),
            "audit_head": self._core.journal.head_hash(),
            "by_kind": {name: registry.count() for name, registry in self.registries().items()},
        }

    def export(self, directory: str | Path) -> dict[str, str]:
        """Export a deterministic snapshot + audit journal as canonical JSON.

        Returns the written paths. Writes only under ``directory`` (never the
        frozen corpus). The snapshot is the *Database model* materialised as data.
        """
        base = Path(directory)
        base.mkdir(parents=True, exist_ok=True)
        from engine.registry.universal.identity import canonical_json

        snapshot_path = base / "registry-snapshot.json"
        snapshot_path.write_text(canonical_json(self._core.snapshot()), encoding="utf-8")
        audit_path = self._core.journal.save(base / "registry-audit.json")
        return {"snapshot": str(snapshot_path), "audit": str(audit_path)}


__all__ = [
    "TypedRegistry",
    "NamespaceRegistry",
    "CapabilityRegistry",
    "DocumentRegistry",
    "EngineRegistry",
    "ComponentRegistry",
    "ApiRegistry",
    "ServiceRegistry",
    "ApplicationRegistry",
    "InfrastructureRegistry",
    "DependencyRegistry",
    "EvidenceRegistry",
    "CertificationRegistry",
    "UniversalRegistryPlatform",
    "REGISTRY_PLATFORM_CONTRACT",
]
