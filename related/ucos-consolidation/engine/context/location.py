"""UCXI-000001 Part 15 — the Location axis and location-derived context resolution.

Deliverables D-08 … D-17, and the whole of AC-006 and AC-007.

Repository truth before this module
-----------------------------------
:mod:`engine.context` had fifteen universal context kinds, a total authority order and
provenance on every value — the correct substrate. What it did **not** have was a
``LOCATION`` axis: ``SPATIAL`` is *repository path space* ("space here is path space"), and
``calendar``, ``timezone``, ``currency``, ``language`` and ``jurisdiction`` existed only as
*prohibited hardcode tokens* and registrable dimensions. So the enforcement that stops the
wrong answer was in place, and the resolvers that produce the right one were absent.

This module adds the missing axis and the resolvers, entirely as an extension of that
substrate. It introduces no second context registry, no second taxonomy, no second
ontology and no second identifier scheme.

The three properties that make AC-001 checkable
-----------------------------------------------
1. **No axis value appears in this file.** Every calendar, time standard, language,
   currency, unit system, tax model, jurisdiction, governance model, policy and execution
   context lives in ``catalog/reference-frames.json`` as DATA. Grep this module for a
   calendar name and you will not find one.
2. **There is no default and no fallback.** An axis a frame chain does not declare
   resolves to :data:`UNRESOLVED` and is reported with the derivation path that would have
   supplied it. The resolver has nothing to guess with.
3. **No function branches on an axis or a frame.** Resolution is one loop over a declared
   derivation graph, ordered by the single ordering authority. A seventeenth axis is a
   tuple entry in :data:`AXIS_DERIVATION`; a frame from a civilisation nobody has met is a
   JSON object.
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from importlib import resources
from typing import Any

from engine.context.errors import ContextValidationError, TaxonomyError
from engine.context.model import ContextDeclaration, ContextRecord, ContextValue
from engine.context.ontology import (
    UNIVERSAL_ONTOLOGY,
    ContextOntology,
    DimensionSpec,
)
from engine.context.registry import ContextRegistry
from engine.context.taxonomy import (
    ROOT_TAXON,
    UNIVERSAL_TAXONOMY,
    ContextAuthority,
    ContextTaxon,
    ContextTaxonomy,
)
from engine.foundation.composition.ordering import (
    DEFAULT_STRATEGY,
    derive_order,
    unresolved_keys,
)
from engine.registry.universal.identity import RegistryKind, deterministic_id
from engine.uckp.canonical import content_hash

#: The value an axis carries when nothing in the frame chain declared it. It is a
#: *stated unknown*, which the ontology already models, never an invented value.
UNRESOLVED = "unresolved"

#: The namespace every reference frame is registered under.
FRAME_NAMESPACE = "ucos.context.frame"

#: The package data file that declares the frames. DATA, shipped with the wheel.
FRAME_CATALOG = "reference-frames.json"

#: The location axis — the single root from which every derived axis hangs.
LOCATION = "location"

#: The Universal Reality Context Principle: no value may be *interpreted* — measured,
#: validated, governed, certified or executed against — until these five resolve. They are
#: the frame of reference the interpretation happens in, and an interpretation without one
#: is not a weaker claim, it is an unfalsifiable one. Ordered as they derive.
REALITY_CONTEXT_AXES: tuple[str, ...] = (
    "existence",
    "reality",
    "observer",
    "spatial",
    "temporal",
)


#: The constitutional derivation chain of AC-006/AC-007, as ``axis → axes it requires``.
#: This is the whole of the architecture: change an entry and the resolution order
#: changes, with no change to any function below. Sixteen axes; the set is open.
AXIS_DERIVATION: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("existence", ()),
    ("reality", ("existence",)),
    ("observer", ("reality",)),
    ("civilization", ("reality",)),
    ("universe", ("reality",)),
    (LOCATION, ("universe", "civilization")),
    ("spatial", (LOCATION,)),
    ("temporal", (LOCATION, "time-standard")),
    ("jurisdiction", (LOCATION,)),
    ("governance", ("jurisdiction",)),
    ("calendar", (LOCATION,)),
    ("time-standard", (LOCATION,)),
    ("language", (LOCATION,)),
    ("units", (LOCATION,)),
    ("currency", (LOCATION, "units")),
    ("regulation", ("jurisdiction",)),
    ("tax", ("jurisdiction", "currency")),
    ("policy", ("governance", "regulation")),
    (
        "execution-context",
        ("policy", "calendar", "time-standard", "language", "currency", "units", "tax"),
    ),
)

#: ``axis → requires`` in the shape the single ordering authority consumes.
AXIS_GRAPH: Mapping[str, tuple[str, ...]] = dict(AXIS_DERIVATION)


#: The axes AC-007 requires a location to determine. Derived from the graph, not restated:
#: an axis that transitively requires ``location`` is location-determined by construction.
def location_determined_axes() -> tuple[str, ...]:
    """Every axis that transitively derives from :data:`LOCATION`, ordered."""
    determined: set[str] = set()
    changed = True
    while changed:
        changed = False
        for axis, requires in AXIS_DERIVATION:
            if axis in determined or axis == LOCATION:
                continue
            if LOCATION in requires or determined & set(requires):
                determined.add(axis)
                changed = True
    return tuple(sorted(determined))


def axis_order(*, strategy: str = DEFAULT_STRATEGY) -> list[str]:
    """The derived resolution order of the axes.

    Raises:
        ContextValidationError: the declared derivation graph contains a cycle.
    """
    ordering = derive_order(AXIS_GRAPH, strategy=strategy)
    unresolved = unresolved_keys(AXIS_GRAPH, ordering)
    if unresolved:
        raise ContextValidationError(
            "the axis derivation graph contains a cycle", at="AXIS_DERIVATION"
        )
    return [key for _wave, key in ordering]


def axis_waves() -> list[tuple[int, str]]:
    """The axes grouped into dependency waves — what may resolve in parallel."""
    return derive_order(AXIS_GRAPH, strategy="parallel-waves")


def derivation_path(axis: str) -> tuple[str, ...]:
    """The transitive closure of what ``axis`` derives from, ordered.

    This is the provenance chain AC-006 requires: an axis's value is only assertable
    together with the axes it was derived through.
    """
    if axis not in AXIS_GRAPH:
        raise ContextValidationError("unknown context axis", at=axis)
    seen: set[str] = set()
    frontier = list(AXIS_GRAPH[axis])
    while frontier:
        current = frontier.pop()
        if current in seen:
            continue
        seen.add(current)
        frontier.extend(AXIS_GRAPH.get(current, ()))
    return tuple(sorted(seen))


# --------------------------------------------------------------------------- #
# Reference frames                                                             #
# --------------------------------------------------------------------------- #


@dataclass(frozen=True, slots=True)
class ReferenceFrame:
    """One registered reference frame: a location and the axis values it declares.

    ``frame_kind`` is an **open string** (physical, digital, virtual, simulated,
    distributed, planetary, orbital, interplanetary, interstellar, galactic, universal, or
    something nobody has named). Nothing in this module tests it; it is carried for
    discovery only, so an unknown kind costs nothing.
    """

    key: str
    title: str
    frame_kind: str
    parent: str | None = None
    axes: Mapping[str, str] = field(default_factory=dict)
    description: str = ""

    def __post_init__(self) -> None:
        for name in ("key", "title", "frame_kind"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ContextValidationError("frame field must be a non-empty string", at=name)
        declared = dict(self.axes or {})
        for axis, value in declared.items():
            if axis not in AXIS_GRAPH:
                raise ContextValidationError(
                    "a frame may only declare a registered axis", at=axis, frame=self.key
                )
            if not isinstance(value, str) or not value.strip():
                raise ContextValidationError(
                    "an axis value must be a non-empty authority reference",
                    at=axis,
                    frame=self.key,
                )
        object.__setattr__(self, "axes", {k: declared[k].strip() for k in sorted(declared)})

    @property
    def universal_id(self) -> str:
        """The frame's identity, minted by the one identifier authority."""
        return deterministic_id(RegistryKind.LOCATION, FRAME_NAMESPACE, self.key)

    def to_dict(self) -> dict[str, Any]:
        return {
            "universal_id": self.universal_id,
            "key": self.key,
            "title": self.title,
            "frame_kind": self.frame_kind,
            "parent": self.parent,
            "axes": dict(self.axes),
            "description": self.description,
        }


