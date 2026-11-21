"""UCOS-UNG-001 — Ω Nucleus generation vocabulary & contracts.

The deterministic vocabulary in which a **generation** is expressed, for any Ω Nucleus and any
artifact — never for one nucleus, one language, or one repository layout.

The separation this vocabulary makes structural:

    * a **target** is a declared obligation ("every nucleus has a contract surface"),
    * a **template** is the one authority that renders that obligation from a declaration,
    * an **artifact** is the rendered result, content-addressed and bound to a destination,
    * a **plan** is the complete artifact set for one nucleus, and nothing more.

A plan is a *determination*, not an act. The generator renders; it never writes. Materialising
a plan into Repository Truth is a constituent act performed by whatever authority governs that
Truth, exactly as measuring freeze readiness is separate from freezing. This is why no module
in this package performs a filesystem write, and why the generator can declare — truthfully,
and provably against its own source — that it emits no tracked artifact.

Every identity is content-addressed from inputs alone and holds no wall-clock, so the same
declaration always yields byte-identical artifacts with the same identities. That is what makes
a generated artifact re-derivable rather than merely reproducible-in-principle.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from enum import Enum
from platform.foundation.contracts import ContractRef, content_hash
from platform.universal_generator.errors import GenerationPlanError, GenerationTargetError
from typing import Any

#: The canonical identity of the Universal Ω Nucleus Generator instance.
UNG_ID = "UCOS-UNG-001"

#: The semantic version of the generation contract surface.
GENERATION_CONTRACT_VERSION = "1.0.0"


class ArtifactKind(str, Enum):
    """What an artifact *is*, independently of what language or format carries it.

    The set is closed because it is the constitutional shape of a nucleus, not a file-type
    list: every entry answers an obligation the Foundation Constitution already places on a
    registered capability. A new file format is a new template, never a new kind.
    """

    #: The register entry through which the nucleus enters constitutional authority.
    CONSTITUTIONAL = "constitutional"
    #: The published, semantically versioned contract surface a consumer binds to.
    CONTRACT = "contract"
    #: The typed error taxonomy through which the nucleus refuses.
    ERRORS = "errors"
    #: The deterministic, fail-closed registry holding the nucleus's population.
    REGISTRY = "registry"
    #: The declared bootstrap and service registration — the runtime wiring.
    BOOTSTRAP = "bootstrap"
    #: The one-command runtime surface.
    RUNTIME = "runtime"
    #: The declared policy document that configures the nucleus.
    POLICY = "policy"
    #: The documentation of record, derived from the declaration.
    DOCUMENTATION = "documentation"
    #: The executable obligations that ship with the nucleus.
    TESTS = "tests"
    #: The build wiring that publishes the runtime surface.
    BUILD = "build"

    @classmethod
    def coerce(cls, value: Any, *, subject: str = "artifact kind") -> ArtifactKind:
        """Coerce ``value`` to a kind, failing closed (never silently)."""
        if isinstance(value, cls):
            return value
        if isinstance(value, str):
            try:
                return cls(value)
            except ValueError as exc:
                raise GenerationTargetError(
                    "unknown artifact kind", subject=subject, value=value
                ) from exc
        raise GenerationTargetError("artifact kind must be a string", subject=subject)


@dataclass(frozen=True, slots=True)
class GenerationTarget:
    """One declared obligation the generator discharges for every nucleus."""

    target_id: str
    kind: ArtifactKind
    template: str
    destination: str
    rationale: str = ""

    @classmethod
    def from_document(cls, payload: Mapping[str, Any]) -> GenerationTarget:
        """Build a validated target declaration (fail-closed)."""
        if not isinstance(payload, Mapping):
            raise GenerationTargetError("generation target must be a mapping")
        required = ("target_id", "kind", "template", "destination")
        missing = [key for key in required if key not in payload]
        if missing:
            raise GenerationTargetError(
                "generation target is incomplete",
                target_id=str(payload.get("target_id", "")),
                missing=",".join(missing),
            )
        target_id = str(payload["target_id"]).strip()
        template = str(payload["template"]).strip()
        destination = str(payload["destination"]).strip()
        if not target_id or not template or not destination:
            raise GenerationTargetError(
                "generation target requires an identity, a template and a destination",
                target_id=target_id,
            )
        return cls(
            target_id=target_id,
            kind=ArtifactKind.coerce(payload["kind"], subject=target_id),
            template=template,
            destination=destination,
            rationale=str(payload.get("rationale", "")),
        )

    def to_dict(self) -> dict[str, Any]:
        """A JSON-serialisable projection of this target."""
        return {
            "target_id": self.target_id,
            "kind": self.kind.value,
            "template": self.template,
            "destination": self.destination,
            "rationale": self.rationale,
        }


@dataclass(frozen=True, slots=True)
class GeneratedArtifact:
    """One rendered artifact: what it is, where it belongs, and exactly what it says."""

    target_id: str
    kind: ArtifactKind
    destination: str
    content: str
    artifact_id: str = ""

    @classmethod
    def create(cls, target: GenerationTarget, destination: str, content: str) -> GeneratedArtifact:
        """Build a content-addressed artifact.

        The identity covers the destination as well as the content, because the same bytes at
        two destinations are two artifacts, and conflating them would let a plan silently
        relocate an artifact without its identity changing.
        """
        core = {
            "target_id": target.target_id,
            "kind": target.kind.value,
            "destination": destination,
            "content": content,
        }
        return cls(
            target_id=target.target_id,
            kind=target.kind,
            destination=destination,
            content=content,
            artifact_id=f"UCOS-UNGA-{content_hash(core)[:16]}",
        )

    @property
    def digest(self) -> str:
        """The content hash of this artifact's bytes alone, independent of where it lands."""
        return content_hash({"content": self.content})

    @property
    def line_count(self) -> int:
        """How many lines this artifact carries."""
        return len(self.content.splitlines())

    def to_dict(self) -> dict[str, Any]:
        """A JSON-serialisable projection of this artifact, content included."""
        return {
            "artifact_id": self.artifact_id,
            "target_id": self.target_id,
            "kind": self.kind.value,
            "destination": self.destination,
            "digest": self.digest,
            "line_count": self.line_count,
            "content": self.content,
        }

    def summary(self) -> dict[str, Any]:
        """A compact projection: everything except the rendered bytes."""
        return {
            "artifact_id": self.artifact_id,
            "target_id": self.target_id,
            "kind": self.kind.value,
            "destination": self.destination,
            "digest": self.digest,
            "line_count": self.line_count,
        }


