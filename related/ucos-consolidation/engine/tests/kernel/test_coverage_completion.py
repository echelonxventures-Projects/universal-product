"""Completion tests — exercise every remaining branch to a genuine 100%.

These cover the defensive integrity paths, the relationship-graph traversal internals,
the generic governance-rejection path, and the compliance failure/offender branches. No
line is waived; each path is driven by a real (if adversarial) input.
"""

from __future__ import annotations

from dataclasses import replace

import pytest

from engine.kernel.compliance import (
    _kernel_has_no_closed_enum,
    _represent_prohibited_by_registration,
    architectural_proof,
)
from engine.kernel.errors import AuditIntegrityError, GovernanceRejection
from engine.kernel.governance import Constraint, Governance
from engine.kernel.kernel import MetaKernel
from engine.kernel.meta import make_metatype, reflective_root
from engine.kernel.registry import UniversalRegistry

# --------------------------------------------------------------------------- registry


def _seeded() -> UniversalRegistry:
    reg = UniversalRegistry()
    reg.register(reflective_root())
    reg.register(make_metatype("T"))
    return reg


def _obj(reg, key, targets=()):
    from engine.kernel.meta import MetaObject

    rels = [{"relation": "dep", "target": t} for t in targets]
    return reg.register(
        MetaObject(metatype="T", namespace="umk.g", natural_key=key, relationships=rels)
    )


def test_would_cycle_direct_self_target():
    reg = _seeded()
    assert reg.would_cycle("SELF", ("SELF",)) is True


def test_would_cycle_walk_detects_cycle_and_backedge():
    reg = _seeded()
    a = _obj(reg, "a")
    b = _obj(reg, "b", targets=[a.identity])
    c = _obj(reg, "c", targets=[a.identity, b.identity])
    # Walk b -> a reaches the target identity (cycle path).
    assert reg.would_cycle(a.identity, (b.identity,)) is True
    # A target not in the graph exercises the already-seen back-edge and the final False.
    assert reg.would_cycle("UMK-X-000000000000", (b.identity, c.identity)) is False


def test_would_cycle_walks_into_unregistered_target():
    # A relationship may point at a not-yet-registered identity; walking into it exercises
    # the branch where the target has no registered chain (head is falsy).
    reg = _seeded()
    b = _obj(reg, "b", targets=["UMK-GHOST-000000000000"])
    assert reg.would_cycle("UMK-OTHER-000000000000", (b.identity,)) is False


def test_generic_governance_rejection_path():
    gov = Governance()
    gov.register_constraint(Constraint("nope", lambda _c, _v: (False, "policy says no")))
    reg = UniversalRegistry(governance=gov)
    with pytest.raises(GovernanceRejection) as excinfo:
        reg.register(reflective_root())
    assert "policy says no" in excinfo.value.reasons


def test_verify_detects_sequence_gap():
    reg = _seeded()
    reg._journal[0] = replace(reg._journal[0], sequence=99)
    with pytest.raises(AuditIntegrityError):
        reg.verify()


def test_verify_detects_broken_chain():
    reg = _seeded()
    reg._journal[0] = replace(reg._journal[0], previous_hash="deadbeef")
    with pytest.raises(AuditIntegrityError):
        reg.verify()


def test_verify_detects_entry_hash_mismatch():
    reg = _seeded()
    reg._journal[0] = replace(reg._journal[0], entry_hash="0" * 64)
    with pytest.raises(AuditIntegrityError):
        reg.verify()


# --------------------------------------------------------------------------- compliance


def test_enum_detector_flags_a_control_sample(tmp_path):
    sample = tmp_path / "closed.py"
    sample.write_text("from enum import Enum\n\nclass Kind(Enum):\n    A = 1\n", encoding="utf-8")
    ok, offenders = _kernel_has_no_closed_enum(tmp_path)
    assert ok is False
    assert any("closed.py:Kind" in o for o in offenders)


def test_architectural_proof_records_failure(monkeypatch):
    # register_object raising simulates a category that could not be represented; the proof
    # must record ok=False and fail overall (the failure-evidence path).
    def boom(self, **kwargs):
        raise RuntimeError("cannot represent")

    monkeypatch.setattr(MetaKernel, "register_object", boom)
    proof = architectural_proof()
    assert proof["passed"] is False
    assert all(r["ok"] is False for r in proof["records"])
    assert any("cannot represent" in r.get("error", "") for r in proof["records"])


def test_represent_prohibited_records_failure(monkeypatch):
    real = MetaKernel.register_metatype

    def selective(self, natural_key, **kwargs):
        if natural_key.startswith("Concrete-"):
            raise RuntimeError("blocked")
        return real(self, natural_key, **kwargs)

    monkeypatch.setattr(MetaKernel, "register_metatype", selective)
    result = _represent_prohibited_by_registration()
    assert result["passed"] is False
