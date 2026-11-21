"""UKIP Part 03 — providers, and the unboundedness of the provider set."""

from __future__ import annotations

import json

import pytest

from engine.knowledge.model import KnowledgeKind, RelationType
from engine.knowledge.ukip.contracts import KnowledgeUnit, ProviderKind, SourceRef
from engine.knowledge.ukip.errors import ProviderConflictError, ProviderError
from engine.knowledge.ukip.providers import (
    DEFAULT_PRIORITY,
    MAX_DOCUMENT_BYTES,
    CallableProvider,
    CanonicalStoreProvider,
    DecisionLogProvider,
    DocumentProvider,
    KnowledgeProvider,
    MappingProvider,
    ProviderDescriptor,
    ProviderRegistry,
    default_providers,
    default_registry,
)
from engine.tests.knowledge.conftest import make_cko, make_decision
from engine.tests.knowledge.ukip.conftest import make_provider, make_source, make_unit

# ---------------------------------------------------------------------------
# unboundedness (UKIP-LAW-001)
# ---------------------------------------------------------------------------


def test_registry_accepts_an_arbitrary_number_of_providers():
    """No ceiling, and no engine change per provider."""
    registry = ProviderRegistry()
    for index in range(50):
        registry.add(
            make_provider(
                f"p{index:03d}",
                (make_unit(f"u{index}", source=make_source(provider_id=f"p{index:03d}")),),
            )
        )
    assert len(registry) == 50
    assert len(registry.collect()) == 50


def test_iteration_order_is_priority_then_id_not_insertion():
    late = make_provider("aaa", (), priority=900)
    early = make_provider("zzz", (), priority=1)
    registry = ProviderRegistry([late, early])
    assert registry.provider_ids() == ("zzz", "aaa")


def test_same_priority_breaks_ties_on_provider_id():
    registry = ProviderRegistry(
        [make_provider("b", (), priority=5), make_provider("a", (), priority=5)]
    )
    assert registry.provider_ids() == ("a", "b")


def test_registration_order_does_not_change_collected_units():
    first = make_provider("one", (make_unit("u1", source=make_source(provider_id="one")),))
    second = make_provider("two", (make_unit("u2", source=make_source(provider_id="two")),))
    forward = ProviderRegistry([first, second]).collect()
    backward = ProviderRegistry([second, first]).collect()
    assert [u.key for u in forward] == [u.key for u in backward]


def test_duplicate_identity_is_rejected_but_re_adding_the_same_object_is_a_no_op():
    provider = make_provider("p", ())
    registry = ProviderRegistry([provider])
    registry.add(provider)
    assert len(registry) == 1
    with pytest.raises(ProviderConflictError):
        registry.add(make_provider("p", ()))


def test_registry_membership_lookup_and_removal():
    provider = make_provider("p", ())
    registry = ProviderRegistry([provider])
    assert "p" in registry
    assert registry.get("p") is provider
    assert registry.require("p") is provider
    assert registry.get("absent") is None
    with pytest.raises(ProviderError):
        registry.require("absent")
    registry.remove("p")
    registry.remove("p")  # idempotent
    assert len(registry) == 0


def test_registry_rejects_non_providers():
    with pytest.raises(ProviderError):
        ProviderRegistry(["not a provider"])


def test_extend_by_kind_and_authoritative_views():
    doc = make_provider("d", (), kind=ProviderKind.DOCUMENT)
    store = make_provider("s", (), kind=ProviderKind.CANONICAL_STORE, authoritative=True)
    registry = ProviderRegistry().extend([doc, store])
    assert registry.by_kind(ProviderKind.DOCUMENT) == (doc,)
    assert registry.authoritative() == (store,)
    assert list(registry) == list(registry.ordered())
    assert registry.to_dict()["count"] == 2


# ---------------------------------------------------------------------------
# protocol enforcement
# ---------------------------------------------------------------------------


def test_descriptor_validates_and_exposes_its_order_key():
    descriptor = ProviderDescriptor(
        provider_id="p", kind=ProviderKind.DOCUMENT, title="t", priority=7
    )
    assert descriptor.order_key == (7, "p")
    assert descriptor.to_dict()["priority"] == 7
    with pytest.raises(ProviderError):
        ProviderDescriptor(provider_id="  ", kind=ProviderKind.DOCUMENT, title="t")
    with pytest.raises(ProviderError):
        ProviderDescriptor(provider_id="p", kind="document", title="t")


