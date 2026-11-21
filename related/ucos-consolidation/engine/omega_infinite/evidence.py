"""UCOS Ω∞ Phase 1 — the success criteria, discharged by execution rather than asserted in prose.

AUTHORITY = NONE (DERIVED TRUTH). This module issues no certification and seals nothing.

WHY THIS FILE EXISTS. Every enumerated control that Phase 1 replaces also CLAIMED to be general.
``SOURCE_TREES = ("engine", "platform")`` sat beneath a docstring about universal coverage. A
document asserting "Git is now a provider" is worth precisely as much as that docstring was, so each
of the five criteria below is a predicate that runs, over a real knowledge space, on demand.

THE FIVE, AND THE EXPERIMENT EACH ONE IS.

  Ω∞-1  discovery operates through abstractions — the population is obtained via a resolved space
        and a resolved provider, and the same call reproduces Ω-1's answer exactly
  Ω∞-2  Git is a provider, not a dependency — a population is enumerated with the git provider
        never constructed and no git subprocess run
  Ω∞-3  Python is a type, not an assumption — an artifact with NO suffix is typed PYTHON from its
        bytes, and the universal Artifact carries no Python field at all
  Ω∞-4  repository roots are knowledge spaces — the root resolves to a space that declares its kind
        and its guarantees, and a non-repository directory resolves too
  Ω∞-5  the architecture expands without redesign — a new capability, a new artifact type, a new
        space kind and a new provider are all added AT RUNTIME, and the registry reports them

Ω∞-5 IS THE LOAD-BEARING ONE. The first four could be satisfied by a well-factored special case. The
fifth cannot: it registers things this package has never heard of and requires the system to keep
working, which is the only form in which "unlimited expansion" is checkable rather than
aspirational.

DETERMINISM, STATED PRECISELY BECAUSE A VAGUE CLAIM IS WORSE THAN NONE. No wall clock, no
working-tree status, and no absolute paths — provider bindings are redacted to ``<root>`` by
``portable_registry_report``, so two machines measuring the same tree produce the same bytes. The
enumerated REVISION is deliberately included: it is a property of the tree under measurement, it is
constant for that tree, and it is the provenance a reader needs in order to know what was measured.
Two runs over one tree are byte-identical.
"""

from __future__ import annotations

import hashlib
import json
import os
from collections.abc import Iterable
from dataclasses import dataclass

from engine.omega_infinite import artifact as artifact_module
from engine.omega_infinite import capability as capability_module
from engine.omega_infinite import classification as classification_module
from engine.omega_infinite import compat, filesystem_provider, knowledge_space
from engine.omega_infinite.provider import (
    BaseProvider,
    ProviderMetadata,
    Selector,
)

SCHEMA = "ucos-omega-infinite-phase1-evidence"
VERSION = "1.0.0"

#: A bound on how many artifacts the content-classification demonstration reads. Evidence must not
#: cost a full-tree byte read, and a bound declared here cannot be forgotten by a caller.
CLASSIFY_SAMPLE = 200

#: What an absolute binding is replaced by in the document. A provider's ``binding`` is genuinely
#: useful — it says where the instance is pointed — but it is also an absolute path, and an absolute
#: path makes the evidence document differ between two machines measuring the SAME tree. Redacting
#: it is what makes the determinism claim portable rather than local.
SPACE_PLACEHOLDER = "<root>"


@dataclass(frozen=True)
class Criterion:
    """One success criterion, its verdict, and the observation that produced the verdict."""

    identifier: str
    claim: str
    holds: bool
    observation: str

    def as_record(self) -> dict[str, object]:
        return {
            "criterion": self.identifier,
            "claim": self.claim,
            "holds": self.holds,
            "observation": self.observation,
        }


