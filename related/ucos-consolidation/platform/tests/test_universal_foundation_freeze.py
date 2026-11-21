"""UCOS-UFC-001 — Foundation freeze readiness (UFC-11).

A freeze is a promise that what is frozen will not need to change, and this module refuses to
make that promise on anything but measurement. The verdict that carries the design is the third
one: ``UNMEASURED`` is *not* a pass. A freeze declared over criteria nobody measured is exactly
the failure a freeze exists to prevent, so absent evidence withholds readiness as firmly as a
failure does — while being reported differently, so an operator can tell "we checked and it is
broken" from "we never checked".

The engine also never freezes anything. It determines eligibility and stops. Every test below
therefore asserts about a *determination*, and the one test that runs a declared verification
command runs one of its own rather than the repository's.
"""

from __future__ import annotations

import json
from platform.universal_foundation.conformance import (
    CapabilityConformance,
    ConformanceDetermination,
    FoundationConformanceError,
    GateResult,
    Verdict,
    default_capability_register,
)
from platform.universal_foundation.constitution import foundation_constitution
from platform.universal_foundation.convergence import (
    ConvergenceDetermination,
    ModelConvergence,
    bootstrap_convergence,
)
from platform.universal_foundation.errors import FoundationFreezeError
from platform.universal_foundation.freeze import (
    DEFAULT_FREEZE_FILENAME,
    CriterionKind,
    CriterionResult,
    CriterionVerdict,
    FreezeCriteriaRegister,
    FreezeCriterion,
    FreezeDetermination,
    FreezeReadinessEngine,
    bootstrap_freeze_readiness,
    catalog_path,
    default_freeze_criteria,
    load_freeze_criteria,
)

import pytest

CAPABILITY = "UCOS-UNG-001"


def criterion(
    criterion_id: str = "FZ-TEST",
    kind: CriterionKind = CriterionKind.NO_FAULT,
    **overrides,
) -> FreezeCriterion:
    fields = {"criterion_id": criterion_id, "requirement": "a declared requirement", "kind": kind}
    fields.update(overrides)
    return FreezeCriterion(**fields)


def register(*criteria: FreezeCriterion, register_id: str = "test.freeze"):
    return FreezeCriteriaRegister(criteria or (criterion(),), register_id=register_id)


def engine(*criteria: FreezeCriterion, **kwargs) -> FreezeReadinessEngine:
    return FreezeReadinessEngine(register(*criteria), **kwargs)


@pytest.fixture(scope="module")
def declaration():
    return default_capability_register().require(CAPABILITY)


def conformance_of(declaration, *results: GateResult, platform=()) -> ConformanceDetermination:
    """A conformance determination carrying exactly the supplied results."""
    return ConformanceDetermination.create(
        foundation_constitution(),
        [CapabilityConformance.create(declaration, results)],
        platform,
    )


def gate(name: str, verdict: Verdict = Verdict.PASS, *, subject: str = CAPABILITY, **kwargs):
    return GateResult.create(name, "UFC-01", subject, verdict, **kwargs)


@pytest.fixture(scope="module")
def convergence():
    return bootstrap_convergence().measure()


# ---------------------------------------------------------------------------
# CriterionKind / CriterionVerdict
# ---------------------------------------------------------------------------


def test_only_ready_discharges_a_criterion():
    """Unmeasured withholds readiness as firmly as a failure."""
    assert CriterionVerdict.READY.discharged
    assert not CriterionVerdict.NOT_READY.discharged
    assert not CriterionVerdict.UNMEASURED.discharged


def test_a_declared_criterion_kind_coerces():
    assert CriterionKind.coerce("maturity") is CriterionKind.MATURITY
    assert CriterionKind.coerce(CriterionKind.COMMAND) is CriterionKind.COMMAND


