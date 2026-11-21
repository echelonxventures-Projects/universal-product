"""URKE-000001 Part 03 — composition. Where a type would otherwise have been added.

A condition is expressed as one state plus axis values plus qualifier values plus a domain. That is
the whole mechanism that let forty-one drafted lifecycle states collapse to seven and twenty-six
unknown classes collapse to a domain attribute: what used to be a class is now a coordinate.

:func:`express` is total over the declared vocabularies and refuses anything outside them. It fills
every axis and every qualifier from its declared initial value before applying overrides, so an
expression is always complete — a partially specified condition would otherwise read as agnosticism
when it actually means "nobody said".
"""

from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType
from typing import Any

from engine.recursive_knowledge.declaration import Condition, Declaration
from engine.recursive_knowledge.model import RecursiveKnowledgeError


class CompositionError(RecursiveKnowledgeError):
    """The composition names something the declaration does not declare. A fault."""


def axis_initial(declaration: Declaration) -> Mapping[str, str]:
    """Every axis at its declared starting value."""
    return MappingProxyType({spec.axis: spec.initial for spec in declaration.lifecycle_axes})


def qualifier_initial(declaration: Declaration) -> Mapping[str, str]:
    """Every qualifier at its declared starting value."""
    return MappingProxyType({spec.qualifier: spec.initial for spec in declaration.qualifiers})


def qualify(
    declaration: Declaration, qualifiers: Mapping[str, str] | None = None
) -> Mapping[str, str]:
    """Return a complete qualifier map, refusing any undeclared qualifier or value."""
    resolved = dict(qualifier_initial(declaration))
    for name, value in dict(qualifiers or {}).items():
        spec = declaration.qualifier(name)
        if value not in spec.values:
            raise CompositionError(
                f"{value!r} is not a declared value of qualifier {name!r}; declared values are "
                f"{', '.join(spec.values)}"
            )
        resolved[name] = value
    return MappingProxyType(resolved)


def axes_for(declaration: Declaration, axes: Mapping[str, str] | None = None) -> Mapping[str, str]:
    """Return a complete axis map, refusing any undeclared axis or value."""
    resolved = dict(axis_initial(declaration))
    for name, value in dict(axes or {}).items():
        spec = declaration.axis(name)
        if value not in spec.values:
            raise CompositionError(
                f"{value!r} is not a declared value of axis {name!r}; declared values are "
                f"{', '.join(spec.values)}"
            )
        resolved[name] = value
    return MappingProxyType(resolved)


def express(
    declaration: Declaration,
    *,
    state: str,
    domain: str,
    axes: Mapping[str, str] | None = None,
    qualifiers: Mapping[str, str] | None = None,
) -> Mapping[str, Any]:
    """Express a condition as a composition. Refuses an undeclared state, domain, axis or "
    "qualifier."""
    declaration.state(state)
    declaration.domain(domain)
    return MappingProxyType(
        {
            "axes": axes_for(declaration, axes),
            "domain": domain,
            "qualifiers": qualify(declaration, qualifiers),
            "state": state,
        }
    )


def express_condition(declaration: Declaration, condition: Condition) -> Mapping[str, Any]:
    """Express a catalogued condition. The measurement behind the claim that nothing was lost."""
    return express(
        declaration,
        state=condition.state,
        domain=condition.domain,
        axes=condition.axes,
        qualifiers=condition.qualifiers,
    )


def signature(expression: Mapping[str, Any]) -> tuple[Any, ...]:
    """What the ledger can tell apart. Two conditions sharing one are a reported collision."""
    return (
        expression["state"],
        expression["domain"],
        tuple(sorted(dict(expression["qualifiers"]).items())),
        tuple(sorted(dict(expression["axes"]).items())),
    )


#: The role a module uses to reach the context profile. A code symbol, bound in the declaration.
SITUATION_ROLE = "situation"


def situate(declaration: Declaration, context_kind: str) -> Mapping[str, Any]:
    """The payload of a context subject: a kind and the root it ultimately sits in.

    Context is a subject with a profile, never a primitive. This function exists so the context
    payload is built in one place from declared data, which is what keeps the root from becoming a
    hardcoded planet somewhere in the call graph.
    """
    kinds = set(declaration.context_kind_ids)
    if context_kind not in kinds:
        raise CompositionError(f"{context_kind!r} is not a declared context kind")
    return MappingProxyType(
        {
            "context_kind": context_kind,
            "definition": declaration.context_root,
            "root": declaration.context_root,
        }
    )


__all__ = [
    "SITUATION_ROLE",
    "CompositionError",
    "axes_for",
    "axis_initial",
    "express",
    "express_condition",
    "qualifier_initial",
    "qualify",
    "signature",
    "situate",
]
