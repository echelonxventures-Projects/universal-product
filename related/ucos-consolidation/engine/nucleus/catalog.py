"""UCOS-NUC-001 Part 03 — the seed structural catalogue (DATA, not code).

Everything in this module is a **declaration**. No function here decides anything, no
function branches on a name, and adding, removing or re-scoping a nucleus, layer or
composition is an edit to a tuple — never to a rule. That is the property AC-005's
"infinite additional nuclei / no architectural limit" requires: the population is data
over an open registry, so the ten-thousandth nucleus costs one tuple entry.

The constitutional correction this catalogue encodes
----------------------------------------------------
**Commerce is not a Nucleus. Commerce is a Composition.** So are Amazon, Uber, PayTM,
WhatsApp, Facebook, Instagram, X, LinkedIn, YouTube, ERP, CRM, LMS, EdTech, and every
sector, banking, insurance, healthcare, government, defence, industrial, scientific,
research and civilisational platform. None of them appears in :data:`SEED_NUCLEI`.
Each appears in :data:`SEED_COMPOSITIONS`, where it exists *only* as a selection of
registered nuclei plus configuration. Because :func:`engine.nucleus.model.derive_role`
derives the role from the presence of a selection, this is not a label applied by
convention: a subject that selects nuclei **cannot** be registered as a nucleus, and a
subject registered as a composition **cannot** own a capability.

This aligns the machine-readable population with
``00-MASTER/UCOS-NUCLEUS-001/02-NUCLEUS-CONSTITUTIONAL-MODEL.md`` §6, which already
classified Commerce, Retail, Marketplace, ERP and CRM as compositions in prose. Before
this module the classification existed only in prose and nothing enforced it.

Layers
------
:data:`SEED_LAYERS` is the ``ucos.architecture-layer`` vocabulary — the fourteen
governed layer terms in :mod:`engine.uckp.vocabulary` — reused verbatim, in rank order.
It is not a second layer model (D-09 names that vocabulary canonical). Each layer is
registered in the LAYER role, and the LAYER role owns nothing.
"""

from __future__ import annotations

from typing import Any

from engine.nucleus.model import CapabilityDeclaration, SubjectDeclaration
from engine.uckp.vocabulary import ARCHITECTURE_LAYER, DEFAULT_VOCABULARIES

#: The namespace every seed structural subject is registered under, per role. A layer and
#: a nucleus may legitimately share a name (``governance`` is both an organisational layer
#: and a capability authority), and they are different subjects — so they are registered in
#: different namespaces and under different identifier kinds. Collapsing them would be the
#: exact ownership ambiguity AC-011 forbids.
STRUCTURE_NAMESPACE = "ucos.structure"
LAYER_NAMESPACE = "ucos.structure.layer"
NUCLEUS_NAMESPACE = "ucos.structure.nucleus"
COMPOSITION_NAMESPACE = "ucos.structure.composition"

#: The namespace every seed capability is registered under.
CAPABILITY_NAMESPACE = "ucos.capability"