def test_an_unknown_criterion_kind_is_refused():
    """A criterion whose evidence has no declared kind cannot discharge a freeze."""
    with pytest.raises(FoundationFreezeError) as exc:
        CriterionKind.coerce("vibes", subject="FZ-99")
    assert "FZ-99" in str(exc.value)


def test_a_non_string_criterion_kind_is_refused():
    with pytest.raises(FoundationFreezeError):
        CriterionKind.coerce(7)


# ---------------------------------------------------------------------------
# FreezeCriterion
# ---------------------------------------------------------------------------


def test_a_criterion_round_trips_through_its_projection():
    original = criterion("FZ-01", CriterionKind.GATES, gates=("FG-01-CONTRACT-PUBLISHED",))
    assert FreezeCriterion.from_document(original.to_dict()) == original
    assert FreezeCriterion.from_document(original.to_dict()).fingerprint() == original.fingerprint()


def test_a_criterion_declaration_that_is_not_a_mapping_is_refused():
    with pytest.raises(FoundationFreezeError) as exc:
        FreezeCriterion.from_document(["FZ-01"])
    assert "must be a mapping" in str(exc.value)


def test_a_criterion_declaration_missing_a_required_key_names_what_is_missing():
    with pytest.raises(FoundationFreezeError) as exc:
        FreezeCriterion.from_document({"criterion_id": "FZ-01"})
    message = str(exc.value)
    assert "requirement" in message and "kind" in message


def test_a_criterion_with_a_blank_identity_is_refused():
    with pytest.raises(FoundationFreezeError) as exc:
        FreezeCriterion.from_document(
            {"criterion_id": "  ", "requirement": "r", "kind": "no-fault"}
        )
    assert "must be non-empty" in str(exc.value)


@pytest.mark.parametrize(
    ("kind", "field"),
    (
        (CriterionKind.GATES, "gates"),
        (CriterionKind.PLATFORM_GATES, "gates"),
        (CriterionKind.MODELS_CONVERGED, "models"),
        (CriterionKind.COMMAND, "command"),
    ),
)
def test_a_criterion_whose_kind_cannot_be_measured_from_its_declaration_is_refused(kind, field):
    with pytest.raises(FoundationFreezeError) as exc:
        FreezeCriterion.from_document(
            {"criterion_id": "FZ-01", "requirement": "r", "kind": kind.value}
        )
    message = str(exc.value)
    assert f"declares no {field}" in message


@pytest.mark.parametrize("threshold", (0.0, -1.0))
def test_a_maturity_criterion_with_no_positive_threshold_is_refused(threshold):
    """A threshold of zero would be discharged by any measurement at all."""
    with pytest.raises(FoundationFreezeError) as exc:
        FreezeCriterion.from_document(
            {
                "criterion_id": "FZ-01",
                "requirement": "r",
                "kind": "maturity",
                "threshold": threshold,
            }
        )
    assert "no positive threshold" in str(exc.value)


# ---------------------------------------------------------------------------
# CriterionResult / FreezeDetermination
# ---------------------------------------------------------------------------


def result(
    verdict: CriterionVerdict = CriterionVerdict.READY,
    criterion_id: str = "FZ-01",
    **kwargs,
) -> CriterionResult:
    return CriterionResult.create(criterion(criterion_id), verdict, **kwargs)


def test_a_result_is_content_addressed_over_its_verdict_and_blockers():
    first = result(blockers=("b",))
    assert first.result_id == result(blockers=("b",)).result_id
    assert first.result_id != result(CriterionVerdict.NOT_READY, blockers=("b",)).result_id
    assert first.result_id.startswith("UCOS-UFCF-")


def test_result_blockers_are_deduplicated_and_ordered():
    built = result(blockers=("z", "a", "a"))
    assert built.blockers == ("a", "z")
    assert built.to_dict()["blockers"] == ["a", "z"]


def test_a_determination_over_no_criterion_is_not_ready():
    """Nothing measured is not readiness; there is no criterion that was discharged."""
    empty = FreezeDetermination.create([])
    assert not empty.ready
    assert empty.total == 0
    assert empty.determination == CriterionVerdict.UNMEASURED.value


