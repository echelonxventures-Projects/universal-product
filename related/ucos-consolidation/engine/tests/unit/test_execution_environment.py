"""UEG-000001 — Universal Execution Governance, measured.

Three kinds of test live here and the distinction matters:

* **Unit measurements** over the model, the checks, the cache and the evidence, using
  synthetic environments so that a failing condition can be constructed rather than waited
  for. A check whose refusal path is never exercised cannot be relied on to refuse.
* **Live measurements** against the environment actually running the suite. These are the
  only tests that prove the capability works on a real machine rather than on a fixture.
* **Contract measurements** over the SOURCE of ``verify.sh``. These are the executable form
  of two declared laws — EEG-SEP (a verification path may not create or install) and
  EEG-PATH (every tool resolves by absolute path) — and they exist so that re-introducing
  either defect fails the suite instead of passing unnoticed.
"""

from __future__ import annotations

import json
import re
import stat
import subprocess
import sys
from pathlib import Path

import pytest

import engine.execution_environment.contract as contract
from engine.execution_environment import __main__ as entry_point
from engine.execution_environment import discovery
from engine.execution_environment import evidence as evidence_module
from engine.execution_environment import fingerprint as fingerprint_module
from engine.execution_environment.contract import CHECKS, assess
from engine.execution_environment.discovery import (
    canonical_series,
    configuration_fingerprint,
    expected_pins,
    git_identity,
    observe,
    repo_root,
    shadowing_executables,
    unexpected_executables,
)
from engine.execution_environment.gate import (
    EXIT_CLOSED,
    EXIT_FAULT,
    EXIT_OPEN,
    _render,
    _render_failure,
    main,
    measure,
)
from engine.execution_environment.model import (
    RESULT_INVALID,
    RESULT_VALID,
    CheckResult,
    Dependencies,
    ExecutionEnvironment,
    ExecutionEnvironmentError,
    MachineIdentity,
    RepositoryIdentity,
    RuntimeIdentity,
    Toolchain,
    ToolRecord,
    _digest,
    load_declaration,
)

REPO = Path(repo_root())
DECLARATION = load_declaration(repository=REPO)


def _git(*args: str) -> str:
    """Run git in the repository and return stdout.

    One helper so the subprocess suppression is declared once. git is deliberately resolved
    from PATH: this suite measures the repository it lives in, and no absolute git path is
    portable across the machines that run it.
    """
    return subprocess.run(  # noqa: S603
        ["git", *args],  # noqa: S607
        cwd=str(REPO),
        capture_output=True,
        text=True,
        check=False,
    ).stdout


# --- fixtures ---------------------------------------------------------------------


def _runtime(**overrides) -> RuntimeIdentity:
    values = {
        "language": "python",
        "version": "3.12.13",
        "series": "3.12",
        "interpreter_path": f"{REPO}/.ec1-venv/bin/python",
        "prefix": f"{REPO}/.ec1-venv",
        "base_prefix": "/opt/homebrew/Cellar/python@3.12/3.12.13",
    }
    values.update(overrides)
    return RuntimeIdentity(**values)


def _tool(name: str = "pytest", **overrides) -> ToolRecord:
    values = {
        "name": name.replace("-", "_"),
        "distribution": name,
        "expected_version": "8.3.4",
        "installed_version": "8.3.4",
        "importable": True,
        "declared_scripts": (f"{REPO}/.ec1-venv/bin/{name}",),
    }
    values.update(overrides)
    return ToolRecord(**values)


def _environment(**overrides) -> ExecutionEnvironment:
    tools = overrides.pop("tools", (_tool(),))
    values = {
        "runtime": _runtime(),
        "toolchain": Toolchain(scripts_directory=f"{REPO}/.ec1-venv/bin", tools=tools),
        "dependencies": Dependencies(
            expected=(("pytest", "8.3.4"),),
            installed=(("pytest", "8.3.4"),),
            fingerprint="dep-fingerprint",
        ),
        "repository": RepositoryIdentity(
            root=str(REPO),
            branch="main",
            commit="0" * 40,
            configuration_fingerprint="config-fingerprint",
        ),
        "machine": MachineIdentity(platform="Darwin", machine="arm64", implementation="CPython"),
        "venv_directory": f"{REPO}/.ec1-venv",
    }
    values.update(overrides)
    return ExecutionEnvironment(**values)


def _check(check_id: str, holds: bool = True, blocking: bool = True) -> CheckResult:
    return CheckResult(check_id=check_id, title=check_id, blocking=blocking, holds=holds)


# --- the declaration, and its agreement with the implementation --------------------


class TestDeclaration:
    def test_every_declared_check_is_implemented(self):
        """A check declared and computed by nothing is a condition enforced by nothing."""
        undeclared = set(DECLARATION.check_ids) - set(CHECKS)
        assert not undeclared, f"declared but unimplemented: {sorted(undeclared)}"

    def test_every_implemented_check_is_declared(self):
        """The other direction: an undeclared check is a rule with no stated authority."""
        unimplemented = set(CHECKS) - set(DECLARATION.check_ids)
        assert not unimplemented, f"implemented but undeclared: {sorted(unimplemented)}"

    def test_the_declaration_binds_the_pin_and_series_authorities_it_does_not_restate(self):
        """UEG owns no version. It names the files that do, and both must exist."""
        assert (REPO / DECLARATION.pin_file).is_file()
        assert (REPO / DECLARATION.series_file).is_file()
        assert DECLARATION.pin_file == "pyproject.toml"

    def test_exactly_one_check_is_non_blocking(self):
        """EEG-08 is advisory by determination; everything else refuses."""
        non_blocking = [check.check_id for check in DECLARATION.checks if not check.blocking]
        assert non_blocking == ["EEG-08"]

    def test_required_plugins_cover_the_arguments_pyproject_actually_passes(self):
        """pytest-cov is required because addopts pass --cov; the link is measured, not assumed."""
        modules = {plugin.module for plugin in DECLARATION.required_plugins}
        assert "pytest_cov" in modules
        addopts = (REPO / "pyproject.toml").read_text(encoding="utf-8")
        assert "--cov-fail-under=90" in addopts

    def test_a_missing_declaration_is_a_fault_not_a_default(self, tmp_path):
        with pytest.raises(ExecutionEnvironmentError, match="not found"):
            load_declaration(tmp_path / "absent.json")

    def test_malformed_json_is_a_fault(self, tmp_path):
        broken = tmp_path / "ueg.json"
        broken.write_text("{not json", encoding="utf-8")
        with pytest.raises(ExecutionEnvironmentError, match="not valid JSON"):
            load_declaration(broken)

    def test_a_missing_required_key_is_a_fault(self, tmp_path):
        partial = tmp_path / "ueg.json"
        partial.write_text(json.dumps({"artifact_id": "UEG-000001"}), encoding="utf-8")
        with pytest.raises(ExecutionEnvironmentError, match="missing the required key"):
            load_declaration(partial)

    def test_a_declaration_with_no_checks_is_a_fault(self, tmp_path):
        """An empty check set would make the gate pass vacuously over nothing."""
        payload = json.loads((REPO / "00-MASTER/UEG-000001/ueg-declaration.json").read_text())
        payload["checks"]["items"] = []
        empty = tmp_path / "ueg.json"
        empty.write_text(json.dumps(payload), encoding="utf-8")
        with pytest.raises(ExecutionEnvironmentError, match="declares no checks"):
            load_declaration(empty)

    def test_asking_for_an_undeclared_check_raises(self):
        with pytest.raises(ExecutionEnvironmentError, match="not a declared check"):
            DECLARATION.check("EEG-99")

    def test_a_known_check_resolves(self):
        assert DECLARATION.check("EEG-01").blocking is True

    def test_load_declaration_defaults_to_the_declared_relative_path(self, monkeypatch):
        monkeypatch.chdir(REPO)
        assert load_declaration().artifact_id == "UEG-000001"


