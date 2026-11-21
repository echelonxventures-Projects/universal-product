"""EC2-TASK-000089 — Project Contracts (EC2-EPIC-005).

The versioned contract surface for the UCOS Platform **Project Management Runtime**
(L3 Application of the Program architecture, §4) plus the immutable **core
vocabulary** every project service speaks. It reuses the certified EC-1 contract
machinery through the Platform Foundation
(:func:`~platform.foundation.contracts.platform_contract`,
:class:`~platform.foundation.contracts.ContractRef`) and binds project authorization
to the single §3.2 :class:`~platform.identity.contracts.CapabilityGroup`
``workspace-project-lifecycle`` — the SAME capability group the Workspace Runtime
(EC2-EPIC-004) realized the workspace half of PC-03 against. EC2-EPIC-005 introduces
**no new capability group, no new authority, and no new authorization logic**.

Vocabulary:
    * :class:`ProjectStatus` — the lifecycle states a project occupies (``active`` /
      ``suspended`` / ``completed`` / ``archived``); ``archived`` is terminal.
    * :class:`AssociationKind` — the typed external work references a project may bind
      **by reference** (``blueprint`` / ``request`` / ``artifact``). These are opaque
      references; the runtime resolves/validates no referenced entity (the entities'
      runtimes — EPIC-006/007/009 — do not yet exist; §5.3).
    * :class:`ProjectAction` — the governed project verbs, each mapped to the coarse
      RBAC :class:`~platform.foundation.identity.Permission` it requires.
    * :class:`Project` — an immutable, content-addressed organizational container
      scoped to a parent workspace: a stable ``slug`` (its identity within a
      workspace), a display name, its parent ``workspace_id``, an optional ``tenant``
      (inherited from the workspace — the isolation boundary), an owner subject, a
      status, and metadata.
    * :class:`ProjectAssociation` — an immutable, content-addressed append-only binding
      of a project to a typed external reference.
    * :data:`PROJECT_CONTRACTS` — the published project service contracts consumers
      bind to by reference (PL-05, versioned).

All types are **immutable, typed, deterministic, and serializable**, hold no runtime
state, and hold no secret material (SEC-04).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from platform.foundation.contracts import (
    Contract,
    ContractRef,
    content_hash,
    platform_contract,
)
from platform.foundation.errors import PlatformContractError
from platform.foundation.identity import Permission
from platform.identity.contracts import CapabilityGroup
from platform.projects.errors import ProjectContractError
from platform.projects.metadata import EMPTY_METADATA, ProjectMetadata
from typing import Any

#: The semantic version of the Project Management Runtime contract surface (AR-03/PL-05).
PROJECT_CONTRACT_VERSION = "1.0.0"

#: The §3.2 capability group that authorizes every project action (reused; no new group).
PROJECT_GROUP = CapabilityGroup.WORKSPACE_PROJECT_LIFECYCLE


class ProjectStatus(str, Enum):
    """The lifecycle states a project occupies (``archived`` is terminal)."""

    ACTIVE = "active"
    SUSPENDED = "suspended"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class AssociationKind(str, Enum):
    """The typed external work references a project may bind **by reference**.

    Published for downstream consumption: EPIC-006 (Blueprint Catalog) binds via
    ``BLUEPRINT``, EPIC-007 (Generation Requests) via ``REQUEST``, and EPIC-009
    (Artifact Explorer) via ``ARTIFACT``. The Project Management Runtime treats each
    ``ref_id`` as opaque and resolves/validates no referenced entity (§5.3).
    """

    BLUEPRINT = "blueprint"
    REQUEST = "request"
    ARTIFACT = "artifact"


class ProjectAction(str, Enum):
    """The governed project verbs (each mapped to a required RBAC permission)."""

    CREATE_PROJECT = "create-project"
    INSPECT = "inspect"
    DISCOVER = "discover"
    SEARCH = "search"
    TRANSITION_LIFECYCLE = "transition-lifecycle"
    ADD_ASSOCIATION = "add-association"
    REMOVE_ASSOCIATION = "remove-association"


#: The verb→permission map (Determination §9). Read verbs require READ; project
#: creation and every mutation (lifecycle transition, association add/remove) require
#: CREATE for the owning create/read roles — Platform Administrator additionally holds
#: ADMINISTER, which the service accepts in lieu of ownership for mutations.
_ACTION_PERMISSIONS: dict[ProjectAction, Permission] = {
    ProjectAction.CREATE_PROJECT: Permission.CREATE,
    ProjectAction.INSPECT: Permission.READ,
    ProjectAction.DISCOVER: Permission.READ,
    ProjectAction.SEARCH: Permission.READ,
    ProjectAction.TRANSITION_LIFECYCLE: Permission.CREATE,
    ProjectAction.ADD_ASSOCIATION: Permission.CREATE,
    ProjectAction.REMOVE_ASSOCIATION: Permission.CREATE,
}

#: The project actions that mutate runtime state (require ownership or administrator).
MUTATING_ACTIONS: frozenset[ProjectAction] = frozenset(
    {
        ProjectAction.CREATE_PROJECT,
        ProjectAction.TRANSITION_LIFECYCLE,
        ProjectAction.ADD_ASSOCIATION,
        ProjectAction.REMOVE_ASSOCIATION,
    }
)


def permission_for(action: ProjectAction) -> Permission:
    """Return the RBAC permission required by a project action (fail-closed)."""
    if not isinstance(action, ProjectAction):
        raise ProjectContractError("action must be a ProjectAction")
    return _ACTION_PERMISSIONS[action]


def all_project_statuses() -> tuple[ProjectStatus, ...]:
    """Return every project status in stable declaration order."""
    return tuple(ProjectStatus)


def all_association_kinds() -> tuple[AssociationKind, ...]:
    """Return every association kind in stable declaration order."""
    return tuple(AssociationKind)


def all_project_actions() -> tuple[ProjectAction, ...]:
    """Return every project action in stable declaration order."""
    return tuple(ProjectAction)


def _require_slug(slug: str) -> str:
    if not isinstance(slug, str) or not slug:
        raise ProjectContractError("project slug is required")
    normalized = slug.strip().lower()
    if not normalized or any(c.isspace() for c in normalized):
        raise ProjectContractError("project slug must be non-empty and whitespace-free")
    return normalized


@dataclass(frozen=True, slots=True)
class Project:
    """An immutable, content-addressed project container scoped to a workspace.

    A project's identity is its ``slug`` within its parent ``workspace_id`` — the
    ``project_id`` is content-addressed from exactly those two fields so registration
    is idempotent and reproducible; mutable facets (status, metadata) never change the
    id. The ``tenant`` is inherited from the parent workspace at creation and is the
    project's isolation boundary (reused workspace isolation rule, P3).
    """

    project_id: str
    slug: str
    name: str
    workspace_id: str
    tenant: str | None
    owner_subject: str
    status: ProjectStatus
    metadata: ProjectMetadata

    @classmethod
    def create(
        cls,
        slug: str,
        name: str,
        workspace_id: str,
        owner_subject: str,
        *,
        tenant: str | None = None,
        status: ProjectStatus = ProjectStatus.ACTIVE,
        metadata: ProjectMetadata | None = None,
    ) -> Project:
        """Build a project with a deterministic, content-addressed ``project_id``."""
        normalized_slug = _require_slug(slug)
        if not isinstance(name, str) or not name:
            raise ProjectContractError("project name is required", slug=normalized_slug)
        if not isinstance(workspace_id, str) or not workspace_id:
            raise ProjectContractError("project requires a workspace_id", slug=normalized_slug)
        if not isinstance(owner_subject, str) or not owner_subject:
            raise ProjectContractError("project owner_subject is required", slug=normalized_slug)
        if not isinstance(status, ProjectStatus):
            raise ProjectContractError("project status must be a ProjectStatus")
        md = metadata if metadata is not None else EMPTY_METADATA
        if not isinstance(md, ProjectMetadata):
            raise ProjectContractError("project metadata must be a ProjectMetadata")
        identity = {"slug": normalized_slug, "workspace_id": workspace_id}
        return cls(
            project_id=f"UCOS-PROJ-{content_hash(identity)[:16]}",
            slug=normalized_slug,
            name=name,
            workspace_id=workspace_id,
            tenant=tenant,
            owner_subject=owner_subject,
            status=status,
            metadata=md,
        )

    def with_status(self, status: ProjectStatus) -> Project:
        """Return an immutable copy in ``status`` (the id is preserved)."""
        if not isinstance(status, ProjectStatus):
            raise ProjectContractError("project status must be a ProjectStatus")
        return Project(
            project_id=self.project_id,
            slug=self.slug,
            name=self.name,
            workspace_id=self.workspace_id,
            tenant=self.tenant,
            owner_subject=self.owner_subject,
            status=status,
            metadata=self.metadata,
        )

    def with_metadata(self, metadata: ProjectMetadata) -> Project:
        """Return an immutable copy carrying ``metadata`` (the id is preserved)."""
        if not isinstance(metadata, ProjectMetadata):
            raise ProjectContractError("project metadata must be a ProjectMetadata")
        return Project(
            project_id=self.project_id,
            slug=self.slug,
            name=self.name,
            workspace_id=self.workspace_id,
            tenant=self.tenant,
            owner_subject=self.owner_subject,
            status=self.status,
            metadata=metadata,
        )

    @property
    def is_active(self) -> bool:
        return self.status is ProjectStatus.ACTIVE

    @property
    def is_terminal(self) -> bool:
        """True iff the project is in the terminal ARCHIVED state."""
        return self.status is ProjectStatus.ARCHIVED

    def to_dict(self) -> dict[str, Any]:
        return {
            "project_id": self.project_id,
            "slug": self.slug,
            "name": self.name,
            "workspace_id": self.workspace_id,
            "tenant": self.tenant,
            "owner_subject": self.owner_subject,
            "status": self.status.value,
            "metadata": self.metadata.to_dict(),
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


@dataclass(frozen=True, slots=True)
class ProjectAssociation:
    """An immutable, content-addressed binding of a project to a typed external reference.

    The ``association_id`` is content-addressed from ``{project_id, kind, ref_id}`` so
    an identical binding always yields the same id (idempotency key) and the same
    reference can never be rebound across projects to the same id (no cross-project
    leakage). The ``ref_id`` is opaque — the runtime resolves nothing.
    """

    association_id: str
    project_id: str
    kind: AssociationKind
    ref_id: str

    @classmethod
    def create(cls, project_id: str, kind: AssociationKind, ref_id: str) -> ProjectAssociation:
        """Build an association with a deterministic, content-addressed id."""
        if not isinstance(project_id, str) or not project_id:
            raise ProjectContractError("association requires a project_id")
        if not isinstance(kind, AssociationKind):
            raise ProjectContractError("association kind must be an AssociationKind")
        if not isinstance(ref_id, str) or not ref_id:
            raise ProjectContractError("association requires a ref_id", project_id=project_id)
        key = {"project_id": project_id, "kind": kind.value, "ref_id": ref_id}
        return cls(
            association_id=f"UCOS-PASC-{content_hash(key)[:16]}",
            project_id=project_id,
            kind=kind,
            ref_id=ref_id,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "association_id": self.association_id,
            "project_id": self.project_id,
            "kind": self.kind.value,
            "ref_id": self.ref_id,
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


# --------------------------------------------------------------------------- #
# The published project contract surface (L3).                                #
# --------------------------------------------------------------------------- #

#: The project service contract identities the Project Management Runtime publishes.
#: Each maps to an EC2-EPIC-005 deliverable; consumers bind to these by reference
#: (PL-05). The ``associations`` contract is the binding point EPIC-006/007/009 use.
_PROJECT_CONTRACT_NAMES: tuple[tuple[str, str], ...] = (
    ("projects.registry.registry", "Project registry — create/register/resolve/discover."),
    ("projects.lifecycle.transition", "Lifecycle — deterministic project state machine."),
    ("projects.associations.bind", "Associations — bind blueprint/request/artifact refs."),
    ("projects.status.derive", "Status — deterministic derived project status."),
    ("projects.search.query", "Project search — authorization + isolation scoped discovery."),
    ("projects.runtime.service", "Project runtime — the L3 access + context decision point."),
)

#: Immutable references to the published project contracts (name + version).
PROJECT_CONTRACTS: tuple[ContractRef, ...] = tuple(
    ContractRef(name, PROJECT_CONTRACT_VERSION) for name, _ in _PROJECT_CONTRACT_NAMES
)


def project_contract(name: str, description: str = "") -> Contract:
    """Build a versioned project :class:`Contract` at the project contract version."""
    if not isinstance(name, str) or not name:
        raise ProjectContractError("project contract name is required")
    try:
        return platform_contract(name, PROJECT_CONTRACT_VERSION, description)
    except PlatformContractError as exc:  # pragma: no cover - defensive normalisation
        raise ProjectContractError(str(exc), name=name) from exc


def default_project_contracts() -> tuple[Contract, ...]:
    """The published project contracts as concrete :class:`Contract` objects."""
    return tuple(
        project_contract(name, description) for name, description in _PROJECT_CONTRACT_NAMES
    )


__all__ = [
    "PROJECT_CONTRACT_VERSION",
    "PROJECT_GROUP",
    "ProjectStatus",
    "AssociationKind",
    "ProjectAction",
    "MUTATING_ACTIONS",
    "permission_for",
    "all_project_statuses",
    "all_association_kinds",
    "all_project_actions",
    "Project",
    "ProjectAssociation",
    "PROJECT_CONTRACTS",
    "project_contract",
    "default_project_contracts",
]