def test_a_determination_whose_criteria_all_discharge_is_ready():
    built = FreezeDetermination.create([result(), result(criterion_id="FZ-02")])
    assert built.ready
    assert built.determination == "READY"
    assert built.blockers() == ()
    assert built.counts() == {"criteria": 2, "ready": 2, "not_ready": 0, "unmeasured": 0}


def test_a_measured_failure_reports_not_ready_rather_than_unmeasured():
    built = FreezeDetermination.create(
        [result(CriterionVerdict.NOT_READY), result(CriterionVerdict.UNMEASURED, "FZ-02")]
    )
    assert built.determination == "NOT-READY"
    assert [item.criterion_id for item in built.failing()] == ["FZ-01"]
    assert [item.criterion_id for item in built.unmeasured()] == ["FZ-02"]


def test_absent_evidence_alone_reports_unmeasured_so_the_two_are_never_confused():
    built = FreezeDetermination.create([result(CriterionVerdict.UNMEASURED)])
    assert built.determination == "UNMEASURED"
    assert not built.ready


def test_blockers_are_prefixed_by_the_criterion_that_raised_them():
    built = FreezeDetermination.create(
        [result(CriterionVerdict.NOT_READY, blockers=("a gate failed",))]
    )
    assert built.blockers() == ("FZ-01: a gate failed",)


def test_a_criterion_with_no_blocker_contributes_its_summary_instead():
    """A withheld criterion always says why, even when nothing itemised the reason."""
    built = FreezeDetermination.create(
        [result(CriterionVerdict.UNMEASURED, summary="no evidence was gathered")]
    )
    assert built.blockers() == ("FZ-01: no evidence was gathered",)


def test_the_full_projection_carries_the_per_blocker_detail_the_summary_drops():
    built = FreezeDetermination.create(
        [result(CriterionVerdict.NOT_READY, blockers=("x",))],
        conformance_id="C-1",
        convergence_id="V-1",
        maturity_percentage=88.5,
    )
    full = built.to_dict()
    compact = built.summary()
    assert full["conformance_id"] == "C-1"
    assert "blockers" in full["results"][0]
    assert "blockers" not in compact["results"][0]
    assert full["determination_id"] == compact["determination_id"]
    assert compact["maturity_percentage"] == 88.5
    assert (
        built.fingerprint()
        == FreezeDetermination.create(
            [result(CriterionVerdict.NOT_READY, blockers=("x",))],
            conformance_id="C-1",
            convergence_id="V-1",
            maturity_percentage=88.5,
        ).fingerprint()
    )


# ---------------------------------------------------------------------------
# FreezeCriteriaRegister
# ---------------------------------------------------------------------------


def test_only_a_freeze_criterion_may_be_declared():
    with pytest.raises(FoundationFreezeError) as exc:
        FreezeCriteriaRegister().add({"criterion_id": "FZ-01"})
    assert "only FreezeCriterion" in str(exc.value)


def test_declaring_the_same_criterion_twice_identically_is_idempotent():
    built = register(criterion("FZ-01"))
    assert built.add(criterion("FZ-01")).criterion_id == "FZ-01"
    assert built.count == 1


def test_a_criterion_redeclared_with_a_different_body_is_refused():
    built = register(criterion("FZ-01", requirement="one"))
    with pytest.raises(FoundationFreezeError) as exc:
        built.add(criterion("FZ-01", requirement="another"))
    assert "different body" in str(exc.value)


def test_get_reports_an_undeclared_criterion_as_absent():
    assert FreezeCriteriaRegister().get("FZ-99") is None


def test_require_returns_a_declared_criterion_and_refuses_an_undeclared_one():
    built = register(criterion("FZ-01"))
    assert built.require("FZ-01").criterion_id == "FZ-01"
    with pytest.raises(FoundationFreezeError) as exc:
        built.require("FZ-99")
    assert "unknown freeze criterion" in str(exc.value)


