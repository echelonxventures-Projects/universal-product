"""Provider Validation tests (Terminal-04).

Every gate is exercised on its passing path and on at least one failing path, and the
three-valued verdict is tested directly: a declared-but-unbuilt provider must come out
``INCOMPLETE``, never ``PASSED`` and never ``FAILED``.
"""

from __future__ import annotations

import copy
import dataclasses
from collections.abc import Iterable
from dataclasses import replace
from pathlib import Path
from platform.tests.universal_provider_helpers import (
    MEMO_RESOURCE_KIND,
    FaultyProvider,
    MemoProvider,
    memo_capabilities,
    memo_descriptor,
)
from platform.universal_provider import validation as module
from platform.universal_provider import validation as validation_module
from platform.universal_provider.constitution import ProviderOperation
from platform.universal_provider.contracts import (
    ProviderCapability,
    ProviderDescriptor,
    ProviderHealth,
    ProviderQuery,
    ProviderResource,
    ProviderState,
)
from platform.universal_provider.errors import (
    ProviderCapabilityError,
    ProviderValidationError,
)
from platform.universal_provider.lifecycle import (
    LifecycleEntry,
    ProviderLifecycle,
    ProviderPhase,
)
from platform.universal_provider.registry import ProviderRegistry
from platform.universal_provider.sdk import declare_capability, declare_dependency, declare_provider
from platform.universal_provider.validation import (
    AdditiveEvolutionGate,
    CapabilitiesDeclaredGate,
    CertifiableGate,
    ComposabilityGate,
    DeterminismGate,
    EffectsDeclaredGate,
    ExtensibilityGate,
    FailClosedGate,
    FaultIsolationGate,
    GateResult,
    GateSeverity,
    GateStatus,
    IdentityDeclaredGate,
    InterfaceCompleteGate,
    KindOpenGate,
    LifecycleGovernedGate,
    ProvenanceGate,
    ProviderGate,
    ProviderValidator,
    ValidationStatus,
    ValidationSubject,
    default_gates,
    framework_source_files,
)

import pytest


def _subject(**kwargs: object) -> ValidationSubject:
    descriptor = kwargs.pop("descriptor", None) or memo_descriptor()
    return ValidationSubject(descriptor=descriptor, **kwargs)  # type: ignore[arg-type]


def _governed(descriptor=None) -> ValidationSubject:
    """A fully equipped subject: instance, registry, and a governed lifecycle."""
    descriptor = descriptor or memo_descriptor()
    registry = ProviderRegistry.from_descriptors([descriptor])
    lifecycle = ProviderLifecycle()
    lifecycle.declare(descriptor.qualified_id)
    lifecycle.transition(descriptor.qualified_id, ProviderPhase.REGISTERED)
    return ValidationSubject(
        descriptor=descriptor,
        instance=MemoProvider(descriptor),
        registry=registry,
        lifecycle=lifecycle,
    )


# --------------------------------------------------------------------------- wiring


def test_there_is_exactly_one_gate_per_constitutional_article() -> None:
    gates = default_gates()
    assert len(gates) == 14
    assert [gate.article_id for gate in gates] == [f"PC-{n:02d}" for n in range(1, 15)]
    assert len({gate.gate_id for gate in gates}) == 14


def test_a_gate_id_is_read_from_the_article_so_it_cannot_drift() -> None:
    assert InterfaceCompleteGate().gate_id == "PV-01-INTERFACE-COMPLETE"
    assert ExtensibilityGate().gate_id == "PV-14-EXTENSIBLE"


def test_framework_source_files_excludes_the_package_init() -> None:
    files = framework_source_files()
    names = {path.name for path in files}
    assert "constitution.py" in names
    assert "__init__.py" not in names


def test_a_validator_requires_gates_and_refuses_duplicates() -> None:
    with pytest.raises(ProviderValidationError):
        ProviderValidator(gates=[])
    with pytest.raises(ProviderValidationError):
        ProviderValidator(gates=[KindOpenGate(), KindOpenGate()])
    assert ProviderValidator().gate_ids()[0] == "PV-01-INTERFACE-COMPLETE"


def test_a_subject_requires_a_descriptor() -> None:
    with pytest.raises(ProviderValidationError):
        ValidationSubject(descriptor="nope")  # type: ignore[arg-type]


def test_validate_requires_a_subject() -> None:
    with pytest.raises(ProviderValidationError):
        ProviderValidator().validate("nope")  # type: ignore[arg-type]


# ------------------------------------------------------------------- per-gate paths


def test_pv01_interface_complete() -> None:
    passing = InterfaceCompleteGate().evaluate(_governed())
    assert passing.status is GateStatus.PASS
    assert len(passing.evidence["implemented"]) == 6

    class Partial:
        def describe(self) -> None: ...
        def query(self) -> None: ...

    failing = InterfaceCompleteGate().evaluate(_subject(instance=Partial()))
    assert failing.status is GateStatus.FAIL
    assert "verify" in failing.findings[0]

    absent = InterfaceCompleteGate().evaluate(_subject())
    assert absent.status is GateStatus.INDETERMINATE


