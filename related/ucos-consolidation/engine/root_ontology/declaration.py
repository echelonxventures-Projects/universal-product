"""UCPA-000001 — the declaration's certification identity, on the uniform interface.

WHY THIS MODULE EXISTS. ``engine/root_ontology`` measured eight laws and returned a verdict that
was attributable to NO state: nothing anywhere in the package minted a digest, so two different
declarations reaching two opposite verdicts produced reports that could not be told apart, and
nothing could later say WHICH declaration a recorded PASS was a pass of. UEC-000001 named that
condition — ``declarations_without_a_certification_identity`` counted this package and
``engine/infinite_scope`` — and a declaration with no certification identity cannot be certified
at all, whatever its laws report.

IT ADDS NO SECOND AUTHORITY OVER THE DECLARATION. ``contract.load_declaration`` still reads the
file and ``AlignmentContract.of`` still rehydrates it; :func:`parse` delegates to both and holds
no parsing of its own. A second parser would be a second reading of one document, and the two
would drift — which is the defect this repository refuses everywhere else.

THE IDENTITY IS COMPLETE BY INVERSION, NEVER BY PROJECTION. :meth:`AlignmentContract.digest_payload`
returns every parsed field, derived from :func:`dataclasses.fields`, minus the exclusions
``DIGEST_EXCLUSIONS`` names and states a reason for. The opposite convention — a hand-written
list of included keys — is not a hypothetical risk here: it is the measured defect this
repository has already paid for twice. ``engine/construct`` listed eleven keys and collapsed ten
to bare identifiers, so flipping ``blocking`` on ``UCON-L-01`` — the flag its own contract reads
to choose OPEN or CLOSED — left the declaration digest byte-identical at ``192c63af…``; and
``engine/recursive_knowledge`` left 101 of its 115 parsed fields outside the identity entirely.

``UEC-L-13`` performs that same mutation experiment against this package from the moment it
exposes this interface, so the identity is proven complete by execution rather than asserted by
this docstring.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from engine.root_ontology.contract import load_declaration
from engine.root_ontology.model import DIGEST_EXCLUSIONS, AlignmentContract


def parse(document: Mapping[str, Any], *, source: str = "") -> AlignmentContract:
    """Rehydrate a declaration document into the contract that carries the identity.

    ``source`` is part of the uniform interface and is deliberately unused: this contract is
    rehydrated from an already-parsed document and holds nothing reader-dependent, so its
    identity does not vary with where the document was read from. Accepting the parameter is
    what lets a test ASSERT that property rather than assume it.
    """
    return AlignmentContract.of(document)


def load(path: str | None = None) -> AlignmentContract:
    """Load and rehydrate the committed declaration."""
    return parse(load_declaration(path), source=path or "")


__all__ = ["DIGEST_EXCLUSIONS", "AlignmentContract", "load", "parse"]
