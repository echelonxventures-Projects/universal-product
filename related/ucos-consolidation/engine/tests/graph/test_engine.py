"""Unit tests for engine.graph.engine — the core graph builder."""

from __future__ import annotations

from engine.graph.engine import (
    _envelope_field,
    _read_optional,
    build_core_graph,
    load_certification,
    load_signals,
    load_twin,
)
from engine.graph.model import KIND_ARTIFACT, KIND_VOLUME
from engine.registry.adapter import RegistryAdapter
from engine.registry.errors import RegistryError


def test_build_core_graph_nodes_and_edges(core):
    # 7 artifacts + 4 volumes = 11 nodes
    assert len(core.nodes_of_kind(KIND_ARTIFACT)) == 7
    assert len(core.nodes_of_kind(KIND_VOLUME)) == 4
    assert core.order() == 11
    # every relationship becomes an edge
    assert core.size() > 0
    book = core.node("UCOS-BOOK-000000")
    assert book.kind == KIND_ARTIFACT
    assert book.attributes["category"] == "BOOK"


def test_core_graph_is_version_aware(core):
    node = core.node("UCOS-REG-000001")
    assert node.version == "1.0.0"
    assert node.attributes["status"] == "CERTIFIED"
    # traceability projection retained on artifact nodes
    arch = core.node("UCOS-ARCH-000001")
    assert arch.attributes["traceability"]["requirement"] == ("UCOS-CON-000001",)


def test_core_graph_provenance(core):
    prov = core.provenance
    assert prov.generated_at == "2026-07-16T00:00:00+00:00"
    assert prov.generator_version == "test-1.0"
    assert prov.artifact_count == 7
    assert prov.volume_count == 4


def test_build_is_idempotent(registry):
    a = build_core_graph(registry)
    b = build_core_graph(registry)
    assert a.node_ids() == b.node_ids()
    assert [e.edge_id for e in a.edges()] == [e.edge_id for e in b.edges()]


def test_load_auxiliary_documents(registry):
    signals = load_signals(registry)
    assert len(signals) == 5
    cert = load_certification(registry)
    assert cert["verdict"] == "CERTIFIED"
    twin = load_twin(registry)
    assert "build" in twin["dimensions"]


def test_load_auxiliary_absent_is_empty(minimal_data_dir):
    registry = RegistryAdapter.open(minimal_data_dir)
    assert load_signals(registry) == ()
    assert load_certification(registry) == {}
    assert load_twin(registry) == {}
    # core graph still builds without the optional documents
    core = build_core_graph(registry)
    assert core.order() == 11


def test_a_registry_document_of_the_wrong_shape_reads_as_absent(tmp_path):
    """AUXILIARY DOCUMENTS ARE BEST-EFFORT, and there are two ways they can be unusable.

    A file the registry refuses to read is one; a file that parses as JSON and is not an
    object is the other. Both mean "no auxiliary content", and returning the parsed value
    anyway would hand a list or a string to code expecting a mapping — an AttributeError
    somewhere downstream naming the consumer rather than the malformed document.
    """

    class _Shapeless:
        @staticmethod
        def exists(_filename: str) -> bool:
            return True

        @staticmethod
        def read_json(_filename: str):
            return ["not", "a", "mapping"]

    class _Adapter:
        source = _Shapeless()

    assert _read_optional(_Adapter(), "anything.json") == {}


def test_a_registry_document_that_cannot_be_read_reads_as_absent():
    """The other half: the registry itself refuses. A graph built over a corpus missing an
    optional document must still build, because the document is optional — raising would make
    every auxiliary file mandatory in practice while being declared optional in the code."""

    class _Refusing:
        @staticmethod
        def exists(_filename: str) -> bool:
            return True

        @staticmethod
        def read_json(_filename: str):
            raise RegistryError("the document could not be read")

    class _Adapter:
        source = _Refusing()

    assert _read_optional(_Adapter(), "anything.json") == {}


def test_a_registry_envelope_that_is_not_an_object_yields_no_metadata():
    """METADATA IS A TOP-LEVEL FIELD OF AN ENVELOPE, and a document that is not an object has
    no top level to read. Returning ``""`` is what keeps the read best-effort: a corpus whose
    envelope is a list still builds a graph, with the metadata simply unstated rather than
    the build failing over a field nobody depends on."""

    class _Listy:
        @staticmethod
        def read_json(_filename: str):
            return ["not", "an", "envelope"]

    class _Adapter:
        source = _Listy()

    assert _envelope_field(_Adapter(), "anything.json", "generated_at") == ""

    class _Envelope:
        @staticmethod
        def read_json(_filename: str):
            return {"generated_at": "2026-01-01", "count": 3}

    class _Good:
        source = _Envelope()

    assert _envelope_field(_Good(), "anything.json", "generated_at") == "2026-01-01"
    assert (
        _envelope_field(_Good(), "anything.json", "count") == ""
    ), "a non-string field is not metadata"
