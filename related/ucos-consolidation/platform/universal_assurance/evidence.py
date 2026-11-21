"""UCOS-EPIC-014 — Evidence Collection (Terminal T7).

The fourth owned capability, and the spine of the other nine. **Evidence Collection**
accumulates one content-addressed :class:`EvidenceArtifact` per stage contribution,
assembles them into an immutable :class:`EvidenceBundle` with a self-verifying
:meth:`EvidenceBundle.manifest`, and — when asked — writes the bundle to disk
deterministically.

*Which* artifacts must exist is **declared by the policy**, not by this module: an
artifact is required because ``evidence.artifacts`` says so. A required artifact that no
stage contributed is recorded as **missing** and is a blocking shortfall (Mandatory Rule 6
— every determination yields evidence). An artifact a stage contributes that the policy
never declared is recorded as **undeclared** and counted, so policy and pipeline can never
drift apart silently in either direction.

Although Evidence Collection sits fourth in the mission's stage order, it *spans* the run:
stages keep contributing to the same collector and the evidence stage record is finalized
last, once every contribution is in. The report still presents it in canonical stage
order.

Writing is guarded and deterministic:

    * **Write scope.** The policy's ``evidence.forbidden_write_prefixes`` are enforced
      before a single byte is written, so evidence collection can never write into the
      read-only certified corpus (DP-03 / C-01).
    * **Byte stability.** Every file is ``json.dumps(..., indent=2, sort_keys=True)`` plus a
      trailing newline, so re-writing an identical bundle produces identical bytes.
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from platform.foundation.contracts import content_hash
from platform.universal_assurance.contracts import AssuranceStage
from platform.universal_assurance.errors import AssuranceEvidenceError
from platform.universal_assurance.policy import AssurancePolicy
from typing import Any

#: The evidence bundle / manifest format identifiers.
EVIDENCE_BUNDLE_FORMAT = "ucos-assurance-evidence-bundle/1.0.0"
EVIDENCE_MANIFEST_FORMAT = "ucos-assurance-evidence-manifest/1.0.0"

#: The manifest file name written alongside the artifacts.
MANIFEST_FILENAME = "MANIFEST.json"

#: The artifact id recorded for a contribution the policy never declared.
UNDECLARED_ARTIFACT_PREFIX = "UNDECLARED"


@dataclass(frozen=True, slots=True)
class EvidenceArtifact:
    """One content-addressed evidence artifact contributed by a stage."""

    artifact_id: str
    stage: AssuranceStage
    name: str
    declared: bool
    content_sha256: str
    payload: Mapping[str, Any]

    @classmethod
    def create(
        cls,
        *,
        artifact_id: str,
        stage: AssuranceStage,
        name: str,
        payload: Mapping[str, Any],
        declared: bool = True,
    ) -> EvidenceArtifact:
        """Content-address ``payload`` and bind it to the artifact it discharges."""
        if not isinstance(payload, Mapping):
            raise AssuranceEvidenceError(
                "an evidence artifact payload must be a mapping",
                artifact=artifact_id,
                stage=stage.value,
            )
        return cls(
            artifact_id=artifact_id,
            stage=stage,
            name=name,
            declared=declared,
            content_sha256=content_hash(payload),
            payload=dict(payload),
        )

    def recompute(self) -> str:
        """Recompute the content hash from the current payload."""
        return content_hash(self.payload)

    @property
    def intact(self) -> bool:
        """True iff the recorded digest matches a recomputation of the payload."""
        return self.recompute() == self.content_sha256

    @property
    def filename(self) -> str:
        return f"{self.name}.json"

    def core(self) -> dict[str, Any]:
        """The canonical, hashable core (the digest stands in for the payload)."""
        return {
            "artifact_id": self.artifact_id,
            "stage": self.stage.value,
            "name": self.name,
            "declared": self.declared,
            "content_sha256": self.content_sha256,
        }

    def to_dict(self) -> dict[str, Any]:
        return {**self.core(), "filename": self.filename}


@dataclass(frozen=True, slots=True)
class EvidenceBundle:
    """An immutable, content-addressed bundle of every artifact an assurance run produced."""

    evidence_id: str
    subject_id: str
    policy_id: str
    policy_digest: str
    artifacts: tuple[EvidenceArtifact, ...]
    required_ids: tuple[str, ...]
    bundle_sha256: str

    @staticmethod
    def _core(
        *,
        subject_id: str,
        policy_id: str,
        policy_digest: str,
        artifacts: tuple[EvidenceArtifact, ...],
        required_ids: tuple[str, ...],
    ) -> dict[str, Any]:
        return {
            "bundle_format": EVIDENCE_BUNDLE_FORMAT,
            "subject_id": subject_id,
            "policy_id": policy_id,
            "policy_digest": policy_digest,
            "required_ids": list(required_ids),
            "artifacts": [artifact.core() for artifact in artifacts],
        }

    @classmethod
    def create(
        cls,
        *,
        subject_id: str,
        policy: AssurancePolicy,
        artifacts: Iterable[EvidenceArtifact],
        required_stages: Iterable[AssuranceStage] | None = None,
    ) -> EvidenceBundle:
        """Assemble a deterministic bundle and content-address it.

        ``required_stages`` narrows the *required* set to the stages already complete. A
        bundle can never contain an artifact that describes itself, so the bundle
        certification intelligence assesses is scoped to the stages that finished before
        it ran; the final bundle is assembled with the full required set.
        """
        ordered = tuple(sorted(artifacts, key=lambda a: (a.stage.order, a.name, a.artifact_id)))
        scope = set(required_stages) if required_stages is not None else None
        required_ids = tuple(
            sorted(
                artifact.id
                for artifact in policy.evidence.required_artifacts()
                if scope is None or artifact.stage in scope
            )
        )
        core = cls._core(
            subject_id=subject_id,
            policy_id=policy.identity.id,
            policy_digest=policy.digest(),
            artifacts=ordered,
            required_ids=required_ids,
        )
        digest = content_hash(core)
        return cls(
            evidence_id=f"UCOS-AEVD-{digest[:16]}",
            subject_id=subject_id,
            policy_id=policy.identity.id,
            policy_digest=policy.digest(),
            artifacts=ordered,
            required_ids=required_ids,
            bundle_sha256=digest,
        )

    # -- derived, measurable properties ----------------------------------------

    def artifact_ids(self) -> tuple[str, ...]:
        return tuple(artifact.artifact_id for artifact in self.artifacts)

    def artifacts_for(self, stage: AssuranceStage) -> tuple[EvidenceArtifact, ...]:
        return tuple(artifact for artifact in self.artifacts if artifact.stage is stage)

    def get(self, artifact_id: str) -> EvidenceArtifact | None:
        for artifact in self.artifacts:
            if artifact.artifact_id == artifact_id:
                return artifact
        return None

    def missing_required(self) -> tuple[str, ...]:
        """The declared-required artifact ids no stage contributed (fail-closed)."""
        present = set(self.artifact_ids())
        return tuple(sorted(set(self.required_ids) - present))

    def undeclared(self) -> tuple[str, ...]:
        """The contributed artifact ids the policy never declared."""
        return tuple(
            sorted(artifact.artifact_id for artifact in self.artifacts if not artifact.declared)
        )

    @property
    def manifest_intact(self) -> bool:
        """True iff every artifact digest matches a recomputation of its payload."""
        return all(artifact.intact for artifact in self.artifacts)

    @property
    def complete(self) -> bool:
        """True iff every policy-required artifact is present and every digest verifies."""
        return not self.missing_required() and self.manifest_intact

    def manifest(self) -> dict[str, Any]:
        """The self-verifying manifest written alongside the artifact files."""
        return {
            "manifest_format": EVIDENCE_MANIFEST_FORMAT,
            "evidence_id": self.evidence_id,
            "subject_id": self.subject_id,
            "policy_id": self.policy_id,
            "policy_digest": self.policy_digest,
            "complete": self.complete,
            "manifest_intact": self.manifest_intact,
            "counts": self.counts(),
            "required_ids": list(self.required_ids),
            "missing_required": list(self.missing_required()),
            "undeclared": list(self.undeclared()),
            "artifacts": [artifact.to_dict() for artifact in self.artifacts],
            "bundle_sha256": self.bundle_sha256,
        }

    def counts(self) -> dict[str, int]:
        return {
            "artifacts": len(self.artifacts),
            "declared": sum(1 for a in self.artifacts if a.declared),
            "undeclared": len(self.undeclared()),
            "required": len(self.required_ids),
            "missing_required": len(self.missing_required()),
        }

    def observations(self) -> dict[str, float]:
        """The numeric facts the policy's evidence metrics are evaluated against."""
        counts = self.counts()
        return {
            "evidence.artifacts": float(counts["artifacts"]),
            "evidence.required_artifacts": float(counts["required"]),
            "evidence.missing_required_artifacts": float(counts["missing_required"]),
            "evidence.undeclared_artifacts": float(counts["undeclared"]),
            "evidence.manifest_intact": 1.0 if self.manifest_intact else 0.0,
        }

    def to_dict(self) -> dict[str, Any]:
        return {**self.manifest(), "bundle_format": EVIDENCE_BUNDLE_FORMAT}


