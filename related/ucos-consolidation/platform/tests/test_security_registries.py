"""EC2-CAP-SEC-001 / SEC-REG — Security Registry Runtime tests.

Covers the seven §17 registries: the attributed/timestamped `RegistryEntry` (RG-05),
the append-only per-kind registry, the composed seven-registry set, the service
composition root, deterministic evidence, secret defense (RR-07), governed-event
emission, structural non-enactment (RG-02), and the bootstrap composition.
"""

from __future__ import annotations

from platform.foundation.bootstrap import bootstrap_platform
from platform.foundation.events import EventBus
from platform.security.bootstrap import (
    SECURITY_REGISTRY_BOOTSTRAP_EVENT,
    bootstrap_security_registry,
)
from platform.security.contracts import (
    SECURITY_REGISTRY_CONTRACTS,
    RegistryKind,
    all_registry_kinds,
)
from platform.security.errors import (
    RegistryValidationError,
    SecurityBootstrapError,
    SecurityRegistryError,
)
from platform.security.registries import (
    REGISTRY_RECORDED_EVENT,
    AppendOnlyRegistry,
    RegistryEntry,
    SecurityRegistryEvidence,
    SecurityRegistryService,
    SecurityRegistrySet,
    build_security_registry_service,
)

import pytest


def _entry(kind: RegistryKind = RegistryKind.TRUST, **kw) -> RegistryEntry:
    base = dict(
        record_type="trust-anchor",
        subject_ref="UCOS-INF-000001",
        recorded_by="UCOS-PRIN-000001",
        recorded_at=1,
    )
    base.update(kw)
    return RegistryEntry.create(kind, base.pop("record_type"), base.pop("subject_ref"), **base)


# --------------------------------------------------------------------------- #
# RegistryEntry (RG-05 attribution / timestamp)                                #
# --------------------------------------------------------------------------- #


def test_create_entry_is_deterministic_and_attributed():
    a = _entry(refs=("UCOS-SFND-x",), attributes={"boundary": "zone-3"})
    b = _entry(refs=("UCOS-SFND-x",), attributes={"boundary": "zone-3"})
    assert a.entry_id == b.entry_id
    assert a.entry_id.startswith("UCOS-SREG-")
    assert a.non_enacting is True
    assert a.recorded_by == "UCOS-PRIN-000001"
    assert a.recorded_at == 1


def test_create_rejects_bad_registry():
    with pytest.raises(SecurityRegistryError):
        RegistryEntry.create("nope", "t", "s", recorded_by="p", recorded_at=1)  # type: ignore[arg-type]


def test_create_rejects_empty_record_type():
    with pytest.raises(SecurityRegistryError):
        _entry(record_type="   ")


def test_create_rejects_empty_subject_ref():
    with pytest.raises(SecurityRegistryError):
        _entry(subject_ref="")


def test_create_rejects_missing_attribution():
    with pytest.raises(SecurityRegistryError):
        _entry(recorded_by="   ")


def test_create_rejects_non_int_timestamp():
    with pytest.raises(SecurityRegistryError):
        _entry(recorded_at="now")
    with pytest.raises(SecurityRegistryError):
        _entry(recorded_at=True)


def test_create_rejects_secret_in_any_field():
    with pytest.raises(SecurityRegistryError):
        _entry(attributes={"cfg": "password: supersecretvalue"})
    with pytest.raises(SecurityRegistryError):
        _entry(refs=("AKIAIOSFODNN7EXAMPLE",))


def test_validate_success_trace_and_dict():
    e = _entry(refs=("UCOS-SFND-1",))
    assert e.validate()["meta_valid"] is True
    t = e.trace()
    assert t["backward"]["registry"] == "trust-registry"
    assert "§17" in t["backward"]["source_ref"]
    assert t["refs"] == ["UCOS-SFND-1"]
    assert e.to_dict()["non_enacting"] is True
    assert e.fingerprint() == _entry(refs=("UCOS-SFND-1",)).fingerprint()


def test_validate_fails_on_hand_built_unattributed_entry():
    # A directly-constructed entry that bypasses create() fails meta-validity.
    bad = RegistryEntry(
        registry=RegistryKind.SECURITY,
        record_type="x",
        subject_ref="s",
        recorded_by="",
        recorded_at=1,
        entry_id="UCOS-SREG-bad",
    )
    with pytest.raises(RegistryValidationError):
        bad.validate()


# --------------------------------------------------------------------------- #
# AppendOnlyRegistry (RG-02: record + read only)                               #
# --------------------------------------------------------------------------- #


def test_registry_rejects_bad_kind():
    with pytest.raises(SecurityRegistryError):
        AppendOnlyRegistry("nope")  # type: ignore[arg-type]


def test_registry_record_and_idempotency():
    reg = AppendOnlyRegistry(RegistryKind.TRUST)
    e = _entry()
    reg.record(e)
    reg.record(e)
    assert len(reg) == 1
    assert e.entry_id in reg
    assert reg.get(e.entry_id) is e


