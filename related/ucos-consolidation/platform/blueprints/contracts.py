"""EC2-TASK-000097 — Blueprint Contracts (EC2-EPIC-006).

The versioned contract surface for the UCOS Platform **Blueprint Catalog & Management
Runtime** (L3 Application / L6 Knowledge of the Program architecture, §4) plus the
immutable **core vocabulary** every blueprint service speaks. It reuses the certified
EC-1 contract machinery through the Platform Foundation
(:func:`~platform.foundation.contracts.platform_contract`,
:class:`~platform.foundation.contracts.ContractRef`) and binds blueprint authorization
to the **two §3.2 capability groups that already physically exist** in the certified
Identity Layer — :class:`~platform.identity.contracts.CapabilityGroup`
``blueprint-authoring`` (PC-04, matrix index 4) and ``blueprint-catalog`` (PC-05,
matrix index 5). EC2-EPIC-006 introduces **no new capability group, no new authority,
and no new authorization logic** (Determination Finding 1).

Vocabulary:
    * :class:`BlueprintFamily` — the six frozen generation families in the
      non-reversible chain Data → Event → API → Workflow → Service → Application
      (``05-GENERATION`` corpus). The platform *records* this classification; it
      *computes* none (Determination Finding 2, §2.4).
    * :class:`BlueprintStatus` — the lifecycle states a blueprint occupies
      (``draft`` / ``validated`` / ``catalogued`` / ``superseded`` / ``retired``);
      ``retired`` is terminal. An invalid blueprint never enters the catalog.
    * :class:`BlueprintAction` — the governed blueprint verbs, each mapped to the
      ``(CapabilityGroup, Permission)`` it requires.
    * :class:`Blueprint` — an immutable, content-addressed blueprint document handle
      scoped to a parent workspace/project: a stable ``slug`` (its identity within a
      workspace), a display name, its parent ``workspace_id``, an optional
      ``project_id`` (the EPIC-005 project it is associated to by reference), an
      optional ``tenant`` (the isolation boundary, inherited from the workspace), an
      owner subject, a recorded generation ``family``, a status, and metadata.
    * :data:`BLUEPRINT_CONTRACTS` — the published blueprint service contracts consumers
      (EPIC-007 Generation Requests) bind to by reference (PL-05, versioned).

All types are **immutable, typed, deterministic, and serializable**, hold no runtime
state, and hold no secret material (SEC-04).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from platform.blueprints.errors import BlueprintContractError
from platform.blueprints.metadata import EMPTY_METADATA, BlueprintMetadata
from platform.foundation.contracts import (
    Contract,
    ContractRef,
    content_hash,
    platform_contract,
)
from platform.foundation.errors import PlatformContractError
from platform.foundation.identity import Permission
from platform.identity.contracts import CapabilityGroup
from typing import Any

#: The semantic version of the Blueprint Runtime contract surface (AR-03/PL-05).
BLUEPRINT_CONTRACT_VERSION = "1.0.0"

#: The §3.2 capability group authorizing blueprint **authoring** (PC-04; reused).
BLUEPRINT_AUTHORING_GROUP = CapabilityGroup.BLUEPRINT_AUTHORING

#: The §3.2 capability group authorizing blueprint **catalog** work (PC-05; reused).
BLUEPRINT_CATALOG_GROUP = CapabilityGroup.BLUEPRINT_CATALOG


class BlueprintFamily(str, Enum):
    """The six frozen ``05-GENERATION`` generation families (recorded, not computed).

    The non-reversible chain Data → Event → API → Workflow → Service → Application
    (Universal Generation Framework Constitution, GEN-000). EC-1 ``Blueprint
    Classification`` (``ENG-CAP-02``) assigns exactly one of these to a blueprint; the
    platform records the result read-only (§2.4, §3.4).
    """

    DATA = "data"
    EVENT = "event"
    API = "api"
    WORKFLOW = "workflow"
    SERVICE = "service"
    APPLICATION = "application"


class BlueprintStatus(str, Enum):
    """The lifecycle states a blueprint occupies (``retired`` is terminal).

    ``draft`` (authored/imported) → ``validated`` (structurally validated + classified
    via EC-1) → ``catalogued`` (immutably versioned, discoverable in the L6 catalog) →
    ``superseded`` (a later version supersedes it) / ``retired`` (terminal). Invalid
    blueprints never enter the catalog — they are refused with the EC-1 gap report.
    """

    DRAFT = "draft"
    VALIDATED = "validated"
    CATALOGUED = "catalogued"
    SUPERSEDED = "superseded"
    RETIRED = "retired"


class BlueprintAction(str, Enum):
    """The governed blueprint verbs (each mapped to a required group + permission)."""

    AUTHOR = "author"
    INSPECT = "inspect"
    DISCOVER = "discover"
    SEARCH = "search"
    CLASSIFY = "classify"
    VALIDATE = "validate"
    VERSION = "version"
    CATALOG = "catalog"
    RETIRE = "retire"
    ASSOCIATE = "associate"
    DISSOCIATE = "dissociate"
    TRACE = "trace"


#: The verb→(capability group, permission) map (Determination §3.3, §13.1). Authoring
#: verbs (author/classify/validate/version) authorize on ``blueprint-authoring``;
#: catalog verbs (catalog/retire/associate/dissociate + all reads) authorize on
#: ``blueprint-catalog``. Reads require READ; creation/mutation require CREATE.
_ACTION_AUTHORITY: dict[BlueprintAction, tuple[CapabilityGroup, Permission]] = {
    BlueprintAction.AUTHOR: (BLUEPRINT_AUTHORING_GROUP, Permission.CREATE),
    BlueprintAction.CLASSIFY: (BLUEPRINT_AUTHORING_GROUP, Permission.CREATE),
    BlueprintAction.VALIDATE: (BLUEPRINT_AUTHORING_GROUP, Permission.CREATE),
    BlueprintAction.VERSION: (BLUEPRINT_AUTHORING_GROUP, Permission.CREATE),
    BlueprintAction.INSPECT: (BLUEPRINT_CATALOG_GROUP, Permission.READ),
    BlueprintAction.DISCOVER: (BLUEPRINT_CATALOG_GROUP, Permission.READ),
    BlueprintAction.SEARCH: (BLUEPRINT_CATALOG_GROUP, Permission.READ),
    BlueprintAction.TRACE: (BLUEPRINT_CATALOG_GROUP, Permission.READ),
    BlueprintAction.CATALOG: (BLUEPRINT_CATALOG_GROUP, Permission.CREATE),
    BlueprintAction.RETIRE: (BLUEPRINT_CATALOG_GROUP, Permission.CREATE),
    BlueprintAction.ASSOCIATE: (BLUEPRINT_CATALOG_GROUP, Permission.CREATE),
    BlueprintAction.DISSOCIATE: (BLUEPRINT_CATALOG_GROUP, Permission.CREATE),
}

#: The blueprint actions that mutate runtime state (require ownership or administrator).
MUTATING_ACTIONS: frozenset[BlueprintAction] = frozenset(
    {
        BlueprintAction.AUTHOR,
        BlueprintAction.CLASSIFY,
        BlueprintAction.VALIDATE,
        BlueprintAction.VERSION,
        BlueprintAction.CATALOG,
        BlueprintAction.RETIRE,
        BlueprintAction.ASSOCIATE,
        BlueprintAction.DISSOCIATE,
    }
)


def authority_for(action: BlueprintAction) -> tuple[CapabilityGroup, Permission]:
    """Return the ``(CapabilityGroup, Permission)`` a blueprint action requires (fail-closed)."""
    if not isinstance(action, BlueprintAction):
        raise BlueprintContractError("action must be a BlueprintAction")
    return _ACTION_AUTHORITY[action]


def group_for(action: BlueprintAction) -> CapabilityGroup:
    """Return the capability group a blueprint action authorizes against (fail-closed)."""
    return authority_for(action)[0]


def permission_for(action: BlueprintAction) -> Permission:
    """Return the RBAC permission required by a blueprint action (fail-closed)."""
    return authority_for(action)[1]


def all_blueprint_families() -> tuple[BlueprintFamily, ...]:
    """Return every generation family in stable declaration order."""
    return tuple(BlueprintFamily)


def all_blueprint_statuses() -> tuple[BlueprintStatus, ...]:
    """Return every blueprint status in stable declaration order."""
    return tuple(BlueprintStatus)


def all_blueprint_actions() -> tuple[BlueprintAction, ...]:
    """Return every blueprint action in stable declaration order."""
    return tuple(BlueprintAction)


def _require_slug(slug: str) -> str:
    if not isinstance(slug, str) or not slug:
        raise BlueprintContractError("blueprint slug is required")
    normalized = slug.strip().lower()
    if not normalized or any(c.isspace() for c in normalized):
        raise BlueprintContractError("blueprint slug must be non-empty and whitespace-free")
    return normalized


@dataclass(frozen=True, slots=True)
class Blueprint:
    """An immutable, content-addressed blueprint document handle scoped to a workspace.

    A blueprint's identity is its ``slug`` within its parent ``workspace_id`` — the
    ``blueprint_id`` is content-addressed from exactly those two fields so registration
    is idempotent and reproducible; mutable facets (family, status, metadata,
    project_id) never change the id. The ``tenant`` is inherited from the parent
    workspace at creation and is the blueprint's isolation boundary (reused workspace
    isolation rule, P3). The recorded ``family`` is the EC-1 classification the
    platform records read-only.
    """

    blueprint_id: str
    slug: str
    name: str
    workspace_id: str
    project_id: str | None
    tenant: str | None
    owner_subject: str
    family: BlueprintFamily
    status: BlueprintStatus
    metadata: BlueprintMetadata

    @classmethod
    def create(
        cls,
        slug: str,
        name: str,
        workspace_id: str,
        owner_subject: str,
        family: BlueprintFamily,
        *,
        project_id: str | None = None,
        tenant: str | None = None,
        status: BlueprintStatus = BlueprintStatus.DRAFT,
        metadata: BlueprintMetadata | None = None,
    ) -> Blueprint:
        """Build a blueprint with a deterministic, content-addressed ``blueprint_id``."""
        normalized_slug = _require_slug(slug)
        if not isinstance(name, str) or not name:
            raise BlueprintContractError("blueprint name is required", slug=normalized_slug)
        if not isinstance(workspace_id, str) or not workspace_id:
            raise BlueprintContractError("blueprint requires a workspace_id", slug=normalized_slug)
        if not isinstance(owner_subject, str) or not owner_subject:
            raise BlueprintContractError(
                "blueprint owner_subject is required", slug=normalized_slug
            )
        if not isinstance(family, BlueprintFamily):
            raise BlueprintContractError("blueprint family must be a BlueprintFamily")
        if not isinstance(status, BlueprintStatus):
            raise BlueprintContractError("blueprint status must be a BlueprintStatus")
        if project_id is not None and (not isinstance(project_id, str) or not project_id):
            raise BlueprintContractError(
                "blueprint project_id must be a non-empty string when provided",
                slug=normalized_slug,
            )
        md = metadata if metadata is not None else EMPTY_METADATA
        if not isinstance(md, BlueprintMetadata):
            raise BlueprintContractError("blueprint metadata must be a BlueprintMetadata")
        identity = {"slug": normalized_slug, "workspace_id": workspace_id}
        return cls(
            blueprint_id=f"UCOS-BLPR-{content_hash(identity)[:16]}",
            slug=normalized_slug,
            name=name,
            workspace_id=workspace_id,
            project_id=project_id,
            tenant=tenant,
            owner_subject=owner_subject,
            family=family,
            status=status,
            metadata=md,
        )

    def with_status(self, status: BlueprintStatus) -> Blueprint:
        """Return an immutable copy in ``status`` (the id is preserved)."""
        if not isinstance(status, BlueprintStatus):
            raise BlueprintContractError("blueprint status must be a BlueprintStatus")
        return Blueprint(
            blueprint_id=self.blueprint_id,
            slug=self.slug,
            name=self.name,
            workspace_id=self.workspace_id,
            project_id=self.project_id,
            tenant=self.tenant,
            owner_subject=self.owner_subject,
            family=self.family,
            status=status,
            metadata=self.metadata,
        )

    def with_metadata(self, metadata: BlueprintMetadata) -> Blueprint:
        """Return an immutable copy carrying ``metadata`` (the id is preserved)."""
        if not isinstance(metadata, BlueprintMetadata):
            raise BlueprintContractError("blueprint metadata must be a BlueprintMetadata")
        return Blueprint(
            blueprint_id=self.blueprint_id,
            slug=self.slug,
            name=self.name,
            workspace_id=self.workspace_id,
            project_id=self.project_id,
            tenant=self.tenant,
            owner_subject=self.owner_subject,
            family=self.family,
            status=self.status,
            metadata=metadata,
        )

    @property
    def is_catalogued(self) -> bool:
        return self.status is BlueprintStatus.CATALOGUED

    @property
    def is_terminal(self) -> bool:
        """True iff the blueprint is in the terminal RETIRED state."""
        return self.status is BlueprintStatus.RETIRED

    def to_dict(self) -> dict[str, Any]:
        return {
            "blueprint_id": self.blueprint_id,
            "slug": self.slug,
            "name": self.name,
            "workspace_id": self.workspace_id,
            "project_id": self.project_id,
            "tenant": self.tenant,
            "owner_subject": self.owner_subject,
            "family": self.family.value,
            "status": self.status.value,
            "metadata": self.metadata.to_dict(),
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


# --------------------------------------------------------------------------- #
# The published blueprint contract surface (L3/L6).                           #
# --------------------------------------------------------------------------- #

#: The blueprint service contract identities the Blueprint Runtime publishes. Each maps
#: to an EC2-EPIC-006 deliverable; consumers bind to these by reference (PL-05). The
#: ``catalog``/``runtime`` contracts are the binding point EPIC-007 uses.
_BLUEPRINT_CONTRACT_NAMES: tuple[tuple[str, str], ...] = (
    ("blueprints.registry.registry", "Blueprint registry — create/register/resolve/version."),
    ("blueprints.classification.classify", "Classification — record EC-1 family (read-only)."),
    ("blueprints.validation.validate", "Validation — structural validation + gap report."),
    ("blueprints.catalog.index", "Catalog — L6 provenance-carrying read model/index."),
    ("blueprints.provenance.trace", "Provenance — 05-GENERATION → implementation trace (link-4)."),
    ("blueprints.associations.bind", "Associations — bind workspace/project/request/etc. refs."),
    ("blueprints.search.query", "Blueprint search — authorization + isolation scoped discovery."),
    ("blueprints.runtime.service", "Blueprint runtime — the L3 access + context decision point."),
)

#: Immutable references to the published blueprint contracts (name + version).
BLUEPRINT_CONTRACTS: tuple[ContractRef, ...] = tuple(
    ContractRef(name, BLUEPRINT_CONTRACT_VERSION) for name, _ in _BLUEPRINT_CONTRACT_NAMES
)


def blueprint_contract(name: str, description: str = "") -> Contract:
    """Build a versioned blueprint :class:`Contract` at the blueprint contract version."""
    if not isinstance(name, str) or not name:
        raise BlueprintContractError("blueprint contract name is required")
    try:
        return platform_contract(name, BLUEPRINT_CONTRACT_VERSION, description)
    except PlatformContractError as exc:  # pragma: no cover - defensive normalisation
        raise BlueprintContractError(str(exc), name=name) from exc


def default_blueprint_contracts() -> tuple[Contract, ...]:
    """The published blueprint contracts as concrete :class:`Contract` objects."""
    return tuple(
        blueprint_contract(name, description) for name, description in _BLUEPRINT_CONTRACT_NAMES
    )


__all__ = [
    "BLUEPRINT_CONTRACT_VERSION",
    "BLUEPRINT_AUTHORING_GROUP",
    "BLUEPRINT_CATALOG_GROUP",
    "BlueprintFamily",
    "BlueprintStatus",
    "BlueprintAction",
    "MUTATING_ACTIONS",
    "authority_for",
    "group_for",
    "permission_for",
    "all_blueprint_families",
    "all_blueprint_statuses",
    "all_blueprint_actions",
    "Blueprint",
    "BLUEPRINT_CONTRACTS",
    "blueprint_contract",
    "default_blueprint_contracts",
]