def test_criteria_are_ordered_by_identity_never_by_insertion():
    built = register(criterion("FZ-09"), criterion("FZ-01"))
    assert built.ids() == ("FZ-01", "FZ-09")
    assert [item.criterion_id for item in built.ordered()] == ["FZ-01", "FZ-09"]
    assert built.register_id == "test.freeze"


def test_a_register_with_a_blank_identity_falls_back_to_the_declared_default():
    assert FreezeCriteriaRegister(register_id="   ").register_id == "foundation.freeze"


def test_a_freeze_document_that_is_not_a_mapping_is_refused():
    with pytest.raises(FoundationFreezeError) as exc:
        FreezeCriteriaRegister.from_document([])
    assert "must be a mapping" in str(exc.value)


@pytest.mark.parametrize("criteria", (None, "FZ-01", 7))
def test_a_freeze_document_without_a_criteria_sequence_is_refused(criteria):
    with pytest.raises(FoundationFreezeError) as exc:
        FreezeCriteriaRegister.from_document({"criteria": criteria})
    assert "'criteria' sequence" in str(exc.value)


def test_a_freeze_document_declaring_no_criterion_is_refused():
    """An empty freeze register would declare the Foundation frozen by requiring nothing."""
    with pytest.raises(FoundationFreezeError) as exc:
        FreezeCriteriaRegister.from_document({"criteria": []})
    assert "declares no criterion" in str(exc.value)


def test_a_register_round_trips_through_its_projection():
    original = register(criterion("FZ-01"), criterion("FZ-02"))
    rebuilt = FreezeCriteriaRegister.from_document(original.to_dict())
    assert rebuilt.to_dict() == original.to_dict()
    assert rebuilt.fingerprint() == original.fingerprint()
    assert original.to_dict()["criterion_count"] == 2


# ---------------------------------------------------------------------------
# loading the declared criteria
# ---------------------------------------------------------------------------


def test_the_packaged_catalogue_declares_the_freeze_criteria():
    built = default_freeze_criteria()
    assert catalog_path().name == DEFAULT_FREEZE_FILENAME
    assert built.count > 0
    assert all(isinstance(item.kind, CriterionKind) for item in built.ordered())


def test_a_register_loaded_from_a_document_matches_one_built_in_memory(tmp_path):
    path = tmp_path / "freeze.json"
    original = register(criterion("FZ-01"))
    path.write_text(json.dumps(original.to_dict()), encoding="utf-8")
    assert load_freeze_criteria(path).to_dict() == original.to_dict()


def test_an_absent_freeze_document_is_a_refusal_naming_the_path(tmp_path):
    missing = tmp_path / "absent.json"
    with pytest.raises(FoundationFreezeError) as exc:
        load_freeze_criteria(missing)
    assert str(missing) in str(exc.value)


def test_a_malformed_freeze_document_is_a_refusal(tmp_path):
    path = tmp_path / "freeze.json"
    path.write_text("{ not json", encoding="utf-8")
    with pytest.raises(FoundationFreezeError):
        load_freeze_criteria(path)


# ---------------------------------------------------------------------------
# the engine's composition
# ---------------------------------------------------------------------------


def test_the_engine_requires_a_declared_register():
    with pytest.raises(FoundationFreezeError) as exc:
        FreezeReadinessEngine([criterion()])
    assert "FreezeCriteriaRegister" in str(exc.value)


def test_the_engine_exposes_what_it_was_composed_from():
    built = engine()
    assert built.register.count == 1
    assert built.runs_commands is False
    assert built.to_dict() == {"register": built.register.to_dict(), "runs_commands": False}
    assert built.fingerprint() == engine().fingerprint()


def test_running_commands_is_opt_in_and_visible_in_the_composition():
    assert engine(run_commands=True).runs_commands is True
    assert engine(run_commands=True).fingerprint() != engine().fingerprint()


