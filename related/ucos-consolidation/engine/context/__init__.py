"""UCXI-000001 — Universal Context Intelligence.

The complete context capability of the platform, in sixteen parts:

    Part 01  ``constitution``   the twelve laws of all context, each with a check
    Part 02  ``taxonomy``       the classification: fifteen universal kinds, open to more
    Part 03  ``ontology``       the declared structural shape of every kind
    Part 04  ``model``          the immutable value objects (declaration, value, record)
    Part 05  ``registry``       the single registration authority, append-only
    Part 06  ``catalog``        the platform's own fifteen universal contexts (DATA)
    Part 07  ``resolution``     precedence-ordered resolution with provenance
    Part 08  ``composition``    bounded, isolated assembly (delegated to the runtime)
    Part 09  ``graph``          the navigable projection of registry + taxonomy
    Part 10  ``runtime``        ambient binding, activation and propagation
    Part 11  ``validation``     twelve rules across five dimensions
    Part 12  ``certification``  eight measured dimensions, one computed verdict
    Part 13  ``evidence``       the deterministic, auditable artefact of the whole layer
    Part 14  ``cli``            the operational surface (``ucos-context``)
    Part 15  ``location``       the location axis and location-derived resolution
    Part 16  ``location_assurance``  the rules and dimensions that measure Part 15

The fifteen universal context kinds — existence, reality, observer, temporal, spatial,
identity, governance, security, knowledge, computational, environmental, economic,
regulatory, linguistic, cultural — are constitutionally present. **Future context types**
are first-class: they are admitted by extending the taxonomy and ontology as data
(:meth:`~engine.context.taxonomy.ContextTaxonomy.extend`,
:meth:`~engine.context.ontology.ContextOntology.extend`), and no control flow in this
package branches on a particular kind, so nothing here needs editing to support one.

Reuse over reinvention: identity and canonical hashing come from the Universal Registry
Platform's single registration authority, boundedness and isolation from the certified
runtime composition primitives, the graph substrate from the Universal Knowledge Graph,
cycle detection and topological ordering from the compiler, and logging, telemetry,
correlation identity and the frozen-path guard from the foundation. This layer is
DERIVED TRUTH: it computes and refuses, and it grants no authority.
"""

from __future__ import annotations

from engine.context.catalog import (
    UNIVERSAL_BOUNDARY,
    UNIVERSAL_CATALOG,
    UNIVERSAL_NAMESPACE,
    bootstrap_registry,
    universal_declarations,
)
from engine.context.certification import (
    VERDICT_CERTIFIED,
    VERDICT_NOT_CERTIFIED,
    CertificationDimension,
    ContextCertificate,
    certify,
    require_certified,
)
from engine.context.composition import (
    ComposedContext,
    Federation,
    compose,
    compose_universal,
)
from engine.context.constitution import (
    CONTEXT_CONSTITUTION,
    CONTEXT_LAWS,
    ConstitutionAssessment,
    ContextConstitution,
    ContextLaw,
)
from engine.context.errors import (
    ConstitutionViolation,
    ContextAmbiguityError,
    ContextCompositionError,
    ContextError,
    ContextGraphError,
    ContextIsolationError,
    ContextNotFoundError,
    ContextOnceViolation,
    ContextResolutionFailure,
    ContextRuntimeError,
    ContextValidationError,
    DuplicateContextError,
    OntologyError,
    TaxonomyError,
)
from engine.context.evidence import build_evidence, evidence_index, write_evidence
from engine.context.graph import ContextGraph, build_context_graph
from engine.context.location import (
    AXIS_DERIVATION,
    AXIS_GRAPH,
    FRAME_NAMESPACE,
    LOCATION,
    UNRESOLVED,
    FrameRegistry,
    LocationResolution,
    ReferenceFrame,
    ResolvedAxis,
    axis_order,
    axis_waves,
    build_context_registry,
    build_frame_registry,
    context_registries,
    derivation_path,
    empty_context_registry,
    extended_ontology,
    extended_taxonomy,
    identity_tuples,
    introduced_axes,
    location_determined_axes,
    register_resolution,
)
from engine.context.location_assurance import (
    LOCATION_DIMENSIONS,
    LOCATION_RULES,
    certify_location,
    complete_frame_kinds,
    complete_frames,
    replay_location,
    require_certified_location,
    validate_location,
)
from engine.context.model import (
    ContextDeclaration,
    ContextRecord,
    ContextRelationEdge,
    ContextValue,
    Observer,
    ResolvedContext,
    values_from_mapping,
)
from engine.context.ontology import (
    UNIVERSAL_ONTOLOGY,
    ContextOntology,
    DimensionSpec,
)
from engine.context.registry import AuditEntry, ContextRegistry
from engine.context.resolution import (
    ContextRequest,
    resolution_report,
    resolve,
    resolve_kind,
    resolve_universal,
)
from engine.context.runtime import ContextActivation, ContextRuntime, activate, current
from engine.context.taxonomy import (
    UNIVERSAL_KINDS,
    UNIVERSAL_TAXONOMY,
    ContextAuthority,
    ContextKind,
    ContextLifecycle,
    ContextRelation,
    ContextTaxon,
    ContextTaxonomy,
)
from engine.context.validation import (
    VALIDATION_RULES,
    ContextValidationReport,
    ContextValidator,
    ValidationRule,
    validate,
)

