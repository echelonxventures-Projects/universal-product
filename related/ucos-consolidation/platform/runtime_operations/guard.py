"""EC2-TASK-000166 — Runtime Operations Admission Guard (EC2-EPIC-012).

The deterministic, fail-closed **admission gate** enforcing the EC2-EPIC-012 core rule:
**only a CERTIFIED runtime unit may be deployed or rolled back**. Admission is a **pure
function** of the assembled :class:`~engine.runtime.assembly.RuntimeUnit` and the governing
:class:`~platform.certification.contracts.CertificationConsoleRecord` (consumed by
reference from the certified Certification Console, EC2-EPIC-011) — it consults no
wall-clock and no external state, so an identical unit + certification always yields an
identical :class:`AdmissionDecision` and an identical fingerprint (P5).

The guard evaluates an ordered, explicit set of admission criteria and is fail-closed: a
unit is admitted only when **every** criterion passes. A non-CERTIFIED unit, a
certification that does not govern this unit, a unit missing the EC-1 provisional-state
disclosure, an unpinned package, or an empty dependency closure all deny admission. The
guard implements no deployment and mutates nothing.
"""

from __future__ import annotations

from dataclasses import dataclass
from platform.certification.contracts import CertificationConsoleRecord
from platform.foundation.contracts import content_hash
from platform.runtime_operations.contracts import RuntimeOperationKind
from platform.runtime_operations.errors import RuntimeOperationsContractError
from typing import Any

from engine.runtime.assembly import RuntimeUnit
from engine.runtime.disclosure import disclosure_present

#: The deterministic admission criteria, in stable evaluation order (fail-closed).
ADMISSION_CRITERIA: tuple[str, ...] = (
    "certification-present",
    "certified",
    "target-matches-unit",
    "blueprint-matches-unit",
    "disclosure-present",
    "package-pinned",
    "closure-present",
)


@dataclass(frozen=True, slots=True)
class AdmissionDecision:
    """An immutable, content-addressed runtime-operation admission decision (fail-closed)."""

    runtime_id: str
    kind: RuntimeOperationKind
    certification_id: str
    target_id: str
    certified: bool
    admitted: bool
    reason: str
    criteria: tuple[tuple[str, bool], ...]
    admission_id: str = ""

    @classmethod
    def create(
        cls,
        *,
        runtime_id: str,
        kind: RuntimeOperationKind,
        certification_id: str,
        target_id: str,
        certified: bool,
        criteria: tuple[tuple[str, bool], ...],
    ) -> AdmissionDecision:
        admitted = all(ok for _, ok in criteria)
        reason = "admitted" if admitted else next(name for name, ok in criteria if not ok)
        core = {
            "runtime_id": runtime_id,
            "kind": kind.value,
            "certification_id": certification_id,
            "target_id": target_id,
            "certified": certified,
            "admitted": admitted,
            "reason": reason,
            "criteria": [list(pair) for pair in criteria],
        }
        return cls(
            runtime_id=runtime_id,
            kind=kind,
            certification_id=certification_id,
            target_id=target_id,
            certified=certified,
            admitted=admitted,
            reason=reason,
            criteria=criteria,
            admission_id=f"UCOS-ROAD-{content_hash(core)[:16]}",
        )

    @property
    def blockers(self) -> tuple[str, ...]:
        """The criteria that failed, in evaluation order."""
        return tuple(name for name, ok in self.criteria if not ok)

    def to_dict(self) -> dict[str, Any]:
        return {
            "admission_id": self.admission_id,
            "runtime_id": self.runtime_id,
            "kind": self.kind.value,
            "certification_id": self.certification_id,
            "target_id": self.target_id,
            "certified": self.certified,
            "admitted": self.admitted,
            "reason": self.reason,
            "criteria": {name: ok for name, ok in self.criteria},
            "blockers": list(self.blockers),
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


class RuntimeAdmissionGuard:
    """The deterministic CERTIFIED-only admission decision point (fail-closed)."""

    __slots__ = ()

    def evaluate(
        self,
        unit: RuntimeUnit,
        certification: CertificationConsoleRecord,
        kind: RuntimeOperationKind,
    ) -> AdmissionDecision:
        """Evaluate deploy/rollback admission for a unit + its governing certification (pure).

        Fail-closed: only a CERTIFIED unit whose certification governs exactly this unit
        (matching runtime target + blueprint), that carries the EC-1 provisional-state
        disclosure, a pinned package, and a non-empty dependency closure is admitted.
        """
        if not isinstance(unit, RuntimeUnit):
            raise RuntimeOperationsContractError("admission requires a RuntimeUnit")
        if not isinstance(certification, CertificationConsoleRecord):
            raise RuntimeOperationsContractError("admission requires a CertificationConsoleRecord")
        if not isinstance(kind, RuntimeOperationKind):
            raise RuntimeOperationsContractError("admission requires a RuntimeOperationKind")
        criteria: tuple[tuple[str, bool], ...] = (
            ("certification-present", bool(certification.certification_id)),
            ("certified", certification.certified),
            ("target-matches-unit", certification.target_id == unit.runtime_id),
            ("blueprint-matches-unit", certification.blueprint_id == unit.blueprint_id),
            ("disclosure-present", disclosure_present(unit.disclosure)),
            ("package-pinned", bool(unit.package_sha256)),
            ("closure-present", bool(unit.dependency_closure)),
        )
        return AdmissionDecision.create(
            runtime_id=unit.runtime_id,
            kind=kind,
            certification_id=certification.certification_id,
            target_id=certification.target_id,
            certified=certification.certified,
            criteria=criteria,
        )

    def admits(
        self,
        unit: RuntimeUnit,
        certification: CertificationConsoleRecord,
        kind: RuntimeOperationKind,
    ) -> bool:
        """True iff the unit is admissible for the operation (fail-closed)."""
        return self.evaluate(unit, certification, kind).admitted


__all__ = ["ADMISSION_CRITERIA", "AdmissionDecision", "RuntimeAdmissionGuard"]
