"""RCM — the Registry Coverage Matrix, measured.

The matrix answers where every governed object is registered and which registries declare
no authority. These tests hold the properties that make that answer trustworthy — it stores
nothing, the partition is exact, and each failure state is detectable — and they construct
each failure so that no state is asserted without ever having been produced.

The constraint under test throughout: the matrix must not become the 141st registry.
"""

from __future__ import annotations

import ast
import copy
import json
import os
import pathlib
import re
import subprocess
from dataclasses import replace

import pytest

from engine.registry_coverage.matrix import (
    COVERED,
    DUPLICATE_REGISTRATION,
    UNREGISTERED,
    CoverageError,
    Declarations,
    Plane,
    build,
    digest,
    load_declarations,
    locate_authority,
    rendered,
    repo_root,
    validate,
    verify,
)


@pytest.fixture(scope="module", name="matrix")
def _matrix() -> dict:
    return build()


@pytest.fixture(scope="module", name="declarations")
def _declarations() -> Declarations:
    return load_declarations()


@pytest.fixture(name="document")
def _document() -> dict:
    path = os.path.join(repo_root(), "engine", "registry_coverage", "declarations.json")
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


# --- it is not a registry ----------------------------------------------------------------


def test_the_matrix_stores_no_object_record(matrix) -> None:
    """Coverage counts, never a catalogue. A stored copy would be the 141st registry."""
    assert isinstance(matrix["objects"]["states"], dict)
    assert all(isinstance(v, int) for v in matrix["objects"]["states"].values())
    # findings are bounded diagnostics, not a population
    assert len(matrix["findings"]) <= 100


def test_the_matrix_claims_no_authority(matrix) -> None:
    assert matrix["authority"].startswith("NONE")


def test_the_matrix_writes_nothing() -> None:
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
    assert before == after


def test_the_matrix_stays_open(matrix) -> None:
    assert matrix["closed_set"] is False
    assert matrix["upper_limit"] is None


# --- partition correctness ----------------------------------------------------------------


def test_every_governed_object_is_covered(matrix) -> None:
    states = matrix["objects"]["states"]
    assert states[UNREGISTERED] == 0
    assert states[DUPLICATE_REGISTRATION] == 0
    assert states["PARTIALLY_COVERED"] == 0
    assert states[COVERED] == matrix["objects"]["total"]


def test_the_partition_is_exact(matrix) -> None:
    """Corpus + repository governed objects equal the whole universe."""
    governed = {p["plane"]: p["governed"] for p in matrix["planes"]}
    assert sum(governed.values()) == matrix["objects"]["total"]


