"""UCOS EC-2 Platform Artifact Explorer Runtime (EC2-EPIC-009).

The Artifact Explorer Runtime (L3 Application of the Program architecture, §4) realizes
Program **Surface #10 Artifact Explorer** (PC-08 artifact discovery + PC-13 search +
PC-16 audit): it makes the EC-2 generation artifacts **discoverable, navigable, and
traceable** to authorized principals, **read-only**. Authorized principals look up an
artifact view, discover/search artifacts under authorization + isolation, navigate an
artifact's lineage (``Generation → Blueprint → Request → Implementation``), inspect its
link-4 provenance-by-reference, and follow its full generation→execution trace — and
navigate from a request to its artifact — with cross-runtime health, append-only audit,
and reproducible evidence.

Authoritative basis: ``06-IMPLEMENTATION/UCOS-EC-2-PLATFORM-REALIZATION-PROGRAM.md``
(§2.1 surface #10 Artifact Explorer, PC-08/PC-13/PC-16, §3.2 RBAC row
``artifact-explorer``, §4 L3, §5 EC2-EPIC-009 acceptance), consuming the certified
EC2-EPIC-007 Generation Request Runtime (``platform/generation/``, consumed read-only by
reference).

It is a strictly **additive**, **read/navigation-only** layer over the EC-2 Foundation
(EC2-EPIC-001), Identity (EC2-EPIC-002), Observability (EC2-EPIC-013), and Generation
Request (EC2-EPIC-007) layers: it authorizes only through the Identity Layer on the
existing ``artifact-explorer`` capability group (no new authority, no new capability
group), consumes the artifact/dispatch/provenance references **only by reference** (never
re-derived, never mutated), observes only through the Observability Layer, and exposes
**no artifact generation, no artifact mutation, and no engine execution** path. It
modifies neither EC-1 nor any prior layer, never writes to the certified corpus (DP-03),
remains deterministic, starts no server, and opens no socket.

Deliverables (EC2-TASK-000127…000134):
    * **errors** — the ``EC2-AX-*`` error taxonomy over ``PlatformError``.
    * **contracts** — vocabulary (``ExplorerAction``), the verb→permission map binding the
      ``artifact-explorer`` group, and ``ARTIFACT_EXPLORER_CONTRACTS``.
    * **references** — the read-only projections (``ArtifactReference``,
      ``ArtifactSummary``, ``ArtifactView``).
    * **lineage** — the navigation projections (``ArtifactProvenance``,
      ``ArtifactLineage``, ``ArtifactTrace``).
    * **context** — the resolved ``ArtifactContext`` runtime binding.
    * **search** — authorization- and isolation-scoped ``ArtifactSearch`` +
      ``ArtifactSearchResult``/``ArtifactSearchResponse`` (consumes EPIC-007 search).
    * **health** — explorer health checks + ``ExplorerHealth`` (reuses L8 model).
    * **evidence** — the deterministic ``ExplorerEvidence`` runtime evidence.
    * **service** — the ``ArtifactExplorerService`` composition root + ``ArtifactAccess``.
    * **bootstrap** — ``bootstrap_artifact_explorer`` (composes identity + observability +
      generation + the explorer runtime).
"""

from __future__ import annotations

