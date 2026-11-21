"""The intelligence kernel — the primitives both research and publication are built on.

WHY THIS MODULE EXISTS. The kernel is reached only indirectly, through the two
subsystems that compose it, and both of them drive it along its happy path: a
well-formed declaration, an intact ledger, a report whose checks all pass. Everything
the kernel exists to REFUSE was therefore unexecuted — the malformed substrate
declaration, the unavailable required surface, the second identity over identical
content, the broken journal link, and the indeterminate verdict that closes a gate
without asserting a failure. A fail-closed primitive nobody has closed is a claim.
"""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import pytest

from intelligence.kernel.config import (
    WRITE_SCOPE_ROOT,
    NestedFileSink,
    subsystem_config,
)
from intelligence.kernel.errors import (
    DuplicateRecordError,
    KernelError,
    KnowledgeOnceViolation,
    LedgerIntegrityError,
    SubstrateDeclarationError,
    SubstrateUnavailableError,
    UnresolvedReferenceError,
)
from intelligence.kernel.ids import (
    ArtifactClass,
    artifact_id,
    class_codes,
    parse_class,
)
from intelligence.kernel.knowledge import (
    _METRICS,
    CONCEPT_FIELDS,
    COVERAGE_ATTRIBUTES,
    LIST_FIELDS,
    PROSE_FIELDS,
    CanonicalKnowledgeResolver,
    make_ref,
    parse_ref,
)
from intelligence.kernel.ledger import GENESIS_HASH, LedgerRegistry
from intelligence.kernel.substrate import SubstrateReader
from intelligence.kernel.validation import (
    EXIT_CLOSED,
    EXIT_OPEN,
    VERDICT_CERTIFIED,
    VERDICT_FAILED,
    VERDICT_INDETERMINATE,
    Check,
    report,
)
from intelligence.rie.config import RepoConfig

# -- errors ---------------------------------------------------------------------------


def test_a_kernel_error_carries_sorted_non_null_context_and_serialises_it():
    error = KernelError("something is wrong", zebra=1, alpha="a", omitted=None)
    assert error.context == {"alpha": "a", "zebra": 1}
    assert "alpha='a'" in str(error)
    assert error.to_dict() == {
        "error": "KernelError",
        "message": "something is wrong",
        "context": {"alpha": "a", "zebra": 1},
    }


def test_an_error_with_no_context_reads_as_its_message_alone():
    assert str(KernelError("bare")) == "bare"
    assert KernelError("bare").to_dict()["context"] == {}


# -- identity -------------------------------------------------------------------------


def test_an_identifier_is_a_pure_function_of_its_identity_tuple():
    first = artifact_id(ArtifactClass.RESEARCH_CLAIM, "the-claim")
    assert first == artifact_id("RESEARCH_CLAIM", "the-claim")
    assert first != artifact_id(ArtifactClass.RESEARCH_CLAIM, "a-different-claim")
    assert first.startswith("UCOS-RCLM-")
    assert len(first.rsplit("-", 1)[1]) == 12


def test_a_namespace_separates_two_otherwise_identical_natural_keys():
    default = artifact_id(ArtifactClass.CITATION, "k")
    elsewhere = artifact_id(ArtifactClass.CITATION, "k", namespace="ucos.elsewhere")
    assert default != elsewhere


def test_an_unknown_artifact_class_is_refused_and_names_what_is_allowed():
    with pytest.raises(KernelError) as excinfo:
        ArtifactClass.coerce("NOT_A_CLASS")
    assert "allowed" in excinfo.value.context


def test_the_class_is_recoverable_from_a_well_formed_identifier():
    identifier = artifact_id(ArtifactClass.PUBLICATION, "a-document")
    assert parse_class(identifier) is ArtifactClass.PUBLICATION


@pytest.mark.parametrize(
    "malformed",
    ["", "UCOS-PUB", "UCOS-PUB-", "NOPE-PUB-0123456789ab", "UCOS-XXXX-0123456789ab"],
)
def test_an_identifier_that_is_not_ours_is_refused_rather_than_guessed(malformed):
    with pytest.raises(KernelError):
        parse_class(malformed)


def test_the_class_code_table_is_published_and_collision_free():
    table = class_codes()
    assert set(table) == {c.value for c in ArtifactClass}
    assert len(set(table.values())) == len(table)
    assert table == dict(sorted(table.items()))


def test_every_class_declares_a_default_namespace():
    assert all(c.default_namespace for c in ArtifactClass)


