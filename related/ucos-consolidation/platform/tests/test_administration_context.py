"""EC2-CAP-ADMIN-001 — Administrative context tests.

Covers the immutable, content-addressed administrative runtime context: deterministic
id, granted-action membership, the ``can_administer`` derivation, validation, and
serialization/fingerprint.
"""

from __future__ import annotations

from platform.administration.context import AdministrativeContext
from platform.administration.contracts import AdministrativeAction, AdministrativeScope
from platform.administration.errors import AdministrationContextError
from platform.foundation.identity import Principal, Role

import pytest


def _principal(subject="admin@x", tenant=None):
    return Principal.create(subject, [Role.PLATFORM_ADMINISTRATOR], tenant=tenant)


def test_context_is_deterministic_and_content_addressed():
    principal = _principal()
    actions = frozenset({AdministrativeAction.INSPECT, AdministrativeAction.CONFIGURE})
    a = AdministrativeContext.create(principal, AdministrativeScope.PLATFORM, actions)
    b = AdministrativeContext.create(principal, AdministrativeScope.PLATFORM, actions)
    assert a.context_id == b.context_id
    assert a.context_id.startswith("UCOS-ACTX-")
    assert a.fingerprint() == b.fingerprint()


def test_context_carries_principal_scope_and_actions():
    principal = _principal(tenant="acme")
    ctx = AdministrativeContext.create(
        principal,
        AdministrativeScope.TENANT,
        frozenset({AdministrativeAction.INSPECT}),
        tenant="acme",
    )
    assert ctx.principal_id == principal.principal_id
    assert ctx.subject == "admin@x"
    assert ctx.scope is AdministrativeScope.TENANT
    assert ctx.tenant == "acme"
    assert ctx.permits(AdministrativeAction.INSPECT)
    assert not ctx.permits(AdministrativeAction.CONFIGURE)


def test_can_administer_is_true_only_with_a_mutating_action():
    principal = _principal()
    inspect_only = AdministrativeContext.create(
        principal, AdministrativeScope.PLATFORM, frozenset({AdministrativeAction.INSPECT})
    )
    assert inspect_only.can_administer is False
    with_mutation = AdministrativeContext.create(
        principal,
        AdministrativeScope.PLATFORM,
        frozenset({AdministrativeAction.INSPECT, AdministrativeAction.ASSIGN}),
    )
    assert with_mutation.can_administer is True


def test_context_to_dict_is_serializable():
    ctx = AdministrativeContext.create(
        _principal(), AdministrativeScope.PLATFORM, frozenset({AdministrativeAction.INSPECT})
    )
    data = ctx.to_dict()
    assert data["scope"] == "platform"
    assert data["actions"] == ["inspect"]


def test_context_rejects_non_principal():
    with pytest.raises(AdministrationContextError):
        AdministrativeContext.create("nope", AdministrativeScope.PLATFORM, frozenset())  # type: ignore[arg-type]


def test_context_rejects_bad_scope():
    with pytest.raises(AdministrationContextError):
        AdministrativeContext.create(_principal(), "platform", frozenset())  # type: ignore[arg-type]


def test_context_rejects_bad_actions():
    with pytest.raises(AdministrationContextError):
        AdministrativeContext.create(
            _principal(),
            AdministrativeScope.PLATFORM,
            frozenset({"inspect"}),  # type: ignore[arg-type]
        )


def test_permits_rejects_non_action():
    ctx = AdministrativeContext.create(
        _principal(), AdministrativeScope.PLATFORM, frozenset({AdministrativeAction.INSPECT})
    )
    with pytest.raises(AdministrationContextError):
        ctx.permits("inspect")  # type: ignore[arg-type]
