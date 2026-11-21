"""EC2-CAP-SEC-001 / SEC-CLASS — readiness validation tests.

Asserts the readiness conditions the determination requires: reuse of certified
components (no duplication), determinism (reproducible evidence with no wall-clock),
and phase discipline (only SEC-CLASS is present — no SEC-INTEL / SEC-REG / SEC-OBS /
SEC-CERT / SEC-ZONE artifacts).
"""

from __future__ import annotations

from pathlib import Path
from platform.security.contracts import ClassificationKind, SubjectLayer
from platform.security.service import build_security_classification_service

from engine.uckp.canonical import content_hash as LAYER_ZERO_CONTENT_HASH

_SECURITY_PKG = Path(__file__).resolve().parents[1] / "security"


def assert_reuses_certified_hashing(module) -> None:
    """Assert a security module hashes through the one certified primitive.

    Originally this compared ``content_hash.__module__`` to
    ``platform.foundation.contracts``, using "where was this function defined" as a
    proxy for "this module defined no hashing of its own". The primitive has since
    been consolidated into UCKP Layer Zero (UCKP-LAW-0001 Art-13, UCKP-INV-03) and
    ``platform.foundation.contracts`` re-exports it, so the defining module is now
    ``engine.uckp.canonical``.

    The check is expressed against object identity instead of a module name, which is
    what the readiness condition actually meant and is strictly stronger: a local
    redefinition would fail this even if it were placed in a module with the expected
    name. The import seam is asserted separately, so the module keeps reaching the
    primitive through the foundation it is certified against.
    """
    from platform.foundation import contracts as foundation_contracts

    assert module.content_hash is LAYER_ZERO_CONTENT_HASH
    assert foundation_contracts.content_hash is LAYER_ZERO_CONTENT_HASH


def test_reuses_certified_foundation_hashing():
    # SEC-CLASS reuses the foundation content hash — it defines no new hashing.
    from platform.security import classification as classification_module

    assert_reuses_certified_hashing(classification_module)


def test_reuses_certified_identity_seam():
    # SEC-CLASS references the certified L7 AuthorizationService — it defines no authz.
    from platform.security import service as service_module

    assert service_module.AuthorizationService.__module__ == "platform.identity.service"


def test_reuses_certified_capability_group_vocabulary():
    from platform.security import contracts as contracts_module

    assert contracts_module.CapabilityGroup.__module__ == "platform.identity.contracts"


def test_no_new_authorization_logic_is_introduced():
    service = build_security_classification_service()
    assert not hasattr(service, "authorize")
    assert not hasattr(service, "authorize_principal")


def test_evidence_is_deterministic_across_identical_runs():
    def build_fingerprint() -> str:
        service = build_security_classification_service()
        service.classify(
            ClassificationKind.CONFIDENTIALITY,
            SubjectLayer.DATA,
            "UCOS-DATA-000001",
            "restricted",
        )
        service.classify(
            ClassificationKind.INTEGRITY, SubjectLayer.SERVICE, "UCOS-SVC-000001", "signed"
        )
        return service.report().fingerprint()

    assert build_fingerprint() == build_fingerprint()


def test_all_six_sub_capability_modules_are_present():
    # Phase discipline: all six record-only sub-capabilities are now present.
    expected = {
        "__init__.py",
        "errors.py",
        "contracts.py",
        "classification.py",
        "service.py",
        "intelligence.py",
        "registries.py",
        "observability.py",
        "certification.py",
        "zones.py",
        "bootstrap.py",
    }
    present = {p.name for p in _SECURITY_PKG.glob("*.py")}
    assert expected.issubset(present)


def test_expected_modules_are_present():
    expected = {
        "__init__.py",
        "errors.py",
        "contracts.py",
        "classification.py",
        "service.py",
        "intelligence.py",
        "registries.py",
        "observability.py",
        "certification.py",
        "zones.py",
        "bootstrap.py",
    }
    present = {p.name for p in _SECURITY_PKG.glob("*.py")}
    assert expected.issubset(present)


def test_zone_runtime_reuses_certified_foundation_hashing():
    from platform.security import zones as zones_module

    assert_reuses_certified_hashing(zones_module)


