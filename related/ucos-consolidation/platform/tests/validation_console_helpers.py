"""Shared test helpers for the EC2-EPIC-010 Validation Console runtime tests.

Not a test module (no ``test_`` prefix, not collected); lives under ``platform/tests``
so it is excluded from coverage. Provides deterministic :class:`ValidationSubject`
builders (accepted / accepted-with-advisories / rejected) and console fixtures reused
across the validation-console test suite.
"""

from __future__ import annotations

from platform.foundation.identity import Permission, Principal, Role
from platform.identity.contracts import CapabilityGroup
from platform.identity.roles import (
    RoleDefinition,
    RoleGrant,
    RoleRegistry,
    default_role_definitions,
)
from platform.identity.service import build_authorization_service
from platform.validation.service import build_validation_console_service

from engine.runtime.disclosure import build_disclosure
from engine.validation.contracts import ValidationSubject

_PKG = "a" * 64
_TARGET = "UCOS-RUN-data-0123456789abcdef"
_BLUEPRINT = "UCOS-BLPR-1"


def accepted_subject(
    *, target: str = _TARGET, blueprint: str = _BLUEPRINT, pkg: str = _PKG
) -> ValidationSubject:
    """A subject that passes every certified check (verdict PASS, no advisories)."""
    return ValidationSubject(
        target_id=target,
        blueprint_id=blueprint,
        provenance_chain=(blueprint, target),
        signature={"algorithm": "ed25519", "value": "sig", "payload_sha256": pkg},
        sbom={"sbom_format": "cyclonedx", "components": [{"name": "x"}]},
        dependency_closure=({"role": "root", "blueprint_id": blueprint, "package_sha256": pkg},),
        disclosure=build_disclosure(),
        package_sha256=pkg,
        image_reference=f"registry/img@sha256:{pkg}",
        runtime_id=target,
    )


def advisory_subject(
    *, target: str = _TARGET, blueprint: str = _BLUEPRINT, pkg: str = _PKG
) -> ValidationSubject:
    """A subject that passes every BLOCKING check but fails the ADVISORY identity check."""
    return ValidationSubject(
        target_id=target,
        blueprint_id=blueprint,
        provenance_chain=(blueprint, target),
        signature={"algorithm": "ed25519", "value": "sig", "payload_sha256": pkg},
        sbom={"sbom_format": "cyclonedx", "components": [{"name": "x"}]},
        dependency_closure=({"role": "root", "blueprint_id": blueprint, "package_sha256": pkg},),
        disclosure=build_disclosure(),
        package_sha256=pkg,
        image_reference=f"registry/img@sha256:{pkg}",
        runtime_id="not-a-deterministic-runtime-id",  # advisory identity check fails
    )


def rejected_subject(
    *, target: str = "UCOS-RUN-bad-badc0ffeebadc0ff", blueprint: str = "UCOS-BLPR-2"
) -> ValidationSubject:
    """A subject that fails BLOCKING checks (verdict FAIL, not accepted)."""
    return ValidationSubject(
        target_id=target,
        blueprint_id=blueprint,
        provenance_chain=(),  # blocking provenance failure
        signature={},
        sbom={},
        dependency_closure=(),
        disclosure=None,
        package_sha256="",
        image_reference="",
        runtime_id=None,
    )


def console_fixture(*, events=None, observability=None, authorization=None):
    """Build a Validation Console service with reusable identity/observability wiring."""
    auth = authorization or build_authorization_service(events=events)
    service = build_validation_console_service(
        authorization=auth, observability=observability, events=events
    )
    return auth, service


def session(auth, *, role=Role.ARCHITECT, subject="arch@x", tenant=None):
    """Establish a session for a principal bearing ``role``."""
    return auth.establish_session(
        Principal.create(subject, [role], tenant=tenant), issued_at=0, ttl=1000
    )


def authorization_without_validation_read():
    """An AuthorizationService whose OPERATOR role has no ``validation-explorer`` grant."""
    definitions = [d for d in default_role_definitions() if d.role is not Role.OPERATOR]
    definitions.append(RoleDefinition(role=Role.OPERATOR, grants={}))
    roles = RoleRegistry()
    roles.register_all(definitions)
    return build_authorization_service(roles=roles)


def authorization_with_validation_admin():
    """An AuthorizationService whose PLATFORM_ADMINISTRATOR holds ADMINISTER on the group."""
    definitions = [
        d for d in default_role_definitions() if d.role is not Role.PLATFORM_ADMINISTRATOR
    ]
    grants = {
        CapabilityGroup.VALIDATION_EXPLORER: RoleGrant(
            group=CapabilityGroup.VALIDATION_EXPLORER,
            permissions=frozenset({Permission.READ, Permission.CREATE, Permission.ADMINISTER}),
        ),
    }
    definitions.append(RoleDefinition(role=Role.PLATFORM_ADMINISTRATOR, grants=grants))
    roles = RoleRegistry()
    roles.register_all(definitions)
    return build_authorization_service(roles=roles)


__all__ = [
    "accepted_subject",
    "advisory_subject",
    "rejected_subject",
    "console_fixture",
    "session",
    "authorization_without_validation_read",
    "authorization_with_validation_admin",
]
