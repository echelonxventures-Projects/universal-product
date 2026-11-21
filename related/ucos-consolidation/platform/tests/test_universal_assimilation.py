"""Tests — Universal Source Assimilation Framework (UCOS-USAF-001)."""

from __future__ import annotations

import io
import json
import zipfile
import zlib
from pathlib import Path
from platform.foundation.services import ServiceRegistry
from platform.universal_assimilation import (
    ASSIMILATION_CONTRACTS,
    KIND_API_RESPONSE,
    KIND_CONVERSATION_EXPORT,
    KIND_DOCUMENT_DOCX,
    KIND_DOCUMENT_PDF,
    KIND_MARKDOWN,
    KIND_PLAIN_TEXT,
    KIND_STRUCTURED_JSON,
    REASON_DESTINATION_NOT_HOME,
    REASON_NO_ADAPTER,
    REASON_NO_DECLARED_DESTINATION,
    REASON_NO_EXTRACTABLE_CONTENT,
    REASON_TRANSIENT_SOURCE,
    REASON_UNCLASSIFIED_SOURCE,
    AssimilationPipeline,
    AssimilationRecord,
    AssimilationReport,
    AssimilationState,
    AssimilationUnit,
    CallableAdapter,
    ConversationExportAdapter,
    DocxAdapter,
    JsonAdapter,
    PdfAdapter,
    RecordSetAdapter,
    SourceAdapterDescriptor,
    SourceAdapterRegistry,
    SourceInput,
    SourceKindDeclaration,
    SourceKindRegistry,
    SourceRef,
    TextAdapter,
    assimilation_contract_names,
    bootstrap_assimilation,
    default_adapter_registry,
    default_source_kind_registry,
    normalize_text,
    payload_digest,
    register_assimilation,
)
from platform.universal_assimilation.cli import main as assimilate_main
from platform.universal_assimilation.errors import (
    AdapterConflictError,
    AssimilationContractError,
    AssimilationPipelineError,
    SourceAdapterError,
    SourceKindError,
)
from platform.universal_truth import TruthClass, default_truth_policy

import pytest

CHATGPT = json.dumps(
    [
        {
            "id": "conv-1",
            "title": "Vision",
            "mapping": {
                "n2": {"message": {"author": {"role": "assistant"}, "content": {"parts": ["B"]}}},
                "n1": {"message": {"author": {"role": "user"}, "content": {"parts": ["A"]}}},
                "n3": {"message": None},
                "n4": "not-a-node",
            },
        }
    ]
)

CLAUDE = json.dumps(
    {
        "conversations": [
            {
                "uuid": "conv-2",
                "title": "Design",
                "chat_messages": [
                    {"sender": "human", "text": "question"},
                    {"sender": "assistant", "content": [{"type": "text", "text": "answer"}]},
                    "not-a-message",
                ],
            }
        ]
    }
)


def _docx(paragraphs: tuple[str, ...]) -> bytes:
    body = "".join(f"<w:p><w:r><w:t>{text}</w:t></w:r></w:p>" for text in paragraphs)
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("word/document.xml", f"<w:document><w:body>{body}</w:body></w:document>")
    return buffer.getvalue()


def _pdf(text: str, *, compress: bool = False) -> bytes:
    stream = f"BT ({text}) Tj ET".encode()
    if compress:
        stream = zlib.compress(stream)
    return b"%PDF-1.4\n4 0 obj\n<< >>\nstream\n" + stream + b"\nendstream\nendobj\n"


def _ref(kind: str, locator: str, payload: bytes = b"x") -> SourceRef:
    return SourceRef.from_payload(kind, locator, payload)


# --------------------------------------------------------------------------- vocabulary


def test_normalisation_and_digest() -> None:
    assert normalize_text("  a\n b  ") == "a b"
    assert payload_digest(b"abc").startswith("ba7816bf")
    with pytest.raises(AssimilationContractError):
        normalize_text(7)
    with pytest.raises(AssimilationContractError):
        payload_digest("abc")


