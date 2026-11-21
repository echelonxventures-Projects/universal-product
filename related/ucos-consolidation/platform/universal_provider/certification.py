"""UPA-000009 — Provider Certification (Terminal-04).

Certification attests **only what validation substantiated** (PC-11). It re-judges
nothing: a certificate is a sound, content-addressed function of a
:class:`~platform.universal_provider.validation.ValidationReport` plus the descriptor
that report was computed over. Identical validation input therefore yields a
byte-identical certificate and a stable ``certificate_id``.

    * :class:`CertificationTier` — what a certificate attests, and what it authorizes.
    * :class:`ProviderCertificate` — the immutable certification record.
    * :class:`CertificationLedgerEntry` / :class:`CertificationLedger` — the
      append-only, hash-chained certification history.
    * :class:`ProviderCertifier` — issues certificates and seals them.

Only :attr:`CertificationTier.UNIVERSAL` authorizes activation. A provider whose
evidence is merely incomplete receives :attr:`CertificationTier.PROVISIONAL`: a real,
recorded, queryable certification that deliberately confers **no** authority to
serve. Incomplete evidence is neither treated as failure nor promoted to sufficiency.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from platform.universal_provider.constitution import (
    PROVIDER_CONSTITUTION_ID,
    PROVIDER_CONSTITUTION_VERSION,
    PROVIDER_FRAMEWORK_OWNER,
    PROVIDER_INTERFACE,
    PROVIDER_INTERFACE_VERSION,
)
from platform.universal_provider.contracts import ProviderDescriptor, content_hash
from platform.universal_provider.errors import ProviderCertificationError
from platform.universal_provider.lifecycle import GENESIS_HASH
from platform.universal_provider.validation import (
    GateStatus,
    ValidationReport,
    ValidationStatus,
)
from typing import Any

#: Semantic version of the Provider Certification contract surface.
PROVIDER_CERTIFICATION_VERSION = "1.0.0"

#: The standard a provider certificate attests against.
PROVIDER_CERTIFICATION_STANDARD = "UCOS-PROVIDER-CERTIFICATION-STANDARD"

#: Length of the short, human-quotable seal derived from the certificate id.
SEAL_LENGTH = 16


class CertificationTier(str, Enum):
    """What a certificate attests — and therefore what it permits.

    * ``UNIVERSAL``   — every constitutional gate passed. Authorizes activation.
    * ``PROVISIONAL`` — no blocking failure, but some evidence is absent.
      Recorded and queryable; authorizes nothing.
    * ``REFUSED``     — at least one blocking constitutional failure.
    """

    UNIVERSAL = "certified-universal"
    PROVISIONAL = "certified-provisional"
    REFUSED = "refused"


def tier_for(report: ValidationReport) -> CertificationTier:
    """Return the tier a validation report substantiates — and no more."""
    status = report.status
    if status is ValidationStatus.FAILED:
        return CertificationTier.REFUSED
    if status is ValidationStatus.INCOMPLETE:
        return CertificationTier.PROVISIONAL
    return CertificationTier.UNIVERSAL


@dataclass(frozen=True, slots=True)
class ProviderCertificate:
    """The immutable, content-addressed certification record for one provider."""

    qualified_id: str
    descriptor_hash: str
    report_hash: str
    tier: CertificationTier
    gates_total: int
    gates_passed: int
    gates_failed: int
    gates_indeterminate: int
    constitution_id: str = PROVIDER_CONSTITUTION_ID
    constitution_version: str = PROVIDER_CONSTITUTION_VERSION
    constitution_hash: str = ""
    interface: str = PROVIDER_INTERFACE
    interface_version: str = PROVIDER_INTERFACE_VERSION
    standard: str = PROVIDER_CERTIFICATION_STANDARD
    authority: str = PROVIDER_FRAMEWORK_OWNER
    findings: tuple[str, ...] = ()

    @property
    def authorizes_activation(self) -> bool:
        """Whether this certificate permits the provider to serve consumers (PC-11)."""
        return self.tier is CertificationTier.UNIVERSAL

    @property
    def certificate_id(self) -> str:
        """The content-addressed identity of this certificate."""
        return content_hash(self.payload())

    @property
    def seal(self) -> str:
        """A short, quotable seal derived from the certificate id."""
        return self.certificate_id[:SEAL_LENGTH]

    def payload(self) -> dict[str, Any]:
        """Return the content the certificate identity is computed over."""
        return {
            "certification_version": PROVIDER_CERTIFICATION_VERSION,
            "qualified_id": self.qualified_id,
            "descriptor_hash": self.descriptor_hash,
            "report_hash": self.report_hash,
            "tier": self.tier.value,
            "gates": {
                "total": self.gates_total,
                "passed": self.gates_passed,
                "failed": self.gates_failed,
                "indeterminate": self.gates_indeterminate,
            },
            "constitution_id": self.constitution_id,
            "constitution_version": self.constitution_version,
            "constitution_hash": self.constitution_hash,
            "interface": self.interface,
            "interface_version": self.interface_version,
            "standard": self.standard,
            "authority": self.authority,
            "findings": list(self.findings),
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            **self.payload(),
            "certificate_id": self.certificate_id,
            "seal": self.seal,
            "authorizes_activation": self.authorizes_activation,
        }

    def summary(self) -> str:
        """Return the one-line corpus-idiomatic certification summary."""
        return (
            f"{self.qualified_id}: {self.tier.value.upper()} | "
            f"gates={self.gates_passed}/{self.gates_total} PASS | "
            f"indeterminate={self.gates_indeterminate} | "
            f"blocking={self.gates_failed or 'none'} | seal={self.seal}"
        )


@dataclass(frozen=True, slots=True)
class CertificationLedgerEntry:
    """One immutable, hash-chained certification record."""

    sequence: int
    certificate: ProviderCertificate
    previous_hash: str
    entry_hash: str

    def payload(self) -> dict[str, Any]:
        return {
            "sequence": self.sequence,
            "certificate_id": self.certificate.certificate_id,
            "qualified_id": self.certificate.qualified_id,
            "tier": self.certificate.tier.value,
            "previous_hash": self.previous_hash,
        }

    def recompute_hash(self) -> str:
        return content_hash(self.payload())

    def to_dict(self) -> dict[str, Any]:
        return {
            **self.payload(),
            "entry_hash": self.entry_hash,
            "certificate": self.certificate.to_dict(),
        }


class CertificationLedger:
    """The append-only, tamper-evident certification history."""

    def __init__(self) -> None:
        self._entries: list[CertificationLedgerEntry] = []

    @property
    def entries(self) -> tuple[CertificationLedgerEntry, ...]:
        return tuple(self._entries)

    @property
    def head_hash(self) -> str:
        return self._entries[-1].entry_hash if self._entries else GENESIS_HASH

    def __len__(self) -> int:
        return len(self._entries)

    def append(self, certificate: ProviderCertificate) -> CertificationLedgerEntry:
        """Append ``certificate`` to the chain and return its entry."""
        if not isinstance(certificate, ProviderCertificate):
            raise ProviderCertificationError(
                "only a ProviderCertificate may be appended to the certification ledger",
                {"received": type(certificate).__name__},
            )
        previous_hash = self.head_hash
        sequence = len(self._entries) + 1
        payload = {
            "sequence": sequence,
            "certificate_id": certificate.certificate_id,
            "qualified_id": certificate.qualified_id,
            "tier": certificate.tier.value,
            "previous_hash": previous_hash,
        }
        entry = CertificationLedgerEntry(
            sequence=sequence,
            certificate=certificate,
            previous_hash=previous_hash,
            entry_hash=content_hash(payload),
        )
        self._entries.append(entry)
        return entry

    def latest(self, qualified_id: str) -> CertificationLedgerEntry | None:
        """Return the most recent certification for ``qualified_id``, if any."""
        for entry in reversed(self._entries):
            if entry.certificate.qualified_id == qualified_id:
                return entry
        return None

    def certificates(self) -> tuple[ProviderCertificate, ...]:
        return tuple(entry.certificate for entry in self._entries)

    def verify(self) -> bool:
        """Whether the certification chain is intact and correctly linked."""
        previous = GENESIS_HASH
        for index, entry in enumerate(self._entries, start=1):
            if entry.sequence != index or entry.previous_hash != previous:
                return False
            if entry.recompute_hash() != entry.entry_hash:
                return False
            previous = entry.entry_hash
        return True

    def require_intact(self) -> None:
        if not self.verify():
            raise ProviderCertificationError(
                "provider certification ledger integrity check failed",
                {"entries": len(self._entries), "head_hash": self.head_hash},
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "certification_version": PROVIDER_CERTIFICATION_VERSION,
            "count": len(self._entries),
            "head_hash": self.head_hash,
            "entries": [entry.to_dict() for entry in self._entries],
        }

    def ledger_hash(self) -> str:
        return content_hash(self.to_dict())


class ProviderCertifier:
    """Issues provider certificates from validation evidence, and records them.

    Sound by construction: the certifier refuses to certify a report that was not
    computed over the descriptor presented, so a certificate can never attest a
    provider other than the one that was measured.
    """

    def __init__(self, ledger: CertificationLedger | None = None) -> None:
        self._ledger = ledger if ledger is not None else CertificationLedger()

    @property
    def ledger(self) -> CertificationLedger:
        return self._ledger

    def certify(
        self,
        descriptor: ProviderDescriptor,
        report: ValidationReport,
        *,
        constitution_hash: str = "",
    ) -> ProviderCertificate:
        """Issue and record the certificate ``report`` substantiates for ``descriptor``."""
        if not isinstance(descriptor, ProviderDescriptor):
            raise ProviderCertificationError(
                "certification requires a ProviderDescriptor",
                {"received": type(descriptor).__name__},
            )
        if not isinstance(report, ValidationReport):
            raise ProviderCertificationError(
                "certification requires a ValidationReport",
                {"received": type(report).__name__},
            )
        if report.qualified_id != descriptor.qualified_id:
            raise ProviderCertificationError(
                "validation report does not concern the presented provider",
                {
                    "report_subject": report.qualified_id,
                    "descriptor": descriptor.qualified_id,
                },
            )
        descriptor_hash = descriptor.content_hash()
        if report.descriptor_hash != descriptor_hash:
            raise ProviderCertificationError(
                "validation report was computed over a different descriptor revision",
                {
                    "qualified_id": descriptor.qualified_id,
                    "report_descriptor_hash": report.descriptor_hash,
                    "descriptor_hash": descriptor_hash,
                },
            )
        if not report.results:
            raise ProviderCertificationError(
                "certification requires an executed validation pass (PC-11)",
                {"qualified_id": descriptor.qualified_id},
            )
        counts = report.counts()
        findings = tuple(
            f"{result.gate_id}[{result.status.value}]: {finding}"
            for result in report.results
            if result.status is not GateStatus.PASS
            for finding in (result.findings or (result.summary,))
        )
        certificate = ProviderCertificate(
            qualified_id=descriptor.qualified_id,
            descriptor_hash=descriptor_hash,
            report_hash=report.report_hash(),
            tier=tier_for(report),
            gates_total=counts["total"],
            gates_passed=counts["pass"],
            gates_failed=counts["fail"],
            gates_indeterminate=counts["indeterminate"],
            constitution_id=report.constitution_id,
            constitution_version=report.constitution_version,
            constitution_hash=constitution_hash,
            findings=findings,
        )
        self._ledger.append(certificate)
        return certificate

    def latest(self, qualified_id: str) -> ProviderCertificate | None:
        entry = self._ledger.latest(qualified_id)
        return entry.certificate if entry is not None else None

    def authorizes_activation(self, qualified_id: str) -> bool:
        """Whether the latest certificate authorizes activation (PC-11)."""
        certificate = self.latest(qualified_id)
        return certificate is not None and certificate.authorizes_activation


__all__ = [
    "PROVIDER_CERTIFICATION_STANDARD",
    "PROVIDER_CERTIFICATION_VERSION",
    "SEAL_LENGTH",
    "CertificationLedger",
    "CertificationLedgerEntry",
    "CertificationTier",
    "ProviderCertificate",
    "ProviderCertifier",
    "tier_for",
]