def test_pv02_kind_open_passes_for_a_provider_the_framework_never_heard_of() -> None:
    result = KindOpenGate().evaluate(_governed())
    assert result.status is GateStatus.PASS
    assert result.evidence["scanned_files"] > 5
    assert result.evidence["kind"] == "memo"


def test_pv02_kind_open_fails_when_the_framework_names_the_provider(tmp_path: Path) -> None:
    """Simulate a framework that was taught about one particular provider."""
    (tmp_path / "leaky.py").write_text('PRIVILEGED = "fixture.memo"\n', encoding="utf-8")
    subject = ValidationSubject(descriptor=memo_descriptor(), framework_root=tmp_path)
    result = KindOpenGate().evaluate(subject)
    assert result.status is GateStatus.FAIL
    assert result.evidence["offenders"] == ["leaky.py"]


def test_pv03_identity_declared() -> None:
    assert IdentityDeclaredGate().evaluate(_governed()).status is GateStatus.PASS
    anonymous = declare_provider("bare.provider", "memo", "1.0.0", capabilities=memo_capabilities())
    failing = IdentityDeclaredGate().evaluate(_subject(descriptor=anonymous))
    assert failing.status is GateStatus.FAIL
    assert any("authority" in finding for finding in failing.findings)
    assert any("source of record" in finding for finding in failing.findings)


def test_pv04_capabilities_declared() -> None:
    assert CapabilitiesDeclaredGate().evaluate(_governed()).status is GateStatus.PASS
    query_only = memo_descriptor(capabilities=memo_capabilities()[:1])
    failing = CapabilitiesDeclaredGate().evaluate(_subject(descriptor=query_only))
    assert failing.status is GateStatus.FAIL
    assert any("'fetch'" in finding for finding in failing.findings)
    keyless = memo_descriptor(
        capabilities=(
            declare_capability("memo.notes", "query"),
            *memo_capabilities()[1:],
        )
    )
    keyless_result = CapabilitiesDeclaredGate().evaluate(_subject(descriptor=keyless))
    assert keyless_result.status is GateStatus.FAIL
    assert any("resource kind" in finding for finding in keyless_result.findings)
    assert any("selector keys" in finding for finding in keyless_result.findings)


def test_pv05_determinism_is_measured_by_repeated_execution() -> None:
    passing = DeterminismGate().evaluate(_governed())
    assert passing.status is GateStatus.PASS
    assert "memo.notes" in passing.evidence["measured"]


def test_pv05_fails_when_a_deterministic_capability_is_not_reproducible() -> None:
    class DriftingProvider(MemoProvider):
        def __init__(self, descriptor, config=None) -> None:  # type: ignore[no-untyped-def]
            super().__init__(descriptor, config)
            self._calls = 0

        def resolve_query(
            self, capability: ProviderCapability, request: ProviderQuery
        ) -> Iterable[ProviderResource]:
            self._calls += 1
            yield self.resource(f"drift-{self._calls}", MEMO_RESOURCE_KIND, {})

    descriptor = memo_descriptor()
    result = DeterminismGate().evaluate(
        _subject(descriptor=descriptor, instance=DriftingProvider(descriptor))
    )
    assert result.status is GateStatus.FAIL
    assert "different result" in result.findings[0]


def test_pv05_refuses_a_provider_declaring_nothing_deterministic() -> None:
    nondeterministic = memo_descriptor(
        capabilities=tuple(
            declare_capability(
                capability.name,
                capability.operation,
                resource_kind=capability.resource_kind,
                selector_keys=capability.selector_keys,
                deterministic=False,
            )
            for capability in memo_capabilities()
        )
    )
    result = DeterminismGate().evaluate(_subject(descriptor=nondeterministic))
    assert result.status is GateStatus.FAIL


def test_pv05_is_indeterminate_without_an_instance_or_an_executable_capability() -> None:
    assert DeterminismGate().evaluate(_subject()).status is GateStatus.INDETERMINATE
    gated = memo_descriptor(
        capabilities=(
            declare_capability(
                "memo.notes",
                "query",
                resource_kind=MEMO_RESOURCE_KIND,
                selector_keys=("tag",),
                required_selector_keys=("tag",),
            ),
            *memo_capabilities()[1:],
        )
    )
    result = DeterminismGate().evaluate(_subject(descriptor=gated, instance=MemoProvider(gated)))
    assert result.status is GateStatus.INDETERMINATE


def test_pv05_reports_a_refused_query_as_a_finding() -> None:
    descriptor = memo_descriptor()
    result = DeterminismGate().evaluate(
        _subject(descriptor=descriptor, instance=FaultyProvider(descriptor))
    )
    assert result.status is GateStatus.FAIL
    assert "query refused" in result.findings[0]


def test_pv06_provenance_samples_and_attests_every_resource() -> None:
    passing = ProvenanceGate().evaluate(_governed())
    assert passing.status is GateStatus.PASS
    assert passing.evidence["sampled"] == 3
    assert passing.evidence["attested"] == 3


