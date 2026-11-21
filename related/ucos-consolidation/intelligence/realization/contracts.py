"""URI-000001 — the value types of the realization pipeline.

Every type here is frozen, slotted, wall-clock free, and **content-addressed**: its
``seal`` is the canonical hash of its own core, so a downstream stage can prove which
upstream state it was derived from, and any post-hoc mutation is detectable.

The chain of seals *is* the traceability spine::

    knowledge_seal → plan.seal → composition.seal → manifest.seal → record.seal

Nothing in this module performs I/O, reads a clock, or holds authority.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from intelligence.realization.canonical import content_hash, sha256_text, short_seal
from intelligence.realization.errors import PlanningError

#: Versioned identity of the realization contract surface (AR-03 / PL-05).
REALIZATION_CONTRACT_NAME = "intelligence.realization"
REALIZATION_CONTRACT_VERSION = "1.0.0"

#: Every artifact records that it derives its content from canonical knowledge and
#: carries no authority of its own.
DERIVED_AUTHORITY = "NONE (derived from canonical knowledge)"


class RealizationStage(str, Enum):
    """The ordered stages of the realization pipeline."""

    INTAKE = "intake"
    PLANNING = "planning"
    COMPOSITION = "composition"
    GENERATION = "generation"
    IMPLEMENTATION = "implementation"
    GOVERNANCE = "governance"
    TRACEABILITY = "traceability"
    EVIDENCE = "evidence"


class ArtifactFamily(str, Enum):
    """The seven artifact families a realization target is realized into.

    OPEN BY REGISTRATION (LYR-L14/IF-08 — "Future Interface"). The seven members are the
    families this substrate ships generators for. Adding another was once a code edit to
    this enum, which is exactly what "Future Interface" promises it will not be; the set
    of *families* is therefore open the same way every other open set in this repository is
    open — a new one is registered, not compiled in. See :func:`register_family`.
    """

    ARCHITECTURE = "architecture"
    API = "api"
    SCHEMA = "schema"
    RUNTIME = "runtime"
    TEST = "test"
    DOCUMENTATION = "documentation"
    DEPLOYMENT = "deployment"

    @classmethod
    def coerce(cls, value: Any) -> ArtifactFamily:
        """Return the member for ``value`` or fail loudly (no silent defaulting)."""
        try:
            return cls(str(value))
        except ValueError as exc:
            # A registered family is reachable by its value before this is called; if it
            # is not a member and not registered, nothing admits it and the refusal stands.
            registered = _REGISTERED_FAMILIES.get(str(value))
            if registered is not None:
                return registered
            raise PlanningError("unknown artifact family", value=value) from exc


#: Families admitted since the substrate was sealed, keyed by value. A registration is an
#: append-only act: an existing value is never overwritten, so a shipped family cannot be
#: redefined and a registered one cannot be shadowed.
_REGISTERED_FAMILIES: dict[str, ArtifactFamily] = {}


def register_family(value: str, *, name: str = "") -> ArtifactFamily:
    """Admit a new artifact family by registration rather than by editing the enum.

    This is the mechanism LYR-L14/IF-08 asks for: "Future Interface" is satisfied by
    registration, the same way metatypes, context kinds, lifecycle stages and capability
    categories are. A family is registered once; a duplicate value is refused rather than
    silently re-bound, and a value the enum already ships is refused rather than shadowed.

    Registration does not create a generator. A registered family still needs a generator
    bound in :func:`intelligence.realization.generators.register_generator`, and the
    registry's own completeness check refuses a family with no generator. So admitting a
    family is open, and realizing it is governed — the two are separate acts on purpose.
    """
    key = str(value)
    if not key:
        raise PlanningError("an artifact family value cannot be empty")
    try:
        existing = ArtifactFamily(key)
    except ValueError:
        existing = None
    if existing is not None:
        raise PlanningError("artifact family is already shipped by the substrate", value=key)
    if key in _REGISTERED_FAMILIES:
        raise PlanningError(
            "artifact family is already registered",
            value=key,
            registered_as=_REGISTERED_FAMILIES[key].name,
        )
    family = _make_family(key, name or key)
    _REGISTERED_FAMILIES[key] = family
    return family


def registered_families() -> tuple[ArtifactFamily, ...]:
    """Every family admitted by registration since the substrate was sealed."""
    return tuple(_REGISTERED_FAMILIES[k] for k in sorted(_REGISTERED_FAMILIES))


def _make_family(value: str, name: str) -> ArtifactFamily:
    """Construct an ArtifactFamily instance for a registered value.

    ``ArtifactFamily`` subclasses ``str``, so a plain ``__new__`` runs the enum's own value
    validation and refuses anything it does not already know. Assigning ``_value_`` after
    construction is the documented way to create an instance whose value is not a declared
    member, and the caller has already established the value is admissible.
    """
    member = str.__new__(ArtifactFamily, value)
    member._name_ = name
    member._value_ = value
    return member


class MediaKind(str, Enum):
    """The concrete serialization of a generated artifact."""

    JSON = "json"
    MARKDOWN = "markdown"
    PYTHON = "python"
    SQL = "sql"
    YAML = "yaml"


#: The realization dependency order between families. Architecture is derived first
#: because every other family is expressed in terms of its components; tests and
#: documentation come last because they assert/describe everything before them.
FAMILY_DEPENDENCIES: Mapping[ArtifactFamily, tuple[ArtifactFamily, ...]] = {
    ArtifactFamily.ARCHITECTURE: (),
    ArtifactFamily.SCHEMA: (ArtifactFamily.ARCHITECTURE,),
    ArtifactFamily.API: (ArtifactFamily.ARCHITECTURE, ArtifactFamily.SCHEMA),
    ArtifactFamily.RUNTIME: (ArtifactFamily.ARCHITECTURE, ArtifactFamily.SCHEMA),
    ArtifactFamily.DEPLOYMENT: (ArtifactFamily.RUNTIME,),
    ArtifactFamily.TEST: (
        ArtifactFamily.ARCHITECTURE,
        ArtifactFamily.SCHEMA,
        ArtifactFamily.API,
        ArtifactFamily.RUNTIME,
        ArtifactFamily.DEPLOYMENT,
    ),
    ArtifactFamily.DOCUMENTATION: (
        ArtifactFamily.ARCHITECTURE,
        ArtifactFamily.SCHEMA,
        ArtifactFamily.API,
        ArtifactFamily.RUNTIME,
        ArtifactFamily.DEPLOYMENT,
        ArtifactFamily.TEST,
    ),
}

#: Deterministic realization order (a topological sort of FAMILY_DEPENDENCIES,
#: ties broken alphabetically so the order is stable across runs and machines).
FAMILY_ORDER: tuple[ArtifactFamily, ...] = (
    ArtifactFamily.ARCHITECTURE,
    ArtifactFamily.SCHEMA,
    ArtifactFamily.API,
    ArtifactFamily.RUNTIME,
    ArtifactFamily.DEPLOYMENT,
    ArtifactFamily.TEST,
    ArtifactFamily.DOCUMENTATION,
)


def family_order() -> tuple[ArtifactFamily, ...]:
    """FAMILY_ORDER extended by any registered families, in a stable order.

    A registered family declares no dependency edges (nothing depends on it and it depends
    on nothing), so it realizes after the shipped families and in the sorted order of its
    own value. The shipped order is untouched: a registration appends, exactly as an
    evolution appends.
    """
    registered = tuple(family for family in registered_families() if family not in FAMILY_ORDER)
    return FAMILY_ORDER + tuple(sorted(registered, key=lambda f: f.value))


def _seal(core: Mapping[str, Any]) -> str:
    """Seal a value type's core with the canonical content hash."""
    return content_hash(dict(core))