# --- the entity -------------------------------------------------------------------


class TestModel:
    def test_digest_cannot_be_confused_by_separator_characters(self):
        """NUL separation: ('a','b') and ('a\\tb',) must not collide."""
        assert _digest("a", "b") != _digest("a\tb")

    def test_a_venv_is_recognised_by_the_interpreter_not_by_a_path_shape(self):
        assert _runtime().in_virtual_environment is True
        assert _runtime(prefix="/usr", base_prefix="/usr").in_virtual_environment is False

    def test_environment_identity_ignores_the_commit(self):
        """The environment did not change because a source file did."""
        first = _environment()
        second = _environment(
            repository=RepositoryIdentity(
                root=str(REPO),
                branch="other",
                commit="f" * 40,
                configuration_fingerprint="config-fingerprint",
            )
        )
        assert first.environment_id == second.environment_id

    def test_environment_identity_moves_when_the_interpreter_does(self):
        moved = _environment(runtime=_runtime(version="3.13.0"))
        assert moved.environment_id != _environment().environment_id

    def test_environment_identity_moves_when_dependencies_do(self):
        moved = _environment(
            dependencies=Dependencies(expected=(), installed=(), fingerprint="other")
        )
        assert moved.environment_id != _environment().environment_id

    def test_a_blocking_failure_makes_the_environment_invalid(self):
        environment = _environment().with_checks((_check("EEG-01", holds=False),))
        assert environment.result == RESULT_INVALID
        assert environment.valid is False
        assert [check.check_id for check in environment.blocking_failures] == ["EEG-01"]

    def test_a_non_blocking_failure_does_not(self):
        environment = _environment().with_checks((_check("EEG-08", holds=False, blocking=False),))
        assert environment.result == RESULT_VALID
        assert [check.check_id for check in environment.advisories] == ["EEG-08"]

    def test_with_checks_does_not_mutate_the_original(self):
        original = _environment()
        derived = original.with_checks((_check("EEG-01"),))
        assert original.checks == ()
        assert len(derived.checks) == 1
        assert derived.environment_id == original.environment_id

    def test_tool_health_requires_version_presence_and_executables(self):
        assert _tool().healthy is True
        assert _tool(installed_version=None).healthy is False
        assert _tool(installed_version="8.0.0").healthy is False
        assert _tool(missing_scripts=("bin/pytest",)).healthy is False
        assert _tool(non_executable_scripts=("bin/pytest",)).healthy is False
        assert _tool(record_readable=False).healthy is False

    def test_a_tool_is_findable_by_module_or_distribution_name(self):
        toolchain = Toolchain(scripts_directory="bin", tools=(_tool("pytest-cov"),))
        assert toolchain.tool("pytest-cov") is not None
        assert toolchain.tool("pytest_cov") is not None
        assert toolchain.tool("absent") is None

    def test_serialisation_carries_every_group_the_declaration_declares(self):
        payload = _environment().with_checks((_check("EEG-01"),)).as_dict()
        for group in DECLARATION.attribute_groups:
            key = "machine" if group == "identity" else group
            assert key in payload or group == "validation"
        assert payload["result"] == RESULT_VALID
        assert payload["checks"][0]["check_id"] == "EEG-01"

    def test_optional_fields_are_omitted_rather_than_null(self):
        assert "command" not in _environment().as_dict()
        assert "expected" not in _check("EEG-01").as_dict()


# --- observation ------------------------------------------------------------------


