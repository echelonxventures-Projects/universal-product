"""Tests — Universal Measurement Policy Framework (UCOS-UMPF-001)."""

from __future__ import annotations

from platform.foundation.services import ServiceRegistry
from platform.measurement.contracts import MeasurementKind
from platform.universal_assimilation import (
    KIND_MARKDOWN,
    AssimilationPipeline,
    AssimilationReport,
    SourceInput,
    bootstrap_assimilation,
    default_adapter_registry,
)
from platform.universal_measurement import (
    POLICY_CONTRACTS,
    AssimilationCoveragePolicy,
    ContestedOwnershipPolicy,
    EvidenceOnlySourcePolicy,
    FoundationCompletenessPolicy,
    MeasurementContext,
    MeasurementPolicy,
    MeasurementPolicyDescriptor,
    MeasurementPolicyRegistry,
    OwnershipCoveragePolicy,
    PolicyMeasurementEngine,
    PolicyOutcome,
    PolicySuite,
    RemediableOwnershipPolicy,
    TruthClassificationCoveragePolicy,
    UnadaptedSourcePolicy,
    UnresolvedOwnershipPolicy,
    bootstrap_measurement_policies,
    build_policy_engine,
    default_measurement_policies,
    default_policy_registry,
    policy_contract_names,
    register_measurement_policies,
)
from platform.universal_measurement.cli import main as cli_main
from platform.universal_measurement.errors import (
    MeasurementContextError,
    MeasurementPolicyContractError,
    MeasurementPolicyError,
    MeasurementPolicyEvaluationError,
    MeasurementPolicyRegistryError,
)
from platform.universal_measurement.policies import policies_from_document
from platform.universal_ownership import (
    DefinitionalLocatorProvider,
    EvidenceProviderRegistry,
    OwnershipDetermination,
    OwnershipDeterminationEngine,
)
from platform.universal_truth import Subject, default_truth_policy

import pytest

HOME = "02-MASTER/UCOS-COMP-000000-CONSTITUTION.md"
EVIDENCE_ONLY = "00-SOURCE/VISION/UCOS-COMP-000001.docx"


def _ownership() -> OwnershipDetermination:
    policy = default_truth_policy()
    engine = OwnershipDeterminationEngine(
        EvidenceProviderRegistry([DefinitionalLocatorProvider(policy)]), policy=policy
    )
    return engine.determine(
        [
            Subject.create("UCOS-COMP-000000", locators=[HOME]),
            Subject.create("UCOS-COMP-000001", locators=[EVIDENCE_ONLY]),
        ]
    )


def _assimilation(*, closed: bool = False) -> AssimilationReport:
    pipeline = bootstrap_assimilation()
    destinations = {"00-SOURCE/a.md": "02-MASTER/a.md"}
    sources = [SourceInput.from_text(KIND_MARKDOWN, "00-SOURCE/a.md", "# H\nbody")]
    if not closed:
        sources.append(SourceInput.from_text(KIND_MARKDOWN, "00-SOURCE/b.md", "# H\nbody"))
        sources.append(SourceInput.from_text("unadapted", "00-SOURCE/c.zzz", "body"))
    return pipeline.assimilate(sources, destinations=destinations)


def _context(**kwargs: object) -> MeasurementContext:
    return MeasurementContext.create(**kwargs)  # type: ignore[arg-type]


# --------------------------------------------------------------------------- context


def test_context_composition_and_fail_closed_requirements() -> None:
    policy = default_truth_policy()
    partition = policy.classify_all([HOME, EVIDENCE_ONLY])
    context = _context(
        partition=partition,
        ownership=_ownership(),
        assimilation=_assimilation(),
        subjects=[Subject.create("A")],
        facts={"declared": 1},
    )
    assert context.context_id.startswith("UCOS-UMPX-")
    assert context.available() == (
        "partition",
        "ownership",
        "assimilation",
        "subjects",
        "facts",
    )
    assert context.fact("declared") == 1.0
    assert context.require_partition("p") is partition
    assert context.require_ownership("p") is not None
    assert context.require_assimilation("p") is not None
    assert context.to_dict()["subject_count"] == 1
    assert context.fingerprint()

    empty = _context()
    assert empty.available() == ()
    for accessor in ("require_partition", "require_ownership", "require_assimilation"):
        with pytest.raises(MeasurementContextError):
            getattr(empty, accessor)("p")
    with pytest.raises(MeasurementContextError):
        empty.fact("missing")


