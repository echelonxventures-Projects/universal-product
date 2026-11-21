"""EC2-TASK-000106 — Blueprint Service (EC2-EPIC-006).

The single, governed **blueprint runtime composition point** (L3 Application / L6
Knowledge of the Program architecture) that composes the whole Blueprint Catalog &
Management Runtime into one entry point — the realization of Program Surface #7
(PC-04 authoring & validation + PC-05 catalog):

    BlueprintRegistry · ClassificationLedger · ProvenanceLedger ·
    BlueprintAssociationRegistry · BlueprintCatalog · BlueprintSearch ·
    BlueprintHealth · (reused) AuthorizationService · WorkspaceRegistry ·
    ObservabilityService

It is a strictly **additive** layer: it authorizes only through the certified Identity
Layer (L7) on the two existing ``blueprint-authoring`` / ``blueprint-catalog``
capability groups — **no duplicate authorization or identity logic, no new authority,
no new capability group** — classifies/validates only through the read-only L4 EC-1
façade (records the result, computes none), observes only through the Observability
Layer (L8), reuses the Foundation registries/events (L4/L6), and binds each blueprint
to a parent workspace through the certified Workspace Runtime (L3) **by reference**. It
re-implements none of them, modifies neither EC-1 nor any prior layer, and writes
nothing to the certified corpus (DP-03).

Every blueprint access is fail-closed and composes gates — **identity authorization**
(RBAC §3.2), **tenant/workspace isolation** (the reused rule, P3), and — for mutating
actions — **owner/administrator scoping** — so cross-tenant access is refused in 100%
of cases. Because every governed action is published onto the Foundation event bus, it
is captured by observability as append-only audit (PC-16 / OP-C3). The runtime
discharges GOV-002 **link-4**: cataloging requires a provenance-by-reference record, so
every cataloged blueprint is a materialized ``05-GENERATION → 06-IMPLEMENTATION`` trace
edge (§5.5).

The service is deterministic: the same identity registrations, workspaces, blueprints,
classifications, versions, provenance, associations, and ordered sequence of calls
yield the same :class:`BlueprintEvidence` fingerprint (P5). :func:`build_blueprint_service`
provides the default wiring; :func:`~platform.blueprints.bootstrap.bootstrap_blueprints`
composes it onto a :class:`~platform.foundation.bootstrap.PlatformContext`.
"""

from __future__ import annotations

from dataclasses import dataclass
from platform.blueprints.associations import (
    BlueprintAssociation,
    BlueprintAssociationKind,
    BlueprintAssociationRegistry,
)
from platform.blueprints.catalog import BlueprintCatalog, CatalogEntry
from platform.blueprints.classification import (
    BlueprintClassification,
    ClassificationLedger,
    classify,
)
from platform.blueprints.context import BlueprintContext
from platform.blueprints.contracts import (
    MUTATING_ACTIONS,
    Blueprint,
    BlueprintAction,
    BlueprintFamily,
    BlueprintStatus,
    authority_for,
)
from platform.blueprints.errors import (
    BlueprintAccessError,
    BlueprintProvenanceError,
    BlueprintServiceError,
)
from platform.blueprints.health import BlueprintHealth, blueprint_health_checks
from platform.blueprints.metadata import BlueprintMetadata
from platform.blueprints.provenance import BlueprintProvenance, ProvenanceLedger
from platform.blueprints.registry import BlueprintRegistry
from platform.blueprints.search import BlueprintSearch, BlueprintSearchResponse
from platform.blueprints.status import DerivedBlueprintStatus, derive_status
from platform.blueprints.validation import ValidationResult, require_valid
from platform.blueprints.versioning import BlueprintVersion
from platform.foundation.contracts import content_hash
from platform.foundation.events import EventBus
from platform.foundation.identity import Permission
from platform.identity.contracts import AccessDecision
from platform.identity.errors import IdentityError
from platform.identity.service import AuthorizationService
from platform.observability.health import HealthRegistry
from platform.observability.service import ObservabilityService
from platform.workspace.isolation import tenants_isolated
from platform.workspace.registration import WorkspaceRegistry
from typing import Any

