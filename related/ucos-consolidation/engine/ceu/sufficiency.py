"""UCOS-CEU-001 Part 03 — the sufficiency test (CEU-038).

Constitutional growth is not a goal; constitutional *sufficiency* is. CEU-038 states the
rule: if a proposed concept can be represented through the twelve primitives, it must
enter through evolution — as registered data — and not by adding a constitutional root.

The rule is worth little as prose, because "could this have been data?" is exactly the
question a tired engineer answers with "no" at 6pm. So it is mechanical here:
:func:`assess` takes a concept and the primitives that express it and returns a verdict,
and :func:`assess_registry` runs the verdict over every form a registry actually holds.
A form that declares no expressing primitive is a claimed new root, and the report says so
by name.

This module adds no root of its own. The twelve primitives are the ones CEU-038
enumerates; they are held as data and the module reads them.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from typing import Any

from engine.ceu.errors import CEUError
from engine.uckp.canonical import content_hash

#: The twelve constitutional primitives of CEU-038. A concept expressible through any of
#: them enters by evolution. Held as data, and appended to only by constitutional act —
#: which is itself the thing this module exists to make expensive and visible.
PRIMITIVES: tuple[str, ...] = (
    "existence",
    "identity",
    "context",
    "classification",
    "relationship",
    "topology",
    "capability",
    "knowledge",
    "governance",
    "evidence",
    "lineage",
    "evolution",
)

#: The attribute a form declares its expressing primitives in.
ATTR_EXPRESSED_BY = "expressed_by"

#: The two verdicts. There is no third: a concept either fits the existing primitives or
#: it does not, and "partially" would be the loophole every new root walks through.
VERDICT_EVOLUTION = "ENTERS-BY-EVOLUTION"
VERDICT_NEW_ROOT = "REQUIRES-NEW-ROOT"


def unknown_primitives(expressed_by: Iterable[str]) -> tuple[str, ...]:
    """Named primitives that are not among the twelve."""
    return tuple(sorted({p for p in expressed_by if p not in PRIMITIVES}))


def assess(concept: str, expressed_by: Sequence[str]) -> dict[str, Any]:
    """Decide how one concept must enter the architecture.

    Args:
        concept: what is being proposed.
        expressed_by: the primitives that already express it. Empty means the proposer
            claims none of the twelve can carry it.

    Returns:
        A verdict document. ``ENTERS-BY-EVOLUTION`` means: register it, do not write a
        root. ``REQUIRES-NEW-ROOT`` is the answer that has to be *argued for*, and the
        document records exactly which primitives were considered so the argument is
        reviewable rather than asserted.

    Raises:
        CEUError: the concept is unnamed, or a named primitive is not one of the twelve —
            an unrecognised primitive is a typo or a smuggled root, and silently ignoring
            it would let both through.
    """
    if not isinstance(concept, str) or not concept.strip():
        raise CEUError("a sufficiency assessment must name its concept")
    unknown = unknown_primitives(expressed_by)
    if unknown:
        raise CEUError(
            "a concept may only be expressed through the declared primitives",
            concept=concept,
            unknown=list(unknown),
            primitives=list(PRIMITIVES),
        )
    via = tuple(p for p in PRIMITIVES if p in set(expressed_by))
    return {
        "concept": concept.strip(),
        "expressed_by": list(via),
        "verdict": VERDICT_EVOLUTION if via else VERDICT_NEW_ROOT,
        "enters_by_evolution": bool(via),
        "primitives_considered": list(PRIMITIVES),
    }


def require_sufficient(concept: str, expressed_by: Sequence[str]) -> dict[str, Any]:
    """Fail-closed form of :func:`assess`, for a caller adding a form.

    Raises:
        CEUError: the concept claims to need a new constitutional root.
    """
    verdict = assess(concept, expressed_by)
    if not verdict["enters_by_evolution"]:
        raise CEUError(
            "this concept is representable only by a new constitutional root; "
            "CEU-038 requires it to enter by evolution instead",
            concept=concept,
            primitives=list(PRIMITIVES),
        )
    return verdict


def assess_registry(registry: Any) -> dict[str, Any]:
    """Run the sufficiency test over every form a registry holds.

    A form declaring no expressing primitive is reported as a claimed root. The root form
    itself is exempt and says so explicitly: it *is* the existence primitive, and a
    self-describing root that had to justify itself in terms of something else would be a
    root with a root.
    """
    claimed_roots: list[str] = []
    assessments: list[dict[str, Any]] = []
    for form in registry.forms():
        if form.key == registry.root_form:
            assessments.append(
                {
                    "concept": form.key,
                    "expressed_by": ["existence"],
                    "verdict": VERDICT_EVOLUTION,
                    "enters_by_evolution": True,
                    "is_root_form": True,
                }
            )
            continue
        declared = form.tuple_attribute(ATTR_EXPRESSED_BY)
        verdict = assess(form.key, declared)
        verdict["is_root_form"] = False
        assessments.append(verdict)
        if not verdict["enters_by_evolution"]:
            claimed_roots.append(form.key)
    return {
        "schema": "ucos-ceu-sufficiency",
        "version": "1.0.0",
        "primitives": list(PRIMITIVES),
        "forms_assessed": len(assessments),
        "assessments": assessments,
        "claimed_new_roots": claimed_roots,
        "sufficient": not claimed_roots,
    }


def digest(report: Mapping[str, Any]) -> str:
    return content_hash(dict(report))


__all__ = [
    "PRIMITIVES",
    "ATTR_EXPRESSED_BY",
    "VERDICT_EVOLUTION",
    "VERDICT_NEW_ROOT",
    "unknown_primitives",
    "assess",
    "require_sufficient",
    "assess_registry",
    "digest",
]
