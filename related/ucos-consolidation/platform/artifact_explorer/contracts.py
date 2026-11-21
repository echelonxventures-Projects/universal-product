"""EC2-TASK-000127 — Artifact Explorer Contracts (EC2-EPIC-009).

The versioned contract surface for the UCOS Platform **Artifact Explorer Runtime**
(L3 Application of the Program architecture, §4) plus the immutable **core vocabulary**
every artifact-explorer service speaks. It reuses the certified EC-1 contract machinery
through the Platform Foundation
(:func:`~platform.foundation.contracts.platform_contract`,
:class:`~platform.foundation.contracts.ContractRef`) and binds explorer authorization to
the single §3.2 :class:`~platform.identity.contracts.CapabilityGroup`
``artifact-explorer`` (PC-08, matrix index 9) that **already physically exists** in the
certified Identity Layer. EC2-EPIC-009 introduces **no new capability group, no new
authority, and no new authorization logic**.

It also **reuses — rather than reinventing** — the frozen EC-2 generation vocabulary: the
recorded generation ``family`` is one of the six frozen
:class:`~platform.blueprints.contracts.BlueprintFamily` members (recorded read-only via
the referenced request), and every artifact datum is a faithful, by-reference projection
of a :class:`~platform.generation.contracts.GenerationRequest`,
:class:`~platform.generation.dispatch.DispatchRecord`, and
:class:`~platform.generation.provenance.RequestProvenance` produced by EC2-EPIC-007. The
explorer **records/derives nothing of its own** — it navigates existing references
(no duplicate artifact model, no artifact generation, no artifact mutation).

Vocabulary:
    * :class:`ExplorerAction` — the governed (read-only) explorer verbs, each mapped to
      the coarse RBAC :class:`~platform.foundation.identity.Permission` it requires (all
      :data:`Permission.READ`).
    * :data:`ARTIFACT_EXPLORER_CONTRACTS` — the published explorer service contracts
      downstream consumers (portal, presentation) bind to by reference (PL-05, versioned).

All types are **immutable, typed, deterministic, and serializable**, hold no runtime
state, and hold no secret material (SEC-04).
"""

from __future__ import annotations

from enum import Enum
from platform.artifact_explorer.errors import ArtifactContractError
from platform.blueprints.contracts import BlueprintFamily
from platform.foundation.contracts import (
    Contract,
    ContractRef,
    platform_contract,
)
from platform.foundation.errors import PlatformContractError
from platform.foundation.identity import Permission
from platform.identity.contracts import CapabilityGroup

#: The semantic version of the Artifact Explorer Runtime contract surface (AR-03/PL-05).
ARTIFACT_EXPLORER_CONTRACT_VERSION = "1.0.0"

#: The §3.2 capability group authorizing every explorer action (reused; no new group).
ARTIFACT_EXPLORER_GROUP = CapabilityGroup.ARTIFACT_EXPLORER

#: Re-export of the frozen generation family vocabulary (recorded, never computed).
ArtifactFamily = BlueprintFamily


class ExplorerAction(str, Enum):
    """The governed (read-only) artifact-explorer verbs.

    Every action requires only :data:`Permission.READ` on the ``artifact-explorer``
    group — the explorer exposes no create/execute/administer authority and no mutation
    path to any artifact, provenance, or dispatch reference (read-only runtime).
    """

    LOOKUP = "lookup"
    DISCOVER = "discover"
    SEARCH = "search"
    LINEAGE = "lineage"
    PROVENANCE = "provenance"
    TRACE = "trace"
    NAVIGATE = "navigate"


#: The verb→permission map. Every explorer verb is READ-only (read-only runtime).
_ACTION_PERMISSIONS: dict[ExplorerAction, Permission] = {
    action: Permission.READ for action in ExplorerAction
}


def permission_for(action: ExplorerAction) -> Permission:
    """Return the RBAC permission required by an explorer action (fail-closed)."""
    if not isinstance(action, ExplorerAction):
        raise ArtifactContractError("action must be an ExplorerAction")
    return _ACTION_PERMISSIONS[action]


def all_explorer_actions() -> tuple[ExplorerAction, ...]:
    """Return every artifact-explorer action in stable declaration order."""
    return tuple(ExplorerAction)


# --------------------------------------------------------------------------- #
# The published artifact-explorer contract surface (L3).                      #
# --------------------------------------------------------------------------- #

#: The explorer service contract identities the Artifact Explorer Runtime publishes.
#: Each maps to an EC2-EPIC-009 deliverable; consumers bind to these by reference (PL-05).
_ARTIFACT_EXPLORER_CONTRACT_NAMES: tuple[tuple[str, str], ...] = (
    ("artifacts.reference.resolve", "Reference — resolve an artifact-by-reference view."),
    ("artifacts.discovery.discover", "Discovery — authorization + isolation scoped artifacts."),
    ("artifacts.lineage.navigate", "Lineage — Generation→Blueprint→Request→Implementation."),
    ("artifacts.provenance.navigate", "Provenance — link-4 provenance-by-reference projection."),
    ("artifacts.trace.navigate", "Trace — full generation→execution trace navigation."),
    ("artifacts.search.query", "Artifact search — authorization + isolation scoped discovery."),
    ("artifacts.runtime.service", "Explorer runtime — the L3 read-only access + navigation point."),
)

#: Immutable references to the published artifact-explorer contracts (name + version).
ARTIFACT_EXPLORER_CONTRACTS: tuple[ContractRef, ...] = tuple(
    ContractRef(name, ARTIFACT_EXPLORER_CONTRACT_VERSION)
    for name, _ in _ARTIFACT_EXPLORER_CONTRACT_NAMES
)


def artifact_explorer_contract(name: str, description: str = "") -> Contract:
    """Build a versioned explorer :class:`Contract` at the explorer contract version."""
    if not isinstance(name, str) or not name:
        raise ArtifactContractError("artifact explorer contract name is required")
    try:
        return platform_contract(name, ARTIFACT_EXPLORER_CONTRACT_VERSION, description)
    except PlatformContractError as exc:  # pragma: no cover - defensive normalisation
        raise ArtifactContractError(str(exc), name=name) from exc


def default_artifact_explorer_contracts() -> tuple[Contract, ...]:
    """The published explorer contracts as concrete :class:`Contract` objects."""
    return tuple(
        artifact_explorer_contract(name, description)
        for name, description in _ARTIFACT_EXPLORER_CONTRACT_NAMES
    )


__all__ = [
    "ARTIFACT_EXPLORER_CONTRACT_VERSION",
    "ARTIFACT_EXPLORER_GROUP",
    "ArtifactFamily",
    "ExplorerAction",
    "permission_for",
    "all_explorer_actions",
    "ARTIFACT_EXPLORER_CONTRACTS",
    "artifact_explorer_contract",
    "default_artifact_explorer_contracts",
]