@dataclass(frozen=True, slots=True)
class ResolvedAxis:
    """One resolved axis with the frame that supplied it and its derivation path."""

    axis: str
    value: str
    source_frame: str
    derived_from: tuple[str, ...]
    authority: ContextAuthority = ContextAuthority.ARCHITECTURAL

    @property
    def resolved(self) -> bool:
        return self.value != UNRESOLVED

    @property
    def location_derived(self) -> bool:
        """True iff this axis's provenance chain passes through the location axis."""
        return self.axis == LOCATION or LOCATION in self.derived_from

    def to_dict(self) -> dict[str, Any]:
        return {
            "axis": self.axis,
            "value": self.value,
            "source_frame": self.source_frame,
            "derived_from": list(self.derived_from),
            "authority": self.authority.value,
            "resolved": self.resolved,
            "location_derived": self.location_derived,
        }


@dataclass(frozen=True, slots=True)
class LocationResolution:
    """The complete resolution of every axis for one frame."""

    frame: str
    frame_id: str
    chain: tuple[str, ...]
    axes: tuple[ResolvedAxis, ...]
    order: tuple[str, ...]

    def get(self, axis: str) -> ResolvedAxis:
        for resolved in self.axes:
            if resolved.axis == axis:
                return resolved
        raise ContextValidationError("axis was not resolved", at=axis, frame=self.frame)

    def value_of(self, axis: str) -> str:
        return self.get(axis).value

    def value_mapping(self) -> dict[str, str]:
        return {a.axis: a.value for a in self.axes}

    @property
    def unresolved_axes(self) -> tuple[str, ...]:
        return tuple(a.axis for a in self.axes if not a.resolved)

    @property
    def resolved_axes(self) -> tuple[str, ...]:
        return tuple(a.axis for a in self.axes if a.resolved)

    @property
    def complete(self) -> bool:
        """True iff every declared axis resolved to a registered authority."""
        return not self.unresolved_axes

    @property
    def reality_context(self) -> dict[str, str]:
        """The five Reality Context axes and their resolved values."""
        return {axis: self.value_of(axis) for axis in REALITY_CONTEXT_AXES}

    @property
    def reality_context_gaps(self) -> tuple[str, ...]:
        """Those of the five that did not resolve. Empty means interpretation may proceed."""
        return tuple(axis for axis in REALITY_CONTEXT_AXES if not self.get(axis).resolved)

    @property
    def reality_context_resolved(self) -> bool:
        """True iff every Reality Context axis resolved for this frame."""
        return not self.reality_context_gaps

    def location_derived_count(self) -> int:
        """How many resolved axes carry a location-derived provenance chain."""
        return sum(1 for a in self.axes if a.resolved and a.location_derived)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "ucos-location-resolution",
            "version": "1.0.0",
            "frame": self.frame,
            "frame_id": self.frame_id,
            "chain": list(self.chain),
            "order": list(self.order),
            "axes": [a.to_dict() for a in self.axes],
            "resolved": list(self.resolved_axes),
            "unresolved": list(self.unresolved_axes),
            "complete": self.complete,
            "location_derived_axes": self.location_derived_count(),
            "reality_context": self.reality_context,
            "reality_context_gaps": list(self.reality_context_gaps),
            "reality_context_resolved": self.reality_context_resolved,
        }

    def digest(self) -> str:
        return content_hash(self.to_dict())