def test_registry_rejects_non_entry_and_wrong_kind():
    reg = AppendOnlyRegistry(RegistryKind.TRUST)
    with pytest.raises(SecurityRegistryError):
        reg.record("nope")  # type: ignore[arg-type]
    with pytest.raises(SecurityRegistryError):
        reg.record(_entry(RegistryKind.RISK))  # wrong registry


def test_registry_get_missing_raises():
    with pytest.raises(SecurityRegistryError):
        AppendOnlyRegistry(RegistryKind.TRUST).get("UCOS-SREG-missing")


def test_registry_queries():
    reg = AppendOnlyRegistry(RegistryKind.EVIDENCE)
    a = RegistryEntry.create(
        RegistryKind.EVIDENCE,
        "pentest",
        "UCOS-SVC-1",
        recorded_by="p",
        recorded_at=1,
        refs=("UCOS-SFND-1",),
    )
    b = RegistryEntry.create(
        RegistryKind.EVIDENCE,
        "audit",
        "UCOS-SVC-2",
        recorded_by="p",
        recorded_at=2,
    )
    reg.record(a)
    reg.record(b)
    assert reg.by_record_type("pentest") == (a,)
    assert reg.by_subject("UCOS-SVC-2") == (b,)
    assert reg.referencing("UCOS-SFND-1") == (a,)
    assert reg.kind is RegistryKind.EVIDENCE
    assert isinstance(reg.fingerprint(), str)
    assert reg.to_dict()["entry_count"] == 2


def test_registry_has_no_enact_or_mutate_methods():
    reg = AppendOnlyRegistry(RegistryKind.SECURITY)
    for forbidden in ("ratify", "enact", "grant", "revoke", "override", "delete", "update"):
        assert not hasattr(reg, forbidden)


# --------------------------------------------------------------------------- #
# SecurityRegistrySet (seven registries; no eighth)                            #
# --------------------------------------------------------------------------- #


def test_set_has_exactly_seven_registries():
    s = SecurityRegistrySet()
    assert len(s.kinds) == 7
    assert set(s.kinds) == set(all_registry_kinds())


def test_set_registry_rejects_bad_kind():
    with pytest.raises(SecurityRegistryError):
        SecurityRegistrySet().registry("nope")  # type: ignore[arg-type]


def test_set_records_routes_to_correct_registry():
    s = SecurityRegistrySet()
    e = _entry(RegistryKind.THREAT, record_type="threat-model", subject_ref="UCOS-CMP-1")
    s.record(e)
    assert len(s.registry(RegistryKind.THREAT)) == 1
    assert len(s) == 1
    counts = dict(s.counts())
    assert counts["threat-registry"] == 1
    assert counts["security-registry"] == 0


def test_set_rejects_non_entry():
    with pytest.raises(SecurityRegistryError):
        SecurityRegistrySet().record("nope")  # type: ignore[arg-type]


def test_set_fingerprint_and_dict_deterministic():
    def build() -> SecurityRegistrySet:
        s = SecurityRegistrySet()
        s.record(_entry(RegistryKind.TRUST))
        return s

    assert build().fingerprint() == build().fingerprint()
    assert build().to_dict()["registry_count"] == 7


# --------------------------------------------------------------------------- #
# SecurityRegistryEvidence                                                     #
# --------------------------------------------------------------------------- #


def test_evidence_is_content_addressed():
    ev = SecurityRegistryEvidence.create(
        set_fingerprint="abc",
        total_entries=0,
        registry_counts=(("trust-registry", 0),),
        registries=(),
    )
    assert ev.evidence_id.startswith("UCOS-SREV-")
    assert ev.to_dict()["total_entries"] == 0
    assert (
        ev.fingerprint()
        == SecurityRegistryEvidence.create(
            set_fingerprint="abc",
            total_entries=0,
            registry_counts=(("trust-registry", 0),),
            registries=(),
        ).fingerprint()
    )


# --------------------------------------------------------------------------- #
# SecurityRegistryService                                                      #
# --------------------------------------------------------------------------- #


def test_service_rejects_bad_registries():
    with pytest.raises(SecurityRegistryError):
        SecurityRegistryService(registries="nope")  # type: ignore[arg-type]


def test_service_rejects_bad_events():
    with pytest.raises(SecurityRegistryError):
        SecurityRegistryService(events="nope")  # type: ignore[arg-type]


def test_service_record_emits_event():
    bus = EventBus()
    service = build_security_registry_service(events=bus)
    e = service.record(
        RegistryKind.TRUST, "trust-anchor", "UCOS-INF-1", recorded_by="UCOS-PRIN-1", recorded_at=1
    )
    assert e.entry_id in service.registries.registry(RegistryKind.TRUST)
    evs = bus.events_of(REGISTRY_RECORDED_EVENT)
    assert len(evs) == 1
    assert evs[0].payload["enacts"] is False


