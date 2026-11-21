"""EC2-TASK-000100 — Blueprint Validation (EC2-EPIC-006).

The deterministic **structural validation orchestration** (Program §4.3, §5, P4). A
blueprint is *valid* iff EC-1 resolves it (``engine.registry.read``) and returns a
non-defective classification (``engine.compiler.compile``) into exactly one of the six
frozen generation families; otherwise it is **rejected with the EC-1 gap report** and
never enters the catalog (fail-closed, TP-01 "STOP → GAP REPORT → REQUEST AUTHORITY").
The platform adds **no second validation semantics** — it surfaces EC-1's
structural/classification result and enforces platform-side integrity only (P10).

:func:`evaluate` returns an immutable, content-addressed :class:`ValidationResult`
(valid/invalid + gap report) as data; :func:`require_valid` is the fail-closed gate
that raises :class:`BlueprintValidationError` (carrying the gap report) on rejection.
"""

from __future__ import annotations

from dataclasses import dataclass
from platform.blueprints.classification import BlueprintClassification
from platform.blueprints.contracts import BlueprintFamily
from platform.blueprints.errors import BlueprintValidationError
from platform.foundation.contracts import content_hash
from typing import Any


@dataclass(frozen=True, slots=True)
class ValidationResult:
    """An immutable, content-addressed structural-validation verdict (fail-closed).

    ``valid`` is ``True`` only when the recorded EC-1 classification resolved the
    blueprint into one of the six frozen families with no defects. ``gap_report``
    carries the EC-1 rejection evidence (empty when valid).
    """

    blueprint_ref: str
    valid: bool
    family: BlueprintFamily
    gap_report: tuple[str, ...]
    result_id: str = ""

    @classmethod
    def create(
        cls,
        *,
        blueprint_ref: str,
        valid: bool,
        family: BlueprintFamily,
        gap_report: tuple[str, ...],
    ) -> ValidationResult:
        core = {
            "blueprint_ref": blueprint_ref,
            "valid": valid,
            "family": family.value,
            "gap_report": list(gap_report),
        }
        return cls(
            blueprint_ref=blueprint_ref,
            valid=valid,
            family=family,
            gap_report=gap_report,
            result_id=f"UCOS-BVLD-{content_hash(core)[:16]}",
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "result_id": self.result_id,
            "blueprint_ref": self.blueprint_ref,
            "valid": self.valid,
            "family": self.family.value,
            "gap_report": list(self.gap_report),
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


def evaluate(classification: BlueprintClassification) -> ValidationResult:
    """Evaluate a recorded EC-1 classification into a structural-validation verdict.

    Pure and deterministic: identical classifications yield identical results. Adds no
    validation semantics beyond surfacing the EC-1 result (P10). An unresolved blueprint
    or one carrying compiler defects is invalid; its gap report is the union of the
    unresolved marker and the recorded defects.
    """
    if not isinstance(classification, BlueprintClassification):
        raise BlueprintValidationError("validation requires a BlueprintClassification")
    if not isinstance(classification.family, BlueprintFamily):  # pragma: no cover - defensive
        raise BlueprintValidationError(
            "classification family must be a frozen BlueprintFamily",
            blueprint_ref=classification.blueprint_ref,
        )
    defects: list[str] = []
    if not classification.resolved:
        defects.append("engine.registry.read: blueprint did not resolve")
    defects.extend(classification.defects)
    return ValidationResult.create(
        blueprint_ref=classification.blueprint_ref,
        valid=classification.valid,
        family=classification.family,
        gap_report=tuple(defects),
    )


def require_valid(classification: BlueprintClassification) -> ValidationResult:
    """Fail-closed validation gate: raise with the gap report unless the blueprint is valid.

    An invalid blueprint is refused with :class:`BlueprintValidationError` carrying the
    EC-1 gap report so it never enters the catalog (P4). Returns the
    :class:`ValidationResult` on success.
    """
    result = evaluate(classification)
    if not result.valid:
        raise BlueprintValidationError(
            "blueprint rejected: structural validation failed (EC-1 gap report)",
            blueprint_ref=result.blueprint_ref,
            gap_report=",".join(result.gap_report),
        )
    return result


__all__ = ["ValidationResult", "evaluate", "require_valid"]
