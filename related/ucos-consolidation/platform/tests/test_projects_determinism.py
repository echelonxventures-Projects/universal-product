"""EC2-EPIC-005 — project determinism validation tests (P5).

Asserts the determinism/reproducibility acceptance criterion: content-addressed ids are
stable, derived status and evidence fingerprints are reproducible in-process, and — the
decisive check — the ProjectEvidence fingerprint is byte-identical across **independent
processes** (no wall-clock in identities or ordering; caller-supplied logical ticks).
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from platform.foundation.bootstrap import bootstrap_platform
from platform.foundation.identity import Principal, Role
from platform.identity.service import bootstrap_identity
from platform.projects.bootstrap import bootstrap_projects
from platform.projects.contracts import AssociationKind, Project, ProjectAssociation, ProjectStatus

# A self-contained script that builds an identical runtime state and prints the
# ProjectEvidence fingerprint on a parseable marker line. Run in a fresh interpreter.
_SCRIPT = """
from platform.foundation.bootstrap import bootstrap_platform
from platform.foundation.identity import Principal, Role
from platform.identity.service import bootstrap_identity
from platform.projects.bootstrap import bootstrap_projects
from platform.projects.contracts import AssociationKind, ProjectStatus

ctx = bootstrap_platform()
auth = bootstrap_identity(ctx)
svc = bootstrap_projects(ctx, authorization=auth)
admin = Principal.create("admin@x", [Role.PLATFORM_ADMINISTRATOR])
sess = auth.establish_session(admin, issued_at=0, ttl=1000)
ws = svc.workspaces.create("team", "Team", admin.subject, tenant="acme")
proj = svc.create_project(sess.session_id, "alpha", "Alpha", ws.workspace_id, now=1)
svc.add_association(sess.session_id, proj.project_id, AssociationKind.BLUEPRINT, "BP-1", now=2)
svc.add_association(sess.session_id, proj.project_id, AssociationKind.REQUEST, "REQ-1", now=3)
svc.transition(sess.session_id, proj.project_id, ProjectStatus.COMPLETED, now=4)
print("FP=" + svc.evidence().fingerprint())
"""


def _fingerprint_in_subprocess() -> str:
    # Run in a fresh interpreter to prove cross-process reproducibility. Strip the
    # pytest-cov subprocess hooks from the child env: coverage's own startup imports
    # the stdlib ``platform`` module, which the editable install's finder would hijack
    # to this repo's ``platform`` package — an environmental collision unrelated to
    # determinism. Disabling child coverage keeps the check hermetic.
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
    a = Project.create("alpha", "Alpha", "UCOS-WSPC-1", "dev@x")
    b = Project.create("alpha", "Alpha", "UCOS-WSPC-1", "dev@x")
    assert a.project_id == b.project_id
    assoc_a = ProjectAssociation.create(a.project_id, AssociationKind.BLUEPRINT, "BP-1")
    assoc_b = ProjectAssociation.create(b.project_id, AssociationKind.BLUEPRINT, "BP-1")
    assert assoc_a.association_id == assoc_b.association_id


def _in_process_fingerprint() -> str:
    ctx = bootstrap_platform()
    auth = bootstrap_identity(ctx)
    svc = bootstrap_projects(ctx, authorization=auth)
    admin = Principal.create("admin@x", [Role.PLATFORM_ADMINISTRATOR])
    sess = auth.establish_session(admin, issued_at=0, ttl=1000)
    ws = svc.workspaces.create("team", "Team", admin.subject, tenant="acme")
    proj = svc.create_project(sess.session_id, "alpha", "Alpha", ws.workspace_id, now=1)
    svc.add_association(sess.session_id, proj.project_id, AssociationKind.BLUEPRINT, "BP-1", now=2)
    svc.add_association(sess.session_id, proj.project_id, AssociationKind.REQUEST, "REQ-1", now=3)
    svc.transition(sess.session_id, proj.project_id, ProjectStatus.COMPLETED, now=4)
    return svc.evidence().fingerprint()


def test_evidence_fingerprint_is_reproducible_in_process():
    assert _in_process_fingerprint() == _in_process_fingerprint()


def test_evidence_fingerprint_is_reproducible_across_processes():
    first = _fingerprint_in_subprocess()
    second = _fingerprint_in_subprocess()
    assert first == second
    # And it matches the in-process computation of the identical state (P5).
    assert first == _in_process_fingerprint()
