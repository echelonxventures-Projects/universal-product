"""PublicationIntelligenceEngine — the producer of every publication and its evidence.

Pipeline, end to end::

    research corpus (UCOS-URI-001)
        → generate one reference-only specification per registered format
        → compose (resolve references, attach provenance)
        → render (markdown / latex / html / plaintext / json / any registered renderer)
        → register (formats, publications, sections, shared citations)
        → validate (fourteen fail-closed obligations)
        → emit sealed JSON evidence + the rendered documents

Operators may extend the format space without touching this file: a JSON declaration
at ``intelligence/UCOS-UPI-001/publication-formats.json`` (sections and/or formats) is
loaded automatically when present.
"""

from __future__ import annotations

from typing import Any

from intelligence.kernel.canonical import canonical_json, sealed, slug
from intelligence.kernel.config import (
    NestedFileSink,
    OutputSink,
    RepoConfig,
    subsystem_config,
)
from intelligence.kernel.validation import EXIT_ABORT, ValidationReport
from intelligence.publication import AUTHORITY, GENERATED_BANNER, PROGRAMME, __version__
from intelligence.publication.composer import PublicationComposer
from intelligence.publication.formats import FormatRegistry
from intelligence.publication.generators import (
    NAMED_DELIVERABLES,
    PublicationGenerator,
    PublicationScope,
)
from intelligence.publication.model import PublicationSet
from intelligence.publication.registry import PublicationRegistry
from intelligence.publication.renderers import renderer_ids
from intelligence.publication.validation import PublicationValidationEngine
from intelligence.research.engine import OUTPUT_DIR as RESEARCH_OUTPUT_DIR
from intelligence.research.engine import ResearchIntelligenceEngine

#: The subsystem-owned output directory (the only place this engine writes).
OUTPUT_DIR = PROGRAMME

#: Rendered documents live in this subdirectory of the output directory.
DOCUMENTS_DIR = "publications"

#: Optional operator-supplied format extension declaration (data, not code).
FORMAT_EXTENSION_FILE = "publication-formats.json"

_CLASSIFICATION = (
    "ADDITIVE INTELLIGENCE — generated publications, derived from canonical knowledge, "
    "non-authoritative"
)

#: The probe format used by PV-14 to prove at runtime that the format space is open.
_PROBE_FORMAT: dict[str, Any] = {
    "format_id": "openness-probe",
    "genre": "probe",
    "label": "Format Openness Probe",
    "sections": ["title-block", "abstract", "results", "references", "provenance"],
    "required": ["title-block", "abstract", "provenance"],
    "renderer": "markdown",
    "extension": "md",
    "citation_style": "canonical-id",
    "audience": "self-verification",
    "notes": "Registered at runtime from a data declaration to prove that adding a "
    "publication format requires no engine change.",
}


