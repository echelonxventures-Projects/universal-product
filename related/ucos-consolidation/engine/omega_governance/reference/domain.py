"""UCOS Ω∞ Universal Reference Architecture — Rule 2: everything is a reference domain.

AUTHORITY = NONE (DERIVED TRUTH).

THE CLAIM UNDER TEST, WHICH RULE 8 REQUIRES BE ASSUMED FALSE. "We removed the hardcoded
assumptions." A first pass at Phase 2 removed ``datetime.now()`` and then hardcoded ``json.dumps``
and ``hashlib.sha256`` two files later, hardcoded ``tuple[int, ...]`` as the shape of a temporal
position, keyed authority rules by ``dict[int, str]`` so an eighth tier raised ``KeyError``, and
quantified a domain model over a module-level tuple of six axes. FOUR RELOCATIONS AND ONE SURVIVING
CLOSED LIST, in code written specifically to eliminate them. That is the normal outcome, and it is
why Rule 4 says every closed list must be challenged rather than every list somebody noticed.

WHAT A REFERENCE DOMAIN IS. The six-part shape Rule 2 names, and each part exists because its
absence is a way for an assumption to survive registration:

    name                  without it, two domains cannot be told apart
    authority             without it, nobody answers for what a value in this domain MEANS, so the
                          meaning defaults to whatever the reading code assumed
    schema                without it, a value's shape is whatever the producer happened to emit, so
                          every consumer hardcodes a shape
    transformation_rules  without them, relating two domains is arithmetic somebody inlines
    invariants            without them, "valid" is a property of the code that validates
    provenance            without it, a registration cannot be re-derived or withdrawn

NO DOMAIN IS PRIVILEGED, INCLUDING TIME. The fourteen domains below are declared exactly as a
fifteenth would be, by a caller, at runtime. Nothing in this package branches on a domain name.
``TIME`` is not the root of the architecture and does not appear in any signature outside the domain
that implements it — which is why ``reference/`` imports nothing from ``temporal/`` while
``temporal/`` imports from ``reference/``. The dependency direction IS the non-privilege claim, and
it is checked structurally by ``openworld.no_domain_is_privileged``.

WHY ``kind`` IS A FREE STRING AND SCHEMA VALIDATION CHECKS PRESENCE ONLY. A schema that validated
Python types would make every domain's value shape a Python fact, which is Rule 6's violation, and
would make a domain whose values are neither numbers nor strings — a lattice element, a quantum
register, a symbol from an unnamed alphabet — unrepresentable. So ``Field.kind`` is a name the
DOMAIN'S AUTHORITY interprets, this module never reads it, and validation reports missing and
unexpected FIELDS. Shape is checked; meaning is delegated to the body that answers for it.

WHY ``Value.components`` IS ``tuple[object, ...]`` AND NOT ``tuple[int, ...]``. Rule 8 requires a
``NonNumericMeasurementSystem`` to register and operate. Integers make determinism easy, so a
temporal position was typed as integers in the first draft and the architecture quietly acquired the
assumption that measurement is numeric. Determinism is now the ENCODING layer's obligation — a codec
declares ``REPRODUCIBLE`` and ``assert_reproducible`` measures it — and magnitude is the
QUANTITATIVE capability, which a domain of symbols simply does not declare. A consumer needing
arithmetic requires the capability and is refused by name; it does not discover the absence by
computing a mean of symbols.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass, field

from engine.omega_governance.reference.capability import (
    ADDRESSABLE,
    APPEND_ONLY,
    AUTHORITY_BEARING,
    ENCODABLE,
    ENUMERABLE,
    FRAME_RELATIVE,
    IDENTIFIABLE,
    ORDERABLE,
    QUANTITATIVE,
    REPRODUCIBLE,
    TRANSFORMABLE,
    Capability,
    CapabilitySet,
)
from engine.omega_governance.reference.encoding import Encoding


class DomainError(RuntimeError):
    """A domain, schema, invariant or value was invalid, or an unknown domain was resolved.

    RAISED, NEVER DEFAULTED. Resolving an unregistered domain must fail loudly. If it returned a
    freshly invented domain, a value citing a misspelt domain would validate against an empty
    schema, hold no invariants and answer to no authority — a governance record that is well-formed
    and means nothing.
    """


# ---------------------------------------------------------------------------------------- schemas


@dataclass(frozen=True, order=True)
class Field:
    """One declared part of a value's shape.

    ``kind`` is a name THIS MODULE NEVER INTERPRETS. It is written for the domain's authority and
    for a consumer that has been told what the domain means. Interpreting it here would make the set
    of expressible kinds a closed list in this file, which is Rule 4's target.
    """

    name: str
    kind: str
    required: bool = True
    repeated: bool = False
    description: str = ""

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise DomainError("a schema field with no name cannot be required or reported")
        if not self.kind.strip():
            raise DomainError(
                f"field {self.name!r} declares no kind; a field whose kind is unstated is a field "
                "every consumer will guess the shape of"
            )

    def as_record(self) -> dict[str, object]:
        return {
            "name": self.name,
            "kind": self.kind,
            "required": self.required,
            "repeated": self.repeated,
            "description": self.description,
        }


@dataclass(frozen=True, order=True)
class Schema:
    """The declared shape of a value in one domain. A CONTRACT, not a Python type.

    ``validate`` reports missing required fields and unexpected fields as NAMES. It does not
    type-check and deliberately cannot: a domain whose values are lattice elements has no Python
    type to check against, and a schema layer that insisted would exclude it.
    """

    identifier: str
    fields: tuple[Field, ...] = ()
    description: str = ""
    #: Whether a record may carry fields the schema does not declare. OPEN BY DEFAULT, because a
    #: provider knows things about its own values that no shared schema can anticipate — the same
    #: argument Phase 1 records for ``Artifact.metadata``. A domain requiring strictness says so.
    closed: bool = False

    def __post_init__(self) -> None:
        if not self.identifier.strip():
            raise DomainError(
                "a schema must be identified so a record can cite the shape it claims"
            )
        object.__setattr__(self, "fields", tuple(sorted(self.fields)))
        names = [f.name for f in self.fields]
        duplicated = sorted({name for name in names if names.count(name) > 1})
        if duplicated:
            raise DomainError(
                f"schema {self.identifier!r} declares {', '.join(duplicated)} more than once; two "
                "declarations of one field name make the applicable kind depend on table order"
            )

    def required_names(self) -> tuple[str, ...]:
        return tuple(f.name for f in self.fields if f.required)

    def declared_names(self) -> tuple[str, ...]:
        return tuple(f.name for f in self.fields)

    def validate(self, record: Mapping[str, object]) -> tuple[str, ...]:
        """Findings, as sentences. EMPTY MEANS VALID; this never raises and never type-checks."""
        findings = [
            f"missing required field {name!r}"
            for name in self.required_names()
            if name not in record
        ]
        if self.closed:
            findings.extend(
                f"unexpected field {name!r} for a closed schema"
                for name in sorted(record)
                if name not in self.declared_names()
            )
        return tuple(sorted(findings))

    def as_record(self) -> dict[str, object]:
        return {
            "schema": self.identifier,
            "description": self.description,
            "closed": self.closed,
            "fields": [f.as_record() for f in self.fields],
        }


# ------------------------------------------------------------------------------------- invariants


@dataclass(frozen=True)
class Invariant:
    """A property values in a domain must hold, stated in words and OPTIONALLY executable.

    ``predicate is None`` IS A LEGITIMATE AND VISIBLE STATE. A domain may know an invariant it
    cannot check here — "this position corresponds to a real areocentric instant" needs an
    ephemeris. The alternative to admitting that is either omitting the invariant, which loses it,
    or writing a predicate that returns ``True``, which is worse: an invariant that always passes is
    indistinguishable from one that holds. ``executable`` makes the difference countable, and
    ``DomainRegistry.unexecutable_invariants`` reports the population.
    """

    identifier: str
    statement: str
    predicate: Callable[[object], bool] | None = None

    def __post_init__(self) -> None:
        if not self.identifier.strip():
            raise DomainError("an invariant with no identifier cannot be cited by a finding")
        if not self.statement.strip():
            raise DomainError(
                f"invariant {self.identifier!r} states nothing; an invariant whose content lives "
                "only in a predicate cannot be reviewed by anyone who cannot run it"
            )

    @property
    def executable(self) -> bool:
        return self.predicate is not None

    def check(self, value: object) -> bool | None:
        """``True``, ``False``, or ``None`` for "not checkable here". THREE OUTCOMES, not two."""
        if self.predicate is None:
            return None
        return bool(self.predicate(value))

    def as_record(self) -> dict[str, object]:
        return {
            "invariant": self.identifier,
            "statement": self.statement,
            "executable": self.executable,
        }


# ------------------------------------------------------------------------------------- provenance


@dataclass(frozen=True, order=True)
class Provenance:
    """Where a registration came from, so it can be re-derived or withdrawn.

    ``recorded_at`` IS AN OPAQUE ``Value``, NOT A TEMPORAL COORDINATE, and that is what keeps Time
    unprivileged. If provenance held a ``TemporalCoordinate``, ``reference/`` would import
    ``temporal/`` and every domain in the architecture would depend on the time domain — making Time
    the root, which Rule 2 forbids. A ``Value`` in whatever domain the deployment uses for recording
    order is enough, and a deployment with no clock at all leaves it ``None``.
    """

    declared_by: str
    rule: str
    notes: str = ""
    recorded_at: Value | None = None

    def __post_init__(self) -> None:
        if not self.declared_by.strip():
            raise DomainError(
                "a provenance record must name who declared the registration; an anonymous "
                "registration cannot be questioned or withdrawn"
            )
        if not self.rule.strip():
            raise DomainError(
                f"the provenance from {self.declared_by!r} cites no rule, so the registration "
                "rests on nothing a reader can check"
            )

    def as_record(self) -> dict[str, object]:
        record: dict[str, object] = {
            "declared_by": self.declared_by,
            "rule": self.rule,
            "notes": self.notes,
        }
        if self.recorded_at is not None:
            record["recorded_at"] = self.recorded_at.as_record()
        return record


# ------------------------------------------------------------------------------------------ values


@dataclass(frozen=True)
class Value:
    """One value in one domain. ``components`` is OPAQUE, so measurement need not be numeric.

    ``tuple[object, ...]`` rather than ``tuple[int, ...]``: a symbol, a grade, a lattice element, a
    branch label and an integer are all components, and none is a special case. Determinism is the
    encoding layer's obligation — the components must be encodable by the codec in use, which
    ``assert_encodable`` measures — and magnitude is the ``QUANTITATIVE`` capability, which a domain
    of symbols does not declare and a consumer needing arithmetic requires by name.

    ``attributes`` carries domain-declared named parts alongside the positional components, because
    some domains are naturally positional (a coordinate) and others naturally named (a measurement
    with a unit and a method). One type serves both rather than two types that must be kept in step.
    """

    domain: str
    components: tuple[object, ...] = ()
    attributes: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.domain.strip():
            raise DomainError(
                "a value must name its domain; a value whose domain is unknown validates against "
                "no schema, holds no invariant and answers to no authority"
            )
        object.__setattr__(self, "components", tuple(self.components))
        object.__setattr__(self, "attributes", dict(sorted(self.attributes.items())))

    def as_record(self) -> dict[str, object]:
        record: dict[str, object] = {"domain": self.domain, "components": list(self.components)}
        if self.attributes:
            record["attributes"] = dict(self.attributes)
        return record

    def fingerprint(self, encoding: Encoding) -> str:
        """The value's identity UNDER A NAMED ENCODING, which is a required argument.

        No default, deliberately. A fingerprint whose codec is implicit cannot be re-verified,
        because two codecs give one value two byte strings and only one yields the stored
        fingerprint.
        """
        return encoding.fingerprint(self.as_record())

    def __str__(self) -> str:
        rendered = "·".join(str(component) for component in self.components)
        return f"{self.domain}[{rendered}]" if rendered else f"{self.domain}[]"


# ------------------------------------------------------------------------------- reference domains


@dataclass(frozen=True, order=True)
class ReferenceDomain:
    """One measurable concept, declared completely enough to be extended by registration alone.

    ``authority`` MUST BE NON-EMPTY, on the same argument as Ω-2.2: a domain nobody answers for is a
    domain whose meaning is supplied by whichever consumer read it last. There is no fallback here
    because there is nothing to fall back to — a registration is an act, so the actor is known.
    """

    name: str
    authority: str
    schema: Schema
    description: str = ""
    capabilities: CapabilitySet = field(default_factory=CapabilitySet)
    transformation_rules: tuple[str, ...] = ()
    invariants: tuple[Invariant, ...] = ()
    provenance: Provenance | None = None

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise DomainError("a reference domain with no name cannot be registered or cited")
        if not self.authority.strip():
            raise DomainError(
                f"domain {self.name!r} names no authority; a domain nobody answers for has its "
                "meaning supplied by whichever consumer read it last, which is the assumption this "
                "architecture exists to remove"
            )
        object.__setattr__(
            self, "transformation_rules", tuple(sorted(set(self.transformation_rules)))
        )
        object.__setattr__(
            self, "invariants", tuple(sorted(self.invariants, key=lambda i: i.identifier))
        )

    def validate(self, value: Value) -> tuple[str, ...]:
        """Schema findings plus invariant findings, as sentences. NEVER RAISES.

        Returns findings rather than raising because a population of invalid values is a governance
        report, and an exception can only describe the first one. An invariant that cannot be
        checked here contributes a finding SAYING SO, so "unchecked" is visible rather than absent.
        """
        if value.domain != self.name:
            return (
                f"value declares domain {value.domain!r} and was validated against {self.name!r}",
            )
        findings = list(self.schema.validate(dict(value.attributes)))
        for invariant in self.invariants:
            outcome = invariant.check(value)
            if outcome is None:
                findings.append(
                    f"{invariant.identifier} is not executable here, so it was not checked: "
                    f"{invariant.statement}"
                )
            elif not outcome:
                findings.append(f"{invariant.identifier} does not hold: {invariant.statement}")
        return tuple(sorted(findings))

    def supports(self, capability: Capability) -> bool:
        return self.capabilities.supports(capability)

    def as_record(self) -> dict[str, object]:
        record: dict[str, object] = {
            "domain": self.name,
            "authority": self.authority,
            "description": self.description,
            "capabilities": list(self.capabilities.names()),
            "transformation_rules": list(self.transformation_rules),
            "schema": self.schema.as_record(),
            "invariants": [i.as_record() for i in self.invariants],
        }
        if self.provenance is not None:
            record["provenance"] = self.provenance.as_record()
        return record

    def __str__(self) -> str:
        return self.name


class DomainRegistry:
    """Domain name -> ``ReferenceDomain``. Open for extension, closed to redefinition.

    NOTHING IN THIS CLASS BRANCHES ON A DOMAIN NAME. There is no ``if name == "TIME"``, no
    privileged lookup, no required domain and no minimum set enforced. A registry holding one
    caller-invented domain and none of the fourteen below is fully functional, which is the form
    Rule 3 requires "registration only" to take: the registry cannot tell whether a domain shipped
    with the package.
    """

    def __init__(self, seed: Iterable[ReferenceDomain] = ()) -> None:
        self._by_name: dict[str, ReferenceDomain] = {}
        for domain in seed:
            self.declare(domain)

    def declare(self, domain: ReferenceDomain) -> ReferenceDomain:
        existing = self._by_name.get(domain.name)
        if existing is None:
            self._by_name[domain.name] = domain
            return domain
        if existing != domain:
            raise DomainError(
                f"domain {domain.name!r} is already declared with different content; one name with "
                "two schemas makes every value citing it ambiguous about which shape it claims"
            )
        return existing

    def declare_domain(
        self,
        name: str,
        authority: str,
        schema: Schema,
        *,
        description: str = "",
        capabilities: CapabilitySet | None = None,
        transformation_rules: Sequence[str] = (),
        invariants: Sequence[Invariant] = (),
        provenance: Provenance | None = None,
    ) -> ReferenceDomain:
        """Declare from primitives. RULE 3 IN ONE CALL, with no edit to any module."""
        return self.declare(
            ReferenceDomain(
                name=name,
                authority=authority,
                schema=schema,
                description=description,
                capabilities=capabilities or CapabilitySet(),
                transformation_rules=tuple(transformation_rules),
                invariants=tuple(invariants),
                provenance=provenance,
            )
        )

    def resolve(self, name: str) -> ReferenceDomain:
        try:
            return self._by_name[name]
        except KeyError:
            raise DomainError(
                f"{name!r} is not a declared reference domain; declare it before recording values "
                "in it, so a misspelling cannot become a domain with an empty schema and no "
                "authority"
            ) from None

    def validate(self, value: Value) -> tuple[str, ...]:
        """Validate a value against ITS OWN declared domain, resolved by name."""
        return self.resolve(value.domain).validate(value)

    def capable(self, *required: Capability) -> tuple[str, ...]:
        """Domains declaring every named capability. RESOLUTION BY CAPABILITY, never by name.

        The same discipline Phase 1 applies to discovery providers: a consumer needing ordered
        values asks for ``ORDERABLE`` rather than for ``"TIME"``, so a caller's own domain that
        orders things is found without this package having heard of it.
        """
        return tuple(
            sorted(
                name
                for name, domain in self._by_name.items()
                if all(domain.supports(capability) for capability in required)
            )
        )

    def unexecutable_invariants(self) -> tuple[tuple[str, str], ...]:
        """Every declared invariant nothing here can check. A COUNTABLE POPULATION, not a
        silence.
        """
        return tuple(
            sorted(
                (domain.name, invariant.identifier)
                for domain in self._by_name.values()
                for invariant in domain.invariants
                if not invariant.executable
            )
        )

    def assert_authority_total(self) -> None:
        """Refuse a registry holding any domain nobody answers for.

        Construction already refuses an empty authority, so this can only fire for a domain built by
        a future path that bypasses the constructor. It exists where the POPULATION is held, on the
        same argument Ω-2.2 gives for keeping ``assert_total`` next to a total resolver.
        """
        orphans = sorted(
            name for name, domain in self._by_name.items() if not domain.authority.strip()
        )
        if orphans:
            raise DomainError(
                "these domains name no authority, so their meaning is supplied by their readers: "
                + ", ".join(orphans)
            )

    def known(self) -> tuple[ReferenceDomain, ...]:
        return tuple(sorted(self._by_name.values()))

    def report(self) -> dict[str, object]:
        return {
            "domains": [domain.as_record() for domain in self.known()],
            "count": len(self._by_name),
            "unexecutable_invariants": [
                {"domain": d, "invariant": i} for d, i in self.unexecutable_invariants()
            ],
            "openness": (
                "Nothing in DomainRegistry branches on a domain name, enforces a minimum set or "
                "distinguishes a shipped domain from a registered one. A registry holding only "
                "caller-declared domains is fully functional."
            ),
        }

    def __contains__(self, name: object) -> bool:
        return isinstance(name, str) and name in self._by_name

    def __len__(self) -> int:
        return len(self._by_name)


# --------------------------------------------------------------------- the fourteen, as
# REGISTRATIONS
# Rule 2 names fourteen minimum domains. They are declared below EXACTLY AS A FIFTEENTH WOULD BE, by
# construction and then registration. Nothing in this package quantifies over the tuple at the end,
# nothing branches on any of these names, and ``default_domains()`` is a convenience factory a
# caller may decline to call. Their presence is a convenience for this repository's evidence run;
# their absence breaks nothing.


def _schema(identifier: str, description: str, *fields: Field) -> Schema:
    return Schema(identifier, tuple(fields), description)


TIME_DOMAIN = ReferenceDomain(
    name="TIME",
    authority="UCOS-TEMPORAL-AUTHORITY",
    schema=_schema(
        "ucos-time-value",
        "A position in time, stated with its frame, its scale, its ordering and its clock.",
        Field("frame", "REFERENCE_FRAME", description="Where the observation was made."),
        Field("scale", "TIME_SCALE", description="What the components count."),
        Field("ordering", "ORDERING", description="How positions on this scale compare."),
        Field("clock", "CLOCK_IDENTIFIER", description="Which clock produced the position."),
    ),
    description="ONE DOMAIN AMONG FOURTEEN. Not the root of the architecture, and not a dependency "
    "of any other domain: reference/ imports nothing from temporal/, which is what makes this "
    "statement checkable rather than aspirational.",
    capabilities=CapabilitySet.of(ORDERABLE, ENCODABLE, IDENTIFIABLE, FRAME_RELATIVE, REPRODUCIBLE),
    invariants=(
        Invariant(
            "Ω∞-D-T-01",
            "A position carries at least one component; a clock producing none is not a clock.",
            lambda value: bool(getattr(value, "components", ())),
        ),
        Invariant(
            "Ω∞-D-T-02",
            "The position corresponds to a real instant in its declared frame. NOT EXECUTABLE "
            "HERE: verifying it needs an ephemeris for the frame, which a governance vocabulary "
            "cannot own. Declared so the gap is countable rather than absent.",
        ),
    ),
)

SPACE_DOMAIN = ReferenceDomain(
    name="SPACE",
    authority="UCOS-SPATIAL-AUTHORITY",
    schema=_schema(
        "ucos-space-value",
        "A position in space, relative to a declared coordinate system and observer.",
        Field(
            "frame",
            "REFERENCE_FRAME",
            description="The body or construct the frame is anchored to.",
        ),
        Field(
            "coordinate_system",
            "COORDINATE_SYSTEM",
            description="The registered system, e.g. a "
            "geodetic datum, an areocentric frame, a graph embedding. WGS84 is one registration.",
        ),
        Field("observer", "OBSERVER_IDENTIFIER", required=False),
    ),
    description="Latitude, longitude and WGS84 are REGISTRATIONS in this domain, never "
    "requirements. "
    "A graph position and an areocentric one use the same shape.",
    capabilities=CapabilitySet.of(ENCODABLE, IDENTIFIABLE, FRAME_RELATIVE, QUANTITATIVE),
)

UNITS_DOMAIN = ReferenceDomain(
    name="UNITS",
    authority="UCOS-UNITS-AUTHORITY",
    schema=_schema(
        "ucos-units-value",
        "A magnitude in a declared unit of a declared system.",
        Field("system", "UNIT_SYSTEM", description="SI, imperial and any other are registrations."),
        Field("unit", "UNIT", description="The unit the magnitude is expressed in."),
        Field("dimension", "DIMENSION", required=False),
    ),
    description="No unit system is privileged. Conversion between systems is a declared "
    "transformation, never inline arithmetic.",
    capabilities=CapabilitySet.of(ENCODABLE, IDENTIFIABLE, QUANTITATIVE, TRANSFORMABLE, ORDERABLE),
)

TEMPERATURE_DOMAIN = ReferenceDomain(
    name="TEMPERATURE",
    authority="UCOS-UNITS-AUTHORITY",
    schema=_schema(
        "ucos-temperature-value",
        "A temperature on a declared scale.",
        Field(
            "scale",
            "TEMPERATURE_SCALE",
            description="Celsius, Fahrenheit, Kelvin and any other "
            "are registrations. None is the base.",
        ),
    ),
    description="Declared separately from UNITS because temperature scales differ in ZERO POINT as "
    "well as in size, so a ratio is meaningful on one scale and not on another — a distinction a "
    "single unit domain would flatten.",
    capabilities=CapabilitySet.of(ENCODABLE, IDENTIFIABLE, QUANTITATIVE, TRANSFORMABLE, ORDERABLE),
)

VELOCITY_DOMAIN = ReferenceDomain(
    name="VELOCITY",
    authority="UCOS-UNITS-AUTHORITY",
    schema=_schema(
        "ucos-velocity-value",
        "A rate of change of position, in a declared unit and relative to a declared frame.",
        Field("unit", "UNIT"),
        Field(
            "frame", "REFERENCE_FRAME", description="A velocity with no frame is not a velocity."
        ),
    ),
    description="km/h, mph and m/s are registrations. The frame is required because a speed "
    "relative "
    "to an unstated frame is the Earth-centric assumption in miniature.",
    capabilities=CapabilitySet.of(
        ENCODABLE, IDENTIFIABLE, QUANTITATIVE, FRAME_RELATIVE, TRANSFORMABLE
    ),
)

IDENTITY_DOMAIN = ReferenceDomain(
    name="IDENTITY",
    authority="UCOS-IDENTITY-AUTHORITY",
    schema=_schema(
        "ucos-identity-value",
        "A stable fingerprint under a declared identity provider.",
        Field("provider", "IDENTITY_PROVIDER", description="SHA-256 and UUID are registrations."),
        Field("fingerprint", "OPAQUE_STRING"),
    ),
    description="The provider is part of the value because a fingerprint without its provider "
    "cannot "
    "be re-verified.",
    capabilities=CapabilitySet.of(ENCODABLE, IDENTIFIABLE, REPRODUCIBLE, ADDRESSABLE),
)

STORAGE_DOMAIN = ReferenceDomain(
    name="STORAGE",
    authority="UCOS-STORAGE-AUTHORITY",
    schema=_schema(
        "ucos-storage-value",
        "A locator within a declared storage provider.",
        Field(
            "provider",
            "STORAGE_PROVIDER",
            description="Filesystem, object store, database, "
            "graph and ledger are registrations.",
        ),
        Field("locator", "OPAQUE_STRING"),
    ),
    description="A filesystem path, an object key, a row identifier, a node id and a ledger "
    "address "
    "are one shape. The provider is part of the locator because the same string means different "
    "things to different providers, and conflating them is how a federation double-counts.",
    capabilities=CapabilitySet.of(ENCODABLE, IDENTIFIABLE, ADDRESSABLE, ENUMERABLE, APPEND_ONLY),
)

EXECUTION_DOMAIN = ReferenceDomain(
    name="EXECUTION",
    authority="UCOS-EXECUTION-AUTHORITY",
    schema=_schema(
        "ucos-execution-value",
        "An invocation of something, on a declared plane, by a declared invoker.",
        Field(
            "plane",
            "EXECUTION_PLANE",
            description="Python, shell, workflow and scheduler are "
            "registrations. None is required.",
        ),
        Field("invoker", "OPAQUE_STRING", required=False),
    ),
    description="Ω∞ Rule 1 forbids Python, Bash, Make and a CI system as architectural "
    "assumptions. "
    "Each is a registered plane here, and a governance engine implemented in another language "
    "registers its own.",
    capabilities=CapabilitySet.of(ENCODABLE, IDENTIFIABLE, ENUMERABLE),
)

REPRESENTATION_DOMAIN = ReferenceDomain(
    name="REPRESENTATION",
    authority="UCOS-REPRESENTATION-AUTHORITY",
    schema=_schema(
        "ucos-representation-value",
        "A value reduced to bytes by a declared codec.",
        Field("codec", "CODEC", description="JSON, YAML and TOML are registrations."),
    ),
    description="The domain whose first implementation in this package was a hardcoded json.dumps. "
    "It is now a provider slot with two shipped codecs, and the open-world suite runs the whole "
    "pipeline under the non-JSON one.",
    capabilities=CapabilitySet.of(ENCODABLE, REPRODUCIBLE),
)

DISCOVERY_DOMAIN = ReferenceDomain(
    name="DISCOVERY",
    authority="UCOS-DISCOVERY-AUTHORITY",
    schema=_schema(
        "ucos-discovery-value",
        "A population obtained from a declared discovery provider under a declared selector.",
        Field("provider", "DISCOVERY_PROVIDER", description="Git is one registration."),
        Field("selector", "OPAQUE_STRING", required=False),
    ),
    description="The domain Phase 1 built. Registered here so discovery holds no more privilege "
    "than "
    "temperature does.",
    capabilities=CapabilitySet.of(ENUMERABLE, ADDRESSABLE, ENCODABLE, AUTHORITY_BEARING),
)

GOVERNANCE_DOMAIN = ReferenceDomain(
    name="GOVERNANCE",
    authority="UCOS-GOVERNANCE-AUTHORITY",
    schema=_schema(
        "ucos-governance-value",
        "A position on a declared governance axis, reached by a declared rule.",
        Field("axis", "GOVERNANCE_AXIS"),
        Field("state", "GOVERNANCE_STATE"),
        Field("rule", "TRANSITION_RULE", required=False),
    ),
    description="Axes and states are registry values, so governing a concern this package never "
    "named is a registration.",
    capabilities=CapabilitySet.of(ENCODABLE, IDENTIFIABLE, ENUMERABLE, AUTHORITY_BEARING),
)

CERTIFICATION_DOMAIN = ReferenceDomain(
    name="CERTIFICATION",
    authority="UCOS-CERTIFICATION-AUTHORITY",
    schema=_schema(
        "ucos-certification-value",
        "A certification disposition, its inputs and the rule that produced it.",
        Field("disposition", "CERTIFICATION_DISPOSITION"),
        Field("rule", "DECISION_RULE"),
    ),
    description="Independent of MEASUREMENT: a disposition consumes measurements and is not one.",
    capabilities=CapabilitySet.of(ENCODABLE, IDENTIFIABLE, AUTHORITY_BEARING),
)

MEASUREMENT_DOMAIN = ReferenceDomain(
    name="MEASUREMENT",
    authority="UCOS-MEASUREMENT-AUTHORITY",
    schema=_schema(
        "ucos-measurement-value",
        "An observation of a subject, by a declared method, expressed in a declared value domain.",
        Field("subject", "OPAQUE_STRING"),
        Field("method", "MEASUREMENT_METHOD"),
        Field(
            "value_domain",
            "REFERENCE_DOMAIN",
            description="Which domain the observed value "
            "belongs to. May be a non-numeric domain, which is why QUANTITATIVE is NOT declared "
            "on this domain.",
        ),
    ),
    description="DELIBERATELY NOT QUANTITATIVE. A measurement whose values are symbols, grades or "
    "lattice elements is a measurement, and requiring magnitude here would exclude every "
    "non-numeric measurement system Rule 8 demands be registerable.",
    capabilities=CapabilitySet.of(ENCODABLE, IDENTIFIABLE, ENUMERABLE, REPRODUCIBLE),
)

ARTIFACT_DOMAIN = ReferenceDomain(
    name="ARTIFACT",
    authority="UCOS-ARTIFACT-AUTHORITY",
    schema=_schema(
        "ucos-artifact-value",
        "A governed thing, wherever it is held and whatever it is made of.",
        Field("identifier", "OPAQUE_STRING"),
        Field("artifact_type", "ARTIFACT_TYPE", required=False),
        Field("storage", "STORAGE_PROVIDER", required=False),
    ),
    description="Not a file. A document, a dataset, a workflow, an object in a bucket, a node in a "
    "graph and a row in a ledger are artifacts under one shape.",
    capabilities=CapabilitySet.of(
        ENCODABLE, IDENTIFIABLE, ADDRESSABLE, ENUMERABLE, AUTHORITY_BEARING
    ),
)

#: The fourteen. A CONVENIENCE TUPLE for ``default_domains()`` and for readers, and nothing else.
#: Nothing in this package quantifies over it, validates against it, or requires membership in it.
MINIMUM_DOMAINS: tuple[ReferenceDomain, ...] = (
    ARTIFACT_DOMAIN,
    CERTIFICATION_DOMAIN,
    DISCOVERY_DOMAIN,
    EXECUTION_DOMAIN,
    GOVERNANCE_DOMAIN,
    IDENTITY_DOMAIN,
    MEASUREMENT_DOMAIN,
    REPRESENTATION_DOMAIN,
    SPACE_DOMAIN,
    STORAGE_DOMAIN,
    TEMPERATURE_DOMAIN,
    TIME_DOMAIN,
    UNITS_DOMAIN,
    VELOCITY_DOMAIN,
)


def default_domains(extra: Iterable[ReferenceDomain] = ()) -> DomainRegistry:
    """A registry holding the fourteen, plus whatever the caller declares.

    ``DomainRegistry(())`` is equally valid and equally functional. This factory is where THIS
    repository's choice of starting vocabulary is made, and it is the only place that choice
    appears.
    """
    registry = DomainRegistry(MINIMUM_DOMAINS)
    for domain in extra:
        registry.declare(domain)
    return registry


def assert_encodable(value: Value, encoding: Encoding) -> None:
    """Refuse a value the codec in use cannot represent. DELIVERABLE: determinism without numbers.

    This is what replaces ``tuple[int, ...]``. A value's components may be anything, and the
    obligation is that the DECLARED CODEC can encode them — checked here, before a fingerprint
    exists, rather than discovered when two runs disagree.
    """
    record = value.as_record()
    if not encoding.codec.supports(record):
        unsupported = [
            f"components[{index}] of type {type(component).__name__}"
            for index, component in enumerate(value.components)
            if not encoding.codec.supports(component)
        ] or ["one or more attributes"]
        raise DomainError(
            f"{encoding.codec.identifier()} cannot represent this {value.domain} value: "
            + ", ".join(unsupported)
            + "; register a codec for that value domain rather than letting the value be "
            "stringified into bytes nobody can parse back"
        )


__all__ = [
    "ARTIFACT_DOMAIN",
    "CERTIFICATION_DOMAIN",
    "DISCOVERY_DOMAIN",
    "EXECUTION_DOMAIN",
    "GOVERNANCE_DOMAIN",
    "IDENTITY_DOMAIN",
    "MEASUREMENT_DOMAIN",
    "MINIMUM_DOMAINS",
    "REPRESENTATION_DOMAIN",
    "SPACE_DOMAIN",
    "STORAGE_DOMAIN",
    "TEMPERATURE_DOMAIN",
    "TIME_DOMAIN",
    "UNITS_DOMAIN",
    "VELOCITY_DOMAIN",
    "DomainError",
    "DomainRegistry",
    "Field",
    "Invariant",
    "Provenance",
    "ReferenceDomain",
    "Schema",
    "Value",
    "assert_encodable",
    "default_domains",
]
