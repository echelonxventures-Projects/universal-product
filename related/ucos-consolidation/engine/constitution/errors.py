"""UCOS-CEL-0001 — typed, structured failures of the constitutional execution system.

Every refusal in this package is *evidence*: it carries the machine-readable detail that
names what was refused and which clause refused it, so a caller never has to string-match
a reason. The hierarchy is one root plus one subclass per constitutional failure mode,
mirroring :mod:`engine.nucleus.errors` rather than inventing a second error style.

Nothing here is recoverable by retrying. Each of these means *the request was not legal*,
which is a statement about the repository, not about the moment.
"""

from __future__ import annotations

from typing import Any


class ConstitutionalError(Exception):
    """Root of every constitutional execution failure."""

    def __init__(self, message: str, **detail: Any) -> None:
        super().__init__(message)
        self.message = message
        self.detail: dict[str, Any] = {k: detail[k] for k in sorted(detail)}

    def to_dict(self) -> dict[str, Any]:
        return {
            "error": type(self).__name__,
            "message": self.message,
            "detail": self.detail,
        }

    def __str__(self) -> str:  # pragma: no cover - trivial formatting
        if not self.detail:
            return self.message
        rendered = ", ".join(f"{k}={self.detail[k]!r}" for k in self.detail)
        return f"{self.message} ({rendered})"


class MetadataIncomplete(ConstitutionalError):
    """CEL-09 — an artifact lacks a mandated metadata facet.

    Incomplete metadata is not a documentation defect. An artifact that has not declared
    its owner, authorities, dependencies and rules is not executable, not governable, not
    certifiable and not registerable, because there is nothing to govern it *against*.
    """


class GraphError(ConstitutionalError):
    """CEL-01 — the declared graph cannot be interpreted (unknown referent, bad shape)."""


class CircularAuthority(ConstitutionalError):
    """CEL-05 — authority, certification or ownership closes a loop.

    A cycle in any of these relations means a subject derives its own permission to
    exist. It is refused rather than broken arbitrarily, because any tie-break here would
    be the system inventing an authority nobody granted.
    """


class SelfAttestation(CircularAuthority):
    """CEL-05 — a subject certifies, validates, verifies or ratifies itself."""


class IllegalExecution(ConstitutionalError):
    """CEL-03 — execution was requested over a subject that has not proven legality."""


class ManualSequencing(ConstitutionalError):
    """CEL-02 / CEL-10 — an execution order was supplied instead of derived."""


class DirtyStateViolation(ConstitutionalError):
    """CEL-07 — a measurement, certification or registration was attempted mid-mutation."""


class MutationRefused(ConstitutionalError):
    """CEL-04 — a mutation did not complete the gateway pipeline, so it does not apply."""


class ReplayDivergence(ConstitutionalError):
    """CEL-06 — replay did not reach a deterministic fixed point within its bound."""


class DuplicateTruth(ConstitutionalError):
    """CEL-08 — creation was requested where a canonical owner or capability exists."""


class AcceptanceFailure(ConstitutionalError):
    """CEL — one or more acceptance criteria of the system measured false."""


__all__ = [
    "AcceptanceFailure",
    "CircularAuthority",
    "ConstitutionalError",
    "DirtyStateViolation",
    "DuplicateTruth",
    "GraphError",
    "IllegalExecution",
    "ManualSequencing",
    "MetadataIncomplete",
    "MutationRefused",
    "ReplayDivergence",
    "SelfAttestation",
]