def test_zones_and_controls_are_policy_configured_not_compiled_ceilings():
    # UMB-015 §4: a free-form future zone/control is recordable additively.
    from platform.security.contracts import RollupState
    from platform.security.zones import POSTURE_TARGET_ZONE, build_security_zone_service

    service = build_security_zone_service()
    future = service.assess(
        POSTURE_TARGET_ZONE,
        "ZONE-99-FUTURE",
        RollupState.IN_PROGRESS,
        rationale="future security model",
        evaluated_at=1,
    )
    assert future.target == "ZONE-99-FUTURE"


def test_zone_posture_service_introduces_no_enforcement():
    from platform.security.zones import build_security_zone_service

    service = build_security_zone_service()
    for forbidden in ("authorize", "grant", "ratify", "enact", "revoke", "override", "escalate"):
        assert not hasattr(service, forbidden)


def test_certification_reuses_certified_foundation_hashing():
    from platform.security import certification as certification_module

    assert_reuses_certified_hashing(certification_module)


def test_certification_is_evidence_backed_and_non_constitutive():
    from platform.security.certification import build_security_certification_service
    from platform.security.contracts import CertificationClass, CertificationDecision

    service = build_security_certification_service()
    # non-constitutive: no ratify/enact/authorize.
    for forbidden in ("authorize", "grant", "ratify", "enact", "revoke", "override"):
        assert not hasattr(service, forbidden)
    # evidence-backed: a CERTIFIED decision without evidence is refused.
    from platform.security.errors import SecurityCertificationError

    import pytest

    with pytest.raises(SecurityCertificationError):
        service.certify(
            CertificationClass.SECURITY,
            "UCOS-1",
            CertificationDecision.CERTIFIED,
            basis="b",
            certified_at=1,
        )


def test_observability_reuses_the_certified_l8_layer_not_a_second_stack():
    # SEC-OBS shapes telemetry through the certified L8 ObservabilityService; it
    # defines no MetricRegistry / LogBuffer / AuditTrail of its own.
    from platform.security import observability as obs_module

    assert obs_module.ObservabilityService.__module__ == "platform.observability.service"
    src = (_SECURITY_PKG / "observability.py").read_text(encoding="utf-8")
    assert "class MetricRegistry" not in src
    assert "class AuditTrail" not in src


def test_observability_introduces_no_new_signal_dimension():
    from platform.security.contracts import SECURITY_SIGNAL_DIMENSION

    assert SECURITY_SIGNAL_DIMENSION == "security"


def test_registry_runtime_reuses_certified_foundation_hashing():
    from platform.security import registries as registries_module

    assert_reuses_certified_hashing(registries_module)


def test_registry_set_introduces_no_eighth_registry_and_no_enactment():
    from platform.security.registries import SecurityRegistrySet, build_security_registry_service

    assert len(SecurityRegistrySet().kinds) == 7
    service = build_security_registry_service()
    for forbidden in ("authorize", "grant", "ratify", "enact", "revoke", "override", "escalate"):
        assert not hasattr(service, forbidden)


def test_intelligence_reuses_certified_foundation_hashing():
    # SEC-INTEL reuses the foundation content hash — it defines no new hashing.
    from platform.security import intelligence as intelligence_module

    assert_reuses_certified_hashing(intelligence_module)


def test_intelligence_evidence_is_deterministic_across_identical_runs():
    from platform.security.contracts import FindingKind, Severity
    from platform.security.intelligence import build_security_intelligence_service

    def build_fingerprint() -> str:
        service = build_security_intelligence_service()
        service.record_finding(FindingKind.VULNERABILITY, "CVE", severity=Severity.CRITICAL)
        service.record_finding(FindingKind.CONTROL, "AC-2")
        return service.report(now=42).fingerprint()

    assert build_fingerprint() == build_fingerprint()


def test_intelligence_introduces_no_enforcement_or_authority():
    from platform.security.intelligence import build_security_intelligence_service

    service = build_security_intelligence_service()
    for forbidden in ("authorize", "grant", "ratify", "enact", "revoke", "override", "escalate"):
        assert not hasattr(service, forbidden)


def test_no_secret_material_module_is_introduced():
    # SEC-04: SEC-CLASS ships no secret/credential/key module.
    forbidden = {"secrets.py", "keys.py", "credentials.py", "crypto.py"}
    present = {p.name for p in _SECURITY_PKG.glob("*.py")}
    assert not (forbidden & present)