def test_source_kind_registry_is_open_and_fail_closed() -> None:
    registry = default_source_kind_registry()
    assert registry.count == 14
    assert KIND_CONVERSATION_EXPORT in registry
    assert 7 not in registry
    declaration = registry.declare_kind("future-telemetry", description="not invented yet")
    assert registry.require("future-telemetry") is declaration
    assert registry.declare(declaration) is declaration
    assert "future-telemetry" in registry.ids()
    assert registry.get("missing") is None
    assert registry.to_dict()["kind_count"] == registry.count
    assert registry.fingerprint()
    with pytest.raises(SourceKindError):
        registry.require("undeclared")
    with pytest.raises(SourceKindError):
        registry.declare_kind("future-telemetry", description="changed")
    with pytest.raises(SourceKindError):
        registry.declare("nope")  # type: ignore[arg-type]
    with pytest.raises(SourceKindError):
        SourceKindDeclaration(" ")
    assert SourceKindRegistry().count == 0


def test_source_ref_and_unit_contracts() -> None:
    ref = SourceRef.from_payload(KIND_MARKDOWN, "./00-SOURCE/a.md", b"body", revision="r1")
    assert ref.locator == "00-SOURCE/a.md"
    assert ref.byte_size == 4
    assert ref.source_id.startswith("UCOS-USAS-")
    assert ref.fingerprint()
    with pytest.raises(AssimilationContractError):
        SourceRef.create(" ", "a.md")
    with pytest.raises(AssimilationContractError):
        SourceRef.create(KIND_MARKDOWN, "  ")

    unit = AssimilationUnit.create(ref.source_id, "k", "  text  ", title="T", sequence=2)
    assert unit.text == "text"
    assert unit.unit_id.startswith("UCOS-USAU-")
    assert unit.to_dict()["sequence"] == 2
    assert unit.fingerprint()
    with pytest.raises(AssimilationContractError):
        AssimilationUnit.create(" ", "k", "t")
    with pytest.raises(AssimilationContractError):
        AssimilationUnit.create(ref.source_id, " ", "t")
    with pytest.raises(AssimilationContractError):
        AssimilationUnit.create(ref.source_id, "k", "   ")


def test_state_machine_and_record_contracts() -> None:
    assert AssimilationState.ASSIMILATED.terminal is True
    assert AssimilationState.NORMALIZED.terminal is False
    ref = _ref(KIND_MARKDOWN, "00-SOURCE/a.md")
    with pytest.raises(AssimilationContractError):
        AssimilationRecord.create("nope", AssimilationState.DEFERRED)  # type: ignore[arg-type]
    with pytest.raises(AssimilationContractError):
        AssimilationRecord.create(ref, "deferred")  # type: ignore[arg-type]
    with pytest.raises(AssimilationContractError):
        AssimilationRecord.create(ref, AssimilationState.DEFERRED)
    with pytest.raises(AssimilationContractError):
        AssimilationRecord.create(ref, AssimilationState.ASSIMILATED)
    record = AssimilationRecord.create(
        ref, AssimilationState.ASSIMILATED, destination="./02-MASTER/a.md", owner="Authority"
    )
    assert record.destination == "02-MASTER/a.md"
    assert record.assimilated is True
    assert record.truth_class is TruthClass.UNCLASSIFIED
    assert record.record_id.startswith("UCOS-USAR-")
    assert record.fingerprint()


