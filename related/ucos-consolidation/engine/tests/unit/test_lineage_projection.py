"""ULP — the Universal Lineage Projection, measured.

Lineage answers "how did this become this?". These tests hold the four properties that make
a derived answer trustworthy — it is composed rather than stored, it is deterministic, each
family keeps its own meaning, and every answer cites its source — and they exercise the
refusals that make those properties non-vacuous.

The F-1 failure pattern is reconstructed here too: a projected structural ancestor that is
not the declared parent must fail, at the projection layer as well as at `ukb validate`.
"""

from __future__ import annotations

import ast
import dataclasses
import json
import os
import pathlib
import re
import subprocess

import pytest

from engine.lineage import query
from engine.lineage.model import Classification, LineageEdge, LineageError, LineageProjection
from engine.lineage.projection import (
    _relation_named,
    build,
    digest,
    load_classification,
    rendered,
    to_document,
    validate,
    verify,
)
from engine.lineage.sources import (
    SOURCE_FILES,
    declared_relations,
    load_sources,
    repo_root,
)


@pytest.fixture(scope="module", name="projection")
def _projection() -> LineageProjection:
    return build()


@pytest.fixture(scope="module", name="classification")
def _classification() -> Classification:
    return load_classification()


@pytest.fixture(name="document")
def _document() -> dict:
    with open(
        os.path.join(repo_root(), "engine", "lineage", "families.json"), encoding="utf-8"
    ) as h:
        return json.load(h)


# --- composition, not storage -----------------------------------------------------------


def test_the_projection_builds_over_every_declared_source(projection) -> None:
    assert set(projection.sources) == {
        "artifacts",
        "births",
        "change_events",
        "change_lineage",
        "generated",
        "identity_history",
        "typed_edges",
    }
    assert all(count > 0 for count in projection.sources.values())


def test_every_declared_source_file_exists() -> None:
    missing = [p for p in SOURCE_FILES if not os.path.exists(os.path.join(repo_root(), p))]
    assert missing == []


def test_the_projection_writes_nothing(tmp_path) -> None:
    """A lineage store is what UCI-001 XVI.5 forbids."""

    before = subprocess.run(  # noqa: S603
        ["git", "status", "--porcelain"],  # noqa: S607
        cwd=repo_root(),
        capture_output=True,
        text=True,
        check=False,
    ).stdout
    build()
    verify()
    after = subprocess.run(  # noqa: S603
        ["git", "status", "--porcelain"],  # noqa: S607
        cwd=repo_root(),
        capture_output=True,
        text=True,
        check=False,
    ).stdout
    assert before == after, "building the projection moved something in the tree"


def test_the_document_claims_no_authority(projection) -> None:
    assert to_document(projection)["authority"].startswith("NONE")


def test_the_document_stays_open(projection) -> None:
    document = to_document(projection)
    assert document["closed_set"] is False
    assert document["upper_limit"] is None


# --- determinism ------------------------------------------------------------------------


def test_two_builds_are_byte_identical() -> None:
    assert rendered(build()) == rendered(build())


def test_the_digest_is_stable_across_builds() -> None:
    assert digest(build()) == digest(build())


def test_verify_reports_determinism_and_passes() -> None:
    report = verify()
    assert report["deterministic"] is True
    assert report["status"] == "PASS", report["problems"]
    assert report["problems"] == []


def test_no_wall_clock_enters_the_document(projection) -> None:
    """A timestamp would make two builds of one state differ."""

    document = to_document(projection)
    document.pop("edges")
    assert re.findall(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}", json.dumps(document)) == []


# --- the four families keep distinct meanings -------------------------------------------


def test_the_four_lineage_families_are_populated(projection) -> None:
    counts = projection.by_family()
    assert set(counts) == {"structure", "dependency", "derivation", "supersession"}
    assert all(count > 0 for count in counts.values())


def test_structural_edges_equal_the_declared_containment_facts(projection) -> None:
    """One containment fact, one edge — not one per direction."""
    sources = load_sources()
    declared = sum(1 for a in sources["artifacts"] if a.get("parent"))
    assert projection.by_family()["structure"] == declared