def test_pv06_fails_without_a_declared_source_of_record() -> None:
    descriptor = memo_descriptor(source_of_record="")
    result = ProvenanceGate().evaluate(_subject(descriptor=descriptor))
    assert result.status is GateStatus.FAIL
    assert ProvenanceGate().evaluate(_subject()).status is GateStatus.INDETERMINATE


def test_pv06_fails_when_an_attestation_cannot_be_produced() -> None:
    class UnattestableProvider(MemoProvider):
        def provenance_chain(self, resource: ProviderResource) -> tuple[str, ...]:
            return ()

    descriptor = memo_descriptor()
    result = ProvenanceGate().evaluate(
        _subject(descriptor=descriptor, instance=UnattestableProvider(descriptor))
    )
    assert result.status is GateStatus.FAIL
    assert "unverified" in result.findings[0]


def test_pv07_fail_closed_probes_three_refusal_paths() -> None:
    passing = FailClosedGate().evaluate(_governed())
    assert passing.status is GateStatus.PASS
    assert set(passing.evidence["probes"]) == {
        "undeclared_capability",
        "undeclared_selector",
        "absent_resource",
    }
    assert FailClosedGate().evaluate(_subject()).status is GateStatus.INDETERMINATE


def test_pv07_fails_a_provider_that_serves_anything_it_is_asked_for() -> None:
    class PermissiveProvider(MemoProvider):
        def query(self, request: ProviderQuery):  # type: ignore[override]
            return super().query(ProviderQuery(capability="memo.notes"))

        def fetch(self, resource_id: str) -> ProviderResource:
            return self.resource(resource_id, MEMO_RESOURCE_KIND, {"fabricated": True})

    descriptor = memo_descriptor()
    result = FailClosedGate().evaluate(
        _subject(descriptor=descriptor, instance=PermissiveProvider(descriptor))
    )
    assert result.status is GateStatus.FAIL
    assert len(result.findings) == 3


def test_pv07_treats_an_untyped_escape_as_a_finding() -> None:
    class UntypedProvider(MemoProvider):
        def query(self, request: ProviderQuery):  # type: ignore[override]
            raise RuntimeError("raw")

        def fetch(self, resource_id: str) -> ProviderResource:
            raise RuntimeError("raw")

    descriptor = memo_descriptor()
    result = FailClosedGate().evaluate(
        _subject(descriptor=descriptor, instance=UntypedProvider(descriptor))
    )
    assert result.status is GateStatus.FAIL
    assert all("untyped" in finding for finding in result.findings)


def test_pv07_notes_when_there_is_no_query_capability_to_probe() -> None:
    descriptor = memo_descriptor(
        capabilities=(
            declare_capability("memo.note", "fetch", resource_kind=MEMO_RESOURCE_KIND),
            declare_capability("memo.attestation", "verify", resource_kind=MEMO_RESOURCE_KIND),
        )
    )

    class FetchOnly:
        def describe(self):  # type: ignore[no-untyped-def]
            return descriptor

        def capabilities(self):  # type: ignore[no-untyped-def]
            return descriptor.capabilities

        def health(self) -> ProviderHealth:
            return ProviderHealth(provider_id=descriptor.provider_id, state=ProviderState.SERVING)

        def query(self, request: ProviderQuery):  # type: ignore[no-untyped-def]
            raise ProviderValidationError("no query surface")

        def fetch(self, resource_id: str):  # type: ignore[no-untyped-def]
            raise ProviderValidationError("absent")

        def verify(self, resource_id: str):  # type: ignore[no-untyped-def]
            raise ProviderValidationError("absent")

    result = FailClosedGate().evaluate(_subject(descriptor=descriptor, instance=FetchOnly()))
    assert result.status is GateStatus.FAIL
    assert any("no query capability" in finding for finding in result.findings)


def test_pv08_effects_declared() -> None:
    passing = EffectsDeclaredGate().evaluate(_governed())
    assert passing.status is GateStatus.PASS
    assert passing.evidence["declared_effects"] == ["mem:read"]


def test_pv08_refuses_a_malformed_effect() -> None:
    descriptor = memo_descriptor(
        capabilities=(
            declare_capability(
                "memo.notes",
                "query",
                resource_kind=MEMO_RESOURCE_KIND,
                selector_keys=("tag",),
                effects=("filesystem",),
            ),
            *memo_capabilities()[1:],
        )
    )
    result = EffectsDeclaredGate().evaluate(_subject(descriptor=descriptor))
    assert result.status is GateStatus.FAIL
    assert "domain:action" in result.findings[0]


def test_pv08_refuses_determinism_declared_alongside_a_mutating_effect() -> None:
    descriptor = memo_descriptor(
        capabilities=(
            declare_capability(
                "memo.notes",
                "query",
                resource_kind=MEMO_RESOURCE_KIND,
                selector_keys=("tag",),
                deterministic=True,
                effects=("db:write",),
            ),
            *memo_capabilities()[1:],
        )
    )
    result = EffectsDeclaredGate().evaluate(_subject(descriptor=descriptor))
    assert result.status is GateStatus.FAIL
    assert "mutating effect" in result.findings[0]