#: The capability identifier of this layer.
CAPABILITY = "UCXI-000001"

#: This layer computes and refuses; it legislates nothing.
AUTHORITY = "NONE (DERIVED TRUTH)"

__all__ = [
    "AUTHORITY",
    "CAPABILITY",
    # taxonomy
    "ContextKind",
    "ContextAuthority",
    "ContextLifecycle",
    "ContextRelation",
    "ContextTaxon",
    "ContextTaxonomy",
    "UNIVERSAL_KINDS",
    "UNIVERSAL_TAXONOMY",
    # ontology
    "ContextOntology",
    "DimensionSpec",
    "UNIVERSAL_ONTOLOGY",
    # model
    "ContextDeclaration",
    "ContextRecord",
    "ContextRelationEdge",
    "ContextValue",
    "Observer",
    "ResolvedContext",
    "values_from_mapping",
    # registry + catalog
    "AuditEntry",
    "ContextRegistry",
    "UNIVERSAL_CATALOG",
    "UNIVERSAL_NAMESPACE",
    "UNIVERSAL_BOUNDARY",
    "bootstrap_registry",
    "universal_declarations",
    # resolution
    "ContextRequest",
    "resolve",
    "resolve_kind",
    "resolve_universal",
    "resolution_report",
    # composition
    "ComposedContext",
    "Federation",
    "compose",
    "compose_universal",
    # graph
    "ContextGraph",
    "build_context_graph",
    # runtime
    "ContextActivation",
    "ContextRuntime",
    "activate",
    "current",
    # constitution
    "CONTEXT_CONSTITUTION",
    "CONTEXT_LAWS",
    "ConstitutionAssessment",
    "ContextConstitution",
    "ContextLaw",
    # validation
    "ContextValidationReport",
    "ContextValidator",
    "ValidationRule",
    "VALIDATION_RULES",
    "validate",
    # certification
    "CertificationDimension",
    "ContextCertificate",
    "VERDICT_CERTIFIED",
    "VERDICT_NOT_CERTIFIED",
    "certify",
    "require_certified",
    # location (Part 15)
    "LOCATION",
    "UNRESOLVED",
    "FRAME_NAMESPACE",
    "AXIS_DERIVATION",
    "AXIS_GRAPH",
    "ReferenceFrame",
    "ResolvedAxis",
    "LocationResolution",
    "FrameRegistry",
    "axis_order",
    "axis_waves",
    "derivation_path",
    "location_determined_axes",
    "introduced_axes",
    "extended_taxonomy",
    "extended_ontology",
    "build_frame_registry",
    "register_resolution",
    "empty_context_registry",
    "build_context_registry",
    "context_registries",
    "identity_tuples",
    # location assurance (Part 16)
    "LOCATION_RULES",
    "LOCATION_DIMENSIONS",
    "complete_frames",
    "complete_frame_kinds",
    "validate_location",
    "certify_location",
    "require_certified_location",
    "replay_location",
    # evidence
    "build_evidence",
    "evidence_index",
    "write_evidence",
    # errors
    "ContextError",
    "ConstitutionViolation",
    "ContextAmbiguityError",
    "ContextCompositionError",
    "ContextGraphError",
    "ContextIsolationError",
    "ContextNotFoundError",
    "ContextOnceViolation",
    "ContextResolutionFailure",
    "ContextRuntimeError",
    "ContextValidationError",
    "DuplicateContextError",
    "OntologyError",
    "TaxonomyError",
]
