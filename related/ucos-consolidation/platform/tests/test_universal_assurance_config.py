"""UCOS-EPIC-014 — Universal Assurance run-configuration tests.

The module separates two authorities and says neither can be inferred from the other:
the **policy** declares what must hold, the **subject** supplies the facts it must hold
over. These tests hold that separation to account — a config that resolves a subject
but no policy, or a policy but no subject, must not produce a runnable configuration.

The distinction the module draws between a *malformed configuration* (an authoring
fault, which raises) and a *fail-closed verdict* (which is data) is load-bearing, so
the subject-assimilation failure is checked to arrive as an ``AssuranceConfigError``
that preserves the underlying subject error rather than leaking it raw.

The reference self-check configuration the package ships is loaded and resolved end
to end, because a known-good run that is never executed is not known to be good.
"""

from __future__ import annotations

import json
from platform.universal_assurance.config import (
    CONFIG_FORMAT,
    SELFCHECK_CONFIG_FILENAME,
    AssuranceConfig,
    load_config,
    load_selfcheck_config,
    parse_config,
    selfcheck_config_path,
)
from platform.universal_assurance.errors import AssuranceConfigError
from platform.universal_assurance.policy import AssurancePolicy, load_default_policy

import pytest

from .universal_assurance_helpers import make_policy, policy_mapping, subject_mapping


def _write(tmp_path, name, text):
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return path


def _config(**overrides):
    document = {"subject": subject_mapping()}
    document.update(overrides)
    return document


# -- shape -------------------------------------------------------------------


@pytest.mark.parametrize("raw", [None, [], "config", 7])
def test_a_configuration_must_be_a_mapping(raw):
    with pytest.raises(AssuranceConfigError, match="config must be a mapping"):
        parse_config(raw)


def test_unknown_configuration_keys_are_rejected_and_the_allowed_set_is_reported():
    with pytest.raises(AssuranceConfigError, match="unknown keys") as excinfo:
        parse_config(_config(zeta=1, alpha=2))
    assert excinfo.value.context["unknown"] == ["alpha", "zeta"]
    assert "subject" in excinfo.value.context["allowed"]


def test_schema_and_comment_annotations_are_permitted_not_rejected():
    """The shipped documents carry them, so the parser must tolerate them."""
    config = parse_config(_config(**{"$schema": "./s.json", "$comment": "note"}))
    assert config.subject.subject_id == "TEST-SUBJECT"


def test_a_configuration_without_a_subject_is_an_authoring_fault():
    with pytest.raises(AssuranceConfigError, match="requires a 'subject' block"):
        parse_config({"policy_path": "p.json"})


def test_an_explicitly_null_subject_is_equally_rejected():
    with pytest.raises(AssuranceConfigError, match="requires a 'subject' block"):
        parse_config({"subject": None})


def test_an_unassimilable_subject_surfaces_as_a_config_error_carrying_the_detail():
    """A subject fault is a *configuration* fault at this boundary, not a raw leak."""
    with pytest.raises(AssuranceConfigError) as excinfo:
        parse_config({"subject": {"version": "1.0.0"}})
    assert "subject could not be assimilated" in str(excinfo.value)
    assert excinfo.value.context["detail"]
    assert excinfo.value.__cause__ is not None


@pytest.mark.parametrize("field_name", ["policy_path", "evidence_dir", "approver"])
@pytest.mark.parametrize("bad", [7, [], {}, True])
def test_optional_text_fields_reject_non_strings_and_name_themselves(field_name, bad):
    with pytest.raises(AssuranceConfigError, match="must be a string") as excinfo:
        parse_config(_config(**{field_name: bad}))
    assert excinfo.value.context["field"] == field_name


@pytest.mark.parametrize("field_name", ["policy_path", "evidence_dir", "approver"])
def test_optional_text_fields_default_to_empty_when_absent_or_null(field_name):
    assert getattr(parse_config(_config()), field_name) == ""
    assert getattr(parse_config(_config(**{field_name: None})), field_name) == ""


def test_an_empty_string_is_preserved_and_means_undeclared():
    assert parse_config(_config(policy_path="")).policy_path == ""


# -- policy resolution: the two authorities stay separate --------------------


def test_a_declared_policy_path_is_loaded_in_preference_to_the_default(tmp_path):
    path = _write(tmp_path, "p.json", json.dumps(policy_mapping()))
    config = parse_config(_config(policy_path=str(path)))
    assert config.load_policy().digest() == make_policy().digest()


def test_an_undeclared_policy_path_falls_back_to_the_canonical_shipped_policy():
    config = parse_config(_config())
    resolved = config.load_policy()
    assert isinstance(resolved, AssurancePolicy)
    assert resolved.digest() == load_default_policy().digest()


def test_a_declared_but_absent_policy_path_fails_closed_rather_than_falling_back(tmp_path):
    """Silent fallback would run the wrong policy — the config must refuse instead."""
    config = parse_config(_config(policy_path=str(tmp_path / "missing.json")))
    with pytest.raises(Exception, match="policy file not found"):
        config.load_policy()


# -- evidence directory resolution -------------------------------------------


def test_a_declared_evidence_dir_wins_over_the_policy_binding():
    config = parse_config(_config(evidence_dir=".runtime/declared-evidence"))
    assert config.resolved_evidence_dir(make_policy()) == ".runtime/declared-evidence"


