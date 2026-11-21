"""UCOS-NUC-001 — FG-18-NUCLEUS-OWNS-CAPABILITY, driven into every one of its refusals.

The registry's constructor path refuses each of these states, which is the primary and
correct defence. The gate is the *second* defence: it measures a population that arrived
some other way — a hand-edited document, a legacy import, a future refactor that loosens
an admission check. A gate whose refusal branches have never executed offers no such
defence, so each invariant is forced here and asserted to be reported.

The forcing technique is the one ``test_gate_detects_a_layer_owned_capability`` already
uses: assemble lawfully through the public API, then overwrite the private structure with
the unlawful record. Nothing here tests the constructor — that is tested where it lives.
"""

from __future__ import annotations

import pytest

from engine.nucleus.errors import OwnershipViolation
from engine.nucleus.law import StructuralRole
from engine.nucleus.model import (
    CapabilityDeclaration,
    CapabilityRecord,
    OwnershipAssignment,
    SubjectDeclaration,
    SubjectRecord,
)
from engine.nucleus.ownership import enforce, gate
from engine.nucleus.registry import NucleusRegistry


def _population() -> NucleusRegistry:
    """A lawful two-nucleus, one-layer, one-composition, one-capability population."""
    fresh = NucleusRegistry()
    fresh.register_subject(SubjectDeclaration(key="payment", title="Payment", concept="payment"))
    fresh.register_subject(SubjectDeclaration(key="ledger", title="Ledger", concept="ledger"))
    fresh.register_subject(SubjectDeclaration(key="platform", title="Platform Layer"))
    fresh.register_subject(
        SubjectDeclaration(key="commerce", title="Commerce", composes=("payment", "ledger"))
    )
    fresh.register_capability(
        CapabilityDeclaration(key="payment.invoice", title="Invoice", owner="payment")
    )
    return fresh


def _replace_capability(registry: NucleusRegistry, key: str, **changes: object) -> None:
    record = registry.capability(key)
    fields = {
        "universal_id": record.universal_id,
        "key": record.key,
        "title": record.title,
        "owner_key": record.owner_key,
        "owner_id": record.owner_id,
        "namespace": record.namespace,
    }
    fields.update(changes)
    registry._capabilities[key] = CapabilityRecord(**fields)  # noqa: SLF001 - forced state


def _replace_subject(registry: NucleusRegistry, key: str, **changes: object) -> SubjectRecord:
    record = registry.subject(key)
    fields = {
        "universal_id": record.universal_id,
        "key": record.key,
        "title": record.title,
        "role": record.role,
        "namespace": record.namespace,
        "concept": record.concept,
        "composes": record.composes,
    }
    fields.update(changes)
    replacement = SubjectRecord(**fields)
    registry._subjects[(record.role.value, key)] = replacement  # noqa: SLF001 - forced state
    registry._by_id[replacement.universal_id] = (record.role.value, key)  # noqa: SLF001
    return replacement


def _assert_reports(registry: NucleusRegistry, invariant: str) -> None:
    report = enforce(registry)
    assert report.status == "FAIL"
    assert invariant in report.blocking_failures, report.blocking_failures
    assert report.measurements[invariant] >= 1
    assert any(finding.invariant_id == invariant for finding in report.findings)
    with pytest.raises(OwnershipViolation):
        gate(registry)


# --------------------------------------------------------------------------- #
# NUC-INV-01 / 02 / 03 — ownership resolves to exactly one nucleus             #
# --------------------------------------------------------------------------- #


def test_a_composition_owned_capability_is_refused():
    registry = _population()
    owner = registry.subject("commerce")
    _replace_capability(
        registry, "payment.invoice", owner_key=owner.key, owner_id=owner.universal_id
    )
    _assert_reports(registry, "NUC-INV-02")


def test_a_layer_owned_capability_is_refused():
    registry = _population()
    owner = registry.subject("platform")
    _replace_capability(
        registry, "payment.invoice", owner_key=owner.key, owner_id=owner.universal_id
    )
    _assert_reports(registry, "NUC-INV-01")


def test_an_owner_that_is_not_registered_is_refused():
    registry = _population()
    _replace_capability(registry, "payment.invoice", owner_id="UCOS-NUC-ffffffffffff")
    _assert_reports(registry, "NUC-INV-03")


def test_a_capability_with_no_assignment_is_refused():
    registry = _population()
    registry._assignments.clear()  # noqa: SLF001 - forced state
    _assert_reports(registry, "NUC-INV-03")