#: The measured raw-path overlap between the two registries: historical identities minted into
#: `id-ledger.json` for objects the CORPUS plane governs — retained, not governed, which is a state
#: the declaration already models and the report already prints. It is held as a RATCHET rather than
#: driven to zero here, because removing an entry from a permanent append-only identity ledger to
#: make a coverage report green would violate identity immutability (UOBC-L-03/L-08) and the
#: single-identity-authority invariant (CAA-INV-04) — repairing a measurement by mutating the thing
#: it measures.
#:
#: THE RULE, STATED PRECISELY. This number may not move SILENTLY. A fall is always welcome and must
#: be recorded. A rise is admissible only when it is measured, explained, and shown to be
#: unpreventable — because both maps that produce it are append-only, so a rise this ratchet could
#: forbid outright would be a ratchet demanding an act the constitution refuses. An unexplained rise
#: is still a failure, and MOVEMENTS below is what separates the two.
#:
#: MOVEMENTS
#:   192 -> 201  (+9)  Recovery integration. Permit P-UCOS-RECOVERY-001 registered 61 documents
#:                     into the CORPUS plane, and nine of them already carried a REPOSITORY-plane
#:                     identity: UCOS-EXDOC-002986/7/8/9/90/91/92/93/94, minted in commits 446…,
#:                     32e…, d19… and d92… long before this transaction. Registering a document the
#:                     repository ledger had already seen puts it in both raw path sets by
#:                     construction. Every one of the nine is EXCLUDED_DOCUMENT, so the REPOSITORY
#:                     plane retains an identity for it and governs nothing — the identical shape as
#:                     the original 192, not a new kind of overlap, and `DUPLICATE_REGISTRATION`
#:                     remains 0. It is irreversible in both directions: `by_object` is append-only
#:                     (UOBC-L-03/L-08) and the corpus registration was an authorized, permanent
#:                     `by_path` allocation. Measured composition at 201: 198 EXDOC, 3 DATAOBJ.
#:   201 -> 210  (+9)  Corpus-registration completion. Permit P-UCOS-CORPUS-003 registered nine
#:                     root-level determination documents into the CORPUS plane, and every one of
#:                     them already carried a REPOSITORY-plane identity minted three commits
#:                     earlier at a4f56e83: UCOS-EXDOC-003048 through UCOS-EXDOC-003056. The shape
#:                     is the 192 -> 201 movement exactly — a document the repository ledger had
#:                     already seen entering the corpus plane puts it in both raw path sets by
#:                     construction — not a new kind of overlap. All nine are EXCLUDED_DOCUMENT, so
#:                     the REPOSITORY plane retains an identity and governs nothing, and
#:                     `DUPLICATE_REGISTRATION` remains 0. Unpreventable in the sense this rule
#:                     requires: refusing the rise would mean refusing either the by_object mint
#:                     (already permanent) or the authorized by_path allocation, and both maps are
#:                     append-only. Measured composition at 210: 207 EXDOC, 3 DATAOBJ.
#:   210 -> 211  (+1)  UAC-000001, the agnosticism conformance harness. Permit P-UCOS-UGA-005
#:                     minted `engine/conformance/axis-register.json` into the REPOSITORY plane as
#:                     UCOS-DATAOBJ-000145, and P-UCOS-CORPUS-006 then registered the same file
#:                     into the CORPUS plane as an ENG declaration document, beside
#:                     `engine/lineage/families.json` and `memory-layers.json`, which is the
#:                     established shape for an engine declaration. A file the repository ledger
#:                     had already seen entering the corpus plane puts it in both raw path sets by
#:                     construction — the same shape as 192 -> 201 and 201 -> 210, not a new kind
#:                     of overlap, and `DUPLICATE_REGISTRATION` remains 0. Measured composition at
#:                     211: 207 EXDOC, 4 DATAOBJ.
#:
#:                     UNPREVENTABLE NOW, AND AVOIDABLE THEN — recorded because this rule asks for
#:                     unpreventability and the honest answer is qualified. Both allocations are
#:                     operator-authorized and permanent, and both maps are append-only, so
#:                     nothing can undo it: unpreventable in exactly the sense the rule requires.
#:                     But the ORDER was a choice. Registering the file into the corpus FIRST
#:                     would likely have removed the by_object requirement entirely — measured in
#:                     the same session, immediately after: registering ADR-0040 and ADR-0041 into
#:                     the corpus left `uga_engine.py run --plan` at total_allocations=0, because
#:                     a document the corpus registry carries is not UGA's subject. The by_object
#:                     mint came first only because the harness was landed before it was
#:                     registered. A future engine declaration should be registered into the
#:                     corpus before any by_object identity is minted for it, and this entry
#:                     exists so that lesson is attached to the number it moved.
#:   211 -> 212  (+1)  engine/zero_class/zero-class-register.json, and this rise is a REPEAT of a
#:                     mistake the 210 -> 211 entry above already recorded. That entry ends: "a
#:                     future engine declaration should be registered into the corpus before any
#:                     by_object identity is minted for it, and this entry exists so that lesson
#:                     is attached to the number it moved." The lesson was attached, and then not
#:                     applied: P-UCOS-UGA-008 minted the register into the REPOSITORY plane on
#:                     the day it was written, and P-UCOS-CORPUS-007 registered it into the CORPUS
#:                     plane hours later. Same file, same order, same result.
#:                     Unpreventable now for the same reason as before — both allocations are
#:                     operator-authorized and both maps are append-only, so nothing can undo it —
#:                     and avoidable then for the same reason. Measured composition at 212: 207
#:                     EXDOC, 5 DATAOBJ. DUPLICATE_REGISTRATION remains 0.
#:                     WHAT WOULD ACTUALLY PREVENT THE THIRD: a check, not a comment. An engine
#:                     declaration is any .json under a package directory carrying a top-level
#:                     `authority` field; minting one into by_object before it is corpus-registered
#:                     is detectable at plan time. A note in a MOVEMENTS log is documentation, and
#:                     this is now the second consecutive entry proving documentation did not hold.
RETAINED_NOT_GOVERNED_OVERLAP = 212