# -- configuration and the write scope -------------------------------------------------


def test_a_subsystem_writes_only_inside_the_one_declared_scope(tmp_path):
    config = subsystem_config("publication", tmp_path)
    assert config.output_dir == tmp_path / WRITE_SCOPE_ROOT / "publication"


def test_a_nested_sink_honours_directory_segments_in_the_output_name(tmp_path):
    sink = NestedFileSink(tmp_path)
    written = sink.emit("publications/paper.md", "# Paper\n")
    assert Path(written) == tmp_path / "publications" / "paper.md"
    assert Path(written).read_text(encoding="utf-8") == "# Paper\n"


def test_a_nested_sink_refuses_an_output_name_that_escapes_its_directory(tmp_path):
    sink = NestedFileSink(tmp_path / "scope")
    with pytest.raises(ValueError, match="escapes the sink directory"):
        sink.emit("../escaped.md", "x")


def test_a_name_that_climbs_and_returns_stays_inside_the_scope(tmp_path):
    """``a/../b.md`` never leaves the directory, and the containment check resolves it
    without touching the filesystem — a not-yet-existing path has nothing to resolve."""
    sink = NestedFileSink(tmp_path / "scope")
    written = sink.emit("a/../b.md", "x")
    assert Path(written).resolve() == (tmp_path / "scope" / "b.md").resolve()


def test_a_name_that_climbs_past_the_root_is_refused(tmp_path):
    sink = NestedFileSink(tmp_path / "scope")
    with pytest.raises(ValueError):
        sink.emit("../../../../../../etc/passwd", "x")


# -- validation primitives ------------------------------------------------------------


def _check(check_id: str, passed: bool | None, *, blocking: bool = True) -> Check:
    return Check(
        check_id=check_id,
        title=f"Title {check_id}",
        obligation=f"Obligation {check_id}",
        passed=passed,
        blocking=blocking,
    )


def test_every_check_passing_certifies_and_opens_the_gate():
    result = report("subject", "PROG", [_check("b", True), _check("a", True)])
    assert [c.check_id for c in result.checks] == ["a", "b"]
    assert result.verdict == VERDICT_CERTIFIED
    assert result.gate_open is True
    assert result.exit_code == EXIT_OPEN
    assert result.blocking_failures() == ()


def test_a_blocking_violation_fails_and_closes_the_gate():
    result = report("subject", "PROG", [_check("a", True), _check("b", False)])
    assert result.verdict == VERDICT_FAILED
    assert result.gate_open is False
    assert result.exit_code == EXIT_CLOSED
    assert [c.check_id for c in result.failed()] == ["b"]


def test_an_indeterminate_blocking_check_closes_the_gate_without_asserting_a_failure():
    """The whole reason the state is tri-valued: absent evidence may not be reported as a
    violation, and may not be reported as a pass either."""
    result = report("subject", "PROG", [_check("a", True), _check("b", None)])
    assert result.verdict == VERDICT_INDETERMINATE
    assert result.gate_open is False
    assert [c.check_id for c in result.indeterminate()] == ["b"]
    assert result.failed() == ()
    assert [c.state for c in result.checks] == ["PASS", VERDICT_INDETERMINATE]


def test_a_violation_outranks_an_indeterminate_when_both_are_present():
    result = report("s", "P", [_check("a", None), _check("b", False)])
    assert result.verdict == VERDICT_FAILED


def test_a_non_blocking_check_is_reported_and_never_closes_the_gate():
    result = report("s", "P", [_check("a", True), _check("b", False, blocking=False)])
    assert result.verdict == VERDICT_CERTIFIED
    assert result.gate_open is True
    assert result.failed() and result.blocking_failures() == ()


def test_a_report_serialises_its_partitions_and_its_summary_line():
    result = report("s", "PROG", [_check("a", True), _check("b", False), _check("c", None)])
    payload = result.to_dict()
    assert payload["gate"] == "CLOSED"
    assert payload["checks_total"] == 3
    assert payload["checks_passed"] == 1
    assert payload["checks_failed"] == 1
    assert payload["checks_indeterminate"] == 1
    assert payload["blocking_failures"] == ["b", "c"]
    assert payload["checks"][0]["state"] == "PASS"
    assert result.summary_line() == "PROG: FAILED | checks=1/3 PASS | gate=CLOSED"


# -- the append-only ledger ------------------------------------------------------------


