"""UCOS-EPIC-014 — Commercial Certification (Terminal T5).

Commercial Certification is the *derived* verdict on a commercial surface. It is never
asserted: it is a deterministic projection of one :class:`CommercialIntelligenceReport`
over the closed determination set, computed by exactly one rule —

    * a blocking failure in any domain  → ``NOT-CERTIFIED``;
    * no blocking failure, but an advisory failure → ``CERTIFIED-PROVISIONAL``;
    * neither → ``CERTIFIED``.

The certificate carries the per-domain and per-family verdicts, the blocking and advisory
failure lists, and the report digest it was derived from, so a certificate can always be
re-derived from — and reconciled against — the report that produced it. It inherits the
report's ``ENGINEERING-EXECUTION-ONLY`` authority and the EC-1 provisional-state
disclosure: a commercial certificate ratifies nothing constitutionally (DE-05 / IP-01).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from platform.commercial_intelligence.contracts import (
    CommercialIntelligenceReport,
    DomainKind,
)
from platform.foundation.contracts import content_hash
from typing import Any

#: The commercial certificate format identifier.
CERTIFICATE_FORMAT = "ucos-commercial-certificate/1.0.0"


class Determination(str, Enum):
    """The closed commercial-certification determination set."""

    CERTIFIED = "CERTIFIED"
    CERTIFIED_PROVISIONAL = "CERTIFIED-PROVISIONAL"
    NOT_CERTIFIED = "NOT-CERTIFIED"

    @property
    def certified(self) -> bool:
        """True for a full or provisional certification; false only when withheld."""
        return self is not Determination.NOT_CERTIFIED


@dataclass(frozen=True, slots=True)
class CommercialCertificate:
    """An immutable, content-addressed commercial certification determination."""

    subject_id: str
    determination: Determination
    report_sha256: str
    domain_verdicts: dict[str, str]
    kind_verdicts: dict[str, str]
    blocking_failures: tuple[str, ...]
    advisory_failures: tuple[str, ...]
    domains_certified: int
    domains_total: int
    authority: str
    disclosure: dict[str, Any]
    certificate_sha256: str

    @classmethod
    def from_report(cls, report: CommercialIntelligenceReport) -> CommercialCertificate:
        """Derive the certificate from ``report`` — one rule, no judgement."""
        blocking = report.blocking_failures()
        advisory = report.advisory_failures()
        if blocking:
            determination = Determination.NOT_CERTIFIED
        elif advisory:
            determination = Determination.CERTIFIED_PROVISIONAL
        else:
            determination = Determination.CERTIFIED
        core = {
            "certificate_format": CERTIFICATE_FORMAT,
            "subject_id": report.target_id,
            "determination": determination.value,
            "report_sha256": report.report_sha256,
            "domain_verdicts": report.domain_verdicts(),
            "kind_verdicts": report.kind_verdicts(),
            "blocking_failures": list(blocking),
            "advisory_failures": list(advisory),
            "authority": report.authority,
            "disclosure": dict(report.disclosure),
        }
        return cls(
            subject_id=report.target_id,
            determination=determination,
            report_sha256=report.report_sha256,
            domain_verdicts=report.domain_verdicts(),
            kind_verdicts=report.kind_verdicts(),
            blocking_failures=blocking,
            advisory_failures=advisory,
            domains_certified=sum(1 for r in report.domain_reports if r.passed),
            domains_total=len(report.domain_reports),
            authority=report.authority,
            disclosure=dict(report.disclosure),
            certificate_sha256=content_hash(core),
        )

    @property
    def certified(self) -> bool:
        return self.determination.certified

    @property
    def provisional(self) -> bool:
        return self.determination is Determination.CERTIFIED_PROVISIONAL

    def kind_certified(self, kind: DomainKind) -> bool:
        """True iff the domain family ``kind`` carries no failing domain."""
        return self.kind_verdicts.get(kind.value) == "pass"

    def to_dict(self) -> dict[str, Any]:
        return {
            "certificate_format": CERTIFICATE_FORMAT,
            "subject_id": self.subject_id,
            "determination": self.determination.value,
            "certified": self.certified,
            "provisional": self.provisional,
            "report_sha256": self.report_sha256,
            "domain_verdicts": dict(self.domain_verdicts),
            "kind_verdicts": dict(self.kind_verdicts),
            "blocking_failures": list(self.blocking_failures),
            "advisory_failures": list(self.advisory_failures),
            "domains_certified": self.domains_certified,
            "domains_total": self.domains_total,
            "authority": self.authority,
            "disclosure": dict(self.disclosure),
            "certificate_sha256": self.certificate_sha256,
        }

    def digest(self) -> str:
        return self.certificate_sha256


def certify(report: CommercialIntelligenceReport) -> CommercialCertificate:
    """Derive the commercial certificate for ``report``."""
    return CommercialCertificate.from_report(report)


__all__ = [
    "CERTIFICATE_FORMAT",
    "Determination",
    "CommercialCertificate",
    "certify",
]