def test_context_type_guards() -> None:
    with pytest.raises(MeasurementPolicyContractError):
        _context(partition="nope")
    with pytest.raises(MeasurementPolicyContractError):
        _context(ownership="nope")
    with pytest.raises(MeasurementPolicyContractError):
        _context(assimilation="nope")


# --------------------------------------------------------------------------- outcomes


def _descriptor(**kwargs: object) -> MeasurementPolicyDescriptor:
    options: dict[str, object] = {
        "policy_id": "p",
        "subject": "s",
        "kind": MeasurementKind.GAP,
    }
    options.update(kwargs)
    return MeasurementPolicyDescriptor(**options)  # type: ignore[arg-type]


def test_descriptor_guards_and_ordering() -> None:
    with pytest.raises(MeasurementPolicyContractError):
        _descriptor(policy_id=" ")
    with pytest.raises(MeasurementPolicyContractError):
        _descriptor(subject=" ")
    with pytest.raises(MeasurementPolicyContractError):
        _descriptor(kind="gap")
    with pytest.raises(MeasurementPolicyContractError):
        _descriptor(precedence="high")
    descriptor = _descriptor(precedence=500)
    assert descriptor.order_key == (-500, "p")
    assert descriptor.to_dict()["blocking"] is False
    assert descriptor.fingerprint()


def test_outcome_projection_and_finding_retention() -> None:
    descriptor = _descriptor(blocking=True)
    outcome = PolicyOutcome.create(
        descriptor,
        value=2,
        population=10,
        satisfied=False,
        summary="two gaps",
        findings=[f"S{index:04d}" for index in range(600)] + ["", "  "],
    )
    assert outcome.finding_total == 600
    assert len(outcome.findings) == 500
    assert outcome.blocks is True
    assert outcome.outcome_id.startswith("UCOS-UMPO-")
    assert outcome.fingerprint()
    measurement = outcome.as_measurement()
    assert measurement.kind is MeasurementKind.GAP
    assert measurement.subject == "s"
    with pytest.raises(MeasurementPolicyContractError):
        PolicyOutcome.create("nope", value=0, population=0, satisfied=True)  # type: ignore[arg-type]


def test_suite_views_and_determination() -> None:
    blocking = PolicyOutcome.create(
        _descriptor(policy_id="a", blocking=True), value=1, population=1, satisfied=False
    )
    passing = PolicyOutcome.create(
        _descriptor(policy_id="b", blocking=True), value=0, population=1, satisfied=True
    )
    advisory = PolicyOutcome.create(
        _descriptor(policy_id="c"), value=5, population=1, satisfied=False
    )
    suite = PolicySuite.create([advisory, blocking, passing], context_id="ctx")
    assert [outcome.policy_id for outcome in suite.outcomes] == ["a", "b", "c"]
    assert suite.total == 3
    assert len(suite.blocking) == 2
    assert [outcome.policy_id for outcome in suite.blockers] == ["a"]
    assert suite.closed is False
    assert suite.completeness == 50.0
    assert suite.values()["c"] == 5.0
    assert suite.outcome("a") is blocking
    assert len(suite.as_measurements()) == 3
    assert suite.to_dict()["determination"] == "NOT-CLOSED"
    assert suite.suite_id.startswith("UCOS-UMPS-")
    assert suite.fingerprint()
    with pytest.raises(MeasurementPolicyContractError):
        suite.outcome("missing")
    with pytest.raises(MeasurementPolicyContractError):
        PolicySuite.create([blocking, blocking])
    assert PolicySuite.create([]).closed is False
    assert PolicySuite.create([]).completeness == 0.0
    assert PolicySuite.create([passing]).closed is True


# --------------------------------------------------------------------------- policies


