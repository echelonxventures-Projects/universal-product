"""The founding universal meta-types — expressed as DATA, not code branches.

The mission's IMPLEMENTATION SCOPE lists the universal abstractions the kernel *may*
establish. Constitutionally, each of these is not a special class in the kernel; it is a
registered :class:`~engine.kernel.meta.MetaObject` classified by the reflective root
meta-type. They are the *founding* meta-types: the vocabulary the kernel is seeded with.

This list is DATA. Adding, removing, or amending a founding meta-type is an edit to this
table, and *any* provider or future programme may register further meta-types at runtime
without touching this file at all. Nothing here enumerates a domain, a provider, a
technology, or an Earth concept — only the universal engineering abstractions themselves.
"""

from __future__ import annotations

#: Each entry: (natural_key, name, description). Ordered for legibility only; the registry
#: orders deterministically by key regardless of insertion order.
FOUNDING_METATYPES: tuple[tuple[str, str, str], ...] = (
    ("MetaObject", "Universal Meta-Object", "The single universal thing everything is."),
    ("Identity", "Universal Identity", "That by which a thing is deterministically named."),
    ("Registry", "Universal Registry", "The governed home in which a thing is admitted and found."),
    ("Classification", "Universal Classification", "The assignment of a thing to a meta-type."),
    ("Capability", "Universal Capability", "Something the platform or a provider can do."),
    ("Contract", "Universal Contract", "A named, versioned interface a thing satisfies."),
    ("Context", "Universal Context", "The frame of reference within which a thing has meaning."),
    ("Policy", "Universal Policy", "A declarative constraint over things and their behaviour."),
    ("Rule", "Universal Rule", "Operational logic evaluated under governance."),
    ("Constraint", "Universal Constraint", "An invariant a thing must satisfy to be admitted."),
    ("Relationship", "Universal Relationship", "A governed, directed connection between things."),
    ("Governance", "Universal Governance", "The authority by which decisions are made."),
    ("Lifecycle", "Universal Lifecycle", "The governed progression of a thing through states."),
    ("Provider", "Universal Provider", "An implementer that realises an abstraction concretely."),
    ("Composition", "Universal Composition", "The assembly of things into larger things."),
    ("Knowledge", "Universal Knowledge", "Structured, homed meaning about things."),
    ("Validation", "Universal Validation", "The determination that a thing meets its constraints."),
    ("Certification", "Universal Certification", "An attested determination of fitness."),
    ("Evidence", "Universal Evidence", "The proof that supports a claim or determination."),
    ("Versioning", "Universal Versioning", "Identity preserved across governed change."),
    ("Evolution", "Universal Evolution", "Governed change without loss of identity."),
    ("ExecutionModel", "Universal Execution Model", "A governed manner of carrying out work."),
)

#: The namespace the founding meta-types are seeded into.
FOUNDING_NAMESPACE = "umk.metatype"


def founding_metatype_keys() -> tuple[str, ...]:
    """The natural keys of the founding meta-types (deterministically ordered)."""
    return tuple(sorted(key for key, _name, _desc in FOUNDING_METATYPES))


__all__ = ["FOUNDING_METATYPES", "FOUNDING_NAMESPACE", "founding_metatype_keys"]
