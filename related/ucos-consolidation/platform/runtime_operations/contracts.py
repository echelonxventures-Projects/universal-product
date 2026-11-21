"""EC2-TASK-000163 — Runtime Operations Contracts (EC2-EPIC-012).

The versioned contract surface for the UCOS Platform **Runtime Operations Runtime**
(L8 Operations of the Program architecture, §4) plus the immutable **core vocabulary**,
the **descriptive record metadata**, and the **read-only view value types** every
runtime-operations service speaks. It reuses the certified EC-1 contract machinery through
the Platform Foundation (:func:`~platform.foundation.contracts.platform_contract`,
:class:`~platform.foundation.contracts.ContractRef`) and binds runtime-operations
authorization to the single §3.2 :class:`~platform.identity.contracts.CapabilityGroup`
``runtime-operations`` (PC-11, matrix index 12) that **already physically exists** in the
certified Identity Layer. EC2-EPIC-012 introduces **no new capability group, no new
authority, and no new authorization logic**.

It also **reuses — rather than reinventing** — the certified EC-1 Runtime Assembly
vocabulary: every surfaced datum is a faithful projection of a
:class:`~engine.runtime.assembly.RuntimeUnit`,
:class:`~engine.runtime.deploy.DeploymentDescriptor`, and
:class:`~engine.runtime.deploy.RollbackDescriptor` produced by the certified engine, and a
faithful projection of a :class:`~platform.certification.contracts.CertificationConsoleRecord`
produced by the certified Certification Console (EC2-EPIC-011). The runtime **records**
these read-only; it computes no descriptor, deployment, or rollback of its own (TP-01).

Vocabulary:
    * :class:`RuntimeOperationKind` — the two governed operation kinds (deploy / rollback).
    * :class:`RuntimeOperationAction` — the governed console verbs, each mapped to the
      coarse RBAC :class:`~platform.foundation.identity.Permission` it requires
      (``deploy``/``rollback`` require :data:`Permission.EXECUTE`; all inspection verbs
      require :data:`Permission.READ`).
    * :class:`RuntimeOperationMetadata` — immutable descriptive metadata for an operation.
    * :class:`RuntimeUnitReference` / :class:`CertificationReference` /
      :class:`DeploymentDescriptorView` / :class:`RollbackDescriptorView` — immutable,
      serializable read projections of the certified engine / certification outputs.
    * :class:`RuntimeOperationRecord` — an immutable, content-addressed operation record
      binding a certified :class:`RuntimeUnit` + the deployment or rollback descriptor
      (produced read-only by EC-1) to the governing certification (by reference), scoped
      to a tenant, carrying the operating owner.
    * :data:`RUNTIME_OPERATIONS_CONTRACTS` — the published runtime-operations contracts.

All types are **immutable, typed, deterministic, and serializable**, hold no runtime
state, and hold no secret material (SEC-04).
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from enum import Enum
from platform.certification.contracts import CertificationConsoleRecord
from platform.foundation.contracts import (
    Contract,
    ContractRef,
    content_hash,
    platform_contract,
)
from platform.foundation.errors import PlatformContractError
from platform.foundation.identity import Permission
from platform.identity.contracts import CapabilityGroup
from platform.runtime_operations.errors import RuntimeOperationsContractError
from typing import Any

from engine.runtime.assembly import RuntimeUnit
from engine.runtime.deploy import DeploymentDescriptor, RollbackDescriptor
from engine.runtime.disclosure import disclosure_present

#: The semantic version of the Runtime Operations Runtime contract surface (AR-03/PL-05).
RUNTIME_OPERATIONS_CONTRACT_VERSION = "1.0.0"

#: The §3.2 capability group authorizing every runtime operation (reused; no new group).
RUNTIME_OPERATIONS_GROUP = CapabilityGroup.RUNTIME_OPERATIONS

#: The certified EC-1 runtime contracts this runtime consumes by reference (L4).
ENGINE_RUNTIME_ASSEMBLE_CONTRACT = "engine.runtime.assemble"
ENGINE_RUNTIME_DEPLOY_CONTRACT = "engine.runtime.deploy"


class RuntimeOperationKind(str, Enum):
    """The two governed runtime-operation kinds (deploy / rollback of a CERTIFIED unit)."""

    DEPLOY = "deploy"
    ROLLBACK = "rollback"


class RuntimeOperationAction(str, Enum):
    """The governed runtime-operations verbs.

    ``DEPLOY`` and ``ROLLBACK`` are the governed operate verbs and require
    :data:`Permission.EXECUTE` on the ``runtime-operations`` group (the §3.2 Operator
    ``X``); every remaining verb is inspection-only and requires :data:`Permission.READ`.
    The runtime exposes no create/administer authority and no mutation path to any
    surfaced descriptor, certification record, or ledger entry.
    """

    DISCOVER = "discover"
    INSPECT = "inspect"
    DEPLOY = "deploy"
    ROLLBACK = "rollback"
    VIEW_LEDGER = "view-ledger"
    VIEW_LINEAGE = "view-lineage"
    SEARCH = "search"
    TRACK = "track"
    VERIFY_REVERSIBILITY = "verify-reversibility"
    VALIDATE_GOVERNANCE = "validate-governance"


#: The governed operate verbs (require EXECUTE); every other verb requires READ.
_EXECUTE_ACTIONS: frozenset[RuntimeOperationAction] = frozenset(
    {RuntimeOperationAction.DEPLOY, RuntimeOperationAction.ROLLBACK}
)

#: The verb→permission map (Determination §7/§13). Fail-closed and total.
_ACTION_PERMISSIONS: dict[RuntimeOperationAction, Permission] = {
    action: (Permission.EXECUTE if action in _EXECUTE_ACTIONS else Permission.READ)
    for action in RuntimeOperationAction
}


def permission_for(action: RuntimeOperationAction) -> Permission:
    """Return the RBAC permission required by a runtime-operations action (fail-closed)."""
    if not isinstance(action, RuntimeOperationAction):
        raise RuntimeOperationsContractError("action must be a RuntimeOperationAction")
    return _ACTION_PERMISSIONS[action]


def all_runtime_operation_actions() -> tuple[RuntimeOperationAction, ...]:
    """Return every runtime-operations action in stable declaration order."""
    return tuple(RuntimeOperationAction)


def action_for_kind(kind: RuntimeOperationKind) -> RuntimeOperationAction:
    """Map an operation kind to the governed operate verb it requires (fail-closed)."""
    if not isinstance(kind, RuntimeOperationKind):
        raise RuntimeOperationsContractError("kind must be a RuntimeOperationKind")
    return (
        RuntimeOperationAction.DEPLOY
        if kind is RuntimeOperationKind.DEPLOY
        else RuntimeOperationAction.ROLLBACK
    )


# --------------------------------------------------------------------------- #
# Descriptive record metadata (value data only; carries no authority).        #
# --------------------------------------------------------------------------- #


@dataclass(frozen=True, slots=True)
class RuntimeOperationMetadata:
    """Immutable, content-addressed descriptive metadata for a runtime-operation record."""

    description: str = ""
    labels: frozenset[str] = field(default_factory=frozenset)
    annotations: Mapping[str, str] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        *,
        description: str = "",
        labels: Iterable[str] | None = None,
        annotations: Mapping[str, str] | None = None,
    ) -> RuntimeOperationMetadata:
        """Build normalized, validated metadata (deterministic)."""
        if not isinstance(description, str):
            raise RuntimeOperationsContractError("operation description must be a string")
        label_set = frozenset(_require_str(label, "label") for label in (labels or ()))
        annots = {
            _require_str(k, "annotation key"): _require_str(v, "annotation value")
            for k, v in dict(annotations or {}).items()
        }
        return cls(description=description, labels=label_set, annotations=annots)

    def has_label(self, label: str) -> bool:
        return label in self.labels

    def to_dict(self) -> dict[str, Any]:
        return {
            "description": self.description,
            "labels": sorted(self.labels),
            "annotations": {k: self.annotations[k] for k in sorted(self.annotations)},
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


def _require_str(value: Any, what: str) -> str:
    if not isinstance(value, str) or not value:
        raise RuntimeOperationsContractError(f"operation {what} must be a non-empty string")
    return value


#: The canonical empty metadata (shared default; immutable).
EMPTY_RUNTIME_OPERATION_METADATA = RuntimeOperationMetadata()


# --------------------------------------------------------------------------- #
# Read-only view projections of the certified engine / certification outputs. #
# --------------------------------------------------------------------------- #


@dataclass(frozen=True, slots=True)
class RuntimeUnitReference:
    """An immutable, content-addressed reference to a certified :class:`RuntimeUnit`.

    Surfaces the deployable runtime unit *by reference* — its pinned identity, image,
    provenance, dependency-closure size, and whether it carries the EC-1 provisional-state
    disclosure — without mutating or re-deriving it (P6). The ``reference_id`` is
    content-addressed from the pinned unit identity, so a rendered reference is verifiable
    against the assembled unit.
    """

    runtime_id: str
    blueprint_id: str
    artifact_id: str
    name: str
    version: str
    package_sha256: str
    image_reference: str
    environment: str
    provenance_chain: tuple[str, ...]
    closure_size: int
    disclosure_present: bool
    reference_id: str = ""

    @classmethod
    def from_unit(cls, unit: RuntimeUnit) -> RuntimeUnitReference:
        if not isinstance(unit, RuntimeUnit):
            raise RuntimeOperationsContractError("RuntimeUnitReference requires a RuntimeUnit")
        core = {
            "runtime_id": unit.runtime_id,
            "blueprint_id": unit.blueprint_id,
            "artifact_id": unit.artifact_id,
            "version": unit.version,
            "package_sha256": unit.package_sha256,
            "image_reference": unit.image_reference,
        }
        return cls(
            runtime_id=unit.runtime_id,
            blueprint_id=unit.blueprint_id,
            artifact_id=unit.artifact_id,
            name=unit.name,
            version=unit.version,
            package_sha256=unit.package_sha256,
            image_reference=unit.image_reference,
            environment=unit.environment,
            provenance_chain=tuple(unit.provenance_chain),
            closure_size=len(unit.dependency_closure),
            disclosure_present=disclosure_present(unit.disclosure),
            reference_id=f"UCOS-RURF-{content_hash(core)[:16]}",
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "reference_id": self.reference_id,
            "runtime_id": self.runtime_id,
            "blueprint_id": self.blueprint_id,
            "artifact_id": self.artifact_id,
            "name": self.name,
            "version": self.version,
            "package_sha256": self.package_sha256,
            "image_reference": self.image_reference,
            "environment": self.environment,
            "provenance_chain": list(self.provenance_chain),
            "closure_size": self.closure_size,
            "disclosure_present": self.disclosure_present,
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


@dataclass(frozen=True, slots=True)
class CertificationReference:
    """An immutable projection of the governing :class:`CertificationConsoleRecord`.

    Records — by reference — the certification that authorizes the operation: the
    certification id, the certified target (which must be the runtime unit), the
    blueprint, the pinned version, the certified status, and whether the target is
    CERTIFIED. It re-derives nothing; every field is a citation of the certified record.
    """

    certification_id: str
    target_id: str
    blueprint_id: str
    version: str
    status: str
    certified: bool

    @classmethod
    def from_record(cls, record: CertificationConsoleRecord) -> CertificationReference:
        if not isinstance(record, CertificationConsoleRecord):
            raise RuntimeOperationsContractError(
                "CertificationReference requires a CertificationConsoleRecord"
            )
        return cls(
            certification_id=record.certification_id,
            target_id=record.target_id,
            blueprint_id=record.blueprint_id,
            version=record.version,
            status=record.record.status.value,
            certified=record.certified,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "certification_id": self.certification_id,
            "target_id": self.target_id,
            "blueprint_id": self.blueprint_id,
            "version": self.version,
            "status": self.status,
            "certified": self.certified,
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


@dataclass(frozen=True, slots=True)
class DeploymentDescriptorView:
    """An immutable read projection of a certified :class:`DeploymentDescriptor` (by reference)."""

    runtime_id: str
    blueprint_id: str
    artifact_id: str
    environment: str
    image: str
    immutable: bool
    manifest_kinds: tuple[str, ...]
    closure_size: int
    provenance_chain: tuple[str, ...]
    disclosure_present: bool
    descriptor_fingerprint: str

    @classmethod
    def from_descriptor(cls, descriptor: DeploymentDescriptor) -> DeploymentDescriptorView:
        if not isinstance(descriptor, DeploymentDescriptor):
            raise RuntimeOperationsContractError(
                "DeploymentDescriptorView requires a DeploymentDescriptor"
            )
        payload = descriptor.to_dict()
        return cls(
            runtime_id=descriptor.runtime_id,
            blueprint_id=descriptor.blueprint_id,
            artifact_id=descriptor.artifact_id,
            environment=descriptor.environment,
            image=descriptor.image,
            immutable=bool(payload["immutable"]),
            manifest_kinds=tuple(m["kind"] for m in descriptor.kubernetes),
            closure_size=len(descriptor.dependency_closure),
            provenance_chain=tuple(descriptor.provenance_chain),
            disclosure_present=disclosure_present(descriptor.disclosure),
            descriptor_fingerprint=content_hash(payload),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": RuntimeOperationKind.DEPLOY.value,
            "runtime_id": self.runtime_id,
            "blueprint_id": self.blueprint_id,
            "artifact_id": self.artifact_id,
            "environment": self.environment,
            "image": self.image,
            "immutable": self.immutable,
            "manifest_kinds": list(self.manifest_kinds),
            "closure_size": self.closure_size,
            "provenance_chain": list(self.provenance_chain),
            "disclosure_present": self.disclosure_present,
            "descriptor_fingerprint": self.descriptor_fingerprint,
        }


@dataclass(frozen=True, slots=True)
class RollbackDescriptorView:
    """An immutable read projection of a certified :class:`RollbackDescriptor` (by reference)."""

    runtime_id: str
    blueprint_id: str
    artifact_id: str
    environment: str
    strategy: str
    reversible: bool
    has_checkpoint: bool
    reverts_to_present: bool
    restore_image: str
    closure_size: int
    disclosure_present: bool
    descriptor_fingerprint: str

    @classmethod
    def from_descriptor(cls, descriptor: RollbackDescriptor) -> RollbackDescriptorView:
        if not isinstance(descriptor, RollbackDescriptor):
            raise RuntimeOperationsContractError(
                "RollbackDescriptorView requires a RollbackDescriptor"
            )
        payload = descriptor.to_dict()
        return cls(
            runtime_id=descriptor.runtime_id,
            blueprint_id=descriptor.blueprint_id,
            artifact_id=descriptor.artifact_id,
            environment=descriptor.environment,
            strategy=descriptor.strategy,
            reversible=descriptor.reversible,
            has_checkpoint=bool(descriptor.checkpoint),
            reverts_to_present=descriptor.reverts_to is not None,
            restore_image=str(descriptor.kubernetes_rollback.get("restore_image", "")),
            closure_size=len(descriptor.dependency_closure),
            disclosure_present=disclosure_present(descriptor.disclosure),
            descriptor_fingerprint=content_hash(payload),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": RuntimeOperationKind.ROLLBACK.value,
            "runtime_id": self.runtime_id,
            "blueprint_id": self.blueprint_id,
            "artifact_id": self.artifact_id,
            "environment": self.environment,
            "strategy": self.strategy,
            "reversible": self.reversible,
            "has_checkpoint": self.has_checkpoint,
            "reverts_to_present": self.reverts_to_present,
            "restore_image": self.restore_image,
            "closure_size": self.closure_size,
            "disclosure_present": self.disclosure_present,
            "descriptor_fingerprint": self.descriptor_fingerprint,
        }


# --------------------------------------------------------------------------- #
# The operation record aggregate.                                             #
# --------------------------------------------------------------------------- #


@dataclass(frozen=True, slots=True)
class RuntimeOperationRecord:
    """An immutable, content-addressed governed runtime-operation record (a snapshot).

    Binds a certified :class:`RuntimeUnit` and the deployment **or** rollback descriptor
    (produced read-only by the certified EC-1 runtime engine) to the governing
    :class:`CertificationConsoleRecord` (by reference) and an optional originating
    generation ``request_ref``, workspace/project (by reference), and a ``tenant``
    isolation boundary, recording the operating ``owner_subject``. Exactly one of
    ``deployment`` / ``rollback`` is set, matching ``kind``. The ``operation_id`` is
    content-addressed from the engine ``runtime_id``, the kind, the descriptor
    fingerprint, and the binding — so recording is idempotent and reproducible for an
    identical operation regardless of when it is recorded (temporal ordering lives in the
    append-only ledger, the operation log, and the governed event stream).
    """

    operation_id: str
    kind: RuntimeOperationKind
    runtime_id: str
    blueprint_id: str
    artifact_id: str
    version: str
    environment: str
    unit: RuntimeUnit
    previous_unit: RuntimeUnit | None
    certification: CertificationConsoleRecord
    deployment: DeploymentDescriptor | None
    rollback: RollbackDescriptor | None
    previous_ref: str | None
    request_ref: str | None
    workspace_id: str | None
    project_id: str | None
    tenant: str | None
    owner_subject: str
    metadata: RuntimeOperationMetadata

    @classmethod
    def create(
        cls,
        *,
        kind: RuntimeOperationKind,
        unit: RuntimeUnit,
        certification: CertificationConsoleRecord,
        deployment: DeploymentDescriptor | None = None,
        rollback: RollbackDescriptor | None = None,
        owner_subject: str,
        environment: str,
        previous_unit: RuntimeUnit | None = None,
        request_ref: str | None = None,
        workspace_id: str | None = None,
        project_id: str | None = None,
        tenant: str | None = None,
        metadata: RuntimeOperationMetadata | None = None,
    ) -> RuntimeOperationRecord:
        """Build a content-addressed operation record (fail-closed; no re-derivation)."""
        if not isinstance(kind, RuntimeOperationKind):
            raise RuntimeOperationsContractError("record requires a RuntimeOperationKind")
        if not isinstance(unit, RuntimeUnit):
            raise RuntimeOperationsContractError("record requires a RuntimeUnit")
        if not isinstance(certification, CertificationConsoleRecord):
            raise RuntimeOperationsContractError("record requires a CertificationConsoleRecord")
        if not isinstance(owner_subject, str) or not owner_subject:
            raise RuntimeOperationsContractError("record owner_subject is required")
        if not isinstance(environment, str) or not environment:
            raise RuntimeOperationsContractError("record environment is required")
        descriptor = _require_descriptor(kind, deployment, rollback, unit)
        if previous_unit is not None and not isinstance(previous_unit, RuntimeUnit):
            raise RuntimeOperationsContractError(
                "record previous_unit must be a RuntimeUnit when provided"
            )
        if kind is RuntimeOperationKind.DEPLOY and previous_unit is not None:
            raise RuntimeOperationsContractError("deploy record must not carry a previous unit")
        previous_ref = previous_unit.runtime_id if previous_unit is not None else None
        for name, value in (
            ("request_ref", request_ref),
            ("workspace_id", workspace_id),
            ("project_id", project_id),
        ):
            if value is not None and (not isinstance(value, str) or not value):
                raise RuntimeOperationsContractError(
                    f"record {name} must be a non-empty string when provided"
                )
        md = metadata if metadata is not None else EMPTY_RUNTIME_OPERATION_METADATA
        if not isinstance(md, RuntimeOperationMetadata):
            raise RuntimeOperationsContractError(
                "record metadata must be a RuntimeOperationMetadata"
            )
        identity = {
            "kind": kind.value,
            "runtime_id": unit.runtime_id,
            "descriptor_sha256": content_hash(descriptor.to_dict()),
            "environment": environment,
            "certification_id": certification.certification_id,
            "previous_ref": previous_ref,
            "request_ref": request_ref,
            "workspace_id": workspace_id,
            "project_id": project_id,
            "tenant": tenant,
            "owner_subject": owner_subject,
        }
        return cls(
            operation_id=f"UCOS-ROPR-{content_hash(identity)[:16]}",
            kind=kind,
            runtime_id=unit.runtime_id,
            blueprint_id=unit.blueprint_id,
            artifact_id=unit.artifact_id,
            version=unit.version,
            environment=environment,
            unit=unit,
            previous_unit=previous_unit,
            certification=certification,
            deployment=deployment,
            rollback=rollback,
            previous_ref=previous_ref,
            request_ref=request_ref,
            workspace_id=workspace_id,
            project_id=project_id,
            tenant=tenant,
            owner_subject=owner_subject,
            metadata=md,
        )

    @property
    def certified(self) -> bool:
        """True iff the governing certification certified the runtime unit."""
        return self.certification.certified

    @property
    def descriptor(self) -> DeploymentDescriptor | RollbackDescriptor:
        """The single governing descriptor for this operation (deploy or rollback)."""
        return self.deployment if self.kind is RuntimeOperationKind.DEPLOY else self.rollback  # type: ignore[return-value]

    @property
    def reversible(self) -> bool:
        """True iff a rollback operation is reversible (IP-08); deploys are not rollbacks."""
        return self.kind is RuntimeOperationKind.ROLLBACK and bool(
            self.rollback is not None and self.rollback.reversible
        )

    def descriptor_fingerprint(self) -> str:
        """The content hash of the governing EC-1 descriptor (fidelity anchor)."""
        return content_hash(self.descriptor.to_dict())

    def unit_reference(self) -> RuntimeUnitReference:
        return RuntimeUnitReference.from_unit(self.unit)

    def certification_reference(self) -> CertificationReference:
        return CertificationReference.from_record(self.certification)

    def deployment_view(self) -> DeploymentDescriptorView:
        if self.deployment is None:
            raise RuntimeOperationsContractError(
                "operation has no deployment descriptor", operation_id=self.operation_id
            )
        return DeploymentDescriptorView.from_descriptor(self.deployment)

    def rollback_view(self) -> RollbackDescriptorView:
        if self.rollback is None:
            raise RuntimeOperationsContractError(
                "operation has no rollback descriptor", operation_id=self.operation_id
            )
        return RollbackDescriptorView.from_descriptor(self.rollback)

    def with_metadata(self, metadata: RuntimeOperationMetadata) -> RuntimeOperationRecord:
        """Return an immutable copy carrying ``metadata`` (the id is preserved)."""
        if not isinstance(metadata, RuntimeOperationMetadata):
            raise RuntimeOperationsContractError(
                "record metadata must be a RuntimeOperationMetadata"
            )
        return RuntimeOperationRecord(
            operation_id=self.operation_id,
            kind=self.kind,
            runtime_id=self.runtime_id,
            blueprint_id=self.blueprint_id,
            artifact_id=self.artifact_id,
            version=self.version,
            environment=self.environment,
            unit=self.unit,
            previous_unit=self.previous_unit,
            certification=self.certification,
            deployment=self.deployment,
            rollback=self.rollback,
            previous_ref=self.previous_ref,
            request_ref=self.request_ref,
            workspace_id=self.workspace_id,
            project_id=self.project_id,
            tenant=self.tenant,
            owner_subject=self.owner_subject,
            metadata=metadata,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "operation_id": self.operation_id,
            "kind": self.kind.value,
            "runtime_id": self.runtime_id,
            "blueprint_id": self.blueprint_id,
            "artifact_id": self.artifact_id,
            "version": self.version,
            "environment": self.environment,
            "certified": self.certified,
            "reversible": self.reversible,
            "unit_reference": self.unit_reference().to_dict(),
            "certification_reference": self.certification_reference().to_dict(),
            "descriptor": self.descriptor.to_dict(),
            "descriptor_fingerprint": self.descriptor_fingerprint(),
            "previous_ref": self.previous_ref,
            "request_ref": self.request_ref,
            "workspace_id": self.workspace_id,
            "project_id": self.project_id,
            "tenant": self.tenant,
            "owner_subject": self.owner_subject,
            "metadata": self.metadata.to_dict(),
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


def _require_descriptor(
    kind: RuntimeOperationKind,
    deployment: DeploymentDescriptor | None,
    rollback: RollbackDescriptor | None,
    unit: RuntimeUnit,
) -> DeploymentDescriptor | RollbackDescriptor:
    """Validate exactly one descriptor is present and consistent with ``kind`` + ``unit``."""
    if kind is RuntimeOperationKind.DEPLOY:
        if not isinstance(deployment, DeploymentDescriptor):
            raise RuntimeOperationsContractError("deploy record requires a DeploymentDescriptor")
        if rollback is not None:
            raise RuntimeOperationsContractError("deploy record must not carry a rollback")
        descriptor: DeploymentDescriptor | RollbackDescriptor = deployment
    else:
        if not isinstance(rollback, RollbackDescriptor):
            raise RuntimeOperationsContractError("rollback record requires a RollbackDescriptor")
        if deployment is not None:
            raise RuntimeOperationsContractError("rollback record must not carry a deployment")
        descriptor = rollback
    if descriptor.runtime_id != unit.runtime_id:
        raise RuntimeOperationsContractError(
            "descriptor/unit runtime mismatch",
            descriptor_runtime=descriptor.runtime_id,
            unit_runtime=unit.runtime_id,
        )
    return descriptor


# --------------------------------------------------------------------------- #
# The published runtime-operations contract surface (L8).                     #
# --------------------------------------------------------------------------- #

#: The service contract identities the Runtime Operations Runtime publishes. Each maps to
#: an EC2-EPIC-012 deliverable; consumers bind to these by reference (PL-05).
_RUNTIME_OPERATIONS_CONTRACT_NAMES: tuple[tuple[str, str], ...] = (
    ("runtime.descriptors.discover", "Descriptors — deploy/rollback discovery + inspection."),
    ("runtime.facade.reference", "Facade — read-only engine.runtime reproduction (P6)."),
    ("runtime.admission.evaluate", "Admission — CERTIFIED-only deploy/rollback gate."),
    ("runtime.operations.orchestrate", "Operations — record-only deploy/rollback orchestration."),
    ("runtime.ledger.navigate", "Ledger — append-only hash-chained operation ledger."),
    ("runtime.lineage.inspect", "Lineage — parent-child / ancestry inspection."),
    ("runtime.reversibility.verify", "Reversibility — IP-08 reversibility proof."),
    ("runtime.status.derive", "Status — deterministic derived operation posture."),
    ("runtime.governance.validate", "Governance — compliance evaluation + violations."),
    ("runtime.search.query", "Operation search — authorization + isolation scoped."),
    ("runtime.operations.service", "Runtime — the L8 access + operation decision point."),
)

#: Immutable references to the published runtime-operations contracts (name + version).
RUNTIME_OPERATIONS_CONTRACTS: tuple[ContractRef, ...] = tuple(
    ContractRef(name, RUNTIME_OPERATIONS_CONTRACT_VERSION)
    for name, _ in _RUNTIME_OPERATIONS_CONTRACT_NAMES
)


def runtime_operations_contract(name: str, description: str = "") -> Contract:
    """Build a versioned runtime-operations :class:`Contract` at the contract version."""
    if not isinstance(name, str) or not name:
        raise RuntimeOperationsContractError("runtime operations contract name is required")
    try:
        return platform_contract(name, RUNTIME_OPERATIONS_CONTRACT_VERSION, description)
    except PlatformContractError as exc:  # pragma: no cover - defensive normalisation
        raise RuntimeOperationsContractError(str(exc), name=name) from exc


def default_runtime_operations_contracts() -> tuple[Contract, ...]:
    """The published runtime-operations contracts as concrete :class:`Contract` objects."""
    return tuple(
        runtime_operations_contract(name, description)
        for name, description in _RUNTIME_OPERATIONS_CONTRACT_NAMES
    )


__all__ = [
    "RUNTIME_OPERATIONS_CONTRACT_VERSION",
    "RUNTIME_OPERATIONS_GROUP",
    "ENGINE_RUNTIME_ASSEMBLE_CONTRACT",
    "ENGINE_RUNTIME_DEPLOY_CONTRACT",
    "RuntimeOperationKind",
    "RuntimeOperationAction",
    "permission_for",
    "all_runtime_operation_actions",
    "action_for_kind",
    "RuntimeOperationMetadata",
    "EMPTY_RUNTIME_OPERATION_METADATA",
    "RuntimeUnitReference",
    "CertificationReference",
    "DeploymentDescriptorView",
    "RollbackDescriptorView",
    "RuntimeOperationRecord",
    "RUNTIME_OPERATIONS_CONTRACTS",
    "runtime_operations_contract",
    "default_runtime_operations_contracts",
]