def _ledger() -> LedgerRegistry:
    return LedgerRegistry(registry_id="TEST-LEDGER", schema="ucos-test-ledger")


def test_an_empty_ledger_heads_at_genesis():
    ledger = _ledger()
    assert ledger.head() == GENESIS_HASH
    assert ledger.count() == 0
    assert ledger.all() == ()
    assert ledger.verify()["intact"] is True


def test_registration_appends_one_journal_entry_and_moves_the_head():
    ledger = _ledger()
    entry = ledger.register(ArtifactClass.RESEARCH_CLAIM, "claim-1", {"body": "one"})
    assert ledger.exists(entry.record_id) is True
    assert ledger.get(entry.record_id) is entry
    assert ledger.get("UCOS-RCLM-000000000000") is None
    assert ledger.head() != GENESIS_HASH
    assert len(ledger.journal()) == 1
    assert ledger.journal()[0].previous_hash == GENESIS_HASH


def test_the_identifier_a_ledger_will_mint_is_computable_before_registration():
    ledger = _ledger()
    predicted = ledger.id_for(ArtifactClass.RESEARCH_CLAIM, "claim-1")
    entry = ledger.register(ArtifactClass.RESEARCH_CLAIM, "claim-1", {"body": "one"})
    assert predicted == entry.record_id
    assert ledger.id_for("RESEARCH_CLAIM", "claim-1", namespace=None) == predicted


def test_records_are_partitioned_by_class():
    ledger = _ledger()
    claim = ledger.register(ArtifactClass.RESEARCH_CLAIM, "c", {"body": "claim"})
    source = ledger.register(ArtifactClass.RESEARCH_SOURCE, "s", {"body": "source"})
    assert ledger.by_class(ArtifactClass.RESEARCH_CLAIM) == (claim,)
    assert ledger.ids_by_class("RESEARCH_SOURCE") == (source.record_id,)
    assert ledger.by_class(ArtifactClass.CITATION) == ()
    assert ledger.class_histogram() == {"RESEARCH_CLAIM": 1, "RESEARCH_SOURCE": 1}


def test_registering_the_same_identity_twice_is_refused():
    ledger = _ledger()
    ledger.register(ArtifactClass.RESEARCH_CLAIM, "claim-1", {"body": "one"})
    with pytest.raises(DuplicateRecordError):
        ledger.register(ArtifactClass.RESEARCH_CLAIM, "claim-1", {"body": "two"})


def test_identical_content_under_a_second_identity_is_refused():
    ledger = _ledger()
    ledger.register(ArtifactClass.RESEARCH_CLAIM, "claim-1", {"body": "same"})
    with pytest.raises(KnowledgeOnceViolation):
        ledger.register(ArtifactClass.RESEARCH_CLAIM, "claim-2", {"body": "same"})


def test_a_tampered_journal_link_is_reported_and_then_refused():
    """The chain is what makes the ledger append-only rather than merely a dict, so the
    detection is forged: no public method can break a link."""
    ledger = _ledger()
    ledger.register(ArtifactClass.RESEARCH_CLAIM, "claim-1", {"body": "one"})
    ledger.register(ArtifactClass.RESEARCH_CLAIM, "claim-2", {"body": "two"})
    journal = ledger.journal()
    ledger._journal[1] = replace(journal[1], previous_hash=GENESIS_HASH)

    verdict = ledger.verify()
    assert verdict["chain_intact"] is False
    assert verdict["broken_links"] == [2]
    assert verdict["intact"] is False
    with pytest.raises(LedgerIntegrityError):
        ledger.require_integrity()


def test_an_intact_ledger_requires_nothing_and_snapshots_itself():
    ledger = _ledger()
    ledger.register(ArtifactClass.PUBLICATION, "doc", {"body": "text"})
    ledger.require_integrity()
    snapshot = ledger.snapshot()
    assert snapshot["registry_id"] == "TEST-LEDGER"
    assert snapshot["count"] == 1
    assert snapshot["journal_head"] == ledger.head()
    assert snapshot["integrity"]["knowledge_once_holds"] is True


# -- the substrate reader --------------------------------------------------------------


_MINIMAL = (
    {
        "key": "records",
        "locator": "data/records.json",
        "media": "json",
        "authority": "DERIVED",
        "role": "test records",
        "required": True,
        "root_key": "rows",
    },
    {
        "key": "docs",
        "locator": "docs",
        "media": "directory",
        "authority": "DERIVED",
        "role": "test documents",
        "required": False,
        "glob": "*.md",
    },
)