def test_report_views() -> None:
    ref_a = _ref(KIND_MARKDOWN, "00-SOURCE/a.md", b"a")
    ref_b = _ref(KIND_MARKDOWN, "00-SOURCE/b.md", b"b")
    report = AssimilationReport.create(
        [
            AssimilationRecord.create(
                ref_a, AssimilationState.ASSIMILATED, destination="02-MASTER/a.md"
            ),
            AssimilationRecord.create(
                ref_b,
                AssimilationState.NORMALIZED,
                truth_class=TruthClass.EVIDENCE,
                reasons=(REASON_NO_DECLARED_DESTINATION,),
            ),
        ]
    )
    assert report.total == 2
    assert report.coverage == 50.0
    assert report.closed is False
    assert [record.source.locator for record in report.outstanding()] == ["00-SOURCE/b.md"]
    assert report.of_reason(REASON_NO_DECLARED_DESTINATION)
    assert report.counts_by_state()["assimilated"] == 1
    assert report.counts_by_kind() == {KIND_MARKDOWN: 2}
    assert report.counts_by_truth_class()["evidence"] == 1
    assert report.by_reason()[REASON_NO_DECLARED_DESTINATION] == 1
    assert report.unit_total == 0
    assert report.report_id.startswith("UCOS-USAP-")
    assert report.fingerprint()
    assert report.to_dict()["closed"] is False
    assert AssimilationReport.create([]).closed is False
    assert AssimilationReport.create([]).coverage == 0.0


# --------------------------------------------------------------------------- adapters


def test_text_adapter_addresses_markdown_by_heading() -> None:
    adapter = TextAdapter()
    ref = _ref(KIND_MARKDOWN, "00-SOURCE/a.md")
    units = adapter.units(ref, b"preamble\n# One\nalpha\n## Two\nbeta")
    keys = [unit.key for unit in units]
    assert keys == [
        "00-SOURCE/a.md#preamble",
        "00-SOURCE/a.md#One",
        "00-SOURCE/a.md#Two",
    ]
    assert units[1].title == "One"


def test_text_adapter_emits_plain_text_as_one_unit() -> None:
    adapter = TextAdapter()
    ref = _ref(KIND_PLAIN_TEXT, "00-SOURCE/a.txt")
    assert len(adapter.units(ref, b"only body")) == 1
    assert adapter.units(ref, b"   ") == ()


def test_json_adapter_handles_every_document_shape() -> None:
    adapter = JsonAdapter()
    ref = _ref(KIND_STRUCTURED_JSON, "a.json")
    assert len(adapter.units(ref, b'{"b": 1, "a": 2}')) == 2
    assert len(adapter.units(ref, b"[1, 2, 3]")) == 3
    assert len(adapter.units(ref, b'"scalar"')) == 1
    with pytest.raises(SourceAdapterError):
        adapter.units(ref, b"{not json")


def test_conversation_adapter_reads_chatgpt_and_claude_shapes() -> None:
    adapter = ConversationExportAdapter()
    chatgpt = adapter.units(_ref(KIND_CONVERSATION_EXPORT, "c.json"), CHATGPT.encode())
    assert [unit.text for unit in chatgpt] == ["A", "B"]
    assert dict(chatgpt[0].attributes)["role"] == "user"
    assert chatgpt[0].title == "Vision"

    claude = adapter.units(_ref(KIND_CONVERSATION_EXPORT, "d.json"), CLAUDE.encode())
    assert [unit.text for unit in claude] == ["question", "answer"]
    assert dict(claude[1].attributes)["role"] == "assistant"

    generic = adapter.units(
        _ref(KIND_CONVERSATION_EXPORT, "e.json"),
        json.dumps({"id": "x", "messages": [{"role": "user", "content": "hi"}]}).encode(),
    )
    assert [unit.text for unit in generic] == ["hi"]
    assert adapter.units(_ref(KIND_CONVERSATION_EXPORT, "f.json"), b'"scalar"') == ()
    assert adapter.units(_ref(KIND_CONVERSATION_EXPORT, "g.json"), b'{"id": "x"}') == ()


def test_docx_adapter_reads_paragraphs_and_fails_closed() -> None:
    adapter = DocxAdapter()
    ref = _ref(KIND_DOCUMENT_DOCX, "00-SOURCE/a.docx")
    units = adapter.units(ref, _docx(("first", "  ", "second")))
    assert [unit.text for unit in units] == ["first", "second"]
    with pytest.raises(SourceAdapterError):
        adapter.units(ref, b"not a zip")