# ---------------------------------------------------------------------------
# measurement — absent evidence
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "kind",
    (
        CriterionKind.NO_FAULT,
        CriterionKind.MATURITY,
        CriterionKind.DEPENDENCY_ORDER,
    ),
)
def test_a_criterion_needing_conformance_is_unmeasured_without_it(kind):
    built = criterion("FZ-01", kind, threshold=90.0 if kind is CriterionKind.MATURITY else 0.0)
    determination = engine(built).measure()
    assert determination.results[0].verdict is CriterionVerdict.UNMEASURED
    assert "no conformance determination" in determination.results[0].summary


@pytest.mark.parametrize(
    ("kind", "extra"),
    (
        (CriterionKind.NO_DUPLICATES, {}),
        (CriterionKind.MODELS_CONVERGED, {"models": ("MODEL-TRUTH",)}),
    ),
)
def test_a_criterion_needing_convergence_is_unmeasured_without_it(kind, extra):
    determination = engine(criterion("FZ-01", kind, **extra)).measure()
    assert determination.results[0].verdict is CriterionVerdict.UNMEASURED
    assert "no convergence determination" in determination.results[0].summary


# ---------------------------------------------------------------------------
# measurement — gates
# ---------------------------------------------------------------------------


def test_a_gate_criterion_is_discharged_when_every_named_gate_passed(declaration):
    built = criterion("FZ-01", CriterionKind.GATES, gates=("FG-01-CONTRACT-PUBLISHED",))
    conformance = conformance_of(declaration, gate("FG-01-CONTRACT-PUBLISHED"))
    outcome = engine(built).measure(conformance=conformance).results[0]
    assert outcome.verdict is CriterionVerdict.READY
    assert "1 gate results discharge" in outcome.summary


def test_a_failing_gate_withholds_the_criterion_and_names_the_capability(declaration):
    built = criterion("FZ-01", CriterionKind.GATES, gates=("FG-01-CONTRACT-PUBLISHED",))
    conformance = conformance_of(
        declaration,
        gate("FG-01-CONTRACT-PUBLISHED", Verdict.FAIL, summary="the surface is not published"),
    )
    outcome = engine(built).measure(conformance=conformance).results[0]
    assert outcome.verdict is CriterionVerdict.NOT_READY
    assert CAPABILITY in outcome.blockers[0]
    assert "not published" in outcome.blockers[0]


def test_a_gate_nobody_measured_leaves_the_criterion_unmeasured(declaration):
    """Not measured is not passed, and the blocker says which gate went unmeasured."""
    built = criterion("FZ-01", CriterionKind.GATES, gates=("FG-99-INVENTED",))
    conformance = conformance_of(declaration, gate("FG-01-CONTRACT-PUBLISHED"))
    outcome = engine(built).measure(conformance=conformance).results[0]
    assert outcome.verdict is CriterionVerdict.UNMEASURED
    assert "FG-99-INVENTED" in outcome.blockers[0]
    assert "was not measured" in outcome.blockers[0]


def test_a_platform_gate_criterion_reads_the_platform_scoped_results(declaration):
    built = criterion("FZ-01", CriterionKind.PLATFORM_GATES, gates=("FG-14-EXACTLY-ONCE",))
    conformance = conformance_of(
        declaration, platform=(gate("FG-14-EXACTLY-ONCE", subject="PLATFORM"),)
    )
    outcome = engine(built).measure(conformance=conformance).results[0]
    assert outcome.verdict is CriterionVerdict.READY