def test_two_concurrent_live_assignments_are_refused():
    registry = _population()
    capability = registry.capability("payment.invoice")
    owner = registry.subject("ledger")
    registry._assignments.append(  # noqa: SLF001 - forced state
        OwnershipAssignment(
            capability_id=capability.universal_id,
            capability_key=capability.key,
            owner_id=owner.universal_id,
            owner_key=owner.key,
            owner_role=StructuralRole.NUCLEUS,
            authority="FORCED",
        )
    )
    _assert_reports(registry, "NUC-INV-04")


# --------------------------------------------------------------------------- #
# NUC-INV-05 / 06 — declared role, record integrity, selections                #
# --------------------------------------------------------------------------- #


def test_a_declared_role_contradicting_the_derived_role_is_refused():
    registry = _population()
    _replace_subject(registry, "platform", concept="platform")
    _assert_reports(registry, "NUC-INV-05")


def test_a_record_that_does_not_reproduce_its_digest_is_refused():
    registry = _population()
    _replace_subject(registry, "payment", title="Tampered Title", content_hash="0" * 64)
    _assert_reports(registry, "NUC-INV-05")


def test_a_selection_that_is_not_a_registered_nucleus_is_refused():
    registry = _population()
    _replace_subject(registry, "commerce", composes=("payment", "absent"))
    _assert_reports(registry, "NUC-INV-06")


# --------------------------------------------------------------------------- #
# NUC-INV-08 — a capability may not be specific to a composition               #
# --------------------------------------------------------------------------- #


def test_a_capability_scoped_to_a_composition_is_refused():
    registry = _population()
    owner = registry.subject("payment")
    registry._capabilities["commerce.checkout"] = CapabilityRecord(  # noqa: SLF001
        universal_id=registry.capability("payment.invoice").universal_id.replace("a", "b"),
        key="commerce.checkout",
        title="Checkout",
        owner_key=owner.key,
        owner_id=owner.universal_id,
        namespace="ucos.capability",
    )
    report = enforce(registry)
    assert "NUC-INV-08" in report.blocking_failures


# --------------------------------------------------------------------------- #
# NUC-INV-09 — every identifier is well formed                                 #
# --------------------------------------------------------------------------- #


def test_a_subject_with_a_malformed_identifier_is_refused():
    registry = _population()
    _replace_subject(registry, "payment", universal_id="NOT-A-UCOS-ID")
    _assert_reports(registry, "NUC-INV-09")


def test_a_capability_with_a_malformed_identifier_is_refused():
    registry = _population()
    _replace_capability(registry, "payment.invoice", universal_id="NOT-A-UCOS-ID")
    _assert_reports(registry, "NUC-INV-09")


# --------------------------------------------------------------------------- #
# NUC-INV-10 — assignments name registered subjects                            #
# --------------------------------------------------------------------------- #


def test_an_assignment_naming_an_unregistered_owner_is_refused():
    registry = _population()
    capability = registry.capability("payment.invoice")
    registry._assignments[0] = OwnershipAssignment(  # noqa: SLF001 - forced state
        capability_id=capability.universal_id,
        capability_key=capability.key,
        owner_id="UCOS-NUC-ffffffffffff",
        owner_key="ghost",
        owner_role=StructuralRole.NUCLEUS,
        authority="FORCED",
    )
    _assert_reports(registry, "NUC-INV-10")


def test_an_assignment_naming_an_unregistered_capability_is_refused():
    registry = _population()
    owner = registry.subject("payment")
    registry._assignments[0] = OwnershipAssignment(  # noqa: SLF001 - forced state
        capability_id="UCOS-CAP-ffffffffffff",
        capability_key="payment.invoice",
        owner_id=owner.universal_id,
        owner_key=owner.key,
        owner_role=StructuralRole.NUCLEUS,
        authority="FORCED",
    )
    _assert_reports(registry, "NUC-INV-10")


# --------------------------------------------------------------------------- #
# The gate reports every violation, not the first                              #
# --------------------------------------------------------------------------- #


def test_the_gate_reports_every_violation_it_finds():
    registry = _population()
    _replace_subject(registry, "payment", universal_id="NOT-A-UCOS-ID")
    _replace_subject(registry, "commerce", composes=("payment", "absent"))
    report = enforce(registry)
    assert {"NUC-INV-06", "NUC-INV-09"} <= set(report.blocking_failures)
    assert len(report.findings) >= 2
    assert report.digest() == report.digest()
