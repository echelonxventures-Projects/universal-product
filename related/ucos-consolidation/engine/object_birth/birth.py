"""UOBC-000001 Part 02 — identity derivation and the birth event.

This module is where "creation is not file generation, creation is an identity birth
event" becomes executable. :func:`derive_identity` answers *what is this object's
identity* using nothing but the namespace and the local name — no path, no clock, no
counter, no filesystem access — so it can be called at stage ``UOBC-S-04`` when no
artifact exists yet. That is the whole point: an identity you can only compute by
looking at a file is an address.

The derivation is not implemented here. It is delegated verbatim to
``engine/uckp/identity.py``, which the repository's authority alignment declares the
**SUPREME** ``CONSTITUTIONAL_OBJECT`` identity plane ("role: SUPREME — this IS
UCKP-ART-05"). Delegating rather than reimplementing is what keeps this contract a
*binding* of the one identity authority instead of a second one.

Two consequences worth stating, because they are the reason the four prohibitions are
provable rather than aspirational:

* **Renaming is not an identity act.** Identity has no path input, so moving a file
  cannot change it. The previous architecture had to treat a rename as retire-and-
  reissue precisely because identity was path-keyed.
* **Evolution cannot replace identity.** Owner, state, content and location are all
  recorded but none is an identity input, so an evolved object derives the same URN
  it was born with. :func:`evolve` proves it by re-deriving.
"""

from __future__ import annotations

from engine.object_birth.model import BirthContract, BirthError, BirthRecord
from engine.uckp.identity import UniversalIdentity, urn_for, uuid_for


def derive_identity(namespace: str, local_name: str) -> str:
    """Return the Universal Unique Identity for ``namespace``/``local_name``.

    Pure and total: no clock, no path, no counter, no I/O. Calling it twice with the
    same inputs returns the same answer in any process, on any machine, in any
    century — which is what makes a birth record replayable.
    """
    identity = UniversalIdentity.mint(namespace, local_name)
    identity.require_intact()
    return identity.urn


def identity_uuid(urn: str) -> str:
    """Return the deterministic RFC 4122 v5 UUID of ``urn``."""
    return uuid_for(urn)


def birth(
    contract: BirthContract,
    *,
    namespace: str,
    local_name: str,
    owner: str,
    creation_timestamp: str,
    creation_context: dict[str, str],
    parent_identity: str | None,
    lifecycle_binding: str,
    initial_state: str,
    certification_boundary: str,
    root: bool = False,
) -> BirthRecord:
    """Conduct a birth event and return its record.

    Identity is derived first, from the two declared identity inputs alone, before
    any artifact is instantiated by the caller. Every refusal below is a declared
    law, not defensive programming:

    Raises:
        BirthError: the namespace is undeclared (``UOBC-L-05`` — an undeclared
            namespace is an invented one), the initial state is inadmissible, a
            non-root object declares no parent (``UOBC-F-06``), or the context is
            empty (``UOBC-S-02`` produced nothing).
    """
    if contract.namespace_owner(namespace) is None:
        raise BirthError(
            "namespace is not declared in the birth contract; "
            "a namespace is admitted by declaration, never at a call site",
            subject=namespace,
        )
    if initial_state not in contract.initial_states:
        raise BirthError(
            "initial state is not admissible at birth "
            f"(declared: {', '.join(contract.initial_states)})",
            subject=initial_state,
        )
    if not creation_context:
        raise BirthError(
            "creation_context is empty; context assimilation produced nothing",
            subject=local_name,
        )
    if parent_identity is None and not root:
        raise BirthError(
            "parent_identity is absent and the object is not declared a root",
            subject=local_name,
        )

    universal_id = derive_identity(namespace, local_name)

    return BirthRecord(
        universal_id=universal_id,
        namespace=namespace,
        owner=owner,
        creation_timestamp=creation_timestamp,
        creation_context=tuple(sorted((str(k), str(v)) for k, v in creation_context.items())),
        parent_identity=parent_identity,
        lifecycle_binding=lifecycle_binding,
        initial_state=initial_state,
        certification_boundary=certification_boundary,
    )


def evolve(
    record: BirthRecord,
    *,
    owner: str | None = None,
    lifecycle_binding: str | None = None,
    certification_boundary: str | None = None,
) -> BirthRecord:
    """Return the record of an evolved object, under the **same** identity.

    Only the three fields the contract marks mutable may change. The identity is
    re-derived from the original namespace and local name and compared, so
    ``UOBC-L-07`` is enforced by recomputation rather than by trusting the caller not
    to pass a new id.

    Raises:
        BirthError: re-derivation does not reproduce the original identity, which
            would mean the identity had been replaced during evolution.
    """
    local_name = local_name_of(record.universal_id)
    rederived = derive_identity(record.namespace, local_name)
    if rederived != record.universal_id:
        raise BirthError(
            "evolution would replace identity",
            subject=f"{record.universal_id} -> {rederived}",
        )
    return BirthRecord(
        universal_id=record.universal_id,
        namespace=record.namespace,
        owner=record.owner if owner is None else owner,
        creation_timestamp=record.creation_timestamp,
        creation_context=record.creation_context,
        parent_identity=record.parent_identity,
        lifecycle_binding=(
            record.lifecycle_binding if lifecycle_binding is None else lifecycle_binding
        ),
        initial_state=record.initial_state,
        certification_boundary=(
            record.certification_boundary
            if certification_boundary is None
            else certification_boundary
        ),
    )


def local_name_of(urn: str) -> str:
    """Return the local name carried by ``urn``.

    Raises:
        BirthError: the string is not a UCKO URN of the declared shape.
    """
    parts = urn.split(":")
    if len(parts) != 5 or ":".join(parts[:3]) != "urn:ucos:ucko":
        raise BirthError("not a UCKO universal identity", subject=urn)
    return parts[4]


def namespace_of(urn: str) -> str:
    """Return the namespace carried by ``urn``.

    Raises:
        BirthError: the string is not a UCKO URN of the declared shape.
    """
    parts = urn.split(":")
    if len(parts) != 5 or ":".join(parts[:3]) != "urn:ucos:ucko":
        raise BirthError("not a UCKO universal identity", subject=urn)
    return parts[3]


def expected_urn(namespace: str, local_name: str) -> str:
    """Return the URN these inputs must produce, without minting."""
    return urn_for(namespace, local_name)