#: The seed nuclei: ``(key, title, canonical concept)``. Each nucleus owns exactly one
#: canonical concept — a nucleus that owned two would be two nuclei. AC-005's mandated
#: minimum is present in full **except Commerce**, which is a composition.
SEED_NUCLEI: tuple[tuple[str, str, str], ...] = (
    ("identity", "Identity Nucleus", "identity"),
    ("identifier", "Identifier Nucleus", "universal-identifier"),
    ("geography", "Geography Nucleus", "geography"),
    ("location", "Location Nucleus", "location"),
    ("context", "Context Nucleus", "context"),
    ("time", "Time Nucleus", "time"),
    ("calendar", "Calendar Nucleus", "calendar"),
    ("language", "Language Nucleus", "language"),
    ("translation", "Translation Nucleus", "translation"),
    ("currency", "Currency Nucleus", "currency"),
    ("units", "Units Nucleus", "units-of-measure"),
    ("measurement", "Measurement Nucleus", "measurement"),
    ("tax", "Tax Nucleus", "taxation"),
    ("jurisdiction", "Jurisdiction Nucleus", "jurisdiction"),
    ("regulation", "Regulation Nucleus", "regulation"),
    ("governance", "Governance Nucleus", "governance"),
    ("policy", "Policy Nucleus", "policy"),
    ("ownership", "Ownership Nucleus", "canonical-ownership"),
    ("security", "Security Nucleus", "security"),
    ("trust", "Trust Nucleus", "trust"),
    ("knowledge", "Knowledge Nucleus", "knowledge"),
    ("learning", "Learning Nucleus", "learning"),
    ("intelligence", "Intelligence Nucleus", "intelligence"),
    ("registry", "Registry Nucleus", "registration"),
    ("lineage", "Lineage Nucleus", "lineage"),
    ("evidence", "Evidence Nucleus", "evidence"),
    ("validation", "Validation Nucleus", "validation"),
    ("certification", "Certification Nucleus", "certification"),
    ("lifecycle", "Lifecycle Nucleus", "constitutional-lifecycle"),
    ("evolution", "Evolution Nucleus", "evolution"),
    ("workflow", "Workflow Nucleus", "workflow"),
    ("execution", "Execution Nucleus", "execution"),
    ("communication", "Communication Nucleus", "communication"),
    ("media", "Media Nucleus", "media"),
    ("relationship", "Relationship Nucleus", "relationship"),
    ("dependency", "Dependency Nucleus", "dependency"),
    ("culture", "Culture Nucleus", "culture"),
    ("economy", "Economy Nucleus", "economic-system"),
    ("product", "Product Nucleus", "product"),
    ("catalog", "Catalog Nucleus", "catalog"),
    ("pricing", "Pricing Nucleus", "pricing"),
    ("billing", "Billing Nucleus", "billing"),
    ("payment", "Payment Nucleus", "payment"),
)


