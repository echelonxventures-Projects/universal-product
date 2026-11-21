"""EC-1 Validation Layer (EPIC-007) — deterministic acceptance validation.

Public API surface for the Validation Layer: a read-only, additive verifier that
validates generated, deployable artifacts (EPIC-005 runtime units, produced via
the EPIC-006 factory) against the constitutional invariants they must hold —
provenance, signature, SBOM, EC-1 provisional-state disclosure, a pinned
dependency closure, a digest-pinned image, and a deterministic identity — then
produces validation evidence and enforces acceptance gates.

The layer is additive and constitutional: it never mutates a subject, never writes
to the certified corpus (DP-03), accesses the registry only through validated
upstream artifacts, invents no verdicts (TP-01), and is fully deterministic
(IMP-007 §5) — an identical subject yields a byte-identical report, evidence, and
acceptance decision.

Tasks: TASK-000046 (architecture + contracts + checks), TASK-000047 (execution),
TASK-000048 (evidence), TASK-000049 (acceptance gates).
"""

from __future__ import annotations

from engine.validation.checks import (
    DependencyClosureCheck,
    DisclosureCheck,
    IdentityCheck,
    ImageDigestCheck,
    ProvenanceCheck,
    SbomCheck,
    SignatureCheck,
    ValidationCheck,
    default_checks,
)
from engine.validation.contracts import (
    VALIDATION_CONTRACT_VERSION,
    CheckStatus,
    Severity,
    ValidationFinding,
    ValidationReport,
    ValidationRequest,
    ValidationSubject,
    Verdict,
)
from engine.validation.errors import (
    AcceptanceGateError,
    ValidationLayerError,
    ValidationSubjectError,
)
from engine.validation.evidence import (
    EVIDENCE_FORMAT,
    ValidationEvidence,
    build_validation_evidence,
)
from engine.validation.executor import ValidationEngine, validate_runtime_unit
from engine.validation.gates import AcceptanceDecision, enforce_acceptance

__all__ = [
    # contracts
    "VALIDATION_CONTRACT_VERSION",
    "Severity",
    "CheckStatus",
    "Verdict",
    "ValidationRequest",
    "ValidationFinding",
    "ValidationReport",
    "ValidationSubject",
    # checks
    "ValidationCheck",
    "ProvenanceCheck",
    "SignatureCheck",
    "SbomCheck",
    "DisclosureCheck",
    "DependencyClosureCheck",
    "ImageDigestCheck",
    "IdentityCheck",
    "default_checks",
    # execution
    "ValidationEngine",
    "validate_runtime_unit",
    # evidence
    "ValidationEvidence",
    "build_validation_evidence",
    "EVIDENCE_FORMAT",
    # gates
    "AcceptanceDecision",
    "enforce_acceptance",
    # errors
    "ValidationLayerError",
    "ValidationSubjectError",
    "AcceptanceGateError",
]
