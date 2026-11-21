"""UCOS-NUC-001 Part 05 — FG-18-NUCLEUS-OWNS-CAPABILITY, the ownership gate (D-07, D-20).

The registry refuses violations at admission. This gate answers the different question a
CI job asks: *given a whole registry, is the ownership law satisfied right now?* It is
needed because a registry can also be built by loading declarations that bypassed the
constructor path (a hand-edited document, a legacy import, a future migration), and
because AC-012 requires the invariants to be **measured**, not merely enforced.

The gate measures every invariant in :data:`engine.nucleus.law.OWNERSHIP_INVARIANTS`,
reports a count per invariant and a finding per violation, and is **fail-closed**: any
blocking invariant above zero yields ``FAIL``. It names no nucleus, no layer, no
composition and no domain, so it measures a population it has never seen before without
modification.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from engine.nucleus import authority
from engine.nucleus.law import LAW_ID, OWNERSHIP_INVARIANTS, StructuralRole
from engine.nucleus.model import derive_role
from engine.nucleus.registry import NucleusRegistry
from engine.registry.universal.identity import is_well_formed
from engine.uckp.canonical import content_hash

#: The identity of the gate this module realises.
GATE_ID = "FG-18-NUCLEUS-OWNS-CAPABILITY"


@dataclass(frozen=True, slots=True)
class Finding:
    """One measured violation, attributed to the clause and invariant it breaks."""

    invariant_id: str
    clause_id: str
    subject: str
    detail: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "invariant_id": self.invariant_id,
            "clause_id": self.clause_id,
            "subject": self.subject,
            "detail": self.detail,
        }


@dataclass(frozen=True, slots=True)
class OwnershipReport:
    """The gate's verdict: per-invariant counts, findings, and a fail-closed status."""

    gate_id: str
    law_id: str
    measurements: Mapping[str, int]
    findings: tuple[Finding, ...]
    counts: Mapping[str, int]

    @property
    def blocking_failures(self) -> tuple[str, ...]:
        """Blocking invariants measured above zero, ordered."""
        blocking = {i.invariant_id for i in OWNERSHIP_INVARIANTS if i.blocking}
        return tuple(
            sorted(inv for inv, value in self.measurements.items() if inv in blocking and value > 0)
        )

    @property
    def passed(self) -> bool:
        """True iff every blocking invariant measured zero."""
        return not self.blocking_failures

    @property
    def status(self) -> str:
        return "PASS" if self.passed else "FAIL"

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "ucos-nucleus-ownership-gate",
            "version": "1.0.0",
            "gate_id": self.gate_id,
            "law_id": self.law_id,
            "status": self.status,
            "measurements": {k: self.measurements[k] for k in sorted(self.measurements)},
            "blocking_failures": list(self.blocking_failures),
            "findings": [f.to_dict() for f in self.findings],
            "population": {k: self.counts[k] for k in sorted(self.counts)},
            "invariants": [i.to_dict() for i in OWNERSHIP_INVARIANTS],
        }

    def digest(self) -> str:
        return content_hash(self.to_dict())


#: Which invariant an ownership refusal is *reported* under, per role. This is a
#: reporting projection, not an ownership rule: whether the refusal happens at all has
#: already been decided by the ownership authority. A role with no entry is reported
#: under the general NUC-INV-03, so an unmapped role is still refused.
_INVARIANT_FOR_ROLE: Mapping[str, str] = {
    StructuralRole.LAYER.value: "NUC-INV-01",
    StructuralRole.COMPOSITION.value: "NUC-INV-02",
}

#: Invariant → the clause it enforces. DATA, so a new invariant is one tuple entry.
_INVARIANT_CLAUSES: Mapping[str, str] = {
    "NUC-INV-01": "NL-02",
    "NUC-INV-02": "NL-03",
    "NUC-INV-03": "NL-04",
    "NUC-INV-04": "NL-04",
    "NUC-INV-05": "NL-06",
    "NUC-INV-06": "NL-08",
    "NUC-INV-07": "NL-08",
    "NUC-INV-08": "NL-07",
    "NUC-INV-09": "NL-09",
    "NUC-INV-10": "NL-10",
}