class FrameRegistry:
    """The open registry of reference frames, and the resolver over them.

    Frames form a tree: a frame names its parent, inherits every axis the parent chain
    declares, and overrides any axis it declares itself. Nothing is hardcoded — including
    the root, which declares no axis at all.
    """

    __slots__ = ("_frames",)

    def __init__(self, frames: Iterable[ReferenceFrame] = ()) -> None:
        self._frames: dict[str, ReferenceFrame] = {}
        for frame in frames:
            self.register(frame)

    # -- registration ------------------------------------------------------- #

    def register(self, frame: ReferenceFrame) -> ReferenceFrame:
        """Admit one frame.

        Raises:
            ContextValidationError: the key is taken, the parent is unregistered, or the
                declaration would create a cycle.
        """
        if frame.key in self._frames:
            raise ContextValidationError("reference frame is already registered", at=frame.key)
        if frame.parent is not None and frame.parent not in self._frames:
            raise ContextValidationError(
                "a frame's parent must already be registered", at=frame.key, parent=frame.parent
            )
        self._frames[frame.key] = frame
        try:
            self.chain(frame.key)
        except ContextValidationError:
            del self._frames[frame.key]
            raise
        return frame

    def register_all(self, frames: Iterable[ReferenceFrame]) -> tuple[ReferenceFrame, ...]:
        return tuple(self.register(frame) for frame in frames)

    # -- lookup ------------------------------------------------------------- #

    def __len__(self) -> int:
        return len(self._frames)

    def has(self, key: str) -> bool:
        return key in self._frames

    def frame(self, key: str) -> ReferenceFrame:
        found = self._frames.get(key)
        if found is None:
            raise ContextValidationError("reference frame is not registered", at=str(key))
        return found

    def frames(self, *, frame_kind: str | None = None) -> tuple[ReferenceFrame, ...]:
        found = tuple(self._frames[k] for k in sorted(self._frames))
        if frame_kind is not None:
            found = tuple(f for f in found if f.frame_kind == frame_kind)
        return found

    def frame_keys(self) -> tuple[str, ...]:
        return tuple(sorted(self._frames))

    def frame_kinds(self) -> tuple[str, ...]:
        return tuple(sorted({f.frame_kind for f in self._frames.values()}))

    def chain(self, key: str) -> tuple[str, ...]:
        """The frame chain from ``key`` up to its root, refusing a cycle."""
        seen: set[str] = set()
        chain: list[str] = []
        cursor: str | None = key
        while cursor is not None:
            if cursor in seen:
                raise ContextValidationError("cycle in the reference frame tree", at=key)
            seen.add(cursor)
            chain.append(cursor)
            cursor = self.frame(cursor).parent
        return tuple(chain)

    def children(self, key: str) -> tuple[str, ...]:
        self.frame(key)
        return tuple(sorted(k for k, f in self._frames.items() if f.parent == key))

    # -- resolution --------------------------------------------------------- #

    def resolve(self, key: str, *, strategy: str = DEFAULT_STRATEGY) -> LocationResolution:
        """Resolve every axis for frame ``key``.

        The chain is walked from the frame outward to the root; the first declaration of an
        axis wins, so a locality overrides its planet and a planet overrides its
        civilisation. An axis no frame in the chain declares resolves to
        :data:`UNRESOLVED` — there is no default, no built-in and no inference.
        """
        frame = self.frame(key)
        chain = self.chain(key)
        order = axis_order(strategy=strategy)
        resolved: list[ResolvedAxis] = []
        for axis in order:
            value = UNRESOLVED
            source = ""
            for step in chain:
                declared = self._frames[step].axes.get(axis)
                if declared is not None:
                    value, source = declared, step
                    break
            resolved.append(
                ResolvedAxis(
                    axis=axis,
                    value=value,
                    source_frame=source,
                    derived_from=derivation_path(axis),
                )
            )
        return LocationResolution(
            frame=frame.key,
            frame_id=frame.universal_id,
            chain=chain,
            axes=tuple(resolved),
            order=tuple(order),
        )

    def rebase(self, subject: str, *, frame_keys: Sequence[str]) -> dict[str, Any]:
        """Resolve one subject across several frames and report what changed.

        This is the AC-007 proof: a change of location re-resolves every dependent axis,
        with no code path aware of any particular location. ``subject`` is carried through
        for attribution only; it is never interpreted.
        """
        resolutions = {key: self.resolve(key) for key in frame_keys}
        axes = axis_order()
        differing = [
            axis
            for axis in axes
            if len({resolutions[key].value_of(axis) for key in frame_keys}) > 1
        ]
        return {
            "schema": "ucos-location-rebase",
            "subject": subject,
            "frames": list(frame_keys),
            "axes_compared": axes,
            "axes_differing": differing,
            "differing_count": len(differing),
            "resolutions": {key: resolutions[key].to_dict() for key in frame_keys},
            "digests": {key: resolutions[key].digest() for key in frame_keys},
        }

    def coverage(self) -> dict[str, Any]:
        """Per-frame resolution coverage — the measurement D-09…D-17 are graded on."""
        axes = axis_order()
        rows = []
        for frame in self.frames():
            resolution = self.resolve(frame.key)
            rows.append(
                {
                    "frame": frame.key,
                    "frame_kind": frame.frame_kind,
                    "resolved": len(resolution.resolved_axes),
                    "unresolved": len(resolution.unresolved_axes),
                    "location_derived": resolution.location_derived_count(),
                    "complete": resolution.complete,
                }
            )
        complete = [r for r in rows if r["complete"]]
        return {
            "schema": "ucos-location-coverage",
            "version": "1.0.0",
            "axis_count": len(axes),
            "axes": axes,
            "location_determined_axes": list(location_determined_axes()),
            "frame_count": len(self),
            "frame_kinds": list(self.frame_kinds()),
            "frames": rows,
            "complete_frames": len(complete),
            "incomplete_frames": len(rows) - len(complete),
        }

    def to_document(self) -> dict[str, Any]:
        return {
            "schema": "ucos-reference-frame-registry",
            "version": "1.0.0",
            "count": len(self._frames),
            "axes": [{"axis": a, "requires": list(r)} for a, r in AXIS_DERIVATION],
            "axis_order": axis_order(),
            "frames": [self._frames[k].to_dict() for k in sorted(self._frames)],
            "closed_set": False,
            "upper_limit": None,
        }

    def digest(self) -> str:
        return content_hash(self.to_document())


