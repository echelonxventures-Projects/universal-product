"""TASK-000020 — Validation Engine (EPIC-003, IMP-007 §13).

Validation runs **before any code is emitted** and enforces, in order:

    1. **Structure** — the entity is schema-shaped (has attributes and exactly the
       primary-key discipline BP-DATA requires). Most structural invariants are
       already guaranteed by IR construction (TASK-000017); this layer adds the
       BP-DATA-specific rules.
    2. **Certification** — the blueprint declares itself ``CERTIFIED`` (IMP-007
       §14/§16; Mandatory Rule 4). Any other posture is an **uncertified input**
       and is rejected.
    3. **Traceability / registry conformance** — every id in the provenance chain
       (IMP-007 §1) resolves, through the **Registry Adapter (used exclusively)**,
       to a *registered* artifact that is itself in a certified lifecycle status.
       An unregistered or non-certified provenance reference is rejected
       (IMP-007 §15/§17; Mandatory Rules 3, 4, 6).

Validation never mutates anything and touches the corpus only through the
read-only Registry Adapter (DP-03). Failures raise :class:`ValidationError` /
:class:`CertificationError`, which the orchestrator converts into a Gap Report.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from engine.compiler.errors import CertificationError, ValidationError
from engine.compiler.ir import BlueprintIR
from engine.foundation.obs.logging import get_logger
from engine.foundation.obs.telemetry import trace
from engine.registry.adapter import RegistryAdapter
from engine.registry.models import Artifact, LifecycleStatus

_logger = get_logger("compiler.validation")

#: Lifecycle statuses accepted as "certified" for a registered provenance source.
#: The certified baseline of the 00-BOOK corpus is ACTIVE (twin verdict CERTIFIED,
#: UMB-017); stronger downstream statuses are also accepted. Anything weaker
#: (planning/in-progress/blocked/retired/superseded) is treated as non-certified.
CERTIFIED_LIFECYCLE: frozenset[LifecycleStatus] = frozenset(
    {
        LifecycleStatus.APPROVED,
        LifecycleStatus.CERTIFIED,
        LifecycleStatus.IMPLEMENTED,
        LifecycleStatus.TESTED,
        LifecycleStatus.DEPLOYED,
        LifecycleStatus.PRODUCTION,
        LifecycleStatus.FROZEN,
        LifecycleStatus.ACTIVE,
        LifecycleStatus.COMPLETE,
        LifecycleStatus.FINAL,
    }
)


@dataclass(frozen=True, slots=True)
class ValidationReport:
    """An auditable record of a successful validation (evidence, IMP-007 §11)."""

    blueprint_id: str
    certified: bool
    resolved_provenance: dict[str, str] = field(default_factory=dict)

    @property
    def is_valid(self) -> bool:
        return self.certified and len(self.resolved_provenance) == 6


class BlueprintValidator:
    """Validates a parsed blueprint IR against structure, certification, registry."""

    __slots__ = ("_registry",)

    def __init__(self, registry: RegistryAdapter) -> None:
        self._registry = registry

    # -- public API ------------------------------------------------------------

    def validate(self, ir: BlueprintIR) -> ValidationReport:
        """Validate ``ir`` fully; return a report or raise on the first failure."""
        with trace("compiler.validate", blueprint=ir.blueprint_id):
            self._check_structure(ir)
            self._check_certification(ir)
            resolved = self._check_registry_provenance(ir)
        _logger.info(
            "compiler.blueprint.validated",
            blueprint=ir.blueprint_id,
            resolved=len(resolved),
        )
        return ValidationReport(
            blueprint_id=ir.blueprint_id,
            certified=True,
            resolved_provenance=resolved,
        )

    def is_valid(self, ir: BlueprintIR) -> bool:
        """Return True iff ``ir`` validates, swallowing the specific failure."""
        try:
            self.validate(ir)
        except ValidationError:
            return False
        return True

    # -- checks ----------------------------------------------------------------

    def _check_structure(self, ir: BlueprintIR) -> None:
        """BP-DATA structural rules beyond the IR's own invariants."""
        primary = ir.entity.primary_key
        if not primary:
            raise ValidationError(
                "BP-DATA entity must declare exactly one primary key",
                blueprint_id=ir.blueprint_id,
                entity=ir.entity.name,
            )
        if len(primary) != 1:
            raise ValidationError(
                "composite primary keys are not supported for BP-DATA",
                blueprint_id=ir.blueprint_id,
                entity=ir.entity.name,
                primary_key_count=len(primary),
            )

    def _check_certification(self, ir: BlueprintIR) -> None:
        """Reject any blueprint that does not declare itself CERTIFIED (Rule 4)."""
        if not ir.certification.is_certified:
            raise CertificationError(
                "blueprint is not certified; the compiler rejects uncertified inputs",
                blueprint_id=ir.blueprint_id,
                declared_status=ir.certification.status.value,
            )

    def _check_registry_provenance(self, ir: BlueprintIR) -> dict[str, str]:
        """Resolve every provenance id via the Registry Adapter (exclusively).

        Returns a mapping ``{chain_field: registered_universal_id}``. Raises if any
        reference is unregistered or resolves to a non-certified artifact.
        """
        chain = {
            "canonical_source": ir.provenance.canonical_source,
            "reference_architecture": ir.provenance.reference_architecture,
            "runtime_catalog": ir.provenance.runtime_catalog,
            "architecture_constitution": ir.provenance.architecture_constitution,
            "ontology_root": ir.provenance.ontology_root,
            "generation_framework": ir.provenance.generation_framework,
        }
        resolved: dict[str, str] = {}
        for field_name, uid in chain.items():
            artifact = self._registry.artifacts.find(uid)
            if artifact is None:
                raise CertificationError(
                    "provenance reference is not registered; input is uncertified",
                    blueprint_id=ir.blueprint_id,
                    chain=field_name,
                    reference=uid,
                )
            self._assert_certified(ir.blueprint_id, field_name, artifact)
            resolved[field_name] = artifact.universal_id
        return resolved

    @staticmethod
    def _assert_certified(blueprint_id: str, chain_field: str, artifact: Artifact) -> None:
        if artifact.status not in CERTIFIED_LIFECYCLE:
            raise CertificationError(
                "provenance reference is not in a certified lifecycle status",
                blueprint_id=blueprint_id,
                chain=chain_field,
                reference=artifact.universal_id,
                status=artifact.status.value,
            )


__all__ = ["CERTIFIED_LIFECYCLE", "ValidationReport", "BlueprintValidator"]
