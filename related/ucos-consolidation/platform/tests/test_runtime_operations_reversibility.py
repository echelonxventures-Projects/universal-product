"""EC2-TASK-000168 — Runtime Operations reversibility proof tests (EC2-EPIC-012).

Covers the deterministic IP-08 reversibility proof over a certified rollback descriptor:
a well-formed reversible rollback proves reversible; a rollback stripped of its disclosure
fails the proof; a non-rollback input is fail-closed.
"""

from __future__ import annotations

import dataclasses
from platform.runtime_operations.errors import RuntimeReversibilityError
from platform.runtime_operations.facade import RuntimeFacade
from platform.runtime_operations.reversibility import (
    REVERSIBILITY_INDICATORS,
    ReversibilityProof,
    prove_reversibility,
)
from platform.tests.runtime_operations_helpers import runtime_unit

import pytest

_FACADE = RuntimeFacade()


def test_proves_reversible_rollback():
    rb = _FACADE.rollback_descriptor(runtime_unit())
    proof = prove_reversibility(rb)
    assert isinstance(proof, ReversibilityProof)
    assert proof.reversible is True
    assert proof.blockers == ()
    assert proof.strategy == "reversible-checkpoint"
    assert proof.reverts_to_present is False
    assert proof.restore_image
    assert proof.proof_id.startswith("UCOS-RORV-")
    assert proof.to_dict()["reversible"] is True
    assert proof.fingerprint() == prove_reversibility(rb).fingerprint()


def test_reverts_to_present_with_previous():
    rb = _FACADE.rollback_descriptor(runtime_unit(), previous=runtime_unit(pkg="b" * 64))
    proof = prove_reversibility(rb)
    assert proof.reverts_to_present is True
    assert proof.reversible is True


def test_proof_fails_when_disclosure_stripped():
    rb = _FACADE.rollback_descriptor(runtime_unit())
    broken = dataclasses.replace(rb, disclosure={})
    proof = prove_reversibility(broken)
    assert proof.reversible is False
    assert "disclosure-present" in proof.blockers


def test_proof_fails_when_not_declared_reversible():
    rb = _FACADE.rollback_descriptor(runtime_unit())
    broken = dataclasses.replace(rb, reversible=False)
    proof = prove_reversibility(broken)
    assert proof.reversible is False
    assert "declared-reversible" in proof.blockers


def test_proof_fails_on_bad_strategy_and_empty_checkpoint():
    rb = _FACADE.rollback_descriptor(runtime_unit())
    bad_strategy = dataclasses.replace(rb, strategy="irreversible")
    assert "checkpoint-strategy" in prove_reversibility(bad_strategy).blockers
    no_checkpoint = dataclasses.replace(rb, checkpoint={})
    assert "checkpoint-present" in prove_reversibility(no_checkpoint).blockers
    no_restore = dataclasses.replace(rb, kubernetes_rollback={})
    assert "restore-image-present" in prove_reversibility(no_restore).blockers


def test_prove_reversibility_rejects_non_rollback():
    with pytest.raises(RuntimeReversibilityError):
        prove_reversibility("nope")  # type: ignore[arg-type]


def test_indicators_order():
    assert REVERSIBILITY_INDICATORS[0] == "declared-reversible"
    assert REVERSIBILITY_INDICATORS[-1] == "disclosure-present"
