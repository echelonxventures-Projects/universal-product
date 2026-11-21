"""UCXI-000001 Part 16 — validation and certification of the location architecture.

Part 15 resolves context from location. This part *measures* that resolution, and it does
so with the layer's own instruments: :class:`~engine.context.validation.ValidationRule`,
:class:`~engine.context.validation.Finding`,
:class:`~engine.context.validation.ContextValidationReport`,
:class:`~engine.context.certification.CertificationDimension` and
:class:`~engine.context.certification.ContextCertificate` are **imported**, not restated.

Why the rules live here and not in Part 11
------------------------------------------
Part 11 measures a ``ContextRegistry`` — a set of registered contexts. These rules measure
a :class:`~engine.context.location.FrameRegistry` — a set of reference frames and the
derivation graph over them. Two different subjects, so two rule sets; but **one** report
type, one severity vocabulary, one certificate shape and one verdict vocabulary, so a
consumer that already reads a context report reads this one with no new code. The derived
context registry produced by :func:`~engine.context.location.build_context_registry` is
also measured by the twelve Part 11 rules (LXV-11), which is what binds the two together:
a location resolution is not merely computed, it is *registered*, and the registration is
then judged by the rules that judge every other context.

The properties these rules exist to make false-able
---------------------------------------------------
* an axis could acquire a value from somewhere other than its frame chain (LXV-06);
* an axis could resolve without passing through location (LXV-05);
* an unresolved axis could be silently defaulted (LXV-07);
* two runs could disagree (LXV-09, LXC-06);
* the architecture could work for exactly one frame (LXC-04, LXC-05).

Each of those is a way the system could look correct and be wrong. Each has a rule.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from engine.context.certification import (
    VERDICT_CERTIFIED,
    VERDICT_NOT_CERTIFIED,
    CertificationDimension,
    ContextCertificate,
)
from engine.context.errors import ContextCertificationError, ContextError
from engine.context.location import (
    AXIS_DERIVATION,
    AXIS_GRAPH,
    FRAME_NAMESPACE,
    LOCATION,
    UNRESOLVED,
    FrameRegistry,
    axis_order,
    build_frame_registry,
    context_registries,
    derivation_path,
    identity_tuples,
    introduced_axes,
    location_determined_axes,
)
from engine.context.location import to_document as location_document
from engine.context.model import content_digest
from engine.context.validation import (
    DIMENSION_CLASSIFICATION,
    DIMENSION_HISTORY,
    DIMENSION_IDENTITY,
    DIMENSION_RELATION,
    DIMENSION_STRUCTURE,
    SEVERITY_ADVISORY,
    SEVERITY_VIOLATION,
    ContextValidationReport,
    Finding,
    ValidationRule,
)
from engine.context.validation import validate as validate_contexts
from engine.foundation.obs.logging import get_logger
from engine.registry.universal.identity import deterministic_id, is_well_formed

_logger = get_logger("context.location.assurance")

#: The dimension name for rules about the derivation graph itself. Declared alongside the
#: five Part 11 dimensions rather than inside them: a derivation edge is neither a
#: classification nor a relation between registered contexts.
DIMENSION_DERIVATION = "derivation"

#: The dimension name for rules about reference frames and their resolution.
DIMENSION_LOCATION = "location"

#: The minimum number of *distinct frame kinds* that must resolve completely for the
#: architecture to have demonstrated frame independence rather than one working example.
#: Three, because two can be coincidence and one is a hardcode with extra steps.
FRAME_KIND_PROOF_MINIMUM = 3


LOCATION_RULES: tuple[ValidationRule, ...] = (
    ValidationRule(
        rule_id="LXV-01",
        dimension=DIMENSION_IDENTITY,
        statement="Every reference frame's identifier is minted by the one identifier "
        "authority and reproduces from its own identity tuple.",
    ),
    ValidationRule(
        rule_id="LXV-02",
        dimension=DIMENSION_DERIVATION,
        statement="The axis derivation graph is acyclic and totally orderable, and every "
        "axis a frame declares is an axis the graph declares.",
    ),
    ValidationRule(
        rule_id="LXV-03",
        dimension=DIMENSION_RELATION,
        statement="Every frame chain terminates at a root; no frame is its own ancestor.",
    ),
    ValidationRule(
        rule_id="LXV-04",
        dimension=DIMENSION_STRUCTURE,
        statement="Every declared axis value is a non-empty authority reference, and no "
        "declared value is the unresolved marker.",
    ),
    ValidationRule(
        rule_id="LXV-05",
        dimension=DIMENSION_DERIVATION,
        statement="Every resolved location-determined axis carries a provenance chain that "
        "passes through the location axis.",
    ),
    ValidationRule(
        rule_id="LXV-06",
        dimension=DIMENSION_LOCATION,
        statement="Every resolved axis names, as its source, a frame in its own chain — no "
        "value enters resolution from outside the frame chain.",
    ),
    ValidationRule(
        rule_id="LXV-07",
        dimension=DIMENSION_STRUCTURE,
        statement="An axis no frame in the chain declares resolves to the stated-unknown "
        "marker: the architecture declares no default and no fallback.",
    ),
    ValidationRule(
        rule_id="LXV-08",
        dimension=DIMENSION_IDENTITY,
        statement="Every identifier the architecture assigns is well-formed under the one "
        "grammar, and no two distinct subjects claim one identifier.",
    ),
    ValidationRule(
        rule_id="LXV-09",
        dimension=DIMENSION_HISTORY,
        statement="Resolution is a deterministic fixed point: resolving a frame twice "
        "produces byte-identical documents.",
    ),
    ValidationRule(
        rule_id="LXV-10",
        dimension=DIMENSION_CLASSIFICATION,
        statement="At least three distinct frame kinds resolve every declared axis, so the "
        "architecture is proven frame-independent rather than proven once.",
        severity=SEVERITY_ADVISORY,
    ),
    ValidationRule(
        rule_id="LXV-11",
        dimension=DIMENSION_CLASSIFICATION,
        statement="The contexts derived from resolution satisfy every rule the context "
        "layer applies to every other registered context.",
    ),
)


# --------------------------------------------------------------------------- #
# The checks                                                                   #
# --------------------------------------------------------------------------- #


def _check_frame_identity(frames: FrameRegistry) -> list[str]:
    out: list[str] = []
    for frame in frames.frames():
        minted = deterministic_id("LOCATION", FRAME_NAMESPACE, frame.key)
        if frame.universal_id != minted:
            out.append(f"{frame.key}: identifier does not reproduce (expected {minted})")
        elif not is_well_formed(frame.universal_id):
            out.append(f"{frame.key}: identifier is not well-formed")
    return out


def _check_derivation_graph(frames: FrameRegistry) -> list[str]:
    out: list[str] = []
    try:
        order = axis_order()
    except ContextError as exc:
        return [f"the axis derivation graph has no total order: {exc}"]
    if len(order) != len(AXIS_DERIVATION):
        out.append(f"{len(order)} axes ordered, {len(AXIS_DERIVATION)} declared")
    for axis, requires in AXIS_DERIVATION:
        for required in requires:
            if required not in AXIS_GRAPH:
                out.append(f"{axis}: derives from {required!r}, which is not a declared axis")
    for frame in frames.frames():
        for axis in frame.axes:
            if axis not in AXIS_GRAPH:
                out.append(f"{frame.key}: declares {axis!r}, which is not a declared axis")
    return out


def _check_frame_chains(frames: FrameRegistry) -> list[str]:
    out: list[str] = []
    for frame in frames.frames():
        try:
            chain = frames.chain(frame.key)
        except ContextError as exc:
            out.append(f"{frame.key}: {exc}")
            continue
        if chain[0] != frame.key:
            out.append(f"{frame.key}: chain does not begin at the frame itself")
        if frames.frame(chain[-1]).parent is not None:
            out.append(f"{frame.key}: chain does not terminate at a root")
    return out


def _check_declared_values(frames: FrameRegistry) -> list[str]:
    out: list[str] = []
    for frame in frames.frames():
        for axis, value in frame.axes.items():
            if not value.strip():
                out.append(f"{frame.key}: axis {axis!r} declares an empty value")
            elif value == UNRESOLVED:
                out.append(f"{frame.key}: axis {axis!r} declares the unresolved marker as a value")
    return out


def _check_location_derivation(frames: FrameRegistry) -> list[str]:
    determined = set(location_determined_axes())
    out: list[str] = []
    for frame in frames.frames():
        resolution = frames.resolve(frame.key)
        for resolved in resolution.axes:
            if resolved.axis not in determined or not resolved.resolved:
                continue
            if LOCATION not in resolved.derived_from:
                out.append(
                    f"{frame.key}/{resolved.axis}: resolved without a location-derived chain"
                )
            if set(resolved.derived_from) != set(derivation_path(resolved.axis)):
                out.append(f"{frame.key}/{resolved.axis}: provenance chain is not the declared one")
    return out


def _check_source_in_chain(frames: FrameRegistry) -> list[str]:
    out: list[str] = []
    for frame in frames.frames():
        resolution = frames.resolve(frame.key)
        chain = set(resolution.chain)
        for resolved in resolution.axes:
            if not resolved.resolved:
                continue
            if resolved.source_frame not in chain:
                out.append(
                    f"{frame.key}/{resolved.axis}: sourced from {resolved.source_frame!r}, "
                    "which is not in the frame chain"
                )
            elif frames.frame(resolved.source_frame).axes.get(resolved.axis) != resolved.value:
                out.append(f"{frame.key}/{resolved.axis}: value does not match its declared source")
    return out


def _check_no_defaults(frames: FrameRegistry) -> list[str]:
    out: list[str] = []
    for frame in frames.frames():
        resolution = frames.resolve(frame.key)
        declared = {axis for step in resolution.chain for axis in frames.frame(step).axes}
        for resolved in resolution.axes:
            if resolved.axis in declared and not resolved.resolved:
                out.append(f"{frame.key}/{resolved.axis}: declared in the chain but unresolved")
            if resolved.axis not in declared and resolved.resolved:
                out.append(
                    f"{frame.key}/{resolved.axis}: resolved to {resolved.value!r} without any "
                    "frame in the chain declaring it"
                )
            if not resolved.resolved and resolved.value != UNRESOLVED:
                out.append(f"{frame.key}/{resolved.axis}: unresolved axis carries a value")
            if not resolved.resolved and resolved.source_frame:
                out.append(f"{frame.key}/{resolved.axis}: unresolved axis names a source frame")
    return out


def _check_assigned_identifiers(frames: FrameRegistry) -> list[str]:
    out: list[str] = []
    claimed: dict[str, tuple[str, str, str]] = {}
    for kind, namespace, natural_key in identity_tuples(frames):
        identifier = deterministic_id(kind, namespace, natural_key)
        if not is_well_formed(identifier):
            out.append(f"{natural_key}: assigned identifier is not well-formed")
            continue
        owner = claimed.get(identifier)
        if owner is not None and owner != (kind, namespace, natural_key):
            out.append(f"{identifier}: claimed by {owner[2]!r} and by {natural_key!r}")
        claimed[identifier] = (kind, namespace, natural_key)
    return out


def _check_fixed_point(frames: FrameRegistry) -> list[str]:
    out: list[str] = []
    for frame in frames.frames():
        first = frames.resolve(frame.key).digest()
        second = frames.resolve(frame.key).digest()
        if first != second:
            out.append(f"{frame.key}: resolution is not a fixed point")
    if frames.digest() != frames.digest():  # pragma: no cover - purity assertion
        out.append("the frame registry digest is not stable")
    return out


def _check_frame_kind_proof(frames: FrameRegistry) -> list[str]:
    kinds = complete_frame_kinds(frames)
    if len(kinds) >= FRAME_KIND_PROOF_MINIMUM:
        return []
    return [
        f"only {len(kinds)} frame kind(s) resolve completely "
        f"({', '.join(kinds) or 'none'}); {FRAME_KIND_PROOF_MINIMUM} are required"
    ]


def _check_derived_contexts(frames: FrameRegistry) -> list[str]:
    """Judge each frame's *registered* projection by the rules that judge every context.

    Per frame, because a context registry represents one reference frame — see
    :func:`~engine.context.location.build_context_registry`. Every frame is checked,
    including the incomplete ones: an incomplete frame registers fewer contexts, and the
    ones it does register must still be lawful.
    """
    out: list[str] = []
    for key, registry in context_registries(frames).items():
        report = validate_contexts(registry)
        out.extend(f"{key}: {finding.rule_id}: {finding.detail}" for finding in report.violations)
    return out


#: rule id → the check that measures it. The same shape Part 11 uses, so a caller can
#: substitute a rule set and its checks in exactly the way it already knows how to.
LOCATION_RULE_CHECKS: dict[str, Any] = {
    "LXV-01": _check_frame_identity,
    "LXV-02": _check_derivation_graph,
    "LXV-03": _check_frame_chains,
    "LXV-04": _check_declared_values,
    "LXV-05": _check_location_derivation,
    "LXV-06": _check_source_in_chain,
    "LXV-07": _check_no_defaults,
    "LXV-08": _check_assigned_identifiers,
    "LXV-09": _check_fixed_point,
    "LXV-10": _check_frame_kind_proof,
    "LXV-11": _check_derived_contexts,
}


def complete_frames(frames: FrameRegistry) -> tuple[str, ...]:
    """The frames that resolve every declared axis, ordered."""
    return tuple(frame.key for frame in frames.frames() if frames.resolve(frame.key).complete)


def complete_frame_kinds(frames: FrameRegistry) -> tuple[str, ...]:
    """The distinct frame kinds among the completely resolving frames, ordered."""
    return tuple(sorted({frames.frame(key).frame_kind for key in complete_frames(frames)}))


def validate_location(frames: FrameRegistry | None = None) -> ContextValidationReport:
    """Run every location rule over a frame registry and return the complete report.

    Every rule runs; the report is ordered and total. Advisory rules are counted and do
    not by themselves invalidate the architecture — certification applies the stricter
    bar, exactly as it does for Part 11.
    """
    catalog = frames if frames is not None else build_frame_registry()
    unenforced = [r.rule_id for r in LOCATION_RULES if r.rule_id not in LOCATION_RULE_CHECKS]
    if unenforced:  # pragma: no cover - guards a rule added without a check
        raise ContextCertificationError(
            "every location rule must carry an executable check", rules=unenforced
        )
    findings: list[Finding] = []
    for rule in LOCATION_RULES:
        for detail in LOCATION_RULE_CHECKS[rule.rule_id](catalog):
            findings.append(
                Finding(
                    rule_id=rule.rule_id,
                    dimension=rule.dimension,
                    severity=rule.severity,
                    detail=detail,
                )
            )
    coverage = catalog.coverage()
    report = ContextValidationReport(
        rules=LOCATION_RULES,
        findings=tuple(findings),
        metrics={
            "frames": len(catalog),
            "frame_kinds": len(catalog.frame_kinds()),
            "axes": coverage["axis_count"],
            "location_determined_axes": len(location_determined_axes()),
            "complete_frames": coverage["complete_frames"],
            "incomplete_frames": coverage["incomplete_frames"],
            "registry_digest": catalog.digest(),
        },
    )
    _logger.info(
        "context.location.validated",
        violations=len(report.violations),
        advisories=len(report.advisories),
    )
    return report


# --------------------------------------------------------------------------- #
# Certification                                                                #
# --------------------------------------------------------------------------- #

#: The declared dimensions (statement only; the outcome is always measured).
LOCATION_DIMENSIONS: tuple[tuple[str, str], ...] = (
    ("LXC-01", "Location is a declared axis and the root every derived axis hangs from."),
    ("LXC-02", "No location validation rule of violation severity produced a finding."),
    ("LXC-03", "Every location-determined axis resolves for every completely declared frame."),
    (
        "LXC-04",
        f"At least {FRAME_KIND_PROOF_MINIMUM} distinct frame kinds resolve every declared axis.",
    ),
    ("LXC-05", "Changing the reference frame re-resolves the dependent axes."),
    ("LXC-06", "The whole architecture is a deterministic fixed point on recomputation."),
    ("LXC-07", "Every resolved axis is registered as a context by the one registration authority."),
)


def rebase_differences(frames: FrameRegistry, frame_keys: Sequence[str]) -> tuple[str, ...]:
    """The axes whose resolved value differs across ``frame_keys``."""
    if len(frame_keys) < 2:
        return ()
    report = frames.rebase("ucos-location-certification", frame_keys=list(frame_keys))
    return tuple(report["axes_differing"])


def certify_location(frames: FrameRegistry | None = None) -> ContextCertificate:
    """Compute the certification of the location architecture.

    Reachable in both directions by construction: a frame registry whose frames declare
    nothing fails LXC-03, LXC-04 and LXC-05, and the declared catalogue passes them. A
    gate with only one reachable outcome is not evidence.
    """
    catalog = frames if frames is not None else build_frame_registry()
    report = validate_location(catalog)
    complete = complete_frames(catalog)
    kinds = complete_frame_kinds(catalog)
    determined = location_determined_axes()

    unresolved_in_complete: list[str] = []
    for key in complete:
        resolution = catalog.resolve(key)
        unresolved_in_complete.extend(
            f"{key}/{axis}" for axis in determined if not resolution.get(axis).resolved
        )

    differing = rebase_differences(catalog, complete[:2])

    registries = context_registries(catalog)
    registered_total = sum(len(registry) for registry in registries.values())
    unregistered: list[str] = []
    admissible = set(introduced_axes())
    for frame in catalog.frames():
        registered_kinds = set(registries[frame.key].kinds())
        for resolved in catalog.resolve(frame.key).axes:
            if resolved.resolved and resolved.axis in admissible:
                if resolved.axis not in registered_kinds:
                    unregistered.append(f"{frame.key}/{resolved.axis}")

    first = _architecture_digest(catalog)
    second = _architecture_digest(catalog)

    outcomes: dict[str, tuple[bool, str, str]] = {
        "LXC-01": (
            LOCATION in AXIS_GRAPH and bool(determined),
            "" if LOCATION in AXIS_GRAPH else "location is not a declared axis",
            f"{len(determined)} axes derive from {LOCATION}",
        ),
        "LXC-02": (
            report.is_valid,
            "; ".join(finding.rule_id for finding in report.violations),
            f"{len(report.violations)} violation(s)",
        ),
        "LXC-03": (
            bool(complete) and not unresolved_in_complete,
            "; ".join(unresolved_in_complete[:3]),
            f"{len(complete)} complete frame(s)",
        ),
        "LXC-04": (
            len(kinds) >= FRAME_KIND_PROOF_MINIMUM,
            "" if len(kinds) >= FRAME_KIND_PROOF_MINIMUM else f"kinds: {', '.join(kinds)}",
            f"{len(kinds)} frame kind(s)",
        ),
        "LXC-05": (
            bool(differing),
            "" if differing else "no axis differs between the compared frames",
            f"{len(differing)} axis/axes re-resolve",
        ),
        "LXC-06": (
            first == second,
            "" if first == second else "the architecture digest is not stable",
            "double-computed",
        ),
        "LXC-07": (
            not unregistered,
            "; ".join(unregistered[:3]),
            f"{registered_total} registered context(s) across {len(registries)} frame(s)",
        ),
    }

    dimensions = tuple(
        CertificationDimension(
            dimension_id=dimension_id,
            statement=statement,
            passed=outcomes[dimension_id][0],
            detail=outcomes[dimension_id][1],
            measured=outcomes[dimension_id][2],
        )
        for dimension_id, statement in LOCATION_DIMENSIONS
    )
    missing = [d for d, _ in LOCATION_DIMENSIONS if d not in outcomes]
    if missing:  # pragma: no cover - guards a dimension added without a measurement
        raise ContextCertificationError(
            "a location certification dimension has no measurement", dimensions=missing
        )

    verdict = VERDICT_CERTIFIED if all(d.passed for d in dimensions) else VERDICT_NOT_CERTIFIED
    seals = {
        "frames": catalog.digest(),
        "validation": report.content_hash,
        "registries": content_digest({key: r.seal() for key, r in sorted(registries.items())}),
        "architecture": first,
    }
    certificate = ContextCertificate(
        certificate_id="UCOS-LOCCERT-" + content_digest(seals)[:12],
        verdict=verdict,
        dimensions=dimensions,
        metrics={
            "frames": len(catalog),
            "frame_kinds": len(catalog.frame_kinds()),
            "complete_frames": len(complete),
            "complete_frame_kinds": len(kinds),
            "axes": len(AXIS_DERIVATION),
            "location_determined_axes": len(determined),
            "registered_contexts": registered_total,
            "rebase_differing_axes": len(differing),
            "rules": len(report.rules),
            "violations": len(report.violations),
            "advisories": len(report.advisories),
        },
        seals=seals,
    )
    _logger.info(
        "context.location.certified",
        verdict=verdict,
        certificate_id=certificate.certificate_id,
        failed=len(certificate.failed_dimensions),
    )
    return certificate


def require_certified_location(frames: FrameRegistry | None = None) -> ContextCertificate:
    """Fail-closed form of :func:`certify_location`."""
    certificate = certify_location(frames)
    if not certificate.certified:
        raise ContextCertificationError(
            "the location architecture is not certified",
            verdict=certificate.verdict,
            failed=list(certificate.failed_dimensions),
        )
    return certificate


# --------------------------------------------------------------------------- #
# Replay                                                                       #
# --------------------------------------------------------------------------- #


def _architecture_digest(frames: FrameRegistry) -> str:
    """The digest of everything the architecture derives from a frame registry."""
    return content_digest(location_document(frames))


def _registries_digest(frames: FrameRegistry) -> str:
    """One digest over every frame's registered context projection."""
    return content_digest(
        {key: registry.seal() for key, registry in sorted(context_registries(frames).items())}
    )


