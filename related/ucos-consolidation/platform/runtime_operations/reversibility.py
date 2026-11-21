"""EC2-TASK-000168 — Runtime Operations Reversibility Proof (EC2-EPIC-012).

The deterministic **reversibility proof** enforcing acceptance criterion **IP-08
(reversibility)**: every governed rollback of a certified runtime unit must be provably
reversible. The proof is a **pure function** of the certified
:class:`~engine.runtime.deploy.RollbackDescriptor` produced read-only by EC-1 — it
consults no wall-clock and no external state, so an identical rollback descriptor always
yields an identical :class:`ReversibilityProof` and fingerprint (P5). It re-derives no
rollback; it audits the certified descriptor against the reversibility invariants:

    * the descriptor declares itself ``reversible``;
    * it uses the certified checkpoint-based strategy
      (:data:`~engine.runtime.deploy.ROLLBACK_STRATEGY`);
    * it captures a restorable **checkpoint** of the current pinned state;
    * it records a concrete **restore image** (the digest-pinned state to restore to); and
    * it carries the EC-1 provisional-state disclosure (DE-05).

A deploy operation is **not** a rollback and is therefore not reversibility-provable; the
proof is fail-closed on any non-rollback input.
"""

from __future__ import annotations

from dataclasses import dataclass
from platform.foundation.contracts import content_hash
from platform.runtime_operations.errors import RuntimeReversibilityError
from typing import Any

from engine.runtime.deploy import ROLLBACK_STRATEGY, RollbackDescriptor
from engine.runtime.disclosure import disclosure_present

#: The deterministic reversibility indicators, in stable evaluation order (IP-08).
REVERSIBILITY_INDICATORS: tuple[str, ...] = (
    "declared-reversible",
    "checkpoint-strategy",
    "checkpoint-present",
    "restore-image-present",
    "disclosure-present",
)


@dataclass(frozen=True, slots=True)
class ReversibilityProof:
    """An immutable, content-addressed reversibility proof over a rollback descriptor (IP-08)."""

    runtime_id: str
    blueprint_id: str
    environment: str
    strategy: str
    reversible: bool
    indicators: tuple[tuple[str, bool], ...]
    satisfied: tuple[str, ...]
    blockers: tuple[str, ...]
    reverts_to_present: bool
    restore_image: str
    proof_id: str = ""

    @classmethod
    def create(
        cls,
        *,
        runtime_id: str,
        blueprint_id: str,
        environment: str,
        strategy: str,
        indicators: tuple[tuple[str, bool], ...],
        reverts_to_present: bool,
        restore_image: str,
    ) -> ReversibilityProof:
        satisfied = tuple(name for name, ok in indicators if ok)
        blockers = tuple(name for name, ok in indicators if not ok)
        reversible = not blockers
        core = {
            "runtime_id": runtime_id,
            "blueprint_id": blueprint_id,
            "environment": environment,
            "strategy": strategy,
            "reversible": reversible,
            "indicators": [list(pair) for pair in indicators],
            "reverts_to_present": reverts_to_present,
            "restore_image": restore_image,
        }
        return cls(
            runtime_id=runtime_id,
            blueprint_id=blueprint_id,
            environment=environment,
            strategy=strategy,
            reversible=reversible,
            indicators=indicators,
            satisfied=satisfied,
            blockers=blockers,
            reverts_to_present=reverts_to_present,
            restore_image=restore_image,
            proof_id=f"UCOS-RORV-{content_hash(core)[:16]}",
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "proof_id": self.proof_id,
            "runtime_id": self.runtime_id,
            "blueprint_id": self.blueprint_id,
            "environment": self.environment,
            "strategy": self.strategy,
            "reversible": self.reversible,
            "indicators": {name: ok for name, ok in self.indicators},
            "satisfied": list(self.satisfied),
            "blockers": list(self.blockers),
            "reverts_to_present": self.reverts_to_present,
            "restore_image": self.restore_image,
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


def prove_reversibility(descriptor: RollbackDescriptor) -> ReversibilityProof:
    """Prove deterministic reversibility of a certified rollback descriptor (pure, IP-08)."""
    if not isinstance(descriptor, RollbackDescriptor):
        raise RuntimeReversibilityError("prove_reversibility requires a RollbackDescriptor")
    restore_image = str(descriptor.kubernetes_rollback.get("restore_image", ""))
    indicators: tuple[tuple[str, bool], ...] = (
        ("declared-reversible", descriptor.reversible),
        ("checkpoint-strategy", descriptor.strategy == ROLLBACK_STRATEGY),
        ("checkpoint-present", bool(descriptor.checkpoint)),
        ("restore-image-present", bool(restore_image)),
        ("disclosure-present", disclosure_present(descriptor.disclosure)),
    )
    return ReversibilityProof.create(
        runtime_id=descriptor.runtime_id,
        blueprint_id=descriptor.blueprint_id,
        environment=descriptor.environment,
        strategy=descriptor.strategy,
        indicators=indicators,
        reverts_to_present=descriptor.reverts_to is not None,
        restore_image=restore_image,
    )


__all__ = ["REVERSIBILITY_INDICATORS", "ReversibilityProof", "prove_reversibility"]
