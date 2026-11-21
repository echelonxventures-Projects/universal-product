"""EC2-EPIC-008 — execution-dashboard determinism validation tests (P5).

Asserts the determinism/reproducibility acceptance criterion: content-addressed view ids
are stable, and — the decisive check — the DashboardEvidence fingerprint is byte-identical
across **independent processes** (no wall-clock in identities or ordering; the dashboard is
a pure projection of caller-supplied, logically-ticked generation state).
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from platform.blueprints.contracts import BlueprintFamily
from platform.execution_dashboard.bootstrap import bootstrap_execution_dashboard
from platform.execution_dashboard.views import ExecutionSnapshot
from platform.foundation.bootstrap import bootstrap_platform
from platform.foundation.identity import Principal, Role
from platform.generation.bootstrap import bootstrap_generation_requests
from platform.generation.registry import GenerationRequestRegistry
from platform.generation.status import derive_status
from platform.identity.service import bootstrap_identity

_SCRIPT = """
from platform.foundation.bootstrap import bootstrap_platform
from platform.foundation.identity import Principal, Role
from platform.identity.service import bootstrap_identity
from platform.generation.bootstrap import bootstrap_generation_requests
from platform.execution_dashboard.bootstrap import bootstrap_execution_dashboard
from platform.blueprints.contracts import BlueprintFamily

ctx = bootstrap_platform()
auth = bootstrap_identity(ctx)
gen = bootstrap_generation_requests(ctx, authorization=auth)
dash = bootstrap_execution_dashboard(ctx, authorization=auth, generation=gen)
arch = Principal.create("arch@x", [Role.ARCHITECT], tenant="acme")
sess = auth.establish_session(arch, issued_at=0, ttl=1000)
ws = gen.workspaces.create("team", "Team", arch.subject, tenant="acme")
req = gen.submit_request(
    sess.session_id, "req-1", "UCOS-BLPR-1", ws.workspace_id, BlueprintFamily.DATA, now=1
)
gen.start_validation(sess.session_id, req.request_id, now=2)
gen.approve(sess.session_id, req.request_id, now=3)
gen.enqueue(sess.session_id, req.request_id, now=4)
dash.view(sess.session_id, now=5, tenant="acme")
print("FP=" + dash.evidence().fingerprint())
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


def test_content_addressed_snapshot_ids_are_stable():
    reg = GenerationRequestRegistry()
    a = reg.create(
        "req", "UCOS-BLPR-1", "UCOS-WSPC-1", "dev@x", BlueprintFamily.DATA, submitted_tick=1
    )
    snap_a = ExecutionSnapshot.from_request(
        a, derive_status(a, has_dispatch=False, has_provenance=False)
    )
    reg2 = GenerationRequestRegistry()
    b = reg2.create(
        "req", "UCOS-BLPR-1", "UCOS-WSPC-1", "dev@x", BlueprintFamily.DATA, submitted_tick=1
    )
    snap_b = ExecutionSnapshot.from_request(
        b, derive_status(b, has_dispatch=False, has_provenance=False)
    )
    assert snap_a.snapshot_id == snap_b.snapshot_id


def _in_process_fingerprint() -> str:
    ctx = bootstrap_platform()
    auth = bootstrap_identity(ctx)
    gen = bootstrap_generation_requests(ctx, authorization=auth)
    dash = bootstrap_execution_dashboard(ctx, authorization=auth, generation=gen)
    arch = Principal.create("arch@x", [Role.ARCHITECT], tenant="acme")
    sess = auth.establish_session(arch, issued_at=0, ttl=1000)
    ws = gen.workspaces.create("team", "Team", arch.subject, tenant="acme")
    req = gen.submit_request(
        sess.session_id, "req-1", "UCOS-BLPR-1", ws.workspace_id, BlueprintFamily.DATA, now=1
    )
    gen.start_validation(sess.session_id, req.request_id, now=2)
    gen.approve(sess.session_id, req.request_id, now=3)
    gen.enqueue(sess.session_id, req.request_id, now=4)
    dash.view(sess.session_id, now=5, tenant="acme")
    return dash.evidence().fingerprint()


def test_evidence_fingerprint_is_reproducible_in_process():
    assert _in_process_fingerprint() == _in_process_fingerprint()


def test_evidence_fingerprint_is_reproducible_across_processes():
    first = _fingerprint_in_subprocess()
    second = _fingerprint_in_subprocess()
    assert first == second
    assert first == _in_process_fingerprint()
