"""EPIC-007 (T7) — Cross-run determinism / reproducibility tests.

Two independently composed runtime platforms driven through an identical ordered
sequence of governed operations must produce byte-identical recorded state — the
reproducibility guarantee (P5): no wall-clock, no ambient state.
"""

from __future__ import annotations

from platform.runtime_platform.service import build_runtime_platform_service
from platform.tests.runtime_platform_helpers import request, workflow


def _drive():
    service = build_runtime_platform_service()
    service.submit_batch([request("a"), request("b", dependencies=("a",))])
    service.run_workflow(workflow())
    service.run_workflow(workflow("wf-2", failing_step="c"))
    return service


def test_kernel_fingerprint_reproducible():
    assert _drive().kernel.fingerprint() == _drive().kernel.fingerprint()


def test_registry_fingerprint_reproducible():
    assert _drive().kernel.registry.fingerprint() == _drive().kernel.registry.fingerprint()


def test_evidence_fingerprint_reproducible():
    assert _drive().evidence().fingerprint() == _drive().evidence().fingerprint()


def test_event_log_is_reproducible():
    a = _drive()
    b = _drive()
    assert [e.event_type for e in a.events.events] == [e.event_type for e in b.events.events]
    assert [e.event_id for e in a.events.events] == [e.event_id for e in b.events.events]
