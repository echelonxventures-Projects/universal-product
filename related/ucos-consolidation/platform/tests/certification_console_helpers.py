"""Shared test helpers for the EC2-EPIC-011 Certification Console runtime tests.

Not a test module (no ``test_`` prefix, not collected); lives under ``platform/tests``
so it is excluded from coverage. Provides deterministic certified / certified-with-
advisories / not-certified validation-output builders (a ``ValidationReport`` +
``ValidationEvidence`` pair the certified certification engine aggregates) and console
fixtures reused across the certification-console test suite. It reuses the certified
EC-1 validation output through the EPIC-010 validation subject builders, so the
certification fixtures re-judge nothing (TP-01).
"""

from __future__ import annotations

from platform.certification.service import build_certification_console_service
from platform.foundation.identity import Permission, Principal, Role
from platform.identity.contracts import CapabilityGroup
from platform.identity.roles import (
    RoleDefinition,
    RoleGrant,
    RoleRegistry,
    default_role_definitions,
)
from platform.identity.service import build_authorization_service
from platform.tests.validation_console_helpers import (
    accepted_subject,
    advisory_subject,
    rejected_subject,
)

from engine.validation.evidence import build_validation_evidence
from engine.validation.executor import ValidationEngine

#: The default version pin every fixture certifies against.
VERSION = "1.0.0"


def _validation_output(subject):
    """Reproduce the certified validation report + evidence for a subject (read-only)."""
    report = ValidationEngine().validate(subject)
    return report, build_validation_evidence(report)


def certified_output(**kw):
    """Validated output that certifies (CERTIFIED, no advisory failure)."""
    return _validation_output(accepted_subject(**kw))


def advisory_output(**kw):
    """Validated output that certifies with an advisory failure (CERTIFIED_WITH_ADVISORIES)."""
    return _validation_output(advisory_subject(**kw))


def not_certified_output(**kw):
    """Validated output that does not certify (NOT_CERTIFIED — blocking failure)."""
    return _validation_output(rejected_subject(**kw))


def console_fixture(*, events=None, observability=None, authorization=None):
    """Build a Certification Console service with reusable identity/observability wiring."""
    auth = authorization or build_authorization_service(events=events)
    service = build_certification_console_service(
        authorization=auth, observability=observability, events=events
    )
    return auth, service


def session(auth, *, role=Role.ARCHITECT, subject="arch@x", tenant=None):
    """Establish a session for a principal bearing ``role``."""
    return auth.establish_session(
        Principal.create(subject, [role], tenant=tenant), issued_at=0, ttl=1000
    )


def authorization_without_certification_read():
    """An AuthorizationService whose OPERATOR role has no ``certification-ledger`` grant."""
    definitions = [d for d in default_role_definitions() if d.role is not Role.OPERATOR]
    definitions.append(RoleDefinition(role=Role.OPERATOR, grants={}))
    roles = RoleRegistry()
    roles.register_all(definitions)
    return build_authorization_service(roles=roles)


def authorization_with_certification_admin():
    """An AuthorizationService whose PLATFORM_ADMINISTRATOR holds ADMINISTER on the group."""
    definitions = [
        d for d in default_role_definitions() if d.role is not Role.PLATFORM_ADMINISTRATOR
    ]
    grants = {
        CapabilityGroup.CERTIFICATION_LEDGER: RoleGrant(
            group=CapabilityGroup.CERTIFICATION_LEDGER,
            permissions=frozenset({Permission.READ, Permission.ADMINISTER}),
        ),
    }
    definitions.append(RoleDefinition(role=Role.PLATFORM_ADMINISTRATOR, grants=grants))
    roles = RoleRegistry()
    roles.register_all(definitions)
    return build_authorization_service(roles=roles)


__all__ = [
    "VERSION",
    "certified_output",
    "advisory_output",
    "not_certified_output",
    "console_fixture",
    "session",
    "authorization_without_certification_read",
    "authorization_with_certification_admin",
]