def slug(text: str) -> str:
    """Return a deterministic, filesystem-safe, lower-case slug for ``text``."""
    out = []
    prev_dash = False
    for char in str(text).strip().lower():
        if char.isalnum():
            out.append(char)
            prev_dash = False
        elif not prev_dash:
            out.append("-")
            prev_dash = True
    return "".join(out).strip("-") or "unnamed"


def identifier(text: str) -> str:
    """Return a deterministic, valid Python identifier fragment for ``text``."""
    body = slug(text).replace("-", "_")
    return body if body[0].isalpha() or body[0] == "_" else f"u_{body}"


@dataclass(frozen=True, slots=True)
class Invariant:
    """A normative canonical statement a realization must honour at runtime."""

    cko_id: str
    kind: str
    authority: str
    statement: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "cko_id": self.cko_id,
            "kind": self.kind,
            "authority": self.authority,
            "statement": self.statement,
        }


@dataclass(frozen=True, slots=True)
class RealizationTarget:
    """One coherent body of canonical knowledge to be realized (a knowledge universe).

    A target is *derived*, never declared: its membership, layers, and invariants are
    read out of the canonical store.
    """

    universe: str
    cko_ids: tuple[str, ...]
    decision_ids: tuple[str, ...]
    kinds: tuple[str, ...]
    authorities: tuple[str, ...]
    lifecycles: tuple[str, ...]
    owners: tuple[str, ...]
    invariants: tuple[Invariant, ...]
    principles: tuple[str, ...]
    patterns: tuple[str, ...]
    conventions: tuple[str, ...]
    anti_patterns: tuple[str, ...]
    edges: tuple[tuple[str, str, str], ...] = ()

    @property
    def target_id(self) -> str:
        """Deterministic identity: ``URI-TGT-<universe-slug>``."""
        return f"URI-TGT-{slug(self.universe).upper()}"

    @property
    def module_name(self) -> str:
        """The Python module-name fragment used by generated code."""
        return identifier(self.universe)

    @property
    def path_slug(self) -> str:
        """The filesystem fragment used by generated artifact paths."""
        return slug(self.universe)

    def _core(self) -> dict[str, Any]:
        return {
            "target_id": self.target_id,
            "universe": self.universe,
            "cko_ids": list(self.cko_ids),
            "decision_ids": list(self.decision_ids),
            "kinds": list(self.kinds),
            "authorities": list(self.authorities),
            "lifecycles": list(self.lifecycles),
            "owners": list(self.owners),
            "invariants": [i.to_dict() for i in self.invariants],
            "principles": list(self.principles),
            "patterns": list(self.patterns),
            "conventions": list(self.conventions),
            "anti_patterns": list(self.anti_patterns),
            "edges": [list(e) for e in self.edges],
        }

    @property
    def seal(self) -> str:
        return _seal(self._core())

    def to_dict(self) -> dict[str, Any]:
        payload = self._core()
        payload["seal"] = self.seal
        return payload


