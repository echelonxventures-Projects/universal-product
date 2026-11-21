"""UCOS-EPIC-013 — Continuous Validation Intelligence configuration tests (Terminal T5).

Everything the runtime does is configuration driven, so the loader is a trust boundary:
a malformed *authoring* fault must raise :class:`IntelligenceConfigError` (never silently
degrade into a weaker run), while the file formats stay standard-library only.
"""

from __future__ import annotations

import json
from pathlib import Path
from platform.tests._validation_intelligence_helpers import (
    passing_config_mapping,
    passing_facts,
)
from platform.validation_intelligence.config import (
    ValidationIntelligenceConfig,
    load_config,
    parse_config,
)
from platform.validation_intelligence.contracts import IntelligenceDimension, IntelligenceTarget
from platform.validation_intelligence.errors import IntelligenceConfigError

import pytest


def _write(tmp_path: Path, name: str, text: str) -> Path:
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return path


# --- assimilation ----------------------------------------------------------------
def test_parse_config_assimilates_a_full_mapping():
    config = parse_config(passing_config_mapping("t1"))
    assert config.target_id == "t1"
    assert set(config.facts) == set(passing_facts())
    assert config.dimensions == ()


def test_config_defaults_to_empty_facts_and_dimensions():
    config = parse_config({"target_id": "t1"})
    assert config.facts == {}
    assert config.dimensions == ()


def test_config_rejects_a_non_mapping():
    with pytest.raises(IntelligenceConfigError):
        ValidationIntelligenceConfig.from_mapping(["not", "a", "mapping"])


@pytest.mark.parametrize("raw", [{}, {"target_id": ""}, {"target_id": None}, {"target_id": 5}])
def test_config_requires_a_non_empty_string_target_id(raw):
    with pytest.raises(IntelligenceConfigError):
        parse_config(raw)


def test_config_rejects_non_mapping_facts():
    with pytest.raises(IntelligenceConfigError) as exc:
        parse_config({"target_id": "t1", "facts": ["nope"]})
    assert exc.value.context["target_id"] == "t1"


def test_config_reuses_target_assimilation_for_the_facts_shape():
    """A bad dimension key inside facts is caught by the target's own assimilation."""
    with pytest.raises(Exception) as exc:
        parse_config({"target_id": "t1", "facts": {"not-a-dimension": {}}})
    assert "dimension" in str(exc.value).lower()


# --- dimension selection ---------------------------------------------------------
def test_declared_dimensions_are_parsed_in_declaration_order():
    config = parse_config(
        {
            "target_id": "t1",
            "dimensions": ["governance_compliance", "repository_completeness"],
        }
    )
    assert config.dimensions == (
        IntelligenceDimension.GOVERNANCE_COMPLIANCE,
        IntelligenceDimension.REPOSITORY_COMPLETENESS,
    )


def test_absent_dimensions_mean_the_full_suite():
    assert parse_config({"target_id": "t1"}).selected_dimensions() is None


def test_an_empty_dimension_list_means_the_full_suite():
    assert parse_config({"target_id": "t1", "dimensions": []}).selected_dimensions() is None


def test_selected_dimensions_returns_the_declared_subset():
    config = parse_config({"target_id": "t1", "dimensions": ["repository_completeness"]})
    assert config.selected_dimensions() == (IntelligenceDimension.REPOSITORY_COMPLETENESS,)


@pytest.mark.parametrize("dimensions", ["repository_completeness", 5, {"a": 1}, b"x"])
def test_dimensions_must_be_a_list(dimensions):
    with pytest.raises(IntelligenceConfigError) as exc:
        parse_config({"target_id": "t1", "dimensions": dimensions})
    assert "list" in str(exc.value)


def test_an_unknown_dimension_is_rejected_with_the_supported_set():
    with pytest.raises(IntelligenceConfigError) as exc:
        parse_config({"target_id": "t1", "dimensions": ["bogus"]})
    assert exc.value.context["dimension"] == "bogus"
    assert len(exc.value.context["supported"]) == 7


def test_a_duplicate_dimension_is_rejected():
    with pytest.raises(IntelligenceConfigError) as exc:
        parse_config({"target_id": "t1", "dimensions": ["repository_completeness"] * 2})
    assert exc.value.context["dimension"] == "repository_completeness"