def test_default_priority_is_the_documented_constant():
    descriptor = ProviderDescriptor(provider_id="p", kind=ProviderKind.DOCUMENT, title="t")
    assert descriptor.priority == DEFAULT_PRIORITY


def test_units_are_returned_in_key_order():
    provider = make_provider(
        "p",
        (
            make_unit("z", source=make_source(provider_id="p")),
            make_unit("a", source=make_source(provider_id="p")),
        ),
    )
    assert [u.key for u in provider.units()] == ["a", "z"]


def test_provider_id_shortcut_and_source_helper():
    provider = make_provider("p", ())
    assert provider.provider_id == "p"
    source = provider.source("loc", revision="r", content_sha256="c")
    assert source.provider_id == "p"
    assert source.kind is ProviderKind.DOCUMENT
    assert source.revision == "r"


def test_unit_citing_a_different_provider_is_rejected():
    bad = make_provider("p", (make_unit("u", source=make_source(provider_id="other")),))
    with pytest.raises(ProviderError):
        bad.units()


def test_duplicate_unit_key_within_a_provider_is_rejected():
    unit = make_unit("same", source=make_source(provider_id="p"))
    other = make_unit("same", statement="Different.", source=make_source(provider_id="p"))
    with pytest.raises(ProviderError):
        make_provider("p", (unit, other)).units()


def test_non_unit_and_non_iterable_returns_are_rejected():
    descriptor = ProviderDescriptor(provider_id="p", kind=ProviderKind.DOCUMENT, title="t")
    with pytest.raises(ProviderError):
        CallableProvider(descriptor, lambda: ["not a unit"]).units()
    with pytest.raises(ProviderError):
        CallableProvider(descriptor, lambda: 7).units()
    with pytest.raises(ProviderError):
        CallableProvider(descriptor, lambda: "a string is not units").units()


def test_a_failing_provider_is_reported_with_its_identity():
    descriptor = ProviderDescriptor(provider_id="broken", kind=ProviderKind.EXTERNAL, title="t")

    def explode():
        raise RuntimeError("upstream is down")

    with pytest.raises(ProviderError) as excinfo:
        CallableProvider(descriptor, explode).units()
    assert "broken" in str(excinfo.value)


def test_provider_error_from_provide_is_not_rewrapped():
    descriptor = ProviderDescriptor(provider_id="p", kind=ProviderKind.EXTERNAL, title="t")

    def explode():
        raise ProviderError("already typed", provider_id="p")

    with pytest.raises(ProviderError, match="already typed"):
        CallableProvider(descriptor, explode).units()


def test_callable_provider_requires_a_callable():
    descriptor = ProviderDescriptor(provider_id="p", kind=ProviderKind.EXTERNAL, title="t")
    with pytest.raises(ProviderError):
        CallableProvider(descriptor, "not callable")


def test_a_bare_function_is_a_sufficient_provider():
    """Contributing knowledge must not require defining a class."""
    descriptor = ProviderDescriptor(provider_id="fn", kind=ProviderKind.HUMAN, title="t")
    provider = CallableProvider(
        descriptor,
        lambda: [
            KnowledgeUnit(
                key="k",
                title="t",
                statement="s",
                source=SourceRef(provider_id="fn", kind=ProviderKind.HUMAN, locator="l"),
            )
        ],
    )
    assert isinstance(provider, KnowledgeProvider)
    assert len(provider.units()) == 1


# ---------------------------------------------------------------------------
# canonical store + decision log providers
# ---------------------------------------------------------------------------


def test_canonical_store_provider_projects_every_object(seed_base):
    provider = CanonicalStoreProvider(seed_base)
    units = provider.units()
    assert len(units) == len(seed_base.objects())
    assert provider.descriptor().authoritative
    assert provider.descriptor().priority == 0
    assert {u.key for u in units} == set(seed_base.object_ids())
    assert all(u.is_classified for u in units)


