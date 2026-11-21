"""UCOS-EPIC-014 — Universal Assurance policy substrate tests.

The module's central claim is that the engine "contains no list of validation
obligations, no list of certification criteria, no gate composition, no metric, no
threshold, and no required-evidence set" — all of it is declared, and the code knows
only the document's *shape*. Two things follow, and both are tested here:

* **Shape enforcement is total.** Every section validates fail-closed against an
  explicit ``ALLOWED_KEYS`` set, so every rejection branch is driven to its error and
  the structured ``context`` is asserted — an error that cannot say *which* section
  and *which* field is not auditable (PL-02, IP-12).
* **Content is never assumed.** The declarative lookups are exercised against a
  document whose ordering, duplication and cross-references differ from the answer,
  so a test cannot pass by restating a constant the module also hard-codes.

The canonical shipped policy is assimilated too: a document the package ships but
never parses under test is an unproven claim.
"""

from __future__ import annotations

import json
from platform.universal_assurance.contracts import (
    AssuranceStage,
    ObligationKind,
    Severity,
)
from platform.universal_assurance.errors import AssurancePolicyError
from platform.universal_assurance.policy import (
    DEFAULT_POLICY_FILENAME,
    POLICY_FORMAT,
    AssurancePolicy,
    PolicyEvidenceArtifact,
    PolicyEvidenceRules,
    PolicyGate,
    PolicyIdentity,
    PolicyMetric,
    PolicyObligation,
    ReproducibilityPolicy,
    default_policy_path,
    load_default_policy,
    load_policy,
    package_data_path,
    parse_policy,
)

import pytest

from engine.universal_certification.contracts import MeasurementComparator

from .universal_assurance_helpers import REAL_RULE_REF, make_policy, policy_mapping


def _write(tmp_path, name, text):
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return path


def _obligation(**kw):
    base = {
        "id": "OB-1",
        "stage": "validation-execution",
        "kind": "validation-rule",
        "ref": REAL_RULE_REF,
        "severity": "blocking",
    }
    base.update(kw)
    return base


# -- section shape: unknown keys are rejected everywhere ---------------------


@pytest.mark.parametrize(
    ("overrides", "section"),
    [
        ({"nonsense": 1}, "<root>"),
        ({"policy": {**policy_mapping()["policy"], "nonsense": 1}}, "policy"),
        ({"obligations": [_obligation(nonsense=1)]}, "obligations"),
        (
            {
                "obligations": [_obligation()],
                "gates": [{"id": "G", "name": "g", "stages": [], "obligations": [], "nonsense": 1}],
            },
            "gates",
        ),
        (
            {
                "metrics": [
                    {
                        "id": "M",
                        "stage": "validation-execution",
                        "observation": "o",
                        "comparator": "ge",
                        "threshold": 1,
                        "severity": "blocking",
                        "nonsense": 1,
                    }
                ]
            },
            "metrics",
        ),
        ({"evidence": {"nonsense": 1}}, "evidence"),
        (
            {
                "evidence": {
                    "artifacts": [
                        {"id": "A", "stage": "evidence-collection", "name": "a", "nonsense": 1}
                    ]
                }
            },
            "evidence.artifacts",
        ),
        ({"reproducibility": {"nonsense": 1}}, "reproducibility"),
    ],
)
def test_every_section_rejects_unknown_keys_and_names_itself(overrides, section):
    with pytest.raises(AssurancePolicyError) as excinfo:
        parse_policy(policy_mapping(**overrides))
    assert excinfo.value.context["section"] == section
    assert excinfo.value.context["unknown"] == ["nonsense"]
    # The rejection is auditable: it reports what WOULD have been accepted.
    assert "allowed" in excinfo.value.context


def test_unknown_key_report_lists_every_offender_sorted():
    with pytest.raises(AssurancePolicyError) as excinfo:
        parse_policy(policy_mapping(zeta=1, alpha=2, mu=3))
    assert excinfo.value.context["unknown"] == ["alpha", "mu", "zeta"]


