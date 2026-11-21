"""UCOS-EPIC-005 — Universal Validation Engine (Terminal T5).

The platform-layer validation **runtime**: a deterministic, fail-closed,
evidence-producing engine that validates a system across the seven universal domains —
**Architecture, Implementation, Dependency, Registry, Schema, Runtime, and Quality** —
from a single, configuration-driven command.

The engine is:

    * **universal** — one normalized :class:`ValidationTarget` and one open rule suite
      validate any system; the seven domains are covered by the built-in
      :func:`default_rules`, and callers may supply their own rules;
    * **fail-closed** — a rule that cannot prove its invariant (absent or malformed
      evidence) records a FAIL, never a pass; the verdict is FAIL iff any *blocking*
      rule failed (Mission mandate);
    * **evidence-required** — every run yields a content-addressed
      :class:`ValidationReport`, a :class:`ValidationDashboard`, and a
      :class:`ValidationEvidence` record (Mandatory Rule 6); and
    * **deterministic** — an identical target validated by an identical suite yields a
      byte-identical report and content hash (IMP-007 §5); no wall-clock or ambient
      state enters any identity.

It is strictly additive and record-only over the certified EC-1 engine: it consumes the
EC-1 foundation (logging, telemetry, disclosure, frozen-path guard) and the platform
foundation (content hashing) through their published surfaces, invents no verdict
(TP-01), mutates no target, and never writes to the certified corpus (DP-03). It asserts
``ENGINEERING-EXECUTION-ONLY`` authority and carries the EC-1 provisional-state
disclosure (DE-05 / IP-01).

Deliverables: Validation Engine (:class:`UniversalValidationEngine`), Rules
(:mod:`platform.universal_validation.rules`), Evidence
(:mod:`platform.universal_validation.evidence`), Reports
(:class:`ValidationReport` / :class:`ValidationDashboard`), and the CLI
(``ucos-validate``).
"""

from __future__ import annotations

from platform.universal_validation.config import (
    UniversalValidationConfig,
    load_config,
    parse_config,
)
from platform.universal_validation.contracts import (
    UNIVERSAL_VALIDATION_CONTRACT_VERSION,
    VALIDATION_AUTHORITY,
    VALIDATION_DASHBOARD_FORMAT,
    VALIDATION_REPORT_FORMAT,
    DomainReport,
    EngineVerdict,
    RuleResult,
    RuleSeverity,
    RuleStatus,
    ValidationDashboard,
    ValidationDomain,
    ValidationReport,
    ValidationTarget,
)
from platform.universal_validation.engine import UniversalValidationEngine
from platform.universal_validation.errors import (
    RuleDefinitionError,
    UniversalValidationError,
    ValidationConfigError,
    ValidationEngineError,
    ValidationTargetError,
)
from platform.universal_validation.evidence import (
    EVIDENCE_FORMAT,
    ValidationEvidence,
    build_validation_evidence,
)
from platform.universal_validation.rules import ValidationRule, default_rules
from platform.universal_validation.service import (
    UniversalValidationService,
    build_universal_validation_service,
)

__all__ = [
    # contracts
    "UNIVERSAL_VALIDATION_CONTRACT_VERSION",
    "VALIDATION_REPORT_FORMAT",
    "VALIDATION_DASHBOARD_FORMAT",
    "VALIDATION_AUTHORITY",
    "ValidationDomain",
    "RuleSeverity",
    "RuleStatus",
    "EngineVerdict",
    "ValidationTarget",
    "RuleResult",
    "DomainReport",
    "ValidationReport",
    "ValidationDashboard",
    # rules
    "ValidationRule",
    "default_rules",
    # engine
    "UniversalValidationEngine",
    # evidence
    "EVIDENCE_FORMAT",
    "ValidationEvidence",
    "build_validation_evidence",
    # config
    "UniversalValidationConfig",
    "parse_config",
    "load_config",
    # service
    "UniversalValidationService",
    "build_universal_validation_service",
    # errors
    "UniversalValidationError",
    "ValidationConfigError",
    "ValidationTargetError",
    "RuleDefinitionError",
    "ValidationEngineError",
]