def test_canonical_store_units_cite_the_object_content_hash(seed_base):
    obj = seed_base.objects()[0]
    unit = next(u for u in CanonicalStoreProvider(seed_base).units() if u.key == obj.cko_id)
    assert unit.source.content_sha256 == obj.content_sha256
    assert unit.attribute("cko_id") == obj.cko_id


def test_canonical_store_provider_projects_the_link_topology(seed_base):
    units = {u.key: u for u in CanonicalStoreProvider(seed_base).units()}
    linked = [u for u in units.values() if u.relations]
    assert linked, "the seed corpus should declare at least one relationship"
    targets = {r.target for u in linked for r in u.relations}
    assert targets & set(seed_base.object_ids())


def test_custom_provider_id_is_honoured(seed_base):
    provider = CanonicalStoreProvider(seed_base, provider_id="my-store")
    assert provider.descriptor().provider_id == "my-store"
    assert all(u.source.provider_id == "my-store" for u in provider.units())


def test_decision_log_provider_projects_decisions(seed_base):
    provider = DecisionLogProvider(seed_base)
    units = provider.units()
    assert len(units) == len(seed_base.decisions())
    record = seed_base.decisions()[0]
    unit = next(u for u in units if u.key == record.decision_id)
    assert unit.statement == record.chosen_architecture
    assert unit.rationale == record.rationale
    assert unit.attribute("kind_hint") == "decision"
    assert unit.attribute("reviewable") == "true"


def test_decision_log_provider_declares_dependencies(seed_base):
    unit = DecisionLogProvider(seed_base).units()[0]
    assert unit.relations, "the seed decision declares dependencies"


def test_default_providers_are_the_two_authoritative_ones(seed_base):
    providers = default_providers(seed_base)
    assert len(providers) == 2
    assert all(p.descriptor().authoritative for p in providers)
    assert default_registry(seed_base).provider_ids() == (
        "ukda-canonical-store",
        "ukda-decision-log",
    )


# ---------------------------------------------------------------------------
# MappingProvider
# ---------------------------------------------------------------------------


def _descriptor(provider_id: str = "ext") -> ProviderDescriptor:
    return ProviderDescriptor(provider_id=provider_id, kind=ProviderKind.EXTERNAL, title="External")


def test_mapping_provider_synthesises_a_source_when_absent():
    provider = MappingProvider(
        _descriptor(), [{"key": "k", "title": "t", "statement": "A statement."}]
    )
    unit = provider.units()[0]
    assert unit.source.provider_id == "ext"
    assert unit.source.locator == "k"
    assert unit.source.content_sha256


def test_mapping_provider_completes_a_partial_source():
    provider = MappingProvider(
        _descriptor(),
        [{"key": "k", "title": "t", "statement": "s", "source": {"locator": "given/loc"}}],
    )
    unit = provider.units()[0]
    assert unit.source.locator == "given/loc"
    assert unit.source.provider_id == "ext"
    assert unit.source.kind is ProviderKind.EXTERNAL


def test_mapping_provider_reads_json_files(tmp_path):
    payload = {
        "units": [
            {
                "key": "k1",
                "title": "External knowledge",
                "statement": "An external statement.",
                "kind": "fact",
            }
        ]
    }
    path = tmp_path / "units.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    provider = MappingProvider.from_json_file(_descriptor(), path)
    units = provider.units()
    assert len(units) == 1
    assert units[0].kind is KnowledgeKind.FACT


def test_mapping_provider_json_failures_are_typed(tmp_path):
    with pytest.raises(ProviderError):
        MappingProvider.from_json_file(_descriptor(), tmp_path / "missing.json")

    bad = tmp_path / "bad.json"
    bad.write_text("{not json", encoding="utf-8")
    with pytest.raises(ProviderError):
        MappingProvider.from_json_file(_descriptor(), bad)

    not_object = tmp_path / "list.json"
    not_object.write_text("[]", encoding="utf-8")
    with pytest.raises(ProviderError):
        MappingProvider.from_json_file(_descriptor(), not_object)

    no_units = tmp_path / "no-units.json"
    no_units.write_text(json.dumps({"other": []}), encoding="utf-8")
    with pytest.raises(ProviderError):
        MappingProvider.from_json_file(_descriptor(), no_units)


