"""UCOS-EPIC-005 — Universal Validation service (Terminal T5).

The single composition point for the Universal Validation Engine. It wires a
:class:`~platform.universal_validation.config.UniversalValidationConfig` (or an explicit
:class:`~platform.universal_validation.contracts.ValidationTarget`) to the
:class:`~platform.universal_validation.engine.UniversalValidationEngine` and exposes the
operations the mission asks for: perform universal validation and return the
deterministic report, dashboard, and evidence record.

The service is strictly additive and record-only: it composes the engine and rules,
invents no verdict (TP-01), and never writes to the certified corpus (DP-03).
"""

from __future__ import annotations

from collections.abc import Iterable
from platform.universal_validation.config import UniversalValidationConfig
from platform.universal_validation.contracts import (
    ValidationDashboard,
    ValidationReport,
    ValidationTarget,
)
from platform.universal_validation.engine import UniversalValidationEngine
from platform.universal_validation.evidence import ValidationEvidence, build_validation_evidence
from platform.universal_validation.rules import ValidationRule


class UniversalValidationService:
    """A thin facade over the engine (validate → report / dashboard / evidence)."""

    __slots__ = ("_engine",)

    def __init__(self, engine: UniversalValidationEngine) -> None:
        self._engine = engine

    @property
    def engine(self) -> UniversalValidationEngine:
        return self._engine

    def validate(self, target: ValidationTarget) -> ValidationReport:
        """Perform universal validation over ``target`` (the T5 deliverable)."""
        return self._engine.validate(target)

    def dashboard(self, target: ValidationTarget) -> ValidationDashboard:
        """Validate ``target`` and project the Validation Dashboard from the report."""
        return self.validate(target).dashboard()

    def evidence(self, target: ValidationTarget) -> ValidationEvidence:
        """Validate ``target`` and assemble the deterministic evidence record."""
        return build_validation_evidence(self.validate(target))


def build_universal_validation_service(
    config: UniversalValidationConfig | None = None,
    *,
    rules: Iterable[ValidationRule] | None = None,
) -> UniversalValidationService:
    """Default composition of the Universal Validation Engine.

    When ``config`` is supplied, its declared domain subset scopes the engine; when
    ``rules`` is supplied, that suite is used verbatim. With neither, the full built-in
    universal suite runs.
    """
    domains = config.selected_domains() if config is not None else None
    engine = UniversalValidationEngine(rules, domains=domains)
    return UniversalValidationService(engine)


__all__ = [
    "UniversalValidationService",
    "build_universal_validation_service",
]