@dataclass(frozen=True, slots=True)
class PlanStep:
    """One unit of realization work: realize ``target`` into ``family``."""

    step_id: str
    target_id: str
    universe: str
    family: ArtifactFamily
    depends_on: tuple[str, ...]
    source_ckos: tuple[str, ...]
    wave: int

    def _core(self) -> dict[str, Any]:
        return {
            "step_id": self.step_id,
            "target_id": self.target_id,
            "universe": self.universe,
            "family": self.family.value,
            "depends_on": list(self.depends_on),
            "source_ckos": list(self.source_ckos),
            "wave": self.wave,
        }

    @property
    def seal(self) -> str:
        return _seal(self._core())

    def to_dict(self) -> dict[str, Any]:
        payload = self._core()
        payload["seal"] = self.seal
        return payload


@dataclass(frozen=True, slots=True)
class RealizationPlan:
    """The full, ordered, acyclic plan derived from a sealed canonical knowledge state."""

    knowledge_seal: str
    targets: tuple[RealizationTarget, ...]
    steps: tuple[PlanStep, ...]
    waves: tuple[tuple[str, ...], ...]
    coverage_gaps: tuple[str, ...] = ()

    @property
    def plan_id(self) -> str:
        """Deterministic identity derived from the plan's own content."""
        return f"URI-PLAN-{short_seal(self.seal)}"

    def step(self, step_id: str) -> PlanStep:
        for candidate in self.steps:
            if candidate.step_id == step_id:
                return candidate
        raise PlanningError("unknown plan step", step_id=step_id)

    def target(self, target_id: str) -> RealizationTarget:
        for candidate in self.targets:
            if candidate.target_id == target_id:
                return candidate
        raise PlanningError("unknown realization target", target_id=target_id)

    def steps_for(self, target_id: str) -> tuple[PlanStep, ...]:
        return tuple(s for s in self.steps if s.target_id == target_id)

    def _core(self) -> dict[str, Any]:
        return {
            "knowledge_seal": self.knowledge_seal,
            "targets": [t.to_dict() for t in self.targets],
            "steps": [s.to_dict() for s in self.steps],
            "waves": [list(w) for w in self.waves],
            "coverage_gaps": list(self.coverage_gaps),
        }

    @property
    def seal(self) -> str:
        return _seal(self._core())

    def to_dict(self) -> dict[str, Any]:
        payload = self._core()
        payload["plan_id"] = self.plan_id
        payload["step_count"] = len(self.steps)
        payload["target_count"] = len(self.targets)
        payload["seal"] = self.seal
        return payload