class PublicationIntelligenceEngine:
    """The Publication Intelligence subsystem: generate → compose → register → validate."""

    def __init__(
        self,
        config: RepoConfig | None = None,
        formats: FormatRegistry | None = None,
    ) -> None:
        self.config = config or subsystem_config(OUTPUT_DIR)
        self.research = ResearchIntelligenceEngine(
            subsystem_config(RESEARCH_OUTPUT_DIR, self.config.repo_root)
        )
        self.resolver = self.research.resolver
        self.formats = formats or self._load_formats()
        self.generator = PublicationGenerator(self.research.corpus(), self.resolver, self.formats)
        self.composer = PublicationComposer(self.resolver, self.formats, self.research.registry())
        self._publications: PublicationSet | None = None
        self._registry: PublicationRegistry | None = None

    def _load_formats(self) -> FormatRegistry:
        registry = FormatRegistry()
        extension = self.config.output_dir / FORMAT_EXTENSION_FILE
        if extension.is_file():
            registry.load_file(extension)
        return registry

    # -- generation ------------------------------------------------------------

    def scope(self) -> PublicationScope:
        return PublicationScope.whole_corpus(self.research.corpus())

    def publications(self) -> PublicationSet:
        """Generate, compose and render one publication per registered format."""
        if self._publications is None:
            scope = self.scope()
            specs = self.generator.build_all(scope)
            documents = []
            rendered: dict[str, str] = {}
            for spec in specs:
                document, body = self.composer.render(spec)
                documents.append(document)
                rendered[self.filename(spec.format_id, spec.area_label)] = body
            self._publications = PublicationSet(
                specs=specs, documents=tuple(documents), rendered=rendered
            )
        return self._publications

    def filename(self, format_id: str, area_label: str) -> str:
        return self.formats.get(format_id).filename(slug(area_label))

    def registry(self) -> PublicationRegistry:
        if self._registry is None:
            self._registry = PublicationRegistry(
                self.publications(), self.formats, self.research.registry()
            )
        return self._registry

    def validation(self) -> ValidationReport:
        return PublicationValidationEngine(
            self.publications(),
            self.formats,
            self.resolver,
            self.registry(),
            self.composer,
            self.research.registry(),
            openness_probe=self.openness_probe,
        ).validate()

    # -- format openness proof -------------------------------------------------

    def openness_probe(self) -> dict[str, Any]:
        """Register a format at runtime, generate it, render it — proof for PV-14."""
        probe_registry = FormatRegistry()
        descriptor = probe_registry.register_format(_PROBE_FORMAT)
        generator = PublicationGenerator(self.research.corpus(), self.resolver, probe_registry)
        composer = PublicationComposer(self.resolver, probe_registry, self.research.registry())
        spec = generator.build(descriptor.format_id, self.scope())
        document, body = composer.render(spec)
        satisfied = [
            block.section_key
            for block in document.blocks
            if block.section_key in descriptor.required and (block.structural or not block.is_empty)
        ]
        return {
            "format_id": descriptor.format_id,
            "declared_as": "data (dict) registered at runtime",
            "code_changed": False,
            "generated": bool(spec.sections),
            "rendered": bool(body) and GENERATED_BANNER in body,
            "required_sections_satisfied": sorted(satisfied) == sorted(descriptor.required),
            "resolved_blocks": document.resolved_total(),
            "registered_formats_after_probe": len(probe_registry.format_ids()),
        }

    # -- envelope --------------------------------------------------------------

    def envelope(self, artifact_id: str, title: str) -> dict[str, Any]:
        return {
            "artifact_id": artifact_id,
            "title": title,
            "programme": PROGRAMME,
            "producer": f"{PROGRAMME} Universal Publication Intelligence v{__version__}",
            "authority": AUTHORITY,
            "classification": _CLASSIFICATION,
            "generated_from": {
                "research_programme": self.research.__class__.__module__.split(".")[1],
                "research_registry_head": self.research.registry().ledger.head(),
                "research_counts": self.research.corpus().counts(),
            },
            "evidence_state": {
                "substrate": self.research.substrate.fingerprint(),
                "knowledge": self.resolver.fingerprint(),
            },
        }

    # -- model -----------------------------------------------------------------

    def model(self) -> dict[str, Any]:
        publications = self.publications()
        registry = self.registry()
        validation = self.validation()
        model = self.envelope("UCOS-UPI-MODEL", "Publication Intelligence Model")
        model.update(
            {
                "counts": publications.counts(),
                "formats": {
                    "registered": len(self.formats.format_ids()),
                    "genres": self.formats.genres(),
                    "renderers_available": renderer_ids(),
                    "named_deliverables": dict(sorted(NAMED_DELIVERABLES.items())),
                    "extensible": True,
                },
                "documents": [
                    {
                        "format_id": d.format_id,
                        "genre": d.genre,
                        "label": d.format_label,
                        "title": d.title,
                        "renderer": d.renderer,
                        "filename": self.filename(d.format_id, d.area_label),
                        "counts": d.counts(),
                    }
                    for d in publications.documents
                ],
                "registry": {
                    "registry_id": registry.ledger.registry_id,
                    "records": registry.count(),
                    "class_histogram": registry.ledger.class_histogram(),
                    "journal_head": registry.ledger.head(),
                    "shared_citations": registry.shared_citation_report(),
                },
                "validation": {
                    "verdict": validation.verdict,
                    "gate": "OPEN" if validation.gate_open else "CLOSED",
                    "checks_passed": len(validation.passed()),
                    "checks_total": len(validation.checks),
                    "blocking_failures": [c.check_id for c in validation.blocking_failures()],
                },
            }
        )
        return model

    # -- outputs ---------------------------------------------------------------

    def outputs(self) -> dict[str, dict[str, Any]]:
        publications = self.publications()
        registry = self.registry()
        validation = self.validation()

        catalog = self.envelope("UCOS-UPI-FORMAT-CATALOG", "Publication Format Catalog")
        catalog.update(self.formats.catalog())
        catalog["renderers_available"] = renderer_ids()
        catalog["named_deliverables"] = dict(sorted(NAMED_DELIVERABLES.items()))

        publication_set = self.envelope("UCOS-UPI-PUBLICATION-SET", "Generated Publication Set")
        publication_set.update(publications.to_dict())

        registry_out = self.envelope("UCOS-UPI-PUBLICATION-REGISTRY", "Publication Registry")
        registry_out.update(registry.document())

        validation_out = self.envelope(
            "UCOS-UPI-PUBLICATION-VALIDATION", "Publication Validation Report"
        )
        validation_out.update(validation.to_dict())

        snapshot = self.envelope("UCOS-UPI-SNAPSHOT", "Publication Intelligence Snapshot")
        snapshot.update(
            {
                "counts": publications.counts(),
                "formats_registered": len(self.formats.format_ids()),
                "genres": sorted(self.formats.genres()),
                "renderers": renderer_ids(),
                "registry_records": registry.count(),
                "registry_head": registry.ledger.head(),
                "citation_reuse_factor": registry.shared_citation_report()["reuse_factor"],
                "verdict": validation.verdict,
                "gate": "OPEN" if validation.gate_open else "CLOSED",
            }
        )

        payloads = {
            "UCOS-UPI-MODEL.json": self.model(),
            "UCOS-UPI-FORMAT-CATALOG.json": catalog,
            "UCOS-UPI-PUBLICATION-SET.json": publication_set,
            "UCOS-UPI-PUBLICATION-REGISTRY.json": registry_out,
            "UCOS-UPI-PUBLICATION-VALIDATION.json": validation_out,
            "UCOS-UPI-SNAPSHOT.json": snapshot,
        }
        return {name: sealed(payload) for name, payload in payloads.items()}

    def rendered_documents(self) -> dict[str, str]:
        """The rendered publication bodies, keyed by their output-relative filename."""
        return {
            f"{DOCUMENTS_DIR}/{name}": body
            for name, body in sorted(self.publications().rendered.items())
        }

    def write(self, sink: OutputSink | None = None) -> list[str]:
        target = sink or NestedFileSink(self.config.output_dir)
        written = [
            target.emit(name, canonical_json(payload)) for name, payload in self.outputs().items()
        ]
        written.extend(target.emit(name, body) for name, body in self.rendered_documents().items())
        return sorted(written)

    # -- determinism -----------------------------------------------------------

    def verify_determinism(self) -> dict[str, Any]:
        other = PublicationIntelligenceEngine(self.config)
        first_json = self.outputs()
        second_json = other.outputs()
        json_mismatches = sorted(
            name
            for name in first_json
            if canonical_json(first_json[name]) != canonical_json(second_json.get(name, {}))
        )
        first_docs = self.rendered_documents()
        second_docs = other.rendered_documents()
        doc_mismatches = sorted(
            name for name in first_docs if first_docs[name] != second_docs.get(name)
        )
        return {
            "programme": PROGRAMME,
            "deterministic": not json_mismatches
            and not doc_mismatches
            and sorted(first_json) == sorted(second_json)
            and sorted(first_docs) == sorted(second_docs),
            "outputs_checked": sorted(first_json),
            "documents_checked": sorted(first_docs),
            "output_mismatches": json_mismatches,
            "document_mismatches": doc_mismatches,
        }

    # -- gate ------------------------------------------------------------------

    def gate(self) -> tuple[int, str]:
        """Fail-closed publication gate. 0 open · 1 closed · 2 fail-closed abort."""
        research_code, research_line = self.research.gate()
        if research_code == EXIT_ABORT:
            return EXIT_ABORT, f"{PROGRAMME}: FAIL-CLOSED ABORT | upstream {research_line}"
        if research_code != 0:
            return 1, f"{PROGRAMME}: CLOSED | upstream research gate closed | {research_line}"
        publications = self.publications()
        registry = self.registry()
        validation = self.validation()
        determinism = self.verify_determinism()
        counts = publications.counts()
        line = (
            f"{PROGRAMME}: {validation.verdict} | "
            f"publications={counts['publications']} formats={len(self.formats.format_ids())} "
            f"genres={len(self.formats.genres())} renderers={len(renderer_ids())} | "
            f"blocks={counts['resolved_blocks']} citations={counts['citations']} | "
            f"records={registry.count()} | "
            f"checks={len(validation.passed())}/{len(validation.checks)} PASS | "
            f"deterministic={str(determinism['deterministic']).lower()} | "
            f"gate={'OPEN' if validation.gate_open else 'CLOSED'} | "
            f"seal={registry.ledger.head()[:16]}"
        )
        if not determinism["deterministic"]:
            return 1, line
        return validation.exit_code, line


__all__ = [
    "DOCUMENTS_DIR",
    "FORMAT_EXTENSION_FILE",
    "OUTPUT_DIR",
    "PublicationIntelligenceEngine",
]
