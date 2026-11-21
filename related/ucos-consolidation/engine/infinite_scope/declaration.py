"""UISD-000001 — the declaration's certification identity, on the uniform interface.

WHY THIS MODULE EXISTS. ``engine/infinite_scope`` measured eleven laws and returned a verdict
that was attributable to NO state: nothing in the package minted a digest, so two different
declarations reaching two opposite verdicts produced reports that could not be told apart, and
nothing could later say WHICH declaration a recorded PASS was a pass of. UEC-000001 named that
condition — ``declarations_without_a_certification_identity`` counted this package and
``engine/root_ontology`` — and a declaration with no certification identity cannot be certified
at all, whatever its laws report.

IT ADDS NO SECOND AUTHORITY OVER THE DECLARATION. ``contract.load_declaration`` still reads the
file and ``InfiniteScopeContract.from_declaration`` still rehydrates it; :func:`parse` delegates
to both and holds no parsing of its own. A second parser would be a second reading of one
document, and the two would drift.

THE IDENTITY IS COMPLETE BY INVERSION, NEVER BY PROJECTION — see
:meth:`InfiniteScopeContract.digest_payload`. ``UEC-L-13`` performs the mutation experiment
against this package from the moment it exposes this interface, so the identity is proven
complete by execution rather than asserted by this docstring.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from engine.infinite_scope.contract import load_declaration
from engine.infinite_scope.model import DIGEST_EXCLUSIONS, InfiniteScopeContract


def parse(document: Mapping[str, Any], *, source: str = "") -> InfiniteScopeContract:
    """Rehydrate a declaration document into the contract that carries the identity.

    ``source`` is part of the uniform interface and is deliberately unused: this contract is
    rehydrated from an already-parsed document and holds nothing reader-dependent, so its
    identity does not vary with where the document was read from. Accepting the parameter is
    what lets a test ASSERT that property rather than assume it.
    """
    return InfiniteScopeContract.from_declaration(document)


def load(path: str | None = None) -> InfiniteScopeContract:
    """Load and rehydrate the committed declaration."""
    return parse(load_declaration(path), source=path or "")


__all__ = ["DIGEST_EXCLUSIONS", "InfiniteScopeContract", "load", "parse"]
