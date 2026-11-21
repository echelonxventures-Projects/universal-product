"""UCOS-UFP-001 — Universal Foundation Platform bootstrap & service registration.

Composes the whole Foundation from a declared specialisation and registers each capability —
Repository Truth, Ownership, Assimilation, Measurement Policy, the Constitution — plus the
composed platform itself into the certified
:class:`~platform.foundation.services.ServiceRegistry`.

After this, "discover the repository", "decide who owns this", "assimilate this source",
"measure this" and "is this constitutional" are all *resolvable services*, not steps an
implementation repeats.

Ownership composition is where the convergence lands. The specialisation declares four project
facts — the registration ledger, the eligibility rules, the ownership grain, and which locator
roles carry constitutive evidence — and this module turns them into the **one** ownership
determination. No engine derives ownership beside it.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Iterable, Mapping
from pathlib import Path
from platform.foundation.contracts import ContractRef, content_hash, platform_contract
from platform.foundation.services import ServiceDescriptor, ServiceRegistry
from platform.universal_assimilation.bootstrap import (
    bootstrap_assimilation,
    register_assimilation,
)
from platform.universal_foundation.conformance import (
    CapabilityRegister,
    ConformanceEngine,
    default_capability_register,
    load_capability_register,
)
from platform.universal_foundation.constitution import (
    FOUNDATION_CONSTITUTION_VERSION,
    FoundationConstitution,
    foundation_constitution,
)
from platform.universal_foundation.errors import FoundationCompositionError
from platform.universal_foundation.service import UniversalFoundation
from platform.universal_foundation.specialization import (
    FoundationSpecialization,
    default_specialization,
    load_specialization,
)
from platform.universal_measurement.bootstrap import (
    bootstrap_measurement_policies,
    register_measurement_policies,
)
from platform.universal_ownership.bootstrap import (
    DEFAULT_CATALOG_FILENAME as OWNERSHIP_CATALOG_FILENAME,
)
from platform.universal_ownership.bootstrap import (
    bootstrap_ownership,
    register_ownership,
)
from platform.universal_ownership.bootstrap import catalog_path as ownership_catalog_path
from platform.universal_ownership.determination import OwnershipDeterminationEngine
from platform.universal_ownership.evidence import (
    DeclaredAssignmentProvider,
    DeclaredIdentityProvider,
    DefinitionalLocatorProvider,
    OwnershipEvidenceProvider,
    RegistrationEvidenceProvider,
    RoleLocatorProvider,
    read_declared_identities,
)
from platform.universal_truth.bootstrap import (
    bootstrap_repository_truth,
    register_repository_truth,
)
from platform.universal_truth.contracts import Subject
from platform.universal_truth.eligibility import CanonicalHomePolicy, EligibilityLedger
from platform.universal_truth.policy import (
    DEFAULT_CATALOG_FILENAME as TRUTH_CATALOG_FILENAME,
)
from platform.universal_truth.policy import TruthPolicy
from platform.universal_truth.policy import catalog_path as truth_catalog_path
from platform.universal_truth.projection import SubjectProjection

#: The service name under which the composed Foundation is published.
FOUNDATION_SERVICE_NAME = "universal.foundation"

#: The service name under which the Foundation Constitution is published.
CONSTITUTION_SERVICE_NAME = "universal.foundation.constitution"

#: The contract version of the composed Foundation platform surface.
FOUNDATION_CONTRACT_VERSION = "1.0.0"

#: The canonical identity of the Universal Foundation Platform instance.
UFP_ID = "UCOS-UFP-001"

#: Declaration prefix by which a project reuses a *packaged* catalogue instead of its own file.
PACKAGED_PREFIX = "packaged:"

_FOUNDATION_CONTRACT_NAMES: tuple[tuple[str, str], ...] = (
    ("foundation.determination.determine", "Determine Truth, ownership, assimilation and policy."),
    ("foundation.population.project", "Project a declared population into subjects."),
    ("foundation.ownership.compose", "Compose the one ownership determination for a project."),
    ("foundation.governance.reduce", "Reduce governance workload to its irreducible minimum."),
)

#: The versioned published contract surface of the composed Foundation platform.
FOUNDATION_CONTRACTS: tuple[ContractRef, ...] = tuple(
    ContractRef(name, FOUNDATION_CONTRACT_VERSION) for name, _ in _FOUNDATION_CONTRACT_NAMES
)


def foundation_contract_names() -> tuple[str, ...]:
    """The published Foundation platform contract names, in declaration order."""
    return tuple(name for name, _ in _FOUNDATION_CONTRACT_NAMES)


def _resolve_declared(
    declared: FoundationSpecialization,
    field: str,
    packaged: Callable[[str], Path],
    default_filename: str,
    *,
    root: Path | str,
) -> Path | None:
    """Resolve a declared document, honouring the ``packaged:`` reuse prefix."""
    value = getattr(declared, field, "")
    if value.startswith(PACKAGED_PREFIX):
        return packaged(value[len(PACKAGED_PREFIX) :] or default_filename)
    return declared.resolve(field, root=root)


def _read_document(path: Path, *, what: str) -> Mapping[str, object]:
    """Read a declared JSON document (fail-closed)."""
    try:
        payload = json.loads(path.read_text("utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise FoundationCompositionError(
            f"{what} could not be read", path=str(path), detail=str(exc)
        ) from exc
    if not isinstance(payload, Mapping):
        raise FoundationCompositionError(f"{what} must be a mapping", path=str(path))
    return payload


def registered_locators(
    declared: FoundationSpecialization, *, root: Path | str = "."
) -> tuple[str, ...] | None:
    """Project the declared registration ledger into locators (``None`` when undeclared).

    The ledger is a projection of a document the project already keeps — an artifact register,
    a governance registry — so the set of registered locators is never restated in a Foundation
    declaration. Knowledge Once.
    """
    document = declared.resolve("registration_document", root=root)
    if document is None or declared.registration_projection is None:
        return None
    subjects = SubjectProjection(declared.registration_projection).project_file(document)
    return tuple(sorted({subject.subject_id for subject in subjects}))


def canonical_home_policy(
    declared: FoundationSpecialization,
    truth: TruthPolicy,
    *,
    root: Path | str = ".",
) -> CanonicalHomePolicy:
    """Compose the one canonical-home policy: declared zones plus declared eligibility."""
    ledger = declared.eligibility
    registered = registered_locators(declared, root=root)
    if ledger is not None and registered is not None:
        ledger = EligibilityLedger.create(
            ledger_id=ledger.ledger_id,
            registered=registered,
            require_registration=ledger.require_registration,
            admitted_suffixes=ledger.admitted_suffixes,
            excluded_segments=ledger.excluded_segments,
            description=ledger.description,
        )
    elif ledger is not None and ledger.require_registration and registered is None:
        raise FoundationCompositionError(
            "eligibility requires registration but no registration projection is declared",
            project_id=declared.project_id,
        )
    return CanonicalHomePolicy(truth, ledger)


def ownership_evidence_providers(
    declared: FoundationSpecialization,
    home: CanonicalHomePolicy,
    subjects: Iterable[Subject] = (),
    *,
    declarations: Path | None = None,
    root: Path | str = ".",
) -> tuple[OwnershipEvidenceProvider, ...]:
    """Compose the declared evidence provider set for a project.

    Four sources, all declared and all optional:

        * the **governed assignment catalogue** — the act of governance itself;
        * the **artifact-declared identity** of each eligible locator, read from the heads of
          locators Truth already declared (never discovered);
        * one provider per declared **locator role**, which adopts a measurement some other
          instrument owns rather than re-deriving it;
        * the framework's **definitional basename** rule, used only when the project declares
          no role — a project that already measures definitional homes never needs it.
    """
    providers: list[OwnershipEvidenceProvider] = []
    if declarations is not None and Path(declarations).exists():
        providers.append(DeclaredAssignmentProvider.from_file(declarations))

    population = tuple(subjects)
    grain = declared.ownership_granularity
    eligible = tuple(
        sorted(
            {
                locator
                for subject in population
                for locator in subject.locators
                if home.admits(locator)
            }
        )
    )
    if eligible:
        identities = read_declared_identities(
            eligible,
            root=root,
            labels=declared.labels,
            head_bytes=declared.identity_head_bytes,
        )
        if identities:
            providers.append(DeclaredIdentityProvider(identities, home, granularity=grain))

    for role, precedence in declared.evidence_roles:
        providers.append(RoleLocatorProvider(role, home, precedence=precedence, granularity=grain))
    if not declared.evidence_roles:
        providers.append(DefinitionalLocatorProvider(home, granularity=grain))

    if declared.require_registration:
        ledger = registered_locators(declared, root=root)
        if ledger is not None:
            providers.append(RegistrationEvidenceProvider(ledger))
    return tuple(providers)


def bootstrap_project_ownership(
    declared: FoundationSpecialization,
    truth: TruthPolicy,
    subjects: Iterable[Subject] = (),
    *,
    declarations: Path | None = None,
    root: Path | str = ".",
) -> OwnershipDeterminationEngine:
    """The ONE ownership determination for a project, composed from its declaration alone."""
    home = canonical_home_policy(declared, truth, root=root)
    population = tuple(subjects)
    providers = ownership_evidence_providers(
        declared, home, population, declarations=declarations, root=root
    )
    registered: tuple[str, ...] | None = None
    if declared.require_registration:
        # A declared requirement with no ledger to satisfy it refuses every subject rather than
        # being quietly ignored. Zero Silent Repair: dropping a declared obligation because its
        # input is absent is exactly how a requirement stops being enforced without anyone
        # having decided that it should.
        registered = registered_locators(declared, root=root) or ()
    return bootstrap_ownership(
        policy=home,
        providers=providers,
        registered=registered,
        require_registration=declared.require_registration,
    )


def bootstrap_universal_foundation(
    specialization: FoundationSpecialization | Path | str | None = None,
    *,
    root: Path | str = ".",
) -> UniversalFoundation:
    """Compose the Foundation from a declared specialisation (packaged one by default)."""
    if specialization is None:
        declared = default_specialization()
    elif isinstance(specialization, FoundationSpecialization):
        declared = specialization
    else:
        declared = load_specialization(specialization)

    policy_document = _resolve_declared(
        declared, "truth_policy", truth_catalog_path, TRUTH_CATALOG_FILENAME, root=root
    )
    if policy_document is not None and not Path(policy_document).exists():
        raise FoundationCompositionError(
            "declared truth policy document does not exist", path=str(policy_document)
        )
    truth = bootstrap_repository_truth(policy_document)

    declarations = _resolve_declared(
        declared,
        "ownership_declarations",
        ownership_catalog_path,
        OWNERSHIP_CATALOG_FILENAME,
        root=root,
    )
    return UniversalFoundation(
        declared,
        truth,
        _LazyOwnership(declared, truth, declarations, root),
        bootstrap_assimilation(policy=truth),
        bootstrap_measurement_policies(),
    )


class _LazyOwnership(OwnershipDeterminationEngine):
    """The project's ownership engine, recomposed against the population it is asked about.

    Ownership evidence for this project includes what its *own artifacts declare about
    themselves*, and that evidence can only be gathered for a known population. Rather than
    read anything at composition time (UFC-07), the engine composes an empty-population form
    immediately and rebinds its providers the first time a real population arrives.
    """

    __slots__ = ("_declared", "_truth", "_declarations", "_root", "_bound")

    def __init__(
        self,
        declared: FoundationSpecialization,
        truth: TruthPolicy,
        declarations: Path | None,
        root: Path | str,
    ) -> None:
        base = bootstrap_project_ownership(
            declared, truth, (), declarations=declarations, root=root
        )
        super().__init__(
            base.providers,
            policy=base.home,
            contract=base.contract,
            registered=base.registration_ledger,
        )
        self._declared = declared
        self._truth = truth
        self._declarations = declarations
        self._root = root
        self._bound: frozenset[str] = frozenset()

    def determine(self, subjects: Iterable[Subject]):  # noqa: ANN201 - inherited signature
        """Recompose against ``subjects``, then determine — one determination, one population."""
        population = tuple(subjects)
        key = frozenset(subject.subject_key for subject in population)
        if population and key != self._bound:
            rebound = bootstrap_project_ownership(
                self._declared,
                self._truth,
                population,
                declarations=self._declarations,
                root=self._root,
            )
            OwnershipDeterminationEngine.__init__(
                self,
                rebound.providers,
                policy=rebound.home,
                contract=rebound.contract,
                registered=rebound.registration_ledger,
            )
            self._bound = key
        return OwnershipDeterminationEngine.determine(self, population)


def bootstrap_foundation_constitution(
    register: CapabilityRegister | Path | str | None = None,
    *,
    project_root: Path | str = ".",
) -> ConformanceEngine:
    """Compose the Constitution's conformance engine over a declared capability register."""
    if register is None:
        resolved = default_capability_register()
    elif isinstance(register, CapabilityRegister):
        resolved = register
    else:
        resolved = load_capability_register(register)
    return ConformanceEngine(resolved, project_root=project_root)


