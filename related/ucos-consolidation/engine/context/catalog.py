"""UCXI-000001 Part 06 — the Universal Context Catalog (DATA).

The sixteen universal contexts *of this platform*, declared once, as data. This is
what makes the layer operational rather than merely definable: a fresh registry can
be bootstrapped to a state in which every universal kind is present, conformant and
provenanced, which is the precondition the certifier measures.

Every value names a **located source** — a repository path or a named instrument that
already exists — so the catalog asserts nothing about the platform that the platform
does not already say about itself. No value is invented for effect; where a dimension
is genuinely open, it carries the explicit ``unknown`` sentinel rather than a
plausible-sounding guess.

Extending the catalog (or replacing it for another deployment) is a data edit: no
consumer of this module branches on a particular kind.
"""

from __future__ import annotations

from typing import Any

from engine.context.model import ContextDeclaration, values_from_mapping
from engine.context.taxonomy import ContextAuthority, ContextKind

#: The namespace the platform's own universal contexts are registered under.
UNIVERSAL_NAMESPACE = "ucos.context.universal"

#: The bounding frame of the platform's own universal contexts.
UNIVERSAL_BOUNDARY = "ucos-universal"

_CONSTITUTIONAL = ContextAuthority.CONSTITUTIONAL
_ARCHITECTURAL = ContextAuthority.ARCHITECTURAL
_OPERATIONAL = ContextAuthority.OPERATIONAL

#: kind -> (authority, source, {dimension: value})
UNIVERSAL_CATALOG: dict[str, tuple[ContextAuthority, str, dict[str, Any]]] = {
    ContextKind.EXISTENCE.value: (
        _CONSTITUTIONAL,
        "00-CEP/CEP-001-CONSTITUTIONAL-ENGINEERING-CONSTITUTION.md",
        {
            "existence_mode": "actual",
            "substrate": "the versioned repository and its certified corpus",
            "boundary": "the repository working tree; nothing outside it is asserted",
            "note": "What exists for this platform is what is present in Repository Truth.",
        },
    ),
    ContextKind.REALITY.value: (
        _CONSTITUTIONAL,
        "00-MASTER/URRC-000001/urrc_engine.py",
        {
            "reality_mode": "actual",
            "fidelity": "derived — every claim is computed from located artifacts",
            "verifiability": "re-run the located engine and compare the seal",
            "note": "Reality is bound by measurement, never by assertion.",
        },
    ),
    ContextKind.OBSERVER.value: (
        _ARCHITECTURAL,
        "engine/foundation/obs/context.py",
        {
            "observer_id": "ucos-engine",
            "vantage": "in-process, read-only over the repository",
            "epistemic_access": "files, git state and computed derivations; no network",
            "note": "Observation confers no authority (CXL-10).",
        },
    ),
    ContextKind.TEMPORAL.value: (
        _ARCHITECTURAL,
        "engine/determinism/reproduce.py",
        {
            "reference_frame": "repository history (commit order), not wall-clock",
            "ordering": "causal — dependency order and commit ancestry",
            "resolution": "one commit",
            "note": "The determined path reads no clock, so outputs are time-invariant.",
        },
    ),
    ContextKind.SPATIAL.value: (
        _ARCHITECTURAL,
        "engine/foundation/guards/frozen_paths.py",
        {
            "reference_frame": "repository-relative POSIX paths",
            "extent": "the workspace root and its subtrees",
            "locality": "local filesystem; the frozen corpus is read-only",
            "note": "Space here is path space; write locality is guarded, not assumed.",
        },
    ),
    ContextKind.IDENTITY.value: (
        _CONSTITUTIONAL,
        "engine/registry/universal/identity.py",
        {
            "subject": "every registered artifact, including every context",
            "identifier": "UCOS-<CODE>-<12 hex> minted from the identity tuple",
            "authority": "the single registration authority (Universal Registry Platform)",
            "note": "Identity is a pure function of (kind, namespace, natural key).",
        },
    ),
    ContextKind.GOVERNANCE.value: (
        _CONSTITUTIONAL,
        "00-CEP/CEP-002-CONSTITUTIONAL-GOVERNANCE-CONSTITUTION.md",
        {
            "authority": "the Constitutional Engineering Programme instruments (00-CEP)",
            "policy": "fail-closed gates; derived truth may not legislate",
            "decision_rights": "constitutional instruments decide; engines only compute",
            "note": "This layer is derived truth and creates no authority.",
        },
    ),
    ContextKind.SECURITY.value: (
        _CONSTITUTIONAL,
        "engine/foundation/obs/errors.py",
        {
            "classification": "internal — proprietary repository content",
            "trust_boundary": "the process boundary; external input is untrusted",
            "controls": [
                "secure-by-default error context (no secret values)",
                "frozen-path write guard",
                "stdlib-only runtime surface",
            ],
            "note": "Error context carries references, never secrets (SEC-04).",
        },
    ),
    ContextKind.KNOWLEDGE.value: (
        _CONSTITUTIONAL,
        "engine/knowledge/model.py",
        {
            "source": "the certified corpus plus the registry of record",
            "provenance": "canonical knowledge objects with content hashes",
            "confidence": "high for located artifacts; unknown is stated explicitly",
            "note": "Knowledge Once: one canonical home per unit of knowledge.",
        },
    ),
    ContextKind.COMPUTATIONAL.value: (
        _ARCHITECTURAL,
        "pyproject.toml",
        {
            "substrate": "CPython >= 3.12, standard library only at runtime",
            "execution_model": "pure, deterministic, single-process computation",
            "resources": {"runtime_dependencies": 0, "network": "none"},
            "note": "Vendor neutrality of core (TP-04) and least sufficient technology (TP-05).",
        },
    ),
    ContextKind.ENVIRONMENTAL.value: (
        _OPERATIONAL,
        "ENVIRONMENT-SETUP.md",
        {
            "medium": "a developer workstation or a CI runner",
            "conditions": {"toolchain": "pinned", "virtualenv": ".ec1-venv"},
            "constraints": [
                "no network access on the determined path",
                "the frozen corpus is never written",
            ],
            "note": "The environment is reproducible by construction, not by convention.",
        },
    ),
    ContextKind.ECONOMIC.value: (
        _OPERATIONAL,
        "Makefile",
        {
            "cost_model": "developer and CI time; zero third-party runtime cost",
            "value_basis": "verifiable completeness — evidence a reviewer can re-derive",
            "scarcity": "reviewer attention and execution context are the scarce goods",
            "note": "Reuse before creation is an economic as well as an architectural rule.",
        },
    ),
    ContextKind.REGULATORY.value: (
        _CONSTITUTIONAL,
        "00-CEP/CEP-010-CONSTITUTIONAL-AUDIT-COMPLIANCE-ASSURANCE-CONSTITUTION.md",
        {
            "jurisdiction": "internal constitutional regime (00-CEP, 00-CMG)",
            "obligations": [
                "evidence-bearing determinations",
                "fail-closed gates with reachable pass states",
                "append-only, auditable history",
            ],
            "compliance_state": "measured by the located gates, never self-asserted",
            "note": "External statutory regimes are out of scope and are not claimed.",
        },
    ),
    ContextKind.LINGUISTIC.value: (
        _OPERATIONAL,
        "00-BOOK/UCOS-BOOK-000000-UNIVERSAL-MASTER-KNOWLEDGE-BOOK.md",
        {
            "language": "en",
            "register": "constitutional-technical; terms of art are defined once",
            "encoding": "UTF-8",
            "note": "One canonical vocabulary; a term means the same thing everywhere.",
        },
    ),
    ContextKind.CULTURAL.value: (
        _OPERATIONAL,
        "00-CMG/CMG-000001-CONSTITUTIONAL-META-GOVERNANCE-CONSTITUTION.md",
        {
            "locale": "engineering culture of the UCOS programme",
            "norms": [
                "repository first — search before implementing",
                "reuse before creation",
                "derived truth never legislates",
            ],
            "conventions": [
                "deterministic, sealed artifacts",
                "fail-closed by default",
                "additive engineering over mutation",
            ],
            "note": "Culture is recorded because it changes how artifacts are read.",
        },
    ),
    ContextKind.MEASUREMENT.value: (
        _ARCHITECTURAL,
        "platform/universal_measurement/engine.py",
        {
            "measurement_system": "dimensionless counting and content-addressing — this "
            "platform measures cardinalities, ratios and digests, so no physical unit "
            "system is in force. SI is not assumed and not required.",
            "units": {
                "cardinality": "count — a whole number of registered artifacts",
                "proportion": "ratio of a measured part to a measured total",
                "integrity": "sha-256 hexadecimal digest",
                "duration": "commit ordinal — repository history, never a wall clock",
            },
            "scale": "human — the repository is measured at the scale of files, commits "
            "and artifacts (one row of engine/ceu/catalog.py SEED_SCALES, not the default)",
            "note": "Units and scales are entities and conversions are relationships "
            "(ADR-0005); nothing here privileges a system, a planet or a civilisation.",
        },
    ),
}