def test_an_undeclared_evidence_dir_falls_back_to_the_policy_binding():
    config = parse_config(_config())
    assert config.resolved_evidence_dir(make_policy()) == ".runtime/test-evidence"


def test_an_undeclared_evidence_dir_and_an_unbinding_policy_resolve_to_empty():
    """The binding default is '' — absence is reported, never invented."""
    policy = make_policy(bindings={"registry_id": "R"})
    assert parse_config(_config()).resolved_evidence_dir(policy) == ""


# -- serialization and content addressing ------------------------------------


def test_to_dict_stamps_the_format_and_embeds_the_subject():
    document = parse_config(_config(approver="qa")).to_dict()
    assert document["config_format"] == CONFIG_FORMAT
    assert document["approver"] == "qa"
    assert document["subject"]["subject_id"] == "TEST-SUBJECT"


def test_the_digest_is_a_pure_function_of_the_configuration_content():
    assert parse_config(_config()).digest() == parse_config(_config()).digest()


def test_the_digest_moves_when_any_resolved_field_moves():
    baseline = parse_config(_config()).digest()
    assert parse_config(_config(approver="qa")).digest() != baseline
    assert parse_config(_config(evidence_dir="/x")).digest() != baseline
    assert parse_config(_config(policy_path="p.json")).digest() != baseline


def test_the_digest_moves_when_the_subject_facts_move():
    baseline = parse_config(_config()).digest()
    other = parse_config({"subject": subject_mapping(subject_id="OTHER")})
    assert other.digest() != baseline


def test_a_config_is_immutable():
    config = parse_config(_config())
    with pytest.raises(AttributeError):
        config.approver = "someone-else"


def test_configs_built_from_equal_documents_are_equal():
    assert parse_config(_config()) == parse_config(_config())


# -- loading from disk -------------------------------------------------------


def test_load_config_reads_json(tmp_path):
    path = _write(tmp_path, "c.json", json.dumps(_config(approver="qa")))
    assert load_config(path).approver == "qa"


def test_load_config_reads_toml(tmp_path):
    toml = """
approver = "toml-qa"

[subject]
subject_id = "TOML-SUBJECT"
version = "2.0.0"
"""
    config = load_config(_write(tmp_path, "c.toml", toml))
    assert config.approver == "toml-qa"
    assert config.subject.subject_id == "TOML-SUBJECT"


def test_load_config_accepts_an_uppercase_suffix_and_a_string_path(tmp_path):
    path = _write(tmp_path, "c.JSON", json.dumps(_config()))
    assert load_config(str(path)).subject.subject_id == "TEST-SUBJECT"


def test_an_absent_configuration_file_fails_closed(tmp_path):
    with pytest.raises(AssuranceConfigError, match="configuration file not found") as excinfo:
        load_config(tmp_path / "nope.json")
    assert excinfo.value.context["path"].endswith("nope.json")


def test_a_directory_is_not_a_configuration_file(tmp_path):
    with pytest.raises(AssuranceConfigError, match="configuration file not found"):
        load_config(tmp_path)


def test_an_unsupported_configuration_file_type_is_named_in_the_error(tmp_path):
    with pytest.raises(AssuranceConfigError, match="unsupported configuration") as excinfo:
        load_config(_write(tmp_path, "c.yaml", "subject: {}"))
    assert excinfo.value.context["suffix"] == ".yaml"


@pytest.mark.parametrize(
    ("name", "text"),
    [("c.json", "{not json"), ("c.toml", "this is = = not toml")],
)
def test_an_unparseable_configuration_fails_closed_with_the_parser_detail(tmp_path, name, text):
    with pytest.raises(AssuranceConfigError, match="could not be read or parsed") as excinfo:
        load_config(_write(tmp_path, name, text))
    assert excinfo.value.context["detail"]


def test_undecodable_bytes_fail_closed_rather_than_crash(tmp_path):
    path = tmp_path / "c.json"
    path.write_bytes(b"\xff\xfe\x00invalid utf-8")
    with pytest.raises(AssuranceConfigError, match="could not be read or parsed"):
        load_config(path)


@pytest.mark.parametrize("payload", ["[]", '"a string"', "7", "null"])
def test_a_configuration_whose_root_is_not_a_mapping_fails_closed(tmp_path, payload):
    with pytest.raises(AssuranceConfigError, match="root must be a mapping"):
        load_config(_write(tmp_path, "c.json", payload))


# -- the reference self-check the package actually ships ---------------------


def test_the_selfcheck_path_resolves_inside_the_package_data_dir():
    path = selfcheck_config_path()
    assert path.name == SELFCHECK_CONFIG_FILENAME
    assert path.parent.name == "data"
    assert path.parent.parent.name == "universal_assurance"


def test_the_shipped_selfcheck_configuration_exists_and_assimilates():
    """A known-good reference run that is never executed is not known to be good."""
    assert selfcheck_config_path().is_file()
    config = load_selfcheck_config()
    assert isinstance(config, AssuranceConfig)
    assert config.subject.subject_id


def test_the_shipped_selfcheck_resolves_a_policy_and_an_evidence_dir():
    config = load_selfcheck_config()
    policy = config.load_policy()
    assert policy.obligations, "the self-check must run against a policy with obligations"
    assert config.resolved_evidence_dir(policy)


def test_the_shipped_selfcheck_digest_is_reproducible():
    assert load_selfcheck_config().digest() == load_selfcheck_config().digest()
