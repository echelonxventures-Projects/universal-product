"""UCOS-NUC-001 Part 10 — binding the structural population to location-derived context.

Parts 06–09 gave the structural population a lifecycle, a lineage ledger, an evolution
ledger and a certification. Every one of them ran *nowhere*: a lifecycle execution, a
lineage entry and an evolution generation named a subject but no reality, so two runs in
two different civilisations were indistinguishable records.

This part supplies the missing coordinate. It creates no new lifecycle, no new ledger and
no new identifier scheme — it threads the reference frame resolved by
:mod:`engine.context.location` through the four that already exist:

    lifecycle  :func:`context_stage_function`  every stage discharged in a named frame
    lineage    :func:`bind_lineage`            every subject bound to the frame it runs in
    evolution  :func:`evolve_in_context`       every generation carries its reality
    identity   :func:`dictionary_with_context` frames and axes enter the one dictionary

Fail-closed, in one place
-------------------------
An incomplete frame — one whose chain leaves an axis unresolved — cannot be bound. Every
entry point here refuses it (:class:`~engine.nucleus.errors.LifecycleError` /
:class:`~engine.nucleus.errors.EvolutionError`), rather than binding a partial context and
letting a downstream consumer discover the hole. That is the same refusal
``ucos-nucleus context --frame <incomplete>`` already makes at the CLI, applied at the
point where the context would otherwise become durable.

Nothing here knows what any axis *means*. A calendar, a currency and a tax model are
opaque authority references carried through as data, which is what keeps the binding
universal and the axis set open.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from engine.context.errors import ContextValidationError
from engine.context.location import (
    FRAME_NAMESPACE,
    LOCATION,
    REALITY_CONTEXT_AXES,
    FrameRegistry,
    LocationResolution,
    build_frame_registry,
    context_registries,
    identity_tuples,
    introduced_axes,
    location_determined_axes,
    require_reality_context,
)
from engine.context.location_assurance import (
    certify_location,
    complete_frames,
    replay_location,
    validate_location,
)
from engine.nucleus.errors import ContextBindingViolation, EvolutionError, LifecycleError
from engine.nucleus.evolution import Evolution, EvolutionLedger
from engine.nucleus.lifecycle import LifecycleExecution, Stage, StageStatus, execute
from engine.nucleus.lifecycle import replay as lifecycle_replay
from engine.nucleus.lineage import CONTEXT_BOUND, LineageLedger, ledger_for
from engine.registry.universal.dictionary import IdentifierDictionary, dictionary_for
from engine.registry.universal.identity import RegistryKind
from engine.uckp.canonical import content_hash


def require_complete(
    resolution: LocationResolution, *, error: type[Exception]
) -> LocationResolution:
    """Return ``resolution`` if every declared axis resolved; otherwise fail closed.

    Raises:
        error: the frame left one or more axes unresolved. The unresolved axes are
            carried on the exception, so the refusal names the gap instead of merely
            reporting one.
    """
    if not resolution.complete:
        raise error(
            "an incomplete context cannot be bound (unresolved context fails closed)",
            frame=resolution.frame,
            unresolved=list(resolution.unresolved_axes),
        )
    return resolution


def context_fingerprint(resolution: LocationResolution) -> dict[str, Any]:
    """The compact, deterministic record of one resolved reality.

    Carried into lifecycle details, lineage details and evolution state. It holds the
    frame, its identifier, the chain that produced it and the digest of the whole
    resolution — enough for a later reader to re-derive the context and compare, and
    small enough to sit inside every journal entry without dominating it.

    The completeness guard lives **here**, at the point a resolution becomes a portable
    coordinate, rather than at each of the seven call sites that carry one. A fingerprint
    is the thing that gets written into registries, ledgers and certificates; if an
    incomplete one could be minted, every one of those would have to re-check, and the
    first caller to forget would persist a reality with a hole in it.

    Two guards apply here, in order, and they are different questions:

    * :func:`~engine.context.location.require_reality_context` — did existence, reality,
      observer, spatial and temporal resolve? Without those five, nothing carried in this
      fingerprint can be *interpreted*, so no measurement, validation, governance,
      certification or execution downstream is meaningful;
    * :func:`require_complete` — did every declared axis resolve? Stricter, and required
      because a fingerprint is a *portable* coordinate: it is written into registries,
      ledgers and certificates, and a partial one would make each of those a record of a
      reality with a hole in it.

    The reality-context refusal is re-raised as a :class:`ContextBindingViolation` — this
    layer's own error type — rather than allowed to escape as a context-layer exception.
    A caller of the nucleus layer catches ``NucleusError``; letting a foreign exception
    through would turn a fail-closed refusal into an uncaught traceback at every CLI and
    gate above. The unresolved axes travel on the error, so nothing is lost in translation.

    Raises:
        ContextBindingViolation: the reality context did not resolve.
        LifecycleError: the resolution left some other declared axis unresolved.
    """
    try:
        require_reality_context(resolution)
    except ContextValidationError as exc:
        raise ContextBindingViolation(
            "no value may be interpreted before the reality context resolves",
            frame=resolution.frame,
            unresolved=list(resolution.reality_context_gaps),
            required=list(REALITY_CONTEXT_AXES),
        ) from exc
    resolved = require_complete(resolution, error=LifecycleError)
    return {
        "frame": resolved.frame,
        "frame_id": resolved.frame_id,
        "chain": list(resolved.chain),
        "resolution_digest": resolved.digest(),
        "axes_resolved": len(resolved.resolved_axes),
        "location_derived_axes": resolved.location_derived_count(),
        "location": resolved.value_of(LOCATION),
        "reality_context": resolved.reality_context,
    }


# --------------------------------------------------------------------------- #
# Lifecycle → context                                                          #
# --------------------------------------------------------------------------- #


def context_stage_function(resolution: LocationResolution) -> Any:
    """Build a lifecycle stage function that discharges every stage inside one frame.

    The returned function has the :data:`~engine.nucleus.lifecycle.StageFunction` shape,
    so it drops into :func:`engine.nucleus.lifecycle.execute` and
    :func:`engine.nucleus.lifecycle.replay` unchanged. Every stage outcome carries the
    context fingerprint, which means the execution digest is a function of the reality the
    run happened in: the same subject run in two frames produces two different — and both
    honest — records.

    Raises:
        LifecycleError: the resolution is incomplete.
    """
    resolved = require_complete(resolution, error=LifecycleError)
    fingerprint = context_fingerprint(resolved)

    def in_context(subject: str, stage: Stage) -> tuple[StageStatus, str, Mapping[str, Any]]:
        return (
            StageStatus.SATISFIED,
            f"{resolved.frame_id}:{stage.stage_id}",
            {"subject": subject, "ordinal": stage.ordinal, "context": fingerprint},
        )

    return in_context


def execute_in_context(subject: str, resolution: LocationResolution) -> LifecycleExecution:
    """Run the whole lifecycle over ``subject`` inside one resolved reference frame.

    Raises:
        LifecycleError: the resolution is incomplete.
    """
    resolved = require_complete(resolution, error=LifecycleError)
    return execute(
        subject,
        stage_function=context_stage_function(resolved),
        context=context_fingerprint(resolved),
    )


def replay_in_context(subject: str, resolution: LocationResolution) -> dict[str, Any]:
    """Prove the lifecycle over ``subject`` is a fixed point *within* one frame.

    Raises:
        LifecycleError: the resolution is incomplete.
    """
    resolved = require_complete(resolution, error=LifecycleError)
    return lifecycle_replay(
        subject,
        stage_function=context_stage_function(resolved),
        context=context_fingerprint(resolved),
    )


# --------------------------------------------------------------------------- #
# Lineage → context                                                            #
# --------------------------------------------------------------------------- #


def bind_lineage(
    ledger: LineageLedger,
    resolution: LocationResolution,
    *,
    subjects: Iterable[tuple[str, str]],
) -> tuple[str, ...]:
    """Record that each ``(subject_id, subject_key)`` runs in the resolved frame.

    Appends one :data:`CONTEXT_BOUND` entry per subject to the *existing* ledger — the
    one hash-chained lineage authority — so a context binding is as tamper-evident as a
    registration or an ownership move, and is discoverable by the same query.

    Binding is **idempotent**: a subject already carrying an identical binding is skipped,
    because binding the same subject to the same reality twice is one fact and not two,
    and an append-only ledger that grew on every re-measurement would make the lineage
    head — and therefore every certificate citing it — depend on how many times something
    was measured.

    Returns:
        The entry hashes appended by *this* call, in order. Empty when everything named
        was already bound.

    Raises:
        LifecycleError: the resolution is incomplete.
    """
    resolved = require_complete(resolution, error=LifecycleError)
    fingerprint = context_fingerprint(resolved)
    already = {
        entry.subject_id
        for entry in ledger.entries(event=CONTEXT_BOUND)
        if dict(entry.detail) == fingerprint
    }
    heads: list[str] = []
    for subject_id, subject_key in subjects:
        if subject_id in already:
            continue
        entry = ledger.record(
            CONTEXT_BOUND,
            subject_id=subject_id,
            subject_key=subject_key,
            detail=dict(fingerprint),
        )
        already.add(subject_id)
        heads.append(entry.entry_hash)
    return tuple(heads)


def bind_registry(
    registry: Any,
    ledger: LineageLedger,
    resolution: LocationResolution,
) -> tuple[str, ...]:
    """Bind a nucleus registry, and every subject in it, to one reference frame.

    Two effects, deliberately together: the registry records the coordinate (so its
    document, its digest and every projection derived from it carry the reality), and the
    ledger records one binding event per subject (so the binding has a chain of custody).
    Doing only the first would leave an unauditable claim; only the second would leave the
    registry's own document silent about where it applies.
    """
    resolved = require_complete(resolution, error=LifecycleError)
    registry.bind_context(context_fingerprint(resolved))
    return bind_lineage(
        ledger,
        resolved,
        subjects=[(s.universal_id, s.key) for s in registry.subjects()],
    )


def bind(registry: Any, resolution: LocationResolution) -> LineageLedger:
    """Bind a registry to a frame and return its context-bearing lineage from scratch.

    The one-call path for "make this population context-aware": the registry takes the
    coordinate first, so :func:`engine.nucleus.lineage.ledger_for` derives a ledger that
    already carries a binding for every subject. No entry is appended twice, because the
    binding is part of the derivation rather than a second pass over it.
    """
    resolved = require_complete(resolution, error=LifecycleError)
    registry.bind_context(context_fingerprint(resolved))
    return ledger_for(registry)


def unbound_subjects(registry: Any, ledger: LineageLedger) -> tuple[str, ...]:
    """Registered subject ids with no context binding — the gap this part exists to close."""
    bound = {entry.subject_id for entry in ledger.entries(event=CONTEXT_BOUND)}
    return tuple(sorted(s.universal_id for s in registry.subjects() if s.universal_id not in bound))


# --------------------------------------------------------------------------- #
# Evolution → context                                                          #
# --------------------------------------------------------------------------- #


def evolve_in_context(
    ledger: EvolutionLedger,
    resolution: LocationResolution,
    *,
    subject_id: str,
    subject_key: str,
    change: str,
    authority: str,
    state: Mapping[str, Any] | None = None,
) -> Evolution:
    """Record one governed evolution *in a named reality*.

    The context fingerprint enters the evolution's ``state``, so it is part of the
    evolution digest and part of the lineage entry the ledger writes. An evolution can
    then be replayed only against the reality it was performed in, which is what stops a
    generation recorded under one frame from being silently reused under another.

    Raises:
        EvolutionError: the resolution is incomplete, or the evolution is refused by the
            ledger's validator.
    """
    resolved = require_complete(resolution, error=EvolutionError)
    payload = dict(state or {})
    payload["context"] = context_fingerprint(resolved)
    return ledger.evolve(
        subject_id=subject_id,
        subject_key=subject_key,
        change=change,
        authority=authority,
        state=payload,
    )


def evolutions_without_context(ledger: EvolutionLedger) -> tuple[str, ...]:
    """Evolution ids whose state names no reference frame."""
    return tuple(
        sorted(
            evolution.evolution_id
            for evolution in ledger.evolutions()
            if not isinstance(evolution.state.get("context"), Mapping)
            or not evolution.state["context"].get("frame")
        )
    )


# --------------------------------------------------------------------------- #
# Identifier → context                                                         #
# --------------------------------------------------------------------------- #


def dictionary_with_context(
    registry: Any,
    frames: FrameRegistry | None = None,
    *,
    dictionary: IdentifierDictionary | None = None,
) -> IdentifierDictionary:
    """Extend the structural identifier dictionary with every frame and resolved axis.

    Frames enter as :attr:`~engine.registry.universal.identity.RegistryKind.LOCATION`,
    resolved axes as ``CONTEXT`` — the same tuples
    :func:`engine.context.location.identity_tuples` declares and the same ones the context
    registry mints from, so the dictionary, the context registry and the frame registry
    agree on identity by construction. Nothing is minted here that is not already minted
    there; the dictionary *enumerates*, it does not assign.
    """
    catalog = frames if frames is not None else build_frame_registry()
    target = dictionary if dictionary is not None else dictionary_for(registry)
    for kind, namespace, natural_key in identity_tuples(catalog):
        if kind == RegistryKind.LOCATION.value:
            owner = ""
            attributes: dict[str, Any] = {"frame_kind": catalog.frame(natural_key).frame_kind}
        else:
            frame_key, _, axis = natural_key.partition(".")
            owner = catalog.frame(frame_key).universal_id
            attributes = {"axis": axis, "frame": frame_key}
        target.assign(kind, namespace, natural_key, owner=owner, attributes=attributes)
    return target


# --------------------------------------------------------------------------- #
# Measurement (consumed by Part 09)                                            #
# --------------------------------------------------------------------------- #


def context_measurements(
    frames: FrameRegistry | None = None,
    *,
    frame_key: str | None = None,
    registry: Any = None,
    lineage: LineageLedger | None = None,
    evolution: EvolutionLedger | None = None,
) -> dict[str, Any]:
    """Measure the context axis of the constitutional population.

    Returns plain data rather than :class:`~engine.nucleus.certification.Check` objects so
    that Part 09 can consume it without this module importing Part 09 — one direction of
    dependency, no cycle, and the measurement stays usable on its own.
    """
    catalog = frames if frames is not None else build_frame_registry()
    validation = validate_location(catalog)
    certificate = certify_location(catalog)
    replay = replay_location(catalog)
    complete = complete_frames(catalog)
    determined = location_determined_axes()

    unresolved: list[str] = []
    for key in complete:
        resolution = catalog.resolve(key)
        unresolved.extend(f"{key}/{a}" for a in determined if not resolution.get(a).resolved)

    registries = context_registries(catalog)
    measurements: dict[str, Any] = {
        "frames": len(catalog),
        "frame_kinds": len(catalog.frame_kinds()),
        "complete_frames": len(complete),
        "axes": len(catalog.coverage()["axes"]),
        "location_determined_axes": len(determined),
        "registered_contexts": sum(len(r) for r in registries.values()),
        "validation_violations": len(validation.violations),
        "validation_failures": list(validation.rules_failed()),
        "certified": certificate.certified,
        "certification_failures": list(certificate.failed_dimensions),
        "unresolved_in_complete_frames": unresolved,
        "replay_fixed_point": bool(replay["fixed_point"]),
        "replay_drift": list(replay["drifted"]),
        "validation_digest": validation.content_hash,
        "certificate_digest": certificate.content_hash,
        "frame": "",
        "resolution_digest": "",
    }
    if frame_key is not None:
        bound = require_complete(catalog.resolve(frame_key), error=LifecycleError)
        measurements["frame"] = bound.frame
        measurements["resolution_digest"] = bound.digest()
        measurements["fingerprint"] = context_fingerprint(bound)
    #: The one digest a certificate cites: the architecture *and* the reality it was
    #: certified in. Two frames therefore yield two digests, which is what makes a
    #: certificate a claim about a named reality rather than about the code alone.
    measurements["context_digest"] = content_hash(
        {
            "architecture": certificate.content_hash,
            "validation": validation.content_hash,
            "frame": measurements["frame"],
            "resolution": measurements["resolution_digest"],
        }
    )
    if registry is not None and lineage is not None:
        measurements["subjects_without_context"] = list(unbound_subjects(registry, lineage))
    if evolution is not None:
        measurements["evolutions_without_context"] = list(evolutions_without_context(evolution))
    measurements["gates"] = context_gates(
        catalog, frame_key=frame_key, registry=registry, lineage=lineage
    )
    return measurements


#: The four constitutional context gates, as ``gate id → what it asserts``. Named rather
#: than numbered alone, because a certificate that says ``CV-CONTEXT-03 FAIL`` and nothing
#: else is a refusal nobody can act on.
CONTEXT_GATES: tuple[tuple[str, str, str], ...] = (
    (
        "CV-CONTEXT-01",
        "Context Bound",
        "Every registered subject is bound to a resolved reference frame.",
    ),
    (
        "CV-CONTEXT-02",
        "Context Resolved",
        "The bound frame resolves every declared axis; no axis is left unresolved.",
    ),
    (
        "CV-CONTEXT-03",
        "Context Verified",
        "Every recorded context fingerprint reproduces from the frame registry.",
    ),
    (
        "CV-CONTEXT-04",
        "Context Registered",
        "Every resolved axis of the bound frame is a registered context.",
    ),
)


def context_gates(
    frames: FrameRegistry | None = None,
    *,
    frame_key: str | None = None,
    registry: Any = None,
    lineage: LineageLedger | None = None,
) -> dict[str, dict[str, Any]]:
    """Measure the four context gates: Bound, Resolved, Verified, Registered.

    Each gate reports ``passed`` and the findings behind it. With no frame named, all four
    are ``applicable: False`` and pass vacuously — an unbound *measurement* is not a
    violation; an unbound *certification* is, and Part 09 is where that distinction is
    enforced.
    """
    catalog = frames if frames is not None else build_frame_registry()
    findings: dict[str, list[str]] = {gate: [] for gate, _, _ in CONTEXT_GATES}
    applicable = frame_key is not None

    if applicable:
        resolution = catalog.resolve(str(frame_key))
        fingerprint = context_fingerprint(resolution) if resolution.complete else {}

        # CV-CONTEXT-01 — Bound.
        if registry is not None and lineage is not None:
            findings["CV-CONTEXT-01"].extend(unbound_subjects(registry, lineage))
        if registry is not None and not getattr(registry, "is_context_bound", False):
            findings["CV-CONTEXT-01"].append("the registry itself declares no reference frame")

        # CV-CONTEXT-02 — Resolved.
        findings["CV-CONTEXT-02"].extend(
            f"{resolution.frame}/{axis}" for axis in resolution.unresolved_axes
        )

        # CV-CONTEXT-03 — Verified: every recorded fingerprint re-derives from the frames.
        if fingerprint:
            if registry is not None and registry.context and registry.context != fingerprint:
                findings["CV-CONTEXT-03"].append(
                    "the registry's binding does not reproduce from the frame registry"
                )
            if lineage is not None:
                for entry in lineage.entries(event=CONTEXT_BOUND):
                    if dict(entry.detail) != fingerprint:
                        findings["CV-CONTEXT-03"].append(
                            f"{entry.subject_id}: recorded context does not reproduce"
                        )
        else:
            findings["CV-CONTEXT-03"].append(
                f"{resolution.frame}: incomplete resolutions have no verifiable fingerprint"
            )

        # CV-CONTEXT-04 — Registered.
        registered = set(
            context_registries(catalog, frame_keys=[resolution.frame])[resolution.frame].kinds()
        )
        admissible = set(introduced_axes())
        findings["CV-CONTEXT-04"].extend(
            f"{resolution.frame}/{axis.axis}"
            for axis in resolution.axes
            if axis.resolved and axis.axis in admissible and axis.axis not in registered
        )

    return {
        gate: {
            "gate": gate,
            "name": name,
            "statement": statement,
            "applicable": applicable,
            "passed": not findings[gate],
            "findings": findings[gate][:5],
            "finding_count": len(findings[gate]),
        }
        for gate, name, statement in CONTEXT_GATES
    }


def to_document(
    registry: Any,
    frames: FrameRegistry | None = None,
) -> dict[str, Any]:
    """The whole binding as one deterministic document."""
    catalog = frames if frames is not None else build_frame_registry()
    dictionary = dictionary_with_context(registry, catalog)
    document = {
        "schema": "ucos-nucleus-context-binding",
        "version": "1.0.0",
        "frame_namespace": FRAME_NAMESPACE,
        "measurements": context_measurements(catalog),
        "dictionary": {
            "count": len(dictionary),
            "by_kind": dictionary.by_kind(),
            "verification": dictionary.verify(),
            "digest": dictionary.digest(),
        },
        "closed_set": False,
        "upper_limit": None,
    }
    document["digest"] = content_hash(document)
    return document


__all__ = [
    "CONTEXT_BOUND",
    "CONTEXT_GATES",
    "FRAME_NAMESPACE",
    "require_complete",
    "context_fingerprint",
    "context_stage_function",
    "execute_in_context",
    "replay_in_context",
    "bind",
    "bind_lineage",
    "bind_registry",
    "unbound_subjects",
    "context_gates",
    "evolve_in_context",
    "evolutions_without_context",
    "dictionary_with_context",
    "context_measurements",
    "to_document",
]