def test_pdf_adapter_recovers_text_or_honestly_reports_none() -> None:
    adapter = PdfAdapter()
    ref = _ref(KIND_DOCUMENT_PDF, "00-SOURCE/a.pdf")
    assert [unit.text for unit in adapter.units(ref, _pdf("Hello world"))] == ["Hello world"]
    assert [unit.text for unit in adapter.units(ref, _pdf("Deflated", compress=True))] == [
        "Deflated"
    ]
    assert adapter.units(ref, b"%PDF-1.4\nno streams here") == ()


def test_record_set_adapter_normalises_declared_schemas() -> None:
    adapter = RecordSetAdapter()
    ref = _ref(KIND_API_RESPONSE, "api/response.json")
    payload = json.dumps(
        {
            "records": [
                {"id": "r1", "body": "first", "title": "T"},
                {"id": "r2"},
                "not-a-record",
            ]
        }
    ).encode()
    units = adapter.units(ref, payload)
    assert [unit.key for unit in units] == ["api/response.json#r1"]
    assert units[0].title == "T"
    assert len(adapter.units(ref, b'[{"id": "r", "text": "t"}]')) == 1
    with pytest.raises(SourceAdapterError):
        adapter.units(ref, b'{"records": "nope"}')


def test_adapter_protocol_enforcement() -> None:
    descriptor = SourceAdapterDescriptor(adapter_id="a", kinds=(KIND_MARKDOWN,))
    ref = _ref(KIND_MARKDOWN, "a.md")

    good = CallableAdapter(
        descriptor,
        lambda source, payload: (AssimilationUnit.create(source.source_id, "k", "text"),),
    )
    assert good.units(ref, b"x")[0].key == "k"
    assert good.supports(ref) is True
    assert good.supports(_ref(KIND_PLAIN_TEXT, "a.txt")) is False

    with pytest.raises(SourceAdapterError):
        good.units("nope", b"x")  # type: ignore[arg-type]
    with pytest.raises(SourceAdapterError):
        good.units(_ref(KIND_PLAIN_TEXT, "a.txt"), b"x")

    exploding = CallableAdapter(descriptor, lambda source, payload: 1 / 0)
    with pytest.raises(SourceAdapterError):
        exploding.units(ref, b"x")

    wrong_type = CallableAdapter(descriptor, lambda source, payload: ("nope",))
    with pytest.raises(SourceAdapterError):
        wrong_type.units(ref, b"x")

    wrong_source = CallableAdapter(
        descriptor,
        lambda source, payload: (AssimilationUnit.create("UCOS-USAS-other", "k", "text"),),
    )
    with pytest.raises(SourceAdapterError):
        wrong_source.units(ref, b"x")

    with pytest.raises(SourceAdapterError):
        CallableAdapter("nope", lambda source, payload: ())  # type: ignore[arg-type]
    with pytest.raises(SourceAdapterError):
        CallableAdapter(descriptor, "nope")  # type: ignore[arg-type]
    with pytest.raises(SourceAdapterError):
        TextAdapter().units(ref, "not bytes")  # type: ignore[arg-type]


def test_adapter_descriptor_guards() -> None:
    with pytest.raises(SourceAdapterError):
        SourceAdapterDescriptor(adapter_id=" ", kinds=(KIND_MARKDOWN,))
    with pytest.raises(SourceAdapterError):
        SourceAdapterDescriptor(adapter_id="a", kinds=())
    with pytest.raises(SourceAdapterError):
        SourceAdapterDescriptor(
            adapter_id="a",
            kinds=(KIND_MARKDOWN,),
            precedence="high",  # type: ignore[arg-type]
        )
    descriptor = SourceAdapterDescriptor(adapter_id="a", kinds=(KIND_MARKDOWN,))
    assert descriptor.order_key == (-100, "a")
    assert descriptor.fingerprint()