def test_a_failing_platform_gate_reports_each_finding_it_carried(declaration):
    built = criterion("FZ-01", CriterionKind.PLATFORM_GATES, gates=("FG-14-EXACTLY-ONCE",))
    conformance = conformance_of(
        declaration,
        platform=(
            gate(
                "FG-14-EXACTLY-ONCE",
                Verdict.FAIL,
                subject="PLATFORM",
                findings=("a second answer exists",),
            ),
        ),
    )
    outcome = engine(built).measure(conformance=conformance).results[0]
    assert outcome.verdict is CriterionVerdict.NOT_READY
    assert outcome.blockers == ("PLATFORM/FG-14-EXACTLY-ONCE: a second answer exists",)


def test_a_failing_platform_gate_with_no_finding_reports_its_summary(declaration):
    built = criterion("FZ-01", CriterionKind.PLATFORM_GATES, gates=("FG-14-EXACTLY-ONCE",))
    conformance = conformance_of(
        declaration,
        platform=(
            gate("FG-14-EXACTLY-ONCE", Verdict.FAIL, subject="PLATFORM", summary="withheld"),
        ),
    )
    outcome = engine(built).measure(conformance=conformance).results[0]
    assert outcome.blockers == ("PLATFORM/FG-14-EXACTLY-ONCE: withheld",)


def test_an_unmeasured_platform_gate_leaves_the_criterion_unmeasured(declaration):
    built = criterion("FZ-01", CriterionKind.PLATFORM_GATES, gates=("FG-99-INVENTED",))
    outcome = engine(built).measure(conformance=conformance_of(declaration)).results[0]
    assert outcome.verdict is CriterionVerdict.UNMEASURED
    assert "was not measured over the platform" in outcome.blockers[0]


# ---------------------------------------------------------------------------
# measurement — the remaining kinds
# ---------------------------------------------------------------------------


def test_no_fault_is_discharged_when_every_probe_reached_a_verdict(declaration):
    conformance = conformance_of(declaration, gate("FG-01-CONTRACT-PUBLISHED", Verdict.FAIL))
    outcome = (
        engine(criterion("FZ-01", CriterionKind.NO_FAULT))
        .measure(conformance=conformance)
        .results[0]
    )
    assert outcome.verdict is CriterionVerdict.READY
    assert "no architecture is unresolved" in outcome.summary


def test_a_faulted_probe_withholds_no_fault_because_the_architecture_is_unresolved(declaration):
    conformance = conformance_of(
        declaration, gate("FG-01-CONTRACT-PUBLISHED", Verdict.FAULT, summary="could not execute")
    )
    outcome = (
        engine(criterion("FZ-01", CriterionKind.NO_FAULT))
        .measure(conformance=conformance)
        .results[0]
    )
    assert outcome.verdict is CriterionVerdict.NOT_READY
    assert "could not execute" in outcome.blockers[0]


def test_maturity_is_measured_against_the_declared_threshold(declaration):
    passing = [gate(article.gate) for article in foundation_constitution().capability_articles()]
    conformance = conformance_of(declaration, *passing)
    built = criterion("FZ-01", CriterionKind.MATURITY, threshold=100.0)
    outcome = engine(built).measure(conformance=conformance).results[0]
    assert outcome.verdict is CriterionVerdict.READY
    assert "100.0%" in outcome.summary


def test_a_capability_below_the_threshold_is_named_as_the_blocker(declaration):
    conformance = conformance_of(declaration)  # nothing measured, so no axis is reached
    built = criterion("FZ-01", CriterionKind.MATURITY, threshold=100.0)
    outcome = engine(built).measure(conformance=conformance).results[0]
    assert outcome.verdict is CriterionVerdict.NOT_READY
    assert any(CAPABILITY in blocker for blocker in outcome.blockers)


def test_the_dependency_order_criterion_is_discharged_when_the_order_resolves(declaration):
    outcome = (
        engine(criterion("FZ-01", CriterionKind.DEPENDENCY_ORDER))
        .measure(conformance=conformance_of(declaration))
        .results[0]
    )
    assert outcome.verdict is CriterionVerdict.READY
    assert "no cycle" in outcome.summary


