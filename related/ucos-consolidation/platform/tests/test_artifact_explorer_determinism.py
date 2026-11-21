"""EC2-EPIC-009 — artifact-explorer determinism validation tests (P5).

Asserts the determinism/reproducibility acceptance criterion: content-addressed view ids
are stable, projections are reproducible in-process, and — the decisive check — the
ExplorerEvidence fingerprint is byte-identical across **independent processes** (no
wall-clock in identities or ordering; caller-supplied logical ticks).
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from platform.artifact_explorer.references import ArtifactView
from platform.blueprints.contracts import BlueprintFamily
from platform.generation.registry import GenerationRequestRegistry

_SCRIPT = """
from platform.foundation.bootstrap import bootstrap_platform
from platform.foundation.identity import Principal, Role
from platform.identity.service import bootstrap_identity
from platform.generation.bootstrap import bootstrap_generation_requests
from platform.generation.provenance import RequestProvenance
from platform.artifact_explorer.bootstrap import bootstrap_artifact_explorer
from platform.blueprints.contracts import BlueprintFamily

ctx = bootstrap_platform()
auth = bootstrap_identity(ctx)
generation = bootstrap_generation_requests(ctx, authorization=auth)
explorer = bootstrap_artifact_explorer(ctx, authorization=auth, generation=generation)
arch = Principal.create("arch@x", [Role.ARCHITECT], tenant="acme")
sess = auth.establish_session(arch, issued_at=0, ttl=1000)
ws = generation.workspaces.create("team", "Team", arch.subject, tenant="acme")
req = generation.submit_request(
    sess.session_id, "req-1", "UCOS-BLPR-1", ws.workspace_id, BlueprintFamily.DATA, now=1
)
generation.start_validation(sess.session_id, req.request_id, now=2)
generation.approve(sess.session_id, req.request_id, now=3)
generation.enqueue(sess.session_id, req.request_id, now=4)
generation.dispatch_request(sess.session_id, req.request_id, now=5, content_hash="c0ffee")
generation.record_provenance(
    sess.session_id, req.request_id,
    RequestProvenance.create(
        request_ref=req.request_id, blueprint_ref="UCOS-BLPR-1", family=BlueprintFamily.DATA,
        generation_reference="GEN-DATA-001", generation_artifact_id="BP-DATA-0001",
        blueprint_provenance_ref="UCOS-BPRV-xyz", implementation_target="platform/generation",
        content_hash="c0ffee", dependency_chain=("EPIC-006",),
    ), now=6,
)
explorer.get_artifact(sess.session_id, req.request_id, now=7)
explorer.lineage(sess.session_id, req.request_id, now=8)
explorer.trace(sess.session_id, req.request_id, now=9)
print("FP=" + explorer.evidence().fingerprint())
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


def test_content_addressed_view_ids_are_stable():
    reg = GenerationRequestRegistry()
    a = reg.create(
        "artifact", "UCOS-BLPR-1", "UCOS-WSPC-1", "dev@x", BlueprintFamily.DATA, submitted_tick=1
    )
    va = ArtifactView.from_request(a)
    reg2 = GenerationRequestRegistry()
    b = reg2.create(
        "artifact", "UCOS-BLPR-1", "UCOS-WSPC-1", "dev@x", BlueprintFamily.DATA, submitted_tick=1
    )
    vb = ArtifactView.from_request(b)
    assert va.view_id == vb.view_id
    assert va.reference.reference_id == vb.reference.reference_id


def test_evidence_fingerprint_is_reproducible_across_processes():
    first = _fingerprint_in_subprocess()
    second = _fingerprint_in_subprocess()
    assert first == second