def enforce(registry: NucleusRegistry) -> OwnershipReport:
    """Measure every ownership invariant over ``registry`` and return the verdict."""
    findings: list[Finding] = []
    measurements: dict[str, int] = {i.invariant_id: 0 for i in OWNERSHIP_INVARIANTS}

    def record(invariant_id: str, subject: str, detail: str) -> None:
        measurements[invariant_id] += 1
        findings.append(
            Finding(
                invariant_id=invariant_id,
                clause_id=_INVARIANT_CLAUSES[invariant_id],
                subject=subject,
                detail=detail,
            )
        )

    # Indexed by identity, not by key: a layer and a nucleus may share a name, and a
    # key-indexed map would silently drop one of them and so under-report violations.
    subjects = {s.universal_id: s for s in registry.subjects()}
    composition_keys = {s.key for s in registry.compositions()}

    # NUC-INV-01/02/03/04 — ownership resolves to exactly one nucleus.
    for capability in registry.capabilities():
        owner = subjects.get(capability.owner_id)
        if owner is None:
            record(
                "NUC-INV-03",
                capability.key,
                f"owner id {capability.owner_id!r} is not a registered subject",
            )
        elif not owner.may_own_capability:
            # The *decision* comes from the one ownership authority (CEU, via
            # `SubjectRecord.may_own_capability`). The role only selects which invariant
            # the finding is attributed to, which is reporting rather than adjudication —
            # so a role the CEU registry has not granted ownership is refused here even if
            # no invariant is specific to it.
            record(
                _INVARIANT_FOR_ROLE.get(owner.role.value, "NUC-INV-03"),
                capability.key,
                f"owned by {owner.role.value} {owner.key!r}, which the ownership "
                f"authority does not grant the {authority.FACULTY_OWN_CAPABILITY} faculty",
            )
        current = registry.assignments(capability_key=capability.key)
        live = [a for a in current if a.supersedes is None]
        if not current:
            record("NUC-INV-03", capability.key, "no ownership assignment recorded")
        elif len(live) > 1:
            record(
                "NUC-INV-04",
                capability.key,
                f"{len(live)} concurrent ownership assignments that supersede nothing",
            )
        # NUC-INV-08 — a capability may not be specific to a composition.
        domain = capability.key.split(".", 1)[0]
        if domain in composition_keys:
            record(
                "NUC-INV-08",
                capability.key,
                f"capability domain {domain!r} resolves to a composition",
            )

    nucleus_keys = {s.key for s in registry.nuclei()}

    # NUC-INV-05 — declared role agrees with the derived role, and the record is intact.
    for subject in subjects.values():
        # The classification rule has exactly one implementation
        # (engine.nucleus.model.derive_role). This gate *measures agreement* with that
        # rule; it does not hold a second copy of it, so a change to NL-06 cannot leave
        # the gate measuring the retired rule.
        derived = derive_role(subject)
        if derived is not subject.role:
            record(
                "NUC-INV-05",
                subject.key,
                f"declared role {subject.role.value!r} contradicts derived {derived.value!r}",
            )
        if not subject.is_intact():
            record(
                "NUC-INV-05",
                subject.key,
                "record does not reproduce its own identity or content digest",
            )
        # NUC-INV-06 — every selection resolves, and resolves to a nucleus.
        for selected in subject.composes:
            if selected not in nucleus_keys:
                record(
                    "NUC-INV-06",
                    subject.key,
                    f"selects {selected!r}, which is not a registered nucleus",
                )
        # NUC-INV-09 — every subject carries a well-formed universal identifier.
        if not is_well_formed(subject.universal_id):
            record("NUC-INV-09", subject.key, "universal identifier is not well formed")

    for capability in registry.capabilities():
        if not is_well_formed(capability.universal_id):
            record("NUC-INV-09", capability.key, "universal identifier is not well formed")

    # NUC-INV-07 — no cycle in the selection graph.
    for vertex in registry.selection_cycles():
        record("NUC-INV-07", vertex, "subject lies on a cycle in the selection graph")

    # NUC-INV-10 — no assignment names an unregistered subject.
    known_ids = set(subjects)
    capability_ids = {c.universal_id for c in registry.capabilities()}
    for assignment in registry.assignments():
        if assignment.owner_id not in known_ids:
            record(
                "NUC-INV-10",
                assignment.capability_key,
                f"assignment names unregistered owner id {assignment.owner_id!r}",
            )
        if assignment.capability_id not in capability_ids:
            record(
                "NUC-INV-10",
                assignment.capability_key,
                f"assignment names unregistered capability id {assignment.capability_id!r}",
            )

    return OwnershipReport(
        gate_id=GATE_ID,
        law_id=LAW_ID,
        measurements=measurements,
        findings=tuple(findings),
        counts=registry.counts(),
    )


def gate(registry: NucleusRegistry) -> OwnershipReport:
    """Run the gate and raise if it fails — the fail-closed CI entry point.

    Raises:
        OwnershipViolation: one or more blocking invariants measured above zero.
    """
    report = enforce(registry)
    if not report.passed:
        from engine.nucleus.errors import OwnershipViolation

        raise OwnershipViolation(
            "the nucleus ownership gate failed",
            gate_id=GATE_ID,
            blocking_failures=list(report.blocking_failures),
            findings=[f.to_dict() for f in report.findings],
        )
    return report


__all__ = ["GATE_ID", "Finding", "OwnershipReport", "enforce", "gate"]