def test_no_duplicates_reads_the_convergence_determination(declaration, convergence):
    outcome = (
        engine(criterion("FZ-01", CriterionKind.NO_DUPLICATES))
        .measure(conformance=conformance_of(declaration), convergence=convergence)
        .results[0]
    )
    expected = CriterionVerdict.READY if convergence.duplicates == 0 else CriterionVerdict.NOT_READY
    assert outcome.verdict is expected
    assert str(convergence.total) in outcome.summary


def test_models_converged_is_discharged_when_every_named_model_has_one_answer(
    declaration, convergence
):
    model_id = convergence.models[0].model_id
    built = criterion("FZ-01", CriterionKind.MODELS_CONVERGED, models=(model_id,))
    outcome = (
        engine(built)
        .measure(conformance=conformance_of(declaration), convergence=convergence)
        .results[0]
    )
    assert outcome.verdict is CriterionVerdict.READY
    assert model_id not in "".join(outcome.blockers)


def test_a_model_the_convergence_register_never_declared_is_a_blocker(declaration, convergence):
    """An undeclared model is not silently converged; it is a named blocker."""
    built = criterion("FZ-01", CriterionKind.MODELS_CONVERGED, models=("MODEL-INVENTED",))
    outcome = (
        engine(built)
        .measure(conformance=conformance_of(declaration), convergence=convergence)
        .results[0]
    )
    assert outcome.verdict is CriterionVerdict.NOT_READY
    assert "MODEL-INVENTED: not declared" in outcome.blockers[0]


def test_a_model_with_a_second_live_answer_withholds_the_criterion(declaration):
    """A competing surface is what this criterion exists to catch, so it is measured directly."""
    unconverged = ModelConvergence(
        model_id="MODEL-SPLIT",
        name="A split model",
        canonical_package="platform.somewhere",
        owner_resolved=True,
        contract_count=1,
        findings=(),
        measurement_stable=False,
        detail="two surfaces answer this question",
    )
    assert not unconverged.converged
    determination = ConvergenceDetermination.create([unconverged], [])
    built = criterion("FZ-01", CriterionKind.MODELS_CONVERGED, models=("MODEL-SPLIT",))
    outcome = (
        engine(built)
        .measure(conformance=conformance_of(declaration), convergence=determination)
        .results[0]
    )
    assert outcome.verdict is CriterionVerdict.NOT_READY
    assert "MODEL-SPLIT: 1 live implementations" in outcome.blockers[0]
    assert "two surfaces answer this question" in outcome.blockers[0]
    assert "1 named models are not converged" in outcome.summary


def test_a_dependency_order_that_cannot_be_read_is_contained_as_a_refusal(declaration, monkeypatch):
    """Fail-closed: an unreadable register withholds the freeze rather than crashing it.

    The criterion resolves the register through ``default_capability_register``, so the seam is
    patched rather than the packaged catalogue corrupted — a cyclic or unreadable register is a
    real failure mode, and mutating frozen repository data to stage it would not be.
    """
    from platform.universal_foundation import conformance as conformance_module

    def _refuses():
        raise FoundationConformanceError("capability dependency graph contains a cycle")

    monkeypatch.setattr(conformance_module, "default_capability_register", _refuses)
    outcome = (
        engine(criterion("FZ-01", CriterionKind.DEPENDENCY_ORDER))
        .measure(conformance=conformance_of(declaration))
        .results[0]
    )
    assert outcome.verdict is CriterionVerdict.NOT_READY
    assert "does not resolve" in outcome.summary
    assert "contains a cycle" in outcome.blockers[0]


# ---------------------------------------------------------------------------
# measurement — declared verification commands
# ---------------------------------------------------------------------------


def test_a_declared_command_is_unmeasured_until_it_is_actually_run():
    """Without --with-suites the criterion is withheld, never assumed to have passed."""
    built = criterion("FZ-01", CriterionKind.COMMAND, command="true")
    outcome = engine(built).measure().results[0]
    assert outcome.verdict is CriterionVerdict.UNMEASURED
    assert outcome.blockers == ("true",)
    assert "was not executed in this run" in outcome.summary


