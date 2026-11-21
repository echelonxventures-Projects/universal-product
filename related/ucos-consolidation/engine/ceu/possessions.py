"""UCOS-CEU-001 Part 05 — the ten possessions (S-011, UCEP-007, Constitution Before Code).

"No implementation may introduce a concept that lacks constitutional representation" is a
rule about *code*, and rules about code are kept by gates rather than by intent. This
module is the gate. For every registered unit it measures ten possessions: identity,
dictionary, registry, context, governance, ownership, relationships, lineage, evolution
and evidence — declared as data in :data:`POSSESSIONS`, so an eleventh is a tuple entry.

Two design choices worth stating, because both could have been made the other way and the
easier way would have made the gate useless:

* **Governance is not satisfied by existing.** A unit possesses governance when some
  registered authority governs it — through a ``governs`` relationship or a declared
  ``governed_by`` — and not merely because it was registered. Most seeded units therefore
  *fail* this possession today, and the report says so by name. A gate tuned until it
  passes is a gate that measures nothing.
* **Context is a property of the substrate, not of the unit.** A registry is bound to one
  reality (the same contract :mod:`engine.nucleus.registry` uses), so either every unit in
  it is interpretable or none is. Reporting it per unit would imply a per-unit answer that
  does not exist.

The dictionary projection here mints nothing: it enumerates identifiers the registry
already assigned, through :class:`~engine.registry.universal.dictionary.IdentifierDictionary`.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from engine.ceu.errors import CEUError
from engine.ceu.existence import ExistenceRegistry
from engine.registry.universal.dictionary import IdentifierDictionary
from engine.registry.universal.identity import is_well_formed
from engine.uckp.canonical import content_hash

#: The attribute a unit may name its governing authority in, when no relationship does.
ATTR_GOVERNED_BY = "governed_by"

#: The relationship type read as conferring governance, when the catalogue declares one.
GOVERNS = "governs"

#: The relationship types read as conferring ownership and evidence, when declared.
OWNS = "owns"
EVIDENCES = "evidences"

#: The journal action that is a unit's genesis — the start of its evolution history.
ACTION_GENESIS = "register"

#: The ten possessions, as ``(key, statement)``. Data: an eleventh is a tuple entry, and
#: nothing below branches on a particular possession key.
POSSESSIONS: tuple[tuple[str, str], ...] = (
    ("identity", "A well-formed identifier minted by the one identity authority."),
    ("dictionary", "An entry in the assigned-identifier dictionary."),
    ("registry", "Resolvable in the registry that holds it."),
    ("context", "Interpreted within a resolved reference frame."),
    ("governance", "A registered authority answers for it."),
    ("ownership", "A registered owner answers for it, or it declares its classification."),
    ("relationships", "Participates in at least one registered relationship."),
    ("lineage", "At least one journal entry records how it came to be."),
    ("evolution", "A genesis event exists, so its history has a readable start."),
    ("evidence", "Something registered stands as evidence for it."),
)


def dictionary_for_existence(registry: ExistenceRegistry) -> IdentifierDictionary:
    """Project every registered unit into the assigned-identifier dictionary.

    A projection, not a second authority: every entry re-mints from the identity tuple the
    registry used, so :meth:`IdentifierDictionary.verify` proves the two agree rather than
    the dictionary asserting it.
    """
    dictionary = IdentifierDictionary()
    for unit in registry.units():
        dictionary.assign(
            unit.identity_kind,
            unit.namespace,
            f"{unit.form}:{unit.key}",
            owner=unit.classification,
            attributes={"form": unit.form, "key": unit.key},
        )
    return dictionary


def governed_units(registry: ExistenceRegistry) -> frozenset[str]:
    """Identifiers some registered authority answers for.

    Read from ``governs`` relationships where the catalogue declares that type, and from a
    unit's own ``governed_by``. Both are registry-driven; neither is inferred.
    """
    governed: set[str] = set()
    for unit in registry.units():
        declared = unit.attribute(ATTR_GOVERNED_BY)
        if declared and registry.find(str(declared)) is not None:
            governed.add(unit.universal_id)
        if unit.attribute("relationship_type") == GOVERNS:
            target = str(unit.attribute("target", ""))
            if registry.find(target) is not None:
                governed.add(target)
    return frozenset(governed)


def _targets_of(registry: ExistenceRegistry, relationship_type: str) -> frozenset[str]:
    """Identifiers that are the target of a relationship of ``relationship_type``.

    Read from the registry rather than from any code structure: which relationship confers
    ownership or evidence is a *registered* fact, so an authority here derives from the
    registry and not from this module's shape.
    """
    found: set[str] = set()
    for unit in registry.units():
        if unit.attribute("relationship_type") == relationship_type:
            target = str(unit.attribute("target", ""))
            if registry.find(target) is not None:
                found.add(target)
    return frozenset(found)


def related_units(registry: ExistenceRegistry) -> frozenset[str]:
    """Identifiers appearing at either end of any registered relationship."""
    endpoints: set[str] = set()
    for unit in registry.units():
        if not unit.attribute("relationship_type"):
            continue
        for role in ("source", "target"):
            endpoint = str(unit.attribute(role, ""))
            if registry.find(endpoint) is not None:
                endpoints.add(endpoint)
    return frozenset(endpoints)


def gaps(registry: ExistenceRegistry) -> dict[str, list[str]]:
    """``possession -> the units that lack it``, complete and unabridged.

    The single measurement both :func:`assess` and :func:`assess_by_form` read, so a
    per-form breakdown can never disagree with the whole-population report.
    """
    dictionary = dictionary_for_existence(registry)
    governed = governed_units(registry)
    owned = _targets_of(registry, OWNS)
    evidenced = _targets_of(registry, EVIDENCES)
    related = related_units(registry)
    journaled = {entry.subject for entry in registry.audit()}
    genesis = {e.subject for e in registry.audit() if e.action == ACTION_GENESIS}
    context_bound = registry.is_context_bound

    gaps: dict[str, list[str]] = {key: [] for key, _ in POSSESSIONS}
    for unit in registry.units():
        identifier = unit.universal_id
        label = f"{unit.form}:{unit.key}"
        if not is_well_formed(identifier):
            gaps["identity"].append(label)
        if identifier not in dictionary:
            gaps["dictionary"].append(label)
        if registry.find(identifier) is None:
            gaps["registry"].append(label)
        if not context_bound:
            gaps["context"].append(label)
        if identifier not in governed:
            gaps["governance"].append(label)
        if identifier not in owned and not unit.classification:
            gaps["ownership"].append(label)
        if identifier not in related:
            gaps["relationships"].append(label)
        if identifier not in journaled:
            gaps["lineage"].append(label)
        if identifier not in genesis:
            gaps["evolution"].append(label)
        if identifier not in evidenced:
            gaps["evidence"].append(label)

    return {key: sorted(value) for key, value in gaps.items()}


def assess(registry: ExistenceRegistry) -> dict[str, Any]:
    """Measure the ten possessions over every registered unit.

    Returns a complete, ordered report: which units lack which possession, and the counts
    behind each. Nothing is rounded up and nothing passes for want of a measurement.
    """
    found = gaps(registry)
    dictionary = dictionary_for_existence(registry)
    total = len(registry.units())
    possessions = [
        {
            "possession": key,
            "statement": statement,
            "held": total - len(found[key]),
            "total": total,
            "missing": len(found[key]),
            "complete": not found[key],
            "examples": found[key][:5],
        }
        for key, statement in POSSESSIONS
    ]
    return {
        "schema": "ucos-ceu-possessions",
        "version": "1.0.0",
        "units": total,
        "possessions": possessions,
        "incomplete": [p["possession"] for p in possessions if not p["complete"]],
        "complete": all(p["complete"] for p in possessions),
        "dictionary_verification": dictionary.verify(),
        "context_bound": registry.is_context_bound,
    }


def assess_by_form(registry: ExistenceRegistry) -> dict[str, dict[str, Any]]:
    """The same measurement, broken down per form.

    Item 5 of the wave — forms, relationship types, topologies, context axes, reality
    models, temporal models and measurement models each measured — needs no per-form code,
    because each of those *is* a form and the breakdown is a group-by. If it had needed
    seven branches, the substrate would have been the thing to fix.
    """
    found = {key: set(value) for key, value in gaps(registry).items()}
    per_form: dict[str, dict[str, Any]] = {}
    for form in sorted({u.form for u in registry.units()}):
        labels = [f"{u.form}:{u.key}" for u in registry.units(form=form)]
        per_form[form] = {
            "form": form,
            "units": len(labels),
            "by_possession": {
                key: {
                    "held": sum(1 for label in labels if label not in missing),
                    "total": len(labels),
                }
                for key, missing in found.items()
            },
            "incomplete": sorted(
                key for key, missing in found.items() if any(label in missing for label in labels)
            ),
        }
    return per_form


def completeness(registry: ExistenceRegistry) -> dict[str, Any]:
    """Constitutional completeness metrics — item 3 of the wave.

    Completeness is reported as a *measured state*, never assumed (CEU-018): the ratio is
    computed from the population actually present, and the denominator travels with it so
    a percentage can never be read without knowing what it is a percentage of.
    """
    report = assess(registry)
    total = report["units"] * len(POSSESSIONS)
    held = sum(p["held"] for p in report["possessions"])
    return {
        "schema": "ucos-ceu-completeness",
        "version": "1.0.0",
        "units": report["units"],
        "possessions": len(POSSESSIONS),
        "held": held,
        "required": total,
        "ratio": (held / total) if total else 0.0,
        "complete": report["complete"],
        "incomplete_possessions": report["incomplete"],
        "by_possession": {
            p["possession"]: {"held": p["held"], "total": p["total"]} for p in report["possessions"]
        },
    }


def require_complete(
    registry: ExistenceRegistry, *, possessions: tuple[str, ...] | None = None
) -> dict[str, Any]:
    """Fail closed on a missing constitutional possession — item 4 of the wave.

    ``possessions`` narrows the gate to a subset, which is how a caller enforces the
    possessions its stage actually requires rather than being blocked by one it does not.
    Narrowing is explicit and recorded in the refusal; there is no silent partial pass.

    Raises:
        CEUError: one of the required possessions is not held by every unit.
    """
    report = assess(registry)
    required = possessions if possessions is not None else tuple(k for k, _ in POSSESSIONS)
    unknown = sorted(set(required) - {k for k, _ in POSSESSIONS})
    if unknown:
        raise CEUError("unknown possession", unknown=unknown)
    missing = [
        p for p in report["possessions"] if p["possession"] in required and not p["complete"]
    ]
    if missing:
        raise CEUError(
            "a constitutional possession is missing; no concept may enter without one",
            required=list(required),
            missing={p["possession"]: p["examples"] for p in missing},
        )
    return report


#: The four levels certification executes at (Steering 014). Ordered narrowest first.
LEVELS: tuple[str, ...] = ("unit", "form", "classification", "registry")


def certify_levels(
    registry: ExistenceRegistry, *, possessions: tuple[str, ...] | None = None
) -> dict[str, Any]:
    """Certify at unit, form, classification and registry level (Steering 014).

    The verdict is the **conjunction** of all four, computed from the one gap measurement.
    A higher level cannot pass a lower one: ``registry`` is not an average over forms, it
    is "every unit holds every required possession", so there is no aggregation step in
    which a form failure could be diluted. Each level reports its own failures by name, so
    a reader sees *where* the incompleteness is and not merely that it exists.
    """
    required = possessions if possessions is not None else tuple(k for k, _ in POSSESSIONS)
    unknown = sorted(set(required) - {k for k, _ in POSSESSIONS})
    if unknown:
        raise CEUError("unknown possession", unknown=unknown)

    found = {key: set(value) for key, value in gaps(registry).items() if key in required}
    failing_labels = {label for missing in found.values() for label in missing}

    units = registry.units()
    by_label = {f"{u.form}:{u.key}": u for u in units}

    failing_forms = sorted({by_label[label].form for label in failing_labels})
    failing_classifications = sorted(
        {
            by_label[label].classification
            for label in failing_labels
            if by_label[label].classification
        }
    )

    levels = {
        "unit": {
            "level": "unit",
            "subjects": len(units),
            "failing": sorted(failing_labels)[:5],
            "failing_count": len(failing_labels),
            "passed": not failing_labels,
        },
        "form": {
            "level": "form",
            "subjects": len({u.form for u in units}),
            "failing": failing_forms[:5],
            "failing_count": len(failing_forms),
            "passed": not failing_forms,
        },
        "classification": {
            "level": "classification",
            "subjects": len({u.classification for u in units if u.classification}),
            "failing": failing_classifications[:5],
            "failing_count": len(failing_classifications),
            "passed": not failing_classifications,
        },
        "registry": {
            "level": "registry",
            "subjects": 1,
            "failing": sorted(found) if failing_labels else [],
            "failing_count": 1 if failing_labels else 0,
            "passed": not failing_labels,
        },
    }
    return {
        "schema": "ucos-ceu-level-certification",
        "version": "1.0.0",
        "required_possessions": list(required),
        "levels": [levels[name] for name in LEVELS],
        "failing_levels": [name for name in LEVELS if not levels[name]["passed"]],
        "certified": all(levels[name]["passed"] for name in LEVELS),
    }


def require_certified(
    registry: ExistenceRegistry, *, possessions: tuple[str, ...] | None = None
) -> dict[str, Any]:
    """Fail-closed four-level certification.

    Raises:
        CEUError: any level failed. The failing levels travel on the error, so no caller
            can observe an aggregate pass over a level failure.
    """
    report = certify_levels(registry, possessions=possessions)
    if not report["certified"]:
        raise CEUError(
            "constitutional certification failed; a lower level may not be masked",
            failing_levels=report["failing_levels"],
            levels={
                level["level"]: level["failing"]
                for level in report["levels"]
                if not level["passed"]
            },
        )
    return report


def digest(report: Mapping[str, Any]) -> str:
    return content_hash(dict(report))


__all__ = [
    "ATTR_GOVERNED_BY",
    "GOVERNS",
    "OWNS",
    "EVIDENCES",
    "ACTION_GENESIS",
    "POSSESSIONS",
    "dictionary_for_existence",
    "governed_units",
    "related_units",
    "assess",
    "assess_by_form",
    "completeness",
    "require_complete",
    "LEVELS",
    "certify_levels",
    "require_certified",
    "digest",
]
