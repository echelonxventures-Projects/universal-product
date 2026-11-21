"""EPIC-VAL-002 — Repository Acceptance Contracts (Terminal T3).

The value types that flow across the Repository Acceptance boundary. Every type is
**immutable, typed, deterministic, and serializable** and holds no runtime state:

    * :class:`GateSeverity` — whether a failing gate blocks acceptance or is advisory.
    * :class:`GateStatus` — the outcome of a single acceptance gate.
    * :class:`AcceptanceStatus` — the aggregate verdict (fail-closed ACCEPTED / REJECTED).
    * :class:`CoverageDimension` / :class:`CoverageProfile` — the repository coverage
      surface that must be 100% (statements, branches, functions, public API,
      exception paths, repository).
    * :class:`UnitRecord`, :class:`DependencyRecord`, :class:`ReuseRecord`,
      :class:`IntegrationRecord`, :class:`RepositoryInventory`,
      :class:`RepositoryHealth` — the normalized, type-independent projection of the
      acceptance-relevant facts of a repository.
    * :class:`RepositorySubject` — the assimilated repository the gates evaluate.
    * :class:`AcceptanceFinding` — the immutable outcome of one gate.
    * :class:`AcceptanceRecord` — the **immutable, content-addressed** Repository
      Acceptance Certificate (append-only, attributable, evidence-referenced,
      non-constitutive).

The subject is normalized (like the Validation Layer's subject) so the same gates
accept any repository / EPIC / feature without per-target branches. The engine
aggregates the assimilated facts and invents no verdict (TP-01): an identical
subject yields a byte-identical decision, record, evidence and readiness report
(IMP-007 §5).
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, ClassVar

from engine.acceptance.errors import (
    AcceptanceIntegrityError,
    RepositorySubjectError,
)

# The canonical serialization primitive has exactly one definition, in UCKP Layer Zero
# (UCKP-LAW-0001 Art-13, UCKP-INV-03). These names are re-exported unchanged, so every
# existing caller of ``engine.acceptance.contracts.content_hash`` keeps working while
# there is only one implementation of the digest behind it.
from engine.uckp.canonical import canonical_json, content_hash

#: The semantic version of the Repository Acceptance contract surface (AR-03/PL-05).
ACCEPTANCE_CONTRACT_VERSION = "1.0.0"

#: The acceptance standard a certificate attests against (record-only, IMP-007 §13).
ACCEPTANCE_STANDARD = "UCOS-REPOSITORY-ACCEPTANCE-STANDARD"
ACCEPTANCE_STANDARD_VERSION = "1.0.0"

#: Acceptance confers no constitutional authority (DE-05 / IP-01): it records
#: engineering readiness only. This is embedded verbatim in every record.
ACCEPTANCE_AUTHORITY = "ENGINEERING-EXECUTION-ONLY"

#: The trace stages a fully-traceable implementation unit must cover (IMP-007 §1).
REQUIRED_TRACE_STAGES: tuple[str, ...] = (
    "requirement",
    "design",
    "implementation",
    "test",
    "certification",
)


class GateSeverity(str, Enum):
    """Whether a failing acceptance gate blocks acceptance or is merely advisory."""

    BLOCKING = "blocking"
    ADVISORY = "advisory"


class GateStatus(str, Enum):
    """The outcome of a single acceptance gate."""

    PASS = "pass"  # noqa: S105 — enum member, not a credential
    FAIL = "fail"


class AcceptanceStatus(str, Enum):
    """The aggregate verdict of a repository acceptance determination (fail-closed)."""

    ACCEPTED = "accepted"
    REJECTED = "rejected"


# ---------------------------------------------------------------------------
# coverage surface
# ---------------------------------------------------------------------------
@dataclass(frozen=True, slots=True)
class CoverageDimension:
    """One measured coverage dimension (covered vs total counts)."""

    name: str
    covered: int
    total: int

    @property
    def complete(self) -> bool:
        """100% complete iff every measured unit is covered (vacuously so at total 0)."""
        return self.covered >= self.total

    @property
    def percent(self) -> float:
        return 100.0 if self.total == 0 else round(self.covered / self.total * 100.0, 4)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "covered": self.covered,
            "total": self.total,
            "percent": self.percent,
            "complete": self.complete,
        }


@dataclass(frozen=True, slots=True)
class CoverageProfile:
    """The repository coverage profile that acceptance requires to be 100%."""

    dimensions: tuple[CoverageDimension, ...] = ()

    #: The coverage dimensions a repository must report and complete (100%).
    REQUIRED: ClassVar[tuple[str, ...]] = (
        "statements",
        "branches",
        "functions",
        "public_api",
        "exception_paths",
        "repository",
    )

    def by_name(self) -> dict[str, CoverageDimension]:
        return {d.name: d for d in self.dimensions}

    def missing_dimensions(self) -> tuple[str, ...]:
        present = {d.name for d in self.dimensions}
        return tuple(name for name in self.REQUIRED if name not in present)

    def incomplete_dimensions(self) -> tuple[str, ...]:
        return tuple(sorted(d.name for d in self.dimensions if not d.complete))

    @property
    def complete(self) -> bool:
        return not self.missing_dimensions() and not self.incomplete_dimensions()

    def to_dict(self) -> dict[str, Any]:
        return {
            "dimensions": [d.to_dict() for d in self.dimensions],
            "required": list(self.REQUIRED),
            "missing_dimensions": list(self.missing_dimensions()),
            "incomplete_dimensions": list(self.incomplete_dimensions()),
            "complete": self.complete,
        }


# ---------------------------------------------------------------------------
# normalized repository facts
# ---------------------------------------------------------------------------
@dataclass(frozen=True, slots=True)
class UnitRecord:
    """A normalized implementation unit and its acceptance-relevant state."""

    unit_id: str
    owner: str | None = None
    implemented: bool = False
    validated: bool = False
    certified: bool = False
    registered: bool = False
    traceability: tuple[str, ...] = ()

    def missing_trace_stages(self) -> tuple[str, ...]:
        present = set(self.traceability)
        return tuple(stage for stage in REQUIRED_TRACE_STAGES if stage not in present)

    def to_dict(self) -> dict[str, Any]:
        return {
            "unit_id": self.unit_id,
            "owner": self.owner,
            "implemented": self.implemented,
            "validated": self.validated,
            "certified": self.certified,
            "registered": self.registered,
            "traceability": list(self.traceability),
        }


@dataclass(frozen=True, slots=True)
class DependencyRecord:
    """A normalized dependency and whether it is resolved and pinned (DE-04)."""

    dependency_id: str
    resolved: bool = False
    pinned: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "dependency_id": self.dependency_id,
            "resolved": self.resolved,
            "pinned": self.pinned,
        }


@dataclass(frozen=True, slots=True)
class ReuseRecord:
    """A capability the repository provides and how reuse was reconciled.

    A capability that is newly built rather than reused is a *duplicate* unless it
    is explicitly justified — unjustified duplication fails the reuse gate (TP-05).
    """

    capability: str
    reused: bool = False
    justified: bool = False

    @property
    def is_unjustified_duplicate(self) -> bool:
        return not self.reused and not self.justified

    def to_dict(self) -> dict[str, Any]:
        return {
            "capability": self.capability,
            "reused": self.reused,
            "justified": self.justified,
        }


@dataclass(frozen=True, slots=True)
class IntegrationRecord:
    """A cross-EPIC integration point and whether it is satisfied."""

    point: str
    satisfied: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {"point": self.point, "satisfied": self.satisfied}


@dataclass(frozen=True, slots=True)
class RepositoryInventory:
    """The declared vs discovered inventory used for missing/duplication/overlap.

    ``expected`` is the declared inventory; ``present`` is what discovery found;
    ``content_hashes`` maps artifact id → content hash (duplicate content across
    ids is duplication); ``responsibilities`` maps a responsibility → the artifact
    ids that own it (a responsibility owned by more than one artifact is overlap).
    """

    expected: tuple[str, ...] = ()
    present: tuple[str, ...] = ()
    content_hashes: Mapping[str, str] = field(default_factory=dict)
    responsibilities: Mapping[str, tuple[str, ...]] = field(default_factory=dict)

    def missing(self) -> tuple[str, ...]:
        present = set(self.present)
        return tuple(a for a in self.expected if a not in present)

    def extras(self) -> tuple[str, ...]:
        expected = set(self.expected)
        return tuple(sorted({a for a in self.present if a not in expected}))

    def duplicates(self) -> tuple[str, ...]:
        seen: set[str] = set()
        dup_ids: set[str] = set()
        for artifact in self.present:
            if artifact in seen:
                dup_ids.add(artifact)
            seen.add(artifact)
        by_hash: dict[str, list[str]] = {}
        for artifact_id, digest in self.content_hashes.items():
            by_hash.setdefault(digest, []).append(artifact_id)
        hash_dups = {aid for ids in by_hash.values() if len(ids) > 1 for aid in ids}
        return tuple(sorted(dup_ids | hash_dups))

    def overlaps(self) -> tuple[str, ...]:
        return tuple(sorted(r for r, owners in self.responsibilities.items() if len(owners) > 1))

    def to_dict(self) -> dict[str, Any]:
        return {
            "expected": list(self.expected),
            "present": list(self.present),
            "content_hashes": dict(self.content_hashes),
            "responsibilities": {r: list(o) for r, o in self.responsibilities.items()},
            "missing": list(self.missing()),
            "extras": list(self.extras()),
            "duplicates": list(self.duplicates()),
            "overlaps": list(self.overlaps()),
        }


@dataclass(frozen=True, slots=True)
class RepositoryHealth:
    """The repository health surface: critical issues block, warnings are advisory."""

    critical_issues: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    @property
    def healthy(self) -> bool:
        return not self.critical_issues

    def to_dict(self) -> dict[str, Any]:
        return {
            "critical_issues": list(self.critical_issues),
            "warnings": list(self.warnings),
            "healthy": self.healthy,
        }


@dataclass(frozen=True, slots=True)
class AcceptanceFinding:
    """The immutable outcome of a single acceptance gate."""

    gate_id: str
    severity: GateSeverity
    status: GateStatus
    message: str = ""
    details: Mapping[str, Any] = field(default_factory=dict)

    @property
    def passed(self) -> bool:
        return self.status is GateStatus.PASS

    @property
    def is_blocking_failure(self) -> bool:
        return self.status is GateStatus.FAIL and self.severity is GateSeverity.BLOCKING

    def to_dict(self) -> dict[str, Any]:
        return {
            "gate_id": self.gate_id,
            "severity": self.severity.value,
            "status": self.status.value,
            "message": self.message,
            "details": dict(self.details),
        }


# ---------------------------------------------------------------------------
# the assimilated subject
# ---------------------------------------------------------------------------
@dataclass(frozen=True, slots=True)
class RepositorySubject:
    """The normalized, assimilated projection of a repository under acceptance."""

    repository_id: str
    epic_id: str
    context_assimilated: bool = False
    constitution_discovered: bool = False
    discovered_repositories: tuple[str, ...] = ()
    units: tuple[UnitRecord, ...] = ()
    dependencies: tuple[DependencyRecord, ...] = ()
    reuse: tuple[ReuseRecord, ...] = ()
    inventory: RepositoryInventory = field(default_factory=RepositoryInventory)
    coverage: CoverageProfile = field(default_factory=CoverageProfile)
    integrations: tuple[IntegrationRecord, ...] = ()
    architecture_violations: tuple[str, ...] = ()
    health: RepositoryHealth = field(default_factory=RepositoryHealth)
    freeze_blockers: tuple[str, ...] = ()

    @classmethod
    def from_mapping(cls, facts: Mapping[str, Any]) -> RepositorySubject:
        """Assimilate a repository facts mapping into a normalized subject.

        This is the acceptance engine's *context assimilation* entry point: it
        projects a plain, serializable facts mapping (as produced by repository
        discovery) into the typed subject the gates evaluate.

        Raises:
            RepositorySubjectError: if ``facts`` is not a mapping, or is missing the
                mandatory ``repository_id`` / ``epic_id`` identity.
        """
        if not isinstance(facts, Mapping):
            raise RepositorySubjectError("repository facts must be a mapping")
        repository_id = facts.get("repository_id")
        epic_id = facts.get("epic_id")
        if not repository_id or not epic_id:
            raise RepositorySubjectError(
                "repository facts require a repository_id and an epic_id",
                repository_id=repository_id,
                epic_id=epic_id,
            )
        return cls(
            repository_id=str(repository_id),
            epic_id=str(epic_id),
            context_assimilated=bool(facts.get("context_assimilated", False)),
            constitution_discovered=bool(facts.get("constitution_discovered", False)),
            discovered_repositories=_str_tuple(facts.get("discovered_repositories")),
            units=tuple(_unit(u) for u in _seq(facts.get("units"))),
            dependencies=tuple(_dependency(d) for d in _seq(facts.get("dependencies"))),
            reuse=tuple(_reuse(r) for r in _seq(facts.get("reuse"))),
            inventory=_inventory(facts.get("inventory")),
            coverage=_coverage(facts.get("coverage")),
            integrations=tuple(_integration(i) for i in _seq(facts.get("integrations"))),
            architecture_violations=_str_tuple(facts.get("architecture_violations")),
            health=_health(facts.get("health")),
            freeze_blockers=_str_tuple(facts.get("freeze_blockers")),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "repository_id": self.repository_id,
            "epic_id": self.epic_id,
            "context_assimilated": self.context_assimilated,
            "constitution_discovered": self.constitution_discovered,
            "discovered_repositories": list(self.discovered_repositories),
            "units": [u.to_dict() for u in self.units],
            "dependencies": [d.to_dict() for d in self.dependencies],
            "reuse": [r.to_dict() for r in self.reuse],
            "inventory": self.inventory.to_dict(),
            "coverage": self.coverage.to_dict(),
            "integrations": [i.to_dict() for i in self.integrations],
            "architecture_violations": list(self.architecture_violations),
            "health": self.health.to_dict(),
            "freeze_blockers": list(self.freeze_blockers),
        }

    def digest(self) -> str:
        """The deterministic content hash of the assimilated subject (evidence ref)."""
        return content_hash(self.to_dict())


# ---------------------------------------------------------------------------
# the immutable, content-addressed acceptance certificate
# ---------------------------------------------------------------------------
@dataclass(frozen=True, slots=True)
class AcceptanceRecord:
    """An immutable, content-addressed Repository Acceptance Certificate.

    The record is **immutable** (frozen) and **self-verifying**: its
    ``content_sha256`` is the canonical hash of every field but the id and the hash
    itself, and ``acceptance_id`` is derived from that hash — so any mutation is
    detectable via :meth:`verify_integrity`. It references the reproducible subject
    digest as evidence, embeds the EC-1 provisional-state disclosure, and asserts
    ``ENGINEERING-EXECUTION-ONLY`` authority (acceptance confers no constitutional
    finality — DE-05 / IP-01).
    """

    acceptance_id: str
    repository_id: str
    epic_id: str
    status: AcceptanceStatus
    standard: str
    standard_version: str
    authority: str
    evidence_ref: str
    gates: tuple[AcceptanceFinding, ...]
    disclosure: Mapping[str, Any]
    content_sha256: str

    @staticmethod
    def _core(
        *,
        repository_id: str,
        epic_id: str,
        status: AcceptanceStatus,
        standard: str,
        standard_version: str,
        authority: str,
        evidence_ref: str,
        gates: tuple[AcceptanceFinding, ...],
        disclosure: Mapping[str, Any],
    ) -> dict[str, Any]:
        """The canonical, hashable core of a record (excludes id + content hash)."""
        return {
            "repository_id": repository_id,
            "epic_id": epic_id,
            "status": status.value,
            "standard": standard,
            "standard_version": standard_version,
            "authority": authority,
            "evidence_ref": evidence_ref,
            "gates": [g.to_dict() for g in gates],
            "disclosure": dict(disclosure),
        }

    @classmethod
    def create(
        cls,
        *,
        repository_id: str,
        epic_id: str,
        status: AcceptanceStatus,
        evidence_ref: str,
        gates: tuple[AcceptanceFinding, ...],
        disclosure: Mapping[str, Any],
        standard: str = ACCEPTANCE_STANDARD,
        standard_version: str = ACCEPTANCE_STANDARD_VERSION,
        authority: str = ACCEPTANCE_AUTHORITY,
    ) -> AcceptanceRecord:
        """Assemble an immutable, content-addressed :class:`AcceptanceRecord`."""
        core = cls._core(
            repository_id=repository_id,
            epic_id=epic_id,
            status=status,
            standard=standard,
            standard_version=standard_version,
            authority=authority,
            evidence_ref=evidence_ref,
            gates=gates,
            disclosure=disclosure,
        )
        digest = content_hash(core)
        acceptance_id = f"UCOS-ACCEPT-{epic_id}-{digest[:16]}"
        return cls(
            acceptance_id=acceptance_id,
            repository_id=repository_id,
            epic_id=epic_id,
            status=status,
            standard=standard,
            standard_version=standard_version,
            authority=authority,
            evidence_ref=evidence_ref,
            gates=gates,
            disclosure=dict(disclosure),
            content_sha256=digest,
        )

    @property
    def accepted(self) -> bool:
        return self.status is AcceptanceStatus.ACCEPTED

    def recompute_hash(self) -> str:
        """Recompute the content hash from the current field values."""
        return content_hash(
            self._core(
                repository_id=self.repository_id,
                epic_id=self.epic_id,
                status=self.status,
                standard=self.standard,
                standard_version=self.standard_version,
                authority=self.authority,
                evidence_ref=self.evidence_ref,
                gates=self.gates,
                disclosure=self.disclosure,
            )
        )

    def verify_integrity(self) -> bool:
        """Return True iff the stored content hash matches a recomputation."""
        return self.recompute_hash() == self.content_sha256

    def require_integrity(self) -> None:
        """Raise :class:`AcceptanceIntegrityError` if the record was mutated."""
        if not self.verify_integrity():
            raise AcceptanceIntegrityError(
                "acceptance record integrity check failed (content mutated)",
                acceptance_id=self.acceptance_id,
                expected=self.content_sha256,
                actual=self.recompute_hash(),
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "acceptance_id": self.acceptance_id,
            "repository_id": self.repository_id,
            "epic_id": self.epic_id,
            "status": self.status.value,
            "accepted": self.accepted,
            "standard": self.standard,
            "standard_version": self.standard_version,
            "authority": self.authority,
            "evidence_ref": self.evidence_ref,
            "gates": [g.to_dict() for g in self.gates],
            "disclosure": dict(self.disclosure),
            "content_sha256": self.content_sha256,
        }


# ---------------------------------------------------------------------------
# assimilation helpers (context assimilation of raw facts)
# ---------------------------------------------------------------------------
def _seq(value: Any) -> Sequence[Any]:
    """Return ``value`` as a sequence of records (empty for None/scalars/mappings)."""
    if isinstance(value, Sequence) and not isinstance(value, str | bytes):
        return value
    return ()


def _str_tuple(value: Any) -> tuple[str, ...]:
    return tuple(str(item) for item in _seq(value))


def _unit(raw: Mapping[str, Any]) -> UnitRecord:
    return UnitRecord(
        unit_id=str(raw.get("unit_id", "")),
        owner=(str(raw["owner"]) if raw.get("owner") else None),
        implemented=bool(raw.get("implemented", False)),
        validated=bool(raw.get("validated", False)),
        certified=bool(raw.get("certified", False)),
        registered=bool(raw.get("registered", False)),
        traceability=_str_tuple(raw.get("traceability")),
    )


def _dependency(raw: Mapping[str, Any]) -> DependencyRecord:
    return DependencyRecord(
        dependency_id=str(raw.get("dependency_id", "")),
        resolved=bool(raw.get("resolved", False)),
        pinned=bool(raw.get("pinned", False)),
    )


def _reuse(raw: Mapping[str, Any]) -> ReuseRecord:
    return ReuseRecord(
        capability=str(raw.get("capability", "")),
        reused=bool(raw.get("reused", False)),
        justified=bool(raw.get("justified", False)),
    )


def _integration(raw: Mapping[str, Any]) -> IntegrationRecord:
    return IntegrationRecord(
        point=str(raw.get("point", "")),
        satisfied=bool(raw.get("satisfied", False)),
    )


def _inventory(raw: Any) -> RepositoryInventory:
    if not isinstance(raw, Mapping):
        return RepositoryInventory()
    responsibilities = {
        str(r): _str_tuple(owners) for r, owners in dict(raw.get("responsibilities") or {}).items()
    }
    content_hashes = {
        str(aid): str(digest) for aid, digest in dict(raw.get("content_hashes") or {}).items()
    }
    return RepositoryInventory(
        expected=_str_tuple(raw.get("expected")),
        present=_str_tuple(raw.get("present")),
        content_hashes=content_hashes,
        responsibilities=responsibilities,
    )


def _coverage(raw: Any) -> CoverageProfile:
    dimensions = tuple(
        CoverageDimension(
            name=str(d.get("name", "")),
            covered=int(d.get("covered", 0)),
            total=int(d.get("total", 0)),
        )
        for d in _seq(raw)
    )
    return CoverageProfile(dimensions=dimensions)


def _health(raw: Any) -> RepositoryHealth:
    if not isinstance(raw, Mapping):
        return RepositoryHealth()
    return RepositoryHealth(
        critical_issues=_str_tuple(raw.get("critical_issues")),
        warnings=_str_tuple(raw.get("warnings")),
    )


__all__ = [
    "ACCEPTANCE_CONTRACT_VERSION",
    "ACCEPTANCE_STANDARD",
    "ACCEPTANCE_STANDARD_VERSION",
    "ACCEPTANCE_AUTHORITY",
    "REQUIRED_TRACE_STAGES",
    "canonical_json",
    "content_hash",
    "GateSeverity",
    "GateStatus",
    "AcceptanceStatus",
    "CoverageDimension",
    "CoverageProfile",
    "UnitRecord",
    "DependencyRecord",
    "ReuseRecord",
    "IntegrationRecord",
    "RepositoryInventory",
    "RepositoryHealth",
    "AcceptanceFinding",
    "RepositorySubject",
    "AcceptanceRecord",
]
