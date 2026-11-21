"""TASK-000046 — Validation architecture: checks (EPIC-007).

A validation **check** is an immutable, deterministic predicate over a
:class:`~engine.validation.contracts.ValidationSubject`. Each check has a stable
id, a severity, and an ``evaluate`` method returning a
:class:`~engine.validation.contracts.ValidationFinding`. Checks are pure functions
of the subject — no secrets, no registry access, no wall-clock — so identical
subjects yield identical findings.

The built-in suite validates the constitutional invariants a generated,
deployable artifact must hold (IMP-007 §1/§8/§12, DE-05): provenance chain,
signature shape, SBOM presence, EC-1 provisional-state disclosure, a pinned
dependency closure, a digest-pinned image, and a deterministic runtime identity.
The architecture is open: callers may supply their own checks to the engine.
"""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from typing import Any, ClassVar

from engine.foundation.contracts.disclosure import disclosure_present
from engine.validation.contracts import (
    CheckStatus,
    Severity,
    ValidationFinding,
    ValidationSubject,
)

_RUNTIME_ID = re.compile(r"^UCOS-RUN-.+-[0-9a-f]{16}$")


class ValidationCheck(ABC):
    """The common contract for a single validation check (the architecture unit)."""

    check_id: ClassVar[str]
    severity: ClassVar[Severity]
    description: ClassVar[str] = ""

    @abstractmethod
    def evaluate(self, subject: ValidationSubject) -> ValidationFinding:
        """Return a finding for ``subject`` (never raises for a well-formed subject)."""
        raise NotImplementedError  # pragma: no cover

    # -- helpers ---------------------------------------------------------------

    def _passed(self, message: str = "", **details: Any) -> ValidationFinding:
        return ValidationFinding(
            check_id=self.check_id,
            severity=self.severity,
            status=CheckStatus.PASS,
            message=message or f"{self.check_id} satisfied",
            details=details,
        )

    def _failed(self, message: str, **details: Any) -> ValidationFinding:
        return ValidationFinding(
            check_id=self.check_id,
            severity=self.severity,
            status=CheckStatus.FAIL,
            message=message,
            details=details,
        )


class ProvenanceCheck(ValidationCheck):
    """The backward-traceability chain is present, well-formed, and rooted (§1)."""

    check_id = "provenance-chain"
    severity = Severity.BLOCKING
    description = "Provenance chain is non-empty, all-string, and rooted at the blueprint."

    def evaluate(self, subject: ValidationSubject) -> ValidationFinding:
        chain = subject.provenance_chain
        if not chain:
            return self._failed("provenance chain is empty")
        if not all(isinstance(link, str) and link for link in chain):
            return self._failed("provenance chain contains an empty or non-string link")
        if chain[0] != subject.blueprint_id:
            return self._failed(
                "provenance chain does not originate at the blueprint",
                head=chain[0],
                blueprint_id=subject.blueprint_id,
            )
        return self._passed(links=len(chain))


class SignatureCheck(ValidationCheck):
    """The package signature is present and well-formed (§12)."""

    check_id = "signature-present"
    severity = Severity.BLOCKING
    description = "Signature has an algorithm, a value, and a payload hash."

    def evaluate(self, subject: ValidationSubject) -> ValidationFinding:
        signature = subject.signature
        missing = [
            key for key in ("algorithm", "value", "payload_sha256") if not signature.get(key)
        ]
        if missing:
            return self._failed("signature is incomplete", missing=missing)
        return self._passed(algorithm=signature.get("algorithm"))


class SbomCheck(ValidationCheck):
    """A well-formed SBOM enumerating components is present (§12)."""

    check_id = "sbom-present"
    severity = Severity.BLOCKING
    description = "SBOM has a format and at least one component."

    def evaluate(self, subject: ValidationSubject) -> ValidationFinding:
        sbom = subject.sbom
        if not sbom.get("sbom_format"):
            return self._failed("SBOM is absent or has no format")
        components = sbom.get("components")
        if not isinstance(components, list) or not components:
            return self._failed("SBOM enumerates no components")
        return self._passed(components=len(components))