# -- root document shape -----------------------------------------------------


@pytest.mark.parametrize("raw", [None, [], "policy", 7])
def test_a_policy_document_must_be_a_mapping(raw):
    with pytest.raises(AssurancePolicyError, match="must be a mapping"):
        parse_policy(raw)


def test_a_policy_must_declare_at_least_one_obligation():
    with pytest.raises(AssurancePolicyError, match="at least one obligation") as excinfo:
        parse_policy(policy_mapping(obligations=[]))
    assert excinfo.value.context["policy"] == "TEST-POLICY-001"


def test_a_policy_with_no_obligations_key_at_all_is_equally_rejected():
    document = policy_mapping()
    del document["obligations"]
    with pytest.raises(AssurancePolicyError, match="at least one obligation"):
        parse_policy(document)


@pytest.mark.parametrize("section", ["obligations", "gates", "metrics"])
def test_list_sections_reject_non_list_values(section):
    with pytest.raises(AssurancePolicyError, match="must be a list") as excinfo:
        parse_policy(policy_mapping(**{section: {"not": "a list"}}))
    assert excinfo.value.context["section"] == section


@pytest.mark.parametrize("value", ["a string is a Sequence but not a list", b"bytes too"])
def test_str_and_bytes_are_not_accepted_as_list_sections(value):
    with pytest.raises(AssurancePolicyError, match="must be a list"):
        parse_policy(policy_mapping(obligations=value))


def test_an_absent_optional_list_section_defaults_to_empty():
    policy = parse_policy(policy_mapping(gates=None, metrics=None))
    assert policy.gates == ()
    assert policy.metrics == ()


# -- identity ----------------------------------------------------------------


@pytest.mark.parametrize("field_name", ["id", "name", "version", "authority"])
@pytest.mark.parametrize("bad", [None, "", 7, [], {}])
def test_identity_requires_every_named_field_as_non_empty_text(field_name, bad):
    identity = {**policy_mapping()["policy"], field_name: bad}
    with pytest.raises(AssurancePolicyError, match="non-empty string") as excinfo:
        parse_policy(policy_mapping(policy=identity))
    assert excinfo.value.context["field"] == field_name
    assert excinfo.value.context["section"] == "policy"


@pytest.mark.parametrize("raw", [None, [], "x"])
def test_the_identity_section_itself_must_be_a_mapping(raw):
    with pytest.raises(AssurancePolicyError, match="section must be a mapping") as excinfo:
        parse_policy(policy_mapping(policy=raw))
    assert excinfo.value.context["section"] == "policy"


@pytest.mark.parametrize("bad", [1, 0, "true", None])
def test_fail_closed_must_be_a_real_boolean_not_a_truthy_stand_in(bad):
    identity = {**policy_mapping()["policy"], "fail_closed": bad}
    with pytest.raises(AssurancePolicyError, match="fail_closed must be a boolean") as excinfo:
        parse_policy(policy_mapping(policy=identity))
    assert excinfo.value.context["value"] == bad


def test_fail_closed_defaults_to_closed_when_undeclared():
    identity = {k: v for k, v in policy_mapping()["policy"].items() if k != "fail_closed"}
    assert parse_policy(policy_mapping(policy=identity)).identity.fail_closed is True


def test_description_is_optional_and_coerced_to_text():
    identity = {**policy_mapping()["policy"], "description": 42}
    assert parse_policy(policy_mapping(policy=identity)).identity.description == "42"
    identity.pop("description")
    assert parse_policy(policy_mapping(policy=identity)).identity.description == ""


def test_identity_round_trips_through_its_dict():
    identity = make_policy().identity
    assert PolicyIdentity(**identity.to_dict()) == identity


# -- obligations -------------------------------------------------------------


