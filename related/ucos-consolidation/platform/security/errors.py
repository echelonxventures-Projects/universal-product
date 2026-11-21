"""EC2-CAP-SEC-001 — Security Runtime error taxonomy.

The Security Runtime **reuses** the EC-2 Platform Foundation error discipline
(:class:`~platform.foundation.errors.PlatformError`) additively — it does not fork or
modify it. Every security error is rooted in :class:`SecurityError`, carries a stable,
category-prefixed ``code`` (``EC2-SEC-*``) and structured, non-secret ``context`` so
failures are auditable (PL-02, IP-12) and machine-consumable.

Scope note (mission boundary): this module ships the errors the implemented
sub-capabilities need. All six sub-capabilities (**SEC-CLASS**, **SEC-INTEL**,
**SEC-REG**, **SEC-OBS**, **SEC-CERT**, **SEC-ZONE**) are present. Every error stores
**no** secret value (SEC-04 / RR-07).
"""

from __future__ import annotations

from platform.foundation.errors import PlatformError


class SecurityError(PlatformError):
    """Base class for all EC2-CAP-SEC-001 Security Runtime errors."""

    code = "EC2-SEC-000"


class SecurityClassificationError(SecurityError):
    """A security classification record is malformed or violates non-enforcement."""

    code = "EC2-SEC-CLASS-001"


class ClassificationBindingError(SecurityError):
    """A classification could not be bound to a construct, or the binding is malformed."""

    code = "EC2-SEC-CLASS-002"


class EnforcementReferenceError(SecurityError):
    """A declared enforcement obligation does not resolve to the existing L7 seam."""

    code = "EC2-SEC-CLASS-003"


class ClassificationValidationError(SecurityError):
    """A classification failed meta-validity (typed / identified / non-enforcing / resolvable)."""

    code = "EC2-SEC-CLASS-004"


class SecurityContractError(SecurityError):
    """A security contract is malformed or violates versioning discipline (AR-03/PL-05)."""

    code = "EC2-SEC-CONTRACT-001"


class SecurityBootstrapError(SecurityError):
    """A Security Runtime sub-capability could not be composed (fail-closed)."""

    code = "EC2-SEC-BOOTSTRAP-001"


# --------------------------------------------------------------------------- #
# SEC-INTEL — Security Intelligence Runtime (Phase 2) error taxonomy.          #
# --------------------------------------------------------------------------- #


class SecurityFindingError(SecurityError):
    """A security finding record is malformed or violates non-enforcement."""

    code = "EC2-SEC-INTEL-001"


class FindingValidationError(SecurityError):
    """A finding failed meta-validity (typed / identified / non-enforcing / kind-consistent)."""

    code = "EC2-SEC-INTEL-002"


class SecretLeakError(SecurityError):
    """A secret pattern was detected in an ingested field (SEC-04 / RR-07; UKB-ADV-005 §6).

    Raised only by low-level ingest guards that must fail closed; the higher-level
    intelligence service instead **records a SECRET-LEAK finding referencing location
    only** and never stores the secret value.
    """

    code = "EC2-SEC-INTEL-003"


class SecurityRollupError(SecurityError):
    """The evidence-derived security roll-up could not be computed (fail-closed)."""

    code = "EC2-SEC-INTEL-004"


# --------------------------------------------------------------------------- #
# SEC-REG — Security Registry Runtime (Phase 3) error taxonomy.                #
# --------------------------------------------------------------------------- #


class SecurityRegistryError(SecurityError):
    """A security registry operation is malformed or violates non-enactment (RG-02)."""

    code = "EC2-SEC-REG-001"


class RegistryEntryError(SecurityError):
    """A registry entry is malformed (untyped / unattributed / not timestamped; RG-05)."""

    code = "EC2-SEC-REG-002"


class RegistryValidationError(SecurityError):
    """A registry entry failed meta-validity (typed / identified / attributed / non-enacting)."""

    code = "EC2-SEC-REG-003"


# --------------------------------------------------------------------------- #
# SEC-OBS — Security Observability Runtime (Phase 4) error taxonomy.           #
# --------------------------------------------------------------------------- #


class SecurityObservabilityError(SecurityError):
    """A security observability operation is malformed (fail-closed)."""

    code = "EC2-SEC-OBS-001"


class SecuritySignalError(SecurityError):
    """A security signal is malformed or emitted on a non-``security`` dimension."""

    code = "EC2-SEC-OBS-002"


class SignalTraceabilityError(SecurityError):
    """A security signal is not reverse-traceable to a finding/scan (UMB-015 §5; PL-02)."""

    code = "EC2-SEC-OBS-003"


# --------------------------------------------------------------------------- #
# SEC-CERT — Security Certification Runtime (Phase 5) error taxonomy.          #
# --------------------------------------------------------------------------- #


class SecurityCertificationError(SecurityError):
    """A security certification record is malformed or violates non-constitutiveness."""

    code = "EC2-SEC-CERT-001"


class CertificationValidationError(SecurityError):
    """A certification failed meta-validity (typed / identified / evidence-backed)."""

    code = "EC2-SEC-CERT-002"


class CertificationGapError(SecurityError):
    """A security control lacks a required §19 facet (Gap Report; generation fails)."""

    code = "EC2-SEC-CERT-003"


# --------------------------------------------------------------------------- #
# SEC-ZONE — Zone & Control Posture Runtime (Phase 6) error taxonomy.          #
# --------------------------------------------------------------------------- #


class SecurityZoneError(SecurityError):
    """A zone/control posture operation is malformed (fail-closed)."""

    code = "EC2-SEC-ZONE-001"


class ZonePostureError(SecurityError):
    """A zone/control posture record is malformed or violates non-enactment."""

    code = "EC2-SEC-ZONE-002"


class ZoneMutationError(SecurityError):
    """A mutation-direction evaluation is malformed (UMB-015 §1 / UMB-INV-01)."""

    code = "EC2-SEC-ZONE-003"


__all__ = [
    "SecurityError",
    "SecurityClassificationError",
    "ClassificationBindingError",
    "EnforcementReferenceError",
    "ClassificationValidationError",
    "SecurityContractError",
    "SecurityBootstrapError",
    # SEC-INTEL
    "SecurityFindingError",
    "FindingValidationError",
    "SecretLeakError",
    "SecurityRollupError",
    # SEC-REG
    "SecurityRegistryError",
    "RegistryEntryError",
    "RegistryValidationError",
    # SEC-OBS
    "SecurityObservabilityError",
    "SecuritySignalError",
    "SignalTraceabilityError",
    # SEC-CERT
    "SecurityCertificationError",
    "CertificationValidationError",
    "CertificationGapError",
    # SEC-ZONE
    "SecurityZoneError",
    "ZonePostureError",
    "ZoneMutationError",
]