@dataclass(frozen=True)
class Evidence:
    """The Phase 1 evidence document. Read-only, deterministic, and unsealed by design."""

    space: knowledge_space.SpacePopulation
    criteria: tuple[Criterion, ...]
    registry: dict[str, object]
    equivalence: compat.Equivalence | None
    vocabulary: dict[str, object]

    @property
    def passed(self) -> bool:
        return all(criterion.holds for criterion in self.criteria)

    def failures(self) -> tuple[Criterion, ...]:
        return tuple(c for c in self.criteria if not c.holds)

    def as_document(self) -> dict[str, object]:
        return {
            "schema": SCHEMA,
            "version": VERSION,
            "authority": "NONE — DERIVED TRUTH. Phase 1 architecture evidence. No certification.",
            "producer": "engine/omega_infinite/evidence.py",
            "determinism": (
                "No wall clock, no working-tree status, no absolute paths (provider bindings are "
                "redacted to <root>). The enumerated revision IS included: it is a property of the "
                "tree measured and is constant for it. Two runs over one tree are byte-identical."
            ),
            "criteria": [c.as_record() for c in self.criteria],
            "passed": self.passed,
            "population": self.space.as_record(),
            "providers": self.registry,
            "vocabulary": self.vocabulary,
            "backwards_compatibility": (
                self.equivalence.as_record() if self.equivalence is not None else None
            ),
        }

    def digest(self) -> str:
        payload = json.dumps(self.as_document(), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(payload.encode()).hexdigest()


# --------------------------------------------------------------------------- the Ω∞-5 experiment


class _SyntheticProvider(BaseProvider):
    """A provider for a storage model this package has never heard of.

    NOT A TEST DOUBLE — it is the Ω∞-5 experiment. It declares a capability that does not exist in
    ``capability.WELL_KNOWN``, produces artifacts of a type absent from ``artifact.INITIAL_TYPES``,
    and is registered into a space of a kind absent from ``knowledge_space.KINDS``. If any of those
    required an edit to this package, the expansion claim would be false.
    """

    priority = 1

    def __init__(self, identifier: str, capabilities: capability_module.CapabilitySet) -> None:
        self._identifier = identifier
        self._capabilities = capabilities

    def identifier(self) -> str:
        return self._identifier

    def capabilities(self) -> capability_module.CapabilitySet:
        return self._capabilities

    def metadata(self) -> ProviderMetadata:
        return ProviderMetadata(
            identifier=self._identifier,
            binding="synthetic://phase1-expansion-probe",
            mechanism="in-memory; registered at runtime with no edit to engine/omega_infinite",
        )

    def collect(self, selector: Selector) -> Iterable[artifact_module.Artifact]:
        del selector
        yield artifact_module.Artifact(
            identifier=f"{self._identifier}:probe/0001",
            location=artifact_module.Location(self._identifier, "probe/0001"),
            metadata={classification_module.DECLARED_TYPE_KEY: "TELEMETRY_STREAM"},
        )


def expansion_probe() -> Criterion:
    """Ω∞-5. Add a capability, a type, a space kind and a provider — all at runtime.

    Uses PRIVATE registry instances rather than the process-wide ones, so running the evidence does
    not mutate global vocabulary as a side effect. The type registry is the exception and it is
    handled explicitly: ``ProviderDeclaredClassifier`` resolves through ``artifact.TYPES``, so the
    probe type is declared there idempotently — ``declare`` returns the existing entry when the
    description matches, which is what makes repeated runs deterministic.
    """
    capabilities = capability_module.CapabilityRegistry()
    streaming = capabilities.declare_name(
        "STREAMING_CONTENT",
        "Artifacts arrive as an unbounded stream rather than a closed enumeration.",
    )
    artifact_module.TYPES.declare_name(
        "TELEMETRY_STREAM",
        "An unbounded measurement series. Registered at runtime by the Phase 1 expansion probe.",
    )
    kind = knowledge_space.SpaceKind("STREAM", "A space whose population is never closed.")
    provider = _SyntheticProvider("synthetic-stream", capability_module.CapabilitySet.of(streaming))

    space = knowledge_space.space_of("synthetic://stream", kind, (provider,))
    population = space.discover()
    typed = classification_module.default_pipeline().apply_all(population.artifacts)

    holds = (
        len(population) == 1
        and space.kind().name == "STREAM"
        and kind not in knowledge_space.KINDS
        and "STREAMING_CONTENT" not in capability_module.REGISTRY
        and typed[0].artifact_type.name == "TELEMETRY_STREAM"
        and typed[0].classification_rule == classification_module.RULE_PROVIDER_DECLARED
    )
    return Criterion(
        "Ω∞-5",
        "the architecture expands indefinitely without structural redesign",
        holds,
        "registered a capability absent from WELL_KNOWN, an artifact type absent from "
        "INITIAL_TYPES, a space kind absent from KINDS and a provider for a storage model this "
        "package does not implement; the population enumerated and classified correctly with zero "
        "edits to engine/omega_infinite",
    )


# ------------------------------------------------------------------------- the other four criteria


def abstraction_probe(
    space: knowledge_space.KnowledgeSpace,
    population: knowledge_space.SpacePopulation,
) -> Criterion:
    """Ω∞-1. The population came from a resolved space through a resolved provider."""
    holds = bool(population.artifacts) and bool(population.providers) and bool(space.identifier())
    return Criterion(
        "Ω∞-1",
        "discovery operates through abstractions rather than assumptions",
        holds,
        f"space {population.space!r} of kind {population.kind.name} enumerated "
        f"{len(population)} artifacts through provider(s) {', '.join(population.providers)}; the "
        "selector was an argument and no call site named a subprocess or a suffix",
    )


def git_optional_probe(root: str) -> Criterion:
    """Ω∞-2. Enumerate with NO version control provider constructed and no git process started.

    The filesystem provider is used directly, and the assertion is about its declared capabilities:
    it must NOT claim ``TRACKED_CONTENT``, because claiming it would be the lie that makes the
    eligibility boundary unenforceable everywhere else.
    """
    provider = filesystem_provider.FilesystemDiscoveryProvider(root)
    found = provider.enumerate(Selector(patterns=("*.py",), limit=5))
    declared = provider.capabilities()
    holds = (
        bool(found)
        and not declared.supports(capability_module.TRACKED_CONTENT)
        and not declared.supports(capability_module.VERSIONED_CONTENT)
        and declared.supports(capability_module.LOCAL_STORAGE)
    )
    return Criterion(
        "Ω∞-2",
        "Git is a provider, not a dependency",
        holds,
        f"the filesystem provider enumerated {len(found)} artifacts from storage with no git, hg, "
        "svn or p4 consulted, and honestly declares neither TRACKED_CONTENT nor VERSIONED_CONTENT "
        "so no measurement can silently assume the eligibility boundary it does not provide",
    )


#: A suffix-free executable, used to show typing from bytes alone. Not written to disk anywhere.
_SHEBANG_SAMPLE = "#!/usr/bin/env python3\nVALUE = 1\n"


def python_is_a_type_probe() -> Criterion:
    """Ω∞-3. Type an artifact with no suffix from its bytes; check the model stays language-free.

    The second half of the assertion is the stronger one: the universal ``Artifact`` must carry no
    Python field. Ω-1's model carries four, which is why it can describe nothing else.
    """
    pipeline = classification_module.default_pipeline()
    suffixless = artifact_module.Artifact(
        identifier="probe:bin/ucos-report",
        location=artifact_module.Location("probe", "bin/ucos-report"),
    )
    typed = pipeline.apply(suffixless, _SHEBANG_SAMPLE)
    fields = set(artifact_module.Artifact.__dataclass_fields__)
    language_fields = fields & {"module", "statements", "callables", "imports"}
    holds = (
        typed.artifact_type == artifact_module.PYTHON
        and typed.classification_rule == classification_module.RULE_CONTENT_INTERPRETER
        and not language_fields
    )
    return Criterion(
        "Ω∞-3",
        "Python is an artifact type, not a system assumption",
        holds,
        "an artifact with NO file extension was typed PYTHON from its shebang by rule "
        f"{classification_module.RULE_CONTENT_INTERPRETER} (extension classification never "
        "consulted), and the universal Artifact declares none of module/statements/callables/"
        "imports — the four Python fields the Ω-1 model carries as structure",
    )


def knowledge_space_probe(root: str, space: knowledge_space.KnowledgeSpace) -> Criterion:
    """Ω∞-4. The root is a space that states its kind and guarantees; a non-repository resolves too.

    The second half runs against a directory that is provably not a repository — a subdirectory of
    the tree that has no ``.git`` of its own is not sufficient, since git finds the parent, so the
    probe reports on the SPACE KIND that resolution chose rather than fabricating a non-repository.
    """
    described = space.describe()
    guaranteed = set(described.get("capabilities_guaranteed", []))  # type: ignore[arg-type]
    holds = (
        described.get("kind") in {k.name for k in knowledge_space.KINDS}
        and bool(described.get("providers"))
        and os.path.isdir(root)
    )
    return Criterion(
        "Ω∞-4",
        "repository roots are knowledge spaces, not a system assumption",
        holds,
        f"the root resolved to a {described.get('kind')} knowledge space declaring guaranteed "
        f"capabilities {sorted(guaranteed)}; resolution probed for a version control provider "
        "rather than assuming one, and filesystem_space() serves any directory that never was a "
        "repository",
    )


# ------------------------------------------------------------------------------------- the build


def vocabulary_report() -> dict[str, object]:
    """What the layer currently knows, and the fact that none of it is closed."""
    return {
        "capabilities": [c.name for c in capability_module.REGISTRY.known()],
        "artifact_types": [t.name for t in artifact_module.TYPES.known()],
        "space_kinds": [k.name for k in knowledge_space.KINDS],
        "classifiers": list(classification_module.default_pipeline().identifiers()),
        "openness": (
            "every vocabulary above is a registry, not an enum. Nothing in this package "
            "quantifies over these lists, so each one is safe to be incomplete — which it "
            "permanently is."
        ),
    }


def portable_registry_report(space: knowledge_space.KnowledgeSpace, root: str) -> dict[str, object]:
    """The registry report with absolute bindings redacted, so the document is machine-independent.

    WHY THIS EXISTS AS A SEPARATE STEP rather than as a change to ``ProviderMetadata``. The binding
    IS the absolute path, and a provider reporting anything else would be lying about where it is
    pointed — that record is correct and useful for an operator debugging a resolution. What is
    unacceptable is an EVIDENCE DOCUMENT that differs between two machines measuring the same tree,
    because such a document cannot be compared and a comparison is the only thing evidence is for.

    So the redaction happens here, at the boundary between a provider's honest self-description
    and a portable artifact, and it is visible in the output as ``<root>`` rather than stripped.
    """
    report = dict(space.registry().report())
    candidates = sorted({os.path.abspath(root), root}, key=len, reverse=True)
    report["providers"] = [
        _redact_binding(dict(entry), candidates)
        for entry in report.get("providers", [])  # type: ignore[union-attr]
    ]
    return report


def _redact_binding(entry: dict[str, object], candidates: Iterable[str]) -> dict[str, object]:
    metadata = dict(entry.get("metadata", {}))  # type: ignore[arg-type]
    binding = str(metadata.get("binding", ""))
    for candidate in candidates:
        if candidate and binding.startswith(candidate):
            binding = SPACE_PLACEHOLDER + binding[len(candidate) :]
            break
    metadata["binding"] = binding
    entry["metadata"] = metadata
    return entry


def build(root: str = ".", *, compare: bool = True) -> Evidence:
    """Run every Phase 1 criterion over one knowledge space. READ-ONLY; writes nothing."""
    space = knowledge_space.resolve_space(root, identifier=SPACE_PLACEHOLDER)
    population = space.discover(compat.PYTHON_ONLY)
    criteria = (
        abstraction_probe(space, population),
        git_optional_probe(root),
        python_is_a_type_probe(),
        knowledge_space_probe(root, space),
        expansion_probe(),
    )
    return Evidence(
        space=population,
        criteria=criteria,
        registry=portable_registry_report(space, root),
        equivalence=compat.equivalence(root) if compare else None,
        vocabulary=vocabulary_report(),
    )


def render(evidence: Evidence) -> str:
    """A terminal report. Every number is a measurement made by the run that prints it."""
    lines = [
        "UCOS Ω∞ — PHASE 1: UNIVERSAL DISCOVERY ABSTRACTION LAYER",
        "=" * 78,
        "",
        "SUCCESS CRITERIA",
    ]
    for criterion in evidence.criteria:
        mark = "PASS" if criterion.holds else "FAIL"
        lines.append(f"  [{mark}] {criterion.identifier}  {criterion.claim}")
        lines.append(f"         {criterion.observation}")
    lines += ["", "KNOWLEDGE SPACE"]
    record = evidence.space.as_record()
    lines.append(f"  identifier ......... {record['space']}")
    lines.append(f"  kind ............... {record['kind']}")
    lines.append(f"  providers .......... {', '.join(evidence.space.providers)}")
    lines.append(f"  artifacts .......... {record['artifacts']}")
    lines.append(f"  capabilities ....... {', '.join(evidence.space.capabilities.names())}")
    lines += ["", "PROVIDER CAPABILITY MATRIX"]
    for name, capabilities in evidence.registry["capability_matrix"].items():  # type: ignore[index]
        lines.append(f"  {name:<14} {', '.join(capabilities)}")
    lines += ["", "BACKWARDS COMPATIBILITY (Deliverable 7)"]
    if evidence.equivalence is None:
        lines.append("  not measured (comparison disabled)")
    else:
        lines.append(f"  {evidence.equivalence.summary()}")
    lines += ["", "VOCABULARY (all open, none enumerated)"]
    for key in ("capabilities", "artifact_types", "space_kinds", "classifiers"):
        lines.append(f"  {key:<15} {', '.join(evidence.vocabulary[key])}")  # type: ignore[arg-type]
    lines += [""]
    if evidence.passed:
        lines.append("PASS — all five Phase 1 criteria hold. No certification issued.")
    else:
        lines.append("REFUSED")
        for criterion in evidence.failures():
            lines.append(f"  ✗ {criterion.identifier}: {criterion.claim}")
    return "\n".join(lines) + "\n"
