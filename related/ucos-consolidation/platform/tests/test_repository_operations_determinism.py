"""EPIC-PLAT-003 — Repository Operations determinism tests (Terminal T5, IMP-007 §5).

Proves the report and dashboard are pure functions of the configuration and the ordered
stage outcomes: identical inputs yield byte-identical content-addressed identities, with
no wall-clock or ambient state leaking into any fingerprint.
"""

from __future__ import annotations

from platform.repository_operations.config import parse_config
from platform.repository_operations.service import build_repository_operations_service
from platform.tests.repository_operations_helpers import acceptance_stage, constant_runner


def _config():
    return parse_config(
        {
            "repository_id": "R",
            "epic_id": "E",
            "stages": [
                {"stage_id": "verify", "kind": "command", "params": {"command": "verify"}},
                {"stage_id": "freeze", "kind": "freeze", "params": {"paths": ["engine/a.py"]}},
                acceptance_stage(),
            ],
        }
    )


def _report(tmp_path):
    service = build_repository_operations_service(
        _config(), repo_root=tmp_path, command_runner=constant_runner(0)
    )
    return service.verify_repository()


def test_report_hash_is_reproducible(tmp_path):
    first = _report(tmp_path)
    second = _report(tmp_path)
    assert first.report_sha256 == second.report_sha256
    assert first.to_dict() == second.to_dict()


def test_dashboard_hash_is_reproducible(tmp_path):
    first = _report(tmp_path).dashboard()
    second = _report(tmp_path).dashboard()
    assert first.dashboard_sha256 == second.dashboard_sha256


def test_config_digest_is_stable():
    assert _config().digest() == _config().digest()
