"""UCOS Ω∞ — Universal Publication Intelligence · UCOS-UPI-001.

The additive subsystem that OWNS publication intelligence for this repository:

    Paper · Journal Article · Conference Paper · White Paper · Technical Article ·
    Patent Draft · Standards Proposal · … and any format registered thereafter

Every publication is generated from the research corpus produced by
``intelligence.research`` (UCOS-URI-001), which is itself a reference-only
projection of canonical knowledge. The chain is therefore:

    canonical knowledge → research corpus (refs) → publication spec (refs)
                                                 → composed document (resolved
                                                   text + provenance, at render time)

Three properties are structural rather than aspirational:

  * **No duplicated content.** A :class:`~intelligence.publication.model.PublicationSpec`
    has no prose field. It cannot store a copy of canonical text; it can only point
    at it. Text materialises in the composed document, always attached to the id and
    content hash of the canonical record it came from.
  * **Unlimited publication formats.** A format is *data*: a
    :class:`~intelligence.publication.formats.FormatDescriptor`. New formats — and new
    section types — are registered at runtime, from a JSON file or a dict, with no
    change to any engine. One generator serves every format.
  * **Deterministic.** Identical repository state ⇒ byte-identical documents, for
    every format and every renderer.

AUTHORITY = NONE (derived truth). Standard library only (TP-04). Writes nothing
outside ``intelligence/UCOS-UPI-001/``.
"""

from __future__ import annotations

__version__ = "1.0.0"

#: The programme identifier every emitted artifact declares.
PROGRAMME = "UCOS-UPI-001"

#: Authority classification of every emitted artifact.
AUTHORITY = "NONE (derived truth)"

#: The banner every rendered document carries, so a reader can never mistake a
#: generated publication for an authored (authoritative) one.
GENERATED_BANNER = (
    "GENERATED FROM CANONICAL KNOWLEDGE BY UCOS-UPI-001 — DO NOT EDIT BY HAND. "
    "Every block below is a resolved reference to a canonical record; edit the "
    "canonical source and regenerate."
)

__all__ = ["AUTHORITY", "GENERATED_BANNER", "PROGRAMME", "__version__"]