def test_the_two_planes_are_disjoint_IN_GOVERNANCE() -> None:
    """The property the declaration actually states, measured — plus a ratchet on the rest.

    THIS TEST ASSERTED SOMETHING THE DECLARATION DOES NOT CLAIM, AND FAILED CONTINUOUSLY FOR IT.
    It required the two registries' raw path sets to be disjoint. But `declarations.json` gives
    each plane `holds_object_classes` to say WHICH objects it governs, and the matrix's own
    report carries `$retained_not_governed`: "A plane may hold MORE entries than it holds
    governed objects, and the difference is not a discrepancy." Raw-path disjointness contradicts
    the existence of that state. The measured overlap is 192 DOCUMENT_ARTIFACTs carrying a
    historical identity in the repository ledger while the corpus plane governs them — and the
    REPOSITORY plane does not declare DOCUMENT_ARTIFACT at all.

    So the assertion is now the declared property: no object is governed by two planes. The raw
    overlap is kept as a two-sided ratchet so the historical residue cannot grow silently and a
    reduction must be recorded here.
    """

    root = repo_root()
    with open(os.path.join(root, "00-BOOK", "DATA", "artifacts.json"), encoding="utf-8") as h:
        corpus = {a["path"] for a in json.load(h)["artifacts"]}
    with open(os.path.join(root, "00-BOOK", "DATA", "id-ledger.json"), encoding="utf-8") as h:
        repository = set(json.load(h)["by_object"])

    matrix = build()
    assert matrix["objects"]["states"][DUPLICATE_REGISTRATION] == 0, [
        f["path"] for f in matrix["findings"] if f["state"] == DUPLICATE_REGISTRATION
    ][:5]

    assert len(corpus & repository) == RETAINED_NOT_GOVERNED_OVERLAP, (
        "the retained-not-governed residue moved. It may only fall, and a fall must be recorded "
        f"here: measured {len(corpus & repository)}, declared {RETAINED_NOT_GOVERNED_OVERLAP}"
    )


def test_a_class_declared_by_two_planes_is_refused() -> None:
    """The partition is measured on every build, never assumed.

    `plane_of_class` is a dict comprehension: two planes declaring one class would silently keep
    the last, and the duplicate rule would lose the ability to see a genuinely double-governed
    object. The refusal is what makes governance-disjointness enforceable rather than hopeful.
    """

    declarations = load_declarations()
    planes = list(declarations.planes)
    forged = replace(
        declarations,
        planes=(
            replace(
                planes[0], object_classes=(*planes[0].object_classes, *planes[1].object_classes)
            ),
            *planes[1:],
        ),
    )
    with pytest.raises(CoverageError, match="do not partition"):
        build(declarations=forged)


def test_an_object_no_plane_governs_is_still_unregistered() -> None:
    """The fix reads the declaration; it must not have made the matrix permissive.

    Scoping `planes_holding` by declared class could have been a way to make every object look
    covered. It is not: a declaration under which no plane governs anything reports the whole
    population UNREGISTERED and `validate` refuses it.
    """

    declarations = load_declarations()
    planes = list(declarations.planes)
    forged = replace(
        declarations,
        planes=(
            replace(planes[0], object_classes=("A_CLASS_NOTHING_HAS",)),
            replace(planes[1], object_classes=("ANOTHER_CLASS_NOTHING_HAS",)),
        ),
    )
    matrix = build(declarations=forged)
    assert matrix["objects"]["states"][UNREGISTERED] == matrix["objects"]["total"]
    assert matrix["objects"]["states"][COVERED] == 0
    assert validate(matrix, forged)


