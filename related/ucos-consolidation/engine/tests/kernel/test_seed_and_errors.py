"""Tests for the founding-meta-type seed table and kernel error surface."""

from __future__ import annotations

from engine.kernel.errors import GovernanceRejection, KernelError
from engine.kernel.seed import (
    FOUNDING_METATYPES,
    FOUNDING_NAMESPACE,
    founding_metatype_keys,
)


def test_seed_table_is_well_formed_and_unique():
    keys = [key for key, _n, _d in FOUNDING_METATYPES]
    assert len(keys) == len(set(keys))  # no duplicates
    for key, name, desc in FOUNDING_METATYPES:
        assert key and name and desc
    assert FOUNDING_NAMESPACE == "umk.metatype"


def test_founding_metatype_keys_sorted():
    keys = founding_metatype_keys()
    assert list(keys) == sorted(keys)
    assert "Capability" in keys


def test_kernel_error_renders_context_and_serialises():
    err = KernelError("boom", a=1, b="x")
    assert "a=1" in str(err)
    assert err.to_dict()["error"] == "KernelError"
    assert err.to_dict()["context"] == {"a": 1, "b": "x"}


def test_kernel_error_without_context():
    assert str(KernelError("plain")) == "plain"


def test_governance_rejection_carries_reasons():
    err = GovernanceRejection("denied", reasons=["r1", "r2"])
    assert err.reasons == ["r1", "r2"]
    assert err.to_dict()["context"]["reasons"] == ["r1", "r2"]
