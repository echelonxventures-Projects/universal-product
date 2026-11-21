"""UCPA-000001 Part 01 — the declaration model.

Every primitive, standing, facet reduction, projection and law is DATA in
``00-MASTER/UCPA-000001/ucpa-declaration.json``. This module rehydrates that data and
refuses to construct a contract that could not be measured. It contains no primitive
name, no facet name, no ``ONT-*`` id, no path and no law text: rehydrating a declaration
that has lost a section fails here rather than producing a gate that silently measures
less.

Two structural rules are worth stating, because they are what separates this from a
checklist.

:meth:`AlignmentContract.validate` refuses **both** directions. A law naming a check that
does not exist is manual governance wearing the costume of enforcement. A check that
exists but no law claims is dead code that looks like a gate — the same defect ``GP-4``
records for a flag that is declared and never read.

:meth:`AlignmentContract.extended_with` exists so that ``UCPA-L-07`` can be *measured*
rather than asserted. Openness that is only claimed in prose is indistinguishable from a
closed enumeration, so the contract must be able to admit a primitive it has never seen
and remain usable, with every existing primitive untouched.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, replace
from typing import Any

from engine.uckp.payload import canonical_payload

#: The standing a primitive may hold. AXIOM is supreme as ground but is not an
#: addressable node in the layered derivation tree; LAYER is a point an object may be
#: anchored to. Which primitive holds which is declared, never decided here.
AXIOM = "AXIOM"
LAYER = "LAYER"

#: The roles a projection may hold. AUTHORITY owns the ontology; RATIFICATION_RECORD
#: records its adjudication; PROJECTION restates it and must reduce to it; SUPERSEDED
#: restates a form the ratification replaced. Which site holds which is declared.
ROLE_AUTHORITY = "AUTHORITY"
ROLE_SUPERSEDED = "SUPERSEDED"


class AlignmentError(RuntimeError):
    """The declaration or contract is unusable. A FAULT, never a verdict."""

    def __init__(self, message: str, *, subject: str | None = None) -> None:
        super().__init__(message if subject is None else f"{message}: {subject}")
        self.subject = subject


def _require_mapping(doc: Any, section: str) -> Mapping[str, Any]:
    """Return ``doc[section]`` as a mapping, or fail closed."""
    value = doc.get(section) if isinstance(doc, Mapping) else None
    if not isinstance(value, Mapping):
        raise AlignmentError("declaration section is absent or not a mapping", subject=section)
    return value


def _require_sequence(doc: Any, section: str) -> Sequence[Any]:
    """Return ``doc[section]`` as a non-empty list, or fail closed."""
    value = doc.get(section) if isinstance(doc, Mapping) else None
    if not isinstance(value, list) or not value:
        raise AlignmentError(
            "declaration section is absent or not a non-empty list", subject=section
        )
    return value


def _require_text(entry: Mapping[str, Any], key: str, context: str) -> str:
    """Return a non-empty string field, or fail closed."""
    value = entry.get(key)
    if not isinstance(value, str) or not value.strip():
        raise AlignmentError(f"{context}: field {key!r} is absent or empty")
    return value


@dataclass(frozen=True, slots=True)
class Primitive:
    """One constitutional primitive, as the canonical register declares it."""

    identifier: str
    element: str
    standing: str
    layer_order: int | None
    ratified_by: str
    basis: str

    @property
    def is_axiom(self) -> bool:
        """True when this primitive is the ground rather than an addressable layer."""
        return self.standing == AXIOM

    @classmethod
    def of(cls, entry: Mapping[str, Any]) -> Primitive:
        """Rehydrate a primitive, refusing an unusable standing or layer order."""
        identifier = _require_text(entry, "id", "primitive")
        standing = _require_text(entry, "standing", identifier)
        if standing not in (AXIOM, LAYER):
            raise AlignmentError(
                "primitive standing is not a declared standing", subject=identifier
            )
        order = entry.get("layer_order")
        if standing == LAYER and not isinstance(order, int):
            raise AlignmentError("a layer primitive declares no layer order", subject=identifier)
        if standing == AXIOM and order is not None:
            raise AlignmentError(
                "the axiom is not a layer and may hold no order", subject=identifier
            )
        return cls(
            identifier=identifier,
            element=_require_text(entry, "element", identifier),
            standing=standing,
            layer_order=order if isinstance(order, int) else None,
            ratified_by=_require_text(entry, "ratified_by", identifier),
            basis=_require_text(entry, "basis", identifier),
        )


@dataclass(frozen=True, slots=True)
class RatifiedStanding:
    """One row of the ratification record, and the standing it requires."""

    supersession_id: str
    element: str
    requires_standing: str
    evidence_phrase: str

    @classmethod
    def of(cls, entry: Mapping[str, Any]) -> RatifiedStanding:
        """Rehydrate a ratified-standing row."""
        supersession_id = _require_text(entry, "supersession_id", "ratified standing")
        context = f"{supersession_id}/{entry.get('element')}"
        standing = _require_text(entry, "requires_standing", context)
        if standing not in (AXIOM, LAYER):
            raise AlignmentError("required standing is not a declared standing", subject=context)
        return cls(
            supersession_id=supersession_id,
            element=_require_text(entry, "element", context),
            requires_standing=standing,
            evidence_phrase=_require_text(entry, "evidence_phrase", context),
        )


@dataclass(frozen=True, slots=True)
class Reduction:
    """One facet, and the primitive whose obligation it discharges."""

    facet: str
    primitive: str
    basis: str

    @classmethod
    def of(cls, entry: Mapping[str, Any]) -> Reduction:
        """Rehydrate a reduction row, refusing one that carries no reasoning."""
        facet = _require_text(entry, "facet", "reduction")
        return cls(
            facet=facet,
            primitive=_require_text(entry, "primitive", facet),
            basis=_require_text(entry, "basis", facet),
        )


@dataclass(frozen=True, slots=True)
class Projection:
    """One site that states or restates the root ontology, and its role."""

    identifier: str
    path: str
    role: str
    superseded_by: str | None

    @classmethod
    def of(cls, entry: Mapping[str, Any]) -> Projection:
        """Rehydrate a projection."""
        identifier = _require_text(entry, "id", "projection")
        role = _require_text(entry, "role", identifier)
        superseded_by = entry.get("superseded_by")
        if superseded_by is not None and not isinstance(superseded_by, str):
            raise AlignmentError("superseded_by is present but not a path", subject=identifier)
        return cls(
            identifier=identifier,
            path=_require_text(entry, "path", identifier),
            role=role,
            superseded_by=superseded_by,
        )


@dataclass(frozen=True, slots=True)
class Law:
    """One alignment law, and the check that computes it."""

    law_id: str
    title: str
    statement: str
    check: str

    @classmethod
    def of(cls, entry: Mapping[str, Any]) -> Law:
        """Rehydrate a law, refusing one that names no check."""
        law_id = _require_text(entry, "id", "law")
        return cls(
            law_id=law_id,
            title=_require_text(entry, "title", law_id),
            statement=_require_text(entry, "statement", law_id),
            check=_require_text(entry, "check", law_id),
        )


@dataclass(frozen=True, slots=True)
class OntologySource:
    """The files that own the ontology, its ratification and its owner binding."""

    canonical_owner: str
    owner_binding: str
    owner_binding_id: str
    ratification_record: str
    constituent_act: str

    @classmethod
    def of(cls, entry: Mapping[str, Any]) -> OntologySource:
        """Rehydrate the source block."""
        return cls(
            canonical_owner=_require_text(entry, "canonical_owner", "ontology_source"),
            owner_binding=_require_text(entry, "owner_binding", "ontology_source"),
            owner_binding_id=_require_text(entry, "owner_binding_id", "ontology_source"),
            ratification_record=_require_text(entry, "ratification_record", "ontology_source"),
            constituent_act=_require_text(entry, "constituent_act", "ontology_source"),
        )


@dataclass(frozen=True, slots=True)
class Openness:
    """The probe that proves the primitive set is not a closed enumeration."""

    probe_id: str
    probe_element: str
    probe_standing: str

    @classmethod
    def of(cls, entry: Mapping[str, Any]) -> Openness:
        """Rehydrate the openness probe."""
        standing = _require_text(entry, "probe_standing", "openness")
        if standing not in (AXIOM, LAYER):
            raise AlignmentError("probe standing is not a declared standing", subject=standing)
        return cls(
            probe_id=_require_text(entry, "probe_id", "openness"),
            probe_element=_require_text(entry, "probe_element", "openness"),
            probe_standing=standing,
        )


@dataclass(frozen=True, slots=True)
class SelfApplication:
    """The primitive this programme itself reduces to, and the law measuring it."""

    reduces_to: str
    basis: str
    measured_by: str

    @classmethod
    def of(cls, entry: Mapping[str, Any]) -> SelfApplication:
        """Rehydrate the self-application block."""
        return cls(
            reduces_to=_require_text(entry, "reduces_to", "self_application"),
            basis=_require_text(entry, "basis", "self_application"),
            measured_by=_require_text(entry, "measured_by", "self_application"),
        )


#: Parsed fields deliberately outside the certification identity, each with the reason it
#: cannot reach a verdict. EMPTY, and that is the honest state rather than an oversight: every
#: field of :class:`AlignmentContract` is a value some law reads, and the contract holds no
#: source path — it is rehydrated from an already-parsed document, so there is nothing
#: reader-dependent to exclude.
DIGEST_EXCLUSIONS: Mapping[str, str] = {}


@dataclass(frozen=True, slots=True)
class AlignmentContract:
    """The whole declaration, rehydrated and structurally usable."""

    artifact_id: str
    name: str
    version: str
    authority: str
    principle: str
    source: OntologySource
    primitives: tuple[Primitive, ...]
    ratified_standing: tuple[RatifiedStanding, ...]
    reductions: tuple[Reduction, ...]
    projections: tuple[Projection, ...]
    openness: Openness
    self_application: SelfApplication
    laws: tuple[Law, ...]

    def digest_payload(self) -> dict[str, Any]:
        """This contract's certification identity: every parsed field, minus declared exclusions.

        Inclusion is the DEFAULT, derived from :func:`dataclasses.fields`, so a field added to
        this contract is inside the identity on the day it is written rather than on the day
        somebody remembers to add it to a list. Omitting one requires naming it in
        :data:`DIGEST_EXCLUSIONS` with the reason it cannot reach a verdict, and the suite fails
        in BOTH directions — on an undeclared omission and on an exclusion naming a field this
        contract no longer has.
        """
        return canonical_payload(self, exclude=tuple(DIGEST_EXCLUSIONS))

    @classmethod
    def of(cls, document: Mapping[str, Any]) -> AlignmentContract:
        """Rehydrate a contract from a parsed declaration."""
        return cls(
            artifact_id=_require_text(document, "artifact_id", "declaration"),
            # THESE FOUR WERE DECLARED AND UNPARSED, WHICH MADE THEM UNENFORCEABLE AND
            # UNCERTIFIABLE AT ONCE. `ucpa-declaration.json` states a name, a version, an
            # authority and a principle about itself, and this contract read none of them — so
            # UEC-L-13 measured that rewriting the declared authority left the certification
            # identity byte-identical at 6c09cf89…, and one digest certified two declarations
            # claiming different authorities. Parsing them puts them inside the identity.
            name=_require_text(document, "name", "declaration"),
            version=_require_text(document, "version", "declaration"),
            authority=_require_text(document, "authority", "declaration"),
            principle=_require_text(document, "principle", "declaration"),
            source=OntologySource.of(_require_mapping(document, "ontology_source")),
            primitives=tuple(
                Primitive.of(e) for e in _require_sequence(document, "primitive_binding")
            ),
            ratified_standing=tuple(
                RatifiedStanding.of(e) for e in _require_sequence(document, "ratified_standing")
            ),
            reductions=tuple(
                Reduction.of(e) for e in _require_sequence(document, "facet_reduction")
            ),
            projections=tuple(Projection.of(e) for e in _require_sequence(document, "projections")),
            openness=Openness.of(_require_mapping(document, "openness")),
            self_application=SelfApplication.of(_require_mapping(document, "self_application")),
            laws=tuple(Law.of(e) for e in _require_sequence(document, "laws")),
        )

    def primitive(self, identifier: str) -> Primitive | None:
        """Return the bound primitive with ``identifier``, or None."""
        for candidate in self.primitives:
            if candidate.identifier == identifier:
                return candidate
        return None

    def extended_with(self, primitive: Primitive) -> AlignmentContract:
        """Return a copy admitting ``primitive`` by append.

        Admission is an append operation: no existing primitive is renumbered,
        reclassified or reordered. ``UCPA-L-07`` measures the result rather than
        trusting the claim.
        """
        if self.primitive(primitive.identifier) is not None:
            raise AlignmentError(
                "the probe primitive is already bound", subject=primitive.identifier
            )
        return replace(self, primitives=self.primitives + (primitive,))

    def validate(self, implemented: frozenset[str]) -> list[str]:
        """Return every structural problem, refusing in both directions."""
        problems: list[str] = []
        claimed = {law.check for law in self.laws}
        for law in sorted(self.laws, key=lambda entry: entry.law_id):
            if law.check not in implemented:
                problems.append(
                    f"{law.law_id}: names check {law.check!r}, which is not implemented"
                )
        for orphan in sorted(implemented - claimed):
            problems.append(f"check {orphan!r} is implemented but no law claims it")
        seen: set[str] = set()
        for law in self.laws:
            if law.law_id in seen:
                problems.append(f"{law.law_id}: declared more than once")
            seen.add(law.law_id)
        return problems


__all__ = [
    "AXIOM",
    "LAYER",
    "AlignmentContract",
    "AlignmentError",
    "Law",
    "Openness",
    "OntologySource",
    "Primitive",
    "Projection",
    "RatifiedStanding",
    "ROLE_AUTHORITY",
    "ROLE_SUPERSEDED",
    "Reduction",
    "SelfApplication",
]