def constitution_service_descriptor() -> ServiceDescriptor:
    """The published service descriptor for the Foundation Constitution."""
    return ServiceDescriptor(
        name=CONSTITUTION_SERVICE_NAME,
        contract=platform_contract(
            "foundation.constitution.conform",
            FOUNDATION_CONSTITUTION_VERSION,
            "Measure every Foundation capability against the Foundation Constitution.",
        ),
        capabilities=(foundation_constitution().constitution_id,),
        description="Universal Foundation Constitution — one law, one probe per article.",
    )


def register_foundation_constitution(
    registry: ServiceRegistry, *, register: CapabilityRegister | Path | str | None = None
) -> ServiceDescriptor:
    """Register the Foundation Constitution into ``registry`` (lazy, memoised)."""
    return registry.register(
        constitution_service_descriptor(),
        lambda: bootstrap_foundation_constitution(register),
    )


def foundation_service_descriptor() -> ServiceDescriptor:
    """The published service descriptor for the composed Foundation."""
    return ServiceDescriptor(
        name=FOUNDATION_SERVICE_NAME,
        contract=platform_contract(
            "foundation.determination.determine",
            FOUNDATION_CONTRACT_VERSION,
            "Determine Truth, ownership, assimilation and measurement as one Foundation.",
        ),
        capabilities=(UFP_ID,),
        dependencies=(
            "universal.truth",
            "universal.ownership",
            "universal.assimilation",
            "universal.measurement.policy",
            CONSTITUTION_SERVICE_NAME,
        ),
        description="Universal Foundation Platform — the composed reusable Foundation.",
    )


