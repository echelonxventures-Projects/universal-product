"""EC2-CAP-SEC-001 / SEC-CLASS — Security Classification contracts (Phase 1).

The versioned contract surface and the immutable **core vocabulary** for the
**Security Classification Runtime** (SEC-CLASS). SEC-CLASS is the constitutional
"enforcement-by-reference seam": it binds the classification records defined by the
four subject-layer security architectures to platform constructs and *records* the
declared enforcement obligation as a **reference** to the existing, certified L7
Identity decision point — it enacts nothing (ARCH-SECURITY-001 §4–§11; DATA-014
DZA-01/03; SERVICE-014 SSE-03; APPLICATION-013 SEC-03/04; INFRASTRUCTURE-013
ISEC-01/04).

This module defines:

    * :class:`ClassificationKind` — the six subject-layer classification record types
      (Authentication / Authorization / Confidentiality / Integrity / Isolation /
      Classification-Label), reused verbatim; no new kind is invented.
    * :class:`SubjectLayer` — the four subject-layer security architectures that own
      the vocabulary, each carrying its constitutional source reference for backward
      traceability (ARCH-SECURITY-001 §14).
    * :class:`EnforcementReference` — an immutable, content-addressed **reference** to
      the L7 seam (a :class:`~platform.identity.contracts.CapabilityGroup` +
      :class:`~platform.foundation.identity.Permission`). It records *what the L7
      point would evaluate*; it performs no authorization (RG-02 / AR-04).
    * the published SEC-CLASS contract surface (:data:`SECURITY_CLASSIFICATION_CONTRACTS`).

All types are **immutable, typed, deterministic, and serializable**, hold no runtime
state, and embed no secret material (SEC-04 / RR-07).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from platform.foundation.contracts import (
    Contract,
    ContractRef,
    content_hash,
    platform_contract,
)
from platform.foundation.errors import PlatformContractError
from platform.foundation.identity import Permission
from platform.identity.contracts import CapabilityGroup
from platform.security.errors import EnforcementReferenceError, SecurityContractError
from typing import Any

#: The semantic version of the Security Classification contract surface (AR-03/PL-05).
SECURITY_CLASSIFICATION_CONTRACT_VERSION = "1.0.0"


class ClassificationKind(str, Enum):
    """The subject-layer security classification record types (reused verbatim).

    These are the evaluative, non-enforcing record types the four subject-layer
    security architectures define: SERVICE-014 / APPLICATION-013 (Authentication,
    Authorization, Confidentiality, Integrity), DATA-014 (Confidentiality, Integrity,
    Classification-Label), and INFRASTRUCTURE-013 (Isolation). No new kind is
    introduced (ARCH-SECURITY-001 §21).
    """

    AUTHENTICATION = "authentication-record"
    AUTHORIZATION = "authorization-record"
    CONFIDENTIALITY = "confidentiality-record"
    INTEGRITY = "integrity-record"
    ISOLATION = "isolation-facet"
    CLASSIFICATION_LABEL = "classification-label"


#: The classification kinds whose declared enforcement obligation resolves to the L7
#: authorization seam (a CapabilityGroup + Permission). The remaining kinds are pure
#: evaluative labels whose enforcement is a data/runtime reference, not the authz
#: decision point — they carry no :class:`EnforcementReference`.
L7_BOUND_KINDS: frozenset[ClassificationKind] = frozenset(
    {ClassificationKind.AUTHENTICATION, ClassificationKind.AUTHORIZATION}
)


class SubjectLayer(str, Enum):
    """The four subject-layer security architectures that own the classification vocabulary."""

    DATA = "DATA-014"
    SERVICE = "SERVICE-014"
    APPLICATION = "APPLICATION-013"
    INFRASTRUCTURE = "INFRASTRUCTURE-013"


#: Backward-traceability: each subject layer's constitutional source reference
#: (ARCH-SECURITY-001 §14 control/evidence traceability). Record-only mapping.
SUBJECT_LAYER_SOURCE: dict[SubjectLayer, str] = {
    SubjectLayer.DATA: "DATA-014/DZA-01 (classification, not enforcement)",
    SubjectLayer.SERVICE: "SERVICE-014/SSE-03 (evaluative-only)",
    SubjectLayer.APPLICATION: "APPLICATION-013/SEC-03 (evaluative-only)",
    SubjectLayer.INFRASTRUCTURE: "INFRASTRUCTURE-013/ISEC-01 (evaluative, non-enforcing)",
}

#: The classification kinds each subject layer is permitted to originate (reused from
#: the subject-layer taxonomies; DATA-014 DXH-10, SERVICE-014 SXH-10,
#: APPLICATION-013 AXH-09, INFRASTRUCTURE-013 §2). Decidable membership.
SUBJECT_LAYER_KINDS: dict[SubjectLayer, frozenset[ClassificationKind]] = {
    SubjectLayer.DATA: frozenset(
        {
            ClassificationKind.CLASSIFICATION_LABEL,
            ClassificationKind.CONFIDENTIALITY,
            ClassificationKind.INTEGRITY,
        }
    ),
    SubjectLayer.SERVICE: frozenset(
        {
            ClassificationKind.AUTHENTICATION,
            ClassificationKind.AUTHORIZATION,
            ClassificationKind.CONFIDENTIALITY,
            ClassificationKind.INTEGRITY,
        }
    ),
    SubjectLayer.APPLICATION: frozenset(
        {
            ClassificationKind.AUTHENTICATION,
            ClassificationKind.AUTHORIZATION,
            ClassificationKind.CONFIDENTIALITY,
            ClassificationKind.INTEGRITY,
        }
    ),
    SubjectLayer.INFRASTRUCTURE: frozenset(
        {
            ClassificationKind.ISOLATION,
            ClassificationKind.AUTHENTICATION,
            ClassificationKind.AUTHORIZATION,
            ClassificationKind.CONFIDENTIALITY,
            ClassificationKind.INTEGRITY,
        }
    ),
}


def all_classification_kinds() -> tuple[ClassificationKind, ...]:
    """Return every classification kind in stable declaration order."""
    return tuple(ClassificationKind)


def all_subject_layers() -> tuple[SubjectLayer, ...]:
    """Return every subject layer in stable declaration order."""
    return tuple(SubjectLayer)


@dataclass(frozen=True, slots=True)
class EnforcementReference:
    """An immutable **reference** to the existing L7 authorization seam.

    Records *what the certified* :class:`~platform.identity.service.AuthorizationService`
    *would evaluate* for a construct — a :class:`~platform.identity.contracts.CapabilityGroup`
    and a :class:`~platform.foundation.identity.Permission`. This is a recorded
    obligation only: SEC-CLASS **never** invokes authorization, grants access, or
    enacts a decision (RG-02 / AR-04; determination §4.1/§4.3). The ``reference_id``
    is content-addressed so an identical reference always yields the same id.
    """

    group: CapabilityGroup
    permission: Permission
    reference_id: str = ""

    @classmethod
    def create(cls, group: CapabilityGroup, permission: Permission) -> EnforcementReference:
        """Build an enforcement reference, validating it resolves to real L7 vocabulary."""
        if not isinstance(group, CapabilityGroup):
            raise EnforcementReferenceError(
                "enforcement reference group must be a CapabilityGroup (the L7 seam)"
            )
        if not isinstance(permission, Permission):
            raise EnforcementReferenceError(
                "enforcement reference permission must be a Permission",
                group=group.value,
            )
        core = {"group": group.value, "permission": permission.value}
        return cls(
            group=group,
            permission=permission,
            reference_id=f"UCOS-SREF-{content_hash(core)[:16]}",
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "reference_id": self.reference_id,
            "group": self.group.value,
            "permission": self.permission.value,
            "seam": "platform.identity.AuthorizationService",
            "enacts": False,
        }


# --------------------------------------------------------------------------- #
# The published SEC-CLASS contract surface.                                    #
# --------------------------------------------------------------------------- #

_SECURITY_CLASSIFICATION_CONTRACT_NAMES: tuple[tuple[str, str], ...] = (
    (
        "security.classification.record",
        "Record an evaluative, non-enforcing security classification against a construct.",
    ),
    (
        "security.classification.binding",
        "Bind a classification to a construct; resolve its enforcement reference to L7.",
    ),
    (
        "security.classification.evidence",
        "Deterministic, content-addressed classification evidence (record-only report).",
    ),
)

#: Immutable references to the published SEC-CLASS contracts (name + version).
SECURITY_CLASSIFICATION_CONTRACTS: tuple[ContractRef, ...] = tuple(
    ContractRef(name, SECURITY_CLASSIFICATION_CONTRACT_VERSION)
    for name, _ in _SECURITY_CLASSIFICATION_CONTRACT_NAMES
)


def security_classification_contract(name: str, description: str = "") -> Contract:
    """Build a versioned SEC-CLASS :class:`Contract` at the classification contract version."""
    try:
        return platform_contract(name, SECURITY_CLASSIFICATION_CONTRACT_VERSION, description)
    except PlatformContractError as exc:  # normalise into the security taxonomy
        raise SecurityContractError(str(exc), name=name) from exc


def default_security_classification_contracts() -> tuple[Contract, ...]:
    """The published SEC-CLASS contracts as concrete :class:`Contract` objects."""
    return tuple(
        security_classification_contract(name, description)
        for name, description in _SECURITY_CLASSIFICATION_CONTRACT_NAMES
    )


# --------------------------------------------------------------------------- #
# SEC-INTEL — Security Intelligence vocabulary + contract surface (Phase 2).   #
#                                                                              #
# Reuses the physical finding schema vocabulary (00-BOOK/SCHEMAS/              #
# finding.schema.json) and the UKB-ADV-005 entity/roll-up model **by           #
# reference** — no new security entity model is invented (ARCH-SECURITY-001    #
# §21). All types are immutable, typed, deterministic, and embed no secret.    #
# --------------------------------------------------------------------------- #

#: The semantic version of the Security Intelligence contract surface (AR-03/PL-05).
SECURITY_INTELLIGENCE_CONTRACT_VERSION = "1.0.0"


class FindingKind(str, Enum):
    """The security-intelligence entity kinds (finding.schema.json ``finding_kind``).

    Reused verbatim from the physical finding schema and UKB-ADV-005 §2; no new kind
    is invented. Threat Models, Controls, Exceptions, PenTest / Compliance / Audit
    evidence are all recorded as findings of the corresponding kind.
    """

    VULNERABILITY = "VULNERABILITY"
    CONTROL = "CONTROL"
    THREAT = "THREAT"
    EXCEPTION = "EXCEPTION"
    PENTEST = "PENTEST"
    COMPLIANCE_EVIDENCE = "COMPLIANCE_EVIDENCE"
    AUDIT_EVIDENCE = "AUDIT_EVIDENCE"


class Severity(str, Enum):
    """Finding severity (finding.schema.json ``severity`` enum)."""

    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class FindingState(str, Enum):
    """Finding lifecycle state (finding.schema.json ``state`` enum)."""

    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    ACCEPTED = "ACCEPTED"
    RESOLVED = "RESOLVED"
    FALSE_POSITIVE = "FALSE_POSITIVE"


class RollupState(str, Enum):
    """The evidence-derived security roll-up state (UKB-ADV-005 §4).

    A member of the corpus signal-state vocabulary so the security dimension rolls up
    deterministically: ``BLOCKED`` (open CRITICAL/HIGH without a valid exception),
    ``IN_PROGRESS`` (open MEDIUM within SLA / lower-severity open findings), or
    ``APPROVED`` (no open findings). No status is entered by hand.
    """

    BLOCKED = "BLOCKED"
    IN_PROGRESS = "IN_PROGRESS"
    APPROVED = "APPROVED"


#: The severities that drive a hard ``BLOCKED`` roll-up when open and un-excepted.
BLOCKING_SEVERITIES: frozenset[Severity] = frozenset({Severity.CRITICAL, Severity.HIGH})

#: The finding states that count as "open" for roll-up (still an active exposure).
OPEN_FINDING_STATES: frozenset[FindingState] = frozenset(
    {FindingState.OPEN, FindingState.IN_PROGRESS}
)

#: The finding-schema source reference (backward traceability; ARCH-SECURITY-001 §14).
FINDING_SCHEMA_SOURCE = "00-BOOK/SCHEMAS/finding.schema.json (UKB-ADV-005 §2)"


def all_finding_kinds() -> tuple[FindingKind, ...]:
    """Return every finding kind in stable declaration order."""
    return tuple(FindingKind)


def all_severities() -> tuple[Severity, ...]:
    """Return every severity in stable declaration order."""
    return tuple(Severity)


def all_finding_states() -> tuple[FindingState, ...]:
    """Return every finding state in stable declaration order."""
    return tuple(FindingState)


_SECURITY_INTELLIGENCE_CONTRACT_NAMES: tuple[tuple[str, str], ...] = (
    (
        "security.intelligence.record",
        "Record a security-intelligence finding (record-only; enacts nothing).",
    ),
    (
        "security.intelligence.rollup",
        "Evidence-derived security roll-up over recorded findings (deterministic).",
    ),
    (
        "security.intelligence.evidence",
        "Deterministic, content-addressed security-intelligence evidence (record-only).",
    ),
)

#: Immutable references to the published SEC-INTEL contracts (name + version).
SECURITY_INTELLIGENCE_CONTRACTS: tuple[ContractRef, ...] = tuple(
    ContractRef(name, SECURITY_INTELLIGENCE_CONTRACT_VERSION)
    for name, _ in _SECURITY_INTELLIGENCE_CONTRACT_NAMES
)


def security_intelligence_contract(name: str, description: str = "") -> Contract:
    """Build a versioned SEC-INTEL :class:`Contract` at the intelligence contract version."""
    try:
        return platform_contract(name, SECURITY_INTELLIGENCE_CONTRACT_VERSION, description)
    except PlatformContractError as exc:  # normalise into the security taxonomy
        raise SecurityContractError(str(exc), name=name) from exc


def default_security_intelligence_contracts() -> tuple[Contract, ...]:
    """The published SEC-INTEL contracts as concrete :class:`Contract` objects."""
    return tuple(
        security_intelligence_contract(name, description)
        for name, description in _SECURITY_INTELLIGENCE_CONTRACT_NAMES
    )


# --------------------------------------------------------------------------- #
# SEC-REG — Security Registry vocabulary + contract surface (Phase 3).         #
#                                                                              #
# The seven constitutional registries (ARCH-SECURITY-001 §17). Each is an      #
# append-only, record-only, attributed, queryable store that NEVER ratifies or #
# enacts (RG-02); every mutation is timestamped + attributed + queryable       #
# (RG-05). No eighth registry is introduced (determination §8).                #
# --------------------------------------------------------------------------- #

#: The semantic version of the Security Registry contract surface (AR-03/PL-05).
SECURITY_REGISTRY_CONTRACT_VERSION = "1.0.0"


class RegistryKind(str, Enum):
    """The seven constitutional security registries (ARCH-SECURITY-001 §17).

    Reused verbatim from the constitution; no eighth registry is introduced
    (determination §8). Each is record-only and non-enacting (RG-02).
    """

    SECURITY = "security-registry"
    IDENTITY = "identity-registry"
    THREAT = "threat-registry"
    RISK = "risk-registry"
    EVIDENCE = "evidence-registry"
    CERTIFICATION = "certification-registry"
    TRUST = "trust-registry"


#: Backward-traceability: each registry's constitutional source + role (§17; §8 table).
REGISTRY_SOURCE: dict[RegistryKind, str] = {
    RegistryKind.SECURITY: "ARCH-SECURITY-001 §17 — security assets/controls/policies",
    RegistryKind.IDENTITY: "ARCH-SECURITY-001 §17/§4 — identity/assurance (view over L7)",
    RegistryKind.THREAT: "ARCH-SECURITY-001 §17/§11 — threat models, correlated findings",
    RegistryKind.RISK: "ARCH-SECURITY-001 §17 — risk classifications, exception roll-ups",
    RegistryKind.EVIDENCE: "ARCH-SECURITY-001 §17/§14 — pentest/compliance/audit evidence",
    RegistryKind.CERTIFICATION: "ARCH-SECURITY-001 §17/§18 — security certification records",
    RegistryKind.TRUST: "ARCH-SECURITY-001 §17/§7 — trust boundaries/anchors/chains",
}


def all_registry_kinds() -> tuple[RegistryKind, ...]:
    """Return every registry kind in stable declaration order."""
    return tuple(RegistryKind)


_SECURITY_REGISTRY_CONTRACT_NAMES: tuple[tuple[str, str], ...] = (
    (
        "security.registry.record",
        "Append an attributed, timestamped record into a §17 registry (never enacts).",
    ),
    (
        "security.registry.query",
        "Query a §17 registry by kind / record type / subject / reference (record-only).",
    ),
    (
        "security.registry.evidence",
        "Deterministic, content-addressed registry evidence over all seven registries.",
    ),
)

#: Immutable references to the published SEC-REG contracts (name + version).
SECURITY_REGISTRY_CONTRACTS: tuple[ContractRef, ...] = tuple(
    ContractRef(name, SECURITY_REGISTRY_CONTRACT_VERSION)
    for name, _ in _SECURITY_REGISTRY_CONTRACT_NAMES
)


def security_registry_contract(name: str, description: str = "") -> Contract:
    """Build a versioned SEC-REG :class:`Contract` at the registry contract version."""
    try:
        return platform_contract(name, SECURITY_REGISTRY_CONTRACT_VERSION, description)
    except PlatformContractError as exc:  # normalise into the security taxonomy
        raise SecurityContractError(str(exc), name=name) from exc


def default_security_registry_contracts() -> tuple[Contract, ...]:
    """The published SEC-REG contracts as concrete :class:`Contract` objects."""
    return tuple(
        security_registry_contract(name, description)
        for name, description in _SECURITY_REGISTRY_CONTRACT_NAMES
    )


# --------------------------------------------------------------------------- #
# SEC-OBS — Security Observability vocabulary + contract surface (Phase 4).    #
#                                                                              #
# Emits the EXISTING ``security`` signal dimension + telemetry THROUGH the L8  #
# Observability Layer (ARCH-SECURITY-001 §15; UMB-015 §5). It creates NO new   #
# signal dimension and NO second telemetry stack (determination §9); it adds   #
# only security-specific signal shaping and reverse-traceability.              #
# --------------------------------------------------------------------------- #

#: The semantic version of the Security Observability contract surface (AR-03/PL-05).
SECURITY_OBSERVABILITY_CONTRACT_VERSION = "1.0.0"

#: The **existing** canonical signal dimension emitted for security (no new dimension
#: is created — the ``security`` dimension already exists in the corpus signal spine:
#: ``00-BOOK/tools/connectors/base.py`` DIMENSIONS; ``ukb.py`` DOMAIN-D). Determination §9.
SECURITY_SIGNAL_DIMENSION = "security"


_SECURITY_OBSERVABILITY_CONTRACT_NAMES: tuple[tuple[str, str], ...] = (
    (
        "security.observability.signal",
        "Emit the `security` signal dimension for a subject (reverse-traceable; record-only).",
    ),
    (
        "security.observability.telemetry",
        "Shape security telemetry (metric/log/audit) through the L8 Observability Layer.",
    ),
    (
        "security.observability.evidence",
        "Deterministic, content-addressed security-observability evidence (record-only).",
    ),
)

#: Immutable references to the published SEC-OBS contracts (name + version).
SECURITY_OBSERVABILITY_CONTRACTS: tuple[ContractRef, ...] = tuple(
    ContractRef(name, SECURITY_OBSERVABILITY_CONTRACT_VERSION)
    for name, _ in _SECURITY_OBSERVABILITY_CONTRACT_NAMES
)


def security_observability_contract(name: str, description: str = "") -> Contract:
    """Build a versioned SEC-OBS :class:`Contract` at the observability contract version."""
    try:
        return platform_contract(name, SECURITY_OBSERVABILITY_CONTRACT_VERSION, description)
    except PlatformContractError as exc:  # normalise into the security taxonomy
        raise SecurityContractError(str(exc), name=name) from exc


def default_security_observability_contracts() -> tuple[Contract, ...]:
    """The published SEC-OBS contracts as concrete :class:`Contract` objects."""
    return tuple(
        security_observability_contract(name, description)
        for name, description in _SECURITY_OBSERVABILITY_CONTRACT_NAMES
    )


# --------------------------------------------------------------------------- #
# SEC-CERT — Security Certification vocabulary + contract surface (Phase 5).   #
#                                                                              #
# Records the §18 security certification objects and the §19 control-facet     #
# requirement. Record-only, immutable, evidence-backed, non-constitutive;      #
# never inferred from source-asset coverage (STATUS-001 §2; determination §11).#
# --------------------------------------------------------------------------- #

#: The semantic version of the Security Certification contract surface (AR-03/PL-05).
SECURITY_CERTIFICATION_CONTRACT_VERSION = "1.0.0"


class CertificationClass(str, Enum):
    """The seven security certification classes (ARCH-SECURITY-001 §18)."""

    IDENTITY = "identity-certification"
    SECURITY = "security-certification"
    PRIVACY = "privacy-certification"
    COMPLIANCE = "compliance-certification"
    OPERATIONAL = "operational-certification"
    TRUST = "trust-certification"
    GOVERNANCE = "governance-certification"


class CertificationDecision(str, Enum):
    """A record-only, evidence-derived certification decision (fail-closed)."""

    CERTIFIED = "CERTIFIED"
    NOT_CERTIFIED = "NOT_CERTIFIED"


class ControlFacet(str, Enum):
    """The seven facets every security control must carry or generation fails (§19)."""

    IDENTITY = "identity-model"
    TRUST = "trust-model"
    TRACEABILITY = "traceability"
    TESTING = "testing"
    OBSERVABILITY = "observability"
    CERTIFICATION = "certification"
    GOVERNANCE = "governance"


#: The §19 required control facets — a control missing any of these fails generation
#: and produces a Gap Report (ARCH-SECURITY-001 §19; determination §13.6).
REQUIRED_CONTROL_FACETS: frozenset[ControlFacet] = frozenset(ControlFacet)


def all_certification_classes() -> tuple[CertificationClass, ...]:
    """Return every certification class in stable declaration order."""
    return tuple(CertificationClass)


def all_control_facets() -> tuple[ControlFacet, ...]:
    """Return every control facet in stable declaration order."""
    return tuple(ControlFacet)


_SECURITY_CERTIFICATION_CONTRACT_NAMES: tuple[tuple[str, str], ...] = (
    (
        "security.certification.record",
        "Record an evidence-backed §18 security certification (record-only; non-constitutive).",
    ),
    (
        "security.certification.control",
        "Evaluate a control's §19 facets; produce a Gap Report on any missing facet.",
    ),
    (
        "security.certification.rollup",
        "Roll recorded certifications into a deterministic program certification.",
    ),
    (
        "security.certification.evidence",
        "Deterministic, content-addressed security-certification evidence (record-only).",
    ),
)

#: Immutable references to the published SEC-CERT contracts (name + version).
SECURITY_CERTIFICATION_CONTRACTS: tuple[ContractRef, ...] = tuple(
    ContractRef(name, SECURITY_CERTIFICATION_CONTRACT_VERSION)
    for name, _ in _SECURITY_CERTIFICATION_CONTRACT_NAMES
)


def security_certification_contract(name: str, description: str = "") -> Contract:
    """Build a versioned SEC-CERT :class:`Contract` at the certification contract version."""
    try:
        return platform_contract(name, SECURITY_CERTIFICATION_CONTRACT_VERSION, description)
    except PlatformContractError as exc:  # normalise into the security taxonomy
        raise SecurityContractError(str(exc), name=name) from exc


def default_security_certification_contracts() -> tuple[Contract, ...]:
    """The published SEC-CERT contracts as concrete :class:`Contract` objects."""
    return tuple(
        security_certification_contract(name, description)
        for name, description in _SECURITY_CERTIFICATION_CONTRACT_NAMES
    )


# --------------------------------------------------------------------------- #
# SEC-ZONE — Zone & Control Posture vocabulary + contract surface (Phase 6).   #
#                                                                              #
# The UMB-015 five-zone / seven-control model. Zones and controls are POLICY   #
# CONFIGURATION, not compiled ceilings (UMB-015 §4); a new zone/control is      #
# incorporable additively. Posture evaluation is record-only (determination    #
# §6.1). Security state is DOMAIN-D and never projected (UMB-015 §5).           #
# --------------------------------------------------------------------------- #

#: The semantic version of the Security Zone contract surface (AR-03/PL-05).
SECURITY_ZONE_CONTRACT_VERSION = "1.0.0"


class SecurityZone(str, Enum):
    """The five UMB-015 protection zones (most → least privileged)."""

    CORE = "ZONE-0"
    GOVERNANCE = "ZONE-1"
    ENGINEERING = "ZONE-2"
    OPERATIONS = "ZONE-3"
    CONSUMPTION = "ZONE-4"


#: Zone privilege level (0 = most privileged / innermost; UMB-015 §1). Data-only.
ZONE_LEVEL: dict[SecurityZone, int] = {
    SecurityZone.CORE: 0,
    SecurityZone.GOVERNANCE: 1,
    SecurityZone.ENGINEERING: 2,
    SecurityZone.OPERATIONS: 3,
    SecurityZone.CONSUMPTION: 4,
}

#: Human-readable zone names (UMB-015 §1 table).
ZONE_NAME: dict[SecurityZone, str] = {
    SecurityZone.CORE: "UCOS CORE",
    SecurityZone.GOVERNANCE: "GOVERNANCE",
    SecurityZone.ENGINEERING: "ENGINEERING",
    SecurityZone.OPERATIONS: "OPERATIONS",
    SecurityZone.CONSUMPTION: "CONSUMPTION",
}

#: Default posture per zone (UMB-015 §1 table). Policy configuration, not a ceiling.
ZONE_DEFAULT_POSTURE: dict[SecurityZone, str] = {
    SecurityZone.CORE: "maximally protected; append-only; write only via transaction T",
    SecurityZone.GOVERNANCE: "governed write; append-only; authority-neutral",
    SecurityZone.ENGINEERING: "registered write via T; reviewed",
    SecurityZone.OPERATIONS: "append-only signal write; connectors read-only against sources",
    SecurityZone.CONSUMPTION: "read/derive only; never mutates canon",
}

#: The canonical canon zones that ZONE-3/ZONE-4 may never mutate (UMB-015 §1; UMB-INV-01).
CANON_ZONES: frozenset[SecurityZone] = frozenset(
    {SecurityZone.CORE, SecurityZone.GOVERNANCE, SecurityZone.ENGINEERING}
)


class SecurityControl(str, Enum):
    """The seven UMB-015 controls (§2)."""

    ACCESS = "access-control"
    VISIBILITY = "visibility-control"
    IDENTITY = "identity-control"
    SYNCHRONIZATION = "synchronization-control"
    PUBLICATION = "publication-control"
    KNOWLEDGE = "knowledge-control"
    AUDIT = "audit-control"


#: The mechanism each control realizes (UMB-015 §2 table). Data-only.
CONTROL_MECHANISM: dict[SecurityControl, str] = {
    SecurityControl.ACCESS: "zone membership + write path (only T writes registers)",
    SecurityControl.VISIBILITY: "projection scope per zone; sensitive facets by handle (RR-07)",
    SecurityControl.IDENTITY: "every actor/change/signal attributed (UMB-003)",
    SecurityControl.SYNCHRONIZATION: "three gates make create=register unskippable (REG-AUTO-001)",
    SecurityControl.PUBLICATION: "exports dynamic, non-authoritative, source as_of (UMB-011)",
    SecurityControl.KNOWLEDGE: "append-only; correction supersedes, never edits (UCI-001 CP-3)",
    SecurityControl.AUDIT: "append-only signal + ID ledger + git = immutable audit trail",
}


def all_security_zones() -> tuple[SecurityZone, ...]:
    """Return every security zone in stable (privilege) order."""
    return tuple(SecurityZone)


def all_security_controls() -> tuple[SecurityControl, ...]:
    """Return every security control in stable declaration order."""
    return tuple(SecurityControl)


_SECURITY_ZONE_CONTRACT_NAMES: tuple[tuple[str, str], ...] = (
    (
        "security.zone.assess",
        "Record an evaluative zone/control posture (policy-configured; record-only).",
    ),
    (
        "security.zone.mutation",
        "Evaluate a zone→zone mutation direction against UMB-INV-01 (decidable; enacts nothing).",
    ),
    (
        "security.zone.evidence",
        "Deterministic, content-addressed zone/control posture evidence (record-only).",
    ),
)

#: Immutable references to the published SEC-ZONE contracts (name + version).
SECURITY_ZONE_CONTRACTS: tuple[ContractRef, ...] = tuple(
    ContractRef(name, SECURITY_ZONE_CONTRACT_VERSION) for name, _ in _SECURITY_ZONE_CONTRACT_NAMES
)


def security_zone_contract(name: str, description: str = "") -> Contract:
    """Build a versioned SEC-ZONE :class:`Contract` at the zone contract version."""
    try:
        return platform_contract(name, SECURITY_ZONE_CONTRACT_VERSION, description)
    except PlatformContractError as exc:  # normalise into the security taxonomy
        raise SecurityContractError(str(exc), name=name) from exc


def default_security_zone_contracts() -> tuple[Contract, ...]:
    """The published SEC-ZONE contracts as concrete :class:`Contract` objects."""
    return tuple(
        security_zone_contract(name, description)
        for name, description in _SECURITY_ZONE_CONTRACT_NAMES
    )


__all__ = [
    "SECURITY_CLASSIFICATION_CONTRACT_VERSION",
    "ClassificationKind",
    "L7_BOUND_KINDS",
    "SubjectLayer",
    "SUBJECT_LAYER_SOURCE",
    "SUBJECT_LAYER_KINDS",
    "all_classification_kinds",
    "all_subject_layers",
    "EnforcementReference",
    "SECURITY_CLASSIFICATION_CONTRACTS",
    "security_classification_contract",
    "default_security_classification_contracts",
    # SEC-INTEL
    "SECURITY_INTELLIGENCE_CONTRACT_VERSION",
    "FindingKind",
    "Severity",
    "FindingState",
    "RollupState",
    "BLOCKING_SEVERITIES",
    "OPEN_FINDING_STATES",
    "FINDING_SCHEMA_SOURCE",
    "all_finding_kinds",
    "all_severities",
    "all_finding_states",
    "SECURITY_INTELLIGENCE_CONTRACTS",
    "security_intelligence_contract",
    "default_security_intelligence_contracts",
    # SEC-REG
    "SECURITY_REGISTRY_CONTRACT_VERSION",
    "RegistryKind",
    "REGISTRY_SOURCE",
    "all_registry_kinds",
    "SECURITY_REGISTRY_CONTRACTS",
    "security_registry_contract",
    "default_security_registry_contracts",
    # SEC-OBS
    "SECURITY_OBSERVABILITY_CONTRACT_VERSION",
    "SECURITY_SIGNAL_DIMENSION",
    "SECURITY_OBSERVABILITY_CONTRACTS",
    "security_observability_contract",
    "default_security_observability_contracts",
    # SEC-CERT
    "SECURITY_CERTIFICATION_CONTRACT_VERSION",
    "CertificationClass",
    "CertificationDecision",
    "ControlFacet",
    "REQUIRED_CONTROL_FACETS",
    "all_certification_classes",
    "all_control_facets",
    "SECURITY_CERTIFICATION_CONTRACTS",
    "security_certification_contract",
    "default_security_certification_contracts",
    # SEC-ZONE
    "SECURITY_ZONE_CONTRACT_VERSION",
    "SecurityZone",
    "ZONE_LEVEL",
    "ZONE_NAME",
    "ZONE_DEFAULT_POSTURE",
    "CANON_ZONES",
    "SecurityControl",
    "CONTROL_MECHANISM",
    "all_security_zones",
    "all_security_controls",
    "SECURITY_ZONE_CONTRACTS",
    "security_zone_contract",
    "default_security_zone_contracts",
]