def test_each_relation_belongs_to_exactly_one_family(classification) -> None:
    seen: dict[str, str] = {}
    for family in classification.families:
        for rule in family.relations:
            assert rule.relation not in seen, f"{rule.relation} in two families"
            seen[rule.relation] = family.name


def test_transformation_is_events_and_never_edges(projection) -> None:
    """The meaning-collapse the architecture forbids (P-2)."""
    assert "transformation" not in projection.by_family()
    assert projection.events, "the event stream is empty"
    assert all(isinstance(e.sequence, int) for e in projection.events)


def test_derivation_comes_from_the_generated_artifact_registry(projection) -> None:
    sources = {e.source for e in projection.edges if e.family == "derivation"}
    assert sources == {"00-BOOK/DATA/generated-artifact-registry.json"}


def test_supersession_comes_from_the_change_ledger_and_the_typed_graph(projection) -> None:
    sources = {e.source for e in projection.edges if e.family == "supersession"}
    assert "00-BOOK/DATA/change-ledger.json" in sources


# --- every edge cites its source ---------------------------------------------------------


def test_every_edge_names_a_declared_source(projection) -> None:
    allowed = set(SOURCE_FILES)
    assert {e.source for e in projection.edges} <= allowed


def test_every_edge_relation_is_declared_by_the_vocabulary_owner(projection) -> None:
    declared = declared_relations()
    assert {e.relation for e in projection.edges} <= declared


def test_within_one_source_a_fact_is_carried_once(projection) -> None:
    """One source states one ancestry fact with one relation — the inverse is collapsed."""
    facts: dict[tuple[str, str, str, str], set[str]] = {}
    for edge in projection.edges:
        key = (edge.family, edge.descendant, edge.ancestor, edge.source)
        facts.setdefault(key, set()).add(edge.relation)
    doubled = {k: v for k, v in facts.items() if len(v) > 1}
    assert doubled == {}, f"one source carried a fact under two relations: {doubled}"


def test_two_sources_may_attest_one_fact_and_each_cites_itself(projection) -> None:
    """Multi-source attestation is kept, not collapsed — and it is measured, not assumed.

    The change ledger records `UCOS-UMB-000024` as SUPERSEDING `…000023`; the typed graph
    records the same pair as EVOLVES-FROM. Two governed sources describing one ancestry in
    their own vocabulary is not duplication, and silently dropping one would discard an
    attestation the repository actually holds. Each edge names the source that made it, so
    a caller can tell the two apart.
    """
    facts: dict[tuple[str, str, str], set[str]] = {}
    for edge in projection.edges:
        facts.setdefault((edge.family, edge.descendant, edge.ancestor), set()).add(edge.source)
    multi = {k: v for k, v in facts.items() if len(v) > 1}
    assert multi, "expected at least one multi-source ancestry attestation"
    for key, sources in multi.items():
        assert len(sources) == len(set(sources)), key


# --- the query surface -------------------------------------------------------------------


def test_the_query_answers_the_six_questions(projection) -> None:
    sources = load_sources()
    node = next(iter(sorted(sources["artifacts_by_id"])))
    answer = query.answer(node, projection)
    assert set(answer) == {
        "node",
        "what_is_this",
        "who_owns_this",
        "where_did_it_come_from",
        "when_was_it_created",
        "what_has_it_become",
        "what_depends_on_it",
    }


def test_every_origin_answer_cites_its_source(projection) -> None:
    sources = load_sources()
    subject = next(e.descendant for e in projection.edges if e.family == "structure")
    for found in query.origin_of(subject, projection, sources):
        assert found["source"], "an answer without a source is not returned"
        assert found["family"]


def test_an_unknown_node_answers_empty_rather_than_guessing(projection) -> None:
    answer = query.answer("UCOS-NOT-A-REAL-ID", projection)
    assert answer["what_is_this"] == {}
    assert answer["who_owns_this"] == {}
    assert answer["where_did_it_come_from"] == []


# --- refusals ----------------------------------------------------------------------------