@pytest.mark.parametrize(
    ("field_name", "enum_cls"),
    [("stage", AssuranceStage), ("kind", ObligationKind), ("severity", Severity)],
)
def test_obligation_enum_fields_reject_unsupported_values_and_report_the_vocabulary(
    field_name, enum_cls
):
    with pytest.raises(AssurancePolicyError, match="unsupported value") as excinfo:
        parse_policy(policy_mapping(obligations=[_obligation(**{field_name: "invented"})]))
    context = excinfo.value.context
    assert context["field"] == field_name
    assert context["value"] == "invented"
    # The error teaches the caller the whole vocabulary rather than just refusing.
    assert context["supported"] == [member.value for member in enum_cls]


def test_requires_facts_defaults_to_empty_and_accepts_declared_addresses():
    policy = parse_policy(policy_mapping(obligations=[_obligation()], gates=[]))
    assert policy.obligations[0].requires_facts == ()
    policy = parse_policy(
        policy_mapping(obligations=[_obligation(requires_facts=["a", "b"])], gates=[])
    )
    assert policy.obligations[0].requires_facts == ("a", "b")


@pytest.mark.parametrize("bad", [[""], [None], [7], [{}]])
def test_requires_facts_entries_must_be_non_empty_strings(bad):
    with pytest.raises(AssurancePolicyError, match="non-empty strings") as excinfo:
        parse_policy(policy_mapping(obligations=[_obligation(requires_facts=bad)]))
    assert excinfo.value.context["field"] == "requires_facts"


def test_obligation_blocking_is_derived_from_declared_severity_only():
    policy = parse_policy(
        policy_mapping(
            obligations=[
                _obligation(id="OB-B", severity="blocking"),
                _obligation(id="OB-A", severity="advisory"),
            ],
            gates=[],
        )
    )
    blocking = {o.id: o.blocking for o in policy.obligations}
    assert blocking == {"OB-B": True, "OB-A": False}


def test_duplicate_obligation_ids_fail_closed():
    with pytest.raises(AssurancePolicyError, match="duplicate ids") as excinfo:
        parse_policy(policy_mapping(obligations=[_obligation(id="SAME"), _obligation(id="SAME")]))
    assert excinfo.value.context["section"] == "obligations"
    assert excinfo.value.context["duplicates"] == ["SAME"]


def test_obligations_are_ordered_by_stage_then_kind_then_id_not_declaration_order():
    policy = parse_policy(
        policy_mapping(
            obligations=[
                _obligation(id="Z", stage="certification-execution", kind="certification-frame"),
                _obligation(
                    id="A", stage="certification-execution", kind="certification-criterion"
                ),
                _obligation(id="M", stage="validation-planning"),
            ],
            gates=[],
        )
    )
    # M sorts first on stage order; within the later stage, criterion precedes frame
    # on kind order — so neither declaration order nor id order explains the result.
    assert [o.id for o in policy.obligations] == ["M", "A", "Z"]


def test_obligation_round_trips_through_its_dict():
    obligation = make_policy().obligation("OB-RULE")
    restored = PolicyObligation.from_mapping(obligation.to_dict())
    assert restored == obligation


# -- gates -------------------------------------------------------------------


def test_gate_stages_are_deduplicated_and_ordered_by_stage_order():
    policy = parse_policy(
        policy_mapping(
            obligations=[_obligation()],
            gates=[
                {
                    "id": "G",
                    "name": "g",
                    "stages": [
                        "certification-execution",
                        "validation-planning",
                        "certification-execution",
                    ],
                    "obligations": ["OB-1"],
                }
            ],
        )
    )
    assert policy.gates[0].stages == (
        AssuranceStage.VALIDATION_PLANNING,
        AssuranceStage.CERTIFICATION_EXECUTION,
    )