@dataclass(frozen=True, slots=True)
class CompositionUnit:
    """A plan step bound to the exact canonical objects and upstream units it consumes."""

    unit_id: str
    step_id: str
    target_id: str
    universe: str
    family: ArtifactFamily
    bound_ckos: tuple[str, ...]
    bound_decisions: tuple[str, ...]
    upstream_units: tuple[str, ...]
    consumed_families: tuple[str, ...]

    def _core(self) -> dict[str, Any]:
        return {
            "unit_id": self.unit_id,
            "step_id": self.step_id,
            "target_id": self.target_id,
            "universe": self.universe,
            "family": self.family.value,
            "bound_ckos": list(self.bound_ckos),
            "bound_decisions": list(self.bound_decisions),
            "upstream_units": list(self.upstream_units),
            "consumed_families": list(self.consumed_families),
        }

    @property
    def seal(self) -> str:
        return _seal(self._core())

    def to_dict(self) -> dict[str, Any]:
        payload = self._core()
        payload["seal"] = self.seal
        return payload


@dataclass(frozen=True, slots=True)
class RealizationComposition:
    """The composed, topologically ordered realization graph ready for generation."""

    plan_id: str
    plan_seal: str
    knowledge_seal: str
    units: tuple[CompositionUnit, ...]
    order: tuple[str, ...]
    conflicts: tuple[tuple[str, str], ...] = ()

    @property
    def composition_id(self) -> str:
        return f"URI-COMP-{short_seal(self.seal)}"

    def unit(self, unit_id: str) -> CompositionUnit:
        for candidate in self.units:
            if candidate.unit_id == unit_id:
                return candidate
        raise PlanningError("unknown composition unit", unit_id=unit_id)

    def ordered_units(self) -> tuple[CompositionUnit, ...]:
        by_id = {u.unit_id: u for u in self.units}
        return tuple(by_id[uid] for uid in self.order)

    def _core(self) -> dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "plan_seal": self.plan_seal,
            "knowledge_seal": self.knowledge_seal,
            "units": [u.to_dict() for u in self.units],
            "order": list(self.order),
            "conflicts": [list(c) for c in self.conflicts],
        }

    @property
    def seal(self) -> str:
        return _seal(self._core())

    def to_dict(self) -> dict[str, Any]:
        payload = self._core()
        payload["composition_id"] = self.composition_id
        payload["unit_count"] = len(self.units)
        payload["seal"] = self.seal
        return payload


