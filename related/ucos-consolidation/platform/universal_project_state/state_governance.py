"""UCOS-CTRL-STATE-000001 — Project State governance adapter (Wave 11).

Project state does not govern itself. It presents itself to the governance service the
repository already has: :class:`~platform.universal_control_plane.governance.GovernanceEngine`,
adjudicating the rule set declared in ``catalog/ucos-control-plane.json``.

This module is therefore an **adapter and nothing else** — one projection from a
:class:`~platform.universal_project_state.state.StateEntity` into the
:class:`~platform.universal_control_plane.governance.GovernanceSubject` shape that engine
already accepts. There is no state rule set, no state severity model, no state verdict
vocabulary and no second engine: a new rule added to the declared manifest governs project
state with no change here, because the rule's ``requires`` fact resolves through the
subject's open fact bag.

The facts are read, never invented. ``owner`` is the owner the entity already carries,
``registered`` is whether the registry holds it, ``version`` and ``canonical_home`` are the
fields the ontology already publishes, and absence is reported as absence — an entity with no
owner fails the owner rule rather than being quietly given one.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from platform.universal_control_plane.governance import GovernanceSubject
from platform.universal_control_plane.ontology import LIFECYCLE_DRAFT
from platform.universal_project_state.state import ProjectStateSnapshot, StateEntity
from platform.universal_project_state.state_registry import ProjectStateRegistry

#: Attribute keys consulted for a declared version, in order of precedence.
VERSION_KEYS: tuple[str, ...] = ("version", "revision")

#: Attribute keys consulted for a canonical home locator, in order of precedence.
HOME_KEYS: tuple[str, ...] = ("locator",)

#: Attribute keys consulted for traceable evidence, in order of precedence.
EVIDENCE_KEYS: tuple[str, ...] = ("evidence_ids", "traceability")


def attribute_text(attributes: Mapping[str, object], keys: tuple[str, ...]) -> str:
    """The first non-empty string among *keys*, or ``""`` when the entity declares none."""
    for key in keys:
        value = attributes.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _evidence(attributes: Mapping[str, object]) -> tuple[str, ...]:
    for key in EVIDENCE_KEYS:
        value = attributes.get(key)
        if isinstance(value, str) and value.strip():
            return (value.strip(),)
        if isinstance(value, list | tuple):
            found = tuple(str(item).strip() for item in value if str(item).strip())
            if found:
                return found
    return ()


def governance_subject(
    entity: StateEntity, *, registry: ProjectStateRegistry | None = None
) -> GovernanceSubject:
    """Project one state entity into the declared governance subject shape."""
    registered = registry is not None and entity.subject_id in registry.subjects()
    return GovernanceSubject(
        subject_id=entity.subject_id,
        kind=entity.kind,
        owner=entity.owner,
        registered=registered,
        version=attribute_text(entity.attributes, VERSION_KEYS),
        canonical_home=bool(attribute_text(entity.attributes, HOME_KEYS)),
        evidence_ids=_evidence(entity.attributes),
        lifecycle_state=entity.lifecycle or LIFECYCLE_DRAFT,
        facts=dict(entity.attributes),
    )


def governance_subjects(
    entities: Iterable[StateEntity], *, registry: ProjectStateRegistry | None = None
) -> tuple[GovernanceSubject, ...]:
    """Project state entities into governance subjects, deterministically ordered."""
    return tuple(
        sorted(
            (governance_subject(e, registry=registry) for e in entities),
            key=lambda s: s.subject_id,
        )
    )


def snapshot_subjects(
    snapshot: ProjectStateSnapshot, *, registry: ProjectStateRegistry | None = None
) -> tuple[GovernanceSubject, ...]:
    """Project every entity a snapshot carries into a governance subject."""
    return governance_subjects(snapshot.entities, registry=registry)


__all__ = [
    "EVIDENCE_KEYS",
    "attribute_text",
    "HOME_KEYS",
    "VERSION_KEYS",
    "governance_subject",
    "governance_subjects",
    "snapshot_subjects",
]