def test_a_gate_may_not_reference_an_undeclared_obligation():
    with pytest.raises(AssurancePolicyError, match="undeclared obligations") as excinfo:
        parse_policy(
            policy_mapping(
                obligations=[_obligation(id="DECLARED")],
                gates=[
                    {
                        "id": "G",
                        "name": "g",
                        "stages": ["validation-execution"],
                        "obligations": ["DECLARED", "GHOST", "PHANTOM"],
                    }
                ],
            )
        )
    assert excinfo.value.context["gate"] == "G"
    assert excinfo.value.context["dangling"] == ["GHOST", "PHANTOM"]


def test_duplicate_gate_ids_fail_closed():
    gate = {"id": "SAME", "name": "g", "stages": [], "obligations": []}
    with pytest.raises(AssurancePolicyError, match="duplicate ids") as excinfo:
        parse_policy(policy_mapping(obligations=[_obligation()], gates=[gate, dict(gate)]))
    assert excinfo.value.context["section"] == "gates"


def test_gates_are_sorted_by_id():
    gates = [
        {"id": "G-Z", "name": "z", "stages": [], "obligations": []},
        {"id": "G-A", "name": "a", "stages": [], "obligations": []},
    ]
    policy = parse_policy(policy_mapping(obligations=[_obligation()], gates=gates))
    assert [g.id for g in policy.gates] == ["G-A", "G-Z"]


def test_gate_round_trips_through_its_dict():
    gate = make_policy().gates[0]
    assert PolicyGate.from_mapping(gate.to_dict()) == gate


# -- metrics -----------------------------------------------------------------


@pytest.mark.parametrize("bad", [True, False, "90", None, [], {}])
def test_metric_threshold_must_be_numeric_and_a_bool_is_not_a_number(bad):
    metric = {
        "id": "M",
        "stage": "validation-execution",
        "observation": "o",
        "comparator": "ge",
        "threshold": bad,
        "severity": "blocking",
    }
    with pytest.raises(AssurancePolicyError, match="threshold must be numeric") as excinfo:
        parse_policy(policy_mapping(metrics=[metric]))
    assert excinfo.value.context["metric"] == "M"


@pytest.mark.parametrize(("declared", "expected"), [(0, 0.0), (90, 90.0), (99.5, 99.5)])
def test_an_integer_threshold_is_normalized_to_float(declared, expected):
    metric = {
        "id": "M",
        "stage": "validation-execution",
        "observation": "o",
        "comparator": "ge",
        "threshold": declared,
        "severity": "blocking",
    }
    threshold = parse_policy(policy_mapping(metrics=[metric])).metrics[0].threshold
    assert isinstance(threshold, float)
    assert threshold == expected


def test_metric_comparator_rejects_a_verdict_the_certifier_does_not_ship():
    metric = {
        "id": "M",
        "stage": "validation-execution",
        "observation": "o",
        "comparator": "approximately",
        "threshold": 1,
        "severity": "blocking",
    }
    with pytest.raises(AssurancePolicyError, match="unsupported value") as excinfo:
        parse_policy(policy_mapping(metrics=[metric]))
    assert excinfo.value.context["supported"] == [m.value for m in MeasurementComparator]


def test_metric_blocking_and_optional_text_fields():
    policy = make_policy()
    by_id = {m.id: m for m in policy.metrics}
    assert by_id["M-EXEC"].blocking is True
    assert by_id["M-COVERAGE"].blocking is False
    assert by_id["M-COVERAGE"].unit == "percent"
    assert by_id["M-EXEC"].rationale == ""


def test_metric_round_trips_through_its_dict():
    metric = make_policy().metrics[0]
    assert PolicyMetric.from_mapping(metric.to_dict()) == metric


def test_duplicate_metric_ids_fail_closed():
    metric = {
        "id": "SAME",
        "stage": "validation-execution",
        "observation": "o",
        "comparator": "ge",
        "threshold": 1,
        "severity": "blocking",
    }
    with pytest.raises(AssurancePolicyError, match="duplicate ids") as excinfo:
        parse_policy(policy_mapping(metrics=[metric, dict(metric)]))
    assert excinfo.value.context["section"] == "metrics"


