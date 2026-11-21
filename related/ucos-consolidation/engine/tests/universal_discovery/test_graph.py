"""Ω-3 — reachability is a relation over module identity, never over directory names."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import pytest

from engine.universal_discovery import discovery, graph
from engine.universal_discovery.model import OmegaError

# ------------------------------------------------------------------------------- edge extraction


def test_plain_and_from_imports_are_both_edges() -> None:
    edges, dynamic = graph.module_imports(
        "import json\nimport alpha.core\nfrom beta import module\n", "x"
    )
    assert {"json", "alpha.core", "beta", "beta.module"} <= edges
    assert dynamic == 0


def test_a_relative_import_is_resolved_against_the_importing_module() -> None:
    """``from . import x`` inside ``alpha.core.service`` names ``alpha.core.x``, not ``.x``."""
    edges, _dynamic = graph.module_imports("from . import helper\n", "alpha.core.service")
    assert "alpha.core.helper" in edges


def test_a_deeper_relative_import_walks_further_up() -> None:
    edges, _dynamic = graph.module_imports("from ..other import thing\n", "alpha.core.service")
    assert "alpha.other" in edges
    assert "alpha.other.thing" in edges


def test_a_dynamic_import_with_a_literal_argument_is_a_real_edge() -> None:
    """Resolvable, therefore measured. Ignoring it would understate the graph."""
    edges, dynamic = graph.module_imports(
        'import importlib\nm = importlib.import_module("alpha.core.service")\n', "x"
    )
    assert "alpha.core.service" in edges
    assert dynamic == 0


def test_a_dynamic_import_with_a_computed_argument_is_reported_not_guessed() -> None:
    """Pretending to resolve it would be the same lie as an enumeration: an unmeasured answer."""
    edges, dynamic = graph.module_imports(
        "import importlib\n\n\ndef load(name):\n    return importlib.import_module(name)\n", "x"
    )
    assert dynamic == 1
    assert not any(e.startswith("alpha") for e in edges)


def test_the_dunder_import_builtin_is_measured_the_same_way() -> None:
    literal, dynamic = graph.module_imports('__import__("alpha.core")\n', "x")
    assert "alpha.core" in literal and dynamic == 0
    _edges, computed = graph.module_imports("__import__(name)\n", "x")
    assert computed == 1


def test_a_module_that_does_not_parse_is_a_fault_not_a_leaf() -> None:
    """A leaf looks governed, so an unparseable file must not be able to look like one."""
    with pytest.raises(OmegaError, match="does not parse"):
        graph.module_imports("def broken(:\n", "alpha.broken")


# --------------------------------------------------------------------------------- the relation


def test_the_reverse_relation_records_only_tracked_targets(layered_repo: Path) -> None:
    """``import json`` is not an edge in THIS population, so the graph stays about this one."""
    root = str(layered_repo)
    paths = discovery.tracked_python(root)
    import_graph = graph.ImportGraph(root, paths)
    assert "json" not in import_graph.imported_by
    assert import_graph.imported_by["alpha.core.service"] == frozenset({"alpha.tests.test_service"})


def test_a_symbol_import_is_attributed_to_its_parent_module(layered_repo: Path) -> None:
    """A symbol import records ``...support.double``; the EDGE belongs to the parent module."""
    root = str(layered_repo)
    paths = discovery.tracked_python(root)
    import_graph = graph.ImportGraph(root, paths)
    assert "alpha.tests.test_service" in import_graph.imported_by["alpha.tests.support"]


def test_a_relative_import_inside_a_package_initialiser_means_the_package_itself() -> None:
    """The off-by-one this pair was written to catch. ``alpha/core/__init__.py`` is ``alpha.core``,
    and ``from . import helper`` inside it names ``alpha.core.helper`` — not ``alpha.helper``."""
    edges, _dynamic = graph.module_imports("from . import helper\n", "alpha.core", is_package=True)
    assert "alpha.core.helper" in edges


def test_the_graph_is_keyed_on_module_identity_so_relocation_preserves_it(
    make_repo: Callable[..., Path],
) -> None:
    """THE Ω-3 PROPERTY at the level of the graph itself.

    Two repositories holding the same modules under different directories produce the same
    relation, because an import names a module and not a place. The contents are renamed along with
    the paths, because that is what a real relocation does — leaving the imports pointing at the old
    root would test dangling references rather than location independence.
    """
    body = {
        "pkg/__init__.py": "",
        "pkg/a.py": "VALUE = 1\n",
        "pkg/b.py": "from pkg.a import VALUE\n",
    }
    first = make_repo(dict(body))
    relocated = make_repo(
        {
            path.replace("pkg/", "moved/"): text.replace("pkg.", "moved.")
            for path, text in body.items()
        }
    )

    def relation(repository: Path, prefix: str) -> dict[str, set[str]]:
        root = str(repository)
        paths = discovery.tracked_python(root)
        built = graph.ImportGraph(root, paths)
        return {
            module.replace(prefix, "P"): {i.replace(prefix, "P") for i in importers}
            for module, importers in built.imported_by.items()
        }

    assert relation(first, "pkg") == relation(relocated, "moved")
    assert relation(first, "pkg")["P.a"] == {"P.b"}, "the fixture proves nothing without an edge"


def test_imported_by_path_projects_the_relation_onto_paths(layered_repo: Path) -> None:
    root = str(layered_repo)
    paths = discovery.tracked_python(root)
    import_graph = graph.ImportGraph(root, paths)
    by_path = graph.imported_by_path(import_graph, paths)
    assert by_path["alpha/core/service.py"] == frozenset({"alpha/tests/test_service.py"})


def test_a_file_no_import_could_name_has_no_importers(layered_repo: Path) -> None:
    root = str(layered_repo)
    paths = discovery.tracked_python(root)
    import_graph = graph.ImportGraph(root, paths)
    assert import_graph.importers_of_path("00-GOV/PROG-001/prog_engine.py") == frozenset()


def test_an_unparseable_tracked_file_is_recorded_rather_than_crashing_the_run(
    make_repo: Callable[..., Path],
) -> None:
    """One broken file must not make the whole population unmeasurable — but it must be NAMED."""
    repository = make_repo({"alpha/good.py": "X = 1\n", "alpha/broken.py": "def f(:\n"})
    root = str(repository)
    paths = discovery.tracked_python(root)
    import_graph = graph.ImportGraph(root, paths)
    assert import_graph.unparsed == ("alpha/broken.py",)


# ---------------------------------------------------------------------------- orchestration


def test_orchestration_texts_are_walked_by_kind_not_listed(layered_repo: Path) -> None:
    texts = graph.orchestration_texts(str(layered_repo))
    assert "Makefile" in texts


def test_a_repository_with_no_orchestration_is_a_fault(
    make_repo: Callable[..., Path],
) -> None:
    """Every artifact would read as unreachable, so the measurement would be about nothing."""
    repository = make_repo({"alpha/module.py": "X = 1\n"})
    with pytest.raises(OmegaError, match="no orchestration text"):
        graph.orchestration_texts(str(repository))


@pytest.mark.parametrize(
    ("location", "plane"),
    [
        ("Makefile", graph.PLANE_MAKE),
        ("verify.sh", graph.PLANE_VERIFY),
        (".github/workflows/uci-gate.yml", graph.PLANE_CI),
        (".github/workflows/anything-new.yml", graph.PLANE_CI),
        ("scripts/tool.sh", graph.PLANE_PYTHON),
        # The unconditional tail. A text under none of the four declared plane locations is
        # still a plane, because the alternative is a location that reaches nothing — and an
        # artifact invoked from an unclassified text would then read as unreachable code.
        ("docs/RUNBOOK.md", graph.PLANE_PYTHON),
        ("Makefile.d/extra.mk", graph.PLANE_PYTHON),
    ],
)
def test_every_orchestration_text_maps_to_a_plane_type(location: str, plane: str) -> None:
    assert graph.plane_for(location) == plane


def test_a_location_under_no_declared_plane_still_names_one() -> None:
    """``plane_for`` is TOTAL, and the last line is what makes it so.

    ``Makefile.d/extra.mk`` is the case that proves the prefix test is a path test rather than a
    string test: it starts with the characters of ``Makefile`` and is not that file, so the
    ``make`` plane must not claim it.
    """
    assert graph.plane_for("Makefile.d/extra.mk") == graph.PLANE_PYTHON
    assert graph.plane_for("verify.sh.bak") == graph.PLANE_PYTHON
    assert graph.plane_for("verify.sh") == graph.PLANE_VERIFY


def test_planes_are_grouped_so_many_workflows_are_still_one_plane() -> None:
    """THE STRICTNESS. Ungrouped, adding a workflow would improve every reachability metric."""
    planes = graph.orchestrated_modules(
        {
            ".github/workflows/a.yml": "run: python3 -m alpha.core.service\n",
            ".github/workflows/b.yml": "run: python3 -m alpha.core.service\n",
            ".github/workflows/c.yml": "run: python3 -m alpha.core.service\n",
        }
    )
    assert planes["alpha.core.service"] == {graph.PLANE_CI}


def test_module_and_script_invocations_are_both_found() -> None:
    planes = graph.orchestrated_modules(
        {"Makefile": "t:\n\t@python3 -m alpha.core.service\n\t@python3 tools/run.py\n"}
    )
    assert planes["alpha.core.service"] == {graph.PLANE_MAKE}
    assert planes["tools/run.py"] == {graph.PLANE_MAKE}


def test_declared_console_entry_points_are_read(make_repo: Callable[..., Path]) -> None:
    repository = make_repo(
        {"alpha/cli.py": "def main():\n    return 0\n"},
        pyproject='[project.scripts]\nalpha = "alpha.cli:main"\n',
    )
    assert graph.console_entry_points(str(repository)) == frozenset({"alpha.cli"})


def test_an_unreadable_project_table_is_a_fault(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("= broken\n", encoding="utf-8")
    with pytest.raises(OmegaError, match="entry points are unreadable"):
        graph.console_entry_points(str(tmp_path))


def test_reading_an_absent_file_is_a_fault(tmp_path: Path) -> None:
    with pytest.raises(OmegaError, match="could not be read"):
        graph.read_text(str(tmp_path), "nothing/here.py")