def _reader(tmp_path: Path, declaration=_MINIMAL) -> SubstrateReader:
    return SubstrateReader(RepoConfig.create(tmp_path), declaration)


def test_a_declared_json_surface_is_read_and_its_records_counted(tmp_path):
    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "records.json").write_text(
        json.dumps({"rows": [{"a": 1}, {"b": 2}, "not-a-row"]}), encoding="utf-8"
    )
    reader = _reader(tmp_path)
    surface = reader.require("records")
    assert surface.available is True
    assert surface.record_count == 2
    assert surface.content_sha256 != "absent"
    assert reader.records("records") == [{"a": 1}, {"b": 2}]
    assert surface.to_dict()["key"] == "records"


def test_a_declared_directory_surface_lists_only_the_files_its_glob_names(tmp_path):
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "one.md").write_text("one", encoding="utf-8")
    (tmp_path / "docs" / "ignored.txt").write_text("two", encoding="utf-8")
    reader = _reader(tmp_path)
    assert reader.directory_names("docs") == ("one.md",)
    assert reader.surface("docs").record_count == 1


def test_an_absent_directory_surface_lists_nothing_and_hashes_as_absent(tmp_path):
    reader = _reader(tmp_path)
    assert reader.available("docs") is False
    assert reader.directory_names("docs") == ()
    assert reader.surface("docs").content_sha256 == "absent"


def test_an_unavailable_required_surface_asserts_no_verdict(tmp_path):
    with pytest.raises(SubstrateUnavailableError):
        _reader(tmp_path).require("records")


def test_an_absent_json_surface_reads_as_an_empty_payload_rather_than_raising(tmp_path):
    reader = _reader(tmp_path)
    assert reader.payload("records") == {}
    assert reader.records("records") == []


def test_a_surface_that_is_not_readable_json_is_fail_closed(tmp_path):
    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "records.json").write_text("{ not json", encoding="utf-8")
    with pytest.raises(SubstrateUnavailableError, match="not readable JSON"):
        _reader(tmp_path).payload("records")


def test_a_json_surface_whose_root_is_not_an_object_reads_as_empty(tmp_path):
    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "records.json").write_text("[1, 2, 3]", encoding="utf-8")
    assert _reader(tmp_path).payload("records") == {}


def test_a_root_key_naming_something_that_is_not_a_list_yields_no_records(tmp_path):
    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "records.json").write_text('{"rows": {"a": 1}}', encoding="utf-8")
    assert _reader(tmp_path).records("records") == []


def test_a_surface_declaring_no_root_key_yields_no_records(tmp_path):
    declaration = ({**_MINIMAL[0], "root_key": ""},)
    assert _reader(tmp_path, declaration).records("records") == []


def test_asking_a_directory_surface_for_a_json_payload_is_a_declaration_error(tmp_path):
    with pytest.raises(SubstrateDeclarationError, match="not a JSON document"):
        _reader(tmp_path).payload("docs")


def test_an_undeclared_key_is_refused_rather_than_resolved(tmp_path):
    with pytest.raises(SubstrateDeclarationError, match="not declared"):
        _reader(tmp_path).declaration("nothing-declares-this")


def test_the_declared_keys_are_reported_in_stable_order(tmp_path):
    assert _reader(tmp_path).keys() == ("docs", "records")


@pytest.mark.parametrize(
    ("mutation", "match"),
    [
        ({"surprise": 1}, "unknown substrate declaration keys"),
        ({"key": ""}, "non-empty string"),
        ({"locator": 7}, "non-empty string"),
        ({"media": "parchment"}, "unknown substrate media"),
        ({"authority": "SELF-EVIDENT"}, "unknown substrate authority"),
        ({"required": "yes"}, "must be a boolean"),
    ],
)
def test_a_malformed_declaration_asserts_no_verdict(tmp_path, mutation, match):
    with pytest.raises(SubstrateDeclarationError, match=match):
        _reader(tmp_path, ({**_MINIMAL[0], **mutation},))


def test_a_key_declared_twice_is_refused(tmp_path):
    with pytest.raises(SubstrateDeclarationError, match="declared twice"):
        _reader(tmp_path, (_MINIMAL[0], dict(_MINIMAL[0])))


def test_an_empty_declaration_is_refused(tmp_path):
    with pytest.raises(SubstrateDeclarationError, match="declaration is empty"):
        _reader(tmp_path, ())


