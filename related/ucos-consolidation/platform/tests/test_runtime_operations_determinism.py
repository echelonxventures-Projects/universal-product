"""EC2-TASK-000172 — Runtime Operations determinism tests (EC2-EPIC-012, P5).

Proves that identical inputs and an identical ordered sequence of governed operations
yield byte-identical content-addressed identities, descriptor fingerprints, ledger chains,
and runtime evidence — the reproducibility invariant (P5) — with no wall-clock or ambient
state leaking into any fingerprint.
"""

from __future__ import annotations

from platform.runtime_operations.facade import RuntimeFacade
from platform.runtime_operations.operations import RuntimeOperationPlanner
from platform.tests.runtime_operations_helpers import (
    certification_record,
    runtime_unit,
    service_fixture,
    session,
)

_FACADE = RuntimeFacade()


def test_descriptor_generation_is_deterministic():
    unit = runtime_unit()
    a = _FACADE.deployment_descriptor(unit).to_dict()
    b = _FACADE.deployment_descriptor(unit).to_dict()
    assert a == b


def test_operation_id_is_stable_for_identical_operation():
    p1 = RuntimeOperationPlanner().plan_deploy(
        runtime_unit(), certification_record(), owner_subject="op@x", tenant="acme"
    )
    p2 = RuntimeOperationPlanner().plan_deploy(
        runtime_unit(), certification_record(), owner_subject="op@x", tenant="acme"
    )
    assert p1.record.operation_id == p2.record.operation_id
    assert p1.record.fingerprint() == p2.record.fingerprint()
    assert p1.record.descriptor_fingerprint() == p2.record.descriptor_fingerprint()


def test_ledger_chain_is_reproducible():
    def build_chain():
        auth, service = service_fixture()
        sess = session(auth)
        service.deploy(sess.session_id, runtime_unit(), certification_record(), now=1)
        service.rollback(
            sess.session_id, runtime_unit(version="2.0.0"), certification_record(), now=2
        )
        return service.ledger.head_hash

    assert build_chain() == build_chain()


def test_evidence_fingerprint_is_reproducible():
    def build_evidence():
        auth, service = service_fixture()
        sess = session(auth)
        service.deploy(sess.session_id, runtime_unit(), certification_record(), now=1)
        return service.evidence().fingerprint()

    assert build_evidence() == build_evidence()
