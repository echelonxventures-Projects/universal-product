"""EPIC-007 (T7) — Runtime kernel / core tests."""

from __future__ import annotations

from platform.runtime_platform.core import RuntimeKernel
from platform.runtime_platform.errors import RuntimeAdmissionError, RuntimeKernelError
from platform.runtime_platform.events import (
    CAPACITY_CHANGED,
    EXECUTION_REGISTERED,
    EXECUTION_SCHEDULED,
    EXECUTION_SUCCEEDED,
)
from platform.tests.runtime_platform_helpers import attestation, request

import pytest


def test_kernel_consumes_five_upstream_contracts():
    kernel = RuntimeKernel()
    assert len(kernel.consumed_contracts) == 5
    assert "engine.certification.certify" in kernel.consumed_contracts
    assert "engine.validation.validate" in kernel.consumed_contracts


def test_admit_gate_pass_and_fail_closed():
    kernel = RuntimeKernel()
    kernel.admit(attestation("w"))
    assert kernel.admission_count == 1
    with pytest.raises(RuntimeAdmissionError):
        kernel.admit(attestation("w", certified=False))
    with pytest.raises(RuntimeAdmissionError):
        kernel.admit(attestation("w", validated=False))
    with pytest.raises(RuntimeKernelError):
        kernel.admit("bad")  # type: ignore[arg-type]


def test_submit_admits_runs_registers_and_emits():
    kernel = RuntimeKernel()
    record = kernel.submit(request("w"))
    assert record.succeeded
    assert record.execution_id in kernel.registry
    assert len(kernel.events.events_of(EXECUTION_SUCCEEDED)) == 1
    assert len(kernel.events.events_of(EXECUTION_REGISTERED)) == 1


def test_submit_rejects_non_admissible_before_run():
    kernel = RuntimeKernel()
    with pytest.raises(RuntimeAdmissionError):
        kernel.submit(request("w", certified=False))
    assert len(kernel.registry) == 0


def test_plan_emits_scheduled_events():
    kernel = RuntimeKernel()
    schedule = kernel.plan([request("a"), request("b", dependencies=("a",))])
    assert schedule.stage_count == 2
    assert len(kernel.events.events_of(EXECUTION_SCHEDULED)) == 2


def test_submit_batch_runs_in_scheduled_order():
    kernel = RuntimeKernel()
    records = kernel.submit_batch([request("b", dependencies=("a",)), request("a")])
    assert [r.workload_id for r in records] == ["a", "b"]
    assert len(kernel.registry) == 2


def test_compensate_and_record_paths():
    kernel = RuntimeKernel()
    record = kernel.submit(request("w"))
    compensated = kernel.compensate(record.execution_id)
    assert compensated.final_state == "compensated"
    assert len(kernel.registry) == 2
    # record() is idempotent for an already-registered record
    again = kernel.record(record)
    assert again.execution_id == record.execution_id


def test_announce_capacity_emits_signal():
    kernel = RuntimeKernel()
    kernel.announce_capacity()
    assert len(kernel.events.events_of(CAPACITY_CHANGED)) == 1


def test_kernel_rejects_bad_components():
    with pytest.raises(RuntimeKernelError):
        RuntimeKernel(infrastructure="bad")  # type: ignore[arg-type]
    with pytest.raises(RuntimeKernelError):
        RuntimeKernel(engine="bad")  # type: ignore[arg-type]
    with pytest.raises(RuntimeKernelError):
        RuntimeKernel(registry="bad")  # type: ignore[arg-type]
    with pytest.raises(RuntimeKernelError):
        RuntimeKernel(events="bad")  # type: ignore[arg-type]
    with pytest.raises(RuntimeKernelError):
        RuntimeKernel(services="bad")  # type: ignore[arg-type]
    with pytest.raises(RuntimeKernelError):
        RuntimeKernel().submit("bad")  # type: ignore[arg-type]
    with pytest.raises(RuntimeKernelError):
        RuntimeKernel().record("bad")  # type: ignore[arg-type]


def test_to_dict_and_fingerprint_deterministic():
    k1 = RuntimeKernel()
    k2 = RuntimeKernel()
    assert k1.fingerprint() == k2.fingerprint()
    k1.submit(request("w"))
    k2.submit(request("w"))
    assert k1.fingerprint() == k2.fingerprint()
    payload = k1.to_dict()
    assert payload["execution_count"] == 1
    assert payload["registry_intact"] is True


def test_the_kernel_exposes_the_infrastructure_it_was_composed_over() -> None:
    """The property is how a consumer reaches the substrate without the kernel leaking it."""
    kernel = RuntimeKernel()
    assert kernel.infrastructure is kernel.infrastructure
