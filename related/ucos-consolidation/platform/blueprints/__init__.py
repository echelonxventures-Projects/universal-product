"""UCOS EC-2 Platform Blueprint Catalog & Management Runtime (EC2-EPIC-006).

The Blueprint Catalog & Management Runtime (L3 Application / L6 Knowledge of the Program
architecture, §4) realizes Program **Surface #7 Blueprint Management** (PC-04 authoring
& validation + PC-05 catalog): it lets authorized principals author or import blueprint
documents, structurally validate + classify them against the certified EC-1 engine
(read-only), version them immutably with append-only lineage, publish them into a
provenance-carrying L6 catalog, discover/search them under authorization + isolation,
and associate them **by reference** to workspaces, projects, requests, artifacts, other
blueprints, and their originating generation artifacts — with cross-runtime health,
append-only audit, and reproducible evidence.

Authoritative basis: ``06-IMPLEMENTATION/UCOS-EC-2-PLATFORM-REALIZATION-PROGRAM.md``
(§2.1 surface #7 Blueprint Management, PC-04 + PC-05, §3.2 ``blueprint-authoring`` +
``blueprint-catalog``, §4 L3/L4/L5/L6, §4.3 EC-1 "validate a blueprint pre-submit",
§5 EC2-EPIC-006 acceptance, P4), as determined by
``platform/blueprints/EC2-EPIC-006-DETERMINATION.md`` (**IMPLEMENTATION AUTHORIZED**),
and the frozen ``05-GENERATION/`` generation-framework corpus (the definition of what a
blueprint is and where blueprints originate).

**Primary objective — GOV-002 link-4 closure.** EPIC-006 is the trace-closure epic: it
discharges the standing ``05-GENERATION → 06-IMPLEMENTATION`` traceability break by
making each cataloged blueprint carry provenance-by-reference from its generation origin
down to its implementation target, rendering the previously-absent generation→
implementation trace materially **present** (``Generation Artifact → Blueprint →
Request → Implementation Artifact``).

It is a strictly **additive** layer over the certified EC-1 engine and the EC-2
Foundation (EC2-EPIC-001), Identity (EC2-EPIC-002), Observability (EC2-EPIC-013),
Workspace (EC2-EPIC-004), and Project Management (EC2-EPIC-005) layers: it authorizes
only through the Identity Layer on the two existing blueprint capability groups (no new
authority, no new capability group), classifies only through the read-only L4 EC-1
façade (records the result, computes none), observes only through the Observability
Layer, and binds to workspaces/projects by reference. It introduces no new
classification model, modifies neither EC-1 nor any prior layer, never writes to the
certified corpus (DP-03), remains deterministic, starts no server, and opens no socket.

Deliverables (EC2-TASK-000097…000108):
    * **errors** — the ``EC2-BP-*`` error taxonomy over ``PlatformError``.
    * **metadata** — the immutable ``BlueprintMetadata`` value type.
    * **contracts** — vocabulary (``BlueprintFamily``, ``BlueprintStatus``,
      ``BlueprintAction``, ``Blueprint``), the verb→(group, permission) map binding
      ``blueprint-authoring`` + ``blueprint-catalog``, and ``BLUEPRINT_CONTRACTS``.
    * **classification** — the read-only L4 EC-1 classification façade + ledger.
    * **validation** — structural validation orchestration (gap report, fail-closed).
    * **lifecycle** — the deterministic blueprint state machine + ``BlueprintEvent``.
    * **versioning** — immutable content-addressed versions + lineage + supersession.
    * **registry** — the ``BlueprintRegistry`` (create/register/resolve/version).
    * **provenance** — provenance-by-reference + ``ProvenanceLedger`` (link-4 closure).
    * **catalog** — the L6 catalog read model / index (``BlueprintCatalog``).
    * **associations** — the append-only ``BlueprintAssociationRegistry`` (by reference).
    * **status** — the deterministic derived-status computation.
    * **context** — the resolved ``BlueprintContext`` runtime binding.
    * **search** — authorization- and isolation-scoped ``BlueprintSearch``.
    * **health** — blueprint health checks + ``BlueprintHealth`` (reuses L8 model).
    * **service** — the ``BlueprintService`` composition root + ``BlueprintEvidence``.
    * **bootstrap** — ``bootstrap_blueprints`` (composes identity + observability +
      workspace + projects + the EC-1 façade + blueprints).
"""

from __future__ import annotations