def register_universal_foundation(
    registry: ServiceRegistry,
    *,
    specialization: FoundationSpecialization | Path | str | None = None,
) -> tuple[ServiceDescriptor, ...]:
    """Register every Foundation capability and the composed platform into ``registry``."""
    descriptors = (
        register_repository_truth(registry),
        register_ownership(registry),
        register_assimilation(registry),
        register_measurement_policies(registry),
        register_foundation_constitution(registry),
        registry.register(
            foundation_service_descriptor(),
            lambda: bootstrap_universal_foundation(specialization),
        ),
    )
    registry.validate()
    return descriptors


def foundation_fingerprint(
    constitution: FoundationConstitution | None = None,
) -> str:
    """The deterministic fingerprint of the law the platform is governed by."""
    return content_hash((constitution or foundation_constitution()).to_dict())


__all__ = [
    "UFP_ID",
    "PACKAGED_PREFIX",
    "FOUNDATION_SERVICE_NAME",
    "CONSTITUTION_SERVICE_NAME",
    "FOUNDATION_CONTRACT_VERSION",
    "FOUNDATION_CONTRACTS",
    "bootstrap_foundation_constitution",
    "bootstrap_project_ownership",
    "bootstrap_universal_foundation",
    "canonical_home_policy",
    "constitution_service_descriptor",
    "foundation_contract_names",
    "foundation_fingerprint",
    "foundation_service_descriptor",
    "ownership_evidence_providers",
    "register_foundation_constitution",
    "register_universal_foundation",
    "registered_locators",
]
