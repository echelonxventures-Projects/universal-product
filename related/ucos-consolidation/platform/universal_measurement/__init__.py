"""UCOS Ω∞ — Universal Measurement Policy Framework (``platform.universal_measurement``).

**UCOS-UMPF-001.** The reusable Foundation capability that makes every measurement a
**registered policy over determinations** rather than a branch inside one engine.

Coverage, homed, upload-only, assimilation, ownership and completeness are all instances of
one shape: a policy reads a :class:`MeasurementContext` (a Repository Truth partition, an
ownership determination, an assimilation report, a subject population, declared facts),
reports a value with the findings that make it up, and declares whether it is satisfied. The
engine conjoins the blocking policies into a determination — CLOSED or NOT-CLOSED — and every
outcome projects into the certified :class:`~platform.measurement.contracts.Measurement`
vocabulary for recording and certification.

Two invariants keep the numbers honest:

    * a policy that **cannot** be evaluated (its determination was not supplied) is skipped and
      reported as missing — never as a pass;
    * every value carries its findings, so any number resolves back to the subjects that
      produced it.

Adding a measurement means registering a policy. No engine is edited, and the same registry
serves every future project.
"""

from __future__ import annotations

from platform.universal_measurement.bootstrap import (
    POLICY_SERVICE_NAME,
    bootstrap_measurement_policies,
    policy_service_descriptor,
    register_measurement_policies,
)
from platform.universal_measurement.contracts import (
    MAX_RETAINED_FINDINGS,
    POLICY_CONTRACT_VERSION,
    POLICY_CONTRACTS,
    UMPF_ID,
    MeasurementContext,
    MeasurementPolicyDescriptor,
    PolicyOutcome,
    PolicySuite,
    policy_contract_names,
)
from platform.universal_measurement.engine import (
    MeasurementPolicyRegistry,
    PolicyMeasurementEngine,
    build_policy_engine,
    default_policy_registry,
)
from platform.universal_measurement.errors import (
    MeasurementContextError,
    MeasurementPolicyContractError,
    MeasurementPolicyError,
    MeasurementPolicyEvaluationError,
    MeasurementPolicyRegistryError,
)
from platform.universal_measurement.policies import (
    AssimilationCoveragePolicy,
    ContestedOwnershipPolicy,
    EvidenceOnlySourcePolicy,
    FoundationCompletenessPolicy,
    MeasurementPolicy,
    OwnershipCoveragePolicy,
    RemediableOwnershipPolicy,
    TruthClassificationCoveragePolicy,
    UnadaptedSourcePolicy,
    UnresolvedOwnershipPolicy,
    default_measurement_policies,
)

__all__ = [
    "UMPF_ID",
    "POLICY_CONTRACT_VERSION",
    "POLICY_CONTRACTS",
    "policy_contract_names",
    "MAX_RETAINED_FINDINGS",
    "MeasurementContext",
    "MeasurementPolicyDescriptor",
    "PolicyOutcome",
    "PolicySuite",
    "MeasurementPolicy",
    "TruthClassificationCoveragePolicy",
    "OwnershipCoveragePolicy",
    "UnresolvedOwnershipPolicy",
    "RemediableOwnershipPolicy",
    "ContestedOwnershipPolicy",
    "AssimilationCoveragePolicy",
    "EvidenceOnlySourcePolicy",
    "UnadaptedSourcePolicy",
    "FoundationCompletenessPolicy",
    "default_measurement_policies",
    "MeasurementPolicyRegistry",
    "PolicyMeasurementEngine",
    "default_policy_registry",
    "build_policy_engine",
    "POLICY_SERVICE_NAME",
    "bootstrap_measurement_policies",
    "policy_service_descriptor",
    "register_measurement_policies",
    "MeasurementPolicyError",
    "MeasurementPolicyContractError",
    "MeasurementPolicyRegistryError",
    "MeasurementPolicyEvaluationError",
    "MeasurementContextError",
]