def test_pv08_permits_a_mutating_effect_that_is_honestly_non_deterministic() -> None:
    descriptor = memo_descriptor(
        capabilities=(
            declare_capability(
                "memo.notes",
                "query",
                resource_kind=MEMO_RESOURCE_KIND,
                selector_keys=("tag",),
                deterministic=False,
                effects=("net:send",),
            ),
            *memo_capabilities()[1:],
        )
    )
    assert EffectsDeclaredGate().evaluate(_subject(descriptor=descriptor)).status is GateStatus.PASS


def test_pv09_fault_isolation() -> None:
    passing = FaultIsolationGate().evaluate(_governed())
    assert passing.status is GateStatus.PASS
    assert passing.evidence["health_state"] == "serving"
    assert FaultIsolationGate().evaluate(_subject()).status is GateStatus.INDETERMINATE


def test_pv09_fails_when_health_raises() -> None:
    class ExplodingHealth(MemoProvider):
        def health(self) -> ProviderHealth:
            raise RuntimeError("no health")

    descriptor = memo_descriptor()
    result = FaultIsolationGate().evaluate(
        _subject(descriptor=descriptor, instance=ExplodingHealth(descriptor))
    )
    assert result.status is GateStatus.FAIL
    assert "raised" in result.findings[0]


def test_pv09_fails_when_health_returns_the_wrong_type_or_a_fault_escapes() -> None:
    class WrongHealth(MemoProvider):
        def health(self):  # type: ignore[override]
            return "fine"

        def fetch(self, resource_id: str) -> ProviderResource:
            raise RuntimeError("raw")

    descriptor = memo_descriptor()
    result = FaultIsolationGate().evaluate(
        _subject(descriptor=descriptor, instance=WrongHealth(descriptor))
    )
    assert result.status is GateStatus.FAIL
    assert len(result.findings) == 2


def test_pv09_fails_when_an_absent_fetch_neither_returns_nor_raises() -> None:
    class FabricatingProvider(MemoProvider):
        def fetch(self, resource_id: str) -> ProviderResource:
            return self.resource(resource_id, MEMO_RESOURCE_KIND, {})

    descriptor = memo_descriptor()
    result = FaultIsolationGate().evaluate(
        _subject(descriptor=descriptor, instance=FabricatingProvider(descriptor))
    )
    assert result.status is GateStatus.FAIL


def test_pv10_lifecycle_governed() -> None:
    passing = LifecycleGovernedGate().evaluate(_governed())
    assert passing.status is GateStatus.PASS
    assert passing.evidence["phase"] == "registered"
    assert LifecycleGovernedGate().evaluate(_subject()).status is GateStatus.INDETERMINATE


def test_pv10_fails_for_an_untracked_provider_and_a_broken_chain() -> None:
    untracked = _subject(lifecycle=ProviderLifecycle())
    assert LifecycleGovernedGate().evaluate(untracked).status is GateStatus.FAIL
    subject = _governed()
    lifecycle = subject.lifecycle
    assert lifecycle is not None
    original = lifecycle.entries[0]
    lifecycle._entries[0] = LifecycleEntry(  # noqa: SLF001 - tamper simulation
        sequence=original.sequence,
        qualified_id=original.qualified_id,
        from_phase=ProviderPhase.CERTIFIED,
        to_phase=ProviderPhase.ACTIVE,
        reason=original.reason,
        evidence_ref=original.evidence_ref,
        previous_hash=original.previous_hash,
        entry_hash=original.entry_hash,
    )
    result = LifecycleGovernedGate().evaluate(subject)
    assert result.status is GateStatus.FAIL
    assert any("hash chain" in finding for finding in result.findings)


def test_pv11_certifiable() -> None:
    passing = CertifiableGate().evaluate(_governed())
    assert passing.status is GateStatus.PASS
    assert CertifiableGate().evaluate(_subject()).status is GateStatus.INDETERMINATE
    unregistered = _subject(registry=ProviderRegistry())
    assert CertifiableGate().evaluate(unregistered).status is GateStatus.FAIL


def test_pv11_fails_when_the_descriptor_diverges_from_the_registered_one() -> None:
    registered = memo_descriptor()
    registry = ProviderRegistry.from_descriptors([registered])
    drifted = memo_descriptor(source_of_record="a substrate nobody registered")
    result = CertifiableGate().evaluate(ValidationSubject(descriptor=drifted, registry=registry))
    assert result.status is GateStatus.FAIL
    assert "differs from the registered descriptor" in result.findings[0]


def test_pv11_fails_in_a_non_certifiable_phase() -> None:
    descriptor = memo_descriptor()
    registry = ProviderRegistry.from_descriptors([descriptor])
    lifecycle = ProviderLifecycle()
    lifecycle.declare(descriptor.qualified_id)
    result = CertifiableGate().evaluate(
        ValidationSubject(descriptor=descriptor, registry=registry, lifecycle=lifecycle)
    )
    assert result.status is GateStatus.FAIL
    assert "not a certifiable phase" in result.findings[0]