def test_truth_classification_coverage_policy() -> None:
    policy = default_truth_policy()
    outcome = TruthClassificationCoveragePolicy().apply(
        _context(partition=policy.classify_all([HOME, "nowhere/x.md"]))
    )
    assert outcome.value == 50.0
    assert outcome.satisfied is False
    assert outcome.findings == ("nowhere/x.md",)
    complete = TruthClassificationCoveragePolicy().apply(
        _context(partition=policy.classify_all([HOME]))
    )
    assert complete.satisfied is True
    assert complete.value == 100.0


def test_ownership_policies_measure_declared_evidence_only() -> None:
    context = _context(ownership=_ownership())
    coverage = OwnershipCoveragePolicy().apply(context)
    assert coverage.value == 50.0
    assert coverage.satisfied is False
    assert coverage.findings == ("UCOS-COMP-000001",)

    unresolved = UnresolvedOwnershipPolicy().apply(context)
    assert unresolved.value == 1.0
    assert unresolved.kind is MeasurementKind.GAP
    assert unresolved.findings[0].startswith("UCOS-COMP-000001:")

    contested = ContestedOwnershipPolicy().apply(context)
    assert contested.value == 0.0
    assert contested.satisfied is True

    remediable = RemediableOwnershipPolicy().apply(context)
    assert remediable.value == 1.0
    assert remediable.kind is MeasurementKind.GAP
    assert remediable.blocking is False
    assert remediable.satisfied is False
    assert remediable.findings == ("UCOS-COMP-000001:ZONE-NOT-CANONICAL-HOME-ELIGIBLE",)
    assert "1 of 1 undeclared subjects name a remediable deficit" in remediable.summary
    assert "0 carry no diagnosed deficit" in remediable.summary


def test_the_remediable_policy_partitions_the_residue_and_never_reblocks_it() -> None:
    """UFC-16: a second quantity over one population, never a second number for one quantity."""
    registry = default_policy_registry()
    unresolved = registry.require("ownership.unresolved").descriptor()
    remediable = registry.require("ownership.remediable").descriptor()
    assert unresolved.subject == remediable.subject
    assert unresolved.blocking is True
    assert remediable.blocking is False
    assert remediable.precedence < unresolved.precedence
    context = _context(ownership=_ownership())
    assert (
        RemediableOwnershipPolicy().apply(context).value
        <= UnresolvedOwnershipPolicy().apply(context).value
    )


def test_an_undiagnosed_residue_is_reported_as_such() -> None:
    """A subject with no locator at all can name no deficit; the policy must say so."""
    policy = default_truth_policy()
    engine = OwnershipDeterminationEngine(
        EvidenceProviderRegistry([DefinitionalLocatorProvider(policy)]), policy=policy
    )
    determination = engine.determine([Subject.create("NOWHERE-001")])
    outcome = RemediableOwnershipPolicy().apply(_context(ownership=determination))
    assert outcome.value == 0.0
    assert outcome.satisfied is True
    assert "1 carry no diagnosed deficit" in outcome.summary


def test_assimilation_policies_measure_the_generalised_upload_only_class() -> None:
    context = _context(assimilation=_assimilation())
    coverage = AssimilationCoveragePolicy().apply(context)
    assert coverage.satisfied is False

    evidence_only = EvidenceOnlySourcePolicy().apply(context)
    assert evidence_only.value == 1.0
    assert evidence_only.findings == ("00-SOURCE/b.md",)
    assert evidence_only.population == 3

    unadapted = UnadaptedSourcePolicy().apply(context)
    assert unadapted.value == 1.0
    assert unadapted.findings == ("unadapted:00-SOURCE/c.zzz",)

    closed = _context(assimilation=_assimilation(closed=True))
    assert AssimilationCoveragePolicy().apply(closed).satisfied is True
    assert EvidenceOnlySourcePolicy().apply(closed).satisfied is True
    assert UnadaptedSourcePolicy().apply(closed).satisfied is True


def test_completeness_policy_conjoins_supplied_determinations() -> None:
    policy = default_truth_policy()
    outcome = FoundationCompletenessPolicy().apply(
        _context(
            partition=policy.classify_all([HOME]),
            ownership=_ownership(),
            assimilation=_assimilation(),
        )
    )
    assert outcome.population == 3
    assert outcome.satisfied is False
    assert set(outcome.findings) == {"ownership.closed", "assimilation.closed"}
    with pytest.raises(MeasurementContextError):
        FoundationCompletenessPolicy().apply(_context())