#: Governed events published onto the Foundation event bus (observed as PC-16).
BLUEPRINT_AUTHORED_EVENT = "blueprint.authored"
BLUEPRINT_CLASSIFIED_EVENT = "blueprint.classified"
BLUEPRINT_VALIDATED_EVENT = "blueprint.validated"
BLUEPRINT_VERSIONED_EVENT = "blueprint.versioned"
BLUEPRINT_CATALOGUED_EVENT = "blueprint.catalogued"
BLUEPRINT_SUPERSEDED_EVENT = "blueprint.superseded"
BLUEPRINT_RETIRED_EVENT = "blueprint.retired"
BLUEPRINT_METADATA_UPDATED_EVENT = "blueprint.metadata.updated"
BLUEPRINT_ASSOCIATION_ADDED_EVENT = "blueprint.association.added"
BLUEPRINT_ASSOCIATION_REMOVED_EVENT = "blueprint.association.removed"
BLUEPRINT_TRACEABILITY_LINKED_EVENT = "blueprint.traceability.linked"
BLUEPRINT_HEALTH_CHANGED_EVENT = "blueprint.health.changed"
BLUEPRINT_ACCESS_EVENT = "blueprint.access.evaluated"

#: The stable subject used for runtime-scoped (non-blueprint) governed events.
_RUNTIME_SUBJECT = "platform.blueprints.runtime"


@dataclass(frozen=True, slots=True)
class BlueprintAccess:
    """An immutable, content-addressed blueprint access decision (fail-closed).

    Composes identity authorization, tenant/workspace isolation, and (for mutating
    actions) owner/administrator scoping into a single verdict for one
    ``(principal, blueprint, action)`` request.
    """

    blueprint_id: str
    principal_id: str
    action: BlueprintAction
    permission: Permission
    granted: bool
    reason: str
    is_owner: bool
    decision: AccessDecision
    access_id: str = ""

    @classmethod
    def create(
        cls,
        *,
        blueprint_id: str,
        action: BlueprintAction,
        permission: Permission,
        granted: bool,
        reason: str,
        decision: AccessDecision,
        is_owner: bool = False,
    ) -> BlueprintAccess:
        principal_id = decision.request.principal_id
        core = {
            "blueprint_id": blueprint_id,
            "principal_id": principal_id,
            "action": action.value,
            "permission": permission.value,
            "granted": granted,
            "reason": reason,
            "is_owner": is_owner,
        }
        return cls(
            blueprint_id=blueprint_id,
            principal_id=principal_id,
            action=action,
            permission=permission,
            granted=granted,
            reason=reason,
            is_owner=is_owner,
            decision=decision,
            access_id=f"UCOS-BACC-{content_hash(core)[:16]}",
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "access_id": self.access_id,
            "blueprint_id": self.blueprint_id,
            "principal_id": self.principal_id,
            "action": self.action.value,
            "permission": self.permission.value,
            "granted": self.granted,
            "reason": self.reason,
            "is_owner": self.is_owner,
            "decision": self.decision.to_dict(),
        }