def test_the_f1_pattern_is_refused_by_the_projection(projection) -> None:
    """A structural ancestor that is not the declared parent must fail."""
    sources = load_sources()
    subject = next(e.descendant for e in projection.edges if e.family == "structure")
    forged = dataclasses.replace(
        projection,
        edges=(
            *projection.edges,
            LineageEdge(
                descendant=subject,
                ancestor="UCOS-USIS-000017",
                relation="Parent",
                family="structure",
                source="00-BOOK/DATA/relationships.json",
            ),
        ),
    )
    problems = validate(forged)
    assert any("is not the declared parent" in p for p in problems)
    assert any("conflicting structural ancestry" in p for p in problems)
    del sources


def test_a_cycle_in_an_acyclic_family_is_refused(projection) -> None:
    forged = dataclasses.replace(
        projection,
        edges=(
            LineageEdge("A", "B", "Depends-On", "dependency", "00-BOOK/DATA/relationships.json"),
            LineageEdge("B", "A", "Depends-On", "dependency", "00-BOOK/DATA/relationships.json"),
        ),
    )
    assert any("not acyclic" in p for p in validate(forged))


def test_an_undeclared_relation_is_refused(projection) -> None:
    forged = dataclasses.replace(
        projection,
        edges=(
            LineageEdge(
                "A", "B", "Invented-Relation", "dependency", "00-BOOK/DATA/relationships.json"
            ),
        ),
    )
    assert any("is not a declared relation" in p for p in validate(forged))


# --- the classification refuses an unusable declaration ----------------------------------


def test_a_relation_the_owner_does_not_declare_is_refused(tmp_path, document) -> None:
    document["families"][0]["types"].append({"type": "Invented-Relation", "ancestor": "to"})
    path = tmp_path / "families.json"
    path.write_text(json.dumps(document), encoding="utf-8")
    with pytest.raises(LineageError, match="does not declare|do not declare"):
        load_classification(str(path))


def test_leaving_a_declared_relation_unclassified_is_refused(tmp_path, document) -> None:
    document["non_lineage"] = document["non_lineage"][:-1]
    path = tmp_path / "families.json"
    path.write_text(json.dumps(document), encoding="utf-8")
    with pytest.raises(LineageError, match="neither as lineage nor"):
        load_classification(str(path))


def test_a_relation_classified_twice_is_refused(document) -> None:
    document["families"][1]["types"].append(document["families"][0]["types"][0])
    with pytest.raises(LineageError, match="two families"):
        Classification.of(document)


def test_a_relation_both_lineage_and_non_lineage_is_refused(document) -> None:
    document["non_lineage"].append(
        {"type": document["families"][0]["types"][0]["type"], "reason": "claimed twice"}
    )
    with pytest.raises(LineageError, match="both lineage and non-lineage"):
        Classification.of(document)


# --- an exclusion argues itself, or it is not an exclusion --------------------------------
#
# Listing a relation as non-lineage stops it being silently ignored, but a bare name leaves the
# exclusion asserted rather than measured — and an unexplained exclusion is indistinguishable
# from an oversight to every later reader. These three make the reason load-bearing.


def test_a_non_lineage_relation_named_without_a_reason_is_refused(document) -> None:
    document["non_lineage"][0] = {"type": document["non_lineage"][0]["type"]}
    with pytest.raises(LineageError, match="reason"):
        Classification.of(document)


def test_a_bare_relation_name_is_not_an_exclusion(document) -> None:
    document["non_lineage"][0] = document["non_lineage"][0]["type"]
    with pytest.raises(LineageError, match="not a bare name"):
        Classification.of(document)


def test_the_same_relation_excluded_twice_is_refused(document) -> None:
    document["non_lineage"].append(dict(document["non_lineage"][0]))
    with pytest.raises(LineageError, match="more than once"):
        Classification.of(document)


def test_every_excluded_relation_carries_its_reason(classification) -> None:
    """The live classification, not a fixture: each exclusion says why it is not ancestry."""
    assert set(classification.exclusions) == set(classification.non_lineage)
    assert all(len(reason) > 40 for reason in classification.exclusions.values())


def test_an_unknown_ancestor_direction_is_refused(document) -> None:
    document["families"][0]["types"][0]["ancestor"] = "sideways"
    with pytest.raises(LineageError, match="edge endpoint"):
        Classification.of(document)