# --------------------------------------------------------------------------- #
# Catalogue loading                                                            #
# --------------------------------------------------------------------------- #


def load_catalog() -> Mapping[str, Any]:
    """Read the declared frame catalogue (DATA shipped as package data)."""
    text = resources.files("engine.context").joinpath("catalog", FRAME_CATALOG).read_text("utf-8")
    payload = json.loads(text)
    if not isinstance(payload, dict) or not isinstance(payload.get("frames"), list):
        raise ContextValidationError("frame catalogue must carry a 'frames' list")
    return payload


def frames_from_catalog(payload: Mapping[str, Any] | None = None) -> tuple[ReferenceFrame, ...]:
    """Build frames from a catalogue payload, ordered so parents precede children.

    A supplied payload is shape-checked exactly as a loaded one is: a caller passing its
    own catalogue is the same trust boundary as the file, and a ``KeyError`` escaping from
    here would be an untyped failure in a layer whose whole contract is typed refusal.
    """
    document = payload if payload is not None else load_catalog()
    if not isinstance(document.get("frames"), list):
        raise ContextValidationError("frame catalogue must carry a 'frames' list")
    raw = [entry for entry in document["frames"] if isinstance(entry, Mapping)]
    built: dict[str, ReferenceFrame] = {}
    for entry in raw:
        frame = ReferenceFrame(
            key=entry.get("key", ""),
            title=entry.get("title", ""),
            frame_kind=entry.get("frame_kind", ""),
            parent=entry.get("parent"),
            axes=entry.get("axes", {}) or {},
            description=entry.get("description", "") or "",
        )
        built[frame.key] = frame
    graph = {key: ((frame.parent,) if frame.parent else ()) for key, frame in built.items()}
    ordering = derive_order(graph)
    stalled = unresolved_keys(graph, ordering)
    if stalled:
        raise ContextValidationError(
            "frame catalogue contains a cycle or an unknown parent", at=",".join(sorted(stalled))
        )
    return tuple(built[key] for _wave, key in ordering)


