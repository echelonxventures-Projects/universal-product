"""UCOS Ω∞ — Universal Repository Truth Framework (``platform.universal_truth``).

**UCOS-URTF-001.** The reusable Foundation capability that answers, for *any* project,
the question every closure, coverage, ownership and assimilation measurement silently
assumed: *what in this repository is Truth, and what is merely a projection of it?*

The framework separates, by declared policy rather than by hardcoded path:

    Evidence · Declarations · Derived outputs · Operational memory ·
    Historical state · Generated output · Transient residue · Canonical Truth

and enforces two constitutional invariants structurally:

    1. **Repository Truth SHALL be determined by policy.** A project declares zones in a
       document; the framework contains no path literal of any repository.
    2. **Classes that cannot own SHALL never be declared a home.** Evidence proves,
       derived output regenerates, operational memory records, historical state is
       superseded — none of them may hold canonical ownership, and a declaration that
       claims otherwise fails closed.

The framework reads Truth and never authors it. Its identities live in a disjoint
``UCOS-URT*`` namespace, hold no wall-clock, and are content-addressed (IMP-007 §5), so
every classification is reproducible and auditable by TRACK-001.
"""

from __future__ import annotations

from platform.universal_truth.bootstrap import (
    TRUTH_SERVICE_NAME,
    bootstrap_repository_truth,
    register_repository_truth,
    truth_service_descriptor,
)
from platform.universal_truth.contracts import (
    AUTHORITATIVE_TRUTH_CLASSES,
    NON_HOME_TRUTH_CLASSES,
    TRUTH_CONTRACT_VERSION,
    TRUTH_CONTRACTS,
    URTF_ID,
    PathSelector,
    SelectorKind,
    Subject,
    TruthClass,
    TruthClassification,
    TruthZone,
    locator_segments,
    normalize_locator,
    truth_contract_names,
)
from platform.universal_truth.eligibility import (
    ELIGIBILITY_REASONS,
    CanonicalHomePolicy,
    EligibilityLedger,
    EligibilityVerdict,
    load_eligibility_ledger,
    open_ledger,
)
from platform.universal_truth.errors import (
    RepositoryTruthError,
    TruthContractError,
    TruthPolicyError,
    TruthProjectionError,
)
from platform.universal_truth.policy import (
    TruthPartition,
    TruthPolicy,
    catalog_path,
    default_truth_policy,
    load_truth_policy,
)
from platform.universal_truth.projection import (
    ProjectionSpec,
    SubjectProjection,
    project_subjects,
)

__all__ = [
    "URTF_ID",
    "TRUTH_CONTRACT_VERSION",
    "TRUTH_CONTRACTS",
    "truth_contract_names",
    "TruthClass",
    "NON_HOME_TRUTH_CLASSES",
    "AUTHORITATIVE_TRUTH_CLASSES",
    "SelectorKind",
    "PathSelector",
    "TruthZone",
    "ELIGIBILITY_REASONS",
    "CanonicalHomePolicy",
    "EligibilityLedger",
    "EligibilityVerdict",
    "load_eligibility_ledger",
    "open_ledger",
    "TruthClassification",
    "Subject",
    "normalize_locator",
    "locator_segments",
    "TruthPolicy",
    "TruthPartition",
    "load_truth_policy",
    "default_truth_policy",
    "catalog_path",
    "ProjectionSpec",
    "SubjectProjection",
    "project_subjects",
    "TRUTH_SERVICE_NAME",
    "bootstrap_repository_truth",
    "truth_service_descriptor",
    "register_repository_truth",
    "RepositoryTruthError",
    "TruthContractError",
    "TruthPolicyError",
    "TruthProjectionError",
]
