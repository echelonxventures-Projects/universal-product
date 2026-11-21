"""EC2-EPIC-006 — blueprint determinism validation tests (P5/P18).

Asserts the determinism/reproducibility acceptance criterion: content-addressed ids are
stable, and the BlueprintEvidence fingerprint is reproducible in-process and — the
decisive check — byte-identical across **independent processes** (no wall-clock in
identities or ordering; caller-supplied logical ticks).
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from platform.blueprints.contracts import Blueprint, BlueprintFamily
from platform.blueprints.provenance import BlueprintProvenance
from platform.foundation.bootstrap import bootstrap_platform
from platform.foundation.identity import Principal, Role
from platform.identity.service import bootstrap_identity

_SCRIPT = """
from platform.foundation.bootstrap import bootstrap_platform
from platform.foundation.identity import Principal, Role
from platform.identity.service import bootstrap_identity
from platform.blueprints.bootstrap import bootstrap_blueprints
from platform.blueprints.contracts import BlueprintFamily
from platform.blueprints.provenance import BlueprintProvenance

ctx = bootstrap_platform()
auth = bootstrap_identity(ctx)
svc = bootstrap_blueprints(ctx, authorization=auth)
arch = Principal.create("arch@x", [Role.ARCHITECT])
sess = auth.establish_session(arch, issued_at=0, ttl=1000)
ws = svc.workspaces.create("team", "Team", arch.subject, tenant="acme")
bp = svc.author_blueprint(
    sess.session_id, "bp-1", "BP", ws.workspace_id, BlueprintFamily.DATA, now=1
)
svc.classify(sess.session_id, bp.blueprint_id, BlueprintFamily.DATA, now=2)
svc.validate(sess.session_id, bp.blueprint_id, now=3)
prov = BlueprintProvenance.create(
    blueprint_ref=bp.blueprint_id, family=BlueprintFamily.DATA,
    generation_reference="GEN-DATA-001", generation_artifact_id="BP-DATA-0001",
    generation_source="05-GENERATION/GEN-DATA-001", implementation_target="platform/blueprints",
    content_hash="deadbeef")
svc.catalog_blueprint(sess.session_id, bp.blueprint_id, prov, now=4)
svc.version(sess.session_id, bp.blueprint_id, "h1", now=5)
print("FP=" + svc.evidence().fingerprint())
"""


def _fingerprint_in_subprocess() -> str:
    child_env = {
        k: v
        for k, v in os.environ.items()
        if not k.startswith("COV_CORE") and k != "COVERAGE_PROCESS_START"
    }
    repo_root = Path(__file__).resolve().parents[2]
    result = subprocess.run(  # noqa: S603 - constant script, trusted interpreter
        [sys.executable, "-c", _SCRIPT],
        capture_output=True,
        text=True,
        check=True,
        cwd=str(repo_root),
        env=child_env,
    )
    for line in result.stdout.splitlines():
        if line.startswith("FP="):
            return line[3:]
    raise AssertionError(f"no fingerprint marker in subprocess output: {result.stdout}")


def test_content_addressed_ids_are_stable():
    a = Blueprint.create("bp", "BP", "UCOS-WSPC-1", "arch@x", BlueprintFamily.DATA)
    b = Blueprint.create("bp", "BP", "UCOS-WSPC-1", "arch@x", BlueprintFamily.DATA)
    assert a.blueprint_id == b.blueprint_id
    p1 = BlueprintProvenance.create(
        blueprint_ref=a.blueprint_id,
        family=BlueprintFamily.DATA,
        generation_reference="GEN-DATA-001",
        generation_artifact_id="BP-DATA-0001",
        generation_source="05-GENERATION/GEN-DATA-001",
        implementation_target="platform/blueprints",
        content_hash="h",
    )
    p2 = BlueprintProvenance.create(
        blueprint_ref=b.blueprint_id,
        family=BlueprintFamily.DATA,
        generation_reference="GEN-DATA-001",
        generation_artifact_id="BP-DATA-0001",
        generation_source="05-GENERATION/GEN-DATA-001",
        implementation_target="platform/blueprints",
        content_hash="h",
    )
    assert p1.provenance_id == p2.provenance_id


def _in_process_fingerprint() -> str:
    ctx = bootstrap_platform()
    auth = bootstrap_identity(ctx)
    from platform.blueprints.bootstrap import bootstrap_blueprints

    svc = bootstrap_blueprints(ctx, authorization=auth)
    arch = Principal.create("arch@x", [Role.ARCHITECT])
    sess = auth.establish_session(arch, issued_at=0, ttl=1000)
    ws = svc.workspaces.create("team", "Team", arch.subject, tenant="acme")
    bp = svc.author_blueprint(
        sess.session_id, "bp-1", "BP", ws.workspace_id, BlueprintFamily.DATA, now=1
    )
    svc.classify(sess.session_id, bp.blueprint_id, BlueprintFamily.DATA, now=2)
    svc.validate(sess.session_id, bp.blueprint_id, now=3)
    prov = BlueprintProvenance.create(
        blueprint_ref=bp.blueprint_id,
        family=BlueprintFamily.DATA,
        generation_reference="GEN-DATA-001",
        generation_artifact_id="BP-DATA-0001",
        generation_source="05-GENERATION/GEN-DATA-001",
        implementation_target="platform/blueprints",
        content_hash="deadbeef",
    )
    svc.catalog_blueprint(sess.session_id, bp.blueprint_id, prov, now=4)
    svc.version(sess.session_id, bp.blueprint_id, "h1", now=5)
    return svc.evidence().fingerprint()


def test_evidence_fingerprint_is_reproducible_in_process():
    assert _in_process_fingerprint() == _in_process_fingerprint()


def test_evidence_fingerprint_is_reproducible_across_processes():
    first = _fingerprint_in_subprocess()
    second = _fingerprint_in_subprocess()
    assert first == second
    assert first == _in_process_fingerprint()