# ---------------------------------------------------------------------------
# DocumentProvider
# ---------------------------------------------------------------------------


def _write(root, name: str, text: str):
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def test_document_provider_extracts_sections(tmp_path):
    _write(
        tmp_path,
        "guide.md",
        "# Title ignored\n\n"
        "## First Rule\nThe first rule body.\nStill the first body.\n\n"
        "### Nested Note\nA nested note body.\n",
    )
    provider = DocumentProvider(tmp_path)
    units = provider.units()
    assert provider.document_count == 1
    titles = {u.title for u in units}
    assert titles == {"First Rule", "Nested Note"}
    first = next(u for u in units if u.title == "First Rule")
    assert first.statement == "The first rule body. Still the first body."
    assert first.key == "guide.md#First Rule"
    assert first.attribute("document") == "guide.md"
    assert first.source.revision, "the file digest pins which version was read"
    assert first.source.excerpt.startswith("The first rule body.")


def test_document_provider_skips_headings_without_a_body(tmp_path):
    _write(tmp_path, "empty.md", "## Only A Heading\n\n## Another\nHas a body.\n")
    units = DocumentProvider(tmp_path).units()
    assert [u.title for u in units] == ["Another"]


def test_document_provider_ignores_h1_and_non_heading_hashes(tmp_path):
    _write(tmp_path, "d.md", "# Doc\nIntro text.\n\n#NotAHeading\n## Real\nBody.\n")
    units = DocumentProvider(tmp_path).units()
    assert [u.title for u in units] == ["Real"]


def test_document_provider_is_deterministic_across_files(tmp_path):
    _write(tmp_path, "b.md", "## B\nBody b.\n")
    _write(tmp_path, "a.md", "## A\nBody a.\n")
    provider = DocumentProvider(tmp_path)
    assert [u.key for u in provider.units()] == ["a.md#A", "b.md#B"]
    assert provider.units() == provider.units()


def test_document_provider_skips_oversized_files(tmp_path):
    _write(tmp_path, "huge.md", "## H\n" + ("x" * (MAX_DOCUMENT_BYTES + 10)))
    assert DocumentProvider(tmp_path).units() == ()


def test_document_provider_units_are_unclassified(tmp_path):
    """A document provider supplies substance; classification is a later stage."""
    _write(tmp_path, "d.md", "## Heading\nBody.\n")
    unit = DocumentProvider(tmp_path).units()[0]
    assert not unit.is_classified
    assert unit.kind is None


def test_document_provider_rejects_a_non_directory_root(tmp_path):
    path = _write(tmp_path, "file.md", "## H\nB.\n")
    with pytest.raises(ProviderError):
        DocumentProvider(path)


def test_document_provider_tolerates_undecodable_bytes(tmp_path):
    path = tmp_path / "binary.md"
    path.write_bytes(b"## Heading\n\xff\xfe body\n")
    units = DocumentProvider(tmp_path).units()
    assert len(units) == 1


# ---------------------------------------------------------------------------
# the arms an authoritative provider never takes
# ---------------------------------------------------------------------------


def test_a_provider_returning_something_that_is_not_iterable_at_all_is_rejected():
    """``CallableProvider`` cannot reach this arm and a custom provider can.

    ``CallableProvider.provide`` materialises its supplier's result, so a non-iterable
    fails inside ``provide`` and is reported as a provider FAILURE. A provider written by
    hand returns whatever it returns, and the contract check in ``units()`` is the only
    thing standing between that and ``tuple(7)`` raising a ``TypeError`` out of the
    registry — an error naming no provider, which is the one thing the wrapping exists to
    prevent.
    """

    class _Wrong(KnowledgeProvider):
        def descriptor(self) -> ProviderDescriptor:
            return ProviderDescriptor(provider_id="wrong", kind=ProviderKind.EXTERNAL, title="t")

        def provide(self):  # type: ignore[override]
            return 7

    with pytest.raises(ProviderError) as excinfo:
        _Wrong().units()
    assert excinfo.value.context["provider_id"] == "wrong"
    assert "iterable" in str(excinfo.value)


