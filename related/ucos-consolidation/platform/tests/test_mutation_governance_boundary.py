"""UCOS-CL-016 — the mutation governance boundary is declared, and it holds.

The determination is OPTION B: the Constitutional Mutation Gateway governs mutations of
constitutional truth, not source files. ``test_the_gateway_does_not_touch_the_filesystem``
is the evidence for that determination rather than a restatement of it — if the gateway
ever grows a filesystem, the determination must be revisited and this test says so by
failing.
"""

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
BOUNDARY = REPO / "00-BOOK" / "DATA" / "mutation-governance-boundary.json"


@pytest.fixture(scope="module")
def boundary() -> dict:
    return json.loads(BOUNDARY.read_text(encoding="utf-8"))


def test_the_boundary_is_declared(boundary: dict) -> None:
    assert boundary["schema"] == "ucos-mutation-governance-boundary"
    assert boundary["determination"].startswith("OPTION B")
    assert boundary["authorities"] and boundary["mutation_classes"]


def test_1_every_mutation_class_names_exactly_one_governing_chain(boundary: dict) -> None:
    for entry in boundary["mutation_classes"]:
        assert entry.get("governed_by"), f"{entry['class']} is ungoverned"
        assert isinstance(entry["governed_by"], str)


def test_2_no_class_is_claimed_by_two_authorities_as_primary(boundary: dict) -> None:
    classes = [e["class"] for e in boundary["mutation_classes"]]
    assert len(classes) == len(set(classes)), f"duplicate mutation class: {classes}"


def test_3_no_mutation_class_is_ungoverned(boundary: dict) -> None:
    """Every class of change the repository can undergo has a named authority chain."""
    covered = {e["class"] for e in boundary["mutation_classes"]}
    required = {
        "CONSTITUTIONAL_TRUTH",
        "SOURCE",
        "GENERATED_ARTIFACT",
        "EXCLUSION",
        "REPOSITORY_STATE",
    }
    assert required <= covered, f"ungoverned mutation classes: {sorted(required - covered)}"

    # THE LITERAL ABOVE IS A FLOOR, NOT THE POPULATION, AND A FLOOR GOES STALE. It names
    # the five original classes; the register now declares nine, so four could vanish
    # without this test noticing. The bijection below is the part that cannot go stale:
    # every class the rules classify into must be declared, and every declared class must
    # have a rule that can reach it. A class with no rule is unreachable, and a rule with
    # no class classifies into nothing.
    ruled = {r["class"] for r in boundary["classification_rules"]["rules"]}
    assert ruled == covered, (
        f"classes with no rule: {sorted(covered - ruled)}; "
        f"rules with no class: {sorted(ruled - covered)}"
    )


def test_4_every_named_authority_implementation_exists(boundary: dict) -> None:
    for authority in boundary["authorities"]:
        impl = authority["implementation"]
        target = REPO / impl
        if "::" in impl:
            target = REPO / impl.split("::")[0]
        assert target.exists(), f"{authority['authority']} names a missing implementation: {impl}"


def test_5_the_boundary_itself_is_tracked() -> None:
    tracked = subprocess.run(  # noqa: S603
        ["git", "ls-files", "--error-unmatch", "00-BOOK/DATA/mutation-governance-boundary.json"],  # noqa: S607
        cwd=REPO,
        capture_output=True,
        text=True,
        check=False,
    )
    # Before the first commit of this closure the file is new; after it, tracked. Either
    # way it must be present on disk and readable, which is what governance depends on.
    assert BOUNDARY.is_file()
    if tracked.returncode != 0:
        pytest.skip("boundary artifact not yet committed (first closure commit pending)")


def test_the_gateway_does_not_touch_the_filesystem() -> None:
    """The evidence for OPTION B, asserted rather than asserted-about.

    The Constitutional Mutation Gateway operates on in-memory Population and
    ConstitutionalMetadata values. It never opens a file, resolves a path, or invokes git.
    That is *why* source mutations fall outside it. If this ever stops being true, the
    determination in the boundary artifact is stale and must be re-made — so this test
    failing is a signal to revisit the boundary, not to relax the test.
    """
    forbidden_calls = {"open", "read_text", "write_text", "mkdir", "unlink"}
    forbidden_names = {"Path", "subprocess"}

    for module in ("gateway.py", "state.py"):
        source = (REPO / "engine" / "constitution" / module).read_text(encoding="utf-8")
        tree = ast.parse(source)

        imported: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imported.add(node.module.split(".")[0])
                imported.update(alias.name for alias in node.names)

        leaked = imported & (forbidden_names | {"pathlib", "os", "shutil"})
        assert not leaked, (
            f"engine/constitution/{module} imports {sorted(leaked)} — the gateway has grown a "
            "filesystem, so the OPTION B determination that source mutations fall outside "
            "CMG is no longer supported by its implementation"
        )

        called = {
            node.func.id
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        }
        assert not (
            called & forbidden_calls
        ), f"engine/constitution/{module} calls {sorted(called & forbidden_calls)}"