def test_adapter_registry_ordering_and_conflicts() -> None:
    registry = default_adapter_registry()
    assert registry.count == 6
    first = registry.ordered()[0]
    assert first.descriptor().adapter_id == "assimilation.conversation-export"
    assert KIND_DOCUMENT_PDF in registry.kinds()
    assert registry.require("assimilation.pdf") is registry.get("assimilation.pdf")
    assert registry.add(first) is first
    assert registry.for_source(_ref(KIND_MARKDOWN, "a.md")) is not None
    assert registry.for_source(_ref("unadapted-kind", "a.x")) is None
    assert registry.to_dict()["adapter_count"] == 6
    assert registry.fingerprint()
    with pytest.raises(AdapterConflictError):
        registry.add(TextAdapter())
    with pytest.raises(SourceAdapterError):
        registry.add("nope")  # type: ignore[arg-type]
    with pytest.raises(SourceAdapterError):
        registry.require("missing")
    assert SourceAdapterRegistry().count == 0


# --------------------------------------------------------------------------- pipeline


def test_source_input_construction() -> None:
    source = SourceInput.from_text(KIND_MARKDOWN, "00-SOURCE/a.md", "body", revision="r")
    assert source.source_ref().revision == "r"
    with pytest.raises(AssimilationPipelineError):
        SourceInput.create(KIND_MARKDOWN, "a.md", "not bytes")  # type: ignore[arg-type]


def test_pipeline_terminal_states_are_named_and_honest() -> None:
    pipeline = bootstrap_assimilation()
    report = pipeline.assimilate(
        [
            SourceInput.from_text(KIND_MARKDOWN, "00-SOURCE/homed.md", "# H\nbody"),
            SourceInput.from_text(KIND_MARKDOWN, "00-SOURCE/unhomed.md", "# H\nbody"),
            SourceInput.from_text(KIND_MARKDOWN, "00-SOURCE/misplaced.md", "# H\nbody"),
            SourceInput.from_text(KIND_MARKDOWN, "00-SOURCE/empty.md", "   "),
            SourceInput.from_text("unadapted-kind", "00-SOURCE/x.zzz", "body"),
            SourceInput.from_text(KIND_MARKDOWN, "platform/__pycache__/x.md", "body"),
            SourceInput.from_text(KIND_MARKDOWN, "nowhere/x.md", "# H\nbody"),
        ],
        destinations={
            "00-SOURCE/homed.md": "02-MASTER/UCOS-HOMED.md",
            "00-SOURCE/misplaced.md": "00-MASTER/programme/x.md",
            "nowhere/x.md": "02-MASTER/UCOS-ELSEWHERE.md",
        },
    )
    states = {record.source.locator: record.state for record in report.records}
    reasons = {record.source.locator: record.reasons for record in report.records}
    assert states["00-SOURCE/homed.md"] is AssimilationState.ASSIMILATED
    assert states["00-SOURCE/unhomed.md"] is AssimilationState.NORMALIZED
    assert reasons["00-SOURCE/unhomed.md"] == (REASON_NO_DECLARED_DESTINATION,)
    assert states["00-SOURCE/misplaced.md"] is AssimilationState.ADMITTED
    assert reasons["00-SOURCE/misplaced.md"] == (REASON_DESTINATION_NOT_HOME,)
    assert reasons["00-SOURCE/empty.md"] == (REASON_NO_EXTRACTABLE_CONTENT,)
    assert reasons["00-SOURCE/x.zzz"] == (REASON_NO_ADAPTER,)
    assert states["platform/__pycache__/x.md"] is AssimilationState.REJECTED
    assert reasons["platform/__pycache__/x.md"] == (REASON_TRANSIENT_SOURCE,)
    assert REASON_UNCLASSIFIED_SOURCE in reasons["nowhere/x.md"]
    assert report.unit_total >= 4


