"""TASK-000031/000034 — Hermetic build controls tests.

Verifies timestamp / ordering / locale / timezone / environment normalization,
pinned toolchain verification, dependency-lock verification, and deterministic
serialization validation. Two clean environments must produce identical compiler
inputs (identical fingerprints).
"""

from __future__ import annotations

import os

import pytest

from engine.compiler.packaging import COMPILER_TOOLCHAIN, TOOLCHAIN_VERSION
from engine.compiler.parser import parse_document
from engine.determinism.errors import (
    DependencyLockError,
    HermeticViolation,
    ToolchainError,
)
from engine.determinism.hermetic import (
    NORMALIZED_LOCALE,
    NORMALIZED_TIMESTAMP,
    NORMALIZED_TIMEZONE,
    SOURCE_DATE_EPOCH,
    HermeticEnvironment,
    hermetic_env,
)

# -- construction & fingerprint -----------------------------------------------


def test_hermetic_env_is_deterministic_across_constructions():
    a = hermetic_env()
    b = hermetic_env()
    assert a == b
    assert a.fingerprint() == b.fingerprint()
    assert a.toolchain == COMPILER_TOOLCHAIN
    assert a.toolchain_version == TOOLCHAIN_VERSION


def test_two_clean_environments_produce_identical_inputs(data_blueprint):
    # Acceptance (TASK-000031): two clean environments produce identical compiler
    # inputs — same normalized env, same normalized IR bytes.
    from engine.compiler.serialization import serialize

    env_a = hermetic_env()
    env_b = hermetic_env()
    assert env_a.normalized_environment() == env_b.normalized_environment()
    ir = parse_document(data_blueprint)
    with env_a.apply():
        bytes_a = serialize(ir)
    with env_b.apply():
        bytes_b = serialize(ir)
    assert bytes_a == bytes_b


# -- timestamp normalization --------------------------------------------------


def test_timestamp_normalization():
    env = hermetic_env()
    assert env.timestamp() == NORMALIZED_TIMESTAMP
    assert env.source_date_epoch == SOURCE_DATE_EPOCH
    assert env.normalized_environment()["SOURCE_DATE_EPOCH"] == "0"


# -- ordering normalization ---------------------------------------------------


def test_ordering_normalization():
    env = hermetic_env()
    assert env.order(["c", "a", "b"]) == ["a", "b", "c"]
    assert env.order([3, 1, 2], key=lambda x: -x) == [3, 2, 1]
    assert env.order_paths(["z/b.txt", "a/c.txt", "a/b.txt"]) == [
        "a/b.txt",
        "a/c.txt",
        "z/b.txt",
    ]


# -- locale / timezone / environment normalization ----------------------------


def test_locale_and_timezone_normalization():
    env = hermetic_env()
    assert env.locale == NORMALIZED_LOCALE
    assert env.timezone == NORMALIZED_TIMEZONE
    normalized = env.normalized_environment()
    assert normalized["LC_ALL"] == "C"
    assert normalized["LANG"] == "C"
    assert normalized["TZ"] == "UTC"
    assert normalized["PYTHONHASHSEED"] == "0"


def test_apply_sets_and_restores_environment(monkeypatch):
    monkeypatch.setenv("LC_ALL", "en_US.UTF-8")
    monkeypatch.delenv("TZ", raising=False)
    env = hermetic_env()
    with env.apply():
        assert os.environ["LC_ALL"] == "C"
        assert os.environ["TZ"] == "UTC"
        assert os.environ["PYTHONHASHSEED"] == "0"
    # restored to prior state
    assert os.environ["LC_ALL"] == "en_US.UTF-8"
    assert "TZ" not in os.environ


# -- pinned toolchain verification --------------------------------------------


def test_verify_toolchain_passes_for_current_interpreter():
    hermetic_env().verify_toolchain()  # does not raise on >= 3.12


def test_verify_toolchain_detects_drift():
    env = HermeticEnvironment(
        toolchain="rogue-compiler",
        toolchain_version="9.9.9",
        python_requires=">=3.12",
        source_date_epoch=0,
        normalized_timestamp=NORMALIZED_TIMESTAMP,
        locale="C",
        timezone="UTC",
        _environment=(),
    )
    with pytest.raises(ToolchainError):
        env.verify_toolchain()


def test_verify_toolchain_detects_old_python(monkeypatch):
    import engine.determinism.hermetic as hermetic

    monkeypatch.setattr(hermetic, "PINNED_PYTHON", (99, 0))
    with pytest.raises(ToolchainError) as exc:
        hermetic.hermetic_env()
    assert exc.value.code == "DET-TOOLCHAIN-001"


# -- dependency locking verification ------------------------------------------


def test_dependency_lock_verifies_real_pyproject():
    report = hermetic_env().verify_dependency_lock()
    assert report.locked
    assert report.runtime_dependencies == ()
    assert all("==" in spec for spec in report.dev_dependencies)
    assert report.to_dict()["locked"] is True


def test_dependency_lock_rejects_unpinned_dev(tmp_path):
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        '[project]\ndependencies = []\n[project.optional-dependencies]\ndev = ["pytest>=8"]\n',
        encoding="utf-8",
    )
    with pytest.raises(DependencyLockError) as exc:
        hermetic_env().verify_dependency_lock(pyproject)
    assert exc.value.context["unpinned_dev"] == ["pytest>=8"]


def test_dependency_lock_rejects_runtime_deps(tmp_path):
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text('[project]\ndependencies = ["requests==2.0.0"]\n', encoding="utf-8")
    with pytest.raises(DependencyLockError):
        hermetic_env().verify_dependency_lock(pyproject)


def test_dependency_lock_missing_pyproject(tmp_path):
    with pytest.raises(DependencyLockError):
        hermetic_env().verify_dependency_lock(tmp_path / "nope.toml")


# -- deterministic serialization validation -----------------------------------


def test_validate_serialization_round_trip(data_blueprint):
    ir = parse_document(data_blueprint)
    assert hermetic_env().validate_serialization(ir) is True


def test_validate_serialization_detects_instability(monkeypatch, data_blueprint):
    import engine.determinism.hermetic as hermetic

    ir = parse_document(data_blueprint)
    calls = {"n": 0}

    def _drifting(_ir):
        calls["n"] += 1
        return f'{{"payload":{calls["n"]}}}'

    # serialize drifts between calls; deserialize is neutralised so the round-trip
    # reaches the byte-stability comparison rather than failing to parse.
    monkeypatch.setattr(hermetic, "serialize", _drifting)
    monkeypatch.setattr(hermetic, "deserialize", lambda _text: ir)
    with pytest.raises(HermeticViolation):
        hermetic_env().validate_serialization(ir)


# -- evidence -----------------------------------------------------------------


def test_to_dict_and_fingerprint_are_stable():
    env = hermetic_env()
    assert env.to_dict()["toolchain"] == COMPILER_TOOLCHAIN
    assert env.fingerprint() == hermetic_env().fingerprint()
    assert len(env.fingerprint()) == 64
