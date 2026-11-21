"""ZX-02's detector, pinned in both directions.

adr/0042 records why both are required: a detector that cannot catch is useless, and one that
cannot spare is worse — false positives make a floor unreachable, because the last entries resist
every fix and the only way to close the count is to "correct" things that were never defects.

Here that risk is concrete. A filename convention and a type decision share the same syntax, and
a detector that flagged both would demand the removal of `name.startswith("test_") and
name.endswith(".py")` — pytest's own contract, where the filename IS the right thing to ask.
"""

from __future__ import annotations

import json

import pytest

from engine.zero_class.entity_derivation import (
    TYPE_DECISION_CEILING,
    asks_the_filename,
    roots,
    type_decisions,
    type_decisions_in,
)


def _module(tmp_path, source: str):
    path = tmp_path / "subject.py"
    path.write_text(source, encoding="utf-8")
    return path


@pytest.mark.parametrize(
    ("label", "source", "caught"),
    [
        (
            "a bare type decision",
            'def f(p):\n    if p.endswith(".py"):\n        return 1\n    return 0\n',
            True,
        ),
        (
            "a bare type decision in a comprehension",
            'def f(paths):\n    return [p for p in paths if p.endswith(".py")]\n',
            True,
        ),
        (
            "a filename CONVENTION — the name is the right question",
            'def f(n):\n    return n.startswith("test_") and n.endswith(".py")\n',
            False,
        ),
        (
            "a path CONVENTION",
            'def f(p):\n    return p.startswith(".github/workflows/") and p.endswith(".yml")\n',
            False,
        ),
        (
            "a DECLARED SCOPE naming several kinds",
            'def f(n):\n    return n.endswith((".yml", ".yaml", ".sh", ".mk"))\n',
            False,
        ),
        (
            "no suffix test at all",
            'def f(artifact):\n    return artifact.artifact_type.name == "PYTHON"\n',
            False,
        ),
    ],
)
def test_the_detector_separates_a_type_decision_from_a_convention(
    tmp_path, label, source, caught
) -> None:
    assert asks_the_filename(_module(tmp_path, source)) is caught, label


def test_the_derived_form_is_never_flagged(tmp_path) -> None:
    """The remedy must not itself be a finding, or the ceiling could never reach zero."""
    remedied = _module(
        tmp_path,
        "def f(artifact):\n" '    return artifact.artifact_type.name == "PYTHON"\n',
    )
    assert type_decisions_in(remedied) == ()


def test_type_decisions_may_only_fall() -> None:
    """The ratchet. A new filename-typed decision is refused with the file and line named."""
    measured = type_decisions()
    assert len(measured) <= TYPE_DECISION_CEILING, (
        "a module decided a type by filename. Ask the classifier instead — "
        "engine/omega_infinite/classification.py types an artifact by four declared rules with "
        "the suffix consulted last:\n  " + "\n  ".join(measured)
    )


def test_the_ceiling_equals_the_measurement() -> None:
    """A ceiling above the measurement leaves room a regression could occupy silently."""
    assert len(type_decisions()) == TYPE_DECISION_CEILING


def test_the_scan_skips_a_declared_root_that_is_not_there_and_every_cache(tmp_path) -> None:
    """THE ROOTS ARE DECLARED AND THE FILESYSTEM IS WHAT IS THERE.

    Both skips run on every scan of this repository and neither had ever been exercised on a
    tree where they MATTER. A declared root that is absent is an ordinary state — a partial
    checkout, an export, a root declared before it was created — and raising there would make
    the detector unable to measure anything rather than measure what exists. The
    ``__pycache__`` skip is the other half: a compiled tree holds ``.py`` files that were
    written by nobody, and counting them would attribute a type decision to a file no author
    can fix.
    """
    (tmp_path / "00-MASTER" / "UCON-000001").mkdir(parents=True)
    (tmp_path / "00-MASTER" / "UCON-000001" / "ucon-declaration.json").write_text(
        json.dumps({"audit": {"roots": ["present", "never-created"]}}), encoding="utf-8"
    )
    subject = tmp_path / "present"
    subject.mkdir()
    (subject / "real.py").write_text('if path.endswith(".json"):\n    pass\n', encoding="utf-8")
    cached = subject / "__pycache__"
    cached.mkdir()
    (cached / "real.py").write_text('if path.endswith(".json"):\n    pass\n', encoding="utf-8")

    found = type_decisions(str(tmp_path))

    assert [entry.split(":")[0] for entry in found] == ["present/real.py"]


def test_a_declaration_naming_no_audit_root_is_a_fault(tmp_path) -> None:
    """THE ROOTS ARE DATA, AND AN EMPTY DECLARATION IS A FAULT AND NEVER AN EMPTY SCAN.

    The declaration always names roots here, so the refusal had no case — and it is what keeps
    a measurement of zero from meaning "nothing was scanned". A detector that returned no
    findings because it looked nowhere reports the same number as one that looked everywhere
    and found nothing, and the ceiling would then ratchet on the strength of a misread file.
    """
    declaration = tmp_path / "00-MASTER" / "UCON-000001" / "ucon-declaration.json"
    declaration.parent.mkdir(parents=True)

    for empty in ({"audit": {"roots": []}}, {"audit": {}}, {"audit": {"roots": "engine"}}):
        declaration.write_text(json.dumps(empty), encoding="utf-8")
        with pytest.raises(RuntimeError, match="declares no audit roots"):
            roots(tmp_path)