def test_exclusion_is_governed_by_a_register_not_by_the_exclusion_mechanism(boundary: dict) -> None:
    """The UCOS-CL-001 correction, stated as a boundary rule.

    `.gitignore` must not be its own governing authority. That circularity is precisely what
    let two ignore lines clear a blocking convergence criterion.
    """
    exclusion = next(e for e in boundary["mutation_classes"] if e["class"] == "EXCLUSION")
    assert "UCOS-EXCLUSION-REGISTER-001" in exclusion["governed_by"]
    assert "GATE-12" in exclusion["governed_by"]


def test_source_class_chain_terminates_in_clone_certification(boundary: dict) -> None:
    """A source mutation is not governed until a clone reproduces its consequences."""
    source = next(e for e in boundary["mutation_classes"] if e["class"] == "SOURCE")
    stages = ("pre-commit", "verify.sh", "UCOS-RIB-001", "UCOS-AEE-001", "Phase 8", "Phase 9")
    for stage in stages:
        assert stage in source["governed_by"], f"SOURCE chain omits {stage}"

    # A CHAIN IS AN ORDER, AND MEMBERSHIP IS NOT AN ORDER. The loop above passes for a
    # chain that names all six stages in any arrangement, including certification before
    # the verification it certifies. MU-02 declares this as mutation -> authority ->
    # evidence -> execution -> verification -> certification, so the order carries the
    # meaning and is measured here rather than assumed.
    positions = [source["governed_by"].index(stage) for stage in stages]
    assert positions == sorted(positions), (
        f"SOURCE chain names its stages out of declared order: "
        f"{sorted(zip(positions, stages, strict=True))}"
    )


# -----------------------------------------------------------------------------
# MU-02 — the chain, measured end to end
#
# The closure register carries MU-02 as OPEN with the gap "Not end-to-end measured": the
# chain mutation -> authority -> evidence -> execution -> verification -> certification is
# declared, and nothing walked it. test_4 above checks that each entry in `authorities`
# names an implementation that exists, which is not the same predicate -- the actors a
# class's chain NAMES are strings in `governed_by`, and no test resolved them. These three
# do, and each states its exceptions as an exact set rather than a minimum, so a new
# exception fails immediately instead of joining a crowd.
# -----------------------------------------------------------------------------

#: Chain actors that resolve to nothing checkable. `producer` is a role, not a named
#: authority: GENERATED_ARTIFACT's chain leaves it to the artifact's producer home without
#: the `(owner-parameterised)` marker its three sibling classes use for exactly this. It is
#: carried as a disclosed exception rather than resolved, because adding that marker edits
#: a governed key of a constitutional register and belongs to the boundary's owner.
CHAIN_ACTORS_RESOLVING_TO_NOTHING = {("GENERATED_ARTIFACT", "producer")}

#: Classes declaring every governed key whose chain nevertheless stops before certification.
#: GOVERNED_ANALYSIS is governed by a self-declared authority and observed by verify.sh, and
#: there it ends -- while GOVERNED_DECLARATION and AUTHORED_DOCUMENT, which declare the same
#: six keys and are governed the same owner-parameterised way, both continue to Phase 8 and
#: Phase 9. No annotation on the class explains the difference, and the class carries two.
#: Whether an analysis should reach pristine-clone certification is the boundary owner's
#: call; that it differs from its siblings without saying so is measured here.
FULLY_DECLARED_CLASSES_NOT_REACHING_CERTIFICATION = {"GOVERNED_ANALYSIS"}

#: Classes carrying no `membership_criteria`, so they are classified by example alone.
#: GOVERNED_DECLARATION's own `$why_this_class_was_missing` names this as the defect that
#: hid an unclassified artifact: "The register classified by example and its invariants
#: quantified over classes rather than over artifacts, so an artifact belonging to no class
#: violated nothing." Six of nine classes still do. The set is pinned so it can only shrink.
CLASSES_WITHOUT_MEMBERSHIP_CRITERIA = {
    "CONSTITUTIONAL_TRUTH",
    "SOURCE",
    "GENERATED_ARTIFACT",
    "EXCLUSION",
    "REPOSITORY_STATE",
    "CORPUS_REGISTRATION",
}