def test_a_missing_section_is_refused(document) -> None:
    document.pop("families")
    with pytest.raises(LineageError):
        Classification.of(document)


def test_a_missing_classification_file_is_a_fault(tmp_path) -> None:
    with pytest.raises(LineageError, match="absent"):
        load_classification(str(tmp_path / "nope.json"))


def test_an_unparseable_classification_is_a_fault(tmp_path) -> None:
    path = tmp_path / "families.json"
    path.write_text("{ not json", encoding="utf-8")
    with pytest.raises(LineageError, match="valid JSON"):
        load_classification(str(path))


# --- no hard-coded reality ----------------------------------------------------------------


def test_the_classification_is_data_not_code(classification) -> None:
    """Family and relation names live in families.json, checked against the owner."""

    source = (pathlib.Path(repo_root()) / "engine" / "lineage" / "model.py").read_text("utf-8")
    tree = ast.parse(source)
    docstrings = set()
    for node in ast.walk(tree):
        body = getattr(node, "body", None)
        if isinstance(node, ast.Module | ast.ClassDef | ast.FunctionDef) and body:
            first = body[0]
            if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant):
                docstrings.add(id(first.value))
    literals = [
        n.value
        for n in ast.walk(tree)
        if isinstance(n, ast.Constant) and isinstance(n.value, str) and id(n) not in docstrings
    ]
    names = {f.name for f in classification.families} | set(classification.rules)
    for literal in literals:
        assert literal not in names, f"model.py hard-codes {literal!r}"


# --- the arms this repository's own sources never take -------------------------------
#
# Every projection above is built from the governed sources of THIS repository, where each
# declared family exists, each declared relation is present, every edge names both ends and
# every source file is readable. The arms below answer for a corpus where one of those is
# false, and none of them had run.


def test_a_classification_that_declares_no_family_projects_only_typed_edges(classification):
    """THE DERIVED FAMILIES ARE LOOKED UP BY NAME, and every lookup can miss.

    Derivation and supersession edges are emitted only when the classification declares the
    family AND the relation inside it. This repository declares both, so all four lookups
    always succeeded and their misses were dead — and a miss is not a fault: the projection
    composes whatever the classification says is ancestry, so a classification that says
    derivation is not ancestry must produce no derivation edges rather than emit them under
    a family nobody declared.
    """
    silent = dataclasses.replace(classification, families=())

    projection = build(classification=silent)

    assert projection.edges == ()


def test_a_family_that_does_not_declare_the_relation_emits_nothing_for_it(classification):
    """A FAMILY IS NOT ENOUGH — THE RELATION INSIDE IT IS WHAT CARRIES THE MEANING.

    The derivation family declares both ``Produced-By`` and ``Derived-From`` here, so the
    per-relation lookup never came back empty. Emitting an edge without it would have to
    invent a relation name and a family, which is precisely the thing the classification
    exists to be the only source of.
    """
    derivation = next(f for f in classification.families if f.name == "derivation")
    stripped = dataclasses.replace(
        classification,
        families=tuple(
            dataclasses.replace(f, relations=()) if f.name == "derivation" else f
            for f in classification.families
        ),
    )

    assert derivation.relations
    projection = build(classification=stripped)

    assert not [e for e in projection.edges if e.family == "derivation"]


def test_a_family_declared_cyclic_is_not_checked_for_cycles(projection):
    """ACYCLICITY IS A DECLARED PROPERTY OF A FAMILY, NOT AN ASSUMPTION ABOUT ALL OF THEM.

    Every family this repository declares is acyclic, so the skip had no case — and it is
    what keeps the validator honest about a family whose question permits a cycle. Checking
    one anyway would report a legitimate structure as a violation, and a validator that
    reports legitimate structures gets its findings ignored.
    """
    permissive = dataclasses.replace(
        projection.classification,
        families=tuple(
            dataclasses.replace(f, acyclic=False) for f in projection.classification.families
        ),
    )
    relaxed = dataclasses.replace(projection, classification=permissive)

    assert validate(relaxed) == [p for p in validate(projection) if "not acyclic" not in p]


