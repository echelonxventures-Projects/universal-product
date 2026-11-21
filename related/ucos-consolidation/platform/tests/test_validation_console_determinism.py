"""EC2-EPIC-010 — validation console determinism & fidelity tests (P5 / P6).

Asserts the determinism/reproducibility and fidelity acceptance criteria: content-
addressed ids are stable, the console evidence fingerprint is reproducible in-process and
— the decisive check — byte-identical across **independent processes**; and the surfaced
report/evidence/decision are byte-for-byte the certified ``engine.validation`` output
(fidelity, P6), verifiable via the machine-checkable fidelity predicate.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from platform.foundation.contracts import content_hash
from platform.tests.validation_console_helpers import accepted_subject

from engine.validation.evidence import build_validation_evidence
from engine.validation.executor import ValidationEngine
from engine.validation.gates import enforce_acceptance

_SCRIPT = """
from platform.foundation.bootstrap import bootstrap_platform
from platform.foundation.identity import Principal, Role
from platform.identity.service import bootstrap_identity
from platform.validation.bootstrap import bootstrap_validation_console
from platform.validation.contracts import ValidationSubject
from engine.runtime.disclosure import build_disclosure

pkg = "a" * 64
subject = ValidationSubject(
    target_id="UCOS-RUN-data-0123456789abcdef",
    blueprint_id="UCOS-BLPR-1",
    provenance_chain=("UCOS-BLPR-1", "UCOS-RUN-data-0123456789abcdef"),
    signature={"algorithm": "ed25519", "value": "sig", "payload_sha256": pkg},
    sbom={"sbom_format": "cyclonedx", "components": [{"name": "x"}]},
    dependency_closure=({"role": "root", "blueprint_id": "UCOS-BLPR-1", "package_sha256": pkg},),
    disclosure=build_disclosure(),
    package_sha256=pkg,
    image_reference="registry/img@sha256:" + pkg,
    runtime_id="UCOS-RUN-data-0123456789abcdef",
)
ctx = bootstrap_platform()
auth = bootstrap_identity(ctx)
svc = bootstrap_validation_console(ctx, authorization=auth)
arch = Principal.create("arch@x", [Role.ARCHITECT], tenant="acme")
sess = auth.establish_session(arch, issued_at=0, ttl=1000)
svc.surface_validation(sess.session_id, subject, now=1, tenant="acme")
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


def _in_process_fingerprint() -> str:
    from platform.foundation.bootstrap import bootstrap_platform
    from platform.foundation.identity import Principal, Role
    from platform.identity.service import bootstrap_identity
    from platform.validation.bootstrap import bootstrap_validation_console

    ctx = bootstrap_platform()
    auth = bootstrap_identity(ctx)
    svc = bootstrap_validation_console(ctx, authorization=auth)
    arch = Principal.create("arch@x", [Role.ARCHITECT], tenant="acme")
    sess = auth.establish_session(arch, issued_at=0, ttl=1000)
    svc.surface_validation(sess.session_id, accepted_subject(), now=1, tenant="acme")
    return svc.evidence().fingerprint()


def test_fidelity_surfaced_equals_certified_engine_output():
    subject = accepted_subject()
    report = ValidationEngine().validate(subject)
    evidence = build_validation_evidence(report)
    decision = enforce_acceptance(report)

    from platform.validation.facade import ValidationFacade

    surfaced = ValidationFacade().surface(subject)
    assert content_hash(surfaced.report.to_dict()) == content_hash(report.to_dict())
    assert content_hash(surfaced.evidence.to_dict()) == content_hash(evidence.to_dict())
    assert content_hash(surfaced.decision.to_dict()) == content_hash(decision.to_dict())


def test_evidence_fingerprint_is_reproducible_in_process():
    assert _in_process_fingerprint() == _in_process_fingerprint()


def test_evidence_fingerprint_is_reproducible_across_processes():
    first = _fingerprint_in_subprocess()
    second = _fingerprint_in_subprocess()
    assert first == second
    assert first == _in_process_fingerprint()