def test_service_record_without_bus():
    service = build_security_registry_service()
    e = service.record(
        RegistryKind.RISK, "risk-class", "UCOS-DATA-1", recorded_by="p", recorded_at=1
    )
    assert e.entry_id in service.registries.registry(RegistryKind.RISK)


def test_service_record_entry_and_rejects_non_entry():
    service = build_security_registry_service()
    e = _entry(RegistryKind.CERTIFICATION, record_type="cert", subject_ref="UCOS-CRT-1")
    assert service.record_entry(e).entry_id == e.entry_id
    with pytest.raises(SecurityRegistryError):
        service.record_entry("nope")  # type: ignore[arg-type]


def test_service_query_variants():
    service = build_security_registry_service()
    service.record(
        RegistryKind.EVIDENCE,
        "pentest",
        "UCOS-SVC-1",
        recorded_by="p",
        recorded_at=1,
        refs=("UCOS-SFND-1",),
    )
    service.record(RegistryKind.EVIDENCE, "audit", "UCOS-SVC-2", recorded_by="p", recorded_at=2)
    assert len(service.query(RegistryKind.EVIDENCE)) == 2
    assert len(service.query(RegistryKind.EVIDENCE, record_type="pentest")) == 1
    assert len(service.query(RegistryKind.EVIDENCE, subject_ref="UCOS-SVC-2")) == 1
    assert len(service.query(RegistryKind.EVIDENCE, ref="UCOS-SFND-1")) == 1


def test_service_trace_validate_validate_all_report():
    service = build_security_registry_service()
    e = service.record(
        RegistryKind.SECURITY, "control", "UCOS-CMP-1", recorded_by="p", recorded_at=1
    )
    assert service.trace(RegistryKind.SECURITY, e.entry_id)["entry_id"] == e.entry_id
    assert service.validate(RegistryKind.SECURITY, e.entry_id)["meta_valid"] is True
    agg = service.validate_all()
    assert agg["entry_count"] == 1
    assert agg["meta_valid"] is True
    report = service.report()
    assert report.evidence_id.startswith("UCOS-SREV-")
    assert report.total_entries == 1
    assert service.to_dict()["registries"]["registry_count"] == 7


def test_report_is_deterministic():
    def build() -> SecurityRegistryEvidence:
        service = build_security_registry_service()
        service.record(RegistryKind.TRUST, "anchor", "UCOS-INF-1", recorded_by="p", recorded_at=1)
        return service.report()

    assert build().evidence_id == build().evidence_id


# --------------------------------------------------------------------------- #
# bootstrap_security_registry                                                  #
# --------------------------------------------------------------------------- #


def test_bootstrap_composes_and_publishes_contracts():
    context = bootstrap_platform()
    service = bootstrap_security_registry(context)
    assert isinstance(service, SecurityRegistryService)
    for ref in SECURITY_REGISTRY_CONTRACTS:
        assert ref.name in context.services


def test_bootstrap_emits_completion_event():
    context = bootstrap_platform()
    bootstrap_security_registry(context)
    events = context.events.events_of(SECURITY_REGISTRY_BOOTSTRAP_EVENT)
    assert len(events) == 1
    assert events[0].payload["registry_count"] == 7
    assert set(events[0].payload["registry_contracts"]) == {
        r.name for r in SECURITY_REGISTRY_CONTRACTS
    }


def test_bootstrap_is_idempotent():
    context = bootstrap_platform()
    bootstrap_security_registry(context)
    bootstrap_security_registry(context)
    for ref in SECURITY_REGISTRY_CONTRACTS:
        assert ref.name in context.services


def test_bootstrapped_service_records_end_to_end():
    context = bootstrap_platform()
    service = bootstrap_security_registry(context)
    service.record(RegistryKind.TRUST, "anchor", "UCOS-INF-1", recorded_by="p", recorded_at=1)
    assert len(context.events.events_of(REGISTRY_RECORDED_EVENT)) == 1


def test_bootstrap_is_fail_closed_on_bad_context():
    class _BadContext:
        pass

    with pytest.raises(SecurityBootstrapError):
        bootstrap_security_registry(_BadContext())


def test_bootstrap_reraises_a_security_bootstrap_error_without_double_wrapping(monkeypatch):
    import platform.security.bootstrap as boot

    sentinel = SecurityBootstrapError("inner registry failure")

    def _raise(*_args, **_kwargs):
        raise sentinel

    monkeypatch.setattr(boot, "build_security_registry_service", _raise, raising=True)
    context = bootstrap_platform()
    with pytest.raises(SecurityBootstrapError) as excinfo:
        bootstrap_security_registry(context)
    assert excinfo.value is sentinel


def test_registry_contract_requires_a_name():
    from platform.security.contracts import security_registry_contract
    from platform.security.errors import SecurityContractError

    with pytest.raises(SecurityContractError):
        security_registry_contract("")