def replay_location(frames: FrameRegistry | None = None) -> dict[str, Any]:
    """Rebuild the architecture from its own declaration twice and compare.

    This is the hermetic double-build applied to location: the catalogue is re-read, the
    registry re-built, every frame re-resolved, the contexts re-registered and the
    certificate recomputed. Every digest must agree. A disagreement means something in
    the path read a clock, an environment variable, a set iteration order or a filesystem
    ordering — all of which are exactly what this measurement exists to catch.
    """
    supplied = frames is not None
    first_frames = frames if frames is not None else build_frame_registry()
    second_frames = frames if frames is not None else build_frame_registry()

    first = {
        "frames": first_frames.digest(),
        "architecture": _architecture_digest(first_frames),
        "contexts": _registries_digest(first_frames),
        "validation": validate_location(first_frames).content_hash,
        "certification": certify_location(first_frames).content_hash,
    }
    second = {
        "frames": second_frames.digest(),
        "architecture": _architecture_digest(second_frames),
        "contexts": _registries_digest(second_frames),
        "validation": validate_location(second_frames).content_hash,
        "certification": certify_location(second_frames).content_hash,
    }
    drifted = sorted(key for key in first if first[key] != second[key])
    return {
        "schema": "ucos-location-replay",
        "version": "1.0.0",
        "rebuilt_from_declaration": not supplied,
        "first": first,
        "second": second,
        "drifted": drifted,
        "fixed_point": not drifted,
    }