def build_frame_registry(payload: Mapping[str, Any] | None = None) -> FrameRegistry:
    """The declared frame registry — the common entry point."""
    return FrameRegistry(frames_from_catalog(payload))


# --------------------------------------------------------------------------- #
# Integration with the existing context layer                                  #
# --------------------------------------------------------------------------- #


def extended_taxonomy(taxonomy: ContextTaxonomy = UNIVERSAL_TAXONOMY) -> ContextTaxonomy:
    """Admit every derivation axis absent from the universal taxonomy, as DATA.

    Uses :meth:`ContextTaxonomy.extend` — the layer's own declared extension point — so
    the new axes are classified by the one taxonomy rather than by a parallel one. Axes
    already classified (existence, reality, governance, …) are left untouched.
    """
    result = taxonomy
    for axis, _requires in AXIS_DERIVATION:
        try:
            result.taxon_for_kind(axis)
            continue
        except TaxonomyError:
            pass
        result = result.extend(
            ContextTaxon(
                taxon_id=f"CTX-{axis.upper().replace('-', '-')}",
                kind=axis,
                title=f"{axis.replace('-', ' ').title()} Context",
                parent=ROOT_TAXON,
                description=(
                    f"The {axis} axis, derived from "
                    f"{', '.join(AXIS_GRAPH[axis]) or 'nothing (a root axis)'}."
                ),
            )
        )
    return result


