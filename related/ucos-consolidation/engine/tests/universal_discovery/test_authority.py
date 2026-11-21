"""Ω-2 — authority derived by a chain whose last rule is unconditional, so NONE is unreachable."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import pytest

from engine.universal_discovery import authority
from engine.universal_discovery.model import OmegaError


def _derive(path: str, source: str = "", **overrides: object) -> tuple[str, str]:
    arguments: dict[str, object] = {
        "source": source,
        "contracts": _EmptyContracts(),
        "invoking_planes": {},
        "importer_authorities": {},
        "transient": {},
    }
    arguments.update(overrides)
    return authority.derive_authority(path, **arguments)  # type: ignore[arg-type]


class _EmptyContracts:
    """A contract index that claims nothing, so each rule below is tested in isolation."""

    def programme_for(self, path: str) -> str:
        return ""


# ------------------------------------------------------------------------ Ω-A-01: self-declaration


def test_a_declared_authority_constant_wins() -> None:
    owner, rule = _derive("alpha/core/x.py", 'EXECUTION_AUTHORITY = "SOME-OWNER-001"\n')
    assert (owner, rule) == ("SOME-OWNER-001", authority.RULE_DECLARATION)


def test_a_declaration_beats_an_inherited_owner() -> None:
    """Order is load-bearing: otherwise a module could be quietly re-owned by whoever imports it."""
    owner, rule = _derive(
        "alpha/core/x.py",
        'MODULE_AUTHORITY = "MINE-001"\n',
        importer_authorities={"alpha/core/x.py": frozenset({"THEIRS-001"})},
    )
    assert (owner, rule) == ("MINE-001", authority.RULE_DECLARATION)


@pytest.mark.parametrize(
    "token",
    [
        "NONE (DERIVED TRUTH)",
        "none",
        "DERIVED TRUTH",
        "derived-truth",
        "ENGINEERING-EXECUTION-ONLY",
        "",
    ],
)
def test_a_derived_truth_disclaimer_is_not_an_absent_owner(token: str) -> None:
    """THE INVERSION THIS PREVENTS, and it would have been severe.

    Roughly every engine in this repository opens with ``AUTHORITY = NONE (DERIVED TRUTH)``. That
    is a disclaimer of LEGISLATIVE authority — the module declares it makes no law — not a
    statement that nobody owns it. Read as an absent owner, the most carefully governed files in
    the repository would have counted as the ungoverned ones, and the Ω-2 measurement would have
    been exactly backwards.
    """
    source = f'MODULE_AUTHORITY = "{token}"\n'
    assert authority.declared_authority(source) == ("", "")
    owner, rule = _derive("alpha/core/x.py", source)
    assert rule != authority.RULE_DECLARATION
    assert owner, "the chain must continue past a disclaimer and still produce an owner"


def test_an_authority_named_inside_a_function_is_not_the_files_own_claim() -> None:
    """Module-level only. A mention in a body is a reference, not a declaration."""
    source = "def configure():\n    LOCAL_AUTHORITY = 'NOT-MINE'\n    return LOCAL_AUTHORITY\n"
    assert authority.declared_authority(source) == ("", "")


def test_an_annotated_module_constant_is_still_a_declaration() -> None:
    token, symbol = authority.declared_authority('GATE_AUTHORITY: str = "OWNER-9"\n')
    assert (token, symbol) == ("OWNER-9", "GATE_AUTHORITY")


# ------------------------------------------------------------------------------- Ω-A-02: contract


def test_a_declaration_that_names_a_path_claims_it(make_repo: Callable[..., Path]) -> None:
    """Discovered both ways: the declarations are walked, and the paths read from their bytes."""
    repository = make_repo(
        {
            "00-GOV/PROG-007/prog-declaration.json": (
                '{"programme": {"id": "PROG-007"}, "governs": ["alpha/core/claimed.py"]}'
            ),
            "alpha/core/claimed.py": "X = 1\n",
        }
    )
    contracts = authority.ContractIndex(str(repository))
    assert contracts.programme_for("alpha/core/claimed.py") == "PROG-007"
    owner, rule = _derive("alpha/core/claimed.py", contracts=contracts)
    assert (owner, rule) == ("PROG-007", authority.RULE_CONTRACT)


def test_a_declaration_key_that_is_a_path_is_indexed_too(
    make_repo: Callable[..., Path],
) -> None:
    repository = make_repo(
        {
            "00-GOV/PROG-008/x-authority.json": '{"files": {"alpha/keyed.py": {"role": "engine"}}}',
            "alpha/keyed.py": "X = 1\n",
        }
    )
    assert authority.ContractIndex(str(repository)).programme_for("alpha/keyed.py") == "PROG-008"


def test_an_unparseable_declaration_loses_precision_and_never_totality(
    make_repo: Callable[..., Path],
) -> None:
    """Each programme gate validates its own declaration; skipping one still yields an owner."""
    repository = make_repo(
        {
            "00-GOV/PROG-009/prog-declaration.json": "{ not json",
            "alpha/core/x.py": "X = 1\n",
        }
    )
    contracts = authority.ContractIndex(str(repository))
    assert contracts.programme_for("alpha/core/x.py") == ""
    owner, _rule = _derive("alpha/core/x.py", contracts=contracts)
    assert owner


def test_only_declaration_shaped_filenames_are_read(make_repo: Callable[..., Path]) -> None:
    """Bounded on purpose: otherwise one file's authority would depend on another file's size."""
    repository = make_repo(
        {
            "00-GOV/PROG-010/some-report.json": '{"governs": ["alpha/core/x.py"]}',
            "alpha/core/x.py": "X = 1\n",
        }
    )
    assert authority.ContractIndex(str(repository)).programme_for("alpha/core/x.py") == ""


def test_a_file_named_like_a_governance_home_is_not_walked_as_one(
    make_repo: Callable[..., Path],
) -> None:
    """``00-NOTES`` matching the home SHAPE does not make it a directory to descend into.

    The index walks whatever ``00-[A-Z]+`` names, and the repository root is not curated, so the
    guard has to survive a plain file sitting there. Without it the walk raises
    ``NotADirectoryError`` and every artifact's authority becomes unavailable because somebody
    committed a note.
    """
    repository = make_repo({"alpha/core/x.py": "X = 1\n"})
    (repository / "00-NOTES").write_text("not a governance home\n", encoding="utf-8")
    contracts = authority.ContractIndex(str(repository))
    assert contracts.declarations == ()
    assert contracts.programme_for("alpha/core/x.py") == ""


def test_an_absurdly_nested_declaration_terminates_rather_than_recursing_forever() -> None:
    """The depth bound, exercised at the depth that trips it.

    A declaration is somebody else's document and this package parses it defensively: the bound
    is what stops one programme's pathological JSON from becoming this measurement's stack
    overflow. Twelve levels deep the path is still found; thirteen and the walk stops, which is
    a LOSS OF PRECISION and never a loss of totality — the ancestry rules below are unconditional.
    """

    def nest(depth: int) -> object:
        node: object = {"subject": "alpha/deep.py"}
        for _ in range(depth):
            node = {"child": node}
        return node

    assert "alpha/deep.py" in authority._strings(nest(10))
    assert authority._strings(nest(40)) == []


# --------------------------------------------------------------------------- Ω-A-03: programme home


def test_a_programme_home_is_itself_the_authority() -> None:
    owner, rule = _derive("00-MASTER/UCI-000001/uci_engine.py")
    assert (owner, rule) == ("UCI-000001", authority.RULE_ANCESTRY_HOME)


def test_the_home_rule_is_a_shape_so_a_new_governance_tree_is_matched() -> None:
    """No list of homes. ``00-QUANTUM/PROG-1/`` is matched by the rule written today."""
    owner, rule = _derive("00-QUANTUM/PROG-1/engine.py")
    assert (owner, rule) == ("PROG-1", authority.RULE_ANCESTRY_HOME)


# ------------------------------------------------------------------------- Ω-A-04: execution graph


def test_an_invoked_artifact_is_owned_through_the_planes_that_invoke_it() -> None:
    owner, rule = _derive(
        "tools/run.py", invoking_planes={"tools/run.py": frozenset({"make", "ci"})}
    )
    assert rule == authority.RULE_EXECUTION
    assert owner == f"{authority.REPOSITORY_AUTHORITY}::ci+make"


# ------------------------------------------------------------------------ Ω-A-05: governance graph


def test_a_single_agreeing_importer_passes_its_owner_down() -> None:
    owner, rule = _derive(
        "alpha/core/x.py", importer_authorities={"alpha/core/x.py": frozenset({"OWNER-1"})}
    )
    assert (owner, rule) == ("OWNER-1", authority.RULE_GOVERNANCE)


def test_disagreeing_importers_do_not_pick_a_winner() -> None:
    """Two claimants is not one owner, so the chain falls through rather than choosing."""
    owner, rule = _derive(
        "alpha/core/x.py",
        importer_authorities={"alpha/core/x.py": frozenset({"OWNER-1", "OWNER-2"})},
    )
    assert rule == authority.RULE_ANCESTRY_MODULE
    assert owner == "alpha.core"


# ------------------------------------------------------------------------ Ω-A-06/07: the ancestry


def test_the_capability_package_is_the_unit_of_custody() -> None:
    owner, rule = _derive("alpha/core/deep/nested.py")
    assert (owner, rule) == ("alpha.core", authority.RULE_ANCESTRY_MODULE)


def test_a_file_directly_under_a_tree_is_owned_by_the_tree() -> None:
    owner, rule = _derive("alpha/module.py")
    assert (owner, rule) == ("alpha", authority.RULE_ANCESTRY_MODULE)


def test_the_last_rule_is_unconditional() -> None:
    """This is what makes the function TOTAL, and totality is the whole Ω-2 claim."""
    owner, rule = _derive("weird file.py")
    assert (owner, rule) == (authority.REPOSITORY_AUTHORITY, authority.RULE_REPOSITORY)


def test_no_input_combination_yields_an_empty_authority_without_a_transient_declaration() -> None:
    for path in (
        "a.py",
        "a/b.py",
        "a/b/c.py",
        "00-X/P/e.py",
        "not-an-identifier/x.py",
        "weird name/deep/x.py",
    ):
        owner, rule = _derive(path)
        assert owner, f"{path} produced no owner via {rule}"


# ------------------------------------------------------------------------------------- transient


def test_a_declared_transient_is_the_only_route_to_no_authority() -> None:
    owner, rule = _derive("alpha/scratch.py", transient={"alpha/scratch.py": "generated in-run"})
    assert (owner, rule) == ("", authority.RULE_TRANSIENT)


def test_totality_is_asserted_and_names_the_offenders() -> None:
    with pytest.raises(OmegaError, match="not total"):
        authority.assert_total({"alpha/orphan.py": ("", authority.RULE_REPOSITORY)}, {})


def test_a_declared_transient_satisfies_totality() -> None:
    authority.assert_total(
        {"alpha/scratch.py": ("", authority.RULE_TRANSIENT)},
        {"alpha/scratch.py": "generated in-run"},
    )


# ------------------------------------------------------------------ the real repository, measured


def test_the_real_repository_has_no_authority_free_artifact() -> None:
    """Ω-2's success criterion over the actual population: 100%, asserted rather than reported."""
    from engine.universal_discovery import surface

    omega = surface.build(".")
    orphans = [a.path for a in omega.artifacts if not a.authority and a.disposition != "TRANSIENT"]
    assert not orphans, f"authority coverage is not 100%: {orphans[:10]}"
    assert omega.totals["authority_coverage_percent"] == 100.0


def test_the_real_repository_needs_no_authority_of_last_resort() -> None:
    """Stronger than totality: every artifact is claimed by something narrower than the fallback.

    Named separately because the fallback existing is what makes the function total, while the
    fallback being UNUSED is what makes the derivation informative. A repository where every file
    resolved to Ω-A-07 would have 100% coverage and no information.
    """
    from engine.universal_discovery import surface

    omega = surface.build(".")
    last_resort = [a.path for a in omega.artifacts if a.authority_rule == authority.RULE_REPOSITORY]
    assert (
        not last_resort
    ), f"{len(last_resort)} artifacts fell through to the unconditional rule: {last_resort[:10]}"
