"""EC2-TASK-000099 — Blueprint Classification (EC2-EPIC-006).

The read-only **L4 EC-1 classification façade**. "Structural validation via EC-1
classification" (Program §4.3, §5, P4) is realized by the already-published Foundation
seam: ``ENG-CAP-01 Registry Resolution → engine.registry.read`` and ``ENG-CAP-02
Blueprint Classification → engine.compiler.compile`` (``platform/foundation/
capabilities.py``), published as ``ENGINE_CONTRACTS`` in ``platform/foundation/
contracts.py``. The platform consumes EC-1 **read-only through these contract
references** and **records** the classification result; it **invents no classification
semantics and modifies no ``engine/**`` module** (Determination Finding 2, P10).

This mirrors the certified ``platform/security/classification.py`` precedent: a
:class:`BlueprintClassification` is a *recorded EC-1 result bound to the certified
engine contracts by reference* — it computes nothing. The EC-1 output (did
``engine.registry.read`` resolve the blueprint? did ``engine.compiler.compile`` return
a non-defective classification, and to which of the six frozen families?) is supplied
to the façade and recorded immutably with a content-addressed id and a frozen gap
report. A classification is *valid* iff EC-1 resolved the blueprint and returned a
non-defective family classification; otherwise the blueprint is rejected with the gap
report (fail-closed, never cataloged).
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from platform.blueprints.contracts import BlueprintFamily
from platform.blueprints.errors import BlueprintClassificationError
from platform.foundation.contracts import ENGINE_CONTRACTS, ContractRef, content_hash
from typing import Any

#: The EC-1 registry-resolution contract the façade consumes read-only (ENG-CAP-01).
REGISTRY_CONTRACT = "engine.registry.read"

#: The EC-1 blueprint-classification contract the façade consumes read-only (ENG-CAP-02).
COMPILER_CONTRACT = "engine.compiler.compile"

#: The certified EC-1 contract references this façade binds to (read-only, by reference).
CLASSIFICATION_CONTRACTS: tuple[ContractRef, ...] = tuple(
    ref for ref in ENGINE_CONTRACTS if ref.name in {REGISTRY_CONTRACT, COMPILER_CONTRACT}
)


@dataclass(frozen=True, slots=True)
class BlueprintClassification:
    """An immutable, content-addressed record of an EC-1 classification result.

    Records — never computes — the EC-1 outcome for a blueprint: whether
    ``engine.registry.read`` ``resolved`` the blueprint, the classified generation
    ``family``, and the frozen ``defects`` gap report from ``engine.compiler.compile``.
    Carries the certified engine ``contracts`` it was produced against (by reference).
    """

    blueprint_ref: str
    family: BlueprintFamily
    resolved: bool
    defects: tuple[str, ...]
    contracts: tuple[str, ...]
    classification_id: str = ""

    @classmethod
    def create(
        cls,
        *,
        blueprint_ref: str,
        family: BlueprintFamily,
        resolved: bool,
        defects: Iterable[str] | None = None,
    ) -> BlueprintClassification:
        """Record an EC-1 classification result read-only (fail-closed on malformed input)."""
        if not isinstance(blueprint_ref, str) or not blueprint_ref.strip():
            raise BlueprintClassificationError("classification requires a non-empty blueprint_ref")
        if not isinstance(family, BlueprintFamily):
            raise BlueprintClassificationError(
                "classification family must be one of the six frozen BlueprintFamily members",
                blueprint_ref=blueprint_ref,
            )
        if not isinstance(resolved, bool):
            raise BlueprintClassificationError(
                "classification resolved must be a bool", blueprint_ref=blueprint_ref
            )
        defect_list = tuple(defects or ())
        for defect in defect_list:
            if not isinstance(defect, str) or not defect:
                raise BlueprintClassificationError(
                    "each classification defect must be a non-empty string",
                    blueprint_ref=blueprint_ref,
                )
        contracts = tuple(ref.name for ref in CLASSIFICATION_CONTRACTS)
        core = {
            "blueprint_ref": blueprint_ref,
            "family": family.value,
            "resolved": resolved,
            "defects": list(defect_list),
            "contracts": list(contracts),
        }
        return cls(
            blueprint_ref=blueprint_ref,
            family=family,
            resolved=resolved,
            defects=defect_list,
            contracts=contracts,
            classification_id=f"UCOS-BCLS-{content_hash(core)[:16]}",
        )

    @property
    def valid(self) -> bool:
        """True iff EC-1 resolved the blueprint and returned a non-defective classification."""
        return self.resolved and not self.defects

    def gap_report(self) -> dict[str, Any]:
        """The EC-1 gap report (empty when valid) — the rejection evidence (P4)."""
        return {
            "classification_id": self.classification_id,
            "blueprint_ref": self.blueprint_ref,
            "resolved": self.resolved,
            "defects": list(self.defects),
            "valid": self.valid,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "classification_id": self.classification_id,
            "blueprint_ref": self.blueprint_ref,
            "family": self.family.value,
            "resolved": self.resolved,
            "defects": list(self.defects),
            "contracts": list(self.contracts),
            "valid": self.valid,
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


def classify(
    blueprint_ref: str,
    family: BlueprintFamily,
    *,
    resolved: bool = True,
    defects: Iterable[str] | None = None,
) -> BlueprintClassification:
    """Record an EC-1 classification result through the read-only L4 façade.

    Convenience wrapper over :meth:`BlueprintClassification.create`. The EC-1 result
    (``resolved`` + ``family`` + ``defects``) is supplied by the caller (the EC-1
    engine output, consumed read-only); the platform records it.
    """
    return BlueprintClassification.create(
        blueprint_ref=blueprint_ref, family=family, resolved=resolved, defects=defects
    )


class ClassificationLedger:
    """A deterministic, append-only ledger of recorded EC-1 classifications (by blueprint)."""

    __slots__ = ("_by_blueprint",)

    def __init__(self) -> None:
        self._by_blueprint: dict[str, BlueprintClassification] = {}

    def record(self, classification: BlueprintClassification) -> BlueprintClassification:
        """Record a classification (idempotent by id; fail-closed on a conflicting record)."""
        if not isinstance(classification, BlueprintClassification):
            raise BlueprintClassificationError("only a BlueprintClassification may be recorded")
        existing = self._by_blueprint.get(classification.blueprint_ref)
        if existing is not None:
            if existing.classification_id == classification.classification_id:
                return existing
            raise BlueprintClassificationError(
                "blueprint already has a distinct classification recorded",
                blueprint_ref=classification.blueprint_ref,
            )
        self._by_blueprint[classification.blueprint_ref] = classification
        return classification

    def __contains__(self, blueprint_ref: str) -> bool:
        return blueprint_ref in self._by_blueprint

    def __len__(self) -> int:
        return len(self._by_blueprint)

    def get(self, blueprint_ref: str) -> BlueprintClassification:
        """Resolve a blueprint's recorded classification (fail-closed on absent)."""
        classification = self._by_blueprint.get(blueprint_ref)
        if classification is None:
            raise BlueprintClassificationError(
                "no classification recorded for blueprint", blueprint_ref=blueprint_ref
            )
        return classification

    @property
    def blueprint_refs(self) -> tuple[str, ...]:
        return tuple(sorted(self._by_blueprint))

    def to_dict(self) -> dict[str, Any]:
        return {
            "classification_count": len(self._by_blueprint),
            "classifications": [self._by_blueprint[ref].to_dict() for ref in self.blueprint_refs],
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


__all__ = [
    "REGISTRY_CONTRACT",
    "COMPILER_CONTRACT",
    "CLASSIFICATION_CONTRACTS",
    "BlueprintClassification",
    "classify",
    "ClassificationLedger",
]