# -- evidence ----------------------------------------------------------------


def test_an_absent_evidence_section_yields_the_empty_contract():
    policy = parse_policy(policy_mapping(evidence=None))
    assert policy.evidence == PolicyEvidenceRules()
    assert policy.evidence.artifacts == ()
    assert policy.evidence.required_artifacts() == ()


@pytest.mark.parametrize("bad", [1, "yes", None])
def test_artifact_required_must_be_a_real_boolean(bad):
    evidence = {
        "artifacts": [{"id": "A", "stage": "evidence-collection", "name": "a", "required": bad}]
    }
    with pytest.raises(AssurancePolicyError, match="'required' must be a boolean") as excinfo:
        parse_policy(policy_mapping(evidence=evidence))
    assert excinfo.value.context["artifact"] == "A"


def test_artifact_required_defaults_to_true():
    evidence = {"artifacts": [{"id": "A", "stage": "evidence-collection", "name": "a"}]}
    policy = parse_policy(policy_mapping(evidence=evidence))
    assert policy.evidence.artifacts[0].required is True


def test_required_artifacts_is_the_required_subset_only():
    rules = make_policy().evidence
    assert {a.id for a in rules.artifacts} == {"EV-PLAN", "EV-OPTIONAL"}
    assert {a.id for a in rules.required_artifacts()} == {"EV-PLAN"}


def test_duplicate_artifact_ids_fail_closed():
    artifact = {"id": "SAME", "stage": "evidence-collection", "name": "a"}
    with pytest.raises(AssurancePolicyError, match="duplicate ids") as excinfo:
        parse_policy(policy_mapping(evidence={"artifacts": [artifact, dict(artifact)]}))
    assert excinfo.value.context["section"] == "evidence.artifacts"


def test_artifacts_are_ordered_by_stage_then_id():
    evidence = {
        "artifacts": [
            {"id": "Z", "stage": "certification-registry", "name": "z"},
            {"id": "B", "stage": "validation-planning", "name": "b"},
            {"id": "A", "stage": "validation-planning", "name": "a"},
        ]
    }
    policy = parse_policy(policy_mapping(evidence=evidence))
    assert [a.id for a in policy.evidence.artifacts] == ["A", "B", "Z"]


def test_forbidden_write_prefixes_are_carried_verbatim():
    assert make_policy().evidence.forbidden_write_prefixes == ("99-FREEZE", "00-BOOK")


def test_evidence_types_round_trip_through_their_dicts():
    rules = make_policy().evidence
    assert PolicyEvidenceRules.from_mapping(rules.to_dict()) == rules
    artifact = rules.artifacts[0]
    assert PolicyEvidenceArtifact.from_mapping(artifact.to_dict()) == artifact


# -- bindings ----------------------------------------------------------------


def test_absent_bindings_yield_an_empty_map():
    assert parse_policy(policy_mapping(bindings=None)).bindings == {}


@pytest.mark.parametrize("raw", [[], "x", 7])
def test_bindings_must_be_a_mapping(raw):
    with pytest.raises(AssurancePolicyError, match="section must be a mapping") as excinfo:
        parse_policy(policy_mapping(bindings=raw))
    assert excinfo.value.context["section"] == "bindings"


def test_binding_names_must_be_non_empty_strings():
    with pytest.raises(AssurancePolicyError, match="binding names must be"):
        parse_policy(policy_mapping(bindings={"": "value"}))


@pytest.mark.parametrize("bad", ["", None, 7, []])
def test_binding_values_must_be_non_empty_strings_and_the_error_names_the_binding(bad):
    with pytest.raises(AssurancePolicyError, match="binding values must be") as excinfo:
        parse_policy(policy_mapping(bindings={"evidence_root": bad}))
    assert excinfo.value.context["binding"] == "evidence_root"


