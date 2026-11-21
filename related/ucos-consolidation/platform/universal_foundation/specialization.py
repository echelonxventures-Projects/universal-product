"""UCOS-UFP-001 — Project specialisation by declaration.

A project does not extend the Foundation with code; it **declares a specialisation**. This
module is that declaration: which Repository Truth policy governs it, where its governed
ownership assignments live, how to project its population out of whatever document it already
keeps, and where its source manifest is.

Everything project-specific in the entire Foundation lives in documents of this shape. That is
the mechanical guarantee behind "nothing shall be implemented as a one-off repository fix":
there is no other place for a repository name to be written down.
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from platform.foundation.contracts import content_hash
from platform.universal_foundation.errors import SpecializationError
from platform.universal_ownership.contracts import OwnershipGranularity
from platform.universal_ownership.evidence import (
    DEFAULT_IDENTITY_HEAD_BYTES,
    DEFAULT_IDENTITY_LABELS,
)
from platform.universal_truth.eligibility import EligibilityLedger
from platform.universal_truth.projection import ProjectionSpec
from typing import Any

#: The packaged catalogue directory holding declared project specialisations.
CATALOG_DIRNAME = "catalog"

#: The specialisation shipped for the containing repository (data, not code).
DEFAULT_CATALOG_FILENAME = "ucos-consolidation.json"


@dataclass(frozen=True, slots=True)
class FoundationSpecialization:
    """A declared specialisation of the Universal Foundation for one project."""

    project_id: str
    truth_policy: str = ""
    ownership_declarations: str = ""
    population_document: str = ""
    projection: ProjectionSpec | None = None
    source_manifest: str = ""
    registered_subjects: str = ""
    require_registration: bool = False
    registration_document: str = ""
    registration_projection: ProjectionSpec | None = None
    eligibility: EligibilityLedger | None = None
    ownership_granularity: OwnershipGranularity = OwnershipGranularity.AUTHORITY
    identity_labels: tuple[str, ...] = ()
    identity_head_bytes: int = DEFAULT_IDENTITY_HEAD_BYTES
    evidence_roles: tuple[tuple[str, int], ...] = ()
    peer_attribute: str = ""
    description: str = ""
    specialization_id: str = ""

    @classmethod
    def create(
        cls,
        project_id: str,
        *,
        truth_policy: str = "",
        ownership_declarations: str = "",
        population_document: str = "",
        projection: ProjectionSpec | Mapping[str, Any] | None = None,
        source_manifest: str = "",
        registered_subjects: str = "",
        require_registration: bool = False,
        registration_document: str = "",
        registration_projection: ProjectionSpec | Mapping[str, Any] | None = None,
        eligibility: EligibilityLedger | Mapping[str, Any] | None = None,
        ownership_granularity: OwnershipGranularity | str = OwnershipGranularity.AUTHORITY,
        identity_labels: Iterable[str] = (),
        identity_head_bytes: int = DEFAULT_IDENTITY_HEAD_BYTES,
        evidence_roles: Mapping[str, int] | Iterable[tuple[str, int]] | None = None,
        peer_attribute: str = "",
        description: str = "",
    ) -> FoundationSpecialization:
        """Build a validated specialisation with a content-addressed identity."""
        if not isinstance(project_id, str) or not project_id.strip():
            raise SpecializationError("specialisation requires a project_id")
        spec = (
            projection
            if projection is None or isinstance(projection, ProjectionSpec)
            else ProjectionSpec.from_dict(projection)
        )
        registration_spec = (
            registration_projection
            if registration_projection is None
            or isinstance(registration_projection, ProjectionSpec)
            else ProjectionSpec.from_dict(registration_projection)
        )
        ledger = (
            eligibility
            if eligibility is None or isinstance(eligibility, EligibilityLedger)
            else EligibilityLedger.from_document(eligibility)
        )
        grain = OwnershipGranularity.coerce(ownership_granularity, subject=project_id.strip())
        labels = tuple(str(item) for item in identity_labels if str(item).strip())
        roles = tuple(
            sorted(
                (str(k), int(v))
                for k, v in dict(evidence_roles or {}).items()
                # A '$'-prefixed key is a declaration comment, never a role.
                if not str(k).strip().startswith("$")
            )
        )
        if registration_spec is not None and not registration_document:
            raise SpecializationError(
                "a registration projection was declared without a registration document",
                project_id=project_id.strip(),
            )
        core = {
            "project_id": project_id.strip(),
            "truth_policy": truth_policy,
            "ownership_declarations": ownership_declarations,
            "population_document": population_document,
            "projection": spec.to_dict() if spec else {},
            "source_manifest": source_manifest,
            "registered_subjects": registered_subjects,
            "require_registration": bool(require_registration),
            "registration_document": registration_document,
            "registration_projection": (registration_spec.to_dict() if registration_spec else {}),
            "eligibility": ledger.to_dict() if ledger else {},
            "ownership_granularity": grain.value,
            "identity_labels": list(labels),
            "identity_head_bytes": int(identity_head_bytes),
            "evidence_roles": list(roles),
            "peer_attribute": peer_attribute,
        }
        return cls(
            project_id=project_id.strip(),
            truth_policy=truth_policy,
            ownership_declarations=ownership_declarations,
            population_document=population_document,
            projection=spec,
            source_manifest=source_manifest,
            registered_subjects=registered_subjects,
            require_registration=bool(require_registration),
            registration_document=registration_document,
            registration_projection=registration_spec,
            eligibility=ledger,
            ownership_granularity=grain,
            identity_labels=labels,
            identity_head_bytes=int(identity_head_bytes),
            evidence_roles=roles,
            peer_attribute=peer_attribute,
            description=description,
            specialization_id=f"UCOS-UFPZ-{content_hash(core)[:16]}",
        )

    @classmethod
    def from_document(cls, document: Mapping[str, Any]) -> FoundationSpecialization:
        """Build a specialisation from a declared document."""
        if not isinstance(document, Mapping):
            raise SpecializationError("specialisation document must be a mapping")
        if "project_id" not in document:
            raise SpecializationError("specialisation document requires 'project_id'")
        return cls.create(
            str(document["project_id"]),
            truth_policy=str(document.get("truth_policy", "")),
            ownership_declarations=str(document.get("ownership_declarations", "")),
            population_document=str(document.get("population_document", "")),
            projection=document.get("projection"),
            source_manifest=str(document.get("source_manifest", "")),
            registered_subjects=str(document.get("registered_subjects", "")),
            require_registration=bool(document.get("require_registration", False)),
            registration_document=str(document.get("registration_document", "")),
            registration_projection=document.get("registration_projection"),
            eligibility=document.get("eligibility"),
            ownership_granularity=document.get(
                "ownership_granularity", OwnershipGranularity.AUTHORITY
            ),
            identity_labels=document.get("identity_labels", ()),
            identity_head_bytes=int(
                document.get("identity_head_bytes", DEFAULT_IDENTITY_HEAD_BYTES)
            ),
            evidence_roles=document.get("evidence_roles"),
            peer_attribute=str(document.get("peer_attribute", "")),
            description=str(document.get("description", "")),
        )

    @property
    def labels(self) -> tuple[str, ...]:
        """The declared identity labels, falling back to the framework's reusable set."""
        return self.identity_labels or DEFAULT_IDENTITY_LABELS

    def resolve(self, name: str, *, root: Path | str = ".") -> Path | None:
        """Resolve a declared relative path against ``root`` (``None`` when undeclared)."""
        value = getattr(self, name, "")
        if not value:
            return None
        candidate = Path(value)
        return candidate if candidate.is_absolute() else Path(root) / candidate

    def to_dict(self) -> dict[str, Any]:
        """A JSON-serialisable projection of this specialisation."""
        return {
            "specialization_id": self.specialization_id,
            "project_id": self.project_id,
            "truth_policy": self.truth_policy,
            "ownership_declarations": self.ownership_declarations,
            "population_document": self.population_document,
            "projection": self.projection.to_dict() if self.projection else None,
            "source_manifest": self.source_manifest,
            "registered_subjects": self.registered_subjects,
            "require_registration": self.require_registration,
            "registration_document": self.registration_document,
            "registration_projection": (
                self.registration_projection.to_dict() if self.registration_projection else None
            ),
            "eligibility": self.eligibility.to_dict() if self.eligibility else None,
            "ownership_granularity": self.ownership_granularity.value,
            "identity_labels": list(self.identity_labels),
            "identity_head_bytes": self.identity_head_bytes,
            "evidence_roles": {name: precedence for name, precedence in self.evidence_roles},
            "peer_attribute": self.peer_attribute,
            "description": self.description,
        }

    def fingerprint(self) -> str:
        """The deterministic content fingerprint of this specialisation."""
        return content_hash(self.to_dict())


def catalog_path(filename: str = DEFAULT_CATALOG_FILENAME) -> Path:
    """The packaged catalogue path for ``filename``."""
    return Path(__file__).resolve().parent / CATALOG_DIRNAME / filename


def load_specialization(path: Path | str) -> FoundationSpecialization:
    """Load a declared specialisation document from ``path`` (fail-closed)."""
    target = Path(path)
    try:
        document = json.loads(target.read_text("utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SpecializationError(
            "specialisation document could not be read", path=str(target), detail=str(exc)
        ) from exc
    return FoundationSpecialization.from_document(document)


def default_specialization(
    filename: str = DEFAULT_CATALOG_FILENAME,
) -> FoundationSpecialization:
    """The specialisation shipped in the packaged catalogue."""
    return load_specialization(catalog_path(filename))


__all__ = [
    "CATALOG_DIRNAME",
    "DEFAULT_CATALOG_FILENAME",
    "FoundationSpecialization",
    "catalog_path",
    "load_specialization",
    "default_specialization",
]
