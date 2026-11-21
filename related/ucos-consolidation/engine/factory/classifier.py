"""TASK-000039 — Blueprint Classification Resolution (EPIC-006).

Derives a blueprint's **class** (its :class:`~engine.compiler.ir.BlueprintFamily`)
from metadata alone, using the closed, registered family vocabulary (IMP-007 §2).
The resolver is the substrate of the Factory Layer's *blueprint-type-independent*
routing: it never hard-codes per-type branches or special-case execution paths —
it reads declared metadata fields and matches them against the shared family
vocabulary, in a deterministic precedence order.

Accepted metadata sources (all "registry metadata" in the constitutional sense —
declared, registered fields, never invented):

    1. an explicit ``family`` field (the authoritative classification),
    2. an id-like field prefix (``blueprint_id`` / ``universal_id`` / ``native_id``
       / ``id``) matching a family value,
    3. a ``category`` token matching a family value or bare family suffix,
    4. a ``tags`` list containing a family token.

Both a registry :class:`~engine.registry.models.Artifact` and a plain blueprint
document mapping are accepted, so the same resolver classifies a registered
artifact record and an input blueprint document identically.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from engine.compiler.ir import BlueprintFamily
from engine.factory.errors import ClassificationError
from engine.registry.models import Artifact

#: The id-like fields, in precedence order, whose prefix can carry a family token.
_ID_FIELDS: tuple[str, ...] = ("blueprint_id", "universal_id", "native_id", "id")

#: Family values ordered longest-first so e.g. ``BP-APPLICATION`` is matched before
#: a hypothetical shorter prefix collision; deterministic and unambiguous.
_FAMILIES_BY_LENGTH: tuple[BlueprintFamily, ...] = tuple(
    sorted(BlueprintFamily, key=lambda f: (-len(f.value), f.value))
)


@dataclass(frozen=True, slots=True)
class BlueprintClassification:
    """The immutable result of classifying a blueprint from its metadata."""

    blueprint_class: BlueprintFamily
    source: str  # which metadata field the class was derived from
    token: str  # the raw metadata token the class was derived from

    @property
    def value(self) -> str:
        """The family value string (e.g. ``BP-DATA``)."""
        return self.blueprint_class.value

    def to_dict(self) -> dict[str, Any]:
        return {
            "blueprint_class": self.blueprint_class.value,
            "source": self.source,
            "token": self.token,
        }


def _artifact_to_metadata(artifact: Artifact) -> dict[str, Any]:
    """Project a registry :class:`Artifact` onto a classification metadata mapping."""
    return {
        "universal_id": artifact.universal_id,
        "native_id": artifact.native_id or "",
        "category": artifact.category,
        "tags": list(artifact.tags),
    }


def _as_metadata(metadata: Artifact | Mapping[str, Any]) -> Mapping[str, Any]:
    if isinstance(metadata, Artifact):
        return _artifact_to_metadata(metadata)
    if isinstance(metadata, Mapping):
        return metadata
    raise ClassificationError(
        "blueprint metadata must be an Artifact or a mapping",
        got=type(metadata).__name__,
    )


def _match_family_token(token: str) -> BlueprintFamily | None:
    """Return the family whose value equals or prefixes ``token`` (deterministic)."""
    needle = token.strip().upper()
    if not needle:
        return None
    for family in _FAMILIES_BY_LENGTH:
        value = family.value  # e.g. "BP-DATA"
        if needle == value or needle.startswith(value + "-"):
            return family
        # bare suffix form, e.g. category "DATA" ⇒ BP-DATA
        if needle == value.split("-", 1)[1]:
            return family
    return None


def resolve_blueprint_class(
    metadata: Artifact | Mapping[str, Any],
) -> BlueprintClassification:
    """Resolve the blueprint class from ``metadata`` (registry metadata only).

    Raises:
        ClassificationError: if no declared field yields a known family.
    """
    data = _as_metadata(metadata)

    # 1. explicit family field — the authoritative declared classification.
    family_field = data.get("family")
    if isinstance(family_field, str) and family_field.strip():
        family = _match_family_token(family_field)
        if family is None:
            raise ClassificationError(
                "declared family is not a registered blueprint family",
                family=family_field,
                allowed=[f.value for f in _FAMILIES_BY_LENGTH],
            )
        return BlueprintClassification(family, source="family", token=family_field)

    # 2. id-like field prefix.
    for key in _ID_FIELDS:
        value = data.get(key)
        if isinstance(value, str) and value.strip():
            family = _match_family_token(value)
            if family is not None:
                return BlueprintClassification(family, source=key, token=value)

    # 3. category token.
    category = data.get("category")
    if isinstance(category, str) and category.strip():
        family = _match_family_token(category)
        if family is not None:
            return BlueprintClassification(family, source="category", token=category)

    # 4. tags.
    tags = data.get("tags")
    if isinstance(tags, list | tuple):
        for tag in tags:
            if isinstance(tag, str):
                family = _match_family_token(tag)
                if family is not None:
                    return BlueprintClassification(family, source="tag", token=tag)

    raise ClassificationError(
        "could not derive a blueprint class from the supplied metadata",
        keys=sorted(str(k) for k in data),
    )


__all__ = [
    "BlueprintClassification",
    "resolve_blueprint_class",
]
