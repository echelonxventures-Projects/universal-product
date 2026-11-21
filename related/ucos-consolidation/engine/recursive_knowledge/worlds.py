"""URKE-000001 Part 05 — realities and temporal systems, resolved from data.

Neither is a branch in code. A reality is a declared row that answers each declared dimension or
names it unresolved; a temporal system is a declared row that binds to a system type its owner
actually implements and a chronology model the existence universe actually carries. Admitting a
reality or a chronology nobody has met is a row, and this module never learns its name.

The live readers matter more than they look. Reading the frame kinds out of the reference-frame
catalogue and the system types out of the temporal capability means a binding that has gone stale is
a measured refusal rather than a comment that used to be true.
"""

from __future__ import annotations

import json
import pathlib
from collections.abc import Mapping
from types import MappingProxyType
from typing import Any

from engine.recursive_knowledge.declaration import Declaration
from engine.recursive_knowledge.model import RecursiveKnowledgeError


class WorldsError(RecursiveKnowledgeError):
    """The reality or temporal system is not one the declaration declares. A fault."""


def frame_kinds(declaration: Declaration, *, repository: str) -> frozenset[str]:
    """The frame kinds the context authority's catalogue actually carries."""
    target = pathlib.Path(repository) / declaration.frame_kind_owner
    try:
        document = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise WorldsError(f"the reference frame catalogue cannot be read: {exc}") from exc
    frames = document.get("frames") if isinstance(document, Mapping) else None
    if not isinstance(frames, list):
        raise WorldsError("the reference frame catalogue declares no frames")
    return frozenset(str(frame.get("frame_kind")) for frame in frames if isinstance(frame, Mapping))


def system_types() -> frozenset[str]:
    """The temporal system types the temporal capability actually implements."""
    try:
        from engine.temporal.coordinate import SystemType
    except ImportError as exc:  # pragma: no cover - a missing owner is a fault, not a verdict
        raise WorldsError(f"the temporal system type owner cannot be read: {exc}") from exc
    return frozenset(member.value for member in SystemType)


def chronology_models() -> frozenset[str]:
    """The temporal models the existence universe actually carries."""
    try:
        from engine.ceu.catalog import SEED_TEMPORAL_MODELS
    except ImportError as exc:  # pragma: no cover - a missing owner is a fault, not a verdict
        raise WorldsError(f"the chronology owner cannot be read: {exc}") from exc
    return frozenset(str(row[0]) for row in SEED_TEMPORAL_MODELS)


def resolve(declaration: Declaration, identifier: str) -> Mapping[str, Any]:
    """Resolve a reality to its dimension systems, marking which are unresolved.

    An unresolved dimension is the declared token, never a default. That is the difference between
    "this reality does not answer that question yet" and "we quietly assumed the answer".
    """
    spec = declaration.reality(identifier)
    systems = {
        dimension.identifier: spec.systems.get(dimension.identifier, declaration.unresolved_token)
        for dimension in declaration.reality_dimensions
    }
    unresolved = tuple(
        sorted(name for name, value in systems.items() if value == declaration.unresolved_token)
    )
    return MappingProxyType(
        {
            "frame_kind": spec.frame_kind,
            "identifier": spec.identifier,
            "is_residual": spec.residual,
            "resolved": len(systems) - len(unresolved),
            "systems": MappingProxyType(systems),
            "unresolved_dimensions": unresolved,
        }
    )


def resolve_temporal(declaration: Declaration, identifier: str) -> Mapping[str, Any]:
    """Resolve a temporal system to its declared bindings, epoch included or explicitly absent."""
    spec = declaration.temporal_system(identifier)
    return MappingProxyType(
        {
            "calendar_system": spec.calendar_system,
            "causality_model": spec.causality_model,
            "chronology_model": spec.chronology_model,
            "epoch": spec.epoch,
            "epoch_resolved": spec.epoch != declaration.temporal_unresolved_token,
            "identifier": spec.identifier,
            "reference_frame": spec.reference_frame,
            "system_type": spec.system_type,
        }
    )


def reality_problems(declaration: Declaration, *, repository: str) -> list[str]:
    """Every reality whose frame binding is stale, or which omits a dimension without saying so."""
    problems: list[str] = []
    live = frame_kinds(declaration, repository=repository)
    dimensions = {spec.identifier for spec in declaration.reality_dimensions}
    for spec in declaration.realities:
        for dimension in sorted(dimensions - set(spec.systems)):
            problems.append(
                f"reality {spec.identifier!r} omits dimension {dimension!r} rather than naming it "
                "unresolved"
            )
        if spec.frame_kind:
            if spec.frame_kind not in live:
                problems.append(
                    f"reality {spec.identifier!r} binds to frame kind {spec.frame_kind!r}, which "
                    "the catalogue does not carry"
                )
        else:
            gap = spec.frame_kind_gap or {}
            for required in ("gap_id", "finding", "referred_to", "remediation"):
                if not str(gap.get(required) or "").strip():
                    problems.append(
                        f"reality {spec.identifier!r} binds to no frame kind and its gap discloses "
                        f"no {required}"
                    )
    return problems


def temporal_problems(declaration: Declaration) -> list[str]:
    """Every temporal system binding to a type or chronology its owner does not implement."""
    problems: list[str] = []
    types, models = system_types(), chronology_models()
    for spec in declaration.temporal_systems:
        if spec.system_type not in types:
            problems.append(
                f"temporal system {spec.identifier!r} binds to system type {spec.system_type!r}, "
                "which the temporal capability does not implement"
            )
        if spec.chronology_model not in models:
            problems.append(
                f"temporal system {spec.identifier!r} binds to chronology model "
                f"{spec.chronology_model!r}, which the existence universe does not carry"
            )
        if spec.epoch == declaration.temporal_unresolved_token and spec.epoch_gap is None:
            continue
    if not any(spec.epoch_gap is not None for spec in declaration.temporal_systems):
        problems.append(
            "no temporal system discloses an epoch gap, so a residual chronology would be claiming "
            "an epoch it cannot have"
        )
    return problems


__all__ = [
    "WorldsError",
    "chronology_models",
    "frame_kinds",
    "reality_problems",
    "resolve",
    "resolve_temporal",
    "system_types",
    "temporal_problems",
]