def universal_declarations(
    *, namespace: str = UNIVERSAL_NAMESPACE, boundary: str = UNIVERSAL_BOUNDARY
) -> tuple[ContextDeclaration, ...]:
    """Build the sixteen universal context declarations from the catalog."""
    out: list[ContextDeclaration] = []
    for kind in sorted(UNIVERSAL_CATALOG):
        authority, source, values = UNIVERSAL_CATALOG[kind]
        out.append(
            ContextDeclaration(
                kind=kind,
                namespace=namespace,
                natural_key=kind,
                values=values_from_mapping(values, authority=authority, source=source),
                authority=authority,
                boundary=boundary,
                description=f"The platform's own {kind} context, derived from {source}.",
            )
        )
    return tuple(out)


def catalog_sources() -> tuple[str, ...]:
    """Every located source the catalog cites, ordered (used by evidence)."""
    return tuple(sorted({source for _, source, _ in UNIVERSAL_CATALOG.values()}))


__all__ = [
    "UNIVERSAL_NAMESPACE",
    "UNIVERSAL_BOUNDARY",
    "UNIVERSAL_CATALOG",
    "universal_declarations",
    "catalog_sources",
]


def bootstrap_registry(
    *,
    namespace: str = UNIVERSAL_NAMESPACE,
    boundary: str = UNIVERSAL_BOUNDARY,
    registry: Any = None,
) -> Any:
    """Return a registry with the sixteen universal contexts registered.

    The single entry point every surface uses to reach an operational state: the CLI,
    the evidence builder and the certifier all bootstrap from this catalog, so they all
    certify the same context set. Registration is idempotent, so bootstrapping an
    already-bootstrapped registry is a no-op rather than a duplicate refusal.
    """
    from engine.context.registry import ContextRegistry  # local import: avoids a cycle

    target = ContextRegistry() if registry is None else registry
    target.register_all(universal_declarations(namespace=namespace, boundary=boundary))
    return target
