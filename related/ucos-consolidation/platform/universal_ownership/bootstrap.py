"""UCOS-UOF-001 — Ownership Framework bootstrap & service registration.

Composes the Ownership Determination Framework from declared inputs only: a Repository
Truth policy (which zones may own), an optional governed assignment catalogue, and an
optional registration ledger. Ownership determination then becomes a resolvable platform
service instead of logic re-grown inside each engine.
"""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from platform.foundation.contracts import platform_contract
from platform.foundation.services import ServiceDescriptor, ServiceRegistry
from platform.universal_ownership.contracts import OWNERSHIP_CONTRACT_VERSION, UOF_ID
from platform.universal_ownership.determination import OwnershipDeterminationEngine
from platform.universal_ownership.evidence import (
    DeclaredAssignmentProvider,
    DefinitionalLocatorProvider,
    EvidenceProviderRegistry,
    OwnershipEvidenceProvider,
    RegistrationEvidenceProvider,
)
from platform.universal_truth.eligibility import CanonicalHomePolicy, EligibilityLedger
from platform.universal_truth.policy import TruthPolicy, default_truth_policy

#: The service name under which canonical ownership determination is published.
OWNERSHIP_SERVICE_NAME = "universal.ownership"

#: The packaged catalogue directory holding declared ownership assignments.
CATALOG_DIRNAME = "catalog"

#: The declared assignment catalogue shipped with the framework (data, not code).
DEFAULT_CATALOG_FILENAME = "ucos-ownership-declarations.json"


def catalog_path(filename: str = DEFAULT_CATALOG_FILENAME) -> Path:
    """The packaged catalogue path for ``filename``."""
    return Path(__file__).resolve().parent / CATALOG_DIRNAME / filename


def default_evidence_providers(
    policy: TruthPolicy | CanonicalHomePolicy,
    *,
    declarations: Path | str | None = None,
    registered: Iterable[str] | None = None,
) -> tuple[OwnershipEvidenceProvider, ...]:
    """The default provider set: declared assignments, definitional locators, registration."""
    providers: list[OwnershipEvidenceProvider] = []
    document = catalog_path() if declarations is None else Path(declarations)
    if document.exists():
        providers.append(DeclaredAssignmentProvider.from_file(document))
    providers.append(DefinitionalLocatorProvider(policy))
    if registered is not None:
        providers.append(RegistrationEvidenceProvider(tuple(registered)))
    return tuple(providers)


def bootstrap_ownership(
    *,
    policy: TruthPolicy | CanonicalHomePolicy | None = None,
    declarations: Path | str | None = None,
    registered: Iterable[str] | None = None,
    require_registration: bool = False,
    eligibility: EligibilityLedger | None = None,
    providers: Iterable[OwnershipEvidenceProvider] | None = None,
) -> OwnershipDeterminationEngine:
    """Build the ownership determination engine from declared inputs only.

    ``eligibility`` composes a declared locator-eligibility ledger onto the Truth policy, so a
    project can require registration, a locator form and the exclusion of derived residue
    without any provider or engine learning what those requirements are. ``providers``
    replaces the default provider set outright, which is how a project contributes a further
    source of constitutional evidence (UFC-03).
    """
    resolved = policy or default_truth_policy()
    home = (
        resolved
        if isinstance(resolved, CanonicalHomePolicy)
        else CanonicalHomePolicy(resolved, eligibility)
    )
    if eligibility is not None and isinstance(resolved, CanonicalHomePolicy):
        home = CanonicalHomePolicy(resolved.policy, eligibility)
    ledger = tuple(registered) if registered is not None else None
    registry = EvidenceProviderRegistry(
        tuple(providers)
        if providers is not None
        else default_evidence_providers(home, declarations=declarations, registered=ledger)
    )
    return OwnershipDeterminationEngine(
        registry,
        policy=home,
        registered=ledger if require_registration else None,
    )


def ownership_service_descriptor() -> ServiceDescriptor:
    """The published service descriptor for canonical ownership determination."""
    return ServiceDescriptor(
        name=OWNERSHIP_SERVICE_NAME,
        contract=platform_contract(
            "ownership.determination.determine",
            OWNERSHIP_CONTRACT_VERSION,
            "Determine canonical ownership from constitutional evidence only.",
        ),
        capabilities=(UOF_ID,),
        description="Universal Ownership Framework — declared, never inferred, ownership.",
    )


def register_ownership(
    registry: ServiceRegistry, *, policy: TruthPolicy | CanonicalHomePolicy | None = None
) -> ServiceDescriptor:
    """Register ownership determination into ``registry`` (lazy, memoised)."""
    return registry.register(
        ownership_service_descriptor(), lambda: bootstrap_ownership(policy=policy)
    )


__all__ = [
    "OWNERSHIP_SERVICE_NAME",
    "CATALOG_DIRNAME",
    "DEFAULT_CATALOG_FILENAME",
    "catalog_path",
    "default_evidence_providers",
    "bootstrap_ownership",
    "ownership_service_descriptor",
    "register_ownership",
]
