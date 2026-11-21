"""Deterministic, content-derived identity for research + publication artifacts.

The repository already owns a deterministic identity algorithm
(``engine.registry.universal.identity``): an id is a pure function of the
identity tuple ``(code, namespace, natural_key)`` and has the shape
``UCOS-<CODE>-<12 hex>``. The kernel **reuses that algorithm verbatim** — its
canonical rendering, its digest, its namespace and natural-key normalizers — and
adds only the artifact-class code table that the Universal Registry Platform does
not (and must not) carry: research and publication classes.

No wall-clock, no counter, no allocator: the same logical artifact always
resolves to the same identifier, in any order, on any machine, which is what
makes duplicate detection and Knowledge-Once enforcement possible.
"""

from __future__ import annotations

import hashlib
from enum import Enum

from engine.registry.universal.identity import (
    ID_PREFIX,
    canonical_json,
    content_digest,
    normalize_namespace,
    normalize_natural_key,
)
from intelligence.kernel.errors import KernelError

#: Length (hex chars) of the embedded identity digest — matches the platform id.
_ID_DIGEST_LEN = 12

#: The namespace root under which every derived research/publication identity lives.
RESEARCH_NAMESPACE = "ucos.intelligence.research"
PUBLICATION_NAMESPACE = "ucos.intelligence.publication"


class ArtifactClass(str, Enum):
    """The artifact classes the research/publication ledgers govern.

    Each class owns a distinct id code so an identifier is self-describing and the
    two registries never collide in identity space (nor with the twelve platform
    registry kinds, whose codes are NS/CAP/DOC/ENG/CMP/API/SVC/APP/INF/DEP/EVD/CERT).
    """

    RESEARCH_SOURCE = "RESEARCH_SOURCE"
    RESEARCH_CLAIM = "RESEARCH_CLAIM"
    RESEARCH_FINDING = "RESEARCH_FINDING"
    RESEARCH_CONTRIBUTION = "RESEARCH_CONTRIBUTION"
    RESEARCH_UNIT = "RESEARCH_UNIT"
    STANDARD_ANALYSIS = "STANDARD_ANALYSIS"
    PUBLICATION = "PUBLICATION"
    PUBLICATION_FORMAT = "PUBLICATION_FORMAT"
    PUBLICATION_SECTION = "PUBLICATION_SECTION"
    CITATION = "CITATION"

    @property
    def code(self) -> str:
        return _CLASS_CODES[self]

    @property
    def default_namespace(self) -> str:
        return _CLASS_NAMESPACES[self]

    @classmethod
    def coerce(cls, value: object) -> ArtifactClass:
        if isinstance(value, cls):
            return value
        try:
            return cls(str(value))
        except ValueError as exc:
            raise KernelError(
                "unknown artifact class",
                value=value,
                allowed=[c.value for c in cls],
            ) from exc


_CLASS_CODES: dict[ArtifactClass, str] = {
    ArtifactClass.RESEARCH_SOURCE: "RSRC",
    ArtifactClass.RESEARCH_CLAIM: "RCLM",
    ArtifactClass.RESEARCH_FINDING: "RFND",
    ArtifactClass.RESEARCH_CONTRIBUTION: "RCTR",
    ArtifactClass.RESEARCH_UNIT: "RSCH",
    ArtifactClass.STANDARD_ANALYSIS: "RSTD",
    ArtifactClass.PUBLICATION: "PUB",
    ArtifactClass.PUBLICATION_FORMAT: "PFMT",
    ArtifactClass.PUBLICATION_SECTION: "PSEC",
    ArtifactClass.CITATION: "CITE",
}

_CLASS_NAMESPACES: dict[ArtifactClass, str] = {
    ArtifactClass.RESEARCH_SOURCE: f"{RESEARCH_NAMESPACE}.source",
    ArtifactClass.RESEARCH_CLAIM: f"{RESEARCH_NAMESPACE}.claim",
    ArtifactClass.RESEARCH_FINDING: f"{RESEARCH_NAMESPACE}.finding",
    ArtifactClass.RESEARCH_CONTRIBUTION: f"{RESEARCH_NAMESPACE}.contribution",
    ArtifactClass.RESEARCH_UNIT: f"{RESEARCH_NAMESPACE}.unit",
    ArtifactClass.STANDARD_ANALYSIS: f"{RESEARCH_NAMESPACE}.standard",
    ArtifactClass.PUBLICATION: f"{PUBLICATION_NAMESPACE}.document",
    ArtifactClass.PUBLICATION_FORMAT: f"{PUBLICATION_NAMESPACE}.format",
    ArtifactClass.PUBLICATION_SECTION: f"{PUBLICATION_NAMESPACE}.section",
    ArtifactClass.CITATION: f"{PUBLICATION_NAMESPACE}.citation",
}

_CODE_CLASSES: dict[str, ArtifactClass] = {code: cls for cls, code in _CLASS_CODES.items()}


def artifact_id(
    artifact_class: ArtifactClass | str,
    natural_key: str,
    *,
    namespace: str | None = None,
) -> str:
    """Compute the deterministic ``UCOS-<CODE>-<12 hex>`` id for an artifact."""
    klass = ArtifactClass.coerce(artifact_class)
    code = klass.code
    ns = normalize_namespace(namespace or klass.default_namespace)
    key = normalize_natural_key(natural_key)
    digest = hashlib.sha256(canonical_json([code, ns, key]).encode("utf-8")).hexdigest()
    return f"{ID_PREFIX}-{code}-{digest[:_ID_DIGEST_LEN]}"


def parse_class(identifier: str) -> ArtifactClass:
    """Recover the :class:`ArtifactClass` encoded in an identifier."""
    parts = str(identifier).split("-")
    if len(parts) != 3 or parts[0] != ID_PREFIX or parts[1] not in _CODE_CLASSES or not parts[2]:
        raise KernelError("not a well-formed intelligence artifact id", value=identifier)
    return _CODE_CLASSES[parts[1]]


def class_codes() -> dict[str, str]:
    """The artifact-class → id-code table (published in every catalog output)."""
    return {
        cls.value: code for cls, code in sorted(_CLASS_CODES.items(), key=lambda kv: kv[0].value)
    }


__all__ = [
    "ID_PREFIX",
    "PUBLICATION_NAMESPACE",
    "RESEARCH_NAMESPACE",
    "ArtifactClass",
    "artifact_id",
    "canonical_json",
    "class_codes",
    "content_digest",
    "parse_class",
]
