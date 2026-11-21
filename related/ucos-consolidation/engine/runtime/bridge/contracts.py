"""EPIC-RTE-003 — Runtime Bridge value types (Repository Execution Bridge).

The immutable, deterministic records the Runtime Bridge produces as it threads a
repository through the runtime lifecycle. Every type is **frozen, slotted,
deterministic, and serialisable** and holds no runtime state: it is a faithful
projection of the records the reused engines already produced (a
:class:`~engine.runtime.execution.platform.ExecutionResult`, a
:class:`~engine.validation.contracts.ValidationReport`, a
:class:`~engine.certification.engine.CertificationDecision`, a
:class:`~engine.acceptance.engine.AcceptanceDecision`, and a
:class:`~engine.knowledge.cko.CanonicalKnowledgeObject`).

    * :class:`UnitAssurance` — the per-universe assurance projection: the modelled
      execution state of one composed universe together with the validation and
      certification records of its assembled runtime unit.
    * :class:`RepositoryExecutionRecord` — the single, canonical, content-addressed
      record of one repository execution: composition → execution → validation →
      certification → acceptance → recorded knowledge evidence. It is the sole
      deliverable of the bridge and is byte-reproducible for identical inputs
      (IMP-007 §5): its ``content_sha256`` hashes every field but the id and the
      hash itself, and ``bridge_id`` is derived from that hash, so any mutation is
      detectable via :meth:`~RepositoryExecutionRecord.verify_integrity`.

The bridge implements only integration: these records **reference and re-project**
the reused engines' own records; they never re-derive a determination.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from engine.knowledge.model import content_hash

if TYPE_CHECKING:  # pragma: no cover - typing only, avoids import cycles
    from engine.acceptance.engine import AcceptanceDecision
    from engine.acceptance.evidence import AcceptanceEvidence
    from engine.certification.engine import CertificationDecision
    from engine.certification.evidence import CertificationEvidence
    from engine.knowledge.cko import CanonicalKnowledgeObject
    from engine.runtime.composition import RuntimeComposition
    from engine.runtime.execution.platform import ExecutionResult
    from engine.validation.contracts import ValidationReport
    from engine.validation.evidence import ValidationEvidence

#: The deterministic Repository Execution Bridge record format.
BRIDGE_RECORD_FORMAT = "ucos-runtime-bridge/1.0.0"

#: The engineering-execution authority the bridge asserts (never constitutional).
BRIDGE_AUTHORITY = "ENGINEERING-EXECUTION-ONLY"


@dataclass(frozen=True, slots=True)
class UnitAssurance:
    """The per-universe assurance projection produced by the bridge.

    Pairs the modelled execution outcome of one composed universe with the
    validation report and certification decision of its assembled runtime unit —
    every record reused verbatim from the Validation and Certification engines.
    """

    universe_id: str
    runtime_id: str
    blueprint_id: str
    execution_status: str
    validation: ValidationReport
    validation_evidence: ValidationEvidence
    certification: CertificationDecision
    certification_evidence: CertificationEvidence

    @property
    def validated(self) -> bool:
        """True iff the unit's validation report passed (no blocking failure)."""
        return self.validation.accepted

    @property
    def certified(self) -> bool:
        """True iff the unit was certified (no blocking certification failure)."""
        return self.certification.certified

    def evidence_refs(self) -> tuple[str, ...]:
        """The reproducible validation + certification evidence references (sorted)."""
        return (
            f"validation:{self.validation.target_id}:"
            f"{content_hash(self.validation_evidence.to_dict())}",
            f"certification:{self.certification.certification_id}:"
            f"{self.certification_evidence.content_sha256()}",
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "universe_id": self.universe_id,
            "runtime_id": self.runtime_id,
            "blueprint_id": self.blueprint_id,
            "execution_status": self.execution_status,
            "validated": self.validated,
            "certified": self.certified,
            "validation": self.validation.to_dict(),
            "validation_evidence": self.validation_evidence.to_dict(),
            "certification": self.certification.to_dict(),
            "certification_evidence": self.certification_evidence.to_dict(),
        }