class EvidenceCollector:
    """**Evidence Collection** — accumulates stage contributions into one bundle.

    The collector is the only mutable object in the package: it is an accumulator, not a
    determination. Every contribution is immediately content-addressed, and the resulting
    bundle is immutable.
    """

    __slots__ = ("_policy", "_artifacts")

    def __init__(self, policy: AssurancePolicy) -> None:
        if not isinstance(policy, AssurancePolicy):
            raise AssuranceEvidenceError("evidence collection requires an AssurancePolicy")
        self._policy = policy
        self._artifacts: dict[str, EvidenceArtifact] = {}

    @property
    def policy(self) -> AssurancePolicy:
        return self._policy

    def __len__(self) -> int:
        return len(self._artifacts)

    def record(
        self, stage: AssuranceStage, name: str, payload: Mapping[str, Any]
    ) -> EvidenceArtifact:
        """Contribute ``payload`` as the ``name`` artifact of ``stage``.

        The contribution is matched to the policy's declared artifact for that
        ``(stage, name)`` pair. A contribution the policy never declared is still
        collected — flagged ``declared=False`` and counted — so drift is visible rather
        than silent.
        """
        if not isinstance(name, str) or not name:
            raise AssuranceEvidenceError(
                "an evidence artifact requires a non-empty name", stage=stage.value
            )
        declared = self._declared_id(stage, name)
        artifact_id = declared or f"{UNDECLARED_ARTIFACT_PREFIX}-{stage.value}-{name}"
        artifact = EvidenceArtifact.create(
            artifact_id=artifact_id,
            stage=stage,
            name=name,
            payload=payload,
            declared=declared is not None,
        )
        self._artifacts[artifact_id] = artifact
        return artifact

    def _declared_id(self, stage: AssuranceStage, name: str) -> str | None:
        for declared in self._policy.artifacts_for(stage):
            if declared.name == name:
                return declared.id
        return None

    def artifacts(self) -> tuple[EvidenceArtifact, ...]:
        return tuple(
            sorted(self._artifacts.values(), key=lambda a: (a.stage.order, a.name, a.artifact_id))
        )

    def bundle(
        self,
        *,
        subject_id: str,
        required_stages: Iterable[AssuranceStage] | None = None,
    ) -> EvidenceBundle:
        """Freeze the accumulated contributions into an immutable bundle."""
        return EvidenceBundle.create(
            subject_id=subject_id,
            policy=self._policy,
            artifacts=self.artifacts(),
            required_stages=required_stages,
        )