def extended_ontology(ontology: ContextOntology = UNIVERSAL_ONTOLOGY) -> ContextOntology:
    """Declare the shape of every axis this module adds, through the one ontology.

    Each new axis has the same simple shape — a required ``authority`` reference and the
    frame that supplied it — because an axis value is a reference, never a structure. One
    shape for all of them is what stops a per-axis special case from existing.
    """
    result = ontology
    for axis in introduced_axes(result):
        result = result.extend(
            axis,
            (
                DimensionSpec(
                    name="authority",
                    value_type="string",
                    required=True,
                    description=f"the registered authority that determines {axis}",
                ),
                DimensionSpec(
                    name="frame",
                    value_type="string",
                    required=True,
                    description="the reference frame that supplied the value",
                ),
            ),
        )
    return result


def introduced_axes(ontology: ContextOntology = UNIVERSAL_ONTOLOGY) -> tuple[str, ...]:
    """The axes this module introduces — those the given ontology does not already specify.

    ``existence``, ``reality`` and ``governance`` already have declared shapes owned by the
    context layer. This module extends the *set* of axes; it does not restate the shape of
    an axis somebody else already owns, because that would be a second authority over one
    model — exactly what AC-011 forbids.
    """
    return tuple(axis for axis, _requires in AXIS_DERIVATION if not ontology.specifies(axis))


def declarations_for(
    resolution: LocationResolution,
    *,
    authority: ContextAuthority = ContextAuthority.ARCHITECTURAL,
    axes: Sequence[str] | None = None,
) -> tuple[ContextDeclaration, ...]:
    """Turn a resolution into registrable context declarations, one per resolved axis.

    Two filters apply, and both are constitutional rather than convenient:

    * only **resolved** axes are declared — an unresolved axis is a stated gap, and
      registering a gap as though it were a determination is the silent-default failure
      this module exists to prevent; and
    * only axes this module **introduced** are declared (see :func:`introduced_axes`), so
      an axis already owned by the context layer keeps its one owner.
    """
    admissible = set(axes) if axes is not None else set(introduced_axes())
    source = f"{FRAME_NAMESPACE}:{resolution.frame}"
    declarations: list[ContextDeclaration] = []
    for axis in resolution.axes:
        if not axis.resolved or axis.axis not in admissible:
            continue
        declarations.append(
            ContextDeclaration(
                kind=axis.axis,
                namespace=FRAME_NAMESPACE,
                natural_key=f"{resolution.frame}.{axis.axis}",
                values=(
                    ContextValue(
                        dimension="authority",
                        value=axis.value,
                        authority=authority,
                        source=source,
                    ),
                    ContextValue(
                        dimension="frame",
                        value=axis.source_frame,
                        authority=authority,
                        source=source,
                    ),
                ),
                authority=authority,
                boundary=resolution.frame,
                description=f"{axis.axis} for frame {resolution.frame}",
            )
        )
    return tuple(declarations)