def test_pv12_composability() -> None:
    assert ComposabilityGate().evaluate(_governed()).status is GateStatus.PASS
    assert ComposabilityGate().evaluate(_subject()).status is GateStatus.PASS


def test_pv12_is_indeterminate_when_dependencies_cannot_be_resolved() -> None:
    dependent = memo_descriptor(dependencies=(declare_dependency("some.dependency"),))
    result = ComposabilityGate().evaluate(_subject(descriptor=dependent))
    assert result.status is GateStatus.INDETERMINATE


def test_pv12_fails_on_an_unresolvable_dependency() -> None:
    dependent = memo_descriptor(dependencies=(declare_dependency("gone.away"),))
    registry = ProviderRegistry.from_descriptors([dependent])
    result = ComposabilityGate().evaluate(
        ValidationSubject(descriptor=dependent, registry=registry)
    )
    assert result.status is GateStatus.FAIL


def test_pv13_additive_evolution() -> None:
    assert AdditiveEvolutionGate().evaluate(_governed()).status is GateStatus.PASS
    assert AdditiveEvolutionGate().evaluate(_subject()).status is GateStatus.INDETERMINATE


def test_pv13_detects_a_narrowed_successor_smuggled_into_the_registry() -> None:
    """The registry refuses narrowing, so the gate is proven against a forced registry."""
    v1 = memo_descriptor(version="1.0.0")
    v2 = memo_descriptor(version="1.1.0", capabilities=memo_capabilities()[:1])
    registry = ProviderRegistry()
    registry.register(v1)
    registry._records[v2.qualified_id] = registry._records[v1.qualified_id].__class__(  # noqa: SLF001
        sequence=2, descriptor=v2, descriptor_hash=v2.content_hash(), registration_id="forced"
    )
    result = AdditiveEvolutionGate().evaluate(ValidationSubject(descriptor=v2, registry=registry))
    assert result.status is GateStatus.FAIL
    assert "removed" in result.findings[0]


def test_pv14_extensibility() -> None:
    passing = ExtensibilityGate().evaluate(_governed())
    assert passing.status is GateStatus.PASS
    assert passing.evidence["entry_point"].endswith(":build_memo")


def test_pv14_is_indeterminate_for_a_declared_only_provider() -> None:
    result = ExtensibilityGate().evaluate(_subject(descriptor=memo_descriptor(entry_point="")))
    assert result.status is GateStatus.INDETERMINATE
    assert "declared, not yet realizable" in result.findings[0]


def test_pv14_fails_on_a_malformed_entry_point() -> None:
    result = ExtensibilityGate().evaluate(
        _subject(descriptor=memo_descriptor(entry_point="no-colon-here"))
    )
    assert result.status is GateStatus.FAIL


# ----------------------------------------------------------------- aggregate verdict


def test_a_fully_equipped_conformant_provider_passes_every_gate() -> None:
    report = ProviderValidator().validate(_governed())
    assert report.status is ValidationStatus.PASSED
    assert report.passed is True
    assert report.counts() == {
        "total": 14,
        "pass": 14,
        "fail": 0,
        "indeterminate": 0,
        "blocking_failures": 0,
    }
    assert report.failures() == ()
    assert report.result("PV-01-INTERFACE-COMPLETE").status is GateStatus.PASS
    assert report.report_hash() == ProviderValidator().validate(_governed()).report_hash()


def test_a_declared_only_provider_is_incomplete_not_failed() -> None:
    descriptor = memo_descriptor(entry_point="")
    registry = ProviderRegistry.from_descriptors([descriptor])
    lifecycle = ProviderLifecycle()
    lifecycle.declare(descriptor.qualified_id)
    lifecycle.transition(descriptor.qualified_id, ProviderPhase.REGISTERED)
    report = ProviderValidator().validate(
        ValidationSubject(descriptor=descriptor, registry=registry, lifecycle=lifecycle)
    )
    assert report.status is ValidationStatus.INCOMPLETE
    assert report.failures() == ()
    assert {r.gate_id for r in report.indeterminate()} >= {
        "PV-01-INTERFACE-COMPLETE",
        "PV-14-EXTENSIBLE",
    }


def test_a_blocking_failure_outranks_indeterminacy() -> None:
    descriptor = memo_descriptor(entry_point="", source_of_record="")
    report = ProviderValidator().validate(ValidationSubject(descriptor=descriptor))
    assert report.status is ValidationStatus.FAILED


def test_an_unknown_gate_lookup_fails_closed() -> None:
    report = ProviderValidator().validate(_governed())
    with pytest.raises(ProviderValidationError):
        report.result("PV-99-IMAGINARY")