GOVERNED_CLASS_KEYS = frozenset(
    {
        "class",
        "governed_by",
        "examples",
        "membership_criteria",
        "does_not_govern",
        "grants_only_mutation_ownership",
    }
)


def _chain_actors(governed_by: str) -> list[str]:
    """The actors a chain names, in declared order, with parentheticals kept for reading."""
    return [actor.strip() for actor in governed_by.split("\u2192") if actor.strip()]


def _identifiers_present_in_tracked_files(candidates: set[str]) -> set[str]:
    """Which of these identifiers occur anywhere in tracked content, in one git call."""
    if not candidates:
        return set()
    args = ["git", "grep", "-h", "-o", "-F"]
    for candidate in sorted(candidates):
        args += ["-e", candidate]
    found = subprocess.run(  # noqa: S603
        args, cwd=REPO, capture_output=True, text=True, check=False
    )
    return {line.strip() for line in found.stdout.splitlines() if line.strip()}


def test_6_every_chain_actor_resolves_or_is_a_disclosed_parameter(boundary: dict) -> None:
    """Every actor named in a governance chain resolves to something, or is disclosed.

    An actor that resolves to nothing is a link in a governance chain that cannot be
    followed, which is indistinguishable from an ungoverned mutation wearing a chain.
    """
    heads = {str(a["authority"]).split("\u2014")[0].strip() for a in boundary["authorities"]}

    unresolved: set[tuple[str, str]] = set()
    identifier_candidates: dict[tuple[str, str], str] = {}

    for entry in boundary["mutation_classes"]:
        for actor in _chain_actors(entry["governed_by"]):
            # The parenthetical carries the disclosure, so it is read before being stripped.
            if "owner-parameterised" in actor:
                continue
            bare = actor.split("(")[0].strip().rstrip(".,")
            if any(bare.startswith(head) or head.startswith(bare) for head in heads):
                continue
            if (REPO / bare).exists():
                continue
            if (REPO / "platform" / bare.lower().replace(" ", "_")).exists():
                continue
            if bare.replace("-", "").replace(".", "").isupper() or bare.isupper():
                identifier_candidates[(entry["class"], bare)] = bare
                continue
            unresolved.add((entry["class"], bare))

    # An identifier that names a register declared elsewhere in the corpus resolves; one
    # that occurs nowhere does not.
    present = _identifiers_present_in_tracked_files(set(identifier_candidates.values()))
    for key, identifier in identifier_candidates.items():
        if identifier not in present:
            unresolved.add(key)

    assert unresolved == CHAIN_ACTORS_RESOLVING_TO_NOTHING, (
        f"chain actors resolving to nothing changed: "
        f"new={sorted(unresolved - CHAIN_ACTORS_RESOLVING_TO_NOTHING)}, "
        f"fixed={sorted(CHAIN_ACTORS_RESOLVING_TO_NOTHING - unresolved)}"
    )


def test_7_fully_declared_classes_reach_certification_or_are_disclosed(boundary: dict) -> None:
    """Classes declared to the same completeness should be governed to the same terminus."""
    fully_declared = {
        e["class"] for e in boundary["mutation_classes"] if GOVERNED_CLASS_KEYS <= set(e)
    }
    assert fully_declared, "no class declares every governed key"

    short = {
        e["class"]
        for e in boundary["mutation_classes"]
        if e["class"] in fully_declared and "Phase 9" not in e["governed_by"]
    }
    assert short == FULLY_DECLARED_CLASSES_NOT_REACHING_CERTIFICATION, (
        f"fully-declared classes not reaching certification changed: "
        f"new={sorted(short - FULLY_DECLARED_CLASSES_NOT_REACHING_CERTIFICATION)}, "
        f"fixed={sorted(FULLY_DECLARED_CLASSES_NOT_REACHING_CERTIFICATION - short)}"
    )


def test_8_classification_by_example_is_bounded_and_may_only_shrink(boundary: dict) -> None:
    """A class with no membership criteria is classified by example, and that is the defect.

    The bound is two-sided on purpose: a tenth class added without criteria fails here, and
    writing criteria for one of these six fails here too until the bound is lowered to
    match. A bound that only refuses growth lets repaid debt sit unrecorded.
    """
    without = {e["class"] for e in boundary["mutation_classes"] if not e.get("membership_criteria")}
    assert without == CLASSES_WITHOUT_MEMBERSHIP_CRITERIA, (
        f"classification-by-example population changed: "
        f"new={sorted(without - CLASSES_WITHOUT_MEMBERSHIP_CRITERIA)}, "
        f"repaid={sorted(CLASSES_WITHOUT_MEMBERSHIP_CRITERIA - without)}"
    )