# -- the canonical knowledge resolver, and every reference it refuses --------------------
#
# WHY THIS SECTION EXISTS. The resolver's contract is "a value may not be invented": every
# reference either resolves to content that exists in a governed record, or is REFUSED by
# name. The publication subsystem exercises the resolving half over this repository, so the
# refusing half — a malformed reference, an unknown space, an unresolvable field, an empty
# field, an undeclared metric, an unavailable surface, a path that dead-ends or lands on a
# container — was entirely unexecuted. Those refusals ARE the no-fabrication guarantee.


def _resolver(tmp_path: Path, declaration=None):
    return CanonicalKnowledgeResolver(_reader(tmp_path, declaration or _MINIMAL))


def test_a_reference_that_is_not_space_colon_target_is_refused(tmp_path):
    assert parse_ref("cko:UCOS-X#statement") == ("cko", "UCOS-X", "statement")
    assert parse_ref("cko:UCOS-X") == ("cko", "UCOS-X", "")
    assert make_ref("cko", "UCOS-X", "statement") == "cko:UCOS-X#statement"
    assert make_ref("cko", "UCOS-X") == "cko:UCOS-X"

    for malformed in ("no-colon", 7, ":target", "space:", "  :  "):
        with pytest.raises(UnresolvedReferenceError):
            parse_ref(malformed)


def test_a_reference_space_the_resolver_does_not_understand_is_refused(tmp_path):
    resolver = _resolver(tmp_path)
    with pytest.raises(UnresolvedReferenceError) as excinfo:
        resolver.resolve("rumour:something#field")
    assert excinfo.value.context["allowed"] == list(resolver.SPACES)
    assert resolver.exists("rumour:something#field") is False


def _concept_repo(tmp_path: Path, rows: list[dict]):
    declaration = (
        {
            "key": "concept-closure",
            "locator": "data/concepts.json",
            "media": "json",
            "authority": "DERIVED",
            "role": "concept closure",
            "required": True,
            "root_key": "concepts",
        },
    )
    (tmp_path / "data").mkdir(parents=True, exist_ok=True)
    (tmp_path / "data" / "concepts.json").write_text(
        json.dumps({"concepts": rows}), encoding="utf-8"
    )
    return _resolver(tmp_path, declaration)


def test_a_concept_reference_resolves_and_every_way_it_can_fail_is_named(tmp_path):
    field = sorted(CONCEPT_FIELDS)[0]
    resolver = _concept_repo(tmp_path, [{"id": "C-1", field: "a value"}])
    resolved = resolver.resolve(f"concept:C-1#{field}")
    assert resolved.text == "a value"
    assert resolved.value_kind == "label"
    assert resolved.source_locator.endswith("#C-1")

    with pytest.raises(UnresolvedReferenceError, match="concept not found"):
        resolver.resolve(f"concept:NOTHING#{field}")
    with pytest.raises(UnresolvedReferenceError, match="not resolvable on a concept"):
        resolver.resolve("concept:C-1#not-a-concept-field")
    missing = sorted(CONCEPT_FIELDS - {field})[0]
    with pytest.raises(UnresolvedReferenceError, match="has no such field"):
        resolver.resolve(f"concept:C-1#{missing}")


def _metric_repo(tmp_path: Path, payload, *, write: bool = True):
    key = sorted(_METRICS)[0]
    declaration_key = _METRICS[key]["surface"]
    locator = f"data/{declaration_key}.json"
    declaration = (
        {
            "key": declaration_key,
            "locator": locator,
            "media": "json",
            "authority": "DERIVED",
            "role": "metric surface",
            "required": True,
        },
    )
    if write:
        (tmp_path / "data").mkdir(parents=True, exist_ok=True)
        (tmp_path / locator).write_text(json.dumps(payload), encoding="utf-8")
    return key, _METRICS[key], _resolver(tmp_path, declaration)


def test_an_undeclared_metric_is_refused_and_names_the_declared_set(tmp_path):
    _key, _declaration, resolver = _metric_repo(tmp_path, {})
    with pytest.raises(UnresolvedReferenceError) as excinfo:
        resolver.resolve("metric:not-a-declared-metric")
    assert excinfo.value.context["allowed"]


def test_an_unavailable_metric_surface_refuses_rather_than_inventing_a_value(tmp_path):
    key, _declaration, resolver = _metric_repo(tmp_path, {}, write=False)
    with pytest.raises(UnresolvedReferenceError, match="may not be invented"):
        resolver.resolve(f"metric:{key}")


