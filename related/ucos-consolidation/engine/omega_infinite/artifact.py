"""UCOS Ω∞ Phase 1, Deliverable 3 — the universal Artifact. Not a file, and not a Python file.

AUTHORITY = NONE (DERIVED TRUTH). A vocabulary, not a policy.

THE ASSUMPTION THIS REMOVES. ``engine/universal_discovery/model.py`` defines an artifact as::

    path: str          # a POSIX repo-relative filesystem path
    module: str        # a DOTTED PYTHON MODULE NAME
    statements: int    # counted from a PYTHON ast
    callables: int     # counted from a PYTHON ast
    imports: int       # counted from a PYTHON ast

Five of its fields are Python, and one is a filesystem. That model cannot describe a row in a
dataset, an object in a bucket, or a workflow definition — not because anyone decided to exclude
them, but because the vocabulary has no word for them. Ω∞ Rule Ω-1 names this exactly: Python and
the filesystem must be IMPLEMENTATIONS of abstractions, never the abstractions themselves.

THE SIX-PART SHAPE, AND WHY EACH PART IS UNIVERSAL RATHER THAN CONVENIENT.

  identifier     stable, provider-scoped, opaque. NOT a path. A path is one provider's way of
                 naming a thing; an object key, a URN and a graph node id are others.
  location       where the bytes are, expressed as ``(provider, locator, revision)``. The
                 provider is part of the location because "the same locator" means different
                 things to different providers, and conflating them is how a federation
                 double-counts.
  type           an extensible ArtifactType. PYTHON is a VALUE here, which is the entire point:
                 the system no longer has a Python case, it has a Python type.
  authority      who owns it and by which derivation step. Carried, never inferred here.
  metadata       provider-declared facts. Open by construction, because a provider knows things
                 about its own artifacts that no abstraction can anticipate.
  relationships  typed edges to other identifiers. The extension point for graph knowledge
                 spaces, dependency closure and lineage — none of which are Phase 1 features,
                 and all of which need somewhere to land or they force a redesign later.

WHAT IS DELIBERATELY ABSENT, AND THIS IS THE HARDEST CONSTRAINT IN THE FILE. There is NO
``statements``, NO ``callables``, NO ``imports`` and NO ``module``. Those are measurements of one
artifact type, produced by a Python-specific analyser, and putting them here is what made the
previous model unable to describe anything else. A language-specific measurement belongs in a
language-specific analyser and reaches this model through ``metadata`` — which is why ``metadata``
is a mapping and not a fixed record.

DETERMINISM IS A CONSTRUCTION, NOT A CONVENTION. ``metadata`` is normalised to a sorted tuple of
pairs internally and ``relationships`` is sorted on construction, so two artifacts built from the
same facts in a different order are equal and serialise to identical bytes. The Ω∞ evidence
document is compared byte-for-byte, and a dict ordering difference would break that for a reason
unrelated to discovery.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field


class ArtifactError(RuntimeError):
    """An artifact could not be constructed from the facts supplied.

    An artifact with no identifier or no type is not a degraded artifact, it is an unusable one:
    every downstream join is keyed on the identifier and every classification asserts the type.
    """


# ------------------------------------------------------------------------------- artifact types


@dataclass(frozen=True, order=True)
class ArtifactType:
    """One artifact kind: a canonical name and what it means.

    A VALUE CLASS AND NOT AN ENUM, for the reason Rule Ω-1 gives. An enum member cannot be added
    by a provider at runtime, so an enum would mean that supporting a new kind of artifact requires
    editing this file — the exact structural limit Phase 1 exists to remove. ``ArtifactType`` is
    open; the six constants below are a starting vocabulary, not a closed world.
    """

    name: str
    description: str = ""

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ArtifactError("an artifact type must have a name")

    def __str__(self) -> str:
        return self.name


PYTHON = ArtifactType(
    "PYTHON",
    "Executable Python source. A TYPE, not a system assumption: the Ω-1 measurements that count "
    "statements and imports apply to artifacts of this type and are silent about every other.",
)
DOCUMENT = ArtifactType(
    "DOCUMENT",
    "Prose intended to be read — determinations, reports, specifications, README files.",
)
CONFIGURATION = ArtifactType(
    "CONFIGURATION",
    "Declarative settings that change behaviour without being executed directly.",
)
WORKFLOW = ArtifactType(
    "WORKFLOW",
    "An orchestration definition: a CI pipeline, a job graph, a scheduled task.",
)
DATASET = ArtifactType(
    "DATASET",
    "Structured data consumed as input or emitted as evidence, rather than read as prose.",
)
UNKNOWN = ArtifactType(
    "UNKNOWN",
    "No classifier in the pipeline could type this artifact. A NAMED FINDING and never an "
    "absence — the population of UNKNOWN is a number that can be reported and driven down, which "
    "is precisely what an untyped artifact could never be.",
)

#: The initial vocabulary. Every one of the six is a value, so a seventh is a registration rather
#: than an edit to a control-flow branch anywhere in this package.
INITIAL_TYPES: tuple[ArtifactType, ...] = (
    CONFIGURATION,
    DATASET,
    DOCUMENT,
    PYTHON,
    UNKNOWN,
    WORKFLOW,
)


class ArtifactTypeRegistry:
    """Canonical ``name -> ArtifactType``. Open for extension, closed to redefinition.

    Same construction and same argument as ``CapabilityRegistry``: one name with two meanings makes
    every assertion about that name unenforceable, so a conflicting re-declaration is refused.
    """

    def __init__(self, seed: Iterable[ArtifactType] = INITIAL_TYPES) -> None:
        self._by_name: dict[str, ArtifactType] = {}
        for artifact_type in seed:
            self.declare(artifact_type)

    def declare(self, artifact_type: ArtifactType) -> ArtifactType:
        existing = self._by_name.get(artifact_type.name)
        if existing is None:
            self._by_name[artifact_type.name] = artifact_type
            return artifact_type
        if existing.description != artifact_type.description:
            raise ArtifactError(
                f"artifact type {artifact_type.name!r} is already declared with a different "
                "meaning; one name with two meanings makes every claim about it unenforceable"
            )
        return existing

    def declare_name(self, name: str, description: str) -> ArtifactType:
        return self.declare(ArtifactType(name, description))

    def resolve(self, name: str) -> ArtifactType:
        try:
            return self._by_name[name]
        except KeyError:
            raise ArtifactError(
                f"{name!r} is not a declared artifact type; declare it before using it so that a "
                "misspelling cannot silently become a seventh kind of artifact"
            ) from None

    def known(self) -> tuple[ArtifactType, ...]:
        return tuple(sorted(self._by_name.values()))

    def __contains__(self, name: object) -> bool:
        return isinstance(name, str) and name in self._by_name

    def __len__(self) -> int:
        return len(self._by_name)


#: The process-wide type vocabulary.
TYPES = ArtifactTypeRegistry()


# ----------------------------------------------------------------------------------- location


@dataclass(frozen=True, order=True)
class Location:
    """Where an artifact's bytes are, without asserting that they are on a filesystem.

    ``provider`` IS PART OF THE IDENTITY OF A LOCATION. Two providers can both hand back the
    locator ``config.toml`` and mean different bytes; a federation that treated the locator alone
    as the key would silently merge them. Including the provider is what makes a federated
    knowledge space possible without a redesign.

    ``revision`` is OPTIONAL and empty is honest. A provider that cannot name a revision declares
    no ``VERSIONED_CONTENT`` capability and leaves this empty, rather than inventing a timestamp
    that would make an unversioned enumeration look reproducible.
    """

    provider: str
    locator: str
    revision: str = ""

    def __post_init__(self) -> None:
        if not self.provider.strip():
            raise ArtifactError("a location must name the provider that resolves its locator")
        if not self.locator.strip():
            raise ArtifactError("a location must carry a locator the provider can resolve")

    def as_record(self) -> dict[str, str]:
        record = {"provider": self.provider, "locator": self.locator}
        if self.revision:
            record["revision"] = self.revision
        return record

    def __str__(self) -> str:
        return f"{self.provider}:{self.locator}"


# ----------------------------------------------------------------------------------- authority


#: The authority token meaning "no owner was derived". Distinct from the empty string so that
#: "nobody asked" and "asked, and the answer was nobody" are different states in a record.
AUTHORITY_UNRESOLVED = "UNRESOLVED"


@dataclass(frozen=True, order=True)
class Authority:
    """Who owns an artifact, and the derivation step that said so.

    CARRIED, NEVER DERIVED HERE. The Ω-2 chain in ``engine/universal_discovery/authority.py`` is a
    repository-specific derivation with seven rules; a bucket provider will have a different chain
    and a registry provider a different one again. This model records the ANSWER and the RULE that
    produced it, so an authority is always auditable, and stays silent about how to compute one.
    """

    owner: str = AUTHORITY_UNRESOLVED
    rule: str = ""

    @property
    def resolved(self) -> bool:
        return bool(self.owner) and self.owner != AUTHORITY_UNRESOLVED

    def as_record(self) -> dict[str, str]:
        return {"owner": self.owner, "rule": self.rule}


# -------------------------------------------------------------------------------- relationships


#: Relationship kinds Phase 1 needs a word for. OPEN, like every other vocabulary here: a
#: relationship kind is a string, so lineage, provenance and derivation edges need no edit.
CONTAINS = "CONTAINS"
DEPENDS_ON = "DEPENDS_ON"
DERIVED_FROM = "DERIVED_FROM"
DESCRIBES = "DESCRIBES"


@dataclass(frozen=True, order=True)
class Relationship:
    """A typed edge from this artifact to another artifact's identifier.

    TARGETS AN IDENTIFIER, NOT A PATH, and that is what lets an edge cross a provider boundary: a
    document in a bucket can describe a module in a git repository only if the edge names something
    neither provider owns exclusively.
    """

    kind: str
    target: str

    def __post_init__(self) -> None:
        if not self.kind.strip():
            raise ArtifactError("a relationship must declare its kind")
        if not self.target.strip():
            raise ArtifactError("a relationship must name the identifier it points at")

    def as_record(self) -> dict[str, str]:
        return {"kind": self.kind, "target": self.target}


# ------------------------------------------------------------------------------------- artifact


@dataclass(frozen=True)
class Artifact:
    """One discovered thing, of any type, from any provider, in any knowledge space.

    NO LANGUAGE-SPECIFIC LOGIC LIVES HERE. There is no method that parses, no field that counts a
    statement and no branch that tests ``type is PYTHON``. A Python analyser produces those numbers
    and attaches them through ``metadata``; this class would be unchanged if Python were removed
    from the repository entirely, which is the test of whether the abstraction is real.
    """

    identifier: str
    location: Location
    artifact_type: ArtifactType = UNKNOWN
    authority: Authority = field(default_factory=Authority)
    metadata: Mapping[str, str] = field(default_factory=dict)
    relationships: tuple[Relationship, ...] = ()
    #: Which classifier in the pipeline produced ``artifact_type``, so a type is auditable rather
    #: than asserted. Empty until the classification layer has run.
    classification_rule: str = ""

    def __post_init__(self) -> None:
        if not self.identifier.strip():
            raise ArtifactError(
                "an artifact with no identifier cannot be joined, deduplicated or reported on, "
                "so an empty identifier is a fault rather than a default"
            )
        object.__setattr__(self, "metadata", dict(sorted(self.metadata.items())))
        object.__setattr__(self, "relationships", tuple(sorted(self.relationships)))

    # ------------------------------------------------------------------ derived, non-mutating

    def with_type(self, artifact_type: ArtifactType, rule: str) -> Artifact:
        """A copy carrying a classification. The rule is REQUIRED, so a type is always auditable."""
        if not rule.strip():
            raise ArtifactError(
                f"classifying {self.identifier!r} as {artifact_type.name} without naming the rule "
                "would make the type unauditable, which is the defect Ω-5 exists to end"
            )
        return self._replace(artifact_type=artifact_type, classification_rule=rule)

    def with_authority(self, authority: Authority) -> Artifact:
        return self._replace(authority=authority)

    def with_metadata(self, **facts: str) -> Artifact:
        return self._replace(metadata={**self.metadata, **facts})

    def with_relationships(self, *edges: Relationship) -> Artifact:
        return self._replace(relationships=(*self.relationships, *edges))

    def _replace(self, **changes: object) -> Artifact:
        """One construction point for every derived copy, so no field is dropped by omission."""
        current: dict[str, object] = {
            "identifier": self.identifier,
            "location": self.location,
            "artifact_type": self.artifact_type,
            "authority": self.authority,
            "metadata": self.metadata,
            "relationships": self.relationships,
            "classification_rule": self.classification_rule,
        }
        current.update(changes)
        return Artifact(**current)  # type: ignore[arg-type]

    # ------------------------------------------------------------------------------ reporting

    @property
    def typed(self) -> bool:
        """Whether a classifier resolved this artifact to something other than UNKNOWN."""
        return self.artifact_type != UNKNOWN

    def related(self, kind: str) -> tuple[str, ...]:
        return tuple(edge.target for edge in self.relationships if edge.kind == kind)

    def as_record(self) -> dict[str, object]:
        """A deterministic record. Sorted throughout, so two equal artifacts serialise equally."""
        return {
            "identifier": self.identifier,
            "location": self.location.as_record(),
            "type": self.artifact_type.name,
            "classification_rule": self.classification_rule,
            "authority": self.authority.as_record(),
            "metadata": dict(sorted(self.metadata.items())),
            "relationships": [edge.as_record() for edge in self.relationships],
        }
