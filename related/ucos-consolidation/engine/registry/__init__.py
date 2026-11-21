"""EC-1 Registry Adapter (EPIC-002) — read-only access over the 00-BOOK substrate.

Public API surface for the read-only Registry Adapter built on the EC-1 Foundation
(EPIC-001). The adapter never writes to the certified corpus (DP-03) and exposes
its capabilities through the versioned ``registry.read`` contract (AR-03, PL-05).

Tasks: TASK-000010 (source + errors), TASK-000011 (models), TASK-000012 (artifacts),
TASK-000013 (relationship graph), TASK-000014 (volumes + integrity),
TASK-000015 (unified adapter facade), TASK-000016 (integration).
"""

from __future__ import annotations

from engine.registry.adapter import REGISTRY_READ_CONTRACT, RegistryAdapter
from engine.registry.artifacts import ArtifactRepository
from engine.registry.errors import (
    ArtifactNotFoundError,
    RegistryDataError,
    RegistryError,
    RegistrySourceError,
    RegistryValidationError,
    VolumeNotFoundError,
)
from engine.registry.graph import CHILD, DEPENDS_ON, PARENT, RelationshipGraph
from engine.registry.models import (
    TRACE_STAGES,
    Artifact,
    LifecycleStatus,
    Relationship,
    Traceability,
    Volume,
)
from engine.registry.source import (
    ARTIFACTS_FILE,
    RELATIONSHIPS_FILE,
    VOLUMES_FILE,
    RegistrySource,
    default_data_dir,
)
from engine.registry.volumes import IntegrityReport, VolumeRepository, check_integrity

__all__ = [
    # adapter facade
    "RegistryAdapter",
    "REGISTRY_READ_CONTRACT",
    # source
    "RegistrySource",
    "default_data_dir",
    "ARTIFACTS_FILE",
    "RELATIONSHIPS_FILE",
    "VOLUMES_FILE",
    # models
    "Artifact",
    "Relationship",
    "Volume",
    "Traceability",
    "LifecycleStatus",
    "TRACE_STAGES",
    # repositories / graph
    "ArtifactRepository",
    "RelationshipGraph",
    "VolumeRepository",
    "DEPENDS_ON",
    "PARENT",
    "CHILD",
    # integrity
    "IntegrityReport",
    "check_integrity",
    # errors
    "RegistryError",
    "RegistrySourceError",
    "RegistryDataError",
    "RegistryValidationError",
    "ArtifactNotFoundError",
    "VolumeNotFoundError",
]