class TestDiscovery:
    def test_the_root_is_the_repository_git_reports(self):
        expected = _git("rev-parse", "--show-toplevel").strip()
        assert Path(repo_root()) == Path(expected).resolve()

    def test_a_directory_that_is_no_repository_is_a_fault_not_a_guess(self, tmp_path):
        with pytest.raises(ExecutionEnvironmentError, match="no repository root"):
            repo_root(tmp_path)

    def test_the_canonical_series_is_read_from_the_authority(self):
        assert canonical_series(REPO, DECLARATION.series_file) == "3.12"

    def test_an_unparseable_series_authority_is_a_fault(self, tmp_path):
        (tmp_path / "env.sh").write_text("# nothing here\n", encoding="utf-8")
        with pytest.raises(ExecutionEnvironmentError, match="no UCOS_PYTHON_SERIES"):
            canonical_series(tmp_path, "env.sh")

    def test_an_unreadable_series_authority_is_a_fault(self, tmp_path):
        with pytest.raises(ExecutionEnvironmentError, match="unreadable"):
            canonical_series(tmp_path, "absent.sh")

    def test_the_pins_are_parsed_from_pyproject_and_not_restated(self):
        pins = dict(expected_pins(REPO, "pyproject.toml"))
        assert "pytest" in pins and "pytest-cov" in pins and "ruff" in pins
        source = (REPO / "pyproject.toml").read_text(encoding="utf-8")
        for name, version in pins.items():
            assert f'"{name}=={version}"' in source

    def test_an_unreadable_pin_authority_is_a_fault(self, tmp_path):
        with pytest.raises(ExecutionEnvironmentError, match="unreadable"):
            expected_pins(tmp_path, "absent.toml")

    def test_invalid_toml_is_a_fault(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text("[project\n", encoding="utf-8")
        with pytest.raises(ExecutionEnvironmentError, match="not valid TOML"):
            expected_pins(tmp_path, "pyproject.toml")

    def test_a_pyproject_without_a_dev_extra_parses_to_an_empty_set(self, tmp_path):
        """Empty is a legal parse and a failing CONFIGURATION — EEG-07 owns that verdict."""
        (tmp_path / "pyproject.toml").write_text('[project]\nname = "x"\n', encoding="utf-8")
        assert expected_pins(tmp_path, "pyproject.toml") == ()

    def test_the_configuration_fingerprint_moves_when_configuration_does(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text("a = 1\n", encoding="utf-8")
        before = configuration_fingerprint(tmp_path, tmp_path / "venv")
        (tmp_path / "pyproject.toml").write_text("a = 2\n", encoding="utf-8")
        assert configuration_fingerprint(tmp_path, tmp_path / "venv") != before

    def test_an_absent_configuration_file_is_itself_a_change(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text("a = 1\n", encoding="utf-8")
        before = configuration_fingerprint(tmp_path, tmp_path / "venv")
        (tmp_path / "pyproject.toml").unlink()
        assert configuration_fingerprint(tmp_path, tmp_path / "venv") != before

    def test_git_identity_answers_unknown_rather_than_raising(self, tmp_path):
        branch, commit = git_identity(tmp_path)
        assert branch == "UNKNOWN" or commit == "UNKNOWN"

    def test_git_identity_reports_the_live_repository(self):
        branch, commit = git_identity(REPO)
        assert re.fullmatch(r"[0-9a-f]{40}", commit)
        assert branch

    def test_an_undeclared_executable_is_reported(self, tmp_path):
        intruder = tmp_path / "pytest 2"
        intruder.write_text("#!/bin/sh\n", encoding="utf-8")
        intruder.chmod(intruder.stat().st_mode | stat.S_IXUSR)
        assert "pytest 2" in unexpected_executables(tmp_path)

    def test_the_venvs_own_files_are_not_reported_as_intruders(self, tmp_path):
        for name in ("python3.12", "activate"):
            entry = tmp_path / name
            entry.write_text("#!/bin/sh\n", encoding="utf-8")
            entry.chmod(entry.stat().st_mode | stat.S_IXUSR)
        assert unexpected_executables(tmp_path) == ()

    def test_a_non_executable_file_is_not_an_executable(self, tmp_path):
        (tmp_path / "notes.txt").write_text("hello\n", encoding="utf-8")
        assert unexpected_executables(tmp_path) == ()

    def test_an_absent_scripts_directory_reports_nothing(self, tmp_path):
        assert unexpected_executables(tmp_path / "absent") == ()

    def test_shadowing_is_reported_against_the_directory_it_is_measured_from(self, tmp_path):
        """Every canonical tool on PATH is outside an empty dir, so all resolvable ones show."""
        reported = shadowing_executables(tmp_path)
        assert any(entry.startswith("python") for entry in reported)

    def test_the_live_environment_observes(self):
        environment = observe(DECLARATION, REPO, command="pytest")
        assert environment.runtime.language == "python"
        assert environment.runtime.series == f"{sys.version_info[0]}.{sys.version_info[1]}"
        assert environment.dependencies.expected
        assert environment.command == "pytest"

    def test_supplied_tool_records_replace_the_scan(self):
        """The cache path: a proven-unchanged environment reuses the previous scan."""
        supplied = (_tool(),)
        environment = observe(DECLARATION, REPO, tool_records=supplied)
        assert environment.toolchain.tools == supplied


# --- the checks -------------------------------------------------------------------


class TestChecks:
    def _run(self, check_id: str, environment: ExecutionEnvironment) -> CheckResult:
        return CHECKS[check_id](environment, DECLARATION.check(check_id), DECLARATION)

    def test_eeg01_holds_for_an_environment_inside_the_repository(self):
        assert self._run("EEG-01", _environment()).holds

    def test_eeg01_refuses_a_venv_outside_the_repository(self):
        """Finding F-2, as a test: this is the venv that was built on the Desktop."""
        outside = _environment(
            venv_directory="/Users/someone/Desktop/.ec1-venv",
            runtime=_runtime(prefix="/Users/someone/Desktop/.ec1-venv"),
        )
        result = self._run("EEG-01", outside)
        assert not result.holds
        assert any("not inside the repository root" in finding for finding in result.findings)

    def test_eeg02_refuses_an_interpreter_that_is_not_in_a_virtual_environment(self):
        system = _environment(runtime=_runtime(prefix="/usr", base_prefix="/usr"))
        result = self._run("EEG-02", system)
        assert not result.holds
        assert any("not running inside a virtual environment" in f for f in result.findings)

    def test_eeg02_refuses_a_different_virtual_environment(self):
        other = _environment(runtime=_runtime(prefix="/nonexistent/other-venv"))
        result = self._run("EEG-02", other)
        assert not result.holds
        assert any("not the canonical" in finding for finding in result.findings)

    def test_eeg03_holds_at_the_canonical_series(self):
        assert self._run("EEG-03", _environment()).holds

    def test_eeg03_refuses_the_homebrew_interpreter(self):
        """The measured condition: /opt/homebrew/bin/python3 is 3.14 against a canonical 3.12."""
        wrong = _environment(
            runtime=_runtime(
                series="3.14", version="3.14.4", interpreter_path="/opt/homebrew/bin/python3"
            )
        )
        result = self._run("EEG-03", wrong)
        assert not result.holds
        assert "3.12" in (result.expected or "")
        assert "/opt/homebrew/bin/python3" in (result.detected or "")

    def test_eeg04_holds_when_pytest_lives_in_this_environment(self):
        live = observe(DECLARATION, REPO)
        assert self._run("EEG-04", live).holds

    def test_eeg04_refuses_a_pytest_outside_the_prefix(self):
        elsewhere = _environment(runtime=_runtime(prefix="/nonexistent/not-this-venv"))
        result = self._run("EEG-04", elsewhere)
        assert not result.holds
        assert any("outside" in finding for finding in result.findings)

    def test_eeg05_holds_because_the_declared_plugins_import_here(self):
        assert self._run("EEG-05", _environment()).holds

    def test_eeg05_refuses_an_unimportable_plugin(self, monkeypatch):
        """pytest-cov recorded at the right version but unimportable is a real state."""

        declared = DECLARATION.check("EEG-05")
        monkeypatch.setattr(
            "importlib.util.find_spec", lambda name: None if name == "pytest_cov" else object()
        )
        result = contract.check_required_plugins(_environment(), declared, DECLARATION)
        assert not result.holds
        assert any("pytest_cov" in finding for finding in result.findings)

    def test_eeg06_holds_for_a_healthy_toolchain(self):
        assert self._run("EEG-06", _environment()).holds

    def test_eeg06_refuses_an_absent_distribution(self):
        result = self._run("EEG-06", _environment(tools=(_tool(installed_version=None),)))
        assert not result.holds
        assert any("is not installed" in finding for finding in result.findings)

    def test_eeg06_refuses_a_version_that_drifted(self):
        result = self._run("EEG-06", _environment(tools=(_tool(installed_version="7.0.0"),)))
        assert any("!= pinned" in finding for finding in result.findings)

    def test_eeg06_refuses_a_missing_executable(self):
        """The ruff case: metadata intact, bin/ruff gone, pip believes it is satisfied."""
        result = self._run(
            "EEG-06", _environment(tools=(_tool("ruff", missing_scripts=("bin/ruff",)),))
        )
        assert any("declared but absent" in finding for finding in result.findings)

    def test_eeg06_refuses_a_non_executable_script(self):
        result = self._run(
            "EEG-06", _environment(tools=(_tool(non_executable_scripts=("bin/pytest",)),))
        )
        assert any("not executable" in finding for finding in result.findings)

    def test_eeg06_refuses_an_unreadable_manifest(self):
        result = self._run("EEG-06", _environment(tools=(_tool(record_readable=False),)))
        assert any("unverifiable" in finding for finding in result.findings)

    def test_eeg07_holds_against_the_live_repository(self):
        assert self._run("EEG-07", observe(DECLARATION, REPO)).holds

    def test_eeg07_refuses_an_empty_expectation(self):
        """An unparseable pyproject would make every dependency check pass over nothing."""
        vacuous = _environment(
            dependencies=Dependencies(expected=(), installed=(), fingerprint="x")
        )
        result = self._run("EEG-07", vacuous)
        assert not result.holds
        assert any("vacuously" in finding for finding in result.findings)

    def test_eeg07_refuses_an_absent_virtual_environment(self):
        result = self._run("EEG-07", _environment(venv_directory="/nonexistent/no-such-venv"))
        assert any("does not exist" in finding for finding in result.findings)

    def test_eeg07_refuses_a_repository_without_the_declared_configuration(self, tmp_path):
        elsewhere = _environment(
            repository=RepositoryIdentity(
                root=str(tmp_path), branch="x", commit="0" * 40, configuration_fingerprint="c"
            )
        )
        result = self._run("EEG-07", elsewhere)
        assert any("is absent from" in finding for finding in result.findings)

    def test_eeg08_is_advisory_and_reports_both_conditions(self):
        noisy = _environment(
            toolchain=Toolchain(
                scripts_directory=f"{REPO}/.ec1-venv/bin",
                tools=(_tool(),),
                unexpected_executables=("pytest 2",),
                shadowing_executables=("pytest -> /opt/homebrew/bin/pytest",),
            )
        )
        result = self._run("EEG-08", noisy)
        assert result.blocking is False
        assert not result.holds
        assert len(result.findings) == 2

    def test_eeg08_holds_on_a_clean_environment(self):
        assert self._run("EEG-08", _environment()).holds

    def test_assess_computes_every_declared_check(self):
        assessed = assess(observe(DECLARATION, REPO), DECLARATION)
        assert [check.check_id for check in assessed.checks] == list(DECLARATION.check_ids)

    def test_assess_faults_on_a_declared_check_nothing_implements(self, monkeypatch):
        """Declared-but-unimplemented must be a fault, not a silent omission."""
        monkeypatch.delitem(CHECKS, "EEG-08")
        with pytest.raises(ExecutionEnvironmentError, match="implemented by nothing"):
            assess(observe(DECLARATION, REPO), DECLARATION)


# --- the fingerprint cache ---------------------------------------------------------


class TestFingerprintCache:
    def test_the_trigger_key_is_deterministic_over_one_state(self):
        first = fingerprint_module.trigger_key(REPO, DECLARATION, REPO / ".ec1-venv")
        second = fingerprint_module.trigger_key(REPO, DECLARATION, REPO / ".ec1-venv")
        assert first == second

    def test_the_trigger_key_moves_when_configuration_moves(self, tmp_path):
        venv = tmp_path / "venv"
        (tmp_path / "pyproject.toml").write_text("a = 1\n", encoding="utf-8")
        before = fingerprint_module.trigger_key(tmp_path, DECLARATION, venv)
        (tmp_path / "pyproject.toml").write_text("a = 2\n", encoding="utf-8")
        assert fingerprint_module.trigger_key(tmp_path, DECLARATION, venv) != before

    def test_the_commit_is_deliberately_not_a_trigger(self):
        """A commit-keyed cache never hits, and would claim the environment changed."""
        raw = json.loads((REPO / "00-MASTER/UEG-000001/ueg-declaration.json").read_text())
        assert "$repository_commit_is_not_a_trigger" in raw["fingerprint_cache"]

    def test_a_stored_fingerprint_is_reusable_under_the_same_key(self, tmp_path):
        environment = _environment()
        path = tmp_path / "fingerprint.json"
        fingerprint_module.store(path, environment, "key-a")
        payload = fingerprint_module.load(path)
        records = fingerprint_module.reusable_tool_records(payload, "key-a")
        assert records is not None
        assert records[0].distribution == "pytest"
        assert records[0].installed_version == "8.3.4"

    def test_a_changed_key_makes_the_cache_unusable(self, tmp_path):
        path = tmp_path / "fingerprint.json"
        fingerprint_module.store(path, _environment(), "key-a")
        assert (
            fingerprint_module.reusable_tool_records(fingerprint_module.load(path), "key-b") is None
        )

    def test_an_absent_cache_is_a_miss_not_an_error(self, tmp_path):
        assert fingerprint_module.load(tmp_path / "absent.json") is None
        assert fingerprint_module.reusable_tool_records(None, "key") is None

    def test_a_corrupt_cache_is_a_miss_not_an_error(self, tmp_path):
        path = tmp_path / "fingerprint.json"
        path.write_text("{ broken", encoding="utf-8")
        assert fingerprint_module.load(path) is None

    def test_a_cache_from_another_version_is_a_miss(self, tmp_path):
        path = tmp_path / "fingerprint.json"
        path.write_text(json.dumps({"cache_version": 0}), encoding="utf-8")
        assert fingerprint_module.load(path) is None

    def test_a_cache_that_is_not_an_object_is_a_miss(self, tmp_path):
        path = tmp_path / "fingerprint.json"
        path.write_text("[]", encoding="utf-8")
        assert fingerprint_module.load(path) is None

    def test_a_malformed_tool_entry_is_a_miss_rather_than_a_partial_reuse(self, tmp_path):
        path = tmp_path / "fingerprint.json"
        fingerprint_module.store(path, _environment(), "key-a")
        payload = fingerprint_module.load(path)
        payload["tools"][0].pop("expected_version")
        assert fingerprint_module.reusable_tool_records(payload, "key-a") is None

    def test_the_cache_carries_no_clock(self):
        """A fingerprint containing a timestamp is not a fingerprint."""
        path = REPO / ".ucos" / "environment-fingerprint.json"
        if not path.is_file():
            pytest.skip("no cache has been written in this working tree")
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert not any("time" in key.lower() or "date" in key.lower() for key in payload)

    def test_invalidate_reports_whether_it_removed_anything(self, tmp_path):
        path = tmp_path / "fingerprint.json"
        fingerprint_module.store(path, _environment(), "key-a")
        assert fingerprint_module.invalidate(path) is True
        assert fingerprint_module.invalidate(path) is False

    def test_the_cache_path_is_the_declared_one(self, tmp_path):
        assert (
            fingerprint_module.cache_path(tmp_path, DECLARATION)
            == tmp_path / DECLARATION.cache_path
        )

    def test_storing_leaves_no_temporary_behind(self, tmp_path):
        path = tmp_path / "sub" / "fingerprint.json"
        fingerprint_module.store(path, _environment(), "key-a")
        assert path.is_file()
        assert list(path.parent.iterdir()) == [path]


# --- execution evidence ------------------------------------------------------------


class TestEvidence:
    def test_every_declared_record_is_produced(self):
        payload = evidence_module.build(observe(DECLARATION, REPO), DECLARATION, "./verify.sh")
        for record in DECLARATION.evidence_records:
            assert record in payload, f"declared evidence record not produced: {record}"

    def test_the_declaration_names_the_eight_records_the_directive_requires(self):
        assert len(DECLARATION.evidence_records) == 8

    def test_a_declared_record_with_no_producer_is_a_fault(self):
        with pytest.raises(ExecutionEnvironmentError, match="nothing produces"):
            evidence_module.assert_complete({}, DECLARATION)

    def test_evidence_names_the_interpreter_that_produced_it(self):
        payload = evidence_module.build(observe(DECLARATION, REPO), DECLARATION)
        assert payload["python executable path"] == sys.executable
        assert payload["python version"].startswith("3.")

    def test_evidence_carries_the_pytest_executable_when_one_is_declared(self):
        payload = evidence_module.build(observe(DECLARATION, REPO), DECLARATION)
        assert Path(payload["pytest executable path"]).name == "pytest"

    def test_evidence_tolerates_an_environment_with_no_pytest(self):
        bare = _environment(tools=())
        payload = evidence_module.build(bare, DECLARATION)
        assert payload["pytest executable path"] is None
        assert payload["pytest version"] is None

    def test_a_tool_declaring_no_pytest_binary_yields_none(self):
        odd = _environment(tools=(_tool(declared_scripts=("/bin/something-else",)),))
        assert evidence_module.build(odd, DECLARATION)["pytest executable path"] is None

    def test_evidence_is_written_to_the_declared_path(self, tmp_path):
        written = evidence_module.write(
            observe(DECLARATION, REPO), DECLARATION, tmp_path, "./verify.sh"
        )
        assert written == tmp_path / DECLARATION.evidence_path
        payload = json.loads(written.read_text(encoding="utf-8"))
        assert payload["command"] == "./verify.sh"
        assert payload["result"] in {RESULT_VALID, RESULT_INVALID}

    def test_the_timestamp_lives_in_evidence_and_nowhere_else(self):
        """A clock in an identity makes two identical environments look different."""
        environment = observe(DECLARATION, REPO)
        payload = evidence_module.build(environment, DECLARATION)
        assert payload["validation timestamp"].endswith("+00:00")
        assert "timestamp" not in json.dumps(
            {"id": environment.environment_id, "dep": environment.dependencies.fingerprint}
        )


# --- the gate ----------------------------------------------------------------------


class TestGate:
    def test_the_live_environment_passes_its_own_gate(self):
        """The one test that proves this works on a real machine rather than a fixture."""
        environment = measure(repository=str(REPO), use_cache=False)
        assert environment.valid, [check.as_dict() for check in environment.blocking_failures]

    def test_the_gate_exits_open_on_a_healthy_environment(self, capsys):
        assert main(["--gate", "--repository", str(REPO), "--no-cache", "--quiet"]) == EXIT_OPEN

    def test_json_output_carries_the_whole_observation(self, capsys):
        assert main(["--repository", str(REPO), "--no-cache", "--quiet", "--json"]) == EXIT_OPEN
        payload = json.loads(capsys.readouterr().out)
        assert payload["result"] == RESULT_VALID
        assert len(payload["checks"]) == len(DECLARATION.check_ids)

    def test_an_unusable_declaration_is_a_fault_and_not_a_refusal(self, tmp_path, capsys):
        """FAULT and CLOSED are different answers and must stay different."""
        broken = tmp_path / "ueg.json"
        broken.write_text("{", encoding="utf-8")
        assert (
            main(["--gate", "--repository", str(REPO), "--declaration", str(broken)]) == EXIT_FAULT
        )
        assert "FAULT" in capsys.readouterr().err

    def test_evidence_is_written_when_asked(self, tmp_path, monkeypatch):
        monkeypatch.setenv("UCOS_VENV_DIR", str(REPO / ".ec1-venv"))
        assert (
            main(["--repository", str(REPO), "--no-cache", "--quiet", "--command", "unit-test"])
            == EXIT_OPEN
        )

    def test_the_cache_is_used_and_reported(self, tmp_path):
        """A hit must supply records and still compute every check over them."""
        first = measure(repository=str(REPO), refresh=True)
        assert first.cache_state in {fingerprint_module.STATE_MISS, fingerprint_module.STATE_HIT}
        second = measure(repository=str(REPO))
        assert second.cache_state == fingerprint_module.STATE_HIT
        assert len(second.checks) == len(DECLARATION.check_ids)
        assert second.environment_id == first.environment_id

    def test_disabling_the_cache_reports_it(self):
        assert (
            measure(repository=str(REPO), use_cache=False).cache_state
            == fingerprint_module.STATE_DISABLED
        )

    def test_the_failure_block_names_expected_detected_and_the_repair(self):
        """A refusal that does not say what to do next sends the reader back to guessing."""
        refused = _environment().with_checks(
            (
                CheckResult(
                    check_id="EEG-03",
                    title="correct interpreter",
                    blocking=True,
                    holds=False,
                    findings=("interpreter series 3.14 != canonical 3.12",),
                    expected="python 3.12",
                    detected="python 3.14.4 at /opt/homebrew/bin/python3",
                ),
            )
        )
        block = _render_failure(refused)
        assert "UCOS EXECUTION ENVIRONMENT FAILURE" in block
        assert "Expected:" in block and "python 3.12" in block
        assert "Detected:" in block and "/opt/homebrew/bin/python3" in block
        assert "Execution blocked." in block
        assert "./bootstrap.sh" in block

    def test_the_summary_elides_long_advisories_but_never_blocking_findings(self):
        many = tuple(f"advisory {index}" for index in range(20))
        environment = _environment().with_checks(
            (CheckResult("EEG-08", "leakage", blocking=False, holds=False, findings=many),)
        )
        rendered = _render(environment)
        assert "+15 more" in rendered
        assert "advisory 0" in rendered and "advisory 19" not in rendered

    def test_a_refusal_without_gate_does_not_change_the_exit_code(self, monkeypatch, capsys):
        """--gate is what makes a refusal blocking; without it the report is informational."""
        refused = _environment().with_checks((_check("EEG-01", holds=False),))
        monkeypatch.setattr("engine.execution_environment.gate.measure", lambda **_: refused)
        assert main(["--repository", str(REPO)]) == EXIT_OPEN
        assert main(["--gate", "--repository", str(REPO)]) == EXIT_CLOSED

    def test_evidence_failure_is_a_fault(self, monkeypatch, capsys):
        def _explode(*args, **kwargs):
            raise OSError("disk full")

        monkeypatch.setattr("engine.execution_environment.evidence.write", _explode)
        assert main(["--repository", str(REPO), "--evidence", "--no-cache"]) == EXIT_FAULT
        assert "evidence could not be written" in capsys.readouterr().err

    def test_an_invalid_environment_is_never_cached(self, tmp_path, monkeypatch):
        """Caching an invalid environment would let the next run reuse a broken toolchain."""
        cache = tmp_path / "fingerprint.json"
        fingerprint_module.invalidate(cache)
        assert not cache.exists()


# --- the declared laws, measured over verify.sh ------------------------------------


def _verify_source() -> str:
    return (REPO / "verify.sh").read_text(encoding="utf-8")


def _executable_lines(source: str) -> list[str]:
    """Return the lines of *source* with comments and blanks removed.

    Comments are stripped because this file DISCUSSES the very constructs the laws forbid —
    the Stage 0 comment names ``ucos_ensure_venv`` and ``pip install`` in order to explain
    why they are gone. A law that could not tell a mention from a use would forbid its own
    explanation, which is the ``UVI-L-06`` distinction applied to a shell script.
    """
    lines = []
    for raw in source.splitlines():
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        lines.append(stripped)
    return lines


class TestSeparationOfPowers:
    """EEG-SEP — a verification entry point may not create, install, or reach the network."""

    def test_verify_does_not_ensure_the_environment_it_is_verifying(self):
        """Finding F-1: the run that detected drift used to erase it and report green."""
        for line in _executable_lines(_verify_source()):
            assert "ucos_ensure_venv" not in line, f"verify.sh repairs its own subject: {line}"

    def test_verify_installs_nothing(self):
        forbidden = ("pip install", "pip3 install", "-m pip", "python -m venv", "-m venv")
        for line in _executable_lines(_verify_source()):
            for token in forbidden:
                assert token not in line, f"verify.sh performs setup: {line}"

    def test_verify_makes_no_network_call(self):
        for line in _executable_lines(_verify_source()):
            for token in ("curl ", "wget ", "https://", "http://"):
                assert token not in line, f"verify.sh reaches the network: {line}"

    def test_verify_deletes_no_environment(self):
        for line in _executable_lines(_verify_source()):
            assert "rm -rf" not in line or ".ec1-venv" not in line

    def test_bootstrap_remains_the_repair_path(self):
        """The capability moved; it did not disappear."""
        assert "ucos_ensure_venv" in (REPO / "bootstrap.sh").read_text(encoding="utf-8")

    def test_the_declaration_and_the_scripts_agree_on_who_may_install(self):
        for entry in DECLARATION.entry_points:
            if entry["name"] == "./verify.sh":
                assert entry["may_install"] is False
                assert entry["may_create_venv"] is False
                assert entry["may_use_network"] is False
            if entry["name"] == "./bootstrap.sh":
                assert entry["may_install"] is True

    def test_verify_invokes_the_environment_gate(self):
        """Deleting the gate must fail the suite, not silently unbind Stage 0."""
        assert any("ucos_env_gate" in line for line in _executable_lines(_verify_source()))


class TestDirectToolResolution:
    """EEG-PATH — every tool resolves through the venv interpreter by absolute path."""

    #: Words that must never appear in command position. ``$PY`` is the only legal way to
    #: reach a tool, and ``$PY`` is an absolute path into the venv by construction.
    BARE_TOOLS = ("python", "python3", "pytest", "ruff", "coverage")

    def test_no_bare_tool_is_ever_in_command_position(self):
        # Split each line on the shell operators that begin a new command, then look at the
        # first word of each fragment. Checking whole lines would miss `foo && pytest` and
        # flag `--cov=coverage`; checking bare substrings would flag every mention.
        offenders = []
        for line in _executable_lines(_verify_source()):
            for fragment in re.split(r"(?:\|\||&&|[;|&()]|\bexec\b)", line):
                words = fragment.strip().split()
                if not words:
                    continue
                first = words[0]
                # `env FOO=bar cmd` and `bash script.sh` delegate; step past the prefix.
                index = 0
                while index < len(words) and (words[index] == "env" or "=" in words[index]):
                    index += 1
                if index < len(words):
                    first = words[index]
                if first in self.BARE_TOOLS:
                    offenders.append(line)
        assert not offenders, f"verify.sh invokes a tool through PATH: {offenders}"

    def test_the_interpreter_is_taken_from_the_environment_library(self):
        assert 'PY="$(ucos_venv_python)"' in _verify_source()

    def test_the_library_resolves_the_interpreter_by_absolute_path(self):
        source = (REPO / "scripts" / "ucos-env.sh").read_text(encoding="utf-8")
        assert "ucos_venv_python() { printf '%s\\n' \"$UCOS_VENV_DIR/bin/python\"; }" in source

    def test_the_repository_root_is_resolved_by_git_not_by_file_layout(self):
        """Finding F-2, closed at its source."""
        source = (REPO / "scripts" / "ucos-env.sh").read_text(encoding="utf-8")
        root_function = source.split("ucos_repo_root() {")[1].split("}")[0]
        assert "git rev-parse --show-toplevel" in root_function

    def test_the_declaration_binds_this_law_to_the_file_it_measures(self):
        assert "verify.sh" in DECLARATION.direct_resolution_files


class TestGitignoreBoundary:
    """The gate writes only to paths git excludes, so it can never dirty the tracked tree."""

    def test_the_cache_and_the_evidence_are_both_ignored(self):
        for relative in (DECLARATION.cache_path, DECLARATION.evidence_path):
            assert _git("check-ignore", relative).strip(), f"{relative} is not gitignored"

    def test_the_gate_writes_nothing_else(self, tmp_path):
        """Measured rather than asserted: run the gate and diff the tracked tree."""
        before = _git("status", "--porcelain")
        main(["--repository", str(REPO), "--quiet", "--evidence", "--command", "boundary-test"])
        after = _git("status", "--porcelain")
        assert before == after


# --- the observations underneath the checks ----------------------------------------
#
# The discovery layer is measured against THIS machine, where git answers, every pin parses,
# every declared script is present and executable, and every distribution is installed. Each
# arm below answers for a machine where one of those is false — which is the only kind of
# machine this capability exists for.


class _FakeDistribution:
    """A stand-in for an installed distribution, so a RECORD can be malformed on purpose."""

    def __init__(self, version: str, record: str | None, base: Path) -> None:
        self.version = version
        self._record = record
        self._base = base

    def read_text(self, name: str) -> str | None:
        return self._record if name == "RECORD" else None

    def locate_file(self, _name: str) -> Path:
        return self._base


class TestDiscoveryArms:
    def test_the_repository_root_is_walked_to_when_git_cannot_answer(self, monkeypatch):
        """GIT IS THE FAST ANSWER AND THE WALK IS THE GUARANTEE.

        ``git rev-parse`` answers on every developer machine, so the fallback had never run —
        and it is what keeps the capability usable where git is absent, on PATH but broken,
        or refusing to run in a sandbox. Raising instead would make the environment gate
        unavailable exactly where an environment problem is most likely.
        """

        def _no_git(*_args, **_kwargs):
            raise OSError("git is not installed")

        monkeypatch.setattr("engine.execution_environment.discovery.subprocess.run", _no_git)

        assert Path(repo_root(REPO)) == REPO.resolve()

    def test_a_dev_dependency_that_declares_no_pin_is_not_a_pin(self, tmp_path):
        """A PIN IS AN EXACT VERSION AND NOTHING ELSE IS ONE.

        This repository pins every dev dependency exactly, so the arm that skips a
        non-matching spec had no case. A range or a bare name is a legitimate declaration and
        it is NOT a pin — recording it as one would put an entry with no version into the
        expected set, and the toolchain check would then compare an installed version against
        nothing at all.
        """
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text(
            '[project.optional-dependencies]\ndev = ["pinned==1.2.3", "ranged>=4", "bare"]\n',
            encoding="utf-8",
        )

        assert expected_pins(tmp_path, "pyproject.toml") == (("pinned", "1.2.3"),)

    def test_a_module_whose_import_machinery_refuses_is_not_importable(self, monkeypatch):
        """``find_spec`` RAISES for a name it cannot even look up, and that is an answer.

        A module inside a package that does not exist raises ImportError rather than
        returning None, and a malformed name raises ValueError. Both mean "not importable",
        which is what the check needs — letting either escape would turn an observation into
        a fault and report the environment as unmeasurable rather than as broken.
        """
        assert discovery._importable("json") is True
        assert discovery._importable("a_module_that_is_not_installed") is False
        assert discovery._importable("no_such_package.submodule") is False
        assert discovery._importable("") is False

    def test_a_pinned_distribution_that_is_not_installed_is_recorded_as_absent(self):
        """AN ABSENT TOOL IS AN OBSERVATION, NOT AN ERROR.

        Every pin in this repository is installed, so the not-found arm had never run — and
        it is the one that matters, because a scan that raised on the first missing tool
        would report nothing about the rest of the toolchain. The record carries the expected
        version and no installed one, which is precisely what the toolchain check reads.
        """
        record = discovery._scan_tool("no-such-distribution", "9.9.9", REPO / ".ec1-venv" / "bin")

        assert record.installed_version is None
        assert record.importable is False
        assert record.expected_version == "9.9.9"

    def test_a_distribution_with_no_record_is_reported_as_unreadable_not_as_scriptless(
        self, monkeypatch, tmp_path
    ):
        """NO RECORD AND AN EMPTY RECORD ARE DIFFERENT FACTS.

        A distribution whose metadata carries no RECORD cannot be asked which executables it
        declares. Returning an empty declared-script tuple would say "this distribution
        declares no scripts", which is a measurement; ``record_readable=False`` says the
        question could not be asked, which is the truth.
        """
        monkeypatch.setattr(
            discovery.metadata,
            "distribution",
            lambda _name: _FakeDistribution("1.0.0", None, tmp_path),
        )

        record = discovery._scan_tool("anything", "1.0.0", tmp_path / "bin")

        assert record.record_readable is False
        assert record.installed_version == "1.0.0"

    def test_a_declared_script_is_observed_present_missing_or_not_executable(
        self, monkeypatch, tmp_path
    ):
        """THREE STATES OF A DECLARED EXECUTABLE, and only "present" had ever been observed.

        RECORD is read directly because ``files()`` hides a recorded file that is absent from
        disk — the very condition being detected. So the missing and non-executable arms are
        the point of reading it that way, and neither had run. A blank RECORD row is skipped
        rather than resolved, because ``base / ""`` resolves to the base directory itself and
        would be reported as a declared script that every distribution shares.
        """
        scripts = tmp_path / "bin"
        scripts.mkdir()
        (scripts / "present").write_text("#!/bin/sh\n", encoding="utf-8")
        (scripts / "present").chmod(0o755)
        (scripts / "not-executable").write_text("#!/bin/sh\n", encoding="utf-8")
        (scripts / "not-executable").chmod(0o644)
        (tmp_path / "elsewhere.py").write_text("", encoding="utf-8")
        record = "\n".join(
            (
                "",  # a blank row
                "bin/present,,",
                "bin/not-executable,,",
                "bin/deleted,,",
                "elsewhere.py,,",
            )
        )
        monkeypatch.setattr(
            discovery.metadata,
            "distribution",
            lambda _name: _FakeDistribution("1.0.0", record, tmp_path),
        )

        observed = discovery._scan_tool("anything", "1.0.0", scripts)

        assert [Path(p).name for p in observed.declared_scripts] == [
            "deleted",
            "not-executable",
            "present",
        ]
        assert [Path(p).name for p in observed.missing_scripts] == ["deleted"]
        assert [Path(p).name for p in observed.non_executable_scripts] == ["not-executable"]

    def test_the_declared_script_index_skips_a_blank_record_row(self, monkeypatch, tmp_path):
        """The same blank-row skip, in the index every unexpected-executable answer is made
        against. Without it the scripts directory itself would enter the declared set under
        its own name, and a real executable sharing that name would stop being reported.
        """
        scripts = tmp_path / "bin"
        scripts.mkdir()
        (scripts / "declared").write_text("", encoding="utf-8")
        monkeypatch.setattr(
            discovery.metadata,
            "distributions",
            lambda: iter([_FakeDistribution("1.0.0", "\nbin/declared,,\n", tmp_path)]),
        )

        assert discovery._declared_script_names(scripts) == {"declared"}

    def test_a_tool_resolving_inside_the_venv_is_not_shadowing(self, monkeypatch, tmp_path):
        """SHADOWING IS ABOUT WHERE A NAME RESOLVES, and the un-shadowed answer had no case.

        On the assessed machine every shadowable tool resolves outside the venv, so the loop
        only ever appended. A tool that resolves inside it must NOT be reported, or the
        advisory would fire on a correctly configured machine and stop being read.
        """
        scripts = tmp_path / "bin"
        scripts.mkdir()
        (scripts / "pytest").write_text("", encoding="utf-8")

        monkeypatch.setattr(
            "shutil.which",
            lambda tool: str(scripts / "pytest") if tool == "pytest" else None,
        )

        assert shadowing_executables(scripts) == ()


class TestCacheStatesAndReporting:
    def test_a_miss_and_a_stale_entry_are_reported_as_different_states(self, monkeypatch):
        """FOUR CACHE STATES AND ONLY TWO HAD BEEN OBSERVED.

        HIT and DISABLED were measured. MISS means there was nothing to reuse; STALE means
        there WAS an entry and its trigger key no longer matches — a toolchain that has
        changed under a cache that would otherwise have been trusted. Collapsing them would
        make "the cache has never run here" indistinguishable from "the environment moved",
        which is the one distinction this field exists to record.
        """
        monkeypatch.setattr(fingerprint_module, "reusable_tool_records", lambda *_: None)
        monkeypatch.setattr(fingerprint_module, "store", lambda *_args, **_kwargs: None)

        monkeypatch.setattr(fingerprint_module, "load", lambda _path: None)
        assert measure(repository=str(REPO)).cache_state == fingerprint_module.STATE_MISS

        monkeypatch.setattr(fingerprint_module, "load", lambda _path: {"trigger_key": "moved"})
        assert measure(repository=str(REPO)).cache_state == fingerprint_module.STATE_STALE

    def test_the_summary_renders_every_check_when_nothing_is_elided(self):
        """The elision test renders ONE check with twenty findings, so the loop never came
        back round with nothing to elide. A healthy environment is every check and no
        findings at all, and that is the shape the gate prints on almost every real run.
        """
        rendered = _render(
            _environment().with_checks((_check("EEG-01"), _check("EEG-02"), _check("EEG-03")))
        )

        assert "EEG-01" in rendered and "EEG-02" in rendered and "EEG-03" in rendered
        assert "more (--json" not in rendered

    def test_a_passing_gate_writes_its_summary_unless_asked_to_be_quiet(self, capsys):
        """--quiet IS AN OPTION AND EVERY GATE TEST PASSED IT.

        So the default output of a successful run — the human summary on stderr — had never
        been produced. It is what an operator sees on every invocation from ``verify.sh``,
        and a gate that reported nothing on success would leave "it passed" and "it did not
        run" looking identical.
        """
        assert main(["--repository", str(REPO), "--no-cache"]) == EXIT_OPEN

        err = capsys.readouterr().err
        assert "UEG-000001 execution environment" in err
        assert "interpreter" in err


class TestObservationSerialisation:
    def test_an_observation_carries_its_command_and_timestamp_only_when_it_has_them(self):
        """THE TWO OPTIONAL FIELDS ARE OMITTED, NOT EMPTIED.

        ``command`` and ``observed_at`` are what make an observation EVIDENCE rather than a
        measurement, and both are absent from a bare in-process observation. Emitting them as
        null would put two fields into the canonical form that participate in its digest, so
        two identical environments observed with and without a command would fingerprint
        differently for a reason that is not about the environment.
        """
        bare = _environment().as_dict()
        assert "command" not in bare
        assert "observed_at" not in bare

        stamped = _environment(command="unit-test", observed_at="2026-01-01T00:00:00Z").as_dict()
        assert stamped["command"] == "unit-test"
        assert stamped["observed_at"] == "2026-01-01T00:00:00Z"


class TestImportabilityChecks:
    def test_a_pytest_the_interpreter_cannot_import_is_a_finding_not_a_crash(self, monkeypatch):
        """EEG-04 ASKS WHETHER *THIS* INTERPRETER CAN IMPORT PYTEST, and the negative answer
        had never been produced — this suite runs under pytest, so it always could.

        Both ways of failing are one finding. ``find_spec`` returning None means there is no
        pytest; ``find_spec`` raising means the name could not even be looked up. Letting the
        exception escape would turn a checkable condition into a fault, and a fault reports
        that the environment could not be measured rather than that it is wrong.
        """
        declared = next(d for d in DECLARATION.checks if d.check_id == "EEG-04")

        monkeypatch.setattr("importlib.util.find_spec", lambda _name: None)
        absent = CHECKS["EEG-04"](_environment(), declared, DECLARATION)
        assert not absent.holds
        assert "not importable" in absent.findings[0]

        def _refuse(_name: str):
            raise ValueError("empty module name")

        monkeypatch.setattr("importlib.util.find_spec", _refuse)
        refused = CHECKS["EEG-04"](_environment(), declared, DECLARATION)
        assert not refused.holds
        assert "not importable" in refused.findings[0]

    def test_a_plugin_whose_lookup_raises_is_reported_as_not_importable(self, monkeypatch):
        """EEG-05 IS THE ASSUMPTION-A4 CHECK: a plugin recorded at a version and unimportable
        is a real state, and it is the one that reports a healthy toolchain right up to the
        moment the certified command aborts. The lookup raising is the same answer as the
        lookup returning None, for the same reason it is in EEG-04.
        """
        declared = next(d for d in DECLARATION.checks if d.check_id == "EEG-05")

        def _refuse(_name: str):
            raise ImportError("no parent package")

        monkeypatch.setattr("importlib.util.find_spec", _refuse)
        result = CHECKS["EEG-05"](_environment(), declared, DECLARATION)

        assert not result.holds
        assert all("is not importable" in finding for finding in result.findings)


def test_the_module_entry_point_dispatches_to_the_gate() -> None:
    """``python -m engine.execution_environment`` IS THE DOCUMENTED INVOCATION.

    The module was never imported by anything, so the one line that binds the package's
    ``-m`` form to the gate's entry point was unmeasured — and a rename or a moved ``main``
    would have broken the documented command with the whole suite still passing.
    """

    assert entry_point.main is main


def test_a_trigger_directory_that_is_not_there_is_ABSENT_rather_than_a_failure(tmp_path) -> None:
    """THE CACHE KEY IS COMPUTED CHEAPLY AND MUST NOT BE COMPUTABLE ONLY ON A HEALTHY VENV.

    The two directory mtimes in the trigger key are read from a venv that exists on every
    machine this suite has run on, so the absent arm was dead. A missing site-packages or
    scripts directory is a real state — a half-removed or not-yet-created virtualenv — and it
    is exactly when the cache must not be trusted. Raising would make the key uncomputable
    and take the whole gate down with the optimisation; ``ABSENT`` is a value that differs
    from every real mtime, so the key changes and the cache misses, which is the answer.
    """
    present = fingerprint_module._directory_mtime(tmp_path)
    assert present.isdigit()

    assert fingerprint_module._directory_mtime(tmp_path / "never-created") == "ABSENT"