def test_a_declared_command_that_exits_zero_discharges_its_criterion(tmp_path):
    built = criterion("FZ-01", CriterionKind.COMMAND, command="true")
    outcome = engine(built, run_commands=True, project_root=tmp_path).measure().results[0]
    assert outcome.verdict is CriterionVerdict.READY
    assert "exited 0" in outcome.summary


def test_a_declared_command_that_fails_withholds_readiness_and_reports_its_tail(tmp_path):
    built = criterion(
        "FZ-01",
        CriterionKind.COMMAND,
        command="sh -c 'echo first; echo the-failing-line; exit 3'",
    )
    outcome = engine(built, run_commands=True, project_root=tmp_path).measure().results[0]
    assert outcome.verdict is CriterionVerdict.NOT_READY
    assert "exited 3" in outcome.summary
    assert "the-failing-line" in outcome.blockers


def test_a_declared_command_that_cannot_be_executed_withholds_readiness(tmp_path):
    built = criterion("FZ-01", CriterionKind.COMMAND, command="a-command-that-does-not-exist --now")
    outcome = engine(built, run_commands=True, project_root=tmp_path).measure().results[0]
    assert outcome.verdict is CriterionVerdict.NOT_READY
    assert "could not be executed" in outcome.summary


def test_a_command_that_exceeds_its_timeout_withholds_readiness(tmp_path):
    """A hung suite is not a passing suite."""
    built = criterion("FZ-01", CriterionKind.COMMAND, command="sleep 5")
    outcome = (
        engine(built, run_commands=True, project_root=tmp_path, timeout=1).measure().results[0]
    )
    assert outcome.verdict is CriterionVerdict.NOT_READY
    assert "could not be executed" in outcome.summary


def test_a_failing_command_that_printed_nothing_still_names_what_failed(tmp_path):
    built = criterion("FZ-01", CriterionKind.COMMAND, command="false")
    outcome = engine(built, run_commands=True, project_root=tmp_path).measure().results[0]
    assert outcome.verdict is CriterionVerdict.NOT_READY
    assert outcome.blockers == ("false",)


# ---------------------------------------------------------------------------
# the whole determination
# ---------------------------------------------------------------------------


def test_measuring_covers_every_declared_criterion_in_identity_order(declaration):
    built = engine(
        criterion("FZ-02", CriterionKind.NO_FAULT),
        criterion("FZ-01", CriterionKind.DEPENDENCY_ORDER),
    )
    determination = built.measure(conformance=conformance_of(declaration))
    assert [item.criterion_id for item in determination.results] == ["FZ-01", "FZ-02"]
    assert determination.conformance_id


def test_the_repository_withholds_its_own_freeze_until_the_suites_are_run():
    """The repository's real reading, asserted as one rather than assumed."""
    determination = bootstrap_freeze_readiness().measure()
    assert not determination.ready
    assert determination.unmeasured()
    assert determination.determination in ("UNMEASURED", "NOT-READY")


# ---------------------------------------------------------------------------
# bootstrap
# ---------------------------------------------------------------------------


def test_bootstrapping_with_nothing_composes_the_packaged_declaration():
    assert bootstrap_freeze_readiness().register.to_dict() == default_freeze_criteria().to_dict()


def test_bootstrapping_accepts_an_already_built_register():
    built = register(criterion("FZ-01"))
    assert bootstrap_freeze_readiness(built).register is built


def test_bootstrapping_accepts_a_path_to_a_declared_document(tmp_path):
    path = tmp_path / "freeze.json"
    path.write_text(json.dumps(register(criterion("FZ-01")).to_dict()), encoding="utf-8")
    assert bootstrap_freeze_readiness(path, run_commands=True).register.ids() == ("FZ-01",)
