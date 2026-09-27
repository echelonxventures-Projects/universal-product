"""UCOS-AKEY-001 — the machine-readable authority key.

Resolves an owner across the three disclaiming planes.

The three planes each answer a different question and each disclaims the others'
authority, which is why ownership rows could not be joined to enforcement (SQ-12 /
T-22.2 / S-3). This module does not create a new authority — CEP-009 I.5 forbids
self-conferral, and SCOPE-B's own finding is that the fix is *composition over
existing authorities, not a new authority*. It composes the two existing planes
and the ownership catalogue into one query.

Composition (all three already exist, all three are authoritative in their own shape):

    CONSTITUTIONAL  engine.uckp.alignment.repository_local_urn   (SUPREME, UCKP-ART-05)
    REPOSITORY      00-BOOK/DATA/id-ledger.json                   (PERSISTENCE)
    OWNERSHIP       platform/universal_ownership/catalog          (the 59 assignments)

The key is derived, never minted. `repository_local_urn` is a pure derivation; the
ledger is append-only and frozen at mint; the catalogue is declared truth. Nothing
here advances a counter or reissues an identity.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]

CONSTITUTIONAL_HOME = "engine/uckp/alignment.py"
LEDGER_HOME = "00-BOOK/DATA/id-ledger.json"
CATALOG_HOME = "platform/universal_ownership/catalog/ucos-ownership-declarations.json"

UNRESOLVED = "UNRESOLVED"


@dataclass(frozen=True)
class AuthorityKey:
    """One owner, resolved as far as the three planes can take it.

    Every field is either located or the literal sentinel. A field that is
    ``UNRESOLVED`` is reported, never guessed: the planes disclaim authority over
    each other's shape, and filling a gap with a plausible value would be the
    fabricated owner OWN-REQ-001 forbids.
    """

    subject: str
    owner: str
    authority: str
    locator: str
    urn: str
    repository_id: str

    def as_dict(self) -> dict[str, str]:
        return {
            "subject": self.subject,
            "owner": self.owner,
            "authority": self.authority,
            "locator": self.locator,
            "urn": self.urn,
            "repository_id": self.repository_id,
        }


def _urn_of(subject: str) -> str:
    """Derive the constitutional-plane URN for a subject id.

    Uses the declared derivation directly; this is the join the discovery report
    measured at 6,079/6,079, 0 failures. The derivation is strict by design — it
    accepts repository identifiers only, and raises on anything else rather than
    emitting a string that looks like an identity but is not one. A mandate id
    such as ``AF-3`` is not a repository identifier, so the plane reports
    ``UNRESOLVED`` instead of a fabricated URN.
    """
    from engine.uckp.alignment import AlignmentError, repository_local_urn

    try:
        return repository_local_urn(subject)
    except AlignmentError:
        return UNRESOLVED


def _ledger_index(root: Path) -> dict[str, str]:
    """path -> repository id, from the persistence plane. Empty when absent.

    The ledger is keyed ``by_path`` directly: each path maps to its minted
    ``UCOS-<CATEGORY>-<NNNNNN>``. That is the whole join surface — no object list
    to walk, the path IS the key.
    """
    path = root / LEDGER_HOME
    if not path.is_file():
        return {}
    document: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    by_path = document.get("by_path", {})
    index: dict[str, str] = {}
    for relative, value in by_path.items():
        if isinstance(value, dict):
            index[str(relative)] = str(value.get("universal_id") or UNRESOLVED)
        else:
            index[str(relative)] = str(value)
    return index


def _catalog_assignments(root: Path) -> dict[str, dict[str, str]]:
    """subject -> assignment row, from the ownership catalogue."""
    path = root / CATALOG_HOME
    if not path.is_file():
        return {}
    document: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    assignments = document.get("assignments", {})
    if isinstance(assignments, dict):
        return {str(k): dict(v) for k, v in assignments.items()}
    if isinstance(assignments, list):
        return {str(row[0]): dict(row[1]) for row in assignments if row}
    return {}


def resolve(subject: str, *, root: Path | None = None) -> AuthorityKey:
    """Resolve one subject to an authority key across all three planes.

    A subject the catalogue does not name returns every plane at ``UNRESOLVED``
    rather than a default owner — the framework has no fallback, by OWN-REQ-004.
    """
    root = root or REPO_ROOT
    assignments = _catalog_assignments(root)
    row = assignments.get(subject)
    if row is None:
        return AuthorityKey(
            subject=subject,
            owner=UNRESOLVED,
            authority=UNRESOLVED,
            locator=UNRESOLVED,
            urn=_urn_of(subject),
            repository_id=UNRESOLVED,
        )

    ledger = _ledger_index(root)
    locator = str(row.get("locator") or "")
    repository_id = ledger.get(locator, UNRESOLVED)

    return AuthorityKey(
        subject=subject,
        owner=str(row.get("owner") or UNRESOLVED),
        authority=str(row.get("authority") or UNRESOLVED),
        locator=locator or UNRESOLVED,
        urn=_urn_of(subject),
        repository_id=repository_id,
    )


def resolve_all(*, root: Path | None = None) -> list[AuthorityKey]:
    """Resolve every subject in the catalogue. Order is stable (catalogue order)."""
    root = root or REPO_ROOT
    return [resolve(subject, root=root) for subject in _catalog_assignments(root)]


def coverage(*, root: Path | None = None) -> dict[str, Any]:
    """Measure the join across all three planes.

    The honest number: how many subjects resolve on every plane, and how many do
    not. A subject whose locator is absent from the ledger is reported as
    ``locator_not_in_ledger`` — the ownership plane names a home the persistence
    plane has no record of, which is the join failure S-3 exists to surface.
    """
    keys = resolve_all(root=root)
    total = len(keys)
    if not total:
        return {
            "subjects": 0,
            "fully_resolved": 0,
            "locator_not_in_ledger": 0,
            "unresolved_owner": 0,
            "fraction_fully_resolved": 0.0,
            "planes_composed": ["CONSTITUTIONAL", "REPOSITORY", "OWNERSHIP"],
        }

    fully = sum(1 for k in keys if k.repository_id != UNRESOLVED and k.owner != UNRESOLVED)
    no_ledger = sum(1 for k in keys if k.locator != UNRESOLVED and k.repository_id == UNRESOLVED)
    no_owner = sum(1 for k in keys if k.owner == UNRESOLVED)
    return {
        "subjects": total,
        "fully_resolved": fully,
        "locator_not_in_ledger": no_ledger,
        "unresolved_owner": no_owner,
        "fraction_fully_resolved": round(fully / total, 4),
        "planes_composed": ["CONSTITUTIONAL", "REPOSITORY", "OWNERSHIP"],
        "authority_key_home": "platform/universal_ownership/authority_key.py",
        "derivation": "composed; nothing minted",
    }