def test_policy_protocol_enforcement() -> None:
    class Broken(MeasurementPolicy):
        def descriptor(self) -> MeasurementPolicyDescriptor:
            return _descriptor(policy_id="broken")

        def evaluate(self, context: MeasurementContext) -> PolicyOutcome:
            raise ZeroDivisionError("boom")

    class WrongType(Broken):
        def evaluate(self, context: MeasurementContext) -> PolicyOutcome:
            return "nope"  # type: ignore[return-value]

    class WrongProvenance(Broken):
        def evaluate(self, context: MeasurementContext) -> PolicyOutcome:
            return PolicyOutcome.create(
                _descriptor(policy_id="other"), value=0, population=0, satisfied=True
            )

    for policy in (Broken(), WrongType(), WrongProvenance()):
        with pytest.raises(MeasurementPolicyEvaluationError):
            policy.apply(_context())
    with pytest.raises(MeasurementPolicyContractError):
        Broken().apply("nope")  # type: ignore[arg-type]


# --------------------------------------------------------------------------- registry


def test_registry_registration_discipline() -> None:
    registry = default_policy_registry()
    assert registry.count == 9
    assert len(registry.blocking()) == 8
    first = registry.ordered()[0]
    assert first.descriptor().policy_id == "truth.classification.coverage"
    assert registry.register(first) is first
    assert registry.require("ownership.coverage") is registry.get("ownership.coverage")
    assert registry.ids()[0] == "assimilation.coverage"
    assert len(registry.of_kind(MeasurementKind.GAP)) == 5
    assert registry.to_dict()["policy_count"] == 9
    assert registry.fingerprint()
    with pytest.raises(MeasurementPolicyRegistryError):
        registry.register(OwnershipCoveragePolicy())
    with pytest.raises(MeasurementPolicyRegistryError):
        registry.register("nope")  # type: ignore[arg-type]
    with pytest.raises(MeasurementPolicyRegistryError):
        registry.require("missing")
    registry.deregister("ownership.coverage")
    assert registry.count == 8
    with pytest.raises(MeasurementPolicyRegistryError):
        registry.deregister("ownership.coverage")
    assert MeasurementPolicyRegistry().count == 0
    assert len(default_measurement_policies()) == 9


def test_engine_skips_unmeasurable_policies_and_never_passes_them() -> None:
    engine = build_policy_engine()
    ownership_only = engine.measure(_context(ownership=_ownership()))
    measured = {outcome.policy_id for outcome in ownership_only.outcomes}
    assert "ownership.coverage" in measured
    assert "truth.classification.coverage" not in measured
    assert "assimilation.coverage" not in measured
    assert ownership_only.closed is False

    with pytest.raises(MeasurementContextError):
        engine.measure_strict(_context(ownership=_ownership()))


def test_engine_measures_a_complete_context() -> None:
    policy = default_truth_policy()
    context = _context(
        partition=policy.classify_all([HOME]),
        ownership=_ownership(),
        assimilation=_assimilation(),
    )
    engine = build_policy_engine()
    suite = engine.measure_strict(context)
    assert suite.total == 9
    assert suite.context_id == context.context_id
    assert engine.evaluate("ownership.coverage", context).value == 50.0
    assert len(engine.measurements(context)) == 9
    assert engine.registry.count == 9


def test_engine_construction_guard() -> None:
    with pytest.raises(MeasurementPolicyRegistryError):
        PolicyMeasurementEngine("nope")  # type: ignore[arg-type]


def test_closed_determination_is_reachable() -> None:
    policy = default_truth_policy()
    engine = OwnershipDeterminationEngine(
        EvidenceProviderRegistry([DefinitionalLocatorProvider(policy)]), policy=policy
    )
    determination = engine.determine([Subject.create("UCOS-COMP-000000", locators=[HOME])])
    pipeline = AssimilationPipeline(default_adapter_registry(), policy=policy)
    report = pipeline.assimilate(
        [SourceInput.from_text(KIND_MARKDOWN, "00-SOURCE/a.md", "# H\nbody")],
        destinations={"00-SOURCE/a.md": "02-MASTER/a.md"},
    )
    suite = build_policy_engine().measure_strict(
        _context(
            partition=policy.classify_all([HOME]),
            ownership=determination,
            assimilation=report,
        )
    )
    assert suite.closed is True
    assert suite.completeness == 100.0
    assert suite.to_dict()["determination"] == "CLOSED"