@dataclass(frozen=True, slots=True)
class BlueprintEvidence:
    """A deterministic, content-addressed record of blueprint runtime state (evidence)."""

    registry_fingerprint: str
    classifications_fingerprint: str
    provenance_fingerprint: str
    associations_fingerprint: str
    catalog_fingerprint: str
    blueprint_count: int
    catalogued_count: int
    provenance_count: int
    association_count: int
    access_evaluation_count: int
    health_status: str
    evidence_id: str = ""

    @classmethod
    def create(
        cls,
        *,
        registry_fingerprint: str,
        classifications_fingerprint: str,
        provenance_fingerprint: str,
        associations_fingerprint: str,
        catalog_fingerprint: str,
        blueprint_count: int,
        catalogued_count: int,
        provenance_count: int,
        association_count: int,
        access_evaluation_count: int,
        health_status: str,
    ) -> BlueprintEvidence:
        core = {
            "registry_fingerprint": registry_fingerprint,
            "classifications_fingerprint": classifications_fingerprint,
            "provenance_fingerprint": provenance_fingerprint,
            "associations_fingerprint": associations_fingerprint,
            "catalog_fingerprint": catalog_fingerprint,
            "blueprint_count": blueprint_count,
            "catalogued_count": catalogued_count,
            "provenance_count": provenance_count,
            "association_count": association_count,
            "access_evaluation_count": access_evaluation_count,
            "health_status": health_status,
        }
        return cls(
            registry_fingerprint=registry_fingerprint,
            classifications_fingerprint=classifications_fingerprint,
            provenance_fingerprint=provenance_fingerprint,
            associations_fingerprint=associations_fingerprint,
            catalog_fingerprint=catalog_fingerprint,
            blueprint_count=blueprint_count,
            catalogued_count=catalogued_count,
            provenance_count=provenance_count,
            association_count=association_count,
            access_evaluation_count=access_evaluation_count,
            health_status=health_status,
            evidence_id=f"UCOS-BEVT-{content_hash(core)[:16]}",
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "registry_fingerprint": self.registry_fingerprint,
            "classifications_fingerprint": self.classifications_fingerprint,
            "provenance_fingerprint": self.provenance_fingerprint,
            "associations_fingerprint": self.associations_fingerprint,
            "catalog_fingerprint": self.catalog_fingerprint,
            "blueprint_count": self.blueprint_count,
            "catalogued_count": self.catalogued_count,
            "provenance_count": self.provenance_count,
            "association_count": self.association_count,
            "access_evaluation_count": self.access_evaluation_count,
            "health_status": self.health_status,
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


class BlueprintService:
    """The governed L3/L6 composition point for the UCOS Blueprint Catalog & Management Runtime."""

    __slots__ = (
        "_registry",
        "_classifications",
        "_provenance",
        "_associations",
        "_catalog",
        "_authorization",
        "_workspaces",
        "_search",
        "_health",
        "_health_registry",
        "_observability",
        "_events",
        "_access_evaluations",
        "_last_health_status",
    )

    def __init__(
        self,
        *,
        registry: BlueprintRegistry,
        classifications: ClassificationLedger,
        provenance: ProvenanceLedger,
        associations: BlueprintAssociationRegistry,
        catalog: BlueprintCatalog,
        authorization: AuthorizationService,
        workspaces: WorkspaceRegistry,
        search: BlueprintSearch,
        health: BlueprintHealth,
        health_registry: HealthRegistry,
        observability: ObservabilityService | None = None,
        events: EventBus | None = None,
    ) -> None:
        if not isinstance(registry, BlueprintRegistry):
            raise BlueprintServiceError("a valid BlueprintRegistry is required")
        if not isinstance(classifications, ClassificationLedger):
            raise BlueprintServiceError("a valid ClassificationLedger is required")
        if not isinstance(provenance, ProvenanceLedger):
            raise BlueprintServiceError("a valid ProvenanceLedger is required")
        if not isinstance(associations, BlueprintAssociationRegistry):
            raise BlueprintServiceError("a valid BlueprintAssociationRegistry is required")
        if not isinstance(catalog, BlueprintCatalog):
            raise BlueprintServiceError("a valid BlueprintCatalog is required")
        if not isinstance(authorization, AuthorizationService):
            raise BlueprintServiceError("a valid AuthorizationService is required")
        if not isinstance(workspaces, WorkspaceRegistry):
            raise BlueprintServiceError("a valid WorkspaceRegistry is required")
        if not isinstance(search, BlueprintSearch):
            raise BlueprintServiceError("a valid BlueprintSearch is required")
        if not isinstance(health, BlueprintHealth):
            raise BlueprintServiceError("a valid BlueprintHealth is required")
        if not isinstance(health_registry, HealthRegistry):
            raise BlueprintServiceError("a valid HealthRegistry is required")
        if observability is not None and not isinstance(observability, ObservabilityService):
            raise BlueprintServiceError(
                "observability must be an ObservabilityService when provided"
            )
        if events is not None and not isinstance(events, EventBus):
            raise BlueprintServiceError("events must be an EventBus when provided")
        self._registry = registry
        self._classifications = classifications
        self._provenance = provenance
        self._associations = associations
        self._catalog = catalog
        self._authorization = authorization
        self._workspaces = workspaces
        self._search = search
        self._health = health
        self._health_registry = health_registry
        self._observability = observability
        self._events = events
        self._access_evaluations = 0
        self._last_health_status = self._current_health_status()

    # -- component access -------------------------------------------------------

    @property
    def registry(self) -> BlueprintRegistry:
        return self._registry

    @property
    def classifications(self) -> ClassificationLedger:
        return self._classifications

    @property
    def provenance(self) -> ProvenanceLedger:
        return self._provenance

    @property
    def associations(self) -> BlueprintAssociationRegistry:
        return self._associations

    @property
    def catalog(self) -> BlueprintCatalog:
        return self._catalog

    @property
    def authorization(self) -> AuthorizationService:
        return self._authorization

    @property
    def workspaces(self) -> WorkspaceRegistry:
        return self._workspaces

    @property
    def health(self) -> BlueprintHealth:
        return self._health

    @property
    def observability(self) -> ObservabilityService | None:
        return self._observability

    @property
    def access_evaluation_count(self) -> int:
        return self._access_evaluations

    # -- authoring --------------------------------------------------------------

    def author_blueprint(
        self,
        session_id: str,
        slug: str,
        name: str,
        workspace_id: str,
        family: BlueprintFamily,
        *,
        now: int,
        project_id: str | None = None,
        metadata: BlueprintMetadata | None = None,
    ) -> Blueprint:
        """Author (or import) a blueprint scoped to a workspace; record the author as owner.

        Requires identity CREATE on ``blueprint-authoring`` (with the parent workspace's
        tenant), an ACTIVE parent workspace, and cross-tenant isolation clearance. Raises
        :class:`BlueprintAccessError` on any denial. The blueprint enters in DRAFT.
        """
        workspace = self._workspaces.get(workspace_id)
        if not workspace.is_active:
            raise BlueprintAccessError(
                "parent workspace is not active",
                reason=f"workspace-{workspace.status.value}",
                workspace_id=workspace_id,
            )
        group, permission = authority_for(BlueprintAction.AUTHOR)
        decision = self._authorization.authorize(
            session_id, group, permission, now=now, tenant=workspace.tenant, resource=slug
        )
        if not decision.permitted:
            raise BlueprintAccessError(
                "blueprint authoring denied", reason=decision.reason, slug=slug
            )
        principal = self._authorization.principals.get(decision.request.principal_id)
        if tenants_isolated(principal.tenant, workspace.tenant):
            raise BlueprintAccessError(
                "cross-tenant blueprint authoring denied",
                reason="tenant-isolation-violation",
                slug=slug,
            )
        blueprint = self._registry.create(
            slug,
            name,
            workspace_id,
            principal.subject,
            family,
            project_id=project_id,
            tenant=workspace.tenant,
            metadata=metadata,
        )
        self._emit(
            BLUEPRINT_AUTHORED_EVENT,
            subject=blueprint.blueprint_id,
            payload={
                "slug": blueprint.slug,
                "workspace_id": workspace_id,
                "project_id": project_id,
                "family": family.value,
                "tenant": blueprint.tenant,
            },
        )
        return blueprint

    # -- classification (EC-1 façade, read-only) --------------------------------

    def classify(
        self,
        session_id: str,
        blueprint_id: str,
        family: BlueprintFamily,
        *,
        now: int,
        resolved: bool = True,
        defects: tuple[str, ...] | None = None,
    ) -> BlueprintClassification:
        """Record an EC-1 classification result for a blueprint (read-only façade).

        Requires CLASSIFY authority. The EC-1 result (``resolved`` + ``family`` +
        ``defects``) is supplied by the caller (the engine output consumed read-only);
        the platform records it — it computes no classification (P10).
        """
        self._require_access(session_id, blueprint_id, BlueprintAction.CLASSIFY, now=now)
        classification = classify(blueprint_id, family, resolved=resolved, defects=defects)
        self._classifications.record(classification)
        self._emit(
            BLUEPRINT_CLASSIFIED_EVENT,
            subject=blueprint_id,
            payload={
                "family": family.value,
                "valid": classification.valid,
                "defects": list(classification.defects),
            },
        )
        return classification

    # -- validation -------------------------------------------------------------

    def validate(self, session_id: str, blueprint_id: str, *, now: int) -> ValidationResult:
        """Structurally validate a blueprint via its recorded EC-1 classification.

        Requires VALIDATE authority. Valid ⇒ transition DRAFT → VALIDATED. Invalid ⇒
        refused with the EC-1 gap report (:class:`BlueprintValidationError`); the
        blueprint stays out of the catalog (fail-closed, P4).
        """
        self._require_access(session_id, blueprint_id, BlueprintAction.VALIDATE, now=now)
        classification = self._classifications.get(blueprint_id)
        result = require_valid(classification)  # raises with gap report if invalid
        self._registry.transition(blueprint_id, BlueprintStatus.VALIDATED, tick=now)
        self._emit(
            BLUEPRINT_VALIDATED_EVENT,
            subject=blueprint_id,
            payload={"family": result.family.value, "valid": True},
        )
        return result

    # -- cataloging (link-4 trace closure) --------------------------------------

    def catalog_blueprint(
        self, session_id: str, blueprint_id: str, provenance: BlueprintProvenance, *, now: int
    ) -> CatalogEntry:
        """Publish a VALIDATED blueprint into the L6 catalog with link-4 provenance.

        Requires CATALOG authority. The ``provenance`` (provenance-by-reference to the
        ``05-GENERATION`` origin) is **mandatory** — a cataloged blueprint without it is
        not admissible (§10). Recording it discharges GOV-002 link-4: the catalog entry
        becomes a materialized ``05-GENERATION → 06-IMPLEMENTATION`` trace edge.
        """
        self._require_access(session_id, blueprint_id, BlueprintAction.CATALOG, now=now)
        if not isinstance(provenance, BlueprintProvenance):
            raise BlueprintServiceError("cataloging requires a BlueprintProvenance")
        if provenance.blueprint_ref != blueprint_id:
            raise BlueprintProvenanceError(
                "provenance blueprint_ref does not match the blueprint being cataloged",
                blueprint_ref=provenance.blueprint_ref,
                blueprint_id=blueprint_id,
            )
        self._provenance.record(provenance)
        self._registry.transition(blueprint_id, BlueprintStatus.CATALOGUED, tick=now)
        self._emit(
            BLUEPRINT_CATALOGUED_EVENT,
            subject=blueprint_id,
            payload={"provenance_id": provenance.provenance_id},
        )
        self._emit(
            BLUEPRINT_TRACEABILITY_LINKED_EVENT,
            subject=blueprint_id,
            payload=provenance.trace_edge(),
        )
        self._emit_health_change()
        return self._catalog.entry(blueprint_id)

    # -- versioning -------------------------------------------------------------

    def version(
        self,
        session_id: str,
        blueprint_id: str,
        content_hash: str,
        *,
        now: int,
        metadata: BlueprintMetadata | None = None,
    ) -> BlueprintVersion:
        """Append an immutable content-addressed version to a blueprint (requires VERSION)."""
        self._require_access(session_id, blueprint_id, BlueprintAction.VERSION, now=now)
        version = self._registry.add_version(blueprint_id, content_hash, metadata=metadata)
        self._emit(
            BLUEPRINT_VERSIONED_EVENT,
            subject=blueprint_id,
            payload={
                "version_id": version.version_id,
                "revision": version.revision,
                "content_hash": version.content_hash,
            },
        )
        return version

    def supersede(self, session_id: str, blueprint_id: str, *, now: int) -> Blueprint:
        """Mark a CATALOGUED blueprint superseded (requires CATALOG authority)."""
        self._require_access(session_id, blueprint_id, BlueprintAction.CATALOG, now=now)
        updated = self._registry.transition(blueprint_id, BlueprintStatus.SUPERSEDED, tick=now)
        self._emit(BLUEPRINT_SUPERSEDED_EVENT, subject=blueprint_id, payload={})
        return updated

    def retire(self, session_id: str, blueprint_id: str, *, now: int) -> Blueprint:
        """Retire a blueprint (terminal). Requires RETIRE authority."""
        self._require_access(session_id, blueprint_id, BlueprintAction.RETIRE, now=now)
        updated = self._registry.transition(blueprint_id, BlueprintStatus.RETIRED, tick=now)
        self._emit(BLUEPRINT_RETIRED_EVENT, subject=blueprint_id, payload={})
        self._emit_health_change()
        return updated

    def update_metadata(
        self, session_id: str, blueprint_id: str, metadata: BlueprintMetadata, *, now: int
    ) -> Blueprint:
        """Replace a blueprint's metadata immutably (requires AUTHOR authority)."""
        self._require_access(session_id, blueprint_id, BlueprintAction.AUTHOR, now=now)
        if not isinstance(metadata, BlueprintMetadata):
            raise BlueprintServiceError("update_metadata requires a BlueprintMetadata")
        updated = self._registry.update_metadata(blueprint_id, metadata)
        self._emit(
            BLUEPRINT_METADATA_UPDATED_EVENT,
            subject=blueprint_id,
            payload={"metadata_fingerprint": metadata.fingerprint()},
        )
        return updated

    # -- associations -----------------------------------------------------------

    def associate(
        self,
        session_id: str,
        blueprint_id: str,
        kind: BlueprintAssociationKind,
        ref_id: str,
        *,
        now: int,
    ) -> BlueprintAssociation:
        """Bind a typed reference to a blueprint (requires owner or administrator)."""
        self._require_access(session_id, blueprint_id, BlueprintAction.ASSOCIATE, now=now)
        association = self._associations.add(blueprint_id, kind, ref_id, tick=now)
        self._emit(
            BLUEPRINT_ASSOCIATION_ADDED_EVENT,
            subject=blueprint_id,
            payload={"kind": kind.value, "ref_id": ref_id},
        )
        return association

    def dissociate(
        self,
        session_id: str,
        blueprint_id: str,
        kind: BlueprintAssociationKind,
        ref_id: str,
        *,
        now: int,
    ) -> BlueprintAssociation:
        """Unbind a typed reference from a blueprint (requires owner or administrator)."""
        self._require_access(session_id, blueprint_id, BlueprintAction.DISSOCIATE, now=now)
        association = self._associations.remove(blueprint_id, kind, ref_id, tick=now)
        self._emit(
            BLUEPRINT_ASSOCIATION_REMOVED_EVENT,
            subject=blueprint_id,
            payload={"kind": kind.value, "ref_id": ref_id},
        )
        return association

    # -- resolution / discovery -------------------------------------------------

    def resolve(self, slug: str, workspace_id: str) -> Blueprint:
        """Resolve a blueprint by slug within a workspace (pure read; fail-closed)."""
        return self._registry.resolve(slug, workspace_id)

    def discover(
        self,
        session_id: str,
        *,
        now: int,
        tenant: str | None = None,
        workspace_id: str | None = None,
        family: BlueprintFamily | None = None,
    ) -> tuple[Blueprint, ...]:
        """Discover the blueprints a caller may see (authorized READ + isolation)."""
        principal = self._resolve_principal(session_id, now)
        if principal is None:
            return ()
        group, permission = authority_for(BlueprintAction.DISCOVER)
        decision = self._authorization.authorize_principal(
            principal, group, permission, tenant=tenant
        )
        if not decision.permitted:
            return ()
        return tuple(
            blueprint
            for blueprint in self._registry.discover(
                workspace_id=workspace_id, tenant=tenant, family=family
            )
            if not tenants_isolated(principal.tenant, blueprint.tenant)
        )

    # -- selection / context ----------------------------------------------------

    def select_blueprint(self, session_id: str, blueprint_id: str, *, now: int) -> BlueprintContext:
        """Select a blueprint and return its runtime context (fail-closed).

        Requires INSPECT (READ) access (identity + isolation). Raises
        :class:`BlueprintAccessError` when access is denied.
        """
        access = self.evaluate_access(session_id, blueprint_id, BlueprintAction.INSPECT, now=now)
        if not access.granted:
            raise BlueprintAccessError(
                "blueprint selection denied", reason=access.reason, blueprint_id=blueprint_id
            )
        blueprint = self._registry.get(blueprint_id)
        principal = self._authorization.principals.get(access.principal_id)
        return BlueprintContext.create(blueprint, principal, is_owner=access.is_owner)

    # -- traceability (link-4 evidence) -----------------------------------------

    def trace(self, session_id: str, blueprint_id: str, *, now: int) -> dict[str, Any]:
        """Return the link-4 trace edge for a blueprint (requires TRACE; fail-closed).

        The returned edge is the evidence-backed ``Generation → Blueprint →
        Implementation`` citation a traceability determination reads to reclassify
        GOV-002 link-4 from BREAK to PRESENT (§5.4/§5.5).
        """
        access = self.evaluate_access(session_id, blueprint_id, BlueprintAction.TRACE, now=now)
        if not access.granted:
            raise BlueprintAccessError(
                "blueprint trace denied", reason=access.reason, blueprint_id=blueprint_id
            )
        return self._provenance.trace(blueprint_id)

    # -- access evaluation ------------------------------------------------------

    def evaluate_access(
        self, session_id: str, blueprint_id: str, action: BlueprintAction, *, now: int
    ) -> BlueprintAccess:
        """Evaluate composed blueprint access (identity ∧ isolation ∧ owner-scoping).

        Denials are returned as data (``granted == False``); a malformed request or an
        unknown blueprint raises. Every evaluation is emitted as a governed
        ``blueprint.access.evaluated`` event (PC-16).
        """
        if not isinstance(action, BlueprintAction):
            raise BlueprintServiceError("action must be a BlueprintAction")
        group, permission = authority_for(action)
        blueprint = self._registry.get(blueprint_id)
        decision = self._authorization.authorize(
            session_id, group, permission, now=now, tenant=blueprint.tenant, resource=blueprint_id
        )
        access = self._compose_access(blueprint, action, permission, decision, group)
        self._access_evaluations += 1
        self._emit(
            BLUEPRINT_ACCESS_EVENT,
            subject=access.principal_id,
            payload={
                "blueprint_id": blueprint_id,
                "action": action.value,
                "granted": access.granted,
                "reason": access.reason,
            },
        )
        return access

    def _compose_access(
        self,
        blueprint: Blueprint,
        action: BlueprintAction,
        permission: Permission,
        decision: AccessDecision,
        group: Any,
    ) -> BlueprintAccess:
        if not decision.permitted:
            return BlueprintAccess.create(
                blueprint_id=blueprint.blueprint_id,
                action=action,
                permission=permission,
                granted=False,
                reason=decision.reason,
                decision=decision,
            )
        principal = self._authorization.principals.get(decision.request.principal_id)
        if tenants_isolated(principal.tenant, blueprint.tenant):
            return BlueprintAccess.create(
                blueprint_id=blueprint.blueprint_id,
                action=action,
                permission=permission,
                granted=False,
                reason="tenant-isolation-violation",
                decision=decision,
            )
        is_owner = principal.subject == blueprint.owner_subject
        if action in MUTATING_ACTIONS:
            if blueprint.is_terminal:
                return BlueprintAccess.create(
                    blueprint_id=blueprint.blueprint_id,
                    action=action,
                    permission=permission,
                    granted=False,
                    reason="blueprint-retired",
                    decision=decision,
                    is_owner=is_owner,
                )
            is_admin = self._authorization.permissions.has_permission(
                principal, group, Permission.ADMINISTER
            )
            if not (is_owner or is_admin):
                return BlueprintAccess.create(
                    blueprint_id=blueprint.blueprint_id,
                    action=action,
                    permission=permission,
                    granted=False,
                    reason="not-an-owner",
                    decision=decision,
                    is_owner=is_owner,
                )
        return BlueprintAccess.create(
            blueprint_id=blueprint.blueprint_id,
            action=action,
            permission=permission,
            granted=True,
            reason="granted",
            decision=decision,
            is_owner=is_owner,
        )

    # -- status derivation ------------------------------------------------------

    def status_of(self, blueprint_id: str) -> DerivedBlueprintStatus:
        """Derive a deterministic status for a blueprint (pure read; fail-closed)."""
        blueprint = self._registry.get(blueprint_id)
        return derive_status(
            blueprint,
            self._associations.associations_of(blueprint_id),
            has_provenance=self._provenance.has(blueprint_id),
        )

    # -- search -----------------------------------------------------------------

    def search(
        self,
        session_id: str,
        query: str,
        *,
        now: int,
        tenant: str | None = None,
        workspace_id: str | None = None,
        family: BlueprintFamily | None = None,
    ) -> BlueprintSearchResponse:
        """Run an authorization- and isolation-scoped blueprint search."""
        return self._search.search(
            session_id, query, now=now, tenant=tenant, workspace_id=workspace_id, family=family
        )

    # -- health integration -----------------------------------------------------

    def health_report(self) -> dict[str, Any]:
        """The blueprint runtime health endpoint (reuses the observability model)."""
        return self._health_registry.endpoint(self._health.probe())

    # -- evidence ---------------------------------------------------------------

    def evidence(self) -> BlueprintEvidence:
        """Produce deterministic Blueprint Evidence over the runtime state."""
        report = self._health_registry.report(self._health.probe())
        catalogued = sum(1 for b in self._registry.all() if b.is_catalogued)
        return BlueprintEvidence.create(
            registry_fingerprint=self._registry.fingerprint(),
            classifications_fingerprint=self._classifications.fingerprint(),
            provenance_fingerprint=self._provenance.fingerprint(),
            associations_fingerprint=self._associations.fingerprint(),
            catalog_fingerprint=self._catalog.fingerprint(),
            blueprint_count=len(self._registry),
            catalogued_count=catalogued,
            provenance_count=len(self._provenance),
            association_count=len(self._associations),
            access_evaluation_count=self._access_evaluations,
            health_status=report.status.value,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "blueprint_count": len(self._registry),
            "provenance_count": len(self._provenance),
            "association_count": len(self._associations),
            "access_evaluation_count": self._access_evaluations,
            "observability_bound": self._observability is not None,
            "evidence": self.evidence().to_dict(),
        }

    # -- internals --------------------------------------------------------------

    def _require_access(
        self, session_id: str, blueprint_id: str, action: BlueprintAction, *, now: int
    ) -> BlueprintAccess:
        access = self.evaluate_access(session_id, blueprint_id, action, now=now)
        if not access.granted:
            raise BlueprintAccessError(
                "blueprint action denied",
                reason=access.reason,
                blueprint_id=blueprint_id,
                action=action.value,
            )
        return access

    def _resolve_principal(self, session_id: str, now: int):
        try:
            session = self._authorization.sessions.validate(session_id, now)
            return self._authorization.principals.get(session.principal_id)
        except IdentityError:
            return None

    def _current_health_status(self) -> str:
        return self._health_registry.report(self._health.probe()).status.value

    def _emit_health_change(self) -> None:
        status = self._current_health_status()
        if status != self._last_health_status:
            self._last_health_status = status
            self._emit(
                BLUEPRINT_HEALTH_CHANGED_EVENT,
                subject=_RUNTIME_SUBJECT,
                payload={"status": status},
            )

    def _emit(self, event_type: str, *, subject: str, payload: dict[str, Any]) -> None:
        if self._events is not None:
            self._events.publish(
                event_type,
                source="platform.blueprints.runtime",
                subject=subject,
                payload=payload,
            )


def build_blueprint_service(
    *,
    authorization: AuthorizationService,
    workspaces: WorkspaceRegistry,
    observability: ObservabilityService | None = None,
    events: EventBus | None = None,
    registry: BlueprintRegistry | None = None,
    classifications: ClassificationLedger | None = None,
    provenance: ProvenanceLedger | None = None,
    associations: BlueprintAssociationRegistry | None = None,
) -> BlueprintService:
    """Default, registry-driven composition of the Blueprint Catalog & Management Runtime.

    Wires the blueprint registry, classification + provenance ledgers, association
    registry, catalog read model, blueprint search (over the supplied Identity
    ``authorization`` service), the blueprint health probe and a health registry seeded
    with the blueprint health checks, the reused workspace registry (parent-scope
    binding + isolation), and — when supplied — the observability layer and event bus.
    """
    if not isinstance(authorization, AuthorizationService):
        raise BlueprintServiceError("build_blueprint_service requires an AuthorizationService")
    if not isinstance(workspaces, WorkspaceRegistry):
        raise BlueprintServiceError("build_blueprint_service requires a WorkspaceRegistry")
    blueprint_registry = registry if registry is not None else BlueprintRegistry()
    classification_ledger = (
        classifications if classifications is not None else ClassificationLedger()
    )
    provenance_ledger = provenance if provenance is not None else ProvenanceLedger()
    association_registry = (
        associations if associations is not None else BlueprintAssociationRegistry()
    )
    catalog = BlueprintCatalog(blueprint_registry, provenance_ledger)
    search = BlueprintSearch(blueprint_registry, authorization)
    health = BlueprintHealth(blueprint_registry, provenance_ledger, association_registry)
    health_registry = HealthRegistry()
    for check in blueprint_health_checks():
        health_registry.register(check)
    return BlueprintService(
        registry=blueprint_registry,
        classifications=classification_ledger,
        provenance=provenance_ledger,
        associations=association_registry,
        catalog=catalog,
        authorization=authorization,
        workspaces=workspaces,
        search=search,
        health=health,
        health_registry=health_registry,
        observability=observability,
        events=events,
    )


__all__ = [
    "BLUEPRINT_AUTHORED_EVENT",
    "BLUEPRINT_CLASSIFIED_EVENT",
    "BLUEPRINT_VALIDATED_EVENT",
    "BLUEPRINT_VERSIONED_EVENT",
    "BLUEPRINT_CATALOGUED_EVENT",
    "BLUEPRINT_SUPERSEDED_EVENT",
    "BLUEPRINT_RETIRED_EVENT",
    "BLUEPRINT_METADATA_UPDATED_EVENT",
    "BLUEPRINT_ASSOCIATION_ADDED_EVENT",
    "BLUEPRINT_ASSOCIATION_REMOVED_EVENT",
    "BLUEPRINT_TRACEABILITY_LINKED_EVENT",
    "BLUEPRINT_HEALTH_CHANGED_EVENT",
    "BLUEPRINT_ACCESS_EVENT",
    "BlueprintAccess",
    "BlueprintEvidence",
    "BlueprintService",
    "build_blueprint_service",
]
