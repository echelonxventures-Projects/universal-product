"""TASK-000028/000029/000030 — Pipeline Orchestrator integration & contract tests.

Exercises the EPIC-003 success criterion end to end: a BP-DATA blueprint executes

    Parse → Validate → Resolve → Compile → Package → Sign → Publish

through executable code, gated on certification and acyclicity, with every
failure surfaced as a Gap Report (IMP-007 §3/§17).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from engine.compiler.gap import Stage
from engine.compiler.pipeline import COMPILE_CONTRACT, CompilerPipeline
from engine.compiler.signing import Signer
from engine.foundation.contracts.contract import ContractRegistry, Version


@pytest.fixture
def pipeline(compiler_registry, tmp_path) -> CompilerPipeline:
    return CompilerPipeline(
        compiler_registry,
        signer=Signer(key=b"pipeline-integration-key"),
        output_dir=tmp_path / "out",
    )


# -- success criterion --------------------------------------------------------


def test_bp_data_full_pipeline_success(pipeline, data_blueprint, tmp_path):
    """The canonical BP-DATA success path (Parse→…→Publish)."""
    result = pipeline.compile_one(data_blueprint)
    assert result.success, result.gap_report
    assert result.gap_report is None
    published = result.published
    assert published is not None
    assert published.artifact_id.startswith("UCOS-CMP-BP-DATA-0001-")

    target = Path(published.output_dir)
    assert (target / "artifacts" / "schema" / "customer.sql").is_file()
    assert (target / "manifest.json").is_file()
    assert (target / "signature.json").is_file()
    assert (target / "sbom.json").is_file()
    assert (target / "artifact-record.json").is_file()
    # provenance preserved into the published record (Mandatory Rule 6)
    assert published.record["provenance"]["chain"][0] == "BP-DATA-0001"
    assert published.record["provenance"]["chain"][1] == "UCOS-DAT-000007"


def test_build_set_with_dependency_orders_and_publishes_both(
    pipeline, data_blueprint, dependency_blueprint
):
    data_blueprint["dependencies"] = ["BP-DATA-0002"]
    build = pipeline.compile([data_blueprint, dependency_blueprint])
    assert build.success, build.gap_report
    assert build.order.index("BP-DATA-0002") < build.order.index("BP-DATA-0001")
    assert build.result_for("BP-DATA-0001").success
    assert build.result_for("BP-DATA-0002").success
    assert build.result_for("BP-DATA-9999") is None


def test_pipeline_reproducible_artifact_identity(compiler_registry, data_blueprint, tmp_path):
    def run(sub: str) -> str:
        pipe = CompilerPipeline(
            compiler_registry,
            signer=Signer(key=b"repro-key"),
            output_dir=tmp_path / sub,
        )
        return pipe.compile_one(data_blueprint).published.artifact_id

    assert run("a") == run("b")


# -- failure conditions → Gap Report (IMP-007 §17) ----------------------------


def test_uncertified_input_halts_at_validate(pipeline, data_blueprint):
    data_blueprint["certification"] = {"status": "UNCERTIFIED", "evidence": ""}
    build = pipeline.compile([data_blueprint])
    assert not build.success
    assert build.gap_report.stage is Stage.VALIDATE
    assert build.gap_report.code == "CMP-CERT-001"
    assert build.gap_report.blueprint_id == "BP-DATA-0001"


def test_unregistered_provenance_halts_at_validate(pipeline, data_blueprint):
    data_blueprint["provenance"]["ontology_root"] = "UCOS-DAT-777777"
    build = pipeline.compile([data_blueprint])
    assert not build.success
    assert build.gap_report.stage is Stage.VALIDATE


def test_cyclic_dependencies_fail_the_build(pipeline, data_blueprint, dependency_blueprint):
    data_blueprint["dependencies"] = ["BP-DATA-0002"]
    dependency_blueprint["dependencies"] = ["BP-DATA-0001"]
    build = pipeline.compile([data_blueprint, dependency_blueprint])
    assert not build.success
    assert build.gap_report.stage is Stage.RESOLVE
    assert build.gap_report.code == "CMP-DEP-CYCLE-001"


def test_malformed_blueprint_halts_at_parse(pipeline, data_blueprint):
    del data_blueprint["entity"]
    build = pipeline.compile([data_blueprint])
    assert not build.success
    assert build.gap_report.stage is Stage.PARSE


def test_non_data_family_halts_at_parse(pipeline, data_blueprint):
    data_blueprint["blueprint_id"] = "BP-EVENT-000001"
    data_blueprint["family"] = "BP-EVENT"
    build = pipeline.compile([data_blueprint])
    assert not build.success
    assert build.gap_report.stage is Stage.PARSE


def test_empty_build_set_halts_at_parse(pipeline):
    build = pipeline.compile([])
    assert not build.success
    assert build.gap_report.stage is Stage.PARSE


def test_compile_one_returns_failure_result(pipeline, data_blueprint):
    data_blueprint["certification"] = {"status": "REVOKED", "evidence": ""}
    result = pipeline.compile_one(data_blueprint)
    assert not result.success
    assert result.gap_report is not None
    assert result.blueprint_id == "BP-DATA-0001"


# -- contract (AR-03 / PL-05) -------------------------------------------------


def test_pipeline_publishes_versioned_contract(pipeline):
    registry = ContractRegistry()
    pipeline.register_contract(registry)
    resolved = registry.get("compiler.compile")
    assert resolved is COMPILE_CONTRACT
    assert resolved.version == Version(1, 0, 0)
    assert pipeline.contract.name == "compiler.compile"


# -- downstream stage failures map to the right Gap Report stage --------------


class _Boom:
    """A stub whose single method raises the supplied compiler error."""

    def __init__(self, method: str, error: Exception) -> None:
        self._method = method
        self._error = error

    def __getattr__(self, name: str):
        def _raise(*_args, **_kwargs):
            raise self._error

        if name == self._method:
            return _raise
        raise AttributeError(name)


def test_compile_stage_failure_reports_compile(pipeline, data_blueprint):
    from engine.compiler.errors import CompilationError

    pipeline._compiler = _Boom("compile", CompilationError("boom", blueprint_id="BP-DATA-0001"))
    build = pipeline.compile([data_blueprint])
    assert not build.success
    assert build.gap_report.stage is Stage.COMPILE


def test_optimize_stage_failure_reports_optimize(pipeline, data_blueprint):
    from engine.compiler.errors import OptimizationError

    pipeline._optimizer = _Boom("optimize", OptimizationError("boom"))
    build = pipeline.compile([data_blueprint])
    assert not build.success
    assert build.gap_report.stage is Stage.OPTIMIZE


def test_package_stage_failure_reports_package(pipeline, data_blueprint):
    from engine.compiler.errors import PackagingError

    pipeline._packager = _Boom("package", PackagingError("boom"))
    build = pipeline.compile([data_blueprint])
    assert not build.success
    assert build.gap_report.stage is Stage.PACKAGE


def test_sign_stage_failure_reports_sign(pipeline, data_blueprint):
    from engine.compiler.errors import SigningError

    pipeline._signer = _Boom("sign", SigningError("boom"))
    build = pipeline.compile([data_blueprint])
    assert not build.success
    assert build.gap_report.stage is Stage.SIGN


def test_publish_stage_failure_reports_publish(pipeline, data_blueprint):
    from engine.compiler.errors import PublishingError

    pipeline._publisher = _Boom("publish", PublishingError("boom"))
    build = pipeline.compile([data_blueprint])
    assert not build.success
    assert build.gap_report.stage is Stage.PUBLISH


def test_partial_results_returned_when_second_blueprint_fails(
    pipeline, data_blueprint, dependency_blueprint
):
    # BP-DATA-0001 depends on 0002, so 0002 compiles first and succeeds; make the
    # compile stage fail only for BP-DATA-0001 to exercise the 'partial' halt path.
    from engine.compiler.data_compiler import DataBlueprintCompiler
    from engine.compiler.errors import CompilationError

    data_blueprint["dependencies"] = ["BP-DATA-0002"]
    real = DataBlueprintCompiler()

    class _SelectiveCompiler:
        def compile(self, ir):
            if ir.blueprint_id == "BP-DATA-0001":
                raise CompilationError("boom", blueprint_id=ir.blueprint_id)
            return real.compile(ir)

    pipeline._compiler = _SelectiveCompiler()
    build = pipeline.compile([data_blueprint, dependency_blueprint])
    assert not build.success
    assert build.gap_report.stage is Stage.COMPILE
    assert build.gap_report.blueprint_id == "BP-DATA-0001"
    # BP-DATA-0002 compiled before the failure and is present as a partial result.
    assert any(r.blueprint_id == "BP-DATA-0002" and r.success for r in build.results)


def test_compile_one_with_empty_source_reports_gap(pipeline):
    # compile_one over a malformed source produces a failure result carrying the
    # parse-stage Gap Report (build.results empty → fallback branch).
    result = pipeline.compile_one("{not json")
    assert not result.success
    assert result.gap_report is not None
    assert result.gap_report.stage is Stage.PARSE