@dataclass(frozen=True, slots=True)
class Provenance:
    """The traceability block every generated artifact carries in its own body."""

    generator: str
    generator_version: str
    capability: str
    plan_id: str
    step_id: str
    unit_id: str
    target_id: str
    knowledge_seal: str
    source_ckos: tuple[str, ...]
    source_decisions: tuple[str, ...] = ()
    authority: str = DERIVED_AUTHORITY

    def to_dict(self) -> dict[str, Any]:
        return {
            "authority": self.authority,
            "capability": self.capability,
            "generator": self.generator,
            "generator_version": self.generator_version,
            "knowledge_seal": self.knowledge_seal,
            "plan_id": self.plan_id,
            "source_ckos": list(self.source_ckos),
            "source_decisions": list(self.source_decisions),
            "step_id": self.step_id,
            "target_id": self.target_id,
            "unit_id": self.unit_id,
        }


@dataclass(frozen=True, slots=True)
class GeneratedArtifact:
    """A fully generated artifact held in memory. Generation never touches disk."""

    relative_path: str
    family: ArtifactFamily
    media: MediaKind
    content: str
    provenance: Provenance

    @property
    def content_sha256(self) -> str:
        return sha256_text(self.content)

    @property
    def artifact_id(self) -> str:
        return f"URI-ART-{short_seal(self.content_sha256, width=16)}"

    @property
    def size(self) -> int:
        return len(self.content.encode("utf-8"))

    def to_record(self) -> dict[str, Any]:
        """The manifest record for this artifact (content excluded; hash included)."""
        return {
            "artifact_id": self.artifact_id,
            "relative_path": self.relative_path,
            "family": self.family.value,
            "media": self.media.value,
            "content_sha256": self.content_sha256,
            "size": self.size,
            "provenance": self.provenance.to_dict(),
        }


@dataclass(frozen=True, slots=True)
class GenerationManifest:
    """The sealed inventory of everything a generation run produced."""

    composition_id: str
    composition_seal: str
    plan_id: str
    knowledge_seal: str
    artifacts: tuple[GeneratedArtifact, ...]

    @property
    def generation_id(self) -> str:
        return f"URI-GEN-{short_seal(self.seal)}"

    def by_family(self) -> dict[str, tuple[str, ...]]:
        grouped: dict[str, list[str]] = {}
        for art in self.artifacts:
            grouped.setdefault(art.family.value, []).append(art.relative_path)
        return {k: tuple(sorted(v)) for k, v in sorted(grouped.items())}

    def paths(self) -> tuple[str, ...]:
        return tuple(sorted(a.relative_path for a in self.artifacts))

    def _core(self) -> dict[str, Any]:
        return {
            "composition_id": self.composition_id,
            "composition_seal": self.composition_seal,
            "plan_id": self.plan_id,
            "knowledge_seal": self.knowledge_seal,
            "artifacts": [a.to_record() for a in self.artifacts],
        }

    @property
    def seal(self) -> str:
        return _seal(self._core())

    def to_dict(self) -> dict[str, Any]:
        payload = self._core()
        payload["generation_id"] = self.generation_id
        payload["artifact_count"] = len(self.artifacts)
        payload["families"] = {k: list(v) for k, v in self.by_family().items()}
        payload["seal"] = self.seal
        return payload


@dataclass(frozen=True, slots=True)
class MaterializedFile:
    """The outcome of materializing one generated artifact onto a writable surface."""

    relative_path: str
    artifact_id: str
    content_sha256: str
    size: int
    action: str

    def to_canonical_dict(self) -> dict[str, Any]:
        """What the file IS. A pure function of the generated artifact.

        ``action`` is deliberately absent. It records what THIS execution did to the
        filesystem — ``created`` on a clone that did not have the file, ``unchanged``
        on the next pass — so it is an observation of one run, not a property of the
        artifact. UAKOS-CLOSURE-008 settled that an execution transcript is evidence
        and never identity; this is the same fact for a materialization pass.
        """
        return {
            "relative_path": self.relative_path,
            "artifact_id": self.artifact_id,
            "content_sha256": self.content_sha256,
            "size": self.size,
        }

    def to_dict(self) -> dict[str, Any]:
        """The canonical facts plus the per-run observation, for evidence and logs."""
        return {**self.to_canonical_dict(), "action": self.action}