from platform.blueprints.associations import (
    BlueprintAssociation,
    BlueprintAssociationEvent,
    BlueprintAssociationKind,
    BlueprintAssociationRegistry,
    all_association_kinds,
)
from platform.blueprints.bootstrap import BLUEPRINT_BOOTSTRAP_EVENT, bootstrap_blueprints
from platform.blueprints.catalog import BlueprintCatalog, CatalogEntry
from platform.blueprints.classification import (
    CLASSIFICATION_CONTRACTS,
    COMPILER_CONTRACT,
    REGISTRY_CONTRACT,
    BlueprintClassification,
    ClassificationLedger,
    classify,
)
from platform.blueprints.context import BlueprintContext
from platform.blueprints.contracts import (
    BLUEPRINT_AUTHORING_GROUP,
    BLUEPRINT_CATALOG_GROUP,
    BLUEPRINT_CONTRACT_VERSION,
    BLUEPRINT_CONTRACTS,
    MUTATING_ACTIONS,
    Blueprint,
    BlueprintAction,
    BlueprintFamily,
    BlueprintStatus,
    all_blueprint_actions,
    all_blueprint_families,
    all_blueprint_statuses,
    authority_for,
    blueprint_contract,
    default_blueprint_contracts,
    group_for,
    permission_for,
)
from platform.blueprints.errors import (
    BlueprintAccessError,
    BlueprintAssociationError,
    BlueprintCatalogError,
    BlueprintClassificationError,
    BlueprintContractError,
    BlueprintError,
    BlueprintLifecycleError,
    BlueprintMetadataError,
    BlueprintProvenanceError,
    BlueprintRegistryError,
    BlueprintSearchError,
    BlueprintServiceError,
    BlueprintStatusError,
    BlueprintValidationError,
    BlueprintVersionError,
)
from platform.blueprints.health import (
    INTEGRITY_CHECK,
    PROVENANCE_CHECK,
    REGISTRY_CHECK,
    BlueprintHealth,
    blueprint_health_checks,
)
from platform.blueprints.lifecycle import (
    BlueprintEvent,
    allowed_transitions,
    can_transition,
    validate_transition,
)
from platform.blueprints.metadata import EMPTY_METADATA, BlueprintMetadata
from platform.blueprints.provenance import BlueprintProvenance, ProvenanceLedger
from platform.blueprints.registry import BlueprintRegistry
from platform.blueprints.search import (
    BlueprintHit,
    BlueprintSearch,
    BlueprintSearchResponse,
)
from platform.blueprints.service import (
    BLUEPRINT_ACCESS_EVENT,
    BLUEPRINT_ASSOCIATION_ADDED_EVENT,
    BLUEPRINT_ASSOCIATION_REMOVED_EVENT,
    BLUEPRINT_AUTHORED_EVENT,
    BLUEPRINT_CATALOGUED_EVENT,
    BLUEPRINT_CLASSIFIED_EVENT,
    BLUEPRINT_HEALTH_CHANGED_EVENT,
    BLUEPRINT_METADATA_UPDATED_EVENT,
    BLUEPRINT_RETIRED_EVENT,
    BLUEPRINT_SUPERSEDED_EVENT,
    BLUEPRINT_TRACEABILITY_LINKED_EVENT,
    BLUEPRINT_VALIDATED_EVENT,
    BLUEPRINT_VERSIONED_EVENT,
    BlueprintAccess,
    BlueprintEvidence,
    BlueprintService,
    build_blueprint_service,
)
from platform.blueprints.status import (
    BlueprintPosture,
    DerivedBlueprintStatus,
    derive_status,
)
from platform.blueprints.validation import ValidationResult, evaluate, require_valid
from platform.blueprints.versioning import (
    BlueprintVersion,
    VersionLineage,
    content_hash_of,
)

__all__ = [
    # contracts
    "BLUEPRINT_CONTRACT_VERSION",
    "BLUEPRINT_CONTRACTS",
    "BLUEPRINT_AUTHORING_GROUP",
    "BLUEPRINT_CATALOG_GROUP",
    "BlueprintFamily",
    "BlueprintStatus",
    "BlueprintAction",
    "MUTATING_ACTIONS",
    "Blueprint",
    "authority_for",
    "group_for",
    "permission_for",
    "all_blueprint_families",
    "all_blueprint_statuses",
    "all_blueprint_actions",
    "blueprint_contract",
    "default_blueprint_contracts",
    # metadata
    "BlueprintMetadata",
    "EMPTY_METADATA",
    # classification
    "REGISTRY_CONTRACT",
    "COMPILER_CONTRACT",
    "CLASSIFICATION_CONTRACTS",
    "BlueprintClassification",
    "classify",
    "ClassificationLedger",
    # validation
    "ValidationResult",
    "evaluate",
    "require_valid",
    # lifecycle
    "BlueprintEvent",
    "allowed_transitions",
    "can_transition",
    "validate_transition",
    # versioning
    "BlueprintVersion",
    "VersionLineage",
    "content_hash_of",
    # registry
    "BlueprintRegistry",
    # provenance
    "BlueprintProvenance",
    "ProvenanceLedger",
    # catalog
    "CatalogEntry",
    "BlueprintCatalog",
    # associations
    "BlueprintAssociationKind",
    "all_association_kinds",
    "BlueprintAssociation",
    "BlueprintAssociationEvent",
    "BlueprintAssociationRegistry",
    # status
    "BlueprintPosture",
    "DerivedBlueprintStatus",
    "derive_status",
    # context
    "BlueprintContext",
    # search
    "BlueprintHit",
    "BlueprintSearchResponse",
    "BlueprintSearch",
    # health
    "REGISTRY_CHECK",
    "PROVENANCE_CHECK",
    "INTEGRITY_CHECK",
    "blueprint_health_checks",
    "BlueprintHealth",
    # service
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
    # bootstrap
    "BLUEPRINT_BOOTSTRAP_EVENT",
    "bootstrap_blueprints",
    # errors
    "BlueprintError",
    "BlueprintContractError",
    "BlueprintMetadataError",
    "BlueprintProvenanceError",
    "BlueprintClassificationError",
    "BlueprintValidationError",
    "BlueprintLifecycleError",
    "BlueprintVersionError",
    "BlueprintRegistryError",
    "BlueprintAssociationError",
    "BlueprintStatusError",
    "BlueprintCatalogError",
    "BlueprintSearchError",
    "BlueprintAccessError",
    "BlueprintServiceError",
]
