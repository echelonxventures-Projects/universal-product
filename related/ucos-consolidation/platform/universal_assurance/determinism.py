"""UCOS-EPIC-014 — Assurance reproducibility (Terminal T7).

**Everything reproducible.** Every artifact this package emits is content-addressed over
a canonical core that excludes wall-clock and ambient state, so an identical subject
assured under an identical policy must reproduce byte-identical output. This module makes
that claim *checkable* rather than merely asserted: it re-runs a caller-supplied
production step the number of times the policy's
:class:`~platform.universal_assurance.policy.ReproducibilityPolicy` demands, canonicalizes
each result, and compares the bytes.

Determinism is proven the same way the constitutional programme engines prove it — render
twice from fixed inputs and compare the canonical bytes — and the resulting
:class:`ReproducibilityReport` is itself content-addressed, so the proof is auditable.

Fail-closed discipline: a replay set that is not byte-identical yields
``byte_identical=False`` and, when the policy requires byte identity, a **blocking**
shortfall. A runner that raises is a caller fault and surfaces as
:class:`~platform.universal_assurance.errors.AssuranceReproducibilityError` — a broken
producer is never silently reported as reproducible.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from platform.foundation.contracts import canonical_json, content_hash
from platform.universal_assurance.errors import AssuranceReproducibilityError
from platform.universal_assurance.policy import ReproducibilityPolicy
from typing import Any

#: The reproducibility report format identifier.
REPRODUCIBILITY_FORMAT = "ucos-assurance-reproducibility-report/1.0.0"


def canonical_bytes(payload: Any) -> bytes:
    """The canonical UTF-8 encoding used for every byte-identity comparison."""
    return canonical_json(payload).encode("utf-8")


@dataclass(frozen=True, slots=True)
class ReplaySample:
    """One replay of the production step under test."""

    index: int
    digest: str
    byte_length: int

    def core(self) -> dict[str, Any]:
        return {
            "index": self.index,
            "digest": self.digest,
            "byte_length": self.byte_length,
        }

    def to_dict(self) -> dict[str, Any]:
        return self.core()


@dataclass(frozen=True, slots=True)
class ReproducibilityReport:
    """An immutable, content-addressed proof (or disproof) of byte-level reproducibility."""

    subject_id: str
    label: str
    replays: int
    required: bool
    byte_identical: bool
    samples: tuple[ReplaySample, ...]
    distinct_digests: tuple[str, ...]
    report_sha256: str

    @staticmethod
    def _core(
        *,
        subject_id: str,
        label: str,
        replays: int,
        required: bool,
        byte_identical: bool,
        samples: tuple[ReplaySample, ...],
        distinct_digests: tuple[str, ...],
    ) -> dict[str, Any]:
        return {
            "reproducibility_format": REPRODUCIBILITY_FORMAT,
            "subject_id": subject_id,
            "label": label,
            "replays": replays,
            "required": required,
            "byte_identical": byte_identical,
            "samples": [sample.core() for sample in samples],
            "distinct_digests": list(distinct_digests),
        }

    @classmethod
    def create(
        cls,
        *,
        subject_id: str,
        label: str,
        required: bool,
        samples: tuple[ReplaySample, ...],
    ) -> ReproducibilityReport:
        distinct = tuple(sorted({sample.digest for sample in samples}))
        byte_identical = len(distinct) <= 1
        core = cls._core(
            subject_id=subject_id,
            label=label,
            replays=len(samples),
            required=required,
            byte_identical=byte_identical,
            samples=samples,
            distinct_digests=distinct,
        )
        return cls(
            subject_id=subject_id,
            label=label,
            replays=len(samples),
            required=required,
            byte_identical=byte_identical,
            samples=samples,
            distinct_digests=distinct,
            report_sha256=content_hash(core),
        )

    @property
    def passed(self) -> bool:
        """True unless the policy requires byte identity and the replays diverged."""
        return self.byte_identical or not self.required

    @property
    def is_blocking_shortfall(self) -> bool:
        return self.required and not self.byte_identical

    def observations(self) -> dict[str, float]:
        """The numeric facts the policy's reproducibility metrics decide."""
        return {
            "reproducibility.replays": float(self.replays),
            "reproducibility.distinct_digests": float(len(self.distinct_digests)),
            "reproducibility.byte_identical": 1.0 if self.byte_identical else 0.0,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "reproducibility_format": REPRODUCIBILITY_FORMAT,
            "subject_id": self.subject_id,
            "label": self.label,
            "replays": self.replays,
            "required": self.required,
            "byte_identical": self.byte_identical,
            "passed": self.passed,
            "distinct_digests": list(self.distinct_digests),
            "samples": [sample.to_dict() for sample in self.samples],
            "observations": self.observations(),
            "report_sha256": self.report_sha256,
        }


def verify_reproducibility(
    runner: Callable[[], Any],
    *,
    subject_id: str,
    label: str,
    policy: ReproducibilityPolicy | None = None,
    replays: int | None = None,
    required: bool | None = None,
) -> ReproducibilityReport:
    """Replay ``runner`` and prove (or disprove) byte-level reproducibility.

    ``runner`` must be a zero-argument callable returning a JSON-serializable payload —
    typically ``lambda: pipeline.run(subject).to_dict()``. The replay count and the
    byte-identity requirement come from ``policy`` unless overridden explicitly.

    Raises:
        AssuranceReproducibilityError: if ``runner`` is not callable, the replay count is
            below two, or a replay raises / returns an uncanonicalizable payload.
    """
    if not callable(runner):
        raise AssuranceReproducibilityError(
            "reproducibility verification requires a zero-argument callable", label=label
        )
    resolved_policy = policy if policy is not None else ReproducibilityPolicy()
    count = replays if replays is not None else resolved_policy.replays
    require = required if required is not None else resolved_policy.byte_identical_required
    if not isinstance(count, int) or isinstance(count, bool) or count < 2:
        raise AssuranceReproducibilityError(
            "reproducibility requires at least two replays", label=label, replays=count
        )

    samples: list[ReplaySample] = []
    for index in range(count):
        try:
            payload = runner()
            encoded = canonical_bytes(payload)
        except AssuranceReproducibilityError:
            raise
        except Exception as exc:  # noqa: BLE001 — a broken producer must not look clean
            raise AssuranceReproducibilityError(
                "a reproducibility replay failed",
                label=label,
                replay=index,
                detail=str(exc),
            ) from exc
        samples.append(
            ReplaySample(
                index=index,
                digest=content_hash(payload),
                byte_length=len(encoded),
            )
        )
    return ReproducibilityReport.create(
        subject_id=subject_id,
        label=label,
        required=require,
        samples=tuple(samples),
    )


def digests_match(left: Any, right: Any) -> bool:
    """True iff two payloads canonicalize to identical bytes."""
    return canonical_bytes(left) == canonical_bytes(right)


def replay_digest(payload: Any) -> str:
    """The canonical content digest of a single replay payload."""
    return content_hash(payload)


def reproducibility_observations(report: ReproducibilityReport | None) -> Mapping[str, float]:
    """Observations for a (possibly absent) reproducibility report — absent fails closed."""
    if report is None:
        return {
            "reproducibility.replays": 0.0,
            "reproducibility.distinct_digests": 0.0,
            "reproducibility.byte_identical": 0.0,
        }
    return report.observations()


__all__ = [
    "REPRODUCIBILITY_FORMAT",
    "canonical_bytes",
    "ReplaySample",
    "ReproducibilityReport",
    "verify_reproducibility",
    "digests_match",
    "replay_digest",
    "reproducibility_observations",
]