def test_a_raising_gate_is_recorded_rather_than_aborting_the_pass() -> None:
    class ExplodingGate(ProviderGate):
        article_id = "PC-01"

        def evaluate(self, subject: ValidationSubject) -> GateResult:
            raise RuntimeError("gate exploded")

    report = ProviderValidator(gates=[ExplodingGate()]).validate(_governed())
    assert report.status is ValidationStatus.FAILED
    result = report.result("PV-01-INTERFACE-COMPLETE")
    assert result.summary == "gate execution raised"
    assert "RuntimeError" in result.findings[0]


def test_an_advisory_failure_does_not_block() -> None:
    class AdvisoryGate(ProviderGate):
        article_id = "PC-02"
        severity = GateSeverity.ADVISORY

        def evaluate(self, subject: ValidationSubject) -> GateResult:
            return self._fail("advisory only", ("noted",))

    report = ProviderValidator(gates=[AdvisoryGate()]).validate(_governed())
    assert report.status is ValidationStatus.PASSED
    assert report.counts()["blocking_failures"] == 0
    assert report.result("PV-02-KIND-OPEN").blocking_failure is False


def test_report_projection_carries_the_constitution_it_was_measured_against() -> None:
    payload = ProviderValidator().validate(_governed()).to_dict()
    assert payload["constitution_id"] == "UCOS-PROVIDER-CONSTITUTION"
    assert payload["status"] == "passed"
    assert len(payload["results"]) == 14
    assert payload["results"][0]["article_id"] == "PC-01"


def test_the_query_operation_gate_binding_is_enforced() -> None:
    """A capability bound to the wrong operation is refused, not silently accepted."""
    provider = MemoProvider(memo_descriptor())
    with pytest.raises(ProviderCapabilityError) as exc:
        provider.query(ProviderQuery(capability="memo.attestation"))
    assert exc.value.code == "UPA-CAPABILITY"
    assert "not bound to the QUERY operation" in exc.value.message
    assert ProviderOperation.VERIFY.value == "verify"


# --------------------------------------------------------------------------------------
# The refusals the gates carry that no test had ever produced.
#
# WHY THESE EXIST. Every gate above has a passing path and "at least one failing path" —
# which is exactly the gap: a gate that reports SEVERAL distinct findings had only ever
# produced one of them, so the others were unexecuted. A finding nobody has seen is a
# sentence nobody has checked, and the whole value of a gate is the specificity of what it
# says when it refuses.
#
# THE DESCRIPTORS ARE FORGED, and that is the finding restated. `ProviderDescriptor` and
# `ProviderIdentity` refuse every one of these malformations at CONSTRUCTION, which is why
# no test could reach the gate that also refuses them: the constructor gets there first.
# The gate is not therefore redundant — a descriptor arriving from a catalog manifest, a
# future release, or a hand-edited file has not passed through this process's constructor —
# so the only way to show it working is to hand it the state the constructor forbids.
# --------------------------------------------------------------------------------------


def _forced(descriptor=None, **fields):
    """A descriptor carrying a value its own constructor refuses."""

    forged = copy.copy(descriptor if descriptor is not None else memo_descriptor())
    identity_fields = {k: v for k, v in fields.items() if k in {"name", "authority", "kind"}}
    if identity_fields:
        identity = copy.copy(forged.identity)
        for key, value in identity_fields.items():
            object.__setattr__(identity, key, value)
        object.__setattr__(forged, "identity", identity)
    for key, value in fields.items():
        if key not in identity_fields:
            object.__setattr__(forged, key, value)
    return forged


def test_pv1_names_the_interface_the_descriptor_actually_declares() -> None:
    descriptor = _forced(interface="some.other.interface")
    result = InterfaceCompleteGate().evaluate(
        _subject(descriptor=descriptor, instance=MemoProvider(memo_descriptor()))
    )
    assert result.status is GateStatus.FAIL
    assert any("some.other.interface" in finding for finding in result.findings)


def test_pv2_reports_a_malformed_kind_as_malformed_rather_than_absent() -> None:
    result = KindOpenGate().evaluate(_subject(descriptor=_forced(kind="  ")))
    assert result.status is GateStatus.FAIL
    assert any("kind is malformed" in finding for finding in result.findings)


@pytest.mark.parametrize(
    ("field", "expected"),
    [
        ("name", "declares no name"),
        ("authority", "declares no authority"),
        ("source_of_record", "declares no source of record"),
    ],
)
def test_pv3_names_each_missing_part_of_a_declared_identity(field, expected) -> None:
    result = IdentityDeclaredGate().evaluate(_subject(descriptor=_forced(**{field: "   "})))
    assert result.status is GateStatus.FAIL
    assert any(expected in finding for finding in result.findings)


def test_pv5_refuses_a_query_that_does_not_return_a_response() -> None:
    """Determinism cannot be measured over something that is not a response, and reporting
    "not deterministic" for it would be a wrong answer rather than no answer."""

    class NotAResponse(MemoProvider):
        def query(self, request):  # type: ignore[override]
            return "not a ProviderResponse"

    descriptor = memo_descriptor()
    result = DeterminismGate().evaluate(
        _subject(descriptor=descriptor, instance=NotAResponse(descriptor))
    )
    assert result.status is GateStatus.FAIL
    assert any("did not return a ProviderResponse" in finding for finding in result.findings)


