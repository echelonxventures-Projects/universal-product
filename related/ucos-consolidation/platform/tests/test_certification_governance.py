"""EC2-EPIC-011 — certification console governance tests.

Asserts the governance invariants of the additive, read-only console: it reuses the
pre-existing ``certification-ledger`` capability group (no new authority), consumes
``engine.certification`` by reference (binds the certified contract, redefines no
criterion/verdict/ledger-rule), exposes no mutation path to any certification datum or
ledger entry, refuses cross-tenant access (P3), and — the certification-specific
invariant — the certified Identity policy denies every mutation of the append-only
certification ledger (§3.2 invariant ii).
"""

from __future__ import annotations

import platform.certification as certification_pkg
from platform.certification.contracts import (
    CERTIFICATION_CONSOLE_GROUP,
    ENGINE_CERTIFICATION_CONTRACT,
    CertificationAction,
    permission_for,
)
from platform.certification.errors import CertificationAccessError
from platform.certification.service import CertificationConsoleService
from platform.foundation.contracts import ENGINE_CONTRACTS
from platform.foundation.identity import Permission, Principal, Role
from platform.identity.contracts import CapabilityGroup, all_capability_groups
from platform.identity.service import build_authorization_service
from platform.tests.certification_console_helpers import (
    certified_output,
    console_fixture,
    session,
)

import pytest


def test_reuses_pre_existing_capability_group_no_new_authority():
    assert CERTIFICATION_CONSOLE_GROUP is CapabilityGroup.CERTIFICATION_LEDGER
    assert CapabilityGroup.CERTIFICATION_LEDGER in all_capability_groups()


def test_every_console_action_is_read_only():
    for action in CertificationAction:
        assert permission_for(action) is Permission.READ


def test_consumes_engine_certification_by_reference():
    assert ENGINE_CERTIFICATION_CONTRACT == "engine.certification.certify"
    assert any(ref.name == ENGINE_CERTIFICATION_CONTRACT for ref in ENGINE_CONTRACTS)


def test_no_duplicate_certification_engine_symbols_exported():
    exported = set(certification_pkg.__all__)
    forbidden = {
        "CertificationEngine",
        "CertificationCriterion",
        "default_criteria",
        "certify_validation",
        "build_certification_evidence",
        "CertificationLedger",
    }
    assert exported.isdisjoint(forbidden)


def test_no_mutation_verbs_exposed_on_service():
    banned = {
        "authorize",
        "ratify",
        "enact",
        "grant",
        "govern",
        "override",
        "mutate",
        "delete",
        "update_record",
        "edit",
        "append",
    }
    surface = {name for name in dir(CertificationConsoleService) if not name.startswith("_")}
    assert surface.isdisjoint(banned)


def test_cross_tenant_access_refused():
    auth, service = console_fixture()
    owner = session(auth, subject="arch@x", tenant="beta")
    report, evidence = certified_output()
    rec = service.surface_certification(
        owner.session_id, report, evidence, now=1, version="1.0.0", tenant="beta"
    )
    intruder = session(auth, subject="x@x", tenant="acme")
    with pytest.raises(CertificationAccessError):
        service.trace(intruder.session_id, rec.record_id, now=2)


@pytest.mark.parametrize(
    "permission",
    [Permission.CREATE, Permission.EXECUTE, Permission.ADMINISTER],
)
def test_certification_ledger_is_append_only_policy_denies_mutation(permission):
    # The certified Identity policy denies every mutation of the certification ledger,
    # regardless of any grant (§3.2 invariant ii) — the console can add no mutation path.
    auth = build_authorization_service()
    principal = Principal.create("admin@x", [Role.PLATFORM_ADMINISTRATOR])
    decision = auth.authorize_principal(principal, CapabilityGroup.CERTIFICATION_LEDGER, permission)
    assert decision.permitted is False
    assert decision.reason == "certification-ledger-append-only"
