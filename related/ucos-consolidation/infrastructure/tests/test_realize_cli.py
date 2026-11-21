"""The command every Band-13 realization module publishes, invoked as a command.

WHY THIS FILE EXISTS. Eleven ``infrastructure/*_realize.py`` modules each end in a ``main``
that an operator (and the Makefile) runs as ``python -m infrastructure.<unit>_realize``. Six
of them had never been called: their argument parsing, their evidence write, their PASS/FAIL
line and — the arm that matters — the ``return 1`` that refuses a determination short of
COMPLETE were unexecuted. A fail-closed entry point that has only ever been read is an entry
point whose refusal is a claim.

The modules are DISCOVERED, not listed (UCKP-ART-08), so a twelfth realization unit is held
to this the moment it exists. The refusal is FORGED by replacing the module's own
``emit_evidence`` with one that reports a determination short of COMPLETE, because the
canonical exemplar is complete by construction and no input can make it otherwise — which is
exactly why the branch had never run.
"""

from __future__ import annotations

import json
import pkgutil
import sys
from typing import Any

import pytest

import infrastructure
from infrastructure import (  # noqa: F401 — imported so the walk below can resolve each one from sys.modules
    band13_realize,
    capability_realize,
    compute_realize,
    environment_realize,
    governance_realize,
    integration_realize,
    network_realize,
    resilience_realize,
    security_realize,
    storage_realize,
    topology_realize,
)


def _realize_modules() -> list[Any]:
    found = []
    for info in sorted(pkgutil.iter_modules(infrastructure.__path__), key=lambda i: i.name):
        if not info.name.endswith("_realize"):
            continue
        # RESOLVED THROUGH ``sys.modules``, NOT ``importlib.import_module``. A dynamic import
        # whose argument is computed is a site Ω-3 can measure no edge through, and Ω-4 holds
        # `unresolved_dynamic_sites` MONOTONIC — so importing the walk's own output would buy
        # this derivation at the cost of a permanently unmeasurable edge. Every module is
        # reached by the STATIC import above, so the lookup cannot miss; a module the header
        # does not name fails HERE, by name, which is the finding rather than a silent skip.
        module = sys.modules.get(f"infrastructure.{info.name}")
        assert module is not None, (
            f"infrastructure.{info.name} exists but no static import reaches it, so this walk "
            f"would silently skip it; name it in this module's header"
        )
        if hasattr(module, "main") and hasattr(module, "emit_evidence"):
            found.append(module)
    return found


MODULES = _realize_modules()
MODULE_IDS = [m.__name__.rsplit(".", 1)[-1] for m in MODULES]

NOT_COMPLETE: dict[str, Any] = {
    "determination": "NOT COMPLETE",
    "validation_accepted": False,
    "certified": False,
    "traceability_closed": False,
    "byte_identical": False,
}


def test_the_discovery_found_every_realization_unit():
    """A discovery that found nothing would make every test below vacuously green."""
    assert len(MODULES) >= 11


@pytest.mark.parametrize("module", MODULES, ids=MODULE_IDS)
def test_the_command_realizes_into_the_directory_it_was_given(module, tmp_path, capsys):
    assert module.main(["--evidence-dir", str(tmp_path)]) == 0
    out = capsys.readouterr().out
    summary, verdict = out.rsplit("\n[", 1)
    payload = json.loads(summary)
    assert payload["determination"] == "COMPLETE"
    assert payload["byte_identical"] is True
    assert verdict.startswith("PASS]")
    assert payload["determination"] in verdict
    assert (tmp_path / "realization-evidence.json").is_file()


@pytest.mark.parametrize("module", MODULES, ids=MODULE_IDS)
def test_the_command_refuses_a_determination_short_of_complete(
    module, tmp_path, capsys, monkeypatch
):
    monkeypatch.setattr(module, "emit_evidence", lambda _dir: dict(NOT_COMPLETE))
    assert module.main(["--evidence-dir", str(tmp_path)]) == 1
    out = capsys.readouterr().out
    assert "[FAIL]" in out
    assert "NOT COMPLETE" in out


@pytest.mark.parametrize("module", MODULES, ids=MODULE_IDS)
def test_a_determination_that_is_complete_only_in_name_is_still_refused(
    module, tmp_path, capsys, monkeypatch
):
    """The verdict is a conjunction over five independent facts, not a reading of one
    string: a summary that says COMPLETE while one of its own flags is false must not
    exit zero, or the word would be doing the work the flags are there to do."""
    monkeypatch.setattr(
        module,
        "emit_evidence",
        lambda _dir: {
            **NOT_COMPLETE,
            "determination": "COMPLETE",
            "byte_identical": True,
            "validation_accepted": True,
            "certified": True,
        },
    )
    assert module.main(["--evidence-dir", str(tmp_path)]) == 1
    assert "[FAIL]" in capsys.readouterr().out


@pytest.mark.parametrize("module", MODULES, ids=MODULE_IDS)
def test_the_default_evidence_directory_is_declared_and_never_the_frozen_corpus(module):
    default = str(module.DEFAULT_EVIDENCE_DIR)
    assert default
    assert not default.startswith(("00-BOOK", "00-SOURCE", "99-FREEZE"))


_WITH_FACETS = [m for m in MODULES if hasattr(m.realize(), "by_facet")]


@pytest.mark.parametrize(
    "module", _WITH_FACETS, ids=[m.__name__.rsplit(".", 1)[-1] for m in _WITH_FACETS]
)
def test_asking_a_multi_facet_result_for_a_facet_it_does_not_carry_is_refused(module):
    """A missing facet raises rather than returning the first realization, because a
    silently-substituted facet would attribute one construct's certification to another."""
    result = module.realize()
    known = result.namesake.construct.facet_value
    assert result.by_facet(known) is result.namesake
    with pytest.raises(KeyError):
        result.by_facet("a-facet-nothing-realizes")