# --------------------------------------------------------------------------- wiring


def test_contract_surface_and_service_registration() -> None:
    assert policy_contract_names()
    assert len(POLICY_CONTRACTS) == len(policy_contract_names())
    assert bootstrap_measurement_policies().registry.count == 9
    registry = ServiceRegistry()
    descriptor = register_measurement_policies(registry)
    assert descriptor.name == "universal.measurement.policy"
    assert isinstance(registry.resolve("universal.measurement.policy"), PolicyMeasurementEngine)


# --------------------------------------------------------------------------- the CLI
#
# WHY THIS SECTION EXISTS. `ucos-measurement` is a PUBLISHED console script — the one
# command this capability names for itself — and nothing had ever invoked it. Its summary
# writer, its JSON writer and its fail-closed exit-2 arm were unexecuted, so the surface an
# operator actually types was the least measured part of the capability.


def test_the_policies_command_summarises_every_declared_policy(capsys) -> None:
    assert cli_main(["policies"]) == 0
    captured = capsys.readouterr()
    assert "UCOS-UMPF-001 MEASUREMENT POLICIES" in captured.err
    assert "command: policies" in captured.err
    assert f"declared policies: {bootstrap_measurement_policies().registry.count}" in captured.err
    assert "BLOCKING" in captured.err
    assert captured.out == ""


def test_the_contracts_command_summarises_the_published_surface(capsys) -> None:
    assert cli_main(["contracts"]) == 0
    captured = capsys.readouterr()
    assert "command: contracts" in captured.err
    for name in policy_contract_names():
        assert name in captured.err