def test_the_generated_registry_is_contained_in_the_repository_plane() -> None:
    """Containment, over the entries that HAVE a repository plane to be contained in.

    THIS TEST ASSERTED SOMETHING THE DECLARATION DOES NOT CLAIM, in the same shape as
    ``test_the_two_planes_are_disjoint_IN_GOVERNANCE`` above. It required every generated
    artifact to hold a `by_object` identity. Twenty-three do not and may not: the
    UCOS-UCTX-001 context projections declare ``tracked: false``,
    ``canonical_identity_role: EXCLUDED`` and ``registration_status:
    EXCLUDED_FROM_CORPUS_REGISTRATION``, and no clone ever commits one — so an identity in
    the ledger would name a path the repository does not hold, and minting one to make this
    assertion green would be an irreversible allocation performed to satisfy a measurement.
    GOV-005 §5.3 states the rule the entries are already following: a generated artifact is
    regenerated, never hand-registered, and consumes no permanent identity.

    So the assertion is now the declared property, EXCLUDED_ARTIFACTS_CONSUME_NO_IDENTITY,
    and it is two-sided — which is what keeps the exemption from being a hole. An entry may
    leave the containment requirement only by declaring itself excluded, that declaration
    must be complete, and an excluded entry that acquires an identity anyway fails here.
    """

    root = repo_root()
    with open(
        os.path.join(root, "00-BOOK", "DATA", "generated-artifact-registry.json"), encoding="utf-8"
    ) as h:
        entries = json.load(h)["entries"]
    with open(os.path.join(root, "00-BOOK", "DATA", "id-ledger.json"), encoding="utf-8") as h:
        repository = set(json.load(h)["by_object"])

    # Absence of the key means the repository materialises the path: 345 of 369 entries are
    # written that way and every one of them carries an identity.
    materialised = {e["canonical_path"] for e in entries if e.get("tracked", True)}
    excluded = [e for e in entries if not e.get("tracked", True)]

    assert materialised <= repository, sorted(materialised - repository)[:5]
    assert excluded, (
        "no entry declares itself excluded, so the exemption below is measuring nothing; if "
        "the excluded family was withdrawn, withdraw this half of the control with it"
    )
    for entry in excluded:
        path = entry["canonical_path"]
        assert entry["canonical_identity_role"] == "EXCLUDED", path
        assert entry["registration_status"] == "EXCLUDED_FROM_CORPUS_REGISTRATION", path
        assert entry["exclusion_register_class"], path
        assert path not in repository, (
            f"{path} declares tracked:false yet holds a repository-plane identity; an "
            "excluded artifact that acquires one is an allocation nothing authorized"
        )


def test_retained_entries_are_reported_separately(matrix) -> None:
    """Append-only retention is not a coverage error, and must not read as one."""
    for plane in matrix["planes"]:
        assert plane["retained_not_governed"] == plane["registered"] - plane["governed"]
        assert plane["retained_not_governed"] >= 0


def test_no_two_planes_claim_one_object_class(declarations) -> None:
    seen: dict[str, str] = {}
    for plane in declarations.planes:
        for klass in plane.object_classes:
            assert klass not in seen, f"{klass} claimed by two planes"
            seen[klass] = plane.name


# --- W5-G1: authority gap handling --------------------------------------------------------


def test_the_disclosed_gaps_record_producer_and_remediation(declarations) -> None:
    """Recorded, not inferred — each gap names where its remediation belongs."""
    assert declarations.gaps, "W5-G1 is not disclosed"
    for gap in declarations.gaps:
        assert gap.producer, gap.gap_id
        assert gap.producer_owner, gap.gap_id
        assert gap.missing, gap.gap_id
        assert gap.remediation, gap.gap_id
        assert gap.referred_to, gap.gap_id


def test_a_disclosed_gap_is_not_reported_as_undeclared(matrix, declarations) -> None:
    disclosed = {g.registry for g in declarations.gaps}
    reported = {
        r["registry"] for r in matrix["registries"]["entries"] if r["status"] == "DISCLOSED_GAP"
    }
    assert reported <= disclosed