def test_pipeline_honours_per_source_destinations_and_no_policy_mode() -> None:
    pipeline = AssimilationPipeline(default_adapter_registry())
    assert pipeline.policy is None
    report = pipeline.assimilate(
        [
            SourceInput.from_text(
                KIND_MARKDOWN, "anywhere/a.md", "# H\nbody", destination="anywhere/b.md"
            )
        ]
    )
    assert report.closed is True
    assert pipeline.to_dict()["policy"] == ""
    assert pipeline.fingerprint()


def test_pipeline_can_accept_undeclared_kinds_when_declared_to() -> None:
    permissive = AssimilationPipeline(
        SourceAdapterRegistry([TextAdapter(adapter_id="assimilation.any", kinds=("future-kind",))]),
        policy=default_truth_policy(),
        require_declared_kind=False,
    )
    report = permissive.assimilate(
        [
            SourceInput.from_text(
                "future-kind", "00-SOURCE/a.future", "body", destination="02-MASTER/a.md"
            )
        ]
    )
    assert report.closed is True


def test_pipeline_construction_guards() -> None:
    with pytest.raises(AssimilationPipelineError):
        AssimilationPipeline("nope")  # type: ignore[arg-type]
    with pytest.raises(AssimilationPipelineError):
        AssimilationPipeline(default_adapter_registry(), policy="nope")  # type: ignore[arg-type]
    pipeline = bootstrap_assimilation()
    with pytest.raises(AssimilationPipelineError):
        pipeline.assimilate_source("nope")  # type: ignore[arg-type]
    assert pipeline.kinds.count == 14
    assert pipeline.adapters.count == 6


def test_outcome_projection() -> None:
    pipeline = bootstrap_assimilation()
    outcome = pipeline.assimilate_source(
        SourceInput.from_text(KIND_MARKDOWN, "00-SOURCE/a.md", "# H\nbody"),
        destination="02-MASTER/a.md",
    )
    payload = outcome.to_dict()
    assert payload["record"]["state"] == "assimilated"
    assert payload["units"]


# --------------------------------------------------------------------------- wiring


def test_contract_surface_is_published() -> None:
    assert assimilation_contract_names()
    assert len(ASSIMILATION_CONTRACTS) == len(assimilation_contract_names())


def test_service_registration() -> None:
    registry = ServiceRegistry()
    descriptor = register_assimilation(registry)
    assert descriptor.name == "universal.assimilation"
    assert isinstance(registry.resolve("universal.assimilation"), AssimilationPipeline)


# --------------------------------------------------------------------------- cli