from platform.artifact_explorer.bootstrap import (
    ARTIFACT_EXPLORER_BOOTSTRAP_EVENT,
    bootstrap_artifact_explorer,
)
from platform.artifact_explorer.context import ArtifactContext
from platform.artifact_explorer.contracts import (
    ARTIFACT_EXPLORER_CONTRACT_VERSION,
    ARTIFACT_EXPLORER_CONTRACTS,
    ARTIFACT_EXPLORER_GROUP,
    ArtifactFamily,
    ExplorerAction,
    all_explorer_actions,
    artifact_explorer_contract,
    default_artifact_explorer_contracts,
    permission_for,
)
from platform.artifact_explorer.errors import (
    ArtifactAccessError,
    ArtifactContractError,
    ArtifactExplorerError,
    ArtifactLineageError,
    ArtifactProvenanceError,
    ArtifactReferenceError,
    ArtifactSearchError,
    ArtifactServiceError,
    ArtifactTraceError,
)
from platform.artifact_explorer.evidence import ExplorerEvidence
from platform.artifact_explorer.health import (
    DISPATCH_CHECK,
    PROVENANCE_CHECK,
    REGISTRY_CHECK,
    ExplorerHealth,
    artifact_explorer_health_checks,
)
from platform.artifact_explorer.lineage import (
    ArtifactLineage,
    ArtifactProvenance,
    ArtifactTrace,
)
from platform.artifact_explorer.references import (
    ArtifactReference,
    ArtifactSummary,
    ArtifactView,
)
from platform.artifact_explorer.search import (
    ArtifactSearch,
    ArtifactSearchResponse,
    ArtifactSearchResult,
)
from platform.artifact_explorer.service import (
    ARTIFACT_ACCESS_EVENT,
    ARTIFACT_DISCOVERED_EVENT,
    ARTIFACT_HEALTH_CHANGED_EVENT,
    ARTIFACT_LINEAGE_NAVIGATED_EVENT,
    ARTIFACT_NAVIGATED_EVENT,
    ARTIFACT_PROVENANCE_NAVIGATED_EVENT,
    ARTIFACT_SEARCHED_EVENT,
    ARTIFACT_TRACE_NAVIGATED_EVENT,
    ARTIFACT_VIEWED_EVENT,
    METRIC_DISCOVERIES,
    METRIC_LINEAGE,
    METRIC_LOOKUPS,
    METRIC_PROVENANCE,
    METRIC_SEARCHES,
    METRIC_TRACE,
    ArtifactAccess,
    ArtifactExplorerService,
    build_artifact_explorer_service,
)

__all__ = [
    # contracts
    "ARTIFACT_EXPLORER_CONTRACT_VERSION",
    "ARTIFACT_EXPLORER_CONTRACTS",
    "ARTIFACT_EXPLORER_GROUP",
    "ArtifactFamily",
    "ExplorerAction",
    "permission_for",
    "all_explorer_actions",
    "artifact_explorer_contract",
    "default_artifact_explorer_contracts",
    # references
    "ArtifactReference",
    "ArtifactSummary",
    "ArtifactView",
    # lineage
    "ArtifactProvenance",
    "ArtifactLineage",
    "ArtifactTrace",
    # context
    "ArtifactContext",
    # search
    "ArtifactSearchResult",
    "ArtifactSearchResponse",
    "ArtifactSearch",
    # health
    "REGISTRY_CHECK",
    "PROVENANCE_CHECK",
    "DISPATCH_CHECK",
    "artifact_explorer_health_checks",
    "ExplorerHealth",
    # evidence
    "ExplorerEvidence",
    # service
    "ARTIFACT_VIEWED_EVENT",
    "ARTIFACT_DISCOVERED_EVENT",
    "ARTIFACT_LINEAGE_NAVIGATED_EVENT",
    "ARTIFACT_PROVENANCE_NAVIGATED_EVENT",
    "ARTIFACT_TRACE_NAVIGATED_EVENT",
    "ARTIFACT_SEARCHED_EVENT",
    "ARTIFACT_NAVIGATED_EVENT",
    "ARTIFACT_HEALTH_CHANGED_EVENT",
    "ARTIFACT_ACCESS_EVENT",
    "METRIC_LOOKUPS",
    "METRIC_DISCOVERIES",
    "METRIC_SEARCHES",
    "METRIC_LINEAGE",
    "METRIC_PROVENANCE",
    "METRIC_TRACE",
    "ArtifactAccess",
    "ArtifactExplorerService",
    "build_artifact_explorer_service",
    # bootstrap
    "ARTIFACT_EXPLORER_BOOTSTRAP_EVENT",
    "bootstrap_artifact_explorer",
    # errors
    "ArtifactExplorerError",
    "ArtifactContractError",
    "ArtifactReferenceError",
    "ArtifactLineageError",
    "ArtifactProvenanceError",
    "ArtifactTraceError",
    "ArtifactSearchError",
    "ArtifactAccessError",
    "ArtifactServiceError",
]