#: The **compositions**: ``(key, title, selected nucleus keys)``. Every entry here owns
#: nothing and adds no capability; it selects registered nuclei and is otherwise pure
#: configuration. This is the corrected classification of Commerce and of every named
#: platform, product, sector and civilisational system.
SEED_COMPOSITIONS: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    (
        "commerce",
        "Commerce Composition",
        (
            "catalog",
            "product",
            "pricing",
            "payment",
            "billing",
            "tax",
            "currency",
            "jurisdiction",
            "identity",
            "workflow",
            "execution",
            "relationship",
            "measurement",
        ),
    ),
    (
        "retail",
        "Retail Composition",
        ("catalog", "product", "pricing", "payment", "billing", "tax", "location", "identity"),
    ),
    (
        "marketplace",
        "Marketplace Composition",
        (
            "catalog",
            "product",
            "pricing",
            "payment",
            "billing",
            "identity",
            "trust",
            "relationship",
            "communication",
        ),
    ),
    (
        "amazon",
        "Amazon-class Composition",
        (
            "catalog",
            "product",
            "pricing",
            "payment",
            "billing",
            "tax",
            "currency",
            "location",
            "geography",
            "identity",
            "trust",
            "workflow",
            "execution",
            "media",
            "measurement",
        ),
    ),
    (
        "uber",
        "Uber-class Composition",
        (
            "identity",
            "location",
            "geography",
            "time",
            "pricing",
            "payment",
            "billing",
            "tax",
            "workflow",
            "execution",
            "communication",
            "trust",
            "measurement",
        ),
    ),
    (
        "paytm",
        "PayTM-class Composition",
        (
            "identity",
            "payment",
            "billing",
            "pricing",
            "currency",
            "tax",
            "jurisdiction",
            "regulation",
            "security",
            "trust",
            "execution",
        ),
    ),
    (
        "whatsapp",
        "WhatsApp-class Composition",
        ("identity", "communication", "media", "security", "trust", "relationship", "language"),
    ),
    (
        "facebook",
        "Facebook-class Composition",
        (
            "identity",
            "relationship",
            "communication",
            "media",
            "knowledge",
            "policy",
            "security",
            "measurement",
        ),
    ),
    (
        "instagram",
        "Instagram-class Composition",
        ("identity", "media", "relationship", "communication", "measurement"),
    ),
    (
        "x",
        "X-class Composition",
        ("identity", "communication", "media", "relationship", "policy", "measurement"),
    ),
    (
        "linkedin",
        "LinkedIn-class Composition",
        ("identity", "relationship", "knowledge", "communication", "media", "learning"),
    ),
    (
        "youtube",
        "YouTube-class Composition",
        ("identity", "media", "catalog", "pricing", "billing", "measurement", "relationship"),
    ),
    (
        "erp",
        "ERP Composition",
        (
            "identity",
            "product",
            "catalog",
            "pricing",
            "billing",
            "payment",
            "tax",
            "currency",
            "workflow",
            "execution",
            "measurement",
            "governance",
            "policy",
            "relationship",
            "dependency",
        ),
    ),
    (
        "crm",
        "CRM Composition",
        ("identity", "relationship", "communication", "workflow", "measurement", "knowledge"),
    ),
    (
        "lms",
        "LMS Composition",
        ("identity", "learning", "knowledge", "media", "measurement", "certification"),
    ),
    (
        "edtech",
        "EdTech Composition",
        (
            "identity",
            "learning",
            "knowledge",
            "media",
            "measurement",
            "certification",
            "pricing",
            "billing",
            "payment",
            "language",
            "translation",
        ),
    ),
    (
        "consultancy-platform",
        "Consultancy Platform Composition",
        (
            "identity",
            "knowledge",
            "relationship",
            "workflow",
            "pricing",
            "billing",
            "measurement",
            "evidence",
        ),
    ),
    (
        "banking-platform",
        "Banking Platform Composition",
        (
            "identity",
            "payment",
            "billing",
            "pricing",
            "currency",
            "tax",
            "jurisdiction",
            "regulation",
            "governance",
            "policy",
            "security",
            "trust",
            "evidence",
            "lineage",
        ),
    ),
    (
        "insurance-platform",
        "Insurance Platform Composition",
        (
            "identity",
            "pricing",
            "billing",
            "payment",
            "currency",
            "jurisdiction",
            "regulation",
            "policy",
            "evidence",
            "measurement",
            "relationship",
        ),
    ),
    (
        "healthcare-platform",
        "Healthcare Platform Composition",
        (
            "identity",
            "knowledge",
            "evidence",
            "measurement",
            "workflow",
            "security",
            "regulation",
            "jurisdiction",
            "billing",
            "payment",
            "communication",
        ),
    ),
    (
        "government-platform",
        "Government Platform Composition",
        (
            "identity",
            "jurisdiction",
            "regulation",
            "governance",
            "policy",
            "tax",
            "location",
            "geography",
            "language",
            "evidence",
            "lineage",
            "communication",
        ),
    ),
    (
        "defence-platform",
        "Defence Platform Composition",
        (
            "identity",
            "security",
            "trust",
            "governance",
            "policy",
            "location",
            "geography",
            "communication",
            "evidence",
            "execution",
        ),
    ),
    (
        "industrial-platform",
        "Industrial Platform Composition",
        (
            "identity",
            "product",
            "measurement",
            "units",
            "workflow",
            "execution",
            "dependency",
            "evidence",
            "location",
        ),
    ),
    (
        "scientific-platform",
        "Scientific Platform Composition",
        (
            "identity",
            "knowledge",
            "measurement",
            "units",
            "evidence",
            "validation",
            "certification",
            "intelligence",
        ),
    ),
    (
        "research-platform",
        "Research Platform Composition",
        (
            "identity",
            "knowledge",
            "learning",
            "intelligence",
            "evidence",
            "measurement",
            "lineage",
            "certification",
        ),
    ),
    (
        "civilizational-platform",
        "Civilizational Platform Composition",
        (
            "identity",
            "context",
            "location",
            "geography",
            "time",
            "calendar",
            "language",
            "currency",
            "units",
            "tax",
            "jurisdiction",
            "regulation",
            "governance",
            "policy",
            "culture",
            "economy",
            "knowledge",
            "intelligence",
            "communication",
        ),
    ),
)


def seed_layers() -> tuple[tuple[str, str, int], ...]:
    """The governed layer stack as ``(key, definition, rank)``, in rank order.

    Read from the ``ucos.architecture-layer`` vocabulary rather than restated, so this
    catalogue cannot become a sixth competing layer model (D-09). A layer added to the
    vocabulary appears here with no edit.
    """
    vocabulary = DEFAULT_VOCABULARIES.require(ARCHITECTURE_LAYER)
    return tuple(
        (term.term_id, term.definition, term.rank)
        for term in sorted(vocabulary.terms, key=lambda t: (t.rank, t.term_id))
    )


#: The capabilities each seed nucleus owns, as ``(nucleus key, capability suffix, title)``.
#: One entry per nucleus: the nucleus's own canonical authority over its concept. Further
#: capabilities are registered against a nucleus at any time; nothing here is a ceiling.
SEED_CAPABILITY_SUFFIXES: tuple[tuple[str, str], ...] = (
    ("authority", "canonical authority over the nucleus's concept"),
    ("resolution", "resolution of the nucleus's concept from registered context"),
    ("registration", "registration of instances of the nucleus's concept"),
)


