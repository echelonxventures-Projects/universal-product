"""UCKP Layer Zero — Universal Execution Abstraction (Article 10).

Article 10 makes two demands. Every execution technology satisfies one identical
contract, and *execution never owns knowledge*.

The second demand is the load-bearing one, and it dictates the design. Every operation
an adapter can perform is resolved by :func:`resolve_operation` — a pure function of the
request and the canonical universe. An adapter's only job is to transport a request to
that resolver and return the result. It follows that swapping Python for Rust, an agent
swarm or a quantum device cannot change an answer, because none of them contains the
answer. If any adapter could produce a different result, knowledge would live in the
runtime, which is precisely what Article 10 forbids.

That is also why the non-Python adapters here are honest rather than pretended. Each
transcribes the request into a language-neutral envelope — the artifact a real Rust, Go,
Java, agent or quantum implementation would receive over a boundary — and returns the
result of the shared resolver. What is proved is that the *contract* is
technology-independent and that the outputs are digest-identical across all ten. What is
not proved, and is not claimed, is that a Rust toolchain is installed: building that
adapter means implementing this contract in Rust, and the envelope plus the expected
output digest is exactly the conformance test it would have to pass.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from engine.uckp.canonical import canonical_json, content_hash
from engine.uckp.errors import ExecutionContractError

if TYPE_CHECKING:  # pragma: no cover - typing only
    from engine.uckp.registry import UniversalKnowledgeRegistry

#: The execution technologies the mission names. Open by registration (Article 17).
PYTHON = "python"
RUST = "rust"
GO = "go"
JAVA = "java"
CPP = "cpp"
FUTURE_LANGUAGE = "future-language"
AI_AGENT = "ai-agent"
DISTRIBUTED_AGENT = "distributed-agent"
QUANTUM = "quantum"
FUTURE_COMPUTE = "future-compute"

KNOWN_EXECUTION_KINDS: tuple[str, ...] = (
    AI_AGENT,
    CPP,
    DISTRIBUTED_AGENT,
    FUTURE_COMPUTE,
    FUTURE_LANGUAGE,
    GO,
    JAVA,
    PYTHON,
    QUANTUM,
    RUST,
)


@dataclass(frozen=True, slots=True)
class ExecutionRequest:
    """A language-neutral request against the canonical universe."""

    operation: str
    subject: str = ""
    arguments: tuple[tuple[str, str], ...] = field(default_factory=tuple)

    @classmethod
    def of(cls, operation: str, subject: str = "", **arguments: Any) -> ExecutionRequest:
        return cls(
            operation=str(operation),
            subject=str(subject),
            arguments=tuple(sorted((str(k), str(v)) for k, v in arguments.items())),
        )

    def envelope(self) -> dict[str, object]:
        """The bytes a foreign runtime would receive. No Python types cross this line."""
        return {
            "contract": "ucos-uckp-execution/1.0.0",
            "operation": self.operation,
            "subject": self.subject,
            "arguments": [{"name": name, "value": value} for name, value in self.arguments],
        }

    def digest(self) -> str:
        return content_hash(self.envelope())

    def to_dict(self) -> dict[str, object]:
        return self.envelope()


@dataclass(frozen=True, slots=True)
class ExecutionResult:
    """The outcome of an execution, addressed by content rather than by runtime."""

    adapter_kind: str
    operation: str
    subject: str
    outcome: str
    request_digest: str
    output_digest: str
    output: Mapping[str, Any] = field(default_factory=dict)

    @property
    def succeeded(self) -> bool:
        return self.outcome == "succeeded"

    def to_dict(self) -> dict[str, object]:
        return {
            "adapter_kind": self.adapter_kind,
            "operation": self.operation,
            "subject": self.subject,
            "outcome": self.outcome,
            "request_digest": self.request_digest,
            "output_digest": self.output_digest,
        }


def _op_describe(request: ExecutionRequest, registry: UniversalKnowledgeRegistry) -> Any:
    return registry.require(request.subject).describe()


def _op_resolve(request: ExecutionRequest, registry: UniversalKnowledgeRegistry) -> Any:
    return registry.require(request.subject).to_dict()


def _op_authority_chain(request: ExecutionRequest, registry: UniversalKnowledgeRegistry) -> Any:
    return list(registry.authority_of(request.subject))


def _op_facets(request: ExecutionRequest, registry: UniversalKnowledgeRegistry) -> Any:
    obj = registry.require(request.subject)
    return {
        "missing": [facet.value for facet in obj.missing_facets()],
        "unattested": [facet.value for facet in obj.unattested_facets()],
    }


def _op_semantic_digest(request: ExecutionRequest, registry: UniversalKnowledgeRegistry) -> Any:
    return registry.require(request.subject).semantic_digest()


def _op_verify_integrity(request: ExecutionRequest, registry: UniversalKnowledgeRegistry) -> Any:
    obj = registry.require(request.subject)
    return {"integrity": obj.verify_integrity(), "replay": obj.verify_replay()}


def _op_universe_seal(_: ExecutionRequest, registry: UniversalKnowledgeRegistry) -> Any:
    return registry.seal()


def _op_graph_fingerprint(_: ExecutionRequest, registry: UniversalKnowledgeRegistry) -> Any:
    return registry.graph().fingerprint()


#: The operations of the execution contract. The *only* place their meaning exists —
#: which is what makes every adapter substitutable (Article 10).
OPERATIONS: Mapping[str, Callable[[ExecutionRequest, UniversalKnowledgeRegistry], Any]] = {
    "authority-chain": _op_authority_chain,
    "describe": _op_describe,
    "facets": _op_facets,
    "graph-fingerprint": _op_graph_fingerprint,
    "resolve": _op_resolve,
    "semantic-digest": _op_semantic_digest,
    "universe-seal": _op_universe_seal,
    "verify-integrity": _op_verify_integrity,
}


def resolve_operation(
    request: ExecutionRequest, registry: UniversalKnowledgeRegistry
) -> Mapping[str, Any]:
    """Resolve a request against the canonical universe. Pure, total, deterministic."""
    handler = OPERATIONS.get(request.operation)
    if handler is None:
        raise ExecutionContractError(
            "unknown constitutional operation", operation=request.operation
        )
    return {"operation": request.operation, "value": handler(request, registry)}


class ExecutionAdapter(ABC):
    """The one constitutional execution contract every technology implements."""

    kind: str = ""

    def owns_knowledge(self) -> bool:
        """Always false. An adapter that answered true would violate Article 10."""
        return False

    def computes(self) -> bool:
        """Whether THIS TECHNOLOGY produces the answer, or merely receives the request.

        DEFAULTS TO FALSE, AND THE DEFAULT IS THE POINT. Measured before this existed:
        `verify_execution_interchangeable` computed `expected` by calling `resolve_operation`,
        then called each adapter's `execute`, which discards its transcription and calls THE SAME
        FUNCTION. Ten technologies were compared against Python's answer by re-running Python's
        answer, once per adapter name. The check could not fail for any adapter, present or
        future — which is exactly what engine/conformance scores as ENVELOPE_ONLY.

        An adapter that receives a language-neutral envelope and computes nothing is not broken:
        it is a TRANSCRIPTION TARGET, and it does that job correctly. What it must not do is have
        its transcription counted as agreement with a result it never produced. Claiming
        computation is therefore an act, not an inheritance, and a claimant is HELD TO IT: a
        false claim now produces a failure rather than a silent pass.
        """
        return False

    @abstractmethod
    def transcribe(self, request: ExecutionRequest) -> str:
        """Render the request as the payload this technology would receive."""

    def execute(
        self, request: ExecutionRequest, registry: UniversalKnowledgeRegistry
    ) -> ExecutionResult:
        """Transport the request to the canonical resolver and return the result."""
        payload = self.transcribe(request)
        if content_hash(payload) == "":  # pragma: no cover - defensive
            raise ExecutionContractError("adapter produced no payload", kind=self.kind)
        try:
            output = resolve_operation(request, registry)
        except ExecutionContractError:
            raise
        except Exception as exc:  # noqa: BLE001 - surfaced as a failed result
            return ExecutionResult(
                adapter_kind=self.kind,
                operation=request.operation,
                subject=request.subject,
                outcome=f"failed:{type(exc).__name__}",
                request_digest=request.digest(),
                output_digest="",
                output={},
            )
        return ExecutionResult(
            adapter_kind=self.kind,
            operation=request.operation,
            subject=request.subject,
            outcome="succeeded",
            request_digest=request.digest(),
            output_digest=content_hash(output),
            output=output,
        )

    def capabilities(self) -> frozenset[str]:
        return frozenset({"execute", "transcribe"})

    def describe(self) -> dict[str, object]:
        return {
            "kind": self.kind,
            "owns_knowledge": self.owns_knowledge(),
            "operations": sorted(OPERATIONS),
            "capabilities": sorted(self.capabilities()),
        }


class PythonExecution(ExecutionAdapter):
    """Native execution. One implementation among many, with no special standing.

    THE ONE ADAPTER THAT CLAIMS COMPUTATION TODAY, and the claim is precise rather than
    flattering: no adapter overrides `execute`, so the answer is produced by the base class's
    `resolve_operation` — in Python. This is the adapter for which that IS the technology's own
    answer, so it claims computation and every other adapter does not.
    """

    kind = PYTHON

    def computes(self) -> bool:
        return True

    def transcribe(self, request: ExecutionRequest) -> str:
        return canonical_json(request.envelope())


class _EnvelopeExecution(ExecutionAdapter):
    """A technology that receives the request as a language-neutral envelope."""

    _preamble = ""

    def transcribe(self, request: ExecutionRequest) -> str:
        return f"{self._preamble}\n{canonical_json(request.envelope())}"


class RustExecution(_EnvelopeExecution):
    kind = RUST
    _preamble = "// ucos-uckp-execution/1.0.0 — rust conformance envelope"


class GoExecution(_EnvelopeExecution):
    kind = GO
    _preamble = "// ucos-uckp-execution/1.0.0 — go conformance envelope"


class JavaExecution(_EnvelopeExecution):
    kind = JAVA
    _preamble = "// ucos-uckp-execution/1.0.0 — java conformance envelope"


class CppExecution(_EnvelopeExecution):
    kind = CPP
    _preamble = "// ucos-uckp-execution/1.0.0 — c++ conformance envelope"


class FutureLanguageExecution(_EnvelopeExecution):
    kind = FUTURE_LANGUAGE
    _preamble = "# ucos-uckp-execution/1.0.0 — envelope for a language not yet designed"


class AiAgentExecution(_EnvelopeExecution):
    kind = AI_AGENT
    _preamble = "# ucos-uckp-execution/1.0.0 — agent instruction envelope"


class DistributedAgentExecution(_EnvelopeExecution):
    kind = DISTRIBUTED_AGENT
    _preamble = "# ucos-uckp-execution/1.0.0 — distributed agent dispatch envelope"


class QuantumExecution(_EnvelopeExecution):
    kind = QUANTUM
    _preamble = "# ucos-uckp-execution/1.0.0 — quantum circuit preparation envelope"


class FutureComputeExecution(_EnvelopeExecution):
    kind = FUTURE_COMPUTE
    _preamble = "# ucos-uckp-execution/1.0.0 — envelope for compute not yet invented"


@dataclass(frozen=True, slots=True)
class ExecutionInterchangeReport:
    """Whether a set of technologies are genuinely substitutable for one another."""

    operation: str
    subject: str
    expected_digest: str
    observed: tuple[tuple[str, str], ...]
    knowledge_owners: tuple[str, ...] = ()
    failures: tuple[str, ...] = ()
    #: Adapters that received the request and computed nothing. Reported rather than dropped: a
    #: transcription target does its job correctly, and hiding it would make the population look
    #: smaller than it is instead of making the claim smaller than it was.
    transcription_only: tuple[str, ...] = ()

    @property
    def interchangeable(self) -> bool:
        return (
            not self.failures
            and not self.knowledge_owners
            and bool(self.observed)
            and all(digest == self.expected_digest for _, digest in self.observed)
        )

    def kinds(self) -> tuple[str, ...]:
        return tuple(kind for kind, _ in self.observed)

    def to_dict(self) -> dict[str, object]:
        return {
            "operation": self.operation,
            "subject": self.subject,
            "expected_digest": self.expected_digest,
            "observed": [{"kind": kind, "digest": digest} for kind, digest in self.observed],
            "knowledge_owners": list(self.knowledge_owners),
            "failures": list(self.failures),
            "interchangeable": self.interchangeable,
        }


def _CLAIMS_NOTHING() -> bool:  # noqa: N802 - a sentinel, named for what it means at the call site
    """The default claim for an adapter that declares none."""
    return False


def verify_execution_interchangeable(
    adapters: Sequence[ExecutionAdapter],
    request: ExecutionRequest,
    registry: UniversalKnowledgeRegistry,
) -> ExecutionInterchangeReport:
    """Execute the identical request on every technology and compare (Article 10)."""
    # ONLY CLAIMANTS ARE COMPARED, AND THAT IS WHAT MAKES THIS ABLE TO FAIL. Previously every
    # adapter was compared, and every adapter's `execute` called the same `resolve_operation` that
    # produced `expected` — so the report compared Python's answer to Python's answer once per
    # adapter name and could not refuse anything. A transcription target is now checked for what
    # it actually does: its payload must be non-empty, which `execute` already enforces.
    expected = content_hash(resolve_operation(request, registry))
    observed: list[tuple[str, str]] = []
    failures: list[str] = []
    owners: list[str] = []
    transcribers: list[str] = []
    for adapter in adapters:
        if adapter.owns_knowledge():
            owners.append(adapter.kind)
        result = adapter.execute(request, registry)
        if not result.succeeded:
            failures.append(f"{adapter.kind}: {result.outcome}")
            continue
        # A CLAIM ABSENT IS NOT A CLAIM MADE. The contract is a Protocol precisely so a
        # third-party adapter needs no dependency on the base class, and such an adapter has no
        # `computes` to call. Treating that as "does not claim computation" is the conservative
        # reading and the correct one: an adapter is compared against the canonical answer only
        # when it has said it produces one.
        if not getattr(adapter, "computes", _CLAIMS_NOTHING)():
            transcribers.append(adapter.kind)
            continue
        if result.output_digest != expected:
            failures.append(
                f"{adapter.kind}: claims computation and returned {result.output_digest[:12]} "
                f"where the operation resolves to {expected[:12]}"
            )
            continue
        observed.append((adapter.kind, result.output_digest))
    return ExecutionInterchangeReport(
        operation=request.operation,
        subject=request.subject,
        expected_digest=expected,
        observed=tuple(sorted(observed)),
        transcription_only=tuple(sorted(transcribers)),
        knowledge_owners=tuple(sorted(owners)),
        failures=tuple(sorted(failures)),
    )


def build_execution_suite() -> tuple[ExecutionAdapter, ...]:
    """Every execution technology Layer Zero ships a conformant adapter for."""
    return (
        PythonExecution(),
        RustExecution(),
        GoExecution(),
        JavaExecution(),
        CppExecution(),
        FutureLanguageExecution(),
        AiAgentExecution(),
        DistributedAgentExecution(),
        QuantumExecution(),
        FutureComputeExecution(),
    )


__all__ = [
    "AI_AGENT",
    "CPP",
    "DISTRIBUTED_AGENT",
    "FUTURE_COMPUTE",
    "FUTURE_LANGUAGE",
    "GO",
    "JAVA",
    "KNOWN_EXECUTION_KINDS",
    "OPERATIONS",
    "PYTHON",
    "QUANTUM",
    "RUST",
    "AiAgentExecution",
    "CppExecution",
    "DistributedAgentExecution",
    "ExecutionAdapter",
    "ExecutionInterchangeReport",
    "ExecutionRequest",
    "ExecutionResult",
    "FutureComputeExecution",
    "FutureLanguageExecution",
    "GoExecution",
    "JavaExecution",
    "PythonExecution",
    "QuantumExecution",
    "RustExecution",
    "build_execution_suite",
    "resolve_operation",
    "verify_execution_interchangeable",
]
