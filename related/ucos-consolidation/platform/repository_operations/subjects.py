"""EPIC-PLAT-003 — Subject assimilation for the canonical validation engine (Terminal T5).

The VALIDATION and CERTIFICATION stages reuse the certified EC-1 Validation and
Certification engines verbatim. Those engines validate a normalized
:class:`~engine.validation.contracts.ValidationSubject`; this module is the *context
assimilation* entry point that projects a plain, serializable facts mapping (as a
repository discovery step would produce) into that subject — mirroring the acceptance
engine's :meth:`RepositorySubject.from_mapping`. It re-implements no check and invents
no verdict (TP-01); it only shapes inputs for the certified engines.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from platform.repository_operations.errors import StageExecutionError
from typing import Any

from engine.validation.contracts import ValidationSubject


def _seq_of_str(value: Any) -> tuple[str, ...]:
    if isinstance(value, Sequence) and not isinstance(value, str | bytes):
        return tuple(str(item) for item in value)
    return ()


def _seq_of_map(value: Any) -> tuple[Mapping[str, Any], ...]:
    if isinstance(value, Sequence) and not isinstance(value, str | bytes):
        return tuple(dict(item) for item in value if isinstance(item, Mapping))
    return ()


def _mapping(value: Any) -> Mapping[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def build_validation_subject(raw: Mapping[str, Any]) -> ValidationSubject:
    """Assimilate a facts mapping into a normalized :class:`ValidationSubject`.

    Raises:
        StageExecutionError: if ``raw`` is not a mapping or lacks the mandatory
            ``target_id`` / ``blueprint_id`` identity the engine requires.
    """
    if not isinstance(raw, Mapping):
        raise StageExecutionError("validation subject facts must be a mapping")
    target_id = raw.get("target_id")
    blueprint_id = raw.get("blueprint_id")
    if not target_id or not blueprint_id:
        raise StageExecutionError(
            "validation subject requires a target_id and a blueprint_id",
            target_id=target_id,
            blueprint_id=blueprint_id,
        )
    disclosure_raw = raw.get("disclosure")
    disclosure = dict(disclosure_raw) if isinstance(disclosure_raw, Mapping) else None
    return ValidationSubject(
        target_id=str(target_id),
        blueprint_id=str(blueprint_id),
        provenance_chain=_seq_of_str(raw.get("provenance_chain")),
        signature=_mapping(raw.get("signature")),
        sbom=_mapping(raw.get("sbom")),
        dependency_closure=_seq_of_map(raw.get("dependency_closure")),
        disclosure=disclosure,
        package_sha256=str(raw.get("package_sha256", "")),
        image_reference=str(raw.get("image_reference", "")),
        runtime_id=(str(raw["runtime_id"]) if raw.get("runtime_id") else None),
        blueprint_class=(str(raw["blueprint_class"]) if raw.get("blueprint_class") else None),
    )


__all__ = ["build_validation_subject"]
