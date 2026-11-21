"""EC2-EPIC-007 — generation-request determinism validation tests (P5).

Asserts the determinism/reproducibility acceptance criterion: content-addressed ids are
stable, derived status and evidence fingerprints are reproducible in-process, and — the
decisive check — the RequestEvidence fingerprint is byte-identical across **independent
processes** (no wall-clock in identities or ordering; caller-supplied logical ticks).
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from platform.blueprints.contracts import BlueprintFamily
from platform.foundation.bootstrap import bootstrap_platform
from platform.foundation.identity import Principal, Role
from platform.generation.bootstrap import bootstrap_generation_requests
from platform.generation.contracts import GenerationRequest
from platform.generation.dispatch import DispatchRecord
from platform.identity.service import bootstrap_identity

_SCRIPT = """
from platform.foundation.bootstrap import bootstrap_platform
from platform.foundation.identity import Principal, Role
from platform.identity.service import bootstrap_identity
from platform.generation.bootstrap import bootstrap_generation_requests
from platform.blueprints.contracts import BlueprintFamily

ctx = bootstrap_platform()
auth = bootstrap_identity(ctx)
svc = bootstrap_generation_requests(ctx, authorization=auth)
arch = Principal.create("arch@x", [Role.ARCHITECT], tenant="acme")
sess = auth.establish_session(arch, issued_at=0, ttl=1000)
ws = svc.workspaces.create("team", "Team", arch.subject, tenant="acme")
req = svc.submit_request(
    sess.session_id, "req-1", "UCOS-BLPR-1", ws.workspace_id, BlueprintFamily.DATA, now=1
)
svc.start_validation(sess.session_id, req.request_id, now=2)
svc.approve(sess.session_id, req.request_id, now=3)
svc.enqueue(sess.session_id, req.request_id, now=4)
svc.dispatch_request(sess.session_id, req.request_id, now=5, content_hash="c0ffee")
svc.mark_running(sess.session_id, req.request_id, now=6)
svc.complete(sess.session_id, req.request_id, now=7)
print("FP=" + svc.evidence().fingerprint())
"""


def _fingerprint_in_subprocess() -> str:
    child_env = {
        k: v
        for k, v in os.environ.items()
        if not k.startswith("COV_CORE") and k != "COVERAGE_PROCESS_START"
    }
    repo_root = Path(__file__).resolve().parents[2]
    result = subprocess.run(  # noqa: S603 - constant script, trusted interpreter (sys.executable)
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
    a = GenerationRequest.create(
        "req", "UCOS-BLPR-1", "UCOS-WSPC-1", "dev@x", BlueprintFamily.DATA, submitted_tick=1
    )
    b = GenerationRequest.create(
        "req", "UCOS-BLPR-1", "UCOS-WSPC-1", "dev@x", BlueprintFamily.DATA, submitted_tick=1
    )
    assert a.request_id == b.request_id
    d1 = DispatchRecord.create(
        request_ref=a.request_id,
        blueprint_ref="UCOS-BLPR-1",
        family=BlueprintFamily.DATA,
        content_hash="h",
        tick=5,
    )
    d2 = DispatchRecord.create(
        request_ref=b.request_id,
        blueprint_ref="UCOS-BLPR-1",
        family=BlueprintFamily.DATA,
        content_hash="h",
        tick=5,
    )
    assert d1.dispatch_id == d2.dispatch_id


def _in_process_fingerprint() -> str:
    ctx = bootstrap_platform()
    auth = bootstrap_identity(ctx)
    svc = bootstrap_generation_requests(ctx, authorization=auth)
    arch = Principal.create("arch@x", [Role.ARCHITECT], tenant="acme")
    sess = auth.establish_session(arch, issued_at=0, ttl=1000)
    ws = svc.workspaces.create("team", "Team", arch.subject, tenant="acme")
    req = svc.submit_request(
        sess.session_id, "req-1", "UCOS-BLPR-1", ws.workspace_id, BlueprintFamily.DATA, now=1
    )
    svc.start_validation(sess.session_id, req.request_id, now=2)
    svc.approve(sess.session_id, req.request_id, now=3)
    svc.enqueue(sess.session_id, req.request_id, now=4)
    svc.dispatch_request(sess.session_id, req.request_id, now=5, content_hash="c0ffee")
    svc.mark_running(sess.session_id, req.request_id, now=6)
    svc.complete(sess.session_id, req.request_id, now=7)
    return svc.evidence().fingerprint()


def test_evidence_fingerprint_is_reproducible_in_process():
    assert _in_process_fingerprint() == _in_process_fingerprint()


def test_evidence_fingerprint_is_reproducible_across_processes():
    first = _fingerprint_in_subprocess()
    second = _fingerprint_in_subprocess()
    assert first == second
    assert first == _in_process_fingerprint()