class DisclosureCheck(ValidationCheck):
    """The EC-1 provisional-state disclosure is present (DE-05 / C-05)."""

    check_id = "provisional-state-disclosure"
    severity = Severity.BLOCKING
    description = "EC-1 provisional-state disclosure is present and asserts no finality."

    def evaluate(self, subject: ValidationSubject) -> ValidationFinding:
        if not disclosure_present(subject.disclosure):
            return self._failed("EC-1 provisional-state disclosure is absent or malformed")
        disclosure = subject.disclosure or {}
        return self._passed(disclosure_id=disclosure.get("disclosure_id"))


class DependencyClosureCheck(ValidationCheck):
    """The dependency closure is present and pinned by digest (§8)."""

    check_id = "dependency-closure-pinned"
    severity = Severity.BLOCKING
    description = "Closure has exactly one root and every member is digest-pinned."

    def evaluate(self, subject: ValidationSubject) -> ValidationFinding:
        closure = subject.dependency_closure
        if not closure:
            return self._failed("dependency closure is empty")
        roots = [e for e in closure if e.get("role") == "root"]
        if len(roots) != 1:
            return self._failed("closure must contain exactly one root", roots=len(roots))
        unpinned = [e.get("blueprint_id") for e in closure if not e.get("package_sha256")]
        if unpinned:
            return self._failed("closure members are not digest-pinned", unpinned=unpinned)
        if roots[0].get("package_sha256") != subject.package_sha256:
            return self._failed(
                "closure root hash does not match the subject package hash",
                root=roots[0].get("package_sha256"),
                subject=subject.package_sha256,
            )
        return self._passed(members=len(closure))


class ImageDigestCheck(ValidationCheck):
    """The runtime image is pinned by digest to the package hash (§8)."""

    check_id = "image-digest-pinned"
    severity = Severity.BLOCKING
    description = "Image reference is pinned by @sha256:<package_hash>."

    def evaluate(self, subject: ValidationSubject) -> ValidationFinding:
        expected = f"@sha256:{subject.package_sha256}"
        if not subject.package_sha256 or expected not in subject.image_reference:
            return self._failed(
                "image reference is not digest-pinned to the package hash",
                image_reference=subject.image_reference,
            )
        return self._passed(image_reference=subject.image_reference)


class IdentityCheck(ValidationCheck):
    """The runtime identity is well-formed and deterministic (§5)."""

    check_id = "identity-deterministic"
    severity = Severity.ADVISORY
    description = "Runtime id matches the deterministic UCOS-RUN-<blueprint>-<hex16> form."

    def evaluate(self, subject: ValidationSubject) -> ValidationFinding:
        runtime_id = subject.runtime_id or ""
        if not _RUNTIME_ID.match(runtime_id):
            return self._failed(
                "runtime id is missing or not in the deterministic form",
                runtime_id=runtime_id,
            )
        return self._passed(runtime_id=runtime_id)


#: The built-in checks, in stable id order (deterministic execution).
def default_checks() -> tuple[ValidationCheck, ...]:
    """Return the built-in validation suite, ordered deterministically by id."""
    checks: tuple[ValidationCheck, ...] = (
        DependencyClosureCheck(),
        DisclosureCheck(),
        IdentityCheck(),
        ImageDigestCheck(),
        ProvenanceCheck(),
        SbomCheck(),
        SignatureCheck(),
    )
    return tuple(sorted(checks, key=lambda c: c.check_id))


__all__ = [
    "ValidationCheck",
    "ProvenanceCheck",
    "SignatureCheck",
    "SbomCheck",
    "DisclosureCheck",
    "DependencyClosureCheck",
    "ImageDigestCheck",
    "IdentityCheck",
    "default_checks",
]
