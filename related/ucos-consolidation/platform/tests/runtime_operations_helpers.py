"""Shared test helpers for the EC2-EPIC-012 Runtime Operations runtime tests.

Not a test module (no ``test_`` prefix, not collected); lives under ``platform/tests``
so it is excluded from coverage. Provides deterministic builders for an already-assembled
EC-1 :class:`~engine.runtime.assembly.RuntimeUnit` (constructed directly and stamped with
the EC-1 provisional-state disclosure, avoiding the heavyweight signed-package assembly
pipeline) and the governing certified / not-certified
:class:`~platform.certification.contracts.CertificationConsoleRecord`, plus runtime-service
fixtures reused across the runtime-operations test suite. It reuses the certified EC-1
validation + certification output through the EPIC-010/011 builders, so the fixtures
re-judge nothing (TP-01).
"""

from __future__ import annotations

from platform.certification.contracts import CertificationConsoleRecord
from platform.foundation.identity import Principal, Role
from platform.identity.roles import (
    RoleDefinition,
    RoleRegistry,
    default_role_definitions,
)
from platform.identity.service import build_authorization_service
from platform.runtime_operations.service import build_runtime_operations_service
from platform.tests.certification_console_helpers import (
    VERSION,
    certified_output,
    not_certified_output,
)

from engine.certification.contracts import CertificationSubject
from engine.certification.engine import CertificationEngine
from engine.certification.evidence import build_certification_evidence
from engine.runtime.assembly import DEFAULT_RESOURCES, ClosureEntry, RuntimeUnit
from engine.runtime.disclosure import inject_provisional_state

#: The default certified target/blueprint (must match the certification-console fixtures).
DEFAULT_RUNTIME_ID = "UCOS-RUN-data-0123456789abcdef"
DEFAULT_BLUEPRINT = "UCOS-BLPR-1"
DEFAULT_ARTIFACT = "UCOS-ART-000001"
DEFAULT_PKG = "a" * 64

#: The not-certified target/blueprint (matches ``not_certified_output`` rejected subject).
REJECTED_RUNTIME_ID = "UCOS-RUN-bad-badc0ffeebadc0ff"
REJECTED_BLUEPRINT = "UCOS-BLPR-2"


def runtime_unit(
    *,
    runtime_id: str = DEFAULT_RUNTIME_ID,
    blueprint: str = DEFAULT_BLUEPRINT,
    artifact: str = DEFAULT_ARTIFACT,
    version: str = VERSION,
    pkg: str = DEFAULT_PKG,
    environment: str = "runtime",
    with_disclosure: bool = True,
    with_package: bool = True,
    with_closure: bool = True,
    with_provenance: bool = True,
) -> RuntimeUnit:
    """Build a deterministic, already-assembled :class:`RuntimeUnit` (disclosure-stamped)."""
    package_sha256 = pkg if with_package else ""
    closure = (
        (
            ClosureEntry(
                blueprint_id=blueprint,
                artifact_id=artifact,
                package_sha256=pkg,
                role="root",
            ),
        )
        if with_closure
        else ()
    )
    provenance = (blueprint, runtime_id) if with_provenance else ()
    descriptor = {
        "runtime_descriptor_format": "ucos-runtime/1.0.0",
        "blueprint_id": blueprint,
        "artifact_id": artifact,
        "provenance": {"chain": list(provenance), "generation_framework": "ucos-ec1"},
    }
    unit = RuntimeUnit(
        runtime_id=runtime_id,
        blueprint_id=blueprint,
        artifact_id=artifact,
        name="data-service",
        version=version,
        package_sha256=package_sha256,
        provenance_chain=provenance,
        signature={"algorithm": "ed25519", "value": "sig", "payload_sha256": pkg},
        sbom={"sbom_format": "cyclonedx", "components": [{"name": "x"}]},
        dependency_closure=closure,
        secrets=(),
        resources=dict(DEFAULT_RESOURCES),
        descriptor=descriptor,
        environment=environment,
        disclosure=None,
    )
    return inject_provisional_state(unit) if with_disclosure else unit


def certification_record(validation_output=None, **kw) -> CertificationConsoleRecord:
    """Build a governing :class:`CertificationConsoleRecord` from certified validation output."""
    report, evidence = validation_output if validation_output is not None else certified_output()
    subject = CertificationSubject.from_validation(report, evidence, version=VERSION)
    decision = CertificationEngine().certify(subject)
    return CertificationConsoleRecord.create(
        report=report,
        validation_evidence=evidence,
        decision=decision,
        certification_evidence=build_certification_evidence(decision),
        owner_subject=kw.pop("owner_subject", "op@x"),
        **kw,
    )


def certified_unit_and_record(**kw):
    """A CERTIFIED runtime unit + its governing certified certification (aligned target)."""
    return runtime_unit(**kw), certification_record()


def not_certified_unit_and_record():
    """A runtime unit + a matching NOT-CERTIFIED certification (target aligned, certified=False)."""
    unit = runtime_unit(runtime_id=REJECTED_RUNTIME_ID, blueprint=REJECTED_BLUEPRINT)
    cert = certification_record(not_certified_output())
    return unit, cert


def service_fixture(*, events=None, observability=None, authorization=None):
    """Build a Runtime Operations service with reusable identity/observability wiring."""
    auth = authorization or build_authorization_service(events=events)
    service = build_runtime_operations_service(
        authorization=auth, observability=observability, events=events
    )
    return auth, service


def session(auth, *, role=Role.PLATFORM_ADMINISTRATOR, subject="admin@x", tenant=None):
    """Establish a session for a principal bearing ``role`` (default: admin — EXECUTE+READ)."""
    return auth.establish_session(
        Principal.create(subject, [role], tenant=tenant), issued_at=0, ttl=1000
    )


def authorization_without_runtime_grant():
    """An AuthorizationService whose OPERATOR role has no ``runtime-operations`` grant."""
    from platform.identity.contracts import CapabilityGroup

    definitions = [d for d in default_role_definitions() if d.role is not Role.OPERATOR]
    grants = {
        g: grant
        for g, grant in _grants_for(Role.OPERATOR).items()
        if g is not CapabilityGroup.RUNTIME_OPERATIONS
    }
    definitions.append(RoleDefinition(role=Role.OPERATOR, grants=grants))
    roles = RoleRegistry()
    roles.register_all(definitions)
    return build_authorization_service(roles=roles)


def _grants_for(role: Role) -> dict:
    for definition in default_role_definitions():
        if definition.role is role:
            return dict(definition.grants)
    return {}


__all__ = [
    "VERSION",
    "DEFAULT_RUNTIME_ID",
    "DEFAULT_BLUEPRINT",
    "DEFAULT_ARTIFACT",
    "DEFAULT_PKG",
    "REJECTED_RUNTIME_ID",
    "REJECTED_BLUEPRINT",
    "runtime_unit",
    "certification_record",
    "certified_unit_and_record",
    "not_certified_unit_and_record",
    "service_fixture",
    "session",
    "authorization_without_runtime_grant",
]
