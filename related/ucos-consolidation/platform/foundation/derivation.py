"""WP-09 — Derivation Purity (PRJ-C2 / ACT-C2).

The engine for **Derived Truth**: a deterministic derivation engine, pure derivation
contracts, immutable pinned inputs, derivation verification, reproducible outputs,
and dependency-graph validation. It realizes:

    * **AIF-L18 Derivation Purity & Version Stamp** — derived value = pure
      ``f(Source, Recorded Truth, Generator-version)``; stamped; **no hidden state or
      wall-clock**;
    * **AIF-L20 Non-Mixing of Determinisms** — identity determinism (recorded) is
      never derived from generated determinism: a *derived* value may never be
      declared as an identity-determinism source.

Design (AX-01/AX-02 bifurcation of truth):
    * A :class:`DerivationContract` pins every input by its Canonical Content Form
      digest (WP-06), the generator version, the dependency edges, and the declared
      identity-determinism sources. Inputs are **immutable**: a derivation refuses to
      run if the supplied content does not match its pinned digest (drift fails
      closed).
    * :meth:`DerivationEngine.derive` enforces purity by **re-running the deriver**
      and comparing digests — a value that changes across identical runs (hidden
      state / wall-clock) is rejected as impure (AIF-L18). The output carries a
      **version stamp** binding the generator version and the input digests.
    * The dependency graph is validated for **acyclicity and closure** (reusing the
      foundation :class:`~platform.foundation.dependencies.DependencyGraph`).

Deterministic and stdlib-only; nothing is written to the certified corpus (DP-03).
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from enum import Enum
from platform.foundation.canonical import CanonicalProfile, content_digest
from platform.foundation.dependencies import DependencyGraph
from platform.foundation.errors import DerivationError, DerivationPurityError
from typing import Any

from engine.foundation.obs.logging import get_logger

_logger = get_logger("foundation.derivation")

#: The self-describing export format tag (semantic version — widens append-only).
DERIVATION_LEDGER_FORMAT = "ucos-derivation-ledger/1.0.0"

#: A pure derivation function: derived output = f(inputs). It must depend on nothing
#: beyond the supplied inputs (no hidden state, no wall-clock — AIF-L18).
Deriver = Callable[[Mapping[str, Any]], Any]


class InputKind(str, Enum):
    """The truth-kind of a derivation input (AX-01 bifurcation of truth)."""

    SOURCE = "source"  # raw source material
    RECORDED = "recorded"  # Recorded Truth (identity, events, attestations)
    DERIVED = "derived"  # a prior derivation output (Derived Truth)


@dataclass(frozen=True, slots=True)
class DerivationInput:
    """An immutable, digest-pinned derivation input (AIF-L18)."""

    name: str
    kind: InputKind
    digest: str

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise DerivationError("derivation input name is required")
        if not isinstance(self.kind, InputKind):
            raise DerivationError("derivation input kind must be an InputKind", name=self.name)
        if not isinstance(self.digest, str) or not self.digest:
            raise DerivationError("derivation input digest is required", name=self.name)

    @classmethod
    def of(
        cls,
        name: str,
        content: Any,
        *,
        kind: InputKind = InputKind.SOURCE,
        profile: CanonicalProfile | None = None,
    ) -> DerivationInput:
        """Pin an input to the CCF digest (WP-06) of its content."""
        return cls(name=name, kind=kind, digest=content_digest(content, profile).value)

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "kind": self.kind.value, "digest": self.digest}


@dataclass(frozen=True, slots=True)
class DerivationContract:
    """A pure derivation contract: pinned inputs, version, deps, identity sources.

    Declares everything a derivation depends on so the derived output is a pure,
    reproducible function of (Source + Recorded Truth + Generator-version) (AIF-L18).
    ``identity_sources`` names the inputs that seed identity determinism; they may
    never be :attr:`InputKind.DERIVED` (non-mixing, AIF-L20).
    """

    output_name: str
    generator_version: str
    inputs: tuple[DerivationInput, ...]
    dependencies: tuple[tuple[str, str], ...] = ()
    identity_sources: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.output_name, str) or not self.output_name.strip():
            raise DerivationError("derivation output name is required")
        if not isinstance(self.generator_version, str) or not self.generator_version.strip():
            raise DerivationError("generator version is required", output=self.output_name)
        names = [i.name for i in self.inputs]
        if len(names) != len(set(names)):
            raise DerivationError("duplicate derivation input name", output=self.output_name)
        known = set(names)
        for source in self.identity_sources:
            if source not in known:
                raise DerivationError("identity source is not a declared input", source=source)
        # Non-mixing (AIF-L20): a derived value may never seed identity determinism.
        for inp in self.inputs:
            if inp.name in self.identity_sources and inp.kind is InputKind.DERIVED:
                raise DerivationPurityError(
                    "a derived value cannot be an identity-determinism source (AIF-L20)",
                    source=inp.name,
                )
        for node, depends_on in self.dependencies:
            if node not in known and node != self.output_name:
                raise DerivationError("dependency references an unknown node", node=node)
            if depends_on not in known and depends_on != self.output_name:
                raise DerivationError("dependency references an unknown node", node=depends_on)

    @property
    def input_names(self) -> tuple[str, ...]:
        return tuple(i.name for i in self.inputs)

    @property
    def digest_map(self) -> dict[str, str]:
        return {i.name: i.digest for i in self.inputs}

    def dependency_graph(self) -> DependencyGraph:
        """Build the derivation dependency graph (output depends on every input)."""
        graph = DependencyGraph()
        explicit: dict[str, set[str]] = {}
        for node, depends_on in self.dependencies:
            explicit.setdefault(node, set()).add(depends_on)
        for name in self.input_names:
            graph.add(name, explicit.get(name, set()))
        # The output depends on every input, plus any explicit output dependency.
        output_deps = set(self.input_names) | explicit.get(self.output_name, set())
        graph.add(self.output_name, output_deps)
        return graph

    def validate_dependencies(self) -> tuple[str, ...]:
        """Validate the dependency graph is acyclic and closed; return its order."""
        return self.dependency_graph().topological_order()

    def to_dict(self) -> dict[str, Any]:
        return {
            "output_name": self.output_name,
            "generator_version": self.generator_version,
            "inputs": [i.to_dict() for i in self.inputs],
            "dependencies": [list(edge) for edge in self.dependencies],
            "identity_sources": list(self.identity_sources),
        }


@dataclass(frozen=True, slots=True)
class DerivationResult:
    """A stamped, reproducible derivation output (Derived Truth, AIF-L18).

    Carries the output value, its Canonical Content Form digest, and the **version
    stamp** binding the generator version and the pinned input digests — so the
    derivation is a verifiable, pure function of its declared inputs.
    """

    output_name: str
    generator_version: str
    output_digest: str
    input_digests: tuple[tuple[str, str], ...]
    output: Any = field(default=None, compare=False)

    @property
    def stamp(self) -> dict[str, Any]:
        """The version stamp: generator version + sorted input digests."""
        return {
            "generator_version": self.generator_version,
            "inputs": [list(pair) for pair in self.input_digests],
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "output_name": self.output_name,
            "generator_version": self.generator_version,
            "output_digest": self.output_digest,
            "input_digests": [list(pair) for pair in self.input_digests],
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> DerivationResult:
        if not isinstance(data, Mapping):
            raise DerivationError("derivation result record must be a mapping")
        try:
            return cls(
                output_name=data["output_name"],
                generator_version=data["generator_version"],
                output_digest=data["output_digest"],
                input_digests=tuple(tuple(pair) for pair in data["input_digests"]),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise DerivationError("derivation result record is malformed") from exc


class DerivationEngine:
    """A deterministic, purity-enforcing derivation engine (WP-09).

    Append-only: it records each reproducible derivation by output name. Re-deriving
    an identical result is idempotent; a conflicting result for the same output name
    fails closed. Purity is enforced by re-running the deriver and comparing digests
    (AIF-L18) and by rejecting derived identity sources (AIF-L20, via the contract).
    """

    __slots__ = ("_results", "_order")

    def __init__(self) -> None:
        self._results: dict[str, DerivationResult] = {}
        self._order: list[str] = []

    def __len__(self) -> int:
        return len(self._order)

    def __contains__(self, output_name: str) -> bool:
        return output_name in self._results

    @property
    def results(self) -> tuple[DerivationResult, ...]:
        return tuple(self._results[n] for n in self._order)

    def _prepare(
        self,
        contract: DerivationContract,
        deriver: Deriver,
        source_values: Mapping[str, Any],
        profile: CanonicalProfile | None,
    ) -> DerivationResult:
        """Validate inputs + purity and return the stamped result (no recording)."""
        # Dependency graph must be acyclic and closed (fails closed).
        contract.validate_dependencies()
        provided = set(source_values)
        declared = set(contract.input_names)
        if provided != declared:
            raise DerivationError(
                "provided values do not match the contract inputs",
                missing=sorted(declared - provided),
                unexpected=sorted(provided - declared),
            )
        # Immutable inputs: supplied content must match the pinned digest (AIF-L18).
        for inp in contract.inputs:
            actual = content_digest(source_values[inp.name], profile).value
            if actual != inp.digest:
                raise DerivationError(
                    "derivation input drifted from its pinned digest", input=inp.name
                )
        # Purity: an identical re-derivation must be byte-identical (AIF-L18).
        first = deriver(source_values)
        second = deriver(source_values)
        try:
            first_digest = content_digest(first, profile)
            second_digest = content_digest(second, profile)
        except Exception as exc:  # non-serializable output ⇒ not a pure Derived value
            raise DerivationError("derivation output is not canonical") from exc
        if first_digest.value != second_digest.value:
            raise DerivationPurityError(
                "derivation is not reproducible (hidden state or wall-clock)",
                output=contract.output_name,
            )
        return DerivationResult(
            output_name=contract.output_name,
            generator_version=contract.generator_version,
            output_digest=first_digest.value,
            input_digests=tuple(sorted(contract.digest_map.items())),
            output=first,
        )

    def derive(
        self,
        contract: DerivationContract,
        deriver: Deriver,
        source_values: Mapping[str, Any],
        *,
        profile: CanonicalProfile | None = None,
    ) -> DerivationResult:
        """Derive a stamped, reproducible output; record it (idempotent)."""
        result = self._prepare(contract, deriver, source_values, profile)
        existing = self._results.get(result.output_name)
        if existing is not None:
            if (
                existing.output_digest != result.output_digest
                or existing.generator_version != result.generator_version
                or existing.input_digests != result.input_digests
            ):
                raise DerivationError(
                    "output name already derived with a different result",
                    output=result.output_name,
                )
            return existing
        self._results[result.output_name] = result
        self._order.append(result.output_name)
        _logger.info(
            "foundation.derivation.derived",
            output=result.output_name,
            generator_version=result.generator_version,
            digest=result.output_digest,
        )
        return result

    def verify(
        self,
        contract: DerivationContract,
        deriver: Deriver,
        source_values: Mapping[str, Any],
        result: DerivationResult,
        *,
        profile: CanonicalProfile | None = None,
    ) -> bool:
        """Re-derive and confirm the output digest + stamp match ``result`` (replay)."""
        try:
            recomputed = self._prepare(contract, deriver, source_values, profile)
        except DerivationError:
            return False
        return (
            recomputed.output_digest == result.output_digest
            and recomputed.generator_version == result.generator_version
            and recomputed.input_digests == result.input_digests
        )

    def get(self, output_name: str) -> DerivationResult:
        result = self._results.get(output_name)
        if result is None:
            raise DerivationError("no derivation for output name", output=output_name)
        return result

    def export(self) -> dict[str, Any]:
        return {
            "ledger_format": DERIVATION_LEDGER_FORMAT,
            "count": len(self._order),
            "results": [self._results[n].to_dict() for n in self._order],
        }

    to_dict = export


__all__ = [
    "DERIVATION_LEDGER_FORMAT",
    "Deriver",
    "InputKind",
    "DerivationInput",
    "DerivationContract",
    "DerivationResult",
    "DerivationEngine",
]