def test_a_provider_returning_a_string_is_rejected_before_it_is_iterated():
    """A string IS iterable, so without the explicit check it would be admitted as a
    sequence of one-character "units" and fail later with a message about characters."""

    class _Stringly(KnowledgeProvider):
        def descriptor(self) -> ProviderDescriptor:
            return ProviderDescriptor(provider_id="stringly", kind=ProviderKind.EXTERNAL, title="t")

        def provide(self):  # type: ignore[override]
            return "not units"

    with pytest.raises(ProviderError, match="iterable of knowledge units"):
        _Stringly().units()


def test_every_declared_link_on_an_object_becomes_a_relation(seed_base):
    """The seed corpus exercises three of the seven link kinds, so four projections were
    dead. A link a provider does not project is a relationship the graph cannot resolve,
    and UKIP's own law is that a relationship that cannot be resolved is not a relationship.
    """

    linked = make_cko(
        "UCKO-TEST-LINKS",
        parent="UCKO-TEST-PARENT",
        dependencies=("UCKO-TEST-DEP",),
        consumers=("UCKO-TEST-CONSUMER",),
        supersedes=("UCKO-TEST-OLD",),
        knowledge_links=("UCKO-TEST-RELATED",),
        conflicts_with=("UCKO-TEST-RIVAL",),
        decision_links=("UDR-TEST-0001",),
    )
    relations = CanonicalStoreProvider._relations(linked)
    by_type = {(r.relation, r.target): r.note for r in relations}

    assert by_type[(RelationType.EXTENDS, "UCKO-TEST-PARENT")] == "cko:parent"
    assert by_type[(RelationType.DEPENDS_ON, "UCKO-TEST-DEP")] == "cko:dependency"
    assert by_type[(RelationType.CONSUMES, "UCKO-TEST-CONSUMER")] == "cko:consumer"
    assert by_type[(RelationType.SUPERSEDES, "UCKO-TEST-OLD")] == "cko:supersedes"
    assert by_type[(RelationType.RELATED_TO, "UCKO-TEST-RELATED")] == "cko:knowledge-link"
    assert by_type[(RelationType.CONFLICTS_WITH, "UCKO-TEST-RIVAL")] == "cko:conflict"
    assert by_type[(RelationType.REFERENCES, "UDR-TEST-0001")] == "cko:decision-link"
    assert len(relations) == 7

    assert CanonicalStoreProvider._relations(make_cko("UCKO-TEST-BARE")) == ()


def test_a_decision_that_supersedes_another_declares_it(seed_base):
    """Supersession is the one relation a decision carries beyond its dependencies, and it
    is what makes the decision log a chain rather than a set."""

    superseding = make_decision(
        "UDR-TEST-0002", dependencies=("UCKO-TEST-DEP",), supersedes="UDR-TEST-0001"
    )
    relations = DecisionLogProvider._relations(superseding)
    assert (RelationType.SUPERSEDES, "UDR-TEST-0001") in {(r.relation, r.target) for r in relations}

    standalone = make_decision("UDR-TEST-0003", dependencies=("UCKO-TEST-DEP",))
    assert all(
        r.relation is not RelationType.SUPERSEDES
        for r in DecisionLogProvider._relations(standalone)
    )


def test_a_document_that_cannot_be_read_names_itself_in_the_failure(tmp_path):
    """One unreadable document must not fail anonymously.

    The provider is pointed at whole trees, so a path it collected and cannot open is a
    realistic state — and a ``PermissionError`` escaping with no provider id and no path
    would send the reader looking through the registry instead of at the file.
    """
    readable = tmp_path / "good.md"
    readable.write_text("## Heading\nBody.\n", encoding="utf-8")
    unreadable = tmp_path / "locked.md"
    unreadable.write_text("## Heading\nBody.\n", encoding="utf-8")
    unreadable.chmod(0o000)
    try:
        with pytest.raises(ProviderError) as excinfo:
            DocumentProvider(tmp_path).units()
        assert excinfo.value.context["path"] == str(unreadable)
        assert excinfo.value.context["provider_id"] == "repository-documents"
    finally:
        unreadable.chmod(0o644)
