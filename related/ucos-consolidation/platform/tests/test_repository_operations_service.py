"""EPIC-PLAT-003 — Repository Operations service tests (Terminal T5)."""

from __future__ import annotations

from platform.repository_operations.config import parse_config
from platform.repository_operations.contracts import OperationsVerdict, RepositoryDashboard
from platform.repository_operations.service import (
    RepositoryOperationsService,
    build_repository_operations_service,
)
from platform.tests.repository_operations_helpers import acceptance_stage, constant_runner


def _config():
    return parse_config(
        {
            "repository_id": "R",
            "epic_id": "E",
            "stages": [
                {"stage_id": "freeze", "kind": "freeze", "params": {"paths": ["engine/a.py"]}},
                acceptance_stage(),
            ],
        }
    )


def test_build_service_with_injected_runner_and_verify(tmp_path):
    service = build_repository_operations_service(
        _config(), repo_root=tmp_path, command_runner=constant_runner(0)
    )
    assert isinstance(service, RepositoryOperationsService)
    assert service.config.repository_id == "R"
    report = service.verify_repository()
    assert report.verdict is OperationsVerdict.PASS


def test_service_dashboard(tmp_path):
    service = build_repository_operations_service(
        _config(), repo_root=tmp_path, command_runner=constant_runner(0)
    )
    dash = service.dashboard()
    assert isinstance(dash, RepositoryDashboard)
    assert dash.verdict is OperationsVerdict.PASS


def test_build_service_with_default_runner_and_checkpoint(tmp_path):
    # No command stage → the default subprocess runner is composed but never invoked.
    service = build_repository_operations_service(
        _config(), repo_root=tmp_path, checkpoint_path=tmp_path / "cp.json"
    )
    assert service.orchestrator.checkpoint_store is not None
    report = service.verify_repository()
    assert report.passed
    assert (tmp_path / "cp.json").is_file()
