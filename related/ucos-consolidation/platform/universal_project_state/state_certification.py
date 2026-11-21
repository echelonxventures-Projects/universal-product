"""UCOS-CTRL-STATE-000001 — Project State certification adapter (Wave 11).

Project state does not certify itself either. It presents its *already governed* records to
:class:`~platform.universal_control_plane.certification.CertificationEngine`, which evaluates
the criteria declared in ``catalog/ucos-control-plane.json``.

Like the governance adapter, this module holds one projection and no policy. It does not
recount severities — governance already adjudicated them, and
:meth:`~platform.universal_control_plane.certification.CertificationSubject.from_governance`
carries that adjudication forward, so a second opinion on the same rule set can never appear
here. What this adapter adds is the one thing the generic projection cannot know: which
version string belongs to which state subject, taken from the version the entity itself
publishes.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from platform.universal_control_plane.certification import CertificationSubject
from platform.universal_control_plane.ontology import GovernanceRecord
from platform.universal_project_state.state import ProjectStateSnapshot, StateEntity
from platform.universal_project_state.state_governance import VERSION_KEYS, attribute_text


def version_index(entities: Iterable[StateEntity]) -> dict[str, str]:
    """The subject-to-version map certification needs, read from the entities themselves."""
    return {
        entity.subject_id: attribute_text(entity.attributes, VERSION_KEYS)
        for entity in entities
        if attribute_text(entity.attributes, VERSION_KEYS)
    }


def certification_subject(
    record: GovernanceRecord, *, versions: Mapping[str, str] | None = None
) -> CertificationSubject:
    """Project one governed state record into the declared certification subject shape."""
    lookup = versions or {}
    return CertificationSubject.from_governance(
        record,
        version=lookup.get(record.subject_id, ""),
        kind=str(record.attributes.get("subject_kind", "StateEntity")),
    )


def certification_subjects(
    records: Iterable[GovernanceRecord], *, versions: Mapping[str, str] | None = None
) -> tuple[CertificationSubject, ...]:
    """Project governed state records into certification subjects, deterministically."""
    return tuple(
        sorted(
            (certification_subject(r, versions=versions) for r in records),
            key=lambda s: s.subject_id,
        )
    )


def snapshot_certification_subjects(
    snapshot: ProjectStateSnapshot, records: Iterable[GovernanceRecord]
) -> tuple[CertificationSubject, ...]:
    """Project governed records for *snapshot*, versioned from the snapshot's own entities."""
    return certification_subjects(records, versions=version_index(snapshot.entities))


__all__ = [
    "certification_subject",
    "certification_subjects",
    "snapshot_certification_subjects",
    "version_index",
]
