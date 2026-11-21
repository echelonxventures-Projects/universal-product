"""The open publication format registry — unlimited formats, declared as data.

Two declarations drive the whole subsystem:

  :data:`SECTION_DECLARATION`
      Every section type: its structural heading label and the *rule* that selects
      which research records fill it. A rule is a selector over the research corpus
      — never a piece of content.

  :data:`BUILT_IN_FORMATS`
      Every format shipped by default: research paper, journal article, conference
      paper (full and short), white paper, technical article, patent draft, standards
      proposal, technical report, preprint, extended abstract, poster abstract,
      literature review, systematic review, thesis chapter, book chapter, RFC-style
      memo, industry brief, executive brief, datasheet, tutorial.

Neither list is a limit. :class:`FormatRegistry` accepts new sections and new formats
at runtime — from a dict or a JSON file — and the single generator in
``intelligence.publication.generators`` serves any format so registered. That is the
operational meaning of *unlimited publication formats*: the format space is data, the
engine is fixed.
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from intelligence.kernel.canonical import slug
from intelligence.kernel.errors import FormatUnknownError, KernelError
from intelligence.kernel.ids import ArtifactClass, artifact_id

#: Structural sections are composed from the document itself (its provenance,
#: its citations, its title block) rather than from a corpus selector.
STRUCTURAL_SOURCES = frozenset({"title-block", "references", "provenance"})

#: Corpus collections a section rule may select from.
_RULE_SOURCES = frozenset({"claims", "findings", "contributions", "standards", "sources"})

#: Allowed keys of a section rule (fail-closed schema).
_RULE_KEYS = frozenset(
    {
        "source",
        "claim_classes",
        "finding_classes",
        "ref",
        "derive_space",
        "derive_field",
        "limit",
        "role",
    }
)

#: Allowed keys of a section declaration entry.
_SECTION_KEYS = frozenset({"key", "label", "rule", "structural"})

#: Allowed keys of a format descriptor entry.
_FORMAT_KEYS = frozenset(
    {
        "format_id",
        "genre",
        "label",
        "sections",
        "required",
        "renderer",
        "extension",
        "citation_style",
        "audience",
        "notes",
    }
)


# ---------------------------------------------------------------------------
# section declaration
# ---------------------------------------------------------------------------

SECTION_DECLARATION: tuple[dict[str, Any], ...] = (
    {"key": "title-block", "label": "Title", "structural": True},
    {
        "key": "abstract",
        "label": "Abstract",
        "rule": {
            "source": "claims",
            "claim_classes": ["foundational-claim"],
            "ref": "claim_ref",
            "limit": 2,
        },
    },
    {
        "key": "keywords",
        "label": "Keywords",
        "rule": {"source": "claims", "ref": "subject_ref", "limit": 8},
    },
    {
        "key": "introduction",
        "label": "Introduction",
        "rule": {"source": "claims", "claim_classes": ["foundational-claim"], "ref": "claim_ref"},
    },
    {
        "key": "background",
        "label": "Background",
        "rule": {
            "source": "claims",
            "claim_classes": ["foundational-claim", "practice-claim", "definitional-claim"],
            "ref": "rationale_ref",
        },
    },
    {
        "key": "problem-statement",
        "label": "Problem Statement",
        "rule": {
            "source": "claims",
            "claim_classes": ["determination"],
            "derive_space": "decision",
            "derive_field": "problem_statement",
        },
    },
    {
        "key": "objective",
        "label": "Objective",
        "rule": {
            "source": "claims",
            "claim_classes": ["determination"],
            "derive_space": "decision",
            "derive_field": "objective",
        },
    },
    {
        "key": "prior-art",
        "label": "Prior Art and Alternatives Considered",
        "rule": {
            "source": "claims",
            "claim_classes": ["determination"],
            "derive_space": "decision",
            "derive_field": "alternatives",
        },
    },
    {
        "key": "related-work",
        "label": "Related Work",
        "rule": {
            "source": "claims",
            "claim_classes": ["determination", "practice-claim"],
            "ref": "support_refs",
        },
    },
    {
        "key": "evaluation-criteria",
        "label": "Evaluation Criteria",
        "rule": {
            "source": "claims",
            "claim_classes": ["determination"],
            "derive_space": "decision",
            "derive_field": "evaluation_criteria",
        },
    },
    {
        "key": "method",
        "label": "Method",
        "rule": {
            "source": "claims",
            "claim_classes": ["method-claim", "practice-claim"],
            "ref": "claim_ref",
        },
    },
    {
        "key": "architecture",
        "label": "Architecture",
        "rule": {"source": "claims", "claim_classes": ["specification-claim"], "ref": "claim_ref"},
    },
    {
        "key": "normative-requirements",
        "label": "Normative Requirements",
        "rule": {
            "source": "claims",
            "claim_classes": ["normative-claim", "invariant-claim"],
            "ref": "claim_ref",
        },
    },
    {
        "key": "specification",
        "label": "Specification",
        "rule": {"source": "standards", "ref": "standard_ref"},
    },
    {
        "key": "results",
        "label": "Results",
        "rule": {"source": "findings", "finding_classes": ["quantitative"], "ref": "metric_ref"},
    },
    {
        "key": "evaluation",
        "label": "Evaluation",
        "rule": {
            "source": "findings",
            "finding_classes": ["qualitative-verdict"],
            "ref": "metric_ref",
        },
    },
    {
        "key": "contributions",
        "label": "Contribution Areas",
        "rule": {"source": "contributions", "ref": "exemplar_refs", "limit": 24},
    },
    {
        "key": "standards-conformance",
        "label": "Standards Conformance",
        "rule": {"source": "standards", "ref": "obligation_refs"},
    },
    {
        "key": "discussion",
        "label": "Discussion",
        "rule": {"source": "claims", "ref": "rationale_ref", "limit": 6},
    },
    {
        "key": "tradeoffs",
        "label": "Trade-offs",
        "rule": {
            "source": "claims",
            "claim_classes": ["determination"],
            "derive_space": "decision",
            "derive_field": "tradeoffs",
        },
    },
    {
        "key": "risk-register",
        "label": "Risks",
        "rule": {
            "source": "claims",
            "claim_classes": ["determination"],
            "derive_space": "decision",
            "derive_field": "risks",
        },
    },
    {
        "key": "limitations",
        "label": "Limitations and Negative Results",
        "rule": {"source": "claims", "claim_classes": ["negative-result"], "ref": "claim_ref"},
    },
    {
        "key": "conclusion",
        "label": "Conclusion",
        "rule": {
            "source": "claims",
            "claim_classes": ["determination"],
            "derive_space": "decision",
            "derive_field": "consequences",
        },
    },
    {
        "key": "future-work",
        "label": "Future Work",
        "rule": {
            "source": "claims",
            "claim_classes": ["determination"],
            "derive_space": "decision",
            "derive_field": "implementation_guidance",
        },
    },
    {
        "key": "executive-summary",
        "label": "Executive Summary",
        "rule": {
            "source": "claims",
            "claim_classes": ["foundational-claim"],
            "ref": "claim_ref",
            "limit": 1,
        },
    },
    {
        "key": "business-context",
        "label": "Context",
        "rule": {
            "source": "claims",
            "claim_classes": ["determination"],
            "derive_space": "decision",
            "derive_field": "context",
        },
    },
    {
        "key": "recommendation",
        "label": "Recommendation",
        "rule": {"source": "claims", "claim_classes": ["determination"], "ref": "claim_ref"},
    },
    {
        "key": "implementation-guidance",
        "label": "Implementation Guidance",
        "rule": {
            "source": "claims",
            "claim_classes": ["determination"],
            "derive_space": "decision",
            "derive_field": "implementation_guidance",
        },
    },
    {
        "key": "validation-strategy",
        "label": "Validation Strategy",
        "rule": {
            "source": "claims",
            "claim_classes": ["determination"],
            "derive_space": "decision",
            "derive_field": "validation_strategy",
        },
    },
    {
        "key": "patent-field",
        "label": "Field of the Invention",
        "rule": {
            "source": "claims",
            "claim_classes": ["specification-claim"],
            "ref": "subject_ref",
        },
    },
    {
        "key": "patent-background",
        "label": "Background of the Invention",
        "rule": {"source": "claims", "claim_classes": ["negative-result"], "ref": "claim_ref"},
    },
    {
        "key": "patent-summary",
        "label": "Summary of the Invention",
        "rule": {"source": "claims", "claim_classes": ["determination"], "ref": "claim_ref"},
    },
    {
        "key": "patent-detailed-description",
        "label": "Detailed Description",
        "rule": {
            "source": "claims",
            "claim_classes": ["method-claim", "specification-claim", "practice-claim"],
            "ref": "claim_ref",
        },
    },
    {
        "key": "patent-claims",
        "label": "Claims",
        "rule": {
            "source": "claims",
            "claim_classes": ["normative-claim", "specification-claim", "invariant-claim"],
            "ref": "claim_ref",
        },
    },
    {
        "key": "patent-industrial-applicability",
        "label": "Industrial Applicability",
        "rule": {
            "source": "findings",
            "finding_classes": ["quantitative"],
            "ref": "metric_ref",
            "limit": 6,
        },
    },
    {
        "key": "substrate",
        "label": "Substrate and Reproducibility",
        "rule": {"source": "findings", "ref": "metric_ref"},
    },
    {"key": "references", "label": "References", "structural": True},
    {"key": "provenance", "label": "Provenance", "structural": True},
)


# ---------------------------------------------------------------------------
# built-in formats
# ---------------------------------------------------------------------------

_ACADEMIC_CORE = [
    "title-block",
    "abstract",
    "keywords",
    "introduction",
    "background",
    "related-work",
    "method",
    "results",
    "evaluation",
    "discussion",
    "limitations",
    "conclusion",
    "future-work",
    "references",
    "provenance",
]

BUILT_IN_FORMATS: tuple[dict[str, Any], ...] = (
    {
        "format_id": "research-paper",
        "genre": "paper",
        "label": "Research Paper",
        "sections": _ACADEMIC_CORE,
        "required": [
            "title-block",
            "abstract",
            "introduction",
            "method",
            "results",
            "references",
            "provenance",
        ],
        "renderer": "markdown",
        "extension": "md",
        "citation_style": "canonical-id",
        "audience": "research",
    },
    {
        "format_id": "journal-article",
        "genre": "journal",
        "label": "Journal Article",
        "sections": [
            "title-block",
            "abstract",
            "keywords",
            "introduction",
            "background",
            "related-work",
            "method",
            "architecture",
            "results",
            "evaluation",
            "discussion",
            "limitations",
            "conclusion",
            "future-work",
            "substrate",
            "references",
            "provenance",
        ],
        "required": [
            "title-block",
            "abstract",
            "keywords",
            "introduction",
            "method",
            "results",
            "discussion",
            "references",
            "provenance",
        ],
        "renderer": "markdown",
        "extension": "md",
        "citation_style": "canonical-id",
        "audience": "journal",
    },
    {
        "format_id": "journal-article-latex",
        "genre": "journal",
        "label": "Journal Article (LaTeX submission)",
        "sections": [
            "title-block",
            "abstract",
            "keywords",
            "introduction",
            "background",
            "method",
            "results",
            "evaluation",
            "discussion",
            "conclusion",
            "references",
            "provenance",
        ],
        "required": [
            "title-block",
            "abstract",
            "introduction",
            "method",
            "results",
            "references",
            "provenance",
        ],
        "renderer": "latex",
        "extension": "tex",
        "citation_style": "canonical-id",
        "audience": "journal",
    },
    {
        "format_id": "conference-paper",
        "genre": "conference",
        "label": "Conference Paper",
        "sections": [
            "title-block",
            "abstract",
            "keywords",
            "introduction",
            "related-work",
            "method",
            "architecture",
            "results",
            "evaluation",
            "limitations",
            "conclusion",
            "references",
            "provenance",
        ],
        "required": [
            "title-block",
            "abstract",
            "introduction",
            "method",
            "results",
            "references",
            "provenance",
        ],
        "renderer": "markdown",
        "extension": "md",
        "citation_style": "canonical-id",
        "audience": "conference",
    },
    {
        "format_id": "conference-short-paper",
        "genre": "conference",
        "label": "Conference Short Paper",
        "sections": [
            "title-block",
            "abstract",
            "introduction",
            "method",
            "results",
            "conclusion",
            "references",
            "provenance",
        ],
        "required": ["title-block", "abstract", "method", "results", "references", "provenance"],
        "renderer": "markdown",
        "extension": "md",
        "citation_style": "canonical-id",
        "audience": "conference",
    },
    {
        "format_id": "extended-abstract",
        "genre": "conference",
        "label": "Extended Abstract",
        "sections": [
            "title-block",
            "abstract",
            "keywords",
            "method",
            "results",
            "references",
            "provenance",
        ],
        "required": ["title-block", "abstract", "results", "references", "provenance"],
        "renderer": "markdown",
        "extension": "md",
        "citation_style": "canonical-id",
        "audience": "conference",
    },
    {
        "format_id": "poster-abstract",
        "genre": "conference",
        "label": "Poster Abstract",
        "sections": ["title-block", "abstract", "results", "references", "provenance"],
        "required": ["title-block", "abstract", "results", "provenance"],
        "renderer": "plaintext",
        "extension": "txt",
        "citation_style": "canonical-id",
        "audience": "conference",
    },
    {
        "format_id": "white-paper",
        "genre": "white-paper",
        "label": "White Paper",
        "sections": [
            "title-block",
            "executive-summary",
            "business-context",
            "problem-statement",
            "objective",
            "prior-art",
            "evaluation-criteria",
            "recommendation",
            "architecture",
            "tradeoffs",
            "risk-register",
            "results",
            "implementation-guidance",
            "conclusion",
            "references",
            "provenance",
        ],
        "required": [
            "title-block",
            "executive-summary",
            "problem-statement",
            "recommendation",
            "references",
            "provenance",
        ],
        "renderer": "markdown",
        "extension": "md",
        "citation_style": "canonical-id",
        "audience": "industry",
    },
    {
        "format_id": "industry-brief",
        "genre": "white-paper",
        "label": "Industry Brief",
        "sections": [
            "title-block",
            "executive-summary",
            "business-context",
            "recommendation",
            "results",
            "references",
            "provenance",
        ],
        "required": ["title-block", "executive-summary", "recommendation", "provenance"],
        "renderer": "markdown",
        "extension": "md",
        "citation_style": "canonical-id",
        "audience": "industry",
    },
    {
        "format_id": "executive-brief",
        "genre": "white-paper",
        "label": "Executive Brief",
        "sections": [
            "title-block",
            "executive-summary",
            "recommendation",
            "risk-register",
            "provenance",
        ],
        "required": ["title-block", "executive-summary", "recommendation", "provenance"],
        "renderer": "plaintext",
        "extension": "txt",
        "citation_style": "canonical-id",
        "audience": "executive",
    },
    {
        "format_id": "technical-article",
        "genre": "technical-article",
        "label": "Technical Article",
        "sections": [
            "title-block",
            "abstract",
            "introduction",
            "background",
            "method",
            "architecture",
            "normative-requirements",
            "results",
            "implementation-guidance",
            "limitations",
            "conclusion",
            "references",
            "provenance",
        ],
        "required": [
            "title-block",
            "abstract",
            "introduction",
            "method",
            "references",
            "provenance",
        ],
        "renderer": "markdown",
        "extension": "md",
        "citation_style": "canonical-id",
        "audience": "engineering",
    },
    {
        "format_id": "technical-article-html",
        "genre": "technical-article",
        "label": "Technical Article (HTML)",
        "sections": [
            "title-block",
            "abstract",
            "introduction",
            "method",
            "architecture",
            "results",
            "conclusion",
            "references",
            "provenance",
        ],
        "required": ["title-block", "abstract", "method", "references", "provenance"],
        "renderer": "html",
        "extension": "html",
        "citation_style": "canonical-id",
        "audience": "engineering",
    },
    {
        "format_id": "tutorial",
        "genre": "technical-article",
        "label": "Tutorial",
        "sections": [
            "title-block",
            "abstract",
            "background",
            "method",
            "implementation-guidance",
            "validation-strategy",
            "references",
            "provenance",
        ],
        "required": ["title-block", "abstract", "method", "provenance"],
        "renderer": "markdown",
        "extension": "md",
        "citation_style": "canonical-id",
        "audience": "engineering",
    },
    {
        "format_id": "patent-draft",
        "genre": "patent",
        "label": "Patent Draft",
        "sections": [
            "title-block",
            "patent-field",
            "patent-background",
            "patent-summary",
            "patent-detailed-description",
            "patent-claims",
            "patent-industrial-applicability",
            "prior-art",
            "references",
            "provenance",
        ],
        "required": [
            "title-block",
            "patent-field",
            "patent-summary",
            "patent-detailed-description",
            "patent-claims",
            "provenance",
        ],
        "renderer": "plaintext",
        "extension": "txt",
        "citation_style": "canonical-id",
        "audience": "patent-office",
        "notes": "A DRAFT for attorney review. Asserts no filing, priority or novelty "
        "opinion; every element is a resolved reference to a canonical record.",
    },
    {
        "format_id": "standards-proposal",
        "genre": "standards",
        "label": "Standards Proposal",
        "sections": [
            "title-block",
            "abstract",
            "problem-statement",
            "objective",
            "normative-requirements",
            "specification",
            "standards-conformance",
            "validation-strategy",
            "prior-art",
            "references",
            "provenance",
        ],
        "required": [
            "title-block",
            "abstract",
            "normative-requirements",
            "specification",
            "references",
            "provenance",
        ],
        "renderer": "markdown",
        "extension": "md",
        "citation_style": "canonical-id",
        "audience": "standards-body",
    },
    {
        "format_id": "rfc-memo",
        "genre": "standards",
        "label": "RFC-style Memo",
        "sections": [
            "title-block",
            "abstract",
            "normative-requirements",
            "specification",
            "validation-strategy",
            "references",
            "provenance",
        ],
        "required": ["title-block", "abstract", "normative-requirements", "provenance"],
        "renderer": "plaintext",
        "extension": "txt",
        "citation_style": "canonical-id",
        "audience": "standards-body",
    },
    {
        "format_id": "technical-report",
        "genre": "report",
        "label": "Technical Report",
        "sections": [
            "title-block",
            "executive-summary",
            "introduction",
            "method",
            "contributions",
            "results",
            "evaluation",
            "standards-conformance",
            "substrate",
            "conclusion",
            "references",
            "provenance",
        ],
        "required": [
            "title-block",
            "introduction",
            "results",
            "contributions",
            "references",
            "provenance",
        ],
        "renderer": "markdown",
        "extension": "md",
        "citation_style": "canonical-id",
        "audience": "institutional",
    },
    {
        "format_id": "datasheet",
        "genre": "report",
        "label": "Substrate Datasheet",
        "sections": ["title-block", "substrate", "results", "contributions", "provenance"],
        "required": ["title-block", "substrate", "provenance"],
        "renderer": "json",
        "extension": "json",
        "citation_style": "canonical-id",
        "audience": "machine",
    },
    {
        "format_id": "preprint",
        "genre": "paper",
        "label": "Preprint",
        "sections": _ACADEMIC_CORE,
        "required": [
            "title-block",
            "abstract",
            "introduction",
            "results",
            "references",
            "provenance",
        ],
        "renderer": "markdown",
        "extension": "md",
        "citation_style": "canonical-id",
        "audience": "preprint-server",
    },
    {
        "format_id": "literature-review",
        "genre": "review",
        "label": "Literature Review",
        "sections": [
            "title-block",
            "abstract",
            "introduction",
            "related-work",
            "prior-art",
            "discussion",
            "conclusion",
            "references",
            "provenance",
        ],
        "required": ["title-block", "abstract", "related-work", "references", "provenance"],
        "renderer": "markdown",
        "extension": "md",
        "citation_style": "canonical-id",
        "audience": "research",
    },
    {
        "format_id": "systematic-review",
        "genre": "review",
        "label": "Systematic Review",
        "sections": [
            "title-block",
            "abstract",
            "objective",
            "method",
            "evaluation-criteria",
            "results",
            "evaluation",
            "limitations",
            "conclusion",
            "references",
            "provenance",
        ],
        "required": ["title-block", "abstract", "method", "results", "references", "provenance"],
        "renderer": "markdown",
        "extension": "md",
        "citation_style": "canonical-id",
        "audience": "research",
    },
    {
        "format_id": "thesis-chapter",
        "genre": "thesis",
        "label": "Thesis Chapter",
        "sections": [
            "title-block",
            "introduction",
            "background",
            "method",
            "architecture",
            "results",
            "evaluation",
            "discussion",
            "limitations",
            "conclusion",
            "references",
            "provenance",
        ],
        "required": [
            "title-block",
            "introduction",
            "method",
            "results",
            "references",
            "provenance",
        ],
        "renderer": "markdown",
        "extension": "md",
        "citation_style": "canonical-id",
        "audience": "academic",
    },
    {
        "format_id": "book-chapter",
        "genre": "book",
        "label": "Book Chapter",
        "sections": [
            "title-block",
            "abstract",
            "introduction",
            "background",
            "method",
            "architecture",
            "discussion",
            "conclusion",
            "references",
            "provenance",
        ],
        "required": ["title-block", "introduction", "background", "references", "provenance"],
        "renderer": "markdown",
        "extension": "md",
        "citation_style": "canonical-id",
        "audience": "book",
    },
)


# ---------------------------------------------------------------------------
# descriptors + registry
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class SectionType:
    """A registered section type: its heading label and its corpus selector."""

    key: str
    label: str
    structural: bool
    rule: Mapping[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "label": self.label,
            "structural": self.structural,
            "rule": dict(self.rule),
        }


@dataclass(frozen=True, slots=True)
class FormatDescriptor:
    """A publication format — pure data, registrable at runtime."""

    format_id: str
    genre: str
    label: str
    sections: tuple[str, ...]
    required: tuple[str, ...]
    renderer: str
    extension: str
    citation_style: str
    audience: str
    notes: str

    @property
    def descriptor_id(self) -> str:
        return artifact_id(ArtifactClass.PUBLICATION_FORMAT, slug(self.format_id))

    @property
    def natural_key(self) -> str:
        return slug(self.format_id)

    @property
    def record_id(self) -> str:
        return self.descriptor_id

    def filename(self, area_key: str) -> str:
        return f"{self.format_id}--{area_key}.{self.extension}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "descriptor_id": self.descriptor_id,
            "format_id": self.format_id,
            "genre": self.genre,
            "label": self.label,
            "sections": list(self.sections),
            "required": list(self.required),
            "renderer": self.renderer,
            "extension": self.extension,
            "citation_style": self.citation_style,
            "audience": self.audience,
            "notes": self.notes,
            "section_count": len(self.sections),
        }


def _validate_rule(key: str, rule: Mapping[str, Any]) -> None:
    unknown = sorted(set(rule) - _RULE_KEYS)
    if unknown:
        raise KernelError("unknown section rule keys", section=key, keys=unknown)
    source = rule.get("source")
    if source not in _RULE_SOURCES:
        raise KernelError(
            "unknown section rule source", section=key, source=source, allowed=sorted(_RULE_SOURCES)
        )
    if not rule.get("ref") and not rule.get("derive_field"):
        raise KernelError("section rule must name a ref field or a derived field", section=key)


class FormatRegistry:
    """The open registry of section types and publication formats.

    Unbounded by construction: :meth:`register_section` and :meth:`register_format`
    accept new declarations at runtime, and :meth:`load_file` reads them from JSON,
    so an operator can add a publication format without touching any engine code.
    """

    def __init__(
        self,
        sections: Sequence[Mapping[str, Any]] = SECTION_DECLARATION,
        formats: Sequence[Mapping[str, Any]] = BUILT_IN_FORMATS,
    ) -> None:
        self._sections: dict[str, SectionType] = {}
        self._formats: dict[str, FormatDescriptor] = {}
        for entry in sections:
            self.register_section(entry)
        for entry in formats:
            self.register_format(entry)

    # -- registration ----------------------------------------------------------

    def register_section(self, entry: Mapping[str, Any]) -> SectionType:
        unknown = sorted(set(entry) - _SECTION_KEYS)
        if unknown:
            raise KernelError("unknown section declaration keys", keys=unknown)
        key = str(entry.get("key") or "")
        label = str(entry.get("label") or "")
        if not key or not label:
            raise KernelError("section declaration requires a key and a label", entry=dict(entry))
        structural = bool(entry.get("structural", False)) or key in STRUCTURAL_SOURCES
        rule = entry.get("rule") or {}
        if not structural:
            if not isinstance(rule, Mapping):
                raise KernelError("section rule must be an object", section=key)
            _validate_rule(key, rule)
        section = SectionType(key=key, label=label, structural=structural, rule=dict(rule))
        self._sections[key] = section
        return section

    def register_format(self, entry: Mapping[str, Any]) -> FormatDescriptor:
        unknown = sorted(set(entry) - _FORMAT_KEYS)
        if unknown:
            raise KernelError("unknown format descriptor keys", keys=unknown)
        format_id = str(entry.get("format_id") or "")
        if not format_id:
            raise KernelError("format descriptor requires a format_id")
        sections = tuple(str(s) for s in (entry.get("sections") or ()))
        if not sections:
            raise KernelError(
                "format descriptor requires at least one section", format_id=format_id
            )
        undeclared = [s for s in sections if s not in self._sections]
        if undeclared:
            raise KernelError(
                "format references undeclared section types — register the section first",
                format_id=format_id,
                undeclared=undeclared,
            )
        required = tuple(str(s) for s in (entry.get("required") or ()))
        outside = [s for s in required if s not in sections]
        if outside:
            raise KernelError(
                "required section is not part of the format", format_id=format_id, outside=outside
            )
        descriptor = FormatDescriptor(
            format_id=format_id,
            genre=str(entry.get("genre") or "publication"),
            label=str(entry.get("label") or format_id),
            sections=sections,
            required=required,
            renderer=str(entry.get("renderer") or "markdown"),
            extension=str(entry.get("extension") or "md"),
            citation_style=str(entry.get("citation_style") or "canonical-id"),
            audience=str(entry.get("audience") or "general"),
            notes=str(entry.get("notes") or ""),
        )
        self._formats[format_id] = descriptor
        return descriptor

    def register_many(self, entries: Iterable[Mapping[str, Any]]) -> tuple[FormatDescriptor, ...]:
        return tuple(self.register_format(e) for e in entries)

    def load_file(self, path: str | Path) -> tuple[FormatDescriptor, ...]:
        """Load additional section types and formats from a JSON declaration file."""
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        if not isinstance(payload, Mapping):
            raise KernelError("format declaration file must contain an object", path=str(path))
        for entry in payload.get("sections") or ():
            self.register_section(entry)
        return self.register_many(payload.get("formats") or ())

    # -- access ----------------------------------------------------------------

    def get(self, format_id: str) -> FormatDescriptor:
        descriptor = self._formats.get(format_id)
        if descriptor is None:
            raise FormatUnknownError(
                "publication format is not registered",
                format_id=format_id,
                registered=self.format_ids(),
            )
        return descriptor

    def has(self, format_id: str) -> bool:
        return format_id in self._formats

    def format_ids(self) -> list[str]:
        return sorted(self._formats)

    def formats(self) -> tuple[FormatDescriptor, ...]:
        return tuple(self._formats[k] for k in self.format_ids())

    def genres(self) -> dict[str, list[str]]:
        table: dict[str, list[str]] = {}
        for descriptor in self.formats():
            table.setdefault(descriptor.genre, []).append(descriptor.format_id)
        return {k: sorted(v) for k, v in sorted(table.items())}

    def by_genre(self, genre: str) -> tuple[FormatDescriptor, ...]:
        return tuple(f for f in self.formats() if f.genre == genre)

    def section(self, key: str) -> SectionType:
        section = self._sections.get(key)
        if section is None:
            raise KernelError(
                "section type is not registered", section=key, registered=sorted(self._sections)
            )
        return section

    def section_keys(self) -> list[str]:
        return sorted(self._sections)

    def sections(self) -> tuple[SectionType, ...]:
        return tuple(self._sections[k] for k in self.section_keys())

    def renderers_used(self) -> list[str]:
        return sorted({f.renderer for f in self.formats()})

    def catalog(self) -> dict[str, Any]:
        return {
            "extensible": True,
            "extension_contract": "register_section() / register_format() / load_file() — "
            "a new publication format is a data declaration, never a "
            "code change; the format space is unbounded",
            "format_count": len(self._formats),
            "section_type_count": len(self._sections),
            "genres": self.genres(),
            "renderers_used": self.renderers_used(),
            "formats": [f.to_dict() for f in self.formats()],
            "section_types": [s.to_dict() for s in self.sections()],
        }


__all__ = [
    "BUILT_IN_FORMATS",
    "SECTION_DECLARATION",
    "STRUCTURAL_SOURCES",
    "FormatDescriptor",
    "FormatRegistry",
    "SectionType",
]