def test_no_registry_is_undeclared_today(matrix) -> None:
    undeclared = [
        r["registry"] for r in matrix["registries"]["entries"] if r["status"] == "UNDECLARED"
    ]
    assert undeclared == [], undeclared


def test_an_undisclosed_registry_without_authority_is_refused(matrix) -> None:
    """The ratchet: disclosure is not permission for the NEXT one."""
    forged = copy.deepcopy(matrix)
    forged["registries"]["entries"].append(
        {
            "registry": "00-MASTER/INVENTED/registry.json",
            "authority_mechanism": "",
            "status": "UNDECLARED",
            "plane": "",
        }
    )
    problems = validate(forged)
    assert any("no declared authority and no disclosure" in p for p in problems)


def test_the_producer_is_recorded_but_not_adopted_as_owner(declarations) -> None:
    """Inferring ownership would manufacture the missing declaration."""
    for gap in declarations.gaps:
        assert gap.missing == "AUTHORITY_DECLARATION"
        # the producer owner is recorded as the REFERRAL target, not as the declared owner
        assert gap.referred_to == gap.producer_owner


# --- failure detection --------------------------------------------------------------------


def test_an_unregistered_object_is_detected(matrix) -> None:
    forged = copy.deepcopy(matrix)
    forged["objects"]["states"][UNREGISTERED] = 1
    forged["findings"].append({"path": "x/y.md", "state": UNREGISTERED, "planes": ""})
    assert any(UNREGISTERED in p for p in validate(forged))


def test_a_duplicate_registration_is_detected(matrix) -> None:
    forged = copy.deepcopy(matrix)
    forged["objects"]["states"][DUPLICATE_REGISTRATION] = 2
    forged["findings"].append(
        {"path": "x/y.md", "state": DUPLICATE_REGISTRATION, "planes": "CORPUS,REPOSITORY"}
    )
    assert any(DUPLICATE_REGISTRATION in p for p in validate(forged))


def test_an_empty_plane_is_detected(matrix) -> None:
    forged = copy.deepcopy(matrix)
    forged["planes"][0]["registered"] = 0
    assert any("registers nothing" in p for p in validate(forged))


# --- determinism ---------------------------------------------------------------------------


def test_two_builds_are_byte_identical() -> None:
    assert rendered(build()) == rendered(build())


def test_the_digest_is_stable() -> None:
    assert digest(build()) == digest(build())


def test_verify_reports_determinism_and_passes() -> None:
    report = verify()
    assert report["deterministic"] is True
    assert report["status"] == "PASS", report["problems"]


def test_no_wall_clock_enters_the_matrix(matrix) -> None:
    trimmed = {k: v for k, v in matrix.items() if k not in ("registries", "findings")}
    assert re.findall(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}", json.dumps(trimmed)) == []


# --- the declaration refuses an unusable document -------------------------------------------


@pytest.mark.parametrize(
    "section", ["authority_mechanisms", "registration_planes", "coverage_states", "scan"]
)
def test_a_missing_section_is_refused(document, section) -> None:
    document.pop(section)
    with pytest.raises(CoverageError):
        Declarations.of(document)


def test_two_planes_claiming_one_class_is_refused(document) -> None:
    document["registration_planes"][1]["holds_object_classes"].append(
        document["registration_planes"][0]["holds_object_classes"][0]
    )
    with pytest.raises(CoverageError, match="same object class"):
        Declarations.of(document)


def test_a_missing_declaration_file_is_a_fault(tmp_path) -> None:
    with pytest.raises(CoverageError, match="absent"):
        load_declarations(str(tmp_path / "nope.json"))


def test_an_unparseable_declaration_is_a_fault(tmp_path) -> None:
    path = tmp_path / "declarations.json"
    path.write_text("{ not json", encoding="utf-8")
    with pytest.raises(CoverageError, match="valid JSON"):
        load_declarations(str(path))