def test_an_edge_missing_either_end_is_skipped_rather_than_projected(tmp_path, classification):
    """AN EDGE WITH ONE END IS NOT AN EDGE.

    Every relationship in this corpus names both ends, so the skip had no case. Projecting a
    half-edge would put the empty string into the ancestry graph as a node — an ancestor
    every such edge shares, joining unrelated subjects through a node that does not exist.
    """
    repo = _corpus(
        tmp_path,
        relationships=[
            {"type": "Parent", "from": "UCOS-A", "to": "UCOS-B"},
            {"type": "Parent", "from": "UCOS-A", "to": ""},
            {"type": "Parent", "from": "", "to": "UCOS-B"},
        ],
    )

    projection = build(repo=str(repo), classification=classification)

    assert [(e.ancestor, e.descendant) for e in projection.edges] == [("UCOS-B", "UCOS-A")]


def _corpus(tmp_path, *, relationships=(), generated=(), change=None, optional=True):
    """A miniature governed corpus: the four required source documents, and optionally the two
    that are declared optional."""

    data = tmp_path / "00-BOOK" / "DATA"
    data.mkdir(parents=True, exist_ok=True)
    (data / "artifacts.json").write_text(json.dumps({"artifacts": []}), encoding="utf-8")
    (data / "relationships.json").write_text(
        json.dumps({"relationships": list(relationships)}), encoding="utf-8"
    )
    (data / "change-ledger.json").write_text(
        json.dumps(change or {"change_events": [], "lineage": {}}), encoding="utf-8"
    )
    (data / "generated-artifact-registry.json").write_text(
        json.dumps({"entries": list(generated)}), encoding="utf-8"
    )
    tools = tmp_path / "00-BOOK" / "tools"
    tools.mkdir(parents=True, exist_ok=True)
    (tools / "config.py").write_text(
        'RELATIONSHIP_TYPES = [{"type": "Parent", "inverse": "Child"}]\n',
        encoding="utf-8",
    )
    if optional:
        births = tmp_path / "00-MASTER" / "UOBC-000001"
        births.mkdir(parents=True, exist_ok=True)
        (births / "birth-ledger.json").write_text(json.dumps({"births": {}}), encoding="utf-8")
        (data / "id-ledger.json").write_text(json.dumps({"history": {}}), encoding="utf-8")
    assert os.path.isdir(data)
    return tmp_path


def test_a_required_source_is_a_refusal_and_an_optional_one_is_an_absence(tmp_path):
    """REQUIRED AND OPTIONAL ARE DIFFERENT ANSWERS TO THE SAME MISSING FILE.

    Every source is present in this repository, so neither arm ran. A required source that
    is absent is a refusal naming the file, because a projection composed without it would
    silently omit a whole family of ancestry. An optional one is simply absent — the births
    ledger and the id ledger are declared optional, and returning None lets the projection
    report what it does have rather than refusing to answer at all.
    """
    complete = _corpus(tmp_path / "complete")
    assert set(load_sources(str(complete))) >= {"artifacts", "edges", "births", "history"}

    without_optional = _corpus(tmp_path / "partial", optional=False)
    partial = load_sources(str(without_optional))
    assert partial["births"] == {}
    assert partial["history"] == {}

    incomplete = _corpus(tmp_path / "incomplete")
    (incomplete / "00-BOOK" / "DATA" / "relationships.json").unlink()
    with pytest.raises(LineageError, match="declared lineage source is absent") as raised:
        load_sources(str(incomplete))
    assert raised.value.subject.endswith("relationships.json")


def test_a_source_that_is_not_valid_json_is_a_named_refusal(tmp_path):
    """A TRUNCATED SOURCE IS NOT AN EMPTY ONE.

    Reading a half-written document as ``{}`` would compose a projection that reports no
    ancestry where ancestry exists — the most dangerous possible answer, because it looks
    like a clean result. The refusal names the file and carries the parser's own position, so
    the fault points at the document rather than at the projection that could not read it.
    """
    corpus = _corpus(tmp_path)
    (corpus / "00-BOOK" / "DATA" / "artifacts.json").write_text("{ truncated", encoding="utf-8")

    with pytest.raises(LineageError, match="not valid JSON") as raised:
        load_sources(str(corpus))

    assert raised.value.subject.endswith("artifacts.json")