def to_document(frames: FrameRegistry | None = None) -> dict[str, Any]:
    """The whole assurance surface as one deterministic, diffable document."""
    catalog = frames if frames is not None else build_frame_registry()
    report = validate_location(catalog)
    certificate = certify_location(catalog)
    replay = replay_location(catalog)
    return {
        "schema": "ucos-location-assurance",
        "version": "1.0.0",
        "rules": [rule.to_dict() for rule in LOCATION_RULES],
        "validation": report.to_dict(),
        "certification": certificate.to_dict(),
        "replay": replay,
        "complete_frames": list(complete_frames(catalog)),
        "complete_frame_kinds": list(complete_frame_kinds(catalog)),
        "operational": report.is_valid and certificate.certified and replay["fixed_point"],
    }


__all__ = [
    "DIMENSION_DERIVATION",
    "DIMENSION_LOCATION",
    "FRAME_KIND_PROOF_MINIMUM",
    "LOCATION_RULES",
    "LOCATION_RULE_CHECKS",
    "LOCATION_DIMENSIONS",
    "SEVERITY_ADVISORY",
    "SEVERITY_VIOLATION",
    "complete_frames",
    "complete_frame_kinds",
    "rebase_differences",
    "validate_location",
    "certify_location",
    "require_certified_location",
    "replay_location",
    "to_document",
]