@dataclass(frozen=True, slots=True)
class GenerationPlan:
    """The complete artifact set for one Ω Nucleus — a determination, never an act."""

    nucleus_id: str
    artifacts: tuple[GeneratedArtifact, ...]
    plan_id: str = ""

    @classmethod
    def create(cls, nucleus_id: str, artifacts: Iterable[GeneratedArtifact]) -> GenerationPlan:
        """Build a content-addressed plan, refusing a destination collision (fail-closed)."""
        ordered = tuple(sorted(artifacts, key=lambda item: item.destination))
        if not ordered:
            raise GenerationPlanError("generation plan is empty", nucleus_id=nucleus_id)
        seen: dict[str, str] = {}
        for artifact in ordered:
            first = seen.get(artifact.destination)
            if first is not None:
                raise GenerationPlanError(
                    "two targets render to one destination",
                    nucleus_id=nucleus_id,
                    destination=artifact.destination,
                    targets=f"{first},{artifact.target_id}",
                )
            seen[artifact.destination] = artifact.target_id
        core = {
            "nucleus_id": nucleus_id,
            "artifacts": [item.artifact_id for item in ordered],
        }
        return cls(
            nucleus_id=nucleus_id,
            artifacts=ordered,
            plan_id=f"UCOS-UNGP-{content_hash(core)[:16]}",
        )

    @property
    def total(self) -> int:
        """How many artifacts this plan determines."""
        return len(self.artifacts)

    def kinds(self) -> tuple[str, ...]:
        """Every artifact kind this plan covers, in canonical order."""
        return tuple(sorted({item.kind.value for item in self.artifacts}))

    def by_kind(self, kind: ArtifactKind | str) -> tuple[GeneratedArtifact, ...]:
        """Every artifact of ``kind``, in destination order."""
        resolved = ArtifactKind.coerce(kind)
        return tuple(item for item in self.artifacts if item.kind is resolved)

    def destinations(self) -> tuple[str, ...]:
        """Every destination this plan would occupy, in canonical order."""
        return tuple(item.destination for item in self.artifacts)

    def require(self, target_id: str) -> GeneratedArtifact:
        """The artifact rendered for ``target_id``; raises when absent (fail-closed)."""
        for artifact in self.artifacts:
            if artifact.target_id == target_id:
                return artifact
        raise GenerationPlanError(
            "plan holds no artifact for this target",
            nucleus_id=self.nucleus_id,
            target_id=target_id,
        )

    def to_dict(self) -> dict[str, Any]:
        """A JSON-serialisable projection of this plan, rendered content included."""
        return {
            "plan_id": self.plan_id,
            "nucleus_id": self.nucleus_id,
            "total": self.total,
            "kinds": list(self.kinds()),
            "artifacts": [item.to_dict() for item in self.artifacts],
        }

    def summary(self) -> dict[str, Any]:
        """A compact projection: what would be written where, without the bytes."""
        return {
            "plan_id": self.plan_id,
            "nucleus_id": self.nucleus_id,
            "total": self.total,
            "kinds": list(self.kinds()),
            "artifacts": [item.summary() for item in self.artifacts],
        }

    def fingerprint(self) -> str:
        """The deterministic content fingerprint of this plan."""
        return content_hash(self.to_dict())


_CONTRACT_NAMES: tuple[tuple[str, str], ...] = (
    ("generation.nucleus.plan", "Determine the complete artifact set for one Ω Nucleus."),
    ("generation.nucleus.targets", "The declared obligations every nucleus generation covers."),
    ("generation.nucleus.templates", "The registered authorities that render each obligation."),
)

#: The versioned published contract surface of the Ω Nucleus generator.
GENERATION_CONTRACTS: tuple[ContractRef, ...] = tuple(
    ContractRef(name, GENERATION_CONTRACT_VERSION) for name, _ in _CONTRACT_NAMES
)


def generation_contract_names() -> tuple[str, ...]:
    """The published generation contract names, in declaration order."""
    return tuple(name for name, _ in _CONTRACT_NAMES)


__all__ = [
    "UNG_ID",
    "GENERATION_CONTRACTS",
    "GENERATION_CONTRACT_VERSION",
    "ArtifactKind",
    "GeneratedArtifact",
    "GenerationPlan",
    "GenerationTarget",
    "generation_contract_names",
]