def test_pv6_reports_a_refused_query_rather_than_an_unprovenanced_resource() -> None:
    descriptor = memo_descriptor()
    result = ProvenanceGate().evaluate(
        _subject(descriptor=descriptor, instance=FaultyProvider(descriptor))
    )
    assert result.status is GateStatus.FAIL
    assert any("query refused" in finding for finding in result.findings)


def test_pv13_reports_a_kind_that_changed_inside_one_major_version_line() -> None:
    """Removing a capability and changing the kind are different breaks, and a successor
    that did both would otherwise be reported as only one of them."""
    registry = ProviderRegistry()
    registry.register(memo_descriptor(version="1.0.0"))
    successor = _forced(memo_descriptor(version="1.1.0"), kind="memo.other")
    result = AdditiveEvolutionGate().evaluate(_subject(descriptor=successor, registry=registry))
    assert result.status is GateStatus.FAIL
    assert any("declares kind" in finding for finding in result.findings)


def test_pv14_refuses_a_descriptor_that_cannot_be_rebuilt_from_its_own_data(monkeypatch) -> None:
    """Forged at the boundary the gate reads through: a descriptor whose serialisation
    cannot be parsed back is a provider that is not expressible as data, and the gate must
    say so rather than crash."""

    class _Unrebuildable:
        @staticmethod
        def from_dict(_payload):
            raise ProviderValidationError("descriptor cannot be rebuilt", {})

    # the subject is built FIRST: `ValidationSubject` type-checks through the same
    # module-level name the gate rebuilds through, so patching before construction would
    # forge the wrong boundary and refuse the subject instead of the round trip.
    subject = _subject()
    monkeypatch.setattr(module, "ProviderDescriptor", _Unrebuildable)
    result = ExtensibilityGate().evaluate(subject)
    assert result.status is GateStatus.FAIL
    assert any("cannot be rebuilt" in finding for finding in result.findings)


def test_the_validator_publishes_the_gates_it_will_run() -> None:
    validator = ProviderValidator()
    assert tuple(gate.gate_id for gate in validator.gates) == validator.gate_ids()
    assert len(validator.gates) == len(default_gates())


# --------------------------------------------------------------------------- #
# The gate findings a WELL-FORMED provider never produces
#
# Every gate above is exercised against the memo provider, which satisfies all of them —
# that is the claim. It also means each gate's finding arms were dead, and a gate whose
# refusal has never executed is a gate nobody has checked. Each is reached by handing the
# gate a subject that is defective in exactly the one way the finding names.
# --------------------------------------------------------------------------- #


class _Unstable(ProviderDescriptor):
    """A descriptor whose content hash changes between two computations.

    A real descriptor cannot do this — the hash is a pure function of the declaration —
    which is exactly why the check had never fired and why the subject type is preserved:
    the gate must be given something it accepts as a descriptor.
    """

    def content_hash(self) -> str:
        _COUNTER.append(len(_COUNTER))
        return f"{super().content_hash()}-{len(_COUNTER)}"


_COUNTER: list[int] = []


def test_a_descriptor_whose_hash_is_not_stable_is_refused() -> None:
    """CONTENT ADDRESSING IS THE WHOLE IDENTITY CLAIM.

    A descriptor is identified by the digest of its own declaration, so a hash that differs
    between two computations means the identity is not a function of the content — after
    which every registry lookup, every ledger entry and every certificate points at a
    provider whose identity changes while it is being read.
    """
    genuine = memo_descriptor()
    unstable = _Unstable(**{f.name: getattr(genuine, f.name) for f in dataclasses.fields(genuine)})
    result = IdentityDeclaredGate().evaluate(_subject(descriptor=unstable))

    assert result.status is GateStatus.FAIL
    assert any("not stable" in f for f in result.findings)


def test_provenance_skips_a_capability_that_requires_a_selector() -> None:
    """A CAPABILITY THAT REQUIRES A SELECTOR CANNOT BE SAMPLED BLIND.

    The provenance gate samples QUERY capabilities by issuing a selector-less query. One
    that declares required selector keys would refuse that query — correctly — and the
    refusal would be recorded as a provenance finding against a provider doing exactly what
    it declared. So it is skipped, and the sampling stays a measurement of the capabilities
    it can actually reach.
    """
    descriptor = memo_descriptor(
        capabilities=(
            declare_capability(
                "memo.filtered",
                ProviderOperation.QUERY,
                resource_kind="memo.note",
                description="Enumerate notes for one tag.",
                selector_keys=("tag",),
                required_selector_keys=("tag",),
                deterministic=True,
                effects=("mem:read",),
            ),
            *memo_capabilities(),
        )
    )
    subject = _governed(descriptor)
    result = ProvenanceGate().evaluate(subject)

    assert result.status is not GateStatus.FAIL, result.findings
    assert not any("memo.filtered" in f for f in result.findings)