def seed_subjects() -> tuple[SubjectDeclaration, ...]:
    """Every seed structural subject: layers, then nuclei, then compositions.

    Ordered layers → nuclei → compositions because a composition's selections must
    already be registered when it is admitted (NL-08).
    """
    declarations: list[SubjectDeclaration] = []
    for key, definition, rank in seed_layers():
        declarations.append(
            SubjectDeclaration(
                key=key,
                title=f"{key.title()} Layer",
                namespace=LAYER_NAMESPACE,
                description=definition,
                profile={"rank": rank, "owns": "nothing"},
            )
        )
    for key, title, concept in SEED_NUCLEI:
        declarations.append(
            SubjectDeclaration(
                key=key,
                title=title,
                namespace=NUCLEUS_NAMESPACE,
                concept=concept,
                description=f"The complete constitutional universe of the concept '{concept}'.",
            )
        )
    for key, title, composes in SEED_COMPOSITIONS:
        declarations.append(
            SubjectDeclaration(
                key=key,
                title=title,
                namespace=COMPOSITION_NAMESPACE,
                composes=composes,
                description=(
                    "A composition: selected nuclei plus configuration. Owns no capability "
                    "and contributes no capability logic of its own."
                ),
            )
        )
    return tuple(declarations)


def seed_capabilities() -> tuple[CapabilityDeclaration, ...]:
    """Every seed capability, each owned by exactly one nucleus (NL-01, NL-04)."""
    declarations: list[CapabilityDeclaration] = []
    for key, _title, concept in SEED_NUCLEI:
        for suffix, purpose in SEED_CAPABILITY_SUFFIXES:
            declarations.append(
                CapabilityDeclaration(
                    key=f"{key}.{suffix}",
                    title=f"{concept} {suffix}",
                    owner=key,
                    namespace=CAPABILITY_NAMESPACE,
                    description=purpose,
                )
            )
    return tuple(declarations)


def nucleus_keys() -> tuple[str, ...]:
    """The keys of every seed nucleus, ordered."""
    return tuple(sorted(key for key, _t, _c in SEED_NUCLEI))


def composition_keys() -> tuple[str, ...]:
    """The keys of every seed composition, ordered."""
    return tuple(sorted(key for key, _t, _c in SEED_COMPOSITIONS))


def layer_keys() -> tuple[str, ...]:
    """The keys of every seed layer, ordered."""
    return tuple(sorted(key for key, _d, _r in seed_layers()))


def to_document() -> dict[str, Any]:
    """The catalogue as a deterministic, machine-readable document."""
    return {
        "schema": "ucos-structural-catalogue",
        "version": "1.0.0",
        "correction": (
            "Commerce is a Composition, not a Nucleus. Every named platform, product, "
            "sector and civilisational system is a Composition of registered Nuclei."
        ),
        "layers": [
            {"key": key, "definition": definition, "rank": rank}
            for key, definition, rank in seed_layers()
        ],
        "nuclei": [
            {"key": key, "title": title, "concept": concept} for key, title, concept in SEED_NUCLEI
        ],
        "compositions": [
            {"key": key, "title": title, "composes": list(composes)}
            for key, title, composes in SEED_COMPOSITIONS
        ],
        "counts": {
            "layers": len(seed_layers()),
            "nuclei": len(SEED_NUCLEI),
            "compositions": len(SEED_COMPOSITIONS),
            "capabilities": len(SEED_NUCLEI) * len(SEED_CAPABILITY_SUFFIXES),
        },
        "closed_set": False,
        "upper_limit": None,
    }


__all__ = [
    "STRUCTURE_NAMESPACE",
    "LAYER_NAMESPACE",
    "NUCLEUS_NAMESPACE",
    "COMPOSITION_NAMESPACE",
    "CAPABILITY_NAMESPACE",
    "SEED_NUCLEI",
    "SEED_COMPOSITIONS",
    "SEED_CAPABILITY_SUFFIXES",
    "seed_layers",
    "seed_subjects",
    "seed_capabilities",
    "nucleus_keys",
    "composition_keys",
    "layer_keys",
    "to_document",
]
