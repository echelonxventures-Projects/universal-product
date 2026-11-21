"""UCOS-NUC-001 Part 11 — the ownership authority, resolved from CEU.

Repository truth before this module
-----------------------------------
Ownership was decided by ``StructuralRole.may_own_capability``, whose whole body was
``return self is StructuralRole.NUCLEUS``. That made the *source code* the ownership
authority: no registration could grant ownership, no registration could withdraw it, and a
fourth structural role could be admitted to the vocabulary while remaining unable to own
anything, because the enum — not the constitution — held the answer.

Meanwhile :mod:`engine.ceu` already held the same fact properly: ``nucleus`` is a
registered classification holding the registered faculty ``own-capability``, discoverable
by :meth:`~engine.ceu.existence.ExistenceRegistry.holding`. Two authorities over one
question, which the Single Authority Principle forbids.

This module removes the second one. It is the **adapter**, not a third authority: it
answers ownership questions by querying the CEU substrate and holds no ownership rule of
its own. Every ownership decision in :mod:`engine.nucleus` now routes through here, and
:class:`~engine.nucleus.law.StructuralRole` becomes a projection whose ownership
properties read this module rather than themselves.

Direction of derivation
-----------------------
Legacy values derive from CEU. Never the reverse. If the CEU catalogue stopped declaring
``own-capability`` on ``nucleus``, ownership would stop being granted here — which is the
observable difference between an authority and a projection, and is asserted directly in
the convergence tests.

Caching
-------
The seeded substrate is deterministic, so the *derived answer* is cached rather than
recomputed per call. The cache holds immutable frozensets, never the registry itself: a
shared mutable registry handed to callers would be a fourth way for ownership to be
changed without registration.
"""

from __future__ import annotations

from functools import cache
from typing import Any

from engine.ceu.catalog import bootstrap
from engine.ceu.existence import ExistenceRegistry

#: The registered faculty that grants the right to own a capability.
FACULTY_OWN_CAPABILITY = "own-capability"

#: The registered faculty that grants the right to select units into a composition.
FACULTY_SELECT_UNITS = "select-units"

#: The CEU form under which structural roles are registered as classifications.
CLASSIFICATION_FORM = "classification"


def ownership_authority() -> ExistenceRegistry:
    """A freshly built CEU substrate — the authority every question here resolves against.

    Returns a new registry each call, deliberately: the substrate is append-only and
    handing out a shared mutable one would let a caller grant itself ownership without
    registering anything. Callers wanting the *answers* should use the cached predicates
    below rather than this.
    """
    return bootstrap()


@cache
def roles_holding(faculty: str) -> frozenset[str]:
    """The classification keys holding ``faculty``, discovered from the CEU registry.

    Cached because the seeded catalogue is deterministic; the cached value is immutable.
    """
    registry = bootstrap()
    return frozenset(
        registry.resolve(identifier).key
        for identifier in registry.holding(faculty, form=CLASSIFICATION_FORM)
    )


def registered_roles() -> frozenset[str]:
    """Every classification the CEU substrate registers — the open role vocabulary."""
    registry = bootstrap()
    return frozenset(u.key for u in registry.units(form=CLASSIFICATION_FORM))


def holds(role: Any, faculty: str) -> bool:
    """True iff ``role`` holds ``faculty`` according to the CEU registry.

    Fails closed: a role the substrate does not register holds nothing. That is the
    correct answer rather than an error, because the question "may this own?" always has
    a safe answer, and the unsafe one is "yes by default".
    """
    return _role_key(role) in roles_holding(faculty)


def may_own_capability(role: Any) -> bool:
    """The one ownership question, answered by the one ownership authority."""
    return holds(role, FACULTY_OWN_CAPABILITY)


def may_select_units(role: Any) -> bool:
    """Whether ``role`` may select registered units into a composition."""
    return holds(role, FACULTY_SELECT_UNITS)


def owning_roles() -> frozenset[str]:
    """Every role that may own — discovered, not enumerated."""
    return roles_holding(FACULTY_OWN_CAPABILITY)


def selecting_roles() -> frozenset[str]:
    """Every role that may select units — discovered, not enumerated."""
    return roles_holding(FACULTY_SELECT_UNITS)


def _role_key(role: Any) -> str:
    """The classification key for a role, accepting an enum member or a bare string."""
    return str(getattr(role, "value", role)).strip()


def to_document() -> dict[str, Any]:
    """The ownership authority as a deterministic, diffable document.

    This is the evidence that ownership is registry-derived: it names the substrate the
    answers came from, and lists which roles hold which faculty as *measured*, not as
    declared by this module.
    """
    registry = bootstrap()
    roles = sorted(registered_roles())
    return {
        "schema": "ucos-nucleus-ownership-authority",
        "version": "1.0.0",
        "authority": "engine.ceu",
        "classification_form": CLASSIFICATION_FORM,
        "faculties": [FACULTY_OWN_CAPABILITY, FACULTY_SELECT_UNITS],
        "roles": [
            {
                "role": role,
                "may_own_capability": may_own_capability(role),
                "may_select_units": may_select_units(role),
            }
            for role in roles
        ],
        "owning_roles": sorted(owning_roles()),
        "selecting_roles": sorted(selecting_roles()),
        "authority_digest": registry.digest(),
        "closed_set": False,
        "upper_limit": None,
    }


__all__ = [
    "FACULTY_OWN_CAPABILITY",
    "FACULTY_SELECT_UNITS",
    "CLASSIFICATION_FORM",
    "ownership_authority",
    "roles_holding",
    "registered_roles",
    "holds",
    "may_own_capability",
    "may_select_units",
    "owning_roles",
    "selecting_roles",
    "to_document",
]