def test_binding_lookup_returns_declared_falls_back_and_finally_fails_closed():
    policy = make_policy()
    assert policy.binding("registry_id") == "TEST-REGISTRY"
    assert policy.binding("undeclared", "fallback") == "fallback"
    with pytest.raises(AssurancePolicyError, match="no such binding") as excinfo:
        policy.binding("undeclared")
    assert excinfo.value.context["binding"] == "undeclared"
    assert excinfo.value.context["policy"] == "TEST-POLICY-001"


# -- reproducibility ---------------------------------------------------------


def test_absent_reproducibility_yields_the_declared_default_contract():
    policy = parse_policy(policy_mapping(reproducibility=None))
    assert policy.reproducibility == ReproducibilityPolicy()
    assert policy.reproducibility.replays == 2
    assert policy.reproducibility.byte_identical_required is True


@pytest.mark.parametrize("bad", [1, 0, -1, True, False, "2", 2.0, None])
def test_replays_below_two_or_not_an_integer_is_rejected(bad):
    with pytest.raises(AssurancePolicyError, match="replays must be an integer >= 2") as excinfo:
        parse_policy(policy_mapping(reproducibility={"replays": bad}))
    assert excinfo.value.context["value"] == bad


def test_two_replays_is_the_accepted_floor():
    policy = parse_policy(policy_mapping(reproducibility={"replays": 2}))
    assert policy.reproducibility.replays == 2


@pytest.mark.parametrize("bad", [1, "yes", None])
def test_byte_identical_required_must_be_a_real_boolean(bad):
    with pytest.raises(AssurancePolicyError, match="byte_identical_required must be a boolean"):
        parse_policy(policy_mapping(reproducibility={"byte_identical_required": bad}))


def test_reproducibility_may_declare_that_byte_identity_is_not_required():
    policy = parse_policy(
        policy_mapping(reproducibility={"replays": 3, "byte_identical_required": False})
    )
    assert policy.reproducibility.replays == 3
    assert policy.reproducibility.byte_identical_required is False
    assert policy.reproducibility.to_dict() == {
        "replays": 3,
        "byte_identical_required": False,
    }


# -- declarative lookups (the engine asks; it never enumerates) --------------


def test_obligations_for_filters_by_stage_by_kind_and_by_both():
    policy = make_policy()
    assert {o.id for o in policy.obligations_for()} == {
        "OB-RULE",
        "OB-DIM",
        "OB-CRIT",
        "OB-FRAME",
    }
    assert {o.id for o in policy.obligations_for(AssuranceStage.CERTIFICATION_EXECUTION)} == {
        "OB-CRIT",
        "OB-FRAME",
    }
    assert {o.id for o in policy.obligations_for(kind=ObligationKind.VALIDATION_RULE)} == {
        "OB-RULE"
    }
    assert {
        o.id
        for o in policy.obligations_for(
            AssuranceStage.CERTIFICATION_EXECUTION,
            kind=ObligationKind.CERTIFICATION_FRAME,
        )
    } == {"OB-FRAME"}


def test_obligations_for_a_stage_the_policy_never_touches_is_empty_not_an_error():
    assert make_policy().obligations_for(AssuranceStage.CERTIFICATION_EVIDENCE) == ()


def test_obligation_lookup_finds_declared_and_fails_closed_on_the_rest():
    policy = make_policy()
    assert policy.obligation("OB-CRIT").ref == "validation-complete"
    with pytest.raises(AssurancePolicyError, match="no such obligation") as excinfo:
        policy.obligation("OB-GHOST")
    assert excinfo.value.context["obligation"] == "OB-GHOST"


def test_metrics_for_returns_all_or_the_stage_subset():
    policy = make_policy()
    assert len(policy.metrics_for()) == 2
    assert len(policy.metrics_for(AssuranceStage.VALIDATION_EXECUTION)) == 2
    assert policy.metrics_for(AssuranceStage.CERTIFICATION_REGISTRY) == ()


