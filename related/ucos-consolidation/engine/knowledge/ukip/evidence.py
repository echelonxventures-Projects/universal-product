"""UKIP Part 13 — Knowledge Evidence (EPIC-UKDA-003).

The durable, verifiable artifact of a knowledge intelligence run: one sealed bundle
carrying the constitution, the providers, the registry, the relationships, the graph,
discovery coverage, the provenance ledger, validation and certification.

Three properties make it evidence rather than a report:

    * **Sealed** — the bundle's ``seal`` is a digest over every component seal. A
      single altered record, relationship, or provenance step changes it, so the
      bundle attests to a specific state of knowledge and nothing else.
    * **Self-verifying** — :func:`verify_evidence` recomputes every seal from the
      bundle's own contents, so a stored bundle can be checked later without the
      registry that produced it.
    * **Deterministic** — no wall clock, no randomness, stable ordering throughout
      (IMP-007 §5), so re-running over unchanged knowledge reproduces the bundle
      byte-for-byte. That is what makes it usable as a CI gate: a changed seal means
      knowledge changed, not that time passed.

Writes refuse the frozen corpus (DP-03) by reusing the Foundation frozen-path guard,
so evidence can never be emitted into read-only territory.
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from engine.foundation.guards.frozen_paths import find_frozen_writes
from engine.knowledge.cko import DecisionRecord
from engine.knowledge.model import canonical_json, content_hash
from engine.knowledge.ukip.assimilation import AssimilationReport
from engine.knowledge.ukip.certification import (
    KnowledgeCertificate,
    KnowledgeIntelligenceCertifier,
)
from engine.knowledge.ukip.constitution import knowledge_constitution
from engine.knowledge.ukip.discovery import KnowledgeDiscovery
from engine.knowledge.ukip.errors import EvidenceError
from engine.knowledge.ukip.graph import KnowledgeIntelligenceGraph
from engine.knowledge.ukip.providers import ProviderRegistry
from engine.knowledge.ukip.registry import KnowledgeRegistry
from engine.knowledge.ukip.relationships import build_relationships
from engine.knowledge.ukip.validation import (
    KnowledgeIntelligenceValidator,
    ValidationReport,
)

#: The evidence bundle schema identifiers.
EVIDENCE_SCHEMA = "ucos-ukip-knowledge-evidence"
EVIDENCE_VERSION = "1.0.0"

#: The canonical filename an evidence bundle is written under.
EVIDENCE_FILENAME = "UKIP-KNOWLEDGE-EVIDENCE.json"

#: The component seals a bundle binds, in the order they are folded into the seal.
SEAL_COMPONENTS: tuple[str, ...] = (
    "constitution",
    "registry",
    "relationships",
    "graph",
    "provenance",
    "validation",
    "certification",
)


@dataclass(frozen=True, slots=True)
class KnowledgeEvidence:
    """A sealed, self-verifying record of one knowledge intelligence run."""

    sections: Mapping[str, Any]
    component_seals: Mapping[str, str]
    seal: str

    # -- verdicts --------------------------------------------------------------

    @property
    def accepted(self) -> bool:
        """True iff validation passed and certification was granted."""
        return bool(
            self.sections.get("validation", {}).get("accepted")
            and self.sections.get("certification", {}).get("certified")
        )

    def section(self, name: str) -> Any:
        if name not in self.sections:
            raise EvidenceError("evidence section not present", section=name)
        return self.sections[name]

    def recompute_seal(self) -> str:
        """Recompute the bundle seal from the recorded component seals."""
        return content_hash({name: self.component_seals.get(name, "") for name in SEAL_COMPONENTS})

    def verify(self) -> bool:
        """True iff the recorded seal matches a recomputation."""
        return self.seal == self.recompute_seal()

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": EVIDENCE_SCHEMA,
            "version": EVIDENCE_VERSION,
            "accepted": self.accepted,
            "seal": self.seal,
            "component_seals": dict(sorted(self.component_seals.items())),
            "sections": dict(self.sections),
        }

    def to_json(self) -> str:
        """The canonical JSON serialization (stable, newline-terminated)."""
        return json.dumps(self.to_dict(), sort_keys=True, indent=2, ensure_ascii=False) + "\n"


def build_evidence(
    registry: KnowledgeRegistry,
    *,
    providers: ProviderRegistry | None = None,
    assimilation: AssimilationReport | None = None,
    decisions: Iterable[DecisionRecord] = (),
    validation: ValidationReport | None = None,
    certificate: KnowledgeCertificate | None = None,
) -> KnowledgeEvidence:
    """Assemble the sealed evidence bundle for a knowledge registry.

    Every component is asked for its own seal rather than re-hashed here, so the
    bundle's seal is a fold of the layers' own attestations and cannot disagree with
    them.
    """
    carried = tuple(decisions) or (assimilation.decisions if assimilation is not None else ())
    constitution = knowledge_constitution()
    relationships = (
        assimilation.relationships if assimilation is not None else build_relationships(registry)
    )
    graph = KnowledgeIntelligenceGraph(registry, relationships)
    discovery = KnowledgeDiscovery(registry)
    report = validation or KnowledgeIntelligenceValidator().validate(
        registry,
        provenance=assimilation.provenance if assimilation is not None else None,
        decisions=carried,
    )
    cert = certificate or KnowledgeIntelligenceCertifier().certify(
        registry, decisions=carried, validation=report
    )

    constitution_payload = constitution.to_dict()
    sections: dict[str, Any] = {
        "constitution": constitution_payload,
        "providers": (
            providers.to_dict()
            if providers is not None
            else {"count": len(registry.provider_ids()), "providers": []}
        ),
        "registry": registry.to_document(),
        "relationships": relationships.to_dict(),
        "graph": graph.to_dict(),
        "discovery": discovery.coverage().to_dict(),
        "provenance": (
            assimilation.provenance.to_dict()
            if assimilation is not None
            else {
                "count": len(registry),
                "seal": content_hash(
                    {r.knowledge_id: r.provenance.seal for r in registry.records()}
                ),
            }
        ),
        "validation": report.to_dict(),
        "certification": cert.to_dict(),
    }
    if assimilation is not None:
        sections["assimilation"] = assimilation.to_document()

    component_seals = {
        "constitution": content_hash(constitution_payload),
        "registry": registry.seal(),
        "relationships": relationships.seal(),
        "graph": graph.seal(),
        "provenance": str(sections["provenance"].get("seal", "")),
        "validation": content_hash(report.to_dict()),
        "certification": cert.seal(),
    }
    seal = content_hash({name: component_seals[name] for name in SEAL_COMPONENTS})
    return KnowledgeEvidence(sections=sections, component_seals=component_seals, seal=seal)


def build_evidence_from_assimilation(
    report: AssimilationReport, *, providers: ProviderRegistry | None = None
) -> KnowledgeEvidence:
    """Build evidence directly from an assimilation run (the normal entry point)."""
    return build_evidence(report.registry, providers=providers, assimilation=report)


def verify_evidence(document: Mapping[str, Any]) -> tuple[bool, tuple[str, ...]]:
    """Verify a stored bundle against itself, returning ``(ok, defects)``.

    Recomputation uses only the document's own contents, so a bundle archived months
    ago can still be checked without the registry that produced it.
    """
    defects: list[str] = []
    if not isinstance(document, Mapping):
        return (False, ("evidence document must be an object",))
    if document.get("schema") != EVIDENCE_SCHEMA:
        defects.append("schema mismatch")
    seals = document.get("component_seals")
    if not isinstance(seals, Mapping):
        return (False, (*defects, "component_seals missing"))
    for name in SEAL_COMPONENTS:
        if not seals.get(name):
            defects.append(f"missing component seal: {name}")
    expected = content_hash({name: seals.get(name, "") for name in SEAL_COMPONENTS})
    if document.get("seal") != expected:
        defects.append("bundle seal does not match its component seals")

    sections = document.get("sections")
    if isinstance(sections, Mapping):
        registry_section = sections.get("registry")
        if isinstance(registry_section, Mapping):
            if registry_section.get("seal") != seals.get("registry"):
                defects.append("registry section seal disagrees with component seal")
        certification = sections.get("certification")
        if isinstance(certification, Mapping):
            if certification.get("seal") != seals.get("certification"):
                defects.append("certification section seal disagrees with component seal")
    else:
        defects.append("sections missing")
    return (not defects, tuple(defects))


def _repository_root() -> Path:
    """``engine/knowledge/ukip/evidence.py`` -> parents[3] is the repository root."""
    return Path(__file__).resolve().parents[3]


def write_evidence(
    evidence: KnowledgeEvidence,
    directory: str | Path,
    *,
    filename: str = EVIDENCE_FILENAME,
) -> Path:
    """Write the bundle as canonical JSON, refusing the frozen corpus (DP-03)."""
    target = Path(directory).resolve()
    try:
        relative = target.relative_to(_repository_root())
    except ValueError:
        relative = None
    if relative is not None and find_frozen_writes([relative.as_posix()]):
        raise EvidenceError(
            "refusing to write knowledge evidence into the frozen corpus",
            directory=str(target),
        )
    path = (target / filename).resolve()
    if path.parent != target:
        raise EvidenceError("resolved evidence path escapes the target directory")
    try:
        target.mkdir(parents=True, exist_ok=True)
        path.write_text(evidence.to_json(), encoding="utf-8")
    except OSError as exc:
        raise EvidenceError(
            "knowledge evidence could not be written", path=str(path), detail=str(exc)
        ) from exc
    return path


def read_evidence(path: str | Path) -> dict[str, Any]:
    """Read a stored bundle, failing loudly on malformed JSON."""
    resolved = Path(path)
    if not resolved.is_file():
        raise EvidenceError("evidence bundle not found", path=str(resolved))
    try:
        document = json.loads(resolved.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise EvidenceError(
            "evidence bundle is not valid JSON", path=str(resolved), detail=str(exc)
        ) from exc
    if not isinstance(document, Mapping):
        raise EvidenceError("evidence bundle root must be an object", path=str(resolved))
    return dict(document)


__all__ = [
    "EVIDENCE_SCHEMA",
    "EVIDENCE_VERSION",
    "EVIDENCE_FILENAME",
    "SEAL_COMPONENTS",
    "KnowledgeEvidence",
    "build_evidence",
    "build_evidence_from_assimilation",
    "verify_evidence",
    "write_evidence",
    "read_evidence",
    "canonical_json",
]