# --- projection ------------------------------------------------------------------
def test_build_target_projects_an_equivalent_target():
    config = parse_config(passing_config_mapping("t1"))
    target = config.build_target()
    assert isinstance(target, IntelligenceTarget)
    assert target.target_id == "t1"
    assert target.digest() == IntelligenceTarget(target_id="t1", facts=config.facts).digest()


def test_config_to_dict_sorts_facts_for_determinism():
    config = parse_config(passing_config_mapping())
    assert list(config.to_dict()["facts"]) == sorted(passing_facts())


def test_config_digest_is_stable_and_order_insensitive():
    first = parse_config(passing_config_mapping("t1"))
    second = parse_config(passing_config_mapping("t1"))
    assert first.digest() == second.digest()


def test_config_digest_changes_with_the_declared_dimensions():
    base = passing_config_mapping("t1")
    scoped = {**base, "dimensions": ["repository_completeness"]}
    assert parse_config(base).digest() != parse_config(scoped).digest()


# --- file loading ----------------------------------------------------------------
def test_load_config_reads_json(tmp_path):
    path = _write(tmp_path, "intel.json", json.dumps(passing_config_mapping("from-json")))
    assert load_config(path).target_id == "from-json"


def test_load_config_reads_toml(tmp_path):
    toml = "\n".join(
        [
            'target_id = "from-toml"',
            'dimensions = ["repository_completeness"]',
            "",
            "[facts.repository_completeness]",
            "gaps = 0",
        ]
    )
    config = load_config(_write(tmp_path, "intel.toml", toml))
    assert config.target_id == "from-toml"
    assert config.dimensions == (IntelligenceDimension.REPOSITORY_COMPLETENESS,)
    assert config.facts["repository_completeness"]["gaps"] == 0


def test_load_config_accepts_a_string_path(tmp_path):
    path = _write(tmp_path, "intel.json", json.dumps({"target_id": "t1"}))
    assert load_config(str(path)).target_id == "t1"


def test_load_config_rejects_a_missing_file(tmp_path):
    with pytest.raises(IntelligenceConfigError) as exc:
        load_config(tmp_path / "absent.json")
    assert "not found" in str(exc.value)


def test_load_config_rejects_a_directory(tmp_path):
    with pytest.raises(IntelligenceConfigError):
        load_config(tmp_path)


@pytest.mark.parametrize("name", ["intel.yaml", "intel.txt", "intel", "intel.JSON.bak"])
def test_load_config_rejects_an_unsupported_file_type(tmp_path, name):
    with pytest.raises(IntelligenceConfigError) as exc:
        load_config(_write(tmp_path, name, "{}"))
    assert "unsupported" in str(exc.value)


def test_load_config_rejects_malformed_json(tmp_path):
    with pytest.raises(IntelligenceConfigError) as exc:
        load_config(_write(tmp_path, "intel.json", "{not json"))
    assert "could not be read or parsed" in str(exc.value)


def test_load_config_rejects_malformed_toml(tmp_path):
    with pytest.raises(IntelligenceConfigError) as exc:
        load_config(_write(tmp_path, "intel.toml", "target_id = "))
    assert "could not be read or parsed" in str(exc.value)


def test_load_config_rejects_undecodable_bytes(tmp_path):
    path = tmp_path / "intel.json"
    path.write_bytes(b"\xff\xfe\x00invalid")
    with pytest.raises(IntelligenceConfigError):
        load_config(path)


@pytest.mark.parametrize("body", ["[1, 2, 3]", '"a string"', "42", "null"])
def test_load_config_requires_a_mapping_root(tmp_path, body):
    with pytest.raises(IntelligenceConfigError) as exc:
        load_config(_write(tmp_path, "intel.json", body))
    assert "mapping/table" in str(exc.value)


def test_a_suffix_is_matched_case_insensitively(tmp_path):
    path = _write(tmp_path, "intel.JSON", json.dumps({"target_id": "t1"}))
    assert load_config(path).target_id == "t1"


def test_json_and_toml_configs_agree_on_one_digest(tmp_path):
    """The file format is a transport detail; identity comes from the content."""
    as_json = _write(tmp_path, "a.json", json.dumps({"target_id": "t", "facts": {}}))
    as_toml = _write(tmp_path, "a.toml", 'target_id = "t"')
    assert load_config(as_json).digest() == load_config(as_toml).digest()