def test_artifacts_for_returns_all_or_the_stage_subset():
    policy = make_policy()
    assert len(policy.artifacts_for()) == 2
    assert [a.id for a in policy.artifacts_for(AssuranceStage.VALIDATION_PLANNING)] == ["EV-PLAN"]
    assert policy.artifacts_for(AssuranceStage.CERTIFICATION_REGISTRY) == ()


def test_stages_declared_unions_obligations_metrics_artifacts_and_gates():
    policy = make_policy()
    assert policy.stages_declared() == (
        AssuranceStage.VALIDATION_PLANNING,
        AssuranceStage.VALIDATION_EXECUTION,
        AssuranceStage.EVIDENCE_COLLECTION,
        AssuranceStage.CERTIFICATION_EXECUTION,
        AssuranceStage.VALIDATION_INTELLIGENCE,
    )


def test_a_stage_reachable_only_through_a_gate_is_still_declared():
    """A gate may name a stage no obligation, metric or artifact mentions."""
    policy = parse_policy(
        policy_mapping(
            obligations=[_obligation(stage="validation-execution")],
            gates=[
                {
                    "id": "G",
                    "name": "g",
                    "stages": ["certification-registry"],
                    "obligations": ["OB-1"],
                }
            ],
            metrics=[],
            evidence=None,
        )
    )
    assert AssuranceStage.CERTIFICATION_REGISTRY in policy.stages_declared()


# -- counts, serialization, content addressing -------------------------------


def test_counts_are_derived_from_the_document_not_declared_in_it():
    assert make_policy().counts() == {
        "obligations": 4,
        "blocking_obligations": 3,
        "gates": 2,
        "metrics": 2,
        "artifacts": 2,
        "required_artifacts": 1,
        "stages": 5,
    }


def test_to_dict_stamps_the_format_and_sorts_bindings():
    document = make_policy().to_dict()
    assert document["policy_format"] == POLICY_FORMAT
    assert list(document["bindings"]) == sorted(document["bindings"])


def test_the_policy_dict_round_trips_back_into_an_identical_policy():
    policy = make_policy()
    restored = parse_policy({k: v for k, v in policy.to_dict().items() if k != "policy_format"})
    assert restored == policy
    assert restored.digest() == policy.digest()


def test_the_digest_is_a_pure_function_of_content_not_declaration_order():
    document = policy_mapping()
    shuffled = dict(document)
    shuffled["obligations"] = list(reversed(document["obligations"]))
    shuffled["gates"] = list(reversed(document["gates"]))
    shuffled["metrics"] = list(reversed(document["metrics"]))
    assert parse_policy(shuffled).digest() == parse_policy(document).digest()


def test_the_digest_moves_when_any_governed_content_moves():
    baseline = make_policy().digest()
    tightened = policy_mapping()
    tightened["metrics"][1]["threshold"] = 95
    assert parse_policy(tightened).digest() != baseline


def test_the_digest_is_stable_across_repeated_derivation():
    policy = make_policy()
    assert policy.digest() == policy.digest() == make_policy().digest()


# -- loading from disk -------------------------------------------------------


def test_load_policy_reads_json(tmp_path):
    path = _write(tmp_path, "p.json", json.dumps(policy_mapping()))
    assert load_policy(path).digest() == make_policy().digest()


