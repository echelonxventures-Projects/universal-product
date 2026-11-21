"""UCOS-EPIC-014 — Repository Intelligence contracts (Terminal T5).

The immutable, deterministic value types Repository Intelligence speaks. Every type is
**immutable, typed, deterministic, and serializable** and holds no runtime state, so an
identical repository substrate yields a byte-identical
:class:`RepositoryIntelligenceReport` and content hash (IMP-007 §5) — no wall-clock or
ambient state leaks into any identity.

Reuse over reinvention (TP-05), stated explicitly because this subsystem's own mandate is
to forbid duplication:

    * hashing/serialization — **reused verbatim** from
      :mod:`platform.foundation.contracts` (:func:`content_hash`); no new hash is defined.
    * ``Severity`` / ``FindingStatus`` / ``Verdict`` — **reused verbatim** from
      :mod:`platform.validation_intelligence.contracts` (UCOS-EPIC-013); the fail-closed
      outcome vocabulary already exists at EC-2 and is not re-declared here.
    * the provisional-state disclosure — **reused verbatim** from
      :mod:`engine.runtime.disclosure` (DE-05 / IP-01).

What is genuinely new is the *repository-intelligence vocabulary*: the eight
:class:`DiscoveryDimension` s, the :class:`RepositoryUnit` / :class:`CapabilityRecord` /
:class:`ReuseAssessment` / :class:`DependencyEdge` / :class:`OwnershipRecord` inventories,
the :class:`Finding` type the gap/conflict/duplicate detectors emit, the
:class:`Recommendation` the recommendation engine ranks, and the
:class:`RepositoryIntelligenceReport` that binds them into one content-addressed answer.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import Enum
from platform.foundation.contracts import content_hash
from platform.repository_intelligence.errors import DiscoveryError
from platform.validation_intelligence.contracts import FindingStatus, Severity, Verdict
from typing import TYPE_CHECKING, Any

from engine.runtime.disclosure import build_disclosure

if TYPE_CHECKING:  # pragma: no cover - typing only, avoids an import cycle
    from platform.repository_intelligence.graph import RepositoryGraph

#: The semantic version of the Repository Intelligence contract surface (AR-03/PL-05).
REPOSITORY_INTELLIGENCE_CONTRACT_VERSION = "1.0.0"

#: The stable programme identity of the Repository Intelligence subsystem (Terminal T5).
REPOSITORY_INTELLIGENCE_PROGRAMME = "UCOS-RPI-000001"

#: Format identifiers for the Repository Intelligence deliverables.
INTELLIGENCE_REPORT_FORMAT = "ucos-repository-intelligence-report/1.0.0"
DEPENDENCY_GRAPH_FORMAT = "ucos-repository-dependency-graph/1.0.0"
RECOMMENDATION_FORMAT = "ucos-repository-recommendation/1.0.0"
VALIDATION_REPORT_FORMAT = "ucos-repository-validation-report/1.0.0"
CERTIFICATE_FORMAT = "ucos-repository-intelligence-certificate/1.0.0"
EVIDENCE_FORMAT = "ucos-repository-intelligence-evidence/1.0.0"

#: The certification standard the certificate attests against (record-only, IMP-007 §13).
CERTIFICATION_STANDARD = "UCOS-REPOSITORY-INTELLIGENCE-STANDARD"
CERTIFICATION_STANDARD_VERSION = "1.0.0"

#: Repository Intelligence confers no constitutional authority (DE-05 / IP-01): it
#: derives truth from repository evidence and records engineering readiness only.
#: Embedded verbatim in every report, certificate and evidence record.
REPOSITORY_INTELLIGENCE_AUTHORITY = "ENGINEERING-EXECUTION-ONLY"

#: Repository evidence remains the only authority; everything this subsystem emits is
#: derived. Mirrors the UCOS-RIE-001 stance so the two intelligence producers agree.
DERIVED_TRUTH = "NONE (derived truth)"


class DiscoveryDimension(str, Enum):
    """The eight repository-discovery dimensions, in canonical (mission) order."""

    REPOSITORY = "repository"
    CAPABILITY = "capability"
    REUSE = "reuse"
    DEPENDENCY = "dependency"
    GAP = "gap"
    CONFLICT = "conflict"
    DUPLICATE = "duplicate"
    OWNERSHIP = "ownership"

    @classmethod
    def parse(cls, value: Any) -> DiscoveryDimension:
        """Parse a dimension, raising :class:`DiscoveryError` on an unknown one."""
        try:
            return cls(value)
        except ValueError as exc:
            raise DiscoveryError(
                "unknown repository-discovery dimension",
                dimension=value,
                supported=[d.value for d in cls],
            ) from exc

    @property
    def order(self) -> int:
        """The canonical (declaration-order) index, for deterministic ordering."""
        return _DIMENSION_ORDER[self]


_DIMENSION_ORDER: dict[DiscoveryDimension, int] = {d: i for i, d in enumerate(DiscoveryDimension)}


class UnitKind(str, Enum):
    """The kind of repository unit discovered by Repository Discovery."""

    CODE_ROOT = "code_root"
    CODE_CAPABILITY = "code_capability"
    CONSTITUTIONAL_ZONE = "constitutional_zone"
    EVIDENCE_STORE = "evidence_store"
    ENTRY_POINT = "entry_point"


class ReuseProof(str, Enum):
    """Whether a capability's reuse disposition is *proven* by the substrate.

    A reuse directive (``REUSE/COMPOSE`` …) is a *policy*; proof is evidence. A
    capability that other capabilities actually import is ``PROVEN``; one reachable only
    through a published console script is ``ENTRY_POINT``; one that nothing imports and
    nothing publishes is ``UNPROVEN`` (a reuse *opportunity*, not a defect).
    """

    PROVEN = "proven"
    ENTRY_POINT = "entry_point"
    UNPROVEN = "unproven"


class EdgeKind(str, Enum):
    """The kind of relationship a :class:`DependencyEdge` records."""

    IMPORTS = "imports"
    CONTAINS = "contains"
    PUBLISHES = "publishes"


class RecommendationAction(str, Enum):
    """The action a :class:`Recommendation` prescribes (never 'build a duplicate')."""

    REUSE = "reuse"
    EXTEND = "extend"
    COMPOSE = "compose"
    REPAIR = "repair"
    REGISTER = "register"
    CREATE = "create"
    NO_ACTION = "no_action"


class Determination(str, Enum):
    """The fail-closed determination of a repository-intelligence certification."""

    CERTIFIED_INTELLIGENT = "CERTIFIED-INTELLIGENT"
    NOT_CERTIFIED = "NOT-CERTIFIED"


# ---------------------------------------------------------------------------
# discovered inventories
# ---------------------------------------------------------------------------
@dataclass(frozen=True, slots=True)
class RepositoryUnit:
    """A unit of the repository discovered by Repository Discovery.

    ``name`` is the unit's canonical identity (a dotted capability path, a top-level
    zone name, or a published console-script name); ``location`` is repository-relative.
    """

    name: str
    kind: UnitKind
    location: str
    tracked_files: int = 0
    loc: int = 0
    detail: str = ""

    @property
    def unit_id(self) -> str:
        """The deterministic, content-addressed identity of the unit."""
        return f"UCOS-RPIU-{content_hash(self.core())[:16]}"

    def core(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "kind": self.kind.value,
            "location": self.location,
            "tracked_files": self.tracked_files,
            "loc": self.loc,
        }

    def to_dict(self) -> dict[str, Any]:
        return {"unit_id": self.unit_id, **self.core(), "detail": self.detail}


@dataclass(frozen=True, slots=True)
class CapabilityRecord:
    """A capability the repository already provides.

    Capability *identity, category, authority and reuse policy* are **not derived here**:
    they are composed from the existing UCOS-RIE-001 capability catalog (see
    :mod:`platform.repository_intelligence.substrate`), which is the repository's
    established owner of capability discovery. This record adds only the
    repository-intelligence facts RIE does not carry: the module/symbol surface, the
    importer set, and the reuse proof.
    """

    name: str
    location: str
    category: str
    authority: str
    reuse_directive: str
    replacement_prohibited: bool
    implementation_status: str
    description: str = ""
    source: str = "rie-catalog"
    modules: int = 0
    symbols: int = 0
    test_modules: int = 0
    present_on_disk: bool = True

    @property
    def capability_id(self) -> str:
        return f"UCOS-RPIC-{content_hash(self.core())[:16]}"

    def core(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "location": self.location,
            "category": self.category,
            "authority": self.authority,
            "reuse_directive": self.reuse_directive,
            "replacement_prohibited": self.replacement_prohibited,
            "implementation_status": self.implementation_status,
            "source": self.source,
            "modules": self.modules,
            "symbols": self.symbols,
            "test_modules": self.test_modules,
            "present_on_disk": self.present_on_disk,
        }

    def to_dict(self) -> dict[str, Any]:
        return {"capability_id": self.capability_id, **self.core(), "description": self.description}


@dataclass(frozen=True, slots=True)
class ReuseAssessment:
    """Whether an existing capability's reuse disposition is proven by the substrate.

    Distinct from :class:`engine.acceptance.contracts.ReuseRecord`, which records whether
    a *newly built* capability justified itself. This assessment is the inverse and
    complementary question — is what already exists actually being reused — and is what
    makes ``never duplicate capabilities`` enforceable rather than aspirational.
    """

    capability: str
    reuse_directive: str
    replacement_prohibited: bool
    proof: ReuseProof
    importers: tuple[str, ...] = ()
    published_entry_points: tuple[str, ...] = ()

    @property
    def reused(self) -> bool:
        """True iff the substrate proves the capability is consumed by something."""
        return self.proof is not ReuseProof.UNPROVEN

    def to_dict(self) -> dict[str, Any]:
        return {
            "capability": self.capability,
            "reuse_directive": self.reuse_directive,
            "replacement_prohibited": self.replacement_prohibited,
            "proof": self.proof.value,
            "reused": self.reused,
            "importers": list(self.importers),
            "published_entry_points": list(self.published_entry_points),
        }


@dataclass(frozen=True, slots=True)
class DependencyEdge:
    """A directed, weighted dependency edge between two repository nodes."""

    source: str
    target: str
    kind: EdgeKind = EdgeKind.IMPORTS
    weight: int = 1
    modules: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "target": self.target,
            "kind": self.kind.value,
            "weight": self.weight,
            "modules": list(self.modules),
        }


@dataclass(frozen=True, slots=True)
class OwnershipRecord:
    """The derived owner of a repository unit, with the basis that establishes it.

    Ownership is *derived from the substrate*, never asserted: a declared terminal or
    programme token in the capability's own package docstring outranks a layer-policy
    default, and a unit with two conflicting declared owners is reported as such rather
    than silently resolved.
    """

    subject: str
    owner: str
    basis: str
    confidence: str
    candidates: tuple[str, ...] = ()

    #: The sentinel owner for a unit whose owner the substrate cannot establish.
    UNOWNED = "UNOWNED"

    @property
    def owned(self) -> bool:
        return self.owner != OwnershipRecord.UNOWNED

    @property
    def contested(self) -> bool:
        """True iff more than one distinct declared owner was found for the subject."""
        return len(self.candidates) > 1

    def to_dict(self) -> dict[str, Any]:
        return {
            "subject": self.subject,
            "owner": self.owner,
            "basis": self.basis,
            "confidence": self.confidence,
            "owned": self.owned,
            "contested": self.contested,
            "candidates": list(self.candidates),
        }


# ---------------------------------------------------------------------------
# findings (the gap / conflict / duplicate discoveries)
# ---------------------------------------------------------------------------
@dataclass(frozen=True, slots=True)
class Finding:
    """The immutable, deterministic outcome of one repository-intelligence check.

    A finding is *always data* — the detectors never raise for a legitimate negative
    result. ``code`` is a stable, machine-consumable finding type (e.g.
    ``capability-unregistered-coverage``); ``subject`` names what the finding is about.
    """

    code: str
    dimension: DiscoveryDimension
    severity: Severity
    status: FindingStatus
    subject: str
    message: str = ""
    details: Mapping[str, Any] = field(default_factory=dict)

    @property
    def finding_id(self) -> str:
        return f"UCOS-RPIF-{content_hash(self.core())[:16]}"

    @property
    def passed(self) -> bool:
        return self.status is FindingStatus.PASS

    @property
    def failed(self) -> bool:
        return self.status is FindingStatus.FAIL

    @property
    def is_blocking_failure(self) -> bool:
        return self.failed and self.severity is Severity.BLOCKING

    @property
    def is_advisory_failure(self) -> bool:
        return self.failed and self.severity is Severity.ADVISORY

    def core(self) -> dict[str, Any]:
        """The canonical, hashable core of the finding (excludes volatile detail)."""
        return {
            "code": self.code,
            "dimension": self.dimension.value,
            "severity": self.severity.value,
            "status": self.status.value,
            "subject": self.subject,
            "message": self.message,
        }

    def to_dict(self) -> dict[str, Any]:
        return {"finding_id": self.finding_id, **self.core(), "details": dict(self.details)}


def sort_findings(findings: tuple[Finding, ...]) -> tuple[Finding, ...]:
    """Return ``findings`` in the canonical deterministic order (dimension, code, subject)."""
    return tuple(sorted(findings, key=lambda f: (f.dimension.order, f.code, f.subject)))


@dataclass(frozen=True, slots=True)
class DimensionResult:
    """The ordered, deterministic aggregate of one discovery dimension."""

    dimension: DiscoveryDimension
    verdict: Verdict
    findings: tuple[Finding, ...]

    @classmethod
    def create(
        cls, dimension: DiscoveryDimension, findings: tuple[Finding, ...]
    ) -> DimensionResult:
        """Aggregate ``findings``; verdict FAIL iff a blocking check failed (fail-closed)."""
        ordered = sort_findings(findings)
        verdict = Verdict.FAIL if any(f.is_blocking_failure for f in ordered) else Verdict.PASS
        return cls(dimension=dimension, verdict=verdict, findings=ordered)

    @property
    def passed(self) -> bool:
        return self.verdict is Verdict.PASS

    def blocking_failures(self) -> tuple[str, ...]:
        return tuple(f.code for f in self.findings if f.is_blocking_failure)

    def advisory_failures(self) -> tuple[str, ...]:
        return tuple(f.code for f in self.findings if f.is_advisory_failure)

    def counts(self) -> dict[str, int]:
        passed = sum(1 for f in self.findings if f.passed)
        return {
            "total": len(self.findings),
            "passed": passed,
            "failed": len(self.findings) - passed,
            "blocking_failed": len(self.blocking_failures()),
            "advisory_failed": len(self.advisory_failures()),
        }

    def core(self) -> dict[str, Any]:
        return {
            "dimension": self.dimension.value,
            "verdict": self.verdict.value,
            "findings": [f.core() for f in self.findings],
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "dimension": self.dimension.value,
            "verdict": self.verdict.value,
            "passed": self.passed,
            "counts": self.counts(),
            "blocking_failures": list(self.blocking_failures()),
            "advisory_failures": list(self.advisory_failures()),
            "findings": [f.to_dict() for f in self.findings],
        }


# ---------------------------------------------------------------------------
# recommendations
# ---------------------------------------------------------------------------
@dataclass(frozen=True, slots=True)
class Recommendation:
    """A ranked, evidence-cited action derived from the intelligence report.

    ``priority`` is a small integer where lower is more urgent; it is *derived* from the
    severity and dimension of the finding that produced the recommendation, never
    assigned by hand. Every recommendation cites the finding codes that justify it, so
    no recommendation exists without evidence.
    """

    action: RecommendationAction
    subject: str
    priority: int
    rationale: str
    target: str = ""
    evidence: tuple[str, ...] = ()

    @property
    def recommendation_id(self) -> str:
        return f"UCOS-RPIR-{content_hash(self.core())[:16]}"

    def core(self) -> dict[str, Any]:
        return {
            "action": self.action.value,
            "subject": self.subject,
            "priority": self.priority,
            "rationale": self.rationale,
            "target": self.target,
            "evidence": list(self.evidence),
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "recommendation_format": RECOMMENDATION_FORMAT,
            "recommendation_id": self.recommendation_id,
            **self.core(),
        }


# ---------------------------------------------------------------------------
# the aggregate report
# ---------------------------------------------------------------------------
@dataclass(frozen=True, slots=True)
class RepositoryIntelligenceReport:
    """The content-addressed answer to all eight discovery questions at once.

    The report is a **pure function of the substrate**: ``report_sha256`` hashes only the
    substrate digest, the inventories, the graph digest and the dimension/finding cores —
    never volatile per-finding detail and never a wall-clock — so an identical repository
    state reproduces a byte-identical report. It asserts ``ENGINEERING-EXECUTION-ONLY``
    authority, records that repository evidence remains the only authority, and carries
    the EC-1 provisional-state disclosure (DE-05 / IP-01).
    """

    repository_id: str
    substrate_digest: str
    units: tuple[RepositoryUnit, ...]
    capabilities: tuple[CapabilityRecord, ...]
    reuse: tuple[ReuseAssessment, ...]
    ownership: tuple[OwnershipRecord, ...]
    graph: RepositoryGraph
    dimension_results: tuple[DimensionResult, ...]
    recommendations: tuple[Recommendation, ...]
    verdict: Verdict
    authority: str
    derived_from: str
    disclosure: Mapping[str, Any]
    report_sha256: str
    drift: Mapping[str, Any] = field(default_factory=dict)

    @staticmethod
    def _core(
        *,
        repository_id: str,
        substrate_digest: str,
        units: tuple[RepositoryUnit, ...],
        capabilities: tuple[CapabilityRecord, ...],
        reuse: tuple[ReuseAssessment, ...],
        ownership: tuple[OwnershipRecord, ...],
        graph_digest: str,
        dimension_results: tuple[DimensionResult, ...],
        recommendations: tuple[Recommendation, ...],
        verdict: Verdict,
        disclosure: Mapping[str, Any],
    ) -> dict[str, Any]:
        return {
            "repository_id": repository_id,
            "substrate_digest": substrate_digest,
            "units": [u.core() for u in units],
            "capabilities": [c.core() for c in capabilities],
            "reuse": [r.to_dict() for r in reuse],
            "ownership": [o.to_dict() for o in ownership],
            "graph_digest": graph_digest,
            "dimensions": [d.core() for d in dimension_results],
            "recommendations": [r.core() for r in recommendations],
            "verdict": verdict.value,
            "authority": REPOSITORY_INTELLIGENCE_AUTHORITY,
            "derived_from": DERIVED_TRUTH,
            "disclosure": dict(disclosure),
        }

    @classmethod
    def create(
        cls,
        *,
        repository_id: str,
        substrate_digest: str,
        units: tuple[RepositoryUnit, ...],
        capabilities: tuple[CapabilityRecord, ...],
        reuse: tuple[ReuseAssessment, ...],
        ownership: tuple[OwnershipRecord, ...],
        graph: RepositoryGraph,
        dimension_results: tuple[DimensionResult, ...],
        recommendations: tuple[Recommendation, ...],
        drift: Mapping[str, Any] | None = None,
    ) -> RepositoryIntelligenceReport:
        """Aggregate the eight dimensions into an immutable, content-addressed report."""
        ordered = tuple(sorted(dimension_results, key=lambda d: d.dimension.order))
        verdict = Verdict.FAIL if any(not d.passed for d in ordered) else Verdict.PASS
        disclosure = build_disclosure()
        core = cls._core(
            repository_id=repository_id,
            substrate_digest=substrate_digest,
            units=units,
            capabilities=capabilities,
            reuse=reuse,
            ownership=ownership,
            graph_digest=graph.digest(),
            dimension_results=ordered,
            recommendations=recommendations,
            verdict=verdict,
            disclosure=disclosure,
        )
        return cls(
            repository_id=repository_id,
            substrate_digest=substrate_digest,
            units=units,
            capabilities=capabilities,
            reuse=reuse,
            ownership=ownership,
            graph=graph,
            dimension_results=ordered,
            recommendations=recommendations,
            verdict=verdict,
            authority=REPOSITORY_INTELLIGENCE_AUTHORITY,
            derived_from=DERIVED_TRUTH,
            disclosure=disclosure,
            report_sha256=content_hash(core),
            drift=dict(drift or {}),
        )

    # -- accessors -------------------------------------------------------
    @property
    def passed(self) -> bool:
        return self.verdict is Verdict.PASS

    @property
    def all_findings(self) -> tuple[Finding, ...]:
        return tuple(f for result in self.dimension_results for f in result.findings)

    def result_for(self, dimension: DiscoveryDimension) -> DimensionResult:
        """Return the result for ``dimension``, or an empty passing result if absent."""
        for result in self.dimension_results:
            if result.dimension is dimension:
                return result
        return DimensionResult.create(dimension, ())

    def findings_of(self, dimension: DiscoveryDimension) -> tuple[Finding, ...]:
        return self.result_for(dimension).findings

    def failures_of(self, dimension: DiscoveryDimension) -> tuple[Finding, ...]:
        return tuple(f for f in self.findings_of(dimension) if f.failed)

    def dimension_verdicts(self) -> dict[str, str]:
        return {r.dimension.value: r.verdict.value for r in self.dimension_results}

    def blocking_failures(self) -> tuple[str, ...]:
        return tuple(f.code for f in self.all_findings if f.is_blocking_failure)

    def advisory_failures(self) -> tuple[str, ...]:
        return tuple(f.code for f in self.all_findings if f.is_advisory_failure)

    def unowned_units(self) -> tuple[str, ...]:
        return tuple(o.subject for o in self.ownership if not o.owned)

    def unproven_capabilities(self) -> tuple[str, ...]:
        return tuple(r.capability for r in self.reuse if not r.reused)

    def counts(self) -> dict[str, int]:
        findings = self.all_findings
        passed = sum(1 for f in findings if f.passed)
        return {
            "units": len(self.units),
            "capabilities": len(self.capabilities),
            "graph_nodes": len(self.graph.nodes),
            "graph_edges": len(self.graph.edges),
            "dimensions": len(self.dimension_results),
            "checks": len(findings),
            "passed": passed,
            "failed": len(findings) - passed,
            "blocking_failed": sum(1 for f in findings if f.is_blocking_failure),
            "advisory_failed": sum(1 for f in findings if f.is_advisory_failure),
            "recommendations": len(self.recommendations),
            "unowned": len(self.unowned_units()),
            "unproven_reuse": len(self.unproven_capabilities()),
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "report_format": INTELLIGENCE_REPORT_FORMAT,
            "contract_version": REPOSITORY_INTELLIGENCE_CONTRACT_VERSION,
            "programme": REPOSITORY_INTELLIGENCE_PROGRAMME,
            "repository_id": self.repository_id,
            "substrate_digest": self.substrate_digest,
            "verdict": self.verdict.value,
            "passed": self.passed,
            "counts": self.counts(),
            "dimension_verdicts": self.dimension_verdicts(),
            "blocking_failures": list(self.blocking_failures()),
            "advisory_failures": list(self.advisory_failures()),
            "units": [u.to_dict() for u in self.units],
            "capabilities": [c.to_dict() for c in self.capabilities],
            "reuse": [r.to_dict() for r in self.reuse],
            "ownership": [o.to_dict() for o in self.ownership],
            "graph": self.graph.to_dict(),
            "dimensions": [d.to_dict() for d in self.dimension_results],
            "recommendations": [r.to_dict() for r in self.recommendations],
            "drift": dict(self.drift),
            "authority": self.authority,
            "derived_from": self.derived_from,
            "disclosure": dict(self.disclosure),
            "report_sha256": self.report_sha256,
        }


__all__ = [
    "REPOSITORY_INTELLIGENCE_CONTRACT_VERSION",
    "REPOSITORY_INTELLIGENCE_PROGRAMME",
    "INTELLIGENCE_REPORT_FORMAT",
    "DEPENDENCY_GRAPH_FORMAT",
    "RECOMMENDATION_FORMAT",
    "VALIDATION_REPORT_FORMAT",
    "CERTIFICATE_FORMAT",
    "EVIDENCE_FORMAT",
    "CERTIFICATION_STANDARD",
    "CERTIFICATION_STANDARD_VERSION",
    "REPOSITORY_INTELLIGENCE_AUTHORITY",
    "DERIVED_TRUTH",
    "DiscoveryDimension",
    "UnitKind",
    "ReuseProof",
    "EdgeKind",
    "RecommendationAction",
    "Determination",
    "Severity",
    "FindingStatus",
    "Verdict",
    "RepositoryUnit",
    "CapabilityRecord",
    "ReuseAssessment",
    "DependencyEdge",
    "OwnershipRecord",
    "Finding",
    "sort_findings",
    "DimensionResult",
    "Recommendation",
    "RepositoryIntelligenceReport",
]
