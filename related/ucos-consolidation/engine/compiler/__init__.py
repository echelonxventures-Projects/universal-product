"""EC-1 Universal Compiler (EPIC-003) — IMP-007 deterministic compilation engine.

Public API surface for the Universal Compiler: the deterministic engine that
parses, validates, resolves, compiles, optimizes, packages, signs, and publishes
registered, certified BP-DATA blueprints into executable implementation artifacts
with complete backward traceability (IMP-007).

The compiler is additive engineering code built on the EC-1 Foundation (EPIC-001)
and the read-only Registry Adapter (EPIC-002), which it uses **exclusively** for
registry access. It never writes to the certified corpus (DP-03), rejects
uncertified inputs (§14/§16), fails builds on circular dependencies (§4/§17), and
preserves provenance across every stage (§1).

Tasks: TASK-000017 (IR + errors + gap + types), TASK-000018 (serialization),
TASK-000019 (parse), TASK-000020 (validation), TASK-000021 (resolution),
TASK-000022 (cycle detection), TASK-000023 (data compiler), TASK-000024
(optimization), TASK-000025 (packaging), TASK-000026 (signing), TASK-000027
(publishing), TASK-000028 (pipeline), TASK-000029 (tests), TASK-000030 (API).
"""

from __future__ import annotations

from engine.compiler.cycles import assert_acyclic, detect_cycle, topological_order
from engine.compiler.data_compiler import (
    ArtifactKind,
    CompiledArtifact,
    CompiledBlueprint,
    DataBlueprintCompiler,
    provenance_chain,
    snake_case,
)
from engine.compiler.errors import (
    CertificationError,
    CompilationError,
    CompilerError,
    CyclicDependencyError,
    DependencyError,
    OptimizationError,
    PackagingError,
    ParseError,
    PipelineError,
    PublishingError,
    SerializationError,
    SigningError,
    ValidationError,
)
from engine.compiler.gap import GapReport, Stage
from engine.compiler.ir import (
    IR_VERSION,
    Attribute,
    BlueprintFamily,
    BlueprintIR,
    Certification,
    CertificationStatus,
    DataRelationship,
    Entity,
    Index,
    Provenance,
    RelationshipKind,
)
from engine.compiler.optimization import OptimizedBlueprint, Optimizer
from engine.compiler.packaging import (
    COMPILER_TOOLCHAIN,
    PACKAGE_FORMAT,
    TOOLCHAIN_VERSION,
    Package,
    Packager,
)
from engine.compiler.parser import (
    SUPPORTED_FAMILIES,
    ensure_supported,
    is_supported,
    parse,
    parse_bytes,
    parse_document,
    parse_text,
)
from engine.compiler.pipeline import (
    COMPILE_CONTRACT,
    BuildResult,
    CompilationResult,
    CompilerPipeline,
)
from engine.compiler.publishing import PublishedArtifact, Publisher
from engine.compiler.resolver import DependencyResolver, ResolvedBuild
from engine.compiler.serialization import (
    deserialize,
    from_dict,
    serialize,
    serialize_bytes,
    to_canonical_dict,
)
from engine.compiler.signing import (
    SBOM_FORMAT,
    SIGNATURE_ALGORITHM,
    SignedPackage,
    Signer,
)
from engine.compiler.types import DataType, TypeBinding, python_type, sql_type
from engine.compiler.validation import (
    CERTIFIED_LIFECYCLE,
    BlueprintValidator,
    ValidationReport,
)

__all__ = [
    # IR + type system
    "IR_VERSION",
    "BlueprintIR",
    "BlueprintFamily",
    "CertificationStatus",
    "RelationshipKind",
    "Provenance",
    "Certification",
    "Attribute",
    "Index",
    "DataRelationship",
    "Entity",
    "DataType",
    "TypeBinding",
    "sql_type",
    "python_type",
    # serialization
    "to_canonical_dict",
    "serialize",
    "serialize_bytes",
    "from_dict",
    "deserialize",
    # parse
    "parse",
    "parse_document",
    "parse_text",
    "parse_bytes",
    "is_supported",
    "ensure_supported",
    "SUPPORTED_FAMILIES",
    # validation
    "BlueprintValidator",
    "ValidationReport",
    "CERTIFIED_LIFECYCLE",
    # resolution + cycles
    "DependencyResolver",
    "ResolvedBuild",
    "detect_cycle",
    "assert_acyclic",
    "topological_order",
    # data compiler
    "DataBlueprintCompiler",
    "CompiledBlueprint",
    "CompiledArtifact",
    "ArtifactKind",
    "provenance_chain",
    "snake_case",
    # optimization
    "Optimizer",
    "OptimizedBlueprint",
    # packaging
    "Packager",
    "Package",
    "PACKAGE_FORMAT",
    "COMPILER_TOOLCHAIN",
    "TOOLCHAIN_VERSION",
    # signing
    "Signer",
    "SignedPackage",
    "SIGNATURE_ALGORITHM",
    "SBOM_FORMAT",
    # publishing
    "Publisher",
    "PublishedArtifact",
    # pipeline
    "CompilerPipeline",
    "CompilationResult",
    "BuildResult",
    "COMPILE_CONTRACT",
    # gap + errors
    "GapReport",
    "Stage",
    "CompilerError",
    "ParseError",
    "SerializationError",
    "ValidationError",
    "CertificationError",
    "DependencyError",
    "CyclicDependencyError",
    "CompilationError",
    "OptimizationError",
    "PackagingError",
    "SigningError",
    "PublishingError",
    "PipelineError",
]
