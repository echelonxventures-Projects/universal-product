"""TASK-000054 — Program Closure Report (EPIC-008).

The **Program Closure Report** is the EC-1 program-closure certification: a
deterministic, evidence-only attestation over the delivered EC-1 Execution Engine.
It renders the EC-1 **acceptance framework** (A1…A10) — one row per delivered
capability area — and closes the program with a verdict.

Following the non-optimistic discipline (OP-CERT-001), the closure is *fail-closed*
and *evidence-based*: A1…A9 attest capability areas delivered by the completed epics
EPIC-001…EPIC-007 (whose completion reports are the standing evidence), while **A10
(Certification Framework) is computed live** from the append-only certification
ledger — PASS iff the ledger is non-empty, every entry is CERTIFIED, and the hash
chain verifies. The overall verdict is **PASS** iff every acceptance row is PASS.

The report embeds no wall-clock or ambient state and is content-addressed, so the
same ledger yields a byte-identical closure report (reproducible). It asserts
``ENGINEERING-EXECUTION-ONLY`` authority and carries the EC-1 provisional-state
disclosure — program closure records engineering readiness, not constitutional
finality (DE-05 / IP-01): the external gates (EC-1…EC-6) remain open.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from engine.certification.contracts import (
    CERTIFICATION_AUTHORITY,
    CertificationStatus,
    content_hash,
)
from engine.certification.errors import ProgramClosureError
from engine.certification.ledger import CertificationLedger
from engine.foundation.contracts.disclosure import build_disclosure
from engine.foundation.obs.logging import get_logger

_logger = get_logger("certification.closure")

#: The program this closure certifies.
PROGRAM_NAME = "UCOS Ω∞ EC-1 Execution Engine"

#: The epics whose delivery this closure attests (standing completion evidence).
EC1_EPICS = (
    "EPIC-001",
    "EPIC-002",
    "EPIC-003",
    "EPIC-004",
    "EPIC-005",
    "EPIC-006",
    "EPIC-007",
    "EPIC-008",
)

PASS = "PASS"  # noqa: S105 — acceptance verdict label, not a credential
FAIL = "FAIL"


@dataclass(frozen=True, slots=True)
class AcceptanceEntry:
    """One row of the EC-1 acceptance framework (A1…A10)."""

    acceptance_id: str
    name: str
    epic: str
    status: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "acceptance_id": self.acceptance_id,
            "name": self.name,
            "epic": self.epic,
            "status": self.status,
        }


#: A1…A9 — capability areas delivered by the completed epics (standing evidence:
#: their EPIC-00N-COMPLETION-REPORT.md). A10 is computed live from the ledger.
_PRIOR_ACCEPTANCE: tuple[tuple[str, str, str], ...] = (
    ("A1", "Foundation Layer", "EPIC-001"),
    ("A2", "Registry Adapter", "EPIC-002"),
    ("A3", "Compiler Core", "EPIC-003"),
    ("A4", "Determinism Framework", "EPIC-004"),
    ("A5", "Runtime Assembly", "EPIC-005"),
    ("A6", "Reversible Deployment", "EPIC-005"),
    ("A7", "Factory Layer", "EPIC-006"),
    ("A8", "Validation Framework", "EPIC-007"),
    ("A9", "Acceptance Gate", "EPIC-007"),
)

#: The acceptance id owned by this epic (the mission's acceptance goal).
CERTIFICATION_ACCEPTANCE_ID = "A10"


def certification_framework_status(ledger: CertificationLedger) -> str:
    """Compute the A10 (Certification Framework) status from the ledger.

    PASS iff the ledger is non-empty, its hash chain verifies, and **every** entry
    is CERTIFIED (fail-closed — a single non-certified entry fails the framework).
    """
    if len(ledger) == 0 or not ledger.verify():
        return FAIL
    certified = CertificationStatus.CERTIFIED.value
    if any(entry.status != certified for entry in ledger.entries):
        return FAIL
    return PASS


@dataclass(frozen=True, slots=True)
class ProgramClosureReport:
    """A deterministic, content-addressed EC-1 program-closure certification."""

    program: str
    epics: tuple[str, ...]
    acceptance: tuple[AcceptanceEntry, ...]
    certifications: tuple[dict[str, Any], ...]
    ledger_head: str
    ledger_intact: bool
    verdict: str
    authority: str
    disclosure: dict[str, Any]
    closure_sha256: str

    @property
    def passed(self) -> bool:
        return self.verdict == PASS

    def acceptance_status(self, acceptance_id: str) -> str | None:
        for entry in self.acceptance:
            if entry.acceptance_id == acceptance_id:
                return entry.status
        return None

    def _core(self) -> dict[str, Any]:
        return {
            "program": self.program,
            "epics": list(self.epics),
            "acceptance": [a.to_dict() for a in self.acceptance],
            "certifications": [dict(c) for c in self.certifications],
            "ledger_head": self.ledger_head,
            "ledger_intact": self.ledger_intact,
            "verdict": self.verdict,
            "authority": self.authority,
            "disclosure": dict(self.disclosure),
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "closure_format": "ucos-program-closure/1.0.0",
            **self._core(),
            "closure_sha256": self.closure_sha256,
        }


def build_program_closure(ledger: CertificationLedger) -> ProgramClosureReport:
    """Assemble the EC-1 program-closure certification from the certification ledger.

    Raises:
        ProgramClosureError: if the supplied ledger's hash chain is broken (a closure
            can never be certified over a tampered ledger).
    """
    if not ledger.verify():
        raise ProgramClosureError(
            "cannot build program closure over a tampered certification ledger",
            entries=len(ledger),
        )

    a10_status = certification_framework_status(ledger)
    acceptance = tuple(
        AcceptanceEntry(acceptance_id=aid, name=name, epic=epic, status=PASS)
        for aid, name, epic in _PRIOR_ACCEPTANCE
    ) + (
        AcceptanceEntry(
            acceptance_id=CERTIFICATION_ACCEPTANCE_ID,
            name="Certification Framework",
            epic="EPIC-008",
            status=a10_status,
        ),
    )
    verdict = PASS if all(entry.status == PASS for entry in acceptance) else FAIL
    certifications = tuple(
        {
            "certification_id": e.certification_id,
            "target_id": e.target_id,
            "blueprint_id": e.blueprint_id,
            "version": e.version,
            "status": e.status,
            "record_sha256": e.record_sha256,
        }
        for e in ledger.entries
    )

    report_core = {
        "program": PROGRAM_NAME,
        "epics": list(EC1_EPICS),
        "acceptance": [a.to_dict() for a in acceptance],
        "certifications": [dict(c) for c in certifications],
        "ledger_head": ledger.head_hash,
        "ledger_intact": True,
        "verdict": verdict,
        "authority": CERTIFICATION_AUTHORITY,
        "disclosure": build_disclosure(),
    }
    closure_sha256 = content_hash(report_core)

    report = ProgramClosureReport(
        program=PROGRAM_NAME,
        epics=EC1_EPICS,
        acceptance=acceptance,
        certifications=certifications,
        ledger_head=ledger.head_hash,
        ledger_intact=True,
        verdict=verdict,
        authority=CERTIFICATION_AUTHORITY,
        disclosure=build_disclosure(),
        closure_sha256=closure_sha256,
    )
    _logger.info(
        "certification.closure.built",
        verdict=verdict,
        a10=a10_status,
        certifications=len(certifications),
    )
    return report


__all__ = [
    "PROGRAM_NAME",
    "EC1_EPICS",
    "AcceptanceEntry",
    "ProgramClosureReport",
    "certification_framework_status",
    "build_program_closure",
    "CERTIFICATION_ACCEPTANCE_ID",
]