def check_write_scope(directory: Path, forbidden_prefixes: Iterable[str]) -> None:
    """Fail closed before writing if ``directory`` falls under a forbidden prefix.

    Both the supplied (possibly relative) path and its resolution relative to the current
    working directory are checked, so neither a relative nor an absolute spelling of a
    forbidden location can slip through.
    """
    candidates = {directory.as_posix().lstrip("./")}
    try:
        candidates.add(directory.resolve().relative_to(Path.cwd()).as_posix())
    except (ValueError, OSError):  # outside the workspace — the prefix rules cannot apply
        pass
    for prefix in forbidden_prefixes:
        normalized = prefix.strip("/") + "/"
        for candidate in candidates:
            if f"{candidate.rstrip('/')}/".startswith(normalized):
                raise AssuranceEvidenceError(
                    "evidence write scope is forbidden by policy",
                    directory=str(directory),
                    forbidden_prefix=prefix,
                )


def write_json(path: Path, payload: Mapping[str, Any]) -> Path:
    """Write ``payload`` deterministically (sorted keys, 2-space indent, trailing newline)."""
    text = json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    path.write_text(text, encoding="utf-8")
    return path


def write_bundle(
    bundle: EvidenceBundle,
    directory: str | Path,
    *,
    forbidden_prefixes: Iterable[str] = (),
) -> tuple[Path, ...]:
    """Write every artifact plus the manifest under ``directory`` (deterministically).

    Returns the written paths in canonical order. Raises
    :class:`~platform.universal_assurance.errors.AssuranceEvidenceError` if the target
    falls under a policy-forbidden prefix or cannot be created.
    """
    target = Path(directory)
    check_write_scope(target, forbidden_prefixes)
    try:
        target.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise AssuranceEvidenceError(
            "evidence directory could not be created",
            directory=str(target),
            detail=str(exc),
        ) from exc

    written: list[Path] = []
    try:
        for artifact in bundle.artifacts:
            written.append(write_json(target / artifact.filename, artifact.payload))
        written.append(write_json(target / MANIFEST_FILENAME, bundle.manifest()))
    except OSError as exc:
        raise AssuranceEvidenceError(
            "evidence artifact could not be written",
            directory=str(target),
            detail=str(exc),
        ) from exc
    return tuple(written)


__all__ = [
    "EVIDENCE_BUNDLE_FORMAT",
    "EVIDENCE_MANIFEST_FORMAT",
    "MANIFEST_FILENAME",
    "UNDECLARED_ARTIFACT_PREFIX",
    "EvidenceArtifact",
    "EvidenceBundle",
    "EvidenceCollector",
    "check_write_scope",
    "write_json",
    "write_bundle",
]