def test_a_vocabulary_owner_declaring_no_relationship_types_is_refused(tmp_path):
    """THE OWNER'S SET IS WHAT MAKES THE CLASSIFICATION CHECKABLE RATHER THAN TRUSTED.

    The forward relations are read from the corpus vocabulary OWNER, so an owner module that
    declares none leaves the projection with no way to tell a forward relation from its
    inverse — and every ancestry fact would then be reported twice, once per direction.
    Treating an empty declaration as "no primaries" would do exactly that silently.
    """
    corpus = _corpus(tmp_path)
    (corpus / "00-BOOK" / "tools" / "config.py").write_text("# no declaration\n", encoding="utf-8")

    with pytest.raises(LineageError, match="declares no RELATIONSHIP_TYPES"):
        declared_relations(str(corpus))


def test_a_vocabulary_that_cannot_be_specified_is_refused(tmp_path, monkeypatch):
    """THE GUARD ABOVE THE LOADER, REACHED BY REMOVING WHAT MAKES IT UNREACHABLE.

    ``spec_from_file_location`` returns a spec for any ``.py`` path, present or not — a
    missing file fails later, inside the loader — so this guard cannot fire through any real
    path today. It is the check that keeps the failure a named LineageError rather than an
    ``AttributeError`` on ``None`` if the import machinery ever declines to describe the
    file, which is what happens for a path Python does not recognise as a module.
    """
    corpus = _corpus(tmp_path)
    monkeypatch.setattr("importlib.util.spec_from_file_location", lambda *_a, **_k: None)

    with pytest.raises(LineageError, match="vocabulary cannot be loaded"):
        declared_relations(str(corpus))


def test_a_relation_lookup_with_no_family_answers_none(classification):
    """THE LOOKUP GUARDS ITSELF AS WELL AS BEING GUARDED BY ITS CALLERS.

    Every call site short-circuits on a missing family, so the parameter check inside the
    lookup is a second defence and cannot fire through ``build``. It is what keeps the
    helper total for a caller that does not short-circuit — the alternative is an
    ``AttributeError`` on ``None.relations`` inside a function whose whole job is to answer
    "is this relation declared".
    """
    derivation = next(f for f in classification.families if f.name == "derivation")

    assert _relation_named(derivation, "Produced-By") is not None
    assert _relation_named(derivation, "A-Relation-Nobody-Declares") is None
    assert _relation_named(None, "Produced-By") is None


def test_a_relation_reports_the_family_that_classifies_it(classification):
    """AN EDGE'S FAMILY IS WHAT GIVES IT MEANING, and the reader that answers it by relation
    name had no caller.

    The projection resolves the family while composing each edge, so nothing later asks — but
    a consumer holding a relation name and no edge has no other way to find out which
    question that relation answers. An unclassified relation answers None, because inventing
    a family would put a relation the classification deliberately excluded into ancestry.
    """
    assert classification.family_of("Parent") == "structure"
    assert classification.family_of("Produced-By") == "derivation"
    assert classification.family_of("A-Relation-Nobody-Declares") is None


def test_an_edge_and_an_event_each_render_every_field_they_carry(projection):
    """AN EDGE CITES ITS SOURCE AND SO DOES AN EVENT, and the renders are where those
    citations are written down.

    The document builder projects both through its own shaping, so neither record's own
    render had a caller — and they are what an evidence consumer uses to write ONE edge or
    ONE event, with its relation, its family and the source that declared it, rather than
    reconstructing those from the projection's aggregate view. An event is deliberately not
    an edge: it carries a kind, a moment and an ordinal where an edge carries a direction,
    and the two renders are what keep that distinction visible in the evidence.
    """
    edge = projection.edges[0]

    assert edge.as_dict() == {
        "ancestor": edge.ancestor,
        "descendant": edge.descendant,
        "family": edge.family,
        "relation": edge.relation,
        "source": edge.source,
    }

    event = projection.events[0]

    assert event.as_dict() == {
        "at": event.at,
        "kind": event.kind,
        "sequence": event.sequence,
        "source": event.source,
        "subject": event.subject,
    }