@dataclass(frozen=True, slots=True)
class RepositoryExecutionRecord:
    """The single, canonical, content-addressed record of a repository execution.

    It threads the repository lifecycle through the reused runtime capabilities —
    composition, execution, per-unit validation and certification, repository
    acceptance, and the recorded knowledge evidence object — into one immutable,
    auditable, byte-reproducible structure. Acceptance confers no constitutional
    finality: the record asserts ``ENGINEERING-EXECUTION-ONLY`` authority and
    embeds the EC-1 provisional-state disclosure (DE-05 / IP-01).
    """

    bridge_id: str
    repository_id: str
    epic_id: str
    composition: RuntimeComposition
    execution: ExecutionResult
    assurances: tuple[UnitAssurance, ...]
    acceptance: AcceptanceDecision
    acceptance_evidence: AcceptanceEvidence
    knowledge_object: CanonicalKnowledgeObject
    disclosure: dict[str, Any]
    content_sha256: str

    # -- identity / status -----------------------------------------------------

    @property
    def composition_id(self) -> str:
        return self.composition.composition_id

    @property
    def run_id(self) -> str:
        return self.execution.run_id

    @property
    def status(self) -> str:
        """The aggregate modelled execution status of the run."""
        return self.execution.status

    @property
    def accepted(self) -> bool:
        """True iff the repository acceptance gate accepted the repository."""
        return self.acceptance.accepted

    @property
    def validated(self) -> bool:
        """True iff every composed unit passed validation."""
        return all(a.validated for a in self.assurances)

    @property
    def certified(self) -> bool:
        """True iff every composed unit was certified."""
        return all(a.certified for a in self.assurances)

    @property
    def knowledge_id(self) -> str:
        """The id of the recorded knowledge evidence object."""
        return self.knowledge_object.cko_id

    def evidence_refs(self) -> tuple[str, ...]:
        """Every evidence reference recorded into knowledge (the single source)."""
        return self.knowledge_object.evidence

    # -- construction ----------------------------------------------------------

    @staticmethod
    def _core(
        *,
        repository_id: str,
        epic_id: str,
        composition: RuntimeComposition,
        execution: ExecutionResult,
        assurances: tuple[UnitAssurance, ...],
        acceptance: AcceptanceDecision,
        acceptance_evidence: AcceptanceEvidence,
        knowledge_object: CanonicalKnowledgeObject,
        disclosure: dict[str, Any],
    ) -> dict[str, Any]:
        """The canonical, hashable core (every field except the id and the hash)."""
        return {
            "bridge_record_format": BRIDGE_RECORD_FORMAT,
            "authority": BRIDGE_AUTHORITY,
            "repository_id": repository_id,
            "epic_id": epic_id,
            "status": execution.status,
            "accepted": acceptance.accepted,
            "composition_id": composition.composition_id,
            "run_id": execution.run_id,
            "composition": composition.to_dict(),
            "execution": execution.to_dict(),
            "assurances": [a.to_dict() for a in assurances],
            "acceptance": acceptance.to_dict(),
            "acceptance_evidence": acceptance_evidence.to_dict(),
            "knowledge_object": knowledge_object.to_dict(),
            "provisional_state_disclosure": disclosure,
        }

    @classmethod
    def create(
        cls,
        *,
        repository_id: str,
        epic_id: str,
        composition: RuntimeComposition,
        execution: ExecutionResult,
        assurances: tuple[UnitAssurance, ...],
        acceptance: AcceptanceDecision,
        acceptance_evidence: AcceptanceEvidence,
        knowledge_object: CanonicalKnowledgeObject,
        disclosure: dict[str, Any],
    ) -> RepositoryExecutionRecord:
        """Assemble and seal a content-addressed :class:`RepositoryExecutionRecord`."""
        core = cls._core(
            repository_id=repository_id,
            epic_id=epic_id,
            composition=composition,
            execution=execution,
            assurances=assurances,
            acceptance=acceptance,
            acceptance_evidence=acceptance_evidence,
            knowledge_object=knowledge_object,
            disclosure=disclosure,
        )
        content_sha256 = content_hash(core)
        return cls(
            bridge_id=f"UCOS-RTE-BRIDGE-{content_sha256[:16]}",
            repository_id=repository_id,
            epic_id=epic_id,
            composition=composition,
            execution=execution,
            assurances=assurances,
            acceptance=acceptance,
            acceptance_evidence=acceptance_evidence,
            knowledge_object=knowledge_object,
            disclosure=disclosure,
            content_sha256=content_sha256,
        )

    # -- integrity -------------------------------------------------------------

    def recompute_hash(self) -> str:
        """Recompute the content hash from the current field values."""
        return content_hash(
            self._core(
                repository_id=self.repository_id,
                epic_id=self.epic_id,
                composition=self.composition,
                execution=self.execution,
                assurances=self.assurances,
                acceptance=self.acceptance,
                acceptance_evidence=self.acceptance_evidence,
                knowledge_object=self.knowledge_object,
                disclosure=self.disclosure,
            )
        )

    def verify_integrity(self) -> bool:
        """Return True iff the stored content hash matches a recomputation."""
        return bool(self.content_sha256) and self.recompute_hash() == self.content_sha256

    def require_integrity(self) -> None:
        """Raise :class:`RuntimeBridgeError` if the record was mutated."""
        if not self.verify_integrity():
            from engine.runtime.bridge.errors import RuntimeBridgeError

            raise RuntimeBridgeError(
                "repository execution bridge record integrity check failed",
                bridge_id=self.bridge_id,
                expected=self.content_sha256,
                actual=self.recompute_hash(),
            )

    def to_dict(self) -> dict[str, Any]:
        """A complete, auditable, JSON-serialisable view of the bridge record."""
        payload = self._core(
            repository_id=self.repository_id,
            epic_id=self.epic_id,
            composition=self.composition,
            execution=self.execution,
            assurances=self.assurances,
            acceptance=self.acceptance,
            acceptance_evidence=self.acceptance_evidence,
            knowledge_object=self.knowledge_object,
            disclosure=self.disclosure,
        )
        payload["bridge_id"] = self.bridge_id
        payload["content_sha256"] = self.content_sha256
        return payload


__all__ = [
    "BRIDGE_RECORD_FORMAT",
    "BRIDGE_AUTHORITY",
    "UnitAssurance",
    "RepositoryExecutionRecord",
]
