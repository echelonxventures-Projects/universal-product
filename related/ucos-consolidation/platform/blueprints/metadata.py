"""EC2-TASK-000097 — Blueprint Metadata (EC2-EPIC-006).

The immutable, deterministic descriptive metadata carried by a
:class:`~platform.blueprints.contracts.Blueprint`: a free-text description, a set of
labels, and string annotations. Metadata is **value data only** — it carries no
authority, no secret material (SEC-04), and no runtime state — and it is
content-addressable so an identical metadata definition always yields the same
fingerprint (IMP-007 §5 determinism). It mirrors the certified
:class:`~platform.projects.metadata.ProjectMetadata` value type exactly (proven
template) rather than inventing a new metadata model.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from platform.blueprints.errors import BlueprintMetadataError
from platform.foundation.contracts import content_hash
from typing import Any


@dataclass(frozen=True, slots=True)
class BlueprintMetadata:
    """Immutable, content-addressed descriptive metadata for a blueprint."""

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
    ) -> BlueprintMetadata:
        """Build normalized, validated metadata (deterministic)."""
        if not isinstance(description, str):
            raise BlueprintMetadataError("blueprint description must be a string")
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
        raise BlueprintMetadataError(f"blueprint {what} must be a non-empty string")
    return value


#: The canonical empty metadata (shared default; immutable).
EMPTY_METADATA = BlueprintMetadata()


__all__ = ["BlueprintMetadata", "EMPTY_METADATA"]