@dataclass(frozen=True, slots=True)
class ImplementationRecord:
    """The sealed record of a materialization pass (or a dry run that wrote nothing)."""

    generation_id: str
    generation_seal: str
    knowledge_seal: str
    artifact_root: str
    files: tuple[MaterializedFile, ...]
    dry_run: bool
    verified: bool

    @property
    def implementation_id(self) -> str:
        return f"URI-IMP-{short_seal(self.seal)}"

    def actions(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for item in self.files:
            counts[item.action] = counts.get(item.action, 0) + 1
        return dict(sorted(counts.items()))

    def _core(self) -> dict[str, Any]:
        """The sealed core. Canonical file facts only.

        The per-file ``action`` is excluded so that the seal — and therefore
        ``implementation_id`` — is a function of WHAT WAS MATERIALIZED and not of
        what the filesystem happened to hold beforehand. While ``action`` was sealed
        here, a pristine clone reported ``created`` and every later pass reported
        ``unchanged``, so the same canonical knowledge produced two different
        implementation identities and the manifest had no fixed point.
        """
        return {
            "generation_id": self.generation_id,
            "generation_seal": self.generation_seal,
            "knowledge_seal": self.knowledge_seal,
            "artifact_root": self.artifact_root,
            "files": [f.to_canonical_dict() for f in self.files],
            "dry_run": self.dry_run,
            "verified": self.verified,
        }

    @property
    def seal(self) -> str:
        return _seal(self._core())

    def to_canonical_dict(self) -> dict[str, Any]:
        """The record as repository truth — no per-run observation. Written to the manifest."""
        payload = self._core()
        payload["implementation_id"] = self.implementation_id
        payload["file_count"] = len(self.files)
        payload["seal"] = self.seal
        return payload

    def to_dict(self) -> dict[str, Any]:
        """The canonical record plus this run's observations, for evidence and logs."""
        payload = self.to_canonical_dict()
        payload["files"] = [f.to_dict() for f in self.files]
        payload["actions"] = self.actions()
        return payload


@dataclass(frozen=True, slots=True)
class TraceEdge:
    """One directed traceability edge in the realization spine."""

    source: str
    relation: str
    target: str
    stage: RealizationStage = RealizationStage.TRACEABILITY

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "relation": self.relation,
            "target": self.target,
            "stage": self.stage.value,
        }


@dataclass(frozen=True, slots=True)
class Envelope:
    """The common, deterministic header every URI output document carries."""

    artifact_id: str
    title: str
    document_format: str
    knowledge_seal: str
    extra: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "artifact_id": self.artifact_id,
            "title": self.title,
            "document_format": self.document_format,
            "producer": (
                f"{REALIZATION_CONTRACT_NAME} v{REALIZATION_CONTRACT_VERSION} "
                "(URI-000001 Universal Realization Intelligence)"
            ),
            "authority": DERIVED_AUTHORITY,
            "capability": "URI-000001",
            "knowledge_seal": self.knowledge_seal,
        }
        payload.update(dict(self.extra))
        return payload


def dedupe(values: Iterable[str]) -> tuple[str, ...]:
    """Return ``values`` de-duplicated and sorted (deterministic set semantics)."""
    return tuple(sorted(set(values)))


__all__ = [
    "DERIVED_AUTHORITY",
    "FAMILY_DEPENDENCIES",
    "FAMILY_ORDER",
    "REALIZATION_CONTRACT_NAME",
    "REALIZATION_CONTRACT_VERSION",
    "ArtifactFamily",
    "CompositionUnit",
    "Envelope",
    "GeneratedArtifact",
    "GenerationManifest",
    "ImplementationRecord",
    "Invariant",
    "MaterializedFile",
    "MediaKind",
    "PlanStep",
    "Provenance",
    "RealizationComposition",
    "RealizationPlan",
    "RealizationStage",
    "RealizationTarget",
    "TraceEdge",
    "dedupe",
    "identifier",
    "slug",
]