def test_provenance_refuses_a_resource_with_no_source_no_hash_or_no_type() -> None:
    """THREE THINGS MAKE A RESOURCE ATTRIBUTABLE, and each absence is reported separately.

    A value that is not a resource at all cannot be attributed to anything. A resource with
    no source of record cannot be traced back to where it came from. A resource with no
    content hash cannot be shown to be the thing that was fetched. Each stops the walk for
    that resource — checking a hash on a value that is not a resource would raise inside a
    gate whose job is to report, not to fail.

    THE FIRST OF THE THREE CANNOT ARRIVE IN A REAL RESPONSE. `ProviderResponse.__post_init__`
    already refuses a non-resource, so the gate's check is a second defence over a response
    assembled some other way — a rehydrated one, or a provider that returns a response-shaped
    object of its own. It is reached here with exactly that: a stand-in exposing `.resources`
    without the contract type's constructor between it and the gate.
    """

    class _LooseResponse:
        def __init__(self, resources) -> None:
            self.resources = resources

    class _Hashless(ProviderResource):
        """A resource whose content hash is empty.

        ``resource_hash`` is a computed PROPERTY, so a real resource can never have one —
        which is why the gate's check had never fired. It is the second defence for a
        resource that arrives already hashless from somewhere the property does not govern.
        """

        @property
        def resource_hash(self) -> str:
            return ""

    def _sourceless(resource):
        """A resource whose provenance names no source of record."""
        clone = replace(resource)
        object.__setattr__(clone, "provenance", {**resource.provenance, "source_of_record": ""})
        return clone

    class _Loose(MemoProvider):
        def query(self, request):
            genuine = super().query(request).resources[0]
            return _LooseResponse(
                (
                    "not a resource at all",
                    _sourceless(genuine),
                    _Hashless(
                        **{f.name: getattr(genuine, f.name) for f in dataclasses.fields(genuine)}
                    ),
                )
            )

    descriptor = memo_descriptor()
    governed = _governed(descriptor)
    result = ProvenanceGate().evaluate(
        ValidationSubject(
            descriptor=descriptor,
            instance=_Loose(descriptor),
            registry=governed.registry,
            lifecycle=governed.lifecycle,
        )
    )

    assert result.status is GateStatus.FAIL
    assert any("non-resource value returned" in f for f in result.findings)
    assert any("no source of record" in f for f in result.findings)
    assert any("no content hash" in f for f in result.findings)


def test_lifecycle_refuses_a_ledger_recording_a_transition_the_law_forbids() -> None:
    """THE LEDGER IS EVIDENCE, SO IT IS CHECKED AGAINST THE LAW IT RECORDS.

    `ProviderLifecycle.transition` refuses an illegal move, so a ledger built through it can
    never hold one — which is why this arm was dead. It is the check that would notice a
    ledger assembled some other way: rehydrated from data, or written by a future caller. A
    ledger whose entries are trusted because the API that usually writes them is careful is
    not evidence, it is an assumption.
    """
    descriptor = memo_descriptor()
    subject = _governed(descriptor)
    history = subject.lifecycle.history(descriptor.qualified_id)
    forged = replace(
        history[0], from_phase=ProviderPhase.REGISTERED, to_phase=ProviderPhase.DECLARED
    )

    class _Forged:
        def __init__(self, real) -> None:
            self._real = real

        def history(self, qualified_id: str):
            return (forged,)

        def __getattr__(self, name: str):
            return getattr(self._real, name)

    result = LifecycleGovernedGate().evaluate(
        ValidationSubject(
            descriptor=descriptor,
            instance=subject.instance,
            registry=subject.registry,
            lifecycle=_Forged(subject.lifecycle),
        )
    )

    assert result.status is GateStatus.FAIL
    assert any("illegal transition" in f for f in result.findings)


def test_a_descriptor_that_round_trips_lossily_is_refused() -> None:
    """EXPRESSIBLE AS DATA MEANS THE DATA IS THE WHOLE PROVIDER.

    The gate serializes a descriptor, rebuilds it, and compares content hashes. A rebuild
    that raises is one failure and a rebuild that SUCCEEDS with a different hash is another
    — the second is worse, because nothing refused and a catalogue round trip would silently
    drop whatever did not survive. A real descriptor cannot do this, which is why the arm was
    dead; it is reached with a descriptor whose rebuild is deliberately not itself.
    """

    genuine = memo_descriptor()

    class _Lossy(ProviderDescriptor):
        @classmethod
        def from_dict(cls, payload):
            rebuilt = ProviderDescriptor.from_dict(payload)
            return replace(rebuilt, description=f"{rebuilt.description} (lost something)")

    # The subject is built BEFORE the patch: `ValidationSubject` type-checks its descriptor
    # against the same name, so patching first would refuse a genuine descriptor.
    subject = _subject(descriptor=genuine)
    original = validation_module.ProviderDescriptor
    try:
        validation_module.ProviderDescriptor = _Lossy
        result = ExtensibilityGate().evaluate(subject)
    finally:
        validation_module.ProviderDescriptor = original

    assert result.status is GateStatus.FAIL
    assert any("round trip through data is lossy" in f for f in result.findings)
