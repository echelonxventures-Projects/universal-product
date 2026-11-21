"""UCOS Ω∞ Universal Reference Architecture — the transformation registry (Deliverable 4).

AUTHORITY = NONE (DERIVED TRUTH).

WHERE CONVERSIONS NORMALLY LIVE, AND WHY THAT IS THE ASSUMPTION::

    seconds = sols * 88775.244          # inline, in whichever function needed it
    kelvin  = celsius + 273.15          # inline, somewhere else
    utc     = local - offset            # inline, in a third place

THREE HARDCODED REFERENCE RELATIONSHIPS, each invisible because it looks like arithmetic rather than
policy. Every one is a CLAIM: that these two systems are relatable, by this factor, on this
authority, with this loss. None of the four is recorded, so none can be questioned, versioned or
withdrawn — and the factor is usually approximate, which nothing states.

WHAT REPLACES IT. A transformation is a REGISTERED, AUTHORITY-BEARING DECLARATION between two
reference domains, and applying one is a lookup rather than a call to a function somebody inlined.
Four properties travel with it, and each closes a specific way a conversion misleads:

    authority    who answers for the relationship. An ephemeris-derived factor is somebody's
                 published result, not a constant of the software.
    invertible   whether the inverse is also declared. Most physical conversions are not exactly
                 invertible in integers, and asserting round-trip safety that does not hold is how
                 a value drifts through a pipeline.
    lossy        whether information is discarded. A sol-to-second conversion at integer precision
                 loses a fraction of a second per sol, which accumulates.
    apply        the computation, OR ``None``.

``apply is None`` IS THE MOST IMPORTANT STATE IN THIS FILE. It means: this relationship is DECLARED
to exist and is NOT COMPUTABLE HERE. Relating Mars local solar time to a terrestrial civil scale
needs an ephemeris, a chosen landing site and a leap-second table; a governance vocabulary that
shipped a number for it would be asserting an astronomical fact it cannot verify. The alternatives
are worse: omitting the transformation loses the knowledge that the domains are relatable at all,
and shipping an approximate constant produces answers that look measured. So the declaration exists,
the computation is absent, and ``TransformationRegistry.apply`` returns a refusal that NAMES THE
MISSING COMPUTATION and the authority that would have to supply it.

NO TRANSITIVE ARITHMETIC WITHOUT A DECLARED PATH. ``path`` searches the declared edges and returns
the sequence, so a two-step conversion is auditable as two steps with two authorities and two loss
statements. A registry that composed silently would produce a value whose provenance is a chain
nobody recorded, and whose accumulated loss is unstated.

NOTHING HERE KNOWS ANY DOMAIN'S NAME. The registry stores edges between strings and searches them.
It has no opinion about which conversions exist, which are physical, or which matter — so
registering a transformation between two domains this package never heard of requires no edit.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass

from engine.omega_governance.reference.domain import Value


class TransformationError(RuntimeError):
    """A transformation declaration was invalid, or an unknown transformation was resolved.

    RAISED, NEVER DEFAULTED — and, as elsewhere, "these domains are not relatable" is not in scope.
    That is a returned ``TransformationOutcome``, because a population of unrelatable pairs is a
    governance finding and an exception can describe only the first.
    """


@dataclass(frozen=True, order=True)
class Transformation:
    """One declared relationship between two reference domains.

    ``order=True`` so a registry reports its edges deterministically. The callable field is excluded
    from comparison, because two declarations differing only in which function object they hold are
    the same declaration, and a document comparing them byte-for-byte must agree.
    """

    identifier: str
    source: str
    target: str
    authority: str
    description: str = ""
    invertible: bool = False
    lossy: bool = True

    def __post_init__(self) -> None:
        for name, value in (
            ("identifier", self.identifier),
            ("source", self.source),
            ("target", self.target),
        ):
            if not value.strip():
                raise TransformationError(f"a transformation with no {name} cannot be cited")
        if not self.authority.strip():
            raise TransformationError(
                f"transformation {self.identifier!r} names no authority; a conversion factor "
                f"nobody "
                "answers for is a constant of the software pretending to be a fact about the world"
            )
        if self.source == self.target:
            raise TransformationError(
                f"transformation {self.identifier!r} maps {self.source} to itself; identity needs "
                f"no "
                "declaration, and declaring it would put a no-op on every search path"
            )

    def as_record(self) -> dict[str, object]:
        return {
            "transformation": self.identifier,
            "source": self.source,
            "target": self.target,
            "authority": self.authority,
            "description": self.description,
            "invertible": self.invertible,
            "lossy": self.lossy,
        }


@dataclass(frozen=True)
class TransformationOutcome:
    """The result of attempting a transformation. A REFUSAL IS A RESULT, not an exception.

    ``lossy`` and ``authorities`` accumulate across a multi-step path, so a caller can see that a
    two-hop conversion passed through two bodies and lost information twice — which a single
    returned value would hide completely.
    """

    applied: bool
    rule: str
    reason: str
    value: Value | None = None
    path: tuple[str, ...] = ()
    authorities: tuple[str, ...] = ()
    lossy: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "path", tuple(self.path))
        object.__setattr__(self, "authorities", tuple(sorted(set(self.authorities))))

    def as_record(self) -> dict[str, object]:
        record: dict[str, object] = {
            "applied": self.applied,
            "rule": self.rule,
            "reason": self.reason,
            "path": list(self.path),
            "authorities": list(self.authorities),
            "lossy": self.lossy,
        }
        if self.value is not None:
            record["value"] = self.value.as_record()
        return record


#: The rules an outcome can cite. Constants so an audit record names a rule rather than quoting
#: prose that may be reworded.
RULE_APPLIED = "Ω∞-X-01"
RULE_NO_PATH = "Ω∞-X-02"
RULE_NOT_COMPUTABLE = "Ω∞-X-03"
RULE_WRONG_DOMAIN = "Ω∞-X-04"
RULE_IDENTITY = "Ω∞-X-05"


class TransformationRegistry:
    """Declared transformations, searchable as a graph. Open for extension, closed to redefinition.

    HOLDS THE COMPUTATION SEPARATELY FROM THE DECLARATION. ``register`` takes the ``Transformation``
    and an optional ``apply``; the declaration is the auditable artifact and the callable is an
    implementation detail that may legitimately be absent. Keeping them in one dataclass would make
    a non-computable declaration look like a broken one.
    """

    def __init__(
        self,
        seed: Iterable[tuple[Transformation, Callable[[Value], Value] | None]] = (),
    ) -> None:
        self._by_identifier: dict[str, Transformation] = {}
        self._apply: dict[str, Callable[[Value], Value] | None] = {}
        self._edges: dict[tuple[str, str], str] = {}
        for transformation, computation in seed:
            self.register(transformation, computation)

    def register(
        self,
        transformation: Transformation,
        computation: Callable[[Value], Value] | None = None,
    ) -> Transformation:
        existing = self._by_identifier.get(transformation.identifier)
        if existing is not None and existing != transformation:
            raise TransformationError(
                f"transformation {transformation.identifier!r} is already declared differently; "
                f"one "
                "identifier for two relationships makes a converted value's provenance ambiguous"
            )
        edge = (transformation.source, transformation.target)
        claimed = self._edges.get(edge)
        if claimed is not None and claimed != transformation.identifier:
            raise TransformationError(
                f"{transformation.source} -> {transformation.target} is already declared as "
                f"{claimed!r}; a second declaration as {transformation.identifier!r} would make "
                f"the "
                "applicable authority and loss statement depend on registration order"
            )
        self._by_identifier[transformation.identifier] = transformation
        self._apply[transformation.identifier] = computation
        self._edges[edge] = transformation.identifier
        return transformation

    def declare(
        self,
        identifier: str,
        source: str,
        target: str,
        authority: str,
        *,
        description: str = "",
        invertible: bool = False,
        lossy: bool = True,
        computation: Callable[[Value], Value] | None = None,
    ) -> Transformation:
        """Declare from primitives. RULE 3: a new relationship needs no edit to any module."""
        return self.register(
            Transformation(identifier, source, target, authority, description, invertible, lossy),
            computation,
        )

    def resolve(self, identifier: str) -> Transformation:
        try:
            return self._by_identifier[identifier]
        except KeyError:
            raise TransformationError(
                f"{identifier!r} names no declared transformation; declare it before citing it, so "
                "a converted value cannot claim a provenance nobody registered"
            ) from None

    def computable(self, identifier: str) -> bool:
        """Whether the declared relationship can actually be computed here. A COUNTABLE PROPERTY."""
        return self._apply.get(identifier) is not None

    def between(self, source: str, target: str) -> Transformation | None:
        identifier = self._edges.get((source, target))
        return self._by_identifier[identifier] if identifier is not None else None

    def path(self, source: str, target: str) -> tuple[Transformation, ...]:
        """The shortest declared route, or empty. BREADTH-FIRST over declared edges only.

        DETERMINISTIC BY CONSTRUCTION: the frontier is expanded in sorted order, so two runs return
        the same route when several are equally short. A registry that returned whichever route a
        hash iteration reached first would make a converted value's provenance vary between runs.
        """
        if source == target:
            return ()
        frontier: list[tuple[str, tuple[Transformation, ...]]] = [(source, ())]
        seen = {source}
        while frontier:
            current, route = frontier.pop(0)
            outgoing = sorted(
                (self._by_identifier[i] for (s, _), i in self._edges.items() if s == current),
                key=lambda t: t.identifier,
            )
            for transformation in outgoing:
                if transformation.target in seen:
                    continue
                extended = (*route, transformation)
                if transformation.target == target:
                    return extended
                seen.add(transformation.target)
                frontier.append((transformation.target, extended))
        return ()

    def apply(self, value: Value, target: str) -> TransformationOutcome:
        """Transform a value into a target domain, or REFUSE WITH A NAMED REASON.

        Five outcomes, and each refusal is a different finding with a different remedy:

          identity          the value is already in the target domain. Returned unchanged.
          applied           a declared, computable route existed and was followed.
          no path           the domains are not declared relatable. The remedy is a DECLARATION.
          not computable    a route is declared and a step has no computation. The remedy is an
                            IMPLEMENTATION, from the named authority. Collapsing this into "no path"
                            would send a reader to write a declaration that already exists.
          wrong domain      a registered computation returned a value in a domain other than the one
                            its own declaration promised. The remedy is a FIX to that computation.

        WRONG DOMAIN WAS A RAISE AND IS NOW A RESULT, and the change is not cosmetic. `apply`
        already detected the case; it raised `DomainError` out of a method whose entire contract —
        stated on `TransformationOutcome` — is that a refusal is a returned value carrying a rule
        id. The consequence was measurable rather than stylistic: `RULE_WRONG_DOMAIN` was declared,
        exported in `__all__`, and citable by no code path in the package, so the one refusal a
        caller most needs to distinguish (a BROKEN computation, as against an ABSENT one) arrived as
        an exception type shared with schema validation. A caller catching `DomainError` around a
        route could not tell which step, or which kind of fault, it had caught.
        """
        if value.domain == target:
            return TransformationOutcome(
                True, RULE_IDENTITY, f"the value is already in {target}", value
            )
        route = self.path(value.domain, target)
        if not route:
            return TransformationOutcome(
                False,
                RULE_NO_PATH,
                f"no transformation is declared from {value.domain} to {target}; declaring one is "
                "how a deployment states that these two reference systems are relatable, and by "
                "whose authority",
            )
        uncomputable = [t.identifier for t in route if not self.computable(t.identifier)]
        if uncomputable:
            return TransformationOutcome(
                False,
                RULE_NOT_COMPUTABLE,
                f"the route {' -> '.join(t.identifier for t in route)} is declared but "
                f"{', '.join(uncomputable)} carries no computation here; the relationship is real "
                "and its arithmetic belongs to "
                + ", ".join(
                    sorted({t.authority for t in route if not self.computable(t.identifier)})
                )
                + ", which this vocabulary cannot verify and will not approximate",
                path=tuple(t.identifier for t in route),
                authorities=tuple(t.authority for t in route),
                lossy=any(t.lossy for t in route),
            )
        current = value
        for transformation in route:
            computation = self._apply[transformation.identifier]
            if computation is None:  # pragma: no cover - guarded by the uncomputable check above
                raise TransformationError(f"{transformation.identifier} lost its computation")
            current = computation(current)
            if current.domain != transformation.target:
                # Refused rather than raised, and refused HERE rather than after the loop: the
                # remaining steps would each be handed a value from a domain they never declared
                # they accept, so continuing would turn one broken computation into a route-long
                # cascade of well-formed nonsense.
                return TransformationOutcome(
                    False,
                    RULE_WRONG_DOMAIN,
                    f"{transformation.identifier} was declared to produce "
                    f"{transformation.target} and produced {current.domain}; a transformation that "
                    "misreports its output domain corrupts every value downstream while appearing "
                    "well-formed",
                    path=tuple(t.identifier for t in route),
                    authorities=tuple(t.authority for t in route),
                    lossy=any(t.lossy for t in route),
                )
        return TransformationOutcome(
            True,
            RULE_APPLIED,
            f"applied {' -> '.join(t.identifier for t in route)}",
            current,
            tuple(t.identifier for t in route),
            tuple(t.authority for t in route),
            any(t.lossy for t in route),
        )

    def declared(self) -> tuple[Transformation, ...]:
        return tuple(sorted(self._by_identifier.values()))

    def uncomputable(self) -> tuple[str, ...]:
        """Every declared relationship with no computation here. NAMED, so the gap is not a
        silence.
        """
        return tuple(sorted(i for i in self._by_identifier if not self.computable(i)))

    def report(self) -> Mapping[str, object]:
        return {
            "transformations": [t.as_record() for t in self.declared()],
            "count": len(self._by_identifier),
            "uncomputable": list(self.uncomputable()),
            "openness": (
                "Nothing in this registry names a domain. Edges are strings, search is generic, "
                "and a relationship between two domains this package never heard of is a declare() "
                "call."
            ),
        }

    def __contains__(self, identifier: object) -> bool:
        return isinstance(identifier, str) and identifier in self._by_identifier

    def __len__(self) -> int:
        return len(self._by_identifier)


def default_transformations() -> TransformationRegistry:
    """A registry holding the relationships THIS repository is willing to declare.

    DELIBERATELY SMALL, AND THE SMALLNESS IS THE POINT. Two of the three entries carry NO
    computation, because the arithmetic belongs to bodies that publish ephemerides and leap-second
    tables. Shipping a factor would make this file the authority for an astronomical fact, and a
    wrong factor that looks measured is worse than a refusal a reader can see.
    """
    registry = TransformationRegistry()
    registry.declare(
        "Ω∞-X-TEMP-01",
        "TEMPERATURE",
        "UNITS",
        "UCOS-UNITS-AUTHORITY",
        description="A temperature is a magnitude in a unit, once its scale's zero point is "
        "stated. "
        "Declared without computation because the zero point differs per scale and choosing one "
        "here would privilege it.",
        invertible=False,
        lossy=True,
    )
    registry.declare(
        "Ω∞-X-TIME-01",
        "TIME",
        "UNITS",
        "UCOS-TEMPORAL-AUTHORITY",
        description="A temporal position becomes a magnitude in a unit once an epoch and a scale "
        "factor are supplied. NO COMPUTATION HERE: the factor for a non-terrestrial scale needs an "
        "ephemeris, and for a terrestrial one a leap-second table.",
        invertible=False,
        lossy=True,
    )
    registry.declare(
        "Ω∞-X-ID-01",
        "ARTIFACT",
        "IDENTITY",
        "UCOS-IDENTITY-AUTHORITY",
        description="An artifact has a fingerprint under a declared identity provider. Computable, "
        "and lossy by construction — a digest is designed to discard the content.",
        invertible=False,
        lossy=True,
        computation=lambda value: Value(
            "IDENTITY",
            (),
            {
                "provider": str(value.attributes.get("identity_provider", "unstated")),
                "fingerprint": str(value.attributes.get("fingerprint", "")),
            },
        ),
    )
    return registry


__all__ = [
    "RULE_APPLIED",
    "RULE_IDENTITY",
    "RULE_NOT_COMPUTABLE",
    "RULE_NO_PATH",
    "RULE_WRONG_DOMAIN",
    "Transformation",
    "TransformationError",
    "TransformationOutcome",
    "TransformationRegistry",
    "default_transformations",
]
