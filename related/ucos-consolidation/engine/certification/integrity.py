"""Constitutional Certification Integrity (EPIC-008 strengthening).

An **additive**, record-only integrity layer over a *set* of certification
determinations. Where :mod:`engine.certification.engine` decides one certification
and :mod:`engine.certification.ledger` chains them tamper-evidently, this module
attests the *constitutional* invariants that must hold across the whole population
of certification records + their evidence:

    * **duplicate detection** — no target/version is certified twice, and no
      evidence record is emitted twice (**zero duplicate certification**, **zero
      duplicate evidence**);
    * **overlap detection** — no single target carries more than one *certified*
      determination (no overlapping active certifications);
    * **drift detection** — the same ``(target, version)`` never yields divergent
      records (a re-certification that changed hash or status is drift);
    * **traceability validation** — every certification evidence pairs back to its
      immutable record and preserves the Validation → Certification evidence chain;
    * **completeness validation** — every *certified* record carries present,
      block-free evidence, and (optionally) every expected target is covered.

Every rule is a falsifiable predicate over declared fields (no invented verdict,
TP-01). The layer is deterministic (IMP-007 §5): an identical population yields a
byte-identical report and evidence. It mutates nothing and never writes the
certified corpus (DP-03).

Two enforcement surfaces are provided:

    * :class:`CertificationRegister` — an **append-only, dedup-aware** collection
      that fails *closed at registration time*: registering an identical
      determination is an idempotent no-op, while a *conflicting* duplicate raises
      :class:`DuplicateCertificationError`. This makes duplicate certification /
      evidence structurally impossible for callers that register through it.
    * :func:`verify_certification_integrity` + :func:`enforce_integrity` — a
      *batch* verifier that detects the same defects over an arbitrary population
      (e.g. records loaded from a ledger) and fails closed with named defects.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

from engine.certification.contracts import (
    CertificationRecord,
    CertificationStatus,
    CriterionSeverity,
    CriterionStatus,
    content_hash,
)
from engine.certification.errors import CertificationLayerError
from engine.certification.evidence import CertificationEvidence
from engine.foundation.obs.logging import get_logger

_logger = get_logger("certification.integrity")

#: The constitutional-integrity report format identifier.
INTEGRITY_REPORT_FORMAT = "ucos-certification-integrity/1.0.0"

#: The constitutional-integrity evidence record format identifier.
INTEGRITY_EVIDENCE_FORMAT = "ucos-certification-integrity-evidence/1.0.0"


# ---------------------------------------------------------------------------
# errors (defined here so the completed error taxonomy stays untouched)
# ---------------------------------------------------------------------------
class DuplicateCertificationError(CertificationLayerError):
    """A conflicting duplicate certification or evidence was registered."""

    code = "CERT-DUPLICATE-001"


class ConstitutionalIntegrityError(CertificationLayerError):
    """A population of certifications failed a blocking constitutional invariant."""

    code = "CERT-CONSTITUTIONAL-001"


# ---------------------------------------------------------------------------
# findings + report
# ---------------------------------------------------------------------------
@dataclass(frozen=True, slots=True)
class IntegrityFinding:
    """The immutable outcome of a single constitutional-integrity check."""

    check_id: str
    severity: CriterionSeverity
    status: CriterionStatus
    message: str = ""
    details: Mapping[str, Any] = field(default_factory=dict)

    @property
    def passed(self) -> bool:
        return self.status is CriterionStatus.PASS

    @property
    def is_blocking_failure(self) -> bool:
        return self.status is CriterionStatus.FAIL and self.severity is CriterionSeverity.BLOCKING

    def to_dict(self) -> dict[str, Any]:
        return {
            "check_id": self.check_id,
            "severity": self.severity.value,
            "status": self.status.value,
            "message": self.message,
            "details": dict(self.details),
        }


@dataclass(frozen=True, slots=True)
class IntegrityReport:
    """The deterministic aggregate of every constitutional-integrity check."""

    findings: tuple[IntegrityFinding, ...]
    records_examined: int
    evidence_examined: int

    @property
    def blocking_failures(self) -> tuple[str, ...]:
        return tuple(f.check_id for f in self.findings if f.is_blocking_failure)

    @property
    def advisory_failures(self) -> tuple[str, ...]:
        return tuple(
            f.check_id
            for f in self.findings
            if f.status is CriterionStatus.FAIL and not f.is_blocking_failure
        )

    @property
    def passed(self) -> bool:
        """Fail-closed: the report passes iff no *blocking* check failed."""
        return not self.blocking_failures

    def counts(self) -> dict[str, int]:
        passed = sum(1 for f in self.findings if f.passed)
        return {
            "total": len(self.findings),
            "passed": passed,
            "failed": len(self.findings) - passed,
            "blocking_failed": len(self.blocking_failures),
            "advisory_failed": len(self.advisory_failures),
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "report_format": INTEGRITY_REPORT_FORMAT,
            "verdict": "pass" if self.passed else "fail",
            "records_examined": self.records_examined,
            "evidence_examined": self.evidence_examined,
            "counts": self.counts(),
            "findings": [f.to_dict() for f in self.findings],
            "blocking_failures": list(self.blocking_failures),
        }


# ---------------------------------------------------------------------------
# append-only, dedup-aware register (fail-closed at registration time)
# ---------------------------------------------------------------------------
class CertificationRegister:
    """An append-only, dedup-aware register of ``(record, evidence)`` pairs.

    Registration is **fail-closed**:

        * an *identical* re-registration (same record hash + same evidence hash) is
          an idempotent no-op — so re-running a certification never grows the
          population (**zero duplicate certification / evidence**);
        * a *conflicting* duplicate raises :class:`DuplicateCertificationError`:
            a *different* certification for the same ``(target_id, version)`` subject.

    The register admits only integrity-sound, correctly-paired determinations: the
    record must pass :meth:`CertificationRecord.require_integrity`, and the evidence
    must reference it (matching ``certification_id`` and record hash). Because each
    certification carries exactly one evidence record and is registered at most
    once, duplicate *evidence* is impossible by construction; the batch
    :func:`verify_certification_integrity` additionally detects it over populations
    assembled elsewhere (e.g. loaded from a ledger).
    """

    __slots__ = (
        "_pairs",
        "_by_cert_id",
        "_subject_cert",
    )

    def __init__(self) -> None:
        self._pairs: list[tuple[CertificationRecord, CertificationEvidence]] = []
        self._by_cert_id: dict[str, str] = {}
        self._subject_cert: dict[tuple[str, str], str] = {}

    @property
    def records(self) -> tuple[CertificationRecord, ...]:
        return tuple(r for r, _ in self._pairs)

    @property
    def evidences(self) -> tuple[CertificationEvidence, ...]:
        return tuple(e for _, e in self._pairs)

    def __len__(self) -> int:
        return len(self._pairs)

    def _validate_pairing(
        self, record: CertificationRecord, evidence: CertificationEvidence
    ) -> None:
        record.require_integrity()
        if evidence.certification_id != record.certification_id:
            raise DuplicateCertificationError(
                "evidence does not belong to the record",
                certification_id=record.certification_id,
                evidence_certification_id=evidence.certification_id,
            )
        if evidence.record_sha256 != record.content_sha256:
            raise DuplicateCertificationError(
                "evidence record hash does not match the record",
                certification_id=record.certification_id,
                expected=record.content_sha256,
                actual=evidence.record_sha256,
            )

    def register(self, record: CertificationRecord, evidence: CertificationEvidence) -> bool:
        """Register a determination. Returns True if newly added, False on no-op.

        Raises:
            DuplicateCertificationError: on a conflicting duplicate (see class doc).
        """
        self._validate_pairing(record, evidence)

        cert_id = record.certification_id
        subject = (record.target_id, record.version)

        known = self._by_cert_id.get(cert_id)
        if known is not None:
            # A known certification_id is derived from (and validated against) the
            # record's content hash, so it necessarily denotes identical content —
            # an idempotent no-op (zero duplicate certification / evidence). Forged
            # records that share an id with different content are detected instead by
            # the batch verifier (record-integrity + no-duplicate-certification).
            _logger.info("certification.integrity.register.noop", certification_id=cert_id)
            return False

        prior_subject = self._subject_cert.get(subject)
        if prior_subject is not None and prior_subject != cert_id:
            raise DuplicateCertificationError(
                "subject already certified by a different certification",
                target_id=record.target_id,
                version=record.version,
                existing_certification_id=prior_subject,
                incoming_certification_id=cert_id,
            )

        self._pairs.append((record, evidence))
        self._by_cert_id[cert_id] = record.content_sha256
        self._subject_cert[subject] = cert_id
        _logger.info(
            "certification.integrity.register.added",
            certification_id=cert_id,
            target=record.target_id,
            version=record.version,
        )
        return True

    def verify(
        self,
        *,
        validation_evidence_index: Mapping[str, str] | None = None,
        expected_targets: Iterable[str] | None = None,
    ) -> IntegrityReport:
        """Run the full constitutional-integrity suite over this register."""
        return verify_certification_integrity(
            self.records,
            self.evidences,
            validation_evidence_index=validation_evidence_index,
            expected_targets=expected_targets,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "register_format": "ucos-certification-register/1.0.0",
            "count": len(self._pairs),
            "certification_ids": [r.certification_id for r, _ in self._pairs],
        }


# ---------------------------------------------------------------------------
# batch verifier (detection over an arbitrary population)
# ---------------------------------------------------------------------------
def _check_record_integrity(records: Sequence[CertificationRecord]) -> IntegrityFinding:
    tampered = [r.certification_id for r in records if not r.verify_integrity()]
    ok = not tampered
    return IntegrityFinding(
        check_id="record-integrity",
        severity=CriterionSeverity.BLOCKING,
        status=CriterionStatus.PASS if ok else CriterionStatus.FAIL,
        message=(
            f"{len(records)} record(s) content-hash intact"
            if ok
            else f"{len(tampered)} record(s) failed integrity"
        ),
        details={} if ok else {"tampered": sorted(tampered)},
    )


def _check_no_duplicate_certification(
    records: Sequence[CertificationRecord],
) -> IntegrityFinding:
    by_id: dict[str, set[str]] = defaultdict(set)
    by_subject: dict[tuple[str, str], set[str]] = defaultdict(set)
    for r in records:
        by_id[r.certification_id].add(r.content_sha256)
        by_subject[(r.target_id, r.version)].add(r.certification_id)
    id_conflicts = sorted(cid for cid, hashes in by_id.items() if len(hashes) > 1)
    subject_dups = sorted(f"{t}@{v}" for (t, v), ids in by_subject.items() if len(ids) > 1)
    ok = not id_conflicts and not subject_dups
    return IntegrityFinding(
        check_id="no-duplicate-certification",
        severity=CriterionSeverity.BLOCKING,
        status=CriterionStatus.PASS if ok else CriterionStatus.FAIL,
        message=("zero duplicate certification" if ok else "duplicate certification detected"),
        details=(
            {}
            if ok
            else {
                "id_content_conflicts": id_conflicts,
                "subjects_certified_more_than_once": subject_dups,
            }
        ),
    )


def _check_no_duplicate_evidence(
    evidences: Sequence[CertificationEvidence],
) -> IntegrityFinding:
    occurrences: dict[str, int] = defaultdict(int)
    owner: dict[str, str] = {}
    for e in evidences:
        digest = e.content_sha256()
        occurrences[digest] += 1
        owner.setdefault(digest, e.certification_id)
    duplicated = sorted(owner[h] for h, n in occurrences.items() if n > 1)
    ok = not duplicated
    return IntegrityFinding(
        check_id="no-duplicate-evidence",
        severity=CriterionSeverity.BLOCKING,
        status=CriterionStatus.PASS if ok else CriterionStatus.FAIL,
        message="zero duplicate evidence" if ok else "duplicate evidence detected",
        details={} if ok else {"duplicate_evidence_for": duplicated},
    )


def _check_no_overlapping_certification(
    records: Sequence[CertificationRecord],
) -> IntegrityFinding:
    certified_by_target: dict[str, set[str]] = defaultdict(set)
    for r in records:
        if r.status is CertificationStatus.CERTIFIED:
            certified_by_target[r.target_id].add(r.certification_id)
    overlaps = sorted(t for t, ids in certified_by_target.items() if len(ids) > 1)
    ok = not overlaps
    return IntegrityFinding(
        check_id="no-overlapping-certification",
        severity=CriterionSeverity.BLOCKING,
        status=CriterionStatus.PASS if ok else CriterionStatus.FAIL,
        message=(
            "no target carries overlapping certifications"
            if ok
            else "overlapping certifications detected"
        ),
        details={} if ok else {"targets_with_multiple_certified": overlaps},
    )


def _check_no_certification_drift(
    records: Sequence[CertificationRecord],
) -> IntegrityFinding:
    by_subject: dict[tuple[str, str], set[tuple[str, str]]] = defaultdict(set)
    for r in records:
        by_subject[(r.target_id, r.version)].add((r.content_sha256, r.status.value))
    drifted = sorted(f"{t}@{v}" for (t, v), variants in by_subject.items() if len(variants) > 1)
    ok = not drifted
    return IntegrityFinding(
        check_id="no-certification-drift",
        severity=CriterionSeverity.BLOCKING,
        status=CriterionStatus.PASS if ok else CriterionStatus.FAIL,
        message=(
            "same subject always yields an identical record"
            if ok
            else "certification drift detected"
        ),
        details={} if ok else {"subjects_with_divergent_records": drifted},
    )


def _check_evidence_traceability(
    records: Sequence[CertificationRecord],
    evidences: Sequence[CertificationEvidence],
    validation_evidence_index: Mapping[str, str] | None,
) -> IntegrityFinding:
    evidence_by_id: dict[str, CertificationEvidence] = {}
    orphan_evidence: list[str] = []
    for e in evidences:
        if e.certification_id in evidence_by_id:
            continue  # multiplicity is reported by the duplicate-evidence check
        evidence_by_id[e.certification_id] = e

    problems: list[str] = []
    for r in records:
        e = evidence_by_id.get(r.certification_id)
        if e is None:
            problems.append(f"{r.certification_id}: no evidence")
            continue
        if e.validation_evidence_ref != r.evidence_ref:
            problems.append(f"{r.certification_id}: validation-evidence chain broken")
        if validation_evidence_index is not None and r.evidence_ref:
            if r.evidence_ref not in validation_evidence_index:
                problems.append(f"{r.certification_id}: validation evidence not found")

    record_ids = {r.certification_id for r in records}
    for e in evidences:
        if e.certification_id not in record_ids:
            orphan_evidence.append(e.certification_id)

    ok = not problems and not orphan_evidence
    return IntegrityFinding(
        check_id="evidence-record-traceability",
        severity=CriterionSeverity.BLOCKING,
        status=CriterionStatus.PASS if ok else CriterionStatus.FAIL,
        message=(
            "every record traces to its evidence and validation chain"
            if ok
            else "traceability chain broken"
        ),
        details=(
            {}
            if ok
            else {
                "problems": sorted(problems),
                "orphan_evidence": sorted(set(orphan_evidence)),
            }
        ),
    )


def _check_completeness(
    records: Sequence[CertificationRecord],
    evidences: Sequence[CertificationEvidence],
    expected_targets: Iterable[str] | None,
) -> IntegrityFinding:
    evidence_by_id = {e.certification_id: e for e in evidences}
    incomplete: list[str] = []
    for r in records:
        if r.status is not CertificationStatus.CERTIFIED:
            continue
        if not r.evidence_ref:
            incomplete.append(f"{r.certification_id}: certified without validation evidence")
        e = evidence_by_id.get(r.certification_id)
        if e is None:
            incomplete.append(f"{r.certification_id}: certified without evidence record")
            continue
        if not e.certified or e.blocking_failures:
            incomplete.append(f"{r.certification_id}: certified evidence carries blocking failures")

    missing_targets: list[str] = []
    if expected_targets is not None:
        certified_targets = {
            r.target_id for r in records if r.status is CertificationStatus.CERTIFIED
        }
        missing_targets = sorted(set(expected_targets) - certified_targets)

    ok = not incomplete and not missing_targets
    return IntegrityFinding(
        check_id="certification-completeness",
        severity=CriterionSeverity.BLOCKING,
        status=CriterionStatus.PASS if ok else CriterionStatus.FAIL,
        message=(
            "every certified record is complete and every expected target covered"
            if ok
            else "certification completeness violated"
        ),
        details=(
            {}
            if ok
            else {
                "incomplete_certifications": sorted(incomplete),
                "uncertified_expected_targets": missing_targets,
            }
        ),
    )


def verify_certification_integrity(
    records: Sequence[CertificationRecord],
    evidences: Sequence[CertificationEvidence],
    *,
    validation_evidence_index: Mapping[str, str] | None = None,
    expected_targets: Iterable[str] | None = None,
) -> IntegrityReport:
    """Run every constitutional-integrity check over a certification population.

    Checks run in a stable id order and the report is deterministic: an identical
    population yields byte-identical findings. The verdict is **fail-closed** — the
    report passes iff no *blocking* check failed.
    """
    findings = (
        _check_record_integrity(records),
        _check_no_duplicate_certification(records),
        _check_no_duplicate_evidence(evidences),
        _check_no_overlapping_certification(records),
        _check_no_certification_drift(records),
        _check_evidence_traceability(records, evidences, validation_evidence_index),
        _check_completeness(records, evidences, expected_targets),
    )
    findings = tuple(sorted(findings, key=lambda f: f.check_id))
    report = IntegrityReport(
        findings=findings,
        records_examined=len(records),
        evidence_examined=len(evidences),
    )
    _logger.info(
        "certification.integrity.verified",
        records=len(records),
        evidence=len(evidences),
        verdict="pass" if report.passed else "fail",
        blocking_failed=len(report.blocking_failures),
    )
    return report


def enforce_integrity(report: IntegrityReport, *, strict: bool = True) -> IntegrityReport:
    """Fail-closed gate. Returns the report when it passes.

    Raises:
        ConstitutionalIntegrityError: when ``strict`` and the report has any
            blocking failure — carrying the exact failing check ids as evidence.
    """
    if strict and not report.passed:
        raise ConstitutionalIntegrityError(
            "constitutional certification integrity failed",
            blocking_failures=list(report.blocking_failures),
        )
    return report


# ---------------------------------------------------------------------------
# evidence generation
# ---------------------------------------------------------------------------
@dataclass(frozen=True, slots=True)
class IntegrityEvidence:
    """A deterministic, serializable evidence record for an integrity report."""

    verdict: str
    passed: bool
    records_examined: int
    evidence_examined: int
    checks_evaluated: tuple[str, ...]
    counts: Mapping[str, int]
    findings: tuple[dict[str, Any], ...]
    blocking_failures: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "evidence_format": INTEGRITY_EVIDENCE_FORMAT,
            "verdict": self.verdict,
            "passed": self.passed,
            "records_examined": self.records_examined,
            "evidence_examined": self.evidence_examined,
            "checks_evaluated": list(self.checks_evaluated),
            "counts": dict(self.counts),
            "findings": [dict(f) for f in self.findings],
            "blocking_failures": list(self.blocking_failures),
        }

    def content_sha256(self) -> str:
        return content_hash(self.to_dict())


def build_integrity_evidence(report: IntegrityReport) -> IntegrityEvidence:
    """Assemble a deterministic :class:`IntegrityEvidence` from a report."""
    return IntegrityEvidence(
        verdict="pass" if report.passed else "fail",
        passed=report.passed,
        records_examined=report.records_examined,
        evidence_examined=report.evidence_examined,
        checks_evaluated=tuple(f.check_id for f in report.findings),
        counts=report.counts(),
        findings=tuple(f.to_dict() for f in report.findings),
        blocking_failures=tuple(report.blocking_failures),
    )


__all__ = [
    "INTEGRITY_REPORT_FORMAT",
    "INTEGRITY_EVIDENCE_FORMAT",
    "DuplicateCertificationError",
    "ConstitutionalIntegrityError",
    "IntegrityFinding",
    "IntegrityReport",
    "CertificationRegister",
    "verify_certification_integrity",
    "enforce_integrity",
    "IntegrityEvidence",
    "build_integrity_evidence",
]
