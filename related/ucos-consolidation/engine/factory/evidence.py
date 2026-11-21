"""TASK-000043 — Factory Evidence (EPIC-006).

A **Generation Evidence Record** captures, deterministically, what a factory run
produced so the outcome is auditable (IMP-007 §11; Mandatory Rule 6 — every
generation yields evidence). The record embeds no wall-clock or ambient state, so
identical inputs produce a byte-identical record.

It captures:

    * **Blueprint** — the blueprint id and version.
    * **Classification** — the resolved blueprint class and how it was derived.
    * **Compiler Artifact** — the published artifact id + package hash (or *none*
      on a deferred gap).
    * **Runtime Artifact** — the assembled runtime id + digest-pinned image
      reference (or *none*).
    * **Dependency Closure** — the pinned closure members.
    * **Disclosure State** — whether the EC-1 provisional-state disclosure is
      present (DE-05).

Evidence is built by the orchestrator from the compiler/runtime outputs; a gap
run records the same shape with the compiler/runtime fields null and the gap
attached.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

from engine.factory.classifier import BlueprintClassification

#: The evidence record format identifier.
EVIDENCE_FORMAT = "ucos-generation-evidence/1.0.0"


@dataclass(frozen=True, slots=True)
class GenerationEvidence:
    """A deterministic, serializable Generation Evidence Record."""

    blueprint_id: str
    blueprint_version: str
    classification: Mapping[str, Any]
    compiler_artifact: Mapping[str, Any] | None
    runtime_artifact: Mapping[str, Any] | None
    dependency_closure: tuple[Mapping[str, Any], ...]
    disclosure_state: Mapping[str, Any]
    gap: Mapping[str, Any] | None = field(default=None)

    def to_dict(self) -> dict[str, Any]:
        return {
            "evidence_format": EVIDENCE_FORMAT,
            "blueprint": {
                "blueprint_id": self.blueprint_id,
                "version": self.blueprint_version,
            },
            "classification": dict(self.classification),
            "compiler_artifact": (
                dict(self.compiler_artifact) if self.compiler_artifact is not None else None
            ),
            "runtime_artifact": (
                dict(self.runtime_artifact) if self.runtime_artifact is not None else None
            ),
            "dependency_closure": [dict(entry) for entry in self.dependency_closure],
            "disclosure_state": dict(self.disclosure_state),
            "gap": dict(self.gap) if self.gap is not None else None,
        }


def build_generation_evidence(
    *,
    blueprint_id: str,
    blueprint_version: str,
    classification: BlueprintClassification,
    compiler_artifact: Mapping[str, Any] | None,
    runtime_artifact: Mapping[str, Any] | None,
    dependency_closure: Sequence[Mapping[str, Any]],
    disclosure: Mapping[str, Any] | None,
    gap: Mapping[str, Any] | None = None,
) -> GenerationEvidence:
    """Assemble a deterministic :class:`GenerationEvidence` record."""
    disclosure_state = {
        "present": disclosure is not None,
        "disclosure_id": disclosure.get("disclosure_id") if disclosure else None,
        "gate": disclosure.get("gate") if disclosure else None,
        "asserts_constitutional_finality": (
            disclosure.get("asserts_constitutional_finality") if disclosure else None
        ),
    }
    return GenerationEvidence(
        blueprint_id=blueprint_id,
        blueprint_version=blueprint_version,
        classification=classification.to_dict(),
        compiler_artifact=dict(compiler_artifact) if compiler_artifact is not None else None,
        runtime_artifact=dict(runtime_artifact) if runtime_artifact is not None else None,
        dependency_closure=tuple(dict(entry) for entry in dependency_closure),
        disclosure_state=disclosure_state,
        gap=dict(gap) if gap is not None else None,
    )


__all__ = [
    "EVIDENCE_FORMAT",
    "GenerationEvidence",
    "build_generation_evidence",
]