def test_the_json_form_carries_the_same_payload_the_summary_describes(capsys) -> None:
    import json

    assert cli_main(["policies", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["policy_count"] == bootstrap_measurement_policies().registry.count
    assert len(payload["policies"]) == payload["policy_count"]
    assert len(payload["fingerprint"]) == 64

    assert cli_main(["contracts", "--json"]) == 0
    contracts = json.loads(capsys.readouterr().out)
    assert contracts["version"]
    assert len(contracts["contracts"]) == len(POLICY_CONTRACTS)


def test_the_two_commands_are_deterministic(capsys) -> None:
    cli_main(["policies", "--json"])
    first = capsys.readouterr().out
    cli_main(["policies", "--json"])
    assert capsys.readouterr().out == first


def test_an_unreadable_declared_composition_is_a_fault_and_never_a_pass(capsys) -> None:
    """Exit 2 is the whole reason this surface is safe to run anywhere: it never reports a
    policy set it could not read."""
    assert cli_main(["policies", "--document", "/nonexistent/policies.json"]) == 2
    assert "measurement error:" in capsys.readouterr().err


def test_an_unknown_command_is_refused_by_the_parser() -> None:
    with pytest.raises(SystemExit):
        cli_main(["not-a-command"])


# --------------------------------------------------------------------------- the composition
#
# WHICH measurements bind and HOW STRONGLY is data: the packaged declaration composes the nine
# shipped policies and configures each. Every test above reads the composed result, so the
# reader that turns a declaration into policies was only ever run over the packaged one — and
# each of its five refusals, which are what keep a declaration from becoming code, had no case.


def test_a_declaration_that_is_not_a_policy_composition_is_refused() -> None:
    """A COMPOSITION DOCUMENT HAS A SHAPE, AND THE SHAPE IS THE CONTRACT.

    A document that is not a mapping, or one whose ``policies`` is absent, a scalar or a
    string, cannot be composed — and each answers with what was wrong rather than raising from
    inside the iteration. A string is refused explicitly because it IS a sequence: iterating
    it would compose one policy per character and fail with a message about a policy named
    ``p``.
    """
    for malformed in ("nope", [], 7):
        with pytest.raises(MeasurementPolicyError, match="must be a mapping"):
            policies_from_document(malformed)  # type: ignore[arg-type]

    for shapeless in ({}, {"policies": "OwnershipCoveragePolicy"}, {"policies": 3}):
        with pytest.raises(MeasurementPolicyError, match="requires a 'policies' sequence"):
            policies_from_document(shapeless)  # type: ignore[arg-type]


def test_an_entry_that_names_no_policy_is_refused() -> None:
    """AN ENTRY IS A NAMED POLICY PLUS ITS CONFIGURATION, and the name is not optional.

    An entry with no ``policy`` key configures nothing — there is no default policy to fall
    back to, and choosing one would make the declaration's silence into a decision the
    declaration did not take.
    """
    for entry in ({"blocking": True}, "OwnershipCoveragePolicy", 7):
        with pytest.raises(MeasurementPolicyError, match="requires 'policy'"):
            policies_from_document({"policies": [entry]})


def test_a_declaration_may_name_only_a_shipped_policy() -> None:
    """RESOLUTION IS CONFINED TO THIS MODULE'S OWN NAMESPACE, and that is the security claim.

    A declaration composes the shipped policies and configures them; it can never name an
    arbitrary importable object. Both refusals were dead because the packaged declaration
    names only real policies: a name that is not a policy class at all, and the ABSTRACT
    policy itself — which would register a base class that measures nothing and answers for
    every measurement it was given.
    """
    with pytest.raises(MeasurementPolicyError, match="is not a MeasurementPolicy"):
        policies_from_document({"policies": [{"policy": "Path"}]})
    with pytest.raises(MeasurementPolicyError, match="is not a MeasurementPolicy"):
        policies_from_document({"policies": [{"policy": "NoSuchPolicyWasEverShipped"}]})
    with pytest.raises(MeasurementPolicyError, match="abstract policy cannot be registered"):
        policies_from_document({"policies": [{"policy": "MeasurementPolicy"}]})


def test_a_policy_that_cannot_be_configured_names_itself_in_the_refusal() -> None:
    """A DECLARED CONFIGURATION THAT THE POLICY REFUSES IS THE DECLARATION'S FAULT.

    ``precedence`` is coerced to an integer and ``blocking`` to a boolean, so a declaration
    supplying something neither can be built from fails at construction. The refusal carries
    the policy name and the underlying detail, because a bare "could not be configured" over a
    nine-entry declaration tells a reader nothing about which entry to fix.
    """
    with pytest.raises(MeasurementPolicyError, match="could not be configured") as raised:
        policies_from_document(
            {"policies": [{"policy": "OwnershipCoveragePolicy", "precedence": "not-a-number"}]}
        )

    assert raised.value.context["policy"] == "OwnershipCoveragePolicy"
    assert raised.value.context["detail"]


def test_a_composition_declaring_no_policy_is_refused() -> None:
    """AN EMPTY COMPOSITION MEASURES NOTHING AND WOULD REPORT EVERYTHING CLOSED.

    An empty ``policies`` list is well formed and unusable: a suite over zero policies is
    vacuously complete, so the engine would certify every project it was pointed at. Refusing
    is what keeps "no policy failed" from meaning "no policy ran".
    """
    with pytest.raises(MeasurementPolicyError, match="declares no policy"):
        policies_from_document({"policies": []})


def test_a_supplied_registry_overrides_the_declaration_entirely() -> None:
    """THREE WAYS TO COMPOSE THE ENGINE AND THE FIRST HAD NO CALLER.

    A registry handed in overrides the declaration; a document specialises it; neither means
    the packaged declaration governs. The override is what lets a caller measure a policy set
    it built or narrowed in memory — without it the only way to run a different set would be
    to write a declaration file first, which makes an in-process composition impossible to
    express.
    """
    narrowed = MeasurementPolicyRegistry((OwnershipCoveragePolicy(),))

    engine = bootstrap_measurement_policies(narrowed)

    assert engine.registry is narrowed
    assert engine.registry.count == 1
    assert bootstrap_measurement_policies().registry.count == 9