def test_load_policy_reads_toml_and_agrees_with_the_json_of_the_same_content(tmp_path):
    toml = """
[policy]
id = "TOML-POLICY"
name = "toml"
version = "1.0.0"
authority = "ENGINEERING-EXECUTION-ONLY"
fail_closed = true

[[obligations]]
id = "OB-1"
stage = "validation-execution"
kind = "validation-rule"
ref = "architecture.layers-declared"
severity = "blocking"
"""
    from_toml = load_policy(_write(tmp_path, "p.toml", toml))
    equivalent = {
        "policy": {
            "id": "TOML-POLICY",
            "name": "toml",
            "version": "1.0.0",
            "authority": "ENGINEERING-EXECUTION-ONLY",
            "fail_closed": True,
        },
        "obligations": [_obligation()],
    }
    assert from_toml.digest() == parse_policy(equivalent).digest()


def test_load_policy_accepts_an_uppercase_suffix(tmp_path):
    path = _write(tmp_path, "p.JSON", json.dumps(policy_mapping()))
    assert load_policy(path).identity.id == "TEST-POLICY-001"


def test_load_policy_accepts_a_string_path(tmp_path):
    path = _write(tmp_path, "p.json", json.dumps(policy_mapping()))
    assert load_policy(str(path)).identity.id == "TEST-POLICY-001"


def test_an_absent_policy_file_fails_closed(tmp_path):
    with pytest.raises(AssurancePolicyError, match="policy file not found") as excinfo:
        load_policy(tmp_path / "nope.json")
    assert excinfo.value.context["path"].endswith("nope.json")


def test_a_directory_is_not_a_policy_file(tmp_path):
    with pytest.raises(AssurancePolicyError, match="policy file not found"):
        load_policy(tmp_path)


def test_an_unsupported_policy_file_type_is_named_in_the_error(tmp_path):
    path = _write(tmp_path, "p.yaml", "policy: {}")
    with pytest.raises(AssurancePolicyError, match="unsupported policy file type") as excinfo:
        load_policy(path)
    assert excinfo.value.context["suffix"] == ".yaml"


@pytest.mark.parametrize(
    ("name", "text"),
    [("p.json", "{not json"), ("p.toml", "this is = = not toml")],
)
def test_an_unparseable_policy_file_fails_closed_with_the_parser_detail(tmp_path, name, text):
    with pytest.raises(AssurancePolicyError, match="could not be read or parsed") as excinfo:
        load_policy(_write(tmp_path, name, text))
    assert excinfo.value.context["detail"]


def test_undecodable_bytes_fail_closed_rather_than_crash(tmp_path):
    path = tmp_path / "p.json"
    path.write_bytes(b"\xff\xfe\x00invalid utf-8")
    with pytest.raises(AssurancePolicyError, match="could not be read or parsed"):
        load_policy(path)


@pytest.mark.parametrize("payload", ["[]", '"a string"', "7", "null"])
def test_a_policy_file_whose_root_is_not_a_mapping_fails_closed(tmp_path, payload):
    with pytest.raises(AssurancePolicyError, match="root must be a mapping"):
        load_policy(_write(tmp_path, "p.json", payload))


# -- the canonical policy the package actually ships -------------------------


def test_package_data_path_resolves_inside_the_package():
    path = package_data_path(DEFAULT_POLICY_FILENAME)
    assert path == default_policy_path()
    assert path.parent.name == "data"
    assert path.parent.parent.name == "universal_assurance"


def test_the_shipped_default_policy_exists_and_assimilates():
    """A policy the package ships but never parses under test is an unproven claim."""
    assert default_policy_path().is_file()
    policy = load_default_policy()
    assert isinstance(policy, AssurancePolicy)
    assert policy.identity.fail_closed is True
    assert policy.obligations, "the shipped policy must declare obligations"


def test_the_shipped_policy_declares_no_dangling_gate_and_no_duplicate_id():
    """Re-assimilation is the check: from_mapping enforces both invariants."""
    policy = load_default_policy()
    declared = {o.id for o in policy.obligations}
    for gate in policy.gates:
        assert set(gate.obligations) <= declared
    assert len(declared) == len(policy.obligations)


def test_the_shipped_policy_digest_is_reproducible():
    assert load_default_policy().digest() == load_default_policy().digest()