def require_reality_context(resolution: LocationResolution) -> LocationResolution:
    """Fail closed unless the five Reality Context axes resolved.

    The Universal Reality Context Principle, as an executable precondition: measurement,
    validation, governance, certification and execution each call this before they read a
    value, so an interpretation without a frame of reference cannot happen rather than
    merely being discouraged.

    It is deliberately *weaker* than requiring a complete resolution: a frame may leave a
    currency or a tax model unresolved and still be a reality in which things can lawfully
    be observed. What it may not leave unresolved is what it *means* to observe — who is
    observing, in which reality, where and when.

    Raises:
        ContextValidationError: one or more of the five did not resolve. The gaps are
            carried on the error, so the refusal names what is missing.
    """
    gaps = resolution.reality_context_gaps
    if gaps:
        raise ContextValidationError(
            "no value may be interpreted before the reality context resolves",
            at=resolution.frame,
            unresolved=list(gaps),
            required=list(REALITY_CONTEXT_AXES),
        )
    return resolution


def register_resolution(
    registry: ContextRegistry,
    resolution: LocationResolution,
    *,
    authority: ContextAuthority = ContextAuthority.ARCHITECTURAL,
    axes: Sequence[str] | None = None,
    require_complete: bool = False,
) -> tuple[ContextRecord, ...]:
    """Enter one frame's resolved axes into the **one** context registration authority.

    This is what makes a resolved axis Repository Truth rather than a computation: it
    becomes a registered context, classified by the one taxonomy, shaped by the one
    ontology, identified by the one identifier authority and journaled in the one audit
    chain. No second registry is created here — the registry is passed in.

    Args:
        require_complete: refuse a frame that did not resolve every declared axis.
            Off by default because a partially declared frame is a legitimate
            intermediate state whose *gaps* are the honest answer; on, it is the
            fail-closed admission gate a consumer that needs a total context asks for.

    Raises:
        ContextValidationError: ``require_complete`` and the frame is incomplete.
    """
    if require_complete and not resolution.complete:
        raise ContextValidationError(
            "an incomplete frame may not be admitted as a resolved context",
            at=resolution.frame,
            unresolved=list(resolution.unresolved_axes),
        )
    return registry.register_all(declarations_for(resolution, authority=authority, axes=axes))


def empty_context_registry() -> ContextRegistry:
    """A context registry that knows about the axes this module introduces.

    Constructed over :func:`extended_taxonomy` and :func:`extended_ontology`, so every
    introduced axis is classified and shaped *before* anything is registered — an
    unclassified kind is then refused at the registration boundary, which is where the
    refusal belongs.
    """
    return ContextRegistry(taxonomy=extended_taxonomy(), ontology=extended_ontology())


