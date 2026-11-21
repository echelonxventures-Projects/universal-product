"""UPA-000011 — Provider Framework façade (Terminal-04).

One object that wires the whole Universal Provider Architecture together and runs the
onboarding pipeline end to end:

    discover → admit (register + lifecycle) → instantiate → validate → certify → activate

    * :class:`OnboardingResult` — the deterministic outcome for one provider.
    * :class:`ProviderFramework` — the façade over registry, discovery, lifecycle,
      validation, certification, and composition.

The pipeline is the executable form of PC-11: :meth:`ProviderFramework.activate`
refuses any provider whose latest certificate does not authorize activation, and the
lifecycle has no edge into ``ACTIVE`` that bypasses ``CERTIFIED``. A provider declared
in a catalog but not yet implemented therefore stops — cleanly, recorded, and
inventoried — at ``REGISTERED``, and :meth:`ProviderFramework.provider` refuses to
hand it to a consumer.

The façade contains no provider-specific code. Every provider reaches it as a
descriptor, and every live provider is built from that descriptor's declared entry
point (PC-02 / PC-14).
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from platform.universal_provider.certification import (
    CertificationTier,
    ProviderCertificate,
    ProviderCertifier,
)
from platform.universal_provider.composition import (
    CompositeProvider,
    CompositionStrategy,
    compose_providers,
)
from platform.universal_provider.constitution import (
    PROVIDER_CONSTITUTION_VERSION,
    provider_constitution,
)
from platform.universal_provider.contracts import (
    Provider,
    ProviderDescriptor,
    content_hash,
)
from platform.universal_provider.discovery import (
    CatalogSource,
    DiscoveryResult,
    DiscoverySource,
    ProviderDiscovery,
    resolve_entry_point,
)
from platform.universal_provider.errors import (
    ProviderFrameworkError,
    ProviderLifecycleError,
    ProviderRegistryError,
)
from platform.universal_provider.lifecycle import ProviderLifecycle, ProviderPhase
from platform.universal_provider.registry import ProviderRegistration, ProviderRegistry
from platform.universal_provider.validation import (
    ProviderValidator,
    ValidationReport,
    ValidationSubject,
)
from typing import Any

#: Semantic version of the Provider Framework façade.
PROVIDER_FRAMEWORK_VERSION = "1.0.0"


@dataclass(frozen=True, slots=True)
class OnboardingResult:
    """The deterministic outcome of onboarding one provider."""

    qualified_id: str
    phase: ProviderPhase
    registration_id: str
    report: ValidationReport | None = None
    certificate: ProviderCertificate | None = None
    realized: bool = False
    reasons: tuple[str, ...] = ()

    @property
    def active(self) -> bool:
        return self.phase is ProviderPhase.ACTIVE

    @property
    def tier(self) -> str:
        return self.certificate.tier.value if self.certificate is not None else "none"

    def to_dict(self) -> dict[str, Any]:
        return {
            "qualified_id": self.qualified_id,
            "phase": self.phase.value,
            "registration_id": self.registration_id,
            "realized": self.realized,
            "tier": self.tier,
            "validation": self.report.to_dict() if self.report is not None else None,
            "certificate": self.certificate.to_dict() if self.certificate is not None else None,
            "reasons": list(self.reasons),
        }


class ProviderFramework:
    """The Universal Provider Architecture, assembled.

    Every collaborator is injectable, so the framework can be exercised over any
    substrate without special-casing anything.
    """

    def __init__(
        self,
        *,
        registry: ProviderRegistry | None = None,
        lifecycle: ProviderLifecycle | None = None,
        validator: ProviderValidator | None = None,
        certifier: ProviderCertifier | None = None,
        discovery: ProviderDiscovery | None = None,
        config: Mapping[str, Mapping[str, Any]] | None = None,
    ) -> None:
        self._registry = registry if registry is not None else ProviderRegistry()
        self._lifecycle = lifecycle if lifecycle is not None else ProviderLifecycle()
        self._validator = validator if validator is not None else ProviderValidator()
        self._certifier = certifier if certifier is not None else ProviderCertifier()
        self._discovery = discovery if discovery is not None else ProviderDiscovery()
        self._config: dict[str, dict[str, Any]] = {
            str(key): dict(value) for key, value in dict(config or {}).items()
        }
        self._instances: dict[str, Provider] = {}
        self._constitution = provider_constitution()

    # ------------------------------------------------------------------- collaborators

    @property
    def registry(self) -> ProviderRegistry:
        return self._registry

    @property
    def lifecycle(self) -> ProviderLifecycle:
        return self._lifecycle

    @property
    def validator(self) -> ProviderValidator:
        return self._validator

    @property
    def certifier(self) -> ProviderCertifier:
        return self._certifier

    @property
    def discovery(self) -> ProviderDiscovery:
        return self._discovery

    def constitution_hash(self) -> str:
        """Return the content hash of the constitution this framework enforces."""
        return content_hash(self._constitution.to_dict())

    # ----------------------------------------------------------------------- discovery

    def add_source(self, source: DiscoverySource) -> ProviderFramework:
        """Register a discovery source. Returns ``self`` for chaining."""
        self._discovery.add_source(source)
        return self

    def add_catalog(self, directory: Path | str, name: str = "catalog") -> ProviderFramework:
        """Register a directory of JSON provider manifests as a discovery source."""
        return self.add_source(CatalogSource(directory, name=name))

    def discover(self) -> DiscoveryResult:
        """Run discovery over every registered source."""
        return self._discovery.discover()

    # ----------------------------------------------------------------------- admission

    def admit(self, descriptor: ProviderDescriptor) -> ProviderRegistration:
        """Register ``descriptor`` and advance it to ``REGISTERED`` (PC-10).

        Admission is the only way a provider enters the framework, and it is
        atomic with respect to lifecycle: a descriptor the registration authority
        refuses is marked ``REJECTED`` rather than left in limbo.
        """
        self._lifecycle.declare(descriptor.qualified_id)
        try:
            record = self._registry.register(descriptor)
        except ProviderRegistryError as exc:
            if self._lifecycle.can_transition(descriptor.qualified_id, ProviderPhase.REJECTED):
                self._lifecycle.transition(
                    descriptor.qualified_id,
                    ProviderPhase.REJECTED,
                    reason=f"registration refused: {exc.code}",
                )
            raise
        self._lifecycle.transition(
            descriptor.qualified_id,
            ProviderPhase.REGISTERED,
            reason="registered by the provider registration authority",
            evidence_ref=record.registration_id,
        )
        return record

    # -------------------------------------------------------------------- realization

    def realize(self, qualified_id: str) -> Provider:
        """Instantiate the provider from its **declared** entry point (PC-14).

        Cached: a provider is constructed once per framework, so repeated validation
        and querying observe one instance and one substrate.
        """
        cached = self._instances.get(qualified_id)
        if cached is not None:
            return cached
        descriptor = self._descriptor(qualified_id)
        instance = resolve_entry_point(descriptor, self._config.get(descriptor.provider_id, {}))
        self._instances[qualified_id] = instance
        return instance

    def realized(self, qualified_id: str) -> Provider | None:
        """Return the cached instance, or ``None`` if the provider is not realized."""
        return self._instances.get(qualified_id)

    # --------------------------------------------------------------------- validation

    def validate(self, qualified_id: str) -> ValidationReport:
        """Execute every constitutional gate against ``qualified_id``.

        Realization is attempted but not required: a provider that cannot be
        instantiated is still validated, and the gates that need a live object report
        ``INDETERMINATE`` — so the report distinguishes "not yet built" from "built
        wrong".
        """
        descriptor = self._descriptor(qualified_id)
        try:
            instance: Provider | None = self.realize(qualified_id)
        except ProviderFrameworkError:
            instance = None
        subject = ValidationSubject(
            descriptor=descriptor,
            instance=instance,
            registry=self._registry,
            lifecycle=self._lifecycle,
        )
        report = self._validator.validate(subject)
        if report.passed and self._lifecycle.can_transition(qualified_id, ProviderPhase.VALIDATED):
            self._lifecycle.transition(
                qualified_id,
                ProviderPhase.VALIDATED,
                reason=f"all {report.counts()['total']} constitutional gates passed",
                evidence_ref=report.report_hash(),
            )
        return report

    # ------------------------------------------------------------------ certification

    def certify(
        self, qualified_id: str, report: ValidationReport | None = None
    ) -> ProviderCertificate:
        """Issue the certificate the validation evidence substantiates (PC-11)."""
        descriptor = self._descriptor(qualified_id)
        evidence = report if report is not None else self.validate(qualified_id)
        certificate = self._certifier.certify(
            descriptor, evidence, constitution_hash=self.constitution_hash()
        )
        if certificate.tier is CertificationTier.UNIVERSAL and self._lifecycle.can_transition(
            qualified_id, ProviderPhase.CERTIFIED
        ):
            self._lifecycle.transition(
                qualified_id,
                ProviderPhase.CERTIFIED,
                reason=f"certified {certificate.tier.value}",
                evidence_ref=certificate.certificate_id,
            )
        return certificate

    def activate(self, qualified_id: str) -> ProviderPhase:
        """Permit ``qualified_id`` to serve consumers — certification required (PC-11)."""
        certificate = self._certifier.latest(qualified_id)
        if certificate is None or not certificate.authorizes_activation:
            raise ProviderLifecycleError(
                "activation requires a certificate that authorizes it (PC-11)",
                {
                    "qualified_id": qualified_id,
                    "tier": certificate.tier.value if certificate is not None else "none",
                },
            )
        self._lifecycle.transition(
            qualified_id,
            ProviderPhase.ACTIVE,
            reason="activated on a certificate authorizing service",
            evidence_ref=certificate.certificate_id,
        )
        return self._lifecycle.phase(qualified_id)

    def suspend(self, qualified_id: str, reason: str = "") -> ProviderPhase:
        """Withdraw a provider from service, reinstatably (PC-10)."""
        self._lifecycle.transition(
            qualified_id, ProviderPhase.SUSPENDED, reason=reason or "suspended"
        )
        return self._lifecycle.phase(qualified_id)

    def retire(self, qualified_id: str, reason: str = "") -> ProviderPhase:
        """Permanently withdraw a provider (terminal, PC-10)."""
        self._lifecycle.transition(qualified_id, ProviderPhase.RETIRED, reason=reason or "retired")
        self._instances.pop(qualified_id, None)
        return self._lifecycle.phase(qualified_id)

    # ------------------------------------------------------------------------ pipeline

    def onboard(self, descriptor: ProviderDescriptor) -> OnboardingResult:
        """Run the full onboarding pipeline for one descriptor.

        Never raises for an unrealizable or non-conformant provider: the outcome is
        reported as a phase plus reasons, because onboarding a catalog of providers
        must not be aborted by one of them (PC-09).
        """
        reasons: list[str] = []
        try:
            record = self.admit(descriptor)
        except ProviderRegistryError as exc:
            return OnboardingResult(
                qualified_id=descriptor.qualified_id,
                phase=self._lifecycle.phase(descriptor.qualified_id),
                registration_id="",
                reasons=(f"admission refused: {exc.message}",),
            )
        qualified_id = record.qualified_id
        realized = False
        try:
            self.realize(qualified_id)
            realized = True
        except ProviderFrameworkError as exc:
            reasons.append(f"not realized: {exc.message}")
        report = self.validate(qualified_id)
        if report.failures():
            reasons.extend(
                f"{result.gate_id} failed: {result.summary}" for result in report.failures()
            )
        if report.indeterminate():
            reasons.extend(
                f"{result.gate_id} indeterminate: {result.summary}"
                for result in report.indeterminate()
            )
        certificate = self.certify(qualified_id, report)
        if certificate.authorizes_activation:
            self.activate(qualified_id)
        else:
            reasons.append(f"activation withheld: certificate tier {certificate.tier.value}")
        return OnboardingResult(
            qualified_id=qualified_id,
            phase=self._lifecycle.phase(qualified_id),
            registration_id=record.registration_id,
            report=report,
            certificate=certificate,
            realized=realized,
            reasons=tuple(reasons),
        )

    def onboard_discovered(
        self, result: DiscoveryResult | None = None
    ) -> tuple[OnboardingResult, ...]:
        """Onboard every discovered provider, in deterministic discovery order."""
        discovered = result if result is not None else self.discover()
        return tuple(self.onboard(descriptor) for descriptor in discovered.descriptors())

    # ------------------------------------------------------------------------ consumers

    def provider(self, qualified_id: str) -> Provider:
        """Return a provider **only if** it is permitted to serve (PC-11 / PC-07)."""
        self._lifecycle.require_serving(qualified_id)
        instance = self._instances.get(qualified_id)
        if instance is None:
            raise ProviderLifecycleError(
                "provider is permitted to serve but has not been realized",
                {"qualified_id": qualified_id},
            )
        return instance

    def resolve(self, provider_id: str, min_version: str = "0.0.0") -> Provider:
        """Resolve the highest serving version of ``provider_id`` and return it."""
        record = self._registry.resolve(provider_id, min_version)
        return self.provider(record.qualified_id)

    def serving(self) -> tuple[str, ...]:
        """Return every provider currently permitted to serve, id-ordered."""
        return self._lifecycle.serving()

    def compose(
        self,
        provider_id: str,
        kind: str,
        version: str,
        member_ids: Sequence[str],
        *,
        strategy: CompositionStrategy | str = CompositionStrategy.FEDERATED,
        name: str = "",
        authority: str = "",
        description: str = "",
    ) -> CompositeProvider:
        """Compose serving providers into a new provider (PC-12).

        Members are resolved through :meth:`provider`, so a composition can only ever
        be built from providers that are themselves permitted to serve.
        """
        members = [self.provider(member_id) for member_id in member_ids]
        return compose_providers(
            provider_id,
            kind,
            version,
            members,
            strategy=strategy,
            name=name,
            authority=authority,
            description=description,
        )

    # ------------------------------------------------------------------------- reports

    def _descriptor(self, qualified_id: str) -> ProviderDescriptor:
        provider_id, _, version = qualified_id.partition("@")
        if not version:
            raise ProviderRegistryError(
                "a framework reference must be version-pinned 'provider_id@version'",
                {"qualified_id": qualified_id},
            )
        return self._registry.get(provider_id, version).descriptor

    def state(self) -> dict[str, Any]:
        """Return the deterministic, content-addressed state of the whole framework."""
        return {
            "framework_version": PROVIDER_FRAMEWORK_VERSION,
            "constitution_version": PROVIDER_CONSTITUTION_VERSION,
            "constitution_hash": self.constitution_hash(),
            "gates": list(self._validator.gate_ids()),
            "registry": {
                "count": len(self._registry),
                "kinds": list(self._registry.kinds()),
                "providers": [record.qualified_id for record in self._registry.registrations()],
                "registry_hash": self._registry.registry_hash(),
            },
            "lifecycle": {
                "phases": self._lifecycle.phases(),
                "serving": list(self._lifecycle.serving()),
                "head_hash": self._lifecycle.head_hash,
                "intact": self._lifecycle.verify(),
            },
            "certification": {
                "count": len(self._certifier.ledger),
                "head_hash": self._certifier.ledger.head_hash,
                "intact": self._certifier.ledger.verify(),
                "tiers": {
                    certificate.qualified_id: certificate.tier.value
                    for certificate in self._certifier.ledger.certificates()
                },
            },
            "realized": sorted(self._instances),
        }

    def state_hash(self) -> str:
        return content_hash(self.state())


__all__ = [
    "PROVIDER_FRAMEWORK_VERSION",
    "OnboardingResult",
    "ProviderFramework",
]
