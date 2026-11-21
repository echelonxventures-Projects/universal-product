"""EC2-EPIC-010 — validation console governance tests.

Asserts the governance invariants of the additive, read-only console: it reuses the
pre-existing ``validation-explorer`` capability group (no new authority), consumes
``engine.validation`` by reference (binds the certified contract, redefines no
check/verdict/gate), exposes no mutation path to any validation datum, and refuses
cross-tenant access (P3).
"""

from __future__ import annotations

import platform.validation as validation_pkg
from platform.foundation.contracts import ENGINE_CONTRACTS
from platform.foundation.identity import Permission
from platform.identity.contracts import CapabilityGroup, all_capability_groups
from platform.tests.validation_console_helpers import (
    accepted_subject,
    console_fixture,
    session,
)
from platform.validation.contracts import (
    ENGINE_VALIDATION_CONTRACT,
    VALIDATION_CONSOLE_GROUP,
    ValidationAction,
    permission_for,
)
from platform.validation.errors import ValidationAccessError
from platform.validation.service import ValidationConsoleService

import pytest


def test_reuses_pre_existing_capability_group_no_new_authority():
    # The group must already exist in the certified Identity Layer (no new group).
    assert VALIDATION_CONSOLE_GROUP is CapabilityGroup.VALIDATION_EXPLORER
    assert CapabilityGroup.VALIDATION_EXPLORER in all_capability_groups()


def test_every_console_action_is_read_only():
    # No console verb requires anything beyond READ (no create/execute/administer path).
    for action in ValidationAction:
        assert permission_for(action) is Permission.READ


def test_consumes_engine_validation_by_reference():
    # The certified engine.validation contract is bound (by reference), and it is the
    # one already published in ENGINE_CONTRACTS — the console adds no new engine contract.
    assert ENGINE_VALIDATION_CONTRACT == "engine.validation.validate"
    assert any(ref.name == ENGINE_VALIDATION_CONTRACT for ref in ENGINE_CONTRACTS)


def test_no_duplicate_validation_engine_symbols_exported():
    # The console re-exports the frozen engine vocabulary but defines no check/gate/engine.
    exported = set(validation_pkg.__all__)
    forbidden = {
        "ValidationEngine",
        "ValidationCheck",
        "default_checks",
        "enforce_acceptance",
        "build_validation_evidence",
    }
    assert exported.isdisjoint(forbidden)


def test_no_mutation_verbs_exposed_on_service():
    # The service surface exposes no authorize/ratify/enact/grant/govern/override or
    # write verb over validation data (read/inspection-only console).
    banned = {
        "authorize",
        "ratify",
        "enact",
        "grant",
        "govern",
        "override",
        "mutate",
        "delete",
        "update_report",
        "edit",
    }
    surface = {name for name in dir(ValidationConsoleService) if not name.startswith("_")}
    assert surface.isdisjoint(banned)


def test_cross_tenant_access_refused():
    auth, service = console_fixture()
    owner = session(auth, subject="arch@x", tenant="beta")
    rec = service.surface_validation(owner.session_id, accepted_subject(), now=1, tenant="beta")
    intruder = session(auth, subject="x@x", tenant="acme")
    with pytest.raises(ValidationAccessError):
        service.trace(intruder.session_id, rec.record_id, now=2)
