"""UCOS-NUC-001 Part 01 — the Nucleus Ownership Law (D-07).

Repository truth before this module existed
-------------------------------------------
``00-MASTER/UCOS-NUCLEUS-001/02-NUCLEUS-CONSTITUTIONAL-MODEL.md`` §1 declares the
Nucleus "the atomic unit of canonical ownership". That is an **affirmative** clause.
A repository-wide search returned no **negative** clause: nothing anywhere stated
that a *layer* may not own a capability, and nothing stated that a *composition*
(Commerce, ERP, a marketplace, a named product) is not a nucleus. Both absences are
enforceable gaps: an affirmative rule alone cannot refuse a wrong owner.

This module supplies exactly those missing clauses and nothing else. It creates no
second nucleus definition, no second registry, no second identifier scheme and no
second lifecycle. The definition of a Nucleus remains NUCLEUS-001 §1; the
completeness contract remains ``UCOS-UNC-001`` (NF-01…NF-36); identifiers remain
minted by :mod:`engine.registry.universal.identity`.

Openness
--------
The clause set and the invariant set are **tuples of data**, and the structural role
vocabulary is admitted through :mod:`engine.uckp.vocabulary` (Article 17), so a
future structural role is a registration and not an edit here. No function in this
package branches on a specific nucleus, layer, composition or domain name.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from engine.uckp.canonical import content_hash

#: The immutable identity of the nucleus ownership law.
LAW_ID = "UCOS-NUC-LAW-0001"

#: Versioned so the law can be *extended* without any prior determination changing.
LAW_VERSION = "1.0.0"

#: The supreme clause of nucleus ownership. Every clause below elaborates it.
SUPREMACY_CLAUSE = (
    "Capabilities are owned by Nuclei and by nothing else. A Layer organises and owns "
    "nothing. A Composition selects Nuclei and owns nothing. Every capability resolves "
    "to exactly one owning Nucleus, or the repository is in violation."
)


class StructuralRole(str, Enum):
    """A **projection** of the CEU classifications, kept as a compatibility surface.

    This enum is no longer an authority. Its members are three of the classifications
    registered in :mod:`engine.ceu.catalog`, and its ownership properties resolve through
    :mod:`engine.nucleus.authority`, which queries the CEU registry. Legacy values derive
    from CEU; never the reverse.

    What that buys, concretely: ownership can be granted or withdrawn by *registration*.
    Remove ``own-capability`` from the ``nucleus`` classification and
    :attr:`may_own_capability` becomes ``False`` here, with no edit to this file. When it
    was ``self is StructuralRole.NUCLEUS``, no registration could have changed it.

    The enum remains closed at three members, and that is a projection limitation rather
    than an ownership one: a fourth *classification* is registered in the CEU catalogue
    and is discoverable through :func:`engine.nucleus.authority.registered_roles`, but
    cannot yet be carried by a legacy ``SubjectRecord``. Consumers needing the open set
    should read the authority module directly.
    """

    #: Operates. Registered as holding ``own-capability`` in the CEU catalogue.
    NUCLEUS = "nucleus"
    #: Organises. A filing structure over subjects. Holds no ownership faculty.
    LAYER = "layer"
    #: Composes. Registered as holding ``select-units``. Holds no ownership faculty.
    COMPOSITION = "composition"

    @property
    def may_own_capability(self) -> bool:
        """True iff the CEU registry grants this classification the ownership faculty."""
        from engine.nucleus import authority

        return authority.may_own_capability(self)

    @property
    def may_select_nuclei(self) -> bool:
        """True iff the CEU registry grants this classification the selection faculty."""
        from engine.nucleus import authority

        return authority.may_select_units(self)

    @classmethod
    def coerce(cls, value: Any, *, at: str = "subject") -> StructuralRole:
        """Return the role for ``value`` or fail closed (never default)."""
        if isinstance(value, cls):
            return value
        try:
            return cls(str(value))
        except ValueError as exc:
            from engine.nucleus.errors import StructuralValidationError

            raise StructuralValidationError(
                "unknown structural role",
                at=at,
                value=str(value),
                allowed=[r.value for r in cls],
            ) from exc

    @classmethod
    def values(cls) -> tuple[str, ...]:
        return tuple(role.value for role in cls)


@dataclass(frozen=True, slots=True)
class Clause:
    """One clause of the nucleus ownership law."""

    clause_id: str
    title: str
    statement: str
    refuses: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "clause_id": self.clause_id,
            "title": self.title,
            "statement": self.statement,
            "refuses": self.refuses,
        }


@dataclass(frozen=True, slots=True)
class Invariant:
    """A property an implementation must *prove* by measurement, not assert."""

    invariant_id: str
    name: str
    statement: str
    blocking: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "invariant_id": self.invariant_id,
            "name": self.name,
            "statement": self.statement,
            "blocking": self.blocking,
        }


#: The clauses of the nucleus ownership law (DATA — extend by appending, never edit).
OWNERSHIP_CLAUSES: tuple[Clause, ...] = (
    Clause(
        "NL-01",
        "Nuclei own capabilities",
        "A capability's owner SHALL be a subject registered in the NUCLEUS role. A "
        "nucleus owns its capability domain, its ontology, its taxonomy, its "
        "identifiers, its governance, its contracts, its runtime, its certification, "
        "its measurement, its validation, its verification, its lineage, its "
        "bookkeeping, its intelligence, its evolution and its constitutional lifecycle.",
        refuses="a capability whose owner holds any role other than NUCLEUS",
    ),
    Clause(
        "NL-02",
        "Layers own nothing",
        "A Layer is an organisational structure. A Layer SHALL NOT own a capability, "
        "truth, an authority, a registry, governance, a contract, an identity, a "
        "runtime, intelligence or an evolution path. Layers organise; nuclei operate.",
        refuses="any ownership assignment whose owner holds the LAYER role",
    ),
    Clause(
        "NL-03",
        "Compositions own nothing",
        "A Composition SHALL be constructed entirely by selecting registered Nuclei "
        "and adding configuration. A Composition SHALL NOT own a capability and SHALL "
        "NOT introduce capability logic of its own.",
        refuses="any ownership assignment whose owner holds the COMPOSITION role",
    ),
    Clause(
        "NL-04",
        "Exactly one owner",
        "Every registered capability SHALL resolve to exactly one owning Nucleus. "
        "Zero owners is a gap (AC-012); two or more is an overlap (AC-011). Both are "
        "violations of equal severity.",
        refuses="a capability with no owner, or with more than one owner",
    ),
    Clause(
        "NL-05",
        "A domain aggregate is a Composition, never a Nucleus",
        "A subject that is realised by selecting two or more Nuclei is a Composition. "
        "Commerce, retail, marketplace, ERP, CRM, LMS, a named product, a named "
        "company platform, a sector vertical and a civilisational platform are "
        "Compositions. None of them is a Nucleus, and none of them may own a "
        "capability.",
        refuses="a NUCLEUS-role subject that declares composed nuclei",
    ),
    Clause(
        "NL-06",
        "Role is declared, classification is derived and checked",
        "A subject SHALL declare its structural role, and the declared role SHALL "
        "agree with the role derived from its own declaration. A subject that selects "
        "nuclei derives the COMPOSITION role; a subject that owns a capability domain "
        "derives the NUCLEUS role; a subject that only contains other subjects derives "
        "the LAYER role. Disagreement is refused, never reconciled silently.",
        refuses="a declared role that contradicts the derived role",
    ),
    Clause(
        "NL-07",
        "No platform-specific capability",
        "No capability SHALL be specific to a composition. A capability that names a "
        "composition in its own domain is a configuration of a nucleus capability, not "
        "a capability.",
        refuses="a capability whose domain resolves to a registered composition",
    ),
    Clause(
        "NL-08",
        "Composition closure",
        "Every Nucleus a Composition selects SHALL itself be registered, and the "
        "selection graph SHALL be acyclic. A composition that selects an unregistered "
        "nucleus is not composable and does not exist.",
        refuses="a composition selecting an unregistered nucleus, or a selection cycle",
    ),
    Clause(
        "NL-09",
        "Nothing exists unless registered",
        "A Nucleus, Layer, Composition, Capability or ownership assignment that is not "
        "registered under a universal identifier does not exist for any constitutional "
        "purpose. Registration is the act that creates existence (AC-002).",
        refuses="a reference to an unregistered subject",
    ),
    Clause(
        "NL-10",
        "Ownership is append-only and lineage-preserving",
        "An ownership assignment SHALL NOT be deleted or silently rewritten. Ownership "
        "moves by supersession, which records the prior owner, the new owner and the "
        "authority for the move (AC-009).",
        refuses="a re-assignment that does not name the assignment it supersedes",
    ),
)


#: The invariants the authority must *measure*. Zero-tolerance by construction.
OWNERSHIP_INVARIANTS: tuple[Invariant, ...] = (
    Invariant(
        "NUC-INV-01",
        "layer_owned_capabilities",
        "The count of capabilities owned by a LAYER-role subject is zero.",
    ),
    Invariant(
        "NUC-INV-02",
        "composition_owned_capabilities",
        "The count of capabilities owned by a COMPOSITION-role subject is zero.",
    ),
    Invariant(
        "NUC-INV-03",
        "capabilities_unowned",
        "The count of registered capabilities with no owning nucleus is zero.",
    ),
    Invariant(
        "NUC-INV-04",
        "capabilities_multi_owned",
        "The count of registered capabilities with more than one owner is zero.",
    ),
    Invariant(
        "NUC-INV-05",
        "misclassified_subjects",
        "The count of subjects whose declared role contradicts their derived role is zero.",
    ),
    Invariant(
        "NUC-INV-06",
        "unregistered_selections",
        "The count of composition selections naming an unregistered nucleus is zero.",
    ),
    Invariant(
        "NUC-INV-07",
        "selection_cycles",
        "The count of cycles in the composition selection graph is zero.",
    ),
    Invariant(
        "NUC-INV-08",
        "composition_specific_capabilities",
        "The count of capabilities whose domain resolves to a composition is zero.",
    ),
    Invariant(
        "NUC-INV-09",
        "subjects_without_identifier",
        "The count of registered subjects lacking a universal identifier is zero.",
    ),
    Invariant(
        "NUC-INV-10",
        "orphan_ownership_assignments",
        "The count of ownership assignments naming an unregistered subject is zero.",
    ),
)


def structural_role_terms() -> tuple[tuple[str, str], ...]:
    """The ``ucos.structural-role`` vocabulary content as ``(term_id, definition)``.

    Returned as data so :mod:`engine.nucleus.registry` can register it through the
    single vocabulary authority rather than declaring a parallel term set here.
    """
    return (
        (
            StructuralRole.NUCLEUS.value,
            "a canonical capability authority; the atomic unit of canonical ownership "
            "and the only lawful owner of a capability",
        ),
        (
            StructuralRole.LAYER.value,
            "an organisational structure over subjects; owns nothing",
        ),
        (
            StructuralRole.COMPOSITION.value,
            "a selection of registered nuclei plus configuration; owns nothing",
        ),
    )


def clause(clause_id: str) -> Clause:
    """Return the clause with ``clause_id`` or fail closed."""
    for item in OWNERSHIP_CLAUSES:
        if item.clause_id == clause_id:
            return item
    from engine.nucleus.errors import StructuralValidationError

    raise StructuralValidationError(
        "no such ownership clause",
        clause_id=clause_id,
        allowed=[c.clause_id for c in OWNERSHIP_CLAUSES],
    )


def to_document() -> dict[str, Any]:
    """The whole law as a deterministic, machine-readable document."""
    return {
        "schema": "ucos-nucleus-ownership-law",
        "law_id": LAW_ID,
        "version": LAW_VERSION,
        "supremacy_clause": SUPREMACY_CLAUSE,
        "structural_roles": [
            {
                "role": role.value,
                "may_own_capability": role.may_own_capability,
                "may_select_nuclei": role.may_select_nuclei,
            }
            for role in StructuralRole
        ],
        "clauses": [c.to_dict() for c in OWNERSHIP_CLAUSES],
        "invariants": [i.to_dict() for i in OWNERSHIP_INVARIANTS],
    }


def digest() -> str:
    """The content digest of the law, computed with the one canonical primitive."""
    return content_hash(to_document())


__all__ = [
    "LAW_ID",
    "LAW_VERSION",
    "SUPREMACY_CLAUSE",
    "StructuralRole",
    "Clause",
    "Invariant",
    "OWNERSHIP_CLAUSES",
    "OWNERSHIP_INVARIANTS",
    "structural_role_terms",
    "clause",
    "to_document",
    "digest",
]