def test_cli_kinds_and_adapters(capsys: pytest.CaptureFixture[str]) -> None:
    assert assimilate_main(["kinds", "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["kind_count"] == 14
    assert assimilate_main(["adapters", "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["adapter_count"] == 6


def test_cli_run_over_a_declared_manifest(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (tmp_path / "00-SOURCE").mkdir()
    (tmp_path / "00-SOURCE" / "a.md").write_text("# H\nbody", "utf-8")
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "sources": [{"kind": KIND_MARKDOWN, "locator": "00-SOURCE/a.md"}],
                "destinations": {"00-SOURCE/a.md": "02-MASTER/a.md"},
            }
        ),
        "utf-8",
    )
    assert (
        assimilate_main(["run", "--manifest", str(manifest), "--root", str(tmp_path), "--json"])
        == 0
    )
    payload = json.loads(capsys.readouterr().out)
    assert payload["closed"] is True

    unhomed = tmp_path / "unhomed.json"
    unhomed.write_text(
        json.dumps({"sources": [{"kind": KIND_MARKDOWN, "locator": "00-SOURCE/a.md"}]}), "utf-8"
    )
    assert (
        assimilate_main(["run", "--manifest", str(unhomed), "--root", str(tmp_path), "--gate"]) == 1
    )


def test_cli_run_over_a_declared_locator_list(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (tmp_path / "00-SOURCE").mkdir()
    (tmp_path / "00-SOURCE" / "a.docx").write_bytes(_docx(("body",)))
    listing = tmp_path / "SOURCE-FILES.txt"
    listing.write_text("00-SOURCE/a.docx\n\n", "utf-8")
    assert (
        assimilate_main(
            [
                "run",
                "--sources-file",
                str(listing),
                "--kind",
                KIND_DOCUMENT_DOCX,
                "--root",
                str(tmp_path),
                "--json",
            ]
        )
        == 0
    )
    payload = json.loads(capsys.readouterr().out)
    assert payload["total"] == 1
    assert payload["by_reason"] == {REASON_NO_DECLARED_DESTINATION: 1}
    assert assimilate_main(["run", "--sources-file", str(listing), "--root", str(tmp_path)]) == 2


def test_cli_manifest_faults(tmp_path: Path) -> None:
    assert assimilate_main(["run"]) == 2
    assert assimilate_main(["run", "--manifest", str(tmp_path / "missing.json")]) == 2
    for body in (
        "[]",
        json.dumps({"sources": {}}),
        json.dumps({"sources": ["nope"]}),
        json.dumps({"sources": [{"kind": KIND_MARKDOWN}]}),
        json.dumps({"sources": [{"kind": KIND_MARKDOWN, "locator": "missing.md"}]}),
        json.dumps({"sources": [], "destinations": []}),
    ):
        manifest = tmp_path / "manifest.json"
        manifest.write_text(body, "utf-8")
        assert assimilate_main(["run", "--manifest", str(manifest), "--root", str(tmp_path)]) == 2


# --------------------------------------------------------------------------- the skipped arms
#
# Every adapter case above supplies a payload that yields text, is small, and is shaped the way
# its format's documents usually are. The arms below answer for the rest — a payload too large
# to decode, a member that normalises to nothing, and content nested in a shape the extractor
# has to walk rather than read.


def test_a_payload_larger_than_the_decodable_limit_is_refused(monkeypatch) -> None:
    """A LIMIT NOBODY HAS CROSSED IS A LIMIT NOBODY HAS CHECKED.

    Both refusals guard the same thing from two directions: text decoding materialises the
    whole payload as a string, and PDF extraction scans the whole byte string with a regular
    expression — so an unbounded input is a memory fault inside a framework whose contract is
    to REPORT what it cannot assimilate. The limit is patched down rather than a 64 MB payload
    built, because the size is a declared constant and constructing one to cross it would make
    the suite slower for no additional evidence.
    """
    monkeypatch.setattr("platform.universal_assimilation.adapters.MAX_PAYLOAD_BYTES", 8)

    with pytest.raises(SourceAdapterError, match="payload exceeds the decodable limit"):
        TextAdapter().units(_ref(KIND_PLAIN_TEXT, "00-SOURCE/big.txt"), b"far too many bytes")

    with pytest.raises(SourceAdapterError, match="pdf payload exceeds the decodable limit"):
        PdfAdapter().units(_ref(KIND_DOCUMENT_PDF, "00-SOURCE/big.pdf"), _pdf("hello"))


def test_a_member_that_normalises_to_nothing_yields_no_unit() -> None:
    """AN EMPTY UNIT IS A CITATION TO NOTHING.

    Two extractors skip a member whose normalised body is empty and neither skip had a case,
    because every fixture here carries text in every member. A message with no content and a
    PDF stream holding no recoverable text are both ordinary; emitting a unit for one would
    put an addressable, digestible record into the corpus whose body is the empty string —
    indistinguishable from every other empty member, and citable as though it said something.
    """
    conversation = ConversationExportAdapter().units(
        _ref(KIND_CONVERSATION_EXPORT, "00-SOURCE/c.json"),
        json.dumps(
            [
                {
                    "id": "c1",
                    "title": "T",
                    "messages": [
                        {"role": "user", "content": "a real message"},
                        {"role": "assistant", "content": "   "},
                    ],
                }
            ]
        ).encode(),
    )
    assert [unit.text for unit in conversation] == ["a real message"]

    empty_stream = PdfAdapter().units(
        _ref(KIND_DOCUMENT_PDF, "00-SOURCE/blank.pdf"),
        b"%PDF-1.4\nstream\n\nendstream\n" + _pdf("real text"),
    )
    assert [unit.text for unit in empty_stream] == ["real text"]


def test_a_json_member_that_renders_to_nothing_is_skipped_too(monkeypatch) -> None:
    """THE SAME SKIP, IN THE ONE EXTRACTOR WHERE IT CANNOT FIRE TODAY.

    A JSON member's body is ``json.dumps`` of its value, which renders SOMETHING for every
    value there is — ``null``, ``""``, ``0`` — so no document can reach this guard. It is the
    second defence for the day the rendering changes: without it a member rendering to nothing
    would enter the corpus as an addressable unit with an empty body, which is the same defect
    the other two extractors refuse. Reached by making the normalisation answer empty, which
    is the only condition it responds to.
    """
    real = normalize_text
    monkeypatch.setattr(
        "platform.universal_assimilation.adapters.normalize_text",
        lambda text: "" if "skipped" in text else real(text),
    )

    units = JsonAdapter().units(
        _ref(KIND_STRUCTURED_JSON, "00-SOURCE/mixed.json"),
        json.dumps({"kept": "content", "gone": "skipped"}).encode(),
    )

    assert [unit.title for unit in units] == ["kept"]


def test_message_content_is_walked_through_every_shape_an_export_uses() -> None:
    """AN EXPORT NESTS ITS TEXT DIFFERENTLY IN EVERY VERSION, and the walker is why.

    The tested exports carry a plain string or a ``parts`` list. The remaining shapes had no
    case: a mapping keyed under one of the declared field names, a mapping keyed under none of
    them, a bare list, an absent content, and a scalar that is not a string. Each is a real
    export shape, and the two ``return ""`` arms are what stop an unknown one from being
    rendered as its Python repr — ``{'kind': 'image'}`` assimilated as text is a unit that
    reads as content and is not.
    """
    walk = ConversationExportAdapter._content_text

    assert walk(None) == ""
    assert walk("plain") == "plain"
    assert walk({"parts": ["a", "b"]}) == "a b"
    assert walk({"value": "under a declared key"}) == "under a declared key"
    assert walk({"kind": "image", "url": "..."}) == ""
    assert walk(["a", {"text": "b"}]) == "a b"
    assert walk(7) == "7"


def test_a_source_no_adapter_claims_is_deferred_rather_than_dropped() -> None:
    """A KIND MAY BE DECLARED AND STILL HAVE NOTHING THAT CAN READ IT.

    The undeclared-kind refusal above it was tested; this is the arm underneath, reached only
    when the kind IS admitted and no registered adapter claims the source. It is the state a
    repository is in the moment it declares a new kind and before it writes the adapter — and
    DEFERRED is the honest answer, because the source is neither assimilated nor refused. A
    silent drop would let a declared kind accumulate sources nothing ever reads.
    """
    permissive = AssimilationPipeline(
        SourceAdapterRegistry(
            [TextAdapter(adapter_id="assimilation.text", kinds=(KIND_MARKDOWN,))]
        ),
        policy=default_truth_policy(),
        require_declared_kind=False,
    )

    report = permissive.assimilate(
        [
            SourceInput.from_text(
                "a-kind-no-adapter-claims",
                "00-SOURCE/a.unknown",
                "body",
                destination="02-MASTER/a.md",
            )
        ]
    )

    assert report.closed is False
    record = report.records[0]
    assert record.state is AssimilationState.DEFERRED
    assert record.reasons == (REASON_NO_ADAPTER,)