# --- no hard-coded reality -------------------------------------------------------------------


def test_registry_paths_and_gap_ids_are_data_not_code(declarations) -> None:
    source = (pathlib.Path(repo_root()) / "engine" / "registry_coverage" / "matrix.py").read_text(
        "utf-8"
    )
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
    forbidden = {g.gap_id for g in declarations.gaps} | {g.registry for g in declarations.gaps}
    for literal in literals:
        for needle in forbidden:
            assert needle not in literal, f"matrix.py hard-codes {needle!r}"


def test_a_registry_document_that_is_not_an_object_declares_no_authority(declarations) -> None:
    """A register that is a list, a string or nothing is unreadable, and unreadable is None.

    The mechanisms answer only when a document can be consulted; coercing a non-mapping would
    turn a broken registry into a silent claim of authority, which is the reverse of the
    finding the None return exists to raise.
    """

    for unreadable in (None, [], "authority: top", 7):
        assert locate_authority("some/registry.json", unreadable, declarations, {}) is None


def test_a_list_populated_registry_is_projected_whole(declarations, tmp_path) -> None:
    """A registry whose population is a LIST of records, not a dict, is a real shape.

    The build path reads both; the list arm had never fired, so a plane that records
    ``[{"path": ...}, ...]`` would have registered as holding nothing while holding all.
    """

    repo = tmp_path / "listy"
    os.makedirs(repo / "registries")
    (repo / "registries").joinpath("a.json").write_text(
        json.dumps(
            {
                "records": [
                    {"path": "x.py"},
                    {"path": "y.py"},
                    "not-a-record",
                    {"no_path": True},
                ]
            }
        ),
        encoding="utf-8",
    )
    (repo / "registries").joinpath("b.json").write_text(json.dumps({"items": []}), encoding="utf-8")
    os.makedirs(repo / "00-BOOK/DATA")
    (repo / "00-BOOK/DATA").joinpath("canonical-observation-audit.json").write_text(
        json.dumps({"entries": []}), encoding="utf-8"
    )
    (repo / "registries").joinpath("c.json").write_text(json.dumps({"count": 7}), encoding="utf-8")
    handcrafted = replace(
        declarations,
        planes=(
            Plane("A", "registries/a.json", "owner", frozenset({"X"}), "M", "records"),
            Plane("B", "registries/b.json", "owner", frozenset({"Y"}), "M", "items"),
            Plane("C", "registries/c.json", "owner", frozenset({"Z"}), "M", "count"),
        ),
    )
    matrix = build(str(repo), handcrafted)
    by_name = {p["plane"]: p for p in matrix["planes"]}
    assert by_name["A"]["registered"] == 2
    assert by_name["C"]["registered"] == 0


def test_a_registry_that_declares_nothing_returns_no_mechanism(declarations) -> None:
    """Every ranked mechanism answers None for a document that carries none of them.

    The fall-through out of the ranked chain is the finding-side of the search: a registry
    that names no authority is reported by the gap table, and the only way to know the
    walk terminates honestly is to watch it terminate.
    """
    indexes = {"generated_paths": set(), "external_text": set(), "declarations": {}}
    kinds = tuple({str(m.get("mechanism")) for m in declarations.mechanisms})
    assert kinds, "the shipped declaration ranks no mechanisms at all"
    assert locate_authority("00-BOOK/DATA/anything.json", {}, declarations, indexes) is None


def test_an_unranked_kind_falls_through_the_search_without_matching(declarations) -> None:
    """A mechanism whose kind this matcher does not know ends the search at None.

    The ranked list is data; the walk must keep going past kinds it cannot evaluate and
    answer None rather than guess the nearest mechanism's name.
    """
    handcrafted = replace(
        declarations,
        mechanisms=(
            {"mechanism": "SOME_FUTURE_KIND", "rank": 1},
            {"mechanism": "TOP_LEVEL_AUTHORITY_KEY", "rank": 2},
        ),
    )
    indexes = {"generated_paths": set(), "external_text": set(), "declarations": {}}
    assert locate_authority("whatever.json", {}, handcrafted, indexes) is None