def test_a_metric_path_that_dead_ends_or_lands_on_a_container_is_refused(tmp_path):
    key, declaration, resolver = _metric_repo(tmp_path, {"nothing": "here"})
    with pytest.raises(UnresolvedReferenceError, match="path does not resolve"):
        resolver.resolve(f"metric:{key}")

    payload: dict = {}
    node = payload
    for step in declaration["path"][:-1]:
        node[step] = {}
        node = node[step]
    node[declaration["path"][-1]] = {"a": "container"}
    _key, _declaration, container = _metric_repo(tmp_path / "container", payload)
    with pytest.raises(UnresolvedReferenceError, match="resolves to a container"):
        container.resolve(f"metric:{key}")


def test_a_metric_that_resolves_to_a_scalar_is_returned_with_its_provenance(tmp_path):
    key, declaration, _resolver_unused = _metric_repo(tmp_path / "seed", {})
    payload: dict = {}
    node = payload
    for step in declaration["path"][:-1]:
        node[step] = {}
        node = node[step]
    node[declaration["path"][-1]] = 42
    _k, _d, resolver = _metric_repo(tmp_path / "value", payload)
    resolved = resolver.resolve(f"metric:{key}")
    assert resolved.text == "42"
    assert resolved.value_kind == "scalar"
    assert resolved.source_content_sha256
    assert set(resolved.provenance()) == {
        "ref",
        "source_locator",
        "source_authority",
        "source_content_sha256",
    }


def test_an_undeclared_coverage_attribute_is_refused(tmp_path):
    resolver = _resolver(tmp_path)
    with pytest.raises(UnresolvedReferenceError) as excinfo:
        resolver.resolve("coverage:not-an-attribute")
    assert excinfo.value.context["allowed"]


def test_unavailable_coverage_evidence_refuses_rather_than_inventing_a_value(tmp_path):
    resolver = _resolver(tmp_path)
    attribute = sorted(COVERAGE_ATTRIBUTES)[0]
    with pytest.raises(UnresolvedReferenceError, match="may not be invented"):
        resolver.resolve(f"coverage:{attribute}")


def test_resolve_all_resolves_each_reference_it_is_given(tmp_path):
    field = sorted(CONCEPT_FIELDS)[0]
    resolver = _concept_repo(tmp_path, [{"id": "C-1", field: "one"}, {"id": "C-2", field: "two"}])
    resolved = resolver.resolve_all([f"concept:C-1#{field}", f"concept:C-2#{field}"])
    assert [r.text for r in resolved] == ["one", "two"]


def test_the_field_guard_refuses_an_unresolvable_name_and_both_empty_shapes(tmp_path):
    """A field the space cannot answer, and a field that answers with nothing.

    An empty value would resolve to a real locator and an empty content, and a consumer
    that hashes it would believe the emptiness is evidence. Both list and prose shapes are
    refused, and the field name itself is checked against the declared vocabulary first.
    """
    resolver = _resolver(tmp_path)
    lists = sorted(LIST_FIELDS["decision"])
    prose = sorted(PROSE_FIELDS["decision"])
    with pytest.raises(UnresolvedReferenceError, match="not resolvable"):
        resolver._field_content(
            ref="decision:D-1#nope",
            space="decision",
            target="D-1",
            field="nope",
            record={},
            content_sha256="x",
            locator="here",
            authority="test",
        )
    with pytest.raises(UnresolvedReferenceError, match="list field is empty"):
        resolver._field_content(
            ref=f"decision:D-1#{lists[0]}",
            space="decision",
            target="D-1",
            field=lists[0],
            record={lists[0]: []},
            content_sha256="x",
            locator="here",
            authority="test",
        )
    with pytest.raises(UnresolvedReferenceError, match="prose field is empty"):
        resolver._field_content(
            ref=f"decision:D-1#{prose[0]}",
            space="decision",
            target="D-1",
            field=prose[0],
            record={prose[0]: "   "},
            content_sha256="x",
            locator="here",
            authority="test",
        )
    resolved = resolver._field_content(
        ref=f"decision:D-1#{prose[0]}",
        space="decision",
        target="D-1",
        field=prose[0],
        record={prose[0]: "stated"},
        content_sha256="x",
        locator="here",
        authority="test",
    )
    assert resolved.text == "stated"
    assert resolved.field == prose[0]
