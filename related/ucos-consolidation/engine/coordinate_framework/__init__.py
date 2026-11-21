"""UCCFA-000001 — the Universal Coordinate Framework Alignment programme.

The root ontology has a gate; the coordinate framework beside it had none. ONT-05 through
ONT-10 appear in no ``.py`` file in this repository, so every field of
``uccfa-declaration.json`` was unenforced text — which is the condition UEC-L-07 counts and
the condition the declaration itself exists to complain about. This package is the consumer
that makes those five coordinates measurable.

It owns no ontology. ``01-WORKING/ONTOLOGY-REGISTER.md`` PART B owns the coordinates and
SUP-02 fixes their standing; every law here reads those surfaces and can introduce nothing.

THE PACKAGE IS THE IMPORT SURFACE, and that is a measured requirement rather than a style.
When this module re-exported nothing, every consumer named a SUBMODULE — ``.contract``,
``.gate`` — and nothing named the package, so Ω-4 counted it among the artifacts "no import,
plane or entry point reaches": 52 against a best-ever 51, on a ratchet that may fall and
never rise. A package whose root nothing imports is unreachable by the language's own
reckoning, whatever runs underneath it.
"""

from engine.coordinate_framework.contract import (
    CHECK_PREFIX,
    CoordinateAlignmentError,
    CoordinateContract,
    assess,
    declaration_path,
    load_contract,
    load_declaration,
    repo_root,
)

__all__ = [
    "CHECK_PREFIX",
    "CoordinateAlignmentError",
    "CoordinateContract",
    "assess",
    "declaration_path",
    "load_contract",
    "load_declaration",
    "repo_root",
]