def build_context_registry(
    frame_key: str,
    *,
    frames: FrameRegistry | None = None,
    registry: ContextRegistry | None = None,
    authority: ContextAuthority = ContextAuthority.ARCHITECTURAL,
    require_complete: bool = False,
) -> ContextRegistry:
    """Project **one** frame's resolution into a context registry.

    One frame, one registry — deliberately, and the context layer is what proves it has
    to be so. A registry holding every frame's axes carries fourteen equally-authoritative
    answers to "what is the calendar?", and CXL-07 refuses an equal-authority
    disagreement rather than picking one. That refusal is correct: an unqualified question
    asked of many realities has no answer. A context registry therefore represents exactly
    one reference frame, and reasoning across frames is federation
    (:mod:`engine.context.composition`), not a bigger registry.

    Registration order is the frame's own axis order, so the audit chain and the seal are
    deterministic.
    """
    catalog = frames if frames is not None else build_frame_registry()
    target = registry if registry is not None else empty_context_registry()
    register_resolution(
        target,
        catalog.resolve(frame_key),
        authority=authority,
        require_complete=require_complete,
    )
    return target


def context_registries(
    frames: FrameRegistry | None = None,
    *,
    frame_keys: Sequence[str] | None = None,
    authority: ContextAuthority = ContextAuthority.ARCHITECTURAL,
    require_complete: bool = False,
) -> dict[str, ContextRegistry]:
    """One context registry per frame, keyed by frame — the federated projection."""
    catalog = frames if frames is not None else build_frame_registry()
    keys = tuple(frame_keys) if frame_keys is not None else catalog.frame_keys()
    return {
        key: build_context_registry(
            key, frames=catalog, authority=authority, require_complete=require_complete
        )
        for key in keys
    }


def identity_tuples(registry: FrameRegistry | None = None) -> tuple[tuple[str, str, str], ...]:
    """Every ``(kind, namespace, natural_key)`` this architecture mints an identifier for.

    Frames mint under :attr:`RegistryKind.LOCATION`; each resolved axis of each frame
    mints under :attr:`RegistryKind.CONTEXT`, which is the same tuple the context
    registry uses, so the dictionary and the registry agree on identity by construction
    rather than by convention.
    """
    catalog = registry if registry is not None else build_frame_registry()
    tuples: list[tuple[str, str, str]] = []
    admissible = set(introduced_axes())
    for frame in catalog.frames():
        tuples.append((RegistryKind.LOCATION.value, FRAME_NAMESPACE, frame.key))
        resolution = catalog.resolve(frame.key)
        for axis in resolution.axes:
            if axis.resolved and axis.axis in admissible:
                tuples.append(
                    (
                        RegistryKind.CONTEXT.value,
                        FRAME_NAMESPACE,
                        f"{frame.key}.{axis.axis}",
                    )
                )
    return tuple(tuples)


def to_document(registry: FrameRegistry | None = None) -> dict[str, Any]:
    """The whole location architecture as a deterministic document."""
    frames = registry if registry is not None else build_frame_registry()
    return {
        "schema": "ucos-location-architecture",
        "version": "1.0.0",
        "location_axis": LOCATION,
        "axis_count": len(AXIS_DERIVATION),
        "axes": [{"axis": a, "requires": list(r)} for a, r in AXIS_DERIVATION],
        "axis_order": axis_order(),
        "axis_waves": [{"wave": w, "axis": k} for w, k in axis_waves()],
        "location_determined_axes": list(location_determined_axes()),
        "registry": frames.to_document(),
        "coverage": frames.coverage(),
        "unresolved_marker": UNRESOLVED,
        "defaults": [],
        "closed_set": False,
        "upper_limit": None,
    }


__all__ = [
    "UNRESOLVED",
    "FRAME_NAMESPACE",
    "FRAME_CATALOG",
    "LOCATION",
    "REALITY_CONTEXT_AXES",
    "require_reality_context",
    "AXIS_DERIVATION",
    "AXIS_GRAPH",
    "ReferenceFrame",
    "ResolvedAxis",
    "LocationResolution",
    "FrameRegistry",
    "location_determined_axes",
    "axis_order",
    "axis_waves",
    "derivation_path",
    "load_catalog",
    "frames_from_catalog",
    "build_frame_registry",
    "extended_taxonomy",
    "extended_ontology",
    "introduced_axes",
    "declarations_for",
    "register_resolution",
    "empty_context_registry",
    "build_context_registry",
    "context_registries",
    "identity_tuples",
    "to_document",
]
